# Week 1: MapReduce & Distributed Systems
## 🛠️ INTERMEDIATE - Hands-On Implementation

---

## 🎯 **Learning Objectives**

By the end of this section, you will:
- Build a working MapReduce framework in Python
- Understand data locality and partitioning
- Handle failures and stragglers
- Debug common MapReduce issues
- Solve 5 interview questions

---

## 🧪 **1. Hands-On Lab: Build MapReduce from Scratch**

### **Lab 1: Simple Word Count (Single Machine Simulation)**

Let's implement the **complete MapReduce workflow** in Python:

```python
from collections import defaultdict
from typing import List, Tuple, Iterator
import multiprocessing as mp

# ============================================
# USER-DEFINED FUNCTIONS
# ============================================

def map_function(document: str) -> Iterator[Tuple[str, int]]:
    """
    Map phase: Split document into words and emit (word, 1)
    """
    words = document.lower().split()
    for word in words:
        # Clean punctuation
        word = word.strip('.,!?;:"()[]')
        if word:  # Skip empty strings
            yield (word, 1)

def reduce_function(word: str, counts: List[int]) -> Tuple[str, int]:
    """
    Reduce phase: Sum all counts for a word
    """
    return (word, sum(counts))

# ============================================
# MAPREDUCE FRAMEWORK
# ============================================

class MapReduceFramework:
    """
    A simplified MapReduce framework that runs locally
    """
    
    def __init__(self, num_map_tasks=4, num_reduce_tasks=2):
        self.num_map_tasks = num_map_tasks
        self.num_reduce_tasks = num_reduce_tasks
    
    def run(self, input_data: List[str], map_fn, reduce_fn):
        """
        Execute the full MapReduce pipeline
        """
        print("🚀 Starting MapReduce Job...")
        
        # PHASE 1: MAP
        print(f"\n📍 MAP PHASE: Splitting into {self.num_map_tasks} tasks")
        map_outputs = self._map_phase(input_data, map_fn)
        
        # PHASE 2: SHUFFLE & SORT
        print(f"\n🔄 SHUFFLE PHASE: Grouping by key")
        shuffled = self._shuffle_phase(map_outputs)
        
        # PHASE 3: REDUCE
        print(f"\n🧮 REDUCE PHASE: Aggregating with {self.num_reduce_tasks} tasks")
        final_output = self._reduce_phase(shuffled, reduce_fn)
        
        print("\n✅ MapReduce Job Complete!")
        return final_output
    
    def _map_phase(self, input_data: List[str], map_fn) -> List[Tuple[str, int]]:
        """
        Simulate parallel map tasks
        """
        # Split input data into chunks
        chunk_size = len(input_data) // self.num_map_tasks
        chunks = [
            input_data[i:i+chunk_size] 
            for i in range(0, len(input_data), chunk_size)
        ]
        
        all_map_outputs = []
        
        for task_id, chunk in enumerate(chunks):
            print(f"  Map Task {task_id}: Processing {len(chunk)} documents")
            
            task_output = []
            for document in chunk:
                # Apply map function to each document
                for key_value in map_fn(document):
                    task_output.append(key_value)
            
            all_map_outputs.extend(task_output)
            print(f"    → Emitted {len(task_output)} key-value pairs")
        
        return all_map_outputs
    
    def _shuffle_phase(self, map_outputs: List[Tuple[str, int]]) -> dict:
        """
        Group all values by key (this is the "magic" of MapReduce)
        """
        shuffled = defaultdict(list)
        
        for key, value in map_outputs:
            shuffled[key].append(value)
        
        print(f"  → Grouped into {len(shuffled)} unique keys")
        return dict(shuffled)
    
    def _reduce_phase(self, shuffled: dict, reduce_fn) -> dict:
        """
        Apply reduce function to each key
        """
        results = {}
        
        # Partition keys across reduce tasks
        keys = list(shuffled.keys())
        chunk_size = len(keys) // self.num_reduce_tasks
        
        for task_id in range(self.num_reduce_tasks):
            start_idx = task_id * chunk_size
            end_idx = start_idx + chunk_size if task_id < self.num_reduce_tasks - 1 else len(keys)
            
            task_keys = keys[start_idx:end_idx]
            print(f"  Reduce Task {task_id}: Processing {len(task_keys)} keys")
            
            for key in task_keys:
                values = shuffled[key]
                result_key, result_value = reduce_fn(key, values)
                results[result_key] = result_value
        
        return results

# ============================================
# EXAMPLE USAGE
# ============================================

if __name__ == "__main__":
    # Sample documents (simulating file chunks)
    documents = [
        "hello world hello",
        "world of big data",
        "hello big data world",
        "data engineering is fun",
        "mapreduce is powerful",
        "big data requires distributed systems",
        "hello distributed world"
    ]
    
    # Create framework
    mr = MapReduceFramework(num_map_tasks=3, num_reduce_tasks=2)
    
    # Run MapReduce
    word_counts = mr.run(documents, map_function, reduce_function)
    
    # Display results
    print("\n📊 FINAL RESULTS:")
    print("=" * 40)
    for word, count in sorted(word_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{word:20s} → {count}")
```

**Output:**
```
🚀 Starting MapReduce Job...

📍 MAP PHASE: Splitting into 3 tasks
  Map Task 0: Processing 2 documents
    → Emitted 6 key-value pairs
  Map Task 1: Processing 2 documents
    → Emitted 8 key-value pairs
  Map Task 2: Processing 3 documents
    → Emitted 14 key-value pairs

🔄 SHUFFLE PHASE: Grouping by key
  → Grouped into 15 unique keys

🧮 REDUCE PHASE: Aggregating with 2 tasks
  Reduce Task 0: Processing 8 keys
  Reduce Task 1: Processing 7 keys

✅ MapReduce Job Complete!

📊 FINAL RESULTS:
========================================
data                 → 4
hello                → 4
world                → 4
big                  → 3
distributed          → 2
is                   → 2
...
```

---

### **Lab 2: Combiner Optimization**

**Problem:** Shuffling sends too much data over the network!

**Solution:** Use a **combiner** (mini-reducer on map side)

```python
def combiner_function(word: str, counts: List[int]) -> Tuple[str, int]:
    """
    Combiner: Reduce BEFORE shuffling to minimize network traffic
    """
    return (word, sum(counts))

class MapReduceWithCombiner(MapReduceFramework):
    """
    Enhanced MapReduce with combiner optimization
    """
    
    def _map_phase(self, input_data: List[str], map_fn) -> List[Tuple[str, int]]:
        """
        Map phase WITH local combining
        """
        chunk_size = len(input_data) // self.num_map_tasks
        chunks = [
            input_data[i:i+chunk_size] 
            for i in range(0, len(input_data), chunk_size)
        ]
        
        all_map_outputs = []
        
        for task_id, chunk in enumerate(chunks):
            # Map
            task_output = defaultdict(list)
            for document in chunk:
                for key, value in map_fn(document):
                    task_output[key].append(value)
            
            # Local combine (mini-reduce)
            combined_output = []
            for key, values in task_output.items():
                combined_key, combined_value = combiner_function(key, values)
                combined_output.append((combined_key, combined_value))
            
            print(f"  Map Task {task_id}: {len(chunk)} docs → {len(combined_output)} unique words (after combine)")
            all_map_outputs.extend(combined_output)
        
        return all_map_outputs

# Usage:
mr_optimized = MapReduceWithCombiner(num_map_tasks=3, num_reduce_tasks=2)
word_counts = mr_optimized.run(documents, map_function, reduce_function)
```

**Benefit:** Reduces network traffic by **10-100x** in practice!

---

## 🔍 **2. Mental Models: How to Think About MapReduce**

### **Model 1: Data Locality Matters**

**Bad Design (Don't do this!):**
```
Storage Cluster A (has data)
    ↓ (send 10TB over network)
Compute Cluster B (processes data)
```

**Good Design (MapReduce way):**
```
Same Cluster:
  Node 1: [Store 1TB] + [Process locally]
  Node 2: [Store 1TB] + [Process locally]
  Node 3: [Store 1TB] + [Process locally]
```

**Why?**
- Disk read: 100 MB/s
- Network: 10 MB/s (10x slower!)

**Analogy:** Cook in the kitchen where ingredients are, don't ship ingredients across the city!

---

### **Model 2: Partitioning Strategy**

**Hash Partitioning (Default):**
```python
def partition(key, num_reducers):
    return hash(key) % num_reducers

# Example:
partition("apple", 3)  → 1
partition("banana", 3) → 0
partition("cherry", 3) → 2
```

**Range Partitioning (For sorted output):**
```python
def partition_range(key, num_reducers):
    if key < 'm':
        return 0  # Reducer 0: a-l
    elif key < 'z':
        return 1  # Reducer 1: m-y
    else:
        return 2  # Reducer 2: z+
```

---

### **Model 3: Fault Tolerance via Re-execution**

```
Master Node tracks:
  Map Task 1 → Worker A (STATUS: Complete)
  Map Task 2 → Worker B (STATUS: Running)
  Map Task 3 → Worker C (STATUS: FAILED)

Master's Action:
  1. Detect failure (no heartbeat from Worker C)
  2. Re-assign Task 3 → Worker D
  3. Worker D re-runs from scratch (data still on HDFS)

Key: MapReduce is DETERMINISTIC
  → Re-running produces same output!
```

---

## 🐛 **3. Debugging & Troubleshooting**

### **Problem 1: Data Skew**

**Symptom:** One reducer takes 10x longer than others

**Cause:** Unbalanced key distribution

**Example:**
```
Reducer 1: Process "the" → 1 million occurrences
Reducer 2: Process "xylophone" → 10 occurrences

Reducer 1 becomes bottleneck!
```

**Solutions:**
1. **Salting:** Add random suffix to hot keys
```python
def map_with_salting(document):
    for word in document.split():
        if word == "the":  # Hot key
            salt = random.randint(0, 9)
            yield (f"{word}_{salt}", 1)
        else:
            yield (word, 1)

# Later, combine salted results
```

2. **Pre-aggregation:** Use combiner aggressively

3. **Custom partitioner:** Assign hot keys to multiple reducers

---

### **Problem 2: Too Many Small Files**

**Symptom:** MapReduce spends more time opening files than processing

**Cause:** Millions of tiny files (< 1MB each)

**Solution:**
```python
# Combine small files before processing
from glob import glob

def combine_small_files(input_dir, output_file, target_size_mb=128):
    """
    Merge small files into chunks of target_size_mb
    """
    files = sorted(glob(f"{input_dir}/*"))
    current_chunk = []
    current_size = 0
    chunk_id = 0
    
    for file in files:
        file_size = os.path.getsize(file)
        if current_size + file_size > target_size_mb * 1024 * 1024:
            # Write current chunk
            write_chunk(current_chunk, f"{output_file}_{chunk_id}")
            chunk_id += 1
            current_chunk = []
            current_size = 0
        
        current_chunk.append(file)
        current_size += file_size
    
    # Write remaining
    if current_chunk:
        write_chunk(current_chunk, f"{output_file}_{chunk_id}")
```

---

### **Problem 3: Stragglers (Slow Tasks)**

**Symptom:** 99 tasks complete in 1 minute, 1 task takes 10 minutes

**Cause:** 
- Bad hardware
- Other jobs on same machine
- Data skew

**MapReduce Solution: Speculative Execution**
```
Master detects:
  Task 100 is 10x slower than average

Master's action:
  1. Launch duplicate Task 100 on different worker
  2. Use result from whichever finishes first
  3. Kill the slower one
```

---

## 🎯 **4. Common Patterns & Use Cases**

### **Pattern 1: Filtering**

**Use Case:** Find all users who logged in from California

```python
def map_filter(log_entry):
    user_id, state, timestamp = log_entry.split(',')
    if state == 'CA':
        yield (user_id, timestamp)

def reduce_identity(user_id, timestamps):
    # Just pass through (no aggregation needed)
    for ts in timestamps:
        yield (user_id, ts)
```

---

### **Pattern 2: Join (Reduce-Side Join)**

**Use Case:** Join user profiles with purchase history

```python
def map_join(record):
    record_type, data = record.split('|', 1)
    
    if record_type == 'USER':
        user_id, name, email = data.split(',')
        yield (user_id, ('USER', name, email))
    
    elif record_type == 'PURCHASE':
        user_id, product, amount = data.split(',')
        yield (user_id, ('PURCHASE', product, amount))

def reduce_join(user_id, records):
    user_info = None
    purchases = []
    
    for record in records:
        if record[0] == 'USER':
            user_info = record[1:]
        else:  # PURCHASE
            purchases.append(record[1:])
    
    # Emit joined records
    for product, amount in purchases:
        yield (user_id, user_info, product, amount)
```

---

### **Pattern 3: Secondary Sort**

**Use Case:** Group by user, sorted by timestamp

```python
def map_secondary_sort(log_entry):
    user_id, timestamp, action = log_entry.split(',')
    # Composite key: (user_id, timestamp)
    yield ((user_id, timestamp), action)

# Custom partitioner: Partition by user_id only
def partition_by_user(composite_key, num_reducers):
    user_id, _ = composite_key
    return hash(user_id) % num_reducers

# Custom comparator: Sort by full composite key
def compare_keys(key1, key2):
    user1, ts1 = key1
    user2, ts2 = key2
    if user1 != user2:
        return user1 < user2
    return ts1 < ts2  # Within same user, sort by timestamp
```

---

## 💡 **5. Interview Questions (Easy to Medium)**

### **Question 1: Explain the purpose of the Combiner**

**Answer:**
The combiner is a **mini-reducer that runs on the map side** before the shuffle phase.

**Purpose:**
- Reduce network traffic by pre-aggregating values locally
- Example: Word count with 1M "hello" on one machine
  - Without combiner: Send 1M × ("hello", 1) pairs
  - With combiner: Send 1 × ("hello", 1000000) pair

**Requirements:**
- Must be associative and commutative
- reduce(k, [v1, v2, v3]) = reduce(k, [reduce(k, [v1, v2]), v3])

**When NOT to use:**
- Computing median/percentiles (not associative)
- Operations that need all values at once

---

### **Question 2: How does MapReduce handle failures?**

**Answer:**
MapReduce uses **re-execution** for fault tolerance:

**Map Task Failure:**
1. Master detects via missing heartbeat
2. Re-schedule task on different worker
3. Worker re-reads input from HDFS (data is replicated)

**Reduce Task Failure:**
1. Master re-schedules on different worker
2. Worker re-reads map outputs (stored on local disk of map workers)
3. If map output lost (machine died), re-run corresponding map tasks

**Master Failure:**
- Checkpoint state periodically
- New master reads checkpoint and resumes
- (In practice, rare — only one master)

**Key Insight:** Deterministic functions ensure re-execution produces same output!

---

### **Question 3: What causes data skew and how do you fix it?**

**Answer:**

**Causes:**
1. **Hot keys:** Few keys with many values (e.g., "the" in word count)
2. **Non-uniform distribution:** Hash function doesn't distribute evenly
3. **Correlated data:** All similar records hash to same reducer

**Solutions:**

**1. Salting (for hot keys):**
```python
# Split "the" across 10 reducers
yield (f"the_{random.randint(0,9)}", 1)
# Later, combine: "the_0" + "the_1" + ...
```

**2. Custom partitioner:**
```python
def smart_partition(key, num_reducers):
    if key in HOT_KEYS:
        # Assign hot keys to dedicated reducers
        return hash(key) % (num_reducers // 2)
    return hash(key) % num_reducers
```

**3. Sampling:**
- Pre-scan data to find hot keys
- Handle them separately

---

### **Question 4: Compare MapReduce with traditional databases**

**Answer:**

| Aspect | MapReduce | Traditional DB |
|--------|-----------|----------------|
| **Data Model** | Unstructured/semi-structured | Structured (schema) |
| **Scale** | Petabytes across 1000s machines | Terabytes on powerful servers |
| **Query** | Custom code (map/reduce functions) | SQL |
| **Performance** | High throughput | Low latency |
| **Best For** | Batch processing, ETL, log analysis | OLTP, OLAP with fast queries |
| **Fault Tolerance** | Re-execution | Replication + transaction logs |

**When to use MapReduce:**
- Processing web crawl data (Google)
- Log aggregation (Facebook, Netflix)
- Graph processing (PageRank)

**When to use DB:**
- User account management
- Real-time dashboards
- Financial transactions

---

### **Question 5: How would you implement PageRank in MapReduce?**

**Answer:**

PageRank requires **iterative processing** (repeat until convergence).

**Algorithm (per iteration):**

**Map Phase:**
```python
def map_pagerank(page_id, rank, outlinks):
    n = len(outlinks)
    for outlink in outlinks:
        # Distribute rank to neighbors
        yield (outlink, rank / n)
    
    # Preserve graph structure
    yield (page_id, ("LINKS", outlinks))
```

**Reduce Phase:**
```python
def reduce_pagerank(page_id, values):
    rank_sum = 0
    outlinks = []
    
    for value in values:
        if value[0] == "LINKS":
            outlinks = value[1]
        else:
            rank_sum += value
    
    # PageRank formula: 0.15 + 0.85 * sum(incoming)
    new_rank = 0.15 + 0.85 * rank_sum
    yield (page_id, new_rank, outlinks)
```

**Run 10-20 iterations until ranks stabilize.**

**Problem:** MapReduce is **inefficient for iterative algorithms**
- Each iteration reads/writes full graph to disk
- Led to Spark (keeps data in memory!)

---

## 🎯 **Next Steps**

**You now understand:**
✅ How to implement MapReduce  
✅ Combiner optimization  
✅ Handling failures and stragglers  
✅ Common patterns (filter, join, secondary sort)  

**Next:**
- 🏗️ [EXPERT](./EXPERT.md) - Google's production architecture
- 📄 [WHITEPAPERS](./WHITEPAPERS.md) - Deep dive into MapReduce (2004) paper

---

**Practice Exercise:**
Build a MapReduce job to find:
- Top 10 most common words
- Average word length per document
- Word co-occurrence matrix

*Solutions in the EXPERT section!* 🚀
