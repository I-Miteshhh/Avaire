# Week 15-16: Production Data Systems — BEGINNER Track

*"The difference between a proof-of-concept and a production system is 10x the effort. Understanding patterns, anti-patterns, and monitoring fundamentals is essential for L5+ engineers."* — Principal Engineer, Google

---

## 🎯 Learning Outcomes

- Understand production vs development environments
- Identify common data platform patterns (Lambda, Kappa, batch, streaming)
- Recognize anti-patterns and their consequences
- Implement monitoring and observability
- Design alerting strategies
- Handle data quality at scale
- Understand SLAs, SLIs, and SLOs
- Build fault-tolerant systems

---

## 🏗️ 1. Production vs Development

### Key Differences

```
┌──────────────────┬─────────────────────┬─────────────────────┐
│ Aspect           │ Development         │ Production          │
├──────────────────┼─────────────────────┼─────────────────────┤
│ Data Volume      │ Sample (1K rows)    │ Full (1B+ rows)     │
│ Availability     │ Best effort         │ 99.9%+ SLA          │
│ Performance      │ "Works on my        │ P50/P95/P99 metrics │
│                  │ laptop"             │ defined             │
│ Error Handling   │ Print to console    │ Structured logging, │
│                  │                     │ alerting            │
│ Monitoring       │ None                │ Dashboards, metrics │
│ Cost             │ Free tier           │ Optimized ($1000s)  │
│ Deployment       │ Manual              │ CI/CD, blue-green   │
│ Rollback         │ Git reset           │ Automated rollback  │
│ Testing          │ Manual              │ Unit + integration  │
│                  │                     │ + load tests        │
│ Documentation    │ Optional            │ Required (runbooks) │
└──────────────────┴─────────────────────┴─────────────────────┘
```

---

### Production Readiness Checklist

```
Infrastructure:
├─ [ ] Multi-region deployment (disaster recovery)
├─ [ ] Autoscaling configured (handle traffic spikes)
├─ [ ] Load balancing (distribute traffic)
├─ [ ] Health checks (liveness/readiness probes)
└─ [ ] Resource limits (CPU, memory, disk quotas)

Observability:
├─ [ ] Logging (structured logs to centralized system)
├─ [ ] Metrics (Prometheus, Datadog, CloudWatch)
├─ [ ] Tracing (distributed tracing with Jaeger/Zipkin)
├─ [ ] Dashboards (Grafana, Kibana for visualization)
└─ [ ] Alerting (PagerDuty, Slack, email on errors)

Reliability:
├─ [ ] Error handling (retry with exponential backoff)
├─ [ ] Circuit breakers (prevent cascading failures)
├─ [ ] Timeouts (avoid hanging requests)
├─ [ ] Rate limiting (protect from abuse)
└─ [ ] Graceful degradation (partial functionality on failure)

Data Quality:
├─ [ ] Schema validation (reject invalid data)
├─ [ ] Duplicate detection (idempotency)
├─ [ ] Data reconciliation (source vs destination counts)
├─ [ ] Data lineage (track data provenance)
└─ [ ] SLA monitoring (data freshness, completeness)

Security:
├─ [ ] Authentication (API keys, OAuth, mTLS)
├─ [ ] Authorization (RBAC, least privilege)
├─ [ ] Encryption at rest (KMS, customer-managed keys)
├─ [ ] Encryption in transit (TLS 1.2+)
└─ [ ] Audit logging (who accessed what, when)

Testing:
├─ [ ] Unit tests (>80% code coverage)
├─ [ ] Integration tests (end-to-end workflows)
├─ [ ] Load tests (simulate production traffic)
├─ [ ] Chaos testing (inject failures, test resilience)
└─ [ ] Canary deployments (gradual rollout)

Operations:
├─ [ ] Runbooks (how to debug common issues)
├─ [ ] Incident response plan (on-call rotation)
├─ [ ] Backup & restore (automated daily backups)
├─ [ ] Disaster recovery plan (RTO/RPO targets)
└─ [ ] Cost monitoring (budget alerts)
```

---

## 📐 2. Common Architecture Patterns

### Pattern 1: Batch Processing (Traditional ETL)

```
┌─────────────────────────────────────────────────────────────┐
│ Batch Processing Architecture                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Source Systems (OLTP):                                      │
│ ├─ PostgreSQL (transactions)                               │
│ ├─ MySQL (user data)                                       │
│ └─ MongoDB (logs)                                          │
│         │                                                   │
│         ▼                                                   │
│ ┌──────────────────┐                                       │
│ │ Extract (Nightly)│  (Airflow DAG runs at 2am)           │
│ │ - Full dump      │                                       │
│ │ - Incremental    │                                       │
│ └────────┬─────────┘                                       │
│          ▼                                                  │
│ ┌──────────────────┐                                       │
│ │ Staging (S3/HDFS)│                                       │
│ │ - Raw data       │                                       │
│ │ - Partitioned    │                                       │
│ └────────┬─────────┘                                       │
│          ▼                                                  │
│ ┌──────────────────┐                                       │
│ │ Transform (Spark)│                                       │
│ │ - Clean          │                                       │
│ │ - Join           │                                       │
│ │ - Aggregate      │                                       │
│ └────────┬─────────┘                                       │
│          ▼                                                  │
│ ┌──────────────────┐                                       │
│ │ Load (Warehouse) │                                       │
│ │ - Snowflake      │                                       │
│ │ - BigQuery       │                                       │
│ │ - Redshift       │                                       │
│ └──────────────────┘                                       │
│                                                             │
│ Characteristics:                                            │
│ ├─ Latency: Hours to days                                  │
│ ├─ Throughput: High (process TB overnight)                 │
│ ├─ Complexity: Low (simple pipelines)                      │
│ └─ Cost: Low (batch compute is cheap)                      │
│                                                             │
│ Use Cases:                                                  │
│ ├─ Daily reports (revenue, KPIs)                           │
│ ├─ ML training (historical data)                           │
│ └─ Data warehousing (OLAP)                                 │
└─────────────────────────────────────────────────────────────┘
```

**Pros:**
- Simple to understand and implement
- High throughput (can process TB of data)
- Cost-effective (batch compute is cheap)
- Well-established tools (Airflow, Spark)

**Cons:**
- High latency (hours to days)
- No real-time insights
- Reprocessing is expensive (must rerun entire batch)

---

### Pattern 2: Streaming Processing (Real-Time)

```
┌─────────────────────────────────────────────────────────────┐
│ Streaming Architecture                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Event Sources:                                              │
│ ├─ User clicks (website, mobile app)                       │
│ ├─ IoT sensors (temperature, location)                     │
│ └─ Transaction logs (CDC from databases)                   │
│         │                                                   │
│         ▼                                                   │
│ ┌──────────────────┐                                       │
│ │ Message Queue    │                                       │
│ │ - Kafka          │  (Buffering, replay, partitioning)   │
│ │ - Kinesis        │                                       │
│ │ - Pub/Sub        │                                       │
│ └────────┬─────────┘                                       │
│          ▼                                                  │
│ ┌──────────────────┐                                       │
│ │ Stream Processor │                                       │
│ │ - Flink          │  (Windowing, aggregations, joins)    │
│ │ - Spark Streaming│                                       │
│ │ - Beam/Dataflow  │                                       │
│ └────────┬─────────┘                                       │
│          ▼                                                  │
│ ┌──────────────────────────────────┐                       │
│ │ Sinks (Multiple):                │                       │
│ │ ├─ Real-time DB (DynamoDB, Bigtable)                    │
│ │ ├─ Search (Elasticsearch)                               │
│ │ ├─ Cache (Redis)                                        │
│ │ └─ Data Lake (S3, for batch)                            │
│ └──────────────────────────────────┘                       │
│                                                             │
│ Characteristics:                                            │
│ ├─ Latency: Milliseconds to seconds                        │
│ ├─ Throughput: Medium (1M events/sec)                      │
│ ├─ Complexity: High (state management, exactly-once)       │
│ └─ Cost: High (always-on compute)                          │
│                                                             │
│ Use Cases:                                                  │
│ ├─ Fraud detection (real-time alerts)                      │
│ ├─ Recommendation engines (personalized content)           │
│ ├─ Real-time dashboards (metrics, monitoring)              │
│ └─ Operational analytics (live KPIs)                       │
└─────────────────────────────────────────────────────────────┘
```

**Pros:**
- Low latency (sub-second)
- Real-time insights
- Incremental processing (no reprocessing)

**Cons:**
- Complex (state management, exactly-once semantics)
- Expensive (always-on compute)
- Harder to debug (distributed, stateful)

---

### Pattern 3: Lambda Architecture (Batch + Streaming)

```
┌─────────────────────────────────────────────────────────────┐
│ Lambda Architecture                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                     ┌──────────────┐                        │
│                     │ Data Sources │                        │
│                     └───────┬──────┘                        │
│                             │                               │
│                ┌────────────┴────────────┐                  │
│                ▼                         ▼                  │
│    ┌─────────────────────┐   ┌─────────────────────┐       │
│    │ Batch Layer (Spark) │   │ Speed Layer (Flink) │       │
│    │ - Full history      │   │ - Recent data only  │       │
│    │ - High latency      │   │ - Low latency       │       │
│    │ - Accurate          │   │ - Approximate       │       │
│    └──────────┬──────────┘   └──────────┬──────────┘       │
│               │                         │                   │
│               ▼                         ▼                   │
│    ┌─────────────────────┐   ┌─────────────────────┐       │
│    │ Batch Views         │   │ Real-time Views     │       │
│    │ (Data Warehouse)    │   │ (Redis, DynamoDB)   │       │
│    └──────────┬──────────┘   └──────────┬──────────┘       │
│               │                         │                   │
│               └────────────┬────────────┘                   │
│                            ▼                                │
│                  ┌───────────────────┐                      │
│                  │ Serving Layer     │                      │
│                  │ - Merge views     │                      │
│                  │ - Query API       │                      │
│                  └───────────────────┘                      │
│                                                             │
│ Query Logic:                                                │
│ result = batch_view(0 to T-1) + speed_view(T to now)       │
│                                                             │
│ Characteristics:                                            │
│ ├─ Latency: Low (via speed layer)                          │
│ ├─ Accuracy: High (via batch layer)                        │
│ ├─ Complexity: Very high (maintain 2 pipelines)            │
│ └─ Cost: High (run batch + streaming)                      │
└─────────────────────────────────────────────────────────────┘
```

**Pros:**
- Best of both worlds (low latency + high accuracy)
- Fault-tolerant (batch layer can recompute)

**Cons:**
- Complex (maintain 2 codebases)
- Expensive (run both batch and streaming)
- Hard to keep in sync (eventual consistency)

---

### Pattern 4: Kappa Architecture (Streaming-Only)

```
┌─────────────────────────────────────────────────────────────┐
│ Kappa Architecture (Simplified Lambda)                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│           ┌──────────────┐                                  │
│           │ Data Sources │                                  │
│           └───────┬──────┘                                  │
│                   ▼                                         │
│           ┌──────────────┐                                  │
│           │ Kafka (Log)  │  (Immutable, replayable)        │
│           │ - Infinite   │                                  │
│           │   retention  │                                  │
│           └───────┬──────┘                                  │
│                   ▼                                         │
│           ┌──────────────┐                                  │
│           │ Stream       │                                  │
│           │ Processor    │  (Flink, Spark, Beam)           │
│           │ - Stateful   │                                  │
│           │ - Exactly-   │                                  │
│           │   once       │                                  │
│           └───────┬──────┘                                  │
│                   ▼                                         │
│           ┌──────────────┐                                  │
│           │ Materialized │                                  │
│           │ Views        │  (Real-time + historical)       │
│           │ - Redis      │                                  │
│           │ - Cassandra  │                                  │
│           └──────────────┘                                  │
│                                                             │
│ Reprocessing (no batch layer):                             │
│ 1. Deploy new streaming job (version 2)                    │
│ 2. Replay Kafka from offset 0                              │
│ 3. Build new materialized views                            │
│ 4. Switch traffic to new views                             │
│                                                             │
│ Characteristics:                                            │
│ ├─ Latency: Low (streaming-only)                           │
│ ├─ Complexity: Medium (1 codebase)                         │
│ ├─ Cost: Medium (streaming compute)                        │
│ └─ Reprocessing: Replay from Kafka                         │
└─────────────────────────────────────────────────────────────┘
```

**Pros:**
- Simpler than Lambda (1 codebase)
- Low latency
- Easy to reprocess (replay Kafka)

**Cons:**
- Requires infinite retention (Kafka storage cost)
- Streaming framework must be powerful (Flink, Beam)
- Hard to debug historical issues

---

## 🚫 3. Anti-Patterns

### Anti-Pattern 1: The "Big Ball of Mud"

```
Problem: Monolithic pipeline with no modularity

Bad:
┌─────────────────────────────────────────────────────────┐
│ single_giant_pipeline.py (5000 lines)                   │
│ ├─ Extract from 10 sources                             │
│ ├─ Transform with 50 steps                             │
│ ├─ Load to 5 destinations                              │
│ └─ No separation of concerns                           │
└─────────────────────────────────────────────────────────┘

Consequences:
├─ ❌ Hard to test (must test entire pipeline)
├─ ❌ Hard to debug (which step failed?)
├─ ❌ Hard to scale (can't parallelize)
└─ ❌ Hard to modify (change 1 line, risk breaking everything)

Good:
┌─────────────────────────────────────────────────────────┐
│ Modular Pipeline (Airflow DAG)                          │
│ ├─ extract_postgres (task 1)                           │
│ ├─ extract_api (task 2, parallel with task 1)          │
│ ├─ transform_clean (task 3, depends on 1+2)            │
│ ├─ transform_aggregate (task 4, depends on 3)          │
│ └─ load_warehouse (task 5, depends on 4)               │
└─────────────────────────────────────────────────────────┘

Benefits:
├─ ✅ Each task is testable
├─ ✅ Easy to debug (view logs per task)
├─ ✅ Parallelizable (tasks 1+2 run together)
└─ ✅ Modifiable (change 1 task without risk)
```

---

### Anti-Pattern 2: No Idempotency

```
Problem: Re-running pipeline creates duplicates

Bad:
def load_data():
    data = extract()
    for record in data:
        db.execute("INSERT INTO users VALUES (%s, %s)", record)
    # Re-run → Duplicates! ❌

Consequences:
├─ ❌ Duplicates in database
├─ ❌ Cannot retry on failure
└─ ❌ Data reconciliation issues

Good (Idempotent):
def load_data():
    data = extract()
    for record in data:
        db.execute("""
            INSERT INTO users (id, name)
            VALUES (%s, %s)
            ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name
        """, record)
    # Re-run → No duplicates! ✅

Or use staging table:
def load_data():
    data = extract()
    
    # Truncate staging
    db.execute("TRUNCATE TABLE users_staging")
    
    # Load to staging
    for record in data:
        db.execute("INSERT INTO users_staging VALUES (%s, %s)", record)
    
    # Atomic swap
    db.execute("BEGIN")
    db.execute("DROP TABLE users_old")
    db.execute("ALTER TABLE users RENAME TO users_old")
    db.execute("ALTER TABLE users_staging RENAME TO users")
    db.execute("COMMIT")
```

---

### Anti-Pattern 3: No Monitoring (Flying Blind)

```
Problem: Pipeline runs silently, failures go unnoticed

Bad:
try:
    run_pipeline()
except Exception as e:
    print(f"Error: {e}")  # Lost in logs ❌

Consequences:
├─ ❌ Data staleness goes undetected
├─ ❌ Failures discovered by users (embarrassing)
└─ ❌ No historical metrics (can't optimize)

Good:
import logging
import statsd
from datetime import datetime

logger = logging.getLogger(__name__)
metrics = statsd.StatsClient('statsd-server', 8125)

def run_pipeline():
    start_time = datetime.now()
    
    try:
        # Extract
        logger.info("Starting extraction")
        records = extract()
        metrics.gauge('pipeline.records.extracted', len(records))
        
        # Transform
        logger.info("Starting transformation")
        transformed = transform(records)
        metrics.gauge('pipeline.records.transformed', len(transformed))
        
        # Load
        logger.info("Starting load")
        load(transformed)
        metrics.gauge('pipeline.records.loaded', len(transformed))
        
        # Success metrics
        duration = (datetime.now() - start_time).total_seconds()
        metrics.timing('pipeline.duration', duration)
        metrics.increment('pipeline.success')
        
        logger.info(f"Pipeline succeeded in {duration}s")
        send_slack_notification("✅ Pipeline success", color="good")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        metrics.increment('pipeline.failure')
        send_pagerduty_alert(f"Pipeline failed: {e}")
        send_slack_notification(f"❌ Pipeline failed: {e}", color="danger")
        raise
```

---

### Anti-Pattern 4: Hardcoded Configuration

```
Problem: Config baked into code

Bad:
def extract():
    conn = psycopg2.connect(
        host="prod-db.company.com",  # Hardcoded! ❌
        user="admin",
        password="P@ssw0rd123",  # Password in code! ❌❌❌
        database="production"
    )

Consequences:
├─ ❌ Cannot test in dev (different DB)
├─ ❌ Security risk (password in version control)
└─ ❌ Hard to change (must redeploy code)

Good:
import os
from dataclasses import dataclass

@dataclass
class Config:
    db_host: str
    db_user: str
    db_password: str
    db_name: str
    
    @classmethod
    def from_env(cls):
        return cls(
            db_host=os.environ['DB_HOST'],
            db_user=os.environ['DB_USER'],
            db_password=os.environ['DB_PASSWORD'],  # From secrets manager
            db_name=os.environ['DB_NAME'],
        )

config = Config.from_env()

def extract():
    conn = psycopg2.connect(
        host=config.db_host,
        user=config.db_user,
        password=config.db_password,
        database=config.db_name,
    )

# Deployment:
# dev:  DB_HOST=dev-db.company.com
# prod: DB_HOST=prod-db.company.com
```

---

## 📊 4. Monitoring Fundamentals

### The Three Pillars of Observability

```
1. Logging:
   ├─ What: Discrete events (errors, warnings, info)
   ├─ Format: Structured JSON logs
   ├─ Storage: Elasticsearch, Splunk, CloudWatch
   └─ Query: "Show me all errors in last hour"

2. Metrics:
   ├─ What: Numerical time-series data
   ├─ Types: Counters, gauges, histograms
   ├─ Storage: Prometheus, InfluxDB, Datadog
   └─ Query: "What's the P95 latency?"

3. Tracing:
   ├─ What: Request flow through distributed system
   ├─ Format: Spans (operation duration) + trace ID
   ├─ Storage: Jaeger, Zipkin, X-Ray
   └─ Query: "Why is this request slow?"
```

---

### Key Metrics to Track

```python
# Throughput metrics
metrics.gauge('pipeline.records.per_second', records_per_sec)
metrics.gauge('pipeline.bytes.per_second', bytes_per_sec)

# Latency metrics
metrics.histogram('pipeline.task.duration', task_duration)
metrics.histogram('pipeline.end_to_end.duration', total_duration)

# Error metrics
metrics.increment('pipeline.errors.total')
metrics.increment('pipeline.errors.retryable')
metrics.increment('pipeline.errors.fatal')

# Data quality metrics
metrics.gauge('data.null_percentage', null_count / total_count * 100)
metrics.gauge('data.duplicate_percentage', dup_count / total_count * 100)

# Resource metrics
metrics.gauge('pipeline.cpu.usage_percent', cpu_usage)
metrics.gauge('pipeline.memory.usage_mb', memory_mb)
metrics.gauge('pipeline.disk.usage_gb', disk_gb)

# SLA metrics
metrics.gauge('pipeline.freshness.minutes', freshness_minutes)
metrics.gauge('pipeline.completeness.percent', completeness_pct)
```

---

## 🚨 5. Alerting Strategies

### Alert Fatigue Prevention

```
Bad Alerting:
├─ Alert on every error (100 alerts/day) ❌
├─ No prioritization (all alerts are "critical") ❌
└─ No context (alert says "Error" with no details) ❌

Result: Team ignores alerts, real issues missed

Good Alerting:
├─ Alert only on SLA violations ✅
├─ Prioritize: P0 (page), P1 (email), P2 (ticket) ✅
└─ Include context (error message, runbook link) ✅
```

---

### Severity Levels

```
P0 (Critical - Page on-call):
├─ Pipeline down >15 minutes
├─ Data corruption detected
├─ Security breach
└─ Customer-facing impact

P1 (High - Email + Slack):
├─ Pipeline delay >1 hour
├─ Data quality check failed
├─ Elevated error rate (>5%)
└─ Resource exhaustion (disk 90% full)

P2 (Medium - Ticket):
├─ Pipeline delay <1 hour
├─ Single task failure (auto-retry working)
├─ Warning-level issues
└─ Performance degradation (P95 latency up 20%)

P3 (Low - Log only):
├─ Informational events
├─ Successful completions
└─ Routine maintenance
```

---

### Example Alert Rules

```yaml
# Prometheus alert rules

groups:
  - name: data_pipeline
    interval: 1m
    rules:
      # P0: Pipeline down
      - alert: PipelineDown
        expr: time() - pipeline_last_success_timestamp > 900  # 15 min
        labels:
          severity: critical
        annotations:
          summary: "Pipeline {{ $labels.pipeline_name }} down for 15+ minutes"
          description: "Last success: {{ $value }}s ago"
          runbook: "https://wiki.company.com/runbooks/pipeline-down"
      
      # P1: High error rate
      - alert: HighErrorRate
        expr: rate(pipeline_errors_total[5m]) > 0.05  # 5% error rate
        labels:
          severity: high
        annotations:
          summary: "Pipeline {{ $labels.pipeline_name }} error rate >5%"
          description: "Current rate: {{ $value | humanizePercentage }}"
      
      # P1: Data freshness SLA violated
      - alert: DataStale
        expr: pipeline_freshness_minutes > 60  # Data >1 hour old
        labels:
          severity: high
        annotations:
          summary: "Data in {{ $labels.table_name }} is stale"
          description: "Freshness: {{ $value }} minutes (SLA: 60 minutes)"
      
      # P2: Disk usage high
      - alert: DiskUsageHigh
        expr: pipeline_disk_usage_percent > 90
        labels:
          severity: medium
        annotations:
          summary: "Disk usage >90% on {{ $labels.instance }}"
          description: "Usage: {{ $value }}%"
```

---

## 📚 Summary Checklist

- [ ] Understand production vs development differences
- [ ] Identify common architecture patterns (batch, streaming, Lambda, Kappa)
- [ ] Recognize anti-patterns (big ball of mud, no idempotency, no monitoring, hardcoded config)
- [ ] Implement the three pillars of observability (logging, metrics, tracing)
- [ ] Design effective alerting (avoid alert fatigue, prioritize by severity)
- [ ] Track key metrics (throughput, latency, errors, data quality, SLA)
- [ ] Build production-ready systems (fault-tolerant, monitored, documented)

**Next:** [INTERMEDIATE.md →](INTERMEDIATE.md)
