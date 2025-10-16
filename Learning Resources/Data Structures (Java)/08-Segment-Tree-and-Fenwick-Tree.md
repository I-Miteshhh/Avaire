# Segment Tree and Fenwick Tree

**Difficulty:** Advanced  
**Learning Time:** 2-3 weeks  
**Interview Frequency:** ⭐⭐⭐ (Medium - Advanced companies)

---

## 📚 Table of Contents

1. [Segment Tree](#segment-tree)
2. [Fenwick Tree (Binary Indexed Tree)](#fenwick-tree-binary-indexed-tree)
3. [Comparison](#comparison)
4. [Interview Problems](#interview-problems)
5. [Real-World Use Cases](#real-world-use-cases)

---

## Segment Tree

### What is a Segment Tree?

```
Tree data structure for range queries
Each node represents interval [L, R]
Leaf nodes represent single elements
Internal nodes represent merged intervals

Example: Array [1, 3, 5, 7, 9, 11]

                 [0-5]: 36
               /          \
         [0-2]: 9         [3-5]: 27
         /     \          /      \
    [0-1]: 4  [2]: 5  [3-4]: 16  [5]: 11
    /    \            /     \
  [0]: 1 [1]: 3    [3]: 7  [4]: 9

✅ Range sum, min, max, GCD in O(log n)
✅ Point update in O(log n)
✅ Range update with lazy propagation
❌ More complex than Fenwick Tree
❌ Higher memory (4n)
```

### Time Complexity

| Operation | Time | Space |
|-----------|------|-------|
| **Build** | O(n) | O(4n) |
| **Query** | O(log n) | - |
| **Update** | O(log n) | - |
| **Range Update** | O(log n) with lazy | - |

---

### Implementation

#### Range Sum Segment Tree

```java
/**
 * Segment Tree for range sum queries
 */
class SegmentTree {
    
    private int[] tree;
    private int n;
    
    public SegmentTree(int[] nums) {
        this.n = nums.length;
        this.tree = new int[4 * n];
        build(nums, 0, 0, n - 1);
    }
    
    /**
     * Build tree: O(n)
     */
    private void build(int[] nums, int node, int start, int end) {
        if (start == end) {
            tree[node] = nums[start];
            return;
        }
        
        int mid = start + (end - start) / 2;
        int leftChild = 2 * node + 1;
        int rightChild = 2 * node + 2;
        
        build(nums, leftChild, start, mid);
        build(nums, rightChild, mid + 1, end);
        
        tree[node] = tree[leftChild] + tree[rightChild];
    }
    
    /**
     * Query range sum: O(log n)
     */
    public int query(int left, int right) {
        return queryHelper(0, 0, n - 1, left, right);
    }
    
    private int queryHelper(int node, int start, int end, int left, int right) {
        // No overlap
        if (right < start || left > end) {
            return 0;
        }
        
        // Complete overlap
        if (left <= start && end <= right) {
            return tree[node];
        }
        
        // Partial overlap
        int mid = start + (end - start) / 2;
        int leftChild = 2 * node + 1;
        int rightChild = 2 * node + 2;
        
        int leftSum = queryHelper(leftChild, start, mid, left, right);
        int rightSum = queryHelper(rightChild, mid + 1, end, left, right);
        
        return leftSum + rightSum;
    }
    
    /**
     * Update single element: O(log n)
     */
    public void update(int index, int value) {
        updateHelper(0, 0, n - 1, index, value);
    }
    
    private void updateHelper(int node, int start, int end, int index, int value) {
        if (start == end) {
            tree[node] = value;
            return;
        }
        
        int mid = start + (end - start) / 2;
        int leftChild = 2 * node + 1;
        int rightChild = 2 * node + 2;
        
        if (index <= mid) {
            updateHelper(leftChild, start, mid, index, value);
        } else {
            updateHelper(rightChild, mid + 1, end, index, value);
        }
        
        tree[node] = tree[leftChild] + tree[rightChild];
    }
}
```

#### Range Minimum Query Segment Tree

```java
/**
 * Segment Tree for range minimum queries
 */
class MinSegmentTree {
    
    private int[] tree;
    private int n;
    
    public MinSegmentTree(int[] nums) {
        this.n = nums.length;
        this.tree = new int[4 * n];
        build(nums, 0, 0, n - 1);
    }
    
    private void build(int[] nums, int node, int start, int end) {
        if (start == end) {
            tree[node] = nums[start];
            return;
        }
        
        int mid = start + (end - start) / 2;
        int leftChild = 2 * node + 1;
        int rightChild = 2 * node + 2;
        
        build(nums, leftChild, start, mid);
        build(nums, rightChild, mid + 1, end);
        
        tree[node] = Math.min(tree[leftChild], tree[rightChild]);
    }
    
    public int queryMin(int left, int right) {
        return queryHelper(0, 0, n - 1, left, right);
    }
    
    private int queryHelper(int node, int start, int end, int left, int right) {
        if (right < start || left > end) {
            return Integer.MAX_VALUE;
        }
        
        if (left <= start && end <= right) {
            return tree[node];
        }
        
        int mid = start + (end - start) / 2;
        int leftMin = queryHelper(2 * node + 1, start, mid, left, right);
        int rightMin = queryHelper(2 * node + 2, mid + 1, end, left, right);
        
        return Math.min(leftMin, rightMin);
    }
}
```

#### Lazy Propagation (Range Update)

```java
/**
 * Segment Tree with lazy propagation for range updates
 */
class LazySegmentTree {
    
    private int[] tree;
    private int[] lazy;
    private int n;
    
    public LazySegmentTree(int[] nums) {
        this.n = nums.length;
        this.tree = new int[4 * n];
        this.lazy = new int[4 * n];
        build(nums, 0, 0, n - 1);
    }
    
    private void build(int[] nums, int node, int start, int end) {
        if (start == end) {
            tree[node] = nums[start];
            return;
        }
        
        int mid = start + (end - start) / 2;
        build(nums, 2 * node + 1, start, mid);
        build(nums, 2 * node + 2, mid + 1, end);
        
        tree[node] = tree[2 * node + 1] + tree[2 * node + 2];
    }
    
    /**
     * Range update: Add value to range [left, right]
     * Time: O(log n)
     */
    public void updateRange(int left, int right, int value) {
        updateRangeHelper(0, 0, n - 1, left, right, value);
    }
    
    private void updateRangeHelper(int node, int start, int end, 
                                   int left, int right, int value) {
        // Apply pending updates
        if (lazy[node] != 0) {
            tree[node] += lazy[node] * (end - start + 1);
            
            if (start != end) {
                lazy[2 * node + 1] += lazy[node];
                lazy[2 * node + 2] += lazy[node];
            }
            
            lazy[node] = 0;
        }
        
        // No overlap
        if (right < start || left > end) {
            return;
        }
        
        // Complete overlap
        if (left <= start && end <= right) {
            tree[node] += value * (end - start + 1);
            
            if (start != end) {
                lazy[2 * node + 1] += value;
                lazy[2 * node + 2] += value;
            }
            
            return;
        }
        
        // Partial overlap
        int mid = start + (end - start) / 2;
        updateRangeHelper(2 * node + 1, start, mid, left, right, value);
        updateRangeHelper(2 * node + 2, mid + 1, end, left, right, value);
        
        tree[node] = tree[2 * node + 1] + tree[2 * node + 2];
    }
    
    /**
     * Range query with lazy propagation
     */
    public int query(int left, int right) {
        return queryHelper(0, 0, n - 1, left, right);
    }
    
    private int queryHelper(int node, int start, int end, int left, int right) {
        // Apply pending updates
        if (lazy[node] != 0) {
            tree[node] += lazy[node] * (end - start + 1);
            
            if (start != end) {
                lazy[2 * node + 1] += lazy[node];
                lazy[2 * node + 2] += lazy[node];
            }
            
            lazy[node] = 0;
        }
        
        if (right < start || left > end) {
            return 0;
        }
        
        if (left <= start && end <= right) {
            return tree[node];
        }
        
        int mid = start + (end - start) / 2;
        int leftSum = queryHelper(2 * node + 1, start, mid, left, right);
        int rightSum = queryHelper(2 * node + 2, mid + 1, end, left, right);
        
        return leftSum + rightSum;
    }
}
```

---

## Fenwick Tree (Binary Indexed Tree)

### What is a Fenwick Tree?

```
Elegant data structure for prefix sums
Uses binary representation for efficient updates

Example: Array [1, 3, 5, 7, 9, 11]

Index:    1  2  3  4  5  6  7  8
Binary:   1 10 11 100 101 110 111 1000
Tree:     1  4  5 16  9 20 11 36

✅ Simpler than Segment Tree
✅ Less memory (n+1)
✅ Faster in practice
✅ Elegant code
❌ Only prefix operations (not arbitrary ranges easily)
❌ Harder to understand initially
```

### Time Complexity

| Operation | Time | Space |
|-----------|------|-------|
| **Build** | O(n log n) | O(n) |
| **Prefix Sum** | O(log n) | - |
| **Range Sum** | O(log n) | - |
| **Update** | O(log n) | - |

---

### Implementation

```java
/**
 * Fenwick Tree (Binary Indexed Tree)
 */
class FenwickTree {
    
    private int[] tree;
    private int n;
    
    public FenwickTree(int n) {
        this.n = n;
        this.tree = new int[n + 1];  // 1-indexed
    }
    
    public FenwickTree(int[] nums) {
        this.n = nums.length;
        this.tree = new int[n + 1];
        
        for (int i = 0; i < n; i++) {
            update(i, nums[i]);
        }
    }
    
    /**
     * Update index by delta: O(log n)
     */
    public void update(int index, int delta) {
        index++;  // Convert to 1-indexed
        
        while (index <= n) {
            tree[index] += delta;
            index += index & (-index);  // Add last set bit
        }
    }
    
    /**
     * Get prefix sum [0, index]: O(log n)
     */
    public int prefixSum(int index) {
        index++;  // Convert to 1-indexed
        int sum = 0;
        
        while (index > 0) {
            sum += tree[index];
            index -= index & (-index);  // Remove last set bit
        }
        
        return sum;
    }
    
    /**
     * Get range sum [left, right]: O(log n)
     */
    public int rangeSum(int left, int right) {
        return prefixSum(right) - (left > 0 ? prefixSum(left - 1) : 0);
    }
    
    /**
     * Set value at index: O(log n)
     */
    public void set(int index, int value) {
        int currentValue = rangeSum(index, index);
        update(index, value - currentValue);
    }
}
```

### 2D Fenwick Tree

```java
/**
 * 2D Fenwick Tree for matrix range sums
 */
class FenwickTree2D {
    
    private int[][] tree;
    private int m, n;
    
    public FenwickTree2D(int m, int n) {
        this.m = m;
        this.n = n;
        this.tree = new int[m + 1][n + 1];
    }
    
    /**
     * Update cell: O(log m * log n)
     */
    public void update(int row, int col, int delta) {
        for (int i = row + 1; i <= m; i += i & (-i)) {
            for (int j = col + 1; j <= n; j += j & (-j)) {
                tree[i][j] += delta;
            }
        }
    }
    
    /**
     * Sum of rectangle [0,0] to [row, col]: O(log m * log n)
     */
    public int sum(int row, int col) {
        int sum = 0;
        
        for (int i = row + 1; i > 0; i -= i & (-i)) {
            for (int j = col + 1; j > 0; j -= j & (-j)) {
                sum += tree[i][j];
            }
        }
        
        return sum;
    }
    
    /**
     * Sum of rectangle [row1,col1] to [row2,col2]
     */
    public int rangeSum(int row1, int col1, int row2, int col2) {
        return sum(row2, col2) 
             - (col1 > 0 ? sum(row2, col1 - 1) : 0)
             - (row1 > 0 ? sum(row1 - 1, col2) : 0)
             + (row1 > 0 && col1 > 0 ? sum(row1 - 1, col1 - 1) : 0);
    }
}
```

---

## Comparison

### Segment Tree vs Fenwick Tree

| Feature | Segment Tree | Fenwick Tree |
|---------|--------------|--------------|
| **Memory** | O(4n) | O(n) |
| **Build Time** | O(n) | O(n log n) |
| **Query Time** | O(log n) | O(log n) |
| **Update Time** | O(log n) | O(log n) |
| **Range Update** | O(log n) with lazy | Not easy |
| **Arbitrary Function** | Yes (min, max, GCD) | Only invertible (sum, XOR) |
| **Complexity** | Higher | Lower |
| **Code Length** | Longer | Shorter |

**Use Segment Tree when:**
- ✅ Need non-invertible operations (min, max, GCD)
- ✅ Need range updates
- ✅ Complex queries

**Use Fenwick Tree when:**
- ✅ Only need sum/XOR
- ✅ Memory constrained
- ✅ Want simpler code

---

## Interview Problems

### Problem 1: Range Sum Query - Mutable (LeetCode 307)

```java
/**
 * Using Fenwick Tree
 */
class NumArray {
    
    private FenwickTree fenwick;
    private int[] nums;
    
    public NumArray(int[] nums) {
        this.nums = nums;
        this.fenwick = new FenwickTree(nums.length);
        
        for (int i = 0; i < nums.length; i++) {
            fenwick.update(i, nums[i]);
        }
    }
    
    public void update(int index, int val) {
        int delta = val - nums[index];
        nums[index] = val;
        fenwick.update(index, delta);
    }
    
    public int sumRange(int left, int right) {
        return fenwick.rangeSum(left, right);
    }
}
```

### Problem 2: Count of Smaller Numbers After Self (LeetCode 315)

```java
/**
 * Count smaller elements to the right
 * 
 * Time: O(n log n), Space: O(n)
 */
public List<Integer> countSmaller(int[] nums) {
    int n = nums.length;
    Integer[] result = new Integer[n];
    
    // Coordinate compression
    int[] sorted = nums.clone();
    Arrays.sort(sorted);
    
    Map<Integer, Integer> rank = new HashMap<>();
    int r = 1;
    for (int num : sorted) {
        if (!rank.containsKey(num)) {
            rank.put(num, r++);
        }
    }
    
    FenwickTree fenwick = new FenwickTree(rank.size());
    
    // Process from right to left
    for (int i = n - 1; i >= 0; i--) {
        int r = rank.get(nums[i]);
        result[i] = fenwick.prefixSum(r - 2);  // Count smaller
        fenwick.update(r - 1, 1);
    }
    
    return Arrays.asList(result);
}
```

### Problem 3: Range Sum Query 2D - Mutable (LeetCode 308)

```java
/**
 * Using 2D Fenwick Tree
 */
class NumMatrix {
    
    private int[][] matrix;
    private FenwickTree2D fenwick;
    private int m, n;
    
    public NumMatrix(int[][] matrix) {
        if (matrix.length == 0 || matrix[0].length == 0) {
            return;
        }
        
        this.m = matrix.length;
        this.n = matrix[0].length;
        this.matrix = new int[m][n];
        this.fenwick = new FenwickTree2D(m, n);
        
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                update(i, j, matrix[i][j]);
            }
        }
    }
    
    public void update(int row, int col, int val) {
        int delta = val - matrix[row][col];
        matrix[row][col] = val;
        fenwick.update(row, col, delta);
    }
    
    public int sumRegion(int row1, int col1, int row2, int col2) {
        return fenwick.rangeSum(row1, col1, row2, col2);
    }
}
```

### Problem 4: Reverse Pairs (LeetCode 493)

```java
/**
 * Count pairs where i < j and nums[i] > 2 * nums[j]
 * 
 * Time: O(n log n), Space: O(n)
 */
public int reversePairs(int[] nums) {
    int n = nums.length;
    
    // Coordinate compression
    long[] sorted = new long[n * 2];
    for (int i = 0; i < n; i++) {
        sorted[i] = nums[i];
        sorted[i + n] = (long) nums[i] * 2;
    }
    Arrays.sort(sorted);
    
    Map<Long, Integer> rank = new HashMap<>();
    int r = 1;
    for (long num : sorted) {
        if (!rank.containsKey(num)) {
            rank.put(num, r++);
        }
    }
    
    FenwickTree fenwick = new FenwickTree(rank.size());
    int count = 0;
    
    for (int i = n - 1; i >= 0; i--) {
        int r1 = rank.get((long) nums[i] * 2);
        count += fenwick.prefixSum(r1 - 2);
        
        int r2 = rank.get((long) nums[i]);
        fenwick.update(r2 - 1, 1);
    }
    
    return count;
}
```

---

## Real-World Use Cases

### 1. Time-Series Aggregations

```java
/**
 * Efficient aggregations over time windows
 */
class TimeSeriesAggregator {
    
    private SegmentTree segmentTree;
    private Map<Long, Integer> timestampToIndex;
    
    public TimeSeriesAggregator(long[] timestamps, int[] values) {
        timestampToIndex = new HashMap<>();
        
        for (int i = 0; i < timestamps.length; i++) {
            timestampToIndex.put(timestamps[i], i);
        }
        
        segmentTree = new SegmentTree(values);
    }
    
    public int aggregateRange(long startTime, long endTime) {
        int startIndex = timestampToIndex.get(startTime);
        int endIndex = timestampToIndex.get(endTime);
        
        return segmentTree.query(startIndex, endIndex);
    }
}
```

### 2. OLAP Cube (Data Warehousing)

```java
/**
 * Fast aggregations for analytics
 */
class OLAPCube {
    
    private FenwickTree2D fenwick;
    
    public OLAPCube(int[][] salesData) {
        int m = salesData.length;
        int n = salesData[0].length;
        fenwick = new FenwickTree2D(m, n);
        
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                fenwick.update(i, j, salesData[i][j]);
            }
        }
    }
    
    public int querySales(int region1, int product1, int region2, int product2) {
        return fenwick.rangeSum(region1, product1, region2, product2);
    }
}
```

---

## 🎯 Interview Tips

### Patterns

1. **Range Queries**: Sum, min, max in range
2. **Dynamic Arrays**: Frequent updates + queries
3. **Inversion Counting**: Smaller/larger elements
4. **2D Matrices**: Region sums

### Common Mistakes

```java
// ❌ BAD: Fenwick Tree is 1-indexed
tree[index] += value;  // Wrong!

// ✅ GOOD: Convert to 1-indexed
index++;
while (index <= n) {
    tree[index] += value;
    index += index & (-index);
}

// ❌ BAD: Using segment tree for simple prefix sum
// Use Fenwick Tree instead (simpler, faster)
```

---

**Next:** [Graph Representations](./11-Graph-Representations.md)
