# Week 11: Performance Optimization & Global Monitoring 📊🔍

*"You can't optimize what you don't measure - and measuring a global system is like being a detective with sensors on every street corner of the planet"*

## 🎯 This Week's Mission
Master performance optimization techniques and monitoring strategies for global-scale systems. Learn to measure, analyze, and optimize distributed architectures, building comprehensive observability into edge computing platforms.

---

## 📋 Prerequisites: Building on Previous Weeks

You should now understand:
- ✅ **Edge Computing**: Distributed computation at network edge
- ✅ **Anycast Networks**: BGP routing and global distribution
- ✅ **Caching Hierarchies**: Multi-layer storage optimization
- ✅ **Microservices**: Distributed system communication

### New Concepts We'll Master
- **Observability Pillars**: Metrics, logs, traces, and profiles
- **Real User Monitoring (RUM)**: Measuring actual user experience
- **Synthetic Monitoring**: Proactive testing from global locations
- **Performance Budgets**: Setting and enforcing speed targets

---

## 🎪 Explain Like I'm 10: The World's Smartest Traffic System

### 🚦 The Old Way: Guessing About Traffic (No Monitoring)

Imagine a city with **no traffic cameras or sensors**:

```
🏙️ Mystery City Problems:

Traffic Jam on Main Street:
Mayor: "Is there a traffic jam?"
Assistant: "I don't know, let me drive there..."
   ↓ (30 minutes later)
Assistant: "Yes, but it's cleared now!"
Mayor: "Too late to help!"

Rush Hour Questions:
- Which roads are slowest? → Unknown
- Where do accidents happen? → No data
- When should we add lanes? → Just guessing
- Are traffic lights working? → Drive around to check

Result: City always congested, nobody knows why!
```

### 🎯 The Smart Way: City-Wide Monitoring System

Now imagine a **super-smart city with sensors everywhere**:

```
🌟 Smart City Monitoring:

Real-Time Traffic Cameras:
├─ 1,000 cameras watching every major intersection
├─ Automatic car counting every 10 seconds
├─ Speed detection on all highways
└─ Live video feeds to control center

Smart Traffic Lights:
├─ Sensors detecting waiting cars
├─ Automatic timing adjustments
├─ Coordination between intersections  
└─ Emergency vehicle priority

Mobile App Data:
├─ Every driver's phone reports their speed
├─ Anonymous location tracking
├─ Automatic slow-down detection
└─ Crowd-sourced accident reporting

Control Center Dashboard:
┌────────────────────────────────────────┐
│  🚦 LIVE CITY TRAFFIC MONITOR          │
├────────────────────────────────────────┤
│  Average Speed: 35 mph ✓               │
│  Main Street: SLOW (15 mph) ⚠️         │
│  Highway 101: FAST (60 mph) ✓         │
│  Accidents Today: 2 (both cleared)     │
│  Traffic Lights: 98% working ✓        │
│  Peak Hour: 5:00 PM (in 2 hours)      │
└────────────────────────────────────────┘
```

### 📊 Three Types of City Monitoring

**1. Real User Monitoring (Actual Drivers)**
```
Every Car Reports Its Experience:

Car A: "Main Street → Office took 25 minutes"
Car B: "Same route took 40 minutes" ⚠️
Car C: "Same route took 22 minutes"

Control Center Analysis:
- Average commute: 29 minutes
- Car B experienced delay (accident?)  
- 80% of drivers under 30 minutes ✓
- Need to investigate Car B's route
```

**2. Synthetic Monitoring (Test Drivers)**
```
Robot Cars Test Routes Every Hour:

Test Car 1: Drives Main Street route
   → Measures: Traffic lights, road quality, travel time
   → Reports: "All green lights working, 20 min travel time"

Test Car 2: Drives Highway 101
   → Measures: Speed limits, lane availability
   → Reports: "3 lanes open, 65 mph average speed"

Benefits:
- Tests routes even when nobody's driving
- Detects problems before real users affected
- Provides baseline performance expectations
```

**3. Performance Tracing (Following One Car's Journey)**
```
Follow Car X's Complete Trip:

🏠 Home (0:00)
   ↓ Start car: 30 seconds
🚦 Intersection A (2:15)
   ↓ Wait at light: 45 seconds  
🚦 Intersection B (5:30)
   ↓ Green light, no wait
🛣️ Highway entrance (7:45)
   ↓ Slow merge: 90 seconds
🏢 Office (22:10)

Total time: 22 minutes 10 seconds
Delays identified:
- Intersection A light (45 sec)
- Highway merge (90 sec)
Action: Fix these two bottlenecks!
```

### 🔧 Smart Optimization Based on Data

```
Problem Detected: Main Street Always Slow

Old Approach (Guessing):
Mayor: "Let's add more lanes everywhere!"
Cost: $10 million
Result: Still slow (wrong diagnosis!)

Smart Approach (Data-Driven):
1. Analyze data: "Traffic jams at Intersection A from 8-9 AM"
2. Root cause: "One traffic light timing causes backup"
3. Solution: "Extend green light by 15 seconds"
4. Cost: $0 (just reprogram light)
5. Result: 40% faster commutes!

Benefits of Monitoring:
✓ Find real problems (not guesses)
✓ Fix cheaply and effectively
✓ Measure improvement
✓ Prevent future issues
```

---

## 🏗️ Principal Architect Depth: Global Observability at Scale

### 🚨 The Observability Challenge at Global Scale

#### The Three Pillars of Observability
```
Observability Stack for Distributed Systems:

Pillar 1: Metrics (Quantitative Measurements)
├─ Time-series data (numbers over time)
├─ Aggregatable and mathematical operations
├─ Examples:
│   ├─ Request rate: 10,000 requests/second
│   ├─ Error rate: 0.1% (10 errors/second)
│   ├─ Latency P95: 250ms
│   ├─ CPU usage: 65%
│   └─ Cache hit rate: 94%
├─ Collection frequency: Every 10-60 seconds
├─ Retention: 30-90 days (aggregated), 1 year (downsampled)
└─ Tools: Prometheus, InfluxDB, Datadog, CloudWatch

Pillar 2: Logs (Discrete Events)
├─ Structured or unstructured text records
├─ Rich context about specific events
├─ Examples:
│   ├─ "User 12345 logged in from IP 203.0.113.50"
│   ├─ "Payment transaction 9876 failed: insufficient funds"
│   ├─ "Edge server tokyo-1 health check failed"
│   ├─ "Cache miss for key: user_profile_12345"
│   └─ "Database query took 2.5s: SELECT * FROM..."
├─ Collection: Real-time streaming
├─ Retention: 7-30 days (expensive to store)
└─ Tools: ELK Stack, Splunk, Loki, CloudWatch Logs

Pillar 3: Traces (Request Journeys)
├─ Distributed request tracking across services
├─ Shows complete path and timing of requests
├─ Example trace:
│   User Request (Total: 245ms)
│   ├─ API Gateway: 5ms
│   ├─ Auth Service: 20ms
│   ├─ User Service: 35ms
│   │   ├─ Cache check: 2ms (hit)
│   │   └─ Response build: 33ms
│   ├─ Recommendation Service: 180ms ← Bottleneck!
│   │   ├─ ML model inference: 150ms
│   │   └─ Result formatting: 30ms
│   └─ Response aggregation: 5ms
├─ Sampling: 1-100% of requests (configurable)
├─ Retention: 7-14 days
└─ Tools: Jaeger, Zipkin, AWS X-Ray, OpenTelemetry

Pillar 4: Profiles (Resource Usage)
├─ Continuous CPU/memory profiling
├─ Identifies performance bottlenecks in code
├─ Examples:
│   ├─ Function X uses 30% of CPU time
│   ├─ JSON parsing consumes 200MB memory
│   ├─ Database queries blocked 40% of time
│   └─ Garbage collection pauses: 50ms average
├─ Collection: Sampling profiler (low overhead)
├─ Retention: 7-30 days
└─ Tools: pprof, pyroscope, Datadog Profiler
```

#### Real User Monitoring (RUM) vs Synthetic Monitoring
```
Real User Monitoring (RUM):

Data Collection:
├─ JavaScript agent in user's browser
├─ Mobile SDK in native apps
├─ Measures actual user experience
└─ Reports back to analytics platform

Metrics Captured:
├─ Page load time (PLT)
├─ First Contentful Paint (FCP)
├─ Largest Contentful Paint (LCP)
├─ First Input Delay (FID)
├─ Cumulative Layout Shift (CLS)
├─ Time to Interactive (TTI)
└─ Custom business metrics

Example RUM Data:
User Session: Tokyo User on Mobile
├─ Device: iPhone 14, iOS 17, Safari
├─ Network: 4G LTE, 50 Mbps
├─ Page load breakdown:
│   ├─ DNS lookup: 45ms
│   ├─ TCP connect: 120ms
│   ├─ TLS handshake: 180ms
│   ├─ TTFB: 250ms
│   ├─ Content download: 800ms
│   └─ DOM processing: 300ms
├─ Total PLT: 1,695ms (slow!) ⚠️
├─ JavaScript errors: 1 (uncaught exception)
└─ User converted: No (abandoned cart)

Benefits:
✓ Measures real user experience
✓ Captures all user diversity (devices, networks, locations)
✓ Correlates performance with business metrics
✓ Identifies issues affecting actual users

Limitations:
✗ Reactive (only shows what users experienced)
✗ Can't test before deployment
✗ Privacy concerns (user tracking)
✗ Affected by client-side issues

Synthetic Monitoring:

Automated Testing:
├─ Scripted robots simulate user behavior
├─ Run from multiple global locations
├─ Execute on schedule (every 1-60 minutes)
└─ Consistent test parameters

Test Scenarios:
├─ Homepage load test
├─ User login flow
├─ Product search and checkout
├─ API endpoint health checks
└─ Critical business workflows

Example Synthetic Test:
Scheduled Test: E-commerce Checkout (Every 5 min)
Locations: New York, London, Tokyo, Sydney
Browser: Chrome 120, Desktop

Test Results (Tokyo):
├─ Homepage load: 1.2s ✓
├─ Product search: 0.8s ✓
├─ Add to cart: 0.3s ✓
├─ Checkout page: 2.5s ⚠️ (slow!)
├─ Payment processing: 1.8s ✓
└─ Order confirmation: 0.9s ✓

Alert triggered: Checkout page >2s threshold

Benefits:
✓ Proactive problem detection
✓ Tests before users are affected
✓ Consistent baseline for comparison
✓ Can test from specific locations/devices

Limitations:
✗ Doesn't capture real user diversity
✗ Fixed scripts may miss edge cases
✗ Can be expensive at scale
✗ May not reflect actual usage patterns
```

### 🌐 Global Monitoring Architecture

#### Distributed Metrics Collection
```
Global Metrics Pipeline Architecture:

Edge Locations (200+ globally):
├─ Local Prometheus agents
├─ Scrape metrics every 15 seconds:
│   ├─ HTTP request rate and latency
│   ├─ Cache hit/miss rates
│   ├─ Edge function execution time
│   ├─ Network bandwidth usage
│   └─ Error rates by status code
├─ Local aggregation (1-minute rollups)
└─ Forward to regional collectors

Regional Collectors (10-15 worldwide):
├─ Receive metrics from 15-20 edge locations
├─ Additional aggregation (5-minute rollups)
├─ Query interface for regional dashboards
├─ Forward to central storage

Central Time-Series Database:
├─ Global view of all metrics
├─ Long-term storage (90+ days)
├─ Advanced querying and analytics
├─ Alerting and anomaly detection
├─ Integration with visualization tools

Data Volume Management:
├─ Raw metrics: 10 million/second globally
├─ 1-minute aggregates: 500K/second
├─ 5-minute aggregates: 100K/second
├─ 1-hour aggregates: 20K/second
├─ Storage requirements: 100TB/month raw data
└─ Compressed & aggregated: 5TB/month retained

Cardinality Control:
Problem: High-cardinality labels explode storage
├─ Bad: user_id as label (millions of unique values)
├─ Good: country as label (hundreds of unique values)
├─ Strategy: Limit labels to low-cardinality dimensions
├─ Example: Store user_id in logs, not metrics
└─ Best practice: <10 labels per metric, <100 unique values each
```

---

## 🌍 Real-World Implementation Examples

### 📊 Case Study 1: Google's Monarch Monitoring System

**The Scale**: Monitor 10+ billion metrics per second across global infrastructure

```
Google Monarch Architecture:

Data Collection:
├─ Every server runs Monarch agent
├─ Collects 1000+ metrics per server
├─ 1+ million servers worldwide
├─ 10+ billion data points per second
└─ Sub-second latency requirements

Hierarchical Aggregation:
Level 1: Machine (localhost)
├─ Aggregate metrics every 1 second
├─ Local storage: 1 minute of data
└─ Push to zone collectors

Level 2: Zone (data center section)
├─ Aggregate from 100-1000 machines
├─ Store 5-minute rollups
└─ Push to global collectors

Level 3: Global (worldwide)
├─ Aggregate from all zones
├─ Store multi-hour rollups
├─ Queryable for dashboards
└─ Power alerting systems

Query Performance:
├─ 95th percentile query latency: <100ms
├─ Queries served: 10+ million per second
├─ Data freshness: 5-10 seconds globally
├─ Availability: 99.99%
└─ Cost optimization: Aggressive downsampling

Advanced Features:
├─ Automatic anomaly detection (ML-based)
├─ Predictive alerting (problems before they happen)
├─ Capacity forecasting (when to add resources)
├─ Multi-dimensional analysis (slice data any way)
└─ Integration with Dapper (distributed tracing)
```

**Google's Monitoring Insights**:
```
Performance Optimization Workflow:

1. Identify Slow Service (RUM Data):
Alert: Search API P99 latency increased from 200ms to 500ms
Geographic Impact: Primarily affects Asia-Pacific users

2. Distributed Tracing Investigation:
Sample trace analysis (Dapper):
├─ Frontend: 10ms (normal)
├─ API Gateway: 15ms (normal)  
├─ Search Service: 450ms (SLOW!) ← Problem here
│   ├─ Cache lookup: 5ms
│   ├─ Database query: 400ms ← Root cause!
│   └─ Result formatting: 45ms
└─ Response marshaling: 25ms

3. Metrics Deep Dive:
Database metrics show:
├─ Query latency P50: 50ms (normal)
├─ Query latency P99: 400ms (high!)
├─ Connection pool: 95% utilized (nearly exhausted)
├─ Slow query log: Complex JOIN taking 300-500ms
└─ Geographic analysis: Only affects Tokyo database

4. Root Cause Analysis:
├─ Tokyo database replica out of sync
├─ Missing index on recently added column
├─ Query planner choosing wrong execution path
└─ Connection pool too small for peak load

5. Remediation:
├─ Add missing database index (immediate 80% improvement)
├─ Increase connection pool size (handle concurrency)
├─ Trigger replica resync (fix data inconsistency)
├─ Update query optimizer statistics
└─ Deploy optimized query (long-term fix)

6. Validation:
├─ P99 latency: 500ms → 180ms (64% improvement)
├─ User satisfaction: Increased by 12%
├─ Bounce rate: Decreased by 8%
└─ Revenue impact: +2.5% from improved performance

Time to Resolution: 45 minutes (detection to fix)
```

### 📊 Case Study 2: Netflix's Observability Platform

**The Innovation**: Atlas metrics + Mantis streaming analytics for real-time insights

```
Netflix Observability Stack:

Atlas (Dimensional Time-Series):
├─ Custom-built metrics platform
├─ 1.2 billion metrics per minute
├─ 2 million distinct time series
├─ Real-time aggregation and queries
├─ Integration with alerting (Atlas Alerts)
└─ Powers internal dashboards (Atlas Graph)

Key Capabilities:
├─ Stack Language: Mathematical operations on metrics
│   Example: errors.rate / requests.rate > 0.01
├─ Multi-dimensional queries:
│   Example: Group by region, device type, content category
├─ Real-time alerting: Sub-minute detection
└─ Automatic anomaly detection

Mantis (Streaming Analytics):
├─ Real-time event processing platform
├─ Processes user viewing events
├─ Aggregates 100+ billion events per day
├─ Powers real-time recommendations
└─ Drives operational dashboards

Example Use Case - Video Quality Monitoring:
Real-time Stream Analysis:
├─ Collect video playback events from 230M+ subscribers
├─ Metrics tracked:
│   ├─ Bitrate changes (quality degradation)
│   ├─ Buffering events (rebuffer ratio)
│   ├─ Startup time (time to first frame)
│   ├─ Error rates (playback failures)
│   └─ CDN performance (edge server health)
├─ Aggregation windows: 1 minute, 5 minutes, 1 hour
├─ Geographic breakdown: Country, city, ISP
└─ Device segmentation: TV, mobile, web, game consoles

Automated Actions:
├─ High rebuffer rate detected → Switch users to alternate CDN
├─ Regional network issues → Reduce video bitrate automatically
├─ Edge server degradation → Route traffic to healthy servers
├─ ISP performance drop → Engage with ISP support team
└─ Client-side issues → Push urgent app update
```

**Netflix Performance Optimization Results**:
```
Continuous Improvement Cycle:

Q1 2024 Optimization Initiative:
Problem: Startup time increased by 200ms globally

Investigation (Atlas + Mantis):
├─ Startup time breakdown by phase:
│   ├─ License acquisition: +50ms
│   ├─ Manifest fetch: +100ms ← Major contributor
│   ├─ First segment download: +30ms
│   ├─ Player initialization: +20ms
│   └─ Ad insertion: No change
├─ Geographic analysis:
│   ├─ North America: +150ms
│   ├─ Europe: +250ms ← Worst affected
│   ├─ Asia: +180ms
│   └─ Latin America: +200ms
└─ Device correlation:
    ├─ Smart TVs: +300ms ← Highest impact
    ├─ Mobile: +150ms
    └─ Web: +100ms

Root Causes Identified:
├─ Manifest service experiencing cache misses (60% miss rate)
├─ CDN routing suboptimal for manifest requests
├─ Smart TV firmware issues with HTTP/2
└─ Database queries for user profile slow during peak hours

Optimizations Deployed:
├─ Pre-warm manifest cache during off-peak hours
├─ Deploy dedicated manifest CDN tier
├─ Fallback to HTTP/1.1 for affected smart TV models
├─ Add read replica for user profile database
├─ Optimize manifest format (reduce size by 40%)
└─ Implement speculative prefetching

Results After 2 Weeks:
├─ Startup time improvement: 200ms → 50ms (75% reduction)
├─ Europe specifically: 250ms → 30ms (88% better!)
├─ Smart TV experience: 300ms → 80ms (73% better!)
├─ User engagement: +5% longer viewing sessions
├─ Subscriber retention: +0.8% improvement
└─ Infrastructure cost: -15% (better cache utilization)

Business Impact:
├─ Revenue increase: $12M annually (retention improvement)
├─ Infrastructure savings: $3M annually
├─ User satisfaction score: +8 points
└─ Competitive advantage: Fastest streaming startup globally
```

### 📊 Case Study 3: Cloudflare's Performance Analytics

**The Scope**: Analyze 35+ million HTTP requests per second globally

```
Cloudflare Analytics Architecture:

Edge Analytics Collection:
├─ Every request logged at edge (275+ locations)
├─ Sampling strategy:
│   ├─ 100% of errors (always log failures)
│   ├─ 10% of slow requests (>1 second)
│   ├─ 1% of normal requests (baseline sampling)
│   └─ 0.1% of fast requests (<100ms)
├─ Efficient encoding (Protocol Buffers)
├─ Batched transmission to analytics clusters
└─ Real-time and historical analytics

ClickHouse Analytics Database:
├─ Columnar storage for analytics queries
├─ Compression ratio: 10:1 average
├─ Query performance: <1s for billions of rows
├─ Retention: 30 days detailed, 1 year aggregated
└─ SQL interface for flexible queries

Customer-Facing Analytics:
├─ Request volume and bandwidth
├─ Cache performance (hit rate, bandwidth saved)
├─ Security events (DDoS, bot traffic, WAF blocks)
├─ Performance metrics (latency, TTFB, origin response time)
├─ Geographic breakdown (country, city)
├─ HTTP status codes and error rates
└─ Content type analysis

Real-Time Threat Detection:
Example: DDoS Attack Mitigation
├─ Traffic spike detected: 10x normal request rate
├─ Pattern analysis: 95% requests to /api/login
├─ Source analysis: 10,000 unique IPs from botnet
├─ Automatic mitigation:
│   ├─ Rate limiting: 10 requests/second per IP
│   ├─ Challenge: CAPTCHA for suspicious traffic
│   ├─ Block: Known malicious IPs
│   └─ Notify: Customer via email/webhook
├─ Time to mitigation: <10 seconds
└─ Attack absorbed: Zero customer downtime
```

---

## 🧪 Hands-On Lab: Build Global Monitoring System

### 🔍 Experiment 1: Implement Real User Monitoring

**Create RUM agent for web applications:**

```javascript
// Web Performance Monitoring Agent
class PerformanceMonitor {
    constructor(config) {
        this.config = {
            endpoint: config.endpoint || 'https://analytics.example.com/rum',
            sampleRate: config.sampleRate || 100, // Percentage
            sessionId: this.generateSessionId(),
            ...config
        };
        
        this.metrics = {};
        this.init();
    }
    
    init() {
        // Check if we should sample this session
        if (Math.random() * 100 > this.config.sampleRate) {
            return; // Skip this session (not sampled)
        }
        
        // Collect performance metrics when page loads
        if (document.readyState === 'complete') {
            this.collectMetrics();
        } else {
            window.addEventListener('load', () => this.collectMetrics());
        }
        
        // Monitor errors
        window.addEventListener('error', (event) => this.trackError(event));
        
        // Monitor user interactions
        this.trackInteractions();
        
        // Send heartbeat every 30 seconds
        setInterval(() => this.sendHeartbeat(), 30000);
    }
    
    collectMetrics() {
        const navigation = performance.getEntriesByType('navigation')[0];
        const paint = performance.getEntriesByType('paint');
        
        this.metrics = {
            // Page Load Timing
            dns: navigation.domainLookupEnd - navigation.domainLookupStart,
            tcp: navigation.connectEnd - navigation.connectStart,
            tls: navigation.secureConnectionStart > 0 
                ? navigation.connectEnd - navigation.secureConnectionStart 
                : 0,
            ttfb: navigation.responseStart - navigation.requestStart,
            download: navigation.responseEnd - navigation.responseStart,
            domProcessing: navigation.domContentLoadedEventEnd - navigation.responseEnd,
            totalLoadTime: navigation.loadEventEnd - navigation.fetchStart,
            
            // Core Web Vitals
            fcp: this.getFCP(paint),
            lcp: this.getLCP(),
            fid: this.getFID(),
            cls: this.getCLS(),
            
            // Custom Metrics
            deviceType: this.getDeviceType(),
            connection: this.getConnectionInfo(),
            viewport: `${window.innerWidth}x${window.innerHeight}`,
            
            // Context
            url: window.location.href,
            referrer: document.referrer,
            userAgent: navigator.userAgent,
            sessionId: this.config.sessionId,
            timestamp: Date.now()
        };
        
        // Send metrics to backend
        this.sendMetrics();
    }
    
    getFCP(paintEntries) {
        const fcp = paintEntries.find(entry => entry.name === 'first-contentful-paint');
        return fcp ? fcp.startTime : null;
    }
    
    getLCP() {
        return new Promise((resolve) => {
            const observer = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                const lastEntry = entries[entries.length - 1];
                resolve(lastEntry.renderTime || lastEntry.loadTime);
            });
            
            observer.observe({ type: 'largest-contentful-paint', buffered: true });
            
            // Timeout after 10 seconds
            setTimeout(() => resolve(null), 10000);
        });
    }
    
    getFID() {
        return new Promise((resolve) => {
            const observer = new PerformanceObserver((list) => {
                const firstInput = list.getEntries()[0];
                resolve(firstInput.processingStart - firstInput.startTime);
            });
            
            observer.observe({ type: 'first-input', buffered: true });
            
            // Timeout after 10 seconds
            setTimeout(() => resolve(null), 10000);
        });
    }
    
    getCLS() {
        let cls = 0;
        const observer = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (!entry.hadRecentInput) {
                    cls += entry.value;
                }
            }
        });
        
        observer.observe({ type: 'layout-shift', buffered: true });
        
        // Return accumulated CLS after a delay
        setTimeout(() => observer.disconnect(), 5000);
        return cls;
    }
    
    getDeviceType() {
        const ua = navigator.userAgent;
        if (/(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(ua)) {
            return 'tablet';
        }
        if (/Mobile|Android|iP(hone|od)|IEMobile|BlackBerry|Kindle|Silk-Accelerated|(hpw|web)OS|Opera M(obi|ini)/.test(ua)) {
            return 'mobile';
        }
        return 'desktop';
    }
    
    getConnectionInfo() {
        const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
        if (connection) {
            return {
                effectiveType: connection.effectiveType,
                downlink: connection.downlink,
                rtt: connection.rtt,
                saveData: connection.saveData
            };
        }
        return null;
    }
    
    trackError(event) {
        const errorData = {
            type: 'javascript_error',
            message: event.message,
            filename: event.filename,
            line: event.lineno,
            column: event.colno,
            stack: event.error?.stack,
            sessionId: this.config.sessionId,
            timestamp: Date.now(),
            url: window.location.href
        };
        
        this.sendData(errorData, '/errors');
    }
    
    trackInteractions() {
        // Track clicks
        document.addEventListener('click', (event) => {
            const target = event.target;
            const interactionData = {
                type: 'click',
                element: target.tagName,
                id: target.id,
                class: target.className,
                text: target.textContent?.substring(0, 100),
                sessionId: this.config.sessionId,
                timestamp: Date.now()
            };
            
            this.sendData(interactionData, '/interactions');
        }, { capture: true, passive: true });
        
        // Track form submissions
        document.addEventListener('submit', (event) => {
            const form = event.target;
            const submitData = {
                type: 'form_submit',
                formId: form.id,
                formName: form.name,
                sessionId: this.config.sessionId,
                timestamp: Date.now()
            };
            
            this.sendData(submitData, '/interactions');
        }, { capture: true });
    }
    
    sendMetrics() {
        this.sendData(this.metrics, '/metrics');
    }
    
    sendHeartbeat() {
        const heartbeat = {
            sessionId: this.config.sessionId,
            timestamp: Date.now(),
            url: window.location.href,
            timeOnPage: performance.now()
        };
        
        this.sendData(heartbeat, '/heartbeat');
    }
    
    sendData(data, path = '/metrics') {
        const url = this.config.endpoint + path;
        
        // Use sendBeacon for reliability (works even when page is closing)
        if (navigator.sendBeacon) {
            const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
            navigator.sendBeacon(url, blob);
        } else {
            // Fallback to fetch with keepalive
            fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
                keepalive: true
            }).catch(err => console.error('Failed to send metrics:', err));
        }
    }
    
    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }
}

// Initialize monitoring
const monitor = new PerformanceMonitor({
    endpoint: 'https://analytics.example.com/rum',
    sampleRate: 100, // Sample 100% of sessions for demo
    appVersion: '1.2.3',
    environment: 'production'
});

// Example: Track custom business metrics
function trackCheckout(orderId, amount) {
    monitor.sendData({
        type: 'checkout_complete',
        orderId: orderId,
        amount: amount,
        sessionId: monitor.config.sessionId,
        timestamp: Date.now()
    }, '/business-metrics');
}
```

### 🔍 Experiment 2: Build Synthetic Monitoring System

**Create global health checking system:**

```python
import asyncio
import aiohttp
import time
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
import json

@dataclass
class HealthCheckConfig:
    url: str
    method: str = 'GET'
    timeout: int = 10
    expected_status: int = 200
    expected_content: Optional[str] = None
    headers: Dict[str, str] = None
    interval: int = 60  # seconds

@dataclass
class HealthCheckResult:
    timestamp: float
    location: str
    url: str
    success: bool
    status_code: Optional[int]
    response_time_ms: float
    error: Optional[str]
    dns_time_ms: float = 0
    connect_time_ms: float = 0
    tls_time_ms: float = 0
    ttfb_ms: float = 0
    download_time_ms: float = 0

class GlobalHealthChecker:
    """
    Synthetic monitoring system that checks endpoints from multiple locations
    """
    def __init__(self):
        self.locations = {
            'us-east': 'New York, USA',
            'us-west': 'California, USA',
            'eu-west': 'Ireland, Europe',
            'asia-se': 'Singapore, Asia',
            'asia-ne': 'Tokyo, Asia',
        }
        
        self.checks: List[HealthCheckConfig] = []
        self.results: List[HealthCheckResult] = []
        self.alert_callbacks = []
    
    def add_check(self, config: HealthCheckConfig):
        """Add a health check configuration"""
        self.checks.append(config)
    
    def add_alert_callback(self, callback):
        """Add callback function for alerts"""
        self.alert_callbacks.append(callback)
    
    async def run_check(self, config: HealthCheckConfig, location: str) -> HealthCheckResult:
        """Execute single health check from a location"""
        start_time = time.time()
        timing = {'dns': 0, 'connect': 0, 'tls': 0, 'ttfb': 0, 'download': 0}
        
        try:
            # Create timing trace
            trace_config = aiohttp.TraceConfig()
            
            async def on_dns_resolvehost_end(session, context, params):
                timing['dns'] = (time.time() - start_time) * 1000
            
            async def on_connection_create_end(session, context, params):
                timing['connect'] = (time.time() - start_time) * 1000
            
            async def on_request_start(session, context, params):
                timing['tls'] = (time.time() - start_time) * 1000
            
            async def on_request_chunk_sent(session, context, params):
                if 'ttfb' not in timing or timing['ttfb'] == 0:
                    timing['ttfb'] = (time.time() - start_time) * 1000
            
            trace_config.on_dns_resolvehost_end.append(on_dns_resolvehost_end)
            trace_config.on_connection_create_end.append(on_connection_create_end)
            trace_config.on_request_start.append(on_request_start)
            trace_config.on_request_chunk_sent.append(on_request_chunk_sent)
            
            async with aiohttp.ClientSession(trace_configs=[trace_config]) as session:
                headers = config.headers or {}
                headers['User-Agent'] = f'HealthCheck/1.0 (Location: {location})'
                
                async with session.request(
                    config.method,
                    config.url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=config.timeout)
                ) as response:
                    # Read response body
                    body = await response.text()
                    end_time = time.time()
                    
                    response_time = (end_time - start_time) * 1000
                    timing['download'] = response_time - timing['ttfb']
                    
                    # Validate response
                    success = True
                    error = None
                    
                    if response.status != config.expected_status:
                        success = False
                        error = f"Unexpected status code: {response.status}"
                    
                    if config.expected_content and config.expected_content not in body:
                        success = False
                        error = f"Expected content not found in response"
                    
                    return HealthCheckResult(
                        timestamp=start_time,
                        location=location,
                        url=config.url,
                        success=success,
                        status_code=response.status,
                        response_time_ms=response_time,
                        error=error,
                        dns_time_ms=timing['dns'],
                        connect_time_ms=timing['connect'] - timing['dns'],
                        tls_time_ms=timing['tls'] - timing['connect'],
                        ttfb_ms=timing['ttfb'],
                        download_time_ms=timing['download']
                    )
        
        except asyncio.TimeoutError:
            return HealthCheckResult(
                timestamp=start_time,
                location=location,
                url=config.url,
                success=False,
                status_code=None,
                response_time_ms=(time.time() - start_time) * 1000,
                error="Request timeout"
            )
        
        except Exception as e:
            return HealthCheckResult(
                timestamp=start_time,
                location=location,
                url=config.url,
                success=False,
                status_code=None,
                response_time_ms=(time.time() - start_time) * 1000,
                error=str(e)
            )
    
    async def run_all_checks(self):
        """Run all health checks from all locations"""
        tasks = []
        
        for config in self.checks:
            for location_code, location_name in self.locations.items():
                task = asyncio.create_task(
                    self.run_check(config, location_code)
                )
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Store results and trigger alerts
        for result in results:
            if isinstance(result, HealthCheckResult):
                self.results.append(result)
                
                if not result.success:
                    await self.trigger_alerts(result)
        
        return results
    
    async def trigger_alerts(self, result: HealthCheckResult):
        """Trigger alert callbacks for failed checks"""
        for callback in self.alert_callbacks:
            try:
                await callback(result)
            except Exception as e:
                print(f"Alert callback failed: {e}")
    
    async def monitor_continuously(self):
        """Run health checks continuously"""
        print("🔍 Starting continuous health monitoring...")
        
        while True:
            print(f"\n📊 Running health checks at {datetime.now().isoformat()}")
            
            results = await self.run_all_checks()
            self.print_summary(results)
            
            # Wait for next check interval
            min_interval = min(check.interval for check in self.checks)
            await asyncio.sleep(min_interval)
    
    def print_summary(self, results):
        """Print summary of health check results"""
        successful = sum(1 for r in results if isinstance(r, HealthCheckResult) and r.success)
        total = len([r for r in results if isinstance(r, HealthCheckResult)])
        
        print(f"\n✅ Success Rate: {successful}/{total} ({successful/total*100:.1f}%)")
        
        # Group by URL
        by_url = {}
        for result in results:
            if isinstance(result, HealthCheckResult):
                if result.url not in by_url:
                    by_url[result.url] = []
                by_url[result.url].append(result)
        
        for url, url_results in by_url.items():
            print(f"\n🌐 {url}")
            
            for result in url_results:
                status = "✅" if result.success else "❌"
                location_name = self.locations.get(result.location, result.location)
                
                if result.success:
                    print(f"   {status} {location_name}: {result.response_time_ms:.0f}ms "
                          f"(DNS: {result.dns_time_ms:.0f}ms, "
                          f"Connect: {result.connect_time_ms:.0f}ms, "
                          f"TTFB: {result.ttfb_ms:.0f}ms)")
                else:
                    print(f"   {status} {location_name}: FAILED - {result.error}")
    
    def get_metrics(self) -> Dict:
        """Calculate aggregated metrics from recent results"""
        recent_results = self.results[-100:]  # Last 100 results
        
        if not recent_results:
            return {}
        
        successful = [r for r in recent_results if r.success]
        failed = [r for r in recent_results if not r.success]
        
        metrics = {
            'total_checks': len(recent_results),
            'success_rate': len(successful) / len(recent_results) * 100,
            'failure_rate': len(failed) / len(recent_results) * 100,
        }
        
        if successful:
            response_times = [r.response_time_ms for r in successful]
            response_times.sort()
            
            metrics['latency'] = {
                'min': min(response_times),
                'max': max(response_times),
                'avg': sum(response_times) / len(response_times),
                'p50': response_times[len(response_times)//2],
                'p95': response_times[int(len(response_times)*0.95)],
                'p99': response_times[int(len(response_times)*0.99)],
            }
        
        return metrics

# Alert callback example
async def alert_on_failure(result: HealthCheckResult):
    """Example alert callback"""
    print(f"\n🚨 ALERT: Health check failed!")
    print(f"   URL: {result.url}")
    print(f"   Location: {result.location}")
    print(f"   Error: {result.error}")
    print(f"   Time: {datetime.fromtimestamp(result.timestamp).isoformat()}")
    
    # In production, send to PagerDuty, Slack, email, etc.

# Example usage
async def main():
    checker = GlobalHealthChecker()
    
    # Add health checks
    checker.add_check(HealthCheckConfig(
        url='https://api.example.com/health',
        method='GET',
        expected_status=200,
        expected_content='{"status":"healthy"}',
        interval=60
    ))
    
    checker.add_check(HealthCheckConfig(
        url='https://www.example.com',
        method='GET',
        expected_status=200,
        interval=60
    ))
    
    # Add alert callback
    checker.add_alert_callback(alert_on_failure)
    
    # Run checks once
    results = await checker.run_all_checks()
    checker.print_summary(results)
    
    # Print metrics
    print(f"\n📈 Aggregated Metrics:")
    metrics = checker.get_metrics()
    print(json.dumps(metrics, indent=2))
    
    # Run continuously (comment out for single run)
    # await checker.monitor_continuously()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🎨 Visual Learning: Performance Monitoring Architecture

### 📊 Observability Stack
```
Complete Observability Architecture:

┌──────────────────────────────────────────────────────────┐
│               Application Layer                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │ Web App │  │ Mobile  │  │   API   │  │ Workers │   │
│  │ (React) │  │  (iOS)  │  │(Node.js)│  │ (Python)│   │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘   │
│       │            │            │            │         │
│   [Instrumentation: Metrics, Logs, Traces]              │
└───────┼────────────┼────────────┼────────────┼──────────┘
        ↓            ↓            ↓            ↓
┌──────────────────────────────────────────────────────────┐
│            Collection & Aggregation Layer                │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │   Prometheus   │  │ Fluentd/Loki │  │   Jaeger    │ │
│  │   (Metrics)    │  │    (Logs)    │  │  (Traces)   │ │
│  └────────┬───────┘  └──────┬───────┘  └──────┬──────┘ │
└───────────┼──────────────────┼──────────────────┼────────┘
            ↓                  ↓                  ↓
┌──────────────────────────────────────────────────────────┐
│              Storage & Analysis Layer                    │
│  ┌────────────┐  ┌────────────┐  ┌───────────────────┐ │
│  │ Time-Series│  │   Search   │  │  Distributed      │ │
│  │  Database  │  │   Engine   │  │  Trace Storage    │ │
│  │(Prometheus,│  │(Elasticsearch│  │  (Cassandra)     │ │
│  │ InfluxDB)  │  │  Splunk)   │  │                   │ │
│  └─────┬──────┘  └─────┬──────┘  └────────┬──────────┘ │
└────────┼─────────────────┼──────────────────┼────────────┘
         ↓                 ↓                  ↓
┌──────────────────────────────────────────────────────────┐
│          Visualization & Alerting Layer                  │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │  Grafana    │  │   Kibana     │  │   PagerDuty    │ │
│  │ (Dashboards)│  │(Log Analysis)│  │ (Alerting/     │ │
│  │             │  │              │  │  Incidents)    │ │
│  └─────────────┘  └──────────────┘  └────────────────┘ │
└──────────────────────────────────────────────────────────┘
                         ↓
                  👤 Engineers & SREs
```

### 🔍 Distributed Tracing Example
```
Request Trace: User Login Flow

TraceID: abc123def456
SpanID   Service           Duration  Details
═══════════════════════════════════════════════════════════
Root     API Gateway       245ms     Total request time
├─ 001   Auth Service      120ms     ⚠️ Slow!
│  ├─ 002 Token Validation  15ms     JWT decode
│  ├─ 003 Database Query   100ms     ⚠️ Bottleneck!
│  │      └─ SELECT * FROM users WHERE email=?
│  └─ 004 Session Create    5ms      Redis write
├─ 005   User Service       80ms     
│  ├─ 006 Cache Check        2ms     Cache MISS
│  ├─ 007 Database Query    75ms     User profile
│  └─ 008 Cache Write        3ms     Store in cache
└─ 009   Response Build     45ms     JSON serialization

Analysis:
🎯 Total: 245ms
⚠️  Bottleneck: Auth Service DB query (100ms = 41% of total)
💡 Optimization: Add index on email column
📈 Expected improvement: 100ms → 10ms (90% faster)
```

### 📈 Performance Dashboard Layout
```
Real-Time Performance Dashboard:

┌─────────────────────────── OVERVIEW ────────────────────────┐
│ ✅ Overall Health: HEALTHY          🌍 Active Users: 1.2M   │
│ 📊 Request Rate: 50K/s             ⏱️ Avg Latency: 85ms   │
│ ❌ Error Rate: 0.15%                💾 Cache Hit: 94%      │
└──────────────────────────────────────────────────────────────┘

┌──────── LATENCY BY REGION ────────┐ ┌──── ERROR BREAKDOWN ──┐
│                                    │ │                       │
│  🇺🇸 US:     65ms P95: 120ms   ✓  │ │ 4xx: 0.10%  ⚠️       │
│  🇪🇺 EU:     85ms P95: 150ms   ✓  │ │ 5xx: 0.05%  ✓        │
│  🇯🇵 Asia:  120ms P95: 250ms   ⚠️ │ │ Timeouts: 0.02%  ✓   │
│  🇦🇺 Oceania: 95ms P95: 180ms   ✓ │ │                       │
│                                    │ └───────────────────────┘
└────────────────────────────────────┘

┌─────────── SERVICE HEALTH ─────────────────────────────────┐
│ Service          Status  Latency   Error%   Throughput     │
│ ──────────────────────────────────────────────────────────│
│ API Gateway      ✅ UP    15ms      0.01%    50K req/s     │
│ Auth Service     ⚠️ SLOW  180ms     0.05%    25K req/s     │
│ User Service     ✅ UP    45ms      0.02%    30K req/s     │
│ Payment Service  ✅ UP    95ms      0.10%    5K req/s      │
│ Notification     ✅ UP    25ms      0.01%    10K req/s     │
└─────────────────────────────────────────────────────────────┘

┌─────────── ALERTS (Last Hour) ──────────────────────────────┐
│ 🔴 CRITICAL: Auth Service latency >150ms (Tokyo region)     │
│    Started: 14:23 UTC | Duration: 15 minutes               │
│    Action: Investigating database slow query                │
│                                                              │
│ 🟡 WARNING: Cache hit rate dropped to 89% (below 92%)      │
│    Started: 13:45 UTC | Duration: 45 minutes               │
│    Action: Cache warming scheduled                          │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎯 Week 11 Wrap-Up: Performance & Monitoring Mastery

### 🧠 Mental Models to Internalize

1. **Observability ≠ Monitoring**: Monitoring tells you what's broken; observability helps you understand why
2. **The Three Pillars**: Metrics (what), Logs (why), Traces (where)
3. **Real Users vs Robots**: RUM shows reality, synthetic shows potential
4. **Performance Budgets**: Speed is a feature, set targets and enforce them

### 🏆 Principal Architect Decision Framework

**Observability Strategy Selection:**
- **Startups/Small Scale**: Managed services (Datadog, New Relic) for quick setup
- **Medium Scale**: Hybrid (Prometheus + cloud logs) for cost optimization
- **Large Scale**: Custom stack (Prometheus + Loki + Jaeger) for control
- **Enterprise**: Multi-vendor (avoid lock-in, best-of-breed tools)

**Sampling Strategy:**
- **High-value traffic**: 100% (payments, checkouts, critical APIs)
- **Normal traffic**: 10-20% (representative sample)
- **Background jobs**: 1-5% (cost optimization)
- **Always capture**: All errors (critical for debugging)

### 🚨 Common Monitoring Mistakes

❌ **Alert fatigue** = Too many alerts, engineers ignore them all
❌ **Vanity metrics** = Tracking what's easy, not what matters
❌ **No SLOs/SLIs** = No objective performance targets
❌ **Reactive only** = Only look at dashboards when things break
✅ **Proactive monitoring** = Synthetic checks, anomaly detection, predictive alerts

### 🔮 Preview: Week 12 - Capstone Project & System Integration

Next week is the culmination of everything you've learned! You'll design and architect a complete global system from scratch, integrating all concepts: protocols, caching, load balancing, CDNs, microservices, DNS, edge computing, and monitoring.

---

## 🤔 Reflection Questions

Before moving to Week 12, ensure you can answer:

1. **ELI5**: "Why does your favorite app sometimes tell you 'something went wrong' and sometimes shows you exactly what's broken?"

2. **Architect Level**: "Design a complete observability strategy for a global fintech application processing $100M daily, including compliance requirements for data retention in multiple jurisdictions."

3. **Technical Deep-Dive**: "Your dashboards show 95th percentile latency is 100ms, but customers complain about slow performance. What's missing from your monitoring and how do you fix it?"

4. **Business Analysis**: "Calculate the ROI of implementing comprehensive observability for a SaaS platform, considering downtime reduction, faster incident resolution, and improved user experience."

---

*"The best systems are invisible when working, obvious when broken, and self-healing before users notice. Monitoring makes all three possible."*

**Next**: [Week 12 - Capstone Project & System Integration](12-Week12-Capstone-Project.md)