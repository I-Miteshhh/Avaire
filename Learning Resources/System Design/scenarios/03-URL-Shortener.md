# Design URL Shortener (like bit.ly) - Complete System Design

**Difficulty:** ⭐⭐⭐⭐  
**Interview Frequency:** Extremely High (Every company, 40 LPA+)  
**Time to Complete:** 30-45 minutes  
**Real-World Examples:** bit.ly, TinyURL, goo.gl, ow.ly

---

## 📋 Problem Statement

**Design a URL shortening service that can:**
- Convert long URLs to short, unique identifiers
- Redirect users from short URLs to original URLs
- Track analytics (clicks, referrers, locations)
- Handle 1 billion URLs
- Serve 10,000 redirects per second
- Provide custom short links (vanity URLs)
- Support link expiration
- Prevent abuse and spam

---

## 🎯 Requirements Analysis

### **Functional Requirements**
1. ✅ Shorten long URLs to unique short codes
2. ✅ Redirect short URLs to original URLs
3. ✅ Custom aliases (e.g., bit.ly/my-brand)
4. ✅ Link expiration (optional TTL)
5. ✅ Click analytics and tracking
6. ✅ API for programmatic access

### **Non-Functional Requirements**
1. **High Availability** - 99.99% uptime
2. **Low Latency** - <100ms redirect time
3. **Scalability** - Handle billions of URLs
4. **Durability** - URLs never lost
5. **Security** - Prevent malicious URLs

### **Extended Features**
- QR code generation
- Link preview/metadata
- Bulk URL shortening
- API rate limiting
- User dashboards

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                              │
├─────────────────────────────────────────────────────────────┤
│  Web App │ Mobile App │ Browser Extension │ API Clients     │
└────┬────────────┬──────────────┬──────────────────┬─────────┘
     │            │              │                  │
     ▼            ▼              ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                 CDN (CloudFront / Cloudflare)               │
├─────────────────────────────────────────────────────────────┤
│  - Cache redirect responses (302)                           │
│  - Serve static assets                                      │
│  - DDoS protection                                          │
└────┬────────────┬──────────────┬──────────────────┬─────────┘
     │            │              │                  │
     ▼            ▼              ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│              LOAD BALANCER (ELB / Nginx)                    │
├─────────────────────────────────────────────────────────────┤
│  - Geographic routing                                        │
│  - Health checks                                            │
│  - SSL termination                                          │
└────┬────────────┬──────────────┬──────────────────┬─────────┘
     │            │              │                  │
     ▼            ▼              ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                  APPLICATION SERVERS                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐        ┌──────────────────┐          │
│  │  Write Service   │        │  Read Service    │          │
│  │  - Create short  │        │  - Redirect      │          │
│  │  - Validation    │        │  - Analytics     │          │
│  │  - Rate limiting │        │  - Caching       │          │
│  └──────────────────┘        └──────────────────┘          │
└────┬────────────┬──────────────┬──────────────────┬─────────┘
     │            │              │                  │
     ▼            ▼              ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                   CACHE LAYER (Redis Cluster)               │
├─────────────────────────────────────────────────────────────┤
│  - Hot URL mappings (99% cache hit)                         │
│  - Rate limiting counters                                   │
│  - Analytics buffers                                        │
└────┬────────────┬──────────────┬──────────────────┬─────────┘
     │            │              │                  │
     ▼            ▼              ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                  DATABASE LAYER                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────┐          │
│  │  Primary DB (PostgreSQL / MySQL)             │          │
│  │  - URL mappings                              │          │
│  │  - User data                                 │          │
│  │  - Master for writes                         │          │
│  └──────────────────────────────────────────────┘          │
│                                                              │
│  ┌──────────────────────────────────────────────┐          │
│  │  Read Replicas (Multi-region)                │          │
│  │  - Redirect lookups                          │          │
│  │  - Analytics queries                         │          │
│  └──────────────────────────────────────────────┘          │
│                                                              │
│  ┌──────────────────────────────────────────────┐          │
│  │  Analytics DB (ClickHouse / BigQuery)        │          │
│  │  - Click events                              │          │
│  │  - Aggregated stats                          │          │
│  └──────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  SUPPORTING SERVICES                         │
├─────────────────────────────────────────────────────────────┤
│  - ID Generation Service (Snowflake)                        │
│  - Analytics Pipeline (Kafka + Spark)                       │
│  - URL Validation / Safety Check                           │
│  - Monitoring (Prometheus + Grafana)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 Core Components Implementation

### **1. Short Code Generation Strategy**

```python
import hashlib
import base62
import time
from typing import Optional

class ShortCodeGenerator:
    """
    Multiple strategies for generating short codes
    """
    
    def __init__(self):
        self.base62_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.counter = 0
        self.machine_id = 1  # Unique per server
    
    def generate_hash_based(self, long_url: str, length: int = 7) -> str:
        """
        Strategy 1: Hash-based (MD5 + Base62)
        Pros: Fast, deterministic for same URL
        Cons: Collision possible, need to check DB
        """
        
        # MD5 hash of URL
        hash_digest = hashlib.md5(long_url.encode()).hexdigest()
        
        # Convert first 8 chars of hex to integer
        hash_int = int(hash_digest[:8], 16)
        
        # Convert to base62
        short_code = self._to_base62(hash_int)[:length]
        
        return short_code
    
    def generate_counter_based(self) -> str:
        """
        Strategy 2: Auto-increment counter + Base62
        Pros: No collisions, predictable
        Cons: Need distributed counter, reveals info about total URLs
        """
        
        # Get next counter value (from Redis or DB sequence)
        counter_value = self._get_next_counter()
        
        # Convert to base62
        short_code = self._to_base62(counter_value)
        
        # Pad to minimum length
        return short_code.rjust(7, '0')
    
    def generate_snowflake(self) -> str:
        """
        Strategy 3: Twitter Snowflake-like ID
        Pros: Unique, distributed, time-ordered
        Cons: Slightly longer codes
        
        Format: 
        - 41 bits: timestamp (milliseconds since epoch)
        - 10 bits: machine ID
        - 12 bits: sequence number
        """
        
        # Current timestamp in milliseconds
        timestamp = int(time.time() * 1000)
        
        # Snowflake ID components
        timestamp_bits = (timestamp - 1609459200000) << 22  # Custom epoch: 2021-01-01
        machine_bits = self.machine_id << 12
        sequence_bits = self.counter % 4096
        
        # Combine
        snowflake_id = timestamp_bits | machine_bits | sequence_bits
        
        # Convert to base62
        short_code = self._to_base62(snowflake_id)
        
        self.counter += 1
        
        return short_code
    
    def generate_random(self, length: int = 7) -> str:
        """
        Strategy 4: Random generation
        Pros: Unpredictable, secure
        Cons: Need to check for collisions
        """
        
        import secrets
        
        # Generate random bytes
        random_bytes = secrets.token_bytes(8)
        
        # Convert to integer
        random_int = int.from_bytes(random_bytes, byteorder='big')
        
        # Convert to base62
        short_code = self._to_base62(random_int)[:length]
        
        return short_code
    
    def _to_base62(self, num: int) -> str:
        """Convert number to base62 string"""
        
        if num == 0:
            return self.base62_chars[0]
        
        result = []
        while num > 0:
            result.append(self.base62_chars[num % 62])
            num //= 62
        
        return ''.join(reversed(result))
    
    def _from_base62(self, code: str) -> int:
        """Convert base62 string to number"""
        
        num = 0
        for char in code:
            num = num * 62 + self.base62_chars.index(char)
        return num
    
    def _get_next_counter(self) -> int:
        """Get next counter from Redis (distributed counter)"""
        
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # Atomic increment
        return r.incr('url_shortener:counter')


### **2. URL Shortening Service**

```python
from flask import Flask, request, jsonify, redirect
from dataclasses import dataclass
from datetime import datetime, timedelta
import re
import validators

@dataclass
class URLMapping:
    short_code: str
    long_url: str
    user_id: Optional[str]
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool
    click_count: int

class URLShortenerService:
    def __init__(self, db_client, cache_client, code_generator):
        self.db = db_client
        self.cache = cache_client
        self.code_generator = code_generator
        self.app = Flask(__name__)
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/api/v1/shorten', methods=['POST'])
        def shorten_url():
            return self.create_short_url(request.get_json())
        
        @self.app.route('/<short_code>', methods=['GET'])
        def redirect_url(short_code):
            return self.handle_redirect(short_code)
        
        @self.app.route('/api/v1/analytics/<short_code>', methods=['GET'])
        def get_analytics(short_code):
            return self.get_url_analytics(short_code)
    
    def create_short_url(self, data: dict) -> tuple:
        """
        Create shortened URL with validation and collision handling
        """
        
        long_url = data.get('long_url')
        custom_alias = data.get('custom_alias')
        user_id = data.get('user_id')
        expires_in_days = data.get('expires_in_days')
        
        # 1. Validate URL
        if not validators.url(long_url):
            return jsonify({'error': 'Invalid URL format'}), 400
        
        # 2. Check if URL is safe (not spam/malicious)
        if not self._is_safe_url(long_url):
            return jsonify({'error': 'URL flagged as unsafe'}), 400
        
        # 3. Check rate limiting
        if not self._check_rate_limit(user_id or request.remote_addr):
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        # 4. Handle custom alias
        if custom_alias:
            # Validate custom alias
            if not self._is_valid_alias(custom_alias):
                return jsonify({'error': 'Invalid custom alias format'}), 400
            
            # Check if alias is available
            if self._alias_exists(custom_alias):
                return jsonify({'error': 'Custom alias already taken'}), 409
            
            short_code = custom_alias
        else:
            # Generate short code with collision handling
            short_code = self._generate_unique_short_code(long_url)
        
        # 5. Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # 6. Create mapping
        url_mapping = URLMapping(
            short_code=short_code,
            long_url=long_url,
            user_id=user_id,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            is_active=True,
            click_count=0
        )
        
        # 7. Store in database
        self._store_url_mapping(url_mapping)
        
        # 8. Cache the mapping for fast lookups
        self._cache_url_mapping(url_mapping)
        
        # 9. Return response
        short_url = f"https://short.ly/{short_code}"
        
        return jsonify({
            'short_url': short_url,
            'short_code': short_code,
            'long_url': long_url,
            'created_at': url_mapping.created_at.isoformat(),
            'expires_at': url_mapping.expires_at.isoformat() if expires_at else None
        }), 201
    
    def handle_redirect(self, short_code: str):
        """
        Handle redirect with caching and analytics
        """
        
        # 1. Try cache first (99% hit rate expected)
        cached_url = self.cache.get(f"url:{short_code}")
        
        if cached_url:
            long_url = cached_url
            cache_hit = True
        else:
            # 2. Cache miss - query database
            url_mapping = self._get_url_mapping(short_code)
            
            if not url_mapping:
                return "URL not found", 404
            
            # Check if expired
            if url_mapping.expires_at and url_mapping.expires_at < datetime.utcnow():
                return "URL has expired", 410  # Gone
            
            if not url_mapping.is_active:
                return "URL has been deactivated", 410
            
            long_url = url_mapping.long_url
            cache_hit = False
            
            # Cache for future requests
            self.cache.setex(
                f"url:{short_code}",
                3600,  # 1 hour TTL
                long_url
            )
        
        # 3. Track analytics asynchronously (don't block redirect)
        self._track_click_async(short_code, request)
        
        # 4. Redirect with 302 (temporary) to allow analytics tracking
        # Use 301 (permanent) only if you don't need analytics
        return redirect(long_url, code=302)
    
    def _generate_unique_short_code(self, long_url: str, max_retries: int = 5) -> str:
        """
        Generate unique short code with collision handling
        """
        
        for attempt in range(max_retries):
            # Try hash-based first (deterministic)
            if attempt == 0:
                short_code = self.code_generator.generate_hash_based(long_url)
            else:
                # Fallback to random if collision
                short_code = self.code_generator.generate_random()
            
            # Check if code exists
            if not self._short_code_exists(short_code):
                return short_code
        
        # Fallback to guaranteed unique (counter-based)
        return self.code_generator.generate_counter_based()
    
    def _short_code_exists(self, short_code: str) -> bool:
        """Check if short code already exists"""
        
        # Check cache first
        if self.cache.exists(f"url:{short_code}"):
            return True
        
        # Check database
        return self.db.exists('url_mappings', {'short_code': short_code})
    
    def _is_safe_url(self, url: str) -> bool:
        """
        Check if URL is safe (not spam/malicious)
        Integration with Google Safe Browsing API or similar
        """
        
        # 1. Check against known malicious domains
        malicious_domains = self._get_malicious_domains()
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        
        if domain in malicious_domains:
            return False
        
        # 2. Check URL pattern for suspicious characteristics
        suspicious_patterns = [
            r'.*\.exe$',  # Executable files
            r'.*phishing.*',  # Phishing keywords
            r'.*malware.*'
        ]
        
        for pattern in suspicious_patterns:
            if re.match(pattern, url, re.IGNORECASE):
                return False
        
        # 3. Check with Google Safe Browsing API (in production)
        # safe_browsing_result = self._check_safe_browsing(url)
        # if not safe_browsing_result:
        #     return False
        
        return True
    
    def _check_rate_limit(self, identifier: str) -> bool:
        """
        Check rate limit using Redis
        Sliding window rate limiting
        """
        
        key = f"rate_limit:{identifier}"
        window = 3600  # 1 hour
        max_requests = 100  # 100 URLs per hour
        
        # Use Redis sorted set for sliding window
        now = time.time()
        
        # Remove old entries
        self.cache.zremrangebyscore(key, 0, now - window)
        
        # Count recent requests
        request_count = self.cache.zcard(key)
        
        if request_count >= max_requests:
            return False
        
        # Add current request
        self.cache.zadd(key, {str(now): now})
        self.cache.expire(key, window)
        
        return True
    
    def _track_click_async(self, short_code: str, request):
        """
        Track click analytics asynchronously
        """
        
        import threading
        
        def track():
            click_data = {
                'short_code': short_code,
                'timestamp': datetime.utcnow(),
                'ip_address': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'referer': request.headers.get('Referer'),
                'country': self._get_country_from_ip(request.remote_addr),
                'device_type': self._get_device_type(request.headers.get('User-Agent'))
            }
            
            # Send to analytics pipeline (Kafka)
            self._send_to_analytics_pipeline(click_data)
            
            # Increment counter in cache
            self.cache.incr(f"clicks:{short_code}")
        
        # Run in background thread
        thread = threading.Thread(target=track)
        thread.daemon = True
        thread.start()
    
    def _store_url_mapping(self, mapping: URLMapping):
        """Store URL mapping in database"""
        
        query = """
        INSERT INTO url_mappings 
        (short_code, long_url, user_id, created_at, expires_at, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        self.db.execute(query, (
            mapping.short_code,
            mapping.long_url,
            mapping.user_id,
            mapping.created_at,
            mapping.expires_at,
            mapping.is_active
        ))
    
    def get_url_analytics(self, short_code: str) -> tuple:
        """Get analytics for shortened URL"""
        
        # Get basic info
        url_mapping = self._get_url_mapping(short_code)
        
        if not url_mapping:
            return jsonify({'error': 'URL not found'}), 404
        
        # Get click analytics from analytics DB
        analytics = self._query_analytics_db(short_code)
        
        return jsonify({
            'short_code': short_code,
            'long_url': url_mapping.long_url,
            'created_at': url_mapping.created_at.isoformat(),
            'total_clicks': analytics['total_clicks'],
            'clicks_by_country': analytics['clicks_by_country'],
            'clicks_by_device': analytics['clicks_by_device'],
            'clicks_by_referer': analytics['clicks_by_referer'],
            'click_timeline': analytics['click_timeline']
        }), 200


### **3. Database Schema**

```sql
-- URL Mappings Table
CREATE TABLE url_mappings (
    id BIGSERIAL PRIMARY KEY,
    short_code VARCHAR(10) UNIQUE NOT NULL,
    long_url TEXT NOT NULL,
    user_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    click_count BIGINT DEFAULT 0,
    
    INDEX idx_short_code (short_code),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- Partition by creation month for efficient archival
CREATE TABLE url_mappings_2024_01 PARTITION OF url_mappings
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Click Analytics Table (ClickHouse for better performance)
CREATE TABLE click_events (
    short_code String,
    timestamp DateTime,
    ip_address String,
    country LowCardinality(String),
    device_type LowCardinality(String),
    referer String,
    user_agent String
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (short_code, timestamp)
TTL timestamp + INTERVAL 90 DAY;

-- Aggregated Analytics (Materialized View)
CREATE MATERIALIZED VIEW click_analytics_hourly
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (short_code, hour, country, device_type)
AS SELECT
    short_code,
    toStartOfHour(timestamp) AS hour,
    country,
    device_type,
    count() AS click_count
FROM click_events
GROUP BY short_code, hour, country, device_type;
```

---

## 🎓 Interview Discussion Points

### **Capacity Estimation:**
```
Writes (URL creation): 100/sec
Reads (Redirects): 10,000/sec (100:1 read-write ratio)
Storage per URL: ~500 bytes
Total URLs: 1 billion
Total storage: 1B × 500 bytes = 500 GB

Short code length calculation:
- 62^6 = 56.8 billion combinations (6 chars)
- 62^7 = 3.5 trillion combinations (7 chars) ✓
```

### **Trade-offs:**
1. **Hash vs Counter vs Random**
   - Hash: Fast but collision possible
   - Counter: No collision but needs coordination
   - Random: Secure but requires DB check

2. **301 vs 302 Redirect**
   - 301: Browser caches, faster but no analytics
   - 302: Always hits server, enables tracking ✓

3. **SQL vs NoSQL**
   - SQL: ACID, relational queries
   - NoSQL: Better horizontal scaling
   - Recommendation: SQL for mappings, ClickHouse for analytics

**This demonstrates complete URL shortener design - a must-know for every interview!** 🔗
