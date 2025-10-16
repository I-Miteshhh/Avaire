# Week 8: Microservices Communication Patterns - Orchestra of Digital Services 🎼🌐

*"Microservices are like musicians in an orchestra - each plays their part perfectly, but the magic happens when they coordinate to create something beautiful together"*

## 🎯 This Week's Mission
Master how distributed systems coordinate across hundreds of services. Learn service meshes, API gateways, and communication patterns that keep systems like Uber, Netflix, and Google running smoothly at planetary scale.

---

## 📋 Prerequisites: Building on Previous Weeks

You should now understand:
- ✅ **Multi-Layer Caching**: How to store and retrieve data efficiently
- ✅ **Load Balancing**: Distributing traffic across multiple servers
- ✅ **CDN Architecture**: Global content distribution strategies
- ✅ **Network Protocols**: TCP, UDP, HTTP evolution and optimization

### New Concepts We'll Master
- **Service Discovery**: How services find and connect to each other
- **Circuit Breakers**: Preventing cascade failures in distributed systems
- **API Gateways**: Centralized entry points for microservice architectures
- **Service Mesh**: Infrastructure layer for service-to-service communication

---

## 🎪 Explain Like I'm 10: The Great Restaurant City

### 🏪 The Old Way: One Giant Restaurant (Monolithic Architecture)

Imagine a **massive restaurant** that serves every type of food in the world:

```
🏢 Mega Restaurant: "Everything Everywhere All at Once"
├─ 🍕 Pizza Kitchen (500 chefs)
├─ 🍣 Sushi Kitchen (300 chefs)  
├─ 🍔 Burger Kitchen (400 chefs)
├─ 🥘 Indian Kitchen (200 chefs)
├─ 🍰 Dessert Kitchen (150 chefs)
└─ 💰 One Giant Cash Register

Problems:
- If pizza oven breaks → Entire restaurant shuts down
- Want to add Thai food → Rebuild entire kitchen
- One busy day → All kitchens overwhelmed
- Training new chef → Must learn ALL cuisines
- Cash register crashes → Nobody can pay for anything!
```

### 🏪 The Smart Way: Specialized Restaurant District (Microservices)

Now imagine a **food district** with specialized restaurants:

```
🌆 Food District: "Best of Everything, Everywhere"

🍕 Tony's Pizza Palace
├─ 5 pizza chefs (experts!)
├─ Own cash register
├─ Own delivery system
└─ Opens/closes independently

🍣 Sakura Sushi House  
├─ 3 sushi masters (specialists!)
├─ Own payment system
├─ Own ordering app
└─ Can expand without affecting others

🍔 Bob's Burger Joint
├─ 4 burger specialists
├─ Own kitchen equipment  
├─ Own customer loyalty program
└─ Operates 24/7 independently

🥘 Mumbai Spice Palace
├─ 2 curry experts
├─ Own spice supply chain
├─ Own cultural decorations
└─ Seasonal menu changes easily

Magic Benefits:
- Pizza place broken? → Sushi still serves customers!
- Want Thai food? → Just open new Thai restaurant!
- Burger place busy? → Doesn't slow down pizza orders!
- New sushi chef? → Only learns sushi, starts immediately!
```

### 📞 The Communication Challenge: How Restaurants Coordinate

But now we have a **coordination problem**:

```
Customer: "I want pizza, sushi, AND dessert for my party!"

Old Way - Customer Chaos:
Customer → 🍕 Pizza place → Wait 20 minutes → Get pizza
Customer → 🍣 Sushi place → Wait 15 minutes → Get sushi  
Customer → 🍰 Dessert shop → Wait 10 minutes → Get dessert
Result: 45 minutes, cold food, frustrated customer!

Smart Way - Food District Coordinator (API Gateway):
Customer → 📋 District Coordinator → Orders from all restaurants
         ↓
Coordinator → 🍕 Pizza (20 min) + 🍣 Sushi (15 min) + 🍰 Dessert (10 min)
         ↓
All food delivered together in 20 minutes, hot and fresh!

The Coordinator's Magic:
- Knows which restaurants are open (service discovery)
- Routes orders to fastest kitchen (load balancing)
- If pizza place is busy → Suggests calzones from Italian place (circuit breaker)
- Tracks all orders → Sends SMS updates (observability)
- Handles payments → Splits bills between restaurants (transaction management)
```

### 🕸️ The Secret Communication Network (Service Mesh)

The restaurants also have a **secret network** for coordination:

```
🕷️ Restaurant WhatsApp Group (Service Mesh):

Pizza Chef: "Running low on cheese, who has extra?"
Dessert Chef: "I have mozzarella for your tiramisu needs!"

Sushi Master: "Big party order coming, need extra rice?"  
Thai Chef: "I have jasmine rice, sending some over!"

Burger Joint: "Fryer is broken, can't make fries!"
API Gateway: "Routing all burger+fries orders to Fish & Chips shop!"

Benefits:
- Instant communication between all restaurants
- Share resources when needed
- Coordinate on big orders  
- Alert everyone about problems
- Monitor each other's health and status
```

---

## 🏗️ Principal Architect Depth: Distributed System Coordination

### 🚨 The Microservices Communication Challenges

#### Challenge 1: Service Discovery Problem
```
Problem: With 500+ microservices, how do they find each other?

Traditional Approach (Hard-coded):
Service A needs Service B → Calls http://service-b:8080/api
Problems:
├─ Service B moves to different server → Service A breaks
├─ Service B scales to 10 instances → Service A only knows 1
├─ Service B goes down → Service A has no fallback
└─ New Service B version deployed → Service A calls old version

Modern Service Discovery:
Service A → Service Registry → "Where is Service B?"
Service Registry → "Service B has 5 healthy instances:"
├─ 10.0.1.15:8080 (load: 20%, latency: 5ms)
├─ 10.0.1.23:8080 (load: 30%, latency: 3ms) ← Best option
├─ 10.0.1.41:8080 (load: 60%, latency: 8ms)
├─ 10.0.1.67:8080 (load: 10%, latency: 2ms) ← Even better!
└─ 10.0.1.89:8080 (load: 40%, latency: 6ms)

Service A → Calls best available instance → Gets fast response!
```

#### Challenge 2: Cascade Failure Prevention
```
The Domino Effect Problem:

Payment Service → Order Service → Inventory Service → Database
     ↓              ↓              ↓                ↓
   Healthy        Healthy        Slow!         Overloaded!

Without Circuit Breakers:
1. Database slows down (2 seconds per query)
2. Inventory Service queues up requests (10 second timeout)
3. Order Service waits for Inventory (30 second timeout)  
4. Payment Service waits for Order (60 second timeout)
5. User waits 60+ seconds → Gives up → Bad experience!
6. Meanwhile, 1000s more requests pile up → System crashes!

With Circuit Breakers:
Payment Service → Order Service → Inventory Service → Database (slow)
                                        ↓
                             Circuit Breaker: "Database is slow!"
                                        ↓
                             Return cached inventory data (100ms)
                                        ↓
                 Order placed with "pending inventory check"
                                        ↓
               User gets confirmation in 200ms instead of 60 seconds!

Circuit Breaker States:
├─ CLOSED: Normal operation, all requests pass through
├─ OPEN: Failure detected, block requests, return fallback  
└─ HALF-OPEN: Test if service recovered, gradually allow requests
```

### 🌐 Service Communication Patterns

#### Pattern 1: Synchronous Communication (Request-Response)
```
HTTP/REST API Pattern:
Client → HTTP Request → Service → Process → HTTP Response → Client

Advantages:
├─ Simple to understand and debug
├─ Immediate response and error handling
├─ Easy to test and mock
└─ Works with existing web infrastructure

Disadvantages:  
├─ Tight coupling between services
├─ Blocking operations (client waits)
├─ Cascade failures propagate quickly
└─ Hard to scale under high load

Best For:
├─ User-facing operations (login, search, view profile)
├─ Real-time data retrieval  
├─ Critical business logic requiring immediate response
└─ Simple CRUD operations
```

#### Pattern 2: Asynchronous Communication (Message Queues)
```
Event-Driven Pattern:
Producer → Message Queue → Consumer(s) → Process Async

Message Flow:
Order Service → "OrderCreated" event → Queue
                    ↓
Queue distributes to:
├─ Inventory Service → "Reserve items"  
├─ Payment Service → "Process payment"
├─ Shipping Service → "Prepare shipment"
├─ Analytics Service → "Record metrics"
└─ Email Service → "Send confirmation"

Advantages:
├─ Loose coupling (services don't know about each other)
├─ Non-blocking (producer continues immediately)  
├─ Resilient (messages stored until processed)
├─ Scalable (add more consumers to handle load)
└─ Reliable (message delivery guarantees)

Disadvantages:
├─ Complex debugging (async flow)
├─ Eventual consistency (not immediate)
├─ Message ordering challenges
└─ Infrastructure overhead (queue management)

Best For:
├─ Background processing (image resizing, email sending)
├─ Event sourcing and audit trails
├─ Fan-out scenarios (one event, many actions)
└─ High-throughput, eventually consistent operations
```

#### Pattern 3: Hybrid Communication (CQRS + Event Sourcing)
```
Command Query Responsibility Segregation:

Write Side (Commands):
User Action → Command Service → Event Store → Events Published
                                    ↓
                              Read Models Updated

Read Side (Queries):  
User Query → Query Service → Read Model → Fast Response

Example: E-commerce Order System
Write: "PlaceOrder" command → OrderCreated, PaymentRequested, InventoryReserved events
Read: "GetOrder" query → Pre-built order view with all details

Advantages:
├─ Optimal performance for reads and writes
├─ Complete audit trail of all changes
├─ Scale reads and writes independently  
└─ Easy to add new features (just add event handlers)

Complexity Trade-offs:
├─ More complex architecture
├─ Eventual consistency between read/write sides
├─ Event schema evolution challenges
└─ Requires sophisticated monitoring
```

---

## 🌍 Real-World Implementation Examples

### 📊 Case Study 1: Netflix's Microservices Architecture

**The Scale**: 500+ microservices serving 230M+ subscribers

```
Netflix's Service Communication Architecture:

API Gateway Layer (Zuul):
├─ Handles 2+ billion requests per day
├─ Routes to 500+ backend services
├─ Implements circuit breakers, rate limiting, authentication
├─ A/B testing and canary deployments
└─ Real-time monitoring and alerting

Service Discovery (Eureka):
├─ 50,000+ service instances register themselves
├─ Health checks every 30 seconds
├─ Automatic instance removal on failure
├─ Load balancing with zone awareness
└─ Graceful shutdown coordination

Inter-Service Communication:
├─ Ribbon: Client-side load balancing
├─ Hystrix: Circuit breakers and fallbacks  
├─ Feign: Declarative REST clients
├─ RxJava: Reactive programming for async operations
└─ Chaos Monkey: Intentional failure testing

Message Queue Architecture (Apache Kafka):
├─ 4 trillion events per day
├─ 700+ billion events stored  
├─ Real-time stream processing
├─ Event sourcing for user interactions
└─ Analytics and machine learning pipelines
```

**Netflix's Communication Innovations**:
```
Hystrix Circuit Breaker Pattern:

Normal Operation:
User Request → API Gateway → Recommendation Service → User Profile Service
                ↓                      ↓                        ↓
           Fast Response         ML Algorithms           User Data (50ms)

Service Degradation:
User Request → API Gateway → Recommendation Service → User Profile Service (Slow!)
                ↓                      ↓                        ↓
         Circuit OPEN!         Use Cached Data        Service Timeout (5s)
                ↓                      ↓
         Fallback Response     Popular Content

Business Impact:
├─ 99.99% uptime despite individual service failures
├─ Graceful degradation (popular content vs personalized)  
├─ User never sees error pages
└─ Revenue protected during partial outages

Performance Metrics:
├─ Average API response: <100ms  
├─ Circuit breaker triggers: <0.1% of requests
├─ Fallback success rate: 99.9%
└─ User satisfaction maintained during outages
```

### 📊 Case Study 2: Uber's Service Mesh (Envoy + gRPC)

**The Challenge**: Coordinate 4,000+ microservices across 8 data centers

```
Uber's Service Communication Stack:

Service Mesh (Envoy Proxy):
├─ Every service gets Envoy sidecar
├─ 40,000+ Envoy proxies deployed
├─ Handles 100M+ requests per minute
├─ Traffic routing, load balancing, retries
├─ End-to-end encryption (mTLS)
├─ Circuit breaking and timeout management
└─ Observability (metrics, logs, traces)

gRPC for Internal Communication:
├─ Protocol Buffers for efficient serialization
├─ HTTP/2 multiplexing for performance
├─ Strongly-typed service contracts
├─ Automatic client generation in 10+ languages
├─ Built-in load balancing and health checking
└─ Streaming for real-time updates

Service Discovery (uDiscovery):
├─ DNS-based service resolution
├─ Health checking with custom probes
├─ Geographic awareness (route to closest instance)
├─ Blue-green deployment support
├─ Traffic shifting for canary releases
└─ Automatic failover between data centers
```

**Uber's Real-World Performance**:
```
Service Communication Metrics:

Latency Improvements:
├─ P50 latency: 15ms (vs 45ms without service mesh)
├─ P99 latency: 100ms (vs 2000ms without circuit breakers)
├─ Cross-datacenter calls: 50ms (vs 200ms without optimization)
└─ Service startup time: 5s (vs 30s without service discovery)

Reliability Improvements:
├─ Service availability: 99.99% (vs 99.5% without circuit breakers)  
├─ Cascade failure prevention: 99.9% effective
├─ Load balancing efficiency: 95% optimal routing
└─ Health check accuracy: 99.8% correct decisions

Developer Productivity:
├─ Service deployment time: 5 minutes (vs 30 minutes)
├─ New service creation: 2 hours (vs 2 days)  
├─ Cross-team API integration: 1 day (vs 1 week)
└─ Production debugging time: 80% reduction
```

### 📊 Case Study 3: Google's Service Mesh (Istio)

**The Innovation**: Open-source service mesh managing traffic for billions of users

```
Google's Istio Architecture:

Control Plane:
├─ Pilot: Service discovery and traffic management
├─ Citadel: Certificate management and security policies
├─ Galley: Configuration validation and distribution  
├─ Mixer: Policy enforcement and telemetry collection
└─ Istiod: Unified control plane (Istio 1.5+)

Data Plane (Envoy Sidecars):
├─ Intercepts all network traffic
├─ Enforces routing rules and policies
├─ Collects metrics and traces
├─ Provides security (mTLS, RBAC)
├─ Load balancing and circuit breaking
└─ Protocol translation (HTTP/1.1, HTTP/2, gRPC)

Traffic Management Features:
├─ Canary deployments: Route 5% traffic to new version
├─ A/B testing: Route based on user attributes
├─ Fault injection: Test resilience with artificial delays
├─ Traffic mirroring: Copy production traffic to test environment
├─ Circuit breakers: Prevent cascade failures
└─ Retries and timeouts: Configurable failure handling
```

---

## 🧪 Hands-On Lab: Build Microservices Communication

### 🔍 Experiment 1: Service Discovery with Consul

**Setup service discovery and health checking:**

```python
# Service Discovery with Consul
import consul
import requests
import time
import threading
from flask import Flask, jsonify
import random

class ServiceRegistry:
    def __init__(self, consul_host='localhost', consul_port=8500):
        self.consul = consul.Consul(host=consul_host, port=consul_port)
    
    def register_service(self, name, host, port, health_check_url=None):
        """Register a service with Consul"""
        service_id = f"{name}-{host}-{port}"
        
        check = None
        if health_check_url:
            check = consul.Check.http(health_check_url, interval="10s")
        
        self.consul.agent.service.register(
            name=name,
            service_id=service_id,
            address=host,
            port=port,
            check=check
        )
        return service_id
    
    def discover_service(self, service_name):
        """Discover healthy instances of a service"""
        _, services = self.consul.health.service(service_name, passing=True)
        
        instances = []
        for service in services:
            instances.append({
                'host': service['Service']['Address'],
                'port': service['Service']['Port'],
                'id': service['Service']['ID']
            })
        
        return instances
    
    def deregister_service(self, service_id):
        """Deregister a service"""
        self.consul.agent.service.deregister(service_id)

# Example microservice with health checks
class UserService:
    def __init__(self, host='localhost', port=5001):
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        self.registry = ServiceRegistry()
        self.healthy = True
        self.service_id = None
        
        self._setup_routes()
    
    def _setup_routes(self):
        @self.app.route('/health')
        def health_check():
            if self.healthy:
                return jsonify({'status': 'healthy', 'service': 'user-service'})
            else:
                return jsonify({'status': 'unhealthy'}), 503
        
        @self.app.route('/users/<user_id>')
        def get_user(user_id):
            # Simulate processing time
            time.sleep(random.uniform(0.01, 0.1))
            
            if not self.healthy:
                return jsonify({'error': 'Service unhealthy'}), 503
                
            return jsonify({
                'user_id': user_id,
                'name': f'User {user_id}',
                'email': f'user{user_id}@example.com',
                'service_instance': f'{self.host}:{self.port}'
            })
        
        @self.app.route('/toggle-health')
        def toggle_health():
            self.healthy = not self.healthy
            status = 'healthy' if self.healthy else 'unhealthy'
            return jsonify({'status': status})
    
    def start(self):
        # Register with service discovery
        health_url = f'http://{self.host}:{self.port}/health'
        self.service_id = self.registry.register_service(
            'user-service', self.host, self.port, health_url
        )
        
        print(f"User service starting on {self.host}:{self.port}")
        print(f"Registered with service ID: {self.service_id}")
        
        # Start Flask app
        self.app.run(host=self.host, port=self.port, debug=False)

# API Gateway with service discovery
class APIGateway:
    def __init__(self, host='localhost', port=8080):
        self.app = Flask(__name__)
        self.host = host  
        self.port = port
        self.registry = ServiceRegistry()
        
        self._setup_routes()
    
    def _setup_routes(self):
        @self.app.route('/api/users/<user_id>')
        def proxy_user_request(user_id):
            # Discover user service instances
            instances = self.registry.discover_service('user-service')
            
            if not instances:
                return jsonify({'error': 'User service unavailable'}), 503
            
            # Simple load balancing (random selection)
            instance = random.choice(instances)
            
            try:
                # Proxy request to service instance
                url = f"http://{instance['host']}:{instance['port']}/users/{user_id}"
                response = requests.get(url, timeout=5)
                
                return jsonify({
                    'data': response.json(),
                    'routed_to': f"{instance['host']}:{instance['port']}",
                    'response_time_ms': response.elapsed.total_seconds() * 1000
                })
                
            except requests.RequestException as e:
                return jsonify({
                    'error': 'Service request failed',
                    'details': str(e)
                }), 502
        
        @self.app.route('/health')
        def gateway_health():
            return jsonify({'status': 'healthy', 'service': 'api-gateway'})
    
    def start(self):
        print(f"API Gateway starting on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=False)

# Test the service discovery system
if __name__ == "__main__":
    # Start multiple user service instances
    import multiprocessing
    
    def start_user_service(port):
        service = UserService(port=port)
        service.start()
    
    def start_api_gateway():
        gateway = APIGateway()
        gateway.start()
    
    # Start services in separate processes
    processes = []
    
    # Start 3 user service instances
    for port in [5001, 5002, 5003]:
        p = multiprocessing.Process(target=start_user_service, args=(port,))
        p.start()
        processes.append(p)
    
    # Start API gateway
    gateway_process = multiprocessing.Process(target=start_api_gateway)
    gateway_process.start()
    processes.append(gateway_process)
    
    # Wait for all processes
    for p in processes:
        p.join()
```

### 🔍 Experiment 2: Circuit Breaker Implementation

**Build resilient service communication:**

```python
import time
import threading
from enum import Enum
from dataclasses import dataclass
from typing import Callable, Any, Optional
import random

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failure mode, blocking requests
    HALF_OPEN = "half_open"  # Testing recovery

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5      # Number of failures to open circuit
    success_threshold: int = 3      # Number of successes to close circuit  
    timeout: float = 60.0          # Seconds to wait before trying half-open
    expected_exception: type = Exception

class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        with self.lock:
            # Check if we should transition from OPEN to HALF_OPEN
            if (self.state == CircuitState.OPEN and 
                self.last_failure_time and 
                time.time() - self.last_failure_time >= self.config.timeout):
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                print(f"Circuit breaker entering HALF_OPEN state")
        
        # Block requests if circuit is OPEN
        if self.state == CircuitState.OPEN:
            raise CircuitOpenException("Circuit breaker is OPEN")
        
        try:
            # Execute the protected function
            result = func(*args, **kwargs)
            
            # Record success
            with self.lock:
                self.failure_count = 0
                if self.state == CircuitState.HALF_OPEN:
                    self.success_count += 1
                    if self.success_count >= self.config.success_threshold:
                        self.state = CircuitState.CLOSED
                        print(f"Circuit breaker CLOSED - service recovered")
            
            return result
            
        except self.config.expected_exception as e:
            # Record failure
            with self.lock:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.config.failure_threshold:
                    self.state = CircuitState.OPEN
                    print(f"Circuit breaker OPEN - too many failures")
                elif self.state == CircuitState.HALF_OPEN:
                    self.state = CircuitState.OPEN
                    print(f"Circuit breaker OPEN - half-open test failed")
            
            raise e
    
    def get_state(self):
        return {
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure_time': self.last_failure_time
        }

class CircuitOpenException(Exception):
    pass

# Resilient HTTP client with circuit breaker
class ResilientHTTPClient:
    def __init__(self):
        self.circuit_breakers = {}
        self.default_config = CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=2,
            timeout=30.0,
            expected_exception=requests.RequestException
        )
    
    def get_circuit_breaker(self, service_name):
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker(self.default_config)
        return self.circuit_breakers[service_name]
    
    def call_service(self, service_name, url, timeout=5):
        """Make HTTP request with circuit breaker protection"""
        circuit = self.get_circuit_breaker(service_name)
        
        def make_request():
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        
        try:
            return circuit.call(make_request)
        except CircuitOpenException:
            # Return fallback response when circuit is open
            return self.get_fallback_response(service_name)
    
    def get_fallback_response(self, service_name):
        """Provide fallback data when service is unavailable"""
        fallbacks = {
            'user-service': {
                'user_id': 'unknown',
                'name': 'Anonymous User',
                'email': 'user@example.com',
                'fallback': True,
                'reason': 'User service circuit breaker open'
            },
            'recommendation-service': {
                'recommendations': ['Popular Item 1', 'Popular Item 2'],
                'fallback': True,
                'reason': 'Recommendation service circuit breaker open'
            }
        }
        
        return fallbacks.get(service_name, {
            'error': 'Service unavailable',
            'fallback': True,
            'service': service_name
        })
    
    def get_circuit_status(self):
        """Get status of all circuit breakers"""
        status = {}
        for service_name, circuit in self.circuit_breakers.items():
            status[service_name] = circuit.get_state()
        return status

# Test circuit breaker behavior
def simulate_unreliable_service():
    """Simulate a service that fails randomly"""
    if random.random() < 0.7:  # 70% failure rate
        raise requests.RequestException("Simulated service failure")
    return {'data': 'success', 'timestamp': time.time()}

# Example usage
client = ResilientHTTPClient()

print("Testing circuit breaker behavior:")
for i in range(20):
    try:
        result = client.call_service('test-service', 'http://fake-service/api')
        print(f"Request {i+1}: SUCCESS - {result}")
    except Exception as e:
        print(f"Request {i+1}: FAILED - {str(e)}")
    
    # Show circuit breaker status
    if (i + 1) % 5 == 0:
        print(f"\nCircuit Status: {client.get_circuit_status()}\n")
    
    time.sleep(1)
```

### 🔍 Experiment 3: API Gateway with Rate Limiting

**Implement traffic control and routing:**

```python
import time
from flask import Flask, request, jsonify
from functools import wraps
import redis
import hashlib
import json

class RateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def is_allowed(self, key, limit, window_seconds):
        """Token bucket rate limiting algorithm"""
        now = time.time()
        pipeline = self.redis.pipeline()
        
        # Remove expired timestamps
        pipeline.zremrangebyscore(key, 0, now - window_seconds)
        
        # Count current requests
        pipeline.zcard(key)
        
        # Add current request
        pipeline.zadd(key, {str(now): now})
        
        # Set expiration
        pipeline.expire(key, window_seconds)
        
        results = pipeline.execute()
        current_count = results[1]
        
        return current_count < limit

class APIGatewayAdvanced:
    def __init__(self, redis_url='redis://localhost:6379'):
        self.app = Flask(__name__)
        self.redis = redis.from_url(redis_url)
        self.rate_limiter = RateLimiter(self.redis)
        
        # Service routing configuration
        self.routes = {
            '/api/users': {
                'service': 'user-service',
                'upstream': 'http://localhost:5001',
                'rate_limit': {'requests': 100, 'window': 60},  # 100 req/min
                'timeout': 5
            },
            '/api/orders': {
                'service': 'order-service', 
                'upstream': 'http://localhost:5002',
                'rate_limit': {'requests': 50, 'window': 60},   # 50 req/min
                'timeout': 10
            }
        }
        
        self._setup_middleware()
        self._setup_routes()
    
    def _setup_middleware(self):
        @self.app.before_request
        def before_request():
            # Authentication check
            if not self._is_authenticated():
                return jsonify({'error': 'Authentication required'}), 401
            
            # Rate limiting check  
            if not self._check_rate_limit():
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': 60
                }), 429
    
    def _is_authenticated(self):
        """Simple API key authentication"""
        api_key = request.headers.get('X-API-Key')
        # In production, validate against database/cache
        return api_key in ['dev-key-123', 'prod-key-456']
    
    def _check_rate_limit(self):
        """Check if request is within rate limits"""
        client_id = self._get_client_id()
        path_prefix = self._get_path_prefix()
        
        if path_prefix in self.routes:
            config = self.routes[path_prefix]
            rate_limit = config['rate_limit']
            
            key = f"rate_limit:{client_id}:{path_prefix}"
            return self.rate_limiter.is_allowed(
                key, 
                rate_limit['requests'],
                rate_limit['window']
            )
        
        return True  # No rate limit configured
    
    def _get_client_id(self):
        """Identify client for rate limiting"""
        api_key = request.headers.get('X-API-Key', 'anonymous')
        client_ip = request.remote_addr
        return hashlib.md5(f"{api_key}:{client_ip}".encode()).hexdigest()
    
    def _get_path_prefix(self):
        """Get routing path prefix"""
        path = request.path
        for prefix in self.routes.keys():
            if path.startswith(prefix):
                return prefix
        return None
    
    def _setup_routes(self):
        @self.app.route('/api/users', defaults={'path': ''})
        @self.app.route('/api/users/<path:path>')
        def proxy_users(path):
            return self._proxy_request('/api/users', path)
        
        @self.app.route('/api/orders', defaults={'path': ''})
        @self.app.route('/api/orders/<path:path>')  
        def proxy_orders(path):
            return self._proxy_request('/api/orders', path)
        
        @self.app.route('/gateway/status')
        def gateway_status():
            return jsonify({
                'status': 'healthy',
                'routes': list(self.routes.keys()),
                'timestamp': time.time()
            })
        
        @self.app.route('/gateway/metrics')
        def gateway_metrics():
            # Get rate limiting metrics
            metrics = {}
            for route in self.routes.keys():
                # This would be more sophisticated in production
                metrics[route] = {
                    'requests_per_minute': 'N/A',  # Would track actual metrics
                    'error_rate': 'N/A',
                    'average_latency': 'N/A'
                }
            return jsonify(metrics)
    
    def _proxy_request(self, prefix, path):
        """Proxy request to upstream service"""
        if prefix not in self.routes:
            return jsonify({'error': 'Route not found'}), 404
        
        config = self.routes[prefix]
        upstream_url = f"{config['upstream']}/{path}"
        
        try:
            # Build request parameters
            params = dict(request.args)
            headers = dict(request.headers)
            
            # Remove hop-by-hop headers
            headers.pop('Host', None)
            headers.pop('Content-Length', None)
            
            # Make upstream request
            start_time = time.time()
            
            if request.method == 'GET':
                response = requests.get(
                    upstream_url, 
                    params=params, 
                    headers=headers,
                    timeout=config['timeout']
                )
            elif request.method == 'POST':
                response = requests.post(
                    upstream_url,
                    json=request.get_json(),
                    headers=headers,
                    timeout=config['timeout']
                )
            else:
                return jsonify({'error': 'Method not allowed'}), 405
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Return response with gateway headers
            result = response.json() if response.content else {}
            result['_gateway'] = {
                'service': config['service'],
                'latency_ms': round(latency_ms, 2),
                'status_code': response.status_code
            }
            
            return jsonify(result), response.status_code
            
        except requests.Timeout:
            return jsonify({
                'error': 'Service timeout',
                'service': config['service']
            }), 504
        
        except requests.RequestException as e:
            return jsonify({
                'error': 'Service unavailable',
                'service': config['service'],
                'details': str(e)
            }), 502
    
    def start(self, host='localhost', port=8080):
        print(f"Advanced API Gateway starting on {host}:{port}")
        print(f"Configured routes: {list(self.routes.keys())}")
        self.app.run(host=host, port=port, debug=False)

# Example usage
if __name__ == "__main__":
    gateway = APIGatewayAdvanced()
    gateway.start()
```

---

## 🎨 Visual Learning: Microservices Communication Architecture

### 🌐 Service Communication Flow
```
Microservices Communication Patterns:

Synchronous Communication (Request-Response):
┌─────────────┐    HTTP/gRPC     ┌─────────────┐
│   Client    │ ──────────────→  │  Service A  │
│ Application │                  │ (User API)  │
└─────────────┘                  └─────────────┘
       ↓                                ↓
   Waits for                    ┌─────────────┐
   response                     │  Service B  │ ← Calls synchronously
   (Blocking)                   │ (Database)  │
                               └─────────────┘

Asynchronous Communication (Event-Driven):
┌─────────────┐    Publish Event  ┌─────────────┐
│   Service   │ ──────────────→   │ Message     │
│  Producer   │                   │ Queue       │
└─────────────┘                   └─────────────┘
                                        ↓
                              ┌─────────────────────┐
                              │  Multiple Consumers │
                              │ ┌─────┐ ┌─────────┐ │
                              │ │Svc C│ │ Svc D   │ │
                              │ └─────┘ └─────────┘ │
                              └─────────────────────┘
```

### 🔄 Circuit Breaker State Machine
```
Circuit Breaker State Transitions:

    ┌──────────────────────────────────────────────┐
    │                 CLOSED                        │
    │        (Normal Operation)                     │
    │                                              │
    │ • All requests pass through                  │
    │ • Monitor success/failure rates              │
    │ • Count consecutive failures                 │
    └──────────────┬───────────────────────────────┘
                   │
                   │ Failure threshold exceeded
                   │ (e.g., 5 failures in 10 requests)
                   ↓
    ┌──────────────────────────────────────────────┐
    │                  OPEN                        │
    │           (Circuit Tripped)                  │
    │                                              │
    │ • Block all requests immediately             │
    │ • Return fallback/cached response            │
    │ • Start timeout timer                       │
    └──────────────┬───────────────────────────────┘
                   │
                   │ Timeout period elapsed
                   │ (e.g., 60 seconds)
                   ↓
    ┌──────────────────────────────────────────────┐
    │               HALF-OPEN                      │
    │           (Testing Recovery)                 │
    │                                              │
    │ • Allow limited requests through             │
    │ • Monitor success rate closely               │
    │ • Ready to close or re-open                 │
    └──┬─────────────────────────────────────────┬─┘
       │                                         │
       │ Success threshold met                   │ Any failure occurs
       │ (e.g., 3 successes)                   │
       ↓                                         ↓
   Back to CLOSED                          Back to OPEN
   (Service recovered)                   (Service still failing)
```

### 🕸️ Service Mesh Architecture
```
Service Mesh Communication Layer:

┌─────────────────────────────────────────────────────────────┐
│                    Control Plane                            │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐│
│ │   Pilot     │ │   Citadel   │ │   Galley    │ │ Mixer   ││
│ │(Discovery)  │ │(Security)   │ │(Config)     │ │(Policy) ││
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘│
└─────────────────────────────────────────────────────────────┘
                             │
                   Configuration & Policies
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                    Data Plane                               │
│                                                            │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐           │
│  │Service A │     │Service B │     │Service C │           │
│  │    +     │←───→│    +     │←───→│    +     │           │
│  │ Sidecar  │     │ Sidecar  │     │ Sidecar  │           │
│  │(Envoy)   │     │(Envoy)   │     │(Envoy)   │           │
│  └──────────┘     └──────────┘     └──────────┘           │
│                                                            │
│ Each sidecar handles:                                      │
│ • Traffic routing & load balancing                         │
│ • Security (mTLS, RBAC)                                   │
│ • Observability (metrics, logs, traces)                   │
│ • Reliability (retries, circuit breakers, timeouts)       │
└─────────────────────────────────────────────────────────────┘

Benefits:
├─ Uniform communication layer across all services
├─ Security and observability without code changes
├─ Traffic management and deployment strategies
└─ Language-agnostic (works with any service)
```

---

## 🎯 Week 8 Wrap-Up: Microservices Communication Mastery

### 🧠 Mental Models to Internalize

1. **Service Discovery = Phone Directory**: Services register themselves and find others dynamically
2. **Circuit Breaker = Electrical Safety**: Prevent system-wide failures by isolating problems
3. **API Gateway = Hotel Concierge**: Single entry point that knows how to reach every service
4. **Service Mesh = Invisible Network**: Communication infrastructure that works behind the scenes

### 🏆 Principal Architect Decision Framework

**Communication Pattern Selection:**
- **Synchronous (REST/gRPC)**: User-facing APIs, real-time requirements, simple request-response
- **Asynchronous (Events/Queues)**: Background processing, fan-out scenarios, eventual consistency
- **Hybrid (CQRS)**: High-scale systems needing both read and write optimization

**Service Mesh vs API Gateway:**
- **API Gateway**: External traffic, authentication, rate limiting, protocol translation
- **Service Mesh**: Internal service communication, security, observability, traffic management

### 🚨 Common Microservices Communication Mistakes

❌ **Chatty interfaces** = Too many small API calls instead of batched requests
❌ **No circuit breakers** = Cascade failures bring down entire system
❌ **Synchronous chains** = Long chains of blocking calls create bottlenecks
❌ **No service discovery** = Hard-coded service locations break during deployment
✅ **Bulkhead pattern** = Isolate critical resources to prevent resource exhaustion

### 🔮 Preview: Advanced Phase (Weeks 9-12)
**Week 9: Global DNS Routing - Intelligent Traffic Direction**

We'll dive into how global services route users to optimal data centers. You'll learn about anycast, GeoDNS, and the routing strategies that ensure users always connect to the fastest available infrastructure.

---

## 🤔 Reflection Questions

Before moving to Week 9, ensure you can answer:

1. **ELI5**: "Why does Netflix still work perfectly when your friend's favorite streaming service goes down during the big game?"

2. **Architect Level**: "Design a communication strategy for a food delivery app with 100+ microservices handling orders, payments, tracking, and recommendations simultaneously."

3. **Technical Deep-Dive**: "Your circuit breakers are triggering frequently but the backend services report they're healthy. What could be causing this and how do you investigate?"

4. **Business Analysis**: "Calculate the cost-benefit of implementing a service mesh for a company with 200 microservices, considering development time, infrastructure overhead, and operational improvements."

---

*"In microservices, the network is the computer - and managing that network communication determines whether you build the next Netflix or the next failure story."*

**Next**: [Week 9 - Global DNS Routing](09-Week9-Global-DNS-Routing.md)