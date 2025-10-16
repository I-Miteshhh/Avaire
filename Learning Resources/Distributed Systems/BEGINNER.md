# Distributed Systems - BEGINNER

**Learning Time:** 2-3 weeks  
**Prerequisite Knowledge:** Basic networking, operating systems, algorithms  
**Difficulty:** Fundamental → Building blocks of all distributed systems

---

## 📚 Table of Contents

1. [What is a Distributed System?](#what-is-a-distributed-system)
2. [Why Distributed Systems?](#why-distributed-systems)
3. [The 8 Fallacies of Distributed Computing](#the-8-fallacies-of-distributed-computing)
4. [Network Models](#network-models)
5. [Time, Clocks, and Ordering](#time-clocks-and-ordering)
6. [Communication Patterns](#communication-patterns)
7. [Failure Models](#failure-models)
8. [Basic Coordination Primitives](#basic-coordination-primitives)
9. [Hands-On Examples](#hands-on-examples)

---

## 1. What is a Distributed System?

### Definition

> **Distributed System:** A collection of independent computers that appear to users as a single coherent system.
> — Andrew Tanenbaum

**Key Characteristics:**
1. **Multiple autonomous nodes:** Each computer (node) operates independently
2. **Network communication:** Nodes communicate via message passing over a network
3. **Shared state:** Nodes coordinate to maintain shared state or perform common tasks
4. **Single system illusion:** Users see one unified system, not individual machines

### Examples of Distributed Systems

```
┌─────────────────────────────────────────────────────────┐
│ Everyday Distributed Systems                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 1. Google Search:                                       │
│    ├─ 15+ data centers worldwide                       │
│    ├─ Millions of servers                              │
│    └─ User sees: Single search box, instant results    │
│                                                         │
│ 2. Netflix:                                             │
│    ├─ AWS cloud infrastructure (1000+ microservices)   │
│    ├─ CDN for video streaming                          │
│    └─ User sees: One streaming platform                │
│                                                         │
│ 3. WhatsApp:                                            │
│    ├─ 2 billion users across 50+ servers               │
│    ├─ Real-time message delivery                       │
│    └─ User sees: Chat app that "just works"            │
│                                                         │
│ 4. Your Bank:                                           │
│    ├─ ATMs, branches, mobile app                       │
│    ├─ Core banking system (distributed database)       │
│    └─ User sees: Single account balance                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Why Distributed Systems?

### Motivations

#### 1. **Scalability** - Handle More Load

```
Vertical Scaling (Single Machine):
┌──────────────────┐
│  Limits:         │
│  ├─ CPU cores    │  Max: ~192 cores
│  ├─ RAM          │  Max: ~24 TB
│  ├─ Disk         │  Max: ~100 TB SSD
│  └─ Cost         │  Exponential growth
└──────────────────┘

Horizontal Scaling (Distributed):
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  Node 1          │  │  Node 2          │  │  Node N          │
│  8 cores, 64 GB  │  │  8 cores, 64 GB  │  │  8 cores, 64 GB  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
     Linear cost          Add more as needed
```

**Example:** Facebook handles 3 billion users by distributing across thousands of servers, not one giant supercomputer.

#### 2. **Availability** - Stay Online Despite Failures

```
Single Server:
├─ Uptime: 99.9% = 8.76 hours downtime/year
└─ Single point of failure ❌

Distributed (3 replicas):
├─ Uptime: 99.999% = 5.26 minutes downtime/year
└─ Redundancy: If 1 node fails, 2 still serve traffic ✅
```

**Example:** Amazon requires 99.99% availability (52 minutes downtime/year max). Impossible with single server.

#### 3. **Fault Tolerance** - Survive Hardware Failures

```
Hardware Failure Rates (Google's Data):
├─ Hard drives: 2-4% fail per year
├─ Memory errors: 1 per 1-2 days per server
└─ Network issues: Daily in large data centers

Solution: Replicate data across multiple machines
├─ 1 copy: If disk fails → Data lost ❌
└─ 3 copies: Need 3 simultaneous failures → 0.0001% chance ✅
```

**Example:** HDFS stores 3 copies of every file block across different servers/racks.

#### 4. **Geographic Distribution** - Low Latency Worldwide

```
User in Tokyo → Server in California
├─ Latency: ~150 ms (round-trip across Pacific)
└─ Poor user experience ❌

User in Tokyo → Server in Tokyo
├─ Latency: ~5 ms (local data center)
└─ Great user experience ✅

Solution: Distribute servers globally (CDN, multi-region databases)
```

**Example:** Netflix has servers in 100+ countries to stream videos with low latency.

---

## 3. The 8 Fallacies of Distributed Computing

**Origin:** Peter Deutsch & James Gosling (Sun Microsystems, 1994)

These are **false assumptions** beginners make about networks. Violating them causes production outages.

### Fallacy 1: "The Network is Reliable"

```python
# ❌ WRONG: Assume network always works
def transfer_money(from_account, to_account, amount):
    deduct(from_account, amount)
    add(to_account, amount)  # What if network fails HERE?
    # Money deducted but not added → Lost money!

# ✅ CORRECT: Use distributed transactions (2-phase commit)
def transfer_money_safe(from_account, to_account, amount):
    transaction = start_transaction()
    try:
        transaction.deduct(from_account, amount)
        transaction.add(to_account, amount)
        transaction.commit()  # Atomic: All or nothing
    except NetworkError:
        transaction.rollback()  # Undo all changes
```

**Reality:** Networks drop packets (0.1%-1%), cables get unplugged, switches crash.

**Fix:** Retries, timeouts, acknowledgements, idempotency.

### Fallacy 2: "Latency is Zero"

```
Local function call:  <1 microsecond
Network RPC call:     1-100 milliseconds

100,000x slower!
```

**Example:**
```python
# ❌ WRONG: Make 1000 network calls in loop
total = 0
for user_id in user_ids:  # 1000 users
    balance = get_balance_from_db(user_id)  # 10ms per call
    total += balance
# Total time: 1000 × 10ms = 10 seconds ❌

# ✅ CORRECT: Batch requests
balances = get_balances_batch(user_ids)  # 1 call, 50ms
total = sum(balances)
# Total time: 50ms ✅ (200x faster)
```

**Fix:** Batching, caching, asynchronous calls.

### Fallacy 3: "Bandwidth is Infinite"

```
Sending 1 GB of data:
├─ 100 Mbps LAN: 80 seconds
├─ 1 Gbps LAN:   8 seconds
└─ WAN (cross-region): 5+ minutes

Bandwidth costs money: AWS charges $0.09/GB for data transfer
```

**Example:** Sending raw images (10 MB each) instead of compressed (1 MB) = 10x higher bandwidth cost.

**Fix:** Compression, send only deltas, design for data locality.

### Fallacy 4: "The Network is Secure"

```
Attacks:
├─ Man-in-the-middle: Attacker intercepts packets
├─ Packet sniffing: Read sensitive data on wire
└─ DDoS: Flood network with traffic

2023 stat: 30,000+ data breaches, $4.5M average cost
```

**Fix:** Encryption (TLS), authentication (mTLS), firewalls, VPCs.

### Fallacy 5: "Topology Doesn't Change"

```
Reality in cloud environments:
├─ Servers auto-scale (add/remove nodes)
├─ IPs change when instances restart
├─ Load balancers route traffic dynamically
└─ Network partitions happen
```

**Example:** Hardcoding IP addresses breaks when servers restart.

**Fix:** Service discovery (Consul, etcd), DNS, load balancers.

### Fallacy 6: "There is One Administrator"

```
Large systems:
├─ Database team manages Postgres
├─ Network team manages routers
├─ Security team manages firewalls
└─ Application team deploys code

Miscommunication → Outages
```

**Example:** Database team upgrades server, doesn't notify app team → App breaks.

**Fix:** Centralized monitoring, change management, communication protocols.

### Fallacy 7: "Transport Cost is Zero"

```
Costs:
├─ Serialization: Convert object → bytes (CPU)
├─ Deserialization: Convert bytes → object (CPU)
├─ Network: Send data over wire (bandwidth)
└─ Context switching: Handle network I/O (latency)
```

**Example:** Sending 1 million small messages (1 KB each) has more overhead than sending 1 large message (1 GB).

**Fix:** Batching, efficient serialization (Protobuf vs JSON), connection pooling.

### Fallacy 8: "The Network is Homogeneous"

```
Reality:
├─ Different operating systems (Linux, Windows)
├─ Different programming languages (Java, Python, Go)
├─ Different protocols (HTTP, gRPC, AMQP)
└─ Different byte orders (big-endian vs little-endian)
```

**Fix:** Standard protocols (HTTP/2, gRPC), platform-agnostic formats (JSON, Protobuf).

---

## 4. Network Models

### Synchronous vs Asynchronous Networks

```
┌─────────────────────────────────────────────────────────┐
│ Synchronous Network (Theoretical)                      │
├─────────────────────────────────────────────────────────┤
│ Assumptions:                                            │
│ ├─ Bounded message delay: Max D seconds                │
│ ├─ Bounded processing time: Max P seconds              │
│ └─ Synchronized clocks: All nodes agree on time        │
│                                                         │
│ Example: Phone call (circuit-switched network)         │
│ ├─ Latency: 100-200ms (predictable)                    │
│ └─ Bandwidth: Reserved (guaranteed)                    │
│                                                         │
│ Properties:                                             │
│ ✅ Can detect failures (no response within D+P)        │
│ ✅ Can use timeouts reliably                            │
│ ❌ Doesn't exist in real distributed systems!          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Asynchronous Network (Reality)                         │
├─────────────────────────────────────────────────────────┤
│ Assumptions:                                            │
│ ├─ Unbounded message delay: No max (can be infinite)   │
│ ├─ Unbounded processing time: Node might be slow/stuck │
│ └─ No synchronized clocks: Clock skew exists           │
│                                                         │
│ Example: Internet (packet-switched network)            │
│ ├─ Latency: 1ms to infinity (unpredictable)            │
│ └─ Bandwidth: Shared (congestion possible)             │
│                                                         │
│ Properties:                                             │
│ ❌ Cannot distinguish slow node from crashed node      │
│ ❌ Timeouts are heuristics, not guarantees             │
│ ✅ Models real networks (Internet, data centers)       │
└─────────────────────────────────────────────────────────┘
```

**Practical Implication:**

```python
# Problem: Is the server crashed or just slow?
response = send_request(server, timeout=5)
if response is None:
    # Could be:
    # 1. Server crashed ❌
    # 2. Network is slow 🐢
    # 3. Server is overloaded 🔥
    # 4. Request lost in transit 📉
    # We cannot know for certain!
```

**Solution:** Assume asynchronous model, design for uncertainty (retries, acknowledgements, consensus algorithms).

---

## 5. Time, Clocks, and Ordering

### The Problem: No Global Clock

```
Question: Did event A happen before event B?

Single machine: Easy!
├─ Read system clock: time(A) < time(B) → A happened first ✅

Distributed system: Hard!
├─ Server 1 clock: 10:00:00
├─ Server 2 clock: 09:59:55 (5 seconds behind)
└─ Which clock is "correct"? Neither! ❌
```

**Real-world example:**
```
Server 1 (New York):  User updates profile at 10:00:00
Server 2 (London):    User deletes account at 09:59:58 (clock behind)

Which operation wins?
├─ Wall clock: Delete (09:59:58 < 10:00:00) ❌ WRONG
└─ Causality: Update (happened first logically) ✅ CORRECT
```

### Types of Clocks

#### 1. Physical Clocks (Wall Clock Time)

```python
import time

# Problem: Clock skew
def physical_clock():
    return time.time()  # Seconds since Jan 1, 1970

# Server 1: 1697385600.123
# Server 2: 1697385595.456  (5 seconds behind)
```

**Issues:**
- **Clock skew:** Clocks drift apart (1ms/second typical)
- **Clock synchronization:** NTP can sync within ~1-10ms, but not perfect
- **Leap seconds:** Time can jump backward!

**When to use:** Timeouts, metrics, logging (humans need wall time)

**When NOT to use:** Ordering events, uniqueness (event IDs)

#### 2. Logical Clocks (Lamport Timestamps)

**Goal:** Capture causality, not wall time.

```python
class LamportClock:
    def __init__(self):
        self.time = 0
    
    def increment(self):
        """Called on local event"""
        self.time += 1
        return self.time
    
    def update(self, received_time):
        """Called when receiving message from another node"""
        self.time = max(self.time, received_time) + 1
        return self.time

# Example
node_a = LamportClock()
node_b = LamportClock()

# Node A: Send message
time_a = node_a.increment()  # time_a = 1
send_message(to=node_b, payload="hello", timestamp=time_a)

# Node B: Receive message
time_b = node_b.update(received_time=time_a)  # time_b = max(0, 1) + 1 = 2
print(f"Received message at logical time {time_b}")

# Property: If event A happened before event B, then timestamp(A) < timestamp(B) ✅
```

**Lamport's Happened-Before Relation:**

```
Event A → Event B (A "happened before" B) if:
1. A and B on same node, and A occurred before B in local execution
2. A is sending a message, B is receiving that message
3. Transitivity: If A → C and C → B, then A → B

Examples:
├─ A: Write to database → B: Read from database (same node) → A → B ✅
├─ A: Send email → B: Receive email → A → B ✅
└─ A: User clicks in NYC → B: User clicks in Tokyo (independent) → NOT ordered ❌
```

#### 3. Vector Clocks (Capture Concurrency)

```python
class VectorClock:
    def __init__(self, node_id, num_nodes):
        self.node_id = node_id
        self.clock = [0] * num_nodes  # Vector: [0, 0, 0] for 3 nodes
    
    def increment(self):
        self.clock[self.node_id] += 1
        return self.clock.copy()
    
    def update(self, received_clock):
        for i in range(len(self.clock)):
            self.clock[i] = max(self.clock[i], received_clock[i])
        self.clock[self.node_id] += 1
        return self.clock.copy()
    
    @staticmethod
    def compare(clock_a, clock_b):
        """Compare two vector clocks"""
        if all(a <= b for a, b in zip(clock_a, clock_b)):
            if any(a < b for a, b in zip(clock_a, clock_b)):
                return "A happened before B"
        elif all(a >= b for a, b in zip(clock_a, clock_b)):
            if any(a > b for a, b in zip(clock_a, clock_b)):
                return "B happened before A"
        return "Concurrent (cannot determine order)"

# Example: 3 nodes
node_0 = VectorClock(node_id=0, num_nodes=3)
node_1 = VectorClock(node_id=1, num_nodes=3)
node_2 = VectorClock(node_id=2, num_nodes=3)

# Node 0: Event
clock_a = node_0.increment()  # [1, 0, 0]

# Node 1: Independent event
clock_b = node_1.increment()  # [0, 1, 0]

# Compare
print(VectorClock.compare(clock_a, clock_b))  # "Concurrent"
# Neither [1, 0, 0] ≤ [0, 1, 0] nor [1, 0, 0] ≥ [0, 1, 0]
```

**Use case:** Detect conflicts in distributed databases (Dynamo, Riak).

---

## 6. Communication Patterns

### 1. Request-Response (RPC)

```python
# Client-Server model
class Client:
    def call_remote_function(self, server, function_name, args):
        # 1. Serialize arguments
        request = serialize(function_name, args)
        
        # 2. Send over network
        response = network.send(server, request, timeout=5)
        
        # 3. Deserialize result
        result = deserialize(response)
        return result

# Example: HTTP API call
def get_user(user_id):
    response = requests.get(f"https://api.example.com/users/{user_id}")
    return response.json()
```

**Characteristics:**
- Synchronous (caller waits for response)
- Tight coupling (caller must know server address)
- Easy to understand (like local function call)

**Challenges:**
```python
# What if server is slow?
try:
    result = call_remote_function(server, "compute", args, timeout=5)
except TimeoutError:
    # Retry? Return error? Use cached value?
    pass

# What if call succeeds but response is lost?
# Server executed function, but client thinks it failed!
# Solution: Idempotent operations
```

### 2. Message Passing (Async)

```python
import asyncio
from queue import Queue

class MessageQueue:
    def __init__(self):
        self.queue = Queue()
    
    def send(self, message):
        """Non-blocking: Put message in queue and return immediately"""
        self.queue.put(message)
        print(f"Sent: {message}")
    
    async def receive(self):
        """Process messages asynchronously"""
        while True:
            message = self.queue.get()
            print(f"Processing: {message}")
            await asyncio.sleep(1)  # Simulate work
            self.queue.task_done()

# Example: Kafka, RabbitMQ
producer.send("topic", {"user_id": 123, "action": "click"})
# Producer doesn't wait for consumer to process
```

**Characteristics:**
- Asynchronous (sender doesn't wait)
- Loose coupling (sender doesn't know receivers)
- Scalable (queue buffers messages)

**Use cases:**
- Event-driven architectures
- Microservices communication
- Background jobs (email sending, image processing)

### 3. Publish-Subscribe

```python
class PubSub:
    def __init__(self):
        self.subscribers = {}  # topic → [subscribers]
    
    def subscribe(self, topic, subscriber):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(subscriber)
    
    def publish(self, topic, message):
        for subscriber in self.subscribers.get(topic, []):
            subscriber.on_message(message)

# Example
pubsub = PubSub()
pubsub.subscribe("user.created", email_service)
pubsub.subscribe("user.created", analytics_service)

pubsub.publish("user.created", {"user_id": 123})
# Both email_service and analytics_service receive message
```

**Use cases:** Real-time notifications, event broadcasting, logs aggregation.

---

## 7. Failure Models

### Types of Failures

```
┌─────────────────────────────────────────────────────────┐
│ 1. Crash Failure (Fail-Stop)                           │
├─────────────────────────────────────────────────────────┤
│ Node stops responding completely (power loss, OOM kill) │
│                                                         │
│ ┌──────┐ PING → ┌──────┐                               │
│ │ Node │ ←  X   │ Dead │  (No response)                │
│ └──────┘        └──────┘                               │
│                                                         │
│ Detection: Timeout (but could be network partition!)   │
│ Solution: Heartbeats, failure detectors                │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 2. Omission Failure                                     │
├─────────────────────────────────────────────────────────┤
│ Node drops some messages (network congestion, buffer    │
│ overflow)                                               │
│                                                         │
│ ┌──────┐  MSG1 → ✅  ┌──────┐                          │
│ │ Node │  MSG2 → ❌  │ Node │  (Lost)                  │
│ │   A  │  MSG3 → ✅  │   B  │                          │
│ └──────┘            └──────┘                           │
│                                                         │
│ Detection: Sequence numbers, acknowledgements          │
│ Solution: Retries, checksums                            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 3. Timing Failure                                       │
├─────────────────────────────────────────────────────────┤
│ Node responds but too late (overloaded, GC pause)       │
│                                                         │
│ ┌──────┐  Request (expect 100ms)                       │
│ │Client│ ─────────────────────────→ ┌──────┐           │
│ └──────┘                            │Server│           │
│    ⏰ Timeout after 5s               └──────┘           │
│    ⏰ Response arrives at 10s (too late!) ❌            │
│                                                         │
│ Problem: Client gave up, but server did work           │
│ Solution: Idempotency, distributed transactions        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 4. Byzantine Failure (Arbitrary)                       │
├─────────────────────────────────────────────────────────┤
│ Node behaves maliciously or unpredictably (hacked,     │
│ buggy, corrupted)                                       │
│                                                         │
│ ┌──────┐  "Balance = $100" → ┌──────┐                 │
│ │ Node │                      │Client│                 │
│ │ (Bad)│  "Balance = $1M"  → │   A  │  (Lies!)        │
│ └──────┘                      └──────┘                 │
│                                                         │
│ Examples:                                               │
│ ├─ Sends conflicting data to different nodes           │
│ ├─ Pretends to be other nodes                          │
│ └─ Corrupts data                                        │
│                                                         │
│ Solution: Byzantine Fault Tolerance (PBFT), quorums,   │
│           cryptographic signatures                      │
└─────────────────────────────────────────────────────────┘
```

### Failure Detection

```python
class FailureDetector:
    def __init__(self, timeout=5):
        self.timeout = timeout
        self.last_heartbeat = {}
    
    def on_heartbeat(self, node_id):
        """Called when receiving heartbeat from node"""
        self.last_heartbeat[node_id] = time.time()
    
    def is_alive(self, node_id):
        """Check if node is alive"""
        if node_id not in self.last_heartbeat:
            return False
        
        elapsed = time.time() - self.last_heartbeat[node_id]
        return elapsed < self.timeout

# Problem: False positives (slow network, not crashed)
# Tradeoff:
# ├─ Short timeout: Fast detection, but many false alarms
# └─ Long timeout: Fewer false alarms, but slow detection
```

**Properties of Failure Detectors:**
- **Completeness:** Every crashed node is eventually detected
- **Accuracy:** No node is incorrectly suspected as crashed

**Reality:** Cannot have both in asynchronous networks! (FLP impossibility)

---

## 8. Basic Coordination Primitives

### 1. Leader Election

**Problem:** Designate one node as coordinator.

```python
class BullyAlgorithm:
    """Simple leader election algorithm"""
    
    def __init__(self, node_id, all_nodes):
        self.node_id = node_id
        self.all_nodes = sorted(all_nodes)
        self.leader = None
    
    def elect_leader(self):
        # Send ELECTION message to all higher-ID nodes
        higher_nodes = [n for n in self.all_nodes if n > self.node_id]
        
        responses = []
        for node in higher_nodes:
            try:
                response = send_message(node, "ELECTION")
                responses.append(response)
            except NetworkError:
                pass  # Node is down
        
        if not responses:
            # No higher node responded → I am the leader!
            self.leader = self.node_id
            self.broadcast("COORDINATOR", self.node_id)
        else:
            # Wait for COORDINATOR message from higher node
            self.wait_for_coordinator()

# Example
nodes = [1, 2, 3, 4, 5]
node_3 = BullyAlgorithm(node_id=3, all_nodes=nodes)
node_3.elect_leader()  # Node 5 will become leader (highest ID)
```

**Use cases:** Primary-backup replication, distributed locking, task scheduling.

### 2. Mutual Exclusion (Distributed Locks)

**Problem:** Ensure only one node accesses critical section at a time.

```python
class DistributedLock:
    def __init__(self, lock_service):
        self.lock_service = lock_service  # e.g., Redis, ZooKeeper
    
    def acquire(self, resource_name, timeout=10):
        """Acquire lock on resource"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Try to set lock (atomic operation)
            success = self.lock_service.set_if_not_exists(
                key=f"lock:{resource_name}",
                value=self.node_id,
                ttl=30  # Lock expires after 30s (prevent deadlocks)
            )
            
            if success:
                return True
            
            time.sleep(0.1)  # Wait and retry
        
        return False  # Failed to acquire lock
    
    def release(self, resource_name):
        """Release lock"""
        self.lock_service.delete(f"lock:{resource_name}")

# Example: Only one node can process payment at a time
lock = DistributedLock(redis_client)
if lock.acquire("payment:user_123"):
    try:
        process_payment(user_id=123, amount=100)
    finally:
        lock.release("payment:user_123")
```

**Challenges:**
- **Deadlocks:** Node acquires lock and crashes (solution: TTL)
- **Split-brain:** Two nodes think they have the lock (solution: Fencing tokens)

### 3. Barriers and Synchronization

```python
class DistributedBarrier:
    """Wait for N nodes to reach checkpoint before continuing"""
    
    def __init__(self, num_nodes, coordination_service):
        self.num_nodes = num_nodes
        self.coordination_service = coordination_service
        self.barrier_id = str(uuid.uuid4())
    
    def wait(self):
        """Block until all nodes reach barrier"""
        # Register this node at barrier
        self.coordination_service.increment(f"barrier:{self.barrier_id}")
        
        # Wait until count reaches num_nodes
        while True:
            count = self.coordination_service.get(f"barrier:{self.barrier_id}")
            if count >= self.num_nodes:
                break
            time.sleep(0.1)

# Example: Wait for 3 workers to finish processing before aggregating
barrier = DistributedBarrier(num_nodes=3, coordination_service=zookeeper)

# Worker 1
process_data_partition_1()
barrier.wait()  # Block
aggregate_results()  # All workers finished

# Worker 2
process_data_partition_2()
barrier.wait()  # Block
aggregate_results()  # All workers finished
```

---

## 9. Hands-On Examples

### Example 1: Distributed Counter

**Problem:** Increment a counter from multiple nodes without losing updates.

```python
import redis
import threading

class DistributedCounter:
    def __init__(self, redis_client, counter_name):
        self.redis = redis_client
        self.counter_name = counter_name
    
    def increment(self):
        """Thread-safe increment using Redis atomic operation"""
        return self.redis.incr(self.counter_name)
    
    def get(self):
        value = self.redis.get(self.counter_name)
        return int(value) if value else 0

# Example: Page view counter
redis_client = redis.Redis(host='localhost', port=6379)
counter = DistributedCounter(redis_client, "page_views:homepage")

# Simulate 100 concurrent increments
threads = []
for i in range(100):
    thread = threading.Thread(target=counter.increment)
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

print(f"Total page views: {counter.get()}")  # Exactly 100 ✅
```

**Why it works:** Redis INCR is atomic (single-threaded event loop).

### Example 2: Distributed Queue

```python
class DistributedQueue:
    def __init__(self, redis_client, queue_name):
        self.redis = redis_client
        self.queue_name = queue_name
    
    def enqueue(self, item):
        """Add item to end of queue"""
        self.redis.rpush(self.queue_name, item)
    
    def dequeue(self, timeout=0):
        """Remove item from front of queue (blocking)"""
        result = self.redis.blpop(self.queue_name, timeout=timeout)
        if result:
            _, item = result
            return item
        return None

# Producer
queue = DistributedQueue(redis_client, "tasks")
queue.enqueue("process_video_123")
queue.enqueue("send_email_456")

# Consumer (different process/server)
while True:
    task = queue.dequeue(timeout=5)
    if task:
        process_task(task)
```

### Example 3: Heartbeat Monitor

```python
import time
from threading import Thread

class HeartbeatMonitor:
    def __init__(self, node_id, peers, interval=1):
        self.node_id = node_id
        self.peers = peers
        self.interval = interval
        self.last_seen = {peer: time.time() for peer in peers}
    
    def send_heartbeats(self):
        """Send heartbeat to all peers"""
        while True:
            for peer in self.peers:
                try:
                    send_message(peer, {"type": "HEARTBEAT", "from": self.node_id})
                except Exception:
                    pass
            time.sleep(self.interval)
    
    def on_heartbeat(self, from_node):
        """Update last seen time for peer"""
        self.last_seen[from_node] = time.time()
    
    def check_failures(self):
        """Detect failed nodes"""
        now = time.time()
        timeout = 3 * self.interval  # 3 missed heartbeats = failure
        
        failed_nodes = []
        for peer, last_seen in self.last_seen.items():
            if now - last_seen > timeout:
                failed_nodes.append(peer)
        
        return failed_nodes
    
    def start(self):
        """Start heartbeat thread"""
        thread = Thread(target=self.send_heartbeats, daemon=True)
        thread.start()

# Example
monitor = HeartbeatMonitor(node_id="node_1", peers=["node_2", "node_3"])
monitor.start()

# Check for failures
time.sleep(10)
failed = monitor.check_failures()
print(f"Failed nodes: {failed}")
```

---

## 🎯 Key Takeaways

1. **Distributed systems are hard:** Networks fail, clocks drift, nodes crash
2. **No global clock:** Use logical clocks (Lamport, Vector) for ordering
3. **Asynchronous model:** Cannot distinguish slow from crashed
4. **Fallacies matter:** Network is unreliable, has latency, costs bandwidth
5. **Failure detection:** Tradeoff between speed and accuracy
6. **Coordination primitives:** Leader election, locks, barriers (building blocks)

---

## 📚 Further Reading

- **"Distributed Systems" by Tanenbaum & Van Steen** (textbook)
- **"Designing Data-Intensive Applications" by Martin Kleppmann** (practical)
- **MIT 6.824:** Distributed Systems course (lectures online)
- **Fallacies of Distributed Computing:** https://en.wikipedia.org/wiki/Fallacies_of_distributed_computing

---

## ✅ Practice Exercises

1. Implement a distributed counter with retry logic (handle network failures)
2. Build a simple failure detector with heartbeats
3. Simulate clock skew and show why wall time fails for ordering
4. Implement Lamport timestamps for 3 nodes
5. Design a distributed lock with deadlock prevention (TTL)

---

**Next:** [INTERMEDIATE.md](INTERMEDIATE.md) — Consensus algorithms (Paxos, Raft), replication strategies, consistency models.
