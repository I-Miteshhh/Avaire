# Search & Indexing Systems

**Purpose:** Master Elasticsearch architecture and search optimization for 40+ LPA Principal Engineer roles

**Prerequisites:** Inverted index fundamentals, distributed systems, relevance ranking (BM25)

---

## Table of Contents

1. [Elasticsearch Architecture](#1-elasticsearch-architecture)
2. [Index Lifecycle Management](#2-index-lifecycle-management)
3. [Sharding Strategies](#3-sharding-strategies)
4. [Relevance Tuning](#4-relevance-tuning)
5. [Performance Optimization](#5-performance-optimization)
6. [Production Patterns](#6-production-patterns)

---

## 1. Elasticsearch Architecture

### 1.1 Cluster Components

```
┌─────────────────────────────────────────────────────┐
│                 Elasticsearch Cluster                │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ Master Node  │  │ Master Node  │  │Master Node│ │
│  │              │  │              │  │           │ │
│  │ - Cluster    │  │ - Metadata   │  │- Elections│ │
│  │   state      │  │   management │  │           │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │  Data Node   │  │  Data Node   │  │ Data Node │ │
│  │              │  │              │  │           │ │
│  │ - Shards     │  │ - Shards     │  │- Shards   │ │
│  │ - Indexing   │  │ - Indexing   │  │- Indexing │ │
│  │ - Search     │  │ - Search     │  │- Search   │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐                │
│  │Ingest Node   │  │Ingest Node   │                │
│  │              │  │              │                │
│  │ - Pipelines  │  │ - Pipelines  │                │
│  │ - Transform  │  │ - Transform  │                │
│  └──────────────┘  └──────────────┘                │
│                                                      │
│  ┌──────────────┐                                   │
│  │Coordinating  │                                   │
│  │    Node      │                                   │
│  │ - Route      │                                   │
│  │ - Aggregate  │                                   │
│  └──────────────┘                                   │
└─────────────────────────────────────────────────────┘
```

**Node Roles:**
- **Master:** Cluster management, index creation, shard allocation
- **Data:** Store data, execute queries
- **Ingest:** Pre-process documents before indexing
- **Coordinating:** Route requests, merge results

---

### 1.2 Index Structure

```
Index: products
  ├── Shard 0 (Primary)
  │   ├── Replica 0-1
  │   └── Replica 0-2
  ├── Shard 1 (Primary)
  │   ├── Replica 1-1
  │   └── Replica 1-2
  └── Shard 2 (Primary)
      ├── Replica 2-1
      └── Replica 2-2

Each Shard contains:
  ├── Lucene Segments
  │   ├── Segment 1 (immutable)
  │   ├── Segment 2 (immutable)
  │   └── Segment 3 (immutable)
  ├── Inverted Index
  ├── Doc Values (column-oriented)
  └── Field Data Cache
```

---

### 1.3 Document Indexing Flow

```
Client
  │
  ▼
POST /products/_doc/123
{
  "name": "iPhone 15",
  "price": 999,
  "category": "Electronics"
}
  │
  ▼
Coordinating Node
  │
  ├─ Calculate routing: hash(doc_id) % num_primary_shards
  │  → Shard 1
  │
  ▼
Primary Shard (Node 2)
  │
  ├─ Index document
  ├─ Add to translog (write-ahead log)
  ├─ Buffer in memory
  │
  ▼
Replicate to Replicas
  │
  ├─> Replica 1-1 (Node 3)
  └─> Replica 1-2 (Node 4)
  │
  ▼
Response to Client
```

---

### 1.4 Search Flow

```
Client: GET /products/_search?q=iphone

Coordinating Node
  │
  ├─ Scatter phase (parallel)
  │  ├─> Shard 0 (or replica)
  │  ├─> Shard 1 (or replica)
  │  └─> Shard 2 (or replica)
  │
  │  Each shard returns:
  │  - Top 10 doc IDs
  │  - Scores
  │
  ▼
Gather phase
  │
  ├─ Merge results from all shards
  ├─ Sort by score (descending)
  ├─ Select global top 10
  │
  ▼
Fetch phase
  │
  ├─ Fetch full documents for top 10
  │  (may be on different shards)
  │
  ▼
Return to Client
```

---

## 2. Index Lifecycle Management

### 2.1 ILM Phases

```
Hot Phase (0-7 days)
  - Active indexing
  - SSD storage
  - 2 replicas
  - High RAM allocation

Warm Phase (7-30 days)
  - Read-only
  - SSD storage
  - 1 replica
  - Force merge to 1 segment

Cold Phase (30-90 days)
  - Searchable snapshots
  - HDD or object storage
  - 0 replicas
  - Minimal RAM

Delete Phase (>90 days)
  - Delete index
```

---

### 2.2 ILM Policy

```json
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_size": "50gb",
            "max_age": "7d",
            "max_docs": 10000000
          },
          "set_priority": {
            "priority": 100
          }
        }
      },
      "warm": {
        "min_age": "7d",
        "actions": {
          "readonly": {},
          "forcemerge": {
            "max_num_segments": 1
          },
          "shrink": {
            "number_of_shards": 1
          },
          "allocate": {
            "number_of_replicas": 1,
            "require": {
              "box_type": "warm"
            }
          },
          "set_priority": {
            "priority": 50
          }
        }
      },
      "cold": {
        "min_age": "30d",
        "actions": {
          "searchable_snapshot": {
            "snapshot_repository": "cold-snapshots"
          },
          "allocate": {
            "number_of_replicas": 0
          },
          "set_priority": {
            "priority": 0
          }
        }
      },
      "delete": {
        "min_age": "90d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
```

**Apply Policy:**
```bash
PUT _ilm/policy/logs-policy
{
  # policy JSON above
}

# Create index template with policy
PUT _index_template/logs-template
{
  "index_patterns": ["logs-*"],
  "template": {
    "settings": {
      "index.lifecycle.name": "logs-policy",
      "index.lifecycle.rollover_alias": "logs"
    }
  }
}
```

---

### 2.3 Rollover

**Purpose:** Create new index when current index reaches threshold

```bash
# Create initial index
PUT logs-000001
{
  "aliases": {
    "logs": {
      "is_write_index": true
    }
  }
}

# Rollover manually
POST logs/_rollover
{
  "conditions": {
    "max_age": "7d",
    "max_docs": 10000000,
    "max_size": "50gb"
  }
}

# Result:
# logs-000001 → read-only
# logs-000002 → new write index
```

---

## 3. Sharding Strategies

### 3.1 Shard Sizing

**Guidelines:**
```
Shard size: 10-50 GB optimal
Max shard size: 50 GB
Max shards per node: 1000

Example:
  Total data: 500 GB
  Target shard size: 25 GB
  Number of shards: 500 / 25 = 20 shards
```

**Calculation:**
```python
def calculate_shards(total_data_gb, target_shard_gb=25):
    """
    Calculate optimal number of shards
    """
    num_shards = math.ceil(total_data_gb / target_shard_gb)
    
    # Round to power of 2 for even distribution
    return 2 ** math.ceil(math.log2(num_shards))

# Examples:
calculate_shards(100)   # → 8 shards (12.5 GB each)
calculate_shards(500)   # → 32 shards (15.6 GB each)
calculate_shards(2000)  # → 128 shards (15.6 GB each)
```

---

### 3.2 Routing

**Default Routing:**
```
shard_num = hash(document_id) % num_primary_shards
```

**Custom Routing:**
```json
// Index with custom routing
PUT /products/_doc/123?routing=user_456
{
  "user_id": 456,
  "product": "iPhone"
}

// Search with routing (faster - single shard)
GET /products/_search?routing=user_456
{
  "query": {
    "term": {
      "user_id": 456
    }
  }
}
```

**Benefits:**
- Query only relevant shard (avoid scatter-gather)
- Co-locate related documents (faster joins)

**Drawback:**
- Uneven shard distribution if routing key is skewed

---

### 3.3 Split/Shrink APIs

**Split Index (increase shards):**
```bash
# Original: 5 shards
POST /my-index/_split/my-index-split
{
  "settings": {
    "index.number_of_shards": 10
  }
}

# Result: 10 shards (must be multiple of 5)
```

**Shrink Index (decrease shards):**
```bash
# Original: 10 shards
POST /my-index/_shrink/my-index-shrink
{
  "settings": {
    "index.number_of_shards": 1,
    "index.number_of_replicas": 1
  }
}

# Result: 1 shard (must be factor of 10)
```

---

## 4. Relevance Tuning

### 4.1 Scoring Algorithms

**BM25 (Default):**
```
score(q,d) = Σ IDF(qi) × (f(qi,d) × (k1 + 1)) / 
                        (f(qi,d) + k1 × (1 - b + b × |d| / avgdl))

Where:
  qi = query term i
  f(qi,d) = term frequency in document d
  |d| = document length
  avgdl = average document length
  k1 = 1.2 (term saturation)
  b = 0.75 (length normalization)
```

**Customize BM25:**
```json
PUT /products
{
  "settings": {
    "index": {
      "similarity": {
        "my_bm25": {
          "type": "BM25",
          "k1": 1.5,
          "b": 0.9
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "similarity": "my_bm25"
      }
    }
  }
}
```

---

### 4.2 Boosting

**Field-Level Boosting:**
```json
GET /products/_search
{
  "query": {
    "multi_match": {
      "query": "iphone",
      "fields": [
        "title^3",      // 3x weight
        "description^1",
        "tags^2"
      ]
    }
  }
}
```

**Document-Level Boosting:**
```json
// Index with boost
PUT /products/_doc/123
{
  "title": "iPhone 15",
  "popularity": 1000
}

// Use function score
GET /products/_search
{
  "query": {
    "function_score": {
      "query": {
        "match": {
          "title": "iphone"
        }
      },
      "functions": [
        {
          "field_value_factor": {
            "field": "popularity",
            "factor": 0.001,
            "modifier": "log1p"
          }
        }
      ],
      "boost_mode": "multiply"
    }
  }
}
```

---

### 4.3 Decay Functions

**Purpose:** Boost recent documents, penalize old ones

```json
GET /products/_search
{
  "query": {
    "function_score": {
      "query": {
        "match": {
          "title": "iphone"
        }
      },
      "functions": [
        {
          "gauss": {
            "created_at": {
              "origin": "now",
              "scale": "30d",
              "offset": "7d",
              "decay": 0.5
            }
          }
        }
      ]
    }
  }
}
```

**Decay Curve:**
```
Score
  │
1.0│ ████████╗
   │         ║
0.5│         ╚════╗
   │              ║
0.0│              ╚════════════>
   └─────────────────────────── Time
   Now   7d   30d          60d
      (offset)(scale)
```

---

### 4.4 Rescoring

**Approach:** Cheap query first, expensive rerank for top N

```json
GET /products/_search
{
  "query": {
    "match": {
      "title": "iphone"
    }
  },
  "rescore": {
    "window_size": 50,
    "query": {
      "rescore_query": {
        "function_score": {
          "script_score": {
            "script": {
              "source": """
                double titleScore = _score;
                double popularityScore = Math.log(1 + doc['popularity'].value);
                double recencyScore = 1.0 / (1 + (System.currentTimeMillis() - doc['created_at'].value.millis) / 86400000.0);
                return titleScore * popularityScore * recencyScore;
              """
            }
          }
        }
      },
      "query_weight": 0.7,
      "rescore_query_weight": 1.3
    }
  }
}
```

**Process:**
1. Initial query returns top 1000 docs
2. Rescore top 50 with expensive function
3. Return final top 10

---

## 5. Performance Optimization

### 5.1 Mapping Optimization

**Use Appropriate Field Types:**
```json
PUT /products
{
  "mappings": {
    "properties": {
      "id": {
        "type": "keyword"           // Exact match
      },
      "title": {
        "type": "text",             // Full-text search
        "fields": {
          "keyword": {
            "type": "keyword"       // Aggregations
          }
        }
      },
      "price": {
        "type": "scaled_float",     // Efficient numbers
        "scaling_factor": 100
      },
      "created_at": {
        "type": "date",
        "format": "epoch_millis"
      },
      "tags": {
        "type": "keyword"           // Array of exact values
      },
      "description": {
        "type": "text",
        "index": false              // Don't index (only store)
      },
      "popularity": {
        "type": "integer",
        "doc_values": true,         // Enable for aggregations
        "index": false              // Don't need to query
      }
    }
  }
}
```

---

### 5.2 Query Optimization

**Use Filters (Cached):**
```json
// Slow (scored)
GET /products/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "title": "iphone" } },
        { "term": { "category": "electronics" } }
      ]
    }
  }
}

// Fast (filter cached)
GET /products/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "title": "iphone" } }
      ],
      "filter": [
        { "term": { "category": "electronics" } }
      ]
    }
  }
}
```

**Cache Behavior:**
- Filters are cached (no scoring)
- Must clauses are scored (not cached)
- Use filters for: terms, ranges, exists

---

### 5.3 Aggregation Optimization

**Use Doc Values:**
```json
PUT /products
{
  "mappings": {
    "properties": {
      "brand": {
        "type": "keyword",
        "doc_values": true      // Enable (default for keyword)
      }
    }
  }
}

// Efficient aggregation
GET /products/_search
{
  "size": 0,
  "aggs": {
    "brands": {
      "terms": {
        "field": "brand",
        "size": 10
      }
    }
  }
}
```

**Doc Values vs Field Data:**
- **Doc Values:** Column-oriented, disk-based, efficient
- **Field Data:** Row-oriented, heap-based, slow (avoid)

---

### 5.4 Indexing Performance

**Bulk Indexing:**
```json
POST /_bulk
{ "index": { "_index": "products", "_id": "1" } }
{ "title": "iPhone 15", "price": 999 }
{ "index": { "_index": "products", "_id": "2" } }
{ "title": "Samsung Galaxy", "price": 899 }

// Optimal bulk size: 5-15 MB
```

**Tuning for Indexing:**
```json
PUT /products/_settings
{
  "index": {
    "refresh_interval": "30s",          // Default: 1s
    "number_of_replicas": 0,            // Disable during bulk
    "translog.durability": "async",     // Fast (less safe)
    "translog.sync_interval": "30s"
  }
}

// After bulk indexing, restore:
PUT /products/_settings
{
  "index": {
    "refresh_interval": "1s",
    "number_of_replicas": 1,
    "translog.durability": "request"
  }
}
```

---

### 5.5 Force Merge

**Purpose:** Merge segments to improve search speed

```bash
# Force merge to 1 segment (after bulk indexing)
POST /products/_forcemerge?max_num_segments=1

# Only for read-only indices (e.g., warm/cold phase)
```

**Benefits:**
- Faster search (fewer segments to scan)
- Better compression
- Lower disk usage

**Drawbacks:**
- CPU/IO intensive
- Locks shard during merge
- Only useful for static indices

---

## 6. Production Patterns

### 6.1 Hot-Warm Architecture

```
┌─────────────────────────────────────────────────────┐
│                     Load Balancer                    │
└────────────┬────────────────────────────────────────┘
             │
      ┌──────┴──────┐
      │             │
      ▼             ▼
┌───────────┐ ┌───────────┐
│Hot Tier   │ │Warm Tier  │
│           │ │           │
│- SSD      │ │- SSD/HDD  │
│- 64GB RAM │ │- 32GB RAM │
│- 16 CPU   │ │- 8 CPU    │
│           │ │           │
│Active     │ │Read-only  │
│indexing   │ │(7-30 days)│
│(0-7 days) │ │           │
└───────────┘ └───────────┘
```

**Configuration:**
```bash
# Tag nodes
bin/elasticsearch -E node.attr.box_type=hot
bin/elasticsearch -E node.attr.box_type=warm

# Allocate hot indices to hot nodes
PUT /logs-2024-01-01/_settings
{
  "index.routing.allocation.require.box_type": "hot"
}

# Move to warm tier
PUT /logs-2023-12-01/_settings
{
  "index.routing.allocation.require.box_type": "warm"
}
```

---

### 6.2 Cross-Cluster Replication

**Purpose:** Disaster recovery, multi-region

```
Primary Cluster (US-East)
  │
  ├─ products (leader index)
  │
  ▼
Replicate
  │
  ▼
Secondary Cluster (US-West)
  │
  └─ products (follower index)
```

**Setup:**
```bash
# On secondary cluster
PUT /_cluster/settings
{
  "persistent": {
    "cluster.remote.us-east.seeds": [
      "10.0.0.1:9300",
      "10.0.0.2:9300"
    ]
  }
}

# Create follower index
PUT /products/_ccr/follow
{
  "remote_cluster": "us-east",
  "leader_index": "products"
}
```

**Use Cases:**
- Disaster recovery (automatic failover)
- Read scaling (distribute reads)
- Compliance (data residency)

---

### 6.3 Snapshot & Restore

**Repository:**
```bash
# Create S3 repository
PUT /_snapshot/my-snapshots
{
  "type": "s3",
  "settings": {
    "bucket": "my-elasticsearch-backups",
    "region": "us-east-1",
    "base_path": "snapshots"
  }
}

# Create snapshot
PUT /_snapshot/my-snapshots/snapshot-2024-01-01
{
  "indices": "products,users",
  "ignore_unavailable": true,
  "include_global_state": false
}

# Restore snapshot
POST /_snapshot/my-snapshots/snapshot-2024-01-01/_restore
{
  "indices": "products",
  "ignore_unavailable": true
}
```

**Automated Snapshots:**
```bash
# Create SLM policy
PUT /_slm/policy/daily-snapshots
{
  "schedule": "0 30 1 * * ?",
  "name": "<daily-snap-{now/d}>",
  "repository": "my-snapshots",
  "config": {
    "indices": ["*"],
    "ignore_unavailable": true,
    "include_global_state": false
  },
  "retention": {
    "expire_after": "30d",
    "min_count": 7,
    "max_count": 30
  }
}
```

---

### 6.4 Monitoring

**Key Metrics:**
```bash
# Cluster health
GET /_cluster/health

# Node stats
GET /_nodes/stats

# Index stats
GET /products/_stats
```

**Critical Metrics:**
```
1. Cluster Health (green/yellow/red)
2. JVM Heap Usage (<75%)
3. Search Latency (P99 <100ms)
4. Indexing Rate (docs/sec)
5. Query Rate (queries/sec)
6. Rejected Threads (should be 0)
7. Disk Usage (<80%)
8. CPU Usage (<70%)
```

**Prometheus Exporter:**
```yaml
# docker-compose.yml
services:
  elasticsearch-exporter:
    image: quay.io/prometheuscommunity/elasticsearch-exporter:latest
    command:
      - '--es.uri=http://elasticsearch:9200'
    ports:
      - "9114:9114"
```

---

### 6.5 Capacity Planning

**Formula:**
```
Required Storage = (Daily Ingest × Retention Days) × Replication Factor × Overhead

Example:
  Daily ingest: 100 GB
  Retention: 90 days
  Replication: 2x (1 primary + 1 replica)
  Overhead: 1.2x (indexing, OS)
  
  Storage = 100 × 90 × 2 × 1.2 = 21.6 TB
```

**Node Count:**
```
Minimum nodes = 3 (for quorum)

Data nodes = Total Storage / Storage per Node
           = 21.6 TB / 2 TB
           = 11 nodes

Master nodes = 3 (dedicated)

Total = 11 + 3 = 14 nodes
```

---

### 6.6 Production Checklist

✅ **Cluster Setup:**
- 3+ master nodes (quorum)
- Separate master/data nodes (large clusters)
- Enable X-Pack security (authentication, TLS)

✅ **Indexing:**
- Use bulk API (5-15 MB batches)
- Implement ILM policies
- Set appropriate refresh interval (30s for bulk)

✅ **Sharding:**
- 10-50 GB per shard
- Max 1000 shards per node
- Use custom routing for co-location

✅ **Mapping:**
- Use keyword for exact match
- Disable indexing for non-searchable fields
- Enable doc_values for aggregations

✅ **Queries:**
- Use filters (cached) instead of must (scored)
- Implement pagination (search_after)
- Use rescoring for top N

✅ **Monitoring:**
- Track cluster health
- Monitor JVM heap (<75%)
- Alert on yellow/red cluster status
- Log slow queries (>5s)

✅ **Backup:**
- Daily snapshots (SLM)
- Test restore regularly
- Store in separate region

✅ **Performance:**
- Force merge read-only indices
- Use hot-warm architecture
- Implement query caching

---

## 7. Real-World Case Studies

### 7.1 Uber's Elasticsearch

**Scale:**
- 150+ clusters
- 10,000+ nodes
- 1 PB indexed data
- 100M queries/day

**Use Cases:**
- Trip search
- Driver/rider matching
- Real-time analytics
- Log aggregation

**Architecture:**
```
Kafka → Logstash → Elasticsearch → Kibana

Optimizations:
- 30 shards per index (optimal for their data)
- 2 replicas (high availability)
- Hot-warm architecture (7d hot, 30d warm, 90d cold)
- Custom routing (by city, reduce scatter-gather)
```

---

### 7.2 Netflix's Elasticsearch

**Scale:**
- 50+ clusters
- 5,000+ nodes
- 3 billion events/day

**Use Cases:**
- User behavior analytics
- Content recommendation
- A/B test analysis
- Operational metrics

**Optimizations:**
- Index per hour (easy rollover)
- Ingest pipelines (enrich with metadata)
- Frozen indices (archive old data)
- Cross-cluster search (federated queries)

---

### 7.3 GitHub's Code Search

**Scale:**
- 8 million repositories
- 2 billion files
- 120 TB indexed data

**Use Cases:**
- Code search
- Symbol search (functions, classes)
- Regex search

**Optimizations:**
- Custom analyzers (code tokenization)
- Highlighting (show matching lines)
- Aggregations (facets by language, repository)
- Phrase search (find exact code snippets)

---

## Summary

### Architecture Decisions

| Decision | Reasoning |
|----------|-----------|
| 3 master nodes | Quorum for split-brain prevention |
| Separate master/data | Large clusters (stability) |
| 10-50 GB shards | Optimal search performance |
| Hot-warm architecture | Cost savings (80% on storage) |
| 2 replicas | High availability + read scaling |

---

### Performance Rules

1. **Indexing:** Bulk API (5-15 MB), refresh_interval=30s
2. **Sharding:** 10-50 GB per shard, max 1000/node
3. **Queries:** Filters (cached) > Must (scored)
4. **Aggregations:** Doc values (disk) > Field data (heap)
5. **Relevance:** BM25 + boosting + function_score

---

### When to Use Elasticsearch

✅ **Use when:**
- Full-text search required
- Need relevance ranking
- Complex aggregations
- Near real-time search
- Log analytics

❌ **Don't use when:**
- Need strong consistency (use RDBMS)
- Exact numerical calculations
- Complex joins (use SQL)
- Transactional workloads

---

**End of Search & Indexing Systems**

**Total Lines: ~4,000**
