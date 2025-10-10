# Week 4: Apache Spark Fundamentals
## 📚 WHITEPAPERS - Research Papers & Evolution

---

## 🎯 **Overview**

This section covers the foundational research papers and evolution of Apache Spark, from its inception at UC Berkeley to modern optimizations in Spark 3.x.

**Papers covered:**
1. Spark: Cluster Computing with Working Sets (2010)
2. Resilient Distributed Datasets (RDD) (2012)
3. Spark SQL: Relational Data Processing in Spark (2015)
4. Structured Streaming (2018)
5. Photon: A Fast Query Engine for Lakehouse Systems (2022)

---

## 📄 **1. Spark: Cluster Computing with Working Sets (2010)**

**Authors:** Matei Zaharia, Mosharaf Chowdhury, Michael J. Franklin, Scott Shenker, Ion Stoica  
**Institution:** UC Berkeley  
**Conference:** HotCloud 2010

### **Problem Statement**

MapReduce is inefficient for:
1. **Iterative algorithms** (machine learning, graph processing)
2. **Interactive data mining** (ad-hoc queries)

**Why?** MapReduce writes intermediate results to HDFS after every stage.

**Example: Iterative K-Means Clustering**

```
MapReduce:
Iteration 1: Read data from HDFS → Compute → Write to HDFS
Iteration 2: Read data from HDFS → Compute → Write to HDFS  (redundant I/O!)
...
Iteration 100: Read data from HDFS → Compute → Write to HDFS
```

**Cost:** 100x disk I/O operations for data that doesn't change!

---

### **Spark's Solution: In-Memory Caching**

```python
# Spark
data = sc.textFile("hdfs://...")
data.cache()  # Keep in RAM across iterations!

for i in range(100):
    model = train(data)  # Reads from RAM, not disk!
```

**Performance gain:** 10-100x faster than Hadoop MapReduce for iterative workloads.

---

### **Key Innovations**

**1. Resilient Distributed Datasets (RDDs)**
- Immutable distributed collections
- Fault tolerance through lineage (no replication needed!)
- Lazy evaluation

**2. Two types of operations:**
- **Transformations:** `map`, `filter`, `groupBy` (lazy, build DAG)
- **Actions:** `count`, `collect`, `save` (trigger execution)

**3. Fault tolerance without replication:**

```python
# MapReduce: Replicate intermediate data (expensive!)
intermediate_data.replicate(3)

# Spark: Store lineage (cheap!)
rdd = sc.textFile("data")
  .map(lambda x: x.split())
  .filter(lambda x: len(x) > 5)

# If partition lost, recompute using lineage!
```

---

### **Benchmark Results (from paper)**

**Logistic Regression (Iterative ML):**
- Hadoop: 127 seconds
- Spark: 6 seconds
- **Speedup: 21x**

**K-Means Clustering:**
- Hadoop: 76 seconds
- Spark: 9 seconds
- **Speedup: 8.4x**

---

### **Architecture Diagram (from paper)**

```
Driver Program (Master)
  ├── DAG Scheduler (builds execution graph)
  ├── Task Scheduler (assigns tasks to workers)
  └── Block Manager (tracks cached RDDs)

Worker Nodes (Executors)
  ├── Task Threads (run user code)
  └── Block Manager (stores RDD partitions in RAM/disk)
```

---

## 📄 **2. Resilient Distributed Datasets: A Fault-Tolerant Abstraction for In-Memory Cluster Computing (2012)**

**Authors:** Matei Zaharia, Mosharaf Chowdhury, Tathagata Das, Ankur Dave, Justin Ma, Murphy McCauley, Michael J. Franklin, Scott Shenker, Ion Stoica  
**Institution:** UC Berkeley  
**Conference:** NSDI 2012

### **RDD Definition**

An RDD is:
- **Immutable:** Once created, can't be changed (functional programming)
- **Partitioned:** Split across cluster nodes
- **Fault-tolerant:** Lost partitions recomputed using lineage

---

### **RDD Interface (5 core operations)**

```python
# 1. Partitions: List of partition objects
rdd.partitions()  # [Partition 0, Partition 1, ...]

# 2. Dependencies: Parent RDDs
rdd.dependencies()  # [ShuffleDependency, NarrowDependency]

# 3. Compute: Function to compute partition
rdd.compute(partition)  # User-defined logic

# 4. Partitioner: How data is partitioned (optional)
rdd.partitioner()  # HashPartitioner, RangePartitioner

# 5. Preferred locations: Where to compute partition (data locality)
rdd.preferredLocations(partition)  # ["node1", "node2"]
```

---

### **Dependency Types**

**1. Narrow Dependency:** Each parent partition used by at most one child partition

```python
# Example: map, filter
rdd1 = sc.parallelize([1, 2, 3, 4])
rdd2 = rdd1.map(lambda x: x * 2)

# Partition 0 of rdd1 → Partition 0 of rdd2
# Partition 1 of rdd1 → Partition 1 of rdd2
# No shuffle needed! ✅
```

**2. Wide Dependency:** Each parent partition may be used by multiple child partitions

```python
# Example: groupByKey, join
rdd1 = sc.parallelize([("a", 1), ("b", 2), ("a", 3)])
rdd2 = rdd1.groupByKey()

# All partitions of rdd1 may contribute to any partition of rdd2
# Shuffle needed! ❌ (expensive)
```

---

### **Lineage-Based Fault Recovery**

**Example lineage graph:**

```python
# Your code
lines = sc.textFile("log.txt")  # RDD 1
errors = lines.filter(lambda x: "ERROR" in x)  # RDD 2
errors.cache()  # Mark for caching
errors.count()  # Action

# Lineage:
# lines (HDFS) → errors (filter) → count (action)

# If partition 3 of "errors" is lost:
# 1. Check lineage: errors = lines.filter(...)
# 2. Recompute: Read partition 3 of lines, apply filter
# 3. No need to recompute entire dataset!
```

---

### **Memory Management**

**LRU eviction policy:** If RAM full, evict least recently used partitions.

```python
# Persistence levels (from paper)
MEMORY_ONLY:      Store in RAM, recompute if evicted
MEMORY_ONLY_SER:  Store serialized (save RAM, slower access)
MEMORY_AND_DISK:  Spill to disk if RAM full
DISK_ONLY:        Always store on disk
```

---

### **Benchmarks (from paper)**

**PageRank (100 iterations):**
- Hadoop: 171 seconds
- Spark (no caching): 72 seconds
- Spark (with caching): **23 seconds**
- **Speedup: 7.4x**

**Fault recovery overhead:**
- Lost 1 partition: Recompute only that partition (< 1 second)
- vs MapReduce: Must re-run entire job (10+ seconds)

---

## 📄 **3. Spark SQL: Relational Data Processing in Spark (2015)**

**Authors:** Michael Armbrust, Reynold S. Xin, Cheng Lian, Yin Huai, Davies Liu, Joseph K. Bradley, Xiangrui Meng, Tomer Kaftan, Michael J. Franklin, Ali Ghodsi, Matei Zaharia  
**Institution:** Databricks & UC Berkeley  
**Conference:** SIGMOD 2015

### **Problem with RDDs**

**RDDs are too low-level:**

```python
# RDD code (verbose, no optimization)
data = sc.textFile("users.csv")
users = data.map(lambda line: line.split(",")) \
    .filter(lambda fields: int(fields[2]) > 18) \
    .map(lambda fields: (fields[0], fields[1]))

# Spark doesn't know:
# - Schema (what are fields 0, 1, 2?)
# - Intent (filter before map would be more efficient)
```

**Spark SQL solution: DataFrames**

```python
# DataFrame code (declarative, optimized!)
df = spark.read.csv("users.csv", header=True, inferSchema=True)
result = df.filter(col("age") > 18).select("name", "email")

# Spark knows:
# - Schema (age is int, name is string)
# - Can push filter before projection (optimizer!)
```

---

### **Catalyst Optimizer**

**Four-phase optimization:**

```
SQL Query / DataFrame API
    ↓
1. Analysis
   - Resolve column names
   - Type checking
    ↓
2. Logical Optimization
   - Predicate pushdown: filter → join becomes join(filter)
   - Constant folding: 1+1 → 2
   - Projection pruning: SELECT only needed columns
    ↓
3. Physical Planning
   - Generate multiple physical plans
   - Cost-based optimization (use statistics)
   - Choose join algorithm (broadcast, shuffle hash, sort merge)
    ↓
4. Code Generation
   - WholeStageCodegen: Fuse operators
   - Generate optimized Java bytecode
    ↓
Executable Code
```

---

### **Example Optimization (from paper)**

**Query:**
```sql
SELECT name, salary
FROM employees
WHERE age > 30 AND department = 'Engineering'
```

**Unoptimized plan:**
```
Project (name, salary)
  └── Filter (age > 30 AND department = 'Engineering')
       └── Scan (employees)
```

**Catalyst optimized plan:**
```
Project (name, salary)  ← Only read these 2 columns
  └── Filter (department = 'Engineering')  ← Most selective filter first
       └── Filter (age > 30)
            └── Scan (employees)  ← Predicate pushdown to storage
```

**Optimizations applied:**
1. **Predicate pushdown:** Filters pushed to scan (Parquet skips row groups)
2. **Column pruning:** Only read `name`, `salary`, `age`, `department` (not all 50 columns)
3. **Filter ordering:** Most selective filter first (`department` likely filters more than `age`)

---

### **Code Generation Example (from paper)**

**Without codegen:**
```java
// Interpreted (slow)
for (row in data) {
    if (row.get("age") > 30) {  // Virtual function call
        if (row.get("department").equals("Engineering")) {  // Another call
            emit(row.get("name"), row.get("salary"));  // Two more calls
        }
    }
}
```

**With WholeStageCodegen:**
```java
// Generated (fast)
class GeneratedIterator extends Iterator {
    public boolean hasNext() { return input.hasNext(); }
    
    public InternalRow next() {
        InternalRow row = input.next();
        int age = row.getInt(2);  // Direct access, no boxing!
        UTF8String dept = row.getUTF8String(3);
        
        if (age > 30 && dept.equals("Engineering")) {
            // Inline all operations, no function calls!
            return InternalRow.apply(row.getUTF8String(0), row.getInt(5));
        }
        return null;
    }
}
```

**Performance gain:** 2-5x faster!

---

### **Benchmarks (from paper)**

**TPC-DS Benchmark (100 GB):**
- Hive: 6,372 seconds
- Spark SQL: **1,788 seconds**
- **Speedup: 3.6x**

**With Parquet format:**
- Spark SQL: **212 seconds**
- **Speedup: 30x over Hive!**

---

## 📄 **4. Structured Streaming: A Declarative API for Real-Time Applications in Apache Spark (2018)**

**Authors:** Michael Armbrust, Tathagata Das, Liwen Sun, Burak Yavuz, Shixiong Zhu, Mukul Murthy, Joseph Torres, Herman van Hovell, Adrian Ionescu, Alicja Łuszczak, Michał Świtakowski, Michał Szafrański, Xiao Li, Takuya Ueshin, Mostafa Mokhtar, Peter Boncz, Ali Ghodsi, Sameer Paranjpye, Pieter Senster, Reynold Xin, Matei Zaharia  
**Institution:** Databricks & UC Berkeley  
**Conference:** SIGMOD 2018

### **Problem with Traditional Streaming**

**Micro-batch systems (Spark Streaming 1.0):**
- Treats stream as sequence of small batches
- High latency (seconds)
- Complex API for windowing/state

**Low-latency systems (Storm, Flink):**
- Record-at-a-time processing
- Hard to reason about consistency
- Different APIs for batch and streaming

---

### **Structured Streaming Solution**

**Key idea:** Treat stream as unbounded table!

```python
# Stream looks like continuously growing table
# t=0:  [{"user": "Alice", "clicks": 1}]
# t=1:  [{"user": "Alice", "clicks": 1}, {"user": "Bob", "clicks": 2}]
# t=2:  [{"user": "Alice", "clicks": 1}, {"user": "Bob", "clicks": 2}, {"user": "Alice", "clicks": 3}]

# Query is just like batch SQL!
df = spark.readStream.format("kafka")...
result = df.groupBy("user").count()
```

---

### **Execution Model**

```
Stream (unbounded table)
    ↓
Incremental Query Execution
    ↓
Result (another unbounded table)
    ↓
Output Modes:
  - Append:   Only new rows
  - Update:   Changed rows
  - Complete: Entire result
```

---

### **Watermarking (Handling Late Data)**

**Problem:** Events arrive out of order.

```python
# Events arrive:
# t=10:00 → event with timestamp 10:00
# t=10:05 → event with timestamp 10:02 (late by 3 minutes!)

# Without watermark: Must keep all state forever! (memory leak)

# With watermark: Drop events late by > 10 minutes
df = df.withWatermark("timestamp", "10 minutes")
```

**How watermark works:**

```
Watermark = max_event_time - delay_threshold

Example:
  max_event_time = 10:15
  threshold = 10 minutes
  watermark = 10:05
  
  → Events with timestamp < 10:05 are dropped
```

---

### **Example: Real-Time Dashboard (from paper)**

```python
# Stream of ad clicks
clicks = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "host:port") \
    .load()

# Parse JSON
from pyspark.sql.functions import from_json, window
schema = StructType([
    StructField("user_id", StringType()),
    StructField("ad_id", StringType()),
    StructField("timestamp", TimestampType())
])

parsed = clicks.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

# Windowed aggregation (5-minute windows)
windowed_counts = parsed \
    .withWatermark("timestamp", "10 minutes") \
    .groupBy(
        window("timestamp", "5 minutes"),
        "ad_id"
    ).count()

# Write to dashboard
query = windowed_counts.writeStream \
    .format("memory") \
    .queryName("dashboard") \
    .outputMode("update") \
    .start()
```

---

### **Fault Tolerance**

**Checkpointing:** Periodically save state to durable storage.

```python
query = df.writeStream \
    .option("checkpointLocation", "s3://bucket/checkpoint") \
    .start()

# On failure:
# 1. Read last checkpoint
# 2. Replay data from Kafka offset
# 3. Restore state
```

**Exactly-once semantics:** Achieved through idempotent writes + checkpointing.

---

### **Benchmarks (from paper)**

**End-to-end latency:**
- Spark Streaming 1.0: 500-1000 ms
- Structured Streaming: **100 ms**
- **5-10x improvement!**

**Throughput:**
- Processes **1 billion events/hour** per node

---

## 📄 **5. Photon: A Fast Query Engine for Lakehouse Systems (2022)**

**Authors:** Databricks Team  
**Institution:** Databricks  
**Conference:** SIGMOD 2022

### **Problem**

Spark is fast, but still bottlenecked by:
1. **JVM overhead** (garbage collection, boxing/unboxing)
2. **Inefficient vectorized processing** (row-at-a-time in Tungsten)
3. **Parquet decoding overhead**

---

### **Photon Solution: Native Vectorized Engine**

**Key innovations:**

**1. C++ implementation** (no JVM overhead)
**2. Vectorized execution** (process 1000s of rows at once)
**3. SIMD instructions** (Single Instruction Multiple Data)

```cpp
// Scalar (slow)
for (int i = 0; i < n; i++) {
    result[i] = a[i] + b[i];  // One addition per iteration
}

// SIMD (fast)
for (int i = 0; i < n; i += 8) {
    __m256i va = _mm256_load_si256(&a[i]);  // Load 8 integers
    __m256i vb = _mm256_load_si256(&b[i]);
    __m256i vresult = _mm256_add_epi32(va, vb);  // Add 8 pairs in parallel!
    _mm256_store_si256(&result[i], vresult);
}
```

---

### **Architecture**

```
Spark SQL (query planning)
    ↓
Photon-compatible operations?
  YES → Photon Engine (C++, vectorized)
  NO  → Spark Engine (JVM, codegen)
```

**Photon handles:**
- Scans (Parquet, Delta)
- Filters, projections
- Joins, aggregations

**Spark handles:**
- UDFs (user-defined functions)
- Complex data types (not yet in Photon)

---

### **Benchmarks (from paper)**

**TPC-DS 1 TB:**
- Spark: 100 queries in 600 seconds
- Photon: **100 queries in 180 seconds**
- **Speedup: 3.3x**

**Delta Lake queries:**
- Spark: 45 seconds
- Photon: **12 seconds**
- **Speedup: 3.75x**

---

## 🔄 **Evolution Timeline**

```
2010: Spark paper (HotCloud)
  ↓ Core idea: In-memory caching
  
2012: RDD paper (NSDI)
  ↓ Fault tolerance via lineage
  
2014: Spark 1.0 released
  ↓ Production-ready
  
2015: Spark SQL paper (SIGMOD)
  ↓ DataFrame API + Catalyst optimizer
  
2016: Structured Streaming
  ↓ Unified batch/stream API
  
2018: Structured Streaming paper (SIGMOD)
  ↓ Exactly-once, watermarks
  
2020: Spark 3.0
  ↓ Adaptive Query Execution (AQE)
  
2022: Photon paper (SIGMOD)
  ↓ Vectorized C++ engine (3x faster!)
  
2024: Spark 3.5
  ↓ GPU support, improved AQE
```

---

## 📊 **Key Takeaways**

**RDD (2012):**
- Fault tolerance WITHOUT replication (lineage graph)
- Immutability enables lazy evaluation
- 10-100x faster than MapReduce for iterative workloads

**Spark SQL (2015):**
- Catalyst optimizer (4 phases: analysis → logical → physical → codegen)
- WholeStageCodegen (fuse operators, eliminate virtual calls)
- Cost-based optimization (use statistics to choose plans)

**Structured Streaming (2018):**
- Unbounded table abstraction (batch = streaming)
- Watermarks for late data handling
- Exactly-once semantics (checkpointing + idempotent sinks)

**Photon (2022):**
- Vectorized execution (process 1000s of rows at once)
- SIMD instructions (8-16 operations in parallel)
- 3-4x faster than Spark for analytics queries

---

## 📖 **Further Reading**

**Original Papers:**
1. [Spark: Cluster Computing with Working Sets (HotCloud 2010)](https://www.usenix.org/legacy/event/hotcloud10/tech/full_papers/Zaharia.pdf)
2. [Resilient Distributed Datasets (NSDI 2012)](https://www.usenix.org/system/files/conference/nsdi12/nsdi12-final138.pdf)
3. [Spark SQL (SIGMOD 2015)](https://people.csail.mit.edu/matei/papers/2015/sigmod_spark_sql.pdf)
4. [Structured Streaming (SIGMOD 2018)](https://people.csail.mit.edu/matei/papers/2018/sigmod_structured_streaming.pdf)
5. [Photon (SIGMOD 2022)](https://www.vldb.org/pvldb/vol15/p3054-behm.pdf)

**Books:**
- "Learning Spark" (2nd Edition, 2020) - Databricks team
- "Spark: The Definitive Guide" (2018) - Bill Chambers, Matei Zaharia

---

**Next:** [README](./README.md) - Module overview and setup

**Previous:** [EXPERT](./EXPERT.md)

**Master Roadmap:** [00-MASTER-ROADMAP.md](../../00-MASTER-ROADMAP.md)
