# Week 4: Apache Spark Fundamentals
## 🚀 EXPERT - Internals, Optimization & Production at Scale

---

## 🎯 **Learning Objectives**

- Understand Catalyst optimizer internals
- Master Tungsten execution engine
- Handle data skew in production
- Design production Spark clusters
- Debug memory issues (OOM, spill to disk)
- Build custom data sources
- Ace FAANG Spark interviews

---

## 🧠 **1. Catalyst Optimizer Deep Dive**

### **What is Catalyst?**

Catalyst is Spark's **query optimizer** that converts your DataFrame operations into optimized physical execution plans.

**Four phases:**

```
DataFrame API
     ↓
1. Analysis        (resolve column names, check types)
     ↓
2. Logical Optimization (push down filters, prune columns)
     ↓
3. Physical Planning (choose join strategies, generate candidates)
     ↓
4. Code Generation (WholeStageCodegen - generate Java bytecode)
     ↓
Executed by Tungsten
```

---

### **1.1 Logical Optimization Rules**

**Example: Filter Pushdown**

```python
# Your code
df = spark.read.parquet("users.parquet")
result = df.join(spark.read.parquet("orders.parquet"), "user_id") \
    .filter(col("country") == "USA")

# Unoptimized logical plan (filter after join)
"""
Filter (country = 'USA')
  └── Join (user_id)
       ├── Scan (users.parquet)
       └── Scan (orders.parquet)
"""

# Catalyst optimized plan (filter before join - reads less data!)
"""
Join (user_id)
  ├── Filter (country = 'USA')
  │    └── Scan (users.parquet)  ← Only scans USA users!
  └── Scan (orders.parquet)
"""
```

**Why this matters:** If 90% of users are NOT from USA, we avoid reading/joining 90% of data!

---

**Column Pruning**

```python
# Your code
df = spark.read.parquet("users.parquet")  # 50 columns
result = df.select("user_id", "name")

# Catalyst only reads 2 columns from Parquet, not all 50!
# Parquet is columnar, so this is HUGE savings
```

---

**Predicate Pushdown to Storage**

```python
# Your code
df = spark.read.parquet("orders.parquet") \
    .filter(col("date") >= "2024-01-01")

# Catalyst pushes filter to Parquet reader
# Parquet file metadata has min/max values per row group
# Skips entire row groups where max(date) < "2024-01-01"
```

---

### **1.2 Physical Planning**

Catalyst generates **multiple physical plans** and picks the cheapest one based on cost model.

```python
# Enable cost-based optimization
spark.conf.set("spark.sql.cbo.enabled", "true")

# Generate statistics for tables
df.write.mode("overwrite").parquet("users.parquet")
spark.sql("ANALYZE TABLE users COMPUTE STATISTICS")

# Now Catalyst uses statistics to choose better join strategies
```

**Join strategies Catalyst considers:**

1. **Broadcast Hash Join:** Small table broadcast to all nodes (fastest for small tables)
2. **Shuffle Hash Join:** Both tables shuffled, then hash joined
3. **Sort Merge Join:** Both tables sorted, then merge joined (good for pre-sorted data)

**How Catalyst chooses:**

```python
# If right table < 10 MB (spark.sql.autoBroadcastJoinThreshold)
→ Broadcast Hash Join

# Else, if both tables can fit in memory
→ Shuffle Hash Join

# Else
→ Sort Merge Join
```

---

### **1.3 WholeStageCodegen**

**Problem:** Interpreting operations one-by-one is slow.

```python
# Your code
df.filter(col("age") > 18) \
  .filter(col("country") == "USA") \
  .select("name", "email")

# Without codegen (slow):
for row in data:
    if row.age > 18:           # Function call overhead
        if row.country == "USA":  # Function call overhead
            yield (row.name, row.email)  # Function call overhead
```

**Solution: Generate Java bytecode**

Catalyst generates optimized Java code that executes all operations in a single loop:

```java
// Generated code (conceptual)
while (input.hasNext()) {
    InternalRow row = input.next();
    if (row.getInt(1) > 18 && row.getUTF8String(2).equals("USA")) {
        // Directly access memory, no overhead!
        resultRow.setUTF8String(0, row.getUTF8String(3));
        resultRow.setUTF8String(1, row.getUTF8String(4));
        output.write(resultRow);
    }
}
```

**Performance gain:** 2-10x faster than interpreted code!

**Check if codegen is used:**

```python
df.explain("codegen")
# Look for "WholeStageCodegen" in plan
```

---

## ⚙️ **2. Tungsten Execution Engine**

### **What is Tungsten?**

Tungsten is Spark's **execution engine** that runs optimized code on data.

**Key innovations:**

1. **Off-heap memory management** (bypass JVM garbage collector)
2. **Cache-aware computation** (CPU cache optimization)
3. **Code generation** (emit optimized bytecode)

---

### **2.1 Memory Management**

**Problem:** JVM garbage collection pauses (stop-the-world events)

**Solution:** Tungsten manages memory manually using `sun.misc.Unsafe`

```
JVM Heap Memory (managed by GC)
  ↓
  Storage for Java objects (slow, GC overhead)

Off-Heap Memory (managed by Tungsten)
  ↓
  Binary format (fast, no GC!)
  ↓
  [4 bytes: age][8 bytes: salary][16 bytes: name_ptr]
```

**Configure off-heap memory:**

```python
spark = SparkSession.builder \
    .config("spark.memory.offHeap.enabled", "true") \
    .config("spark.memory.offHeap.size", "10g") \
    .getOrCreate()
```

---

### **2.2 Cache-Friendly Computation**

**Modern CPUs have caches:**

```
CPU Registers (fastest, ~1 ns access)
  ↓
L1 Cache (~1 ns)
  ↓
L2 Cache (~10 ns)
  ↓
L3 Cache (~40 ns)
  ↓
RAM (~100 ns)
  ↓
Disk (~10,000,000 ns)
```

**Tungsten optimization:** Store data in contiguous memory (better cache locality)

```python
# Bad: Row-based storage (each row is separate object)
Row(id=1, name="Alice", age=30)  # Object 1
Row(id=2, name="Bob", age=25)    # Object 2
# CPU fetches Object 1, cache miss on Object 2

# Good: Columnar storage (all ages together)
[30, 25, 28, 22, ...]  # All in contiguous memory
# CPU fetches ages, likely all in same cache line!
```

---

## 🔥 **3. Handling Data Skew**

### **What is Data Skew?**

**Problem:** Some partitions have WAY more data than others.

```python
# Example: Grouping users by country
df.groupBy("country").count()

# Partition distribution:
# USA: 1,000,000 rows (one task processing this is slow!)
# UK:  100,000 rows
# Canada: 50,000 rows
# Other countries: ~1,000 rows each
```

**Impact:** One task takes 10x longer → entire job waits for that one task!

---

### **3.1 Detecting Skew**

**Check Spark UI:**
- Go to **Stages** tab
- Look at task durations
- If max duration >> median duration → skew!

**Example:**
```
Task 1: 5 seconds
Task 2: 5 seconds
Task 3: 5 seconds
Task 4: 120 seconds  ← SKEW! (This task has too much data)
Task 5: 5 seconds
```

---

### **3.2 Solution 1: Salting**

**Idea:** Add random prefix to skewed key to split it across multiple partitions.

```python
from pyspark.sql.functions import concat, lit, rand, floor

# Original (skewed)
df.groupBy("country").count()  # USA partition is huge

# Salting (distribute USA across 10 partitions)
df_salted = df.withColumn(
    "salted_country",
    when(col("country") == "USA", 
         concat(col("country"), lit("_"), floor(rand() * 10).cast("int")))
    .otherwise(col("country"))
)

result = df_salted.groupBy("salted_country").count()

# Now USA is split into:
# USA_0, USA_1, USA_2, ..., USA_9 (10 partitions instead of 1!)

# Final aggregation
final = result.withColumn(
    "country",
    when(col("salted_country").startswith("USA_"), lit("USA"))
    .otherwise(col("salted_country"))
).groupBy("country").sum("count")
```

---

### **3.3 Solution 2: Adaptive Query Execution (AQE)**

**Spark 3.0+ feature:** Automatically handles skew!

```python
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256MB")

# Spark detects skew at runtime and splits large partitions
```

**How AQE works:**
1. Runs initial shuffle
2. Detects partitions > 256 MB (configurable)
3. Splits those partitions into smaller ones
4. Re-runs join with balanced partitions

---

### **3.4 Solution 3: Broadcast Join (if possible)**

```python
# If skewed table is small enough, broadcast it
large_df.join(broadcast(small_skewed_df), "key")
# No shuffle = no skew problem!
```

---

## 💾 **4. Memory Tuning**

### **4.1 Spark Memory Model**

```
Total Executor Memory (e.g., 10 GB)
  ├── Reserved Memory (300 MB) - Spark internals
  ├── User Memory (25%) - Your UDFs, Python objects
  └── Spark Memory (75%)
       ├── Storage Memory (50%) - Cached DataFrames
       └── Execution Memory (50%) - Shuffles, joins, sorts
```

**Configure memory:**

```python
spark = SparkSession.builder \
    .config("spark.executor.memory", "10g") \
    .config("spark.memory.fraction", "0.75") \
    .config("spark.memory.storageFraction", "0.5") \
    .getOrCreate()
```

---

### **4.2 Debugging OOM (Out of Memory)**

**Common causes:**

**1. Collecting too much data to driver**

```python
# Bad (brings all data to driver)
data = df.collect()  # If df is 100 GB, driver OOM! ❌

# Good (process in distributed manner)
df.write.parquet("output")  # Executors write directly ✅
```

---

**2. Too many partitions**

```python
# Bad (200,000 partitions for 1 GB data)
df.repartition(200000)  # Each partition = 5 KB, huge overhead!

# Good (10 partitions)
df.repartition(10)  # Each partition = 100 MB
```

---

**3. Caching too much**

```python
# Bad (caches 100 GB DataFrame with only 10 GB RAM)
df.cache()  # Spills to disk, becomes slower than not caching!

# Good (cache only if it fits in memory)
# Or use MEMORY_AND_DISK storage level
df.persist(StorageLevel.MEMORY_AND_DISK)
```

---

**4. Shuffle spill**

**What is spill?** When shuffle data doesn't fit in memory, Spark writes to disk (slow!).

**Check Spark UI:**
- Stages → Shuffle Write / Shuffle Read
- If "Spill (Memory)" and "Spill (Disk)" > 0 → memory pressure!

**Fix:**

```python
# Increase executor memory
spark.conf.set("spark.executor.memory", "20g")

# Increase shuffle partitions (more partitions = less data per partition)
spark.conf.set("spark.sql.shuffle.partitions", "400")

# Use more executors (distribute load)
spark.conf.set("spark.executor.instances", "50")
```

---

## 🏗️ **5. Production Cluster Design**

### **5.1 Sizing Executors**

**Rule of thumb:**

```python
# Executor cores: 4-5 cores per executor
# (More cores = more parallelism, but diminishing returns after 5)

# Executor memory: 
# - YARN: Max 64 GB per executor (YARN overhead)
# - Kubernetes: Can go higher, but 32-64 GB is typical

# Number of executors:
# Total cores in cluster / cores_per_executor
```

**Example cluster:**

```
Cluster: 10 nodes, each with 16 cores and 64 GB RAM

Executor configuration:
  - Cores per executor: 5
  - Memory per executor: 32 GB
  - Executors per node: 16 / 5 = 3 executors
  - Total executors: 10 nodes * 3 = 30 executors
  
Total capacity:
  - Cores: 30 * 5 = 150 cores
  - Memory: 30 * 32 GB = 960 GB
```

**Spark submit command:**

```bash
spark-submit \
  --master yarn \
  --deploy-mode cluster \
  --num-executors 30 \
  --executor-cores 5 \
  --executor-memory 32g \
  --driver-memory 8g \
  --conf spark.sql.shuffle.partitions=300 \
  my_job.py
```

---

### **5.2 Dynamic Allocation**

**Problem:** You don't always need 30 executors (wastes resources during light load).

**Solution:** Let Spark dynamically add/remove executors based on workload.

```python
spark = SparkSession.builder \
    .config("spark.dynamicAllocation.enabled", "true") \
    .config("spark.dynamicAllocation.minExecutors", "5") \
    .config("spark.dynamicAllocation.maxExecutors", "50") \
    .config("spark.dynamicAllocation.initialExecutors", "10") \
    .getOrCreate()
```

**How it works:**
1. Starts with 10 executors
2. If tasks are queued → adds executors (up to 50)
3. If executors idle for 60s → removes them (down to 5)

---

## 🛠️ **6. Custom Data Sources**

### **Building a Custom Data Source**

**Use case:** Read from proprietary database or API.

```python
from pyspark.sql.datasource import DataSource, DataSourceReader
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

class CustomDataSource(DataSource):
    """
    Custom data source to read from external API
    """
    
    @classmethod
    def name(cls):
        return "custom"
    
    def schema(self):
        return StructType([
            StructField("id", IntegerType(), False),
            StructField("name", StringType(), True),
            StructField("value", IntegerType(), True)
        ])
    
    def reader(self, schema):
        return CustomDataSourceReader(schema)

class CustomDataSourceReader(DataSourceReader):
    def __init__(self, schema):
        self.schema = schema
    
    def read(self, partition):
        # Your custom logic to fetch data
        # (e.g., call REST API, read from proprietary DB)
        
        # Example: Generate sample data
        data = [
            (1, "Alice", 100),
            (2, "Bob", 200),
            (3, "Charlie", 300)
        ]
        
        for row in data:
            yield row

# Register custom data source
spark.dataSource.register("custom", CustomDataSource)

# Use it
df = spark.read.format("custom").load()
df.show()
```

---

## 🎤 **7. FAANG Interview Questions**

### **Question 1: Explain Catalyst Optimizer Phases**

**Answer:**

Catalyst has 4 phases:

1. **Analysis:** Resolves column names using catalog, checks types
2. **Logical Optimization:** Applies rule-based optimizations:
   - Filter pushdown (move filters before joins)
   - Column pruning (only read needed columns)
   - Constant folding (`WHERE 1+1=2` → `WHERE TRUE`)
3. **Physical Planning:** Generates multiple physical plans, picks cheapest:
   - Chooses join strategies (broadcast vs shuffle hash vs sort merge)
   - Uses statistics from `ANALYZE TABLE`
4. **Code Generation:** WholeStageCodegen emits optimized Java bytecode

---

### **Question 2: How would you optimize this query?**

```python
# Given query
df = spark.read.parquet("users")  # 1 billion rows, 50 columns
result = df.join(spark.read.parquet("orders"), "user_id") \
    .filter(col("country") == "USA") \
    .select("user_id", "order_id", "amount")
```

**Optimizations:**

```python
# 1. Filter pushdown (do it manually before join)
users = spark.read.parquet("users") \
    .filter(col("country") == "USA") \
    .select("user_id", "country")  # Column pruning

orders = spark.read.parquet("orders") \
    .select("user_id", "order_id", "amount")  # Column pruning

# 2. If users (after filter) is small, broadcast it
result = orders.join(broadcast(users), "user_id") \
    .select("user_id", "order_id", "amount")

# 3. Partition data by country (if this is common query pattern)
# Then filter will read only USA partition!
```

---

### **Question 3: What causes shuffle and how to minimize it?**

**Answer:**

**Shuffle causes:**
- `groupBy()`, `join()`, `orderBy()`, `repartition()`, `distinct()`

**Minimize shuffle:**

1. **Use broadcast join** for small tables (< 10 MB)
2. **Pre-partition data** by common join keys
3. **Coalesce instead of repartition** (when reducing partitions)
4. **Use `mapPartitions` instead of `map`** (process entire partition at once)
5. **Enable AQE** (Adaptive Query Execution) to handle skew

---

### **Question 4: Explain data skew and solutions**

**Answer:**

**Data skew:** Uneven distribution of data across partitions.

**Example:**
```python
# 90% of users are from USA
df.groupBy("country").count()
# USA partition: 900M rows
# Other countries: 100M rows total
```

**Solutions:**

1. **Salting:** Add random suffix to skewed key
2. **AQE:** `spark.sql.adaptive.skewJoin.enabled=true`
3. **Broadcast join:** If skewed table is small
4. **Filter skewed values:** Process separately

**Code example:**

```python
# Salting for skewed key
df_salted = df.withColumn(
    "salted_key",
    when(col("country") == "USA",
         concat(col("country"), lit("_"), (rand() * 10).cast("int")))
    .otherwise(col("country"))
)
```

---

### **Question 5: How would you process 100 TB of data in Spark?**

**Answer:**

**Strategy:**

1. **Cluster sizing:**
   - 100 TB / 128 MB per partition = ~800,000 partitions
   - Need ~160,000 cores (5 tasks per core concurrently)
   - ~1,000 nodes with 160 cores each
   - Total memory: ~50 TB (2x shuffle data size)

2. **Optimizations:**
   - Read Parquet (columnar, compressed ~5x)
   - Partition by date/region (prune partitions)
   - Use broadcast join for small dimensions
   - Enable AQE for skew handling
   - Dynamic allocation (scale down after heavy shuffles)

3. **Processing strategy:**
   - Process incrementally (daily/hourly batches)
   - Use Delta Lake for ACID transactions
   - Checkpoint intermediate results

**Sample config:**

```python
spark = SparkSession.builder \
    .config("spark.executor.memory", "64g") \
    .config("spark.executor.cores", "5") \
    .config("spark.dynamicAllocation.maxExecutors", "2000") \
    .config("spark.sql.shuffle.partitions", "10000") \
    .config("spark.sql.adaptive.enabled", "true") \
    .getOrCreate()
```

---

### **Question 6: Design a real-time fraud detection system with Spark**

**Answer:**

**Architecture:**

```
Transactions → Kafka → Spark Streaming → Feature Engineering → ML Model → Alert
```

**Implementation:**

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window, avg, count

spark = SparkSession.builder \
    .appName("Fraud Detection") \
    .getOrCreate()

# Read from Kafka
transactions = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "transactions") \
    .load()

# Parse JSON
from pyspark.sql.functions import from_json
schema = StructType([
    StructField("user_id", StringType()),
    StructField("amount", DoubleType()),
    StructField("timestamp", TimestampType())
])

parsed = transactions.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

# Feature engineering (windowed aggregations)
features = parsed \
    .withWatermark("timestamp", "1 minute") \
    .groupBy(
        col("user_id"),
        window("timestamp", "5 minutes")
    ).agg(
        count("*").alias("txn_count"),
        avg("amount").alias("avg_amount"),
        sum("amount").alias("total_amount")
    )

# Flag suspicious transactions
suspicious = features.filter(
    (col("txn_count") > 10) |  # More than 10 txns in 5 min
    (col("avg_amount") > 1000)  # Average > $1000
)

# Write alerts to Kafka
query = suspicious.selectExpr("user_id as key", "to_json(struct(*)) as value") \
    .writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("topic", "fraud_alerts") \
    .option("checkpointLocation", "/tmp/checkpoint") \
    .start()

query.awaitTermination()
```

---

### **Question 7: Explain Tungsten's memory management**

**Answer:**

Tungsten uses **off-heap memory** to avoid JVM garbage collection overhead.

**Key concepts:**

1. **Off-heap allocation:** Uses `sun.misc.Unsafe` to allocate memory outside JVM heap
2. **Binary format:** Stores data in binary (not Java objects)
3. **No GC pauses:** GC doesn't scan off-heap memory

**Memory layout:**

```
[4 bytes: null bits][4 bytes: int][8 bytes: long][offset to string]
```

**Benefits:**
- No GC pauses (critical for low-latency apps)
- Compact representation (less memory)
- Cache-friendly (contiguous memory)

**Configuration:**

```python
spark.conf.set("spark.memory.offHeap.enabled", "true")
spark.conf.set("spark.memory.offHeap.size", "10g")
```

---

### **Question 8: How to handle slowly changing dimensions (SCD) in Spark?**

**Answer:** (See INTERMEDIATE.md for full code example)

**SCD Type 2 strategy:**

1. **Hash current and new records** (to detect changes)
2. **Join source with existing dimension**
3. **Categorize records:**
   - INSERT: New records
   - UPDATE: Changed records
   - NO_CHANGE: Unchanged records
4. **Expire old versions** (set `end_date` and `is_current=false`)
5. **Insert new versions** (with new `effective_date`)

**Key challenge:** Generating surrogate keys in distributed manner.

**Solution:** Use `row_number()` with window function or UUID.

---

### **Question 9: What is WholeStageCodegen?**

**Answer:**

WholeStageCodegen is Catalyst's **code generation optimization** that fuses multiple operators into a single generated function.

**Example:**

```python
# Your code
df.filter(col("age") > 18).filter(col("country") == "USA").select("name")

# Generated Java code (conceptual)
while (hasNext()) {
    row = next();
    if (row.age > 18 && row.country.equals("USA")) {
        emit(row.name);
    }
}
```

**Benefits:**
- No virtual function calls (faster)
- Better CPU cache utilization
- JIT compiler optimizations

**Check if enabled:**

```python
df.explain("codegen")
# Look for "*WholeStageCodegen*" in output
```

---

### **Question 10: Describe Spark's DAG execution model**

**Answer:**

**DAG (Directed Acyclic Graph):** Graph of transformations and dependencies.

**Stages:** Group of tasks that can run in parallel without shuffle.

**Example:**

```python
df = spark.read.csv("data.csv")  # Stage 1: Read
df2 = df.filter(col("age") > 18)  # Stage 1: Filter (no shuffle)
df3 = df2.groupBy("country").count()  # Stage 2: GroupBy (shuffle!)
```

**DAG:**

```
Stage 1: Read CSV → Filter
         ↓ (shuffle)
Stage 2: GroupBy → Count
```

**Stage boundaries:**
- Shuffle operations (`groupBy`, `join`, `orderBy`)
- Actions (`count`, `show`, `write`)

**Task scheduling:**
- Stage 1 runs first
- After Stage 1 completes, Stage 2 starts
- Tasks within stage run in parallel

---

## 🎯 **Summary**

**Catalyst Optimizer:**
- Logical optimization (filter pushdown, column pruning)
- Physical planning (choose join strategies)
- Code generation (WholeStageCodegen)

**Tungsten:**
- Off-heap memory (no GC)
- Binary data format (compact)
- Cache-aware computation

**Performance:**
- Handle skew (salting, AQE)
- Minimize shuffle (broadcast, pre-partition)
- Right-size executors (5 cores, 32-64 GB)

**Production:**
- Dynamic allocation
- Monitor Spark UI
- Checkpoint streaming apps

---

**Next:** [WHITEPAPERS](./WHITEPAPERS.md) - Original Spark paper and research

**Previous:** [INTERMEDIATE](./INTERMEDIATE.md)

**Master Roadmap:** [00-MASTER-ROADMAP.md](../../00-MASTER-ROADMAP.md)
