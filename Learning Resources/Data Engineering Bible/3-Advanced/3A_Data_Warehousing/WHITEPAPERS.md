# Week 6-7: Data Warehousing & Columnar Storage — WHITEPAPERS

*"The Dremel paper (2010) revolutionized data warehousing. Every modern columnar system traces back to these foundational papers."* — Research Perspective

---

## 📋 Table of Contents

1. [Dremel: Interactive Analysis of Web-Scale Datasets (Google, 2010)](#dremel-2010)
2. [C-Store: A Column-oriented DBMS (MIT, 2005)](#c-store-2005)
3. [MonetDB/X100: Hyper-Pipelining Query Execution (CWI, 2005)](#monetdb-2005)
4. [Parquet: Columnar Storage for Hadoop (2013)](#parquet-2013)
5. [The Snowflake Elastic Data Warehouse (2016)](#snowflake-2016)

---

<a name="dremel-2010"></a>
## 📄 Paper 1: Dremel: Interactive Analysis of Web-Scale Datasets

**Authors:** Sergey Melnik, Andrey Gubarev, Jing Jing Long, Geoffrey Romer, Shiva Shivakumar, Matt Tolton, Theo Vassilakis (Google)  
**Published:** VLDB 2010  
**Citations:** 3,000+  
**Impact:** Foundation for BigQuery, Parquet, Apache Drill

---

### 🎯 Abstract Summary

Dremel is Google's scalable, interactive ad-hoc query system for read-only nested data. It processes **trillions of rows** in seconds using:
1. **Columnar storage** for nested data (repetition/definition levels)
2. **Tree architecture** for parallel query execution
3. **In-situ analysis** (query data where it lives, no ETL)

**Key Innovation:** Encoding nested/repeated fields in columnar format while preserving structure.

---

### 🏗️ 1. Motivation & Background

#### Google's Data Problem (2010)

```
Google's data repositories (2010):
┌─────────────────────────────────────────────────────────┐
│ Bigtable: Petabytes of structured data                 │
│ - Web crawl data                                        │
│ - User logs                                             │
│ - Application data                                      │
├─────────────────────────────────────────────────────────┤
│ Storage Format: Protocol Buffers (nested data)         │
│ - Repeated fields (arrays)                              │
│ - Nested messages (structs)                             │
│ - Optional fields (nulls)                               │
└─────────────────────────────────────────────────────────┘

Challenge:
- MapReduce: Too slow for interactive queries (minutes to hours)
- Traditional RDBMS: Can't handle nested data, petabyte scale
- Goal: Sub-second queries on trillion-row tables
```

#### Design Goals

```
1. Scalability:
   - Handle petabytes of data
   - Thousands of nodes
   - Trillion-row tables

2. Performance:
   - Interactive latency (<10 seconds p90)
   - Scan billions of rows/second

3. Flexibility:
   - Schema evolution (add/remove fields)
   - Nested data support (Protocol Buffers, JSON)
   - In-situ analysis (no data movement)

4. Fault Tolerance:
   - Handle node failures mid-query
   - No query failures due to single node crashes
```

---

### 🗂️ 2. Nested Columnar Storage

#### The Problem: Storing Nested Data in Columns

```protobuf
// Protocol Buffer schema
message Document {
  required int64 DocId;
  optional group Links {
    repeated int64 Backward;
    repeated int64 Forward;
  }
  repeated group Name {
    repeated group Language {
      required string Code;
      optional string Country;
    }
    optional string Url;
  }
}
```

**Sample Data:**
```
Document 1:
  DocId: 10
  Links:
    Backward: [20, 40, 60]
    Forward: [80]
  Name:
    - Language:
        - Code: "en-us", Country: "us"
        - Code: "en"
      Url: "http://A"
    - Language:
        - Code: "en-gb", Country: "gb"
      Url: "http://B"

Document 2:
  DocId: 20
  Links:
    Backward: [10, 30]
    Forward: [10, 20, 30]
  Name:
    - Language:
        - Code: "en", Country: "us"
```

#### Dremel's Solution: Repetition & Definition Levels

**Column: Name.Language.Code**

```
┌────────┬────────────┬────────────┬──────────┐
│ Value  │ Repetition │ Definition │ Document │
│        │ Level (r)  │ Level (d)  │          │
├────────┼────────────┼────────────┼──────────┤
│ "en-us"│ 0          │ 3          │ Doc 1    │  ← r=0: New document
│ "en"   │ 2          │ 2          │ Doc 1    │  ← r=2: Repeated Language in same Name
│ "en-gb"│ 1          │ 3          │ Doc 1    │  ← r=1: Repeated Name in same Document
│ "en"   │ 0          │ 3          │ Doc 2    │  ← r=0: New document
└────────┴────────────┴────────────┴──────────┘
```

**Repetition Level (r):**
- 0: Value starts new record (new Document)
- 1: Value repeats at "Name" level (new Name in same Document)
- 2: Value repeats at "Language" level (new Language in same Name)

**Definition Level (d):**
- 0: DocId level (all ancestors null)
- 1: Name level defined
- 2: Language level defined (but Code might be null)
- 3: Code level defined (value present)

**Mathematical Formalization:**

```
For a field f at depth D in schema:
- r ∈ [0, D]: Indicates which ancestor repeated
- d ∈ [0, D]: Indicates deepest defined ancestor

Algorithm to compute r and d:
def compute_levels(current_path, previous_path):
    r = 0
    d = 0
    
    # Find first repeating ancestor
    for i, (curr, prev) in enumerate(zip(current_path, previous_path)):
        if curr.repeated and curr.index != prev.index:
            r = i + 1
            break
    
    # Find deepest defined ancestor
    for i, field in enumerate(current_path):
        if field.defined:
            d = i + 1
    
    return r, d
```

---

### 🚀 3. Query Execution Architecture

#### Tree-Based Serving Architecture

```
┌────────────────────────────────────────────────────────┐
│                  Root Server                           │
│  - Receives query from client                         │
│  - Rewrites query (optimization)                      │
│  - Distributes to intermediate servers                │
│  - Aggregates final results                           │
└─────────────────┬──────────────────────────────────────┘
                  │
        ┌─────────┴─────────┬──────────────┐
        ▼                   ▼              ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ Intermediate     │ │ Intermediate     │ │ Intermediate     │
│ Server 1         │ │ Server 2         │ │ Server 3         │
│ - Shuffles data  │ │ - Partial agg    │ │ - Partial agg    │
│ - Sorts/joins    │ │ - Filters        │ │ - Filters        │
└────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
         │                    │                    │
    ┌────┴─────┬─────┬────────┴────┬─────┬─────────┴────┐
    ▼          ▼     ▼             ▼     ▼              ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ Leaf   │ │ Leaf   │ │ Leaf   │ │ Leaf   │ │ Leaf   │ │ Leaf   │
│ Server │ │ Server │ │ Server │ │ Server │ │ Server │ │ Server │
│ 1      │ │ 2      │ │ 3      │ │ 4      │ │ 5      │ │ 6      │
│        │ │        │ │        │ │        │ │        │ │        │
│ Scan   │ │ Scan   │ │ Scan   │ │ Scan   │ │ Scan   │ │ Scan   │
│ tablets│ │ tablets│ │ tablets│ │ tablets│ │ tablets│ │ tablets│
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘
```

**Query Flow:**

```sql
Query: SELECT COUNT(*) FROM Documents WHERE DocId > 100;

Step 1: Root Server
- Parse query
- Rewrite: Push filters down to leaf servers
- Distribute to 3 intermediate servers

Step 2: Intermediate Servers
- Each coordinates 2 leaf servers
- Send query to leaf servers

Step 3: Leaf Servers (Parallel Scan)
- Server 1: Scan tablets 0-1000 → COUNT=500
- Server 2: Scan tablets 1001-2000 → COUNT=300
- Server 3: Scan tablets 2001-3000 → COUNT=200
- Server 4: Scan tablets 3001-4000 → COUNT=100
- Server 5: Scan tablets 4001-5000 → COUNT=400
- Server 6: Scan tablets 5001-6000 → COUNT=150

Step 4: Intermediate Servers (Partial Aggregation)
- Intermediate 1: 500 + 300 = 800
- Intermediate 2: 200 + 100 = 300
- Intermediate 3: 400 + 150 = 550

Step 5: Root Server (Final Aggregation)
- 800 + 300 + 550 = 1650
- Return to client
```

**Scalability:**

```
Performance Model:
- n = number of leaf servers
- m = number of intermediate servers
- T = total data size
- p = parallelism factor

Scan time: O(T / n)  ← Linear speedup with more leaf servers
Aggregation time: O(log m)  ← Logarithmic tree depth
Total time: O(T / n + log m)

Example:
- 1 PB data, 10,000 leaf servers
- Scan time: 1 PB / 10,000 = 100 GB per server
- At 1 GB/sec: 100 seconds scan time
- Tree depth: log₁₀₀(10,000) = 2 levels
- Aggregation time: 2 × 0.1 sec = 0.2 sec
- Total: 100.2 seconds

With caching + filtering: <10 seconds typical!
```

---

### 📊 4. Performance Evaluation (From Paper)

#### Experiment 1: Trillion-Row Table Scan

```
Setup:
- Table: ~3000 columns, 85 billion rows, 87 TB compressed
- Query: SELECT COUNT(*) FROM T1 WHERE A > threshold
- Cluster: 3000 leaf servers

Results:
┌──────────────────────────────────────────────────────┐
│ Execution Time │ Percentage of Data Scanned         │
├──────────────────────────────────────────────────────┤
│ 10 seconds     │ 0.1% (highly selective)            │
│ 30 seconds     │ 1%                                 │
│ 180 seconds    │ 10%                                │
│ 600 seconds    │ 100% (full table scan)             │
└──────────────────────────────────────────────────────┘

Key Insights:
- Columnar format enables fast scans (only read filtered columns)
- Metadata-based pruning (skip tablets with no matching values)
- Caching hot columns (80% cache hit rate in production)
```

#### Experiment 2: Nested Data Query

```
Query:
SELECT
  COUNT(Name.Language.Code)
FROM Documents
WHERE Name.Language.Code = 'en-us';

Execution:
- Column: Name.Language.Code (nested 3 levels deep)
- Total Documents: 100 billion
- Result: 2.3 billion matching rows
- Time: 20 seconds

Breakdown:
1. Scan Name.Language.Code column (120 GB compressed)
2. Decode repetition/definition levels
3. Filter Code = 'en-us'
4. Count results
5. Aggregate across leaf servers

Performance vs Alternatives:
- MapReduce: 30+ minutes (full row scan)
- Traditional RDBMS: Can't handle nested data
- Dremel: 20 seconds (columnar + parallel)
```

---

### 🔑 5. Key Takeaways from Dremel Paper

1. **Columnar storage for nested data** is possible and efficient (repetition/definition levels)
2. **Tree-based execution** enables massive parallelism (thousands of nodes)
3. **In-situ analysis** eliminates ETL overhead (query data where it lives)
4. **Interactive latency** on petabyte data is achievable (<10 sec p90)

**Quote from Paper:**

> "Dremel can execute many queries over such data that would ordinarily require a sequence of MapReduce jobs, but at a fraction of the execution time."

---

<a name="c-store-2005"></a>
## 📄 Paper 2: C-Store: A Column-oriented DBMS

**Authors:** Mike Stonebraker, Daniel Abadi, Adam Batkin, Xuedong Chen, Mitch Cherniack, Miguel Ferreira, Edmond Lau, Amerson Lin, Sam Madden, Elizabeth O'Neil, Pat O'Neil, Alex Rasin, Nga Tran, Stan Zdonik (MIT)  
**Published:** VLDB 2005  
**Citations:** 5,000+  
**Impact:** Foundation for Vertica, MonetDB, ClickHouse

---

### 🎯 Abstract Summary

C-Store is a read-optimized database system that stores data in **columns** rather than rows. Key innovations:
1. **Hybrid storage**: Writeable Store (row-oriented) + Read-optimized Store (column-oriented)
2. **Compression**: Aggressive column compression (10x better than row-stores)
3. **Multiple projections**: Pre-materialized sorted views for different query patterns

---

### 🏗️ 1. Architecture Overview

```
┌────────────────────────────────────────────────────────┐
│                  C-Store Architecture                  │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Writeable Store (WS) - Row-Oriented                  │
│  ├─ Recent inserts/updates (last 10 min)             │
│  ├─ Traditional row format (fast writes)              │
│  └─ In-memory + periodic disk flush                   │
│                                                        │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Read-optimized Store (RS) - Column-Oriented          │
│  ├─ Historical data (bulk of data)                    │
│  ├─ Columnar format (aggressive compression)          │
│  ├─ Multiple projections (different sort orders)      │
│  └─ On-disk (SSD/HDD)                                 │
│                                                        │
└────────────────────────────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────────────────────────┐
│  Tuple Mover (Background Process)                      │
│  - Batch move data: WS → RS                           │
│  - Sort, compress, create projections                 │
│  - Run every 10-60 minutes                            │
└────────────────────────────────────────────────────────┘
```

**Query Execution:**

```sql
Query: SELECT SUM(sales) FROM transactions WHERE date = '2023-01-01';

Step 1: Query Decomposition
- Scan WS (row-oriented)
- Scan RS (columnar)

Step 2: WS Scan
- Filter rows: date = '2023-01-01'
- Extract sales column
- Partial sum: 1000

Step 3: RS Scan
- Read date column (compressed)
- Filter using bitmap index
- Read sales column for matching rows
- Partial sum: 999000

Step 4: Merge Results
- Total: 1000 + 999000 = 1,000,000
```

---

### 🗜️ 2. Compression Techniques

#### Run-Length Encoding (RLE)

```
Column: status (sorted)
Values: [A, A, A, A, B, B, C, C, C, ...]

RLE Encoding:
[(A, 4), (B, 2), (C, 3), ...]

Storage:
- Original: 9 values × 1 byte = 9 bytes
- RLE: 3 tuples × 2 bytes = 6 bytes
- Compression: 1.5x

For highly sorted columns: 10-100x compression!
```

#### Bitmap Encoding

```
Column: country (low cardinality)
Values: [US, US, CA, UK, US, CA, ...]
Unique: [US, CA, UK]

Bitmap Encoding:
US: [1, 1, 0, 0, 1, 0, ...] ← Bitmap for US
CA: [0, 0, 1, 0, 0, 1, ...] ← Bitmap for CA
UK: [0, 0, 0, 1, 0, 0, ...] ← Bitmap for UK

Storage:
- Original: N × 2 bytes = 2N bytes
- Bitmap: 3 bitmaps × N bits = 3N/8 bytes
- Compression: 5.3x

For very low cardinality (<10 values): 10-50x compression!
```

#### Dictionary Encoding + Bit-Packing

```
Column: product_name
Values: ["Laptop", "Phone", "Laptop", "Tablet", ...]
Cardinality: 100 unique products

Dictionary:
0: "Laptop"
1: "Phone"
2: "Tablet"
...
99: "Monitor"

Encoded: [0, 1, 0, 2, ...]

Bit-Packing:
- 100 values → requires 7 bits (2^7 = 128)
- Original: N × 20 bytes = 20N bytes
- Encoded: N × 7 bits = 7N/8 bytes
- Compression: 22.8x
```

---

### 📈 3. Projections: Pre-Materialized Views

```sql
-- Base Table
CREATE TABLE sales (
    sale_id INT,
    date DATE,
    product_id INT,
    customer_id INT,
    amount DECIMAL
);

-- Projection 1: Sorted by date (for time-series queries)
CREATE PROJECTION sales_by_date AS
SELECT date, sale_id, amount
FROM sales
ORDER BY date;

-- Projection 2: Sorted by product_id (for product analytics)
CREATE PROJECTION sales_by_product AS
SELECT product_id, sale_id, amount
FROM sales
ORDER BY product_id;

-- Projection 3: Sorted by customer_id (for customer analytics)
CREATE PROJECTION sales_by_customer AS
SELECT customer_id, sale_id, amount
FROM sales
ORDER BY customer_id;
```

**Query Optimizer Selection:**

```sql
Query 1: SELECT SUM(amount) FROM sales WHERE date = '2023-01-01';
Optimizer: Use sales_by_date (already sorted by date!)
Cost: O(log N) binary search + O(k) scan

Query 2: SELECT SUM(amount) FROM sales WHERE product_id = 123;
Optimizer: Use sales_by_product (already sorted by product_id!)
Cost: O(log N) binary search + O(k) scan

Query 3: SELECT SUM(amount) FROM sales WHERE customer_id = 456;
Optimizer: Use sales_by_customer (already sorted by customer_id!)
Cost: O(log N) binary search + O(k) scan

Trade-off:
- Storage: 3x (3 projections)
- Write cost: 3x (update all projections)
- Query cost: 10-100x faster (optimal projection per query!)
```

---

### 📊 4. Performance Evaluation (From Paper)

```
Benchmark: TPC-H (Decision Support Benchmark)
Dataset: 100 GB
Queries: 22 analytical queries

Results:
┌────────────────────────────────────────────────────────┐
│ System     │ Total Query Time │ Speedup vs Row-Store │
├────────────────────────────────────────────────────────┤
│ Row-Store  │ 10,000 seconds   │ 1x (baseline)        │
│ C-Store    │ 300 seconds      │ 33x faster           │
└────────────────────────────────────────────────────────┘

Key Factors:
1. Columnar I/O: Read only needed columns (10x less data)
2. Compression: Aggressive encoding (5-10x compression)
3. Projections: Pre-sorted for common queries
4. Late materialization: Delay row reconstruction
```

---

<a name="monetdb-2005"></a>
## 📄 Paper 3: MonetDB/X100: Hyper-Pipelining Query Execution

**Authors:** Peter Boncz, Marcin Zukowski, Niels Nes (CWI Amsterdam)  
**Published:** CIDR 2005  
**Citations:** 2,000+  
**Impact:** Foundation for vectorized execution in DuckDB, ClickHouse, Snowflake

---

### 🎯 Key Innovation: Vectorized Execution

Traditional query engines process one tuple (row) at a time (**Volcano model**). MonetDB/X100 processes **vectors** (batches of ~1000 tuples) for CPU efficiency.

```
Volcano Model (Tuple-at-a-Time):
for each tuple in table:
    if filter(tuple):
        result.append(tuple)

Problems:
- Function call per tuple (overhead)
- Poor CPU cache utilization
- No SIMD vectorization

X100 Model (Vector-at-a-Time):
for each vector (1000 tuples) in table:
    filtered_vector = filter_vector(vector)  # SIMD!
    result.append(filtered_vector)

Benefits:
- Amortize function call overhead
- Better CPU cache locality
- SIMD instructions (4-8x speedup)
```

**Performance Comparison:**

```
Benchmark: TPC-H Query 1 (100 GB dataset)
┌────────────────────────────────────────────────────────┐
│ Execution Model   │ Time     │ CPU Efficiency         │
├────────────────────────────────────────────────────────┤
│ Tuple-at-a-time   │ 100 sec  │ 10% (90% overhead!)    │
│ Vector-at-a-time  │ 10 sec   │ 80% (20% overhead)     │
└────────────────────────────────────────────────────────┘

Result: 10x speedup with vectorization!
```

---

<a name="parquet-2013"></a>
## 📄 Paper 4: Parquet: Columnar Storage for Hadoop Ecosystem

**Authors:** Julien Le Dem, Nong Li (Twitter, Cloudera)  
**Published:** 2013 (White Paper)  
**Impact:** De facto standard for Hadoop, Spark, Presto, Athena

---

### 🎯 Design Goals

1. **Compatibility**: Work with any data processing framework (Hadoop, Spark, Hive)
2. **Nested data**: Support complex schemas (Avro, Thrift, Protocol Buffers)
3. **Compression**: Leverage column-specific encoding
4. **Performance**: Fast scans via predicate pushdown

---

### 🗂️ File Format

```
Parquet File Layout:
┌────────────────────────────────────────────────────────┐
│ Magic Number: PAR1 (4 bytes)                          │
├────────────────────────────────────────────────────────┤
│ Row Group 1 (128 MB default)                          │
│   ├─ Column Chunk: sale_id                            │
│   │  ├─ Page 1: Dictionary (keys: [101, 102, 103])   │
│   │  ├─ Page 2: Data (encoded: [0, 1, 0, 2, ...])    │
│   │  └─ Page 3: Data                                  │
│   ├─ Column Chunk: amount                             │
│   │  ├─ Page 1: Data (delta-encoded)                 │
│   │  └─ Page 2: Data                                  │
│   └─ ...                                               │
│ Row Group 2                                           │
│   └─ ...                                               │
├────────────────────────────────────────────────────────┤
│ Footer (metadata)                                      │
│   ├─ Schema                                            │
│   ├─ Row group metadata                               │
│   │  ├─ Location, compressed size, # rows             │
│   │  └─ Column metadata (min, max, null count)        │
│   └─ Version, created_by                              │
├────────────────────────────────────────────────────────┤
│ Footer Length (4 bytes)                                │
│ Magic Number: PAR1 (4 bytes)                          │
└────────────────────────────────────────────────────────┘
```

---

<a name="snowflake-2016"></a>
## 📄 Paper 5: The Snowflake Elastic Data Warehouse

**Authors:** Benoit Dageville, Thierry Cruanes, Marcin Zukowski, Vadim Antonov, Artin Avanes, Jon Bock, Jonathan Claybaugh, Daniel Engovatov, Martin Hentschel, Jiansheng Huang, Allison W. Lee, Ashish Motivala, Abdul Q. Munir, Steven Pelley, Peter Povinec, Greg Rahn, Spyridon Triantafyllis, Philipp Unterbrunner (Snowflake Computing)  
**Published:** SIGMOD 2016  
**Citations:** 1,500+  
**Impact:** Pioneered cloud-native data warehouse architecture

---

### 🎯 Key Innovations

1. **Multi-Cluster Shared Data Architecture**
   - Separate compute from storage
   - Elastic scaling (add/remove warehouses)
   - No data copying between warehouses

2. **Micro-Partitions**
   - Automatic 16 MB partitions
   - Min/max stats for all columns
   - Multi-dimensional pruning

3. **Time Travel & Cloning**
   - Query historical data (up to 90 days)
   - Zero-copy table cloning
   - Immutable storage + metadata snapshots

---

## 🎓 Summary: Key Papers & Contributions

| Paper | Year | Key Innovation | Impact |
|-------|------|---------------|--------|
| **C-Store** | 2005 | Columnar storage, projections, compression | Vertica, MonetDB |
| **MonetDB/X100** | 2005 | Vectorized execution | DuckDB, ClickHouse |
| **Dremel** | 2010 | Nested columnar storage, tree execution | BigQuery, Parquet |
| **Parquet** | 2013 | Open columnar format for Hadoop | Spark, Presto, Athena |
| **Snowflake** | 2016 | Cloud-native, multi-cluster shared data | Modern cloud warehouses |

**Reading Order:**
1. C-Store (foundation of columnar storage)
2. MonetDB/X100 (vectorized execution)
3. Dremel (nested data + scale)
4. Parquet (practical implementation)
5. Snowflake (cloud-native architecture)

---

**End of WHITEPAPERS** | [Next: README.md →](README.md) | [Back: EXPERT.md](EXPERT.md)
