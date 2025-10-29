# Cost Optimization for Data Platforms - Part 2 (Sections 12–14)

## 12. Implementation Tracks (Azure + Open Source Focus)

We present two tracks:
1. Rapid Retrofit (2–3 weeks): Minimum viable cost discipline for existing Azure data lake using open-source tooling.
2. Production Governance Platform (8–12 weeks): Full-lifecycle automated cost intelligence integrating Azure native + OSS components.

### 12.1 Rapid Retrofit Track (2–3 Weeks)
**Goal**: Achieve 20–30% immediate cost reduction and build telemetry baselines without architectural upheaval.

| Step | Action | Azure Service / OSS Tool | Measured Outcome | Principal Architect Notes |
|------|--------|---------------------------|------------------|---------------------------|
| 1 | Inventory datasets | Azure Data Lake Storage (ADLS) list + custom Python crawler | Visibility of file size distribution | Snapshot baseline; store in Cosmos DB or simple Parquet table for delta trending. |
| 2 | Convert raw CSV/JSON to columnar | Azure Databricks / Apache Spark | 50–70% storage & IO reduction | Use Snappy for hot; ZSTD for warm/cold. |
| 3 | Add compaction job | Azure Data Factory (ADF) schedule Spark notebook | Reduce small file count by >80% | Focus last 30 days partitions; avoid rewriting older stable partitions. |
| 4 | Implement compression tiering | Spark re-encoding + Azure Blob lifecycle rule | CPU saved for interactive queries | Tag files with access last timestamp; re-encode weekly. |
| 5 | Query audit logging | Trino / Databricks system tables into Log Analytics | Identify heavy scans (scanned_bytes vs output_rows) | Build top 20 wasteful query report; feed governance. |
| 6 | Basic metrics export | Prometheus (self-hosted) + custom exporters | Daily cost anomaly detection | Push small_file_ratio, partition_count gauges. |
| 7 | Lifecycle policy cold tier | ADLS -> Cool/Archive tier policies | 40–60% cost for aged data | Use prefix + age filter rules. |

Rapid Retrofit Code Snippets:

**Dataset Inventory (Python)**
```python
from azure.storage.filedatalake import DataLakeServiceClient
import os, json, math

service = DataLakeServiceClient(account_url=f"https://{os.getenv('ACCOUNT_NAME')}.dfs.core.windows.net", credential=os.getenv('SAS_TOKEN'))
file_system_client = service.get_file_system_client(file_system=os.getenv('FS_NAME'))

inventory = []

paths = file_system_client.get_paths(recursive=True)
for p in paths:
    if not p.is_directory:
        size_mb = int(p.content_length) / (1024*1024)
        inventory.append({
            'path': p.name,
            'size_mb': round(size_mb, 2),
            'small_file': size_mb < 64,
            'ext': p.name.split('.')[-1]
        })

# Persist to Parquet (for trend analysis)
import pandas as pd
pd.DataFrame(inventory).to_parquet('inventory_snapshot.parquet')
```

**Compaction Notebook Pseudocode (Spark / Databricks)**
```python
from pyspark.sql import functions as F

SOURCE = "abfss://raw@account.dfs.core.windows.net/transactions/"
TARGET = "abfss://silver@account.dfs.core.windows.net/transactions/"
PARTITIONS = 30  # target number of output files per day partition

for day in list_recent_days(30):
    df = spark.read.parquet(f"{SOURCE}/event_date={day}")
    df.repartition(PARTITIONS).write.mode('overwrite').parquet(f"{TARGET}/event_date={day}")

# Validate file sizes
sizes = spark._jsparkSession.catalog().listTables()  # Or use Hadoop FileSystem API
```

**Query Scan Waste Detector (Trino)**
```sql
-- Trino built-in system tables (if enabled)
SELECT query_id,
       table_name,
       processed_bytes,
       output_rows,
       (processed_bytes / NULLIF(output_rows,0)) AS bytes_per_row
FROM system.runtime.queries
WHERE state = 'FINISHED'
  AND processed_bytes > 10*1024*1024*1024  -- >10GB scanned
ORDER BY bytes_per_row DESC
LIMIT 50;
```

**Compression Tier Re-Encoder (ZSTD vs Snappy)**
```python
import pyarrow.parquet as pq, pyarrow as pa
from datetime import datetime, timedelta

COLD_THRESHOLD = 30  # days since last access

for meta in load_file_access_metadata():
    age_days = (datetime.utcnow() - meta['last_access']).days
    if age_days > COLD_THRESHOLD and meta['compression'] == 'SNAPPY':
        table = pq.read_table(meta['path'])
        pq.write_table(table, meta['path'], compression='zstd', compression_level=6)
```

**Prometheus Exporter (Azure Container Apps)**
```python
from prometheus_client import start_http_server, Gauge
import time

SMALL_FILE_RATIO = Gauge('small_file_ratio', 'Ratio of small files', ['dataset'])
PARTITION_COUNT = Gauge('partition_count', 'Partition count', ['dataset'])

start_http_server(9108)

while True:
    metrics = compute_layout_metrics()  # custom logic reading inventory snapshot
    for m in metrics:
        SMALL_FILE_RATIO.labels(m['dataset']).set(m['small_file_ratio'])
        PARTITION_COUNT.labels(m['dataset']).set(m['partition_count'])
    time.sleep(300)
```

### 12.2 Production Governance Platform (8–12 Weeks)
**Goal**: Continuous optimization—self-healing layout, proactive query rewriting, policy enforcement.

| Capability | Azure Component | OSS / Integration | Cost Payoff | Architect Pattern |
|------------|-----------------|-------------------|-------------|-------------------|
| Data Layout Orchestrator | Azure Kubernetes Service (AKS) microservice | Python / FastAPI | Automates compaction, format upgrade | Event-driven (new partition triggers layout policy) |
| Query Governance Engine | Azure Function pre-processor | Trino / Databricks hooks | Blocks wasteful queries | Inline rewriting (add column projection) |
| Cost Telemetry Pipeline | Event Hub ingest | Prometheus / Thanos | Central chargeback & anomaly detection | Multi-tenant tagging at ingestion |
| Lifecycle & Tiering | ADLS access logs + policy scheduler | Custom rule engine | Reduces hot tier footprint | SAS token policy enforcement |
| Metadata Health Jobs | ADF scheduled notebooks | Iceberg API / Spark | Maintains manifest hygiene | Snapshot expiration & rewrite cycle |
| Intelligent Compression Advisor | AKS model service | Python (scikit-learn) | Predict optimal compression | Feature: access frequency, decompress CPU, file size |
| Skew & Shuffle Optimizer | Spark listener plugin | Scala extension | Cuts long tail tasks | Adaptive rebalance threshold tuned by metrics |

**Microservice Sketch: Layout Orchestrator (FastAPI)**
```python
from fastapi import FastAPI
import subprocess, json

app = FastAPI()

@app.post('/layout/compact')
def compact(request: dict):
    table = request['table']
    partition = request['partition']
    target_size_mb = request.get('target_size_mb', 512)
    # Invoke Spark job via Databricks REST API or spark-submit
    submit_job(table, partition, target_size_mb)
    return {'status': 'submitted'}

@app.post('/layout/evaluate')
def evaluate(dataset: dict):
    metrics = compute_dataset_metrics(dataset['name'])
    actions = []
    if metrics['small_file_ratio'] > 0.2:
        actions.append({'action':'compact','partition':metrics['hottest_partition']})
    if metrics['avg_compression'] == 'SNAPPY' and metrics['cold_percent'] > 0.3:
        actions.append({'action':'reencode','level':6})
    return {'actions': actions}
```

**Query Rewriter (Presto/Trino)**
Pseudocode hook that intercepts user query:
```python
def rewrite_query(sql: str) -> str:
    if 'SELECT *' in sql.upper():
        # Analyze table schema and limit to top accessed columns
        columns = recommend_projection(sql)
        return sql.upper().replace('SELECT *', f"SELECT {','.join(columns)}")
    return sql
```

**Compression Advisor Model**
Features: `access_frequency`, `avg_scan_bytes`, `decompression_cpu_sec`, `current_compression`, `file_size_mb`.
Prediction: recommended compression tier (Snappy / ZSTD level 3 / ZSTD level 9).

```python
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(n_estimators=120)
X_train, y_train = load_training_data()
model.fit(X_train, y_train)

# Serve predictions
def recommend(features: dict):
    vec = to_vector(features)
    return model.predict([vec])[0]
```

Security & Governance Integrations:
- Use Managed Identities for AKS services accessing ADLS.
- RBAC: Only data platform service principal can trigger compaction.
- Policy-as-code: Store layout policies in Git; CI enforces schema for new datasets.

### 12.3 Minimal vs Production Comparison
| Aspect | Minimal Retrofit | Full Governance |
|--------|------------------|-----------------|
| File Management | Manual scheduled compaction | Event-driven + adaptive thresholds |
| Query Optimization | Reports (manual fixes) | Inline rewriting + blocking policies |
| Compression | Static tier rules | ML-driven dynamic recommendation |
| Telemetry Scope | Core metrics | Full lineage + chargeback tagging |
| Lifecycle | Basic age-based tiering | Access-pattern + business SLA aware |
| Risk | Human drift over time | Automated continuous enforcement |
| Savings Sustainment | Medium (plateaus) | High (continuous incremental gains) |

---

## 13. Case Studies (Azure & Open Source Adaptations)
(Values marked Illustrative unless publicly sourced.)

### Case Study 1: Streaming Retail Analytics (Inspired by Netflix Scan Reduction Concepts)
**Context**: Retail company on Azure struggling with rising Databricks cluster hours; raw JSON ingestion, frequent dashboard scans.

| Pain | Root Cause | Action | Result (Illustrative) | Key Lesson |
|------|------------|--------|-----------------------|------------|
| High cluster cost | Raw JSON full scans | Convert to Parquet + Snappy | 45% IO reduction | Columnar baseline first. |
| Slow dashboard load | SELECT * queries | Query rewriting + projections | p95 latency 12s → 5s | Enforce projection early. |
| Large small file count | 2MB micro-batches | Daily compaction 512MB target | Small file ratio 0.35 → 0.05 | Structured file sizing matters. |
| Cost unpredictability | No telemetry tagging | Add team tags + Prom metrics | Monthly variance -30% | Attribution drives accountability. |

### Case Study 2: Rider Demand Platform (Uber Shuffle Optimization Analogy)
**Context**: Real-time demand shaping job experiencing skew-induced spills on Azure Synapse Spark pools.

| Pain | Root Cause | Action | Result (Illustrative) | Key Lesson |
|------|------------|--------|-----------------------|------------|
| Long tail tasks | Skewed city_id partitions | Introduce salting + AQE | Job duration 40m → 26m | Adaptive execution + salting effective. |
| High spill bytes | Insufficient parallelism | Increase shuffle partitions (dynamic) | Spill GB 120 → 35 | Monitor task metrics continuously. |
| Recompute overhead | Failed skew tasks | Retry with dynamic repartition | Failure rate 8% → 1% | Resilience reduces waste. |

### Case Study 3: Hospitality Booking (Airbnb Partition Lifecycle Analogy)
**Context**: Excess storage spend retaining hot-tier data older than 1 year; over-partitioning by city+date.

| Pain | Root Cause | Action | Result (Illustrative) | Key Lesson |
|------|------------|--------|-----------------------|------------|
| Storage bloat | No tiering policy | Apply lifecycle to Cool/Archive | Hot tier GB 500 → 300 | Aggressive tiering safe after 90d. |
| Partition explosion | city_id + date partitions | Replace with DATE + hashed_city bucket | Partition count 250K → 12K | Hash/bucket for high-cardinality. |
| Planning latency | Massive manifest listing | Weekly manifest rewrite (Iceberg) | Planning p95 4.2s → 1.1s | Metadata hygiene mandatory. |
| Limited visibility | Missing dataset usage stats | Implement access logging | Dropped 38% unused datasets | Usage telemetry justifies cleanup. |

### Case Study 4: SaaS Metrics Platform (Snowflake Credit Control Analogy on Azure Stack)
**Context**: Trino + Spark lakehouse; cost creep due to unbounded large analytical scans.

| Pain | Root Cause | Action | Result (Illustrative) | Key Lesson |
|------|------------|--------|-----------------------|------------|
| High compute hours | Broad SELECT * queries | Add columnar semantic views | Scan bytes -30% | Semantic abstraction curbs misuse. |
| Unused aggregates | Legacy ETL tables | Usage audit + retire | Storage TB 120 → 82 | Delete or re-aggregate. |
| CPU cost per query | Heavy GZIP decompression | Re-encode hot partitions to Snappy | CPU/time -22% | Compression aligned to workload. |
| Siloed cost ownership | No team tagging | Query tagging → chargeback reports | Team-level optimization adoption | Cultural change accelerates savings. |

### Case Study 5: IoT Telemetry Platform (Edge Event Flood Control)
**Context**: Billions of device events daily; early-stage cost runaway in ADLS and Spark.

| Pain | Root Cause | Action | Result (Illustrative) | Key Lesson |
|------|------------|--------|-----------------------|------------|
| Small file storm | Per-device direct writes | Buffer aggregator → batch writes | File count/day 2M → 120K | Buffer layer essential at scale. |
| High ingestion latency | GZIP device compression | Switch to LZ4 for ingest, ZSTD downstream | Ingest CPU -35% | Multi-phase compression pipeline. |
| Inefficient joins | Wide device dimension scans | Precompute dimension subset cache | Join latency 18s → 6s | Cache hot dimensions strategically. |
| Cold data on hot tier | Uniform retention | Tier policies (30d → Cool, 180d → Archive) | Hot GB 400 → 190 | Lifecycle enforcement immediate win. |

---

## 14. Interview Question Bank (Cost Optimization Focus)

### Category A: Fundamentals
1. Explain why columnar formats reduce query cost compared to row-based storage.
2. What is the small file problem and how does it manifest in Spark planning time?
3. How do predicate pushdown and column pruning differ? Give an example of each.
4. Why might you choose Snappy over ZSTD or vice versa? Consider workload patterns.

### Category B: Architecture & Strategy
5. Design a cost-aware ingestion pipeline for an Azure data lake receiving 10B events/day.
6. Propose a lifecycle policy for a mixed workload (hot analytics + archival compliance) with access metrics.
7. How would you introduce Iceberg into an existing Parquet lake without unlocking a massive refactor cost?
8. Outline a governance system that prevents runaway SELECT * queries across Trino and Spark.

### Category C: Troubleshooting & Scenarios
9. A critical dashboard query suddenly doubles scan bytes overnight. Walk through your diagnostic steps.
10. Planning latency for a key table increased from 500ms to 4s. Possible causes and remediation?
11. A compaction job improved file sizes but query times did not drop—what hypotheses do you test?
12. Shuffle spills spike after enabling new partition strategy—what metrics and root causes do you examine?

### Category D: Principal-Level Trade-Offs
13. You can save 10% storage by re-encoding hot data to ZSTD level 9 but at +25% CPU latency cost—justify decision.
14. Engineering suggests adding bloom filters to 30 columns; evaluate cost/benefit and propose a selective strategy.
15. A proposal aims to materialize 15 new aggregates daily for potential future analytics. How do you evaluate ROI?
16. A team wants to partition by customer_id to "speed up queries". Provide a principled alternative and its trade-offs.

### Category E: Optimization Economics
17. Explain how you would build a chargeback system mapping scan cost to teams with tagging and telemetry.
18. Present a framework for prioritizing cost initiatives—what dimensions and scoring formula do you use?
19. Quantify the impact of reducing small file ratio from 0.30 to 0.05 on planning and IO (illustrative reasoning).
20. How do you balance cost optimization with innovation velocity for data science teams needing flexibility?

### Example Principal-Level Answer (Q13)
"Re-encoding hot partitions from Snappy to ZSTD level 9 for 10% extra storage savings yields marginal direct dollar savings relative to the added CPU overhead. For interactive queries with p95 < 3s SLA, raising decompression CPU by 25% risks SLA breach and cluster scaling. Unless we pair it with reduced compute sizing or prove net cost drop after holistic benchmarking (storage savings vs increased compute), I defer and adopt a hybrid: ZSTD level 5 for warm partitions (last accessed >7 days) while keeping Snappy for sub-7-day hot partitions. We'll revisit with monthly access frequency regression modeling."

### Red Flag Answer Patterns
| Question | Red Flag |
|----------|----------|
| Small file problem | "Just increase cluster size" (Avoids root cause) |
| Predicate pushdown | "It's automatic so we don't need to do anything" |
| Compression choice | "Always use ZSTD it's smaller" (Ignores CPU trade-off) |
| Partition strategy | "Partition by every dimension we filter on" |
| Chargeback | "Tagging is optional" |

### High-Signal Follow-Ups
Interviewers may probe:
- "How do you prevent optimization from becoming premature complexity?"
- "Explain your rollback strategy if a compaction job corrupts manifests."
- "How do you quantify value of dropping unused datasets?"

---

## ✅ Sections 12–14 Complete Summary
- Two implementation tracks (minimal vs full governance) tuned to Azure + OSS components.
- Concrete microservice + query rewriting pseudocode patterns.
- Five adapted case studies (retail, rider demand, hospitality, SaaS metrics, IoT telemetry) with knowledge transfer from public domain patterns.
- 20 progressive interview questions with principal-level reasoning example and red flag pattern table.

Next (Part 3 Sections 15–27): Labs, Benchmarks Deep Dive (format/compression/partition experiments), Anti-Patterns, Migration Roadmaps, Checklists, KPI/SLO Cost Playbook, Cloud Pricing (Azure-specific SKUs), Terraform/Azure Bicep sketch, Reference Configs, Extension Ideas (ML compression advisor), Glossary, Citations, Summary Matrix.
