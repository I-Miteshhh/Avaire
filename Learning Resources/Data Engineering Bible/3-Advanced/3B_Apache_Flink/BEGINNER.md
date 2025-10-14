# Week 8-9: Apache Flink — BEGINNER Track

*"Flink is the most advanced stream processing engine. Understanding event time, watermarks, and state management is essential for building real-time data applications."* — Flink PMC Member

---

## 🎯 Learning Outcomes

By the end of this track, you will:
- Understand stream processing fundamentals (bounded vs unbounded data)
- Master event time vs processing time concepts
- Learn watermark mechanics for handling out-of-order data
- Implement windowed computations (tumbling, sliding, session windows)
- Use Flink DataStream API for basic transformations
- Deploy simple Flink applications on local cluster

---

## 📚 Prerequisites

- ✅ Java/Scala basics
- ✅ Distributed systems fundamentals
- ✅ Kafka basics (producers, consumers, topics)

---

## 🌊 1. Stream Processing Fundamentals

### Bounded vs Unbounded Data

```
Bounded Data (Batch Processing):
┌─────────────────────────────────────────┐
│ Dataset: Fixed size, known end         │
│ Example: Historical sales (Jan-Dec)    │
│ Processing: MapReduce, Spark Batch     │
└─────────────────────────────────────────┘

Unbounded Data (Stream Processing):
┌─────────────────────────────────────────┐
│ Dataset: Infinite, continuous          │
│ Example: Real-time clicks, IoT sensors │
│ Processing: Flink, Kafka Streams        │
└─────────────────────────────────────────┘

Key Difference:
- Batch: "Process all data, then produce result"
- Stream: "Process data incrementally as it arrives"
```

### Why Flink?

```
Comparison with other systems:

Spark Streaming (Micro-Batching):
├─ Processes data in small batches (500ms-2s)
├─ Higher latency (seconds)
└─ Simpler model, but not true streaming

Kafka Streams (Library):
├─ True streaming, low latency (<100ms)
├─ Embedded in application (no separate cluster)
└─ Limited to Kafka sources/sinks

Flink (True Streaming):
├─ True streaming, ultra-low latency (<10ms)
├─ Rich state management
├─ Event time processing, watermarks
├─ Exactly-once guarantees
└─ Batch + streaming in one engine
```

---

## ⏰ 2. Event Time vs Processing Time

### The Problem: Out-of-Order Events

```
Real-World Scenario: Mobile app events

User clicks "Buy" at 10:00:00 (event time)
├─ Network delay: 5 seconds
└─ Arrives at server: 10:00:05 (processing time)

User clicks "View" at 10:00:03 (event time)
├─ Fast network
└─ Arrives at server: 10:00:04 (processing time)

Order of arrival: "View" (10:00:04), "Buy" (10:00:05)
Order of occurrence: "Buy" (10:00:00), "View" (10:00:03)

Question: How to count events in 1-minute windows correctly?
```

### Event Time vs Processing Time

```
Processing Time:
- Time when event is processed by the system
- Simple, no need to extract timestamps
- Problem: Non-deterministic (network delays)

┌──────────────────────────────────────┐
│ Window: 10:00 - 10:01                │
│ Events: All events that arrived      │
│         between 10:00 and 10:01      │
│ Issue: Events from 9:59 might arrive │
│        at 10:00:05 (wrong window!)   │
└──────────────────────────────────────┘

Event Time:
- Time when event actually occurred
- Deterministic, reproducible results
- Requires: Extract timestamp from event data

┌──────────────────────────────────────┐
│ Window: 10:00 - 10:01                │
│ Events: All events with timestamp    │
│         between 10:00 and 10:01      │
│ Benefit: Correct semantics even with │
│          delays!                     │
└──────────────────────────────────────┘
```

---

## 💧 3. Watermarks: Handling Late Data

### What Are Watermarks?

```
Watermark = "All events with timestamp < T have arrived"

Example:
┌──────────────────────────────────────────────────────────┐
│ Stream of events:                                        │
│                                                          │
│ Event A: timestamp=10:00:00, arrives at 10:00:02       │
│ Event B: timestamp=10:00:05, arrives at 10:00:06       │
│ Event C: timestamp=10:00:03, arrives at 10:00:07 (late!)│
│ Event D: timestamp=10:00:10, arrives at 10:00:11       │
│                                                          │
│ Watermarks:                                              │
│ ├─ After Event B: Watermark(10:00:05)                  │
│ │  → "Events up to 10:00:05 have arrived"             │
│ ├─ Event C arrives (late, but within watermark)        │
│ └─ After Event D: Watermark(10:00:10)                  │
│    → "Events up to 10:00:10 have arrived"              │
└──────────────────────────────────────────────────────────┘

When watermark(T) passes:
- Trigger window computation for windows ending at T
- Assume no more events with timestamp < T will arrive
```

### Watermark Strategies

```java
// 1. Bounded Out-of-Orderness (most common)
WatermarkStrategy<Event> strategy = WatermarkStrategy
    .<Event>forBoundedOutOfOrderness(Duration.ofSeconds(5))
    .withTimestampAssigner((event, timestamp) -> event.getTimestamp());

// Meaning: "Events can arrive up to 5 seconds late"
// Watermark = max_event_timestamp - 5 seconds

// 2. Monotonous Timestamps (no late data)
WatermarkStrategy<Event> strategy = WatermarkStrategy
    .<Event>forMonotonousTimestamps()
    .withTimestampAssigner((event, timestamp) -> event.getTimestamp());

// Meaning: "Events arrive in order"
// Watermark = max_event_timestamp
```

**Example:**

```
Events:
├─ Event A: timestamp=10:00:00, arrives
│  Watermark = 10:00:00 - 5s = 09:59:55
├─ Event B: timestamp=10:00:10, arrives
│  Watermark = 10:00:10 - 5s = 10:00:05
├─ Event C: timestamp=10:00:03, arrives (late, but within 5s)
│  Accepted! (10:00:03 > 10:00:05 - 5s)
└─ Event D: timestamp=09:59:50, arrives (too late!)
   Dropped! (09:59:50 < 10:00:05 - 5s)
```

---

## 🪟 4. Windowing: Grouping Events

### Tumbling Windows (Non-Overlapping)

```
Window size: 1 minute

10:00:00 ────────────────────────────── 10:01:00 ────────────────────────────── 10:02:00
│        Window 1               │        Window 2               │
│ Events: [A, B, C]             │ Events: [D, E, F]             │
│ Result: COUNT=3               │ Result: COUNT=3               │

Use case: "Count clicks per minute"
```

```java
DataStream<Event> stream = ...;

stream
    .keyBy(event -> event.getUserId())
    .window(TumblingEventTimeWindows.of(Time.minutes(1)))
    .sum("amount");
```

### Sliding Windows (Overlapping)

```
Window size: 1 minute, slide: 30 seconds

10:00:00 ─────── 10:00:30 ─────── 10:01:00 ─────── 10:01:30
│        Window 1        │
                │        Window 2        │
                                │        Window 3        │

Window 1: [10:00:00, 10:01:00) → Events: [A, B, C]
Window 2: [10:00:30, 10:01:30) → Events: [B, C, D, E]
Window 3: [10:01:00, 10:02:00) → Events: [D, E, F, G]

Use case: "Moving average of last 1 minute, updated every 30 seconds"
```

```java
stream
    .keyBy(event -> event.getUserId())
    .window(SlidingEventTimeWindows.of(Time.minutes(1), Time.seconds(30)))
    .sum("amount");
```

### Session Windows (Gap-Based)

```
Session gap: 10 minutes (inactivity timeout)

Events:
├─ 10:00:00 (Event A)
├─ 10:05:00 (Event B) ← Within 10 min
├─ 10:08:00 (Event C) ← Within 10 min
├─ 10:20:00 (Event D) ← Gap > 10 min, NEW SESSION!

Session 1: [10:00:00, 10:18:00) → Events: [A, B, C]
Session 2: [10:20:00, ...) → Events: [D, ...]

Use case: "User session analytics (activity bursts)"
```

```java
stream
    .keyBy(event -> event.getUserId())
    .window(EventTimeSessionWindows.withGap(Time.minutes(10)))
    .sum("amount");
```

---

## 🛠️ 5. Flink DataStream API Basics

### Simple Word Count (Stream Version)

```java
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.api.common.functions.FlatMapFunction;
import org.apache.flink.util.Collector;

public class StreamingWordCount {
    public static void main(String[] args) throws Exception {
        // 1. Create execution environment
        StreamExecutionEnvironment env = 
            StreamExecutionEnvironment.getExecutionEnvironment();
        
        // 2. Read from socket (for testing)
        DataStream<String> text = env.socketTextStream("localhost", 9999);
        
        // 3. Transform: Split into words
        DataStream<Tuple2<String, Integer>> counts = text
            .flatMap(new Tokenizer())
            .keyBy(value -> value.f0)
            .sum(1);
        
        // 4. Print to console
        counts.print();
        
        // 5. Execute
        env.execute("Streaming WordCount");
    }
    
    public static class Tokenizer 
        implements FlatMapFunction<String, Tuple2<String, Integer>> {
        
        @Override
        public void flatMap(String value, Collector<Tuple2<String, Integer>> out) {
            for (String word : value.split("\\s")) {
                out.collect(new Tuple2<>(word, 1));
            }
        }
    }
}
```

**Test:**

```bash
# Terminal 1: Start netcat
nc -lk 9999

# Terminal 2: Run Flink application
./bin/flink run WordCount.jar

# Terminal 1: Type words
hello world
hello flink

# Terminal 2: See output
(hello, 1)
(world, 1)
(hello, 2)
(flink, 1)
```

---

### Reading from Kafka

```java
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer;
import org.apache.flink.api.common.serialization.SimpleStringSchema;

Properties props = new Properties();
props.setProperty("bootstrap.servers", "localhost:9092");
props.setProperty("group.id", "flink-consumer");

FlinkKafkaConsumer<String> consumer = new FlinkKafkaConsumer<>(
    "events",                  // Topic
    new SimpleStringSchema(),  // Deserialization schema
    props                      // Kafka properties
);

DataStream<String> stream = env.addSource(consumer);
```

---

### Windowed Aggregation

```java
public class SlidingWindowExample {
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = 
            StreamExecutionEnvironment.getExecutionEnvironment();
        
        // Enable event time
        env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);
        
        DataStream<Event> events = env
            .addSource(new KafkaSource())
            .assignTimestampsAndWatermarks(
                WatermarkStrategy
                    .<Event>forBoundedOutOfOrderness(Duration.ofSeconds(5))
                    .withTimestampAssigner((event, ts) -> event.getTimestamp())
            );
        
        // Sliding window: 1 minute, slide 10 seconds
        DataStream<Tuple2<String, Double>> avgPerUser = events
            .keyBy(event -> event.getUserId())
            .window(SlidingEventTimeWindows.of(
                Time.minutes(1),  // Window size
                Time.seconds(10)  // Slide interval
            ))
            .aggregate(new AverageAggregate());
        
        avgPerUser.print();
        
        env.execute("Sliding Window Average");
    }
}
```

---

## 📊 6. State Management Basics

### Keyed State (Per-Key Storage)

```java
public class StatefulCounter extends RichFlatMapFunction<Event, Tuple2<String, Long>> {
    
    // State: Store count per key
    private transient ValueState<Long> countState;
    
    @Override
    public void open(Configuration config) {
        ValueStateDescriptor<Long> descriptor = 
            new ValueStateDescriptor<>("count", Long.class, 0L);
        countState = getRuntimeContext().getState(descriptor);
    }
    
    @Override
    public void flatMap(Event event, Collector<Tuple2<String, Long>> out) throws Exception {
        // Get current count
        Long currentCount = countState.value();
        
        // Increment
        currentCount++;
        
        // Update state
        countState.update(currentCount);
        
        // Emit result
        out.collect(new Tuple2<>(event.getUserId(), currentCount));
    }
}

// Usage:
stream
    .keyBy(event -> event.getUserId())
    .flatMap(new StatefulCounter());
```

**State Lifecycle:**

```
State per key:
├─ user_id=123 → count=5
├─ user_id=456 → count=12
└─ user_id=789 → count=3

When event for user_id=123 arrives:
1. Retrieve state: count=5
2. Process: count++
3. Update state: count=6
4. Emit: (123, 6)
```

---

## 🚀 7. Deploying Flink Applications

### Local Cluster (Development)

```bash
# Download Flink
wget https://archive.apache.org/dist/flink/flink-1.18.0/flink-1.18.0-bin-scala_2.12.tgz
tar -xzf flink-1.18.0-bin-scala_2.12.tgz
cd flink-1.18.0

# Start local cluster
./bin/start-cluster.sh

# Open Web UI
http://localhost:8081

# Submit job
./bin/flink run examples/streaming/WordCount.jar

# Stop cluster
./bin/stop-cluster.sh
```

### Docker Compose Setup

```yaml
version: '3.8'
services:
  jobmanager:
    image: flink:1.18.0
    ports:
      - "8081:8081"
    command: jobmanager
    environment:
      - JOB_MANAGER_RPC_ADDRESS=jobmanager

  taskmanager:
    image: flink:1.18.0
    depends_on:
      - jobmanager
    command: taskmanager
    environment:
      - JOB_MANAGER_RPC_ADDRESS=jobmanager
```

```bash
docker-compose up -d
```

---

## 🏆 Interview Questions (Beginner Level)

1. **What is the difference between event time and processing time?**
2. **What are watermarks and why are they needed?**
3. **Explain tumbling vs sliding vs session windows.**
4. **How does Flink handle late-arriving events?**
5. **What is keyed state in Flink?**

---

## 🎓 Summary Checklist

- [ ] Understand bounded vs unbounded data
- [ ] Explain event time vs processing time
- [ ] Implement watermark strategies
- [ ] Use tumbling, sliding, and session windows
- [ ] Write basic Flink DataStream programs
- [ ] Deploy Flink application on local cluster
- [ ] Answer beginner interview questions

**Next:** [INTERMEDIATE.md →](INTERMEDIATE.md)
