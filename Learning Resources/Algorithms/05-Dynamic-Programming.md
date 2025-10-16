# Dynamic Programming

**Difficulty:** Advanced  
**Learning Time:** 2-3 weeks  
**Interview Frequency:** ⭐⭐⭐⭐⭐ (Extremely High for 40 LPA)

---

## 📚 Core Concepts

### DP Prerequisites

1. **Optimal Substructure:** Solution can be constructed from subproblems
2. **Overlapping Subproblems:** Same subproblems solved multiple times

### Approaches

```
1. Top-Down (Memoization):
   - Recursive with caching
   - DFS + HashMap/Array

2. Bottom-Up (Tabulation):
   - Iterative with DP table
   - Fill table systematically
```

---

## Classic DP Problems

### Fibonacci (Learning DP)

```java
class Fibonacci {
    
    /**
     * Top-Down with Memoization
     * Time: O(n), Space: O(n)
     */
    public int fibMemo(int n) {
        int[] memo = new int[n + 1];
        Arrays.fill(memo, -1);
        return fibMemoHelper(n, memo);
    }
    
    private int fibMemoHelper(int n, int[] memo) {
        if (n <= 1) {
            return n;
        }
        
        if (memo[n] != -1) {
            return memo[n];
        }
        
        memo[n] = fibMemoHelper(n - 1, memo) + fibMemoHelper(n - 2, memo);
        return memo[n];
    }
    
    /**
     * Bottom-Up Tabulation
     * Time: O(n), Space: O(n)
     */
    public int fibDP(int n) {
        if (n <= 1) {
            return n;
        }
        
        int[] dp = new int[n + 1];
        dp[0] = 0;
        dp[1] = 1;
        
        for (int i = 2; i <= n; i++) {
            dp[i] = dp[i - 1] + dp[i - 2];
        }
        
        return dp[n];
    }
    
    /**
     * Space Optimized
     * Time: O(n), Space: O(1)
     */
    public int fibOptimized(int n) {
        if (n <= 1) {
            return n;
        }
        
        int prev2 = 0, prev1 = 1;
        
        for (int i = 2; i <= n; i++) {
            int curr = prev1 + prev2;
            prev2 = prev1;
            prev1 = curr;
        }
        
        return prev1;
    }
}
```

### Climbing Stairs

```java
/**
 * LeetCode 70
 * You can climb 1 or 2 steps. How many ways to reach top?
 */
class Solution {
    public int climbStairs(int n) {
        if (n <= 2) {
            return n;
        }
        
        int prev2 = 1, prev1 = 2;
        
        for (int i = 3; i <= n; i++) {
            int curr = prev1 + prev2;
            prev2 = prev1;
            prev1 = curr;
        }
        
        return prev1;
    }
}
```

### House Robber

```java
/**
 * LeetCode 198
 * Cannot rob adjacent houses
 * Time: O(n), Space: O(1)
 */
class Solution {
    public int rob(int[] nums) {
        if (nums.length == 0) {
            return 0;
        }
        if (nums.length == 1) {
            return nums[0];
        }
        
        int prev2 = 0, prev1 = 0;
        
        for (int num : nums) {
            int curr = Math.max(prev1, prev2 + num);
            prev2 = prev1;
            prev1 = curr;
        }
        
        return prev1;
    }
}
```

### Longest Increasing Subsequence

```java
/**
 * LeetCode 300
 * Find length of longest increasing subsequence
 */
class Solution {
    
    /**
     * DP Solution
     * Time: O(n²), Space: O(n)
     */
    public int lengthOfLIS(int[] nums) {
        int n = nums.length;
        int[] dp = new int[n];
        Arrays.fill(dp, 1);
        
        int maxLen = 1;
        
        for (int i = 1; i < n; i++) {
            for (int j = 0; j < i; j++) {
                if (nums[i] > nums[j]) {
                    dp[i] = Math.max(dp[i], dp[j] + 1);
                }
            }
            maxLen = Math.max(maxLen, dp[i]);
        }
        
        return maxLen;
    }
    
    /**
     * Binary Search + DP (Patience Sorting)
     * Time: O(n log n), Space: O(n)
     */
    public int lengthOfLISOptimized(int[] nums) {
        List<Integer> tails = new ArrayList<>();
        
        for (int num : nums) {
            int pos = binarySearch(tails, num);
            
            if (pos == tails.size()) {
                tails.add(num);
            } else {
                tails.set(pos, num);
            }
        }
        
        return tails.size();
    }
    
    private int binarySearch(List<Integer> tails, int target) {
        int left = 0, right = tails.size();
        
        while (left < right) {
            int mid = left + (right - left) / 2;
            
            if (tails.get(mid) < target) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }
        
        return left;
    }
}
```

### Coin Change

```java
/**
 * LeetCode 322
 * Minimum coins to make amount
 * Time: O(n * amount), Space: O(amount)
 */
class Solution {
    public int coinChange(int[] coins, int amount) {
        int[] dp = new int[amount + 1];
        Arrays.fill(dp, amount + 1);
        dp[0] = 0;
        
        for (int i = 1; i <= amount; i++) {
            for (int coin : coins) {
                if (i >= coin) {
                    dp[i] = Math.min(dp[i], dp[i - coin] + 1);
                }
            }
        }
        
        return dp[amount] > amount ? -1 : dp[amount];
    }
}
```

### 0/1 Knapsack

```java
/**
 * Classic 0/1 Knapsack
 * Time: O(n * capacity), Space: O(n * capacity)
 */
class Knapsack {
    
    public int knapsack(int[] weights, int[] values, int capacity) {
        int n = weights.length;
        int[][] dp = new int[n + 1][capacity + 1];
        
        for (int i = 1; i <= n; i++) {
            for (int w = 1; w <= capacity; w++) {
                if (weights[i - 1] <= w) {
                    dp[i][w] = Math.max(
                        dp[i - 1][w],  // Don't take item
                        dp[i - 1][w - weights[i - 1]] + values[i - 1]  // Take item
                    );
                } else {
                    dp[i][w] = dp[i - 1][w];
                }
            }
        }
        
        return dp[n][capacity];
    }
    
    /**
     * Space Optimized: O(capacity)
     */
    public int knapsackOptimized(int[] weights, int[] values, int capacity) {
        int[] dp = new int[capacity + 1];
        
        for (int i = 0; i < weights.length; i++) {
            // Traverse backwards to avoid using same item multiple times
            for (int w = capacity; w >= weights[i]; w--) {
                dp[w] = Math.max(dp[w], dp[w - weights[i]] + values[i]);
            }
        }
        
        return dp[capacity];
    }
}
```

### Longest Common Subsequence

```java
/**
 * LeetCode 1143
 * Time: O(m * n), Space: O(m * n)
 */
class Solution {
    public int longestCommonSubsequence(String text1, String text2) {
        int m = text1.length();
        int n = text2.length();
        int[][] dp = new int[m + 1][n + 1];
        
        for (int i = 1; i <= m; i++) {
            for (int j = 1; j <= n; j++) {
                if (text1.charAt(i - 1) == text2.charAt(j - 1)) {
                    dp[i][j] = dp[i - 1][j - 1] + 1;
                } else {
                    dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
                }
            }
        }
        
        return dp[m][n];
    }
}
```

### Edit Distance

```java
/**
 * LeetCode 72
 * Minimum operations to convert word1 to word2
 * Operations: insert, delete, replace
 * Time: O(m * n), Space: O(m * n)
 */
class Solution {
    public int minDistance(String word1, String word2) {
        int m = word1.length();
        int n = word2.length();
        int[][] dp = new int[m + 1][n + 1];
        
        // Base cases
        for (int i = 0; i <= m; i++) {
            dp[i][0] = i;  // Delete all characters
        }
        
        for (int j = 0; j <= n; j++) {
            dp[0][j] = j;  // Insert all characters
        }
        
        for (int i = 1; i <= m; i++) {
            for (int j = 1; j <= n; j++) {
                if (word1.charAt(i - 1) == word2.charAt(j - 1)) {
                    dp[i][j] = dp[i - 1][j - 1];
                } else {
                    dp[i][j] = 1 + Math.min(
                        dp[i - 1][j],      // Delete
                        Math.min(
                            dp[i][j - 1],  // Insert
                            dp[i - 1][j - 1]  // Replace
                        )
                    );
                }
            }
        }
        
        return dp[m][n];
    }
}
```

### Maximum Subarray (Kadane's Algorithm)

```java
/**
 * LeetCode 53
 * Find contiguous subarray with largest sum
 * Time: O(n), Space: O(1)
 */
class Solution {
    public int maxSubArray(int[] nums) {
        int maxEndingHere = nums[0];
        int maxSoFar = nums[0];
        
        for (int i = 1; i < nums.length; i++) {
            maxEndingHere = Math.max(nums[i], maxEndingHere + nums[i]);
            maxSoFar = Math.max(maxSoFar, maxEndingHere);
        }
        
        return maxSoFar;
    }
}
```

### Partition Equal Subset Sum

```java
/**
 * LeetCode 416
 * Can partition into two subsets with equal sum?
 * Time: O(n * sum), Space: O(sum)
 */
class Solution {
    public boolean canPartition(int[] nums) {
        int sum = Arrays.stream(nums).sum();
        
        if (sum % 2 != 0) {
            return false;
        }
        
        int target = sum / 2;
        boolean[] dp = new boolean[target + 1];
        dp[0] = true;
        
        for (int num : nums) {
            for (int j = target; j >= num; j--) {
                dp[j] = dp[j] || dp[j - num];
            }
        }
        
        return dp[target];
    }
}
```

### Word Break

```java
/**
 * LeetCode 139
 * Can segment string using dictionary words?
 * Time: O(n² * m), Space: O(n)
 */
class Solution {
    public boolean wordBreak(String s, List<String> wordDict) {
        Set<String> wordSet = new HashSet<>(wordDict);
        boolean[] dp = new boolean[s.length() + 1];
        dp[0] = true;
        
        for (int i = 1; i <= s.length(); i++) {
            for (int j = 0; j < i; j++) {
                if (dp[j] && wordSet.contains(s.substring(j, i))) {
                    dp[i] = true;
                    break;
                }
            }
        }
        
        return dp[s.length()];
    }
}
```

---

## 🎯 DP Pattern Recognition

### 1D DP

```
State depends on previous elements
Examples: Climbing Stairs, House Robber, Decode Ways
Pattern: dp[i] depends on dp[i-1], dp[i-2], etc.
```

### 2D DP

```
Two sequences/strings
Examples: LCS, Edit Distance, Regex Matching
Pattern: dp[i][j] depends on dp[i-1][j], dp[i][j-1], dp[i-1][j-1]
```

### Knapsack DP

```
Include/exclude decision
Examples: 0/1 Knapsack, Partition, Coin Change
Pattern: dp[i][w] = max(take, don't take)
```

---

**Next:** [Graph Algorithms](./08-Graph-Algorithms.md)
