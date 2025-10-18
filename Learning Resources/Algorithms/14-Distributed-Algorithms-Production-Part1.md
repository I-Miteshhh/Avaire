# Distributed Algorithms - Production Grade (Part 1)

**Target Role:** Principal Data Engineer / Staff Engineer (40+ LPA)  
**Difficulty:** Advanced  
**Learning Time:** 2-3 weeks  
**Interview Frequency:** ⭐⭐⭐⭐⭐

---

## 📚 Overview

This module covers **production-grade distributed algorithms** essential for building scalable data systems. These algorithms are used by companies like Netflix, Uber, LinkedIn, and Google to handle billions of requests daily.

**What You'll Learn:**
- Consistent Hashing for distributed caching and storage
- Rate Limiting algorithms at scale
- Probabilistic data structures (Bloom Filters, Count-Min Sketch, HyperLogLog)
- External Sort for data that doesn't fit in memory
- Distributed aggregation algorithms

**Real-World Applications:**
- Building distributed caches (Memcached, Redis clusters)
- API rate limiting (Stripe, Shopify, AWS API Gateway)
- Big data processing (Cassandra, DynamoDB, BigTable)
- Web crawlers and deduplication systems
- Real-time analytics and metric aggregation

---

## 1. Consistent Hashing

### The Problem

Traditional hashing for distributed systems:
```
server_index = hash(key) % num_servers
```

**Problem:** When a server is added or removed, almost ALL keys need to be remapped!

```
Before (3 servers):
key "user123" → hash = 12345 → 12345 % 3 = 0 → Server 0

After adding 1 server (4 servers):
key "user123" → hash = 12345 → 12345 % 4 = 1 → Server 1 ❌
```

**Impact:** Adding/removing one server causes ~80% of cache misses in a distributed cache!

### Solution: Consistent Hashing

Consistent hashing minimizes key redistribution:
- When a node is added, only K/n keys are remapped (K = total keys, n = num nodes)
- When a node is removed, only K/n keys are remapped

**Used By:**
- Amazon DynamoDB
- Apache Cassandra
- Memcached clusters
- Akamai CDN
- Discord (for partitioning)

---

### Algorithm Explanation

**Core Concept:** Hash both servers and keys onto a ring (0 to 2^32-1).

```
Visualization of Hash Ring:

         0
         |
    270° |  90°
         |
    -----*-----
    |    |    |
  S2     |    S1
         |
        180°
        S3

Keys are assigned to the next server clockwise:
- key1 (hash=50) → Server S1 (at 90°)
- key2 (hash=100) → Server S1 (at 90°)
- key3 (hash=200) → Server S3 (at 180°)
```

**Virtual Nodes:** Each physical server gets multiple positions on the ring for better load distribution.

```
Physical Server S1 gets virtual nodes:
- S1-vnode-0 at position 45
- S1-vnode-1 at position 134
- S1-vnode-2 at position 289
...
```

---

### Production-Grade Implementation (Java)

```java
package com.dateng.distributed;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.*;
import java.util.concurrent.ConcurrentSkipListMap;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;

/**
 * Production-grade Consistent Hashing implementation with virtual nodes.
 * 
 * Features:
 * - Thread-safe operations
 * - Configurable virtual nodes per server
 * - MD5 hashing for uniform distribution
 * - Hot-spot detection
 * - Rebalancing support
 * 
 * Used for:
 * - Distributed cache (Memcached cluster)
 * - Database sharding
 * - Load balancing
 * 
 * @author Principal Data Engineer
 */
public class ConsistentHashRing<T> {
    
    /**
     * Hash ring: Maps hash values to server nodes
     * Using TreeMap for O(log n) lookups
     * ConcurrentSkipListMap for thread-safety
     */
    private final NavigableMap<Long, VirtualNode<T>> ring;
    
    /**
     * Physical nodes to virtual nodes mapping
     */
    private final Map<T, Set<VirtualNode<T>>> physicalNodeMap;
    
    /**
     * Number of virtual nodes per physical node
     * Higher value = better distribution, more memory
     * Recommended: 150-300 for production
     */
    private final int virtualNodesPerNode;
    
    /**
     * Hash function for consistent hashing
     */
    private final MessageDigest md5;
    
    /**
     * Read-write lock for thread-safe add/remove operations
     */
    private final ReadWriteLock lock;
    
    /**
     * Metrics for monitoring
     */
    private final Metrics metrics;
    
    /**
     * Constructor
     * 
     * @param virtualNodesPerNode Number of virtual nodes per physical node (default: 150)
     */
    public ConsistentHashRing(int virtualNodesPerNode) {
        this.ring = new ConcurrentSkipListMap<>();
        this.physicalNodeMap = new ConcurrentHashMap<>();
        this.virtualNodesPerNode = virtualNodesPerNode;
        this.lock = new ReentrantReadWriteLock();
        this.metrics = new Metrics();
        
        try {
            this.md5 = MessageDigest.getInstance("MD5");
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("MD5 algorithm not available", e);
        }
    }
    
    /**
     * Default constructor with 150 virtual nodes
     */
    public ConsistentHashRing() {
        this(150);
    }
    
    /**
     * Add a physical node to the hash ring
     * Creates virtual nodes for better distribution
     * 
     * Time Complexity: O(V log N) where V = virtualNodesPerNode, N = total nodes
     * 
     * @param node Physical node to add
     */
    public void addNode(T node) {
        lock.writeLock().lock();
        try {
            if (physicalNodeMap.containsKey(node)) {
                throw new IllegalArgumentException("Node already exists: " + node);
            }
            
            Set<VirtualNode<T>> virtualNodes = new HashSet<>();
            
            // Create virtual nodes
            for (int i = 0; i < virtualNodesPerNode; i++) {
                String virtualNodeKey = node.toString() + "-vnode-" + i;
                long hash = hash(virtualNodeKey);
                
                VirtualNode<T> vnode = new VirtualNode<>(node, i, hash);
                ring.put(hash, vnode);
                virtualNodes.add(vnode);
            }
            
            physicalNodeMap.put(node, virtualNodes);
            metrics.incrementNodeCount();
            
            System.out.printf("[ConsistentHash] Added node '%s' with %d virtual nodes%n", 
                              node, virtualNodesPerNode);
            
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    /**
     * Remove a physical node from the hash ring
     * All keys on this node will be redistributed
     * 
     * Time Complexity: O(V log N)
     * 
     * @param node Physical node to remove
     * @return true if node was removed, false if node didn't exist
     */
    public boolean removeNode(T node) {
        lock.writeLock().lock();
        try {
            Set<VirtualNode<T>> virtualNodes = physicalNodeMap.remove(node);
            
            if (virtualNodes == null) {
                return false;
            }
            
            // Remove all virtual nodes from ring
            for (VirtualNode<T> vnode : virtualNodes) {
                ring.remove(vnode.hash);
            }
            
            metrics.decrementNodeCount();
            
            System.out.printf("[ConsistentHash] Removed node '%s' and %d virtual nodes%n", 
                              node, virtualNodes.size());
            
            return true;
            
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    /**
     * Get the node responsible for a given key
     * 
     * Algorithm:
     * 1. Hash the key
     * 2. Find the first virtual node clockwise on the ring
     * 3. Return the corresponding physical node
     * 
     * Time Complexity: O(log N)
     * 
     * @param key Key to look up
     * @return Node responsible for this key
     * @throws IllegalStateException if ring is empty
     */
    public T getNode(String key) {
        lock.readLock().lock();
        try {
            if (ring.isEmpty()) {
                throw new IllegalStateException("Hash ring is empty");
            }
            
            long hash = hash(key);
            
            // Find the first node clockwise (ceiling)
            Map.Entry<Long, VirtualNode<T>> entry = ring.ceilingEntry(hash);
            
            // If no node found, wrap around to the first node
            if (entry == null) {
                entry = ring.firstEntry();
            }
            
            metrics.incrementLookupCount();
            
            return entry.getValue().physicalNode;
            
        } finally {
            lock.readLock().unlock();
        }
    }
    
    /**
     * Get N nodes responsible for a key (for replication)
     * 
     * Used for replication in distributed systems:
     * - Cassandra: RF (Replication Factor)
     * - DynamoDB: 3 replicas
     * 
     * @param key Key to look up
     * @param n Number of nodes to return
     * @return List of n nodes (may be less if not enough nodes available)
     */
    public List<T> getNodes(String key, int n) {
        lock.readLock().lock();
        try {
            if (ring.isEmpty()) {
                return Collections.emptyList();
            }
            
            Set<T> nodes = new LinkedHashSet<>();
            long hash = hash(key);
            
            // Start from the ceiling entry
            Map.Entry<Long, VirtualNode<T>> entry = ring.ceilingEntry(hash);
            
            // If no node found, start from beginning
            if (entry == null) {
                entry = ring.firstEntry();
            }
            
            // Traverse clockwise until we have n unique physical nodes
            Iterator<Map.Entry<Long, VirtualNode<T>>> iterator = 
                ring.tailMap(entry.getKey()).entrySet().iterator();
            
            while (nodes.size() < n && iterator.hasNext()) {
                nodes.add(iterator.next().getValue().physicalNode);
            }
            
            // If we reached the end, wrap around
            if (nodes.size() < n) {
                iterator = ring.headMap(entry.getKey()).entrySet().iterator();
                while (nodes.size() < n && iterator.hasNext()) {
                    nodes.add(iterator.next().getValue().physicalNode);
                }
            }
            
            return new ArrayList<>(nodes);
            
        } finally {
            lock.readLock().unlock();
        }
    }
    
    /**
     * Hash function using MD5
     * Returns first 8 bytes as long (64-bit hash)
     * 
     * MD5 chosen for:
     * - Uniform distribution
     * - Fast computation
     * - Not used for security, so MD5 is fine
     * 
     * @param key Key to hash
     * @return 64-bit hash value
     */
    private long hash(String key) {
        md5.reset();
        md5.update(key.getBytes(StandardCharsets.UTF_8));
        byte[] digest = md5.digest();
        
        // Take first 8 bytes and convert to long
        long hash = 0;
        for (int i = 0; i < 8; i++) {
            hash = (hash << 8) | (digest[i] & 0xFF);
        }
        
        return hash;
    }
    
    /**
     * Get distribution statistics
     * Useful for detecting hot spots
     * 
     * @param keys Sample keys to analyze
     * @return Map of node to key count
     */
    public Map<T, Integer> getDistribution(List<String> keys) {
        Map<T, Integer> distribution = new HashMap<>();
        
        for (String key : keys) {
            T node = getNode(key);
            distribution.put(node, distribution.getOrDefault(node, 0) + 1);
        }
        
        return distribution;
    }
    
    /**
     * Detect hot spots (nodes with > 1.5x average load)
     * 
     * @param keys Sample keys
     * @return List of overloaded nodes
     */
    public List<T> detectHotSpots(List<String> keys) {
        Map<T, Integer> distribution = getDistribution(keys);
        int totalKeys = keys.size();
        int numNodes = physicalNodeMap.size();
        double avgLoad = (double) totalKeys / numNodes;
        double hotSpotThreshold = avgLoad * 1.5;
        
        List<T> hotSpots = new ArrayList<>();
        for (Map.Entry<T, Integer> entry : distribution.entrySet()) {
            if (entry.getValue() > hotSpotThreshold) {
                hotSpots.add(entry.getKey());
            }
        }
        
        return hotSpots;
    }
    
    /**
     * Get current metrics
     */
    public Metrics getMetrics() {
        return metrics;
    }
    
    /**
     * Get number of physical nodes
     */
    public int getNodeCount() {
        return physicalNodeMap.size();
    }
    
    /**
     * Get all physical nodes
     */
    public Set<T> getNodes() {
        return new HashSet<>(physicalNodeMap.keySet());
    }
    
    /**
     * Virtual node representation
     */
    private static class VirtualNode<T> {
        final T physicalNode;
        final int replicaIndex;
        final long hash;
        
        VirtualNode(T physicalNode, int replicaIndex, long hash) {
            this.physicalNode = physicalNode;
            this.replicaIndex = replicaIndex;
            this.hash = hash;
        }
        
        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            VirtualNode<?> that = (VirtualNode<?>) o;
            return hash == that.hash;
        }
        
        @Override
        public int hashCode() {
            return Long.hashCode(hash);
        }
    }
    
    /**
     * Metrics for monitoring
     */
    public static class Metrics {
        private long lookupCount = 0;
        private int nodeCount = 0;
        
        synchronized void incrementLookupCount() {
            lookupCount++;
        }
        
        synchronized void incrementNodeCount() {
            nodeCount++;
        }
        
        synchronized void decrementNodeCount() {
            nodeCount--;
        }
        
        public synchronized long getLookupCount() {
            return lookupCount;
        }
        
        public synchronized int getNodeCount() {
            return nodeCount;
        }
    }
}
```

---

### Usage Example: Distributed Cache

```java
package com.dateng.distributed;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Distributed cache using consistent hashing
 * Similar to Memcached cluster
 */
public class DistributedCache {
    
    /**
     * Cache nodes (servers)
     */
    private static class CacheNode {
        private final String serverId;
        private final Map<String, String> cache;
        private long hitCount = 0;
        private long missCount = 0;
        
        CacheNode(String serverId) {
            this.serverId = serverId;
            this.cache = new ConcurrentHashMap<>();
        }
        
        void put(String key, String value) {
            cache.put(key, value);
        }
        
        String get(String key) {
            String value = cache.get(key);
            if (value != null) {
                hitCount++;
            } else {
                missCount++;
            }
            return value;
        }
        
        void remove(String key) {
            cache.remove(key);
        }
        
        int size() {
            return cache.size();
        }
        
        double getHitRate() {
            long total = hitCount + missCount;
            return total == 0 ? 0 : (double) hitCount / total;
        }
        
        @Override
        public String toString() {
            return serverId;
        }
    }
    
    private final ConsistentHashRing<CacheNode> hashRing;
    private final int replicationFactor;
    
    /**
     * Constructor
     * 
     * @param replicationFactor Number of replicas for each key (default: 3)
     */
    public DistributedCache(int replicationFactor) {
        this.hashRing = new ConsistentHashRing<>(150);
        this.replicationFactor = replicationFactor;
    }
    
    /**
     * Add a cache server
     */
    public void addServer(String serverId) {
        CacheNode node = new CacheNode(serverId);
        hashRing.addNode(node);
        System.out.printf("[DistributedCache] Added server: %s%n", serverId);
    }
    
    /**
     * Remove a cache server
     * All keys on this server are lost (unless replicated)
     */
    public void removeServer(String serverId) {
        // Find the node
        for (CacheNode node : hashRing.getNodes()) {
            if (node.serverId.equals(serverId)) {
                hashRing.removeNode(node);
                System.out.printf("[DistributedCache] Removed server: %s (had %d keys)%n", 
                                  serverId, node.size());
                return;
            }
        }
    }
    
    /**
     * Put key-value into cache
     * With replication for fault tolerance
     */
    public void put(String key, String value) {
        List<CacheNode> nodes = hashRing.getNodes(key, replicationFactor);
        
        for (CacheNode node : nodes) {
            node.put(key, value);
        }
        
        System.out.printf("[DistributedCache] PUT %s = %s (replicated to %d nodes)%n", 
                          key, value, nodes.size());
    }
    
    /**
     * Get value from cache
     * Tries primary node first, falls back to replicas
     */
    public String get(String key) {
        List<CacheNode> nodes = hashRing.getNodes(key, replicationFactor);
        
        for (CacheNode node : nodes) {
            String value = node.get(key);
            if (value != null) {
                return value;
            }
        }
        
        return null;
    }
    
    /**
     * Remove key from cache
     */
    public void remove(String key) {
        List<CacheNode> nodes = hashRing.getNodes(key, replicationFactor);
        
        for (CacheNode node : nodes) {
            node.remove(key);
        }
    }
    
    /**
     * Print cache statistics
     */
    public void printStats() {
        System.out.println("\n=== Cache Statistics ===");
        
        for (CacheNode node : hashRing.getNodes()) {
            System.out.printf("Server %s: %d keys, Hit Rate: %.2f%%%n", 
                              node.serverId, node.size(), node.getHitRate() * 100);
        }
        
        System.out.println();
    }
}
```

---

### Performance Test

```java
package com.dateng.distributed;

import java.util.*;

/**
 * Performance test for consistent hashing
 * Demonstrates key redistribution when nodes are added/removed
 */
public class ConsistentHashingBenchmark {
    
    public static void main(String[] args) {
        System.out.println("=== Consistent Hashing Performance Test ===\n");
        
        // Test 1: Distribution quality
        testDistribution();
        
        // Test 2: Node addition impact
        testNodeAddition();
        
        // Test 3: Distributed cache simulation
        testDistributedCache();
    }
    
    /**
     * Test 1: Distribution quality
     * Verify that keys are evenly distributed across nodes
     */
    private static void testDistribution() {
        System.out.println("Test 1: Distribution Quality");
        System.out.println("-----------------------------");
        
        ConsistentHashRing<String> ring = new ConsistentHashRing<>(150);
        
        // Add 5 servers
        for (int i = 1; i <= 5; i++) {
            ring.addNode("server-" + i);
        }
        
        // Generate 10,000 keys
        List<String> keys = new ArrayList<>();
        for (int i = 0; i < 10000; i++) {
            keys.add("key-" + i);
        }
        
        // Check distribution
        Map<String, Integer> distribution = ring.getDistribution(keys);
        
        System.out.println("\nKey distribution across 5 servers:");
        int total = 0;
        for (Map.Entry<String, Integer> entry : distribution.entrySet()) {
            int count = entry.getValue();
            double percentage = (count * 100.0) / keys.size();
            System.out.printf("%s: %d keys (%.2f%%)%n", entry.getKey(), count, percentage);
            total += count;
        }
        
        // Calculate standard deviation
        double mean = total / (double) distribution.size();
        double variance = 0;
        for (int count : distribution.values()) {
            variance += Math.pow(count - mean, 2);
        }
        double stdDev = Math.sqrt(variance / distribution.size());
        
        System.out.printf("\nMean: %.2f, Std Dev: %.2f (lower is better)%n", mean, stdDev);
        System.out.println("Expected: ~2000 keys per server (20% each)");
        
        // Detect hot spots
        List<String> hotSpots = ring.detectHotSpots(keys);
        if (hotSpots.isEmpty()) {
            System.out.println("✓ No hot spots detected");
        } else {
            System.out.println("⚠ Hot spots detected: " + hotSpots);
        }
        
        System.out.println();
    }
    
    /**
     * Test 2: Node addition impact
     * Measure key redistribution when adding a new node
     */
    private static void testNodeAddition() {
        System.out.println("Test 2: Node Addition Impact");
        System.out.println("-----------------------------");
        
        ConsistentHashRing<String> ring = new ConsistentHashRing<>(150);
        
        // Start with 3 servers
        ring.addNode("server-1");
        ring.addNode("server-2");
        ring.addNode("server-3");
        
        // Generate keys and track their nodes
        int numKeys = 10000;
        Map<String, String> keyToNode = new HashMap<>();
        
        for (int i = 0; i < numKeys; i++) {
            String key = "key-" + i;
            String node = ring.getNode(key);
            keyToNode.put(key, node);
        }
        
        System.out.println("Initial state: 3 servers, 10,000 keys");
        
        // Add a 4th server
        ring.addNode("server-4");
        
        // Count how many keys moved
        int keysRelocated = 0;
        for (Map.Entry<String, String> entry : keyToNode.entrySet()) {
            String key = entry.getKey();
            String oldNode = entry.getValue();
            String newNode = ring.getNode(key);
            
            if (!oldNode.equals(newNode)) {
                keysRelocated++;
            }
        }
        
        double relocatedPercentage = (keysRelocated * 100.0) / numKeys;
        double expectedPercentage = 100.0 / 4; // Ideally ~25%
        
        System.out.printf("\nAfter adding server-4:%n");
        System.out.printf("Keys relocated: %d / %d (%.2f%%)%n", 
                          keysRelocated, numKeys, relocatedPercentage);
        System.out.printf("Expected: ~%.2f%% (1/n where n = num_servers)%n", expectedPercentage);
        
        if (Math.abs(relocatedPercentage - expectedPercentage) < 10) {
            System.out.println("✓ Redistribution is optimal");
        } else {
            System.out.println("⚠ Redistribution is suboptimal");
        }
        
        System.out.println("\nComparison with modulo hashing:");
        System.out.println("Modulo hashing would relocate ~75% of keys (very bad!)");
        
        System.out.println();
    }
    
    /**
     * Test 3: Distributed cache simulation
     */
    private static void testDistributedCache() {
        System.out.println("Test 3: Distributed Cache Simulation");
        System.out.println("-------------------------------------");
        
        DistributedCache cache = new DistributedCache(3); // RF=3
        
        // Add 3 servers
        cache.addServer("cache-1");
        cache.addServer("cache-2");
        cache.addServer("cache-3");
        
        // Populate cache
        System.out.println("\nPopulating cache with 1000 key-value pairs...");
        for (int i = 0; i < 1000; i++) {
            cache.put("user:" + i, "data-" + i);
        }
        
        // Simulate reads
        System.out.println("Simulating 5000 read operations...");
        Random rand = new Random(42);
        for (int i = 0; i < 5000; i++) {
            int userId = rand.nextInt(1000);
            cache.get("user:" + userId);
        }
        
        cache.printStats();
        
        // Simulate node failure
        System.out.println("Simulating server failure (removing cache-2)...");
        cache.removeServer("cache-2");
        
        // Reads should still work (due to replication)
        System.out.println("Attempting reads after failure...");
        int successfulReads = 0;
        for (int i = 0; i < 100; i++) {
            String value = cache.get("user:" + i);
            if (value != null) {
                successfulReads++;
            }
        }
        
        System.out.printf("Successful reads: %d / 100%n", successfulReads);
        
        if (successfulReads >= 95) {
            System.out.println("✓ Replication working as expected");
        }
        
        cache.printStats();
    }
}
```

---

### Real-World Use Cases

#### 1. **Memcached/Redis Cluster**
```java
// Memcached uses consistent hashing to distribute keys across servers
ConsistentHashRing<MemcachedServer> memcached = new ConsistentHashRing<>(160);

// Add servers
memcached.addNode(new MemcachedServer("10.0.1.5:11211"));
memcached.addNode(new MemcachedServer("10.0.1.6:11211"));
memcached.addNode(new MemcachedServer("10.0.1.7:11211"));

// Get/Set operations
MemcachedServer server = memcached.getNode("user:12345:profile");
server.set("user:12345:profile", userData);
```

#### 2. **Cassandra Partitioning**
```
Cassandra uses consistent hashing (with virtual nodes) for partitioning:

- Each node owns a range of tokens on the ring
- Data is distributed based on partition key hash
- Virtual nodes (default: 256) for better balance
- Replication: copies go to next N nodes clockwise
```

#### 3. **DynamoDB**
```
DynamoDB uses consistent hashing internally:

- Partition key is hashed to determine storage node
- Virtual nodes for scalability
- When adding nodes, only affected partitions are moved
```

#### 4. **Content Delivery Network (CDN)**
```java
// Akamai CDN uses consistent hashing for edge server selection
ConsistentHashRing<EdgeServer> cdn = new ConsistentHashRing<>();

// Add edge servers
cdn.addNode(new EdgeServer("edge-1.akamai.net", "us-east-1"));
cdn.addNode(new EdgeServer("edge-2.akamai.net", "us-west-1"));

// Route user request to nearest edge server
EdgeServer edge = cdn.getNode(clientIp + ":" + contentUrl);
```

---

### Performance Characteristics

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Add Node | O(V log N) | O(V) |
| Remove Node | O(V log N) | O(V) |
| Lookup | O(log N) | O(1) |
| Get N Nodes | O(N log N) | O(N) |

Where:
- V = virtual nodes per physical node
- N = total virtual nodes in ring

**Production Recommendations:**
- Virtual nodes: 150-300 (trade-off between distribution and memory)
- Hash function: MD5 or MurmurHash3
- Replication factor: 3 (for fault tolerance)
- Monitor hot spots and rebalance if needed

---

### Interview Problems

**Problem 1:** Implement consistent hashing with bounded load

When some keys are very popular (hot keys), they can overload certain nodes. Implement a variant where each node has a maximum load capacity.

**Solution:**
```java
public T getNodeWithBoundedLoad(String key, Map<T, Integer> currentLoad, int maxLoad) {
    long hash = hash(key);
    Map.Entry<Long, VirtualNode<T>> entry = ring.ceilingEntry(hash);
    
    if (entry == null) {
        entry = ring.firstEntry();
    }
    
    // Try to find a node that's not overloaded
    int attempts = 0;
    while (attempts < ring.size()) {
        T node = entry.getValue().physicalNode;
        
        if (currentLoad.getOrDefault(node, 0) < maxLoad) {
            return node;
        }
        
        // Try next node
        entry = ring.higherEntry(entry.getKey());
        if (entry == null) {
            entry = ring.firstEntry();
        }
        
        attempts++;
    }
    
    // All nodes overloaded, return best effort
    return entry.getValue().physicalNode;
}
```

**Problem 2:** Design a system to migrate data when rebalancing

When adding new nodes, how do you migrate data efficiently?

**Solution Approach:**
1. Create a new hash ring with the new node
2. For each key, compare old node vs new node
3. If different, mark key for migration
4. Migrate in batches to avoid overwhelming network
5. Use double-write during migration (write to both old and new)
6. Switch reads to new node after migration complete

---

## 2. Rate Limiting Algorithms

### The Problem

**Scenario:** You're building an API that handles millions of requests. You need to:
- Prevent abuse (DDoS, scrapers)
- Ensure fair usage
- Protect backend services
- Comply with rate limits of downstream services

**Requirements:**
- Limit users to N requests per time window
- Low latency (<1ms overhead)
- Distributed (work across multiple servers)
- Memory efficient

**Used By:**
- Stripe API: 100 requests per second per API key
- Twitter API: 900 requests per 15 minutes
- GitHub API: 5000 requests per hour
- AWS API Gateway: Configurable rate limits

---

### Algorithm 1: Token Bucket

**Concept:** Tokens are added to a bucket at a fixed rate. Each request consumes one token. If no tokens available, request is rejected.

```
Visualization:

Bucket Capacity: 10 tokens
Refill Rate: 2 tokens/second

Time 0: ●●●●●●●●●● (10 tokens)
  ↓ 5 requests
Time 1: ●●●●● (5 tokens)
  ↓ Wait 1 second, +2 tokens
Time 2: ●●●●●●● (7 tokens)
```

**Advantages:**
- Handles burst traffic (up to bucket capacity)
- Simple to implement
- Memory efficient (just track token count and last refill time)

**Used By:** Amazon API Gateway, Stripe

---

### Implementation (Java)

```java
package com.dateng.ratelimit;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Token Bucket Rate Limiter
 * 
 * Features:
 * - Thread-safe
 * - Handles bursts
 * - Distributed support (with Redis)
 * 
 * @author Principal Data Engineer
 */
public class TokenBucketRateLimiter {
    
    /**
     * Bucket for each user/API key
     */
    private static class TokenBucket {
        private final long capacity;          // Maximum tokens
        private final long refillRate;        // Tokens per second
        private final AtomicLong tokens;      // Current tokens
        private final AtomicLong lastRefill;  // Last refill timestamp (ns)
        
        TokenBucket(long capacity, long refillRate) {
            this.capacity = capacity;
            this.refillRate = refillRate;
            this.tokens = new AtomicLong(capacity);
            this.lastRefill = new AtomicLong(System.nanoTime());
        }
        
        /**
         * Try to consume tokens
         * 
         * @param tokensToConsume Number of tokens to consume
         * @return true if allowed, false if rate limited
         */
        boolean tryConsume(long tokensToConsume) {
            refill();
            
            long currentTokens = tokens.get();
            
            if (currentTokens >= tokensToConsume) {
                // CAS loop to handle concurrent requests
                while (true) {
                    currentTokens = tokens.get();
                    
                    if (currentTokens < tokensToConsume) {
                        return false; // Rate limited
                    }
                    
                    if (tokens.compareAndSet(currentTokens, currentTokens - tokensToConsume)) {
                        return true; // Allowed
                    }
                }
            }
            
            return false; // Not enough tokens
        }
        
        /**
         * Refill tokens based on elapsed time
         */
        private void refill() {
            long now = System.nanoTime();
            long lastRefillTime = lastRefill.get();
            
            long elapsedNanos = now - lastRefillTime;
            long tokensToAdd = (elapsedNanos * refillRate) / TimeUnit.SECONDS.toNanos(1);
            
            if (tokensToAdd > 0) {
                // CAS loop to update tokens and lastRefill atomically
                while (true) {
                    long currentTokens = tokens.get();
                    long newTokens = Math.min(capacity, currentTokens + tokensToAdd);
                    
                    if (tokens.compareAndSet(currentTokens, newTokens)) {
                        lastRefill.compareAndSet(lastRefillTime, now);
                        break;
                    }
                }
            }
        }
        
        /**
         * Get current token count (for monitoring)
         */
        long getAvailableTokens() {
            refill();
            return tokens.get();
        }
    }
    
    private final ConcurrentHashMap<String, TokenBucket> buckets;
    private final long capacity;
    private final long refillRate;
    
    /**
     * Constructor
     * 
     * @param capacity Maximum tokens (burst size)
     * @param refillRate Tokens added per second (sustained rate)
     */
    public TokenBucketRateLimiter(long capacity, long refillRate) {
        this.buckets = new ConcurrentHashMap<>();
        this.capacity = capacity;
        this.refillRate = refillRate;
    }
    
    /**
     * Check if request is allowed
     * 
     * @param userId User identifier (API key, user ID, IP address)
     * @return true if allowed, false if rate limited
     */
    public boolean allowRequest(String userId) {
        return allowRequest(userId, 1);
    }
    
    /**
     * Check if request is allowed (with custom token cost)
     * 
     * @param userId User identifier
     * @param cost Number of tokens to consume (for weighted rate limiting)
     * @return true if allowed, false if rate limited
     */
    public boolean allowRequest(String userId, long cost) {
        TokenBucket bucket = buckets.computeIfAbsent(userId, 
            k -> new TokenBucket(capacity, refillRate));
        
        return bucket.tryConsume(cost);
    }
    
    /**
     * Get remaining tokens for user (for monitoring)
     */
    public long getRemainingTokens(String userId) {
        TokenBucket bucket = buckets.get(userId);
        return bucket == null ? capacity : bucket.getAvailableTokens();
    }
    
    /**
     * Reset bucket for user (for testing)
     */
    public void reset(String userId) {
        buckets.remove(userId);
    }
}
```

---

### Algorithm 2: Sliding Window Log

**Concept:** Keep a log of all request timestamps. Count requests in the last N seconds.

```
Time window: 10 seconds
Current time: 15

Request log:
[6, 7, 8, 12, 13, 14, 15]
         |______________|
         Last 10 seconds: 5 requests

If limit is 10 requests/10s → ALLOWED
If limit is 4 requests/10s → DENIED
```

**Advantages:**
- Exact rate limiting (no approximation)
- Easy to understand

**Disadvantages:**
- Memory intensive (store all timestamps)
- O(N) lookup time

**Used By:** Systems requiring exact rate limiting

---

### Implementation (Java)

```java
package com.dateng.ratelimit;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentLinkedDeque;

/**
 * Sliding Window Log Rate Limiter
 * 
 * Exact rate limiting by tracking all request timestamps
 */
public class SlidingWindowLogRateLimiter {
    
    private static class RequestLog {
        private final ConcurrentLinkedDeque<Long> timestamps;
        
        RequestLog() {
            this.timestamps = new ConcurrentLinkedDeque<>();
        }
        
        /**
         * Try to allow a request
         * 
         * @param limit Maximum requests allowed
         * @param windowMs Time window in milliseconds
         * @return true if allowed, false if rate limited
         */
        boolean tryAllow(int limit, long windowMs) {
            long now = System.currentTimeMillis();
            long windowStart = now - windowMs;
            
            // Remove old timestamps outside the window
            while (!timestamps.isEmpty() && timestamps.peekFirst() < windowStart) {
                timestamps.pollFirst();
            }
            
            // Check if under limit
            if (timestamps.size() < limit) {
                timestamps.addLast(now);
                return true;
            }
            
            return false;
        }
        
        int getRequestCount(long windowMs) {
            long now = System.currentTimeMillis();
            long windowStart = now - windowMs;
            
            // Remove old timestamps
            while (!timestamps.isEmpty() && timestamps.peekFirst() < windowStart) {
                timestamps.pollFirst();
            }
            
            return timestamps.size();
        }
    }
    
    private final ConcurrentHashMap<String, RequestLog> logs;
    private final int limit;
    private final long windowMs;
    
    /**
     * Constructor
     * 
     * @param limit Maximum requests per window
     * @param windowMs Time window in milliseconds
     */
    public SlidingWindowLogRateLimiter(int limit, long windowMs) {
        this.logs = new ConcurrentHashMap<>();
        this.limit = limit;
        this.windowMs = windowMs;
    }
    
    /**
     * Check if request is allowed
     */
    public boolean allowRequest(String userId) {
        RequestLog log = logs.computeIfAbsent(userId, k -> new RequestLog());
        return log.tryAllow(limit, windowMs);
    }
    
    /**
     * Get request count in current window
     */
    public int getRequestCount(String userId) {
        RequestLog log = logs.get(userId);
        return log == null ? 0 : log.getRequestCount(windowMs);
    }
}
```

---

### Algorithm 3: Sliding Window Counter

**Concept:** Hybrid approach combining fixed window counters with weighted calculation.

```
Window: 1 minute (60 seconds)
Current time: 15 seconds into minute 2

Previous window (minute 1): 80 requests
Current window (minute 2): 30 requests

Estimated requests in last 60 seconds:
= 80 * (45/60) + 30
= 60 + 30
= 90 requests
```

**Advantages:**
- Memory efficient (just 2 counters)
- Smooth rate limiting (no reset spike)
- O(1) lookup

**Disadvantages:**
- Approximate (not exact)

**Used By:** Redis-based rate limiters, Cloudflare

---

### Implementation (Java)

```java
package com.dateng.ratelimit;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Sliding Window Counter Rate Limiter
 * 
 * Memory-efficient rate limiting with smooth transitions
 */
public class SlidingWindowCounterRateLimiter {
    
    private static class WindowCounter {
        private final AtomicInteger previousCount;
        private final AtomicInteger currentCount;
        private final AtomicLong previousWindowStart;
        private final AtomicLong currentWindowStart;
        private final long windowSizeMs;
        
        WindowCounter(long windowSizeMs) {
            this.windowSizeMs = windowSizeMs;
            long now = System.currentTimeMillis();
            this.previousCount = new AtomicInteger(0);
            this.currentCount = new AtomicInteger(0);
            this.previousWindowStart = new AtomicLong(now - windowSizeMs);
            this.currentWindowStart = new AtomicLong(now);
        }
        
        /**
         * Try to allow a request
         * 
         * @param limit Maximum requests per window
         * @return true if allowed, false if rate limited
         */
        boolean tryAllow(int limit) {
            long now = System.currentTimeMillis();
            slideWindow(now);
            
            double estimatedCount = getEstimatedCount(now);
            
            if (estimatedCount < limit) {
                currentCount.incrementAndGet();
                return true;
            }
            
            return false;
        }
        
        /**
         * Slide the window if needed
         */
        private void slideWindow(long now) {
            long currentStart = currentWindowStart.get();
            
            // Check if we need to slide to a new window
            if (now - currentStart >= windowSizeMs) {
                // Move current to previous
                previousCount.set(currentCount.get());
                previousWindowStart.set(currentStart);
                
                // Reset current
                currentCount.set(0);
                currentWindowStart.set(now);
            }
        }
        
        /**
         * Calculate estimated request count in sliding window
         */
        private double getEstimatedCount(long now) {
            long currentStart = currentWindowStart.get();
            long previousStart = previousWindowStart.get();
            
            // Time elapsed in current window
            long elapsedInCurrent = now - currentStart;
            
            // Weight of previous window
            double previousWeight = Math.max(0, (windowSizeMs - elapsedInCurrent) / (double) windowSizeMs);
            
            // Estimated count = weighted previous + current
            return previousCount.get() * previousWeight + currentCount.get();
        }
        
        double getEstimatedCount() {
            return getEstimatedCount(System.currentTimeMillis());
        }
    }
    
    private final ConcurrentHashMap<String, WindowCounter> counters;
    private final int limit;
    private final long windowSizeMs;
    
    /**
     * Constructor
     * 
     * @param limit Maximum requests per window
     * @param windowSizeMs Time window in milliseconds
     */
    public SlidingWindowCounterRateLimiter(int limit, long windowSizeMs) {
        this.counters = new ConcurrentHashMap<>();
        this.limit = limit;
        this.windowSizeMs = windowSizeMs;
    }
    
    /**
     * Check if request is allowed
     */
    public boolean allowRequest(String userId) {
        WindowCounter counter = counters.computeIfAbsent(userId, 
            k -> new WindowCounter(windowSizeMs));
        
        return counter.tryAllow(limit);
    }
    
    /**
     * Get estimated request count
     */
    public double getRequestCount(String userId) {
        WindowCounter counter = counters.get(userId);
        return counter == null ? 0 : counter.getEstimatedCount();
    }
}
```

---

### Algorithm 4: Distributed Rate Limiting with Redis

**Challenge:** Previous implementations only work on a single server. How to rate limit across multiple servers?

**Solution:** Use Redis as a centralized counter store.

---

### Implementation (Java with Redis)

```java
package com.dateng.ratelimit;

import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.Transaction;

import java.util.List;

/**
 * Distributed Rate Limiter using Redis
 * 
 * Uses Redis Sorted Sets to implement sliding window log
 * Works across multiple application servers
 */
public class RedisRateLimiter {
    
    private final JedisPool jedisPool;
    private final int limit;
    private final long windowMs;
    
    /**
     * Constructor
     * 
     * @param jedisPool Redis connection pool
     * @param limit Maximum requests per window
     * @param windowMs Time window in milliseconds
     */
    public RedisRateLimiter(JedisPool jedisPool, int limit, long windowMs) {
        this.jedisPool = jedisPool;
        this.limit = limit;
        this.windowMs = windowMs;
    }
    
    /**
     * Check if request is allowed using Lua script for atomicity
     * 
     * Redis Lua script ensures atomic execution
     */
    public boolean allowRequest(String userId) {
        try (Jedis jedis = jedisPool.getResource()) {
            long now = System.currentTimeMillis();
            long windowStart = now - windowMs;
            
            String key = "rate_limit:" + userId;
            
            // Lua script for atomic rate limit check
            String luaScript = 
                "local key = KEYS[1]\n" +
                "local now = tonumber(ARGV[1])\n" +
                "local window_start = tonumber(ARGV[2])\n" +
                "local limit = tonumber(ARGV[3])\n" +
                "\n" +
                "-- Remove old entries\n" +
                "redis.call('ZREMRANGEBYSCORE', key, '-inf', window_start)\n" +
                "\n" +
                "-- Count current entries\n" +
                "local count = redis.call('ZCARD', key)\n" +
                "\n" +
                "if count < limit then\n" +
                "  -- Add new entry\n" +
                "  redis.call('ZADD', key, now, now)\n" +
                "  -- Set expiration\n" +
                "  redis.call('EXPIRE', key, math.ceil(ARGV[4] / 1000))\n" +
                "  return 1\n" +
                "else\n" +
                "  return 0\n" +
                "end";
            
            Object result = jedis.eval(
                luaScript,
                1,
                key,
                String.valueOf(now),
                String.valueOf(windowStart),
                String.valueOf(limit),
                String.valueOf(windowMs)
            );
            
            return result != null && (Long) result == 1L;
        }
    }
    
    /**
     * Get current request count for user
     */
    public long getRequestCount(String userId) {
        try (Jedis jedis = jedisPool.getResource()) {
            long now = System.currentTimeMillis();
            long windowStart = now - windowMs;
            
            String key = "rate_limit:" + userId;
            
            // Remove old entries
            jedis.zremrangeByScore(key, "-inf", String.valueOf(windowStart));
            
            // Count remaining entries
            return jedis.zcard(key);
        }
    }
    
    /**
     * Alternative: Token bucket implementation using Redis
     */
    public boolean allowRequestTokenBucket(String userId) {
        try (Jedis jedis = jedisPool.getResource()) {
            String key = "rate_limit:token:" + userId;
            
            // Lua script for token bucket
            String luaScript =
                "local key = KEYS[1]\n" +
                "local capacity = tonumber(ARGV[1])\n" +
                "local refill_rate = tonumber(ARGV[2])\n" +
                "local now = tonumber(ARGV[3])\n" +
                "\n" +
                "local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')\n" +
                "local tokens = tonumber(bucket[1]) or capacity\n" +
                "local last_refill = tonumber(bucket[2]) or now\n" +
                "\n" +
                "-- Refill tokens\n" +
                "local elapsed = now - last_refill\n" +
                "local tokens_to_add = math.floor(elapsed * refill_rate / 1000)\n" +
                "tokens = math.min(capacity, tokens + tokens_to_add)\n" +
                "\n" +
                "if tokens >= 1 then\n" +
                "  tokens = tokens - 1\n" +
                "  redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)\n" +
                "  redis.call('EXPIRE', key, 3600)\n" +
                "  return 1\n" +
                "else\n" +
                "  return 0\n" +
                "end";
            
            Object result = jedis.eval(
                luaScript,
                1,
                key,
                String.valueOf(100),        // capacity
                String.valueOf(10),         // refill_rate (tokens per second)
                String.valueOf(System.currentTimeMillis())
            );
            
            return result != null && (Long) result == 1L;
        }
    }
}
```

---

### Performance Comparison

| Algorithm | Memory | Accuracy | Distributed | Burst Handling |
|-----------|--------|----------|-------------|----------------|
| Token Bucket | O(1) | Approximate | Yes (with Redis) | ✓ Excellent |
| Sliding Window Log | O(N) | Exact | Yes | ✓ Good |
| Sliding Window Counter | O(1) | Approximate | Yes | ✓ Good |
| Fixed Window | O(1) | Poor | Yes | ✗ Poor |

**Recommendation:**
- **API Gateway:** Token Bucket (handles bursts well)
- **Fair usage:** Sliding Window Counter (smooth limits)
- **Exact limits:** Sliding Window Log (audit/compliance)

---

### Real-World Examples

#### 1. Stripe API Rate Limiter
```java
// Stripe uses token bucket with multiple limits:
// - Per second: 100 requests/second (burst)
// - Per hour: 1000 requests/hour (sustained)

public class StripeRateLimiter {
    private final TokenBucketRateLimiter perSecond;
    private final TokenBucketRateLimiter perHour;
    
    public StripeRateLimiter() {
        this.perSecond = new TokenBucketRateLimiter(100, 100); // 100 capacity, 100/s refill
        this.perHour = new TokenBucketRateLimiter(1000, 1000 / 3600.0); // 1000 capacity, ~0.28/s refill
    }
    
    public boolean allowRequest(String apiKey) {
        return perSecond.allowRequest(apiKey) && perHour.allowRequest(apiKey);
    }
}
```

#### 2. GitHub API Rate Limiter
```java
// GitHub: 5000 requests per hour per user
// Returns rate limit info in headers:
// X-RateLimit-Limit: 5000
// X-RateLimit-Remaining: 4999
// X-RateLimit-Reset: 1618884000

public class GitHubRateLimiter {
    private final SlidingWindowCounterRateLimiter limiter;
    
    public GitHubRateLimiter() {
        this.limiter = new SlidingWindowCounterRateLimiter(5000, 3600_000); // 5000/hour
    }
    
    public RateLimitResponse checkLimit(String userId) {
        boolean allowed = limiter.allowRequest(userId);
        double remaining = 5000 - limiter.getRequestCount(userId);
        long resetTime = System.currentTimeMillis() + 3600_000;
        
        return new RateLimitResponse(allowed, 5000, (int) remaining, resetTime);
    }
    
    static class RateLimitResponse {
        final boolean allowed;
        final int limit;
        final int remaining;
        final long resetTime;
        
        RateLimitResponse(boolean allowed, int limit, int remaining, long resetTime) {
            this.allowed = allowed;
            this.limit = limit;
            this.remaining = remaining;
            this.resetTime = resetTime;
        }
    }
}
```

---

### Advanced: Hierarchical Rate Limiting

Rate limit at multiple levels:
- Per user
- Per API endpoint
- Per region
- Global

```java
public class HierarchicalRateLimiter {
    private final TokenBucketRateLimiter userLimiter;      // 100/s per user
    private final TokenBucketRateLimiter endpointLimiter;  // 10000/s per endpoint
    private final TokenBucketRateLimiter regionLimiter;    // 100000/s per region
    private final TokenBucketRateLimiter globalLimiter;    // 1000000/s global
    
    public HierarchicalRateLimiter() {
        this.userLimiter = new TokenBucketRateLimiter(100, 100);
        this.endpointLimiter = new TokenBucketRateLimiter(10000, 10000);
        this.regionLimiter = new TokenBucketRateLimiter(100000, 100000);
        this.globalLimiter = new TokenBucketRateLimiter(1000000, 1000000);
    }
    
    public boolean allowRequest(String userId, String endpoint, String region) {
        // Check all levels
        return globalLimiter.allowRequest("global") &&
               regionLimiter.allowRequest(region) &&
               endpointLimiter.allowRequest(endpoint) &&
               userLimiter.allowRequest(userId);
    }
}
```

---

### Interview Problems

**Problem 1:** Design a rate limiter that allows bursts but prevents sustained abuse.

**Solution:** Use token bucket with a smaller capacity but higher refill rate.
```java
// Allow bursts up to 50 requests, but sustained rate of 10/s
TokenBucketRateLimiter limiter = new TokenBucketRateLimiter(50, 10);
```

**Problem 2:** How to handle rate limiting in a multi-region deployment?

**Solution:** 
- Option 1: Regional rate limits (each region independent)
- Option 2: Global rate limit (use Redis with geo-replication)
- Option 3: Hybrid (soft limit per region, hard limit global)

**Problem 3:** Design a rate limiter that gives premium users higher limits.

**Solution:**
```java
public class TieredRateLimiter {
    private final Map<String, TokenBucketRateLimiter> limiters = new ConcurrentHashMap<>();
    
    public boolean allowRequest(String userId, UserTier tier) {
        String key = userId + ":" + tier;
        
        TokenBucketRateLimiter limiter = limiters.computeIfAbsent(key, k -> {
            switch (tier) {
                case FREE:
                    return new TokenBucketRateLimiter(10, 10);    // 10/s
                case PREMIUM:
                    return new TokenBucketRateLimiter(100, 100);  // 100/s
                case ENTERPRISE:
                    return new TokenBucketRateLimiter(1000, 1000); // 1000/s
                default:
                    return new TokenBucketRateLimiter(10, 10);
            }
        });
        
        return limiter.allowRequest(userId);
    }
    
    enum UserTier {
        FREE, PREMIUM, ENTERPRISE
    }
}
```

---

**[Continue to Part 2 for Bloom Filters, Count-Min Sketch, HyperLogLog, External Sort, and Distributed Aggregation...]**
