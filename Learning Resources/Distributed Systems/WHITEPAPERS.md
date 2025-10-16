# Distributed Systems - WHITEPAPERS

**Reading Time:** 4-6 weeks  
**Prerequisites:** BEGINNER.md + INTERMEDIATE.md + EXPERT.md  
**Focus:** Seminal papers that shaped distributed systems

---

## 📚 Table of Contents

1. [Time, Clocks, and the Ordering of Events (Lamport, 1978)](#1-time-clocks-and-the-ordering-of-events)
2. [FLP Impossibility Result (1985)](#2-flp-impossibility-result)
3. [Paxos Made Simple (Lamport, 2001)](#3-paxos-made-simple)
4. [Dynamo: Amazon's Highly Available Key-Value Store (2007)](#4-dynamo-amazons-highly-available-key-value-store)
5. [Raft Consensus Algorithm (2014)](#5-raft-consensus-algorithm)
6. [Spanner: Google's Globally Distributed Database (2012)](#6-spanner-googles-globally-distributed-database)
7. [Calvin: Fast Distributed Transactions (2012)](#7-calvin-fast-distributed-transactions)
8. [Bonus Papers](#8-bonus-papers)

---

## 1. Time, Clocks, and the Ordering of Events

**Author:** Leslie Lamport  
**Published:** Communications of the ACM, July 1978  
**Link:** https://lamport.azurewebsites.net/pubs/time-clocks.pdf

### The Problem

```
Question: How do we order events in a distributed system without a global clock?

Example:
├─ Event A: User sends email from New York
├─ Event B: User receives email in London
└─ Which happened first?

Challenge:
├─ Clocks on different machines drift
├─ Network delays are variable
└─ No way to know absolute order
```

### Lamport's Solution: Happened-Before Relation

```
Definition: Event a → Event b (a "happened before" b) if:

1. Same process: a occurs before b in program order
2. Message passing: a is send(m), b is receive(m)
3. Transitivity: If a → c and c → b, then a → b

Example:
Process P1: a ──────→ b ──────→ send(m1) ─────→
                                    ↓
Process P2:                    receive(m1) ──→ c ──→ send(m2) ──→
                                                         ↓
Process P3:                                         receive(m2) ──→ d

Ordering:
├─ a → b (same process)
├─ send(m1) → receive(m1) (message)
├─ receive(m1) → c (same process)
├─ a → b → send(m1) → receive(m1) → c (transitivity)
├─ c → send(m2) → receive(m2) → d (transitivity)
└─ Conclusion: a → d ✅

Concurrent events (no ordering):
├─ a and c (no path from a to c or c to a)
└─ a || c (concurrent)
```

### Logical Clocks

**Algorithm:**
```python
class LamportClock:
    def __init__(self):
        self.time = 0
    
    def tick(self):
        """Local event"""
        self.time += 1
        return self.time
    
    def send(self):
        """Sending message"""
        self.time += 1
        return self.time
    
    def receive(self, msg_time):
        """Receiving message"""
        self.time = max(self.time, msg_time) + 1
        return self.time

# Example
p1 = LamportClock()
p2 = LamportClock()

# P1: Event a
t_a = p1.tick()  # 1

# P1: Event b
t_b = p1.tick()  # 2

# P1: Send message
t_send = p1.send()  # 3

# P2: Receive message
t_recv = p2.receive(t_send)  # max(0, 3) + 1 = 4

# P2: Event c
t_c = p2.tick()  # 5

# Property: If a → b, then C(a) < C(b) ✅
print(f"a: {t_a}, b: {t_b}, send: {t_send}, recv: {t_recv}, c: {t_c}")
# Output: a: 1, b: 2, send: 3, recv: 4, c: 5
```

**Limitation:**
```
C(a) < C(b) does NOT imply a → b

Counterexample:
├─ P1: Event a at time 1
├─ P2: Event b at time 2 (concurrent)
├─ C(a) < C(b) BUT a || b (concurrent, not ordered)
```

### Total Ordering

```
To break ties, use process ID:

(time, process_id)

Example:
├─ Event a: (5, P1)
├─ Event b: (5, P2)
├─ Total order: (5, P1) < (5, P2) because P1 < P2 ✅
```

### Key Insights

```
1. Physical time is not needed for ordering
2. Logical clocks capture causality
3. Concurrent events cannot be ordered
4. Total ordering requires breaking ties (process ID)
```

### Impact on Distributed Systems

```
Applications:
├─ Distributed debugging (order log events)
├─ Consistency models (causal consistency)
├─ Version vectors (detect conflicts)
└─ Blockchain (order transactions)

Still relevant in 2025:
├─ Every distributed database uses logical clocks
├─ Foundation for vector clocks, version vectors
└─ Required reading for distributed systems engineers
```

---

## 2. FLP Impossibility Result

**Authors:** Fischer, Lynch, Paterson  
**Published:** Journal of the ACM, April 1985  
**Link:** https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf

### The Theorem

```
┌─────────────────────────────────────────────────────────┐
│ FLP Impossibility Theorem                              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ In an asynchronous network where even ONE process can  │
│ fail by crashing, there is NO deterministic consensus  │
│ algorithm that guarantees termination.                 │
│                                                         │
└─────────────────────────────────────────────────────────┘

Properties:
├─ Agreement: All non-faulty processes decide same value
├─ Validity: Decided value was proposed by some process
├─ Termination: All non-faulty processes eventually decide

FLP proves: Cannot have all three in asynchronous networks!
```

### Why Consensus is Impossible

```
Scenario: 2 processes, 1 can fail

Process A proposes: 0
Process B proposes: 1

Problem: Cannot distinguish crashed process from slow process

Case 1: A crashed
├─ B waits for A's message
├─ A never responds (crashed)
├─ B cannot decide (might violate agreement if A is just slow)

Case 2: A is slow
├─ B waits for A's message
├─ A sends message, but network is slow
├─ B decides without A (might violate agreement if A decides differently)

Catch-22:
├─ Wait forever: No termination ❌
└─ Decide without waiting: Might violate agreement ❌
```

### Proof Sketch

```python
# Simplified proof intuition

def consensus_algorithm(initial_value, processes):
    """Hypothetical consensus algorithm"""
    
    # Start in bivalent state (can decide 0 or 1)
    state = "bivalent"
    
    while state == "bivalent":
        # Receive messages from processes
        messages = receive_messages(processes)
        
        # Problem: What if one process is slow/crashed?
        # ├─ Wait: Might wait forever ❌
        # └─ Don't wait: Might decide prematurely ❌
        
        # FLP shows: There exists an execution where system
        # remains bivalent forever (never reaches decision)
        pass
    
    # Cannot guarantee termination!


# The "always bivalent" execution
def flp_execution():
    """Adversarial execution that prevents decision"""
    
    # Scheduler delays messages to keep system bivalent
    while True:
        # Identify critical message (would make system univalent)
        critical_msg = find_critical_message()
        
        # Delay that message
        delay(critical_msg)
        
        # Process other messages
        # System remains bivalent (can still decide 0 or 1)
```

### Practical Implications

```
Does FLP mean consensus is impossible in practice?

NO! FLP has loopholes:

1. Randomization (not deterministic)
   ├─ Example: Random timeouts
   └─ Guarantee: Terminate with probability 1 (not certainty)

2. Partial Synchrony
   ├─ Assumption: Eventually network becomes synchronous
   └─ Paxos, Raft work in practice (assume bounded delays)

3. Failure Detectors
   ├─ Eventually Perfect detector (◇P)
   └─ Eventually suspects all crashed processes

4. Weakening Guarantees
   ├─ Probabilistic termination
   └─ Bounded time with high probability
```

### Real-World Systems

```
How do real systems handle FLP?

Paxos/Raft:
├─ Use timeouts (randomization)
├─ Assume partial synchrony
└─ Work in practice, but no theoretical guarantee

Bitcoin:
├─ Probabilistic finality (6 confirmations ≈ 99.9% certain)
└─ Not guaranteed, but good enough

Spanner:
├─ TrueTime (bounded clock uncertainty)
├─ Wait out uncertainty
└─ Strong consistency in practice
```

### Key Takeaway

```
FLP teaches us:
├─ Perfect consensus is impossible in asynchronous networks
├─ Real systems make trade-offs (timeouts, assumptions)
├─ Understand limitations when designing distributed systems
└─ "In theory, theory and practice are the same. In practice, they are not."
```

---

## 3. Paxos Made Simple

**Author:** Leslie Lamport  
**Published:** ACM SIGACT News, November 2001  
**Link:** https://lamport.azurewebsites.net/pubs/paxos-simple.pdf

### Background

```
Original Paxos paper (1998): "The Part-Time Parliament"
├─ Written as Greek allegory
├─ Reviewers couldn't understand it
└─ Rejected multiple times

"Paxos Made Simple" (2001):
├─ Lamport rewrote in plain English
├─ Opening line: "The Paxos algorithm, when presented in plain English, is very simple."
└─ Still considered complex by many! 😅
```

### The Paxos Problem

```
Goal: Multiple proposers, choose single value

Setup:
├─ N processes (odd number, e.g., 5)
├─ Any process can propose value
├─ Goal: All processes agree on ONE value
└─ Tolerate F = (N-1)/2 failures

Example:
├─ 5 processes: Tolerate 2 failures
└─ 3 processes: Tolerate 1 failure
```

### Paxos Roles

```
1. Proposer: Proposes values
2. Acceptor: Votes on proposals (needs majority)
3. Learner: Learns chosen value

Note: One process can play multiple roles
```

### Paxos Algorithm (Detailed)

```
Phase 1a: Prepare
┌─────────────────────────────────────────────────────────┐
│ Proposer:                                               │
│ ├─ Choose proposal number n (higher than any seen)     │
│ └─ Send PREPARE(n) to majority of acceptors            │
└─────────────────────────────────────────────────────────┘

Phase 1b: Promise
┌─────────────────────────────────────────────────────────┐
│ Acceptor:                                               │
│ ├─ Receive PREPARE(n)                                   │
│ ├─ If n > highest_promised_n:                           │
│ │  ├─ Promise not to accept proposals < n              │
│ │  ├─ Reply with highest accepted (n_a, v_a)           │
│ │  └─ highest_promised_n = n                           │
│ └─ Else: Ignore (already promised higher)              │
└─────────────────────────────────────────────────────────┘

Phase 2a: Accept
┌─────────────────────────────────────────────────────────┐
│ Proposer:                                               │
│ ├─ Receive promises from majority                      │
│ ├─ If any acceptor returned (n_a, v_a):                │
│ │  └─ Use v_a with highest n_a (not our value!)       │
│ ├─ Else: Use our proposed value v                      │
│ └─ Send ACCEPT(n, v) to majority of acceptors          │
└─────────────────────────────────────────────────────────┘

Phase 2b: Accepted
┌─────────────────────────────────────────────────────────┐
│ Acceptor:                                               │
│ ├─ Receive ACCEPT(n, v)                                 │
│ ├─ If n >= highest_promised_n:                          │
│ │  ├─ Accept (n, v)                                    │
│ │  └─ Notify learners                                  │
│ └─ Else: Reject (promised higher)                      │
└─────────────────────────────────────────────────────────┘
```

### Example Execution

```
Setup: 5 acceptors (A1, A2, A3, A4, A5)
       2 proposers (P1, P2)

─────────────────────────────────────────────────────────
T1: P1 proposes value "X" with n=1

    P1 → A1, A2, A3: PREPARE(n=1)

T2: Acceptors promise

    A1 → P1: PROMISE (no prior accepts)
    A2 → P1: PROMISE (no prior accepts)
    A3 → P1: PROMISE (no prior accepts)

    P1 has majority (3/5) ✅

T3: P1 sends ACCEPT

    P1 → A1, A2, A3: ACCEPT(n=1, v="X")

T4: Acceptors accept

    A1: accepted = (1, "X")
    A2: accepted = (1, "X")
    
    "X" is chosen! (majority accepted) ✅

─────────────────────────────────────────────────────────
T5: P2 proposes value "Y" with n=2 (concurrent)

    P2 → A1, A2, A3: PREPARE(n=2)

T6: Acceptors promise, report accepted value

    A1 → P2: PROMISE (accepted=(1, "X"))
    A2 → P2: PROMISE (accepted=(1, "X"))
    A3 → P2: PROMISE (no accept yet)

T7: P2 MUST use "X" (not "Y"!)

    Highest accepted: (1, "X")
    P2 → A1, A2, A3: ACCEPT(n=2, v="X")  ← Not "Y"!

T8: Result: "X" remains chosen ✅
```

### Why Paxos Works

```
Safety (agreement):
├─ Once value is chosen, all future proposals choose same value
├─ Proof: Proposer adopts highest accepted value
└─ Invariant: Chosen value appears in all majority quorums

Liveness (termination):
├─ Eventually one proposer succeeds
├─ Challenge: Dueling proposers (livelock)
└─ Solution: Leader election, exponential backoff
```

### Multi-Paxos Optimization

```
Basic Paxos: 2 round trips per decision (slow!)

Multi-Paxos optimization:
├─ Run Phase 1 once for entire log
├─ Leader sends Phase 2 (ACCEPT) for each entry
└─ 1 round trip per decision ✅

State Machine Replication:
├─ Paxos chooses log entries (commands)
├─ All replicas execute commands in same order
└─ Result: Replicated state machine
```

### Paxos in Production

```
Google Chubby (2006):
├─ Distributed lock service
├─ Uses Paxos for consensus
└─ Powers BigTable, GFS

Apache ZooKeeper:
├─ Based on ZAB (similar to Paxos)
├─ Coordination service (locks, config, leader election)
└─ Used by Kafka, HBase, Hadoop

etcd:
├─ Uses Raft (not Paxos)
├─ Simpler than Paxos
└─ Powers Kubernetes
```

---

## 4. Dynamo: Amazon's Highly Available Key-Value Store

**Authors:** DeCandia et al. (Amazon)  
**Published:** SOSP 2007  
**Link:** https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf

### The Problem

```
Amazon's requirements:
├─ 99.9% availability (5.26 min downtime/month max)
├─ Handle peak load (10M requests/second)
├─ Low latency (<300ms P99)
└─ Eventual consistency acceptable (shopping cart can merge)

Traditional databases:
├─ Strong consistency → Low availability ❌
└─ Cannot meet 99.9% SLA
```

### Dynamo's Design Principles

```
1. Always Writable
   ├─ Accept writes even during failures
   └─ Resolve conflicts later (eventual consistency)

2. Incremental Scalability
   ├─ Add nodes without downtime
   └─ Automatic data redistribution

3. Symmetry
   ├─ No master/slave
   └─ All nodes have same responsibilities

4. Decentralization
   ├─ No single point of failure
   └─ Peer-to-peer architecture

5. Heterogeneity
   ├─ Nodes have different capacities
   └─ Workload proportional to capacity
```

### Dynamo Architecture

```
┌─────────────────────────────────────────────────────────┐
│ 1. Partitioning: Consistent Hashing                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Hash Ring (0 to 2^128):                                │
│                                                         │
│         Node A (token: 0x0000)                          │
│            ↓                                            │
│    ┌───────────────┐                                    │
│    │               │                                    │
│    │               │ ← Node D (token: 0xC000)          │
│    │               │                                    │
│    │               │                                    │
│    │               │                                    │
│    │               │ ← Node C (token: 0x8000)          │
│    │               │                                    │
│    └───────────────┘                                    │
│            ↑                                            │
│         Node B (token: 0x4000)                          │
│                                                         │
│ Key placement:                                          │
│ ├─ hash("user123") = 0x3000 → Node B                  │
│ ├─ hash("user456") = 0xA000 → Node C                  │
│ └─ Add/remove node: Only 1/N keys move ✅              │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 2. Replication: N replicas (default: 3)               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Key "user123" → hash = 0x3000 → Node B                │
│                                                         │
│ Replicas:                                               │
│ ├─ Primary: Node B (coordinator)                       │
│ ├─ Replica 1: Node C (next clockwise)                  │
│ └─ Replica 2: Node D (next clockwise)                  │
│                                                         │
│ Preference list: [B, C, D]                             │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 3. Versioning: Vector Clocks                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Track causality to detect conflicts:                    │
│                                                         │
│ Version 1: {A:1} (Node A wrote)                        │
│ Version 2: {A:1, B:1} (Node B updated)                 │
│ Version 3a: {A:1, B:1, C:1} (Node C updated)           │
│ Version 3b: {A:1, B:2} (Node B updated, concurrent!)   │
│                                                         │
│ Conflict: 3a and 3b are concurrent                     │
│ ├─ Neither {A:1, B:1, C:1} ≤ {A:1, B:2}               │
│ └─ Application must resolve (e.g., merge carts)       │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 4. Quorum: Tunable Consistency                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Parameters:                                             │
│ ├─ N = replication factor (e.g., 3)                    │
│ ├─ W = write quorum (e.g., 2)                          │
│ └─ R = read quorum (e.g., 2)                           │
│                                                         │
│ Constraint: R + W > N (ensures overlap)                │
│                                                         │
│ Configurations:                                         │
│ ├─ (R=1, W=3): Fast reads, slow writes                │
│ ├─ (R=3, W=1): Slow reads, fast writes                │
│ └─ (R=2, W=2): Balanced                                │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 5. Anti-Entropy: Merkle Trees                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Detect inconsistencies efficiently:                     │
│                                                         │
│        Root Hash (entire dataset)                       │
│          /                \                             │
│    Hash(Keys 0-100)   Hash(Keys 101-200)              │
│      /        \          /           \                  │
│  H(0-50)  H(51-100)  H(101-150)  H(151-200)           │
│                                                         │
│ Sync protocol:                                          │
│ 1. Exchange root hashes                                 │
│ 2. If different, exchange subtree hashes                │
│ 3. Identify divergent leaf, sync only that range        │
│                                                         │
│ Efficiency: O(log N) hashes exchanged ✅               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Dynamo Read/Write Protocol

```python
class DynamoNode:
    def __init__(self, node_id, N=3, R=2, W=2):
        self.node_id = node_id
        self.N = N  # Replication factor
        self.R = R  # Read quorum
        self.W = W  # Write quorum
        self.data = {}  # key → [(value, vector_clock)]
    
    def put(self, key, value):
        """Write with quorum"""
        # 1. Coordinate write
        coordinator = self.get_coordinator(key)
        
        # 2. Get preference list (N replicas)
        replicas = self.get_preference_list(key, self.N)
        
        # 3. Increment vector clock
        vector_clock = self.get_vector_clock(key)
        vector_clock[self.node_id] = vector_clock.get(self.node_id, 0) + 1
        
        # 4. Write to W replicas
        acks = 0
        for replica in replicas:
            try:
                replica.local_put(key, value, vector_clock)
                acks += 1
                if acks >= self.W:
                    return "SUCCESS"
            except Exception:
                pass
        
        raise Exception(f"Failed to write to {self.W} replicas")
    
    def get(self, key):
        """Read with quorum"""
        # 1. Get preference list
        replicas = self.get_preference_list(key, self.N)
        
        # 2. Read from R replicas
        versions = []
        for replica in replicas:
            try:
                version = replica.local_get(key)
                versions.append(version)
                if len(versions) >= self.R:
                    break
            except Exception:
                pass
        
        if len(versions) < self.R:
            raise Exception(f"Failed to read from {self.R} replicas")
        
        # 3. Reconcile versions
        return self.reconcile(versions)
    
    def reconcile(self, versions):
        """Resolve conflicts using vector clocks"""
        # Remove dominated versions (A ≤ B means A is older)
        current = []
        for v1 in versions:
            is_dominated = False
            for v2 in versions:
                if self.is_dominated(v1["clock"], v2["clock"]):
                    is_dominated = True
                    break
            if not is_dominated:
                current.append(v1)
        
        if len(current) == 1:
            return current[0]  # No conflict
        else:
            # Conflict! Return all versions, let app resolve
            return {"conflict": True, "versions": current}
    
    def is_dominated(self, clock1, clock2):
        """Check if clock1 ≤ clock2 (clock1 is older)"""
        for node_id in set(clock1.keys()).union(clock2.keys()):
            if clock1.get(node_id, 0) > clock2.get(node_id, 0):
                return False
        return True

# Example: Shopping cart
dynamo = DynamoNode("node1", N=3, R=2, W=2)

# User adds item
dynamo.put("cart:user123", ["apple"])
# Version: {node1: 1}

# User adds another item (from different node)
dynamo.put("cart:user123", ["apple", "banana"])
# Version: {node1: 1, node2: 1}

# Concurrent add (conflict!)
# Node 3 adds "orange" without seeing "banana"
# Version: {node1: 1, node3: 1}

# Read returns conflict
result = dynamo.get("cart:user123")
# result = {
#   "conflict": True,
#   "versions": [
#     {"value": ["apple", "banana"], "clock": {node1: 1, node2: 1}},
#     {"value": ["apple", "orange"], "clock": {node1: 1, node3: 1}}
#   ]
# }

# Application resolves: Merge carts
merged = ["apple", "banana", "orange"]
dynamo.put("cart:user123", merged)
# Version: {node1: 1, node2: 1, node3: 1, node4: 1}
```

### Dynamo's Impact

```
Influenced many systems:
├─ Apache Cassandra (Dynamo + BigTable)
├─ Riak (direct Dynamo implementation)
├─ Voldemort (LinkedIn)
└─ DynamoDB (AWS managed service)

Key innovations:
├─ Consistent hashing (partition + add nodes)
├─ Vector clocks (detect conflicts)
├─ Quorum (tunable consistency)
├─ Merkle trees (efficient anti-entropy)
└─ Always writable (high availability)

Lessons:
├─ Eventual consistency is acceptable for many apps
├─ Application-level conflict resolution works
└─ Availability > Consistency (for Amazon's use case)
```

---

## 5. Raft Consensus Algorithm

**Authors:** Diego Ongaro, John Ousterhout (Stanford)  
**Published:** USENIX ATC 2014  
**Link:** https://raft.github.io/raft.pdf

### Motivation

```
Problem with Paxos:
├─ Difficult to understand
├─ Difficult to implement correctly
├─ Incomplete specification (Multi-Paxos not in paper)
└─ Google took years to implement Chubby

Raft's goal: "Understandability as primary design goal"
├─ Easier to teach in courses
├─ Easier to implement in systems
└─ Same guarantees as Paxos
```

### Raft's Key Ideas

```
1. Strong Leader
   ├─ All writes go through leader
   ├─ Log entries flow one direction (leader → followers)
   └─ Simpler than Paxos (no dueling proposers)

2. Leader Election
   ├─ Randomized timeouts prevent split votes
   ├─ Candidate with longest log wins
   └─ One leader per term (epoch)

3. Log Replication
   ├─ Leader appends to local log
   ├─ Replicates to followers
   ├─ Commits when majority replicated
   └─ Eventually all logs identical

4. Safety
   ├─ Elected leader has all committed entries
   ├─ Log matching property
   └─ State machine safety
```

### Raft Algorithm

```
┌─────────────────────────────────────────────────────────┐
│ Leader Election                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ States: Follower, Candidate, Leader                    │
│                                                         │
│ Timeout (follower → candidate):                        │
│ ├─ Increment term                                       │
│ ├─ Vote for self                                        │
│ ├─ Request votes from all peers                        │
│ └─ If majority: Become leader                          │
│                                                         │
│ Voting rules:                                           │
│ ├─ One vote per term (first come first served)         │
│ ├─ Vote only if candidate's log ≥ ours                 │
│ └─ Reset timeout when voting                           │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Log Replication                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Client → Leader: Command                               │
│                                                         │
│ Leader:                                                 │
│ ├─ Append to local log                                 │
│ ├─ Send AppendEntries to followers                     │
│ ├─ Wait for majority to replicate                      │
│ ├─ Commit (advance commitIndex)                        │
│ ├─ Apply to state machine                              │
│ └─ Reply to client                                     │
│                                                         │
│ Log matching property:                                  │
│ ├─ If two entries have same (index, term), they have   │
│ │  same command AND all preceding entries are identical│
│ └─ Enforced by AppendEntries consistency check         │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Safety                                                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Election Safety:                                        │
│ ├─ At most one leader per term                         │
│ └─ Proof: Majority votes, can't have two majorities    │
│                                                         │
│ Leader Completeness:                                    │
│ ├─ If entry committed in term T, it appears in logs of │
│ │  all leaders for terms ≥ T                           │
│ └─ Proof: Candidate must have majority's log, majority │
│    has committed entry                                  │
│                                                         │
│ State Machine Safety:                                   │
│ ├─ If server applies entry at index i, no other server │
│ │  applies different entry at i                        │
│ └─ Follows from leader completeness                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Raft vs Paxos

```
┌───────────────────────────────────────────────────────────┐
│ Feature          │ Raft              │ Paxos             │
├──────────────────┼───────────────────┼───────────────────┤
│ Understandability│ ✅ High           │ ❌ Low            │
│ Leader           │ ✅ Strong         │ ⚠️ Weak (Multi-P) │
│ Log structure    │ ✅ Must be contig │ ❌ Gaps allowed   │
│ Election         │ ✅ Simple (term)  │ ⚠️ Complex (ballots)│
│ Implementation   │ ✅ Straightforward│ ❌ Tricky         │
│ Liveness         │ ✅ Good (rand TO) │ ⚠️ Dueling props  │
│ Performance      │ ≈ Same            │ ≈ Same            │
└───────────────────────────────────────────────────────────┘
```

### Raft in Production

```
Systems using Raft:
├─ etcd (Kubernetes, CoreOS)
├─ Consul (HashiCorp)
├─ TiKV (TiDB)
├─ CockroachDB
└─ InfluxDB

Why Raft won:
├─ Easier to implement (companies can build it in-house)
├─ Easier to debug (clearer invariants)
├─ Great educational resources (raft.github.io)
└─ Same performance as Paxos
```

---

## 6. Spanner: Google's Globally Distributed Database

**Authors:** Corbett et al. (Google)  
**Published:** OSDI 2012  
**Link:** https://research.google/pubs/pub39966/

### The Grand Challenge

```
Build a database that is:
├─ Globally distributed (replicate across continents)
├─ Strongly consistent (external consistency = linearizability)
├─ High availability (survive data center failures)
├─ Scalable (millions of QPS, petabytes of data)
└─ SQL support (not just key-value)

Problem: CAP theorem says can't have consistency + availability!

Spanner's answer: Redefine "available"
├─ 99.999% uptime (5 min downtime/year)
├─ Sacrifice availability during network partitions (rare)
└─ Choose consistency over availability (CP system)
```

### TrueTime API

```
The key innovation: Bounded clock uncertainty

API:
├─ TT.now() → [earliest, latest]
├─ TT.after(t) → true if t definitely in past
└─ TT.before(t) → true if t definitely in future

Implementation:
┌─────────────────────────────────────────────────────────┐
│ Each Google data center:                               │
│ ├─ GPS receivers (cheap, 1μs accuracy when locked)    │
│ ├─ Atomic clocks (expensive, but no drift)             │
│ └─ Time masters: Sync from GPS + atomic clocks         │
│                                                         │
│ Every server:                                           │
│ ├─ Daemon syncs with time masters                      │
│ ├─ Uses Marzullo's algorithm (best estimate)           │
│ └─ Uncertainty: ε ≈ 1-7 milliseconds                   │
│                                                         │
│ Failure modes:                                          │
│ ├─ GPS signal lost: Use atomic clocks (hours backup)   │
│ ├─ Both fail: Increase ε (uncertainty grows)           │
│ └─ ε too large: Refuse to serve (availability↓)       │
└─────────────────────────────────────────────────────────┘
```

### Spanner Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Universe (Spanner deployment)                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│ │ Zone (DC 1) │  │ Zone (DC 2) │  │ Zone (DC 3) │     │
│ │             │  │             │  │             │     │
│ │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │     │
│ │ │Spanserver│ │  │ │Spanserver│ │  │ │Spanserver│ │     │
│ │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │     │
│ │      ...    │  │      ...    │  │      ...    │     │
│ │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │     │
│ │ │Spanserver│ │  │ │Spanserver│ │  │ │Spanserver│ │     │
│ │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │     │
│ └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                         │
│ Spanserver = 100-1000 tablets (partitions)             │
│ Tablet = Paxos group (5-7 replicas across zones)       │
│                                                         │
└─────────────────────────────────────────────────────────┘

Data organization:
├─ Directory: Unit of data movement
├─ Tablet: Range of rows [start_key, end_key)
├─ Paxos group: Replicate tablet (one leader)
└─ Spanserver: Hosts multiple tablets
```

### Spanner Transactions

```python
class SpannerTransaction:
    def __init__(self, true_time):
        self.tt = true_time
        self.reads = []
        self.writes = []
    
    def read_write_txn(self, operations):
        """Read-write transaction (uses 2PC + Paxos)"""
        
        # 1. Acquire locks on participants
        participants = self.get_participants(operations)
        
        # 2. Execute reads/writes (buffer writes)
        start = self.tt.now()
        
        for op in operations:
            if op["type"] == "READ":
                self.reads.append(self.read(op["key"]))
            elif op["type"] == "WRITE":
                self.writes.append((op["key"], op["value"]))
        
        # 3. Choose commit timestamp
        # Must be after all reads, within TrueTime bound
        commit_ts = start["latest"]
        
        # 4. Two-phase commit
        # Prepare phase
        for participant in participants:
            participant.prepare(commit_ts, self.writes)
        
        # 5. Commit wait (KEY INNOVATION!)
        # Wait until commit_ts is definitely in the past
        while not self.tt.after(commit_ts):
            time.sleep(0.001)  # Wait ~7ms
        
        # 6. Commit phase
        for participant in participants:
            participant.commit(commit_ts)
        
        # 7. Release locks
        self.release_locks()
        
        return commit_ts
    
    def read_only_txn(self, keys, timestamp=None):
        """Read-only transaction (NO locks, NO 2PC!)"""
        
        if timestamp is None:
            # Use latest safe time (TT.now().latest)
            timestamp = self.tt.now()["latest"]
        
        # Read from any replica at timestamp
        results = []
        for key in keys:
            # Might block if timestamp > replica's safe time
            value = self.read_at_timestamp(key, timestamp)
            results.append(value)
        
        return results


# External consistency example

tt = TrueTime()
txn1 = SpannerTransaction(tt)
txn2 = SpannerTransaction(tt)

# T1: Transfer $100 from Alice to Bob
ts1 = txn1.read_write_txn([
    {"type": "READ", "key": "alice"},
    {"type": "WRITE", "key": "alice", "value": 900},
    {"type": "WRITE", "key": "bob", "value": 600}
])
# Commit wait: Waits ~7ms before returning to client

# Client sees T1 committed, starts T2
# T2: Read balances
ts2 = txn2.read_write_txn([
    {"type": "READ", "key": "alice"},  # Sees 900
    {"type": "READ", "key": "bob"}     # Sees 600
])

# Property: ts1 < ts2 (external consistency) ✅
# Guaranteed by commit wait!
```

### Spanner's Impact

```
Proved CAP is not absolute:
├─ With bounded clock uncertainty, can have strong consistency + high availability
├─ TrueTime: 1-7ms uncertainty, acceptable for Google
└─ Redefines "available" (99.999%, not 100%)

Influenced:
├─ CockroachDB (HLC: Hybrid Logical Clocks, no GPS)
├─ YugabyteDB (similar architecture)
├─ Amazon Aurora (different approach, MySQL compatible)
└─ Azure Cosmos DB (tunable consistency)

Key lesson:
├─ Hardware can help solve distributed systems problems
├─ GPS + atomic clocks = globally synchronized time
└─ Trade latency (7ms commit wait) for strong guarantees
```

---

## 7. Calvin: Fast Distributed Transactions

**Authors:** Thomson et al. (Yale)  
**Published:** SIGMOD 2012  
**Link:** http://cs.yale.edu/homes/thomson/publications/calvin-sigmod12.pdf

### The Problem

```
Traditional distributed transactions:
├─ Two-phase commit (2PC)
├─ Locks acquired during transaction
├─ High latency (multiple round trips)
└─ Deadlocks possible

Calvin's idea: Deterministic database
├─ Pre-order transactions (sequence number)
├─ All replicas execute in same order
├─ No 2PC needed! (order determines outcome)
└─ Locks acquired upfront (no deadlocks)
```

### Calvin Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Calvin's 3 Layers                                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 1. Sequencing Layer (Paxos/Raft)                       │
│    ├─ Assign global sequence number to transactions    │
│    ├─ Replicate log to all replicas                    │
│    └─ Output: Ordered transaction log                  │
│                                                         │
│ 2. Scheduling Layer                                     │
│    ├─ Lock manager (acquire in sequence order)         │
│    ├─ Deterministic: Same locks, same order            │
│    └─ No deadlocks (acquire in global order)           │
│                                                         │
│ 3. Storage Layer                                        │
│    ├─ Execute transaction (reads, writes)              │
│    ├─ Deterministic: Same inputs → same outputs        │
│    └─ Commit (release locks)                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Calvin Protocol

```python
class CalvinNode:
    def __init__(self, node_id, sequencer):
        self.node_id = node_id
        self.sequencer = sequencer  # Paxos/Raft instance
        self.lock_manager = {}
        self.storage = {}
        self.sequence_number = 0
    
    def submit_transaction(self, txn):
        """Client submits transaction"""
        # 1. Send to sequencer (Paxos/Raft)
        seq_num = self.sequencer.append(txn)
        return seq_num
    
    def execute_batch(self, txns):
        """Execute batch of transactions in sequence order"""
        
        # 1. Collect locks needed (from txn metadata)
        lock_table = {}
        for i, txn in enumerate(txns):
            for key in txn["read_set"] + txn["write_set"]:
                if key not in lock_table:
                    lock_table[key] = []
                lock_table[key].append(i)
        
        # 2. Acquire locks in sequence order (no deadlocks!)
        for txn_idx in range(len(txns)):
            txn = txns[txn_idx]
            for key in txn["read_set"] + txn["write_set"]:
                self.acquire_lock(key, txn_idx)
        
        # 3. Execute transactions in order
        for txn_idx in range(len(txns)):
            txn = txns[txn_idx]
            self.execute_txn(txn)
        
        # 4. Release locks
        for txn_idx in range(len(txns)):
            txn = txns[txn_idx]
            for key in txn["read_set"] + txn["write_set"]:
                self.release_lock(key, txn_idx)
    
    def execute_txn(self, txn):
        """Execute single transaction deterministically"""
        
        # Read phase
        reads = {}
        for key in txn["read_set"]:
            reads[key] = self.storage.get(key)
        
        # Execute logic (must be deterministic!)
        writes = txn["logic"](reads)
        
        # Write phase
        for key, value in writes.items():
            self.storage[key] = value


# Example: Transfer money

def transfer_logic(reads):
    """Deterministic transaction logic"""
    alice_balance = reads["alice"]
    bob_balance = reads["bob"]
    
    # Transfer $100
    return {
        "alice": alice_balance - 100,
        "bob": bob_balance + 100
    }

txn = {
    "read_set": ["alice", "bob"],
    "write_set": ["alice", "bob"],
    "logic": transfer_logic
}

# Submit to Calvin
calvin = CalvinNode("node1", sequencer)
calvin.submit_transaction(txn)

# All replicas execute in same order → Same result ✅
# No 2PC needed!
```

### Calvin's Benefits

```
Advantages:
├─ No distributed deadlocks (locks in sequence order)
├─ No 2PC overhead (order determines commit)
├─ Deterministic replicas (easy to debug)
└─ High throughput (batch transactions)

Disadvantages:
├─ Requires read/write sets upfront (not all apps can provide)
├─ Aborts expensive (must re-sequence)
├─ Multi-partition transactions still slow (lock contention)
└─ Not suitable for interactive transactions (unknown read set)
```

### Calvin's Impact

```
Inspired:
├─ FaunaDB (Calvin-based commercial database)
├─ Deterministic databases (VoltDB)
└─ Research on determinism vs coordination

Key insight:
├─ Determinism eliminates coordination overhead
├─ Pre-ordering transactions = strong consistency without 2PC
└─ Trade-off: Need to know read/write sets upfront
```

---

## 8. Bonus Papers

### 8.1 MapReduce (Google, 2004)

**Link:** https://research.google/pubs/pub62/

**Impact:** Started big data revolution, inspired Hadoop

### 8.2 BigTable (Google, 2006)

**Link:** https://research.google/pubs/pub27898/

**Impact:** Wide-column store, inspired HBase, Cassandra

### 8.3 Kafka (LinkedIn, 2011)

**Link:** https://www.confluent.io/blog/event-streaming-platform-1/

**Impact:** Distributed log, unified streaming platform

### 8.4 Chandy-Lamport Snapshot (1985)

**Link:** https://www.microsoft.com/en-us/research/publication/distributed-snapshots-determining-global-states-distributed-system/

**Impact:** Foundation for Flink savepoints, distributed debugging

---

## 🎯 Reading Guide

```
Essential (must-read):
├─ Lamport's Time & Clocks (foundational)
├─ FLP Impossibility (know the limits)
├─ Paxos Made Simple (consensus gold standard)
├─ Raft (modern consensus, easier to implement)
└─ Spanner (state-of-the-art distributed database)

Important (should-read):
├─ Dynamo (eventual consistency, influenced NoSQL)
├─ Calvin (deterministic transactions)
└─ Chandy-Lamport (distributed snapshots)

Nice-to-have:
├─ MapReduce (historical context)
├─ BigTable (wide-column stores)
└─ Kafka (distributed logs)
```

---

## ✅ Reading Checklist

- [ ] Lamport's Time & Clocks (understand happened-before, logical clocks)
- [ ] FLP Impossibility (know why consensus is "impossible")
- [ ] Paxos Made Simple (understand consensus algorithm)
- [ ] Dynamo (eventual consistency, vector clocks, quorums)
- [ ] Raft (modern consensus, compare with Paxos)
- [ ] Spanner (TrueTime, external consistency, commit wait)
- [ ] Calvin (deterministic execution, no 2PC)

---

**Next:** [README.md](README.md) — Module overview, learning path, capstone project.
