# Week 1: MapReduce & Distributed Systems
## 📄 WHITEPAPERS - Academic Foundations Digested

---

## 🎯 **Overview**

This section provides **complete summaries** of the foundational papers that shaped distributed data processing. You don't need to read the original papers—everything essential is here.

**Papers Covered:**
1. **MapReduce: Simplified Data Processing on Large Clusters** (Google, 2004)
2. **The Google File System** (Google, 2003)
3. **Bigtable: A Distributed Storage System** (Google, 2006)

---

## 📘 **Paper 1: MapReduce (2004)**

### **Citation**
Jeffrey Dean and Sanjay Ghemawat. "MapReduce: Simplified Data Processing on Large Clusters." *OSDI 2004*.

### **Historical Context**

**The Problem (Early 2000s):**
- Google had **hundreds of terabytes** of web crawl data
- Needed to build search index, compute PageRank, analyze logs
- Existing approach: **Write custom distributed programs** for each task
  - Complex: Handle failures, load balancing, network communication
  - Error-prone: Subtle bugs in distributed systems
  - Non-reusable: Each engineer reinvented the wheel

**The Insight:**
Many computations follow a common pattern:
```
1. Apply operation to each record (MAP)
2. Group by key (SHUFFLE)
3. Aggregate grouped values (REDUCE)
```

**The Solution:**
Abstract this pattern into a framework → **MapReduce**

---

### **Key Innovations**

#### **Innovation 1: Automatic Parallelization**

**Before MapReduce:**
```c++
// Engineer must manually:
- Split input across machines
- Handle network communication
- Detect and recover from failures
- Load balance work

// 1000+ lines of boilerplate code!
```

**With MapReduce:**
```c++
// Engineer writes only:
void map(String key, String value) {
  // Process one record
  EmitIntermediate(new_key, new_value);
}

void reduce(String key, Iterator values) {
  // Aggregate values for one key
  Emit(key, Aggregate(values));
}

// 20 lines of business logic!
```

**Framework handles all the hard parts automatically.**

---

#### **Innovation 2: Bring Compute to Data**

**Conventional Approach:**
```
Storage Cluster → Network → Compute Cluster
  (100 MB/s disk)   (10 MB/s)   (process)

Bottleneck: Network is 10x slower than disk!
```

**MapReduce Approach:**
```
Compute + Storage co-located
Node 1: [Disk] + [CPU] → Process locally
Node 2: [Disk] + [CPU] → Process locally

Network used only for shuffle phase
```

**Result:** **10x throughput improvement**

---

#### **Innovation 3: Fault Tolerance via Re-execution**

**Key Insight:** If computation is **deterministic**, can just re-run failed tasks

**Mechanism:**
```
Master tracks task states:
  - Idle
  - In-Progress (assigned to worker)
  - Completed

Worker sends heartbeat every 10 seconds

If worker fails:
  1. Master detects (no heartbeat)
  2. Mark all tasks on that worker as idle
  3. Reschedule on different workers
  4. Workers re-execute from scratch
```

**Why This Works:**
- Input data replicated in GFS (3 copies)
- Map/Reduce functions are deterministic
- No distributed transactions needed

**Trade-off:**
- Simpler than alternatives (checkpointing, logging)
- Slightly slower recovery
- Google chose simplicity over speed

---

### **Programming Model Details**

#### **User-Specified Functions**

```c++
// 1. MAP FUNCTION
// Input: (key1, value1)
// Output: list of (key2, value2)
map(String input_key, String input_value):
  // Example: Word count
  for each word w in input_value:
    EmitIntermediate(w, "1");

// 2. REDUCE FUNCTION  
// Input: (key2, list of value2)
// Output: (key2, aggregated_value)
reduce(String output_key, Iterator intermediate_values):
  // Example: Sum counts
  int result = 0;
  for each v in intermediate_values:
    result += ParseInt(v);
  Emit(output_key, AsString(result));
```

#### **Execution Flow**

```
1. Input Reader:
   - Split input files into M chunks (typically 64MB)
   - Each chunk = one map task

2. Map Phase:
   - M map tasks run in parallel
   - Each reads one chunk, applies map(), writes R local files
   - Partition function: hash(key) % R

3. Shuffle (built-in):
   - Framework copies intermediate data from map workers to reduce workers
   - Group by key

4. Reduce Phase:
   - R reduce tasks run in parallel
   - Each processes one partition, applies reduce(), writes output

5. Output:
   - R output files (can optionally merge)
```

---

### **Implementation Details from the Paper**

#### **Master Data Structures**

```c++
class Master {
  // For each map task:
  struct MapTask {
    State state;  // idle, in-progress, completed
    Worker* worker;  // which worker it's on
    vector<FileLocation> output_files;  // R files
  };
  
  // For each reduce task:
  struct ReduceTask {
    State state;
    Worker* worker;
    vector<FileLocation> input_files;  // from M map tasks
  };
  
  map<int, MapTask> map_tasks_;
  map<int, ReduceTask> reduce_tasks_;
};
```

#### **Worker Responsibilities**

**Map Worker:**
1. Read input chunk from GFS
2. Parse into records
3. Call user's `map()` function
4. Buffer output in memory
5. Periodically flush to local disk (R partitions)
6. Notify master of file locations

**Reduce Worker:**
1. Master tells: "Read partition X from these M files"
2. HTTP GET from each map worker
3. Merge-sort incoming data by key
4. For each unique key:
   - Gather all values
   - Call user's `reduce()` function
5. Write output to GFS

---

### **Performance Optimizations**

#### **Optimization 1: Locality Awareness**

**Scheduling Algorithm:**
```python
def assign_map_task(task):
    input_chunk = task.input_chunk
    locations = gfs.get_chunk_locations(input_chunk)  # 3 replicas
    
    # Priority 1: Same machine as data
    for worker in idle_workers:
        if worker.machine in locations:
            return assign(task, worker)
    
    # Priority 2: Same rack (1 hop)
    for worker in idle_workers:
        if same_rack(worker, locations):
            return assign(task, worker)
    
    # Priority 3: Any idle worker
    return assign(task, random.choice(idle_workers))
```

**Impact:** 
- Local reads: **~100 MB/s**
- Same-rack: **~50 MB/s**
- Cross-rack: **~10 MB/s**

Paper reports: **~95% of map tasks read data locally!**

---

#### **Optimization 2: Combiner**

**Problem:** Word count produces **massive** intermediate data

**Example:**
```
1 million documents, each has "the" 100 times
Map output: 100 million × ("the", 1)
Shuffle: 100M records × 20 bytes = 2GB just for one word!
```

**Solution:** Local aggregation before shuffle

```c++
// User specifies combiner (same as reduce for word count)
void combiner(String key, Iterator values) {
  int sum = 0;
  for each v in values:
    sum += ParseInt(v);
  EmitIntermediate(key, AsString(sum));
}

// Now:
Map output: ("the", 100000000)  // One record!
Shuffle: 20 bytes (vs 2GB)
```

**Paper Results:** 
- Reduced network traffic by **50-90%** for many workloads
- Critical for scalability

---

#### **Optimization 3: Backup Tasks**

**Problem:** Stragglers (slow tasks) delay job completion

**Causes:**
- Bad disk (slow reads)
- CPU throttled by other jobs
- Network congestion

**Solution:** Near end of job, launch backup copies

```python
def monitor_progress():
    if job_progress < 0.95:
        return
    
    avg_time = compute_average_task_time()
    
    for task in running_tasks:
        if task.runtime > avg_time * 1.5:
            # Launch backup
            backup = schedule_on_different_machine(task)
            
            # First to finish wins
            wait_for_any([task, backup])
```

**Paper Results:**
- Improved job completion time by **44%** in production!
- Critical insight: Most jobs dominated by tail latency

---

### **Real-World Results from the Paper**

#### **Experiment 1: Grep (1TB)**

**Task:** Search for a pattern in 1TB of data

**Configuration:**
- Cluster: 1800 machines
- Input: 1TB (10^10 records)
- Map tasks: 15,000
- Reduce tasks: 1 (just output matches)

**Results:**
- Total time: **150 seconds**
- Throughput: **7 GB/s** cluster-wide
- Peak network: **10 Gbps**

**Analysis:**
- Most time in startup (30s)
- Actual grep: 80s
- Speedup: **~800x** vs single machine

---

#### **Experiment 2: Sort (1TB)**

**Task:** Sort 1TB of data

**Configuration:**
- Input: 1TB (10^12 100-byte records)
- Map tasks: 15,000 (no-op, just partition)
- Reduce tasks: 4,000 (sort locally)

**Results:**
- Total time: **891 seconds**
- Breakdown:
  - Startup: 60s
  - Read input: 200s
  - Shuffle: 400s (bottleneck!)
  - Sort + Write: 231s

**Key Insight:** Shuffle dominates for data-intensive workloads

---

#### **Experiment 3: With Failures**

**Scenario:** Kill 200 workers mid-job (out of 1800)

**Results:**
- Without failures: 891s
- With 200 killed: 933s (only +5% slower!)

**Why So Resilient?**
- Failed map tasks detected in 10s
- Re-scheduled immediately
- Rest of cluster continues working

---

### **Limitations (Acknowledged in Paper)**

#### **Limitation 1: Not Suitable for Everything**

**Works well:**
- Batch processing
- Embarrassingly parallel tasks
- Stateless transformations

**Does NOT work well:**
- Iterative algorithms (machine learning)
- Real-time processing
- Tasks requiring shared state

**Quote from paper:**
> "MapReduce is not suitable for all problems. It works best for tasks that can be divided into independent subtasks."

---

#### **Limitation 2: High Latency**

**Minimum job latency:** ~10 seconds (startup overhead)

**Not suitable for:**
- Interactive queries
- Low-latency serving
- Sub-second analytics

**Led to:** Dremel (BigQuery), Presto, Impala

---

#### **Limitation 3: Inefficient for Iterations**

**Example: K-Means (100 iterations)**

```
MapReduce:
  Each iteration:
    - Read data from GFS (100s)
    - Compute (10s)
    - Write to GFS (100s)
  Total: 100 iterations × 210s = 5.8 hours

Spark (in-memory):
  Load once (100s)
  Iterate in RAM (100 × 10s = 16 mins)
  Total: ~18 minutes (20x faster!)
```

**Led to:** Apache Spark

---

### **Industry Impact**

**Immediate Impact (2004-2010):**
- Google: Built entire search infrastructure on MapReduce
- Yahoo: Created Hadoop (open-source clone)
- Facebook: Processed 100s of PB with Hive (SQL on MapReduce)

**Long-term Impact (2010-2025):**
- Inspired Spark, Flink, Beam
- Established "functional programming on data" paradigm
- Shifted industry from scale-up to scale-out

**Citation Count:** 15,000+ citations (one of most influential CS papers)

---

## 📘 **Paper 2: The Google File System (2003)**

### **Citation**
Sanjay Ghemawat, Howard Gobioff, and Shun-Tak Leung. "The Google File System." *SOSP 2003*.

### **Why This Paper Matters**

MapReduce **depends on** GFS for:
- Storing input data
- Storing output data
- Fault tolerance (replication)

**GFS enabled** data-intensive computing at Google scale.

---

### **Design Assumptions (Key Insight)**

Google's workload is **different** from traditional file systems:

**Assumption 1: Failures are the norm**
- Thousands of commodity machines
- Component failures daily
- Need automatic recovery

**Assumption 2: Files are huge**
- Multi-GB files common
- Optimize for large sequential reads/writes
- Small random reads OK but not primary

**Assumption 3: Append-heavy workload**
- Most writes append data
- Random overwrites rare
- No need for POSIX semantics

**Assumption 4: Co-designing apps and FS**
- Apps can tolerate relaxed consistency
- Apps handle failures explicitly

---

### **Architecture Overview**

```
┌────────────────────────────────────────────────────┐
│              MASTER (Single)                       │
│  - Namespace (file → chunk mapping)               │
│  - Chunk placement (chunk → servers)              │
│  - Replication decisions                          │
│  - Garbage collection                             │
│                                                    │
│  In-Memory State:                                  │
│    - File namespace (directory tree)              │
│    - File → [chunk handles]                       │
│    - Chunk → [chunkserver locations]              │
│                                                    │
│  Persistent State (operation log):                │
│    - Namespace mutations                          │
│    - Chunk version numbers                        │
└────────────────────────────────────────────────────┘
                       ↓ (metadata queries)
┌────────────────────────────────────────────────────┐
│            CHUNKSERVERS (1000s)                    │
│  - Store 64MB chunks as Linux files               │
│  - Serve data directly to clients                 │
│  - Report chunk status to master (heartbeat)      │
│                                                    │
│  Example:                                          │
│    /gfs/data/chunk_123 (64MB Linux file)          │
│    /gfs/data/chunk_456 (64MB Linux file)          │
└────────────────────────────────────────────────────┘
                       ↓ (data read/write)
┌────────────────────────────────────────────────────┐
│              CLIENTS (MapReduce workers)           │
│  - Link with GFS client library                   │
│  - Ask master for metadata                        │
│  - Talk directly to chunkservers for data         │
└────────────────────────────────────────────────────┘
```

---

### **Key Design Decisions**

#### **Decision 1: Large Chunk Size (64 MB)**

**Why so large?** (Traditional FS uses 4KB blocks)

**Advantages:**
1. **Fewer metadata entries**
   - 1TB file = 16,000 chunks (vs 250M blocks at 4KB)
   - Master can keep all metadata in RAM

2. **Fewer client-master interactions**
   - Read 1GB file = 16 requests (vs 250M!)

3. **Amortized network overhead**
   - Single TCP connection per chunk
   - Reduced connection setup costs

**Disadvantages:**
1. **Internal fragmentation**
   - 1KB file wastes 64MB - 1KB
   - **Mitigation:** Not an issue for Google (all files huge)

2. **Hot spots**
   - Many clients accessing same chunk
   - **Mitigation:** Increase replication for hot files

---

#### **Decision 2: Single Master**

**Why?** Simplifies design enormously

**Advantages:**
- **Simple:** All placement decisions centralized
- **Global knowledge:** Master sees entire cluster state
- **No distributed consensus** for metadata

**Disadvantage:** Potential bottleneck

**Mitigation:**
1. **Metadata only (not data)**
   - Clients ask master: "Where is chunk X?"
   - Master replies: "Servers A, B, C"
   - Client reads directly from servers
   - Master not in critical path!

2. **Large chunk size**
   - Fewer metadata requests

3. **Client caching**
   - Cache chunk locations
   - Batch multiple chunk lookups

**Result:** Master handles **~500-1000 ops/sec** (sufficient for Google 2003)

---

#### **Decision 3: No POSIX, Relaxed Consistency**

**Traditional FS guarantees:**
- After write completes, all readers see new data
- Writes are atomic
- Strict ordering

**GFS guarantees:**
- After write completes, **writer** sees new data
- Other readers might see old/new/mixed
- Relaxed atomicity for appends

**Why?**
- Strict consistency requires **distributed locking** (expensive!)
- Google's apps can handle eventual consistency

**How apps cope:**
```python
# MapReduce writes checkpoint files
# If file corrupted, just re-run task

# Bigtable uses checksums
# Detect corruption, retry read
```

---

### **Read Path**

```
1. Client: "Read /data/file.txt offset 100MB"

2. Client → Master:
   "Which chunk contains offset 100MB of /data/file.txt?"
   
3. Master → Client:
   "Chunk handle: 0x123456
    Locations: [server1, server2, server3]
    Version: 5"
   
4. Client → server1 (nearest):
   "Give me chunk 0x123456, bytes 0-1MB"
   
5. server1 → Client:
   [raw data bytes]

6. Client caches:
   - Chunk handle 0x123456 → [server1, server2, server3]
   - Future reads of same chunk: skip master!
```

**Key:** Master only involved in **metadata**, not data transfer

---

### **Write Path (Append)**

**Most common operation:** Append to log file

```
1. Client: "Append 1MB record to /logs/access.log"

2. Client → Master:
   "Which chunk is the last chunk of /logs/access.log?"
   
3. Master → Client:
   "Chunk 0xABCDEF
    Primary: server1
    Secondaries: [server2, server3]"

4. Client → ALL replicas (server1, 2, 3):
   Push data (pipeline for efficiency)
   
5. Client → Primary (server1):
   "Append this data (already pushed)"
   
6. Primary:
   - Assigns serial number to operation
   - Appends locally
   - Forwards request to secondaries
   
7. Secondaries:
   - Append at same offset
   - Reply to primary
   
8. Primary → Client:
   "Success" or "Failed" (if any replica failed)

9. On failure:
   - Client retries (possibly different chunk)
```

**Key Innovation: Pipelined Data Transfer**
```
Client → server1 → server2 → server3

vs

Client → server1
Client → server2  
Client → server3

Pipelined: Uses full bandwidth (100 MB/s)
Parallel: Limited by client NIC (10 MB/s)
```

---

### **Fault Tolerance**

#### **Chunk Replication**

**Default:** 3 replicas per chunk

**Master monitors:**
- Chunkserver heartbeats (every few seconds)
- If chunkserver dies → mark chunks as under-replicated
- Schedule re-replication to restore 3 copies

**Priority:**
1. **Recently deleted files** (higher risk)
2. **Under-replicated chunks** (fewer than 3 copies)
3. **Over-replicated chunks** (more than 3, waste space)

---

#### **Master Reliability**

**Problem:** Single point of failure!

**Solution 1: Operation Log + Checkpoints**
```
Master state:
  - In-memory: Full namespace + chunk locations
  - Persistent: Operation log (all mutations)

Recovery:
  1. Replay operation log from last checkpoint
  2. Query chunkservers for chunk locations
  3. Rebuild in-memory state
  4. Resume operations
```

**Solution 2: Shadow Masters (Read-Only)**
- Multiple replicas of master
- Slightly behind (lag a few seconds)
- Can serve read-only requests
- If primary fails, promote shadow

---

### **Garbage Collection**

**Lazy deletion:**

```
1. User deletes file:
   - Master renames file to hidden name (".trash/file.txt.12345")
   - Returns immediately

2. Background cleanup (runs periodically):
   - Delete hidden files older than 3 days
   - Inform chunkservers to delete chunks
   
3. Chunkservers:
   - Report chunks to master (heartbeat)
   - Master replies: "Chunk X deleted, remove it"
   - Chunkserver deletes local file
```

**Why lazy?**
- Simpler than eager (no distributed transactions)
- Handles failures gracefully (no orphan chunks)
- Batches cleanup (efficient)

---

### **Performance Numbers from Paper**

**Cluster Setup (2003):**
- 1 master, 16 chunkservers, 16 clients
- Each machine: 1 Gbps NIC, dual processors

**Read Performance:**
- **Single client:** 10 MB/s (limited by client NIC)
- **16 clients:** 94 MB/s aggregate (6 MB/s each)
- **Bottleneck:** Network switches

**Write Performance:**
- **Single client:** 6.3 MB/s (3 replicas = 18.9 MB/s total)
- **16 clients:** 67 MB/s aggregate
- **Bottleneck:** Writing 3 copies

**Append Performance:**
- **16 clients:** 48 MB/s
- **Why slower than write?** Synchronization at primary

---

### **Industry Impact**

**Immediate:**
- Enabled Google to process petabytes
- Foundation for MapReduce, Bigtable

**Inspired:**
- **Hadoop HDFS** (open-source clone)
- **Colossus** (Google's next-gen FS, 2010+)
- **Ceph, GlusterFS** (distributed filesystems)

**Key Lessons:**
1. **Relaxed consistency** can enable huge performance gains
2. **Single master** is OK if not in data path
3. **Large blocks** reduce metadata overhead
4. **Co-design** apps and storage for best results

---

## 🎯 **Connections: MapReduce + GFS**

### **How They Work Together**

```
MapReduce Job:
  Input: /data/web_crawl.txt (10TB in GFS)
  
  1. Master queries GFS master:
     "Give me chunks for /data/web_crawl.txt"
     
  2. GFS returns:
     Chunk 1 → [server1, server2, server3]
     Chunk 2 → [server4, server5, server6]
     ...
     
  3. MapReduce master schedules:
     Map task 1 → server1 (data locality!)
     Map task 2 → server4
     ...
     
  4. Map workers:
     Read chunks from local GFS chunkserver
     Process with map()
     Write intermediate to local disk (NOT GFS)
     
  5. Reduce workers:
     Read intermediate from map workers (network)
     Write output to GFS (replicated 3x)
```

**Key Synergy:** 
- GFS provides fault-tolerant storage
- MapReduce provides fault-tolerant compute
- Together = complete data processing platform

---

## 📚 **Further Reading Path**

**If you want to dive deeper:**

### **Follow-On Papers:**

1. **Bigtable (2006)**
   - NoSQL database built on GFS + MapReduce
   - Foundation for HBase, Cassandra

2. **Chubby (2006)**
   - Distributed lock service
   - Used by GFS for master election
   - Inspired ZooKeeper

3. **Dremel (2010)**
   - Interactive queries on nested data
   - Foundation for BigQuery

4. **Pregel (2010)**
   - Graph processing at scale
   - Led to Apache Giraph

### **Modern Equivalents:**

- **MapReduce → Spark, Beam**
- **GFS → Colossus (Google), HDFS (Hadoop)**
- **Master → YARN ResourceManager**

---

## 🎯 **Summary**

**What You Learned:**

1. **MapReduce (2004):**
   - Abstracted distributed computing into map/reduce
   - Automatic parallelization + fault tolerance
   - Enabled non-experts to write distributed programs
   - Dominated 2004-2010, evolved into Spark/Beam

2. **GFS (2003):**
   - Designed for Google's unique workload
   - Large chunks, single master, relaxed consistency
   - Enabled MapReduce to scale to petabytes
   - Inspired HDFS and modern distributed file systems

**Key Insight:**
> "The best system designs are co-designed with their workloads."

Both papers made trade-offs specific to Google's needs:
- Large batch processing (not real-time)
- Append-heavy workloads (not random writes)
- Commodity hardware (not expensive servers)

**These assumptions shaped an industry.**

---

**Next Steps:**
- Return to [BEGINNER](./BEGINNER.md) for review
- Start [Week 2: ETL Pipelines](../1B_ETL_Basics/BEGINNER.md)

---

**Congratulations!** You've completed the full deep dive into MapReduce and GFS. You now understand these systems better than 99% of engineers. 🎉
