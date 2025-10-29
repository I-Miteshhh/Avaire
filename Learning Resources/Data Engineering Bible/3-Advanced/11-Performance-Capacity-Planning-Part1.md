# Performance & Capacity Planning - Part 1 (Sections 0–11)

## 0. Executive Snapshot (Strategic Foundation)
Performance and capacity planning is not reactive monitoring—it is predictive engineering that models system behavior, prevents resource starvation, and optimizes cost per throughput unit. The failure mode is over-provisioning for peak scenarios that happen <5% of the time versus under-provisioning causing SLA breaches and customer churn.

| Objective | Business Impact | Engineering Lever | Success Metric | Annualized Value (Illustrative) |
|-----------|-----------------|-------------------|----------------|----------------------------------|
| Right-Size Compute Resources | Eliminate waste from over-provisioning | Dynamic scaling policies + workload classification | 15–25% infrastructure cost reduction | $180K (petabyte-scale platform) |
| Prevent Capacity Cliff Incidents | Avoid revenue loss from system saturation | Proactive capacity alerts + runway modeling | Zero capacity-driven outages >15min | $2.4M (revenue protection, SLA credits avoided) |
| Optimize Latency Distribution | Improve user experience + reduce timeouts | P95/P99 latency budgets + tail latency optimization | P95 <SLA threshold 99.5% of time | $400K (conversion rate + retention) |
| Enable Predictable Scaling | Support business growth without performance surprise | Capacity forecasting models + load testing automation | Scaling decisions made 2+ weeks before need | $120K (prevent emergency scaling premium) |
| Multi-Workload Resource Efficiency | Maximize cluster utilization via intelligent scheduling | Workload classification + bin packing optimization | Average CPU utilization >65% (vs <45% naive) | $300K (infrastructure efficiency) |

Strategic Principle: Model first, measure second, optimize third. Build capacity planning as a feedback loop: forecast → provision → observe → refine model → forecast.

---

## 1. ELI10 Analogy
Imagine you run a pizza restaurant. You need enough ovens (compute), ingredients (memory), and delivery drivers (network) to handle customers. If you only prepare for quiet Tuesday but get Saturday rush, customers wait forever and leave angry. If you always prepare for Saturday, you waste money heating empty ovens Tuesday through Thursday. Good capacity planning is like having a crystal ball that tells you "next Tuesday will be busy because there's a football game, so pre-heat 2 extra ovens but don't order extra cheese until Thursday when the big party calls in."

Performance planning adds: "measure how long each pizza type takes to cook (latency), track how many you can make per hour (throughput), and when ovens get full, prioritize the orders that make the most money (workload classification)."

---

## 2. Problem Framing (Why Capacity Planning Fails)
Common patterns causing performance incidents and resource waste:
1. Reactive Scaling: Adding capacity only after alerts fire → SLA breach windows during scale-up delay.
2. Linear Growth Assumptions: Expecting smooth 2× data growth but getting 10× spikes during viral events or data backfills.
3. Hidden Resource Contention: CPU looks fine but memory fragmentation or disk IO queuing causes tail latencies.
4. Workload Interference: Batch jobs consuming resources during interactive query peak hours.
5. Synthetic Load Testing Gaps: Load tests miss real traffic patterns (bursty, skewed distributions, cascading failures).
6. Ignoring Degradation Curves: Assuming performance stays flat until saturation cliff—reality shows gradual degradation starting at 60% utilization.
7. Single-Point Sizing: Optimizing for average case while ignoring P95/P99 scenarios that determine user experience.
8. Seasonal & Event Blindness: Missing predictable traffic patterns (Black Friday, quarter-end reports, compliance deadlines).
9. Capacity Model Staleness: Models not updated when code changes or data distributions shift.
10. Cross-Service Dependencies: Focusing on one service while upstream/downstream services become bottlenecks.

---

## 3. Core Concepts & Terminology
| Concept | Definition | Capacity Planning Role | Principal Architect Insight |
|---------|------------|------------------------|----------------------------|
| Latency (P50/P95/P99) | Time to complete single request at percentile | Sets SLA targets; P99 drives tail experience | P99 often dominated by queuing theory vs algorithm; optimize queues not just code |
| Throughput (RPS/QPS) | Requests processed per unit time | Determines scale-up triggers | Throughput often plateaus before CPU saturation due to contention |
| Utilization | % of resource capacity consumed | Early warning signal for scaling | Sweet spot typically 60–70%; above triggers degradation |
| Saturation | Resource exhaustion causing queuing delays | Capacity cliff prevention | Measure queue depths not just utilization |
| Little's Law | Concurrency = Throughput × Latency | Relates service metrics to user experience | Validates capacity model math; useful for queue sizing |
| Amdahl's Law | Speedup limited by sequential bottleneck portion | Guides parallelization investment | Identifies where adding cores/nodes won't help |
| Universal Scalability Law | Models throughput degradation with contention + coherency overhead | Predicts scaling limits | More realistic than linear scaling assumptions |
| Workload Classification | Categorizing requests by resource consumption pattern | Enables priority-based scheduling | Interactive vs batch vs ML training have different SLA needs |
| Capacity Runway | Time until resource exhaustion at current growth rate | Triggers proactive scaling | Must account for lead time: provision lag + scaling delay |
| Load Testing | Synthetic traffic generation to validate capacity | Proves scaling assumptions before production | Combine steady-state + spike + soak testing patterns |
| Auto-Scaling Policy | Rules governing when/how to add/remove resources | Maintains performance within cost constraints | Trade-off: reaction speed vs cost efficiency vs stability |
| Resource Packing | Efficient allocation of heterogeneous workloads to nodes | Maximizes infrastructure ROI | Bin packing with constraints (memory, CPU, IO) |
| Performance Budget | Allowable latency/throughput degradation for features | Prevents performance regression | Link to business metrics (conversion, engagement) |
| Circuit Breaker | Fail-fast pattern to prevent cascade overload | Protects capacity during incidents | Essential for multi-service capacity planning |

---

## 4. Architecture Overview (Performance & Capacity Platform)

```
                   +----------------------------------------------+
                   |          Business Intelligence Layer         |
                   |  (Growth Forecasts, Event Calendar,         |
                   |   Cost/Performance Trade-off Dashboard)     |
                   +----------------------+-----------------------+
                                          |
          +----------------------------------+----------------------------------+
          |               Capacity Planning Engine                            |
          |  • Models (Universal Scalability Law, Linear/Polynomial Growth)  |
          |  • Forecasting (Time Series, Regression, Event-Driven)          |
          |  • Optimization (Cost vs Performance, Multi-Objective)          |
          +----------------------------------+----------------------------------+
                                          |
                   +----------------------+-----------------------+
                   |       Control Loop (Scaling Decisions)      |
                   +----------------------+-----------------------+
                                          |
      +-----------------+-----------------+-----------------+-----------------+
      |  Workload       |   Resource      |  Performance    |   Cost          |
      |  Classification |   Monitoring    |  Observability  |   Attribution   |
      +-----------------+-----------------+-----------------+-----------------+
              |                 |                 |                 |
      +-----------------+-----------------+-----------------+-----------------+
      |  Data Platform Infrastructure (Spark, Kafka, Storage, Network)      |
      +---------------------------------------------------------------------+
```

Control Flow:
1. **Telemetry Collection**: Metrics, traces, resource utilization, business events gathered real-time.
2. **Workload Classification**: Tag requests by priority (interactive, batch, ML) and resource profile (CPU-bound, memory-bound, IO-bound).
3. **Performance Modeling**: Apply Universal Scalability Law, queueing theory, regression models to predict capacity needs.
4. **Forecast Integration**: Combine historical trends with business event calendar (product launches, seasonal spikes).
5. **Multi-Objective Optimization**: Balance cost (minimize resources) vs performance (maintain SLA) vs agility (fast scaling response).
6. **Control Loop Execution**: Auto-scaling triggers, pre-provisioning for events, workload scheduling.
7. **Feedback Refinement**: Compare predictions vs actual usage; retrain models monthly.

---

## 5. Performance Modeling Deep Dive
### Universal Scalability Law (USL)
Standard form: `Throughput(N) = N / (1 + α(N-1) + βN(N-1))`
- N = number of workers/cores
- α = contention coefficient (serialization)
- β = coherency coefficient (data synchronization)

**Why USL Over Linear Scaling**: Accounts for real-world degradation as system size increases.

Practical Application:
```python
def usl_throughput(N, alpha, beta):
    return N / (1 + alpha * (N - 1) + beta * N * (N - 1))

# Example: Spark cluster scaling
alpha = 0.05  # 5% serialization overhead
beta = 0.001  # 0.1% coherency cost per node
optimal_N = int(1 / (2 * beta))  # ~316 cores theoretical max
```

**Capacity Decision**: Adding cores beyond optimal point reduces throughput due to coordination overhead.

### Little's Law Applications
`Concurrency = Throughput × Response Time`

Use Case: Size connection pools, queue depths, request rate limits.
```python
target_rps = 1000
target_latency_ms = 200
required_concurrency = target_rps * (target_latency_ms / 1000)  # 200 concurrent requests
```

### Queuing Theory (M/M/c Model)
For service with Poisson arrivals, exponential service times, c servers:
```python
import math

def mm_c_wait_time(arrival_rate, service_rate, servers):
    utilization = arrival_rate / (service_rate * servers)
    if utilization >= 1:
        return float('inf')  # System unstable
    
    # Erlang C formula for wait time
    erlang_c = (utilization**servers / math.factorial(servers)) / \
               sum((utilization**k / math.factorial(k)) for k in range(servers + 1))
    
    return erlang_c / (servers * service_rate - arrival_rate)
```

**Insight**: Wait time increases exponentially near 100% utilization; keep systems <75% loaded.

---

## 6. Capacity Formulas & Sizing Models
| Resource Type | Formula | Input Variables | Output | Use Case |
|---------------|---------|-----------------|---------|----------|
| CPU (General) | `required_cores = (RPS × CPU_per_request) / (target_util × cores_per_node)` | RPS, CPU/req, target util, cores/node | Node count | Web services, APIs |
| Memory (Spark) | `executor_memory = (input_data_size × expansion_factor) / parallelism` | Data size, expansion (2-4×), tasks | Memory per executor | ETL jobs |
| Storage (IOPS) | `required_iops = (write_rps × iops_per_write) + (read_rps × iops_per_read)` | Read/write rates, IOPS cost | Total IOPS | Database, queue backends |
| Network | `bandwidth_gbps = (message_rate × avg_message_size × 8) / 1e9` | Msg/sec, size bytes | Network capacity | Kafka, streaming |
| Kafka Partitions | `partitions = max(target_throughput / partition_limit, consumer_count)` | Target MB/s, limit, consumers | Partition count | Event streaming |
| Connection Pool | `pool_size = (peak_rps × avg_query_time) × safety_margin` | RPS, query latency, margin | Pool connections | Database access |
| Cache Hit Ratio | `required_cache_size = working_set_size × (1 - acceptable_miss_rate)` | Working set, miss tolerance | Cache memory | Redis, memcached |

### Spark-Specific Sizing
```python
def spark_sizing(input_gb, transformation_factor=3, target_task_size_mb=128):
    """
    Size Spark cluster for ETL job
    
    Args:
        input_gb: Input data size
        transformation_factor: Data expansion during processing (shuffles, joins)
        target_task_size_mb: Optimal task size for parallelism
    """
    expanded_data_gb = input_gb * transformation_factor
    tasks_needed = (expanded_data_gb * 1024) // target_task_size_mb
    
    # Sizing recommendations
    executor_memory_gb = max(4, expanded_data_gb / tasks_needed * 2)  # 2× safety margin
    executor_cores = min(5, max(2, tasks_needed // 100))  # 2-5 cores sweet spot
    num_executors = tasks_needed // executor_cores
    
    return {
        'executors': num_executors,
        'executor_memory_gb': executor_memory_gb,
        'executor_cores': executor_cores,
        'total_memory_gb': num_executors * executor_memory_gb,
        'estimated_duration_min': input_gb / 10  # Rough throughput estimate
    }
```

---

## 7. Auto-Scaling Strategies & Policies
| Strategy | Trigger | Scaling Speed | Use Case | Trade-off |
|----------|---------|---------------|----------|-----------|
| Reactive (Threshold) | CPU/Memory >70% for 5min | Medium (2-5min) | General web services | Simple but may lag spikes |
| Predictive (Time-Based) | Calendar events, historical patterns | Fast (pre-provision) | Known traffic patterns | Higher cost during false predictions |
| Hybrid (ML + Reactive) | ML forecast + threshold fallback | Fast + reliable | Complex applications | Requires training data |
| Multi-Metric | CPU AND queue depth AND latency | Balanced | Mission-critical services | More complex tuning |
| Cascading (Service Mesh) | Upstream service scaling triggers downstream | Coordinated | Microservices architecture | Potential cascade overreaction |

### Auto-Scaling Policy Template
```yaml
scaling_policy:
  scale_up:
    triggers:
      - metric: cpu_utilization
        threshold: 70
        duration: 300s
      - metric: request_queue_depth
        threshold: 100
        duration: 60s
    actions:
      - increase_instances: 2
      - max_increase: 50%
      - cooldown: 300s
  
  scale_down:
    triggers:
      - metric: cpu_utilization
        threshold: 30
        duration: 900s  # Longer cooldown for scale-down
    actions:
      - decrease_instances: 1
      - min_instances: 2
      - cooldown: 600s
```

### Workload-Aware Scaling
```python
class WorkloadScaler:
    def should_scale(self, metrics, workload_type):
        if workload_type == 'interactive':
            return metrics['p95_latency'] > 200  # Latency-sensitive
        elif workload_type == 'batch':
            return metrics['cpu_util'] > 85     # Throughput-focused
        elif workload_type == 'ml_training':
            return metrics['gpu_util'] > 90     # GPU-bound
        return False
```

---

## 8. Failure Modes (Performance & Capacity)
| Failure Mode | Symptom | Root Cause | Detection | Mitigation | Prevention |
|--------------|---------|-----------|----------|-----------|-----------|
| Capacity Cliff | Sudden performance collapse | Resource exhaustion triggers cascading failure | Utilization >90% + latency spike | Emergency scale-up + circuit breakers | Scaling triggers at 70% not 90% |
| Memory Leak Growth | Gradual memory increase | Unclosed resources or reference cycles | Memory growth trend analysis | Restart affected services | Automated memory profiling + alerts |
| Thrashing (GC/Swap) | High CPU but low useful work | Memory pressure causing excessive GC | GC time >10% total time | Increase heap size or reduce load | Memory sizing formulas + monitoring |
| Hot Partition/Skew | Uneven load distribution | Data/request skew concentrated on subset | Max partition load >> avg partition load | Repartition/rebalance + request routing | Hash function analysis + proactive rebalancing |
| Connection Pool Exhaustion | Request timeouts despite low CPU | All connections busy waiting | Connection pool stats + queue depth | Increase pool size or reduce query time | Pool sizing formula + connection leak detection |
| Network Bandwidth Saturation | Packet loss, high latency | Network interface limits exceeded | Network utilization metrics | Traffic shaping + scale network | Bandwidth capacity planning |
| Context Switching Overhead | High CPU, low application throughput | Too many threads for available cores | Context switch rate metrics | Reduce thread pools | Thread pool sizing guidelines |
| Lock Contention | Thread blocking, uneven CPU | Shared resource serialization | Lock wait time metrics | Lock-free data structures + partitioning | Concurrency profiling + design review |
| Cache Stampede | Downstream overload on cache miss | Multiple requests refill same cache key | Cache miss rate spike + downstream load | Cache warming + probabilistic early expiration | Cache sizing + TTL optimization |
| Thundering Herd | System overload after downtime | All clients reconnect simultaneously | Connection rate spike after outage | Connection backoff + rate limiting | Graceful degradation + jitter |

---

## 9. Benchmarking Foundations
### Synthetic Load Generation
Realistic load testing requires modeling actual traffic patterns, not just steady-state throughput.

Traffic Patterns to Model:
```python
import numpy as np

def generate_realistic_load(duration_minutes):
    """Generate traffic pattern mimicking real user behavior"""
    time_points = np.arange(0, duration_minutes * 60, 1)
    
    # Base load with diurnal pattern
    base_rps = 100 + 50 * np.sin(2 * np.pi * time_points / (24 * 3600))
    
    # Add spiky traffic (viral events, marketing campaigns)
    spikes = np.random.poisson(0.01, len(time_points)) * 500
    
    # Add background batch job load
    batch_load = 20 if time_points % 3600 < 1800 else 0  # 30min every hour
    
    return base_rps + spikes + batch_load
```

### Benchmark Harness Design
```python
class PerformanceBenchmark:
    def __init__(self, target_endpoint, workload_profile):
        self.endpoint = target_endpoint
        self.profile = workload_profile
        
    def run_benchmark(self, duration_minutes=10):
        results = {
            'latency_p50': [],
            'latency_p95': [],
            'latency_p99': [],
            'throughput_rps': [],
            'error_rate': [],
            'cpu_utilization': [],
            'memory_usage': []
        }
        
        for minute in range(duration_minutes):
            target_rps = self.profile.get_rps(minute)
            minute_results = self.execute_load(target_rps, duration=60)
            
            for metric, value in minute_results.items():
                results[metric].append(value)
                
        return self.analyze_results(results)
```

### Load Testing Patterns
| Pattern | Description | Use Case | Key Metrics |
|---------|-------------|----------|-------------|
| Ramp-Up | Gradually increase load | Find breaking point | Throughput vs latency curve |
| Sustained | Constant load over time | Stability testing | Memory leaks, degradation |
| Spike | Sudden load increase | Auto-scaling validation | Scale-up response time |
| Soak | Long-duration constant load | Memory leak detection | Resource usage over time |
| Capacity | Find maximum sustainable throughput | SLA planning | Max RPS at acceptable latency |

---

## 10. Workload Classification & Resource Modeling
### Classification Taxonomy
```python
class WorkloadClassifier:
    def classify_request(self, request_metadata):
        """Classify request into resource profile and priority"""
        
        # Resource Profile Classification
        if request_metadata.get('query_type') == 'aggregation':
            profile = 'cpu_intensive'
        elif request_metadata.get('data_size_mb', 0) > 100:
            profile = 'memory_intensive'
        elif 'ml_inference' in request_metadata.get('operation', ''):
            profile = 'gpu_bound'
        else:
            profile = 'io_bound'
            
        # Priority Classification
        if request_metadata.get('user_tier') == 'premium':
            priority = 'high'
        elif request_metadata.get('request_type') == 'interactive':
            priority = 'medium'
        else:
            priority = 'low'
            
        return {
            'resource_profile': profile,
            'priority': priority,
            'estimated_cpu_seconds': self.estimate_cpu_cost(request_metadata),
            'estimated_memory_mb': self.estimate_memory_cost(request_metadata)
        }
```

### Resource Scheduling Algorithm
```python
def schedule_workloads(pending_requests, available_resources):
    """Bin-packing algorithm with priority and resource constraints"""
    
    # Sort by priority, then by resource efficiency
    sorted_requests = sorted(pending_requests, 
                           key=lambda r: (r['priority_score'], -r['resource_cost']))
    
    scheduled = []
    for request in sorted_requests:
        best_node = find_best_fit_node(request, available_resources)
        if best_node:
            schedule_on_node(request, best_node)
            scheduled.append(request)
    
    return scheduled

def find_best_fit_node(request, nodes):
    """Find node with best resource fit (minimize waste)"""
    best_node = None
    min_waste = float('inf')
    
    for node in nodes:
        if can_fit(request, node):
            waste = calculate_resource_waste(request, node)
            if waste < min_waste:
                min_waste = waste
                best_node = node
                
    return best_node
```

---

## 11. Observability & Telemetry Foundations
### Golden Signals for Capacity Planning
| Signal | Metric | Threshold Example | Capacity Insight |
|--------|--------|-------------------|------------------|
| Latency | P95 response time | <200ms interactive, <30s batch | Queue depth and resource contention |
| Traffic | Requests per second | Growth rate trending | Scale-up timing predictions |
| Errors | Error rate percentage | <0.1% for critical paths | Capacity-related failure patterns |
| Saturation | Resource utilization | CPU <70%, Memory <85% | Time to exhaustion forecasting |

### Telemetry Schema
```python
class CapacityMetrics:
    def emit_metrics(self, service_name, request_context):
        """Emit standardized capacity planning metrics"""
        
        # Performance Metrics
        self.histogram('request_duration_seconds', 
                      duration, 
                      labels={'service': service_name, 
                             'workload_type': request_context.workload_type})
        
        # Resource Consumption
        self.gauge('cpu_utilization_percent', 
                  get_cpu_usage(), 
                  labels={'node_id': get_node_id()})
        
        # Capacity Indicators
        self.gauge('request_queue_depth', 
                  get_queue_size(), 
                  labels={'service': service_name})
        
        # Business Context
        self.counter('requests_total', 
                    labels={'priority': request_context.priority,
                           'user_tier': request_context.user_tier})
```

### Capacity Runway Calculation
```python
def calculate_runway(resource_usage_timeseries, growth_rate_monthly):
    """Calculate time until resource exhaustion"""
    
    current_usage = resource_usage_timeseries[-1]
    capacity_limit = 100  # percent
    
    # Linear extrapolation
    if growth_rate_monthly > 0:
        months_to_exhaustion = (capacity_limit - current_usage) / growth_rate_monthly
        return max(0, months_to_exhaustion)
    else:
        return float('inf')  # Negative or zero growth

# Example usage
cpu_usage_history = [45, 47, 48, 52, 55]  # Monthly averages
growth_rate = 3  # 3% per month
runway_months = calculate_runway(cpu_usage_history, growth_rate)
print(f"CPU capacity runway: {runway_months:.1f} months")
```

---

## ✅ Sections 0–11 Complete Summary
- Executive framing with 5 strategic objectives and ROI quantification
- ELI10 pizza restaurant analogy for capacity planning intuition
- Problem framing covering 10 failure patterns (reactive scaling, linear assumptions, hidden contention)
- Core concepts including Universal Scalability Law, Little's Law, workload classification
- Performance-focused architecture with capacity planning engine and control loops
- Deep modeling section (USL, queuing theory, practical formulas)
- Capacity sizing formulas for CPU, memory, storage, network, Spark clusters
- Auto-scaling strategies (reactive, predictive, hybrid) with policy templates
- Failure mode catalog (capacity cliff, memory leaks, thrashing, hot partitions)
- Benchmarking foundations (realistic load patterns, harness design, testing strategies)
- Workload classification and resource scheduling algorithms
- Observability schema with golden signals and capacity runway calculations

Next (Sections 12–14): Implementation tracks (basic monitoring → full capacity platform), case studies (scaling stories from production), interview question bank (sizing problems → system design).