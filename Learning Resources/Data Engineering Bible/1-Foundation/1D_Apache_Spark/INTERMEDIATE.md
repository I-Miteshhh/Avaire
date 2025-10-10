# Week 4: Apache Spark Fundamentals
## 🔨 INTERMEDIATE - Production ETL with PySpark

---

## 🎯 **Learning Objectives**

- Build production ETL pipelines with PySpark
- Optimize Spark jobs (partitioning, caching, broadcast joins)
- Handle data quality and error handling
- Work with complex data types (arrays, structs, maps)
- Implement SCD Type 2 in Spark
- Debug performance issues with Spark UI

---

## 🏭 **1. Production ETL Pipeline**

### **Complete E-Commerce ETL Example**

**Scenario:** Process daily orders from multiple sources, transform, load to data warehouse.

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, when, lit, current_timestamp, to_date, sum, count,
    md5, concat, row_number, dense_rank
)
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DecimalType, TimestampType
from pyspark.sql.window import Window
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EcommerceETL:
    """Production ETL pipeline for e-commerce data"""
    
    def __init__(self, app_name="Ecommerce ETL"):
        self.spark = SparkSession.builder \
            .appName(app_name) \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.sql.shuffle.partitions", "200") \
            .getOrCreate()
        
        logger.info(f"Spark session created: {app_name}")
    
    def extract_orders(self, path):
        """
        Extract orders from CSV files
        
        Args:
            path: S3/HDFS path to order data
        
        Returns:
            DataFrame with raw orders
        """
        logger.info(f"Extracting orders from {path}")
        
        # Define schema explicitly (don't rely on inferSchema in production)
        schema = StructType([
            StructField("order_id", StringType(), False),
            StructField("customer_id", StringType(), False),
            StructField("order_date", StringType(), False),
            StructField("product_id", StringType(), False),
            StructField("quantity", IntegerType(), False),
            StructField("price", DecimalType(10, 2), False),
            StructField("status", StringType(), True)
        ])
        
        df = self.spark.read \
            .schema(schema) \
            .option("header", "true") \
            .option("mode", "PERMISSIVE") \
            .csv(path)
        
        logger.info(f"Extracted {df.count()} orders")
        return df
    
    def extract_customers(self, path):
        """Extract customer dimension from Parquet"""
        logger.info(f"Extracting customers from {path}")
        
        df = self.spark.read.parquet(path)
        
        logger.info(f"Extracted {df.count()} customers")
        return df
    
    def extract_products(self, jdbc_url, table_name):
        """
        Extract products from PostgreSQL database
        
        Args:
            jdbc_url: JDBC connection string
            table_name: Table to read
        """
        logger.info(f"Extracting products from database: {table_name}")
        
        df = self.spark.read \
            .format("jdbc") \
            .option("url", jdbc_url) \
            .option("dbtable", table_name) \
            .option("user", "your_user") \
            .option("password", "your_password") \
            .option("driver", "org.postgresql.Driver") \
            .load()
        
        return df
    
    def transform_orders(self, orders_df, customers_df, products_df):
        """
        Transform orders with business logic
        
        Transformations:
        1. Join with customers and products
        2. Calculate revenue
        3. Add data quality flags
        4. Standardize status codes
        5. Add processing timestamp
        """
        logger.info("Starting transformations...")
        
        # 1. Data quality checks
        orders_clean = orders_df \
            .filter(col("order_id").isNotNull()) \
            .filter(col("quantity") > 0) \
            .filter(col("price") > 0) \
            .withColumn("is_valid", 
                when((col("order_id").isNotNull()) & 
                     (col("quantity") > 0) & 
                     (col("price") > 0), True)
                .otherwise(False))
        
        # 2. Calculate revenue
        orders_revenue = orders_clean \
            .withColumn("revenue", col("quantity") * col("price"))
        
        # 3. Standardize status (handle NULL and inconsistent values)
        orders_status = orders_revenue \
            .withColumn("status", 
                when(col("status").isNull(), "unknown")
                .when(col("status").isin(["delivered", "DELIVERED"]), "delivered")
                .when(col("status").isin(["pending", "PENDING"]), "pending")
                .when(col("status").isin(["cancelled", "CANCELLED"]), "cancelled")
                .otherwise("other"))
        
        # 4. Convert date string to date type
        orders_dated = orders_status \
            .withColumn("order_date", to_date(col("order_date"), "yyyy-MM-dd"))
        
        # 5. Join with customers (enrich with customer info)
        orders_with_customers = orders_dated \
            .join(customers_df, "customer_id", "left") \
            .select(
                orders_dated["*"],
                customers_df["customer_name"],
                customers_df["customer_email"],
                customers_df["customer_country"]
            )
        
        # 6. Join with products (enrich with product info)
        orders_enriched = orders_with_customers \
            .join(products_df, "product_id", "left") \
            .select(
                orders_with_customers["*"],
                products_df["product_name"],
                products_df["product_category"],
                products_df["product_brand"]
            )
        
        # 7. Add processing metadata
        orders_final = orders_enriched \
            .withColumn("processed_at", current_timestamp()) \
            .withColumn("etl_batch_id", lit("batch_2024_10_09"))
        
        logger.info(f"Transformations complete: {orders_final.count()} rows")
        return orders_final
    
    def validate_data_quality(self, df):
        """
        Validate data quality and log issues
        
        Returns:
            DataFrame with only valid rows
        """
        logger.info("Validating data quality...")
        
        total_rows = df.count()
        
        # Check for NULL critical fields
        null_checks = {
            "order_id": df.filter(col("order_id").isNull()).count(),
            "customer_id": df.filter(col("customer_id").isNull()).count(),
            "product_id": df.filter(col("product_id").isNull()).count()
        }
        
        for field, null_count in null_checks.items():
            if null_count > 0:
                logger.warning(f"{field} has {null_count} NULL values ({null_count/total_rows*100:.2f}%)")
        
        # Check for invalid values
        invalid_quantity = df.filter(col("quantity") <= 0).count()
        invalid_price = df.filter(col("price") <= 0).count()
        
        logger.info(f"Invalid quantity: {invalid_quantity}")
        logger.info(f"Invalid price: {invalid_price}")
        
        # Filter to valid rows only
        valid_df = df.filter(col("is_valid") == True)
        
        logger.info(f"Data quality check complete: {valid_df.count()}/{total_rows} valid rows")
        return valid_df
    
    def load_to_warehouse(self, df, output_path, partition_by=None):
        """
        Load data to data warehouse (Parquet format)
        
        Args:
            df: DataFrame to write
            output_path: S3/HDFS path
            partition_by: List of columns to partition by
        """
        logger.info(f"Loading data to {output_path}")
        
        writer = df.write \
            .mode("overwrite") \
            .format("parquet") \
            .option("compression", "snappy")
        
        if partition_by:
            writer = writer.partitionBy(*partition_by)
        
        writer.save(output_path)
        
        logger.info("Data loaded successfully")
    
    def run(self, orders_path, customers_path, products_jdbc, output_path):
        """
        Execute full ETL pipeline
        """
        logger.info("=" * 50)
        logger.info("Starting ETL Pipeline")
        logger.info("=" * 50)
        
        try:
            # Extract
            orders = self.extract_orders(orders_path)
            customers = self.extract_customers(customers_path)
            # products = self.extract_products(products_jdbc, "products")
            
            # For demo, create sample products
            products_data = [
                ("P001", "Laptop", "Electronics", "Dell"),
                ("P002", "Mouse", "Electronics", "Logitech"),
                ("P003", "Keyboard", "Electronics", "Logitech")
            ]
            products = self.spark.createDataFrame(
                products_data, 
                ["product_id", "product_name", "product_category", "product_brand"]
            )
            
            # Transform
            transformed = self.transform_orders(orders, customers, products)
            
            # Validate
            validated = self.validate_data_quality(transformed)
            
            # Load (partitioned by date for efficient querying)
            self.load_to_warehouse(
                validated, 
                output_path, 
                partition_by=["order_date"]
            )
            
            logger.info("=" * 50)
            logger.info("ETL Pipeline Completed Successfully")
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"ETL Pipeline failed: {str(e)}", exc_info=True)
            raise
        finally:
            self.spark.stop()

# Usage
if __name__ == "__main__":
    etl = EcommerceETL()
    
    # Sample data for testing
    orders_data = [
        ("O001", "C001", "2024-01-01", "P001", 1, 1000.00, "delivered"),
        ("O002", "C002", "2024-01-01", "P002", 2, 20.00, "pending"),
        ("O003", "C001", "2024-01-02", "P003", 1, 50.00, "delivered"),
        ("O004", "C003", "2024-01-02", "P001", 1, 1000.00, None),  # NULL status
        ("O005", "C002", "2024-01-03", "P002", 0, 20.00, "cancelled"),  # Invalid quantity
    ]
    
    customers_data = [
        ("C001", "Alice", "alice@example.com", "USA"),
        ("C002", "Bob", "bob@example.com", "UK"),
        ("C003", "Charlie", "charlie@example.com", "Canada")
    ]
    
    # Create sample files (in production, data comes from S3/HDFS)
    orders_df = etl.spark.createDataFrame(
        orders_data,
        ["order_id", "customer_id", "order_date", "product_id", "quantity", "price", "status"]
    )
    orders_df.write.mode("overwrite").option("header", "true").csv("/tmp/orders")
    
    customers_df = etl.spark.createDataFrame(
        customers_data,
        ["customer_id", "customer_name", "customer_email", "customer_country"]
    )
    customers_df.write.mode("overwrite").parquet("/tmp/customers")
    
    # Run ETL
    etl.run(
        orders_path="/tmp/orders",
        customers_path="/tmp/customers",
        products_jdbc=None,
        output_path="/tmp/warehouse/orders"
    )
```

---

## ⚡ **2. Performance Optimization**

### **2.1 Partitioning Strategy**

**Problem:** Skewed data causes some tasks to run much longer than others.

```python
from pyspark.sql.functions import spark_partition_id

# Check current partitions
df.select(spark_partition_id().alias("partition_id")).distinct().show()

# Bad: Default partitions (200) may be too many for small data
df = spark.read.csv("small_data.csv")  # 1 MB of data
# 200 partitions = 5 KB per partition (overhead > data!)

# Good: Repartition based on data size
df = df.repartition(10)  # ~100 KB per partition

# Rule of thumb: 128 MB - 1 GB per partition
data_size_mb = 10000  # 10 GB
num_partitions = data_size_mb / 128  # ~78 partitions
df = df.repartition(int(num_partitions))
```

---

### **2.2 Broadcast Joins (Small Table Join)**

**Problem:** Large shuffle when joining large table with small table.

**Bad: Regular join (shuffles both tables)**
```python
# orders: 1 billion rows
# products: 1000 rows

result = orders.join(products, "product_id")
# Shuffles 1B rows across network! Slow! ❌
```

**Good: Broadcast join (sends small table to all nodes)**
```python
from pyspark.sql.functions import broadcast

# Broadcast small table (< 10 MB)
result = orders.join(broadcast(products), "product_id")
# Only shuffles products (1000 rows), not orders! Fast! ✅
```

**How it works:**
```
Without broadcast:
  Orders (1B rows) → Shuffle → Join ← Shuffle ← Products (1000 rows)
  
With broadcast:
  Orders (1B rows) → Join ← (Products copied to all executors)
  No shuffle for orders!
```

---

### **2.3 Caching and Persistence**

**When to cache:** DataFrame used multiple times in your code.

```python
# Without caching (re-reads from disk every time)
df = spark.read.parquet("large_data.parquet")
df.filter(col("country") == "USA").count()  # Read from disk
df.filter(col("country") == "UK").count()   # Read from disk again! ❌

# With caching (reads once, stores in memory)
df = spark.read.parquet("large_data.parquet")
df.cache()  # or df.persist()

df.filter(col("country") == "USA").count()  # Reads from disk, caches
df.filter(col("country") == "UK").count()   # Reads from cache! ✅

# Unpersist when done
df.unpersist()
```

**Storage levels:**
```python
from pyspark import StorageLevel

# Memory only (fastest, but may fail if not enough RAM)
df.persist(StorageLevel.MEMORY_ONLY)

# Memory and disk (spills to disk if RAM full)
df.persist(StorageLevel.MEMORY_AND_DISK)

# Disk only
df.persist(StorageLevel.DISK_ONLY)

# Serialized (compressed, slower access but uses less RAM)
df.persist(StorageLevel.MEMORY_ONLY_SER)
```

---

### **2.4 Avoid Shuffles**

**Shuffle = Data movement across network (slow!)**

**Operations that cause shuffle:**
- `groupBy()`, `join()`, `orderBy()`, `repartition()`, `distinct()`

**Minimize shuffles:**

```python
# Bad: Multiple shuffles
df.groupBy("country").count()  # Shuffle 1
df.orderBy("country")          # Shuffle 2

# Good: Combine operations
df.groupBy("country").count().orderBy("country")  # Still 2 shuffles, but optimized

# Best: Use sortWithinPartitions (no global shuffle)
df.sortWithinPartitions("country")
```

---

## 🧩 **3. Complex Data Types**

### **3.1 Arrays**

```python
from pyspark.sql.functions import array, explode, size, array_contains

# Create array column
df = spark.createDataFrame([
    (1, "Alice", ["Python", "Scala", "SQL"]),
    (2, "Bob", ["Java", "Python"]),
    (3, "Charlie", ["R", "Python", "Julia"])
], ["id", "name", "skills"])

df.show(truncate=False)
"""
+---+-------+---------------------+
|id |name   |skills               |
+---+-------+---------------------+
|1  |Alice  |[Python, Scala, SQL] |
|2  |Bob    |[Java, Python]       |
|3  |Charlie|[R, Python, Julia]   |
+---+-------+---------------------+
"""

# Explode array (one row per element)
df.select("name", explode("skills").alias("skill")).show()
"""
+-------+------+
|   name| skill|
+-------+------+
|  Alice|Python|
|  Alice| Scala|
|  Alice|   SQL|
|    Bob|  Java|
|    Bob|Python|
|Charlie|     R|
|Charlie|Python|
|Charlie| Julia|
+-------+------+
"""

# Array functions
df.select("name", size("skills").alias("num_skills")).show()
df.filter(array_contains("skills", "Python")).show()
```

---

### **3.2 Structs (Nested Objects)**

```python
from pyspark.sql.functions import struct, col

# Create struct column
df = spark.createDataFrame([
    (1, "Alice", 30, "alice@example.com"),
    (2, "Bob", 25, "bob@example.com")
], ["id", "name", "age", "email"])

# Nest columns into struct
df_nested = df.select(
    col("id"),
    struct("name", "age", "email").alias("user_info")
)

df_nested.show(truncate=False)
"""
+---+----------------------------+
|id |user_info                   |
+---+----------------------------+
|1  |{Alice, 30, alice@example.com}|
|2  |{Bob, 25, bob@example.com}  |
+---+----------------------------+
"""

# Access nested fields
df_nested.select("user_info.name", "user_info.age").show()

# Flatten struct
df_nested.select("id", "user_info.*").show()
```

---

### **3.3 JSON Data**

```python
from pyspark.sql.functions import from_json, to_json, get_json_object
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Sample JSON data
json_data = [
    ('{"name":"Alice","age":30,"city":"NYC"}',),
    ('{"name":"Bob","age":25,"city":"LA"}',)
]

df = spark.createDataFrame(json_data, ["json_string"])

# Define JSON schema
json_schema = StructType([
    StructField("name", StringType()),
    StructField("age", IntegerType()),
    StructField("city", StringType())
])

# Parse JSON
df_parsed = df.select(from_json(col("json_string"), json_schema).alias("data"))
df_parsed.select("data.*").show()

# Extract specific field without parsing entire JSON
df.select(get_json_object("json_string", "$.name").alias("name")).show()
```

---

## 🔄 **4. Slowly Changing Dimension (SCD) Type 2 in Spark**

**Goal:** Track historical changes to customer dimension.

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lit, current_date, md5, concat, row_number
from pyspark.sql.window import Window

spark = SparkSession.builder.appName("SCD Type 2").getOrCreate()

# Existing customer dimension (with history)
existing_customers = [
    (1, "C001", "Alice", "alice@old.com", "NYC", "2023-01-01", "9999-12-31", True),
    (2, "C002", "Bob", "bob@example.com", "LA", "2023-01-01", "9999-12-31", True)
]
existing_schema = ["sk", "customer_id", "name", "email", "city", "effective_date", "end_date", "is_current"]
dim_customer = spark.createDataFrame(existing_customers, existing_schema)

# New data from source system
new_customers = [
    ("C001", "Alice", "alice@new.com", "SF"),  # Email and city changed
    ("C002", "Bob", "bob@example.com", "LA"),  # No change
    ("C003", "Charlie", "charlie@example.com", "NYC")  # New customer
]
new_schema = ["customer_id", "name", "email", "city"]
source_data = spark.createDataFrame(new_customers, new_schema)

# SCD Type 2 Logic

# Step 1: Identify changes (hash current and new data)
dim_current = dim_customer.filter(col("is_current") == True) \
    .withColumn("current_hash", md5(concat(col("name"), col("email"), col("city"))))

source_with_hash = source_data \
    .withColumn("source_hash", md5(concat(col("name"), col("email"), col("city"))))

# Step 2: Join to find matches and changes
joined = source_with_hash.alias("src") \
    .join(
        dim_current.alias("dim"),
        col("src.customer_id") == col("dim.customer_id"),
        "left"
    )

# Step 3: Categorize records
categorized = joined.select(
    col("src.*"),
    col("dim.sk"),
    col("dim.current_hash"),
    when(col("dim.customer_id").isNull(), "INSERT")  # New customer
    .when(col("source_hash") != col("current_hash"), "UPDATE")  # Changed customer
    .otherwise("NO_CHANGE").alias("change_type")
)

categorized.show(truncate=False)

# Step 4: Handle INSERTs (new customers)
inserts = categorized.filter(col("change_type") == "INSERT") \
    .withColumn("sk", lit(None).cast("int")) \
    .withColumn("effective_date", current_date()) \
    .withColumn("end_date", lit("9999-12-31")) \
    .withColumn("is_current", lit(True)) \
    .select("sk", "customer_id", "name", "email", "city", "effective_date", "end_date", "is_current")

# Step 5: Handle UPDATEs (changed customers)
updates = categorized.filter(col("change_type") == "UPDATE")

# 5a: Expire old records
expired = updates.select(
    col("sk"),
    col("customer_id"),
    col("dim.name").alias("name"),
    col("dim.email").alias("email"),
    col("dim.city").alias("city"),
    col("dim.effective_date").alias("effective_date"),
    current_date().alias("end_date"),
    lit(False).alias("is_current")
)

# 5b: Insert new versions
new_versions = updates \
    .withColumn("sk", lit(None).cast("int")) \
    .withColumn("effective_date", current_date()) \
    .withColumn("end_date", lit("9999-12-31")) \
    .withColumn("is_current", lit(True)) \
    .select("sk", "customer_id", "name", "email", "city", "effective_date", "end_date", "is_current")

# Step 6: Union all records
unchanged = dim_customer.filter(
    ~col("customer_id").isin([r.customer_id for r in updates.select("customer_id").collect()])
)

final_dimension = unchanged \
    .union(expired) \
    .union(new_versions) \
    .union(inserts)

# Assign surrogate keys
window = Window.orderBy("customer_id", "effective_date")
final_dimension = final_dimension \
    .withColumn("sk", row_number().over(window))

print("Final Customer Dimension (SCD Type 2):")
final_dimension.orderBy("customer_id", "effective_date").show(truncate=False)
```

**Output:**
```
+---+-----------+-------+-------------------+----+--------------+----------+----------+
|sk |customer_id|name   |email              |city|effective_date|end_date  |is_current|
+---+-----------+-------+-------------------+----+--------------+----------+----------+
|1  |C001       |Alice  |alice@old.com      |NYC |2023-01-01    |2024-10-09|false     |
|2  |C001       |Alice  |alice@new.com      |SF  |2024-10-09    |9999-12-31|true      |
|3  |C002       |Bob    |bob@example.com    |LA  |2023-01-01    |9999-12-31|true      |
|4  |C003       |Charlie|charlie@example.com|NYC |2024-10-09    |9999-12-31|true      |
+---+-----------+-------+-------------------+----+--------------+----------+----------+
```

---

## 🐛 **5. Error Handling and Data Quality**

### **5.1 Handling Bad Records**

```python
# Option 1: PERMISSIVE mode (default) - Sets corrupt fields to NULL
df = spark.read \
    .option("mode", "PERMISSIVE") \
    .option("columnNameOfCorruptRecord", "_corrupt_record") \
    .csv("data.csv")

# Check for corrupt records
corrupt_records = df.filter(col("_corrupt_record").isNotNull())
corrupt_records.show()

# Option 2: DROPMALFORMED - Skip bad records
df_clean = spark.read \
    .option("mode", "DROPMALFORMED") \
    .csv("data.csv")

# Option 3: FAILFAST - Fail entire job if any bad record
df_strict = spark.read \
    .option("mode", "FAILFAST") \
    .csv("data.csv")
```

---

### **5.2 Data Validation**

```python
from pyspark.sql.functions import col, when

def validate_order_data(df):
    """
    Add data quality flags
    """
    return df.withColumn("quality_issues",
        when(col("order_id").isNull(), "missing_order_id")
        .when(col("quantity") <= 0, "invalid_quantity")
        .when(col("price") < 0, "negative_price")
        .when(col("order_date").isNull(), "missing_date")
        .otherwise(None)
    )

df_validated = validate_order_data(df)

# Count quality issues
df_validated.groupBy("quality_issues").count().show()

# Write bad records to quarantine
bad_records = df_validated.filter(col("quality_issues").isNotNull())
bad_records.write.mode("overwrite").parquet("s3://bucket/quarantine/")

# Process only good records
good_records = df_validated.filter(col("quality_issues").isNull())
```

---

## 📊 **6. Spark UI for Debugging**

### **Access Spark UI**

```python
# Spark UI runs at http://localhost:4040 by default
# If multiple Spark applications running: 4040, 4041, 4042, etc.
```

**Key tabs:**

**1. Jobs:** See all Spark jobs and their stages
- Identify slow jobs
- See which action triggered execution

**2. Stages:** See details of each stage
- Number of tasks
- Shuffle read/write
- Executor compute time

**3. Storage:** See cached DataFrames
- Memory usage
- Fraction cached

**4. SQL:** See query execution plans
- DAG visualization
- Physical plan

---

### **Reading Execution Plans**

```python
# Show physical plan
df.explain()

# Show detailed plan with cost estimates
df.explain("extended")

# Show formatted plan
df.explain("formatted")
```

**Example plan:**
```
== Physical Plan ==
*(2) HashAggregate(keys=[department#10], functions=[count(1)])
+- Exchange hashpartitioning(department#10, 200)
   +- *(1) HashAggregate(keys=[department#10], functions=[partial_count(1)])
      +- *(1) FileScan csv [department#10] ... 
```

**Key indicators:**
- `Exchange`: Shuffle (data movement across network)
- `FileScan`: Reading from storage
- `HashAggregate`: Aggregation operation
- `*(1)`, `*(2)`: WholeStageCodegen (Spark optimizes multiple operations into single generated code)

---

## 🎯 **Summary**

**Production Best Practices:**

1. **Always define schemas explicitly** (don't use `inferSchema` in production)
2. **Partition data by date** for efficient querying
3. **Use broadcast joins** for small tables (< 10 MB)
4. **Cache DataFrames** used multiple times
5. **Handle bad data** with PERMISSIVE mode + corrupt record column
6. **Validate data quality** and quarantine bad records
7. **Monitor Spark UI** for performance bottlenecks

**Performance Checklist:**
- ✅ Right-size partitions (128 MB - 1 GB each)
- ✅ Minimize shuffles (avoid unnecessary groupBy, orderBy)
- ✅ Broadcast small tables
- ✅ Cache frequently used DataFrames
- ✅ Use Parquet over CSV (10x faster, compressed)

---

**Next:** [EXPERT](./EXPERT.md) - Catalyst optimizer, Tungsten execution engine, advanced performance tuning

**Previous:** [BEGINNER](./BEGINNER.md)

**Master Roadmap:** [00-MASTER-ROADMAP.md](../../00-MASTER-ROADMAP.md)
