# Week 12: Capstone Project - Build a Global Video Streaming Platform 🎬🌍

*"You've learned the parts - now build the whole machine. This is where theory meets reality."*

## 🎯 The Ultimate Challenge

### Your Mission: Design "StreamVerse"

Build a **complete global video streaming platform** that rivals Netflix, YouTube, and Twitch. You'll integrate **every concept** from Weeks 1-11 into a production-grade architecture.

**StreamVerse Requirements:**
- 🌍 **100 million users** across 6 continents
- 🎥 **10,000 videos uploaded daily** (user-generated content)
- ⚡ **Sub-1-second startup time** globally
- 📊 **4K video streaming** with adaptive bitrate
- 💰 **99.99% uptime SLA** ($100K/minute in lost revenue)
- 🔐 **GDPR/CCPA compliance** for user data
- 📱 **Multi-device support** (web, mobile, smart TV, game consoles)

---

## 🎪 Explain Like I'm 10: The Ultimate Ice Cream Empire

Remember all our analogies? Now you're building the **world's biggest ice cream company** that combines everything!

### 🏗️ Your Ice Cream Empire Has:

**1. Recipes (Video Content)**
```
🍦 Ice Cream Factory (Content Origin):
├─ 10,000 new recipes created daily
├─ Professional chefs (Netflix Originals)
├─ Amateur cooks (User uploads)
└─ Quality control (Content moderation)

Process:
1. Chef creates recipe → Upload to factory
2. Factory creates ice cream → Store in warehouses
3. Package in different sizes → 4K, HD, SD versions
4. Distribute to shops → Global CDN delivery
```

**2. Delivery Network (CDN + Edge)**
```
🚚 Global Distribution (Remember Week 6?):
Main Warehouse (Origin Server):
└─ California HQ with all recipes

Regional Warehouses (CDN PoPs):
├─ 200 warehouses worldwide
├─ Stock popular flavors locally
├─ Predict what customers want
└─ Refresh from HQ nightly

Neighborhood Shops (Edge Locations):
├─ 1,000 local shops
├─ Serve customers in <1 minute
├─ Custom flavors on demand
└─ Smart inventory (cache)
```

**3. Smart Ordering System (Routing + Load Balancing)**
```
📱 Customer Orders Ice Cream (User Requests Video):

Step 1: Find Nearest Shop (DNS + GeoDNS)
Customer in Tokyo → Smart GPS system
├─ Check: Which shop is closest?
├─ Check: Which shop has stock?
├─ Check: Which shop is busy?
└─ Route: Tokyo Shop #3 (200ms away)

Step 2: Shop Serves Customer (Edge Delivery)
Tokyo Shop #3:
├─ Has flavor in freezer? → Serve instantly! (cache hit)
├─ No flavor? → Call regional warehouse (cache miss)
├─ Still no flavor? → Order from California HQ (origin)
└─ Save popular flavors (cache warming)

Step 3: Handle Rush Hour (Load Balancing)
100 customers arrive at once!
├─ Shop #3: 40 customers (40% capacity)
├─ Shop #5: 35 customers (35% capacity)  
├─ Shop #8: 25 customers (25% capacity)
└─ All shops balanced = Happy customers!
```

**4. Quality Monitoring (Observability)**
```
📊 Empire Control Center (Remember Week 11?):

Real-Time Dashboard:
┌────────────────────────────────────────┐
│ 🍦 GLOBAL ICE CREAM STATUS             │
├────────────────────────────────────────┤
│ Active Customers: 5.2 Million          │
│ Avg Wait Time: 45 seconds ✓           │
│ Customer Satisfaction: 98% ✓          │
│ Shops with Issues: 3 (1.5%) ⚠️        │
│                                        │
│ Problem Detected:                      │
│ Tokyo Shop #7 - Freezer broken!       │
│ Action: Route customers to Shop #3    │
│ ETA Fix: 15 minutes                   │
└────────────────────────────────────────┘

Monitoring Systems:
├─ Every shop reports status every 10 seconds
├─ Cameras watch customer lines (queue monitoring)
├─ Temperature sensors on freezers (infrastructure health)
├─ Customer feedback forms (RUM - Real User Monitoring)
└─ Robot customers test service (Synthetic monitoring)
```

**5. Emergency Response (Disaster Recovery)**
```
🚨 Crisis Scenarios:

Scenario 1: California Earthquake Destroys HQ
├─ Main warehouse gone!
├─ But regional warehouses still working
├─ Continue serving from cached inventory
├─ Activate backup HQ in Texas
└─ Customers never notice! ✓

Scenario 2: Typhoon Hits Tokyo
├─ All Tokyo shops flooded
├─ Redirect Tokyo customers to Osaka shops
├─ Osaka shops pre-stocked with popular Tokyo flavors
├─ Slightly slower (300ms vs 100ms) but working
└─ Service continues! ✓

Scenario 3: Chocolate Ice Cream Goes Viral
├─ Sudden 1000x demand for chocolate!
├─ Predictive system detects trend
├─ Auto-order more chocolate from HQ
├─ Rush delivery to all shops
├─ Increase chocolate freezer space
└─ Trend satisfied! ✓
```

### 🎯 The Complete Customer Journey

```
Customer: "I want to watch 'Stranger Things' in 4K!"

Journey Map (300 milliseconds total):

1. DNS Lookup (20ms) - Week 9 Concepts
   ├─ Customer asks: "Where is StreamVerse?"
   ├─ Smart DNS: "Use Tokyo server at 203.0.113.50"
   ├─ Anycast routing to nearest DNS
   └─ GeoDNS selects optimal server

2. TLS Handshake (80ms) - Week 3 Concepts
   ├─ Secure connection established
   ├─ Certificate validation
   ├─ HTTP/3 with QUIC
   └─ 0-RTT resumption (cached session)

3. Authentication (30ms) - Week 8 Concepts
   ├─ JWT token validation
   ├─ Edge authentication (no origin round-trip)
   ├─ User profile cached at edge
   └─ Authorization checks

4. Content Discovery (50ms) - Week 8 Concepts
   ├─ API Gateway routes request
   ├─ Recommendation service
   ├─ Cached recommendations (Redis)
   └─ Personalized homepage

5. Video Manifest Fetch (20ms) - Week 6/7 Concepts
   ├─ Manifest cached at Tokyo CDN
   ├─ Lists available quality levels
   ├─ Adaptive bitrate metadata
   └─ DRM license information

6. First Segment Download (100ms) - Week 6 Concepts
   ├─ CDN serves from Tokyo PoP
   ├─ First 2 seconds of video
   ├─ Parallel download of next segments
   └─ Prefetch based on predictions

Total: 300ms from click to playback! 🚀

Continuous Monitoring (Week 11):
├─ Every step measured and logged
├─ Trace ID: abc123 tracks entire journey
├─ Alerts if any step >threshold
├─ Automatic optimization suggestions
└─ User experience score: 98/100
```

---

## 🏗️ Principal Architect: StreamVerse Complete Architecture

### 🌍 Global Infrastructure Design

```
StreamVerse Multi-Region Architecture:

┌─────────────────────── GLOBAL LAYER ────────────────────────┐
│                                                              │
│  🌐 DNS (Route 53 / Cloudflare)                             │
│  ├─ GeoDNS: Route users to nearest region                   │
│  ├─ Health checks: Remove unhealthy regions                 │
│  ├─ Latency-based routing                                   │
│  └─ Failover: Primary → Secondary region                    │
│                                                              │
│  🔒 Global DDoS Protection (Cloudflare / Akamai)            │
│  ├─ 100+ Tbps capacity                                      │
│  ├─ Automatic attack mitigation                             │
│  ├─ Bot protection (ML-based)                               │
│  └─ WAF rules (OWASP Top 10)                                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────── EDGE LAYER ──────────────────────────┐
│                                                              │
│  📍 Edge PoPs (200+ Locations Worldwide)                    │
│  ├─ Cloudflare Workers / Lambda@Edge                        │
│  ├─ Edge compute for:                                       │
│  │   ├─ Authentication (JWT validation)                     │
│  │   ├─ A/B testing (feature flags)                         │
│  │   ├─ Image optimization (WebP conversion)               │
│  │   ├─ API response transformation                        │
│  │   └─ Request routing and rewrites                       │
│  │                                                           │
│  ├─ CDN Cache (Hot Content):                                │
│  │   ├─ Video segments (HLS/DASH)                           │
│  │   ├─ Thumbnails and images                               │
│  │   ├─ Static assets (JS, CSS)                             │
│  │   ├─ API responses (short TTL)                           │
│  │   └─ Cache size: 100TB per PoP                           │
│  │                                                           │
│  └─ Edge Storage (Warm Content):                            │
│      ├─ Recently popular videos                             │
│      ├─ Regional trending content                           │
│      ├─ Predicted popular uploads                           │
│      └─ Storage: 1PB per major PoP                          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────── REGIONAL LAYER ──────────────────────┐
│                                                              │
│  🌎 Regional Data Centers (6 Regions: US-East, US-West,     │
│     EU-West, Asia-Pacific, South America, Middle East)      │
│                                                              │
│  Each Region Contains:                                       │
│                                                              │
│  🔀 Load Balancers (L4 + L7)                                │
│  ├─ L4 (Network Load Balancer):                             │
│  │   ├─ Handles 10M+ concurrent connections                 │
│  │   ├─ TCP/UDP load balancing                              │
│  │   ├─ Direct Server Return (DSR)                          │
│  │   └─ Sub-millisecond latency                             │
│  │                                                           │
│  └─ L7 (Application Load Balancer):                         │
│      ├─ HTTP/HTTPS/HTTP2/HTTP3 support                      │
│      ├─ Path-based routing                                  │
│      ├─ Header-based routing                                │
│      ├─ WebSocket support (live streaming)                  │
│      └─ SSL/TLS termination                                 │
│                                                              │
│  🎬 Application Services (Kubernetes):                      │
│  ├─ Video Ingestion Service                                 │
│  │   ├─ Upload handling (resumable uploads)                 │
│  │   ├─ Virus/malware scanning                              │
│  │   ├─ Content moderation (ML-based)                       │
│  │   ├─ Metadata extraction                                 │
│  │   └─ Queue for transcoding: 10K videos/day               │
│  │                                                           │
│  ├─ Transcoding Service (GPU clusters)                      │
│  │   ├─ Multiple quality levels:                            │
│  │   │   ├─ 4K (3840x2160) @ 15 Mbps                        │
│  │   │   ├─ 1080p @ 5 Mbps                                  │
│  │   │   ├─ 720p @ 2.5 Mbps                                 │
│  │   │   ├─ 480p @ 1 Mbps                                   │
│  │   │   └─ 360p @ 500 Kbps                                 │
│  │   ├─ Codecs: H.264, H.265 (HEVC), AV1                    │
│  │   ├─ Formats: HLS, DASH                                  │
│  │   ├─ Parallel processing: 500 GPUs                       │
│  │   └─ Processing time: 1 hour video → 15 min encode       │
│  │                                                           │
│  ├─ API Gateway                                              │
│  │   ├─ Rate limiting (10K req/s per user)                  │
│  │   ├─ Authentication (OAuth 2.0 / JWT)                    │
│  │   ├─ Request validation (JSON Schema)                    │
│  │   ├─ Response caching (Redis)                            │
│  │   └─ Circuit breakers (prevent cascade failures)         │
│  │                                                           │
│  ├─ User Service                                             │
│  │   ├─ Profile management                                  │
│  │   ├─ Authentication / Authorization                       │
│  │   ├─ Subscription management                             │
│  │   ├─ Watch history                                       │
│  │   └─ Database: PostgreSQL (read replicas)                │
│  │                                                           │
│  ├─ Video Metadata Service                                   │
│  │   ├─ Video information (title, description, tags)         │
│  │   ├─ View counts and analytics                           │
│  │   ├─ Search indexing (Elasticsearch)                     │
│  │   ├─ Thumbnail management                                │
│  │   └─ Database: MongoDB (sharded)                         │
│  │                                                           │
│  ├─ Recommendation Service                                   │
│  │   ├─ ML models: Collaborative filtering                  │
│  │   ├─ Personalization engine                              │
│  │   ├─ Trending detection                                  │
│  │   ├─ A/B testing framework                               │
│  │   └─ Feature store: Redis                                │
│  │                                                           │
│  ├─ Live Streaming Service                                   │
│  │   ├─ WebRTC for low-latency streaming                    │
│  │   ├─ RTMP ingestion                                      │
│  │   ├─ Chat service (WebSocket)                            │
│  │   ├─ Concurrent viewers: 1M per stream                   │
│  │   └─ Latency: <2 seconds glass-to-glass                  │
│  │                                                           │
│  └─ Analytics Service                                        │
│      ├─ Real-time metrics (Prometheus)                      │
│      ├─ User behavior tracking                              │
│      ├─ Business intelligence                               │
│      ├─ Ad performance (if applicable)                      │
│      └─ Data warehouse: Snowflake                           │
│                                                              │
│  💾 Caching Layer (Multi-Tier)                              │
│  ├─ L1 Cache: Application memory (10ms)                     │
│  ├─ L2 Cache: Redis cluster (50ms)                          │
│  │   ├─ Session data                                        │
│  │   ├─ User profiles                                       │
│  │   ├─ API responses                                       │
│  │   ├─ Recommendation results                              │
│  │   └─ Size: 10TB per region                               │
│  │                                                           │
│  └─ L3 Cache: Memcached (100ms)                             │
│      ├─ Video metadata                                      │
│      ├─ Search results                                      │
│      ├─ Static content                                      │
│      └─ Size: 50TB per region                               │
│                                                              │
│  🗄️ Databases (Multi-Master Replication)                   │
│  ├─ PostgreSQL (User data, transactions)                    │
│  │   ├─ Primary: 1 write master per region                  │
│  │   ├─ Replicas: 5 read replicas per region               │
│  │   ├─ Cross-region replication: Async                    │
│  │   └─ Backup: Point-in-time recovery (PITR)              │
│  │                                                           │
│  ├─ MongoDB (Video metadata, comments)                      │
│  │   ├─ Sharded by video_id (100 shards)                    │
│  │   ├─ Replica set: 3 nodes per shard                     │
│  │   ├─ Global secondary indexes                            │
│  │   └─ Size: 500TB per region                              │
│  │                                                           │
│  ├─ Elasticsearch (Search, analytics)                       │
│  │   ├─ 50 nodes per cluster                                │
│  │   ├─ Full-text search on metadata                        │
│  │   ├─ Aggregations for trending                           │
│  │   └─ Size: 200TB per region                              │
│  │                                                           │
│  └─ Cassandra (Time-series data)                            │
│      ├─ Viewing history                                     │
│      ├─ Analytics events                                    │
│      ├─ Log aggregation                                     │
│      └─ Size: 1PB per region                                │
│                                                              │
│  📦 Object Storage (Video Files)                            │
│  ├─ Amazon S3 / Google Cloud Storage                        │
│  ├─ Storage classes:                                        │
│  │   ├─ Hot: Recent uploads (30 days)                       │
│  │   ├─ Warm: Popular content (90 days)                     │
│  │   ├─ Cold: Archive (>90 days)                            │
│  │   └─ Glacier: Legal retention (7 years)                  │
│  ├─ Redundancy: Cross-region replication                    │
│  ├─ Total storage: 100PB+ globally                          │
│  └─ Cost optimization: Lifecycle policies                   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────── OBSERVABILITY LAYER ─────────────────────┐
│                                                              │
│  📊 Metrics (Prometheus + Grafana)                          │
│  ├─ System metrics: CPU, memory, disk, network              │
│  ├─ Application metrics: Request rate, latency, errors      │
│  ├─ Business metrics: Uploads, views, revenue               │
│  ├─ Retention: 90 days detailed, 2 years aggregated         │
│  └─ Alerting: PagerDuty integration                         │
│                                                              │
│  📝 Logs (ELK Stack: Elasticsearch, Logstash, Kibana)      │
│  ├─ Application logs: Structured JSON                       │
│  ├─ Access logs: HTTP requests                              │
│  ├─ Error logs: Stack traces, exceptions                    │
│  ├─ Volume: 100TB/day globally                              │
│  ├─ Retention: 30 days                                      │
│  └─ Search: Sub-second queries                              │
│                                                              │
│  🔍 Traces (Jaeger / AWS X-Ray)                            │
│  ├─ Distributed request tracing                             │
│  ├─ Service dependency maps                                 │
│  ├─ Performance bottleneck detection                        │
│  ├─ Sampling: 1% of requests (10M traces/day)               │
│  └─ Retention: 14 days                                      │
│                                                              │
│  🎯 Real User Monitoring (RUM)                              │
│  ├─ JavaScript agent in web player                          │
│  ├─ Mobile SDK in apps                                      │
│  ├─ Metrics: Page load, video startup, buffering            │
│  ├─ Sampling: 10% of sessions                               │
│  └─ Correlation with business metrics                       │
│                                                              │
│  🤖 Synthetic Monitoring                                    │
│  ├─ Automated tests from 50 global locations                │
│  ├─ Test scenarios:                                         │
│  │   ├─ Homepage load                                       │
│  │   ├─ Video playback                                      │
│  │   ├─ Upload workflow                                     │
│  │   ├─ Search functionality                                │
│  │   └─ Live stream startup                                 │
│  ├─ Frequency: Every 5 minutes                              │
│  └─ Alerting: <99.9% success rate                           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎬 Implementation: Critical User Flows

### Flow 1: Video Upload & Processing Pipeline

```python
"""
StreamVerse Video Upload Service
Handles user video uploads, processing, and distribution
"""

import asyncio
import hashlib
import os
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
import aiohttp
import boto3
from datetime import datetime

class VideoQuality(Enum):
    QUALITY_4K = "4k"
    QUALITY_1080P = "1080p"
    QUALITY_720P = "720p"
    QUALITY_480P = "480p"
    QUALITY_360P = "360p"

class ProcessingStatus(Enum):
    UPLOADED = "uploaded"
    SCANNING = "scanning"
    TRANSCODING = "transcoding"
    READY = "ready"
    FAILED = "failed"

@dataclass
class VideoMetadata:
    video_id: str
    user_id: str
    title: str
    description: str
    duration_seconds: int
    upload_timestamp: float
    original_size_bytes: int
    original_format: str
    status: ProcessingStatus
    qualities_available: List[VideoQuality]
    
@dataclass
class TranscodingJob:
    job_id: str
    video_id: str
    input_file: str
    output_quality: VideoQuality
    status: ProcessingStatus
    progress_percent: int
    error_message: Optional[str] = None

class VideoUploadService:
    """
    Handles video upload with resumable uploads, virus scanning,
    and queuing for transcoding
    """
    
    def __init__(self, s3_bucket: str, cdn_url: str):
        self.s3_bucket = s3_bucket
        self.cdn_url = cdn_url
        self.s3_client = boto3.client('s3')
        
        # Upload configuration
        self.chunk_size = 10 * 1024 * 1024  # 10MB chunks
        self.max_file_size = 100 * 1024 * 1024 * 1024  # 100GB
        
        # Virus scanning (simulated)
        self.virus_scanner_url = "https://scanner.streamverse.com/scan"
    
    async def create_upload_session(self, user_id: str, filename: str, 
                                   file_size: int) -> dict:
        """
        Create resumable upload session
        Returns upload URL and session ID
        """
        if file_size > self.max_file_size:
            raise ValueError(f"File size {file_size} exceeds maximum {self.max_file_size}")
        
        # Generate unique video ID
        video_id = self.generate_video_id(user_id, filename)
        
        # Calculate number of chunks
        num_chunks = (file_size + self.chunk_size - 1) // self.chunk_size
        
        # Create multipart upload in S3
        response = self.s3_client.create_multipart_upload(
            Bucket=self.s3_bucket,
            Key=f"uploads/{video_id}/original",
            ContentType='video/mp4',
            Metadata={
                'user_id': user_id,
                'filename': filename,
                'upload_timestamp': str(datetime.now().timestamp())
            }
        )
        
        upload_id = response['UploadId']
        
        # Generate presigned URLs for each chunk
        presigned_urls = []
        for part_number in range(1, num_chunks + 1):
            url = self.s3_client.generate_presigned_url(
                'upload_part',
                Params={
                    'Bucket': self.s3_bucket,
                    'Key': f"uploads/{video_id}/original",
                    'UploadId': upload_id,
                    'PartNumber': part_number
                },
                ExpiresIn=3600  # 1 hour expiry
            )
            presigned_urls.append(url)
        
        return {
            'video_id': video_id,
            'upload_id': upload_id,
            'chunk_size': self.chunk_size,
            'num_chunks': num_chunks,
            'presigned_urls': presigned_urls,
            'expires_in': 3600
        }
    
    async def complete_upload(self, video_id: str, upload_id: str, 
                             parts: List[dict]) -> VideoMetadata:
        """
        Complete multipart upload and start processing
        """
        # Complete multipart upload
        self.s3_client.complete_multipart_upload(
            Bucket=self.s3_bucket,
            Key=f"uploads/{video_id}/original",
            UploadId=upload_id,
            MultipartUpload={'Parts': parts}
        )
        
        # Get file metadata
        response = self.s3_client.head_object(
            Bucket=self.s3_bucket,
            Key=f"uploads/{video_id}/original"
        )
        
        metadata = VideoMetadata(
            video_id=video_id,
            user_id=response['Metadata']['user_id'],
            title="Untitled Video",  # Set by user later
            description="",
            duration_seconds=0,  # Extracted during transcoding
            upload_timestamp=float(response['Metadata']['upload_timestamp']),
            original_size_bytes=response['ContentLength'],
            original_format='mp4',
            status=ProcessingStatus.SCANNING,
            qualities_available=[]
        )
        
        # Start virus scanning
        await self.scan_video(video_id)
        
        # Queue for transcoding
        await self.queue_transcoding(metadata)
        
        return metadata
    
    async def scan_video(self, video_id: str):
        """
        Scan video for viruses and malware
        """
        print(f"🔍 Scanning video {video_id} for viruses...")
        
        # Simulated virus scanning
        # In production, use ClamAV, VirusTotal API, or cloud provider scanning
        await asyncio.sleep(2)  # Simulate scan time
        
        print(f"✅ Video {video_id} passed virus scan")
    
    async def queue_transcoding(self, metadata: VideoMetadata):
        """
        Queue video for transcoding into multiple quality levels
        """
        print(f"📤 Queuing video {metadata.video_id} for transcoding...")
        
        # In production, send to message queue (SQS, RabbitMQ, Kafka)
        transcoding_job = {
            'video_id': metadata.video_id,
            'input_file': f"s3://{self.s3_bucket}/uploads/{metadata.video_id}/original",
            'output_formats': [q.value for q in VideoQuality],
            'callback_url': f"https://api.streamverse.com/transcoding/callback"
        }
        
        # Simulate queue submission
        print(f"✅ Transcoding job queued: {transcoding_job}")
    
    def generate_video_id(self, user_id: str, filename: str) -> str:
        """Generate unique video ID"""
        data = f"{user_id}:{filename}:{datetime.now().timestamp()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

class VideoTranscodingService:
    """
    Transcodes videos into multiple quality levels and formats
    Uses GPU-accelerated encoding
    """
    
    def __init__(self, gpu_cluster_url: str):
        self.gpu_cluster_url = gpu_cluster_url
        
        # Encoding presets (bitrates in Mbps)
        self.encoding_presets = {
            VideoQuality.QUALITY_4K: {
                'resolution': '3840x2160',
                'bitrate': '15000k',
                'codec': 'libx265',  # HEVC for 4K
                'fps': 60
            },
            VideoQuality.QUALITY_1080P: {
                'resolution': '1920x1080',
                'bitrate': '5000k',
                'codec': 'libx264',
                'fps': 60
            },
            VideoQuality.QUALITY_720P: {
                'resolution': '1280x720',
                'bitrate': '2500k',
                'codec': 'libx264',
                'fps': 30
            },
            VideoQuality.QUALITY_480P: {
                'resolution': '854x480',
                'bitrate': '1000k',
                'codec': 'libx264',
                'fps': 30
            },
            VideoQuality.QUALITY_360P: {
                'resolution': '640x360',
                'bitrate': '500k',
                'codec': 'libx264',
                'fps': 30
            }
        }
    
    async def transcode_video(self, job: TranscodingJob) -> dict:
        """
        Transcode video to specified quality
        Returns output file path and metadata
        """
        print(f"🎬 Starting transcoding: {job.video_id} → {job.output_quality.value}")
        
        preset = self.encoding_presets[job.output_quality]
        
        # In production, use FFmpeg with GPU acceleration:
        # ffmpeg -hwaccel cuda -i input.mp4 \
        #        -c:v h264_nvenc -preset p7 -b:v 5000k \
        #        -s 1920x1080 -r 60 \
        #        -c:a aac -b:a 128k \
        #        -f hls -hls_time 6 -hls_list_size 0 \
        #        output.m3u8
        
        # Simulate transcoding progress
        for progress in range(0, 101, 10):
            job.progress_percent = progress
            print(f"   Progress: {progress}% ({job.output_quality.value})")
            await asyncio.sleep(0.5)  # Simulate work
        
        output_path = f"s3://streamverse/videos/{job.video_id}/{job.output_quality.value}/playlist.m3u8"
        
        print(f"✅ Transcoding complete: {job.output_quality.value} → {output_path}")
        
        return {
            'job_id': job.job_id,
            'video_id': job.video_id,
            'quality': job.output_quality.value,
            'output_path': output_path,
            'format': 'HLS',
            'duration_seconds': 120,  # Extracted during transcoding
            'file_size_mb': 50
        }
    
    async def transcode_all_qualities(self, video_id: str, input_file: str) -> List[dict]:
        """
        Transcode video into all quality levels in parallel
        """
        print(f"\n🚀 Starting parallel transcoding for {video_id}...\n")
        
        # Create transcoding jobs for each quality
        jobs = []
        for quality in VideoQuality:
            job = TranscodingJob(
                job_id=f"{video_id}_{quality.value}",
                video_id=video_id,
                input_file=input_file,
                output_quality=quality,
                status=ProcessingStatus.TRANSCODING,
                progress_percent=0
            )
            jobs.append(job)
        
        # Run transcoding jobs in parallel
        results = await asyncio.gather(
            *[self.transcode_video(job) for job in jobs]
        )
        
        print(f"\n✅ All transcoding complete for {video_id}!")
        return results

# Example usage
async def demo_video_upload():
    """Demonstrate video upload and processing pipeline"""
    
    upload_service = VideoUploadService(
        s3_bucket='streamverse-uploads',
        cdn_url='https://cdn.streamverse.com'
    )
    
    transcoding_service = VideoTranscodingService(
        gpu_cluster_url='https://transcode.streamverse.com'
    )
    
    # Step 1: Create upload session
    print("📤 Creating upload session...")
    session = await upload_service.create_upload_session(
        user_id='user_12345',
        filename='my_awesome_video.mp4',
        file_size=1024 * 1024 * 100  # 100MB
    )
    
    print(f"✅ Upload session created:")
    print(f"   Video ID: {session['video_id']}")
    print(f"   Chunks: {session['num_chunks']}")
    print(f"   Chunk size: {session['chunk_size'] / 1024 / 1024}MB")
    
    # Step 2: Simulate chunk uploads (in production, client uploads chunks)
    print(f"\n📦 Simulating {session['num_chunks']} chunk uploads...")
    await asyncio.sleep(2)
    
    # Step 3: Complete upload
    print("\n✅ All chunks uploaded, completing upload...")
    parts = [{'ETag': f"etag_{i}", 'PartNumber': i} for i in range(1, session['num_chunks'] + 1)]
    
    # In production, call complete_upload after scanning and metadata extraction
    # metadata = await upload_service.complete_upload(
    #     session['video_id'], 
    #     session['upload_id'], 
    #     parts
    # )
    
    # Step 4: Transcode video
    print("\n🎬 Starting transcoding pipeline...")
    results = await transcoding_service.transcode_all_qualities(
        video_id=session['video_id'],
        input_file=f"s3://streamverse-uploads/uploads/{session['video_id']}/original"
    )
    
    # Step 5: Update CDN
    print("\n🌍 Distributing to global CDN...")
    for result in results:
        print(f"   ✅ {result['quality']}: {result['output_path']}")
    
    print("\n🎉 Video processing complete! Ready for playback globally.")

if __name__ == "__main__":
    asyncio.run(demo_video_upload())
```

### Flow 2: Adaptive Bitrate Video Playback

```python
"""
StreamVerse Adaptive Bitrate Player
Dynamically adjusts video quality based on network conditions
"""

import asyncio
import time
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class NetworkQuality(Enum):
    EXCELLENT = "excellent"  # >10 Mbps
    GOOD = "good"            # 5-10 Mbps
    FAIR = "fair"            # 2-5 Mbps
    POOR = "poor"            # <2 Mbps

@dataclass
class VideoSegment:
    segment_number: int
    quality: VideoQuality
    url: str
    duration_seconds: float
    size_bytes: int

@dataclass
class PlaybackMetrics:
    current_bandwidth_mbps: float
    buffer_seconds: float
    dropped_frames: int
    current_quality: VideoQuality
    rebuffer_count: int
    startup_time_ms: float

class AdaptiveBitratePlayer:
    """
    Adaptive Bitrate (ABR) video player with smart quality switching
    """
    
    def __init__(self, video_id: str, cdn_url: str):
        self.video_id = video_id
        self.cdn_url = cdn_url
        
        # Player state
        self.current_segment = 0
        self.current_quality = VideoQuality.QUALITY_720P
        self.buffer: List[VideoSegment] = []
        self.max_buffer_seconds = 30
        self.min_buffer_seconds = 5
        
        # Performance metrics
        self.metrics = PlaybackMetrics(
            current_bandwidth_mbps=5.0,
            buffer_seconds=0,
            dropped_frames=0,
            current_quality=self.current_quality,
            rebuffer_count=0,
            startup_time_ms=0
        )
        
        # Bandwidth estimation
        self.bandwidth_samples: List[float] = []
        self.max_bandwidth_samples = 10
    
    async def start_playback(self):
        """
        Start video playback with fast startup
        """
        start_time = time.time()
        
        print(f"▶️  Starting playback for video {self.video_id}...")
        
        # Step 1: Fetch manifest (lists all available qualities and segments)
        manifest = await self.fetch_manifest()
        print(f"✅ Manifest fetched: {len(manifest['qualities'])} qualities available")
        
        # Step 2: Start with lower quality for fast startup
        startup_quality = VideoQuality.QUALITY_480P
        print(f"🚀 Starting with {startup_quality.value} for fast startup")
        
        # Step 3: Download first segment
        first_segment = await self.download_segment(0, startup_quality)
        self.buffer.append(first_segment)
        
        # Step 4: Calculate startup time
        self.metrics.startup_time_ms = (time.time() - start_time) * 1000
        print(f"✅ First frame in {self.metrics.startup_time_ms:.0f}ms")
        
        # Step 5: Start playback loop
        await self.playback_loop()
    
    async def fetch_manifest(self) -> dict:
        """
        Fetch HLS/DASH manifest with available qualities
        """
        # Simulate manifest fetch
        await asyncio.sleep(0.02)  # 20ms (cached at edge)
        
        return {
            'video_id': self.video_id,
            'duration_seconds': 600,
            'segment_duration': 6,
            'qualities': [q.value for q in VideoQuality]
        }
    
    async def download_segment(self, segment_number: int, 
                              quality: VideoQuality) -> VideoSegment:
        """
        Download video segment from CDN
        """
        url = f"{self.cdn_url}/videos/{self.video_id}/{quality.value}/segment_{segment_number}.ts"
        
        # Simulate download with bandwidth measurement
        segment_size = {
            VideoQuality.QUALITY_4K: 11_250_000,     # 15 Mbps * 6 sec / 8
            VideoQuality.QUALITY_1080P: 3_750_000,   # 5 Mbps * 6 sec / 8
            VideoQuality.QUALITY_720P: 1_875_000,    # 2.5 Mbps * 6 sec / 8
            VideoQuality.QUALITY_480P: 750_000,      # 1 Mbps * 6 sec / 8
            VideoQuality.QUALITY_360P: 375_000,      # 0.5 Mbps * 6 sec / 8
        }[quality]
        
        download_start = time.time()
        
        # Simulate download time based on bandwidth
        download_time = segment_size / (self.metrics.current_bandwidth_mbps * 1_000_000 / 8)
        await asyncio.sleep(download_time)
        
        download_duration = time.time() - download_start
        
        # Update bandwidth estimate
        measured_bandwidth = (segment_size * 8) / download_duration / 1_000_000  # Mbps
        self.update_bandwidth_estimate(measured_bandwidth)
        
        return VideoSegment(
            segment_number=segment_number,
            quality=quality,
            url=url,
            duration_seconds=6.0,
            size_bytes=segment_size
        )
    
    def update_bandwidth_estimate(self, measured_bandwidth: float):
        """
        Update bandwidth estimate using exponential weighted moving average
        """
        self.bandwidth_samples.append(measured_bandwidth)
        
        # Keep only recent samples
        if len(self.bandwidth_samples) > self.max_bandwidth_samples:
            self.bandwidth_samples.pop(0)
        
        # Calculate weighted average (more weight to recent samples)
        weights = [0.5 ** (len(self.bandwidth_samples) - i - 1) 
                   for i in range(len(self.bandwidth_samples))]
        total_weight = sum(weights)
        
        self.metrics.current_bandwidth_mbps = sum(
            bw * w for bw, w in zip(self.bandwidth_samples, weights)
        ) / total_weight
    
    def select_optimal_quality(self) -> VideoQuality:
        """
        Select optimal quality based on bandwidth and buffer level
        Uses conservative algorithm to avoid rebuffering
        """
        bandwidth = self.metrics.current_bandwidth_mbps
        buffer_level = self.metrics.buffer_seconds
        
        # Safety margin: Use 80% of measured bandwidth
        safe_bandwidth = bandwidth * 0.8
        
        # If buffer is low, be more conservative
        if buffer_level < self.min_buffer_seconds:
            safe_bandwidth *= 0.6
        
        # Select quality based on bandwidth
        if safe_bandwidth >= 15:
            return VideoQuality.QUALITY_4K
        elif safe_bandwidth >= 5:
            return VideoQuality.QUALITY_1080P
        elif safe_bandwidth >= 2.5:
            return VideoQuality.QUALITY_720P
        elif safe_bandwidth >= 1:
            return VideoQuality.QUALITY_480P
        else:
            return VideoQuality.QUALITY_360P
    
    async def playback_loop(self):
        """
        Main playback loop: download segments, manage buffer, adapt quality
        """
        print("\n🎬 Playback started!\n")
        
        for segment_num in range(100):  # Demo: play 100 segments (10 minutes)
            # Simulate playback consuming buffer
            if self.buffer:
                playing_segment = self.buffer.pop(0)
                self.metrics.buffer_seconds = sum(s.duration_seconds for s in self.buffer)
                
                print(f"▶️  Playing segment {playing_segment.segment_number} "
                      f"({playing_segment.quality.value}) | "
                      f"Buffer: {self.metrics.buffer_seconds:.1f}s | "
                      f"Bandwidth: {self.metrics.current_bandwidth_mbps:.2f} Mbps")
                
                # Simulate playback time
                await asyncio.sleep(0.1)  # Compressed time for demo
            
            # Select optimal quality for next segment
            optimal_quality = self.select_optimal_quality()
            
            if optimal_quality != self.current_quality:
                print(f"🔄 Quality switching: {self.current_quality.value} → {optimal_quality.value}")
                self.current_quality = optimal_quality
            
            # Download next segment(s) to maintain buffer
            while self.metrics.buffer_seconds < self.max_buffer_seconds:
                next_segment_num = segment_num + len(self.buffer) + 1
                
                try:
                    segment = await self.download_segment(next_segment_num, self.current_quality)
                    self.buffer.append(segment)
                    self.metrics.buffer_seconds += segment.duration_seconds
                    
                    print(f"📥 Downloaded segment {next_segment_num} "
                          f"({self.current_quality.value}) | "
                          f"Buffer: {self.metrics.buffer_seconds:.1f}s")
                
                except Exception as e:
                    print(f"❌ Download failed: {e}")
                    break
            
            # Check for rebuffering
            if self.metrics.buffer_seconds < 0.5:
                print("⏸️  REBUFFERING! Waiting for buffer to fill...")
                self.metrics.rebuffer_count += 1
                await asyncio.sleep(2)
        
        print("\n✅ Playback complete!")
        print(f"\n📊 Final Metrics:")
        print(f"   Startup time: {self.metrics.startup_time_ms:.0f}ms")
        print(f"   Rebuffer count: {self.metrics.rebuffer_count}")
        print(f"   Final quality: {self.current_quality.value}")
        print(f"   Avg bandwidth: {self.metrics.current_bandwidth_mbps:.2f} Mbps")

# Example usage
async def demo_adaptive_playback():
    """Demonstrate adaptive bitrate playback"""
    
    player = AdaptiveBitratePlayer(
        video_id='video_abc123',
        cdn_url='https://cdn.streamverse.com'
    )
    
    await player.start_playback()

if __name__ == "__main__":
    asyncio.run(demo_adaptive_playback())
```

---

## 🎯 Capstone Project Deliverables

### Your Final Architecture Document Should Include:

1. **System Architecture Diagram** ✅
   - Global topology with all regions
   - Service dependencies
   - Data flow diagrams
   - Failure scenarios and recovery

2. **Capacity Planning** 📊
   - Storage requirements (100PB+)
   - Bandwidth calculations (50+ Tbps)
   - Database sizing (sharding strategy)
   - Cost projections ($10M+/month infrastructure)

3. **Performance Targets** ⚡
   - Video startup time: <1 second globally
   - API latency: <100ms P95
   - Uptime SLA: 99.99%
   - CDN cache hit rate: >95%

4. **Operational Runbook** 📖
   - Deployment procedures
   - Incident response playbooks
   - Scaling procedures
   - Disaster recovery plans

5. **Monitoring & Alerting** 🚨
   - SLIs (Service Level Indicators)
   - SLOs (Service Level Objectives)
   - Alert thresholds
   - Dashboard designs

---

## 🏆 Principal Architect Reflection

### Weeks 1-12 Integration Checklist

Review how each week contributed to StreamVerse:

- ✅ **Week 1-2 (Networks & Protocols)**: TCP for uploads, UDP for live streaming
- ✅ **Week 3 (HTTP Evolution)**: HTTP/3 + QUIC for fast video delivery
- ✅ **Week 4 (QUIC)**: 0-RTT reconnection for mobile users
- ✅ **Week 5 (Load Balancers)**: L4/L7 balancing for global traffic
- ✅ **Week 6 (CDN)**: 200 PoPs for sub-100ms latency worldwide
- ✅ **Week 7 (Caching)**: Multi-tier caching (edge, regional, origin)
- ✅ **Week 8 (Microservices)**: Independent services for scalability
- ✅ **Week 9 (Global DNS)**: GeoDNS routes users to nearest region
- ✅ **Week 10 (Anycast & Edge)**: Edge compute for authentication, A/B tests
- ✅ **Week 11 (Monitoring)**: RUM, synthetic, traces, logs, metrics
- ✅ **Week 12 (Integration)**: All concepts unified into cohesive system

---

## 🎓 Final Exam: Architecture Interview Questions

Test your mastery with these Principal Architect-level questions:

### Question 1: Viral Video Handling
*"A video suddenly goes viral, receiving 100 million views in 1 hour (10,000x normal traffic). Your CDN cache hit rate drops from 95% to 60%, causing origin servers to fail. What's your response plan?"*

<details>
<summary>Expected Answer</summary>

**Immediate Actions (0-15 minutes):**
1. Activate CDN pre-warming: Force-push video to all PoPs
2. Increase origin capacity: Auto-scale from 100 to 1,000 servers
3. Enable aggressive caching: TTL 1 hour → 24 hours for this video
4. Rate limiting: Implement per-IP limits to prevent abuse

**Medium-term (15-60 minutes):**
1. Enable multi-CDN: Activate backup CDN (Cloudflare + Akamai)
2. Optimize video: Serve lower quality as default, upgrade on request
3. Database read replicas: Add 50 replicas for metadata queries
4. Traffic shaping: Prioritize P2P delivery where possible

**Long-term Prevention:**
1. Predictive analytics: ML to detect potential viral content
2. Pre-warming: Automatically distribute trending content
3. Capacity buffers: Always maintain 10x headroom
4. Cost alerts: Monitor CDN bill in real-time
</details>

### Question 2: Global Failure Scenario
*"Your primary US-East region goes offline (AWS outage). 60% of your users are affected. Describe your failover strategy."*

<details>
<summary>Expected Answer</summary>

**Automatic Failover (0-60 seconds):**
1. DNS health checks detect US-East failure
2. GeoDNS automatically routes to US-West region
3. Load balancers redirect traffic to healthy regions
4. Users experience 200ms latency increase (acceptable)

**Data Consistency:**
1. User sessions: Stored in global Redis (multi-region)
2. Video metadata: MongoDB with cross-region replication
3. Watch history: Cassandra with eventual consistency
4. User uploads: S3 with cross-region replication (RPO: 15 minutes)

**Communication:**
1. Status page updated automatically
2. Customers notified via email/push notification
3. Social media announcement
4. Internal incident channel activated

**Recovery:**
1. US-East region comes back online after 4 hours
2. Gradual traffic shift back (10% every 10 minutes)
3. Data reconciliation for eventual consistency
4. Post-mortem within 48 hours
</details>

### Question 3: Cost Optimization
*"Your monthly infrastructure bill is $15M. Analyze and optimize while maintaining performance."*

<details>
<summary>Expected Answer</summary>

**Cost Breakdown:**
- CDN bandwidth: $6M (40%)
- Compute (transcoding, APIs): $4M (27%)
- Storage (S3, databases): $3M (20%)
- Data transfer: $1.5M (10%)
- Other (monitoring, logs): $0.5M (3%)

**Optimization Strategy:**

**CDN ($6M → $4M = $2M saved):**
- Negotiate volume discounts (multi-CDN bidding)
- Optimize cache hit rate: 95% → 98% (+3% = $600K saved)
- Implement P2P delivery for popular content ($400K saved)
- Smart routing: Route to cheaper PoPs when possible ($1M saved)

**Compute ($4M → $3M = $1M saved):**
- GPU spot instances for transcoding (50% discount = $500K saved)
- Right-size Kubernetes pods (30% over-provisioned = $300K saved)
- Auto-scaling optimization (shut down during low traffic = $200K saved)

**Storage ($3M → $2.2M = $800K saved):**
- Lifecycle policies: Move old content to Glacier ($400K saved)
- Deduplication: Remove duplicate user uploads ($200K saved)
- Compression: Use H.265 instead of H.264 (40% size = $200K saved)

**Total Savings: $3.8M/month (25% reduction)**
</details>

---

## 🎉 Congratulations, Principal Systems Architect!

You've completed the **12-week journey** from network packets to global-scale systems! 

### 🏅 What You've Mastered:

✅ **Foundation**: TCP, UDP, HTTP/1.1→HTTP/3, QUIC, load balancing
✅ **Intermediate**: CDNs, caching hierarchies, microservices, service mesh
✅ **Advanced**: GeoDNS, anycast, edge computing, CRDTs, distributed state
✅ **Expert**: Global monitoring, observability, performance optimization
✅ **Architect**: Complete system design, cost optimization, failure handling

### 📚 Recommended Next Steps:

1. **Build the Capstone**: Actually implement StreamVerse (start small!)
2. **Contribute to Open Source**: Contribute to NGINX, Envoy, Prometheus
3. **Read SRE Books**: "Site Reliability Engineering" by Google
4. **Study Real Systems**: Analyze Netflix, YouTube, Cloudflare architectures
5. **Interview Practice**: LeetCode System Design, Grokking the System Design Interview

---

## 🌟 Final Wisdom

*"The best architecture is the one that serves users invisibly, scales effortlessly, and costs reasonably. You now have the knowledge to build it."*

**Key Principles to Remember:**

1. **Simplicity**: Start simple, scale when needed
2. **Measure Everything**: You can't optimize what you don't measure
3. **Fail Gracefully**: Design for failure, not just success
4. **Cost-Conscious**: Every architectural decision has a price
5. **User-Centric**: Performance is a feature, not an afterthought

---

*Thank you for completing this journey! You're now equipped to design, build, and operate world-class distributed systems. Go build something amazing! 🚀*

---

**End of 12-Week Core System Infrastructure Curriculum**

*Created with ❤️ for aspiring Principal Systems Architects worldwide*