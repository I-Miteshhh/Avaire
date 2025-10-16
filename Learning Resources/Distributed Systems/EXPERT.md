# Distributed Systems - EXPERT

**Learning Time:** 4-6 weeks  
**Prerequisites:** BEGINNER.md + INTERMEDIATE.md completed  
**Difficulty:** Expert → Advanced algorithms for production distributed systems

---

## 📚 Table of Contents

1. [Distributed Transactions](#distributed-transactions)
2. [Two-Phase Commit (2PC)](#two-phase-commit-2pc)
3. [Three-Phase Commit (3PC)](#three-phase-commit-3pc)
4. [Spanner: Google's Globally Distributed Database](#spanner-googles-globally-distributed-database)
5. [Conflict-Free Replicated Data Types (CRDTs)](#conflict-free-replicated-data-types-crdts)
6. [Gossip Protocols](#gossip-protocols)
7. [Distributed Snapshots](#distributed-snapshots)
8. [Advanced Consensus Algorithms](#advanced-consensus-algorithms)
9. [Byzantine Fault Tolerance](#byzantine-fault-tolerance)
10. [System Design Case Studies](#system-design-case-studies)

---

## 1. Distributed Transactions

### The ACID Problem in Distributed Systems

```
Single-node transaction (easy):
BEGIN TRANSACTION
  UPDATE account1 SET balance = balance - 100
  UPDATE account2 SET balance = balance + 100
COMMIT  ← Atomic: Both updates succeed or both fail

Distributed transaction (hard):
BEGIN TRANSACTION
  UPDATE db1.account1 SET balance = balance - 100  ← Node 1
  UPDATE db2.account2 SET balance = balance + 100  ← Node 2
COMMIT  ← How to ensure atomicity across nodes?
```

**Challenges:**
1. **Atomicity:** All nodes commit or all abort
2. **Network failures:** Node might commit but message lost
3. **Node failures:** Node crashes after voting yes
4. **Blocking:** Transaction holds locks, waiting for coordinator

---

## 2. Two-Phase Commit (2PC)

**Goal:** Atomic commitment across multiple nodes.

### 2PC Protocol

```
Roles:
├─ Coordinator: Orchestrates transaction
└─ Participants: Execute transaction locally

┌─────────────────────────────────────────────────────────┐
│ Phase 1: Voting (Prepare)                              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Coordinator → Participants: PREPARE(txn_id)            │
│                                                         │
│ Each Participant:                                       │
│ ├─ Execute transaction locally (no commit yet)         │
│ ├─ Write PREPARE record to log (WAL)                   │
│ ├─ Acquire locks                                        │
│ └─ Vote: YES (can commit) or NO (must abort)           │
│                                                         │
│ Participants → Coordinator: VOTE(YES/NO)               │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Phase 2: Decision (Commit/Abort)                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Coordinator decides:                                    │
│ ├─ ALL voted YES → COMMIT                              │
│ └─ ANY voted NO → ABORT                                │
│                                                         │
│ Coordinator → Participants: COMMIT or ABORT            │
│                                                         │
│ Each Participant:                                       │
│ ├─ Write COMMIT/ABORT record to log                    │
│ ├─ Execute commit/abort                                 │
│ ├─ Release locks                                        │
│ └─ Send ACK to coordinator                             │
│                                                         │
│ Coordinator: Wait for all ACKs, transaction complete   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2PC Implementation

```python
import enum
import time
from typing import List, Dict

class TxnState(enum.Enum):
    INIT = 1
    PREPARING = 2
    PREPARED = 3
    COMMITTING = 4
    COMMITTED = 5
    ABORTED = 6

class TwoPhaseCommitCoordinator:
    def __init__(self, txn_id: str, participants: List):
        self.txn_id = txn_id
        self.participants = participants
        self.state = TxnState.INIT
        self.votes: Dict[str, bool] = {}
        self.wal = []  # Write-Ahead Log
    
    def execute_transaction(self, operations: Dict):
        """Execute distributed transaction using 2PC"""
        
        # Phase 1: Prepare
        print(f"[Coordinator] Starting transaction {self.txn_id}")
        self.state = TxnState.PREPARING
        self.log_event("PREPARE", {"operations": operations})
        
        # Send PREPARE to all participants
        for participant_id, participant in self.participants.items():
            try:
                vote = participant.prepare(self.txn_id, operations.get(participant_id))
                self.votes[participant_id] = vote
                print(f"[Coordinator] {participant_id} voted: {'YES' if vote else 'NO'}")
            except Exception as e:
                print(f"[Coordinator] {participant_id} failed to respond: {e}")
                self.votes[participant_id] = False
        
        # Decide: ALL yes → commit, ANY no → abort
        decision = all(self.votes.values())
        
        if decision:
            return self.commit()
        else:
            return self.abort()
    
    def commit(self):
        """Phase 2: Commit"""
        print(f"[Coordinator] Decision: COMMIT")
        self.state = TxnState.COMMITTING
        self.log_event("COMMIT", {})
        
        # Send COMMIT to all participants
        acks = {}
        for participant_id, participant in self.participants.items():
            try:
                ack = participant.commit(self.txn_id)
                acks[participant_id] = ack
                print(f"[Coordinator] {participant_id} committed: {ack}")
            except Exception as e:
                print(f"[Coordinator] {participant_id} failed to commit: {e}")
                # Retry indefinitely until success (blocking!)
                while participant_id not in acks or not acks[participant_id]:
                    time.sleep(1)
                    try:
                        acks[participant_id] = participant.commit(self.txn_id)
                    except:
                        pass
        
        self.state = TxnState.COMMITTED
        self.log_event("COMMITTED", {})
        print(f"[Coordinator] Transaction {self.txn_id} COMMITTED")
        return True
    
    def abort(self):
        """Phase 2: Abort"""
        print(f"[Coordinator] Decision: ABORT")
        self.state = TxnState.ABORTED
        self.log_event("ABORT", {})
        
        # Send ABORT to all participants
        for participant_id, participant in self.participants.items():
            try:
                participant.abort(self.txn_id)
                print(f"[Coordinator] {participant_id} aborted")
            except Exception as e:
                print(f"[Coordinator] {participant_id} failed to abort: {e}")
        
        print(f"[Coordinator] Transaction {self.txn_id} ABORTED")
        return False
    
    def log_event(self, event: str, data: Dict):
        """Write to Write-Ahead Log"""
        self.wal.append({
            "txn_id": self.txn_id,
            "event": event,
            "timestamp": time.time(),
            "data": data
        })


class TwoPhaseCommitParticipant:
    def __init__(self, participant_id: str):
        self.participant_id = participant_id
        self.transactions: Dict[str, Dict] = {}  # txn_id → state
        self.data: Dict[str, int] = {}  # Local database
        self.wal = []
    
    def prepare(self, txn_id: str, operations: List) -> bool:
        """Phase 1: Prepare to commit"""
        print(f"[{self.participant_id}] PREPARE {txn_id}")
        
        try:
            # Simulate executing transaction (without committing)
            tentative_data = self.data.copy()
            for op in operations:
                if op["type"] == "UPDATE":
                    key, value = op["key"], op["value"]
                    tentative_data[key] = value
            
            # Save tentative state
            self.transactions[txn_id] = {
                "state": TxnState.PREPARED,
                "tentative_data": tentative_data,
                "operations": operations
            }
            
            # Write PREPARE to WAL
            self.log_event("PREPARE", {"txn_id": txn_id})
            
            # Vote YES
            print(f"[{self.participant_id}] Voting YES for {txn_id}")
            return True
        
        except Exception as e:
            print(f"[{self.participant_id}] Voting NO for {txn_id}: {e}")
            return False
    
    def commit(self, txn_id: str) -> bool:
        """Phase 2: Commit transaction"""
        print(f"[{self.participant_id}] COMMIT {txn_id}")
        
        if txn_id not in self.transactions:
            raise Exception(f"Transaction {txn_id} not found")
        
        txn = self.transactions[txn_id]
        
        # Apply tentative changes
        self.data = txn["tentative_data"]
        txn["state"] = TxnState.COMMITTED
        
        # Write COMMIT to WAL
        self.log_event("COMMIT", {"txn_id": txn_id})
        
        print(f"[{self.participant_id}] Committed {txn_id}")
        return True
    
    def abort(self, txn_id: str) -> bool:
        """Phase 2: Abort transaction"""
        print(f"[{self.participant_id}] ABORT {txn_id}")
        
        if txn_id in self.transactions:
            self.transactions[txn_id]["state"] = TxnState.ABORTED
            self.log_event("ABORT", {"txn_id": txn_id})
        
        print(f"[{self.participant_id}] Aborted {txn_id}")
        return True
    
    def log_event(self, event: str, data: Dict):
        self.wal.append({
            "event": event,
            "timestamp": time.time(),
            "data": data
        })


# Example: Distributed money transfer
participant1 = TwoPhaseCommitParticipant("DB1")
participant2 = TwoPhaseCommitParticipant("DB2")

# Initialize data
participant1.data = {"alice": 1000}
participant2.data = {"bob": 500}

# Coordinator
coordinator = TwoPhaseCommitCoordinator(
    txn_id="txn_001",
    participants={"DB1": participant1, "DB2": participant2}
)

# Transaction: Transfer $100 from Alice to Bob
operations = {
    "DB1": [{"type": "UPDATE", "key": "alice", "value": 900}],
    "DB2": [{"type": "UPDATE", "key": "bob", "value": 600}]
}

success = coordinator.execute_transaction(operations)

print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
print(f"Alice balance: {participant1.data.get('alice')}")  # 900
print(f"Bob balance: {participant2.data.get('bob')}")      # 600
```

### 2PC Problems

```
┌─────────────────────────────────────────────────────────┐
│ Problem 1: Blocking                                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Scenario: Coordinator crashes after PREPARE            │
│                                                         │
│ Participants:                                           │
│ ├─ Voted YES                                            │
│ ├─ Holding locks                                        │
│ ├─ Waiting for decision (COMMIT/ABORT)                 │
│ └─ Cannot unilaterally abort! ❌ (Might violate atomicity)│
│                                                         │
│ Result: System BLOCKED until coordinator recovers      │
│ ├─ Locks held indefinitely                             │
│ ├─ Other transactions wait                              │
│ └─ Poor availability ❌                                 │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Problem 2: Single Point of Failure                     │
├─────────────────────────────────────────────────────────┤
│ Coordinator crash → Entire system blocked              │
│ Solution: Replicate coordinator (adds complexity)      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Problem 3: High Latency                                │
├─────────────────────────────────────────────────────────┤
│ Two round trips:                                        │
│ ├─ PREPARE → VOTE (round 1)                            │
│ └─ COMMIT → ACK (round 2)                               │
│                                                         │
│ With 3 participants across 3 continents:                │
│ ├─ Round 1: 150ms                                       │
│ ├─ Round 2: 150ms                                       │
│ └─ Total: 300ms ❌ (Too slow for interactive apps)     │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Three-Phase Commit (3PC)

**Goal:** Non-blocking atomic commitment (fix 2PC blocking problem).

### 3PC Protocol

```
Phase 1: CanCommit (like 2PC Prepare)
├─ Coordinator → Participants: CAN_COMMIT?
└─ Participants → Coordinator: YES/NO

Phase 2: PreCommit (NEW!)
├─ If ALL voted YES:
│  ├─ Coordinator → Participants: PRE_COMMIT
│  ├─ Participants: Write PRE_COMMIT to log
│  └─ Participants → Coordinator: ACK
├─ If ANY voted NO:
│  └─ Coordinator → Participants: ABORT

Phase 3: DoCommit
├─ Coordinator → Participants: DO_COMMIT
├─ Participants: Commit transaction
└─ Participants → Coordinator: ACK
```

**Key insight:** After PRE_COMMIT, participants know:
- All participants voted YES
- Coordinator decided to commit
- Can unilaterally commit if coordinator crashes

### 3PC vs 2PC

```
┌─────────────────────────────────────────────────────────┐
│ 2PC:                                                    │
│ ├─ PREPARE → Vote                                       │
│ └─ COMMIT/ABORT                                         │
│                                                         │
│ Problem: After voting YES, participant doesn't know if │
│ others voted YES → Cannot safely commit/abort alone    │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 3PC:                                                    │
│ ├─ CAN_COMMIT → Vote                                    │
│ ├─ PRE_COMMIT (NEW: Tells participant "all voted YES") │
│ └─ DO_COMMIT                                            │
│                                                         │
│ After PRE_COMMIT: Participant knows everyone agreed    │
│ → Can commit even if coordinator crashes ✅            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3PC Limitations

```
3PC is non-blocking in asynchronous networks BUT:

Problem: Network partitions
├─ Partition separates participants into two groups
├─ Both groups might make different decisions
└─ Violates safety! ❌

Example:
├─ Participants: {A, B, C}
├─ Network partition: {A, B} | {C}
├─ A, B receive PRE_COMMIT → Commit
├─ C doesn't receive PRE_COMMIT → Times out, aborts
└─ Inconsistency! A, B committed but C aborted

Reality: 3PC rarely used in practice
├─ 2PC: Simple, works if coordinator is reliable
└─ Consensus (Paxos/Raft): Better fault tolerance
```

---

## 4. Spanner: Google's Globally Distributed Database

**Paper:** "Spanner: Google's Globally-Distributed Database" (OSDI 2012)

### The Challenge

```
Goal: Distributed SQL database with:
├─ Global distribution (replicate across continents)
├─ External consistency (linearizability)
├─ High availability (survive data center failures)
└─ SQL support (ACID transactions)

Problem: How to order transactions across data centers?
├─ Clock skew: Servers have different times
├─ Network delays: Messages take 50-150ms between continents
└─ Causality: Need to respect "happens-before"
```

### TrueTime: Google's Solution

```
TrueTime API:
├─ TT.now() → Returns interval [earliest, latest]
├─ TT.after(t) → True if t is definitely in the past
└─ TT.before(t) → True if t is definitely in the future

Example:
Server 1: TT.now() = [10:00:00.001, 10:00:00.007]  (6ms uncertainty)
Server 2: TT.now() = [10:00:00.003, 10:00:00.009]  (6ms uncertainty)

Implementation:
├─ GPS receivers + atomic clocks in each data center
├─ Uncertainty bound: ε ≈ 1-7 milliseconds
└─ Synchronized across globe
```

### Spanner Transaction Protocol

```python
class TrueTime:
    """Simulated TrueTime API"""
    
    def __init__(self, uncertainty_ms=7):
        self.uncertainty_ms = uncertainty_ms
    
    def now(self):
        """Returns interval [earliest, latest]"""
        current_time = time.time() * 1000  # ms
        epsilon = self.uncertainty_ms
        return {
            "earliest": current_time - epsilon,
            "latest": current_time + epsilon
        }
    
    def after(self, timestamp):
        """True if timestamp is definitely in the past"""
        interval = self.now()
        return timestamp < interval["earliest"]
    
    def before(self, timestamp):
        """True if timestamp is definitely in the future"""
        interval = self.now()
        return timestamp > interval["latest"]


class SpannerTransaction:
    def __init__(self, node_id, true_time):
        self.node_id = node_id
        self.true_time = true_time
        self.data = {}
    
    def read_write_transaction(self, operations):
        """Execute read-write transaction"""
        
        # Step 1: Execute operations, acquire locks
        start_interval = self.true_time.now()
        
        for op in operations:
            if op["type"] == "READ":
                value = self.data.get(op["key"])
            elif op["type"] == "WRITE":
                self.data[op["key"]] = op["value"]
        
        # Step 2: Prepare timestamp (2PC prepare phase)
        # Choose commit timestamp s within start interval
        commit_ts = start_interval["latest"]
        
        # Step 3: Wait until commit_ts is in the past (Commit Wait)
        print(f"[{self.node_id}] Commit timestamp: {commit_ts}")
        while not self.true_time.after(commit_ts):
            time.sleep(0.001)  # Wait for uncertainty to pass
            print(f"[{self.node_id}] Waiting for commit timestamp to be in past...")
        
        # Step 4: Commit (2PC commit phase)
        print(f"[{self.node_id}] Transaction committed at {commit_ts}")
        return commit_ts
    
    def read_only_transaction(self, timestamp, keys):
        """Read-only transaction at given timestamp"""
        # No locks, no 2PC needed!
        # Just read data as of timestamp
        results = {}
        for key in keys:
            results[key] = self.data.get(key)
        return results


# Example: External consistency

tt = TrueTime(uncertainty_ms=7)

txn1 = SpannerTransaction("DC1", tt)
txn2 = SpannerTransaction("DC2", tt)

# Transaction 1: Write x = 5
print("=== Transaction 1 ===")
ts1 = txn1.read_write_transaction([
    {"type": "WRITE", "key": "x", "value": 5}
])

# Wait a bit (simulate network delay)
time.sleep(0.01)

# Transaction 2: Write y = 10 (started after txn1 committed)
print("\n=== Transaction 2 ===")
ts2 = txn2.read_write_transaction([
    {"type": "WRITE", "key": "y", "value": 10}
])

# Property: ts1 < ts2 (external consistency)
print(f"\nTimestamps: txn1={ts1:.3f}, txn2={ts2:.3f}")
print(f"External consistency: {ts1 < ts2}")  # True!
```

### Spanner's Commit Wait

```
Key Innovation: Wait out uncertainty before committing

┌─────────────────────────────────────────────────────────┐
│ Without Commit Wait (broken):                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ T1: Server A commits with timestamp 10:00:00.005       │
│ T2: Client notified "SUCCESS"                          │
│ T3: Client → Server B: Start transaction 2             │
│ T4: Server B's clock shows 10:00:00.003 (behind!)      │
│ T5: Transaction 2 gets timestamp 10:00:00.003          │
│                                                         │
│ Result: ts(txn2) < ts(txn1) ❌                         │
│ Violates external consistency!                         │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ With Commit Wait (correct):                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ T1: Server A prepares with timestamp 10:00:00.005      │
│ T2: Server A WAITS until 10:00:00.005 is in past       │
│     (Waits ε = 7ms for uncertainty)                    │
│ T3: Server A commits, client notified "SUCCESS"        │
│ T4: Client → Server B: Start transaction 2             │
│ T5: Server B's clock shows ≥ 10:00:00.012 (caught up) │
│ T6: Transaction 2 gets timestamp ≥ 10:00:00.012        │
│                                                         │
│ Result: ts(txn2) > ts(txn1) ✅                         │
│ External consistency guaranteed!                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Cost:** Every transaction pays ~7ms commit wait latency.

**Trade-off:** Acceptable for Google's use case (strong consistency > low latency).

---

## 5. Conflict-Free Replicated Data Types (CRDTs)

**Goal:** Replicas can update independently and always converge (no conflicts).

### CRDT Properties

```
Strong Eventual Consistency (SEC):
├─ Eventual delivery: All updates eventually reach all replicas
├─ Convergence: Replicas with same updates have same state
└─ No conflicts: Concurrent updates merge automatically
```

### CRDT Types

#### 1. G-Counter (Grow-only Counter)

```python
class GCounter:
    """Grow-only counter (can only increment)"""
    
    def __init__(self, node_id, num_nodes):
        self.node_id = node_id
        self.counts = [0] * num_nodes  # One counter per node
    
    def increment(self):
        """Increment local counter"""
        self.counts[self.node_id] += 1
    
    def value(self):
        """Get total count (sum of all node counters)"""
        return sum(self.counts)
    
    def merge(self, other):
        """Merge with another replica"""
        for i in range(len(self.counts)):
            self.counts[i] = max(self.counts[i], other.counts[i])


# Example: Distributed like counter
replica1 = GCounter(node_id=0, num_nodes=3)
replica2 = GCounter(node_id=1, num_nodes=3)
replica3 = GCounter(node_id=2, num_nodes=3)

# Concurrent increments
replica1.increment()  # counts = [1, 0, 0]
replica1.increment()  # counts = [2, 0, 0]
replica2.increment()  # counts = [0, 1, 0]
replica3.increment()  # counts = [0, 0, 1]

# Replicas sync (order doesn't matter!)
replica1.merge(replica2)  # [2, 1, 0]
replica1.merge(replica3)  # [2, 1, 1]

replica2.merge(replica1)  # [2, 1, 1]
replica2.merge(replica3)  # [2, 1, 1]

replica3.merge(replica1)  # [2, 1, 1]
replica3.merge(replica2)  # [2, 1, 1]

# All replicas converge to same value ✅
print(replica1.value())  # 4
print(replica2.value())  # 4
print(replica3.value())  # 4
```

#### 2. PN-Counter (Positive-Negative Counter)

```python
class PNCounter:
    """Counter that can increment and decrement"""
    
    def __init__(self, node_id, num_nodes):
        self.node_id = node_id
        self.increments = GCounter(node_id, num_nodes)
        self.decrements = GCounter(node_id, num_nodes)
    
    def increment(self):
        self.increments.increment()
    
    def decrement(self):
        self.decrements.increment()  # Decrement = increment in decrements counter
    
    def value(self):
        return self.increments.value() - self.decrements.value()
    
    def merge(self, other):
        self.increments.merge(other.increments)
        self.decrements.merge(other.decrements)


# Example
counter1 = PNCounter(node_id=0, num_nodes=2)
counter2 = PNCounter(node_id=1, num_nodes=2)

counter1.increment()  # +1
counter1.increment()  # +1
counter2.decrement()  # -1

counter1.merge(counter2)
counter2.merge(counter1)

print(counter1.value())  # 1 (2 - 1)
print(counter2.value())  # 1 ✅ Converged!
```

#### 3. LWW-Element-Set (Last-Write-Wins Set)

```python
class LWWElementSet:
    """Set where add/remove use timestamps, last write wins"""
    
    def __init__(self):
        self.add_set = {}  # element → timestamp
        self.remove_set = {}  # element → timestamp
    
    def add(self, element):
        """Add element with current timestamp"""
        self.add_set[element] = time.time()
    
    def remove(self, element):
        """Remove element with current timestamp"""
        self.remove_set[element] = time.time()
    
    def contains(self, element):
        """Element exists if:
        - Added, AND
        - Not removed OR add timestamp > remove timestamp
        """
        if element not in self.add_set:
            return False
        
        add_ts = self.add_set[element]
        remove_ts = self.remove_set.get(element, 0)
        
        return add_ts > remove_ts  # Bias towards add
    
    def merge(self, other):
        """Merge with another replica"""
        # Merge add_set (keep max timestamp)
        for element, ts in other.add_set.items():
            if element not in self.add_set or ts > self.add_set[element]:
                self.add_set[element] = ts
        
        # Merge remove_set (keep max timestamp)
        for element, ts in other.remove_set.items():
            if element not in self.remove_set or ts > self.remove_set[element]:
                self.remove_set[element] = ts


# Example: Collaborative shopping cart
cart1 = LWWElementSet()
cart2 = LWWElementSet()

# User 1 adds item
cart1.add("apple")
time.sleep(0.01)

# User 2 removes item (concurrent)
cart2.remove("apple")

# Replicas sync
cart1.merge(cart2)
cart2.merge(cart1)

# Last write wins
print(cart1.contains("apple"))  # False (remove timestamp > add timestamp)
print(cart2.contains("apple"))  # False ✅ Converged!
```

#### 4. OR-Set (Observed-Remove Set)

```python
class ORSet:
    """Set where remove only affects observed adds"""
    
    def __init__(self):
        self.elements = {}  # element → set of unique tags
    
    def add(self, element):
        """Add element with unique tag"""
        tag = (time.time(), id(self))  # Unique per operation
        if element not in self.elements:
            self.elements[element] = set()
        self.elements[element].add(tag)
    
    def remove(self, element):
        """Remove all observed tags for element"""
        if element in self.elements:
            self.elements[element] = set()  # Remove all tags
    
    def contains(self, element):
        """Element exists if it has any tags"""
        return element in self.elements and len(self.elements[element]) > 0
    
    def merge(self, other):
        """Merge: Union of tags"""
        for element, tags in other.elements.items():
            if element not in self.elements:
                self.elements[element] = set()
            self.elements[element] = self.elements[element].union(tags)


# Example: Concurrent add/remove
set1 = ORSet()
set2 = ORSet()

# Replica 1: Add "apple"
set1.add("apple")  # tag = (t1, id1)

# Sync
set2.merge(set1)

# Replica 2: Remove "apple" (observed add)
set2.remove("apple")  # Removes tag (t1, id1)

# Replica 1: Add "apple" again (concurrent with remove)
set1.add("apple")  # tag = (t2, id2) ← NEW tag!

# Sync
set1.merge(set2)
set2.merge(set1)

# "apple" still in set (new add not observed by remove) ✅
print(set1.contains("apple"))  # True
print(set2.contains("apple"))  # True
```

### CRDTs in Production

```
Use Cases:
├─ Redis CRDTs: Multi-region replication
├─ Riak: Shopping carts, session storage
├─ Akka: Distributed data (cluster sharding)
└─ TiKV: Conflict-free multi-region writes

Trade-offs:
✅ No coordination needed (low latency, high availability)
✅ Automatic conflict resolution
❌ Limited operations (can't do arbitrary transactions)
❌ Metadata overhead (vector clocks, timestamps)
```

---

## 6. Gossip Protocols

**Goal:** Disseminate information efficiently in large clusters.

### Gossip Algorithm

```python
import random
import time
from typing import Set, Dict

class GossipNode:
    def __init__(self, node_id: str, peers: Set[str]):
        self.node_id = node_id
        self.peers = peers
        self.data: Dict[str, any] = {}  # key → value
        self.versions: Dict[str, int] = {}  # key → version
    
    def update(self, key: str, value: any):
        """Local update"""
        self.versions[key] = self.versions.get(key, 0) + 1
        self.data[key] = value
        print(f"[{self.node_id}] Updated {key} = {value} (v{self.versions[key]})")
    
    def gossip_round(self):
        """Periodically gossip with random peer"""
        if not self.peers:
            return
        
        # Pick random peer
        peer = random.choice(list(self.peers))
        
        # Send digest (key → version)
        digest = {key: ver for key, ver in self.versions.items()}
        
        # Peer responds with missing/newer data
        peer_updates = peer.receive_gossip(digest)
        
        # Merge peer's updates
        for key, (value, version) in peer_updates.items():
            if key not in self.versions or version > self.versions[key]:
                self.data[key] = value
                self.versions[key] = version
                print(f"[{self.node_id}] Learned {key} = {value} (v{version}) from {peer.node_id}")
    
    def receive_gossip(self, peer_digest: Dict[str, int]) -> Dict:
        """Handle gossip from peer"""
        updates = {}
        
        # Send data peer is missing or has older version
        for key, version in self.versions.items():
            peer_version = peer_digest.get(key, 0)
            if version > peer_version:
                updates[key] = (self.data[key], version)
        
        return updates
    
    def run(self, rounds=10):
        """Run gossip protocol"""
        for i in range(rounds):
            self.gossip_round()
            time.sleep(0.1)


# Example: Cluster membership
node1 = GossipNode("node1", set())
node2 = GossipNode("node2", set())
node3 = GossipNode("node3", set())

# Connect nodes
node1.peers = {node2, node3}
node2.peers = {node1, node3}
node3.peers = {node1, node2}

# Node 1 updates
node1.update("status", "healthy")

# Gossip spreads update
for _ in range(5):
    node1.gossip_round()
    node2.gossip_round()
    node3.gossip_round()
    time.sleep(0.1)

# All nodes eventually learn the update
print(f"\nFinal state:")
print(f"Node 1: {node1.data}")
print(f"Node 2: {node2.data}")  # Learned from node 1
print(f"Node 3: {node3.data}")  # Learned from node 1 or 2
```

### Gossip Properties

```
Scalability:
├─ Each node contacts O(log N) nodes per round
├─ Entire cluster learns update in O(log N) rounds
└─ Exponential spread (1 → 2 → 4 → 8 → 16...)

Fault Tolerance:
├─ Works even if 50% of nodes fail
├─ No single point of failure
└─ Self-healing (nodes rejoin automatically)

Trade-offs:
✅ Highly available
✅ Eventually consistent
✅ Simple to implement
❌ High network bandwidth (redundant messages)
❌ Eventual (not immediate) propagation
```

### Gossip Use Cases

```
1. Cluster Membership (Cassandra, Consul)
   ├─ Nodes gossip "I'm alive"
   └─ Failure detection (no gossip = node down)

2. Anti-Entropy (Dynamo)
   ├─ Replicas gossip key-value pairs
   └─ Repair inconsistencies

3. Aggregate Computation
   ├─ Gossip local metrics (CPU, memory)
   └─ Compute global average

4. Rumor Spreading
   ├─ Broadcast events to cluster
   └─ Example: Configuration updates
```

---

## 7. Distributed Snapshots

**Goal:** Capture consistent global state of distributed system.

### Chandy-Lamport Algorithm

```python
from collections import defaultdict
from queue import Queue

class ChannelState:
    """Communication channel between two processes"""
    def __init__(self):
        self.messages = Queue()
        self.recorded_messages = []
        self.recording = False
    
    def send(self, message):
        self.messages.put(message)
    
    def receive(self):
        if self.messages.empty():
            return None
        return self.messages.get()
    
    def start_recording(self):
        self.recording = True
        self.recorded_messages = []
    
    def stop_recording(self):
        self.recording = False
    
    def record_if_needed(self, message):
        if self.recording:
            self.recorded_messages.append(message)


class DistributedProcess:
    def __init__(self, process_id, neighbors):
        self.process_id = process_id
        self.neighbors = neighbors  # neighbor_id → channel
        self.state = {"balance": 0}
        
        # Snapshot state
        self.snapshot_taken = False
        self.snapshot_state = None
        self.markers_received = set()
    
    def local_event(self, delta):
        """Local state change"""
        self.state["balance"] += delta
        print(f"[{self.process_id}] Balance: {self.state['balance']}")
    
    def send_message(self, to_process, message):
        """Send message to neighbor"""
        channel = self.neighbors[to_process]
        channel.send(message)
    
    def initiate_snapshot(self):
        """Initiate snapshot (marker protocol)"""
        print(f"[{self.process_id}] Initiating snapshot")
        
        # Record local state
        self.snapshot_state = self.state.copy()
        self.snapshot_taken = True
        
        # Send markers to all outgoing channels
        for neighbor_id in self.neighbors:
            self.send_message(neighbor_id, {"type": "MARKER"})
        
        # Start recording incoming channels
        for channel in self.neighbors.values():
            channel.start_recording()
    
    def receive_marker(self, from_process):
        """Receive marker from neighbor"""
        print(f"[{self.process_id}] Received marker from {from_process}")
        
        channel = self.neighbors[from_process]
        
        if not self.snapshot_taken:
            # First marker received
            # Record local state
            self.snapshot_state = self.state.copy()
            self.snapshot_taken = True
            
            # Mark channel from sender as empty
            channel.stop_recording()
            
            # Send markers to all other channels
            for neighbor_id in self.neighbors:
                if neighbor_id != from_process:
                    self.send_message(neighbor_id, {"type": "MARKER"})
            
            # Start recording all other channels
            for other_id, other_channel in self.neighbors.items():
                if other_id != from_process:
                    other_channel.start_recording()
        else:
            # Already taken snapshot
            # Stop recording this channel
            channel.stop_recording()
        
        self.markers_received.add(from_process)
        
        # Check if snapshot complete
        if len(self.markers_received) == len(self.neighbors):
            self.snapshot_complete()
    
    def snapshot_complete(self):
        """Snapshot complete, collect channel states"""
        print(f"\n[{self.process_id}] Snapshot complete:")
        print(f"  Local state: {self.snapshot_state}")
        for neighbor_id, channel in self.neighbors.items():
            print(f"  Channel from {neighbor_id}: {channel.recorded_messages}")


# Example: Distributed banking system
# Process 1 ⇄ Process 2 ⇄ Process 3

# Create channels
ch_1_to_2 = ChannelState()
ch_2_to_1 = ChannelState()
ch_2_to_3 = ChannelState()
ch_3_to_2 = ChannelState()

# Create processes
p1 = DistributedProcess("P1", {"P2": ch_1_to_2})
p2 = DistributedProcess("P2", {"P1": ch_2_to_1, "P3": ch_2_to_3})
p3 = DistributedProcess("P3", {"P2": ch_3_to_2})

# Initial state
p1.state["balance"] = 1000
p2.state["balance"] = 2000
p3.state["balance"] = 3000

# Events happen
p1.send_message("P2", {"type": "TRANSFER", "amount": 100})
p1.local_event(-100)

# P1 initiates snapshot
p1.initiate_snapshot()

# P2 receives marker
p2.receive_marker("P1")

# More events after snapshot started
p2.local_event(100)  # Receive transfer from P1
p2.send_message("P3", {"type": "TRANSFER", "amount": 50})
p2.local_event(-50)

# P2 sends marker to P3
# P3 receives marker
p3.receive_marker("P2")

# P3 sends marker back to P2
p2.receive_marker("P3")
```

### Snapshot Use Cases

```
1. Checkpointing
   ├─ Save distributed state for recovery
   └─ Example: Flink savepoints

2. Deadlock Detection
   ├─ Capture wait-for graph
   └─ Check for cycles

3. Debugging
   ├─ Capture global state for analysis
   └─ Reproduce bugs

4. Monitoring
   ├─ Calculate global metrics (total balance)
   └─ Detect anomalies
```

---

## 8. Advanced Consensus Algorithms

### Multi-Paxos

**Goal:** Optimize Paxos for multiple decisions (log of values, not single value).

```python
class MultiPaxos:
    """Optimized Paxos for log replication"""
    
    def __init__(self, node_id, peers):
        self.node_id = node_id
        self.peers = peers
        self.log = []  # Sequence of decided values
        self.leader = None
        self.proposal_number = 0
    
    def elect_leader(self):
        """Phase 1: Leader election (run once)"""
        self.proposal_number += 1
        
        # Send PREPARE for entire log
        promises = []
        for peer in self.peers:
            promise = peer.prepare(self.proposal_number)
            if promise:
                promises.append(promise)
        
        # Majority?
        if len(promises) > len(self.peers) // 2:
            self.leader = self.node_id
            return True
        return False
    
    def append(self, value):
        """Append value to log (skip Phase 1 if leader)"""
        if self.leader != self.node_id:
            raise Exception("Not leader")
        
        slot = len(self.log)
        
        # Phase 2: Accept (no prepare needed, already leader!)
        accepts = 0
        for peer in self.peers:
            if peer.accept(slot, self.proposal_number, value):
                accepts += 1
        
        # Majority?
        if accepts > len(self.peers) // 2:
            self.log.append(value)
            return True
        return False


# Optimization: Leader sends ACCEPT directly (skips PREPARE)
# Result: 1 round trip instead of 2 ✅
```

### EPaxos (Egalitarian Paxos)

**Key idea:** No single leader, any node can propose.

```
Benefits:
├─ Lower latency (no need to forward to leader)
├─ Better load distribution
└─ Tolerates slow leaders

Challenge: Ordering conflicts
├─ Concurrent proposals might conflict
└─ Need to establish dependencies
```

### Flexible Paxos

**Key idea:** Relax quorum requirements.

```
Classic Paxos: Q1 ∩ Q2 ≠ ∅
├─ Prepare quorum: Q1
├─ Accept quorum: Q2
└─ Requirement: Q1 + Q2 > N

Flexible Paxos: Only requires Q1 ∩ Q2 ≠ ∅
├─ Example: N=5, Q1=2, Q2=4
├─ Faster prepares (need only 2 nodes)
└─ Slower accepts (need 4 nodes)

Use case: Optimize for leader election (rare) vs log replication (common)
```

---

## 9. Byzantine Fault Tolerance

**Goal:** Tolerate malicious nodes (not just crashes).

### PBFT (Practical Byzantine Fault Tolerance)

```
Setup:
├─ N = 3f + 1 nodes (tolerate f Byzantine faults)
├─ Example: 4 nodes tolerate 1 Byzantine fault
└─ 1 Primary, 3 Backups

Algorithm (3 phases):

Phase 1: Pre-Prepare
├─ Client → Primary: Request
├─ Primary → Backups: PRE-PREPARE(seq_num, request)
└─ Backups: Validate sequence number

Phase 2: Prepare
├─ Backups → All: PREPARE(seq_num, request)
├─ Wait for 2f PREPARE messages
└─ Ensures all honest nodes agree on order

Phase 3: Commit
├─ Nodes → All: COMMIT(seq_num)
├─ Wait for 2f+1 COMMIT messages
├─ Execute request
└─ Reply to client

Client waits for f+1 matching replies (proves majority honest)
```

```python
class PBFTNode:
    def __init__(self, node_id, is_primary, f):
        self.node_id = node_id
        self.is_primary = is_primary
        self.f = f  # Max Byzantine faults
        self.sequence_number = 0
        self.prepare_messages = {}
        self.commit_messages = {}
    
    def pre_prepare(self, request):
        """Primary sends pre-prepare"""
        if not self.is_primary:
            raise Exception("Only primary can send pre-prepare")
        
        self.sequence_number += 1
        return {
            "type": "PRE-PREPARE",
            "seq": self.sequence_number,
            "request": request,
            "primary": self.node_id
        }
    
    def on_pre_prepare(self, message):
        """Backup receives pre-prepare"""
        seq = message["seq"]
        
        # Validate
        if seq <= self.sequence_number:
            return None  # Old message
        
        self.sequence_number = seq
        
        # Send PREPARE to all
        return {
            "type": "PREPARE",
            "seq": seq,
            "request": message["request"],
            "node": self.node_id
        }
    
    def on_prepare(self, message):
        """Collect PREPARE messages"""
        seq = message["seq"]
        
        if seq not in self.prepare_messages:
            self.prepare_messages[seq] = []
        
        self.prepare_messages[seq].append(message)
        
        # Prepared if 2f PREPARE messages
        if len(self.prepare_messages[seq]) >= 2 * self.f:
            return {
                "type": "COMMIT",
                "seq": seq,
                "request": message["request"],
                "node": self.node_id
            }
        
        return None
    
    def on_commit(self, message):
        """Collect COMMIT messages"""
        seq = message["seq"]
        
        if seq not in self.commit_messages:
            self.commit_messages[seq] = []
        
        self.commit_messages[seq].append(message)
        
        # Committed if 2f+1 COMMIT messages
        if len(self.commit_messages[seq]) >= 2 * self.f + 1:
            return self.execute(message["request"])
        
        return None
    
    def execute(self, request):
        """Execute request"""
        print(f"[{self.node_id}] Executing: {request}")
        return {"result": "SUCCESS"}
```

### HotStuff

**Modern BFT:** Simplified PBFT with linear communication complexity.

```
PBFT: O(N²) messages per consensus
HotStuff: O(N) messages per consensus ✅

Used by:
├─ Libra/Diem (Facebook's blockchain)
└─ Casper (Ethereum 2.0)
```

---

## 🎯 Key Takeaways

1. **2PC is blocking:** Use only with reliable coordinator
2. **Spanner's TrueTime:** Trade latency for strong consistency
3. **CRDTs:** No coordination, but limited operations
4. **Gossip:** Highly available, eventually consistent
5. **Snapshots:** Capture distributed state consistently
6. **Multi-Paxos:** Optimize for common case (leader stable)
7. **PBFT:** 3f+1 nodes tolerate f Byzantine faults

---

## 📚 Further Reading

- **Spanner Paper:** https://research.google/pubs/pub39966/
- **PBFT Paper:** http://pmg.csail.mit.edu/papers/osdi99.pdf
- **CRDTs:** https://crdt.tech/
- **Chandy-Lamport:** https://www.microsoft.com/en-us/research/publication/distributed-snapshots-determining-global-states-distributed-system/

---

**Next:** [WHITEPAPERS.md](WHITEPAPERS.md) — Seminal papers in distributed systems.
