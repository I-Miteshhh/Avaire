# Week 12-13: Lakehouse Architecture — EXPERT Track

*"Apache Hudi's merge-on-read with incremental processing changed the game for real-time analytics at Uber. Understanding COW vs MOR, compaction strategies, and indexing is critical for L7+ engineers."* — Principal Engineer, Uber

---

## 🎯 Learning Outcomes

- Master Apache Hudi copy-on-write (COW) vs merge-on-read (MOR) architectures
- Implement incremental processing with Hudi timeline server
- Design compaction strategies for MOR tables
- Optimize query performance with indexing (Bloom filters, HBase, record-level)
- Implement CDC pipelines with Hudi DeltaStreamer
- Handle small file problems with clustering
- Design multi-table transactions with Iceberg
- Tune lakehouse performance for 10+ PB scale (Netflix, Uber case studies)

---

## 🔷 1. Apache Hudi Deep Dive

### Copy-on-Write (COW) vs Merge-on-Read (MOR)

```
┌────────────────────────────────────────────────────────────────┐
│ Copy-on-Write (COW)                                            │
├────────────────────────────────────────────────────────────────┤
│ Write Path:                                                    │
│ 1. Read existing Parquet file (if update)                     │
│ 2. Merge with new records                                     │
│ 3. Write new Parquet file (full rewrite)                      │
│ 4. Delete old file                                            │
│                                                                │
│ Storage:                                                       │
│ ├─ Only Parquet files (.parquet)                              │
│ └─ No delta logs                                              │
│                                                                │
│ Read Path:                                                     │
│ ├─ Read Parquet files directly                                │
│ └─ No merge required ✅ FAST                                  │
│                                                                │
│ Write Performance:                                             │
│ ├─ Slow (full file rewrite)                                   │
│ └─ High I/O cost ❌                                           │
│                                                                │
│ Use Case:                                                      │
│ ├─ Read-heavy workloads                                       │
│ ├─ Batch processing (hourly/daily)                            │
│ └─ Append-mostly data                                         │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ Merge-on-Read (MOR)                                            │
├────────────────────────────────────────────────────────────────┤
│ Write Path:                                                    │
│ 1. Write updates to delta log (.log file)                     │
│ 2. No file rewrite (append-only)                              │
│ 3. Periodic compaction merges deltas → Parquet                │
│                                                                │
│ Storage:                                                       │
│ ├─ Base files: Parquet (.parquet)                             │
│ └─ Delta files: Avro logs (.log)                              │
│                                                                │
│ Read Path (Two Views):                                        │
│ 1. Read Optimized (RO):                                       │
│    ├─ Read only Parquet files                                 │
│    ├─ Skip delta logs                                         │
│    └─ Fast but stale ⚠️                                       │
│                                                                │
│ 2. Real-Time (RT):                                            │
│    ├─ Read Parquet + delta logs                               │
│    ├─ Merge on-the-fly                                        │
│    └─ Slow but fresh ✅                                       │
│                                                                │
│ Write Performance:                                             │
│ ├─ Fast (append-only writes)                                  │
│ └─ Low I/O cost ✅                                            │
│                                                                │
│ Use Case:                                                      │
│ ├─ Write-heavy workloads                                      │
│ ├─ Real-time upserts (CDC)                                    │
│ └─ Low-latency writes (<1 min)                                │
└────────────────────────────────────────────────────────────────┘
```

---

### File Layout Example

```
Copy-on-Write (COW):
s3://bucket/hudi-table/
├─ .hoodie/
│  ├─ 20231015100000.commit
│  └─ 20231015110000.commit
└─ partition_path=2023-10-15/
   ├─ abc123_0_20231015100000.parquet (Version 1)
   └─ abc123_0_20231015110000.parquet (Version 2, replaced Version 1)

Merge-on-Read (MOR):
s3://bucket/hudi-table/
├─ .hoodie/
│  ├─ 20231015100000.deltacommit
│  ├─ 20231015101000.deltacommit
│  └─ 20231015110000.commit (compaction)
└─ partition_path=2023-10-15/
   ├─ abc123_0_20231015100000.parquet (Base file)
   ├─ .abc123_0_20231015100000.log.1 (Delta 1)
   ├─ .abc123_0_20231015100000.log.2 (Delta 2)
   └─ abc123_0_20231015110000.parquet (Compacted base file)
```

---

### Creating COW vs MOR Tables

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.hudi.catalog.HoodieCatalog") \
    .config("spark.sql.extensions", "org.apache.spark.sql.hudi.HoodieSparkSessionExtension") \
    .getOrCreate()

# Copy-on-Write Table
spark.sql("""
    CREATE TABLE events_cow (
        event_id BIGINT,
        event_time TIMESTAMP,
        user_id BIGINT,
        data STRING
    )
    USING hudi
    TBLPROPERTIES (
        type = 'cow',
        primaryKey = 'event_id',
        preCombineField = 'event_time'
    )
    PARTITIONED BY (event_date DATE)
    LOCATION 's3://bucket/events_cow'
""")

# Merge-on-Read Table
spark.sql("""
    CREATE TABLE events_mor (
        event_id BIGINT,
        event_time TIMESTAMP,
        user_id BIGINT,
        data STRING
    )
    USING hudi
    TBLPROPERTIES (
        type = 'mor',
        primaryKey = 'event_id',
        preCombineField = 'event_time'
    )
    PARTITIONED BY (event_date DATE)
    LOCATION 's3://bucket/events_mor'
""")
```

---

## ⚙️ 2. Compaction Strategies

### Inline vs Async Compaction

```
┌────────────────────────────────────────────────────────────┐
│ Inline Compaction                                          │
├────────────────────────────────────────────────────────────┤
│ Behavior:                                                  │
│ ├─ Compaction runs DURING write                           │
│ ├─ Blocks write until compaction completes                │
│ └─ Configurable interval (every N commits)                │
│                                                            │
│ Pros:                                                      │
│ ├─ Simple (no separate job)                               │
│ └─ Automatic compaction                                   │
│                                                            │
│ Cons:                                                      │
│ ├─ Slow writes (compaction overhead)                      │
│ └─ Resource contention (write + compact)                  │
│                                                            │
│ Use Case:                                                  │
│ └─ Low write volume (<10 GB/hour)                         │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ Async Compaction                                           │
├────────────────────────────────────────────────────────────┤
│ Behavior:                                                  │
│ ├─ Compaction scheduled by writer                         │
│ ├─ Executed by separate compaction job                    │
│ └─ Does NOT block writes                                  │
│                                                            │
│ Pros:                                                      │
│ ├─ Fast writes (no compaction overhead)                   │
│ ├─ Dedicated resources for compaction                     │
│ └─ Scalable (parallel compaction)                         │
│                                                            │
│ Cons:                                                      │
│ ├─ Operational complexity (separate job)                  │
│ └─ Potential lag (if compactor slow)                      │
│                                                            │
│ Use Case:                                                  │
│ └─ High write volume (>100 GB/hour)                       │
└────────────────────────────────────────────────────────────┘
```

---

### Compaction Configuration

```python
# Inline compaction (simple)
hudi_options = {
    'hoodie.table.name': 'events_mor',
    'hoodie.datasource.write.table.type': 'MERGE_ON_READ',
    'hoodie.datasource.write.operation': 'upsert',
    'hoodie.datasource.write.recordkey.field': 'event_id',
    'hoodie.datasource.write.precombine.field': 'event_time',
    'hoodie.datasource.write.partitionpath.field': 'event_date',
    
    # Inline compaction config
    'hoodie.compact.inline': 'true',
    'hoodie.compact.inline.max.delta.commits': '5',  # Compact every 5 commits
    'hoodie.compaction.strategy': 'org.apache.hudi.table.action.compact.strategy.LogFileSizeBasedCompactionStrategy',
    'hoodie.compaction.logfile.size.threshold': '1073741824',  # 1 GB
}

df.write.format('hudi').options(**hudi_options).mode('append').save('s3://bucket/events_mor')

# Async compaction (production)
hudi_options_async = {
    'hoodie.table.name': 'events_mor',
    'hoodie.datasource.write.table.type': 'MERGE_ON_READ',
    'hoodie.datasource.write.operation': 'upsert',
    'hoodie.datasource.write.recordkey.field': 'event_id',
    'hoodie.datasource.write.precombine.field': 'event_time',
    'hoodie.datasource.write.partitionpath.field': 'event_date',
    
    # Async compaction config
    'hoodie.compact.inline': 'false',  # Disable inline
    'hoodie.compact.schedule.inline': 'true',  # Schedule only
    'hoodie.compact.inline.max.delta.commits': '10',
}

# Writer: Schedule compaction
df.write.format('hudi').options(**hudi_options_async).mode('append').save('s3://bucket/events_mor')

# Separate Compactor Job:
from pyspark.sql import SparkSession

compactor = SparkSession.builder \
    .appName("HudiCompactor") \
    .config("spark.sql.extensions", "org.apache.spark.sql.hudi.HoodieSparkSessionExtension") \
    .getOrCreate()

compactor.sql("""
    CALL run_compaction(
        table => 'events_mor',
        path => 's3://bucket/events_mor'
    )
""")
```

---

### Compaction Strategies

```
1. LogFileSizeBasedCompactionStrategy:
   ├─ Trigger: Total log file size > threshold
   ├─ Config: hoodie.compaction.logfile.size.threshold = 1 GB
   └─ Use case: Balanced (default)

2. UnboundedCompactionStrategy:
   ├─ Trigger: Every scheduled commit
   ├─ Compacts ALL file groups
   └─ Use case: Aggressive compaction (small tables)

3. BoundedPartitionAwareCompactionStrategy:
   ├─ Trigger: Based on partition age
   ├─ Config: hoodie.compaction.strategy.daybased.lookback.partitions = 3
   ├─ Compacts only recent partitions (last 3 days)
   └─ Use case: Large tables (>10 TB)

Example:
hudi_options = {
    'hoodie.compaction.strategy': 'org.apache.hudi.table.action.compact.strategy.BoundedPartitionAwareCompactionStrategy',
    'hoodie.compaction.strategy.daybased.lookback.partitions': '3',
    'hoodie.compaction.daybased.target.io': '5368709120',  # 5 GB target I/O
}
```

---

## 📇 3. Indexing for Fast Upserts

### Index Types

```
┌─────────────────┬──────────────┬─────────────┬────────────────┐
│ Index Type      │ Lookup Time  │ Storage     │ Use Case       │
├─────────────────┼──────────────┼─────────────┼────────────────┤
│ BLOOM           │ O(files)     │ Metadata    │ Small tables   │
│                 │ ~100ms       │ (~1% size)  │ (<100 GB)      │
├─────────────────┼──────────────┼─────────────┼────────────────┤
│ SIMPLE (Global) │ O(1)         │ Spark state │ Medium tables  │
│                 │ ~10ms        │ (in-memory) │ (100 GB-1 TB)  │
├─────────────────┼──────────────┼─────────────┼────────────────┤
│ HBASE           │ O(1)         │ HBase       │ Large tables   │
│                 │ ~5ms         │ (external)  │ (>1 TB)        │
├─────────────────┼──────────────┼─────────────┼────────────────┤
│ BUCKET          │ O(1)         │ Metadata    │ Known dist.    │
│                 │ ~1ms         │ (minimal)   │ (hash buckets) │
└─────────────────┴──────────────┴─────────────┴────────────────┘
```

---

### Bloom Filter Index

```python
# Bloom filter index (default for COW/MOR)
hudi_options = {
    'hoodie.index.type': 'BLOOM',
    'hoodie.bloom.index.parallelism': '100',
    'hoodie.bloom.index.prune.by.ranges': 'true',  # Prune by column ranges
    'hoodie.bloom.index.use.metadata': 'true',  # Use metadata table
    
    # Bloom filter tuning
    'hoodie.index.bloom.num_entries': '60000',  # Expected entries per file
    'hoodie.index.bloom.fpp': '0.000000001',  # False positive probability (1 in 1B)
}

# How it works:
# 1. Upsert 1000 records with keys [k1, k2, ..., k1000]
# 2. For each file:
#    ├─ Check bloom filter: "Does file contain k1?"
#    ├─ If NO → Skip file ✅
#    └─ If MAYBE → Read file, check actual keys
# 3. Only read files with matching keys
# 4. Merge updates, write new files
```

---

### HBase Index

```python
# HBase index for large-scale upserts
hudi_options = {
    'hoodie.index.type': 'HBASE',
    'hoodie.index.hbase.zkquorum': 'zk1:2181,zk2:2181,zk3:2181',
    'hoodie.index.hbase.zkport': '2181',
    'hoodie.index.hbase.table': 'hudi_index_events',
    'hoodie.index.hbase.zknode.path': '/hbase',
    
    # HBase tuning
    'hoodie.index.hbase.put.batch.size': '100',
    'hoodie.index.hbase.get.batch.size': '100',
}

# How it works:
# 1. Upsert 1M records with keys [k1, k2, ..., k1000000]
# 2. Batch lookup in HBase (100 keys at a time):
#    HBase: k1 → partition=2023-10-15, file=abc123.parquet
# 3. Group updates by file
# 4. Read only affected files (~100 files instead of 10,000)
# 5. Merge and write

# Throughput:
# ├─ Bloom: 10K upserts/sec
# └─ HBase: 100K upserts/sec ✅
```

---

### Bucket Index (Hash-Based)

```python
# Bucket index for uniform distribution
hudi_options = {
    'hoodie.index.type': 'BUCKET',
    'hoodie.index.bucket.engine': 'CONSISTENT_HASHING',
    'hoodie.bucket.index.num.buckets': '256',  # Fixed bucket count
    'hoodie.bucket.index.hash.field': 'user_id',  # Hash on user_id
}

# How it works:
# 1. Hash user_id to bucket: bucket = hash(user_id) % 256
# 2. Each bucket = 1 file group
# 3. Upsert record with user_id=12345:
#    ├─ bucket = hash(12345) % 256 = 45
#    └─ Write to bucket 45 file
# 4. No index lookup needed! O(1) ✅

# Requirements:
# ├─ Uniform key distribution (hash works well)
# ├─ Fixed bucket count (no auto-scaling)
# └─ Single hash key (no composite keys)
```

---

## 🚰 4. Incremental Processing

### Hudi Timeline and Incremental Queries

```
Hudi Timeline = Ordered sequence of commits

Timeline:
├─ 20231015100000.commit (1000 records inserted)
├─ 20231015110000.commit (500 records updated)
├─ 20231015120000.commit (200 records deleted)
└─ 20231015130000.commit (1500 records inserted)

Incremental Query:
"Give me all changes since commit 20231015100000"

Result:
├─ 500 updated records (from commit 110000)
├─ 200 deleted records (from commit 120000)
└─ 1500 inserted records (from commit 130000)
Total: 2200 records (instead of scanning full table)
```

**Implementation:**

```python
# Initial read (full table scan)
df = spark.read.format('hudi').load('s3://bucket/events')

# Get latest commit
latest_commit = spark.read.format('hudi') \
    .option('hoodie.datasource.query.type', 'snapshot') \
    .load('s3://bucket/events') \
    .selectExpr('max(_hoodie_commit_time) as max_commit') \
    .collect()[0]['max_commit']

print(f"Latest commit: {latest_commit}")

# Incremental query (only changes since last commit)
incremental_df = spark.read.format('hudi') \
    .option('hoodie.datasource.query.type', 'incremental') \
    .option('hoodie.datasource.read.begin.instanttime', '20231015100000') \
    .option('hoodie.datasource.read.end.instanttime', latest_commit) \
    .load('s3://bucket/events')

print(f"Incremental rows: {incremental_df.count()}")

# Process only changed data
incremental_df.write.format('delta').mode('append').save('s3://bucket/processed')
```

---

### DeltaStreamer for CDC

```python
# Hudi DeltaStreamer: Incremental ingestion from Kafka

from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("HudiDeltaStreamer") \
    .config("spark.sql.extensions", "org.apache.spark.sql.hudi.HoodieSparkSessionExtension") \
    .getOrCreate()

# DeltaStreamer config
deltastreamer_config = {
    'hoodie.datasource.write.recordkey.field': 'id',
    'hoodie.datasource.write.partitionpath.field': 'date',
    'hoodie.datasource.write.precombine.field': 'updated_at',
    'hoodie.datasource.write.table.name': 'users',
    'hoodie.datasource.write.operation': 'upsert',
    'hoodie.datasource.write.table.type': 'MERGE_ON_READ',
    
    # Kafka source
    'hoodie.deltastreamer.source.kafka.topic': 'users_cdc',
    'hoodie.deltastreamer.source.kafka.bootstrap.servers': 'kafka:9092',
    'hoodie.deltastreamer.source.kafka.value.deserializer.class': 'io.confluent.kafka.serializers.KafkaAvroDeserializer',
    'hoodie.deltastreamer.schema.registry.url': 'http://schema-registry:8081',
    
    # Checkpoint
    'hoodie.deltastreamer.checkpoint.provider.path': 's3://bucket/checkpoints/users',
    
    # Compaction
    'hoodie.compact.inline': 'false',
    'hoodie.compact.schedule.inline': 'true',
    'hoodie.compact.inline.max.delta.commits': '5',
}

# Run DeltaStreamer
spark.sparkContext.setSystemProperty('hoodie.deltastreamer.config.file', 'deltastreamer.properties')

spark.sql("""
    CALL run_deltastreamer(
        table_name => 'users',
        table_type => 'MERGE_ON_READ',
        base_path => 's3://bucket/users',
        source_class => 'org.apache.hudi.utilities.sources.JsonKafkaSource',
        source_ordering_field => 'updated_at',
        target_table => 'users',
        target_base_path => 's3://bucket/users',
        props => 'deltastreamer.properties'
    )
""")
```

**Pipeline:**

```
┌─────────────┐       ┌─────────────────┐       ┌─────────────┐
│ MySQL CDC   │ ───>  │ Kafka (Debezium)│ ───>  │ Hudi Table  │
│ (binlog)    │       │ (JSON/Avro)     │       │ (MOR)       │
└─────────────┘       └─────────────────┘       └─────────────┘
      │                      │                         │
      ▼                      ▼                         ▼
   INSERT                 Produce                  Upsert
   UPDATE                 {                        (merge)
   DELETE                   "op": "u",
                           "before": {...},
                           "after": {...}
                         }

Latency: <1 minute (Kafka → Hudi)
Throughput: 100K events/sec
```

---

## 🏆 Production Case Studies

### Uber: Trip Data Processing

```
Requirements:
├─ 100M trips/day
├─ Real-time updates (ETA, fare changes)
├─ Historical analysis (3 years retention)
└─ Sub-minute freshness

Architecture:
┌──────────────────────────────────────────────────────────┐
│ Source: Kafka (trip events)                              │
│ ├─ trip_started, trip_updated, trip_completed            │
│ └─ 1M events/hour                                        │
└──────────────┬───────────────────────────────────────────┘
               ▼
┌──────────────────────────────────────────────────────────┐
│ Hudi DeltaStreamer (MOR table)                           │
│ ├─ Upsert by trip_id (primary key)                      │
│ ├─ Partitioned by date                                  │
│ ├─ HBase index (fast lookups)                           │
│ └─ Async compaction (every hour)                        │
└──────────────┬───────────────────────────────────────────┘
               ▼
┌──────────────────────────────────────────────────────────┐
│ Hudi Table: trips (10 PB)                                │
│ ├─ Real-time view: Fresh data (<1 min lag)              │
│ ├─ Read-optimized view: Compacted data (1 hour lag)     │
│ └─ Incremental queries: Only changed trips               │
└──────────────┬───────────────────────────────────────────┘
               ▼
┌──────────────────────────────────────────────────────────┐
│ Consumers:                                               │
│ ├─ Presto (real-time analytics)                         │
│ ├─ Spark (ML training on read-optimized)                │
│ └─ Hive (batch ETL on incremental)                      │
└──────────────────────────────────────────────────────────┘

Configuration:
- Table type: MERGE_ON_READ
- Index: HBASE (HBase cluster with 50 nodes)
- Compaction: Async (dedicated Spark cluster)
- Partitions: Daily (365 partitions/year)
- File size target: 512 MB
- Retention: 3 years (automated cleanup)
```

---

### Netflix: Content Metadata (Iceberg)

```
Requirements:
├─ 10M content items (movies, series, episodes)
├─ 1000 updates/sec (metadata changes)
├─ Query across 100+ tables (JOIN optimization)
└─ Multi-region replication

Architecture:
┌──────────────────────────────────────────────────────────┐
│ Apache Iceberg Tables (100+ tables)                      │
│ ├─ content_metadata (10M rows)                          │
│ ├─ viewing_history (1B rows)                            │
│ ├─ recommendations (500M rows)                           │
│ └─ user_profiles (200M rows)                            │
└──────────────┬───────────────────────────────────────────┘
               ▼
┌──────────────────────────────────────────────────────────┐
│ Features Used:                                           │
│ 1. Hidden Partitioning:                                 │
│    PARTITIONED BY (days(updated_at))                    │
│    → Users query: WHERE updated_at = '2023-10-15'       │
│    → Iceberg auto-prunes partitions                     │
│                                                          │
│ 2. Snapshot Isolation:                                  │
│    ├─ Read-after-write consistency                      │
│    ├─ Time travel for auditing                          │
│    └─ Rollback on bad writes                            │
│                                                          │
│ 3. Schema Evolution:                                    │
│    ├─ Add columns without downtime                      │
│    ├─ Rename columns (column ID mapping)                │
│    └─ Backward compatible reads                         │
│                                                          │
│ 4. Multi-Engine Support:                                │
│    ├─ Spark (ETL)                                       │
│    ├─ Presto (ad-hoc queries)                           │
│    ├─ Flink (real-time updates)                         │
│    └─ Trino (federated queries)                         │
└──────────────────────────────────────────────────────────┘

Storage:
├─ S3 (primary: 10 PB)
├─ Multi-region replication (us-east-1, eu-west-1)
└─ Intelligent tiering (Glacier for old data)

Performance:
├─ Query latency: <1 second (P50), <5 seconds (P99)
├─ Write throughput: 1M rows/minute
└─ Concurrent readers: 1000+ Spark jobs
```

---

## 🏆 Interview Questions (Expert Level)

1. **Compare Hudi COW vs MOR. When would you choose each for a real-time analytics platform?**
2. **Explain async compaction in Hudi. How would you tune it for a 10 TB table with 1M upserts/hour?**
3. **What is the HBase index? How does it achieve O(1) lookups for upserts?**
4. **Design a CDC pipeline from PostgreSQL to Hudi with sub-minute latency. What are the bottlenecks?**
5. **Explain Iceberg's three-level metadata. Why is it more scalable than Delta Lake's JSON log?**
6. **How would you handle small file problems in a lakehouse with 100K partitions?**
7. **Compare bloom filter vs HBase vs bucket indexing. Which would you use for 1B row table?**
8. **Design a multi-table transaction in Iceberg. How does it ensure atomicity?**
9. **Explain partition evolution in Iceberg. How does it work without rewriting data?**
10. **You have a Hudi MOR table with 1000 log files per partition. Read queries are slow. How do you fix it?**

---

## 🎓 Summary Checklist

- [ ] Understand Hudi COW vs MOR architectures
- [ ] Implement compaction strategies (inline vs async)
- [ ] Configure indexing (Bloom, HBase, Bucket)
- [ ] Design incremental processing pipelines
- [ ] Implement CDC with Hudi DeltaStreamer
- [ ] Optimize for 10+ PB scale (Uber, Netflix patterns)
- [ ] Handle schema evolution and partition evolution
- [ ] Answer expert-level interview questions

**Next:** [WHITEPAPERS.md →](WHITEPAPERS.md)
