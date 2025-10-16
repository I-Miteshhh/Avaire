# Recursion & Backtracking

**Difficulty:** Medium to Hard  
**Learning Time:** 2 weeks  
**Interview Frequency:** ⭐⭐⭐⭐⭐ (Extremely High)  
**Common In:** Combinatorial problems, tree/graph traversal, constraint satisfaction

---

## 📚 Table of Contents

1. [Recursion Fundamentals](#recursion-fundamentals)
2. [Backtracking Pattern](#backtracking-pattern)
3. [Subset Problems](#subset-problems)
4. [Permutation Problems](#permutation-problems)
5. [Combination Problems](#combination-problems)
6. [Constraint Satisfaction](#constraint-satisfaction)
7. [Real-World Applications](#real-world-applications)

---

## Recursion Fundamentals

### Definition

Function that calls itself with smaller/simpler input until base case reached.

### Components

1. **Base Case:** Stopping condition (prevents infinite recursion)
2. **Recursive Case:** Function calls itself with modified input
3. **Return Value:** Combine results from recursive calls

### Template

```java
public ReturnType recursiveFunction(Input input) {
    // Base case
    if (baseCondition(input)) {
        return baseResult;
    }
    
    // Recursive case
    Input smallerInput = reduce(input);
    ReturnType subResult = recursiveFunction(smallerInput);
    
    // Combine results
    return combine(subResult);
}
```

---

## Classic Recursion Examples

### 1. Factorial

```java
/**
 * Calculate n! = n * (n-1) * ... * 1
 * Time: O(n), Space: O(n) call stack
 */
public int factorial(int n) {
    // Base case
    if (n <= 1) {
        return 1;
    }
    
    // Recursive case
    return n * factorial(n - 1);
}
```

**Tail-Recursive (Optimizable):**

```java
public int factorialTail(int n, int accumulator) {
    if (n <= 1) {
        return accumulator;
    }
    return factorialTail(n - 1, n * accumulator);
}

public int factorial(int n) {
    return factorialTail(n, 1);
}
```

---

### 2. Fibonacci

```java
/**
 * Naive recursion - AVOID (exponential time)
 * Time: O(2^n), Space: O(n)
 */
public int fibonacciNaive(int n) {
    if (n <= 1) return n;
    return fibonacciNaive(n - 1) + fibonacciNaive(n - 2);
}

/**
 * With memoization - PREFERRED
 * Time: O(n), Space: O(n)
 */
public int fibonacci(int n) {
    return fibonacciMemo(n, new HashMap<>());
}

private int fibonacciMemo(int n, Map<Integer, Integer> memo) {
    if (n <= 1) return n;
    
    if (memo.containsKey(n)) {
        return memo.get(n);
    }
    
    int result = fibonacciMemo(n - 1, memo) + fibonacciMemo(n - 2, memo);
    memo.put(n, result);
    return result;
}

/**
 * Iterative - MOST EFFICIENT
 * Time: O(n), Space: O(1)
 */
public int fibonacciIterative(int n) {
    if (n <= 1) return n;
    
    int prev2 = 0, prev1 = 1;
    for (int i = 2; i <= n; i++) {
        int curr = prev1 + prev2;
        prev2 = prev1;
        prev1 = curr;
    }
    return prev1;
}
```

---

## Backtracking Pattern

### Concept

Explore all possible solutions by:
1. Make a choice
2. Recurse
3. Undo the choice (backtrack)

### Template

```java
public void backtrack(State state, List<Solution> results) {
    // Base case: found valid solution
    if (isComplete(state)) {
        results.add(new Solution(state));
        return;
    }
    
    // Try all possible choices
    for (Choice choice : getChoices(state)) {
        // Make choice
        makeChoice(state, choice);
        
        // Recurse
        backtrack(state, results);
        
        // Undo choice (backtrack)
        undoChoice(state, choice);
    }
}
```

### Visualization

```
                    []
                   /  \
                 [1]  [2]
                /  \
             [1,2][1,3]
```

At each node:
- Make choice (add element)
- Recurse to children
- Backtrack (remove element)

---

## Subset Problems

### Problem 1: Subsets (All Subsets)

**LeetCode 78**

```java
/**
 * Generate all subsets of array (power set)
 * Time: O(2^n), Space: O(n) recursion depth
 */
class Solution {
    public List<List<Integer>> subsets(int[] nums) {
        List<List<Integer>> result = new ArrayList<>();
        backtrack(nums, 0, new ArrayList<>(), result);
        return result;
    }
    
    private void backtrack(int[] nums, int start, 
                          List<Integer> current, List<List<Integer>> result) {
        // Add current subset to result
        result.add(new ArrayList<>(current));
        
        // Try adding each remaining element
        for (int i = start; i < nums.length; i++) {
            // Make choice
            current.add(nums[i]);
            
            // Recurse
            backtrack(nums, i + 1, current, result);
            
            // Backtrack
            current.remove(current.size() - 1);
        }
    }
}
```

**Alternative: Iterative (Cascading)**

```java
public List<List<Integer>> subsetsIterative(int[] nums) {
    List<List<Integer>> result = new ArrayList<>();
    result.add(new ArrayList<>());  // Empty set
    
    for (int num : nums) {
        int size = result.size();
        for (int i = 0; i < size; i++) {
            List<Integer> newSubset = new ArrayList<>(result.get(i));
            newSubset.add(num);
            result.add(newSubset);
        }
    }
    
    return result;
}
```

---

### Problem 2: Subsets II (With Duplicates)

**LeetCode 90**

```java
/**
 * Generate subsets when array contains duplicates
 * Time: O(2^n), Space: O(n)
 */
class Solution {
    public List<List<Integer>> subsetsWithDup(int[] nums) {
        Arrays.sort(nums);  // Sort to group duplicates
        List<List<Integer>> result = new ArrayList<>();
        backtrack(nums, 0, new ArrayList<>(), result);
        return result;
    }
    
    private void backtrack(int[] nums, int start,
                          List<Integer> current, List<List<Integer>> result) {
        result.add(new ArrayList<>(current));
        
        for (int i = start; i < nums.length; i++) {
            // Skip duplicates at same level
            if (i > start && nums[i] == nums[i - 1]) {
                continue;
            }
            
            current.add(nums[i]);
            backtrack(nums, i + 1, current, result);
            current.remove(current.size() - 1);
        }
    }
}
```

**Key Difference:**
- Skip duplicates at same recursion level
- `i > start` ensures we don't skip first occurrence

---

## Permutation Problems

### Problem 3: Permutations

**LeetCode 46**

```java
/**
 * Generate all permutations of distinct integers
 * Time: O(n! * n), Space: O(n)
 */
class Solution {
    public List<List<Integer>> permute(int[] nums) {
        List<List<Integer>> result = new ArrayList<>();
        backtrack(nums, new ArrayList<>(), new boolean[nums.length], result);
        return result;
    }
    
    private void backtrack(int[] nums, List<Integer> current,
                          boolean[] used, List<List<Integer>> result) {
        // Base case: permutation complete
        if (current.size() == nums.length) {
            result.add(new ArrayList<>(current));
            return;
        }
        
        // Try each number
        for (int i = 0; i < nums.length; i++) {
            if (used[i]) continue;  // Skip if already used
            
            // Make choice
            current.add(nums[i]);
            used[i] = true;
            
            // Recurse
            backtrack(nums, current, used, result);
            
            // Backtrack
            current.remove(current.size() - 1);
            used[i] = false;
        }
    }
}
```

**Alternative: Swap-based (No extra space)**

```java
public List<List<Integer>> permuteSwap(int[] nums) {
    List<List<Integer>> result = new ArrayList<>();
    backtrackSwap(nums, 0, result);
    return result;
}

private void backtrackSwap(int[] nums, int start, List<List<Integer>> result) {
    if (start == nums.length) {
        result.add(Arrays.stream(nums).boxed().collect(Collectors.toList()));
        return;
    }
    
    for (int i = start; i < nums.length; i++) {
        // Swap
        swap(nums, start, i);
        
        // Recurse
        backtrackSwap(nums, start + 1, result);
        
        // Swap back
        swap(nums, start, i);
    }
}

private void swap(int[] nums, int i, int j) {
    int temp = nums[i];
    nums[i] = nums[j];
    nums[j] = temp;
}
```

---

### Problem 4: Permutations II (With Duplicates)

**LeetCode 47**

```java
/**
 * Generate unique permutations with duplicates
 * Time: O(n! * n), Space: O(n)
 */
class Solution {
    public List<List<Integer>> permuteUnique(int[] nums) {
        Arrays.sort(nums);
        List<List<Integer>> result = new ArrayList<>();
        backtrack(nums, new ArrayList<>(), new boolean[nums.length], result);
        return result;
    }
    
    private void backtrack(int[] nums, List<Integer> current,
                          boolean[] used, List<List<Integer>> result) {
        if (current.size() == nums.length) {
            result.add(new ArrayList<>(current));
            return;
        }
        
        for (int i = 0; i < nums.length; i++) {
            if (used[i]) continue;
            
            // Skip duplicates: if previous same element not used, skip current
            if (i > 0 && nums[i] == nums[i - 1] && !used[i - 1]) {
                continue;
            }
            
            current.add(nums[i]);
            used[i] = true;
            
            backtrack(nums, current, used, result);
            
            current.remove(current.size() - 1);
            used[i] = false;
        }
    }
}
```

---

## Combination Problems

### Problem 5: Combinations

**LeetCode 77**

```java
/**
 * Generate all combinations of k numbers from 1 to n
 * Time: O(C(n,k) * k), Space: O(k)
 */
class Solution {
    public List<List<Integer>> combine(int n, int k) {
        List<List<Integer>> result = new ArrayList<>();
        backtrack(n, k, 1, new ArrayList<>(), result);
        return result;
    }
    
    private void backtrack(int n, int k, int start,
                          List<Integer> current, List<List<Integer>> result) {
        // Base case: combination complete
        if (current.size() == k) {
            result.add(new ArrayList<>(current));
            return;
        }
        
        // Optimization: prune if not enough elements left
        int need = k - current.size();
        int available = n - start + 1;
        if (available < need) {
            return;
        }
        
        for (int i = start; i <= n; i++) {
            current.add(i);
            backtrack(n, k, i + 1, current, result);
            current.remove(current.size() - 1);
        }
    }
}
```

---

### Problem 6: Combination Sum

**LeetCode 39**

```java
/**
 * Find all combinations that sum to target
 * Can reuse same element unlimited times
 * 
 * Time: O(n^(target/min)), Space: O(target/min)
 */
class Solution {
    public List<List<Integer>> combinationSum(int[] candidates, int target) {
        List<List<Integer>> result = new ArrayList<>();
        Arrays.sort(candidates);  // Optimization for pruning
        backtrack(candidates, target, 0, new ArrayList<>(), result);
        return result;
    }
    
    private void backtrack(int[] candidates, int remain, int start,
                          List<Integer> current, List<List<Integer>> result) {
        if (remain == 0) {
            result.add(new ArrayList<>(current));
            return;
        }
        
        if (remain < 0) {
            return;  // Exceeded target
        }
        
        for (int i = start; i < candidates.length; i++) {
            // Pruning: if current > remain, all next will also exceed
            if (candidates[i] > remain) {
                break;
            }
            
            current.add(candidates[i]);
            backtrack(candidates, remain - candidates[i], i, current, result);  // i, not i+1 (can reuse)
            current.remove(current.size() - 1);
        }
    }
}
```

---

### Problem 7: Combination Sum II

**LeetCode 40**

```java
/**
 * Each number can be used only once
 * Array may contain duplicates
 * 
 * Time: O(2^n), Space: O(n)
 */
class Solution {
    public List<List<Integer>> combinationSum2(int[] candidates, int target) {
        Arrays.sort(candidates);
        List<List<Integer>> result = new ArrayList<>();
        backtrack(candidates, target, 0, new ArrayList<>(), result);
        return result;
    }
    
    private void backtrack(int[] candidates, int remain, int start,
                          List<Integer> current, List<List<Integer>> result) {
        if (remain == 0) {
            result.add(new ArrayList<>(current));
            return;
        }
        
        for (int i = start; i < candidates.length; i++) {
            if (candidates[i] > remain) break;
            
            // Skip duplicates at same level
            if (i > start && candidates[i] == candidates[i - 1]) {
                continue;
            }
            
            current.add(candidates[i]);
            backtrack(candidates, remain - candidates[i], i + 1, current, result);  // i+1 (can't reuse)
            current.remove(current.size() - 1);
        }
    }
}
```

---

## Constraint Satisfaction Problems

### Problem 8: N-Queens

**LeetCode 51**

```java
/**
 * Place N queens on N×N chessboard
 * No two queens attack each other
 * 
 * Time: O(N!), Space: O(N²)
 */
class Solution {
    public List<List<String>> solveNQueens(int n) {
        List<List<String>> result = new ArrayList<>();
        char[][] board = new char[n][n];
        
        // Initialize board
        for (int i = 0; i < n; i++) {
            Arrays.fill(board[i], '.');
        }
        
        backtrack(board, 0, result);
        return result;
    }
    
    private void backtrack(char[][] board, int row, List<List<String>> result) {
        if (row == board.length) {
            result.add(construct(board));
            return;
        }
        
        for (int col = 0; col < board.length; col++) {
            if (!isValid(board, row, col)) {
                continue;
            }
            
            // Place queen
            board[row][col] = 'Q';
            
            // Recurse to next row
            backtrack(board, row + 1, result);
            
            // Remove queen
            board[row][col] = '.';
        }
    }
    
    private boolean isValid(char[][] board, int row, int col) {
        int n = board.length;
        
        // Check column
        for (int i = 0; i < row; i++) {
            if (board[i][col] == 'Q') {
                return false;
            }
        }
        
        // Check diagonal (top-left)
        for (int i = row - 1, j = col - 1; i >= 0 && j >= 0; i--, j--) {
            if (board[i][j] == 'Q') {
                return false;
            }
        }
        
        // Check diagonal (top-right)
        for (int i = row - 1, j = col + 1; i >= 0 && j < n; i--, j++) {
            if (board[i][j] == 'Q') {
                return false;
            }
        }
        
        return true;
    }
    
    private List<String> construct(char[][] board) {
        List<String> result = new ArrayList<>();
        for (char[] row : board) {
            result.add(new String(row));
        }
        return result;
    }
}

/**
 * Optimized with sets (faster validity check)
 */
class SolutionOptimized {
    public List<List<String>> solveNQueens(int n) {
        List<List<String>> result = new ArrayList<>();
        backtrack(n, 0, new HashSet<>(), new HashSet<>(), new HashSet<>(), 
                 new ArrayList<>(), result);
        return result;
    }
    
    private void backtrack(int n, int row, Set<Integer> cols,
                          Set<Integer> diag1, Set<Integer> diag2,
                          List<String> board, List<List<String>> result) {
        if (row == n) {
            result.add(new ArrayList<>(board));
            return;
        }
        
        for (int col = 0; col < n; col++) {
            int d1 = row - col;
            int d2 = row + col;
            
            if (cols.contains(col) || diag1.contains(d1) || diag2.contains(d2)) {
                continue;
            }
            
            // Place queen
            cols.add(col);
            diag1.add(d1);
            diag2.add(d2);
            
            char[] rowChars = new char[n];
            Arrays.fill(rowChars, '.');
            rowChars[col] = 'Q';
            board.add(new String(rowChars));
            
            // Recurse
            backtrack(n, row + 1, cols, diag1, diag2, board, result);
            
            // Backtrack
            board.remove(board.size() - 1);
            cols.remove(col);
            diag1.remove(d1);
            diag2.remove(d2);
        }
    }
}
```

---

### Problem 9: Sudoku Solver

**LeetCode 37**

```java
/**
 * Solve 9×9 Sudoku
 * Time: O(9^(n²)) worst case, Space: O(n²)
 */
class Solution {
    public void solveSudoku(char[][] board) {
        backtrack(board);
    }
    
    private boolean backtrack(char[][] board) {
        for (int row = 0; row < 9; row++) {
            for (int col = 0; col < 9; col++) {
                if (board[row][col] != '.') {
                    continue;
                }
                
                // Try each digit 1-9
                for (char digit = '1'; digit <= '9'; digit++) {
                    if (!isValid(board, row, col, digit)) {
                        continue;
                    }
                    
                    // Place digit
                    board[row][col] = digit;
                    
                    // Recurse
                    if (backtrack(board)) {
                        return true;  // Solution found
                    }
                    
                    // Backtrack
                    board[row][col] = '.';
                }
                
                return false;  // No valid digit found
            }
        }
        
        return true;  // All cells filled
    }
    
    private boolean isValid(char[][] board, int row, int col, char digit) {
        // Check row
        for (int j = 0; j < 9; j++) {
            if (board[row][j] == digit) {
                return false;
            }
        }
        
        // Check column
        for (int i = 0; i < 9; i++) {
            if (board[i][col] == digit) {
                return false;
            }
        }
        
        // Check 3×3 box
        int boxRow = (row / 3) * 3;
        int boxCol = (col / 3) * 3;
        for (int i = boxRow; i < boxRow + 3; i++) {
            for (int j = boxCol; j < boxCol + 3; j++) {
                if (board[i][j] == digit) {
                    return false;
                }
            }
        }
        
        return true;
    }
}
```

---

### Problem 10: Word Search

**LeetCode 79**

```java
/**
 * Find if word exists in 2D grid
 * Time: O(m*n*4^L) where L = word length, Space: O(L)
 */
class Solution {
    public boolean exist(char[][] board, String word) {
        int m = board.length;
        int n = board[0].length;
        
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                if (backtrack(board, word, i, j, 0)) {
                    return true;
                }
            }
        }
        
        return false;
    }
    
    private boolean backtrack(char[][] board, String word, int row, int col, int index) {
        // Base case: found word
        if (index == word.length()) {
            return true;
        }
        
        // Boundary check
        if (row < 0 || row >= board.length || col < 0 || col >= board[0].length) {
            return false;
        }
        
        // Character mismatch or already visited
        if (board[row][col] != word.charAt(index)) {
            return false;
        }
        
        // Mark as visited
        char temp = board[row][col];
        board[row][col] = '#';
        
        // Explore 4 directions
        boolean found = backtrack(board, word, row + 1, col, index + 1) ||
                       backtrack(board, word, row - 1, col, index + 1) ||
                       backtrack(board, word, row, col + 1, index + 1) ||
                       backtrack(board, word, row, col - 1, index + 1);
        
        // Restore cell
        board[row][col] = temp;
        
        return found;
    }
}
```

---

## Real-World Data Engineering Applications

### 1. ETL Pipeline Configuration Generator

```java
/**
 * Generate all valid ETL pipeline configurations
 */
class PipelineConfigurator {
    
    static class Stage {
        String name;
        List<String> dependencies;
        
        Stage(String name, List<String> dependencies) {
            this.name = name;
            this.dependencies = dependencies;
        }
    }
    
    /**
     * Generate all valid execution orders
     */
    public List<List<String>> generateExecutionPlans(List<Stage> stages) {
        List<List<String>> result = new ArrayList<>();
        backtrack(stages, new ArrayList<>(), new HashSet<>(), result);
        return result;
    }
    
    private void backtrack(List<Stage> stages, List<String> current,
                          Set<String> completed, List<List<String>> result) {
        if (current.size() == stages.size()) {
            result.add(new ArrayList<>(current));
            return;
        }
        
        for (Stage stage : stages) {
            if (completed.contains(stage.name)) {
                continue;
            }
            
            // Check if dependencies met
            if (!completed.containsAll(stage.dependencies)) {
                continue;
            }
            
            // Execute stage
            current.add(stage.name);
            completed.add(stage.name);
            
            backtrack(stages, current, completed, result);
            
            // Backtrack
            current.remove(current.size() - 1);
            completed.remove(stage.name);
        }
    }
}
```

---

## 🎯 Interview Tips

### When to Use Backtracking

**Clear signals:**
- "Find all combinations/permutations/subsets"
- "Generate all valid configurations"
- "Place N items with constraints"
- Constraint satisfaction problems

### Optimization Techniques

1. **Pruning:** Skip invalid branches early
   ```java
   if (currentSum > target) {
       return;  // Prune
   }
   ```

2. **Sorting:** Enable early termination
   ```java
   Arrays.sort(candidates);
   if (candidates[i] > remain) {
       break;  // All next will exceed
   }
   ```

3. **Memoization:** Cache repeated subproblems
   ```java
   String key = state.toString();
   if (memo.containsKey(key)) {
       return memo.get(key);
   }
   ```

### Common Mistakes

1. **Forgetting to backtrack:**
   ```java
   // ❌ Wrong
   current.add(num);
   backtrack(current);
   // Forgot to remove
   
   // ✅ Correct
   current.add(num);
   backtrack(current);
   current.remove(current.size() - 1);
   ```

2. **Not copying result:**
   ```java
   // ❌ Wrong
   result.add(current);  // Reference added
   
   // ✅ Correct
   result.add(new ArrayList<>(current));  // Copy
   ```

3. **Wrong duplicate handling:**
   ```java
   // ❌ Wrong
   if (i > 0 && nums[i] == nums[i-1]) continue;
   
   // ✅ Correct (same level only)
   if (i > start && nums[i] == nums[i-1]) continue;
   ```

---

## 📊 Complexity Summary

| Problem | Time | Space |
|---------|------|-------|
| Subsets | O(2^n) | O(n) |
| Permutations | O(n!) | O(n) |
| Combinations | O(C(n,k)) | O(k) |
| Combination Sum | O(n^(T/M)) | O(T/M) |
| N-Queens | O(N!) | O(N²) |
| Sudoku | O(9^(n²)) | O(n²) |
| Word Search | O(m*n*4^L) | O(L) |

*T = target, M = min element*

---

**Next:** [Graph Algorithms](./08-Graph-Algorithms-BFS-DFS.md)
