# Design Distributed Cache System (Redis Cluster) - Complete System Design

**Difficulty:** ⭐⭐⭐⭐⭐  
**Interview Frequency:** Very High (All tech companies, 40 LPA+)  
**Time to Complete:** 40-45 minutes  
**Real-World Examples:** Redis Cluster, Memcached, AWS ElastiCache

---

## 📋 Problem Statement

**Design a distributed caching system that can:**
- Handle 1 million requests per second
- Store 1 TB of data
- Provide <1ms p99 latency
- Support multiple eviction policies (LRU, LFU, TTL)
- Handle cache invalidation strategies
- Provide high availability (99.99% uptime)
- Scale horizontally
- Support consistent hashing for data distribution
- Handle cache stampede/thundering herd
- Support cache warming strategies

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                REDIS CLUSTER ARCHITECTURE                     │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Hash Slots: 16,384 slots distributed across nodes           │
│  Sharding: Consistent hashing                                │
│  Replication: Primary-Replica (async replication)            │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  NODE 1 (Slots 0-5460)                                │ │
│  │  ┌──────────┐           ┌──────────┐                  │ │
│  │  │ Primary  │──────────▶│ Replica  │                  │ │
│  │  │ Master1  │           │ Slave1   │                  │ │
│  │  └──────────┘           └──────────┘                  │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  NODE 2 (Slots 5461-10922)                            │ │
│  │  ┌──────────┐           ┌──────────┐                  │ │
│  │  │ Primary  │──────────▶│ Replica  │                  │ │
│  │  │ Master2  │           │ Slave2   │                  │ │
│  │  └──────────┘           └──────────┘                  │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  NODE 3 (Slots 10923-16383)                           │ │
│  │  ┌──────────┐           ┌──────────┐                  │ │
│  │  │ Primary  │──────────▶│ Replica  │                  │ │
│  │  │ Master3  │           │ Slave3   │                  │ │
│  │  └──────────┘           └──────────┘                  │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  Key Distribution:                                           │
│  slot = CRC16(key) % 16384                                   │
│  → Route to node owning that slot                            │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                  CACHE PATTERNS                               │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  1. CACHE-ASIDE (Lazy Loading)                               │
│     ┌─────────────────────────────────────────────────────┐ │
│     │ def get_user(user_id):                              │ │
│     │     # Check cache                                    │ │
│     │     cached = redis.get(f"user:{user_id}")           │ │
│     │     if cached:                                       │ │
│     │         return json.loads(cached)                    │ │
│     │                                                      │ │
│     │     # Cache miss - query DB                         │ │
│     │     user = db.query("SELECT * FROM users ...")      │ │
│     │                                                      │ │
│     │     # Update cache                                   │ │
│     │     redis.setex(f"user:{user_id}", 3600, ...)       │ │
│     │                                                      │ │
│     │     return user                                      │ │
│     └─────────────────────────────────────────────────────┘ │
│                                                               │
│  2. WRITE-THROUGH                                            │
│     ┌─────────────────────────────────────────────────────┐ │
│     │ def update_user(user_id, data):                     │ │
│     │     # Update cache first                             │ │
│     │     redis.setex(f"user:{user_id}", 3600, ...)       │ │
│     │                                                      │ │
│     │     # Then update DB                                 │ │
│     │     db.update("UPDATE users SET ...")               │ │
│     └─────────────────────────────────────────────────────┘ │
│                                                               │
│  3. WRITE-BEHIND (Write-Back)                                │
│     ┌─────────────────────────────────────────────────────┐ │
│     │ def update_user(user_id, data):                     │ │
│     │     # Update cache                                   │ │
│     │     redis.setex(f"user:{user_id}", 3600, ...)       │ │
│     │                                                      │ │
│     │     # Queue for async DB write                       │ │
│     │     queue.enqueue("db_write", user_id, data)        │ │
│     └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## 💻 Implementation

### **1. Cache Client with Consistent Hashing**

```python
import hashlib
import bisect
from typing import List, Dict, Any, Optional

class ConsistentHashRing:
    """
    Consistent hashing for distributed cache
    """
    
    def __init__(self, nodes: List[str], virtual_nodes: int = 150):
        self.virtual_nodes = virtual_nodes
        self.ring: Dict[int, str] = {}
        self.sorted_keys: List[int] = []
        
        for node in nodes:
            self.add_node(node)
    
    def _hash(self, key: str) -> int:
        """Hash function (CRC16 for Redis compatibility)"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def add_node(self, node: str):
        """Add node with virtual nodes"""
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:{i}"
            hash_val = self._hash(virtual_key)
            self.ring[hash_val] = node
            bisect.insort(self.sorted_keys, hash_val)
    
    def remove_node(self, node: str):
        """Remove node"""
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:{i}"
            hash_val = self._hash(virtual_key)
            del self.ring[hash_val]
            self.sorted_keys.remove(hash_val)
    
    def get_node(self, key: str) -> str:
        """Get node for key"""
        if not self.ring:
            return None
        
        hash_val = self._hash(key)
        
        # Find first node >= hash_val
        idx = bisect.bisect_right(self.sorted_keys, hash_val)
        
        # Wrap around if needed
        if idx == len(self.sorted_keys):
            idx = 0
        
        return self.ring[self.sorted_keys[idx]]


class DistributedCache:
    """
    Distributed cache client
    """
    
    def __init__(self, redis_nodes: List[str]):
        import redis
        
        # Create connection pool for each node
        self.connections = {}
        for node in redis_nodes:
            host, port = node.split(':')
            self.connections[node] = redis.Redis(
                host=host,
                port=int(port),
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=1,
                retry_on_timeout=True,
                max_connections=50
            )
        
        # Consistent hash ring
        self.hash_ring = ConsistentHashRing(redis_nodes)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        node = self.hash_ring.get_node(key)
        
        try:
            return self.connections[node].get(key)
        except Exception as e:
            # Fallback to next node
            print(f"Error getting key {key} from {node}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL"""
        node = self.hash_ring.get_node(key)
        
        try:
            return self.connections[node].setex(key, ttl, value)
        except Exception as e:
            print(f"Error setting key {key} on {node}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key"""
        node = self.hash_ring.get_node(key)
        
        try:
            return self.connections[node].delete(key) > 0
        except Exception as e:
            print(f"Error deleting key {key} from {node}: {e}")
            return False
    
    def mget(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple keys (batched by node)"""
        
        # Group keys by node
        node_keys = {}
        for key in keys:
            node = self.hash_ring.get_node(key)
            if node not in node_keys:
                node_keys[node] = []
            node_keys[node].append(key)
        
        # Fetch from each node in parallel
        results = {}
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(node_keys)) as executor:
            futures = {}
            
            for node, node_key_list in node_keys.items():
                future = executor.submit(
                    self.connections[node].mget,
                    node_key_list
                )
                futures[future] = (node, node_key_list)
            
            for future in concurrent.futures.as_completed(futures):
                node, node_key_list = futures[future]
                try:
                    values = future.result()
                    for key, value in zip(node_key_list, values):
                        results[key] = value
                except Exception as e:
                    print(f"Error in mget from {node}: {e}")
        
        return results


### **2. Cache Invalidation Strategies**

```python
from enum import Enum
from typing import Set

class InvalidationStrategy(Enum):
    TTL = "ttl"  # Time-based expiration
    EVENT_DRIVEN = "event_driven"  # Invalidate on DB write
    VERSION_BASED = "version_based"  # Version numbers
    TAG_BASED = "tag_based"  # Group invalidation

class CacheInvalidator:
    """
    Handle cache invalidation
    """
    
    def __init__(self, cache: DistributedCache):
        self.cache = cache
    
    def invalidate_by_pattern(self, pattern: str):
        """
        Invalidate all keys matching pattern
        Warning: Expensive operation!
        """
        # In production, use Redis SCAN instead of KEYS
        # to avoid blocking
        pass
    
    def invalidate_by_tags(self, tags: Set[str]):
        """
        Tag-based invalidation
        
        Example:
        SET user:123 "data"
        SADD tag:user_posts user:123 post:456 post:789
        
        To invalidate: DEL all keys in tag:user_posts
        """
        for tag in tags:
            tag_key = f"tag:{tag}"
            
            # Get all keys with this tag
            keys = self.cache.connections[0].smembers(tag_key)
            
            # Delete them
            if keys:
                pipeline = self.cache.connections[0].pipeline()
                for key in keys:
                    pipeline.delete(key)
                pipeline.delete(tag_key)
                pipeline.execute()
    
    def version_based_get(self, key: str, version: int) -> Optional[Any]:
        """
        Version-based caching
        """
        versioned_key = f"{key}:v{version}"
        return self.cache.get(versioned_key)
    
    def version_based_set(self, key: str, version: int, value: Any, ttl: int):
        """Set with version"""
        versioned_key = f"{key}:v{version}"
        return self.cache.set(versioned_key, value, ttl)


### **3. Prevent Cache Stampede**

```python
import time
import random

class CacheStampedeProtection:
    """
    Prevent thundering herd when cache expires
    """
    
    def __init__(self, cache: DistributedCache):
        self.cache = cache
    
    def get_with_lock(self, key: str, compute_fn, ttl: int = 3600):
        """
        Probabilistic early expiration to prevent stampede
        """
        
        # Get from cache
        cached = self.cache.get(key)
        
        if cached:
            # Check if we should recompute early
            # to prevent stampede
            metadata = self.cache.get(f"{key}:meta")
            
            if metadata:
                expiry_time = float(metadata.get('expiry', 0))
                current_time = time.time()
                time_to_expiry = expiry_time - current_time
                
                # Probabilistic early recomputation
                # P = exp(-time_to_expiry / beta)
                beta = 1.0  # Tuning parameter
                prob = random.random()
                
                if prob < (beta / time_to_expiry):
                    # Recompute in background
                    self._async_recompute(key, compute_fn, ttl)
            
            return cached
        
        # Cache miss - use distributed lock
        lock_key = f"lock:{key}"
        lock_acquired = self.cache.set(lock_key, "1", ttl=10)
        
        if lock_acquired:
            try:
                # Compute value
                value = compute_fn()
                
                # Set cache with metadata
                self.cache.set(key, value, ttl)
                self.cache.set(f"{key}:meta", {
                    'expiry': time.time() + ttl
                }, ttl)
                
                return value
            finally:
                # Release lock
                self.cache.delete(lock_key)
        else:
            # Another process is computing
            # Wait briefly and retry
            time.sleep(0.1)
            return self.get_with_lock(key, compute_fn, ttl)
```

---

## 🎓 Interview Points

**Capacity:**
```
QPS: 1M/sec
Storage: 1 TB
Nodes: 10 × 100 GB = 1 TB
Latency: <1ms (in-memory)
```

**Key topics:** Consistent hashing, replication, eviction policies, stampede prevention!
