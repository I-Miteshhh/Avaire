# Week 10-11: Apache Beam — EXPERT Track

*"Beam's portability framework is engineering excellence—write once in Java, run on Flink with RocksDB state, or Dataflow with autoscaling. Understanding runner internals separates architects from users."* — Distinguished Engineer, Google

---

## 🎯 Learning Outcomes

- Master Beam portability framework architecture
- Understand runner-specific optimizations (Dataflow, Flink, Spark)
- Implement custom IO connectors with Splittable DoFn
- Design exactly-once semantics with Beam
- Optimize large-scale pipelines (>10TB/day)
- Handle schema evolution and data lineage
- Troubleshoot production pipeline failures

---

## 🏗️ 1. Portability Framework Architecture

### The Portability Layer

```
┌──────────────────────────────────────────────────────────┐
│                   Beam SDK (Java/Python/Go)              │
│  User Code: Pipeline construction, DoFns, CombineFns     │
└────────────────────────┬─────────────────────────────────┘
                         │ Beam Model Pipeline Proto
                         ▼
┌──────────────────────────────────────────────────────────┐
│              Beam Portability Framework                   │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Runner API: Language-agnostic pipeline proto      │  │
│  │ Fn API: Cross-language SDK harness                │  │
│  │ Job API: Job management, metrics, logs            │  │
│  └────────────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┬────────────────┐
        ▼                ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│Flink Runner  │ │Spark Runner  │ │Dataflow      │ │Custom Runner │
│              │ │              │ │              │ │              │
│ Translates   │ │ Translates   │ │ Translates   │ │ Translates   │
│ to Flink     │ │ to Spark     │ │ to Dataflow  │ │ to ...       │
│ DAG          │ │ RDD/Dataset  │ │ execution    │ │              │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

**Key Insight:** Pipeline proto is runner-agnostic. Runners translate to native execution.

---

### Runner Translation Example

```java
// Beam Pipeline:
PCollection<KV<String, Integer>> wordCounts = lines
    .apply(ParDo.of(new ExtractWordsFn()))  // ParDo
    .apply(Count.perElement());              // GroupByKey + Combine

// Flink Runner Translation:
DataStream<String> lines = ...;
DataStream<Tuple2<String, Long>> counts = lines
    .flatMap(new ExtractWordsFn())          // FlatMapFunction
    .keyBy(word -> word)                    // keyBy (hash partition)
    .window(GlobalWindows.create())         // Global window
    .reduce((a, b) -> a + b);               // ReduceFunction

// Spark Runner Translation:
JavaRDD<String> lines = ...;
JavaPairRDD<String, Long> counts = lines
    .flatMap(new ExtractWordsFn())          // flatMap
    .mapToPair(word -> new Tuple2<>(word, 1L))
    .reduceByKey((a, b) -> a + b);          // reduceByKey
```

---

## 🎯 2. Exactly-Once Semantics in Beam

### Source Checkpointing

```java
// Kafka source with checkpointed offsets
PCollection<KV<String, String>> events = pipeline.apply(
    KafkaIO.<String, String>read()
        .withBootstrapServers("localhost:9092")
        .withTopic("events")
        .withKeyDeserializer(StringDeserializer.class)
        .withValueDeserializer(StringDeserializer.class)
        // Enable checkpointing (runner-dependent)
        .commitOffsetsInFinalize()
);

// Flink Runner: Offsets checkpointed with Flink snapshots
// Dataflow Runner: Offsets stored in Dataflow state
```

**Checkpoint Recovery:**

```
Job fails at T=100:
├─ Last successful checkpoint: T=80
├─ Kafka offsets at T=80: partition-0: 10000, partition-1: 50000
├─ Recovery: Seek to offset 10000, 50000
└─ Replay events from T=80 to T=100 (exactly-once)
```

---

### Transactional Sinks

```java
// Kafka sink with exactly-once (2PC)
PCollection<KV<String, String>> results = ...;

results.apply(
    KafkaIO.<String, String>write()
        .withBootstrapServers("localhost:9092")
        .withTopic("output")
        .withKeySerializer(StringSerializer.class)
        .withValueSerializer(StringSerializer.class)
        // Exactly-once requires transactions
        .withEOS(20, "beam-txn")  // Transactional writes
);

// Under the hood (Flink Runner):
// 1. Pre-commit during checkpoint barrier
// 2. Commit after checkpoint completes
// 3. Abort if checkpoint fails
```

---

## 🔌 3. Custom IO Connectors

### Splittable DoFn (SDF) for Bounded Sources

```java
import org.apache.beam.sdk.transforms.DoFn;
import org.apache.beam.sdk.transforms.splittabledofn.*;

// Custom file source with parallel reading
@BoundedPerElement
public class ReadFileFn extends DoFn<String, String> {
    
    // Restriction: byte range to read
    @GetInitialRestriction
    public OffsetRange getInitialRestriction(@Element String filename) {
        long fileSize = getFileSize(filename);
        return new OffsetRange(0, fileSize);
    }
    
    // Split restriction for parallel processing
    @SplitRestriction
    public void splitRestriction(
        @Restriction OffsetRange range,
        OutputReceiver<OffsetRange> receiver
    ) {
        long chunkSize = 64 * 1024 * 1024;  // 64 MB chunks
        for (long offset = range.getFrom(); offset < range.getTo(); offset += chunkSize) {
            receiver.output(new OffsetRange(
                offset,
                Math.min(offset + chunkSize, range.getTo())
            ));
        }
    }
    
    // Process restriction
    @ProcessElement
    public void processElement(
        ProcessContext c,
        RestrictionTracker<OffsetRange, Long> tracker
    ) {
        String filename = c.element();
        OffsetRange range = tracker.currentRestriction();
        
        try (RandomAccessFile file = new RandomAccessFile(filename, "r")) {
            file.seek(range.getFrom());
            
            long position = range.getFrom();
            while (tracker.tryClaim(position)) {
                String line = file.readLine();
                if (line == null || position >= range.getTo()) {
                    break;
                }
                c.output(line);
                position = file.getFilePointer();
            }
        }
    }
}

// Usage:
PCollection<String> files = pipeline.apply(Create.of("file1.txt", "file2.txt"));
PCollection<String> lines = files.apply(ParDo.of(new ReadFileFn()));
```

**Execution:**

```
Input: file1.txt (200 MB)

Step 1: getInitialRestriction
├─ file1.txt → OffsetRange(0, 200MB)

Step 2: splitRestriction (64 MB chunks)
├─ OffsetRange(0, 64MB)
├─ OffsetRange(64MB, 128MB)
├─ OffsetRange(128MB, 192MB)
└─ OffsetRange(192MB, 200MB)

Step 3: processElement (parallel on 4 workers)
├─ Worker 1: Read 0-64MB
├─ Worker 2: Read 64-128MB
├─ Worker 3: Read 128-192MB
└─ Worker 4: Read 192-200MB

Result: 4x parallelism, linear scalability
```

---

### Unbounded Source with SDF

```java
// Custom Kafka-like source
@UnboundedPerElement
public class ReadStreamFn extends DoFn<String, String> {
    
    @GetInitialRestriction
    public OffsetRange getInitialRestriction(@Element String topic) {
        return new OffsetRange(0, Long.MAX_VALUE);  // Unbounded
    }
    
    @GetInitialWatermarkEstimatorState
    public Instant getInitialWatermarkState(@Element String topic) {
        return Instant.EPOCH;
    }
    
    @NewWatermarkEstimator
    public WatermarkEstimator<Instant> newWatermarkEstimator(
        @WatermarkEstimatorState Instant state
    ) {
        return new Manual(state);
    }
    
    @ProcessElement
    public ProcessContinuation processElement(
        ProcessContext c,
        RestrictionTracker<OffsetRange, Long> tracker,
        WatermarkEstimator<Instant> watermarkEstimator
    ) {
        String topic = c.element();
        
        // Poll messages
        List<Message> messages = pollMessages(topic, 100);  // Max 100
        
        for (Message msg : messages) {
            if (!tracker.tryClaim(msg.getOffset())) {
                return ProcessContinuation.stop();
            }
            
            c.outputWithTimestamp(msg.getData(), msg.getTimestamp());
            watermarkEstimator.setWatermark(msg.getTimestamp());
        }
        
        // Continue processing (unbounded)
        return ProcessContinuation.resume().withResumeDelay(Duration.standardSeconds(1));
    }
}
```

---

## 🚀 4. Runner-Specific Optimizations

### Dataflow Runner

```java
// Auto-scaling configuration
DataflowPipelineOptions options = 
    PipelineOptionsFactory.as(DataflowPipelineOptions.class);

options.setRunner(DataflowRunner.class);
options.setProject("my-project");
options.setRegion("us-central1");
options.setTempLocation("gs://my-bucket/temp");

// Auto-scaling
options.setAutoscalingAlgorithm(AutoscalingAlgorithmType.THROUGHPUT_BASED);
options.setMaxNumWorkers(100);  // Scale to 100 workers
options.setWorkerMachineType("n1-standard-4");

// Dataflow-specific optimizations
options.setEnableStreamingEngine(true);  // Offload shuffle to service
options.setStreaming(true);

Pipeline pipeline = Pipeline.create(options);
```

**Streaming Engine:**

```
Traditional:
├─ Shuffle on worker VMs (memory + disk)
├─ State on worker persistent disks
└─ Scaling requires state migration

Streaming Engine:
├─ Shuffle offloaded to Google service
├─ State in disaggregated storage
├─ Scaling: Attach new workers instantly
└─ No state migration overhead
```

---

### Flink Runner

```java
// Flink-specific pipeline options
FlinkPipelineOptions options = 
    PipelineOptionsFactory.as(FlinkPipelineOptions.class);

options.setRunner(FlinkRunner.class);
options.setFlinkMaster("localhost:8081");
options.setParallelism(64);

// Flink state backend (use RocksDB for large state)
options.setStateBackend("rocksdb");
options.setCheckpointingInterval(60000L);  // 1 minute checkpoints

// Flink-specific optimizations
options.setObjectReuse(true);  // Reuse objects (avoid serialization)
options.setAutoWatermarkInterval(200L);  // Watermark interval

Pipeline pipeline = Pipeline.create(options);
```

**State Backend Mapping:**

```
Beam State → Flink RocksDB State:
├─ ValueState → ValueState
├─ BagState → ListState
├─ MapState → MapState
└─ SetState → MapState (value=null)

Checkpointing:
├─ Beam checkpoints trigger Flink snapshots
├─ State persisted to S3/HDFS
└─ Recovery: Restore from last Flink checkpoint
```

---

### Spark Runner

```java
// Spark-specific options
SparkPipelineOptions options = 
    PipelineOptionsFactory.as(SparkPipelineOptions.class);

options.setRunner(SparkRunner.class);
options.setSparkMaster("spark://master:7077");

// Spark configurations
Map<String, String> sparkConf = new HashMap<>();
sparkConf.put("spark.executor.memory", "8g");
sparkConf.put("spark.executor.cores", "4");
sparkConf.put("spark.dynamicAllocation.enabled", "true");

options.setSparkMasterUrl("spark://master:7077");
options.setFilesToStage(Collections.singletonList("pipeline.jar"));

Pipeline pipeline = Pipeline.create(options);
```

---

## 📊 5. Production Case Studies

### Netflix: Content Recommendation Pipeline

```
Requirements:
├─ Process 500M viewing events/day
├─ Join with content catalog (1M items)
├─ Generate recommendations in <1 hour
└─ Run on Google Cloud Dataflow

Architecture:
┌────────────────────────────────────────────────────────┐
│ Kafka (viewing events)                                 │
└──────────────────┬─────────────────────────────────────┘
                   ▼
┌────────────────────────────────────────────────────────┐
│ Beam Pipeline (Dataflow Runner)                        │
│                                                        │
│ 1. Read: KafkaIO                                       │
│    ├─ 500M events/day                                 │
│    └─ Parallelism: 200 (match Kafka partitions)       │
│                                                        │
│ 2. Enrich: Side input (content catalog)               │
│    ├─ AsMap view (1M items)                           │
│    └─ Broadcast to all workers                        │
│                                                        │
│ 3. Window: Fixed windows (1 hour)                     │
│    └─ Group viewing sessions                          │
│                                                        │
│ 4. Aggregate: CombineFn (user preferences)            │
│    ├─ Genres watched, total time, recency             │
│    └─ Custom CombineFn (efficient)                    │
│                                                        │
│ 5. Compute: ML inference (TensorFlow)                 │
│    ├─ ParDo with TensorFlow Serving                   │
│    └─ Batch predictions (100 users/request)           │
│                                                        │
│ 6. Write: BigQuery (analytics), Cassandra (serving)   │
└────────────────────────────────────────────────────────┘

Configuration:
- Dataflow Streaming Engine: Enabled
- Max workers: 500 (auto-scaling)
- Machine type: n1-highmem-8 (52 GB RAM)
- Checkpoint interval: 5 minutes
- State: Managed by Dataflow service
```

---

### Spotify: Real-Time Music Analytics

```
Requirements:
├─ Process 2B play events/day
├─ Calculate artist/playlist statistics
├─ Update dashboards every 1 minute
└─ Run on Apache Flink

Architecture:
┌────────────────────────────────────────────────────────┐
│ Kafka (play events)                                    │
└──────────────────┬─────────────────────────────────────┘
                   ▼
┌────────────────────────────────────────────────────────┐
│ Beam Pipeline (Flink Runner)                           │
│                                                        │
│ 1. Read: KafkaIO with Flink offset management         │
│    ├─ 2B events/day (~23k/sec sustained)             │
│    └─ Parallelism: 128                                │
│                                                        │
│ 2. Window: Sliding (5 min size, 1 min slide)          │
│    └─ For moving averages                             │
│                                                        │
│ 3. Aggregate: Combine.perKey                          │
│    ├─ Play count per artist                           │
│    ├─ Unique listeners (HyperLogLog)                  │
│    └─ Avg play duration                               │
│                                                        │
│ 4. Triggers: Early + On-time + Late                   │
│    ├─ Early: Every 10 seconds (dashboard updates)     │
│    ├─ On-time: Watermark (accurate count)             │
│    └─ Late: Accept 5 min late data                    │
│                                                        │
│ 5. Write: Kafka (downstream), Redis (caching)         │
└────────────────────────────────────────────────────────┘

Configuration:
- Flink TaskManagers: 32 (8 slots each)
- RocksDB state backend (incremental checkpoints)
- Checkpoint interval: 1 minute
- Unaligned checkpoints: Enabled (high throughput)
- State size: ~200 GB (5-minute windows, millions of keys)
```

---

## 🏆 Interview Questions (Expert Level)

1. **Explain Beam's portability framework. How does it achieve write-once-run-anywhere?**
2. **How would you implement exactly-once semantics in a Beam pipeline with Kafka source and sink?**
3. **What is Splittable DoFn? When would you use it instead of a standard source?**
4. **Compare Dataflow Streaming Engine vs traditional Flink execution. What are the trade-offs?**
5. **Design a real-time recommendation pipeline processing 1B events/day. What are the bottlenecks?**
6. **How would you handle schema evolution in a long-running Beam pipeline?**
7. **Explain runner translation: How does a Beam GroupByKey map to Flink's keyBy + window?**
8. **What optimizations does Beam perform (fusion, combiner lifting)? How do they affect performance?**
9. **How would you debug a Beam pipeline with high checkpoint latency on Flink runner?**
10. **Design a multi-tenant Beam platform. How would you isolate tenants and allocate resources?**

---

## 🎓 Summary Checklist

- [ ] Understand Beam portability framework architecture
- [ ] Implement exactly-once semantics with transactional sinks
- [ ] Build custom IO connectors with Splittable DoFn
- [ ] Configure runner-specific optimizations (Dataflow, Flink, Spark)
- [ ] Design large-scale production pipelines (>10TB/day)
- [ ] Handle schema evolution and late data
- [ ] Troubleshoot performance issues (checkpoints, backpressure)
- [ ] Answer expert-level interview questions

**Next:** [WHITEPAPERS.md →](WHITEPAPERS.md)
