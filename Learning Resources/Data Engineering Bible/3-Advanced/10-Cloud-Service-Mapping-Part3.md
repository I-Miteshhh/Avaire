# Cloud & Service Mapping - Part 3 (Sections 15–27)

## 15. Hands-On Labs (Roadmap Technologies Only)

### Lab 1: Iceberg Catalog Dual-Registration (45 min)
Objective: Register the same Iceberg table in two catalogs (e.g., Hive Metastore on AWS EMR and Nessie/Glue equivalent on secondary cloud) and validate snapshot hash parity.

Steps:
1. Create Iceberg table on primary (Spark):
```scala
spark.sql("CREATE TABLE sales_iceberg (order_id BIGINT, amount DOUBLE, country STRING, event_date DATE) USING ICEBERG PARTITIONED BY (event_date)")
```
2. Insert sample data.
3. Export snapshot metadata hash:
```scala
val meta = spark.sql("SELECT * FROM sales_iceberg.snapshots ORDER BY committed_at DESC LIMIT 1")
meta.show(false)
```
4. Replicate data files + metadata (`metadata/*.json`, `manifest/*.avro`) to secondary cloud storage bucket.
5. Register table in secondary catalog referencing same location.
6. Query parity harness:
```scala
val primaryAgg = spark.sql("SELECT country, SUM(amount) FROM sales_iceberg GROUP BY country ORDER BY country")
// Secondary environment run same query; compare row sets & sums
```
Success: Row-level parity; snapshot id identical.

### Lab 2: Hudi vs Iceberg Mutation Cost (90 min)
Objective: Measure update latency and file operation counts for upsert workload under Hudi Merge-On-Read vs Iceberg copy-on-write.

Dataset: 10M user profile rows; 100K daily updates.

Benchmark Skeleton:
```scala
val updates = spark.read.parquet("updates/day=2024-10-30")
// Hudi upsert
updates.write.format("hudi")
  .option("hoodie.table.name","user_profiles_hudi")
  .option("hoodie.datasource.write.operation","upsert")
  .mode("append").save("/lake/hudi/user_profiles")
// Iceberg rewrite (simulate update via overwrite of affected partitions)
val base = spark.read.table("user_profiles_iceberg")
val merged = base.join(updates, Seq("user_id"), "left_semi") // refine logic
merged.writeTo("user_profiles_iceberg").overwritePartitions()
```
Metrics: Write duration, number of file groups touched, compaction backlog.
Outcome: Hudi MOR lower latency for sparse updates; Iceberg full partition rewrite costlier.

### Lab 3: Beam Portable Pipeline Parity (60 min)
Objective: Run identical Beam pipeline on two runners (Spark vs Flink) and compare windowed aggregation outputs.

Pipeline Sketch (Python):
```python
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

class ParseEvent(beam.DoFn):
    def process(self, line):
        fields = line.split(',')
        yield {
            'user_id': fields[0],
            'amount': float(fields[1]),
            'ts': fields[2]
        }

with beam.Pipeline(options=PipelineOptions()) as p:
    (p
     | beam.io.ReadFromText('events.csv')
     | beam.ParDo(ParseEvent())
     | beam.Map(lambda e: (e['user_id'], e['amount']))
     | beam.WindowInto(beam.window.FixedWindows(60))
     | beam.CombinePerKey(sum)
     | beam.io.WriteToText('out'))
```
Run on Spark runner vs Flink runner; compare outputs. Check watermark instrumentation (optional logs) for drift.

### Lab 4: Kafka MirrorMaker Lag Dashboard (60 min)
Objective: Instrument replication lag metrics, display in Grafana.

Lag Exporter:
```python
from prometheus_client import Gauge, start_http_server
import time, kafka

LAG = Gauge('mirror_lag_seconds', 'Replication lag seconds', ['topic','partition'])
start_http_server(9109)

while True:
    for tp in get_topic_partitions():
        source_end = get_source_end_offset(tp)
        target_end = get_target_end_offset(tp)
        lag = compute_lag_seconds(source_end, target_end)
        LAG.labels(tp.topic, tp.partition).set(lag)
    time.sleep(5)
```
Grafana Panels: p95 lag per topic, top partitions by lag.

### Lab 5: Airflow → Dagster Asset Migration (90 min)
Objective: Convert a legacy Airflow DAG to Dagster assets preserving lineage.

Airflow DAG snippet:
```python
from airflow import DAG
from airflow.operators.python import PythonOperator

def extract(): ...
def transform(): ...
def load(): ...
```
Dagster Assets:
```python
from dagster import asset

@asset(metadata={"partition":{"daily":True}})
def raw_events(): ...

@asset(deps=[raw_events])
def cleaned_events(raw_events): ...

@asset(deps=[cleaned_events])
def fact_sales(cleaned_events): ...
```
Validation: Generate lineage graph; confirm dependency chain matches original DAG topology.

### Lab 6: Schema Compatibility Gate (45 min)
Objective: Implement compatibility matrix test for Avro schemas before replication.

Matrix Implementation (Python):
```python
def diff(old, new): ...

def is_backward_compatible(changes):
    for c in changes:
        if c.type in ['remove_field','rename_field','narrow_type']:
            return False
    return True
```
Integrate into Airflow pre-replication task.

### Lab 7: Query Parity Harness (60 min)
Objective: Compare BigQuery vs Redshift aggregate results referencing Iceberg external tables.

Steps:
1. Define canonical queries list.
2. Execute queries both sides; collect results.
3. Compute relative difference per metric.

Harness Pseudocode:
```python
queries = ["SELECT country, SUM(amount) amt FROM sales WHERE event_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) GROUP BY country"]
for q in queries:
    bq_res = run_bigquery(q)
    rs_res = run_redshift(q)
    compare(bq_res, rs_res)
```
Success: All differences <0.1%.

---

## 16. Expanded Benchmark Suite

Benchmarks Aligned to Interoperability Dimensions:
| Benchmark | Metric | Tool | Purpose |
|-----------|-------|------|---------|
| Metadata Sync | latency_seconds | Script + catalog API | Snapshot propagation speed |
| Replication Lag | lag_seconds p95 | Prometheus (MirrorMaker) | Event freshness cross-cloud |
| Format Mutation | update_latency_ms | Spark metrics | Upsert cost trade-offs |
| Runner Parity | output_diff_pct | Beam pipeline checker | Semantic correctness across runners |
| Query Parity | diff_pct | Parity harness | Warehouse consistency |
| Manifest Health | manifest_file_count | Iceberg API | Planning cost predictor |

Sample Benchmark Driver:
```python
SCENARIOS = [
  {'table':'sales','format':'iceberg','mutation_type':'append'},
  {'table':'user_profiles','format':'hudi','mutation_type':'upsert'}
]
for s in SCENARIOS:
    start = now()
    perform_mutation(s)
    dur = now() - start
    record('update_latency_ms', dur*1000, labels=s)
```

Reporting Table:
| Scenario | Format | Mutation | Latency ms | File Ops | Manifest Count | Notes |
|----------|--------|----------|-----------|----------|----------------|-------|

Interpretation:
- High latency for Iceberg upsert → consider Hudi for entity changes.
- Large manifest count growth → schedule rewrite.

---

## 17. Anti-Patterns (Cloud Mapping)
| Anti-Pattern | Description | Impact | Correction |
|--------------|-------------|--------|-----------|
| Lowest Common Denominator API | Hiding advanced features (e.g., Iceberg partition evolution) | Lost performance & innovation | Provide escape hatches (vendor-specific extensions) |
| Over-Replication | Replicating all topics/tables indiscriminately | Egress cost spike | Usage-driven selection + pruning |
| Format Sprawl | Adding formats without workload justification | Operational complexity | Formal format selection policy (append vs upsert) |
| Unbounded Snapshot Retention | Never expiring Delta/Iceberg snapshots | Planning latency, storage bloat | Scheduled vacuum / expire snapshots |
| Ignoring Schema Compatibility | Blind propagation of changes | Consumer breakage cross-cloud | Pre-change compatibility tests gate |
| Portal Gateway Bottleneck | Single rewriting service saturates | Latency inflation | Horizontal scale or sidecar model |
| Inconsistent Lineage | Separate lineage per orchestrator | Debugging friction | Emit OpenLineage from all systems |
| Single Runner Assumption | Expect Beam results identical w/o testing | Semantic divergence | Runner parity harness automated |
| Manual Lag Monitoring | Ad-hoc scripts | Hidden replication delays | Prometheus lag exporter + alerts |
| Multi-Format Without Docs | Ops reliant on tribal knowledge | On-call escalations | Unified operations playbook |

---

## 18. Migration Roadmap (Single-Cloud → Hybrid Governance)
| Phase | Goal | Actions | Success Metric | Rollback |
|-------|------|--------|----------------|----------|
| 0 Assessment | Baseline inventory | Catalog scan (tables/formats) + lag profiling | Inventory completeness ≥98% | N/A |
| 1 Format Governance | Select initial format strategy | Convert Tier-1 fact tables → Iceberg; keep Delta dims | Conversion latency < defined SLA | Revert to original Parquet files (retained) |
| 2 Streaming Replication | Hot topics cross-region | MirrorMaker + lag alerts | p95 lag < 8s | Disable replication + failover to source cluster |
| 3 Orchestration Hybrid | Asset lineage clarity | Dagster partial adoption + OpenLineage emission | Lineage coverage ≥90% | Keep Airflow only; assets flagged legacy |
| 4 Schema Enforcement | Prevent breaking changes | Compatibility gating before propagate | Zero failing consumer due to schema break | Pause propagation; manual diff approval |
| 5 Portability Expansion | Runner portability | Introduce Beam pipelines for shared transforms | Beam pipeline parity diff <0.5% | Fallback to Spark job artifact |
| 6 Policy Automation | OPA-driven replication | Residency + PII block policies enforced | Policy decision latency <2s | Manual override path documented |
| 7 Optimization & DR | Efficient ops + recovery | Snapshot expiration + quarterly restore test | DR test < defined RTO | Rollback to last validated snapshot |

---

## 19. Checklists

### 19.1 Design Readiness
- [ ] Table classification (fact, dimension, entity) complete.
- [ ] Format mapping rationale documented (Iceberg vs Hudi vs Delta).
- [ ] Replication scope list (hot tables + critical topics) approved.
- [ ] Compatibility test harness integrated in CI.
- [ ] Lag SLO defined (p95 < X seconds) per topic.
- [ ] Lineage emission configured (OpenLineage endpoints).
- [ ] Policy definitions version-controlled (residency, PII).
- [ ] Benchmark baseline captured (mutation latency, planning time).
- [ ] Rollback playbook written (format, schema, replication).

### 19.2 Launch Readiness
- [ ] Dry-run replication executed; parity harness green.
- [ ] Prometheus lag exporter returning stable metrics.
- [ ] Snapshot expiration schedule validated (no under-retention risk).
- [ ] Beam runner parity test passed (Spark vs Flink).
- [ ] OPA policy evaluation latency measured < target.
- [ ] On-call runbook includes multi-cloud failure scenarios.
- [ ] Backfills tested across both catalogs.
- [ ] OpenLineage dataset graph renders correctly.

### 19.3 Operations
- [ ] Weekly: Lag SLO report & incident review.
- [ ] Bi-weekly: Manifest count audit & rewrite trigger.
- [ ] Monthly: Schema change diff summary published.
- [ ] Quarterly: DR restore exercise documented.
- [ ] Continuous: Parity harness diffs <0.1%; escalate if above.

---

## 20. KPI / SLO Set
| KPI | Formula | Target | Rationale |
|-----|---------|--------|-----------|
| Metadata Sync Latency | avg(time_to_reflect_change) | <60s | Keep schema propagation tight |
| Replication Lag p95 | p95(lag_seconds) | <8s hot topics | Fresh data for analytics |
| Parity Diff Rate | diffs / total parity checks | <0.1% | Maintain trust in dual engines |
| Snapshot Retention Health | expired_snapshots / total | ≥ policy compliance | Avoid planning bloat |
| Format Appropriateness Coverage | tables_correct_format / total mutable tables | >90% | Validate format policy adherence |
| Schema Break Incidents | count(per month) | 0 | Prevent consumer downtime |
| Policy Decision Latency | avg(opa_eval_ms) | <2000ms | Avoid orchestration delays |
| Lineage Coverage | lineage_traced_assets / total_assets | >95% | Debug & compliance clarity |

Alert Example:
```
(replication_lag_seconds{topic="orders"} > 10) AND on(topic) (parity_diff_rate{topic="orders"} > 0.001)
```
Issue: Lag causing parity divergence.

---

## 21. Pricing Nuances (Conceptual)
Focus only on pricing models from roadmap context: BigQuery (scan-based), Redshift (compute node hours), Snowflake (warehouse credits), Spark (cluster hours), Kafka (broker instance + storage).

Comparative Cost Lens:
| Workload Type | Dominant Cost Driver | Optimization Lever |
|---------------|----------------------|--------------------|
| Interactive Ad-hoc (BigQuery) | Scan bytes | Partition filters + column pruning via external table design |
| Scheduled ETL (Spark) | Cluster runtime hours | Adaptive execution + file sizing + partition tuning |
| ML Feature Extraction (Beam/Spark) | Compute hours + shuffle | Windowing efficiency + state optimization |
| Streaming Ingestion (Kafka) | Broker storage + replication factor | Topic retention tiering + compaction |
| Analytical Marts (Redshift/Snowflake) | Warehouse uptime | Suspend idle clusters, concurrency scaling policies |
| Upsert Entities (Hudi) | Write amplification | Merge-on-Read compaction schedule tuning |

Sample Cost Scenario (Illustrative):
- Switching dimension upsert from Iceberg rewrite (full partition) to Hudi MOR reduces daily write IO by ~40% leading to cluster hour savings.
- Tightening BigQuery external table partition filters reduces scan bytes by 35% for weekly reporting queries.

---

## 22. Infra-as-Code Sketch (Multi-Provider Catalog Provisioning)
Terraform-like pseudo (conceptual only):
```hcl
module "iceberg_catalog_primary" {
  source = "./modules/iceberg_catalog"
  name   = "iceberg_primary"
  backend = "glue"
  region  = "us-east-1"
}

module "iceberg_catalog_secondary" {
  source = "./modules/iceberg_catalog"
  name   = "iceberg_secondary"
  backend = "hive_metastore"
  region  = "us-central1"
}

module "openlineage_collector" {
  source = "./modules/openlineage"
  endpoint = "https://lineage.internal/api"
}
```
Bicep pseudo for Dataflow/Beam scheduler omitted (out of scope for roadmap specifics).

---

## 23. Reference Configurations

### Airflow Portable DAG Pattern
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

CLOUD = '{{ var.value.target_cloud }}'

with DAG('portable_sales_etl', start_date=datetime(2024,1,1), schedule_interval='@daily') as dag:
    def extract():
        if CLOUD == 'aws':
            return read_from_s3('s3://sales/raw/{{ ds }}.csv')
        else:
            return read_from_gcs('gs://sales/raw/{{ ds }}.csv')
    def transform(data):
        return normalize(data)
    def load(rows):
        write_iceberg(rows, table='sales_iceberg')

    extract_task = PythonOperator(task_id='extract', python_callable=extract)
    transform_task = PythonOperator(task_id='transform', python_callable=transform)
    load_task = PythonOperator(task_id='load', python_callable=load)

    extract_task >> transform_task >> load_task
```

### Dagster Asset Definition Example
```python
from dagster import asset

@asset(group_name="sales", metadata={"format":"iceberg"})
def raw_sales(): ...

@asset(deps=[raw_sales], group_name="sales")
def cleaned_sales(raw_sales): ...

@asset(deps=[cleaned_sales], group_name="sales")
def fact_sales(cleaned_sales): ...
```

### Beam Pipeline Skeleton (Portability Emphasis)
```python
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

class Enrich(beam.DoFn):
    def process(self, record):
        record['amount_bucket'] = int(record['amount'] // 10)
        yield record

options = PipelineOptions(runner='SparkRunner')  # Switch to FlinkRunner for parity test

with beam.Pipeline(options=options) as p:
    (p
     | beam.io.ReadFromText('sales_events.csv')
     | beam.Map(lambda l: l.split(','))
     | beam.Map(lambda f: {'user': f[0], 'amount': float(f[1]), 'ts': f[2]})
     | beam.ParDo(Enrich())
     | beam.WindowInto(beam.window.FixedWindows(300))
     | beam.CombineGlobally(beam.combiners.CountCombineFn())
     | beam.io.WriteToText('out/result'))
```

### Kafka MirrorMaker Config Snippet
```properties
# mirror-maker.properties
consumer.bootstrap.servers=source-kafka:9092
producer.bootstrap.servers=target-kafka:9092
whitelist=orders,users_activity
num.streams=6
```

---

## 24. Extension Ideas (Roadmap-Aligned)
| Idea | Description | Stack Component | Benefit |
|------|-------------|-----------------|---------|
| Replication Selector | Airflow task ranks tables by query frequency & freshness SLA to update replication list | Airflow + query log analysis | Avoid over-replication |
| Schema Diff Visualizer | Web UI highlighting compatibility matrix decisions | Iceberg/Delta/Hudi catalogs + registry | Faster change approvals |
| Lineage Drift Detector | Compares OpenLineage graphs over time | OpenLineage + Dagster + Airflow emitters | Detect missing emissions |
| Runner Parity Auditor | Nightly Beam Spark vs Flink output diff job | Beam runners | Confidence in portability |
| Format Health Dashboard | Compaction, manifest count, snapshot age visualization | Iceberg/Hudi/Delta metrics | Prevent silent performance decay |
| Mutation Strategy Advisor | Suggests format switch (Iceberg→Hudi) when update latency threshold breached | Spark metrics + policy engine | Data-driven format evolution |

---

## 25. Glossary (Module-Specific)
| Term | Definition | Principal Note |
|------|------------|----------------|
| Portability | Ability to run workloads across different clouds/services | Selective portability beats universal mediocrity |
| Replication Lag | Delay between source commit and target availability | Monitor p95; p99 reveals edge cases |
| Parity Harness | Tool verifying cross-engine query equivalence | Key for trust during dual consumption phase |
| Hidden Partitioning | Iceberg feature obscuring partition details from queries | Simplifies query syntax; reduces user error |
| Merge-On-Read | Hudi strategy mixing base + delta logs for efficient upserts | Tune compaction to balance read vs write cost |
| Manifest Rewrite | Iceberg operation consolidating metadata for planning efficiency | Schedule before planning latency degrades |
| Asset Graph | Dagster representation of data dependencies | Enables selective recomputation |
| Policy Gate | Automated evaluation of replication/schema rules | Prevents post-facto incident remediation |
| Runner Portability | Beam executing same pipeline on different engines | Not absolute; validate semantics (watermarks) |
| Snapshot Expiration | Removal of old table versions (Iceberg/Delta) | Guardrail against metadata bloat |
| Lineage Emission | Publishing dependency & operation metadata (OpenLineage) | Basis for drift & compliance checks |

---

## 26. Citations / Further Reading
1. Iceberg Design Docs – Apache Iceberg site
2. Delta Lake Transaction Log Principles – Delta Lake docs
3. Apache Hudi Concepts – Hudi documentation
4. Kafka MirrorMaker Overview – Kafka docs
5. Apache Beam Programming Guide – Beam documentation
6. Airflow DAG Concepts – Airflow docs
7. Dagster Software Defined Assets – Dagster docs
8. OpenLineage Specification – openlineage.io
9. BigQuery External Tables – Google Cloud docs
10. Redshift Spectrum (External) – AWS docs
11. Netflix Data Platform (Maestro) – Netflix Tech Blog
12. LinkedIn Kafka Scaling Papers – LinkedIn Engineering Blog

---

## 27. Knowledge Matrix (Progression)
| Level | Capabilities Gained | Representative Artifacts |
|-------|---------------------|--------------------------|
| Beginner | Understand table formats and basic replication concepts | Single Iceberg table + simple Airflow DAG |
| Intermediate | Implement MirrorMaker lag monitoring + Delta vs Iceberg differences | Lag dashboard + compatibility test harness |
| Advanced | Hybrid format strategy (Iceberg + Hudi), Beam runner parity, Dagster asset lineage | Multi-format ops playbook + parity harness |
| Principal | Policy-driven multi-cloud governance, economic replication selection, lineage drift detection | OPA policy repo + replication selector + format health dashboard |

---

## ✅ Module Completion Checklist (Cloud & Service Mapping)
- [x] Sections 0–11
- [x] Sections 12–14
- [x] Sections 15–27

Quality Gates:
- Only roadmap technologies referenced.
- No external unapproved tooling introduced.
- Principal-level trade-offs articulated (format selection, replication economics, abstraction ROI).
- Failure modes mapped to detection & prevention actions.
- Labs comprehensive (catalog, mutation, parity, lag, migration, compatibility).

Study Plan Suggestion (2–3 Weeks):
1. Week 1: Labs 1–3 + read Parts 1–2.
2. Week 2: Labs 4–7 + build parity & lag dashboards.
3. Week 3: Draft migration roadmap + practice interview questions.

Last Updated: 2025-10-30  
Version: 1.0  
Maintainer: Avaire Learning Resources
