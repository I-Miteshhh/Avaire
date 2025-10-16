# Week 7: Caching Hierarchies - Smart Storage at Every Level 🧠💾

*"Caching is like having a perfect memory that remembers everything useful and forgets everything wasteful - but coordinating millions of these memories is the real challenge"*

## 🎯 This Week's Mission
Master multi-layer caching architectures that power high-performance systems. Understand how companies like Redis, Facebook, and Google coordinate distributed caches to serve billions of users with millisecond response times.

---

## 📋 Prerequisites: Building on Previous Weeks

You should now understand:
- ✅ **CDN Concepts**: Edge caching and content distribution
- ✅ **Load Balancing**: Traffic distribution patterns
- ✅ **Network Latency**: Physical limits of data transfer
- ✅ **HTTP Protocols**: Request/response optimization techniques

### New Concepts We'll Master
- **Multi-Level Cache Hierarchies**: L1, L2, L3+ caching layers
- **Cache Coherence**: Keeping distributed caches synchronized
- **Eviction Policies**: Smart decisions on what to keep/remove
- **Cache Warming**: Proactive loading of anticipated data

---

## 🎪 Explain Like I'm 10: The Library Empire of Perfect Memory

### 📚 The Traditional Library Problem (No Caching)

Imagine a **magical library** where every book in the world exists, but there's only **one copy of each book** in a **giant vault underground**:

```
Student needs "How Dragons Work" book:

Student → 🏢 Library Entrance → 📞 Calls vault librarian
         ↓
Librarian → 🚇 Takes elevator down 20 floors → 🔍 Searches millions of books
         ↓
Found book! → 🚇 Takes elevator back up → 📖 Gives to student
         ↓
TIME: 30 minutes for one book!

Problems:
- Every book request takes 30 minutes (high latency)
- Librarian gets exhausted (server overload)
- Only one student served at a time (no concurrency)
- Popular books cause long queues (bottlenecks)
```

### 🧠 The Smart Library System (Multi-Level Caching)

Now imagine a **brilliant library system** with **memory helpers at every level**:

```
📖 Level 1: Student's Backpack (L1 Cache - Personal Memory)
   ├─ Capacity: 3 books
   ├─ Speed: Instant access (0 seconds)
   └─ Contents: Books currently studying

📚 Level 2: Classroom Bookshelf (L2 Cache - Shared Memory)  
   ├─ Capacity: 50 books
   ├─ Speed: Very fast (30 seconds)
   └─ Contents: Popular books for this class

🏫 Level 3: Floor Library (L3 Cache - Department Memory)
   ├─ Capacity: 1,000 books  
   ├─ Speed: Fast (5 minutes)
   └─ Contents: Popular books for this floor/department

🏢 Level 4: Building Library (L4 Cache - Campus Memory)
   ├─ Capacity: 50,000 books
   ├─ Speed: Moderate (15 minutes)  
   └─ Contents: Popular books across campus

🌍 Level 5: The Vault (Origin Server - All Knowledge)
   ├─ Capacity: All books ever written
   ├─ Speed: Slow (30 minutes)
   └─ Contents: Complete collection
```

### 🎭 The Magic Memory Rules

**Smart Retrieval Process:**
```
Student needs "Dragon Biology" book:

1. Check backpack → Not there → Continue
2. Check classroom shelf → Found it! → Take copy, put in backpack
3. Total time: 30 seconds instead of 30 minutes!

Student needs "Advanced Dragon Physics":

1. Check backpack → Not there → Continue  
2. Check classroom shelf → Not there → Continue
3. Check floor library → Found it! → Take copy
4. Put copy on classroom shelf for others
5. Put copy in backpack for me
6. Total time: 5 minutes + sharing benefit for classmates!

Student needs "Rare Dragon History":

1. Check all levels → Not found anywhere → Go to vault
2. Vault librarian finds it (30 minutes)
3. Put copies at ALL levels on way back up:
   - Building library (for all campus)
   - Floor library (for department) 
   - Classroom shelf (for class)
   - Personal backpack (for me)
4. Next student wanting same book: Gets it in 30 seconds!
```

**The Memory Helpers' Wisdom:**
- **Remember popular stuff longer** (frequently used books stay cached)
- **Forget old unused stuff** (make room for new popular books)
- **Share discoveries upward** (popular items bubble up to higher levels)
- **Predict what's needed next** (cache related books proactively)

---

## 🏗️ Principal Architect Depth: Distributed Cache Engineering

### 🚨 The Multi-Dimensional Cache Challenge

#### Cache Level Performance Characteristics
```
Performance vs Capacity Trade-offs:

L1 Cache (Application Memory):
├─ Latency: 1-10 microseconds
├─ Throughput: 1M+ operations/second  
├─ Capacity: 1GB - 64GB
├─ Scope: Single application instance
└─ Failure Impact: Process restart clears cache

L2 Cache (Local Redis/Memcached):
├─ Latency: 100-500 microseconds
├─ Throughput: 100K operations/second
├─ Capacity: 64GB - 1TB  
├─ Scope: Single server
└─ Failure Impact: Server restart clears cache

L3 Cache (Distributed Cache Cluster):
├─ Latency: 1-5 milliseconds
├─ Throughput: 10K operations/second per node
├─ Capacity: 1TB - 100TB across cluster
├─ Scope: Multiple servers, data centers
└─ Failure Impact: Individual node failure, not total loss

L4 Cache (Regional Database Replicas):
├─ Latency: 10-50 milliseconds  
├─ Throughput: 1K operations/second
├─ Capacity: 100TB - 10PB
├─ Scope: Geographic region
└─ Failure Impact: Regional failover available

L5 Origin (Primary Database):
├─ Latency: 50-200+ milliseconds
├─ Throughput: 100 operations/second (complex queries)
├─ Capacity: Unlimited (disk-based)
├─ Scope: Authoritative source
└─ Failure Impact: System-wide outage
```

### 🧠 Advanced Caching Strategies

#### Cache Coherence Protocols
```
Problem: Multiple cache levels have different versions of the same data

Write-Through Strategy:
Write Request → L1 Cache → L2 Cache → L3 Cache → Database
├─ Pros: All levels always consistent  
├─ Cons: Write latency = slowest level
└─ Use Case: Financial systems requiring strict consistency

Write-Behind (Write-Back) Strategy:  
Write Request → L1 Cache → Background sync to lower levels
├─ Pros: Fast writes, high performance
├─ Cons: Risk of data loss if L1 fails before sync
└─ Use Case: Analytics, social media feeds

Write-Around Strategy:
Write Request → Database directly, bypass caches → Invalidate cache entries
├─ Pros: Doesn't pollute cache with infrequently read writes
├─ Cons: Next read will be cache miss
└─ Use Case: Large file uploads, bulk data imports
```

#### Intelligent Eviction Policies
```
LRU (Least Recently Used) - The Classic:
Cache tracks access time for each item
When full → Remove oldest accessed item
├─ Good for: Temporal locality (recently used = likely reused)
├─ Bad for: Cyclical access patterns
└─ Implementation: Doubly-linked list + hashtable

LFU (Least Frequently Used) - The Counter:
Cache tracks access count for each item  
When full → Remove least accessed item
├─ Good for: Long-term popularity patterns
├─ Bad for: Changing popularity (new viral content)
└─ Implementation: Frequency counters + min-heap

ARC (Adaptive Replacement Cache) - The Smart One:
Maintains TWO LRU lists: recent items + frequent items
Dynamically adjusts between recency vs frequency
├─ Good for: Adapting to changing access patterns
├─ Bad for: Complex implementation, higher memory overhead
└─ Implementation: Four LRU lists + adaptive parameters

TinyLFU - The Modern Champion:
Combines frequency estimation with recency
Uses probabilistic data structures (Count-Min Sketch)
├─ Good for: High performance with low memory overhead
├─ Bad for: Probabilistic (tiny chance of errors)
└─ Implementation: Bloom filters + frequency sketching
```

### 🔥 Cache Architecture Patterns

#### Pattern 1: Cache-Aside (Lazy Loading)
```
Application-Controlled Caching:

Read Flow:
1. App checks cache for data
2. If hit → Return cached data  
3. If miss → Query database → Cache result → Return data

Write Flow:  
1. App writes to database
2. App invalidates/updates cache entry
3. Next read will refresh cache

Code Pattern:
```
def get_user(user_id):
    # Try cache first
    user = cache.get(f"user:{user_id}")
    if user:
        return user  # Cache hit!
    
    # Cache miss - query database
    user = database.query(f"SELECT * FROM users WHERE id = {user_id}")
    
    # Cache for future requests
    cache.set(f"user:{user_id}", user, ttl=3600)
    return user

def update_user(user_id, data):
    # Update database
    database.update(f"UPDATE users SET ... WHERE id = {user_id}")
    
    # Invalidate cache to force refresh
    cache.delete(f"user:{user_id}")
```

Pros: Simple, app controls cache logic, works with any database
Cons: Cache miss penalty, potential inconsistency, extra code complexity
```

#### Pattern 2: Read-Through Cache
```
Cache-Managed Database Access:

Read Flow:
1. App requests data from cache
2. Cache checks if data exists locally
3. If miss → Cache automatically queries database → Stores result → Returns data
4. If hit → Cache returns data directly

Code Pattern:
```
# Cache handles database interaction transparently
user = smart_cache.get(f"user:{user_id}")  
# Cache automatically queries database on miss

def cache_loader_function(key):
    # This function is called by cache on miss
    user_id = key.split(":")[1] 
    return database.query(f"SELECT * FROM users WHERE id = {user_id}")

smart_cache.register_loader(cache_loader_function)
```

Pros: Simpler application code, guaranteed cache population
Cons: Cache tied to specific database, harder to customize
```

#### Pattern 3: Write-Through Cache  
```
Synchronous Cache + Database Updates:

Write Flow:
1. App writes data to cache
2. Cache immediately writes to database  
3. Both cache and database updated before returning success

Read Flow:
1. App reads from cache (always up-to-date)

Code Pattern:
```
def update_user(user_id, data):
    # Write-through cache handles both cache and database
    cache.set(f"user:{user_id}", data, write_through=True)
    # Cache automatically updates database before returning

def get_user(user_id):
    # Always read from cache (guaranteed fresh)
    return cache.get(f"user:{user_id}")
```

Pros: Strong consistency, simple read logic
Cons: Slower writes, database becomes bottleneck
```

---

## 🌍 Real-World Implementation Examples

### 📊 Case Study 1: Facebook's Multi-Layer Cache Architecture

**The Challenge**: Serve 3+ billion users with sub-millisecond response times

```
Facebook's TAO (The Associations and Objects) Cache Hierarchy:

L1: Application Server Cache (In-Memory)
├─ Technology: Custom C++ in-memory cache
├─ Capacity: 32GB per server
├─ Hit Rate: 80% for active user data
├─ Latency: 0.1ms average
└─ Scope: Single web server process

L2: Local Memcached Cluster (Server Rack)
├─ Technology: Modified Memcached with Facebook optimizations
├─ Capacity: 1TB per rack (16 servers × 64GB)
├─ Hit Rate: 95% for popular content  
├─ Latency: 0.5ms average
└─ Scope: Server rack (50-100 web servers)

L3: Regional Cache Cluster (Data Center)
├─ Technology: Distributed Memcached with consistent hashing
├─ Capacity: 100TB per data center
├─ Hit Rate: 99% for regional content
├─ Latency: 2ms average  
└─ Scope: Entire data center (thousands of servers)

L4: Cross-Region Cache (Global)
├─ Technology: MySQL read replicas + TAO caching layer
├─ Capacity: 1PB+ across regions
├─ Hit Rate: 99.9% for global content
├─ Latency: 10-50ms (depending on geography)
└─ Scope: Multiple data centers worldwide

L5: Master Database (Authoritative)
├─ Technology: Sharded MySQL with custom storage engines
├─ Capacity: Multi-petabyte social graph
├─ Hit Rate: 100% (by definition)
├─ Latency: 100-500ms for complex queries
└─ Scope: Authoritative source for all social data
```

**Facebook's Cache Intelligence**:
```
Smart Cache Warming:
├─ Friend Graph Prediction: Pre-load friends' posts when user logs in
├─ Timeline Generation: Background processing of news feed
├─ Photo Optimization: Multiple resolution caching based on device type
└─ Real-time Events: Live updates bypass cache for immediate consistency

Cache Invalidation Strategy:
├─ Write-through for critical data (user profiles, privacy settings)
├─ Eventual consistency for social content (posts, comments, likes) 
├─ Geographic clustering: Regional cache invalidation
└─ Smart batching: Group invalidations to reduce database load

Performance Results:
├─ 99.9% of reads served from cache (0.1% hit database)
├─ Average page load time: <200ms globally
├─ Cache efficiency: Handles 10M+ queries per second per data center
└─ Cost savings: 100x reduction in database load
```

### 📊 Case Study 2: Redis Labs' Multi-Tenant Cache Architecture

**The Mission**: Provide cache-as-a-service for 8,000+ companies

```
Redis Enterprise Multi-Layer Architecture:

Client-Side Cache (Application Level):
├─ Technology: Redis client libraries with local caching
├─ Capacity: 100MB - 1GB per application instance
├─ Hit Rate: 60-80% for session data
├─ Use Case: Session state, user preferences, temporary data

Proxy Cache (Network Level):
├─ Technology: Redis proxy with intelligent routing
├─ Capacity: 10GB per proxy instance  
├─ Hit Rate: 85-95% for routing decisions
├─ Use Case: Connection pooling, query routing, basic caching

Cluster Cache (Database Level):
├─ Technology: Redis Cluster with automatic sharding
├─ Capacity: 100GB - 10TB per cluster
├─ Hit Rate: 95-99% for application data
├─ Use Case: Primary application cache, session store

Persistent Cache (Storage Level):  
├─ Technology: Redis on Flash (RAM + SSD hybrid)
├─ Capacity: 10TB+ per node with SSD backing
├─ Hit Rate: 99%+ for warm data  
├─ Use Case: Large datasets, persistent caching
```

**Redis Enterprise Innovations**:
```
Active-Active Geo-Replication:
├─ Conflict-free Replicated Data Types (CRDTs)
├─ Multi-master replication across regions
├─ Automatic conflict resolution for concurrent writes
└─ <1ms local latency with global consistency

Intelligent Tiering:
├─ Hot data: Pure RAM (sub-millisecond access)
├─ Warm data: RAM + Flash (1-5ms access)  
├─ Cold data: Compressed on Flash (10-50ms access)
└─ Automatic promotion/demotion based on access patterns

Advanced Eviction:
├─ Machine learning-based access prediction  
├─ Time-series analysis for cyclical patterns
├─ Business priority weighting (VIP customer data stays cached)
└─ Cost-aware eviction (expensive-to-compute data prioritized)
```

### 📊 Case Study 3: Netflix's EVCache (Ephemeral Volatile Cache)

**The Scale**: Cache movie recommendations for 230M+ subscribers

```
Netflix EVCache Architecture:

Browser Cache (Client Level):
├─ Technology: HTTP caching + browser local storage
├─ Capacity: 50MB per browser 
├─ Duration: 24 hours for movie artwork, metadata
├─ Hit Rate: 70% for repeated browsing sessions
└─ Purpose: Reduce CDN requests for UI assets

API Gateway Cache (Edge Level):
├─ Technology: Zuul proxy with embedded caching  
├─ Capacity: 1GB per gateway instance
├─ Duration: 5 minutes for popular API responses
├─ Hit Rate: 60% for trending content APIs
└─ Purpose: Reduce backend microservice calls

EVCache Cluster (Application Level):
├─ Technology: Modified Memcached optimized for AWS
├─ Capacity: 1TB+ per cluster across multiple zones
├─ Duration: 1-24 hours based on content type  
├─ Hit Rate: 99%+ for personalization data
└─ Purpose: User recommendations, viewing history, preferences

Cassandra Cache (Data Level):
├─ Technology: Distributed NoSQL with built-in caching
├─ Capacity: 100TB+ across global clusters
├─ Duration: Persistent with TTL-based expiration
├─ Hit Rate: 95% for metadata queries
└─ Purpose: Movie metadata, user profiles, viewing analytics
```

---

## 🧪 Hands-On Lab: Build Multi-Level Cache System

### 🔍 Experiment 1: Implement Cache-Aside Pattern

**Create a smart caching wrapper:**

```python
import redis
import time
import json
from typing import Any, Optional

class SmartCache:
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port)
        self.local_cache = {}  # L1: In-memory cache
        self.stats = {
            'l1_hits': 0, 'l1_misses': 0,
            'l2_hits': 0, 'l2_misses': 0,
            'database_queries': 0
        }
    
    def get(self, key: str, database_loader=None) -> Optional[Any]:
        # L1 Cache check (local memory)
        if key in self.local_cache:
            self.stats['l1_hits'] += 1
            return self.local_cache[key]
        
        self.stats['l1_misses'] += 1
        
        # L2 Cache check (Redis)
        redis_value = self.redis_client.get(key)
        if redis_value:
            self.stats['l2_hits'] += 1
            value = json.loads(redis_value)
            
            # Promote to L1 cache
            self.local_cache[key] = value
            return value
        
        self.stats['l2_misses'] += 1
        
        # Database fallback
        if database_loader:
            self.stats['database_queries'] += 1
            value = database_loader(key)
            
            # Cache at all levels
            self.set(key, value, ttl=3600)
            return value
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        # Store in L1 (local memory)  
        self.local_cache[key] = value
        
        # Store in L2 (Redis)
        self.redis_client.setex(key, ttl, json.dumps(value))
    
    def invalidate(self, key: str):
        # Remove from all cache levels
        if key in self.local_cache:
            del self.local_cache[key]
        self.redis_client.delete(key)
    
    def get_stats(self):
        total_requests = sum(self.stats.values()) - self.stats['database_queries']
        l1_hit_rate = self.stats['l1_hits'] / total_requests * 100 if total_requests > 0 else 0
        l2_hit_rate = self.stats['l2_hits'] / total_requests * 100 if total_requests > 0 else 0
        
        return {
            'l1_hit_rate': f"{l1_hit_rate:.1f}%",
            'l2_hit_rate': f"{l2_hit_rate:.1f}%", 
            'database_hit_rate': f"{self.stats['database_queries'] / total_requests * 100:.1f}%" if total_requests > 0 else "0%",
            **self.stats
        }

# Example usage with simulated database
def simulate_database_query(key):
    """Simulate expensive database operation"""
    time.sleep(0.1)  # Simulate 100ms database query
    user_id = key.split(':')[1]
    return {
        'id': user_id,
        'name': f'User {user_id}',
        'email': f'user{user_id}@example.com',
        'last_login': time.time()
    }

# Test the caching system
cache = SmartCache()

# Simulate user requests
for i in range(100):
    user_id = str(i % 10)  # 10 different users, repeated access
    key = f'user:{user_id}'
    
    user_data = cache.get(key, database_loader=simulate_database_query)
    print(f"Retrieved user: {user_data['name']}")

print("\nCache Performance:")
print(json.dumps(cache.get_stats(), indent=2))
```

### 🔍 Experiment 2: Advanced Eviction Policies

**Implement and compare LRU vs LFU caching:**

```python
from collections import OrderedDict
import heapq
import time

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()
    
    def get(self, key):
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def set(self, key, value):
        if key in self.cache:
            # Update existing key
            self.cache.move_to_end(key)
            self.cache[key] = value
        else:
            # Add new key
            if len(self.cache) >= self.capacity:
                # Remove least recently used (first item)
                self.cache.popitem(last=False)
            self.cache[key] = value

class LFUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        self.frequencies = {}
        self.frequency_groups = {}
        self.min_frequency = 0
    
    def get(self, key):
        if key in self.cache:
            self._update_frequency(key)
            return self.cache[key]
        return None
    
    def set(self, key, value):
        if self.capacity == 0:
            return
            
        if key in self.cache:
            # Update existing
            self.cache[key] = value
            self._update_frequency(key)
        else:
            # Add new
            if len(self.cache) >= self.capacity:
                self._evict_least_frequent()
            
            self.cache[key] = value
            self.frequencies[key] = 1
            self.frequency_groups.setdefault(1, set()).add(key)
            self.min_frequency = 1
    
    def _update_frequency(self, key):
        old_freq = self.frequencies[key]
        new_freq = old_freq + 1
        
        # Remove from old frequency group
        self.frequency_groups[old_freq].remove(key)
        if not self.frequency_groups[old_freq] and old_freq == self.min_frequency:
            self.min_frequency += 1
        
        # Add to new frequency group
        self.frequencies[key] = new_freq
        self.frequency_groups.setdefault(new_freq, set()).add(key)
    
    def _evict_least_frequent(self):
        # Remove any key from the min frequency group
        key_to_remove = self.frequency_groups[self.min_frequency].pop()
        del self.cache[key_to_remove]
        del self.frequencies[key_to_remove]

# Performance comparison
def test_cache_performance(cache, access_pattern):
    hits = 0
    total = 0
    
    start_time = time.time()
    
    for key, value in access_pattern:
        result = cache.get(key)
        if result is None:
            cache.set(key, value)
        else:
            hits += 1
        total += 1
    
    end_time = time.time()
    
    return {
        'hit_rate': hits / total * 100,
        'execution_time': end_time - start_time,
        'total_requests': total
    }

# Test with different access patterns
def generate_temporal_pattern():
    """Recent items accessed repeatedly"""
    pattern = []
    for i in range(1000):
        # 80% of accesses to recent items (temporal locality)
        if i % 5 < 4:
            key = f"recent_{i % 20}"
        else:
            key = f"old_{i % 100}"
        pattern.append((key, f"value_{i}"))
    return pattern

def generate_frequency_pattern():
    """Some items accessed much more frequently"""
    pattern = []
    for i in range(1000):
        # 80% of accesses to popular items (frequency locality)  
        if i % 5 < 4:
            key = f"popular_{i % 5}"
        else:
            key = f"rare_{i % 50}"
        pattern.append((key, f"value_{i}"))
    return pattern

# Compare cache performance
cache_size = 20

print("Testing with Temporal Access Pattern (LRU should win):")
lru_cache = LRUCache(cache_size)
lfu_cache = LFUCache(cache_size)

temporal_pattern = generate_temporal_pattern()
lru_results = test_cache_performance(lru_cache, temporal_pattern)
lfu_results = test_cache_performance(lfu_cache, temporal_pattern)

print(f"LRU Cache: {lru_results['hit_rate']:.1f}% hit rate")
print(f"LFU Cache: {lfu_results['hit_rate']:.1f}% hit rate")

print("\nTesting with Frequency Access Pattern (LFU should win):")
lru_cache = LRUCache(cache_size) 
lfu_cache = LFUCache(cache_size)

frequency_pattern = generate_frequency_pattern()
lru_results = test_cache_performance(lru_cache, frequency_pattern)
lfu_results = test_cache_performance(lfu_cache, frequency_pattern)

print(f"LRU Cache: {lru_results['hit_rate']:.1f}% hit rate")
print(f"LFU Cache: {lfu_results['hit_rate']:.1f}% hit rate")
```

### 🔍 Experiment 3: Cache Warming and Preloading

**Implement intelligent cache warming:**

```python
import asyncio
import aioredis
import json
from datetime import datetime, timedelta

class CacheWarmer:
    def __init__(self, redis_url='redis://localhost'):
        self.redis = None
        self.warming_strategies = {}
    
    async def connect(self):
        self.redis = await aioredis.from_url(redis_url)
    
    def register_strategy(self, name, strategy_func):
        """Register a cache warming strategy"""
        self.warming_strategies[name] = strategy_func
    
    async def warm_cache(self, strategy_names=None):
        """Execute cache warming strategies"""
        if strategy_names is None:
            strategy_names = self.warming_strategies.keys()
        
        warming_tasks = []
        for name in strategy_names:
            if name in self.warming_strategies:
                task = asyncio.create_task(
                    self._execute_strategy(name, self.warming_strategies[name])
                )
                warming_tasks.append(task)
        
        results = await asyncio.gather(*warming_tasks, return_exceptions=True)
        return dict(zip(strategy_names, results))
    
    async def _execute_strategy(self, name, strategy_func):
        """Execute a single warming strategy"""
        start_time = datetime.now()
        try:
            items_warmed = await strategy_func(self.redis)
            duration = datetime.now() - start_time
            return {
                'success': True,
                'items_warmed': items_warmed,
                'duration_ms': duration.total_seconds() * 1000
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'duration_ms': (datetime.now() - start_time).total_seconds() * 1000
            }

# Example warming strategies
async def warm_popular_users(redis):
    """Pre-load popular user profiles"""
    popular_user_ids = ['user:1', 'user:2', 'user:3', 'user:4', 'user:5']
    
    warming_data = {}
    for user_id in popular_user_ids:
        # Simulate fetching from database
        user_data = {
            'id': user_id,
            'name': f'Popular User {user_id.split(":")[1]}',
            'followers': 10000 + int(user_id.split(":")[1]) * 1000,
            'last_active': datetime.now().isoformat()
        }
        
        # Cache with 1 hour TTL
        await redis.setex(user_id, 3600, json.dumps(user_data))
        warming_data[user_id] = user_data
    
    return len(popular_user_ids)

async def warm_trending_content(redis):
    """Pre-load trending posts and content"""
    trending_posts = [f'post:trending:{i}' for i in range(1, 11)]
    
    for post_id in trending_posts:
        post_data = {
            'id': post_id,
            'title': f'Trending Post {post_id.split(":")[-1]}',
            'views': 50000 + int(post_id.split(":")[-1]) * 5000,
            'engagement_score': 0.85,
            'cached_at': datetime.now().isoformat()
        }
        
        # Cache trending content for 30 minutes
        await redis.setex(post_id, 1800, json.dumps(post_data))
    
    return len(trending_posts)

async def warm_session_data(redis):
    """Pre-warm session storage for expected users"""
    # Simulate pre-loading session data for users likely to be active
    active_sessions = [f'session:{i}' for i in range(1, 21)]
    
    for session_id in active_sessions:
        session_data = {
            'user_id': f'user:{session_id.split(":")[1]}', 
            'login_time': datetime.now().isoformat(),
            'preferences': {'theme': 'dark', 'language': 'en'},
            'temporary_data': {}
        }
        
        # Session cache for 24 hours
        await redis.setex(session_id, 86400, json.dumps(session_data))
    
    return len(active_sessions)

# Example usage
async def main():
    warmer = CacheWarmer()
    await warmer.connect()
    
    # Register warming strategies
    warmer.register_strategy('popular_users', warm_popular_users)
    warmer.register_strategy('trending_content', warm_trending_content)
    warmer.register_strategy('session_data', warm_session_data)
    
    print("Starting cache warming...")
    start_time = datetime.now()
    
    # Warm cache with all strategies
    results = await warmer.warm_cache()
    
    total_duration = datetime.now() - start_time
    
    print(f"\nCache warming completed in {total_duration.total_seconds():.2f}s")
    print("\nResults by strategy:")
    
    total_items = 0
    for strategy, result in results.items():
        if result['success']:
            print(f"✅ {strategy}: {result['items_warmed']} items in {result['duration_ms']:.1f}ms")
            total_items += result['items_warmed']
        else:
            print(f"❌ {strategy}: Failed - {result['error']}")
    
    print(f"\nTotal items warmed: {total_items}")

# Run the cache warming
# asyncio.run(main())
```

---

## 🎨 Visual Learning: Cache Hierarchy Architectures

### 🏗️ Multi-Level Cache Flow
```
Cache Request Flow Visualization:

    👤 User Request: "Get user profile for user:12345"
         ↓
    ┌─────────────────────────────────────────┐
    │ L1: Application Memory (HashMap)        │ → 0.001ms latency
    │ Status: MISS (user not in memory)       │
    └─────────────────────────────────────────┘
         ↓
    ┌─────────────────────────────────────────┐  
    │ L2: Local Redis (Same Server)           │ → 0.5ms latency
    │ Status: HIT (user found in Redis!)      │ ✅
    │ Action: Promote to L1 + Return data     │
    └─────────────────────────────────────────┘
         ↓
    📦 Cache Response: User data returned in 0.5ms
       (Database query avoided - saved 50-200ms!)

Cache Population Flow (On L2 Miss):

    👤 User Request: "Get user profile for user:99999"  
         ↓
    L1 Cache: MISS → L2 Cache: MISS → L3 Cluster: MISS
         ↓
    ┌─────────────────────────────────────────┐
    │ 🗃️  Database Query (Last Resort)         │ → 100ms latency
    │ SELECT * FROM users WHERE id = 99999    │
    └─────────────────────────────────────────┘
         ↓
    ┌─────────────────────────────────────────┐
    │ 📤 Cache Population (Reverse Flow)       │
    │ Database → L3 → L2 → L1 → User          │
    │ Future requests: 0.5ms instead of 100ms │
    └─────────────────────────────────────────┘
```

### 📊 Cache Performance Pyramid
```
Cache Performance Characteristics:

            🔥 L1: Application Memory 🔥
           ├─ Latency: 0.001 - 0.01ms
           ├─ Capacity: 64MB - 8GB  
           ├─ Hit Rate: 60-80%
           └─ Scope: Single process
                    ↓
          ⚡ L2: Local Cache Server ⚡
         ├─ Latency: 0.1 - 1ms
         ├─ Capacity: 1GB - 1TB
         ├─ Hit Rate: 85-95% 
         └─ Scope: Single machine
                    ↓
        🌐 L3: Distributed Cache Cluster 🌐  
       ├─ Latency: 1 - 10ms
       ├─ Capacity: 1TB - 100TB
       ├─ Hit Rate: 95-99%
       └─ Scope: Data center
                    ↓
      🏢 L4: Regional Database Replicas 🏢
     ├─ Latency: 10 - 50ms  
     ├─ Capacity: 100TB - 10PB
     ├─ Hit Rate: 99-99.9%
     └─ Scope: Geographic region
                    ↓
    🗄️ L5: Master Database (Origin) 🗄️
   ├─ Latency: 50 - 500ms
   ├─ Capacity: Unlimited
   ├─ Hit Rate: 100% (authoritative)
   └─ Scope: Global truth source

Performance Formula:
Average Response Time = 
  (L1_Hit_Rate × L1_Latency) + 
  (L2_Hit_Rate × L2_Latency) + 
  ... + 
  (Database_Hit_Rate × Database_Latency)

Example Calculation:
= (0.70 × 0.01ms) + (0.25 × 0.5ms) + (0.04 × 5ms) + (0.01 × 100ms)
= 0.007ms + 0.125ms + 0.2ms + 1ms  
= 1.332ms average (vs 100ms without caching!)
```

### 🔄 Cache Coherence Strategies
```
Multi-Level Cache Consistency:

Write-Through Strategy:
┌─────────────────────────────────────────────────────────────┐
│                    Write Request                            │
└─────────────────────────────────────────────────────────────┘
    ↓           ↓           ↓           ↓
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│   L1    │→│   L2    │→│   L3    │→│Database │
│ Memory  │ │ Redis   │ │Cluster  │ │ MySQL   │
└─────────┘ └─────────┘ └─────────┘ └─────────┘
Pros: Strong consistency, all levels updated
Cons: Write latency = slowest level (database)

Write-Behind Strategy:  
┌─────────────────────────────────────────────────────────────┐
│                    Write Request                            │  
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────┐    Background Sync Jobs
│   L1    │ ┌──────────────────────────────────┐
│ Memory  │→│ Async Workers Update L2→L3→DB    │
└─────────┘ └──────────────────────────────────┘
Pros: Fast writes, high throughput
Cons: Risk of data loss, eventual consistency

Invalidate-on-Write Strategy:
┌─────────────────────────────────────────────────────────────┐
│                    Write Request                            │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────┐                           ┌─────────┐
│Database │ ← Direct Write            │ Cache   │ ← Invalidate
│ MySQL   │                           │ Layers  │   All Levels  
└─────────┘                           └─────────┘
Pros: No cache pollution, consistency guaranteed
Cons: Next read will be cache miss (slower)
```

---

## 🎯 Week 7 Wrap-Up: Caching Architecture Mastery

### 🧠 Mental Models to Internalize

1. **Cache Hierarchy = Memory Palace**: Each level stores what it can remember best
2. **Cache Coherence = Family Updates**: Keeping everyone informed of changes
3. **Eviction Policies = Smart Forgetting**: Make room for more important memories
4. **Cache Warming = Preparation**: Load anticipated data before it's needed

### 🏆 Principal Architect Decision Framework

**Cache Level Selection:**
- **L1 (Application Memory)**: Session data, user preferences, temp calculations
- **L2 (Local Cache Server)**: Popular content, API responses, computed results  
- **L3 (Distributed Cache)**: Shared data, cross-service communication
- **L4+ (Database Replicas)**: Large datasets, analytics, backup access

**Eviction Policy Selection:**
- **LRU**: Temporal locality workloads (recently used = likely reused)
- **LFU**: Popularity-based workloads (some items always popular)
- **ARC/TinyLFU**: Mixed workloads with changing access patterns

### 🚨 Common Caching Architecture Mistakes

❌ **Cache stampede** = Multiple requests for same missing data overwhelm database
❌ **Cache pollution** = Storing data that's never accessed again
❌ **Inconsistent TTLs** = Some levels expire before others, causing confusion
❌ **No monitoring** = Can't optimize what you don't measure
✅ **Circuit breakers** = Graceful degradation when cache systems fail

### 🔮 Preview: Next Week's Deep Dive
**Week 8: Microservices Communication Patterns**

We'll explore how distributed systems coordinate across hundreds of services. You'll learn about service meshes, API gateways, and the communication patterns that keep systems like Uber, Netflix, and Google running smoothly at planetary scale.

---

## 🤔 Reflection Questions

Before moving to Week 8, ensure you can answer:

1. **ELI5**: "Why does your phone get faster at loading apps the more you use it, but sometimes slows down when you haven't used an app in weeks?"

2. **Architect Level**: "Design a caching strategy for a global e-commerce platform during Black Friday. How do you handle flash sales where millions of users want the same product simultaneously?"

3. **Technical Deep-Dive**: "Your L2 cache shows 95% hit rate but L1 shows only 60%. Users still report slow performance. What's happening and how do you fix it?"

4. **Business Analysis**: "Calculate the infrastructure cost savings of implementing a 4-level cache hierarchy for a service handling 1 billion requests per day with 2% database hit rate vs no caching."

---

*"The best cache is the one that's invisible - users never wait, developers never worry, and the system just works."*

**Next**: [Week 8 - Microservices Communication](08-Week8-Microservices-Communication.md)