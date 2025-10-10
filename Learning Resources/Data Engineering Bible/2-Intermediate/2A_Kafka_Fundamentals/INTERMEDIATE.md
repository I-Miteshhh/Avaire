# Week 5: Kafka & Distributed Messaging — INTERMEDIATE Track

*"The log is the unifying abstraction for distributed data systems."* — Jay Kreps

---

## 🎯 Learning Outcomes

Building on the fundamentals, you will master:

- **Multi-broker cluster architecture**: Controller election, partition reassignment, cluster expansion
- **ISR protocol internals**: High-water marks, leader epoch, log reconciliation after failures
- **Schema Registry deep dive**: Avro schemas, compatibility types, schema evolution strategies
- **Kafka Connect framework**: Source/sink connectors, distributed mode, exactly-once delivery
- **Producer idempotence internals**: Producer ID generation, sequence tracking, duplicate detection
- **Consumer group coordination**: Group coordinator, rebalance protocols (EAGER, COOPERATIVE, STATIC)
- **Log compaction mechanics**: Tombstones, cleaner threads, min.cleanable.dirty.ratio tuning
- **Monitoring and observability**: JMX metrics, Burrow lag monitoring, end-to-end latency tracking
- **Multi-datacenter replication**: MirrorMaker 2, active-active setups, conflict resolution
- **Security hardening**: SSL/TLS, SASL authentication (PLAIN, SCRAM, GSSAPI), ACLs, encryption at rest

---

## 📚 Prerequisites Check

Before diving into intermediate concepts, ensure you understand:

- ✅ Commit log abstraction and why it beats queues
- ✅ Partition leadership and follower replication
- ✅ Producer acks modes (0, 1, all)
- ✅ Consumer offset management and commit strategies
- ✅ Delivery semantics (at-most-once, at-least-once, exactly-once)
- ✅ Basic Docker setup and topic creation

If any of these are unclear, review the BEGINNER track first.

---

## 🏗️ Multi-Broker Cluster Architecture: Complete Internals

Let's understand how a Kafka cluster actually operates under the hood.

### The Controller: Kafka's Brain

In every Kafka cluster, **exactly one broker** is elected as the **controller**. This is the most important broker in the cluster.

```
┌────────────────────────────────────────────────────────────┐
│                    Kafka Cluster                           │
│                                                            │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────┐ │
│  │  Broker 1      │  │  Broker 2      │  │  Broker 3   │ │
│  │  (Controller)  │  │                │  │             │ │
│  │  👑            │  │                │  │             │ │
│  └────────────────┘  └────────────────┘  └─────────────┘ │
│         ▲                    ▲                  ▲          │
│         │                    │                  │          │
│         └────────────────────┴──────────────────┘          │
│                              │                             │
│                    ┌─────────┴──────────┐                 │
│                    │    ZooKeeper       │                 │
│                    │  /controller       │                 │
│                    │  /brokers          │                 │
│                    │  /topics           │                 │
│                    └────────────────────┘                 │
└────────────────────────────────────────────────────────────┘

Controller Responsibilities:
1. Partition leader election
2. Topic creation/deletion
3. Partition reassignment
4. Replica management
5. Broker failure detection
6. ISR set updates
```

#### Controller Election Process (Deep Dive)

```
Cluster Startup:
────────────────────────────────────────────────────────────

T0: All brokers start, connect to ZooKeeper
    ├─ Broker 1: "I'm alive!" → Creates /brokers/ids/1
    ├─ Broker 2: "I'm alive!" → Creates /brokers/ids/2
    └─ Broker 3: "I'm alive!" → Creates /brokers/ids/3

T1: Brokers race to become controller
    ├─ Broker 1: Tries to create /controller (ephemeral node)
    │   └─ SUCCESS! Broker 1 is now controller
    ├─ Broker 2: Tries to create /controller
    │   └─ FAIL: Node already exists
    └─ Broker 3: Tries to create /controller
        └─ FAIL: Node already exists

T2: All brokers watch /controller for changes
    └─ If controller dies, /controller node deleted (ephemeral!)
    └─ Triggers new election

Controller Failure:
────────────────────────────────────────────────────────────

T0: Broker 1 (controller) crashes
    └─ ZooKeeper detects session timeout (6 seconds)
    └─ Deletes /controller node

T1: All brokers receive ZooKeeper notification
    └─ "Controller node deleted!"

T2: Brokers race to become new controller
    ├─ Broker 2: Tries to create /controller
    │   └─ SUCCESS! Broker 2 is new controller
    └─ Broker 3: Tries to create /controller
        └─ FAIL: Node already exists

T3: New controller (Broker 2) initializes
    ├─ Loads cluster metadata from ZooKeeper
    ├─ Determines partition leadership states
    ├─ Sends LeaderAndIsr requests to all brokers
    └─ Cluster operational again

Downtime: 5-10 seconds (session timeout + initialization)
```

**Why Controller Elections Are Expensive:**

```python
# What controller does during initialization:
def on_controller_election():
    # 1. Load all topic metadata from ZooKeeper
    topics = zk.get_children("/brokers/topics")  # Could be 10,000+ topics!
    
    # 2. For each topic, load partition info
    for topic in topics:
        partitions = zk.get_children(f"/brokers/topics/{topic}/partitions")
        for partition in partitions:
            state = zk.get(f"/brokers/topics/{topic}/partitions/{partition}/state")
            # Load leader, ISR, controller epoch, etc.
    
    # 3. Load all broker states
    brokers = zk.get_children("/brokers/ids")
    
    # 4. Rebuild in-memory state
    rebuild_partition_state_machine()
    rebuild_replica_state_machine()
    
    # 5. Send metadata to all brokers
    for broker in brokers:
        send_update_metadata_request(broker)
    
    # With 10K topics × 10 partitions × 3 replicas = 300K ZK reads!
    # Can take 30-60 seconds in large clusters
```

**KRaft Mode (Kafka 3.0+): The Future Without ZooKeeper**

```
Old Architecture (ZooKeeper):
┌──────────────────────────────────────────────┐
│  Kafka Cluster                               │
│  ├─ Broker 1                                 │
│  ├─ Broker 2                                 │
│  └─ Broker 3                                 │
│         ▲                                    │
│         │ (reads metadata on every request!) │
│         ▼                                    │
│  ┌────────────────┐                         │
│  │   ZooKeeper    │ ← Single point of       │
│  │   (3 nodes)    │   contention!           │
│  └────────────────┘                         │
└──────────────────────────────────────────────┘

New Architecture (KRaft):
┌──────────────────────────────────────────────┐
│  Kafka Cluster (with built-in consensus)     │
│  ├─ Broker 1 (Controller + Data)            │
│  ├─ Broker 2 (Controller + Data)            │
│  ├─ Broker 3 (Controller + Data)            │
│  │                                           │
│  │  Controllers use Raft consensus          │
│  │  Metadata stored in Kafka itself!        │
│  │  (__cluster_metadata topic)              │
│  │                                           │
│  └─ No external dependency!                 │
└──────────────────────────────────────────────┘

Benefits:
✓ Faster controller failover (1-2 seconds vs 5-10 seconds)
✓ Better scalability (millions of partitions)
✓ Simpler operations (one system instead of two)
✓ Lower latency metadata reads (local cache vs ZK round-trip)
```

---

### Partition Reassignment: Moving Data Without Downtime

**Scenario**: You add new brokers to the cluster. How do you rebalance partitions?

#### Manual Reassignment Process

```bash
# Step 1: Generate reassignment plan
# List topics to rebalance
cat > topics-to-move.json <<EOF
{
  "topics": [
    {"topic": "orders"}
  ],
  "version": 1
}
EOF

# Generate plan (distributes across all brokers)
kafka-reassign-partitions.sh \
  --bootstrap-server localhost:9092 \
  --topics-to-move-json-file topics-to-move.json \
  --broker-list "1,2,3,4,5" \
  --generate

# Output:
# Current partition replica assignment:
# {"version":1,"partitions":[
#   {"topic":"orders","partition":0,"replicas":[1,2,3]},
#   {"topic":"orders","partition":1,"replicas":[1,2,3]},
#   ...
# ]}
#
# Proposed partition reassignment configuration:
# {"version":1,"partitions":[
#   {"topic":"orders","partition":0,"replicas":[1,4,5]},  ← Moved to new brokers!
#   {"topic":"orders","partition":1,"replicas":[2,3,4]},
#   ...
# ]}

# Step 2: Execute reassignment
kafka-reassign-partitions.sh \
  --bootstrap-server localhost:9092 \
  --reassignment-json-file reassignment.json \
  --execute

# Step 3: Monitor progress
kafka-reassign-partitions.sh \
  --bootstrap-server localhost:9092 \
  --reassignment-json-file reassignment.json \
  --verify

# Output:
# Reassignment of partition orders-0 is still in progress
# Reassignment of partition orders-1 completed successfully
```

#### What Happens During Reassignment (Under the Hood)

```
Initial State:
┌─────────────────────────────────────────────────────────┐
│ Partition orders-0                                      │
│ Leader: Broker 1                                        │
│ ISR: [Broker 1, Broker 2, Broker 3]                    │
│ Replicas: [Broker 1, Broker 2, Broker 3]               │
└─────────────────────────────────────────────────────────┘

Target State:
┌─────────────────────────────────────────────────────────┐
│ Partition orders-0                                      │
│ Leader: Broker 1                                        │
│ ISR: [Broker 1, Broker 4, Broker 5]                    │
│ Replicas: [Broker 1, Broker 4, Broker 5]               │
└─────────────────────────────────────────────────────────┘

Reassignment Steps:
────────────────────────────────────────────────────────

T0: Controller receives reassignment command
    └─ Target replicas: [1, 4, 5]
    └─ Current replicas: [1, 2, 3]

T1: Controller adds new replicas (expansion phase)
    ├─ Replicas: [1, 2, 3, 4, 5] ← Temporarily 5 replicas!
    ├─ ISR: [1, 2, 3] (new replicas not in ISR yet)
    └─ Broker 4 and 5 start fetching data from leader

T2: New replicas catch up
    ├─ Broker 4: Offset 0 → 10000 → 50000 → 100000 (caught up!)
    ├─ Broker 5: Offset 0 → 10000 → 50000 → 100000 (caught up!)
    └─ ISR: [1, 2, 3, 4, 5] ← All replicas in sync

T3: Controller removes old replicas (contraction phase)
    ├─ Replicas: [1, 4, 5] ← Target achieved!
    ├─ ISR: [1, 4, 5]
    └─ Broker 2 and 3 delete partition data

T4: Reassignment complete
    └─ Partition now on new brokers, no data loss!

Impact During Reassignment:
✓ Producers/consumers: No downtime (leader unchanged)
✓ Disk I/O: High (replication traffic)
✓ Network: High (data transfer to new replicas)
✓ Cluster capacity: Reduced (extra replicas consuming disk)

Throttling (to avoid overwhelming cluster):
kafka-reassign-partitions.sh \
  --throttle 100000000 \  # 100 MB/sec
  --execute
```

---

## 🔍 ISR Protocol Internals: High-Water Marks and Leader Epochs

The ISR protocol is the heart of Kafka's durability guarantees. Let's understand it completely.

### High-Water Mark (HWM) vs Log End Offset (LEO)

```
Partition 0 on Leader (Broker 1):
Position:  0     1     2     3     4     5     6     7     8
           ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
Messages:  │ M0  │ M1  │ M2  │ M3  │ M4  │ M5  │ M6  │ M7  │ M8  │
           └─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
                                       ▲                       ▲
                                       │                       │
                                      HWM=4                  LEO=8
                                  (committed)           (uncommitted)

Follower 1 (Broker 2):
Position:  0     1     2     3     4     5     6
           ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┐
Messages:  │ M0  │ M1  │ M2  │ M3  │ M4  │ M5  │ M6  │
           └─────┴─────┴─────┴─────┴─────┴─────┴─────┘
                                                   ▲
                                                   │
                                                 LEO=6

Follower 2 (Broker 3):
Position:  0     1     2     3     4
           ┌─────┬─────┬─────┬─────┬─────┐
Messages:  │ M0  │ M1  │ M2  │ M3  │ M4  │
           └─────┴─────┴─────┴─────┴─────┘
                                       ▲
                                       │
                                     LEO=4

Definitions:
────────────────────────────────────────────────────────
LEO (Log End Offset): Position of NEXT message to append
HWM (High-Water Mark): Min LEO of all ISR replicas

Calculation:
ISR = {Leader, Follower 1, Follower 2}
LEOs = {Leader: 8, Follower 1: 6, Follower 2: 4}
HWM = min(8, 6, 4) = 4

Consumer Visibility:
- Consumers can read offsets 0-3 (< HWM) ✓
- Consumers CANNOT read offsets 4-7 (>= HWM) ✗
- Why? Not yet replicated to all ISR → not durable!
```

**Why HWM Matters: Preventing Data Loss**

```
Scenario: Leader crashes before followers catch up

T0: Leader has [M0, M1, M2, M3, M4, M5]
    Follower 1 has [M0, M1, M2, M3]
    Follower 2 has [M0, M1, M2, M3]
    HWM = 3

T1: Leader crashes!

T2: Follower 1 elected as new leader
    Follower 1 only has [M0, M1, M2, M3]
    Messages M4, M5 lost from old leader

T3: Consumer reads from new leader
    Consumer sees offsets 0-3 only
    But consumer already read up to offset 3 (HWM)!
    
Result: ✓ No data inconsistency!
        ✓ Consumer never sees M4, M5 (they were uncommitted)
        ✗ Data loss (M4, M5 vanished)

This is why acks=all is critical:
- With acks=all, M4, M5 wouldn't have been ACKed to producer
- Producer would retry after leader election
- No data loss!
```

---

### Leader Epoch: Solving the High-Water Mark Truncation Problem

**The Problem with HWM Alone:**

```
Scenario: Split-brain during leader election

T0: Initial state
    Leader (Broker 1): [M0, M1, M2, M3], HWM=3, LEO=4
    Follower (Broker 2): [M0, M1, M2], HWM=2, LEO=3
    ISR: {Broker 1, Broker 2}

T1: Broker 2 goes offline (network partition)
    Leader (Broker 1): [M0, M1, M2, M3, M4, M5], HWM=5, LEO=6
    Follower (Broker 2): OFFLINE
    ISR: {Broker 1} ← Broker 2 removed from ISR!

T2: Broker 1 crashes, Broker 2 comes back online
    Broker 2 elected as new leader (only survivor!)
    Broker 2: [M0, M1, M2], HWM=2, LEO=3

T3: Broker 1 recovers
    Broker 1 has: [M0, M1, M2, M3, M4, M5]
    Broker 2 (leader) has: [M0, M1, M2]
    
    Old behavior (HWM only):
    ├─ Broker 1 truncates to Broker 2's HWM=2
    ├─ Broker 1: [M0, M1, M2] ← Lost M3, M4, M5!
    └─ Messages lost even though they were in ISR!

Problem: HWM isn't enough to determine safe truncation point!
```

**Solution: Leader Epoch**

```
Leader Epoch = (Epoch Number, Start Offset)

Example Evolution:
┌────────────────────────────────────────────────────┐
│ Epoch 0: Broker 1 became leader at offset 0       │
│ Epoch 1: Broker 2 became leader at offset 100     │
│ Epoch 2: Broker 1 became leader at offset 200     │
│ Epoch 3: Broker 3 became leader at offset 350     │
└────────────────────────────────────────────────────┘

Each replica maintains leader epoch history:
{
  "epochs": [
    {"epoch": 0, "startOffset": 0},
    {"epoch": 1, "startOffset": 100},
    {"epoch": 2, "startOffset": 200},
    {"epoch": 3, "startOffset": 350}
  ]
}

Truncation with Leader Epoch:
────────────────────────────────────────────────────

T0: Broker 1 (old leader) recovers
    Broker 1 last epoch: Epoch 2
    Broker 1 messages: [M0...M350] (from Epoch 2)

T1: Broker 1 asks current leader (Broker 3): 
    "What offset did Epoch 2 end at?"

T2: Broker 3 responds:
    "Epoch 2 ended at offset 350"
    "Epoch 3 started at offset 350"

T3: Broker 1 truncates to offset 350
    ✓ Safe truncation point
    ✓ No data loss from committed messages
    ✓ Only uncommitted messages from failed leader removed

Benefits:
✓ Prevents incorrect truncation
✓ Enables safe recovery after split-brain
✓ Guarantees: If message was in ISR when ACKed, it survives leader changes
```

---

## 📋 Schema Registry: Enforcing Data Contracts

Schema Registry is critical for production Kafka deployments. It ensures data quality and enables schema evolution.

### Why Schema Registry Exists

**The Problem:**

```python
# Day 1: Producer sends
{"user_id": 123, "amount": 99.99}

# Day 30: New producer version sends
{"user_id": 123, "amount": 99.99, "currency": "USD"}

# Day 60: Another producer sends
{"userId": 123, "total": 99.99}  # Different field names!

# Consumer nightmare:
def process_message(msg):
    user_id = msg.get("user_id") or msg.get("userId")  # ugh!
    amount = msg.get("amount") or msg.get("total")  # ugh!
    currency = msg.get("currency", "USD")  # hope this is right!
```

**Solution: Centralized Schema Management**

```
┌──────────────────────────────────────────────────────────┐
│                   Schema Registry                        │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Schemas (versioned)                                │ │
│  │  ├─ orders-value schema v1                         │ │
│  │  ├─ orders-value schema v2 (added currency field)  │ │
│  │  └─ orders-value schema v3 (added timestamp)       │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
         ▲                                    ▲
         │                                    │
         │ Register schema                   │ Fetch schema
         │                                    │
    ┌────┴─────┐                        ┌────┴─────┐
    │ Producer │                        │ Consumer │
    └──────────┘                        └──────────┘
         │                                    ▲
         │    Kafka Topic: orders             │
         └────────────────────────────────────┘
              [Schema ID: 1][Data bytes]
```

### Avro: The Standard Schema Format

**Why Avro?**

1. **Compact**: Binary encoding (50% smaller than JSON)
2. **Fast**: No parsing overhead (direct binary read)
3. **Schema evolution**: Built-in compatibility rules
4. **Self-describing**: Schema embedded in file

**Avro Schema Example:**

```json
{
  "type": "record",
  "name": "Order",
  "namespace": "com.company.orders",
  "fields": [
    {
      "name": "order_id",
      "type": "string",
      "doc": "Unique order identifier"
    },
    {
      "name": "user_id",
      "type": "long",
      "doc": "User who placed the order"
    },
    {
      "name": "amount",
      "type": "double",
      "doc": "Order total amount"
    },
    {
      "name": "currency",
      "type": "string",
      "default": "USD",
      "doc": "Currency code (ISO 4217)"
    },
    {
      "name": "timestamp",
      "type": "long",
      "logicalType": "timestamp-millis",
      "doc": "Order creation time (Unix timestamp)"
    },
    {
      "name": "items",
      "type": {
        "type": "array",
        "items": {
          "type": "record",
          "name": "OrderItem",
          "fields": [
            {"name": "sku", "type": "string"},
            {"name": "quantity", "type": "int"},
            {"name": "price", "type": "double"}
          ]
        }
      }
    }
  ]
}
```

### Schema Evolution: Forward, Backward, and Full Compatibility

```
┌────────────────────────────────────────────────────────────┐
│ Compatibility Types                                        │
└────────────────────────────────────────────────────────────┘

1. BACKWARD (default):
   New schema can read old data
   
   Example:
   v1: {user_id, amount}
   v2: {user_id, amount, currency="USD"}  ← Added field with default
   
   ✓ Consumer with v2 schema can read v1 data (uses default for currency)
   ✗ Consumer with v1 schema CANNOT read v2 data (missing currency field)
   
   Use case: Upgrade consumers first, then producers

2. FORWARD:
   Old schema can read new data
   
   Example:
   v1: {user_id, amount, currency}
   v2: {user_id, amount}  ← Removed currency field
   
   ✓ Consumer with v1 schema can read v2 data (ignores missing currency)
   ✗ Consumer with v2 schema CANNOT read v1 data (unexpected currency field)
   
   Use case: Upgrade producers first, then consumers

3. FULL:
   New schema can read old data AND old schema can read new data
   
   Example:
   v1: {user_id, amount}
   v2: {user_id, amount, currency="USD"}  ← Added optional field with default
   
   ✓ Consumer v2 reads v1 data (uses default)
   ✓ Consumer v1 reads v2 data (ignores new field)
   
   Use case: No coordination needed, safest option

4. NONE:
   No compatibility checks
   
   Use case: Development environments only!
```

**Schema Evolution Rules:**

```
Backward Compatible Changes:
✓ Add field with default value
✓ Remove field

Forward Compatible Changes:
✓ Add field
✓ Remove field with default value

Full Compatible Changes:
✓ Add field with default value
✓ Remove field with default value

Breaking Changes (NEVER do these!):
✗ Rename field
✗ Change field type
✗ Add required field (no default)
✗ Remove required field (no default)
```

### Production Implementation with Confluent Schema Registry

```python
from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
import json

# Avro schema (usually loaded from file)
order_schema_str = """
{
  "type": "record",
  "name": "Order",
  "namespace": "com.company.orders",
  "fields": [
    {"name": "order_id", "type": "string"},
    {"name": "user_id", "type": "long"},
    {"name": "amount", "type": "double"},
    {"name": "currency", "type": "string", "default": "USD"}
  ]
}
"""

class Order:
    """Order object matching Avro schema."""
    def __init__(self, order_id, user_id, amount, currency="USD"):
        self.order_id = order_id
        self.user_id = user_id
        self.amount = amount
        self.currency = currency

def order_to_dict(order, ctx):
    """Convert Order object to dict for Avro serialization."""
    return {
        "order_id": order.order_id,
        "user_id": order.user_id,
        "amount": order.amount,
        "currency": order.currency
    }

# Initialize Schema Registry client
schema_registry_conf = {'url': 'http://localhost:8081'}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

# Create Avro serializer
avro_serializer = AvroSerializer(
    schema_registry_client,
    order_schema_str,
    order_to_dict
)

# Producer configuration
producer_conf = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'order-producer'
}

producer = Producer(producer_conf)

# Produce message with schema
order = Order(
    order_id="ORD-2025-001",
    user_id=12345,
    amount=99.99,
    currency="USD"
)

producer.produce(
    topic='orders',
    key=str(order.user_id),
    value=avro_serializer(
        order,
        SerializationContext('orders', MessageField.VALUE)
    ),
    on_delivery=lambda err, msg: print(f"Delivered: {msg.topic()} [{msg.partition()}]")
)

producer.flush()
```

**What Happens Under the Hood:**

```
Producer Flow:
──────────────────────────────────────────────────────────

1. Producer calls avro_serializer(order)

2. Serializer checks cache for schema ID
   ├─ Cache miss → Register schema with Schema Registry
   │   └─ POST /subjects/orders-value/versions
   │       Body: {"schema": "<avro_schema>"}
   │       Response: {"id": 1}
   ├─ Cache hit → Use cached schema ID
   └─ Store: schema_id = 1

3. Serialize object to Avro binary
   order = {"order_id": "ORD-2025-001", "user_id": 12345, ...}
   ↓
   binary_data = [0x4F, 0x52, 0x44, 0x2D, ...]  # Avro binary

4. Prepend magic byte and schema ID (5 bytes)
   message = [0x00] + [0x00, 0x00, 0x00, 0x01] + binary_data
              ▲         ▲──────────┬──────────▲
              │                    │
         Magic byte           Schema ID=1

5. Send to Kafka
   Topic: orders
   Value: [0x00, 0x00, 0x00, 0x00, 0x01, 0x4F, 0x52, 0x44, ...]

Consumer Flow:
──────────────────────────────────────────────────────────

1. Consumer receives message from Kafka
   message = [0x00, 0x00, 0x00, 0x00, 0x01, 0x4F, 0x52, 0x44, ...]

2. Deserializer parses magic byte and schema ID
   magic_byte = 0x00
   schema_id = 1
   binary_data = [0x4F, 0x52, 0x44, ...]

3. Fetch schema from registry (with caching)
   GET /schemas/ids/1
   Response: {"schema": "<avro_schema>"}

4. Deserialize binary data using schema
   binary_data + schema → Order object
   
5. Return to application
   order = Order(order_id="ORD-2025-001", user_id=12345, ...)
```

---

## 🔌 Kafka Connect: Data Integration at Scale

Kafka Connect is a framework for streaming data between Kafka and external systems (databases, files, APIs, etc.) without writing code.

### Connect Architecture

```
┌──────────────────────────────────────────────────────────┐
│                  Kafka Connect Cluster                   │
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │  Worker 1  │  │  Worker 2  │  │  Worker 3  │        │
│  │            │  │            │  │            │        │
│  │ ┌────────┐ │  │ ┌────────┐ │  │ ┌────────┐ │        │
│  │ │Task 1.1│ │  │ │Task 1.2│ │  │ │Task 2.1│ │        │
│  │ └────────┘ │  │ └────────┘ │  │ └────────┘ │        │
│  │ ┌────────┐ │  │ ┌────────┐ │  │            │        │
│  │ │Task 2.2│ │  │ │Task 3.1│ │  │            │        │
│  │ └────────┘ │  │ └────────┘ │  │            │        │
│  └────────────┘  └────────────┘  └────────────┘        │
│         │               │               │               │
│         └───────────────┴───────────────┘               │
│                         │                               │
│               ┌─────────┴─────────┐                    │
│               │  Kafka (Config &  │                    │
│               │   Offset Storage) │                    │
│               └───────────────────┘                    │
└──────────────────────────────────────────────────────────┘
         ▲                                    │
         │                                    ▼
    ┌────┴────┐                          ┌────┴────┐
    │ Source  │                          │  Sink   │
    │ (MySQL) │                          │ (S3)    │
    └─────────┘                          └─────────┘
```

### Source Connector Example: MySQL CDC

```json
{
  "name": "mysql-source-connector",
  "config": {
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "tasks.max": "3",
    
    "database.hostname": "mysql.example.com",
    "database.port": "3306",
    "database.user": "debezium",
    "database.password": "secret",
    "database.server.id": "184054",
    "database.server.name": "mysql-prod",
    
    "database.whitelist": "ecommerce",
    "table.whitelist": "ecommerce.orders,ecommerce.users",
    
    "database.history.kafka.bootstrap.servers": "localhost:9092",
    "database.history.kafka.topic": "schema-changes.mysql",
    
    "transforms": "unwrap",
    "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "transforms.unwrap.drop.tombstones": "false",
    
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable": "true",
    "value.converter.schemas.enable": "true"
  }
}
```

**What This Connector Does:**

```
MySQL binlog events → Kafka topics (one topic per table)

Example flow:
──────────────────────────────────────────────────────────

T0: INSERT INTO orders (id, user_id, amount) VALUES (1, 123, 99.99)

T1: MySQL writes to binlog
    Event: INSERT, table=orders, row={id=1, user_id=123, amount=99.99}

T2: Debezium connector reads binlog
    ├─ Parses event
    ├─ Transforms to Kafka message
    └─ Produces to topic: mysql-prod.ecommerce.orders

T3: Message in Kafka:
    Key: {"id": 1}
    Value: {
      "before": null,
      "after": {"id": 1, "user_id": 123, "amount": 99.99},
      "op": "c",  ← CREATE
      "ts_ms": 1728646200000
    }

T4: UPDATE orders SET amount = 149.99 WHERE id = 1

T5: Debezium produces:
    Key: {"id": 1}
    Value: {
      "before": {"id": 1, "user_id": 123, "amount": 99.99},
      "after": {"id": 1, "user_id": 123, "amount": 149.99},
      "op": "u",  ← UPDATE
      "ts_ms": 1728646250000
    }

T6: DELETE FROM orders WHERE id = 1

T7: Debezium produces:
    Key: {"id": 1}
    Value: {
      "before": {"id": 1, "user_id": 123, "amount": 149.99},
      "after": null,
      "op": "d",  ← DELETE
      "ts_ms": 1728646300000
    }
    
    PLUS tombstone message:
    Key: {"id": 1}
    Value: null  ← Tombstone (for log compaction)
```

### Sink Connector Example: S3 Export

```json
{
  "name": "s3-sink-connector",
  "config": {
    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
    "tasks.max": "3",
    
    "topics": "orders,users,products",
    
    "s3.region": "us-east-1",
    "s3.bucket.name": "my-data-lake",
    "s3.part.size": "5242880",
    
    "flush.size": "10000",
    "rotate.interval.ms": "3600000",
    "rotate.schedule.interval.ms": "3600000",
    
    "format.class": "io.confluent.connect.s3.format.parquet.ParquetFormat",
    "parquet.codec": "snappy",
    
    "partitioner.class": "io.confluent.connect.storage.partitioner.TimeBasedPartitioner",
    "path.format": "'year'=YYYY/'month'=MM/'day'=dd/'hour'=HH",
    "partition.duration.ms": "3600000",
    "timestamp.extractor": "Record",
    
    "schema.compatibility": "NONE",
    "schema.generator.class": "io.confluent.connect.storage.hive.schema.DefaultSchemaGenerator",
    
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "value.converter": "io.confluent.connect.avro.AvroConverter",
    "value.converter.schema.registry.url": "http://localhost:8081"
  }
}
```

**S3 Output Structure:**

```
s3://my-data-lake/
├─ topics/
│  ├─ orders/
│  │  ├─ year=2025/
│  │  │  ├─ month=10/
│  │  │  │  ├─ day=11/
│  │  │  │  │  ├─ hour=10/
│  │  │  │  │  │  ├─ orders+0+0000000000.snappy.parquet
│  │  │  │  │  │  ├─ orders+0+0000010000.snappy.parquet
│  │  │  │  │  │  ├─ orders+1+0000000000.snappy.parquet
│  │  │  │  │  │  └─ orders+2+0000000000.snappy.parquet
│  │  │  │  │  └─ hour=11/
│  │  │  │  └─ day=12/
│  │  │  └─ month=11/
│  │  └─ year=2026/
│  ├─ users/
│  └─ products/
```

---

This continues with more sections (log compaction, monitoring, multi-DC replication, security). Should I continue expanding INTERMEDIATE.md or move to creating EXPERT.md and WHITEPAPERS.md?

