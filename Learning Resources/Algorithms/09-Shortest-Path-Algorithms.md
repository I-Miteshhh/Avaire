# Shortest Path Algorithms

**Difficulty:** Hard  
**Learning Time:** 5-7 days  
**Interview Frequency:** ⭐⭐⭐⭐⭐ (Very High)  
**Common In:** Google, Amazon, Facebook, System Design

---

## 📚 Table of Contents

1. [Single-Source Shortest Path](#single-source-shortest-path)
2. [Dijkstra's Algorithm](#dijkstras-algorithm)
3. [Bellman-Ford Algorithm](#bellman-ford-algorithm)
4. [All-Pairs Shortest Path](#all-pairs-shortest-path)
5. [A* Algorithm](#a-algorithm)
6. [Real-World Applications](#real-world-applications)

---

## Single-Source Shortest Path

Finding shortest path from **one source** to all other vertices.

### Algorithm Comparison

| Algorithm | Graph Type | Edge Weights | Time Complexity | Space |
|-----------|-----------|--------------|-----------------|-------|
| BFS | Unweighted | N/A | O(V + E) | O(V) |
| Dijkstra | Weighted | Non-negative | O((V+E) log V) | O(V) |
| Bellman-Ford | Weighted | Any (can detect negative cycles) | O(VE) | O(V) |

---

## Dijkstra's Algorithm

**Greedy algorithm** for shortest path with **non-negative** edge weights.

### Algorithm

1. Initialize distances: `dist[source] = 0`, rest = ∞
2. Use min heap (priority queue) with vertices by distance
3. Pop vertex with minimum distance
4. Relax all neighbors: if `dist[u] + weight(u,v) < dist[v]`, update `dist[v]`
5. Repeat until heap empty

### Implementation

```java
/**
 * Dijkstra's Algorithm - Shortest Path from Source
 * Time: O((V + E) log V) with binary heap
 * Space: O(V)
 */
class DijkstraShortestPath {
    
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
        int distance;
        
        Node(int vertex, int distance) {
            this.vertex = vertex;
            this.distance = distance;
        }
        
        @Override
        public int compareTo(Node other) {
            return Integer.compare(this.distance, other.distance);
        }
    }
    
    public int[] dijkstra(List<List<Edge>> graph, int source) {
        int n = graph.size();
        int[] dist = new int[n];
        Arrays.fill(dist, Integer.MAX_VALUE);
        dist[source] = 0;
        
        PriorityQueue<Node> pq = new PriorityQueue<>();
        pq.offer(new Node(source, 0));
        
        while (!pq.isEmpty()) {
            Node current = pq.poll();
            int u = current.vertex;
            int d = current.distance;
            
            // Skip if already processed with better distance
            if (d > dist[u]) continue;
            
            // Relax neighbors
            for (Edge edge : graph.get(u)) {
                int v = edge.to;
                int newDist = dist[u] + edge.weight;
                
                if (newDist < dist[v]) {
                    dist[v] = newDist;
                    pq.offer(new Node(v, newDist));
                }
            }
        }
        
        return dist;
    }
    
    /**
     * Dijkstra with path reconstruction
     */
    public List<Integer> dijkstraWithPath(List<List<Edge>> graph, int source, int target) {
        int n = graph.size();
        int[] dist = new int[n];
        int[] parent = new int[n];
        Arrays.fill(dist, Integer.MAX_VALUE);
        Arrays.fill(parent, -1);
        dist[source] = 0;
        
        PriorityQueue<Node> pq = new PriorityQueue<>();
        pq.offer(new Node(source, 0));
        
        while (!pq.isEmpty()) {
            Node current = pq.poll();
            int u = current.vertex;
            
            if (u == target) break;  // Found shortest path to target
            
            if (current.distance > dist[u]) continue;
            
            for (Edge edge : graph.get(u)) {
                int v = edge.to;
                int newDist = dist[u] + edge.weight;
                
                if (newDist < dist[v]) {
                    dist[v] = newDist;
                    parent[v] = u;
                    pq.offer(new Node(v, newDist));
                }
            }
        }
        
        // Reconstruct path
        if (dist[target] == Integer.MAX_VALUE) {
            return Collections.emptyList();  // No path
        }
        
        List<Integer> path = new ArrayList<>();
        for (int at = target; at != -1; at = parent[at]) {
            path.add(at);
        }
        Collections.reverse(path);
        return path;
    }
}
```

---

### LeetCode Problem: Network Delay Time

**LeetCode 743**

```java
/**
 * Network delay time = shortest time for signal to reach all nodes
 * Time: O((E + V) log V), Space: O(E + V)
 */
class Solution {
    public int networkDelayTime(int[][] times, int n, int k) {
        // Build adjacency list
        List<List<int[]>> graph = new ArrayList<>();
        for (int i = 0; i <= n; i++) {
            graph.add(new ArrayList<>());
        }
        
        for (int[] time : times) {
            int u = time[0];
            int v = time[1];
            int w = time[2];
            graph.get(u).add(new int[]{v, w});
        }
        
        // Dijkstra
        int[] dist = new int[n + 1];
        Arrays.fill(dist, Integer.MAX_VALUE);
        dist[k] = 0;
        
        PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[1] - b[1]);
        pq.offer(new int[]{k, 0});
        
        while (!pq.isEmpty()) {
            int[] current = pq.poll();
            int u = current[0];
            int d = current[1];
            
            if (d > dist[u]) continue;
            
            for (int[] edge : graph.get(u)) {
                int v = edge[0];
                int w = edge[1];
                int newDist = dist[u] + w;
                
                if (newDist < dist[v]) {
                    dist[v] = newDist;
                    pq.offer(new int[]{v, newDist});
                }
            }
        }
        
        // Find maximum distance
        int maxDist = 0;
        for (int i = 1; i <= n; i++) {
            if (dist[i] == Integer.MAX_VALUE) {
                return -1;  // Unreachable node
            }
            maxDist = Math.max(maxDist, dist[i]);
        }
        
        return maxDist;
    }
}
```

---

### LeetCode Problem: Path with Minimum Effort

**LeetCode 1631**

```java
/**
 * Find path with minimum maximum absolute difference
 * Use Dijkstra where "distance" is max effort so far
 * Time: O(mn log(mn)), Space: O(mn)
 */
class Solution {
    public int minimumEffortPath(int[][] heights) {
        int m = heights.length;
        int n = heights[0].length;
        
        int[][] effort = new int[m][n];
        for (int[] row : effort) {
            Arrays.fill(row, Integer.MAX_VALUE);
        }
        effort[0][0] = 0;
        
        PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[2] - b[2]);
        pq.offer(new int[]{0, 0, 0});  // {row, col, effort}
        
        int[][] dirs = {{0, 1}, {1, 0}, {0, -1}, {-1, 0}};
        
        while (!pq.isEmpty()) {
            int[] current = pq.poll();
            int row = current[0];
            int col = current[1];
            int eff = current[2];
            
            if (row == m - 1 && col == n - 1) {
                return eff;
            }
            
            if (eff > effort[row][col]) continue;
            
            for (int[] dir : dirs) {
                int newRow = row + dir[0];
                int newCol = col + dir[1];
                
                if (newRow >= 0 && newRow < m && newCol >= 0 && newCol < n) {
                    int newEffort = Math.max(eff, 
                        Math.abs(heights[newRow][newCol] - heights[row][col]));
                    
                    if (newEffort < effort[newRow][newCol]) {
                        effort[newRow][newCol] = newEffort;
                        pq.offer(new int[]{newRow, newCol, newEffort});
                    }
                }
            }
        }
        
        return 0;
    }
}
```

---

## Bellman-Ford Algorithm

Handles **negative edge weights** and detects **negative cycles**.

### Algorithm

1. Initialize distances: `dist[source] = 0`, rest = ∞
2. Relax all edges V-1 times
3. Check for negative cycle: if any edge can still be relaxed, negative cycle exists

### Why V-1 iterations?

Shortest path in graph without negative cycles has at most V-1 edges.

### Implementation

```java
/**
 * Bellman-Ford Algorithm
 * Time: O(VE), Space: O(V)
 */
class BellmanFord {
    
    static class Edge {
        int from;
        int to;
        int weight;
        
        Edge(int from, int to, int weight) {
            this.from = from;
            this.to = to;
            this.weight = weight;
        }
    }
    
    public int[] bellmanFord(int n, List<Edge> edges, int source) {
        int[] dist = new int[n];
        Arrays.fill(dist, Integer.MAX_VALUE);
        dist[source] = 0;
        
        // Relax all edges V-1 times
        for (int i = 0; i < n - 1; i++) {
            for (Edge edge : edges) {
                if (dist[edge.from] != Integer.MAX_VALUE) {
                    int newDist = dist[edge.from] + edge.weight;
                    if (newDist < dist[edge.to]) {
                        dist[edge.to] = newDist;
                    }
                }
            }
        }
        
        // Check for negative cycle
        for (Edge edge : edges) {
            if (dist[edge.from] != Integer.MAX_VALUE) {
                int newDist = dist[edge.from] + edge.weight;
                if (newDist < dist[edge.to]) {
                    throw new IllegalArgumentException("Negative cycle detected");
                }
            }
        }
        
        return dist;
    }
    
    /**
     * Detect negative cycle reachable from source
     */
    public boolean hasNegativeCycle(int n, List<Edge> edges, int source) {
        int[] dist = new int[n];
        Arrays.fill(dist, Integer.MAX_VALUE);
        dist[source] = 0;
        
        for (int i = 0; i < n - 1; i++) {
            for (Edge edge : edges) {
                if (dist[edge.from] != Integer.MAX_VALUE) {
                    dist[edge.to] = Math.min(dist[edge.to], 
                        dist[edge.from] + edge.weight);
                }
            }
        }
        
        for (Edge edge : edges) {
            if (dist[edge.from] != Integer.MAX_VALUE &&
                dist[edge.from] + edge.weight < dist[edge.to]) {
                return true;
            }
        }
        
        return false;
    }
}
```

---

### LeetCode Problem: Cheapest Flights Within K Stops

**LeetCode 787**

```java
/**
 * Shortest path with constraint on number of edges
 * Modified Bellman-Ford (K iterations instead of V-1)
 * Time: O(K * E), Space: O(V)
 */
class Solution {
    public int findCheapestPrice(int n, int[][] flights, int src, int dst, int k) {
        int[] dist = new int[n];
        Arrays.fill(dist, Integer.MAX_VALUE);
        dist[src] = 0;
        
        // Relax edges k+1 times (k stops = k+1 edges)
        for (int i = 0; i <= k; i++) {
            int[] temp = Arrays.copyOf(dist, n);
            
            for (int[] flight : flights) {
                int from = flight[0];
                int to = flight[1];
                int price = flight[2];
                
                if (dist[from] != Integer.MAX_VALUE) {
                    temp[to] = Math.min(temp[to], dist[from] + price);
                }
            }
            
            dist = temp;
        }
        
        return dist[dst] == Integer.MAX_VALUE ? -1 : dist[dst];
    }
}
```

---

## All-Pairs Shortest Path

Finding shortest path between **all pairs** of vertices.

### Floyd-Warshall Algorithm

**Dynamic Programming** approach.

**Time:** O(V³), **Space:** O(V²)

### Algorithm

```
For each intermediate vertex k:
    For each source i:
        For each destination j:
            dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
```

### Implementation

```java
/**
 * Floyd-Warshall All-Pairs Shortest Path
 * Time: O(V³), Space: O(V²)
 */
class FloydWarshall {
    
    public int[][] floydWarshall(int[][] graph) {
        int n = graph.length;
        int[][] dist = new int[n][n];
        
        // Initialize distances
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                dist[i][j] = graph[i][j];
            }
        }
        
        // Try all intermediate vertices
        for (int k = 0; k < n; k++) {
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    if (dist[i][k] != Integer.MAX_VALUE && 
                        dist[k][j] != Integer.MAX_VALUE) {
                        dist[i][j] = Math.min(dist[i][j], 
                            dist[i][k] + dist[k][j]);
                    }
                }
            }
        }
        
        return dist;
    }
    
    /**
     * Floyd-Warshall with path reconstruction
     */
    public int[][] floydWarshallWithPath(int[][] graph) {
        int n = graph.length;
        int[][] dist = new int[n][n];
        int[][] next = new int[n][n];
        
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                dist[i][j] = graph[i][j];
                if (graph[i][j] != Integer.MAX_VALUE && i != j) {
                    next[i][j] = j;
                } else {
                    next[i][j] = -1;
                }
            }
        }
        
        for (int k = 0; k < n; k++) {
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    if (dist[i][k] != Integer.MAX_VALUE && 
                        dist[k][j] != Integer.MAX_VALUE &&
                        dist[i][k] + dist[k][j] < dist[i][j]) {
                        dist[i][j] = dist[i][k] + dist[k][j];
                        next[i][j] = next[i][k];
                    }
                }
            }
        }
        
        return dist;
    }
    
    /**
     * Reconstruct path
     */
    public List<Integer> reconstructPath(int[][] next, int u, int v) {
        if (next[u][v] == -1) {
            return Collections.emptyList();
        }
        
        List<Integer> path = new ArrayList<>();
        path.add(u);
        
        while (u != v) {
            u = next[u][v];
            path.add(u);
        }
        
        return path;
    }
}
```

---

### LeetCode Problem: Find the City

**LeetCode 1334**

```java
/**
 * Find city with smallest number of reachable cities within threshold
 * Time: O(n³), Space: O(n²)
 */
class Solution {
    public int findTheCity(int n, int[][] edges, int distanceThreshold) {
        int[][] dist = new int[n][n];
        
        // Initialize
        for (int i = 0; i < n; i++) {
            Arrays.fill(dist[i], Integer.MAX_VALUE / 2);
            dist[i][i] = 0;
        }
        
        for (int[] edge : edges) {
            int u = edge[0];
            int v = edge[1];
            int w = edge[2];
            dist[u][v] = w;
            dist[v][u] = w;
        }
        
        // Floyd-Warshall
        for (int k = 0; k < n; k++) {
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    dist[i][j] = Math.min(dist[i][j], dist[i][k] + dist[k][j]);
                }
            }
        }
        
        // Find city with minimum reachable cities
        int minReachable = n;
        int result = 0;
        
        for (int i = 0; i < n; i++) {
            int reachable = 0;
            for (int j = 0; j < n; j++) {
                if (i != j && dist[i][j] <= distanceThreshold) {
                    reachable++;
                }
            }
            
            if (reachable <= minReachable) {
                minReachable = reachable;
                result = i;
            }
        }
        
        return result;
    }
}
```

---

## A* Algorithm

**Heuristic-based** shortest path algorithm.

### Algorithm

Similar to Dijkstra, but uses **f(n) = g(n) + h(n)**:
- **g(n):** Actual cost from start to n
- **h(n):** Heuristic estimated cost from n to goal
- **f(n):** Total estimated cost

### Heuristic Requirements

**Admissible:** Never overestimates actual cost  
**Consistent:** h(n) ≤ cost(n, n') + h(n')

### Common Heuristics

- **Manhattan distance:** |x1-x2| + |y1-y2| (grid, 4-directional)
- **Euclidean distance:** √((x1-x2)² + (y1-y2)²) (grid, any direction)
- **Diagonal distance:** max(|x1-x2|, |y1-y2|) (grid, 8-directional)

### Implementation

```java
/**
 * A* Pathfinding Algorithm
 * Time: O(b^d) where b=branching factor, d=depth
 * Space: O(b^d)
 */
class AStar {
    
    static class Node implements Comparable<Node> {
        int x, y;
        int g;  // Cost from start
        int h;  // Heuristic cost to goal
        int f;  // Total cost = g + h
        Node parent;
        
        Node(int x, int y, int g, int h, Node parent) {
            this.x = x;
            this.y = y;
            this.g = g;
            this.h = h;
            this.f = g + h;
            this.parent = parent;
        }
        
        @Override
        public int compareTo(Node other) {
            return Integer.compare(this.f, other.f);
        }
    }
    
    /**
     * A* shortest path in grid
     */
    public List<int[]> aStar(int[][] grid, int[] start, int[] goal) {
        int m = grid.length;
        int n = grid[0].length;
        
        PriorityQueue<Node> openSet = new PriorityQueue<>();
        boolean[][] visited = new boolean[m][n];
        
        int h = manhattanDistance(start, goal);
        openSet.offer(new Node(start[0], start[1], 0, h, null));
        
        int[][] dirs = {{0, 1}, {1, 0}, {0, -1}, {-1, 0}};
        
        while (!openSet.isEmpty()) {
            Node current = openSet.poll();
            
            if (current.x == goal[0] && current.y == goal[1]) {
                return reconstructPath(current);
            }
            
            if (visited[current.x][current.y]) continue;
            visited[current.x][current.y] = true;
            
            for (int[] dir : dirs) {
                int newX = current.x + dir[0];
                int newY = current.y + dir[1];
                
                if (newX >= 0 && newX < m && newY >= 0 && newY < n &&
                    grid[newX][newY] == 0 && !visited[newX][newY]) {
                    
                    int g = current.g + 1;
                    int h = manhattanDistance(new int[]{newX, newY}, goal);
                    
                    openSet.offer(new Node(newX, newY, g, h, current));
                }
            }
        }
        
        return Collections.emptyList();  // No path found
    }
    
    private int manhattanDistance(int[] a, int[] b) {
        return Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]);
    }
    
    private List<int[]> reconstructPath(Node node) {
        List<int[]> path = new ArrayList<>();
        while (node != null) {
            path.add(new int[]{node.x, node.y});
            node = node.parent;
        }
        Collections.reverse(path);
        return path;
    }
}
```

---

## Real-World Data Engineering Applications

### 1. Network Routing (Dijkstra)

```java
/**
 * Find optimal data route in network with latency weights
 */
class DataCenterRouter {
    
    static class NetworkNode {
        String dcId;
        int latency;
        
        NetworkNode(String dcId, int latency) {
            this.dcId = dcId;
            this.latency = latency;
        }
    }
    
    public List<String> findOptimalRoute(
            Map<String, List<NetworkNode>> network,
            String source,
            String destination) {
        
        Map<String, Integer> latency = new HashMap<>();
        Map<String, String> parent = new HashMap<>();
        PriorityQueue<NetworkNode> pq = new PriorityQueue<>(
            (a, b) -> Integer.compare(a.latency, b.latency)
        );
        
        latency.put(source, 0);
        pq.offer(new NetworkNode(source, 0));
        
        while (!pq.isEmpty()) {
            NetworkNode current = pq.poll();
            String u = current.dcId;
            
            if (u.equals(destination)) break;
            
            if (current.latency > latency.getOrDefault(u, Integer.MAX_VALUE)) {
                continue;
            }
            
            for (NetworkNode neighbor : network.getOrDefault(u, Collections.emptyList())) {
                int newLatency = latency.get(u) + neighbor.latency;
                
                if (newLatency < latency.getOrDefault(neighbor.dcId, Integer.MAX_VALUE)) {
                    latency.put(neighbor.dcId, newLatency);
                    parent.put(neighbor.dcId, u);
                    pq.offer(new NetworkNode(neighbor.dcId, newLatency));
                }
            }
        }
        
        // Reconstruct path
        List<String> path = new ArrayList<>();
        String current = destination;
        while (current != null) {
            path.add(current);
            current = parent.get(current);
        }
        Collections.reverse(path);
        return path;
    }
}
```

### 2. Currency Arbitrage Detection (Bellman-Ford)

```java
/**
 * Detect arbitrage opportunities using negative cycle detection
 */
class CurrencyArbitrage {
    
    static class ExchangeRate {
        String from;
        String to;
        double rate;
        
        ExchangeRate(String from, String to, double rate) {
            this.from = from;
            this.to = to;
            this.rate = rate;
        }
    }
    
    /**
     * Convert to negative log to use Bellman-Ford
     * Arbitrage exists if negative cycle detected
     */
    public boolean hasArbitrage(List<ExchangeRate> rates) {
        Map<String, Integer> currencyIndex = new HashMap<>();
        int index = 0;
        
        for (ExchangeRate rate : rates) {
            if (!currencyIndex.containsKey(rate.from)) {
                currencyIndex.put(rate.from, index++);
            }
            if (!currencyIndex.containsKey(rate.to)) {
                currencyIndex.put(rate.to, index++);
            }
        }
        
        int n = currencyIndex.size();
        double[] dist = new double[n];
        Arrays.fill(dist, Double.MAX_VALUE);
        dist[0] = 0;
        
        // Convert rates to negative log
        List<Edge> edges = new ArrayList<>();
        for (ExchangeRate rate : rates) {
            int from = currencyIndex.get(rate.from);
            int to = currencyIndex.get(rate.to);
            double weight = -Math.log(rate.rate);
            edges.add(new Edge(from, to, weight));
        }
        
        // Bellman-Ford
        for (int i = 0; i < n - 1; i++) {
            for (Edge edge : edges) {
                if (dist[edge.from] != Double.MAX_VALUE) {
                    dist[edge.to] = Math.min(dist[edge.to], 
                        dist[edge.from] + edge.weight);
                }
            }
        }
        
        // Check for negative cycle (arbitrage)
        for (Edge edge : edges) {
            if (dist[edge.from] != Double.MAX_VALUE &&
                dist[edge.from] + edge.weight < dist[edge.to]) {
                return true;  // Arbitrage exists
            }
        }
        
        return false;
    }
    
    static class Edge {
        int from;
        int to;
        double weight;
        
        Edge(int from, int to, double weight) {
            this.from = from;
            this.to = to;
            this.weight = weight;
        }
    }
}
```

### 3. Multi-Region Data Sync (Floyd-Warshall)

```java
/**
 * Calculate sync latency between all data center pairs
 */
class DataCenterSync {
    
    public int[][] calculateAllPairsLatency(
            String[] dataCenters,
            int[][] directLatencies) {
        
        int n = dataCenters.length;
        int[][] latency = new int[n][n];
        
        // Initialize
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                latency[i][j] = directLatencies[i][j];
            }
        }
        
        // Floyd-Warshall
        for (int k = 0; k < n; k++) {
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    if (latency[i][k] != Integer.MAX_VALUE &&
                        latency[k][j] != Integer.MAX_VALUE) {
                        latency[i][j] = Math.min(latency[i][j],
                            latency[i][k] + latency[k][j]);
                    }
                }
            }
        }
        
        return latency;
    }
}
```

---

## 🎯 Interview Tips

### Algorithm Selection

**Dijkstra:**
- Single source
- Non-negative weights
- Need optimal performance

**Bellman-Ford:**
- Negative weights allowed
- Need to detect negative cycles
- Simpler to implement

**Floyd-Warshall:**
- All-pairs shortest path
- Dense graph (many edges)
- Need path between every pair

**A*:**
- Known goal vertex
- Good heuristic available
- Grid-based problems

### Common Mistakes

1. **Using Dijkstra with negative weights**
   ```java
   // ❌ Wrong - Dijkstra fails with negative weights
   // Use Bellman-Ford instead
   ```

2. **Forgetting to check for visited in Dijkstra**
   ```java
   // ❌ Wrong
   Node current = pq.poll();
   
   // ✅ Correct
   Node current = pq.poll();
   if (current.distance > dist[current.vertex]) continue;
   ```

3. **Integer overflow in Floyd-Warshall**
   ```java
   // ❌ Wrong
   dist[i][j] = Math.min(dist[i][j], dist[i][k] + dist[k][j]);
   
   // ✅ Correct - check for infinity first
   if (dist[i][k] != INF && dist[k][j] != INF) {
       dist[i][j] = Math.min(dist[i][j], dist[i][k] + dist[k][j]);
   }
   ```

---

## 📊 Complexity Cheat Sheet

| Algorithm | Time | Space | Negative Weights? | All-Pairs? |
|-----------|------|-------|------------------|-----------|
| BFS | O(V+E) | O(V) | No (unweighted) | No |
| Dijkstra | O((V+E) log V) | O(V) | ❌ No | No |
| Bellman-Ford | O(VE) | O(V) | ✅ Yes | No |
| Floyd-Warshall | O(V³) | O(V²) | ✅ Yes | ✅ Yes |
| A* | O(b^d) | O(b^d) | No | No |

---

**Next:** [Minimum Spanning Tree Algorithms](./10-MST-Algorithms.md)
