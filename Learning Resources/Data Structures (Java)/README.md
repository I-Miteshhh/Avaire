# Data Structures (Java) - Complete Interview Prep for 40 LPA SDE-Data

**Target Role:** Senior/Staff Data Engineer (40 LPA+)  
**Total Content:** 10 comprehensive modules  
**Study Time:** 3-4 weeks intensive preparation  
**Level:** Intermediate to Advanced

---

## 📚 Module Overview

This module covers **production-grade implementations** of all critical data structures with:
- ✅ Complete Java implementations from scratch
- ✅ Time/space complexity analysis for every operation
- ✅ Real-world data engineering use cases (Spark, Kafka, AWS)
- ✅ LeetCode-style interview problems with optimal solutions
- ✅ Thread-safety considerations
- ✅ Advanced optimizations and techniques

---

## 🗺️ Learning Path

### Week 1: Foundational Structures (Linear)

**Day 1-2:** [Arrays & ArrayList](./01-Arrays-and-ArrayList.md)
- Static arrays, dynamic resizing, growth factor (1.5×)
- Two Pointers, Sliding Window, Prefix Sum
- Interview: Two Sum, Product Except Self, Trapping Rain Water

**Day 3-4:** [LinkedList](./02-LinkedList.md)
- Singly, Doubly, Circular linked lists
- Floyd's cycle detection, fast/slow pointers
- Interview: Reverse List, Merge K Lists, LRU Cache foundation

**Day 5-6:** [Stack & Queue](./03-Stack-and-Queue.md)
- Array-based, LinkedList-based implementations
- Circular queue, dynamic resizing
- Interview: Valid Parentheses, Min Stack, Daily Temperatures

**Day 7:** [Deque & PriorityQueue](./04-Deque-and-PriorityQueue.md)
- Double-ended queue, binary heap (min/max)
- Heapify operations, custom comparator
- Interview: Sliding Window Maximum, Top K Frequent

---

### Week 2: Hash-based & Tree Structures

**Day 8-10:** [HashMap & HashSet](./05-HashMap-and-HashSet.md) ⭐ CRITICAL
- Hash function design, collision resolution (chaining, open addressing)
- Custom HashMap/HashSet from scratch
- Thread-safe: ConcurrentHashMap, Collections.synchronizedMap
- Interview: Two Sum, Group Anagrams, Longest Substring, LRU Cache

**Day 11-12:** [TreeMap & TreeSet](./06-TreeMap-and-TreeSet.md)
- Red-Black tree fundamentals
- Range queries: floor, ceiling, subMap, headMap, tailMap
- Interview: Range Sum Query, My Calendar, Contains Duplicate III

**Day 13-14:** [Trie](./07-Trie.md)
- Prefix tree for O(m) string operations
- HashMap-based and array-based implementations
- Compressed trie (radix tree), suffix trie
- Interview: Word Search II, Autocomplete, Wildcard Search

---

### Week 3: Advanced Structures

**Day 15-16:** [Segment Tree & Fenwick Tree](./08-Segment-Tree-and-Fenwick-Tree.md)
- Range queries (sum/min/max/GCD) in O(log n)
- Lazy propagation, Binary Indexed Tree
- Interview: Range Sum Query, Count Smaller Numbers
- Real-world: Time-series aggregations, OLAP cubes

**Day 17-18:** [Union Find](./10-Union-Find.md)
- Disjoint Set Union, path compression
- Union by rank/size, O(α(n)) complexity
- Interview: Connected Components, Kruskal's MST, Accounts Merge
- Real-world: Social networks, percolation systems

**Day 19-20:** [Graph Representations](./11-Graph-Representations.md)
- Adjacency Matrix, Adjacency List, Edge List
- BFS, DFS, topological sort, cycle detection
- Interview: Clone Graph, Course Schedule, Number of Islands

---

### Week 4: Practice & Mastery

**Day 21-24:** Interview Problem Blitz
- Solve 50+ problems from all categories
- Focus on optimal solutions and edge cases
- Practice explaining complexity analysis

**Day 25-28:** System Design Integration
- Design LRU Cache (HashMap + DoublyLinkedList)
- Design Rate Limiter (Sliding Window + TreeMap)
- Design Distributed Cache (Consistent Hashing)

---

## 🎯 Quick Reference: When to Use Each

### Decision Tree

```
Need to store data?
│
├─ Need fast lookup by key?
│  ├─ Keys are integers/hashable? → HashMap/HashSet
│  ├─ Need sorted order/range queries? → TreeMap/TreeSet
│  └─ Keys are strings with prefix operations? → Trie
│
├─ Need fast access by index?
│  ├─ Fixed size? → Array
│  └─ Dynamic size? → ArrayList
│
├─ Need LIFO (last in, first out)? → Stack
│
├─ Need FIFO (first in, first out)? → Queue
│
├─ Need min/max quickly? → PriorityQueue (Heap)
│
├─ Need range queries/updates? → Segment Tree / Fenwick Tree
│
├─ Need to track connected components? → Union Find
│
└─ Modeling relationships? → Graph (Adjacency List)
```

---

## ⚡ Time Complexity Cheat Sheet

| Data Structure | Access | Search | Insert | Delete | Space |
|----------------|--------|--------|--------|--------|-------|
| **Array** | O(1) | O(n) | O(n) | O(n) | O(n) |
| **ArrayList** | O(1) | O(n) | O(1)* | O(n) | O(n) |
| **LinkedList** | O(n) | O(n) | O(1) | O(1) | O(n) |
| **Stack** | O(n) | O(n) | O(1) | O(1) | O(n) |
| **Queue** | O(n) | O(n) | O(1) | O(1) | O(n) |
| **HashMap** | - | O(1)* | O(1)* | O(1)* | O(n) |
| **TreeMap** | - | O(log n) | O(log n) | O(log n) | O(n) |
| **Trie** | - | O(m) | O(m) | O(m) | O(ALPHABET_SIZE * m * n) |
| **PriorityQueue** | O(1)** | O(n) | O(log n) | O(log n) | O(n) |
| **Segment Tree** | - | O(log n) | O(log n) | O(log n) | O(4n) |
| **Fenwick Tree** | - | O(log n) | O(log n) | - | O(n) |
| **Union Find** | - | O(α(n))*** | O(α(n))*** | - | O(n) |

*Amortized  
**Access min/max only  
***Inverse Ackermann function, effectively O(1)

---

## 📊 Interview Problem Distribution

### By Difficulty

**Easy (30%):**
- Arrays: Two Sum, Contains Duplicate, Best Time to Buy Stock
- LinkedList: Reverse List, Merge Two Lists, Middle Node
- Stack: Valid Parentheses, Implement Stack using Queues
- HashMap: Valid Anagram, Intersection of Arrays

**Medium (50%):**
- Arrays: 3Sum, Container With Most Water, Subarray Sum
- LinkedList: Add Two Numbers, Remove Nth from End, Reorder List
- Stack: Min Stack, Daily Temperatures, Evaluate RPN
- Queue: Sliding Window Maximum, Top K Frequent
- HashMap: Group Anagrams, Longest Substring, Subarray Sum Equals K
- Tree: LRU Cache, Range Sum Query, My Calendar
- Trie: Word Search II, Add and Search Word, Replace Words
- Graph: Clone Graph, Course Schedule, Number of Islands

**Hard (20%):**
- Arrays: Trapping Rain Water, Median of Two Sorted Arrays
- LinkedList: Merge K Sorted Lists, Reverse Nodes in K-Group
- Heap: Find Median from Data Stream, Sliding Window Median
- Trie: Word Search II (optimized), Palindrome Pairs
- Segment Tree: Count of Range Sum, Range Sum Query 2D
- Union Find: Redundant Connection II, Accounts Merge
- Graph: Word Ladder II, Alien Dictionary

---

## 🏢 Company-Specific Focus

### FAANG (Meta, Amazon, Apple, Netflix, Google)

**High Frequency:**
- HashMap/HashSet (35%)
- Arrays (25%)
- Trees (15%)
- Graphs (15%)
- Others (10%)

**Google:**
- Focus on graphs, trees, and string algorithms
- Expect follow-up optimizations
- Common: Word Search II, Course Schedule, LRU Cache

**Amazon:**
- Focus on practical problems (e.g., warehouse, logistics)
- Common: Two Sum variations, Top K Frequent, Graph traversals

**Meta:**
- Focus on social network graphs
- Common: Clone Graph, Friend Circles, Shortest Path

### Big Tech India (Microsoft, Adobe, Intuit)

**Microsoft:**
- Focus on design + implementation
- Common: LRU Cache, Design HashMap, Implement Trie

**Adobe:**
- Focus on string processing and tries
- Common: Autocomplete, Word Search, String matching

---

## 🚀 Real-World Data Engineering Applications

### 1. Distributed Systems

**HashMap/HashSet:**
- Distributed caching (Redis, Memcached)
- Bloom filters for deduplication
- Rate limiting with sliding windows

**TreeMap/TreeSet:**
- Time-series event processing
- Leaderboards and ranking systems
- Partition range indexing in Spark

**Trie:**
- Autocomplete in search engines
- IP routing tables
- Dictionary compression

### 2. Stream Processing (Kafka, Flink)

**Queue/Deque:**
- Message buffering in Kafka consumers
- Sliding window aggregations
- Event time vs processing time handling

**PriorityQueue:**
- Event ordering by timestamp
- Top-K processing (trending topics)
- Scheduled task execution

### 3. Big Data (Spark, Hadoop)

**Segment Tree:**
- Range aggregations in OLAP cubes
- Fast analytics on partitioned data

**Union Find:**
- Connected components in graph analytics
- Deduplication across partitions

**Graph:**
- PageRank algorithm
- Social network analysis
- Dependency resolution in DAGs

---

## 💡 Advanced Topics & Optimizations

### HashMap Optimizations

```java
// 1. Right-sizing to avoid rehashing
Map<String, Integer> map = new HashMap<>((int) (expectedSize / 0.75) + 1);

// 2. ConcurrentHashMap for thread-safety
ConcurrentHashMap<String, Integer> concurrentMap = new ConcurrentHashMap<>();

// 3. Custom hash function for better distribution
@Override
public int hashCode() {
    return Objects.hash(field1, field2, field3);
}
```

### ArrayList Optimizations

```java
// 1. Pre-allocate capacity if size known
List<Integer> list = new ArrayList<>(expectedSize);

// 2. Use Arrays.asList for fixed-size
List<String> fixedList = Arrays.asList("a", "b", "c");

// 3. Bulk operations for efficiency
list.addAll(collection);  // Better than loop
```

### PriorityQueue Advanced

```java
// 1. Custom comparator for complex objects
PriorityQueue<Event> pq = new PriorityQueue<>((a, b) -> {
    if (a.priority != b.priority) {
        return Integer.compare(b.priority, a.priority);  // Max heap
    }
    return Long.compare(a.timestamp, b.timestamp);  // Tie-breaker
});

// 2. K-way merge with heap
PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> 
    Integer.compare(lists.get(a[0]).get(a[1]), 
                    lists.get(b[0]).get(b[1])));
```

### Union Find Optimizations

```java
// Path compression with halving (faster than recursion)
public int find(int x) {
    while (x != parent[x]) {
        parent[x] = parent[parent[x]];  // Halving
        x = parent[x];
    }
    return x;
}

// Union by size (better than rank)
public void union(int x, int y) {
    int rootX = find(x);
    int rootY = find(y);
    
    if (rootX == rootY) return;
    
    if (size[rootX] < size[rootY]) {
        parent[rootX] = rootY;
        size[rootY] += size[rootX];
    } else {
        parent[rootY] = rootX;
        size[rootX] += size[rootY];
    }
}
```

---

## 🎓 Interview Preparation Strategy

### Phase 1: Foundation (Week 1-2)
1. **Understand internals:** Don't just use Java's built-in, implement from scratch
2. **Master complexity:** Be able to justify every O(n) or O(log n)
3. **Practice patterns:** Two Pointers, Sliding Window, Fast/Slow Pointers

### Phase 2: Problem Solving (Week 3)
1. **Solve by category:** 10 Array, 10 LinkedList, 10 HashMap, etc.
2. **Focus on optimal:** Don't settle for brute force
3. **Time yourself:** 30 min for Medium, 45 min for Hard

### Phase 3: System Design Integration (Week 4)
1. **Design problems:** LRU Cache, Rate Limiter, Consistent Hashing
2. **Real-world scenarios:** "Design a recommendation system", "Design a metrics aggregation pipeline"
3. **Explain trade-offs:** Why HashMap over TreeMap? When to use Trie?

---

## 🔍 Common Interview Mistakes

### 1. Not Asking Clarifying Questions

```java
// ❌ Assume constraints
public int[] twoSum(int[] nums, int target) {
    // What if no solution?
    // Can I modify input?
    // Are there duplicates?
    // Can solution use same element twice?
}

// ✅ Clarify first
public int[] twoSum(int[] nums, int target) {
    // Given: Exactly one solution exists
    // Given: Cannot use same element twice
    // Given: Order of output doesn't matter
}
```

### 2. Ignoring Edge Cases

```java
// ❌ Missing null/empty checks
public int findMax(int[] nums) {
    int max = nums[0];  // What if nums is null or empty?
}

// ✅ Handle edge cases
public int findMax(int[] nums) {
    if (nums == null || nums.length == 0) {
        throw new IllegalArgumentException("Array cannot be null or empty");
    }
    int max = nums[0];
}
```

### 3. Not Discussing Trade-offs

```java
// ❌ Just give one solution
"I'll use a HashMap to solve this in O(n)."

// ✅ Discuss alternatives
"We could use:
1. HashMap: O(n) time, O(n) space - Best for single pass
2. Two Pointers (sorted): O(n log n) time, O(1) space - Better if sorting acceptable
3. Binary Search: O(n log n) time, O(1) space - Alternative to two pointers
I'll go with HashMap because..."
```

### 4. Poor Variable Naming

```java
// ❌ Cryptic names
for (int i = 0; i < n; i++) {
    for (int j = 0; j < m; j++) {
        int x = a[i][j];
    }
}

// ✅ Descriptive names
for (int row = 0; row < numRows; row++) {
    for (int col = 0; col < numCols; col++) {
        int cellValue = matrix[row][col];
    }
}
```

### 5. Not Testing Code

```java
// ❌ Just write and submit
public boolean isPalindrome(String s) {
    // ... implementation
}

// ✅ Walk through test cases
// Test 1: "A man a plan a canal Panama" → true
// Test 2: "" → true (empty string)
// Test 3: "race a car" → false
// Test 4: "a" → true (single character)
```

---

## 📖 Recommended Practice Problems

### Must-Solve (Top 50)

**Arrays (10):**
1. Two Sum (Easy)
2. Best Time to Buy and Sell Stock (Easy)
3. Contains Duplicate (Easy)
4. Product of Array Except Self (Medium)
5. Maximum Subarray (Medium)
6. 3Sum (Medium)
7. Container With Most Water (Medium)
8. Merge Intervals (Medium)
9. Trapping Rain Water (Hard)
10. Median of Two Sorted Arrays (Hard)

**LinkedList (8):**
11. Reverse Linked List (Easy)
12. Merge Two Sorted Lists (Easy)
13. Linked List Cycle (Easy)
14. Remove Nth Node From End (Medium)
15. Add Two Numbers (Medium)
16. Reorder List (Medium)
17. LRU Cache (Medium)
18. Merge K Sorted Lists (Hard)

**Stack/Queue (5):**
19. Valid Parentheses (Easy)
20. Min Stack (Medium)
21. Daily Temperatures (Medium)
22. Evaluate Reverse Polish Notation (Medium)
23. Largest Rectangle in Histogram (Hard)

**HashMap/HashSet (8):**
24. Valid Anagram (Easy)
25. Ransom Note (Easy)
26. Group Anagrams (Medium)
27. Top K Frequent Elements (Medium)
28. Longest Substring Without Repeating Characters (Medium)
29. Subarray Sum Equals K (Medium)
30. First Missing Positive (Hard)
31. Longest Consecutive Sequence (Hard)

**TreeMap/TreeSet (5):**
32. Kth Largest Element (Medium)
33. Top K Frequent Words (Medium)
34. Range Sum Query (Medium)
35. Contains Duplicate III (Medium)
36. My Calendar I (Medium)

**Trie (4):**
37. Implement Trie (Medium)
38. Add and Search Word (Medium)
39. Word Search II (Hard)
40. Design Search Autocomplete System (Hard)

**Heap (4):**
41. Kth Largest in Stream (Easy)
42. K Closest Points to Origin (Medium)
43. Find Median from Data Stream (Hard)
44. Sliding Window Median (Hard)

**Graph (6):**
45. Clone Graph (Medium)
46. Course Schedule (Medium)
47. Number of Islands (Medium)
48. Pacific Atlantic Water Flow (Medium)
49. Alien Dictionary (Hard)
50. Word Ladder II (Hard)

---

## 🛠️ Setup & Tools

### Java Environment

```bash
# Install Java 17 (LTS)
java --version

# IDE: IntelliJ IDEA (recommended) or Eclipse
# Plugins: SonarLint, CheckStyle

# Run a single file
javac Solution.java
java Solution

# Use jshell for quick testing
jshell
> List<Integer> list = new ArrayList<>();
> list.add(1);
> list.get(0)
```

### Testing Framework

```java
// JUnit 5
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class SolutionTest {
    
    @Test
    void testTwoSum() {
        Solution solution = new Solution();
        int[] nums = {2, 7, 11, 15};
        int target = 9;
        int[] result = solution.twoSum(nums, target);
        assertArrayEquals(new int[]{0, 1}, result);
    }
}
```

---

## 📚 Additional Resources

### Books
- **"Cracking the Coding Interview"** by Gayle Laakmann McDowell
- **"Designing Data-Intensive Applications"** by Martin Kleppmann
- **"Effective Java"** by Joshua Bloch

### Online Platforms
- **LeetCode:** 2000+ problems, company-specific lists
- **HackerRank:** Data structures tutorials
- **GeeksforGeeks:** Detailed explanations

### Video Resources
- **NeetCode:** LeetCode problem solutions
- **Back to Back SWE:** In-depth explanations
- **Tushar Roy:** Algorithm visualizations

---

## 🎯 Final Tips for 40 LPA Interviews

### Technical Round

1. **Think Out Loud:** Interviewers want to see your thought process
2. **Start with Brute Force:** Then optimize
3. **Draw Examples:** Visualize the problem
4. **Test Your Code:** Walk through 2-3 test cases
5. **Discuss Trade-offs:** Time vs space, clarity vs optimization

### System Design Integration

For SDE-Data roles, expect questions like:
- "Design a metrics aggregation system"
- "How would you implement a distributed cache?"
- "Design a real-time analytics pipeline"

**Connect data structures to systems:**
- HashMap → Distributed caching (Redis)
- TreeMap → Time-series databases
- Trie → Search engines, autocomplete
- Union Find → Distributed graph processing
- Segment Tree → OLAP cubes

### Behavioral Round

Prepare stories demonstrating:
- **Ownership:** Led data pipeline optimization that reduced latency by 50%
- **Collaboration:** Worked with ML team to design feature store
- **Problem Solving:** Debugged production issue in distributed system
- **Impact:** Built system processing 10M events/sec

---

## 📅 Daily Study Checklist

```
Day ____ / 28

□ Read 1 module section (45 min)
□ Implement data structure from scratch (30 min)
□ Solve 3 LeetCode problems (90 min)
  - 1 Easy
  - 1 Medium
  - 1 Hard
□ Review time/space complexity (15 min)
□ Write down 3 key learnings (10 min)

Total: ~3 hours/day
```

---

## 🏆 Success Metrics

**After completing this module, you should be able to:**

✅ Implement any data structure from scratch in 15-20 minutes  
✅ Analyze time/space complexity on the fly  
✅ Solve Medium LeetCode problems in 25-30 minutes  
✅ Solve Hard LeetCode problems in 40-45 minutes  
✅ Explain real-world applications of each structure  
✅ Design systems using appropriate data structures  
✅ Discuss trade-offs between different approaches  

---

**Good luck with your interview preparation! 🚀**

*Last Updated: January 2025*  
*Target: 40 LPA SDE-Data Role*  
*Level: Senior/Staff Data Engineer*
