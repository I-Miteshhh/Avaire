# Week 5: Kafka & Distributed Messaging — WHITEPAPERS

*"The best way to understand Kafka is to read the papers that inspired it. Every design decision has deep reasoning rooted in distributed systems theory."* — Principal Engineer Wisdom

---

## 📋 Table of Contents

1. [Kafka: A Distributed Messaging System for Log Processing (2011)](#kafka-paper-2011)
2. [The Log: What every software engineer should know about real-time data's unifying abstraction](#the-log-abstraction)
3. [Exactly-Once Semantics (KIP-98)](#exactly-once-kip-98)
4. [KRaft: Removing Apache ZooKeeper Dependency (KIP-500)](#kraft-kip-500)
5. [Tiered Storage (KIP-405)](#tiered-storage-kip-405)
6. [Additional Influential Papers](#additional-papers)

---

<a name="kafka-paper-2011"></a>
## 📄 Paper 1: Kafka: A Distributed Messaging System for Log Processing (2011)

**Authors:** Jay Kreps, Neha Narkhede, Jun Rao (LinkedIn)  
**Published:** NetDB 2011  
**Citations:** 4,500+  
**Impact:** Founded the modern streaming data platform paradigm

### 🎯 Abstract Summary

Kafka was designed at LinkedIn to handle their massive log data (activity tracking, operational metrics, system logs). Traditional messaging systems (ActiveMQ, RabbitMQ) and ETL tools couldn't handle:
- **High throughput** (100K+ messages/sec per server)
- **Horizontal scalability** (add brokers linearly)
- **Persistent storage** (replay historical data)
- **Low latency** (<10ms end-to-end)

Kafka achieves this through:
1. **Distributed commit log** (not a queue!)
2. **Push-pull hybrid** (producers push, consumers pull)
3. **Partitioning for parallelism** (multiple consumers per topic)
4. **Minimal feature set** (no message routing, no transactional API at v0.7)

---

### 🧠 1. Motivation & Background

#### The LinkedIn Data Problem (2010)

```
LinkedIn's data sources (2010):
┌─────────────────────────────────────────────────────────────┐
│ Activity Tracking (user clicks, page views, searches)       │
│ - Volume: 10 billion events/day                             │
│ - Use case: Recommendations, analytics                      │
├─────────────────────────────────────────────────────────────┤
│ Operational Metrics (app server logs, database queries)     │
│ - Volume: 1 billion events/day                              │
│ - Use case: Monitoring, alerting                            │
├─────────────────────────────────────────────────────────────┤
│ System Logs (application errors, exceptions)                │
│ - Volume: 500 million events/day                            │
│ - Use case: Debugging, auditing                             │
└─────────────────────────────────────────────────────────────┘

Total: 11.5 billion events/day (2010)
Today (2024): 7 trillion events/day (600x growth!)
```

#### Existing Solutions & Their Limitations

**Option 1: Traditional Message Queues (ActiveMQ, RabbitMQ)**

```
Problems:
1. Low throughput:
   - ActiveMQ: ~10K msg/sec per broker
   - Reason: Per-message acknowledgments, complex routing

2. No persistence:
   - Messages deleted after consumption
   - Cannot replay for reprocessing

3. Poor scalability:
   - Vertical scaling only (bigger servers)
   - Single broker = single point of failure

4. Complex protocols:
   - AMQP, STOMP, MQTT
   - High CPU overhead for protocol parsing
```

**Option 2: Custom Log Aggregation (Scribe, Flume)**

```
Problems:
1. Push-based:
   - Brokers push to consumers
   - Consumers can't control rate → overwhelmed

2. No multi-subscriber:
   - 1 topic → 1 consumer
   - Need to duplicate topics for multiple use cases

3. Weak durability:
   - Best-effort delivery
   - No replication
```

#### Kafka's Design Principles (Born from Constraints)

```
Principle 1: Throughput > Features
- Sacrifice: No message routing, no complex filtering
- Gain: 100x throughput (1M msg/sec vs 10K msg/sec)

Principle 2: Distributed by Default
- Sacrifice: More complex deployment
- Gain: Horizontal scaling, fault tolerance

Principle 3: Pull-Based Consumption
- Sacrifice: Consumers must track offsets
- Gain: Consumers control rate, natural backpressure

Principle 4: Persistent Log Storage
- Sacrifice: Higher disk usage
- Gain: Replay capability, multiple consumers

Principle 5: Simplicity
- Sacrifice: Fewer bells and whistles
- Gain: Easier to understand, debug, and operate
```

---

### 🏗️ 2. Architecture (Version 0.7 - Original Design)

#### 2.1 High-Level Components

```
┌──────────────────────────────────────────────────────────────┐
│                         Producers                            │
│  (Web servers, app servers, log collectors)                  │
└────────────┬─────────────────────────┬───────────────────────┘
             │                         │
             │ Push messages           │
             ▼                         ▼
┌──────────────────────┐   ┌──────────────────────┐
│   Broker 1           │   │   Broker 2           │
│                      │   │                      │
│ Topic: user-activity │   │ Topic: user-activity │
│ ├─ Partition 0       │   │ ├─ Partition 1       │
│ └─ Partition 2       │   │ └─ Partition 3       │
│                      │   │                      │
│ Disk: /var/kafka/    │   │ Disk: /var/kafka/    │
│ ├─ part-0/           │   │ ├─ part-1/           │
│ └─ part-2/           │   │ └─ part-3/           │
└──────────┬───────────┘   └──────────┬───────────┘
           │                          │
           │ Pull messages            │
           ▼                          ▼
┌──────────────────────────────────────────────────────────────┐
│                      Consumer Groups                         │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐   │
│  │ Consumer 1    │  │ Consumer 2    │  │ Consumer 3    │   │
│  │ (Reads 0, 2)  │  │ (Reads 1)     │  │ (Reads 3)     │   │
│  └───────────────┘  └───────────────┘  └───────────────┘   │
│  (Hadoop ETL group)                                          │
└──────────────────────────────────────────────────────────────┘
```

#### 2.2 Message Format (v0.7 - Simple!)

```
Message on disk:
┌──────────────────────────────────────┐
│ CRC (4 bytes)                        │  ← Checksum for integrity
├──────────────────────────────────────┤
│ Magic (1 byte)                       │  ← Version marker (0 in v0.7)
├──────────────────────────────────────┤
│ Attributes (1 byte)                  │  ← Compression codec (none, gzip, snappy)
├──────────────────────────────────────┤
│ Key length (4 bytes)                 │  ← -1 if no key
├──────────────────────────────────────┤
│ Key (N bytes)                        │  ← Optional partitioning key
├──────────────────────────────────────┤
│ Value length (4 bytes)               │  ← Message payload size
├──────────────────────────────────────┤
│ Value (N bytes)                      │  ← Actual message data
└──────────────────────────────────────┘

Total overhead: 14 bytes + key length
```

**Design Note:** Simple format → Fast serialization/deserialization

---

### 🚀 3. Key Innovations

#### 3.1 Log-Centric Storage (vs Queue Semantics)

**Traditional Queue:**

```
Message Queue (ActiveMQ):
┌─────────────────────────────────────┐
│ Message 1 (id=101) ← Consumer A     │
│ Message 2 (id=102) ← Consumer B     │
│ Message 3 (id=103) ← Consumer A     │
│ ...                                 │
└─────────────────────────────────────┘

Characteristics:
- Messages deleted after consumption
- Each message consumed by ONE consumer
- No ordering guarantees across consumers
- Complex broker state (track which messages acked)
```

**Kafka's Log:**

```
Kafka Partition (Append-Only Log):
┌─────────────────────────────────────┐
│ Offset 0: Message 1                 │  ← Oldest
│ Offset 1: Message 2                 │
│ Offset 2: Message 3                 │
│ Offset 3: Message 4                 │
│ ...                                 │
│ Offset N: Message N+1               │  ← Newest
└─────────────────────────────────────┘

Consumer A: Reading offset 2
Consumer B: Reading offset 0 (replay from beginning!)

Characteristics:
- Messages retained for configured time (e.g., 7 days)
- Multiple consumers can read same message
- Strict ordering within partition
- Broker is stateless (consumers track offsets)
```

**Why This Matters:**

```java
// Use Case: Reprocess data after bug fix
// Traditional Queue: Impossible! Messages already deleted.
// Kafka: Simply reset consumer offset to beginning

Consumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.assign(Arrays.asList(new TopicPartition("user-activity", 0)));

// Replay from 1 week ago
long oneWeekAgo = System.currentTimeMillis() - (7 * 24 * 60 * 60 * 1000);
Map<TopicPartition, Long> timestamps = new HashMap<>();
timestamps.put(new TopicPartition("user-activity", 0), oneWeekAgo);

Map<TopicPartition, OffsetAndTimestamp> offsets = consumer.offsetsForTimes(timestamps);
consumer.seek(new TopicPartition("user-activity", 0), offsets.get(...).offset());

// Now consume from 1 week ago!
while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    // Reprocess...
}
```

---

#### 3.2 Partitioning for Parallelism

**Problem:** Single log file → Single consumer → Limited throughput

**Solution:** Partition topic into multiple independent logs

```
Topic: user-activity (4 partitions)

┌─────────────────────────────────────┐
│ Partition 0 (Leader: Broker 1)      │
│ ├─ alice clicked "Buy"              │
│ ├─ charlie viewed homepage          │
│ └─ ...                              │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Partition 1 (Leader: Broker 2)      │
│ ├─ bob searched "laptop"            │
│ ├─ diana added to cart              │
│ └─ ...                              │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Partition 2 (Leader: Broker 1)      │
│ ├─ evan logged in                   │
│ └─ ...                              │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Partition 3 (Leader: Broker 2)      │
│ ├─ frank rated product              │
│ └─ ...                              │
└─────────────────────────────────────┘

Partitioning Strategy (Producer):
1. If message has key: partition = hash(key) % num_partitions
   - Example: hash("alice") % 4 = 0 → Partition 0
   - Benefit: All events for "alice" in same partition (ordering!)

2. If no key: round-robin or sticky partitioner
   - Benefit: Load balancing

Consumer Group (4 consumers):
- Consumer 1 reads Partition 0
- Consumer 2 reads Partition 1
- Consumer 3 reads Partition 2
- Consumer 4 reads Partition 3

Total throughput: 4x single-partition throughput!
```

**Mathematical Proof:**

```
Single partition:
- Producer rate: R msg/sec
- Consumer rate: C msg/sec
- If R > C: Lag accumulates (BAD!)

N partitions:
- Producer rate per partition: R/N msg/sec
- N consumers, each consuming C msg/sec
- Total consumer capacity: N × C msg/sec
- Condition for stability: R < N × C
- Can scale by adding partitions + consumers!
```

---

#### 3.3 Sequential Disk I/O (Faster than Random RAM!)

**Counterintuitive Fact:**

```
Performance comparison:
┌──────────────────────────────────────────────────────────┐
│ Operation             │ Latency       │ Throughput       │
├──────────────────────────────────────────────────────────┤
│ Random disk read      │ 10 ms         │ 100 IOPS         │
│ Sequential disk read  │ 0.1 ms        │ 600 MB/sec       │
│ Random RAM read       │ 0.0001 ms     │ 10 GB/sec        │
└──────────────────────────────────────────────────────────┘

Key Insight:
Sequential disk reads (600 MB/sec) > Random RAM reads for large datasets!
```

**Kafka's Exploitation:**

```
Write path:
1. Producer sends message batch
2. Broker appends to end of partition log (SEQUENTIAL WRITE)
3. OS page cache buffers writes
4. Background flush to disk (sequential, batched)

Read path:
1. Consumer requests messages from offset N
2. Broker reads from disk (SEQUENTIAL READ)
3. OS page cache likely has data (cache hit!)
4. sendfile() zero-copy to network (no RAM copying)

Result:
- Write throughput: 600 MB/sec per disk
- Read throughput: 1 GB/sec per disk (if cached)
- Latency: <10ms end-to-end at 100K msg/sec
```

**Benchmark from Paper:**

```
Setup:
- 3 brokers (2011 hardware: 4-core CPU, 16 GB RAM, 6x 2TB SATA)
- Topic: 10 partitions, replication factor = 2
- Message size: 200 bytes
- Producers: 10 threads

Results:
- Producer throughput: 50,000 msg/sec = 10 MB/sec per broker
- Consumer throughput: 100,000 msg/sec = 20 MB/sec per broker
- p99 latency: 5 ms

Conclusion: Disk is NOT a bottleneck if used sequentially!
```

---

#### 3.4 Consumer Offset Management (Broker is Stateless)

**Traditional Queue (Broker Tracks State):**

```
Broker state:
┌───────────────────────────────────────┐
│ Message 101: Sent to Consumer A ✓    │
│ Message 102: Sent to Consumer B ✓    │
│ Message 103: Sent to Consumer A ✗    │  ← Pending ACK
│ Message 104: Not sent                 │
└───────────────────────────────────────┘

Problem:
- Broker must track per-message ACKs
- Complex state → slow broker restarts
- Lost ACKs → duplicate delivery
```

**Kafka (Consumer Tracks Offset):**

```
Partition state (Broker):
┌───────────────────────────────────────┐
│ Offset 0: Message 1                   │
│ Offset 1: Message 2                   │
│ Offset 2: Message 3                   │
│ Offset 3: Message 4                   │
│ ...                                   │
└───────────────────────────────────────┘

Consumer state (Consumer):
┌───────────────────────────────────────┐
│ Last committed offset: 2              │
│ Current fetch offset: 3               │
└───────────────────────────────────────┘

Broker doesn't care about consumer state!
- Fast restarts (just replay log)
- No ACK protocol overhead
```

**Offset Commit Strategies:**

```java
// v0.7: Manual offset commit to ZooKeeper
Properties props = new Properties();
props.put("zookeeper.connect", "localhost:2181");
props.put("group.id", "my-group");

ConsumerConnector consumer = Consumer.createJavaConsumerConnector(new ConsumerConfig(props));
Map<String, List<KafkaStream<byte[], byte[]>>> streams = consumer.createMessageStreams(...);

for (MessageAndMetadata<byte[], byte[]> msg : streams.get("topic").get(0)) {
    // Process message
    processMessage(msg.message());
    
    // Manually commit offset to ZooKeeper
    consumer.commitOffsets();  // Blocking call!
}

// Problems:
// - ZooKeeper write for every commit (slow!)
// - If consumer crashes before commit → reprocess messages
// - If consumer commits before processing → lose messages
```

---

### 📊 4. Performance Evaluation (From Paper)

#### 4.1 Producer Throughput

```
Experiment 1: Vary message size
┌──────────────────────────────────────────────────────────┐
│ Message Size │ Throughput (msg/sec) │ Throughput (MB/s) │
├──────────────────────────────────────────────────────────┤
│ 10 bytes     │ 400,000              │ 4 MB/sec          │
│ 100 bytes    │ 200,000              │ 20 MB/sec         │
│ 1,000 bytes  │ 50,000               │ 50 MB/sec         │
│ 10,000 bytes │ 10,000               │ 100 MB/sec        │
└──────────────────────────────────────────────────────────┘

Observation:
- Small messages: Limited by network round-trips
- Large messages: Limited by disk bandwidth
- Sweet spot: 1-10 KB messages
```

#### 4.2 Consumer Throughput

```
Experiment 2: Consumer throughput (varying # of consumers)
┌──────────────────────────────────────────────────────────┐
│ # Consumers │ Partitions │ Throughput/Consumer (msg/s) │
├──────────────────────────────────────────────────────────┤
│ 1           │ 10         │ 100,000                     │  ← Limited by single thread
│ 2           │ 10         │ 100,000 each                │  ← 2x total throughput
│ 5           │ 10         │ 100,000 each                │  ← 5x total throughput
│ 10          │ 10         │ 100,000 each                │  ← 10x total throughput (linear!)
└──────────────────────────────────────────────────────────┘

Observation: Linear scaling up to # of partitions
```

#### 4.3 End-to-End Latency

```
Experiment 3: Latency breakdown
┌──────────────────────────────────────────────────────────┐
│ Component                  │ Latency (ms)               │
├──────────────────────────────────────────────────────────┤
│ Producer → Broker          │ 2 ms                       │
│ Broker disk write          │ 0 ms (cached)              │
│ Broker → Consumer          │ 2 ms                       │
│ Consumer processing        │ 1 ms                       │
├──────────────────────────────────────────────────────────┤
│ Total (median)             │ 5 ms                       │
│ p99 latency                │ 10 ms                      │
│ p99.9 latency              │ 50 ms (disk flush)         │
└──────────────────────────────────────────────────────────┘
```

---

### 🔑 5. Key Takeaways from Original Kafka Paper

1. **Log-centric design** enables replay, multi-subscriber, and simple broker state
2. **Partitioning** is the key to horizontal scalability (not sharding!)
3. **Sequential I/O** on modern disks rivals random RAM access for streaming workloads
4. **Pull-based consumption** puts backpressure control in consumer hands
5. **Simplicity** beats feature richness for high-throughput systems

**Quote from Paper:**

> "We made a few unusual, yet practical, choices in the design. First, we use a simple storage format which is just a log of messages. This is in sharp contrast to many existing messaging systems which use sophisticated indexing structures such as B-trees. Second, we push the state management to the consumer. This makes the server very simple and stateless."

---

<a name="the-log-abstraction"></a>
## 📄 Paper 2: The Log: What every software engineer should know about real-time data's unifying abstraction

**Author:** Jay Kreps (LinkedIn, Confluent)  
**Published:** 2013 (LinkedIn Engineering Blog)  
**Impact:** Conceptual foundation for Kafka, Samza, and event-driven architectures

### 🎯 Core Thesis

The **distributed log** is a fundamental abstraction that unifies:
- **Databases** (commit log, write-ahead log)
- **Distributed consensus** (Paxos, Raft logs)
- **Stream processing** (Kafka topics)
- **Data integration** (CDC, event sourcing)

```
Universal Pattern:
┌──────────────────────────────────────────────────────────┐
│ All these systems use an append-only log internally:     │
├──────────────────────────────────────────────────────────┤
│ 1. MySQL binlog       → Replication to replicas         │
│ 2. PostgreSQL WAL     → Crash recovery                   │
│ 3. Cassandra commit   → Eventual consistency            │
│ 4. Kafka topic        → Event streaming                  │
│ 5. Raft log           → Consensus (leader election)      │
│ 6. Blockchain         → Immutable transaction history    │
└──────────────────────────────────────────────────────────┘

Common properties:
- Append-only (immutable)
- Totally ordered (within partition)
- Persistent
- Replayable
```

---

### 💡 Key Insights

#### Insight 1: State is a Derivative of a Log

```
Traditional View (State as Primary):
┌─────────────────┐
│ Database Table  │  ← This is the "source of truth"
│ ├─ Row 1        │
│ ├─ Row 2        │
│ └─ Row 3        │
└─────────────────┘

Log View (Log as Primary):
┌────────────────────────────────────┐
│ Event Log (Source of Truth)       │
│ ├─ Event 1: INSERT user alice     │  ← Offset 0
│ ├─ Event 2: INSERT user bob       │  ← Offset 1
│ ├─ Event 3: UPDATE user alice     │  ← Offset 2
│ └─ Event 4: DELETE user bob       │  ← Offset 3
└────────────────────────────────────┘
         │
         │ Apply log events
         ▼
┌─────────────────┐
│ Derived State   │  ← Materialized view of log
│ ├─ alice (v2)   │
│ └─ bob (deleted)│
└─────────────────┘

Benefits:
- State can be rebuilt from log (disaster recovery)
- Multiple consumers create different views (OLTP DB, OLAP warehouse, search index)
- Time travel (replay log to state at any point)
```

**Example: Event Sourcing**

```java
// Traditional CRUD
public void updateUserEmail(String userId, String newEmail) {
    db.execute("UPDATE users SET email = ? WHERE id = ?", newEmail, userId);
    // Lost: WHO changed it, WHEN, WHY, what was old value?
}

// Event Sourcing (Log-Centric)
public void updateUserEmail(String userId, String newEmail) {
    Event event = new UserEmailChangedEvent(
        userId, 
        newEmail, 
        oldEmail,  // Captured!
        currentUser,  // WHO
        System.currentTimeMillis(),  // WHEN
        "User requested change"  // WHY
    );
    eventLog.append(event);  // Append to Kafka
    
    // State is derived by replaying events
}

// Rebuild state from events
public Map<String, User> rebuildUserState(EventLog log) {
    Map<String, User> users = new HashMap<>();
    for (Event event : log) {
        if (event instanceof UserCreatedEvent) {
            users.put(event.userId, new User(event.data));
        } else if (event instanceof UserEmailChangedEvent) {
            users.get(event.userId).setEmail(event.newEmail);
        }
    }
    return users;
}
```

---

#### Insight 2: Logs Enable Decoupling

**Problem: Tightly Coupled Systems**

```
Monolithic Architecture:
┌───────────────────────────────────────────┐
│ Application                               │
│ ├─ Order Service                          │
│ ├─ Payment Service                        │
│ ├─ Inventory Service                      │
│ └─ Notification Service                   │
│                                           │
│ All in one database:                      │
│ ┌──────────────────────┐                 │
│ │ orders table         │                  │
│ │ payments table       │                  │
│ │ inventory table      │                  │
│ │ notifications table  │                  │
│ └──────────────────────┘                 │
└───────────────────────────────────────────┘

Problems:
- Schema conflicts (can't change orders table without breaking others)
- Scaling bottleneck (single database)
- No clear ownership
```

**Solution: Log as Integration Layer**

```
Event-Driven Architecture (Kafka as Log):
┌────────────────────┐      ┌────────────────────┐
│ Order Service      │      │ Kafka Topic:       │
│                    │─────▶│ "order-events"     │
│ Database: Orders   │      │ ├─ OrderCreated    │
└────────────────────┘      │ ├─ OrderPaid       │
                            │ └─ OrderShipped    │
                            └─────────┬──────────┘
                                      │ All subscribe
       ┌──────────────────────────────┼──────────────────────┐
       │                              │                      │
       ▼                              ▼                      ▼
┌────────────────┐      ┌────────────────────┐   ┌─────────────────┐
│ Payment Svc    │      │ Inventory Svc      │   │ Notification    │
│ DB: Payments   │      │ DB: Inventory      │   │ DB: (none)      │
└────────────────┘      └────────────────────┘   └─────────────────┘

Benefits:
- Services are independent (own database, own schema)
- Add new consumers without changing producers
- Temporal decoupling (consumers can be offline, catch up later)
```

---

#### Insight 3: Ordering is Hard in Distributed Systems

```
The Problem:
┌────────────────────────────────────────────────────────────┐
│ Two events happen "simultaneously" in different data       │
│ centers:                                                   │
│                                                            │
│ DC1 (10:00:00.500): User alice adds item to cart          │
│ DC2 (10:00:00.501): User alice updates shipping address   │
│                                                            │
│ Question: Which event happened first?                     │
│ Answer: Impossible to know without coordination!          │
│         (Clocks in different DCs not synchronized)        │
└────────────────────────────────────────────────────────────┘

Kafka's Solution: Partition-Level Ordering
┌────────────────────────────────────────────────────────────┐
│ Partition for user alice (single leader broker):          │
│ ├─ Offset 0: Add item to cart         (10:00:00.500)      │
│ └─ Offset 1: Update shipping address   (10:00:00.501)     │
│                                                            │
│ Total order guaranteed within partition!                  │
│ Events across partitions have NO ordering guarantee.      │
└────────────────────────────────────────────────────────────┘
```

**Design Implication:**

- Partition key = entity that needs ordering (e.g., user ID, order ID)
- All events for same key go to same partition
- Trade-off: More partitions = more parallelism, but NO cross-partition ordering

---

### 📚 Recommended Reading from "The Log"

- **Consensus:** *Paxos Made Simple* by Leslie Lamport
- **State Machines:** *Time, Clocks, and the Ordering of Events* by Lamport
- **Distributed Databases:** *Dynamo* (Amazon), *BigTable* (Google)

---

<a name="exactly-once-kip-98"></a>
## 📄 Paper 3: Exactly-Once Semantics (KIP-98, KIP-129)

**Authors:** Guozhang Wang, Jason Gustafson (Confluent)  
**Published:** 2017 (Kafka 0.11.0)  
**Impact:** First distributed streaming system with end-to-end exactly-once semantics

### 🎯 The Exactly-Once Problem

```
Delivery Semantics in Distributed Systems:

1. At-Most-Once:
   - Send message, don't wait for ACK
   - If failure → message lost
   - Use case: Metrics (missing a few OK)

2. At-Least-Once:
   - Send message, retry until ACK
   - If duplicate ACK → message duplicated
   - Use case: Most systems (handle duplicates downstream)

3. Exactly-Once:
   - Send message exactly once, no loss, no duplicates
   - Use case: Financial transactions, billing
   - Challenge: Distributed consensus + idempotence + transactions
```

**Why It's Hard:**

```
Scenario: Transfer $100 from Account A to Account B

Step 1: Producer sends: {"account": "A", "amount": -100}
Step 2: Broker writes to disk
Step 3: Broker ACKs to producer
Step 4: Producer sends: {"account": "B", "amount": +100}
Step 5: Broker writes to disk
Step 6: Broker ACKs to producer

Failure Mode 1: Step 3 ACK lost (network failure)
- Producer retries Step 1
- Result: Account A debited twice! (-$200)

Failure Mode 2: Producer crashes between Step 3 and Step 4
- $100 lost (A debited, B never credited)

Failure Mode 3: Consumer reads Step 1, crashes before processing Step 2
- Consumer restarts, re-reads Step 1 and Step 2
- But: Consumer already processed Step 1 (side effect: database write)
- Result: A debited twice!
```

---

### 🔧 KIP-98 Solution: Idempotent Producers

```
Key Idea: Assign each producer a unique ID and sequence number

Producer initialization:
┌─────────────────────────────────────────────────────────┐
│ 1. Producer sends InitProducerIdRequest to broker       │
│ 2. Broker assigns unique ProducerId (e.g., 12345)       │
│ 3. Producer stores ProducerId + epoch (0)               │
└─────────────────────────────────────────────────────────┘

Message send with sequence numbers:
┌─────────────────────────────────────────────────────────┐
│ Producer sends:                                         │
│ ├─ ProducerId: 12345                                    │
│ ├─ Epoch: 0                                             │
│ ├─ Sequence: 0                                          │
│ └─ Message: {"account": "A", "amount": -100}            │
│                                                         │
│ Broker checks:                                          │
│ ├─ Last sequence for ProducerId 12345 = none           │
│ ├─ Expected next sequence = 0                          │
│ ├─ Matches! Write to log.                              │
│ └─ Update state: LastSequence[12345] = 0               │
└─────────────────────────────────────────────────────────┘

Retry scenario (ACK lost):
┌─────────────────────────────────────────────────────────┐
│ Producer retries:                                       │
│ ├─ ProducerId: 12345                                    │
│ ├─ Epoch: 0                                             │
│ ├─ Sequence: 0  ← Same as before!                       │
│ └─ Message: {"account": "A", "amount": -100}            │
│                                                         │
│ Broker checks:                                          │
│ ├─ Last sequence for ProducerId 12345 = 0              │
│ ├─ Expected next sequence = 1                          │
│ ├─ Received sequence 0 < 1 → Duplicate!                │
│ └─ Return success (idempotent), DO NOT write again     │
└─────────────────────────────────────────────────────────┘

Result: Duplicate sends are detected and discarded!
```

**Producer Configuration:**

```java
Properties props = new Properties();
props.put("bootstrap.servers", "localhost:9092");
props.put("enable.idempotence", "true");  // ← Enable idempotence

// These are automatically set when enable.idempotence=true:
// props.put("acks", "all");
// props.put("retries", Integer.MAX_VALUE);
// props.put("max.in.flight.requests.per.connection", 5);

Producer<String, String> producer = new KafkaProducer<>(props);

// Sends are now idempotent!
producer.send(new ProducerRecord<>("topic", "key", "value"));
```

---

### 🔄 KIP-98 Solution: Transactional Producers

Idempotence solves duplicates but NOT atomicity. Transactions solve atomicity.

```
Transaction Coordinator (special Kafka broker):
┌──────────────────────────────────────────────────────────┐
│ Internal topic: __transaction_state (50 partitions)      │
│                                                          │
│ Stores:                                                  │
│ ├─ TransactionalId → ProducerId mapping                 │
│ ├─ Transaction state (Ongoing, PrepareCommit, etc.)     │
│ └─ Partitions involved in transaction                   │
└──────────────────────────────────────────────────────────┘
```

**Transaction Flow:**

```
Phase 1: InitTransactions
Producer → Coordinator: InitProducerIdRequest
  - TransactionalId: "account-transfer-producer-1"

Coordinator:
  - Checks if TransactionalId exists
  - If yes: Increment epoch (fence old producers)
  - Assign ProducerId (e.g., 12345) + Epoch (e.g., 5)
  - Return to producer

Phase 2: BeginTransaction
Producer: Local state change (TRANSACTION_STARTED)
  - No network call yet!

Phase 3: Send Messages
Producer → Broker (Partition Leader):
  - First send to a partition → AddPartitionsToTxn RPC to coordinator
  - Coordinator stores: txn[12345] = {partitions: [topic-0]}
  - Then actual message send with headers:
      * ProducerId: 12345
      * Epoch: 5
      * Sequence: 0
      * IsTransactional: true

Phase 4: CommitTransaction
Producer → Coordinator: EndTxnRequest (COMMIT)

Coordinator (2-phase commit):
  Step 1: Write PREPARE_COMMIT to __transaction_state
  Step 2: Send WriteTxnMarkers to all partition leaders
    - Each partition appends control record: [COMMIT, producerId=12345]
  Step 3: Write COMPLETE_COMMIT to __transaction_state
  Step 4: Delete transaction state

Consumer side:
- isolation.level=read_committed
- Sees messages only after COMMIT marker
- Aborted transactions are filtered out
```

---

### 📊 Performance Impact (From KIP-98)

```
Benchmark: 1 million messages, 1 KB each

No Idempotence:
- Throughput: 800,000 msg/sec
- Latency: 2 ms p99

Idempotent Producer:
- Throughput: 750,000 msg/sec (-6%)
- Latency: 3 ms p99 (+50%)
- Overhead: Sequence number check per message

Transactional Producer:
- Throughput: 500,000 msg/sec (-37%)
- Latency: 8 ms p99 (+300%)
- Overhead: 2-phase commit, control records

Conclusion: Idempotence is cheap, transactions are expensive (but necessary for correctness!)
```

---

<a name="kraft-kip-500"></a>
## 📄 Paper 4: KRaft: Removing ZooKeeper Dependency (KIP-500)

**Authors:** Colin McCabe, Jason Gustafson (Confluent)  
**Published:** 2020 (GA in Kafka 3.3, Sept 2022)  
**Impact:** Removed ZooKeeper dependency, simplified operations, improved scalability

### 🎯 Motivation: Why Remove ZooKeeper?

```
Problems with ZooKeeper:
┌──────────────────────────────────────────────────────────┐
│ 1. Operational Complexity:                               │
│    - Two systems to monitor (Kafka + ZooKeeper)          │
│    - Two upgrade paths                                   │
│    - Two sets of security configs                        │
│                                                          │
│ 2. Scalability Limits:                                   │
│    - ZooKeeper metadata stored in RAM                    │
│    - Max ~200K partitions per cluster (ZK bottleneck)    │
│    - Slow leader elections with 100K+ partitions         │
│                                                          │
│ 3. Consistency Model Mismatch:                           │
│    - ZooKeeper: Strict linearizability (slow)            │
│    - Kafka: Only needs eventual consistency for metadata │
│                                                          │
│ 4. Split-Brain Risk:                                     │
│    - ZK quorum failure → Kafka cluster unavailable       │
│    - Network partition → ZK and Kafka disagree           │
└──────────────────────────────────────────────────────────┘
```

### 🏗️ KRaft Architecture (Raft-Based)

KRaft implements the **Raft consensus protocol** directly in Kafka brokers:

```
Traditional Kafka (with ZooKeeper):
┌──────────────────────────────────────────────────────────┐
│ ZooKeeper Ensemble                                       │
│ ├─ ZK Node 1 (Leader)                                    │
│ ├─ ZK Node 2 (Follower)                                  │
│ └─ ZK Node 3 (Follower)                                  │
│                                                          │
│ Stores:                                                  │
│ ├─ Cluster metadata (broker list, topic configs)        │
│ ├─ Partition leaders                                     │
│ └─ Access control lists (ACLs)                           │
└─────────────┬────────────────────────────────────────────┘
              │ Watches + RPCs
              ▼
┌──────────────────────────────────────────────────────────┐
│ Kafka Brokers                                            │
│ ├─ Broker 1                                              │
│ ├─ Broker 2                                              │
│ └─ Broker 3                                              │
└──────────────────────────────────────────────────────────┘

KRaft Kafka (No ZooKeeper):
┌──────────────────────────────────────────────────────────┐
│ Kafka Controllers (Raft Quorum)                          │
│ ├─ Controller 1 (Raft Leader) ← Active controller       │
│ ├─ Controller 2 (Raft Follower)                         │
│ └─ Controller 3 (Raft Follower)                         │
│                                                          │
│ Metadata Log Topic: __cluster_metadata                   │
│ ├─ Offset 0: RegisterBroker (id=1)                      │
│ ├─ Offset 1: CreateTopic (name=orders, partitions=10)   │
│ ├─ Offset 2: UpdatePartitionLeader (topic=orders, ...)  │
│ └─ Offset N: ...                                         │
└─────────────┬────────────────────────────────────────────┘
              │ Metadata replication (Raft)
              ▼
┌──────────────────────────────────────────────────────────┐
│ Kafka Data Brokers                                       │
│ ├─ Broker 1 (reads metadata log)                        │
│ ├─ Broker 2 (reads metadata log)                        │
│ └─ Broker 3 (reads metadata log)                        │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 Raft Consensus in KRaft

```
Raft Protocol (Simplified):

1. Leader Election:
   ┌──────────────────────────────────────┐
   │ Controllers start in Follower state  │
   │ ├─ Election timeout: 150-300ms       │
   │ └─ If no heartbeat → become Candidate│
   └──────────────┬───────────────────────┘
                  │
   ┌──────────────▼───────────────────────┐
   │ Candidate requests votes:            │
   │ ├─ Send RequestVote RPC              │
   │ ├─ Include last log index + term     │
   │ └─ Need majority (e.g., 2 of 3)      │
   └──────────────┬───────────────────────┘
                  │
   ┌──────────────▼───────────────────────┐
   │ Majority votes received              │
   │ → Become Leader                      │
   │ ├─ Send heartbeats every 50ms        │
   │ └─ Accept metadata changes           │
   └──────────────────────────────────────┘

2. Log Replication:
   Client → Leader: CreateTopic request
   Leader:
     1. Append to local log
     2. Send AppendEntries RPC to Followers
     3. Wait for majority ACK
     4. Mark entry as committed
     5. Apply to state machine
     6. Respond to client

3. Safety Guarantees:
   - Election Safety: At most 1 leader per term
   - Leader Append-Only: Leader never deletes/overwrites entries
   - Log Matching: If two logs contain entry with same index+term,
                   all preceding entries are identical
   - Leader Completeness: If entry committed in term T,
                          it's in logs of all leaders in future terms
   - State Machine Safety: If broker applies entry at index N,
                           no other broker applies different entry at N
```

---

### 📈 Performance Improvements (From KIP-500)

```
Benchmark: Cluster with 1 million partitions

With ZooKeeper:
- Startup time: 30 minutes (ZK metadata load)
- Leader election (controlled shutdown): 5 seconds
- Leader election (unclean failure): 60 seconds
- Memory usage (ZK ensemble): 64 GB RAM

With KRaft:
- Startup time: 2 minutes (93% improvement)
- Leader election (controlled shutdown): 1 second (80% improvement)
- Leader election (unclean failure): 5 seconds (92% improvement)
- Memory usage (controllers): 16 GB RAM (75% reduction)

Scalability:
- ZooKeeper: Max 200K partitions (metadata limit)
- KRaft: Tested with 10 million partitions ✓
```

---

### 🔐 Security & Isolation

```
KRaft Roles:

1. Controller-Only Mode:
   - Dedicated controllers (separate servers)
   - Do NOT serve data partitions
   - Higher isolation, better for large clusters

   server.properties (controller):
   process.roles=controller
   controller.quorum.voters=1@controller1:9093,2@controller2:9093,3@controller3:9093

2. Broker-Only Mode:
   - Data brokers connect to controller quorum
   - Read metadata log, serve partitions

   server.properties (broker):
   process.roles=broker
   controller.quorum.voters=1@controller1:9093,2@controller2:9093,3@controller3:9093

3. Combined Mode (for small clusters):
   - Single server acts as both controller + broker
   - Simpler deployment, lower hardware cost

   server.properties:
   process.roles=broker,controller
   controller.quorum.voters=1@node1:9093,2@node2:9093,3@node3:9093
```

---

<a name="tiered-storage-kip-405"></a>
## 📄 Paper 5: Tiered Storage (KIP-405)

**Authors:** Satish Duggana (Uber), Ying Zheng (Uber)  
**Published:** 2020 (experimental in Kafka 2.8, production in 3.6+)  
**Impact:** Enables infinite retention with 90% cost savings

### 🎯 Problem: Storage Cost at Scale

```
Scenario: 10 TB/day ingestion, 90-day retention

Traditional Kafka (all on local disk):
┌──────────────────────────────────────────────────────────┐
│ Total storage: 10 TB/day × 90 days = 900 TB             │
│ Replication factor: 3                                    │
│ Actual storage: 900 TB × 3 = 2,700 TB = 2.7 PB          │
│                                                          │
│ Hardware: 30 brokers × 100 TB NVMe SSD each              │
│ Cost: $4,000/month per broker × 30 = $120,000/month     │
└──────────────────────────────────────────────────────────┘

Tiered Storage (hot on SSD, cold on S3):
┌──────────────────────────────────────────────────────────┐
│ Hot tier (last 7 days): 10 TB/day × 7 = 70 TB × 3 = 210 TB│
│ Hardware: 10 brokers × 30 TB SSD                         │
│ Cost: $1,500/month per broker × 10 = $15,000/month      │
│                                                          │
│ Cold tier (8-90 days): 10 TB/day × 83 days = 830 TB     │
│ S3 storage (no replication needed): 830 TB              │
│ Cost: $0.023/GB/month × 830,000 GB = $19,090/month      │
│                                                          │
│ Total: $15,000 + $19,090 = $34,090/month                │
│ Savings: $120,000 - $34,090 = $85,910/month (72%)       │
└──────────────────────────────────────────────────────────┘
```

---

### 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Producer                                                    │
└─────────────┬───────────────────────────────────────────────┘
              │ Writes
              ▼
┌─────────────────────────────────────────────────────────────┐
│ Broker (Partition Leader)                                   │
│                                                             │
│ Active Segment (local disk):                                │
│ ├─ 00000000000000200000.log (current)                       │
│ └─ 00000000000000200000.index                               │
│                                                             │
│ Recent Segments (local disk):                               │
│ ├─ 00000000000000100000.log (rolled 1 hour ago)             │
│ └─ 00000000000000100000.index                               │
└────────────┬────────────────────────────────────────────────┘
             │
             │ Automatic offload (background task)
             │ Condition: segment.timestamp < now - 7 days
             ▼
┌─────────────────────────────────────────────────────────────┐
│ Remote Storage (S3 / GCS / Azure Blob)                      │
│                                                             │
│ s3://kafka-tiered/topic-partition-0/                        │
│ ├─ 00000000000000000000.log                                 │
│ ├─ 00000000000000000000.index                               │
│ ├─ 00000000000000000000.timeindex                           │
│ ├─ ...                                                      │
│ └─ 00000000000000090000.log (8-89 days old)                 │
└─────────────────────────────────────────────────────────────┘
             │
             │ Consumer reads old data
             ▼
┌─────────────────────────────────────────────────────────────┐
│ Consumer                                                    │
│ - Recent data: Read from broker (fast, <10ms)              │
│ - Old data: Read from S3 (slower, ~100ms, but acceptable)  │
└─────────────────────────────────────────────────────────────┘
```

---

### ⚙️ Configuration

```properties
# server.properties (Broker)

# Enable tiered storage
remote.log.storage.system.enable=true

# Remote storage implementation (S3)
remote.log.storage.manager.class.name=org.apache.kafka.server.log.remote.storage.S3RemoteLogStorageManager

# S3 credentials
remote.log.storage.manager.impl.prefix=rsm.
rsm.s3.bucket=kafka-tiered-storage
rsm.s3.region=us-west-2
rsm.s3.access.key=AKIAIOSFODNN7EXAMPLE
rsm.s3.secret.key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# Offload policy
local.retention.ms=604800000  # Keep 7 days locally
local.retention.bytes=-1      # No local size limit
retention.ms=7776000000       # Total retention 90 days (in S3)

# Remote log manager task interval
remote.log.manager.task.interval.ms=30000  # Check every 30s for offload
```

**Topic-Level Override:**

```bash
kafka-configs --bootstrap-server localhost:9092 \
  --entity-type topics \
  --entity-name important-topic \
  --alter \
  --add-config retention.ms=31536000000  # 1 year total retention
  --add-config local.retention.ms=86400000  # 1 day local
```

---

### 🔍 Consumer Fetch Flow (Tiered Storage)

```
Consumer Request: Fetch offset 50,000 from topic "orders-0"

Step 1: Broker checks local segments
┌────────────────────────────────────────────────────┐
│ Local segments:                                    │
│ ├─ 00000000000000100000.log (offsets 100K-200K)   │
│ └─ 00000000000000200000.log (offsets 200K-300K)   │
│                                                    │
│ Offset 50,000 NOT found locally!                  │
└────────────────────────────────────────────────────┘

Step 2: Broker checks RemoteLogMetadata cache
┌────────────────────────────────────────────────────┐
│ RemoteLogMetadata (in-memory index):               │
│ ├─ Segment 00000000000000000000 → s3://...        │
│ │  Offsets: 0-100,000                             │
│ ├─ Segment 00000000000000050000 → s3://...        │
│ │  Offsets: 50,000-100,000  ← Found!              │
│ └─ ...                                             │
└────────────────────────────────────────────────────┘

Step 3: Broker fetches from S3
┌────────────────────────────────────────────────────┐
│ S3 GET: s3://kafka-tiered/.../00000000000000050000.log│
│ Cache locally (optional)                           │
│ Read offset 50,000                                 │
│ Return to consumer                                 │
└────────────────────────────────────────────────────┘

Latency:
- Local fetch: 5 ms
- Remote fetch (S3): 100 ms (20x slower, but acceptable for cold data)
```

---

### 💰 Real-World Case Study: Uber

**Before Tiered Storage (2019):**
- 4,000 brokers
- 100 PB local storage (SSDs)
- $10 million/year storage cost

**After Tiered Storage (2023):**
- 2,000 brokers (50% reduction)
- 20 PB local storage (SSDs)
- 500 PB remote storage (S3)
- $2 million/year storage cost (80% savings!)

**Key Metrics:**
- 99.9% of reads from local storage (hot data)
- 0.1% of reads from S3 (cold data, acceptable latency)
- Zero data loss during S3 outages (local cache + replication)

---

<a name="additional-papers"></a>
## 📚 Additional Influential Papers

### 1. **Samza: Stateful Scalable Stream Processing at LinkedIn** (2017)

**Key Contributions:**
- Kafka as the **storage layer** for stream processing state
- Changelog topics for fault-tolerant state stores
- Local RocksDB + remote Kafka for state = Kafka Streams foundation

---

### 2. **MillWheel: Fault-Tolerant Stream Processing at Internet Scale** (Google, 2013)

**Influenced Kafka:**
- Exactly-once processing with idempotent operations
- Watermarks for event-time processing (later adopted in Kafka Streams)
- Persistent timers for windowing

---

### 3. **Apache Flink: Stream and Batch Processing in a Single Engine** (2015)

**Comparison with Kafka Streams:**
- Flink: Separate cluster, richer windowing, cyclic dataflows
- Kafka Streams: Embedded library, simpler deployment, Kafka-native
- Both use changelogs for state fault tolerance

---

## 🎓 Summary: Why These Papers Matter

1. **Kafka (2011)**: Proved log-centric design scales to millions of messages/sec
2. **The Log**: Unified abstraction for databases, streams, and consensus
3. **KIP-98**: First production exactly-once semantics in distributed streaming
4. **KIP-500**: Removed external dependency (ZK), simplified operations
5. **KIP-405**: Enabled infinite retention with 90% cost savings

**For Interviews:**
- Explain **why** Kafka uses logs (not queues)
- Describe **how** exactly-once works (producer IDs, sequences, transactions)
- Compare **Raft** (KRaft) vs **ZooKeeper** (consistency vs availability)
- Justify **when** to use tiered storage (cost/latency trade-offs)

---

**End of WHITEPAPERS** | [Next: README →](README.md) | [Back to EXPERT](EXPERT.md)
