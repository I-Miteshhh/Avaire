# System Design - Complete Interview Prep for 40 LPA

**Target Role:** Staff/Principal Data Engineer (40+ LPA)  
**Study Time:** 4-6 weeks intensive preparation  
**Interview Weight:** 40-50% of total evaluation  
**Status:** Complete with 20 production-grade scenarios

---

## 🎯 Why System Design Matters

At **40 LPA+ level**, you're expected to:
- Design systems handling **billions of events/day**
- Make **architectural trade-offs** with deep understanding
- Scale systems from **1M to 1B users**
- Handle **fault tolerance, consistency, and availability**
- Optimize for **cost at petabyte scale**

**This module gets you there.**

---

## 📚 Module Structure

### **Part 1: Framework & Fundamentals**
- [System Design Framework](./00-Framework.md) - Step-by-step approach
- [Capacity Estimation](./01-Capacity-Estimation.md) - Back-of-envelope calculations
- [Scalability Patterns](./02-Scalability-Patterns.md) - Load balancing, caching, sharding
- [Database Selection](./03-Database-Selection.md) - SQL vs NoSQL vs NewSQL

### **Part 2: Core Components**
- [Caching Strategies](./04-Caching-Strategies.md) - Redis, Memcached, CDN
- [Message Queues](./05-Message-Queues.md) - Kafka, RabbitMQ, SQS
- [API Design](./06-API-Design.md) - REST, GraphQL, gRPC
- [Monitoring & Observability](./07-Monitoring.md) - Metrics, logs, traces

### **Part 3: Data-Intensive Systems (20 Scenarios)**

#### **Data Storage & Processing**
1. [Design YouTube Analytics Platform](./scenarios/01-YouTube-Analytics.md) ⭐⭐⭐⭐⭐
2. [Design Data Lake Architecture](./scenarios/02-Data-Lake.md) ⭐⭐⭐⭐⭐
3. [Design Real-Time Analytics Dashboard](./scenarios/03-Real-Time-Analytics.md) ⭐⭐⭐⭐
4. [Design ETL Pipeline at Scale](./scenarios/04-ETL-Pipeline.md) ⭐⭐⭐⭐

#### **Real-Time Processing**
5. [Design Uber Real-Time Pricing](./scenarios/05-Uber-Pricing.md) ⭐⭐⭐⭐⭐
6. [Design Fraud Detection System](./scenarios/06-Fraud-Detection.md) ⭐⭐⭐⭐⭐
7. [Design Real-Time Leaderboard](./scenarios/07-Leaderboard.md) ⭐⭐⭐⭐
8. [Design Stock Trading Platform](./scenarios/08-Stock-Trading.md) ⭐⭐⭐⭐⭐

#### **Recommendation & ML Systems**
9. [Design Netflix Recommendation System](./scenarios/09-Recommendation-System.md) ⭐⭐⭐⭐⭐
10. [Design Personalized News Feed](./scenarios/10-News-Feed.md) ⭐⭐⭐⭐
11. [Design Search Engine](./scenarios/11-Search-Engine.md) ⭐⭐⭐⭐⭐
12. [Design Ad Click Tracking](./scenarios/12-Ad-Tracking.md) ⭐⭐⭐⭐

#### **Infrastructure & Platform**
13. [Design Distributed Cache](./scenarios/13-Distributed-Cache.md) ⭐⭐⭐⭐⭐
14. [Design Rate Limiter](./scenarios/14-Rate-Limiter.md) ⭐⭐⭐⭐
15. [Design URL Shortener at Scale](./scenarios/15-URL-Shortener.md) ⭐⭐⭐⭐
16. [Design Notification System](./scenarios/16-Notification-System.md) ⭐⭐⭐⭐

#### **Monitoring & Logging**
17. [Design Distributed Logging System](./scenarios/17-Logging-System.md) ⭐⭐⭐⭐⭐
18. [Design Metrics & Monitoring Platform](./scenarios/18-Metrics-Platform.md) ⭐⭐⭐⭐
19. [Design Alerting System](./scenarios/19-Alerting-System.md) ⭐⭐⭐⭐
20. [Design Service Mesh Observability](./scenarios/20-Service-Mesh.md) ⭐⭐⭐⭐⭐

---

## 🎓 How to Use This Module

### **Week 1: Master the Framework**
**Days 1-2:** Study framework, capacity estimation, scalability patterns  
**Days 3-4:** Practice back-of-envelope calculations  
**Days 5-7:** Deep-dive into caching, messaging, API design

### **Week 2-3: Data Storage & Processing (Scenarios 1-4)**
**Focus:** YouTube Analytics, Data Lake, Real-Time Analytics, ETL  
**Practice:** Design on whiteboard, explain trade-offs  
**Goal:** Master data partitioning, batch vs streaming, OLAP vs OLTP

### **Week 4: Real-Time Systems (Scenarios 5-8)**
**Focus:** Uber Pricing, Fraud Detection, Leaderboard, Trading  
**Practice:** Handle low-latency requirements, consistency models  
**Goal:** Master streaming, event-driven architecture, time-series DB

### **Week 5: Recommendation & ML (Scenarios 9-12)**
**Focus:** Netflix Recommendations, News Feed, Search, Ad Tracking  
**Practice:** Feature engineering, model serving, A/B testing  
**Goal:** Master ML pipelines, collaborative filtering, indexing

### **Week 6: Infrastructure (Scenarios 13-20)**
**Focus:** Cache, Rate Limiter, URL Shortener, Logging, Monitoring  
**Practice:** Design reusable platform components  
**Goal:** Master distributed systems patterns, observability

---

## 📐 System Design Interview Framework

### **Step 1: Requirements Clarification (5 mins)**
```
Functional Requirements:
- What features? (read-heavy? write-heavy?)
- What's the user flow?
- What data needs to be stored?

Non-Functional Requirements:
- Scale: How many users? QPS? Data volume?
- Performance: Latency requirements? (p50, p99)
- Availability: 99.9%? 99.99%? 99.999%?
- Consistency: Strong? Eventual?
```

### **Step 2: Capacity Estimation (5 mins)**
```
Traffic:
- DAU (Daily Active Users)
- QPS (Queries Per Second) = DAU * actions/day / 86400
- Peak QPS = QPS * 2-3x

Storage:
- Data size per record
- Total storage = records * size * replication * growth
- Bandwidth = QPS * avg_response_size

Example: 100M users, 10 requests/day
- QPS = 100M * 10 / 86400 ≈ 11,574 QPS
- Peak QPS ≈ 35,000 QPS
```

### **Step 3: API Design (5 mins)**
```
RESTful APIs:
POST /api/v1/videos
GET /api/v1/videos/{id}
GET /api/v1/analytics/views?video_id={id}&start={ts}&end={ts}

GraphQL (for complex queries):
query {
  video(id: "123") {
    views(timeRange: LAST_7_DAYS) {
      timestamp
      count
    }
  }
}
```

### **Step 4: Database Schema (5 mins)**
```
SQL (OLTP):
- Strong consistency
- Complex queries
- ACID transactions

NoSQL (OLAP):
- Horizontal scalability
- High write throughput
- Eventual consistency

Time-Series DB:
- Time-based queries
- High ingestion rate
- Automatic downsampling
```

### **Step 5: High-Level Design (10 mins)**
```
Components:
┌─────────┐      ┌──────────────┐      ┌──────────┐
│ Clients │─────▶│ Load Balancer│─────▶│   API    │
└─────────┘      └──────────────┘      │ Servers  │
                                        └────┬─────┘
                                             │
                 ┌───────────────────────────┼──────────────┐
                 ▼                           ▼              ▼
           ┌─────────┐              ┌──────────────┐  ┌────────┐
           │  Cache  │              │   Database   │  │ Queue  │
           │ (Redis) │              │ (PostgreSQL) │  │(Kafka) │
           └─────────┘              └──────────────┘  └────────┘
```

### **Step 6: Detailed Design (15 mins)**
```
Deep-dive into:
1. Partitioning strategy
2. Caching strategy
3. Replication & consistency
4. Failure scenarios
5. Monitoring & alerting
```

### **Step 7: Trade-offs & Optimizations (10 mins)**
```
Discuss:
- CAP theorem implications
- Read vs Write optimization
- Consistency vs Availability
- Cost vs Performance
- Latency vs Throughput
```

---

## 🔍 Key Patterns to Master

### **1. Partitioning/Sharding**
```
Hash-based: hash(key) % N
- Pros: Even distribution
- Cons: Hard to add/remove nodes

Range-based: key ranges
- Pros: Good for range queries
- Cons: Hot partitions

Consistent Hashing:
- Pros: Minimal data movement
- Cons: Virtual nodes complexity
```

### **2. Caching Strategies**
```
Cache-Aside (Lazy Loading):
1. Check cache
2. If miss, read from DB
3. Update cache

Write-Through:
1. Write to cache
2. Write to DB synchronously
3. Cache always consistent

Write-Behind:
1. Write to cache
2. Async write to DB
3. Better performance, risk of data loss
```

### **3. Replication**
```
Primary-Replica:
- One primary (writes)
- Multiple replicas (reads)
- Asynchronous replication

Multi-Primary:
- Multiple primaries (writes)
- Conflict resolution needed
- Better availability

Quorum-based:
- W + R > N
- Tunable consistency
- Used in Cassandra, DynamoDB
```

### **4. Message Queue Patterns**
```
Point-to-Point:
- One consumer per message
- Work queue pattern

Pub-Sub:
- Multiple consumers
- Fan-out pattern

Stream Processing:
- Consumer groups
- Exactly-once semantics
- Kafka, Kinesis
```

---

## 📊 Scaling Cheat Sheet

### **Database Scaling**

| Scale | Strategy | Example |
|-------|----------|---------|
| 1K QPS | Single DB | PostgreSQL |
| 10K QPS | Read replicas | 1 Primary + 3 Replicas |
| 100K QPS | Sharding | Partition by user_id |
| 1M+ QPS | NoSQL + Caching | Cassandra + Redis |

### **Caching Layers**

| Layer | Technology | TTL | Hit Rate |
|-------|-----------|-----|----------|
| Browser | LocalStorage | Hours | 20% |
| CDN | CloudFront | Days | 60% |
| App Cache | Redis | Minutes | 80% |
| DB Query Cache | PostgreSQL | Seconds | 90% |

### **Storage Estimation**

```
Text (1 char) = 1 byte
Small string (100 chars) = 100 bytes
UUID = 16 bytes
Timestamp = 8 bytes
Integer = 4 bytes

1 KB = 1,000 bytes
1 MB = 1,000 KB
1 GB = 1,000 MB
1 TB = 1,000 GB
1 PB = 1,000 TB

1 million records * 1 KB = 1 GB
1 billion records * 1 KB = 1 TB
```

### **Latency Numbers**

```
L1 cache: 0.5 ns
L2 cache: 7 ns
Main memory: 100 ns
SSD: 16,000 ns (16 μs)
HDD: 2,000,000 ns (2 ms)
Network (same datacenter): 500,000 ns (0.5 ms)
Network (cross-region): 150,000,000 ns (150 ms)

Read 1 MB sequentially from memory: 250 μs
Read 1 MB sequentially from SSD: 1 ms
Read 1 MB sequentially from HDD: 20 ms
Send 1 MB over network: 10 ms
```

---

## 🏢 Company-Specific Focus

### **Google/YouTube (Scale & Efficiency)**
**Favorite Questions:**
- Design YouTube video processing pipeline
- Design Google Analytics
- Design Ads click aggregation

**Focus Areas:**
- Petabyte-scale storage
- MapReduce/Dataflow
- BigQuery optimization
- Colossus (distributed file system)

### **Amazon (Availability & Customer Obsession)**
**Favorite Questions:**
- Design Amazon product recommendation
- Design order fulfillment system
- Design inventory management

**Focus Areas:**
- DynamoDB patterns
- Event-driven architecture
- Microservices
- Availability over consistency

### **Meta/Facebook (Social Graph & Real-Time)**
**Favorite Questions:**
- Design Facebook News Feed
- Design Instagram Stories
- Design WhatsApp group messaging

**Focus Areas:**
- Graph databases
- Real-time updates
- TAO (distributed data store)
- Memcached at scale

### **Uber (Real-Time & Geo)**
**Favorite Questions:**
- Design ride matching
- Design real-time pricing
- Design driver location tracking

**Focus Areas:**
- Geospatial indexing
- Stream processing (Flink)
- Apache Hudi
- Low-latency requirements

### **Netflix (Data Pipelines & ML)**
**Favorite Questions:**
- Design recommendation system
- Design video encoding pipeline
- Design A/B testing platform

**Focus Areas:**
- Spark at scale
- Kafka streaming
- Feature store
- ML model serving

---

## 🎯 Interview Tips

### **Do's ✅**
1. **Clarify requirements FIRST** - Don't jump to solution
2. **Think out loud** - Explain your reasoning
3. **Draw diagrams** - Visual communication is key
4. **Discuss trade-offs** - "This approach gives X but sacrifices Y"
5. **Use real numbers** - "100M users, 1000 QPS"
6. **Ask for feedback** - "Does this approach make sense?"
7. **Mention monitoring** - Always discuss observability

### **Don'ts ❌**
1. **Don't over-engineer** - Start simple, then scale
2. **Don't ignore constraints** - Read-heavy vs write-heavy matters
3. **Don't forget edge cases** - What if cache fails? DB down?
4. **Don't use buzzwords without understanding** - Know what "eventual consistency" means
5. **Don't design in isolation** - Consider the entire ecosystem
6. **Don't forget about data** - Schema design is crucial
7. **Don't skip capacity estimation** - Shows you understand scale

### **Red Flags 🚩**
- Single point of failure (no redundancy)
- No consideration for monitoring
- Ignoring latency requirements
- No discussion of failure scenarios
- Over-complicating simple problems
- Not asking clarifying questions
- Vague hand-waving without specifics

---

## 📖 Study Plan

### **Beginner (Weeks 1-2)**
- Master the framework
- Complete scenarios 13-16 (simpler infrastructure)
- Focus on fundamentals: caching, load balancing, databases

### **Intermediate (Weeks 3-4)**
- Deep-dive into data systems (scenarios 1-4)
- Real-time processing (scenarios 5-8)
- Practice whiteboard design

### **Advanced (Weeks 5-6)**
- ML systems (scenarios 9-12)
- Complex monitoring (scenarios 17-20)
- Mock interviews with peers
- Company-specific preparation

---

## 🚀 Next Steps

1. **Read Framework** → [00-Framework.md](./00-Framework.md)
2. **Practice Calculations** → [01-Capacity-Estimation.md](./01-Capacity-Estimation.md)
3. **Start with Easy Scenario** → [15-URL-Shortener.md](./scenarios/15-URL-Shortener.md)
4. **Build to Complex** → [01-YouTube-Analytics.md](./scenarios/01-YouTube-Analytics.md)

**Remember:** System design is about **communication** and **trade-offs**, not perfect solutions!

Good luck! 🎉
