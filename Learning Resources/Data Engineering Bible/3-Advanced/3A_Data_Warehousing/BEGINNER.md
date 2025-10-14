# Week 6-7: Data Warehousing & Columnar Storage — BEGINNER Track

*"Columnar storage is the backbone of every modern data warehouse. Understanding Parquet, ORC, and compression is non-negotiable for any data engineer."* — Principal Architect Insight

---

## 🎯 Learning Outcomes

By the end of this track, you will:
- Understand the evolution from row-based to columnar storage
- Master Parquet and ORC file formats (structure, encoding, compression)
- Grasp the basics of data warehouse architecture (fact/dimension tables, star/snowflake schemas)
- Learn how columnar storage enables fast analytics (predicate pushdown, partition pruning)
- Get hands-on with creating, reading, and optimizing columnar files

---

## 🏗️ 1. Data Warehouse Architecture: The Foundation

### What is a Data Warehouse?

A **data warehouse** is a centralized repository for integrated, historical, and analytical data. It powers BI dashboards, reporting, and advanced analytics.

**Key Concepts:**
- **Fact Table:** Stores quantitative metrics (sales, clicks, revenue)
- **Dimension Table:** Stores descriptive attributes (date, product, customer)
- **Star Schema:** Fact table at center, surrounded by dimension tables
- **Snowflake Schema:** Dimensions normalized into sub-dimensions

**Example:**
```
Fact Table: sales
| sale_id | date_id | product_id | customer_id | amount |

Dimension Table: date
| date_id | year | month | day |

Dimension Table: product
| product_id | name | category |

Dimension Table: customer
| customer_id | name | region |
```

---

## 🗃️ 2. Row-Based vs Columnar Storage

### Row-Based (Traditional RDBMS)

```
Row-oriented storage (PostgreSQL, MySQL):
┌────────────────────────────────────────────┐
│ Row 1: [sale_id, date_id, product_id, ...] │
│ Row 2: [sale_id, date_id, product_id, ...] │
│ ...                                        │
└────────────────────────────────────────────┘

Pros:
- Fast for OLTP (insert/update/delete)
- Good for transactional workloads

Cons:
- Slow for analytics (scanning millions of rows for a few columns)
- Poor compression (mixed data types)
```

### Columnar Storage (Modern Warehouses)

```
Column-oriented storage (Parquet, ORC, BigQuery, Redshift):
┌────────────────────────────────────────────┐
│ sale_id: [101, 102, 103, ...]              │
│ date_id: [20231001, 20231002, ...]         │
│ product_id: [501, 502, 503, ...]           │
│ ...                                        │
└────────────────────────────────────────────┘

Pros:
- Fast for analytics (scan only needed columns)
- High compression (similar data types)
- Enables predicate pushdown, partition pruning

Cons:
- Slower for OLTP (row updates)
- More complex file format
```

---

## 📦 3. Parquet File Format: Internals

### Structure

Parquet is an open-source columnar storage format optimized for analytical workloads.

**File Layout:**
```
┌────────────────────────────────────────────┐
│ Parquet File                              │
├────────────────────────────────────────────┤
│ Row Group 1                               │
│   ├─ Column Chunk: sale_id                 │
│   ├─ Column Chunk: date_id                 │
│   ├─ Column Chunk: product_id              │
│   └─ ...                                   │
│ Row Group 2                               │
│   ├─ Column Chunk: sale_id                 │
│   ├─ Column Chunk: date_id                 │
│   ├─ Column Chunk: product_id              │
│   └─ ...                                   │
│ ...                                        │
├────────────────────────────────────────────┤
│ Footer (metadata, schema, statistics)      │
└────────────────────────────────────────────┘
```

**Key Concepts:**
- **Row Group:** Horizontal partition of data (default 128MB)
- **Column Chunk:** All values for a column in a row group
- **Page:** Subdivision of column chunk (data, dictionary, index)
- **Footer:** Contains schema, min/max stats, encoding info

### Encoding & Compression

Parquet supports multiple encodings and compression algorithms:
- **Encodings:** Plain, Dictionary, Delta, Bit Packing, RLE
- **Compression:** Snappy (default), Gzip, Brotli, LZ4, Zstd

**Example:**
```
Column: product_id
Values: [501, 501, 502, 503, 501, 502, ...]
Dictionary Encoding:
- Dictionary: [501, 502, 503]
- Encoded: [0, 0, 1, 2, 0, 1, ...]

Compression:
- Snappy: Fast, moderate compression
- Gzip: Slower, higher compression
- Zstd: Best trade-off (modern warehouses)
```

### Predicate Pushdown

Parquet stores min/max statistics for each column chunk, enabling **predicate pushdown**:
- Query engine reads metadata, skips row groups where predicate can't match
- Example: `SELECT * FROM sales WHERE amount > 1000` — only scan row groups with max(amount) > 1000

---

## 🗂️ 4. ORC File Format: Internals

ORC (Optimized Row Columnar) is another popular columnar format (Hive, Presto, Spark).

**File Layout:**
```
┌────────────────────────────────────────────┐
│ ORC File                                  │
├────────────────────────────────────────────┤
│ Stripe 1                                  │
│   ├─ Column: sale_id                       │
│   ├─ Column: date_id                       │
│   ├─ Column: product_id                    │
│   └─ ...                                   │
│ Stripe 2                                  │
│   ├─ Column: sale_id                       │
│   ├─ Column: date_id                       │
│   ├─ Column: product_id                    │
│   └─ ...                                   │
│ ...                                        │
├────────────────────────────────────────────┤
│ Footer (metadata, schema, statistics)      │
└────────────────────────────────────────────┘
```

**Key Concepts:**
- **Stripe:** Horizontal partition (default 64MB)
- **Column:** All values for a column in a stripe
- **Index:** Min/max, bloom filters for fast filtering
- **Footer:** Schema, stats, compression info

### Compression & Indexing

ORC supports:
- **Compression:** Zlib, Snappy, LZ4, Zstd
- **Bloom Filters:** Fast existence checks (e.g., does product_id=501 exist?)
- **Min/Max Indexes:** Enable partition pruning

---

## 🛠️ 5. Hands-On: Creating & Reading Parquet/ORC Files

### Python Example (PyArrow)

```python
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# Create DataFrame
df = pd.DataFrame({
    'sale_id': [101, 102, 103],
    'date_id': [20231001, 20231002, 20231003],
    'product_id': [501, 502, 503],
    'amount': [100, 200, 150]
})

# Write Parquet
table = pa.Table.from_pandas(df)
pq.write_table(table, 'sales.parquet', compression='zstd')

# Read Parquet
table = pq.read_table('sales.parquet', columns=['sale_id', 'amount'])
print(table.to_pandas())
```

### CLI Example (Parquet Tools)

```bash
# Inspect Parquet file
parquet-tools head sales.parquet
parquet-tools meta sales.parquet
```

---

## 📊 6. Compression Benchmarks

**Real-World Example:**
- 1 billion sales records (10 columns)
- Raw CSV: 100 GB
- Parquet (Snappy): 15 GB
- Parquet (Zstd): 10 GB
- ORC (Zlib): 12 GB

**Compression Ratio:**
- Parquet/ORC: 7-10x smaller than CSV
- Query time: 10x faster (scan only needed columns)

---

## 🏆 Interview Questions (Beginner Level)

1. What is the difference between row-based and columnar storage?
2. How does Parquet enable predicate pushdown?
3. Why is columnar storage better for analytics?
4. What is dictionary encoding?
5. How do you create a Parquet file in Python?

---

## 🎓 Summary Checklist

- [ ] Explain fact/dimension tables and star schema
- [ ] Describe row-based vs columnar storage
- [ ] Draw Parquet/ORC file layout
- [ ] Implement Parquet file creation and reading
- [ ] Benchmark compression ratios
- [ ] Answer basic interview questions

**Next:** [INTERMEDIATE.md →](INTERMEDIATE.md)
