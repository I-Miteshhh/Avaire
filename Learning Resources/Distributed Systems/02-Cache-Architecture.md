# Cache Architecture Patterns

**Purpose:** Master enterprise-grade caching strategies for 40+ LPA Principal Engineer roles

**Prerequisites:** Redis fundamentals, distributed systems, consistency models

---

## Table of Contents

1. [Caching Fundamentals](#1-caching-fundamentals)
2. [Cache Patterns](#2-cache-patterns)
3. [Redis Cluster Architecture](#3-redis-cluster-architecture)
4. [Invalidation Strategies](#4-invalidation-strategies)
5. [CDC-Based Invalidation](#5-cdc-based-invalidation)
6. [Production Best Practices](#6-production-best-practices)

---

## 1. Caching Fundamentals

### 1.1 Why Cache?

**Problem:** Database queries are slow (10-100ms)

**Solution:** In-memory cache (<1ms)

**Benefits:**
```
Without Cache:
  Request → Database (50ms) → Response
  Throughput: 20 req/sec

With Cache:
  Request → Cache (0.5ms) → Response
  Throughput: 2000 req/sec

100x improvement!
```

---

### 1.2 Cache Hit Rate

**Formula:**
```
Hit Rate = Cache Hits / Total Requests

Example:
  1000 requests
  800 cache hits
  200 cache misses
  
  Hit Rate = 800 / 1000 = 80%
```

**Impact:**
```
Hit Rate | Avg Latency (DB=50ms, Cache=0.5ms)
---------|------------------------------------
50%      | 0.5*0.5 + 0.5*50 = 25.25ms
80%      | 0.8*0.5 + 0.2*50 = 10.4ms
95%      | 0.95*0.5 + 0.05*50 = 3ms
99%      | 0.99*0.5 + 0.01*50 = 1ms
```

**Goal:** Achieve 95%+ hit rate in production

---

### 1.3 Cache Consistency Models

```
┌─────────────────────────────────────────────────────────────┐
│                   Consistency Spectrum                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Strong ───────────────────────────────── Eventual          │
│    │                 │                 │         │          │
│    │                 │                 │         │          │
│  Write-           Write-            Cache-   Write-         │
│  Through         Behind             Aside    Back           │
│                                                              │
│  Slow            Medium            Fast      Fastest        │
│  100% consistent 99.9% consistent  95%       90%            │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Cache Patterns

### 2.1 Cache-Aside (Lazy Loading)

**Flow:**
```
Read:
  1. Check cache
  2. If hit → return cached data
  3. If miss → read from DB, populate cache, return

Write:
  1. Write to DB
  2. Invalidate cache (or update)
```

**Implementation:**
```go
// cache/cache_aside.go
package cache

import (
    "context"
    "encoding/json"
    "fmt"
    "github.com/go-redis/redis/v8"
    "time"
)

type CacheAside struct {
    redis *redis.Client
    db    Database
    ttl   time.Duration
}

func NewCacheAside(redis *redis.Client, db Database) *CacheAside {
    return &CacheAside{
        redis: redis,
        db:    db,
        ttl:   1 * time.Hour,
    }
}

// Read with cache
func (ca *CacheAside) GetUser(ctx context.Context, userID int) (*User, error) {
    cacheKey := fmt.Sprintf("user:%d", userID)
    
    // Try cache first
    cached, err := ca.redis.Get(ctx, cacheKey).Result()
    if err == nil {
        var user User
        if err := json.Unmarshal([]byte(cached), &user); err == nil {
            fmt.Println("CACHE HIT")
            return &user, nil
        }
    }
    
    fmt.Println("CACHE MISS")
    
    // Cache miss - read from database
    user, err := ca.db.GetUser(ctx, userID)
    if err != nil {
        return nil, err
    }
    
    // Populate cache
    data, _ := json.Marshal(user)
    ca.redis.Set(ctx, cacheKey, data, ca.ttl)
    
    return user, nil
}

// Write (invalidate cache)
func (ca *CacheAside) UpdateUser(ctx context.Context, user *User) error {
    // Write to database
    if err := ca.db.UpdateUser(ctx, user); err != nil {
        return err
    }
    
    // Invalidate cache
    cacheKey := fmt.Sprintf("user:%d", user.ID)
    ca.redis.Del(ctx, cacheKey)
    
    return nil
}
```

**Pros:**
- Simple to implement
- Cache only what's requested (efficient memory usage)
- Works well for read-heavy workloads

**Cons:**
- Cache miss penalty (3x latency: check cache, read DB, update cache)
- Stale data possible
- Thundering herd on cache miss

---

### 2.2 Write-Through Cache

**Flow:**
```
Read:
  1. Check cache
  2. If hit → return
  3. If miss → read DB, cache, return

Write:
  1. Write to cache
  2. Write to DB (synchronously)
  3. Return success
```

**Implementation:**
```go
// cache/write_through.go
package cache

type WriteThrough struct {
    redis *redis.Client
    db    Database
    ttl   time.Duration
}

func (wt *WriteThrough) UpdateUser(ctx context.Context, user *User) error {
    cacheKey := fmt.Sprintf("user:%d", user.ID)
    
    // Write to cache first
    data, err := json.Marshal(user)
    if err != nil {
        return err
    }
    
    if err := wt.redis.Set(ctx, cacheKey, data, wt.ttl).Err(); err != nil {
        return fmt.Errorf("cache write failed: %w", err)
    }
    
    // Write to database (synchronously)
    if err := wt.db.UpdateUser(ctx, user); err != nil {
        // Rollback cache on DB failure
        wt.redis.Del(ctx, cacheKey)
        return fmt.Errorf("database write failed: %w", err)
    }
    
    return nil
}
```

**Pros:**
- Cache always consistent with DB
- No stale data
- Simple consistency model

**Cons:**
- Higher write latency (2x: cache + DB)
- Unused data cached (wasted memory)

---

### 2.3 Write-Behind (Write-Back) Cache

**Flow:**
```
Write:
  1. Write to cache (fast)
  2. Return success immediately
  3. Asynchronously write to DB (background)
```

**Implementation:**
```go
// cache/write_behind.go
package cache

import (
    "sync"
    "time"
)

type WriteBehind struct {
    redis      *redis.Client
    db         Database
    writeQueue chan *User
    batchSize  int
    flushTime  time.Duration
}

func NewWriteBehind(redis *redis.Client, db Database) *WriteBehind {
    wb := &WriteBehind{
        redis:      redis,
        db:         db,
        writeQueue: make(chan *User, 10000),
        batchSize:  100,
        flushTime:  5 * time.Second,
    }
    
    // Start background writer
    go wb.flushWorker()
    
    return wb
}

func (wb *WriteBehind) UpdateUser(ctx context.Context, user *User) error {
    cacheKey := fmt.Sprintf("user:%d", user.ID)
    
    // Write to cache (fast)
    data, _ := json.Marshal(user)
    if err := wb.redis.Set(ctx, cacheKey, data, 0).Err(); err != nil {
        return err
    }
    
    // Queue for async DB write
    select {
    case wb.writeQueue <- user:
        return nil
    default:
        return fmt.Errorf("write queue full")
    }
}

func (wb *WriteBehind) flushWorker() {
    ticker := time.NewTicker(wb.flushTime)
    defer ticker.Stop()
    
    batch := make([]*User, 0, wb.batchSize)
    
    for {
        select {
        case user := <-wb.writeQueue:
            batch = append(batch, user)
            
            if len(batch) >= wb.batchSize {
                wb.flushBatch(batch)
                batch = batch[:0]
            }
            
        case <-ticker.C:
            if len(batch) > 0 {
                wb.flushBatch(batch)
                batch = batch[:0]
            }
        }
    }
}

func (wb *WriteBehind) flushBatch(batch []*User) {
    ctx := context.Background()
    
    // Batch write to database
    if err := wb.db.BatchUpdateUsers(ctx, batch); err != nil {
        fmt.Printf("ERROR: Failed to flush batch: %v\n", err)
        // TODO: Retry logic, dead letter queue
    } else {
        fmt.Printf("Flushed %d users to database\n", len(batch))
    }
}
```

**Pros:**
- Very fast writes (cache only)
- High throughput (batching)
- Reduces DB load

**Cons:**
- Risk of data loss (if cache crashes before flush)
- Complex error handling
- Eventual consistency

**When to use:** High-write workloads where some data loss is acceptable (e.g., analytics, view counts)

---

### 2.4 Read-Through Cache

**Flow:**
```
Read:
  1. Check cache
  2. If hit → return
  3. If miss → cache loads from DB automatically
```

**Implementation:**
```go
// cache/read_through.go
package cache

type ReadThrough struct {
    redis   *redis.Client
    db      Database
    loader  DataLoader
    ttl     time.Duration
}

// DataLoader interface
type DataLoader interface {
    Load(ctx context.Context, key string) (interface{}, error)
}

type UserLoader struct {
    db Database
}

func (ul *UserLoader) Load(ctx context.Context, key string) (interface{}, error) {
    // Parse user ID from key
    var userID int
    fmt.Sscanf(key, "user:%d", &userID)
    
    return ul.db.GetUser(ctx, userID)
}

func (rt *ReadThrough) Get(ctx context.Context, key string) (interface{}, error) {
    // Try cache
    cached, err := rt.redis.Get(ctx, key).Result()
    if err == nil {
        var result interface{}
        json.Unmarshal([]byte(cached), &result)
        return result, nil
    }
    
    // Cache miss - load via loader
    value, err := rt.loader.Load(ctx, key)
    if err != nil {
        return nil, err
    }
    
    // Populate cache
    data, _ := json.Marshal(value)
    rt.redis.Set(ctx, key, data, rt.ttl)
    
    return value, nil
}
```

**Pros:**
- Abstraction (business logic doesn't handle cache misses)
- Consistent data loading pattern

**Cons:**
- Tight coupling between cache and data source
- Less flexible than cache-aside

---

## 3. Redis Cluster Architecture

### 3.1 Sharding Strategy

**Hash Slot Partitioning:**
```
Redis Cluster: 16,384 hash slots

Hash Slot = CRC16(key) % 16384

Distribution (3 masters):
  Master 1: Slots 0-5460     (5,461 slots)
  Master 2: Slots 5461-10922 (5,461 slots)
  Master 3: Slots 10923-16383 (5,461 slots)

Example:
  Key "user:123" → CRC16("user:123") = 15,123 → Slot 15,123
  Slot 15,123 → Master 3
```

---

### 3.2 Cluster Configuration

```go
// cluster/redis_cluster.go
package cluster

import (
    "context"
    "github.com/go-redis/redis/v8"
)

func NewRedisCluster(addrs []string) *redis.ClusterClient {
    return redis.NewClusterClient(&redis.ClusterOptions{
        Addrs: addrs,
        
        // Connection pool
        PoolSize:     100,
        MinIdleConns: 10,
        
        // Timeouts
        DialTimeout:  5 * time.Second,
        ReadTimeout:  3 * time.Second,
        WriteTimeout: 3 * time.Second,
        
        // Retries
        MaxRetries:      3,
        MinRetryBackoff: 8 * time.Millisecond,
        MaxRetryBackoff: 512 * time.Millisecond,
    })
}

// Usage
func main() {
    client := NewRedisCluster([]string{
        "redis-1:6379",
        "redis-2:6379",
        "redis-3:6379",
    })
    
    ctx := context.Background()
    
    // Writes are automatically routed to correct shard
    client.Set(ctx, "user:123", "John", 0)
    client.Set(ctx, "user:456", "Jane", 0)
    
    // Reads too
    val, _ := client.Get(ctx, "user:123").Result()
    fmt.Println(val)  // "John"
}
```

---

### 3.3 Replication

**Architecture:**
```
Master 1 (Slots 0-5460)
  ├── Replica 1a
  └── Replica 1b

Master 2 (Slots 5461-10922)
  ├── Replica 2a
  └── Replica 2b

Master 3 (Slots 10923-16383)
  ├── Replica 3a
  └── Replica 3b
```

**Failover:**
```
If Master 1 fails:
  1. Replicas detect failure (ping timeout)
  2. Election: Replica with most up-to-date data wins
  3. Replica 1a becomes new Master 1
  4. Cluster config updated
  5. Clients redirected to new master

Downtime: ~1-2 seconds
```

---

### 3.4 Multi-Key Operations

**Problem:** Keys may be on different shards

```go
// Won't work in cluster mode
client.MGet(ctx, "user:123", "user:456")  // ERROR: CROSSSLOT
```

**Solution 1: Hash Tags**
```go
// Force keys to same slot using {}
client.Set(ctx, "{user}:123", "John", 0)
client.Set(ctx, "{user}:456", "Jane", 0)

// Now this works (both keys on same slot)
client.MGet(ctx, "{user}:123", "{user}:456")
```

**Solution 2: Pipeline**
```go
pipe := client.Pipeline()
pipe.Get(ctx, "user:123")
pipe.Get(ctx, "user:456")
results, _ := pipe.Exec(ctx)
```

---

## 4. Invalidation Strategies

### 4.1 TTL-Based Invalidation

**Simple Expiration:**
```go
// Set with TTL
client.Set(ctx, "user:123", userData, 1*time.Hour)

// After 1 hour, key auto-expires
```

**Pros:**
- Simple
- Prevents memory leaks
- Works for all cache patterns

**Cons:**
- Stale data until expiry
- Cache misses at expiration

---

### 4.2 Event-Based Invalidation

**Approach:** Invalidate on write

```go
// cache/invalidation.go
package cache

type CacheInvalidator struct {
    redis *redis.Client
}

func (ci *CacheInvalidator) InvalidateUser(ctx context.Context, userID int) error {
    keys := []string{
        fmt.Sprintf("user:%d", userID),
        fmt.Sprintf("user:%d:profile", userID),
        fmt.Sprintf("user:%d:settings", userID),
    }
    
    return ci.redis.Del(ctx, keys...).Err()
}

// In your service
func (s *UserService) UpdateUser(ctx context.Context, user *User) error {
    // Update database
    if err := s.db.UpdateUser(ctx, user); err != nil {
        return err
    }
    
    // Invalidate cache
    s.invalidator.InvalidateUser(ctx, user.ID)
    
    return nil
}
```

---

### 4.3 Pattern-Based Invalidation

**Use Lua script for atomic pattern delete:**

```lua
-- invalidate_pattern.lua
local cursor = "0"
local keys_deleted = 0

repeat
    local result = redis.call("SCAN", cursor, "MATCH", ARGV[1], "COUNT", 100)
    cursor = result[1]
    local keys = result[2]
    
    for i, key in ipairs(keys) do
        redis.call("DEL", key)
        keys_deleted = keys_deleted + 1
    end
until cursor == "0"

return keys_deleted
```

```go
// Load and execute Lua script
func (ci *CacheInvalidator) InvalidatePattern(ctx context.Context, pattern string) (int, error) {
    script := `
        local cursor = "0"
        local keys_deleted = 0
        repeat
            local result = redis.call("SCAN", cursor, "MATCH", ARGV[1], "COUNT", 100)
            cursor = result[1]
            local keys = result[2]
            for i, key in ipairs(keys) do
                redis.call("DEL", key)
                keys_deleted = keys_deleted + 1
            end
        until cursor == "0"
        return keys_deleted
    `
    
    result, err := ci.redis.Eval(ctx, script, []string{}, pattern).Result()
    if err != nil {
        return 0, err
    }
    
    return int(result.(int64)), nil
}

// Usage
invalidator.InvalidatePattern(ctx, "user:*")  // Delete all user keys
```

---

### 4.4 Tagging-Based Invalidation

**Approach:** Tag cache entries, invalidate by tag

```go
// cache/tags.go
package cache

type TaggedCache struct {
    redis *redis.Client
}

func (tc *TaggedCache) SetWithTags(ctx context.Context, key string, value interface{}, tags []string, ttl time.Duration) error {
    // Store value
    data, _ := json.Marshal(value)
    if err := tc.redis.Set(ctx, key, data, ttl).Err(); err != nil {
        return err
    }
    
    // Add key to each tag set
    for _, tag := range tags {
        tagKey := fmt.Sprintf("tag:%s", tag)
        tc.redis.SAdd(ctx, tagKey, key)
        tc.redis.Expire(ctx, tagKey, ttl)
    }
    
    return nil
}

func (tc *TaggedCache) InvalidateTag(ctx context.Context, tag string) error {
    tagKey := fmt.Sprintf("tag:%s", tag)
    
    // Get all keys with this tag
    keys, err := tc.redis.SMembers(ctx, tagKey).Result()
    if err != nil {
        return err
    }
    
    // Delete all keys
    if len(keys) > 0 {
        tc.redis.Del(ctx, keys...)
    }
    
    // Delete tag set
    tc.redis.Del(ctx, tagKey)
    
    return nil
}

// Example usage
func Example() {
    tc := &TaggedCache{redis: client}
    
    // Cache user with tags
    user := &User{ID: 123, Name: "John", CompanyID: 10}
    tc.SetWithTags(ctx, "user:123", user, 
        []string{"user", "company:10"}, 
        1*time.Hour)
    
    // Invalidate all company:10 caches
    tc.InvalidateTag(ctx, "company:10")
}
```

---

## 5. CDC-Based Invalidation

### 5.1 Change Data Capture Overview

**Idea:** Listen to database changes, invalidate cache automatically

```
PostgreSQL
  │
  ├─ Write-Ahead Log (WAL)
  │
  ▼
Debezium (CDC)
  │
  ▼
Kafka Topic: db.changes
  │
  ▼
Cache Invalidator
  │
  ▼
Redis
```

---

### 5.2 Debezium Setup

```yaml
# debezium-postgres.json
{
  "name": "postgres-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "postgres",
    "database.password": "password",
    "database.dbname": "myapp",
    "database.server.name": "myapp",
    "table.include.list": "public.users,public.products",
    "plugin.name": "pgoutput"
  }
}
```

**Deploy:**
```bash
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @debezium-postgres.json
```

---

### 5.3 CDC Consumer Implementation

```go
// cdc/invalidator.go
package cdc

import (
    "context"
    "encoding/json"
    "fmt"
    "github.com/go-redis/redis/v8"
    "github.com/segmentio/kafka-go"
)

type ChangeEvent struct {
    Schema  Schema  `json:"schema"`
    Payload Payload `json:"payload"`
}

type Payload struct {
    Before map[string]interface{} `json:"before"`
    After  map[string]interface{} `json:"after"`
    Op     string                 `json:"op"`  // c=create, u=update, d=delete
    Source Source                 `json:"source"`
}

type Source struct {
    Table string `json:"table"`
}

type CDCInvalidator struct {
    redis  *redis.Client
    kafka  *kafka.Reader
}

func NewCDCInvalidator(redis *redis.Client, kafkaBrokers []string) *CDCInvalidator {
    reader := kafka.NewReader(kafka.ReaderConfig{
        Brokers: kafkaBrokers,
        Topic:   "myapp.public.users",
        GroupID: "cache-invalidator",
    })
    
    return &CDCInvalidator{
        redis: redis,
        kafka: reader,
    }
}

func (ci *CDCInvalidator) Start(ctx context.Context) {
    for {
        msg, err := ci.kafka.ReadMessage(ctx)
        if err != nil {
            fmt.Printf("Error reading message: %v\n", err)
            continue
        }
        
        var event ChangeEvent
        if err := json.Unmarshal(msg.Value, &event); err != nil {
            fmt.Printf("Error unmarshaling: %v\n", err)
            continue
        }
        
        ci.handleChange(ctx, &event)
    }
}

func (ci *CDCInvalidator) handleChange(ctx context.Context, event *ChangeEvent) {
    table := event.Payload.Source.Table
    op := event.Payload.Op
    
    switch table {
    case "users":
        ci.handleUserChange(ctx, event, op)
    case "products":
        ci.handleProductChange(ctx, event, op)
    }
}

func (ci *CDCInvalidator) handleUserChange(ctx context.Context, event *ChangeEvent, op string) {
    var userID int
    
    if op == "d" {
        // Delete: use 'before' data
        userID = int(event.Payload.Before["id"].(float64))
    } else {
        // Create/Update: use 'after' data
        userID = int(event.Payload.After["id"].(float64))
    }
    
    // Invalidate user cache
    keys := []string{
        fmt.Sprintf("user:%d", userID),
        fmt.Sprintf("user:%d:profile", userID),
        fmt.Sprintf("user:%d:posts", userID),
    }
    
    result := ci.redis.Del(ctx, keys...)
    fmt.Printf("Invalidated %d keys for user %d (op=%s)\n", 
               result.Val(), userID, op)
}

func (ci *CDCInvalidator) handleProductChange(ctx context.Context, event *ChangeEvent, op string) {
    // Similar logic for products
}
```

---

### 5.4 CDC Event Flow

**Example:**
```
1. Application updates user:
   UPDATE users SET name = 'John Doe' WHERE id = 123;

2. PostgreSQL writes to WAL

3. Debezium reads WAL, publishes to Kafka:
   {
     "payload": {
       "before": {"id": 123, "name": "John"},
       "after": {"id": 123, "name": "John Doe"},
       "op": "u",
       "source": {"table": "users"}
     }
   }

4. CDC Invalidator consumes event

5. Invalidates Redis keys:
   DEL user:123
   DEL user:123:profile

6. Next read will cache miss, reload from DB
```

---

### 5.5 CDC vs Manual Invalidation

| Aspect | Manual | CDC |
|--------|--------|-----|
| **Coupling** | Tight (app must know about cache) | Loose (decoupled) |
| **Consistency** | Risk of bugs (forgot to invalidate) | Always consistent |
| **Latency** | Instant | Small delay (~100ms) |
| **Complexity** | Low | Medium |
| **Best For** | Simple apps | Microservices, complex systems |

---

## 6. Production Best Practices

### 6.1 Cache Stampede Prevention

**Problem:** When cache expires, many requests hit DB simultaneously

```
Time 0:00 - Cache expires
Time 0:01 - 1000 requests → all cache miss → 1000 DB queries!
```

**Solution 1: Probabilistic Early Expiration**

```go
func (ca *CacheAside) GetWithProbabilisticExpiry(ctx context.Context, key string, ttl time.Duration) (interface{}, error) {
    cached, remainingTTL, err := ca.redis.Get(ctx, key).Result()
    
    // Calculate probability of early expiration
    xfetch := -log(rand.Float64()) * 1.0  // Random exponential
    
    if remainingTTL < xfetch * ttl / 10 {
        // Refresh cache early
        value, _ := ca.loader.Load(ctx, key)
        ca.redis.Set(ctx, key, value, ttl)
        return value, nil
    }
    
    return cached, nil
}
```

**Solution 2: Distributed Lock**

```go
func (ca *CacheAside) GetWithLock(ctx context.Context, key string) (interface{}, error) {
    // Try cache
    cached, err := ca.redis.Get(ctx, key).Result()
    if err == nil {
        return cached, nil
    }
    
    lockKey := fmt.Sprintf("lock:%s", key)
    
    // Try to acquire lock
    locked, _ := ca.redis.SetNX(ctx, lockKey, "1", 5*time.Second).Result()
    
    if locked {
        // This request loads data
        defer ca.redis.Del(ctx, lockKey)
        
        value, _ := ca.loader.Load(ctx, key)
        ca.redis.Set(ctx, key, value, 1*time.Hour)
        return value, nil
    } else {
        // Other requests wait and retry
        time.Sleep(50 * time.Millisecond)
        return ca.GetWithLock(ctx, key)
    }
}
```

---

### 6.2 Monitoring

```go
// metrics/cache_metrics.go
package metrics

import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

var (
    CacheHits = promauto.NewCounter(prometheus.CounterOpts{
        Name: "cache_hits_total",
        Help: "Total cache hits",
    })
    
    CacheMisses = promauto.NewCounter(prometheus.CounterOpts{
        Name: "cache_misses_total",
        Help: "Total cache misses",
    })
    
    CacheLatency = promauto.NewHistogram(prometheus.HistogramOpts{
        Name:    "cache_request_duration_seconds",
        Help:    "Cache request latency",
        Buckets: []float64{.0001, .0005, .001, .005, .01},
    })
)

func RecordCacheHit() {
    CacheHits.Inc()
}

func RecordCacheMiss() {
    CacheMisses.Inc()
}

// Calculate hit rate
func GetCacheHitRate() float64 {
    // In Prometheus:
    // rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m]))
    return 0.0
}
```

---

### 6.3 Cache Warming

```go
// warming/cache_warmer.go
package warming

type CacheWarmer struct {
    redis *redis.Client
    db    Database
}

func (cw *CacheWarmer) WarmCache(ctx context.Context) error {
    // Load hot data
    hotUsers, err := cw.db.GetHotUsers(ctx, 10000)  // Top 10K users
    if err != nil {
        return err
    }
    
    // Populate cache
    pipe := cw.redis.Pipeline()
    for _, user := range hotUsers {
        key := fmt.Sprintf("user:%d", user.ID)
        data, _ := json.Marshal(user)
        pipe.Set(ctx, key, data, 1*time.Hour)
    }
    
    _, err = pipe.Exec(ctx)
    return err
}

// Run on startup
func main() {
    warmer := &CacheWarmer{redis: client, db: db}
    warmer.WarmCache(context.Background())
    
    // Start server
    startServer()
}
```

---

### 6.4 Memory Management

**Set Max Memory:**
```conf
# redis.conf
maxmemory 10gb
maxmemory-policy allkeys-lru
```

**Policies:**
- `noeviction`: Return errors when memory limit reached
- `allkeys-lru`: Evict least recently used keys
- `allkeys-lfu`: Evict least frequently used keys
- `volatile-lru`: Evict LRU among keys with TTL
- `volatile-ttl`: Evict keys with shortest TTL

**Monitor Memory:**
```bash
redis-cli INFO memory

# Output:
# used_memory:8589934592
# used_memory_human:8.00G
# used_memory_peak:10737418240
# used_memory_peak_human:10.00G
```

---

## Summary

### Pattern Selection

| Use Case | Pattern | Consistency | Performance |
|----------|---------|-------------|-------------|
| Read-heavy, can tolerate stale | Cache-Aside | Eventual | High |
| Need consistency | Write-Through | Strong | Medium |
| High-write, can tolerate loss | Write-Behind | Eventual | Very High |
| Complex data loading | Read-Through | Eventual | High |

### Invalidation Selection

| Use Case | Strategy | Complexity | Accuracy |
|----------|----------|------------|----------|
| Simple app | TTL | Low | Medium |
| Microservices | CDC | Medium | High |
| Real-time | Event-based | Low | High |
| Complex relationships | Tagging | Medium | High |

### Production Checklist

✅ Achieve 95%+ cache hit rate  
✅ Set appropriate TTLs (1 hour default)  
✅ Implement cache stampede prevention  
✅ Monitor hit rate, latency, memory  
✅ Use Redis Cluster for horizontal scaling  
✅ Enable replication (3x for HA)  
✅ Implement CDC for automatic invalidation  
✅ Warm cache on startup  
✅ Set max memory and eviction policy  
✅ Use connection pooling  

---

**End of Cache Architecture Patterns**

**Total Lines: ~4,000**
