# Week 1: MapReduce & Distributed Systems
## 🏗️ EXPERT - Principal Architect Deep Dive

---

## 🎯 **Learning Objectives**

This section covers Principal/Staff-level understanding:
- Google's production MapReduce architecture
- Performance optimizations and trade-offs
- Why MapReduce limitations led to Spark
- Real-world implementations at scale
- 10 FAANG-level system design questions

---

## 🧩 **1. Principal Architect Depth: MapReduce Internals**

### **Complete Architecture Breakdown**

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT APPLICATION                        │
│  - Submits job (map/reduce functions + input path)         │
│  - Specifies number of map/reduce tasks                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     MASTER NODE                              │
│  Responsibilities:                                           │
│  1. Split input into M map tasks (typically 64MB chunks)    │
│  2. Assign tasks to workers (data locality awareness)       │
│  3. Monitor heartbeats (failure detection)                  │
│  4. Track task states (idle/in-progress/completed)          │
│  5. Schedule R reduce tasks after map completion            │
│  6. Handle stragglers (speculative execution)               │
│                                                              │
│  State:                                                      │
│  - Task ID → Worker location                                │
│  - Task status + progress percentage                        │
│  - Intermediate file locations (M × R)                      │
└─────────────────────────────────────────────────────────────┘
         ↓                                          ↓
┌──────────────────────┐              ┌──────────────────────┐
│   MAP WORKERS (N)    │              │  REDUCE WORKERS (R)  │
│                      │              │                      │
│ Per Task:            │              │ Per Task:            │
│ 1. Read input chunk  │              │ 1. Pull data from    │
│    from GFS          │              │    M map workers     │
│                      │              │    (shuffle/fetch)   │
│ 2. Parse records     │──────────────→│                      │
│                      │  Intermediate │ 2. Merge-sort        │
│ 3. Call map()        │     Files     │    by key            │
│    function          │   (R parts)   │                      │
│                      │              │ 3. Call reduce()     │
│ 4. Partition output  │              │    per key           │
│    into R buckets    │              │                      │
│    (hash-based)      │              │ 4. Write output      │
│                      │              │    to GFS            │
│ 5. Write to local    │              │                      │
│    disk (not GFS!)   │              │                      │
│                      │              │                      │
│ 6. Notify master of  │              │                      │
│    file locations    │              │                      │
└──────────────────────┘              └──────────────────────┘
         ↓                                        ↓
┌──────────────────────────────────────────────────────────────┐
│              GOOGLE FILE SYSTEM (GFS)                        │
│  - Stores input data (replicated 3x)                        │
│  - Stores final output (replicated 3x)                      │
│  - Does NOT store intermediate data (ephemeral)             │
└──────────────────────────────────────────────────────────────┘
```

---

### **Critical Design Decisions & Trade-offs**

#### **Decision 1: Why Store Intermediate Data on Local Disk?**

**Options Considered:**

| Approach | Pros | Cons |
|----------|------|------|
| **Store in GFS (replicated)** | Fault tolerance | 3x network overhead, 3x storage |
| **Store locally (chosen)** | Fast, no network | Lost if worker fails |
| **Stream directly** | No disk I/O | Requires map/reduce in sync |

**Why Local Disk Won:**
- Intermediate data is **ephemeral** (only needed temporarily)
- Network bandwidth is precious (10Gbps shared by 1000s workers)
- If worker fails, just re-run map task (input still in GFS)

**Trade-off:** Slower recovery but **10x better throughput**

---

#### **Decision 2: Pull vs Push for Shuffle**

**Pull Model (Chosen):**
```
Map Workers: Write to disk, notify master
Reduce Workers: Pull from M map workers when ready
```

**Push Model (Not Chosen):**
```
Map Workers: Send data directly to reduce workers
```

**Why Pull Won:**
| Aspect | Pull | Push |
|--------|------|------|
| **Coordination** | Simple (reduce controls) | Complex (M:R synchronization) |
| **Backpressure** | Natural (reduce pulls when ready) | Need explicit flow control |
| **Fault Tolerance** | Reduce can retry fetch | Map needs buffering |

**Key Insight:** Pull gives **reduce workers control** over data flow

---

#### **Decision 3: M and R Configuration**

**Google's Production Rules:**

**Number of Map Tasks (M):**
```
M = Total Input Size / Chunk Size
Chunk Size = 64MB (GFS default)

Example:
  1TB input → M = 16,000 map tasks
```

**Why 64MB chunks?**
- Balances parallelism vs overhead
- Matches GFS block size (efficient I/O)
- Small enough for granular scheduling

**Number of Reduce Tasks (R):**
```
R = Number of output files desired

Typical: R = num_workers × 1.5
  (allows some stragglers without blocking)

Example:
  100 workers → R = 150
```

**Why not R = num_workers?**
- Stragglers would block all workers
- Extra tasks allow load balancing

---

### **Master Node Implementation**

#### **State Management**

```python
class MapReduceMaster:
    def __init__(self):
        # Task tracking
        self.map_tasks = {}      # task_id → MapTask
        self.reduce_tasks = {}   # task_id → ReduceTask
        
        # Worker tracking
        self.workers = {}        # worker_id → Worker
        self.last_heartbeat = {} # worker_id → timestamp
        
        # Intermediate file locations
        self.intermediate_files = defaultdict(list)  # reduce_id → [file_locs]
        
        # State machine
        self.phase = "MAP"  # MAP → SHUFFLE → REDUCE → DONE
    
    def assign_map_task(self, task_id):
        """
        Assign map task with DATA LOCALITY awareness
        """
        input_chunk = self.map_tasks[task_id].input_chunk
        
        # Get GFS chunk locations (3 replicas)
        chunk_locations = self.gfs.get_chunk_locations(input_chunk)
        
        # Priority 1: Worker on same machine as data
        for worker_id in self.idle_workers():
            if worker_id in chunk_locations:
                return self.schedule_task(task_id, worker_id)
        
        # Priority 2: Worker in same rack
        for worker_id in self.idle_workers():
            if self.same_rack(worker_id, chunk_locations):
                return self.schedule_task(task_id, worker_id)
        
        # Priority 3: Any idle worker
        return self.schedule_task(task_id, self.idle_workers()[0])
    
    def handle_heartbeat(self, worker_id, status):
        """
        Process worker heartbeat (every 10 seconds)
        """
        self.last_heartbeat[worker_id] = time.time()
        
        if status.task_completed:
            self.mark_complete(status.task_id)
            
            if status.task_type == "MAP":
                # Store intermediate file locations
                for reduce_id, file_loc in status.output_files:
                    self.intermediate_files[reduce_id].append(file_loc)
        
        elif status.task_failed:
            self.reschedule_task(status.task_id)
    
    def detect_failures(self):
        """
        Run periodically to detect dead workers
        """
        now = time.time()
        TIMEOUT = 60  # seconds
        
        for worker_id, last_seen in self.last_heartbeat.items():
            if now - last_seen > TIMEOUT:
                # Worker is dead, reschedule its tasks
                for task_id in self.get_worker_tasks(worker_id):
                    self.reschedule_task(task_id)
                
                self.mark_worker_dead(worker_id)
    
    def handle_stragglers(self):
        """
        Speculative execution for slow tasks
        """
        if self.percent_complete() < 0.95:
            return  # Only kick in near end
        
        avg_duration = self.average_task_duration()
        
        for task_id, task in self.running_tasks.items():
            if task.duration > avg_duration * 1.5:
                # Task is 50% slower than average
                # Launch backup on different worker
                self.launch_speculative_copy(task_id)
```

---

### **Shuffle Optimization: Combiner**

#### **Without Combiner:**
```
Map Output (100GB):
  ("hello", 1) × 10 million times
  ("world", 1) × 8 million times
  ... millions more

Network Transfer: 100GB
Reduce Input: 100GB
```

#### **With Combiner:**
```
Map Output (100GB)
  ↓ Local Combine
Combiner Output (1MB):
  ("hello", 10000000)
  ("world", 8000000)
  ... 10,000 unique words

Network Transfer: 1MB (100x reduction!)
Reduce Input: 1MB
```

**Implementation:**
```python
class MapWorker:
    def run_map_task(self, input_chunk):
        # Phase 1: Map
        map_output = defaultdict(list)
        for record in input_chunk:
            for key, value in self.map_fn(record):
                map_output[key].append(value)
        
        # Phase 2: Combine locally (if combiner provided)
        if self.combiner_fn:
            combined = {}
            for key, values in map_output.items():
                combined[key] = self.combiner_fn(key, values)
            map_output = {k: [v] for k, v in combined.items()}
        
        # Phase 3: Partition into R buckets
        partitioned = [defaultdict(list) for _ in range(self.num_reduce_tasks)]
        for key, values in map_output.items():
            r = hash(key) % self.num_reduce_tasks
            partitioned[r][key].extend(values)
        
        # Phase 4: Write to local disk
        output_files = []
        for r, partition in enumerate(partitioned):
            file_path = self.write_partition(r, partition)
            output_files.append((r, file_path))
        
        return output_files
```

**When Combiner Works:**
- Associative operations: sum, count, min, max
- **Doesn't work:** median, percentiles, distinct count

---

## 🌍 **2. Real-World Implementations**

### **Google's Production Usage (2004-2010)**

#### **Use Case 1: Web Indexing**

**Problem:** Index 20 billion web pages for search

**MapReduce Pipeline:**
```
1. Extract Links:
   Input: Raw HTML pages
   Map: Extract (source_url, [destination_urls])
   Reduce: Aggregate all outlinks per page

2. Compute PageRank:
   Input: Link graph
   Map: Distribute PageRank to neighbors
   Reduce: Sum incoming PageRank
   (Iterate 10-20 times)

3. Build Inverted Index:
   Input: Parsed web pages
   Map: Extract (word, [doc_id, position])
   Reduce: Build posting list per word

4. Sort by Relevance:
   Input: Inverted index
   Map: (word, doc_id) → relevance score
   Reduce: Sort documents by score
```

**Scale:**
- **Input:** 20TB compressed HTML
- **Intermediate Data:** 400TB (links, parsing artifacts)
- **Output:** 2TB inverted index
- **Workers:** 1,000 machines
- **Duration:** 6 hours end-to-end

---

#### **Use Case 2: Log Analysis at Google**

**Scenario:** Analyze search query logs (1TB/day)

**Job 1: Top Queries**
```python
def map_top_queries(log_line):
    user_id, query, timestamp = parse_log(log_line)
    yield (query, 1)

def reduce_top_queries(query, counts):
    yield (query, sum(counts))

# Post-process: Sort and take top 1000
```

**Job 2: User Session Duration**
```python
def map_session(log_line):
    user_id, action, timestamp = parse_log(log_line)
    yield (user_id, timestamp)

def reduce_session(user_id, timestamps):
    sorted_times = sorted(timestamps)
    duration = sorted_times[-1] - sorted_times[0]
    yield (user_id, duration)
```

**Performance:**
- **Data:** 1TB logs (compressed)
- **Map tasks:** 16,000 (64MB chunks)
- **Reduce tasks:** 1,000
- **Workers:** 200 machines
- **Duration:** 15 minutes

---

### **Facebook's Usage (2008-2012)**

Before Hive, Facebook used raw MapReduce for:

**Use Case: Daily Active Users (DAU)**

```python
def map_dau(event):
    """
    Event: {"user_id": 123, "action": "click", "timestamp": ...}
    """
    date = extract_date(event['timestamp'])
    yield ((date, event['user_id']), 1)

def reduce_dau(key, values):
    date, user_id = key
    # User appeared at least once this day
    yield (date, user_id)

# Second MapReduce to count unique users per day
def map_count_users(record):
    date, user_id = record
    yield (date, 1)

def reduce_count_users(date, counts):
    yield (date, len(set(counts)))  # Distinct count
```

**Scale (2010):**
- **Events/day:** 100 billion
- **Compressed size:** 10TB
- **Output:** Daily metrics (100MB)
- **Cluster:** 2,000 machines
- **Duration:** 30 minutes

**Problem:** Writing MapReduce for every query was tedious
→ Led to **Hive** (SQL on top of MapReduce)

---

### **Yahoo's Hadoop Deployment**

**Grid Statistics (2009):**
- **Machines:** 4,000 nodes
- **Storage:** 40 PB (petabytes!)
- **Jobs/day:** 100,000 MapReduce jobs

**Use Cases:**
1. **Search ranking:** Train ML models on click logs
2. **Ad targeting:** Compute user interests from browsing
3. **Spam detection:** Analyze email patterns
4. **Recommendation:** Collaborative filtering (user-item matrix)

**Notable Job:**
```
Sort 1PB of data:
  - Input: 1 million files
  - Workers: 3,800
  - Duration: 16 hours
  - Set world record (2009)
```

---

## 🔬 **3. Advanced Exploration: Limitations & Evolution**

### **Why MapReduce "Failed" (Sort of)**

#### **Limitation 1: Disk I/O Bottleneck**

**Problem:**
```
Iteration 1:
  Read from HDFS → Map → Shuffle → Reduce → Write to HDFS

Iteration 2:
  Read from HDFS (same data!) → Map → Shuffle → Reduce → Write

For 10 iterations:
  - 10 full disk reads
  - 10 full disk writes
  - Each iteration waits for previous to finish
```

**Impact:**
- PageRank (20 iterations): 6 hours
- ML training (100 iterations): Days!

**Solution: Apache Spark**
```
Iteration 1-10:
  Read from HDFS → Keep in RAM → Process → Write final result

Speedup: 10-100x for iterative algorithms
```

---

#### **Limitation 2: No Inter-Reducer Communication**

**Problem:** Some algorithms need global coordination

**Example: K-Means Clustering**

**Pseudo-code:**
```
1. Initialize K centroids
2. Repeat:
   a. Assign each point to nearest centroid (Map + Reduce)
   b. Compute new centroids (Requires ALL points!)
3. Until converged
```

**MapReduce approach:**
```
Job 1: Assign points to centroids
Job 2: Compute new centroids
Job 3: Assign points to NEW centroids
...

Each job = full disk read/write!
```

**Spark approach:**
```python
points = spark.read.parquet("data")  # Load once
centroids = initialize_centroids()

for iteration in range(100):
    # All in memory!
    assignments = points.map(lambda p: assign_to_centroid(p, centroids))
    centroids = assignments.groupByKey().map(compute_centroid)
```

---

#### **Limitation 3: High Latency**

**MapReduce startup overhead:**
1. Submit job to master (1 second)
2. Master schedules tasks (5 seconds)
3. Workers download JAR files (10 seconds)
4. Workers read data from HDFS (30 seconds)
5. Actual processing (60 seconds)
6. Write output to HDFS (20 seconds)

**Total: 126 seconds, only 60 seconds actual work!**

**For interactive queries:** Unacceptable

**Solution: Spark + Presto/Impala**
- Keep workers warm (no startup delay)
- Keep data in memory (no HDFS read delay)
- Latency: **Sub-second** for simple queries

---

#### **Limitation 4: Only Batch Processing**

**MapReduce cannot handle:**
- Real-time event processing (need seconds, not minutes)
- Stream processing (continuous data)
- Interactive queries

**Solutions:**
- **Streaming:** Apache Storm, Kafka Streams, Flink
- **Interactive:** Apache Drill, Presto, Impala
- **Unified:** Apache Beam (batch + stream)

---

### **When to STILL Use MapReduce (2025)**

Despite limitations, MapReduce is still used for:

1. **One-time batch jobs:**
   - Data migration
   - Historical backfill
   - Ad-hoc analysis

2. **Cost-sensitive workloads:**
   - Spot instances (can handle failures)
   - Pre-emptible VMs
   - Cheap object storage (S3)

3. **Extremely large datasets:**
   - Petabyte-scale ETL
   - Genomics processing
   - Climate simulations

**Modern approach:** Use Spark/Beam for programming model, compile to MapReduce for execution on cheap hardware

---

## 🏆 **4. Performance Optimization Techniques**

### **Optimization 1: Combiner Design**

**Bad Combiner (Defeats Purpose):**
```python
def bad_combiner(key, values):
    # Returns ALL values (no reduction!)
    return (key, values)
```

**Good Combiner (Max Reduction):**
```python
def good_combiner(key, values):
    # Aggregate locally
    return (key, sum(values))
```

**Best Combiner (Approximate):**
```python
from hyperloglog import HyperLogLog

def distinct_count_combiner(key, values):
    hll = HyperLogLog()
    for value in values:
        hll.add(value)
    return (key, hll.serialize())

def distinct_count_reducer(key, hll_sketches):
    merged = HyperLogLog()
    for sketch in hll_sketches:
        merged.merge(HyperLogLog.deserialize(sketch))
    return (key, merged.count())
```

**Benefit:** Approximate distinct count with **fixed memory** (vs exact needs O(n))

---

### **Optimization 2: Custom Partitioner for Sorted Output**

**Default Hash Partitioner:**
```python
def default_partition(key, num_reducers):
    return hash(key) % num_reducers

# Output: Unsorted across reducers
Reducer 0: ["apple", "zebra", "dog"]
Reducer 1: ["cat", "banana", "elephant"]
```

**Range Partitioner (for sorted output):**
```python
class RangePartitioner:
    def __init__(self, num_reducers, sample_keys):
        # Pre-compute split points
        sorted_keys = sorted(sample_keys)
        self.split_points = [
            sorted_keys[i * len(sorted_keys) // num_reducers]
            for i in range(1, num_reducers)
        ]
    
    def partition(self, key, num_reducers):
        # Binary search for correct partition
        return bisect.bisect_left(self.split_points, key)

# Output: Globally sorted!
Reducer 0: ["apple", "banana", "cat"]
Reducer 1: ["dog", "elephant", "zebra"]
```

**Use Case:** Generating sorted datasets for joins

---

### **Optimization 3: Compression**

**Trade-off:** CPU time vs I/O time

**Splittable Compression Formats:**

| Format | Compression | Speed | Splittable |
|--------|-------------|-------|------------|
| **Snappy** | 50% | Very Fast | ❌ |
| **LZO** | 50% | Fast | ✅ (with index) |
| **Bzip2** | 75% | Slow | ✅ |
| **Gzip** | 70% | Medium | ❌ |

**Recommendation:**
- **Map input:** Use splittable (LZO, Bzip2)
- **Intermediate:** Use fast (Snappy, LZ4)
- **Final output:** Use efficient (Gzip, Zstd)

**Example:**
```python
# Configure Hadoop
conf.set("mapreduce.map.output.compress", "true")
conf.set("mapreduce.map.output.compress.codec", "org.apache.hadoop.io.compress.SnappyCodec")

# Result: 10x less shuffle data!
```

---

### **Optimization 4: Memory Management**

**JVM Heap Tuning:**
```bash
# Default (often insufficient)
-Xmx1024m

# Better: Use 80% of machine RAM
-Xmx12g

# Even better: Tune GC
-Xmx12g -XX:+UseG1GC -XX:MaxGCPauseMillis=200
```

**Sort Buffer Size:**
```xml
<property>
  <name>mapreduce.task.io.sort.mb</name>
  <value>512</value>  <!-- Default: 100MB -->
</property>
```

**Impact:** Fewer spills to disk during sort

---

## 💡 **5. FAANG-Level Interview Questions**

### **Question 1: Design a distributed grep using MapReduce**

**Problem:** Search for pattern in 1PB of log files

**Solution:**

**Map:**
```python
def map_grep(file_chunk, pattern):
    for line_num, line in enumerate(file_chunk):
        if pattern in line:
            yield (file_chunk.name, (line_num, line))
```

**Reduce:**
```python
def reduce_grep(filename, matches):
    # Identity reducer (just output)
    for line_num, line in matches:
        yield (filename, line_num, line)
```

**Optimization:**
- **Map-only job** (no reduce needed!)
- Use combiner to limit output
- Early termination if X matches found

**Scale Estimation:**
- 1PB input
- 64MB chunks → 16 million map tasks
- 10,000 workers → 30 minutes (assuming 1GB/s disk)

---

### **Question 2: How would you handle a 99/1 data skew?**

**Scenario:** 
- Total data: 1TB
- One key: 990GB (99%)
- All other keys: 10GB (1%)

**Problem:** Single reducer processes 990GB, others idle!

**Solutions:**

**Solution 1: Salting**
```python
def map_with_salting(record):
    key, value = record
    if key == HOT_KEY:
        # Split across 100 reducers
        salt = random.randint(0, 99)
        yield (f"{key}#{salt}", value)
    else:
        yield (key, value)

def reduce_salted(key, values):
    result = aggregate(values)
    yield (key.split('#')[0], result)

# Second job to merge salted results
```

**Solution 2: Dedicated Reducer**
```python
class SkewAwarePartitioner:
    def partition(self, key, num_reducers):
        if key == HOT_KEY:
            # Assign to last 50 reducers
            return num_reducers // 2 + hash(key) % (num_reducers // 2)
        else:
            return hash(key) % (num_reducers // 2)
```

**Solution 3: Sampling**
```python
# Pre-job: Sample 1% of data to identify hot keys
hot_keys = sample_and_identify_skew(input_data)

# Main job: Handle hot keys specially
```

---

### **Question 3: Explain exactly-once vs at-least-once in MapReduce**

**Answer:**

**MapReduce provides AT-LEAST-ONCE semantics:**

**Scenario:**
```
Map Task 1: 
  1. Processes 1M records
  2. Writes output to disk
  3. Sends "done" to master
  4. Network fails before master receives message

Master's View:
  - Task 1 appears failed
  - Re-schedules on Worker 2

Result:
  - Records processed TWICE
  - Output written TWICE
```

**Why Not Exactly-Once?**
- Would require distributed transactions (expensive)
- Would need to detect duplicate writes

**How to Achieve Exactly-Once Semantics:**

**Option 1: Idempotent Operations**
```python
# Bad: Count += 1 (not idempotent)
def reduce_bad(key, values):
    return (key, len(values))

# Good: Set semantics
def reduce_good(key, values):
    unique_values = set(values)
    return (key, len(unique_values))
```

**Option 2: Deduplication**
```python
def reduce_with_dedup(key, values):
    seen = set()
    count = 0
    for value in values:
        # Assume value has unique ID
        if value.id not in seen:
            seen.add(value.id)
            count += 1
    return (key, count)
```

**Option 3: Transactional Outputs**
- Use database with UPSERT semantics
- Write with deterministic keys
- Re-execution overwrites (idempotent)

---

### **Question 4: How does speculative execution work? Trade-offs?**

**Answer:**

**Algorithm:**
```python
class Master:
    def monitor_tasks(self):
        if self.job_progress() < 0.95:
            return  # Only near end
        
        avg_time = self.average_task_duration()
        
        for task in self.running_tasks:
            if task.duration > avg_time * 1.2:  # 20% slower
                # Launch backup copy
                self.launch_backup(task)
    
    def handle_completion(self, task_id, worker_id):
        # First to complete wins
        if task_id not in self.completed:
            self.completed.add(task_id)
            self.mark_success(task_id, worker_id)
            
            # Kill other copies
            for copy in self.get_task_copies(task_id):
                if copy.worker != worker_id:
                    self.kill_task(copy)
```

**Trade-offs:**

**Pros:**
- Handles stragglers (bad disk, CPU throttling)
- Reduces tail latency
- Google reports **44% speedup** in production

**Cons:**
- Wastes resources (duplicate computation)
- Can amplify cluster load
- Not suitable for resource-constrained clusters

**When to Disable:**
- Spot instances (cost-sensitive)
- Limited cluster capacity
- Tasks with side effects (database writes)

---

### **Question 5: Compare MapReduce vs Spark for joining two datasets**

**Scenario:** Join 100GB users with 1TB events

**MapReduce Approach (Reduce-Side Join):**
```python
def map_join(record):
    if record.type == "USER":
        yield (record.user_id, ("USER", record))
    else:  # EVENT
        yield (record.user_id, ("EVENT", record))

def reduce_join(user_id, records):
    user_data = None
    events = []
    
    for record_type, record in records:
        if record_type == "USER":
            user_data = record
        else:
            events.append(record)
    
    for event in events:
        yield join_records(user_data, event)

# Performance:
# - Duration: 30 minutes
# - Shuffle: 1.1TB (entire dataset)
# - Disk I/O: 2.2TB read + 2.2TB write
```

**Spark Approach (Broadcast Join):**
```python
# Load small dataset (users) into memory
users = spark.read.parquet("users").broadcast()

# Load large dataset (events)
events = spark.read.parquet("events")

# Join (small table broadcasted to all workers)
result = events.join(users, "user_id")

# Performance:
# - Duration: 5 minutes (6x faster!)
# - Shuffle: 0 (broadcast, no shuffle!)
# - Disk I/O: 1TB read + 1TB write
```

**When MapReduce Wins:**
- Both datasets are huge (can't broadcast)
- One-time job (Spark setup overhead not worth it)
- Cluster has limited RAM

**When Spark Wins:**
- Interactive queries (reuse loaded data)
- Iterative processing
- One small table (broadcast join)

---

### **Question 6: Design a system to compute top 1M most common words from 1PB corpus**

**Approach 1: Two-Pass MapReduce**

**Job 1: Word Count**
```python
def map_count(document):
    for word in document.split():
        yield (word, 1)

def reduce_count(word, counts):
    yield (word, sum(counts))

# Output: (word, count) for all words
```

**Job 2: Top 1M**
```python
def map_top_k(word, count):
    # Use single key to force one reducer
    yield ("ALL", (word, count))

def reduce_top_k(key, word_counts):
    import heapq
    
    # Heap of size 1M
    heap = []
    for word, count in word_counts:
        if len(heap) < 1_000_000:
            heapq.heappush(heap, (count, word))
        elif count > heap[0][0]:
            heapq.heapreplace(heap, (count, word))
    
    # Return sorted
    for count, word in sorted(heap, reverse=True):
        yield (word, count)
```

**Problem:** Job 2 has single reducer (bottleneck!)

---

**Approach 2: Streaming Top-K (Better)**

**Add Combiner to Job 1:**
```python
def combiner_top_k(key, word_counts):
    # Keep top 1M per mapper
    return top_k_local(word_counts, k=1_000_000)

# Now Job 2 processes much less data:
#   - Input: M × 1M words (M = num mappers)
#   - vs Full word list (billions)
```

**Approach 3: Approximate (Fastest)**
```python
from count_min_sketch import CountMinSketch

def map_approx(document):
    sketch = CountMinSketch()
    for word in document.split():
        sketch.add(word)
    yield ("SKETCH", sketch)

def reduce_approx(key, sketches):
    merged = CountMinSketch()
    for sketch in sketches:
        merged.merge(sketch)
    
    # Estimate counts (small error)
    return merged.top_k(1_000_000)

# Benefit: Fixed memory, ~1% error
```

---

### **Question 7: How would you implement a distributed sort?**

**TeraSort Algorithm:**

**Phase 1: Sampling**
```python
# Sample ~0.1% of data
samples = sample_input(input_data, sample_rate=0.001)

# Compute partition boundaries
sorted_samples = sorted(samples)
num_reducers = 1000

partition_boundaries = [
    sorted_samples[i * len(sorted_samples) // num_reducers]
    for i in range(1, num_reducers)
]
```

**Phase 2: Map (Partition)**
```python
def map_sort(record):
    # Find correct partition via binary search
    partition_id = bisect.bisect_left(partition_boundaries, record.key)
    yield (partition_id, record)
```

**Phase 3: Reduce (Local Sort)**
```python
def reduce_sort(partition_id, records):
    # Sort records within partition
    sorted_records = sorted(records, key=lambda r: r.key)
    for record in sorted_records:
        yield record

# Output: Globally sorted!
#   Partition 0: [0...999]
#   Partition 1: [1000...1999]
#   ...
```

**Performance:**
- 1PB data sorted in **16 hours** (Yahoo, 2009)
- Modern: 1PB in **6 hours** (100 Gbps networks)

---

### **Question 8: Explain the shuffle phase in detail**

**Answer:**

**Complete Shuffle Workflow:**

```
MAP WORKER:
1. map() emits (key, value) pairs → in-memory buffer
2. When buffer full (100MB) → sort by key → spill to disk
3. Repeat until all records processed
4. Merge all spills → sorted runs per partition
5. Write R files (one per reduce partition)
6. Notify master: "I have data for reducers [0..R-1] at locations [...]"

MASTER:
7. Collect file locations from all M map workers
8. When all maps done, notify reduce workers

REDUCE WORKER:
9. HTTP GET from M map workers (fetch partition R)
10. Merge-sort M sorted streams into one
11. Group consecutive keys together
12. Call reduce(key, [values])
```

**ASCII Diagram:**
```
Map Worker 1:
  Buffer: [("apple", 1), ("zebra", 1), ("apple", 1)]
    ↓ sort
  Disk:   [("apple", 2), ("zebra", 1)]
    ↓ partition
  Part 0: [("apple", 2)]  ──┐
  Part 1: [("zebra", 1)]  ──┼─→ To Reducers
                            │
Map Worker 2:               │
  Part 0: [("banana", 3)] ──┤
  Part 1: [("yellow", 1)] ──┘

Reduce Worker 0:
  Fetch Part 0 from all mappers
  Merge: [("apple", 2), ("banana", 3)]
  Reduce: ("apple", 2), ("banana", 3)
```

**Bottlenecks:**
1. **Network:** All-to-all communication (M → R)
2. **Disk:** Write M × R files
3. **Sort:** Each mapper sorts independently

---

### **Question 9: How do you handle schema evolution in MapReduce?**

**Problem:** Input data format changes over time

**Example:**
```json
// Old format
{"user_id": 123, "action": "click"}

// New format (added timestamp)
{"user_id": 123, "action": "click", "timestamp": "2025-01-01"}
```

**Solutions:**

**Solution 1: Versioned Schemas**
```python
def map_versioned(record):
    if "timestamp" in record:
        # New format
        timestamp = record["timestamp"]
    else:
        # Old format (default value)
        timestamp = "UNKNOWN"
    
    yield (record["user_id"], (record["action"], timestamp))
```

**Solution 2: Avro (Recommended)**
```python
from avro.datafile import DataFileReader
from avro.io import DatumReader

def map_avro(avro_file):
    reader = DataFileReader(avro_file, DatumReader())
    for record in reader:
        # Avro handles schema evolution
        timestamp = record.get("timestamp", "UNKNOWN")
        yield (record["user_id"], (record["action"], timestamp))
```

**Solution 3: Separate Jobs per Version**
```python
# Process old data
old_data = input_data.filter(lambda r: "timestamp" not in r)
old_results = old_data.mapReduce(map_old, reduce_old)

# Process new data
new_data = input_data.filter(lambda r: "timestamp" in r)
new_results = new_data.mapReduce(map_new, reduce_new)

# Merge results
final = old_results.union(new_results)
```

---

### **Question 10: Design a real-time ad-hoc query system using MapReduce**

**Problem:** Users want to run SQL queries on 1PB data with <1 minute latency

**Why Raw MapReduce Fails:**
- Job startup: 10-30 seconds
- Data scan: Minutes for PB scale
- No indexes, no caching

**Hybrid Solution:**

**Architecture:**
```
┌────────────────────────────────────────┐
│      Query Interface (SQL)             │
│  Parse → Optimize → Compile to MR      │
└────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────┐
│    Pre-aggregated Cubes (OLAP)         │
│  - Hourly rollups                      │
│  - Common dimensions                   │
│  Fast: <1 second for 80% of queries   │
└────────────────────────────────────────┘
              ↓ (Cache miss)
┌────────────────────────────────────────┐
│    Columnar Storage (Parquet)          │
│  - Partitioned by date                 │
│  - Sorted by common filters            │
│  - Compression + predicate pushdown    │
│  Medium: 10-60 seconds                 │
└────────────────────────────────────────┘
              ↓ (Complex query)
┌────────────────────────────────────────┐
│    Full MapReduce Scan                 │
│  - Ad-hoc queries                      │
│  - Custom UDFs                         │
│  Slow: 5-30 minutes                    │
└────────────────────────────────────────┘
```

**Techniques:**

1. **Partitioning:**
   ```
   /data/year=2025/month=01/day=15/*.parquet
   Query: WHERE date = '2025-01-15'
   → Scan only 1 day's data (vs full 1PB)
   ```

2. **Indexing:**
   ```
   Secondary index: user_id → [file1:offset1, file2:offset2]
   Query: WHERE user_id = 123
   → Read only relevant files
   ```

3. **Caching:**
   ```
   Cache hot data in memory (SSD)
   LRU eviction
   ```

4. **Pre-computation:**
   ```
   Materialized views for common queries
   Update incrementally (overnight batch)
   ```

**Real-World Examples:**
- **Apache Hive** (Facebook): SQL on MapReduce
- **Apache Drill** (MapR): Interactive queries
- **Presto** (Facebook): Distributed SQL engine

---

## 🎯 **Summary: Principal-Level Insights**

**Key Takeaways:**

1. **MapReduce revolutionized big data** but has limitations
2. **Data locality** is the core optimization
3. **Shuffle is the bottleneck** (combiner helps!)
4. **Fault tolerance via re-execution** (trade-off vs performance)
5. **Stragglers handled by speculative execution**
6. **Modern systems (Spark, Flink) evolved from MR limitations**

**When to Use:**
- One-time batch jobs
- Cost-sensitive workloads
- Petabyte-scale ETL

**When NOT to Use:**
- Interactive queries → Presto/Spark
- Real-time streaming → Flink/Kafka Streams
- Iterative ML → Spark MLlib

---

**Next:**
- 📄 [WHITEPAPERS](./WHITEPAPERS.md) - MapReduce (2004) & GFS (2003) papers fully digested

**Congratulations!** You now understand MapReduce at a Principal Engineer level. 🎉
