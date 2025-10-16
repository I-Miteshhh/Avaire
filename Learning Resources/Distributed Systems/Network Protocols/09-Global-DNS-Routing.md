# Week 9: Global DNS Routing - Traffic Director of the Internet 🌍📡

*"DNS is like having the world's smartest traffic controller who knows exactly which road will get you home fastest, no matter where you are on the planet"*

## 🎯 This Week's Mission
Master how global services route users to optimal data centers using DNS intelligence. Learn anycast, GeoDNS, and traffic steering that ensures billions of users always connect to the fastest available infrastructure.

---

## 📋 Prerequisites: Building on Previous Weeks

You should now understand:
- ✅ **Microservices Communication**: How services coordinate across networks
- ✅ **CDN Architecture**: Global content distribution strategies
- ✅ **Load Balancing**: Traffic distribution across servers
- ✅ **Network Protocols**: TCP/UDP foundations and HTTP optimization

### New Concepts We'll Master
- **DNS Hierarchy**: The distributed naming system of the internet
- **Anycast Routing**: One IP address, multiple global locations
- **GeoDNS**: Location-based intelligent DNS responses
- **Traffic Steering**: Dynamic routing based on performance and health

---

## 🎪 Explain Like I'm 10: The World's Smartest GPS System

### 🗺️ The Old Way: Fixed Directions (Traditional DNS)

Imagine you want to visit "McDonald's" and your **old GPS** only knows about one location:

```
You: "Take me to McDonald's!"
Old GPS: "McDonald's is at 123 Main Street, New York"
You (in Tokyo): "But that's 7,000 miles away!"
Old GPS: "Sorry, that's the only McDonald's I know about"

Problems:
- Everyone goes to the same location (no load distribution)
- People from Tokyo fly to New York for a burger (terrible performance)
- If New York McDonald's closes → Nobody can get McDonald's anywhere
- No consideration for traffic, weather, or personal preferences
```

### 🧠 The Smart Way: Intelligent Location Service (Modern DNS)

Now imagine a **super-smart GPS** that knows about ALL McDonald's locations worldwide:

```
You (in Tokyo): "Take me to McDonald's!"
Smart GPS: 
├─ Checks your location: Tokyo, Japan
├─ Finds nearest McDonald's: Tokyo Shibuya (5 minutes away)
├─ Checks if it's open: Yes, 24/7
├─ Checks traffic conditions: Light traffic, clear roads
├─ Checks your preferences: You like the one with PlayPlace
└─ Result: "Go to Tokyo Shibuya McDonald's, 5 minutes via Route 246"

You (in London): "Take me to McDonald's!"
Smart GPS:
├─ Checks your location: London, UK  
├─ Finds nearest: London Oxford Street (3 minutes)
├─ Checks status: Very crowded (20 minute wait)
├─ Finds alternative: London Covent Garden (8 minutes, no wait)
└─ Result: "Go to Covent Garden McDonald's for faster service"

You (in Antarctica): "Take me to McDonald's!"
Smart GPS:
├─ Checks location: Antarctica Research Station
├─ Finds nearest: McMurdo Station (2 hours by snowmobile)
├─ Checks weather: Blizzard conditions, -40°F
├─ Safety check: Too dangerous to travel
└─ Result: "McDonald's delivery unavailable. Try instant ramen from base kitchen!"
```

### 🌍 The Magic Network: How Every GPS Knows Everything

The **Smart GPS Network** works like this:

```
🏢 Global Command Center (Root DNS)
├─ Knows about ALL regional controllers
├─ Updates every GPS device hourly
└─ Handles emergency route changes

🌍 Regional Controllers (TLD DNS - .com, .org, .jp)
├─ North America Controller → Knows all US/Canada McDonald's
├─ Europe Controller → Knows all European locations  
├─ Asia Controller → Knows all Asian locations
└─ Updates local GPS units every 15 minutes

📍 Local GPS Units (Recursive Resolvers)
├─ Cache popular locations (McDonald's, Starbucks)
├─ Remember recent searches (faster next time)
├─ Ask regional controllers for new places
└─ Share traffic updates with network

🎯 Smart Features:
├─ Health Monitoring: "Shibuya McDonald's ice cream machine is broken"
├─ Load Balancing: "Route 1/3 of customers to alternative locations"
├─ Failover: "Main location closed, redirect to backup location"
└─ Performance: "Route via highways during rush hour"
```

### 🔄 Anycast Magic: Same Address, Different Places

Here's the **coolest part** - imagine if ALL McDonald's had the **same exact address**:

```
Magic Address: "The McDonald's" (same everywhere)

Tokyo person calls "The McDonald's":
├─ Magic network checks caller location
├─ Routes call to Tokyo McDonald's automatically
└─ Person gets connected to nearby restaurant

London person calls "The McDonald's":  
├─ Same magic address, but network is smart
├─ Routes call to London McDonald's automatically  
└─ Person gets connected to their local restaurant

Benefits:
- Everyone remembers ONE simple address  
- Network automatically finds closest location
- If local McDonald's is closed → Routes to next closest
- No need to update address books when new locations open
```

---

## 🏗️ Principal Architect Depth: DNS as Global Traffic Intelligence

### 🚨 The DNS Performance Challenge

#### Problem 1: DNS Resolution Latency Impact
```
DNS Resolution Performance Analysis:

Traditional DNS Query Chain:
User → ISP DNS → Root DNS → .com DNS → example.com DNS → IP Address
  ↓       ↓         ↓        ↓           ↓              ↓
 1ms    50ms     100ms    150ms      200ms         300ms total

Impact on Web Performance:
├─ DNS resolution: 300ms
├─ TCP connection: 100ms  
├─ TLS handshake: 100ms
├─ HTTP request: 50ms
└─ Total Time to First Byte: 550ms

Optimized DNS (with caching and anycast):
User → Cached DNS → Anycast example.com → IP Address
  ↓       ↓              ↓                  ↓
 1ms     5ms           10ms             15ms total

Optimized Performance:
├─ DNS resolution: 15ms (95% improvement)
├─ Connection to optimal server: 20ms (geographically close)
├─ TLS with optimized ciphers: 50ms
├─ HTTP with compressed headers: 25ms
└─ Total Time to First Byte: 110ms (80% improvement)
```

#### Problem 2: Global Scale DNS Requirements
```
DNS Query Volume at Scale:

Google DNS (8.8.8.8) Statistics:
├─ Queries per second: 400+ billion
├─ Peak queries per second: 1.2 trillion  
├─ Global anycast locations: 100+
├─ Average response time: 7ms globally
└─ Uptime: 99.99% (4 minutes downtime per year)

Cloudflare DNS (1.1.1.1) Performance:
├─ Queries per day: 1+ trillion
├─ Response time P50: 4ms globally
├─ Response time P99: 30ms globally
├─ Coverage: 275+ cities worldwide
└─ Query resolution success rate: 99.99%

Facebook DNS Infrastructure:
├─ Internal DNS queries: 100+ million per second
├─ Authoritative DNS queries: 50+ billion per day
├─ DNS-based load balancing decisions: Real-time
├─ Failover detection time: <10 seconds globally
└─ Traffic steering accuracy: 99.95%
```

### 🌐 Advanced DNS Architecture Patterns

#### GeoDNS: Location-Aware Routing
```
Geographic DNS Resolution Strategy:

DNS Record Configuration:
example.com A Records:
├─ North America: 192.0.2.10 (Virginia data center)
├─ Europe: 192.0.2.20 (Ireland data center)  
├─ Asia-Pacific: 192.0.2.30 (Singapore data center)
├─ South America: 192.0.2.40 (Brazil data center)
└─ Oceania: 192.0.2.50 (Australia data center)

Intelligent Resolution Logic:
User Query from Tokyo:
├─ GeoDNS detects client IP: 203.0.113.100 (Tokyo, Japan)
├─ Calculates distance to all data centers:
│   ├─ Singapore: 5,300km (best choice)
│   ├─ Virginia: 10,900km  
│   ├─ Ireland: 9,600km
│   └─ Australia: 7,800km
├─ Returns Singapore IP: 192.0.2.30
└─ Result: 20ms latency vs 150ms to Virginia

Advanced GeoDNS Features:
├─ City-level granularity (not just country)
├─ ISP-specific routing (Comcast users → specific servers)
├─ Mobile carrier detection (Verizon vs AT&T routing)
└─ IPv6 dual-stack support
```

#### Anycast DNS: Same IP, Multiple Locations
```
Anycast Implementation Strategy:

Traditional Unicast:
DNS Server A: 192.0.2.10 (Only in Virginia)
DNS Server B: 192.0.2.11 (Only in Ireland)
DNS Server C: 192.0.2.12 (Only in Singapore)
Problem: Users must know which server to use

Anycast Deployment:
All DNS Servers: 192.0.2.1 (Same IP everywhere!)
├─ Virginia announces 192.0.2.1 to internet
├─ Ireland announces 192.0.2.1 to internet  
├─ Singapore announces 192.0.2.1 to internet
└─ Internet routing automatically sends users to closest

BGP Routing Magic:
User in New York → Routes to Virginia (shortest network path)
User in London → Routes to Ireland (shortest network path)
User in Tokyo → Routes to Singapore (shortest network path)

Anycast Benefits:
├─ Automatic load distribution by network topology
├─ Instant failover (if Virginia fails → Ireland takes over)
├─ DDoS attack mitigation (attack distributed across locations)
├─ Simplified client configuration (one IP to remember)
└─ Network-level load balancing (no application logic needed)
```

#### DNS-Based Load Balancing
```
Health-Check Driven DNS Responses:

Server Health Monitoring:
┌─────────────────────────────────────────────────────────┐
│ DNS Load Balancer continuously monitors:                │
│ ├─ Server A (Virginia): HTTP 200, 50ms response        │
│ ├─ Server B (Ireland): HTTP 200, 45ms response         │
│ ├─ Server C (Singapore): HTTP 503, server overloaded   │
│ └─ Server D (Australia): HTTP 200, 80ms response       │
└─────────────────────────────────────────────────────────┘

Intelligent DNS Responses:
Query from Europe:
├─ Primary choice: Ireland (45ms, healthy) ✓
├─ Backup choice: Virginia (85ms via Atlantic cable)
└─ DNS returns: Ireland IP with 60-second TTL

Query from Asia:
├─ Primary choice: Singapore (overloaded) ✗
├─ Fallback logic activated
├─ Alternative: Australia (80ms, healthy) ✓  
└─ DNS returns: Australia IP with 30-second TTL (shorter for faster recovery)

Advanced Load Balancing:
├─ Weighted round-robin (Server A gets 60% traffic, Server B gets 40%)
├─ Latency-based (always route to fastest responding server)
├─ Capacity-aware (consider CPU, memory, connection count)
├─ Cost optimization (prefer cheaper regions during off-peak)
└─ Compliance-aware (EU users must stay in EU for GDPR)
```

---

## 🌍 Real-World Implementation Examples

### 📊 Case Study 1: Netflix's Global DNS Strategy

**The Challenge**: Route 230M+ subscribers to optimal CDN servers globally

```
Netflix DNS Architecture:

Authoritative DNS Infrastructure:
├─ 50+ anycast DNS servers globally
├─ Custom DNS software optimized for video delivery
├─ Real-time integration with Open Connect CDN
├─ Sub-10ms DNS response times worldwide
└─ 99.99% uptime with automatic failover

Intelligent Routing Logic:
User requests "netflix.com":
├─ GeoDNS determines user location (city-level accuracy)
├─ Checks Netflix CDN server health in region:
│   ├─ ISP-embedded servers (1-2ms latency)
│   ├─ Regional cache servers (5-10ms latency)  
│   └─ Backbone cache servers (20-50ms latency)
├─ Considers current server load and capacity
├─ Factors in content availability (specific movies/shows)
└─ Returns IP of optimal server for that user

Performance Optimizations:
├─ EDNS Client Subnet (ECS) for precise location detection
├─ Dynamic TTLs (shorter during peak hours for faster failover)
├─ DNS prefetching for logged-in users
├─ IPv6 dual-stack with IPv6 preference
└─ DNS over HTTPS (DoH) for privacy and performance
```

**Netflix's DNS Performance Results**:
```
Global DNS Resolution Metrics:

Response Time by Region:
├─ North America: 8ms average (P99: 25ms)
├─ Europe: 12ms average (P99: 35ms)  
├─ Asia-Pacific: 15ms average (P99: 45ms)
├─ Latin America: 20ms average (P99: 60ms)
└─ Global Average: 11ms (P99: 35ms)

Routing Accuracy:
├─ Users routed to ISP-embedded servers: 85%
├─ Users routed to regional caches: 12%
├─ Users routed to backbone caches: 3%
├─ Optimal server selection accuracy: 99.2%
└─ Failover success rate: 99.8% (sub-30 second detection)

Business Impact:
├─ Streaming startup time: <2 seconds globally
├─ Rebuffering events: <0.1% of viewing time  
├─ User satisfaction: 95%+ in all regions
└─ Infrastructure cost optimization: 30% savings vs random routing
```

### 📊 Case Study 2: Cloudflare's Anycast DNS Network

**The Innovation**: Single IP address (1.1.1.1) serving from 275+ locations

```
Cloudflare's Global Anycast Implementation:

Network Architecture:
├─ 1.1.1.1 announced from 275+ cities worldwide
├─ 100+ Tbps total network capacity
├─ Average distance to user: <50km globally
├─ Automatic DDoS protection at network edge
└─ 99.99% uptime across entire global network

Anycast Routing Strategy:
Internet Routing Protocol (BGP):
├─ Each Cloudflare location announces 1.1.1.1 via BGP
├─ Internet routers automatically select shortest path
├─ If location fails → Traffic automatically reroutes  
├─ Load naturally distributes based on internet topology
└─ Zero configuration required for load balancing

Advanced Features:
├─ DNS over HTTPS (DoH) and DNS over TLS (DoT)
├─ DNSSEC validation for security
├─ Malware and phishing domain blocking
├─ Privacy protection (no logging of personal data)
├─ Query Name Minimization for enhanced privacy
└─ ECS (EDNS Client Subnet) support for CDN optimization
```

**Cloudflare's Performance Achievements**:
```
Global DNS Performance Metrics:

Speed Comparison (2023 data):
├─ Cloudflare 1.1.1.1: 4ms average globally
├─ Google 8.8.8.8: 7ms average globally
├─ Quad9 9.9.9.9: 12ms average globally  
├─ OpenDNS: 15ms average globally
└─ ISP Default DNS: 35ms average globally

Reliability Metrics:
├─ Query success rate: 99.99%
├─ Network uptime: 99.99% (measured per city)
├─ DDoS attack mitigation: 100+ Tbps peak capacity
├─ Failover time: <10 seconds (automatic BGP convergence)
└─ Global capacity utilization: <30% (massive headroom)

Privacy and Security:
├─ Malware domains blocked: 100M+ per day
├─ Privacy protection: No personal data logging  
├─ DNSSEC validation: 95%+ of signed domains
├─ DoH/DoT encryption: 40%+ of queries encrypted
└─ Response consistency: 99.98% (same answers globally)
```

### 📊 Case Study 3: Google's Traffic Director

**The Scale**: Route traffic for Google Search, YouTube, Gmail globally

```
Google's Global Load Balancing Architecture:

Maglev Load Balancer:
├─ Consistent hashing for connection affinity
├─ 10M+ packets per second per server
├─ Sub-microsecond failover detection
├─ ECMP (Equal Cost Multi-Path) routing
└─ Integration with Google's global network backbone

Cross-Region DNS Load Balancing:
├─ Real-time health checks across all regions
├─ Capacity-aware routing (CPU, memory, network utilization)  
├─ Predictive scaling based on traffic patterns
├─ Cost optimization (route to cheaper regions when possible)
├─ Compliance routing (data sovereignty requirements)
└─ Emergency traffic shifting for maintenance

Traffic Steering Intelligence:
├─ Machine learning for optimal routing decisions
├─ Real-time latency measurements between all regions
├─ User experience optimization (not just server metrics)
├─ A/B testing infrastructure integrated with routing
└─ Canary deployment support with gradual traffic shifting
```

---

## 🧪 Hands-On Lab: Build Global DNS Infrastructure

### 🔍 Experiment 1: GeoDNS Implementation

**Create location-aware DNS responses:**

```python
import socket
import geoip2.database
import geoip2.errors
from dnslib import DNSLabel, QTYPE, RR, A, DNSHeader, DNSRecord
from dnslib.server import DNSServer, DNSHandler, BaseResolver
import threading
import time

class GeoDNSResolver(BaseResolver):
    def __init__(self):
        # Download GeoLite2-City.mmdb from MaxMind for real implementation
        self.geo_db_path = 'GeoLite2-City.mmdb'
        
        # Define data center locations and their IP addresses
        self.data_centers = {
            'us-east': {
                'ip': '192.0.2.10',
                'location': {'lat': 39.0458, 'lon': -76.6413},  # Virginia
                'regions': ['US', 'CA']
            },
            'eu-west': {
                'ip': '192.0.2.20', 
                'location': {'lat': 53.4084, 'lon': -6.3044},   # Ireland
                'regions': ['GB', 'IE', 'FR', 'DE', 'NL', 'BE']
            },
            'asia-southeast': {
                'ip': '192.0.2.30',
                'location': {'lat': 1.3521, 'lon': 103.8198},   # Singapore  
                'regions': ['SG', 'MY', 'TH', 'ID', 'PH']
            },
            'asia-northeast': {
                'ip': '192.0.2.31',
                'location': {'lat': 35.6762, 'lon': 139.6503},  # Tokyo
                'regions': ['JP', 'KR']
            }
        }
        
        # Health status of each data center
        self.health_status = {dc: True for dc in self.data_centers}
        
        # Start health monitoring
        self.start_health_monitoring()
    
    def resolve(self, request, handler):
        """Resolve DNS query with geographic intelligence"""
        reply = request.reply()
        qname = str(request.q.qname).rstrip('.')
        qtype = request.q.qtype
        
        # Only handle A records for our demo domain
        if qtype == QTYPE.A and qname == 'api.example.com':
            client_ip = handler.client_address[0]
            optimal_ip = self.get_optimal_server(client_ip)
            
            if optimal_ip:
                # Return the optimal server IP
                reply.add_answer(RR(
                    request.q.qname,
                    QTYPE.A,
                    rdata=A(optimal_ip),
                    ttl=60  # Short TTL for faster failover
                ))
                
                print(f"GeoDNS: {client_ip} → {optimal_ip} (geo-optimized)")
            else:
                # No healthy servers available
                reply.header.rcode = 2  # SERVFAIL
                print(f"GeoDNS: No healthy servers for {client_ip}")
        
        return reply
    
    def get_optimal_server(self, client_ip):
        """Find optimal server for client based on location and health"""
        try:
            # Skip geo lookup for localhost/private IPs (use default)
            if client_ip in ['127.0.0.1', '::1'] or client_ip.startswith('192.168.'):
                return self.get_fallback_server()
            
            # Get client location (would use real GeoIP database)
            client_country = self.get_client_country(client_ip)
            
            # Find best data center for this client
            best_dc = None
            best_score = float('inf')
            
            for dc_name, dc_info in self.data_centers.items():
                # Skip unhealthy data centers
                if not self.health_status[dc_name]:
                    continue
                
                score = self.calculate_routing_score(client_country, dc_info)
                if score < best_score:
                    best_score = score
                    best_dc = dc_name
            
            if best_dc:
                return self.data_centers[best_dc]['ip']
            else:
                # All servers unhealthy, return fallback
                return self.get_fallback_server()
                
        except Exception as e:
            print(f"GeoDNS error: {e}")
            return self.get_fallback_server()
    
    def get_client_country(self, client_ip):
        """Get client country (simplified - would use real GeoIP)"""
        # Simulate geo detection based on IP ranges
        ip_parts = client_ip.split('.')
        if ip_parts[0] == '203':  # Simulate Asian IP range
            return 'JP'
        elif ip_parts[0] == '85':  # Simulate European IP range  
            return 'GB'
        elif ip_parts[0] == '198': # Simulate US IP range
            return 'US'
        else:
            return 'US'  # Default to US
    
    def calculate_routing_score(self, client_country, dc_info):
        """Calculate routing score (lower = better)"""
        base_score = 100
        
        # Regional preference
        if client_country in dc_info['regions']:
            base_score -= 50  # Strong preference for regional DC
        
        # Add latency simulation (would be real measurements)
        if client_country == 'US' and 'us-east' in str(dc_info['ip']):
            base_score -= 30
        elif client_country in ['GB', 'FR', 'DE'] and 'eu-west' in str(dc_info['ip']):
            base_score -= 30  
        elif client_country in ['JP', 'SG'] and 'asia' in str(dc_info['ip']):
            base_score -= 30
        
        return base_score
    
    def get_fallback_server(self):
        """Return fallback server when geo routing fails"""
        # Return first healthy server
        for dc_name, dc_info in self.data_centers.items():
            if self.health_status[dc_name]:
                return dc_info['ip']
        
        # Emergency fallback (would be cached/backup response)
        return '192.0.2.10'  # US East as last resort
    
    def start_health_monitoring(self):
        """Start background health monitoring"""
        def health_checker():
            while True:
                self.check_server_health()
                time.sleep(30)  # Check every 30 seconds
        
        health_thread = threading.Thread(target=health_checker, daemon=True)
        health_thread.start()
    
    def check_server_health(self):
        """Check health of all data centers"""
        for dc_name, dc_info in self.data_centers.items():
            # Simulate health check (would be real HTTP/TCP checks)
            import random
            healthy = random.random() > 0.1  # 90% uptime simulation
            
            if self.health_status[dc_name] != healthy:
                status = "HEALTHY" if healthy else "UNHEALTHY"
                print(f"Health Monitor: {dc_name} ({dc_info['ip']}) is now {status}")
                self.health_status[dc_name] = healthy

# DNS Server with GeoDNS
class GeoDNSServer:
    def __init__(self, host='localhost', port=5353):
        self.resolver = GeoDNSResolver()
        self.server = DNSServer(
            self.resolver, 
            port=port, 
            address=host,
            tcp=True
        )
    
    def start(self):
        print(f"GeoDNS Server starting on port 5353")
        print("Try: dig @localhost -p 5353 api.example.com")
        print("Server locations:")
        for dc_name, dc_info in self.resolver.data_centers.items():
            print(f"  {dc_name}: {dc_info['ip']} (regions: {dc_info['regions']})")
        
        self.server.start_thread()
        
        # Keep server running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down GeoDNS server...")
            self.server.stop()

# Test the GeoDNS server
if __name__ == "__main__":
    server = GeoDNSServer()
    server.start()
```

### 🔍 Experiment 2: DNS Load Balancing with Health Checks

**Implement intelligent DNS-based load balancing:**

```python
import asyncio
import aiohttp
import time
from datetime import datetime, timedelta
import json

class HealthChecker:
    def __init__(self):
        self.servers = {
            'web-1': {
                'ip': '192.0.2.100',
                'url': 'http://192.0.2.100:8080/health',
                'healthy': True,
                'last_check': None,
                'response_time': 0,
                'consecutive_failures': 0,
                'weight': 100  # Default weight
            },
            'web-2': {
                'ip': '192.0.2.101', 
                'url': 'http://192.0.2.101:8080/health',
                'healthy': True,
                'last_check': None,
                'response_time': 0,
                'consecutive_failures': 0,
                'weight': 100
            },
            'web-3': {
                'ip': '192.0.2.102',
                'url': 'http://192.0.2.102:8080/health',
                'healthy': True,
                'last_check': None,
                'response_time': 0,
                'consecutive_failures': 0,
                'weight': 100
            }
        }
        
        self.check_interval = 10  # seconds
        self.failure_threshold = 3
        self.recovery_threshold = 2
        
    async def start_monitoring(self):
        """Start continuous health monitoring"""
        while True:
            await self.check_all_servers()
            await asyncio.sleep(self.check_interval)
    
    async def check_all_servers(self):
        """Check health of all servers concurrently"""
        tasks = []
        for server_name in self.servers:
            task = asyncio.create_task(self.check_server_health(server_name))
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Update DNS records based on health status
        self.update_dns_records()
    
    async def check_server_health(self, server_name):
        """Check health of individual server"""
        server = self.servers[server_name]
        
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    server['url'], 
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    response_time = (time.time() - start_time) * 1000  # ms
                    
                    if response.status == 200:
                        # Health check passed
                        server['healthy'] = True
                        server['response_time'] = response_time
                        server['consecutive_failures'] = 0
                        server['last_check'] = datetime.now()
                        
                        # Adjust weight based on performance
                        if response_time < 50:
                            server['weight'] = 150  # Fast server gets more traffic
                        elif response_time < 100:
                            server['weight'] = 100  # Normal weight
                        else:
                            server['weight'] = 75   # Slow server gets less traffic
                        
                        print(f"✅ {server_name}: Healthy ({response_time:.1f}ms, weight: {server['weight']})")
                    else:
                        raise aiohttp.ClientResponseError(
                            None, None, status=response.status
                        )
                        
        except Exception as e:
            # Health check failed
            server['consecutive_failures'] += 1
            server['last_check'] = datetime.now()
            
            if server['consecutive_failures'] >= self.failure_threshold:
                if server['healthy']:
                    print(f"❌ {server_name}: Marking as UNHEALTHY after {server['consecutive_failures']} failures")
                server['healthy'] = False
                server['weight'] = 0  # Remove from load balancing
            else:
                print(f"⚠️  {server_name}: Failure {server['consecutive_failures']}/{self.failure_threshold} - {str(e)}")
    
    def update_dns_records(self):
        """Update DNS records based on current health status"""
        healthy_servers = [
            server for server in self.servers.values() 
            if server['healthy']
        ]
        
        if not healthy_servers:
            print("🚨 CRITICAL: No healthy servers available!")
            return
        
        # Calculate weighted distribution
        total_weight = sum(server['weight'] for server in healthy_servers)
        
        print(f"\n📊 DNS Record Update ({len(healthy_servers)} healthy servers):")
        for server_name, server in self.servers.items():
            if server['healthy']:
                percentage = (server['weight'] / total_weight) * 100
                print(f"   {server_name}: {server['ip']} (weight: {server['weight']}, {percentage:.1f}% traffic)")
        print()
    
    def get_dns_response(self, client_region='default'):
        """Generate DNS response based on current server health"""
        healthy_servers = [
            (name, server) for name, server in self.servers.items()
            if server['healthy']
        ]
        
        if not healthy_servers:
            # Emergency fallback
            return ['192.0.2.200']  # Backup server
        
        # Weighted random selection for demonstration
        import random
        weights = [server['weight'] for _, server in healthy_servers]
        selected = random.choices(healthy_servers, weights=weights, k=1)[0]
        
        return [selected[1]['ip']]
    
    def get_status_report(self):
        """Generate detailed status report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'healthy_servers': sum(1 for s in self.servers.values() if s['healthy']),
            'total_servers': len(self.servers),
            'servers': {}
        }
        
        for name, server in self.servers.items():
            report['servers'][name] = {
                'ip': server['ip'],
                'healthy': server['healthy'],
                'response_time': server['response_time'],
                'weight': server['weight'],
                'consecutive_failures': server['consecutive_failures'],
                'last_check': server['last_check'].isoformat() if server['last_check'] else None
            }
        
        return report

# DNS Load Balancer with Health-Aware Responses
class DNSLoadBalancer:
    def __init__(self):
        self.health_checker = HealthChecker()
        
    async def start(self):
        """Start the DNS load balancer"""
        print("🚀 Starting DNS Load Balancer with Health Monitoring")
        print("Monitoring servers:")
        for name, server in self.health_checker.servers.items():
            print(f"   {name}: {server['ip']} ({server['url']})")
        print()
        
        # Start health monitoring
        await self.health_checker.start_monitoring()
    
    def resolve_dns(self, domain, client_ip='0.0.0.0'):
        """Resolve DNS query with health-aware load balancing"""
        if domain == 'app.example.com':
            return self.health_checker.get_dns_response()
        else:
            return None  # Domain not handled

# Test the DNS load balancer
async def main():
    load_balancer = DNSLoadBalancer()
    
    # Start monitoring in background
    monitoring_task = asyncio.create_task(load_balancer.start())
    
    # Simulate DNS queries
    await asyncio.sleep(5)  # Let health checks run
    
    print("🧪 Testing DNS Resolution:")
    for i in range(10):
        response = load_balancer.resolve_dns('app.example.com')
        print(f"Query {i+1}: app.example.com → {response}")
        await asyncio.sleep(2)
    
    # Print final status report
    report = load_balancer.health_checker.get_status_report()
    print(f"\n📋 Final Status Report:")
    print(json.dumps(report, indent=2, default=str))

# Run the example
if __name__ == "__main__":
    # Note: This requires aiohttp: pip install aiohttp
    asyncio.run(main())
```

### 🔍 Experiment 3: Anycast Simulation

**Simulate anycast routing behavior:**

```python
import networkx as nx
import matplotlib.pyplot as plt
import random
from dataclasses import dataclass
from typing import List, Dict, Tuple
import math

@dataclass
class Location:
    name: str
    lat: float
    lon: float
    
@dataclass  
class AnycastNode:
    location: Location
    ip: str = "192.0.2.1"  # Same IP for all nodes (anycast)
    capacity: int = 1000   # Requests per second
    current_load: int = 0

class AnycastSimulator:
    def __init__(self):
        # Create global anycast network
        self.anycast_nodes = {
            'new-york': AnycastNode(Location('New York', 40.7128, -74.0060)),
            'london': AnycastNode(Location('London', 51.5074, -0.1278)),
            'tokyo': AnycastNode(Location('Tokyo', 35.6762, 139.6503)),
            'sydney': AnycastNode(Location('Sydney', -33.8688, 151.2093)),
            'singapore': AnycastNode(Location('Singapore', 1.3521, 103.8198)),
            'mumbai': AnycastNode(Location('Mumbai', 19.0760, 72.8777)),
            'sao-paulo': AnycastNode(Location('São Paulo', -23.5505, -46.6333)),
            'johannesburg': AnycastNode(Location('Johannesburg', -26.2041, 28.0473))
        }
        
        # Create network topology (simplified internet backbone)
        self.network = nx.Graph()
        self._build_network_topology()
        
        # Simulate user locations
        self.users = self._generate_user_locations(1000)
    
    def _build_network_topology(self):
        """Build simplified global internet topology"""
        locations = list(self.anycast_nodes.keys())
        
        # Add all locations as nodes
        for loc in locations:
            self.network.add_node(loc)
        
        # Add realistic intercontinental connections with latencies
        connections = [
            ('new-york', 'london', 70),      # Trans-Atlantic cable
            ('new-york', 'sao-paulo', 120),  # North-South America
            ('london', 'singapore', 180),    # Europe-Asia via Middle East
            ('london', 'johannesburg', 160), # Europe-Africa
            ('singapore', 'tokyo', 60),      # Intra-Asia
            ('singapore', 'sydney', 120),    # Asia-Oceania
            ('singapore', 'mumbai', 80),     # Southeast-South Asia
            ('tokyo', 'sydney', 140),        # Japan-Australia
            ('mumbai', 'london', 150),       # India-Europe
            ('new-york', 'tokyo', 180),      # Trans-Pacific (northern)
            ('sao-paulo', 'johannesburg', 200), # South America-Africa
        ]
        
        for src, dst, latency in connections:
            self.network.add_edge(src, dst, weight=latency)
    
    def _generate_user_locations(self, count):
        """Generate random user locations globally"""
        users = []
        
        # Population-weighted random locations
        population_centers = [
            ('new-york', 0.15),    # 15% North America  
            ('london', 0.12),      # 12% Europe
            ('tokyo', 0.08),       # 8% East Asia
            ('mumbai', 0.18),      # 18% South Asia (high population)
            ('singapore', 0.12),   # 12% Southeast Asia
            ('sydney', 0.03),      # 3% Oceania  
            ('sao-paulo', 0.15),   # 15% South America
            ('johannesburg', 0.17) # 17% Africa
        ]
        
        for i in range(count):
            # Choose region based on population weight
            region = random.choices(
                [center[0] for center in population_centers],
                weights=[center[1] for center in population_centers]
            )[0]
            
            users.append({
                'id': f'user_{i}',
                'region': region,
                'closest_node': region  # Simplified - users are "near" their regional node
            })
        
        return users
    
    def simulate_anycast_routing(self, user_requests=100):
        """Simulate anycast routing for user requests"""
        results = {
            'routing_decisions': [],
            'node_loads': {node: 0 for node in self.anycast_nodes},
            'total_latency': 0,
            'successful_requests': 0
        }
        
        # Randomly select users to make requests
        requesting_users = random.sample(self.users, user_requests)
        
        for user in requesting_users:
            # Find optimal anycast node for this user
            optimal_node = self._find_optimal_anycast_node(user)
            
            if optimal_node and self._can_handle_request(optimal_node):
                # Route to optimal node
                latency = self._calculate_latency(user['region'], optimal_node)
                
                results['routing_decisions'].append({
                    'user': user['id'],
                    'user_region': user['region'],
                    'routed_to': optimal_node,
                    'latency_ms': latency
                })
                
                results['node_loads'][optimal_node] += 1
                results['total_latency'] += latency
                results['successful_requests'] += 1
                
                # Update node load
                self.anycast_nodes[optimal_node].current_load += 1
            else:
                # Request failed (all nodes overloaded)
                results['routing_decisions'].append({
                    'user': user['id'],
                    'user_region': user['region'], 
                    'routed_to': None,
                    'latency_ms': float('inf')
                })
        
        # Calculate metrics
        if results['successful_requests'] > 0:
            results['average_latency'] = results['total_latency'] / results['successful_requests']
        else:
            results['average_latency'] = float('inf')
        
        results['success_rate'] = results['successful_requests'] / user_requests
        
        return results
    
    def _find_optimal_anycast_node(self, user):
        """Find optimal anycast node using network topology"""
        user_region = user['region']
        best_node = None
        best_latency = float('inf')
        
        for node_name, node in self.anycast_nodes.items():
            # Skip overloaded nodes
            if node.current_load >= node.capacity:
                continue
                
            # Calculate network latency using shortest path
            try:
                latency = nx.shortest_path_length(
                    self.network, 
                    user_region, 
                    node_name, 
                    weight='weight'
                )
                
                # Prefer less loaded nodes (add load penalty)
                load_penalty = (node.current_load / node.capacity) * 50
                total_cost = latency + load_penalty
                
                if total_cost < best_latency:
                    best_latency = total_cost
                    best_node = node_name
                    
            except nx.NetworkXNoPath:
                # No path to this node
                continue
        
        return best_node
    
    def _can_handle_request(self, node_name):
        """Check if node can handle additional request"""
        node = self.anycast_nodes[node_name]
        return node.current_load < node.capacity
    
    def _calculate_latency(self, source, destination):
        """Calculate latency between two nodes"""
        try:
            return nx.shortest_path_length(
                self.network,
                source,
                destination,
                weight='weight'
            )
        except nx.NetworkXNoPath:
            return 500  # High latency for unreachable nodes
    
    def generate_report(self, simulation_results):
        """Generate comprehensive simulation report"""
        print("🌍 Anycast Routing Simulation Report")
        print("=" * 50)
        
        print(f"📊 Overall Performance:")
        print(f"   Success Rate: {simulation_results['success_rate']:.1%}")
        print(f"   Average Latency: {simulation_results['average_latency']:.1f}ms")
        print(f"   Total Requests: {len(simulation_results['routing_decisions'])}")
        
        print(f"\n🏢 Node Utilization:")
        total_load = sum(simulation_results['node_loads'].values())
        for node_name, load in simulation_results['node_loads'].items():
            if total_load > 0:
                percentage = (load / total_load) * 100
                capacity = self.anycast_nodes[node_name].capacity
                utilization = (load / capacity) * 100
                print(f"   {node_name}: {load} requests ({percentage:.1f}% of traffic, {utilization:.1f}% capacity)")
        
        print(f"\n🌐 Latency Distribution:")
        latencies = [r['latency_ms'] for r in simulation_results['routing_decisions'] 
                    if r['latency_ms'] != float('inf')]
        
        if latencies:
            latencies.sort()
            p50 = latencies[len(latencies)//2]
            p90 = latencies[int(len(latencies)*0.9)]
            p99 = latencies[int(len(latencies)*0.99)]
            
            print(f"   P50 (median): {p50:.1f}ms")
            print(f"   P90: {p90:.1f}ms") 
            print(f"   P99: {p99:.1f}ms")
        
        print(f"\n🔀 Sample Routing Decisions:")
        for i, decision in enumerate(simulation_results['routing_decisions'][:10]):
            if decision['routed_to']:
                print(f"   {decision['user']} ({decision['user_region']}) → {decision['routed_to']} ({decision['latency_ms']:.1f}ms)")
            else:
                print(f"   {decision['user']} ({decision['user_region']}) → FAILED (overload)")
    
    def visualize_network(self):
        """Visualize the anycast network topology"""
        plt.figure(figsize=(15, 10))
        
        # Create layout based on geographic positions
        pos = {}
        for node_name, node in self.anycast_nodes.items():
            # Convert lat/lon to x/y for visualization  
            pos[node_name] = (node.location.lon, node.location.lat)
        
        # Draw network
        nx.draw(self.network, pos, with_labels=True, node_color='lightblue', 
                node_size=3000, font_size=8, font_weight='bold')
        
        # Add edge labels (latencies)
        edge_labels = nx.get_edge_attributes(self.network, 'weight')
        nx.draw_networkx_edge_labels(self.network, pos, edge_labels, font_size=6)
        
        plt.title('Anycast Network Topology\n(Numbers on edges are latencies in ms)')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.grid(True, alpha=0.3)
        plt.show()

# Run anycast simulation
def main():
    simulator = AnycastSimulator()
    
    print("🌍 Initializing Global Anycast Network")
    print(f"Anycast nodes: {len(simulator.anycast_nodes)}")
    print(f"Simulated users: {len(simulator.users)}")
    
    # Run simulation with different load levels
    for load_multiplier in [0.5, 1.0, 1.5, 2.0]:
        print(f"\n🧪 Simulation with {load_multiplier}x load:")
        
        # Reset node loads
        for node in simulator.anycast_nodes.values():
            node.current_load = 0
        
        # Run simulation
        requests = int(500 * load_multiplier)
        results = simulator.simulate_anycast_routing(requests)
        simulator.generate_report(results)
    
    # Visualize network (requires matplotlib)
    try:
        simulator.visualize_network()
    except ImportError:
        print("\n📈 Network visualization requires matplotlib")
        print("Install with: pip install matplotlib networkx")

if __name__ == "__main__":
    main()
```

---

## 🎨 Visual Learning: Global DNS Architecture

### 🌍 DNS Hierarchy and Resolution Flow
```
Global DNS Resolution Architecture:

┌─────────────────────────────────────────────────────────────┐
│                    Root DNS Servers                         │
│  a.root-servers.net → k.root-servers.net (13 worldwide)    │  
│  Authoritative for: "." (root zone)                        │
└─────────────────┬───────────────────────────────────────────┘
                  │ "Who handles .com?"
                  ↓
┌─────────────────────────────────────────────────────────────┐
│                  TLD DNS Servers                            │
│  .com → VeriSign (192.5.6.30, 192.12.94.30, etc.)        │
│  .org → PIR      .net → VeriSign   .gov → US Gov          │
└─────────────────┬───────────────────────────────────────────┘  
                  │ "Who handles example.com?"
                  ↓
┌─────────────────────────────────────────────────────────────┐
│              Authoritative DNS Servers                      │
│  example.com → ns1.example.com (203.0.113.10)             │
│               ns2.example.com (203.0.113.11)              │
└─────────────────┬───────────────────────────────────────────┘
                  │ "What's the IP for www.example.com?"
                  ↓
┌─────────────────────────────────────────────────────────────┐
│                 DNS Resolution                              │
│  www.example.com → 192.0.2.10 (GeoDNS response)           │
│  api.example.com → 192.0.2.20 (Load balanced)             │
│  cdn.example.com → 192.0.2.30 (CDN endpoint)              │
└─────────────────────────────────────────────────────────────┘

Full Resolution Chain (worst case):
User → ISP DNS → Root → .com TLD → example.com NS → Final IP
1ms → 50ms → 150ms → 200ms → 250ms → 300ms total

Optimized Resolution (with caching):
User → Cached ISP DNS → Cached example.com → Final IP  
1ms → 5ms → 10ms → 15ms total (95% improvement!)
```

### 🗺️ Anycast vs Unicast Routing
```
Unicast Routing (Traditional):

User A (Tokyo) → Specific Server (Virginia): 192.0.2.10
User B (London) → Specific Server (Virginia): 192.0.2.10  
User C (Sydney) → Specific Server (Virginia): 192.0.2.10

Problems:
├─ All traffic to single location (no geographic optimization)
├─ High latency for distant users (150ms+ from Asia/Europe)  
├─ Single point of failure (Virginia outage = global outage)
└─ Bandwidth bottleneck at single data center

Anycast Routing (Modern):

Multiple servers announce SAME IP: 192.0.2.1

┌──────────────────────────────────────────────────────────┐
│             Internet BGP Routing                         │
│                                                          │
│  192.0.2.1 ← Tokyo Server (AS64512)                    │
│  192.0.2.1 ← London Server (AS64513)                   │  
│  192.0.2.1 ← Virginia Server (AS64514)                 │
│                                                          │
└──────────────────────────────────────────────────────────┘
                          ↓
             Internet Automatically Routes:

User A (Tokyo) → 192.0.2.1 → Tokyo Server (10ms)
User B (London) → 192.0.2.1 → London Server (8ms)
User C (Sydney) → 192.0.2.1 → Tokyo Server (40ms) ← Closest

Benefits:
├─ Automatic geographic optimization (route to closest)
├─ Instant failover (if Tokyo fails → route to London)
├─ Load distribution by network topology
└─ Simplified client configuration (one IP to remember)
```

### 🎯 GeoDNS Intelligent Routing
```
GeoDNS Decision Matrix:

Query: api.example.com from Client IP: 203.0.113.50

Step 1: Geographic Detection
┌─────────────────────────────────────────┐
│ IP Geolocation Analysis                 │
│ 203.0.113.50 → Tokyo, Japan           │
│ ISP: NTT Communications                 │  
│ Coordinates: 35.6762°N, 139.6503°E    │
└─────────────────────────────────────────┘

Step 2: Data Center Distance Calculation
┌─────────────────────────────────────────┐
│ Distance to Available Servers:          │
│ ├─ Tokyo DC: 15km (5ms)                │
│ ├─ Singapore DC: 5,300km (45ms)        │
│ ├─ Virginia DC: 10,900km (150ms)       │
│ └─ London DC: 9,600km (130ms)          │
└─────────────────────────────────────────┘

Step 3: Health & Load Consideration  
┌─────────────────────────────────────────┐
│ Server Health Status:                   │
│ ├─ Tokyo DC: Healthy (CPU: 45%)        │
│ ├─ Singapore DC: Healthy (CPU: 80%)    │
│ ├─ Virginia DC: Overloaded (CPU: 95%)  │
│ └─ London DC: Healthy (CPU: 30%)       │
└─────────────────────────────────────────┘

Step 4: Intelligent Decision
┌─────────────────────────────────────────┐
│ GeoDNS Decision Logic:                  │
│ Primary: Tokyo (closest + healthy)      │
│ Backup: Singapore (regional + healthy)  │
│ Result: Return Tokyo IP: 192.0.2.30   │
│ TTL: 300 seconds (5 minutes)          │
└─────────────────────────────────────────┘

Benefits for User:
├─ Optimal performance: 5ms vs 150ms latency
├─ Reliable service: Healthy server selected
├─ Automatic failover: Backup server ready
└─ Regional compliance: Data stays in Asia-Pacific
```

---

## 🎯 Week 9 Wrap-Up: Global DNS Mastery

### 🧠 Mental Models to Internalize

1. **DNS = Global Phone Directory**: Hierarchical system that knows how to reach everyone
2. **Anycast = Magic Teleportation**: Same address, but you arrive at the closest location
3. **GeoDNS = Smart Travel Agent**: Always books you the best route based on your location
4. **Health Checks = Traffic Updates**: Real-time information about which routes are clear

### 🏆 Principal Architect Decision Framework

**DNS Strategy Selection:**
- **Traditional DNS**: Simple services, single data center, cost-sensitive
- **GeoDNS**: Global services, performance-critical, regional compliance needs
- **Anycast**: High availability, DDoS protection, simplified operations
- **Hybrid**: Large-scale systems using GeoDNS for application servers + Anycast for DNS infrastructure

**Performance Optimization Priorities:**
1. **Minimize DNS Resolution Time**: Anycast DNS servers, aggressive caching
2. **Optimize Routing Decisions**: Real-time health checks, performance monitoring
3. **Plan for Failures**: Multi-provider DNS, automatic failover, chaos testing
4. **Monitor User Experience**: Real user monitoring, synthetic checks, alerting

### 🚨 Common Global DNS Mistakes

❌ **Single DNS provider** = Vendor lock-in and single point of failure
❌ **Static DNS responses** = No adaptation to changing conditions
❌ **Long TTLs everywhere** = Slow failover and poor load distribution
❌ **No health monitoring** = Routing traffic to failed servers
✅ **Multi-provider strategy** = Redundancy and performance optimization

### 🔮 Preview: Week 10 - Anycast Implementation & Edge Computing

Next week we'll dive deep into implementing anycast networks and edge computing platforms. You'll learn how companies deploy compute resources globally and the technical challenges of maintaining consistency across edge locations.

---

## 🤔 Reflection Questions

Before moving to Week 10, ensure you can answer:

1. **ELI5**: "Why does Google.com load almost instantly no matter where you are in the world, but some websites take forever to load from different countries?"

2. **Architect Level**: "Design a global DNS strategy for a financial services company that must comply with data residency laws in 50+ countries while maintaining sub-50ms response times globally."

3. **Technical Deep-Dive**: "Your GeoDNS shows optimal routing decisions, but users in Asia report slow performance. Your CDN metrics show good hit rates. What could be wrong and how do you investigate?"

4. **Business Analysis**: "Calculate the infrastructure investment required to reduce global DNS resolution time from 150ms to 15ms for a service handling 1 billion queries per day."

---

*"DNS is the invisible foundation of the internet - get it right, and users never think about it. Get it wrong, and it's the only thing they remember."*

**Next**: [Week 10 - Anycast Implementation & Edge Computing](10-Week10-Anycast-Edge-Computing.md)