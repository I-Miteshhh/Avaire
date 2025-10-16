# Design URL Shortener at Scale - Complete System Design

**Difficulty:** ⭐⭐⭐⭐  
**Interview Frequency:** Very High (Classic design problem)  
**Time to Complete:** 30-35 minutes  
**Real-World Examples:** bit.ly, TinyURL, goo.gl

---

## 📋 Problem Statement

**Design a URL shortener that can:**
- Shorten long URLs to 7-character codes
- Redirect users to original URLs (<10ms latency)
- Handle 1 billion URL shortenings per month
- Support custom aliases (vanity URLs)
- Track click analytics (geo, device, time)
- Provide expiration for URLs
- Prevent abuse (spam, malicious URLs)
- Support QR code generation
- Scale to 100K redirects per second

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                BASE62 ENCODING ALGORITHM                      │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Character set: [a-zA-Z0-9] (62 characters)                  │
│  Short URL length: 7 characters                              │
│  Total combinations: 62^7 = 3.5 trillion URLs               │
│                                                               │
│  Algorithm:                                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  1. Generate unique ID (auto-increment or UUID)        │ │
│  │     Example: ID = 123456789                            │ │
│  │                                                         │ │
│  │  2. Convert to Base62:                                 │ │
│  │     base62_chars = "0123456789abcdefghijklmnopqrs...Z" │ │
│  │                                                         │ │
│  │     result = ""                                         │ │
│  │     while id > 0:                                       │ │
│  │         result = base62_chars[id % 62] + result        │ │
│  │         id = id // 62                                   │ │
│  │                                                         │ │
│  │     123456789 → "8M0kX"                               │ │
│  │                                                         │ │
│  │  3. Pad to 7 characters:                               │ │
│  │     "8M0kX" → "008M0kX"                               │ │
│  │                                                         │ │
│  │  Short URL: example.com/008M0kX                       │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                   SYSTEM ARCHITECTURE                         │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    WRITE PATH                           ││
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━││
│  │                                                         ││
│  │  POST /shorten                                          ││
│  │  Body: {"url": "https://example.com/very/long/path"}  ││
│  │         │                                               ││
│  │         ▼                                               ││
│  │  ┌────────────────────┐                                ││
│  │  │  API Server        │                                ││
│  │  │  1. Validate URL   │                                ││
│  │  │  2. Check blacklist│                                ││
│  │  │  3. Get next ID    │ ← ID Generator (Redis INCR)   ││
│  │  │  4. Base62 encode  │                                ││
│  │  │  5. Store mapping  │                                ││
│  │  └─────────┬──────────┘                                ││
│  │            │                                            ││
│  │            ▼                                            ││
│  │  ┌────────────────────┐                                ││
│  │  │   PostgreSQL       │                                ││
│  │  │   ━━━━━━━━━━━━━━━  │                                ││
│  │  │   urls table:      │                                ││
│  │  │   ┌──────────────┐ │                                ││
│  │  │   │id | short_url│ │                                ││
│  │  │   │long_url      │ │                                ││
│  │  │   │user_id       │ │                                ││
│  │  │   │created_at    │ │                                ││
│  │  │   │expires_at    │ │                                ││
│  │  │   └──────────────┘ │                                ││
│  │  └────────────────────┘                                ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    READ PATH (REDIRECT)                 ││
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━││
│  │                                                         ││
│  │  GET /008M0kX                                          ││
│  │         │                                               ││
│  │         ▼                                               ││
│  │  ┌────────────────────┐                                ││
│  │  │  Redis Cache       │ ← Cache hit (99% case)        ││
│  │  │  Key: 008M0kX      │                                ││
│  │  │  Value: long_url   │                                ││
│  │  │  TTL: 24 hours     │                                ││
│  │  └─────────┬──────────┘                                ││
│  │            │ Cache miss (1%)                           ││
│  │            ▼                                            ││
│  │  ┌────────────────────┐                                ││
│  │  │   PostgreSQL       │                                ││
│  │  │   SELECT long_url  │                                ││
│  │  │   WHERE short_url  │                                ││
│  │  └─────────┬──────────┘                                ││
│  │            │                                            ││
│  │            ▼                                            ││
│  │  302 Redirect to long_url                             ││
│  │                                                         ││
│  │  (Async) Track click analytics → Kafka                ││
│  └─────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                   ANALYTICS PIPELINE                          │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Click Event:                                                │
│  {                                                            │
│    "short_url": "008M0kX",                                  │
│    "ip": "192.168.1.1",                                     │
│    "user_agent": "Mozilla/5.0...",                          │
│    "referer": "https://twitter.com",                        │
│    "timestamp": 1640000000                                   │
│  }                                                            │
│         │                                                     │
│         ▼                                                     │
│  ┌──────────────┐                                           │
│  │    Kafka     │                                           │
│  │  (clicks)    │                                           │
│  └──────┬───────┘                                           │
│         │                                                     │
│         ▼                                                     │
│  ┌──────────────────────────────────────────┐               │
│  │  Flink Stream Processing                 │               │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │               │
│  │  1. Parse user agent → device, browser   │               │
│  │  2. GeoIP lookup → country, city         │               │
│  │  3. Aggregate by 1-minute windows        │               │
│  │  4. Write to ClickHouse                   │               │
│  └──────────────────────────────────────────┘               │
│         │                                                     │
│         ▼                                                     │
│  ┌──────────────────────────────────────────┐               │
│  │  ClickHouse (Analytics)                   │               │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │               │
│  │  clicks table:                            │               │
│  │  ┌────────────────────────────────────┐  │               │
│  │  │ short_url | timestamp | country    │  │               │
│  │  │ device    | browser   | referer    │  │               │
│  │  └────────────────────────────────────┘  │               │
│  │                                            │               │
│  │  Analytics queries:                       │               │
│  │  - Clicks per day                         │               │
│  │  - Top countries                          │               │
│  │  - Device breakdown                       │               │
│  │  - Referer sources                        │               │
│  └──────────────────────────────────────────┘               │
└──────────────────────────────────────────────────────────────┘
```

---

## 💻 Implementation

### **1. Base62 Encoder**

```python
class Base62Encoder:
    """
    Convert integer IDs to Base62 strings
    """
    
    CHARSET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    BASE = 62
    
    @staticmethod
    def encode(num: int, min_length: int = 7) -> str:
        """
        Encode integer to Base62
        
        Example:
        123456789 → "8M0kX" → "008M0kX" (padded to 7)
        """
        
        if num == 0:
            return Base62Encoder.CHARSET[0] * min_length
        
        result = []
        while num > 0:
            result.append(Base62Encoder.CHARSET[num % Base62Encoder.BASE])
            num //= Base62Encoder.BASE
        
        # Reverse and pad
        encoded = ''.join(reversed(result))
        return encoded.rjust(min_length, Base62Encoder.CHARSET[0])
    
    @staticmethod
    def decode(encoded: str) -> int:
        """
        Decode Base62 string to integer
        """
        
        num = 0
        for char in encoded:
            num = num * Base62Encoder.BASE + Base62Encoder.CHARSET.index(char)
        return num


### **2. URL Shortener Service**

```python
import hashlib
import re
from typing import Optional
from datetime import datetime, timedelta

class URLShortener:
    """
    Core URL shortening logic
    """
    
    def __init__(self, db, redis_client, id_generator):
        self.db = db
        self.redis = redis_client
        self.id_gen = id_generator
        self.encoder = Base62Encoder()
    
    def shorten(self, long_url: str, user_id: Optional[str] = None,
                custom_alias: Optional[str] = None,
                expires_days: Optional[int] = None) -> str:
        """
        Shorten a URL
        
        Args:
            long_url: Original URL
            user_id: User creating the short URL
            custom_alias: Custom short code (vanity URL)
            expires_days: Expiration in days
        
        Returns:
            Short URL code
        """
        
        # 1. Validate URL
        if not self._is_valid_url(long_url):
            raise ValueError("Invalid URL format")
        
        # 2. Check blacklist (malware, spam)
        if self._is_blacklisted(long_url):
            raise ValueError("URL is blacklisted")
        
        # 3. Check if URL already shortened
        existing = self._find_existing(long_url, user_id)
        if existing:
            return existing
        
        # 4. Generate short code
        if custom_alias:
            # Validate custom alias
            if not self._is_valid_alias(custom_alias):
                raise ValueError("Invalid custom alias")
            
            # Check availability
            if self._alias_exists(custom_alias):
                raise ValueError("Alias already taken")
            
            short_code = custom_alias
        else:
            # Auto-generate
            url_id = self.id_gen.get_next_id()
            short_code = self.encoder.encode(url_id)
        
        # 5. Calculate expiration
        expires_at = None
        if expires_days:
            expires_at = datetime.now() + timedelta(days=expires_days)
        
        # 6. Store in database
        self.db.execute("""
            INSERT INTO urls (short_url, long_url, user_id, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?)
        """, (short_code, long_url, user_id, datetime.now(), expires_at))
        
        # 7. Cache in Redis
        self.redis.setex(
            f"url:{short_code}",
            86400,  # 24 hours
            long_url
        )
        
        return short_code
    
    def expand(self, short_code: str) -> Optional[str]:
        """
        Get original URL from short code
        """
        
        # 1. Check cache
        cache_key = f"url:{short_code}"
        long_url = self.redis.get(cache_key)
        
        if long_url:
            return long_url.decode()
        
        # 2. Query database
        result = self.db.query("""
            SELECT long_url, expires_at
            FROM urls
            WHERE short_url = ?
        """, (short_code,))
        
        if not result:
            return None
        
        long_url, expires_at = result[0]
        
        # 3. Check expiration
        if expires_at and datetime.now() > expires_at:
            return None
        
        # 4. Cache for next time
        self.redis.setex(cache_key, 86400, long_url)
        
        return long_url
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )
        return bool(pattern.match(url))
    
    def _is_blacklisted(self, url: str) -> bool:
        """Check if URL is in blacklist"""
        # Hash URL for privacy
        url_hash = hashlib.sha256(url.encode()).hexdigest()
        return self.redis.sismember("blacklist", url_hash)
    
    def _find_existing(self, long_url: str, user_id: str) -> Optional[str]:
        """Find existing short URL for same long URL"""
        result = self.db.query("""
            SELECT short_url FROM urls
            WHERE long_url = ? AND user_id = ?
            AND (expires_at IS NULL OR expires_at > ?)
            LIMIT 1
        """, (long_url, user_id, datetime.now()))
        
        return result[0][0] if result else None


### **3. ID Generator (Redis)**

```python
class RedisIDGenerator:
    """
    Generate unique IDs using Redis INCR
    """
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.key = "url_id_counter"
    
    def get_next_id(self) -> int:
        """
        Atomic increment
        """
        return self.redis.incr(self.key)


### **4. Click Analytics Tracker**

```python
from kafka import KafkaProducer
import json
from user_agents import parse

class ClickTracker:
    """
    Track URL clicks for analytics
    """
    
    def __init__(self, kafka_producer, geoip_db):
        self.kafka = kafka_producer
        self.geoip = geoip_db
    
    def track_click(self, short_code: str, request):
        """
        Track click asynchronously
        """
        
        # Parse user agent
        user_agent = parse(request.headers.get('User-Agent', ''))
        
        # Get geo location from IP
        ip = request.remote_addr
        geo = self.geoip.lookup(ip)
        
        # Build event
        event = {
            'short_url': short_code,
            'timestamp': int(time.time() * 1000),
            'ip': ip,
            'country': geo.get('country'),
            'city': geo.get('city'),
            'device': user_agent.device.family,
            'browser': user_agent.browser.family,
            'os': user_agent.os.family,
            'referer': request.headers.get('Referer')
        }
        
        # Send to Kafka (non-blocking)
        self.kafka.send('url_clicks', json.dumps(event).encode())


### **5. API Endpoints (Flask)**

```python
from flask import Flask, request, redirect, jsonify

app = Flask(__name__)

@app.route('/shorten', methods=['POST'])
def shorten_url():
    """
    POST /shorten
    Body: {
        "url": "https://example.com/long/path",
        "custom_alias": "mylink",  // optional
        "expires_days": 30          // optional
    }
    """
    
    data = request.json
    long_url = data.get('url')
    custom_alias = data.get('custom_alias')
    expires_days = data.get('expires_days')
    user_id = request.headers.get('X-User-ID', 'anonymous')
    
    try:
        short_code = url_shortener.shorten(
            long_url,
            user_id=user_id,
            custom_alias=custom_alias,
            expires_days=expires_days
        )
        
        short_url = f"https://short.ly/{short_code}"
        
        return jsonify({
            'short_url': short_url,
            'short_code': short_code,
            'original_url': long_url
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@app.route('/<short_code>')
def redirect_url(short_code):
    """
    GET /{short_code}
    Redirects to original URL
    """
    
    # Get original URL
    long_url = url_shortener.expand(short_code)
    
    if not long_url:
        return "URL not found or expired", 404
    
    # Track click (async)
    click_tracker.track_click(short_code, request)
    
    # 302 redirect (temporary)
    return redirect(long_url, code=302)


@app.route('/analytics/<short_code>')
def get_analytics(short_code):
    """
    GET /analytics/{short_code}
    Returns click analytics
    """
    
    # Query ClickHouse
    stats = clickhouse.query(f"""
        SELECT
            COUNT(*) as total_clicks,
            uniq(ip) as unique_visitors,
            topK(5)(country) as top_countries,
            topK(5)(device) as top_devices,
            topK(5)(referer) as top_referers
        FROM clicks
        WHERE short_url = '{short_code}'
        AND timestamp >= now() - INTERVAL 30 DAY
    """)
    
    return jsonify(stats), 200
```

---

## 🎓 Interview Points

**Capacity Estimation:**
```
Shortenings: 1B/month = 385/sec
Redirects: 100K/sec (read-heavy, 100:1 ratio)

Storage:
1B URLs × 500 bytes = 500 GB/month
3 years: 18 TB

Cache (Redis):
100M hot URLs × 500 bytes = 50 GB
```

**Key Design Choices:**
- **Base62 vs UUID**: Base62 shorter (7 chars vs 36), more user-friendly
- **Auto-increment vs Hash**: Auto-increment predictable but simpler; hash collision-free
- **Cache strategy**: Write-through for writes, cache-aside for reads
- **Analytics**: Async Kafka → Flink → ClickHouse (don't block redirects)

Perfect for 40 LPA interviews!