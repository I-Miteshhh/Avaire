# Deque and PriorityQueue

**Difficulty:** Intermediate  
**Learning Time:** 1-2 weeks  
**Interview Frequency:** ⭐⭐⭐⭐ (High)

---

## 📚 Table of Contents

1. [Deque (Double-Ended Queue)](#deque-double-ended-queue)
2. [PriorityQueue (Heap)](#priorityqueue-heap)
3. [Custom Implementations](#custom-implementations)
4. [Interview Problems](#interview-problems)
5. [Real-World Use Cases](#real-world-use-cases)

---

## Deque (Double-Ended Queue)

### Characteristics

```
✅ Insert/delete from both ends: O(1)
✅ Can be used as Stack or Queue
✅ More flexible than Stack/Queue
❌ More complex than simple Stack/Queue
```

### Java Deque API

```java
Deque<Integer> deque = new ArrayDeque<>();

// Add elements
deque.addFirst(10);      // Add to front
deque.addLast(20);       // Add to rear
deque.offerFirst(30);    // Add to front (returns false if full)
deque.offerLast(40);     // Add to rear

// Remove elements
int first = deque.removeFirst();  // Remove from front
int last = deque.removeLast();    // Remove from rear
int pollFirst = deque.pollFirst(); // Remove from front (returns null if empty)
int pollLast = deque.pollLast();   // Remove from rear

// Peek elements
int peekFirst = deque.peekFirst(); // View front
int peekLast = deque.peekLast();   // View rear

// Size
int size = deque.size();
boolean isEmpty = deque.isEmpty();
```

### Use as Stack

```java
Deque<Integer> stack = new ArrayDeque<>();
stack.push(10);         // addFirst()
stack.push(20);
int top = stack.pop();  // removeFirst()
int peek = stack.peek(); // peekFirst()
```

### Use as Queue

```java
Deque<Integer> queue = new ArrayDeque<>();
queue.offer(10);          // addLast()
queue.offer(20);
int front = queue.poll(); // removeFirst()
int peek = queue.peek();  // peekFirst()
```

---

## Custom Deque Implementation

```java
/**
 * Doubly Linked List-based Deque
 * 
 * Time: O(1) for all operations
 * Space: O(n)
 */
public class LinkedDeque<T> {
    
    private static class Node<T> {
        T data;
        Node<T> prev;
        Node<T> next;
        
        Node(T data) {
            this.data = data;
        }
    }
    
    private Node<T> head;
    private Node<T> tail;
    private int size;
    
    public LinkedDeque() {
        this.head = null;
        this.tail = null;
        this.size = 0;
    }
    
    /**
     * Add at front: O(1)
     */
    public void addFirst(T element) {
        Node<T> newNode = new Node<>(element);
        
        if (head == null) {
            head = tail = newNode;
        } else {
            newNode.next = head;
            head.prev = newNode;
            head = newNode;
        }
        
        size++;
    }
    
    /**
     * Add at rear: O(1)
     */
    public void addLast(T element) {
        Node<T> newNode = new Node<>(element);
        
        if (tail == null) {
            head = tail = newNode;
        } else {
            newNode.prev = tail;
            tail.next = newNode;
            tail = newNode;
        }
        
        size++;
    }
    
    /**
     * Remove from front: O(1)
     */
    public T removeFirst() {
        if (head == null) {
            throw new NoSuchElementException("Deque is empty");
        }
        
        T data = head.data;
        head = head.next;
        
        if (head == null) {
            tail = null;
        } else {
            head.prev = null;
        }
        
        size--;
        return data;
    }
    
    /**
     * Remove from rear: O(1)
     */
    public T removeLast() {
        if (tail == null) {
            throw new NoSuchElementException("Deque is empty");
        }
        
        T data = tail.data;
        tail = tail.prev;
        
        if (tail == null) {
            head = null;
        } else {
            tail.next = null;
        }
        
        size--;
        return data;
    }
    
    /**
     * Peek at front: O(1)
     */
    public T peekFirst() {
        if (head == null) {
            throw new NoSuchElementException("Deque is empty");
        }
        return head.data;
    }
    
    /**
     * Peek at rear: O(1)
     */
    public T peekLast() {
        if (tail == null) {
            throw new NoSuchElementException("Deque is empty");
        }
        return tail.data;
    }
    
    public int size() {
        return size;
    }
    
    public boolean isEmpty() {
        return size == 0;
    }
}
```

---

## PriorityQueue (Heap)

### Characteristics

```
✅ Elements ordered by priority (not insertion order)
✅ O(log n) insert, O(log n) remove
✅ O(1) peek at highest priority
✅ Great for top-k problems, job scheduling
❌ Not thread-safe
❌ No random access
```

### Java PriorityQueue API

```java
// Min Heap (default)
PriorityQueue<Integer> minHeap = new PriorityQueue<>();

// Max Heap (custom comparator)
PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Collections.reverseOrder());
// OR
PriorityQueue<Integer> maxHeap = new PriorityQueue<>((a, b) -> b - a);

// Basic operations
minHeap.offer(10);           // Add: O(log n)
minHeap.add(20);             // Same as offer
int min = minHeap.poll();    // Remove min: O(log n)
int peek = minHeap.peek();   // View min: O(1)
int size = minHeap.size();   // O(1)
boolean isEmpty = minHeap.isEmpty();

// Custom objects
PriorityQueue<Task> taskQueue = new PriorityQueue<>(
    (t1, t2) -> t1.priority - t2.priority
);
```

---

## Custom PriorityQueue (Binary Heap)

```java
/**
 * Min Heap implementation
 * 
 * Time: O(log n) insert, O(log n) remove, O(1) peek
 * Space: O(n)
 */
public class MinHeap {
    
    private int[] heap;
    private int size;
    private int capacity;
    
    public MinHeap(int capacity) {
        this.capacity = capacity;
        this.heap = new int[capacity];
        this.size = 0;
    }
    
    /**
     * Insert element: O(log n)
     */
    public void insert(int value) {
        if (size == capacity) {
            throw new IllegalStateException("Heap is full");
        }
        
        heap[size] = value;
        heapifyUp(size);
        size++;
    }
    
    /**
     * Remove minimum: O(log n)
     */
    public int extractMin() {
        if (size == 0) {
            throw new NoSuchElementException("Heap is empty");
        }
        
        int min = heap[0];
        heap[0] = heap[size - 1];
        size--;
        heapifyDown(0);
        
        return min;
    }
    
    /**
     * Peek minimum: O(1)
     */
    public int peek() {
        if (size == 0) {
            throw new NoSuchElementException("Heap is empty");
        }
        return heap[0];
    }
    
    /**
     * Heapify up (bubble up): O(log n)
     */
    private void heapifyUp(int index) {
        while (index > 0) {
            int parent = (index - 1) / 2;
            
            if (heap[index] >= heap[parent]) {
                break;
            }
            
            swap(index, parent);
            index = parent;
        }
    }
    
    /**
     * Heapify down (bubble down): O(log n)
     */
    private void heapifyDown(int index) {
        while (true) {
            int left = 2 * index + 1;
            int right = 2 * index + 2;
            int smallest = index;
            
            if (left < size && heap[left] < heap[smallest]) {
                smallest = left;
            }
            
            if (right < size && heap[right] < heap[smallest]) {
                smallest = right;
            }
            
            if (smallest == index) {
                break;
            }
            
            swap(index, smallest);
            index = smallest;
        }
    }
    
    private void swap(int i, int j) {
        int temp = heap[i];
        heap[i] = heap[j];
        heap[j] = temp;
    }
    
    public int size() {
        return size;
    }
    
    public boolean isEmpty() {
        return size == 0;
    }
}
```

### Generic Min Heap with Comparator

```java
/**
 * Generic Min Heap
 */
public class GenericMinHeap<T> {
    
    private Object[] heap;
    private int size;
    private int capacity;
    private Comparator<? super T> comparator;
    
    @SuppressWarnings("unchecked")
    public GenericMinHeap(int capacity, Comparator<? super T> comparator) {
        this.capacity = capacity;
        this.heap = new Object[capacity];
        this.size = 0;
        this.comparator = comparator;
    }
    
    public void insert(T value) {
        if (size == capacity) {
            resize();
        }
        
        heap[size] = value;
        heapifyUp(size);
        size++;
    }
    
    @SuppressWarnings("unchecked")
    public T extractMin() {
        if (size == 0) {
            throw new NoSuchElementException("Heap is empty");
        }
        
        T min = (T) heap[0];
        heap[0] = heap[size - 1];
        heap[size - 1] = null;
        size--;
        
        if (size > 0) {
            heapifyDown(0);
        }
        
        return min;
    }
    
    @SuppressWarnings("unchecked")
    public T peek() {
        if (size == 0) {
            throw new NoSuchElementException("Heap is empty");
        }
        return (T) heap[0];
    }
    
    @SuppressWarnings("unchecked")
    private void heapifyUp(int index) {
        while (index > 0) {
            int parent = (index - 1) / 2;
            
            if (comparator.compare((T) heap[index], (T) heap[parent]) >= 0) {
                break;
            }
            
            swap(index, parent);
            index = parent;
        }
    }
    
    @SuppressWarnings("unchecked")
    private void heapifyDown(int index) {
        while (true) {
            int left = 2 * index + 1;
            int right = 2 * index + 2;
            int smallest = index;
            
            if (left < size && comparator.compare((T) heap[left], (T) heap[smallest]) < 0) {
                smallest = left;
            }
            
            if (right < size && comparator.compare((T) heap[right], (T) heap[smallest]) < 0) {
                smallest = right;
            }
            
            if (smallest == index) {
                break;
            }
            
            swap(index, smallest);
            index = smallest;
        }
    }
    
    private void swap(int i, int j) {
        Object temp = heap[i];
        heap[i] = heap[j];
        heap[j] = temp;
    }
    
    private void resize() {
        capacity = (int) (capacity * 1.5);
        heap = Arrays.copyOf(heap, capacity);
    }
    
    public int size() {
        return size;
    }
    
    public boolean isEmpty() {
        return size == 0;
    }
}
```

---

## Interview Problems

### Problem 1: Sliding Window Maximum (LeetCode 239)

```java
/**
 * Find maximum in each sliding window using Deque
 * 
 * Example: nums=[1,3,-1,-3,5,3,6,7], k=3 → [3,3,5,5,6,7]
 * 
 * Time: O(n), Space: O(k)
 */
public int[] maxSlidingWindow(int[] nums, int k) {
    if (nums == null || nums.length == 0) {
        return new int[0];
    }
    
    int n = nums.length;
    int[] result = new int[n - k + 1];
    Deque<Integer> deque = new ArrayDeque<>();  // Store indices
    
    for (int i = 0; i < n; i++) {
        // Remove indices outside window
        while (!deque.isEmpty() && deque.peekFirst() < i - k + 1) {
            deque.pollFirst();
        }
        
        // Maintain decreasing order (remove smaller elements)
        while (!deque.isEmpty() && nums[deque.peekLast()] < nums[i]) {
            deque.pollLast();
        }
        
        deque.offerLast(i);
        
        // Add to result once window size reached
        if (i >= k - 1) {
            result[i - k + 1] = nums[deque.peekFirst()];
        }
    }
    
    return result;
}
```

### Problem 2: K Closest Points to Origin (LeetCode 973)

```java
/**
 * Find k closest points to origin using Max Heap
 * 
 * Time: O(n log k), Space: O(k)
 */
public int[][] kClosest(int[][] points, int k) {
    // Max heap based on distance
    PriorityQueue<int[]> maxHeap = new PriorityQueue<>(
        (a, b) -> {
            int distA = a[0] * a[0] + a[1] * a[1];
            int distB = b[0] * b[0] + b[1] * b[1];
            return distB - distA;  // Max heap
        }
    );
    
    for (int[] point : points) {
        maxHeap.offer(point);
        
        if (maxHeap.size() > k) {
            maxHeap.poll();  // Remove farthest
        }
    }
    
    int[][] result = new int[k][2];
    for (int i = 0; i < k; i++) {
        result[i] = maxHeap.poll();
    }
    
    return result;
}
```

### Problem 3: Merge K Sorted Lists (LeetCode 23)

```java
/**
 * Merge k sorted linked lists using Min Heap
 * 
 * Time: O(n log k) where n = total nodes
 * Space: O(k)
 */
public ListNode mergeKLists(ListNode[] lists) {
    if (lists == null || lists.length == 0) {
        return null;
    }
    
    // Min heap based on node value
    PriorityQueue<ListNode> minHeap = new PriorityQueue<>(
        (a, b) -> a.val - b.val
    );
    
    // Add first node of each list
    for (ListNode head : lists) {
        if (head != null) {
            minHeap.offer(head);
        }
    }
    
    ListNode dummy = new ListNode(0);
    ListNode current = dummy;
    
    while (!minHeap.isEmpty()) {
        ListNode node = minHeap.poll();
        current.next = node;
        current = current.next;
        
        if (node.next != null) {
            minHeap.offer(node.next);
        }
    }
    
    return dummy.next;
}
```

### Problem 4: Top K Frequent Elements (LeetCode 347)

```java
/**
 * Find k most frequent elements
 * 
 * Time: O(n log k), Space: O(n)
 */
public int[] topKFrequent(int[] nums, int k) {
    // Count frequencies
    Map<Integer, Integer> freqMap = new HashMap<>();
    for (int num : nums) {
        freqMap.put(num, freqMap.getOrDefault(num, 0) + 1);
    }
    
    // Min heap based on frequency
    PriorityQueue<Map.Entry<Integer, Integer>> minHeap = new PriorityQueue<>(
        (a, b) -> a.getValue() - b.getValue()
    );
    
    for (Map.Entry<Integer, Integer> entry : freqMap.entrySet()) {
        minHeap.offer(entry);
        
        if (minHeap.size() > k) {
            minHeap.poll();
        }
    }
    
    int[] result = new int[k];
    int i = 0;
    while (!minHeap.isEmpty()) {
        result[i++] = minHeap.poll().getKey();
    }
    
    return result;
}

// Alternative: Bucket Sort - O(n) time
public int[] topKFrequentBucketSort(int[] nums, int k) {
    // Count frequencies
    Map<Integer, Integer> freqMap = new HashMap<>();
    for (int num : nums) {
        freqMap.put(num, freqMap.getOrDefault(num, 0) + 1);
    }
    
    // Bucket sort by frequency
    List<Integer>[] buckets = new List[nums.length + 1];
    for (int i = 0; i < buckets.length; i++) {
        buckets[i] = new ArrayList<>();
    }
    
    for (Map.Entry<Integer, Integer> entry : freqMap.entrySet()) {
        int freq = entry.getValue();
        buckets[freq].add(entry.getKey());
    }
    
    // Collect top k
    int[] result = new int[k];
    int index = 0;
    
    for (int i = buckets.length - 1; i >= 0 && index < k; i--) {
        for (int num : buckets[i]) {
            result[index++] = num;
            if (index == k) break;
        }
    }
    
    return result;
}
```

### Problem 5: Find Median from Data Stream (LeetCode 295)

```java
/**
 * Maintain running median using two heaps
 * 
 * Time: O(log n) addNum, O(1) findMedian
 * Space: O(n)
 */
class MedianFinder {
    
    private PriorityQueue<Integer> maxHeap;  // Lower half
    private PriorityQueue<Integer> minHeap;  // Upper half
    
    public MedianFinder() {
        maxHeap = new PriorityQueue<>(Collections.reverseOrder());
        minHeap = new PriorityQueue<>();
    }
    
    /**
     * Add number: O(log n)
     */
    public void addNum(int num) {
        if (maxHeap.isEmpty() || num <= maxHeap.peek()) {
            maxHeap.offer(num);
        } else {
            minHeap.offer(num);
        }
        
        // Balance heaps (size difference at most 1)
        if (maxHeap.size() > minHeap.size() + 1) {
            minHeap.offer(maxHeap.poll());
        } else if (minHeap.size() > maxHeap.size()) {
            maxHeap.offer(minHeap.poll());
        }
    }
    
    /**
     * Find median: O(1)
     */
    public double findMedian() {
        if (maxHeap.size() == minHeap.size()) {
            return (maxHeap.peek() + minHeap.peek()) / 2.0;
        } else {
            return maxHeap.peek();
        }
    }
}
```

### Problem 6: Task Scheduler (LeetCode 621)

```java
/**
 * Schedule tasks with cooldown using priority queue
 * 
 * Example: tasks=['A','A','A','B','B','B'], n=2 → 8
 * 
 * Time: O(n log 26), Space: O(26)
 */
public int leastInterval(char[] tasks, int n) {
    // Count task frequencies
    int[] freq = new int[26];
    for (char task : tasks) {
        freq[task - 'A']++;
    }
    
    // Max heap of frequencies
    PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Collections.reverseOrder());
    for (int f : freq) {
        if (f > 0) {
            maxHeap.offer(f);
        }
    }
    
    int time = 0;
    
    while (!maxHeap.isEmpty()) {
        List<Integer> temp = new ArrayList<>();
        
        // Execute n+1 tasks (or fewer if not available)
        for (int i = 0; i <= n; i++) {
            if (!maxHeap.isEmpty()) {
                int f = maxHeap.poll();
                if (f > 1) {
                    temp.add(f - 1);
                }
            }
        }
        
        // Add back remaining tasks
        for (int f : temp) {
            maxHeap.offer(f);
        }
        
        // Add time
        if (maxHeap.isEmpty()) {
            time += temp.size() + 1;
        } else {
            time += n + 1;
        }
    }
    
    return time;
}
```

### Problem 7: Kth Largest Element in Array (LeetCode 215)

```java
/**
 * Find kth largest element using Min Heap
 * 
 * Time: O(n log k), Space: O(k)
 */
public int findKthLargest(int[] nums, int k) {
    // Min heap of size k
    PriorityQueue<Integer> minHeap = new PriorityQueue<>();
    
    for (int num : nums) {
        minHeap.offer(num);
        
        if (minHeap.size() > k) {
            minHeap.poll();
        }
    }
    
    return minHeap.peek();
}

// Alternative: QuickSelect - Average O(n), Worst O(n²)
public int findKthLargestQuickSelect(int[] nums, int k) {
    return quickSelect(nums, 0, nums.length - 1, nums.length - k);
}

private int quickSelect(int[] nums, int left, int right, int kSmallest) {
    if (left == right) {
        return nums[left];
    }
    
    int pivotIndex = partition(nums, left, right);
    
    if (kSmallest == pivotIndex) {
        return nums[kSmallest];
    } else if (kSmallest < pivotIndex) {
        return quickSelect(nums, left, pivotIndex - 1, kSmallest);
    } else {
        return quickSelect(nums, pivotIndex + 1, right, kSmallest);
    }
}

private int partition(int[] nums, int left, int right) {
    int pivot = nums[right];
    int i = left;
    
    for (int j = left; j < right; j++) {
        if (nums[j] < pivot) {
            swap(nums, i, j);
            i++;
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
```

---

## Real-World Use Cases

### 1. Job Scheduling with Priority

```java
/**
 * Priority-based task scheduler
 */
class Task {
    String name;
    int priority;
    long createdAt;
    
    Task(String name, int priority) {
        this.name = name;
        this.priority = priority;
        this.createdAt = System.currentTimeMillis();
    }
}

class TaskScheduler {
    
    private PriorityQueue<Task> taskQueue;
    
    public TaskScheduler() {
        // Higher priority first, then earlier creation time
        taskQueue = new PriorityQueue<>((t1, t2) -> {
            if (t1.priority != t2.priority) {
                return t2.priority - t1.priority;  // Higher priority first
            }
            return Long.compare(t1.createdAt, t2.createdAt);  // Earlier first
        });
    }
    
    public void addTask(Task task) {
        taskQueue.offer(task);
    }
    
    public Task getNextTask() {
        return taskQueue.poll();
    }
    
    public boolean hasTasks() {
        return !taskQueue.isEmpty();
    }
}
```

### 2. Kafka-like Message Queue with Deque

```java
/**
 * Message buffer with deque for priority messages
 */
class MessageQueue {
    
    private Deque<Message> queue;
    
    public MessageQueue() {
        queue = new ArrayDeque<>();
    }
    
    public void sendMessage(Message msg) {
        if (msg.isPriority()) {
            queue.addFirst(msg);  // Priority messages at front
        } else {
            queue.addLast(msg);   // Regular messages at rear
        }
    }
    
    public Message receiveMessage() {
        return queue.pollFirst();
    }
    
    public int getPendingCount() {
        return queue.size();
    }
}

class Message {
    String content;
    boolean priority;
    
    Message(String content, boolean priority) {
        this.content = content;
        this.priority = priority;
    }
    
    boolean isPriority() {
        return priority;
    }
}
```

### 3. Top-K Trending Topics (Data Streaming)

```java
/**
 * Track top-k trending topics in real-time
 */
class TrendingTopics {
    
    private Map<String, Integer> topicCount;
    private PriorityQueue<Map.Entry<String, Integer>> topK;
    private int k;
    
    public TrendingTopics(int k) {
        this.k = k;
        this.topicCount = new HashMap<>();
        this.topK = new PriorityQueue<>(
            (a, b) -> a.getValue() - b.getValue()  // Min heap
        );
    }
    
    public void addTopic(String topic) {
        topicCount.put(topic, topicCount.getOrDefault(topic, 0) + 1);
        updateTopK();
    }
    
    private void updateTopK() {
        topK.clear();
        
        for (Map.Entry<String, Integer> entry : topicCount.entrySet()) {
            topK.offer(entry);
            
            if (topK.size() > k) {
                topK.poll();
            }
        }
    }
    
    public List<String> getTopKTopics() {
        return topK.stream()
            .sorted((a, b) -> b.getValue() - a.getValue())
            .map(Map.Entry::getKey)
            .collect(Collectors.toList());
    }
}
```

---

## 🎯 Interview Tips

### Deque vs Queue vs Stack

**Use Deque when:**
- ✅ Need both stack and queue operations
- ✅ Sliding window problems
- ✅ Palindrome checking
- ✅ Browser history (back/forward)

**Use PriorityQueue when:**
- ✅ Need top-k elements
- ✅ Job scheduling with priorities
- ✅ Merge k sorted lists/arrays
- ✅ Median from data stream (two heaps)
- ✅ Dijkstra's shortest path

### Heap Patterns

1. **Top-K Elements**: Use min heap of size k
2. **Kth Largest**: Min heap of size k
3. **Kth Smallest**: Max heap of size k
4. **Median**: Two heaps (max heap for lower half, min heap for upper half)
5. **Merge K Sorted**: Min heap with first element of each list

### Complexity Summary

| Operation | Deque | PriorityQueue |
|-----------|-------|---------------|
| **Add Front/Rear** | O(1) | - |
| **Remove Front/Rear** | O(1) | - |
| **Insert** | - | O(log n) |
| **Remove Min/Max** | - | O(log n) |
| **Peek** | O(1) | O(1) |
| **Search** | O(n) | O(n) |
| **Space** | O(n) | O(n) |

---

**Next:** [HashMap and HashSet](./05-HashMap-and-HashSet.md) — Hash-based data structures
