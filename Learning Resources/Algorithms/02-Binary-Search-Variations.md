# Binary Search Variations

**Difficulty:** Fundamental to Advanced  
**Learning Time:** 3-4 days  
**Interview Frequency:** ⭐⭐⭐⭐⭐ (Extremely High)

---

## 📚 Table of Contents

1. [Classic Binary Search](#classic-binary-search)
2. [Find First/Last Occurrence](#find-firstlast-occurrence)
3. [Search in Rotated Array](#search-in-rotated-array)
4. [Search in 2D Matrix](#search-in-2d-matrix)
5. [Search for Peak Element](#search-for-peak-element)
6. [Binary Search on Answer](#binary-search-on-answer)

---

## Classic Binary Search

### Template

```java
/**
 * Binary Search - Iterative
 * Time: O(log n)
 * Space: O(1)
 */
class BinarySearch {
    
    public int search(int[] nums, int target) {
        int left = 0, right = nums.length - 1;
        
        while (left <= right) {
            int mid = left + (right - left) / 2;  // Prevent overflow
            
            if (nums[mid] == target) {
                return mid;
            } else if (nums[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        
        return -1;  // Not found
    }
    
    /**
     * Binary Search - Recursive
     */
    public int searchRecursive(int[] nums, int target) {
        return searchHelper(nums, target, 0, nums.length - 1);
    }
    
    private int searchHelper(int[] nums, int target, int left, int right) {
        if (left > right) {
            return -1;
        }
        
        int mid = left + (right - left) / 2;
        
        if (nums[mid] == target) {
            return mid;
        } else if (nums[mid] < target) {
            return searchHelper(nums, target, mid + 1, right);
        } else {
            return searchHelper(nums, target, left, mid - 1);
        }
    }
}
```

---

## Find First/Last Occurrence

### Implementation

```java
/**
 * Find first and last position of target
 * LeetCode 34
 */
class Solution {
    
    /**
     * Find first occurrence
     * Time: O(log n)
     */
    public int findFirst(int[] nums, int target) {
        int left = 0, right = nums.length - 1;
        int result = -1;
        
        while (left <= right) {
            int mid = left + (right - left) / 2;
            
            if (nums[mid] == target) {
                result = mid;
                right = mid - 1;  // Continue searching left
            } else if (nums[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        
        return result;
    }
    
    /**
     * Find last occurrence
     */
    public int findLast(int[] nums, int target) {
        int left = 0, right = nums.length - 1;
        int result = -1;
        
        while (left <= right) {
            int mid = left + (right - left) / 2;
            
            if (nums[mid] == target) {
                result = mid;
                left = mid + 1;  // Continue searching right
            } else if (nums[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        
        return result;
    }
    
    /**
     * Find range [first, last]
     */
    public int[] searchRange(int[] nums, int target) {
        int first = findFirst(nums, target);
        
        if (first == -1) {
            return new int[]{-1, -1};
        }
        
        int last = findLast(nums, target);
        
        return new int[]{first, last};
    }
}
```

---

## Search in Rotated Array

### Implementation

```java
/**
 * Search in Rotated Sorted Array
 * LeetCode 33
 * 
 * Example: [4,5,6,7,0,1,2], target = 0 → index 4
 */
class Solution {
    
    /**
     * Time: O(log n)
     * Space: O(1)
     */
    public int search(int[] nums, int target) {
        int left = 0, right = nums.length - 1;
        
        while (left <= right) {
            int mid = left + (right - left) / 2;
            
            if (nums[mid] == target) {
                return mid;
            }
            
            // Determine which half is sorted
            if (nums[left] <= nums[mid]) {
                // Left half is sorted
                if (nums[left] <= target && target < nums[mid]) {
                    right = mid - 1;  // Target in left half
                } else {
                    left = mid + 1;   // Target in right half
                }
            } else {
                // Right half is sorted
                if (nums[mid] < target && target <= nums[right]) {
                    left = mid + 1;   // Target in right half
                } else {
                    right = mid - 1;  // Target in left half
                }
            }
        }
        
        return -1;
    }
    
    /**
     * Search in Rotated Array with Duplicates
     * LeetCode 81
     * 
     * Worst case: O(n) when all elements are same
     */
    public boolean searchWithDuplicates(int[] nums, int target) {
        int left = 0, right = nums.length - 1;
        
        while (left <= right) {
            int mid = left + (right - left) / 2;
            
            if (nums[mid] == target) {
                return true;
            }
            
            // Handle duplicates
            if (nums[left] == nums[mid] && nums[mid] == nums[right]) {
                left++;
                right--;
            } else if (nums[left] <= nums[mid]) {
                // Left half sorted
                if (nums[left] <= target && target < nums[mid]) {
                    right = mid - 1;
                } else {
                    left = mid + 1;
                }
            } else {
                // Right half sorted
                if (nums[mid] < target && target <= nums[right]) {
                    left = mid + 1;
                } else {
                    right = mid - 1;
                }
            }
        }
        
        return false;
    }
    
    /**
     * Find minimum in rotated array
     * LeetCode 153
     */
    public int findMin(int[] nums) {
        int left = 0, right = nums.length - 1;
        
        while (left < right) {
            int mid = left + (right - left) / 2;
            
            if (nums[mid] > nums[right]) {
                // Min is in right half
                left = mid + 1;
            } else {
                // Min is in left half or is mid
                right = mid;
            }
        }
        
        return nums[left];
    }
}
```

---

## Search in 2D Matrix

### Implementation

```java
/**
 * Search in 2D Matrix variations
 */
class Solution {
    
    /**
     * Matrix is fully sorted
     * LeetCode 74
     * 
     * [1, 3, 5, 7]
     * [10, 11, 16, 20]
     * [23, 30, 34, 60]
     * 
     * Time: O(log(m * n))
     */
    public boolean searchMatrix(int[][] matrix, int target) {
        if (matrix == null || matrix.length == 0) {
            return false;
        }
        
        int m = matrix.length;
        int n = matrix[0].length;
        
        int left = 0, right = m * n - 1;
        
        while (left <= right) {
            int mid = left + (right - left) / 2;
            int midValue = matrix[mid / n][mid % n];
            
            if (midValue == target) {
                return true;
            } else if (midValue < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        
        return false;
    }
    
    /**
     * Matrix rows and columns sorted separately
     * LeetCode 240
     * 
     * [1,  4,  7,  11, 15]
     * [2,  5,  8,  12, 19]
     * [3,  6,  9,  16, 22]
     * [10, 13, 14, 17, 24]
     * 
     * Time: O(m + n)
     */
    public boolean searchMatrixII(int[][] matrix, int target) {
        if (matrix == null || matrix.length == 0) {
            return false;
        }
        
        int row = 0;
        int col = matrix[0].length - 1;
        
        // Start from top-right corner
        while (row < matrix.length && col >= 0) {
            if (matrix[row][col] == target) {
                return true;
            } else if (matrix[row][col] > target) {
                col--;  // Move left
            } else {
                row++;  // Move down
            }
        }
        
        return false;
    }
}
```

---

## Search for Peak Element

### Implementation

```java
/**
 * Find Peak Element
 * LeetCode 162
 * 
 * Peak element is greater than its neighbors
 */
class Solution {
    
    /**
     * Time: O(log n)
     * Space: O(1)
     */
    public int findPeakElement(int[] nums) {
        int left = 0, right = nums.length - 1;
        
        while (left < right) {
            int mid = left + (right - left) / 2;
            
            if (nums[mid] > nums[mid + 1]) {
                // Peak is in left half (including mid)
                right = mid;
            } else {
                // Peak is in right half
                left = mid + 1;
            }
        }
        
        return left;
    }
    
    /**
     * Find Peak in 2D Array
     * LeetCode 1901
     */
    public int[] findPeakGrid(int[][] mat) {
        int left = 0, right = mat[0].length - 1;
        
        while (left <= right) {
            int midCol = left + (right - left) / 2;
            int maxRow = 0;
            
            // Find max in column
            for (int row = 0; row < mat.length; row++) {
                if (mat[row][midCol] > mat[maxRow][midCol]) {
                    maxRow = row;
                }
            }
            
            // Check if peak
            boolean leftBigger = midCol > 0 && mat[maxRow][midCol - 1] > mat[maxRow][midCol];
            boolean rightBigger = midCol < mat[0].length - 1 && 
                                  mat[maxRow][midCol + 1] > mat[maxRow][midCol];
            
            if (!leftBigger && !rightBigger) {
                return new int[]{maxRow, midCol};
            } else if (leftBigger) {
                right = midCol - 1;
            } else {
                left = midCol + 1;
            }
        }
        
        return new int[]{-1, -1};
    }
}
```

---

## Binary Search on Answer

### Concept

When answer is in a range and we can verify if a value works, use binary search.

### Implementation

```java
/**
 * Binary Search on Answer - Common Pattern
 */
class BinarySearchOnAnswer {
    
    /**
     * Koko Eating Bananas
     * LeetCode 875
     * 
     * Find minimum eating speed to finish all bananas in h hours
     * Time: O(n log m) where m = max(piles)
     */
    public int minEatingSpeed(int[] piles, int h) {
        int left = 1;
        int right = Arrays.stream(piles).max().getAsInt();
        
        while (left < right) {
            int mid = left + (right - left) / 2;
            
            if (canFinish(piles, mid, h)) {
                right = mid;  // Try slower speed
            } else {
                left = mid + 1;  // Need faster speed
            }
        }
        
        return left;
    }
    
    private boolean canFinish(int[] piles, int speed, int h) {
        long hours = 0;
        
        for (int pile : piles) {
            hours += (pile + speed - 1) / speed;  // Ceiling division
        }
        
        return hours <= h;
    }
    
    /**
     * Split Array Largest Sum
     * LeetCode 410
     * 
     * Split array into k subarrays, minimize largest sum
     * Time: O(n log(sum - max))
     */
    public int splitArray(int[] nums, int k) {
        int left = Arrays.stream(nums).max().getAsInt();  // Min possible (each element alone)
        int right = Arrays.stream(nums).sum();            // Max possible (all together)
        
        while (left < right) {
            int mid = left + (right - left) / 2;
            
            if (canSplit(nums, k, mid)) {
                right = mid;  // Try smaller max sum
            } else {
                left = mid + 1;  // Need larger max sum
            }
        }
        
        return left;
    }
    
    private boolean canSplit(int[] nums, int k, int maxSum) {
        int splits = 1;
        int currentSum = 0;
        
        for (int num : nums) {
            if (currentSum + num > maxSum) {
                splits++;
                currentSum = num;
                
                if (splits > k) {
                    return false;
                }
            } else {
                currentSum += num;
            }
        }
        
        return true;
    }
    
    /**
     * Capacity To Ship Packages Within D Days
     * LeetCode 1011
     */
    public int shipWithinDays(int[] weights, int days) {
        int left = Arrays.stream(weights).max().getAsInt();
        int right = Arrays.stream(weights).sum();
        
        while (left < right) {
            int mid = left + (right - left) / 2;
            
            if (canShip(weights, days, mid)) {
                right = mid;
            } else {
                left = mid + 1;
            }
        }
        
        return left;
    }
    
    private boolean canShip(int[] weights, int days, int capacity) {
        int daysNeeded = 1;
        int currentWeight = 0;
        
        for (int weight : weights) {
            if (currentWeight + weight > capacity) {
                daysNeeded++;
                currentWeight = weight;
                
                if (daysNeeded > days) {
                    return false;
                }
            } else {
                currentWeight += weight;
            }
        }
        
        return true;
    }
    
    /**
     * Minimize Max Distance to Gas Station
     * LeetCode 774
     * 
     * Add k gas stations to minimize max distance between adjacent stations
     * Time: O(n log(max - min))
     */
    public double minmaxGasDist(int[] stations, int k) {
        double left = 0;
        double right = stations[stations.length - 1] - stations[0];
        double epsilon = 1e-6;
        
        while (right - left > epsilon) {
            double mid = left + (right - left) / 2;
            
            if (canPlaceStations(stations, k, mid)) {
                right = mid;
            } else {
                left = mid;
            }
        }
        
        return left;
    }
    
    private boolean canPlaceStations(int[] stations, int k, double maxDist) {
        int stationsNeeded = 0;
        
        for (int i = 1; i < stations.length; i++) {
            double dist = stations[i] - stations[i - 1];
            stationsNeeded += (int) (dist / maxDist);
        }
        
        return stationsNeeded <= k;
    }
}
```

---

## Advanced Patterns

### Find Smallest Letter Greater Than Target

```java
/**
 * LeetCode 744
 * Time: O(log n)
 */
class Solution {
    public char nextGreatestLetter(char[] letters, char target) {
        int left = 0, right = letters.length - 1;
        
        while (left <= right) {
            int mid = left + (right - left) / 2;
            
            if (letters[mid] <= target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        
        // Wrap around if necessary
        return letters[left % letters.length];
    }
}
```

### Find K Closest Elements

```java
/**
 * LeetCode 658
 * Find k closest elements to x
 * Time: O(log n + k)
 */
class Solution {
    public List<Integer> findClosestElements(int[] arr, int k, int x) {
        int left = 0, right = arr.length - k;
        
        while (left < right) {
            int mid = left + (right - left) / 2;
            
            // Compare distances from x to arr[mid] and arr[mid + k]
            if (x - arr[mid] > arr[mid + k] - x) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }
        
        List<Integer> result = new ArrayList<>();
        for (int i = left; i < left + k; i++) {
            result.add(arr[i]);
        }
        
        return result;
    }
}
```

### Median of Two Sorted Arrays

```java
/**
 * LeetCode 4 (Hard)
 * Time: O(log(min(m, n)))
 * Space: O(1)
 */
class Solution {
    public double findMedianSortedArrays(int[] nums1, int[] nums2) {
        // Ensure nums1 is smaller
        if (nums1.length > nums2.length) {
            return findMedianSortedArrays(nums2, nums1);
        }
        
        int m = nums1.length;
        int n = nums2.length;
        int left = 0, right = m;
        
        while (left <= right) {
            int partition1 = left + (right - left) / 2;
            int partition2 = (m + n + 1) / 2 - partition1;
            
            int maxLeft1 = (partition1 == 0) ? Integer.MIN_VALUE : nums1[partition1 - 1];
            int minRight1 = (partition1 == m) ? Integer.MAX_VALUE : nums1[partition1];
            
            int maxLeft2 = (partition2 == 0) ? Integer.MIN_VALUE : nums2[partition2 - 1];
            int minRight2 = (partition2 == n) ? Integer.MAX_VALUE : nums2[partition2];
            
            if (maxLeft1 <= minRight2 && maxLeft2 <= minRight1) {
                // Found correct partition
                if ((m + n) % 2 == 0) {
                    return (Math.max(maxLeft1, maxLeft2) + Math.min(minRight1, minRight2)) / 2.0;
                } else {
                    return Math.max(maxLeft1, maxLeft2);
                }
            } else if (maxLeft1 > minRight2) {
                right = partition1 - 1;
            } else {
                left = partition1 + 1;
            }
        }
        
        throw new IllegalArgumentException("Input arrays are not sorted");
    }
}
```

---

## 🎯 Interview Tips

### Binary Search Template Choice

```java
// Template 1: Most common
while (left <= right) {
    int mid = left + (right - left) / 2;
    if (condition) {
        return mid;
    } else if (...) {
        left = mid + 1;
    } else {
        right = mid - 1;
    }
}
return -1;

// Template 2: Finding boundary
while (left < right) {
    int mid = left + (right - left) / 2;
    if (condition) {
        right = mid;
    } else {
        left = mid + 1;
    }
}
return left;

// Template 3: Two pointers with gap
while (left + 1 < right) {
    int mid = left + (right - left) / 2;
    if (condition) {
        right = mid;
    } else {
        left = mid;
    }
}
// Post-processing: check left and right
```

### Common Mistakes

1. **Integer Overflow:** Use `left + (right - left) / 2` instead of `(left + right) / 2`
2. **Infinite Loop:** Ensure `left` and `right` converge
3. **Off by One:** Carefully handle `left <= right` vs `left < right`
4. **Boundary Conditions:** Test with single element, two elements

---

**Next:** [Two Pointers & Sliding Window](./03-Two-Pointers-Sliding-Window.md)
