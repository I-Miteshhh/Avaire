# Week 8-9: Apache Flink — INTERMEDIATE Track

*"Flink's checkpointing mechanism enables exactly-once processing with millisecond latencies. Understanding the JobManager, TaskManager architecture and state backends is critical for production deployments."* — Flink Committer

---

## 🎯 Learning Outcomes

By the end of this track, you will:
- Master Flink runtime architecture (JobManager, TaskManagers, slots)
- Understand checkpointing internals and recovery mechanisms
- Configure state backends (Memory, FsStateBackend, RocksDB)
- Implement custom operators and ProcessFunctions
- Optimize Flink jobs for throughput and latency
- Design fault-tolerant streaming pipelines

---

## 🏗️ 1. Flink Runtime Architecture

### Component Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client (Job Submission)                   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                          JobManager                              │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────────────┐     │
│  │ JobGraph      │  │ Scheduler    │  │ Checkpoint       │     │
│  │ (DAG of tasks)│  │              │  │ Coordinator      │     │
│  └───────────────┘  └──────────────┘  └──────────────────┘     │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
        ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
        │ TaskManager  │ │ TaskManager  │ │ TaskManager  │
        │              │ │              │ │              │
        │ ┌──────────┐ │ │ ┌──────────┐ │ │ ┌──────────┐ │
        │ │  Slot 1  │ │ │ │  Slot 1  │ │ │ │  Slot 1  │ │
        │ ├──────────┤ │ │ ├──────────┤ │ │ ├──────────┤ │
        │ │  Slot 2  │ │ │ │  Slot 2  │ │ │ │  Slot 2  │ │
        │ └──────────┘ │ │ └──────────┘ │ │ └──────────┘ │
        └──────────────┘ └──────────────┘ └──────────────┘
```

### JobManager Responsibilities

```
1. Job Submission & Planning:
   ├─ Receive JobGraph from client
   ├─ Convert JobGraph → ExecutionGraph
   ├─ Schedule tasks to TaskManagers
   └─ Track task execution status

2. Checkpoint Coordination:
   ├─ Trigger periodic checkpoints
   ├─ Collect checkpoint acknowledgments
   ├─ Store checkpoint metadata
   └─ Orchestrate recovery on failure

3. Resource Management:
   ├─ Allocate slots from TaskManagers
   ├─ Handle slot sharing and co-location
   └─ Rescale jobs (dynamic scaling)

4. High Availability:
   ├─ Standby JobManager for failover
   ├─ Store state in ZooKeeper/K8s
   └─ Recover from JobManager failure
```

**Configuration:**

```yaml
# flink-conf.yaml
jobmanager.memory.process.size: 1600m
jobmanager.rpc.address: localhost
jobmanager.rpc.port: 6123
jobmanager.bind-host: 0.0.0.0

# High Availability (ZooKeeper)
high-availability: zookeeper
high-availability.storageDir: hdfs:///flink/ha/
high-availability.zookeeper.quorum: zk1:2181,zk2:2181,zk3:2181
high-availability.zookeeper.path.root: /flink
```

---

### TaskManager Responsibilities

```
1. Task Execution:
   ├─ Execute operator tasks in slots
   ├─ Manage local state (memory or RocksDB)
   ├─ Buffer data for network transport
   └─ Report metrics to JobManager

2. Network Communication:
   ├─ Send data to downstream operators (network buffers)
   ├─ Apply backpressure when buffers full
   └─ Handle data shuffling (hash partitioning, broadcasting)

3. State Management:
   ├─ Store keyed state locally
   ├─ Participate in checkpointing
   └─ Restore state from checkpoints

4. Resource Isolation:
   ├─ Each slot = isolated resources (CPU, memory)
   ├─ Slots can share pipeline (slot sharing)
   └─ Prevents resource contention
```

**Configuration:**

```yaml
taskmanager.memory.process.size: 4096m
taskmanager.numberOfTaskSlots: 4
taskmanager.network.memory.fraction: 0.1
taskmanager.network.memory.min: 64mb
taskmanager.network.memory.max: 1gb

# Managed Memory (for RocksDB, sorting, etc.)
taskmanager.memory.managed.fraction: 0.4
```

---

### Task Slots and Parallelism

```
Example: 3 TaskManagers, 2 slots each = 6 total slots

Job with parallelism=6:

┌─────────────────────────────────────────────────────────────┐
│ Operator: Source (parallelism=6)                            │
│ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌──│
│ │Source-1│ │Source-2│ │Source-3│ │Source-4│ │Source-5│ │S.│
│ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └──│
│      │          │          │          │          │       │  │
│      ▼          ▼          ▼          ▼          ▼       ▼  │
│ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌──│
│ │ Map-1  │ │ Map-2  │ │ Map-3  │ │ Map-4  │ │ Map-5  │ │M.│
│ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └──│
│      │          │          │          │          │       │  │
│      └──────────┴──────────┴──────────┴──────────┴───────┘  │
│                           │ (Hash Partition)                 │
│                           ▼                                  │
│ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌──│
│ │KeyBy-1 │ │KeyBy-2 │ │KeyBy-3 │ │KeyBy-4 │ │KeyBy-5 │ │K.│
│ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └──│
└─────────────────────────────────────────────────────────────┘

Slot Allocation (with slot sharing):
TM1-Slot1: Source-1 → Map-1 → KeyBy-1
TM1-Slot2: Source-2 → Map-2 → KeyBy-2
TM2-Slot1: Source-3 → Map-3 → KeyBy-3
TM2-Slot2: Source-4 → Map-4 → KeyBy-4
TM3-Slot1: Source-5 → Map-5 → KeyBy-5
TM3-Slot2: Source-6 → Map-6 → KeyBy-6
```

**Key Concepts:**

```java
// Set parallelism at different levels:

// 1. Global default
env.setParallelism(4);

// 2. Per operator
stream
    .map(new MyMapper()).setParallelism(8)  // Override
    .keyBy(...)
    .window(...)
    .aggregate(new MyAgg()).setParallelism(4);  // Different parallelism

// 3. Command-line override
./bin/flink run -p 16 MyJob.jar
```

---

## 🔒 2. Checkpointing Internals

### Checkpoint Barrier Mechanism

```
Concept: Asynchronous Barrier Snapshotting (Chandy-Lamport variant)

Stream of events with barriers:

Source 1:  [e1] [e2] ──BARRIER(ckpt-5)── [e3] [e4]
Source 2:  [e5] ──BARRIER(ckpt-5)── [e6] [e7] [e8]
                    │
                    ▼
            ┌──────────────┐
            │ Map Operator │
            └──────────────┘
                    │
When barrier arrives at operator:
1. Align barriers from all inputs (wait for slowest)
2. Snapshot local state
3. Acknowledge checkpoint to JobManager
4. Forward barrier to downstream operators
```

### Checkpoint Process (Step-by-Step)

```
Timeline of Checkpoint 5:

T=0ms:  JobManager triggers checkpoint 5
        ├─ Send RPC to all sources: "Emit barrier for ckpt-5"

T=5ms:  Sources emit barriers into streams
        ├─ Source-1: ... [e1] [e2] ──BARRIER(5)── [e3] ...
        ├─ Source-2: ... [e5] ──BARRIER(5)── [e6] ...
        └─ Source-3: ... [e9] ──BARRIER(5)── [e10] ...

T=10ms: Barriers flow through operators
        ├─ Map operators receive barriers
        ├─ Snapshot local state (if any)
        └─ Forward barriers downstream

T=15ms: KeyBy operators (stateful) receive barriers
        ├─ Align barriers from all upstream tasks
        ├─ Snapshot keyed state:
        │  - ValueState, ListState, MapState
        │  - Window buffers
        │  - Timers
        ├─ Write state to state backend (async)
        └─ Acknowledge to JobManager

T=20ms: JobManager receives all acknowledgments
        ├─ Mark checkpoint 5 as COMPLETED
        ├─ Store checkpoint metadata:
        │  {
        │    "checkpointId": 5,
        │    "timestamp": 1697385600000,
        │    "stateHandles": [
        │      "s3://bucket/ckpt-5/task-1/state",
        │      "s3://bucket/ckpt-5/task-2/state",
        │      ...
        │    ]
        │  }
        └─ Trigger cleanup of old checkpoints (ckpt-3)

Total latency: 20ms (typical for small state)
```

---

### Checkpoint Configuration

```java
StreamExecutionEnvironment env = 
    StreamExecutionEnvironment.getExecutionEnvironment();

// Enable checkpointing every 60 seconds
env.enableCheckpointing(60000);

// Checkpoint configuration
CheckpointConfig config = env.getCheckpointConfig();

// 1. Checkpoint mode (exactly-once vs at-least-once)
config.setCheckpointingMode(CheckpointingMode.EXACTLY_ONCE);

// 2. Minimum pause between checkpoints (avoid back-to-back)
config.setMinPauseBetweenCheckpoints(30000);  // 30 seconds

// 3. Checkpoint timeout (fail if not completed)
config.setCheckpointTimeout(300000);  // 5 minutes

// 4. Max concurrent checkpoints
config.setMaxConcurrentCheckpoints(1);  // Only 1 at a time

// 5. Externalized checkpoints (survive job cancellation)
config.enableExternalizedCheckpoints(
    ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION
);

// 6. Tolerate failed checkpoints
config.setTolerableCheckpointFailureNumber(3);  // Fail job after 3 failures

// 7. Unaligned checkpoints (faster for high backpressure)
config.enableUnalignedCheckpoints();
```

**State Backend Configuration:**

```java
// Store checkpoints in HDFS/S3
env.setStateBackend(new HashMapStateBackend());
env.getCheckpointConfig().setCheckpointStorage("s3://my-bucket/checkpoints");

// OR use RocksDB for large state
env.setStateBackend(new EmbeddedRocksDBStateBackend());
env.getCheckpointConfig().setCheckpointStorage("hdfs:///flink/checkpoints");
```

---

### Barrier Alignment vs Unaligned Checkpoints

```
Aligned Checkpoints (Default):
┌─────────────────────────────────────────────────────────┐
│ Input 1:  [e1] [e2] ──BARRIER── [e3] [e4] [e5]        │
│ Input 2:  [e6] ──BARRIER── [e7] [e8] [e9] [e10]       │
│                                                         │
│ Operator waits for barriers from ALL inputs:           │
│ ├─ Buffer events from Input 1 (e3, e4, e5)            │
│ ├─ Process events from Input 2 until barrier arrives  │
│ └─ When both barriers received → snapshot state       │
│                                                         │
│ Problem: High backpressure if one input is slow!      │
└─────────────────────────────────────────────────────────┘

Unaligned Checkpoints (Flink 1.11+):
┌─────────────────────────────────────────────────────────┐
│ Input 1:  [e1] [e2] ──BARRIER── [e3] [e4] [e5]        │
│ Input 2:  [e6] ──BARRIER── [e7] [e8] [e9] [e10]       │
│                                                         │
│ Operator snapshots state immediately when first        │
│ barrier arrives:                                        │
│ ├─ Snapshot in-flight buffers (e3, e4, e5)            │
│ ├─ Snapshot operator state                            │
│ └─ Continue processing without blocking                │
│                                                         │
│ Benefit: Faster checkpoints under backpressure!       │
│ Cost: Larger checkpoint size (includes buffers)       │
└─────────────────────────────────────────────────────────┘
```

---

## 💾 3. State Backends

### Comparison

```
┌─────────────────────┬────────────────────┬──────────────────────┐
│ State Backend       │ Storage            │ Use Case             │
├─────────────────────┼────────────────────┼──────────────────────┤
│ HashMapStateBackend │ JVM Heap           │ Small state (<100MB) │
│ (MemoryStateBackend)│ (synchronous)      │ Low latency          │
│                     │                    │ Development/testing  │
├─────────────────────┼────────────────────┼──────────────────────┤
│ EmbeddedRocksDB     │ Local disk (RocksDB│ Large state (>100GB) │
│ StateBackend        │ LSM-tree)          │ Production           │
│                     │ (asynchronous)     │ Disk I/O tolerance   │
└─────────────────────┴────────────────────┴──────────────────────┘
```

### HashMapStateBackend (In-Memory)

```java
import org.apache.flink.runtime.state.hashmap.HashMapStateBackend;
import org.apache.flink.runtime.state.storage.FileSystemCheckpointStorage;

StreamExecutionEnvironment env = ...;

// State stored in JVM heap
env.setStateBackend(new HashMapStateBackend());

// Checkpoints written to filesystem
env.getCheckpointConfig().setCheckpointStorage(
    new FileSystemCheckpointStorage("s3://my-bucket/checkpoints")
);
```

**Architecture:**

```
TaskManager JVM Heap:
┌──────────────────────────────────────────────────┐
│ Task Slot 1:                                     │
│ ┌──────────────────────────────────────────────┐ │
│ │ Keyed State (HashMap):                       │ │
│ │ ┌────────────────────────────────────┐       │ │
│ │ │ user_id=123 → ValueState(count=5)  │       │ │
│ │ │ user_id=456 → ValueState(count=12) │       │ │
│ │ │ user_id=789 → ValueState(count=3)  │       │ │
│ │ └────────────────────────────────────┘       │ │
│ └──────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘

Checkpoint:
├─ Serialize HashMap → byte[]
├─ Write to S3/HDFS (synchronously)
└─ Checkpoint completes when all writes finish
```

**Pros:**
- Ultra-low latency (no disk I/O)
- Simple configuration

**Cons:**
- Limited by JVM heap size
- Full GC pauses for large state
- Synchronous checkpoints (blocks processing)

---

### EmbeddedRocksDBStateBackend (Disk-Based)

```java
import org.apache.flink.contrib.streaming.state.EmbeddedRocksDBStateBackend;
import org.apache.flink.contrib.streaming.state.PredefinedOptions;

StreamExecutionEnvironment env = ...;

EmbeddedRocksDBStateBackend rocksDB = new EmbeddedRocksDBStateBackend();

// Predefined tuning profiles
rocksDB.setPredefinedOptions(PredefinedOptions.SPINNING_DISK_OPTIMIZED);
// OR: FLASH_SSD_OPTIMIZED, SPINNING_DISK_OPTIMIZED_HIGH_MEM

// Custom RocksDB options
rocksDB.setOptions(new OptionsFactory() {
    @Override
    public DBOptions createDBOptions(DBOptions currentOptions, Collection<AutoCloseable> handlesToClose) {
        return currentOptions
            .setMaxBackgroundJobs(4)
            .setMaxOpenFiles(1000);
    }
    
    @Override
    public ColumnFamilyOptions createColumnOptions(ColumnFamilyOptions currentOptions, Collection<AutoCloseable> handlesToClose) {
        return currentOptions
            .setCompactionStyle(CompactionStyle.LEVEL)
            .setWriteBufferSize(64 * 1024 * 1024);  // 64 MB
    }
});

env.setStateBackend(rocksDB);
env.getCheckpointConfig().setCheckpointStorage("s3://my-bucket/checkpoints");
```

**Architecture:**

```
TaskManager Local Disk (RocksDB):
┌──────────────────────────────────────────────────┐
│ /tmp/flink-state/                                │
│ ├─ operator-1/                                   │
│ │  ├─ db/ (RocksDB files)                        │
│ │  │  ├─ 000123.sst (Level 0)                    │
│ │  │  ├─ 000456.sst (Level 1)                    │
│ │  │  └─ MANIFEST                                │
│ │  └─ checkpoint-5/ (incremental checkpoint)     │
│ │     ├─ shared/ (SST files unchanged)           │
│ │     └─ private/ (new SST files)                │
│ └─ operator-2/                                   │
└──────────────────────────────────────────────────┘

State Access:
├─ get(key) → RocksDB JNI call → Read from disk (cached in block cache)
├─ put(key, value) → Write to memtable → Flush to SST
└─ Asynchronous background compaction
```

**Incremental Checkpointing:**

```
Checkpoint 1:  [sst-1, sst-2, sst-3]
Checkpoint 2:  [sst-1, sst-2, sst-4, sst-5]  (reuse sst-1, sst-2)
Checkpoint 3:  [sst-1, sst-4, sst-6]          (reuse sst-1, sst-4)

Only new/modified SST files are uploaded!
Reduces checkpoint time from minutes to seconds.
```

```java
rocksDB.enableIncrementalCheckpointing(true);
```

**Pros:**
- Supports state > TaskManager memory
- Asynchronous snapshots (no blocking)
- Incremental checkpoints (faster)

**Cons:**
- Higher latency (disk I/O)
- RocksDB tuning required
- Disk space requirements

---

## ⚙️ 4. ProcessFunction: Custom Operators

### KeyedProcessFunction

```java
import org.apache.flink.streaming.api.functions.KeyedProcessFunction;
import org.apache.flink.util.Collector;

public class TimeoutDetector extends KeyedProcessFunction<String, Event, Alert> {
    
    private ValueState<Long> lastEventTimeState;
    
    @Override
    public void open(Configuration config) {
        ValueStateDescriptor<Long> descriptor = 
            new ValueStateDescriptor<>("lastEventTime", Long.class);
        lastEventTimeState = getRuntimeContext().getState(descriptor);
    }
    
    @Override
    public void processElement(
        Event event,
        Context ctx,
        Collector<Alert> out
    ) throws Exception {
        
        // Update last event time
        lastEventTimeState.update(event.getTimestamp());
        
        // Register timer: Fire if no event in next 60 seconds
        long timerTimestamp = event.getTimestamp() + 60_000;
        ctx.timerService().registerEventTimeTimer(timerTimestamp);
    }
    
    @Override
    public void onTimer(
        long timestamp,
        OnTimerContext ctx,
        Collector<Alert> out
    ) throws Exception {
        
        Long lastEventTime = lastEventTimeState.value();
        
        // Check if timeout occurred (no event in 60 seconds)
        if (timestamp - lastEventTime >= 60_000) {
            out.collect(new Alert(
                ctx.getCurrentKey(),
                "No activity for 60 seconds"
            ));
        }
    }
}
```

**Usage:**

```java
stream
    .keyBy(event -> event.getUserId())
    .process(new TimeoutDetector());
```

---

### Side Outputs (Multi-Stream Output)

```java
public class SplitStream extends ProcessFunction<Event, Event> {
    
    // Define side output tags
    private static final OutputTag<Event> highValueTag = 
        new OutputTag<Event>("high-value"){};
    
    private static final OutputTag<Event> lowValueTag = 
        new OutputTag<Event>("low-value"){};
    
    @Override
    public void processElement(
        Event event,
        Context ctx,
        Collector<Event> out
    ) {
        if (event.getValue() > 1000) {
            ctx.output(highValueTag, event);  // Side output
        } else if (event.getValue() < 100) {
            ctx.output(lowValueTag, event);   // Side output
        } else {
            out.collect(event);  // Main output
        }
    }
}

// Usage:
SingleOutputStreamOperator<Event> mainStream = stream.process(new SplitStream());

DataStream<Event> highValueStream = mainStream.getSideOutput(highValueTag);
DataStream<Event> lowValueStream = mainStream.getSideOutput(lowValueTag);
```

---

## 📈 5. Performance Optimization

### Parallelism Tuning

```
Rule of thumb:
├─ Parallelism = Number of Kafka partitions (for source alignment)
├─ Slots per TaskManager = Number of CPU cores
└─ TaskManagers = Total parallelism / slots per TM

Example:
├─ Kafka topic: 64 partitions
├─ Desired parallelism: 64
├─ TaskManager: 8 slots (8-core machines)
└─ Required TaskManagers: 64 / 8 = 8
```

```java
// Set parallelism to match Kafka partitions
env.setParallelism(64);

// Source inherits parallelism (64 parallel consumers)
DataStream<Event> stream = env.addSource(kafkaConsumer);

// Reduce parallelism for aggregation (fewer keys)
stream
    .keyBy(...)
    .window(...)
    .aggregate(new MyAgg()).setParallelism(16);  // Only 16 parallel aggregations
```

---

### Network Buffers

```yaml
# flink-conf.yaml

# Network buffer configuration
taskmanager.network.memory.fraction: 0.1
taskmanager.network.memory.min: 64mb
taskmanager.network.memory.max: 1gb

# Number of network buffers per channel
taskmanager.network.memory.buffers-per-channel: 2
taskmanager.network.memory.floating-buffers-per-gate: 8

# Buffer timeout (trade-off: latency vs throughput)
# Low value (0ms): Lower latency, more network overhead
# High value (100ms): Higher throughput, higher latency
env.setBufferTimeout(100);  // milliseconds
```

**Buffer Timeout Trade-Off:**

```
Buffer Timeout = 0ms (low latency):
├─ Send buffer immediately (even if not full)
├─ Latency: ~10ms
└─ Throughput: 500k records/sec

Buffer Timeout = 100ms (high throughput):
├─ Wait for buffer to fill before sending
├─ Latency: ~100ms
└─ Throughput: 2M records/sec
```

---

### Watermark Intervals

```java
// Global watermark interval (default: 200ms)
env.getConfig().setAutoWatermarkInterval(200);

// Custom watermark generator with periodic emission
public class BoundedOutOfOrdernessGenerator 
    implements WatermarkGenerator<Event> {
    
    private long maxTimestamp = Long.MIN_VALUE;
    private final long maxOutOfOrderness = 5000;  // 5 seconds
    
    @Override
    public void onEvent(Event event, long eventTimestamp, WatermarkOutput output) {
        maxTimestamp = Math.max(maxTimestamp, event.getTimestamp());
    }
    
    @Override
    public void onPeriodicEmit(WatermarkOutput output) {
        // Emit watermark every 200ms (configured above)
        output.emitWatermark(new Watermark(maxTimestamp - maxOutOfOrderness));
    }
}
```

---

## 🔍 6. Monitoring and Metrics

### Web UI Metrics

```
http://localhost:8081

Key metrics:
├─ Checkpoint Duration: Should be < checkpoint interval
├─ Checkpoint Size: Monitor growth over time
├─ Backpressure: Red = high backpressure (bottleneck)
├─ Records Sent/Received: Balance across operators
└─ CPU/Memory Usage: Detect resource exhaustion
```

### Custom Metrics

```java
import org.apache.flink.metrics.Counter;
import org.apache.flink.api.common.functions.RichMapFunction;

public class CountingMapper extends RichMapFunction<Event, Event> {
    
    private transient Counter counter;
    
    @Override
    public void open(Configuration config) {
        this.counter = getRuntimeContext()
            .getMetricGroup()
            .counter("events_processed");
    }
    
    @Override
    public Event map(Event event) {
        counter.inc();
        return event;
    }
}
```

---

## 🏆 Interview Questions (Intermediate Level)

1. **Explain the role of JobManager vs TaskManager.**
2. **How does barrier alignment work in checkpointing?**
3. **What are the differences between HashMapStateBackend and RocksDBStateBackend?**
4. **How would you tune Flink for low latency vs high throughput?**
5. **What are unaligned checkpoints and when should you use them?**
6. **How does Flink achieve exactly-once semantics?**
7. **What is slot sharing and why is it important?**

---

## 🎓 Summary Checklist

- [ ] Understand JobManager and TaskManager architecture
- [ ] Explain checkpoint barrier mechanism
- [ ] Configure state backends (HashMap vs RocksDB)
- [ ] Implement custom ProcessFunctions
- [ ] Optimize parallelism and network buffers
- [ ] Monitor Flink jobs with Web UI
- [ ] Answer intermediate interview questions

**Next:** [EXPERT.md →](EXPERT.md)
