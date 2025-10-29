# Week 12-13: Lakehouse Architecture — WHITEPAPERS

*"Reading the Delta Lake protocol, Iceberg spec, and Hudi design papers is essential for understanding the trade-offs. These aren't just formats—they're distributed systems solving different problems."* — Distinguished Engineer, Databricks

---

## 📚 Paper 1: Delta Lake Protocol (Databricks, 2019)

**Link:** https://github.com/delta-io/delta/blob/master/PROTOCOL.md

### Abstract

Delta Lake provides ACID transactions on top of object stores (S3, ADLS, GCS) by maintaining a transaction log as a sequence of JSON files. The protocol defines:
1. How to read/write transaction logs atomically
2. Optimistic concurrency control for conflicting writes
3. Checkpoint mechanism for fast metadata access

---

### Core Concepts

#### 1. Transaction Log Structure

```
_delta_log/
├─ 00000000000000000000.json  (Version 0: CREATE TABLE)
├─ 00000000000000000001.json  (Version 1: INSERT)
├─ 00000000000000000002.json  (Version 2: UPDATE)
├─ 00000000000000000003.json  (Version 3: DELETE)
├─ ...
├─ 00000000000000000010.checkpoint.parquet  (Checkpoint at v10)
└─ 00000000000000000020.json  (Version 20)

Each JSON file contains actions:
{
  "add": {
    "path": "part-00000.parquet",
    "size": 1024,
    "partitionValues": {"date": "2023-10-15"},
    "stats": "{\"numRecords\": 1000, \"minValues\": {...}, \"maxValues\": {...}}"
  }
}

{
  "remove": {
    "path": "part-00001.parquet",
    "deletionTimestamp": 1697385600000
  }
}
```

**Insight:** By listing files in sorted order (`00000.json`, `00001.json`, ...), Delta can reconstruct table state at any version by replaying actions.

---

#### 2. Optimistic Concurrency Control (OCC)

```
Writer 1:                          Writer 2:
├─ Read latest version: v10       ├─ Read latest version: v10
├─ Compute changes                ├─ Compute changes
├─ Write v11.json ✅              ├─ Write v11.json ❌ CONFLICT!
└─ Success                         └─ Retry as v12

Conflict Detection:
1. Writer reads current version (v10)
2. Writer computes changes locally
3. Writer attempts to write v11.json
4. S3 PUT with precondition:
   "if-none-match: v11.json does not exist"
5. If another writer created v11.json first:
   ├─ PUT fails (409 Conflict)
   ├─ Writer re-reads table (now v11)
   ├─ Re-computes changes
   └─ Retries as v12

Conflict Resolution Rules:
├─ APPEND + APPEND = No conflict (both succeed)
├─ UPDATE + UPDATE (disjoint files) = No conflict
├─ UPDATE + UPDATE (same files) = Conflict (retry)
├─ DELETE + UPDATE (same files) = Conflict (retry)
└─ Schema change + Data change = Conflict (retry)
```

**Insight:** Delta trades off availability (retry on conflict) for consistency (no lost updates).

---

#### 3. Checkpointing

```
Problem: Replaying 1M JSON files is slow

Solution: Checkpoint every 10 commits

_delta_log/
├─ 00000000000000000000.json
├─ ...
├─ 00000000000000000010.checkpoint.parquet  ← Snapshot at v10
│    (Contains aggregated state of all actions 0-10)
├─ 00000000000000000011.json
├─ ...
├─ 00000000000000000020.checkpoint.parquet  ← Snapshot at v20
└─ 00000000000000000025.json

Reading at v25:
1. Find latest checkpoint ≤ 25 → v20.checkpoint.parquet
2. Load checkpoint (Parquet, fast)
3. Replay JSON files 21-25
4. Result: Table state at v25

Without checkpoint: Replay 0-25 (26 files)
With checkpoint: Replay 20-25 (6 files) ✅
```

**Performance:**
- Checkpoint read: 100 ms
- JSON replay (10 files): 50 ms
- **Total: 150 ms** (vs 2.6 seconds without checkpoint)

---

#### 4. Stats Pruning

```json
{
  "add": {
    "path": "date=2023-10-15/part-00000.parquet",
    "size": 1048576,
    "partitionValues": {"date": "2023-10-15"},
    "stats": {
      "numRecords": 1000,
      "minValues": {"user_id": 1, "timestamp": "2023-10-15T00:00:00Z"},
      "maxValues": {"user_id": 5000, "timestamp": "2023-10-15T23:59:59Z"}
    }
  }
}
```

**Query Pruning:**

```sql
SELECT * FROM events WHERE user_id = 12345 AND date = '2023-10-15'
```

Delta optimizer:
1. Partition pruning: `date = '2023-10-15'` → Only read partition `date=2023-10-15/`
2. Stats pruning: `user_id = 12345` → Check min/max:
   - File 1: min=1, max=5000 → ✅ Read (12345 in range)
   - File 2: min=6000, max=10000 → ❌ Skip (12345 not in range)

**Result:** Read 1 file instead of 10 files ✅

---

### Critical Insights

1. **S3 Consistency Challenges:**
   - Old S3 (pre-2020): Eventually consistent LIST
   - Delta protocol assumes atomic PUT (exists since S3 launch)
   - Solved with S3 Strong Consistency (Dec 2020)

2. **Why JSON for Transaction Log?**
   - Human-readable (debug-friendly)
   - Schema evolution support (add new fields)
   - Small size (<1 KB/commit)
   - Trade-off: Slower than binary (Parquet), but fast enough with checkpoints

3. **Comparison to Iceberg:**
   - Delta: Single JSON file per commit (simple, but scales to ~1M commits)
   - Iceberg: 3-level metadata (complex, but scales to ~100M snapshots)

---

## 📄 Paper 2: Apache Iceberg Table Format Specification (Netflix, 2018)

**Link:** https://iceberg.apache.org/spec/

### Abstract

Iceberg is a table format designed for **multi-petabyte** analytic datasets with:
1. Three-level metadata hierarchy (metadata.json → manifest list → manifest files)
2. Hidden partitioning with automatic partition pruning
3. Time travel via immutable snapshots
4. Schema evolution with backward compatibility

---

### Core Architecture

#### 1. Three-Level Metadata

```
s3://bucket/my_table/
├─ metadata/
│  ├─ v1.metadata.json             ← Version 1
│  ├─ v2.metadata.json             ← Version 2
│  ├─ snap-12345.avro              ← Snapshot 12345 manifest list
│  ├─ snap-12346.avro              ← Snapshot 12346 manifest list
│  ├─ manifest-abc123.avro         ← Manifest file (file-level metadata)
│  └─ manifest-def456.avro
└─ data/
   ├─ part-00000.parquet
   └─ part-00001.parquet

Level 1: metadata.json (Pointer to current snapshot)
{
  "format-version": 2,
  "table-uuid": "abc-123",
  "current-snapshot-id": 12346,
  "snapshots": [
    {"snapshot-id": 12345, "manifest-list": "snap-12345.avro"},
    {"snapshot-id": 12346, "manifest-list": "snap-12346.avro"}
  ]
}

Level 2: snap-12346.avro (Manifest list)
[
  {"manifest_path": "manifest-abc123.avro", "added_files": 10},
  {"manifest_path": "manifest-def456.avro", "added_files": 5}
]

Level 3: manifest-abc123.avro (Manifest file)
[
  {
    "file_path": "data/part-00000.parquet",
    "file_size_in_bytes": 1048576,
    "partition": {"date": 18915},  # days since epoch
    "record_count": 1000,
    "column_sizes": {...},
    "value_counts": {...},
    "null_value_counts": {...},
    "lower_bounds": {"user_id": 1},
    "upper_bounds": {"user_id": 5000}
  }
]
```

**Why 3 Levels?**

- **Level 1 (metadata.json):** Small (<10 KB), atomic updates via S3 PUT
- **Level 2 (manifest list):** Reusable across snapshots (unchanged manifests reused)
- **Level 3 (manifest files):** File-level stats for pruning

**Scalability:**
- Delta Lake: 1M commits → 1M JSON files (~1 GB metadata)
- Iceberg: 100M snapshots → 1 metadata.json + 100M manifest entries (~10 GB metadata) ✅

---

#### 2. Hidden Partitioning

```sql
-- Traditional partitioning (Hive-style)
CREATE TABLE events (
    event_id BIGINT,
    event_time TIMESTAMP,
    user_id BIGINT
)
PARTITIONED BY (event_date DATE);  -- User must provide partition value

INSERT INTO events PARTITION(event_date = '2023-10-15')
VALUES (1, '2023-10-15 10:00:00', 100);

-- Iceberg hidden partitioning
CREATE TABLE events (
    event_id BIGINT,
    event_time TIMESTAMP,
    user_id BIGINT
)
PARTITIONED BY (days(event_time));  -- Transform function

INSERT INTO events VALUES (1, '2023-10-15 10:00:00', 100);
-- Iceberg automatically computes: days('2023-10-15 10:00:00') = 18915
```

**Transform Functions:**

```
1. days(timestamp_col) → Integer (days since 1970-01-01)
   '2023-10-15 10:30:00' → 18915

2. months(timestamp_col) → Integer (months since 1970-01)
   '2023-10-15' → 645

3. years(timestamp_col) → Integer (years since 1970)
   '2023-10-15' → 53

4. hours(timestamp_col) → Integer (hours since 1970-01-01 00:00:00)
   '2023-10-15 10:30:00' → 454584

5. bucket(N, col) → Integer (hash(col) % N)
   bucket(10, user_id) → hash(12345) % 10 = 5

6. truncate(width, col) → Same type (round down)
   truncate(10, user_id) → user_id = 12345 → 12340
```

**Automatic Partition Pruning:**

```sql
SELECT * FROM events WHERE event_time BETWEEN '2023-10-15' AND '2023-10-16'

Iceberg optimizer:
1. Compute partition range:
   days('2023-10-15') = 18915
   days('2023-10-16') = 18916
2. Scan manifests for partitions [18915, 18916]
3. Skip all other partitions ✅

Result: Read 2 days instead of 365 days
```

---

#### 3. Partition Evolution

```sql
-- Initial: Partition by day
CREATE TABLE events PARTITIONED BY (days(event_time));

-- Insert data for 2023
INSERT INTO events VALUES (...);  -- Partitioned by day

-- After 1 year: Too many partitions (365 partitions/year)
-- Change to monthly partitioning
ALTER TABLE events SET PARTITION SPEC (months(event_time));

-- Insert data for 2024
INSERT INTO events VALUES (...);  -- Partitioned by month

-- Query works across both partition schemes!
SELECT * FROM events WHERE event_time >= '2023-01-01'
-- Iceberg reads:
-- ├─ 2023 data: daily partitions (365 partitions)
-- └─ 2024 data: monthly partitions (12 partitions)
```

**How it works:**

```
metadata.json:
{
  "partition-specs": [
    {"spec-id": 0, "fields": [{"name": "event_day", "transform": "days", "source-id": 2}]},
    {"spec-id": 1, "fields": [{"name": "event_month", "transform": "months", "source-id": 2}]}
  ],
  "default-spec-id": 1
}

Manifest files:
manifest-2023.avro:
  file: data/2023-10-15/part-00000.parquet, spec-id: 0, partition: {event_day: 18915}

manifest-2024.avro:
  file: data/2024-10/part-00000.parquet, spec-id: 1, partition: {event_month: 660}

Query planner:
1. For spec-id=0 files: Use days(event_time) for pruning
2. For spec-id=1 files: Use months(event_time) for pruning
3. Combine results
```

**Delta/Hudi limitation:** Changing partitioning requires full table rewrite ❌

---

#### 4. Schema Evolution with Column IDs

```
Problem: Rename column without breaking old files

Hive/Delta approach:
├─ Column identified by NAME
├─ Rename "user_id" → "customer_id"
└─ Old files still have "user_id" → Need rewrite ❌

Iceberg approach:
├─ Column identified by ID (immutable)
├─ Schema mapping:
│  v1: {1: "user_id", 2: "event_time"}
│  v2: {1: "customer_id", 2: "event_time"}  ← Rename
└─ Old files: Read field ID=1 as "customer_id" ✅
```

**Implementation:**

```json
// Schema v1
{
  "schema-id": 0,
  "fields": [
    {"id": 1, "name": "user_id", "type": "long"},
    {"id": 2, "name": "event_time", "type": "timestamp"}
  ]
}

// Schema v2 (after rename)
{
  "schema-id": 1,
  "fields": [
    {"id": 1, "name": "customer_id", "type": "long"},  // Same ID!
    {"id": 2, "name": "event_time", "type": "timestamp"}
  ]
}

// Old Parquet file (written with schema v1):
// Column 0: user_id (maps to ID=1)
// Column 1: event_time (maps to ID=2)

// Reading with schema v2:
// Query: SELECT customer_id FROM events
// Iceberg: Read field ID=1 from Parquet (column 0) ✅
```

---

### Critical Insights

1. **Manifest Reuse:**
   - When writing new data, Iceberg reuses unchanged manifest files
   - Example: Insert to partition `2023-10-15`
     - Manifest for partition `2023-10-14` unchanged → Reuse
     - Only create new manifest for `2023-10-15`
   - Result: Faster commits (less metadata I/O)

2. **Optimistic Concurrency:**
   - Similar to Delta: Atomic S3 PUT on `metadata.json`
   - Conflict detection: Check snapshot ID
   - Retry on conflict

3. **Comparison to Delta:**
   - Iceberg: Better scalability (100M+ snapshots)
   - Delta: Simpler (single JSON log)
   - Trade-off: Complexity vs simplicity

---

## 📘 Paper 3: Apache Hudi Design Paper (Uber, 2016)

**Link:** https://www.uber.com/blog/hoodie/

### Abstract

Hudi (Hadoop Upserts Deletes Incrementals) is designed for:
1. **Low-latency upserts** on data lakes
2. **Incremental processing** (consume only changes)
3. **Minute-level freshness** (real-time analytics)

---

### Core Architecture

#### 1. Timeline-Based Design

```
Hudi Timeline = Ordered sequence of instants

Instant types:
├─ REQUESTED: Action requested (not started)
├─ INFLIGHT: Action in progress
└─ COMPLETED: Action finished

Example timeline:
├─ 20231015100000.commit.requested
├─ 20231015100000.commit.inflight
├─ 20231015100000.commit (completed)
├─ 20231015110000.deltacommit.inflight
├─ 20231015110000.deltacommit (completed)
├─ 20231015120000.compaction.requested
└─ 20231015120000.compaction.inflight

Timeline enables:
1. Incremental queries: "Give me commits 100000 to 110000"
2. Rollback: Delete inflight commits
3. Crash recovery: Resume inflight commits
```

---

#### 2. Copy-on-Write vs Merge-on-Read (Revisited)

```
┌──────────────────────────────────────────────────────────────┐
│ Copy-on-Write (COW)                                          │
├──────────────────────────────────────────────────────────────┤
│ File Layout:                                                 │
│ partition/                                                   │
│ ├─ abc123_0_20231015100000.parquet (base file v1)           │
│ └─ abc123_0_20231015110000.parquet (base file v2, replaces v1)│
│                                                              │
│ Write:                                                       │
│ 1. Read existing file                                       │
│ 2. Merge with updates                                       │
│ 3. Write new file                                           │
│ 4. Delete old file                                          │
│                                                              │
│ Read:                                                        │
│ └─ Read latest base files directly                          │
│                                                              │
│ Latency:                                                     │
│ ├─ Write: High (full rewrite)                               │
│ └─ Read: Low (no merge needed)                              │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ Merge-on-Read (MOR)                                          │
├──────────────────────────────────────────────────────────────┤
│ File Layout:                                                 │
│ partition/                                                   │
│ ├─ abc123_0_20231015100000.parquet (base file)              │
│ ├─ .abc123_0_20231015100000.log.1_0-1-0 (delta 1)           │
│ ├─ .abc123_0_20231015100000.log.2_0-1-0 (delta 2)           │
│ └─ .abc123_0_20231015100000.log.3_0-1-0 (delta 3)           │
│                                                              │
│ Write:                                                       │
│ 1. Append updates to log file (Avro)                        │
│ 2. No base file rewrite                                     │
│ 3. Periodic compaction: Merge logs → new base file          │
│                                                              │
│ Read (Two Views):                                           │
│ 1. Read Optimized (RO):                                     │
│    └─ Read only base files (skip logs)                      │
│    → Fast, but stale                                        │
│                                                              │
│ 2. Real-Time (RT):                                          │
│    ├─ Read base file                                        │
│    ├─ Read log files                                        │
│    └─ Merge on-the-fly                                      │
│    → Slow, but fresh                                        │
│                                                              │
│ Latency:                                                     │
│ ├─ Write: Low (append-only)                                 │
│ ├─ Read (RO): Low (skip logs)                               │
│ └─ Read (RT): High (merge logs)                             │
└──────────────────────────────────────────────────────────────┘
```

**Key Insight:** MOR trades read latency (merge cost) for write latency (append-only).

---

#### 3. Indexing for Upserts

```
Problem: Upsert 1M records with keys [k1, k2, ..., k1000000]
         Table has 10,000 files
         How to find which files contain these keys?

Naive approach: Scan all 10,000 files ❌
Hudi approach: Use index ✅

Index Types:

1. Bloom Filter Index:
   ├─ Store bloom filter for each file (in metadata)
   ├─ Check: "Does file contain key k1?"
   ├─ False positives: Possible (1% FPP)
   ├─ False negatives: Never
   └─ Lookup: O(files) = O(10,000)

2. HBase Index:
   ├─ External HBase table: key → (partition, file_id)
   ├─ Lookup: O(1) via HBase Get
   └─ Overhead: Maintain HBase cluster

3. Simple Index (In-Memory):
   ├─ Load all keys into Spark executor memory
   ├─ HashMap: key → (partition, file_id)
   └─ Limitation: Memory intensive (10 GB+ for 1B keys)
```

**Performance Comparison:**

```
Table: 1B rows, 10K files, 1M upserts

Bloom Filter Index:
├─ Lookup: 10K bloom filter checks = 100 ms
├─ False positives: 10K * 0.01 = 100 files to scan
└─ Total: 100 ms + (100 files * 10 ms) = 1.1 seconds

HBase Index:
├─ Batch lookup: 1M keys in batches of 1000
├─ HBase Get latency: 5 ms/batch
└─ Total: (1M / 1000) * 5 ms = 5 seconds

Simple Index:
├─ Load keys into memory: 10 GB
├─ HashMap lookup: O(1) = 0.1 ms
└─ Total: 0.1 ms ✅ (but 10 GB memory)
```

---

#### 4. Incremental Processing

```
Use Case: Process only changed records

Traditional approach:
1. Scan full table (1B rows)
2. Filter by updated_at > last_checkpoint
3. Process filtered rows

Hudi approach:
1. Query incremental view:
   BEGIN_INSTANT = 20231015100000
   END_INSTANT = 20231015110000
2. Hudi returns only commits in range
3. Process only changed rows (10K rows instead of 1B)

Code:
df = spark.read.format('hudi') \
    .option('hoodie.datasource.query.type', 'incremental') \
    .option('hoodie.datasource.read.begin.instanttime', '20231015100000') \
    .option('hoodie.datasource.read.end.instanttime', '20231015110000') \
    .load('s3://bucket/hudi_table')

print(f"Incremental rows: {df.count()}")  # 10,000 rows
```

**Latency:**
- Full scan: 10 minutes (1B rows)
- Incremental: 5 seconds (10K rows) ✅

---

### Critical Insights

1. **Timeline as First-Class Citizen:**
   - Hudi's timeline enables incremental processing natively
   - Delta/Iceberg: Possible via time travel, but not primary design goal
   - Hudi: Built for streaming use cases (Kafka → Hudi → Incremental consumers)

2. **DeltaStreamer for CDC:**
   - Hudi DeltaStreamer: Kafka → Hudi in <1 minute
   - Handles schema evolution, deduplication, compaction
   - Production-ready (Uber runs 100+ DeltaStreamer jobs)

3. **Comparison to Delta/Iceberg:**
   - Hudi: Best for upsert-heavy + incremental processing
   - Delta: Best for Databricks ecosystem + batch processing
   - Iceberg: Best for multi-engine + partition evolution

---

## 🔬 Comparison Matrix

```
┌────────────────┬─────────────┬─────────────┬─────────────┐
│ Feature        │ Delta Lake  │ Iceberg     │ Hudi        │
├────────────────┼─────────────┼─────────────┼─────────────┤
│ ACID           │ OCC (JSON)  │ OCC (JSON)  │ OCC (JSON)  │
│ Metadata       │ 1-level     │ 3-level     │ Timeline    │
│ Partitioning   │ Static      │ Hidden/Evol │ Static      │
│ Schema Evol    │ Name-based  │ ID-based    │ Name-based  │
│ Indexing       │ Stats only  │ Stats only  │ Bloom/HBase │
│ Incremental    │ Time travel │ Snapshots   │ Native      │
│ Upsert         │ MERGE       │ MERGE       │ Native      │
│ Compaction     │ N/A (COW)   │ N/A (COW)   │ Async (MOR) │
│ Multi-Engine   │ Limited     │ Excellent   │ Moderate    │
│ Maturity       │ High        │ High        │ High        │
│ Scalability    │ 1M commits  │ 100M snaps  │ 10M commits │
└────────────────┴─────────────┴─────────────┴─────────────┘
```

---

## 🎓 Key Takeaways

1. **Delta Lake:**
   - Simple, production-ready
   - Best for Databricks/Spark ecosystem
   - Limitation: Scalability (~1M commits)

2. **Iceberg:**
   - Highly scalable (100M+ snapshots)
   - Multi-engine support (Spark, Flink, Presto, Trino)
   - Hidden partitioning + partition evolution
   - Complexity: 3-level metadata

3. **Hudi:**
   - Built for upserts + incremental processing
   - MOR table type for low-latency writes
   - Timeline-based design
   - Indexing (Bloom, HBase) for fast upserts

4. **When to Choose:**
   - **Delta:** Databricks platform, batch-heavy, simple operations
   - **Iceberg:** Multi-engine, massive scale, partition evolution
   - **Hudi:** Real-time upserts, CDC, incremental consumers

**Next:** [README.md →](README.md)
