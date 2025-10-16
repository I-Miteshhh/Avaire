# Design Metrics & Monitoring Platform - Complete System Design

**Difficulty:** ⭐⭐⭐⭐⭐  
**Interview Frequency:** High (All tech companies, 40 LPA+)  
**Time to Complete:** 35-40 minutes  
**Real-World Examples:** Prometheus, Datadog, New Relic, Grafana Cloud

---

## 📋 Problem Statement

**Design a metrics monitoring platform that can:**
- Collect 10 million metrics per second
- Support multi-dimensional time series (labels/tags)
- Provide sub-second query latency
- Store metrics for 90 days
- Support alerting rules (threshold, anomaly detection)
- Handle cardinality explosion (avoid too many unique time series)
- Provide dashboards and visualizations
- Support distributed tracing integration
- Auto-discover services

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                  METRIC TYPES & DATA MODEL                    │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  1. COUNTER (monotonically increasing)                       │
│     http_requests_total{method="GET", status="200"} 1523    │
│     ↑ only goes up, rate() used for queries                 │
│                                                               │
│  2. GAUGE (can go up or down)                                │
│     memory_usage_bytes{host="web-1"} 4294967296             │
│     ↑ current value                                          │
│                                                               │
│  3. HISTOGRAM (distribution)                                  │
│     http_request_duration_seconds_bucket{le="0.1"} 100      │
│     http_request_duration_seconds_bucket{le="0.5"} 250      │
│     http_request_duration_seconds_bucket{le="1.0"} 300      │
│     ↑ percentiles, quantiles                                 │
│                                                               │
│  4. SUMMARY (similar to histogram, client-side)              │
│     http_request_duration_seconds{quantile="0.95"} 0.8      │
│                                                               │
│  Time Series Format:                                         │
│  metric_name{label1="value1", label2="value2"} value timestamp│
│  http_requests_total{method="POST", path="/api"} 42 1640000000│
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                   COLLECTION ARCHITECTURE                     │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              PUSH MODEL (StatsD/Telegraf)               ││
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━││
│  │                                                         ││
│  │  Application → UDP → StatsD Agent → Aggregator        ││
│  │                                                         ││
│  │  Pros: Simple, low overhead                            ││
│  │  Cons: Fire-and-forget (data loss possible)            ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              PULL MODEL (Prometheus)                    ││
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━││
│  │                                                         ││
│  │  ┌──────────┐         ┌──────────┐                     ││
│  │  │   App    │         │Prometheus│                     ││
│  │  │ /metrics │ ← scrape│ Server   │                     ││
│  │  │ endpoint │         │          │                     ││
│  │  └──────────┘         └──────────┘                     ││
│  │                                                         ││
│  │  Scrape config:                                         ││
│  │  scrape_interval: 15s                                   ││
│  │  scrape_timeout: 10s                                    ││
│  │                                                         ││
│  │  Pros: Service discovery, guaranteed delivery           ││
│  │  Cons: Targets must expose HTTP endpoint               ││
│  └─────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│            PROMETHEUS ARCHITECTURE (PULL MODEL)               │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  SERVICE DISCOVERY                                     │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  Kubernetes SD:                                        │ │
│  │  - kubernetes_sd_configs:                             │ │
│  │      role: pod                                         │ │
│  │      namespaces: [production, staging]                │ │
│  │                                                        │ │
│  │  Discovered targets:                                   │ │
│  │  - web-server-1:8080/metrics                          │ │
│  │  - web-server-2:8080/metrics                          │ │
│  │  - db-server-1:9104/metrics                           │ │
│  └────────────────────────────────────────────────────────┘ │
│            │                                                  │
│            ▼                                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  SCRAPER                                               │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  Every 15 seconds:                                     │ │
│  │  1. HTTP GET /metrics                                  │ │
│  │  2. Parse Prometheus text format                       │ │
│  │  3. Add metadata (job, instance)                       │ │
│  │  4. Write to TSDB                                      │ │
│  └────────────────────────────────────────────────────────┘ │
│            │                                                  │
│            ▼                                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  TSDB (Time Series Database)                          │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  Storage format (Chunks):                             │ │
│  │  ┌───────────────────────────────────────────────┐   │ │
│  │  │ Time Series: http_requests_total{...}         │   │ │
│  │  │ ┌───────────────────────────────────────────┐ │   │ │
│  │  │ │ t0: 100  t1: 105  t2: 110  t3: 120       │ │   │ │
│  │  │ │ (delta-of-delta encoding, XOR)            │ │   │ │
│  │  │ └───────────────────────────────────────────┘ │   │ │
│  │  └───────────────────────────────────────────────┘   │ │
│  │                                                        │ │
│  │  Compression: ~1.3 bytes per sample                   │ │
│  │  Retention: 90 days (WAL + blocks)                    │ │
│  └────────────────────────────────────────────────────────┘ │
│            │                                                  │
│            ▼                                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  QUERY ENGINE (PromQL)                                │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  Query:                                                │ │
│  │  rate(http_requests_total[5m])                        │ │
│  │                                                        │ │
│  │  1. Fetch samples for last 5 minutes                  │ │
│  │  2. Calculate rate (delta / time)                     │ │
│  │  3. Return time series                                │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                    ALERTING SYSTEM                            │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Alert Rule (YAML):                                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  - alert: HighErrorRate                                │ │
│  │    expr: |                                             │ │
│  │      sum(rate(http_requests_total{status=~"5.."}[5m]))│ │
│  │      /                                                  │ │
│  │      sum(rate(http_requests_total[5m]))               │ │
│  │      > 0.05                                            │ │
│  │    for: 10m                                            │ │
│  │    labels:                                             │ │
│  │      severity: critical                                │ │
│  │    annotations:                                        │ │
│  │      summary: High error rate detected                 │ │
│  └────────────────────────────────────────────────────────┘ │
│            │                                                  │
│            ▼                                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  ALERTMANAGER                                          │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  1. Deduplication (same alert from multiple sources)  │ │
│  │  2. Grouping (batch similar alerts)                   │ │
│  │  3. Inhibition (suppress dependent alerts)            │ │
│  │  4. Routing (PagerDuty, Slack, email)                 │ │
│  │  5. Silencing (maintenance windows)                   │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## 💻 Implementation

### **1. Metrics Instrumentation (Python)**

```python
from prometheus_client import Counter, Gauge, Histogram, Summary, CollectorRegistry
import time

# Create registry
registry = CollectorRegistry()

# Define metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=registry
)

active_users = Gauge(
    'active_users',
    'Number of active users',
    ['tier'],
    registry=registry
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0],
    registry=registry
)

db_query_duration = Summary(
    'db_query_duration_seconds',
    'Database query duration',
    ['query_type'],
    registry=registry
)


# Use metrics
def handle_request(method: str, endpoint: str):
    """
    Handle HTTP request with metrics
    """
    
    # Start timer
    start = time.time()
    
    try:
        # Process request
        response = process_request(method, endpoint)
        status = response.status_code
        
        # Record success
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()
        
        return response
    
    except Exception as e:
        # Record error
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=500
        ).inc()
        
        raise
    
    finally:
        # Record duration
        duration = time.time() - start
        request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)


def update_active_users(tier: str, count: int):
    """
    Update active users gauge
    """
    active_users.labels(tier=tier).set(count)


### **2. Metrics Exporter (Flask)**

```python
from flask import Flask, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

@app.route('/metrics')
def metrics():
    """
    Prometheus scrape endpoint
    """
    return Response(
        generate_latest(registry),
        mimetype=CONTENT_TYPE_LATEST
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)


### **3. Custom Collector (Advanced)**

```python
from prometheus_client.core import GaugeMetricFamily

class DatabaseStatsCollector:
    """
    Custom collector for database metrics
    """
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def collect(self):
        """
        Called every scrape
        """
        
        # Get DB stats
        stats = self.db.get_stats()
        
        # Connection pool
        pool_metric = GaugeMetricFamily(
            'db_connection_pool_size',
            'Database connection pool size',
            labels=['state']
        )
        pool_metric.add_metric(['active'], stats['active_connections'])
        pool_metric.add_metric(['idle'], stats['idle_connections'])
        yield pool_metric
        
        # Table sizes
        table_metric = GaugeMetricFamily(
            'db_table_size_bytes',
            'Database table size in bytes',
            labels=['table']
        )
        for table, size in stats['table_sizes'].items():
            table_metric.add_metric([table], size)
        yield table_metric


# Register custom collector
from prometheus_client import REGISTRY
REGISTRY.register(DatabaseStatsCollector(db))


### **4. PromQL Queries (for dashboards/alerts)**

```python
"""
Common PromQL queries for monitoring
"""

# Request rate (QPS)
rate_query = """
sum(rate(http_requests_total[5m])) by (method)
"""

# Error rate percentage
error_rate_query = """
sum(rate(http_requests_total{status=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))
* 100
"""

# P95 latency
p95_latency_query = """
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, endpoint)
)
"""

# Memory usage by host
memory_query = """
node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes
"""

# CPU usage
cpu_query = """
100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
"""

# Disk I/O
disk_io_query = """
rate(node_disk_written_bytes_total[5m])
"""


### **5. Alerting Rules**

```python
# Alert configuration (YAML)
alert_rules = """
groups:
  - name: application
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
          /
          sum(rate(http_requests_total[5m]))
          > 0.05
        for: 10m
        labels:
          severity: critical
          team: backend
        annotations:
          summary: "High error rate: {{ $value }}%"
          description: "Error rate is above 5% for 10 minutes"
      
      - alert: HighLatency
        expr: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
          ) > 1.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "P95 latency > 1s"
      
      - alert: HighMemoryUsage
        expr: |
          (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes)
          /
          node_memory_MemTotal_bytes
          > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Memory usage > 90%"

  - name: database
    interval: 60s
    rules:
      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database is down"
      
      - alert: SlowQueries
        expr: rate(db_query_duration_seconds_sum[5m]) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High number of slow queries"
"""


### **6. Grafana Dashboard (JSON)**

```python
dashboard = {
    "dashboard": {
        "title": "Application Metrics",
        "panels": [
            {
                "title": "Request Rate",
                "targets": [
                    {
                        "expr": "sum(rate(http_requests_total[5m])) by (method)",
                        "legendFormat": "{{method}}"
                    }
                ],
                "type": "graph"
            },
            {
                "title": "Error Rate %",
                "targets": [
                    {
                        "expr": """
                            sum(rate(http_requests_total{status=~"5.."}[5m]))
                            /
                            sum(rate(http_requests_total[5m]))
                            * 100
                        """
                    }
                ],
                "type": "singlestat",
                "thresholds": "1,5"
            },
            {
                "title": "P95 Latency",
                "targets": [
                    {
                        "expr": """
                            histogram_quantile(0.95,
                              sum(rate(http_request_duration_seconds_bucket[5m])) by (le, endpoint)
                            )
                        """,
                        "legendFormat": "{{endpoint}}"
                    }
                ],
                "type": "graph"
            }
        ]
    }
}
```

---

## 🎓 Interview Points

**Capacity:**
```
Metrics: 10M/sec
Time series: 1M unique series
Sample size: 16 bytes (timestamp + value)

Storage:
10M samples/sec × 16 bytes = 160 MB/sec
Compressed (1.3 bytes): 13 MB/sec
90 days: 101 TB → compressed: 8.3 TB

Query: <100ms for 1-hour range scan
```

**Key design choices:** Pull vs push, cardinality management, retention, compression!
