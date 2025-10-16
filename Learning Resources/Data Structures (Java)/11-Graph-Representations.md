# Graph Representations

**Difficulty:** Fundamental-Intermediate  
**Learning Time:** 1 week  
**Interview Frequency:** ⭐⭐⭐⭐⭐ (Extremely High)

---

## 📚 Table of Contents

1. [Graph Fundamentals](#graph-fundamentals)
2. [Adjacency Matrix](#adjacency-matrix)
3. [Adjacency List](#adjacency-list)
4. [Edge List](#edge-list)
5. [Comparison](#comparison)
6. [Graph Implementations](#graph-implementations)
7. [Real-World Use Cases](#real-world-use-cases)

---

## Graph Fundamentals

### Graph Types

```
1. DIRECTED vs UNDIRECTED
   - Directed: Edges have direction (A → B)
   - Undirected: Edges bidirectional (A — B)

2. WEIGHTED vs UNWEIGHTED
   - Weighted: Edges have values/costs
   - Unweighted: All edges equal (weight = 1)

3. CYCLIC vs ACYCLIC
   - Cyclic: Contains cycles
   - Acyclic: No cycles (DAG = Directed Acyclic Graph)

4. CONNECTED vs DISCONNECTED
   - Connected: Path exists between all vertices
   - Disconnected: Some vertices unreachable
```

### Graph Terminology

```
- Vertex/Node: Point in graph
- Edge: Connection between vertices
- Degree: Number of edges connected to vertex
  * In-degree: Incoming edges (directed)
  * Out-degree: Outgoing edges (directed)
- Path: Sequence of vertices
- Cycle: Path that starts and ends at same vertex
- Connected Component: Maximal set of connected vertices
```

---

## Adjacency Matrix

### Characteristics

```
2D array where matrix[i][j] = 1 if edge exists from i to j

✅ O(1) edge lookup
✅ Simple to implement
✅ Good for dense graphs
❌ O(V²) space
❌ O(V) to find all neighbors
❌ Wasteful for sparse graphs
```

### Implementation

```java
/**
 * Adjacency Matrix for Unweighted Graph
 */
class GraphMatrix {
    
    private int[][] matrix;
    private int vertices;
    private boolean directed;
    
    public GraphMatrix(int vertices, boolean directed) {
        this.vertices = vertices;
        this.directed = directed;
        this.matrix = new int[vertices][vertices];
    }
    
    /**
     * Add edge: O(1)
     */
    public void addEdge(int src, int dest) {
        matrix[src][dest] = 1;
        
        if (!directed) {
            matrix[dest][src] = 1;
        }
    }
    
    /**
     * Remove edge: O(1)
     */
    public void removeEdge(int src, int dest) {
        matrix[src][dest] = 0;
        
        if (!directed) {
            matrix[dest][src] = 0;
        }
    }
    
    /**
     * Has edge: O(1)
     */
    public boolean hasEdge(int src, int dest) {
        return matrix[src][dest] == 1;
    }
    
    /**
     * Get neighbors: O(V)
     */
    public List<Integer> getNeighbors(int vertex) {
        List<Integer> neighbors = new ArrayList<>();
        
        for (int i = 0; i < vertices; i++) {
            if (matrix[vertex][i] == 1) {
                neighbors.add(i);
            }
        }
        
        return neighbors;
    }
    
    /**
     * Print graph: O(V²)
     */
    public void print() {
        for (int i = 0; i < vertices; i++) {
            System.out.print(i + ": ");
            for (int j = 0; j < vertices; j++) {
                if (matrix[i][j] == 1) {
                    System.out.print(j + " ");
                }
            }
            System.out.println();
        }
    }
}
```

### Weighted Graph Matrix

```java
/**
 * Adjacency Matrix for Weighted Graph
 */
class WeightedGraphMatrix {
    
    private int[][] matrix;
    private int vertices;
    private static final int INF = Integer.MAX_VALUE;
    
    public WeightedGraphMatrix(int vertices) {
        this.vertices = vertices;
        this.matrix = new int[vertices][vertices];
        
        // Initialize with infinity (no edge)
        for (int i = 0; i < vertices; i++) {
            Arrays.fill(matrix[i], INF);
            matrix[i][i] = 0;  // Distance to self is 0
        }
    }
    
    public void addEdge(int src, int dest, int weight) {
        matrix[src][dest] = weight;
    }
    
    public int getWeight(int src, int dest) {
        return matrix[src][dest];
    }
    
    public boolean hasEdge(int src, int dest) {
        return matrix[src][dest] != INF;
    }
}
```

---

## Adjacency List

### Characteristics

```
Array/Map of lists where list[i] contains neighbors of vertex i

✅ O(1) add edge
✅ O(degree) to find neighbors
✅ Space-efficient for sparse graphs: O(V + E)
✅ Most common representation
❌ O(degree) to check if edge exists
❌ O(degree) to remove edge
```

### Implementation

```java
/**
 * Adjacency List using ArrayList
 */
class GraphList {
    
    private List<List<Integer>> adjList;
    private int vertices;
    private boolean directed;
    
    public GraphList(int vertices, boolean directed) {
        this.vertices = vertices;
        this.directed = directed;
        this.adjList = new ArrayList<>(vertices);
        
        for (int i = 0; i < vertices; i++) {
            adjList.add(new ArrayList<>());
        }
    }
    
    /**
     * Add edge: O(1)
     */
    public void addEdge(int src, int dest) {
        adjList.get(src).add(dest);
        
        if (!directed) {
            adjList.get(dest).add(src);
        }
    }
    
    /**
     * Remove edge: O(degree)
     */
    public void removeEdge(int src, int dest) {
        adjList.get(src).remove(Integer.valueOf(dest));
        
        if (!directed) {
            adjList.get(dest).remove(Integer.valueOf(src));
        }
    }
    
    /**
     * Has edge: O(degree)
     */
    public boolean hasEdge(int src, int dest) {
        return adjList.get(src).contains(dest);
    }
    
    /**
     * Get neighbors: O(1)
     */
    public List<Integer> getNeighbors(int vertex) {
        return adjList.get(vertex);
    }
    
    /**
     * Get degree: O(1)
     */
    public int getDegree(int vertex) {
        return adjList.get(vertex).size();
    }
    
    /**
     * Print graph: O(V + E)
     */
    public void print() {
        for (int i = 0; i < vertices; i++) {
            System.out.print(i + ": ");
            for (int neighbor : adjList.get(i)) {
                System.out.print(neighbor + " ");
            }
            System.out.println();
        }
    }
}
```

### Weighted Graph List

```java
/**
 * Weighted graph using adjacency list
 */
class WeightedGraphList {
    
    static class Edge {
        int dest;
        int weight;
        
        Edge(int dest, int weight) {
            this.dest = dest;
            this.weight = weight;
        }
    }
    
    private List<List<Edge>> adjList;
    private int vertices;
    
    public WeightedGraphList(int vertices) {
        this.vertices = vertices;
        this.adjList = new ArrayList<>(vertices);
        
        for (int i = 0; i < vertices; i++) {
            adjList.add(new ArrayList<>());
        }
    }
    
    public void addEdge(int src, int dest, int weight) {
        adjList.get(src).add(new Edge(dest, weight));
    }
    
    public List<Edge> getNeighbors(int vertex) {
        return adjList.get(vertex);
    }
}
```

### HashMap-based Adjacency List

```java
/**
 * Generic graph using HashMap
 * Useful when vertices are not sequential integers
 */
class Graph<T> {
    
    private Map<T, List<T>> adjList;
    private boolean directed;
    
    public Graph(boolean directed) {
        this.adjList = new HashMap<>();
        this.directed = directed;
    }
    
    public void addVertex(T vertex) {
        adjList.putIfAbsent(vertex, new ArrayList<>());
    }
    
    public void addEdge(T src, T dest) {
        adjList.putIfAbsent(src, new ArrayList<>());
        adjList.putIfAbsent(dest, new ArrayList<>());
        
        adjList.get(src).add(dest);
        
        if (!directed) {
            adjList.get(dest).add(src);
        }
    }
    
    public List<T> getNeighbors(T vertex) {
        return adjList.getOrDefault(vertex, new ArrayList<>());
    }
    
    public Set<T> getVertices() {
        return adjList.keySet();
    }
    
    public int getVertexCount() {
        return adjList.size();
    }
}
```

---

## Edge List

### Characteristics

```
List of all edges in graph

✅ Simple to implement
✅ Good for algorithms that process all edges (Kruskal's MST)
✅ O(1) add edge
❌ O(E) to find neighbors
❌ O(E) to check if edge exists
❌ Not efficient for graph traversal
```

### Implementation

```java
/**
 * Edge List representation
 */
class EdgeListGraph {
    
    static class Edge {
        int src;
        int dest;
        int weight;
        
        Edge(int src, int dest, int weight) {
            this.src = src;
            this.dest = dest;
            this.weight = weight;
        }
        
        Edge(int src, int dest) {
            this(src, dest, 1);
        }
    }
    
    private List<Edge> edges;
    private int vertices;
    
    public EdgeListGraph(int vertices) {
        this.vertices = vertices;
        this.edges = new ArrayList<>();
    }
    
    /**
     * Add edge: O(1)
     */
    public void addEdge(int src, int dest, int weight) {
        edges.add(new Edge(src, dest, weight));
    }
    
    /**
     * Get all edges: O(1)
     */
    public List<Edge> getEdges() {
        return edges;
    }
    
    /**
     * Get edges for vertex: O(E)
     */
    public List<Edge> getEdgesForVertex(int vertex) {
        List<Edge> result = new ArrayList<>();
        
        for (Edge edge : edges) {
            if (edge.src == vertex) {
                result.add(edge);
            }
        }
        
        return result;
    }
}
```

---

## Comparison

### Space Complexity

| Representation | Space Complexity |
|----------------|------------------|
| **Adjacency Matrix** | O(V²) |
| **Adjacency List** | O(V + E) |
| **Edge List** | O(E) |

### Time Complexity

| Operation | Matrix | List | Edge List |
|-----------|--------|------|-----------|
| **Add Vertex** | O(V²)* | O(1) | O(1) |
| **Add Edge** | O(1) | O(1) | O(1) |
| **Remove Edge** | O(1) | O(degree) | O(E) |
| **Has Edge** | O(1) | O(degree) | O(E) |
| **Get Neighbors** | O(V) | O(1) | O(E) |
| **Get All Edges** | O(V²) | O(V + E) | O(1) |

*Requires resizing matrix

### When to Use Each

**Adjacency Matrix:**
- ✅ Dense graphs (many edges)
- ✅ Need O(1) edge lookup
- ✅ Graph operations like matrix multiplication
- ❌ Sparse graphs (wasteful)

**Adjacency List:**
- ✅ Sparse graphs (most real-world graphs)
- ✅ Graph traversal (BFS, DFS)
- ✅ Most common choice
- ❌ Need fast edge existence check

**Edge List:**
- ✅ Kruskal's MST algorithm
- ✅ Simple graph representation
- ✅ Serialization/storage
- ❌ Graph traversal

---

## Graph Implementations

### Complete Graph Class

```java
/**
 * Production-grade graph with multiple operations
 */
public class Graph {
    
    private int vertices;
    private List<List<Integer>> adjList;
    private boolean directed;
    
    public Graph(int vertices, boolean directed) {
        this.vertices = vertices;
        this.directed = directed;
        this.adjList = new ArrayList<>(vertices);
        
        for (int i = 0; i < vertices; i++) {
            adjList.add(new ArrayList<>());
        }
    }
    
    public void addEdge(int src, int dest) {
        adjList.get(src).add(dest);
        
        if (!directed) {
            adjList.get(dest).add(src);
        }
    }
    
    /**
     * BFS Traversal: O(V + E)
     */
    public void bfs(int start) {
        boolean[] visited = new boolean[vertices];
        Queue<Integer> queue = new LinkedList<>();
        
        visited[start] = true;
        queue.offer(start);
        
        while (!queue.isEmpty()) {
            int vertex = queue.poll();
            System.out.print(vertex + " ");
            
            for (int neighbor : adjList.get(vertex)) {
                if (!visited[neighbor]) {
                    visited[neighbor] = true;
                    queue.offer(neighbor);
                }
            }
        }
    }
    
    /**
     * DFS Traversal: O(V + E)
     */
    public void dfs(int start) {
        boolean[] visited = new boolean[vertices];
        dfsHelper(start, visited);
    }
    
    private void dfsHelper(int vertex, boolean[] visited) {
        visited[vertex] = true;
        System.out.print(vertex + " ");
        
        for (int neighbor : adjList.get(vertex)) {
            if (!visited[neighbor]) {
                dfsHelper(neighbor, visited);
            }
        }
    }
    
    /**
     * Check if graph has cycle (undirected): O(V + E)
     */
    public boolean hasCycle() {
        boolean[] visited = new boolean[vertices];
        
        for (int i = 0; i < vertices; i++) {
            if (!visited[i]) {
                if (hasCycleUtil(i, visited, -1)) {
                    return true;
                }
            }
        }
        
        return false;
    }
    
    private boolean hasCycleUtil(int vertex, boolean[] visited, int parent) {
        visited[vertex] = true;
        
        for (int neighbor : adjList.get(vertex)) {
            if (!visited[neighbor]) {
                if (hasCycleUtil(neighbor, visited, vertex)) {
                    return true;
                }
            } else if (neighbor != parent) {
                return true;  // Back edge found
            }
        }
        
        return false;
    }
    
    /**
     * Topological Sort (DAG only): O(V + E)
     */
    public List<Integer> topologicalSort() {
        if (!directed) {
            throw new IllegalStateException("Topological sort requires directed graph");
        }
        
        Stack<Integer> stack = new Stack<>();
        boolean[] visited = new boolean[vertices];
        
        for (int i = 0; i < vertices; i++) {
            if (!visited[i]) {
                topologicalSortUtil(i, visited, stack);
            }
        }
        
        List<Integer> result = new ArrayList<>();
        while (!stack.isEmpty()) {
            result.add(stack.pop());
        }
        
        return result;
    }
    
    private void topologicalSortUtil(int vertex, boolean[] visited, Stack<Integer> stack) {
        visited[vertex] = true;
        
        for (int neighbor : adjList.get(vertex)) {
            if (!visited[neighbor]) {
                topologicalSortUtil(neighbor, visited, stack);
            }
        }
        
        stack.push(vertex);
    }
    
    /**
     * Find shortest path (unweighted): O(V + E)
     */
    public int shortestPath(int src, int dest) {
        if (src == dest) {
            return 0;
        }
        
        boolean[] visited = new boolean[vertices];
        Queue<Integer> queue = new LinkedList<>();
        Map<Integer, Integer> distance = new HashMap<>();
        
        visited[src] = true;
        queue.offer(src);
        distance.put(src, 0);
        
        while (!queue.isEmpty()) {
            int vertex = queue.poll();
            
            for (int neighbor : adjList.get(vertex)) {
                if (!visited[neighbor]) {
                    visited[neighbor] = true;
                    distance.put(neighbor, distance.get(vertex) + 1);
                    queue.offer(neighbor);
                    
                    if (neighbor == dest) {
                        return distance.get(neighbor);
                    }
                }
            }
        }
        
        return -1;  // No path
    }
    
    /**
     * Count connected components: O(V + E)
     */
    public int countConnectedComponents() {
        boolean[] visited = new boolean[vertices];
        int count = 0;
        
        for (int i = 0; i < vertices; i++) {
            if (!visited[i]) {
                dfsHelper(i, visited);
                count++;
            }
        }
        
        return count;
    }
}
```

---

## Real-World Use Cases

### 1. Social Network (HashMap-based)

```java
/**
 * Social network with user relationships
 */
class SocialNetwork {
    
    private Graph<String> friendGraph;
    
    public SocialNetwork() {
        friendGraph = new Graph<>(false);  // Undirected
    }
    
    public void addUser(String user) {
        friendGraph.addVertex(user);
    }
    
    public void addFriendship(String user1, String user2) {
        friendGraph.addEdge(user1, user2);
    }
    
    public List<String> getFriends(String user) {
        return friendGraph.getNeighbors(user);
    }
    
    /**
     * Find mutual friends
     */
    public List<String> getMutualFriends(String user1, String user2) {
        Set<String> friends1 = new HashSet<>(friendGraph.getNeighbors(user1));
        List<String> mutualFriends = new ArrayList<>();
        
        for (String friend : friendGraph.getNeighbors(user2)) {
            if (friends1.contains(friend)) {
                mutualFriends.add(friend);
            }
        }
        
        return mutualFriends;
    }
}
```

### 2. Dependency Graph (Build Systems)

```java
/**
 * Track dependencies between modules
 */
class DependencyGraph {
    
    private Graph<String> graph;
    
    public DependencyGraph() {
        graph = new Graph<>(true);  // Directed
    }
    
    public void addModule(String module) {
        graph.addVertex(module);
    }
    
    public void addDependency(String module, String dependency) {
        graph.addEdge(module, dependency);
    }
    
    public boolean hasCycle() {
        // Detect circular dependencies
        Set<String> visited = new HashSet<>();
        Set<String> recursionStack = new HashSet<>();
        
        for (String module : graph.getVertices()) {
            if (hasCycleUtil(module, visited, recursionStack)) {
                return true;
            }
        }
        
        return false;
    }
    
    private boolean hasCycleUtil(String module, Set<String> visited, 
                                 Set<String> recursionStack) {
        visited.add(module);
        recursionStack.add(module);
        
        for (String dependency : graph.getNeighbors(module)) {
            if (!visited.contains(dependency)) {
                if (hasCycleUtil(dependency, visited, recursionStack)) {
                    return true;
                }
            } else if (recursionStack.contains(dependency)) {
                return true;  // Back edge
            }
        }
        
        recursionStack.remove(module);
        return false;
    }
}
```

---

## 🎯 Interview Tips

### Graph Representation Choice

**In interviews, default to Adjacency List unless:**
- Problem states graph is dense → Matrix
- Need O(1) edge lookup → Matrix
- Implementing MST algorithm → Edge List

### Common Graph Patterns

1. **BFS**: Shortest path (unweighted), level-order
2. **DFS**: Cycle detection, topological sort, connected components
3. **Topological Sort**: Build order, course schedule
4. **Union Find**: Connected components, cycle detection
5. **Dijkstra**: Shortest path (weighted, non-negative)

### Implementation Tips

```java
// Always clarify with interviewer:
// 1. Directed or undirected?
// 2. Weighted or unweighted?
// 3. Can have self-loops?
// 4. Can have multiple edges?
// 5. 0-indexed or 1-indexed?

// Common mistake: Forgetting to check visited
while (!queue.isEmpty()) {
    int vertex = queue.poll();
    // ❌ Process even if visited
    
    if (visited[vertex]) continue;  // ✅ Check visited
    visited[vertex] = true;
}
```

---

**Next:** [Module README](./README.md) — Learning path and interview guide
