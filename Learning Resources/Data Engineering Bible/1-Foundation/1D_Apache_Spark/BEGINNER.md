# Week 4: Apache Spark Fundamentals
## 🌱 BEGINNER - Spark for Distributed Data Processing

---

## 🎯 **What You'll Learn**

- What is Apache Spark and why it replaced MapReduce
- RDDs vs DataFrames vs Datasets (which to use when)
- Spark's execution model (lazy evaluation, DAG)
- Writing your first Spark job in Python (PySpark)
- Reading/writing data (CSV, Parquet, JSON)

---

## 📖 **The Factory Analogy: Spark vs MapReduce**

### **MapReduce = Old Factory (Disk-Based)**

Imagine a car factory that writes everything to paper:

```
Step 1: Build engine → Write to warehouse
Step 2: Read from warehouse → Build chassis → Write to warehouse
Step 3: Read from warehouse → Assemble car → Write to warehouse

Each step reads/writes to disk! Slow! 🐢
```

**MapReduce workflow:**
```
Input (HDFS) → Map → Write to disk
               ↓
          Read from disk → Reduce → Write to disk
                                      ↓
                                   Output (HDFS)
```

---

### **Spark = Modern Factory (In-Memory)**

Now imagine a smart factory with conveyor belts:

```
Step 1: Build engine → Pass on conveyor belt
Step 2: Receive engine → Build chassis → Pass on conveyor belt
Step 3: Receive chassis → Assemble car → Done!

Everything stays in memory (RAM)! Fast! ⚡
```

**Spark workflow:**
```
Input (HDFS/S3) → Transform (in RAM) → Transform (in RAM) → Output
```

**Speed comparison:**
- MapReduce: 10 minutes ❌
- Spark: 30 seconds ✅ (20x faster!)

---

## 🚀 **1. What is Apache Spark?**

### **Definition**

> **Apache Spark is a distributed data processing engine that runs computations in-memory, making it 10-100x faster than MapReduce.**

**Key Features:**
- ⚡ **In-memory processing:** Data stays in RAM between steps
- 🔄 **Lazy evaluation:** Builds execution plan, optimizes before running
- 📊 **Unified API:** Batch, streaming, SQL, ML in one framework
- 🌍 **Distributed:** Runs on clusters (1 to 10,000 machines)

**Created:** UC Berkeley (2009), Apache project (2013)  
**Written in:** Scala (runs on JVM)  
**APIs:** Scala, Java, Python (PySpark), R, SQL

---

### **When to Use Spark**

**Use Spark for:**
- ✅ ETL pipelines processing GB-TB of data daily
- ✅ Ad-hoc data analysis (interactive queries)
- ✅ Machine learning on large datasets
- ✅ Log processing, clickstream analysis
- ✅ Real-time streaming (Spark Streaming)

**Don't use Spark for:**
- ❌ Small datasets (< 1 GB) - Use pandas, SQL
- ❌ OLTP transactions - Use PostgreSQL, MySQL
- ❌ Low-latency queries (< 1 second) - Use Elasticsearch, Cassandra

---

## 📦 **2. Spark Data Structures**

### **RDD: Resilient Distributed Dataset (Low-Level)**

**Think:** Raw building blocks, like assembly language

```python
from pyspark import SparkContext

sc = SparkContext("local", "RDD Example")

# Create RDD from list
numbers = sc.parallelize([1, 2, 3, 4, 5])

# Transform: Multiply each by 2
doubled = numbers.map(lambda x: x * 2)

# Action: Collect results
result = doubled.collect()
print(result)  # [2, 4, 6, 8, 10]
```

**Characteristics:**
- Low-level API (you control partitioning, caching)
- Functional programming (map, filter, reduce)
- No schema (just data)
- Hard to optimize (Spark can't understand your lambda functions)

---

### **DataFrame: Structured Data (High-Level)**

**Think:** SQL tables with schema, like pandas but distributed

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("DataFrame Example").getOrCreate()

# Create DataFrame from data
data = [
    ("Alice", 30, "Engineering"),
    ("Bob", 25, "Sales"),
    ("Charlie", 35, "Engineering")
]
columns = ["name", "age", "department"]

df = spark.createDataFrame(data, columns)

# Show data
df.show()
"""
+-------+---+------------+
|   name|age|  department|
+-------+---+------------+
|  Alice| 30|Engineering|
|    Bob| 25|       Sales|
|Charlie| 35|Engineering|
+-------+---+------------+
"""

# SQL-like operations
df.filter(df.age > 25).select("name", "department").show()
"""
+-------+------------+
|   name|  department|
+-------+------------+
|  Alice|Engineering|
|Charlie|Engineering|
+-------+------------+
"""
```

**Characteristics:**
- High-level API (declarative, like SQL)
- Schema enforced (typed columns)
- Catalyst optimizer (Spark optimizes your queries automatically)
- **Preferred for 95% of use cases**

---

### **Dataset: Typed DataFrames (Scala/Java Only)**

**Note:** Not available in Python (PySpark only has DataFrames)

```scala
// Scala code
case class Person(name: String, age: Int, department: String)

val ds: Dataset[Person] = df.as[Person]

// Type-safe operations (compile-time checking)
ds.filter(_.age > 25).map(_.name).show()
```

**When to use:**
- Scala projects needing compile-time type safety
- Otherwise, use DataFrames (Python, Scala, Java)

---

## 🛠️ **3. Your First Spark Job (PySpark)**

### **Installation**

```bash
# Install PySpark
pip install pyspark

# Verify
python -c "import pyspark; print(pyspark.__version__)"
```

---

### **Example 1: Word Count (The "Hello World" of Spark)**

```python
from pyspark.sql import SparkSession

# Create Spark session
spark = SparkSession.builder \
    .appName("Word Count") \
    .master("local[*]") \
    .getOrCreate()

# Sample text data
text = """
Apache Spark is a unified analytics engine.
Spark runs on Hadoop, Kubernetes, standalone.
Spark provides high-level APIs in Python, Scala, Java.
"""

# Create RDD from text
lines = spark.sparkContext.parallelize(text.split('\n'))

# Word count logic
word_counts = lines \
    .flatMap(lambda line: line.split()) \
    .map(lambda word: (word.lower(), 1)) \
    .reduceByKey(lambda a, b: a + b)

# Collect results
results = word_counts.collect()
for word, count in sorted(results, key=lambda x: -x[1])[:5]:
    print(f"{word}: {count}")

"""
Output:
spark: 3
in: 1
apis: 1
engine: 1
analytics: 1
"""

spark.stop()
```

---

### **Example 2: DataFrame Operations (More Pythonic)**

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum, avg, desc

spark = SparkSession.builder.appName("Sales Analysis").getOrCreate()

# Sample sales data
data = [
    ("2024-01-01", "Alice", "Laptop", 1000),
    ("2024-01-01", "Bob", "Mouse", 20),
    ("2024-01-02", "Alice", "Keyboard", 50),
    ("2024-01-02", "Charlie", "Monitor", 300),
    ("2024-01-03", "Bob", "Laptop", 1000),
]
columns = ["date", "customer", "product", "amount"]

df = spark.createDataFrame(data, columns)

# Show original data
print("Original Data:")
df.show()

# Analysis 1: Total sales per customer
print("Total Sales per Customer:")
df.groupBy("customer") \
    .agg(sum("amount").alias("total_sales")) \
    .orderBy(desc("total_sales")) \
    .show()

# Analysis 2: Number of transactions per product
print("Transactions per Product:")
df.groupBy("product") \
    .agg(count("*").alias("num_transactions")) \
    .show()

# Analysis 3: Filter expensive items
print("Expensive Items (>= $500):")
df.filter(col("amount") >= 500).show()

spark.stop()
```

**Output:**
```
Original Data:
+----------+--------+--------+------+
|      date|customer| product|amount|
+----------+--------+--------+------+
|2024-01-01|   Alice|  Laptop|  1000|
|2024-01-01|     Bob|   Mouse|    20|
|2024-01-02|   Alice|Keyboard|    50|
|2024-01-02| Charlie| Monitor|   300|
|2024-01-03|     Bob|  Laptop|  1000|
+----------+--------+--------+------+

Total Sales per Customer:
+--------+-----------+
|customer|total_sales|
+--------+-----------+
|   Alice|       1050|
|     Bob|       1020|
| Charlie|        300|
+--------+-----------+

Transactions per Product:
+--------+-----------------+
| product|num_transactions|
+--------+-----------------+
|  Laptop|                2|
|Keyboard|                1|
|   Mouse|                1|
| Monitor|                1|
+--------+-----------------+

Expensive Items (>= $500):
+----------+--------+-------+------+
|      date|customer|product|amount|
+----------+--------+-------+------+
|2024-01-01|   Alice| Laptop|  1000|
|2024-01-03|     Bob| Laptop|  1000|
+----------+--------+-------+------+
```

---

## 📂 **4. Reading and Writing Data**

### **Reading CSV**

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("CSV Example").getOrCreate()

# Read CSV with header
df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv("data/sales.csv")

df.printSchema()
df.show(5)

# Alternative: Explicitly define schema
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

schema = StructType([
    StructField("date", StringType(), True),
    StructField("customer", StringType(), True),
    StructField("product", StringType(), True),
    StructField("amount", IntegerType(), True)
])

df = spark.read.schema(schema).csv("data/sales.csv")
```

---

### **Reading Parquet (Recommended for Big Data)**

```python
# Read Parquet (columnar format, compressed)
df = spark.read.parquet("s3://my-bucket/sales_data/")

# Parquet preserves schema automatically
df.printSchema()
```

**Why Parquet?**
- ✅ Compressed (10x smaller than CSV)
- ✅ Columnar (fast for analytics)
- ✅ Schema embedded (no need to infer)
- ✅ Predicate pushdown (skip irrelevant files)

---

### **Reading JSON**

```python
# Read JSON (one JSON object per line)
df = spark.read.json("data/events.json")

# Nested JSON
df = spark.read.option("multiLine", "true").json("data/nested.json")
```

---

### **Writing Data**

```python
# Write to Parquet (partitioned by date)
df.write \
    .mode("overwrite") \
    .partitionBy("date") \
    .parquet("output/sales_by_date/")

# Write to CSV
df.write \
    .mode("overwrite") \
    .option("header", "true") \
    .csv("output/sales.csv")

# Write to single file (repartition to 1)
df.repartition(1).write \
    .mode("overwrite") \
    .csv("output/sales_single_file.csv")
```

**Write modes:**
- `overwrite`: Delete existing data, write new
- `append`: Add to existing data
- `ignore`: Skip if data exists
- `error`: Fail if data exists (default)

---

## ⚙️ **5. Lazy Evaluation and DAG**

### **Lazy Evaluation**

**Key Concept:** Spark doesn't execute transformations immediately. It builds a plan and executes when you call an action.

```python
# These are transformations (lazy - no execution yet)
df1 = spark.read.csv("data.csv")
df2 = df1.filter(col("age") > 25)
df3 = df2.select("name", "salary")
df4 = df3.groupBy("name").agg(sum("salary"))

# This is an action (triggers execution)
df4.show()  # NOW Spark executes the entire pipeline
```

**Transformations (lazy):**
- `filter()`, `select()`, `groupBy()`, `join()`, `orderBy()`

**Actions (eager - trigger execution):**
- `show()`, `collect()`, `count()`, `write()`, `save()`

---

### **Why Lazy Evaluation?**

**Optimization opportunity:**

```python
# User's code
df = spark.read.csv("sales.csv")
df = df.filter(col("country") == "USA")
df = df.filter(col("amount") > 1000)
df = df.select("customer", "amount")
df.show()

# Spark optimizes to:
# 1. Push filters down (read only USA rows with amount > 1000)
# 2. Project only needed columns (customer, amount)
# 3. Minimize data shuffling
```

**Without lazy evaluation:** Each transformation would execute immediately (inefficient).

---

### **DAG: Directed Acyclic Graph**

**Spark builds an execution plan:**

```
Read CSV
    ↓
Filter (country = USA)
    ↓
Filter (amount > 1000)
    ↓
Select (customer, amount)
    ↓
Show
```

**View DAG in Spark UI:**
```python
# Access Spark UI at http://localhost:4040
# See DAG visualization under "SQL" tab
```

---

## 🧩 **6. Transformations vs Actions**

### **Transformations (Return New DataFrame)**

```python
# Narrow transformations (no shuffle, fast)
df.filter(col("age") > 25)        # Filter rows
df.select("name", "age")          # Select columns
df.withColumn("age_next", col("age") + 1)  # Add column
df.drop("middle_name")            # Drop column

# Wide transformations (shuffle data, slow)
df.groupBy("department").agg(sum("salary"))  # Aggregation
df.orderBy(desc("salary"))        # Sorting
df.join(other_df, "customer_id") # Joins
```

**Narrow vs Wide:**
- **Narrow:** Each output partition depends on ONE input partition (fast, no shuffle)
- **Wide:** Output partition depends on MULTIPLE input partitions (slow, requires shuffle)

---

### **Actions (Return Results or Write Data)**

```python
# Collect results to driver
df.show()                # Show first 20 rows
df.collect()             # Get all rows as list (careful with large data!)
df.count()               # Count rows
df.first()               # Get first row
df.take(5)               # Get first 5 rows

# Write to storage
df.write.parquet("output/")
df.write.csv("output.csv")

# Other actions
df.describe().show()     # Statistics (count, mean, stddev, min, max)
```

---

## 📊 **7. Common Operations Cheat Sheet**

### **Filtering**

```python
# Single condition
df.filter(col("age") > 25)
df.filter("age > 25")  # SQL-style string

# Multiple conditions
df.filter((col("age") > 25) & (col("department") == "Sales"))

# OR condition
df.filter((col("age") < 25) | (col("age") > 60))

# IN clause
df.filter(col("department").isin(["Sales", "Marketing"]))

# NULL checks
df.filter(col("email").isNotNull())
```

---

### **Selecting and Renaming**

```python
# Select columns
df.select("name", "age")

# Rename columns
df.select(col("name").alias("employee_name"), col("age"))

# Add new column
df.withColumn("age_in_10_years", col("age") + 10)

# Drop columns
df.drop("middle_name", "ssn")
```

---

### **Aggregations**

```python
from pyspark.sql.functions import sum, avg, max, min, count, countDistinct

# Group by single column
df.groupBy("department").agg(
    count("*").alias("num_employees"),
    avg("salary").alias("avg_salary"),
    max("salary").alias("max_salary")
)

# Group by multiple columns
df.groupBy("department", "job_title").agg(count("*"))
```

---

### **Joins**

```python
# Inner join (default)
df1.join(df2, df1.customer_id == df2.customer_id, "inner")

# Left join
df1.join(df2, "customer_id", "left")

# Right join
df1.join(df2, "customer_id", "right")

# Full outer join
df1.join(df2, "customer_id", "outer")

# Anti join (rows in df1 NOT in df2)
df1.join(df2, "customer_id", "anti")
```

---

### **Sorting**

```python
# Ascending
df.orderBy("age")
df.orderBy(col("age").asc())

# Descending
df.orderBy(col("salary").desc())

# Multiple columns
df.orderBy(col("department").asc(), col("salary").desc())
```

---

## 🎯 **Summary**

**Key Takeaways:**

1. **Spark = In-memory MapReduce** (10-100x faster)
2. **DataFrame API > RDD API** (use DataFrames 95% of the time)
3. **Lazy evaluation** = Spark optimizes before executing
4. **Transformations are lazy, actions trigger execution**
5. **Parquet > CSV** for big data (compressed, columnar, fast)

**Your First Spark Job Checklist:**
- ✅ Create SparkSession
- ✅ Read data (CSV, Parquet, JSON)
- ✅ Transform (filter, select, groupBy)
- ✅ Action (show, write)
- ✅ Stop SparkSession

---

## ✅ **Practice Exercise**

**Task:** Analyze e-commerce orders

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, count, avg, desc

spark = SparkSession.builder.appName("E-commerce Analysis").getOrCreate()

# Sample data
orders = [
    ("2024-01-01", "Alice", "Laptop", 1000, 1),
    ("2024-01-01", "Bob", "Mouse", 20, 2),
    ("2024-01-02", "Alice", "Keyboard", 50, 1),
    ("2024-01-02", "Charlie", "Monitor", 300, 1),
    ("2024-01-03", "Bob", "Laptop", 1000, 1),
    ("2024-01-03", "Alice", "Mouse", 20, 3),
]
columns = ["date", "customer", "product", "price", "quantity"]

df = spark.createDataFrame(orders, columns)

# TODO: Calculate total revenue per customer
# TODO: Find top 3 most popular products by quantity sold
# TODO: Calculate average order value per day
```

<details>
<summary>Solution</summary>

```python
# Total revenue per customer
df.withColumn("revenue", col("price") * col("quantity")) \
    .groupBy("customer") \
    .agg(sum("revenue").alias("total_revenue")) \
    .orderBy(desc("total_revenue")) \
    .show()

# Top 3 products by quantity
df.groupBy("product") \
    .agg(sum("quantity").alias("total_quantity")) \
    .orderBy(desc("total_quantity")) \
    .limit(3) \
    .show()

# Average order value per day
df.withColumn("order_value", col("price") * col("quantity")) \
    .groupBy("date") \
    .agg(avg("order_value").alias("avg_order_value")) \
    .show()
```
</details>

---

**Next:** [INTERMEDIATE](./INTERMEDIATE.md) - Production ETL with PySpark, performance tuning, partitioning strategies

**Master Roadmap:** [00-MASTER-ROADMAP.md](../../00-MASTER-ROADMAP.md)
