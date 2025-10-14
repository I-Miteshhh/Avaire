# Week 6-7: Data Warehousing & Columnar Storage — INTERMEDIATE Track

*"Understanding Dremel's nested columnar format and BigQuery's execution engine separates good data engineers from great ones."* — Google Principal Engineer

---

## 🎯 Learning Outcomes

At the INTERMEDIATE level, you will master:

- **BigQuery/Dremel Architecture**: Query execution, shuffle, capacitor storage
- **Nested Data in Parquet**: Repetition/definition levels for complex schemas
- **Predicate Pushdown**: How query engines skip data at file/row group/page level
- **Partition Pruning**: Physical partitioning strategies (Hive-style, BigQuery)
- **Query Optimization**: Statistics, cost-based optimization, materialized views
- **Compression Deep Dive**: Encoding schemes (RLE, bit-packing, delta encoding)
- **Scan Performance**: I/O patterns, vectorized execution, late materialization

---

## 📚 Prerequisites

- ✅ Parquet/ORC file structure (BEGINNER.md)
- ✅ SQL fundamentals (joins, aggregations, window functions)
- ✅ Distributed systems basics (partitioning, replication)

---

## 🏗️ 1. BigQuery Architecture: The Complete Picture

BigQuery is Google's serverless data warehouse built on **Dremel** (2010 research paper).

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                      BigQuery Frontend                          │
│  (Query parsing, optimization, job scheduling)                  │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Dremel Query Engine                           │
│  ├─ Root Server (aggregates results)                           │
│  ├─ Intermediate Servers (shuffle, join)                       │
│  └─ Leaf Servers (scan Capacitor files)                        │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Colossus (Distributed Storage)                │
│  ├─ Capacitor files (columnar, compressed)                     │
│  ├─ Metadata (schema, statistics, partitions)                  │
│  └─ Replication factor: 3                                      │
└─────────────────────────────────────────────────────────────────┘
```

### Query Execution Flow

```
Step 1: Query Submission
User → Frontend: SELECT product_id, SUM(amount) FROM sales GROUP BY product_id

Step 2: Query Planning
Frontend:
- Parse SQL
- Analyze table metadata (schema, partitions, stats)
- Generate execution plan (DAG of operators)
- Estimate cost (bytes scanned, slots needed)

Step 3: Job Scheduling
Frontend → Borg (Google's cluster manager):
- Request worker slots (e.g., 2000 slots for large query)
- Allocate leaf/intermediate/root servers

Step 4: Execution
Root Server:
  ├─ Coordinate execution
  └─ Aggregate final results

Intermediate Servers (if joins/shuffles):
  ├─ Hash-based shuffle
  └─ Partial aggregations

Leaf Servers (parallel):
  ├─ Read Capacitor files from Colossus
  ├─ Apply filters (predicate pushdown)
  ├─ Project columns (column pruning)
  └─ Send data to intermediate/root

Step 5: Result Return
Root Server → Frontend → User
```

**Key Insight:** BigQuery separates **compute** (Dremel workers) from **storage** (Colossus), enabling:
- Elastic scaling (spin up 10,000 workers for one query)
- No cluster management
- Pay-per-query pricing

---

## 🗂️ 2. Nested Data in Columnar Formats

### The Problem: Representing Nested Structures

```
JSON data:
{
  "user_id": 123,
  "events": [
    {"type": "click", "timestamp": 1609459200},
    {"type": "purchase", "timestamp": 1609459300}
  ]
}

Challenge: How to store nested arrays in columnar format?
- Row-based: Easy (store JSON blob)
- Columnar: Complex (need to reconstruct nesting)
```

### Dremel's Solution: Repetition & Definition Levels

Parquet/Dremel use **repetition levels** and **definition levels** to encode nested data.

**Example Schema:**
```protobuf
message Document {
  required int64 user_id;
  repeated Event events {
    required string type;
    required int64 timestamp;
  }
}
```

**Sample Data:**
```
Document 1:
  user_id: 123
  events:
    - type: "click", timestamp: 1609459200
    - type: "purchase", timestamp: 1609459300

Document 2:
  user_id: 456
  events:
    - type: "view", timestamp: 1609459400
```

**Columnar Encoding:**

```
Column: events.type
┌───────────┬───────────────┬──────────────┬─────────────┐
│ Value     │ Repetition    │ Definition   │ Document    │
│           │ Level (RL)    │ Level (DL)   │             │
├───────────┼───────────────┼──────────────┼─────────────┤
│ "click"   │ 0             │ 2            │ Doc 1       │ ← First event in Doc 1
│ "purchase"│ 1             │ 2            │ Doc 1       │ ← Repeat event in Doc 1
│ "view"    │ 0             │ 2            │ Doc 2       │ ← First event in Doc 2
└───────────┴───────────────┴──────────────┴─────────────┘

Repetition Level (RL):
- 0: New record (start of new document)
- 1: Repeated field (another event in same document)

Definition Level (DL):
- 0: Field is null
- 1: Field's parent is null
- 2: Field is defined (has value)
```

**Reconstruction Algorithm:**

```python
def reconstruct_records(values, repetition_levels, definition_levels):
    records = []
    current_record = None
    
    for val, rl, dl in zip(values, repetition_levels, definition_levels):
        if rl == 0:  # New record
            if current_record:
                records.append(current_record)
            current_record = {"events": []}
        
        if dl == 2:  # Field defined
            current_record["events"].append({"type": val})
    
    if current_record:
        records.append(current_record)
    
    return records

# Example:
values = ["click", "purchase", "view"]
repetition_levels = [0, 1, 0]
definition_levels = [2, 2, 2]

result = reconstruct_records(values, repetition_levels, definition_levels)
# [
#   {"events": [{"type": "click"}, {"type": "purchase"}]},
#   {"events": [{"type": "view"}]}
# ]
```

**Why This Matters:**
- Columnar storage for nested data (JSON, Avro, Protobuf)
- Efficient scanning (read only needed nested fields)
- Used in Parquet, BigQuery, Snowflake

---

## 🔍 3. Predicate Pushdown: Multi-Level Filtering

Predicate pushdown skips data at **multiple levels** to minimize I/O.

### Level 1: Partition Pruning (File-Level)

```
Table: sales (partitioned by date)
Files:
├─ date=2023-01-01/
│  ├─ chunk-001.parquet
│  └─ chunk-002.parquet
├─ date=2023-01-02/
│  └─ chunk-003.parquet
└─ date=2023-01-03/
   └─ chunk-004.parquet

Query: SELECT * FROM sales WHERE date = '2023-01-02' AND amount > 1000

Step 1: Partition Pruning
- Read metadata (partition values)
- Skip: date=2023-01-01, date=2023-01-03
- Scan: date=2023-01-02 only (1 file vs 4 files = 75% reduction)
```

### Level 2: Row Group Pruning (Parquet Metadata)

```
File: chunk-003.parquet
Row Groups:
├─ Row Group 0: min(amount)=100, max(amount)=500   ← Skip! (max < 1000)
├─ Row Group 1: min(amount)=800, max(amount)=1500  ← Scan (max > 1000)
└─ Row Group 2: min(amount)=200, max(amount)=900   ← Skip! (max < 1000)

Result: Scan 1 row group instead of 3 (66% reduction)
```

### Level 3: Page Pruning (Column Chunk Statistics)

```
Row Group 1 → Column: amount
Pages:
├─ Page 0: min=800, max=950    ← Skip! (max < 1000)
├─ Page 1: min=1000, max=1200  ← Scan (min >= 1000)
└─ Page 2: min=1100, max=1500  ← Scan (min >= 1000)

Result: Scan 2 pages instead of 3 (33% reduction)
```

### Level 4: Row-Level Filtering (After Decompression)

```
Page 1 values: [1000, 1050, 1020, 980, 1100, ...]
Filter: amount > 1000
Result: [1050, 1020, 1100, ...] (remove 980)
```

**Total Reduction:**
- Partition pruning: 75% (4 files → 1 file)
- Row group pruning: 66% (3 row groups → 1)
- Page pruning: 33% (3 pages → 2)
- Combined: ~96% data skipped!

---

## 🗂️ 4. Partitioning Strategies

### Hive-Style Partitioning

```
sales/
├── year=2023/
│   ├── month=01/
│   │   ├── day=01/
│   │   │   ├── part-00000.parquet
│   │   │   └── part-00001.parquet
│   │   └── day=02/
│   │       └── part-00000.parquet
│   └── month=02/
│       └── day=01/
│           └── part-00000.parquet
└── year=2024/
    └── month=01/
        └── day=01/
            └── part-00000.parquet

Pros:
- Easy to understand (filesystem paths)
- Works with Spark, Hive, Presto, Athena
- Efficient time-range queries

Cons:
- Many small files (metadata overhead)
- Slow partition discovery (millions of files)
```

### BigQuery Partitioning (Internal)

```
Table: sales (partitioned by date, clustered by product_id)

Internal Structure (Capacitor files):
├─ Partition: 2023-01-01
│  ├─ Cluster 0 (product_id: 1-1000)
│  ├─ Cluster 1 (product_id: 1001-2000)
│  └─ Cluster 2 (product_id: 2001-3000)
├─ Partition: 2023-01-02
│  ├─ Cluster 0 (product_id: 1-1000)
│  └─ Cluster 1 (product_id: 1001-2000)
└── ...

Query: SELECT * FROM sales 
       WHERE date = '2023-01-01' AND product_id = 1500

Optimizations:
1. Partition pruning: Only scan 2023-01-01 (skip other dates)
2. Cluster pruning: Only scan Cluster 1 (product_id 1001-2000)
3. Result: Scan 1 cluster instead of 6 (83% reduction)
```

**Partitioning Best Practices:**
- Partition by time (date, timestamp) for time-series data
- Cluster by frequently filtered columns (user_id, product_id)
- Avoid over-partitioning (< 1GB per partition is wasteful)

---

## 🚀 5. Query Optimization Techniques

### Statistics-Based Optimization

```
Table: sales (1 billion rows)
Columns:
- user_id (cardinality: 10 million)
- product_id (cardinality: 100,000)

Query: SELECT * FROM sales WHERE user_id = 123 AND product_id = 456

Cost Estimation (without stats):
- Scan 1 billion rows
- Cost: 1 billion I/O operations

Cost Estimation (with stats):
- Selectivity(user_id = 123) = 1/10M = 0.0001%
- Selectivity(product_id = 456) = 1/100K = 0.001%
- Combined selectivity = 0.0001% × 0.001% = 0.0000001%
- Estimated rows: 1B × 0.0000001% = 100 rows
- Cost: 100 I/O operations (much cheaper!)

Optimizer Decision:
- Use index on user_id (if exists)
- Or: Scan full table with predicate pushdown
```

### Materialized Views

```
Base Table: sales (100 billion rows, 10 TB)

Query (expensive):
SELECT date, product_id, SUM(amount) as total_sales
FROM sales
GROUP BY date, product_id

Problem: Aggregates 100B rows every query!

Solution: Materialized View
CREATE MATERIALIZED VIEW sales_summary AS
SELECT date, product_id, SUM(amount) as total_sales
FROM sales
GROUP BY date, product_id;

Result: Pre-computed aggregates (1 million rows, 10 GB)
Query time: 10 seconds → 0.1 seconds (100x faster!)

Maintenance:
- Incremental refresh (only new data since last refresh)
- BigQuery: Auto-refresh when base table updated
- Snowflake: Manual refresh (ALTER MATERIALIZED VIEW REFRESH)
```

---

## 🔬 6. Compression & Encoding Deep Dive

### Dictionary Encoding

```
Column: product_name
Values: ["Laptop", "Phone", "Laptop", "Tablet", "Phone", "Laptop", ...]

Dictionary: ["Laptop", "Phone", "Tablet"]
Encoded: [0, 1, 0, 2, 1, 0, ...]

Storage:
- Dictionary: 3 strings (~60 bytes)
- Encoded: Array of 2-bit integers (4 values per byte)
- Original: N strings × 20 bytes = 20N bytes
- Compressed: 60 bytes + N/4 bytes ≈ N/4 bytes
- Compression ratio: 80x for high-cardinality repeating data!

When to use:
- Low cardinality columns (< 1000 unique values)
- High repetition (same values occur many times)
```

### Run-Length Encoding (RLE)

```
Column: status
Values: ["ACTIVE", "ACTIVE", "ACTIVE", "ACTIVE", "INACTIVE", "INACTIVE", ...]

RLE: [(ACTIVE, 4), (INACTIVE, 2), ...]

Storage:
- Original: 6 strings × 10 bytes = 60 bytes
- RLE: 2 tuples × 12 bytes = 24 bytes
- Compression ratio: 2.5x

When to use:
- Sorted columns (values grouped together)
- Boolean flags (long runs of true/false)
```

### Delta Encoding

```
Column: timestamp (sorted)
Values: [1609459200, 1609459201, 1609459202, 1609459210, ...]

Delta encoding:
- Base: 1609459200
- Deltas: [0, 1, 2, 10, ...]

Storage:
- Original: 4 × 8 bytes = 32 bytes (64-bit integers)
- Delta: 8 bytes (base) + 4 × 1 byte (deltas) = 12 bytes
- Compression ratio: 2.7x

When to use:
- Monotonically increasing columns (timestamps, IDs)
- Small deltas (< 256 for 1-byte encoding)
```

### Bit-Packing

```
Column: age (0-127)
Values: [25, 30, 45, 62, 18, ...]

Bit-packing:
- Max value: 127 → requires 7 bits (2^7 = 128)
- Original: 5 × 8 bits = 40 bits
- Packed: 5 × 7 bits = 35 bits
- Compression ratio: 1.14x

When to use:
- Bounded integer columns (small range)
- Combined with delta encoding for better compression
```

---

## 📊 7. Scan Performance: Vectorized Execution

### Row-at-a-Time Execution (Traditional)

```java
// Slow: Process one row at a time
for (Row row : table) {
    if (row.amount > 1000) {
        sum += row.amount;
    }
}

Problems:
- Function call overhead per row
- Poor CPU cache utilization
- Branch mispredictions
```

### Vectorized Execution (Modern)

```java
// Fast: Process batches of 1024 rows
for (Batch batch : table.batches(1024)) {
    // SIMD: Single Instruction Multiple Data
    int[] amounts = batch.getColumn("amount");
    boolean[] filter = vectorGreaterThan(amounts, 1000);  // SIMD!
    int batchSum = vectorSum(amounts, filter);  // SIMD!
    sum += batchSum;
}

Benefits:
- Amortize function call overhead
- Better CPU cache locality
- SIMD instructions (process 4-8 values per instruction)
```

**Performance Comparison:**
- Row-at-a-time: 100 MB/sec per core
- Vectorized: 1 GB/sec per core (10x faster!)

**Used In:**
- Apache Arrow (in-memory columnar format)
- DuckDB (embedded analytics database)
- BigQuery, Snowflake, Redshift

---

## 🛠️ 8. Hands-On: Advanced Parquet Usage

### Writing Parquet with Custom Settings

```python
import pyarrow as pa
import pyarrow.parquet as pq

# Create schema with nested data
schema = pa.schema([
    pa.field('user_id', pa.int64()),
    pa.field('events', pa.list_(pa.struct([
        pa.field('type', pa.string()),
        pa.field('timestamp', pa.int64())
    ])))
])

# Sample data
data = {
    'user_id': [123, 456],
    'events': [
        [{'type': 'click', 'timestamp': 1609459200},
         {'type': 'purchase', 'timestamp': 1609459300}],
        [{'type': 'view', 'timestamp': 1609459400}]
    ]
}

table = pa.Table.from_pydict(data, schema=schema)

# Write with custom settings
pq.write_table(
    table,
    'events.parquet',
    compression='zstd',              # Best compression
    compression_level=9,             # Max compression
    row_group_size=1000000,          # 1M rows per row group
    use_dictionary=True,             # Enable dictionary encoding
    write_statistics=True,           # Write min/max stats
    data_page_size=1024*1024,        # 1 MB pages
)
```

### Reading Parquet with Filters

```python
import pyarrow.parquet as pq

# Read with filter (predicate pushdown)
table = pq.read_table(
    'events.parquet',
    columns=['user_id', 'events'],   # Column pruning
    filters=[                         # Predicate pushdown
        ('user_id', '=', 123)
    ]
)

# Inspect metadata
metadata = pq.read_metadata('events.parquet')
print(f"Row groups: {metadata.num_row_groups}")
print(f"Rows: {metadata.num_rows}")

for i in range(metadata.num_row_groups):
    rg = metadata.row_group(i)
    print(f"\nRow Group {i}:")
    for j in range(rg.num_columns):
        col = rg.column(j)
        print(f"  Column {col.path_in_schema}:")
        print(f"    Min: {col.statistics.min}")
        print(f"    Max: {col.statistics.max}")
        print(f"    Null count: {col.statistics.null_count}")
```

---

## 🏆 Interview Questions (Intermediate Level)

### Question 1: Explain Predicate Pushdown in Detail

**Expected Answer:**
Predicate pushdown optimizes queries by pushing filters down to the storage layer, minimizing data read:

1. **Partition Pruning**: Skip entire partitions based on partition key
2. **Row Group Pruning**: Skip row groups using min/max statistics
3. **Page Pruning**: Skip pages within row groups using stats
4. **Row Filtering**: Filter individual rows after decompression

Example: Query with `WHERE date = '2023-01-01' AND amount > 1000`:
- Skip 99% of partitions (other dates)
- Skip 80% of row groups (max(amount) < 1000)
- Skip 50% of pages within selected row groups
- Final filtering removes remaining rows

Result: Scan 0.1% of data instead of 100%!

### Question 2: How Does BigQuery Handle Nested Data?

**Expected Answer:**
BigQuery (Dremel) uses **repetition levels** and **definition levels** to encode nested data in columnar format:

- **Repetition Level**: Indicates at which level a value repeats (0 = new record, 1+ = repeated field)
- **Definition Level**: Indicates how deeply a value is defined (handles nulls in nested structures)

This allows:
- Columnar storage for nested JSON/Protobuf
- Efficient scanning (read only needed nested fields)
- Full reconstruction of original nested structure

Example: Querying `events[0].type` only scans the `type` column, skipping all other nested fields.

### Question 3: Compare Parquet vs ORC

**Expected Answer:**

| Feature | Parquet | ORC |
|---------|---------|-----|
| **File Structure** | Row groups → Column chunks → Pages | Stripes → Columns → Indexes |
| **Default Row Group Size** | 128 MB | 64 MB |
| **Compression** | Snappy (default), Gzip, Zstd | Zlib (default), Snappy, LZ4 |
| **Indexes** | Min/max stats | Min/max + Bloom filters |
| **Nested Data** | Repetition/definition levels | Same as Parquet |
| **Ecosystem** | Spark, BigQuery, Athena, Snowflake | Hive, Presto, Trino |
| **Performance** | Faster for wide tables (many columns) | Faster for selective scans (bloom filters) |

**When to use Parquet**: General-purpose, cross-platform compatibility
**When to use ORC**: Hive/Presto workloads, need bloom filters

---

## 🎓 Summary Checklist

At the end of INTERMEDIATE track, you should be able to:

- [ ] Explain BigQuery/Dremel architecture (root/intermediate/leaf servers)
- [ ] Describe repetition/definition levels for nested data
- [ ] Implement multi-level predicate pushdown
- [ ] Design partitioning strategies (Hive-style vs BigQuery)
- [ ] Use statistics for query optimization
- [ ] Apply compression/encoding techniques (dictionary, RLE, delta, bit-packing)
- [ ] Understand vectorized execution benefits
- [ ] Create advanced Parquet files with custom settings
- [ ] Answer intermediate-level interview questions

**Next Steps:**
- **EXPERT Track**: Snowflake architecture, Redshift internals, cost-based optimization, query execution deep dive
- **Hands-On**: Build a multi-TB data warehouse with partitioning, compression, and materialized views

---

**End of INTERMEDIATE Track** | [Next: EXPERT.md →](EXPERT.md) | [Back: BEGINNER.md](BEGINNER.md)
