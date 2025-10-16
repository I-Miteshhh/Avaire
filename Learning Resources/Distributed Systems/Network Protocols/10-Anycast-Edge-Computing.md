# Week 10: Anycast Implementation & Edge Computing 🌐⚡

*"Edge computing is like having a mini-brain in every neighborhood that can think and act locally, while still coordinating with the global mind"*

## 🎯 This Week's Mission
Master anycast network implementation and edge computing platforms. Learn how companies deploy compute resources globally, maintain consistency across edge locations, and optimize for millisecond-level performance at planetary scale.

---

## 📋 Prerequisites: Building on Previous Weeks

You should now understand:
- ✅ **Global DNS Routing**: GeoDNS and intelligent traffic steering
- ✅ **Anycast Concepts**: Same IP address, multiple locations
- ✅ **CDN Architecture**: Content distribution and caching strategies
- ✅ **Microservices**: Distributed system communication patterns

### New Concepts We'll Master
- **BGP Anycast**: Border Gateway Protocol for anycast routing
- **Edge Functions**: Running code at CDN edge locations
- **Distributed State Management**: Consistency across edge nodes
- **Edge-to-Origin Communication**: Hybrid edge/cloud architectures

---

## 🎪 Explain Like I'm 10: The Neighborhood Smart Library Network

### 📚 The Old Way: Central Library Only (Cloud Computing)

Imagine your city has **one giant library downtown**:

```
🏢 Central Downtown Library
├─ 1 million books (complete collection)
├─ Expert librarians (powerful computers)
├─ Research labs (data processing)
└─ Location: Downtown (30 minutes away)

Reading a Book Process:
You → 🚌 Bus to downtown (30 min) → Find book (5 min) → Read → 🚌 Bus home (30 min)
Total time: 65+ minutes just to check a simple fact!

Problems:
- Long travel time (high latency)
- Library crowded during peak hours (bottlenecks)
- If library closes → No books for anyone (single point of failure)
- Everyone must go downtown (network congestion)
```

### 🏘️ The Smart Way: Neighborhood Smart Libraries (Edge Computing)

Now imagine **smart mini-libraries in every neighborhood**:

```
🏘️ Neighborhood Smart Library Network

Your Neighborhood (5-minute walk):
├─ 1,000 popular books (cached content)
├─ Self-service kiosks (edge functions)
├─ Local reading room (edge compute)
└─ Connected to downtown (can request any book)

Next Neighborhood (15-minute walk):
├─ Same 1,000 popular books
├─ Same self-service kiosks
├─ Same local capabilities
└─ Also connected to downtown

Magic Features:
1. Quick Access: Walk 5 min instead of bus 30 min
2. Smart Caching: Popular books always available locally
3. Local Processing: Simple questions answered immediately
4. Backup Power: If one library closes, go to next one
5. Downtown Connection: Rare books fetched from central library
```

### 🧠 The Anycast Magic: Same Address, Closest Location

Here's the **brilliant part** - all libraries have the **same address**:

```
Every Library's Address: "123 Library Street"

You ask Google Maps: "Navigate to 123 Library Street"
Google Maps: 
├─ Detects your location: North Neighborhood
├─ Finds closest "123 Library Street": 5 min walk  
├─ Gives directions to YOUR neighborhood library
└─ Result: You arrive at closest location automatically!

Your Friend in South Neighborhood:
├─ Same address: "123 Library Street"
├─ Google Maps detects: South Neighborhood
├─ Routes to South neighborhood library (also 5 min)
└─ Different building, same address, same service!

Benefits:
- One simple address to remember
- Always go to closest location automatically
- If your local library is full → Auto-routes to next closest
- New libraries added without changing address
```

### 🔄 The Distributed Brain: How Libraries Stay Synchronized

The **smart library network** coordinates like this:

```
📖 Popular New Book Released: "Dragons of 2025"

Day 1 - Downtown Receives Book:
🏢 Central Library → Receives 1,000 copies
                   ↓
         Monitors reader demand
                   ↓
         "This book is trending!"

Day 2 - Smart Distribution:
🏢 Central Library → Sends to all neighborhood libraries
                   ↓
🏘️ All neighborhood libraries receive copies
                   ↓
         Now available everywhere in 5 minutes!

Day 3 - Local Processing:
Student: "I need to write a report on dragons"
🏘️ Neighborhood Library Kiosk:
├─ Has "Dragons of 2025" book ✓
├─ Has AI assistant to help with research ✓
├─ Can print summary immediately ✓
└─ No need to call downtown!

Week Later - Smart Coordination:
North Library: "Dragons book checked out 50 times!"
South Library: "Only checked out 5 times here"
🏢 Central Library: "Move extra copies from South to North"
         ↓
Network auto-balances based on demand!
```

### ⚡ Edge Functions: Smart Robots in Every Library

Each library has **smart robot assistants** (edge functions):

```
🤖 Library Robot Capabilities:

Simple Questions (Answered Locally):
Student: "What time does library open?"
Robot: "9 AM - instant answer from local memory"

Medium Questions (Use Local Books):
Student: "Summarize this chapter about dragons"
Robot: "Reads book → Generates summary → 30 seconds"

Complex Questions (Call Downtown):  
Student: "Cross-reference dragons in all 1M books"
Robot: "Too complex for me → Calling central library..."
🏢 Central: "Processing... results in 5 minutes"

Benefits:
- 80% of questions answered instantly (local)
- 15% of questions answered in seconds (local processing)
- 5% of complex questions use central library (acceptable delay)
```

---

## 🏗️ Principal Architect Depth: Edge Computing at Global Scale

### 🚨 The Edge Computing Architecture Challenge

#### Challenge 1: BGP Anycast Network Implementation
```
Border Gateway Protocol Anycast Setup:

Traditional Internet Routing:
├─ Each server has unique IP address
├─ Internet routes to specific location  
├─ No automatic failover
└─ Manual DNS changes for routing

Anycast Implementation with BGP:

Step 1: Configure Same IP at Multiple Locations
Virginia Data Center → Announces 192.0.2.1/32 via AS64512
London Data Center → Announces 192.0.2.1/32 via AS64513
Tokyo Data Center → Announces 192.0.2.1/32 via AS64514

Step 2: BGP Propagation
Each data center advertises to upstream ISPs:
├─ Virginia → Verizon, Level3, Cogent
├─ London → BT, Telia, LINX
└─ Tokyo → NTT, KDDI, JPIX

Step 3: Internet Routing Decision
User in New York requests 192.0.2.1:
├─ Local router checks BGP table
├─ Sees 3 paths to 192.0.2.1:
│   ├─ Via Verizon → Virginia (2 hops) ← Shortest!
│   ├─ Via Telia → London (6 hops)
│   └─ Via NTT → Tokyo (12 hops)
├─ Selects Virginia (shortest AS path)
└─ Routes traffic automatically

Automatic Failover:
Virginia data center goes down:
├─ Stops announcing 192.0.2.1
├─ BGP propagates withdrawal (30-180 seconds)
├─ New York traffic now routes to London  
├─ Users experience brief disruption, then automatic recovery
└─ No manual intervention required!
```

#### Challenge 2: Edge Computing Execution Models
```
Edge Function Deployment Patterns:

Pattern 1: CDN Edge Workers (Cloudflare Workers, Fastly Compute@Edge)
Deployment Model:
├─ JavaScript/WebAssembly code
├─ Deployed to 200+ global locations  
├─ Isolated V8 runtime per request
├─ 0-5ms cold start time
└─ Sub-millisecond execution for simple logic

Use Cases:
├─ Request/response manipulation (add headers, modify URLs)
├─ A/B testing and feature flags
├─ API gateway and authentication
├─ Simple business logic (rate limiting, validation)
└─ Edge caching decisions

Constraints:
├─ Execution time limit: 50-200ms
├─ Memory limit: 128MB-512MB
├─ No local filesystem
├─ Limited CPU time
└─ Stateless (ephemeral storage only)

Pattern 2: Edge Containers (AWS Lambda@Edge, Azure Edge Zones)
Deployment Model:  
├─ Container or function package
├─ Deployed to regional edge locations (20-50 globally)
├─ Container runtime (Docker-compatible)
├─ 100-500ms cold start time
└─ Longer execution allowed (up to 30 seconds)

Use Cases:
├─ Image/video processing and transformation
├─ Complex API aggregation
├─ Server-side rendering (SSR)
├─ Machine learning inference
└─ Database queries and aggregations

Constraints:
├─ Higher cold start latency
├─ Fewer global locations
├─ More expensive per request
└─ Still limited by edge location resources

Pattern 3: Edge Kubernetes (Google Anthos, Azure Arc)
Deployment Model:
├─ Full Kubernetes clusters at edge
├─ Deployed to specific customer locations
├─ Complete container orchestration
├─ Persistent storage available
└─ Can run any workload

Use Cases:
├─ IoT data processing at source
├─ Manufacturing floor automation
├─ Retail point-of-sale systems
├─ 5G network functions
└─ Latency-critical applications

Constraints:
├─ Higher infrastructure cost
├─ Complex operational overhead
├─ Requires local hardware
└─ Network connectivity dependencies
```

### 🌐 Distributed State Management at Edge

#### Edge Data Consistency Strategies
```
Challenge: Keep data synchronized across 200+ edge locations

Strategy 1: Eventually Consistent Edge Cache
Architecture:
Origin DB → Regional Replication → Edge Caches
   ↓              ↓                    ↓
MySQL       Read Replicas         Distributed Cache
(source)    (15 regions)         (200+ locations)

Update Flow:
1. Write to origin database (100ms)
2. Replicate to regional databases (1-5 seconds)
3. Edge caches invalidated (10-30 seconds)
4. Edge fetches fresh data on next request

Use Cases:
├─ Product catalogs (changes infrequently)
├─ User profiles (eventual consistency acceptable)
├─ Content metadata
└─ Configuration data

Consistency Model: Eventual (seconds to minutes)

Strategy 2: Distributed Edge Database (CRDTs)
Architecture:
Edge Location 1 ← → Edge Location 2 ← → Edge Location 3
     ↓                    ↓                    ↓
   CRDT DB            CRDT DB              CRDT DB
(Conflict-free)    (Auto-merge)         (Convergent)

Update Flow:
1. Write to local edge database (10ms)
2. Asynchronously sync to other edges (background)
3. Conflict-free merges using CRDT algorithms
4. All edges eventually converge to same state

CRDT Examples:
├─ Counters: LWW (Last-Write-Wins) counter
├─ Sets: OR-Set (Observed-Remove Set)
├─ Maps: LWW-Map with tombstones
└─ Registers: Multi-Value Register

Use Cases:
├─ Collaborative editing (Google Docs)
├─ Shopping cart state
├─ User presence/status
├─ Real-time analytics counters
└─ Distributed configuration

Consistency Model: Strong eventual (automatic convergence)

Strategy 3: Edge-to-Origin Validation
Architecture:
Edge Compute → Local Decision → Origin Validation (if needed)

Decision Flow:
User Request → Edge Function:
├─ Check local cache (5ms)
├─ If critical operation → Validate with origin (100ms)
├─ If read operation → Use cached data (5ms)
└─ If write operation → Write to origin + invalidate caches

Use Cases:
├─ Payment authorization (must validate)
├─ Inventory checks (eventual consistency OK)
├─ User authentication (cached with TTL)
└─ Content delivery (cached with long TTL)

Consistency Model: Hybrid (critical=strong, others=eventual)
```

---

## 🌍 Real-World Implementation Examples

### 📊 Case Study 1: Cloudflare Workers - Serverless Edge Platform

**The Scale**: 275+ cities, 100+ countries, processing 35M+ requests/second

```
Cloudflare Workers Architecture:

Global Deployment:
├─ JavaScript/WebAssembly code deployed globally
├─ Executes in V8 isolates (not containers)
├─ 0ms cold start (isolates are instant)
├─ Automatic routing to nearest location
└─ 100% CPU time included (no throttling)

Execution Environment:
├─ V8 JavaScript engine
├─ WebAssembly support (Rust, C++, Go compiled)
├─ Service bindings (Worker-to-Worker calls)
├─ KV storage (eventually consistent, global)
├─ Durable Objects (strongly consistent, regional)
└─ R2 object storage (S3-compatible, no egress fees)

Performance Characteristics:
├─ Cold start: 0ms (isolates pre-warmed)
├─ Execution time: median 1-2ms
├─ P99 latency: <50ms globally
├─ Throughput: 1M+ requests/sec per account
└─ Memory: 128MB per request

Advanced Features:
├─ Cron triggers (scheduled execution)
├─ Queue integration (async messaging)
├─ WebSocket support (real-time connections)
├─ Image transformation (built-in)
└─ Email routing and transformation
```

**Cloudflare Workers Real-World Performance**:
```
Production Performance Metrics:

E-commerce API Gateway:
├─ Traditional cloud API: 200-300ms latency globally
├─ Cloudflare Workers API: 15-40ms latency globally
├─ Improvement: 85% latency reduction
├─ Cost reduction: 60% (vs serverless cloud functions)
└─ Scalability: Automatic (no capacity planning)

Authentication Layer:
├─ JWT validation at edge (2-5ms)
├─ Session check in Workers KV (10-15ms)
├─ Total auth overhead: <20ms
├─ Traditional auth: 100-200ms (origin round-trip)
└─ User experience: Feels instant globally

A/B Testing Platform:
├─ Traffic split decisions: <1ms at edge
├─ Experiment tracking: Workers KV
├─ Analytics: Sent to origin async
├─ Zero impact on user latency
└─ Real-time experimentation across globe

Developer Experience:
├─ Deploy time: 30 seconds globally
├─ Rollback time: 10 seconds
├─ Local testing: Miniflare emulator
├─ Debugging: Real-time logs and traces
└─ Cost: $5/month + $0.50 per million requests
```

### 📊 Case Study 2: AWS Lambda@Edge with CloudFront

**The Innovation**: Run Lambda functions at 400+ CloudFront edge locations

```
Lambda@Edge Architecture:

Deployment Model:
├─ Node.js or Python Lambda functions
├─ Triggered by CloudFront events:
│   ├─ Viewer Request (before cache check)
│   ├─ Origin Request (after cache miss)
│   ├─ Origin Response (after origin responds)
│   └─ Viewer Response (before returning to user)
├─ Deployed from us-east-1 → Replicated globally
├─ Cold start: 100-500ms (first request per region)
└─ Warm execution: 5-50ms

Use Cases and Implementations:

1. Dynamic Content Generation (Viewer Request):
```javascript
exports.handler = async (event) => {
    const request = event.Records[0].cf.request;
    const headers = request.headers;
    
    // Detect mobile devices
    const userAgent = headers['user-agent'][0].value;
    const isMobile = /Mobile|Android/i.test(userAgent);
    
    // Modify request to serve appropriate content
    if (isMobile) {
        request.uri = request.uri.replace('/web/', '/mobile/');
    }
    
    return request;
};
```

2. Security Headers Injection (Viewer Response):
```javascript
exports.handler = async (event) => {
    const response = event.Records[0].cf.response;
    
    // Add security headers at edge
    response.headers['strict-transport-security'] = [{
        key: 'Strict-Transport-Security',
        value: 'max-age=31536000; includeSubdomains; preload'
    }];
    
    response.headers['content-security-policy'] = [{
        key: 'Content-Security-Policy',
        value: "default-src 'self'; script-src 'self' 'unsafe-inline'"
    }];
    
    return response;
};
```

3. Image Optimization (Origin Response):
```javascript
const Sharp = require('sharp');

exports.handler = async (event) => {
    const response = event.Records[0].cf.response;
    const request = event.Records[0].cf.request;
    
    // Check if WebP is supported
    const accept = request.headers.accept?.[0]?.value || '';
    const supportsWebP = accept.includes('image/webp');
    
    if (supportsWebP && response.status === '200') {
        const imageBuffer = Buffer.from(response.body, 'base64');
        
        // Convert to WebP at edge
        const webpBuffer = await Sharp(imageBuffer)
            .webp({ quality: 80 })
            .toBuffer();
        
        response.body = webpBuffer.toString('base64');
        response.bodyEncoding = 'base64';
        response.headers['content-type'] = [{
            key: 'Content-Type',
            value: 'image/webp'
        }];
    }
    
    return response;
};
```

Performance Results:
├─ Image optimization: 60% size reduction at edge
├─ Security header injection: 0ms latency overhead
├─ Dynamic routing: 5-10ms decision time
├─ Global deployment: 2-3 minutes
└─ Cost: $0.60 per 1M requests + $0.00001 per GB-second
```

### 📊 Case Study 3: Fastly Compute@Edge - WebAssembly at the Edge

**The Power**: Compile any language to WebAssembly, run at 70+ global locations

```
Fastly Compute@Edge Architecture:

Execution Environment:
├─ WebAssembly runtime (Lucet JIT compiler)
├─ Language support: Rust, JavaScript, Go, Python, C/C++
├─ Cold start: 35-100µs (microseconds!)
├─ Execution: Native speed (compiled to machine code)
└─ Memory: Isolated, secure sandboxing

Performance Characteristics:
├─ Startup: 50µs median (vs 100+ms for containers)
├─ Execution: Near-native performance
├─ Throughput: 1M+ requests/second per location
├─ Latency: P50 <10ms, P99 <50ms globally
└─ Efficiency: 100x more efficient than containers

Example: Rust-based Edge API
```rust
use fastly::{Error, Request, Response};
use serde_json::json;

#[fastly::main]
fn main(mut req: Request) -> Result<Response, Error> {
    // Parse request
    let client_ip = req.get_client_ip_addr()
        .map(|ip| ip.to_string())
        .unwrap_or_else(|| "unknown".to_string());
    
    // Geolocation lookup (built-in)
    let geo = req.get_client_geo_info()?;
    
    // Route based on geography
    let backend = match geo.country_code().as_deref() {
        Some("US") | Some("CA") => "us_backend",
        Some("GB") | Some("FR") | Some("DE") => "eu_backend",
        Some("JP") | Some("SG") | Some("AU") => "asia_backend",
        _ => "default_backend",
    };
    
    // Make backend request
    let mut backend_req = Request::get(format!(
        "https://{}/api/data",
        backend
    ));
    
    // Add custom headers
    backend_req.set_header("X-Client-IP", client_ip);
    backend_req.set_header("X-Client-Country", 
                          geo.country_code().unwrap_or("unknown"));
    
    // Send to backend
    let backend_resp = backend_req.send(backend)?;
    
    // Return response
    Ok(backend_resp)
}
```

Production Performance:
├─ API routing latency: 5-8ms (including geo lookup)
├─ Custom logic execution: 1-3ms
├─ Backend selection: <1ms
├─ Total request overhead: <10ms
└─ Developer experience: Excellent (full language features)

Advanced Capabilities:
├─ Edge-side rendering (SSR)
├─ Real-time personalization
├─ Complex routing logic
├─ Protocol transformation
└─ Security policy enforcement
```

---

## 🧪 Hands-On Lab: Build Edge Computing Platform

### 🔍 Experiment 1: Simple Edge Function Implementation

**Create edge workers for common use cases:**

```javascript
// Cloudflare Workers example: Intelligent routing and caching

addEventListener('fetch', event => {
    event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
    const url = new URL(request.url);
    const cache = caches.default;
    
    // Check cache first
    let response = await cache.match(request);
    
    if (response) {
        // Cache hit - add header and return
        response = new Response(response.body, response);
        response.headers.set('X-Cache', 'HIT');
        return response;
    }
    
    // Cache miss - intelligent routing
    const origin = await selectOptimalOrigin(request);
    
    // Modify request for origin
    const originRequest = new Request(request);
    originRequest.headers.set('X-Edge-Location', 
        request.cf?.colo || 'unknown');
    
    // Fetch from selected origin
    response = await fetch(originRequest, {
        backend: origin,
        timeout: 10000
    });
    
    // Cache successful responses
    if (response.ok) {
        response = new Response(response.body, response);
        response.headers.set('X-Cache', 'MISS');
        response.headers.set('X-Origin', origin);
        
        // Determine cache TTL based on content type
        const contentType = response.headers.get('Content-Type') || '';
        let cacheTTL = 3600; // Default 1 hour
        
        if (contentType.includes('image/')) {
            cacheTTL = 86400; // Images: 24 hours
        } else if (contentType.includes('application/json')) {
            cacheTTL = 300; // API responses: 5 minutes
        } else if (contentType.includes('text/html')) {
            cacheTTL = 60; // HTML: 1 minute
        }
        
        response.headers.set('Cache-Control', `public, max-age=${cacheTTL}`);
        
        // Store in cache
        event.waitUntil(cache.put(request, response.clone()));
    }
    
    return response;
}

async function selectOptimalOrigin(request) {
    // Get client location from Cloudflare
    const country = request.cf?.country || 'US';
    const continent = request.cf?.continent || 'NA';
    
    // Route to nearest healthy origin
    const origins = {
        'NA': 'https://us-origin.example.com',
        'EU': 'https://eu-origin.example.com',
        'AS': 'https://asia-origin.example.com',
        'OC': 'https://aus-origin.example.com',
    };
    
    // Check origin health (simplified)
    const preferredOrigin = origins[continent] || origins['NA'];
    
    // Could implement sophisticated health checking here
    const isHealthy = await checkOriginHealth(preferredOrigin);
    
    if (isHealthy) {
        return preferredOrigin;
    } else {
        // Failover to primary origin
        return origins['NA'];
    }
}

async function checkOriginHealth(origin) {
    try {
        const healthCheck = await fetch(`${origin}/health`, {
            timeout: 2000
        });
        return healthCheck.ok;
    } catch (error) {
        return false;
    }
}

// A/B Testing at edge
addEventListener('fetch', event => {
    event.respondWith(handleABTest(event.request))
})

async function handleABTest(request) {
    const url = new URL(request.url);
    
    // Get or assign experiment variant
    const cookie = request.headers.get('Cookie') || '';
    let variant = getVariantFromCookie(cookie);
    
    if (!variant) {
        // Assign new user to variant (50/50 split)
        variant = Math.random() < 0.5 ? 'A' : 'B';
    }
    
    // Route to appropriate backend
    const backend = variant === 'A' 
        ? 'https://version-a.example.com'
        : 'https://version-b.example.com';
    
    const response = await fetch(backend + url.pathname, {
        headers: request.headers
    });
    
    // Set cookie to maintain variant assignment
    const newResponse = new Response(response.body, response);
    newResponse.headers.set('Set-Cookie', 
        `experiment_variant=${variant}; Path=/; Max-Age=2592000; SameSite=Lax`);
    newResponse.headers.set('X-Experiment-Variant', variant);
    
    return newResponse;
}

function getVariantFromCookie(cookie) {
    const match = cookie.match(/experiment_variant=([AB])/);
    return match ? match[1] : null;
}
```

### 🔍 Experiment 2: Edge Database with CRDTs

**Implement distributed counter using Conflict-free Replicated Data Types:**

```python
import asyncio
import json
from dataclasses import dataclass, field
from typing import Dict, Set
import hashlib
import time

@dataclass
class GCounter:
    """
    Grow-only Counter CRDT
    Allows increments at any replica, automatically merges
    """
    node_id: str
    counts: Dict[str, int] = field(default_factory=dict)
    
    def increment(self, amount: int = 1):
        """Increment counter at this node"""
        if self.node_id not in self.counts:
            self.counts[self.node_id] = 0
        self.counts[self.node_id] += amount
    
    def value(self) -> int:
        """Get total counter value across all nodes"""
        return sum(self.counts.values())
    
    def merge(self, other: 'GCounter'):
        """Merge with another GCounter (conflict-free)"""
        for node_id, count in other.counts.items():
            current = self.counts.get(node_id, 0)
            # Take maximum value for each node
            self.counts[node_id] = max(current, count)
    
    def to_dict(self):
        return {
            'node_id': self.node_id,
            'counts': self.counts,
            'total': self.value()
        }

@dataclass
class PNCounter:
    """
    Positive-Negative Counter CRDT
    Allows both increments and decrements
    """
    node_id: str
    positive: GCounter = field(default_factory=lambda: GCounter(''))
    negative: GCounter = field(default_factory=lambda: GCounter(''))
    
    def __post_init__(self):
        self.positive.node_id = self.node_id
        self.negative.node_id = self.node_id
    
    def increment(self, amount: int = 1):
        """Increment counter"""
        self.positive.increment(amount)
    
    def decrement(self, amount: int = 1):
        """Decrement counter"""
        self.negative.increment(amount)
    
    def value(self) -> int:
        """Get net counter value"""
        return self.positive.value() - self.negative.value()
    
    def merge(self, other: 'PNCounter'):
        """Merge with another PNCounter"""
        self.positive.merge(other.positive)
        self.negative.merge(other.negative)
    
    def to_dict(self):
        return {
            'node_id': self.node_id,
            'value': self.value(),
            'positive': self.positive.to_dict(),
            'negative': self.negative.to_dict()
        }

@dataclass
class LWWRegister:
    """
    Last-Write-Wins Register CRDT
    Stores a value with timestamp, latest write wins
    """
    node_id: str
    value: any = None
    timestamp: float = 0.0
    writer_id: str = ''
    
    def write(self, value):
        """Write new value with current timestamp"""
        self.value = value
        self.timestamp = time.time()
        self.writer_id = self.node_id
    
    def merge(self, other: 'LWWRegister'):
        """Merge with another register, keeping latest write"""
        if other.timestamp > self.timestamp:
            self.value = other.value
            self.timestamp = other.timestamp
            self.writer_id = other.writer_id
        elif other.timestamp == self.timestamp:
            # Tie-breaker: use writer_id lexicographically
            if other.writer_id > self.writer_id:
                self.value = other.value
                self.writer_id = other.writer_id
    
    def to_dict(self):
        return {
            'value': self.value,
            'timestamp': self.timestamp,
            'writer_id': self.writer_id
        }

class EdgeNode:
    """
    Simulates an edge computing node with CRDT storage
    """
    def __init__(self, node_id: str, location: str):
        self.node_id = node_id
        self.location = location
        self.page_views = PNCounter(node_id)
        self.user_sessions = GCounter(node_id)
        self.feature_flag = LWWRegister(node_id)
        self.peers: Set['EdgeNode'] = set()
    
    def add_peer(self, peer: 'EdgeNode'):
        """Connect to another edge node"""
        self.peers.add(peer)
        peer.peers.add(self)
    
    async def sync_with_peers(self):
        """Synchronize CRDT state with all peers"""
        for peer in self.peers:
            # Send our state to peer
            await peer.receive_sync(self)
    
    async def receive_sync(self, peer: 'EdgeNode'):
        """Receive and merge state from peer"""
        # Merge all CRDTs
        self.page_views.merge(peer.page_views)
        self.user_sessions.merge(peer.user_sessions)
        self.feature_flag.merge(peer.feature_flag)
    
    def record_page_view(self):
        """Record a page view at this edge location"""
        self.page_views.increment(1)
    
    def record_session(self):
        """Record a new user session"""
        self.user_sessions.increment(1)
    
    def update_feature_flag(self, enabled: bool):
        """Update feature flag"""
        self.feature_flag.write(enabled)
    
    def get_stats(self):
        """Get current statistics"""
        return {
            'node_id': self.node_id,
            'location': self.location,
            'total_page_views': self.page_views.value(),
            'total_sessions': self.user_sessions.value(),
            'feature_enabled': self.feature_flag.value,
            'last_feature_update': self.feature_flag.timestamp
        }

# Simulate edge network with CRDTs
async def simulate_edge_network():
    """
    Simulate a global edge network with multiple nodes
    using CRDTs for distributed state management
    """
    # Create edge nodes in different locations
    nodes = {
        'us-west': EdgeNode('us-west', 'California'),
        'us-east': EdgeNode('us-east', 'Virginia'),
        'eu-west': EdgeNode('eu-west', 'Ireland'),
        'asia-se': EdgeNode('asia-se', 'Singapore'),
        'asia-ne': EdgeNode('asia-ne', 'Tokyo'),
    }
    
    # Connect nodes in a mesh network
    node_list = list(nodes.values())
    for i, node in enumerate(node_list):
        for peer in node_list[i+1:]:
            node.add_peer(peer)
    
    print("🌍 Edge Network Initialized")
    print(f"Nodes: {list(nodes.keys())}")
    print(f"Mesh connections: {len(node_list) * (len(node_list)-1) // 2}\n")
    
    # Simulate traffic at different edge locations
    print("📊 Simulating User Traffic...")
    
    # California gets high traffic
    for _ in range(100):
        nodes['us-west'].record_page_view()
        if _ % 10 == 0:
            nodes['us-west'].record_session()
    
    # Virginia gets medium traffic
    for _ in range(60):
        nodes['us-east'].record_page_view()
        if _ % 8 == 0:
            nodes['us-east'].record_session()
    
    # Ireland gets medium traffic
    for _ in range(70):
        nodes['eu-west'].record_page_view()
        if _ % 7 == 0:
            nodes['eu-west'].record_session()
    
    # Singapore gets low traffic
    for _ in range(30):
        nodes['asia-se'].record_page_view()
        if _ % 5 == 0:
            nodes['asia-se'].record_session()
    
    # Tokyo gets low traffic
    for _ in range(40):
        nodes['asia-ne'].record_page_view()
        if _ % 6 == 0:
            nodes['asia-ne'].record_session()
    
    # Feature flag update from Ireland
    nodes['eu-west'].update_feature_flag(True)
    
    print("\n📡 Before Synchronization:")
    for name, node in nodes.items():
        stats = node.get_stats()
        print(f"{name}: {stats['total_page_views']} views, "
              f"{stats['total_sessions']} sessions, "
              f"feature={stats['feature_enabled']}")
    
    # Synchronize all nodes
    print("\n🔄 Synchronizing Edge Nodes...")
    sync_tasks = [node.sync_with_peers() for node in nodes.values()]
    await asyncio.gather(*sync_tasks)
    
    # Small delay for realism
    await asyncio.sleep(0.1)
    
    print("\n✅ After Synchronization:")
    for name, node in nodes.items():
        stats = node.get_stats()
        print(f"{name}: {stats['total_page_views']} views, "
              f"{stats['total_sessions']} sessions, "
              f"feature={stats['feature_enabled']}")
    
    # Verify all nodes converged to same state
    values = [node.page_views.value() for node in nodes.values()]
    sessions = [node.user_sessions.value() for node in nodes.values()]
    flags = [node.feature_flag.value for node in nodes.values()]
    
    print(f"\n🎯 Convergence Check:")
    print(f"All nodes agree on page views: {len(set(values)) == 1} (value: {values[0]})")
    print(f"All nodes agree on sessions: {len(set(sessions)) == 1} (value: {sessions[0]})")
    print(f"All nodes agree on feature flag: {len(set(flags)) == 1} (value: {flags[0]})")
    
    # Demonstrate conflict-free merging
    print(f"\n🔬 CRDT Properties Demonstrated:")
    print(f"✓ Commutative: Merge order doesn't matter")
    print(f"✓ Associative: Can merge in any grouping")
    print(f"✓ Idempotent: Merging same state multiple times is safe")
    print(f"✓ Eventual Consistency: All nodes converge to same state")

# Run the simulation
if __name__ == "__main__":
    asyncio.run(simulate_edge_network())
```

### 🔍 Experiment 3: Edge-to-Origin Hybrid Architecture

**Implement intelligent edge caching with origin fallback:**

```python
import asyncio
import aiohttp
import time
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict
import hashlib
import json

class CacheStrategy(Enum):
    EDGE_FIRST = "edge_first"  # Try edge, fallback to origin
    ORIGIN_FIRST = "origin_first"  # Always fetch from origin
    EDGE_ONLY = "edge_only"  # Only use edge (fail if not cached)

@dataclass
class CachedData:
    data: any
    timestamp: float
    ttl: int
    etag: str
    
    def is_expired(self) -> bool:
        return time.time() > (self.timestamp + self.ttl)
    
    def is_stale(self, stale_threshold: int = 60) -> bool:
        """Check if data is stale but might be acceptable"""
        age = time.time() - self.timestamp
        return age > (self.ttl - stale_threshold)

class EdgeOriginCache:
    """
    Hybrid edge-to-origin caching system
    Demonstrates stale-while-revalidate and other advanced patterns
    """
    def __init__(self, node_id: str, origin_url: str):
        self.node_id = node_id
        self.origin_url = origin_url
        self.cache: Dict[str, CachedData] = {}
        self.revalidation_in_progress: Dict[str, asyncio.Event] = {}
        
        # Metrics
        self.stats = {
            'edge_hits': 0,
            'edge_misses': 0,
            'origin_requests': 0,
            'stale_while_revalidate': 0,
            'revalidations': 0
        }
    
    async def get(self, key: str, strategy: CacheStrategy = CacheStrategy.EDGE_FIRST,
                  ttl: int = 300, stale_while_revalidate: bool = True) -> Optional[dict]:
        """
        Get data with specified caching strategy
        """
        cache_key = self._make_cache_key(key)
        
        if strategy == CacheStrategy.EDGE_ONLY:
            return await self._get_edge_only(cache_key)
        elif strategy == CacheStrategy.ORIGIN_FIRST:
            return await self._get_origin_first(cache_key, ttl)
        else:  # EDGE_FIRST
            return await self._get_edge_first(
                cache_key, ttl, stale_while_revalidate
            )
    
    async def _get_edge_only(self, cache_key: str) -> Optional[dict]:
        """Get from edge cache only, fail if not available"""
        cached = self.cache.get(cache_key)
        
        if cached and not cached.is_expired():
            self.stats['edge_hits'] += 1
            return {
                'data': cached.data,
                'source': 'edge_cache',
                'age_seconds': time.time() - cached.timestamp
            }
        
        self.stats['edge_misses'] += 1
        return None
    
    async def _get_origin_first(self, cache_key: str, ttl: int) -> dict:
        """Always fetch from origin (cache-aside pattern)"""
        data = await self._fetch_from_origin(cache_key)
        
        if data:
            # Cache the result
            self.cache[cache_key] = CachedData(
                data=data,
                timestamp=time.time(),
                ttl=ttl,
                etag=self._generate_etag(data)
            )
        
        return {
            'data': data,
            'source': 'origin',
            'cached_at_edge': data is not None
        }
    
    async def _get_edge_first(self, cache_key: str, ttl: int,
                             stale_while_revalidate: bool) -> dict:
        """
        Try edge cache first, implement stale-while-revalidate
        """
        cached = self.cache.get(cache_key)
        
        # Case 1: Fresh cache hit
        if cached and not cached.is_expired():
            self.stats['edge_hits'] += 1
            
            # Check if stale and should revalidate in background
            if cached.is_stale() and stale_while_revalidate:
                # Return stale data immediately
                self.stats['stale_while_revalidate'] += 1
                
                # Revalidate in background (don't await)
                asyncio.create_task(
                    self._revalidate_in_background(cache_key, ttl)
                )
                
                return {
                    'data': cached.data,
                    'source': 'edge_cache_stale_revalidating',
                    'age_seconds': time.time() - cached.timestamp
                }
            
            return {
                'data': cached.data,
                'source': 'edge_cache_fresh',
                'age_seconds': time.time() - cached.timestamp
            }
        
        # Case 2: Cache miss or expired - fetch from origin
        self.stats['edge_misses'] += 1
        
        # Check if revalidation already in progress
        if cache_key in self.revalidation_in_progress:
            # Wait for ongoing revalidation
            await self.revalidation_in_progress[cache_key].wait()
            # Try cache again
            cached = self.cache.get(cache_key)
            if cached:
                return {
                    'data': cached.data,
                    'source': 'edge_cache_after_wait',
                    'age_seconds': time.time() - cached.timestamp
                }
        
        # Fetch from origin
        data = await self._fetch_from_origin(cache_key)
        
        if data:
            self.cache[cache_key] = CachedData(
                data=data,
                timestamp=time.time(),
                ttl=ttl,
                etag=self._generate_etag(data)
            )
            
            return {
                'data': data,
                'source': 'origin_fresh',
                'age_seconds': 0
            }
        
        # Origin failed - return stale if available
        if cached:
            return {
                'data': cached.data,
                'source': 'edge_cache_stale_fallback',
                'age_seconds': time.time() - cached.timestamp,
                'warning': 'origin_unavailable'
            }
        
        return {'data': None, 'source': 'failed', 'error': 'origin_unavailable'}
    
    async def _revalidate_in_background(self, cache_key: str, ttl: int):
        """Background revalidation for stale-while-revalidate"""
        if cache_key in self.revalidation_in_progress:
            return  # Already revalidating
        
        event = asyncio.Event()
        self.revalidation_in_progress[cache_key] = event
        
        try:
            self.stats['revalidations'] += 1
            data = await self._fetch_from_origin(cache_key)
            
            if data:
                self.cache[cache_key] = CachedData(
                    data=data,
                    timestamp=time.time(),
                    ttl=ttl,
                    etag=self._generate_etag(data)
                )
        finally:
            del self.revalidation_in_progress[cache_key]
            event.set()
    
    async def _fetch_from_origin(self, cache_key: str) -> Optional[dict]:
        """Fetch data from origin server"""
        self.stats['origin_requests'] += 1
        
        try:
            # Simulate origin request
            await asyncio.sleep(0.1)  # Simulate network latency
            
            # Return simulated data
            return {
                'key': cache_key,
                'value': f'Data for {cache_key}',
                'timestamp': time.time(),
                'origin': self.origin_url
            }
        except Exception as e:
            print(f"Origin fetch failed: {e}")
            return None
    
    def _make_cache_key(self, key: str) -> str:
        """Generate cache key"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _generate_etag(self, data: dict) -> str:
        """Generate ETag for data"""
        content = json.dumps(data, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_stats(self) -> dict:
        """Get cache performance statistics"""
        total_requests = self.stats['edge_hits'] + self.stats['edge_misses']
        hit_rate = (self.stats['edge_hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'node_id': self.node_id,
            'total_requests': total_requests,
            'edge_hit_rate': f"{hit_rate:.1f}%",
            **self.stats
        }

# Test the edge-origin hybrid caching
async def test_edge_origin_cache():
    """
    Test edge-origin hybrid caching with various scenarios
    """
    cache = EdgeOriginCache('edge-us-west', 'https://origin.example.com')
    
    print("🧪 Testing Edge-Origin Hybrid Caching\n")
    
    # Test 1: Cold cache (cache miss)
    print("Test 1: Cold Cache Miss")
    result = await cache.get('user:12345', ttl=60)
    print(f"Result: {result['source']}, Age: {result.get('age_seconds', 0):.1f}s\n")
    
    # Test 2: Warm cache (cache hit)
    print("Test 2: Warm Cache Hit")
    result = await cache.get('user:12345', ttl=60)
    print(f"Result: {result['source']}, Age: {result.get('age_seconds', 0):.1f}s\n")
    
    # Test 3: Stale-while-revalidate
    print("Test 3: Stale-While-Revalidate")
    # Make cache stale
    cache.cache[cache._make_cache_key('user:12345')].timestamp -= 50
    result = await cache.get('user:12345', ttl=60, stale_while_revalidate=True)
    print(f"Result: {result['source']}, Age: {result.get('age_seconds', 0):.1f}s")
    await asyncio.sleep(0.2)  # Wait for background revalidation
    print(f"Background revalidation completed\n")
    
    # Test 4: Concurrent requests (cache stampede prevention)
    print("Test 4: Concurrent Requests (Stampede Prevention)")
    tasks = [cache.get('popular:item', ttl=120) for _ in range(10)]
    results = await asyncio.gather(*tasks)
    sources = [r['source'] for r in results]
    print(f"10 concurrent requests - Sources: {set(sources)}")
    print(f"Origin requests made: {cache.stats['origin_requests']} (should be 1)\n")
    
    # Print final statistics
    print("📊 Cache Performance Statistics:")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_edge_origin_cache())
```

---

## 🎨 Visual Learning: Edge Computing Architecture

### 🌐 Edge Computing Deployment Model
```
Global Edge Computing Architecture:

┌──────────────────────────────────────────────────────────┐
│                   Control Plane                          │
│  ┌────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │   Code     │  │  Configuration│  │   Monitoring   │  │
│  │ Repository │  │   Management  │  │  & Analytics   │  │
│  └────────────┘  └──────────────┘  └────────────────┘  │
└──────────────────────┬───────────────────────────────────┘
                       │ Deploy & Configure
                       ↓
┌──────────────────────────────────────────────────────────┐
│                Edge Computing Layer                      │
│                                                          │
│  🌍 North America (10 locations)                        │
│  ├─ us-west-1: 5ms user latency                        │
│  ├─ us-east-1: 8ms user latency                        │
│  └─ ca-central: 6ms user latency                       │
│                                                          │
│  🌍 Europe (8 locations)                                │
│  ├─ eu-west-1: 7ms user latency                        │
│  ├─ eu-central: 9ms user latency                       │
│  └─ eu-north: 12ms user latency                        │
│                                                          │
│  🌍 Asia-Pacific (12 locations)                         │
│  ├─ asia-se: 6ms user latency                          │
│  ├─ asia-ne: 8ms user latency                          │
│  └─ oceania: 15ms user latency                         │
└──────────────────────┬───────────────────────────────────┘
                       │ Fallback for complex operations
                       ↓
┌──────────────────────────────────────────────────────────┐
│               Regional Cloud Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │Americas  │  │  Europe  │  │   Asia   │             │
│  │50ms RTT  │  │ 45ms RTT │  │ 60ms RTT │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└──────────────────────┬───────────────────────────────────┘
                       │ Heavy processing & storage
                       ↓
┌──────────────────────────────────────────────────────────┐
│            Central Origin Infrastructure                 │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Database  │  │  ML Training  │  │  Analytics   │  │
│  │  Cluster    │  │   Pipeline    │  │  Warehouse   │  │
│  └─────────────┘  └──────────────┘  └──────────────┘  │
└──────────────────────────────────────────────────────────┘

Request Processing Flow:
User Request (0ms)
  ↓
Edge Location (5-15ms) → 80% of requests handled here
  ↓ (if needed)
Regional Cloud (50ms) → 15% escalated here
  ↓ (if needed)
Central Origin (100-200ms) → 5% need central processing
```

### 🔄 Anycast BGP Routing
```
BGP Anycast Network Topology:

Same IP Address: 192.0.2.1 announced from multiple locations

           Internet Core Routers
                    │
        ┌───────────┼───────────┐
        │           │           │
    ┌───┴───┐   ┌───┴───┐   ┌───┴───┐
    │ ISP A │   │ ISP B │   │ ISP C │
    │  AS1  │   │  AS2  │   │  AS3  │
    └───┬───┘   └───┬───┘   └───┬───┘
        │           │           │
┌───────┼───────────┼───────────┼───────┐
│       ↓           ↓           ↓       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│  │Virginia │ │ London  │ │  Tokyo  │ │
│  │ Anycast │ │ Anycast │ │ Anycast │ │
│  │192.0.2.1│ │192.0.2.1│ │192.0.2.1│ │
│  │ AS64512 │ │ AS64513 │ │ AS64514 │ │
│  └─────────┘ └─────────┘ └─────────┘ │
└───────────────────────────────────────┘

User in New York queries 192.0.2.1:
├─ ISP A routing table sees 3 paths:
│   ├─ Via AS64512 (Virginia): 2 hops ← Selected!
│   ├─ Via AS64513 (London): 6 hops
│   └─ Via AS64514 (Tokyo): 12 hops
├─ Automatically routes to Virginia
└─ User connects in 20ms

User in London queries 192.0.2.1:
├─ ISP B routing table sees 3 paths:
│   ├─ Via AS64512 (Virginia): 5 hops
│   ├─ Via AS64513 (London): 1 hop ← Selected!
│   └─ Via AS64514 (Tokyo): 10 hops
├─ Automatically routes to London
└─ User connects in 8ms

Benefits:
✓ Automatic geographic optimization
✓ Instant failover (BGP convergence: 30-180s)
✓ DDoS distribution across all locations
✓ No DNS dependency for routing
```

### 📊 Edge vs Cloud Performance
```
Performance Comparison:

Traditional Cloud Architecture:
User (Tokyo) → Internet → Cloud (Virginia) → Response
     ↓            ↓            ↓
   0ms         150ms        20ms (processing)
                           ────────────────
                           Total: 170ms

Edge Computing Architecture:
User (Tokyo) → Edge (Tokyo) → Response
     ↓            ↓
   0ms          8ms (processing)
                ────────────
                Total: 8ms

Performance Improvement: 95% faster! (170ms → 8ms)

Cost Comparison (1M requests/month):

Cloud-Only:
├─ Compute: 1M requests × $0.20/M = $0.20
├─ Data transfer: 100GB × $0.09/GB = $9.00
├─ Total: $9.20/month

Edge + Cloud (80% edge, 20% cloud):
├─ Edge compute: 800K × $0.50/M = $0.40
├─ Edge data transfer: 80GB × $0.01/GB = $0.80
├─ Cloud compute: 200K × $0.20/M = $0.04
├─ Cloud data transfer: 20GB × $0.09/GB = $1.80
├─ Total: $3.04/month

Savings: 67% cost reduction + 95% latency improvement!
```

---

## 🎯 Week 10 Wrap-Up: Edge Computing & Anycast Mastery

### 🧠 Mental Models to Internalize

1. **Edge Computing = Local Intelligence**: Process close to users, escalate to cloud when needed
2. **Anycast = Quantum Networking**: Same address exists in multiple places simultaneously
3. **CRDTs = Distributed Harmony**: Data structures that merge automatically without conflicts
4. **Stale-While-Revalidate = Optimistic Caching**: Serve fast, update in background

### 🏆 Principal Architect Decision Framework

**When to Use Edge Computing:**
- ✅ **Latency-sensitive applications** (gaming, video, real-time collaboration)
- ✅ **High-volume static content** (images, videos, CSS/JS)
- ✅ **Simple business logic** (authentication, routing, transformation)
- ✅ **Geographic compliance** (data must stay in region)

**When to Keep in Cloud:**
- ❌ **Complex stateful operations** (long transactions, heavy computation)
- ❌ **Large database queries** (multi-table joins, analytics)
- ❌ **Machine learning training** (requires GPU clusters)
- ❌ **Rare operations** (batch jobs, admin functions)

### 🚨 Common Edge Computing Mistakes

❌ **Over-engineering edge logic** = Complex code that belongs in cloud
❌ **Ignoring state management** = Assuming edge nodes are isolated
❌ **No fallback strategy** = Edge failures cause complete outages
❌ **Underestimating costs** = Edge compute can be expensive at high volume
✅ **Hybrid approach** = Use edge for performance, cloud for functionality

### 🔮 Preview: Week 11 - Performance Optimization & Monitoring

Next week we'll dive into performance optimization techniques and monitoring strategies. You'll learn how to measure, analyze, and optimize global systems, and build observability into distributed edge architectures.

---

## 🤔 Reflection Questions

Before moving to Week 11, ensure you can answer:

1. **ELI5**: "Why does TikTok load videos almost instantly no matter where you are, but some websites take forever?"

2. **Architect Level**: "Design an edge computing architecture for a multiplayer gaming platform that needs <20ms latency globally with strong consistency for game state."

3. **Technical Deep-Dive**: "Your anycast network shows good BGP convergence times (60s), but users report 5-minute outages during failures. What could be causing this discrepancy?"

4. **Business Analysis**: "Calculate the ROI of deploying edge computing for an e-commerce platform serving 10M users globally, considering latency improvements, conversion rate impacts, and infrastructure costs."

---

*"Edge computing is not just about speed - it's about fundamentally rethinking where computation happens in our globally distributed world."*

**Next**: [Week 11 - Performance Optimization & Monitoring](11-Week11-Performance-Monitoring.md)