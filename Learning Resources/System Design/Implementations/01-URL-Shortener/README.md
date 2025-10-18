# URL Shortener - Complete Production Implementation

**Target Role:** Principal Engineer / Staff Engineer (40+ LPA)  
**Companies:** bit.ly, TinyURL, Twitter (t.co), Google (goo.gl)  
**Scale:** 100M URLs, 10K writes/sec, 100K reads/sec  

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Requirements & Scale](#2-requirements--scale)
3. [Architecture Design](#3-architecture-design)
4. [Data Model](#4-data-model)
5. [Core Implementation](#5-core-implementation)
6. [Deployment](#6-deployment)
7. [Performance & Optimization](#7-performance--optimization)
8. [Monitoring & Operations](#8-monitoring--operations)

---

## 1. Problem Statement

### Functional Requirements

✅ Given a long URL, generate a short URL  
✅ Given a short URL, redirect to original URL  
✅ Custom aliases (optional)  
✅ Expiration time (optional)  
✅ Analytics (click tracking)  

### Non-Functional Requirements

✅ **High Availability:** 99.9% uptime  
✅ **Low Latency:** <10ms p99 for redirects  
✅ **Scalability:** Handle millions of URLs  
✅ **Durability:** No data loss  

### Out of Scope

❌ URL validation (assume valid)  
❌ User authentication  
❌ Rate limiting (covered separately)  

---

## 2. Requirements & Scale

### Traffic Estimates

```
Assumptions:
- 100M new URLs per month
- 10:1 read/write ratio

Writes:
- 100M URLs / month = 100M / (30 * 24 * 3600) ≈ 40 writes/sec
- Peak: 40 * 10 = 400 writes/sec

Reads:
- 40 * 10 = 400 reads/sec
- Peak: 400 * 10 = 4,000 reads/sec
```

### Storage Estimates

```
Per URL:
- Short code: 7 bytes (base62)
- Long URL: 500 bytes (average)
- Metadata: 100 bytes
- Total: ~600 bytes

Total storage (5 years):
- 100M URLs/month * 12 * 5 = 6B URLs
- 6B * 600 bytes = 3.6 TB
```

### Cache Requirements

```
Cache top 20% hot URLs:
- 6B * 0.2 = 1.2B URLs
- 1.2B * 600 bytes = 720 GB

Redis cluster: 10 nodes * 100 GB = 1 TB capacity
```

---

## 3. Architecture Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer                        │
│                   (AWS ALB / Nginx)                     │
└────────────┬────────────────────────────┬───────────────┘
             │                            │
             ▼                            ▼
┌──────────────────────┐      ┌──────────────────────┐
│   Write Service      │      │   Read Service       │
│   (Create short URL) │      │   (Redirect)         │
│                      │      │                      │
│   - Generate code    │      │   - Cache lookup     │
│   - Store in DB      │      │   - DB fallback      │
│   - Update cache     │      │   - Track analytics  │
└──────────┬───────────┘      └──────────┬───────────┘
           │                             │
           ▼                             ▼
┌─────────────────────────────────────────────────────────┐
│                    Redis Cache Cluster                  │
│     (Hot URLs, 720 GB, LRU eviction)                   │
└─────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│              PostgreSQL Primary/Replica                  │
│  Primary: Writes                                         │
│  Replicas (3x): Reads                                    │
│  Sharding: By hash(short_code) % num_shards             │
└─────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│                  Analytics Pipeline                      │
│  Kafka → Flink → ClickHouse                             │
│  (Real-time click tracking)                             │
└─────────────────────────────────────────────────────────┘
```

### Components

1. **Load Balancer:** Route traffic, SSL termination
2. **API Servers:** Stateless, horizontally scalable
3. **Redis:** Cache hot URLs, reduce DB load
4. **PostgreSQL:** Persistent storage, sharded
5. **ID Generator:** Distributed unique IDs (Snowflake)
6. **Analytics:** Real-time click tracking

---

## 4. Data Model

### Database Schema

```sql
-- urls table (sharded by short_code)
CREATE TABLE urls (
    id BIGSERIAL PRIMARY KEY,
    short_code VARCHAR(10) UNIQUE NOT NULL,
    long_url TEXT NOT NULL,
    user_id BIGINT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP,
    click_count BIGINT DEFAULT 0,
    INDEX idx_short_code (short_code),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- clicks table (for analytics)
CREATE TABLE clicks (
    id BIGSERIAL PRIMARY KEY,
    short_code VARCHAR(10) NOT NULL,
    clicked_at TIMESTAMP NOT NULL DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,
    referer TEXT,
    country VARCHAR(2),
    INDEX idx_short_code_time (short_code, clicked_at),
    INDEX idx_clicked_at (clicked_at)
) PARTITION BY RANGE (clicked_at);

-- Partitioning for clicks table
CREATE TABLE clicks_2024_01 PARTITION OF clicks
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE clicks_2024_02 PARTITION OF clicks
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
-- ... more partitions
```

### Sharding Strategy

```
Sharding Key: hash(short_code) % num_shards

Example with 4 shards:
- short_code "abc123" → hash → shard 0
- short_code "xyz789" → hash → shard 2

Benefits:
- Even distribution
- No hot shards
- Easy to add shards

Drawback:
- Range queries span all shards
```

---

## 5. Core Implementation

### Project Structure

```
url-shortener/
├── api/                    # REST API
│   ├── main.go
│   ├── handlers.go
│   └── middleware.go
├── service/                # Business logic
│   ├── shortener.go
│   ├── redirector.go
│   └── analytics.go
├── storage/                # Data access
│   ├── postgres.go
│   ├── redis.go
│   └── sharding.go
├── idgen/                  # ID generation
│   └── snowflake.go
├── config/                 # Configuration
│   └── config.go
└── docker-compose.yml      # Local setup
```

### ID Generation (Snowflake Algorithm)

```go
// idgen/snowflake.go
package idgen

import (
    "errors"
    "sync"
    "time"
)

/*
Snowflake ID structure (64 bits):
- 41 bits: Timestamp (milliseconds since epoch)
- 10 bits: Machine ID (supports 1024 machines)
- 12 bits: Sequence number (4096 IDs per ms per machine)

Total: 4096 * 1024 = 4.2M IDs per millisecond
*/

const (
    epoch           = int64(1609459200000) // 2021-01-01 00:00:00 UTC
    machineIDBits   = 10
    sequenceBits    = 12
    machineIDShift  = sequenceBits
    timestampShift  = sequenceBits + machineIDBits
    sequenceMask    = int64(-1) ^ (int64(-1) << sequenceBits)
)

type SnowflakeGenerator struct {
    mu             sync.Mutex
    machineID      int64
    sequence       int64
    lastTimestamp  int64
}

func NewSnowflakeGenerator(machineID int64) (*SnowflakeGenerator, error) {
    if machineID < 0 || machineID >= (1<<machineIDBits) {
        return nil, errors.New("machine ID out of range")
    }
    
    return &SnowflakeGenerator{
        machineID: machineID,
        sequence:  0,
        lastTimestamp: 0,
    }, nil
}

func (s *SnowflakeGenerator) NextID() (int64, error) {
    s.mu.Lock()
    defer s.mu.Unlock()
    
    timestamp := time.Now().UnixMilli()
    
    if timestamp < s.lastTimestamp {
        return 0, errors.New("clock moved backwards")
    }
    
    if timestamp == s.lastTimestamp {
        // Same millisecond, increment sequence
        s.sequence = (s.sequence + 1) & sequenceMask
        
        if s.sequence == 0 {
            // Sequence overflow, wait for next millisecond
            timestamp = s.waitNextMillis(s.lastTimestamp)
        }
    } else {
        // New millisecond, reset sequence
        s.sequence = 0
    }
    
    s.lastTimestamp = timestamp
    
    // Construct ID
    id := ((timestamp - epoch) << timestampShift) |
          (s.machineID << machineIDShift) |
          s.sequence
    
    return id, nil
}

func (s *SnowflakeGenerator) waitNextMillis(lastTimestamp int64) int64 {
    timestamp := time.Now().UnixMilli()
    for timestamp <= lastTimestamp {
        time.Sleep(100 * time.Microsecond)
        timestamp = time.Now().UnixMilli()
    }
    return timestamp
}
```

### Base62 Encoding

```go
// service/encoder.go
package service

const base62Chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

// Encode converts a number to base62 string
func EncodeBase62(num int64) string {
    if num == 0 {
        return string(base62Chars[0])
    }
    
    result := make([]byte, 0, 11) // Max 11 chars for int64
    base := int64(62)
    
    for num > 0 {
        remainder := num % base
        result = append(result, base62Chars[remainder])
        num = num / base
    }
    
    // Reverse
    for i, j := 0, len(result)-1; i < j; i, j = i+1, j-1 {
        result[i], result[j] = result[j], result[i]
    }
    
    return string(result)
}

// Decode converts base62 string to number
func DecodeBase62(str string) int64 {
    result := int64(0)
    base := int64(62)
    
    for _, char := range str {
        result = result * base
        
        if char >= '0' && char <= '9' {
            result += int64(char - '0')
        } else if char >= 'a' && char <= 'z' {
            result += int64(char - 'a' + 10)
        } else if char >= 'A' && char <= 'Z' {
            result += int64(char - 'A' + 36)
        }
    }
    
    return result
}
```

### Shortener Service

```go
// service/shortener.go
package service

import (
    "context"
    "errors"
    "time"
    "url-shortener/idgen"
    "url-shortener/storage"
)

type ShortenerService struct {
    idGen   *idgen.SnowflakeGenerator
    storage *storage.Storage
}

func NewShortenerService(
    idGen *idgen.SnowflakeGenerator,
    storage *storage.Storage,
) *ShortenerService {
    return &ShortenerService{
        idGen:   idGen,
        storage: storage,
    }
}

type ShortenRequest struct {
    LongURL    string
    CustomCode string        // Optional custom alias
    ExpiresAt  *time.Time    // Optional expiration
    UserID     int64
}

type ShortenResponse struct {
    ShortCode string
    ShortURL  string
    LongURL   string
    CreatedAt time.Time
}

func (s *ShortenerService) Shorten(
    ctx context.Context,
    req ShortenRequest,
) (*ShortenResponse, error) {
    // Validate long URL
    if len(req.LongURL) == 0 {
        return nil, errors.New("long URL is required")
    }
    
    if len(req.LongURL) > 2048 {
        return nil, errors.New("long URL too long")
    }
    
    var shortCode string
    
    if req.CustomCode != "" {
        // Use custom code
        if !isValidCustomCode(req.CustomCode) {
            return nil, errors.New("invalid custom code")
        }
        
        // Check if custom code already exists
        exists, err := s.storage.ExistsShortCode(ctx, req.CustomCode)
        if err != nil {
            return nil, err
        }
        if exists {
            return nil, errors.New("custom code already taken")
        }
        
        shortCode = req.CustomCode
    } else {
        // Generate short code
        id, err := s.idGen.NextID()
        if err != nil {
            return nil, err
        }
        
        shortCode = EncodeBase62(id)
    }
    
    // Store in database
    url := &storage.URL{
        ShortCode: shortCode,
        LongURL:   req.LongURL,
        UserID:    req.UserID,
        CreatedAt: time.Now(),
        ExpiresAt: req.ExpiresAt,
    }
    
    if err := s.storage.CreateURL(ctx, url); err != nil {
        return nil, err
    }
    
    // Cache in Redis
    if err := s.storage.CacheURL(ctx, url); err != nil {
        // Log error but don't fail the request
        // Cache is not critical
    }
    
    return &ShortenResponse{
        ShortCode: shortCode,
        ShortURL:  "https://short.ly/" + shortCode,
        LongURL:   req.LongURL,
        CreatedAt: url.CreatedAt,
    }, nil
}

func isValidCustomCode(code string) bool {
    if len(code) < 3 || len(code) > 20 {
        return false
    }
    
    for _, char := range code {
        if !((char >= '0' && char <= '9') ||
             (char >= 'a' && char <= 'z') ||
             (char >= 'A' && char <= 'Z') ||
             char == '-' || char == '_') {
            return false
        }
    }
    
    return true
}
```

### Redirector Service

```go
// service/redirector.go
package service

import (
    "context"
    "errors"
    "time"
    "url-shortener/storage"
)

type RedirectorService struct {
    storage *storage.Storage
}

func NewRedirectorService(storage *storage.Storage) *RedirectorService {
    return &RedirectorService{storage: storage}
}

func (r *RedirectorService) GetLongURL(
    ctx context.Context,
    shortCode string,
) (string, error) {
    // Try cache first
    url, err := r.storage.GetURLFromCache(ctx, shortCode)
    if err == nil && url != nil {
        // Check expiration
        if url.ExpiresAt != nil && url.ExpiresAt.Before(time.Now()) {
            return "", errors.New("URL expired")
        }
        
        // Track click asynchronously
        go r.trackClick(shortCode)
        
        return url.LongURL, nil
    }
    
    // Cache miss, query database
    url, err = r.storage.GetURLFromDB(ctx, shortCode)
    if err != nil {
        return "", err
    }
    
    if url == nil {
        return "", errors.New("URL not found")
    }
    
    // Check expiration
    if url.ExpiresAt != nil && url.ExpiresAt.Before(time.Now()) {
        return "", errors.New("URL expired")
    }
    
    // Update cache
    go r.storage.CacheURL(ctx, url)
    
    // Track click
    go r.trackClick(shortCode)
    
    return url.LongURL, nil
}

func (r *RedirectorService) trackClick(shortCode string) {
    // Send to analytics pipeline (Kafka)
    // Implementation in analytics.go
}
```

### Storage Layer

```go
// storage/postgres.go
package storage

import (
    "context"
    "database/sql"
    "errors"
    "time"
    
    _ "github.com/lib/pq"
)

type URL struct {
    ID         int64
    ShortCode  string
    LongURL    string
    UserID     int64
    CreatedAt  time.Time
    ExpiresAt  *time.Time
    ClickCount int64
}

type Storage struct {
    db    *sql.DB
    cache *RedisCache
}

func NewStorage(db *sql.DB, cache *RedisCache) *Storage {
    return &Storage{
        db:    db,
        cache: cache,
    }
}

func (s *Storage) CreateURL(ctx context.Context, url *URL) error {
    query := `
        INSERT INTO urls (short_code, long_url, user_id, created_at, expires_at)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (short_code) DO NOTHING
        RETURNING id
    `
    
    err := s.db.QueryRowContext(
        ctx,
        query,
        url.ShortCode,
        url.LongURL,
        url.UserID,
        url.CreatedAt,
        url.ExpiresAt,
    ).Scan(&url.ID)
    
    if err != nil {
        if err == sql.ErrNoRows {
            return errors.New("short code already exists")
        }
        return err
    }
    
    return nil
}

func (s *Storage) GetURLFromDB(ctx context.Context, shortCode string) (*URL, error) {
    query := `
        SELECT id, short_code, long_url, user_id, created_at, expires_at, click_count
        FROM urls
        WHERE short_code = $1
    `
    
    url := &URL{}
    err := s.db.QueryRowContext(ctx, query, shortCode).Scan(
        &url.ID,
        &url.ShortCode,
        &url.LongURL,
        &url.UserID,
        &url.CreatedAt,
        &url.ExpiresAt,
        &url.ClickCount,
    )
    
    if err != nil {
        if err == sql.ErrNoRows {
            return nil, nil
        }
        return nil, err
    }
    
    return url, nil
}

func (s *Storage) ExistsShortCode(ctx context.Context, shortCode string) (bool, error) {
    query := `SELECT EXISTS(SELECT 1 FROM urls WHERE short_code = $1)`
    
    var exists bool
    err := s.db.QueryRowContext(ctx, query, shortCode).Scan(&exists)
    if err != nil {
        return false, err
    }
    
    return exists, nil
}

func (s *Storage) IncrementClickCount(ctx context.Context, shortCode string) error {
    query := `
        UPDATE urls
        SET click_count = click_count + 1
        WHERE short_code = $1
    `
    
    _, err := s.db.ExecContext(ctx, query, shortCode)
    return err
}
```

---

### Redis Caching

```go
// storage/redis.go
package storage

import (
    "context"
    "encoding/json"
    "fmt"
    "time"
    
    "github.com/go-redis/redis/v8"
)

type RedisCache struct {
    client *redis.Client
    ttl    time.Duration
}

func NewRedisCache(addr string, ttl time.Duration) *RedisCache {
    client := redis.NewClient(&redis.Options{
        Addr:         addr,
        PoolSize:     100,
        MinIdleConns: 10,
    })
    
    return &RedisCache{
        client: client,
        ttl:    ttl,
    }
}

func (r *RedisCache) Set(ctx context.Context, shortCode string, url *URL) error {
    key := fmt.Sprintf("url:%s", shortCode)
    
    data, err := json.Marshal(url)
    if err != nil {
        return err
    }
    
    return r.client.Set(ctx, key, data, r.ttl).Err()
}

func (r *RedisCache) Get(ctx context.Context, shortCode string) (*URL, error) {
    key := fmt.Sprintf("url:%s", shortCode)
    
    data, err := r.client.Get(ctx, key).Result()
    if err != nil {
        if err == redis.Nil {
            return nil, nil // Cache miss
        }
        return nil, err
    }
    
    url := &URL{}
    if err := json.Unmarshal([]byte(data), url); err != nil {
        return nil, err
    }
    
    return url, nil
}

func (s *Storage) CacheURL(ctx context.Context, url *URL) error {
    return s.cache.Set(ctx, url.ShortCode, url)
}

func (s *Storage) GetURLFromCache(ctx context.Context, shortCode string) (*URL, error) {
    return s.cache.Get(ctx, shortCode)
}
```

---

**Continuing in next file due to length...**

This is Part 1 of the URL Shortener implementation (~2,000 lines). Part 2 will cover:
- REST API handlers
- Docker/Kubernetes deployment
- Performance testing & optimization
- Monitoring & alerting
- Analytics pipeline

Total expected: ~10,000 lines for complete URL Shortener implementation.
