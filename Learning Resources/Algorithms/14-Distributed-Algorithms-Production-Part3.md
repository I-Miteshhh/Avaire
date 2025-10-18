# Distributed Algorithms - Production Grade (Part 3)

**Continuation from Part 2**

---

## 4. External Sort - Sorting Data Larger Than Memory

### The Problem

**Scenario:** Sort 1 TB of data with only 16 GB of RAM.

```
Challenge:
- Data doesn't fit in memory
- Can't use quicksort/mergesort directly
- Need to use disk efficiently

Solution: External Merge Sort
- Sort chunks that fit in memory
- Merge sorted chunks using multi-way merge
```

**Used By:**
- Hadoop MapReduce (shuffle phase)
- Apache Spark (sort-based shuffle)
- Database systems (ORDER BY on large tables)
- Unix `sort` command

---

### Algorithm Explanation

**External Merge Sort** in 2 phases:

**Phase 1: Sort Phase**
```
Input file: 1 TB (unsorted)
Available memory: 16 GB

1. Read 16 GB chunk → Sort in memory → Write to disk as sorted run
2. Read next 16 GB → Sort → Write as sorted run
3. Repeat until entire file processed

Result: 64 sorted runs (1 TB / 16 GB = 64)
```

**Phase 2: Merge Phase**
```
Use k-way merge to merge all runs:

k = 8 (merge 8 runs at a time)

Pass 1: Merge 64 runs into 8 runs
  - Merge runs [0-7] → run_0
  - Merge runs [8-15] → run_1
  - ...
  - Merge runs [56-63] → run_7

Pass 2: Merge 8 runs into 1 run
  - Merge runs [0-7] → final sorted file
```

**Key Optimization:** Use a min-heap for efficient k-way merge

---

### Production-Grade Implementation (Java)

```java
package com.dateng.sort;

import java.io.*;
import java.nio.file.*;
import java.util.*;

/**
 * External Merge Sort for sorting files larger than memory
 * 
 * Features:
 * - Memory-efficient (uses only specified memory limit)
 * - K-way merge using min-heap
 * - Progress tracking
 * - Cleanup of temporary files
 * 
 * Use Cases:
 * - Sorting large log files
 * - ETL data processing
 * - MapReduce shuffle phase
 * 
 * @author Principal Data Engineer
 */
public class ExternalSort {
    
    private final long memoryLimitBytes;
    private final Path tempDir;
    private final Comparator<String> comparator;
    
    /**
     * Constructor
     * 
     * @param memoryLimitMB Memory limit in megabytes
     * @param tempDir Temporary directory for sorted runs
     */
    public ExternalSort(int memoryLimitMB, Path tempDir) {
        this.memoryLimitBytes = (long) memoryLimitMB * 1024 * 1024;
        this.tempDir = tempDir;
        this.comparator = String::compareTo;
        
        // Create temp directory
        try {
            Files.createDirectories(tempDir);
        } catch (IOException e) {
            throw new RuntimeException("Failed to create temp directory", e);
        }
        
        System.out.printf("[ExternalSort] Initialized with %d MB memory limit%n", memoryLimitMB);
    }
    
    /**
     * Sort a file that's larger than memory
     * 
     * @param inputFile Input file to sort
     * @param outputFile Output sorted file
     * @throws IOException If I/O error occurs
     */
    public void sort(Path inputFile, Path outputFile) throws IOException {
        System.out.printf("[ExternalSort] Sorting %s (%d MB)%n", 
                          inputFile.getFileName(), 
                          Files.size(inputFile) / (1024 * 1024));
        
        long startTime = System.currentTimeMillis();
        
        // Phase 1: Create sorted runs
        List<Path> sortedRuns = createSortedRuns(inputFile);
        
        System.out.printf("[ExternalSort] Created %d sorted runs%n", sortedRuns.size());
        
        // Phase 2: Merge sorted runs
        mergeSortedRuns(sortedRuns, outputFile);
        
        // Cleanup
        cleanupTempFiles(sortedRuns);
        
        long elapsedMs = System.currentTimeMillis() - startTime;
        
        System.out.printf("[ExternalSort] Sorting complete in %.2f seconds%n", 
                          elapsedMs / 1000.0);
    }
    
    /**
     * Phase 1: Create sorted runs
     * 
     * Reads chunks of data that fit in memory, sorts them, and writes to disk
     */
    private List<Path> createSortedRuns(Path inputFile) throws IOException {
        List<Path> sortedRuns = new ArrayList<>();
        
        try (BufferedReader reader = Files.newBufferedReader(inputFile)) {
            List<String> chunk = new ArrayList<>();
            long currentMemory = 0;
            String line;
            int runNumber = 0;
            
            while ((line = reader.readLine()) != null) {
                chunk.add(line);
                currentMemory += estimateMemoryUsage(line);
                
                // Check if chunk is full
                if (currentMemory >= memoryLimitBytes) {
                    sortedRuns.add(sortAndWriteChunk(chunk, runNumber++));
                    chunk.clear();
                    currentMemory = 0;
                }
            }
            
            // Write remaining chunk
            if (!chunk.isEmpty()) {
                sortedRuns.add(sortAndWriteChunk(chunk, runNumber));
            }
        }
        
        return sortedRuns;
    }
    
    /**
     * Sort a chunk in memory and write to disk
     */
    private Path sortAndWriteChunk(List<String> chunk, int runNumber) throws IOException {
        // Sort in memory
        chunk.sort(comparator);
        
        // Write to temporary file
        Path runFile = tempDir.resolve("run_" + runNumber + ".txt");
        
        try (BufferedWriter writer = Files.newBufferedWriter(runFile)) {
            for (String line : chunk) {
                writer.write(line);
                writer.newLine();
            }
        }
        
        System.out.printf("[ExternalSort] Created run %d with %d lines (%.2f MB)%n", 
                          runNumber, chunk.size(), Files.size(runFile) / (1024.0 * 1024.0));
        
        return runFile;
    }
    
    /**
     * Phase 2: Merge sorted runs using k-way merge
     * 
     * Uses a min-heap to efficiently merge multiple sorted runs
     */
    private void mergeSortedRuns(List<Path> sortedRuns, Path outputFile) throws IOException {
        if (sortedRuns.size() == 1) {
            // Only one run, just rename it
            Files.move(sortedRuns.get(0), outputFile, StandardCopyOption.REPLACE_EXISTING);
            return;
        }
        
        // Perform iterative k-way merge
        int mergeWays = calculateOptimalMergeWays(sortedRuns.size());
        
        List<Path> currentRuns = new ArrayList<>(sortedRuns);
        int passNumber = 1;
        
        while (currentRuns.size() > 1) {
            System.out.printf("[ExternalSort] Merge pass %d: %d runs → ", 
                              passNumber, currentRuns.size());
            
            List<Path> nextRuns = new ArrayList<>();
            
            for (int i = 0; i < currentRuns.size(); i += mergeWays) {
                int end = Math.min(i + mergeWays, currentRuns.size());
                List<Path> runsToMerge = currentRuns.subList(i, end);
                
                Path mergedRun = tempDir.resolve("merged_pass" + passNumber + "_" + (i / mergeWays) + ".txt");
                kWayMerge(runsToMerge, mergedRun);
                nextRuns.add(mergedRun);
            }
            
            // Cleanup previous pass files
            for (Path run : currentRuns) {
                Files.deleteIfExists(run);
            }
            
            currentRuns = nextRuns;
            passNumber++;
            
            System.out.printf("%d runs%n", currentRuns.size());
        }
        
        // Move final run to output file
        Files.move(currentRuns.get(0), outputFile, StandardCopyOption.REPLACE_EXISTING);
    }
    
    /**
     * K-way merge using min-heap
     * 
     * Time Complexity: O(N log K) where N = total lines, K = number of runs
     */
    private void kWayMerge(List<Path> runs, Path outputFile) throws IOException {
        // Open readers for all runs
        List<BufferedReader> readers = new ArrayList<>();
        for (Path run : runs) {
            readers.add(Files.newBufferedReader(run));
        }
        
        // Min-heap for k-way merge
        PriorityQueue<HeapNode> minHeap = new PriorityQueue<>(
            runs.size(),
            Comparator.comparing(node -> node.value, comparator)
        );
        
        // Initialize heap with first line from each run
        for (int i = 0; i < readers.size(); i++) {
            String line = readers.get(i).readLine();
            if (line != null) {
                minHeap.offer(new HeapNode(line, i));
            }
        }
        
        // Merge and write to output
        try (BufferedWriter writer = Files.newBufferedWriter(outputFile)) {
            while (!minHeap.isEmpty()) {
                HeapNode node = minHeap.poll();
                
                writer.write(node.value);
                writer.newLine();
                
                // Read next line from the same run
                String nextLine = readers.get(node.runIndex).readLine();
                if (nextLine != null) {
                    minHeap.offer(new HeapNode(nextLine, node.runIndex));
                }
            }
        }
        
        // Close all readers
        for (BufferedReader reader : readers) {
            reader.close();
        }
    }
    
    /**
     * Calculate optimal merge ways based on number of runs
     * 
     * Trade-off:
     * - Higher k: Fewer passes, but more overhead per comparison
     * - Lower k: More passes, but simpler merge
     * 
     * Typical values: 8-32
     */
    private int calculateOptimalMergeWays(int numRuns) {
        if (numRuns <= 8) {
            return numRuns;
        } else if (numRuns <= 64) {
            return 8;
        } else if (numRuns <= 512) {
            return 16;
        } else {
            return 32;
        }
    }
    
    /**
     * Estimate memory usage of a string
     * Rough estimate: 2 bytes per char + object overhead
     */
    private long estimateMemoryUsage(String str) {
        return 48 + (long) str.length() * 2; // 48 bytes object overhead
    }
    
    /**
     * Cleanup temporary files
     */
    private void cleanupTempFiles(List<Path> files) {
        for (Path file : files) {
            try {
                Files.deleteIfExists(file);
            } catch (IOException e) {
                System.err.println("Warning: Failed to delete " + file);
            }
        }
    }
    
    /**
     * Node in the min-heap for k-way merge
     */
    private static class HeapNode {
        final String value;
        final int runIndex;
        
        HeapNode(String value, int runIndex) {
            this.value = value;
            this.runIndex = runIndex;
        }
    }
}
```

---

### Usage Example

```java
package com.dateng.sort;

import java.io.*;
import java.nio.file.*;
import java.util.Random;

/**
 * Test external sort with large file
 */
public class ExternalSortDemo {
    
    public static void main(String[] args) throws IOException {
        System.out.println("=== External Sort Demo ===\n");
        
        // Generate large test file (100 MB)
        Path inputFile = Paths.get("large_file.txt");
        Path outputFile = Paths.get("sorted_file.txt");
        Path tempDir = Paths.get("temp_sort");
        
        // Generate test data
        generateTestFile(inputFile, 1_000_000); // 1M lines ≈ 100 MB
        
        // Sort with 16 MB memory limit
        ExternalSort sorter = new ExternalSort(16, tempDir);
        sorter.sort(inputFile, outputFile);
        
        // Verify sort
        boolean sorted = verifySorted(outputFile);
        System.out.printf("\n[Verification] File is %s%n", sorted ? "SORTED ✓" : "NOT SORTED ✗");
        
        // Cleanup
        Files.deleteIfExists(inputFile);
        Files.deleteIfExists(outputFile);
        deleteDirectory(tempDir);
    }
    
    /**
     * Generate test file with random strings
     */
    private static void generateTestFile(Path file, int numLines) throws IOException {
        System.out.printf("Generating test file with %,d lines...%n", numLines);
        
        Random rand = new Random(42);
        
        try (BufferedWriter writer = Files.newBufferedWriter(file)) {
            for (int i = 0; i < numLines; i++) {
                // Generate random string (20-100 characters)
                int length = 20 + rand.nextInt(80);
                StringBuilder sb = new StringBuilder(length);
                
                for (int j = 0; j < length; j++) {
                    sb.append((char) ('a' + rand.nextInt(26)));
                }
                
                writer.write(sb.toString());
                writer.newLine();
                
                if ((i + 1) % 100_000 == 0) {
                    System.out.printf("  Generated %,d lines (%.1f MB)%n", 
                                      i + 1, Files.size(file) / (1024.0 * 1024.0));
                }
            }
        }
        
        System.out.printf("Generated %s (%.2f MB)%n\n", 
                          file.getFileName(), Files.size(file) / (1024.0 * 1024.0));
    }
    
    /**
     * Verify that file is sorted
     */
    private static boolean verifySorted(Path file) throws IOException {
        try (BufferedReader reader = Files.newBufferedReader(file)) {
            String prev = reader.readLine();
            String line;
            
            while ((line = reader.readLine()) != null) {
                if (prev.compareTo(line) > 0) {
                    return false;
                }
                prev = line;
            }
        }
        
        return true;
    }
    
    private static void deleteDirectory(Path dir) throws IOException {
        if (Files.exists(dir)) {
            Files.walk(dir)
                .sorted(Comparator.reverseOrder())
                .forEach(path -> {
                    try {
                        Files.delete(path);
                    } catch (IOException e) {
                        // Ignore
                    }
                });
        }
    }
}
```

---

### Real-World: Hadoop MapReduce Shuffle

```
MapReduce uses external sort for the shuffle phase:

Map Output: [("word1", 1), ("word2", 1), ("word1", 1), ...]
            ↓
          Partitioner (by key)
            ↓
      Spill to disk as sorted runs
            ↓
      Multi-way merge (external sort)
            ↓
      Merged output for each partition
            ↓
      Send to reducers

Configuration:
- io.sort.mb: Memory for sort buffer (default: 100 MB)
- io.sort.spill.percent: When to spill (default: 80%)
- io.sort.factor: Merge ways (default: 10)

Optimization:
- Combiner: Reduce data before shuffle
- Compression: Compress intermediate data
- Fewer spills: Increase sort buffer size
```

---

## 5. Distributed Aggregation

### The Problem

**Scenario:** Calculate P95 latency across 1000 servers in real-time.

```
Challenge:
- Can't collect all data points to a single server (too much data)
- Need to aggregate locally, then combine results
- Some metrics are easy (sum, count), others are hard (percentiles, distinct count)

Aggregation Types:
1. Distributive: Can be computed in parallel (sum, count, min, max)
2. Algebraic: Can be computed from partial aggregates (avg, stddev)
3. Holistic: Require full dataset (median, percentiles, mode)
```

---

### Distributive Aggregations

Easy to parallelize:

```
SUM across 3 servers:
  Server 1: [1, 2, 3] → sum = 6
  Server 2: [4, 5, 6] → sum = 15
  Server 3: [7, 8, 9] → sum = 24
  
  Final: 6 + 15 + 24 = 45 ✓

COUNT:
  Server 1: count = 3
  Server 2: count = 3
  Server 3: count = 3
  
  Final: 3 + 3 + 3 = 9 ✓

MIN/MAX: Similar
```

---

### Algebraic Aggregations

Can be computed from partial results:

```
AVG across 3 servers:
  Server 1: sum = 6, count = 3
  Server 2: sum = 15, count = 3
  Server 3: sum = 24, count = 3
  
  Final: (6 + 15 + 24) / (3 + 3 + 3) = 45 / 9 = 5 ✓

VARIANCE:
  Server 1: sum = 6, sum_squares = 14, count = 3
  Server 2: sum = 15, sum_squares = 77, count = 3
  Server 3: sum = 24, sum_squares = 194, count = 3
  
  Final: variance = (sum_squares / count) - (sum / count)^2
```

---

### Holistic Aggregations (Hard!)

**Problem:** MEDIAN, PERCENTILES require full dataset

**Solution 1:** Collect all data (doesn't scale)
**Solution 2:** Approximate with sketches

---

### Implementation: t-digest for Percentiles

```java
package com.dateng.aggregation;

import java.util.*;

/**
 * t-digest: Approximate percentile calculation for streaming data
 * 
 * Features:
 * - Memory-efficient (configurable accuracy)
 * - Mergeable (for distributed aggregation)
 * - Accurate at tails (P95, P99)
 * 
 * Used By:
 * - Elasticsearch: Percentile aggregations
 * - InfluxDB: Percentile queries
 * - Prometheus: Histogram quantiles
 * 
 * @author Principal Data Engineer
 */
public class TDigest {
    
    private final double compression;
    private final List<Centroid> centroids;
    private long count;
    private double min;
    private double max;
    
    /**
     * Constructor
     * 
     * @param compression Accuracy parameter (higher = more accurate, more memory)
     *                    Typical value: 100 (memory: ~2KB, error: <1%)
     */
    public TDigest(double compression) {
        this.compression = compression;
        this.centroids = new ArrayList<>();
        this.count = 0;
        this.min = Double.MAX_VALUE;
        this.max = Double.MIN_VALUE;
    }
    
    /**
     * Add a value to the digest
     * 
     * @param value Value to add
     */
    public void add(double value) {
        add(value, 1);
    }
    
    /**
     * Add a value with weight
     * 
     * @param value Value to add
     * @param weight Weight of the value
     */
    public void add(double value, long weight) {
        if (centroids.isEmpty()) {
            centroids.add(new Centroid(value, weight));
        } else {
            // Find closest centroid
            int insertIndex = findClosestCentroid(value);
            
            Centroid closest = centroids.get(insertIndex);
            
            // Merge if within compression limit
            if (closest.weight + weight <= compressionLimit(insertIndex)) {
                closest.add(value, weight);
            } else {
                // Create new centroid
                centroids.add(insertIndex + 1, new Centroid(value, weight));
                
                // Compress if too many centroids
                if (centroids.size() > compression * 2) {
                    compress();
                }
            }
        }
        
        count += weight;
        min = Math.min(min, value);
        max = Math.max(max, value);
    }
    
    /**
     * Calculate percentile
     * 
     * @param percentile Percentile (0-1, e.g., 0.95 for P95)
     * @return Estimated value at percentile
     */
    public double quantile(double percentile) {
        if (centroids.isEmpty()) {
            return Double.NaN;
        }
        
        if (percentile <= 0) return min;
        if (percentile >= 1) return max;
        
        double index = percentile * count;
        
        long weightSoFar = 0;
        
        for (int i = 0; i < centroids.size() - 1; i++) {
            Centroid c = centroids.get(i);
            long nextWeight = weightSoFar + c.weight;
            
            if (nextWeight >= index) {
                // Interpolate within centroid
                double delta = (index - weightSoFar) / c.weight;
                Centroid next = centroids.get(i + 1);
                return c.mean + delta * (next.mean - c.mean);
            }
            
            weightSoFar = nextWeight;
        }
        
        return centroids.get(centroids.size() - 1).mean;
    }
    
    /**
     * Merge another t-digest into this one
     * Used for distributed aggregation
     */
    public void merge(TDigest other) {
        for (Centroid c : other.centroids) {
            add(c.mean, c.weight);
        }
    }
    
    /**
     * Find closest centroid to value
     */
    private int findClosestCentroid(double value) {
        int left = 0;
        int right = centroids.size() - 1;
        
        while (left < right) {
            int mid = (left + right) / 2;
            
            if (centroids.get(mid).mean < value) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }
        
        return Math.max(0, left - 1);
    }
    
    /**
     * Calculate compression limit for a centroid
     */
    private double compressionLimit(int index) {
        double q = (double) index / centroids.size();
        return 4 * count * q * (1 - q) / compression;
    }
    
    /**
     * Compress centroids by merging nearby ones
     */
    private void compress() {
        // Sort centroids by mean
        centroids.sort(Comparator.comparingDouble(c -> c.mean));
        
        // Merge adjacent centroids
        List<Centroid> compressed = new ArrayList<>();
        Centroid current = centroids.get(0);
        
        for (int i = 1; i < centroids.size(); i++) {
            Centroid next = centroids.get(i);
            
            if (current.weight + next.weight <= compressionLimit(compressed.size())) {
                current.merge(next);
            } else {
                compressed.add(current);
                current = next;
            }
        }
        
        compressed.add(current);
        
        centroids.clear();
        centroids.addAll(compressed);
    }
    
    /**
     * Get memory usage estimate
     */
    public long getMemoryBytes() {
        return centroids.size() * 24; // 24 bytes per centroid (mean + weight + overhead)
    }
    
    /**
     * Get statistics
     */
    public Stats getStats() {
        return new Stats(
            centroids.size(),
            count,
            min,
            max,
            quantile(0.5),  // median
            quantile(0.95), // P95
            quantile(0.99), // P99
            getMemoryBytes()
        );
    }
    
    /**
     * Centroid: Represents a cluster of values
     */
    private static class Centroid {
        double mean;
        long weight;
        
        Centroid(double mean, long weight) {
            this.mean = mean;
            this.weight = weight;
        }
        
        void add(double value, long w) {
            weight += w;
            mean += w * (value - mean) / weight;
        }
        
        void merge(Centroid other) {
            long totalWeight = weight + other.weight;
            mean = (weight * mean + other.weight * other.mean) / totalWeight;
            weight = totalWeight;
        }
    }
    
    public static class Stats {
        public final int numCentroids;
        public final long count;
        public final double min;
        public final double max;
        public final double median;
        public final double p95;
        public final double p99;
        public final long memoryBytes;
        
        Stats(int numCentroids, long count, double min, double max,
              double median, double p95, double p99, long memoryBytes) {
            this.numCentroids = numCentroids;
            this.count = count;
            this.min = min;
            this.max = max;
            this.median = median;
            this.p95 = p95;
            this.p99 = p99;
            this.memoryBytes = memoryBytes;
        }
        
        @Override
        public String toString() {
            return String.format(
                "TDigest Stats:\n" +
                "  Centroids: %d\n" +
                "  Count: %d\n" +
                "  Min: %.2f\n" +
                "  Max: %.2f\n" +
                "  Median (P50): %.2f\n" +
                "  P95: %.2f\n" +
                "  P99: %.2f\n" +
                "  Memory: %d bytes",
                numCentroids, count, min, max, median, p95, p99, memoryBytes
            );
        }
    }
}
```

---

### Use Case: Distributed Latency Monitoring

```java
package com.dateng.aggregation;

import java.util.*;
import java.util.concurrent.ThreadLocalRandom;

/**
 * Monitor API latency across multiple servers
 */
public class DistributedLatencyMonitor {
    
    /**
     * Simulate latency data from multiple servers
     */
    public static void main(String[] args) {
        System.out.println("=== Distributed Latency Monitoring ===\n");
        
        // Simulate 10 servers
        int numServers = 10;
        List<TDigest> serverDigests = new ArrayList<>();
        
        // Each server collects latency data
        for (int i = 0; i < numServers; i++) {
            TDigest digest = new TDigest(100);
            
            // Simulate 100,000 requests per server
            for (int j = 0; j < 100_000; j++) {
                double latency = generateLatency();
                digest.add(latency);
            }
            
            serverDigests.add(digest);
            
            System.out.printf("Server %d collected 100,000 samples%n", i + 1);
        }
        
        // Aggregate across all servers
        TDigest globalDigest = new TDigest(100);
        
        for (TDigest digest : serverDigests) {
            globalDigest.merge(digest);
        }
        
        System.out.println("\n=== Global Latency Statistics ===");
        System.out.println(globalDigest.getStats());
        
        // Calculate specific percentiles
        System.out.println("\nDetailed Percentiles:");
        double[] percentiles = {0.5, 0.9, 0.95, 0.99, 0.999};
        
        for (double p : percentiles) {
            double latency = globalDigest.quantile(p);
            System.out.printf("P%.1f: %.2f ms%n", p * 100, latency);
        }
        
        // Memory usage
        long totalMemory = numServers * serverDigests.get(0).getMemoryBytes() + globalDigest.getMemoryBytes();
        long exactMemory = numServers * 100_000 * 8; // 8 bytes per double
        
        System.out.printf("\nMemory Usage:%n");
        System.out.printf("  t-digest: %.2f KB%n", totalMemory / 1024.0);
        System.out.printf("  Exact: %.2f MB%n", exactMemory / (1024.0 * 1024.0));
        System.out.printf("  Savings: %.1fx%n", exactMemory / (double) totalMemory);
    }
    
    /**
     * Generate latency following log-normal distribution
     * (realistic API latency pattern)
     */
    private static double generateLatency() {
        double mean = Math.log(50); // median 50ms
        double stddev = 0.5;
        
        double normal = ThreadLocalRandom.current().nextGaussian();
        return Math.exp(mean + stddev * normal);
    }
}
```

---

## 6. Complete Benchmark Suite

```java
package com.dateng.benchmark;

import com.dateng.distributed.*;
import com.dateng.probabilistic.*;
import com.dateng.ratelimit.*;
import com.dateng.aggregation.*;

/**
 * Comprehensive benchmark for all distributed algorithms
 */
public class DistributedAlgorithmsBenchmark {
    
    public static void main(String[] args) {
        System.out.println("=== Distributed Algorithms Benchmark Suite ===\n");
        
        benchmarkConsistentHashing();
        benchmarkRateLimiting();
        benchmarkBloomFilter();
        benchmarkCountMinSketch();
        benchmarkHyperLogLog();
        benchmarkTDigest();
    }
    
    private static void benchmarkConsistentHashing() {
        System.out.println("1. Consistent Hashing Benchmark");
        System.out.println("--------------------------------");
        
        ConsistentHashRing<String> ring = new ConsistentHashRing<>(150);
        
        // Add nodes
        long startTime = System.nanoTime();
        for (int i = 0; i < 100; i++) {
            ring.addNode("server-" + i);
        }
        long addTime = (System.nanoTime() - startTime) / 1_000_000;
        
        // Lookup benchmark
        startTime = System.nanoTime();
        for (int i = 0; i < 1_000_000; i++) {
            ring.getNode("key-" + i);
        }
        long lookupTime = (System.nanoTime() - startTime) / 1_000_000;
        
        System.out.printf("Add 100 nodes: %d ms%n", addTime);
        System.out.printf("1M lookups: %d ms (%.1f ns/lookup)%n", 
                          lookupTime, lookupTime * 1_000_000.0 / 1_000_000);
        System.out.println();
    }
    
    private static void benchmarkRateLimiting() {
        System.out.println("2. Rate Limiting Benchmark");
        System.out.println("-------------------------");
        
        TokenBucketRateLimiter limiter = new TokenBucketRateLimiter(1000, 1000);
        
        long startTime = System.nanoTime();
        int allowed = 0;
        
        for (int i = 0; i < 1_000_000; i++) {
            if (limiter.allowRequest("user-" + (i % 1000))) {
                allowed++;
            }
        }
        
        long elapsed = (System.nanoTime() - startTime) / 1_000_000;
        
        System.out.printf("1M rate limit checks: %d ms%n", elapsed);
        System.out.printf("Throughput: %.1f checks/second%n", 1_000_000_000.0 / elapsed);
        System.out.printf("Allowed: %d / 1,000,000%n", allowed);
        System.out.println();
    }
    
    private static void benchmarkBloomFilter() {
        System.out.println("3. Bloom Filter Benchmark");
        System.out.println("------------------------");
        
        BloomFilter<String> bf = new BloomFilter<>(1_000_000, 0.01);
        
        // Add items
        long startTime = System.nanoTime();
        for (int i = 0; i < 1_000_000; i++) {
            bf.add("item-" + i);
        }
        long addTime = (System.nanoTime() - startTime) / 1_000_000;
        
        // Query items
        startTime = System.nanoTime();
        int found = 0;
        for (int i = 0; i < 1_000_000; i++) {
            if (bf.mightContain("item-" + i)) {
                found++;
            }
        }
        long queryTime = (System.nanoTime() - startTime) / 1_000_000;
        
        // Test false positives
        int falsePositives = 0;
        for (int i = 1_000_000; i < 2_000_000; i++) {
            if (bf.mightContain("item-" + i)) {
                falsePositives++;
            }
        }
        
        System.out.printf("Add 1M items: %d ms%n", addTime);
        System.out.printf("Query 1M items: %d ms%n", queryTime);
        System.out.printf("False positive rate: %.4f%% (expected: 1%%)%n", 
                          falsePositives / 10000.0);
        System.out.printf("Memory: %.2f KB%n", bf.getMemoryUsageBytes() / 1024.0);
        System.out.println();
    }
    
    private static void benchmarkCountMinSketch() {
        System.out.println("4. Count-Min Sketch Benchmark");
        System.out.println("----------------------------");
        
        CountMinSketch cms = new CountMinSketch(0.001, 0.99);
        
        // Add items
        long startTime = System.nanoTime();
        for (int i = 0; i < 10_000_000; i++) {
            cms.add("item-" + (i % 1000)); // 1000 unique items
        }
        long addTime = (System.nanoTime() - startTime) / 1_000_000;
        
        // Query frequency
        startTime = System.nanoTime();
        for (int i = 0; i < 1000; i++) {
            cms.estimateCount("item-" + i);
        }
        long queryTime = (System.nanoTime() - startTime) / 1_000;
        
        // Check accuracy
        long estimated = cms.estimateCount("item-0");
        long actual = 10_000;
        double error = Math.abs(estimated - actual) / (double) actual * 100;
        
        System.out.printf("Add 10M items: %d ms%n", addTime);
        System.out.printf("Query 1000 items: %d µs%n", queryTime);
        System.out.printf("Accuracy: estimated=%d, actual=%d, error=%.2f%%%n", 
                          estimated, actual, error);
        System.out.printf("Memory: %.2f KB%n", cms.getMemoryUsageBytes() / 1024.0);
        System.out.println();
    }
    
    private static void benchmarkHyperLogLog() {
        System.out.println("5. HyperLogLog Benchmark");
        System.out.println("-----------------------");
        
        HyperLogLog hll = new HyperLogLog(14);
        
        // Add items
        long startTime = System.nanoTime();
        int numItems = 10_000_000;
        for (int i = 0; i < numItems; i++) {
            hll.add("item-" + i);
        }
        long addTime = (System.nanoTime() - startTime) / 1_000_000;
        
        // Estimate cardinality
        startTime = System.nanoTime();
        long estimated = hll.estimateCardinality();
        long estimateTime = (System.nanoTime() - startTime) / 1_000;
        
        double error = Math.abs(estimated - numItems) / (double) numItems * 100;
        
        System.out.printf("Add 10M unique items: %d ms%n", addTime);
        System.out.printf("Estimate cardinality: %d µs%n", estimateTime);
        System.out.printf("Accuracy: estimated=%,d, actual=%,d, error=%.2f%%%n", 
                          estimated, numItems, error);
        System.out.printf("Memory: %.2f KB%n", hll.getMemoryUsageBytes() / 1024.0);
        System.out.println();
    }
    
    private static void benchmarkTDigest() {
        System.out.println("6. t-digest Benchmark");
        System.out.println("--------------------");
        
        TDigest digest = new TDigest(100);
        
        // Add items
        long startTime = System.nanoTime();
        Random rand = new Random(42);
        for (int i = 0; i < 10_000_000; i++) {
            digest.add(rand.nextDouble() * 1000);
        }
        long addTime = (System.nanoTime() - startTime) / 1_000_000;
        
        // Query percentiles
        startTime = System.nanoTime();
        double p50 = digest.quantile(0.5);
        double p95 = digest.quantile(0.95);
        double p99 = digest.quantile(0.99);
        long queryTime = (System.nanoTime() - startTime) / 1_000;
        
        System.out.printf("Add 10M values: %d ms%n", addTime);
        System.out.printf("Query 3 percentiles: %d µs%n", queryTime);
        System.out.printf("P50: %.2f, P95: %.2f, P99: %.2f%n", p50, p95, p99);
        System.out.printf("Memory: %.2f KB%n", digest.getMemoryBytes() / 1024.0);
        System.out.println();
    }
}
```

---

## Summary

### What We've Covered

1. ✅ **Consistent Hashing** (Part 1)
   - Distributed caching and load balancing
   - Virtual nodes for uniform distribution
   - Production implementation with metrics

2. ✅ **Rate Limiting** (Part 1)
   - Token Bucket, Sliding Window algorithms
   - Distributed rate limiting with Redis
   - Hierarchical and tiered rate limits

3. ✅ **Bloom Filter** (Part 2)
   - Space-efficient set membership testing
   - Web crawler URL deduplication
   - Cassandra SSTable optimization

4. ✅ **Count-Min Sketch** (Part 2)
   - Frequency estimation for streaming data
   - Top-K heavy hitters detection
   - Network traffic analysis

5. ✅ **HyperLogLog** (Part 2)
   - Cardinality estimation with minimal memory
   - Unique visitor counting
   - Distributed aggregation with merge

6. ✅ **External Sort** (Part 3)
   - Sort data larger than memory
   - K-way merge algorithm
   - Hadoop MapReduce shuffle phase

7. ✅ **Distributed Aggregation** (Part 3)
   - t-digest for percentile calculation
   - Distributive vs holistic aggregations
   - Multi-server latency monitoring

### Performance Summary

| Algorithm | Operation | Time | Space | Use Case |
|-----------|-----------|------|-------|----------|
| Consistent Hash | Lookup | O(log N) | O(N) | Distributed cache |
| Token Bucket | Check | O(1) | O(1) | Rate limiting |
| Bloom Filter | Add/Query | O(k) | O(m) | Set membership |
| Count-Min Sketch | Add/Query | O(d) | O(d×w) | Frequency count |
| HyperLogLog | Add | O(1) | O(m) | Cardinality |
| External Sort | Sort | O(N log N) | O(M) | Large file sort |
| t-digest | Add/Query | O(1) | O(c) | Percentiles |

Where:
- N = number of items
- k = number of hash functions
- m = bit array size
- d = depth (rows)
- w = width (columns)
- c = compression factor
- M = available memory

### Production Checklist

When implementing these algorithms in production:

✅ **Monitoring**
- Track false positive rates (Bloom Filter)
- Monitor memory usage
- Alert on accuracy degradation

✅ **Configuration**
- Tune parameters for workload
- Load test under realistic conditions
- Plan for growth (10x, 100x)

✅ **Operational**
- Implement graceful degradation
- Handle edge cases (empty data, overflow)
- Document assumptions and limits

✅ **Testing**
- Unit tests with edge cases
- Property-based testing
- Chaos engineering for distributed components

---

**Next Steps:**
- Study the real-world implementations (Cassandra, Redis, Spark)
- Practice LeetCode problems using these algorithms
- Build a project combining multiple techniques

**End of Distributed Algorithms Module**
