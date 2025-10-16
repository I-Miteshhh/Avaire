# Design Service Mesh Observability - Complete System Design

**Difficulty:** ⭐⭐⭐⭐⭐  
**Interview Frequency:** High (Senior/Staff roles, 40 LPA+)  
**Time to Complete:** 40-45 minutes  
**Real-World Examples:** Istio, Linkerd, Envoy, Consul

---

## 📋 Problem Statement

**Design observability for a service mesh that can:**
- Monitor 10,000 microservices
- Track 1 million requests per second
- Provide distributed tracing across services
- Measure service-to-service latency
- Monitor service mesh control plane health
- Support traffic shaping metrics (retries, timeouts, circuit breakers)
- Provide service dependency visualization
- Track mTLS certificate expiration
- Alert on service mesh configuration issues
- Support multi-cluster observability

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                  SERVICE MESH ARCHITECTURE                    │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                   DATA PLANE (Envoy Sidecar)            ││
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━││
│  │                                                         ││
│  │  Pod: frontend-service                                 ││
│  │  ┌───────────────────────────────────────────────────┐││
│  │  │ ┌──────────────┐     ┌──────────────┐           │││
│  │  │ │              │     │    Envoy     │           │││
│  │  │ │  Container   │────▶│   Sidecar    │───────┐   │││
│  │  │ │ (app logic)  │     │   Proxy      │       │   │││
│  │  │ │              │◀────│              │       │   │││
│  │  │ └──────────────┘     └──────┬───────┘       │   │││
│  │  │                             │                │   │││
│  │  │                             ▼                │   │││
│  │  │                    ┌─────────────────┐      │   │││
│  │  │                    │  TELEMETRY:     │      │   │││
│  │  │                    │  ━━━━━━━━━━━━━  │      │   │││
│  │  │                    │  - Metrics      │      │   │││
│  │  │                    │  - Traces       │      │   │││
│  │  │                    │  - Access logs  │      │   │││
│  │  │                    └─────────────────┘      │   │││
│  │  └───────────────────────────────────────────────────┘││
│  │                                                         ││
│  │  Envoy Stats (Prometheus format):                     ││
│  │  envoy_cluster_upstream_rq_total{cluster="backend"}   ││
│  │  envoy_cluster_upstream_rq_time{cluster="backend"}    ││
│  │  envoy_cluster_upstream_rq_xx{cluster="backend",      ││
│  │                                response_code_class="5"}││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │               CONTROL PLANE (Istio/Linkerd)             ││
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━││
│  │                                                         ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   ││
│  │  │   Pilot     │  │   Citadel   │  │   Mixer     │   ││
│  │  │ (config)    │  │   (mTLS)    │  │ (telemetry) │   ││
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘   ││
│  │         │                │                │            ││
│  │         └────────────────┼────────────────┘            ││
│  │                          │                              ││
│  │                          ▼                              ││
│  │              ┌───────────────────────┐                 ││
│  │              │   Configuration:      │                 ││
│  │              │   - VirtualService    │                 ││
│  │              │   - DestinationRule   │                 ││
│  │              │   - ServiceEntry      │                 ││
│  │              │   - Gateway           │                 ││
│  │              └───────────────────────┘                 ││
│  └─────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│             DISTRIBUTED TRACING (Jaeger/Zipkin)               │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Request flow:                                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Trace ID: abc123                                       ││
│  │                                                          ││
│  │  ┌────────────────────────────────────────────────────┐││
│  │  │ Span 1: frontend → backend                         │││
│  │  │ trace_id: abc123                                   │││
│  │  │ span_id: span1                                     │││
│  │  │ parent_span_id: null                               │││
│  │  │ duration: 150ms                                    │││
│  │  │ tags: {http.method: GET, http.status_code: 200}  │││
│  │  └────────────────────────────────────────────────────┘││
│  │           │                                             ││
│  │           ▼                                             ││
│  │  ┌────────────────────────────────────────────────────┐││
│  │  │ Span 2: backend → database                         │││
│  │  │ trace_id: abc123                                   │││
│  │  │ span_id: span2                                     │││
│  │  │ parent_span_id: span1                              │││
│  │  │ duration: 50ms                                     │││
│  │  │ tags: {db.type: postgres, db.statement: SELECT...}│││
│  │  └────────────────────────────────────────────────────┘││
│  │           │                                             ││
│  │           ▼                                             ││
│  │  ┌────────────────────────────────────────────────────┐││
│  │  │ Span 3: backend → cache                            │││
│  │  │ trace_id: abc123                                   │││
│  │  │ span_id: span3                                     │││
│  │  │ parent_span_id: span1                              │││
│  │  │ duration: 10ms                                     │││
│  │  │ tags: {cache.hit: true, cache.key: user:123}      │││
│  │  └────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  Visualization (Jaeger UI):                                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  frontend ████████████████████████ 150ms               ││
│  │    ├─ backend ██████████ 50ms                          ││
│  │    │    └─ database ███ 30ms                           ││
│  │    └─ cache ██ 10ms                                    ││
│  └─────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                   SERVICE MESH METRICS                        │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  1. GOLDEN SIGNALS                                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Latency (P50, P95, P99):                             │ │
│  │  histogram_quantile(0.95,                             │ │
│  │    sum(rate(                                          │ │
│  │      istio_request_duration_milliseconds_bucket[5m]  │ │
│  │    )) by (le, destination_service)                    │ │
│  │  )                                                     │ │
│  │                                                        │ │
│  │  Traffic (requests/sec):                              │ │
│  │  sum(rate(                                            │ │
│  │    istio_requests_total[5m]                           │ │
│  │  )) by (destination_service)                          │ │
│  │                                                        │ │
│  │  Errors (error rate %):                               │ │
│  │  sum(rate(                                            │ │
│  │    istio_requests_total{response_code=~"5.."}[5m]    │ │
│  │  ))                                                    │ │
│  │  /                                                     │ │
│  │  sum(rate(istio_requests_total[5m]))                 │ │
│  │  * 100                                                │ │
│  │                                                        │ │
│  │  Saturation (CPU/memory):                             │ │
│  │  container_memory_usage_bytes{                        │ │
│  │    pod=~".*-envoy-.*"                                 │ │
│  │  }                                                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  2. SERVICE-TO-SERVICE METRICS                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Request rate by source/destination:                  │ │
│  │  sum(rate(                                            │ │
│  │    istio_requests_total[5m]                           │ │
│  │  )) by (source_service, destination_service)          │ │
│  │                                                        │ │
│  │  Circuit breaker trips:                               │ │
│  │  sum(increase(                                        │ │
│  │    envoy_cluster_upstream_rq_pending_overflow[5m]    │ │
│  │  )) by (cluster)                                      │ │
│  │                                                        │ │
│  │  Retry rate:                                          │ │
│  │  sum(rate(                                            │ │
│  │    envoy_cluster_upstream_rq_retry[5m]               │ │
│  │  )) by (cluster)                                      │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  3. MTLS METRICS                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Certificate expiration:                              │ │
│  │  (envoy_server_days_until_first_cert_expiring < 30)  │ │
│  │                                                        │ │
│  │  mTLS enforcement:                                    │ │
│  │  sum(rate(                                            │ │
│  │    istio_requests_total{                              │ │
│  │      connection_security_policy="mutual_tls"          │ │
│  │    }[5m]                                              │ │
│  │  ))                                                    │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## 💻 Implementation

### **1. Envoy Metrics Exporter**

```python
from prometheus_client import Counter, Histogram, Gauge
import time

class EnvoyMetrics:
    """
    Custom metrics for Envoy sidecar
    """
    
    def __init__(self):
        # Request metrics
        self.requests_total = Counter(
            'envoy_cluster_upstream_rq_total',
            'Total requests to upstream cluster',
            ['cluster', 'response_code']
        )
        
        # Latency histogram
        self.request_duration = Histogram(
            'envoy_cluster_upstream_rq_time',
            'Request duration in milliseconds',
            ['cluster'],
            buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000]
        )
        
        # Active connections
        self.active_connections = Gauge(
            'envoy_cluster_upstream_cx_active',
            'Active connections to upstream',
            ['cluster']
        )
        
        # Circuit breaker
        self.circuit_breaker_open = Gauge(
            'envoy_cluster_circuit_breakers_open',
            'Circuit breaker state (1=open, 0=closed)',
            ['cluster']
        )
    
    def record_request(self, cluster: str, response_code: int, duration_ms: float):
        """
        Record request metrics
        """
        
        # Increment counter
        self.requests_total.labels(
            cluster=cluster,
            response_code=response_code
        ).inc()
        
        # Record latency
        self.request_duration.labels(cluster=cluster).observe(duration_ms)


### **2. Distributed Tracing Integration**

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Setup Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name='jaeger-agent',
    agent_port=6831
)

# Configure tracer
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)
trace.set_tracer_provider(tracer_provider)

tracer = trace.get_tracer(__name__)


def handle_request_with_tracing(request):
    """
    Handle request with distributed tracing
    """
    
    # Extract trace context from headers
    parent_ctx = extract_trace_context(request.headers)
    
    # Start span
    with tracer.start_as_current_span(
        'frontend-service',
        context=parent_ctx,
        kind=trace.SpanKind.SERVER
    ) as span:
        
        # Add attributes
        span.set_attribute('http.method', request.method)
        span.set_attribute('http.url', request.url)
        span.set_attribute('http.target', request.path)
        
        try:
            # Call downstream service
            response = call_backend_service(span)
            
            # Record response
            span.set_attribute('http.status_code', response.status_code)
            
            return response
        
        except Exception as e:
            # Record error
            span.set_status(trace.Status(trace.StatusCode.ERROR))
            span.record_exception(e)
            raise


def call_backend_service(parent_span):
    """
    Call backend with trace propagation
    """
    
    with tracer.start_as_current_span(
        'call-backend',
        kind=trace.SpanKind.CLIENT
    ) as span:
        
        # Inject trace context into headers
        headers = {}
        inject_trace_context(headers)
        
        # Make HTTP request
        response = requests.get(
            'http://backend-service/api',
            headers=headers
        )
        
        return response


### **3. Service Dependency Graph**

```python
from collections import defaultdict
import networkx as nx

class ServiceDependencyGraph:
    """
    Build service dependency graph from traces
    """
    
    def __init__(self, jaeger_client):
        self.jaeger = jaeger_client
        self.graph = nx.DiGraph()
    
    def build_graph(self, lookback_hours: int = 24):
        """
        Build dependency graph from recent traces
        """
        
        # Query traces
        traces = self.jaeger.search_traces(
            service='*',
            lookback=f'{lookback_hours}h'
        )
        
        # Extract dependencies
        for trace in traces:
            self._process_trace(trace)
        
        return self.graph
    
    def _process_trace(self, trace):
        """
        Extract service dependencies from trace
        """
        
        # Build span tree
        spans_by_id = {span.span_id: span for span in trace.spans}
        
        for span in trace.spans:
            if span.parent_span_id:
                parent = spans_by_id.get(span.parent_span_id)
                
                if parent:
                    # Add edge: parent_service → current_service
                    self.graph.add_edge(
                        parent.service_name,
                        span.service_name,
                        weight=self.graph.get_edge_data(
                            parent.service_name,
                            span.service_name,
                            default={'weight': 0}
                        )['weight'] + 1
                    )
    
    def get_critical_path(self, start_service: str, end_service: str):
        """
        Find critical path between services
        """
        
        try:
            path = nx.shortest_path(
                self.graph,
                source=start_service,
                target=end_service,
                weight='weight'
            )
            return path
        except nx.NetworkXNoPath:
            return None
    
    def visualize(self):
        """
        Generate GraphViz visualization
        """
        
        import matplotlib.pyplot as plt
        
        pos = nx.spring_layout(self.graph)
        nx.draw(
            self.graph,
            pos,
            with_labels=True,
            node_color='lightblue',
            node_size=1500,
            font_size=10,
            arrows=True
        )
        
        plt.savefig('service_graph.png')


### **4. Service Mesh Alerting**

```python
"""
Prometheus alert rules for service mesh
"""

service_mesh_alerts = """
groups:
  - name: istio
    interval: 30s
    rules:
      - alert: HighServiceLatency
        expr: |
          histogram_quantile(0.95,
            sum(rate(istio_request_duration_milliseconds_bucket[5m]))
            by (le, destination_service)
          ) > 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High P95 latency for {{ $labels.destination_service }}"
          description: "P95 latency is {{ $value }}ms"
      
      - alert: HighErrorRate
        expr: |
          sum(rate(istio_requests_total{response_code=~"5.."}[5m]))
          by (destination_service)
          /
          sum(rate(istio_requests_total[5m]))
          by (destination_service)
          > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate for {{ $labels.destination_service }}"
      
      - alert: CircuitBreakerTripped
        expr: |
          sum(increase(envoy_cluster_upstream_rq_pending_overflow[5m]))
          by (cluster) > 10
        labels:
          severity: warning
        annotations:
          summary: "Circuit breaker tripped for {{ $labels.cluster }}"
      
      - alert: CertificateExpiringSoon
        expr: envoy_server_days_until_first_cert_expiring < 30
        labels:
          severity: warning
        annotations:
          summary: "mTLS certificate expiring in {{ $value }} days"
      
      - alert: SidecarCrashLooping
        expr: |
          rate(kube_pod_container_status_restarts_total{
            container="istio-proxy"
          }[15m]) > 0
        labels:
          severity: critical
        annotations:
          summary: "Envoy sidecar crash looping"
"""


### **5. Multi-Cluster Observability**

```python
class MultiClusterObservability:
    """
    Federate metrics across multiple clusters
    """
    
    def __init__(self, cluster_endpoints: dict):
        self.clusters = cluster_endpoints
    
    def query_all_clusters(self, promql: str):
        """
        Query Prometheus in all clusters
        """
        
        results = {}
        
        for cluster_name, endpoint in self.clusters.items():
            prom = PrometheusClient(endpoint)
            result = prom.query(promql)
            results[cluster_name] = result
        
        return results
    
    def aggregate_metrics(self, metric_name: str):
        """
        Aggregate same metric across clusters
        """
        
        promql = f'sum({metric_name}) by (destination_service)'
        
        cluster_results = self.query_all_clusters(promql)
        
        # Combine results
        aggregated = defaultdict(float)
        
        for cluster, results in cluster_results.items():
            for result in results:
                service = result['metric']['destination_service']
                value = float(result['value'][1])
                aggregated[service] += value
        
        return dict(aggregated)
```

---

## 🎓 Interview Points

**Capacity:**
```
Services: 10K
Requests: 1M/sec
Traces: 1% sampling = 10K traces/sec
Spans: avg 5 spans/trace = 50K spans/sec

Storage:
Spans: 50K/sec × 1KB = 50 MB/sec
Retention: 7 days = 30 TB

Metrics: 100K time series
```

**Key concepts:** Sidecar pattern, distributed tracing, service graph, golden signals, mTLS observability!

🎉 **ALL 20 SCENARIOS COMPLETE!**