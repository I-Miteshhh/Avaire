# Distributed Systems - INTERMEDIATE

**Learning Time:** 3-4 weeks  
**Prerequisites:** BEGINNER.md completed  
**Difficulty:** Intermediate → Core algorithms that power production systems

---

## 📚 Table of Contents

1. [Consensus Algorithms Overview](#consensus-algorithms-overview)
2. [Paxos: The Original Consensus Algorithm](#paxos-the-original-consensus-algorithm)
3. [Raft: Consensus Made Understandable](#raft-consensus-made-understandable)
4. [ZAB: ZooKeeper Atomic Broadcast](#zab-zookeeper-atomic-broadcast)
5. [Replication Strategies](#replication-strategies)
6. [Consistency Models](#consistency-models)
7. [Conflict Resolution](#conflict-resolution)
8. [Quorum Systems](#quorum-systems)
9. [Hands-On Implementations](#hands-on-implementations)

---

## 1. Consensus Algorithms Overview

### The Consensus Problem

**Definition:** Get multiple nodes to agree on a single value, even when nodes fail or messages are lost.

```
Scenario: 3 nodes must agree on next database operation

Node 1 proposes: "UPDATE balance = 100"
Node 2 proposes: "DELETE account"
Node 3 proposes: "UPDATE balance = 200"

Goal: All nodes agree on ONE operation, execute in same order ✅
```

### Why Consensus is Hard

```
Challenges in Asynchronous Networks:
├─ Network delays: Messages arrive out of order
├─ Node failures: Nodes crash mid-protocol
├─ Network partitions: Nodes split into groups
└─ FLP Impossibility: Cannot guarantee consensus in bounded time
```

**FLP Impossibility Theorem (1985):**
> In an asynchronous network with even one faulty node, no deterministic consensus algorithm can guarantee termination.

**Practical solution:** Use timeouts (not perfect, but works in practice).

### Properties of Consensus Algorithms

```
Safety Properties (MUST hold):
├─ Agreement: All nodes decide on same value
├─ Validity: Decided value was proposed by some node
└─ Integrity: Nodes decide at most once

Liveness Property (SHOULD hold):
└─ Termination: All non-faulty nodes eventually decide
   (FLP says this is impossible to guarantee!)
```

---

## 2. Paxos: The Original Consensus Algorithm

**Author:** Leslie Lamport (1989, published 1998)  
**Fame:** "The algorithm that powers Google Chubby, Apache ZooKeeper (modified)"

### Paxos Roles

```
┌─────────────────────────────────────────────────────────┐
│ 3 Roles (nodes can play multiple roles):               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 1. Proposer:                                            │
│    ├─ Proposes values to acceptors                     │
│    └─ Example: Client wants to write "X"               │
│                                                         │
│ 2. Acceptor:                                            │
│    ├─ Votes on proposed values                         │
│    ├─ Stores chosen value                              │
│    └─ Typically 2F+1 acceptors (tolerate F failures)   │
│                                                         │
│ 3. Learner:                                             │
│    ├─ Learns which value was chosen                    │
│    └─ Example: Database executes the chosen operation  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Paxos Algorithm (2 Phases)

#### Phase 1: Prepare/Promise

```python
class PaxosProposer:
    def __init__(self, node_id, acceptors):
        self.node_id = node_id
        self.acceptors = acceptors
        self.proposal_number = 0
    
    def prepare(self, value):
        """Phase 1a: Send PREPARE to acceptors"""
        self.proposal_number += 1
        proposal_id = (self.proposal_number, self.node_id)  # (n, node_id)
        
        promises = []
        for acceptor in self.acceptors:
            promise = acceptor.receive_prepare(proposal_id)
            if promise:
                promises.append(promise)
        
        # Need majority (quorum)
        if len(promises) > len(self.acceptors) // 2:
            return self.accept(proposal_id, value, promises)
        else:
            return None  # Failed to get quorum

class PaxosAcceptor:
    def __init__(self):
        self.promised_id = None  # Highest proposal ID promised
        self.accepted_id = None  # Proposal ID of accepted value
        self.accepted_value = None
    
    def receive_prepare(self, proposal_id):
        """Phase 1b: Promise not to accept lower proposals"""
        if self.promised_id is None or proposal_id > self.promised_id:
            self.promised_id = proposal_id
            
            # Return any previously accepted value
            return {
                "promised": True,
                "accepted_id": self.accepted_id,
                "accepted_value": self.accepted_value
            }
        else:
            return {"promised": False}  # Already promised to higher proposal
```

#### Phase 2: Accept/Accepted

```python
class PaxosProposer:
    def accept(self, proposal_id, value, promises):
        """Phase 2a: Send ACCEPT to acceptors"""
        
        # Check if any acceptor already accepted a value
        accepted_values = [p for p in promises if p["accepted_value"] is not None]
        
        if accepted_values:
            # Use highest accepted value (not our proposed value!)
            highest = max(accepted_values, key=lambda p: p["accepted_id"])
            value = highest["accepted_value"]
        
        # Send ACCEPT request
        accepted_count = 0
        for acceptor in self.acceptors:
            if acceptor.receive_accept(proposal_id, value):
                accepted_count += 1
        
        # Need majority
        if accepted_count > len(self.acceptors) // 2:
            # Value is chosen! Notify learners
            self.notify_learners(value)
            return value
        else:
            return None

class PaxosAcceptor:
    def receive_accept(self, proposal_id, value):
        """Phase 2b: Accept value if not promised to higher proposal"""
        if self.promised_id is None or proposal_id >= self.promised_id:
            self.promised_id = proposal_id
            self.accepted_id = proposal_id
            self.accepted_value = value
            return True
        else:
            return False  # Promised to higher proposal
```

### Example: Paxos Run

```
Setup: 3 acceptors (A1, A2, A3), 2 proposers (P1, P2)

Timeline:
─────────────────────────────────────────────────────────
T1: P1 proposes value "X" with proposal_id = (1, P1)

    P1 → A1: PREPARE(1, P1)
    P1 → A2: PREPARE(1, P1)
    P1 → A3: PREPARE(1, P1)

T2: Acceptors promise (no prior proposals)

    A1 → P1: PROMISE (no accepted value yet)
    A2 → P1: PROMISE (no accepted value yet)
    A3 → P1: PROMISE (no accepted value yet)

    P1 has quorum (3/3) ✅

T3: P1 sends ACCEPT

    P1 → A1: ACCEPT(1, P1, "X")
    P1 → A2: ACCEPT(1, P1, "X")
    P1 → A3: ACCEPT(1, P1, "X") ← Message lost! ❌

T4: Acceptors accept

    A1 → P1: ACCEPTED (1, P1, "X")
    A2 → P1: ACCEPTED (1, P1, "X")

    P1 has quorum (2/3) ✅ → "X" is CHOSEN!

T5: P2 proposes value "Y" with proposal_id = (2, P2)

    P2 → A1: PREPARE(2, P2)
    P2 → A2: PREPARE(2, P2)
    P2 → A3: PREPARE(2, P2)

T6: Acceptors promise, but report accepted value "X"

    A1 → P2: PROMISE (accepted_id=(1, P1), value="X")
    A2 → P2: PROMISE (accepted_id=(1, P1), value="X")
    A3 → P2: PROMISE (no accepted value)

T7: P2 must use "X" (not "Y"!)

    P2 → A1: ACCEPT(2, P2, "X")  ← Changed from "Y" to "X"!
    P2 → A2: ACCEPT(2, P2, "X")
    P2 → A3: ACCEPT(2, P2, "X")

    Result: "X" remains chosen (consensus maintained) ✅
```

**Key insight:** Once value is chosen, all future proposals must choose same value.

### Why Paxos is Hard

```
Challenges:
├─ Confusing roles (proposer, acceptor, learner)
├─ Livelock: Two proposers compete, neither makes progress
├─ Multi-Paxos: Choosing sequence of values (not in basic Paxos)
└─ Difficult to implement correctly (Google took years!)

Quote: "There are only two kinds of consensus algorithms: Paxos and
        those that don't work." — Mike Burrows (Google Chubby)
```

---

## 3. Raft: Consensus Made Understandable

**Authors:** Diego Ongaro & John Ousterhout (Stanford, 2014)  
**Goal:** "Understandability as a primary design goal"

### Raft Overview

```
Key Ideas:
├─ Strong leader: All writes go through leader
├─ Leader election: Followers elect leader via voting
├─ Log replication: Leader replicates log to followers
└─ Safety: Leader has all committed entries
```

### Raft Roles

```
┌─────────────────────────────────────────────────────────┐
│ 3 States (each node is in exactly one state):          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 1. Follower:                                            │
│    ├─ Receives log entries from leader                 │
│    ├─ Votes in elections                               │
│    └─ Most nodes are followers most of the time        │
│                                                         │
│ 2. Candidate:                                           │
│    ├─ Requests votes from other nodes                  │
│    ├─ Becomes leader if wins majority                  │
│    └─ Temporary state during election                  │
│                                                         │
│ 3. Leader:                                              │
│    ├─ Handles all client requests                      │
│    ├─ Replicates log to followers                      │
│    └─ Only one leader per term                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Raft Terms

```
Term: Logical clock (monotonically increasing)

Term 1: Leader A  ┃ Term 2: Leader B  ┃ Term 3: No leader ┃ Term 4: Leader A
────────────────────────────────────────────────────────────────────────────→
                  ┃                   ┃ (split vote)      ┃              time

Properties:
├─ Each term has at most 1 leader
├─ Terms used to detect stale information
└─ Node with higher term always wins
```

### Leader Election

```python
import time
import random
from enum import Enum

class State(Enum):
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3

class RaftNode:
    def __init__(self, node_id, peers):
        self.node_id = node_id
        self.peers = peers
        self.state = State.FOLLOWER
        
        # Persistent state
        self.current_term = 0
        self.voted_for = None
        self.log = []
        
        # Volatile state
        self.commit_index = 0
        self.last_applied = 0
        
        # Election timeout
        self.election_timeout = random.uniform(150, 300)  # ms
        self.last_heartbeat = time.time()
    
    def run(self):
        """Main loop"""
        while True:
            if self.state == State.FOLLOWER:
                self.run_follower()
            elif self.state == State.CANDIDATE:
                self.run_candidate()
            elif self.state == State.LEADER:
                self.run_leader()
    
    def run_follower(self):
        """Follower behavior"""
        while self.state == State.FOLLOWER:
            # Check for election timeout
            if time.time() - self.last_heartbeat > self.election_timeout / 1000:
                print(f"Node {self.node_id}: Election timeout, becoming candidate")
                self.state = State.CANDIDATE
                break
            
            time.sleep(0.01)
    
    def run_candidate(self):
        """Candidate behavior: Start election"""
        self.current_term += 1
        self.voted_for = self.node_id
        votes_received = 1  # Vote for self
        
        print(f"Node {self.node_id}: Starting election for term {self.current_term}")
        
        # Request votes from all peers
        for peer in self.peers:
            vote_granted = self.request_vote(peer)
            if vote_granted:
                votes_received += 1
        
        # Check if won election
        if votes_received > (len(self.peers) + 1) // 2:
            print(f"Node {self.node_id}: Won election with {votes_received} votes")
            self.state = State.LEADER
        else:
            print(f"Node {self.node_id}: Lost election")
            self.state = State.FOLLOWER
            self.last_heartbeat = time.time()
    
    def request_vote(self, peer):
        """RPC: Request vote from peer"""
        request = {
            "term": self.current_term,
            "candidate_id": self.node_id,
            "last_log_index": len(self.log) - 1 if self.log else -1,
            "last_log_term": self.log[-1]["term"] if self.log else 0
        }
        
        response = peer.receive_request_vote(request)
        return response.get("vote_granted", False)
    
    def receive_request_vote(self, request):
        """Handle RequestVote RPC"""
        # Update term if higher
        if request["term"] > self.current_term:
            self.current_term = request["term"]
            self.voted_for = None
            self.state = State.FOLLOWER
        
        # Grant vote if:
        # 1. Haven't voted in this term, or already voted for this candidate
        # 2. Candidate's log is at least as up-to-date as ours
        vote_granted = False
        if request["term"] >= self.current_term:
            if self.voted_for is None or self.voted_for == request["candidate_id"]:
                if self.is_log_up_to_date(request):
                    vote_granted = True
                    self.voted_for = request["candidate_id"]
                    self.last_heartbeat = time.time()
        
        return {"term": self.current_term, "vote_granted": vote_granted}
    
    def is_log_up_to_date(self, request):
        """Check if candidate's log is at least as up-to-date"""
        last_log_term = self.log[-1]["term"] if self.log else 0
        last_log_index = len(self.log) - 1 if self.log else -1
        
        if request["last_log_term"] > last_log_term:
            return True
        if request["last_log_term"] == last_log_term:
            return request["last_log_index"] >= last_log_index
        return False
```

### Log Replication

```python
class RaftNode:
    def run_leader(self):
        """Leader behavior: Send heartbeats, replicate log"""
        # Leader state
        self.next_index = {peer: len(self.log) for peer in self.peers}
        self.match_index = {peer: -1 for peer in self.peers}
        
        while self.state == State.LEADER:
            # Send AppendEntries (heartbeat) to all peers
            for peer in self.peers:
                self.send_append_entries(peer)
            
            time.sleep(0.05)  # Heartbeat interval: 50ms
    
    def send_append_entries(self, peer):
        """RPC: Replicate log entries to follower"""
        prev_log_index = self.next_index[peer] - 1
        prev_log_term = self.log[prev_log_index]["term"] if prev_log_index >= 0 else 0
        
        # Entries to send (from next_index to end of log)
        entries = self.log[self.next_index[peer]:]
        
        request = {
            "term": self.current_term,
            "leader_id": self.node_id,
            "prev_log_index": prev_log_index,
            "prev_log_term": prev_log_term,
            "entries": entries,
            "leader_commit": self.commit_index
        }
        
        response = peer.receive_append_entries(request)
        
        if response["success"]:
            # Update next_index and match_index for follower
            self.match_index[peer] = prev_log_index + len(entries)
            self.next_index[peer] = self.match_index[peer] + 1
            
            # Update commit_index if majority has replicated
            self.update_commit_index()
        else:
            # Log inconsistency, decrement next_index and retry
            self.next_index[peer] = max(0, self.next_index[peer] - 1)
    
    def receive_append_entries(self, request):
        """Handle AppendEntries RPC"""
        # Update term
        if request["term"] > self.current_term:
            self.current_term = request["term"]
            self.state = State.FOLLOWER
            self.voted_for = None
        
        # Reset election timeout (received heartbeat)
        self.last_heartbeat = time.time()
        
        # Check if log matches
        if request["prev_log_index"] >= 0:
            if request["prev_log_index"] >= len(self.log):
                return {"term": self.current_term, "success": False}
            if self.log[request["prev_log_index"]]["term"] != request["prev_log_term"]:
                # Log inconsistency, delete conflicting entries
                self.log = self.log[:request["prev_log_index"]]
                return {"term": self.current_term, "success": False}
        
        # Append new entries
        for i, entry in enumerate(request["entries"]):
            index = request["prev_log_index"] + 1 + i
            if index < len(self.log):
                if self.log[index]["term"] != entry["term"]:
                    # Conflict, delete this entry and all following
                    self.log = self.log[:index]
                    self.log.append(entry)
            else:
                self.log.append(entry)
        
        # Update commit index
        if request["leader_commit"] > self.commit_index:
            self.commit_index = min(request["leader_commit"], len(self.log) - 1)
        
        return {"term": self.current_term, "success": True}
    
    def update_commit_index(self):
        """Advance commit_index if majority has replicated"""
        for n in range(self.commit_index + 1, len(self.log)):
            # Count replicas
            replicas = 1  # Leader has it
            for peer in self.peers:
                if self.match_index[peer] >= n:
                    replicas += 1
            
            # Majority and from current term
            if replicas > (len(self.peers) + 1) // 2:
                if self.log[n]["term"] == self.current_term:
                    self.commit_index = n
```

### Example: Raft Execution

```
Setup: 5 nodes (S1, S2, S3, S4, S5)

─────────────────────────────────────────────────────────
T0: All nodes start as followers

    S1, S2, S3, S4, S5: State = FOLLOWER

T1: S1's election timeout expires first

    S1: State = CANDIDATE
    S1: current_term = 1
    S1: Request votes from S2, S3, S4, S5

T2: S2, S3, S4 grant vote (S5 crashed)

    S2 → S1: VOTE GRANTED
    S3 → S1: VOTE GRANTED
    S4 → S1: VOTE GRANTED

    S1: votes = 4/5 (majority) → State = LEADER ✅

T3: S1 sends heartbeats

    S1 → S2, S3, S4, S5: AppendEntries (empty, heartbeat)

T4: Client sends write request to S1

    Client → S1: "SET x = 5"
    S1: Append to log [{"term": 1, "cmd": "SET x = 5"}]
    S1: Replicate to followers

T5: S1 replicates to S2, S3 (S4, S5 slow)

    S1 → S2: AppendEntries [{"term": 1, "cmd": "SET x = 5"}]
    S1 → S3: AppendEntries [{"term": 1, "cmd": "SET x = 5"}]
    
    S2, S3: Append to log ✅

T6: S1 has majority (3/5), commits

    S1: commit_index = 0
    S1: Apply "SET x = 5" to state machine
    S1 → Client: SUCCESS

T7: S1 crashes, S2 times out

    S2: State = CANDIDATE
    S2: current_term = 2
    S2: Request votes

T8: S3, S4 grant vote (S2 has complete log)

    S2: votes = 3/5 → State = LEADER ✅
    S2: Replicate log to all followers (including S4, S5)
```

**Key properties:**
1. **Safety:** Committed entries never lost (S2 has "SET x = 5")
2. **Liveness:** System makes progress (S2 became leader)
3. **Understandability:** Clear roles and state transitions

---

## 4. ZAB: ZooKeeper Atomic Broadcast

**Used by:** Apache ZooKeeper  
**Similar to:** Raft, but optimized for primary-backup replication

### ZAB vs Raft

```
┌─────────────────────────────────────────────────────────┐
│ Similarities:                                           │
├─────────────────────────────────────────────────────────┤
│ ├─ Leader-based consensus                              │
│ ├─ Leader election via voting                          │
│ ├─ Log replication with majority quorum                │
│ └─ Total order of operations                           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Differences:                                            │
├─────────────────────────────────────────────────────────┤
│ ZAB:                              Raft:                 │
│ ├─ Epochs (like terms)            ├─ Terms              │
│ ├─ Recovery phase first           ├─ No recovery phase │
│ ├─ ZXID (epoch + counter)         ├─ Log index + term  │
│ └─ Primary-backup focus           └─ State machine     │
└─────────────────────────────────────────────────────────┘
```

### ZAB Algorithm (High-Level)

```python
class ZABNode:
    def __init__(self, node_id, peers):
        self.node_id = node_id
        self.peers = peers
        self.epoch = 0
        self.zxid = (0, 0)  # (epoch, counter)
        self.state = "LOOKING"
    
    def run(self):
        while True:
            if self.state == "LOOKING":
                self.leader_election()
            elif self.state == "FOLLOWING":
                self.follow_leader()
            elif self.state == "LEADING":
                self.lead_followers()
    
    def leader_election(self):
        """Phase 1: Elect leader with highest ZXID"""
        votes = {}
        
        # Broadcast vote for self
        my_vote = (self.epoch, self.zxid, self.node_id)
        for peer in self.peers:
            peer.receive_vote(my_vote)
        
        # Collect votes
        for peer in self.peers:
            vote = peer.get_vote()
            votes[vote[2]] = vote  # node_id → (epoch, zxid, node_id)
        
        # Leader has highest (epoch, zxid)
        leader_vote = max(votes.values())
        
        if leader_vote[2] == self.node_id:
            self.state = "LEADING"
            self.epoch += 1
        else:
            self.state = "FOLLOWING"
    
    def lead_followers(self):
        """Phase 2: Synchronization - send missing transactions"""
        for peer in self.peers:
            # Send peer's missing transactions from log
            peer.sync_transactions(self.get_missing_txns(peer))
        
        # Phase 3: Broadcast - accept new proposals
        while self.state == "LEADING":
            proposal = self.get_next_proposal()
            if proposal:
                self.broadcast_proposal(proposal)
    
    def broadcast_proposal(self, proposal):
        """Broadcast proposal to followers"""
        self.zxid = (self.epoch, self.zxid[1] + 1)
        proposal["zxid"] = self.zxid
        
        acks = 0
        for peer in self.peers:
            if peer.receive_proposal(proposal):
                acks += 1
        
        # Commit if majority
        if acks > len(self.peers) // 2:
            self.commit(proposal)
            for peer in self.peers:
                peer.commit(proposal["zxid"])
```

---

## 5. Replication Strategies

### Primary-Backup Replication

```
┌─────────────────────────────────────────────────────────┐
│ Setup:                                                  │
│ ├─ 1 Primary (accepts writes)                          │
│ └─ N Backups (replicate from primary)                  │
└─────────────────────────────────────────────────────────┘

Write Flow:
1. Client → Primary: WRITE(x = 5)
2. Primary → Backups: Replicate(x = 5)
3. Backups → Primary: ACK
4. Primary → Client: SUCCESS (after majority ACK)

Read Flow (Linearizable):
1. Client → Primary: READ(x)
2. Primary → Client: 5

Read Flow (Eventually Consistent):
1. Client → Any Backup: READ(x)
2. Backup → Client: 5 (might be stale!)
```

```python
class PrimaryBackup:
    def __init__(self, role, backups=None):
        self.role = role  # "primary" or "backup"
        self.backups = backups or []
        self.data = {}
    
    def write(self, key, value):
        """Write to primary, replicate to backups"""
        if self.role != "primary":
            raise Exception("Only primary accepts writes")
        
        # Write to local storage
        self.data[key] = value
        
        # Replicate to backups
        acks = 0
        for backup in self.backups:
            try:
                backup.replicate(key, value)
                acks += 1
            except Exception:
                pass  # Backup failed
        
        # Require majority
        if acks < len(self.backups) // 2:
            raise Exception("Failed to replicate to majority")
        
        return "SUCCESS"
    
    def replicate(self, key, value):
        """Backup receives replication"""
        if self.role != "backup":
            raise Exception("Not a backup")
        
        self.data[key] = value
        return "ACK"
    
    def read(self, key):
        """Read from local storage"""
        return self.data.get(key)

# Example
primary = PrimaryBackup("primary")
backup1 = PrimaryBackup("backup")
backup2 = PrimaryBackup("backup")
primary.backups = [backup1, backup2]

# Write
primary.write("x", 5)  # Replicates to backups

# Read from primary (linearizable)
print(primary.read("x"))  # 5

# Read from backup (might be stale if replication delayed)
print(backup1.read("x"))  # 5
```

**Failover:**
```python
def failover(primary, backups):
    """Promote backup to primary"""
    # Detect primary failure
    if not primary.is_alive():
        # Elect new primary (backup with most up-to-date log)
        new_primary = max(backups, key=lambda b: b.get_log_length())
        new_primary.role = "primary"
        
        # Notify clients of new primary
        update_dns(new_primary.address)
```

### Multi-Primary Replication

```
┌─────────────────────────────────────────────────────────┐
│ Setup:                                                  │
│ ├─ N Primaries (all accept writes)                     │
│ └─ Conflict resolution required!                       │
└─────────────────────────────────────────────────────────┘

Conflict Example:
1. Client A → Primary 1: WRITE(x = 5)
2. Client B → Primary 2: WRITE(x = 10)  (concurrent)

Which value wins? Need conflict resolution strategy!
```

**Conflict Resolution Strategies:**
1. **Last-Write-Wins (LWW):** Use timestamp, higher wins
2. **Vector Clocks:** Detect conflicts, let application resolve
3. **CRDTs:** Merge operations automatically (see EXPERT.md)

---

## 6. Consistency Models

### Consistency Spectrum

```
Strongest ────────────────────────────────────→ Weakest

Linearizability → Sequential → Causal → Eventual

Higher consistency = Higher latency, Lower availability
Lower consistency = Lower latency, Higher availability
```

### 1. Linearizability (Strongest)

**Definition:** Operations appear instantaneous, respect real-time order.

```
Example: Bank account balance

Timeline (real-time):
─────────────────────────────────────────────────────────
T1: Client A: WRITE(balance = 100)  ✅ Success
T2: Client B: READ(balance)  → Must return 100 ✅
T3: Client C: READ(balance)  → Must return 100 ✅
T4: Client A: WRITE(balance = 200)  ✅ Success
T5: Client B: READ(balance)  → Must return 200 ✅

Property: All reads return most recent write
```

**Implementation:** Single primary, wait for quorum before responding.

```python
class LinearizableStore:
    def __init__(self, replicas):
        self.replicas = replicas
        self.version = 0
    
    def write(self, key, value):
        """Write to majority, then respond"""
        self.version += 1
        
        # Write to all replicas
        acks = 0
        for replica in self.replicas:
            if replica.set(key, value, self.version):
                acks += 1
        
        # Wait for majority
        if acks > len(self.replicas) // 2:
            return "SUCCESS"
        else:
            raise Exception("Failed to achieve quorum")
    
    def read(self, key):
        """Read from majority to ensure latest value"""
        results = []
        for replica in self.replicas:
            results.append(replica.get(key))
        
        # Return value with highest version
        return max(results, key=lambda r: r["version"])["value"]
```

### 2. Sequential Consistency

**Definition:** All nodes see operations in same order (but not necessarily real-time order).

```
Example: Social media posts

Timeline (real-time):
─────────────────────────────────────────────────────────
T1: Alice: POST("Hello")
T2: Bob: POST("Hi")
T3: Charlie: GET_FEED() → ["Hello", "Hi"] ✅
T4: Dave: GET_FEED() → ["Hi", "Hello"] ❌ Violates sequential!

Valid (sequential):
├─ All users see: ["Hello", "Hi"] ✅
└─ All users see: ["Hi", "Hello"] ✅ (order flipped, but consistent)

Invalid:
├─ Charlie sees: ["Hello", "Hi"]
└─ Dave sees: ["Hi", "Hello"] ❌ Different orders!
```

### 3. Causal Consistency

**Definition:** Causally related operations seen in order, concurrent ops can differ.

```
Example: Comment thread

Timeline:
─────────────────────────────────────────────────────────
T1: Alice: POST("Question?")  (Post A)
T2: Bob: REPLY("Answer!", parent=A)  (Post B, depends on A)
T3: Charlie: POST("Unrelated")  (Post C, independent)

Causal dependencies:
├─ A → B (B depends on A)
└─ C independent

User 1 sees: [A, B, C] ✅
User 2 sees: [A, C, B] ✅ (C before B is OK, they're concurrent)
User 3 sees: [C, A, B] ✅
User 4 sees: [B, A, C] ❌ INVALID (B before A violates causality!)
```

### 4. Eventual Consistency (Weakest)

**Definition:** If no new updates, all replicas eventually converge to same value.

```
Example: Dynamo-style database

Timeline:
─────────────────────────────────────────────────────────
T0: Replicas A, B, C have x = 0

T1: Client writes x = 5 to Replica A
    A: x = 5 ✅
    B: x = 0 (not yet replicated)
    C: x = 0 (not yet replicated)

T2: Client reads from Replica B
    Returns: x = 0 ❌ Stale! (but acceptable in eventual consistency)

T3: Replication completes
    A: x = 5
    B: x = 5 ✅
    C: x = 5 ✅

T4: Client reads from any replica
    Returns: x = 5 ✅ Eventually consistent!
```

---

## 7. Conflict Resolution

### Last-Write-Wins (LWW)

```python
class LWWRegister:
    def __init__(self):
        self.value = None
        self.timestamp = 0
    
    def write(self, value):
        """Write with current timestamp"""
        self.timestamp = time.time()
        self.value = value
    
    def merge(self, other_value, other_timestamp):
        """Merge with concurrent write"""
        if other_timestamp > self.timestamp:
            # Other write is newer, adopt it
            self.value = other_value
            self.timestamp = other_timestamp

# Example: Concurrent writes
replica1 = LWWRegister()
replica2 = LWWRegister()

# Replica 1: Write x = 5 at T1
replica1.write(5)  # timestamp = 1000.0

# Replica 2: Write x = 10 at T2 (concurrent)
replica2.write(10)  # timestamp = 1000.1

# Replicas sync
replica1.merge(replica2.value, replica2.timestamp)
print(replica1.value)  # 10 (higher timestamp wins)

replica2.merge(replica1.value, replica1.timestamp)
print(replica2.value)  # 10 (both converge!)
```

**Problem:** Lost updates (earlier write discarded).

### Vector Clocks

```python
class VectorClockRegister:
    def __init__(self, node_id, num_nodes):
        self.node_id = node_id
        self.value = None
        self.clock = [0] * num_nodes
    
    def write(self, value):
        """Write and increment local clock"""
        self.clock[self.node_id] += 1
        self.value = value
    
    def merge(self, other_value, other_clock):
        """Detect conflicts using vector clocks"""
        if self.is_before(other_clock):
            # Other is newer, adopt it
            self.value = other_value
            self.clock = other_clock
        elif self.is_after(other_clock):
            # We are newer, keep ours
            pass
        else:
            # Concurrent! Report conflict to application
            raise ConflictError(self.value, other_value, self.clock, other_clock)
    
    def is_before(self, other_clock):
        """Check if our clock is before other"""
        return all(a <= b for a, b in zip(self.clock, other_clock)) and \
               any(a < b for a, b in zip(self.clock, other_clock))
    
    def is_after(self, other_clock):
        """Check if our clock is after other"""
        return all(a >= b for a, b in zip(self.clock, other_clock)) and \
               any(a > b for a, b in zip(self.clock, other_clock))

# Example
node0 = VectorClockRegister(node_id=0, num_nodes=2)
node1 = VectorClockRegister(node_id=1, num_nodes=2)

# Node 0 writes x = 5
node0.write(5)  # clock = [1, 0]

# Node 1 writes x = 10 (concurrent, no sync yet)
node1.write(10)  # clock = [0, 1]

# Nodes sync
try:
    node0.merge(node1.value, node1.clock)
except ConflictError:
    # Application resolves: Maybe sum values?
    resolved_value = node0.value + node1.value
    node0.value = resolved_value
    node0.clock = [max(a, b) for a, b in zip(node0.clock, node1.clock)]
```

---

## 8. Quorum Systems

### Quorum Definition

```
Setup: N replicas

Quorum: Subset of replicas such that any two quorums overlap

Example: N = 5
├─ Quorum size = 3
├─ Q1 = {R1, R2, R3}
├─ Q2 = {R3, R4, R5}
└─ Q1 ∩ Q2 = {R3} ≠ ∅ ✅ (overlap guaranteed)
```

### Read/Write Quorums

```python
class QuorumStore:
    def __init__(self, replicas, R, W):
        """
        R: Read quorum size
        W: Write quorum size
        Constraint: R + W > N (ensures overlap)
        """
        self.replicas = replicas
        self.R = R
        self.W = W
        assert R + W > len(replicas), "R + W must be > N"
    
    def write(self, key, value):
        """Write to W replicas"""
        version = self.get_latest_version(key) + 1
        
        acks = 0
        for replica in self.replicas:
            try:
                replica.set(key, value, version)
                acks += 1
                if acks >= self.W:
                    return "SUCCESS"
            except Exception:
                pass
        
        raise Exception(f"Failed to achieve write quorum ({acks}/{self.W})")
    
    def read(self, key):
        """Read from R replicas, return latest version"""
        results = []
        for replica in self.replicas:
            try:
                result = replica.get(key)
                results.append(result)
                if len(results) >= self.R:
                    break
            except Exception:
                pass
        
        if len(results) < self.R:
            raise Exception(f"Failed to achieve read quorum ({len(results)}/{self.R})")
        
        # Return value with highest version
        return max(results, key=lambda r: r["version"])["value"]

# Example configurations
# N = 5 replicas

# Strong consistency: R=3, W=3 (R + W = 6 > 5)
store_strong = QuorumStore(replicas, R=3, W=3)

# Optimize for reads: R=2, W=4 (R + W = 6 > 5)
store_read_optimized = QuorumStore(replicas, R=2, W=4)

# Optimize for writes: R=4, W=2 (R + W = 6 > 5)
store_write_optimized = QuorumStore(replicas, R=4, W=2)
```

**Trade-offs:**
```
Low W (e.g., W=2):
├─ Fast writes ✅
└─ Slow reads (need R=4 to ensure overlap) ❌

High W (e.g., W=4):
├─ Slow writes ❌
└─ Fast reads (need R=2 to ensure overlap) ✅

Balanced (W=3, R=3):
├─ Moderate write latency
└─ Moderate read latency
```

---

## 🎯 Key Takeaways

1. **Consensus is fundamental:** Paxos, Raft, ZAB all solve same problem
2. **Raft is understandable:** Use Raft for new systems
3. **Replication != Consensus:** Primary-backup is simpler but less fault-tolerant
4. **Consistency is a spectrum:** Choose based on application needs
5. **Quorums ensure correctness:** R + W > N guarantees overlap
6. **Conflicts are inevitable:** Design for conflict resolution (LWW, vector clocks)

---

## 📚 Further Reading

- **Raft Paper:** https://raft.github.io/raft.pdf
- **Paxos Made Simple:** https://lamport.azurewebsites.net/pubs/paxos-simple.pdf
- **ZAB (ZooKeeper):** https://zookeeper.apache.org/doc/r3.4.13/zookeeperInternals.html
- **Consistency Models:** https://jepsen.io/consistency

---

**Next:** [EXPERT.md](EXPERT.md) — Distributed transactions, CRDTs, Byzantine fault tolerance.
