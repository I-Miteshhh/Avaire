# Design YouTube Analytics Platform

**Difficulty:** ⭐⭐⭐⭐⭐ (Very Hard)  
**Time:** 60 minutes  
**Companies:** Google, Amazon, Netflix, Meta

---

## 📋 Problem Statement

Design a real-time analytics platform for YouTube that tracks:
- Video views (billions/day)
- Watch time per video
- User engagement metrics (likes, comments, shares)
- Real-time trending videos
- Creator analytics dashboard

**Scale:**
- 2 billion users
- 500 hours of video uploaded every minute
- 1 billion video views per day
- Real-time dashboards for 50 million creators

---

## Step 1: Requirements Clarification

### Functional Requirements

**Core Features:**
1. Track video views in real-time
2. Aggregate metrics (views, watch time, likes, comments)
3. Trending videos (last 1 hour, 24 hours, 7 days)
4. Creator analytics dashboard
5. Geographic breakdowns
6. Device/platform analytics

**Out of Scope (clarify with interviewer):**
- Video recommendation algorithm
- Ad analytics
- Content moderation
- Video upload/processing

### Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| **Scale** | 1B views/day, 50M creators |
| **Latency** | <100ms for dashboard queries |
| **Freshness** | <1 min for trending, <5 min for creator dashboard |
| **Availability** | 99.99% uptime |
| **Consistency** | Eventual consistency OK for counts |
| **Data Retention** | 2 years historical data |

---

## Step 2: Capacity Estimation

### Traffic Estimation

```python
# Video Views
daily_views = 1_000_000_000  # 1 billion
views_per_second = daily_views / 86400
# = 11,574 views/sec

peak_views_per_second = views_per_second * 3
# = 34,722 views/sec

# Engagement Events (likes, comments, shares)
# Assume 10% engagement rate
engagement_per_second = views_per_second * 0.1
# = 1,157 events/sec

# Creator Dashboard Queries
creators = 50_000_000
queries_per_creator_per_day = 10
dashboard_qps = (creators * queries_per_creator_per_day) / 86400
# = 5,787 QPS

# Total Write QPS
total_write_qps = views_per_second + engagement_per_second
# = 12,731 QPS

# Total Read QPS  
total_read_qps = dashboard_qps + views_per_second  # real-time updates
# = 17,361 QPS
```

### Storage Estimation

```python
# View Event Storage
view_event_size = 200 bytes  # video_id, user_id, timestamp, device, location, etc.
daily_view_storage = daily_views * view_event_size
# = 200 GB/day
# = 73 TB/year
# = 146 TB for 2 years (raw)

# With compression (3x)
compressed_storage = 146 / 3
# = 48.6 TB

# Aggregated Metrics (per video per day)
total_videos = 800_000_000  # approximate active videos
metric_size = 100 bytes  # views, likes, watch_time, etc.
daily_aggregate_storage = total_videos * metric_size
# = 80 GB/day

# Total Storage (2 years)
# Raw events: 48.6 TB
# Aggregates: 58.4 TB
# Total: ~100 TB

# With replication (3x)
total_with_replication = 100 * 3
# = 300 TB
```

### Memory (Cache) Estimation

```python
# Trending videos cache (hot data)
trending_videos = 10_000
trending_data_per_video = 500 bytes
trending_cache = trending_videos * trending_data_per_video
# = 5 MB

# Popular videos (20% get 80% views)
popular_videos = total_videos * 0.2
popular_cache = popular_videos * 500
# = 80 GB

# Creator dashboard cache (active creators)
active_creators = creators * 0.1  # 10% active daily
cache_per_creator = 10_000 bytes  # dashboard data
creator_cache = active_creators * cache_per_creator
# = 50 GB

# Total cache memory
total_cache = 80 + 50
# = 130 GB (use 200 GB for safety)
```

### Bandwidth Estimation

```python
# Incoming (writes)
write_bandwidth = total_write_qps * view_event_size
# = 12,731 * 200 bytes
# = 2.5 MB/sec

# Outgoing (reads)
avg_response_size = 1000 bytes  # dashboard data
read_bandwidth = total_read_qps * avg_response_size
# = 17,361 * 1000
# = 17.4 MB/sec
```

---

## Step 3: API Design

### REST API

```http
# 1. Track View Event
POST /api/v1/analytics/view
Content-Type: application/json

Request:
{
  "video_id": "dQw4w9WgXcQ",
  "user_id": "user_123",
  "session_id": "sess_456",
  "timestamp": 1697368200,
  "watch_time_seconds": 45,
  "device": "mobile",
  "platform": "android",
  "location": {
    "country": "US",
    "region": "CA"
  }
}

Response: 202 Accepted


# 2. Get Video Analytics
GET /api/v1/analytics/video/{video_id}?timeRange=24h
Response:
{
  "video_id": "dQw4w9WgXcQ",
  "metrics": {
    "views": 1234567,
    "unique_viewers": 987654,
    "watch_time_hours": 5000,
    "likes": 50000,
    "comments": 2000,
    "shares": 3000
  },
  "demographics": {
    "age_groups": {
      "18-24": 0.35,
      "25-34": 0.40,
      "35-44": 0.15
    },
    "countries": {
      "US": 0.40,
      "IN": 0.20,
      "UK": 0.10
    }
  },
  "devices": {
    "mobile": 0.70,
    "desktop": 0.25,
    "tv": 0.05
  }
}


# 3. Get Trending Videos
GET /api/v1/analytics/trending?region=global&timeRange=1h&limit=50
Response:
{
  "trending": [
    {
      "rank": 1,
      "video_id": "dQw4w9WgXcQ",
      "title": "...",
      "views_last_hour": 150000,
      "growth_rate": 2.5
    },
    ...
  ],
  "updated_at": 1697368200
}


# 4. Creator Dashboard
GET /api/v1/analytics/creator/{creator_id}?period=7d
Response:
{
  "creator_id": "creator_123",
  "period": "7d",
  "total_views": 5000000,
  "subscribers_gained": 10000,
  "revenue": {
    "total": 15000.50,
    "by_source": {
      "ads": 12000.00,
      "memberships": 3000.50
    }
  },
  "top_videos": [
    {
      "video_id": "...",
      "views": 500000,
      "watch_time_hours": 10000
    }
  ],
  "metrics_over_time": [
    {
      "date": "2025-10-08",
      "views": 700000,
      "watch_time": 15000
    },
    ...
  ]
}
```

---

## Step 4: Database Schema

### Event Stream (Kafka Topics)

```javascript
// Topic: video_view_events
{
  "video_id": "dQw4w9WgXcQ",
  "user_id": "user_123",
  "timestamp": 1697368200,
  "watch_time_seconds": 45,
  "device": "mobile",
  "platform": "android",
  "country": "US",
  "region": "CA"
}

// Topic: engagement_events
{
  "event_type": "like",  // like, comment, share
  "video_id": "dQw4w9WgXcQ",
  "user_id": "user_123",
  "timestamp": 1697368200
}
```

### OLAP Database (ClickHouse)

```sql
-- Raw events table (fact table)
CREATE TABLE video_views (
    video_id String,
    user_id String,
    timestamp DateTime,
    watch_time_seconds UInt32,
    device Enum8('mobile'=1, 'desktop'=2, 'tv'=3),
    platform String,
    country FixedString(2),
    region String,
    date Date DEFAULT toDate(timestamp)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (video_id, timestamp)
TTL date + INTERVAL 2 YEAR;

-- Materialized view for video metrics (pre-aggregated)
CREATE MATERIALIZED VIEW video_metrics_mv
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (video_id, date)
AS SELECT
    video_id,
    toDate(timestamp) as date,
    count() as views,
    uniq(user_id) as unique_viewers,
    sum(watch_time_seconds) as total_watch_time_seconds
FROM video_views
GROUP BY video_id, date;

-- Real-time trending (last 1 hour)
CREATE MATERIALIZED VIEW trending_1h_mv
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMMDD(timestamp)
ORDER BY (timestamp)
TTL timestamp + INTERVAL 2 HOUR
AS SELECT
    video_id,
    toStartOfHour(timestamp) as hour,
    countState() as views,
    maxState(timestamp) as last_view
FROM video_views
WHERE timestamp > now() - INTERVAL 1 HOUR
GROUP BY video_id, hour;
```

### Cache Layer (Redis)

```redis
# Video metrics cache (hash)
HSET video:dQw4w9WgXcQ:metrics:24h
  views 1234567
  unique_viewers 987654
  watch_time 5000
  likes 50000
EXPIRE video:dQw4w9WgXcQ:metrics:24h 300  # 5 min TTL

# Trending videos (sorted set by views)
ZADD trending:global:1h 150000 "dQw4w9WgXcQ"
ZADD trending:global:1h 120000 "video_2"
EXPIRE trending:global:1h 60  # 1 min TTL

# Creator dashboard cache
SET creator:123:dashboard:7d "{...json data...}" EX 300
```

---

## Step 5: High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                    VIDEO PLAYERS (Clients)                       │
│        (Web, Mobile Apps, Smart TVs, Embedded Players)           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ View events, engagement events
                             ▼
                 ┌───────────────────────┐
                 │   API Gateway / LB    │
                 │    (AWS ALB/nginx)    │
                 └───────────┬───────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │Analytics │      │Analytics │      │Analytics │
    │ Ingestion│      │ Ingestion│      │ Ingestion│
    │ Service  │      │ Service  │      │ Service  │
    └─────┬────┘      └─────┬────┘      └─────┬────┘
          │                 │                  │
          └─────────────────┼──────────────────┘
                            │
                            ▼
              ┌──────────────────────────┐
              │     Kafka Cluster        │
              │  (video_view_events,     │
              │   engagement_events)     │
              └──────┬──────────┬────────┘
                     │          │
        ┌────────────┘          └──────────────┐
        │                                      │
        ▼                                      ▼
┌───────────────┐                    ┌─────────────────┐
│ Stream        │                    │ Batch           │
│ Processing    │                    │ Processing      │
│ (Flink/Spark) │                    │ (Spark)         │
│               │                    │                 │
│ • Real-time   │                    │ • Daily rollups │
│   aggregation │                    │ • Historical    │
│ • Trending    │                    │   analytics     │
│ • Alerts      │                    │ • ML features   │
└───────┬───────┘                    └────────┬────────┘
        │                                     │
        │                                     │
        ▼                                     ▼
┌──────────────────────────────────────────────────────┐
│              ClickHouse Cluster                      │
│  (Distributed OLAP for time-series analytics)        │
│                                                      │
│  Shard 1    Shard 2    Shard 3    Shard 4          │
│  (Replica)  (Replica)  (Replica)  (Replica)        │
└──────────────────────┬───────────────────────────────┘
                       │
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │  Redis   │  │Analytics │  │  CDN     │
  │ Cluster  │  │   API    │  │ (cached  │
  │ (Cache)  │  │ Servers  │  │ queries) │
  └──────────┘  └─────┬────┘  └──────────┘
                      │
                      ▼
              ┌───────────────┐
              │   Creators    │
              │  Dashboard    │
              │   (React)     │
              └───────────────┘
```

---

## Step 6: Detailed Design

### 6.1 Ingestion Pipeline

**Analytics Ingestion Service (Python/Go):**
```python
from kafka import KafkaProducer
import json

class AnalyticsIngestion:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['kafka1:9092', 'kafka2:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            compression_type='snappy',  # Reduce bandwidth
            linger_ms=10,  # Batch for 10ms
            batch_size=16384  # 16KB batches
        )
    
    def track_view(self, event: dict):
        """
        Handle incoming view event
        """
        # Validate event
        if not self._validate_event(event):
            return {"error": "Invalid event"}, 400
        
        # Enrich event
        enriched_event = self._enrich_event(event)
        
        # Send to Kafka (async)
        future = self.producer.send(
            'video_view_events',
            key=event['video_id'].encode('utf-8'),  # Partition by video_id
            value=enriched_event
        )
        
        # Fire and forget (low latency)
        return {"status": "accepted"}, 202
    
    def _enrich_event(self, event: dict) -> dict:
        """
        Add derived fields
        """
        event['timestamp'] = int(time.time())
        event['date'] = datetime.now().strftime('%Y-%m-%d')
        
        # Geo-lookup (from IP)
        if 'ip_address' in event:
            geo = geoip_lookup(event['ip_address'])
            event['country'] = geo['country']
            event['region'] = geo['region']
        
        return event
```

**Why Kafka?**
- High throughput (millions of events/sec)
- Durable (replication)
- Decouples ingestion from processing
- Exactly-once semantics
- Replay capability for backfill

**Kafka Configuration:**
```properties
# Topic: video_view_events
partitions = 100  # Parallel processing
replication.factor = 3
retention.hours = 48  # 2 days
compression.type = snappy

# Consumer groups
- real_time_aggregation (Flink)
- batch_processing (Spark)
- ml_feature_extraction (Spark)
```

### 6.2 Real-Time Aggregation (Apache Flink)

**Flink Job for Trending Videos:**
```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

// Kafka source
FlinkKafkaConsumer<ViewEvent> source = new FlinkKafkaConsumer<>(
    "video_view_events",
    new ViewEventSchema(),
    kafkaProps
);

DataStream<ViewEvent> events = env.addSource(source);

// Windowed aggregation (1-hour tumbling window)
DataStream<TrendingVideo> trending = events
    .keyBy(event -> event.getVideoId())
    .window(TumblingEventTimeWindows.of(Time.hours(1)))
    .aggregate(new ViewCountAggregator())
    .process(new RankByViews(50));  // Top 50

// Sink to Redis (trending cache)
trending.addSink(new RedisSink<>());

env.execute("Trending Videos - 1 Hour");
```

**Per-Minute Aggregation:**
```java
// For near real-time dashboard updates
DataStream<VideoMetrics> minuteMetrics = events
    .keyBy(event -> event.getVideoId())
    .window(TumblingEventTimeWindows.of(Time.minutes(1)))
    .aggregate(new MetricsAggregator());

// Sink to ClickHouse
minuteMetrics.addSink(new ClickHouseSink<>());
```

### 6.3 Batch Processing (Apache Spark)

**Daily Rollup Job:**
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder \
    .appName("YouTube Daily Metrics") \
    .getOrCreate()

# Read from ClickHouse (yesterday's data)
df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:clickhouse://ch-cluster:8123") \
    .option("query", """
        SELECT video_id, user_id, timestamp, watch_time_seconds, country
        FROM video_views
        WHERE date = today() - 1
    """) \
    .load()

# Aggregate by video
daily_metrics = df.groupBy("video_id").agg(
    count("*").alias("views"),
    countDistinct("user_id").alias("unique_viewers"),
    sum("watch_time_seconds").alias("total_watch_time"),
    collect_list(struct("country", "user_id")).alias("demographics")
)

# Write to aggregated table
daily_metrics.write \
    .format("jdbc") \
    .option("url", "jdbc:clickhouse://ch-cluster:8123") \
    .option("dbtable", "video_daily_metrics") \
    .mode("append") \
    .save()
```

### 6.4 Query Service (Analytics API)

**Fast Query with ClickHouse:**
```python
from clickhouse_driver import Client

class AnalyticsQuery:
    def __init__(self):
        self.ch_client = Client(
            host='ch-cluster',
            settings={'max_execution_time': 10}  # 10s timeout
        )
        self.redis_client = redis.Redis()
    
    def get_video_metrics(self, video_id: str, time_range: str):
        """
        Get video metrics with caching
        """
        cache_key = f"video:{video_id}:metrics:{time_range}"
        
        # Check cache
        cached = self.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Query ClickHouse
        query = """
            SELECT
                video_id,
                sum(views) as total_views,
                uniq(user_id) as unique_viewers,
                sum(watch_time_seconds) / 3600 as watch_time_hours,
                topK(10)(country) as top_countries
            FROM video_views
            WHERE video_id = %(video_id)s
              AND timestamp >= now() - INTERVAL %(interval)s
            GROUP BY video_id
        """
        
        result = self.ch_client.execute(
            query,
            {'video_id': video_id, 'interval': time_range}
        )
        
        metrics = self._format_result(result)
        
        # Cache for 5 minutes
        self.redis_client.setex(cache_key, 300, json.dumps(metrics))
        
        return metrics
```

---

## Step 7: Trade-offs & Optimizations

### CAP Theorem Trade-off

**Chosen: AP (Availability + Partition Tolerance)**

**Rationale:**
- View counts don't need strong consistency
- Acceptable to show slightly stale data (< 1 min lag)
- High availability critical for creator experience

**Example:**
```
Video at 10:00:00 AM: 1,000,000 views
User checks at 10:00:01 AM: sees 999,950 views (replication lag)
User checks at 10:01:00 AM: sees 1,000,050 views (caught up)

Impact: Negligible for creators
Benefit: System stays up during network partitions
```

### Data Freshness vs Cost

**Option 1: Real-time (Expensive)**
```
Pipeline: Kafka → Flink → ClickHouse
Latency: < 1 second
Cost: $50,000/month (Flink cluster)
```

**Option 2: Near Real-time (Chosen)**
```
Pipeline: Kafka → Flink (1-min windows) → ClickHouse
Latency: < 1 minute
Cost: $20,000/month
Benefit: 60% cost savings, acceptable for creators
```

**Option 3: Batch (Cheapest)**
```
Pipeline: Kafka → Spark (hourly) → ClickHouse
Latency: 1 hour
Cost: $5,000/month
Issue: Not acceptable for trending/real-time features
```

### Storage Optimization

**Compression:**
```sql
-- ClickHouse compression (ZSTD)
CREATE TABLE video_views (...)
ENGINE = MergeTree()
SETTINGS 
    storage_policy = 'tiered',  -- Hot (SSD) → Cold (S3)
    ttl_only_drop_parts = 1

-- Automatic tiering
ALTER TABLE video_views 
MODIFY TTL 
    timestamp + INTERVAL 7 DAY TO VOLUME 'ssd',
    timestamp + INTERVAL 90 DAY TO VOLUME 's3';

-- Result:
-- Raw: 146 TB
-- Compressed: 48 TB (3x)
-- With tiering: 5 TB SSD + 43 TB S3
-- Cost: $500/mo (SSD) + $1,000/mo (S3) = $1,500/mo
```

### Query Performance

**Materialized Views (Pre-aggregation):**
```sql
-- Instead of scanning 1B rows every query
-- Pre-aggregate by day
CREATE MATERIALIZED VIEW video_daily_metrics
AS SELECT
    video_id,
    toDate(timestamp) as date,
    count() as views,
    uniq(user_id) as unique_viewers
FROM video_views
GROUP BY video_id, date;

-- Query performance
-- Before: 10 seconds (scan 1B rows)
-- After: 50ms (scan 800M pre-aggregated rows)
```

---

## 🎯 Interview Discussion Points

### Scalability

**Q: How would you handle 10x traffic (10B views/day)?**

**A:**
1. **Horizontal scaling:**
   - Kafka: 100 → 1000 partitions
   - Flink: 10 → 100 task managers
   - ClickHouse: 4 → 40 shards

2. **Sampling:**
   - Sample 10% of events for trending (still 1B events)
   - Full data for creator analytics
   - Result: 90% cost savings, minimal accuracy loss

3. **Edge processing:**
   - Pre-aggregate at CDN edge before Kafka
   - Reduce 10B events → 100M aggregates

### Failure Scenarios

**Q: What if ClickHouse goes down?**

**A:**
1. **Kafka retains data** (48 hours)
2. **Replay from Kafka** once ClickHouse recovers
3. **Serve stale data from Redis** during outage
4. **Graceful degradation:** Show "Data delayed" message

**Q: What if Flink crashes?**

**A:**
1. **Checkpointing:** Flink saves state to S3 every 1 min
2. **Restart from last checkpoint**
3. **Kafka offset management:** No data loss (exactly-once)

### Monitoring

**Key Metrics:**
```
• Kafka lag (should be < 1000 messages)
• Flink checkpoint duration (should be < 10s)
• ClickHouse query latency (p99 < 1s)
• Redis cache hit rate (should be > 80%)
• End-to-end latency (event → dashboard, should be < 60s)
```

**Alerts:**
```
CRITICAL: Kafka lag > 100,000
WARNING: Cache hit rate < 70%
INFO: ClickHouse query slow (> 2s)
```

---

## 📊 Final Architecture Summary

| Component | Technology | Purpose | Scale |
|-----------|-----------|---------|-------|
| Ingestion | Kafka | Event buffering | 35K events/sec |
| Stream Processing | Flink | Real-time aggregation | 1-min windows |
| Batch Processing | Spark | Daily rollups | 1B events/day |
| OLAP DB | ClickHouse | Analytics queries | 300 TB |
| Cache | Redis | Hot data | 200 GB |
| Query API | Python/Go | Serve dashboards | 6K QPS |

**Monthly Cost:** ~$30,000  
**Team Size:** 5-7 engineers (2 backend, 2 data, 1 ML, 1 SRE, 1 PM)

---

**Next:** [Design Data Lake Architecture](./02-Data-Lake.md)
