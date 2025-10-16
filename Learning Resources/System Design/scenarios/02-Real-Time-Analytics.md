# Design Real-Time Analytics Platform - Complete System Design

**Difficulty:** ⭐⭐⭐⭐⭐  
**Interview Frequency:** Very High (Uber, Netflix, Amazon, 40 LPA+)  
**Time to Complete:** 45-60 minutes  
**Real-World Examples:** Uber's Real-Time Data Platform, Netflix Keystone, LinkedIn Brooklin

---

## 📋 Problem Statement

**Design a real-time analytics platform that can:**
- Process 10 million events per second
- Provide sub-second query latency for dashboards
- Support complex aggregations and windowing operations
- Handle late-arriving data and out-of-order events
- Scale to 1000+ concurrent dashboards
- Maintain exactly-once processing semantics
- Support both streaming and batch queries

**Use Cases:**
- Real-time ride tracking dashboard (Uber)
- Live video streaming analytics (Netflix)
- Real-time fraud detection (PayPal)
- IoT sensor monitoring (Tesla)
- E-commerce sales dashboards (Amazon)

---

## 🎯 Functional Requirements

### **Core Capabilities**
1. **Data Ingestion**
   - Ingest from Kafka, Kinesis, Pub/Sub
   - Support schema evolution
   - Handle backpressure gracefully
   - Support multiple data formats (JSON, Avro, Protobuf)

2. **Stream Processing**
   - Complex event processing (CEP)
   - Windowed aggregations (tumbling, sliding, session)
   - Stateful transformations
   - Join streams with reference data
   - Late data handling

3. **Storage**
   - Time-series optimized storage
   - Columnar format for analytics
   - Support for point and range queries
   - Data retention and compaction

4. **Query Layer**
   - SQL queries on real-time data
   - Sub-second query latency
   - Support for complex aggregations
   - Historical + real-time unified queries

5. **Visualization**
   - Real-time dashboards
   - Alerts and notifications
   - Drill-down capabilities
   - Export capabilities

---

## 🏗️ High-Level Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     EVENT SOURCES                               │
├────────────────────────────────────────────────────────────────┤
│  Mobile Apps │ Web Apps │ IoT Devices │ Services │ Databases   │
└────┬───────────────┬────────────┬──────────┬─────────────┬─────┘
     │               │            │          │             │
     ▼               ▼            ▼          ▼             ▼
┌────────────────────────────────────────────────────────────────┐
│                   MESSAGE BROKER (Kafka)                        │
├────────────────────────────────────────────────────────────────┤
│  Topics: events, clicks, orders, metrics, logs                 │
│  Partitions: 100+ per topic for parallelism                    │
│  Retention: 7 days (configurable)                              │
│  Replication: 3x for fault tolerance                           │
└────┬───────────────┬────────────┬──────────┬─────────────┬─────┘
     │               │            │          │             │
     ▼               ▼            ▼          ▼             ▼
┌────────────────────────────────────────────────────────────────┐
│               STREAM PROCESSING (Flink/Spark Streaming)        │
├────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Aggregation  │  │ Enrichment   │  │ Filtering    │        │
│  │ Pipeline     │  │ Pipeline     │  │ Pipeline     │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
│  Features:                                                      │
│  - Windowing (tumbling, sliding, session)                     │
│  - State management (RocksDB backend)                         │
│  - Exactly-once semantics                                     │
│  - Watermarks for late data                                   │
└────┬───────────────┬────────────┬──────────┬─────────────┬─────┘
     │               │            │          │             │
     │               │            │          │             │
     ▼               ▼            ▼          ▼             ▼
┌────────────────────────────────────────────────────────────────┐
│                   STORAGE LAYER                                 │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────┐      │
│  │  OLAP Storage (ClickHouse / Druid / Pinot)         │      │
│  │  - Columnar storage for fast analytics             │      │
│  │  - Pre-aggregated rollups                          │      │
│  │  - Bitmap indexing                                  │      │
│  │  - Distributed queries                              │      │
│  └─────────────────────────────────────────────────────┘      │
│                                                                 │
│  ┌─────────────────────────────────────────────────────┐      │
│  │  Time-Series DB (TimescaleDB / InfluxDB)           │      │
│  │  - Optimized for time-series data                  │      │
│  │  - Automatic downsampling                          │      │
│  │  - Continuous aggregates                           │      │
│  └─────────────────────────────────────────────────────┘      │
│                                                                 │
│  ┌─────────────────────────────────────────────────────┐      │
│  │  Cache Layer (Redis / Memcached)                   │      │
│  │  - Hot data caching                                 │      │
│  │  - Query result caching                            │      │
│  └─────────────────────────────────────────────────────┘      │
└────┬───────────────┬────────────┬──────────┬─────────────┬─────┘
     │               │            │          │             │
     ▼               ▼            ▼          ▼             ▼
┌────────────────────────────────────────────────────────────────┐
│                   QUERY LAYER                                   │
├────────────────────────────────────────────────────────────────┤
│  Presto/Trino - Federated SQL queries                         │
│  GraphQL API - Flexible data fetching                         │
│  REST API - Standard integrations                             │
└────┬───────────────┬────────────┬──────────┬─────────────┬─────┘
     │               │            │          │             │
     ▼               ▼            ▼          ▼             ▼
┌────────────────────────────────────────────────────────────────┐
│                 VISUALIZATION LAYER                             │
├────────────────────────────────────────────────────────────────┤
│  Grafana │ Tableau │ Custom Dashboards │ Mobile Apps           │
└────────────────────────────────────────────────────────────────┘
```

---

## 💻 Detailed Component Design

### **1. Stream Processing with Apache Flink**

```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.window import TumblingEventTimeWindows, SlidingEventTimeWindows
from pyflink.common import Time, WatermarkStrategy
from pyflink.common.typeinfo import Types
from pyflink.datastream.functions import KeyedProcessFunction, RuntimeContext
from pyflink.datastream.state import ValueStateDescriptor, MapStateDescriptor
from datetime import datetime, timedelta
import json

class RealTimeAnalyticsPipeline:
    def __init__(self):
        self.env = StreamExecutionEnvironment.get_execution_environment()
        
        # Checkpoint configuration for exactly-once
        self.env.enable_checkpointing(60000)  # Checkpoint every 60 seconds
        self.env.get_checkpoint_config().set_checkpoint_timeout(300000)  # 5 min timeout
        self.env.get_checkpoint_config().set_min_pause_between_checkpoints(30000)
        self.env.get_checkpoint_config().set_max_concurrent_checkpoints(1)
        
        # State backend configuration
        self.env.set_state_backend_rocksdb_options({
            'state.backend': 'rocksdb',
            'state.backend.rocksdb.memory.managed': 'true',
            'state.backend.rocksdb.block.cache-size': '256m',
            'state.backend.rocksdb.write-buffer-size': '64m',
            'state.backend.incremental': 'true'  # Incremental checkpointing
        })
        
        # Parallelism configuration
        self.env.set_parallelism(100)  # Match Kafka partition count
    
    def create_event_stream(self):
        """Create Kafka source with schema and watermarks"""
        
        from pyflink.datastream.connectors import FlinkKafkaConsumer
        from pyflink.common.serialization import JsonRowDeserializationSchema
        
        # Define event schema
        event_schema = Types.ROW_NAMED(
            ['event_id', 'user_id', 'event_type', 'timestamp', 'properties'],
            [Types.STRING(), Types.STRING(), Types.STRING(), Types.LONG(), Types.MAP(Types.STRING(), Types.STRING())]
        )
        
        # Kafka consumer configuration
        kafka_props = {
            'bootstrap.servers': 'kafka-1:9092,kafka-2:9092,kafka-3:9092',
            'group.id': 'realtime-analytics',
            'enable.auto.commit': 'false',  # Flink manages offsets
            'max.partition.fetch.bytes': '10485760',  # 10 MB
            'fetch.max.wait.ms': '500',
            'isolation.level': 'read_committed'  # Exactly-once semantics
        }
        
        # Create Kafka source
        kafka_consumer = FlinkKafkaConsumer(
            topics=['user-events', 'clickstream', 'transactions'],
            deserialization_schema=JsonRowDeserializationSchema.builder()
                .type_info(event_schema)
                .build(),
            properties=kafka_props
        )
        
        # Set up watermark strategy for handling late data
        watermark_strategy = WatermarkStrategy \
            .for_bounded_out_of_orderness(timedelta(minutes=5)) \
            .with_timestamp_assigner(lambda event, timestamp: event['timestamp'])
        
        kafka_consumer.set_start_from_earliest()  # Or latest/timestamp
        
        # Create data stream
        event_stream = self.env.add_source(kafka_consumer) \
            .assign_timestamps_and_watermarks(watermark_strategy)
        
        return event_stream
    
    def compute_realtime_metrics(self, event_stream):
        """
        Compute various real-time metrics with different window types
        """
        
        # 1. Tumbling Window - Fixed time windows (e.g., events per minute)
        events_per_minute = event_stream \
            .key_by(lambda event: event['event_type']) \
            .window(TumblingEventTimeWindows.of(Time.minutes(1))) \
            .reduce(
                lambda acc, event: {
                    'event_type': event['event_type'],
                    'count': acc.get('count', 0) + 1,
                    'window_start': acc.get('window_start', event['timestamp']),
                    'window_end': event['timestamp']
                }
            )
        
        # 2. Sliding Window - Overlapping windows (e.g., events per 5 min, updated every 1 min)
        events_per_5min = event_stream \
            .key_by(lambda event: event['event_type']) \
            .window(SlidingEventTimeWindows.of(Time.minutes(5), Time.minutes(1))) \
            .reduce(
                lambda acc, event: {
                    'event_type': event['event_type'],
                    'count': acc.get('count', 0) + 1,
                    'unique_users': len(set(acc.get('users', set()) | {event['user_id']}))
                }
            )
        
        # 3. Session Window - Dynamic windows based on user activity
        from pyflink.datastream.window import SessionWindowTimeGapExtractor
        
        user_sessions = event_stream \
            .key_by(lambda event: event['user_id']) \
            .window(SessionWindowTimeGapExtractor.with_dynamic_gap(
                lambda event: Time.minutes(30)  # 30 min inactivity = session end
            )) \
            .process(UserSessionProcessor())
        
        # 4. Global aggregations with custom window logic
        custom_metrics = event_stream \
            .key_by(lambda event: event['event_type']) \
            .process(CustomMetricsProcessor())
        
        return {
            'events_per_minute': events_per_minute,
            'events_per_5min': events_per_5min,
            'user_sessions': user_sessions,
            'custom_metrics': custom_metrics
        }
    
    def enrich_events(self, event_stream):
        """
        Enrich events with reference data (user profiles, product info)
        """
        
        from pyflink.datastream.connectors.jdbc import JdbcConnectionOptions, JdbcSink
        
        class EventEnricher(KeyedProcessFunction):
            def __init__(self):
                self.user_cache = None
                
            def open(self, runtime_context: RuntimeContext):
                # Initialize state for user cache
                user_cache_descriptor = MapStateDescriptor(
                    'user_cache',
                    Types.STRING(),
                    Types.MAP(Types.STRING(), Types.STRING())
                )
                self.user_cache = runtime_context.get_map_state(user_cache_descriptor)
            
            def process_element(self, event, ctx: KeyedProcessFunction.Context):
                user_id = event['user_id']
                
                # Check cache first
                cached_user = self.user_cache.get(user_id)
                
                if cached_user is None:
                    # Fetch from database (async recommended)
                    user_data = self.fetch_user_data(user_id)
                    self.user_cache.put(user_id, user_data)
                else:
                    user_data = cached_user
                
                # Enrich event
                enriched_event = {
                    **event,
                    'user_tier': user_data.get('tier', 'free'),
                    'user_country': user_data.get('country', 'unknown'),
                    'user_signup_date': user_data.get('signup_date')
                }
                
                yield enriched_event
            
            def fetch_user_data(self, user_id: str):
                # In production, use async I/O
                # from pyflink.datastream.functions import AsyncDataStreamAPI
                import psycopg2
                
                conn = psycopg2.connect(
                    host="postgres-read-replica",
                    database="users",
                    user="readonly",
                    password="***"
                )
                
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT tier, country, signup_date FROM users WHERE user_id = %s",
                    (user_id,)
                )
                
                result = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if result:
                    return {
                        'tier': result[0],
                        'country': result[1],
                        'signup_date': str(result[2])
                    }
                return {}
        
        enriched_stream = event_stream \
            .key_by(lambda event: event['user_id']) \
            .process(EventEnricher())
        
        return enriched_stream
    
    def handle_late_data(self, windowed_stream):
        """
        Handle late-arriving data using side outputs
        """
        
        from pyflink.datastream.window import TumblingEventTimeWindows
        from pyflink.datastream.functions import ProcessWindowFunction
        
        # Define side output tag for late data
        late_data_tag = OutputTag('late-data', Types.ROW(...))
        
        class WindowProcessorWithLateData(ProcessWindowFunction):
            def process(self, key, context: ProcessWindowFunction.Context, elements):
                # Main output - on-time data
                count = len(list(elements))
                window_end = context.window().max_timestamp()
                
                yield {
                    'key': key,
                    'count': count,
                    'window_end': window_end
                }
            
            def process_late_data(self, element, context):
                # Side output - late data
                context.output(late_data_tag, element)
        
        # Main stream
        main_output = windowed_stream \
            .window(TumblingEventTimeWindows.of(Time.minutes(1))) \
            .allowed_lateness(Time.minutes(5)) \
            .process(WindowProcessorWithLateData())
        
        # Late data stream
        late_data_stream = main_output.get_side_output(late_data_tag)
        
        # Store late data separately for analysis
        late_data_stream.add_sink(
            self.create_late_data_sink()
        )
        
        return main_output

class CustomMetricsProcessor(KeyedProcessFunction):
    """
    Custom stateful processor for complex metrics
    """
    
    def __init__(self):
        self.count_state = None
        self.timer_state = None
    
    def open(self, runtime_context: RuntimeContext):
        # Initialize state
        count_descriptor = ValueStateDescriptor('count', Types.LONG())
        self.count_state = runtime_context.get_state(count_descriptor)
        
        timer_descriptor = ValueStateDescriptor('timer', Types.LONG())
        self.timer_state = runtime_context.get_state(timer_descriptor)
    
    def process_element(self, event, ctx: KeyedProcessFunction.Context):
        # Update count
        current_count = self.count_state.value() or 0
        self.count_state.update(current_count + 1)
        
        # Set timer for 1 minute if not already set
        timer_timestamp = self.timer_state.value()
        if timer_timestamp is None:
            # Align to minute boundary
            next_minute = ((event['timestamp'] // 60000) + 1) * 60000
            ctx.timer_service().register_event_time_timer(next_minute)
            self.timer_state.update(next_minute)
    
    def on_timer(self, timestamp: int, ctx: KeyedProcessFunction.OnTimerContext):
        # Emit metric when timer fires
        count = self.count_state.value() or 0
        
        yield {
            'event_type': ctx.get_current_key(),
            'count': count,
            'timestamp': timestamp
        }
        
        # Reset state
        self.count_state.clear()
        self.timer_state.clear()

class UserSessionProcessor(KeyedProcessFunction):
    """
    Process user sessions to compute session metrics
    """
    
    def process_element(self, events, ctx):
        events_list = list(events)
        
        if not events_list:
            return
        
        session_start = min(e['timestamp'] for e in events_list)
        session_end = max(e['timestamp'] for e in events_list)
        duration = session_end - session_start
        
        # Compute session metrics
        session_metrics = {
            'user_id': ctx.get_current_key(),
            'session_start': session_start,
            'session_end': session_end,
            'duration_seconds': duration / 1000,
            'event_count': len(events_list),
            'event_types': list(set(e['event_type'] for e in events_list)),
            'page_views': sum(1 for e in events_list if e['event_type'] == 'page_view'),
            'conversions': sum(1 for e in events_list if e['event_type'] == 'purchase')
        }
        
        yield session_metrics

### **2. OLAP Storage with ClickHouse**

```python
class ClickHouseStorageManager:
    """
    Manage ClickHouse cluster for real-time analytics
    """
    
    def __init__(self, cluster_hosts: List[str]):
        from clickhouse_driver import Client
        
        self.clients = [Client(host=host) for host in cluster_hosts]
        self.write_client = self.clients[0]  # Primary for writes
        
    def create_events_table(self):
        """
        Create optimized ClickHouse table for event analytics
        """
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS events ON CLUSTER '{cluster}'
        (
            event_id String,
            user_id String,
            event_type LowCardinality(String),
            event_timestamp DateTime64(3),
            event_date Date DEFAULT toDate(event_timestamp),
            
            -- User dimensions
            user_tier LowCardinality(String),
            user_country LowCardinality(String),
            
            -- Event properties (flexible schema)
            properties Map(String, String),
            
            -- Derived metrics
            session_id String,
            is_conversion UInt8,
            revenue Decimal(10, 2),
            
            -- Technical fields
            ingestion_time DateTime DEFAULT now(),
            partition_key UInt32 DEFAULT cityHash64(user_id) % 100
        )
        ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/events', '{replica}')
        PARTITION BY toYYYYMM(event_date)
        ORDER BY (event_type, event_date, user_id, event_timestamp)
        TTL event_date + INTERVAL 90 DAY
        SETTINGS 
            index_granularity = 8192,
            merge_with_ttl_timeout = 3600,
            min_bytes_for_wide_part = 10485760,
            compress_primary_key = 1;
        
        -- Create distributed table
        CREATE TABLE IF NOT EXISTS events_distributed ON CLUSTER '{cluster}' AS events
        ENGINE = Distributed('{cluster}', default, events, rand());
        
        -- Create materialized views for pre-aggregation
        CREATE MATERIALIZED VIEW IF NOT EXISTS events_by_hour ON CLUSTER '{cluster}'
        ENGINE = ReplicatedSummingMergeTree('/clickhouse/tables/{shard}/events_by_hour', '{replica}')
        PARTITION BY toYYYYMM(event_hour)
        ORDER BY (event_type, event_hour, user_tier)
        AS SELECT
            event_type,
            toStartOfHour(event_timestamp) AS event_hour,
            user_tier,
            count() AS event_count,
            uniqExact(user_id) AS unique_users,
            sumIf(revenue, is_conversion = 1) AS total_revenue
        FROM events
        GROUP BY event_type, event_hour, user_tier;
        
        -- Bitmap index for high-cardinality columns
        CREATE INDEX user_id_bitmap_idx user_id TYPE bloom_filter GRANULARITY 1;
        """
        
        self.write_client.execute(create_table_sql)
    
    def insert_events_batch(self, events: List[Dict]):
        """
        Batch insert events into ClickHouse
        """
        
        # Transform events to match schema
        rows = []
        for event in events:
            rows.append((
                event['event_id'],
                event['user_id'],
                event['event_type'],
                datetime.fromtimestamp(event['timestamp'] / 1000),
                event.get('user_tier', 'free'),
                event.get('user_country', 'unknown'),
                event.get('properties', {}),
                event.get('session_id', ''),
                1 if event.get('event_type') == 'purchase' else 0,
                event.get('revenue', 0.0)
            ))
        
        # Batch insert
        insert_sql = """
        INSERT INTO events 
        (event_id, user_id, event_type, event_timestamp, user_tier, user_country,
         properties, session_id, is_conversion, revenue)
        VALUES
        """
        
        self.write_client.execute(insert_sql, rows, types_check=True)
    
    def query_realtime_metrics(self, metric_type: str, time_range_minutes: int = 60):
        """
        Query real-time metrics with sub-second latency
        """
        
        queries = {
            'events_per_minute': """
                SELECT
                    toStartOfMinute(event_timestamp) AS minute,
                    event_type,
                    count() AS event_count,
                    uniqExact(user_id) AS unique_users
                FROM events
                WHERE event_timestamp >= now() - INTERVAL {time_range} MINUTE
                GROUP BY minute, event_type
                ORDER BY minute DESC
                LIMIT 1000
            """,
            
            'top_users': """
                SELECT
                    user_id,
                    user_tier,
                    count() AS event_count,
                    countIf(is_conversion = 1) AS conversion_count,
                    sum(revenue) AS total_revenue
                FROM events
                WHERE event_timestamp >= now() - INTERVAL {time_range} MINUTE
                GROUP BY user_id, user_tier
                ORDER BY event_count DESC
                LIMIT 100
            """,
            
            'funnel_analysis': """
                SELECT
                    funnel_step,
                    count() AS users_count,
                    count() / (SELECT count(DISTINCT user_id) FROM events WHERE event_type = 'page_view') AS conversion_rate
                FROM (
                    SELECT
                        user_id,
                        CASE
                            WHEN has(arraySort(groupArray(event_type)), 'page_view') THEN 'step_1_view'
                            WHEN has(arraySort(groupArray(event_type)), 'add_to_cart') THEN 'step_2_cart'
                            WHEN has(arraySort(groupArray(event_type)), 'checkout') THEN 'step_3_checkout'
                            WHEN has(arraySort(groupArray(event_type)), 'purchase') THEN 'step_4_purchase'
                        END AS funnel_step
                    FROM events
                    WHERE event_timestamp >= now() - INTERVAL {time_range} MINUTE
                    GROUP BY user_id
                )
                GROUP BY funnel_step
                ORDER BY funnel_step
            """,
            
            'cohort_retention': """
                WITH cohorts AS (
                    SELECT
                        user_id,
                        toStartOfDay(min(event_timestamp)) AS cohort_date
                    FROM events
                    GROUP BY user_id
                )
                SELECT
                    cohort_date,
                    dateDiff('day', cohort_date, event_date) AS days_since_signup,
                    count(DISTINCT user_id) AS active_users,
                    active_users / (SELECT count(*) FROM cohorts WHERE cohorts.cohort_date = events.cohort_date) AS retention_rate
                FROM events
                JOIN cohorts USING (user_id)
                WHERE cohort_date >= today() - INTERVAL 30 DAY
                GROUP BY cohort_date, days_since_signup
                ORDER BY cohort_date, days_since_signup
            """
        }
        
        query = queries.get(metric_type, queries['events_per_minute'])
        query = query.format(time_range=time_range_minutes)
        
        # Execute with query result caching
        result = self.write_client.execute(
            query,
            settings={
                'use_query_cache': 1,
                'query_cache_ttl': 60,  # Cache for 60 seconds
                'max_threads': 8
            }
        )
        
        return result
```

### **3. Caching Layer with Redis**

```python
import redis
import json
from typing import Optional

class AnalyticsCacheManager:
    def __init__(self, redis_hosts: List[str]):
        # Redis Cluster for high availability
        from rediscluster import RedisCluster
        
        startup_nodes = [{"host": host, "port": 6379} for host in redis_hosts]
        self.redis_client = RedisCluster(
            startup_nodes=startup_nodes,
            decode_responses=True,
            skip_full_coverage_check=True,
            max_connections=100
        )
    
    def cache_query_result(self, query_hash: str, result: dict, ttl: int = 60):
        """Cache query result with TTL"""
        
        cache_key = f"query_result:{query_hash}"
        
        # Store with compression
        import gzip
        compressed_result = gzip.compress(json.dumps(result).encode())
        
        self.redis_client.setex(
            cache_key,
            ttl,
            compressed_result
        )
    
    def get_cached_result(self, query_hash: str) -> Optional[dict]:
        """Retrieve cached query result"""
        
        cache_key = f"query_result:{query_hash}"
        cached_data = self.redis_client.get(cache_key)
        
        if cached_data:
            import gzip
            decompressed = gzip.decompress(cached_data)
            return json.loads(decompressed)
        
        return None
    
    def cache_realtime_metric(self, metric_name: str, value: float):
        """Cache real-time metric with time series"""
        
        import time
        timestamp = int(time.time())
        
        # Use Redis time series
        ts_key = f"metric:{metric_name}"
        
        self.redis_client.ts().add(
            ts_key,
            timestamp,
            value,
            retention_msecs=3600000,  # 1 hour
            labels={'metric': metric_name}
        )
    
    def get_metric_timeseries(self, metric_name: str, time_range_seconds: int = 3600):
        """Get metric time series"""
        
        import time
        end_time = int(time.time())
        start_time = end_time - time_range_seconds
        
        ts_key = f"metric:{metric_name}"
        
        result = self.redis_client.ts().range(
            ts_key,
            start_time * 1000,
            end_time * 1000
        )
        
        return [(ts / 1000, value) for ts, value in result]
```

---

## 🎓 Key Interview Points

### **Critical Design Decisions:**
1. **Exactly-once semantics** - Flink checkpointing + Kafka transactions
2. **Watermarking strategy** - 5-minute bounded out-of-orderness
3. **State management** - RocksDB for large state, incremental checkpointing
4. **Storage optimization** - ClickHouse MergeTree with pre-aggregation
5. **Query caching** - Redis for sub-second dashboard loads

### **Scale Calculations:**
```
Events: 10M/sec × 86,400 sec = 864B events/day
Storage (compressed): 864B × 200 bytes × 0.3 = 52 TB/day
ClickHouse nodes: 52 TB / 2 TB per node = 26 nodes minimum
Kafka partitions: 10M / 100K per partition = 100 partitions
Flink parallelism: Match Kafka partitions = 100
```

**This scenario demonstrates production-grade real-time analytics - essential for FAANG interviews!** 🚀
