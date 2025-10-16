# Sorting Algorithms

**Difficulty:** Fundamental to Advanced  
**Learning Time:** 1 week  
**Interview Frequency:** ⭐⭐⭐⭐⭐ (Extremely High)

---

## 📚 Table of Contents

1. [Quick Sort](#quick-sort)
2. [Merge Sort](#merge-sort)
3. [Heap Sort](#heap-sort)
4. [Counting Sort](#counting-sort)
5. [Radix Sort](#radix-sort)
6. [Bucket Sort](#bucket-sort)
7. [Comparison](#comparison)

---

## Quick Sort

### Characteristics

```
- Divide-and-Conquer algorithm
- Average: O(n log n)
- Worst: O(n²) (already sorted, bad pivot)
- Space: O(log n) recursive stack
- NOT stable
- In-place sorting
```

### Implementation

```java
/**
 * QuickSort with different pivot strategies
 */
class QuickSort {
    
    /**
     * QuickSort - Last element as pivot
     * Time: O(n log n) average, O(n²) worst
     * Space: O(log n) stack
     */
    public static void quickSort(int[] arr) {
        quickSortHelper(arr, 0, arr.length - 1);
    }
    
    private static void quickSortHelper(int[] arr, int low, int high) {
        if (low < high) {
            int pivotIndex = partition(arr, low, high);
            
            quickSortHelper(arr, low, pivotIndex - 1);
            quickSortHelper(arr, pivotIndex + 1, high);
        }
    }
    
    /**
     * Lomuto Partition Scheme
     * Pivot = last element
     */
    private static int partition(int[] arr, int low, int high) {
        int pivot = arr[high];
        int i = low - 1;  // Index of smaller element
        
        for (int j = low; j < high; j++) {
            if (arr[j] <= pivot) {
                i++;
                swap(arr, i, j);
            }
        }
        
        swap(arr, i + 1, high);
        return i + 1;
    }
    
    /**
     * Hoare Partition Scheme (more efficient)
     * Pivot = first element
     */
    private static int hoarePartition(int[] arr, int low, int high) {
        int pivot = arr[low];
        int i = low - 1;
        int j = high + 1;
        
        while (true) {
            do {
                i++;
            } while (arr[i] < pivot);
            
            do {
                j--;
            } while (arr[j] > pivot);
            
            if (i >= j) {
                return j;
            }
            
            swap(arr, i, j);
        }
    }
    
    /**
     * QuickSort with Random Pivot (prevents O(n²) on sorted data)
     */
    public static void quickSortRandom(int[] arr) {
        quickSortRandomHelper(arr, 0, arr.length - 1);
    }
    
    private static void quickSortRandomHelper(int[] arr, int low, int high) {
        if (low < high) {
            int pivotIndex = randomPartition(arr, low, high);
            
            quickSortRandomHelper(arr, low, pivotIndex - 1);
            quickSortRandomHelper(arr, pivotIndex + 1, high);
        }
    }
    
    private static int randomPartition(int[] arr, int low, int high) {
        Random rand = new Random();
        int randomIndex = low + rand.nextInt(high - low + 1);
        
        swap(arr, randomIndex, high);  // Move random pivot to end
        
        return partition(arr, low, high);
    }
    
    /**
     * 3-Way QuickSort (Dutch National Flag)
     * Efficient for arrays with many duplicate elements
     */
    public static void quickSort3Way(int[] arr) {
        quickSort3WayHelper(arr, 0, arr.length - 1);
    }
    
    private static void quickSort3WayHelper(int[] arr, int low, int high) {
        if (low >= high) {
            return;
        }
        
        int pivot = arr[low];
        int lt = low;      // arr[low..lt-1] < pivot
        int gt = high;     // arr[gt+1..high] > pivot
        int i = low + 1;   // arr[lt..i-1] == pivot
        
        while (i <= gt) {
            if (arr[i] < pivot) {
                swap(arr, lt++, i++);
            } else if (arr[i] > pivot) {
                swap(arr, i, gt--);
            } else {
                i++;
            }
        }
        
        quickSort3WayHelper(arr, low, lt - 1);
        quickSort3WayHelper(arr, gt + 1, high);
    }
    
    private static void swap(int[] arr, int i, int j) {
        int temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }
}
```

### Optimizations

```java
/**
 * Hybrid QuickSort + InsertionSort
 * Use insertion sort for small subarrays (< 10 elements)
 */
class OptimizedQuickSort {
    private static final int INSERTION_SORT_THRESHOLD = 10;
    
    public static void sort(int[] arr) {
        sortHelper(arr, 0, arr.length - 1);
    }
    
    private static void sortHelper(int[] arr, int low, int high) {
        if (high - low < INSERTION_SORT_THRESHOLD) {
            insertionSort(arr, low, high);
            return;
        }
        
        int pivotIndex = partition(arr, low, high);
        sortHelper(arr, low, pivotIndex - 1);
        sortHelper(arr, pivotIndex + 1, high);
    }
    
    private static void insertionSort(int[] arr, int low, int high) {
        for (int i = low + 1; i <= high; i++) {
            int key = arr[i];
            int j = i - 1;
            
            while (j >= low && arr[j] > key) {
                arr[j + 1] = arr[j];
                j--;
            }
            
            arr[j + 1] = key;
        }
    }
    
    private static int partition(int[] arr, int low, int high) {
        int pivot = arr[high];
        int i = low - 1;
        
        for (int j = low; j < high; j++) {
            if (arr[j] <= pivot) {
                i++;
                swap(arr, i, j);
            }
        }
        
        swap(arr, i + 1, high);
        return i + 1;
    }
    
    private static void swap(int[] arr, int i, int j) {
        int temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }
}
```

---

## Merge Sort

### Characteristics

```
- Divide-and-Conquer algorithm
- Time: O(n log n) always
- Space: O(n) auxiliary array
- STABLE sort
- Good for linked lists, external sorting
```

### Implementation

```java
/**
 * Merge Sort
 */
class MergeSort {
    
    /**
     * Top-down (recursive) merge sort
     * Time: O(n log n)
     * Space: O(n)
     */
    public static void mergeSort(int[] arr) {
        if (arr == null || arr.length <= 1) {
            return;
        }
        
        int[] temp = new int[arr.length];
        mergeSortHelper(arr, temp, 0, arr.length - 1);
    }
    
    private static void mergeSortHelper(int[] arr, int[] temp, int left, int right) {
        if (left >= right) {
            return;
        }
        
        int mid = left + (right - left) / 2;
        
        mergeSortHelper(arr, temp, left, mid);
        mergeSortHelper(arr, temp, mid + 1, right);
        merge(arr, temp, left, mid, right);
    }
    
    /**
     * Merge two sorted subarrays
     */
    private static void merge(int[] arr, int[] temp, int left, int mid, int right) {
        // Copy to temp array
        for (int i = left; i <= right; i++) {
            temp[i] = arr[i];
        }
        
        int i = left;       // Left subarray index
        int j = mid + 1;    // Right subarray index
        int k = left;       // Merged array index
        
        while (i <= mid && j <= right) {
            if (temp[i] <= temp[j]) {
                arr[k++] = temp[i++];
            } else {
                arr[k++] = temp[j++];
            }
        }
        
        // Copy remaining elements from left subarray
        while (i <= mid) {
            arr[k++] = temp[i++];
        }
        
        // Right subarray already in place
    }
    
    /**
     * Bottom-up (iterative) merge sort
     * No recursion, better for some systems
     */
    public static void mergeSortIterative(int[] arr) {
        int n = arr.length;
        int[] temp = new int[n];
        
        // Merge subarrays of size 1, 2, 4, 8, ...
        for (int size = 1; size < n; size *= 2) {
            for (int left = 0; left < n - size; left += 2 * size) {
                int mid = left + size - 1;
                int right = Math.min(left + 2 * size - 1, n - 1);
                
                merge(arr, temp, left, mid, right);
            }
        }
    }
}

/**
 * Merge Sort for Linked List
 * No extra space needed!
 */
class ListNode {
    int val;
    ListNode next;
    
    ListNode(int val) {
        this.val = val;
    }
}

class MergeSortLinkedList {
    
    public ListNode sortList(ListNode head) {
        if (head == null || head.next == null) {
            return head;
        }
        
        // Find middle using slow/fast pointers
        ListNode slow = head;
        ListNode fast = head;
        ListNode prev = null;
        
        while (fast != null && fast.next != null) {
            prev = slow;
            slow = slow.next;
            fast = fast.next.next;
        }
        
        prev.next = null;  // Split list
        
        ListNode left = sortList(head);
        ListNode right = sortList(slow);
        
        return merge(left, right);
    }
    
    private ListNode merge(ListNode l1, ListNode l2) {
        ListNode dummy = new ListNode(0);
        ListNode curr = dummy;
        
        while (l1 != null && l2 != null) {
            if (l1.val <= l2.val) {
                curr.next = l1;
                l1 = l1.next;
            } else {
                curr.next = l2;
                l2 = l2.next;
            }
            curr = curr.next;
        }
        
        curr.next = (l1 != null) ? l1 : l2;
        
        return dummy.next;
    }
}
```

---

## Heap Sort

### Characteristics

```
- Uses binary heap
- Time: O(n log n) always
- Space: O(1) in-place
- NOT stable
- Good when memory is limited
```

### Implementation

```java
/**
 * Heap Sort
 */
class HeapSort {
    
    /**
     * Heap sort using max heap
     * Time: O(n log n)
     * Space: O(1)
     */
    public static void heapSort(int[] arr) {
        int n = arr.length;
        
        // Build max heap: O(n)
        for (int i = n / 2 - 1; i >= 0; i--) {
            heapify(arr, n, i);
        }
        
        // Extract elements from heap one by one
        for (int i = n - 1; i > 0; i--) {
            // Move current root to end
            swap(arr, 0, i);
            
            // Heapify reduced heap
            heapify(arr, i, 0);
        }
    }
    
    /**
     * Heapify subtree rooted at index i
     * n = size of heap
     */
    private static void heapify(int[] arr, int n, int i) {
        int largest = i;
        int left = 2 * i + 1;
        int right = 2 * i + 2;
        
        if (left < n && arr[left] > arr[largest]) {
            largest = left;
        }
        
        if (right < n && arr[right] > arr[largest]) {
            largest = right;
        }
        
        if (largest != i) {
            swap(arr, i, largest);
            heapify(arr, n, largest);
        }
    }
    
    private static void swap(int[] arr, int i, int j) {
        int temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }
}
```

---

## Counting Sort

### Characteristics

```
- Non-comparison sort
- Time: O(n + k) where k = range
- Space: O(k)
- STABLE (with careful implementation)
- Only works for integers in limited range
```

### Implementation

```java
/**
 * Counting Sort
 */
class CountingSort {
    
    /**
     * Counting sort for positive integers
     * Time: O(n + k)
     * Space: O(k)
     */
    public static void countingSort(int[] arr) {
        if (arr == null || arr.length == 0) {
            return;
        }
        
        // Find max element
        int max = Arrays.stream(arr).max().getAsInt();
        
        countingSort(arr, max);
    }
    
    private static void countingSort(int[] arr, int max) {
        int[] count = new int[max + 1];
        int[] output = new int[arr.length];
        
        // Count occurrences
        for (int num : arr) {
            count[num]++;
        }
        
        // Cumulative count (for stable sort)
        for (int i = 1; i <= max; i++) {
            count[i] += count[i - 1];
        }
        
        // Build output array (traverse backwards for stability)
        for (int i = arr.length - 1; i >= 0; i--) {
            output[count[arr[i]] - 1] = arr[i];
            count[arr[i]]--;
        }
        
        // Copy back
        System.arraycopy(output, 0, arr, 0, arr.length);
    }
    
    /**
     * Counting sort with negative numbers
     */
    public static void countingSortWithNegatives(int[] arr) {
        if (arr == null || arr.length == 0) {
            return;
        }
        
        int min = Arrays.stream(arr).min().getAsInt();
        int max = Arrays.stream(arr).max().getAsInt();
        int range = max - min + 1;
        
        int[] count = new int[range];
        int[] output = new int[arr.length];
        
        // Count occurrences (shift by min)
        for (int num : arr) {
            count[num - min]++;
        }
        
        // Cumulative count
        for (int i = 1; i < range; i++) {
            count[i] += count[i - 1];
        }
        
        // Build output
        for (int i = arr.length - 1; i >= 0; i--) {
            output[count[arr[i] - min] - 1] = arr[i];
            count[arr[i] - min]--;
        }
        
        System.arraycopy(output, 0, arr, 0, arr.length);
    }
}
```

---

## Radix Sort

### Characteristics

```
- Non-comparison sort
- Time: O(d * (n + k)) where d = digits, k = range
- Space: O(n + k)
- STABLE
- Good for sorting large numbers
```

### Implementation

```java
/**
 * Radix Sort
 */
class RadixSort {
    
    /**
     * Radix sort (LSD - Least Significant Digit first)
     * Time: O(d * (n + 10)) where d = max digits
     * Space: O(n)
     */
    public static void radixSort(int[] arr) {
        if (arr == null || arr.length == 0) {
            return;
        }
        
        // Find max to know number of digits
        int max = Arrays.stream(arr).max().getAsInt();
        
        // Sort by each digit
        for (int exp = 1; max / exp > 0; exp *= 10) {
            countingSortByDigit(arr, exp);
        }
    }
    
    /**
     * Counting sort by specific digit
     */
    private static void countingSortByDigit(int[] arr, int exp) {
        int n = arr.length;
        int[] output = new int[n];
        int[] count = new int[10];  // Digits 0-9
        
        // Count occurrences of digit
        for (int num : arr) {
            int digit = (num / exp) % 10;
            count[digit]++;
        }
        
        // Cumulative count
        for (int i = 1; i < 10; i++) {
            count[i] += count[i - 1];
        }
        
        // Build output (backwards for stability)
        for (int i = n - 1; i >= 0; i--) {
            int digit = (arr[i] / exp) % 10;
            output[count[digit] - 1] = arr[i];
            count[digit]--;
        }
        
        System.arraycopy(output, 0, arr, 0, n);
    }
    
    /**
     * Radix sort for strings
     */
    public static void radixSortStrings(String[] arr) {
        if (arr == null || arr.length == 0) {
            return;
        }
        
        // Find max length
        int maxLen = Arrays.stream(arr).mapToInt(String::length).max().getAsInt();
        
        // Sort by each character position (right to left)
        for (int pos = maxLen - 1; pos >= 0; pos--) {
            countingSortByChar(arr, pos);
        }
    }
    
    private static void countingSortByChar(String[] arr, int pos) {
        int n = arr.length;
        String[] output = new String[n];
        int[] count = new int[256];  // ASCII characters
        
        for (String str : arr) {
            char ch = (pos < str.length()) ? str.charAt(pos) : 0;
            count[ch]++;
        }
        
        for (int i = 1; i < 256; i++) {
            count[i] += count[i - 1];
        }
        
        for (int i = n - 1; i >= 0; i--) {
            char ch = (pos < arr[i].length()) ? arr[i].charAt(pos) : 0;
            output[count[ch] - 1] = arr[i];
            count[ch]--;
        }
        
        System.arraycopy(output, 0, arr, 0, n);
    }
}
```

---

## Bucket Sort

### Characteristics

```
- Distribution sort
- Time: O(n + k) average, O(n²) worst
- Space: O(n + k)
- STABLE (if underlying sort is stable)
- Good for uniformly distributed data
```

### Implementation

```java
/**
 * Bucket Sort
 */
class BucketSort {
    
    /**
     * Bucket sort for floats in range [0, 1)
     * Time: O(n) average
     * Space: O(n)
     */
    public static void bucketSort(float[] arr) {
        int n = arr.length;
        
        // Create n buckets
        List<List<Float>> buckets = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            buckets.add(new ArrayList<>());
        }
        
        // Distribute elements into buckets
        for (float num : arr) {
            int bucketIndex = (int) (num * n);
            buckets.get(bucketIndex).add(num);
        }
        
        // Sort individual buckets
        for (List<Float> bucket : buckets) {
            Collections.sort(bucket);
        }
        
        // Concatenate buckets
        int index = 0;
        for (List<Float> bucket : buckets) {
            for (float num : bucket) {
                arr[index++] = num;
            }
        }
    }
    
    /**
     * Bucket sort for integers
     */
    public static void bucketSortIntegers(int[] arr, int bucketCount) {
        if (arr == null || arr.length == 0) {
            return;
        }
        
        int min = Arrays.stream(arr).min().getAsInt();
        int max = Arrays.stream(arr).max().getAsInt();
        int range = max - min + 1;
        int bucketSize = (range + bucketCount - 1) / bucketCount;
        
        // Create buckets
        List<List<Integer>> buckets = new ArrayList<>(bucketCount);
        for (int i = 0; i < bucketCount; i++) {
            buckets.add(new ArrayList<>());
        }
        
        // Distribute
        for (int num : arr) {
            int bucketIndex = (num - min) / bucketSize;
            buckets.get(bucketIndex).add(num);
        }
        
        // Sort buckets
        for (List<Integer> bucket : buckets) {
            Collections.sort(bucket);
        }
        
        // Concatenate
        int index = 0;
        for (List<Integer> bucket : buckets) {
            for (int num : bucket) {
                arr[index++] = num;
            }
        }
    }
}
```

---

## Comparison

### Time Complexity

| Algorithm | Best | Average | Worst | Space | Stable |
|-----------|------|---------|-------|-------|--------|
| **Quick Sort** | O(n log n) | O(n log n) | O(n²) | O(log n) | No |
| **Merge Sort** | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes |
| **Heap Sort** | O(n log n) | O(n log n) | O(n log n) | O(1) | No |
| **Counting Sort** | O(n + k) | O(n + k) | O(n + k) | O(k) | Yes |
| **Radix Sort** | O(d(n + k)) | O(d(n + k)) | O(d(n + k)) | O(n + k) | Yes |
| **Bucket Sort** | O(n + k) | O(n + k) | O(n²) | O(n + k) | Yes* |

*if underlying sort is stable

### When to Use

**QuickSort:**
- ✅ General purpose, good cache locality
- ✅ In-place sorting preferred
- ❌ Worst case O(n²) unacceptable

**MergeSort:**
- ✅ Stability required
- ✅ Worst case O(n log n) guaranteed
- ✅ Linked list sorting
- ❌ Extra space not available

**HeapSort:**
- ✅ Memory constrained (O(1) space)
- ✅ Worst case O(n log n) guaranteed
- ❌ Stability required

**Counting Sort:**
- ✅ Small range of integers (k is small)
- ✅ Linear time needed
- ❌ Large range (k > n)

**Radix Sort:**
- ✅ Large numbers, limited digits
- ✅ Linear time needed
- ❌ Variable-length data

**Bucket Sort:**
- ✅ Uniformly distributed data
- ✅ Float numbers
- ❌ Skewed distribution

---

## Interview Problems

### 1. Sort Colors (Dutch National Flag)

```java
/**
 * LeetCode 75: Sort Colors
 * Given array with 0s, 1s, 2s, sort in-place
 * Time: O(n), Space: O(1)
 */
class Solution {
    public void sortColors(int[] nums) {
        int low = 0, mid = 0, high = nums.length - 1;
        
        while (mid <= high) {
            if (nums[mid] == 0) {
                swap(nums, low++, mid++);
            } else if (nums[mid] == 1) {
                mid++;
            } else {
                swap(nums, mid, high--);
            }
        }
    }
    
    private void swap(int[] nums, int i, int j) {
        int temp = nums[i];
        nums[i] = nums[j];
        nums[j] = temp;
    }
}
```

### 2. Kth Largest Element (QuickSelect)

```java
/**
 * LeetCode 215: Kth Largest Element
 * Time: O(n) average, O(n²) worst
 * Space: O(1)
 */
class Solution {
    public int findKthLargest(int[] nums, int k) {
        return quickSelect(nums, 0, nums.length - 1, nums.length - k);
    }
    
    private int quickSelect(int[] nums, int left, int right, int k) {
        if (left == right) {
            return nums[left];
        }
        
        int pivotIndex = partition(nums, left, right);
        
        if (k == pivotIndex) {
            return nums[k];
        } else if (k < pivotIndex) {
            return quickSelect(nums, left, pivotIndex - 1, k);
        } else {
            return quickSelect(nums, pivotIndex + 1, right, k);
        }
    }
    
    private int partition(int[] nums, int left, int right) {
        int pivot = nums[right];
        int i = left;
        
        for (int j = left; j < right; j++) {
            if (nums[j] <= pivot) {
                swap(nums, i++, j);
            }
        }
        
        swap(nums, i, right);
        return i;
    }
    
    private void swap(int[] nums, int i, int j) {
        int temp = nums[i];
        nums[i] = nums[j];
        nums[j] = temp;
    }
}
```

---

**Next:** [Binary Search Variations](./02-Binary-Search-Variations.md)
