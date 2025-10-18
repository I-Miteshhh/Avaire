# Distributed Cache - Production Implementation

**Target Scale:** Support **10M+ QPS** (queries per second) with **sub-millisecond latency**

---

## Table of Contents
1. [Problem Statement](#1-problem-statement)
2. [Requirements](#2-requirements)
3. [Cache Eviction Policies](#3-cache-eviction-policies)
4. [Consistency Models](#4-consistency-models)
5. [Architecture](#5-architecture)
6. [Implementation](#6-implementation)
7. [Advanced Features](#7-advanced-features)

---

## 1. Problem Statement

### What is a Distributed Cache?

A distributed cache is an in-memory data store that spans multiple servers to:
- **Reduce latency:** Serve data from memory (μs) vs disk (ms)
- **Reduce load:** Offload database queries
- **Scale horizontally:** Add more cache nodes as needed
- **Improve availability:** Replicate data across nodes

**Real-World Examples:**
- **Memcached:** Used by Facebook, Twitter (handles 1 million ops/sec per server)
- **Redis:** Used by Twitter, GitHub, Instagram (5M ops/sec single-threaded)
- **Amazon ElastiCache:** Fully managed cache service (millions of ops/sec)

---

### Use Cases

1. **Session Storage:** Store user sessions in distributed cache
2. **Database Query Caching:** Cache expensive database queries
3. **API Response Caching:** Cache API responses to reduce backend load
4. **Rate Limiting:** Store request counters
5. **Leaderboards:** Real-time gaming leaderboards using sorted sets
6. **Message Queues:** Pub/sub messaging

---

## 2. Requirements

### Functional Requirements

1. **Core Operations:**
   - `Get(key)` - Retrieve value by key
   - `Put(key, value, ttl)` - Store key-value pair with TTL
   - `Delete(key)` - Remove key
   - `Exists(key)` - Check if key exists
   
2. **Advanced Operations:**
   - Batch operations: `MGet`, `MSet`
   - Atomic operations: `Increment`, `Decrement`
   - Expiration: TTL-based eviction

3. **Data Structures:**
   - Strings
   - Lists
   - Sets
   - Sorted Sets
   - Hashes

4. **Distribution:**
   - Consistent hashing for key distribution
   - Replication for high availability
   - Sharding for horizontal scaling

### Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Latency (Read) | <1ms P99 |
| Latency (Write) | <2ms P99 |
| Throughput | 10M+ ops/sec (cluster) |
| Availability | 99.99% |
| Consistency | Eventually consistent |
| Memory Efficiency | >80% utilization |

### Scale Estimates

```
Assumptions:
- 1 billion cached items
- Average item size: 1 KB
- Total cache size: 1 TB
- Read:Write ratio: 90:10
- QPS: 10 million

Cache nodes (128 GB RAM each): 1 TB / 128 GB = 8 nodes
Replication factor: 3x
Total nodes: 8 × 3 = 24 nodes

Per-node QPS: 10M / 8 = 1.25M ops/sec
```

---

## 3. Cache Eviction Policies

### 3.1 LRU (Least Recently Used)

**How it works:** Evict the item that was least recently accessed

**Implementation:** Doubly linked list + HashMap

```
Access pattern: A, B, C, D, A, E (capacity: 3)

Step 1: A          [A]
Step 2: A, B       [A, B]
Step 3: A, B, C    [A, B, C]
Step 4: A, B, C, D [B, C, D]  (A evicted)
Step 5: B, C, D, A [C, D, A]  (B evicted)
Step 6: C, D, A, E [D, A, E]  (C evicted)
```

**Pros:** Simple, effective for temporal locality  
**Cons:** Doesn't consider access frequency

**Best for:** Web caches, database query caches

---

### 3.2 LFU (Least Frequently Used)

**How it works:** Evict the item with lowest access frequency

```
Access pattern: A(3x), B(2x), C(1x), D(1x)
Capacity: 3

Cache: [A(3), B(2), C(1)]
New item D → Evict C (lowest frequency)
Result: [A(3), B(2), D(1)]
```

**Pros:** Good for skewed workloads (80-20 rule)  
**Cons:** Cold start problem (new items have low frequency)

**Solution:** Use window-LFU or decay counters over time

---

### 3.3 FIFO (First In First Out)

**How it works:** Evict oldest item (by insertion time)

**Pros:** Simple, O(1) eviction  
**Cons:** Doesn't consider access patterns

**Best for:** Stream processing, message queues

---

### 3.4 TTL-Based Eviction

**How it works:** Items expire after fixed time

```go
Put("session:123", userData, ttl=3600) // 1 hour
Get("session:123") after 3601 seconds → nil (expired)
```

**Implementation:** Min-heap of expiration times + background thread

**Best for:** Session storage, temporary data

---

### 3.5 Random Eviction

**How it works:** Evict random item

**Pros:** Simplest, O(1), no overhead  
**Cons:** Poor hit rate

**Best for:** When all items have equal importance

---

## 4. Consistency Models

### 4.1 Strong Consistency

**Guarantee:** All nodes see the same data at the same time

**Implementation:** Synchronous replication (write to all replicas before ACK)

```
Client → Master → [ Replica1, Replica2, Replica3 ] → ACK to Client
         ↓ wait for all replicas
```

**Pros:** No stale reads  
**Cons:** High latency (wait for slowest replica)

**Best for:** Financial systems, inventory management

---

### 4.2 Eventual Consistency

**Guarantee:** All nodes will eventually converge to same value

**Implementation:** Asynchronous replication

```
Client → Master → ACK to Client
         ↓ async
         [ Replica1, Replica2, Replica3 ]
```

**Pros:** Low latency, high availability  
**Cons:** Stale reads possible

**Best for:** Social media feeds, comments, view counts

---

### 4.3 Read-Your-Writes Consistency

**Guarantee:** User always sees their own writes

**Implementation:** Route reads from same user to same replica

```
User A writes to Master → Replicates to Replica1
User A reads → Route to Replica1 (guaranteed to have write)
User B reads → Route to any replica (may see old data)
```

**Best for:** User profile updates, shopping carts

---

## 5. Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                     Load Balancer / Router                   │
│                   (Consistent Hashing)                       │
└────────────┬───────────────┬───────────────┬────────────────┘
             │               │               │
    ┌────────▼──────┐ ┌─────▼──────┐ ┌──────▼─────┐
    │ Cache Shard 1 │ │Cache Shard 2│ │Cache Shard 3│
    │  (Master)     │ │  (Master)   │ │  (Master)  │
    │   128 GB      │ │   128 GB    │ │   128 GB   │
    └────────┬──────┘ └─────┬──────┘ └──────┬─────┘
             │               │               │
      ┌──────┴──────┐  ┌────┴────┐    ┌─────┴─────┐
      ▼      ▼      ▼  ▼    ▼    ▼    ▼     ▼     ▼
    [R1]  [R2]  [R3] [R1] [R2] [R3]  [R1]  [R2]  [R3]
    Replicas (async replication)
```

### Components

1. **Client Library:** Implements consistent hashing, connection pooling
2. **Cache Nodes:** Store data in memory (RAM)
3. **Replication:** Async replication to replicas for availability
4. **Monitoring:** Track hit rate, latency, memory usage

---

## 6. Implementation

### 6.1 LRU Cache (Go)

```go
// cache/lru.go
package cache

import (
    "container/list"
    "sync"
)

type LRUCache struct {
    capacity int
    mu       sync.RWMutex
    items    map[string]*list.Element
    lruList  *list.List
}

type entry struct {
    key   string
    value interface{}
}

func NewLRUCache(capacity int) *LRUCache {
    return &LRUCache{
        capacity: capacity,
        items:    make(map[string]*list.Element),
        lruList:  list.New(),
    }
}

func (lru *LRUCache) Get(key string) (interface{}, bool) {
    lru.mu.Lock()
    defer lru.mu.Unlock()
    
    if elem, ok := lru.items[key]; ok {
        // Move to front (most recently used)
        lru.lruList.MoveToFront(elem)
        return elem.Value.(*entry).value, true
    }
    
    return nil, false
}

func (lru *LRUCache) Put(key string, value interface{}) {
    lru.mu.Lock()
    defer lru.mu.Unlock()
    
    // Update existing
    if elem, ok := lru.items[key]; ok {
        lru.lruList.MoveToFront(elem)
        elem.Value.(*entry).value = value
        return
    }
    
    // Add new entry
    elem := lru.lruList.PushFront(&entry{key, value})
    lru.items[key] = elem
    
    // Evict if over capacity
    if lru.lruList.Len() > lru.capacity {
        lru.evict()
    }
}

func (lru *LRUCache) evict() {
    elem := lru.lruList.Back()
    if elem != nil {
        lru.lruList.Remove(elem)
        delete(lru.items, elem.Value.(*entry).key)
    }
}

func (lru *LRUCache) Delete(key string) {
    lru.mu.Lock()
    defer lru.mu.Unlock()
    
    if elem, ok := lru.items[key]; ok {
        lru.lruList.Remove(elem)
        delete(lru.items, key)
    }
}

func (lru *LRUCache) Len() int {
    lru.mu.RLock()
    defer lru.mu.RUnlock()
    return lru.lruList.Len()
}
```

**Time Complexity:**
- Get: O(1)
- Put: O(1)
- Delete: O(1)
- Space: O(n)

---

### 6.2 LFU Cache (Go)

```go
// cache/lfu.go
package cache

import (
    "container/heap"
    "sync"
)

type LFUCache struct {
    capacity int
    mu       sync.RWMutex
    items    map[string]*lfuEntry
    minFreq  int
    freqMap  map[int]*list.List  // frequency → list of entries
}

type lfuEntry struct {
    key   string
    value interface{}
    freq  int
}

func NewLFUCache(capacity int) *LFUCache {
    return &LFUCache{
        capacity: capacity,
        items:    make(map[string]*lfuEntry),
        freqMap:  make(map[int]*list.List),
    }
}

func (lfu *LFUCache) Get(key string) (interface{}, bool) {
    lfu.mu.Lock()
    defer lfu.mu.Unlock()
    
    entry, ok := lfu.items[key]
    if !ok {
        return nil, false
    }
    
    // Increment frequency
    lfu.incrementFreq(entry)
    
    return entry.value, true
}

func (lfu *LFUCache) Put(key string, value interface{}) {
    lfu.mu.Lock()
    defer lfu.mu.Unlock()
    
    if lfu.capacity == 0 {
        return
    }
    
    // Update existing
    if entry, ok := lfu.items[key]; ok {
        entry.value = value
        lfu.incrementFreq(entry)
        return
    }
    
    // Evict if at capacity
    if len(lfu.items) >= lfu.capacity {
        lfu.evict()
    }
    
    // Add new entry
    entry := &lfuEntry{
        key:   key,
        value: value,
        freq:  1,
    }
    lfu.items[key] = entry
    
    if lfu.freqMap[1] == nil {
        lfu.freqMap[1] = list.New()
    }
    lfu.freqMap[1].PushFront(entry)
    lfu.minFreq = 1
}

func (lfu *LFUCache) incrementFreq(entry *lfuEntry) {
    freq := entry.freq
    
    // Remove from old frequency list
    lfu.freqMap[freq].Remove(entry)
    if lfu.freqMap[freq].Len() == 0 && freq == lfu.minFreq {
        lfu.minFreq++
    }
    
    // Add to new frequency list
    entry.freq++
    if lfu.freqMap[entry.freq] == nil {
        lfu.freqMap[entry.freq] = list.New()
    }
    lfu.freqMap[entry.freq].PushFront(entry)
}

func (lfu *LFUCache) evict() {
    // Evict least frequently used (and least recently used if tied)
    freqList := lfu.freqMap[lfu.minFreq]
    if freqList == nil || freqList.Len() == 0 {
        return
    }
    
    elem := freqList.Back()
    entry := elem.Value.(*lfuEntry)
    freqList.Remove(elem)
    delete(lfu.items, entry.key)
}
```

---

### 6.3 TTL-Based Cache (Go)

```go
// cache/ttl_cache.go
package cache

import (
    "sync"
    "time"
)

type TTLCache struct {
    mu    sync.RWMutex
    items map[string]*ttlEntry
}

type ttlEntry struct {
    value      interface{}
    expiration time.Time
}

func NewTTLCache() *TTLCache {
    tc := &TTLCache{
        items: make(map[string]*ttlEntry),
    }
    
    // Start background cleanup
    go tc.cleanup()
    
    return tc
}

func (tc *TTLCache) Get(key string) (interface{}, bool) {
    tc.mu.RLock()
    defer tc.mu.RUnlock()
    
    entry, ok := tc.items[key]
    if !ok {
        return nil, false
    }
    
    // Check expiration
    if time.Now().After(entry.expiration) {
        return nil, false
    }
    
    return entry.value, true
}

func (tc *TTLCache) Put(key string, value interface{}, ttl time.Duration) {
    tc.mu.Lock()
    defer tc.mu.Unlock()
    
    tc.items[key] = &ttlEntry{
        value:      value,
        expiration: time.Now().Add(ttl),
    }
}

func (tc *TTLCache) Delete(key string) {
    tc.mu.Lock()
    defer tc.mu.Unlock()
    delete(tc.items, key)
}

func (tc *TTLCache) cleanup() {
    ticker := time.NewTicker(time.Minute)
    defer ticker.Stop()
    
    for range ticker.C {
        tc.mu.Lock()
        now := time.Now()
        for key, entry := range tc.items {
            if now.After(entry.expiration) {
                delete(tc.items, key)
            }
        }
        tc.mu.Unlock()
    }
}
```

---

### 6.4 Consistent Hashing for Distribution

```go
// cache/consistent_hash.go
package cache

import (
    "crypto/md5"
    "fmt"
    "sort"
    "sync"
)

type ConsistentHash struct {
    mu       sync.RWMutex
    ring     []int        // Sorted hash ring
    nodes    map[int]string  // hash → node
    vnodes   int          // Virtual nodes per physical node
}

func NewConsistentHash(vnodes int) *ConsistentHash {
    return &ConsistentHash{
        nodes:  make(map[int]string),
        vnodes: vnodes,
    }
}

func (ch *ConsistentHash) AddNode(node string) {
    ch.mu.Lock()
    defer ch.mu.Unlock()
    
    // Add virtual nodes
    for i := 0; i < ch.vnodes; i++ {
        hash := ch.hash(fmt.Sprintf("%s:%d", node, i))
        ch.ring = append(ch.ring, hash)
        ch.nodes[hash] = node
    }
    
    sort.Ints(ch.ring)
}

func (ch *ConsistentHash) RemoveNode(node string) {
    ch.mu.Lock()
    defer ch.mu.Unlock()
    
    // Remove virtual nodes
    for i := 0; i < ch.vnodes; i++ {
        hash := ch.hash(fmt.Sprintf("%s:%d", node, i))
        idx := sort.SearchInts(ch.ring, hash)
        if idx < len(ch.ring) && ch.ring[idx] == hash {
            ch.ring = append(ch.ring[:idx], ch.ring[idx+1:]...)
        }
        delete(ch.nodes, hash)
    }
}

func (ch *ConsistentHash) GetNode(key string) string {
    ch.mu.RLock()
    defer ch.mu.RUnlock()
    
    if len(ch.ring) == 0 {
        return ""
    }
    
    hash := ch.hash(key)
    idx := sort.Search(len(ch.ring), func(i int) bool {
        return ch.ring[i] >= hash
    })
    
    if idx == len(ch.ring) {
        idx = 0
    }
    
    return ch.nodes[ch.ring[idx]]
}

func (ch *ConsistentHash) hash(key string) int {
    h := md5.Sum([]byte(key))
    return int(h[0])<<24 | int(h[1])<<16 | int(h[2])<<8 | int(h[3])
}
```

---

**Continued in next part...**
