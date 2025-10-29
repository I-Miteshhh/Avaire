# Week 10-11: Apache Beam — INTERMEDIATE Track

*"Beam's trigger system is the most flexible I've seen—combine watermark, processing time, and count-based triggers to balance latency and accuracy."* — Staff Engineer, Spotify

---

## 🎯 Learning Outcomes

By the end of this track, you will:
- Master triggers (early, on-time, late firings)
- Understand accumulation modes (discarding, accumulating, retracting)
- Use side inputs for enrichment
- Implement custom CombineFns for efficient aggregations
- Handle state and timers in stateful DoFns
- Optimize pipeline performance
- Debug and monitor Beam pipelines

---

## ⏰ 1. Triggers: When to Emit Results

### The Triggering Problem

```
Question: When should we emit windowed aggregation results?

Scenario: 1-minute fixed window, COUNT events

Events arrive:
T=10:00:02: Event A (timestamp=10:00:00)
T=10:00:15: Event B (timestamp=10:00:05)
T=10:00:45: Event C (timestamp=10:00:30)
T=10:01:05: Event D (timestamp=10:00:50) ← LATE!

Options:
1. Wait for watermark → High latency, complete data
2. Emit early → Low latency, incomplete data
3. Emit multiple times → Balance both!
```

---

### Trigger Types

```java
import org.apache.beam.sdk.transforms.windowing.*;

// 1. AfterWatermark: Fire when watermark passes window end (ON-TIME)
Trigger onTime = AfterWatermark.pastEndOfWindow();

// 2. AfterProcessingTime: Fire after N seconds of processing time (EARLY)
Trigger early = AfterProcessingTime.pastFirstElementInPane()
    .plusDelayOf(Duration.standardSeconds(30));

// 3. AfterPane: Fire after N elements (EARLY)
Trigger earlyCount = AfterPane.elementCountAtLeast(1000);

// 4. Repeatedly: Repeat trigger multiple times
Trigger repeated = Repeatedly.forever(
    AfterProcessingTime.pastFirstElementInPane()
        .plusDelayOf(Duration.standardSeconds(10))
);

// 5. Combined: Early + On-time + Late
Trigger combined = AfterWatermark.pastEndOfWindow()
    .withEarlyFirings(
        AfterProcessingTime.pastFirstElementInPane()
            .plusDelayOf(Duration.standardSeconds(10))
    )
    .withLateFirings(AfterPane.elementCountAtLeast(1));
```

---

### Example: Real-Time Dashboard

```java
// Requirement: Show results every 10 seconds, update on watermark, handle late data

PCollection<KV<String, Integer>> dashboardCounts = events
    .apply(Window.<KV<String, Integer>>into(
            FixedWindows.of(Duration.standardMinutes(1))
        )
        .triggering(
            AfterWatermark.pastEndOfWindow()
                .withEarlyFirings(
                    AfterProcessingTime.pastFirstElementInPane()
                        .plusDelayOf(Duration.standardSeconds(10))
                )
                .withLateFirings(AfterPane.elementCountAtLeast(1))
        )
        .withAllowedLateness(Duration.standardMinutes(5))
        .accumulatingFiredPanes()  // Cumulative results
    )
    .apply(Sum.integersPerKey());
```

**Timeline:**

```
Window: [10:00:00, 10:01:00)

T=10:00:10: Early firing #1 → COUNT=5 (5 events so far)
T=10:00:20: Early firing #2 → COUNT=12 (cumulative)
T=10:00:30: Early firing #3 → COUNT=18
...
T=10:01:00: Watermark firing (ON-TIME) → COUNT=25 (complete)
T=10:01:30: Late event arrives
T=10:01:30: Late firing #1 → COUNT=26 (updated)
T=10:06:00: Allowed lateness expires, window closed
```

---

## 📊 2. Accumulation Modes

### Discarding vs Accumulating vs Retracting

```
Given events for window [10:00, 10:01):
├─ Early trigger (10s): [e1, e2] → sum=30
├─ Early trigger (20s): [e3, e4] → sum=50
├─ On-time trigger: [e5] → sum=40
└─ Late trigger: [e6] → sum=15

1. DISCARDING (.discardingFiredPanes()):
   - Emit only NEW data since last trigger
   - Output: 30, 50, 40, 15
   - Total (downstream sum): 135 ✅
   - Use case: Incremental updates, Kafka compaction

2. ACCUMULATING (.accumulatingFiredPanes()):
   - Emit cumulative results
   - Output: 30, 80, 120, 135
   - Downstream needs to handle overwrite/replace
   - Use case: Replacing previous result (database upsert)

3. ACCUMULATING & RETRACTING:
   - Emit: (retract old, emit new)
   - Output: +30, (-30, +80), (-80, +120), (-120, +135)
   - Correct downstream aggregations automatically
   - Use case: SQL-like changelogs, Beam SQL
```

**Java Example:**

```java
// Discarding
PCollection<KV<String, Integer>> discarding = events
    .apply(Window.<KV<String, Integer>>into(FixedWindows.of(Duration.standardMinutes(1)))
        .triggering(...)
        .discardingFiredPanes()
    )
    .apply(Sum.integersPerKey());

// Accumulating
PCollection<KV<String, Integer>> accumulating = events
    .apply(Window.<KV<String, Integer>>into(FixedWindows.of(Duration.standardMinutes(1)))
        .triggering(...)
        .accumulatingFiredPanes()
    )
    .apply(Sum.integersPerKey());
```

---

## 🔗 3. Side Inputs: Enrichment Patterns

### What are Side Inputs?

```
Main input: Stream of events
Side input: Small dataset for lookup/enrichment

Example: Enrich transactions with user profiles

Main Input (PCollection<Transaction>):
├─ {user_id: "123", amount: $50}
├─ {user_id: "456", amount: $200}

Side Input (PCollection<UserProfile> → PCollectionView<Map>):
├─ {user_id: "123", country: "US", tier: "premium"}
├─ {user_id: "456", country: "UK", tier: "basic"}

Enriched Output:
├─ {user_id: "123", amount: $50, country: "US", tier: "premium"}
├─ {user_id: "456", amount: $200, country: "UK", tier: "basic"}
```

---

### Implementation

```java
import org.apache.beam.sdk.values.PCollectionView;
import org.apache.beam.sdk.transforms.View;

// 1. Create side input (materialized as Map)
PCollection<KV<String, UserProfile>> profiles = pipeline.apply(
    TextIO.read().from("profiles.txt")
).apply(ParDo.of(new ParseProfileFn()));

PCollectionView<Map<String, UserProfile>> profileView = 
    profiles.apply(View.asMap());

// 2. Use side input in ParDo
PCollection<EnrichedTransaction> enriched = transactions.apply(
    ParDo.of(new EnrichTransactionFn(profileView))
        .withSideInputs(profileView)
);

public static class EnrichTransactionFn extends DoFn<Transaction, EnrichedTransaction> {
    
    private final PCollectionView<Map<String, UserProfile>> profileView;
    
    public EnrichTransactionFn(PCollectionView<Map<String, UserProfile>> profileView) {
        this.profileView = profileView;
    }
    
    @ProcessElement
    public void processElement(ProcessContext c) {
        Transaction txn = c.element();
        
        // Lookup profile from side input
        Map<String, UserProfile> profileMap = c.sideInput(profileView);
        UserProfile profile = profileMap.get(txn.getUserId());
        
        if (profile != null) {
            c.output(new EnrichedTransaction(txn, profile));
        }
    }
}
```

**Python:**

```python
import apache_beam as beam

# Create side input
profiles = (
    pipeline
    | 'ReadProfiles' >> beam.io.ReadFromText('profiles.txt')
    | 'ParseProfiles' >> beam.Map(parse_profile)
)

profile_dict = beam.pvalue.AsDict(profiles)

# Use side input
enriched = (
    transactions
    | beam.ParDo(EnrichTransactionFn(), profile_dict=profile_dict)
)

class EnrichTransactionFn(beam.DoFn):
    def process(self, element, profile_dict):
        txn = element
        profile = profile_dict.get(txn['user_id'])
        if profile:
            yield {**txn, **profile}
```

---

### Windowed Side Inputs

```java
// Side input that changes over time (e.g., exchange rates)

PCollection<KV<String, Double>> rates = pipeline.apply(
    KafkaIO.<String, String>read()...
).apply(/* parse rates */);

// Window side input to match main input
PCollectionView<Map<String, Double>> ratesView = rates
    .apply(Window.<KV<String, Double>>into(
        FixedWindows.of(Duration.standardMinutes(1))
    ))
    .apply(View.asMap());

// Apply to main input
PCollection<ConvertedTransaction> converted = transactions
    .apply(Window.<Transaction>into(
        FixedWindows.of(Duration.standardMinutes(1))
    ))
    .apply(ParDo.of(new ConvertCurrencyFn(ratesView))
        .withSideInputs(ratesView)
    );
```

---

## 🧮 4. Custom CombineFns

### Why CombineFn?

```
Problem: GroupByKey + ParDo is inefficient

// INEFFICIENT:
PCollection<KV<String, Iterable<Integer>>> grouped = kvs.apply(GroupByKey.create());
PCollection<KV<String, Integer>> sums = grouped.apply(ParDo.of(new SumFn()));

Issues:
├─ All values sent to single worker (shuffle)
├─ No combiner optimization
└─ High memory usage

// EFFICIENT:
PCollection<KV<String, Integer>> sums = kvs.apply(
    Combine.perKey(Sum.ofIntegers())
);

Benefits:
├─ Partial aggregation before shuffle
├─ Reduced network transfer
└─ Constant memory usage
```

---

### Implementing CombineFn

```java
import org.apache.beam.sdk.transforms.Combine.CombineFn;

// Example: Calculate average
public class AverageFn extends CombineFn<Integer, AverageFn.Accum, Double> {
    
    // Accumulator: holds intermediate state
    public static class Accum {
        int sum = 0;
        int count = 0;
    }
    
    @Override
    public Accum createAccumulator() {
        return new Accum();
    }
    
    @Override
    public Accum addInput(Accum accum, Integer input) {
        accum.sum += input;
        accum.count++;
        return accum;
    }
    
    @Override
    public Accum mergeAccumulators(Iterable<Accum> accums) {
        Accum merged = new Accum();
        for (Accum accum : accums) {
            merged.sum += accum.sum;
            merged.count += accum.count;
        }
        return merged;
    }
    
    @Override
    public Double extractOutput(Accum accum) {
        return ((double) accum.sum) / accum.count;
    }
}

// Usage
PCollection<KV<String, Double>> averages = kvs.apply(
    Combine.perKey(new AverageFn())
);
```

**Execution:**

```
Input: KV<"user_123", 10>, KV<"user_123", 20>, KV<"user_123", 30>

Step 1: Local combiner (before shuffle)
├─ Worker 1: [10, 20] → Accum{sum=30, count=2}
└─ Worker 2: [30] → Accum{sum=30, count=1}

Step 2: Shuffle grouped accumulators by key

Step 3: Merge accumulators
├─ mergeAccumulators([Accum{30, 2}, Accum{30, 1}])
└─ Result: Accum{sum=60, count=3}

Step 4: Extract output
├─ extractOutput(Accum{60, 3})
└─ Result: 20.0

Output: KV<"user_123", 20.0>
```

---

## 🔧 5. Stateful DoFn

### When to Use Stateful Processing

```
Use cases:
├─ Deduplication (track seen IDs)
├─ Session tracking (maintain user state)
├─ Rate limiting (count requests per window)
└─ Custom windowing logic
```

---

### State and Timers

```java
import org.apache.beam.sdk.state.*;
import org.apache.beam.sdk.transforms.DoFn;
import org.apache.beam.sdk.values.KV;

public class DeduplicationFn extends DoFn<KV<String, Event>, KV<String, Event>> {
    
    // State: Track seen event IDs
    @StateId("seen")
    private final StateSpec<SetState<String>> seenSpec = StateSpecs.set();
    
    // Timer: Clear state after 1 hour
    @TimerId("expire")
    private final TimerSpec expireSpec = TimerSpecs.timer(TimeDomain.EVENT_TIME);
    
    @ProcessElement
    public void processElement(
        ProcessContext c,
        @StateId("seen") SetState<String> seenState,
        @TimerId("expire") Timer expireTimer
    ) {
        KV<String, Event> kv = c.element();
        Event event = kv.getValue();
        
        // Check if event ID already seen
        if (seenState.contains(event.getId()).read()) {
            // Duplicate, skip
            return;
        }
        
        // New event, emit and track
        seenState.add(event.getId());
        c.output(kv);
        
        // Set timer to clear state after 1 hour
        expireTimer.set(c.timestamp().plus(Duration.standardHours(1)));
    }
    
    @OnTimer("expire")
    public void onExpire(
        OnTimerContext c,
        @StateId("seen") SetState<String> seenState
    ) {
        // Clear state
        seenState.clear();
    }
}

// Usage
PCollection<KV<String, Event>> deduplicated = events
    .apply(ParDo.of(new DeduplicationFn()));
```

---

### Session Tracking Example

```java
public class SessionTrackerFn extends DoFn<KV<String, Event>, KV<String, Session>> {
    
    @StateId("session")
    private final StateSpec<ValueState<Session>> sessionSpec = 
        StateSpecs.value(Session.class);
    
    @TimerId("timeout")
    private final TimerSpec timeoutSpec = TimerSpecs.timer(TimeDomain.EVENT_TIME);
    
    private static final Duration SESSION_GAP = Duration.standardMinutes(30);
    
    @ProcessElement
    public void processElement(
        ProcessContext c,
        @StateId("session") ValueState<Session> sessionState,
        @TimerId("timeout") Timer timeoutTimer
    ) {
        Event event = c.element().getValue();
        Session session = sessionState.read();
        
        if (session == null) {
            // Start new session
            session = new Session(event.getUserId(), event.getTimestamp());
        }
        
        // Add event to session
        session.addEvent(event);
        
        // Update state
        sessionState.write(session);
        
        // Reset timeout timer
        timeoutTimer.set(event.getTimestamp().plus(SESSION_GAP));
    }
    
    @OnTimer("timeout")
    public void onTimeout(
        OnTimerContext c,
        @StateId("session") ValueState<Session> sessionState,
        OutputReceiver<KV<String, Session>> out
    ) {
        // Session timed out, emit final session
        Session session = sessionState.read();
        if (session != null) {
            out.output(KV.of(session.getUserId(), session));
            sessionState.clear();
        }
    }
}
```

---

## 📈 6. Performance Optimization

### Fusion Optimization

```
Beam optimizes by fusing compatible transforms:

Pipeline:
PCollection<String> lines = ...;
PCollection<String> words = lines.apply(ParDo.of(new SplitFn()));
PCollection<String> filtered = words.apply(ParDo.of(new FilterFn()));
PCollection<String> upper = filtered.apply(ParDo.of(new UpperCaseFn()));

Fused Execution (single worker task):
lines → [SplitFn → FilterFn → UpperCaseFn] → upper

Benefits:
├─ No intermediate materialization
├─ Reduced serialization/deserialization
└─ Better CPU cache locality

Preventing Fusion (when needed):
upper = filtered.apply(Reshuffle.<String>viaRandomKey());
// Forces materialization, breaks fusion
```

---

### Combiner Lifting

```
GroupByKey + Combine can be lifted to reduce shuffle:

Original:
kvs → GroupByKey → Combine → output

Optimized:
kvs → PartialCombine (local) → GroupByKey → FinalCombine → output

Reducing shuffle size from O(N) to O(K * W):
├─ N = total elements
├─ K = number of keys
└─ W = average values per key after combining
```

---

## 🏆 Interview Questions (Intermediate Level)

1. **Explain the difference between early, on-time, and late triggers.**
2. **What are the three accumulation modes in Beam? When would you use each?**
3. **How do side inputs work? Give an example use case.**
4. **Why should you use CombineFn instead of GroupByKey + ParDo?**
5. **What is the difference between state and side inputs?**
6. **How would you implement deduplication in Beam?**

---

## 🎓 Summary Checklist

- [ ] Configure triggers for early, on-time, and late firings
- [ ] Choose appropriate accumulation modes
- [ ] Use side inputs for enrichment
- [ ] Implement custom CombineFns
- [ ] Use stateful DoFns with state and timers
- [ ] Understand fusion and combiner lifting optimizations
- [ ] Answer intermediate interview questions

**Next:** [EXPERT.md →](EXPERT.md)
