# Week 5: Apache Kafka & Distributed Messaging

**Status:** ✅ Complete  
**Duration:** 1 week (40-50 hours)  
**Prerequisites:** MapReduce, ETL Basics, SQL Deep Dive, Apache Spark  
**Target Audience:** L2+ Data Engineers (40+ LPA), Principal Architect aspirants

---

## 📚 Module Overview

Apache Kafka is the de facto standard for **distributed streaming platforms** at scale. Originally built at LinkedIn (2011) to handle 7 trillion messages/day, Kafka has evolved into a complete event streaming ecosystem powering real-time data pipelines at companies like Uber, Netflix, Airbnb, and every FAANG company.

This module provides **Principal Architect-level depth** across:
- Kafka internals (log segments, indexes, ISR protocol, controller election)
- Stream processing (Kafka Streams, state stores, exactly-once semantics)
- Multi-DC replication (MirrorMaker 2, conflict resolution, active-active)
- Performance tuning (zero-copy, page cache optimization, compression strategies)
- Security architecture (SSL/TLS, SASL, ACLs, OAuth integration)
- Modern advancements (KRaft, tiered storage, transactional semantics)

### Why This Matters

```
Real-World Kafka Deployments (2024):

LinkedIn:
- 7 trillion messages/day
- 20,000+ brokers
- 100,000+ topics
- 10+ petabytes/day

Uber:
- 4,000 brokers
- 1 trillion messages/day
- Powers: Surge pricing, driver matching, fraud detection

Netflix:
- 700+ billion events/day
- Powers: Recommendations, A/B testing, real-time analytics

Common Use Cases:
✓ Real-time analytics pipelines
✓ Event-driven microservices
✓ CDC (Change Data Capture) from databases
✓ Log aggregation at scale
✓ Stream processing (fraud detection, recommendations)
✓ Metrics & monitoring infrastructure
```

---

## 🎯 Learning Path

### File Structure

```
2A_Kafka_Fundamentals/
├── BEGINNER.md          (73 KB)  ← Kafka basics, producers, consumers
├── INTERMEDIATE.md      (38 KB)  ← Multi-broker clusters, Schema Registry, Connect
├── EXPERT.md           (90 KB)  ← Internals, transactions, multi-DC, performance
├── WHITEPAPERS.md      (105 KB) ← Research papers (2011 Kafka, KIP-98, KIP-500)
└── README.md           (This file)
```

### Recommended Study Sequence

#### Week 5 Day-by-Day Plan

| Day | Topic | Files | Hands-On Lab |
|-----|-------|-------|-------------|
| **Day 1-2** | Kafka Fundamentals | BEGINNER.md | Set up 3-broker cluster, produce/consume messages |
| **Day 3-4** | Distributed Kafka | INTERMEDIATE.md | Implement Schema Registry, Kafka Connect pipeline |
| **Day 5-6** | Advanced Internals | EXPERT.md | Transactional streams app, multi-DC setup |
| **Day 7** | Research Deep Dive | WHITEPAPERS.md | Read original Kafka paper, analyze KIP-98 |

---

## 📖 File Descriptions

### 1. BEGINNER.md (73,844 bytes)

**Target Audience:** Engineers new to Kafka or coming from traditional messaging systems (RabbitMQ, ActiveMQ)

**Key Topics:**
- Kafka architecture (brokers, topics, partitions, offsets)
- Producer API (sync/async sends, partitioning strategies, compression)
- Consumer API (consumer groups, rebalancing, offset management)
- Serialization (Avro, Protobuf, JSON Schema)
- Basic cluster setup (single-node → 3-node cluster)
- Common patterns (fan-out, work queue, competing consumers)

**Practical Labs:**
1. Set up Kafka on local machine (Docker Compose)
2. Implement producer with custom partitioner
3. Build consumer group with auto-commit
4. Test fault tolerance (kill broker, observe rebalancing)

**Time Estimate:** 15-20 hours

---

### 2. INTERMEDIATE.md (37,935 bytes)

**Target Audience:** Engineers with 1-2 years Kafka experience, ready to operate production clusters

**Key Topics:**
- Multi-broker cluster architecture (ZooKeeper coordination, controller election)
- Replication protocol (ISR, high-water mark, leader election)
- Schema Registry (schema evolution, compatibility types)
- Kafka Connect (source/sink connectors, distributed mode, transforms)
- Monitoring (JMX metrics, Prometheus exporters, Grafana dashboards)
- Multi-DC replication (MirrorMaker 2, offset translation, provenance headers)
- Security basics (SSL/TLS, SASL mechanisms, ACLs)

**Practical Labs:**
1. Deploy 3-broker cluster with ZooKeeper ensemble
2. Set up Schema Registry with Avro schemas
3. Build Kafka Connect pipeline (Postgres → Kafka → Elasticsearch)
4. Monitor cluster with JMX + Prometheus + Grafana
5. Configure SSL/TLS encryption and SASL authentication

**Time Estimate:** 15-20 hours

---

### 3. EXPERT.md (90,000+ bytes)

**Target Audience:** Staff+ engineers, Principal Architects, FAANG interview candidates

**Key Topics:**
- Storage internals (log segment format, index files, time-based indexes, log cleaner)
- Transactional semantics (idempotent producers, exactly-once delivery, transaction coordinator)
- Kafka Streams internals (state stores, RocksDB tuning, interactive queries, punctuators)
- Multi-DC active-active (conflict resolution, CRDTs, timestamp-based merging)
- Performance engineering (zero-copy sendfile(), page cache tuning, compression benchmarks)
- Cruise Control (automated balancing, partition reassignment, broker decommissioning)
- KRaft mode (Raft consensus, metadata log, removing ZooKeeper)
- Tiered storage (S3/GCS offloading, infinite retention, cost optimization)
- Interview questions (system design, debugging scenarios, trade-off analysis)

**Practical Labs:**
1. Analyze log segment files (hexdump, index structures)
2. Implement transactional producer + read_committed consumer
3. Build Kafka Streams app with state stores and exactly-once processing
4. Set up multi-DC replication with conflict resolution
5. Tune cluster for 1M msg/sec throughput
6. Migrate cluster from ZooKeeper to KRaft mode

**Time Estimate:** 20-25 hours

---

### 4. WHITEPAPERS.md (105,000+ bytes)

**Target Audience:** Researchers, architects designing distributed systems, deep-dive enthusiasts

**Key Papers:**
1. **Kafka: A Distributed Messaging System for Log Processing** (2011)
   - Original Kafka paper from LinkedIn
   - Motivation (LinkedIn's 10B events/day in 2010)
   - Design principles (throughput > features, pull-based consumption, persistent log)
   - Performance benchmarks (50K msg/sec on 2011 hardware)

2. **The Log: What every software engineer should know** (Jay Kreps, 2013)
   - Log as universal abstraction (databases, consensus, streams)
   - State as derivative of log (event sourcing)
   - Ordering guarantees in distributed systems

3. **Exactly-Once Semantics** (KIP-98, KIP-129, 2017)
   - Idempotent producers (producer IDs, sequence numbers, epoch fencing)
   - Transactional API (transaction coordinator, 2-phase commit, control records)
   - Performance impact (6% overhead for idempotence, 37% for transactions)

4. **KRaft: Removing ZooKeeper Dependency** (KIP-500, 2020-2022)
   - Raft consensus in Kafka (leader election, log replication)
   - Metadata log architecture (__cluster_metadata topic)
   - Performance improvements (93% faster startup, 92% faster leader election)

5. **Tiered Storage** (KIP-405, 2020-2024)
   - Hot/cold data separation (SSD for recent, S3 for historical)
   - 72% cost savings (Uber case study: $10M → $2M/year)
   - Remote fetch protocol (100ms latency for cold data)

**Time Estimate:** 8-12 hours (deep reading + note-taking)

---

## 🛠️ Hands-On Project: Real-Time E-Commerce Analytics Pipeline

### Objective
Build a production-grade real-time analytics system for an e-commerce platform using Kafka ecosystem.

### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│ Data Sources                                                 │
│ ├─ Website clicks (Kafka Producer in Node.js)                │
│ ├─ Order DB (Postgres CDC via Debezium)                     │
│ └─ Inventory updates (REST API → Kafka via Connect)         │
└─────────────┬────────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────────┐
│ Kafka Cluster (3 brokers, KRaft mode)                        │
│ Topics:                                                      │
│ ├─ user-clicks (100 partitions, 7-day retention)            │
│ ├─ orders (50 partitions, 90-day retention, tiered)         │
│ └─ inventory (20 partitions, compacted)                     │
└─────────────┬────────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────────┐
│ Stream Processing (Kafka Streams)                            │
│ ├─ Click aggregation (sessionization, 30-min windows)       │
│ ├─ Revenue calculation (join orders + clicks)                │
│ └─ Inventory alerting (low-stock detection)                 │
└─────────────┬────────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────────┐
│ Sinks                                                        │
│ ├─ Elasticsearch (search & analytics)                        │
│ ├─ PostgreSQL (OLTP queries)                                │
│ └─ S3 (data lake for ML)                                    │
└──────────────────────────────────────────────────────────────┘
```

### Implementation Steps

#### Phase 1: Infrastructure Setup (Day 1-2)

```bash
# docker-compose.yml
version: '3.8'
services:
  kafka-1:
    image: apache/kafka:3.7.0
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka-1:9093,2@kafka-2:9093,3@kafka-3:9093
      KAFKA_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-1:9092
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
    volumes:
      - kafka1-data:/var/lib/kafka/data

  kafka-2:
    image: apache/kafka:3.7.0
    environment:
      KAFKA_NODE_ID: 2
      KAFKA_PROCESS_ROLES: broker,controller
      # ... similar config

  kafka-3:
    image: apache/kafka:3.7.0
    environment:
      KAFKA_NODE_ID: 3
      KAFKA_PROCESS_ROLES: broker,controller
      # ... similar config

  schema-registry:
    image: confluentinc/cp-schema-registry:7.6.0
    environment:
      SCHEMA_REGISTRY_HOST_NAME: schema-registry
      SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: kafka-1:9092

  kafka-connect:
    image: confluentinc/cp-kafka-connect:7.6.0
    environment:
      CONNECT_BOOTSTRAP_SERVERS: kafka-1:9092,kafka-2:9092,kafka-3:9092
      CONNECT_GROUP_ID: connect-cluster
      CONNECT_CONFIG_STORAGE_TOPIC: connect-configs
      CONNECT_OFFSET_STORAGE_TOPIC: connect-offsets
      CONNECT_STATUS_STORAGE_TOPIC: connect-status

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"

volumes:
  kafka1-data:
  kafka2-data:
  kafka3-data:
```

#### Phase 2: Schema Design (Day 3)

```avro
// user-click.avsc
{
  "type": "record",
  "name": "ClickEvent",
  "namespace": "com.ecommerce.events",
  "fields": [
    {"name": "userId", "type": "string"},
    {"name": "sessionId", "type": "string"},
    {"name": "timestamp", "type": "long", "logicalType": "timestamp-millis"},
    {"name": "pageUrl", "type": "string"},
    {"name": "productId", "type": ["null", "string"], "default": null},
    {"name": "action", "type": {"type": "enum", "name": "ClickAction", 
                                  "symbols": ["VIEW", "ADD_TO_CART", "PURCHASE"]}},
    {"name": "metadata", "type": {"type": "map", "values": "string"}}
  ]
}
```

#### Phase 3: Kafka Streams Application (Day 4-5)

```java
StreamsBuilder builder = new StreamsBuilder();

// Click stream
KStream<String, ClickEvent> clicks = builder.stream("user-clicks",
    Consumed.with(Serdes.String(), clickEventSerde));

// Sessionization (30-minute windows)
KTable<Windowed<String>, Long> clicksPerSession = clicks
    .groupByKey()
    .windowedBy(SessionWindows.ofInactivityGapWithNoGrace(Duration.ofMinutes(30)))
    .count(Materialized.as("clicks-per-session-store"));

// Order stream
KStream<String, Order> orders = builder.stream("orders",
    Consumed.with(Serdes.String(), orderSerde));

// Revenue calculation (join clicks + orders)
KStream<String, RevenueEvent> revenue = clicks
    .selectKey((k, v) -> v.getSessionId())
    .join(orders,
        (click, order) -> new RevenueEvent(click, order),
        JoinWindows.ofTimeDifferenceWithNoGrace(Duration.ofHours(1)),
        StreamJoined.with(Serdes.String(), clickEventSerde, orderSerde)
    );

revenue.to("revenue-events");

// Exactly-once processing
Properties props = new Properties();
props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, "exactly_once_v2");
props.put(StreamsConfig.APPLICATION_ID_CONFIG, "ecommerce-analytics");

KafkaStreams streams = new KafkaStreams(builder.build(), props);
streams.start();
```

#### Phase 4: Monitoring & Alerting (Day 6)

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'kafka'
    static_configs:
      - targets: ['kafka-1:9092', 'kafka-2:9092', 'kafka-3:9092']
    metrics_path: '/metrics'

  - job_name: 'kafka-streams'
    static_configs:
      - targets: ['streams-app:8080']

# Alert rules
groups:
  - name: kafka_alerts
    rules:
      - alert: HighConsumerLag
        expr: kafka_consumer_lag > 10000
        for: 5m
        annotations:
          summary: "Consumer lag exceeds 10K messages"
```

---

## 📊 Assessment Checklist

After completing this module, you should be able to:

### Beginner Level ✅
- [ ] Explain Kafka architecture (brokers, topics, partitions, offsets)
- [ ] Write producer code with custom partitioner
- [ ] Implement consumer with manual offset management
- [ ] Set up 3-broker Kafka cluster
- [ ] Choose appropriate serialization format (Avro vs Protobuf)
- [ ] Debug common issues (rebalancing, lag, message loss)

### Intermediate Level ✅
- [ ] Configure ISR and replication factor for durability
- [ ] Implement Schema Registry with schema evolution
- [ ] Build Kafka Connect pipeline (database CDC)
- [ ] Set up monitoring (JMX → Prometheus → Grafana)
- [ ] Configure SSL/TLS and SASL authentication
- [ ] Design multi-DC replication with MirrorMaker 2

### Expert Level ✅
- [ ] Explain log segment file format and indexing
- [ ] Implement transactional producer with exactly-once semantics
- [ ] Tune Kafka Streams RocksDB state stores
- [ ] Design active-active multi-DC with conflict resolution
- [ ] Optimize cluster for 1M+ msg/sec throughput
- [ ] Migrate cluster from ZooKeeper to KRaft
- [ ] Implement tiered storage for cost optimization
- [ ] Answer FAANG-level system design questions

---

## 🎓 Interview Preparation

### Common Kafka Interview Questions

1. **Basic:**
   - "Explain the difference between Kafka and RabbitMQ."
   - "How does Kafka achieve high throughput?"
   - "What is a consumer group? How does rebalancing work?"

2. **Intermediate:**
   - "How does Kafka guarantee message ordering?"
   - "Explain ISR (In-Sync Replicas) and how leader election works."
   - "When would you use log compaction vs time-based retention?"

3. **Advanced:**
   - "Design a real-time fraud detection system using Kafka."
   - "How would you achieve exactly-once semantics end-to-end?"
   - "Explain trade-offs between ZooKeeper mode and KRaft mode."

4. **Principal Architect:**
   - "Design Kafka architecture for a global social network (1B users)."
   - "How would you migrate 5 PB of Kafka data to tiered storage with zero downtime?"
   - "Explain the CAP theorem trade-offs in Kafka's ISR protocol."

### Recommended Practice
- **LeetCode/AlgoExpert:** System design questions (URL shortener, Twitter feed)
- **Confluent Certified Developer:** Official Kafka certification
- **Real Projects:** Contribute to Kafka ecosystem (KRaft, Tiered Storage, Streams)

---

## 🔗 Additional Resources

### Official Documentation
- [Apache Kafka Docs](https://kafka.apache.org/documentation/)
- [Confluent Developer Portal](https://developer.confluent.io/)
- [Kafka Improvement Proposals (KIPs)](https://cwiki.apache.org/confluence/display/KAFKA/Kafka+Improvement+Proposals)

### Books
- **Kafka: The Definitive Guide** (2nd Edition) - Gwen Shapira et al.
- **Designing Data-Intensive Applications** (Chapter 11) - Martin Kleppmann
- **Streaming Systems** - Tyler Akidau (Google)

### Video Courses
- [Confluent Kafka Fundamentals](https://www.confluent.io/training/) (Free)
- [Udemy: Apache Kafka Series](https://www.udemy.com/course/apache-kafka/) (Stephane Maarek)

### Community
- [Kafka Users Mailing List](https://kafka.apache.org/contact)
- [Confluent Community Slack](https://confluentcommunity.slack.com/)
- [Stack Overflow - Kafka Tag](https://stackoverflow.com/questions/tagged/apache-kafka)

---

## ✅ Completion Criteria

You have mastered Week 5 when you can:

1. **Build:** Implement a production-grade Kafka Streams application with exactly-once semantics
2. **Operate:** Deploy and monitor a multi-broker Kafka cluster with KRaft
3. **Optimize:** Tune a cluster to handle 1M+ msg/sec with <10ms p99 latency
4. **Design:** Architect a global multi-DC Kafka deployment with active-active replication
5. **Explain:** Teach Kafka internals (log format, ISR protocol, transactions) to a junior engineer
6. **Interview:** Pass FAANG-level system design interviews involving Kafka

---

**Time Investment:** 40-50 hours  
**Difficulty:** ★★★★☆ (Advanced)  
**ROI:** ★★★★★ (Critical for modern data engineering)

**Next Steps:** 
- Continue to [Week 6: Data Warehousing](../3-Advanced/3A_Data_Warehousing/README.md)
- Or review [Week 4: Apache Spark](../1-Foundation/1D_Apache_Spark/README.md)

---

**Last Updated:** January 2025  
**Contributors:** Data Engineering Bible Project  
**License:** Educational Use Only

---

**End of README** | [Start with BEGINNER.md →](BEGINNER.md)
