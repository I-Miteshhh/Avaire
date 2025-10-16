# Monitoring & Observability - From Metrics to Full Observability

**Mastery Level:** Critical for Production Systems  
**Interview Weight:** 20-30% of system design interviews  
**Time to Master:** 2-3 weeks  
**Difficulty:** ⭐⭐⭐⭐⭐

---

## 🎯 Why Observability Mastery Matters

At **Staff/Principal level**, observability enables:
- **Proactive issue detection** before users notice
- **Rapid incident resolution** with precise root cause analysis
- **Performance optimization** based on real data
- **Business insights** from operational metrics
- **SLA compliance** and reliability guarantees

**No observability = blind system operations. Full observability = data-driven reliability.**

---

## 📊 The Three Pillars of Observability

### **1. Metrics - What's happening?**
```
Quantitative measurements over time
- System metrics: CPU, memory, disk, network
- Application metrics: request rate, error rate, latency
- Business metrics: orders/sec, revenue, user engagement
```

### **2. Logs - What happened?**
```
Timestamped records of discrete events
- Structured logs with consistent format
- Log aggregation and centralized storage
- Log correlation across services
```

### **3. Traces - How did it happen?**
```
Request flow through distributed systems
- Distributed tracing across microservices
- Performance bottleneck identification
- Service dependency mapping
```

---

## 📈 Comprehensive Metrics Strategy

### **Application Performance Monitoring:**

```python
import time
import psutil
import threading
from collections import defaultdict, deque
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class MetricPoint:
    timestamp: float
    value: float
    tags: Dict[str, str]

class MetricsCollector:
    def __init__(self, flush_interval: int = 60):
        self.metrics = defaultdict(deque)
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(list)
        self.flush_interval = flush_interval
        
        # Start background flusher
        self.flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self.flush_thread.start()
    
    def counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """Increment counter metric"""
        key = self._make_key(name, tags or {})
        self.counters[key] += value
        
        # Also store time series data
        self.metrics[key].append(MetricPoint(
            timestamp=time.time(),
            value=self.counters[key],
            tags=tags or {}
        ))
    
    def gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Set gauge metric (latest value)"""
        key = self._make_key(name, tags or {})
        self.gauges[key] = value
        
        self.metrics[key].append(MetricPoint(
            timestamp=time.time(),
            value=value,
            tags=tags or {}
        ))
    
    def histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record histogram value for percentile calculations"""
        key = self._make_key(name, tags or {})
        self.histograms[key].append(value)
        
        # Keep only recent values (last hour)
        cutoff = time.time() - 3600
        self.histograms[key] = [v for v in self.histograms[key] if v >= cutoff]
    
    def timing(self, name: str, start_time: float, tags: Dict[str, str] = None):
        """Record timing metric"""
        duration = (time.time() - start_time) * 1000  # Convert to milliseconds
        self.histogram(name, duration, tags)
    
    def _make_key(self, name: str, tags: Dict[str, str]) -> str:
        """Create unique key from metric name and tags"""
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}#{tag_str}" if tag_str else name
    
    def get_percentiles(self, name: str, tags: Dict[str, str] = None) -> Dict[str, float]:
        """Calculate percentiles for histogram metric"""
        key = self._make_key(name, tags or {})
        values = sorted(self.histograms.get(key, []))
        
        if not values:
            return {}
        
        percentiles = {}
        for p in [50, 90, 95, 99]:
            index = int((p / 100.0) * len(values))
            percentiles[f"p{p}"] = values[min(index, len(values) - 1)]
        
        percentiles['min'] = values[0]
        percentiles['max'] = values[-1]
        percentiles['avg'] = sum(values) / len(values)
        
        return percentiles
    
    def _flush_loop(self):
        """Background thread to flush metrics"""
        while True:
            time.sleep(self.flush_interval)
            self._flush_metrics()
    
    def _flush_metrics(self):
        """Flush metrics to storage/external system"""
        # In production, send to Prometheus, DataDog, etc.
        print(f"Flushing {len(self.metrics)} metric series...")
        
        # Example: Print current metrics
        for key, points in self.metrics.items():
            if points:
                latest = points[-1]
                print(f"{key}: {latest.value} at {datetime.fromtimestamp(latest.timestamp)}")

# System metrics collector
class SystemMetricsCollector:
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.collection_thread = threading.Thread(target=self._collect_loop, daemon=True)
        self.collection_thread.start()
    
    def _collect_loop(self):
        """Continuously collect system metrics"""
        while True:
            try:
                self._collect_system_metrics()
                time.sleep(10)  # Collect every 10 seconds
            except Exception as e:
                print(f"Error collecting system metrics: {e}")
    
    def _collect_system_metrics(self):
        """Collect CPU, memory, disk, network metrics"""
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        self.metrics.gauge('system.cpu.usage', cpu_percent, {'unit': 'percent'})
        
        # Memory metrics
        memory = psutil.virtual_memory()
        self.metrics.gauge('system.memory.usage', memory.percent, {'unit': 'percent'})
        self.metrics.gauge('system.memory.available', memory.available, {'unit': 'bytes'})
        self.metrics.gauge('system.memory.total', memory.total, {'unit': 'bytes'})
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        self.metrics.gauge('system.disk.usage', disk.percent, {'unit': 'percent', 'mount': '/'})
        self.metrics.gauge('system.disk.free', disk.free, {'unit': 'bytes', 'mount': '/'})
        
        # Network metrics
        network = psutil.net_io_counters()
        self.metrics.counter('system.network.bytes_sent', network.bytes_sent, {'direction': 'out'})
        self.metrics.counter('system.network.bytes_recv', network.bytes_recv, {'direction': 'in'})

# Application metrics with decorators
class ApplicationMetrics:
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
    
    def timed(self, metric_name: str, tags: Dict[str, str] = None):
        """Decorator to time function execution"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    # Success metrics
                    self.metrics.counter(f'{metric_name}.success', tags=tags)
                    return result
                except Exception as e:
                    # Error metrics
                    error_tags = {**(tags or {}), 'error_type': type(e).__name__}
                    self.metrics.counter(f'{metric_name}.error', tags=error_tags)
                    raise
                finally:
                    # Timing metrics
                    self.metrics.timing(f'{metric_name}.duration', start_time, tags)
            return wrapper
        return decorator
    
    def counted(self, metric_name: str, tags: Dict[str, str] = None):
        """Decorator to count function calls"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                self.metrics.counter(metric_name, tags=tags)
                return func(*args, **kwargs)
            return wrapper
        return decorator

# Example usage in Flask application
from flask import Flask, request, g
import uuid

app = Flask(__name__)
metrics_collector = MetricsCollector()
system_metrics = SystemMetricsCollector(metrics_collector)
app_metrics = ApplicationMetrics(metrics_collector)

@app.before_request
def before_request():
    """Set up request tracking"""
    g.start_time = time.time()
    g.request_id = str(uuid.uuid4())
    
    # Track request metrics
    metrics_collector.counter('http.requests.total', tags={
        'method': request.method,
        'endpoint': request.endpoint or 'unknown'
    })

@app.after_request
def after_request(response):
    """Track response metrics"""
    duration = time.time() - g.start_time
    
    tags = {
        'method': request.method,
        'endpoint': request.endpoint or 'unknown',
        'status_code': str(response.status_code)
    }
    
    # Response time
    metrics_collector.histogram('http.request.duration', duration * 1000, tags)
    
    # Response status
    metrics_collector.counter('http.responses.total', tags=tags)
    
    return response

@app.route('/api/users')
@app_metrics.timed('api.users.list', tags={'version': 'v1'})
@app_metrics.counted('api.users.calls')
def list_users():
    # Simulate database query
    time.sleep(0.1)
    return {'users': []}

@app.route('/api/orders')
@app_metrics.timed('api.orders.list')
def list_orders():
    # Simulate potential error
    import random
    if random.random() < 0.1:  # 10% error rate
        raise Exception("Database connection failed")
    
    return {'orders': []}
```

### **Custom Business Metrics:**

```python
class BusinessMetricsCollector:
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
    
    def track_order_created(self, order_amount: float, user_tier: str, payment_method: str):
        """Track order creation with business context"""
        tags = {
            'user_tier': user_tier,
            'payment_method': payment_method
        }
        
        # Count orders
        self.metrics.counter('business.orders.created', tags=tags)
        
        # Track revenue
        self.metrics.histogram('business.order.amount', order_amount, tags)
        
        # Daily revenue gauge (would be calculated differently in production)
        self.metrics.gauge('business.revenue.daily', order_amount, tags={'date': datetime.now().strftime('%Y-%m-%d')})
    
    def track_user_signup(self, acquisition_channel: str, user_tier: str):
        """Track user acquisition"""
        tags = {
            'channel': acquisition_channel,
            'tier': user_tier
        }
        
        self.metrics.counter('business.users.signup', tags=tags)
    
    def track_user_activity(self, user_id: str, activity_type: str, session_duration: float):
        """Track user engagement"""
        tags = {
            'activity_type': activity_type,
            'user_segment': self._get_user_segment(user_id)
        }
        
        self.metrics.counter('business.user.activity', tags=tags)
        self.metrics.histogram('business.session.duration', session_duration, tags)
    
    def track_feature_usage(self, feature_name: str, user_id: str, success: bool):
        """Track feature adoption and success rates"""
        tags = {
            'feature': feature_name,
            'user_segment': self._get_user_segment(user_id),
            'success': str(success).lower()
        }
        
        self.metrics.counter('business.feature.usage', tags=tags)
    
    def _get_user_segment(self, user_id: str) -> str:
        # In practice, lookup user segment from database/cache
        return 'premium' if hash(user_id) % 2 else 'standard'

# Alert conditions
class AlertManager:
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.alert_rules = []
        self.alert_history = defaultdict(list)
    
    def add_alert_rule(self, name: str, condition_func, severity: str = 'warning'):
        """Add alert rule"""
        self.alert_rules.append({
            'name': name,
            'condition': condition_func,
            'severity': severity,
            'last_triggered': None
        })
    
    def check_alerts(self):
        """Check all alert conditions"""
        current_time = time.time()
        
        for rule in self.alert_rules:
            try:
                if rule['condition'](self.metrics):
                    # Check if we should fire alert (avoid spam)
                    if self._should_fire_alert(rule, current_time):
                        self._fire_alert(rule, current_time)
            except Exception as e:
                print(f"Error checking alert rule {rule['name']}: {e}")
    
    def _should_fire_alert(self, rule: dict, current_time: float) -> bool:
        """Check if enough time has passed since last alert"""
        cooldown_period = 300  # 5 minutes
        
        if rule['last_triggered'] is None:
            return True
        
        return (current_time - rule['last_triggered']) > cooldown_period
    
    def _fire_alert(self, rule: dict, current_time: float):
        """Fire alert (send to notification system)"""
        alert = {
            'name': rule['name'],
            'severity': rule['severity'],
            'timestamp': current_time,
            'message': f"Alert triggered: {rule['name']}"
        }
        
        # Store in history
        self.alert_history[rule['name']].append(alert)
        rule['last_triggered'] = current_time
        
        # Send notification (would integrate with PagerDuty, Slack, etc.)
        print(f"🚨 ALERT: {alert['message']} (Severity: {alert['severity']})")

# Example alert conditions
def setup_alerts(alert_manager: AlertManager):
    """Setup common alert conditions"""
    
    # High error rate
    def high_error_rate(metrics):
        error_count = metrics.counters.get('http.responses.total#status_code=500', 0)
        total_count = sum(v for k, v in metrics.counters.items() if k.startswith('http.responses.total'))
        
        if total_count > 100:  # Only alert if we have significant traffic
            error_rate = error_count / total_count
            return error_rate > 0.05  # 5% error rate
        
        return False
    
    alert_manager.add_alert_rule('high_error_rate', high_error_rate, 'critical')
    
    # High response time
    def high_response_time(metrics):
        response_times = metrics.histograms.get('http.request.duration', [])
        if len(response_times) > 10:
            avg_time = sum(response_times[-10:]) / 10  # Last 10 requests
            return avg_time > 2000  # 2 seconds
        return False
    
    alert_manager.add_alert_rule('high_response_time', high_response_time, 'warning')
    
    # High CPU usage
    def high_cpu_usage(metrics):
        cpu_metrics = [m for k, v in metrics.metrics.items() 
                      if k.startswith('system.cpu.usage') for m in v]
        if cpu_metrics:
            latest_cpu = cpu_metrics[-1].value
            return latest_cpu > 80  # 80% CPU
        return False
    
    alert_manager.add_alert_rule('high_cpu_usage', high_cpu_usage, 'warning')
```

---

## 📝 Structured Logging Strategy

### **Comprehensive Logging Framework:**

```python
import json
import logging
import sys
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import contextmanager
import threading

class StructuredLogger:
    def __init__(self, service_name: str, version: str, environment: str):
        self.service_name = service_name
        self.version = version
        self.environment = environment
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(logging.INFO)
        
        # Setup structured JSON formatter
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(self.JSONFormatter())
        self.logger.addHandler(handler)
        
        # Thread-local storage for request context
        self.local = threading.local()
    
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_entry = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'level': record.levelname,
                'message': record.getMessage(),
                'logger': record.name,
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno,
            }
            
            # Add extra fields
            if hasattr(record, 'extra_fields'):
                log_entry.update(record.extra_fields)
            
            # Add exception info
            if record.exc_info:
                log_entry['exception'] = {
                    'type': record.exc_info[0].__name__,
                    'message': str(record.exc_info[1]),
                    'traceback': traceback.format_exception(*record.exc_info)
                }
            
            return json.dumps(log_entry, default=str)
    
    def set_request_context(self, request_id: str, user_id: Optional[str] = None, 
                           trace_id: Optional[str] = None):
        """Set request context for correlation"""
        self.local.request_id = request_id
        self.local.user_id = user_id
        self.local.trace_id = trace_id
    
    def _get_base_fields(self) -> Dict[str, Any]:
        """Get base fields for all log entries"""
        fields = {
            'service': self.service_name,
            'version': self.version,
            'environment': self.environment,
        }
        
        # Add request context if available
        if hasattr(self.local, 'request_id'):
            fields['request_id'] = self.local.request_id
        if hasattr(self.local, 'user_id'):
            fields['user_id'] = self.local.user_id
        if hasattr(self.local, 'trace_id'):
            fields['trace_id'] = self.local.trace_id
        
        return fields
    
    def info(self, message: str, **kwargs):
        """Log info message with structured data"""
        extra_fields = {**self._get_base_fields(), **kwargs}
        self.logger.info(message, extra={'extra_fields': extra_fields})
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        extra_fields = {**self._get_base_fields(), **kwargs}
        self.logger.warning(message, extra={'extra_fields': extra_fields})
    
    def error(self, message: str, exc_info=None, **kwargs):
        """Log error message with optional exception"""
        extra_fields = {**self._get_base_fields(), **kwargs}
        self.logger.error(message, exc_info=exc_info, extra={'extra_fields': extra_fields})
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        extra_fields = {**self._get_base_fields(), **kwargs}
        self.logger.debug(message, extra={'extra_fields': extra_fields})
    
    @contextmanager
    def operation_context(self, operation: str, **context):
        """Context manager for operation logging"""
        operation_id = str(uuid.uuid4())
        start_time = time.time()
        
        self.info(f"Starting operation: {operation}", 
                 operation=operation, 
                 operation_id=operation_id,
                 **context)
        
        try:
            yield operation_id
            duration = time.time() - start_time
            self.info(f"Completed operation: {operation}",
                     operation=operation,
                     operation_id=operation_id,
                     duration_ms=duration * 1000,
                     status='success',
                     **context)
        except Exception as e:
            duration = time.time() - start_time
            self.error(f"Failed operation: {operation}",
                      operation=operation,
                      operation_id=operation_id,
                      duration_ms=duration * 1000,
                      status='error',
                      error_type=type(e).__name__,
                      exc_info=True,
                      **context)
            raise

# Flask integration
from flask import Flask, request, g

def setup_logging_middleware(app: Flask, logger: StructuredLogger):
    """Setup logging middleware for Flask"""
    
    @app.before_request
    def before_request():
        g.request_id = str(uuid.uuid4())
        g.start_time = time.time()
        
        # Set request context
        user_id = request.headers.get('X-User-ID')  # From auth middleware
        trace_id = request.headers.get('X-Trace-ID')
        logger.set_request_context(g.request_id, user_id, trace_id)
        
        # Log request start
        logger.info("Request started",
                   method=request.method,
                   path=request.path,
                   user_agent=request.headers.get('User-Agent'),
                   remote_addr=request.remote_addr,
                   content_length=request.content_length)
    
    @app.after_request
    def after_request(response):
        duration = (time.time() - g.start_time) * 1000
        
        # Log request completion
        logger.info("Request completed",
                   method=request.method,
                   path=request.path,
                   status_code=response.status_code,
                   duration_ms=duration,
                   response_size=len(response.get_data()) if response.get_data() else 0)
        
        return response
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error("Unhandled exception",
                    method=request.method,
                    path=request.path,
                    exc_info=True)
        return {'error': 'Internal server error'}, 500

# Usage example
logger = StructuredLogger('ecommerce-api', '1.0.0', 'production')

@app.route('/api/orders', methods=['POST'])
def create_order():
    with logger.operation_context('create_order', user_id=g.current_user_id) as op_id:
        try:
            order_data = request.json
            logger.info("Processing order creation", 
                       order_items=len(order_data.get('items', [])),
                       total_amount=order_data.get('total_amount'))
            
            # Create order
            order = order_service.create_order(order_data)
            
            logger.info("Order created successfully",
                       order_id=order.id,
                       customer_id=order.customer_id)
            
            return {'order_id': order.id}
            
        except ValidationError as e:
            logger.warning("Order validation failed",
                          validation_errors=e.errors)
            return {'error': 'Validation failed', 'details': e.errors}, 400
        
        except Exception as e:
            logger.error("Order creation failed", exc_info=True)
            return {'error': 'Internal server error'}, 500
```

---

## 🔍 Distributed Tracing Implementation

### **OpenTelemetry Integration:**

```python
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
import uuid

class DistributedTracing:
    def __init__(self, service_name: str, jaeger_endpoint: str = "http://localhost:14268/api/traces"):
        self.service_name = service_name
        
        # Setup resource
        resource = Resource.create({
            "service.name": service_name,
            "service.version": "1.0.0"
        })
        
        # Setup tracing
        trace.set_tracer_provider(TracerProvider(resource=resource))
        tracer = trace.get_tracer(__name__)
        
        # Setup Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name="localhost",
            agent_port=6831,
        )
        
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        # Setup metrics
        metrics.set_meter_provider(MeterProvider(resource=resource))
        self.meter = metrics.get_meter(__name__)
        
        # Auto-instrument common libraries
        FlaskInstrumentor().instrument()
        RequestsInstrumentor().instrument()
        SQLAlchemyInstrumentor().instrument()
        
        self.tracer = tracer
    
    def trace_function(self, span_name: str = None):
        """Decorator to trace function execution"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                name = span_name or f"{func.__module__}.{func.__name__}"
                
                with self.tracer.start_as_current_span(name) as span:
                    # Add function metadata
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)
                    
                    # Add arguments (be careful with sensitive data)
                    if args:
                        span.set_attribute("function.args.count", len(args))
                    if kwargs:
                        span.set_attribute("function.kwargs.count", len(kwargs))
                    
                    try:
                        result = func(*args, **kwargs)
                        span.set_attribute("function.status", "success")
                        return result
                    except Exception as e:
                        span.set_attribute("function.status", "error")
                        span.set_attribute("error.type", type(e).__name__)
                        span.set_attribute("error.message", str(e))
                        span.record_exception(e)
                        raise
            return wrapper
        return decorator
    
    def trace_database_query(self, query: str, parameters: dict = None):
        """Context manager for database query tracing"""
        return self.tracer.start_as_current_span(
            "database.query",
            attributes={
                "db.statement": query,
                "db.operation": query.split()[0].upper() if query else "UNKNOWN"
            }
        )
    
    def trace_external_call(self, service: str, operation: str):
        """Context manager for external service calls"""
        return self.tracer.start_as_current_span(
            f"external.{service}.{operation}",
            attributes={
                "service.name": service,
                "operation.name": operation
            }
        )

# Advanced tracing patterns
class ServiceTracing:
    def __init__(self, distributed_tracing: DistributedTracing):
        self.tracing = distributed_tracing
        self.tracer = distributed_tracing.tracer
    
    def trace_user_request(self, user_id: str, operation: str):
        """Trace user-initiated operations"""
        span = self.tracer.start_span(f"user.{operation}")
        span.set_attribute("user.id", user_id)
        span.set_attribute("operation.type", "user_request")
        return span
    
    def trace_background_job(self, job_type: str, job_id: str):
        """Trace background job execution"""
        span = self.tracer.start_span(f"job.{job_type}")
        span.set_attribute("job.id", job_id)
        span.set_attribute("job.type", job_type)
        span.set_attribute("operation.type", "background_job")
        return span
    
    def trace_message_processing(self, queue_name: str, message_id: str):
        """Trace message queue processing"""
        span = self.tracer.start_span(f"queue.{queue_name}.process")
        span.set_attribute("message.id", message_id)
        span.set_attribute("queue.name", queue_name)
        span.set_attribute("operation.type", "message_processing")
        return span

# Example usage in application
tracing = DistributedTracing('ecommerce-service')
service_tracing = ServiceTracing(tracing)

class OrderService:
    def __init__(self):
        self.db = DatabaseConnection()
        self.payment_service = PaymentServiceClient()
        self.inventory_service = InventoryServiceClient()
    
    @tracing.trace_function("order.create")
    def create_order(self, user_id: str, order_data: dict) -> dict:
        """Create order with full tracing"""
        
        with service_tracing.trace_user_request(user_id, "create_order") as user_span:
            user_span.set_attribute("order.items.count", len(order_data.get('items', [])))
            user_span.set_attribute("order.total", order_data.get('total_amount', 0))
            
            # Validate order
            with self.tracer.start_as_current_span("order.validate") as validate_span:
                validation_result = self.validate_order(order_data)
                validate_span.set_attribute("validation.result", validation_result)
                
                if not validation_result:
                    validate_span.set_attribute("error", "validation_failed")
                    raise ValidationError("Order validation failed")
            
            # Check inventory
            with tracing.trace_external_call("inventory", "check_availability") as inv_span:
                availability = self.inventory_service.check_availability(order_data['items'])
                inv_span.set_attribute("inventory.available", availability)
            
            # Process payment
            with tracing.trace_external_call("payment", "charge") as pay_span:
                payment_result = self.payment_service.charge(
                    user_id, 
                    order_data['total_amount']
                )
                pay_span.set_attribute("payment.transaction_id", payment_result['transaction_id'])
                pay_span.set_attribute("payment.status", payment_result['status'])
            
            # Save order to database
            with tracing.trace_database_query(
                "INSERT INTO orders (user_id, total_amount, status) VALUES (?, ?, ?)",
                {"user_id": user_id, "total_amount": order_data['total_amount'], "status": "confirmed"}
            ) as db_span:
                order_id = self.db.create_order(user_id, order_data)
                db_span.set_attribute("order.id", order_id)
            
            user_span.set_attribute("order.id", order_id)
            user_span.set_attribute("order.status", "success")
            
            return {"order_id": order_id, "status": "confirmed"}
    
    def validate_order(self, order_data: dict) -> bool:
        # Validation logic
        return True

# Trace correlation across services
class TraceCorrelation:
    def __init__(self):
        self.tracer = trace.get_tracer(__name__)
    
    def propagate_trace_context(self, headers: dict) -> dict:
        """Add tracing headers for cross-service calls"""
        from opentelemetry.propagate import inject
        
        # Inject current trace context into headers
        inject(headers)
        return headers
    
    def extract_trace_context(self, headers: dict):
        """Extract trace context from incoming headers"""
        from opentelemetry.propagate import extract
        
        # Extract trace context from headers
        context = extract(headers)
        return context
    
    def start_child_span(self, name: str, parent_context=None):
        """Start span with proper parent context"""
        if parent_context:
            with trace.use_span(parent_context):
                return self.tracer.start_span(name)
        else:
            return self.tracer.start_span(name)

# Cross-service call example
import requests

class PaymentServiceClient:
    def __init__(self):
        self.base_url = "https://payment-service.example.com"
        self.trace_correlation = TraceCorrelation()
    
    def charge(self, user_id: str, amount: float) -> dict:
        """Make payment charge with trace propagation"""
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'ecommerce-service/1.0.0'
        }
        
        # Propagate trace context
        headers = self.trace_correlation.propagate_trace_context(headers)
        
        with trace.get_tracer(__name__).start_as_current_span("payment.charge.http") as span:
            span.set_attribute("http.method", "POST")
            span.set_attribute("http.url", f"{self.base_url}/charges")
            span.set_attribute("user.id", user_id)
            span.set_attribute("payment.amount", amount)
            
            response = requests.post(
                f"{self.base_url}/charges",
                json={
                    'user_id': user_id,
                    'amount': amount,
                    'currency': 'USD'
                },
                headers=headers,
                timeout=30
            )
            
            span.set_attribute("http.status_code", response.status_code)
            
            if response.status_code != 200:
                span.set_attribute("error", True)
                span.set_attribute("error.message", f"HTTP {response.status_code}")
                raise Exception(f"Payment failed: {response.status_code}")
            
            return response.json()
```

---

## 📊 Advanced Monitoring Dashboards

### **Prometheus & Grafana Integration:**

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
import threading

class PrometheusMetrics:
    def __init__(self, port: int = 8000):
        # Define metrics
        self.request_count = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code']
        )
        
        self.request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        self.active_connections = Gauge(
            'http_active_connections',
            'Active HTTP connections'
        )
        
        self.business_orders_total = Counter(
            'business_orders_total',
            'Total orders created',
            ['payment_method', 'user_tier']
        )
        
        self.business_revenue = Counter(
            'business_revenue_total',
            'Total revenue',
            ['currency', 'payment_method']
        )
        
        self.system_cpu_usage = Gauge(
            'system_cpu_usage_percent',
            'CPU usage percentage'
        )
        
        self.system_memory_usage = Gauge(
            'system_memory_usage_bytes',
            'Memory usage in bytes'
        )
        
        self.database_connections = Gauge(
            'database_connections_active',
            'Active database connections',
            ['database']
        )
        
        self.queue_depth = Gauge(
            'message_queue_depth',
            'Message queue depth',
            ['queue_name']
        )
        
        # Start metrics server
        start_http_server(port)
        
        # Start system metrics collection
        self.start_system_metrics_collection()
    
    def start_system_metrics_collection(self):
        """Start background thread for system metrics"""
        def collect_system_metrics():
            while True:
                try:
                    import psutil
                    
                    # CPU usage
                    cpu_percent = psutil.cpu_percent(interval=1)
                    self.system_cpu_usage.set(cpu_percent)
                    
                    # Memory usage
                    memory = psutil.virtual_memory()
                    self.system_memory_usage.set(memory.used)
                    
                    time.sleep(10)
                except Exception as e:
                    print(f"Error collecting system metrics: {e}")
        
        thread = threading.Thread(target=collect_system_metrics, daemon=True)
        thread.start()
    
    def track_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Track HTTP request metrics"""
        self.request_count.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        
        self.request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def track_business_order(self, payment_method: str, user_tier: str, amount: float, currency: str = 'USD'):
        """Track business metrics"""
        self.business_orders_total.labels(
            payment_method=payment_method,
            user_tier=user_tier
        ).inc()
        
        self.business_revenue.labels(
            currency=currency,
            payment_method=payment_method
        ).inc(amount)
    
    def update_queue_depth(self, queue_name: str, depth: int):
        """Update queue depth metric"""
        self.queue_depth.labels(queue_name=queue_name).set(depth)
    
    def update_database_connections(self, database: str, count: int):
        """Update database connection count"""
        self.database_connections.labels(database=database).set(count)

# Flask middleware for Prometheus
from flask import Flask, request, g
import time

def setup_prometheus_middleware(app: Flask, metrics: PrometheusMetrics):
    """Setup Prometheus metrics collection for Flask"""
    
    @app.before_request
    def before_request():
        g.start_time = time.time()
        metrics.active_connections.inc()
    
    @app.after_request
    def after_request(response):
        duration = time.time() - g.start_time
        
        metrics.track_http_request(
            method=request.method,
            endpoint=request.endpoint or 'unknown',
            status_code=response.status_code,
            duration=duration
        )
        
        metrics.active_connections.dec()
        return response

# Custom metrics for application
class ApplicationMetrics:
    def __init__(self, prometheus_metrics: PrometheusMetrics):
        self.prometheus = prometheus_metrics
        
        # Define custom application metrics
        self.user_login_attempts = Counter(
            'user_login_attempts_total',
            'Total login attempts',
            ['success', 'method']
        )
        
        self.cache_operations = Counter(
            'cache_operations_total',
            'Cache operations',
            ['operation', 'result']
        )
        
        self.external_api_calls = Counter(
            'external_api_calls_total',
            'External API calls',
            ['service', 'operation', 'status']
        )
        
        self.background_jobs = Histogram(
            'background_job_duration_seconds',
            'Background job duration',
            ['job_type', 'status']
        )
    
    def track_login_attempt(self, success: bool, method: str):
        """Track user login attempts"""
        self.user_login_attempts.labels(
            success=str(success).lower(),
            method=method
        ).inc()
    
    def track_cache_operation(self, operation: str, hit: bool):
        """Track cache hit/miss"""
        result = 'hit' if hit else 'miss'
        self.cache_operations.labels(
            operation=operation,
            result=result
        ).inc()
    
    def track_external_api_call(self, service: str, operation: str, success: bool):
        """Track external API calls"""
        status = 'success' if success else 'error'
        self.external_api_calls.labels(
            service=service,
            operation=operation,
            status=status
        ).inc()
    
    def track_background_job(self, job_type: str, duration: float, success: bool):
        """Track background job execution"""
        status = 'success' if success else 'error'
        self.background_jobs.labels(
            job_type=job_type,
            status=status
        ).observe(duration)

# Grafana dashboard configuration (JSON)
grafana_dashboard_config = {
    "dashboard": {
        "id": None,
        "title": "Ecommerce Service Dashboard",
        "tags": ["ecommerce", "monitoring"],
        "timezone": "browser",
        "panels": [
            {
                "id": 1,
                "title": "Request Rate",
                "type": "graph",
                "targets": [
                    {
                        "expr": "rate(http_requests_total[5m])",
                        "legendFormat": "{{method}} {{endpoint}}"
                    }
                ],
                "yAxes": [
                    {"label": "Requests/sec"}
                ]
            },
            {
                "id": 2,
                "title": "Response Time",
                "type": "graph", 
                "targets": [
                    {
                        "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
                        "legendFormat": "95th percentile"
                    },
                    {
                        "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
                        "legendFormat": "50th percentile"
                    }
                ]
            },
            {
                "id": 3,
                "title": "Error Rate",
                "type": "graph",
                "targets": [
                    {
                        "expr": "rate(http_requests_total{status_code=~\"5..\"}[5m])",
                        "legendFormat": "5xx errors"
                    },
                    {
                        "expr": "rate(http_requests_total{status_code=~\"4..\"}[5m])",
                        "legendFormat": "4xx errors"
                    }
                ]
            },
            {
                "id": 4,
                "title": "Business Metrics",
                "type": "graph",
                "targets": [
                    {
                        "expr": "rate(business_orders_total[5m])",
                        "legendFormat": "Orders/sec"
                    },
                    {
                        "expr": "rate(business_revenue_total[5m])",
                        "legendFormat": "Revenue/sec"
                    }
                ]
            }
        ],
        "time": {
            "from": "now-1h",
            "to": "now"
        },
        "refresh": "5s"
    }
}
```

---

## 🚨 Incident Response & SLA Management

### **SLA Monitoring System:**

```python
from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime, timedelta
import json

@dataclass
class SLATarget:
    name: str
    description: str
    target_percentage: float  # e.g., 99.9 for 99.9%
    measurement_window: str   # e.g., "30d", "7d", "1h"
    metric_query: str        # Prometheus query
    alert_threshold: float   # When to alert (e.g., when below 99.5%)

class SLAManager:
    def __init__(self, prometheus_client):
        self.prometheus = prometheus_client
        self.sla_targets = {}
        self.sla_history = {}
        
        # Define common SLA targets
        self.setup_default_slas()
    
    def setup_default_slas(self):
        """Setup common SLA targets"""
        
        # Availability SLA
        self.add_sla_target(SLATarget(
            name="api_availability",
            description="API endpoint availability",
            target_percentage=99.9,
            measurement_window="30d",
            metric_query="(sum(rate(http_requests_total{status_code!~\"5..\"}[5m])) / sum(rate(http_requests_total[5m]))) * 100",
            alert_threshold=99.5
        ))
        
        # Latency SLA
        self.add_sla_target(SLATarget(
            name="api_latency_p95",
            description="95th percentile API latency under 500ms",
            target_percentage=95.0,  # 95% of requests under 500ms
            measurement_window="1h",
            metric_query="histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) * 1000",
            alert_threshold=500  # 500ms threshold
        ))
        
        # Business SLA
        self.add_sla_target(SLATarget(
            name="order_processing_success",
            description="Order processing success rate",
            target_percentage=99.95,
            measurement_window="24h",
            metric_query="(sum(increase(business_orders_successful[1h])) / sum(increase(business_orders_total[1h]))) * 100",
            alert_threshold=99.5
        ))
    
    def add_sla_target(self, sla_target: SLATarget):
        """Add SLA target for monitoring"""
        self.sla_targets[sla_target.name] = sla_target
        self.sla_history[sla_target.name] = []
    
    def check_sla_compliance(self) -> Dict[str, Dict]:
        """Check all SLA targets and return compliance status"""
        
        compliance_status = {}
        
        for name, sla in self.sla_targets.items():
            try:
                current_value = self._query_metric(sla.metric_query)
                
                is_compliant = self._is_sla_compliant(sla, current_value)
                
                status = {
                    'sla_target': sla.target_percentage,
                    'current_value': current_value,
                    'is_compliant': is_compliant,
                    'alert_threshold': sla.alert_threshold,
                    'should_alert': current_value < sla.alert_threshold,
                    'measurement_window': sla.measurement_window,
                    'last_checked': datetime.utcnow().isoformat()
                }
                
                # Store in history
                self.sla_history[name].append({
                    'timestamp': datetime.utcnow(),
                    'value': current_value,
                    'compliant': is_compliant
                })
                
                # Keep only recent history
                cutoff = datetime.utcnow() - timedelta(days=30)
                self.sla_history[name] = [
                    h for h in self.sla_history[name] 
                    if h['timestamp'] > cutoff
                ]
                
                compliance_status[name] = status
                
            except Exception as e:
                compliance_status[name] = {
                    'error': str(e),
                    'last_checked': datetime.utcnow().isoformat()
                }
        
        return compliance_status
    
    def _query_metric(self, query: str) -> float:
        """Query Prometheus for metric value"""
        # In practice, this would use prometheus_api_client
        # For example purposes, returning mock value
        import random
        return random.uniform(95.0, 99.9)
    
    def _is_sla_compliant(self, sla: SLATarget, current_value: float) -> bool:
        """Check if current value meets SLA target"""
        return current_value >= sla.target_percentage
    
    def get_sla_report(self, time_range: str = "7d") -> Dict:
        """Generate SLA compliance report"""
        
        report = {
            'report_period': time_range,
            'generated_at': datetime.utcnow().isoformat(),
            'sla_summary': {},
            'overall_compliance': True
        }
        
        for name, sla in self.sla_targets.items():
            history = self.sla_history.get(name, [])
            
            if not history:
                continue
            
            # Calculate compliance over period
            compliant_count = sum(1 for h in history if h['compliant'])
            total_count = len(history)
            compliance_rate = (compliant_count / total_count) * 100 if total_count > 0 else 0
            
            # Calculate average value
            avg_value = sum(h['value'] for h in history) / total_count if total_count > 0 else 0
            
            sla_summary = {
                'target': sla.target_percentage,
                'compliance_rate': compliance_rate,
                'average_value': avg_value,
                'total_measurements': total_count,
                'compliant_measurements': compliant_count,
                'is_meeting_sla': compliance_rate >= sla.target_percentage
            }
            
            report['sla_summary'][name] = sla_summary
            
            if not sla_summary['is_meeting_sla']:
                report['overall_compliance'] = False
        
        return report

# Incident management system
class IncidentManager:
    def __init__(self, sla_manager: SLAManager, alert_manager):
        self.sla_manager = sla_manager
        self.alert_manager = alert_manager
        self.active_incidents = {}
        self.incident_history = []
    
    def check_for_incidents(self):
        """Check SLA compliance and create incidents if needed"""
        
        compliance_status = self.sla_manager.check_sla_compliance()
        
        for sla_name, status in compliance_status.items():
            if status.get('should_alert', False):
                self._create_or_update_incident(sla_name, status)
            elif sla_name in self.active_incidents:
                self._resolve_incident(sla_name)
    
    def _create_or_update_incident(self, sla_name: str, status: Dict):
        """Create new incident or update existing one"""
        
        if sla_name not in self.active_incidents:
            # Create new incident
            incident = {
                'id': f"INC-{int(datetime.utcnow().timestamp())}",
                'sla_name': sla_name,
                'severity': self._determine_severity(status),
                'status': 'open',
                'created_at': datetime.utcnow(),
                'description': f"SLA breach: {sla_name}",
                'current_value': status['current_value'],
                'target_value': status['sla_target'],
                'updates': []
            }
            
            self.active_incidents[sla_name] = incident
            
            # Send alert
            self.alert_manager.send_incident_alert(incident)
            
            print(f"🚨 NEW INCIDENT: {incident['id']} - {incident['description']}")
        
        else:
            # Update existing incident
            incident = self.active_incidents[sla_name]
            incident['current_value'] = status['current_value']
            incident['updates'].append({
                'timestamp': datetime.utcnow(),
                'value': status['current_value'],
                'note': 'SLA metric updated'
            })
    
    def _resolve_incident(self, sla_name: str):
        """Resolve incident when SLA is back to normal"""
        
        if sla_name in self.active_incidents:
            incident = self.active_incidents[sla_name]
            incident['status'] = 'resolved'
            incident['resolved_at'] = datetime.utcnow()
            
            # Move to history
            self.incident_history.append(incident)
            del self.active_incidents[sla_name]
            
            print(f"✅ RESOLVED: {incident['id']} - {incident['description']}")
    
    def _determine_severity(self, status: Dict) -> str:
        """Determine incident severity based on SLA breach"""
        
        current = status['current_value']
        target = status['sla_target']
        
        breach_percentage = ((target - current) / target) * 100
        
        if breach_percentage > 5:  # More than 5% below target
            return 'critical'
        elif breach_percentage > 2:  # More than 2% below target
            return 'high'
        elif breach_percentage > 1:  # More than 1% below target
            return 'medium'
        else:
            return 'low'
    
    def get_incident_report(self) -> Dict:
        """Generate incident report"""
        
        return {
            'active_incidents': len(self.active_incidents),
            'incidents_today': len([
                i for i in self.incident_history 
                if i['created_at'].date() == datetime.utcnow().date()
            ]),
            'incidents_this_week': len([
                i for i in self.incident_history 
                if i['created_at'] > datetime.utcnow() - timedelta(weeks=1)
            ]),
            'active_incident_details': list(self.active_incidents.values()),
            'mttr_hours': self._calculate_mttr(),
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def _calculate_mttr(self) -> float:
        """Calculate Mean Time To Recovery"""
        
        resolved_incidents = [
            i for i in self.incident_history 
            if i['status'] == 'resolved' and 'resolved_at' in i
            ]
        
        if not resolved_incidents:
            return 0.0
        
        total_resolution_time = sum([
            (i['resolved_at'] - i['created_at']).total_seconds() / 3600
            for i in resolved_incidents
        ])
        
        return total_resolution_time / len(resolved_incidents)

# Usage example
prometheus_metrics = PrometheusMetrics()
sla_manager = SLAManager(prometheus_client=None)
incident_manager = IncidentManager(sla_manager, alert_manager=None)

# Run monitoring loop
def monitoring_loop():
    while True:
        try:
            # Check SLA compliance
            compliance = sla_manager.check_sla_compliance()
            
            # Check for incidents
            incident_manager.check_for_incidents()
            
            # Generate reports
            sla_report = sla_manager.get_sla_report()
            incident_report = incident_manager.get_incident_report()
            
            print(f"SLA Compliance: {sla_report['overall_compliance']}")
            print(f"Active Incidents: {incident_report['active_incidents']}")
            
            time.sleep(60)  # Check every minute
            
        except Exception as e:
            print(f"Error in monitoring loop: {e}")
            time.sleep(60)
```

---

## ✅ Observability Mastery Checklist

### **Metrics & Monitoring**
- [ ] Application performance metrics (RED/USE method)
- [ ] Business metrics and KPI tracking
- [ ] System metrics (CPU, memory, disk, network)
- [ ] Custom metrics for domain-specific monitoring
- [ ] Prometheus integration and alerting rules

### **Logging Strategy**
- [ ] Structured logging with consistent format
- [ ] Log aggregation and centralized storage
- [ ] Request correlation and tracing IDs
- [ ] Log levels and filtering strategies
- [ ] Security considerations (no sensitive data)

### **Distributed Tracing**
- [ ] OpenTelemetry implementation
- [ ] Cross-service trace propagation
- [ ] Performance bottleneck identification
- [ ] Service dependency mapping
- [ ] Error tracking and debugging

### **Alerting & Incident Response**
- [ ] SLA definition and monitoring
- [ ] Alert fatigue prevention (smart thresholds)
- [ ] Incident escalation procedures
- [ ] Post-incident review processes
- [ ] Runbook automation

### **Dashboards & Visualization**
- [ ] Executive dashboards (business metrics)
- [ ] Operational dashboards (system health)
- [ ] Debug dashboards (deep-dive analysis)
- [ ] Mobile-friendly alerting
- [ ] Historical trend analysis

**Master these observability patterns, and you'll build systems that are transparent, debuggable, and reliable!** 📊