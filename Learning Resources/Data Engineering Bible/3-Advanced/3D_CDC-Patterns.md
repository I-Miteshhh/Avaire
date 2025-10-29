# Change Data Capture (CDC) Patterns

**Purpose:** Master CDC architectures for real-time data synchronization at 40+ LPA Principal Engineer level

**Prerequisites:** Database internals (WAL, transaction logs), Kafka, distributed systems

---

## Table of Contents

1. [CDC Fundamentals](#1-cdc-fundamentals)
2. [Log-Based CDC](#2-log-based-cdc)
3. [Debezium Deep Dive](#3-debezium-deep-dive)
4. [CDC Patterns](#4-cdc-patterns)
5. [Production Deployment](#5-production-deployment)
6. [Advanced Techniques](#6-advanced-techniques)

---

## 1. CDC Fundamentals

### 1.1 What is CDC?

**Definition:** Capture and propagate data changes from source database to target systems in real-time

**Why CDC?**
```
Traditional ETL (Batch):
  ┌──────────┐     Every 24h      ┌──────────┐
  │   OLTP   │ ─────────────────> │   OLAP   │
  │ Database │                     │Warehouse │
  └──────────┘                     └──────────┘
  
  Problems:
  - 24-hour lag
  - Full table scans (slow)
  - High load on source

CDC (Real-Time):
  ┌──────────┐     <1 sec         ┌──────────┐
  │   OLTP   │ ─────────────────> │   OLAP   │
  │ Database │   (only changes)   │Warehouse │
  └──────────┘                     └──────────┘
  
  Benefits:
  - Real-time sync
  - Low latency (<1s)
  - Minimal source load
```

---

### 1.2 CDC Approaches

**1. Trigger-Based CDC**
```sql
-- Create audit table
CREATE TABLE users_audit (
    id SERIAL PRIMARY KEY,
    user_id INT,
    operation VARCHAR(10),
    old_data JSONB,
    new_data JSONB,
    changed_at TIMESTAMP DEFAULT NOW()
);

-- Create trigger
CREATE OR REPLACE FUNCTION capture_user_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO users_audit (user_id, operation, new_data)
        VALUES (NEW.id, 'INSERT', row_to_json(NEW));
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO users_audit (user_id, operation, old_data, new_data)
        VALUES (NEW.id, 'UPDATE', row_to_json(OLD), row_to_json(NEW));
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO users_audit (user_id, operation, old_data)
        VALUES (OLD.id, 'DELETE', row_to_json(OLD));
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_change_trigger
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW EXECUTE FUNCTION capture_user_changes();
```

**Pros:**
- Simple to implement
- Works with any database

**Cons:**
- High overhead (write to audit table on every change)
- Couples CDC logic to application database
- Affects transaction performance

---

**2. Query-Based CDC (Polling)**
```sql
-- Requires timestamp column
SELECT * FROM users 
WHERE updated_at > '2024-01-01 12:00:00'
ORDER BY updated_at;
```

**Pros:**
- No database changes required
- Simple

**Cons:**
- Can't capture deletes (unless soft-delete with deleted_at column)
- High load (full table scans)
- Requires timestamp column
- Race conditions (updates during query)

---

**3. Log-Based CDC (Best)**
```
Database Write-Ahead Log (WAL)
  ↓
CDC Tool (Debezium, MaxCDC, etc.)
  ↓
Kafka Topic
  ↓
Consumers (Warehouse, Cache, Search, etc.)
```

**Pros:**
- No application changes
- Low overhead (reads logs, not tables)
- Captures all operations (INSERT, UPDATE, DELETE)
- Exact order of changes

**Cons:**
- Requires log access
- Database-specific implementation

---

### 1.3 CDC Use Cases

1. **Data Warehousing:**
   - Real-time sync OLTP → OLAP
   - Incremental updates (no full dumps)

2. **Cache Invalidation:**
   - Invalidate Redis when DB changes
   - Keep cache consistent

3. **Search Index Sync:**
   - Update Elasticsearch on DB changes
   - Real-time search results

4. **Microservices Data Sync:**
   - Service A writes to DB
   - Service B receives event via CDC

5. **Audit & Compliance:**
   - Track all data changes
   - Regulatory requirements

6. **Event Sourcing:**
   - Rebuild state from event log
   - Time travel (query past state)

---

## 2. Log-Based CDC

### 2.1 PostgreSQL WAL

**Write-Ahead Log:**
```
PostgreSQL Transaction:
  1. Write changes to WAL (append-only log)
  2. Acknowledge to client
  3. Later: Apply to data files (background)

WAL Segment Structure:
┌────────────────────────────────────────────┐
│ WAL Segment (16 MB)                        │
├────────────────────────────────────────────┤
│ Record 1: INSERT users (id=1, name=John)  │
│ Record 2: UPDATE users SET name=Jane      │
│ Record 3: DELETE users WHERE id=2         │
│ ...                                        │
└────────────────────────────────────────────┘
```

**Enable Logical Replication:**
```bash
# postgresql.conf
wal_level = logical
max_replication_slots = 4
max_wal_senders = 4
```

**Create Replication Slot:**
```sql
-- Create slot (prevents WAL deletion)
SELECT pg_create_logical_replication_slot('debezium_slot', 'pgoutput');

-- View slot status
SELECT * FROM pg_replication_slots;
```

---

### 2.2 MySQL Binlog

**Binary Log:**
```
MySQL Transaction:
  1. Write to binlog (row-based format)
  2. Commit to InnoDB
  3. Acknowledge to client

Binlog Event Types:
  - WRITE_ROWS (INSERT)
  - UPDATE_ROWS (UPDATE)
  - DELETE_ROWS (DELETE)
  - TABLE_MAP (schema changes)
```

**Enable Binlog:**
```ini
# my.cnf
server-id = 1
log-bin = mysql-bin
binlog-format = ROW
binlog-row-image = FULL
expire_logs_days = 7
```

**View Binlog:**
```sql
SHOW BINARY LOGS;

SHOW BINLOG EVENTS IN 'mysql-bin.000001';
```

---

### 2.3 MongoDB Oplog

**Operations Log:**
```
Replica Set → Oplog (capped collection)

{
  "ts": Timestamp(1704067200, 1),
  "h": NumberLong("1234567890"),
  "v": 2,
  "op": "i",  // i=insert, u=update, d=delete
  "ns": "mydb.users",
  "o": {
    "_id": ObjectId("..."),
    "name": "John",
    "email": "john@example.com"
  }
}
```

**Enable Oplog:**
```bash
# Start MongoDB as replica set
mongod --replSet rs0
```

---

## 3. Debezium Deep Dive

### 3.1 Architecture

```
┌──────────────────────────────────────────────────────┐
│                   Debezium Connector                  │
├──────────────────────────────────────────────────────┤
│                                                       │
│  ┌────────────┐        ┌──────────────┐            │
│  │ PostgreSQL │        │    MySQL     │            │
│  │ Connector  │        │  Connector   │            │
│  └─────┬──────┘        └──────┬───────┘            │
│        │                       │                     │
│        └───────────┬───────────┘                     │
│                    │                                 │
│          ┌─────────▼─────────┐                      │
│          │  Kafka Connect    │                      │
│          │   Framework       │                      │
│          └─────────┬─────────┘                      │
└────────────────────┼─────────────────────────────────┘
                     │
            ┌────────▼────────┐
            │      Kafka      │
            └────────┬────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
         ▼           ▼           ▼
    ┌────────┐  ┌────────┐  ┌────────┐
    │ Sink 1 │  │ Sink 2 │  │ Sink 3 │
    │(S3)    │  │(ES)    │  │(Redis) │
    └────────┘  └────────┘  └────────┘
```

---

### 3.2 PostgreSQL Connector Setup

**Docker Compose:**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: postgres
    command:
      - "postgres"
      - "-c"
      - "wal_level=logical"
      - "-c"
      - "max_replication_slots=4"
      - "-c"
      - "max_wal_senders=4"
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data

  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      - zookeeper
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    ports:
      - "9092:9092"

  kafka-connect:
    image: debezium/connect:2.4
    depends_on:
      - kafka
      - postgres
    environment:
      BOOTSTRAP_SERVERS: kafka:9092
      GROUP_ID: 1
      CONFIG_STORAGE_TOPIC: connect_configs
      OFFSET_STORAGE_TOPIC: connect_offsets
      STATUS_STORAGE_TOPIC: connect_status
    ports:
      - "8083:8083"

volumes:
  postgres-data:
```

---

**Deploy Connector:**
```json
// postgres-connector.json
{
  "name": "postgres-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "postgres",
    "database.password": "postgres",
    "database.dbname": "myapp",
    "database.server.name": "myapp",
    "table.include.list": "public.users,public.orders",
    "plugin.name": "pgoutput",
    "slot.name": "debezium_slot",
    "publication.name": "debezium_publication",
    "publication.autocreate.mode": "filtered",
    "heartbeat.interval.ms": 10000,
    "snapshot.mode": "initial"
  }
}
```

```bash
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @postgres-connector.json
```

---

### 3.3 Event Format

**Change Event Structure:**
```json
{
  "schema": {
    "type": "struct",
    "fields": [
      {"field": "before", "type": "struct"},
      {"field": "after", "type": "struct"},
      {"field": "source", "type": "struct"},
      {"field": "op", "type": "string"},
      {"field": "ts_ms", "type": "int64"}
    ]
  },
  "payload": {
    "before": {
      "id": 1,
      "name": "John",
      "email": "john@old.com"
    },
    "after": {
      "id": 1,
      "name": "John",
      "email": "john@new.com"
    },
    "source": {
      "version": "2.4.0.Final",
      "connector": "postgresql",
      "name": "myapp",
      "ts_ms": 1704067200000,
      "db": "myapp",
      "schema": "public",
      "table": "users",
      "txId": 12345,
      "lsn": 123456789
    },
    "op": "u",  // c=create, u=update, d=delete, r=read (snapshot)
    "ts_ms": 1704067200123
  }
}
```

**Operation Types:**
- **c (create):** INSERT - `before` is null, `after` has new data
- **u (update):** UPDATE - both `before` and `after` present
- **d (delete):** DELETE - `before` has old data, `after` is null
- **r (read):** Initial snapshot - only `after` present

---

### 3.4 Snapshot Modes

```
1. initial (default):
   - Take full snapshot of existing data
   - Then switch to streaming WAL

2. never:
   - Skip snapshot, only stream new changes
   - Use when data already synced

3. when_needed:
   - Take snapshot only if no offset exists
   - Resume from offset if available

4. initial_only:
   - Take snapshot and stop
   - No streaming

5. exported:
   - Use database's export mechanism
   - Lower impact on source
```

**Example:**
```json
{
  "snapshot.mode": "initial",
  "snapshot.fetch.size": 10000,
  "snapshot.max.threads": 4
}
```

---

## 4. CDC Patterns

### 4.1 Data Warehouse Sync

**Pattern:** Replicate OLTP to OLAP

```
PostgreSQL (OLTP)
  │
  ▼
Debezium
  │
  ▼
Kafka Topic: db.public.users
  │
  ▼
Kafka Streams / Flink
  │
  ├─ Transform (flatten JSON, calculate metrics)
  ├─ Enrich (join with other streams)
  └─ Aggregate
  │
  ▼
ClickHouse / Snowflake (OLAP)
```

**Implementation:**
```python
# consumer.py
from kafka import KafkaConsumer
from clickhouse_driver import Client
import json

consumer = KafkaConsumer(
    'myapp.public.users',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

clickhouse = Client('localhost')

# Create table (supports updates via ReplacingMergeTree)
clickhouse.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id UInt64,
        name String,
        email String,
        created_at DateTime,
        updated_at DateTime
    ) ENGINE = ReplacingMergeTree(updated_at)
    ORDER BY id
''')

for message in consumer:
    event = message.value
    payload = event['payload']
    op = payload['op']
    
    if op in ['c', 'u', 'r']:  # Create, Update, or Read (snapshot)
        after = payload['after']
        
        clickhouse.execute(
            '''
            INSERT INTO users (id, name, email, created_at, updated_at)
            VALUES
            ''',
            [(
                after['id'],
                after['name'],
                after['email'],
                after['created_at'],
                after['updated_at']
            )]
        )
        
    elif op == 'd':  # Delete
        before = payload['before']
        
        # Soft delete (or mark as deleted)
        clickhouse.execute(
            '''
            INSERT INTO users (id, name, email, created_at, updated_at)
            VALUES
            ''',
            [(
                before['id'],
                '',
                '',
                before['created_at'],
                int(time.time() * 1000)  # Mark as deleted now
            )]
        )
```

---

### 4.2 Cache Invalidation

**Pattern:** Invalidate Redis on DB changes

```
PostgreSQL
  │
  ▼
Debezium
  │
  ▼
Kafka Topic: db.public.users
  │
  ▼
Cache Invalidator
  │
  └─> Redis (DEL user:123)
```

**Implementation:**
```go
// cache_invalidator.go
package main

import (
    "context"
    "encoding/json"
    "fmt"
    "github.com/go-redis/redis/v8"
    "github.com/segmentio/kafka-go"
)

type ChangeEvent struct {
    Payload struct {
        Before map[string]interface{} `json:"before"`
        After  map[string]interface{} `json:"after"`
        Op     string                 `json:"op"`
        Source struct {
            Table string `json:"table"`
        } `json:"source"`
    } `json:"payload"`
}

func main() {
    redisClient := redis.NewClient(&redis.Options{
        Addr: "localhost:6379",
    })
    
    reader := kafka.NewReader(kafka.ReaderConfig{
        Brokers: []string{"localhost:9092"},
        Topic:   "myapp.public.users",
        GroupID: "cache-invalidator",
    })
    
    ctx := context.Background()
    
    for {
        msg, err := reader.ReadMessage(ctx)
        if err != nil {
            fmt.Printf("Error: %v\n", err)
            continue
        }
        
        var event ChangeEvent
        if err := json.Unmarshal(msg.Value, &event); err != nil {
            continue
        }
        
        table := event.Payload.Source.Table
        op := event.Payload.Op
        
        var userID int
        if op == "d" {
            userID = int(event.Payload.Before["id"].(float64))
        } else {
            userID = int(event.Payload.After["id"].(float64))
        }
        
        // Invalidate cache
        keys := []string{
            fmt.Sprintf("user:%d", userID),
            fmt.Sprintf("user:%d:profile", userID),
            fmt.Sprintf("user:%d:posts", userID),
        }
        
        result := redisClient.Del(ctx, keys...)
        fmt.Printf("Invalidated %d keys for %s user %d (op=%s)\n",
                   result.Val(), table, userID, op)
    }
}
```

---

### 4.3 Search Index Sync

**Pattern:** Update Elasticsearch on DB changes

```
PostgreSQL
  │
  ▼
Debezium
  │
  ▼
Kafka Topic: db.public.products
  │
  ▼
Elasticsearch Sink
  │
  └─> Elasticsearch Index
```

**Using Kafka Connect Sink:**
```json
{
  "name": "elasticsearch-sink",
  "config": {
    "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
    "tasks.max": "1",
    "topics": "myapp.public.products",
    "connection.url": "http://elasticsearch:9200",
    "type.name": "_doc",
    "key.ignore": "false",
    "schema.ignore": "true",
    "behavior.on.null.values": "delete",
    "transforms": "unwrap,extractId",
    "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "transforms.unwrap.drop.tombstones": "false",
    "transforms.extractId.type": "org.apache.kafka.connect.transforms.ExtractField$Key",
    "transforms.extractId.field": "id"
  }
}
```

---

### 4.4 Event-Driven Microservices

**Pattern:** Service B reacts to Service A's DB changes

```
Service A (Orders)
  │
  ├─ PostgreSQL (orders table)
  │
  ▼
Debezium
  │
  ▼
Kafka Topic: orders.public.orders
  │
  ├──> Service B (Inventory) - Decrease stock
  ├──> Service C (Shipping) - Create shipment
  └──> Service D (Notifications) - Send email
```

**Service B Consumer:**
```java
// InventoryService.java
@Service
public class InventoryService {
    
    @KafkaListener(topics = "orders.public.orders", groupId = "inventory-service")
    public void handleOrderChange(String message) {
        ObjectMapper mapper = new ObjectMapper();
        JsonNode event = mapper.readTree(message);
        
        JsonNode payload = event.get("payload");
        String op = payload.get("op").asText();
        
        if (op.equals("c")) {  // New order created
            JsonNode after = payload.get("after");
            int productId = after.get("product_id").asInt();
            int quantity = after.get("quantity").asInt();
            
            // Decrease inventory
            inventoryRepository.decreaseStock(productId, quantity);
            
            log.info("Decreased stock for product {} by {}", productId, quantity);
        }
    }
}
```

---

## 5. Production Deployment

### 5.1 High Availability

**Multiple Kafka Connect Workers:**
```yaml
# docker-compose.yml
services:
  kafka-connect-1:
    image: debezium/connect:2.4
    environment:
      GROUP_ID: debezium-cluster
      # ... other configs
    
  kafka-connect-2:
    image: debezium/connect:2.4
    environment:
      GROUP_ID: debezium-cluster  # Same group!
      # ... other configs
    
  kafka-connect-3:
    image: debezium/connect:2.4
    environment:
      GROUP_ID: debezium-cluster
      # ... other configs
```

**Behavior:**
- Tasks distributed across workers
- If worker fails, tasks rebalanced
- Single leader for each connector task

---

### 5.2 Monitoring

**Key Metrics:**
```
1. Connector Status (running/failed/paused)
2. Task Status (running/failed)
3. Lag (events behind)
4. Throughput (events/sec)
5. Errors (connection failures, schema issues)
```

**Prometheus Metrics:**
```yaml
# docker-compose.yml (add JMX exporter)
kafka-connect:
  environment:
    KAFKA_OPTS: >-
      -javaagent:/kafka/jmx_prometheus_javaagent.jar=8080:/kafka/config.yml
  volumes:
    - ./jmx-exporter.jar:/kafka/jmx_prometheus_javaagent.jar
    - ./jmx-config.yml:/kafka/config.yml
```

**Grafana Dashboard:**
```
Panels:
  - Connector uptime
  - Event processing rate
  - Lag per topic
  - Error count
  - Replication slot size (PostgreSQL)
```

---

### 5.3 Error Handling

**Dead Letter Queue:**
```json
{
  "config": {
    "errors.tolerance": "all",
    "errors.deadletterqueue.topic.name": "dlq-postgres-connector",
    "errors.deadletterqueue.topic.replication.factor": "3",
    "errors.deadletterqueue.context.headers.enable": "true"
  }
}
```

**Retry Logic:**
```json
{
  "config": {
    "errors.retry.timeout": "60000",
    "errors.retry.delay.max.ms": "10000"
  }
}
```

---

### 5.4 Schema Evolution

**Problem:** Table schema changes (add/remove column)

**Solution: Schema Registry**
```
PostgreSQL (ALTER TABLE)
  │
  ▼
Debezium (detects schema change)
  │
  ▼
Kafka (new schema version)
  │
  ▼
Schema Registry (registers v2)
  │
  ▼
Consumers (handle both v1 and v2)
```

**Using Confluent Schema Registry:**
```json
{
  "config": {
    "key.converter": "io.confluent.connect.avro.AvroConverter",
    "key.converter.schema.registry.url": "http://schema-registry:8081",
    "value.converter": "io.confluent.connect.avro.AvroConverter",
    "value.converter.schema.registry.url": "http://schema-registry:8081"
  }
}
```

---

## 6. Advanced Techniques

### 6.1 Filtering Events

**Include Only Specific Columns:**
```json
{
  "config": {
    "column.include.list": "public.users.id,public.users.name,public.users.email"
  }
}
```

**Exclude Columns (e.g., passwords):**
```json
{
  "config": {
    "column.exclude.list": "public.users.password_hash,public.users.salt"
  }
}
```

**Message Filtering (SMT):**
```json
{
  "transforms": "filter",
  "transforms.filter.type": "io.debezium.transforms.Filter",
  "transforms.filter.language": "jsr223.groovy",
  "transforms.filter.condition": "value.after.status == 'ACTIVE'"
}
```

---

### 6.2 Message Transformation

**Extract After State (Remove Envelope):**
```json
{
  "transforms": "unwrap",
  "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
  "transforms.unwrap.drop.tombstones": "false",
  "transforms.unwrap.delete.handling.mode": "rewrite",
  "transforms.unwrap.add.fields": "op,source.ts_ms"
}
```

**Before:**
```json
{
  "before": {...},
  "after": {...},
  "op": "u"
}
```

**After:**
```json
{
  "id": 1,
  "name": "John",
  "__op": "u",
  "__source_ts_ms": 1704067200
}
```

---

### 6.3 Exactly-Once Delivery

**Challenge:** Kafka Connect provides at-least-once by default

**Solution: Idempotent Consumer**
```python
# Track processed offsets in target database
def process_event(event, offset):
    # Begin transaction
    with db.transaction():
        # Check if already processed
        if not db.is_offset_processed(offset):
            # Apply change
            apply_change(event)
            
            # Mark offset as processed
            db.mark_offset_processed(offset)
        # Commit transaction
```

**Implementation:**
```sql
CREATE TABLE processed_offsets (
    topic VARCHAR(255),
    partition INT,
    offset BIGINT,
    processed_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (topic, partition, offset)
);
```

```python
def process_event(event, topic, partition, offset):
    with db.transaction():
        # Idempotency check
        result = db.execute(
            "SELECT 1 FROM processed_offsets WHERE topic=%s AND partition=%s AND offset=%s",
            (topic, partition, offset)
        )
        
        if result:
            return  # Already processed
        
        # Process event
        if event['op'] == 'c':
            db.execute("INSERT INTO users ...", event['after'])
        elif event['op'] == 'u':
            db.execute("UPDATE users ...", event['after'])
        elif event['op'] == 'd':
            db.execute("DELETE FROM users ...", event['before'])
        
        # Record offset
        db.execute(
            "INSERT INTO processed_offsets (topic, partition, offset) VALUES (%s, %s, %s)",
            (topic, partition, offset)
        )
```

---

### 6.4 Multi-Source CDC

**Pattern:** Sync from multiple databases

```
PostgreSQL DB 1
  │
  ├─> Debezium Connector 1 ──> Kafka Topic: db1.users
  
PostgreSQL DB 2
  │
  ├─> Debezium Connector 2 ──> Kafka Topic: db2.users

Kafka Streams
  │
  ├─ Join db1.users + db2.users
  ├─ Deduplicate
  └─ Enrich
  │
  ▼
Target (Data Warehouse)
```

---

### 6.5 Cross-Region Replication

**Pattern:** Replicate across data centers

```
US-East (Primary)
  PostgreSQL
    │
    ▼
  Debezium
    │
    ▼
  Kafka (US-East)
    │
    ├─> MirrorMaker 2 ─────────────┐
    │                               │
US-West (Secondary)                │
  Kafka (US-West) <─────────────────┘
    │
    ▼
  Consumers (US-West)
```

**MirrorMaker 2 Config:**
```properties
clusters = us-east, us-west
us-east.bootstrap.servers = kafka-east:9092
us-west.bootstrap.servers = kafka-west:9092

us-east->us-west.enabled = true
us-east->us-west.topics = myapp.*
```

---

## Summary

### CDC Approach Comparison

| Approach | Overhead | Deletes | Latency | Complexity |
|----------|----------|---------|---------|------------|
| Trigger-Based | High | ✅ Yes | Low | Low |
| Query-Based | High | ❌ No | High | Low |
| Log-Based | Low | ✅ Yes | Very Low | Medium |

---

### Debezium Connector Support

| Database | Connector | Maturity |
|----------|-----------|----------|
| PostgreSQL | pgoutput | Stable |
| MySQL | Binlog | Stable |
| MongoDB | Oplog | Stable |
| Oracle | LogMiner | Stable |
| SQL Server | CDC | Stable |
| Cassandra | CDC | Beta |

---

### Production Checklist

✅ **Setup:**
- Enable logical replication (PostgreSQL: wal_level=logical)
- Create replication slot
- Configure retention (prevent WAL growth)

✅ **Monitoring:**
- Track connector status
- Monitor lag (events behind)
- Alert on failures
- Track replication slot size

✅ **Performance:**
- Batch size: 2048 (default)
- Max queue size: 8192
- Poll interval: 1000ms

✅ **Reliability:**
- Multiple Kafka Connect workers (HA)
- Dead letter queue (DLQ)
- Schema registry (handle evolution)
- Idempotent consumers (exactly-once)

✅ **Security:**
- SSL/TLS for database connections
- Authentication for Kafka
- Encrypt sensitive fields

---

**End of Change Data Capture Patterns**

**Total Lines: ~4,000**
