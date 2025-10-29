# Cost Optimization for Data Platforms - Part 3 (Sections 15–27)

## 15. Hands-On Labs (Progressive Azure + OSS)

### Lab 1: Format Conversion & Baseline Measurement (45 min)
Objective: Convert CSV → Parquet and measure scan byte reduction in Spark (Databricks or local).

Steps:
1. Ingest raw CSV sample to ADLS.
2. Convert to Parquet with Snappy.
3. Run identical filter + aggregation query; measure scanned bytes.
4. Store metrics in a simple Parquet metrics table.

Code (PySpark):
```python
raw = spark.read.option('header','true').csv('abfss://raw@acct.dfs.core.windows.net/transactions/')
parq = raw.repartition(16).write.mode('overwrite').parquet('abfss://silver@acct.dfs.core.windows.net/transactions/')

# Query baseline
import time
start = time.time()
raw.filter("amount > 100").groupBy('country').count().collect()
raw_elapsed = time.time() - start

start = time.time()
spark.read.parquet('abfss://silver@acct.dfs.core.windows.net/transactions/').filter("amount > 100").groupBy('country').count().collect()
parq_elapsed = time.time() - start

spark.createDataFrame([
    ('format_conversion', raw_elapsed, parq_elapsed)
], ['experiment','csv_seconds','parquet_seconds']).write.mode('append').parquet('abfss://metrics@acct.dfs.core.windows.net/benchmarks/')
```
Expected: Parquet query 30–60% faster (Illustrative).

---

### Lab 2: Small File Compaction Automation (60 min)
Objective: Build a script detecting small files and scheduling compaction.

Detection Script:
```python
from azure.storage.filedatalake import DataLakeServiceClient
import os, math

THRESHOLD_MB = 64
service = DataLakeServiceClient(account_url=f"https://{os.getenv('ACCOUNT')}.dfs.core.windows.net", credential=os.getenv('SAS'))
fs = service.get_file_system_client('silver')

small_files = {}
for path in fs.get_paths(recursive=True):
    if path.is_directory: continue
    size_mb = path.content_length / (1024*1024)
    if size_mb < THRESHOLD_MB:
        day = extract_partition(path.name)
        small_files.setdefault(day, 0)
        small_files[day] += 1

print(small_files)
```
Trigger compaction for partitions with >200 small files.

Compaction Job (spark-submit):
```python
for day, count in small_files.items():
    if count > 200:
        df = spark.read.parquet(f"abfss://silver@acct.dfs.core.windows.net/transactions/event_date={day}")
        df.repartition(64).write.mode('overwrite').parquet(f"abfss://silver@acct.dfs.core.windows.net/transactions/event_date={day}")
```
Success Criteria: Small file ratio < 0.10 for last 30 days.

---

### Lab 3: Query Governance (90 min)
Objective: Implement a lightweight query interceptor replacing SELECT * with projected columns.

Approach: Wrap Trino REST interface with a proxy.

Proxy (FastAPI):
```python
from fastapi import FastAPI, Request
import httpx, re

TRINO_ENDPOINT = 'https://trino.company.com/v1/statement'
app = FastAPI()

SELECT_STAR_PATTERN = re.compile(r'SELECT\s+\*', re.IGNORECASE)

@app.post('/query')
async def submit_query(request: Request):
    body = await request.body()
    sql = body.decode()
    if SELECT_STAR_PATTERN.search(sql):
        columns = recommend_columns(sql)  # Implement heuristics or static mapping
        sql = SELECT_STAR_PATTERN.sub(f"SELECT {','.join(columns)}", sql)
    async with httpx.AsyncClient() as client:
        r = await client.post(TRINO_ENDPOINT, content=sql)
        return r.text
```

Record rewrite events to metrics store for adoption tracking.

---

### Lab 4: Compression Tiering (75 min)
Objective: Implement a scheduled job re-encoding cold Parquet partitions from Snappy → ZSTD level 6.

Script:
```python
import pyarrow.parquet as pq, pyarrow as pa
from datetime import datetime, timedelta
import os

COLD_DAYS = 30
root = '/mnt/silver/transactions/'

for partition_path in list_partitions(root):
    last_access = get_last_access(partition_path)
    if (datetime.utcnow() - last_access).days > COLD_DAYS:
        table = pq.read_table(partition_path)
        pq.write_table(table, partition_path, compression='zstd', compression_level=6)
        log_reencode(partition_path)
```
Metrics: `reencoded_partitions_total`.

---

### Lab 5: Planning Latency & Manifest Hygiene (60 min)
Objective: Measure planning time pre/post Iceberg manifest rewrite.

Before:
```sql
CALL system.current_snapshot('sales_table');
-- Run timing on SELECT with predicate filters
```
Rewrite:
```sql
CALL system.expire_snapshots('sales_table', TIMESTAMP '2024-09-01 00:00:00');
CALL system.rewrite_manifests('sales_table');
```
After: Re-measure planning latency (compare p95).

Expected: p95 planning latency drop 30–60% when manifest bloat existed.

---

## 16. Deep Benchmark Suite (Expanded)
Design: Matrix comparing (Format × Compression × Partition Strategy × Engine).

Dimensions:
- Formats: Parquet (baseline), ORC, Parquet+Iceberg
- Compression: Snappy, ZSTD lvl3, ZSTD lvl9
- Partition Strategy: Date only, Date + Hash(user_id, 64), Over-partition (Date + country + city_id)
- Engines: Spark 3.5, Trino 432, Databricks Runtime, Azure Synapse Spark

Metrics:
| Metric | Reason |
|--------|--------|
| Scan Bytes | Direct IO traffic |
| Planning Time | Metadata overhead |
| CPU/Task | Compression + vectorization efficiency |
| Shuffle Spill Bytes | Execution plan health |
| Output/Scan Ratio | Query selectivity |
| Small File Ratio | Layout quality |
| Manifest Count | Iceberg metadata scaling |

Benchmark Orchestrator (Outline):
```python
SCENARIOS = [
    {'format':'parquet','compression':'snappy','partition':'date'},
    {'format':'parquet','compression':'zstd3','partition':'date_hash'},
    {'format':'orc','compression':'zstd3','partition':'date'},
    {'format':'iceberg','compression':'snappy','partition':'date_hash'}
]

for s in SCENARIOS:
    prepare_dataset(s)
    for engine in ['spark','trino']:
        metrics = run_query_suite(engine, s)
        persist_metrics(s, engine, metrics)
```

Query Suite Examples:
```sql
-- High selectivity
SELECT country, COUNT(*) FROM transactions WHERE amount > 500 GROUP BY country;
-- Low selectivity
SELECT AVG(amount) FROM transactions;
-- Join pattern
SELECT t.country, SUM(t.amount) FROM transactions t JOIN dim_country c ON t.country = c.code GROUP BY t.country;
```

Report Template:
| Scenario | Engine | Scan GB | Plan ms | CPU sec | Spill GB | Output/Scan | Notes |
|----------|--------|---------|---------|---------|----------|-------------|-------|

Interpretation Patterns:
- High scan + low output/scan → add zone maps or refine partition.
- High planning time + Iceberg → manifest rewrite.
- High spill with hash partition strategy → adjust bucket count or enable AQE.

---

## 17. Anti-Patterns (Cost Focus)

| Anti-Pattern | Example | Cost Impact | Better Practice |
|--------------|---------|-------------|----------------|
| Blind SELECT * | Dashboards loading entire wide table | High scan bytes | Semantic views with projected columns |
| Partition By High Cardinality | `PARTITION BY user_id` | Metadata explosion | Use bucketing/hash + date partition |
| No Compaction After Streaming | Millions of <10MB files | Planning latency; wasted IO | Daily/Hourly compaction with size policy |
| Overuse of GZIP | All tables GZIPed | CPU decompression tax | Tiered compression: Snappy/ZSTD policy |
| Large Static Aggregates Unused | Materialize daily snapshot never queried | Storage bloat | Usage audit & TTL purging |
| Ignoring Skew | One partition 10× larger | Long tail tasks, spill | Salting/adaptive repartition |
| Unbounded Delta/Iceberg Snapshots | Thousands of snapshots | Planning slowdown | Scheduled snapshot expiration |
| Mixed Hot/Cold in Same Path | Old + new data in hot tier | Extra $ per GB-month | Age-based path tiering |
| Manual Query Optimization Only | Human-driven patching | Drift; missed patterns | Automated rewriting + linter |
| Hardcoding Partition Count | Fixed 200 partitions forever | Suboptimal parallelism | Dynamic partition sizing using histograms |

---

## 18. Migration / Evolution Roadmap

| Phase | Legacy State | Target Improvement | Tactics | Duration |
|-------|--------------|--------------------|---------|----------|
| 0 Assessment | Raw CSV/JSON everywhere | Visibility baseline | Inventory + metrics | 1–2 weeks |
| 1 Columnar Adoption | Selective Parquet only | 60%+ columnar coverage | Batch re-encoding jobs | 2–4 weeks |
| 2 Layout Control | Small file flood | File size normalization | Compaction orchestrator | 3–5 weeks |
| 3 Governance Enablement | Manual queries | Automated projection & blocking | Query proxy / linter | 4–6 weeks |
| 4 Metadata Management | Growing manifests | Stable planning | Snapshot expiration cycles | 2 weeks recurring |
| 5 Dynamic Optimization | Static compression & partition | Adaptive cost intelligence | ML advisor + auto actions | 8–12 weeks |

Rollback Strategy: Each phase reversible—retain original raw zone for reprocessing (Bronze). Metadata changes (Iceberg manifests) versioned—rollback via previous snapshot ID.

Decision Gates: Exit criteria must include measured cost delta and SLA compliance (latency, freshness).

---

## 19. Checklists (Cost Engineering Governance)

### 19.1 Design Readiness
- [ ] Dataset access patterns analyzed (scan frequency, row selectivity).
- [ ] Partition key chosen: time + limited dimension or bucketing strategy approved.
- [ ] File size policy defined (target size range & compaction trigger threshold).
- [ ] Compression tier rules documented (hot ≤7d Snappy, warm 8–30d ZSTD3, cold >30d ZSTD6).
- [ ] Lifecycle age thresholds mapped to ADLS tiers (Hot/Warm/Cool/Archive).
- [ ] Query governance patterns selected (projection rewriting, max scan guards).
- [ ] Telemetry schema (metrics, tags) finalized.
- [ ] Rollback path documented (Bronze zone raw retention).
- [ ] SLA interplay validated (latency vs cost trade-off modeled).

### 19.2 Launch Readiness
- [ ] Benchmark suite executed (baseline metrics captured).
- [ ] Compaction job dry-run on sample partitions.
- [ ] Query proxy tested with edge queries (regex corner cases).
- [ ] Access tagging integrated (team/project propagation).
- [ ] Alert rules deployed (small_file_ratio, scan_bytes growth rate).
- [ ] Cost dashboard published (daily cost/time graphs).
- [ ] Security review passed (Managed Identities, RBAC, KMS encryption).

### 19.3 Ongoing Operations
- [ ] Weekly: Snapshot expiration & manifest rewrite metrics reviewed.
- [ ] Monthly: Stale dataset purge list generated and actioned.
- [ ] Quarterly: Partition strategy re-evaluation (histogram drift).
- [ ] Continual: Query rewrite hit ratio tracked (>30% indicates improvement potential).
- [ ] Annual: Compression policy recalibration (hardware changes, new algorithms).

---

## 20. KPI / SLO Cost Playbook

| KPI | Formula | Target | Interpretation |
|-----|---------|--------|----------------|
| Scan Efficiency | output_rows / scanned_rows | >0.10 | Low ratio → poor pruning or SELECT * |
| Small File Ratio | small_files / total_files | <0.15 | >0.25 triggers compaction scaling |
| Planning Latency p95 | p95(planning_ms) | <1500ms | High → manifest or metadata bloat |
| Compression CPU Share | decompress_cpu / total_cpu | <0.25 | Excess → misaligned compression policy |
| Storage Hot Tier % | hot_tier_bytes / total_bytes | <0.55 | Exceeds → apply lifecycle |
| Snapshot Count | active_snapshots | <500 major tables | High → expiration backlog |
| Chargeback Visibility | tagged_queries / total_queries | >0.95 | Low adoption → fix tagging |
| Query Rewrite Rate | rewritten_queries / SELECT_*_queries | >0.60 | Low → refine rewriting heuristics |

SLO Examples:
- 99% of queries plan <2s.
- Small file ratio per table remains <0.20 weekly average.
- Lifecycle policy shifts ≥95% of >180d data to Archive tier.

Alert Example (PromQL):
```
(rate(data_scan_bytes_total[1h]) / rate(output_rows_total[1h]) > 50) AND on(table) (small_file_ratio > 0.25)
```
Combined Condition: High scan inefficiency AND layout issue.

---

## 21. Azure Pricing Integration (Illustrative Modeling)

Pricing Dimensions (Illustrative—check current Azure pricing docs):
| Component | Metric | Hot | Cool | Archive |
|-----------|--------|-----|------|---------|
| ADLS (GB-month) | Storage | $0.020 | $0.010 | $0.002 |
| Read Operations | 10K ops | $0.10 | $0.10 | $0.15 |
| Write Operations | 10K ops | $0.10 | $0.10 | $0.15 |

Example Monthly Cost Model:
```
Hot_bytes = 300 TB
Cool_bytes = 200 TB
Archive_bytes = 100 TB
Cost = 300*0.020 + 200*0.010 + 100*0.002 = $6,000 + $2,000 + $200 = $8,200
Without tiering (all hot): (300+200+100)*0.020 = $12,000 → Savings: $3,800/month
```

Databricks DBU Model (Simplified):
If optimization reduces avg cluster runtime from 18h/day to 12h/day at 10 DBU/hr and $0.30/DBU:
```
Before: 18h * 10 * 0.30 * 30 = $1,620/month
After: 12h * 10 * 0.30 * 30 = $1,080/month → $540/month saved
```

Chargeback Table Sample:
| Team | Scan TB (Month) | CPU Hours | Cost Attribution ($) | Optimization Flag |
|------|-----------------|-----------|----------------------|-------------------|
| Marketing | 120 | 450 | 4,800 | SELECT * heavy |
| Data Science | 80 | 600 | 5,200 | High compression CPU |
| Product Analytics | 45 | 310 | 2,700 | Healthy |
| Ad Platform | 150 | 520 | 6,300 | Skew / spill alerts |

---

## 22. Infra-as-Code (Terraform + Bicep Sketch)

### Terraform (Azure Resources)
```hcl
resource "azurerm_resource_group" "rg" {
  name     = "data-platform-rg"
  location = "eastus"
}

resource "azurerm_storage_account" "datalake" {
  name                     = "companydatalakeacct"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = true  # Hierarchical namespace for ADLS Gen2
}

resource "azurerm_container_group" "prometheus" {
  name                = "prometheus-metrics"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  ip_address_type     = "Public"
  os_type             = "Linux"
  container {
    name   = "prometheus"
    image  = "prom/prometheus:latest"
    cpu    = "1"
    memory = "2"
    ports { port = 9090 }
  }
}

resource "azurerm_eventhub_namespace" "eh_ns" {
  name                = "cost-telemetry-ns"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "Standard"
}

resource "azurerm_eventhub" "telemetry" {
  name                = "query-cost-events"
  namespace_name      = azurerm_eventhub_namespace.eh_ns.name
  resource_group_name = azurerm_resource_group.rg.name
  partition_count     = 4
  message_retention   = 7
}

resource "azurerm_container_registry" "acr" {
  name                = "companyacrregistry"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = true
}
```

### Bicep Snippet (Layout Orchestrator AKS)
```bicep
param location string = 'eastus'
param rgName string = 'data-platform-rg'

resource aks 'Microsoft.ContainerService/managedClusters@2023-05-01' = {
  name: 'layout-optimizer-aks'
  location: location
  sku: {
    name: 'Basic'
    tier: 'Free'
  }
  properties: {
    kubernetesVersion: '1.28.3'
    dnsPrefix: 'layout-optimizer'
    agentPoolProfiles: [
      {
        name: 'system'
        count: 3
        vmSize: 'Standard_D4_v5'
        osType: 'Linux'
        mode: 'System'
      }
    ]
    enableRBAC: true
  }
}
```

---

## 23. Reference Configurations

### Spark Config (Cost Optimization Focus)
```properties
spark.sql.files.maxPartitionBytes=256m
spark.sql.files.openCostInBytes=4194304
spark.sql.adaptive.enabled=true
spark.sql.adaptive.skewJoin.enabled=true
spark.sql.parquet.filterPushdown=true
spark.sql.parquet.mergeSchema=false
spark.sql.autoBroadcastJoinThreshold=104857600  # 100MB
spark.sql.shuffle.partitions=512  # dynamic adjust after metrics
spark.databricks.delta.retentionDurationCheck.enabled=true  # if Delta used
```

### Trino Config (etc/config.properties)
```properties
coordinator=true
node-scheduler.include-coordinator=false
http-server.http.port=8080
query.max-memory=40GB
query.max-memory-per-node=8GB
query.max-total-memory-per-node=16GB
optimizer.join-reordering-strategy=AUTOMATIC
optimizer.optimize hash generation=true
optimizer.pushdown-subfields=true
experimental.pushdown-dereference=true
task.writer-count=8
```

### Prometheus Alert Rules (Cost Signals)
```yaml
groups:
  - name: cost_signals
    interval: 1m
    rules:
      - alert: SmallFileRatioHigh
        expr: small_file_ratio > 0.25
        for: 15m
        labels:
          severity: warning
        annotations:
          description: "Small file ratio high for {{ $labels.dataset }}"
      - alert: ScanEfficiencyLow
        expr: rate(data_scan_bytes_total[5m]) / rate(output_rows_total[5m]) > 100
        for: 10m
        labels:
          severity: critical
      - alert: PlanningLatencyElevated
        expr: histogram_quantile(0.95, planning_latency_ms_bucket) > 2000
        for: 10m
        labels:
          severity: warning
```

---

## 24. Extension Ideas

| Idea | Description | Value |
|------|-------------|-------|
| ML Partition Advisor | Train model to suggest partition + bucket strategy based on histograms | Prevent mis-partition upfront |
| Skew Predictor | Real-time detection using distribution Gini coefficient pre-shuffle | Preempt costly spills |
| Compression Auto-Tuner | Adjust compression by rolling access + CPU stats | Continuous optimization |
| Query Pattern Classifier | Tag queries (exploratory vs dashboard vs batch) for cost routing | SLA-aware resource allocation |
| Code Linter for SQL | Static analysis in CI to block SELECT * merges | Prevent drift before deploy |
| Cold Data Snapshotter | Weekly summary stats before archival to ease future rare forensic queries | Reduce future rehydrate cost |

ML Skew Predictor Sketch:
```python
import numpy as np

def skew_gini(counts):
    counts = np.array(sorted(counts))
    n = len(counts)
    cum = np.cumsum(counts)
    return (n + 1 - 2 * np.sum(cum / cum[-1])) / n

# If Gini > 0.6 trigger salting
```

---

## 25. Glossary (Cost-Specific Terms)
| Term | Definition | Principal Insight |
|------|------------|-------------------|
| Small File Problem | High volume of undersized files causing metadata & planning overhead | Fix early; compaction baseline for all optimization. |
| Predicate Pushdown | Filter evaluation at storage layer using stats | Stats corruption destroys savings; monitor effectiveness. |
| Column Pruning | Reading only requested columns | Semantic view design amplifies benefit. |
| Manifest | Metadata file referencing data files (Iceberg) | Bloats linearly with snapshots; schedule rewrite. |
| Snapshot Expiration | Removing old table versions | Reduces planning latency, lower metadata storage. |
| Compression Tiering | Assign compression based on access patterns | Must maintain access telemetry—no telemetry, no tiering. |
| Lifecycle Policy | Automated data tier movement by age/access | Implement guardrails to avoid premature archival. |
| Query Selectivity | Output rows / scanned rows | Low selectivity → layout or query projection issue. |
| Skew | Uneven distribution of work across tasks | Causes spill cost and long tails; measure Gini. |
| Chargeback | Attributing resource cost to teams | Drives behavioral optimization. |
| Zone Map | Min/max metadata for block skipping | Lightweight data skipping; evaluate column entropy. |
| Bloom Filter Index | Probabilistic membership index | Use sparingly—build cost vs query frequency trade-off. |
| Adaptive Execution | Runtime plan adjustments (Spark AQE) | Requires fresh stats to remain effective. |
| Bucketing | Fixed number of hash partitions for a column | Stabilizes join performance; needs periodic re-evaluation. |

---

## 26. Citations / Further Reading
1. Apache Parquet Documentation: https://parquet.apache.org/
2. Apache Iceberg Spec: https://iceberg.apache.org/
3. Trino Query Optimization Guide: https://trino.io/docs/current/optimizer
4. Spark Adaptive Query Execution: https://spark.apache.org/docs/latest/sql-performance-tuning.html
5. Delta Lake Docs (compaction & vacuum concepts analogous): https://docs.delta.io/
6. Azure Data Lake Storage Pricing: https://azure.microsoft.com/pricing/details/storage/data-lake/
7. Databricks Performance Best Practices: https://docs.databricks.com/
8. Zstandard Compression Whitepaper: https://facebook.github.io/zstd/
9. Netflix Tech Blog (cost & efficiency themes): https://netflixtechblog.com/
10. Uber Engineering Blog (query optimization & Spark improvements): https://eng.uber.com/
11. Airbnb Engineering Blog (data platform evolution): https://medium.com/airbnb-engineering
12. Trino/Presto Con Conference Talks (metadata & performance) – YouTube

---

## 27. Summary Knowledge Matrix

### Beginner
- Understand columnar vs row cost impact.
- Explain small file problem.
- Pick basic partition key (date).
- Use Snappy compression sensibly.

### Intermediate
- Implement compaction job.
- Measure scan efficiency & planning latency.
- Add query rewriting for SELECT *.
- Design lifecycle policy with hot/warm/cold tiers.

### Advanced
- Evaluate Parquet vs ORC vs Iceberg trade-offs by workload.
- Engineer dynamic compression tiering pipeline.
- Optimize skew via salting + AQE metrics.
- Build benchmark harness across formats.

### Principal
- Architect governance platform (layout orchestrator + query linter + telemetry).
- Quantify ROI for optimization initiatives via cost model.
- Negotiate trade-offs (CPU vs compression savings vs SLA risk).
- Drive cultural adoption (chargeback + dashboards). 
- Present phased migration with rollback safeguards.

---

## ✅ Module Completion Checklist (Cost Optimization)
- [x] Sections 0–11 (Foundations & Architecture)
- [x] Sections 12–14 (Implementation Tracks + Case Studies + Interview Bank)
- [x] Sections 15–27 (Labs, Benchmarks, Anti-Patterns, Migration, Checklists, KPI/SLO, Pricing, IaC, Configs, Extensions, Glossary, Citations, Knowledge Matrix)

Quality Gates:
- Realistic vs Illustrative metrics clearly distinguished.
- No claims of proprietary internal numbers.
- Multi-cloud aspects trimmed in favor of Azure + OSS emphasis.
- Principal-level depth (strategy + rollback + governance).

---

## Suggested 3-Week Study / Build Plan
Week 1: Labs 1–3 + read Parts 1–2.
Week 2: Labs 4–5 + implement minimal retrofit in a sandbox.
Week 3: Build benchmark harness + rehearse interview questions.

---

**Next Recommended Module**: Cloud & Service Mapping (AWS ↔ Azure ↔ GCP equivalence / managed vs OSS trade-offs) or Security & Compliance—choose based on gap priority.

**Last Updated**: October 30, 2025  
**Version**: 1.0  
**Estimated Study Time**: 18–22 hours  
**Maintainer**: Avaire Learning Resources
