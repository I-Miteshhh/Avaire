# Two Pointers & Sliding Window

**Difficulty:** Medium  
**Learning Time:** 1 week  
**Interview Frequency:** ⭐⭐⭐⭐⭐ (Extremely High)  
**Common In:** Array/String problems, optimization problems

---

## 📚 Table of Contents

1. [Two Pointers Pattern](#two-pointers-pattern)
2. [Sliding Window Pattern](#sliding-window-pattern)
3. [Interview Problems](#interview-problems)
4. [Real-World Applications](#real-world-applications)

---

## Two Pointers Pattern

### Concept

Use two pointers to iterate through data structure, typically to:
- Find pair/triplet with target sum
- Remove duplicates in-place
- Reverse array/string
- Merge sorted arrays

### Types

1. **Same Direction (Fast-Slow):** Both move forward, different speeds
2. **Opposite Direction:** One from start, one from end
3. **Sliding Window:** Maintain window between pointers

---

## Pattern 1: Opposite Direction Pointers

### Characteristics

```
Start:  [1, 2, 3, 4, 5]
         ↑           ↑
        left       right

Move inward until left >= right
```

### Template

```java
public void oppositeDirection(int[] arr) {
    int left = 0;
    int right = arr.length - 1;
    
    while (left < right) {
        // Process arr[left] and arr[right]
        
        // Move pointers based on condition
        if (condition) {
            left++;
        } else {
            right--;
        }
    }
}
```

### Problem 1: Two Sum II (Sorted Array)

**LeetCode 167**

```java
/**
 * Find two numbers that add up to target in sorted array
 * Time: O(n), Space: O(1)
 */
class Solution {
    public int[] twoSum(int[] numbers, int target) {
        int left = 0;
        int right = numbers.length - 1;
        
        while (left < right) {
            int sum = numbers[left] + numbers[right];
            
            if (sum == target) {
                return new int[]{left + 1, right + 1};  // 1-indexed
            } else if (sum < target) {
                left++;  // Need larger sum
            } else {
                right--;  // Need smaller sum
            }
        }
        
        return new int[]{-1, -1};  // No solution
    }
}
```

**Complexity:**
- Time: O(n) - single pass
- Space: O(1) - no extra space

**Why Two Pointers Works:**
- Array is sorted
- If sum too small → increase left (moves to larger value)
- If sum too large → decrease right (moves to smaller value)

---

### Problem 2: Container With Most Water

**LeetCode 11**

```java
/**
 * Find two lines that form container with max area
 * Area = min(height[i], height[j]) * (j - i)
 * 
 * Time: O(n), Space: O(1)
 */
class Solution {
    public int maxArea(int[] height) {
        int left = 0;
        int right = height.length - 1;
        int maxArea = 0;
        
        while (left < right) {
            // Calculate current area
            int width = right - left;
            int currentHeight = Math.min(height[left], height[right]);
            int area = width * currentHeight;
            
            maxArea = Math.max(maxArea, area);
            
            // Move pointer with smaller height
            // (moving larger height won't increase area)
            if (height[left] < height[right]) {
                left++;
            } else {
                right--;
            }
        }
        
        return maxArea;
    }
}
```

**Key Insight:**
- Always move pointer with smaller height
- Moving larger height can only decrease area (width decreases, height can't increase)

---

### Problem 3: 3Sum

**LeetCode 15**

```java
/**
 * Find all unique triplets that sum to zero
 * Time: O(n²), Space: O(1) (excluding output)
 */
class Solution {
    public List<List<Integer>> threeSum(int[] nums) {
        List<List<Integer>> result = new ArrayList<>();
        
        // Sort array
        Arrays.sort(nums);
        
        for (int i = 0; i < nums.length - 2; i++) {
            // Skip duplicates for first element
            if (i > 0 && nums[i] == nums[i - 1]) {
                continue;
            }
            
            // Two sum on remaining array
            int target = -nums[i];
            int left = i + 1;
            int right = nums.length - 1;
            
            while (left < right) {
                int sum = nums[left] + nums[right];
                
                if (sum == target) {
                    result.add(Arrays.asList(nums[i], nums[left], nums[right]));
                    
                    // Skip duplicates
                    while (left < right && nums[left] == nums[left + 1]) {
                        left++;
                    }
                    while (left < right && nums[right] == nums[right - 1]) {
                        right--;
                    }
                    
                    left++;
                    right--;
                } else if (sum < target) {
                    left++;
                } else {
                    right--;
                }
            }
        }
        
        return result;
    }
}
```

**Complexity:**
- Time: O(n²) - O(n log n) sort + O(n) * O(n) two sum
- Space: O(1) excluding output

**Extension: 4Sum (LeetCode 18)**

```java
/**
 * Find all unique quadruplets that sum to target
 * Time: O(n³), Space: O(1)
 */
class Solution {
    public List<List<Integer>> fourSum(int[] nums, int target) {
        List<List<Integer>> result = new ArrayList<>();
        Arrays.sort(nums);
        
        for (int i = 0; i < nums.length - 3; i++) {
            if (i > 0 && nums[i] == nums[i - 1]) continue;
            
            for (int j = i + 1; j < nums.length - 2; j++) {
                if (j > i + 1 && nums[j] == nums[j - 1]) continue;
                
                int left = j + 1;
                int right = nums.length - 1;
                
                while (left < right) {
                    long sum = (long) nums[i] + nums[j] + nums[left] + nums[right];
                    
                    if (sum == target) {
                        result.add(Arrays.asList(nums[i], nums[j], nums[left], nums[right]));
                        
                        while (left < right && nums[left] == nums[left + 1]) left++;
                        while (left < right && nums[right] == nums[right - 1]) right--;
                        
                        left++;
                        right--;
                    } else if (sum < target) {
                        left++;
                    } else {
                        right--;
                    }
                }
            }
        }
        
        return result;
    }
}
```

---

## Pattern 2: Same Direction Pointers (Fast-Slow)

### Characteristics

```
Start:  [1, 2, 2, 3, 4, 4, 5]
         ↑
       slow/fast

Process: Move fast, copy unique to slow
```

### Template

```java
public int fastSlow(int[] arr) {
    int slow = 0;
    
    for (int fast = 0; fast < arr.length; fast++) {
        if (condition) {
            arr[slow] = arr[fast];
            slow++;
        }
    }
    
    return slow;  // New length
}
```

### Problem 4: Remove Duplicates from Sorted Array

**LeetCode 26**

```java
/**
 * Remove duplicates in-place, return new length
 * Time: O(n), Space: O(1)
 */
class Solution {
    public int removeDuplicates(int[] nums) {
        if (nums.length == 0) return 0;
        
        int slow = 1;  // Position to place next unique element
        
        for (int fast = 1; fast < nums.length; fast++) {
            if (nums[fast] != nums[fast - 1]) {
                nums[slow] = nums[fast];
                slow++;
            }
        }
        
        return slow;
    }
}
```

**Visualization:**

```
[1, 1, 2, 2, 3] → [1, 2, 3, ?, ?]
 s                  s
 f

[1, 1, 2, 2, 3]
    s
    f

[1, 1, 2, 2, 3]
    s
       f

[1, 2, 2, 2, 3]
       s
       f
```

---

### Problem 5: Move Zeroes

**LeetCode 283**

```java
/**
 * Move all zeros to end, maintain relative order
 * Time: O(n), Space: O(1)
 */
class Solution {
    public void moveZeroes(int[] nums) {
        int slow = 0;  // Position for next non-zero
        
        // Move all non-zeros to front
        for (int fast = 0; fast < nums.length; fast++) {
            if (nums[fast] != 0) {
                nums[slow] = nums[fast];
                slow++;
            }
        }
        
        // Fill remaining with zeros
        while (slow < nums.length) {
            nums[slow] = 0;
            slow++;
        }
    }
}

/**
 * Alternative: Swap approach (preserves non-zero positions)
 */
class SolutionSwap {
    public void moveZeroes(int[] nums) {
        int slow = 0;
        
        for (int fast = 0; fast < nums.length; fast++) {
            if (nums[fast] != 0) {
                // Swap nums[slow] and nums[fast]
                int temp = nums[slow];
                nums[slow] = nums[fast];
                nums[fast] = temp;
                slow++;
            }
        }
    }
}
```

---

## Sliding Window Pattern

### Concept

Maintain a window `[left, right]` that satisfies certain condition.

### Types

1. **Fixed Size Window:** Window size constant (e.g., k)
2. **Variable Size Window:** Window expands/contracts based on condition

---

## Pattern 3: Fixed Size Sliding Window

### Template

```java
public void fixedWindow(int[] arr, int k) {
    // Initialize window [0, k-1]
    for (int i = 0; i < k; i++) {
        // Add arr[i] to window
    }
    
    // Slide window
    for (int i = k; i < arr.length; i++) {
        // Remove arr[i - k] from window
        // Add arr[i] to window
        // Process window
    }
}
```

### Problem 6: Maximum Sum Subarray of Size K

```java
/**
 * Find maximum sum of any subarray of size k
 * Time: O(n), Space: O(1)
 */
class Solution {
    public int maxSumSubarray(int[] arr, int k) {
        if (arr.length < k) {
            throw new IllegalArgumentException("Array too small");
        }
        
        // Initialize first window
        int windowSum = 0;
        for (int i = 0; i < k; i++) {
            windowSum += arr[i];
        }
        
        int maxSum = windowSum;
        
        // Slide window
        for (int i = k; i < arr.length; i++) {
            windowSum += arr[i] - arr[i - k];  // Add new, remove old
            maxSum = Math.max(maxSum, windowSum);
        }
        
        return maxSum;
    }
}
```

**Brute Force (O(n*k)):**

```java
// Don't do this!
for (int i = 0; i <= arr.length - k; i++) {
    int sum = 0;
    for (int j = i; j < i + k; j++) {
        sum += arr[j];
    }
    maxSum = Math.max(maxSum, sum);
}
```

---

### Problem 7: Sliding Window Maximum

**LeetCode 239**

```java
/**
 * Find maximum in each sliding window of size k
 * Use deque to maintain decreasing order
 * 
 * Time: O(n), Space: O(k)
 */
class Solution {
    public int[] maxSlidingWindow(int[] nums, int k) {
        int n = nums.length;
        int[] result = new int[n - k + 1];
        Deque<Integer> deque = new ArrayDeque<>();  // Store indices
        
        for (int i = 0; i < n; i++) {
            // Remove indices outside window
            while (!deque.isEmpty() && deque.peekFirst() < i - k + 1) {
                deque.pollFirst();
            }
            
            // Remove smaller elements (they'll never be max)
            while (!deque.isEmpty() && nums[deque.peekLast()] < nums[i]) {
                deque.pollLast();
            }
            
            deque.offerLast(i);
            
            // Add to result (window is full)
            if (i >= k - 1) {
                result[i - k + 1] = nums[deque.peekFirst()];
            }
        }
        
        return result;
    }
}
```

**Deque maintains:**
- Indices in decreasing order of values
- Front has index of maximum element

---

## Pattern 4: Variable Size Sliding Window

### Template

```java
public int variableWindow(int[] arr, int target) {
    int left = 0;
    int sum = 0;
    int result = 0;
    
    for (int right = 0; right < arr.length; right++) {
        sum += arr[right];
        
        // Shrink window while condition violated
        while (sum > target) {
            sum -= arr[left];
            left++;
        }
        
        // Update result
        result = Math.max(result, right - left + 1);
    }
    
    return result;
}
```

### Problem 8: Longest Substring Without Repeating Characters

**LeetCode 3**

```java
/**
 * Find length of longest substring without repeating characters
 * Time: O(n), Space: O(min(m, n)) where m = alphabet size
 */
class Solution {
    public int lengthOfLongestSubstring(String s) {
        Map<Character, Integer> lastSeen = new HashMap<>();
        int maxLength = 0;
        int left = 0;
        
        for (int right = 0; right < s.length(); right++) {
            char c = s.charAt(right);
            
            // If character seen in current window, move left
            if (lastSeen.containsKey(c) && lastSeen.get(c) >= left) {
                left = lastSeen.get(c) + 1;
            }
            
            lastSeen.put(c, right);
            maxLength = Math.max(maxLength, right - left + 1);
        }
        
        return maxLength;
    }
}

/**
 * Alternative: Using array for ASCII characters
 */
class SolutionArray {
    public int lengthOfLongestSubstring(String s) {
        int[] lastIndex = new int[128];  // ASCII
        Arrays.fill(lastIndex, -1);
        
        int maxLength = 0;
        int left = 0;
        
        for (int right = 0; right < s.length(); right++) {
            char c = s.charAt(right);
            
            left = Math.max(left, lastIndex[c] + 1);
            lastIndex[c] = right;
            maxLength = Math.max(maxLength, right - left + 1);
        }
        
        return maxLength;
    }
}
```

---

### Problem 9: Minimum Window Substring

**LeetCode 76**

```java
/**
 * Find minimum window in s that contains all characters in t
 * Time: O(|s| + |t|), Space: O(|t|)
 */
class Solution {
    public String minWindow(String s, String t) {
        if (s.length() < t.length()) return "";
        
        // Count characters in t
        Map<Character, Integer> targetCount = new HashMap<>();
        for (char c : t.toCharArray()) {
            targetCount.put(c, targetCount.getOrDefault(c, 0) + 1);
        }
        
        Map<Character, Integer> windowCount = new HashMap<>();
        int required = targetCount.size();
        int formed = 0;  // Number of unique chars in window with desired frequency
        
        int left = 0;
        int minLen = Integer.MAX_VALUE;
        int minLeft = 0;
        
        for (int right = 0; right < s.length(); right++) {
            char c = s.charAt(right);
            windowCount.put(c, windowCount.getOrDefault(c, 0) + 1);
            
            // Check if frequency of current character matches
            if (targetCount.containsKey(c) && 
                windowCount.get(c).intValue() == targetCount.get(c).intValue()) {
                formed++;
            }
            
            // Try to shrink window
            while (formed == required && left <= right) {
                // Update result
                if (right - left + 1 < minLen) {
                    minLen = right - left + 1;
                    minLeft = left;
                }
                
                // Remove leftmost character
                char leftChar = s.charAt(left);
                windowCount.put(leftChar, windowCount.get(leftChar) - 1);
                
                if (targetCount.containsKey(leftChar) && 
                    windowCount.get(leftChar) < targetCount.get(leftChar)) {
                    formed--;
                }
                
                left++;
            }
        }
        
        return minLen == Integer.MAX_VALUE ? "" : s.substring(minLeft, minLeft + minLen);
    }
}
```

---

### Problem 10: Subarray Sum Equals K

**LeetCode 560**

```java
/**
 * Count subarrays with sum equal to k
 * Use prefix sum + hashmap
 * 
 * Time: O(n), Space: O(n)
 */
class Solution {
    public int subarraySum(int[] nums, int k) {
        Map<Integer, Integer> prefixSumCount = new HashMap<>();
        prefixSumCount.put(0, 1);  // Empty subarray
        
        int sum = 0;
        int count = 0;
        
        for (int num : nums) {
            sum += num;
            
            // Check if (sum - k) exists
            // If yes, there's a subarray ending here with sum k
            if (prefixSumCount.containsKey(sum - k)) {
                count += prefixSumCount.get(sum - k);
            }
            
            prefixSumCount.put(sum, prefixSumCount.getOrDefault(sum, 0) + 1);
        }
        
        return count;
    }
}
```

**Why it works:**

```
If prefix_sum[i] - prefix_sum[j] = k
Then subarray (j, i] has sum k

Example: nums = [1, 2, 3], k = 3
prefix_sum = [0, 1, 3, 6]

At i=2 (sum=3):
  sum - k = 3 - 3 = 0
  prefixSumCount[0] = 1
  So 1 subarray: [1, 2]

At i=3 (sum=6):
  sum - k = 6 - 3 = 3
  prefixSumCount[3] = 1
  So 1 subarray: [3]
```

---

## Real-World Data Engineering Applications

### 1. Stream Processing (Kafka)

```java
/**
 * Detect anomalies in streaming data
 * Use sliding window to compute moving average
 */
class StreamAnomalyDetector {
    private final Queue<Double> window;
    private final int windowSize;
    private double sum;
    
    public StreamAnomalyDetector(int windowSize) {
        this.window = new LinkedList<>();
        this.windowSize = windowSize;
        this.sum = 0.0;
    }
    
    public boolean isAnomaly(double value, double threshold) {
        // Add new value
        window.offer(value);
        sum += value;
        
        // Remove old value if window full
        if (window.size() > windowSize) {
            sum -= window.poll();
        }
        
        // Check if value deviates from moving average
        double avg = sum / window.size();
        return Math.abs(value - avg) > threshold * avg;
    }
}
```

### 2. Time-Series Data Processing (Spark)

```java
/**
 * Aggregate metrics over time windows
 */
class TimeSeriesAggregator {
    
    static class Event {
        long timestamp;
        double value;
        
        Event(long timestamp, double value) {
            this.timestamp = timestamp;
            this.value = value;
        }
    }
    
    /**
     * Compute 1-hour rolling sum
     */
    public List<Double> rollingSumHourly(List<Event> events) {
        List<Double> results = new ArrayList<>();
        Queue<Event> window = new LinkedList<>();
        double sum = 0.0;
        long windowMs = 3600_000L;  // 1 hour
        
        for (Event event : events) {
            // Add new event
            window.offer(event);
            sum += event.value;
            
            // Remove old events outside window
            while (!window.isEmpty() && 
                   event.timestamp - window.peek().timestamp > windowMs) {
                sum -= window.poll().value;
            }
            
            results.add(sum);
        }
        
        return results;
    }
}
```

---

## 🎯 Interview Tips

### Pattern Recognition

**Use Two Pointers when:**
- Array/string is sorted
- Need to find pair/triplet
- In-place modification required
- Merge sorted structures

**Use Sliding Window when:**
- Subarray/substring problem
- Need to optimize brute force O(n²) → O(n)
- "Maximum/minimum subarray" problems
- "Longest/shortest substring" problems

### Common Mistakes

1. **Off-by-one errors:**
   ```java
   // ❌ Wrong
   while (left <= right)  // Should be <
   
   // ✅ Correct
   while (left < right)
   ```

2. **Forgetting to update window:**
   ```java
   // ❌ Wrong
   sum += arr[right];
   // Forgot to remove arr[left]
   
   // ✅ Correct
   sum += arr[right];
   sum -= arr[left];
   left++;
   ```

3. **Not handling duplicates:**
   ```java
   // ❌ Wrong - includes duplicates
   result.add(Arrays.asList(nums[i], nums[left], nums[right]));
   left++; right--;
   
   // ✅ Correct
   while (left < right && nums[left] == nums[left + 1]) left++;
   while (left < right && nums[right] == nums[right - 1]) right--;
   left++; right--;
   ```

---

## 📊 Complexity Cheat Sheet

| Problem Pattern | Time | Space |
|----------------|------|-------|
| Two Sum (sorted) | O(n) | O(1) |
| 3Sum | O(n²) | O(1) |
| 4Sum | O(n³) | O(1) |
| Remove Duplicates | O(n) | O(1) |
| Fixed Window Max | O(n) | O(1) |
| Sliding Window Max (deque) | O(n) | O(k) |
| Longest Substring | O(n) | O(min(m,n)) |
| Minimum Window | O(n+m) | O(m) |
| Subarray Sum K | O(n) | O(n) |

---

**Next:** [Recursion & Backtracking](./04-Recursion-Backtracking.md)
