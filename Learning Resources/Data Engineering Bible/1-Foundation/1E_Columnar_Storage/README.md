# Week 6-7: Data Warehousing & Columnar Storage

**Status:** ✅ Complete  
**Duration:** 2 weeks (80-100 hours)  
**Prerequisites:** SQL Deep Dive, Spark, Kafka  
**Target Audience:** L3+ Data Engineers, Data Warehouse Architects

---

## 📚 Module Overview

Modern data warehousing has evolved from row-based OLAP databases to **cloud-native columnar platforms** capable of querying petabytes in seconds. This module provides Principal Architect-level depth across:

- Columnar storage internals (Parquet, ORC, Capacitor)
- Modern warehouse architectures (Snowflake, BigQuery, Redshift)
- Query optimization (predicate pushdown, partition pruning, cost-based optimization)
- Performance tuning (compression, clustering, materialized views)
- Research foundations (Dremel, C-Store, MonetDB/X100)

### Why This Matters

```
Real-World Data Warehouse Deployments:

Uber:
- 100 PB data warehouse
- 10,000+ tables
- Migrated Hadoop → Snowflake/Databricks
- 70% cost reduction, 60x query speedup

Netflix:
- 10 PB data warehouse
- Redshift + S3 + BigQuery hybrid
- Powers recommendations for 200M+ users
- <1 sec p95 latency for dashboards

Airbnb:
- Multi-PB data warehouse
- Presto + Hive + BigQuery
- 10,000 analysts
- $5M/year savings via query optimization
```

---

## 🎯 Learning Path

### File Structure

```
3A_Data_Warehousing/
├── BEGINNER.md         (~15 KB)  ← Columnar basics, Parquet/ORC
├── INTERMEDIATE.md     (~35 KB)  ← BigQuery Dremel, predicate pushdown
├── EXPERT.md          (~50 KB)  ← Snowflake, Redshift, optimization
├── WHITEPAPERS.md     (~40 KB)  ← Dremel, C-Store, research papers
└── README.md          (This file)
```

### Recommended Study Sequence

| Week | Days | Topic | Files | Hands-On Lab |
|------|------|-------|-------|-------------|
| **Week 6** | Day 1-2 | Columnar Storage Basics | BEGINNER.md | Create Parquet files, compression benchmarks |
| | Day 3-4 | BigQuery Architecture | INTERMEDIATE.md | Query nested data, partition pruning analysis |
| | Day 5-7 | Snowflake/Redshift Internals | EXPERT.md (Part 1) | Micro-partitions, clustering keys |
| **Week 7** | Day 1-3 | Query Optimization | EXPERT.md (Part 2) | Cost-based optimization, materialized views |
| | Day 4-5 | Research Deep Dive | WHITEPAPERS.md | Read Dremel paper, C-Store analysis |
| | Day 6-7 | Capstone Project | All files | Build multi-TB warehouse |

---

## 📖 File Descriptions

### 1. BEGINNER.md (~15,000 bytes)

**Target Audience:** Engineers new to data warehousing or coming from OLTP databases

**Key Topics:**
- Row-based vs columnar storage (OLTP vs OLAP)
- Parquet file format (row groups, column chunks, pages, footer)
- ORC file format (stripes, columns, indexes)
- Encoding schemes (dictionary, RLE, delta, bit-packing)
- Compression algorithms (Snappy, Gzip, Zstd)
- Predicate pushdown basics (min/max statistics)
- Partition pruning fundamentals

**Practical Labs:**
1. Create Parquet files with PyArrow
2. Benchmark compression ratios (Snappy vs Zstd)
3. Inspect Parquet metadata with parquet-tools
4. Compare row-based vs columnar scan performance

**Time Estimate:** 15-20 hours

---

### 2. INTERMEDIATE.md (~35,000 bytes)

**Target Audience:** Engineers with 1-2 years data warehouse experience

**Key Topics:**
- **BigQuery/Dremel Architecture:**
  - Root/intermediate/leaf server hierarchy
  - Capacitor storage format
  - Query execution flow (parsing, planning, distribution, aggregation)
- **Nested Data in Parquet:**
  - Repetition levels (encoding repeated fields)
  - Definition levels (encoding optional/null fields)
  - Reconstruction algorithm
- **Multi-Level Predicate Pushdown:**
  - Level 1: Partition pruning (file-level)
  - Level 2: Row group pruning (metadata)
  - Level 3: Page pruning (statistics)
  - Level 4: Row filtering (after decompression)
- **Partitioning Strategies:**
  - Hive-style partitioning (year=2023/month=01/day=01/)
  - BigQuery partitioning + clustering
  - Best practices (partition size, cardinality)
- **Query Optimization:**
  - Statistics-based optimization
  - Materialized views
  - Result caching
- **Compression Deep Dive:**
  - Dictionary encoding (when to use)
  - Run-length encoding (RLE)
  - Delta encoding (for timestamps, IDs)
  - Bit-packing (bounded integers)
- **Vectorized Execution:**
  - Row-at-a-time vs batch processing
  - SIMD instructions
  - Performance benchmarks (10x speedup)

**Practical Labs:**
1. Query nested JSON data in BigQuery
2. Implement repetition/definition level encoding in Python
3. Analyze Parquet statistics for predicate pushdown
4. Create partitioned + clustered tables
5. Benchmark vectorized vs row-at-a-time execution

**Time Estimate:** 25-30 hours

---

### 3. EXPERT.md (~50,000 bytes)

**Target Audience:** Staff+ engineers, Principal Architects, FAANG candidates

**Key Topics:**

#### Snowflake Architecture
- Multi-cluster shared data architecture (compute/storage separation)
- Micro-partitions (16 MB, automatic, multi-dimensional pruning)
- Clustering keys (optimization, clustering depth, re-clustering)
- Time travel (query historical data, immutable storage)
- Zero-copy cloning (instant table copies, copy-on-write)

#### Redshift Architecture
- MPP architecture (leader node, compute nodes, slices)
- Distribution styles (KEY, ALL, EVEN)
- Sort keys (COMPOUND vs INTERLEAVED)
- Zone maps (min/max per 1MB block)
- Redshift Spectrum (query S3 Parquet directly)
- Workload management (WLM queues, concurrency scaling)

#### Cost-Based Optimization
- Cardinality estimation (histograms, multi-column stats, ML models)
- Join algorithms (nested loop, hash, merge)
- Join ordering (dynamic programming, greedy heuristics)
- Selectivity estimation (independence assumption, correlations)

#### Query Execution Models
- Volcano model (traditional, row-at-a-time, pull-based)
- Morsel-driven parallelism (batch-at-a-time, push-based, modern)
- Adaptive query execution (runtime re-optimization, Spark 3.0+)

#### Cost Optimization
- Query cost analysis (bytes scanned, slots used)
- Materialized views (incremental refresh, cost savings)
- Tiered storage (hot/warm/cold, S3 Glacier)
- Result caching (cache hit rates, TTL)

#### Real-World Case Studies
- Uber: 100 PB warehouse, 70% cost reduction
- Netflix: Multi-cloud architecture, <1 sec dashboards
- Airbnb: Query optimization, $5M/year savings

**Practical Labs:**
1. Design micro-partitions with optimal clustering
2. Choose Redshift distribution/sort keys for workload
3. Debug slow queries using EXPLAIN plans
4. Implement cost-based query optimizer prototype
5. Build multi-TB data warehouse with all optimizations
6. Migrate legacy warehouse to cloud-native platform

**Time Estimate:** 30-40 hours

---

### 4. WHITEPAPERS.md (~40,000 bytes)

**Target Audience:** Researchers, architects designing new systems, deep-dive enthusiasts

**Key Papers:**

1. **Dremel: Interactive Analysis of Web-Scale Datasets** (Google, 2010)
   - Nested columnar storage (repetition/definition levels)
   - Tree-based query execution (root/intermediate/leaf)
   - Performance: Trillion-row scans in 20 seconds
   - Impact: Foundation for BigQuery, Parquet, Drill

2. **C-Store: A Column-oriented DBMS** (MIT, 2005)
   - Hybrid storage (writeable row-store + read-optimized column-store)
   - Aggressive compression (10x better than row-stores)
   - Multiple projections (pre-materialized sorted views)
   - Performance: 33x speedup vs row-stores on TPC-H
   - Impact: Foundation for Vertica, MonetDB, ClickHouse

3. **MonetDB/X100: Hyper-Pipelining Query Execution** (CWI, 2005)
   - Vectorized execution (process batches of 1000 rows)
   - CPU efficiency (10% → 80% CPU utilization)
   - SIMD vectorization (4-8x speedup)
   - Impact: Foundation for DuckDB, ClickHouse, Snowflake

4. **Parquet: Columnar Storage for Hadoop Ecosystem** (2013)
   - Open-source columnar format
   - Compatibility with Hadoop, Spark, Hive, Presto
   - Nested data support (Avro, Thrift, Protocol Buffers)
   - Impact: De facto standard for data lakes

5. **The Snowflake Elastic Data Warehouse** (2016)
   - Cloud-native architecture (multi-cluster shared data)
   - Micro-partitions (automatic, 16 MB)
   - Time travel & zero-copy cloning
   - Impact: Pioneered modern cloud warehouse paradigm

**Time Estimate:** 15-20 hours (deep reading + note-taking)

---

## 🛠️ Hands-On Capstone Project: Multi-TB Analytics Warehouse

### Objective
Build a production-grade data warehouse for e-commerce analytics with 10 TB historical data.

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│ Data Sources                                             │
│ ├─ PostgreSQL OLTP (orders, users, products)            │
│ ├─ S3 logs (clickstream, application logs)              │
│ └─ External APIs (payment processor, shipping)          │
└─────────────┬────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────┐
│ Ingestion Layer (Kafka + Spark Streaming)               │
│ ├─ CDC from PostgreSQL (Debezium)                       │
│ ├─ Parse logs (JSON → Parquet)                          │
│ └─ Enrich with external data                            │
└─────────────┬────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────┐
│ Storage Layer (S3 Data Lake)                             │
│ ├─ Raw zone: JSON/CSV (1 day retention)                 │
│ ├─ Processed zone: Parquet partitioned by date          │
│ └─ Curated zone: Aggregated tables                      │
└─────────────┬────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────┐
│ Data Warehouse (Choose One)                              │
│ Option 1: Snowflake                                      │
│ ├─ External tables → S3 Parquet                         │
│ ├─ Materialized views for hot aggregations              │
│ └─ Clustering by (date, country, product_category)      │
│                                                          │
│ Option 2: Redshift                                       │
│ ├─ COPY from S3 Parquet                                 │
│ ├─ DISTSTYLE KEY (user_id for fact tables)             │
│ ├─ SORTKEY (date, country)                              │
│ └─ Spectrum for historical data (90+ days)              │
│                                                          │
│ Option 3: BigQuery                                       │
│ ├─ Load Parquet from GCS                                │
│ ├─ Partitioned by date, clustered by (country, category)│
│ └─ Materialized views auto-refreshed                    │
└─────────────┬────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────┐
│ BI & Analytics                                           │
│ ├─ Tableau dashboards (sales, customers, products)      │
│ ├─ Jupyter notebooks (data science)                     │
│ └─ Superset (self-service analytics)                    │
└──────────────────────────────────────────────────────────┘
```

### Implementation Steps

#### Phase 1: Data Ingestion (Week 1)

```python
# Kafka producer (CDC from PostgreSQL)
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Debezium CDC event
change_event = {
    "op": "c",  # create
    "after": {
        "order_id": 12345,
        "user_id": 67890,
        "amount": 100.50,
        "created_at": "2023-01-01T10:00:00Z"
    }
}

producer.send('orders', value=change_event)
```

```python
# Spark Streaming (consume Kafka, write Parquet)
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("CDC").getOrCreate()

df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "orders") \
    .load()

query = df \
    .selectExpr("CAST(value AS STRING) as json") \
    .writeStream \
    .format("parquet") \
    .option("path", "s3://bucket/orders/") \
    .option("checkpointLocation", "s3://bucket/checkpoints/") \
    .partitionBy("date") \
    .start()

query.awaitTermination()
```

#### Phase 2: Data Warehouse Setup (Week 1-2)

**Snowflake:**

```sql
-- Create external stage (S3)
CREATE STAGE my_s3_stage
URL = 's3://bucket/orders/'
CREDENTIALS = (AWS_KEY_ID='xxx' AWS_SECRET_KEY='yyy');

-- Create external table
CREATE EXTERNAL TABLE orders_external
WITH LOCATION = @my_s3_stage
FILE_FORMAT = (TYPE = PARQUET);

-- Load into internal table with clustering
CREATE TABLE orders
CLUSTER BY (date, country, product_category)
AS SELECT * FROM orders_external;

-- Create materialized view
CREATE MATERIALIZED VIEW sales_summary AS
SELECT 
    date,
    country,
    product_category,
    SUM(amount) as total_sales,
    COUNT(*) as num_orders
FROM orders
GROUP BY date, country, product_category;
```

**Redshift:**

```sql
-- Create table with distribution/sort keys
CREATE TABLE orders (
    order_id BIGINT,
    user_id BIGINT,
    product_id INT,
    amount DECIMAL(10,2),
    date DATE,
    country VARCHAR(2)
)
DISTSTYLE KEY
DISTKEY (user_id)
SORTKEY (date, country);

-- Load from S3
COPY orders
FROM 's3://bucket/orders/'
IAM_ROLE 'arn:aws:iam::123:role/RedshiftRole'
FORMAT AS PARQUET;

-- Create materialized view
CREATE MATERIALIZED VIEW sales_summary AS
SELECT 
    date,
    country,
    SUM(amount) as total_sales,
    COUNT(*) as num_orders
FROM orders
GROUP BY date, country;
```

**BigQuery:**

```sql
-- Load Parquet from GCS
LOAD DATA INTO dataset.orders
FROM FILES (
  format = 'PARQUET',
  uris = ['gs://bucket/orders/*.parquet']
)
PARTITION BY date
CLUSTER BY country, product_category;

-- Create materialized view
CREATE MATERIALIZED VIEW dataset.sales_summary
PARTITION BY date
CLUSTER BY country
AS
SELECT 
    date,
    country,
    SUM(amount) as total_sales,
    COUNT(*) as num_orders
FROM dataset.orders
GROUP BY date, country;
```

#### Phase 3: Optimization & Monitoring (Week 2)

```sql
-- Snowflake: Check clustering quality
SELECT SYSTEM$CLUSTERING_INFORMATION('orders', '(date, country)');

-- Redshift: Analyze distribution skew
SELECT 
    slice,
    COUNT(*) as row_count
FROM stv_blocklist
WHERE tbl = (SELECT oid FROM pg_class WHERE relname = 'orders')
GROUP BY slice
ORDER BY row_count DESC;

-- BigQuery: Query execution analysis
SELECT
    query,
    total_bytes_processed,
    total_slot_ms,
    total_bytes_billed
FROM `project.dataset.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
ORDER BY total_bytes_processed DESC
LIMIT 10;
```

---

## 📊 Assessment Checklist

### Beginner Level ✅
- [ ] Explain row-based vs columnar storage
- [ ] Describe Parquet file structure (row groups, pages, footer)
- [ ] Implement compression benchmarks (Snappy vs Zstd)
- [ ] Create Parquet files with PyArrow
- [ ] Understand predicate pushdown basics

### Intermediate Level ✅
- [ ] Explain BigQuery/Dremel architecture
- [ ] Encode nested data with repetition/definition levels
- [ ] Implement multi-level predicate pushdown
- [ ] Design partitioning + clustering strategies
- [ ] Create materialized views for optimization
- [ ] Understand vectorized execution

### Expert Level ✅
- [ ] Design Snowflake micro-partitions with optimal clustering
- [ ] Choose Redshift distribution/sort keys for workload
- [ ] Implement cost-based query optimizer
- [ ] Debug slow queries using execution plans
- [ ] Optimize warehouse costs (materialized views, caching, tiering)
- [ ] Migrate multi-TB warehouse to cloud platform
- [ ] Pass Staff+/Principal Engineer interviews

---

## 🎓 Interview Preparation

### Common Questions

1. **Basic:**
   - "Why is columnar storage faster for analytics?"
   - "Explain Parquet file format."
   - "How does predicate pushdown work?"

2. **Intermediate:**
   - "Design a partitioning strategy for time-series data."
   - "How does BigQuery handle nested JSON?"
   - "Compare Snowflake vs Redshift."

3. **Advanced:**
   - "Design a multi-PB data warehouse for global e-commerce."
   - "Debug a query that's 100x slower than expected."
   - "Optimize warehouse costs by 80%."

4. **Principal Architect:**
   - "Migrate 100 PB Hadoop warehouse to cloud with zero downtime."
   - "Design active-active multi-region warehouse for compliance."
   - "Explain trade-offs: Snowflake vs Databricks vs BigQuery."

---

## 🔗 Additional Resources

### Official Documentation
- [Snowflake Docs](https://docs.snowflake.com/)
- [BigQuery Docs](https://cloud.google.com/bigquery/docs)
- [Redshift Docs](https://docs.aws.amazon.com/redshift/)
- [Parquet Format Spec](https://parquet.apache.org/docs/)

### Books
- **The Data Warehouse Toolkit** (3rd Edition) - Ralph Kimball
- **Designing Data-Intensive Applications** (Chapter 3) - Martin Kleppmann
- **Database Internals** - Alex Petrov

### Courses
- [Snowflake Hands-On Essentials](https://learn.snowflake.com/)
- [BigQuery for Data Warehousing](https://cloud.google.com/training)
- [AWS Redshift Deep Dive](https://aws.amazon.com/training/)

---

## ✅ Completion Criteria

You have mastered Week 6-7 when you can:

1. **Build:** Implement a multi-TB data warehouse with partitioning, clustering, and materialized views
2. **Optimize:** Reduce query costs by 80% via optimization techniques
3. **Debug:** Identify and fix slow queries using execution plans
4. **Design:** Architect a petabyte-scale warehouse for global company
5. **Explain:** Teach warehouse internals (micro-partitions, predicate pushdown) to junior engineers
6. **Interview:** Pass Staff+/Principal Engineer interviews at FAANG

---

**Time Investment:** 80-100 hours  
**Difficulty:** ★★★★☆ (Advanced)  
**ROI:** ★★★★★ (Critical for modern data infrastructure)

**Next Steps:**
- Continue to [Week 8-9: Apache Flink](../3B_Apache_Flink/README.md)
- Or review [Week 5: Kafka](../../2-Intermediate/2A_Kafka_Fundamentals/README.md)

---

**Last Updated:** January 2025  
**Contributors:** Data Engineering Bible Project  
**License:** Educational Use Only

---

**End of README** | [Start with BEGINNER.md →](BEGINNER.md)
