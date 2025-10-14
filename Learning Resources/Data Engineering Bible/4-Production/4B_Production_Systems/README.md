# Week 15-16: Production Data Systems & Capstone

**Duration:** 2 weeks  
**Difficulty:** Expert  
**Prerequisites:** Weeks 1-14 (Entire curriculum)

---

## 🎓 Module Overview

This final module brings together everything you've learned across 16 weeks to build **production-grade data systems at FAANG scale**. You'll master:

1. **Architecture Patterns:** Lambda, Kappa, Data Mesh
2. **Trade-Off Analysis:** CAP theorem, consistency models, cost optimization
3. **System Design:** Real-time analytics, data lakes, recommendation engines
4. **Production Operations:** Monitoring, alerting, disaster recovery
5. **FAANG Interviews:** L6+ system design questions

By the end of this module, you will:
- Design end-to-end data platforms serving 100M+ users
- Justify every architectural decision with trade-offs
- Optimize for $10M+ annual budgets
- Pass L6+ system design interviews at FAANG companies
- Lead architecture reviews as a Principal Engineer

---

## 🗓️ 2-Week Learning Path

### Week 15: Production Fundamentals + Trade-Offs

#### Day 1-2: Production vs Development
- **Theory:** Production readiness checklist (observability, reliability, security)
- **Reading:** [BEGINNER.md](BEGINNER.md) — Sections 1-2
- **Hands-on:** Build monitoring dashboard (Prometheus + Grafana)
  ```python
  # Track pipeline metrics
  metrics.gauge('pipeline.records.per_second', records_per_sec)
  metrics.histogram('pipeline.latency', latency_ms)
  metrics.increment('pipeline.errors.total')
  ```
- **Exercise:** Implement SLA monitoring with alerting (PagerDuty)

#### Day 3-4: Architecture Patterns
- **Theory:** Batch, streaming, Lambda, Kappa
- **Reading:** [BEGINNER.md](BEGINNER.md) — Section 2 + [WHITEPAPERS.md](WHITEPAPERS.md) — Papers 1-2
- **Hands-on:** Compare Lambda vs Kappa for pageview counting
  ```
  Lambda:  Batch (Spark) + Speed (Flink) → Merge in serving layer
  Kappa:   Stream (Flink) + Replay Kafka for reprocessing
  ```
- **Exercise:** When would you choose Lambda over Kappa? Justify.

#### Day 5-6: CAP Theorem & Consistency Models
- **Theory:** CAP, PACELC, linearizability to eventual consistency
- **Reading:** [INTERMEDIATE.md](INTERMEDIATE.md) — Sections 1-3
- **Hands-on:** Configure Cassandra consistency levels
  ```python
  # Strong consistency: R + W > N
  session.execute(query, consistency_level=ConsistencyLevel.QUORUM)
  
  # Eventual consistency: R + W ≤ N
  session.execute(query, consistency_level=ConsistencyLevel.ONE)
  ```
- **Quiz:** CP vs AP systems—which would you choose for banking? Social media?

#### Day 7-8: Cost Optimization
- **Theory:** Compute, storage, network optimization strategies
- **Reading:** [INTERMEDIATE.md](INTERMEDIATE.md) — Section 4
- **Hands-on:** Reduce $100K/month pipeline to $30K/month
  ```
  Optimizations:
  ├─ Spot instances + autoscaling (70% discount)
  ├─ S3 lifecycle policies (hot → warm → cold → Glacier)
  ├─ Compress with Parquet + Snappy (3x smaller)
  └─ VPC endpoints (avoid NAT gateway costs)
  ```
- **Exercise:** Estimate cost for 10M events/day pipeline

#### Day 9-10: SLA/SLI/SLO Framework
- **Theory:** Error budgets, P50/P95/P99 latency
- **Reading:** [INTERMEDIATE.md](INTERMEDIATE.md) — Section 5
- **Hands-on:** Define SLOs for data pipeline
  ```yaml
  SLOs:
    latency_p95: 300s  # 5 minutes
    availability: 99.9%  # 43 min downtime/month
    freshness: 900s  # 15 minutes max staleness
  ```
- **Exercise:** Calculate error budget consumption

---

### Week 16: Expert System Design + Capstone

#### Day 11-12: Real-Time Analytics Platform
- **Theory:** 10M events/sec, exactly-once, sub-second latency
- **Reading:** [EXPERT.md](EXPERT.md) — Section 1
- **Hands-on:** Design Instagram Stories analytics
  ```
  Architecture:
  ├─ Ingestion: Kafka (100 partitions)
  ├─ Processing: Flink (exactly-once checkpointing)
  ├─ Serving: Redis (real-time) + Presto (historical)
  └─ Cost: $5M/year
  ```
- **Interview Question:** "How do you ensure exactly-once processing?"

#### Day 13-14: Multi-Region Data Lake
- **Theory:** GDPR compliance, multi-region replication
- **Reading:** [EXPERT.md](EXPERT.md) — Section 2
- **Hands-on:** Design Airbnb's 500 PB data lake
  ```
  Regions: US (200 PB), EU (150 PB, GDPR), APAC (150 PB)
  Query Federation: Trino (global coordinator)
  Cost: $6M/year (optimized from $21M)
  ```
- **Interview Question:** "How do you enforce GDPR data residency?"

#### Day 15-16: Recommendation Engine
- **Theory:** Netflix scale (200M users, <200ms latency)
- **Reading:** [EXPERT.md](EXPERT.md) — Section 3
- **Hands-on:** Design two-layer architecture
  ```
  Offline: ML training (Spark, TensorFlow, 1000 GPUs)
  Online: Serving (TF Serving, ANN index, Redis)
  Cost: $18M/year
  ```
- **Interview Question:** "How do you A/B test 100 models simultaneously?"

#### Day 17: Data Mesh Architecture
- **Theory:** Domain ownership, data as product
- **Reading:** [WHITEPAPERS.md](WHITEPAPERS.md) — Paper 3
- **Hands-on:** Design self-service data platform
  ```
  Principles:
  ├─ Domain-oriented decentralization
  ├─ Data as a product (SLA, quality, docs)
  ├─ Self-service platform
  └─ Federated governance
  ```
- **Discussion:** When to use Data Mesh vs centralized data team?

#### Day 18: Interview Preparation
- **Reading:** [EXPERT.md](EXPERT.md) — Summary section
- **Practice:** System design interview framework (45 minutes)
  ```
  1. Clarify requirements (5 min)
  2. High-level design (10 min)
  3. Deep dive (20 min)
  4. Trade-offs (5 min)
  5. Optimizations (5 min)
  ```
- **Mock Interview:** Uber's real-time surge pricing system

---

## 🏆 Capstone Project: Design Uber's Data Platform

### Requirements

You are interviewing for **Principal Data Engineer (L7)** at Uber. Design the data platform that powers:

1. **Real-Time Surge Pricing:**
   - 10M rides/day (peak: 100K rides/hour)
   - Calculate surge multiplier every 30 seconds per city zone
   - Latency: <5 seconds (rider sees surge before booking)

2. **Driver Matching:**
   - Match 1M drivers to riders in <200ms
   - Consider: Distance, ETA, ratings, acceptance rate
   - Optimize for lowest ETA + driver utilization

3. **Analytics & Reporting:**
   - Analysts query historical data (3 years, 10 PB)
   - ML models train on full dataset (fraud detection, ETA prediction)
   - Dashboards update every 5 minutes (city metrics, KPIs)

4. **Constraints:**
   - Budget: $20M/year
   - Availability: 99.99% (52 min downtime/year)
   - Compliance: GDPR (EU data stays in EU), CCPA (California)
   - Scale: 100+ countries, 10K cities

**You have 60 minutes. Design, justify, optimize.**

---

### Solution: Architecture

```
┌──────────────────────────────────────────────────────────────┐
│ Layer 1: Real-Time Ingestion (10M rides/day)                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ Data Sources:                                                │
│ ├─ Driver locations (GPS every 5 seconds, 1M drivers)       │
│ ├─ Ride requests (user opens app, requests ride)            │
│ ├─ Trip events (start, end, cancel, payment)                │
│ └─ Surge calculations (per zone, every 30 seconds)          │
│         │                                                    │
│         ▼                                                    │
│ ┌────────────────────────────────────────┐                  │
│ │ Kafka (Multi-Region):                  │                  │
│ │ ├─ Topics:                             │                  │
│ │ │  ├─ driver-locations (1K partitions) │                  │
│ │ │  ├─ ride-requests (100 partitions)   │                  │
│ │ │  └─ trip-events (100 partitions)     │                  │
│ │ ├─ Replication: 3x (fault tolerance)   │                  │
│ │ └─ Retention: 7 days (replay)          │                  │
│ └────────────────────────────────────────┘                  │
│                                                              │
│ Cost: $2M/year                                              │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ Layer 2: Stream Processing (Flink)                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ Job 1: Surge Pricing (Per City Zone)                        │
│ ┌────────────────────────────────────────┐                  │
│ │ Input: ride-requests, driver-locations │                  │
│ │                                        │                  │
│ │ Processing (30-second tumbling window):│                  │
│ │ 1. Group by city_zone                  │                  │
│ │ 2. Calculate:                          │                  │
│ │    demand = COUNT(ride_requests)       │                  │
│ │    supply = COUNT(available_drivers)   │                  │
│ │ 3. Surge multiplier:                   │                  │
│ │    if demand > supply × 1.5:           │                  │
│ │       surge = min(3.0, demand/supply)  │                  │
│ │    else:                                │                  │
│ │       surge = 1.0                      │                  │
│ │ 4. Write to Redis (city_zone → surge)  │                  │
│ │                                        │                  │
│ │ Exactly-once: Flink checkpointing      │                  │
│ └────────────────────────────────────────┘                  │
│                                                              │
│ Job 2: Trip Aggregation (Historical)                        │
│ ┌────────────────────────────────────────┐                  │
│ │ Input: trip-events                      │                  │
│ │ Output: Iceberg table (S3)             │                  │
│ │ Partition: city, date, hour            │                  │
│ │ Use case: Analytics, ML training       │                  │
│ └────────────────────────────────────────┘                  │
│                                                              │
│ Cluster: 200 nodes (spot instances)                         │
│ Cost: $4M/year                                              │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ Layer 3: Serving (Low Latency)                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ Real-Time Data (Redis Cluster):                             │
│ ┌────────────────────────────────────────┐                  │
│ │ Data:                                  │                  │
│ │ ├─ Surge multipliers (city_zone → 1.5)│                  │
│ │ ├─ Driver locations (driver_id → GPS) │                  │
│ │ └─ Rider state (rider_id → status)    │                  │
│ │                                        │                  │
│ │ Cluster: 100 nodes (sharded)           │                  │
│ │ Replication: 2x                        │                  │
│ │ Query latency: <10ms (P99)             │                  │
│ └────────────────────────────────────────┘                  │
│                                                              │
│ Historical Data (Iceberg on S3):                            │
│ ┌────────────────────────────────────────┐                  │
│ │ Storage: 10 PB (3 years history)       │                  │
│ │ Query Engine: Presto (100 workers)     │                  │
│ │ Query latency: <10 seconds (P95)       │                  │
│ └────────────────────────────────────────┘                  │
│                                                              │
│ Cost: $3M/year (Redis) + $4M/year (S3 + Presto) = $7M/year  │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ Layer 4: Driver Matching (Microservice)                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ Matching Algorithm:                                          │
│ ┌────────────────────────────────────────┐                  │
│ │ 1. Rider requests ride (lat, lon)      │                  │
│ │ 2. Query Redis:                        │                  │
│ │    drivers_nearby = geosearch(         │                  │
│ │      lat, lon, radius=5km              │                  │
│ │    )                                   │                  │
│ │ 3. Score drivers:                      │                  │
│ │    score = (                           │                  │
│ │      0.6 × (1 / ETA)                   │                  │
│ │      + 0.2 × rating                    │                  │
│ │      + 0.2 × acceptance_rate           │                  │
│ │    )                                   │                  │
│ │ 4. Select top driver                   │                  │
│ │ 5. Send match request (async)          │                  │
│ │                                        │                  │
│ │ Latency: <200ms (P95)                  │                  │
│ │ Throughput: 10K matches/second         │                  │
│ └────────────────────────────────────────┘                  │
│                                                              │
│ Infrastructure: Kubernetes (500 pods, autoscale)             │
│ Cost: $2M/year                                              │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ Layer 5: ML Training (Offline)                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ Use Cases:                                                   │
│ ├─ ETA prediction (gradient boosting)                       │
│ ├─ Fraud detection (anomaly detection)                      │
│ └─ Demand forecasting (LSTM)                                │
│                                                              │
│ Pipeline:                                                    │
│ 1. Read from Iceberg (10 PB, 3 years)                       │
│ 2. Feature engineering (Spark)                              │
│ 3. Training (TensorFlow, 100 GPUs)                          │
│ 4. Model serving (TF Serving)                               │
│                                                              │
│ Cost: $3M/year (mostly GPU)                                 │
└──────────────────────────────────────────────────────────────┘

TOTAL COST: $2M + $4M + $7M + $2M + $3M = $18M/year ✅
(Within $20M budget, 10% buffer)
```

---

### Deep Dive: GDPR Compliance

```python
# Enforce GDPR: EU data stays in EU

class GDPREnforcer:
    def __init__(self):
        self.regions = {
            'EU': ['eu-west-1', 'eu-central-1'],
            'US': ['us-east-1', 'us-west-2'],
            'APAC': ['ap-south-1', 'ap-southeast-1'],
        }
    
    def route_data(self, user_location, data):
        """Route data to correct region based on GDPR"""
        # Determine user region
        user_region = self.get_user_region(user_location)
        
        if user_region == 'EU':
            # GDPR: Store in EU-only
            kafka_topic = 'eu-trip-events'
            s3_bucket = 's3://uber-eu-data-lake/'
            
            # Encrypt with EU KMS key
            encrypted_data = self.encrypt(data, kms_key_region='eu-west-1')
            
            # Write to EU Kafka cluster
            kafka_producer.send(kafka_topic, encrypted_data, region='eu-west-1')
            
            # Block cross-region transfer
            assert not self.is_cross_region_transfer(kafka_topic, 'US')
        else:
            # Non-EU: Standard processing
            kafka_topic = 'trip-events'
            s3_bucket = 's3://uber-data-lake/'
            kafka_producer.send(kafka_topic, data)
    
    def query_data(self, user_region, query):
        """Enforce query region restrictions"""
        if 'eu_users' in query and user_region != 'EU':
            raise GDPRViolation(
                "Cannot query EU data from non-EU region"
            )
        
        # Route query to correct region
        if user_region == 'EU':
            return presto.execute(query, catalog='eu_data_lake')
        else:
            return presto.execute(query, catalog='data_lake')
```

---

### Performance Optimization

```
Bottleneck 1: Driver Location Updates (1M drivers × 12 updates/min)
├─ Problem: 200K writes/second to Redis
├─ Solution: Batch updates (100 locations/batch)
└─ Result: 2K batches/second ✅

Bottleneck 2: Surge Calculation (10K zones × 2 calculations/min)
├─ Problem: High CPU usage in Flink
├─ Solution: Parallel processing (1 zone/partition)
└─ Result: 10K partitions, 100 cores ✅

Bottleneck 3: Historical Queries (10 PB Iceberg table)
├─ Problem: Slow scans (1 hour for full table)
├─ Solution: Partition pruning (city, date, hour)
└─ Result: Query 1 day = 10 min ✅ (99% data skipped)

Cost Optimization:
├─ Flink: Spot instances (70% discount) → Save $8M/year
├─ S3: Lifecycle policies (Glacier) → Save $3M/year
├─ Redis: Compress data (50% smaller) → Save $1.5M/year
└─ Total Savings: $12.5M/year
```

---

## 📊 Assessment: Principal Engineer Interview

### System Design Question 1 (60 minutes)

**Design YouTube's video recommendation system that:**
- Serves 2B users
- Generates personalized recommendations in <100ms
- Processes 500M watch events/day
- Trains on 15 years of data (1 exabyte)
- A/B tests 500+ models simultaneously
- Costs <$50M/year

**What the interviewer is looking for:**
1. Clarify requirements (functional, scale, latency, cost)
2. High-level architecture (ingestion, processing, serving, ML)
3. Deep dive on 2-3 components (candidate generation, ranking, A/B testing)
4. Trade-offs (batch vs streaming, CP vs AP, cost vs latency)
5. Optimizations (caching, ANN, model compression)
6. Monitoring (SLAs, metrics, alerting)

---

### System Design Question 2 (60 minutes)

**Design DoorDash's delivery dispatch system that:**
- Matches 10M orders/day to drivers
- Optimizes for: Delivery time, driver utilization, food quality
- Handles constraints: Driver capacity, restaurant prep time, traffic
- Multi-objective optimization (Pareto frontier)
- Real-time updates (order ready, driver arrived)
- Latency: <500ms per match

**What the interviewer is looking for:**
1. Constraint programming vs heuristic algorithms
2. How to handle dynamic updates (order ready early)
3. Multi-objective optimization (weighted scoring)
4. Scalability (10M orders → 100M orders)
5. Failure handling (driver cancels, restaurant closed)
6. Cost analysis (compute, storage, network)

---

## ✅ Module Completion Checklist

### Beginner Level
- [ ] Understand production readiness checklist
- [ ] Identify common architecture patterns (batch, streaming, Lambda, Kappa)
- [ ] Recognize anti-patterns (no monitoring, hardcoded config)
- [ ] Implement basic monitoring (metrics, logging, alerting)
- [ ] Design simple ETL pipeline with error handling

### Intermediate Level
- [ ] Apply CAP theorem to system design decisions
- [ ] Choose appropriate consistency model (CP vs AP)
- [ ] Optimize costs (compute, storage, network)
- [ ] Define SLAs, SLIs, SLOs with error budgets
- [ ] Design multi-region architectures
- [ ] Implement disaster recovery (RTO/RPO)

### Expert Level
- [ ] Design real-time analytics platform (10M+ events/sec)
- [ ] Architect multi-region data lake with GDPR compliance
- [ ] Build recommendation engine at Netflix scale
- [ ] Implement Data Mesh architecture
- [ ] Pass L6+ FAANG system design interviews
- [ ] Lead architecture reviews as Principal Engineer

### Capstone Project
- [ ] Design Uber's data platform (surge pricing, driver matching, analytics)
- [ ] Justify every architectural decision with trade-offs
- [ ] Optimize for $20M/year budget
- [ ] Handle 99.99% availability SLA
- [ ] Ensure GDPR/CCPA compliance
- [ ] Present to mock interview panel (60 minutes)

---

## 🎯 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Interview Success** | Pass L6+ system design | Mock interviews |
| **System Design** | End-to-end architecture in 45 min | Timed practice |
| **Trade-Off Analysis** | Justify every decision | Peer review |
| **Cost Optimization** | Reduce costs by 50%+ | Real-world analysis |
| **Scalability** | Design for 10x growth | Load testing |
| **Production Readiness** | 99.9%+ availability | SLA monitoring |

---

## 🏆 Congratulations!

You've completed the **16-Week Data Engineering Bible**—a comprehensive journey from MapReduce fundamentals to Principal Engineer-level system design.

### What You've Mastered

**Weeks 1-4: Foundation**
- MapReduce & distributed batch processing
- ETL basics & dimensional modeling
- SQL optimization & query planning
- Apache Spark internals & performance tuning

**Weeks 5-7: Intermediate**
- Kafka & distributed messaging
- Data warehousing & columnar storage
- Snowflake, BigQuery, Redshift architecture

**Weeks 8-11: Advanced Streaming**
- Apache Flink (exactly-once, checkpointing, CEP)
- Apache Beam (unified batch/stream model)

**Weeks 12-14: Lakehouse & Orchestration**
- Delta Lake, Iceberg, Hudi (ACID on data lakes)
- Airflow, Dagster, Prefect (workflow orchestration)

**Weeks 15-16: Production & Capstone**
- Lambda/Kappa/Data Mesh architectures
- CAP theorem & trade-off analysis
- FAANG-level system design
- $20M data platform for Uber

---

## 🚀 Next Steps

### Continue Learning
1. **Read Research Papers:** [Papers We Love - Distributed Systems](https://github.com/papers-we-love/papers-we-love/tree/master/distributed_systems)
2. **Contribute to Open Source:** Flink, Spark, Kafka, Iceberg
3. **Build Side Projects:** Real-time analytics, recommendation engine
4. **Write Blog Posts:** Share your learnings, build online presence

### Career Advancement
1. **Apply to FAANG:** L6+ Data Engineer, Staff/Principal roles
2. **Practice Interviews:** [Pramp](https://www.pramp.com/), [interviewing.io](https://interviewing.io/)
3. **Network:** Attend conferences (Spark Summit, Kafka Summit, DataEngConf)
4. **Mentor Others:** Teach what you learned, solidify knowledge

---

## 📚 Additional Resources

### Books
- **"Designing Data-Intensive Applications"** by Martin Kleppmann (must-read!)
- **"Streaming Systems"** by Tyler Akidau, Slava Chernyak, Reuven Lax
- **"The Data Warehouse Toolkit"** by Ralph Kimball
- **"Site Reliability Engineering"** by Google

### Online Courses
- **Stanford CS246:** Mining Massive Datasets
- **MIT 6.824:** Distributed Systems
- **UC Berkeley CS294:** AI Systems

### Communities
- **Slack:** [Data Engineering](https://datatalks.club/slack.html)
- **Reddit:** [r/dataengineering](https://www.reddit.com/r/dataengineering/)
- **Conferences:** Spark Summit, Kafka Summit, Flink Forward

---

## ✨ Final Words

Data Engineering is a rapidly evolving field. Technologies change, but **principles remain constant:**

1. **Understand Trade-Offs:** Every design decision has pros and cons
2. **Optimize for Scale:** Systems that work at 1K rows often break at 1B rows
3. **Monitor Everything:** You can't fix what you can't measure
4. **Keep Learning:** New technologies emerge every year
5. **Build in Public:** Share your knowledge, teach others

**You are now equipped to build data systems that power the world's largest companies.**

Good luck! 🚀

---

**Author:** Data Engineering Bible  
**Version:** 1.0  
**Last Updated:** October 15, 2025  
**License:** MIT  

**Feedback?** Open an issue on GitHub or reach out on Slack.
