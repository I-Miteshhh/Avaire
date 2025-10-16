# Caching Strategies - From Cache-Aside to Global CDN

**Mastery Level:** Essential for 40+ LPA roles  
**Interview Weight:** 25-35% of system design interviews  
**Time to Master:** 2-3 weeks  
**Difficulty:** ⭐⭐⭐⭐

---

## 🎯 Why Caching Mastery Matters

At **Staff/Principal level**, caching decisions can:
- **Reduce latency** from 500ms to 5ms (100x improvement)
- **Save millions** in database infrastructure costs
- **Enable scale** from 1K to 1M concurrent users  
- **Improve availability** by reducing database load
- **Geographic performance** via global edge caches

**Poor caching = expensive infrastructure. Great caching = lean, fast systems.**

---

## 🏗️ The Caching Hierarchy

### **L1: Application-Level Caching**
```
[Application Memory] → Response in 0.1ms
├─ In-process cache (Caffeine, Guava)
├─ Thread-local storage  
└─ JVM heap caching
```

### **L2: Distributed Caching**
```
[Redis/Memcached Cluster] → Response in 1-5ms
├─ Session storage
├─ API response caching
└─ Database query caching
```

### **L3: Edge Caching**
```
[CDN Edge Locations] → Response in 10-50ms
├─ Static assets (images, CSS, JS)
├─ API responses with TTL
└─ Dynamic content personalization
```

### **L4: Client-Side Caching**
```
[Browser/Mobile Cache] → Response in 0ms
├─ Browser cache (HTTP headers)
├─ Service worker cache
└─ Mobile app local storage
```

---

## 🔧 Core Caching Patterns

### **1. Cache-Aside (Lazy Loading)**

**When to use:** Most common pattern, good for read-heavy workloads

```python
import redis
import json
from typing import Optional, Any

class CacheAsidePattern:
    def __init__(self, redis_client, database):
        self.cache = redis_client
        self.db = database
        self.default_ttl = 3600  # 1 hour
    
    def get(self, key: str) -> Optional[Any]:
        """Get data with cache-aside pattern"""
        
        # Step 1: Try cache first
        cached_data = self.cache.get(key)
        if cached_data:
            return json.loads(cached_data)
        
        # Step 2: Cache miss - get from database
        data = self.db.get(key)
        if data is None:
            return None
        
        # Step 3: Store in cache for future requests
        self.cache.setex(key, self.default_ttl, json.dumps(data))
        
        return data
    
    def set(self, key: str, value: Any) -> bool:
        """Update data in database and cache"""
        
        # Step 1: Write to database first (source of truth)
        success = self.db.set(key, value)
        if not success:
            return False
        
        # Step 2: Update cache
        self.cache.setex(key, self.default_ttl, json.dumps(value))
        
        return True
    
    def delete(self, key: str) -> bool:
        """Delete from both database and cache"""
        
        # Step 1: Delete from database
        db_success = self.db.delete(key)
        
        # Step 2: Remove from cache (even if DB delete failed)
        cache_success = self.cache.delete(key)
        
        return db_success

# Example usage
cache_aside = CacheAsidePattern(redis.Redis(), database)

# Read path: Cache → DB → Cache
user = cache_aside.get("user:12345")

# Write path: DB → Cache
cache_aside.set("user:12345", {"name": "John", "email": "john@example.com"})
```

**Pros:**
- Cache is only populated on demand
- Resilient to cache failures
- Cache and database can have different data models

**Cons:**
- Cache miss penalty (extra database call)
- Potential for stale data
- Complex invalidation logic

---

### **2. Write-Through Cache**

**When to use:** When you need strong consistency between cache and database

```python
class WriteThroughCache:
    def __init__(self, cache, database):
        self.cache = cache
        self.db = database
        self.default_ttl = 3600
    
    def set(self, key: str, value: Any) -> bool:
        """Write to both cache and database synchronously"""
        
        try:
            # Step 1: Write to database first
            db_success = self.db.set(key, value)
            if not db_success:
                return False
            
            # Step 2: Write to cache
            cache_success = self.cache.setex(key, self.default_ttl, json.dumps(value))
            
            return db_success and cache_success
            
        except Exception as e:
            # If either fails, rollback database write
            self.db.delete(key)
            self.cache.delete(key)
            raise e
    
    def get(self, key: str) -> Optional[Any]:
        """Read from cache (guaranteed to be consistent)"""
        
        cached_data = self.cache.get(key)
        if cached_data:
            return json.loads(cached_data)
        
        # If not in cache, it doesn't exist
        return None

# Example: User profile that must be consistent
write_through = WriteThroughCache(redis_client, database)

# All writes go through both systems
write_through.set("profile:12345", user_profile)

# Reads are always from cache (fast and consistent)
profile = write_through.get("profile:12345")
```

**Pros:**
- Strong consistency between cache and database
- Fast reads (always from cache)
- Simple read logic

**Cons:**
- Higher write latency
- Wasted cache space (may cache unused data)
- More complex error handling

---

### **3. Write-Behind Cache (Write-Back)**

**When to use:** High write throughput, can tolerate some data loss risk

```python
import asyncio
import time
from collections import deque
from threading import Thread, Lock

class WriteBehindCache:
    def __init__(self, cache, database, batch_size=100, flush_interval=5):
        self.cache = cache
        self.db = database
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        
        # Write queue for batching
        self.write_queue = deque()
        self.queue_lock = Lock()
        
        # Start background writer
        self.writer_thread = Thread(target=self._background_writer, daemon=True)
        self.writer_thread.start()
    
    def set(self, key: str, value: Any) -> bool:
        """Write to cache immediately, queue for database"""
        
        # Step 1: Write to cache immediately (fast response)
        cache_success = self.cache.setex(key, self.default_ttl, json.dumps(value))
        
        # Step 2: Queue for background database write
        with self.queue_lock:
            self.write_queue.append({
                'key': key,
                'value': value,
                'timestamp': time.time()
            })
        
        # Step 3: Trigger immediate flush if queue is full
        if len(self.write_queue) >= self.batch_size:
            self._flush_to_database()
        
        return cache_success
    
    def get(self, key: str) -> Optional[Any]:
        """Read from cache (may be more recent than database)"""
        
        cached_data = self.cache.get(key)
        if cached_data:
            return json.loads(cached_data)
        
        # Cache miss - get from database
        data = self.db.get(key)
        if data:
            self.cache.setex(key, self.default_ttl, json.dumps(data))
        
        return data
    
    def _background_writer(self):
        """Background thread to flush writes to database"""
        
        while True:
            time.sleep(self.flush_interval)
            self._flush_to_database()
    
    def _flush_to_database(self):
        """Batch write queued items to database"""
        
        if not self.write_queue:
            return
        
        batch = []
        with self.queue_lock:
            # Get batch of items to write
            while self.write_queue and len(batch) < self.batch_size:
                batch.append(self.write_queue.popleft())
        
        if not batch:
            return
        
        try:
            # Batch write to database
            self.db.batch_write(batch)
        except Exception as e:
            # On failure, put items back in queue for retry
            with self.queue_lock:
                self.write_queue.extendleft(reversed(batch))
            print(f"Batch write failed: {e}")

# Example: Gaming leaderboard with high write frequency
write_behind = WriteBehindCache(redis_client, database)

# Writes are fast (only cache update)
for player_id in range(1000):
    write_behind.set(f"score:{player_id}", random.randint(0, 1000))

# Database is updated in background batches
```

**Pros:**
- Excellent write performance
- Batch writes reduce database load
- Can handle write spikes

**Cons:**
- Risk of data loss on cache failure
- Complex error handling and recovery
- Eventual consistency between cache and database

---

### **4. Refresh-Ahead Cache**

**When to use:** Predictable access patterns, cannot tolerate cache misses

```python
import asyncio
import time
from typing import Callable

class RefreshAheadCache:
    def __init__(self, cache, data_loader: Callable, refresh_threshold=0.8):
        self.cache = cache
        self.data_loader = data_loader
        self.refresh_threshold = refresh_threshold  # Refresh when 80% of TTL passed
        self.refresh_tasks = {}  # Track ongoing refresh tasks
    
    async def get(self, key: str, ttl: int = 3600) -> Optional[Any]:
        """Get data and refresh proactively if needed"""
        
        # Get data and metadata from cache
        cache_data = self.cache.get(key)
        if cache_data:
            data = json.loads(cache_data)
            
            # Check if we should refresh proactively
            cache_time = data.get('_cached_at', 0)
            age = time.time() - cache_time
            
            if age > (ttl * self.refresh_threshold):
                # Trigger async refresh without blocking
                if key not in self.refresh_tasks:
                    self.refresh_tasks[key] = asyncio.create_task(
                        self._refresh_data(key, ttl)
                    )
            
            return data.get('value')
        
        # Cache miss - load synchronously
        fresh_data = await self.data_loader(key)
        if fresh_data:
            await self._store_with_metadata(key, fresh_data, ttl)
        
        return fresh_data
    
    async def _refresh_data(self, key: str, ttl: int):
        """Background refresh of cached data"""
        
        try:
            fresh_data = await self.data_loader(key)
            if fresh_data:
                await self._store_with_metadata(key, fresh_data, ttl)
        
        except Exception as e:
            print(f"Failed to refresh {key}: {e}")
        
        finally:
            # Remove from tracking
            self.refresh_tasks.pop(key, None)
    
    async def _store_with_metadata(self, key: str, value: Any, ttl: int):
        """Store data with caching metadata"""
        
        cache_entry = {
            'value': value,
            '_cached_at': time.time(),
            '_ttl': ttl
        }
        
        self.cache.setex(key, ttl, json.dumps(cache_entry))

# Example: Product recommendations that must always be fast
async def load_recommendations(user_id):
    # Expensive ML inference
    await asyncio.sleep(0.5)  # Simulate ML model call
    return {"recommendations": [1, 2, 3, 4, 5]}

refresh_ahead = RefreshAheadCache(redis_client, load_recommendations)

# First call loads data
recommendations = await refresh_ahead.get("user:12345:recs", ttl=3600)

# Subsequent calls get cached data, refresh happens in background
recommendations = await refresh_ahead.get("user:12345:recs", ttl=3600)  # Fast!
```

**Pros:**
- Eliminates cache miss penalty for hot data
- Keeps cache warm automatically
- Predictable response times

**Cons:**
- More complex implementation
- Wastes resources refreshing unused data
- Requires good TTL estimation

---

## 🌐 Distributed Caching Architectures

### **Redis Cluster Architecture**

```python
import redis
from rediscluster import RedisCluster

class RedisClusterManager:
    def __init__(self, startup_nodes):
        self.redis_cluster = RedisCluster(
            startup_nodes=startup_nodes,
            decode_responses=True,
            health_check_interval=30
        )
        
    def get_cluster_info(self):
        """Get cluster topology and health"""
        
        info = {
            'nodes': [],
            'slots_distribution': {},
            'replication_info': {}
        }
        
        for node in self.redis_cluster.get_nodes():
            node_info = {
                'id': node.name,
                'host': node.host,
                'port': node.port,
                'role': 'master' if node.server_type == 'master' else 'slave',
                'slots': node.slots if hasattr(node, 'slots') else [],
                'memory_usage': self.redis_cluster.memory_usage(node=node)
            }
            info['nodes'].append(node_info)
        
        return info
    
    def hash_slot_for_key(self, key: str) -> int:
        """Calculate hash slot for a key (Redis uses CRC16)"""
        import crc16
        if '{' in key:
            # Hash tag support: use content between {}
            start = key.find('{')
            end = key.find('}', start)
            if end > start + 1:
                key = key[start+1:end]
        
        return crc16.crc16xmodem(key.encode()) % 16384
    
    def multi_key_operation(self, keys):
        """Handle operations across multiple hash slots"""
        
        # Group keys by hash slot
        slots_to_keys = {}
        for key in keys:
            slot = self.hash_slot_for_key(key)
            if slot not in slots_to_keys:
                slots_to_keys[slot] = []
            slots_to_keys[slot].append(key)
        
        # Execute operations per slot
        results = {}
        for slot, slot_keys in slots_to_keys.items():
            # Use pipeline for keys in same slot
            pipe = self.redis_cluster.pipeline()
            for key in slot_keys:
                pipe.get(key)
            
            slot_results = pipe.execute()
            for key, result in zip(slot_keys, slot_results):
                results[key] = result
        
        return results

# Configuration for 6-node Redis cluster
startup_nodes = [
    {"host": "redis-node-1", "port": "7000"},
    {"host": "redis-node-2", "port": "7001"}, 
    {"host": "redis-node-3", "port": "7002"},
    {"host": "redis-node-4", "port": "7003"},
    {"host": "redis-node-5", "port": "7004"},
    {"host": "redis-node-6", "port": "7005"}
]

cluster_manager = RedisClusterManager(startup_nodes)
```

### **Consistent Hashing for Cache Distribution**

```python
import hashlib
import bisect
from typing import List, Dict, Any

class ConsistentHashRing:
    def __init__(self, nodes: List[str], virtual_nodes: int = 150):
        self.virtual_nodes = virtual_nodes
        self.ring: Dict[int, str] = {}
        self.sorted_keys: List[int] = []
        
        for node in nodes:
            self.add_node(node)
    
    def _hash(self, key: str) -> int:
        """Hash function for consistent hashing"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def add_node(self, node: str):
        """Add a node to the hash ring"""
        
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:{i}" 
            hash_value = self._hash(virtual_key)
            
            self.ring[hash_value] = node
            bisect.insort(self.sorted_keys, hash_value)
    
    def remove_node(self, node: str):
        """Remove a node from the hash ring"""
        
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:{i}"
            hash_value = self._hash(virtual_key)
            
            if hash_value in self.ring:
                del self.ring[hash_value]
                self.sorted_keys.remove(hash_value)
    
    def get_node(self, key: str) -> str:
        """Get the node responsible for a given key"""
        
        if not self.ring:
            return None
        
        hash_value = self._hash(key)
        
        # Find the first node with hash >= key's hash
        idx = bisect.bisect_right(self.sorted_keys, hash_value)
        
        # Wrap around if necessary
        if idx == len(self.sorted_keys):
            idx = 0
        
        return self.ring[self.sorted_keys[idx]]
    
    def get_nodes_for_replication(self, key: str, replicas: int = 2) -> List[str]:
        """Get multiple nodes for replication"""
        
        if not self.ring:
            return []
        
        hash_value = self._hash(key)
        idx = bisect.bisect_right(self.sorted_keys, hash_value)
        
        nodes = []
        seen_physical_nodes = set()
        
        # Get unique physical nodes for replication
        while len(nodes) < replicas and len(seen_physical_nodes) < len(set(self.ring.values())):
            if idx >= len(self.sorted_keys):
                idx = 0
            
            node = self.ring[self.sorted_keys[idx]]
            if node not in seen_physical_nodes:
                nodes.append(node)
                seen_physical_nodes.add(node)
            
            idx += 1
        
        return nodes

# Example: Distributed cache with consistent hashing
class DistributedCache:
    def __init__(self, cache_nodes: List[str]):
        self.hash_ring = ConsistentHashRing(cache_nodes)
        self.node_connections = {}
        
        # Create Redis connections for each node
        for node in cache_nodes:
            host, port = node.split(':')
            self.node_connections[node] = redis.Redis(host=host, port=int(port))
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set key-value with replication"""
        
        # Get primary and replica nodes
        nodes = self.hash_ring.get_nodes_for_replication(key, replicas=2)
        
        success_count = 0
        for node in nodes:
            try:
                conn = self.node_connections[node]
                conn.setex(key, ttl, json.dumps(value))
                success_count += 1
            except Exception as e:
                print(f"Failed to write to {node}: {e}")
        
        # Require at least one successful write
        return success_count > 0
    
    def get(self, key: str) -> Any:
        """Get value with fallback to replicas"""
        
        nodes = self.hash_ring.get_nodes_for_replication(key, replicas=2)
        
        for node in nodes:
            try:
                conn = self.node_connections[node]
                data = conn.get(key)
                if data:
                    return json.loads(data)
            except Exception as e:
                print(f"Failed to read from {node}: {e}")
                continue
        
        return None  # Not found in any replica

# Usage
cache_nodes = ["redis1:6379", "redis2:6379", "redis3:6379", "redis4:6379"]
distributed_cache = DistributedCache(cache_nodes)

# Automatically routes to correct nodes based on key
distributed_cache.set("user:12345", {"name": "John"})
user_data = distributed_cache.get("user:12345")
```

---

## 🌍 CDN and Edge Caching

### **CDN Configuration Strategies**

```python
class CDNConfiguration:
    def __init__(self):
        self.cache_policies = {
            'static_assets': {
                'ttl': 31536000,  # 1 year
                'cache_control': 'public, max-age=31536000, immutable',
                'file_types': ['.js', '.css', '.png', '.jpg', '.woff2']
            },
            'api_responses': {
                'ttl': 300,  # 5 minutes
                'cache_control': 'public, max-age=300',
                'endpoints': ['/api/catalog', '/api/popular']
            },
            'personalized_content': {
                'ttl': 60,  # 1 minute
                'cache_control': 'private, max-age=60',
                'vary_headers': ['Authorization', 'User-Agent']
            },
            'no_cache': {
                'ttl': 0,
                'cache_control': 'no-store, no-cache, must-revalidate',
                'endpoints': ['/api/user', '/api/cart', '/api/checkout']
            }
        }
    
    def generate_nginx_config(self):
        """Generate nginx configuration for CDN edge"""
        
        config = """
        # Static assets - long cache
        location ~* \.(js|css|png|jpg|jpeg|gif|webp|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, max-age=31536000, immutable";
            add_header X-Cache-Status $upstream_cache_status;
            
            # Enable compression
            gzip on;
            gzip_vary on;
            gzip_types text/css application/javascript image/svg+xml;
        }
        
        # API responses - moderate cache
        location ~* ^/api/(catalog|popular|trending) {
            expires 5m;
            add_header Cache-Control "public, max-age=300";
            add_header Vary "Accept-Encoding";
            
            # Cache based on query parameters
            proxy_cache_key $scheme$request_method$host$request_uri;
            proxy_cache_valid 200 302 5m;
            proxy_cache_valid 404 1m;
        }
        
        # Personalized content - short cache
        location ~* ^/api/(feed|recommendations) {
            expires 1m;
            add_header Cache-Control "private, max-age=60";
            add_header Vary "Authorization, User-Agent";
            
            # Cache per user
            proxy_cache_key $scheme$request_method$host$request_uri$http_authorization;
        }
        
        # Never cache - user-specific
        location ~* ^/api/(user|cart|checkout|payment) {
            expires -1;
            add_header Cache-Control "no-store, no-cache, must-revalidate";
            add_header Pragma "no-cache";
        }
        """
        
        return config
    
    def cloudflare_workers_example(self):
        """Cloudflare Workers script for advanced caching logic"""
        
        worker_script = """
        addEventListener('fetch', event => {
            event.respondWith(handleRequest(event.request))
        })
        
        async function handleRequest(request) {
            const url = new URL(request.url)
            const cacheKey = new Request(url.toString(), request)
            const cache = caches.default
            
            // Try cache first
            let response = await cache.match(cacheKey)
            if (response) {
                // Add cache hit header
                response = new Response(response.body, response)
                response.headers.set('X-Cache', 'HIT')
                return response
            }
            
            // Cache miss - fetch from origin
            response = await fetch(request)
            
            // Clone response for caching
            const responseToCache = response.clone()
            
            // Determine cache TTL based on path
            let cacheTTL = 0
            if (url.pathname.startsWith('/api/catalog')) {
                cacheTTL = 300  // 5 minutes
            } else if (url.pathname.match(/\.(js|css|png|jpg)$/)) {
                cacheTTL = 86400  // 1 day
            }
            
            if (cacheTTL > 0) {
                // Set cache headers
                responseToCache.headers.set('Cache-Control', `public, max-age=${cacheTTL}`)
                
                // Store in cache
                event.waitUntil(cache.put(cacheKey, responseToCache))
            }
            
            // Add cache miss header
            response.headers.set('X-Cache', 'MISS')
            return response
        }
        """
        
        return worker_script

# Example: Multi-tier caching architecture
class MultiTierCache:
    def __init__(self):
        self.l1_cache = {}  # In-memory (application level)
        self.l2_cache = redis.Redis()  # Redis (distributed)
        self.l3_cache = "https://cdn.example.com"  # CDN
    
    async def get(self, key: str) -> Any:
        """Multi-tier cache lookup"""
        
        # L1: Check application memory first
        if key in self.l1_cache:
            return self.l1_cache[key]
        
        # L2: Check Redis
        redis_data = self.l2_cache.get(key)
        if redis_data:
            data = json.loads(redis_data)
            # Populate L1 cache
            self.l1_cache[key] = data
            return data
        
        # L3: Check CDN (for static content)
        if self.is_static_content(key):
            cdn_response = await self.fetch_from_cdn(key)
            if cdn_response:
                # Populate L2 and L1
                self.l2_cache.setex(key, 3600, json.dumps(cdn_response))
                self.l1_cache[key] = cdn_response
                return cdn_response
        
        # Cache miss - fetch from origin
        return None
    
    def is_static_content(self, key: str) -> bool:
        static_patterns = ['.js', '.css', '.png', '.jpg', '/images/', '/assets/']
        return any(pattern in key for pattern in static_patterns)
    
    async def fetch_from_cdn(self, key: str):
        # Simulate CDN fetch
        import aiohttp
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.l3_cache}/{key}") as response:
                    if response.status == 200:
                        return await response.json()
            except:
                pass
        return None
```

---

## 🎯 Advanced Caching Patterns

### **Cache Warming Strategies**

```python
import asyncio
from typing import List
from concurrent.futures import ThreadPoolExecutor

class CacheWarmer:
    def __init__(self, cache, data_loader, batch_size=100):
        self.cache = cache
        self.data_loader = data_loader
        self.batch_size = batch_size
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    async def warm_cache_predictive(self, user_id: str):
        """Predictively warm cache based on user behavior"""
        
        # Get user's historical access patterns
        access_patterns = await self.get_user_access_patterns(user_id)
        
        # Predict what user will likely access next
        likely_keys = self.predict_next_access(access_patterns)
        
        # Warm cache in background
        warming_tasks = []
        for key in likely_keys[:20]:  # Limit to top 20 predictions
            task = asyncio.create_task(self.warm_single_key(key))
            warming_tasks.append(task)
        
        # Execute warming tasks concurrently
        await asyncio.gather(*warming_tasks, return_exceptions=True)
    
    async def warm_cache_batch(self, keys: List[str]):
        """Efficiently warm cache for multiple keys"""
        
        # Check which keys are already cached
        uncached_keys = []
        pipe = self.cache.pipeline()
        
        for key in keys:
            pipe.exists(key)
        
        results = pipe.execute()
        
        for key, exists in zip(keys, results):
            if not exists:
                uncached_keys.append(key)
        
        if not uncached_keys:
            return  # All keys already cached
        
        # Load data in batches
        for i in range(0, len(uncached_keys), self.batch_size):
            batch = uncached_keys[i:i + self.batch_size]
            await self.warm_batch(batch)
    
    async def warm_batch(self, keys: List[str]):
        """Warm a batch of keys concurrently"""
        
        # Load data concurrently
        load_tasks = []
        for key in keys:
            task = asyncio.create_task(self.data_loader(key))
            load_tasks.append(task)
        
        results = await asyncio.gather(*load_tasks, return_exceptions=True)
        
        # Store successful results in cache
        pipe = self.cache.pipeline()
        for key, result in zip(keys, results):
            if not isinstance(result, Exception) and result is not None:
                pipe.setex(key, 3600, json.dumps(result))
        
        pipe.execute()
    
    async def warm_single_key(self, key: str):
        """Warm a single key if not already cached"""
        
        if self.cache.exists(key):
            return  # Already cached
        
        try:
            data = await self.data_loader(key)
            if data:
                self.cache.setex(key, 3600, json.dumps(data))
        except Exception as e:
            print(f"Failed to warm {key}: {e}")
    
    def predict_next_access(self, access_patterns):
        """Simple prediction based on historical patterns"""
        
        # This could be a sophisticated ML model
        # For now, simple heuristics:
        predictions = []
        
        for pattern in access_patterns:
            # Predict based on time of day
            if pattern['hour'] == time.localtime().tm_hour:
                predictions.extend(pattern['keys'])
            
            # Predict based on access frequency
            if pattern['frequency'] > 0.1:  # Accessed > 10% of the time
                predictions.extend(pattern['keys'])
        
        return list(set(predictions))  # Remove duplicates
    
    async def get_user_access_patterns(self, user_id: str):
        """Analyze user's historical access patterns"""
        
        # This would typically query analytics database
        # Simplified example:
        return [
            {
                'hour': 9,  # 9 AM
                'keys': [f'user:{user_id}:feed', f'user:{user_id}:notifications'],
                'frequency': 0.8
            },
            {
                'hour': 13,  # 1 PM  
                'keys': [f'user:{user_id}:messages', f'user:{user_id}:calendar'],
                'frequency': 0.6
            }
        ]

# Usage: Warm cache for active users
warmer = CacheWarmer(redis_client, data_loader)

# Predictive warming for logged-in user
await warmer.warm_cache_predictive("user:12345")

# Batch warming for trending content
trending_keys = ["trending:today", "trending:week", "trending:month"]
await warmer.warm_cache_batch(trending_keys)
```

### **Cache Invalidation Patterns**

```python
import time
from typing import Set, List
from enum import Enum

class InvalidationType(Enum):
    IMMEDIATE = "immediate"
    LAZY = "lazy"
    SCHEDULED = "scheduled"
    EVENT_DRIVEN = "event_driven"

class SmartCacheInvalidator:
    def __init__(self, cache, message_queue=None):
        self.cache = cache
        self.message_queue = message_queue
        self.dependency_graph = {}  # Track cache dependencies
        self.invalidation_log = []
    
    def register_dependency(self, parent_key: str, child_keys: List[str]):
        """Register cache key dependencies"""
        
        if parent_key not in self.dependency_graph:
            self.dependency_graph[parent_key] = set()
        
        self.dependency_graph[parent_key].update(child_keys)
    
    def invalidate_key(self, key: str, invalidation_type: InvalidationType = InvalidationType.IMMEDIATE):
        """Invalidate a cache key with different strategies"""
        
        if invalidation_type == InvalidationType.IMMEDIATE:
            self._immediate_invalidation(key)
        
        elif invalidation_type == InvalidationType.LAZY:
            self._lazy_invalidation(key)
        
        elif invalidation_type == InvalidationType.SCHEDULED:
            self._scheduled_invalidation(key)
        
        elif invalidation_type == InvalidationType.EVENT_DRIVEN:
            self._event_driven_invalidation(key)
    
    def _immediate_invalidation(self, key: str):
        """Immediately remove from cache and cascade"""
        
        # Remove the key
        deleted_count = self.cache.delete(key)
        
        # Cascade to dependent keys
        dependent_keys = self.dependency_graph.get(key, set())
        for dependent_key in dependent_keys:
            self.cache.delete(dependent_key)
        
        # Log invalidation
        self.invalidation_log.append({
            'key': key,
            'type': 'immediate',
            'timestamp': time.time(), 
            'dependent_keys': list(dependent_keys),
            'deleted_count': deleted_count
        })
    
    def _lazy_invalidation(self, key: str):
        """Mark for lazy invalidation (check on access)"""
        
        # Set a flag that this key needs refresh
        self.cache.set(f"{key}:invalidated", "1", ex=86400)  # 24 hour flag
        
        # Also set short TTL on original key
        current_data = self.cache.get(key)
        if current_data:
            self.cache.setex(key, 60, current_data)  # 1 minute grace period
    
    def _scheduled_invalidation(self, key: str, delay_seconds: int = 300):
        """Schedule invalidation for later"""
        
        if self.message_queue:
            # Send delayed message
            invalidation_message = {
                'action': 'invalidate',
                'key': key,
                'scheduled_time': time.time() + delay_seconds
            }
            self.message_queue.send_delayed(invalidation_message, delay_seconds)
    
    def _event_driven_invalidation(self, key: str):
        """Publish invalidation event for other services"""
        
        if self.message_queue:
            event = {
                'event_type': 'cache_invalidated',
                'key': key,
                'timestamp': time.time(),
                'service': 'cache-service'
            }
            self.message_queue.publish('cache.invalidation', event)
    
    def invalidate_by_pattern(self, pattern: str):
        """Invalidate multiple keys matching a pattern"""
        
        # Redis-specific pattern matching
        keys_to_delete = self.cache.keys(pattern)
        
        if keys_to_delete:
            deleted_count = self.cache.delete(*keys_to_delete)
            
            self.invalidation_log.append({
                'pattern': pattern,
                'type': 'pattern',
                'timestamp': time.time(),
                'keys_deleted': len(keys_to_delete),
                'deleted_count': deleted_count
            })
    
    def smart_invalidate_user_data(self, user_id: str):
        """Intelligent invalidation for user-related data"""
        
        # Define what needs to be invalidated when user data changes
        patterns_to_invalidate = [
            f"user:{user_id}:*",           # All user data
            f"feed:{user_id}:*",           # User's feed
            f"recommendations:{user_id}:*", # User recommendations
            f"friends:{user_id}:*"         # User's social graph
        ]
        
        # Also invalidate caches that include this user
        aggregate_patterns = [
            f"leaderboard:*",              # User might be in leaderboards
            f"trending:*"                  # If user content was trending
        ]
        
        # Immediate invalidation for personal data
        for pattern in patterns_to_invalidate:
            self.invalidate_by_pattern(pattern)
        
        # Lazy invalidation for aggregate data (expensive to recompute)
        for pattern in aggregate_patterns:
            keys = self.cache.keys(pattern)
            for key in keys:
                self._lazy_invalidation(key)

# Example: Tag-based invalidation
class TaggedCache:
    def __init__(self, cache):
        self.cache = cache
        self.tag_to_keys = {}  # Track which keys have which tags
        self.key_to_tags = {}  # Track which tags belong to each key
    
    def set_with_tags(self, key: str, value: Any, tags: List[str], ttl: int = 3600):
        """Set cache value with associated tags"""
        
        # Store the actual data
        self.cache.setex(key, ttl, json.dumps(value))
        
        # Update tag mappings
        self.key_to_tags[key] = set(tags)
        
        for tag in tags:
            if tag not in self.tag_to_keys:
                self.tag_to_keys[tag] = set()
            self.tag_to_keys[tag].add(key)
    
    def invalidate_by_tag(self, tag: str):
        """Invalidate all keys associated with a tag"""
        
        keys_to_invalidate = self.tag_to_keys.get(tag, set())
        
        for key in keys_to_invalidate:
            # Remove from cache
            self.cache.delete(key)
            
            # Update tag mappings
            if key in self.key_to_tags:
                key_tags = self.key_to_tags[key]
                for key_tag in key_tags:
                    if key_tag in self.tag_to_keys:
                        self.tag_to_keys[key_tag].discard(key)
                
                del self.key_to_tags[key]
        
        # Clean up empty tag
        self.tag_to_keys.pop(tag, None)
        
        return len(keys_to_invalidate)

# Usage example
tagged_cache = TaggedCache(redis_client)

# Cache user profile with tags
tagged_cache.set_with_tags(
    "user:12345:profile", 
    {"name": "John", "email": "john@example.com"},
    tags=["user:12345", "profile", "personal_data"]
)

# Cache user's posts with tags
tagged_cache.set_with_tags(
    "user:12345:posts",
    [{"id": 1, "content": "Hello World"}],
    tags=["user:12345", "posts", "social_content"]
)

# When user updates profile, invalidate all their personal data
tagged_cache.invalidate_by_tag("user:12345")
```

---

## 📊 Cache Performance Optimization

### **Cache Hit Rate Optimization**

```python
import statistics
from collections import defaultdict, deque
import time

class CacheAnalytics:
    def __init__(self, cache, window_size=1000):
        self.cache = cache
        self.window_size = window_size
        
        # Sliding window for hit/miss tracking
        self.access_history = deque(maxlen=window_size)
        self.key_access_frequency = defaultdict(int)
        self.key_last_access = {}
        
        # Performance metrics
        self.metrics = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'hit_rate': 0.0,
            'avg_response_time': 0.0
        }
    
    def record_access(self, key: str, was_hit: bool, response_time_ms: float):
        """Record cache access for analytics"""
        
        access_record = {
            'key': key,
            'hit': was_hit,
            'timestamp': time.time(),
            'response_time': response_time_ms
        }
        
        self.access_history.append(access_record)
        self.key_access_frequency[key] += 1
        self.key_last_access[key] = time.time()
        
        # Update metrics
        self.metrics['total_requests'] += 1
        if was_hit:
            self.metrics['cache_hits'] += 1
        else:
            self.metrics['cache_misses'] += 1
        
        self.metrics['hit_rate'] = self.metrics['cache_hits'] / self.metrics['total_requests']
        
        # Update average response time
        response_times = [record['response_time'] for record in self.access_history]
        self.metrics['avg_response_time'] = statistics.mean(response_times)
    
    def get_hot_keys(self, top_n: int = 10) -> List[str]:
        """Get most frequently accessed keys"""
        
        sorted_keys = sorted(
            self.key_access_frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [key for key, freq in sorted_keys[:top_n]]
    
    def get_cold_keys(self, threshold_hours: float = 24) -> List[str]:
        """Get keys not accessed recently"""
        
        current_time = time.time()
        threshold_seconds = threshold_hours * 3600
        
        cold_keys = []
        for key, last_access in self.key_last_access.items():
            if (current_time - last_access) > threshold_seconds:
                cold_keys.append(key)
        
        return cold_keys
    
    def optimize_cache_size(self):
        """Suggest cache optimization based on access patterns"""
        
        hot_keys = self.get_hot_keys(50)  # Top 50 hot keys
        cold_keys = self.get_cold_keys(1)  # Keys not accessed in 1 hour
        
        recommendations = {
            'increase_ttl': hot_keys[:10],  # Keep hot keys longer
            'decrease_ttl': cold_keys[:20], # Expire cold keys sooner
            'preload_candidates': [],
            'eviction_candidates': cold_keys
        }
        
        # Identify preload candidates (consistent access patterns)
        for key in hot_keys:
            key_accesses = [
                record for record in self.access_history 
                if record['key'] == key
            ]
            
            if len(key_accesses) >= 5:
                # Check if access pattern is regular
                timestamps = [access['timestamp'] for access in key_accesses]
                intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
                
                if statistics.stdev(intervals) < statistics.mean(intervals) * 0.5:
                    # Regular access pattern - good preload candidate
                    recommendations['preload_candidates'].append(key)
        
        return recommendations

# Example: Adaptive cache with dynamic TTL
class AdaptiveCache:
    def __init__(self, cache):
        self.cache = cache
        self.analytics = CacheAnalytics(cache)
        self.base_ttl = 3600  # 1 hour base TTL
        self.ttl_adjustments = {}  # Per-key TTL adjustments
    
    def get(self, key: str) -> Any:
        """Get with performance tracking"""
        
        start_time = time.time()
        
        data = self.cache.get(key)
        
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        was_hit = data is not None
        
        self.analytics.record_access(key, was_hit, response_time)
        
        if data:
            return json.loads(data)
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set with adaptive TTL"""
        
        if ttl is None:
            ttl = self.calculate_adaptive_ttl(key)
        
        return self.cache.setex(key, ttl, json.dumps(value))
    
    def calculate_adaptive_ttl(self, key: str) -> int:
        """Calculate TTL based on access patterns"""
        
        base_ttl = self.base_ttl
        
        # Adjust based on access frequency
        frequency = self.analytics.key_access_frequency.get(key, 0)
        
        if frequency > 100:  # Very hot key
            return base_ttl * 3  # Keep 3x longer
        elif frequency > 50:  # Hot key
            return base_ttl * 2  # Keep 2x longer
        elif frequency < 5:   # Cold key
            return base_ttl // 2  # Expire sooner
        
        return base_ttl
    
    def auto_optimize(self):
        """Automatically apply optimization recommendations"""
        
        recommendations = self.analytics.optimize_cache_size()
        
        # Increase TTL for hot keys
        for key in recommendations['increase_ttl']:
            current_ttl = self.cache.ttl(key)
            if current_ttl > 0:
                new_ttl = min(current_ttl * 2, 86400)  # Max 24 hours
                current_data = self.cache.get(key)
                if current_data:
                    self.cache.setex(key, new_ttl, current_data)
        
        # Expire cold keys early
        for key in recommendations['eviction_candidates']:
            self.cache.expire(key, 60)  # Expire in 1 minute
        
        # Preload predicted keys (would implement actual preloading logic)
        print(f"Preload candidates: {recommendations['preload_candidates']}")

# Usage
adaptive_cache = AdaptiveCache(redis_client)

# Normal cache operations with automatic optimization
adaptive_cache.set("user:12345", user_data)
user = adaptive_cache.get("user:12345")

# Periodic optimization
adaptive_cache.auto_optimize()
```

---

## 🎯 Interview Scenarios & Solutions

### **Scenario 1: Social Media Feed Caching**

**Problem:** Design caching for a social media feed serving 100M users

**Solution:**

```python
class SocialMediaFeedCache:
    def __init__(self):
        self.redis_cluster = RedisCluster()
        self.cdn = CDNService()
        self.db = DatabaseService()
    
    def get_user_feed(self, user_id: str, page: int = 1) -> List[Dict]:
        """Multi-layer caching for social media feeds"""
        
        cache_key = f"feed:{user_id}:page:{page}"
        
        # L1: Try Redis cluster first
        cached_feed = self.redis_cluster.get(cache_key)
        if cached_feed:
            return json.loads(cached_feed)
        
        # L2: Generate feed from user's social graph
        feed_data = self.generate_feed(user_id, page)
        
        # Cache with different TTLs based on user activity
        user_activity = self.get_user_activity_level(user_id)
        
        if user_activity == 'high':
            ttl = 300  # 5 minutes for active users
        elif user_activity == 'medium':
            ttl = 900  # 15 minutes
        else:
            ttl = 3600  # 1 hour for inactive users
        
        # Store in cache
        self.redis_cluster.setex(cache_key, ttl, json.dumps(feed_data))
        
        return feed_data
    
    def invalidate_user_feeds(self, user_id: str):
        """Invalidate feeds when user posts new content"""
        
        # Get user's followers
        followers = self.get_user_followers(user_id)
        
        # Invalidate feeds for active followers only (optimization)
        active_followers = self.filter_active_users(followers)
        
        # Batch invalidation
        invalidation_keys = []
        for follower_id in active_followers:
            # Invalidate first few pages only
            for page in range(1, 4):
                invalidation_keys.append(f"feed:{follower_id}:page:{page}")
        
        # Use pipeline for efficient batch deletion
        pipe = self.redis_cluster.pipeline()
        for key in invalidation_keys:
            pipe.delete(key)
        pipe.execute()
```

### **Scenario 2: E-commerce Product Catalog**

**Problem:** Cache product catalog with real-time inventory updates

**Solution:**

```python
class EcommerceCatalogCache:
    def __init__(self):
        self.product_cache = RedisCluster()  # Product details
        self.inventory_cache = RedisCluster()  # Real-time inventory
        self.search_cache = ElasticsearchCache()  # Search results
        self.cdn = CDNService()  # Static assets
    
    def get_product(self, product_id: str) -> Dict:
        """Get product with multi-layer caching"""
        
        # Product details (rarely change) - long TTL
        product_key = f"product:{product_id}"
        product_data = self.product_cache.get(product_key)
        
        if not product_data:
            product_data = self.db.get_product(product_id)
            self.product_cache.setex(product_key, 86400, json.dumps(product_data))  # 24 hours
        else:
            product_data = json.loads(product_data)
        
        # Inventory (changes frequently) - short TTL
        inventory_key = f"inventory:{product_id}"
        inventory_data = self.inventory_cache.get(inventory_key)
        
        if not inventory_data:
            inventory_data = self.db.get_inventory(product_id)
            self.inventory_cache.setex(inventory_key, 30, json.dumps(inventory_data))  # 30 seconds
        else:
            inventory_data = json.loads(inventory_data)
        
        # Combine product details + real-time inventory
        return {**product_data, **inventory_data}
    
    def update_inventory(self, product_id: str, new_quantity: int):
        """Update inventory with cache invalidation"""
        
        # Update database
        self.db.update_inventory(product_id, new_quantity)
        
        # Immediate cache update
        inventory_key = f"inventory:{product_id}"
        inventory_data = {"quantity": new_quantity, "updated_at": time.time()}
        self.inventory_cache.setex(inventory_key, 30, json.dumps(inventory_data))
        
        # Invalidate search results that might show this product
        self.invalidate_search_cache(product_id)
    
    def get_search_results(self, query: str, filters: Dict) -> List[Dict]:
        """Cache search results with smart invalidation"""
        
        # Create cache key from query + filters
        cache_key = self.create_search_cache_key(query, filters)
        
        # Try cache first
        results = self.search_cache.get(cache_key)
        if results:
            return results
        
        # Execute search
        results = self.search_service.search(query, filters)
        
        # Cache with shorter TTL for personalized results
        ttl = 300 if 'user_id' in filters else 1800  # 5min vs 30min
        self.search_cache.set(cache_key, results, ttl)
        
        return results
```

---

## ✅ Caching Mastery Checklist

### **Core Patterns**
- [ ] Cache-aside pattern implementation and use cases
- [ ] Write-through vs write-behind trade-offs
- [ ] Refresh-ahead for predictable workloads
- [ ] Multi-level caching architecture

### **Distributed Caching**
- [ ] Redis Cluster setup and hash slot distribution
- [ ] Consistent hashing for cache distribution
- [ ] Replication strategies and failover handling
- [ ] Cross-region cache synchronization

### **Performance Optimization**
- [ ] Cache hit rate monitoring and optimization
- [ ] Adaptive TTL based on access patterns
- [ ] Memory usage optimization techniques
- [ ] Hotspot detection and mitigation

### **Invalidation Strategies**
- [ ] Tag-based invalidation for complex dependencies
- [ ] Event-driven invalidation patterns
- [ ] Bulk invalidation optimization
- [ ] Cache warming strategies

### **Production Considerations**
- [ ] Monitoring and alerting setup
- [ ] Cost optimization techniques
- [ ] Security considerations (encryption, access control)
- [ ] Disaster recovery and backup strategies

**Master these caching patterns, and you'll build systems that are lightning-fast and cost-efficient!** ⚡