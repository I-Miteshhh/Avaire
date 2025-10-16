# System Design Framework - Step-by-Step Approach

**Time:** 45-60 minutes (typical interview)  
**Goal:** Demonstrate structured thinking, not perfect solution

---

## 📐 The 7-Step Framework

### **Step 1: Requirements Clarification (5 minutes)**

#### **What to Ask:**

**Functional Requirements:**
```
❓ What are the core features?
❓ Who are the users? (B2C, B2B, internal?)
❓ What's the expected user journey?
❓ Read-heavy or write-heavy workload?
❓ Are there any specific features to prioritize?
```

**Non-Functional Requirements:**
```
❓ Scale: How many users? (DAU, MAU)
❓ Performance: Latency requirements? (p50, p95, p99)
❓ Availability: What's acceptable downtime? (99.9%? 99.99%?)
❓ Consistency: Strong consistency required or eventual OK?
❓ Durability: Can we lose data? Acceptable data loss?
❓ Geographic distribution: Global or regional?
❓ Cost constraints: Budget limitations?
```

#### **Example: Design URL Shortener**

**Interviewer:** "Design a URL shortener like bit.ly"

**You:** 
```
Clarifying questions:

Functional:
- Create short URL from long URL? ✓
- Redirect when accessing short URL? ✓
- Custom short URLs or auto-generated? → Auto-generated
- Analytics (click tracking)? → Out of scope for now
- URL expiration? → Optional feature

Non-Functional:
- Scale: How many URLs per day? → 100M new URLs/day
- Read/Write ratio? → 100:1 (read-heavy)
- Latency for redirect? → < 100ms p99
- Availability: → 99.99% uptime required
- URL lifetime? → Permanent unless user deletes
- Geographic: → Global service

Constraints:
- Short URL length? → 7 characters max
```

---

### **Step 2: Capacity Estimation (5 minutes)**

#### **Back-of-Envelope Calculations**

**Traffic Estimation:**
```python
# Daily Active Users (DAU)
DAU = 100_000_000

# Requests per user per day
requests_per_user = 10

# Total requests per day
daily_requests = DAU * requests_per_user
# = 1,000,000,000 requests/day

# Queries Per Second (QPS)
QPS = daily_requests / 86400  # seconds in a day
# = 11,574 QPS

# Peak QPS (assume 2-3x average)
peak_QPS = QPS * 3
# = 34,722 QPS
```

**Storage Estimation:**
```python
# URLs created per day
urls_per_day = 100_000_000

# Average URL size
url_size = 500 bytes  # long URL + metadata

# Daily storage
daily_storage = urls_per_day * url_size
# = 50 GB/day

# 5-year storage
storage_5_years = daily_storage * 365 * 5
# = 91.25 TB (raw)

# With replication factor 3
total_storage = storage_5_years * 3
# = 273.75 TB
```

**Bandwidth Estimation:**
```python
# Write bandwidth
write_bandwidth = urls_per_day * url_size / 86400
# = 0.578 MB/s

# Read bandwidth (100:1 ratio)
read_bandwidth = write_bandwidth * 100
# = 57.8 MB/s
```

**Memory (Cache) Estimation:**
```python
# Follow 80-20 rule: cache 20% of daily requests
cache_requests = daily_requests * 0.2

# Average cached response size
response_size = 100 bytes  # short URL + metadata

# Cache memory needed
cache_memory = cache_requests * response_size
# = 20 GB

# Round up for safety
cache_memory_total = 30 GB
```

#### **Quick Reference Table**

| Metric | Formula | Example (100M DAU) |
|--------|---------|-------------------|
| QPS | DAU × actions/day ÷ 86400 | 11,574 |
| Peak QPS | QPS × 3 | 34,722 |
| Storage/day | records/day × size | 50 GB |
| Bandwidth | QPS × avg_size | 58 MB/s |
| Cache size | daily_requests × 0.2 × size | 30 GB |

---

### **Step 3: API Design (5 minutes)**

#### **REST API Design**

```http
# Create short URL
POST /api/v1/urls
Content-Type: application/json

Request:
{
  "long_url": "https://example.com/very/long/url",
  "custom_alias": "my-link",  // optional
  "expiration_date": "2025-12-31"  // optional
}

Response:
{
  "short_url": "https://short.ly/abc1234",
  "long_url": "https://example.com/very/long/url",
  "created_at": "2025-10-15T10:30:00Z",
  "expires_at": "2025-12-31T23:59:59Z"
}

# Redirect (handled by HTTP 302)
GET /{shortCode}
→ HTTP 302 Redirect to long_url

# Get URL info (optional)
GET /api/v1/urls/{shortCode}
Response:
{
  "short_url": "https://short.ly/abc1234",
  "long_url": "https://example.com/very/long/url",
  "clicks": 15234,
  "created_at": "2025-10-15T10:30:00Z"
}

# Delete URL
DELETE /api/v1/urls/{shortCode}
Response: 204 No Content
```

#### **gRPC API Design (Alternative)**

```protobuf
service URLShortener {
  rpc CreateShortURL(CreateURLRequest) returns (URLResponse);
  rpc GetURL(GetURLRequest) returns (URLResponse);
  rpc DeleteURL(DeleteURLRequest) returns (Empty);
}

message CreateURLRequest {
  string long_url = 1;
  string custom_alias = 2;  // optional
  int64 expiration_timestamp = 3;  // optional
}

message URLResponse {
  string short_url = 1;
  string long_url = 2;
  int64 created_at = 3;
  int64 clicks = 4;
}
```

---

### **Step 4: Database Schema (5 minutes)**

#### **SQL Schema (PostgreSQL)**

```sql
-- URLs table
CREATE TABLE urls (
    id BIGSERIAL PRIMARY KEY,
    short_code VARCHAR(10) UNIQUE NOT NULL,
    long_url TEXT NOT NULL,
    user_id BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    clicks BIGINT DEFAULT 0,
    INDEX idx_short_code (short_code),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- Analytics table (optional)
CREATE TABLE url_clicks (
    id BIGSERIAL PRIMARY KEY,
    short_code VARCHAR(10) NOT NULL,
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_agent TEXT,
    ip_address INET,
    referrer TEXT,
    country_code CHAR(2),
    INDEX idx_short_code_time (short_code, clicked_at)
);

-- Partitioning for analytics (by month)
CREATE TABLE url_clicks_2025_10 PARTITION OF url_clicks
FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
```

#### **NoSQL Schema (DynamoDB)**

```javascript
// URLs table
{
  "TableName": "urls",
  "KeySchema": [
    { "AttributeName": "short_code", "KeyType": "HASH" }
  ],
  "AttributeDefinitions": [
    { "AttributeName": "short_code", "AttributeType": "S" },
    { "AttributeName": "user_id", "AttributeType": "S" },
    { "AttributeName": "created_at", "AttributeType": "N" }
  ],
  "GlobalSecondaryIndexes": [
    {
      "IndexName": "user-id-index",
      "KeySchema": [
        { "AttributeName": "user_id", "KeyType": "HASH" },
        { "AttributeName": "created_at", "KeyType": "RANGE" }
      ]
    }
  ]
}

// Sample record
{
  "short_code": "abc1234",
  "long_url": "https://example.com/very/long/url",
  "user_id": "user_123",
  "created_at": 1697368200,
  "expires_at": 1735689599,
  "clicks": 15234
}
```

#### **Cache Schema (Redis)**

```redis
# Key-value for quick redirect
SET url:abc1234 "https://example.com/very/long/url" EX 86400

# Hash for metadata
HSET url:abc1234:meta 
  long_url "https://example.com/very/long/url"
  created_at "1697368200"
  clicks "15234"

# Sorted set for trending URLs
ZADD trending_urls 15234 "abc1234"

# Set for user's URLs
SADD user:123:urls "abc1234" "def5678"
```

---

### **Step 5: High-Level Design (10 minutes)**

#### **System Architecture Diagram**

```
┌──────────────────────────────────────────────────────────────┐
│                         CLIENTS                               │
│  (Web, Mobile, API consumers)                                 │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │   DNS / CDN      │
              │  (CloudFlare)    │
              └────────┬─────────┘
                       │
                       ▼
            ┌─────────────────────┐
            │   Load Balancer     │
            │  (AWS ALB / nginx)  │
            └──────────┬──────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
  ┌─────────┐    ┌─────────┐    ┌─────────┐
  │  API    │    │  API    │    │  API    │
  │ Server 1│    │ Server 2│    │ Server 3│
  └────┬────┘    └────┬────┘    └────┬────┘
       │              │              │
       └──────────────┼──────────────┘
                      │
        ┌─────────────┼─────────────┬───────────────┐
        │             │             │               │
        ▼             ▼             ▼               ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐   ┌──────────┐
  │  Cache   │  │ Database │  │  Queue   │   │ Analytics│
  │ (Redis)  │  │(Postgres)│  │ (Kafka)  │   │(ClickHse)│
  │ Cluster  │  │ Primary  │  │          │   │          │
  └──────────┘  └────┬─────┘  └──────────┘   └──────────┘
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
     ┌─────────┬─────────┬─────────┐
     │Replica 1│Replica 2│Replica 3│
     └─────────┴─────────┴─────────┘
```

#### **Component Responsibilities**

**1. DNS/CDN**
- Resolves domain to closest server
- Caches static content
- DDoS protection

**2. Load Balancer**
- Distributes traffic across API servers
- Health checks
- SSL termination

**3. API Servers (Stateless)**
- Handle business logic
- Validate requests
- Generate short codes
- Return responses

**4. Cache (Redis Cluster)**
- Hot URL redirects (80-20 rule)
- TTL: 24 hours
- Eviction: LRU

**5. Database (PostgreSQL Primary-Replica)**
- Primary: Writes (create, update, delete)
- Replicas: Reads (get URL info, analytics)
- Replication lag: < 100ms

**6. Message Queue (Kafka)**
- Async processing (click events)
- Decouples analytics from main flow
- Exactly-once semantics

**7. Analytics DB (ClickHouse)**
- Time-series data
- Optimized for aggregations
- Columnar storage

---

### **Step 6: Detailed Design (15 minutes)**

#### **Deep-Dive Topic 1: Short Code Generation**

**Approach 1: Hash-based**
```python
import hashlib
import base62

def generate_short_code_hash(long_url: str) -> str:
    """
    Pros: Deterministic, no coordination needed
    Cons: Collisions possible, not truly random
    """
    # MD5 hash (fast)
    hash_obj = hashlib.md5(long_url.encode())
    hash_hex = hash_obj.hexdigest()
    
    # Take first 7 characters in base62
    hash_int = int(hash_hex[:10], 16)
    short_code = base62.encode(hash_int)[:7]
    
    return short_code

# Collision handling
def create_url_with_hash(long_url: str):
    short_code = generate_short_code_hash(long_url)
    
    # Check if exists
    while db.exists(short_code):
        # Append random suffix
        short_code = generate_short_code_hash(long_url + str(random.random()))
    
    db.insert(short_code, long_url)
    return short_code
```

**Approach 2: Counter-based (Better)**
```python
def generate_short_code_counter(counter: int) -> str:
    """
    Pros: No collisions, predictable growth
    Cons: Requires distributed counter (coordination)
    """
    base62_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    short_code = ""
    
    while counter > 0:
        short_code = base62_chars[counter % 62] + short_code
        counter //= 62
    
    return short_code.rjust(7, '0')

# Example:
# 0 → "0000000"
# 62 → "0000010"
# 3521614606207 → "zzzzzz" (62^7 - 1)
# Total: 3.5 trillion possible codes
```

**Approach 3: Range-based (Scalable)**
```python
"""
Pre-allocate ID ranges to each API server:
- Server 1: 1 - 1,000,000
- Server 2: 1,000,001 - 2,000,000
- Server 3: 2,000,001 - 3,000,000

Each server maintains local counter.
No coordination needed!
"""

class RangeBasedIDGenerator:
    def __init__(self, server_id: int, range_size: int = 1_000_000):
        self.start = server_id * range_size
        self.end = self.start + range_size
        self.current = self.start
    
    def get_next_id(self) -> int:
        if self.current >= self.end:
            raise Exception("Range exhausted, request new range")
        
        id = self.current
        self.current += 1
        return id
    
    def generate_short_code(self) -> str:
        id = self.get_next_id()
        return base62_encode(id)
```

**Chosen Approach:** Range-based with ZooKeeper coordination
- Each server requests range from ZooKeeper
- No collisions
- No single point of failure
- Can scale horizontally

#### **Deep-Dive Topic 2: Caching Strategy**

**Cache-Aside Pattern:**
```python
def get_long_url(short_code: str) -> str:
    # 1. Check cache first
    long_url = redis.get(f"url:{short_code}")
    
    if long_url:
        # Cache hit
        return long_url
    
    # 2. Cache miss - read from DB
    long_url = db.query("SELECT long_url FROM urls WHERE short_code = ?", short_code)
    
    if not long_url:
        raise NotFoundError("URL not found")
    
    # 3. Update cache (TTL: 24 hours)
    redis.setex(f"url:{short_code}", 86400, long_url)
    
    return long_url
```

**Cache Warming (Optional):**
```python
# Pre-populate cache with trending URLs
def warm_cache():
    trending_urls = db.query("""
        SELECT short_code, long_url 
        FROM urls 
        ORDER BY clicks DESC 
        LIMIT 10000
    """)
    
    for row in trending_urls:
        redis.setex(f"url:{row.short_code}", 86400, row.long_url)
```

**Cache Invalidation:**
```python
def delete_url(short_code: str):
    # 1. Delete from cache
    redis.delete(f"url:{short_code}")
    
    # 2. Delete from DB
    db.execute("DELETE FROM urls WHERE short_code = ?", short_code)
```

#### **Deep-Dive Topic 3: Database Sharding**

**Why Shard?**
- Single DB can't handle 11K writes/sec
- Data > 5TB (PostgreSQL limit for good performance)

**Sharding Strategy:**
```python
# Hash-based sharding by short_code
def get_shard(short_code: str, num_shards: int = 10) -> int:
    hash_value = hashlib.md5(short_code.encode()).hexdigest()
    return int(hash_value, 16) % num_shards

# Example:
short_code = "abc1234"
shard = get_shard(short_code, num_shards=10)  # → Shard 3

# Write
db_shard_3.insert(short_code, long_url)

# Read
shard = get_shard(short_code, num_shards=10)
long_url = db_shard[shard].query(short_code)
```

**Shard Configuration:**
```
Shard 0: urls_0000 (short_codes: hash % 10 == 0)
Shard 1: urls_0001 (short_codes: hash % 10 == 1)
...
Shard 9: urls_0009 (short_codes: hash % 10 == 9)

Each shard:
- 1 Primary + 2 Replicas
- 27 TB total / 10 shards = 2.7 TB per shard
- 11K QPS / 10 shards = 1.1K QPS per shard
```

---

### **Step 7: Trade-offs & Optimizations (10 minutes)**

#### **Consistency vs Availability**

**Eventual Consistency (Chosen):**
```
Pros:
✓ High availability (99.99%+)
✓ Better performance
✓ Survives network partitions

Cons:
✗ User might see stale data briefly
✗ Replication lag (< 100ms acceptable)

Acceptable because:
- URL redirects don't need strong consistency
- Slight delay in analytics is OK
```

**Strong Consistency (Alternative):**
```
Pros:
✓ Always consistent
✓ Easier to reason about

Cons:
✗ Lower availability
✗ Synchronous replication overhead
✗ Slower writes

Not chosen because:
- Overkill for URL shortener
- Availability more important
```

#### **Read Optimization**

**Current: 100:1 read-to-write ratio**

**Optimizations:**
1. **Read Replicas:**
   - 3 replicas for reads
   - Load balance read traffic
   - Result: 3x read capacity

2. **Redis Cluster:**
   - Cache hot 20% URLs
   - Result: 80% cache hit rate → 5x reduction in DB load

3. **CDN:**
   - Cache 302 redirects at edge
   - Result: 90% offloaded from origin

**Final Architecture:**
```
100M requests/day
├─ CDN (90%) = 90M requests (handled at edge)
└─ Origin (10%) = 10M requests
   ├─ Cache (80% hit) = 8M requests (Redis)
   └─ Database (20% miss) = 2M requests
      ├─ Replicas (read) = 1.99M
      └─ Primary (write) = 0.01M
```

#### **Write Optimization**

**Batch Writes:**
```python
# Instead of: 1 write per URL creation
# Use: Batch 100 URLs every 100ms

write_buffer = []

def create_url_async(long_url: str):
    short_code = generate_short_code()
    write_buffer.append((short_code, long_url))
    
    if len(write_buffer) >= 100:
        flush_buffer()
    
    return short_code

def flush_buffer():
    db.bulk_insert(write_buffer)
    write_buffer.clear()
```

#### **Cost vs Performance**

**Scenario 1: High Performance (Expensive)**
```
- 50 API servers
- 10-shard PostgreSQL cluster (each with 3 replicas)
- Redis cluster (6 nodes)
- Monthly cost: ~$50,000

Performance:
- Latency: p99 < 50ms
- Availability: 99.99%
```

**Scenario 2: Cost-Optimized (Good Enough)**
```
- 10 API servers
- 2-shard PostgreSQL (each with 2 replicas)
- Redis cluster (3 nodes)
- Monthly cost: ~$10,000

Performance:
- Latency: p99 < 100ms
- Availability: 99.9%
```

**Chosen: Scenario 2** (meets requirements at 1/5th cost)

---

## 🎯 Framework Summary

| Step | Time | Output |
|------|------|--------|
| 1. Requirements | 5 min | Clear functional & non-functional reqs |
| 2. Capacity | 5 min | QPS, storage, bandwidth numbers |
| 3. API Design | 5 min | REST/gRPC endpoints |
| 4. Schema | 5 min | SQL/NoSQL tables |
| 5. High-Level | 10 min | Architecture diagram |
| 6. Deep-Dive | 15 min | 2-3 components in detail |
| 7. Trade-offs | 10 min | Discuss alternatives |

**Total: 55 minutes** (leaves 5 min buffer)

---

**Next:** Practice with real scenarios → [Scenarios](./scenarios/)
