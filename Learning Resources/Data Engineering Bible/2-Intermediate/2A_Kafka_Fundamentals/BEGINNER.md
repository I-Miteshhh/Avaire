# Week 5: Kafka & Distributed Messaging — BEGINNER Track

*"Kafka is not a message queue. It's a distributed commit log that happens to be really good at messaging."* — Jay Kreps

---

## 🎯 Learning Outcomes

By the end of this module, you will deeply understand:

- **Why Kafka exists**: The fundamental problems traditional message queues couldn't solve
- **The commit log abstraction**: Why append-only logs are the universal data structure
- **Kafka's architecture**: Brokers, topics, partitions, producers, consumers, and ZooKeeper/KRaft
- **Delivery semantics**: At-most-once, at-least-once, and exactly-once explained from first principles
- **Replication protocol**: How Kafka achieves fault tolerance without sacrificing throughput
- **Consumer groups**: Parallel processing, rebalancing, and offset management
- **Production patterns**: Idempotent producers, transactional writes, and backpressure handling

---

## 📚 Prerequisites: What You Must Know First

Before diving into Kafka, let's build the foundational mental models. **You cannot understand Kafka without understanding these concepts first.**

### 1. The Problem: Why Traditional Message Queues Failed at Scale

#### The Old World: Point-to-Point Queues (RabbitMQ, ActiveMQ, IBM MQ)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Producer   │────▶│    Queue    │────▶│  Consumer   │
│  (Sender)   │     │   (Broker)  │     │ (Receiver)  │
└─────────────┘     └─────────────┘     └─────────────┘

Message Flow:
1. Producer sends message to queue
2. Broker stores message in memory/disk
3. Consumer pulls message
4. Message is DELETED from queue (destructive read!)
5. If consumer crashes → message lost (unless using ACKs)
```

**Problems with Traditional Queues:**

1. **Destructive Reads**: Once consumed, messages are gone. No replay capability.
2. **Memory Bottlenecks**: Queues must hold ALL unconsumed messages in memory.
3. **Throughput Limits**: Typical queues handle ~10K msg/sec. Modern systems need millions.
4. **No Multi-Subscriber Support**: Each message consumed once. Hard to broadcast.
5. **Ordering Guarantees**: Either global ordering (slow) or no ordering (chaos).
6. **State Management**: Broker tracks which messages each consumer has seen (complex!).

#### Real-World Failure Example: LinkedIn's Problem (2010)

LinkedIn tried using ActiveMQ for their activity stream:
- **Volume**: 1.3 billion events/day = **15,000 events/second**
- **ActiveMQ Performance**: ~10,000 msg/sec with acknowledgments
- **Result**: Queue backed up, messages dropped, data loss

**They needed something fundamentally different.**

---

### 2. The Paradigm Shift: From Queue to Log

#### What is a Commit Log?

A commit log is an **append-only**, **totally-ordered** sequence of records.

```
Position:  0    1    2    3    4    5    6    7
           ┌────┬────┬────┬────┬────┬────┬────┬────┐
Log:       │ A  │ B  │ C  │ D  │ E  │ F  │ G  │ H  │
           └────┴────┴────┴────┴────┴────┴────┴────┘
            ▲                             ▲
            │                             │
         Oldest                       Newest
         (immutable)                  (append here)

Key Properties:
- Append-only: New records added to end
- Immutable: Old records never change
- Ordered: Each record has a position (offset)
- Retained: Records stay in log (not deleted on read)
```

**This is the same data structure used by:**
- **Databases**: WAL (Write-Ahead Log) in PostgreSQL, MySQL binlog
- **Distributed Systems**: Raft log, Paxos log
- **File Systems**: Ext4 journal, NTFS change journal
- **Event Sourcing**: All state changes as events

#### Why Logs Beat Queues

| Feature | Traditional Queue | Commit Log (Kafka) |
|---------|-------------------|---------------------|
| **Read Model** | Destructive (message deleted) | Non-destructive (message retained) |
| **Throughput** | 10K msg/sec | 1M+ msg/sec |
| **Storage** | Memory-bound | Disk-sequential (cheap!) |
| **Replay** | Impossible | Seek to any offset |
| **Multi-Consumer** | Hard (fan-out queues) | Native (each tracks own offset) |
| **Ordering** | Global OR per-key | Per-partition ordering |
| **State Tracking** | Broker tracks state | Consumer tracks offset |

---

### 3. The Mental Model: Kafka as a Distributed File System for Events

Think of Kafka like this:

```
Kafka Topic = Massive Append-Only File Partitioned Across Machines

Topic: "user-clicks"
├─ Partition 0 (on Broker 1):
│  ├─ Segment 0.log: [msg0, msg1, msg2, ..., msg999]
│  ├─ Segment 1.log: [msg1000, ..., msg1999]
│  └─ Segment 2.log: [msg2000, ..., msg2999]
│
├─ Partition 1 (on Broker 2):
│  ├─ Segment 0.log: [msg0, msg1, msg2, ..., msg999]
│  └─ Segment 1.log: [msg1000, ..., msg1999]
│
└─ Partition 2 (on Broker 3):
   ├─ Segment 0.log: [msg0, msg1, msg2, ..., msg999]
   └─ Segment 1.log: [msg1000, ..., msg1999]

Key Insight:
- Writing = Appending to file (sequential disk I/O = FAST!)
- Reading = Sequential read from offset (predictable, cacheable)
- Scaling = Add more partitions
```

**Why Sequential Disk Beats Random Memory:**

```
Performance Numbers (from LinkedIn's benchmarks):
- Random disk seeks: ~100 IOPS (10ms per seek)
- Sequential disk reads: ~100 MB/sec (modern SSD: 500+ MB/sec)
- Random memory access: ~100 GB/sec
- Sequential disk > Random memory for large batches!

Kafka's Secret Sauce:
1. Append-only writes = Sequential disk (fast!)
2. OS page cache = Free memory caching
3. Zero-copy = sendfile() syscall (kernel → socket, no userspace copy)
4. Batching = Amortize syscall overhead
```

---

## 🏗️ Kafka Architecture: The Complete Picture

Now that you understand **why** Kafka exists, let's learn **how** it works.

### Core Components

```
┌──────────────────────────────────────────────────────────────────┐
│                         Kafka Cluster                            │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  Broker 1   │  │  Broker 2   │  │  Broker 3   │            │
│  │             │  │             │  │             │            │
│  │ Topic: logs │  │ Topic: logs │  │ Topic: logs │            │
│  │ └─Part 0    │  │ └─Part 1    │  │ └─Part 2    │            │
│  │   (Leader)  │  │   (Follower)│  │   (Leader)  │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│         ▲                 ▲                 ▲                   │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           │                                     │
│                 ┌─────────┴─────────┐                          │
│                 │    ZooKeeper      │                          │
│                 │  (Metadata Store)  │                          │
│                 └────────────────────┘                          │
└──────────────────────────────────────────────────────────────────┘
         ▲                                        │
         │                                        ▼
    ┌────┴───┐                              ┌────┴───┐
    │Producer│                              │Consumer│
    └────────┘                              └────────┘
```

#### Component Breakdown

**1. Broker**
- A single Kafka server (think: one machine in the cluster)
- Stores partitions on local disk
- Handles client requests (produce, fetch, metadata)
- Coordinates with other brokers for replication

**2. Topic**
- Logical category of messages (e.g., "user-clicks", "orders", "logs")
- Partitioned across multiple brokers
- Configurable retention (time-based or size-based)

**3. Partition**
- **The unit of parallelism** in Kafka
- Append-only log stored on disk
- Messages within a partition are **totally ordered**
- Each partition has one leader and N-1 followers (replicas)

**4. Producer**
- Publishes messages to topics
- Chooses partition (round-robin, key-hash, or custom)
- Handles retries, batching, compression

**5. Consumer**
- Reads messages from partitions
- Tracks offset (position in log)
- Part of a consumer group (for load balancing)

**6. ZooKeeper (or KRaft in Kafka 3.0+)**
- **Metadata store**: Topic configs, partition assignments, broker registry
- **Leader election**: Which broker is leader for each partition
- **Consumer group coordination**: (deprecated in new consumer API)

---

### Deep Dive: Topic Partitioning

**Why Partitions?**

1. **Scalability**: Single partition limited by one disk. More partitions = more throughput.
2. **Parallelism**: Each consumer in a group reads from different partitions.
3. **Ordering**: Messages in same partition stay ordered.

#### Partition Assignment Example

```
Topic: "orders" (6 partitions, replication factor = 3)

Partition Distribution:
┌─────────────────────────────────────────────────────────┐
│ Broker 1         │ Broker 2         │ Broker 3         │
├──────────────────┼──────────────────┼──────────────────┤
│ Part 0 (Leader)  │ Part 0 (Follower)│ Part 0 (Follower)│
│ Part 1 (Follower)│ Part 1 (Leader)  │ Part 1 (Follower)│
│ Part 2 (Follower)│ Part 2 (Follower)│ Part 2 (Leader)  │
│ Part 3 (Leader)  │ Part 3 (Follower)│ Part 3 (Follower)│
│ Part 4 (Follower)│ Part 4 (Leader)  │ Part 4 (Follower)│
│ Part 5 (Follower)│ Part 5 (Follower)│ Part 5 (Leader)  │
└──────────────────┴──────────────────┴──────────────────┘

Leadership Spread:
- Broker 1: Leader for partitions 0, 3
- Broker 2: Leader for partitions 1, 4
- Broker 3: Leader for partitions 2, 5

Benefits:
✓ Load balanced across brokers
✓ Fault tolerant (2 copies can fail)
✓ Each partition has 1 authoritative leader
```

#### How Producers Choose Partitions

```java
// Method 1: Explicit partition
producer.send(new ProducerRecord<>("orders", 2, key, value));
                                           // ▲
                                    // Partition 2

// Method 2: Key-based hashing (most common)
producer.send(new ProducerRecord<>("orders", "user123", orderData));
// Hash("user123") % 6 = 4 → Always goes to Partition 4
// Same key = Same partition = Ordering guaranteed!

// Method 3: Round-robin (no key provided)
producer.send(new ProducerRecord<>("orders", null, orderData));
// Distributes evenly: P0, P1, P2, P3, P4, P5, P0, P1, ...

// Method 4: Custom partitioner
class CustomPartitioner implements Partitioner {
    public int partition(String topic, Object key, byte[] keyBytes,
                        Object value, byte[] valueBytes, Cluster cluster) {
        if (key.equals("VIP_USER"))
            return 0; // VIP users go to partition 0 (fast SSD!)
        else
            return hash(keyBytes) % cluster.partitionCountForTopic(topic);
    }
}
```

**Key Insight**: Partitioning is **the fundamental trade-off** in Kafka:
- ✅ More partitions = More throughput, better parallelism
- ❌ More partitions = More overhead (file handles, ZK metadata, leader election time)
- 🎯 Sweet spot: 1000-4000 partitions per broker

---

### Deep Dive: Replication Protocol (ISR - In-Sync Replicas)

Kafka's replication is **different** from traditional consensus (Raft, Paxos). Here's why:

#### Traditional Consensus (Raft/Paxos)

```
Client → Leader → Wait for majority ACK → Commit → Respond

Timeline:
T0: Client writes "X"
T1: Leader replicates to Follower 1, Follower 2
T2: Leader waits for ACK from Follower 1 OR Follower 2 (quorum)
T3: Leader commits and responds to client

Latency: 2 network round-trips (leader → followers → leader)
```

#### Kafka's ISR Model

```
Producer → Leader → Followers pull asynchronously → Commit based on ISR

┌────────────────────────────────────────────────────┐
│ Partition 0 State                                  │
│                                                    │
│ Leader (Broker 1):    [msg0, msg1, msg2, msg3]    │
│ Follower 1 (Broker 2): [msg0, msg1, msg2]  ← ISR  │
│ Follower 2 (Broker 3): [msg0, msg1, msg2]  ← ISR  │
│ Follower 3 (Broker 4): [msg0]             ← Out of sync!
│                                                    │
│ ISR Set: {Broker 1, Broker 2, Broker 3}          │
│ High Water Mark (HWM): offset 2                   │
│    (last offset replicated to ALL ISR members)    │
└────────────────────────────────────────────────────┘

Key Concepts:
- ISR = Set of replicas that are "caught up" with leader
- A replica is ISR if it fetched within replica.lag.time.max.ms (default 10s)
- Messages visible to consumers only AFTER replicated to all ISR
```

#### The Brilliance of ISR

**Problem Kafka Solved:**

Traditional consensus: "Wait for majority of ALL replicas"
- If 1 slow replica, system slows down
- If replica dies, need to reconfigure quorum (complex!)

Kafka ISR: "Wait for ALL replicas that are actually keeping up"
- Slow replica falls out of ISR automatically
- System maintains throughput
- When replica catches up, rejoins ISR automatically

```
Scenario: One slow follower

Traditional Quorum (3 replicas, need 2 ACKs):
Leader writes msg1
├─ Follower 1 ACKs in 5ms   ✓
├─ Follower 2 ACKs in 5ms   ✓
└─ Follower 3 ACKs in 2000ms (SLOW!)
Commit latency: 5ms (only need 2 ACKs, ignore slow one)

Kafka ISR (3 replicas, all in ISR):
Leader writes msg1
├─ Follower 1 ACKs in 5ms   ✓
├─ Follower 2 ACKs in 5ms   ✓
└─ Follower 3 ACKs in 2000ms (SLOW!)

After 10 seconds:
- Follower 3 kicked out of ISR
- ISR = {Leader, Follower 1, Follower 2}
- Commit latency drops to 5ms!
- When Follower 3 catches up, rejoins ISR
```

#### Producer Acknowledgment Modes

```java
// acks=0: Fire and forget (no durability guarantee)
props.put("acks", "0");
// Leader doesn't wait for replication
// Fastest, but can lose data if leader crashes before replication

// acks=1: Leader acknowledgment (default in old versions)
props.put("acks", "1");
// Leader writes to local log, then ACKs
// Can lose data if leader crashes AFTER ACK but BEFORE replication

// acks=all (or acks=-1): ISR acknowledgment (safest)
props.put("acks", "all");
// Leader waits for all ISR replicas to write
// Won't lose data as long as 1 ISR replica survives
// Combined with min.insync.replicas=2, guarantees durability
```

**Critical Configuration: min.insync.replicas**

```
Scenario: Replication factor = 3, min.insync.replicas = 2

Normal operation:
ISR = {Broker 1, Broker 2, Broker 3} → Writes succeed ✓

One broker dies:
ISR = {Broker 1, Broker 2} → Writes still succeed ✓
(ISR size 2 >= min.insync.replicas 2)

Two brokers die:
ISR = {Broker 1} → Writes FAIL ✗
(ISR size 1 < min.insync.replicas 2)

Why this matters:
- With min.insync.replicas=1, could lose data if only 1 replica survives and it crashes
- With min.insync.replicas=2, guaranteed 2 copies exist before ACK
- Trade-off: Higher durability vs. lower availability
```

---

### Deep Dive: Consumer Groups and Offset Management

#### The Problem: How Do Multiple Consumers Cooperate?

**Scenario**: You have 1 million events/second. One consumer can't keep up.

**Solution**: Consumer groups provide **automatic load balancing**.

```
Topic: "orders" (6 partitions)
Consumer Group: "order-processors" (3 consumers)

Partition Assignment:
┌─────────────────────────────────────────────────────┐
│ Partition 0 ────▶ Consumer A                       │
│ Partition 1 ────▶ Consumer A                       │
│ Partition 2 ────▶ Consumer B                       │
│ Partition 3 ────▶ Consumer B                       │
│ Partition 4 ────▶ Consumer C                       │
│ Partition 5 ────▶ Consumer C                       │
└─────────────────────────────────────────────────────┘

Rules:
1. Each partition consumed by EXACTLY ONE consumer in group
2. One consumer can read from MULTIPLE partitions
3. Adding consumer → Rebalance (redistribute partitions)
4. Consumer dies → Rebalance (reassign its partitions)
```

#### Rebalancing: The Double-Edged Sword

**What Happens During Rebalance:**

```
Before Rebalance:
Consumer A: [P0, P1]
Consumer B: [P2, P3]
Consumer C: [P4, P5]

New Consumer D joins!

During Rebalance (all consumers STOP processing):
1. Consumers commit offsets
2. Coordinator picks rebalancing strategy
3. Partitions redistributed
4. Consumers resume from committed offsets

After Rebalance:
Consumer A: [P0, P1]
Consumer B: [P2]
Consumer C: [P3, P4]
Consumer D: [P5]

Downtime: 5-30 seconds (session.timeout.ms + rebalance.timeout.ms)
```

**Why Rebalancing is Problematic:**

1. **Stop-the-World**: ALL consumers in group stop processing
2. **Duplicate Processing**: Messages between last commit and rebalance processed twice
3. **Thundering Herd**: All consumers reconnect simultaneously

**Modern Solution: Incremental Cooperative Rebalancing (Kafka 2.4+)**

```
Old (EAGER protocol):
Rebalance → Stop ALL consumers → Reassign ALL partitions

New (COOPERATIVE protocol):
Rebalance → Stop ONLY consumers losing partitions → Reassign incrementally

Example:
Consumer A: [P0, P1] → Only stops P1
Consumer B: [P2, P3] → Keeps processing!
Consumer C: [P4, P5] → Keeps processing!
Consumer D: [] → Takes P1

Result: Minimal downtime, only affected partitions pause
```

#### Offset Management: The Consumer's Bookmark

**What is an Offset?**

```
Partition 0:
Position:  0     1     2     3     4     5     6     7
           ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
Messages:  │ M0  │ M1  │ M2  │ M3  │ M4  │ M5  │ M6  │ M7  │
           └─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
                                ▲
                                │
                         Consumer offset = 3
                         (next message to read: M4)
```

**Offset Storage Evolution:**

```
Kafka 0.8: Offsets stored in ZooKeeper
├─ Path: /consumers/{group}/offsets/{topic}/{partition}
├─ Problem: ZooKeeper not designed for high write throughput
└─ Result: ZooKeeper became bottleneck

Kafka 0.9+: Offsets stored in Kafka itself!
├─ Special topic: __consumer_offsets (50 partitions, compacted)
├─ Format: (group, topic, partition) → offset
├─ Benefits: Scales with Kafka, survives ZK outage
└─ Compaction: Only latest offset per key kept
```

**Commit Strategies:**

```java
// 1. Auto-commit (dangerous for exactly-once!)
props.put("enable.auto.commit", "true");
props.put("auto.commit.interval.ms", "5000");
// Commits every 5 seconds in background
// Problem: Can lose messages if consumer crashes between commits

// 2. Manual commit (sync) - safest but slowest
while (true) {
    ConsumerRecords<K, V> records = consumer.poll(Duration.ofMillis(100));
    for (ConsumerRecord<K, V> record : records) {
        process(record);
    }
    consumer.commitSync(); // Blocks until committed
}

// 3. Manual commit (async) - fast but risky
while (true) {
    ConsumerRecords<K, V> records = consumer.poll(Duration.ofMillis(100));
    for (ConsumerRecord<K, V> record : records) {
        process(record);
    }
    consumer.commitAsync((offsets, exception) -> {
        if (exception != null) {
            log.error("Commit failed", exception);
        }
    });
}

// 4. Per-message commit (exactly-once but slow)
for (ConsumerRecord<K, V> record : records) {
    process(record);
    consumer.commitSync(Collections.singletonMap(
        new TopicPartition(record.topic(), record.partition()),
        new OffsetAndMetadata(record.offset() + 1)
    ));
}
```

---

## 🎭 Explain Like I'm 10: Kafka as a Train Station

Let's make this concrete with a fun analogy!

### The Train Station Analogy

```
         🚉 KAFKA CENTRAL STATION 🚉
         
🚂 Train Lines (Topics):
├─ Express Line (topic: "priority-orders")
├─ Local Line (topic: "regular-orders")
└─ Freight Line (topic: "batch-jobs")

🛤️ Tracks (Partitions):
Express Line has 3 tracks:
├─ Track 0: Platform A
├─ Track 1: Platform B
└─ Track 2: Platform C

🚃 Train Cars (Messages):
Each train car carries passengers (data):
├─ Car #0: [Passenger 1, Passenger 2]
├─ Car #1: [Passenger 3, Passenger 4]
└─ Car #2: [Passenger 5, Passenger 6]

👷 Station Masters (Brokers):
├─ Master A: Manages Track 0
├─ Master B: Manages Track 1
├─ Master C: Manages Track 2

📸 Platform Cameras (Replication):
- Each track has 3 cameras (replication factor = 3)
- Main camera (leader), Backup camera 1, Backup camera 2
- If main camera fails, backup becomes main!

🎫 Ticket Inspectors (Consumers):
- Inspection Team "Alpha" (consumer group)
  ├─ Inspector A checks Track 0
  ├─ Inspector B checks Track 1
  └─ Inspector C checks Track 2
- Each inspector remembers last car checked (offset)
```

**The Story:**

1. **Sending Passengers (Producing):**
   ```
   Train Dispatcher (Producer) needs to send passengers:
   
   VIP Passenger "Alice" → Assign to Express Line, Track 0
   Regular Passenger "Bob" → Hash ticket number, lands on Track 2
   Freight Cargo → Round-robin: Track 1, Track 2, Track 0, ...
   ```

2. **Recording Everything (Replication):**
   ```
   Train arrives at Track 0:
   ├─ Main Camera (Leader) records: "Train #42 arrived at 3:15 PM"
   ├─ Backup Camera 1 copies: "Train #42 arrived at 3:15 PM"
   └─ Backup Camera 2 copies: "Train #42 arrived at 3:15 PM"
   
   If Main Camera breaks:
   └─ Backup Camera 1 becomes the new Main Camera!
   ```

3. **Checking Passengers (Consuming):**
   ```
   Inspector A (Consumer) at Track 0:
   ├─ Checks Car #0 (offset 0): "Passenger 1, Passenger 2" ✓
   ├─ Marks checkpoint: "Last checked: Car #0"
   ├─ Checks Car #1 (offset 1): "Passenger 3, Passenger 4" ✓
   ├─ Marks checkpoint: "Last checked: Car #1"
   
   If Inspector A goes on break:
   └─ New Inspector D comes and asks: "Where was Inspector A?"
   └─ Checkpoint says: "Car #1" → Starts at Car #2!
   ```

4. **Team Reorganization (Rebalancing):**
   ```
   Initial Team (3 inspectors, 3 tracks):
   ├─ Inspector A: Track 0
   ├─ Inspector B: Track 1
   └─ Inspector C: Track 2
   
   Inspector D joins the team:
   ├─ EVERYONE STOPS CHECKING! (rebalance pause)
   ├─ Manager reassigns:
   │   ├─ Inspector A: Track 0
   │   ├─ Inspector B: Track 1
   │   ├─ Inspector C: Track 2
   │   └─ Inspector D: Track 3 (new track!)
   └─ Everyone resumes from their last checkpoint
   ```

---

## 🔧 Hands-On: Build Your First Kafka System

Let's build a complete Kafka pipeline step by step. You'll understand every line of code and why it exists.

### Setup: Docker Compose for Local Kafka

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    hostname: zookeeper
    container_name: zookeeper
    ports:
      - "2181:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    volumes:
      - zookeeper-data:/var/lib/zookeeper/data
      - zookeeper-logs:/var/lib/zookeeper/log

  kafka-1:
    image: confluentinc/cp-kafka:7.5.0
    hostname: kafka-1
    container_name: kafka-1
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-1:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 2
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
    volumes:
      - kafka-1-data:/var/lib/kafka/data

  kafka-2:
    image: confluentinc/cp-kafka:7.5.0
    hostname: kafka-2
    container_name: kafka-2
    depends_on:
      - zookeeper
    ports:
      - "9093:9093"
    environment:
      KAFKA_BROKER_ID: 2
      KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-2:29092,PLAINTEXT_HOST://localhost:9093
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 2
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
    volumes:
      - kafka-2-data:/var/lib/kafka/data

  kafka-3:
    image: confluentinc/cp-kafka:7.5.0
    hostname: kafka-3
    container_name: kafka-3
    depends_on:
      - zookeeper
    ports:
      - "9094:9094"
    environment:
      KAFKA_BROKER_ID: 3
      KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-3:29092,PLAINTEXT_HOST://localhost:9094
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 2
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
    volumes:
      - kafka-3-data:/var/lib/kafka/data

volumes:
  zookeeper-data:
  zookeeper-logs:
  kafka-1-data:
  kafka-2-data:
  kafka-3-data:
```

**Start the cluster:**

```powershell
docker-compose up -d
```

**Verify it's running:**

```powershell
docker-compose ps
```

### Create Your First Topic

```powershell
# Create topic with 6 partitions, replication factor 3
docker exec kafka-1 kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic orders \
  --partitions 6 \
  --replication-factor 3 \
  --config retention.ms=604800000 \
  --config segment.ms=3600000

# Explain configuration:
# - retention.ms=604800000 → Keep messages for 7 days
# - segment.ms=3600000 → Roll log segment every hour
```

**Inspect the topic:**

```powershell
docker exec kafka-1 kafka-topics --describe \
  --bootstrap-server localhost:9092 \
  --topic orders

# Output shows partition leaders and ISR:
# Topic: orders  Partition: 0  Leader: 2  Replicas: 2,3,1  Isr: 2,3,1
# Topic: orders  Partition: 1  Leader: 3  Replicas: 3,1,2  Isr: 3,1,2
# ...
```

---

### Producer Implementation: Production-Ready Code

Let's build a producer that handles real-world scenarios: retries, idempotence, batching, compression.

#### Basic Producer (Don't Use This in Production!)

```python
from kafka import KafkaProducer
import json

# Simple producer - missing error handling, retries, etc.
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Send a message
producer.send('orders', {'order_id': 123, 'amount': 99.99})

# Problem: What if network fails? What if broker is down?
# This will silently fail!
```

#### Production-Ready Producer with Complete Configuration

```python
from kafka import KafkaProducer
from kafka.errors import KafkaError, KafkaTimeoutError
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RobustProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            # Cluster Configuration
            bootstrap_servers=['localhost:9092', 'localhost:9093', 'localhost:9094'],
            # ^ Multiple brokers for failover!
            
            # Serialization
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            
            # Durability Settings
            acks='all',  # Wait for all ISR replicas
            # ^ Critical for data safety! Don't use acks=1 in production.
            
            # Idempotence (prevents duplicates on retry)
            enable_idempotence=True,
            # ^ Under the hood: Producer assigns sequence numbers to messages
            # Broker detects duplicates and deduplicates automatically
            
            # Retry Configuration
            retries=3,  # Retry failed sends up to 3 times
            retry_backoff_ms=1000,  # Wait 1s between retries
            max_in_flight_requests_per_connection=5,
            # ^ With idempotence, can have multiple in-flight while maintaining order
            
            # Timeout Configuration
            request_timeout_ms=30000,  # 30s to wait for broker response
            delivery_timeout_ms=120000,  # 2min total time including retries
            
            # Batching (performance optimization)
            batch_size=16384,  # 16KB batch size
            linger_ms=10,  # Wait up to 10ms to fill batch
            # ^ Trade-off: Lower latency vs higher throughput
            
            # Compression (reduces network bandwidth)
            compression_type='snappy',  # Options: gzip, snappy, lz4, zstd
            # ^ Snappy: Good balance of speed and compression ratio
            
            # Buffer Configuration
            buffer_memory=33554432,  # 32MB buffer for pending messages
            max_block_ms=60000,  # Block for 60s if buffer full (then throw exception)
        )
        
    def send_message(self, topic, key, value):
        """
        Send a message with complete error handling.
        
        Args:
            topic: Kafka topic name
            key: Partition key (messages with same key go to same partition)
            value: Message payload (dict)
        
        Returns:
            RecordMetadata if successful, None if failed
        """
        try:
            # Asynchronous send (non-blocking)
            future = self.producer.send(
                topic=topic,
                key=key,
                value=value,
                # Optional: Specify partition manually
                # partition=2,
                # Optional: Add headers (metadata)
                headers=[
                    ('source', b'payment-service'),
                    ('version', b'1.0')
                ]
            )
            
            # Block to get result (for demonstration; in prod, use callbacks)
            record_metadata = future.get(timeout=10)
            
            logger.info(f"Message sent successfully:")
            logger.info(f"  Topic: {record_metadata.topic}")
            logger.info(f"  Partition: {record_metadata.partition}")
            logger.info(f"  Offset: {record_metadata.offset}")
            logger.info(f"  Timestamp: {record_metadata.timestamp}")
            
            return record_metadata
            
        except KafkaTimeoutError:
            logger.error("Timeout waiting for broker response")
            # In production: Send to DLQ, trigger alert
            return None
            
        except KafkaError as e:
            logger.error(f"Kafka error: {e}")
            # Common errors:
            # - TOPIC_AUTHORIZATION_FAILED: ACL issue
            # - INVALID_TOPIC_EXCEPTION: Topic doesn't exist
            # - MESSAGE_TOO_LARGE: Increase max.message.bytes
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
    
    def send_batch(self, topic, messages):
        """
        Send multiple messages efficiently using callbacks.
        
        Args:
            topic: Kafka topic
            messages: List of (key, value) tuples
        """
        success_count = 0
        failure_count = 0
        
        def on_success(metadata):
            nonlocal success_count
            success_count += 1
            logger.debug(f"Sent to partition {metadata.partition}, offset {metadata.offset}")
        
        def on_error(exc):
            nonlocal failure_count
            failure_count += 1
            logger.error(f"Failed to send message: {exc}")
        
        # Send all messages asynchronously
        for key, value in messages:
            self.producer.send(topic, key=key, value=value)\
                .add_callback(on_success)\
                .add_errback(on_error)
        
        # Wait for all sends to complete
        self.producer.flush()
        
        logger.info(f"Batch complete: {success_count} succeeded, {failure_count} failed")
        
        return success_count, failure_count
    
    def close(self):
        """Gracefully shutdown producer."""
        logger.info("Flushing pending messages...")
        self.producer.flush(timeout=30)  # Wait up to 30s for pending sends
        self.producer.close()
        logger.info("Producer closed")

# Usage Example
if __name__ == "__main__":
    producer = RobustProducer()
    
    # Single message
    producer.send_message(
        topic='orders',
        key='user_123',  # All orders from user_123 go to same partition
        value={
            'order_id': 'ORD-2025-001',
            'user_id': 'user_123',
            'items': [
                {'sku': 'WIDGET-A', 'quantity': 2, 'price': 29.99}
            ],
            'total': 59.98,
            'timestamp': '2025-10-11T10:30:00Z'
        }
    )
    
    # Batch of messages
    batch = [
        ('user_123', {'order_id': f'ORD-{i}', 'amount': i * 10})
        for i in range(1000)
    ]
    producer.send_batch('orders', batch)
    
    producer.close()
```

#### Understanding Producer Configuration Deep Dive

**1. Idempotence: How Does It Actually Work?**

```
Without Idempotence:
Producer sends msg1 → Broker receives → Broker crashes before ACK
Producer retries msg1 → Broker recovers → msg1 written AGAIN
Result: Duplicate!

With Idempotence (enable_idempotence=True):
Producer assigns: PID=12345, Sequence=0
Producer sends msg1 (PID=12345, Seq=0) → Broker receives
Broker stores: (PID=12345, Seq=0) → msg1

Producer retries msg1 (PID=12345, Seq=0) → Broker receives
Broker checks: "I already have Seq=0 for PID=12345!"
Broker discards duplicate, sends ACK anyway
Result: Exactly-once delivery to partition!

Technical Details:
- PID (Producer ID): Assigned by broker on first connection
- Sequence Number: Per-partition counter incremented for each message
- Broker maintains last 5 sequences per (PID, Partition) pair
- OutOfOrderSequenceException if gap detected (producer resets)
```

**2. Batching vs Latency Trade-off**

```python
# Low-latency configuration (financial trading)
producer = KafkaProducer(
    batch_size=1,        # Send immediately (no batching)
    linger_ms=0,         # Don't wait
    compression_type=None  # No compression overhead
)
# Result: ~5ms latency, ~10K msg/sec throughput

# High-throughput configuration (log aggregation)
producer = KafkaProducer(
    batch_size=1048576,  # 1MB batches
    linger_ms=100,       # Wait up to 100ms to fill batch
    compression_type='lz4'  # Fast compression
)
# Result: ~100ms latency, ~500K msg/sec throughput

# Balanced configuration (most applications)
producer = KafkaProducer(
    batch_size=16384,    # 16KB (default)
    linger_ms=10,        # 10ms wait
    compression_type='snappy'
)
# Result: ~15ms latency, ~100K msg/sec throughput
```

**3. Compression: When and Why**

```
Message: {"user_id": "user_123", "action": "click", "timestamp": 1234567890}
Original size: 512 bytes

Compression Ratios:
- gzip: 512 → 180 bytes (35% of original) - Highest compression, slowest
- snappy: 512 → 280 bytes (55% of original) - Balanced
- lz4: 512 → 300 bytes (58% of original) - Fastest, lowest compression
- zstd: 512 → 200 bytes (39% of original) - Best ratio/speed balance (Kafka 2.1+)

When to compress:
✓ Text/JSON payloads (70-80% compression)
✓ High network cost (cloud egress charges)
✓ Throughput-bound workloads

When NOT to compress:
✗ Already compressed data (Parquet, images, video)
✗ Latency-critical applications (compression adds CPU overhead)
✗ Tiny messages (<100 bytes) - overhead exceeds benefit
```

---

### Consumer Implementation: Production-Ready Code

Now let's build a consumer that handles rebalancing, offset management, and failure scenarios.

#### Production-Ready Consumer with Complete Configuration

```python
from kafka import KafkaConsumer, TopicPartition, OffsetAndMetadata
from kafka.errors import KafkaError
import json
import logging
import signal
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RobustConsumer:
    def __init__(self, group_id, topics):
        self.running = True
        self.consumer = KafkaConsumer(
            *topics,  # Subscribe to multiple topics
            
            # Cluster Configuration
            bootstrap_servers=['localhost:9092', 'localhost:9093', 'localhost:9094'],
            
            # Consumer Group Configuration
            group_id=group_id,
            # ^ All consumers with same group_id share partition load
            
            # Deserialization
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            
            # Offset Management
            auto_offset_reset='earliest',
            # ^ Options:
            #   - 'earliest': Start from beginning if no committed offset
            #   - 'latest': Start from newest messages
            #   - 'none': Throw exception if no offset found
            
            enable_auto_commit=False,
            # ^ We'll commit manually for exactly-once processing!
            # Auto-commit can lose messages on crash
            
            # Session Management
            session_timeout_ms=30000,  # 30s - max time between heartbeats
            heartbeat_interval_ms=10000,  # 10s - how often to send heartbeat
            # ^ If no heartbeat for session_timeout_ms, consumer kicked out
            
            # Rebalancing Configuration
            max_poll_interval_ms=300000,  # 5min - max time between poll() calls
            # ^ If processing takes >5min, consumer considered dead → rebalance
            
            # Fetch Configuration
            fetch_min_bytes=1,  # Fetch immediately if any data available
            fetch_max_wait_ms=500,  # Wait up to 500ms if no data
            max_partition_fetch_bytes=1048576,  # 1MB per partition per fetch
            
            # Performance Tuning
            max_poll_records=500,  # Return up to 500 records per poll()
            # ^ Lower value = more frequent commits, less data loss on crash
            # ^ Higher value = better throughput, more duplicates on crash
        )
        
        # Graceful shutdown handler
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)
        
    def _shutdown(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def process_message(self, message):
        """
        Process a single message.
        
        This is where your business logic goes!
        """
        try:
            logger.info(f"Processing message:")
            logger.info(f"  Partition: {message.partition}")
            logger.info(f"  Offset: {message.offset}")
            logger.info(f"  Key: {message.key}")
            logger.info(f"  Value: {message.value}")
            logger.info(f"  Timestamp: {message.timestamp}")
            
            # Your business logic here
            # Example: Write to database
            # db.insert(message.value)
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing message at offset {message.offset}: {e}")
            # In production:
            # - Send to dead-letter queue
            # - Write to error log
            # - Trigger alert
            return False
    
    def consume_with_manual_commit(self):
        """
        Consume messages with manual offset management.
        
        This pattern provides exactly-once processing semantics.
        """
        logger.info("Starting consumer...")
        
        try:
            while self.running:
                # Poll for new messages (timeout=1000ms)
                messages = self.consumer.poll(timeout_ms=1000)
                
                if not messages:
                    continue  # No messages, poll again
                
                # Process messages partition by partition
                for topic_partition, records in messages.items():
                    logger.info(f"Received {len(records)} messages from {topic_partition}")
                    
                    for message in records:
                        success = self.process_message(message)
                        
                        if success:
                            # Commit offset AFTER successful processing
                            # This ensures exactly-once: if processing fails, we'll retry
                            self.consumer.commit({
                                topic_partition: OffsetAndMetadata(message.offset + 1, None)
                            })
                            # Note: +1 because offset is inclusive (we want to start at NEXT message)
                        else:
                            # Processing failed - decide what to do
                            logger.warning(f"Skipping failed message at offset {message.offset}")
                            # Options:
                            # 1. Skip and commit (lose message)
                            # 2. Don't commit, retry next poll (may process duplicates)
                            # 3. Send to DLQ and commit
                            
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            self.close()
    
    def consume_with_batch_commit(self):
        """
        Consume with periodic batch commits.
        
        Better throughput than per-message commit, but may duplicate on crash.
        """
        logger.info("Starting consumer with batch commits...")
        
        batch_size = 100
        processed_count = 0
        
        try:
            for message in self.consumer:
                if not self.running:
                    break
                    
                self.process_message(message)
                processed_count += 1
                
                # Commit every 100 messages
                if processed_count % batch_size == 0:
                    self.consumer.commit()
                    logger.info(f"Committed offset after {processed_count} messages")
                    
        except Exception as e:
            logger.error(f"Consumer error: {e}")
        finally:
            # Commit any remaining messages
            self.consumer.commit()
            self.close()
    
    def seek_to_timestamp(self, timestamp_ms):
        """
        Seek to specific timestamp (for reprocessing historical data).
        
        Args:
            timestamp_ms: Unix timestamp in milliseconds
        """
        # Get all assigned partitions
        partitions = self.consumer.assignment()
        
        # Build timestamp dict
        timestamp_dict = {tp: timestamp_ms for tp in partitions}
        
        # Seek to timestamps
        offsets = self.consumer.offsets_for_times(timestamp_dict)
        
        for tp, offset_and_timestamp in offsets.items():
            if offset_and_timestamp is not None:
                self.consumer.seek(tp, offset_and_timestamp.offset)
                logger.info(f"Seeked {tp} to offset {offset_and_timestamp.offset}")
    
    def reset_to_beginning(self):
        """Reset consumer to beginning of all partitions."""
        self.consumer.seek_to_beginning()
        logger.info("Reset consumer to beginning of all partitions")
    
    def get_current_lag(self):
        """
        Calculate consumer lag (how far behind the latest messages).
        
        Returns:
            Dict mapping TopicPartition to lag (in number of messages)
        """
        partitions = self.consumer.assignment()
        lag_info = {}
        
        for partition in partitions:
            # Get current offset (where consumer is)
            committed = self.consumer.committed(partition)
            current_offset = committed if committed else 0
            
            # Get latest offset (end of partition)
            end_offsets = self.consumer.end_offsets([partition])
            latest_offset = end_offsets[partition]
            
            # Calculate lag
            lag = latest_offset - current_offset
            lag_info[partition] = lag
            
            logger.info(f"{partition}: Current={current_offset}, Latest={latest_offset}, Lag={lag}")
        
        return lag_info
    
    def close(self):
        """Gracefully shutdown consumer."""
        logger.info("Closing consumer...")
        self.consumer.close()
        logger.info("Consumer closed")

# Usage Example
if __name__ == "__main__":
    consumer = RobustConsumer(
        group_id='order-processors',
        topics=['orders']
    )
    
    # Check lag before starting
    consumer.get_current_lag()
    
    # Consume with manual commit (exactly-once)
    consumer.consume_with_manual_commit()
```

#### Advanced Consumer Patterns

**1. Multi-Threaded Consumer (Scale-Up Pattern)**

```python
from concurrent.futures import ThreadPoolExecutor
import threading

class MultiThreadedConsumer:
    """
    Single consumer with multiple processing threads.
    
    Use when:
    - Processing is CPU-bound
    - Want to scale up on single machine
    - Order within partition can be relaxed
    """
    def __init__(self, group_id, topics, num_threads=4):
        self.consumer = KafkaConsumer(
            *topics,
            group_id=group_id,
            bootstrap_servers=['localhost:9092'],
            enable_auto_commit=False,
            max_poll_records=num_threads * 10  # Fetch enough for all threads
        )
        self.executor = ThreadPoolExecutor(max_workers=num_threads)
        self.lock = threading.Lock()
        
    def process_message(self, message):
        """Heavy processing in thread pool."""
        # Simulate heavy CPU work
        import time
        time.sleep(0.1)
        logger.info(f"Processed {message.value} in thread {threading.current_thread().name}")
        return message
    
    def run(self):
        """Consume and process in parallel."""
        futures = []
        
        for message in self.consumer:
            # Submit to thread pool
            future = self.executor.submit(self.process_message, message)
            futures.append((message, future))
            
            # Commit in batches
            if len(futures) >= 100:
                # Wait for all futures to complete
                for msg, fut in futures:
                    fut.result()  # Block until done
                
                # Commit offsets (thread-safe!)
                with self.lock:
                    self.consumer.commit()
                
                futures = []
```

**2. Pause/Resume Consumer (Backpressure Handling)**

```python
class BackpressureConsumer:
    """
    Consumer that pauses when downstream system is overloaded.
    
    Example: Database can't keep up with message rate
    """
    def __init__(self, group_id, topics):
        self.consumer = KafkaConsumer(
            *topics,
            group_id=group_id,
            bootstrap_servers=['localhost:9092']
        )
        self.max_queue_size = 1000
        self.processing_queue = []
        
    def run(self):
        while True:
            # Check if downstream is overwhelmed
            if len(self.processing_queue) > self.max_queue_size:
                logger.warning("Queue full, pausing consumer...")
                self.consumer.pause(*self.consumer.assignment())
                
                # Process backlog
                while len(self.processing_queue) > 100:
                    self.process_batch(self.processing_queue[:100])
                    self.processing_queue = self.processing_queue[100:]
                
                # Resume consuming
                logger.info("Queue cleared, resuming consumer...")
                self.consumer.resume(*self.consumer.assignment())
            
            # Poll for new messages
            messages = self.consumer.poll(timeout_ms=1000)
            for tp, records in messages.items():
                self.processing_queue.extend(records)
```

---

## 🎯 Delivery Semantics: The Critical Trade-offs

This is one of the most important concepts in distributed systems. Let's understand each guarantee deeply.

### 1. At-Most-Once Delivery

**Guarantee**: Each message delivered **zero or one times**. May lose messages, but never duplicates.

```
Timeline:
T0: Consumer polls and receives message M1
T1: Consumer processes M1
T2: Consumer commits offset
T3: ❌ CRASH before commit!

Result: Offset never committed → M1 lost forever

Code Pattern:
for message in consumer:
    consumer.commit()  # Commit BEFORE processing
    process(message)   # If this fails, message is lost!
```

**Use Cases:**
- Metrics collection (OK to lose some data points)
- Log aggregation (lossy is acceptable)
- Click tracking (statistical accuracy, not exact)

**Configuration:**
```python
consumer = KafkaConsumer(
    enable_auto_commit=True,
    auto_commit_interval_ms=1000  # Commit every 1s regardless
)
```

---

### 2. At-Least-Once Delivery

**Guarantee**: Each message delivered **one or more times**. Never loses messages, but may duplicate.

```
Timeline:
T0: Consumer polls and receives message M1
T1: Consumer processes M1 ✓
T2: Consumer about to commit offset
T3: ❌ CRASH before commit!
T4: Consumer restarts, polls again
T5: Receives M1 AGAIN (duplicate!)

Result: M1 processed twice

Code Pattern:
for message in consumer:
    process(message)      # Process BEFORE committing
    consumer.commit()     # If crash happens here, duplicate next time
```

**Use Cases:**
- Financial transactions (with idempotent processing)
- Order processing (check if order already exists)
- Email delivery (better to send twice than never)

**Configuration:**
```python
consumer = KafkaConsumer(
    enable_auto_commit=False  # Manual commit after processing
)

for message in consumer:
    process_idempotently(message)  # Must handle duplicates!
    consumer.commit()
```

**Idempotent Processing Pattern:**

```python
def process_order_idempotently(order_message):
    """
    Process order, but detect duplicates.
    """
    order_id = order_message['order_id']
    
    # Check if already processed (database unique constraint)
    if db.order_exists(order_id):
        logger.info(f"Order {order_id} already processed, skipping")
        return  # Idempotent!
    
    # Process order
    db.insert_order(order_message)
    inventory.decrement(order_message['items'])
    payment.charge(order_message['total'])
```

---

### 3. Exactly-Once Semantics (EOS)

**Guarantee**: Each message delivered and processed **exactly one time**. Holy grail of distributed systems!

**How Kafka Achieves Exactly-Once (Deep Dive):**

```
┌──────────────────────────────────────────────────────────┐
│ Exactly-Once = Idempotent Producer + Transactional Writes│
│                + Atomic Read-Process-Write                │
└──────────────────────────────────────────────────────────┘

Component 1: Idempotent Producer
├─ Producer assigns sequence numbers to each message
├─ Broker deduplicates based on (PID, Sequence)
└─ Prevents duplicates on retry

Component 2: Transactions
├─ Producer writes to multiple partitions atomically
├─ Consumer reads only committed transactions
└─ Prevents partial writes

Component 3: Atomic Commit
├─ Consumer commits offset in same transaction as output
├─ If crash happens, BOTH offset and output rolled back
└─ Reprocessing produces same output (idempotent!)
```

#### Exactly-Once Producer Setup

```python
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    
    # Enable idempotence (prevents duplicates)
    enable_idempotence=True,
    
    # Enable transactions
    transactional_id='my-transactional-producer-1',
    # ^ Must be unique per producer instance!
    # ^ Kafka uses this to fence out zombie producers
    
    acks='all',  # Required for transactions
    max_in_flight_requests_per_connection=5,
)

# Initialize transactions
producer.init_transactions()

try:
    # Begin transaction
    producer.begin_transaction()
    
    # Send multiple messages atomically
    producer.send('topic-A', b'message-1')
    producer.send('topic-B', b'message-2')
    producer.send('topic-C', b'message-3')
    
    # All-or-nothing: Either all 3 messages written, or none
    producer.commit_transaction()
    
except Exception as e:
    # Rollback on error
    producer.abort_transaction()
    raise
```

#### Exactly-Once Consumer-Producer (Read-Process-Write Pattern)

```python
from kafka import KafkaConsumer, KafkaProducer, TopicPartition, OffsetAndMetadata

def exactly_once_stream_processing():
    """
    Read from input topic, process, write to output topic.
    Exactly-once guarantee end-to-end!
    """
    consumer = KafkaConsumer(
        'input-topic',
        bootstrap_servers=['localhost:9092'],
        group_id='stream-processor',
        enable_auto_commit=False,
        isolation_level='read_committed'  # Only read committed transactions!
    )
    
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        enable_idempotence=True,
        transactional_id='stream-processor-1'
    )
    
    producer.init_transactions()
    
    for message in consumer:
        try:
            producer.begin_transaction()
            
            # Process message
            result = process(message.value)
            
            # Write result to output topic
            producer.send('output-topic', result)
            
            # Commit consumer offset IN SAME TRANSACTION!
            offsets = {
                TopicPartition(message.topic, message.partition):
                OffsetAndMetadata(message.offset + 1, None)
            }
            producer.send_offsets_to_transaction(
                offsets,
                consumer.config['group_id']
            )
            
            # Commit transaction (atomic: output + offset)
            producer.commit_transaction()
            
            # If crash happens here, BOTH output and offset rolled back!
            # On restart, will reprocess message and produce same output
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            producer.abort_transaction()
```

**How Transaction Coordinator Works (Under the Hood):**

```
┌─────────────────────────────────────────────────────────────┐
│ Transaction State Machine                                   │
│                                                             │
│ BEGIN → ONGOING → PREPARE_COMMIT → COMPLETED               │
│            │                                                │
│            └──────→ PREPARE_ABORT → ABORTED                │
└─────────────────────────────────────────────────────────────┘

Step-by-Step:
1. Producer calls begin_transaction()
   └─ Coordinator marks transaction as ONGOING

2. Producer sends messages to partitions
   └─ Messages written with transaction markers
   └─ Not visible to consumers yet!

3. Producer calls commit_transaction()
   └─ Coordinator writes to __transaction_state topic
   └─ State: PREPARE_COMMIT

4. Coordinator writes COMMIT marker to all partitions
   └─ Messages now visible to consumers!
   └─ State: COMPLETED

If crash at any step before COMMIT marker:
└─ Coordinator aborts transaction
└─ Messages never become visible
```

---

## 🚀 Performance Tuning: Getting to 1M+ Messages/Second

Let's optimize our Kafka setup for maximum throughput.

### Producer Tuning

```python
# HIGH THROUGHPUT PRODUCER
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    
    # Batching (most important for throughput!)
    batch_size=1048576,  # 1MB batches (default: 16KB)
    linger_ms=100,  # Wait 100ms to accumulate batch
    # ^ Larger batches = better compression, fewer requests
    
    # Compression
    compression_type='lz4',  # Fastest compression
    # ^ lz4: 3-4x compression with minimal CPU overhead
    
    # Buffer
    buffer_memory=67108864,  # 64MB (default: 32MB)
    # ^ Larger buffer = can handle bursty traffic
    
    # Reduce round-trips
    acks='1',  # Only wait for leader (not all ISR)
    # ^ Trade durability for speed (use 'all' for critical data)
    
    # Pipelining
    max_in_flight_requests_per_connection=10,
    # ^ Send multiple batches without waiting for ACK
    # ⚠️ Warning: Can reorder messages if retries > 0
    #   Solution: Use enable_idempotence=True
)

# Expected throughput: 500K-1M msg/sec on modern hardware
```

### Consumer Tuning

```python
# HIGH THROUGHPUT CONSUMER
consumer = KafkaConsumer(
    'high-volume-topic',
    bootstrap_servers=['localhost:9092'],
    
    # Fetch more data per request
    max_partition_fetch_bytes=10485760,  # 10MB (default: 1MB)
    fetch_min_bytes=1048576,  # Wait for 1MB before returning
    fetch_max_wait_ms=500,  # But don't wait more than 500ms
    
    # Process more records per poll
    max_poll_records=5000,  # Default: 500
    # ^ Larger batches = better throughput
    # ^ But increases risk of exceeding max_poll_interval_ms
    
    # Disable auto-commit for batch processing
    enable_auto_commit=False,
)

# Batch processing pattern
batch_size = 1000
batch = []

for message in consumer:
    batch.append(message)
    
    if len(batch) >= batch_size:
        # Process entire batch
        process_batch(batch)
        
        # Commit once per batch (not per message!)
        consumer.commit()
        batch = []

# Expected throughput: 300K-500K msg/sec
```

### Broker-Level Tuning

```properties
# server.properties

# --- Network ---
num.network.threads=8
# ^ Threads handling network requests
# ^ Rule of thumb: # of CPU cores

num.io.threads=16
# ^ Threads handling disk I/O
# ^ Rule of thumb: 2x # of disks

socket.send.buffer.bytes=1048576
socket.receive.buffer.bytes=1048576
# ^ 1MB socket buffers (OS default often too small)

# --- Replication ---
num.replica.fetchers=4
# ^ Threads fetching data from leader
# ^ More threads = faster replication catch-up

replica.fetch.max.bytes=10485760
# ^ Fetch up to 10MB per replication request

# --- Log Retention ---
log.retention.hours=168
# ^ Keep logs for 7 days (168 hours)

log.segment.bytes=1073741824
# ^ 1GB log segments
# ^ Smaller = faster log compaction, more files
# ^ Larger = fewer files, slower compaction

log.roll.hours=24
# ^ Roll new segment every 24 hours

# --- Log Cleanup ---
log.cleanup.policy=delete
# ^ Options: delete (time/size-based) or compact (keep latest per key)

# --- Compression ---
compression.type=producer
# ^ Use producer's compression (don't recompress broker-side)

# --- Flush (don't change unless you know what you're doing!) ---
log.flush.interval.messages=9223372036854775807
log.flush.interval.ms=9223372036854775807
# ^ Effectively infinite: rely on OS page cache
# ^ Kafka's design: Don't fsync, trust replication for durability
```

---

## 🐛 Common Pitfalls and Debugging

### 1. Consumer Lag Explosion

**Symptom**: Consumer falls behind, lag increases forever

```
Diagnosis:
$ kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group my-group --describe

GROUP           TOPIC   PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
my-group        orders  0          1000            10000           9000  ← LAG!
my-group        orders  1          2000            12000           10000 ← LAG!
```

**Causes & Solutions**:

```python
# Cause 1: Processing too slow
# Solution: Scale out (add more consumers)

# Before (1 consumer, 3 partitions)
# Consumer 1: [P0, P1, P2] ← bottleneck!

# After (3 consumers, 3 partitions)
# Consumer 1: [P0]
# Consumer 2: [P1]
# Consumer 3: [P2]

# Cause 2: max_poll_interval_ms exceeded
consumer = KafkaConsumer(
    max_poll_interval_ms=300000,  # 5 minutes
)

# If processing takes >5min, consumer kicked out → rebalance → lag
# Solution: Increase max_poll_interval_ms OR reduce max_poll_records

# Cause 3: GC pauses (JVM consumers)
# Solution: Tune JVM GC, use G1GC
java -Xms4g -Xmx4g \
     -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=20 \
     -XX:InitiatingHeapOccupancyPercent=35 \
     -jar consumer.jar
```

### 2. Rebalancing Storms

**Symptom**: Continuous rebalancing, no progress made

```
[2025-10-11 10:30:00] Rebalancing...
[2025-10-11 10:30:15] Rebalancing...
[2025-10-11 10:30:30] Rebalancing...
```

**Causes**:

1. **Session timeout too low**:
   ```python
   consumer = KafkaConsumer(
       session_timeout_ms=10000,  # 10s - too aggressive!
       heartbeat_interval_ms=3000,
   )
   # If network hiccup >10s → consumer kicked → rebalance
   
   # Solution: Increase timeouts
   session_timeout_ms=30000,  # 30s
   heartbeat_interval_ms=10000,  # 10s
   ```

2. **Processing exceeds max_poll_interval_ms**:
   ```python
   # Symptom in logs:
   # "Member ... sending LeaveGroup request due to consumer poll timeout"
   
   # Solution: Process faster OR increase timeout
   max_poll_interval_ms=600000,  # 10 minutes
   ```

3. **Too many consumers for partitions**:
   ```
   Topic has 3 partitions, but 10 consumers in group
   
   Active consumers:
   - Consumer 1: [P0]
   - Consumer 2: [P1]
   - Consumer 3: [P2]
   
   Idle consumers (trigger rebalances trying to get partitions):
   - Consumers 4-10: []
   
   Solution: # consumers <= # partitions
   ```

### 3. Lost Messages Despite acks=all

**Scenario**: Producer uses `acks=all`, but messages still lost!

```python
producer = KafkaProducer(
    acks='all',  # Wait for all ISR replicas
    # ⚠️ But what if ISR={Leader} only?
)

# Dangerous scenario:
# Replication factor = 3, but 2 followers are down
# ISR = {Broker 1 (leader)}
# Producer sends with acks=all → Leader writes → ACKs immediately
# Leader crashes before followers catch up → DATA LOST!

# Solution: Set min.insync.replicas
# Topic config:
min.insync.replicas=2

# Now:
# ISR = {Broker 1} → Writes REJECTED!
# "NotEnoughReplicasException: Not enough in-sync replicas"
# Forces you to fix replication before accepting writes
```

### 4. Out-of-Order Messages

```python
# Scenario: Messages appear out of order!
producer.send('orders', key='user_123', value={'seq': 1})
producer.send('orders', key='user_123', value={'seq': 2})
producer.send('orders', key='user_123', value={'seq': 3})

# Consumer receives: seq 1, seq 3, seq 2 ← OUT OF ORDER!

# Cause: Retries with in-flight requests
producer = KafkaProducer(
    retries=3,
    max_in_flight_requests_per_connection=5,
    enable_idempotence=False,  # ← This is the problem!
)

# What happens:
# Batch 1 [seq=1] sent → SUCCESS
# Batch 2 [seq=2] sent → TIMEOUT → Retry queued
# Batch 3 [seq=3] sent → SUCCESS (before retry!)
# Batch 2 [seq=2] retry → SUCCESS (arrives late!)

# Solutions:
# Option 1: Enable idempotence (maintains order)
enable_idempotence=True

# Option 2: Disable pipelining (slow!)
max_in_flight_requests_per_connection=1

# Option 3: Don't retry (risk data loss)
retries=0
```

---

## 📝 Interview Prep: Key Questions

### Question 1: How does Kafka achieve such high throughput compared to traditional message queues?

**Answer**: 

Kafka's performance comes from five key architectural decisions:

1. **Sequential Disk I/O**: Kafka is append-only. Sequential writes to disk can reach 600MB/s on modern SSDs, comparable to memory for large batches. Traditional queues do random I/O.

2. **Zero-Copy**: Kafka uses the `sendfile()` system call to transfer data from disk → OS page cache → network socket without copying to userspace. Saves CPU and memory bandwidth.

3. **Batching**: Kafka batches messages at multiple levels:
   - Producer batches before sending
   - Broker writes batches to disk
   - Consumer fetches batches
   - Network protocol is batch-oriented
   
   This amortizes overhead (syscalls, network RTT, disk seeks).

4. **OS Page Cache**: Kafka doesn't manage an in-memory cache. It relies on the OS page cache, which is more efficient (zero-copy, pre-fetching, etc.).

5. **Partition Parallelism**: Kafka scales horizontally by partitioning. Each partition is an independent log that can be on different brokers, enabling linear scaling.

**Follow-up**: *What's the trade-off with this design?*

Answer: Latency. Batching adds latency (linger.ms). For ultra-low-latency (<1ms), traditional queues with in-memory storage can be faster. Kafka optimizes for throughput over latency.

---

### Question 2: Explain the ISR protocol and why it's better than traditional quorum-based replication.

**Answer**:

Traditional Quorum (Raft/Paxos):
- Need majority of ALL replicas to ACK
- If you have 5 replicas and 2 are slow, you still need 3 ACKs (including slow ones)
- Result: Latency determined by median replica speed

Kafka ISR:
- Only replicas that are "in-sync" (caught up within `replica.lag.time.max.ms`) are in the ISR
- Producer waits for ALL ISR members, but ISR dynamically shrinks if replicas fall behind
- Slow replicas are kicked out of ISR automatically
- Result: Latency determined by fast replicas, not median

Benefits:
1. **Throughput preserved**: Slow replicas don't slow down writes
2. **Durability maintained**: Still wait for replication, just to fast replicas
3. **Automatic recovery**: When slow replica catches up, it rejoins ISR automatically

Trade-off:
- If ISR shrinks to just the leader and leader crashes, you can lose data
- Mitigation: Use `min.insync.replicas` to enforce minimum ISR size

---

### Question 3: How would you design a system to process 10 million events per second with exactly-once semantics?

**Answer**:

Architecture:
```
Producers (1000 instances)
  ↓
Kafka (100 brokers, 1000 partitions)
  ↓
Stream Processors (Kafka Streams / Flink) - 500 instances
  ↓
Output (Database / Kafka / S3)
```

Configuration:

1. **Producers**:
   ```python
   enable_idempotence=True  # Prevent duplicates
   acks='all'  # Durability
   batch_size=1MB  # High throughput
   linger_ms=10
   compression_type='lz4'
   ```

2. **Kafka Cluster**:
   - 100 brokers across 3 availability zones
   - 1000 partitions (10K msg/sec per partition)
   - Replication factor = 3
   - min.insync.replicas = 2
   - Disk: NVMe SSDs for high throughput

3. **Stream Processing**:
   ```python
   # Kafka Streams exactly-once
   properties.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG,
                  StreamsConfig.EXACTLY_ONCE_V2)
   ```

4. **Scaling Math**:
   - 10M events/sec ÷ 1000 partitions = 10K events/sec per partition ✓
   - Each consumer handles ~2 partitions (500 consumers × 2 = 1000 partitions)
   - Per-consumer throughput: 20K events/sec (easily achievable)

5. **Monitoring**:
   - Consumer lag alerts
   - End-to-end latency tracking
   - Partition skew detection
   - Rebalance frequency metrics

**Follow-up**: *What if one partition becomes a hotspot?*

Answer: 
- Option 1: Re-partition with better key distribution
- Option 2: Add random suffix to hot keys (e.g., `user_123_0`, `user_123_1`)
- Option 3: Process hot partition separately with more resources

---

## 🎓 Next Steps

You now have a deep understanding of Kafka fundamentals! Here's what to explore next:

### Immediate Practice
1. **Set up local cluster**: Run the Docker Compose example
2. **Build end-to-end pipeline**: Producer → Kafka → Consumer → Database
3. **Test failure scenarios**: Kill brokers, kill consumers, fill disk
4. **Measure performance**: Benchmark your setup with kafka-producer-perf-test

### Advanced Topics (covered in INTERMEDIATE track)
- Multi-datacenter replication (MirrorMaker 2)
- Schema Registry and Avro
- Kafka Connect for data integration
- ksqlDB for stream processing with SQL
- Monitoring and observability (JMX metrics, Burrow)

### Production Readiness Checklist
- [ ] Monitoring: Set up Prometheus + Grafana for Kafka metrics
- [ ] Alerting: Consumer lag, under-replicated partitions, disk usage
- [ ] Security: Enable SSL/TLS, SASL authentication, ACLs
- [ ] Capacity planning: Disk, network, retention policies
- [ ] Disaster recovery: Backup procedures, cross-datacenter replication
- [ ] Documentation: Runbooks for common failures

---

**Remember**: Kafka is not a message queue—it's a distributed commit log. Once you internalize this mental model, everything else clicks into place.

Now go build something amazing! 🚀
