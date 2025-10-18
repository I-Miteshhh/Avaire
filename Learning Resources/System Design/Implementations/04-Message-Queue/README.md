# Message Queue - Production Implementation

**Target Scale:** Handle **1M+ messages/sec** with **exactly-once delivery guarantees**

---

## Table of Contents
1. [Problem Statement](#1-problem-statement)
2. [Requirements](#2-requirements)
3. [Core Concepts](#3-core-concepts)
4. [Architecture](#4-architecture)
5. [Implementation](#5-implementation)
6. [Delivery Guarantees](#6-delivery-guarantees)
7. [Advanced Features](#7-advanced-features)

---

## 1. Problem Statement

### What is a Message Queue?

A message queue is a form of asynchronous service-to-service communication that enables:
- **Decoupling:** Producers and consumers don't need to know about each other
- **Reliability:** Messages persist even if consumers are down
- **Scalability:** Multiple consumers can process messages in parallel
- **Load Leveling:** Queue absorbs traffic spikes

**Real-World Examples:**
- **Amazon SQS:** 100,000+ messages/sec, fully managed
- **Apache Kafka:** 1M+ messages/sec, LinkedIn uses for event streaming
- **RabbitMQ:** 20,000+ messages/sec, used by Instagram for async tasks
- **Google Cloud Pub/Sub:** Globally distributed, 100M+ messages/sec

---

### Use Cases

1. **Async Task Processing:** Send emails, generate reports, process uploads
2. **Event Streaming:** Real-time analytics, clickstream processing
3. **Microservices Communication:** Order service → Payment service → Shipping service
4. **Log Aggregation:** Collect logs from distributed services
5. **Data Pipeline:** ETL workflows (Extract → Transform → Load)

---

## 2. Requirements

### Functional Requirements

1. **Core Operations:**
   - `Send(topic, message)` - Publish message to topic
   - `Receive(topic, consumer_group)` - Consume messages from topic
   - `Ack(message_id)` - Acknowledge message processing
   - `Nack(message_id)` - Negative acknowledgment (retry)

2. **Message Ordering:**
   - FIFO (First In First Out) within partition
   - Total ordering (single partition)
   - Partial ordering (multiple partitions)

3. **Delivery Guarantees:**
   - At-most-once: Message may be lost
   - At-least-once: Message may be delivered multiple times
   - Exactly-once: Message delivered exactly once

4. **Consumer Groups:**
   - Multiple consumers in same group share load
   - Each message consumed by one consumer per group
   - Different groups receive same messages (pub/sub)

### Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Throughput | 1M+ messages/sec |
| Latency (P99) | <10ms |
| Availability | 99.99% |
| Durability | Messages survive node failures |
| Retention | 7 days default, configurable |
| Max Message Size | 1 MB |

### Scale Estimates

```
Assumptions:
- 1M messages/sec
- Average message size: 10 KB
- Retention: 7 days

Storage required:
1M msg/sec × 10 KB × 86,400 sec/day × 7 days = 6,048 TB = 6.05 PB

With compression (3x): 2 PB

Partitions needed (100K msg/sec per partition):
1M / 100K = 10 partitions minimum
Recommended: 30 partitions (room for growth)

Broker nodes (1 TB SSD each, 3x replication):
2 PB × 3 / 1 TB = 6,000 nodes

Practical deployment:
- 20 brokers (100 TB storage each)
- 30 partitions per topic
- 3x replication factor
```

---

## 3. Core Concepts

### 3.1 Topics and Partitions

**Topic:** Logical channel for messages (e.g., "user-signups", "order-events")

**Partition:** Physical subdivision of topic for parallelism

```
Topic: "orders"
├── Partition 0: [Msg1, Msg4, Msg7, ...]
├── Partition 1: [Msg2, Msg5, Msg8, ...]
└── Partition 2: [Msg3, Msg6, Msg9, ...]
```

**Partitioning Strategy:**
- **Round-robin:** Distribute evenly across partitions
- **Key-based:** Hash(key) % num_partitions (e.g., user_id for ordering)
- **Custom:** Business logic determines partition

---

### 3.2 Consumer Groups

**Problem:** How to scale consumers without duplicate processing?

**Solution:** Consumer groups

```
Topic: "orders" (3 partitions)

Consumer Group "fast-processor":
├── Consumer 1 → Partition 0
├── Consumer 2 → Partition 1
└── Consumer 3 → Partition 2

Consumer Group "slow-processor":
├── Consumer 1 → Partitions 0, 1
└── Consumer 2 → Partition 2

Each group receives ALL messages
Within group, each message processed by ONE consumer
```

---

### 3.3 Message Format

```protobuf
// message.proto
message QueueMessage {
  string id = 1;                    // Unique message ID
  string topic = 2;                 // Topic name
  int32 partition = 3;              // Partition number
  int64 offset = 4;                 // Position in partition
  bytes key = 5;                    // Optional key for partitioning
  bytes value = 6;                  // Message payload
  map<string, string> headers = 7;  // Metadata
  int64 timestamp = 8;              // Creation time (ms)
  int32 retry_count = 9;            // Number of retries
}
```

---

## 4. Architecture

### High-Level Design

```
┌────────────────────────────────────────────────────────────┐
│                        Producers                            │
│       (1000s of services sending messages)                  │
└──────┬───────────┬───────────┬────────────┬────────────────┘
       │           │           │            │
       ▼           ▼           ▼            ▼
┌──────────────────────────────────────────────────────────┐
│                   Message Brokers                         │
│                                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  Broker 1   │  │  Broker 2   │  │  Broker 3   │     │
│  │             │  │             │  │             │      │
│  │ Topic: orders│  │ Topic: orders│  │ Topic: orders│    │
│  │ Partition 0 │  │ Partition 1 │  │ Partition 2 │     │
│  │ [════════]  │  │ [════════]  │  │ [════════]  │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                           │
│  Replication: Each partition replicated 3x                │
│  Leader-Follower: One leader, two followers per partition│
└──────┬───────────┬───────────┬────────────┬──────────────┘
       │           │           │            │
       ▼           ▼           ▼            ▼
┌──────────────────────────────────────────────────────────┐
│                   Consumer Groups                         │
│                                                           │
│  Group "processor":                                       │
│    Consumer 1 → Partition 0                               │
│    Consumer 2 → Partition 1                               │
│    Consumer 3 → Partition 2                               │
│                                                           │
│  Group "analytics":                                       │
│    Consumer 1 → Partitions 0, 1, 2                       │
└───────────────────────────────────────────────────────────┘
```

### Components

1. **Producer:** Sends messages to brokers
2. **Broker:** Stores messages on disk, serves consumers
3. **Consumer:** Reads messages from brokers
4. **ZooKeeper/Raft:** Cluster coordination (leader election, metadata)

---

## 5. Implementation

### 5.1 Message Broker (Go)

```go
// broker/broker.go
package broker

import (
    "fmt"
    "os"
    "sync"
)

type Broker struct {
    id         int
    topics     map[string]*Topic
    mu         sync.RWMutex
    dataDir    string
    replicator *Replicator
}

func NewBroker(id int, dataDir string) *Broker {
    return &Broker{
        id:      id,
        topics:  make(map[string]*Topic),
        dataDir: dataDir,
    }
}

// CreateTopic: Create a new topic with partitions
func (b *Broker) CreateTopic(name string, numPartitions int) error {
    b.mu.Lock()
    defer b.mu.Unlock()
    
    if _, exists := b.topics[name]; exists {
        return fmt.Errorf("topic %s already exists", name)
    }
    
    topic := &Topic{
        name:       name,
        partitions: make([]*Partition, numPartitions),
    }
    
    // Create partitions
    for i := 0; i < numPartitions; i++ {
        partitionDir := fmt.Sprintf("%s/%s/%d", b.dataDir, name, i)
        if err := os.MkdirAll(partitionDir, 0755); err != nil {
            return err
        }
        
        topic.partitions[i] = &Partition{
            id:       i,
            topic:    name,
            dataDir:  partitionDir,
            segments: make([]*Segment, 0),
            mu:       sync.RWMutex{},
        }
        
        // Create initial segment
        if err := topic.partitions[i].createSegment(); err != nil {
            return err
        }
    }
    
    b.topics[name] = topic
    return nil
}

// Publish: Write message to partition
func (b *Broker) Publish(topic string, key []byte, value []byte) (int64, error) {
    b.mu.RLock()
    t, ok := b.topics[topic]
    b.mu.RUnlock()
    
    if !ok {
        return 0, fmt.Errorf("topic %s not found", topic)
    }
    
    // Determine partition
    partitionID := b.getPartition(key, len(t.partitions))
    partition := t.partitions[partitionID]
    
    // Append to partition
    offset, err := partition.Append(key, value)
    if err != nil {
        return 0, err
    }
    
    // Replicate to followers (async)
    go b.replicator.Replicate(topic, partitionID, offset, key, value)
    
    return offset, nil
}

func (b *Broker) getPartition(key []byte, numPartitions int) int {
    if len(key) == 0 {
        // Round-robin if no key
        return int(time.Now().UnixNano()) % numPartitions
    }
    
    // Hash-based partitioning
    h := fnv.New32a()
    h.Write(key)
    return int(h.Sum32()) % numPartitions
}
```

---

### 5.2 Topic and Partition

```go
// broker/topic.go
package broker

type Topic struct {
    name       string
    partitions []*Partition
}

// broker/partition.go
package broker

import (
    "encoding/binary"
    "fmt"
    "os"
    "sync"
    "time"
)

type Partition struct {
    id       int
    topic    string
    dataDir  string
    segments []*Segment
    offset   int64  // Next offset to write
    mu       sync.RWMutex
}

type Segment struct {
    baseOffset int64
    file       *os.File
    index      *Index
    size       int64
    maxSize    int64  // 1 GB default
}

// Append: Write message to partition
func (p *Partition) Append(key []byte, value []byte) (int64, error) {
    p.mu.Lock()
    defer p.mu.Unlock()
    
    // Get current segment
    currentSegment := p.segments[len(p.segments)-1]
    
    // Roll to new segment if current is full
    if currentSegment.size >= currentSegment.maxSize {
        if err := p.createSegment(); err != nil {
            return 0, err
        }
        currentSegment = p.segments[len(p.segments)-1]
    }
    
    // Create message record
    record := p.createRecord(p.offset, key, value)
    
    // Write to segment file
    n, err := currentSegment.file.Write(record)
    if err != nil {
        return 0, err
    }
    
    // Update index (offset → file position)
    currentSegment.index.Add(p.offset, currentSegment.size)
    currentSegment.size += int64(n)
    
    offset := p.offset
    p.offset++
    
    return offset, nil
}

func (p *Partition) createRecord(offset int64, key []byte, value []byte) []byte {
    // Message format:
    // [8 bytes: offset]
    // [8 bytes: timestamp]
    // [4 bytes: key length]
    // [N bytes: key]
    // [4 bytes: value length]
    // [M bytes: value]
    // [4 bytes: CRC32 checksum]
    
    timestamp := time.Now().UnixMilli()
    keyLen := len(key)
    valueLen := len(value)
    
    recordSize := 8 + 8 + 4 + keyLen + 4 + valueLen + 4
    record := make([]byte, recordSize)
    
    pos := 0
    
    // Offset
    binary.BigEndian.PutUint64(record[pos:], uint64(offset))
    pos += 8
    
    // Timestamp
    binary.BigEndian.PutUint64(record[pos:], uint64(timestamp))
    pos += 8
    
    // Key length
    binary.BigEndian.PutUint32(record[pos:], uint32(keyLen))
    pos += 4
    
    // Key
    copy(record[pos:], key)
    pos += keyLen
    
    // Value length
    binary.BigEndian.PutUint32(record[pos:], uint32(valueLen))
    pos += 4
    
    // Value
    copy(record[pos:], value)
    pos += valueLen
    
    // CRC32 checksum
    crc := crc32.ChecksumIEEE(record[:pos])
    binary.BigEndian.PutUint32(record[pos:], crc)
    
    return record
}

func (p *Partition) createSegment() error {
    baseOffset := p.offset
    segmentFile := fmt.Sprintf("%s/%020d.log", p.dataDir, baseOffset)
    indexFile := fmt.Sprintf("%s/%020d.index", p.dataDir, baseOffset)
    
    file, err := os.OpenFile(segmentFile, os.O_CREATE|os.O_RDWR|os.O_APPEND, 0644)
    if err != nil {
        return err
    }
    
    index, err := NewIndex(indexFile)
    if err != nil {
        file.Close()
        return err
    }
    
    segment := &Segment{
        baseOffset: baseOffset,
        file:       file,
        index:      index,
        size:       0,
        maxSize:    1 * 1024 * 1024 * 1024, // 1 GB
    }
    
    p.segments = append(p.segments, segment)
    return nil
}
```

---

### 5.3 Index for Fast Lookups

```go
// broker/index.go
package broker

import (
    "encoding/binary"
    "os"
)

type Index struct {
    file    *os.File
    mmap    []byte  // Memory-mapped file for fast reads
    size    int64
    maxSize int64
}

func NewIndex(filename string) (*Index, error) {
    file, err := os.OpenFile(filename, os.O_CREATE|os.O_RDWR, 0644)
    if err != nil {
        return nil, err
    }
    
    // Preallocate 10 MB
    maxSize := int64(10 * 1024 * 1024)
    if err := file.Truncate(maxSize); err != nil {
        file.Close()
        return nil, err
    }
    
    // Memory-map file (for fast reads)
    mmap, err := syscall.Mmap(
        int(file.Fd()),
        0,
        int(maxSize),
        syscall.PROT_READ|syscall.PROT_WRITE,
        syscall.MAP_SHARED,
    )
    if err != nil {
        file.Close()
        return nil, err
    }
    
    return &Index{
        file:    file,
        mmap:    mmap,
        size:    0,
        maxSize: maxSize,
    }, nil
}

// Add: Add entry to index (offset → file position)
func (idx *Index) Add(offset int64, position int64) error {
    if idx.size+16 > idx.maxSize {
        return fmt.Errorf("index full")
    }
    
    // Write: [8 bytes offset][8 bytes position]
    binary.BigEndian.PutUint64(idx.mmap[idx.size:], uint64(offset))
    binary.BigEndian.PutUint64(idx.mmap[idx.size+8:], uint64(position))
    
    idx.size += 16
    return nil
}

// Lookup: Find file position for offset
func (idx *Index) Lookup(offset int64) (int64, error) {
    // Binary search in index
    numEntries := idx.size / 16
    
    left, right := int64(0), numEntries-1
    
    for left <= right {
        mid := (left + right) / 2
        pos := mid * 16
        
        entryOffset := int64(binary.BigEndian.Uint64(idx.mmap[pos:]))
        
        if entryOffset == offset {
            return int64(binary.BigEndian.Uint64(idx.mmap[pos+8:])), nil
        } else if entryOffset < offset {
            left = mid + 1
        } else {
            right = mid - 1
        }
    }
    
    return 0, fmt.Errorf("offset not found")
}
```

---

### 5.4 Producer Client

```go
// client/producer.go
package client

import (
    "fmt"
    "net"
    "time"
)

type Producer struct {
    brokers []string
    conns   map[string]net.Conn
}

func NewProducer(brokers []string) *Producer {
    return &Producer{
        brokers: brokers,
        conns:   make(map[string]net.Conn),
    }
}

func (p *Producer) Send(topic string, key []byte, value []byte) error {
    // Get leader broker for topic partition
    broker := p.getLeaderBroker(topic, key)
    
    // Get or create connection
    conn, err := p.getConnection(broker)
    if err != nil {
        return err
    }
    
    // Send produce request
    req := &ProduceRequest{
        Topic: topic,
        Key:   key,
        Value: value,
    }
    
    if err := p.sendRequest(conn, req); err != nil {
        return err
    }
    
    // Read response
    resp, err := p.readResponse(conn)
    if err != nil {
        return err
    }
    
    if resp.Error != "" {
        return fmt.Errorf("produce failed: %s", resp.Error)
    }
    
    return nil
}

func (p *Producer) SendAsync(topic string, key []byte, value []byte, callback func(error)) {
    go func() {
        err := p.Send(topic, key, value)
        if callback != nil {
            callback(err)
        }
    }()
}

func (p *Producer) getConnection(broker string) (net.Conn, error) {
    if conn, ok := p.conns[broker]; ok {
        return conn, nil
    }
    
    conn, err := net.DialTimeout("tcp", broker, 5*time.Second)
    if err != nil {
        return nil, err
    }
    
    p.conns[broker] = conn
    return conn, nil
}
```

---

**Continued in next part...**
