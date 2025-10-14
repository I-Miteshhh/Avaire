# Week 8-9: Apache Flink — EXPERT Track

*"Flink's Chandy-Lamport implementation with barrier alignment achieves exactly-once semantics without sacrificing throughput. Understanding savepoints, RocksDB internals, and CEP is what separates good engineers from architects."* — Data Platform Architect, Uber

---

## 🎯 Learning Outcomes

By the end of this track, you will:
- Master Chandy-Lamport distributed snapshot algorithm
- Understand exactly-once semantics end-to-end (source, processing, sink)
- Optimize RocksDB state backend for production workloads
- Implement Complex Event Processing (CEP) patterns
- Handle backpressure and resource management
- Design multi-tenant Flink deployments
- Troubleshoot production incidents (checkpoint failures, OOM, backpressure)

---

## 🔬 1. Chandy-Lamport Distributed Snapshots

### The Problem: Consistent Global State

```
Challenge: Snapshot state of distributed system without stopping execution

Example: Bank transfers
┌────────────────────────────────────────────────────────────┐
│ Account A: $1000                Account B: $500            │
│                                                            │
│ Transfer $200 from A to B:                                 │
│ ├─ T1: A = $1000 - $200 = $800                            │
│ └─ T2: B = $500 + $200 = $700                             │
│                                                            │
│ Snapshot taken BETWEEN T1 and T2:                         │
│ ├─ A = $800 (after debit)                                │
│ ├─ B = $500 (before credit)                              │
│ └─ Total = $1300 ❌ INCONSISTENT! ($200 lost in flight)  │
└────────────────────────────────────────────────────────────┘

Chandy-Lamport Solution:
- Snapshot local state
- Snapshot in-flight messages (data in network buffers)
- Reconstruct consistent global state
```

---

### Chandy-Lamport Algorithm (Original)

```
Distributed System with 3 processes:

Process P1 ──────────────────────────────> Process P2
                    │
                    │ messages
                    ▼
              Process P3

Algorithm:
1. Initiator (P1) snapshots its local state
2. P1 sends MARKER message on all outgoing channels
3. P1 starts recording incoming messages

When process receives MARKER:
├─ If first MARKER on any channel:
│  ├─ Snapshot local state
│  ├─ Send MARKER on all outgoing channels
│  └─ Start recording messages on OTHER channels
└─ If already snapshotted:
   └─ Stop recording on this channel

Termination: All processes snapshotted + all channel states recorded
```

**Example Execution:**

```
Time T0: P1 initiates snapshot
├─ P1: state = {x=10}, sends MARKER to P2, P3

Time T1: P2 receives MARKER from P1
├─ P2: snapshot state = {y=20}
├─ P2: sends MARKER to P1, P3
├─ P2: records channel P3→P2

Time T2: P3 receives MARKER from P1
├─ P3: snapshot state = {z=30}
├─ P3: sends MARKER to P1, P2
├─ P3: stops recording P1→P3 (already received MARKER)

Time T3: All markers received
├─ Global snapshot: P1={x=10}, P2={y=20}, P3={z=30}
├─ Channel states: P1→P2=[msg1], P3→P2=[msg2], ...
```

---

### Flink's Barrier-Based Implementation

```
Flink Adaptation:
- MARKER → CHECKPOINT BARRIER
- Channels → Flink data streams
- Process state → Operator state

Checkpoint Barrier Flow:

Source 1:  [e1] [e2] ──BARRIER(ckpt-5)── [e3] [e4] [e5]
Source 2:  [e6] [e7] ──BARRIER(ckpt-5)── [e8] [e9] [e10]
                    │
                    ▼
            ┌──────────────────┐
            │  Stateful Op 1   │  (2 input channels)
            │ (keyBy + window) │
            └──────────────────┘
                    │
            Barrier Alignment:
            ├─ Receive barrier from Source 1 at time T1
            ├─ Block Source 1, buffer events [e3, e4, e5]
            ├─ Continue processing Source 2
            ├─ Receive barrier from Source 2 at time T2
            └─ Both barriers aligned! Snapshot state.
                    │
                    ▼
            State Snapshot:
            ├─ Keyed state: {user_id=123 → count=5, ...}
            ├─ Window buffers: [e1, e2, e6, e7]
            ├─ In-flight events: [e3, e4, e5] (buffered)
            └─ Acknowledge to JobManager
```

---

### Barrier Alignment vs Unaligned Checkpoints

```java
// ALIGNED (Default): Wait for all barriers
config.enableUnalignedCheckpoints(false);

Aligned Checkpoint Timeline:
T=0:    Barrier arrives at input 1
T=0-50: Buffer events from input 1, process input 2
T=50:   Barrier arrives at input 2
T=50:   SNAPSHOT state (includes buffered events)
T=51:   Continue processing

Cost: 50ms latency increase (barrier alignment)
Benefit: Smaller checkpoint size

// UNALIGNED: Don't wait, snapshot buffers
config.enableUnalignedCheckpoints(true);

Unaligned Checkpoint Timeline:
T=0:    Barrier arrives at input 1
T=0:    SNAPSHOT state + in-flight buffers IMMEDIATELY
T=1:    Continue processing (no blocking)
T=50:   Barrier arrives at input 2 (ignored)

Cost: Larger checkpoint (includes in-flight data)
Benefit: No latency increase, handles backpressure better
```

**Unaligned Checkpoint Deep Dive:**

```
Unaligned checkpoint includes:

1. Operator State:
   ├─ Keyed state: HashMap<Key, Value>
   └─ Operator state: ListState, BroadcastState

2. In-Flight Buffers (NEW):
   ├─ Input buffers: Events received but not processed
   ├─ Output buffers: Events processed but not sent
   └─ Network buffers: Events in network stack

Example:
Input buffer:  [e3, e4, e5] (waiting to be processed)
Output buffer: [e10, e11] (waiting to be sent)

Checkpoint includes ALL:
├─ State: {user_id=123 → count=5}
├─ Input buffer: [e3, e4, e5]
└─ Output buffer: [e10, e11]

On recovery:
├─ Restore state
├─ Replay input buffer events
└─ Resend output buffer events
```

**When to use unaligned:**

```
Use aligned checkpoints when:
├─ Low backpressure (barriers aligned quickly)
├─ Small in-flight data
└─ Checkpoint storage is expensive

Use unaligned checkpoints when:
├─ High backpressure (barrier alignment takes >1 second)
├─ Large in-flight data is acceptable
└─ Checkpoint latency is critical
```

---

## 🎯 2. Exactly-Once Semantics End-to-End

### Three Components

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Source    │ ───> │ Processing  │ ───> │    Sink     │
│ (Kafka)     │      │  (Flink)    │      │  (Kafka)    │
└─────────────┘      └─────────────┘      └─────────────┘
      │                     │                     │
      ▼                     ▼                     ▼
Exactly-once         Exactly-once         Exactly-once
source reads         processing           sink writes

Requirements:
1. Replayable source (Kafka offsets)
2. Checkpointed processing (Flink barriers)
3. Transactional sink (2PC commit)
```

---

### Source: Kafka Offset Management

```java
FlinkKafkaConsumer<String> consumer = new FlinkKafkaConsumer<>(
    "events",
    new SimpleStringSchema(),
    properties
);

// Enable offset checkpointing
consumer.setCommitOffsetsOnCheckpoints(true);

// Checkpoint includes Kafka offsets:
Checkpoint State:
├─ Operator state: {...}
├─ Kafka offsets: {
│    partition-0: offset=12345,
│    partition-1: offset=67890,
│    partition-2: offset=11111
│  }
```

**Recovery Process:**

```
Job fails at T=100:
├─ Last successful checkpoint: T=80 (ckpt-5)
├─ Kafka offsets at ckpt-5:
│  ├─ partition-0: offset=10000
│  ├─ partition-1: offset=50000
│  └─ partition-2: offset=9000

Recovery:
1. Restore operator state from ckpt-5
2. Seek Kafka consumers to checkpointed offsets:
   ├─ consumer-0.seek(partition-0, 10000)
   ├─ consumer-1.seek(partition-1, 50000)
   └─ consumer-2.seek(partition-2, 9000)
3. Resume processing from offset 10000, 50000, 9000

Result: Events from T=80 to T=100 are REPLAYED (exactly-once)
```

---

### Sink: Two-Phase Commit (2PC)

```
Transactional Sink (Kafka, JDBC, etc.):

Phase 1: Pre-commit (during checkpoint)
┌──────────────────────────────────────────────────────┐
│ Checkpoint barrier arrives at sink                   │
│ ├─ Flush buffered records to transaction            │
│ ├─ Kafka: kafkaProducer.flush()                     │
│ ├─ Do NOT commit yet!                               │
│ └─ Acknowledge checkpoint to JobManager             │
└──────────────────────────────────────────────────────┘

Phase 2: Commit (after checkpoint completes)
┌──────────────────────────────────────────────────────┐
│ JobManager confirms checkpoint success               │
│ ├─ Notify all sinks: "Checkpoint X completed"       │
│ ├─ Sinks commit transactions:                       │
│ │  ├─ Kafka: kafkaProducer.commitTransaction()     │
│ │  └─ JDBC: connection.commit()                    │
│ └─ Records become visible to consumers              │
└──────────────────────────────────────────────────────┘

Failure Handling:
- If checkpoint fails → Abort transactions
- If sink fails after pre-commit → Restore from checkpoint, retry
```

**Kafka Transactional Producer:**

```java
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaProducer;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaProducer.Semantic;

Properties props = new Properties();
props.setProperty("bootstrap.servers", "localhost:9092");
props.setProperty("transaction.timeout.ms", "900000");  // 15 min

FlinkKafkaProducer<String> producer = new FlinkKafkaProducer<>(
    "output-topic",
    new SimpleStringSchema(),
    props,
    Semantic.EXACTLY_ONCE  // Enable transactions
);

stream.addSink(producer);
```

**2PC Protocol Deep Dive:**

```
Timeline:

T=0:  Checkpoint 5 starts
      ├─ Sink receives barrier
      ├─ kafkaProducer.beginTransaction("txn-5")
      ├─ Buffered records: [r1, r2, r3]
      ├─ kafkaProducer.send(r1, r2, r3)  (to transaction)
      └─ kafkaProducer.flush()  (ensure sent)

T=10: Sink acknowledges checkpoint 5
      ├─ Transaction "txn-5" in PREPARED state
      └─ Wait for JobManager confirmation

T=20: JobManager confirms checkpoint 5 success
      ├─ Notify sink: "Commit txn-5"
      └─ kafkaProducer.commitTransaction("txn-5")

T=21: Records [r1, r2, r3] become visible to consumers

Failure Scenario:
T=15: Job fails BEFORE commit
      ├─ Transaction "txn-5" in PREPARED state
      ├─ Kafka times out transaction (transaction.timeout.ms)
      └─ Transaction ABORTED, records NOT visible

Recovery:
├─ Restore from checkpoint 4
├─ Replay records [r1, r2, r3]
└─ New transaction "txn-6" commits successfully
```

---

## 🗄️ 3. RocksDB State Backend Internals

### LSM-Tree Architecture

```
RocksDB = Log-Structured Merge-Tree

Write Path:
┌─────────────────────────────────────────────────────────┐
│ 1. Write to WAL (Write-Ahead Log)                       │
│    └─ Durability: Crash recovery                        │
│ 2. Insert into MemTable (in-memory sorted map)          │
│    └─ Fast writes: O(log N) insert                      │
│ 3. When MemTable full → Flush to SST file (Level 0)     │
│    └─ Immutable SSTable (sorted string table)           │
└─────────────────────────────────────────────────────────┘

Read Path:
┌─────────────────────────────────────────────────────────┐
│ 1. Check MemTable (newest data)                         │
│ 2. Check Block Cache (in-memory LRU cache)              │
│ 3. Check Bloom Filters (avoid disk reads)               │
│ 4. Read SST files (Level 0 → Level 1 → ... → Level 6)   │
│    └─ Binary search within SST file                     │
└─────────────────────────────────────────────────────────┘

Compaction:
┌─────────────────────────────────────────────────────────┐
│ Background process merges SST files:                    │
│ Level 0: [sst-1, sst-2, sst-3, sst-4]  (overlapping)   │
│    ↓ Compact                                            │
│ Level 1: [sst-5, sst-6]  (non-overlapping)              │
│    ↓ Compact                                            │
│ Level 2: [sst-7]                                        │
└─────────────────────────────────────────────────────────┘
```

---

### RocksDB Configuration for Flink

```java
import org.apache.flink.contrib.streaming.state.EmbeddedRocksDBStateBackend;
import org.apache.flink.contrib.streaming.state.RocksDBOptionsFactory;
import org.rocksdb.*;

public class CustomRocksDBConfig implements RocksDBOptionsFactory {
    
    @Override
    public DBOptions createDBOptions(DBOptions currentOptions, Collection<AutoCloseable> handlesToClose) {
        return currentOptions
            // Parallelism for background jobs (compaction, flush)
            .setMaxBackgroundJobs(4)
            
            // Limit open files (avoid "too many open files" error)
            .setMaxOpenFiles(1000)
            
            // WAL configuration
            .setMaxTotalWalSize(256 * 1024 * 1024)  // 256 MB
            
            // Statistics (for debugging)
            .setStatistics(new Statistics())
            .setStatsDumpPeriodSec(60);
    }
    
    @Override
    public ColumnFamilyOptions createColumnOptions(ColumnFamilyOptions currentOptions, Collection<AutoCloseable> handlesToClose) {
        return currentOptions
            // Write buffer size (MemTable size)
            .setWriteBufferSize(64 * 1024 * 1024)  // 64 MB
            
            // Number of write buffers (allows parallel flushes)
            .setMaxWriteBufferNumber(3)
            
            // Trigger compaction when 4 Level-0 files exist
            .setLevel0FileNumCompactionTrigger(4)
            
            // Block size for SST files (trade-off: read amplification vs memory)
            .setBlockSize(16 * 1024)  // 16 KB
            
            // Compression (zstd has best ratio, but slower)
            .setCompressionType(CompressionType.SNAPPY_COMPRESSION)
            .setBottommostCompressionType(CompressionType.ZSTD_COMPRESSION)
            
            // Bloom filter (reduces disk reads)
            .setTableFormatConfig(
                new BlockBasedTableConfig()
                    .setFilterPolicy(new BloomFilter(10, false))
                    .setBlockCache(new LRUCache(256 * 1024 * 1024))  // 256 MB
            )
            
            // Compaction style (LEVEL for read-heavy, UNIVERSAL for write-heavy)
            .setCompactionStyle(CompactionStyle.LEVEL);
    }
}

// Apply configuration:
EmbeddedRocksDBStateBackend rocksDB = new EmbeddedRocksDBStateBackend();
rocksDB.setRocksDBOptions(new CustomRocksDBConfig());
env.setStateBackend(rocksDB);
```

---

### Tuning for Different Workloads

```
Read-Heavy Workload (high get() calls):
├─ Increase block cache size: 512 MB - 2 GB
├─ Enable bloom filters: BloomFilter(10)
├─ Use LEVEL compaction
└─ Smaller write buffers: 32 MB

rocksDB.setRocksDBOptions(new RocksDBOptionsFactory() {
    @Override
    public ColumnFamilyOptions createColumnOptions(...) {
        return currentOptions
            .setWriteBufferSize(32 * 1024 * 1024)
            .setTableFormatConfig(
                new BlockBasedTableConfig()
                    .setBlockCache(new LRUCache(2L * 1024 * 1024 * 1024))  // 2 GB
                    .setFilterPolicy(new BloomFilter(10, false))
            );
    }
});

Write-Heavy Workload (high put() calls):
├─ Increase write buffer size: 128 MB
├─ More write buffers: 4-6
├─ Use UNIVERSAL compaction
└─ Reduce block cache: 128 MB

rocksDB.setRocksDBOptions(new RocksDBOptionsFactory() {
    @Override
    public ColumnFamilyOptions createColumnOptions(...) {
        return currentOptions
            .setWriteBufferSize(128 * 1024 * 1024)
            .setMaxWriteBufferNumber(6)
            .setCompactionStyle(CompactionStyle.UNIVERSAL)
            .setTableFormatConfig(
                new BlockBasedTableConfig()
                    .setBlockCache(new LRUCache(128 * 1024 * 1024))
            );
    }
});

Large State (>100 GB per operator):
├─ Enable incremental checkpoints
├─ Increase max_open_files: 5000
├─ Use tiered storage (SSD for hot, HDD for cold)
└─ Monitor compaction lag

rocksDB.enableIncrementalCheckpointing(true);
rocksDB.setRocksDBOptions(new RocksDBOptionsFactory() {
    @Override
    public DBOptions createDBOptions(...) {
        return currentOptions
            .setMaxOpenFiles(5000)
            .setMaxBackgroundJobs(8);
    }
});
```

---

### Incremental Checkpointing

```
Full Checkpoint (default):
├─ Checkpoint 1: Upload ALL SST files (10 GB)
├─ Checkpoint 2: Upload ALL SST files (12 GB)
└─ Checkpoint 3: Upload ALL SST files (15 GB)

Total uploaded: 37 GB
Checkpoint time: ~5 minutes per checkpoint

Incremental Checkpoint:
├─ Checkpoint 1: Upload ALL SST files (10 GB)
├─ Checkpoint 2: Upload ONLY new/modified SST files (2 GB)
└─ Checkpoint 3: Upload ONLY new/modified SST files (3 GB)

Total uploaded: 15 GB
Checkpoint time: ~30 seconds per checkpoint

Implementation:
rocksDB.enableIncrementalCheckpointing(true);

Checkpoint Metadata:
{
  "checkpointId": 5,
  "sharedState": [
    "s3://bucket/shared/sst-001",  // Reused from ckpt-4
    "s3://bucket/shared/sst-002",  // Reused from ckpt-4
  ],
  "privateState": [
    "s3://bucket/ckpt-5/sst-003",  // New in ckpt-5
    "s3://bucket/ckpt-5/sst-004"   // New in ckpt-5
  ]
}
```

---

## 🔍 4. Complex Event Processing (CEP)

### Pattern Matching

```java
import org.apache.flink.cep.CEP;
import org.apache.flink.cep.PatternStream;
import org.apache.flink.cep.pattern.Pattern;
import org.apache.flink.cep.pattern.conditions.SimpleCondition;

// Detect: "Login → Purchase within 5 minutes"
Pattern<Event, ?> pattern = Pattern
    .<Event>begin("login")
    .where(new SimpleCondition<Event>() {
        @Override
        public boolean filter(Event event) {
            return event.getType().equals("LOGIN");
        }
    })
    .next("purchase")
    .where(new SimpleCondition<Event>() {
        @Override
        public boolean filter(Event event) {
            return event.getType().equals("PURCHASE");
        }
    })
    .within(Time.minutes(5));  // Time constraint

PatternStream<Event> patternStream = CEP.pattern(
    stream.keyBy(Event::getUserId),
    pattern
);

patternStream.select((Map<String, List<Event>> pattern) -> {
    Event login = pattern.get("login").get(0);
    Event purchase = pattern.get("purchase").get(0);
    return new Alert(login.getUserId(), "Quick purchase detected");
});
```

---

### Fraud Detection Pattern

```java
// Detect: "Multiple small transactions followed by large withdrawal"

Pattern<Transaction, ?> fraudPattern = Pattern
    .<Transaction>begin("smallTransactions")
    .where(new SimpleCondition<Transaction>() {
        @Override
        public boolean filter(Transaction txn) {
            return txn.getAmount() < 100;
        }
    })
    .times(5)  // At least 5 small transactions
    .next("largeWithdrawal")
    .where(new SimpleCondition<Transaction>() {
        @Override
        public boolean filter(Transaction txn) {
            return txn.getAmount() > 5000 && txn.getType().equals("WITHDRAWAL");
        }
    })
    .within(Time.hours(1));

PatternStream<Transaction> fraudStream = CEP.pattern(
    transactions.keyBy(Transaction::getAccountId),
    fraudPattern
);

DataStream<Alert> alerts = fraudStream.select((Map<String, List<Transaction>> pattern) -> {
    List<Transaction> small = pattern.get("smallTransactions");
    Transaction large = pattern.get("largeWithdrawal").get(0);
    
    return new Alert(
        large.getAccountId(),
        String.format("Fraud: %d small txns + $%.2f withdrawal", small.size(), large.getAmount())
    );
});
```

---

### Temporal Patterns

```java
// Detect: "Temperature rising continuously for 10 readings"

Pattern<SensorReading, ?> pattern = Pattern
    .<SensorReading>begin("rising")
    .where(new IterativeCondition<SensorReading>() {
        @Override
        public boolean filter(SensorReading value, Context<SensorReading> ctx) throws Exception {
            // Check if current reading > previous reading
            if (!ctx.getEventsForPattern("rising").iterator().hasNext()) {
                return true;  // First event
            }
            
            SensorReading previous = null;
            for (SensorReading prev : ctx.getEventsForPattern("rising")) {
                previous = prev;
            }
            
            return value.getTemperature() > previous.getTemperature();
        }
    })
    .times(10)  // 10 consecutive rising readings
    .consecutive();  // Must be consecutive (no gaps)

PatternStream<SensorReading> risingTemp = CEP.pattern(
    sensorStream.keyBy(SensorReading::getSensorId),
    pattern
);
```

---

## 📊 5. Backpressure Handling

### Backpressure Detection

```
Web UI → Job Graph → Click on operator → Backpressure tab

Status:
├─ OK: Backpressure ratio < 10%
├─ LOW: 10% - 50%
├─ HIGH: 50% - 100%  ⚠️ BOTTLENECK!

Root Cause Analysis:
1. High backpressure on Map operator?
   └─> CPU-intensive processing → Increase parallelism

2. High backpressure on KeyBy operator?
   └─> Data skew (hot keys) → Repartition or salt keys

3. High backpressure on Sink?
   └─> Slow external system → Increase sink parallelism or batch writes
```

---

### Handling Data Skew

```
Problem:
Key distribution: 
├─ user_id=123: 1M events (HOT KEY)
├─ user_id=456: 100 events
└─ user_id=789: 50 events

Task allocation:
├─ Task 1: Processes user_id=123 (1M events) ← BOTTLENECK
├─ Task 2: Processes user_id=456 (100 events)
└─ Task 3: Processes user_id=789 (50 events)

Solution 1: Key Salting
stream
    .map(event -> {
        // Add random suffix to hot keys
        String saltedKey = event.getUserId() + "_" + (event.hashCode() % 10);
        return new Tuple2<>(saltedKey, event);
    })
    .keyBy(tuple -> tuple.f0)
    .window(...)
    .aggregate(...)
    .map(result -> {
        // Remove salt
        String originalKey = result.f0.split("_")[0];
        return new Tuple2<>(originalKey, result.f1);
    })
    .keyBy(tuple -> tuple.f0)
    .sum(1);  // Final aggregation

Solution 2: Two-Stage Aggregation
// Stage 1: Local pre-aggregation
stream
    .keyBy(event -> event.getUserId() + "_" + (event.hashCode() % 100))
    .window(TumblingEventTimeWindows.of(Time.minutes(1)))
    .sum("amount")
    // Stage 2: Global aggregation
    .keyBy(result -> result.getUserId())
    .sum("amount");
```

---

## 🚀 6. Production Case Studies

### Uber: Real-Time Pricing

```
Requirements:
├─ Process 100M ride events/day
├─ Update surge pricing every 30 seconds
├─ 99.9% availability
└─ <500ms latency

Architecture:
┌─────────────────────────────────────────────────────────────┐
│ Kafka (200 partitions)                                       │
│ ├─ ride_events: START, END, CANCEL                          │
│ └─ geo_hash: sf_downtown, sf_airport, ...                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Flink Job (parallelism=200)                                 │
│ ├─ KeyBy: geo_hash                                          │
│ ├─ Window: Sliding (5 min, slide 30 sec)                    │
│ ├─ Aggregate: COUNT(rides), AVG(wait_time)                  │
│ └─ ProcessFunction: Calculate surge multiplier              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Redis Cache (geo_hash → surge_multiplier)                   │
│ └─ TTL: 30 seconds                                          │
└─────────────────────────────────────────────────────────────┘

Configuration:
- TaskManagers: 25 (8 slots each)
- RocksDB state backend (incremental checkpoints)
- Checkpoint interval: 1 minute
- Unaligned checkpoints: Enabled
- State size: ~50 GB (30 days of windowed data)
```

---

### Netflix: Viewing Analytics

```
Requirements:
├─ Process 500M viewing events/day
├─ Generate recommendations in real-time
├─ Join with content metadata (enrichment)
└─ Output to S3 for offline analysis

Architecture:
┌─────────────────────────────────────────────────────────────┐
│ Kafka: viewing_events                                        │
│ ├─ user_id, content_id, timestamp, duration                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Flink Job 1: Enrichment (parallelism=128)                   │
│ ├─ BroadcastStream: Content metadata (10k items)            │
│ ├─ connect() viewing events with metadata                   │
│ └─ Output: Enriched events                                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Flink Job 2: Aggregation (parallelism=256)                  │
│ ├─ KeyBy: user_id                                           │
│ ├─ Window: Session (30 min gap)                             │
│ ├─ Aggregate: Total watch time, genres watched              │
│ └─ Output: User viewing sessions                            │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
        ┌──────────────┐        ┌──────────────┐
        │ Kafka: recs  │        │ S3 (Parquet) │
        └──────────────┘        └──────────────┘

State Management:
- Broadcast state: 100 MB (content metadata)
- Keyed state: 200 GB (user session buffers)
- Checkpoint interval: 5 minutes
- Incremental checkpoints: Enabled
- S3 checkpoint storage
```

---

## 🏆 Interview Questions (Expert Level)

1. **Explain Chandy-Lamport algorithm and how Flink implements it with barriers.**
2. **How does Flink achieve exactly-once semantics end-to-end? Explain two-phase commit.**
3. **Compare aligned vs unaligned checkpoints. When would you use each?**
4. **Describe RocksDB LSM-tree architecture. How would you tune it for a read-heavy workload?**
5. **How does incremental checkpointing work in RocksDB state backend?**
6. **Design a fraud detection system using Flink CEP. What patterns would you detect?**
7. **Your Flink job has high backpressure on a KeyBy operator. How would you diagnose and fix it?**
8. **How would you handle data skew in a windowed aggregation?**
9. **Explain the trade-offs between checkpoint interval, state size, and recovery time.**
10. **Design a multi-tenant Flink platform. How would you isolate tenants and allocate resources?**

---

## 🎓 Summary Checklist

- [ ] Understand Chandy-Lamport distributed snapshots
- [ ] Implement exactly-once semantics with transactional sinks
- [ ] Configure RocksDB for production workloads
- [ ] Design CEP patterns for complex event detection
- [ ] Diagnose and resolve backpressure issues
- [ ] Handle data skew with salting and two-stage aggregation
- [ ] Optimize checkpoint performance (aligned vs unaligned)
- [ ] Answer expert-level interview questions

**Next:** [WHITEPAPERS.md →](WHITEPAPERS.md)
