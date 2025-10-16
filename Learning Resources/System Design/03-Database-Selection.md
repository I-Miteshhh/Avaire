# Database Selection - Choosing the Right Database for Scale

**Mastery Level:** Critical for Staff+ Data Engineers  
**Interview Weight:** 30-40% of system design interviews  
**Time to Master:** 2-3 weeks  
**Difficulty:** ⭐⭐⭐⭐⭐

---

## 🎯 Why Database Selection Matters

At **40+ LPA level**, choosing the wrong database can:
- **Cost millions** in infrastructure and migration
- **Block scaling** from 1M to 100M users
- **Create technical debt** lasting years
- **Impact availability** and consistency guarantees
- **Limit product features** due to query limitations

**The right choice enables scale, the wrong choice breaks it.**

---

## 🗃️ The Database Landscape

### **SQL Databases (ACID Guarantees)**
- **PostgreSQL** - Advanced relational with JSON support
- **MySQL** - Web-scale relational database
- **SQL Server** - Enterprise relational with analytics
- **Oracle** - Enterprise-grade with advanced features

### **NoSQL Databases**
- **Document:** MongoDB, CouchDB, Amazon DocumentDB
- **Key-Value:** Redis, DynamoDB, Riak
- **Column-Family:** Cassandra, HBase, Amazon SimpleDB
- **Graph:** Neo4j, Amazon Neptune, ArangoDB

### **NewSQL Databases**
- **Distributed SQL:** CockroachDB, TiDB, Yugabyte
- **In-Memory:** SAP HANA, VoltDB, MemSQL

### **Specialized Databases**
- **Time-Series:** InfluxDB, TimescaleDB, Amazon Timestream
- **Search:** Elasticsearch, Solr, Amazon CloudSearch
- **Analytics:** ClickHouse, Apache Druid, Snowflake

---

## 🤔 Database Selection Framework

### **Step 1: Analyze Your Data Characteristics**

#### **Data Structure Questions:**
```
📋 Data Structure Assessment
┌─────────────────────────────────────────────────────┐
│ ✅ Is your data highly structured?                   │
│   → Consider: PostgreSQL, MySQL                     │
│                                                     │
│ ✅ Do you need complex relationships?                │
│   → Consider: PostgreSQL, Neo4j                     │
│                                                     │
│ ✅ Is your data semi-structured/flexible schema?     │
│   → Consider: MongoDB, PostgreSQL (JSONB)          │
│                                                     │
│ ✅ Do you need full-text search?                    │
│   → Consider: Elasticsearch + Primary DB           │
│                                                     │
│ ✅ Is it primarily key-value access?                │
│   → Consider: Redis, DynamoDB                      │
└─────────────────────────────────────────────────────┘
```

#### **Scale Requirements:**
```python
class ScaleAnalysis:
    def analyze_scale_requirements(self):
        questions = {
            'read_qps': 'Expected read queries per second?',
            'write_qps': 'Expected write queries per second?',  
            'data_size': 'Total data size in 5 years?',
            'concurrent_users': 'Peak concurrent users?',
            'global_distribution': 'Need multi-region deployment?'
        }
        
        # Example analysis
        requirements = {
            'read_qps': 100_000,      # High read load
            'write_qps': 10_000,      # Medium write load  
            'data_size': '10TB',      # Large dataset
            'concurrent_users': 1_000_000,  # High concurrency
            'global_distribution': True   # Multi-region needed
        }
        
        return self.recommend_database(requirements)
    
    def recommend_database(self, req):
        recommendations = []
        
        # High read load suggests read replicas
        if req['read_qps'] > 50_000:
            recommendations.append('Need read replicas or caching')
        
        # Large data suggests sharding
        if 'TB' in req['data_size']:
            recommendations.append('Need horizontal scaling (sharding)')
        
        # Global distribution suggests consistency trade-offs
        if req['global_distribution']:
            recommendations.append('Consider eventual consistency')
        
        return recommendations
```

### **Step 2: Consistency Requirements (CAP Theorem)**

```
CAP Theorem Trade-offs:

Consistency + Availability (Sacrifice Partition Tolerance)
├─ PostgreSQL with synchronous replication
├─ MySQL Cluster  
└─ SQL Server Always On

Consistency + Partition Tolerance (Sacrifice Availability)  
├─ MongoDB with majority writes
├─ Cassandra with QUORUM consistency
└─ HBase with strong consistency

Availability + Partition Tolerance (Sacrifice Consistency)
├─ Cassandra with eventual consistency
├─ DynamoDB with eventual consistency  
└─ Riak with eventual consistency
```

#### **Consistency Levels Explained:**
```python
class ConsistencyLevels:
    def strong_consistency_example(self):
        """
        Example: Banking system - account balance
        Requirement: Never show incorrect balance
        """
        return {
            'database': 'PostgreSQL',
            'pattern': 'ACID transactions',
            'trade_off': 'Higher latency, potential unavailability'
        }
    
    def eventual_consistency_example(self):
        """
        Example: Social media likes count  
        Requirement: Slight delays in like count OK
        """
        return {
            'database': 'DynamoDB',
            'pattern': 'Asynchronous replication',
            'trade_off': 'Lower latency, high availability'
        }
    
    def causal_consistency_example(self):
        """
        Example: Chat messages
        Requirement: Messages appear in order for each user
        """
        return {
            'database': 'MongoDB',
            'pattern': 'Read-your-writes consistency',
            'trade_off': 'Balanced latency and correctness'
        }
```

---

## 🏆 Database Deep Dives

### **PostgreSQL - The Swiss Army Knife**

**Best For:** Complex queries, ACID requirements, JSON data, analytics

#### **Strengths:**
- **ACID Compliance:** Full transaction support
- **Rich Data Types:** JSON, arrays, custom types
- **Advanced Features:** Window functions, CTEs, full-text search
- **Extensible:** PostGIS for geospatial, TimescaleDB for time-series
- **Mature Ecosystem:** Excellent tooling and community

#### **Scaling Patterns:**
```python
class PostgreSQLScaling:
    def read_scaling(self):
        """Scale reads with replicas and connection pooling"""
        return {
            'read_replicas': 'async replication for read queries',
            'connection_pooling': 'PgBouncer to handle 10K+ connections',
            'query_optimization': 'Proper indexing and query tuning'
        }
    
    def write_scaling(self):
        """Scale writes with partitioning and sharding"""
        return {
            'partitioning': 'Built-in table partitioning by date/range',
            'sharding': 'Citus extension for horizontal sharding',
            'vertical_scaling': 'Scale up to 128 cores, 4TB RAM'
        }

# Example: Time-based partitioning
CREATE TABLE events (
    id BIGSERIAL,
    user_id INTEGER,
    event_type VARCHAR(50),
    created_at TIMESTAMP
) PARTITION BY RANGE (created_at);

CREATE TABLE events_2024_01 PARTITION OF events 
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE events_2024_02 PARTITION OF events
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
```

#### **When PostgreSQL Breaks:**
```python
class PostgreSQLLimitations:
    def write_bottleneck(self):
        """Single-master architecture limits write scaling"""
        return {
            'limit': '~50,000 writes/second on high-end hardware',
            'solution': 'Shard across multiple PostgreSQL clusters'
        }
    
    def cross_shard_queries(self):
        """Complex to query across shards"""
        return {
            'limit': 'JOINs across shards require application logic',
            'solution': 'Denormalize data or use distributed SQL'
        }
```

---

### **MongoDB - Document Flexibility**

**Best For:** Rapid development, flexible schemas, real-time apps

#### **Strengths:**
- **Schema Flexibility:** No predefined schema required
- **Horizontal Scaling:** Built-in sharding
- **Rich Queries:** Complex document queries and aggregations
- **Replication:** Automatic failover with replica sets
- **Ecosystem:** Atlas (managed), extensive drivers

#### **Scaling Architecture:**
```python
class MongoDBScaling:
    def __init__(self):
        self.sharding_config = {
            'config_servers': 3,     # Store cluster metadata
            'mongos_routers': 3,     # Query routing layer  
            'shards': 6,             # Data storage shards
            'replicas_per_shard': 3  # Replica set per shard
        }
    
    def shard_key_selection(self):
        """Critical: Choose the right shard key"""
        examples = {
            'user_data': {
                'good_key': 'user_id',  # Even distribution
                'bad_key': 'created_at',  # Hotspotting on recent data
                'compound_key': {'user_id': 1, 'category': 1}
            },
            'time_series': {
                'good_key': {'device_id': 1, 'timestamp': 1},
                'bad_key': 'timestamp'  # All recent data on one shard
            }
        }
        return examples

# Example: Proper sharding setup
db.adminCommand({
    shardCollection: "myapp.users",
    key: {"user_id": "hashed"}  # Hash-based sharding
})

# Zone sharding for geographic distribution  
sh.addShardTag("shard0000", "US")
sh.addShardTag("shard0001", "EU") 
sh.addTagRange("myapp.users", {"region": "US"}, {"region": "US\uffff"}, "US")
```

#### **MongoDB Best Practices:**
```javascript
// 1. Efficient schema design
{
  "_id": ObjectId("..."),
  "user_id": 12345,
  "profile": {
    "name": "John Doe",
    "email": "john@example.com"
  },
  "posts": [  // Embed if bounded, reference if unbounded
    {"title": "Post 1", "content": "..."},
    {"title": "Post 2", "content": "..."}
  ],
  "follower_count": 1500,  // Denormalize frequently accessed data
  "created_at": ISODate("2024-01-15")
}

// 2. Compound indexes for common query patterns
db.users.createIndex({"user_id": 1, "created_at": -1})

// 3. Aggregation pipelines for complex analytics
db.events.aggregate([
  {"$match": {"event_type": "purchase", "date": {"$gte": ISODate("2024-01-01")}}},
  {"$group": {"_id": "$product_id", "revenue": {"$sum": "$amount"}}},
  {"$sort": {"revenue": -1}},
  {"$limit": 10}
])
```

---

### **Cassandra - Petabyte Scale**

**Best For:** Time-series data, IoT, high write throughput, multi-region

#### **Strengths:**
- **Linear Scalability:** Add nodes to increase capacity
- **High Availability:** No single point of failure
- **Multi-Datacenter:** Built-in cross-region replication
- **Write Performance:** Optimized for high write workloads
- **Tunable Consistency:** Choose consistency vs performance

#### **Cassandra Data Modeling:**
```python
class CassandraDataModel:
    def design_for_queries(self):
        """Model data around query patterns, not relationships"""
        
        # Example: Time-series IoT data
        schema = """
        CREATE TABLE sensor_data_by_device (
            device_id UUID,
            year INT,
            month INT, 
            timestamp TIMESTAMP,
            temperature DOUBLE,
            humidity DOUBLE,
            PRIMARY KEY ((device_id, year, month), timestamp)
        ) WITH CLUSTERING ORDER BY (timestamp DESC);
        
        -- Separate table for different access pattern
        CREATE TABLE sensor_data_by_location (
            location TEXT,
            year INT,
            month INT,
            timestamp TIMESTAMP, 
            device_id UUID,
            temperature DOUBLE,
            PRIMARY KEY ((location, year, month), timestamp, device_id)
        ) WITH CLUSTERING ORDER BY (timestamp DESC);
        """
        
        return schema
    
    def consistency_levels(self):
        """Choose appropriate consistency for each operation"""
        return {
            'writes': {
                'ONE': 'Fastest, least durable',
                'QUORUM': 'Balanced durability/performance', 
                'ALL': 'Highest durability, slowest'
            },
            'reads': {
                'ONE': 'Fastest, may be stale',
                'QUORUM': 'Consistent with majority',
                'ALL': 'Strongest consistency'
            }
        }

# Example: Multi-datacenter setup
CREATE KEYSPACE analytics 
WITH REPLICATION = {
    'class': 'NetworkTopologyStrategy',
    'us-east': 3,  -- 3 replicas in US East
    'eu-west': 3,  -- 3 replicas in EU West  
    'ap-south': 2  -- 2 replicas in Asia Pacific
};
```

#### **Cassandra Operations:**
```python
class CassandraOperations:
    def write_path(self):
        """Understanding Cassandra's write path"""
        return {
            'commit_log': 'Append-only log for durability',
            'memtable': 'In-memory write cache',
            'sstables': 'Immutable disk files',
            'compaction': 'Background process to merge SSTables'
        }
    
    def read_path(self):
        """Understanding Cassandra's read path"""
        return {
            'bloom_filter': 'Check if key might exist in SSTable',
            'partition_summary': 'Find correct SSTable partition',
            'partition_index': 'Find exact location in partition',
            'data_file': 'Read actual data from disk'
        }
    
    def anti_patterns(self):
        """Common mistakes that break Cassandra"""
        return {
            'large_partitions': 'Keep partitions under 100MB',
            'hot_partitions': 'Avoid skewed access patterns',
            'secondary_indexes': 'Use sparingly, prefer denormalization',
            'counters': 'Avoid for high-frequency updates'
        }
```

---

### **DynamoDB - Serverless NoSQL**

**Best For:** Serverless apps, unpredictable traffic, AWS ecosystem

#### **Strengths:**
- **Serverless:** No infrastructure management
- **Auto-scaling:** Handles traffic spikes automatically
- **Single-digit Latency:** Consistent performance at scale
- **Global Tables:** Multi-region with eventual consistency
- **Streams:** Real-time change capture

#### **DynamoDB Design Patterns:**
```python
class DynamoDBDesign:
    def single_table_design(self):
        """One table to rule them all - DynamoDB best practice"""
        
        table_design = {
            'table_name': 'ecommerce-app',
            'partition_key': 'PK',  # Overloaded partition key
            'sort_key': 'SK',       # Overloaded sort key
            'gsi1': {'pk': 'GSI1PK', 'sk': 'GSI1SK'},
            'gsi2': {'pk': 'GSI2PK', 'sk': 'GSI2SK'}
        }
        
        # Example data patterns in single table
        examples = [
            # User entity
            {'PK': 'USER#12345', 'SK': 'PROFILE', 'name': 'John', 'email': 'john@example.com'},
            
            # User's orders
            {'PK': 'USER#12345', 'SK': 'ORDER#67890', 'total': 99.99, 'status': 'shipped'},
            
            # Product entity  
            {'PK': 'PRODUCT#ABC', 'SK': 'DETAILS', 'name': 'Widget', 'price': 29.99},
            
            # Product reviews
            {'PK': 'PRODUCT#ABC', 'SK': 'REVIEW#12345', 'rating': 5, 'comment': 'Great!'},
            
            # GSI1 for querying orders by status
            {'PK': 'USER#12345', 'SK': 'ORDER#67890', 'GSI1PK': 'STATUS#shipped', 'GSI1SK': '2024-01-15'}
        ]
        
        return {'design': table_design, 'examples': examples}
    
    def access_patterns(self):
        """Design around specific access patterns"""
        return {
            'get_user': 'PK = USER#12345, SK = PROFILE',
            'get_user_orders': 'PK = USER#12345, SK begins_with ORDER#',
            'get_product_reviews': 'PK = PRODUCT#ABC, SK begins_with REVIEW#',
            'get_orders_by_status': 'GSI1: GSI1PK = STATUS#shipped, sort by GSI1SK'
        }

# Example: DynamoDB with auto-scaling
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ecommerce-app')

# Batch write for efficiency
with table.batch_writer() as batch:
    for item in items:
        batch.put_item(Item=item)

# Query with pagination
def get_user_orders(user_id, last_key=None):
    kwargs = {
        'KeyConditionExpression': Key('PK').eq(f'USER#{user_id}') & Key('SK').begins_with('ORDER#'),
        'ScanIndexForward': False,  # Latest first
        'Limit': 20
    }
    
    if last_key:
        kwargs['ExclusiveStartKey'] = last_key
    
    response = table.query(**kwargs)
    return response['Items'], response.get('LastEvaluatedKey')
```

---

### **Redis - High Performance Caching**

**Best For:** Caching, session storage, real-time analytics, pub/sub

#### **Redis Data Structures:**
```python
class RedisPatterns:
    def caching_patterns(self):
        """Common caching patterns with Redis"""
        
        patterns = {
            'simple_cache': {
                'pattern': 'SET key value EX 3600',  # 1 hour TTL
                'use_case': 'API response caching'
            },
            
            'cache_aside': {
                'pattern': 'Check cache -> DB -> Update cache',
                'code': '''
                def get_user(user_id):
                    # Try cache first
                    user = redis.get(f"user:{user_id}")
                    if user:
                        return json.loads(user)
                    
                    # Cache miss - get from DB
                    user = db.get_user(user_id)
                    redis.setex(f"user:{user_id}", 3600, json.dumps(user))
                    return user
                '''
            },
            
            'write_through': {
                'pattern': 'Write to cache and DB simultaneously',
                'use_case': 'Critical data that must be cached'
            }
        }
        return patterns
    
    def advanced_structures(self):
        """Redis beyond simple key-value"""
        
        examples = {
            'leaderboard': '''
                # Sorted sets for leaderboards
                ZADD leaderboard 1000 "player1" 950 "player2" 800 "player3"
                ZREVRANGE leaderboard 0 9 WITHSCORES  # Top 10
                ZRANK leaderboard "player1"  # Get player rank
            ''',
            
            'rate_limiting': '''
                # Sliding window rate limiter
                key = f"rate_limit:{user_id}:{current_minute}"
                count = INCR key
                EXPIRE key 60  # Window size
                if count > rate_limit:
                    return "Rate limited"
            ''',
            
            'pub_sub': '''
                # Real-time notifications
                PUBLISH notifications "{"user_id": 123, "message": "New follower"}"
                SUBSCRIBE notifications
            ''',
            
            'distributed_locks': '''
                # Distributed locking with expiration
                SET lock:resource "owner_id" PX 30000 NX  # 30 second lock
                if result == "OK":
                    # Got the lock, do critical work
                    DEL lock:resource  # Release lock
            '''
        }
        return examples

# Redis Cluster for high availability
class RedisCluster:
    def __init__(self):
        self.nodes = [
            {'host': 'redis-node-1', 'port': 7000},
            {'host': 'redis-node-2', 'port': 7001}, 
            {'host': 'redis-node-3', 'port': 7002},
            {'host': 'redis-node-4', 'port': 7003},
            {'host': 'redis-node-5', 'port': 7004},
            {'host': 'redis-node-6', 'port': 7005}
        ]
    
    def hash_slot(self, key):
        """Redis uses CRC16 for consistent hashing"""
        import crc16
        return crc16.crc16xmodem(key.encode()) % 16384
    
    def get_node_for_key(self, key):
        slot = self.hash_slot(key)
        # Each node handles ~2730 slots (16384 / 6 nodes)
        node_index = slot // 2730
        return self.nodes[node_index]
```

---

## 🎯 Database Selection Decision Tree

### **Interactive Decision Framework:**

```python
class DatabaseSelector:
    def select_database(self, requirements):
        """Systematic database selection based on requirements"""
        
        # Step 1: Data model requirements
        if requirements.get('complex_relationships'):
            if requirements.get('graph_traversal'):
                return self._consider_graph_db(requirements)
            else:
                return self._consider_relational_db(requirements)
        
        elif requirements.get('flexible_schema'):
            return self._consider_document_db(requirements)
        
        elif requirements.get('simple_key_value'):
            return self._consider_key_value_db(requirements)
        
        # Step 2: Scale requirements
        elif requirements.get('high_write_throughput'):
            return self._consider_write_optimized_db(requirements)
        
        elif requirements.get('analytics_workload'):
            return self._consider_analytical_db(requirements)
        
        else:
            return self._default_recommendation(requirements)
    
    def _consider_relational_db(self, req):
        if req.get('scale') == 'large' and req.get('distributed'):
            return ['CockroachDB', 'TiDB', 'Yugabyte']  # Distributed SQL
        elif req.get('analytics_heavy'):
            return ['PostgreSQL with Citus', 'MySQL with Vitess']
        else:
            return ['PostgreSQL', 'MySQL']
    
    def _consider_document_db(self, req):
        if req.get('serverless'):
            return ['DynamoDB', 'CosmosDB'] 
        elif req.get('complex_queries'):
            return ['MongoDB', 'DocumentDB']
        else:
            return ['MongoDB']
    
    def _consider_key_value_db(self, req):
        if req.get('low_latency'):
            return ['Redis', 'KeyDB']
        elif req.get('serverless'):
            return ['DynamoDB']  
        elif req.get('high_durability'):
            return ['Riak', 'Cassandra as KV']
        else:
            return ['Redis', 'DynamoDB']

# Example usage
selector = DatabaseSelector()

requirements_ecommerce = {
    'complex_relationships': True,
    'scale': 'medium',
    'consistency': 'strong',
    'analytics_heavy': False
}
# Result: ['PostgreSQL', 'MySQL']

requirements_iot = {
    'flexible_schema': True,
    'high_write_throughput': True,
    'scale': 'large',
    'time_series': True
}  
# Result: ['Cassandra', 'InfluxDB', 'TimescaleDB']
```

### **Common Architecture Patterns:**

#### **Lambda Architecture (Batch + Streaming)**
```
Raw Data → [Kafka] → [Flink/Spark Streaming] → [Cassandra] (Real-time)
            ↓
         [HDFS/S3] → [Spark Batch] → [Snowflake/BigQuery] (Batch)
```

#### **Polyglot Persistence**
```python
class ECommerceArchitecture:
    databases = {
        'user_profiles': 'PostgreSQL',      # ACID for user data
        'product_catalog': 'Elasticsearch', # Search and faceting
        'shopping_carts': 'Redis',          # Session storage
        'order_history': 'MongoDB',         # Document flexibility
        'inventory': 'PostgreSQL',          # Consistency critical
        'recommendations': 'Neo4j',         # Graph relationships
        'analytics': 'ClickHouse',          # Fast aggregations
        'logs': 'Elasticsearch'             # Full-text search
    }
    
    def get_database_for_usecase(self, use_case):
        return self.databases.get(use_case, 'PostgreSQL')  # Default to PostgreSQL
```

---

## 💰 Cost Considerations

### **Database Cost Analysis:**

```python
class DatabaseCostAnalyzer:
    def calculate_monthly_cost(self, db_type, requirements):
        """Estimate monthly database costs"""
        
        costs = {
            'postgresql_rds': {
                'compute': 0.35,  # per vCPU hour
                'storage': 0.115,  # per GB/month
                'iops': 0.065     # per provisioned IOPS
            },
            'dynamodb': {
                'read_units': 0.00013,  # per RRU
                'write_units': 0.00065, # per WRU  
                'storage': 0.25         # per GB/month
            },
            'mongodb_atlas': {
                'compute': 0.08,   # M40 instance per hour
                'storage': 0.25,   # per GB/month
                'transfer': 0.10   # per GB out
            }
        }
        
        if db_type == 'dynamodb':
            monthly_cost = (
                requirements['reads_per_second'] * 2.628e6 * costs['dynamodb']['read_units'] +  # RRUs per month
                requirements['writes_per_second'] * 2.628e6 * costs['dynamodb']['write_units'] +  # WRUs per month
                requirements['storage_gb'] * costs['dynamodb']['storage']
            )
        
        elif db_type == 'postgresql_rds':
            monthly_cost = (
                requirements['instance_hours'] * costs['postgresql_rds']['compute'] +
                requirements['storage_gb'] * costs['postgresql_rds']['storage'] +
                requirements['provisioned_iops'] * costs['postgresql_rds']['iops']
            )
        
        return monthly_cost
    
    def cost_optimization_tips(self):
        return {
            'postgresql': [
                'Use read replicas instead of scaling master',
                'Enable compression for large tables',
                'Archive old data to cheaper storage',
                'Use connection pooling to reduce instance size'
            ],
            'dynamodb': [
                'Use on-demand billing for unpredictable workloads',
                'Enable auto-scaling for provisioned capacity',
                'Compress large items before storing',
                'Use DynamoDB Accelerator (DAX) for hot data'
            ],
            'mongodb': [
                'Use appropriate index strategies',
                'Enable compression at rest',
                'Use MongoDB Atlas auto-scaling',
                'Archive old data with online archive'
            ]
        }
```

---

## 🎯 Real-World Case Studies

### **Case Study 1: Uber's Database Evolution**

**Challenge:** Store and query trillion+ trips, real-time pricing, global scale

**Evolution:**
```python
class UberDatabaseEvolution:
    def phase_1_postgresql(self):
        """2009-2014: PostgreSQL with read replicas"""
        return {
            'database': 'PostgreSQL',
            'pattern': 'Master-slave replication',
            'challenges': 'Write scaling bottleneck',
            'data_size': '~100GB'
        }
    
    def phase_2_sharding(self):
        """2014-2016: Sharded PostgreSQL"""
        return {
            'database': 'Sharded PostgreSQL', 
            'pattern': 'Geographic + user-based sharding',
            'challenges': 'Cross-shard queries, operational complexity',
            'data_size': '~10TB'
        }
    
    def phase_3_schemaless(self):
        """2016-2020: Schemaless (MySQL + blob storage)"""
        return {
            'database': 'MySQL + Blob storage',
            'pattern': 'Schemaless architecture on MySQL',
            'benefits': 'Schema evolution, better sharding',
            'data_size': '~100TB+'
        }
    
    def phase_4_specialized(self):
        """2020+: Polyglot persistence"""
        return {
            'trip_data': 'Schemaless (MySQL)',
            'real_time': 'Apache Pinot',
            'maps': 'PostGIS',
            'ml_features': 'Cassandra',
            'search': 'Elasticsearch'
        }
```

### **Case Study 2: Discord's Message Storage**

**Challenge:** Store billions of messages, real-time delivery, message history

**Solution:**
```python
class DiscordMessageStorage:
    def cassandra_approach(self):
        """Discord's Cassandra solution"""
        
        schema = """
        CREATE TABLE messages (
            channel_id BIGINT,
            bucket INT,          -- Time bucket (hour/day)
            message_id BIGINT,
            author_id BIGINT, 
            content TEXT,
            created_at TIMESTAMP,
            PRIMARY KEY ((channel_id, bucket), message_id)
        ) WITH CLUSTERING ORDER BY (message_id DESC);
        """
        
        benefits = [
            'Linear scaling with node addition',
            'No single point of failure', 
            'Tunable consistency',
            'Excellent write performance'
        ]
        
        challenges = [
            'Hot partitions for popular channels',
            'Complex bucket management',
            'Limited query flexibility'
        ]
        
        return {'schema': schema, 'benefits': benefits, 'challenges': challenges}
    
    def optimization_techniques(self):
        return {
            'bucketing': 'Distribute messages across time buckets',
            'denormalization': 'Store user info with messages',
            'caching': 'Redis for recent messages',
            'compression': 'LZ4 compression for old messages'
        }
```

---

## ✅ Database Selection Checklist

### **Requirements Analysis**
- [ ] Data structure (relational, document, key-value, graph)
- [ ] Query patterns (simple lookups, complex joins, analytics)
- [ ] Consistency requirements (ACID, eventual, causal)
- [ ] Scale requirements (reads/writes per second, data size)
- [ ] Latency requirements (sub-ms, <100ms, <1s)

### **Technical Evaluation**  
- [ ] Horizontal scaling capabilities
- [ ] Backup and disaster recovery
- [ ] Security features (encryption, access control)
- [ ] Monitoring and observability
- [ ] Ecosystem and tooling maturity

### **Operational Considerations**
- [ ] Team expertise and learning curve
- [ ] Operational overhead (managed vs self-hosted)
- [ ] Cost analysis (compute, storage, transfer)
- [ ] Vendor lock-in implications
- [ ] Migration strategy from current system

### **Future-Proofing**
- [ ] Roadmap and community support
- [ ] Performance characteristics at target scale
- [ ] Feature development velocity
- [ ] Multi-cloud deployment options
- [ ] Compliance requirements (GDPR, HIPAA, SOX)

**Master these selection criteria, and you'll choose databases that scale beautifully!** 🎯