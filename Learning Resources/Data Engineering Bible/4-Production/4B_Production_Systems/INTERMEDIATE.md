# Week 15-16: Production Data Systems — INTERMEDIATE Track

*"Every system design is a trade-off. Understanding consistency vs availability, latency vs throughput, and cost vs performance separates L6 engineers from L5."* — Staff Engineer, Meta

---

## 🎯 Learning Outcomes

- Master trade-off analysis (CAP theorem, PACELC, consistency models)
- Design for cost optimization
- Implement SLA/SLI/SLO frameworks
- Handle data partitioning and sharding strategies
- Design disaster recovery (RTO/RPO)
- Understand multi-region architectures
- Implement backpressure and flow control
- Build self-healing systems

---

## ⚖️ 1. Trade-Off Analysis

### The Universal Truth

```
"You cannot optimize for everything. Every decision is a trade-off."

Common Trade-Offs:
┌─────────────────────┬──────────────────────┐
│ Optimize For        │ Trade Off            │
├─────────────────────┼──────────────────────┤
│ Low Latency         │ High Cost            │
│ High Availability   │ Consistency          │
│ Scalability         │ Complexity           │
│ Strong Consistency  │ Performance          │
│ Simplicity          │ Features             │
│ Flexibility         │ Performance          │
│ Durability          │ Latency              │
│ Cost                │ Everything else      │
└─────────────────────┴──────────────────────┘
```

---

## 🔺 2. CAP Theorem

### The Impossible Triangle

```
CAP Theorem (Brewer, 2000):
"A distributed system can provide at most 2 of the following 3 guarantees"

C = Consistency:
    All nodes see the same data at the same time
    Read reflects most recent write

A = Availability:
    Every request receives a response (success or failure)
    No request hangs indefinitely

P = Partition Tolerance:
    System continues to operate despite network partitions
    Some nodes cannot communicate with others

┌────────────────────────────────────────────────────┐
│         Consistency (C)                            │
│              /\                                    │
│             /  \                                   │
│            /    \                                  │
│           /  CP  \                                 │
│          /  (e.g.,\                                │
│         /   MongoDB)\                              │
│        /            \                              │
│       /              \                             │
│      /                \                            │
│     /   CA (impossible \                           │
│    /    in distributed) \                          │
│   /                      \                         │
│  /________________________\                        │
│ Availability (A)           Partition Tolerance (P) │
│         AP                                         │
│    (e.g., Cassandra)                               │
└────────────────────────────────────────────────────┘

Reality: P is mandatory (networks always partition)
So the real choice is: CP vs AP
```

---

### CP Systems (Consistency + Partition Tolerance)

```
Examples: MongoDB, HBase, Redis (single master), Spanner

Behavior during partition:
┌────────────────────────────────────────────────────┐
│ Normal Operation:                                  │
│ ┌────────┐       ┌────────┐                       │
│ │ Node A │◄─────►│ Node B │  (Connected)          │
│ │ value=5│       │ value=5│                       │
│ └────────┘       └────────┘                       │
│                                                    │
│ Write to A: value=10                               │
│ ✅ Replicate to B → Both have value=10            │
│                                                    │
│ During Partition:                                 │
│ ┌────────┐   X   ┌────────┐                       │
│ │ Node A │ ─ ─ ─ │ Node B │  (Disconnected)       │
│ │ value=10│      │ value=10│                      │
│ └────────┘       └────────┘                       │
│                                                    │
│ Write to A: value=20                               │
│ ❌ Cannot replicate to B                          │
│ ❌ A rejects write OR becomes unavailable          │
│                                                    │
│ Result: Consistency guaranteed, availability lost │
└────────────────────────────────────────────────────┘

Use Cases:
├─ Financial transactions (no inconsistency allowed)
├─ Inventory management (prevent overselling)
└─ Strong consistency requirements
```

---

### AP Systems (Availability + Partition Tolerance)

```
Examples: Cassandra, DynamoDB, Riak, CouchDB

Behavior during partition:
┌────────────────────────────────────────────────────┐
│ Normal Operation:                                  │
│ ┌────────┐       ┌────────┐                       │
│ │ Node A │◄─────►│ Node B │  (Connected)          │
│ │ value=5│       │ value=5│                       │
│ └────────┘       └────────┘                       │
│                                                    │
│ Write to A: value=10                               │
│ ✅ Eventually replicate to B                       │
│                                                    │
│ During Partition:                                 │
│ ┌────────┐   X   ┌────────┐                       │
│ │ Node A │ ─ ─ ─ │ Node B │  (Disconnected)       │
│ │ value=10│      │ value=10│                      │
│ └────────┘       └────────┘                       │
│                                                    │
│ Write to A: value=20 ✅ (succeeds)                │
│ Write to B: value=30 ✅ (succeeds)                │
│                                                    │
│ After partition heals:                            │
│ ├─ Conflict: A has value=20, B has value=30       │
│ └─ Resolve via:                                   │
│    ├─ Last-write-wins (timestamp)                 │
│    ├─ Vector clocks (causal ordering)             │
│    └─ Application-level merge                     │
│                                                    │
│ Result: Availability guaranteed, consistency lost │
└────────────────────────────────────────────────────┘

Use Cases:
├─ Social media (temporary inconsistency OK)
├─ Shopping carts (can merge later)
└─ High availability required (24/7 uptime)
```

---

### PACELC Theorem (Extension of CAP)

```
PACELC = "If Partition, choose A or C, Else choose L or C"

During partition (P):
├─ Choose Availability (A) or Consistency (C)

When no partition (E = Else):
├─ Choose Latency (L) or Consistency (C)

┌──────────────┬─────────────┬─────────────┐
│ System       │ If P        │ Else        │
├──────────────┼─────────────┼─────────────┤
│ DynamoDB     │ AP          │ EL (low L)  │
│ Cassandra    │ AP          │ EL (low L)  │
│ MongoDB      │ CP          │ EC (strong) │
│ HBase        │ CP          │ EC (strong) │
│ Spanner      │ CP          │ EC (strong) │
│ Cosmos DB    │ Tunable     │ Tunable     │
│ (consistency │             │             │
│  levels)     │             │             │
└──────────────┴─────────────┴─────────────┘
```

---

## 🔄 3. Consistency Models

### Spectrum of Consistency

```
Strongest ────────────────────────────────► Weakest
│                                                   │
Linearizability                          Eventual
(Strict)                                 Consistency
│            │           │           │              │
│            │           │           │              │
Sequential   Causal      Session     Read-your-writes

Linearizability (Strongest):
├─ Reads always return most recent write
├─ Global ordering of all operations
├─ Example: Single-node database
└─ Cost: High latency (coordination overhead)

Sequential Consistency:
├─ All nodes see operations in same order
├─ But not necessarily real-time order
├─ Example: Spanner (within same region)
└─ Cost: Medium latency

Causal Consistency:
├─ Causally related operations seen in order
├─ Concurrent operations can be reordered
├─ Example: DynamoDB global tables
└─ Cost: Low latency, complex implementation

Session Consistency:
├─ Within single session, reads follow writes
├─ Different sessions may see different order
├─ Example: Azure Cosmos DB (session level)
└─ Cost: Low latency

Read-Your-Writes:
├─ User's reads reflect their own writes
├─ Other users may see stale data
├─ Example: Social media (you see your post immediately)
└─ Cost: Very low latency

Eventual Consistency (Weakest):
├─ All replicas eventually converge
├─ No guarantee on convergence time
├─ Example: S3, DNS, Cassandra (default)
└─ Cost: Lowest latency, highest availability
```

---

### Choosing Consistency Level

```python
# Example: Cassandra consistency levels

# Write with QUORUM (majority)
session.execute(
    "INSERT INTO users (id, name) VALUES (1, 'Alice')",
    consistency_level=ConsistencyLevel.QUORUM
)
# Writes to majority of replicas (2 out of 3)
# Trade-off: Higher latency, stronger consistency

# Read with ONE (fastest)
session.execute(
    "SELECT * FROM users WHERE id = 1",
    consistency_level=ConsistencyLevel.ONE
)
# Reads from 1 replica (fastest)
# Trade-off: Might read stale data

# Strong consistency: R + W > N
# Example: N=3 replicas, W=2 (quorum), R=2 (quorum)
# Guarantees: Read always sees most recent write
# Cost: Higher latency (must wait for 2 nodes)

# Eventual consistency: R + W ≤ N
# Example: N=3, W=1, R=1
# Guarantees: None (might read stale)
# Cost: Lowest latency (only 1 node)
```

---

## 💰 4. Cost Optimization

### The $100K/Month Data Pipeline

```
Inefficient Architecture (Cost: $100K/month):
┌────────────────────────────────────────────────┐
│ Spark Cluster:                                 │
│ ├─ 100 nodes × 8 cores × $0.50/hour           │
│ ├─ Running 24/7 (even when idle)              │
│ └─ Cost: 100 × 8 × $0.50 × 730 = $292K/month│
│                                                │
│ S3 Storage:                                    │
│ ├─ 500 TB × $0.023/GB = $11.5K/month          │
│ ├─ No lifecycle policy (hot storage)          │
│ └─ No compression (3x larger than needed)     │
│                                                │
│ Total: $292K + $11.5K = $303.5K/month ❌      │
└────────────────────────────────────────────────┘

Optimized Architecture (Cost: $30K/month):
┌────────────────────────────────────────────────┐
│ Spot Instances + Autoscaling:                  │
│ ├─ 10-100 nodes (autoscale based on load)     │
│ ├─ Spot pricing (70% discount)                │
│ ├─ Run only during batch window (8 hours/day) │
│ └─ Cost: 50 × 8 × $0.15 × 240 = $14.4K/month │
│                                                │
│ S3 Intelligent Tiering:                        │
│ ├─ 500 TB compressed to 150 TB (Parquet snappy)│
│ ├─ 100 TB hot (frequent access): $2.3K/month  │
│ ├─ 50 TB warm (S3-IA): $0.6K/month            │
│ └─ 400 TB cold (Glacier): $0.4K/month         │
│ Total storage: $3.3K/month                    │
│                                                │
│ Reserved Instances (1-year):                   │
│ ├─ 5 baseline nodes (always-on)               │
│ └─ Cost: 5 × 8 × $0.20 × 730 = $5.8K/month   │
│                                                │
│ Network Transfer (optimized):                  │
│ ├─ Use VPC endpoints (avoid NAT gateway)      │
│ ├─ Compress before transfer                   │
│ └─ Cost: $2K/month                            │
│                                                │
│ Query Engine (Presto on EMR):                  │
│ ├─ On-demand cluster (1 hour/day)             │
│ └─ Cost: $1K/month                            │
│                                                │
│ Total: $14.4K + $3.3K + $5.8K + $2K + $1K     │
│      = $26.5K/month ✅ (91% savings!)         │
└────────────────────────────────────────────────┘
```

---

### Cost Optimization Strategies

```
1. Compute:
   ├─ Use spot instances (70% discount, handle interruptions)
   ├─ Autoscale (scale to zero when idle)
   ├─ Right-size instances (don't over-provision)
   ├─ Reserved instances for baseline (1-year commitment)
   └─ Serverless for intermittent workloads (Lambda, Fargate)

2. Storage:
   ├─ Compress data (Parquet with Snappy: 3x compression)
   ├─ Use lifecycle policies (hot → warm → cold → archive)
   ├─ Delete old data (retention policy: 3 years, then delete)
   ├─ Partition data (query only needed partitions)
   └─ Use cheaper storage (S3 vs EBS: 10x cheaper)

3. Network:
   ├─ Use VPC endpoints (avoid NAT gateway: $0.045/GB)
   ├─ Compress before transfer (reduce data volume)
   ├─ Keep data in same region (avoid cross-region: $0.02/GB)
   └─ Use CDN for hot data (CloudFront caching)

4. Query Optimization:
   ├─ Partition pruning (query only needed partitions)
   ├─ Predicate pushdown (filter at storage layer)
   ├─ Column pruning (read only needed columns)
   ├─ Materialized views (precompute aggregations)
   └─ Query result caching (avoid re-computation)

5. Monitoring:
   ├─ Set budget alerts (notify when >80% of budget)
   ├─ Tag resources (track cost by team/project)
   ├─ Delete unused resources (orphaned EBS volumes)
   └─ Use cost explorer (identify cost spikes)
```

---

## 📏 5. SLA, SLI, SLO Framework

### Definitions

```
SLI (Service Level Indicator):
├─ What: Metric that measures service level
├─ Examples:
│  ├─ Latency: P50, P95, P99 response time
│  ├─ Availability: Uptime percentage
│  ├─ Throughput: Requests per second
│  ├─ Error rate: Percentage of failed requests
│  └─ Freshness: Data staleness in minutes
└─ Measurement: Actual observed values

SLO (Service Level Objective):
├─ What: Target for SLI (internal goal)
├─ Examples:
│  ├─ "P95 latency < 200ms"
│  ├─ "Availability > 99.9%"
│  ├─ "Data freshness < 15 minutes"
│  └─ "Error rate < 0.1%"
└─ Purpose: Set expectations, measure success

SLA (Service Level Agreement):
├─ What: Contract with customers (legal commitment)
├─ Examples:
│  ├─ "99.9% uptime (43 minutes downtime/month)"
│  ├─ "If violated: 10% refund"
│  └─ "P99 latency < 1 second"
└─ Purpose: Customer expectations, penalties
```

---

### Calculating Error Budget

```
Error Budget = 100% - SLO

Example:
SLO = 99.9% availability
Error Budget = 100% - 99.9% = 0.1%

Time-based budget (30-day month):
Total time: 30 days × 24 hours = 720 hours
Error budget: 720 × 0.1% = 0.72 hours = 43 minutes

Budget Consumption:
├─ Week 1: 10 minutes downtime → 10/43 = 23% consumed
├─ Week 2: 5 minutes downtime → 5/43 = 12% consumed
├─ Week 3: 15 minutes downtime → 15/43 = 35% consumed
├─ Week 4: 0 minutes downtime → 0% consumed
└─ Total: 30/43 = 70% consumed ✅ (within budget)

Actions based on budget:
┌─────────────────┬──────────────────────────────────┐
│ Budget Remaining│ Action                           │
├─────────────────┼──────────────────────────────────┤
│ > 50%           │ Ship new features aggressively   │
│ 20-50%          │ Ship features with caution       │
│ 10-20%          │ Focus on reliability             │
│ < 10%           │ Feature freeze, fix bugs only    │
│ 0%              │ Emergency: rollback, incident    │
└─────────────────┴──────────────────────────────────┘
```

---

### Real-World SLOs

```python
# Example: Data Pipeline SLOs

SLOs = {
    # Latency SLO
    'latency_p50': {
        'sli': 'histogram_quantile(0.50, pipeline_duration_seconds)',
        'slo': 60,  # 1 minute P50
        'unit': 'seconds',
    },
    'latency_p95': {
        'sli': 'histogram_quantile(0.95, pipeline_duration_seconds)',
        'slo': 300,  # 5 minutes P95
        'unit': 'seconds',
    },
    
    # Availability SLO
    'availability': {
        'sli': 'sum(pipeline_success) / sum(pipeline_total)',
        'slo': 0.999,  # 99.9% success rate
        'unit': 'ratio',
    },
    
    # Freshness SLO
    'freshness': {
        'sli': 'time() - pipeline_last_success_timestamp',
        'slo': 900,  # 15 minutes max staleness
        'unit': 'seconds',
    },
    
    # Throughput SLO
    'throughput': {
        'sli': 'rate(pipeline_records_processed[5m])',
        'slo': 10000,  # 10K records/second
        'unit': 'records_per_second',
    },
}

# Monitor SLO compliance
def check_slo_compliance(slo_name, current_value):
    slo_config = SLOs[slo_name]
    target = slo_config['slo']
    
    if slo_name == 'availability':
        compliant = current_value >= target
    else:
        compliant = current_value <= target
    
    if not compliant:
        alert(f"SLO violated: {slo_name} = {current_value} (target: {target})")
    
    return compliant
```

---

## 🌍 6. Multi-Region Architecture

### Single-Region vs Multi-Region

```
Single-Region (Simple):
┌──────────────────────────────────────────┐
│ us-east-1                                │
│ ├─ App servers                           │
│ ├─ Database (primary)                    │
│ └─ S3 bucket                             │
└──────────────────────────────────────────┘

Pros:
├─ Simple (no replication)
├─ Low latency (local reads/writes)
└─ Low cost (no cross-region transfer)

Cons:
├─ Single point of failure (region outage = downtime)
├─ High latency for distant users (Asia → us-east-1)
└─ No disaster recovery

Multi-Region (Complex):
┌──────────────────────────────────────────┐
│ us-east-1 (Primary)                      │
│ ├─ App servers                           │
│ ├─ Database (read replica)               │
│ └─ S3 bucket (replicated)                │
└──────────────────────────────────────────┘
         │ Replication
         ▼
┌──────────────────────────────────────────┐
│ eu-west-1 (Secondary)                    │
│ ├─ App servers                           │
│ ├─ Database (read replica)               │
│ └─ S3 bucket (replicated)                │
└──────────────────────────────────────────┘
         │ Replication
         ▼
┌──────────────────────────────────────────┐
│ ap-south-1 (Secondary)                   │
│ ├─ App servers                           │
│ ├─ Database (read replica)               │
│ └─ S3 bucket (replicated)                │
└──────────────────────────────────────────┘

Pros:
├─ High availability (region outage = failover)
├─ Low latency (route users to nearest region)
└─ Disaster recovery (multi-region backups)

Cons:
├─ Complex (replication, consistency)
├─ Higher cost (3x storage, cross-region transfer)
└─ Data consistency challenges (eventual consistency)
```

---

### Multi-Region Replication Strategies

```
1. Active-Passive (Disaster Recovery):
   ┌──────────────┐           ┌──────────────┐
   │ Primary      │ ────────► │ Secondary    │
   │ (us-east-1)  │ Async     │ (eu-west-1)  │
   │ - All writes │ Replication│ - Standby    │
   │ - All reads  │           │ - No traffic │
   └──────────────┘           └──────────────┘
   
   Normal: All traffic → Primary
   Failover: Traffic switches → Secondary
   
   Pros: Simple, low cost
   Cons: Secondary unused (wasted $), slow failover

2. Active-Active (Low Latency):
   ┌──────────────┐ ◄────────► ┌──────────────┐
   │ Region A     │ Bidirectional│ Region B     │
   │ (us-east-1)  │ Replication │ (eu-west-1)  │
   │ - US writes  │             │ - EU writes  │
   │ - US reads   │             │ - EU reads   │
   └──────────────┘             └──────────────┘
   
   Routing: DNS routes US users → Region A
           DNS routes EU users → Region B
   
   Pros: Low latency, high availability
   Cons: Complex (conflict resolution), high cost

3. Active-Active with Sharding:
   ┌──────────────┐             ┌──────────────┐
   │ Region A     │             │ Region B     │
   │ - Shard 0-99 │             │ - Shard 100- │
   │              │             │   199        │
   └──────────────┘             └──────────────┘
   
   Routing: user_id % 200 → Shard
           Shard 0-99 → Region A
           Shard 100-199 → Region B
   
   Pros: No conflicts (non-overlapping data)
   Cons: Cross-shard queries expensive
```

---

## 🔄 7. Disaster Recovery (RTO/RPO)

### Definitions

```
RTO (Recovery Time Objective):
├─ How long can we be down?
├─ Example: "Restore service within 4 hours"
└─ Metric: Time to recovery

RPO (Recovery Point Objective):
├─ How much data loss is acceptable?
├─ Example: "Lose at most 1 hour of data"
└─ Metric: Data loss window

┌────────────────────────────────────────────────┐
│ Timeline:                                      │
│                                                │
│ Last Backup   Disaster    Recovery             │
│     │            │            │                │
│     ▼            ▼            ▼                │
│ ────●────────────●────────────●────►           │
│     │◄───RPO────►│◄───RTO───►│                │
│                                                │
│ RPO: Data between last backup and disaster     │
│      is LOST (1 hour in this example)          │
│                                                │
│ RTO: Time to restore service (4 hours)         │
└────────────────────────────────────────────────┘
```

---

### RTO/RPO Tiers

```
┌──────┬─────────┬─────────┬───────────────┬──────────┐
│ Tier │ RTO     │ RPO     │ Strategy      │ Cost     │
├──────┼─────────┼─────────┼───────────────┼──────────┤
│ Gold │ Minutes │ Seconds │ Active-Active │ Very High│
│      │         │         │ Multi-region  │          │
│      │         │         │ Sync replica  │          │
├──────┼─────────┼─────────┼───────────────┼──────────┤
│Silver│ Hours   │ Minutes │ Active-Passive│ Medium   │
│      │         │         │ Async replica │          │
│      │         │         │ Warm standby  │          │
├──────┼─────────┼─────────┼───────────────┼──────────┤
│Bronze│ Days    │ Hours   │ Backups only  │ Low      │
│      │         │         │ Cold storage  │          │
│      │         │         │ Manual restore│          │
└──────┴─────────┴─────────┴───────────────┴──────────┘
```

---

### Example: Gold-Tier DR

```python
# Gold Tier: RTO=5 min, RPO=0 (no data loss)

# Architecture: Active-Active with synchronous replication

# Region A (Primary)
primary_db = Database(
    region='us-east-1',
    mode='read-write',
    replication='sync',
    replicas=['eu-west-1', 'ap-south-1'],
)

# Region B (Secondary)
secondary_db = Database(
    region='eu-west-1',
    mode='read-write',
    replication='sync',
    replicas=['us-east-1', 'ap-south-1'],
)

# Write path (synchronous):
def write_data(data):
    # Write to primary
    primary_db.write(data)
    
    # Wait for sync replication (blocks until all replicas ACK)
    wait_for_replication(replicas=['eu-west-1', 'ap-south-1'])
    
    # Return success only after all replicas confirm
    return 'success'

# Failover (automatic):
def health_check():
    if not primary_db.is_healthy():
        # Promote secondary to primary
        secondary_db.promote_to_primary()
        
        # Update DNS (Route 53 health check)
        update_dns(primary='eu-west-1')
        
        # Alert on-call
        page_oncall('Primary region down, failed over to eu-west-1')

# Cost: 3x compute + 3x storage + cross-region transfer
# RTO: 5 minutes (automatic failover)
# RPO: 0 seconds (synchronous replication, no data loss)
```

---

## 📊 Summary Checklist

- [ ] Understand fundamental trade-offs (latency vs consistency, cost vs performance)
- [ ] Apply CAP theorem and PACELC to system design
- [ ] Choose appropriate consistency model (linearizability to eventual)
- [ ] Optimize costs (spot instances, lifecycle policies, compression)
- [ ] Define SLAs, SLIs, SLOs with error budgets
- [ ] Design multi-region architectures (active-passive, active-active)
- [ ] Implement disaster recovery with RTO/RPO targets
- [ ] Build self-healing systems with backpressure

**Next:** [EXPERT.md →](EXPERT.md)
