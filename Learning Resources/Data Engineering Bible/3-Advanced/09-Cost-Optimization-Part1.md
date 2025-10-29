# Cost Optimization for Data Platforms - Part 1 (Sections 0–11)

## 0. Executive Snapshot (TL;DR for Leadership)
Cost optimization in modern data platforms is not random cost-cutting—it is structured engineering that reduces unneeded IO, CPU, network, and storage amplification while preserving reliability and latency SLAs.

| Lever | Typical Waste | Target Reduction | 90-Day Initiative | Annualized Savings (Illustrative) |
|-------|---------------|------------------|-------------------|-----------------------------------|
| Storage Format & Layout | Raw JSON / CSV lakes | 50–70% size reduction | Migrate to columnar + compaction | $120K (petabyte-scale) |
| Small Files (Metadata Storm) | Millions of sub-128MB files | 90% file count reduction | Auto-compaction + size policy | $40K (NameNode / listing) |
| Unpruned Scans | Full table scans for small queries | 30–60% scan reduction | Partition + data skipping indexes | $75K (query engine compute) |
| Over-Partitioning | Hourly + high-cardinality partitions | 5–10× manifest overhead | Rebalance strategy + dynamic partition pruning | $25K |
| Expensive Compression Misuse | GZIP for interactive workloads | 30–50% CPU saved | Move to ZSTD/Snappy tiered policy | $30K |
| Redundant Tier Storage | Hot data sitting on premium storage | 40–60% storage tier savings | Lifecycle to warm/cold tiers (S3 IA / Glacier) | $55K |
| Shuffle & Skew | Long tail tasks cause spill | 20–35% job duration ↓ | Skew mitigation + adaptive execution | $65K |

Strategic Principle: Optimize the data shape before tackling engine changes. Format → Layout → Access Path → Execution Plan → Resource Policy.

ROI Rule of Thumb: 1 principal engineer + 1 senior engineer focusing 3 months on structured cost optimization can unlock 15–30% recurring platform spend reduction without degrading SLA—if backed by measurement.

---

## 1. ELI10 Analogy (Explain Like I'm 10)
Imagine you run a big library. People search for books every minute. If you store all books in giant messy boxes (CSV/JSON), the librarian must open every box to find one page—slow and tiring. If you reorganize books by topic and put labels showing which shelf has what (Parquet + metadata), the librarian only walks to the right shelf and picks the correct chapter.

Compression is like flattening clothes before packing; some methods flatten fast (Snappy), others flatten tighter but take longer to unpack (GZIP). Partitioning is grouping books by year so you don't check 1990 books for a 2024 topic.

Cost optimization = arranging the library so fewer steps, less lifting, same answers.

---

## 2. Problem Framing (Why Teams Overspend)
Common systemic causes of runaway data platform costs:
1. Format Friction: Raw ingestion never upgraded from CSV/JSON → high scan amplification.
2. Small File Problem: Streaming micro-batches produce huge numbers of tiny files → metadata overhead, poor sequential IO.
3. Over-Partitioning: Combining time + high-cardinality dimension (e.g., country + user_id) leads to partition explosion; query pruning ineffective.
4. Unbounded Retention: No lifecycle policies → cold data sits in hot tier (high $/GB-month).
5. Heavy Compression Misalignment: Using GZIP universally—even for frequent interactive queries → decompression CPU waste.
6. Blind Full Scans: Dashboards / ad-hoc SQL selecting * without projections; no column pruning enforced.
7. No Query Feedback Loop: Lack of audit logs feeding optimization decisions; reactive rather than proactive tuning.
8. Shuffle Spills: Poor partitioning and skew cause large shuffle stages to spill to disk—compute time balloon.
9. Redundant Derived Tables: Unmanaged duplication (daily snapshots, unreferenced aggregates) → silent storage bloat.
10. Unused Materializations: Incremental jobs generating persisted copies for latency savings that no longer justified.

Risk: Without guardrails, a data platform scales cost linearly (or worse super-linearly) with volume growth while value per TB remains flat.

---

## 3. Core Concepts & Terminology Deep Dive

| Concept | Definition | Cost Impact | Principal Architect Insight |
|---------|------------|-------------|------------------------------|
| Columnar Format | Stores values by column (Parquet/ORC) instead of row | Reduces IO via selective reads; high compression ratio | Enables predicate + column pruning, foundation of long-term efficiency. |
| Predicate Pushdown | Engine applies filters at file/segment level using metadata min/max statistics | Avoids scanning uninterested row groups | Must validate metadata accuracy during ingestion; corrupted stats degrade pushdown efficacy. |
| Data Skipping / Zone Maps | Per-block summaries (min/max, bloom indexes) letting engine skip blocks | Reduces disk + network IO | For Iceberg, optimize manifests + add persistent indexes for high-selectivity workloads. |
| Partitioning | Physical layout by key (e.g., date) | Enables coarse pruning, reduces scan domain | Limit high-cardinality keys; prefer composite normalized keys with bucketing. |
| Bucketing / Hash Partition | Distributes rows into fixed number of buckets by hash | Balances load, improves joins | Use for large dimension join keys; watch for bucket count drift over time. |
| Compaction | Merges small files into larger chunks (~256MB–1GB) | Reduces metadata operations, improves sequential reads | Schedule off-peak; tiered compaction (recent vs historical). |
| File Size Policy | Target size for optimal scan throughput (e.g., 512MB) | Minimizes seek overhead, avoids tiny file penalty | Enforce via ingestion writer buffer and post-processing compactor. |
| Manifest / Metadata Scaling | Table metadata describing file lists and stats | Governs planning latency | Iceberg manifests must be periodically rewritten to avoid planning blow-ups. |
| Adaptive Query Execution (AQE) | Runtime optimization adjusting plans based on metrics | Reduces skew and spills | Ensure engines have accurate stats; stale stats sabotage AQE benefits. |
| Compression Algorithm | Method to reduce size (Snappy, ZSTD, GZIP) | Balances CPU vs storage | Tier by workload: interactive → Snappy/ZSTD medium; archival → ZSTD high or GZIP. |
| Vectorized Execution | Operates on batches (column vectors) | Improves CPU efficiency | Ensure format + encoding support; avoid exotic encodings that block vectorization. |
| Materialization Strategy | Persisting intermediate datasets | Saves recompute or wastes storage | Catalog actual usage; drop stale layers aggressively. |
| Query Governance | Shaping query patterns (limit * selects) | Avoids unnecessary scan amplification | Implement views with projected columns; enforce policies via lint/CI. |

---

## 4. Architecture Overview (Cost-Aware Data Platform)

```
                +-----------------------------+
                |     Access Layer (BI / ML)  |
                +---------------+-------------+
                                |
                        Query Engines (Trino / Spark / Snowflake)
                                |
                    +-----------+-----------+
                    |   Optimization Layer  |  (Stats, Zone Maps, Caching)
                    +-----------+-----------+
                                |
                        Data Layout Manager (Compaction, Partition Strategy)
                                |
        +--------------------+--------------------+--------------------+
        |  Bronze (Raw)      |  Silver (Cleaned)  |  Gold (Curated)    |
        |  JSON/CSV → Parquet|  Parquet (Compacted)| Aggregates, HLL,  |
        |                    |  ZSTD / Snappy     | Semantic Models    |
        +---------+----------+--------------------+----------+--------+
                  |                                        |
          Ingestion Services                          Lifecycle / Tiering
```

Key Cost Control Points:
1. Ingestion: Enforce columnar conversion early; prevent raw format sprawl.
2. Layout Manager: Scheduled compaction, partition/bucket enforcement.
3. Optimization Layer: Maintains stats (min/max), bloom filters, zone maps.
4. Query Engines: Enforce resource quotas, detect anti-pattern queries.
5. Lifecycle Policies: Transition cold data to cheaper tiers (S3 IA/Glacier / GCS Nearline / Azure Cool).
6. Governance Hooks: Pre-query rewriting for dropping unused columns.

Architectural Tenet: Treat data shape transformations as first-class scheduled jobs with success/failure SLOs.

---

## 5. Storage Formats Deep Dive (Parquet vs ORC vs Iceberg Table Abstraction)

### Parquet
- Strengths: Widely adopted; efficient column encoding (DICT, RLE); strong ecosystem; good predicate pushdown.
- Limitations: Lacks built-in ACID table management (needs Delta/Iceberg layer for transactions & schema evolution versions).
- Operational Consideration: Stats sometimes coarse at row-group level; may need building auxiliary indexes.

### ORC
- Strengths: Index streams (min/max, bloom) more granular; strong predicate pushdown; lightweight metadata footprint.
- Limitations: Less universal outside Hive/Spark ecosystems; sometimes slower adoption for lakehouse frameworks.
- Operational Consideration: Bloom filter index building increments write cost—evaluate for high-selectivity columns only.

### Iceberg (Table Format Layer)
- Not a file format—an abstraction orchestrating Parquet/ORC/Avro underneath.
- Strengths: Hidden partitioning, versioned snapshots, metadata scaling through manifest lists, schema evolution safety.
- Cost Win: Planning minimal if manifests cleaned; snapshot rollback reduces expensive recomputation.
- Pitfall: Neglecting periodic manifest compaction leads to planning time explosion and memory pressure.

| Attribute | Parquet | ORC | Iceberg (Table) |
|----------|---------|-----|-----------------|
| Predicate Pushdown | ✅ Row-group stats | ✅ Granular indexes | Depends on underlying + manifests |
| Bloom Index | Manual (external tooling) | Built-in optional | External (or underlying) |
| Schema Evolution | Limited (add columns) | Limited | Robust (rename, add, delete with versions) |
| Metadata Scaling | Row-group stats only | Index streams | Manifests + snapshot layering |
| Ecosystem | Very broad | Moderate | Rapidly growing (Trino, Spark, Flink) |
| Typical Use | General columnar | High-selectivity analytics | Lakehouse governance |

Architect Decision Lens:
- Start with Parquet baseline; layer Iceberg for governance & evolution once table count + evolution demands escalate.
- Use ORC selectively if extremely high selectivity queries dominate and ecosystem support is aligned.

---

## 6. Compression Algorithms Comparative Analysis

### Algorithms
| Algorithm | Compression Ratio (Illustrative) | Decompression Speed | CPU Cost | Typical Use |
|-----------|----------------------------------|---------------------|----------|-------------|
| Snappy | Low–Medium | Very Fast | Low | Interactive queries, streaming ingestion |
| ZSTD (Level 1–6) | Medium–High | Fast | Medium | General-purpose, balanced workloads |
| ZSTD (Level 10+) | High | Slower | High | Archival with periodic access |
| GZIP | High | Moderate | High | Legacy compatibility, static archival |
| LZ4 | Low | Fastest | Low | Real-time pipelines, logs |

Decision Matrix:
- Interactive Presto/Trino dashboards: Snappy or ZSTD level 3–5 for balance.
- Archival (regulatory, rarely queried): ZSTD level 9–12 or GZIP if ecosystem tooling bound to it.
- Streaming Append Logs (Kafka connectors): LZ4/Snappy for minimal latency.

Cost Model Example (Illustrative):
- 100 TB raw → Snappy reduces to ~60 TB; ZSTD (lvl 5) → ~50 TB; ZSTD (lvl 12) → ~45 TB.
- If storage = $20/TB-month: Snappy saves $800/month; ZSTD lvl 5 saves $1,000; lvl 12 saves $1,100 but adds ~30% CPU overhead—justify only if read frequency <1× per week.

Tiered Compression Policy: Assign compression by access frequency bucket (Hot, Warm, Cold) tracked via query logs and last-access timestamps.

---

## 7. Partition Strategy & File Sizing

### Goals:
- Enable maximum pruning (minimize scanned row groups).
- Avoid partition explosion and metadata overhead.
- Balance file sizes for optimal sequential IO (avoid extremely large >2GB or tiny <64MB).

| Pattern | Good Use Case | Anti-Pattern Risk | Mitigation |
|---------|---------------|-------------------|------------|
| DATE (YYYY-MM-DD) | Time-series ingestion | None (if daily) | Revisit if daily partitions too small (<128MB) |
| DATE + HOUR | High-frequency events | 24× partition multiplier | Auto-merge low-volume hours |
| HASH(user_id, 64 buckets) | Large user-based joins | Too few buckets → skew | Periodically rehash with stats |
| COUNTRY + DATE | Moderate cardinality dimension | High cardinality dimension floods partitions | Collapse rare countries into OTHER bucket |
| DEVICE_ID | Very high cardinality (>1M) | Partition explosion | Replace with bucketing or omit |

Sizing Guidelines:
- Target Parquet row group ~128MB uncompressed; file size 256–1024MB compressed.
- Implement writer buffering: accumulate records until threshold, flush sequentially.
- Scheduled Compaction: Daily job merging small files (<128MB) in last 7 days partition, skip older stable partitions.

Dynamic Partition Pruning: Ensure engine (Spark 3+/Trino) enabled; validate via query plan inspection.

---

## 8. Failure Modes (Cost-Centric)

| Failure Mode | Symptom | Root Cause | Detection | Mitigation | Prevention |
|--------------|---------|-----------|----------|-----------|-----------|
| Small File Flood | Query planning slow; NameNode metadata spikes | Micro-batch writes w/o compaction | Files <64MB count by partition | Run compaction job; consolidate | Enforce writer min-buffer; alert on file count ratio |
| Partition Explosion | Millions of tiny partitions; high listing latency | High-cardinality key used as partition | Metadata listing time > threshold | Repartition using bucketing | Partition strategy review in design gate |
| Unpruned Scans | High scan GB per query; long tail latency | Missing partition filters; SELECT * | Query audit log (scanned_bytes / output_rows high) | Add views with projections; educate | Query lint rule; auto-rewriting layer |
| Excessive Shuffle Spill | Long-running tasks; disk IO spike | Skewed keys; insufficient parallelism | Executor metrics (spill bytes) | Skew-aware repartition; AQE on | Stats refresh; key distribution audit |
| Compression Mismatch | CPU hotspots; low overall savings | Heavy compression on hot data | Profile decompression CPU per query | Tier compression; re-encode hot partitions | Policy engine based on last-access time |
| Manifest Bloat (Iceberg) | Planning latency increases | Uncompacted manifests; many snapshots | Planning time > SLA threshold | Run snapshot expire + rewrite manifests | Scheduled metadata housekeeping |
| Redundant Materializations | Storage growth w/o query usage | Stale derived datasets | Query access logs (0 reads 30d) | Deprecate and delete | Automatic TTL on derived layers |
| Zombie Partitions | Data retained beyond retention | Lifecycle not applied | Age distribution report | Apply retention delete job | Policy enforced via infra-as-code |

---

## 9. Benchmark Harness (Foundational Measurement)

Principle: Never optimize blindly. Build reproducible harness comparing scenarios (format, compression, partition strategy) using identical data distribution.

### Synthetic Data Generator (Python)
```python
import pandas as pd, numpy as np
import pyarrow as pa, pyarrow.parquet as pq
from datetime import datetime, timedelta

rows = 50_000_000
np.random.seed(42)

user_ids = np.random.randint(1, 5_000_000, rows)
amounts = np.random.exponential(scale=50, size=rows)
country = np.random.choice(['US','IN','CA','DE','FR','BR'], rows, p=[0.4,0.2,0.1,0.1,0.1,0.1])
ts = np.random.randint(0, 30, rows)
dates = pd.to_datetime('2024-09-01') + pd.to_timedelta(ts, unit='D')

pdf = pd.DataFrame({
    'user_id': user_ids,
    'amount': amounts,
    'country': country,
    'event_date': dates
})

# Write raw CSV (baseline cost)
pdf.sample(5_000_000).to_csv('transactions_raw.csv', index=False)

# Write Parquet (Snappy)
table = pa.Table.from_pandas(pdf)
pq.write_table(table, 'transactions_parquet_snappy.parquet', compression='snappy', row_group_size=500_000)

# Write Parquet (ZSTD)
pq.write_table(table, 'transactions_parquet_zstd.parquet', compression='zstd', row_group_size=500_000)
```

### Spark Benchmark Script (Scala)
```scala
val t1 = spark.read.option("header","true").csv("transactions_raw.csv")
val t2 = spark.read.parquet("transactions_parquet_snappy.parquet")
val t3 = spark.read.parquet("transactions_parquet_zstd.parquet")

def bench(df: DataFrame, label: String)(f: DataFrame => Unit) = {
  val start = System.nanoTime()
  f(df)
  val secs = (System.nanoTime() - start) / 1e9
  println(s"$label took ${secs}s")
}

bench(t1, "CSV full scan")(_.filter("amount > 100").groupBy("country").count().collect())
bench(t2, "Parquet Snappy")(_.filter("amount > 100").groupBy("country").count().collect())
bench(t3, "Parquet ZSTD")(_.filter("amount > 100").groupBy("country").count().collect())
```

### Metrics to Capture
| Metric | Why | Tool |
|--------|-----|------|
| Scan Bytes | Direct IO cost | Engine query stats |
| CPU Time / Task | Compression overhead | Spark UI / Trino profile |
| Planning Time | Manifest / metadata health | Engine logs |
| Shuffle Spill Bytes | Execution inefficiency | Executor metrics |
| Output Rows / Scanned Bytes Ratio | Query selectivity | Derived metric |

Store benchmark snapshots; track delta after each optimization.

---

## 10. Quick Wins Matrix (Impact vs Effort)

| Initiative | Impact | Effort | Time-to-Value | Notes |
|------------|--------|--------|---------------|-------|
| Add Column Projections in BI Views | High | Low | <1 week | Remove SELECT * default |
| Compaction of Last 30 Days | High | Medium | 2 weeks | Solve small file & scan overhead |
| Lifecycle Policy (Move >90d to Cold Tier) | Medium | Low | 1 week | Immediate storage savings |
| Compression Tiering (Hot/Warm/Cold) | Medium | Medium | 3 weeks | Balance CPU vs storage |
| Partition Strategy Review | High | High | 4–6 weeks | Requires data distribution analysis |
| Add Zone Maps / Bloom Index | Medium | Medium | 3 weeks | Beneficial for selective columns |
| Stale Dataset Pruning | Medium | Low | 1 week | Needs usage telemetry |
| Query Linter / Governance | Medium | Medium | 4 weeks | Cultural + tooling change |
| Adaptive Execution Enablement | Low–Medium | Low | <1 week | Validate config correctness |
| Manifest/Metadata Housekeeping | Medium | Low | <1 week | Regular maintenance schedule |

Choose 3–5 high-impact low-medium effort for first 30 days to build momentum.

---

## 11. Observability & Cost Telemetry (Foundations)

Instrumentation Goals:
1. Attribute cost to queries (scan bytes, CPU seconds) by team / project tag.
2. Detect anomalies (sudden scan amplification day-over-day).
3. Provide leading indicators of future runaway spend (partition count growth rate, small file ratio).

### Metrics Catalog
| Metric | Type | Description | Alert Condition |
|--------|------|-------------|-----------------|
| data_scan_bytes_total | Counter | Sum of bytes scanned | 3-day moving average +30% |
| small_file_ratio | Gauge | (#files <64MB) / total files per table | >0.25 |
| partition_count | Gauge | Current partition count per table | Growth >10% week-over-week |
| query_selectivity | Histogram | (output_rows / scanned_rows) | Median <0.05 for key workloads |
| compression_cpu_seconds | Counter | CPU spent decompressing | >20% of total CPU budget |
| manifest_planning_ms | Histogram | Planning latency for Iceberg tables | p95 > 2000ms |
| stale_dataset_count | Gauge | Derived datasets no reads 30d | >100 triggers cleanup |

### Example Prometheus Export (Pseudo-Python)
```python
from prometheus_client import Counter, Gauge

SCAN_BYTES = Counter('data_scan_bytes_total', 'Total scan bytes', ['table','team'])
SMALL_FILE_RATIO = Gauge('small_file_ratio', 'Small file ratio', ['table'])
COMPRESSION_CPU = Counter('compression_cpu_seconds', 'CPU seconds decompress', ['algorithm'])
MANIFEST_MS = Gauge('manifest_planning_ms', 'Iceberg planning ms', ['table'])

def record_query_metrics(table, team, scanned_bytes, output_rows, decompress_cpu, planning_ms):
    SCAN_BYTES.labels(table, team).inc(scanned_bytes)
    COMPRESSION_CPU.labels('zstd').inc(decompress_cpu)
    MANIFEST_MS.labels(table).set(planning_ms)
    # Additional logic: push selectivity metric via StatsD or aggregated label
```

### Cost Attribution Tagging
- Inject user/team tags at query entrypoint (BI tool, API). Example: Presto session properties: `SET session client_tags = 'team=marketing,project=ad_insights';`
- Pipe metrics to monthly chargeback reports.

Alert Philosophy: Prefer rate-of-change alerts (growth acceleration) over absolute thresholds alone—catches early cost curve inflection.

---

## ✅ Sections 0–11 Complete Summary
- Executive framing with 7 levers and ROI
- ELI10 analogy mapping library organization to data layout
- Problem framing enumerating 10 systemic waste patterns
- Deep concept table with architect insights
- Layered architecture emphasizing transformation sequencing
- Storage format evaluation (Parquet vs ORC vs Iceberg governance)
- Compression strategy and tiered policy recommendation
- Partition & file sizing patterns with anti-pattern mitigation
- Cost-focused failure modes with detection & prevention
- Reproducible benchmark harness (generator + Spark script)
- Quick Wins matrix + observability metric catalog

---

Next (Part 2 Sections 12–14): Implementation Tracks, Real Company Case Studies (Netflix, Uber, Airbnb cost wins), Interview Question Bank.
