# Week 15-16: Production Data Systems — EXPERT Track

*"L7+ interviews focus on end-to-end system design at massive scale. You must justify every decision, explain trade-offs, and handle millions of events per second with five-nines availability."* — Distinguished Engineer, Amazon

---

## 🎯 Learning Outcomes

- Master FAANG-level system design interviews
- Design real-time analytics platforms (1M+ events/sec)
- Architect multi-region data lakes with consistency
- Implement streaming ETL with exactly-once guarantees
- Design recommendation engines at Netflix scale
- Handle data mesh architectures
- Optimize for $10M+ annual budgets
- Lead architecture reviews and drive decisions

---

## 🏗️ 1. FAANG System Design: Real-Time Analytics Platform

### Interview Question (Meta L6+)

```
Design a real-time analytics platform for Instagram Stories that:
- Ingests 10M story views/second (peak: 50M/sec)
- Calculates view counts, unique viewers, engagement metrics
- Provides sub-second query latency for creators
- Handles 2B daily active users
- Ensures exactly-once processing (no double-counting)
- Costs <$5M/year to operate

You have 45 minutes. Go.
```

---

### Solution: Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│ Layer 1: Data Ingestion (10M events/sec)                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ Mobile Apps (iOS/Android):                                  │
│ ├─ User views story → Fire event                           │
│ ├─ Batch events locally (100 events/batch)                 │
│ └─ Send to nearest edge location (CloudFront)              │
│         │                                                   │
│         ▼                                                   │
│ ┌────────────────────────────────────────┐                 │
│ │ API Gateway (Regional):                │                 │
│ │ ├─ Rate limiting (1000 req/sec/user)   │                 │
│ │ ├─ Authentication (JWT validation)     │                 │
│ │ ├─ Schema validation (Protobuf)        │                 │
│ │ └─ Write to Kafka (async)              │                 │
│ └────────────────┬───────────────────────┘                 │
│                  ▼                                          │
│ ┌────────────────────────────────────────┐                 │
│ │ Kafka Cluster (Multi-Region):          │                 │
│ │ ├─ 100 partitions (keyed by story_id)  │                 │
│ │ ├─ Replication factor = 3              │                 │
│ │ ├─ Retention = 7 days (replay)         │                 │
│ │ └─ Throughput: 50M events/sec          │                 │
│ └────────────────┬───────────────────────┘                 │
│                                                              │
│ Cost: API Gateway ($1M/year) + Kafka ($500K/year)           │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ Layer 2: Stream Processing (Flink)                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ Flink Job 1: Real-Time Aggregation                          │
│ ┌────────────────────────────────────────┐                 │
│ │ Kafka → Flink → Redis                  │                 │
│ │                                        │                 │
│ │ Processing:                             │                 │
│ │ 1. Deduplicate (based on event_id)     │                 │
│ │ 2. Window: 5-second tumbling           │                 │
│ │ 3. Aggregate:                           │                 │
│ │    - COUNT(DISTINCT viewer_id)          │                 │
│ │    - SUM(watch_time_seconds)            │                 │
│ │    - COUNT(shares), COUNT(replies)      │                 │
│ │ 4. Write to Redis (story_id → metrics)  │                 │
│ │                                        │                 │
│ │ Exactly-Once:                           │                 │
│ │ ├─ Flink checkpointing (every 10s)     │                 │
│ │ ├─ Kafka offset commit in checkpoint   │                 │
│ │ └─ Redis writes idempotent (SET)       │                 │
│ └────────────────────────────────────────┘                 │
│                                                              │
│ Flink Job 2: Historical Aggregation                         │
│ ┌────────────────────────────────────────┐                 │
│ │ Kafka → Flink → Iceberg (S3)           │                 │
│ │                                        │                 │
│ │ Processing:                             │                 │
│ │ 1. Window: 1-minute tumbling            │                 │
│ │ 2. Aggregate same metrics              │                 │
│ │ 3. Write to Iceberg table:             │                 │
│ │    Partition: story_id, hour            │                 │
│ │    Format: Parquet + Snappy             │                 │
│ │                                        │                 │
│ │ Use case: Historical analysis, ML       │                 │
│ └────────────────────────────────────────┘                 │
│                                                              │
│ Cluster Size:                                               │
│ ├─ TaskManagers: 200 (spot instances)                      │
│ ├─ CPUs: 1600 cores (200 × 8)                              │
│ ├─ Memory: 12.8 TB (200 × 64 GB)                           │
│ └─ State Backend: RocksDB on SSD                           │
│                                                              │
│ Cost: $2M/year (mostly spot instances)                      │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ Layer 3: Serving (Query Layer)                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ Real-Time Queries (<100ms):                                 │
│ ┌────────────────────────────────────────┐                 │
│ │ Redis Cluster:                          │                 │
│ │ ├─ 100 nodes (sharded by story_id)     │                 │
│ │ ├─ 10 TB total memory                   │                 │
│ │ ├─ Replication: 2 replicas/shard       │                 │
│ │ └─ Query: GET story:12345:metrics       │                 │
│ │    → {views: 1000000, unique: 500000}   │                 │
│ └────────────────────────────────────────┘                 │
│                                                              │
│ Historical Queries (1-10 seconds):                          │
│ ┌────────────────────────────────────────┐                 │
│ │ Presto/Trino (Query Engine):            │                 │
│ │ ├─ 50 worker nodes                      │                 │
│ │ ├─ Read from Iceberg table (S3)        │                 │
│ │ ├─ Partition pruning (story_id, hour)   │                 │
│ │ └─ Query: SELECT SUM(views) FROM ...    │                 │
│ │    WHERE story_id = 12345               │                 │
│ │    AND hour >= '2025-10-01'             │                 │
│ └────────────────────────────────────────┘                 │
│                                                              │
│ Cost: Redis ($800K/year) + Presto ($500K/year)              │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ Layer 4: Monitoring & Observability                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ Metrics:                                                     │
│ ├─ Prometheus (scrape Flink, Kafka, Redis)                 │
│ ├─ Grafana dashboards (P50/P95/P99 latency)                │
│ └─ Alerting: PagerDuty (SLA violations)                    │
│                                                              │
│ Tracing:                                                     │
│ ├─ Jaeger (distributed tracing)                             │
│ ├─ Trace ID: Follow event from app → Kafka → Flink → Redis │
│ └─ Debug slow queries                                       │
│                                                              │
│ Logging:                                                     │
│ ├─ Elasticsearch (centralized logs)                         │
│ ├─ Kibana (search, visualize)                              │
│ └─ Retention: 30 days                                       │
│                                                              │
│ Cost: $200K/year                                            │
└──────────────────────────────────────────────────────────────┘

TOTAL COST: $1M + $0.5M + $2M + $0.8M + $0.5M + $0.2M
          = $5M/year ✅ (within budget)
```

---

### Deep Dive: Exactly-Once Processing

```python
# Flink job with exactly-once semantics

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.datastream.checkpoint import CheckpointingMode

env = StreamExecutionEnvironment.get_execution_environment()

# Enable checkpointing (exactly-once)
env.enable_checkpointing(10000)  # 10 seconds
env.get_checkpoint_config().set_checkpointing_mode(CheckpointingMode.EXACTLY_ONCE)
env.get_checkpoint_config().set_checkpoint_storage_dir('s3://checkpoints/')

# State backend (RocksDB for large state)
env.set_state_backend(RocksDBStateBackend('s3://state/'))

# Kafka consumer (read from earliest on first run)
kafka_consumer = FlinkKafkaConsumer(
    topics='story-views',
    deserialization_schema=JsonDeserializationSchema(),
    properties={
        'bootstrap.servers': 'kafka:9092',
        'group.id': 'flink-aggregator',
        'enable.auto.commit': 'false',  # Manual offset management
    }
)
kafka_consumer.set_start_from_earliest()

# Deduplication with state
class DeduplicateFunction(KeyedProcessFunction):
    def open(self, runtime_context):
        # TTL state (expire after 1 hour)
        state_descriptor = ValueStateDescriptor(
            'seen_events',
            Types.BOOLEAN(),
        )
        state_descriptor.enable_time_to_live(
            StateTtlConfig.new_builder(Time.hours(1))
                .set_update_type(StateTtlConfig.UpdateType.OnCreateAndWrite)
                .build()
        )
        self.seen_state = runtime_context.get_state(state_descriptor)
    
    def process_element(self, value, ctx):
        event_id = value['event_id']
        
        # Check if seen before
        if self.seen_state.value():
            return  # Skip duplicate
        
        # Mark as seen
        self.seen_state.update(True)
        
        # Emit
        yield value

# Aggregation with windowing
aggregated = (
    env.add_source(kafka_consumer)
    .key_by(lambda x: x['story_id'])
    .process(DeduplicateFunction())
    .key_by(lambda x: x['story_id'])
    .window(TumblingEventTimeWindows.of(Time.seconds(5)))
    .aggregate(
        AggregateFunction(
            create_accumulator=lambda: {'views': 0, 'unique_viewers': set()},
            add=lambda acc, value: {
                'views': acc['views'] + 1,
                'unique_viewers': acc['unique_viewers'] | {value['viewer_id']},
            },
            get_result=lambda acc: {
                'views': acc['views'],
                'unique_viewers': len(acc['unique_viewers']),
            },
            merge=lambda acc1, acc2: {
                'views': acc1['views'] + acc2['views'],
                'unique_viewers': acc1['unique_viewers'] | acc2['unique_viewers'],
            },
        )
    )
)

# Sink to Redis (exactly-once via checkpointing)
redis_sink = RedisSink(
    redis_host='redis-cluster',
    key_template='story:{story_id}:metrics',
    value_serializer=JsonSerializer(),
)

aggregated.add_sink(redis_sink)

env.execute('Story Views Aggregation')
```

**How exactly-once works:**

1. **Checkpoint Coordination:**
   - Flink injects barriers into stream every 10 seconds
   - Barriers flow through pipeline (source → operators → sink)
   - When operator receives barrier: Take snapshot of state

2. **Atomic Commit:**
   - When all operators complete checkpoint:
     - Kafka offsets committed
     - Redis writes committed
     - State snapshots saved to S3
   - If any operator fails: Rollback entire checkpoint

3. **Recovery:**
   - On failure: Restore from last checkpoint
   - Kafka: Rewind to committed offsets
   - Redis: Idempotent writes (SET overwrites)
   - State: Restore from S3

---

### Deep Dive: Cost Optimization

```
Initial Design (Naive): $15M/year
├─ Always-on Flink cluster (200 nodes × $5/hour × 8760 hours)
├─ Redis with 3 replicas (300 nodes × $2/hour × 8760 hours)
└─ Premium S3 storage (100 TB × $0.023/GB × 12 months)

Optimized Design: $5M/year (67% savings)

1. Flink: Spot Instances + Autoscaling
   ├─ Use spot instances (70% discount)
   ├─ Autoscale based on Kafka lag (50-200 nodes)
   ├─ Cost: 125 avg nodes × $1.5/hour × 8760 = $1.6M/year
   └─ Savings: $8.7M - $1.6M = $7.1M ✅

2. Redis: Memory Optimization
   ├─ Compress metrics (JSON → MessagePack): 50% smaller
   ├─ Use Redis Cluster (vs Enterprise): 40% cheaper
   ├─ Expire old data (TTL = 7 days): 80% less memory
   ├─ Cost: 30 nodes × $2/hour × 8760 = $525K/year
   └─ Savings: $5.2M - $525K = $4.7M ✅

3. S3: Lifecycle Policies
   ├─ Hot (last 7 days): Standard (10 TB × $23/month)
   ├─ Warm (8-30 days): S3-IA (20 TB × $12.5/month)
   ├─ Cold (31-365 days): Glacier (100 TB × $4/month)
   ├─ Archive (>365 days): Glacier Deep (200 TB × $1/month)
   ├─ Cost: $230 + $250 + $400 + $200 = $1080/month = $13K/year
   └─ Savings: $276K - $13K = $263K ✅

4. Network: VPC Endpoints
   ├─ Avoid NAT Gateway ($0.045/GB): Use VPC endpoints
   ├─ Compress before transfer (Snappy): 3x smaller
   ├─ Cost: $50K/year
   └─ Savings: $500K - $50K = $450K ✅

5. Kafka: Tiered Storage
   ├─ Hot (last 7 days): Local SSD (fast, expensive)
   ├─ Cold (8-90 days): S3 tiered storage (slow, cheap)
   ├─ Cost: $300K/year
   └─ Savings: $800K - $300K = $500K ✅

Total Savings: $7.1M + $4.7M + $263K + $450K + $500K = $13M
Final Cost: $15M - $13M = $2M/year (with $3M buffer)
```

---

## 🌐 2. System Design: Multi-Region Data Lake

### Interview Question (AWS L7+)

```
Design Airbnb's data lake that:
- Stores 500 PB of data (listings, bookings, reviews, events)
- Supports 10K analysts running SQL queries
- Handles 100M events/day from 7M listings
- Multi-region (US, EU, APAC) with <1 second latency
- Complies with GDPR (EU data stays in EU)
- Costs <$10M/year

45 minutes. Design, justify, optimize.
```

---

### Solution: Architecture

```
┌──────────────────────────────────────────────────────────────┐
│ Region 1: US (Primary)                                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ Data Sources:                                                │
│ ├─ Application databases (RDS, DynamoDB)                    │
│ ├─ Kafka streams (user events, bookings)                    │
│ └─ Third-party APIs (payment providers)                     │
│         │                                                    │
│         ▼                                                    │
│ ┌────────────────────────────────────────┐                  │
│ │ Ingestion Layer:                       │                  │
│ │ ├─ Firehose → S3 (clickstream)         │                  │
│ │ ├─ DMS → S3 (CDC from RDS)             │                  │
│ │ └─ Lambda → S3 (API polling)           │                  │
│ └────────────────┬───────────────────────┘                  │
│                  ▼                                           │
│ ┌────────────────────────────────────────┐                  │
│ │ S3 Data Lake (Iceberg):                │                  │
│ │ ├─ Raw zone: JSON/Avro (7 days)        │                  │
│ │ ├─ Cleaned zone: Parquet (90 days)     │                  │
│ │ ├─ Curated zone: Aggregated (365 days) │                  │
│ │ └─ Archive zone: Glacier (7 years)     │                  │
│ │                                        │                  │
│ │ Partitioning: region, date, entity     │                  │
│ │ Size: 200 PB (US listings + bookings)  │                  │
│ └────────────────┬───────────────────────┘                  │
│                  ▼                                           │
│ ┌────────────────────────────────────────┐                  │
│ │ Query Engines:                          │                  │
│ │ ├─ Presto (ad-hoc queries)             │                  │
│ │ ├─ Spark (batch ETL)                   │                  │
│ │ └─ Athena (serverless queries)         │                  │
│ └────────────────────────────────────────┘                  │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ Region 2: EU (GDPR Compliant)                                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ Data Sources:                                                │
│ ├─ EU-only data (listings, users, bookings in EU)          │
│ └─ NO cross-region transfer (GDPR requirement)              │
│         │                                                    │
│         ▼                                                    │
│ ┌────────────────────────────────────────┐                  │
│ │ S3 Data Lake (EU-only):                │                  │
│ │ ├─ Encrypted with EU KMS keys           │                  │
│ │ ├─ Access restricted to EU resources    │                  │
│ │ └─ Size: 150 PB (EU listings)           │                  │
│ └────────────────┬───────────────────────┘                  │
│                  ▼                                           │
│ ┌────────────────────────────────────────┐                  │
│ │ Query Engines (EU-only):                │                  │
│ │ ├─ Presto cluster (EU analysts)         │                  │
│ │ └─ Athena (EU compliance team)          │                  │
│ └────────────────────────────────────────┘                  │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ Region 3: APAC                                               │
├──────────────────────────────────────────────────────────────┤
│ Similar to US, size: 150 PB                                  │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ Global Query Federation:                                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ Trino Coordinator (Global):                                 │
│ ├─ Query: "SELECT COUNT(*) FROM bookings"                   │
│ ├─ Plan: Federate across US + EU + APAC                    │
│ ├─ Execute: Workers read local S3                          │
│ └─ Merge results from 3 regions                            │
│                                                              │
│ GDPR Enforcement:                                            │
│ ├─ Query: "SELECT * FROM users WHERE region = 'EU'"         │
│ ├─ Plan: Only read from EU data lake                       │
│ └─ Block: Cannot export EU data to non-EU regions           │
└──────────────────────────────────────────────────────────────┘
```

---

### Deep Dive: GDPR Compliance

```python
# Trino query planner with GDPR enforcement

class GDPRQueryPlanner:
    def plan_query(self, sql, user_region):
        """
        Enforce GDPR: EU data cannot leave EU
        """
        # Parse SQL
        query = parse_sql(sql)
        
        # Extract referenced tables
        tables = extract_tables(query)
        
        # Check data residency
        for table in tables:
            table_region = get_table_region(table)
            
            if table_region == 'EU' and user_region != 'EU':
                # GDPR violation: EU data accessed from non-EU
                raise GDPRViolation(
                    f"Cannot access EU table '{table}' from region '{user_region}'"
                )
            
            if table_region == 'EU':
                # Ensure query runs in EU region only
                query_region = 'EU'
            else:
                query_region = user_region
        
        # Plan execution
        plan = {
            'query': sql,
            'region': query_region,
            'workers': get_workers(query_region),
            's3_paths': [f's3://{query_region}-data-lake/{table}' for table in tables],
        }
        
        return plan

# Example: Compliant query
plan = GDPRQueryPlanner().plan_query(
    sql="SELECT COUNT(*) FROM eu_users WHERE country = 'France'",
    user_region='EU',
)
# Result: Run in EU region ✅

# Example: Blocked query
plan = GDPRQueryPlanner().plan_query(
    sql="SELECT * FROM eu_users",
    user_region='US',
)
# Result: GDPRViolation exception ❌
```

---

### Deep Dive: Cost Breakdown

```
Total Cost: $10M/year

1. Storage (S3):
   ├─ 500 PB total
   ├─ Hot (7 days): 5 PB × $23/TB/month = $115K/month
   ├─ Warm (90 days): 50 PB × $12.5/TB/month = $625K/month
   ├─ Cold (365 days): 200 PB × $4/TB/month = $800K/month
   ├─ Archive (7 years): 245 PB × $1/TB/month = $245K/month
   └─ Total: $1.785M/month = $21.4M/year ❌ Over budget!
   
   Optimization:
   ├─ Compress with Zstd: 500 PB → 150 PB (3x compression)
   ├─ Deduplicate: 150 PB → 120 PB (20% dedup)
   ├─ Delete old data: 120 PB → 100 PB (retention policy)
   └─ Cost: 100 PB × weighted avg ($5/TB/month) = $500K/month = $6M/year ✅

2. Compute (Presto/Spark):
   ├─ 100 nodes × $2/hour × 8760 hours = $1.75M/year ❌
   
   Optimization:
   ├─ Autoscale: 20-100 nodes (avg 40 nodes)
   ├─ Spot instances (70% discount)
   ├─ Cost: 40 nodes × $0.6/hour × 8760 = $210K/year ✅

3. Network:
   ├─ Cross-region queries: 10 TB/day × $0.02/GB × 365 = $73K/year
   ├─ Optimization: Use S3 replication (cheaper)
   └─ Cost: $50K/year ✅

4. Metadata (Glue Catalog):
   ├─ 100M objects × $1/million/month = $100/month = $1.2K/year ✅

5. Monitoring:
   ├─ CloudWatch, X-Ray, Grafana
   └─ Cost: $100K/year ✅

Total: $6M + $210K + $50K + $1.2K + $100K = $6.36M/year ✅ (36% under budget)
```

---

## 🎬 3. System Design: Recommendation Engine (Netflix Scale)

### Interview Question (Netflix L8+)

```
Design Netflix's recommendation engine that:
- Serves 200M subscribers
- Generates personalized recommendations in <200ms
- Processes 1B viewing events/day
- Trains ML models on 10 years of data (100 PB)
- A/B tests 100+ models simultaneously
- Costs <$20M/year

60 minutes. Focus on ML pipeline + serving infrastructure.
```

---

### Solution: Architecture

```
┌──────────────────────────────────────────────────────────────┐
│ Offline Layer: ML Training                                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ Data Lake (Iceberg):                                         │
│ ├─ 100 PB historical data (10 years)                        │
│ ├─ 1B events/day (watch, pause, rewind, skip)              │
│ └─ Partitioned by date, user_segment                        │
│         │                                                    │
│         ▼                                                    │
│ ┌────────────────────────────────────────┐                  │
│ │ Feature Engineering (Spark):            │                  │
│ │ ├─ User features:                       │                  │
│ │ │  ├─ Watch history (last 90 days)      │                  │
│ │ │  ├─ Genre preferences                 │                  │
│ │ │  └─ Time-of-day patterns              │                  │
│ │ ├─ Item features:                       │                  │
│ │  ├─ Metadata (genre, cast, director)   │                  │
│ │  ├─ Popularity metrics                  │                  │
│ │  └─ Engagement scores                   │                  │
│ │ └─ Interaction features:                │                  │
│ │    ├─ Collaborative filtering           │                  │
│ │    └─ Content-based filtering           │                  │
│ └────────────────┬───────────────────────┘                  │
│                  ▼                                           │
│ ┌────────────────────────────────────────┐                  │
│ │ Model Training (TensorFlow):            │                  │
│ │ ├─ Two-Tower DNN (user × item)          │                  │
│ │ ├─ Training:                            │                  │
│ │ │  ├─ 1000 GPU cluster (A100)           │                  │
│ │ │  ├─ Distributed training (Horovod)    │                  │
│ │ │  └─ 7 days to train 1 model           │                  │
│ │ ├─ Hyperparameter tuning (Optuna)       │                  │
│ │ └─ Model versioning (MLflow)            │                  │
│ └────────────────┬───────────────────────┘                  │
│                  ▼                                           │
│ ┌────────────────────────────────────────┐                  │
│ │ Model Evaluation:                       │                  │
│ │ ├─ Offline metrics:                     │                  │
│ │ │  ├─ AUC, Precision@K, Recall@K        │                  │
│ │ │  └─ NDCG (ranking quality)            │                  │
│ │ ├─ A/B test framework:                  │                  │
│ │ │  ├─ Deploy to 1% of users             │                  │
│ │ │  ├─ Measure watch time, engagement    │                  │
│ │ │  └─ Promote if +2% watch time         │                  │
│ │ └─ Shadow testing (log predictions)     │                  │
│ └────────────────────────────────────────┘                  │
│                                                              │
│ Cost: $8M/year (GPU training + Spark)                        │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ Online Layer: Real-Time Serving                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ ┌────────────────────────────────────────┐                  │
│ │ User Request:                           │                  │
│ │ "Show homepage recommendations"         │                  │
│ └────────────────┬───────────────────────┘                  │
│                  ▼                                           │
│ ┌────────────────────────────────────────┐                  │
│ │ API Gateway + Feature Store:            │                  │
│ │ ├─ Get user features (DynamoDB):        │                  │
│ │ │  ├─ user_id → watch_history           │                  │
│ │ │  └─ Cached in Redis (10M users)       │                  │
│ │ ├─ Get item features (Cassandra):       │                  │
│ │ │  ├─ 100K titles × 500 features        │                  │
│ │ │  └─ Precomputed, updated hourly       │                  │
│ │ └─ Latency: 20ms                        │                  │
│ └────────────────┬───────────────────────┘                  │
│                  ▼                                           │
│ ┌────────────────────────────────────────┐                  │
│ │ Candidate Generation:                   │                  │
│ │ ├─ Retrieve top 1000 candidates         │                  │
│ │ ├─ Methods:                             │                  │
│ │ │  ├─ Collaborative filtering (ANN)     │                  │
│ │ │  ├─ Content-based (similar titles)    │                  │
│ │ │  └─ Trending (popular today)          │                  │
│ │ └─ Latency: 50ms                        │                  │
│ └────────────────┬───────────────────────┘                  │
│                  ▼                                           │
│ ┌────────────────────────────────────────┐                  │
│ │ Ranking (TensorFlow Serving):           │                  │
│ │ ├─ Score 1000 candidates                │                  │
│ │ ├─ Model: Two-Tower DNN                 │                  │
│ │ ├─ Batch inference (100 items/batch)    │                  │
│ │ ├─ Return top 50 ranked items           │                  │
│ │ └─ Latency: 100ms                       │                  │
│ └────────────────┬───────────────────────┘                  │
│                  ▼                                           │
│ ┌────────────────────────────────────────┐                  │
│ │ Post-Processing:                        │                  │
│ │ ├─ Diversity (avoid same genre)         │                  │
│ │ ├─ Freshness (mix old + new titles)     │                  │
│ │ ├─ Business rules (promote originals)   │                  │
│ │ └─ Latency: 10ms                        │                  │
│ └────────────────┬───────────────────────┘                  │
│                  ▼                                           │
│ ┌────────────────────────────────────────┐                  │
│ │ Response:                               │                  │
│ │ [Title1, Title2, ..., Title50]          │                  │
│ │ Total Latency: 20+50+100+10 = 180ms ✅  │                  │
│ └────────────────────────────────────────┘                  │
│                                                              │
│ Infrastructure:                                              │
│ ├─ TF Serving: 500 instances (CPU)                          │
│ ├─ Feature Store: 200 DynamoDB nodes                        │
│ ├─ Candidate Gen: 100 instances (CPU + ANN index)           │
│ └─ Cost: $10M/year                                          │
└──────────────────────────────────────────────────────────────┘

TOTAL COST: $8M (offline) + $10M (online) = $18M/year ✅
```

---

### Deep Dive: ANN for Candidate Generation

```python
# Approximate Nearest Neighbor (ANN) for fast retrieval

import faiss
import numpy as np

# 1. Build index (offline)
class ANNIndex:
    def __init__(self, embedding_dim=128):
        self.embedding_dim = embedding_dim
        
        # HNSW index (Hierarchical Navigable Small World)
        self.index = faiss.IndexHNSWFlat(embedding_dim, 32)
        self.index.hnsw.efConstruction = 40
        self.item_ids = []
    
    def build(self, item_embeddings):
        """
        item_embeddings: dict {item_id: embedding (128-dim vector)}
        """
        # Convert to numpy array
        item_ids = list(item_embeddings.keys())
        embeddings = np.array([item_embeddings[id] for id in item_ids], dtype='float32')
        
        # Add to index
        self.index.add(embeddings)
        self.item_ids = item_ids
        
        print(f"Built index with {len(item_ids)} items")
    
    def search(self, user_embedding, k=1000):
        """
        Find k nearest items to user embedding
        """
        # Search index
        distances, indices = self.index.search(
            np.array([user_embedding], dtype='float32'),
            k
        )
        
        # Map indices to item IDs
        candidates = [(self.item_ids[idx], distances[0][i]) 
                      for i, idx in enumerate(indices[0])]
        
        return candidates

# 2. Online serving
ann_index = ANNIndex()
ann_index.load_from_disk('/models/ann_index.faiss')

def get_recommendations(user_id):
    # Get user embedding (from feature store)
    user_embedding = feature_store.get_user_embedding(user_id)
    
    # Search ANN index (50ms)
    candidates = ann_index.search(user_embedding, k=1000)
    
    # candidates = [(item_id, distance), ...]
    return [item_id for item_id, _ in candidates]

# Performance:
# ├─ Brute-force (dot product with 100K items): 500ms
# └─ HNSW ANN (approximate): 50ms ✅ (10x faster, 99% recall)
```

---

## 📚 Summary: FAANG Interview Checklist

### System Design Framework (45-60 minutes)

```
1. Clarify Requirements (5 min):
   ├─ Functional: What features? (read-heavy vs write-heavy)
   ├─ Non-functional: Scale? Latency? Availability?
   └─ Constraints: Budget? Existing infrastructure?

2. High-Level Design (10 min):
   ├─ Draw boxes: Client → API → Processing → Storage
   ├─ Identify bottlenecks
   └─ Choose technologies (justify each choice)

3. Deep Dive (20 min):
   ├─ Pick 2-3 components to detail
   ├─ Examples:
   │  ├─ How does exactly-once work?
   │  ├─ How do you handle hot partitions?
   │  └─ How do you ensure GDPR compliance?
   └─ Show code/pseudocode if helpful

4. Trade-Offs (5 min):
   ├─ Explain alternatives considered
   ├─ Justify final decisions
   └─ Example: "Chose Kafka over Kinesis because..."

5. Optimizations (5 min):
   ├─ Performance: Caching, indexing, partitioning
   ├─ Cost: Spot instances, lifecycle policies
   └─ Reliability: Multi-region, backups

6. Monitoring (3 min):
   ├─ Metrics to track (latency, errors, throughput)
   ├─ Alerts (SLA violations)
   └─ Debugging (tracing, logging)

7. Q&A (7 min):
   ├─ Answer follow-up questions
   └─ Admit unknowns ("I'd research X before implementing")
```

---

### Common Pitfalls to Avoid

```
❌ Don't:
├─ Jump into implementation without clarifying requirements
├─ Over-engineer (add complexity without justification)
├─ Ignore trade-offs (every decision has pros/cons)
├─ Forget about cost (unlimited budget doesn't exist)
├─ Neglect monitoring (how do you know it works?)
└─ Use buzzwords without understanding (e.g., "microservices solve everything")

✅ Do:
├─ Ask clarifying questions early
├─ Start simple, then scale
├─ Justify every technology choice
├─ Mention cost at least once
├─ Discuss monitoring and alerting
└─ Show deep understanding of 2-3 technologies
```

---

**Next:** [WHITEPAPERS.md →](WHITEPAPERS.md)
