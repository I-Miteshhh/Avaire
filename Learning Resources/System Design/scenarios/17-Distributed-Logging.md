# Design Distributed Logging System - Complete System Design

**Difficulty:** ⭐⭐⭐⭐⭐  
**Interview Frequency:** High (Infrastructure companies, 40 LPA+)  
**Time to Complete:** 35-40 minutes  
**Real-World Examples:** Elasticsearch (ELK), Splunk, Datadog Logs

---

## 📋 Problem Statement

**Design a distributed logging system that can:**
- Ingest 10 TB of logs per day (100K log events/sec)
- Support structured logging (JSON) and unstructured (plain text)
- Provide real-time search and filtering
- Aggregate logs from 10K+ microservices
- Retain logs for 30 days (hot) + 1 year (cold storage)
- Support log correlation (trace IDs, request IDs)
- Provide alerting on log patterns
- Handle spikes (10x traffic during incidents)
- Query latency <1 second for recent logs

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    LOG INGESTION PIPELINE                     │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Application Servers (10K instances):                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   App 1     │  │   App 2     │  │   App 3     │         │
│  │ (stdout/    │  │ (file logs) │  │ (syslog)    │         │
│  │  stderr)    │  │             │  │             │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                  │
│         ▼                ▼                ▼                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          LOG COLLECTION AGENTS                       │   │
│  │  (Filebeat / Fluentd / Vector)                      │   │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │   │
│  │                                                       │   │
│  │  1. Tail log files (inotify)                        │   │
│  │  2. Parse log format (JSON, syslog, regex)          │   │
│  │  3. Add metadata (hostname, pod, namespace)         │   │
│  │  4. Buffer locally (disk queue for reliability)     │   │
│  │  5. Batch and compress (gzip)                       │   │
│  │  6. Send to Kafka                                    │   │
│  └─────────────────────┬───────────────────────────────┘   │
│                        │                                     │
│                        ▼                                     │
│          ┌─────────────────────────────┐                   │
│          │   KAFKA (Message Buffer)    │                   │
│          │   ━━━━━━━━━━━━━━━━━━━━━━━   │                   │
│          │   Topics:                    │                   │
│          │   - logs-raw (all logs)      │                   │
│          │   - logs-errors (filtering) │                   │
│          │   - logs-audit              │                   │
│          │                              │                   │
│          │   Retention: 24 hours        │                   │
│          │   Partitions: 100            │                   │
│          │   Replication: 3             │                   │
│          └──────────┬──────────────────┘                   │
│                     │                                        │
│         ┌───────────┼───────────┐                           │
│         │           │           │                            │
│         ▼           ▼           ▼                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                   │
│  │  Stream  │ │  Stream  │ │  Stream  │                   │
│  │ Processor│ │ Processor│ │ Processor│                   │
│  │    1     │ │    2     │ │    3     │                   │
│  └──────────┘ └──────────┘ └──────────┘                   │
│         │           │           │                            │
│         └───────────┼───────────┘                           │
│                     ▼                                        │
│          ┌─────────────────────────────┐                   │
│          │  ELASTICSEARCH CLUSTER       │                   │
│          │  ━━━━━━━━━━━━━━━━━━━━━━━━━  │                   │
│          │  Index pattern:              │                   │
│          │  logs-YYYY.MM.DD             │                   │
│          │                              │                   │
│          │  100 shards × 2 replicas     │                   │
│          │  500 GB per day              │                   │
│          └─────────────────────────────┘                   │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                 LOG PROCESSING & ENRICHMENT                   │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Raw Log:                                                    │
│  "2024-01-15 10:30:45 ERROR user login failed: invalid pwd" │
│                                                               │
│         ▼                                                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  PARSING & STRUCTURING (Logstash/Flink)               │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  Grok pattern:                                         │ │
│  │  %{TIMESTAMP_ISO8601:timestamp}                       │ │
│  │  %{LOGLEVEL:level}                                     │ │
│  │  %{GREEDYDATA:message}                                │ │
│  │                                                        │ │
│  │  Extracted fields:                                     │ │
│  │  {                                                     │ │
│  │    "timestamp": "2024-01-15T10:30:45Z",              │ │
│  │    "level": "ERROR",                                  │ │
│  │    "message": "user login failed: invalid pwd",      │ │
│  │    "service": "auth-service",                         │ │
│  │    "hostname": "web-server-01",                       │ │
│  │    "pod": "auth-abc123",                              │ │
│  │    "namespace": "production"                          │ │
│  │  }                                                     │ │
│  └────────────────────────────────────────────────────────┘ │
│         │                                                     │
│         ▼                                                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  ENRICHMENT                                            │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  1. Add trace context (from distributed tracing):     │ │
│  │     - trace_id: abc123                                │ │
│  │     - span_id: def456                                 │ │
│  │                                                        │ │
│  │  2. GeoIP lookup (if IP present):                     │ │
│  │     - country: US                                     │ │
│  │     - city: San Francisco                             │ │
│  │                                                        │ │
│  │  3. Add business context:                             │ │
│  │     - user_id: 12345                                  │ │
│  │     - customer_tier: premium                          │ │
│  └────────────────────────────────────────────────────────┘ │
│         │                                                     │
│         ▼                                                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  FILTERING & SAMPLING                                  │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  - Drop debug logs in production (too noisy)          │ │
│  │  - Sample INFO logs (1% rate)                         │ │
│  │  - Keep ALL ERROR/FATAL logs                          │ │
│  │  - Deduplicate identical logs (window: 5 min)         │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                   SEARCH & QUERYING                           │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Query DSL (Elasticsearch):                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  GET /logs-*/_search                                   │ │
│  │  {                                                     │ │
│  │    "query": {                                          │ │
│  │      "bool": {                                         │ │
│  │        "must": [                                       │ │
│  │          {"match": {"service": "auth-service"}},      │ │
│  │          {"range": {"@timestamp": {                   │ │
│  │            "gte": "now-1h",                            │ │
│  │            "lte": "now"                                │ │
│  │          }}}                                            │ │
│  │        ],                                              │ │
│  │        "filter": [                                     │ │
│  │          {"term": {"level": "ERROR"}}                 │ │
│  │        ]                                               │ │
│  │      }                                                  │ │
│  │    },                                                   │ │
│  │    "aggs": {                                           │ │
│  │      "errors_over_time": {                            │ │
│  │        "date_histogram": {                            │ │
│  │          "field": "@timestamp",                       │ │
│  │          "interval": "5m"                             │ │
│  │        }                                               │ │
│  │      }                                                  │ │
│  │    }                                                    │ │
│  │  }                                                     │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## 💻 Implementation

### **1. Log Shipper (Python Agent)**

```python
import json
import gzip
import time
from kafka import KafkaProducer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class LogShipper(FileSystemEventHandler):
    """
    Tail log files and ship to Kafka
    """
    
    def __init__(self, log_file_path: str, kafka_topic: str):
        self.log_file = log_file_path
        self.kafka = KafkaProducer(
            bootstrap_servers=['kafka1:9092', 'kafka2:9092'],
            compression_type='gzip',
            batch_size=16384,
            linger_ms=10
        )
        self.topic = kafka_topic
        self.buffer = []
        self.buffer_size = 100
    
    def on_modified(self, event):
        """
        File changed - read new lines
        """
        if event.src_path == self.log_file:
            with open(self.log_file, 'r') as f:
                # Seek to last read position
                f.seek(self.last_position)
                
                for line in f:
                    self._process_log_line(line.strip())
                
                # Update position
                self.last_position = f.tell()
    
    def _process_log_line(self, line: str):
        """
        Parse and enrich log line
        """
        
        # Parse log (assume JSON)
        try:
            log_event = json.loads(line)
        except:
            # Fallback to plain text
            log_event = {'message': line}
        
        # Add metadata
        log_event['@timestamp'] = int(time.time() * 1000)
        log_event['hostname'] = self._get_hostname()
        log_event['service'] = self._get_service_name()
        
        # Buffer
        self.buffer.append(log_event)
        
        if len(self.buffer) >= self.buffer_size:
            self._flush()
    
    def _flush(self):
        """
        Send buffered logs to Kafka
        """
        
        for log in self.buffer:
            self.kafka.send(
                self.topic,
                value=json.dumps(log).encode()
            )
        
        self.kafka.flush()
        self.buffer.clear()


### **2. Log Parser (Flink)**

```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.common.serialization import SimpleStringSchema
import json
import re

def parse_logs():
    """
    Parse raw logs using Flink
    """
    
    env = StreamExecutionEnvironment.get_execution_environment()
    
    # Kafka source
    kafka_source = FlinkKafkaConsumer(
        topics='logs-raw',
        deserialization_schema=SimpleStringSchema(),
        properties={'bootstrap.servers': 'kafka:9092'}
    )
    
    # Read stream
    log_stream = env.add_source(kafka_source)
    
    # Parse and enrich
    parsed_stream = log_stream.map(parse_log_event)
    
    # Filter errors
    error_stream = parsed_stream.filter(lambda log: log['level'] == 'ERROR')
    
    # Kafka sink
    kafka_sink = FlinkKafkaProducer(
        topic='logs-errors',
        serialization_schema=SimpleStringSchema(),
        producer_config={'bootstrap.servers': 'kafka:9092'}
    )
    
    error_stream.map(lambda log: json.dumps(log)).add_sink(kafka_sink)
    
    env.execute("Log Parser")


def parse_log_event(raw_log: str) -> dict:
    """
    Parse log line using regex (Grok-style)
    """
    
    # Pattern: timestamp level message
    pattern = r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (?P<level>\w+) (?P<message>.*)'
    
    match = re.match(pattern, raw_log)
    
    if match:
        return {
            'timestamp': match.group('timestamp'),
            'level': match.group('level'),
            'message': match.group('message'),
            'raw': raw_log
        }
    else:
        return {'raw': raw_log, 'level': 'UNKNOWN'}


### **3. Elasticsearch Indexer**

```python
from elasticsearch import Elasticsearch, helpers
from kafka import KafkaConsumer
import json

class LogIndexer:
    """
    Index logs into Elasticsearch
    """
    
    def __init__(self):
        self.es = Elasticsearch(['http://es1:9200', 'http://es2:9200'])
        self.kafka = KafkaConsumer(
            'logs-raw',
            bootstrap_servers=['kafka:9092'],
            auto_offset_reset='earliest',
            group_id='log-indexer'
        )
    
    def run(self):
        """
        Consume from Kafka and index to ES
        """
        
        batch = []
        batch_size = 1000
        
        for message in self.kafka:
            log_event = json.loads(message.value)
            
            # Prepare for bulk index
            batch.append({
                '_index': self._get_index_name(log_event['@timestamp']),
                '_source': log_event
            })
            
            if len(batch) >= batch_size:
                self._bulk_index(batch)
                batch.clear()
    
    def _get_index_name(self, timestamp: int) -> str:
        """
        Time-based index: logs-2024.01.15
        """
        from datetime import datetime
        dt = datetime.fromtimestamp(timestamp / 1000)
        return f"logs-{dt.strftime('%Y.%m.%d')}"
    
    def _bulk_index(self, batch):
        """
        Bulk index for performance
        """
        helpers.bulk(self.es, batch)


### **4. Log Search API**

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search_logs():
    """
    Search logs
    
    Query params:
    - query: search text
    - service: filter by service
    - level: filter by log level
    - from_time: start timestamp
    - to_time: end timestamp
    """
    
    query_text = request.args.get('query', '*')
    service = request.args.get('service')
    level = request.args.get('level')
    from_time = request.args.get('from_time', 'now-1h')
    to_time = request.args.get('to_time', 'now')
    
    # Build Elasticsearch query
    es_query = {
        "query": {
            "bool": {
                "must": [
                    {"query_string": {"query": query_text}},
                    {"range": {"@timestamp": {"gte": from_time, "lte": to_time}}}
                ],
                "filter": []
            }
        },
        "sort": [{"@timestamp": "desc"}],
        "size": 100
    }
    
    if service:
        es_query['query']['bool']['filter'].append({"term": {"service": service}})
    
    if level:
        es_query['query']['bool']['filter'].append({"term": {"level": level}})
    
    # Execute search
    result = es.search(index="logs-*", body=es_query)
    
    logs = [hit['_source'] for hit in result['hits']['hits']]
    
    return jsonify({
        'total': result['hits']['total']['value'],
        'logs': logs
    }), 200


@app.route('/aggregate', methods=['GET'])
def aggregate_logs():
    """
    Aggregate log statistics
    """
    
    # Aggregation query
    agg_query = {
        "size": 0,
        "aggs": {
            "errors_by_service": {
                "filter": {"term": {"level": "ERROR"}},
                "aggs": {
                    "services": {
                        "terms": {"field": "service.keyword", "size": 10}
                    }
                }
            },
            "log_volume_over_time": {
                "date_histogram": {
                    "field": "@timestamp",
                    "interval": "1h"
                }
            }
        }
    }
    
    result = es.search(index="logs-*", body=agg_query)
    
    return jsonify(result['aggregations']), 200


### **5. Log Alerting**

```python
from elasticsearch import Elasticsearch
import time

class LogAlerter:
    """
    Alert on log patterns
    """
    
    def __init__(self, es_client, alert_webhook):
        self.es = es_client
        self.webhook = alert_webhook
    
    def check_error_spike(self):
        """
        Alert if error rate exceeds threshold
        """
        
        # Count errors in last 5 minutes
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"level": "ERROR"}},
                        {"range": {"@timestamp": {"gte": "now-5m"}}}
                    ]
                }
            }
        }
        
        result = self.es.count(index="logs-*", body=query)
        error_count = result['count']
        
        # Threshold: 1000 errors in 5 min
        if error_count > 1000:
            self._send_alert({
                'title': 'High Error Rate',
                'message': f'{error_count} errors in last 5 minutes',
                'severity': 'critical'
            })
    
    def check_log_pattern(self, pattern: str):
        """
        Alert on specific log message pattern
        """
        
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"message": pattern}},
                        {"range": {"@timestamp": {"gte": "now-1m"}}}
                    ]
                }
            }
        }
        
        result = self.es.count(index="logs-*", body=query)
        
        if result['count'] > 0:
            self._send_alert({
                'title': f'Log Pattern Detected: {pattern}',
                'message': f'{result["count"]} occurrences',
                'severity': 'warning'
            })
```

---

## 🎓 Interview Points

**Capacity:**
```
Ingestion: 10 TB/day = 115 MB/sec
Events: 100K/sec × 1KB = 100 MB/sec

Storage:
Hot (30 days): 300 TB
Cold (1 year): 3.6 PB (S3)

Elasticsearch:
100 shards × 3 GB = 300 GB per day
30 days: 9 TB (with replication: 18 TB)
```

**Key challenges:** Parsing, enrichment, retention, search performance!
