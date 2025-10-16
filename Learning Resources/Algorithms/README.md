# Algorithms - Complete Interview Prep for 40 LPA SDE-Data

**Target Role:** Senior/Staff Data Engineer (40 LPA+)  
**Study Time:** 3-4 weeks intensive preparation  
**Level:** Intermediate to Advanced  
**Status:** Core modules complete (Sorting, Binary Search, DP + more coming)

---

## 📚 Module Overview

This module covers **production-grade algorithm implementations** with:
- ✅ All major algorithm categories with optimal solutions
- ✅ Time/space complexity analysis
- ✅ Real-world data engineering applications
- ✅ LeetCode-style interview problems
- ✅ Pattern recognition and problem-solving strategies

---

## 🗺️ Complete Learning Path

### Week 1: Fundamentals

**Day 1-2:** [Sorting Algorithms](./01-Sorting-Algorithms.md) ⭐⭐⭐⭐⭐
- QuickSort (O(n log n) average, O(n²) worst)
- MergeSort (O(n log n) stable)
- HeapSort (O(n log n) in-place)
- Counting Sort, Radix Sort, Bucket Sort (O(n) for specific cases)
- Dutch National Flag, Kth Largest Element
- **Real-world:** Distributed sorting in Spark, external merge sort

**Day 3-4:** [Binary Search Variations](./02-Binary-Search-Variations.md) ⭐⭐⭐⭐⭐
- Classic binary search O(log n)
- Find first/last occurrence
- Search in rotated sorted array
- Search in 2D matrix
- Binary search on answer (Koko Bananas, Split Array)
- Median of two sorted arrays (Hard)
- **Real-world:** Time-series data lookups, partition pruning in databases

---

### Week 2: Core Patterns

**Day 5-6:** Two Pointers & Sliding Window
- Same/opposite direction pointers
- Fixed/variable window size
- Longest substring, subarray problems
- Container with most water, trapping rain water
- **Real-world:** Stream processing windows, moving averages

**Day 7-9:** [Dynamic Programming](./05-Dynamic-Programming.md) ⭐⭐⭐⭐⭐
- **1D DP:** Climbing Stairs, House Robber, Decode Ways
- **2D DP:** LCS, Edit Distance, Regex Matching
- **Knapsack:** 0/1 Knapsack, Partition, Coin Change
- **LIS:** Longest Increasing Subsequence O(n log n)
- **Kadane:** Maximum Subarray
- **Real-world:** Resource allocation, job scheduling optimization

**Day 10-11:** Recursion & Backtracking
- Subsets, permutations, combinations
- N-Queens, Sudoku Solver
- Word Search, Palindrome Partitioning
- Generate Parentheses
- **Real-world:** Configuration generation, constraint satisfaction

---

### Week 3: Graph Algorithms

**Day 12-13:** Graph Traversals
- **BFS:** Level-order, shortest path (unweighted)
- **DFS:** Cycle detection, topological sort
- Connected components, bipartite check
- **Real-world:** Dependency graphs (Airflow, Spark DAGs), social networks

**Day 14-15:** Shortest Path Algorithms
- **Dijkstra:** O((V + E) log V) for non-negative weights
- **Bellman-Ford:** O(VE) handles negative weights
- **Floyd-Warshall:** O(V³) all-pairs shortest path
- **A* Algorithm:** Heuristic search
- **Real-world:** Network routing, Google Maps, logistics optimization

**Day 16:** Minimum Spanning Tree
- **Kruskal's Algorithm:** Union Find O(E log E)
- **Prim's Algorithm:** Priority Queue O(E log V)
- **Real-world:** Network design, clustering algorithms

---

### Week 4: Advanced Topics

**Day 17-18:** Tree Algorithms
- Binary tree traversals (inorder, preorder, postorder, level-order)
- LCA (Lowest Common Ancestor)
- Diameter, height, serialize/deserialize
- Morris traversal O(1) space
- **Real-world:** File system operations, expression parsing

**Day 19:** String Algorithms
- **KMP:** Pattern matching O(n + m)
- **Rabin-Karp:** Rolling hash O(n)
- **Z-Algorithm:** Pattern matching O(n)
- **Manacher:** Longest palindrome O(n)
- **Real-world:** Log parsing, DNA sequence matching, plagiarism detection

**Day 20:** Greedy Algorithms
- Activity selection, interval scheduling
- Huffman coding
- Jump Game, Gas Station
- **Real-world:** Task scheduling, compression algorithms

**Day 21:** Bit Manipulation
- XOR tricks, counting bits
- Power of 2, single number variations
- Subset generation using bitmasks
- **Real-world:** Low-level optimizations, hash functions

---

## ⚡ Algorithm Complexity Cheat Sheet

### Sorting

| Algorithm | Best | Average | Worst | Space | Stable |
|-----------|------|---------|-------|-------|--------|
| QuickSort | O(n log n) | O(n log n) | O(n²) | O(log n) | No |
| MergeSort | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes |
| HeapSort | O(n log n) | O(n log n) | O(n log n) | O(1) | No |
| Counting | O(n + k) | O(n + k) | O(n + k) | O(k) | Yes |
| Radix | O(d(n + k)) | O(d(n + k)) | O(d(n + k)) | O(n + k) | Yes |

### Searching

| Algorithm | Time | Space | Notes |
|-----------|------|-------|-------|
| Binary Search | O(log n) | O(1) | Sorted array |
| BFS | O(V + E) | O(V) | Shortest path (unweighted) |
| DFS | O(V + E) | O(V) | Topological sort, cycles |
| Dijkstra | O((V + E) log V) | O(V) | Non-negative weights |
| Bellman-Ford | O(VE) | O(V) | Negative weights |

### Dynamic Programming

| Problem | Time | Space | Pattern |
|---------|------|-------|---------|
| Fibonacci | O(n) | O(1) | 1D DP |
| LIS | O(n²) or O(n log n) | O(n) | 1D DP |
| LCS | O(mn) | O(mn) | 2D DP |
| Edit Distance | O(mn) | O(mn) | 2D DP |
| 0/1 Knapsack | O(n * W) | O(W) | Knapsack |
| Coin Change | O(n * amount) | O(amount) | Knapsack |

---

## 🎯 Pattern Recognition Guide

### When to Use Each Algorithm

```
Sorted Array? → Binary Search
Unsorted Array, need min/max? → Heap
Need stable sort? → Merge Sort
Memory constrained? → Heap Sort (O(1) space)
Integer sorting, small range? → Counting Sort
Large integers? → Radix Sort

Graph traversal? → BFS (shortest path) or DFS (all paths)
Shortest path, weighted? → Dijkstra (non-negative) or Bellman-Ford
All-pairs shortest path? → Floyd-Warshall

Optimization problem? → DP or Greedy
Overlapping subproblems? → DP
Greedy choice property? → Greedy

Sliding window? → Two Pointers
Substring/subarray problems? → Sliding Window
Permutations/combinations? → Backtracking
```

---

## 💡 Problem-Solving Framework

### Step-by-Step Approach

```
1. CLARIFY
   - Input constraints (size, range, duplicates?)
   - Output format
   - Edge cases (empty, single element, all same?)

2. EXAMPLES
   - Walk through 2-3 examples
   - Include edge cases
   - Verify understanding

3. APPROACH
   - Brute force first (for baseline)
   - Identify patterns (sliding window, DP, etc.)
   - Consider multiple approaches
   - Discuss trade-offs

4. CODE
   - Start with high-level structure
   - Implement carefully with good variable names
   - Handle edge cases

5. TEST
   - Walk through code with example
   - Check edge cases
   - Analyze time/space complexity

6. OPTIMIZE
   - Can we do better on time?
   - Can we reduce space?
   - Is there a mathematical insight?
```

---

## 🏢 Company-Specific Focus

### FAANG (Meta, Amazon, Apple, Netflix, Google)

**High Frequency Topics:**
1. **Arrays & Strings (30%):** Two Sum, Longest Substring, Trapping Rain Water
2. **Dynamic Programming (25%):** LIS, LCS, Edit Distance, Coin Change
3. **Trees & Graphs (20%):** BFS/DFS, LCA, Dijkstra
4. **Sorting & Searching (15%):** Binary Search, Merge K Lists
5. **Others (10%):** Backtracking, Bit Manipulation

**Google:** Focus on optimal solutions, follow-up questions
**Amazon:** Focus on practical problems, leadership principles
**Meta:** Focus on graph algorithms, scale discussions

### Data Engineering Specific

**Databricks, Snowflake, Confluent:**
1. **Graph Algorithms:** DAG scheduling, dependency resolution
2. **Sorting:** External merge sort, distributed sorting
3. **Dynamic Programming:** Query optimization, resource allocation
4. **String Algorithms:** Log parsing, pattern matching

**Common Questions:**
- Design a DAG scheduler (topological sort, cycle detection)
- Optimize JOIN operation (sorting, hashing)
- Parse and aggregate logs (string algorithms, hash maps)
- Distribute data across partitions (consistent hashing, range partitioning)

---

## 📖 Must-Solve Problems by Category

### Arrays & Sorting (15 problems)

**Easy:**
1. Two Sum
2. Best Time to Buy Stock
3. Contains Duplicate

**Medium:**
4. 3Sum
5. Sort Colors (Dutch National Flag)
6. Merge Intervals
7. Product of Array Except Self
8. Container With Most Water

**Hard:**
9. Trapping Rain Water
10. Median of Two Sorted Arrays
11. First Missing Positive

### Binary Search (10 problems)

**Easy:**
12. Binary Search
13. Search Insert Position

**Medium:**
14. Search in Rotated Sorted Array
15. Find First and Last Position
16. Koko Eating Bananas
17. Capacity to Ship Packages

**Hard:**
18. Split Array Largest Sum
19. Median of Two Sorted Arrays

### Dynamic Programming (20 problems)

**Easy:**
20. Climbing Stairs
21. House Robber

**Medium:**
22. Longest Increasing Subsequence
23. Coin Change
24. Longest Common Subsequence
25. Word Break
26. Partition Equal Subset Sum
27. Unique Paths
28. Decode Ways
29. Maximum Product Subarray

**Hard:**
30. Edit Distance
31. Regular Expression Matching
32. Longest Valid Parentheses
33. Maximal Rectangle

### Graphs (15 problems)

**Medium:**
34. Number of Islands (BFS/DFS)
35. Clone Graph
36. Course Schedule (Topological Sort)
37. Pacific Atlantic Water Flow
38. Network Delay Time (Dijkstra)
39. Cheapest Flights Within K Stops

**Hard:**
40. Word Ladder II
41. Alien Dictionary

### Trees (10 problems)

**Easy:**
42. Maximum Depth of Binary Tree
43. Invert Binary Tree

**Medium:**
44. Binary Tree Level Order Traversal
45. Lowest Common Ancestor
46. Serialize and Deserialize Binary Tree
47. Diameter of Binary Tree

### Backtracking (8 problems)

**Medium:**
48. Subsets
49. Permutations
50. Combination Sum
51. Word Search
52. Generate Parentheses

---

## 🎓 Advanced Optimization Techniques

### Space Optimization in DP

```java
// From O(n) to O(1) space
// Example: Fibonacci

// Unoptimized: O(n) space
int[] dp = new int[n + 1];
dp[0] = 0; dp[1] = 1;
for (int i = 2; i <= n; i++) {
    dp[i] = dp[i-1] + dp[i-2];
}

// Optimized: O(1) space
int prev2 = 0, prev1 = 1;
for (int i = 2; i <= n; i++) {
    int curr = prev1 + prev2;
    prev2 = prev1;
    prev1 = curr;
}
```

### Two-Pass vs One-Pass

```java
// Two-pass: Find max, then use it
int max = Arrays.stream(arr).max().getAsInt();
// ... use max

// One-pass: Track max while processing
int max = Integer.MIN_VALUE;
for (int num : arr) {
    max = Math.max(max, num);
    // ... process with max
}
```

### Precomputation

```java
// Example: Range sum queries
// Without precomputation: O(n) per query
int sum = 0;
for (int i = left; i <= right; i++) {
    sum += arr[i];
}

// With prefix sum: O(1) per query, O(n) preprocessing
int[] prefixSum = new int[n + 1];
for (int i = 0; i < n; i++) {
    prefixSum[i + 1] = prefixSum[i] + arr[i];
}
int sum = prefixSum[right + 1] - prefixSum[left];
```

---

## 🔍 Common Interview Mistakes

### 1. Not Considering Edge Cases

```java
// ❌ Assumes array not empty
int max = arr[0];

// ✅ Handles empty array
if (arr == null || arr.length == 0) {
    throw new IllegalArgumentException("Array is empty");
}
int max = arr[0];
```

### 2. Integer Overflow

```java
// ❌ May overflow
int mid = (left + right) / 2;

// ✅ Prevents overflow
int mid = left + (right - left) / 2;
```

### 3. Off-by-One Errors

```java
// ❌ May cause index out of bounds
for (int i = 0; i <= arr.length; i++) {
    // ...
}

// ✅ Correct boundary
for (int i = 0; i < arr.length; i++) {
    // ...
}
```

### 4. Not Explaining Complexity

```
❌ "This solution works"

✅ "This solution runs in O(n log n) time due to sorting, 
    and uses O(n) space for the hash map. 
    We could optimize to O(1) space by sorting in-place if mutation is allowed."
```

---

## 🛠️ Practice Strategy

### Week-by-Week Plan

**Week 1:** Foundations
- Day 1-2: Arrays & Sorting (solve 10 easy, 5 medium)
- Day 3-4: Binary Search (solve 5 easy, 5 medium)
- Day 5-7: Review and practice contest

**Week 2:** Core Patterns
- Day 8-9: Two Pointers & Sliding Window (10 medium)
- Day 10-14: Dynamic Programming (15 problems, increasing difficulty)

**Week 3:** Advanced
- Day 15-17: Graphs (BFS/DFS, shortest path)
- Day 18-19: Trees
- Day 20-21: Backtracking & Greedy

**Week 4:** Practice & Mock Interviews
- Day 22-24: Solve 3 problems/day under time pressure
- Day 25-26: Mock interviews
- Day 27-28: Review mistakes, weak areas

---

## 📅 Daily Study Checklist

```
Day ____ / 28

□ Solve 2-3 LeetCode problems (90 min)
  - 1 Easy (warm-up)
  - 1-2 Medium
□ Review 1 algorithm pattern (30 min)
□ Implement 1 algorithm from scratch (30 min)
□ Analyze complexity for all solutions (15 min)
□ Write down key learnings (10 min)

Total: ~3 hours/day
```

---

## 🏆 Success Metrics

**After completing this module, you should be able to:**

✅ Solve Easy problems in 10-15 minutes  
✅ Solve Medium problems in 25-30 minutes  
✅ Solve Hard problems in 40-45 minutes  
✅ Recognize patterns immediately (DP, Binary Search, etc.)  
✅ Optimize brute force to optimal solution  
✅ Explain time/space complexity clearly  
✅ Handle follow-up questions confidently  
✅ Connect algorithms to real-world data engineering problems  

---

**Good luck with your interview preparation! 🚀**

*Last Updated: January 2025*  
*Target: 40 LPA SDE-Data Role*  
*Level: Senior/Staff Data Engineer*
