# Week 8-9: Apache Flink — Stream Processing Mastery

> **"Flink is the most advanced stream processing framework. Mastering event time, state management, and exactly-once semantics is essential for building production-grade real-time systems."**  
> — Principal Data Engineer, FAANG

---

## 📋 Module Overview

**Duration:** 2 weeks (80-100 hours)  
**Difficulty:** Advanced  
**Prerequisites:** Kafka, distributed systems basics, Java/Scala

This module provides comprehensive coverage of Apache Flink, from fundamental stream processing concepts to production-grade deployment strategies. You'll master event time processing, stateful computations, exactly-once semantics, and advanced optimization techniques.

---

## 🎯 Learning Objectives

By completing this module, you will be able to:

✅ **Foundational Skills:**
- Understand stream processing paradigms (bounded vs unbounded data)
- Differentiate event time from processing time
- Implement watermark strategies for out-of-order data
- Design windowed computations (tumbling, sliding, session)
- Use Flink DataStream API for transformations

✅ **Intermediate Skills:**
- Master Flink runtime architecture (JobManager, TaskManagers)
- Configure checkpointing and state backends
- Implement custom operators with ProcessFunctions
- Optimize parallelism and network buffers
- Monitor Flink jobs with metrics and Web UI

✅ **Expert Skills:**
- Implement Chandy-Lamport distributed snapshots
- Achieve exactly-once semantics end-to-end
- Tune RocksDB state backend for production workloads
- Design Complex Event Processing (CEP) patterns
- Diagnose and resolve backpressure issues
- Handle data skew in distributed aggregations

✅ **Production Readiness:**
- Deploy multi-tenant Flink clusters on Kubernetes
- Implement disaster recovery strategies
- Optimize checkpoint performance (aligned vs unaligned)
- Debug production incidents (OOM, checkpoint failures)
- Design cost-effective streaming architectures

---

## 📚 File Structure

```
3B_Apache_Flink/
├── BEGINNER.md         Stream processing basics, event time vs processing time,
│                       watermarks, windowing, DataStream API fundamentals
│
├── INTERMEDIATE.md     Flink runtime architecture, checkpointing internals,
│                       state backends (HashMap vs RocksDB), custom operators,
│                       performance tuning
│
├── EXPERT.md           Chandy-Lamport algorithm, exactly-once semantics,
│                       RocksDB optimization, CEP, backpressure handling,
│                       production case studies (Uber, Netflix)
│
├── WHITEPAPERS.md      Apache Flink paper (2015), Chandy-Lamport distributed
│                       snapshots, Dataflow Model (Google, 2015),
│                       barrier snapshotting deep dive
│
└── README.md           This file: Module overview, learning path,
                        hands-on project, assessment checklist
```

---

## 🗺️ Learning Path (2-Week Schedule)

### **Week 1: Foundations + Intermediate Concepts**

#### **Day 1-2: Stream Processing Fundamentals**
- [ ] Read: BEGINNER.md (Sections 1-3)
- [ ] Concepts: Bounded vs unbounded data, event time vs processing time
- [ ] Hands-on: Deploy Flink local cluster, run WordCount example
- [ ] Lab: Implement simple Kafka → Flink → Kafka pipeline

#### **Day 3-4: Watermarks and Windowing**
- [ ] Read: BEGINNER.md (Sections 4-5)
- [ ] Concepts: Watermark generation, tumbling/sliding/session windows
- [ ] Hands-on: Implement windowed aggregations with different watermark strategies
- [ ] Lab: Build real-time clickstream analytics with late data handling

#### **Day 5-6: State Management**
- [ ] Read: BEGINNER.md (Section 6), INTERMEDIATE.md (Section 1)
- [ ] Concepts: Keyed state, operator state, ValueState/ListState/MapState
- [ ] Hands-on: Implement stateful operators with ValueState
- [ ] Lab: Session timeout detection using timers

#### **Day 7: Flink Runtime Architecture**
- [ ] Read: INTERMEDIATE.md (Sections 1-2)
- [ ] Concepts: JobManager, TaskManagers, slots, parallelism
- [ ] Hands-on: Configure task slots, adjust parallelism, analyze execution graph
- [ ] Lab: Deploy Flink on Docker Compose with multiple TaskManagers

---

### **Week 2: Advanced Concepts + Production Skills**

#### **Day 8-9: Checkpointing Deep Dive**
- [ ] Read: INTERMEDIATE.md (Section 3), EXPERT.md (Sections 1-2)
- [ ] Concepts: Barrier alignment, state backends, incremental checkpoints
- [ ] Hands-on: Configure RocksDB state backend, enable incremental checkpoints
- [ ] Lab: Compare checkpoint performance (HashMap vs RocksDB)

#### **Day 10-11: Exactly-Once Semantics**
- [ ] Read: EXPERT.md (Section 2), WHITEPAPERS.md (Chandy-Lamport)
- [ ] Concepts: Two-phase commit, transactional sinks, Kafka offsets
- [ ] Hands-on: Implement end-to-end exactly-once with Kafka source and sink
- [ ] Lab: Simulate failures and verify no data loss or duplication

#### **Day 12: RocksDB Optimization**
- [ ] Read: EXPERT.md (Section 3)
- [ ] Concepts: LSM-tree, write buffers, compaction, bloom filters
- [ ] Hands-on: Tune RocksDB for read-heavy vs write-heavy workloads
- [ ] Lab: Monitor RocksDB metrics, optimize for large state (>100 GB)

#### **Day 13: Complex Event Processing**
- [ ] Read: EXPERT.md (Section 4)
- [ ] Concepts: Pattern matching, temporal patterns, CEP API
- [ ] Hands-on: Implement fraud detection patterns
- [ ] Lab: Build intrusion detection system with CEP

#### **Day 14: Production Troubleshooting**
- [ ] Read: EXPERT.md (Sections 5-6), WHITEPAPERS.md (Dataflow Model)
- [ ] Concepts: Backpressure, data skew, checkpoint failures
- [ ] Hands-on: Diagnose backpressure using Web UI, implement key salting
- [ ] Lab: Capstone project deployment with monitoring

---

## 🛠️ Hands-On Capstone Project

### **Real-Time Fraud Detection System**

**Scenario:**  
You are building a fraud detection system for a payment processing company. The system must:
- Process 10,000 transactions/second
- Detect suspicious patterns in real-time (<1 second latency)
- Provide exactly-once guarantees (no false alerts)
- Handle data skew (some merchants have 100x more transactions)
- Survive node failures with <1 minute recovery time

---

#### **Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                        Kafka Cluster                         │
│  Topics: transactions, user_profiles, merchant_metadata      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Flink Fraud Detection Job                  │
│                                                              │
│  ┌────────────┐     ┌──────────────┐     ┌──────────────┐  │
│  │  Source    │ ──> │  Enrichment  │ ──> │   Pattern    │  │
│  │  (Kafka)   │     │  (Broadcast) │     │   Detection  │  │
│  └────────────┘     └──────────────┘     │   (CEP)      │  │
│                                           └──────────────┘  │
│                            │                      │         │
│                            ▼                      ▼         │
│                     ┌──────────────┐     ┌──────────────┐  │
│                     │  Aggregation │     │  Alerts      │  │
│                     │  (Windowed)  │     │  (Kafka)     │  │
│                     └──────────────┘     └──────────────┘  │
│                            │                                │
│                            ▼                                │
│                     ┌──────────────┐                        │
│                     │ Risk Scores  │                        │
│                     │ (Kafka)      │                        │
│                     └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
┌─────────────────┐            ┌─────────────────┐
│  Alert Service  │            │  Analytics DB   │
│  (Notification) │            │  (PostgreSQL)   │
└─────────────────┘            └─────────────────┘
```

---

#### **Implementation Tasks**

**Phase 1: Data Ingestion (Day 1-2)**
```java
// Task 1.1: Kafka source with exactly-once semantics
FlinkKafkaConsumer<Transaction> transactionSource = new FlinkKafkaConsumer<>(
    "transactions",
    new TransactionDeserializationSchema(),
    kafkaProps
);
transactionSource.setCommitOffsetsOnCheckpoints(true);

DataStream<Transaction> transactions = env
    .addSource(transactionSource)
    .assignTimestampsAndWatermarks(
        WatermarkStrategy
            .<Transaction>forBoundedOutOfOrderness(Duration.ofSeconds(5))
            .withTimestampAssigner((txn, ts) -> txn.getTimestamp())
    );

// Task 1.2: Broadcast user profiles for enrichment
MapStateDescriptor<String, UserProfile> profileDescriptor = 
    new MapStateDescriptor<>("profiles", String.class, UserProfile.class);

BroadcastStream<UserProfile> profiles = env
    .addSource(new FlinkKafkaConsumer<>("user_profiles", ...))
    .broadcast(profileDescriptor);

// Task 1.3: Connect and enrich
DataStream<EnrichedTransaction> enriched = transactions
    .connect(profiles)
    .process(new EnrichmentFunction(profileDescriptor));
```

**Expected Output:**
```
Transaction: {user_id=123, merchant_id=456, amount=$50, timestamp=...}
Profile: {user_id=123, avg_transaction=$120, country=US}
Enriched: {user_id=123, merchant_id=456, amount=$50, avg_transaction=$120, country=US}
```

---

**Phase 2: Pattern Detection with CEP (Day 3-4)**
```java
// Task 2.1: Detect rapid succession of small transactions
Pattern<EnrichedTransaction, ?> rapidSmallTxns = Pattern
    .<EnrichedTransaction>begin("first")
    .where(new SimpleCondition<EnrichedTransaction>() {
        @Override
        public boolean filter(EnrichedTransaction txn) {
            return txn.getAmount() < 50;
        }
    })
    .times(5).consecutive()  // 5 consecutive small transactions
    .within(Time.minutes(10));

PatternStream<EnrichedTransaction> rapidPattern = CEP.pattern(
    enriched.keyBy(EnrichedTransaction::getUserId),
    rapidSmallTxns
);

DataStream<Alert> rapidAlerts = rapidPattern.select((Map<String, List<EnrichedTransaction>> pattern) -> {
    List<EnrichedTransaction> txns = pattern.get("first");
    return new Alert(
        txns.get(0).getUserId(),
        "RAPID_SMALL_TRANSACTIONS",
        "5 transactions < $50 in 10 minutes"
    );
});

// Task 2.2: Detect unusual location pattern
Pattern<EnrichedTransaction, ?> locationJump = Pattern
    .<EnrichedTransaction>begin("txn1")
    .next("txn2")
    .where(new IterativeCondition<EnrichedTransaction>() {
        @Override
        public boolean filter(EnrichedTransaction txn2, Context<EnrichedTransaction> ctx) {
            EnrichedTransaction txn1 = ctx.getEventsForPattern("txn1").iterator().next();
            // Different countries within 1 hour
            return !txn1.getCountry().equals(txn2.getCountry());
        }
    })
    .within(Time.hours(1));

// Task 2.3: Detect large withdrawal after account takeover signals
Pattern<EnrichedTransaction, ?> accountTakeover = Pattern
    .<EnrichedTransaction>begin("passwordChange")
    .where(txn -> txn.getType().equals("PASSWORD_CHANGE"))
    .next("largeWithdrawal")
    .where(txn -> txn.getAmount() > 5000 && txn.getType().equals("WITHDRAWAL"))
    .within(Time.minutes(30));
```

**Expected Output:**
```
Alert: {user_id=123, type=RAPID_SMALL_TRANSACTIONS, severity=MEDIUM}
Alert: {user_id=456, type=LOCATION_JUMP, severity=HIGH, details="US → Russia in 30 min"}
Alert: {user_id=789, type=ACCOUNT_TAKEOVER, severity=CRITICAL}
```

---

**Phase 3: Windowed Aggregations (Day 5-6)**
```java
// Task 3.1: Calculate risk score per user (sliding window)
DataStream<RiskScore> riskScores = enriched
    .keyBy(EnrichedTransaction::getUserId)
    .window(SlidingEventTimeWindows.of(Time.hours(1), Time.minutes(10)))
    .aggregate(new RiskAggregateFunction());

public class RiskAggregateFunction 
    implements AggregateFunction<EnrichedTransaction, RiskAccumulator, RiskScore> {
    
    @Override
    public RiskAccumulator createAccumulator() {
        return new RiskAccumulator();
    }
    
    @Override
    public RiskAccumulator add(EnrichedTransaction txn, RiskAccumulator acc) {
        acc.totalAmount += txn.getAmount();
        acc.transactionCount++;
        acc.uniqueMerchants.add(txn.getMerchantId());
        
        // Risk signals
        if (txn.getAmount() > acc.avgTransaction * 3) {
            acc.riskScore += 10;  // Unusually large transaction
        }
        if (acc.uniqueMerchants.size() > 20) {
            acc.riskScore += 5;  // Too many merchants
        }
        
        return acc;
    }
    
    @Override
    public RiskScore getResult(RiskAccumulator acc) {
        return new RiskScore(
            acc.userId,
            acc.riskScore,
            acc.transactionCount,
            acc.totalAmount
        );
    }
    
    @Override
    public RiskAccumulator merge(RiskAccumulator a, RiskAccumulator b) {
        // Merge logic for session windows
        a.totalAmount += b.totalAmount;
        a.transactionCount += b.transactionCount;
        a.uniqueMerchants.addAll(b.uniqueMerchants);
        a.riskScore += b.riskScore;
        return a;
    }
}

// Task 3.2: Handle late data
riskScores = enriched
    .keyBy(EnrichedTransaction::getUserId)
    .window(SlidingEventTimeWindows.of(Time.hours(1), Time.minutes(10)))
    .allowedLateness(Time.minutes(5))
    .sideOutputLateData(lateDataTag)
    .aggregate(new RiskAggregateFunction());

DataStream<EnrichedTransaction> lateData = riskScores.getSideOutput(lateDataTag);
lateData.addSink(new FlinkKafkaProducer<>("late-transactions", ...));
```

**Expected Output:**
```
RiskScore: {user_id=123, score=25, txn_count=15, total=$1,250}
RiskScore: {user_id=456, score=80, txn_count=50, total=$10,000}  ← HIGH RISK
```

---

**Phase 4: Data Skew Handling (Day 7-8)**
```java
// Task 4.1: Detect skewed keys
DataStream<Tuple2<String, Long>> txnCounts = enriched
    .map(txn -> new Tuple2<>(txn.getUserId(), 1L))
    .keyBy(0)
    .sum(1);

// Task 4.2: Implement key salting for hot users
DataStream<EnrichedTransaction> rebalanced = enriched
    .map(new KeySaltingMapper())  // Add salt: user_id_0, user_id_1, ...
    .keyBy(txn -> txn.getSaltedKey())
    .window(TumblingEventTimeWindows.of(Time.minutes(1)))
    .aggregate(new PreAggregateFunction())
    .map(new DesaltMapper())  // Remove salt
    .keyBy(txn -> txn.getUserId())
    .sum("amount");

public class KeySaltingMapper extends RichMapFunction<EnrichedTransaction, EnrichedTransaction> {
    
    private transient ValueState<Long> countState;
    
    @Override
    public void open(Configuration config) {
        ValueStateDescriptor<Long> descriptor = 
            new ValueStateDescriptor<>("count", Long.class, 0L);
        countState = getRuntimeContext().getState(descriptor);
    }
    
    @Override
    public EnrichedTransaction map(EnrichedTransaction txn) throws Exception {
        Long count = countState.value();
        
        // Apply salting to hot keys (>1000 txns/min)
        if (count > 1000) {
            int salt = (int) (System.currentTimeMillis() % 10);
            txn.setSaltedKey(txn.getUserId() + "_" + salt);
        } else {
            txn.setSaltedKey(txn.getUserId());
        }
        
        countState.update(count + 1);
        return txn;
    }
}
```

---

**Phase 5: Production Configuration (Day 9-10)**
```java
// Task 5.1: Configure checkpointing
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

env.enableCheckpointing(60000);  // 1 minute
CheckpointConfig config = env.getCheckpointConfig();

config.setCheckpointingMode(CheckpointingMode.EXACTLY_ONCE);
config.setMinPauseBetweenCheckpoints(30000);
config.setCheckpointTimeout(600000);  // 10 minutes
config.setMaxConcurrentCheckpoints(1);
config.enableExternalizedCheckpoints(
    ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION
);
config.enableUnalignedCheckpoints();  // For high backpressure

// Task 5.2: Configure RocksDB state backend
EmbeddedRocksDBStateBackend rocksDB = new EmbeddedRocksDBStateBackend();
rocksDB.enableIncrementalCheckpointing(true);
rocksDB.setRocksDBOptions(new CustomRocksDBConfig());

env.setStateBackend(rocksDB);
env.getCheckpointConfig().setCheckpointStorage("s3://fraud-detection/checkpoints");

// Task 5.3: Configure parallelism
env.setParallelism(64);  // Match Kafka partitions

// Task 5.4: Configure Kafka sink with exactly-once
Properties sinkProps = new Properties();
sinkProps.setProperty("bootstrap.servers", "kafka:9092");
sinkProps.setProperty("transaction.timeout.ms", "900000");

FlinkKafkaProducer<Alert> alertSink = new FlinkKafkaProducer<>(
    "fraud-alerts",
    new AlertSerializationSchema(),
    sinkProps,
    FlinkKafkaProducer.Semantic.EXACTLY_ONCE
);

alerts.addSink(alertSink);
```

**Task 5.5: Deploy on Kubernetes**
```yaml
# flink-deployment.yaml
apiVersion: flink.apache.org/v1beta1
kind: FlinkDeployment
metadata:
  name: fraud-detection
spec:
  image: fraud-detection:1.0.0
  flinkVersion: v1_18
  flinkConfiguration:
    taskmanager.numberOfTaskSlots: "8"
    state.backend: rocksdb
    state.checkpoints.dir: s3://fraud-detection/checkpoints
    state.savepoints.dir: s3://fraud-detection/savepoints
    execution.checkpointing.interval: 60s
    execution.checkpointing.mode: EXACTLY_ONCE
    jobmanager.memory.process.size: 2048m
    taskmanager.memory.process.size: 8192m
  jobManager:
    resource:
      memory: "2048m"
      cpu: 2
  taskManager:
    replicas: 8
    resource:
      memory: "8192m"
      cpu: 4
  job:
    jarURI: local:///opt/flink/usrlib/fraud-detection.jar
    parallelism: 64
    upgradeMode: savepoint
```

```bash
# Deploy
kubectl apply -f flink-deployment.yaml

# Monitor
kubectl port-forward svc/fraud-detection-rest 8081:8081
# Open http://localhost:8081

# Trigger savepoint
kubectl exec -it fraud-detection-jobmanager-0 -- \
  ./bin/flink savepoint <job-id> s3://fraud-detection/savepoints/manual-1
```

---

#### **Success Criteria**

✅ **Functional Requirements:**
- [ ] Process 10,000+ transactions/second
- [ ] Detect fraud patterns with <1 second latency
- [ ] Zero data loss or duplication (exactly-once)
- [ ] Handle 5 minutes of late data
- [ ] Capture very late data in side output

✅ **Performance Requirements:**
- [ ] Checkpoint completes in <30 seconds
- [ ] 99th percentile latency <500ms
- [ ] Handle 2x traffic spike without backpressure
- [ ] Recovery time <1 minute after node failure

✅ **Operational Requirements:**
- [ ] Kubernetes deployment with auto-scaling
- [ ] Prometheus metrics exported
- [ ] Grafana dashboards for monitoring
- [ ] Alerting on checkpoint failures
- [ ] Documented runbook for incidents

---

## 📊 Assessment Checklist

### **Beginner Level (Week 1)**
- [ ] Explain the difference between event time and processing time
- [ ] Implement watermark strategies (bounded out-of-orderness)
- [ ] Use tumbling, sliding, and session windows
- [ ] Write Flink DataStream programs with map, filter, keyBy
- [ ] Deploy Flink on local cluster and Docker Compose

### **Intermediate Level (Week 1-2)**
- [ ] Understand JobManager and TaskManager architecture
- [ ] Configure checkpointing with different intervals
- [ ] Use HashMapStateBackend and RocksDBStateBackend
- [ ] Implement custom ProcessFunctions with timers
- [ ] Optimize parallelism and network buffers
- [ ] Monitor Flink jobs with Web UI and metrics

### **Expert Level (Week 2)**
- [ ] Explain Chandy-Lamport distributed snapshots
- [ ] Implement exactly-once semantics with transactional Kafka sink
- [ ] Tune RocksDB for read-heavy and write-heavy workloads
- [ ] Design CEP patterns for fraud detection
- [ ] Diagnose backpressure and data skew
- [ ] Configure unaligned checkpoints for high-backpressure scenarios
- [ ] Deploy multi-tenant Flink on Kubernetes with resource isolation

### **Production Readiness**
- [ ] Complete capstone project (fraud detection system)
- [ ] Implement disaster recovery with savepoints
- [ ] Set up monitoring with Prometheus/Grafana
- [ ] Document architecture and runbooks
- [ ] Conduct chaos engineering tests (kill nodes, inject delays)
- [ ] Optimize costs (checkpoint frequency, state backends)

---

## 🏆 Interview Preparation

### **Common Interview Questions:**

1. **What is the difference between event time and processing time? Give a real-world example.**
2. **How do watermarks work in Flink? What happens to late data?**
3. **Explain Flink's checkpointing mechanism. How does it achieve exactly-once semantics?**
4. **What are the differences between HashMap and RocksDB state backends?**
5. **Your Flink job has high backpressure. How would you diagnose and fix it?**
6. **How would you handle data skew in a windowed aggregation?**
7. **Explain the trade-offs between aligned and unaligned checkpoints.**
8. **Design a real-time recommendation system using Flink. What are the key challenges?**
9. **How does Flink achieve fault tolerance? Compare with Spark Streaming.**
10. **What is the role of JobManager vs TaskManager?**

### **System Design Questions:**

1. **Design a real-time fraud detection system processing 100K events/sec.**
2. **Build a session analytics pipeline with Flink (like Google Analytics).**
3. **Implement a real-time leaderboard for a gaming platform.**
4. **Design a monitoring system for microservices using Flink.**
5. **Build a change data capture (CDC) pipeline with exactly-once guarantees.**

---

## 🔗 Additional Resources

### **Official Documentation:**
- Flink Documentation: https://flink.apache.org/docs/
- Flink GitHub: https://github.com/apache/flink
- Flink Forward Conference Talks: https://www.flink-forward.org/

### **Books:**
- *Stream Processing with Apache Flink* by Fabian Hueske, Vasiliki Kalavri
- *Designing Data-Intensive Applications* by Martin Kleppmann (Chapter 11)

### **Online Courses:**
- Flink Training (free): https://training.ververica.com/
- Confluent Kafka + Flink Integration

### **Blogs:**
- Ververica Blog: https://www.ververica.com/blog
- Uber Engineering: https://eng.uber.com/tag/flink/
- Netflix Tech Blog: https://netflixtechblog.com/

---

## ✅ Completion Criteria

You have mastered Apache Flink when you can:

1. **Build production-grade streaming applications** with exactly-once semantics
2. **Optimize Flink jobs** for latency and throughput
3. **Debug production incidents** (backpressure, OOM, checkpoint failures)
4. **Design complex event processing** patterns for real-world use cases
5. **Deploy and operate** Flink on Kubernetes with monitoring
6. **Answer expert-level interview questions** confidently
7. **Read and discuss** Flink research papers (ABS, Dataflow Model)

**Estimated Time to Completion:** 80-100 hours over 2 weeks

**Next Module:** [Week 10-11: Apache Beam & Unified Batch/Stream →](../../3-Advanced/3C_Apache_Beam/)

---

## 📝 Feedback and Contributions

Found an error or have a suggestion? Please contribute:
- Open an issue: [GitHub Issues](https://github.com/your-repo/issues)
- Submit a PR: [Contribute Guide](https://github.com/your-repo/CONTRIBUTING.md)

**Happy Streaming! 🚀**
