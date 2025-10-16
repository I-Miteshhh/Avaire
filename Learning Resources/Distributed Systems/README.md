# Distributed Systems - Complete Guide

**Duration:** 8-12 weeks  
**Difficulty:** Intermediate to Expert  
**Prerequisites:** Basic networking, operating systems, algorithms

---

## 🎓 Module Overview

This comprehensive module covers distributed systems from fundamentals to advanced topics used in production at FAANG companies. You'll master:

1. **Fundamentals:** Time, clocks, ordering, failure models, network models
2. **Consensus:** Paxos, Raft, ZAB algorithms
3. **Replication:** Primary-backup, multi-primary, quorums
4. **Consistency:** Linearizability, causal, eventual consistency
5. **Advanced Topics:** Distributed transactions, CRDTs, Byzantine fault tolerance
6. **Real Systems:** Spanner, Dynamo, Calvin, Kafka

By the end of this module, you will:
- Design distributed systems handling millions of users
- Implement consensus algorithms (Raft)
- Choose appropriate consistency models for applications
- Debug distributed systems issues (timing, partitions, failures)
- Pass distributed systems interviews at FAANG companies

---

## 🗓️ 12-Week Learning Path

### Weeks 1-2: Fundamentals

#### Week 1: Distributed Systems Basics
- **Reading:** [BEGINNER.md](BEGINNER.md) — Sections 1-4
- **Topics:**
  - What is a distributed system? Examples, motivations
  - 8 Fallacies of distributed computing
  - Network models (synchronous vs asynchronous)
  - Time, clocks, and ordering (Lamport clocks)
- **Hands-on:**
  - Implement Lamport logical clock
  - Build distributed counter with Redis
  - Simulate clock skew problems
- **Paper:** Lamport's "Time, Clocks, and Ordering of Events" (1978)

#### Week 2: Failure Models & Communication
- **Reading:** [BEGINNER.md](BEGINNER.md) — Sections 5-9
- **Topics:**
  - Communication patterns (RPC, message passing, pub-sub)
  - Failure models (crash, omission, timing, Byzantine)
  - Failure detection (heartbeats, timeouts)
  - Coordination primitives (leader election, distributed locks, barriers)
- **Hands-on:**
  - Implement heartbeat-based failure detector
  - Build distributed lock with Redis
  - Create distributed queue
- **Exercise:** Design failure detector with tunable accuracy/completeness trade-off

---

### Weeks 3-5: Consensus Algorithms

#### Week 3: Paxos
- **Reading:** [INTERMEDIATE.md](INTERMEDIATE.md) — Section 2
- **Topics:**
  - Consensus problem (agreement, validity, termination)
  - Paxos roles (proposer, acceptor, learner)
  - Paxos algorithm (prepare/promise, accept/accepted)
  - Multi-Paxos optimization
- **Hands-on:**
  - Implement Basic Paxos (Python)
  - Simulate Paxos with failures
  - Trace Paxos execution with multiple proposers
- **Paper:** "Paxos Made Simple" by Lamport (2001)
- **Challenge:** Why is Paxos considered difficult? What causes livelock?

#### Week 4: Raft
- **Reading:** [INTERMEDIATE.md](INTERMEDIATE.md) — Section 3 + [WHITEPAPERS.md](WHITEPAPERS.md) — Section 5
- **Topics:**
  - Raft overview (strong leader, leader election, log replication)
  - Terms and state machine
  - Leader election with randomized timeouts
  - Log replication (AppendEntries RPC)
  - Safety properties
- **Hands-on:**
  - Implement Raft leader election
  - Build log replication
  - Test with network partitions
- **Paper:** "In Search of an Understandable Consensus Algorithm" (2014)
- **Interactive:** Play with Raft visualization: https://raft.github.io/

#### Week 5: ZAB and Comparison
- **Reading:** [INTERMEDIATE.md](INTERMEDIATE.md) — Section 4
- **Topics:**
  - ZooKeeper Atomic Broadcast (ZAB)
  - ZAB phases (discovery, synchronization, broadcast)
  - Comparison: Paxos vs Raft vs ZAB
- **Hands-on:**
  - Use ZooKeeper for leader election
  - Implement distributed configuration service
- **Project:** Build simple distributed key-value store using Raft

---

### Weeks 6-7: Replication & Consistency

#### Week 6: Replication Strategies
- **Reading:** [INTERMEDIATE.md](INTERMEDIATE.md) — Section 5
- **Topics:**
  - Primary-backup replication
  - Multi-primary replication
  - Quorum systems (R + W > N)
  - Conflict resolution (last-write-wins, vector clocks)
- **Hands-on:**
  - Implement primary-backup with failover
  - Build quorum-based key-value store
  - Simulate split-brain scenario
- **Exercise:** Design replication strategy for:
  - Banking system (strong consistency needed)
  - Social media feed (eventual consistency OK)

#### Week 7: Consistency Models
- **Reading:** [INTERMEDIATE.md](INTERMEDIATE.md) — Sections 6-7
- **Topics:**
  - Consistency spectrum (linearizability → eventual)
  - CAP theorem (consistency, availability, partition tolerance)
  - PACELC theorem
  - Vector clocks for conflict detection
- **Hands-on:**
  - Implement linearizable store (single primary + quorum)
  - Build eventually consistent store (gossip-based)
  - Detect conflicts with vector clocks
- **Paper:** "Dynamo: Amazon's Highly Available Key-Value Store" (2007)
- **Challenge:** Design shopping cart with eventual consistency

---

### Weeks 8-9: Distributed Transactions

#### Week 8: Two-Phase Commit
- **Reading:** [EXPERT.md](EXPERT.md) — Sections 1-3
- **Topics:**
  - ACID in distributed systems
  - Two-phase commit (2PC) protocol
  - 2PC problems (blocking, single point of failure)
  - Three-phase commit (3PC) - non-blocking
- **Hands-on:**
  - Implement 2PC coordinator and participants
  - Simulate coordinator failure (blocking scenario)
  - Implement recovery from WAL
- **Exercise:** When would you use 2PC despite its limitations?

#### Week 9: Spanner & TrueTime
- **Reading:** [EXPERT.md](EXPERT.md) — Section 4 + [WHITEPAPERS.md](WHITEPAPERS.md) — Section 6
- **Topics:**
  - Spanner architecture (globally distributed SQL)
  - TrueTime API (bounded clock uncertainty)
  - External consistency (linearizability across data centers)
  - Commit wait protocol
- **Hands-on:**
  - Simulate TrueTime with artificial uncertainty
  - Implement commit wait
  - Compare with 2PC latency
- **Paper:** "Spanner: Google's Globally-Distributed Database" (2012)
- **Discussion:** Why is TrueTime a game-changer? Can you replicate without GPS?

---

### Weeks 10-11: Advanced Topics

#### Week 10: CRDTs and Gossip
- **Reading:** [EXPERT.md](EXPERT.md) — Sections 5-6
- **Topics:**
  - Conflict-Free Replicated Data Types (CRDTs)
  - G-Counter, PN-Counter, LWW-Set, OR-Set
  - Strong eventual consistency
  - Gossip protocols (epidemic algorithms)
  - Merkle trees for anti-entropy
- **Hands-on:**
  - Implement G-Counter and PN-Counter
  - Build collaborative text editor with CRDTs
  - Implement gossip-based cluster membership
- **Use Case:** When to use CRDTs vs consensus?

#### Week 11: Distributed Snapshots & Advanced Consensus
- **Reading:** [EXPERT.md](EXPERT.md) — Sections 7-8
- **Topics:**
  - Chandy-Lamport snapshot algorithm
  - Distributed debugging and checkpointing
  - Multi-Paxos, EPaxos, Flexible Paxos
  - Calvin (deterministic databases)
- **Hands-on:**
  - Implement Chandy-Lamport algorithm
  - Build distributed snapshot service
- **Paper:** "Distributed Snapshots" by Chandy & Lamport (1985)
- **Paper:** "Calvin: Fast Distributed Transactions" (2012)

---

### Week 12: Byzantine Fault Tolerance & Capstone

#### Byzantine Fault Tolerance
- **Reading:** [EXPERT.md](EXPERT.md) — Section 9
- **Topics:**
  - Byzantine failures (malicious nodes)
  - PBFT algorithm (3f+1 nodes tolerate f Byzantine faults)
  - HotStuff (modern BFT for blockchains)
- **Hands-on:**
  - Implement simple PBFT (3 phases)
  - Simulate Byzantine node (sends conflicting messages)
- **Use Case:** Blockchain consensus (Bitcoin, Ethereum)

#### Capstone Project (see below)

---

## 🏆 Capstone Project: Build a Distributed Database

### Project Overview

Build a production-ready distributed key-value store with the following features:

**Requirements:**

1. **Consensus:** Raft-based replication (5 nodes, tolerate 2 failures)
2. **Consistency:** Linearizable reads and writes
3. **Partitioning:** Consistent hashing with virtual nodes
4. **API:** Simple key-value operations (GET, PUT, DELETE)
5. **Fault Tolerance:** Handle node crashes, network partitions
6. **Performance:** <10ms P99 latency for local reads/writes

**Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│ Client Layer                                            │
├─────────────────────────────────────────────────────────┤
│ ├─ Client library (consistent hashing for routing)     │
│ └─ API: get(key), put(key, value), delete(key)         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Raft Cluster (5 nodes)                                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Node 1 (Leader)                                         │
│ ├─ Raft consensus (leader election, log replication)   │
│ ├─ Storage engine (RocksDB or in-memory map)           │
│ └─ Partitions: [0x0000-0x3333]                         │
│                                                         │
│ Node 2 (Follower)                                       │
│ ├─ Raft consensus                                       │
│ └─ Partitions: [0x3333-0x6666]                         │
│                                                         │
│ Node 3 (Follower)                                       │
│ ├─ Raft consensus                                       │
│ └─ Partitions: [0x6666-0x9999]                         │
│                                                         │
│ Node 4 (Follower)                                       │
│ └─ Partitions: [0x9999-0xCCCC]                         │
│                                                         │
│ Node 5 (Follower)                                       │
│ └─ Partitions: [0xCCCC-0xFFFF]                         │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Storage Layer                                           │
├─────────────────────────────────────────────────────────┤
│ ├─ Persistent storage (WAL + snapshots)                │
│ ├─ Compaction (remove old log entries)                  │
│ └─ Metrics (latency, throughput, error rate)           │
└─────────────────────────────────────────────────────────┘
```

**Implementation Steps:**

**Phase 1: Raft Consensus (Weeks 1-2)**
```python
# Implement Raft state machine
class RaftNode:
    def __init__(self, node_id, peers):
        self.state = State.FOLLOWER
        self.current_term = 0
        self.log = []
        self.commit_index = 0
    
    def start_election(self):
        """Transition to candidate, request votes"""
        pass
    
    def append_entries(self, entries):
        """Leader replicates log entries"""
        pass
    
    def apply_committed_entries(self):
        """Apply committed entries to state machine"""
        pass
```

**Phase 2: Key-Value Store (Week 3)**
```python
class KeyValueStore:
    def __init__(self, raft_node):
        self.raft = raft_node
        self.data = {}
    
    def get(self, key):
        """Linearizable read (read from leader)"""
        if not self.raft.is_leader():
            raise NotLeaderError()
        return self.data.get(key)
    
    def put(self, key, value):
        """Linearizable write (replicate via Raft)"""
        command = {"op": "PUT", "key": key, "value": value}
        self.raft.append_entries([command])
        # Wait for commit
        return "SUCCESS"
```

**Phase 3: Partitioning (Week 4)**
```python
class ConsistentHashRing:
    def __init__(self, nodes, virtual_nodes=100):
        self.ring = {}
        for node in nodes:
            for i in range(virtual_nodes):
                hash_val = hash(f"{node}:{i}")
                self.ring[hash_val] = node
    
    def get_node(self, key):
        """Find node responsible for key"""
        hash_val = hash(key)
        for ring_hash in sorted(self.ring.keys()):
            if hash_val <= ring_hash:
                return self.ring[ring_hash]
        return self.ring[min(self.ring.keys())]
```

**Phase 4: Testing & Benchmarking (Week 5)**
```python
def test_fault_tolerance():
    """Test with node failures"""
    cluster = start_cluster(num_nodes=5)
    
    # Write data
    cluster.put("key1", "value1")
    
    # Kill leader
    cluster.kill_leader()
    
    # New leader elected
    time.sleep(1)  # Election timeout
    
    # Read should still work
    assert cluster.get("key1") == "value1"

def benchmark():
    """Measure throughput and latency"""
    for i in range(10000):
        start = time.time()
        cluster.put(f"key{i}", f"value{i}")
        latency = time.time() - start
        record_latency(latency)
    
    print(f"Throughput: {10000 / total_time} ops/sec")
    print(f"P50 latency: {p50_latency}ms")
    print(f"P99 latency: {p99_latency}ms")
```

**Stretch Goals:**
- [ ] Read-only optimizations (read from followers)
- [ ] Snapshot and log compaction
- [ ] Multi-partition transactions
- [ ] Monitoring dashboard (Grafana + Prometheus)
- [ ] Client-side caching
- [ ] Compare performance with Redis, etcd

**Success Metrics:**
- Passes linearizability checker (Jepsen-style)
- Survives 2 node failures
- <10ms P99 latency for single-key operations
- Handles 10K+ ops/sec throughput

---

## 📊 Assessment Checklist

### Beginner Level
- [ ] Explain the 8 fallacies of distributed computing with examples
- [ ] Implement Lamport logical clocks
- [ ] Distinguish between crash, omission, and Byzantine failures
- [ ] Build distributed counter and queue with Redis
- [ ] Understand happened-before relation

### Intermediate Level
- [ ] Implement Paxos or Raft from scratch
- [ ] Design primary-backup replication with failover
- [ ] Configure quorum systems (R, W, N) for different use cases
- [ ] Detect conflicts using vector clocks
- [ ] Explain CAP theorem with real-world examples
- [ ] Choose appropriate consistency model for application

### Expert Level
- [ ] Implement Two-Phase Commit with recovery
- [ ] Understand Spanner's TrueTime and commit wait
- [ ] Build CRDTs (G-Counter, OR-Set)
- [ ] Implement Chandy-Lamport snapshot algorithm
- [ ] Design Byzantine fault-tolerant system (PBFT)
- [ ] Pass distributed systems interviews at FAANG

### Capstone
- [ ] Build distributed key-value store with Raft
- [ ] Handle node failures and network partitions
- [ ] Achieve linearizable consistency
- [ ] Benchmark performance (throughput, latency)
- [ ] Pass linearizability testing (Jepsen-style)

---

## 🎯 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Theoretical Knowledge** | Explain consensus algorithms | Mock interview |
| **Implementation** | Working Raft implementation | Code review |
| **System Design** | Design distributed database | Design review |
| **Debugging** | Debug partition scenarios | Troubleshooting exercise |
| **Performance** | <10ms P99 latency | Benchmark tests |
| **Fault Tolerance** | Tolerate 2/5 node failures | Chaos testing |

---

## 📚 Additional Resources

### Books
- **"Designing Data-Intensive Applications"** by Martin Kleppmann (must-read!)
- **"Distributed Systems"** by Tanenbaum & Van Steen (textbook)
- **"Database Internals"** by Alex Petrov (deep dive)

### Online Courses
- **MIT 6.824:** Distributed Systems (legendary course)
  - https://pdos.csail.mit.edu/6.824/
  - Labs: Implement Raft, MapReduce, key-value store
- **CMU 15-440:** Distributed Systems
- **UIUC CS 425:** Distributed Systems

### Papers Reading List
1. ✅ Lamport's Time & Clocks (1978)
2. ✅ FLP Impossibility (1985)
3. ✅ Paxos Made Simple (2001)
4. ✅ Dynamo (2007)
5. ✅ Raft (2014)
6. ✅ Spanner (2012)
7. ✅ Calvin (2012)
8. Chandy-Lamport Snapshot (1985)
9. MapReduce (2004)
10. BigTable (2006)

### Tools & Frameworks
- **etcd:** Distributed key-value store (Raft-based)
- **ZooKeeper:** Coordination service (ZAB-based)
- **Consul:** Service mesh (Raft-based)
- **Jepsen:** Distributed systems testing
- **TLA+:** Formal specification (by Lamport)

### Communities
- **Distributed Systems Reading Group:** https://charap.co/category/reading-group/
- **Papers We Love:** https://paperswelove.org/
- **Aphyr's Blog:** https://aphyr.com/posts (Jepsen author)
- **The Morning Paper:** https://blog.acolyer.org/ (paper summaries)

---

## 🔍 Interview Preparation

### Common Interview Questions

**Conceptual:**
1. Explain CAP theorem with examples
2. What is the difference between Paxos and Raft?
3. How does Spanner achieve external consistency?
4. When would you choose eventual consistency over strong consistency?
5. What is the FLP impossibility result? How do real systems handle it?

**System Design:**
1. Design a distributed lock service (like Google Chubby)
2. Design a distributed key-value store (like Dynamo)
3. Design a distributed transaction system (like Spanner)
4. How would you implement leader election without external coordination?
5. Design a globally distributed database with <100ms latency

**Debugging:**
1. Your distributed database reports inconsistent reads. How do you debug?
2. Leader election is failing (split votes). What's wrong?
3. Clients see stale data despite strong consistency. Diagnose the issue.
4. Network partition causes split-brain. How do you recover?

**Coding:**
1. Implement Raft leader election
2. Implement vector clocks for conflict detection
3. Implement distributed lock with Redis
4. Write linearizability checker

---

## 🏁 Completion Celebration

You've completed the **Distributed Systems** module! You now have:

✅ **Deep understanding** of distributed systems fundamentals  
✅ **Hands-on experience** implementing consensus algorithms  
✅ **Production knowledge** of real systems (Spanner, Dynamo, Calvin)  
✅ **Interview readiness** for FAANG distributed systems roles  
✅ **Capstone project** showcasing your skills  

### What's Next?

**Career Paths:**
1. **Distributed Systems Engineer** (Google, Amazon, Meta)
2. **Infrastructure Engineer** (databases, storage, compute)
3. **Site Reliability Engineer** (SRE) with distributed systems focus
4. **Research Scientist** (PhD in distributed systems)

**Continue Learning:**
1. **Blockchain & Cryptocurrencies** (Bitcoin, Ethereum consensus)
2. **Stream Processing** (Kafka, Flink, distributed dataflow)
3. **Serverless & Edge Computing** (distributed execution)
4. **Formal Methods** (TLA+, model checking)

---

## ✨ Final Words

Distributed systems are everywhere:
- Every time you Google search → distributed system
- Every time you watch Netflix → distributed CDN
- Every time you buy on Amazon → distributed transactions

**Key Principles to Remember:**

1. **There is no global clock** → Use logical clocks, happened-before
2. **Networks are unreliable** → Design for partitions, retries, timeouts
3. **Consensus is hard** → Use Raft/Paxos, understand trade-offs
4. **Consistency vs Availability** → Choose based on use case (CAP theorem)
5. **Testing is critical** → Use Jepsen, chaos engineering

**You are now equipped to build planet-scale distributed systems!** 🚀

---

**Author:** Distributed Systems Module  
**Version:** 1.0  
**Last Updated:** October 15, 2025  
**License:** MIT  

**Questions?** Open an issue or join the discussion on our community forum.

---

**Congratulations on completing the Distributed Systems module!** 🎉
