# Design Distributed Rate Limiter - Complete System Design

**Difficulty:** ⭐⭐⭐⭐  
**Interview Frequency:** Very High (All tech companies, 40 LPA+)  
**Time to Complete:** 30-40 minutes  
**Real-World Examples:** Stripe API, Twitter API, AWS API Gateway

---

## 📋 Problem Statement

**Design a distributed rate limiter that can:**
- Limit requests per user/IP/API key
- Support multiple algorithms (token bucket, leaky bucket, sliding window)
- Handle 1 million requests per second
- Provide accurate limiting across distributed servers
- Support different rate limit tiers (free: 100/min, premium: 10K/min)
- Return remaining quota in response headers
- Handle burst traffic gracefully
- Provide analytics on rate limit violations

---

## 🏗️ Architecture & Algorithms

```
┌──────────────────────────────────────────────────────────────┐
│              RATE LIMITING ALGORITHMS                         │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  1. TOKEN BUCKET                                             │
│     ┌────────────────────────────────────────────────────┐  │
│     │  Bucket: capacity = 100 tokens                     │  │
│     │  Refill: 10 tokens/second                          │  │
│     │                                                     │  │
│     │  ┌──────────────┐                                  │  │
│     │  │ ████████████ │ ← 100 tokens                    │  │
│     │  │ ████████████ │                                  │  │
│     │  │ ██░░░░░░░░░░ │ ← 40 consumed, 60 remaining     │  │
│     │  └──────────────┘                                  │  │
│     │                                                     │  │
│     │  Algorithm:                                         │  │
│     │    tokens = min(capacity, tokens + refill_rate × Δt)│  │
│     │    if tokens >= cost:                              │  │
│     │        tokens -= cost                              │  │
│     │        allow()                                      │  │
│     │    else:                                            │  │
│     │        deny()                                       │  │
│     │                                                     │  │
│     │  Pros: Allows bursts up to capacity                │  │
│     │  Cons: Complex to implement correctly              │  │
│     └────────────────────────────────────────────────────┘  │
│                                                               │
│  2. SLIDING WINDOW LOG                                       │
│     ┌────────────────────────────────────────────────────┐  │
│     │  Window: 1 minute (60 seconds)                     │  │
│     │  Limit: 100 requests                                │  │
│     │                                                     │  │
│     │  Request Log:                                       │  │
│     │  [t-50s, t-45s, t-30s, ..., t-2s, t-1s, t-0s]     │  │
│     │                                                     │  │
│     │  Algorithm:                                         │  │
│     │    Remove timestamps older than (now - window)     │  │
│     │    count = len(log)                                │  │
│     │    if count < limit:                               │  │
│     │        log.append(now)                             │  │
│     │        allow()                                      │  │
│     │    else:                                            │  │
│     │        deny()                                       │  │
│     │                                                     │  │
│     │  Pros: Very accurate                                │  │
│     │  Cons: Memory intensive (store all timestamps)     │  │
│     └────────────────────────────────────────────────────┘  │
│                                                               │
│  3. SLIDING WINDOW COUNTER (Hybrid)                         │
│     ┌────────────────────────────────────────────────────┐  │
│     │  Current window: 100 requests                      │  │
│     │  Previous window: 80 requests                      │  │
│     │  Time in current window: 40%                       │  │
│     │                                                     │  │
│     │  Estimated count:                                   │  │
│     │    = prev_count × (1 - progress) + curr_count      │  │
│     │    = 80 × 0.6 + 100                                │  │
│     │    = 148 requests                                   │  │
│     │                                                     │  │
│     │  if estimated_count < limit:                       │  │
│     │      allow()                                        │  │
│     │  else:                                              │  │
│     │      deny()                                         │  │
│     │                                                     │  │
│     │  Pros: Memory efficient, accurate                  │  │
│     │  Cons: Slight approximation                        │  │
│     └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│           DISTRIBUTED RATE LIMITER (Redis)                    │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐        │
│  │  API       │    │  API       │    │  API       │        │
│  │  Server 1  │    │  Server 2  │    │  Server 3  │        │
│  └─────┬──────┘    └─────┬──────┘    └─────┬──────┘        │
│        │                 │                 │                 │
│        └─────────────────┼─────────────────┘                 │
│                          │                                    │
│                          ▼                                    │
│              ┌───────────────────────┐                       │
│              │   REDIS CLUSTER       │                       │
│              │   ━━━━━━━━━━━━━━━━━   │                       │
│              │                       │                       │
│              │  Key Pattern:         │                       │
│              │  rate_limit:{id}:     │                       │
│              │    {window}           │                       │
│              │                       │                       │
│              │  Example:             │                       │
│              │  rate_limit:user123:  │                       │
│              │    1640000000         │                       │
│              │  → count: 45          │                       │
│              │  → expires: 60s       │                       │
│              └───────────────────────┘                       │
└──────────────────────────────────────────────────────────────┘
```

---

## 💻 Implementation

### **1. Token Bucket (Redis Lua)**

```python
import redis
import time

class TokenBucketRateLimiter:
    """
    Token bucket rate limiter using Redis
    """
    
    LUA_SCRIPT = """
    local key = KEYS[1]
    local capacity = tonumber(ARGV[1])
    local refill_rate = tonumber(ARGV[2])
    local cost = tonumber(ARGV[3])
    local now = tonumber(ARGV[4])
    
    local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
    local tokens = tonumber(bucket[1])
    local last_refill = tonumber(bucket[2])
    
    if tokens == nil then
        tokens = capacity
        last_refill = now
    end
    
    -- Calculate tokens to add
    local elapsed = now - last_refill
    local tokens_to_add = elapsed * refill_rate
    tokens = math.min(capacity, tokens + tokens_to_add)
    
    local allowed = 0
    if tokens >= cost then
        tokens = tokens - cost
        allowed = 1
    end
    
    -- Update bucket
    redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
    redis.call('EXPIRE', key, 3600)
    
    return {allowed, tokens}
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.script = self.redis.register_script(self.LUA_SCRIPT)
    
    def allow_request(self, identifier: str, capacity: int = 100, 
                     refill_rate: float = 10.0, cost: int = 1) -> tuple:
        """
        Check if request is allowed
        
        Args:
            identifier: User ID, IP, API key
            capacity: Max tokens in bucket
            refill_rate: Tokens per second
            cost: Tokens consumed per request
        
        Returns:
            (allowed: bool, remaining: int)
        """
        
        key = f"rate_limit:token_bucket:{identifier}"
        now = time.time()
        
        result = self.script(
            keys=[key],
            args=[capacity, refill_rate, cost, now]
        )
        
        allowed = bool(result[0])
        remaining = int(result[1])
        
        return allowed, remaining


### **2. Sliding Window Counter (Redis)**

```python
class SlidingWindowRateLimiter:
    """
    Sliding window counter using Redis
    Memory efficient, good accuracy
    """
    
    LUA_SCRIPT = """
    local current_key = KEYS[1]
    local previous_key = KEYS[2]
    local limit = tonumber(ARGV[1])
    local window = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])
    
    -- Get counts
    local current_count = tonumber(redis.call('GET', current_key) or 0)
    local previous_count = tonumber(redis.call('GET', previous_key) or 0)
    
    -- Calculate progress in current window
    local current_window_start = math.floor(now / window) * window
    local progress = (now - current_window_start) / window
    
    -- Weighted count
    local estimated_count = previous_count * (1 - progress) + current_count
    
    if estimated_count < limit then
        -- Increment current window
        redis.call('INCR', current_key)
        redis.call('EXPIRE', current_key, window * 2)
        return {1, limit - current_count - 1}
    else
        return {0, 0}
    end
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.script = self.redis.register_script(self.LUA_SCRIPT)
    
    def allow_request(self, identifier: str, limit: int = 100, 
                     window: int = 60) -> tuple:
        """
        Check if request is allowed
        
        Args:
            identifier: User ID, IP, API key
            limit: Max requests per window
            window: Window size in seconds
        
        Returns:
            (allowed: bool, remaining: int)
        """
        
        now = time.time()
        
        # Current and previous window keys
        current_window = int(now // window)
        previous_window = current_window - 1
        
        current_key = f"rate_limit:sliding:{identifier}:{current_window}"
        previous_key = f"rate_limit:sliding:{identifier}:{previous_window}"
        
        result = self.script(
            keys=[current_key, previous_key],
            args=[limit, window, now]
        )
        
        allowed = bool(result[0])
        remaining = int(result[1])
        
        return allowed, remaining


### **3. Fixed Window Counter (Simple)**

```python
class FixedWindowRateLimiter:
    """
    Simple fixed window rate limiter
    Fast but less accurate
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def allow_request(self, identifier: str, limit: int = 100, 
                     window: int = 60) -> tuple:
        """
        Fixed window rate limiting
        """
        
        # Window key based on current time
        current_window = int(time.time() // window)
        key = f"rate_limit:fixed:{identifier}:{current_window}"
        
        # Atomic increment
        pipeline = self.redis.pipeline()
        pipeline.incr(key)
        pipeline.expire(key, window * 2)  # Cleanup old keys
        results = pipeline.execute()
        
        count = results[0]
        
        if count <= limit:
            return True, limit - count
        else:
            return False, 0


### **4. Multi-Tier Rate Limiter**

```python
from enum import Enum

class UserTier(Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class MultiTierRateLimiter:
    """
    Rate limiter with different tiers
    """
    
    TIER_LIMITS = {
        UserTier.FREE: {"requests_per_minute": 100, "requests_per_day": 1000},
        UserTier.BASIC: {"requests_per_minute": 1000, "requests_per_day": 50000},
        UserTier.PREMIUM: {"requests_per_minute": 10000, "requests_per_day": 1000000},
        UserTier.ENTERPRISE: {"requests_per_minute": 100000, "requests_per_day": 10000000}
    }
    
    def __init__(self, redis_client: redis.Redis):
        self.sliding_limiter = SlidingWindowRateLimiter(redis_client)
    
    def allow_request(self, user_id: str, tier: UserTier) -> dict:
        """
        Check multiple rate limits
        """
        
        limits = self.TIER_LIMITS[tier]
        
        # Check per-minute limit
        minute_allowed, minute_remaining = self.sliding_limiter.allow_request(
            f"{user_id}:minute",
            limit=limits["requests_per_minute"],
            window=60
        )
        
        # Check per-day limit
        day_allowed, day_remaining = self.sliding_limiter.allow_request(
            f"{user_id}:day",
            limit=limits["requests_per_day"],
            window=86400
        )
        
        allowed = minute_allowed and day_allowed
        
        return {
            "allowed": allowed,
            "rate_limit_minute": limits["requests_per_minute"],
            "rate_limit_day": limits["requests_per_day"],
            "remaining_minute": minute_remaining,
            "remaining_day": day_remaining,
            "retry_after": 60 if not minute_allowed else 0
        }


### **5. API Middleware (Flask)**

```python
from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)

def rate_limit(tier: UserTier):
    """
    Rate limiting decorator
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Get user/API key from request
            api_key = request.headers.get('X-API-Key')
            
            if not api_key:
                return jsonify({'error': 'Missing API key'}), 401
            
            # Check rate limit
            limiter = MultiTierRateLimiter(redis_client)
            result = limiter.allow_request(api_key, tier)
            
            # Add headers
            response_headers = {
                'X-RateLimit-Limit': result['rate_limit_minute'],
                'X-RateLimit-Remaining': result['remaining_minute'],
                'X-RateLimit-Reset': int(time.time()) + 60
            }
            
            if not result['allowed']:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': result['retry_after']
                }), 429, response_headers
            
            # Process request
            response = f(*args, **kwargs)
            
            # Add rate limit headers to response
            if isinstance(response, tuple):
                response_data, status_code = response
                return response_data, status_code, response_headers
            else:
                response.headers.update(response_headers)
                return response
        
        return wrapped
    return decorator


@app.route('/api/v1/data')
@rate_limit(UserTier.FREE)
def get_data():
    return jsonify({'data': 'Your data here'}), 200


### **6. Distributed Counter (for Analytics)**

```python
class RateLimitAnalytics:
    """
    Track rate limit violations
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def track_violation(self, identifier: str, endpoint: str):
        """
        Track rate limit violation
        """
        
        # Increment violation counter
        key = f"violations:{identifier}:{endpoint}"
        pipeline = self.redis.pipeline()
        pipeline.incr(key)
        pipeline.expire(key, 86400)  # 24 hours
        pipeline.execute()
        
        # Add to sorted set (leaderboard)
        self.redis.zincrby("violations:leaderboard", 1, identifier)
    
    def get_top_violators(self, n: int = 100):
        """
        Get top rate limit violators
        """
        
        violators = self.redis.zrevrange(
            "violations:leaderboard",
            0, n - 1,
            withscores=True
        )
        
        return [
            {"identifier": id, "violations": int(score)}
            for id, score in violators
        ]
```

---

## 🎓 Interview Points

**Capacity:**
```
QPS: 1M/sec
Redis memory: 10M users × 100 bytes = 1 GB
Latency: <5ms (Redis lookup)
```

**Comparison:**
- **Token Bucket**: Best for burst traffic
- **Sliding Window**: Most accurate
- **Fixed Window**: Simplest, fastest

**Key decisions:** Algorithm choice, distributed sync, tier management!
