# LLD Case Studies - Classic Interview Problems

**Learning Time:** 4-6 weeks of practice  
**Prerequisites:** Design Patterns, SOLID Principles  
**Difficulty:** Interview-Level (Medium to Hard)

---

## 📚 Table of Contents

1. [LRU Cache](#1-lru-cache)
2. [Rate Limiter](#2-rate-limiter)
3. [Parking Lot System](#3-parking-lot-system)
4. [URL Shortener](#4-url-shortener)
5. [Notification System](#5-notification-system)
6. [Distributed Cache](#6-distributed-cache)

---

## 1. LRU Cache

### Problem Statement
Design and implement a data structure for Least Recently Used (LRU) cache. Support:
- `get(key)`: Get value (return -1 if not exists). Mark as recently used.
- `put(key, value)`: Insert/update key-value pair. If capacity full, evict least recently used.
- Both operations in **O(1) time**.

### Approach
Use **HashMap** + **Doubly Linked List**:
- HashMap: O(1) lookup by key
- Doubly Linked List: O(1) move to front (most recent) and remove from back (least recent)

### Implementation

```java
/**
 * Production-Grade LRU Cache with Thread Safety
 */
public class LRUCache<K, V> {
    
    // Node in doubly linked list
    private static class Node<K, V> {
        K key;
        V value;
        Node<K, V> prev;
        Node<K, V> next;
        
        Node(K key, V value) {
            this.key = key;
            this.value = value;
        }
    }
    
    private final int capacity;
    private final Map<K, Node<K, V>> cache;
    private final Node<K, V> head;  // Dummy head (most recent)
    private final Node<K, V> tail;  // Dummy tail (least recent)
    private final ReadWriteLock lock;
    
    public LRUCache(int capacity) {
        if (capacity <= 0) {
            throw new IllegalArgumentException("Capacity must be positive");
        }
        
        this.capacity = capacity;
        this.cache = new HashMap<>(capacity);
        this.lock = new ReentrantReadWriteLock();
        
        // Initialize dummy head and tail
        this.head = new Node<>(null, null);
        this.tail = new Node<>(null, null);
        head.next = tail;
        tail.prev = head;
    }
    
    public V get(K key) {
        lock.readLock().lock();
        try {
            Node<K, V> node = cache.get(key);
            if (node == null) {
                return null;
            }
            
            // Move to front (most recently used)
            moveToFront(node);
            return node.value;
            
        } finally {
            lock.readLock().unlock();
        }
    }
    
    public void put(K key, V value) {
        lock.writeLock().lock();
        try {
            Node<K, V> node = cache.get(key);
            
            if (node != null) {
                // Update existing node
                node.value = value;
                moveToFront(node);
            } else {
                // Create new node
                node = new Node<>(key, value);
                cache.put(key, node);
                addToFront(node);
                
                // Evict if over capacity
                if (cache.size() > capacity) {
                    evictLRU();
                }
            }
            
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    public boolean containsKey(K key) {
        lock.readLock().lock();
        try {
            return cache.containsKey(key);
        } finally {
            lock.readLock().unlock();
        }
    }
    
    public int size() {
        lock.readLock().lock();
        try {
            return cache.size();
        } finally {
            lock.readLock().unlock();
        }
    }
    
    // Remove node from current position
    private void removeNode(Node<K, V> node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
    }
    
    // Add node right after head (most recent position)
    private void addToFront(Node<K, V> node) {
        node.next = head.next;
        node.prev = head;
        head.next.prev = node;
        head.next = node;
    }
    
    // Move existing node to front
    private void moveToFront(Node<K, V> node) {
        removeNode(node);
        addToFront(node);
    }
    
    // Evict least recently used (node before tail)
    private void evictLRU() {
        Node<K, V> lru = tail.prev;
        if (lru != head) {  // Not empty
            removeNode(lru);
            cache.remove(lru.key);
            System.out.println("Evicted: " + lru.key);
        }
    }
    
    // For debugging
    public void printCache() {
        lock.readLock().lock();
        try {
            System.out.print("Cache (MRU → LRU): ");
            Node<K, V> current = head.next;
            while (current != tail) {
                System.out.print(current.key + "=" + current.value + " ");
                current = current.next;
            }
            System.out.println();
        } finally {
            lock.readLock().unlock();
        }
    }
}

// Usage
public class Main {
    public static void main(String[] args) {
        LRUCache<Integer, String> cache = new LRUCache<>(3);
        
        cache.put(1, "One");
        cache.put(2, "Two");
        cache.put(3, "Three");
        cache.printCache();  // 3=Three 2=Two 1=One
        
        cache.get(1);  // Access 1 (move to front)
        cache.printCache();  // 1=One 3=Three 2=Two
        
        cache.put(4, "Four");  // Evicts 2 (LRU)
        cache.printCache();  // 4=Four 1=One 3=Three
        
        cache.get(3);  // Access 3 (move to front)
        cache.printCache();  // 3=Three 4=Four 1=One
        
        cache.put(5, "Five");  // Evicts 1 (LRU)
        cache.printCache();  // 5=Five 3=Three 4=Four
    }
}
```

### LRU with Expiration (Time-Based Eviction)

```java
/**
 * LRU Cache with TTL (Time To Live)
 */
public class LRUCacheWithTTL<K, V> {
    
    private static class CacheEntry<V> {
        V value;
        long expirationTime;
        
        CacheEntry(V value, long ttlMillis) {
            this.value = value;
            this.expirationTime = System.currentTimeMillis() + ttlMillis;
        }
        
        boolean isExpired() {
            return System.currentTimeMillis() > expirationTime;
        }
    }
    
    private final LRUCache<K, CacheEntry<V>> cache;
    private final long defaultTtlMillis;
    
    public LRUCacheWithTTL(int capacity, long defaultTtlMillis) {
        this.cache = new LRUCache<>(capacity);
        this.defaultTtlMillis = defaultTtlMillis;
    }
    
    public V get(K key) {
        CacheEntry<V> entry = cache.get(key);
        if (entry == null) {
            return null;
        }
        
        if (entry.isExpired()) {
            cache.put(key, null);  // Remove expired entry
            return null;
        }
        
        return entry.value;
    }
    
    public void put(K key, V value) {
        cache.put(key, new CacheEntry<>(value, defaultTtlMillis));
    }
    
    public void put(K key, V value, long ttlMillis) {
        cache.put(key, new CacheEntry<>(value, ttlMillis));
    }
}

// Usage
public class Main {
    public static void main(String[] args) throws InterruptedException {
        // Cache with 5 second TTL
        LRUCacheWithTTL<String, String> cache = new LRUCacheWithTTL<>(3, 5000);
        
        cache.put("session1", "user123");
        cache.put("session2", "user456", 2000);  // Custom TTL: 2 seconds
        
        System.out.println(cache.get("session1"));  // user123
        System.out.println(cache.get("session2"));  // user456
        
        Thread.sleep(3000);  // Wait 3 seconds
        
        System.out.println(cache.get("session1"));  // user123 (still valid)
        System.out.println(cache.get("session2"));  // null (expired)
    }
}
```

### Interview Discussion Points

**Time Complexity:**
- `get(key)`: O(1) — HashMap lookup + linked list reordering
- `put(key, value)`: O(1) — HashMap insert + linked list operations

**Space Complexity:** O(capacity) — HashMap + linked list nodes

**Thread Safety:**
- Use `ReadWriteLock` for concurrent access
- Read operations (get) can run in parallel
- Write operations (put) are exclusive

**Variations Asked in Interviews:**
1. **LFU Cache** (Least Frequently Used): Track access count instead of recency
2. **LRU with Priority**: Some keys have higher priority (never evict)
3. **2Q Cache**: Maintain two queues (recently used + frequently used)
4. **ARC** (Adaptive Replacement Cache): Balance recency and frequency

**Real-World Usage:**
- **Redis**: Uses LRU for eviction policy
- **Memcached**: LRU eviction
- **CDN**: Cache objects with LRU
- **Database Buffer Pool**: OS page cache, database query cache

---

## 2. Rate Limiter

### Problem Statement
Design a rate limiter to throttle requests:
- **Fixed Window**: Allow N requests per time window (e.g., 100 requests/minute)
- **Sliding Window**: More accurate, no burst at window boundaries
- **Token Bucket**: Allow bursts, refill tokens at fixed rate
- **Leaky Bucket**: Smooth request rate

### Approach 1: Fixed Window Counter

```java
/**
 * Fixed Window Rate Limiter
 * Example: 100 requests per minute
 */
public class FixedWindowRateLimiter {
    
    private static class WindowCounter {
        long windowStart;
        int count;
        
        WindowCounter(long windowStart) {
            this.windowStart = windowStart;
            this.count = 0;
        }
    }
    
    private final int maxRequests;
    private final long windowSizeMillis;
    private final Map<String, WindowCounter> counters;
    private final ReadWriteLock lock;
    
    public FixedWindowRateLimiter(int maxRequests, long windowSizeMillis) {
        this.maxRequests = maxRequests;
        this.windowSizeMillis = windowSizeMillis;
        this.counters = new ConcurrentHashMap<>();
        this.lock = new ReentrantReadWriteLock();
    }
    
    public boolean allowRequest(String userId) {
        lock.writeLock().lock();
        try {
            long now = System.currentTimeMillis();
            long windowStart = (now / windowSizeMillis) * windowSizeMillis;
            
            WindowCounter counter = counters.computeIfAbsent(
                userId,
                k -> new WindowCounter(windowStart)
            );
            
            // Reset counter if new window
            if (counter.windowStart < windowStart) {
                counter.windowStart = windowStart;
                counter.count = 0;
            }
            
            // Check limit
            if (counter.count < maxRequests) {
                counter.count++;
                return true;
            }
            
            return false;
            
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    public int getRemainingRequests(String userId) {
        lock.readLock().lock();
        try {
            WindowCounter counter = counters.get(userId);
            if (counter == null) {
                return maxRequests;
            }
            
            long now = System.currentTimeMillis();
            long windowStart = (now / windowSizeMillis) * windowSizeMillis;
            
            if (counter.windowStart < windowStart) {
                return maxRequests;  // New window
            }
            
            return Math.max(0, maxRequests - counter.count);
            
        } finally {
            lock.readLock().unlock();
        }
    }
}

// Usage
public class Main {
    public static void main(String[] args) throws InterruptedException {
        // 5 requests per 10 seconds
        FixedWindowRateLimiter limiter = new FixedWindowRateLimiter(5, 10_000);
        
        String userId = "user123";
        
        // First 5 requests succeed
        for (int i = 1; i <= 5; i++) {
            boolean allowed = limiter.allowRequest(userId);
            System.out.println("Request " + i + ": " + (allowed ? "ALLOWED" : "DENIED"));
        }
        
        // 6th request denied
        boolean allowed = limiter.allowRequest(userId);
        System.out.println("Request 6: " + (allowed ? "ALLOWED" : "DENIED"));
        
        System.out.println("Remaining: " + limiter.getRemainingRequests(userId));
        
        // Wait for window to reset
        Thread.sleep(10_000);
        
        // New window, request allowed
        allowed = limiter.allowRequest(userId);
        System.out.println("Request after reset: " + (allowed ? "ALLOWED" : "DENIED"));
    }
}
```

### Approach 2: Sliding Window Log

```java
/**
 * Sliding Window Log Rate Limiter
 * More accurate than fixed window, no burst issues
 */
public class SlidingWindowLogRateLimiter {
    
    private final int maxRequests;
    private final long windowSizeMillis;
    private final Map<String, Deque<Long>> requestLogs;
    private final ReadWriteLock lock;
    
    public SlidingWindowLogRateLimiter(int maxRequests, long windowSizeMillis) {
        this.maxRequests = maxRequests;
        this.windowSizeMillis = windowSizeMillis;
        this.requestLogs = new ConcurrentHashMap<>();
        this.lock = new ReentrantReadWriteLock();
    }
    
    public boolean allowRequest(String userId) {
        lock.writeLock().lock();
        try {
            long now = System.currentTimeMillis();
            
            Deque<Long> log = requestLogs.computeIfAbsent(userId, k -> new ArrayDeque<>());
            
            // Remove timestamps outside the current window
            while (!log.isEmpty() && log.peekFirst() <= now - windowSizeMillis) {
                log.pollFirst();
            }
            
            // Check if under limit
            if (log.size() < maxRequests) {
                log.addLast(now);
                return true;
            }
            
            return false;
            
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    public int getRemainingRequests(String userId) {
        lock.readLock().lock();
        try {
            long now = System.currentTimeMillis();
            Deque<Long> log = requestLogs.get(userId);
            
            if (log == null) {
                return maxRequests;
            }
            
            // Count requests in current window
            long count = log.stream()
                .filter(timestamp -> timestamp > now - windowSizeMillis)
                .count();
            
            return (int) Math.max(0, maxRequests - count);
            
        } finally {
            lock.readLock().unlock();
        }
    }
}
```

### Approach 3: Token Bucket

```java
/**
 * Token Bucket Rate Limiter
 * Allows bursts, refills at steady rate
 * Used by AWS, Stripe, GitHub APIs
 */
public class TokenBucketRateLimiter {
    
    private static class Bucket {
        double tokens;
        long lastRefillTime;
        
        Bucket(double initialTokens) {
            this.tokens = initialTokens;
            this.lastRefillTime = System.currentTimeMillis();
        }
    }
    
    private final int capacity;          // Max tokens
    private final double refillRate;     // Tokens per second
    private final Map<String, Bucket> buckets;
    private final ReadWriteLock lock;
    
    public TokenBucketRateLimiter(int capacity, double refillRate) {
        this.capacity = capacity;
        this.refillRate = refillRate;
        this.buckets = new ConcurrentHashMap<>();
        this.lock = new ReentrantReadWriteLock();
    }
    
    public boolean allowRequest(String userId) {
        return allowRequest(userId, 1);
    }
    
    public boolean allowRequest(String userId, int tokens) {
        lock.writeLock().lock();
        try {
            Bucket bucket = buckets.computeIfAbsent(
                userId,
                k -> new Bucket(capacity)
            );
            
            refillBucket(bucket);
            
            if (bucket.tokens >= tokens) {
                bucket.tokens -= tokens;
                return true;
            }
            
            return false;
            
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    private void refillBucket(Bucket bucket) {
        long now = System.currentTimeMillis();
        double elapsedSeconds = (now - bucket.lastRefillTime) / 1000.0;
        
        double tokensToAdd = elapsedSeconds * refillRate;
        bucket.tokens = Math.min(capacity, bucket.tokens + tokensToAdd);
        bucket.lastRefillTime = now;
    }
    
    public double getAvailableTokens(String userId) {
        lock.readLock().lock();
        try {
            Bucket bucket = buckets.get(userId);
            if (bucket == null) {
                return capacity;
            }
            
            // Calculate with refill
            long now = System.currentTimeMillis();
            double elapsedSeconds = (now - bucket.lastRefillTime) / 1000.0;
            double tokensToAdd = elapsedSeconds * refillRate;
            
            return Math.min(capacity, bucket.tokens + tokensToAdd);
            
        } finally {
            lock.readLock().unlock();
        }
    }
}

// Usage
public class Main {
    public static void main(String[] args) throws InterruptedException {
        // Capacity: 10 tokens, Refill: 1 token/second
        TokenBucketRateLimiter limiter = new TokenBucketRateLimiter(10, 1.0);
        
        String userId = "user123";
        
        // Burst: Use all 10 tokens
        for (int i = 1; i <= 10; i++) {
            boolean allowed = limiter.allowRequest(userId);
            System.out.println("Request " + i + ": " + (allowed ? "ALLOWED" : "DENIED"));
        }
        
        // 11th request denied (no tokens)
        boolean allowed = limiter.allowRequest(userId);
        System.out.println("Request 11: " + (allowed ? "ALLOWED" : "DENIED"));
        
        System.out.println("Available tokens: " + limiter.getAvailableTokens(userId));
        
        // Wait 5 seconds (refill 5 tokens)
        Thread.sleep(5000);
        
        System.out.println("Available tokens after 5s: " + limiter.getAvailableTokens(userId));
        
        // Can make 5 more requests
        for (int i = 1; i <= 5; i++) {
            allowed = limiter.allowRequest(userId);
            System.out.println("Request after wait " + i + ": " + (allowed ? "ALLOWED" : "DENIED"));
        }
    }
}
```

### Distributed Rate Limiter (Redis)

```java
/**
 * Distributed Rate Limiter using Redis
 * For microservices architecture
 */
public class RedisRateLimiter {
    
    private final Jedis jedis;
    private final int maxRequests;
    private final int windowSeconds;
    
    public RedisRateLimiter(Jedis jedis, int maxRequests, int windowSeconds) {
        this.jedis = jedis;
        this.maxRequests = maxRequests;
        this.windowSeconds = windowSeconds;
    }
    
    public boolean allowRequest(String userId) {
        String key = "rate_limit:" + userId;
        long now = System.currentTimeMillis();
        long windowStart = now - (windowSeconds * 1000);
        
        // Remove old entries
        jedis.zremrangeByScore(key, 0, windowStart);
        
        // Count requests in current window
        long count = jedis.zcard(key);
        
        if (count < maxRequests) {
            // Add current request
            jedis.zadd(key, now, String.valueOf(now));
            
            // Set expiration
            jedis.expire(key, windowSeconds);
            
            return true;
        }
        
        return false;
    }
    
    public long getRemainingRequests(String userId) {
        String key = "rate_limit:" + userId;
        long now = System.currentTimeMillis();
        long windowStart = now - (windowSeconds * 1000);
        
        // Remove old entries
        jedis.zremrangeByScore(key, 0, windowStart);
        
        long count = jedis.zcard(key);
        return Math.max(0, maxRequests - count);
    }
}
```

### Interview Discussion Points

**Comparison:**

| Algorithm | Pros | Cons | Use Case |
|-----------|------|------|----------|
| **Fixed Window** | Simple, low memory | Burst at boundaries | Basic rate limiting |
| **Sliding Window Log** | Accurate, no burst | High memory (stores all timestamps) | Strict rate limiting |
| **Token Bucket** | Allows bursts, smooth | Complex refill logic | APIs (AWS, Stripe) |
| **Leaky Bucket** | Smooth output rate | No bursts allowed | Traffic shaping |

**Real-World Examples:**
- **AWS API Gateway**: Token Bucket
- **Stripe API**: Token Bucket (burst + sustained rate)
- **GitHub API**: 5000 requests/hour (fixed window)
- **Twitter API**: 15 requests/15 minutes (sliding window)

**Distributed Considerations:**
- Use Redis for shared state across servers
- Use Redis Lua scripts for atomic operations
- Consider eventual consistency (AP over CP for rate limiting)

**Interview Follow-ups:**
1. "How to handle distributed rate limiting?" → Redis
2. "How to rate limit by IP + User?" → Composite key
3. "How to implement different limits for different tiers (free/premium)?" → Strategy pattern
4. "How to handle clock skew in distributed system?" → Use centralized timestamp (Redis TIME command)

---

## 🎯 Interview Cheat Sheet

### LRU Cache Quick Facts
- **Data Structures**: HashMap + Doubly Linked List
- **Time**: O(1) get, O(1) put
- **Space**: O(capacity)
- **Thread-Safe**: ReadWriteLock or ConcurrentHashMap
- **Variations**: LFU, LRU-K, 2Q, ARC
- **Real Usage**: Redis, Memcached, OS page cache

### Rate Limiter Quick Facts
- **Algorithms**: Fixed Window, Sliding Window, Token Bucket, Leaky Bucket
- **Distributed**: Use Redis with atomic operations (Lua scripts)
- **Trade-offs**: Accuracy vs Memory vs Complexity
- **Real Usage**: AWS (Token Bucket), GitHub (Fixed Window), Stripe (Token Bucket)

---

**Next:** [Parking Lot System](#3-parking-lot-system) — OOP design, state management, strategy pattern
