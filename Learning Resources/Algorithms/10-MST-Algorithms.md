# Minimum Spanning Tree (MST) Algorithms

**Difficulty:** Medium-Hard  
**Learning Time:** 3-4 days  
**Interview Frequency:** ⭐⭐⭐⭐ (High)  
**Common In:** Google, Amazon, Network Design Problems

---

## 📚 Table of Contents

1. [MST Fundamentals](#mst-fundamentals)
2. [Kruskal's Algorithm](#kruskals-algorithm)
3. [Prim's Algorithm](#prims-algorithm)
4. [Advanced MST Problems](#advanced-mst-problems)
5. [Real-World Applications](#real-world-applications)

---

## MST Fundamentals

### Definition

**Minimum Spanning Tree:** Subset of edges that:
1. Connects all vertices (spanning)
2. Forms a tree (no cycles, V-1 edges)
3. Has minimum total weight

### Properties

1. **Unique MST:** If all edge weights are distinct, MST is unique
2. **Cut Property:** For any cut, minimum weight edge crossing cut is in some MST
3. **Cycle Property:** For any cycle, maximum weight edge is NOT in any MST
4. **Number of edges:** MST has exactly V-1 edges

### Algorithm Comparison

| Algorithm | Approach | Time Complexity | Best For |
|-----------|----------|----------------|----------|
| Kruskal | Edge-based (Union-Find) | O(E log E) | Sparse graphs |
| Prim | Vertex-based (Priority Queue) | O(E log V) | Dense graphs |

---

## Kruskal's Algorithm

**Greedy algorithm** using **Union-Find** data structure.

### Algorithm

1. Sort all edges by weight (ascending)
2. Initialize empty MST
3. For each edge (u, v) in sorted order:
   - If u and v are in different components (no cycle), add edge to MST
   - Union the components
4. Stop when MST has V-1 edges

### Implementation

```java
/**
 * Kruskal's Algorithm with Union-Find
 * Time: O(E log E), Space: O(V)
 */
class KruskalMST {
    
    static class Edge implements Comparable<Edge> {
        int u;
        int v;
        int weight;
        
        Edge(int u, int v, int weight) {
            this.u = u;
            this.v = v;
            this.weight = weight;
        }
        
        @Override
        public int compareTo(Edge other) {
            return Integer.compare(this.weight, other.weight);
        }
    }
    
    /**
     * Union-Find (Disjoint Set Union)
     */
    static class UnionFind {
        int[] parent;
        int[] rank;
        
        UnionFind(int n) {
            parent = new int[n];
            rank = new int[n];
            for (int i = 0; i < n; i++) {
                parent[i] = i;
                rank[i] = 0;
            }
        }
        
        int find(int x) {
            if (parent[x] != x) {
                parent[x] = find(parent[x]);  // Path compression
            }
            return parent[x];
        }
        
        boolean union(int x, int y) {
            int rootX = find(x);
            int rootY = find(y);
            
            if (rootX == rootY) {
                return false;  // Already in same set
            }
            
            // Union by rank
            if (rank[rootX] < rank[rootY]) {
                parent[rootX] = rootY;
            } else if (rank[rootX] > rank[rootY]) {
                parent[rootY] = rootX;
            } else {
                parent[rootY] = rootX;
                rank[rootX]++;
            }
            
            return true;
        }
    }
    
    /**
     * Find MST using Kruskal's algorithm
     */
    public List<Edge> kruskalMST(int n, List<Edge> edges) {
        // Sort edges by weight
        Collections.sort(edges);
        
        UnionFind uf = new UnionFind(n);
        List<Edge> mst = new ArrayList<>();
        
        for (Edge edge : edges) {
            if (uf.union(edge.u, edge.v)) {
                mst.add(edge);
                
                if (mst.size() == n - 1) {
                    break;  // MST complete
                }
            }
        }
        
        return mst;
    }
    
    /**
     * Calculate total MST weight
     */
    public int getMSTWeight(int n, List<Edge> edges) {
        List<Edge> mst = kruskalMST(n, edges);
        return mst.stream().mapToInt(e -> e.weight).sum();
    }
}
```

---

### LeetCode Problem: Min Cost to Connect All Points

**LeetCode 1584**

```java
/**
 * Connect all points with minimum total Manhattan distance
 * Time: O(n² log n), Space: O(n²)
 */
class Solution {
    public int minCostConnectPoints(int[][] points) {
        int n = points.length;
        
        // Generate all edges
        List<Edge> edges = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                int dist = Math.abs(points[i][0] - points[j][0]) +
                          Math.abs(points[i][1] - points[j][1]);
                edges.add(new Edge(i, j, dist));
            }
        }
        
        // Kruskal's algorithm
        Collections.sort(edges);
        
        UnionFind uf = new UnionFind(n);
        int totalCost = 0;
        int edgesAdded = 0;
        
        for (Edge edge : edges) {
            if (uf.union(edge.u, edge.v)) {
                totalCost += edge.weight;
                edgesAdded++;
                
                if (edgesAdded == n - 1) {
                    break;
                }
            }
        }
        
        return totalCost;
    }
    
    static class Edge implements Comparable<Edge> {
        int u, v, weight;
        
        Edge(int u, int v, int weight) {
            this.u = u;
            this.v = v;
            this.weight = weight;
        }
        
        @Override
        public int compareTo(Edge other) {
            return Integer.compare(this.weight, other.weight);
        }
    }
    
    static class UnionFind {
        int[] parent;
        int[] rank;
        
        UnionFind(int n) {
            parent = new int[n];
            rank = new int[n];
            for (int i = 0; i < n; i++) {
                parent[i] = i;
            }
        }
        
        int find(int x) {
            if (parent[x] != x) {
                parent[x] = find(parent[x]);
            }
            return parent[x];
        }
        
        boolean union(int x, int y) {
            int rootX = find(x);
            int rootY = find(y);
            
            if (rootX == rootY) return false;
            
            if (rank[rootX] < rank[rootY]) {
                parent[rootX] = rootY;
            } else if (rank[rootX] > rank[rootY]) {
                parent[rootY] = rootX;
            } else {
                parent[rootY] = rootX;
                rank[rootX]++;
            }
            
            return true;
        }
    }
}
```

---

## Prim's Algorithm

**Greedy algorithm** using **Priority Queue**.

### Algorithm

1. Start with arbitrary vertex in MST
2. Maintain min heap of edges crossing cut (MST vs non-MST vertices)
3. Repeatedly:
   - Extract minimum weight edge from heap
   - If edge connects to new vertex, add to MST
   - Add all edges from new vertex to heap
4. Stop when all vertices in MST

### Implementation

```java
/**
 * Prim's Algorithm with Priority Queue
 * Time: O(E log V), Space: O(V)
 */
class PrimMST {
    
    static class Edge {
        int to;
        int weight;
        
        Edge(int to, int weight) {
            this.to = to;
            this.weight = weight;
        }
    }
    
    static class Node implements Comparable<Node> {
        int vertex;
        int weight;
        
        Node(int vertex, int weight) {
            this.vertex = vertex;
            this.weight = weight;
        }
        
        @Override
        public int compareTo(Node other) {
            return Integer.compare(this.weight, other.weight);
        }
    }
    
    /**
     * Find MST using Prim's algorithm
     */
    public List<int[]> primMST(List<List<Edge>> graph) {
        int n = graph.size();
        boolean[] inMST = new boolean[n];
        List<int[]> mst = new ArrayList<>();  // [from, to, weight]
        
        PriorityQueue<Node> pq = new PriorityQueue<>();
        pq.offer(new Node(0, 0));
        
        while (!pq.isEmpty()) {
            Node current = pq.poll();
            int u = current.vertex;
            
            if (inMST[u]) continue;
            
            inMST[u] = true;
            
            if (current.weight > 0) {  // Not the starting vertex
                mst.add(new int[]{-1, u, current.weight});  // Simplified
            }
            
            for (Edge edge : graph.get(u)) {
                int v = edge.to;
                if (!inMST[v]) {
                    pq.offer(new Node(v, edge.weight));
                }
            }
        }
        
        return mst;
    }
    
    /**
     * Calculate total MST weight
     */
    public int getMSTWeight(List<List<Edge>> graph) {
        int n = graph.size();
        boolean[] inMST = new boolean[n];
        int totalWeight = 0;
        
        PriorityQueue<Node> pq = new PriorityQueue<>();
        pq.offer(new Node(0, 0));
        
        while (!pq.isEmpty()) {
            Node current = pq.poll();
            int u = current.vertex;
            
            if (inMST[u]) continue;
            
            inMST[u] = true;
            totalWeight += current.weight;
            
            for (Edge edge : graph.get(u)) {
                if (!inMST[edge.to]) {
                    pq.offer(new Node(edge.to, edge.weight));
                }
            }
        }
        
        return totalWeight;
    }
}
```

---

### Prim's with Edge Tracking

```java
/**
 * Prim's algorithm tracking parent for edge reconstruction
 */
class PrimMSTWithParent {
    
    static class Edge {
        int to;
        int weight;
        
        Edge(int to, int weight) {
            this.to = to;
            this.weight = weight;
        }
    }
    
    public int primMST(List<List<Edge>> graph) {
        int n = graph.size();
        boolean[] visited = new boolean[n];
        int[] minCost = new int[n];
        int[] parent = new int[n];
        Arrays.fill(minCost, Integer.MAX_VALUE);
        Arrays.fill(parent, -1);
        
        PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[1] - b[1]);
        pq.offer(new int[]{0, 0});  // {vertex, cost}
        minCost[0] = 0;
        
        int totalCost = 0;
        
        while (!pq.isEmpty()) {
            int[] current = pq.poll();
            int u = current[0];
            int cost = current[1];
            
            if (visited[u]) continue;
            
            visited[u] = true;
            totalCost += cost;
            
            for (Edge edge : graph.get(u)) {
                int v = edge.to;
                if (!visited[v] && edge.weight < minCost[v]) {
                    minCost[v] = edge.weight;
                    parent[v] = u;
                    pq.offer(new int[]{v, edge.weight});
                }
            }
        }
        
        return totalCost;
    }
}
```

---

## Advanced MST Problems

### Problem 1: Connecting Cities With Minimum Cost

**LeetCode 1135**

```java
/**
 * Minimum cost to connect all cities (Kruskal approach)
 * Time: O(E log E), Space: O(V)
 */
class Solution {
    public int minimumCost(int n, int[][] connections) {
        Arrays.sort(connections, (a, b) -> Integer.compare(a[2], b[2]));
        
        UnionFind uf = new UnionFind(n);
        int totalCost = 0;
        int edgesAdded = 0;
        
        for (int[] conn : connections) {
            int u = conn[0] - 1;  // Convert to 0-indexed
            int v = conn[1] - 1;
            int cost = conn[2];
            
            if (uf.union(u, v)) {
                totalCost += cost;
                edgesAdded++;
                
                if (edgesAdded == n - 1) {
                    return totalCost;
                }
            }
        }
        
        return -1;  // Cannot connect all cities
    }
    
    static class UnionFind {
        int[] parent;
        int[] rank;
        
        UnionFind(int n) {
            parent = new int[n];
            rank = new int[n];
            for (int i = 0; i < n; i++) {
                parent[i] = i;
            }
        }
        
        int find(int x) {
            if (parent[x] != x) {
                parent[x] = find(parent[x]);
            }
            return parent[x];
        }
        
        boolean union(int x, int y) {
            int rootX = find(x);
            int rootY = find(y);
            
            if (rootX == rootY) return false;
            
            if (rank[rootX] < rank[rootY]) {
                parent[rootX] = rootY;
            } else if (rank[rootX] > rank[rootY]) {
                parent[rootY] = rootX;
            } else {
                parent[rootY] = rootX;
                rank[rootX]++;
            }
            
            return true;
        }
    }
}
```

---

### Problem 2: Critical Connections

**LeetCode 1192** (Tarjan's Algorithm)

```java
/**
 * Find bridges (critical connections) in network
 * Time: O(V + E), Space: O(V)
 */
class Solution {
    private int time = 0;
    
    public List<List<Integer>> criticalConnections(int n, List<List<Integer>> connections) {
        // Build adjacency list
        List<List<Integer>> graph = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            graph.add(new ArrayList<>());
        }
        
        for (List<Integer> conn : connections) {
            int u = conn.get(0);
            int v = conn.get(1);
            graph.get(u).add(v);
            graph.get(v).add(u);
        }
        
        int[] disc = new int[n];  // Discovery time
        int[] low = new int[n];   // Lowest reachable vertex
        boolean[] visited = new boolean[n];
        List<List<Integer>> result = new ArrayList<>();
        
        dfs(0, -1, graph, disc, low, visited, result);
        
        return result;
    }
    
    private void dfs(int u, int parent, List<List<Integer>> graph,
                     int[] disc, int[] low, boolean[] visited,
                     List<List<Integer>> result) {
        visited[u] = true;
        disc[u] = low[u] = time++;
        
        for (int v : graph.get(u)) {
            if (v == parent) continue;
            
            if (!visited[v]) {
                dfs(v, u, graph, disc, low, visited, result);
                
                low[u] = Math.min(low[u], low[v]);
                
                // Bridge condition: no back edge from subtree of v to ancestors of u
                if (low[v] > disc[u]) {
                    result.add(Arrays.asList(u, v));
                }
            } else {
                low[u] = Math.min(low[u], disc[v]);
            }
        }
    }
}
```

---

## Real-World Data Engineering Applications

### 1. Network Cable Layout Optimization

```java
/**
 * Minimize cost of laying cables between data centers
 */
class NetworkCableOptimizer {
    
    static class DataCenter {
        String id;
        double lat;
        double lon;
        
        DataCenter(String id, double lat, double lon) {
            this.id = id;
            this.lat = lat;
            this.lon = lon;
        }
    }
    
    static class Cable implements Comparable<Cable> {
        int from;
        int to;
        double cost;
        
        Cable(int from, int to, double cost) {
            this.from = from;
            this.to = to;
            this.cost = cost;
        }
        
        @Override
        public int compareTo(Cable other) {
            return Double.compare(this.cost, other.cost);
        }
    }
    
    /**
     * Calculate optimal cable layout using Kruskal
     */
    public List<Cable> optimizeCableLayout(List<DataCenter> centers) {
        int n = centers.size();
        
        // Generate all possible cables with costs
        List<Cable> cables = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                double cost = calculateCableCost(centers.get(i), centers.get(j));
                cables.add(new Cable(i, j, cost));
            }
        }
        
        // Kruskal's algorithm
        Collections.sort(cables);
        
        UnionFind uf = new UnionFind(n);
        List<Cable> optimalLayout = new ArrayList<>();
        
        for (Cable cable : cables) {
            if (uf.union(cable.from, cable.to)) {
                optimalLayout.add(cable);
                
                if (optimalLayout.size() == n - 1) {
                    break;
                }
            }
        }
        
        return optimalLayout;
    }
    
    private double calculateCableCost(DataCenter a, DataCenter b) {
        // Haversine formula for distance
        double lat1 = Math.toRadians(a.lat);
        double lat2 = Math.toRadians(b.lat);
        double lon1 = Math.toRadians(a.lon);
        double lon2 = Math.toRadians(b.lon);
        
        double dLat = lat2 - lat1;
        double dLon = lon2 - lon1;
        
        double aVal = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                     Math.cos(lat1) * Math.cos(lat2) *
                     Math.sin(dLon / 2) * Math.sin(dLon / 2);
        
        double c = 2 * Math.atan2(Math.sqrt(aVal), Math.sqrt(1 - aVal));
        
        double distanceKm = 6371 * c;  // Earth radius in km
        double costPerKm = 1000;  // $1000 per km
        
        return distanceKm * costPerKm;
    }
    
    static class UnionFind {
        int[] parent;
        int[] rank;
        
        UnionFind(int n) {
            parent = new int[n];
            rank = new int[n];
            for (int i = 0; i < n; i++) {
                parent[i] = i;
            }
        }
        
        int find(int x) {
            if (parent[x] != x) {
                parent[x] = find(parent[x]);
            }
            return parent[x];
        }
        
        boolean union(int x, int y) {
            int rootX = find(x);
            int rootY = find(y);
            
            if (rootX == rootY) return false;
            
            if (rank[rootX] < rank[rootY]) {
                parent[rootX] = rootY;
            } else if (rank[rootX] > rank[rootY]) {
                parent[rootY] = rootX;
            } else {
                parent[rootY] = rootX;
                rank[rootX]++;
            }
            
            return true;
        }
    }
}
```

### 2. Clustering Algorithm (Single-Link Clustering)

```java
/**
 * Use MST for clustering data points
 */
class MSTClustering {
    
    static class Point {
        double[] features;
        
        Point(double[] features) {
            this.features = features;
        }
    }
    
    static class Edge implements Comparable<Edge> {
        int u, v;
        double distance;
        
        Edge(int u, int v, double distance) {
            this.u = u;
            this.v = v;
            this.distance = distance;
        }
        
        @Override
        public int compareTo(Edge other) {
            return Double.compare(this.distance, other.distance);
        }
    }
    
    /**
     * Cluster points by removing k-1 largest edges from MST
     */
    public List<List<Integer>> cluster(List<Point> points, int k) {
        int n = points.size();
        
        // Generate all edges
        List<Edge> edges = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                double dist = euclideanDistance(points.get(i), points.get(j));
                edges.add(new Edge(i, j, dist));
            }
        }
        
        // Build MST
        Collections.sort(edges);
        
        UnionFind uf = new UnionFind(n);
        List<Edge> mstEdges = new ArrayList<>();
        
        for (Edge edge : edges) {
            if (uf.union(edge.u, edge.v)) {
                mstEdges.add(edge);
                
                if (mstEdges.size() == n - 1) {
                    break;
                }
            }
        }
        
        // Remove k-1 largest edges to create k clusters
        Collections.sort(mstEdges, (a, b) -> Double.compare(b.distance, a.distance));
        
        UnionFind clusterUF = new UnionFind(n);
        for (int i = k - 1; i < mstEdges.size(); i++) {
            clusterUF.union(mstEdges.get(i).u, mstEdges.get(i).v);
        }
        
        // Group points by cluster
        Map<Integer, List<Integer>> clusters = new HashMap<>();
        for (int i = 0; i < n; i++) {
            int root = clusterUF.find(i);
            clusters.computeIfAbsent(root, x -> new ArrayList<>()).add(i);
        }
        
        return new ArrayList<>(clusters.values());
    }
    
    private double euclideanDistance(Point a, Point b) {
        double sum = 0;
        for (int i = 0; i < a.features.length; i++) {
            double diff = a.features[i] - b.features[i];
            sum += diff * diff;
        }
        return Math.sqrt(sum);
    }
    
    static class UnionFind {
        int[] parent;
        
        UnionFind(int n) {
            parent = new int[n];
            for (int i = 0; i < n; i++) {
                parent[i] = i;
            }
        }
        
        int find(int x) {
            if (parent[x] != x) {
                parent[x] = find(parent[x]);
            }
            return parent[x];
        }
        
        boolean union(int x, int y) {
            int rootX = find(x);
            int rootY = find(y);
            if (rootX == rootY) return false;
            parent[rootX] = rootY;
            return true;
        }
    }
}
```

---

## 🎯 Interview Tips

### Kruskal vs Prim

**Use Kruskal when:**
- Sparse graph (few edges)
- Edges given as list
- Need to sort edges anyway

**Use Prim when:**
- Dense graph (many edges)
- Graph given as adjacency list
- Need incremental MST construction

### Common Mistakes

1. **Forgetting to check connectivity**
   ```java
   // After Kruskal, verify MST has n-1 edges
   if (mst.size() != n - 1) {
       return -1;  // Graph not connected
   }
   ```

2. **Not using Union-Find optimizations**
   ```java
   // ✅ Use path compression + union by rank
   // Gives amortized O(α(n)) ≈ O(1)
   ```

3. **Comparing wrong weights in Prim**
   ```java
   // ❌ Wrong - comparing total distance
   if (totalDist < minCost[v])
   
   // ✅ Correct - comparing edge weight
   if (edge.weight < minCost[v])
   ```

---

## 📊 Complexity Summary

| Algorithm | Time | Space | Best For |
|-----------|------|-------|----------|
| Kruskal | O(E log E) | O(V) | Sparse graphs |
| Prim (binary heap) | O(E log V) | O(V) | Dense graphs |
| Prim (Fibonacci heap) | O(E + V log V) | O(V) | Theoretical |

---

**Next:** [Tree Algorithms](./11-Tree-Algorithms.md)
