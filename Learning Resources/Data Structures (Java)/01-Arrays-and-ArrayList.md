# Arrays & Dynamic Arrays (ArrayList)

**Difficulty:** Fundamental  
**Learning Time:** 1 week  
**Interview Frequency:** ⭐⭐⭐⭐⭐ (Very High)

---

## 📚 Table of Contents

1. [Static Arrays](#static-arrays)
2. [Dynamic Arrays (ArrayList)](#dynamic-arrays-arraylist)
3. [Time & Space Complexity](#time--space-complexity)
4. [Custom Implementation](#custom-implementation-from-scratch)
5. [Interview Problems](#interview-problems)
6. [Advanced Techniques](#advanced-techniques)

---

## Static Arrays

### Characteristics
```
✅ Fixed size (determined at creation)
✅ Contiguous memory allocation
✅ Random access in O(1)
✅ Cache-friendly (locality of reference)
❌ Cannot grow/shrink
❌ Insertion/deletion expensive (O(n))
```

### Declaration & Initialization

```java
// Declaration
int[] arr1;                          // null reference
int[] arr2 = new int[5];            // [0, 0, 0, 0, 0]
int[] arr3 = {1, 2, 3, 4, 5};       // [1, 2, 3, 4, 5]
int[] arr4 = new int[]{1, 2, 3};    // [1, 2, 3]

// 2D arrays
int[][] matrix1 = new int[3][4];    // 3 rows, 4 columns
int[][] matrix2 = {
    {1, 2, 3},
    {4, 5, 6},
    {7, 8, 9}
};

// Jagged arrays (rows can have different lengths)
int[][] jagged = new int[3][];
jagged[0] = new int[]{1, 2};
jagged[1] = new int[]{3, 4, 5, 6};
jagged[2] = new int[]{7};
```

### Common Operations

```java
public class ArrayOperations {
    
    /**
     * Access element: O(1)
     */
    public int get(int[] arr, int index) {
        if (index < 0 || index >= arr.length) {
            throw new IndexOutOfBoundsException("Index: " + index);
        }
        return arr[index];
    }
    
    /**
     * Update element: O(1)
     */
    public void set(int[] arr, int index, int value) {
        if (index < 0 || index >= arr.length) {
            throw new IndexOutOfBoundsException("Index: " + index);
        }
        arr[index] = value;
    }
    
    /**
     * Insert at index: O(n) - Need to shift elements
     */
    public int[] insert(int[] arr, int index, int value) {
        if (index < 0 || index > arr.length) {
            throw new IndexOutOfBoundsException("Index: " + index);
        }
        
        int[] newArr = new int[arr.length + 1];
        
        // Copy elements before index
        System.arraycopy(arr, 0, newArr, 0, index);
        
        // Insert new value
        newArr[index] = value;
        
        // Copy elements after index
        System.arraycopy(arr, index, newArr, index + 1, arr.length - index);
        
        return newArr;
    }
    
    /**
     * Delete at index: O(n) - Need to shift elements
     */
    public int[] delete(int[] arr, int index) {
        if (index < 0 || index >= arr.length) {
            throw new IndexOutOfBoundsException("Index: " + index);
        }
        
        int[] newArr = new int[arr.length - 1];
        
        // Copy elements before index
        System.arraycopy(arr, 0, newArr, 0, index);
        
        // Copy elements after index
        System.arraycopy(arr, index + 1, newArr, index, arr.length - index - 1);
        
        return newArr;
    }
    
    /**
     * Search for value: O(n) linear search
     */
    public int linearSearch(int[] arr, int target) {
        for (int i = 0; i < arr.length; i++) {
            if (arr[i] == target) {
                return i;
            }
        }
        return -1;
    }
    
    /**
     * Binary search (sorted array): O(log n)
     */
    public int binarySearch(int[] arr, int target) {
        int left = 0;
        int right = arr.length - 1;
        
        while (left <= right) {
            int mid = left + (right - left) / 2;  // Avoid overflow
            
            if (arr[mid] == target) {
                return mid;
            } else if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        
        return -1;
    }
    
    /**
     * Reverse array: O(n)
     */
    public void reverse(int[] arr) {
        int left = 0;
        int right = arr.length - 1;
        
        while (left < right) {
            // Swap
            int temp = arr[left];
            arr[left] = arr[right];
            arr[right] = temp;
            
            left++;
            right--;
        }
    }
    
    /**
     * Rotate array right by k positions: O(n)
     * Example: [1,2,3,4,5] rotate 2 → [4,5,1,2,3]
     */
    public void rotateRight(int[] arr, int k) {
        int n = arr.length;
        k = k % n;  // Handle k > n
        
        if (k == 0) return;
        
        // Reverse entire array
        reverse(arr, 0, n - 1);
        
        // Reverse first k elements
        reverse(arr, 0, k - 1);
        
        // Reverse remaining elements
        reverse(arr, k, n - 1);
    }
    
    private void reverse(int[] arr, int start, int end) {
        while (start < end) {
            int temp = arr[start];
            arr[start] = arr[end];
            arr[end] = temp;
            start++;
            end--;
        }
    }
}
```

---

## Dynamic Arrays (ArrayList)

### Why Dynamic Arrays?
```
Problem: Static arrays have fixed size
Solution: Dynamic array that grows/shrinks automatically
```

### How ArrayList Works

```
1. Start with initial capacity (e.g., 10)
2. When full, create new array with 1.5× capacity
3. Copy all elements to new array
4. O(1) amortized insertion (occasional O(n) for resize)
```

### ArrayList Operations

```java
import java.util.ArrayList;
import java.util.List;

public class ArrayListExample {
    public static void main(String[] args) {
        // Create ArrayList
        List<Integer> list = new ArrayList<>();           // Initial capacity: 10
        List<Integer> list2 = new ArrayList<>(100);       // Initial capacity: 100
        List<Integer> list3 = new ArrayList<>(List.of(1, 2, 3));  // From collection
        
        // Add elements: O(1) amortized
        list.add(10);           // [10]
        list.add(20);           // [10, 20]
        list.add(1, 15);        // [10, 15, 20] - Insert at index (O(n))
        
        // Get element: O(1)
        int val = list.get(1);  // 15
        
        // Set element: O(1)
        list.set(1, 25);        // [10, 25, 20]
        
        // Remove element: O(n)
        list.remove(1);         // [10, 20] - Remove at index
        list.remove(Integer.valueOf(20));  // [10] - Remove by value
        
        // Size: O(1)
        int size = list.size(); // 1
        
        // Contains: O(n)
        boolean contains = list.contains(10);  // true
        
        // Index of: O(n)
        int index = list.indexOf(10);  // 0
        
        // Clear: O(n)
        list.clear();  // []
        
        // Is empty: O(1)
        boolean empty = list.isEmpty();  // true
    }
}
```

---

## Time & Space Complexity

### Static Array

| Operation | Time Complexity | Notes |
|-----------|-----------------|-------|
| **Access** | O(1) | Direct indexing |
| **Search** | O(n) | Linear search; O(log n) if sorted (binary search) |
| **Insert at end** | ❌ Not possible | Fixed size |
| **Insert at index** | ❌ Not possible | Fixed size |
| **Delete** | ❌ Not possible | Fixed size |

### ArrayList (Dynamic Array)

| Operation | Time Complexity | Amortized | Notes |
|-----------|-----------------|-----------|-------|
| **Access (get)** | O(1) | O(1) | Random access |
| **Set** | O(1) | O(1) | Update value |
| **Add at end** | O(n) | **O(1)** | Resize if full |
| **Add at index** | O(n) | O(n) | Shift elements |
| **Remove at end** | O(1) | O(1) | No shifting |
| **Remove at index** | O(n) | O(n) | Shift elements |
| **Search** | O(n) | O(n) | Linear search |
| **Contains** | O(n) | O(n) | Linear search |

**Space Complexity**: O(n) for n elements

---

## Custom Implementation from Scratch

```java
/**
 * Production-Grade Dynamic Array Implementation
 * Mimics ArrayList behavior
 */
public class DynamicArray<T> {
    
    private static final int DEFAULT_CAPACITY = 10;
    private static final double GROWTH_FACTOR = 1.5;
    
    private Object[] data;
    private int size;
    private int capacity;
    
    public DynamicArray() {
        this(DEFAULT_CAPACITY);
    }
    
    public DynamicArray(int initialCapacity) {
        if (initialCapacity < 0) {
            throw new IllegalArgumentException("Illegal capacity: " + initialCapacity);
        }
        this.capacity = initialCapacity;
        this.data = new Object[capacity];
        this.size = 0;
    }
    
    /**
     * Add element at end: O(1) amortized
     */
    public void add(T element) {
        ensureCapacity();
        data[size++] = element;
    }
    
    /**
     * Add element at index: O(n)
     */
    public void add(int index, T element) {
        checkIndexForAdd(index);
        ensureCapacity();
        
        // Shift elements to the right
        System.arraycopy(data, index, data, index + 1, size - index);
        
        data[index] = element;
        size++;
    }
    
    /**
     * Get element: O(1)
     */
    @SuppressWarnings("unchecked")
    public T get(int index) {
        checkIndex(index);
        return (T) data[index];
    }
    
    /**
     * Set element: O(1)
     */
    public T set(int index, T element) {
        checkIndex(index);
        
        @SuppressWarnings("unchecked")
        T oldValue = (T) data[index];
        data[index] = element;
        return oldValue;
    }
    
    /**
     * Remove element at index: O(n)
     */
    @SuppressWarnings("unchecked")
    public T remove(int index) {
        checkIndex(index);
        
        T oldValue = (T) data[index];
        
        // Shift elements to the left
        int numMoved = size - index - 1;
        if (numMoved > 0) {
            System.arraycopy(data, index + 1, data, index, numMoved);
        }
        
        data[--size] = null;  // Help GC
        
        return oldValue;
    }
    
    /**
     * Remove first occurrence of element: O(n)
     */
    public boolean remove(T element) {
        int index = indexOf(element);
        if (index >= 0) {
            remove(index);
            return true;
        }
        return false;
    }
    
    /**
     * Find index of element: O(n)
     */
    public int indexOf(T element) {
        if (element == null) {
            for (int i = 0; i < size; i++) {
                if (data[i] == null) {
                    return i;
                }
            }
        } else {
            for (int i = 0; i < size; i++) {
                if (element.equals(data[i])) {
                    return i;
                }
            }
        }
        return -1;
    }
    
    /**
     * Check if contains element: O(n)
     */
    public boolean contains(T element) {
        return indexOf(element) >= 0;
    }
    
    /**
     * Get size: O(1)
     */
    public int size() {
        return size;
    }
    
    /**
     * Check if empty: O(1)
     */
    public boolean isEmpty() {
        return size == 0;
    }
    
    /**
     * Clear all elements: O(n)
     */
    public void clear() {
        for (int i = 0; i < size; i++) {
            data[i] = null;  // Help GC
        }
        size = 0;
    }
    
    /**
     * Ensure capacity for growth
     */
    private void ensureCapacity() {
        if (size == capacity) {
            int newCapacity = (int) (capacity * GROWTH_FACTOR);
            if (newCapacity == capacity) {
                newCapacity = capacity + 1;
            }
            resize(newCapacity);
        }
    }
    
    /**
     * Resize internal array
     */
    private void resize(int newCapacity) {
        Object[] newData = new Object[newCapacity];
        System.arraycopy(data, 0, newData, 0, size);
        data = newData;
        capacity = newCapacity;
        System.out.println("Resized to capacity: " + newCapacity);
    }
    
    /**
     * Trim to size (reduce capacity to match size)
     */
    public void trimToSize() {
        if (size < capacity) {
            Object[] newData = new Object[size];
            System.arraycopy(data, 0, newData, 0, size);
            data = newData;
            capacity = size;
        }
    }
    
    /**
     * Validate index for access
     */
    private void checkIndex(int index) {
        if (index < 0 || index >= size) {
            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
        }
    }
    
    /**
     * Validate index for add operation
     */
    private void checkIndexForAdd(int index) {
        if (index < 0 || index > size) {
            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
        }
    }
    
    /**
     * Convert to array
     */
    @SuppressWarnings("unchecked")
    public T[] toArray() {
        Object[] arr = new Object[size];
        System.arraycopy(data, 0, arr, 0, size);
        return (T[]) arr;
    }
    
    @Override
    public String toString() {
        if (size == 0) {
            return "[]";
        }
        
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < size; i++) {
            sb.append(data[i]);
            if (i < size - 1) {
                sb.append(", ");
            }
        }
        sb.append("]");
        return sb.toString();
    }
}

// Usage
public class Main {
    public static void main(String[] args) {
        DynamicArray<Integer> arr = new DynamicArray<>(3);
        
        // Add elements (will trigger resize)
        arr.add(10);
        arr.add(20);
        arr.add(30);
        arr.add(40);  // Triggers resize to capacity 4
        arr.add(50);  // Triggers resize to capacity 6
        
        System.out.println("Array: " + arr);  // [10, 20, 30, 40, 50]
        System.out.println("Size: " + arr.size());  // 5
        
        // Insert at index
        arr.add(2, 25);
        System.out.println("After insert: " + arr);  // [10, 20, 25, 30, 40, 50]
        
        // Remove
        arr.remove(3);
        System.out.println("After remove: " + arr);  // [10, 20, 25, 40, 50]
        
        // Get
        System.out.println("Get index 2: " + arr.get(2));  // 25
        
        // Set
        arr.set(2, 35);
        System.out.println("After set: " + arr);  // [10, 20, 35, 40, 50]
        
        // Contains
        System.out.println("Contains 40: " + arr.contains(40));  // true
        System.out.println("Contains 100: " + arr.contains(100));  // false
        
        // Index of
        System.out.println("Index of 40: " + arr.indexOf(40));  // 3
    }
}
```

---

## Interview Problems

### Problem 1: Remove Duplicates from Sorted Array (LeetCode 26)

```java
/**
 * Given sorted array, remove duplicates in-place
 * Return new length
 * 
 * Example: [1,1,2,2,3] → [1,2,3,_,_], return 3
 * 
 * Time: O(n), Space: O(1)
 */
public int removeDuplicates(int[] nums) {
    if (nums.length == 0) return 0;
    
    int writeIndex = 1;  // Position to write next unique element
    
    for (int readIndex = 1; readIndex < nums.length; readIndex++) {
        if (nums[readIndex] != nums[readIndex - 1]) {
            nums[writeIndex] = nums[readIndex];
            writeIndex++;
        }
    }
    
    return writeIndex;
}
```

### Problem 2: Move Zeroes (LeetCode 283)

```java
/**
 * Move all zeroes to end, maintain relative order
 * 
 * Example: [0,1,0,3,12] → [1,3,12,0,0]
 * 
 * Time: O(n), Space: O(1)
 */
public void moveZeroes(int[] nums) {
    int writeIndex = 0;  // Position to write next non-zero
    
    // Move all non-zero elements to front
    for (int readIndex = 0; readIndex < nums.length; readIndex++) {
        if (nums[readIndex] != 0) {
            nums[writeIndex] = nums[readIndex];
            writeIndex++;
        }
    }
    
    // Fill remaining positions with zeros
    while (writeIndex < nums.length) {
        nums[writeIndex] = 0;
        writeIndex++;
    }
}

// Optimized: Swap instead of overwrite
public void moveZeroesOptimized(int[] nums) {
    int writeIndex = 0;
    
    for (int readIndex = 0; readIndex < nums.length; readIndex++) {
        if (nums[readIndex] != 0) {
            // Swap
            int temp = nums[writeIndex];
            nums[writeIndex] = nums[readIndex];
            nums[readIndex] = temp;
            writeIndex++;
        }
    }
}
```

### Problem 3: Two Sum (LeetCode 1)

```java
/**
 * Find two numbers that add up to target
 * Return indices
 * 
 * Example: nums = [2,7,11,15], target = 9 → [0,1]
 * 
 * Time: O(n), Space: O(n)
 */
public int[] twoSum(int[] nums, int target) {
    Map<Integer, Integer> map = new HashMap<>();  // value → index
    
    for (int i = 0; i < nums.length; i++) {
        int complement = target - nums[i];
        
        if (map.containsKey(complement)) {
            return new int[]{map.get(complement), i};
        }
        
        map.put(nums[i], i);
    }
    
    throw new IllegalArgumentException("No solution");
}
```

### Problem 4: Product of Array Except Self (LeetCode 238)

```java
/**
 * Return array where output[i] = product of all elements except nums[i]
 * Cannot use division, must be O(n)
 * 
 * Example: [1,2,3,4] → [24,12,8,6]
 * 
 * Time: O(n), Space: O(1) excluding output array
 */
public int[] productExceptSelf(int[] nums) {
    int n = nums.length;
    int[] output = new int[n];
    
    // Left products: output[i] = product of all elements to left of i
    output[0] = 1;
    for (int i = 1; i < n; i++) {
        output[i] = output[i - 1] * nums[i - 1];
    }
    
    // Right products: multiply by product of all elements to right of i
    int rightProduct = 1;
    for (int i = n - 1; i >= 0; i--) {
        output[i] *= rightProduct;
        rightProduct *= nums[i];
    }
    
    return output;
}
```

---

## Advanced Techniques

### 1. Two Pointers

```java
/**
 * Reverse string (character array)
 */
public void reverseString(char[] s) {
    int left = 0;
    int right = s.length - 1;
    
    while (left < right) {
        char temp = s[left];
        s[left] = s[right];
        s[right] = temp;
        left++;
        right--;
    }
}
```

### 2. Sliding Window

```java
/**
 * Maximum sum of k consecutive elements
 * 
 * Time: O(n), Space: O(1)
 */
public int maxSumSubarray(int[] arr, int k) {
    if (arr.length < k) {
        throw new IllegalArgumentException("Array size < k");
    }
    
    // Calculate sum of first window
    int windowSum = 0;
    for (int i = 0; i < k; i++) {
        windowSum += arr[i];
    }
    
    int maxSum = windowSum;
    
    // Slide window
    for (int i = k; i < arr.length; i++) {
        windowSum = windowSum - arr[i - k] + arr[i];
        maxSum = Math.max(maxSum, windowSum);
    }
    
    return maxSum;
}
```

### 3. Prefix Sum

```java
/**
 * Range sum queries in O(1)
 * 
 * Preprocess: O(n), Query: O(1), Space: O(n)
 */
public class RangeSumQuery {
    private int[] prefixSum;
    
    public RangeSumQuery(int[] nums) {
        int n = nums.length;
        prefixSum = new int[n + 1];
        
        // prefixSum[i] = sum of nums[0..i-1]
        for (int i = 0; i < n; i++) {
            prefixSum[i + 1] = prefixSum[i] + nums[i];
        }
    }
    
    /**
     * Sum of elements from index left to right (inclusive)
     */
    public int sumRange(int left, int right) {
        return prefixSum[right + 1] - prefixSum[left];
    }
}

// Usage
RangeSumQuery rsq = new RangeSumQuery(new int[]{1, 2, 3, 4, 5});
System.out.println(rsq.sumRange(1, 3));  // 2+3+4 = 9
```

---

## 🎯 Interview Tips

### When to Use Arrays
- ✅ Need fast random access (O(1))
- ✅ Know size in advance or bounded size
- ✅ Memory-efficient (no overhead)
- ✅ Cache-friendly (contiguous memory)

### When NOT to Use Arrays
- ❌ Frequent insertions/deletions (O(n))
- ❌ Unknown/unbounded size (use ArrayList)
- ❌ Need fast search without sorting (use HashSet)

### Common Pitfalls
```java
// ❌ BAD: Incorrect mid calculation (overflow)
int mid = (left + right) / 2;

// ✅ GOOD: Prevent overflow
int mid = left + (right - left) / 2;

// ❌ BAD: Modifying array while iterating
for (int num : arr) {
    if (num == 0) {
        arr.remove(num);  // ConcurrentModificationException
    }
}

// ✅ GOOD: Use iterator or reverse iteration
for (int i = arr.size() - 1; i >= 0; i--) {
    if (arr.get(i) == 0) {
        arr.remove(i);
    }
}
```

---

**Next:** [LinkedList.md](./02-LinkedList.md) — Singly, Doubly, Circular linked lists
