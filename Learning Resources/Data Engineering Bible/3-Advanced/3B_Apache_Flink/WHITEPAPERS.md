# Week 8-9: Apache Flink — WHITEPAPERS Track

*"Reading the Flink, Dataflow Model, and Chandy-Lamport papers transforms you from a user of stream processing to an architect of distributed systems."* — Principal Engineer, LinkedIn

---

## 📜 Core Research Papers

This track covers the foundational research papers that define modern stream processing. Each paper is analyzed with context, key innovations, and practical implications.

---

## 1. Apache Flink: Stream and Batch Processing in a Single Engine (2015)

**Citation:**
Carbone, Paris, et al. "Apache Flink: Stream and batch processing in a single engine." Bulletin of the IEEE Computer Society Technical Committee on Data Engineering 38.4 (2015).

**Link:** http://sites.computer.org/debull/A15dec/p28.pdf

---

### 🎯 Context and Motivation

```
Problem (2015):
┌────────────────────────────────────────────────────────┐
│ Lambda Architecture (Nathan Marz, 2011):               │
│                                                        │
│ ┌──────────────┐                 ┌──────────────┐    │
│ │ Batch Layer  │ (Hadoop/Spark)  │ Speed Layer  │    │
│ │ (hours)      │                 │ (Storm)      │    │
│ └──────────────┘                 └──────────────┘    │
│        │                                 │            │
│        └────────────┬────────────────────┘            │
│                     ▼                                 │
│             ┌──────────────┐                          │
│             │ Serving Layer│                          │
│             └──────────────┘                          │
│                                                        │
│ Issues:                                               │
│ ├─ Two separate codebases (MapReduce + Storm)        │
│ ├─ Data inconsistency between batch and stream       │
│ ├─ High maintenance overhead                         │
│ └─ Eventual consistency only                         │
└────────────────────────────────────────────────────────┘

Flink's Vision: Kappa Architecture (Jay Kreps, 2014)
┌────────────────────────────────────────────────────────┐
│                                                        │
│          ┌─────────────────────────────┐              │
│          │  Unified Stream Processing  │              │
│          │  (Flink)                    │              │
│          └─────────────────────────────┘              │
│                     │                                 │
│                     ▼                                 │
│            ┌──────────────┐                           │
│            │ Serving Layer│                           │
│            └──────────────┘                           │
│                                                        │
│ Benefits:                                             │
│ ├─ Single codebase (batch = bounded stream)          │
│ ├─ Consistent semantics                              │
│ ├─ Lower operational complexity                      │
│ └─ Exactly-once guarantees                           │
└────────────────────────────────────────────────────────┘
```

---

### 🔬 Key Innovations

#### 1. Dataflow Programming Model

```
Flink Program = Directed Acyclic Graph (DAG)

User Code:
DataStream<Event> stream = env.addSource(kafkaSource);
stream
    .map(new ParseEvent())
    .keyBy(event -> event.getUserId())
    .window(TumblingEventTimeWindows.of(Time.minutes(1)))
    .sum("amount")
    .addSink(kafkaSink);

Compiled to JobGraph:
┌──────────┐
│  Source  │
└────┬─────┘
     │
     ▼
┌──────────┐
│   Map    │
└────┬─────┘
     │
     ▼
┌──────────┐
│  KeyBy   │ (Hash Partition)
└────┬─────┘
     │
     ▼
┌──────────┐
│  Window  │ (Stateful)
└────┬─────┘
     │
     ▼
┌──────────┐
│   Sum    │
└────┬─────┘
     │
     ▼
┌──────────┐
│   Sink   │
└──────────┘

Execution Graph (with parallelism=4):
┌────┐ ┌────┐ ┌────┐ ┌────┐
│Src1│ │Src2│ │Src3│ │Src4│
└─┬──┘ └─┬──┘ └─┬──┘ └─┬──┘
  │      │      │      │
  ▼      ▼      ▼      ▼
┌────┐ ┌────┐ ┌────┐ ┌────┐
│Map1│ │Map2│ │Map3│ │Map4│
└─┬──┘ └─┬──┘ └─┬──┘ └─┬──┘
  │      │      │      │
  └──────┴──────┴──────┘
         │ (Shuffle)
  ┌──────┴──────┬──────┐
  ▼      ▼      ▼      ▼
┌────┐ ┌────┐ ┌────┐ ┌────┐
│Win1│ │Win2│ │Win3│ │Win4│
└─┬──┘ └─┬──┘ └─┬──┘ └─┬──┘
  │      │      │      │
  ▼      ▼      ▼      ▼
┌────┐ ┌────┐ ┌────┐ ┌────┐
│Snk1│ │Snk2│ │Snk3│ │Snk4│
└────┘ └────┘ └────┘ └────┘
```

---

#### 2. Asynchronous Barrier Snapshotting (ABS)

**Based on Chandy-Lamport algorithm (see next paper)**

```
Innovation: Non-blocking distributed snapshots

Traditional Approach (pause-the-world):
T=0:  Stop all processing
T=1:  Snapshot all state
T=2:  Resume processing
Cost: Downtime = 1-10 seconds

Flink ABS Approach:
T=0:  Inject checkpoint barriers into streams
T=0-5: Process data concurrently with checkpointing
T=5:  Checkpoint completes
Cost: No downtime, millisecond overhead

Algorithm:
1. JobManager triggers checkpoint N
2. Sources emit barrier(N) into data stream
3. Operators:
   - Receive barrier from all inputs (alignment)
   - Snapshot local state
   - Forward barrier to outputs
4. Sinks acknowledge checkpoint N
5. JobManager marks checkpoint N complete

State Snapshot Includes:
├─ Operator state (keyed state, operator state)
├─ In-flight data (for unaligned checkpoints)
├─ Source positions (Kafka offsets, file pointers)
└─ Metadata (checkpoint ID, timestamp)
```

---

#### 3. Pipelined Execution Engine

```
Traditional Batch (MapReduce):
Map Phase:   [====100%====] → Write to disk
                                   ↓
Reduce Phase:                [====100%====] → Write to disk

Latency: Minutes to hours

Flink Pipelined Execution:
Source → Map → KeyBy → Window → Sink
  ↓      ↓      ↓       ↓       ↓
 [====== continuous data flow ======]

Latency: Milliseconds

Key Difference:
├─ No materialization between operators
├─ Data flows through memory (network buffers)
├─ Backpressure propagates upstream
└─ Enables true streaming
```

---

#### 4. Memory Management

```
JVM Heap vs Flink Managed Memory:

Standard JVM Approach:
┌──────────────────────────────────────┐
│ JVM Heap (all objects)               │
│ ├─ Application objects               │
│ ├─ Intermediate results              │
│ └─ Cached data                       │
│                                      │
│ Problem:                             │
│ ├─ Full GC pauses (10+ seconds)     │
│ └─ OutOfMemoryError unpredictable   │
└──────────────────────────────────────┘

Flink Managed Memory:
┌──────────────────────────────────────┐
│ JVM Heap (small, controlled)         │
│ ├─ Application objects               │
│ └─ Flink framework objects           │
└──────────────────────────────────────┘
┌──────────────────────────────────────┐
│ Off-Heap Managed Memory              │
│ ├─ Sorting/Hashing (batch)           │
│ ├─ RocksDB state (streaming)         │
│ └─ Network buffers                   │
│                                      │
│ Benefits:                            │
│ ├─ Predictable memory usage          │
│ ├─ No GC overhead                    │
│ └─ Efficient serialization           │
└──────────────────────────────────────┘

Configuration:
taskmanager.memory.process.size: 4096m
├─ Framework Heap: 128m (Flink internals)
├─ Task Heap: 512m (user code)
├─ Managed Memory: 1638m (40%, for RocksDB)
├─ Network Memory: 409m (10%, for shuffle)
└─ JVM Overhead: 409m (10%, for JVM)
```

---

### 💡 Practical Implications

```
1. Batch as Bounded Stream:
   - Write once, run in batch or streaming mode
   - Same code for historical analysis and real-time

2. State as First-Class Citizen:
   - Persistent, fault-tolerant state
   - Enables complex stateful computations

3. Exactly-Once Guarantees:
   - ABS + transactional sinks
   - Production-ready consistency

4. High Throughput + Low Latency:
   - Pipelined execution: <10ms latency
   - Millions of events/second per core
```

---

## 2. Lightweight Asynchronous Snapshots for Distributed Dataflows (2015)

**Citation:**
Carbone, Paris, et al. "Lightweight asynchronous snapshots for distributed dataflows." arXiv preprint arXiv:1506.08603 (2015).

**Link:** https://arxiv.org/pdf/1506.08603.pdf

---

### 🎯 The Distributed Snapshot Problem

```
Given:
- Distributed system with N processes
- Communication via message passing
- Continuous execution (no global clock)

Goal:
- Capture consistent global state
- Without stopping execution
- Such that: State can be used for recovery

Consistency Definition:
A snapshot is consistent if:
∀ message m: 
  If receive(m) is in snapshot → send(m) is in snapshot
  (No "orphan" messages)

Example of INCONSISTENT snapshot:
Process A: state = {sent: $100 to B}
Process B: state = {received: $0}
Problem: $100 lost!

Example of CONSISTENT snapshot:
Process A: state = {sent: $100 to B}
Process B: state = {received: $100}
OR:
Process A: state = {balance: $100}
Process B: state = {balance: $0}
In-flight: [$100 transfer]
```

---

### 🔬 Chandy-Lamport Algorithm (1985)

**Original Paper:** Chandy, K. M., and Leslie Lamport. "Distributed snapshots: Determining global states of distributed systems." ACM Transactions on Computer Systems (1985).

```
Algorithm:

Initiator Process Pi:
1. Record own state
2. Send MARKER on all outgoing channels
3. Start recording incoming messages

Non-Initiator Process Pj (receives MARKER from Pk):
IF first MARKER:
   1. Record own state
   2. Mark channel Pk→Pj state as empty
   3. Send MARKER on all outgoing channels
   4. Start recording messages on OTHER channels
ELSE:
   1. Stop recording channel Pk→Pj
   2. Channel state = recorded messages

Termination: All processes recorded + all channel states recorded

Example (3 processes):
┌────────────────────────────────────────────────────────┐
│ T=0: P1 initiates                                      │
│ ├─ P1: state = {x=10}                                 │
│ ├─ P1 sends: MARKER → P2, MARKER → P3                 │
│ └─ P1 records: channel P2→P1, channel P3→P1           │
│                                                        │
│ T=1: P2 receives MARKER from P1                       │
│ ├─ P2: state = {y=20}                                 │
│ ├─ P2: channel P1→P2 = {} (empty)                     │
│ ├─ P2 sends: MARKER → P1, MARKER → P3                 │
│ └─ P2 records: channel P3→P2                          │
│                                                        │
│ T=2: P3 receives MARKER from P1                       │
│ ├─ P3: state = {z=30}                                 │
│ ├─ P3: channel P1→P3 = {}                             │
│ ├─ P3 sends: MARKER → P1, MARKER → P2                 │
│ └─ P3 records: channel P2→P3                          │
│                                                        │
│ T=3: P2 receives MARKER from P3                       │
│ ├─ P2 stops recording channel P3→P2                   │
│ └─ P2: channel P3→P2 = {msg1, msg2}                   │
│                                                        │
│ ... (all markers received) ...                        │
│                                                        │
│ Global Snapshot:                                       │
│ ├─ P1: {x=10}                                         │
│ ├─ P2: {y=20}                                         │
│ ├─ P3: {z=30}                                         │
│ └─ Channels: P3→P2 = {msg1, msg2}, ...               │
└────────────────────────────────────────────────────────┘
```

---

### 🚀 Flink's Adaptation: Barrier Snapshotting

```
Differences from Chandy-Lamport:

1. Markers → Checkpoint Barriers
   - Injected at sources (not arbitrary process)
   - Flow with data stream

2. Channel State Recording → Barrier Alignment
   - Buffer data between first and last barrier
   - Ensures exactly-once semantics

3. Asynchronous State Snapshot
   - Use copy-on-write (e.g., RocksDB snapshots)
   - No blocking of processing

Flink Algorithm:

Source Operators (on checkpoint trigger):
1. Snapshot source state (Kafka offsets, file position)
2. Emit barrier(checkpoint_id) into output stream
3. Acknowledge checkpoint

Stateful Operators (on barrier arrival):
1. IF multiple inputs:
      WAIT for barriers from ALL inputs (alignment)
      BUFFER late-arriving data
2. Snapshot operator state:
   - ValueState, ListState, MapState, etc.
   - Window contents
   - Timers
3. Emit barrier to downstream operators
4. Acknowledge checkpoint

Sink Operators (on barrier arrival):
1. Snapshot sink state (transactional state)
2. Pre-commit pending transactions (2PC phase 1)
3. Acknowledge checkpoint

JobManager (on all acknowledgments):
1. Mark checkpoint as COMPLETED
2. Notify sinks to COMMIT transactions (2PC phase 2)
3. Store checkpoint metadata
4. Trigger cleanup of old checkpoints
```

---

### 📊 Performance Analysis

```
Metrics from Paper:

Checkpoint Latency (time to complete):
├─ Small state (<1 GB): 50-200ms
├─ Medium state (1-10 GB): 200ms-2s
└─ Large state (>10 GB): 2-10s (with incremental)

Overhead on Throughput:
├─ Aligned checkpoints: 1-5% throughput decrease
├─ Unaligned checkpoints: <1% throughput decrease
└─ Network overhead: ~2% (barrier messages)

State Snapshot Methods:
┌─────────────────────────────────────────────────────┐
│ Method            │ Time      │ Blocking │ Size    │
├───────────────────┼───────────┼──────────┼─────────┤
│ Synchronous copy  │ O(state)  │ Yes      │ Full    │
│ Copy-on-write     │ O(1)      │ No       │ Full    │
│ Incremental       │ O(delta)  │ No       │ Delta   │
└─────────────────────────────────────────────────────┘

RocksDB Incremental Checkpointing:
- Uses SST file sharing
- Checkpoint time: O(modified data)
- 10x faster for large state (paper shows 100GB → 1GB delta)
```

---

### 💡 Practical Implications

```
1. Exactly-Once Guarantees:
   - Barrier alignment ensures no duplicates
   - Combined with transactional sinks (2PC)

2. Minimal Performance Impact:
   - Asynchronous snapshots (no pause-the-world)
   - Sub-second checkpoints for most workloads

3. Failure Recovery:
   - Restore state from last checkpoint
   - Replay source from checkpointed position
   - Mean time to recovery (MTTR): <1 minute

4. Tuning Trade-offs:
   Checkpoint Interval:
   ├─ Short (10s): Fast recovery, higher overhead
   ├─ Medium (1min): Balanced
   └─ Long (10min): Low overhead, slower recovery

   Aligned vs Unaligned:
   ├─ Aligned: Smaller checkpoints, may cause backpressure
   └─ Unaligned: Faster under backpressure, larger checkpoints
```

---

## 3. The Dataflow Model (2015)

**Citation:**
Akidau, Tyler, et al. "The dataflow model: a practical approach to balancing correctness, latency, and cost in massive-scale, unbounded, out-of-order data processing." Proceedings of the VLDB Endowment 8.12 (2015): 1792-1803.

**Link:** http://www.vldb.org/pvldb/vol8/p1792-Akidau.pdf

---

### 🎯 The Four Questions

```
Framework for reasoning about stream processing:

1. WHAT results are calculated?
   → Transformations, aggregations, windows

2. WHERE in event time are results calculated?
   → Event time windows, processing time windows

3. WHEN in processing time are results materialized?
   → Triggers (early, on-time, late)

4. HOW do refinements relate to each other?
   → Accumulation modes (discarding, accumulating, retracting)
```

---

### 🔬 Windowing and Triggers

```
Example: 1-minute tumbling event time windows

Stream of events (event_time, processing_time):
├─ e1: (10:00:05, 10:00:07)
├─ e2: (10:00:30, 10:00:32)
├─ e3: (10:00:45, 10:00:47)
├─ e4: (10:01:10, 10:01:12)
├─ e5: (10:00:50, 10:01:15)  ← LATE by 15 seconds!

Window: [10:00:00, 10:01:00)

Trigger Strategies:

1. Watermark Trigger (ON-TIME):
   Fires when: watermark passes window end
   ├─ Watermark = max_event_time - allowed_lateness
   ├─ If allowed_lateness = 5s:
   │  └─ Watermark(10:01:05) → Trigger window [10:00, 10:01)
   └─ Result: [e1, e2, e3] (e5 missed, it's late)

2. Early Trigger (SPECULATIVE):
   Fires when: Every N records or M seconds
   ├─ Every 2 events:
   │  ├─ After e1, e2: Emit partial result
   │  └─ After e3: Emit updated result
   └─ Allows early insights (trading accuracy)

3. Late Trigger (REFINEMENT):
   Fires when: Late data arrives after watermark
   ├─ e5 arrives (late)
   ├─ Re-trigger window [10:00, 10:01)
   └─ Emit refined result: [e1, e2, e3, e5]

Combined Triggering:
stream
    .keyBy(...)
    .window(TumblingEventTimeWindows.of(Time.minutes(1)))
    .trigger(
        EventTimeTrigger.create()
            .withEarlyFirings(ProcessingTimeTrigger.every(Time.seconds(10)))
            .withLateFirings(AfterWatermark.pastEndOfWindow())
    )
    .sum("amount");
```

---

### 📐 Accumulation Modes

```
Question: How do we handle multiple outputs for same window?

Given events for window [10:00, 10:01):
├─ Early trigger (10s): [e1, e2] → sum=30
├─ Early trigger (20s): [e1, e2, e3] → sum=80
├─ On-time trigger: [e1, e2, e3, e4] → sum=120
└─ Late trigger: [e1, e2, e3, e4, e5] → sum=135

1. DISCARDING:
   - Emit only NEW data since last trigger
   - Output: 30, 50 (Δ), 40 (Δ), 15 (Δ)
   - Use case: Incremental updates (Kafka compaction)

2. ACCUMULATING:
   - Emit cumulative results
   - Output: 30, 80, 120, 135
   - Use case: Replacing previous result (overwrite table)

3. ACCUMULATING & RETRACTING:
   - Emit: (retract old, emit new)
   - Output: +30, (-30, +80), (-80, +120), (-120, +135)
   - Use case: Changelogs, correct downstream aggregations

Flink Implementation:
// Discarding
.window(...).evictor(CountEvictor.of(0))

// Accumulating (default)
.window(...).sum("amount")

// Retracting (for SQL)
tableEnv.executeSql("SELECT SUM(amount) FROM events GROUP BY TUMBLE(ts, INTERVAL '1' MINUTE)")
// Produces retraction stream
```

---

### 💡 Allowed Lateness

```
Configuration:

stream
    .keyBy(...)
    .window(TumblingEventTimeWindows.of(Time.minutes(1)))
    .allowedLateness(Time.minutes(5))  // Accept late data up to 5 min
    .sideOutputLateData(lateOutputTag)  // Capture very late data
    .sum("amount");

Behavior:
Window [10:00, 10:01):

T=10:01:05: Watermark passes 10:01:00
├─ Trigger ON-TIME: [e1, e2, e3] → sum=80
├─ Keep window state (don't discard yet)

T=10:02:30: Late event e4 arrives (timestamp=10:00:50)
├─ e4 is within allowed lateness (< 5 min late)
├─ Add to window state
├─ Trigger LATE: [e1, e2, e3, e4] → sum=95

T=10:06:05: Watermark passes 10:06:00
├─ Allowed lateness expires (10:01 + 5min)
├─ Discard window state

T=10:07:00: Very late event e5 arrives (timestamp=10:00:55)
├─ e5 is beyond allowed lateness
├─ Emit to side output (lateOutputTag)
└─ Do NOT update window

Side output handling:
DataStream<Event> veryLateEvents = result.getSideOutput(lateOutputTag);
veryLateEvents.addSink(new KafkaSink("late-events"));
```

---

### 📊 Performance Trade-offs

```
From Paper (Google Cloud Dataflow):

Latency vs Correctness:
┌────────────────────────────────────────────────────┐
│ Processing Time Windows:                           │
│ ├─ Latency: Low (~100ms)                          │
│ ├─ Correctness: Low (skewed by delays)            │
│ └─ Cost: Low (no state for late data)             │
│                                                    │
│ Event Time Windows (no late data):                │
│ ├─ Latency: Medium (~1s, watermark delay)         │
│ ├─ Correctness: High (deterministic)              │
│ └─ Cost: Medium (watermark computation)           │
│                                                    │
│ Event Time + Allowed Lateness:                    │
│ ├─ Latency: High (wait for late data)             │
│ ├─ Correctness: Very High (99.9% completeness)    │
│ └─ Cost: High (retain state, recomputation)       │
└────────────────────────────────────────────────────┘

Recommendation:
- Real-time dashboards: Early triggers, discarding mode
- Financial aggregations: Allowed lateness, accumulating mode
- ML training: Processing time (latency critical)
- Analytics: Event time + late firings (accuracy critical)
```

---

## 🏆 Interview Discussion Topics

1. **Compare Chandy-Lamport with Flink's barrier snapshotting. What are the key differences?**

2. **Explain the "WHAT/WHERE/WHEN/HOW" questions from the Dataflow Model. Give examples.**

3. **How would you configure triggers for a real-time analytics dashboard that needs to show results every 10 seconds but still handle late data?**

4. **What are the trade-offs between aligned and unaligned checkpoints? When would you use each?**

5. **Describe RocksDB incremental checkpointing. Why is it faster for large state?**

6. **How does Flink achieve exactly-once semantics end-to-end? Explain the role of ABS and two-phase commit.**

---

## 🎓 Summary Checklist

- [ ] Understand Flink's dataflow programming model
- [ ] Explain asynchronous barrier snapshotting (ABS)
- [ ] Master Chandy-Lamport distributed snapshots
- [ ] Apply Dataflow Model's four questions
- [ ] Configure triggers and allowed lateness
- [ ] Understand accumulation modes (discarding, accumulating, retracting)
- [ ] Answer whitepaper-based interview questions

**Next:** [README.md →](README.md)
