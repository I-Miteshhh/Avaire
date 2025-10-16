# Graph Algorithms - BFS & DFS

**Difficulty:** Medium to Hard  
**Learning Time:** 1.5 weeks  
**Interview Frequency:** ⭐⭐⭐⭐⭐ (Extremely High)  
**Common In:** Network problems, dependency resolution, pathfinding

---

## 📚 Table of Contents

1. [Graph Traversal Fundamentals](#graph-traversal-fundamentals)
2. [Breadth-First Search (BFS)](#breadth-first-search-bfs)
3. [Depth-First Search (DFS)](#depth-first-search-dfs)
4. [Topological Sort](#topological-sort)
5. [Cycle Detection](#cycle-detection)
6. [Connected Components](#connected-components)
7. [Bipartite Graphs](#bipartite-graphs)
8. [Real-World Applications](#real-world-applications)

---

## Graph Traversal Fundamentals

### Graph Representation Review

```java
// Adjacency List (most common)
List<List<Integer>> graph = new ArrayList<>();

// Add edge
graph.get(u).add(v);

// Adjacency Matrix
int[][] graph = new int[n][n];
graph[u][v] = 1;
```

---

## Breadth-First Search (BFS)

### Concept

Explore graph level by level using **queue**.

### Characteristics

```
✅ Shortest path in unweighted graph
✅ Level-order traversal
✅ O(V + E) time
❌ Uses O(V) space for queue
```

### Template

```java
public void bfs(List<List<Integer>> graph, int start) {
    boolean[] visited = new boolean[graph.size()];
    Queue<Integer> queue = new LinkedList<>();
    
    visited[start] = true;
    queue.offer(start);
    
    while (!queue.isEmpty()) {
        int node = queue.poll();
        System.out.println(node);  // Process node
        
        for (int neighbor : graph.get(node)) {
            if (!visited[neighbor]) {
                visited[neighbor] = true;
                queue.offer(neighbor);
            }
        }
    }
}
```

---

### Problem 1: Binary Tree Level Order Traversal

**LeetCode 102**

```java
/**
 * Return level-order traversal of binary tree
 * Time: O(n), Space: O(n)
 */
class Solution {
    public List<List<Integer>> levelOrder(TreeNode root) {
        List<List<Integer>> result = new ArrayList<>();
        if (root == null) return result;
        
        Queue<TreeNode> queue = new LinkedList<>();
        queue.offer(root);
        
        while (!queue.isEmpty()) {
            int levelSize = queue.size();
            List<Integer> currentLevel = new ArrayList<>();
            
            for (int i = 0; i < levelSize; i++) {
                TreeNode node = queue.poll();
                currentLevel.add(node.val);
                
                if (node.left != null) {
                    queue.offer(node.left);
                }
                if (node.right != null) {
                    queue.offer(node.right);
                }
            }
            
            result.add(currentLevel);
        }
        
        return result;
    }
}
```

**Key Pattern:** Track `levelSize` to process one level at a time.

---

### Problem 2: Number of Islands

**LeetCode 200**

```java
/**
 * Count islands (connected 1s) in 2D grid
 * Time: O(m * n), Space: O(min(m, n)) for queue
 */
class Solution {
    public int numIslands(char[][] grid) {
        if (grid == null || grid.length == 0) {
            return 0;
        }
        
        int m = grid.length;
        int n = grid[0].length;
        int count = 0;
        
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                if (grid[i][j] == '1') {
                    count++;
                    bfs(grid, i, j);
                }
            }
        }
        
        return count;
    }
    
    private void bfs(char[][] grid, int row, int col) {
        int m = grid.length;
        int n = grid[0].length;
        Queue<int[]> queue = new LinkedList<>();
        
        queue.offer(new int[]{row, col});
        grid[row][col] = '0';  // Mark as visited
        
        int[][] directions = {{0, 1}, {0, -1}, {1, 0}, {-1, 0}};
        
        while (!queue.isEmpty()) {
            int[] cell = queue.poll();
            int r = cell[0];
            int c = cell[1];
            
            for (int[] dir : directions) {
                int newRow = r + dir[0];
                int newCol = c + dir[1];
                
                if (newRow >= 0 && newRow < m && newCol >= 0 && newCol < n &&
                    grid[newRow][newCol] == '1') {
                    queue.offer(new int[]{newRow, newCol});
                    grid[newRow][newCol] = '0';
                }
            }
        }
    }
}
```

---

### Problem 3: Shortest Path in Binary Matrix

**LeetCode 1091**

```java
/**
 * Find shortest path from top-left to bottom-right
 * Can move in 8 directions
 * 
 * Time: O(n²), Space: O(n²)
 */
class Solution {
    public int shortestPathBinaryMatrix(int[][] grid) {
        int n = grid.length;
        
        if (grid[0][0] == 1 || grid[n-1][n-1] == 1) {
            return -1;
        }
        
        Queue<int[]> queue = new LinkedList<>();
        queue.offer(new int[]{0, 0, 1});  // row, col, distance
        grid[0][0] = 1;  // Mark as visited
        
        int[][] directions = {
            {-1, -1}, {-1, 0}, {-1, 1},
            {0, -1},           {0, 1},
            {1, -1},  {1, 0},  {1, 1}
        };
        
        while (!queue.isEmpty()) {
            int[] cell = queue.poll();
            int row = cell[0];
            int col = cell[1];
            int dist = cell[2];
            
            if (row == n - 1 && col == n - 1) {
                return dist;
            }
            
            for (int[] dir : directions) {
                int newRow = row + dir[0];
                int newCol = col + dir[1];
                
                if (newRow >= 0 && newRow < n && newCol >= 0 && newCol < n &&
                    grid[newRow][newCol] == 0) {
                    queue.offer(new int[]{newRow, newCol, dist + 1});
                    grid[newRow][newCol] = 1;  // Mark visited
                }
            }
        }
        
        return -1;
    }
}
```

**BFS guarantees shortest path** in unweighted graph.

---

### Problem 4: Word Ladder

**LeetCode 127**

```java
/**
 * Find shortest transformation sequence from beginWord to endWord
 * Each step changes one letter, intermediate words must be in wordList
 * 
 * Time: O(M² * N) where M = word length, N = wordList size
 * Space: O(M * N)
 */
class Solution {
    public int ladderLength(String beginWord, String endWord, List<String> wordList) {
        Set<String> wordSet = new HashSet<>(wordList);
        if (!wordSet.contains(endWord)) {
            return 0;
        }
        
        Queue<String> queue = new LinkedList<>();
        queue.offer(beginWord);
        
        int level = 1;
        
        while (!queue.isEmpty()) {
            int size = queue.size();
            
            for (int i = 0; i < size; i++) {
                String word = queue.poll();
                
                if (word.equals(endWord)) {
                    return level;
                }
                
                // Try changing each character
                char[] chars = word.toCharArray();
                for (int j = 0; j < chars.length; j++) {
                    char original = chars[j];
                    
                    for (char c = 'a'; c <= 'z'; c++) {
                        if (c == original) continue;
                        
                        chars[j] = c;
                        String newWord = new String(chars);
                        
                        if (wordSet.contains(newWord)) {
                            queue.offer(newWord);
                            wordSet.remove(newWord);  // Avoid revisit
                        }
                    }
                    
                    chars[j] = original;  // Restore
                }
            }
            
            level++;
        }
        
        return 0;
    }
}
```

---

## Depth-First Search (DFS)

### Concept

Explore as far as possible along each branch using **recursion or stack**.

### Characteristics

```
✅ Memory efficient (O(h) for tree, h = height)
✅ Good for exploring all paths
✅ Simple to implement with recursion
❌ Doesn't find shortest path
```

### Template (Recursive)

```java
public void dfs(List<List<Integer>> graph, int node, boolean[] visited) {
    visited[node] = true;
    System.out.println(node);  // Process node
    
    for (int neighbor : graph.get(node)) {
        if (!visited[neighbor]) {
            dfs(graph, neighbor, visited);
        }
    }
}
```

### Template (Iterative with Stack)

```java
public void dfsIterative(List<List<Integer>> graph, int start) {
    boolean[] visited = new boolean[graph.size()];
    Stack<Integer> stack = new Stack<>();
    
    stack.push(start);
    
    while (!stack.isEmpty()) {
        int node = stack.pop();
        
        if (visited[node]) continue;
        
        visited[node] = true;
        System.out.println(node);
        
        for (int neighbor : graph.get(node)) {
            if (!visited[neighbor]) {
                stack.push(neighbor);
            }
        }
    }
}
```

---

### Problem 5: Clone Graph

**LeetCode 133**

```java
/**
 * Deep copy of undirected graph
 * Time: O(V + E), Space: O(V)
 */
class Solution {
    private Map<Node, Node> visited = new HashMap<>();
    
    public Node cloneGraph(Node node) {
        if (node == null) {
            return null;
        }
        
        if (visited.containsKey(node)) {
            return visited.get(node);
        }
        
        // Clone node
        Node cloneNode = new Node(node.val);
        visited.put(node, cloneNode);
        
        // Clone neighbors
        for (Node neighbor : node.neighbors) {
            cloneNode.neighbors.add(cloneGraph(neighbor));
        }
        
        return cloneNode;
    }
}
```

---

### Problem 6: All Paths From Source to Target

**LeetCode 797**

```java
/**
 * Find all paths from node 0 to node n-1 in DAG
 * Time: O(2^V * V), Space: O(V)
 */
class Solution {
    public List<List<Integer>> allPathsSourceTarget(int[][] graph) {
        List<List<Integer>> result = new ArrayList<>();
        List<Integer> path = new ArrayList<>();
        path.add(0);
        
        dfs(graph, 0, path, result);
        return result;
    }
    
    private void dfs(int[][] graph, int node, List<Integer> path,
                    List<List<Integer>> result) {
        if (node == graph.length - 1) {
            result.add(new ArrayList<>(path));
            return;
        }
        
        for (int neighbor : graph[node]) {
            path.add(neighbor);
            dfs(graph, neighbor, path, result);
            path.remove(path.size() - 1);  // Backtrack
        }
    }
}
```

---

## Topological Sort

### Concept

Linear ordering of vertices in DAG such that for every edge u → v, u comes before v.

### Applications

- Build systems (compile order)
- Course prerequisites
- Task scheduling

### Kahn's Algorithm (BFS-based)

```java
/**
 * Topological sort using BFS
 * Time: O(V + E), Space: O(V)
 */
public List<Integer> topologicalSort(int numCourses, int[][] prerequisites) {
    List<List<Integer>> graph = new ArrayList<>();
    int[] indegree = new int[numCourses];
    
    // Build graph
    for (int i = 0; i < numCourses; i++) {
        graph.add(new ArrayList<>());
    }
    
    for (int[] edge : prerequisites) {
        int course = edge[0];
        int prereq = edge[1];
        graph.get(prereq).add(course);
        indegree[course]++;
    }
    
    // Start with nodes with indegree 0
    Queue<Integer> queue = new LinkedList<>();
    for (int i = 0; i < numCourses; i++) {
        if (indegree[i] == 0) {
            queue.offer(i);
        }
    }
    
    List<Integer> result = new ArrayList<>();
    
    while (!queue.isEmpty()) {
        int node = queue.poll();
        result.add(node);
        
        for (int neighbor : graph.get(node)) {
            indegree[neighbor]--;
            if (indegree[neighbor] == 0) {
                queue.offer(neighbor);
            }
        }
    }
    
    return result.size() == numCourses ? result : new ArrayList<>();
}
```

### Problem 7: Course Schedule

**LeetCode 207**

```java
/**
 * Determine if can finish all courses
 * Time: O(V + E), Space: O(V + E)
 */
class Solution {
    public boolean canFinish(int numCourses, int[][] prerequisites) {
        List<List<Integer>> graph = new ArrayList<>();
        int[] indegree = new int[numCourses];
        
        for (int i = 0; i < numCourses; i++) {
            graph.add(new ArrayList<>());
        }
        
        for (int[] prereq : prerequisites) {
            graph.get(prereq[1]).add(prereq[0]);
            indegree[prereq[0]]++;
        }
        
        Queue<Integer> queue = new LinkedList<>();
        for (int i = 0; i < numCourses; i++) {
            if (indegree[i] == 0) {
                queue.offer(i);
            }
        }
        
        int count = 0;
        
        while (!queue.isEmpty()) {
            int course = queue.poll();
            count++;
            
            for (int next : graph.get(course)) {
                indegree[next]--;
                if (indegree[next] == 0) {
                    queue.offer(next);
                }
            }
        }
        
        return count == numCourses;
    }
}
```

### DFS-based Topological Sort

```java
/**
 * Topological sort using DFS
 * Time: O(V + E), Space: O(V)
 */
public List<Integer> topologicalSortDFS(int n, List<List<Integer>> graph) {
    boolean[] visited = new boolean[n];
    Stack<Integer> stack = new Stack<>();
    
    for (int i = 0; i < n; i++) {
        if (!visited[i]) {
            dfsTopological(graph, i, visited, stack);
        }
    }
    
    List<Integer> result = new ArrayList<>();
    while (!stack.isEmpty()) {
        result.add(stack.pop());
    }
    
    return result;
}

private void dfsTopological(List<List<Integer>> graph, int node,
                           boolean[] visited, Stack<Integer> stack) {
    visited[node] = true;
    
    for (int neighbor : graph.get(node)) {
        if (!visited[neighbor]) {
            dfsTopological(graph, neighbor, visited, stack);
        }
    }
    
    stack.push(node);  // Add after visiting all neighbors
}
```

---

## Cycle Detection

### Undirected Graph (DFS)

```java
/**
 * Detect cycle in undirected graph
 * Time: O(V + E), Space: O(V)
 */
public boolean hasCycle(List<List<Integer>> graph) {
    boolean[] visited = new boolean[graph.size()];
    
    for (int i = 0; i < graph.size(); i++) {
        if (!visited[i]) {
            if (dfsCycle(graph, i, visited, -1)) {
                return true;
            }
        }
    }
    
    return false;
}

private boolean dfsCycle(List<List<Integer>> graph, int node,
                        boolean[] visited, int parent) {
    visited[node] = true;
    
    for (int neighbor : graph.get(node)) {
        if (!visited[neighbor]) {
            if (dfsCycle(graph, neighbor, visited, node)) {
                return true;
            }
        } else if (neighbor != parent) {
            return true;  // Back edge found
        }
    }
    
    return false;
}
```

### Directed Graph (DFS with Recursion Stack)

```java
/**
 * Detect cycle in directed graph
 * Time: O(V + E), Space: O(V)
 */
public boolean hasCycleDirected(List<List<Integer>> graph) {
    int n = graph.size();
    boolean[] visited = new boolean[n];
    boolean[] recStack = new boolean[n];
    
    for (int i = 0; i < n; i++) {
        if (dfsCycleDirected(graph, i, visited, recStack)) {
            return true;
        }
    }
    
    return false;
}

private boolean dfsCycleDirected(List<List<Integer>> graph, int node,
                                boolean[] visited, boolean[] recStack) {
    if (recStack[node]) {
        return true;  // Cycle detected
    }
    
    if (visited[node]) {
        return false;
    }
    
    visited[node] = true;
    recStack[node] = true;
    
    for (int neighbor : graph.get(node)) {
        if (dfsCycleDirected(graph, neighbor, visited, recStack)) {
            return true;
        }
    }
    
    recStack[node] = false;  // Remove from recursion stack
    return false;
}
```

---

## Connected Components

### Problem 8: Number of Connected Components

**LeetCode 323**

```java
/**
 * Count connected components in undirected graph
 * Time: O(V + E), Space: O(V)
 */
class Solution {
    public int countComponents(int n, int[][] edges) {
        List<List<Integer>> graph = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            graph.add(new ArrayList<>());
        }
        
        for (int[] edge : edges) {
            graph.get(edge[0]).add(edge[1]);
            graph.get(edge[1]).add(edge[0]);
        }
        
        boolean[] visited = new boolean[n];
        int count = 0;
        
        for (int i = 0; i < n; i++) {
            if (!visited[i]) {
                dfs(graph, i, visited);
                count++;
            }
        }
        
        return count;
    }
    
    private void dfs(List<List<Integer>> graph, int node, boolean[] visited) {
        visited[node] = true;
        
        for (int neighbor : graph.get(node)) {
            if (!visited[neighbor]) {
                dfs(graph, neighbor, visited);
            }
        }
    }
}
```

---

## Bipartite Graphs

### Problem 9: Is Graph Bipartite?

**LeetCode 785**

```java
/**
 * Check if graph can be colored with 2 colors
 * Time: O(V + E), Space: O(V)
 */
class Solution {
    public boolean isBipartite(int[][] graph) {
        int n = graph.length;
        int[] colors = new int[n];
        Arrays.fill(colors, -1);
        
        for (int i = 0; i < n; i++) {
            if (colors[i] == -1) {
                if (!bfsColor(graph, i, colors)) {
                    return false;
                }
            }
        }
        
        return true;
    }
    
    private boolean bfsColor(int[][] graph, int start, int[] colors) {
        Queue<Integer> queue = new LinkedList<>();
        queue.offer(start);
        colors[start] = 0;
        
        while (!queue.isEmpty()) {
            int node = queue.poll();
            
            for (int neighbor : graph[node]) {
                if (colors[neighbor] == -1) {
                    colors[neighbor] = 1 - colors[node];
                    queue.offer(neighbor);
                } else if (colors[neighbor] == colors[node]) {
                    return false;  // Same color as neighbor
                }
            }
        }
        
        return true;
    }
}
```

---

## Real-World Data Engineering Applications

### 1. Apache Airflow DAG Validation

```java
/**
 * Validate Airflow DAG (no cycles)
 */
class DAGValidator {
    
    static class Task {
        String name;
        List<String> dependencies;
        
        Task(String name, List<String> dependencies) {
            this.name = name;
            this.dependencies = dependencies;
        }
    }
    
    public boolean isValidDAG(List<Task> tasks) {
        Map<String, List<String>> graph = new HashMap<>();
        Map<String, Integer> indegree = new HashMap<>();
        
        // Build graph
        for (Task task : tasks) {
            graph.putIfAbsent(task.name, new ArrayList<>());
            indegree.putIfAbsent(task.name, 0);
            
            for (String dep : task.dependencies) {
                graph.putIfAbsent(dep, new ArrayList<>());
                graph.get(dep).add(task.name);
                indegree.put(task.name, indegree.getOrDefault(task.name, 0) + 1);
            }
        }
        
        // Topological sort
        Queue<String> queue = new LinkedList<>();
        for (String task : indegree.keySet()) {
            if (indegree.get(task) == 0) {
                queue.offer(task);
            }
        }
        
        int processed = 0;
        
        while (!queue.isEmpty()) {
            String task = queue.poll();
            processed++;
            
            for (String next : graph.get(task)) {
                indegree.put(next, indegree.get(next) - 1);
                if (indegree.get(next) == 0) {
                    queue.offer(next);
                }
            }
        }
        
        return processed == graph.size();  // All tasks processed = no cycle
    }
}
```

### 2. Social Network Friend Suggestions

```java
/**
 * Suggest friends (friends of friends)
 */
class FriendSuggestion {
    
    public List<String> suggestFriends(Map<String, List<String>> friendGraph, 
                                       String user) {
        Set<String> directFriends = new HashSet<>(friendGraph.get(user));
        Map<String, Integer> friendOfFriendCount = new HashMap<>();
        
        // BFS to find friends of friends
        for (String friend : directFriends) {
            for (String friendOfFriend : friendGraph.get(friend)) {
                if (!friendOfFriend.equals(user) && !directFriends.contains(friendOfFriend)) {
                    friendOfFriendCount.put(friendOfFriend, 
                        friendOfFriendCount.getOrDefault(friendOfFriend, 0) + 1);
                }
            }
        }
        
        // Sort by mutual friend count
        return friendOfFriendCount.entrySet().stream()
            .sorted((a, b) -> b.getValue().compareTo(a.getValue()))
            .map(Map.Entry::getKey)
            .collect(Collectors.toList());
    }
}
```

---

## 🎯 Interview Tips

### BFS vs DFS

| Use BFS When | Use DFS When |
|--------------|--------------|
| Shortest path needed | Memory constrained |
| Level-order traversal | All paths needed |
| Nearest neighbor | Backtracking problems |

### Common Mistakes

1. **Forgetting to mark visited before adding to queue**
   ```java
   // ❌ Wrong
   queue.offer(neighbor);
   visited[neighbor] = true;  // May add duplicate
   
   // ✅ Correct
   visited[neighbor] = true;
   queue.offer(neighbor);
   ```

2. **Cycle detection in directed vs undirected**
   - Undirected: Track parent
   - Directed: Track recursion stack

3. **Not handling disconnected graphs**
   ```java
   // ❌ Wrong - only explores one component
   bfs(graph, 0);
   
   // ✅ Correct - explores all components
   for (int i = 0; i < n; i++) {
       if (!visited[i]) {
           bfs(graph, i);
       }
   }
   ```

---

**Next:** [Shortest Path Algorithms](./09-Shortest-Path-Algorithms.md)
