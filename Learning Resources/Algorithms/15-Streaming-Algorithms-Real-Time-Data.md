# Streaming Algorithms - Real-Time Data Processing

**Target Role:** Principal Data Engineer / Staff Engineer (40+ LPA)  
**Difficulty:** Advanced  
**Learning Time:** 1-2 weeks  
**Interview Frequency:** ⭐⭐⭐⭐

---

## 📚 Overview

Streaming algorithms process data as it arrives, without storing the entire dataset in memory. They're essential for real-time analytics, monitoring, and big data processing.

**Key Characteristics:**
- **Single Pass:** Data seen only once
- **Limited Memory:** Space << data size
- **Real-Time:** Low latency processing
- **Approximate:** Trade accuracy for speed/space

**Applications:**
- Real-time analytics dashboards
- Network traffic monitoring
- Log analysis and anomaly detection
- Time-series data processing

**Used By:**
- Apache Flink/Spark Streaming
- Prometheus/Datadog metrics
- Twitter trending topics
- Financial market data processing

---

## 1. Reservoir Sampling

### The Problem

**Scenario:** Sample K items uniformly at random from a stream of unknown size.

```
Challenge:
- Stream size is unknown in advance
- Can't store entire stream
- Must maintain uniform distribution

Example:
Sample 10 random lines from a 1TB log file
```

**Use Cases:**
- Sample data for testing (get representative subset)
- Monitoring (sample 1% of requests for detailed logging)
- Machine learning (sample training data from stream)

---

### Algorithm Explanation

**Reservoir Sampling Algorithm (Algorithm R)**

```
Maintain a reservoir of size k:

reservoir = [item_0, item_1, ..., item_{k-1}]

For each new item (i >= k):
  j = random(0, i)
  if j < k:
    reservoir[j] = item_i

Proof of uniform distribution:
- Each item has probability k/n of being in reservoir
- Where n = total items seen
```

**Visualization:**

```
Stream: [A, B, C, D, E, F, G, H, ...]
Reservoir size k = 3

Step 1: [A, _, _]  (fill reservoir)
Step 2: [A, B, _]
Step 3: [A, B, C]

Step 4: Item D
  j = random(0, 3) = 1
  Replace reservoir[1]: [A, D, C]

Step 5: Item E
  j = random(0, 4) = 4 (>= k)
  Don't replace: [A, D, C]

Step 6: Item F
  j = random(0, 5) = 0
  Replace reservoir[0]: [F, D, C]

...
```

---

### Production-Grade Implementation (Java)

```java
package com.dateng.streaming;

import java.util.*;
import java.util.concurrent.ThreadLocalRandom;

/**
 * Reservoir Sampling for uniform random sampling from streams
 * 
 * Features:
 * - Weighted sampling support
 * - Thread-safe operations
 * - Statistics tracking
 * 
 * Use Cases:
 * - Sample data for monitoring/debugging
 * - Create representative datasets
 * - A/B testing (sample users)
 * 
 * @author Principal Data Engineer
 */
public class ReservoirSampler<T> {
    
    private final int reservoirSize;
    private final List<T> reservoir;
    private long itemsSeen;
    private final Random random;
    
    /**
     * Constructor
     * 
     * @param reservoirSize Maximum number of samples to keep
     */
    public ReservoirSampler(int reservoirSize) {
        if (reservoirSize <= 0) {
            throw new IllegalArgumentException("Reservoir size must be positive");
        }
        
        this.reservoirSize = reservoirSize;
        this.reservoir = new ArrayList<>(reservoirSize);
        this.itemsSeen = 0;
        this.random = ThreadLocalRandom.current();
        
        System.out.printf("[ReservoirSampler] Created with size %d%n", reservoirSize);
    }
    
    /**
     * Add an item to the stream
     * 
     * Time Complexity: O(1)
     * Space Complexity: O(k) where k = reservoir size
     * 
     * @param item Item to potentially sample
     */
    public synchronized void add(T item) {
        itemsSeen++;
        
        if (reservoir.size() < reservoirSize) {
            // Fill reservoir
            reservoir.add(item);
        } else {
            // Randomly decide whether to include item
            long j = random.nextLong(itemsSeen);
            
            if (j < reservoirSize) {
                reservoir.set((int) j, item);
            }
        }
    }
    
    /**
     * Get current sample
     * 
     * @return List of sampled items
     */
    public synchronized List<T> getSample() {
        return new ArrayList<>(reservoir);
    }
    
    /**
     * Get sample size
     */
    public synchronized int getSampleSize() {
        return reservoir.size();
    }
    
    /**
     * Get total items seen
     */
    public synchronized long getItemsSeen() {
        return itemsSeen;
    }
    
    /**
     * Get sampling rate
     */
    public synchronized double getSamplingRate() {
        if (itemsSeen == 0) return 0;
        return Math.min(1.0, reservoir.size() / (double) itemsSeen);
    }
    
    /**
     * Clear the reservoir
     */
    public synchronized void clear() {
        reservoir.clear();
        itemsSeen = 0;
    }
    
    /**
     * Get statistics
     */
    public synchronized Stats getStats() {
        return new Stats(
            reservoirSize,
            reservoir.size(),
            itemsSeen,
            getSamplingRate()
        );
    }
    
    public static class Stats {
        public final int reservoirSize;
        public final int currentSize;
        public final long itemsSeen;
        public final double samplingRate;
        
        Stats(int reservoirSize, int currentSize, long itemsSeen, double samplingRate) {
            this.reservoirSize = reservoirSize;
            this.currentSize = currentSize;
            this.itemsSeen = itemsSeen;
            this.samplingRate = samplingRate;
        }
        
        @Override
        public String toString() {
            return String.format(
                "ReservoirSampler Stats:\n" +
                "  Reservoir size: %d\n" +
                "  Current samples: %d\n" +
                "  Items seen: %,d\n" +
                "  Sampling rate: %.4f%%",
                reservoirSize,
                currentSize,
                itemsSeen,
                samplingRate * 100
            );
        }
    }
}
```

---

### Weighted Reservoir Sampling

**Problem:** Sample with different weights (e.g., sample errors more frequently than successes)

```java
package com.dateng.streaming;

import java.util.*;
import java.util.concurrent.ThreadLocalRandom;

/**
 * Weighted Reservoir Sampling (Algorithm A-Res)
 * 
 * Each item has a weight; probability of inclusion proportional to weight
 */
public class WeightedReservoirSampler<T> {
    
    private final int reservoirSize;
    private final PriorityQueue<WeightedItem> reservoir;
    private final Random random;
    
    /**
     * Constructor
     * 
     * @param reservoirSize Maximum number of samples
     */
    public WeightedReservoirSampler(int reservoirSize) {
        this.reservoirSize = reservoirSize;
        this.reservoir = new PriorityQueue<>(reservoirSize, 
            Comparator.comparingDouble(item -> item.key));
        this.random = ThreadLocalRandom.current();
    }
    
    /**
     * Add item with weight
     * 
     * Algorithm A-Res:
     * 1. Generate random key: k = u^(1/w) where u ~ Uniform(0,1), w = weight
     * 2. If reservoir not full, add item
     * 3. Else if k > min_key in reservoir, replace item with min_key
     * 
     * @param item Item to add
     * @param weight Weight of item (higher = more likely to be sampled)
     */
    public void add(T item, double weight) {
        if (weight <= 0) {
            throw new IllegalArgumentException("Weight must be positive");
        }
        
        // Generate random key
        double u = random.nextDouble();
        double key = Math.pow(u, 1.0 / weight);
        
        WeightedItem wi = new WeightedItem(item, weight, key);
        
        if (reservoir.size() < reservoirSize) {
            reservoir.offer(wi);
        } else if (key > reservoir.peek().key) {
            reservoir.poll();
            reservoir.offer(wi);
        }
    }
    
    /**
     * Get sample
     */
    public List<T> getSample() {
        List<T> sample = new ArrayList<>();
        for (WeightedItem wi : reservoir) {
            sample.add(wi.item);
        }
        return sample;
    }
    
    private class WeightedItem {
        final T item;
        final double weight;
        final double key;
        
        WeightedItem(T item, double weight, double key) {
            this.item = item;
            this.weight = weight;
            this.key = key;
        }
    }
}
```

---

### Use Case: Log Sampling

```java
package com.dateng.streaming;

import java.util.*;
import java.util.concurrent.ThreadLocalRandom;

/**
 * Sample logs for debugging without storing all logs
 */
public class LogSampler {
    
    private final ReservoirSampler<LogEntry> errorSampler;
    private final ReservoirSampler<LogEntry> warnSampler;
    private final ReservoirSampler<LogEntry> infoSampler;
    
    private long totalLogs = 0;
    
    public LogSampler() {
        // Keep different sample sizes based on severity
        this.errorSampler = new ReservoirSampler<>(1000);  // Keep 1000 errors
        this.warnSampler = new ReservoirSampler<>(500);    // Keep 500 warnings
        this.infoSampler = new ReservoirSampler<>(100);    // Keep 100 info logs
    }
    
    /**
     * Process a log entry
     */
    public void log(LogLevel level, String message) {
        LogEntry entry = new LogEntry(System.currentTimeMillis(), level, message);
        totalLogs++;
        
        switch (level) {
            case ERROR:
                errorSampler.add(entry);
                break;
            case WARN:
                warnSampler.add(entry);
                break;
            case INFO:
                infoSampler.add(entry);
                break;
        }
    }
    
    /**
     * Get sampled errors for debugging
     */
    public List<LogEntry> getErrorSample() {
        return errorSampler.getSample();
    }
    
    /**
     * Get sampled warnings
     */
    public List<LogEntry> getWarnSample() {
        return warnSampler.getSample();
    }
    
    /**
     * Get sampled info logs
     */
    public List<LogEntry> getInfoSample() {
        return infoSampler.getSample();
    }
    
    /**
     * Print sampling statistics
     */
    public void printStats() {
        System.out.println("\n=== Log Sampling Statistics ===");
        System.out.printf("Total logs processed: %,d%n", totalLogs);
        System.out.println("\nError logs:");
        System.out.println(errorSampler.getStats());
        System.out.println("\nWarning logs:");
        System.out.println(warnSampler.getStats());
        System.out.println("\nInfo logs:");
        System.out.println(infoSampler.getStats());
    }
    
    enum LogLevel {
        ERROR, WARN, INFO
    }
    
    static class LogEntry {
        final long timestamp;
        final LogLevel level;
        final String message;
        
        LogEntry(long timestamp, LogLevel level, String message) {
            this.timestamp = timestamp;
            this.level = level;
            this.message = message;
        }
        
        @Override
        public String toString() {
            return String.format("[%d] %s: %s", timestamp, level, message);
        }
    }
}
```

---

## 2. Flajolet-Martin Algorithm (Distinct Count)

### The Problem

**Scenario:** Count unique users visiting a website with billions of page views.

```
Challenge:
- Can't store all user IDs (too much memory)
- Need approximate count

Traditional HashSet:
- 1 billion unique users
- 16 bytes per UUID
- Memory: 16 GB

Flajolet-Martin:
- 1 billion unique users
- Memory: ~10 KB
- Error: ~20% (can be improved)
```

---

### Algorithm Explanation

**Key Insight:** If you hash values uniformly, the max number of trailing zeros tells you about cardinality.

```
Example with 3-bit hashes:

Items: [A, B, C, D]

Hash(A) = 101 → 0 trailing zeros
Hash(B) = 100 → 2 trailing zeros
Hash(C) = 110 → 1 trailing zero
Hash(D) = 010 → 1 trailing zero

Max trailing zeros (R) = 2

Estimated cardinality ≈ 2^R = 4

Actual cardinality = 4 ✓
```

**Why it works:**
- Probability of hash ending in 0: 1/2
- Probability of hash ending in 00: 1/4
- Probability of hash ending in 000: 1/8
- If max trailing zeros = k, likely saw ~2^k distinct items

---

### Implementation (Java)

```java
package com.dateng.streaming;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

/**
 * Flajolet-Martin algorithm for distinct count estimation
 * 
 * Features:
 * - O(log n) space complexity
 * - Single pass over data
 * - Probabilistic estimate
 * 
 * Improvement over basic FM: Use multiple hash functions and take median
 * 
 * @author Principal Data Engineer
 */
public class FlajoletMartin {
    
    private final int numBitmaps;
    private final int[] maxTrailingZeros;
    private final MessageDigest md5;
    
    /**
     * Constructor
     * 
     * @param numBitmaps Number of hash functions (higher = more accurate)
     */
    public FlajoletMartin(int numBitmaps) {
        this.numBitmaps = numBitmaps;
        this.maxTrailingZeros = new int[numBitmaps];
        
        try {
            this.md5 = MessageDigest.getInstance("MD5");
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("MD5 not available", e);
        }
        
        System.out.printf("[FlajoletMartin] Created with %d bitmaps%n", numBitmaps);
    }
    
    /**
     * Add an item
     * 
     * Time Complexity: O(numBitmaps)
     * 
     * @param item Item to add
     */
    public void add(String item) {
        byte[] digest = md5.digest(item.getBytes(StandardCharsets.UTF_8));
        long hash = bytesToLong(digest, 0);
        
        for (int i = 0; i < numBitmaps; i++) {
            // Use different part of hash for each bitmap
            long bitmapHash = hash ^ i;
            
            // Count trailing zeros
            int trailingZeros = Long.numberOfTrailingZeros(bitmapHash);
            
            // Update maximum
            if (trailingZeros > maxTrailingZeros[i]) {
                maxTrailingZeros[i] = trailingZeros;
            }
        }
    }
    
    /**
     * Estimate distinct count
     * 
     * Uses median of estimates from all bitmaps for better accuracy
     * 
     * @return Estimated number of distinct items
     */
    public long estimateCount() {
        // Calculate estimates from each bitmap
        long[] estimates = new long[numBitmaps];
        
        for (int i = 0; i < numBitmaps; i++) {
            estimates[i] = (long) Math.pow(2, maxTrailingZeros[i]);
        }
        
        // Return median estimate
        Arrays.sort(estimates);
        return estimates[numBitmaps / 2];
    }
    
    /**
     * Get expected error rate
     * 
     * Flajolet-Martin error: ~78% for single hash
     * With multiple hashes and median: ~20%
     * 
     * Use HyperLogLog for better accuracy (~2%)
     */
    public double getExpectedErrorRate() {
        return 0.20; // 20% error with median of multiple estimates
    }
    
    private long bytesToLong(byte[] bytes, int offset) {
        long result = 0;
        for (int i = 0; i < 8 && offset + i < bytes.length; i++) {
            result = (result << 8) | (bytes[offset + i] & 0xFF);
        }
        return result;
    }
    
    /**
     * Clear all counters
     */
    public void clear() {
        Arrays.fill(maxTrailingZeros, 0);
    }
}
```

---

## 3. Misra-Gries Algorithm (Frequent Items)

### The Problem

**Scenario:** Find top-K most frequent items in a stream (e.g., most visited URLs, trending hashtags).

```
Challenge:
- Stream is too large to count all items
- Need to identify heavy hitters

Example:
Find top 10 hashtags from 1 billion tweets
```

**Use Cases:**
- Trending topics (Twitter, Reddit)
- Most accessed URLs (web server logs)
- Fraud detection (most frequent patterns)
- Network monitoring (heavy hitters)

---

### Algorithm Explanation

**Misra-Gries Algorithm** (Space-Saving variation)

```
Maintain k counters for k frequent items:

When new item arrives:
1. If item already tracked, increment its counter
2. Else if counters < k, add new counter for item
3. Else decrement all counters by 1, remove zeros

Example (k=2):

Stream: [A, B, A, C, A, B, D, A, B]

Step 1: A → {A:1}
Step 2: B → {A:1, B:1}
Step 3: A → {A:2, B:1}
Step 4: C → Decrement all: {A:1, B:0} → Remove B → {A:1, C:1}
Step 5: A → {A:2, C:1}
Step 6: B → Decrement all: {A:1, C:0} → {A:1, B:1}
Step 7: D → Decrement all: {A:0, B:0} → {D:1}
Step 8: A → {D:1, A:1}
Step 9: B → Decrement all: {D:0, A:0} → {B:1}

Result: B appears most frequently (but we lost exact counts)

Guarantee: True top-k items will be in result
Error: Counts may be underestimated by at most n/k
```

---

### Implementation (Java)

```java
package com.dateng.streaming;

import java.util.*;

/**
 * Misra-Gries algorithm for finding frequent items
 * 
 * Also known as Space-Saving algorithm
 * 
 * Features:
 * - Find top-K heavy hitters
 * - O(k) space complexity
 * - Guaranteed to find items with frequency > n/(k+1)
 * 
 * Use Cases:
 * - Trending topics
 * - Anomaly detection
 * - Cache eviction policies
 * 
 * @author Principal Data Engineer
 */
public class MisraGries<T> {
    
    private final int k;
    private final Map<T, Long> counters;
    private long totalItems;
    
    /**
     * Constructor
     * 
     * @param k Number of frequent items to track
     */
    public MisraGries(int k) {
        if (k <= 0) {
            throw new IllegalArgumentException("k must be positive");
        }
        
        this.k = k;
        this.counters = new HashMap<>(k);
        this.totalItems = 0;
        
        System.out.printf("[MisraGries] Created with k=%d%n", k);
    }
    
    /**
     * Add an item to the stream
     * 
     * Time Complexity: O(k) worst case
     * Space Complexity: O(k)
     * 
     * @param item Item to add
     */
    public void add(T item) {
        totalItems++;
        
        if (counters.containsKey(item)) {
            // Item already tracked, increment counter
            counters.put(item, counters.get(item) + 1);
        } else if (counters.size() < k) {
            // Have space for new item
            counters.put(item, 1L);
        } else {
            // No space, decrement all counters
            decrementAll();
        }
    }
    
    /**
     * Decrement all counters by 1
     * Remove items with zero count
     */
    private void decrementAll() {
        Iterator<Map.Entry<T, Long>> iterator = counters.entrySet().iterator();
        
        while (iterator.hasNext()) {
            Map.Entry<T, Long> entry = iterator.next();
            long newCount = entry.getValue() - 1;
            
            if (newCount <= 0) {
                iterator.remove();
            } else {
                entry.setValue(newCount);
            }
        }
    }
    
    /**
     * Get top-K frequent items
     * 
     * Note: Counts are approximations (may be underestimated)
     * 
     * @return List of (item, count) pairs sorted by count
     */
    public List<ItemCount<T>> getTopK() {
        List<ItemCount<T>> topK = new ArrayList<>();
        
        for (Map.Entry<T, Long> entry : counters.entrySet()) {
            topK.add(new ItemCount<>(entry.getKey(), entry.getValue()));
        }
        
        topK.sort(Comparator.comparingLong((ItemCount<T> ic) -> ic.count).reversed());
        
        return topK;
    }
    
    /**
     * Get estimated frequency of an item
     * 
     * Returns 0 if item not tracked (could still have occurred < n/k times)
     */
    public long getFrequency(T item) {
        return counters.getOrDefault(item, 0L);
    }
    
    /**
     * Get maximum possible error
     * 
     * Actual frequency >= estimated frequency
     * Actual frequency <= estimated frequency + n/k
     */
    public long getMaxError() {
        return totalItems / k;
    }
    
    /**
     * Clear all counters
     */
    public void clear() {
        counters.clear();
        totalItems = 0;
    }
    
    /**
     * Get statistics
     */
    public Stats getStats() {
        return new Stats(k, counters.size(), totalItems, getMaxError());
    }
    
    public static class ItemCount<T> {
        public final T item;
        public final long count;
        
        public ItemCount(T item, long count) {
            this.item = item;
            this.count = count;
        }
        
        @Override
        public String toString() {
            return String.format("%s: %d", item, count);
        }
    }
    
    public static class Stats {
        public final int k;
        public final int itemsTracked;
        public final long totalItems;
        public final long maxError;
        
        Stats(int k, int itemsTracked, long totalItems, long maxError) {
            this.k = k;
            this.itemsTracked = itemsTracked;
            this.totalItems = totalItems;
            this.maxError = maxError;
        }
        
        @Override
        public String toString() {
            return String.format(
                "MisraGries Stats:\n" +
                "  k: %d\n" +
                "  Items tracked: %d\n" +
                "  Total items: %,d\n" +
                "  Max error: %,d",
                k, itemsTracked, totalItems, maxError
            );
        }
    }
}
```

---

### Use Case: Twitter Trending Topics

```java
package com.dateng.streaming;

import java.util.*;
import java.util.concurrent.ThreadLocalRandom;

/**
 * Find trending hashtags in real-time
 */
public class TrendingTopics {
    
    private final MisraGries<String> heavyHitters;
    private final int windowSize;
    private final Queue<String> window;
    
    /**
     * Constructor
     * 
     * @param k Number of trending topics to track
     * @param windowSize Time window (number of tweets)
     */
    public TrendingTopics(int k, int windowSize) {
        this.heavyHitters = new MisraGries<>(k);
        this.windowSize = windowSize;
        this.window = new LinkedList<>();
    }
    
    /**
     * Process a tweet (extract hashtags and update trending topics)
     */
    public void processTweet(String tweet) {
        // Extract hashtags
        List<String> hashtags = extractHashtags(tweet);
        
        for (String hashtag : hashtags) {
            heavyHitters.add(hashtag);
            window.offer(hashtag);
        }
        
        // Maintain sliding window
        if (window.size() > windowSize) {
            window.poll();
        }
    }
    
    /**
     * Get current trending topics
     */
    public List<MisraGries.ItemCount<String>> getTrendingTopics() {
        return heavyHitters.getTopK();
    }
    
    /**
     * Extract hashtags from tweet
     */
    private List<String> extractHashtags(String tweet) {
        List<String> hashtags = new ArrayList<>();
        String[] words = tweet.split("\\s+");
        
        for (String word : words) {
            if (word.startsWith("#")) {
                hashtags.add(word.toLowerCase());
            }
        }
        
        return hashtags;
    }
    
    /**
     * Print trending topics
     */
    public void printTrending() {
        System.out.println("\n=== Trending Topics ===");
        
        List<MisraGries.ItemCount<String>> trending = getTrendingTopics();
        
        for (int i = 0; i < Math.min(10, trending.size()); i++) {
            MisraGries.ItemCount<String> topic = trending.get(i);
            System.out.printf("%d. %s (%d mentions)%n", i + 1, topic.item, topic.count);
        }
        
        System.out.println("\n" + heavyHitters.getStats());
    }
}
```

---

## 4. Complete Demo Application

```java
package com.dateng.streaming;

import java.util.*;
import java.util.concurrent.ThreadLocalRandom;

/**
 * Comprehensive demo of all streaming algorithms
 */
public class StreamingAlgorithmsDemo {
    
    public static void main(String[] args) {
        System.out.println("=== Streaming Algorithms Demo ===\n");
        
        demoReservoirSampling();
        demoFlajoletMartin();
        demoMisraGries();
    }
    
    /**
     * Demo 1: Reservoir Sampling
     */
    private static void demoReservoirSampling() {
        System.out.println("1. Reservoir Sampling Demo");
        System.out.println("-------------------------");
        
        ReservoirSampler<Integer> sampler = new ReservoirSampler<>(100);
        
        // Stream 1 million numbers
        for (int i = 0; i < 1_000_000; i++) {
            sampler.add(i);
        }
        
        // Check distribution
        List<Integer> sample = sampler.getSample();
        
        System.out.println(sampler.getStats());
        
        // Verify uniform distribution
        Collections.sort(sample);
        System.out.printf("\nSample (first 10): %s%n", sample.subList(0, 10));
        System.out.printf("Sample (last 10): %s%n", sample.subList(90, 100));
        
        // Expected: samples spread across entire range [0, 1M)
        double avgGap = (sample.get(99) - sample.get(0)) / 99.0;
        System.out.printf("Average gap between samples: %.0f (expected: ~10,000)%n", avgGap);
        
        System.out.println();
    }
    
    /**
     * Demo 2: Flajolet-Martin (Distinct Count)
     */
    private static void demoFlajoletMartin() {
        System.out.println("2. Flajolet-Martin Demo");
        System.out.println("-----------------------");
        
        FlajoletMartin fm = new FlajoletMartin(64);
        
        // Stream with known distinct count
        int actualDistinct = 100_000;
        Random rand = new Random(42);
        
        for (int i = 0; i < 1_000_000; i++) {
            int value = rand.nextInt(actualDistinct);
            fm.add("item-" + value);
        }
        
        long estimated = fm.estimateCount();
        double error = Math.abs(estimated - actualDistinct) / (double) actualDistinct * 100;
        
        System.out.printf("Actual distinct count: %,d%n", actualDistinct);
        System.out.printf("Estimated count: %,d%n", estimated);
        System.out.printf("Error: %.2f%% (expected: ~20%%)%n", error);
        
        System.out.println();
    }
    
    /**
     * Demo 3: Misra-Gries (Frequent Items)
     */
    private static void demoMisraGries() {
        System.out.println("3. Misra-Gries Demo");
        System.out.println("------------------");
        
        MisraGries<String> mg = new MisraGries<>(10);
        
        // Generate stream with some frequent items
        Map<String, Integer> actualCounts = new HashMap<>();
        Random rand = new Random(42);
        
        // Add frequent items
        String[] frequentItems = {"item-A", "item-B", "item-C"};
        for (int i = 0; i < 10_000; i++) {
            String item = frequentItems[rand.nextInt(frequentItems.length)];
            mg.add(item);
            actualCounts.put(item, actualCounts.getOrDefault(item, 0) + 1);
        }
        
        // Add many rare items
        for (int i = 0; i < 90_000; i++) {
            String item = "item-" + i;
            mg.add(item);
            actualCounts.put(item, actualCounts.getOrDefault(item, 0) + 1);
        }
        
        System.out.println("Top-10 frequent items:");
        List<MisraGries.ItemCount<String>> topK = mg.getTopK();
        
        for (int i = 0; i < topK.size(); i++) {
            MisraGries.ItemCount<String> ic = topK.get(i);
            int actual = actualCounts.get(ic.item);
            System.out.printf("%d. %s: estimated=%,d, actual=%,d%n", 
                              i + 1, ic.item, ic.count, actual);
        }
        
        System.out.println("\n" + mg.getStats());
    }
}
```

---

## 5. Performance Comparison

```java
package com.dateng.streaming;

import java.util.*;

/**
 * Compare streaming algorithms vs exact algorithms
 */
public class StreamingVsExactComparison {
    
    public static void main(String[] args) {
        System.out.println("=== Streaming vs Exact Comparison ===\n");
        
        compareDistinctCount();
        compareFrequentItems();
    }
    
    private static void compareDistinctCount() {
        System.out.println("Distinct Count: Exact vs Flajolet-Martin vs HyperLogLog");
        System.out.println("--------------------------------------------------------");
        
        int numItems = 10_000_000;
        int numDistinct = 1_000_000;
        
        // Exact (HashSet)
        Set<Integer> exactSet = new HashSet<>();
        long exactTime = System.nanoTime();
        Random rand = new Random(42);
        
        for (int i = 0; i < numItems; i++) {
            exactSet.add(rand.nextInt(numDistinct));
        }
        
        exactTime = (System.nanoTime() - exactTime) / 1_000_000;
        int exactCount = exactSet.size();
        long exactMemory = estimateSetMemory(exactSet);
        
        // Flajolet-Martin
        FlajoletMartin fm = new FlajoletMartin(64);
        long fmTime = System.nanoTime();
        rand = new Random(42);
        
        for (int i = 0; i < numItems; i++) {
            fm.add(String.valueOf(rand.nextInt(numDistinct)));
        }
        
        fmTime = (System.nanoTime() - fmTime) / 1_000_000;
        long fmCount = fm.estimateCount();
        long fmMemory = 64 * 4; // 64 integers
        
        // Print comparison
        System.out.printf("Processing %,d items with %,d distinct values:%n", numItems, numDistinct);
        System.out.println();
        
        System.out.printf("Exact (HashSet):%n");
        System.out.printf("  Count: %,d%n", exactCount);
        System.out.printf("  Time: %d ms%n", exactTime);
        System.out.printf("  Memory: %.2f MB%n", exactMemory / (1024.0 * 1024));
        System.out.println();
        
        System.out.printf("Flajolet-Martin:%n");
        System.out.printf("  Count: %,d%n", fmCount);
        System.out.printf("  Time: %d ms%n", fmTime);
        System.out.printf("  Memory: %.2f KB%n", fmMemory / 1024.0);
        System.out.printf("  Error: %.2f%%%n", Math.abs(fmCount - exactCount) / (double) exactCount * 100);
        System.out.println();
        
        System.out.printf("Savings:%n");
        System.out.printf("  Memory: %.0fx smaller%n", exactMemory / (double) fmMemory);
        System.out.printf("  Time: %.1fx faster%n", (double) exactTime / fmTime);
        System.out.println();
    }
    
    private static void compareFrequentItems() {
        System.out.println("Frequent Items: Exact vs Misra-Gries");
        System.out.println("------------------------------------");
        
        int numItems = 1_000_000;
        int k = 100;
        
        // Exact (HashMap)
        Map<String, Long> exactMap = new HashMap<>();
        long exactTime = System.nanoTime();
        Random rand = new Random(42);
        
        for (int i = 0; i < numItems; i++) {
            String item = "item-" + rand.nextInt(1000);
            exactMap.put(item, exactMap.getOrDefault(item, 0L) + 1);
        }
        
        exactTime = (System.nanoTime() - exactTime) / 1_000_000;
        long exactMemory = estimateMapMemory(exactMap);
        
        // Misra-Gries
        MisraGries<String> mg = new MisraGries<>(k);
        long mgTime = System.nanoTime();
        rand = new Random(42);
        
        for (int i = 0; i < numItems; i++) {
            String item = "item-" + rand.nextInt(1000);
            mg.add(item);
        }
        
        mgTime = (System.nanoTime() - mgTime) / 1_000_000;
        long mgMemory = k * 50; // Rough estimate: 50 bytes per entry
        
        System.out.printf("Processing %,d items (1000 unique):%n", numItems);
        System.out.println();
        
        System.out.printf("Exact (HashMap):%n");
        System.out.printf("  Entries: %,d%n", exactMap.size());
        System.out.printf("  Time: %d ms%n", exactTime);
        System.out.printf("  Memory: %.2f KB%n", exactMemory / 1024.0);
        System.out.println();
        
        System.out.printf("Misra-Gries (k=%d):%n", k);
        System.out.printf("  Entries tracked: %d%n", k);
        System.out.printf("  Time: %d ms%n", mgTime);
        System.out.printf("  Memory: %.2f KB%n", mgMemory / 1024.0);
        System.out.println();
        
        System.out.printf("Savings:%n");
        System.out.printf("  Memory: %.0fx smaller%n", exactMemory / (double) mgMemory);
        System.out.printf("  Space: O(%d) vs O(%d)%n", k, exactMap.size());
        System.out.println();
    }
    
    private static long estimateSetMemory(Set<?> set) {
        return set.size() * 50L; // Rough estimate: 50 bytes per entry
    }
    
    private static long estimateMapMemory(Map<?, ?> map) {
        return map.size() * 100L; // Rough estimate: 100 bytes per entry
    }
}
```

---

## Summary

### Algorithms Covered

1. ✅ **Reservoir Sampling**
   - Uniform random sampling from streams
   - Weighted sampling variant
   - Applications: Log sampling, data subset selection

2. ✅ **Flajolet-Martin**
   - Distinct count estimation
   - O(log n) space complexity
   - Applications: Unique visitor counting

3. ✅ **Misra-Gries**
   - Frequent items (top-K heavy hitters)
   - O(k) space complexity
   - Applications: Trending topics, anomaly detection

### Performance Summary

| Algorithm | Space | Time (per item) | Accuracy |
|-----------|-------|-----------------|----------|
| Reservoir Sampling | O(k) | O(1) | Exact |
| Flajolet-Martin | O(log n) | O(1) | ~20% error |
| Misra-Gries | O(k) | O(k) | Guaranteed top-k |

### When to Use

**Reservoir Sampling:**
- Need uniform random sample
- Data size unknown in advance
- Want to debug with representative sample

**Flajolet-Martin:**
- Count unique items
- Can tolerate 20% error
- Upgrade to HyperLogLog for 2% error

**Misra-Gries:**
- Find frequent items (top-K)
- Guaranteed to find items with frequency > n/(k+1)
- Real-time analytics dashboards

### Production Considerations

✅ **Choose the right algorithm:**
- Exact counts needed? Use HashMap/HashSet
- Large data + approximate OK? Use streaming algorithms

✅ **Tune parameters:**
- Reservoir size: Larger = more representative sample
- Flajolet-Martin bitmaps: More = better accuracy
- Misra-Gries k: Should be ~2-3x expected heavy hitters

✅ **Monitor accuracy:**
- Track actual vs estimated values in production
- Alert if error exceeds threshold

✅ **Combine with exact methods:**
- Use streaming for real-time dashboards
- Use exact for billing/compliance

---

**End of Streaming Algorithms Module**
