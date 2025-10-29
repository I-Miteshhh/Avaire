# Week 12-13: Lakehouse Architecture (Delta Lake, Iceberg, Hudi)

**Duration:** 2 weeks  
**Difficulty:** Advanced  
**Prerequisites:** Weeks 1-11 (Spark, Kafka, Flink, Beam)

---

## 📋 Module Overview

Modern data platforms are converging on the **lakehouse architecture**—combining the flexibility of data lakes with the ACID guarantees of data warehouses. This module covers the three leading lakehouse formats:

1. **Delta Lake** (Databricks): Simple, production-ready ACID transactions
2. **Apache Iceberg** (Netflix): Scalable, multi-engine table format
3. **Apache Hudi** (Uber): Real-time upserts and incremental processing

By the end of this module, you will:
- Understand how ACID transactions work on object storage (S3, ADLS, GCS)
- Implement time travel and schema evolution
- Design CDC pipelines with Hudi DeltaStreamer
- Optimize query performance with hidden partitioning (Iceberg)
- Choose the right format for production use cases

---

## 🗓️ 2-Week Learning Path

### Week 1: Foundations + Delta Lake + Iceberg

#### Day 1-2: Lakehouse Fundamentals
- **Theory:** Data lake vs warehouse vs lakehouse evolution
- **Reading:** [BEGINNER.md](BEGINNER.md) — Sections 1-3
- **Hands-on:** Create your first Delta Lake table
  ```python
  # Create Delta table
  df.write.format('delta').mode('overwrite').save('s3://bucket/delta_table')
  
  # Time travel
  spark.read.format('delta').option('versionAsOf', 0).load('s3://bucket/delta_table')
  ```
- **Quiz:** What is optimistic concurrency control? How does Delta ensure ACID on S3?

#### Day 3-4: Delta Lake Deep Dive
- **Theory:** Transaction log, checkpointing, VACUUM
- **Reading:** [BEGINNER.md](BEGINNER.md) — Sections 4-6
- **Hands-on:** Implement UPDATE, DELETE, MERGE (upsert)
  ```python
  from delta.tables import DeltaTable
  
  delta_table = DeltaTable.forPath(spark, 's3://bucket/delta_table')
  delta_table.update(condition="age < 18", set={"status": "'minor'"})
  delta_table.delete(condition="status = 'deleted'")
  delta_table.merge(source_df, "target.id = source.id") \
      .whenMatchedUpdateAll() \
      .whenNotMatchedInsertAll() \
      .execute()
  ```
- **Exercise:** Build CDC pipeline from PostgreSQL → Kafka → Delta Lake

#### Day 5-6: Apache Iceberg Metadata
- **Theory:** 3-level metadata hierarchy, hidden partitioning
- **Reading:** [INTERMEDIATE.md](INTERMEDIATE.md) — Sections 1-2
- **Hands-on:** Create Iceberg table with hidden partitioning
  ```python
  spark.sql("""
      CREATE TABLE events (
          event_id BIGINT,
          event_time TIMESTAMP,
          data STRING
      )
      USING iceberg
      PARTITIONED BY (days(event_time))
      LOCATION 's3://bucket/events_iceberg'
  """)
  
  # Query auto-prunes partitions
  spark.sql("SELECT * FROM events WHERE event_time = '2023-10-15'")
  ```
- **Exercise:** Compare query performance with/without hidden partitioning

#### Day 7: Partition Evolution
- **Theory:** Iceberg partition spec evolution
- **Reading:** [INTERMEDIATE.md](INTERMEDIATE.md) — Section 4
- **Hands-on:** Change partitioning without rewriting data
  ```python
  # Start: Daily partitions
  spark.sql("CREATE TABLE events PARTITIONED BY (days(event_time))")
  
  # After 1 year: Switch to monthly
  spark.sql("ALTER TABLE events SET PARTITION SPEC (months(event_time))")
  
  # Query works across both partition schemes!
  spark.sql("SELECT * FROM events WHERE event_time >= '2023-01-01'")
  ```
- **Quiz:** Why can't Delta Lake do partition evolution?

---

### Week 2: Apache Hudi + Production Optimization

#### Day 8-9: Hudi COW vs MOR
- **Theory:** Copy-on-write vs merge-on-read table types
- **Reading:** [EXPERT.md](EXPERT.md) — Section 1
- **Hands-on:** Create COW and MOR tables, compare write latency
  ```python
  # COW table
  df.write.format('hudi') \
      .option('hoodie.table.name', 'events_cow') \
      .option('hoodie.datasource.write.table.type', 'COPY_ON_WRITE') \
      .mode('append').save('s3://bucket/events_cow')
  
  # MOR table
  df.write.format('hudi') \
      .option('hoodie.table.name', 'events_mor') \
      .option('hoodie.datasource.write.table.type', 'MERGE_ON_READ') \
      .mode('append').save('s3://bucket/events_mor')
  
  # Compare write times
  ```
- **Exercise:** Measure write throughput (COW vs MOR)

#### Day 10-11: Compaction Strategies
- **Theory:** Inline vs async compaction, compaction strategies
- **Reading:** [EXPERT.md](EXPERT.md) — Section 2
- **Hands-on:** Configure async compaction with separate compactor job
  ```python
  # Writer: Schedule compaction
  hudi_options = {
      'hoodie.compact.inline': 'false',
      'hoodie.compact.schedule.inline': 'true',
      'hoodie.compact.inline.max.delta.commits': '10',
  }
  
  # Compactor job:
  spark.sql("CALL run_compaction(table => 'events_mor', path => 's3://bucket/events_mor')")
  ```
- **Exercise:** Implement BoundedPartitionAwareCompactionStrategy for 10 TB table

#### Day 12-13: Indexing and Incremental Processing
- **Theory:** Bloom filter, HBase index, bucket index, incremental queries
- **Reading:** [EXPERT.md](EXPERT.md) — Sections 3-4
- **Hands-on:** Implement HBase index for fast upserts
  ```python
  hudi_options = {
      'hoodie.index.type': 'HBASE',
      'hoodie.index.hbase.zkquorum': 'zk1:2181',
      'hoodie.index.hbase.table': 'hudi_index_events',
  }
  
  # Incremental query
  incremental_df = spark.read.format('hudi') \
      .option('hoodie.datasource.query.type', 'incremental') \
      .option('hoodie.datasource.read.begin.instanttime', '20231015100000') \
      .load('s3://bucket/events_mor')
  ```
- **Exercise:** Build real-time analytics pipeline with incremental processing

#### Day 14: Whitepaper Analysis
- **Reading:** [WHITEPAPERS.md](WHITEPAPERS.md)
- **Deep dive:** Delta protocol, Iceberg spec, Hudi design paper
- **Discussion:** Trade-offs between formats (scalability, complexity, maturity)
- **Quiz:** When would you choose Delta vs Iceberg vs Hudi?

---

## 🏗️ Capstone Project: Build Production Lakehouse from Scratch

### Project Requirements

Design and implement a **real-time analytics platform** for an e-commerce company processing:
- **User events:** 10M events/day (clicks, searches, purchases)
- **Product catalog:** 1M products, updated hourly
- **Order transactions:** 100K orders/day, CDC from PostgreSQL
- **Latency:** <5 minute end-to-end (event → analytics)
- **Retention:** 3 years (hot: 90 days, warm: 1 year, cold: archive)

---

### Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│ Data Sources                                                     │
├──────────────────────────────────────────────────────────────────┤
│ 1. User Events (Kafka):                                         │
│    ├─ Topic: user-events                                        │
│    ├─ Schema: {event_id, user_id, event_type, timestamp, data}  │
│    └─ Volume: 10M events/day (~120 events/sec)                  │
│                                                                  │
│ 2. Product Catalog (S3 CSV):                                    │
│    ├─ File: products.csv (updated hourly)                       │
│    ├─ Schema: {product_id, name, price, category, updated_at}   │
│    └─ Volume: 1M products (~500 MB)                             │
│                                                                  │
│ 3. Order Transactions (PostgreSQL CDC):                         │
│    ├─ Database: orders_db                                       │
│    ├─ Schema: {order_id, user_id, products, total, created_at}  │
│    └─ Volume: 100K orders/day (~1 order/sec)                    │
└──────────────────────────────────────────────────────────────────┘
               │                │                │
               ▼                ▼                ▼
┌──────────────────────────────────────────────────────────────────┐
│ Ingestion Layer                                                  │
├──────────────────────────────────────────────────────────────────┤
│ 1. User Events:                                                  │
│    ├─ Flink job consumes Kafka                                  │
│    ├─ Watermarks for late events (5 min)                        │
│    ├─ Writes to Hudi MOR table (low-latency writes)             │
│    └─ Partitioned by date (days(timestamp))                     │
│                                                                  │
│ 2. Product Catalog:                                             │
│    ├─ Spark batch job (hourly)                                  │
│    ├─ Writes to Delta Lake table (simple batch)                 │
│    └─ Schema evolution enabled                                  │
│                                                                  │
│ 3. Order Transactions:                                          │
│    ├─ Debezium CDC → Kafka                                      │
│    ├─ Hudi DeltaStreamer consumes Kafka                         │
│    ├─ Writes to Hudi MOR table (upserts)                        │
│    └─ HBase index for fast lookups                              │
└──────────────────────────────────────────────────────────────────┘
               │                │                │
               ▼                ▼                ▼
┌──────────────────────────────────────────────────────────────────┐
│ Lakehouse Layer (S3)                                             │
├──────────────────────────────────────────────────────────────────┤
│ 1. user_events/ (Hudi MOR)                                       │
│    ├─ Partitions: date=2023-10-15/, date=2023-10-16/, ...       │
│    ├─ Files: .parquet (base) + .log (deltas)                    │
│    ├─ Compaction: Async (every hour)                            │
│    └─ Retention: 3 years (Glacier after 1 year)                 │
│                                                                  │
│ 2. products/ (Delta Lake)                                        │
│    ├─ Partitions: None (small table)                            │
│    ├─ Files: .parquet                                           │
│    ├─ Time travel: 30 days                                      │
│    └─ VACUUM: 7 days                                            │
│                                                                  │
│ 3. orders/ (Hudi MOR)                                            │
│    ├─ Partitions: date=2023-10-15/, date=2023-10-16/, ...       │
│    ├─ Files: .parquet (base) + .log (deltas)                    │
│    ├─ Index: HBase (order_id → file mapping)                    │
│    └─ Incremental processing: Enabled                           │
└──────────────────────────────────────────────────────────────────┘
               │                │                │
               ▼                ▼                ▼
┌──────────────────────────────────────────────────────────────────┐
│ Consumption Layer                                                │
├──────────────────────────────────────────────────────────────────┤
│ 1. Real-time Dashboard (Presto):                                │
│    ├─ Query: "Top 10 products sold in last hour"                │
│    ├─ Read: Hudi real-time view (fresh data)                    │
│    └─ Latency: <5 seconds (P99)                                 │
│                                                                  │
│ 2. Batch Analytics (Spark):                                     │
│    ├─ Job: "Daily revenue report"                               │
│    ├─ Read: Hudi read-optimized view (compacted)                │
│    └─ Runtime: <10 minutes                                      │
│                                                                  │
│ 3. ML Training (Spark):                                         │
│    ├─ Dataset: Last 90 days of events                           │
│    ├─ Incremental: Only changed data (Hudi incremental)         │
│    └─ Frequency: Daily                                          │
└──────────────────────────────────────────────────────────────────┘
```

---

### Implementation Tasks

#### Task 1: Set Up Hudi MOR Table for User Events

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, window
from pyspark.sql.types import StructType, StringType, LongType, TimestampType

spark = SparkSession.builder \
    .appName("UserEventsIngestion") \
    .config("spark.sql.extensions", "org.apache.spark.sql.hudi.HoodieSparkSessionExtension") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .getOrCreate()

# Read from Kafka
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "user-events") \
    .option("startingOffsets", "latest") \
    .load()

# Parse JSON
schema = StructType() \
    .add("event_id", LongType()) \
    .add("user_id", LongType()) \
    .add("event_type", StringType()) \
    .add("timestamp", TimestampType()) \
    .add("data", StringType())

events_df = kafka_df.select(
    from_json(col("value").cast("string"), schema).alias("event")
).select("event.*")

# Write to Hudi MOR
hudi_options = {
    'hoodie.table.name': 'user_events',
    'hoodie.datasource.write.table.type': 'MERGE_ON_READ',
    'hoodie.datasource.write.operation': 'upsert',
    'hoodie.datasource.write.recordkey.field': 'event_id',
    'hoodie.datasource.write.precombine.field': 'timestamp',
    'hoodie.datasource.write.partitionpath.field': 'date',
    
    # Async compaction
    'hoodie.compact.inline': 'false',
    'hoodie.compact.schedule.inline': 'true',
    'hoodie.compact.inline.max.delta.commits': '10',
    
    # Bloom filter index
    'hoodie.index.type': 'BLOOM',
    'hoodie.bloom.index.parallelism': '100',
}

query = events_df \
    .withColumn("date", col("timestamp").cast("date")) \
    .writeStream \
    .format("hudi") \
    .options(**hudi_options) \
    .option("checkpointLocation", "s3://bucket/checkpoints/user_events") \
    .outputMode("append") \
    .start("s3://bucket/lakehouse/user_events")

query.awaitTermination()
```

**Success Criteria:**
- [ ] Kafka consumer running (no lag)
- [ ] Hudi table partitioned by date
- [ ] Compaction scheduled (check .hoodie/ directory)
- [ ] Query latency <5 seconds (Presto real-time view)

---

#### Task 2: Set Up Delta Lake for Product Catalog

```python
# Read product catalog CSV
products_df = spark.read.csv(
    "s3://bucket/raw/products.csv",
    header=True,
    inferSchema=True
)

# Write to Delta Lake
products_df.write.format('delta') \
    .mode('overwrite') \
    .option('overwriteSchema', 'true') \
    .save('s3://bucket/lakehouse/products')

# Enable schema evolution
spark.sql("""
    ALTER TABLE delta.`s3://bucket/lakehouse/products`
    SET TBLPROPERTIES (
        'delta.autoOptimize.optimizeWrite' = 'true',
        'delta.autoOptimize.autoCompact' = 'true'
    )
""")

# Hourly refresh job
from delta.tables import DeltaTable

delta_table = DeltaTable.forPath(spark, 's3://bucket/lakehouse/products')

# Upsert new data
new_products_df = spark.read.csv("s3://bucket/raw/products_latest.csv", header=True)

delta_table.alias("target").merge(
    new_products_df.alias("source"),
    "target.product_id = source.product_id"
).whenMatchedUpdateAll() \
 .whenNotMatchedInsertAll() \
 .execute()
```

**Success Criteria:**
- [ ] Delta table created with schema enforcement
- [ ] Hourly refresh working (no duplicates)
- [ ] Time travel enabled (query past versions)
- [ ] VACUUM configured (7-day retention)

---

#### Task 3: Set Up Hudi DeltaStreamer for Orders CDC

```bash
# Start Debezium connector for PostgreSQL
curl -X POST http://localhost:8083/connectors -H "Content-Type: application/json" -d '{
  "name": "orders-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "debezium",
    "database.password": "password",
    "database.dbname": "orders_db",
    "database.server.name": "orders",
    "table.include.list": "public.orders",
    "plugin.name": "pgoutput",
    "topic.prefix": "orders-cdc"
  }
}'
```

```python
# Hudi DeltaStreamer config
deltastreamer_config = {
    'hoodie.datasource.write.recordkey.field': 'order_id',
    'hoodie.datasource.write.partitionpath.field': 'date',
    'hoodie.datasource.write.precombine.field': 'updated_at',
    'hoodie.datasource.write.table.name': 'orders',
    'hoodie.datasource.write.operation': 'upsert',
    'hoodie.datasource.write.table.type': 'MERGE_ON_READ',
    
    # HBase index for fast upserts
    'hoodie.index.type': 'HBASE',
    'hoodie.index.hbase.zkquorum': 'zookeeper:2181',
    'hoodie.index.hbase.table': 'hudi_orders_index',
    
    # Kafka source
    'hoodie.deltastreamer.source.kafka.topic': 'orders-cdc.public.orders',
    'hoodie.deltastreamer.source.kafka.bootstrap.servers': 'kafka:9092',
}

# Run DeltaStreamer
spark.sparkContext.setSystemProperty('hoodie.deltastreamer.config.file', 'deltastreamer.properties')

spark.sql("""
    CALL run_deltastreamer(
        table_name => 'orders',
        table_type => 'MERGE_ON_READ',
        base_path => 's3://bucket/lakehouse/orders',
        source_class => 'org.apache.hudi.utilities.sources.JsonKafkaSource',
        source_ordering_field => 'updated_at',
        target_table => 'orders',
        props => 'deltastreamer.properties'
    )
""")
```

**Success Criteria:**
- [ ] Debezium capturing PostgreSQL changes
- [ ] Kafka topic receiving CDC events
- [ ] Hudi DeltaStreamer ingesting with <1 min latency
- [ ] HBase index lookup <10 ms (measure with tracing)

---

#### Task 4: Query Optimization

```sql
-- Presto real-time analytics
-- Query: Top 10 products sold in last hour

SELECT
    p.product_id,
    p.name,
    COUNT(DISTINCT o.order_id) AS order_count,
    SUM(o.total) AS revenue
FROM hudi.user_events e
JOIN delta.products p ON e.data:product_id = p.product_id
JOIN hudi.orders o ON e.user_id = o.user_id
WHERE e.event_type = 'purchase'
  AND e.timestamp >= NOW() - INTERVAL '1' HOUR
GROUP BY p.product_id, p.name
ORDER BY revenue DESC
LIMIT 10;

-- Optimization 1: Partition pruning
-- Hudi auto-prunes partitions: Only read today's partition

-- Optimization 2: Predicate pushdown
-- Filter event_type = 'purchase' pushed to Parquet reader

-- Optimization 3: Stats pruning
-- Skip files where timestamp < NOW() - 1 HOUR (using min/max stats)

-- Expected latency: <5 seconds (P99)
```

**Performance Tuning:**

```python
# Enable dynamic partition pruning
spark.conf.set("spark.sql.optimizer.dynamicPartitionPruning.enabled", "true")

# Enable adaptive query execution
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")

# Set target file size
spark.conf.set("hoodie.parquet.max.file.size", 536870912)  # 512 MB

# Enable predicate pushdown
spark.conf.set("spark.sql.parquet.filterPushdown", "true")
spark.conf.set("spark.sql.parquet.aggregatePushdown", "true")
```

---

#### Task 5: Incremental ML Pipeline

```python
# ML training with incremental processing

# Initial training (full dataset)
initial_df = spark.read.format('hudi') \
    .option('hoodie.datasource.query.type', 'snapshot') \
    .load('s3://bucket/lakehouse/user_events')

initial_df.write.parquet('s3://bucket/ml/training_v1')

# Get latest commit
latest_commit = spark.read.format('hudi') \
    .load('s3://bucket/lakehouse/user_events') \
    .selectExpr('max(_hoodie_commit_time) as max_commit') \
    .collect()[0]['max_commit']

# Daily incremental update
incremental_df = spark.read.format('hudi') \
    .option('hoodie.datasource.query.type', 'incremental') \
    .option('hoodie.datasource.read.begin.instanttime', latest_commit) \
    .load('s3://bucket/lakehouse/user_events')

# Append to training dataset
incremental_df.write.mode('append').parquet('s3://bucket/ml/training_v2')

# Train model (only on changed data)
from pyspark.ml.classification import RandomForestClassifier

rf = RandomForestClassifier(labelCol="purchased", featuresCol="features")
model = rf.fit(incremental_df)

model.save('s3://bucket/ml/models/rf_v2')
```

**Success Criteria:**
- [ ] Incremental processing reduces data scanned by 99%
- [ ] Daily ML training completes in <10 minutes
- [ ] Model accuracy improves with fresh data

---

## 📊 Assessment Checklist

### Beginner Level
- [ ] Explain data lake vs data warehouse vs lakehouse
- [ ] Create Delta Lake table with time travel
- [ ] Implement schema evolution (add column)
- [ ] Understand optimistic concurrency control
- [ ] Configure VACUUM for data retention

### Intermediate Level
- [ ] Explain Iceberg 3-level metadata hierarchy
- [ ] Implement hidden partitioning with transform functions
- [ ] Understand snapshot isolation model
- [ ] Compare Delta vs Iceberg vs Hudi (use cases)
- [ ] Design partition evolution strategy

### Expert Level
- [ ] Implement Hudi MOR table with async compaction
- [ ] Configure HBase index for fast upserts
- [ ] Build CDC pipeline with Hudi DeltaStreamer
- [ ] Optimize query performance (partition pruning, stats pruning)
- [ ] Design lakehouse for 10 PB scale (Netflix/Uber patterns)

### Capstone Project
- [ ] Ingest 10M events/day with <5 min latency
- [ ] Implement CDC from PostgreSQL to Hudi
- [ ] Build real-time dashboard (Presto)
- [ ] Implement incremental ML pipeline
- [ ] Handle 3-year retention with tiering (hot/warm/cold)

---

## 🎯 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Ingestion Latency** | <5 minutes | Kafka event time → Hudi commit time |
| **Query Latency (Real-time)** | <5 seconds (P99) | Presto query on Hudi RT view |
| **Query Latency (Batch)** | <1 second (P50) | Presto query on Hudi RO view |
| **Write Throughput** | 10K events/sec | Hudi upsert rate |
| **Storage Efficiency** | <10% overhead | Metadata size / data size |
| **Compaction Lag** | <1 hour | Time since last compaction |
| **Data Freshness** | <1 minute | Latest commit timestamp |

---

## 📚 Additional Resources

### Official Documentation
- [Delta Lake Docs](https://docs.delta.io/)
- [Apache Iceberg Docs](https://iceberg.apache.org/)
- [Apache Hudi Docs](https://hudi.apache.org/)

### Research Papers
- [Delta Lake: High-Performance ACID Table Storage](https://databricks.com/wp-content/uploads/2020/08/p975-armbrust.pdf)
- [Apache Iceberg: The Definitive Guide](https://www.oreilly.com/library/view/apache-iceberg-the/9781098148614/)
- [Building a Lakehouse at Uber](https://www.uber.com/blog/lakehouse/)

### Video Tutorials
- [Databricks Delta Lake Deep Dive](https://www.youtube.com/watch?v=LJtShrQqYZY)
- [Netflix Tech Blog: Iceberg at Scale](https://netflixtechblog.com/iceberg-tables-powering-data-analytics-at-netflix-870c6b3566ef)
- [Uber Engineering: Hudi Architecture](https://www.youtube.com/watch?v=1w3IpavhSWA)

---

## ✅ Module Completion

Upon completing this module, you should:
1. Understand how lakehouse formats enable ACID on data lakes
2. Implement production CDC pipelines with sub-minute latency
3. Optimize query performance with partition/stats pruning
4. Choose the right format (Delta/Iceberg/Hudi) for specific use cases
5. Design lakehouse architecture for 10+ PB scale

**Congratulations! You've mastered Lakehouse Architecture.**

**Next Module:** [Week 14: Orchestration (Airflow, Dagster, Prefect) →](../../4-Production/4A_Orchestration/README.md)
