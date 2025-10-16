# Design Ad Click Tracking & Attribution System - Complete System Design

**Difficulty:** ⭐⭐⭐⭐  
**Interview Frequency:** Very High (Google Ads, Facebook Ads, Amazon Advertising, 40 LPA+)  
**Time to Complete:** 40-45 minutes  
**Real-World Examples:** Google Analytics, Facebook Pixel, Amazon Attribution

---

## 📋 Problem Statement

**Design an ad click tracking system that can:**
- Track 10 billion ad impressions daily
- Record 500 million clicks per day
- Attribute conversions to ad campaigns (multi-touch attribution)
- Process events in real-time (<1 second delay)
- Provide analytics dashboard (CTR, conversion rate, ROAS)
- Handle ad fraud detection
- Support A/B testing for ad creatives
- Generate billing reports (pay-per-click, pay-per-impression)
- Scale globally across regions
- Provide near real-time reporting (<5 minute delay)

**Business Goals:**
- Accurate attribution for advertisers
- Prevent click fraud
- Maximize ad revenue
- Provide actionable insights

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                  EVENT COLLECTION PIPELINE                    │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Ad Impression Flow:                                         │
│  ┌────────┐    ┌──────────┐    ┌────────┐    ┌──────────┐  │
│  │Browser │───▶│ CDN/Edge │───▶│ Tracker│───▶│  Kafka   │  │
│  │ Pixel  │    │ Endpoint │    │ Service│    │  Topic   │  │
│  └────────┘    └──────────┘    └────────┘    └──────────┘  │
│                                                               │
│  Tracking Pixel (1x1 transparent GIF):                       │
│  <img src="https://track.adnetwork.com/pixel?                │
│    ad_id=12345&                                               │
│    campaign_id=67890&                                         │
│    user_id=abc123&                                            │
│    timestamp=1640000000&                                      │
│    event=impression" />                                       │
│                                                               │
│  Click Tracking (302 Redirect):                              │
│  https://track.adnetwork.com/click?                          │
│    ad_id=12345&redirect=https://example.com                  │
│                                                               │
│  Conversion Tracking (Postback):                             │
│  POST /api/v1/conversions                                    │
│  {                                                            │
│    "click_id": "xyz789",                                      │
│    "conversion_value": 99.99,                                 │
│    "conversion_type": "purchase"                              │
│  }                                                            │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│              REAL-TIME PROCESSING (Apache Flink)              │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  DEDUPLICATION PIPELINE                                │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  Problem: Same event sent multiple times              │ │
│  │  Solution: Deduplicate using event_id + timestamp     │ │
│  │                                                        │ │
│  │  Flink State:                                          │ │
│  │  - 5-minute window                                     │ │
│  │  - Store event_id hashes (Bloom filter)               │ │
│  │  - Drop duplicates                                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  FRAUD DETECTION PIPELINE                             │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  Click Fraud Patterns:                                │ │
│  │  1. Click Flooding: Same IP > 100 clicks/min          │ │
│  │  2. Bot Traffic: Missing User-Agent, suspicious IPs   │ │
│  │  3. Click Farms: Geolocation mismatch                 │ │
│  │  4. Invalid Traffic: No subsequent page views         │ │
│  │                                                        │ │
│  │  Detection:                                            │ │
│  │  - Velocity checks (clicks per IP, user)              │ │
│  │  - Device fingerprinting                              │ │
│  │  - ML anomaly detection                               │ │
│  │  - Blacklist known fraud IPs                          │ │
│  │                                                        │ │
│  │  Action: Mark event as "fraud_suspected"              │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  ATTRIBUTION PIPELINE                                  │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  Attribution Models:                                   │ │
│  │                                                        │ │
│  │  1. Last-Click Attribution:                           │ │
│  │     - 100% credit to last ad clicked                  │ │
│  │     - Simple, fast                                     │ │
│  │                                                        │ │
│  │  2. First-Click Attribution:                          │ │
│  │     - 100% credit to first ad clicked                 │ │
│  │                                                        │ │
│  │  3. Linear Attribution:                               │ │
│  │     - Equal credit to all touchpoints                 │ │
│  │     - User journey: Ad1 → Ad2 → Ad3 → Conversion      │ │
│  │     - Each ad gets 33% credit                         │ │
│  │                                                        │ │
│  │  4. Time-Decay Attribution:                           │ │
│  │     - More credit to recent touchpoints               │ │
│  │     - Exponential decay: 50% → 30% → 20%             │ │
│  │                                                        │ │
│  │  5. Data-Driven Attribution (ML):                     ││
│  │     - Learn from historical data                      │ │
│  │     - Credit based on actual impact                   │ │
│  │                                                        │ │
│  │  Implementation:                                       │ │
│  │  - Join clicks with conversions (windowed join)       │ │
│  │  - Attribution window: 30 days                        │ │
│  │  - Store in Cassandra (user_id → touchpoints)         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  REAL-TIME AGGREGATION                                │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  Metrics per (campaign_id, ad_id, hour):              │ │
│  │  - Impressions count                                   │ │
│  │  - Clicks count                                        │ │
│  │  - Conversions count                                   │ │
│  │  - Revenue sum                                         │ │
│  │  - CTR = clicks / impressions                          │ │
│  │  - Conversion rate = conversions / clicks              │ │
│  │  - CPC = cost / clicks                                 │ │
│  │  - ROAS = revenue / cost                               │ │
│  │                                                        │ │
│  │  Output: Druid (for fast analytics)                   │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                    STORAGE LAYER                              │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  KAFKA (Event Stream)                                  │ │
│  │  - impressions (10B/day = 115K/sec)                    │ │
│  │  - clicks (500M/day = 5.7K/sec)                        │ │
│  │  - conversions (50M/day = 578/sec)                     │ │
│  │  Retention: 7 days                                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  CASSANDRA (Click Store)                               │ │
│  │  - Store click events (for attribution)                │ │
│  │  - Partition by user_id + date                         │ │
│  │  - TTL: 30 days (attribution window)                   │ │
│  │  Schema:                                               │ │
│  │    PRIMARY KEY ((user_id, date), timestamp)            │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  DRUID (OLAP Analytics)                                │ │
│  │  - Pre-aggregated metrics                              │ │
│  │  - Roll-up: hourly → daily → monthly                   │ │
│  │  - Fast queries (<1 second)                            │ │
│  │  - Dimensions: campaign, ad, geo, device, time         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  S3 (Cold Storage)                                     │ │
│  │  - Raw event logs (compliance, audits)                 │ │
│  │  - Parquet format (columnar)                           │ │
│  │  - Partitioned by date                                 │ │
│  │  - Lifecycle: Glacier after 90 days                    │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## 💻 Implementation

### **1. Event Tracking Service**

```python
from flask import Flask, request, redirect, send_file
from kafka import KafkaProducer
import json
import hashlib
import time
from io import BytesIO

app = Flask(__name__)

class AdTracker:
    """
    High-throughput ad tracking service
    """
    
    def __init__(self, kafka_brokers: str):
        self.kafka_producer = KafkaProducer(
            bootstrap_servers=kafka_brokers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            compression_type='snappy',
            batch_size=16384,
            linger_ms=10  # Batch for 10ms
        )
        
        # 1x1 transparent GIF
        self.pixel = BytesIO(
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
            b'\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00'
            b'\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02'
            b'\x44\x01\x00\x3b'
        )
    
    @app.route('/pixel', methods=['GET'])
    def track_impression(self):
        """
        Track ad impression via pixel
        GET /pixel?ad_id=123&campaign_id=456&user_id=abc
        """
        
        # Extract parameters
        ad_id = request.args.get('ad_id')
        campaign_id = request.args.get('campaign_id')
        user_id = request.args.get('user_id')
        
        # Enrich with metadata
        event = {
            'event_id': self._generate_event_id(),
            'event_type': 'impression',
            'ad_id': ad_id,
            'campaign_id': campaign_id,
            'user_id': user_id,
            'timestamp': int(time.time() * 1000),  # Milliseconds
            'user_agent': request.headers.get('User-Agent'),
            'ip_address': request.remote_addr,
            'referer': request.headers.get('Referer'),
            'country': self._get_country_from_ip(request.remote_addr)
        }
        
        # Send to Kafka (async)
        self.kafka_producer.send('impressions', event)
        
        # Return 1x1 pixel
        self.pixel.seek(0)
        return send_file(self.pixel, mimetype='image/gif')
    
    @app.route('/click', methods=['GET'])
    def track_click(self):
        """
        Track ad click and redirect
        GET /click?ad_id=123&redirect=https://example.com
        """
        
        ad_id = request.args.get('ad_id')
        campaign_id = request.args.get('campaign_id')
        user_id = request.args.get('user_id')
        redirect_url = request.args.get('redirect')
        
        # Generate click ID (for attribution)
        click_id = self._generate_click_id(user_id, ad_id)
        
        # Track click event
        event = {
            'event_id': self._generate_event_id(),
            'event_type': 'click',
            'click_id': click_id,
            'ad_id': ad_id,
            'campaign_id': campaign_id,
            'user_id': user_id,
            'timestamp': int(time.time() * 1000),
            'user_agent': request.headers.get('User-Agent'),
            'ip_address': request.remote_addr,
            'redirect_url': redirect_url
        }
        
        # Send to Kafka
        self.kafka_producer.send('clicks', event)
        
        # 302 Redirect
        return redirect(redirect_url, code=302)
    
    @app.route('/api/v1/conversions', methods=['POST'])
    def track_conversion(self):
        """
        Track conversion (server-to-server postback)
        POST /api/v1/conversions
        {"click_id": "xyz", "value": 99.99, "type": "purchase"}
        """
        
        data = request.json
        
        event = {
            'event_id': self._generate_event_id(),
            'event_type': 'conversion',
            'click_id': data['click_id'],
            'conversion_value': data.get('value', 0),
            'conversion_type': data.get('type', 'unknown'),
            'timestamp': int(time.time() * 1000)
        }
        
        # Send to Kafka
        self.kafka_producer.send('conversions', event)
        
        return {'status': 'ok', 'event_id': event['event_id']}, 200
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        return hashlib.sha256(
            f"{time.time()}{os.urandom(16)}".encode()
        ).hexdigest()[:16]
    
    def _generate_click_id(self, user_id: str, ad_id: str) -> str:
        """Generate click ID for attribution"""
        return hashlib.sha256(
            f"{user_id}{ad_id}{time.time()}".encode()
        ).hexdigest()[:16]


### **2. Attribution Engine**

```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment
from datetime import timedelta

class AttributionEngine:
    """
    Multi-touch attribution using Flink
    """
    
    def __init__(self):
        self.env = StreamExecutionEnvironment.get_execution_environment()
        self.t_env = StreamTableEnvironment.create(self.env)
        
        # Attribution window: 30 days
        self.attribution_window = timedelta(days=30)
    
    def process_attribution(self):
        """
        Join clicks with conversions for attribution
        """
        
        # Define clicks table
        self.t_env.execute_sql("""
            CREATE TABLE clicks (
                click_id STRING,
                user_id STRING,
                ad_id STRING,
                campaign_id STRING,
                click_timestamp BIGINT,
                event_time AS TO_TIMESTAMP(FROM_UNIXTIME(click_timestamp / 1000)),
                WATERMARK FOR event_time AS event_time - INTERVAL '10' SECOND
            ) WITH (
                'connector' = 'kafka',
                'topic' = 'clicks',
                'properties.bootstrap.servers' = 'kafka:9092',
                'format' = 'json'
            )
        """)
        
        # Define conversions table
        self.t_env.execute_sql("""
            CREATE TABLE conversions (
                click_id STRING,
                conversion_value DOUBLE,
                conversion_type STRING,
                conversion_timestamp BIGINT,
                event_time AS TO_TIMESTAMP(FROM_UNIXTIME(conversion_timestamp / 1000)),
                WATERMARK FOR event_time AS event_time - INTERVAL '10' SECOND
            ) WITH (
                'connector' = 'kafka',
                'topic' = 'conversions',
                'properties.bootstrap.servers' = 'kafka:9092',
                'format' = 'json'
            )
        """)
        
        # Interval join (30-day window)
        self.t_env.execute_sql("""
            CREATE VIEW attributed_conversions AS
            SELECT 
                c.click_id,
                c.user_id,
                c.ad_id,
                c.campaign_id,
                c.click_timestamp,
                conv.conversion_value,
                conv.conversion_type,
                conv.conversion_timestamp,
                (conv.conversion_timestamp - c.click_timestamp) / 1000 AS time_to_convert_seconds
            FROM clicks c
            INNER JOIN conversions conv
            ON c.click_id = conv.click_id
            WHERE conv.event_time BETWEEN c.event_time AND c.event_time + INTERVAL '30' DAY
        """)
        
        # Output to Kafka
        self.t_env.execute_sql("""
            CREATE TABLE attributed_output (
                click_id STRING,
                user_id STRING,
                ad_id STRING,
                campaign_id STRING,
                conversion_value DOUBLE,
                conversion_type STRING,
                time_to_convert_seconds BIGINT
            ) WITH (
                'connector' = 'kafka',
                'topic' = 'attributed-conversions',
                'properties.bootstrap.servers' = 'kafka:9092',
                'format' = 'json'
            )
        """)
        
        self.t_env.execute_sql("""
            INSERT INTO attributed_output
            SELECT 
                click_id,
                user_id,
                ad_id,
                campaign_id,
                conversion_value,
                conversion_type,
                time_to_convert_seconds
            FROM attributed_conversions
        """)


### **3. Real-Time Analytics**

```python
class AdAnalytics:
    """
    Real-time ad performance metrics
    """
    
    def compute_metrics(self):
        """
        Aggregate metrics per campaign/ad
        """
        
        self.t_env.execute_sql("""
            CREATE TABLE ad_metrics (
                campaign_id STRING,
                ad_id STRING,
                window_start TIMESTAMP(3),
                window_end TIMESTAMP(3),
                impressions BIGINT,
                clicks BIGINT,
                conversions BIGINT,
                revenue DOUBLE,
                ctr DOUBLE,
                conversion_rate DOUBLE,
                cpc DOUBLE,
                roas DOUBLE
            ) WITH (
                'connector' = 'druid',
                'datasource' = 'ad_performance',
                'coordinator-url' = 'http://druid-coordinator:8081'
            )
        """)
        
        # Compute metrics
        self.t_env.execute_sql("""
            INSERT INTO ad_metrics
            SELECT 
                campaign_id,
                ad_id,
                TUMBLE_START(event_time, INTERVAL '1' HOUR) as window_start,
                TUMBLE_END(event_time, INTERVAL '1' HOUR) as window_end,
                COUNT(CASE WHEN event_type = 'impression' THEN 1 END) as impressions,
                COUNT(CASE WHEN event_type = 'click' THEN 1 END) as clicks,
                COUNT(CASE WHEN event_type = 'conversion' THEN 1 END) as conversions,
                SUM(CASE WHEN event_type = 'conversion' THEN conversion_value ELSE 0 END) as revenue,
                CAST(COUNT(CASE WHEN event_type = 'click' THEN 1 END) AS DOUBLE) / 
                    NULLIF(COUNT(CASE WHEN event_type = 'impression' THEN 1 END), 0) as ctr,
                CAST(COUNT(CASE WHEN event_type = 'conversion' THEN 1 END) AS DOUBLE) / 
                    NULLIF(COUNT(CASE WHEN event_type = 'click' THEN 1 END), 0) as conversion_rate,
                cost / NULLIF(COUNT(CASE WHEN event_type = 'click' THEN 1 END), 0) as cpc,
                SUM(CASE WHEN event_type = 'conversion' THEN conversion_value ELSE 0 END) / 
                    NULLIF(cost, 0) as roas
            FROM events
            GROUP BY 
                campaign_id,
                ad_id,
                TUMBLE(event_time, INTERVAL '1' HOUR)
        """)
```

---

## 🎓 Interview Points

**Capacity:**
```
Impressions: 10B/day = 115K/sec
Clicks: 500M/day = 5.7K/sec
Conversions: 50M/day = 578/sec

Kafka: 115K events/sec × 500 bytes = 57 MB/sec
Storage: 10B × 500 bytes × 7 days = 35 TB
```

**Key challenges:** Deduplication, fraud detection, attribution windows!
