# Union Find (Disjoint Set Union)

**Difficulty:** Intermediate-Advanced  
**Learning Time:** 1-2 weeks  
**Interview Frequency:** ⭐⭐⭐⭐ (High - Graph connectivity problems)

---

## 📚 Table of Contents

1. [Union Find Fundamentals](#union-find-fundamentals)
2. [Implementation](#implementation)
3. [Optimizations](#optimizations)
4. [Interview Problems](#interview-problems)
5. [Real-World Use Cases](#real-world-use-cases)

---

## Union Find Fundamentals

### What is Union Find?

```
Data structure to track elements partitioned into disjoint sets
Supports two operations:
1. FIND: Determine which set an element belongs to
2. UNION: Merge two sets into one

Use cases:
✅ Detect cycles in graphs
✅ Check connectivity
✅ Kruskal's MST algorithm
✅ Network connectivity
```

### Example

```
Initial: {0}, {1}, {2}, {3}, {4}

union(0, 1): {0,1}, {2}, {3}, {4}
union(2, 3): {0,1}, {2,3}, {4}
union(0, 2): {0,1,2,3}, {4}

find(1) = find(3) → true (same set)
find(1) = find(4) → false (different sets)
```

### Time Complexity

| Operation | Without Optimization | With Path Compression + Union by Rank |
|-----------|---------------------|---------------------------------------|
| **Find** | O(n) | O(α(n)) ≈ O(1)* |
| **Union** | O(n) | O(α(n)) ≈ O(1)* |

**Note:** α(n) is inverse Ackermann function, grows extremely slowly

---

## Implementation

### Naive Union Find

```java
/**
 * Basic Union Find without optimizations
 * 
 * Time: O(n) for both find and union
 */
class NaiveUnionFind {
    
    private int[] parent;
    
    public NaiveUnionFind(int n) {
        parent = new int[n];
        
        // Each element is its own parent initially
        for (int i = 0; i < n; i++) {
            parent[i] = i;
        }
    }
    
    /**
     * Find root: O(n) worst case
     */
    public int find(int x) {
        while (x != parent[x]) {
            x = parent[x];
        }
        return x;
    }
    
    /**
     * Union two sets: O(n)
     */
    public void union(int x, int y) {
        int rootX = find(x);
        int rootY = find(y);
        
        if (rootX != rootY) {
            parent[rootX] = rootY;
        }
    }
    
    /**
     * Check if connected: O(n)
     */
    public boolean connected(int x, int y) {
        return find(x) == find(y);
    }
}
```

---

## Optimizations

### 1. Path Compression

```java
/**
 * Flatten tree during find operation
 * Makes subsequent finds faster
 */
public int findWithPathCompression(int x) {
    if (x != parent[x]) {
        parent[x] = findWithPathCompression(parent[x]);  // Recursive compression
    }
    return parent[x];
}

// Iterative version
public int findIterative(int x) {
    int root = x;
    
    // Find root
    while (root != parent[root]) {
        root = parent[root];
    }
    
    // Compress path
    while (x != root) {
        int next = parent[x];
        parent[x] = root;
        x = next;
    }
    
    return root;
}
```

### 2. Union by Rank

```java
/**
 * Attach smaller tree under larger tree
 * Keeps tree height small
 */
class UnionFindByRank {
    
    private int[] parent;
    private int[] rank;  // Tree height
    
    public UnionFindByRank(int n) {
        parent = new int[n];
        rank = new int[n];
        
        for (int i = 0; i < n; i++) {
            parent[i] = i;
            rank[i] = 0;
        }
    }
    
    public int find(int x) {
        if (x != parent[x]) {
            parent[x] = find(parent[x]);  // Path compression
        }
        return parent[x];
    }
    
    public void union(int x, int y) {
        int rootX = find(x);
        int rootY = find(y);
        
        if (rootX == rootY) {
            return;
        }
        
        // Attach smaller rank tree under larger rank tree
        if (rank[rootX] < rank[rootY]) {
            parent[rootX] = rootY;
        } else if (rank[rootX] > rank[rootY]) {
            parent[rootY] = rootX;
        } else {
            parent[rootY] = rootX;
            rank[rootX]++;
        }
    }
    
    public boolean connected(int x, int y) {
        return find(x) == find(y);
    }
}
```

### 3. Union by Size

```java
/**
 * Attach smaller set to larger set
 * Alternative to union by rank
 */
class UnionFindBySize {
    
    private int[] parent;
    private int[] size;  // Set size
    
    public UnionFindBySize(int n) {
        parent = new int[n];
        size = new int[n];
        
        for (int i = 0; i < n; i++) {
            parent[i] = i;
            size[i] = 1;
        }
    }
    
    public int find(int x) {
        if (x != parent[x]) {
            parent[x] = find(parent[x]);
        }
        return parent[x];
    }
    
    public void union(int x, int y) {
        int rootX = find(x);
        int rootY = find(y);
        
        if (rootX == rootY) {
            return;
        }
        
        // Attach smaller set to larger set
        if (size[rootX] < size[rootY]) {
            parent[rootX] = rootY;
            size[rootY] += size[rootX];
        } else {
            parent[rootY] = rootX;
            size[rootX] += size[rootY];
        }
    }
    
    public int getSize(int x) {
        return size[find(x)];
    }
}
```

### Complete Optimized Union Find

```java
/**
 * Production-grade Union Find with all optimizations
 */
public class UnionFind {
    
    private int[] parent;
    private int[] rank;
    private int count;  // Number of disjoint sets
    
    public UnionFind(int n) {
        parent = new int[n];
        rank = new int[n];
        count = n;
        
        for (int i = 0; i < n; i++) {
            parent[i] = i;
            rank[i] = 0;
        }
    }
    
    /**
     * Find with path compression: O(α(n))
     */
    public int find(int x) {
        if (x != parent[x]) {
            parent[x] = find(parent[x]);
        }
        return parent[x];
    }
    
    /**
     * Union by rank: O(α(n))
     */
    public boolean union(int x, int y) {
        int rootX = find(x);
        int rootY = find(y);
        
        if (rootX == rootY) {
            return false;  // Already in same set
        }
        
        if (rank[rootX] < rank[rootY]) {
            parent[rootX] = rootY;
        } else if (rank[rootX] > rank[rootY]) {
            parent[rootY] = rootX;
        } else {
            parent[rootY] = rootX;
            rank[rootX]++;
        }
        
        count--;
        return true;
    }
    
    /**
     * Check if connected: O(α(n))
     */
    public boolean connected(int x, int y) {
        return find(x) == find(y);
    }
    
    /**
     * Get number of disjoint sets: O(1)
     */
    public int getCount() {
        return count;
    }
}
```

---

## Interview Problems

### Problem 1: Number of Connected Components (LeetCode 323)

```java
/**
 * Find number of connected components in undirected graph
 * 
 * Time: O(E * α(V)) where E = edges, V = vertices
 * Space: O(V)
 */
public int countComponents(int n, int[][] edges) {
    UnionFind uf = new UnionFind(n);
    
    for (int[] edge : edges) {
        uf.union(edge[0], edge[1]);
    }
    
    return uf.getCount();
}
```

### Problem 2: Redundant Connection (LeetCode 684)

```java
/**
 * Find edge that creates a cycle in graph
 * 
 * Time: O(N * α(N))
 * Space: O(N)
 */
public int[] findRedundantConnection(int[][] edges) {
    int n = edges.length;
    UnionFind uf = new UnionFind(n + 1);
    
    for (int[] edge : edges) {
        if (!uf.union(edge[0], edge[1])) {
            return edge;  // Creates cycle
        }
    }
    
    return new int[0];
}
```

### Problem 3: Accounts Merge (LeetCode 721)

```java
/**
 * Merge accounts belonging to same person
 * 
 * Example: [["John","john@mail.com","john_work@mail.com"],
 *           ["John","john_work@mail.com","john_home@mail.com"]]
 *       → [["John","john@mail.com","john_home@mail.com","john_work@mail.com"]]
 * 
 * Time: O(N log N) where N = total emails
 */
public List<List<String>> accountsMerge(List<List<String>> accounts) {
    Map<String, String> emailToName = new HashMap<>();
    Map<String, Integer> emailToId = new HashMap<>();
    int id = 0;
    
    // Assign ID to each unique email
    for (List<String> account : accounts) {
        String name = account.get(0);
        
        for (int i = 1; i < account.size(); i++) {
            String email = account.get(i);
            emailToName.put(email, name);
            
            if (!emailToId.containsKey(email)) {
                emailToId.put(email, id++);
            }
        }
    }
    
    UnionFind uf = new UnionFind(id);
    
    // Union emails in same account
    for (List<String> account : accounts) {
        int firstEmailId = emailToId.get(account.get(1));
        
        for (int i = 2; i < account.size(); i++) {
            int emailId = emailToId.get(account.get(i));
            uf.union(firstEmailId, emailId);
        }
    }
    
    // Group emails by root
    Map<Integer, List<String>> components = new HashMap<>();
    
    for (Map.Entry<String, Integer> entry : emailToId.entrySet()) {
        String email = entry.getKey();
        int emailId = entry.getValue();
        int root = uf.find(emailId);
        
        components.computeIfAbsent(root, k -> new ArrayList<>()).add(email);
    }
    
    // Build result
    List<List<String>> result = new ArrayList<>();
    
    for (List<String> emails : components.values()) {
        Collections.sort(emails);
        String name = emailToName.get(emails.get(0));
        
        List<String> account = new ArrayList<>();
        account.add(name);
        account.addAll(emails);
        
        result.add(account);
    }
    
    return result;
}
```

### Problem 4: Most Stones Removed (LeetCode 947)

```java
/**
 * Remove maximum stones where stone shares row or column
 * 
 * Time: O(N * α(N))
 * Space: O(N)
 */
public int removeStones(int[][] stones) {
    int n = stones.length;
    UnionFind uf = new UnionFind(20000);  // Max coordinate value
    
    for (int[] stone : stones) {
        int row = stone[0];
        int col = stone[1] + 10000;  // Offset to avoid collision
        uf.union(row, col);
    }
    
    Set<Integer> roots = new HashSet<>();
    for (int[] stone : stones) {
        roots.add(uf.find(stone[0]));
    }
    
    return n - roots.size();
}
```

### Problem 5: Number of Islands II (LeetCode 305)

```java
/**
 * Count islands as land is added dynamically
 * 
 * Time: O(k * α(m*n)) where k = positions
 * Space: O(m * n)
 */
public List<Integer> numIslands2(int m, int n, int[][] positions) {
    List<Integer> result = new ArrayList<>();
    UnionFind uf = new UnionFind(m * n);
    boolean[] land = new boolean[m * n];
    
    int[][] directions = {{-1,0}, {1,0}, {0,-1}, {0,1}};
    int count = 0;
    
    for (int[] pos : positions) {
        int row = pos[0];
        int col = pos[1];
        int index = row * n + col;
        
        if (land[index]) {
            result.add(count);
            continue;
        }
        
        land[index] = true;
        count++;
        
        // Check 4 neighbors
        for (int[] dir : directions) {
            int newRow = row + dir[0];
            int newCol = col + dir[1];
            int newIndex = newRow * n + newCol;
            
            if (newRow >= 0 && newRow < m && newCol >= 0 && newCol < n && land[newIndex]) {
                if (uf.union(index, newIndex)) {
                    count--;
                }
            }
        }
        
        result.add(count);
    }
    
    return result;
}
```

### Problem 6: Satisfiability of Equality Equations (LeetCode 990)

```java
/**
 * Check if equations are satisfiable
 * 
 * Example: ["a==b","b!=a"] → false
 *          ["a==b","b==c","a==c"] → true
 * 
 * Time: O(N * α(26))
 */
public boolean equationsPossible(String[] equations) {
    UnionFind uf = new UnionFind(26);
    
    // Process equality equations first
    for (String eq : equations) {
        if (eq.charAt(1) == '=') {
            int x = eq.charAt(0) - 'a';
            int y = eq.charAt(3) - 'a';
            uf.union(x, y);
        }
    }
    
    // Check inequality equations
    for (String eq : equations) {
        if (eq.charAt(1) == '!') {
            int x = eq.charAt(0) - 'a';
            int y = eq.charAt(3) - 'a';
            
            if (uf.connected(x, y)) {
                return false;  // Contradiction
            }
        }
    }
    
    return true;
}
```

### Problem 7: Smallest String With Swaps (LeetCode 1202)

```java
/**
 * Find lexicographically smallest string after allowed swaps
 * 
 * Example: s="dcab", pairs=[[0,3],[1,2]] → "bacd"
 * 
 * Time: O(N log N + E * α(N))
 */
public String smallestStringWithSwaps(String s, List<List<Integer>> pairs) {
    int n = s.length();
    UnionFind uf = new UnionFind(n);
    
    // Union pairs
    for (List<Integer> pair : pairs) {
        uf.union(pair.get(0), pair.get(1));
    }
    
    // Group indices by root
    Map<Integer, List<Integer>> components = new HashMap<>();
    
    for (int i = 0; i < n; i++) {
        int root = uf.find(i);
        components.computeIfAbsent(root, k -> new ArrayList<>()).add(i);
    }
    
    char[] result = s.toCharArray();
    
    // Sort characters in each component
    for (List<Integer> indices : components.values()) {
        List<Character> chars = new ArrayList<>();
        
        for (int i : indices) {
            chars.add(s.charAt(i));
        }
        
        Collections.sort(chars);
        Collections.sort(indices);
        
        for (int i = 0; i < indices.size(); i++) {
            result[indices.get(i)] = chars.get(i);
        }
    }
    
    return new String(result);
}
```

### Problem 8: Evaluate Division (LeetCode 399)

```java
/**
 * Evaluate division equations
 * 
 * Example: equations=[["a","b"],["b","c"]], values=[2.0,3.0]
 *          queries=[["a","c"],["b","a"]]
 *       → [6.0, 0.5]
 * 
 * Time: O(E + Q) where E = equations, Q = queries
 */
public double[] calcEquation(List<List<String>> equations, double[] values, 
                             List<List<String>> queries) {
    Map<String, String> parent = new HashMap<>();
    Map<String, Double> ratio = new HashMap<>();  // ratio to parent
    
    // Initialize
    for (List<String> eq : equations) {
        parent.put(eq.get(0), eq.get(0));
        parent.put(eq.get(1), eq.get(1));
        ratio.put(eq.get(0), 1.0);
        ratio.put(eq.get(1), 1.0);
    }
    
    // Union with ratio
    for (int i = 0; i < equations.size(); i++) {
        String x = equations.get(i).get(0);
        String y = equations.get(i).get(1);
        double value = values[i];
        
        String rootX = find(x, parent, ratio);
        String rootY = find(y, parent, ratio);
        
        if (!rootX.equals(rootY)) {
            parent.put(rootX, rootY);
            ratio.put(rootX, value * ratio.get(y) / ratio.get(x));
        }
    }
    
    // Answer queries
    double[] result = new double[queries.size()];
    
    for (int i = 0; i < queries.size(); i++) {
        String x = queries.get(i).get(0);
        String y = queries.get(i).get(1);
        
        if (!parent.containsKey(x) || !parent.containsKey(y)) {
            result[i] = -1.0;
        } else {
            String rootX = find(x, parent, ratio);
            String rootY = find(y, parent, ratio);
            
            if (!rootX.equals(rootY)) {
                result[i] = -1.0;
            } else {
                result[i] = ratio.get(x) / ratio.get(y);
            }
        }
    }
    
    return result;
}

private String find(String x, Map<String, String> parent, Map<String, Double> ratio) {
    if (!x.equals(parent.get(x))) {
        String originalParent = parent.get(x);
        String root = find(originalParent, parent, ratio);
        parent.put(x, root);
        ratio.put(x, ratio.get(x) * ratio.get(originalParent));
    }
    return parent.get(x);
}
```

---

## Real-World Use Cases

### 1. Network Connectivity (Kruskal's MST)

```java
/**
 * Find Minimum Spanning Tree using Kruskal's algorithm
 */
class KruskalMST {
    
    static class Edge implements Comparable<Edge> {
        int src, dest, weight;
        
        Edge(int src, int dest, int weight) {
            this.src = src;
            this.dest = dest;
            this.weight = weight;
        }
        
        @Override
        public int compareTo(Edge other) {
            return this.weight - other.weight;
        }
    }
    
    public List<Edge> findMST(int n, List<Edge> edges) {
        Collections.sort(edges);
        
        UnionFind uf = new UnionFind(n);
        List<Edge> mst = new ArrayList<>();
        
        for (Edge edge : edges) {
            if (uf.union(edge.src, edge.dest)) {
                mst.add(edge);
                
                if (mst.size() == n - 1) {
                    break;  // MST complete
                }
            }
        }
        
        return mst;
    }
}
```

### 2. Social Network Friends

```java
/**
 * Track friend circles in social network
 */
class FriendCircles {
    
    private UnionFind uf;
    
    public FriendCircles(int users) {
        uf = new UnionFind(users);
    }
    
    public void makeFriends(int user1, int user2) {
        uf.union(user1, user2);
    }
    
    public boolean areFriends(int user1, int user2) {
        return uf.connected(user1, user2);
    }
    
    public int countFriendCircles() {
        return uf.getCount();
    }
}
```

### 3. Percolation System

```java
/**
 * Model percolation in physical systems
 * Used in material science, hydrology
 */
class Percolation {
    
    private UnionFind uf;
    private boolean[] open;
    private int n;
    private int virtualTop;
    private int virtualBottom;
    
    public Percolation(int n) {
        this.n = n;
        this.uf = new UnionFind(n * n + 2);  // +2 for virtual sites
        this.open = new boolean[n * n];
        this.virtualTop = n * n;
        this.virtualBottom = n * n + 1;
    }
    
    public void open(int row, int col) {
        if (isOpen(row, col)) {
            return;
        }
        
        int index = row * n + col;
        open[index] = true;
        
        // Connect to virtual top
        if (row == 0) {
            uf.union(index, virtualTop);
        }
        
        // Connect to virtual bottom
        if (row == n - 1) {
            uf.union(index, virtualBottom);
        }
        
        // Connect to open neighbors
        int[][] directions = {{-1,0}, {1,0}, {0,-1}, {0,1}};
        
        for (int[] dir : directions) {
            int newRow = row + dir[0];
            int newCol = col + dir[1];
            
            if (newRow >= 0 && newRow < n && newCol >= 0 && newCol < n && 
                isOpen(newRow, newCol)) {
                uf.union(index, newRow * n + newCol);
            }
        }
    }
    
    public boolean isOpen(int row, int col) {
        return open[row * n + col];
    }
    
    public boolean percolates() {
        return uf.connected(virtualTop, virtualBottom);
    }
}
```

---

## 🎯 Interview Tips

### Union Find Patterns

1. **Graph Connectivity**: Connected components, cycles
2. **Dynamic Connectivity**: Add edges dynamically
3. **Grouping**: Merge accounts, friend circles
4. **Minimum Spanning Tree**: Kruskal's algorithm
5. **Grid Problems**: Islands, percolation

### When to Use Union Find

**Use Union Find when:**
- ✅ Need to track connected components
- ✅ Detect cycles in undirected graph
- ✅ Dynamic connectivity queries
- ✅ Minimum spanning tree (Kruskal's)
- ✅ Equivalence relationships

**Avoid Union Find when:**
- ❌ Need path information → use DFS/BFS
- ❌ Directed graph cycles → use DFS with coloring
- ❌ Need to disconnect elements → not supported

### Common Mistakes

```java
// ❌ BAD: Forgetting path compression
public int find(int x) {
    while (x != parent[x]) {
        x = parent[x];
    }
    return x;
}

// ✅ GOOD: With path compression
public int find(int x) {
    if (x != parent[x]) {
        parent[x] = find(parent[x]);
    }
    return parent[x];
}

// ❌ BAD: Not checking if already connected
uf.union(x, y);
count--;

// ✅ GOOD: Check before decrementing count
if (uf.union(x, y)) {
    count--;
}
```

---

**Next:** [Graph Representations](./11-Graph-Representations.md) — Adjacency matrix, list, edge list
