# Distributed Rate Limiter - Production Implementation

**Target Scale:** Handle rate limiting for systems processing **1M+ requests/sec** across distributed infrastructure

---

## Table of Contents
1. [Problem Statement](#1-problem-statement)
2. [Requirements](#2-requirements)
3. [Rate Limiting Algorithms](#3-rate-limiting-algorithms)
4. [Architecture](#4-architecture)
5. [Implementation](#5-implementation)
6. [Deployment](#6-deployment)
7. [Performance](#7-performance)

---

## 1. Problem Statement

### What is Rate Limiting?

Rate limiting controls the rate at which users can make requests to prevent abuse, ensure fair usage, and protect backend services from overload.

**Real-World Examples:**
- **Twitter API:** 300 requests per 15 minutes per user
- **GitHub API:** 5000 requests per hour per user
- **Stripe API:** 100 requests per second per account
- **DDoS Protection:** Block IPs making > 1000 requests/sec

### Use Cases

1. **API Gateway:** Limit requests per API key
2. **Authentication:** Prevent brute force attacks (5 failed logins per minute)
3. **Resource Protection:** Limit expensive operations (100 database queries/user/minute)
4. **Fair Usage:** Ensure one user doesn't consume all resources

---

## 2. Requirements

### Functional Requirements

1. **Multiple rate limiting strategies:**
   - Fixed window
   - Sliding window log
   - Sliding window counter
   - Token bucket
   - Leaky bucket

2. **Flexible configuration:**
   - Per user, IP, API key, or custom identifier
   - Different limits for different endpoints
   - Tiered limits (free tier: 100/hr, paid tier: 10,000/hr)

3. **Distributed support:**
   - Works across multiple servers
   - Consistent rate limiting globally
   - No single point of failure

4. **Response headers:**
   ```
   X-RateLimit-Limit: 1000
   X-RateLimit-Remaining: 847
   X-RateLimit-Reset: 1640000000
   ```

### Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Latency | <1ms P99 |
| Throughput | 1M+ decisions/sec |
| Availability | 99.99% |
| Accuracy | >99% (acceptable under high load) |
| Memory | O(active users) |

### Scale Estimates

```
Assumptions:
- 10M active users
- 100 requests/user/hour average
- Peak: 3x average = 300 requests/user/hour

Total requests: 10M * 100 = 1B requests/hour
                = 278K requests/sec average
                = 834K requests/sec peak
```

---

## 3. Rate Limiting Algorithms

### 3.1 Fixed Window

**How it works:**
- Divide time into fixed windows (e.g., 1 minute)
- Count requests in current window
- Reset counter at window boundary

**Pros:** Simple, low memory  
**Cons:** Burst at window boundaries (200 requests in 2 seconds across boundary)

```
Window: [12:00:00 - 12:01:00]
Limit: 100 requests/minute

12:00:00 ━━━━━━━━━━━━━━━━━━━━ 12:01:00 ━━━━━━━━━━━━━━━━━━━━ 12:02:00
         ▲ 60 requests      ▲ reset, 80 requests
         allowed             allowed
```

**Problem:** User can make 60 requests at 12:00:59 and 80 requests at 12:01:00 → 140 requests in 1 second!

---

### 3.2 Sliding Window Log

**How it works:**
- Store timestamp of each request
- Count requests in last N seconds
- Remove old timestamps

**Pros:** Accurate, no burst issues  
**Cons:** High memory (stores every request)

```
Current time: 12:01:30
Window: last 60 seconds
Limit: 100 requests/minute

Requests: [12:00:31, 12:00:35, 12:00:40, ..., 12:01:28]
          └─────────── 60 seconds ──────────┘
Count: 87 → Allow request
```

**Memory:** O(limit × active_users)

---

### 3.3 Sliding Window Counter

**How it works:**
- Hybrid of fixed window and sliding window log
- Use weighted count from previous window

**Formula:**
```
count = current_window_count + 
        previous_window_count × (1 - elapsed_time_in_current_window / window_size)
```

**Example:**
```
Previous window [12:00-12:01]: 80 requests
Current window [12:01-12:02]: 30 requests (so far)
Current time: 12:01:30 (50% into window)

Weighted count = 30 + 80 × (1 - 0.5) = 30 + 40 = 70
Limit: 100 → Allow request
```

**Pros:** Memory efficient, more accurate than fixed window  
**Cons:** Not 100% accurate

---

### 3.4 Token Bucket

**How it works:**
- Bucket holds tokens (capacity = rate limit)
- Tokens added at fixed rate (refill rate)
- Each request consumes 1 token
- Request allowed if bucket has tokens

**Example:**
```
Capacity: 100 tokens
Refill rate: 10 tokens/second

Initial: [████████████████████] 100 tokens
         ↓ consume 20 tokens
After:   [████████████░░░░░░░░] 80 tokens
         ↓ wait 5 seconds, refill 50 tokens
After:   [███████████████████░] 100 tokens (capped)
```

**Pros:** Allows bursts (up to capacity), smooth over time  
**Cons:** Complexity in implementation

**Best for:** APIs allowing occasional bursts (e.g., AWS API Gateway)

---

### 3.5 Leaky Bucket

**How it works:**
- Queue holds requests
- Requests processed at fixed rate (leak rate)
- Queue has maximum capacity

**Example:**
```
Capacity: 100 requests
Process rate: 10 requests/second

Queue: [R][R][R][R][R]... → Process → Backend
       ↑ new requests      ↓ 10/sec
```

**Pros:** Smooth, predictable rate  
**Cons:** Doesn't allow bursts, can cause latency

**Best for:** Background job processing, message queues

---

## 4. Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                        Load Balancer                         │
└──────────────────┬──────────────────────────────────────────┘
                   │
         ┌─────────┼─────────┐
         ▼         ▼         ▼
    ┌────────┐ ┌────────┐ ┌────────┐
    │ API    │ │ API    │ │ API    │
    │ Server │ │ Server │ │ Server │
    │   1    │ │   2    │ │   3    │
    └────┬───┘ └───┬────┘ └───┬────┘
         │         │          │
         └─────────┼──────────┘
                   ▼
         ┌──────────────────┐
         │  Redis Cluster   │
         │  (Rate Limiter)  │
         │                  │
         │  ┌────┬────┬────┐│
         │  │ M1 │ M2 │ M3 ││  Masters
         │  └─┬──┴─┬──┴─┬──┘│
         │    │    │    │   │
         │  ┌─┴──┬─┴──┬─┴──┐│
         │  │ S1 │ S2 │ S3 ││  Slaves
         │  └────┴────┴────┘│
         └──────────────────┘
                   │
         ┌─────────┼─────────┐
         ▼         ▼         ▼
    ┌────────┐ ┌────────┐ ┌────────┐
    │Backend │ │Backend │ │Backend │
    │Service │ │Service │ │Service │
    └────────┘ └────────┘ └────────┘
```

### Components

1. **API Servers:** Check rate limits before forwarding requests
2. **Redis Cluster:** Stores rate limit counters (distributed, fast)
3. **Rate Limiter Library:** Implements algorithms, used by API servers

### Why Redis?

| Feature | Redis | Database | Local Memory |
|---------|-------|----------|--------------|
| Speed | <1ms | 5-10ms | <0.1ms |
| Distributed | ✅ | ✅ | ❌ |
| Atomic operations | ✅ | ✅ | ⚠️ |
| Memory efficiency | ✅ | ❌ | ✅ |
| TTL support | ✅ | ⚠️ | ⚠️ |

**Verdict:** Redis is optimal for distributed rate limiting

---

## 5. Implementation

### 5.1 Token Bucket (Go)

```go
// ratelimiter/token_bucket.go
package ratelimiter

import (
    "context"
    "fmt"
    "time"
    
    "github.com/go-redis/redis/v8"
)

type TokenBucketLimiter struct {
    client *redis.Client
    capacity int64
    refillRate int64 // tokens per second
}

func NewTokenBucketLimiter(
    client *redis.Client,
    capacity int64,
    refillRate int64,
) *TokenBucketLimiter {
    return &TokenBucketLimiter{
        client: client,
        capacity: capacity,
        refillRate: refillRate,
    }
}

// Allow checks if request is allowed and consumes a token
func (tb *TokenBucketLimiter) Allow(ctx context.Context, key string) (bool, error) {
    now := time.Now().Unix()
    
    // Lua script for atomic token bucket operation
    script := `
        local key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        
        -- Get current state
        local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(bucket[1])
        local last_refill = tonumber(bucket[2])
        
        -- Initialize if not exists
        if tokens == nil then
            tokens = capacity
            last_refill = now
        end
        
        -- Refill tokens based on elapsed time
        local elapsed = now - last_refill
        local refill_tokens = elapsed * refill_rate
        tokens = math.min(capacity, tokens + refill_tokens)
        
        -- Check if request can be allowed
        if tokens >= 1 then
            tokens = tokens - 1
            redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
            redis.call('EXPIRE', key, 3600)  -- 1 hour TTL
            return 1  -- allowed
        else
            return 0  -- denied
        end
    `
    
    result, err := tb.client.Eval(ctx, script, []string{key},
        tb.capacity, tb.refillRate, now).Int()
    
    if err != nil {
        return false, fmt.Errorf("rate limiter error: %w", err)
    }
    
    return result == 1, nil
}

// GetState returns current tokens and refill time
func (tb *TokenBucketLimiter) GetState(ctx context.Context, key string) (int64, int64, error) {
    result, err := tb.client.HMGet(ctx, key, "tokens", "last_refill").Result()
    if err != nil {
        return 0, 0, err
    }
    
    tokens := int64(0)
    lastRefill := int64(0)
    
    if result[0] != nil {
        fmt.Sscanf(result[0].(string), "%d", &tokens)
    }
    if result[1] != nil {
        fmt.Sscanf(result[1].(string), "%d", &lastRefill)
    }
    
    return tokens, lastRefill, nil
}
```

### 5.2 Sliding Window Counter (Go)

```go
// ratelimiter/sliding_window.go
package ratelimiter

import (
    "context"
    "fmt"
    "time"
    
    "github.com/go-redis/redis/v8"
)

type SlidingWindowLimiter struct {
    client *redis.Client
    limit int64
    windowSize time.Duration
}

func NewSlidingWindowLimiter(
    client *redis.Client,
    limit int64,
    windowSize time.Duration,
) *SlidingWindowLimiter {
    return &SlidingWindowLimiter{
        client: client,
        limit: limit,
        windowSize: windowSize,
    }
}

func (sw *SlidingWindowLimiter) Allow(ctx context.Context, key string) (bool, error) {
    now := time.Now()
    currentWindow := now.Truncate(sw.windowSize).Unix()
    previousWindow := now.Add(-sw.windowSize).Truncate(sw.windowSize).Unix()
    
    script := `
        local current_key = KEYS[1]
        local previous_key = KEYS[2]
        local limit = tonumber(ARGV[1])
        local window_size = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        local current_window_start = tonumber(ARGV[4])
        
        -- Get counts
        local current_count = tonumber(redis.call('GET', current_key) or 0)
        local previous_count = tonumber(redis.call('GET', previous_key) or 0)
        
        -- Calculate elapsed percentage in current window
        local elapsed_pct = (now - current_window_start) / window_size
        
        -- Weighted count
        local weighted_count = current_count + previous_count * (1 - elapsed_pct)
        
        if weighted_count < limit then
            redis.call('INCR', current_key)
            redis.call('EXPIRE', current_key, window_size * 2)
            return 1
        else
            return 0
        end
    `
    
    currentKey := fmt.Sprintf("%s:%d", key, currentWindow)
    previousKey := fmt.Sprintf("%s:%d", key, previousWindow)
    
    result, err := sw.client.Eval(ctx, script,
        []string{currentKey, previousKey},
        sw.limit,
        int64(sw.windowSize.Seconds()),
        now.Unix(),
        currentWindow,
    ).Int()
    
    if err != nil {
        return false, fmt.Errorf("rate limiter error: %w", err)
    }
    
    return result == 1, nil
}
```

### 5.3 Sliding Window Log (Go)

```go
// ratelimiter/sliding_window_log.go
package ratelimiter

import (
    "context"
    "fmt"
    "time"
    
    "github.com/go-redis/redis/v8"
)

type SlidingWindowLogLimiter struct {
    client *redis.Client
    limit int64
    windowSize time.Duration
}

func NewSlidingWindowLogLimiter(
    client *redis.Client,
    limit int64,
    windowSize time.Duration,
) *SlidingWindowLogLimiter {
    return &SlidingWindowLogLimiter{
        client: client,
        limit: limit,
        windowSize: windowSize,
    }
}

func (swl *SlidingWindowLogLimiter) Allow(ctx context.Context, key string) (bool, error) {
    now := time.Now().UnixNano()
    windowStart := now - int64(swl.windowSize)
    
    // Use Redis Sorted Set (ZSET) to store timestamps
    script := `
        local key = KEYS[1]
        local limit = tonumber(ARGV[1])
        local window_start = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        
        -- Remove old entries
        redis.call('ZREMRANGEBYSCORE', key, 0, window_start)
        
        -- Count current entries
        local count = redis.call('ZCARD', key)
        
        if count < limit then
            redis.call('ZADD', key, now, now)
            redis.call('EXPIRE', key, 3600)
            return 1
        else
            return 0
        end
    `
    
    result, err := swl.client.Eval(ctx, script,
        []string{key},
        swl.limit,
        windowStart,
        now,
    ).Int()
    
    if err != nil {
        return false, fmt.Errorf("rate limiter error: %w", err)
    }
    
    return result == 1, nil
}
```

### 5.4 Fixed Window Counter (Go)

```go
// ratelimiter/fixed_window.go
package ratelimiter

import (
    "context"
    "fmt"
    "time"
    
    "github.com/go-redis/redis/v8"
)

type FixedWindowLimiter struct {
    client *redis.Client
    limit int64
    windowSize time.Duration
}

func NewFixedWindowLimiter(
    client *redis.Client,
    limit int64,
    windowSize time.Duration,
) *FixedWindowLimiter {
    return &FixedWindowLimiter{
        client: client,
        limit: limit,
        windowSize: windowSize,
    }
}

func (fw *FixedWindowLimiter) Allow(ctx context.Context, key string) (bool, error) {
    now := time.Now()
    window := now.Truncate(fw.windowSize).Unix()
    windowKey := fmt.Sprintf("%s:%d", key, window)
    
    // Atomic increment and check
    pipe := fw.client.Pipeline()
    incr := pipe.Incr(ctx, windowKey)
    pipe.Expire(ctx, windowKey, fw.windowSize)
    
    _, err := pipe.Exec(ctx)
    if err != nil {
        return false, fmt.Errorf("rate limiter error: %w", err)
    }
    
    count := incr.Val()
    return count <= fw.limit, nil
}

func (fw *FixedWindowLimiter) GetRemaining(ctx context.Context, key string) (int64, error) {
    now := time.Now()
    window := now.Truncate(fw.windowSize).Unix()
    windowKey := fmt.Sprintf("%s:%d", key, window)
    
    count, err := fw.client.Get(ctx, windowKey).Int64()
    if err == redis.Nil {
        return fw.limit, nil
    }
    if err != nil {
        return 0, err
    }
    
    remaining := fw.limit - count
    if remaining < 0 {
        remaining = 0
    }
    
    return remaining, nil
}
```

---

### 5.5 Middleware Integration

```go
// middleware/ratelimit.go
package middleware

import (
    "fmt"
    "net/http"
    "time"
    
    "myapp/ratelimiter"
)

type RateLimitMiddleware struct {
    limiter RateLimiter
}

type RateLimiter interface {
    Allow(ctx context.Context, key string) (bool, error)
}

func NewRateLimitMiddleware(limiter RateLimiter) *RateLimitMiddleware {
    return &RateLimitMiddleware{limiter: limiter}
}

func (rlm *RateLimitMiddleware) Handler(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Extract identifier (user ID, API key, IP, etc.)
        identifier := getIdentifier(r)
        
        // Check rate limit
        allowed, err := rlm.limiter.Allow(r.Context(), identifier)
        if err != nil {
            http.Error(w, "Rate limiter unavailable", http.StatusInternalServerError)
            return
        }
        
        if !allowed {
            // Rate limit exceeded
            w.Header().Set("X-RateLimit-Limit", "1000")
            w.Header().Set("X-RateLimit-Remaining", "0")
            w.Header().Set("X-RateLimit-Reset", fmt.Sprintf("%d", time.Now().Add(time.Hour).Unix()))
            w.Header().Set("Retry-After", "3600")
            
            http.Error(w, "Rate limit exceeded", http.StatusTooManyRequests)
            return
        }
        
        // Add rate limit headers
        w.Header().Set("X-RateLimit-Limit", "1000")
        // Note: Getting remaining count requires additional Redis call
        // In production, return approximate value or skip for performance
        
        next.ServeHTTP(w, r)
    })
}

func getIdentifier(r *http.Request) string {
    // Priority: API key > User ID > IP address
    
    // 1. Check API key header
    apiKey := r.Header.Get("X-API-Key")
    if apiKey != "" {
        return fmt.Sprintf("api_key:%s", apiKey)
    }
    
    // 2. Check authenticated user
    userID := r.Context().Value("user_id")
    if userID != nil {
        return fmt.Sprintf("user:%v", userID)
    }
    
    // 3. Fallback to IP address
    ip := r.Header.Get("X-Forwarded-For")
    if ip == "" {
        ip = r.RemoteAddr
    }
    return fmt.Sprintf("ip:%s", ip)
}
```

---

### 5.6 Configuration-Driven Rate Limiting

```go
// config/ratelimit_config.go
package config

import (
    "time"
)

type RateLimitRule struct {
    Endpoint string
    Method string
    Limit int64
    Window time.Duration
    Algorithm string // "token_bucket", "sliding_window", etc.
}

type RateLimitConfig struct {
    Rules []RateLimitRule
    DefaultLimit int64
    DefaultWindow time.Duration
}

var DefaultConfig = RateLimitConfig{
    DefaultLimit: 1000,
    DefaultWindow: time.Hour,
    Rules: []RateLimitRule{
        {
            Endpoint: "/api/auth/login",
            Method: "POST",
            Limit: 5,
            Window: time.Minute,
            Algorithm: "fixed_window",
        },
        {
            Endpoint: "/api/search",
            Method: "GET",
            Limit: 100,
            Window: time.Minute,
            Algorithm: "sliding_window",
        },
        {
            Endpoint: "/api/upload",
            Method: "POST",
            Limit: 10,
            Window: time.Hour,
            Algorithm: "token_bucket",
        },
    },
}

func GetRuleForEndpoint(endpoint, method string) *RateLimitRule {
    for _, rule := range DefaultConfig.Rules {
        if rule.Endpoint == endpoint && rule.Method == method {
            return &rule
        }
    }
    
    // Return default rule
    return &RateLimitRule{
        Endpoint: endpoint,
        Method: method,
        Limit: DefaultConfig.DefaultLimit,
        Window: DefaultConfig.DefaultWindow,
        Algorithm: "sliding_window",
    }
}
```

---

### 5.7 Advanced: Tiered Rate Limiting

```go
// ratelimiter/tiered_limiter.go
package ratelimiter

import (
    "context"
    "fmt"
)

type Tier struct {
    Name string
    Limit int64
    Window time.Duration
}

type TieredLimiter struct {
    tiers map[string]Tier
    limiter RateLimiter
}

func NewTieredLimiter(limiter RateLimiter) *TieredLimiter {
    return &TieredLimiter{
        limiter: limiter,
        tiers: map[string]Tier{
            "free": {
                Name: "free",
                Limit: 100,
                Window: time.Hour,
            },
            "basic": {
                Name: "basic",
                Limit: 1000,
                Window: time.Hour,
            },
            "premium": {
                Name: "premium",
                Limit: 10000,
                Window: time.Hour,
            },
            "enterprise": {
                Name: "enterprise",
                Limit: 100000,
                Window: time.Hour,
            },
        },
    }
}

func (tl *TieredLimiter) Allow(ctx context.Context, userID string, tierName string) (bool, error) {
    tier, exists := tl.tiers[tierName]
    if !exists {
        tier = tl.tiers["free"] // default to free tier
    }
    
    key := fmt.Sprintf("tier:%s:user:%s", tierName, userID)
    return tl.limiter.Allow(ctx, key)
}
```

---

**Continued in next part...**
