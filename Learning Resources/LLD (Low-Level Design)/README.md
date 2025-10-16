# Low-Level Design (LLD) - Complete Interview Prep for 40 LPA SDE-Data

**Target Role:** Senior/Staff Data Engineer (40 LPA+)  
**Total Content:** 6 comprehensive modules  
**Study Time:** 2-3 weeks intensive preparation  
**Level:** Intermediate to Advanced

---

## 📚 Module Overview

This module covers **production-grade low-level design** with:
- ✅ SOLID principles with real-world examples
- ✅ All 23 GoF design patterns with Java implementations
- ✅ Real system design case studies (LRU Cache, Rate Limiter, Parking Lot, etc.)
- ✅ Concurrency patterns for distributed systems
- ✅ Data engineering focus (Spark, Kafka, distributed systems)
- ✅ Thread-safety and performance optimization

---

## 🗺️ Learning Path

### Week 1: Foundational Principles & Creational Patterns

**Day 1-2:** [SOLID Principles](./01-SOLID-PRINCIPLES/PRINCIPLES.md)
- Single Responsibility, Open/Closed, Liskov Substitution
- Interface Segregation, Dependency Inversion
- Real examples from Apache Spark, Kafka

**Day 3-4:** [Creational Patterns](./02-DESIGN-PATTERNS/01-Creational-Patterns.md)
- Singleton, Factory Method, Abstract Factory
- Builder, Prototype
- Spark session creation, Kafka producer configuration

**Day 5-7:** [Structural Patterns](./02-DESIGN-PATTERNS/02-Structural-Patterns.md)
- Adapter, Bridge, Composite, Decorator
- Facade, Flyweight, Proxy
- Data pipeline transformations, caching layers

---

### Week 2: Behavioral Patterns & Case Studies

**Day 8-10:** [Behavioral Patterns](./02-DESIGN-PATTERNS/03-Behavioral-Patterns.md)
- Chain of Responsibility, Command, Iterator, Mediator
- Memento, Observer, State, Strategy, Template Method
- Visitor, Interpreter
- Event processing, state machines, ETL pipelines

**Day 11-14:** [Case Studies](./03-CASE-STUDIES/)
- [LRU Cache](./03-CASE-STUDIES/01-LRU-Cache.md): HashMap + DoublyLinkedList, O(1) operations
- [Rate Limiter](./03-CASE-STUDIES/02-Rate-Limiter.md): Token Bucket, Sliding Window, distributed rate limiting
- [Additional Problems](./03-CASE-STUDIES/03-More-Problems.md):
  * Parking Lot System (State pattern, pricing strategies)
  * URL Shortener (Distributed ID generation, Base62 encoding, consistent hashing)
  * Notification System (Multi-channel, priority queue, retry logic)
  * Distributed Cache (Eviction policies, consistent hashing, replication)

---

### Week 3: Concurrency & Practice

**Day 15-18:** [Concurrency Patterns](./04-CONCURRENCY-PATTERNS/PATTERNS.md)
- Producer-Consumer (BlockingQueue, Kafka-style broker)
- Thread Pool (Executor framework, custom implementation)
- Read-Write Lock (Concurrent cache, time-series DB)
- Semaphore (Connection pool, rate limiter)
- Barrier and Latch (DAG execution, parallel ML training)
- Real Kafka/Spark examples

**Day 19-21:** Practice & Integration
- Design 5 complete systems from scratch
- Explain pattern choices and trade-offs
- Practice whiteboard coding

---

## 🎯 Quick Reference: When to Use Each Pattern

### Creational Patterns

| Pattern | Use Case | Example |
|---------|----------|---------|
| **Singleton** | Single shared instance | SparkSession, Kafka AdminClient |
| **Factory Method** | Object creation without specifying class | Kafka producer/consumer factory |
| **Abstract Factory** | Family of related objects | Cloud provider clients (AWS, GCP, Azure) |
| **Builder** | Complex object with many parameters | Spark configuration, Kafka properties |
| **Prototype** | Clone expensive objects | DataFrame transformations |

### Structural Patterns

| Pattern | Use Case | Example |
|---------|----------|---------|
| **Adapter** | Incompatible interfaces | Legacy system integration |
| **Bridge** | Separate abstraction from implementation | Storage backends (S3, HDFS, local) |
| **Composite** | Tree structures | File system, expression trees |
| **Decorator** | Add behavior dynamically | Stream transformations, caching |
| **Facade** | Simplify complex system | Data pipeline orchestration |
| **Flyweight** | Share common state | String interning, column metadata |
| **Proxy** | Control access | Lazy loading, access control |

### Behavioral Patterns

| Pattern | Use Case | Example |
|---------|----------|---------|
| **Chain of Responsibility** | Sequential processing | ETL pipeline stages |
| **Command** | Encapsulate operations | Database transactions |
| **Iterator** | Traverse collections | Spark RDD/DataFrame iteration |
| **Mediator** | Coordinate objects | Event bus, message broker |
| **Memento** | Save/restore state | Checkpointing in Spark |
| **Observer** | Publish-subscribe | Event streaming, Kafka consumers |
| **State** | Object behavior changes | Connection states (open, closed, error) |
| **Strategy** | Interchangeable algorithms | Compression (gzip, snappy), serialization |
| **Template Method** | Algorithm skeleton | Data processing pipeline template |
| **Visitor** | Operations on object structure | Query plan optimization |

### Concurrency Patterns

| Pattern | Use Case | Example |
|---------|----------|---------|
| **Producer-Consumer** | Async processing | Kafka topics, message queues |
| **Thread Pool** | Reuse threads | Spark task execution |
| **Read-Write Lock** | Concurrent reads | Metadata cache, configuration |
| **Semaphore** | Resource limiting | Connection pool, rate limiting |
| **Barrier** | Synchronize threads | Parallel ML training iterations |
| **CountDownLatch** | Wait for events | DAG stage dependencies |

---

## 💡 SOLID Principles Quick Reference

### Single Responsibility Principle (SRP)

```
❌ Bad: Class handles parsing AND validation AND storage
✅ Good: Separate classes for Parser, Validator, Repository
```

**Real Example:** Kafka Producer
- Producer handles message sending
- Serializer handles data conversion
- Partitioner handles partition selection

### Open/Closed Principle (OCP)

```
❌ Bad: Modify class to add new behavior
✅ Good: Extend through interfaces/abstract classes
```

**Real Example:** Spark DataSource API
- Add new data source without modifying Spark core
- Implement DataSourceV2 interface

### Liskov Substitution Principle (LSP)

```
❌ Bad: Subclass breaks parent class contract
✅ Good: Subclass can replace parent without issues
```

**Real Example:** Collection hierarchy
- ArrayList, LinkedList can substitute List

### Interface Segregation Principle (ISP)

```
❌ Bad: Fat interface with many methods
✅ Good: Multiple focused interfaces
```

**Real Example:** Java I/O
- Readable, Writeable, Closeable (separate interfaces)

### Dependency Inversion Principle (DIP)

```
❌ Bad: Depend on concrete implementations
✅ Good: Depend on abstractions (interfaces)
```

**Real Example:** Repository pattern
- Service depends on Repository interface
- Can swap implementations (MySQL, PostgreSQL, MongoDB)

---

## 📊 Design Pattern Categories

### By Purpose

**Creational (5):** Object creation mechanisms
- Singleton, Factory Method, Abstract Factory, Builder, Prototype

**Structural (7):** Object composition
- Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy

**Behavioral (11):** Object communication
- Chain, Command, Iterator, Mediator, Memento, Observer, State, Strategy, Template, Visitor, Interpreter

### By Frequency in Interviews

**Very High (⭐⭐⭐⭐⭐):**
- Singleton, Factory, Builder
- Decorator, Proxy
- Observer, Strategy, Template Method

**High (⭐⭐⭐⭐):**
- Abstract Factory, Prototype
- Adapter, Facade, Flyweight
- Chain of Responsibility, Command, State

**Medium (⭐⭐⭐):**
- Bridge, Composite
- Iterator, Mediator, Memento, Visitor

**Lower (⭐⭐):**
- Interpreter (rare in data engineering)

---

## 🏢 Company-Specific Focus

### FAANG (Meta, Amazon, Apple, Netflix, Google)

**Design Questions:**
- Design LRU Cache (HashMap + DoublyLinkedList)
- Design Rate Limiter (Token Bucket, Sliding Window)
- Design Parking Lot (State pattern, Strategy for pricing)
- Design URL Shortener (Distributed ID, consistent hashing)

**Pattern Focus:**
- Singleton (lazy initialization, thread-safety)
- Factory (object creation abstraction)
- Observer (event-driven systems)
- Strategy (algorithm selection)

### Data Engineering Specific (Databricks, Snowflake, Confluent)

**Design Questions:**
- Design Data Pipeline Orchestration (Template Method, Chain)
- Design Distributed Cache (Eviction policies, consistent hashing)
- Design Stream Processing System (Producer-Consumer, Backpressure)
- Design Metrics Aggregation (Time-series DB, windowing)

**Pattern Focus:**
- Builder (configuration)
- Decorator (stream transformations)
- Template Method (pipeline stages)
- Producer-Consumer (Kafka-style)

---

## 🚀 Real-World Case Studies

### 1. LRU Cache (Google, Amazon)

**Problem:** Implement cache with O(1) get, put, and eviction

**Solution:**
- HashMap for O(1) lookup
- DoublyLinkedList for O(1) eviction (LRU)
- Maintain head (most recent), tail (least recent)

**Patterns Used:** Composite (HashMap + LinkedList)

**Complexity:**
- get(): O(1)
- put(): O(1)
- Space: O(capacity)

### 2. Rate Limiter (Meta, Stripe)

**Problem:** Limit requests per user per time window

**Solutions:**
- **Token Bucket:** Refill tokens at fixed rate
- **Sliding Window:** Count requests in rolling window
- **Fixed Window:** Reset counter at fixed intervals

**Patterns Used:** Strategy (different algorithms)

**Distributed:** Redis with atomic operations

### 3. Parking Lot System (Amazon, Microsoft)

**Problem:** Multi-floor parking with different vehicle types

**Patterns Used:**
- Factory (vehicle creation)
- State (spot status: available, occupied, reserved)
- Strategy (pricing: hourly, flat, dynamic)
- Singleton (parking lot instance)

**Complexity:**
- parkVehicle(): O(F * S) where F = floors, S = spots
- removeVehicle(): O(1)

### 4. URL Shortener (Google, Bitly)

**Problem:** Convert long URL to short code

**Solutions:**
- **Distributed ID Generation:** Snowflake algorithm
  * 41 bits: timestamp
  * 10 bits: machine ID
  * 12 bits: sequence number
- **Encoding:** Base62 (0-9, a-z, A-Z)
- **Distribution:** Consistent hashing for sharding

**Patterns Used:**
- Factory (encoder), Strategy (encoding algorithms)

**Complexity:**
- createShortUrl(): O(1)
- getLongUrl(): O(1) with cache, O(log n) without

### 5. Notification System (Uber, LinkedIn)

**Problem:** Multi-channel notifications with priority and retry

**Patterns Used:**
- Observer (subscribers)
- Strategy (channels: email, SMS, push, in-app)
- Template Method (common notification flow)
- Chain of Responsibility (retry logic with exponential backoff)

**Concurrency:**
- PriorityBlockingQueue for priority ordering
- ExecutorService for parallel delivery
- Semaphore for rate limiting

### 6. Distributed Cache (Redis, Memcached)

**Problem:** In-memory cache distributed across nodes

**Patterns Used:**
- Strategy (eviction: LRU, LFU, FIFO)
- Singleton (cache instance per node)
- Proxy (routing to nodes)

**Key Techniques:**
- **Consistent Hashing:** Virtual nodes for even distribution
- **Eviction Policies:** LRU (access order), LFU (frequency)
- **Replication:** Master-replica for fault tolerance
- **TTL:** Auto-expiration with background cleanup

---

## 🎓 Interview Preparation Strategy

### Phase 1: Learn Patterns (Week 1)

1. **Understand Intent:** What problem does it solve?
2. **Study Structure:** UML diagram, participants
3. **Implement:** Code from scratch (not copy-paste)
4. **Practice:** Explain trade-offs, when to use/avoid

### Phase 2: Solve Case Studies (Week 2)

1. **LRU Cache:** HashMap + DoublyLinkedList
2. **Rate Limiter:** Token Bucket, Sliding Window
3. **Parking Lot:** State, Strategy, Factory
4. **URL Shortener:** Distributed ID, Base62, consistent hashing
5. **Notification System:** Observer, Strategy, Chain
6. **Distributed Cache:** LRU eviction, consistent hashing

### Phase 3: Practice & Mock Interviews (Week 3)

1. **Whiteboard Practice:** 30-45 minutes per problem
2. **Explain Trade-offs:** Time vs space, simplicity vs extensibility
3. **Handle Follow-ups:** Scalability, fault tolerance, monitoring
4. **Code Quality:** Clean code, edge cases, testing

---

## 🔍 Common Interview Mistakes

### 1. Jumping to Code Too Quickly

```
❌ Bad: Start coding without clarifying requirements

✅ Good:
1. Ask clarifying questions (scale, constraints, functional/non-functional requirements)
2. Discuss high-level approach and alternatives
3. Choose approach and explain trade-offs
4. Then code
```

### 2. Not Discussing Trade-offs

```
❌ Bad: "I'll use a HashMap"

✅ Good:
"We could use:
1. HashMap: O(1) lookup but unordered, no range queries
2. TreeMap: O(log n) lookup but ordered, supports range queries
3. Trie: O(m) lookup where m = key length, good for prefix operations

For this problem, HashMap is best because..."
```

### 3. Ignoring Concurrency

```
❌ Bad: Single-threaded implementation only

✅ Good:
"In production with concurrent access, we need:
1. ConcurrentHashMap for thread-safe cache
2. ReadWriteLock for read-heavy workloads
3. Atomic operations for counters
4. Lock-free data structures where possible"
```

### 4. Not Handling Edge Cases

```
❌ Bad: Assume inputs are always valid

✅ Good:
1. Null/empty checks
2. Boundary conditions (capacity = 0, negative values)
3. Concurrent modification
4. Resource cleanup (finally blocks, try-with-resources)
```

### 5. Poor Code Organization

```
❌ Bad: Everything in one class, long methods

✅ Good:
1. Separate concerns (SRP)
2. Small methods (< 20 lines)
3. Meaningful names
4. Clear interfaces
```

---

## 📖 Recommended Practice Problems

### Must-Solve LLD Problems

**Easy (5):**
1. Design Stack using Queue
2. Design Queue using Stack
3. Min Stack (O(1) getMin)
4. Design HashSet
5. Design HashMap

**Medium (10):**
6. LRU Cache
7. LFU Cache
8. Design File System
9. Design Tic Tac Toe
10. Design Snake Game
11. Design Hit Counter
12. Design Logger Rate Limiter
13. Design In-Memory File System
14. Design Search Autocomplete System
15. Design Leaderboard

**Hard (5):**
16. Design Parking System
17. Design URL Shortener
18. Design Distributed Cache
19. Design Notification System
20. Design Data Pipeline Orchestrator

---

## 🛠️ Code Quality Checklist

### Before Interview

- [ ] Review SOLID principles with examples
- [ ] Implement all 23 GoF patterns from scratch
- [ ] Practice 10+ case studies
- [ ] Study concurrency patterns (Producer-Consumer, Thread Pool, etc.)
- [ ] Prepare questions to ask interviewer

### During Interview

- [ ] Clarify requirements (functional, non-functional)
- [ ] Ask about scale (QPS, data size, users)
- [ ] Discuss high-level approach first
- [ ] Explain trade-offs between alternatives
- [ ] Write clean, modular code
- [ ] Handle edge cases
- [ ] Discuss testing strategy
- [ ] Consider concurrency and thread-safety
- [ ] Explain time/space complexity
- [ ] Discuss how to scale the design

### After Coding

- [ ] Walk through 2-3 examples
- [ ] Discuss potential issues and improvements
- [ ] Explain monitoring and alerting strategy
- [ ] Handle follow-up questions gracefully

---

## 📚 Additional Resources

### Books

- **"Design Patterns: Elements of Reusable Object-Oriented Software"** by Gang of Four
- **"Head First Design Patterns"** by Eric Freeman (beginner-friendly)
- **"Effective Java"** by Joshua Bloch
- **"Java Concurrency in Practice"** by Brian Goetz

### Online Platforms

- **LeetCode:** Design section (200+ problems)
- **System Design Primer:** GitHub repository
- **Refactoring Guru:** Interactive design patterns

### Video Resources

- **Gaurav Sen:** System design YouTube channel
- **TechDummies:** Design patterns explanations
- **Back to Back SWE:** In-depth problem walkthroughs

---

## 🎯 Final Tips for 40 LPA Interviews

### Technical Round

1. **Think Aloud:** Share your thought process
2. **Ask Questions:** Clarify ambiguities before coding
3. **Start Simple:** Basic version first, then optimize
4. **Explain Trade-offs:** Every design decision has pros/cons
5. **Consider Scale:** How would this work with 1M users? 1B?

### Design Round Expectations

**For 40 LPA SDE-Data:**
- **Deep understanding** of distributed systems patterns
- **Real-world experience** with Spark, Kafka, cloud platforms
- **Performance optimization** mindset
- **Trade-off analysis** (consistency vs availability, latency vs throughput)
- **Operational excellence** (monitoring, alerting, debugging)

### Sample Questions to Expect

1. **Design a data pipeline** that processes 1M events/sec from Kafka
2. **Design a distributed cache** with LRU eviction and replication
3. **Design a metrics aggregation system** with 1-second granularity
4. **Design a rate limiter** for an API with 10M users
5. **Design a real-time analytics dashboard** with low latency

### Connecting LLD to Data Engineering

Always relate patterns to real systems:
- **Singleton** → SparkSession, Kafka AdminClient
- **Factory** → DataSource creation (Parquet, CSV, JSON)
- **Builder** → Spark/Kafka configuration
- **Decorator** → DataFrame transformations (map, filter, aggregate)
- **Observer** → Kafka consumer groups, event streaming
- **Strategy** → Compression algorithms (gzip, snappy, lz4)
- **Template Method** → ETL pipeline stages
- **Producer-Consumer** → Kafka topics, message queues

---

## 📅 Daily Study Checklist

```
Day ____ / 21

□ Study 1 design pattern (45 min)
□ Implement pattern from scratch (30 min)
□ Solve 1 LLD problem (60 min)
□ Review concurrency concepts (30 min)
□ Practice explaining pattern to someone (15 min)

Total: ~3 hours/day
```

---

## 🏆 Success Metrics

**After completing this module, you should be able to:**

✅ Implement all 23 GoF patterns from memory  
✅ Design LRU Cache in 15 minutes  
✅ Design Rate Limiter with multiple approaches  
✅ Explain SOLID principles with real examples  
✅ Handle concurrency patterns (Producer-Consumer, Thread Pool)  
✅ Design complete systems (Parking Lot, URL Shortener, Notification)  
✅ Discuss trade-offs between different designs  
✅ Scale designs to millions of users  

---

**Good luck with your interview preparation! 🚀**

*Last Updated: January 2025*  
*Target: 40 LPA SDE-Data Role*  
*Level: Senior/Staff Data Engineer*
