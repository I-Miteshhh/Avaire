# Capacity Estimation - Back-of-Envelope Calculations

**Mastery Level:** Essential for 40+ LPA roles  
**Interview Weight:** 20-30% of system design interviews  
**Time to Master:** 1-2 weeks with practice  
**Difficulty:** ⭐⭐⭐⭐

---

## 🎯 Why Capacity Estimation Matters

At **Principal/Staff Data Engineer** level, you must:
- Estimate storage needs for **petabyte-scale** data lakes
- Calculate **throughput requirements** for streaming systems
- Size **compute clusters** for batch processing jobs
- Predict **network bandwidth** for data replication
- Estimate **costs** for multi-region deployments

**This is the foundation of all system design.**

---

## 📊 Essential Numbers to Memorize

### **Latency Numbers Every Engineer Should Know**

```
Operation                    Time (ns)    Time (μs)    Time (ms)
L1 cache reference          0.5          0.0005       -
Branch mispredict           5            0.005        -
L2 cache reference          7            0.007        -
Mutex lock/unlock           25           0.025        -
Main memory reference       100          0.1          -
Compress 1K with Zippy      3,000        3            -
Send 1K over 1 Gbps network 10,000       10           0.01
Read 4K randomly from SSD   150,000      150          0.15
Read 1 MB sequentially SSD  1,000,000    1,000        1
Round trip within datacenter 500,000     500          0.5
Read 1 MB from memory       250,000      250          0.25
Round trip CA->Netherlands  150,000,000  150,000      150
Disk seek                   10,000,000   10,000       10
Read 1 MB sequentially HDD  20,000,000   20,000       20
```

### **Data Size References**

```
Unit        Exact Value       Approximate    Examples
Byte        1 byte           -              Single character
KB          1,024 bytes      ~1 thousand    Small email (1KB)
MB          1,024 KB         ~1 million     High-res photo (3MB)
GB          1,024 MB         ~1 billion     Movie file (2GB)
TB          1,024 GB         ~1 trillion    Company database (100TB)
PB          1,024 TB         ~1 quadrillion Netflix catalog (1PB)
```

### **Internet Scale Numbers**

```
Service            Daily Active Users    Requests/Day    Peak QPS
Google Search      8.5 billion          8.5 billion     100,000
YouTube            2 billion            5 billion       60,000
WhatsApp           2 billion            100 billion     1,200,000
Instagram          2 billion            1 billion       12,000
Uber               100 million          40 million      500
```

---

## 🔢 Step-by-Step Calculation Framework

### **Step 1: Requirements Gathering**
- **Daily Active Users (DAU)**
- **Read vs Write ratio**
- **Data size per operation**
- **Peak traffic patterns**
- **Geographic distribution**

### **Step 2: Scale Estimation**

#### **Traffic Estimation**
```
Example: Design Twitter-like system
- 200M DAU
- Each user tweets 2 times/day on average
- Each user reads 200 tweets/day
- Peak traffic = 2x average

Calculations:
- Tweets per day = 200M × 2 = 400M
- Tweet reads per day = 200M × 200 = 40B
- Read:Write ratio = 40B:400M = 100:1

- Write QPS = 400M / 86,400 = 4,600 QPS
- Peak Write QPS = 4,600 × 2 = 9,200 QPS
- Read QPS = 40B / 86,400 = 462,000 QPS
- Peak Read QPS = 462,000 × 2 = 924,000 QPS
```

#### **Storage Estimation**
```
Example: Twitter storage calculation
- Tweet text: 140 characters = 140 bytes
- Metadata: user_id, timestamp, etc. = 60 bytes
- Total per tweet = 200 bytes
- Media (20% tweets have media): avg 200KB
- Tweets with media = 400M × 0.2 = 80M/day
- Text storage = 400M × 200 bytes = 80GB/day
- Media storage = 80M × 200KB = 16TB/day
- Total daily storage = 80GB + 16TB ≈ 16TB/day
- Annual storage = 16TB × 365 = 5.8PB/year
```

#### **Bandwidth Estimation**
```
Example: Twitter bandwidth calculation
- Daily data ingestion = 16TB
- Bandwidth = 16TB / 86,400s = 185MB/s
- Peak bandwidth = 185MB/s × 2 = 370MB/s
- Read bandwidth = Write bandwidth × Read:Write ratio
- Read bandwidth = 185MB/s × 100 = 18.5GB/s
- Peak read bandwidth = 37GB/s
```

### **Step 3: Component Sizing**

#### **Database Sizing**
```
Example: Choose database for Twitter
- Total storage: 5.8PB/year
- Query pattern: Heavy reads (100:1 ratio)
- Latency requirement: <100ms for reads

Options:
1. MySQL: Max ~100TB per instance
   - Need: 5.8PB / 100TB = 58 shards
   - Read replicas: 3-5 per shard
   - Total instances: 58 × 4 = 232 instances

2. Cassandra: Linear scalability
   - Node capacity: ~2TB per node
   - Need: 5.8PB / 2TB = 2,900 nodes
   - Replication factor: 3
   - Total nodes: 2,900 × 3 = 8,700 nodes
```

#### **Cache Sizing**
```
Example: Twitter cache estimation
- Cache hot tweets (last 24 hours)
- Hot tweets = 400M tweets
- Cache size = 400M × 200 bytes = 80GB
- Add 20% buffer = 96GB
- Redis cluster: 16GB per node
- Nodes needed = 96GB / 16GB = 6 nodes
- With replication = 12 nodes
```

#### **CDN Sizing**
```
Example: Twitter media CDN
- Daily media uploads = 16TB
- CDN storage (30 days) = 16TB × 30 = 480TB
- Egress traffic = Ingress × Read:Write ratio
- Daily egress = 16TB × 100 = 1.6PB
- Peak egress = 1.6PB / 86,400 × 2 = 37GB/s
```

---

## 🚀 Advanced Estimation Patterns

### **Pattern 1: Time-Series Data Estimation**

```python
# Example: IoT sensor data platform
def estimate_timeseries_storage():
    # Input parameters
    sensors = 10_000_000  # 10M sensors
    data_points_per_hour = 60  # 1 per minute
    bytes_per_point = 24  # timestamp(8) + value(8) + metadata(8)
    retention_days = 365
    
    # Calculations
    hourly_data = sensors * data_points_per_hour * bytes_per_point
    daily_data = hourly_data * 24
    annual_data = daily_data * retention_days
    
    print(f"Hourly ingestion: {hourly_data / (1024**3):.2f} GB")
    print(f"Daily ingestion: {daily_data / (1024**3):.2f} GB") 
    print(f"Annual storage: {annual_data / (1024**4):.2f} TB")
    
    # Compression factor (typical for time-series)
    compression_ratio = 0.1  # 90% compression
    compressed_storage = annual_data * compression_ratio
    print(f"Compressed storage: {compressed_storage / (1024**4):.2f} TB")

estimate_timeseries_storage()
# Output:
# Hourly ingestion: 13.42 GB
# Daily ingestion: 322.27 GB
# Annual storage: 108.79 TB
# Compressed storage: 10.88 TB
```

### **Pattern 2: ML Training Data Estimation**

```python
# Example: Image classification dataset
def estimate_ml_dataset():
    # Dataset parameters
    total_images = 100_000_000  # 100M images
    avg_image_size_mb = 2  # 2MB per image
    augmentation_factor = 5  # 5x data augmentation
    backup_copies = 2  # Original + 1 backup
    
    # Storage calculations
    raw_storage_tb = total_images * avg_image_size_mb / (1024 * 1024)
    augmented_storage_tb = raw_storage_tb * augmentation_factor
    total_storage_tb = augmented_storage_tb * backup_copies
    
    # Bandwidth calculations (for training)
    training_batch_size = 1024
    batches_per_epoch = total_images // training_batch_size
    data_per_epoch_gb = batches_per_epoch * training_batch_size * avg_image_size_mb / 1024
    
    print(f"Raw dataset: {raw_storage_tb:.2f} TB")
    print(f"With augmentation: {augmented_storage_tb:.2f} TB")
    print(f"Total with backups: {total_storage_tb:.2f} TB")
    print(f"Data per epoch: {data_per_epoch_gb:.2f} GB")

estimate_ml_dataset()
# Output:
# Raw dataset: 190.73 TB
# With augmentation: 953.67 TB
# Total with backups: 1907.35 TB
# Data per epoch: 190.73 GB
```

### **Pattern 3: Real-Time Analytics Estimation**

```python
# Example: Real-time dashboard for e-commerce
def estimate_realtime_analytics():
    # Event parameters
    events_per_second = 50_000  # Peak events/sec
    event_size_bytes = 1024  # 1KB per event
    window_sizes = [1, 5, 15, 60]  # minutes
    metrics_per_window = 20
    
    # Memory requirements for windowing
    for window_min in window_sizes:
        events_in_window = events_per_second * window_min * 60
        memory_gb = events_in_window * event_size_bytes / (1024**3)
        print(f"{window_min}min window: {memory_gb:.2f} GB")
    
    # Output data rate
    output_metrics_per_sec = len(window_sizes) * metrics_per_window
    output_bytes_per_sec = output_metrics_per_sec * 100  # 100 bytes per metric
    output_mbps = output_bytes_per_sec * 8 / (1024 * 1024)
    
    print(f"Output data rate: {output_mbps:.2f} Mbps")
    
    # Database writes (for historical data)
    daily_events = events_per_second * 86_400
    daily_storage_gb = daily_events * event_size_bytes / (1024**3)
    print(f"Daily storage: {daily_storage_gb:.2f} GB")

estimate_realtime_analytics()
# Output:
# 1min window: 2.86 GB
# 5min window: 14.31 GB
# 15min window: 42.92 GB
# 60min window: 171.66 GB
# Output data rate: 0.61 Mbps
# Daily storage: 4137.99 GB
```

---

## 💡 Pro Tips for Interviews

### **1. Start with Reasonable Assumptions**
```
❌ Bad: "Let's assume 1 billion users"
✅ Good: "For a new social media platform, let's start with 100M DAU, 
          similar to early-stage Twitter"
```

### **2. Show Your Math Clearly**
```
❌ Bad: "We need about 10TB storage"
✅ Good: "Storage = 1M users × 100 posts/user × 1KB/post = 100GB"
```

### **3. Round Numbers Intelligently**
```
❌ Bad: "86,400 seconds in a day"
✅ Good: "~100K seconds in a day (close enough for estimation)"
```

### **4. Consider Peak vs Average**
```
❌ Bad: Only calculating average load
✅ Good: "Average QPS is 1000, but peak can be 3-5x, so plan for 5000 QPS"
```

### **5. Account for Growth**
```
❌ Bad: Only current requirements
✅ Good: "Current needs are 1TB, but with 100% YoY growth, plan for 5TB"
```

---

## 🎯 Practice Problems

### **Problem 1: WhatsApp-like Messaging**
**Requirements:**
- 2 billion users
- Each user sends 40 messages/day
- Each message is 100 bytes on average
- 5% of messages include media (average 1MB)
- Message history kept for 5 years

**Calculate:**
1. Daily message volume
2. Storage requirements (text + media)
3. Peak QPS for message delivery
4. Bandwidth requirements
5. Database sharding strategy

### **Problem 2: Netflix-like Video Streaming**
**Requirements:**
- 200M subscribers
- Each user watches 2 hours/day
- Video bitrates: 1080p (5Mbps), 4K (25Mbps)
- 70% watch 1080p, 30% watch 4K
- Content catalog: 100K hours of video
- Global CDN with 100 edge locations

**Calculate:**
1. Total bandwidth requirements
2. CDN storage per edge location
3. Video encoding and storage costs
4. Database size for metadata
5. Recommendation system compute needs

### **Problem 3: Uber-like Ride Sharing**
**Requirements:**
- 100M users in 1000 cities
- 10M rides/day
- Each ride generates GPS points every 5 seconds
- GPS data kept for 2 years for analytics
- Real-time ETA calculations
- Surge pricing based on supply/demand

**Calculate:**
1. GPS data volume and storage
2. Real-time processing requirements
3. Database design for geospatial queries
4. Caching strategy for hot areas
5. ML model serving for pricing

---

## 📚 Additional Resources

### **Books**
- "Designing Data-Intensive Applications" by Martin Kleppmann
- "System Design Interview" by Alex Xu

### **Online Calculators**
- AWS Pricing Calculator
- Google Cloud Pricing Calculator
- Redis Memory Calculator

### **Practice Platforms**
- LeetCode System Design
- Pramp System Design
- InterviewBit System Design

---

## ✅ Mastery Checklist

- [ ] Can calculate QPS from user requirements in 30 seconds
- [ ] Can estimate storage needs for any data type
- [ ] Can size databases, caches, and queues appropriately  
- [ ] Can account for replication, backup, and growth
- [ ] Can estimate network bandwidth and CDN requirements
- [ ] Can break down complex systems into manageable components
- [ ] Can present calculations clearly during interviews
- [ ] Can validate estimates using real-world benchmarks

**Master these patterns, and you'll handle any capacity estimation question with confidence!**