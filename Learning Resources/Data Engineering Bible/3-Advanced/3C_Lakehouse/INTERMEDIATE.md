# Week 12-13: Lakehouse Architecture — INTERMEDIATE Track

*"Iceberg's hidden partitioning and time travel implementation is brilliant—partition pruning without exposing partition columns to users. This is the evolution beyond Hive."* — Staff Engineer, Netflix

---

## 🎯 Learning Outcomes

By the end of this track, you will:
- Master Apache Iceberg table format and metadata architecture
- Implement hidden partitioning for automatic partition pruning
- Use Iceberg's snapshot isolation for time travel
- Compare Delta Lake, Iceberg, and Hudi architectures
- Optimize partition layouts for query performance
- Handle schema evolution with column mapping
- Implement partition evolution (change partitioning without rewriting data)
- Configure catalog integrations (Hive, Glue, Nessie)

---

## 🧊 1. Apache Iceberg Deep Dive

### Iceberg Metadata Architecture

```
Iceberg Table Structure:

s3://my-bucket/iceberg-table/
├─ metadata/
│  ├─ v1.metadata.json  ← Version 1 metadata
│  ├─ v2.metadata.json  ← Version 2 metadata (current)
│  ├─ snap-123.avro     ← Snapshot 123 manifest list
│  ├─ snap-124.avro     ← Snapshot 124 manifest list
│  └─ manifest-*.avro   ← Manifest files (list of data files)
│
└─ data/
   ├─ date=2023-10-15/
   │  ├─ part-00000.parquet
   │  └─ part-00001.parquet
   └─ date=2023-10-16/
      └─ part-00000.parquet

Three-Level Metadata Hierarchy:
┌─────────────────────────────────────────────────────────┐
│ 1. Metadata File (v2.metadata.json)                     │
│    ├─ Current snapshot ID: 124                          │
│    ├─ Schema (columns, types)                           │
│    ├─ Partition spec                                    │
│    └─ Snapshot list: [123, 124]                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Manifest List (snap-124.avro)                        │
│    ├─ manifest-abc123.avro (partition: date=2023-10-15) │
│    ├─ manifest-def456.avro (partition: date=2023-10-16) │
│    └─ Added files: 2, Deleted files: 0                  │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Manifest File (manifest-abc123.avro)                 │
│    ├─ part-00000.parquet (status: ADDED)                │
│    │  ├─ size: 1 GB                                     │
│    │  ├─ record_count: 1,000,000                        │
│    │  ├─ partition: {date: 2023-10-15}                  │
│    │  └─ lower_bounds/upper_bounds (min/max values)     │
│    └─ part-00001.parquet (status: ADDED)                │
└─────────────────────────────────────────────────────────┘
```

**Why Three Levels?**

```
Benefits:
1. Fast snapshot listing (metadata file only)
2. Partition pruning (manifest list level)
3. File-level stats (manifest file level)
4. Efficient time travel (swap metadata pointer)

Example Query:
SELECT * FROM events WHERE date = '2023-10-15' AND user_id = 123

Step 1: Read metadata file (v2.metadata.json)
├─ Current snapshot: 124
└─ Read manifest list: snap-124.avro

Step 2: Partition pruning (manifest list)
├─ Filter manifests by partition: date=2023-10-15
└─ Read only manifest-abc123.avro (skip manifest-def456.avro)

Step 3: File pruning (manifest file)
├─ Check lower_bounds/upper_bounds for user_id
├─ part-00000.parquet: user_id in [1, 500] → Read
└─ part-00001.parquet: user_id in [501, 1000] → Skip

Result: Read 1 of 3 data files (66% reduction)
```

---

### Hidden Partitioning

```
Problem with Hive-style partitioning:

-- User must know partition column
SELECT * FROM events
WHERE year = 2023 AND month = 10 AND day = 15;  ❌ Tedious!

-- Without partition columns → Full scan
SELECT * FROM events
WHERE event_date = '2023-10-15';  ❌ Slow!

Iceberg Solution: Hidden Partitioning

CREATE TABLE events (
  event_id BIGINT,
  event_date DATE,
  user_id BIGINT,
  data STRING
)
USING iceberg
PARTITIONED BY (days(event_date));  ← Partition function!

-- Query with natural column (no partition exposure)
SELECT * FROM events
WHERE event_date = '2023-10-15';  ✅ Automatic partition pruning!

-- Iceberg translates:
-- event_date = '2023-10-15' → days(event_date) = 19650
-- → Read only partition 19650
```

**Partition Transform Functions:**

```sql
-- Temporal transforms
PARTITIONED BY (years(timestamp_col))   -- Year partition
PARTITIONED BY (months(timestamp_col))  -- Month partition
PARTITIONED BY (days(date_col))         -- Day partition
PARTITIONED BY (hours(timestamp_col))   -- Hour partition

-- Identity transform
PARTITIONED BY (identity(region))       -- Exact value

-- Hash transform (for uniform distribution)
PARTITIONED BY (bucket(10, user_id))    -- 10 buckets by user_id

-- Truncate transform
PARTITIONED BY (truncate(5, price))     -- Truncate to nearest 5
```

**Example:**

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.spark_catalog.type", "hadoop") \
    .config("spark.sql.catalog.spark_catalog.warehouse", "s3://my-bucket/warehouse") \
    .getOrCreate()

# Create table with hidden partitioning
spark.sql("""
    CREATE TABLE events (
        event_id BIGINT,
        event_time TIMESTAMP,
        user_id BIGINT,
        data STRING
    )
    USING iceberg
    PARTITIONED BY (days(event_time), bucket(100, user_id))
""")

# Insert data
spark.sql("""
    INSERT INTO events VALUES
    (1, TIMESTAMP '2023-10-15 10:00:00', 12345, 'login'),
    (2, TIMESTAMP '2023-10-15 11:00:00', 67890, 'purchase'),
    (3, TIMESTAMP '2023-10-16 09:00:00', 12345, 'logout')
""")

# Query with automatic partition pruning
result = spark.sql("""
    SELECT * FROM events
    WHERE event_time >= TIMESTAMP '2023-10-15 00:00:00'
      AND event_time < TIMESTAMP '2023-10-16 00:00:00'
      AND user_id = 12345
""")

# Iceberg automatically prunes:
# ├─ Partition: days(event_time) = 19650 (Oct 15)
# └─ Partition: bucket(100, 12345) = 45
# Result: Reads only 1 of 100+ partitions
```

---

## 🕰️ 2. Snapshot Isolation and Time Travel

### Iceberg Snapshot Model

```
Snapshots = Immutable point-in-time table states

Timeline:
T1: Snapshot 100 (1000 files)
├─ metadata: v10.metadata.json → snap-100.avro
├─ Added: 1000 files
└─ Schema: v1

T2: INSERT (100 new files)
├─ Snapshot 101 created
├─ metadata: v11.metadata.json → snap-101.avro
├─ Added: 100 files (incremental)
└─ Total files: 1100

T3: DELETE (remove 50 files)
├─ Snapshot 102 created
├─ metadata: v12.metadata.json → snap-102.avro
├─ Deleted: 50 files (marked as deleted)
└─ Live files: 1050

Snapshot Lineage:
snap-100 → snap-101 → snap-102 (current)
   │          │           │
   └──────────┴───────────┘
   All snapshots retained (until expiration)
```

**Time Travel Query:**

```sql
-- Current state (snapshot 102)
SELECT COUNT(*) FROM events;
-- Result: 1,050,000 rows

-- Time travel to snapshot 100
SELECT COUNT(*) FROM events VERSION AS OF 100;
-- Result: 1,000,000 rows

-- Time travel by timestamp
SELECT COUNT(*) FROM events TIMESTAMP AS OF '2023-10-15T10:00:00Z';
-- Result: 1,050,000 rows (snapshot at that time)
```

**PySpark Time Travel:**

```python
# Read current snapshot
df_current = spark.read.format("iceberg").load("events")
print(f"Current: {df_current.count()}")

# Read specific snapshot
df_snapshot = spark.read.format("iceberg") \
    .option("snapshot-id", "100") \
    .load("events")
print(f"Snapshot 100: {df_snapshot.count()}")

# Read as of timestamp
df_timestamp = spark.read.format("iceberg") \
    .option("as-of-timestamp", "1697385600000") \
    .load("events")
print(f"As of timestamp: {df_timestamp.count()}")
```

---

## 🔄 3. Comparing Lakehouse Formats

### Delta Lake vs Iceberg vs Hudi

```
┌──────────────────┬────────────────┬────────────────┬────────────────┐
│ Feature          │ Delta Lake     │ Iceberg        │ Hudi           │
├──────────────────┼────────────────┼────────────────┼────────────────┤
│ Metadata         │ JSON log       │ Avro metadata  │ Avro timeline  │
│                  │ (_delta_log/)  │ (3-level)      │ (.hoodie/)     │
├──────────────────┼────────────────┼────────────────┼────────────────┤
│ ACID             │ Optimistic     │ Optimistic     │ MVCC           │
│                  │ concurrency    │ concurrency    │                │
├──────────────────┼────────────────┼────────────────┼────────────────┤
│ Partitioning     │ Hive-style     │ Hidden         │ Hive-style     │
│                  │ (exposed)      │ (automatic)    │ (exposed)      │
├──────────────────┼────────────────┼────────────────┼────────────────┤
│ Time Travel      │ ✅ Version/TS  │ ✅ Snapshot/TS │ ✅ Instant/TS  │
├──────────────────┼────────────────┼────────────────┼────────────────┤
│ Schema Evolution │ ✅ Add columns │ ✅ Add/rename/ │ ✅ Add columns │
│                  │                │ reorder        │                │
├──────────────────┼────────────────┼────────────────┼────────────────┤
│ Partition Evol.  │ ❌ No          │ ✅ Yes         │ ❌ No          │
├──────────────────┼────────────────┼────────────────┼────────────────┤
│ Engine Support   │ Spark, Presto, │ Spark, Flink,  │ Spark, Flink,  │
│                  │ Flink, Trino   │ Presto, Trino, │ Presto, Hive   │
│                  │                │ Dremio         │                │
├──────────────────┼────────────────┼────────────────┼────────────────┤
│ Streaming        │ ✅ Spark       │ ✅ Flink, Spark│ ✅ Spark, Flink│
│                  │ Structured     │                │ DeltaStreamer  │
├──────────────────┼────────────────┼────────────────┼────────────────┤
│ Cloud Native     │ ✅ Excellent   │ ✅ Excellent   │ ⚠️ Good        │
│                  │ (S3, ADLS, GCS)│ (S3, ADLS, GCS)│ (S3, HDFS)     │
├──────────────────┼────────────────┼────────────────┼────────────────┤
│ Maturity         │ Production     │ Production     │ Production     │
│                  │ (Databricks)   │ (Netflix, Apple│ (Uber, Amazon) │
│                  │                │ LinkedIn)      │                │
└──────────────────┴────────────────┴────────────────┴────────────────┘
```

---

### When to Choose Each

```
Choose Delta Lake:
├─ Databricks ecosystem (tight integration)
├─ Strong Spark focus
├─ Need MERGE INTO with advanced conditions
├─ Real-time streaming with Delta Live Tables
└─ Simplicity (fewer moving parts)

Choose Apache Iceberg:
├─ Multi-engine support (Spark, Flink, Trino, Presto)
├─ Need hidden partitioning (user-friendly queries)
├─ Partition evolution required
├─ Large-scale analytics (Netflix: 10+ PB)
├─ Open governance (Apache Foundation)
└─ Advanced schema evolution (rename columns)

Choose Apache Hudi:
├─ Upsert-heavy workloads (CDC, near-real-time)
├─ Need incremental processing (MOR tables)
├─ Record-level indexing (Bloom filters, HBase index)
├─ AWS ecosystem (EMR, Glue)
└─ Low-latency reads with MOR (merge-on-read)
```

---

## 📊 4. Partition Evolution (Iceberg Only)

### The Problem with Static Partitioning

```
Initial design (2020):
PARTITIONED BY (days(event_time))
├─ 365 partitions/year
├─ Works well for 1M events/day

2023 (10M events/day):
├─ 365 partitions/year
├─ Each partition: 10M events
├─ Queries slow (large partition scans)
└─ Need finer granularity!

Traditional solution (Hive, Delta):
1. CREATE new table with hours(event_time)
2. Rewrite ALL historical data (expensive!)
3. Swap table names
Cost: $10,000+ for 10 PB rewrite ❌
```

---

### Iceberg Partition Evolution

```sql
-- Initial partition spec (2020)
CREATE TABLE events (
  event_id BIGINT,
  event_time TIMESTAMP,
  data STRING
)
USING iceberg
PARTITIONED BY (days(event_time));

-- 2023: Evolve to hourly partitioning (NO rewrite!)
ALTER TABLE events
SET PARTITION SPEC (hours(event_time));

-- Iceberg behavior:
-- Old data: Partitioned by days (unchanged)
-- New data: Partitioned by hours (from now on)

-- Query optimization:
SELECT * FROM events
WHERE event_time >= TIMESTAMP '2023-01-01 00:00:00';

-- Iceberg uses:
-- ├─ 2020-2022 data: 1095 day partitions
-- └─ 2023 data: 8760 hour partitions
-- Mixed granularity, optimal for each period!
```

**Partition Evolution Metadata:**

```
metadata/v15.metadata.json:
{
  "partition-specs": [
    {
      "spec-id": 0,
      "fields": [
        {"name": "event_time_day", "transform": "day", "source-id": 2}
      ]
    },
    {
      "spec-id": 1,  ← New spec
      "fields": [
        {"name": "event_time_hour", "transform": "hour", "source-id": 2}
      ]
    }
  ],
  "default-spec-id": 1  ← Use spec-id 1 for new writes
}

Data files:
├─ spec-id=0 (old files, day partitions)
│  ├─ event_time_day=19000/part-00000.parquet
│  └─ event_time_day=19001/part-00001.parquet
└─ spec-id=1 (new files, hour partitions)
   ├─ event_time_hour=456000/part-00002.parquet
   └─ event_time_hour=456001/part-00003.parquet
```

---

## 🗂️ 5. Schema Evolution with Column Mapping

### Column ID Mapping (Iceberg)

```
Problem (Parquet):
Parquet stores columns by NAME or POSITION
├─ Rename column → breaks existing files
└─ Reorder columns → breaks position-based readers

Iceberg Solution: Column ID Mapping

Schema v1:
{
  "fields": [
    {"id": 1, "name": "event_id", "type": "long"},
    {"id": 2, "name": "event_time", "type": "timestamp"},
    {"id": 3, "name": "user_id", "type": "long"}
  ]
}

Schema v2 (rename "event_id" → "id"):
{
  "fields": [
    {"id": 1, "name": "id", "type": "long"},  ← Same ID!
    {"id": 2, "name": "event_time", "type": "timestamp"},
    {"id": 3, "name": "user_id", "type": "long"}
  ]
}

Reading old files with new schema:
├─ Map column ID 1 (old: "event_id") → (new: "id")
├─ Read column by ID, not name
└─ Works seamlessly! ✅
```

**Advanced Schema Evolution:**

```sql
-- Add column
ALTER TABLE events ADD COLUMN country STRING;

-- Rename column (Iceberg only)
ALTER TABLE events RENAME COLUMN user_id TO customer_id;

-- Reorder columns (Iceberg only)
ALTER TABLE events ALTER COLUMN country AFTER event_time;

-- Change column type (widen only)
ALTER TABLE events ALTER COLUMN user_id TYPE BIGINT;  -- int → long

-- Drop column (Iceberg only)
ALTER TABLE events DROP COLUMN country;
```

---

## 🏆 Interview Questions (Intermediate Level)

1. **Explain Iceberg's three-level metadata hierarchy. Why is it more efficient than Delta's JSON log?**
2. **What is hidden partitioning? How does it improve query usability?**
3. **Compare Delta Lake, Iceberg, and Hudi. When would you choose each?**
4. **How does Iceberg achieve partition evolution without rewriting data?**
5. **Explain column ID mapping. Why is it important for schema evolution?**
6. **How does snapshot isolation enable time travel in Iceberg?**

---

## 🎓 Summary Checklist

- [ ] Understand Iceberg metadata architecture
- [ ] Implement hidden partitioning with transform functions
- [ ] Use snapshot isolation for time travel queries
- [ ] Compare Delta Lake, Iceberg, and Hudi
- [ ] Evolve partition specs without data rewrite
- [ ] Implement schema evolution with column mapping
- [ ] Answer intermediate interview questions

**Next:** [EXPERT.md →](EXPERT.md)
