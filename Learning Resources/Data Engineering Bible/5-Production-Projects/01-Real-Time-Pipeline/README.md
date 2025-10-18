# Real-Time Analytics Pipeline

**Target Role:** Principal Data Engineer / Staff Engineer (40+ LPA)  
**Complexity:** Production-Grade Full Stack  
**Implementation:** Kafka + Flink + Iceberg  
**Deployment:** Docker + Kubernetes  

---

## 📚 Project Overview

This is a **production-ready** real-time analytics pipeline that processes clickstream events from a million-user e-commerce platform.

**Architecture:**
```
Web/Mobile Apps → Kafka → Flink Processing → Iceberg Data Lake → Query Engines
                                ↓
                            Redis Cache
                                ↓
                          Monitoring Stack
                       (Prometheus + Grafana)
```

**What You'll Build:**
- Event ingestion with Kafka (1M events/sec)
- Real-time processing with Flink (sessionization, aggregations)
- Data lake with Iceberg (ACID transactions, time travel)
- Caching layer with Redis
- Complete monitoring and alerting
- Kubernetes deployment with auto-scaling

**Real-World Use Cases:**
- **Netflix:** Real-time viewing metrics for recommendations
- **Uber:** Real-time trip analytics and pricing
- **Airbnb:** Search analytics and pricing optimization
- **LinkedIn:** Feed engagement metrics

---

## Table of Contents

1. [Architecture](#architecture)
2. [Prerequisites](#prerequisites)
3. [Project Structure](#project-structure)
4. [Implementation](#implementation)
   - [Kafka Setup](#1-kafka-setup)
   - [Flink Jobs](#2-flink-jobs)
   - [Iceberg Data Lake](#3-iceberg-data-lake)
   - [Redis Caching](#4-redis-caching)
   - [Monitoring](#5-monitoring)
5. [Deployment](#deployment)
6. [Operations Guide](#operations-guide)
7. [Performance Tuning](#performance-tuning)
8. [Troubleshooting](#troubleshooting)

---

## Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                        Data Producers                        │
│  (Web Apps, Mobile Apps, IoT Devices, Microservices)       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      Kafka Cluster                          │
│  Topic: clickstream_events (partitions: 30)                 │
│  Replication Factor: 3                                       │
│  Retention: 7 days                                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Flink Processing                          │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │  Sessionization  │  │  Aggregations    │               │
│  │  Job             │  │  Job             │               │
│  └──────────────────┘  └──────────────────┘               │
│                                                              │
│  Features:                                                   │
│  - Session windows (30min inactivity)                       │
│  - Tumbling windows (1min, 5min, 1hr)                      │
│  - Exactly-once semantics                                   │
│  - Late data handling (5min)                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ├───────────────┐
                     ▼               ▼
┌───────────────────────────┐  ┌──────────────┐
│   Iceberg Data Lake       │  │    Redis     │
│                           │  │    Cache     │
│  Tables:                  │  │              │
│  - events_raw             │  │  Hot data:   │
│  - sessions               │  │  - Last 1hr  │
│  - metrics_1min           │  │  - Top URLs  │
│  - metrics_hourly         │  │  - Active    │
│                           │  │    users     │
│  Features:                │  └──────────────┘
│  - ACID transactions      │
│  - Time travel queries    │
│  - Schema evolution       │
│  - Partition pruning      │
└───────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                     Query Engines                            │
│  - Trino (ad-hoc queries)                                   │
│  - Presto (dashboards)                                       │
│  - Spark (batch jobs)                                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   Monitoring Stack                           │
│  - Prometheus (metrics)                                      │
│  - Grafana (visualization)                                   │
│  - Elasticsearch (logs)                                      │
│  - Jaeger (traces)                                           │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

**Event Schema:**
```json
{
  "event_id": "uuid",
  "timestamp": "2024-01-15T10:30:00Z",
  "user_id": "user123",
  "session_id": "session456",
  "event_type": "page_view",
  "page_url": "/products/12345",
  "referrer": "https://google.com",
  "user_agent": "Mozilla/5.0...",
  "ip_address": "192.168.1.1",
  "geo": {
    "country": "US",
    "city": "San Francisco"
  },
  "device": {
    "type": "mobile",
    "os": "iOS"
  },
  "metadata": {
    "product_id": "12345",
    "category": "electronics"
  }
}
```

**Processing Steps:**

1. **Ingestion (Kafka)**
   - Events arrive at 1M/sec
   - Partitioned by user_id (for ordering)
   - Compressed with LZ4

2. **Stream Processing (Flink)**
   - Sessionization: Group events by user with 30min timeout
   - Aggregations: Count events per URL, category, device
   - Enrichment: Add geo data, device classification
   - Late data: Accept events up to 5min late

3. **Storage (Iceberg)**
   - Raw events: Partitioned by date, hour
   - Sessions: Partitioned by date
   - Metrics: Partitioned by time window

4. **Caching (Redis)**
   - Last 1hr metrics for dashboards
   - Top 100 URLs with visit counts
   - Active user count (HyperLogLog)

---

## Prerequisites

**Required Skills:**
- Java 11+ (Flink jobs)
- Scala (optional for Flink)
- SQL (Iceberg queries)
- Docker & Kubernetes
- Linux command line

**Tools to Install:**
- Docker Desktop (20.10+)
- kubectl (1.24+)
- Helm (3.0+)
- Maven (3.6+)
- Git

**Cloud Resources (if deploying to cloud):**
- AWS EKS / GCP GKE / Azure AKS
- S3 / GCS / ADLS (for Iceberg storage)
- 3x c5.2xlarge (Kafka brokers)
- 3x c5.4xlarge (Flink task managers)
- 1x r5.xlarge (Redis)

**Estimated Costs:**
- Development (local): $0
- Staging (cloud): ~$500/month
- Production (cloud): ~$5,000/month

---

## Project Structure

```
01-Real-Time-Pipeline/
│
├── README.md                          # This file
│
├── docker/                            # Docker configurations
│   ├── docker-compose.yml             # Local dev environment
│   ├── kafka/
│   │   └── Dockerfile
│   ├── flink/
│   │   └── Dockerfile
│   └── monitoring/
│       ├── prometheus.yml
│       └── grafana-dashboards/
│
├── k8s/                               # Kubernetes manifests
│   ├── namespace.yaml
│   ├── kafka/
│   │   ├── kafka-cluster.yaml
│   │   └── topics.yaml
│   ├── flink/
│   │   ├── flink-configuration.yaml
│   │   ├── sessionization-job.yaml
│   │   └── aggregations-job.yaml
│   ├── iceberg/
│   │   └── catalog-config.yaml
│   ├── redis/
│   │   └── redis-cluster.yaml
│   └── monitoring/
│       ├── prometheus.yaml
│       ├── grafana.yaml
│       └── alertmanager.yaml
│
├── flink-jobs/                        # Flink streaming jobs
│   ├── pom.xml
│   ├── src/main/java/com/dateng/
│   │   ├── SessionizationJob.java
│   │   ├── AggregationsJob.java
│   │   ├── schema/
│   │   │   ├── ClickstreamEvent.java
│   │   │   └── Session.java
│   │   ├── functions/
│   │   │   ├── SessionAssigner.java
│   │   │   ├── EventAggregator.java
│   │   │   └── GeoEnrichment.java
│   │   └── sinks/
│   │       ├── IcebergSink.java
│   │       └── RedisSink.java
│   └── src/test/java/
│
├── data-generator/                    # Test data generator
│   ├── pom.xml
│   └── src/main/java/
│       └── ClickstreamGenerator.java
│
├── sql/                               # Iceberg DDL & queries
│   ├── create_tables.sql
│   └── sample_queries.sql
│
├── scripts/                           # Helper scripts
│   ├── setup-local.sh
│   ├── deploy-k8s.sh
│   ├── kafka-topics-create.sh
│   └── monitoring-setup.sh
│
└── docs/                              # Additional documentation
    ├── OPERATIONS.md
    ├── PERFORMANCE_TUNING.md
    └── TROUBLESHOOTING.md
```

---

## Implementation

Next sections will cover:
1. Kafka cluster setup with optimal configurations
2. Flink jobs with exactly-once semantics
3. Iceberg table setup with time travel
4. Redis caching patterns
5. Complete monitoring stack

**File Organization:**
- Part 1: Kafka + Data Producer (01-kafka-setup.md)
- Part 2: Flink Sessionization Job (02-flink-sessionization.md)
- Part 3: Flink Aggregations Job (03-flink-aggregations.md)
- Part 4: Iceberg Data Lake (04-iceberg-setup.md)
- Part 5: Redis Caching (05-redis-caching.md)
- Part 6: Monitoring Stack (06-monitoring.md)
- Part 7: Kubernetes Deployment (07-k8s-deployment.md)
- Part 8: Operations Guide (08-operations.md)

---

## Quick Start

### Local Development (Docker Compose)

```bash
# 1. Clone the repository
git clone https://github.com/your-org/realtime-pipeline.git
cd realtime-pipeline

# 2. Start infrastructure
docker-compose up -d

# 3. Create Kafka topics
./scripts/kafka-topics-create.sh

# 4. Build Flink jobs
cd flink-jobs
mvn clean package

# 5. Submit Flink jobs
./scripts/submit-flink-jobs.sh

# 6. Start data generator
cd data-generator
mvn exec:java -Dexec.mainClass="com.dateng.ClickstreamGenerator"

# 7. View Flink UI
open http://localhost:8081

# 8. View Grafana dashboards
open http://localhost:3000
```

### Production Deployment (Kubernetes)

```bash
# 1. Setup Kubernetes cluster
eksctl create cluster -f k8s/cluster-config.yaml

# 2. Install Kafka with Strimzi operator
kubectl apply -f k8s/kafka/

# 3. Deploy Flink jobs
kubectl apply -f k8s/flink/

# 4. Deploy monitoring stack
kubectl apply -f k8s/monitoring/

# 5. Verify deployments
kubectl get pods -n realtime-pipeline
```

---

## Performance Targets

**Throughput:**
- Kafka ingestion: 1M events/sec
- Flink processing: 1M events/sec
- Iceberg writes: 100K events/sec

**Latency:**
- End-to-end (p99): < 5 seconds
- Sessionization: < 10 seconds
- Aggregations: < 1 second

**Reliability:**
- Uptime: 99.9% (43 min downtime/month)
- Data loss: Zero (exactly-once semantics)
- Recovery time: < 5 minutes

**Scalability:**
- Horizontal: 10x traffic without architecture change
- Vertical: Support 10M concurrent users

---

## Next Steps

Proceed to Part 1 for detailed Kafka setup:
- [01-kafka-setup.md](./01-kafka-setup.md)

---

**End of README**
