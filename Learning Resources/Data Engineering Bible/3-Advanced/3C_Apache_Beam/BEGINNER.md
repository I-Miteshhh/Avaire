# Week 10-11: Apache Beam — BEGINNER Track

*"Apache Beam's unified model lets you write once and run anywhere—Dataflow, Flink, Spark. Understanding PCollections, PTransforms, and windowing is the foundation for portable data processing."* — Google Cloud Architect

---

## 🎯 Learning Outcomes

By the end of this track, you will:
- Understand the Beam programming model (PCollections, PTransforms)
- Write portable batch and streaming pipelines
- Master windowing strategies (fixed, sliding, session, global)
- Use triggers for early and late data
- Deploy Beam pipelines on multiple runners (Direct, Flink, Spark, Dataflow)
- Understand the "What/Where/When/How" paradigm

---

## 📚 Prerequisites

- ✅ Java or Python basics
- ✅ Understanding of MapReduce or Spark
- ✅ Stream processing concepts (Flink module recommended)

---

## 🌟 1. What is Apache Beam?

### The Unified Model

```
Problem (Pre-Beam):
┌──────────────────────────────────────────────────────┐
│ Batch Processing:        Stream Processing:          │
│ ├─ MapReduce            ├─ Storm                     │
│ ├─ Spark Batch          ├─ Flink                     │
│ └─ Different API        └─ Different API             │
│                                                      │
│ Issues:                                              │
│ ├─ Rewrite code for batch vs stream                 │
│ ├─ Different semantics                              │
│ └─ Vendor lock-in                                   │
└──────────────────────────────────────────────────────┘

Beam Solution:
┌──────────────────────────────────────────────────────┐
│         Apache Beam (Unified API)                    │
│  ┌────────────────────────────────────┐              │
│  │  Beam SDK (Java, Python, Go)      │              │
│  └────────────────────────────────────┘              │
│                  │                                   │
│      ┌───────────┼───────────┬───────────┐          │
│      ▼           ▼           ▼           ▼          │
│  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐       │
│  │Direct │  │Flink  │  │Spark  │  │Cloud  │       │
│  │Runner │  │Runner │  │Runner │  │Dataflow│      │
│  └───────┘  └───────┘  └───────┘  └───────┘       │
│                                                      │
│ Benefits:                                            │
│ ├─ Write once, run anywhere                         │
│ ├─ Same code for batch and streaming                │
│ └─ No vendor lock-in                                │
└──────────────────────────────────────────────────────┘
```

---

### Beam Model: What/Where/When/How

```
Four fundamental questions for data processing:

1. WHAT results are calculated?
   → Transformations (ParDo, GroupByKey, Combine)

2. WHERE in event time?
   → Windowing (Fixed, Sliding, Session, Global)

3. WHEN in processing time are results materialized?
   → Triggers (AfterWatermark, AfterProcessingTime, AfterCount)

4. HOW do refinements relate?
   → Accumulation modes (Discarding, Accumulating, Accumulating & Retracting)
```

---

## 📦 2. Core Abstractions

### PCollection (Parallel Collection)

```
PCollection = Distributed, immutable dataset

Properties:
├─ Immutable: Once created, cannot be modified
├─ Distributed: Partitioned across workers
├─ Unbounded or Bounded:
│  ├─ Bounded: Finite dataset (batch)
│  └─ Unbounded: Infinite stream (streaming)
└─ Timestamped: Each element has timestamp

Creation:
// Bounded (batch)
PCollection<String> lines = pipeline.apply(
    TextIO.read().from("gs://bucket/input.txt")
);

// Unbounded (streaming)
PCollection<String> events = pipeline.apply(
    KafkaIO.<String, String>read()
        .withBootstrapServers("localhost:9092")
        .withTopic("events")
        .withoutMetadata()
).apply(Values.<String>create());
```

---

### PTransform (Parallel Transform)

```
PTransform = Operation on PCollection(s)

Types:
1. Element-wise: Apply function to each element independently
   ├─ ParDo (like map/flatMap)
   └─ Map, Filter, FlatMap (convenience wrappers)

2. Aggregating: Combine elements
   ├─ GroupByKey: Group by key
   ├─ Combine: Aggregate values
   └─ Count, Sum, Mean (convenience wrappers)

3. Composite: Combine multiple transforms
   └─ Custom PTransform

Example:
PCollection<String> input = ...;

// Element-wise transform
PCollection<Integer> lengths = input.apply(
    MapElements.into(TypeDescriptors.integers())
        .via((String word) -> word.length())
);

// Aggregating transform
PCollection<KV<String, Long>> wordCounts = input
    .apply(ParDo.of(new ExtractWordsFn()))
    .apply(Count.perElement());
```

---

## 🛠️ 3. Basic Transformations

### ParDo: The Swiss Army Knife

```java
import org.apache.beam.sdk.transforms.DoFn;
import org.apache.beam.sdk.transforms.ParDo;

// Custom DoFn
public class ExtractWordsFn extends DoFn<String, String> {
    
    @ProcessElement
    public void processElement(@Element String line, OutputReceiver<String> out) {
        // Split line into words
        for (String word : line.split("\\s+")) {
            if (!word.isEmpty()) {
                out.output(word.toLowerCase());
            }
        }
    }
}

// Usage
PCollection<String> lines = ...;
PCollection<String> words = lines.apply(
    ParDo.of(new ExtractWordsFn())
);
```

**Python Version:**

```python
import apache_beam as beam

class ExtractWordsFn(beam.DoFn):
    def process(self, element):
        for word in element.split():
            if word:
                yield word.lower()

# Usage
words = lines | beam.ParDo(ExtractWordsFn())
```

---

### GroupByKey and Combine

```java
// GroupByKey: Group values by key
PCollection<KV<String, Integer>> keyedValues = ...;
PCollection<KV<String, Iterable<Integer>>> grouped = keyedValues.apply(
    GroupByKey.<String, Integer>create()
);

// Combine: Aggregate grouped values
PCollection<KV<String, Integer>> sums = keyedValues.apply(
    Combine.perKey((Iterable<Integer> values) -> {
        int sum = 0;
        for (int value : values) {
            sum += value;
        }
        return sum;
    })
);

// Built-in combiners
PCollection<KV<String, Integer>> counts = words
    .apply(Count.perElement());  // Count occurrences

PCollection<Integer> total = values
    .apply(Sum.integersGlobally());  // Sum all values

PCollection<Double> average = values
    .apply(Mean.globally());  // Calculate mean
```

---

### Example: Word Count (Java)

```java
import org.apache.beam.sdk.Pipeline;
import org.apache.beam.sdk.io.TextIO;
import org.apache.beam.sdk.transforms.*;
import org.apache.beam.sdk.values.KV;
import org.apache.beam.sdk.values.PCollection;

public class WordCount {
    
    public static void main(String[] args) {
        // 1. Create pipeline
        Pipeline pipeline = Pipeline.create();
        
        // 2. Read input
        PCollection<String> lines = pipeline.apply(
            "ReadLines",
            TextIO.read().from("input.txt")
        );
        
        // 3. Transform: Split into words
        PCollection<String> words = lines.apply(
            "ExtractWords",
            FlatMapElements.into(TypeDescriptors.strings())
                .via((String line) -> Arrays.asList(line.split("\\s+")))
        );
        
        // 4. Count words
        PCollection<KV<String, Long>> wordCounts = words.apply(
            "CountWords",
            Count.perElement()
        );
        
        // 5. Format output
        PCollection<String> formatted = wordCounts.apply(
            "FormatResults",
            MapElements.into(TypeDescriptors.strings())
                .via((KV<String, Long> kv) -> kv.getKey() + ": " + kv.getValue())
        );
        
        // 6. Write output
        formatted.apply(
            "WriteResults",
            TextIO.write().to("output")
        );
        
        // 7. Run pipeline
        pipeline.run().waitUntilFinish();
    }
}
```

---

### Example: Word Count (Python)

```python
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

def run():
    with beam.Pipeline(options=PipelineOptions()) as pipeline:
        (
            pipeline
            | 'ReadLines' >> beam.io.ReadFromText('input.txt')
            | 'ExtractWords' >> beam.FlatMap(lambda line: line.split())
            | 'CountWords' >> beam.combiners.Count.PerElement()
            | 'FormatResults' >> beam.Map(lambda kv: f'{kv[0]}: {kv[1]}')
            | 'WriteResults' >> beam.io.WriteToText('output')
        )

if __name__ == '__main__':
    run()
```

**Run:**

```bash
# Direct Runner (local)
python wordcount.py --runner=DirectRunner

# Flink Runner
python wordcount.py --runner=FlinkRunner \
    --flink_master=localhost:8081

# Dataflow (Google Cloud)
python wordcount.py --runner=DataflowRunner \
    --project=my-project \
    --region=us-central1 \
    --temp_location=gs://my-bucket/temp
```

---

## 🪟 4. Windowing

### Fixed Windows (Tumbling)

```
Window size: 1 minute

10:00:00 ────────────────────────────── 10:01:00 ────────────────────────────── 10:02:00
│        Window 1               │        Window 2               │
│ Events: [e1, e2, e3]          │ Events: [e4, e5, e6]          │
│ Result: COUNT=3               │ Result: COUNT=3               │
```

```java
PCollection<KV<String, Integer>> keyedEvents = ...;

PCollection<KV<String, Integer>> windowedCounts = keyedEvents
    .apply(Window.<KV<String, Integer>>into(
        FixedWindows.of(Duration.standardMinutes(1))
    ))
    .apply(Sum.integersPerKey());
```

**Python:**

```python
windowed_counts = (
    keyed_events
    | beam.WindowInto(beam.window.FixedWindows(60))  # 60 seconds
    | beam.CombinePerKey(sum)
)
```

---

### Sliding Windows

```
Window size: 1 minute, slide: 30 seconds

10:00:00 ─────── 10:00:30 ─────── 10:01:00 ─────── 10:01:30
│        Window 1        │
                │        Window 2        │
                                │        Window 3        │

Window 1: [10:00:00, 10:01:00) → Events: [e1, e2, e3]
Window 2: [10:00:30, 10:01:30) → Events: [e2, e3, e4, e5]
Window 3: [10:01:00, 10:02:00) → Events: [e4, e5, e6, e7]
```

```java
PCollection<KV<String, Integer>> windowedCounts = keyedEvents
    .apply(Window.<KV<String, Integer>>into(
        SlidingWindows.of(Duration.standardMinutes(1))
            .every(Duration.standardSeconds(30))
    ))
    .apply(Sum.integersPerKey());
```

---

### Session Windows

```
Session gap: 10 minutes (inactivity timeout)

Events:
├─ 10:00:00 (e1)
├─ 10:05:00 (e2) ← Within 10 min
├─ 10:08:00 (e3) ← Within 10 min
├─ 10:20:00 (e4) ← Gap > 10 min, NEW SESSION!

Session 1: [10:00:00, 10:18:00) → Events: [e1, e2, e3]
Session 2: [10:20:00, ...) → Events: [e4, ...]
```

```java
PCollection<KV<String, Integer>> sessionCounts = keyedEvents
    .apply(Window.<KV<String, Integer>>into(
        Sessions.withGapDuration(Duration.standardMinutes(10))
    ))
    .apply(Sum.integersPerKey());
```

**Use case:** User session analytics

---

### Global Window (Default)

```
All events in single window (for bounded data)

────────────────────────────────────────────────────────────────
│                   Global Window                               │
│ All events: [e1, e2, e3, ..., eN]                            │
└────────────────────────────────────────────────────────────────

Default for bounded PCollections (batch processing)
```

---

## ⏰ 5. Event Time and Watermarks

### Timestamps

```java
// Assign timestamps to events
PCollection<Event> timestamped = events.apply(
    WithTimestamps.of((Event event) -> new Instant(event.getTimestamp()))
);

// Extract timestamp from string
PCollection<String> timestamped = lines.apply(
    WithTimestamps.of((String line) -> {
        // Parse: "2023-10-15T10:00:00Z,event_data"
        String timestamp = line.split(",")[0];
        return Instant.parse(timestamp);
    })
);
```

**Python:**

```python
import apache_beam as beam
from apache_beam.transforms import window

timestamped = events | beam.Map(
    lambda event: beam.window.TimestampedValue(event, event.timestamp)
)
```

---

### Watermarks (Handling Late Data)

```
Watermark = "All events with timestamp < T have been seen"

Example:
┌──────────────────────────────────────────────────────────┐
│ Stream of events:                                        │
│                                                          │
│ Event A: timestamp=10:00:00, arrives at 10:00:02       │
│ Event B: timestamp=10:00:05, arrives at 10:00:06       │
│ Event C: timestamp=10:00:03, arrives at 10:00:07 (late!)│
│ Event D: timestamp=10:00:10, arrives at 10:00:11       │
│                                                          │
│ Watermarks (with 5-second allowed lateness):            │
│ ├─ After Event B: Watermark(10:00:00)                  │
│ ├─ Event C arrives (late, but within 5s)               │
│ └─ After Event D: Watermark(10:00:05)                  │
└──────────────────────────────────────────────────────────┘

In Beam:
PCollection<Event> windowed = events
    .apply(Window.<Event>into(FixedWindows.of(Duration.standardMinutes(1)))
        .withAllowedLateness(Duration.standardSeconds(5))
        .discardingFiredPanes()  // or accumulatingFiredPanes()
    );
```

---

## 🚀 6. Running Pipelines

### Direct Runner (Local Testing)

```bash
# Java
mvn compile exec:java \
    -Dexec.mainClass=com.example.WordCount \
    -Pdirect-runner

# Python
python wordcount.py \
    --runner=DirectRunner \
    --input=input.txt \
    --output=output
```

---

### Apache Flink Runner

```bash
# Java
mvn compile exec:java \
    -Dexec.mainClass=com.example.WordCount \
    -Pflink-runner \
    -Dexec.args="--runner=FlinkRunner \
                 --flinkMaster=localhost:8081 \
                 --parallelism=4"

# Python
python wordcount.py \
    --runner=FlinkRunner \
    --flink_master=localhost:8081 \
    --flink_submit_uber_jar
```

---

### Google Cloud Dataflow

```bash
# Java
mvn compile exec:java \
    -Dexec.mainClass=com.example.WordCount \
    -Pdataflow-runner \
    -Dexec.args="--runner=DataflowRunner \
                 --project=my-project \
                 --region=us-central1 \
                 --tempLocation=gs://my-bucket/temp \
                 --gcpTempLocation=gs://my-bucket/temp"

# Python
python wordcount.py \
    --runner=DataflowRunner \
    --project=my-project \
    --region=us-central1 \
    --temp_location=gs://my-bucket/temp \
    --staging_location=gs://my-bucket/staging
```

---

## 🏆 Interview Questions (Beginner Level)

1. **What is the difference between PCollection and RDD (Spark)?**
2. **Explain the "What/Where/When/How" paradigm in Beam.**
3. **How do you assign timestamps to events in Beam?**
4. **What are the different types of windows in Beam?**
5. **How does Beam achieve portability across runners?**

---

## 🎓 Summary Checklist

- [ ] Understand Beam's unified model (batch + streaming)
- [ ] Use PCollections and PTransforms
- [ ] Implement ParDo for custom transformations
- [ ] Apply windowing strategies (fixed, sliding, session)
- [ ] Assign timestamps and handle watermarks
- [ ] Run pipelines on multiple runners (Direct, Flink, Dataflow)
- [ ] Answer beginner interview questions

**Next:** [INTERMEDIATE.md →](INTERMEDIATE.md)
