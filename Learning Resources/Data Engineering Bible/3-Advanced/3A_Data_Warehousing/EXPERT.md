# Week 6-7: Data Warehousing & Columnar Storage — EXPERT Track

*"At scale, every query optimization decision has multi-million dollar cost implications. Understanding warehouse internals is what separates Principal Architects from senior engineers."* — Snowflake Distinguished Engineer

---

## 🎯 Learning Outcomes

At the EXPERT level, you will achieve mastery in:

- **Snowflake Architecture**: Micro-partitions, pruning algorithms, time travel, zero-copy cloning
- **Redshift Architecture**: Distribution styles, sort keys, zone maps, workload management
- **Cost-Based Optimization**: Join algorithms, selectivity estimation, cardinality estimation
- **Query Execution Internals**: Volcano model, Morsel-driven parallelism, adaptive query execution
- **Storage Optimization**: Data skipping, clustering keys, automatic query acceleration
- **Performance Tuning**: Identifying bottlenecks, optimizing hot paths, cost analysis
- **Real-World Case Studies**: Multi-PB warehouses at Uber, Netflix, Airbnb

---

## 📚 Prerequisites

- ✅ Parquet/ORC internals (BEGINNER.md)
- ✅ BigQuery/Dremel architecture (INTERMEDIATE.md)
- ✅ Predicate pushdown and partition pruning
- ✅ SQL advanced concepts (CTEs, window functions, lateral joins)

---

## ❄️ 1. Snowflake Architecture: The Cloud Data Warehouse

Snowflake pioneered the **multi-cluster shared data architecture**, separating storage, compute, and services.

### Three-Layer Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Cloud Services Layer                      │
│  ├─ Authentication & Access Control                         │
│  ├─ Query Optimizer & Compiler                              │
│  ├─ Metadata Management                                     │
│  └─ Transaction Management                                  │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│                  Compute Layer (Virtual Warehouses)          │
│  ├─ Warehouse 1 (X-Small: 1 node, 8 cores)                 │
│  ├─ Warehouse 2 (Large: 8 nodes, 64 cores)                 │
│  └─ Warehouse 3 (X-Large: 16 nodes, 128 cores)             │
│  (Elastically scaled, isolated compute)                     │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│                Storage Layer (Cloud Object Storage)          │
│  ├─ S3/Azure Blob/GCS (columnar files)                      │
│  ├─ Micro-partitions (16 MB compressed)                     │
│  ├─ Metadata (min/max, bloom filters, clustering info)      │
│  └─ Immutable files (time travel, zero-copy clone)          │
└──────────────────────────────────────────────────────────────┘
```

**Key Innovations:**
1. **Shared-Nothing Compute**: Each virtual warehouse is independent (no contention)
2. **Shared-Everything Storage**: All warehouses access same data (no data copying)
3. **Elastic Scaling**: Add/remove warehouses in seconds
4. **Pay-Per-Use**: Compute and storage billed separately

---

### Micro-Partitions: Snowflake's Secret Sauce

```
Traditional Table (Hive-style partitioning):
┌────────────────────────────────────────────────────────┐
│ date=2023-01-01/                                       │
│   ├─ part-00000.parquet (1 GB)                         │
│   ├─ part-00001.parquet (1 GB)                         │
│   └─ part-00002.parquet (1 GB)                         │
│ date=2023-01-02/                                       │
│   └─ part-00000.parquet (1 GB)                         │
└────────────────────────────────────────────────────────┘

Problem:
- Large files → Slow small queries
- User must choose partition key (static decision)
- Partition explosion (too many small files)

Snowflake Micro-Partitions:
┌────────────────────────────────────────────────────────┐
│ Micro-Partition 0: 16 MB compressed (50-500 MB raw)   │
│   Metadata:                                            │
│   ├─ date: min=2023-01-01, max=2023-01-01             │
│   ├─ user_id: min=1000, max=5000                      │
│   └─ amount: min=10, max=9999                         │
│                                                        │
│ Micro-Partition 1: 16 MB compressed                   │
│   Metadata:                                            │
│   ├─ date: min=2023-01-01, max=2023-01-01             │
│   ├─ user_id: min=5001, max=9000                      │
│   └─ amount: min=5, max=8888                          │
│ ...                                                    │
│ Micro-Partition N: 16 MB compressed                   │
│   Metadata:                                            │
│   ├─ date: min=2023-01-02, max=2023-01-02             │
│   ├─ user_id: min=1000, max=6000                      │
│   └─ amount: min=20, max=7777                         │
└────────────────────────────────────────────────────────┘

Benefits:
- Automatic partitioning (no user intervention)
- Small files → Fast small queries
- Min/max stats for ALL columns (multi-dimensional pruning)
- Clustering automatically optimized
```

**Pruning Algorithm:**

```sql
SELECT * FROM sales WHERE date = '2023-01-01' AND user_id = 3000;

Step 1: Prune by date
- Check: date_min <= '2023-01-01' <= date_max
- Micro-Partition 0: ✓ (min=2023-01-01, max=2023-01-01)
- Micro-Partition 1: ✓ (min=2023-01-01, max=2023-01-01)
- Micro-Partition N: ✗ (min=2023-01-02, skip!)

Step 2: Prune by user_id
- Check: user_id_min <= 3000 <= user_id_max
- Micro-Partition 0: ✓ (min=1000, max=5000)
- Micro-Partition 1: ✗ (min=5001, skip!)

Result: Scan 1 micro-partition instead of N (99% pruning!)
```

---

### Clustering Keys: Optimizing Micro-Partition Layout

```sql
-- Table without clustering (random order)
CREATE TABLE sales AS
SELECT * FROM raw_sales;

Micro-partitions (random layout):
MP 0: date=[2023-01-01, 2023-01-15], user_id=[1, 9999]
MP 1: date=[2023-01-03, 2023-01-20], user_id=[5, 8888]
MP 2: date=[2023-01-02, 2023-01-10], user_id=[10, 7777]
...

Query: WHERE date = '2023-01-01'
Result: Must scan ALL micro-partitions (poor pruning!)

-- Table with clustering key
CREATE TABLE sales_clustered
CLUSTER BY (date, user_id) AS
SELECT * FROM raw_sales;

Micro-partitions (sorted by date, user_id):
MP 0: date=[2023-01-01, 2023-01-01], user_id=[1, 3000]
MP 1: date=[2023-01-01, 2023-01-01], user_id=[3001, 6000]
MP 2: date=[2023-01-01, 2023-01-01], user_id=[6001, 9000]
MP 3: date=[2023-01-02, 2023-01-02], user_id=[1, 3000]
...

Query: WHERE date = '2023-01-01'
Result: Scan only MP 0-2 (3 partitions instead of all!)

Query: WHERE date = '2023-01-01' AND user_id = 3000
Result: Scan only MP 0 (1 partition!)
```

**Clustering Depth:**

```sql
-- Check clustering quality
SELECT SYSTEM$CLUSTERING_INFORMATION('sales_clustered', '(date, user_id)');

Result:
{
  "cluster_by_keys": "(date, user_id)",
  "total_partition_count": 1000,
  "total_constant_partition_count": 800,  -- 80% perfectly clustered
  "average_overlaps": 2.5,                 -- Avg 2.5 overlapping partitions
  "average_depth": 3.2,                    -- Avg 3.2 partitions per value
  "partition_depth_histogram": {
    "00000": 0,
    "00001": 500,
    "00002": 300,
    "00003": 150,
    "00004": 50
  }
}

Interpretation:
- Lower depth = better clustering
- Depth 1 = perfect (1 partition per value)
- Depth > 10 = poor clustering (re-cluster!)

-- Re-cluster table
ALTER TABLE sales_clustered RECLUSTER;
```

---

### Time Travel & Zero-Copy Cloning

```sql
-- Time travel (query historical data)
SELECT * FROM sales AT (OFFSET => -3600);  -- 1 hour ago
SELECT * FROM sales BEFORE (STATEMENT => '01a1b2c3-...');  -- Before specific query
SELECT * FROM sales AT (TIMESTAMP => '2023-01-01 10:00:00'::TIMESTAMP);

-- How it works:
Snowflake maintains:
1. Immutable micro-partitions (never modified)
2. Metadata snapshots every transaction
3. Retention period: 1-90 days (configurable)

When you query historical data:
- Lookup metadata snapshot at specified time
- Read micro-partitions that existed at that time
- No data copying! (just metadata lookup)

Cost: Storage for retained micro-partitions

-- Zero-copy clone (instant table copy)
CREATE TABLE sales_copy CLONE sales;

How it works:
1. Copy metadata (pointers to micro-partitions)
2. Do NOT copy actual data
3. Copy completes in seconds (even for multi-TB tables!)

When you modify sales_copy:
- New micro-partitions created for modified data
- Original micro-partitions remain shared with sales
- Copy-on-write semantics

Use cases:
- Dev/test environments (clone production data)
- Data science experiments (clone, experiment, discard)
- Backup/restore (clone before risky operations)
```

---

## 🔴 2. Amazon Redshift Architecture: MPP Data Warehouse

Redshift is a **Massively Parallel Processing (MPP)** warehouse based on PostgreSQL.

### Cluster Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Leader Node                               │
│  ├─ Query Parser & Optimizer                                │
│  ├─ Query Planner (generates execution plan)                │
│  ├─ Metadata Catalog                                        │
│  └─ Coordinates compute nodes                               │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│                  Compute Nodes (2-128)                       │
│                                                              │
│  Node 1:                                                     │
│  ├─ Local SSD (1.6 TB)                                      │
│  ├─ Slices (2-32 per node)                                  │
│  │  ├─ Slice 0: CPU cores, memory, disk                     │
│  │  └─ Slice 1: CPU cores, memory, disk                     │
│  └─ Query execution engine                                  │
│                                                              │
│  Node 2:                                                     │
│  ├─ Local SSD (1.6 TB)                                      │
│  └─ Slices ...                                               │
│  ...                                                         │
│  Node N:                                                     │
│  └─ Slices ...                                               │
└──────────────────────────────────────────────────────────────┘
```

**Key Concepts:**
- **Slice:** Unit of parallelism (1-32 per node)
- **Distribution:** How data is distributed across nodes
- **Sort Key:** Physical sort order on disk
- **Zone Map:** Min/max statistics per 1MB block

---

### Distribution Styles

```sql
-- 1. KEY Distribution (hash-based)
CREATE TABLE sales (
    sale_id INT,
    user_id INT,
    amount DECIMAL
)
DISTSTYLE KEY
DISTKEY (user_id);

How it works:
- Hash user_id → Distribute to slice
- sale_id=101, user_id=12345 → hash(12345) % num_slices = slice 5
- All rows with same user_id on same slice

Pros:
- Fast joins (co-located data)
- Even distribution (if good key)

Cons:
- Skew risk (if key has hot values)

-- 2. ALL Distribution (replicate to all nodes)
CREATE TABLE dim_date (
    date_id INT,
    year INT,
    month INT,
    day INT
)
DISTSTYLE ALL;

How it works:
- Copy table to all slices
- Every slice has full table

Pros:
- No shuffle for joins
- Fast for small dimension tables

Cons:
- Wasted storage
- Slow writes (replicate to all nodes)

-- 3. EVEN Distribution (round-robin)
CREATE TABLE events (
    event_id INT,
    timestamp TIMESTAMP,
    data JSON
)
DISTSTYLE EVEN;

How it works:
- Round-robin distribution
- Row 0 → Slice 0, Row 1 → Slice 1, ...

Pros:
- Perfect balance
- Good for staging tables

Cons:
- No join optimization
- Requires shuffle for aggregations
```

**Distribution Strategy Decision Tree:**

```
Is table < 10 GB and used in many joins?
├─ YES: DISTSTYLE ALL (dimension table)
└─ NO:
    Is there a column frequently used in joins?
    ├─ YES: DISTSTYLE KEY DISTKEY(column)
    └─ NO: DISTSTYLE EVEN
```

---

### Sort Keys: Physical Data Ordering

```sql
-- Compound Sort Key (multi-column sort)
CREATE TABLE events (
    user_id INT,
    timestamp TIMESTAMP,
    event_type VARCHAR(50)
)
SORTKEY (user_id, timestamp);

Physical layout on disk:
Block 0: user_id=[1, 100], timestamp=[2023-01-01, 2023-01-05]
Block 1: user_id=[101, 200], timestamp=[2023-01-01, 2023-01-03]
Block 2: user_id=[201, 300], timestamp=[2023-01-02, 2023-01-06]

Query: WHERE user_id = 150 AND timestamp = '2023-01-02'
Zone map pruning:
- Block 0: user_id max=100 < 150 → Skip!
- Block 1: user_id in [101, 200] ✓, timestamp doesn't match → Scan
- Block 2: user_id min=201 > 150 → Skip!

-- Interleaved Sort Key (multi-dimensional sort)
CREATE TABLE events (
    user_id INT,
    timestamp TIMESTAMP,
    event_type VARCHAR(50)
)
INTERLEAVED SORTKEY (user_id, timestamp, event_type);

How it works:
- Z-order curve (space-filling curve)
- Interleaves bits from multiple columns
- Better for multi-dimensional queries

Example (simplified):
user_id=5 (binary: 101), timestamp=3 (binary: 011)
Interleaved: 100111 (alternating bits)

Pros:
- Good for range queries on ANY column
- No column order priority

Cons:
- Expensive to maintain (VACUUM)
- Slower than compound for single-column filters
```

**Sort Key Best Practices:**

```
Use COMPOUND SORTKEY when:
- Clear filter column priority (e.g., always filter by date first)
- Query pattern: WHERE date = X AND user_id = Y (in that order)

Use INTERLEAVED SORTKEY when:
- No clear column priority
- Query pattern: WHERE user_id = X OR WHERE timestamp = Y (varied)

Recommendation: Start with COMPOUND (simpler), switch to INTERLEAVED if needed
```

---

### Redshift Spectrum: Query S3 Data Directly

```sql
-- External table (data in S3, schema in Redshift)
CREATE EXTERNAL SCHEMA spectrum
FROM DATA CATALOG
DATABASE 'sales_db'
IAM_ROLE 'arn:aws:iam::123456:role/SpectrumRole'
CREATE EXTERNAL DATABASE IF NOT EXISTS;

CREATE EXTERNAL TABLE spectrum.sales (
    sale_id INT,
    user_id INT,
    amount DECIMAL
)
STORED AS PARQUET
LOCATION 's3://my-bucket/sales/';

-- Query combines Redshift table + S3 data
SELECT 
    r.user_id,
    r.user_name,
    SUM(s.amount) as total_sales
FROM 
    users r  -- Redshift table
JOIN 
    spectrum.sales s  -- S3 Parquet files
ON 
    r.user_id = s.user_id
GROUP BY 
    r.user_id, r.user_name;

How it works:
1. Redshift scans local `users` table
2. Pushes predicates to Spectrum layer
3. Spectrum spins up workers in S3 (separate compute pool)
4. Spectrum workers scan Parquet files in S3
5. Return filtered results to Redshift
6. Redshift performs join

Benefits:
- Separate compute for S3 scans (no impact on Redshift cluster)
- Query PB-scale data without loading into Redshift
- Pay per GB scanned (not per hour)

Use cases:
- Historical data (rarely queried, stored in S3)
- Data lake integration
- Cost optimization (keep hot data in Redshift, cold in S3)
```

---

## ⚙️ 3. Cost-Based Query Optimization

### Cardinality Estimation

```sql
Table: users (10 million rows)
- user_id: primary key (unique)
- country: 100 unique values
- age: 100 unique values

Query: SELECT * FROM users WHERE country = 'US' AND age = 25;

Naive estimate (independence assumption):
- Selectivity(country='US') = 1/100 = 1%
- Selectivity(age=25) = 1/100 = 1%
- Combined: 1% × 1% = 0.01%
- Estimated rows: 10M × 0.01% = 1,000 rows

Problem: country and age are correlated!
- US has older population (age 25 rare)
- Actual rows: 50 (50x underestimate!)

Advanced estimate (histogram + multi-column stats):
- Histogram: country='US' has 30% of rows (3M)
- Age distribution in US: age=25 → 0.5% of US rows
- Estimated rows: 3M × 0.5% = 15,000 rows (closer!)

Actual estimate (machine learning):
- Train model on query workload
- Predict cardinality using learned patterns
- Estimated rows: 45 rows (within 10% error!)
```

**Optimizer Statistics:**

```sql
-- Snowflake (automatic stats collection)
-- No manual ANALYZE needed, stats updated on writes

-- Redshift (manual stats collection)
ANALYZE users;  -- Collect stats for all columns
ANALYZE users (country, age);  -- Specific columns

-- PostgreSQL (manual with sampling)
ANALYZE users;  -- Default 100 sample rows
ANALYZE users (10000);  -- Custom sample size

-- BigQuery (automatic stats, manual refresh)
-- Stats automatically collected, updated every 30 days
```

---

### Join Algorithms

#### 1. Nested Loop Join (Small × Large)

```sql
SELECT * FROM small_table s
JOIN large_table l ON s.id = l.id;

Algorithm:
for each row in small_table:
    for each row in large_table:
        if small.id == large.id:
            output row

Complexity: O(n × m)
Use when: One table is small (< 10K rows), no indexes

Cost: 100 rows × 1M rows = 100M comparisons
```

#### 2. Hash Join (Medium × Medium)

```sql
SELECT * FROM table1 t1
JOIN table2 t2 ON t1.id = t2.id;

Algorithm:
1. Build phase: Hash table1 on join key
   hash_table = {id: row for row in table1}

2. Probe phase: Scan table2, lookup in hash
   for each row in table2:
       if row.id in hash_table:
           output (hash_table[row.id], row)

Complexity: O(n + m)
Use when: Both tables fit in memory, no indexes

Cost: 1M rows + 1M rows = 2M operations (much faster!)
```

#### 3. Merge Join (Sorted × Sorted)

```sql
SELECT * FROM table1 t1
JOIN table2 t2 ON t1.id = t2.id;
-- Both tables have SORTKEY(id)

Algorithm:
pointer1 = 0
pointer2 = 0
while pointer1 < len(table1) and pointer2 < len(table2):
    if table1[pointer1].id == table2[pointer2].id:
        output (table1[pointer1], table2[pointer2])
        pointer1++
        pointer2++
    elif table1[pointer1].id < table2[pointer2].id:
        pointer1++
    else:
        pointer2++

Complexity: O(n + m)
Use when: Both tables sorted on join key

Cost: 1M rows + 1M rows = 2M operations (fast, no hash overhead!)
```

**Optimizer Decision:**

```
Join Cost Estimation:
┌────────────────────────────────────────────────────────┐
│ Join Type      │ Cost Formula                         │
├────────────────────────────────────────────────────────┤
│ Nested Loop    │ O(n × m)                             │
│ Hash Join      │ O(n + m) + memory(n)                 │
│ Merge Join     │ O(n + m) if sorted, else O(n log n)  │
└────────────────────────────────────────────────────────┘

Decision:
if min(n, m) < 1000:
    use Nested Loop Join
elif both sorted:
    use Merge Join
else:
    use Hash Join
```

---

## 🚀 4. Query Execution Models

### Volcano Model (Traditional)

```
Volcano Model (row-at-a-time, pull-based):

┌─────────────────┐
│  Root Operator  │  ← Pull one row
│   (Aggregate)   │
└────────┬────────┘
         │ Pull
         ▼
┌─────────────────┐
│  Join Operator  │  ← Pull one row from each child
└────────┬────────┘
         │ Pull
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│ Scan A │ │ Scan B │  ← Read one row from disk
└────────┘ └────────┘

Problems:
- Function call per row (overhead)
- Poor CPU cache utilization
- Hard to vectorize
```

### Morsel-Driven Parallelism (Modern)

```
Morsel-Driven (batch-at-a-time, push-based):

┌─────────────────────────────────────────┐
│  Coordinator                            │
│  - Generates morsels (batches of ~1000) │
│  - Assigns to worker threads            │
└─────────────┬───────────────────────────┘
              │
        ┌─────┴──────┬──────────┐
        ▼            ▼          ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │ Worker 1│ │ Worker 2│ │ Worker 3│
   │ Process │ │ Process │ │ Process │
   │ Morsel A│ │ Morsel B│ │ Morsel C│
   └─────────┘ └─────────┘ └─────────┘

Benefits:
- Batch processing (amortize overhead)
- Better CPU cache (SIMD vectorization)
- Dynamic load balancing (worker steals morsels)
- Lock-free shared hash tables

Used in:
- Hyper (now Tableau/Salesforce)
- DuckDB
- Snowflake
```

### Adaptive Query Execution (Spark 3.0+)

```
Problem: Static plans break with bad estimates

Example:
SELECT * FROM users u
JOIN events e ON u.id = e.user_id
WHERE u.country = 'US';

Static plan (before execution):
1. Scan users, filter country='US'
   Estimated: 1M rows (but actually 10 rows!)
2. Hash join with events
   Allocated: 1 GB memory (wasted!)
   Join type: Hash join (wrong choice!)

Adaptive plan (during execution):
1. Scan users, filter country='US'
   Actual: 10 rows (re-optimize!)
2. Broadcast join with events (change plan mid-execution!)
   Allocated: 1 KB memory
   Join type: Broadcast join (correct!)

Techniques:
- Runtime statistics collection
- Dynamic join strategy selection
- Dynamic partition coalescing
- Dynamic filter pushdown
```

---

## 💰 5. Cost Optimization Strategies

### Query Cost Analysis

```sql
-- Snowflake: Query profile
SELECT SYSTEM$EXPLAIN_PLAN_JSON(
  'SELECT * FROM sales WHERE date = ''2023-01-01'''
);

Output:
{
  "nodes": [
    {
      "id": 1,
      "operation": "TableScan[sales]",
      "partitionsTotal": 1000,
      "partitionsAssigned": 10,  ← 99% pruned!
      "bytesScanned": 160000000,
      "rowsProduced": 1000000
    },
    {
      "id": 2,
      "operation": "Filter[date='2023-01-01']",
      "rowsInput": 1000000,
      "rowsOutput": 50000
    }
  ]
}

Cost Analysis:
- 1000 micro-partitions total
- 990 pruned (date mismatch)
- 10 scanned (160 MB)
- At $40/TB: 160 MB × $40/TB = $0.006 per query

Optimization:
- Cluster by date → Improve pruning to 995/1000 → $0.002 per query
- 3x cost reduction!
```

### Materialized Views for Cost Reduction

```sql
-- Expensive query (runs 1000x/day)
SELECT 
    date,
    product_id,
    SUM(amount) as total_sales,
    COUNT(*) as num_orders
FROM sales
WHERE date >= '2023-01-01'
GROUP BY date, product_id;

Cost per query: 1 TB scanned × $5/TB = $5
Daily cost: $5 × 1000 = $5,000

-- Create materialized view
CREATE MATERIALIZED VIEW sales_summary AS
SELECT 
    date,
    product_id,
    SUM(amount) as total_sales,
    COUNT(*) as num_orders
FROM sales
WHERE date >= '2023-01-01'
GROUP BY date, product_id;

Cost per query: 100 MB scanned × $5/TB = $0.0005
Daily cost: $0.0005 × 1000 = $0.50

Savings: $5,000 - $0.50 = $4,999.50/day = $1.8M/year!

Maintenance cost:
- Refresh nightly: 10 GB incremental × $5/TB = $0.05/day = $18/year
- Net savings: $1.8M - $18 = $1,799,982/year
```

---

## 🏆 Real-World Case Studies

### Case Study 1: Uber's Lakehouse (100 PB)

**Challenge:**
- 100 PB data warehouse (Hadoop/Hive)
- Slow queries (minutes to hours)
- High cost ($10M/year infrastructure)

**Solution (Migrated to Snowflake/Databricks):**
1. **Partitioning Strategy:**
   - City + Date partitioning (top 2 filters)
   - Clustering by trip_id, driver_id

2. **Tiered Storage:**
   - Hot data (last 7 days): Snowflake
   - Warm data (8-90 days): S3 with Spectrum
   - Cold data (90+ days): S3 Glacier

3. **Materialized Views:**
   - 50 critical aggregations pre-computed
   - Reduced 80% of query compute

**Results:**
- Query latency: 10 min → 10 sec (60x faster)
- Cost: $10M → $3M/year (70% reduction)
- Developer productivity: 5x increase

---

### Case Study 2: Netflix's Data Warehouse (10 PB)

**Architecture:**
- **Redshift:** Real-time analytics (last 30 days)
- **S3 + Presto:** Historical data (30+ days)
- **BigQuery:** Ad-hoc exploration

**Optimizations:**
1. **Distribution Keys:**
   - user_id for user_events (co-locate user data)
   - title_id for viewing_data (co-locate title data)

2. **Sort Keys:**
   - COMPOUND SORTKEY (date, country) for time-series queries
   - 95% zone map pruning efficiency

3. **Concurrency Scaling:**
   - Auto-scale for peak hours (US evening)
   - Scale down during off-peak (3 AM)

4. **Result Caching:**
   - Cache frequent queries (top 100 dashboards)
   - 80% cache hit rate → 5x cost reduction

**Results:**
- Support 10,000 analysts
- <1 sec p95 latency for dashboards
- $2M/year savings via caching

---

## 📊 Performance Tuning Checklist

### Snowflake Tuning

```sql
-- 1. Check clustering quality
SELECT SYSTEM$CLUSTERING_INFORMATION('table_name', '(cluster_key)');

-- 2. Analyze query profile
SELECT * FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE QUERY_ID = 'xxx'
ORDER BY BYTES_SCANNED DESC;

-- 3. Identify expensive queries
SELECT 
    QUERY_TEXT,
    TOTAL_ELAPSED_TIME,
    BYTES_SCANNED,
    CREDITS_USED
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE START_TIME >= DATEADD(day, -7, CURRENT_TIMESTAMP())
ORDER BY CREDITS_USED DESC
LIMIT 10;

-- 4. Optimize warehouse size
-- Start small (X-Small), scale up if queued
ALTER WAREHOUSE my_wh SET WAREHOUSE_SIZE = 'LARGE';

-- 5. Enable result caching
ALTER SESSION SET USE_CACHED_RESULT = TRUE;
```

### Redshift Tuning

```sql
-- 1. Check table design
SELECT 
    "schema",
    "table",
    diststyle,
    sortkey1
FROM SVV_TABLE_INFO
ORDER BY size DESC;

-- 2. Identify skewed distributions
SELECT 
    slice,
    COUNT(*) as rows
FROM STV_BLOCKLIST
WHERE tbl = (SELECT oid FROM pg_class WHERE relname = 'table_name')
GROUP BY slice
ORDER BY rows DESC;

-- 3. Analyze query execution
EXPLAIN SELECT * FROM sales WHERE date = '2023-01-01';

-- 4. Vacuum and analyze
VACUUM FULL table_name;
ANALYZE table_name;

-- 5. Monitor queue times
SELECT 
    query,
    queue_time,
    exec_time,
    queue_time::float / (queue_time + exec_time) as queue_pct
FROM STL_QUERY
WHERE userid > 1
ORDER BY queue_time DESC;
```

---

## 🎯 Interview Questions (Expert Level)

### Question 1: Design a Multi-PB Data Warehouse

**Scenario:** Design a data warehouse for a global e-commerce company:
- 10 billion transactions/day
- 100 PB historical data
- 10,000 analysts
- <1 sec p95 latency for dashboards

**Expected Answer:**

**Architecture:**
```
Tiered Storage:
1. Hot Tier (last 7 days, 1 PB):
   - Snowflake/BigQuery
   - High-performance SSD
   - Clustered by (country, date, product_id)

2. Warm Tier (8-90 days, 10 PB):
   - S3 Parquet with Redshift Spectrum/BigQuery BI Engine
   - Query via external tables

3. Cold Tier (90+ days, 89 PB):
   - S3 Glacier
   - Load to hot tier on-demand

Partitioning:
- Physical: Hive-style date partitioning (s3://bucket/year=2023/month=01/day=01/)
- Clustering: (country, product_category) for multi-dimensional pruning

Materialized Views:
- Top 100 dashboards pre-aggregated
- Refresh every 15 minutes (incremental)

Optimization:
- Result caching (80% hit rate)
- Concurrency scaling (peak hours)
- Query result compression (Brotli)

Cost: ~$500K/year (vs $5M without optimization)
```

---

### Question 2: Debug Slow Query Performance

**Scenario:** Query runs in 10 minutes, SLA is 10 seconds.

```sql
SELECT 
    u.country,
    COUNT(*) as num_users,
    SUM(o.amount) as total_sales
FROM users u
JOIN orders o ON u.user_id = o.user_id
WHERE o.date >= '2023-01-01'
GROUP BY u.country;
```

**Expected Answer:**

**Step 1: Analyze Execution Plan**
```
EXPLAIN output:
1. Seq Scan on orders (10 billion rows) ← Problem!
2. Hash Join with users
3. Aggregate
```

**Step 2: Check Statistics**
```sql
SELECT 
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE tablename = 'orders';

-- n_distinct for date: 1000 (last 3 years)
-- Predicate: date >= '2023-01-01' (last year)
-- Selectivity: 1/3 (33% of data)
```

**Step 3: Identify Issues**
1. **No partition pruning**: Orders table not partitioned by date
2. **Poor join distribution**: user_id not distribution key
3. **Missing stats**: Stats outdated (6 months old)

**Step 4: Fixes**
```sql
-- 1. Partition table by date
CREATE TABLE orders_partitioned (
    order_id BIGINT,
    user_id BIGINT,
    amount DECIMAL,
    date DATE
)
PARTITION BY RANGE (date);

-- 2. Set distribution key
ALTER TABLE orders_partitioned
DISTSTYLE KEY
DISTKEY (user_id);

-- 3. Refresh statistics
ANALYZE orders_partitioned;

-- 4. Create materialized view
CREATE MATERIALIZED VIEW sales_by_country AS
SELECT 
    u.country,
    DATE_TRUNC('day', o.date) as date,
    COUNT(*) as num_users,
    SUM(o.amount) as total_sales
FROM users u
JOIN orders o ON u.user_id = o.user_id
WHERE o.date >= '2023-01-01'
GROUP BY u.country, DATE_TRUNC('day', o.date);

-- 5. Query materialized view
SELECT country, SUM(total_sales)
FROM sales_by_country
WHERE date >= '2023-01-01'
GROUP BY country;
```

**Result:**
- 10 minutes → 2 seconds (300x faster!)
- Data scanned: 10 GB → 100 MB (100x reduction)

---

## 🎓 Summary: Expert-Level Mastery

By completing this track, you should be able to:

- ✅ Design Snowflake micro-partitions with optimal clustering
- ✅ Choose correct Redshift distribution/sort keys
- ✅ Implement cost-based query optimization
- ✅ Debug slow queries using execution plans
- ✅ Design multi-PB data warehouses
- ✅ Optimize costs via materialized views, caching, tiering
- ✅ Understand trade-offs: Snowflake vs Redshift vs BigQuery
- ✅ Pass Principal Engineer/Architect interviews

**Next Steps:**
- Read WHITEPAPERS.md (Dremel, C-Store, columnar research)
- Build hands-on project (multi-TB warehouse with partitioning + clustering)
- Practice FAANG interview questions

---

**End of EXPERT Track** | [Next: WHITEPAPERS.md →](WHITEPAPERS.md) | [Back: INTERMEDIATE.md](INTERMEDIATE.md)
