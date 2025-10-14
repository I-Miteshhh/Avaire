# Week 12-13: Lakehouse Architecture — BEGINNER Track

*"The lakehouse unifies data lakes and warehouses—bringing ACID transactions, schema enforcement, and time travel to S3/ADLS. Delta Lake, Iceberg, and Hudi are revolutionizing data platforms."* — Principal Engineer, Databricks

---

## 🎯 Learning Outcomes

By the end of this track, you will:
- Understand the lakehouse architecture paradigm
- Implement ACID transactions on cloud object storage (S3, ADLS, GCS)
- Use Delta Lake for batch and streaming workloads
- Master schema evolution and enforcement
- Implement time travel and data versioning
- Understand partition management and optimization
- Deploy Delta Lake on Spark and query with multiple engines

---

## 📚 Prerequisites

- ✅ SQL fundamentals
- ✅ Apache Spark basics
- ✅ Object storage concepts (S3, ADLS)
- ✅ Parquet file format understanding

---

## 🏛️ 1. Data Lake vs Data Warehouse vs Lakehouse

### The Evolution

```
┌────────────────────────────────────────────────────────────────┐
│ Data Warehouse (1990s-2010s)                                   │
│ ┌────────────────────────────────────────────────────────┐    │
│ │ Examples: Oracle, Teradata, SQL Server, Snowflake      │    │
│ │                                                         │    │
│ │ Pros:                                  Cons:            │    │
│ │ ├─ ACID transactions                  ├─ Expensive      │    │
│ │ ├─ SQL support                        ├─ Vendor lock-in │    │
│ │ ├─ Performance (indexes, stats)       ├─ Structured only│    │
│ │ └─ Data quality guarantees            └─ Limited scale  │    │
│ └────────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ Data Lake (2010s)                                              │
│ ┌────────────────────────────────────────────────────────┐    │
│ │ Examples: S3, ADLS, GCS with Parquet/ORC/Avro         │    │
│ │                                                         │    │
│ │ Pros:                                  Cons:            │    │
│ │ ├─ Cheap storage ($0.023/GB/month)    ├─ No ACID       │    │
│ │ ├─ Scales to petabytes                ├─ No schema     │    │
│ │ ├─ Supports all data types            ├─ Data swamp    │    │
│ │ └─ Open formats (Parquet)             └─ Complex ETL   │    │
│ └────────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ Lakehouse (2020s+)                                             │
│ ┌────────────────────────────────────────────────────────┐    │
│ │ Examples: Delta Lake, Apache Iceberg, Apache Hudi      │    │
│ │                                                         │    │
│ │ Best of Both Worlds:                                   │    │
│ │ ├─ ACID transactions (from warehouse)                  │    │
│ │ ├─ Schema enforcement & evolution                      │    │
│ │ ├─ Time travel & versioning                            │    │
│ │ ├─ Cheap storage (from lake: $0.023/GB)               │    │
│ │ ├─ Scales to petabytes                                 │    │
│ │ ├─ Open formats (Parquet + metadata layer)            │    │
│ │ └─ Multi-engine support (Spark, Presto, Flink)        │    │
│ └────────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────┘
```

---

### The Lakehouse Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Storage Layer (S3/ADLS)                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Data Files (Parquet/ORC):                            │   │
│  │ ├─ part-00000.parquet (1 GB)                         │   │
│  │ ├─ part-00001.parquet (1 GB)                         │   │
│  │ └─ part-00002.parquet (1 GB)                         │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                            ▲
                            │ (managed by)
                            │
┌──────────────────────────────────────────────────────────────┐
│              Metadata Layer (Delta/Iceberg/Hudi)              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Transaction Log:                                     │   │
│  │ ├─ 00000.json (add part-00000.parquet)              │   │
│  │ ├─ 00001.json (add part-00001.parquet)              │   │
│  │ ├─ 00002.json (remove part-00000.parquet)           │   │
│  │ └─ 00003.json (add part-00003.parquet)              │   │
│  │                                                       │   │
│  │ Features Enabled:                                    │   │
│  │ ├─ ACID transactions (optimistic concurrency)       │   │
│  │ ├─ Schema enforcement & evolution                   │   │
│  │ ├─ Time travel (query version 00001)                │   │
│  │ ├─ Data versioning (audit trail)                    │   │
│  │ └─ VACUUM (delete old files)                        │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                            ▲
                            │ (queried by)
                            │
┌──────────────────────────────────────────────────────────────┐
│                    Query Engines                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │ Spark      │  │ Presto     │  │ Flink      │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔷 2. Delta Lake Fundamentals

### What is Delta Lake?

```
Delta Lake = Parquet files + Transaction log (JSON files)

Location: s3://my-bucket/delta-table/

Files:
├─ _delta_log/
│  ├─ 00000.json  ← Transaction log (metadata)
│  ├─ 00001.json
│  ├─ 00002.json
│  └─ 00000.checkpoint.parquet  ← Checkpoints (every 10 commits)
│
├─ part-00000-*.parquet  ← Data files
├─ part-00001-*.parquet
└─ part-00002-*.parquet

Transaction Log Entry (00000.json):
{
  "add": {
    "path": "part-00000-abc123.parquet",
    "size": 1073741824,
    "partitionValues": {"date": "2023-10-15"},
    "modificationTime": 1697385600000,
    "dataChange": true,
    "stats": "{\"numRecords\": 1000000, \"minValues\": {...}, \"maxValues\": {...}}"
  }
}
```

---

### Creating a Delta Table (PySpark)

```python
from pyspark.sql import SparkSession
from delta import *

# Initialize Spark with Delta
builder = SparkSession.builder \
    .appName("DeltaLakeDemo") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

spark = configure_spark_with_delta_pip(builder).getOrCreate()

# Create sample data
data = [
    (1, "Alice", 25, "2023-10-15"),
    (2, "Bob", 30, "2023-10-15"),
    (3, "Charlie", 35, "2023-10-15")
]

df = spark.createDataFrame(data, ["id", "name", "age", "date"])

# Write as Delta table
df.write.format("delta") \
    .mode("overwrite") \
    .partitionBy("date") \
    .save("s3://my-bucket/users")

print("✅ Delta table created!")
```

**What Happened:**

```
1. Spark writes Parquet files:
   s3://my-bucket/users/date=2023-10-15/part-00000.parquet

2. Delta creates transaction log:
   s3://my-bucket/users/_delta_log/00000.json
   {
     "add": {
       "path": "date=2023-10-15/part-00000.parquet",
       "size": 1234,
       "partitionValues": {"date": "2023-10-15"},
       "stats": "{\"numRecords\": 3}"
     }
   }

3. Schema stored in log:
   {
     "metaData": {
       "schemaString": "{\"type\":\"struct\",\"fields\":[{\"name\":\"id\",\"type\":\"long\"}, ...]}"
     }
   }
```

---

### Reading Delta Tables

```python
# Read latest version
df = spark.read.format("delta").load("s3://my-bucket/users")
df.show()

# Output:
# +---+-------+---+----------+
# | id|   name|age|      date|
# +---+-------+---+----------+
# |  1|  Alice| 25|2023-10-15|
# |  2|    Bob| 30|2023-10-15|
# |  3|Charlie| 35|2023-10-15|
# +---+-------+---+----------+

# SQL interface
spark.sql("CREATE TABLE users USING DELTA LOCATION 's3://my-bucket/users'")
spark.sql("SELECT * FROM users WHERE age > 28").show()
```

---

## 💾 3. ACID Transactions on S3

### The Challenge: S3 is NOT ACID

```
S3 Properties:
├─ Eventually consistent (before 2020)
├─ No atomic directory operations
├─ No locking mechanism
└─ List operations are slow

Problems for Data Warehouses:
1. Write Conflict:
   User A writes file1.parquet
   User B writes file2.parquet (same partition)
   → Both succeed, but metadata inconsistent!

2. Read During Write:
   Writer adds 10 files
   Reader lists directory mid-write
   → Sees partial data (5 files) ❌

3. Failed Writes:
   Write fails after 5 of 10 files written
   → Orphaned files, inconsistent state ❌
```

---

### Delta Lake's Solution: Optimistic Concurrency Control

```
Transaction Protocol:

1. Read Phase:
   ├─ Read latest transaction log version (e.g., 00005.json)
   ├─ Determine files to read
   └─ Load data from Parquet files

2. Write Phase:
   ├─ Write new Parquet files to S3 (no conflicts yet)
   ├─ Prepare transaction log entry (00006.json)
   └─ Attempt atomic commit

3. Commit Phase (Atomic):
   ├─ PUT 00006.json to S3 (conditional write)
   ├─ If file already exists → Conflict! Retry
   └─ If PUT succeeds → Commit successful ✅

Example:
Writer A:
T1: Read log (version 5)
T2: Write part-00003.parquet
T3: Attempt PUT _delta_log/00006.json → Success!

Writer B (concurrent):
T1: Read log (version 5)
T2: Write part-00004.parquet
T3: Attempt PUT _delta_log/00006.json → FAIL (already exists)
T4: Retry: Read log (version 6), resolve conflict, PUT 00007.json → Success!
```

**Code Example:**

```python
# Concurrent writes handled automatically

# Writer 1
df1.write.format("delta").mode("append").save("s3://my-bucket/users")

# Writer 2 (concurrent)
df2.write.format("delta").mode("append").save("s3://my-bucket/users")

# Delta Lake ensures:
# ✅ Both writes succeed (serially)
# ✅ No data loss
# ✅ Readers see consistent state
```

---

## 🕰️ 4. Time Travel and Versioning

### Query Historical Versions

```python
# Current version
df = spark.read.format("delta").load("s3://my-bucket/users")
print(f"Current count: {df.count()}")  # 1000 rows

# Time travel: Query version 5
df_v5 = spark.read.format("delta") \
    .option("versionAsOf", 5) \
    .load("s3://my-bucket/users")
print(f"Version 5 count: {df_v5.count()}")  # 800 rows

# Time travel: Query as of timestamp
df_yesterday = spark.read.format("delta") \
    .option("timestampAsOf", "2023-10-14") \
    .load("s3://my-bucket/users")
print(f"Yesterday count: {df_yesterday.count()}")  # 750 rows
```

**SQL Syntax:**

```sql
-- Query version 3
SELECT * FROM users VERSION AS OF 3;

-- Query as of timestamp
SELECT * FROM users TIMESTAMP AS OF '2023-10-14T10:00:00Z';
```

---

### Version History

```python
from delta.tables import DeltaTable

deltaTable = DeltaTable.forPath(spark, "s3://my-bucket/users")

# Show version history
deltaTable.history().show()

# Output:
# +-------+-------------------+---------+----------+
# |version|          timestamp|operation|      info|
# +-------+-------------------+---------+----------+
# |      5|2023-10-15 14:00:00|   DELETE|{"num...|
# |      4|2023-10-15 12:00:00|    MERGE|{"num...|
# |      3|2023-10-15 10:00:00|   UPDATE|{"num...|
# |      2|2023-10-15 08:00:00|   INSERT|{"num...|
# |      1|2023-10-15 06:00:00|   INSERT|{"num...|
# |      0|2023-10-15 00:00:00|    WRITE|{"num...|
# +-------+-------------------+---------+----------+

# Detailed version info
deltaTable.history(5).select("version", "operation", "operationMetrics").show(truncate=False)
```

---

## 🔄 5. Schema Evolution and Enforcement

### Schema Enforcement (Default)

```python
# Initial schema
df1 = spark.createDataFrame([(1, "Alice", 25)], ["id", "name", "age"])
df1.write.format("delta").mode("overwrite").save("s3://my-bucket/users")

# Try to append with different schema
df2 = spark.createDataFrame([(2, "Bob")], ["id", "name"])  # Missing 'age'
df2.write.format("delta").mode("append").save("s3://my-bucket/users")

# ❌ ERROR:
# AnalysisException: A schema mismatch detected when writing to the Delta table.
# To enable schema migration, please set:
# '.option("mergeSchema", "true")'
```

---

### Schema Evolution (Opt-In)

```python
# Enable schema evolution
df2.write.format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .save("s3://my-bucket/users")

# ✅ Success! New schema:
# id: long
# name: string
# age: long (nullable)

# Read merged data
df = spark.read.format("delta").load("s3://my-bucket/users")
df.show()

# Output:
# +---+-----+----+
# | id| name| age|
# +---+-----+----+
# |  1|Alice|  25|
# |  2|  Bob|null|  ← Missing column filled with null
# +---+-----+----+
```

---

### Schema Evolution Rules

```
Allowed:
├─ Add new columns (nullable)
├─ Widen column types (int → long, float → double)
└─ Change column nullability (non-null → nullable)

NOT Allowed:
├─ Drop columns
├─ Rename columns
├─ Change column types (string → int)
└─ Change nullability (nullable → non-null)

Workaround for complex changes:
1. Read old table
2. Transform data (rename, drop columns)
3. Write to new table
4. Swap table locations
```

---

## 🧹 6. Data Management Operations

### UPDATE

```python
from delta.tables import DeltaTable

deltaTable = DeltaTable.forPath(spark, "s3://my-bucket/users")

# Update records
deltaTable.update(
    condition="age < 30",
    set={"age": "age + 1"}
)

# SQL equivalent
spark.sql("""
    UPDATE users
    SET age = age + 1
    WHERE age < 30
""")
```

---

### DELETE

```python
# Delete records
deltaTable.delete(condition="age > 60")

# SQL equivalent
spark.sql("DELETE FROM users WHERE age > 60")
```

---

### MERGE (Upsert)

```python
# Source data (updates + inserts)
updates = spark.createDataFrame([
    (1, "Alice Updated", 26),  # Update
    (4, "David", 40)            # Insert
], ["id", "name", "age"])

# Merge into Delta table
deltaTable.alias("target").merge(
    updates.alias("source"),
    "target.id = source.id"
).whenMatchedUpdate(
    set={"name": "source.name", "age": "source.age"}
).whenNotMatchedInsert(
    values={"id": "source.id", "name": "source.name", "age": "source.age"}
).execute()

# SQL equivalent
spark.sql("""
    MERGE INTO users AS target
    USING updates AS source
    ON target.id = source.id
    WHEN MATCHED THEN
        UPDATE SET name = source.name, age = source.age
    WHEN NOT MATCHED THEN
        INSERT (id, name, age) VALUES (source.id, source.name, source.age)
""")
```

---

### VACUUM (Clean Old Files)

```python
# Remove files older than 7 days (default retention)
deltaTable.vacuum()

# Custom retention (3 days)
deltaTable.vacuum(72)  # hours

# WARNING: Disables time travel beyond retention period!
```

**What VACUUM Does:**

```
Before VACUUM:
_delta_log/
├─ 00000.json → part-00000.parquet (deleted in v3)
├─ 00001.json → part-00001.parquet
├─ 00002.json → part-00002.parquet
├─ 00003.json → remove part-00000.parquet

Data files:
├─ part-00000.parquet  ← Orphaned (removed from log)
├─ part-00001.parquet
└─ part-00002.parquet

After VACUUM (retention expired):
Data files:
├─ part-00001.parquet  ← Only current files remain
└─ part-00002.parquet

Time travel to version 0 → FAIL (file missing)
```

---

## 🏆 Interview Questions (Beginner Level)

1. **What is the lakehouse architecture? How does it differ from data lakes and warehouses?**
2. **How does Delta Lake achieve ACID transactions on S3?**
3. **What is time travel? How would you query a table as of yesterday?**
4. **Explain schema enforcement vs schema evolution.**
5. **What does VACUUM do? When should you run it?**

---

## 🎓 Summary Checklist

- [ ] Understand lakehouse architecture benefits
- [ ] Create Delta tables with partitioning
- [ ] Implement ACID transactions on S3/ADLS
- [ ] Use time travel for historical queries
- [ ] Configure schema evolution
- [ ] Perform UPDATE, DELETE, MERGE operations
- [ ] Run VACUUM for data retention
- [ ] Answer beginner interview questions

**Next:** [INTERMEDIATE.md →](INTERMEDIATE.md)
