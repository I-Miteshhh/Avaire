# Week 15-16: Production Data Systems — WHITEPAPERS

*"The Lambda Architecture paper by Nathan Marz, Kappa by Jay Kreps, and Data Mesh by Zhamak Dehghani fundamentally changed how we think about data platforms at scale."* — VP Engineering, LinkedIn

---

## 📄 Paper 1: Lambda Architecture (Nathan Marz, 2011)

**Link:** http://nathanmarz.com/blog/how-to-beat-the-cap-theorem.html

### Abstract

Lambda Architecture is a data-processing architecture designed to handle massive quantities of data by taking advantage of both batch and stream-processing methods. It provides a systematic approach to building robust, fault-tolerant, and scalable data systems.

---

### Core Concepts

#### 1. The Three Layers

```
┌──────────────────────────────────────────────────────────────┐
│ Lambda Architecture                                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│                     ALL DATA                                 │
│                        │                                     │
│            ┌───────────┴───────────┐                         │
│            ▼                       ▼                         │
│    ┌────────────────┐      ┌────────────────┐               │
│    │ Batch Layer    │      │ Speed Layer    │               │
│    │                │      │                │               │
│    │ - Process ALL  │      │ - Process      │               │
│    │   historical   │      │   RECENT data  │               │
│    │   data         │      │   only         │               │
│    │ - High latency │      │ - Low latency  │               │
│    │   (hours)      │      │   (seconds)    │               │
│    │ - Accurate     │      │ - Approximate  │               │
│    │ - Immutable    │      │ - Mutable      │               │
│    │                │      │                │               │
│    │ Tech:          │      │ Tech:          │               │
│    │ - Spark        │      │ - Flink        │               │
│    │ - MapReduce    │      │ - Storm        │               │
│    │ - Hadoop       │      │ - Samza        │               │
│    └────────┬───────┘      └────────┬───────┘               │
│             │                       │                        │
│             ▼                       ▼                        │
│    ┌─────────────────────────────────────┐                  │
│    │ Batch Views      Speed Views        │                  │
│    │ (Precomputed)    (Real-time)        │                  │
│    └──────────┬──────────────┬───────────┘                  │
│               │              │                               │
│               └──────┬───────┘                               │
│                      ▼                                       │
│            ┌──────────────────┐                              │
│            │ Serving Layer    │                              │
│            │                  │                              │
│            │ - Merge views    │                              │
│            │ - Query API      │                              │
│            │ - Low latency    │                              │
│            │                  │                              │
│            │ query(t) =       │                              │
│            │   batch(0 to T-1)│                              │
│            │   + speed(T to t)│                              │
│            └──────────────────┘                              │
└──────────────────────────────────────────────────────────────┘
```

---

#### 2. Properties of Lambda Architecture

```
Property 1: Human Fault-Tolerance
├─ Batch layer processes immutable raw data
├─ If bug in algorithm → Recompute batch views
├─ No data loss, no corruption
└─ Example: Bug in aggregation logic
    → Fix code, rerun batch job, overwrite views ✅

Property 2: Data is Immutable
├─ Only append new data, never update/delete
├─ Benefits:
│  ├─ Simplicity (no complex update logic)
│  ├─ Debuggability (full history preserved)
│  └─ Reprocessing (can replay any time range)
└─ Example:
    Raw events: [e1, e2, e3, e4, ...]
    Never: UPDATE e1 SET value = X ❌
    Always: APPEND e5 (correction for e1) ✅

Property 3: Recomputation
├─ Ability to recompute views from scratch
├─ Use case: Algorithm change, bug fix, schema evolution
└─ Example:
    Old algorithm: COUNT(DISTINCT user_id)
    New algorithm: HyperLogLog(user_id) (more accurate)
    → Recompute all batch views with new algorithm

Property 4: Separation of Concerns
├─ Batch layer: Accuracy, completeness
├─ Speed layer: Latency, availability
├─ Serving layer: Query performance
└─ Each layer optimized independently
```

---

#### 3. Example: Pageview Counter

```python
# Lambda Architecture for counting pageviews

# ===== Batch Layer =====
# Runs daily, processes ALL historical data

from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("BatchLayer").getOrCreate()

# Read ALL pageviews from data lake (1 year = 100 TB)
pageviews = spark.read.parquet('s3://datalake/pageviews/')

# Aggregate
batch_views = pageviews.groupBy('url', 'date') \
    .agg({'user_id': 'count'}) \
    .withColumnRenamed('count(user_id)', 'total_views')

# Write to batch view (overwrite daily)
batch_views.write.mode('overwrite').parquet('s3://batch-views/pageviews/')

# Runtime: 4 hours (processes 100 TB)
# Freshness: Up to 1 day old

# ===== Speed Layer =====
# Runs continuously, processes RECENT data only

from pyflink.datastream import StreamExecutionEnvironment

env = StreamExecutionEnvironment.get_execution_environment()

# Read from Kafka (real-time pageviews)
pageviews = env.add_source(FlinkKafkaConsumer('pageviews', ...))

# Aggregate (5-minute tumbling window)
speed_views = pageviews \
    .key_by(lambda x: (x['url'], x['date'])) \
    .window(TumblingEventTimeWindows.of(Time.minutes(5))) \
    .aggregate(CountAggregateFunction())

# Write to speed view (append)
speed_views.add_sink(RedisSink('speed-views'))

# Runtime: Continuous
# Freshness: <5 minutes

# ===== Serving Layer =====
# Merges batch + speed views

def get_pageviews(url, date):
    # Get batch view (accurate, but up to 1 day old)
    batch_count = read_from_parquet(f's3://batch-views/pageviews/{date}/')
    batch_count = batch_count[batch_count['url'] == url]['total_views']
    
    # Get speed view (recent, last 24 hours)
    speed_count = redis.get(f'speed-views:{url}:{date}')
    
    # Merge
    total = batch_count + speed_count
    return total

# Query latency: <100ms
# Accuracy: Eventual (batch layer catches up daily)
```

---

### Critique of Lambda Architecture

```
Pros:
├─ ✅ Handles both batch and real-time
├─ ✅ Fault-tolerant (recompute batch views)
├─ ✅ Scalable (batch and speed layers scale independently)
└─ ✅ Proven at scale (LinkedIn, Twitter, Uber)

Cons:
├─ ❌ Complexity: Maintain 2 codebases (batch + speed)
├─ ❌ Synchronization: Keep batch and speed views consistent
├─ ❌ Cost: Run both batch and streaming infrastructure
└─ ❌ Learning curve: Need expertise in both batch and streaming
```

---

## 📘 Paper 2: Kappa Architecture (Jay Kreps, 2014)

**Link:** https://www.oreilly.com/radar/questioning-the-lambda-architecture/

### Abstract

Jay Kreps (creator of Kafka, co-founder of Confluent) proposed **Kappa Architecture** as a simplification of Lambda. Key insight: *"What if everything is a stream?"*

---

### Core Concepts

#### The Kappa Principle

```
"Instead of maintaining batch and speed layers,
 use streaming-only with replayable logs."

┌──────────────────────────────────────────────────────────────┐
│ Kappa Architecture                                           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│                     ALL DATA                                 │
│                        │                                     │
│                        ▼                                     │
│                ┌───────────────┐                             │
│                │ Immutable Log │                             │
│                │ (Kafka)       │                             │
│                │ - Infinite    │                             │
│                │   retention   │                             │
│                │ - Replayable  │                             │
│                └───────┬───────┘                             │
│                        │                                     │
│                        ▼                                     │
│                ┌───────────────┐                             │
│                │ Stream        │                             │
│                │ Processor     │                             │
│                │ (Flink/Beam)  │                             │
│                │ - Stateful    │                             │
│                │ - Exactly-once│                             │
│                └───────┬───────┘                             │
│                        │                                     │
│                        ▼                                     │
│                ┌───────────────┐                             │
│                │ Materialized  │                             │
│                │ Views         │                             │
│                │ (Redis, DB)   │                             │
│                └───────────────┘                             │
│                                                              │
│ Reprocessing:                                                │
│ 1. Deploy new stream processor (version 2)                  │
│ 2. Replay Kafka from offset 0                               │
│ 3. Build new materialized views                             │
│ 4. Switch traffic to new views                              │
│ 5. Decommission old version                                 │
└──────────────────────────────────────────────────────────────┘
```

---

#### Key Differences from Lambda

```
┌────────────────────┬─────────────────┬─────────────────┐
│ Aspect             │ Lambda          │ Kappa           │
├────────────────────┼─────────────────┼─────────────────┤
│ Layers             │ Batch + Speed   │ Stream only     │
│ Codebases          │ 2 (different)   │ 1 (unified)     │
│ Reprocessing       │ Batch job       │ Replay stream   │
│ Complexity         │ High            │ Medium          │
│ Cost               │ High (both)     │ Medium (stream) │
│ Latency            │ Mixed           │ Low (uniform)   │
│ Storage            │ HDFS/S3         │ Kafka (log)     │
└────────────────────┴─────────────────┴─────────────────┘
```

---

#### Example: Kappa Implementation

```python
# Kappa Architecture for pageview counting

# ===== Immutable Log (Kafka) =====
kafka_config = {
    'topic': 'pageviews',
    'partitions': 100,
    'replication_factor': 3,
    'retention': -1,  # Infinite retention ✅
    'compression': 'zstd',  # 3x compression
}

# Write pageviews to Kafka
producer.send('pageviews', {
    'url': 'https://example.com/article',
    'user_id': 12345,
    'timestamp': '2025-10-15T10:30:00Z',
})

# ===== Stream Processor (Flink) =====
from pyflink.datastream import StreamExecutionEnvironment

env = StreamExecutionEnvironment.get_execution_environment()

# Read from Kafka (can replay from any offset)
pageviews = env.add_source(FlinkKafkaConsumer(
    topics='pageviews',
    deserialization_schema=JsonDeserializationSchema(),
    properties={'bootstrap.servers': 'kafka:9092'},
))

# Aggregate (exactly-once semantics)
aggregated = pageviews \
    .key_by(lambda x: (x['url'], x['date'])) \
    .window(TumblingEventTimeWindows.of(Time.hours(1))) \
    .aggregate(CountAggregateFunction())

# Write to materialized view (Redis)
aggregated.add_sink(RedisSink('pageview-counts'))

# ===== Reprocessing =====
# Scenario: Algorithm changed (use HyperLogLog for unique users)

# Step 1: Deploy new Flink job (version 2) with new algorithm
flink_job_v2 = FlinkJob(
    algorithm='hyperloglog',
    kafka_offset='earliest',  # Replay from beginning
    output_table='pageview-counts-v2',  # New table
)

# Step 2: Wait for catch-up (process 1 year of data)
# Throughput: 100K events/sec × 86400 sec/day × 365 days
#           = 3.15 trillion events
# Time to process: ~3 days (with 200-node cluster)

# Step 3: Switch traffic (blue-green deployment)
app.config['redis_table'] = 'pageview-counts-v2'

# Step 4: Decommission old job
flink_job_v1.stop()

# Result: Reprocessing without maintaining separate batch layer ✅
```

---

### When to Use Kappa vs Lambda

```
Use Kappa if:
├─ ✅ All data can be treated as streams
├─ ✅ Reprocessing is acceptable (can replay Kafka)
├─ ✅ Team has streaming expertise
└─ ✅ Want to minimize complexity (1 codebase)

Use Lambda if:
├─ ✅ Have legacy batch systems (can't rewrite everything)
├─ ✅ Very large historical data (100+ PB, replay too slow)
├─ ✅ Batch and streaming algorithms differ significantly
└─ ✅ Need to separate concerns (different teams own batch vs stream)

Real-World Examples:
├─ Kappa: Uber (replaced Lambda with Kappa in 2017)
├─ Lambda: LinkedIn (still uses Lambda for massive scale)
└─ Hybrid: Netflix (Kappa for real-time, batch for ML training)
```

---

## 🌐 Paper 3: Data Mesh (Zhamak Dehghani, 2019)

**Link:** https://martinfowler.com/articles/data-monolith-to-mesh.html

### Abstract

Zhamak Dehghani (Principal at ThoughtWorks) proposed **Data Mesh** as a paradigm shift from centralized data platforms to domain-oriented, decentralized data ownership.

---

### Core Principles

#### 1. Domain-Oriented Decentralization

```
Traditional: Centralized Data Platform

┌─────────────────────────────────────────────────────────────┐
│ Central Data Team (Bottleneck)                              │
│ ├─ Owns all data pipelines                                  │
│ ├─ Ingests from all domains                                 │
│ └─ Serves all teams                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
  ┌──────────┐     ┌──────────┐     ┌──────────┐
  │ Marketing│     │ Sales    │     │ Support  │
  │ Team     │     │ Team     │     │ Team     │
  │ (waits)  │     │ (waits)  │     │ (waits)  │
  └──────────┘     └──────────┘     └──────────┘

Problems:
├─ ❌ Bottleneck: Central team overwhelmed
├─ ❌ Slow: Weeks to build new pipeline
├─ ❌ Context loss: Data team doesn't understand domain
└─ ❌ Fragile: One team owns all critical infrastructure

────────────────────────────────────────────────────────────────

Data Mesh: Decentralized Ownership

┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Marketing    │   │ Sales        │   │ Support      │
│ Domain       │   │ Domain       │   │ Domain       │
│              │   │              │   │              │
│ ┌──────────┐ │   │ ┌──────────┐ │   │ ┌──────────┐ │
│ │ Data     │ │   │ │ Data     │ │   │ │ Data     │ │
│ │ Product  │ │   │ │ Product  │ │   │ │ Product  │ │
│ │ ────────│ │   │ │ ────────│ │   │ │ ────────│ │
│ │ - Pipeline│ │   │ │ - Pipeline│ │   │ │ - Pipeline│ │
│ │ - Quality │ │   │ │ - Quality │ │   │ │ - Quality │ │
│ │ - SLA     │ │   │ │ - SLA     │ │   │ │ - SLA     │ │
│ └──────────┘ │   │ └──────────┘ │   │ └──────────┘ │
└──────────────┘   └──────────────┘   └──────────────┘
     │                  │                  │
     └──────────────────┼──────────────────┘
                        ▼
              ┌──────────────────┐
              │ Self-Service     │
              │ Platform         │
              │ (Infrastructure) │
              └──────────────────┘

Benefits:
├─ ✅ No bottleneck: Each domain owns their data
├─ ✅ Fast: Domain team builds pipeline themselves
├─ ✅ Context: Domain experts own their data
└─ ✅ Scalable: Add domains without central team
```

---

#### 2. Data as a Product

```
Treat data like a product, not a byproduct

Traditional Data:
├─ Dumped into data lake (no quality guarantees)
├─ No SLA (might be stale, incomplete)
├─ No ownership (who do I ask for help?)
└─ No documentation (what does this field mean?)

Data as Product:
├─ ✅ Quality: Schema validation, data quality checks
├─ ✅ SLA: Freshness (<15 min), completeness (>99%)
├─ ✅ Ownership: Clear owner (Slack channel, PagerDuty)
├─ ✅ Documentation: README, data dictionary, examples
└─ ✅ Discoverability: Data catalog, search

Example: "Customer Events" Data Product

Product Spec:
┌────────────────────────────────────────────────────┐
│ Data Product: customer_events                      │
├────────────────────────────────────────────────────┤
│ Owner: marketing-data-team@company.com             │
│ Slack: #marketing-data                             │
│                                                    │
│ Schema:                                            │
│ ├─ event_id: STRING (UUID, required)               │
│ ├─ customer_id: STRING (UUID, required)            │
│ ├─ event_type: STRING (ENUM: click, view, purchase)│
│ ├─ timestamp: TIMESTAMP (UTC, required)            │
│ └─ properties: JSON (optional metadata)            │
│                                                    │
│ SLA:                                               │
│ ├─ Freshness: <5 minutes (P95)                     │
│ ├─ Completeness: >99.9% (no data loss)             │
│ ├─ Availability: 99.9% (43 min downtime/month)     │
│ └─ Schema stability: Backward compatible changes   │
│                                                    │
│ Access:                                            │
│ ├─ Format: Parquet (Iceberg table)                 │
│ ├─ Location: s3://data-mesh/customer_events/       │
│ ├─ Query: Presto (catalog: data_mesh)              │
│ └─ Stream: Kafka (topic: customer-events)          │
│                                                    │
│ Documentation:                                     │
│ ├─ README: https://wiki.company.com/customer-events│
│ ├─ Examples: https://github.com/company/examples   │
│ └─ Changelog: Schema version history               │
└────────────────────────────────────────────────────┘
```

---

#### 3. Self-Service Data Infrastructure Platform

```
Platform team provides infrastructure, not pipelines

Platform Capabilities:
┌────────────────────────────────────────────────────┐
│ 1. Data Pipeline Templates:                       │
│    ├─ Kafka → S3 (Firehose)                        │
│    ├─ Database → S3 (DMS)                          │
│    └─ S3 → Iceberg (Spark job)                     │
│                                                    │
│ 2. Data Quality Framework:                         │
│    ├─ Schema validation (Great Expectations)       │
│    ├─ Freshness checks (data age < SLA)            │
│    └─ Completeness checks (row count reconciliation)│
│                                                    │
│ 3. Observability:                                  │
│    ├─ Metrics (Prometheus dashboards)              │
│    ├─ Logging (Elasticsearch)                      │
│    └─ Alerting (PagerDuty)                         │
│                                                    │
│ 4. Data Catalog:                                   │
│    ├─ Search (Amundsen, DataHub)                   │
│    ├─ Lineage (track data flow)                    │
│    └─ Metadata (owner, SLA, schema)                │
│                                                    │
│ 5. Governance:                                     │
│    ├─ Access control (RBAC)                        │
│    ├─ Data retention policies                      │
│    └─ Compliance (GDPR, encryption)                │
└────────────────────────────────────────────────────┘

Domain teams self-serve using platform ✅
```

---

#### 4. Federated Computational Governance

```
Centralized policies, decentralized execution

Governance Examples:
┌────────────────────────────────────────────────────┐
│ Global Policies (Platform Team):                   │
│ ├─ PII must be encrypted at rest (AES-256)         │
│ ├─ Data retention: 7 years for compliance          │
│ ├─ SLA: P95 freshness <15 minutes                  │
│ └─ Schema: Use Avro/Protobuf (not JSON)            │
│                                                    │
│ Automated Enforcement:                             │
│ ├─ Pipeline CI/CD fails if policy violated         │
│ ├─ Data quality checks run automatically           │
│ └─ Access control enforced by platform             │
└────────────────────────────────────────────────────┘

Domain teams comply automatically (platform enforces) ✅
```

---

### Data Mesh vs Traditional

```
┌──────────────────────┬─────────────────┬─────────────────┐
│ Aspect               │ Traditional     │ Data Mesh       │
├──────────────────────┼─────────────────┼─────────────────┤
│ Ownership            │ Central team    │ Domain teams    │
│ Bottleneck           │ Yes (central)   │ No (distributed)│
│ Scalability          │ Linear (1 team) │ Exponential     │
│ Context              │ Lost            │ Preserved       │
│ Time to Pipeline     │ Weeks           │ Days            │
│ Data Quality         │ Variable        │ Product-grade   │
│ SLA                  │ Best-effort     │ Guaranteed      │
│ Documentation        │ Sparse          │ Required        │
│ Discoverability      │ Manual          │ Catalog         │
└──────────────────────┴─────────────────┴─────────────────┘
```

---

### Challenges of Data Mesh

```
Pros:
├─ ✅ Scales with organization (no central bottleneck)
├─ ✅ Domain expertise (owners understand their data)
├─ ✅ Faster iteration (self-service)
└─ ✅ Clear ownership (no ambiguity)

Cons:
├─ ❌ Complex coordination (100+ data products)
├─ ❌ Requires cultural shift (not just technology)
├─ ❌ Higher initial cost (build self-service platform)
└─ ❌ Risk of fragmentation (if governance weak)

When to Use:
├─ ✅ Large organization (>500 engineers)
├─ ✅ Multiple domains (marketing, sales, engineering, etc.)
├─ ✅ Central team is bottleneck
└─ ✅ Willing to invest in platform

When NOT to Use:
├─ ❌ Small team (<50 engineers)
├─ ❌ Single domain
└─ ❌ Central team works fine
```

---

## 📚 Summary Checklist

- [ ] Understand Lambda Architecture (batch + speed + serving layers)
- [ ] Understand Kappa Architecture (streaming-only with replay)
- [ ] Know when to use Lambda vs Kappa
- [ ] Understand Data Mesh principles (domain ownership, data as product)
- [ ] Design self-service data platforms
- [ ] Implement federated governance
- [ ] Compare centralized vs decentralized data architectures

**Next:** [README.md →](README.md) — Final Capstone Project!
