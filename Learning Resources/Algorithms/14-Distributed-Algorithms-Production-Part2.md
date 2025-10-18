# Distributed Algorithms - Production Grade (Part 2)

**Continuation from Part 1**

---

## 3. Probabilistic Data Structures

### Overview

Probabilistic data structures trade exactness for space efficiency. They're essential for big data systems where storing everything is impractical.

**Key Trade-off:** Accept small false positive rate for massive space savings (often 100x-1000x smaller)

**Used By:**
- Google BigTable: Bloom filters to avoid disk reads
- Apache Cassandra: Bloom filters per SSTable
- Redis: HyperLogLog for counting unique visitors
- Apache Spark: Approximate distinct count

---

## 3.1. Bloom Filter

### The Problem

**Scenario:** Web crawler needs to check if URL has been crawled before.

```
Traditional approach (HashSet):
- 1 billion URLs
- Average URL length: 100 bytes
- Memory needed: 100 GB

Bloom Filter approach:
- 1 billion URLs
- False positive rate: 1%
- Memory needed: ~1.2 GB (83x smaller!)
```

**Key Insight:** We don't need to store the actual URLs, just answer "definitely not in set" or "probably in set"

---

### Algorithm Explanation

**Bloom Filter** = Bit array + Multiple hash functions

```
Visualization:

Bit array (size m = 20):
[0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0]

Add "hello" with 3 hash functions:
h1("hello") = 3  →  [0][0][0][1][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0]
h2("hello") = 7  →  [0][0][0][1][0][0][0][1][0][0][0][0][0][0][0][0][0][0][0][0]
h3("hello") = 15 →  [0][0][0][1][0][0][0][1][0][0][0][0][0][0][0][1][0][0][0][0]

Add "world":
h1("world") = 5  →  [0][0][0][1][0][1][0][1][0][0][0][0][0][0][0][1][0][0][0][0]
h2("world") = 11 →  [0][0][0][1][0][1][0][1][0][0][0][1][0][0][0][1][0][0][0][0]
h3("world") = 15 →  [0][0][0][1][0][1][0][1][0][0][0][1][0][0][0][1][0][0][0][0]

Check "hello":
- h1("hello") = 3  → bit[3] = 1 ✓
- h2("hello") = 7  → bit[7] = 1 ✓
- h3("hello") = 15 → bit[15] = 1 ✓
→ Probably in set

Check "foo" (not added):
- h1("foo") = 2  → bit[2] = 0 ✗
→ Definitely NOT in set

Check "bar" (false positive):
- h1("bar") = 5  → bit[5] = 1 ✓
- h2("bar") = 7  → bit[7] = 1 ✓
- h3("bar") = 15 → bit[15] = 1 ✓
→ Probably in set (FALSE POSITIVE!)
```

**Key Properties:**
- No false negatives (if returns "no", definitely not in set)
- Possible false positives (if returns "yes", might not be in set)
- Can't remove items (would cause false negatives)

---

### Production-Grade Implementation (Java)

```java
package com.dateng.probabilistic;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.BitSet;

/**
 * Production-grade Bloom Filter implementation
 * 
 * Features:
 * - Configurable false positive rate
 * - Optimal hash function count
 * - Memory-efficient BitSet
 * - Thread-safe operations
 * 
 * Use Cases:
 * - Web crawler URL deduplication
 * - Database query cache (avoid expensive lookups)
 * - Network packet filtering
 * 
 * @author Principal Data Engineer
 */
public class BloomFilter<T> {
    
    private final BitSet bitSet;           // Bit array
    private final int bitSetSize;          // Size of bit array (m)
    private final int numHashFunctions;    // Number of hash functions (k)
    private final MessageDigest md5;
    private long insertCount;              // Number of items inserted
    
    /**
     * Constructor with automatic sizing
     * 
     * @param expectedInsertions Expected number of items to insert (n)
     * @param falsePositiveRate Desired false positive rate (e.g., 0.01 for 1%)
     */
    public BloomFilter(long expectedInsertions, double falsePositiveRate) {
        // Calculate optimal bit array size: m = -n*ln(p) / (ln(2))^2
        this.bitSetSize = optimalBitSetSize(expectedInsertions, falsePositiveRate);
        
        // Calculate optimal number of hash functions: k = m/n * ln(2)
        this.numHashFunctions = optimalNumHashFunctions(expectedInsertions, bitSetSize);
        
        this.bitSet = new BitSet(bitSetSize);
        this.insertCount = 0;
        
        try {
            this.md5 = MessageDigest.getInstance("MD5");
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("MD5 not available", e);
        }
        
        System.out.printf("[BloomFilter] Created with %d bits, %d hash functions%n", 
                          bitSetSize, numHashFunctions);
        System.out.printf("[BloomFilter] Expected insertions: %d, Target FP rate: %.4f%%%n", 
                          expectedInsertions, falsePositiveRate * 100);
    }
    
    /**
     * Constructor with explicit parameters
     * 
     * @param bitSetSize Size of bit array
     * @param numHashFunctions Number of hash functions
     */
    public BloomFilter(int bitSetSize, int numHashFunctions) {
        this.bitSetSize = bitSetSize;
        this.numHashFunctions = numHashFunctions;
        this.bitSet = new BitSet(bitSetSize);
        this.insertCount = 0;
        
        try {
            this.md5 = MessageDigest.getInstance("MD5");
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("MD5 not available", e);
        }
    }
    
    /**
     * Add an item to the Bloom filter
     * 
     * Time Complexity: O(k) where k = number of hash functions
     * Space Complexity: O(1)
     * 
     * @param item Item to add
     */
    public synchronized void add(T item) {
        int[] hashes = getHashes(item);
        
        for (int hash : hashes) {
            bitSet.set(hash);
        }
        
        insertCount++;
    }
    
    /**
     * Check if item might be in the set
     * 
     * Time Complexity: O(k)
     * 
     * @param item Item to check
     * @return true if probably in set, false if definitely not in set
     */
    public synchronized boolean mightContain(T item) {
        int[] hashes = getHashes(item);
        
        for (int hash : hashes) {
            if (!bitSet.get(hash)) {
                return false; // Definitely not in set
            }
        }
        
        return true; // Probably in set
    }
    
    /**
     * Generate k hash values for an item
     * 
     * Uses double hashing technique:
     * hash_i = (hash1 + i * hash2) % m
     * 
     * @param item Item to hash
     * @return Array of k hash values
     */
    private int[] getHashes(T item) {
        int[] hashes = new int[numHashFunctions];
        
        // Get two base hash values from MD5
        byte[] digest = md5.digest(item.toString().getBytes(StandardCharsets.UTF_8));
        
        long hash1 = bytesToLong(digest, 0);
        long hash2 = bytesToLong(digest, 8);
        
        // Generate k hash values using double hashing
        for (int i = 0; i < numHashFunctions; i++) {
            long combinedHash = hash1 + (i * hash2);
            
            // Ensure positive and within bitSet size
            hashes[i] = (int) ((combinedHash & Long.MAX_VALUE) % bitSetSize);
        }
        
        return hashes;
    }
    
    /**
     * Convert 8 bytes to long
     */
    private long bytesToLong(byte[] bytes, int offset) {
        long result = 0;
        for (int i = 0; i < 8 && offset + i < bytes.length; i++) {
            result = (result << 8) | (bytes[offset + i] & 0xFF);
        }
        return result;
    }
    
    /**
     * Calculate optimal bit array size
     * Formula: m = -n*ln(p) / (ln(2))^2
     */
    private static int optimalBitSetSize(long expectedInsertions, double falsePositiveRate) {
        double bits = -expectedInsertions * Math.log(falsePositiveRate) / Math.pow(Math.log(2), 2);
        return (int) Math.ceil(bits);
    }
    
    /**
     * Calculate optimal number of hash functions
     * Formula: k = m/n * ln(2)
     */
    private static int optimalNumHashFunctions(long expectedInsertions, int bitSetSize) {
        double k = (bitSetSize / (double) expectedInsertions) * Math.log(2);
        return Math.max(1, (int) Math.round(k));
    }
    
    /**
     * Get current false positive probability
     * Formula: p = (1 - e^(-kn/m))^k
     */
    public synchronized double getCurrentFalsePositiveProbability() {
        double exponent = -numHashFunctions * insertCount / (double) bitSetSize;
        double base = 1 - Math.exp(exponent);
        return Math.pow(base, numHashFunctions);
    }
    
    /**
     * Get memory usage in bytes
     */
    public long getMemoryUsageBytes() {
        return (long) Math.ceil(bitSetSize / 8.0);
    }
    
    /**
     * Get fill ratio (percentage of bits set)
     */
    public synchronized double getFillRatio() {
        return bitSet.cardinality() / (double) bitSetSize;
    }
    
    /**
     * Clear the filter
     */
    public synchronized void clear() {
        bitSet.clear();
        insertCount = 0;
    }
    
    /**
     * Get statistics
     */
    public synchronized Stats getStats() {
        return new Stats(
            bitSetSize,
            numHashFunctions,
            insertCount,
            bitSet.cardinality(),
            getFillRatio(),
            getCurrentFalsePositiveProbability(),
            getMemoryUsageBytes()
        );
    }
    
    /**
     * Statistics class
     */
    public static class Stats {
        public final int bitSetSize;
        public final int numHashFunctions;
        public final long insertCount;
        public final int bitsSet;
        public final double fillRatio;
        public final double falsePositiveProbability;
        public final long memoryBytes;
        
        Stats(int bitSetSize, int numHashFunctions, long insertCount, 
              int bitsSet, double fillRatio, double falsePositiveProbability,
              long memoryBytes) {
            this.bitSetSize = bitSetSize;
            this.numHashFunctions = numHashFunctions;
            this.insertCount = insertCount;
            this.bitsSet = bitsSet;
            this.fillRatio = fillRatio;
            this.falsePositiveProbability = falsePositiveProbability;
            this.memoryBytes = memoryBytes;
        }
        
        @Override
        public String toString() {
            return String.format(
                "BloomFilter Stats:\n" +
                "  Bit array size: %d bits (%.2f KB)\n" +
                "  Hash functions: %d\n" +
                "  Items inserted: %d\n" +
                "  Bits set: %d (%.2f%% full)\n" +
                "  Current FP probability: %.6f%%\n" +
                "  Memory usage: %d bytes (%.2f KB)",
                bitSetSize,
                bitSetSize / 8192.0,
                numHashFunctions,
                insertCount,
                bitsSet,
                fillRatio * 100,
                falsePositiveProbability * 100,
                memoryBytes,
                memoryBytes / 1024.0
            );
        }
    }
}
```

---

### Real-World Use Case: Web Crawler

```java
package com.dateng.probabilistic;

import java.util.*;
import java.util.concurrent.*;

/**
 * Web crawler using Bloom Filter for URL deduplication
 * 
 * Prevents crawling the same URL twice
 * Memory efficient: 1B URLs in ~1.2 GB
 */
public class WebCrawler {
    
    private final BloomFilter<String> visitedUrls;
    private final Queue<String> urlQueue;
    private final ExecutorService crawler;
    private final Set<String> actualVisitedForValidation; // For testing
    private long urlsCrawled = 0;
    private long duplicatesAvoided = 0;
    
    /**
     * Constructor
     * 
     * @param expectedUrls Expected number of URLs to crawl
     * @param falsePositiveRate Acceptable false positive rate
     */
    public WebCrawler(long expectedUrls, double falsePositiveRate) {
        this.visitedUrls = new BloomFilter<>(expectedUrls, falsePositiveRate);
        this.urlQueue = new ConcurrentLinkedQueue<>();
        this.crawler = Executors.newFixedThreadPool(10);
        this.actualVisitedForValidation = ConcurrentHashMap.newKeySet();
        
        System.out.printf("[WebCrawler] Initialized for %d URLs, FP rate: %.4f%%%n", 
                          expectedUrls, falsePositiveRate * 100);
    }
    
    /**
     * Add seed URLs to start crawling
     */
    public void addSeedUrls(List<String> seedUrls) {
        urlQueue.addAll(seedUrls);
        System.out.printf("[WebCrawler] Added %d seed URLs%n", seedUrls.size());
    }
    
    /**
     * Crawl a single URL
     */
    private void crawlUrl(String url) {
        // Check if URL was likely visited before
        if (visitedUrls.mightContain(url)) {
            duplicatesAvoided++;
            
            // Validate against actual set (for testing)
            if (!actualVisitedForValidation.contains(url)) {
                System.out.printf("[FALSE POSITIVE] URL marked as visited but wasn't: %s%n", url);
            }
            
            return;
        }
        
        // Mark URL as visited
        visitedUrls.add(url);
        actualVisitedForValidation.add(url);
        urlsCrawled++;
        
        // Simulate crawling (fetch page, extract links, etc.)
        System.out.printf("[CRAWL] %s%n", url);
        
        // Extract and queue new URLs (simulated)
        List<String> newUrls = extractLinks(url);
        urlQueue.addAll(newUrls);
    }
    
    /**
     * Simulate extracting links from a page
     */
    private List<String> extractLinks(String url) {
        List<String> links = new ArrayList<>();
        
        // Simulate finding 5-10 new URLs per page
        int numLinks = ThreadLocalRandom.current().nextInt(5, 11);
        for (int i = 0; i < numLinks; i++) {
            links.add(url + "/link" + i);
        }
        
        return links;
    }
    
    /**
     * Start crawling (up to maxUrls)
     */
    public void crawl(int maxUrls) {
        System.out.printf("[WebCrawler] Starting crawl (max %d URLs)%n", maxUrls);
        
        while (urlsCrawled < maxUrls && !urlQueue.isEmpty()) {
            String url = urlQueue.poll();
            if (url != null) {
                crawlUrl(url);
            }
        }
        
        printStats();
    }
    
    /**
     * Print crawler statistics
     */
    public void printStats() {
        System.out.println("\n=== Crawler Statistics ===");
        System.out.printf("URLs crawled: %d%n", urlsCrawled);
        System.out.printf("Duplicates avoided: %d%n", duplicatesAvoided);
        System.out.printf("URLs in queue: %d%n", urlQueue.size());
        
        System.out.println("\n" + visitedUrls.getStats());
        
        // Calculate space savings
        long hashSetMemory = urlsCrawled * 100; // Assume 100 bytes per URL
        long bloomFilterMemory = visitedUrls.getMemoryUsageBytes();
        double savings = (1 - bloomFilterMemory / (double) hashSetMemory) * 100;
        
        System.out.printf("\nMemory comparison:%n");
        System.out.printf("  HashSet: %.2f MB%n", hashSetMemory / 1_000_000.0);
        System.out.printf("  Bloom Filter: %.2f MB%n", bloomFilterMemory / 1_000_000.0);
        System.out.printf("  Savings: %.2f%%%n", savings);
    }
    
    /**
     * Shutdown crawler
     */
    public void shutdown() {
        crawler.shutdown();
    }
}
```

---

### Bloom Filter in Apache Cassandra

Cassandra uses Bloom filters to optimize reads:

```
Read path without Bloom filter:
1. Check memtable (memory) - not found
2. Check SSTable 1 (disk read) - not found
3. Check SSTable 2 (disk read) - not found
4. Check SSTable 3 (disk read) - not found
5. Return "not found"
→ 3 expensive disk reads for non-existent key!

Read path with Bloom filter:
1. Check memtable (memory) - not found
2. Check SSTable 1 Bloom filter (memory) - definitely not present → SKIP
3. Check SSTable 2 Bloom filter (memory) - definitely not present → SKIP
4. Check SSTable 3 Bloom filter (memory) - might be present → check disk - not found
5. Return "not found"
→ Only 1 disk read!

Space cost:
- SSTable size: 100 GB
- Bloom filter: 125 MB (0.125% overhead)
- Disk reads saved: 60-70% for non-existent keys
```

**Configuration in Cassandra:**
```sql
CREATE TABLE users (
    user_id uuid PRIMARY KEY,
    name text,
    email text
) WITH bloom_filter_fp_chance = 0.01;  -- 1% false positive rate
```

---

## 3.2. Count-Min Sketch

### The Problem

**Scenario:** Track frequency of events in a stream (e.g., count requests per IP address).

```
Traditional approach (HashMap):
- 1 million unique IPs
- Each counter: 8 bytes
- Memory: 8 MB

Count-Min Sketch:
- Memory: 100 KB (80x smaller!)
- Accuracy: Errors are always overestimates
```

**Applications:**
- Network traffic monitoring
- Top-K frequent items
- Heavy hitters detection
- Query frequency in databases

---

### Algorithm Explanation

Count-Min Sketch = 2D array + Multiple hash functions

```
Visualization:

2D array (width = 10, depth = 3):

   0  1  2  3  4  5  6  7  8  9
0 [0][0][0][0][0][0][0][0][0][0]  ← hash function h1
1 [0][0][0][0][0][0][0][0][0][0]  ← hash function h2
2 [0][0][0][0][0][0][0][0][0][0]  ← hash function h3

Add "IP_A" (count = 1):
h1("IP_A") = 2  →  0[2]++
h2("IP_A") = 5  →  1[5]++
h3("IP_A") = 8  →  2[8]++

   0  1  2  3  4  5  6  7  8  9
0 [0][0][1][0][0][0][0][0][0][0]
1 [0][0][0][0][0][1][0][0][0][0]
2 [0][0][0][0][0][0][0][0][1][0]

Add "IP_B" (count = 1):
h1("IP_B") = 2  →  0[2]++  (collision!)
h2("IP_B") = 7  →  1[7]++
h3("IP_B") = 4  →  2[4]++

   0  1  2  3  4  5  6  7  8  9
0 [0][0][2][0][0][0][0][0][0][0]
1 [0][0][0][0][0][1][0][1][0][0]
2 [0][0][0][0][1][0][0][0][1][0]

Query count("IP_A"):
= min(0[2], 1[5], 2[8])
= min(2, 1, 1)
= 1 (correct!)

Query count("IP_B"):
= min(0[2], 1[7], 2[4])
= min(2, 1, 1)
= 1 (correct!)
```

**Key Property:** Estimate is always ≥ actual count (overestimate due to collisions)

---

### Production-Grade Implementation (Java)

```java
package com.dateng.probabilistic;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

/**
 * Count-Min Sketch for frequency estimation
 * 
 * Features:
 * - Space-efficient frequency counting
 * - Configurable accuracy
 * - Handles high-cardinality streams
 * - Never underestimates (only overestimates)
 * 
 * Use Cases:
 * - Network traffic analysis
 * - Top-K heavy hitters
 * - Query frequency tracking
 * 
 * @author Principal Data Engineer
 */
public class CountMinSketch {
    
    private final int width;    // Number of counters per row (w)
    private final int depth;    // Number of rows (d)
    private final long[][] counters;
    private final MessageDigest md5;
    private long totalCount;
    
    /**
     * Constructor with automatic sizing
     * 
     * @param epsilon Error rate (e.g., 0.01 for 1% error)
     * @param delta Confidence (e.g., 0.99 for 99% confidence)
     */
    public CountMinSketch(double epsilon, double delta) {
        // Width: w = e / epsilon
        this.width = (int) Math.ceil(Math.E / epsilon);
        
        // Depth: d = ln(1/delta)
        this.depth = (int) Math.ceil(Math.log(1.0 / delta));
        
        this.counters = new long[depth][width];
        this.totalCount = 0;
        
        try {
            this.md5 = MessageDigest.getInstance("MD5");
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("MD5 not available", e);
        }
        
        System.out.printf("[CountMinSketch] Created with %d x %d = %d counters%n", 
                          depth, width, depth * width);
        System.out.printf("[CountMinSketch] Error: %.2f%%, Confidence: %.2f%%%n", 
                          epsilon * 100, delta * 100);
    }
    
    /**
     * Constructor with explicit parameters
     */
    public CountMinSketch(int width, int depth) {
        this.width = width;
        this.depth = depth;
        this.counters = new long[depth][width];
        this.totalCount = 0;
        
        try {
            this.md5 = MessageDigest.getInstance("MD5");
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("MD5 not available", e);
        }
    }
    
    /**
     * Add an item with count = 1
     * 
     * Time Complexity: O(d)
     * 
     * @param item Item to add
     */
    public synchronized void add(String item) {
        add(item, 1);
    }
    
    /**
     * Add an item with custom count
     * 
     * @param item Item to add
     * @param count Count to add
     */
    public synchronized void add(String item, long count) {
        int[] hashes = getHashes(item);
        
        for (int i = 0; i < depth; i++) {
            counters[i][hashes[i]] += count;
        }
        
        totalCount += count;
    }
    
    /**
     * Estimate frequency of an item
     * 
     * Returns the minimum count across all hash functions
     * 
     * Time Complexity: O(d)
     * 
     * @param item Item to query
     * @return Estimated frequency (always ≥ actual frequency)
     */
    public synchronized long estimateCount(String item) {
        int[] hashes = getHashes(item);
        
        long minCount = Long.MAX_VALUE;
        
        for (int i = 0; i < depth; i++) {
            minCount = Math.min(minCount, counters[i][hashes[i]]);
        }
        
        return minCount;
    }
    
    /**
     * Generate hash values for item
     */
    private int[] getHashes(String item) {
        int[] hashes = new int[depth];
        
        byte[] digest = md5.digest(item.getBytes(StandardCharsets.UTF_8));
        
        long hash1 = bytesToLong(digest, 0);
        long hash2 = bytesToLong(digest, 8);
        
        for (int i = 0; i < depth; i++) {
            long combinedHash = hash1 + (i * hash2);
            hashes[i] = (int) ((combinedHash & Long.MAX_VALUE) % width);
        }
        
        return hashes;
    }
    
    private long bytesToLong(byte[] bytes, int offset) {
        long result = 0;
        for (int i = 0; i < 8 && offset + i < bytes.length; i++) {
            result = (result << 8) | (bytes[offset + i] & 0xFF);
        }
        return result;
    }
    
    /**
     * Get total count of all items
     */
    public synchronized long getTotalCount() {
        return totalCount;
    }
    
    /**
     * Get memory usage in bytes
     */
    public long getMemoryUsageBytes() {
        return (long) depth * width * 8; // 8 bytes per long
    }
    
    /**
     * Clear all counters
     */
    public synchronized void clear() {
        for (int i = 0; i < depth; i++) {
            for (int j = 0; j < width; j++) {
                counters[i][j] = 0;
            }
        }
        totalCount = 0;
    }
    
    /**
     * Get statistics
     */
    public synchronized Stats getStats() {
        return new Stats(width, depth, totalCount, getMemoryUsageBytes());
    }
    
    public static class Stats {
        public final int width;
        public final int depth;
        public final long totalCount;
        public final long memoryBytes;
        
        Stats(int width, int depth, long totalCount, long memoryBytes) {
            this.width = width;
            this.depth = depth;
            this.totalCount = totalCount;
            this.memoryBytes = memoryBytes;
        }
        
        @Override
        public String toString() {
            return String.format(
                "CountMinSketch Stats:\n" +
                "  Dimensions: %d x %d = %d counters\n" +
                "  Total count: %d\n" +
                "  Memory usage: %d bytes (%.2f KB)",
                depth,
                width,
                depth * width,
                totalCount,
                memoryBytes,
                memoryBytes / 1024.0
            );
        }
    }
}
```

---

### Use Case: Top-K Heavy Hitters

```java
package com.dateng.probabilistic;

import java.util.*;

/**
 * Find top-K most frequent items using Count-Min Sketch + Min Heap
 * 
 * Space: O(K) instead of O(N) for exact solution
 */
public class TopKHeavyHitters {
    
    private final CountMinSketch cms;
    private final PriorityQueue<ItemCount> minHeap;
    private final Map<String, Long> topKMap;
    private final int k;
    
    public TopKHeavyHitters(int k, double epsilon, double delta) {
        this.k = k;
        this.cms = new CountMinSketch(epsilon, delta);
        this.minHeap = new PriorityQueue<>(k, Comparator.comparingLong(a -> a.count));
        this.topKMap = new HashMap<>();
    }
    
    /**
     * Process an item from the stream
     */
    public void add(String item) {
        // Update Count-Min Sketch
        cms.add(item);
        
        // Get estimated count
        long count = cms.estimateCount(item);
        
        // Update top-K
        if (topKMap.containsKey(item)) {
            // Update existing item in heap
            updateTopK(item, count);
        } else if (minHeap.size() < k) {
            // Heap not full, add item
            ItemCount ic = new ItemCount(item, count);
            minHeap.offer(ic);
            topKMap.put(item, count);
        } else if (count > minHeap.peek().count) {
            // Replace minimum item in heap
            ItemCount removed = minHeap.poll();
            topKMap.remove(removed.item);
            
            ItemCount ic = new ItemCount(item, count);
            minHeap.offer(ic);
            topKMap.put(item, count);
        }
    }
    
    private void updateTopK(String item, long count) {
        // Remove old entry
        minHeap.removeIf(ic -> ic.item.equals(item));
        
        // Add updated entry
        minHeap.offer(new ItemCount(item, count));
        topKMap.put(item, count);
    }
    
    /**
     * Get top-K items
     */
    public List<ItemCount> getTopK() {
        List<ItemCount> topK = new ArrayList<>(minHeap);
        topK.sort(Comparator.comparingLong((ItemCount ic) -> ic.count).reversed());
        return topK;
    }
    
    /**
     * Print top-K
     */
    public void printTopK() {
        System.out.println("\n=== Top " + k + " Heavy Hitters ===");
        
        List<ItemCount> topK = getTopK();
        
        for (int i = 0; i < topK.size(); i++) {
            ItemCount ic = topK.get(i);
            System.out.printf("%d. %s: %d%n", i + 1, ic.item, ic.count);
        }
        
        System.out.println("\n" + cms.getStats());
    }
    
    static class ItemCount {
        final String item;
        final long count;
        
        ItemCount(String item, long count) {
            this.item = item;
            this.count = count;
        }
    }
}
```

---

## 3.3. HyperLogLog

### The Problem

**Scenario:** Count distinct users visiting your website.

```
Traditional approach (HashSet):
- 1 billion unique users
- Each user ID: 16 bytes (UUID)
- Memory: 16 GB

HyperLogLog:
- 1 billion unique users
- Error rate: ~2%
- Memory: 12 KB (1.3 million times smaller!)
```

**Used By:**
- Redis: PFADD, PFCOUNT commands
- Google Analytics: Unique visitor counting
- BigQuery: APPROX_COUNT_DISTINCT()
- Druid: Approximate distinct count aggregation

---

### Algorithm Explanation

HyperLogLog uses the observation that if you hash values uniformly, the maximum number of leading zeros is related to the cardinality.

```
Example with 4-bit hashes:

Items: [A, B, C, D, E]

Hash(A) = 0101 → 0 leading zeros
Hash(B) = 0011 → 0 leading zeros
Hash(C) = 0001 → 0 leading zeros
Hash(D) = 1000 → 3 leading zeros (rare!)
Hash(E) = 0110 → 0 leading zeros

Max leading zeros = 3
Estimated cardinality ≈ 2^3 = 8

Actual cardinality = 5
Error due to randomness

To improve accuracy:
- Use multiple buckets (like Count-Min Sketch)
- Take harmonic mean instead of simple mean
```

---

### Production Implementation (Java)

```java
package com.dateng.probabilistic;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

/**
 * HyperLogLog for cardinality estimation
 * 
 * Features:
 * - Extremely space-efficient (KB for billions of items)
 * - Configurable precision
 * - Error rate: 1.04 / sqrt(m) where m = number of buckets
 * 
 * Use Cases:
 * - Unique visitor counting
 * - Distinct value estimation in big data
 * - Database query optimization
 * 
 * @author Principal Data Engineer
 */
public class HyperLogLog {
    
    private final int precision;        // Number of bits for bucket index (p)
    private final int numBuckets;       // Number of buckets (m = 2^p)
    private final byte[] buckets;       // Max leading zeros per bucket
    private final double alphaMM;       // Bias correction constant
    private final MessageDigest md5;
    
    /**
     * Constructor
     * 
     * @param precision Number of bits for bucket index (4-16)
     *                  Higher = more accurate but more memory
     *                  Recommended: 14 (16KB memory, 0.81% error)
     */
    public HyperLogLog(int precision) {
        if (precision < 4 || precision > 16) {
            throw new IllegalArgumentException("Precision must be between 4 and 16");
        }
        
        this.precision = precision;
        this.numBuckets = 1 << precision; // 2^p
        this.buckets = new byte[numBuckets];
        this.alphaMM = getAlphaMM(numBuckets);
        
        try {
            this.md5 = MessageDigest.getInstance("MD5");
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("MD5 not available", e);
        }
        
        System.out.printf("[HyperLogLog] Created with precision=%d, buckets=%d%n", 
                          precision, numBuckets);
        System.out.printf("[HyperLogLog] Estimated error rate: %.4f%%%n", 
                          getExpectedErrorRate() * 100);
    }
    
    /**
     * Add an item
     * 
     * Time Complexity: O(1)
     * 
     * @param item Item to add
     */
    public void add(String item) {
        // Hash the item
        long hash = hash(item);
        
        // Use first p bits as bucket index
        int bucketIdx = (int) (hash >>> (64 - precision));
        
        // Count leading zeros in remaining bits + 1
        long w = hash << precision;
        int leadingZeros = Long.numberOfLeadingZeros(w) + 1;
        
        // Update bucket with maximum leading zeros seen
        if (leadingZeros > buckets[bucketIdx]) {
            buckets[bucketIdx] = (byte) leadingZeros;
        }
    }
    
    /**
     * Estimate cardinality
     * 
     * Time Complexity: O(m) where m = number of buckets
     * 
     * @return Estimated number of distinct items
     */
    public long estimateCardinality() {
        // Calculate harmonic mean
        double sum = 0;
        int zeroCount = 0;
        
        for (int i = 0; i < numBuckets; i++) {
            sum += Math.pow(2, -buckets[i]);
            if (buckets[i] == 0) {
                zeroCount++;
            }
        }
        
        double rawEstimate = alphaMM / sum;
        
        // Apply bias correction for small cardinalities
        if (rawEstimate <= 2.5 * numBuckets) {
            if (zeroCount > 0) {
                // Small range correction
                return Math.round(numBuckets * Math.log(numBuckets / (double) zeroCount));
            }
        }
        
        // Apply correction for large cardinalities
        if (rawEstimate > (1.0 / 30.0) * (1L << 32)) {
            return Math.round(-1L * (1L << 32) * Math.log(1 - rawEstimate / (1L << 32)));
        }
        
        return Math.round(rawEstimate);
    }
    
    /**
     * Merge with another HyperLogLog
     * Used for distributed counting
     */
    public void merge(HyperLogLog other) {
        if (this.precision != other.precision) {
            throw new IllegalArgumentException("Cannot merge HLLs with different precision");
        }
        
        for (int i = 0; i < numBuckets; i++) {
            if (other.buckets[i] > this.buckets[i]) {
                this.buckets[i] = other.buckets[i];
            }
        }
    }
    
    /**
     * Hash function
     */
    private long hash(String item) {
        byte[] digest = md5.digest(item.getBytes(StandardCharsets.UTF_8));
        
        long hash = 0;
        for (int i = 0; i < 8; i++) {
            hash = (hash << 8) | (digest[i] & 0xFF);
        }
        
        return hash;
    }
    
    /**
     * Get bias correction constant alpha_m
     */
    private double getAlphaMM(int m) {
        switch (m) {
            case 16:
                return 0.673 * m * m;
            case 32:
                return 0.697 * m * m;
            case 64:
                return 0.709 * m * m;
            default:
                return (0.7213 / (1 + 1.079 / m)) * m * m;
        }
    }
    
    /**
     * Get expected error rate
     * Formula: 1.04 / sqrt(m)
     */
    public double getExpectedErrorRate() {
        return 1.04 / Math.sqrt(numBuckets);
    }
    
    /**
     * Get memory usage in bytes
     */
    public int getMemoryUsageBytes() {
        return numBuckets; // 1 byte per bucket
    }
    
    /**
     * Clear all buckets
     */
    public void clear() {
        for (int i = 0; i < numBuckets; i++) {
            buckets[i] = 0;
        }
    }
    
    /**
     * Get statistics
     */
    public Stats getStats() {
        return new Stats(
            precision,
            numBuckets,
            estimateCardinality(),
            getExpectedErrorRate(),
            getMemoryUsageBytes()
        );
    }
    
    public static class Stats {
        public final int precision;
        public final int numBuckets;
        public final long estimatedCardinality;
        public final double expectedErrorRate;
        public final int memoryBytes;
        
        Stats(int precision, int numBuckets, long estimatedCardinality,
              double expectedErrorRate, int memoryBytes) {
            this.precision = precision;
            this.numBuckets = numBuckets;
            this.estimatedCardinality = estimatedCardinality;
            this.expectedErrorRate = expectedErrorRate;
            this.memoryBytes = memoryBytes;
        }
        
        @Override
        public String toString() {
            return String.format(
                "HyperLogLog Stats:\n" +
                "  Precision: %d\n" +
                "  Buckets: %d\n" +
                "  Estimated cardinality: %d\n" +
                "  Expected error rate: %.4f%%\n" +
                "  Memory usage: %d bytes (%.2f KB)",
                precision,
                numBuckets,
                estimatedCardinality,
                expectedErrorRate * 100,
                memoryBytes,
                memoryBytes / 1024.0
            );
        }
    }
}
```

---

### Comparison: Exact vs Approximate

```java
package com.dateng.probabilistic;

import java.util.*;

/**
 * Compare exact counting (HashSet) vs approximate counting (HyperLogLog)
 */
public class CardinalityComparison {
    
    public static void main(String[] args) {
        System.out.println("=== Exact vs Approximate Cardinality ===\n");
        
        // Test with increasing cardinalities
        int[] testSizes = {1_000, 10_000, 100_000, 1_000_000, 10_000_000};
        
        for (int size : testSizes) {
            compareCardinality(size);
        }
    }
    
    private static void compareCardinality(int numItems) {
        System.out.printf("Testing with %,d unique items:%n", numItems);
        
        // Exact counting with HashSet
        Set<String> exactSet = new HashSet<>();
        long exactMemoryBefore = getMemoryUsage();
        long exactTimeStart = System.nanoTime();
        
        for (int i = 0; i < numItems; i++) {
            exactSet.add("user_" + i);
        }
        
        long exactTimeMs = (System.nanoTime() - exactTimeStart) / 1_000_000;
        long exactMemoryAfter = getMemoryUsage();
        long exactMemory = exactMemoryAfter - exactMemoryBefore;
        int exactCount = exactSet.size();
        
        // Approximate counting with HyperLogLog
        HyperLogLog hll = new HyperLogLog(14); // precision=14
        long hllTimeStart = System.nanoTime();
        
        for (int i = 0; i < numItems; i++) {
            hll.add("user_" + i);
        }
        
        long hllTimeMs = (System.nanoTime() - hllTimeStart) / 1_000_000;
        long hllCount = hll.estimateCardinality();
        int hllMemory = hll.getMemoryUsageBytes();
        
        // Calculate error
        double error = Math.abs(hllCount - exactCount) / (double) exactCount * 100;
        
        // Print comparison
        System.out.printf("  Exact (HashSet):%n");
        System.out.printf("    Count: %,d%n", exactCount);
        System.out.printf("    Memory: %.2f MB%n", exactMemory / 1_000_000.0);
        System.out.printf("    Time: %d ms%n", exactTimeMs);
        
        System.out.printf("  Approximate (HyperLogLog):%n");
        System.out.printf("    Count: %,d%n", hllCount);
        System.out.printf("    Memory: %.2f KB%n", hllMemory / 1024.0);
        System.out.printf("    Time: %d ms%n", hllTimeMs);
        System.out.printf("    Error: %.4f%%%n", error);
        
        System.out.printf("  Savings:%n");
        System.out.printf("    Memory: %.1fx smaller%n", exactMemory / (double) hllMemory);
        System.out.printf("    Time: %.1fx faster%n", exactTimeMs / (double) hllTimeMs);
        
        System.out.println();
    }
    
    private static long getMemoryUsage() {
        Runtime runtime = Runtime.getRuntime();
        return runtime.totalMemory() - runtime.freeMemory();
    }
}
```

---

**[To be continued with External Sort, Distributed Aggregation, and Benchmark tests in the final sections...]**

### Summary So Far

We've covered:
1. ✅ **Consistent Hashing** - Distributed caching and load balancing
2. ✅ **Rate Limiting** - Token bucket, sliding window algorithms
3. ✅ **Bloom Filter** - Space-efficient set membership
4. ✅ **Count-Min Sketch** - Frequency estimation
5. ✅ **HyperLogLog** - Cardinality estimation

**Remaining in Part 3:**
- External Sort for large-scale data
- Distributed Aggregation algorithms
- Performance benchmarks
- Production deployment considerations
