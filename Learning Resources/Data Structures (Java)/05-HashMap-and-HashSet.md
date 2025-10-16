# HashMap and HashSet

**Difficulty:** Intermediate  
**Learning Time:** 2-3 weeks  
**Interview Frequency:** ⭐⭐⭐⭐⭐ (Extremely High - Most Important!)

---

## 📚 Table of Contents

1. [Hash Table Fundamentals](#hash-table-fundamentals)
2. [HashMap](#hashmap)
3. [HashSet](#hashset)
4. [Custom HashMap Implementation](#custom-hashmap-implementation)
5. [Collision Resolution](#collision-resolution)
6. [Interview Problems](#interview-problems)
7. [Thread-Safe Variants](#thread-safe-variants)
8. [Real-World Use Cases](#real-world-use-cases)

---

## Hash Table Fundamentals

### How Hash Tables Work

```
1. Hash Function: key → hash code → index
2. Collision Handling: Multiple keys map to same index
3. Load Factor: ratio of entries to buckets (triggers resize)
4. Rehashing: Create larger array, redistribute entries
```

### Hash Function Properties

```
✅ Deterministic: Same input → same output
✅ Uniform distribution: Minimize collisions
✅ Fast to compute
✅ Avalanche effect: Small input change → large output change
```

### Time Complexity

| Operation | Average | Worst Case |
|-----------|---------|------------|
| **Get** | O(1) | O(n) |
| **Put** | O(1) | O(n) |
| **Remove** | O(1) | O(n) |
| **Contains** | O(1) | O(n) |

**Note:** Worst case O(n) occurs when all keys hash to same bucket (rare with good hash function)

---

## HashMap

### Characteristics

```
✅ Key-value pairs
✅ O(1) average get/put/remove
✅ Allows one null key, multiple null values
✅ No ordering guarantees
❌ Not thread-safe
❌ Iteration order unpredictable
```

### Java HashMap API

```java
HashMap<String, Integer> map = new HashMap<>();

// Basic operations
map.put("apple", 10);           // Add/Update: O(1)
int value = map.get("apple");   // Get: O(1)
map.remove("apple");            // Remove: O(1)
boolean exists = map.containsKey("apple");    // O(1)
boolean hasValue = map.containsValue(10);     // O(n)

// Size
int size = map.size();
boolean isEmpty = map.isEmpty();

// Iteration
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    String key = entry.getKey();
    Integer value = entry.getValue();
}

for (String key : map.keySet()) {
    Integer value = map.get(key);
}

for (Integer value : map.values()) {
    // ...
}

// Java 8+ methods
map.putIfAbsent("banana", 20);
map.getOrDefault("orange", 0);
map.computeIfAbsent("grape", k -> k.length());
map.computeIfPresent("apple", (k, v) -> v + 1);
map.merge("apple", 1, Integer::sum);

// Replace
map.replace("apple", 15);
map.replace("apple", 10, 15);  // Only if current value is 10
```

### HashMap Internals (Java 8+)

```
1. Array of buckets (default 16)
2. Each bucket: LinkedList (converts to TreeMap if > 8 nodes)
3. Load factor: 0.75 (resize when 75% full)
4. Capacity: Always power of 2
5. Hash code: key.hashCode() → (h = hash) ^ (h >>> 16)
6. Index: hash & (capacity - 1)
```

---

## Custom HashMap Implementation

### Separate Chaining (LinkedList)

```java
/**
 * HashMap with separate chaining for collision resolution
 * 
 * Time: O(1) average, O(n) worst
 * Space: O(n)
 */
public class MyHashMap<K, V> {
    
    private static final int DEFAULT_CAPACITY = 16;
    private static final double LOAD_FACTOR = 0.75;
    
    private static class Entry<K, V> {
        K key;
        V value;
        Entry<K, V> next;
        
        Entry(K key, V value) {
            this.key = key;
            this.value = value;
        }
    }
    
    private Entry<K, V>[] table;
    private int size;
    private int capacity;
    
    @SuppressWarnings("unchecked")
    public MyHashMap() {
        this.capacity = DEFAULT_CAPACITY;
        this.table = new Entry[capacity];
        this.size = 0;
    }
    
    /**
     * Hash function
     */
    private int hash(K key) {
        if (key == null) {
            return 0;
        }
        
        int h = key.hashCode();
        return (h ^ (h >>> 16)) & (capacity - 1);
    }
    
    /**
     * Put: O(1) average
     */
    public V put(K key, V value) {
        if (size >= capacity * LOAD_FACTOR) {
            resize();
        }
        
        int index = hash(key);
        Entry<K, V> entry = table[index];
        
        // Check if key exists (update value)
        while (entry != null) {
            if (key == null ? entry.key == null : key.equals(entry.key)) {
                V oldValue = entry.value;
                entry.value = value;
                return oldValue;
            }
            entry = entry.next;
        }
        
        // Add new entry at head
        Entry<K, V> newEntry = new Entry<>(key, value);
        newEntry.next = table[index];
        table[index] = newEntry;
        size++;
        
        return null;
    }
    
    /**
     * Get: O(1) average
     */
    public V get(K key) {
        int index = hash(key);
        Entry<K, V> entry = table[index];
        
        while (entry != null) {
            if (key == null ? entry.key == null : key.equals(entry.key)) {
                return entry.value;
            }
            entry = entry.next;
        }
        
        return null;
    }
    
    /**
     * Remove: O(1) average
     */
    public V remove(K key) {
        int index = hash(key);
        Entry<K, V> entry = table[index];
        Entry<K, V> prev = null;
        
        while (entry != null) {
            if (key == null ? entry.key == null : key.equals(entry.key)) {
                if (prev == null) {
                    table[index] = entry.next;
                } else {
                    prev.next = entry.next;
                }
                size--;
                return entry.value;
            }
            prev = entry;
            entry = entry.next;
        }
        
        return null;
    }
    
    /**
     * Contains key: O(1) average
     */
    public boolean containsKey(K key) {
        return get(key) != null || (get(key) == null && hasNullValue(key));
    }
    
    private boolean hasNullValue(K key) {
        int index = hash(key);
        Entry<K, V> entry = table[index];
        
        while (entry != null) {
            if (key == null ? entry.key == null : key.equals(entry.key)) {
                return true;
            }
            entry = entry.next;
        }
        
        return false;
    }
    
    /**
     * Resize: O(n)
     */
    @SuppressWarnings("unchecked")
    private void resize() {
        int newCapacity = capacity * 2;
        Entry<K, V>[] oldTable = table;
        
        table = new Entry[newCapacity];
        capacity = newCapacity;
        size = 0;
        
        // Rehash all entries
        for (Entry<K, V> entry : oldTable) {
            while (entry != null) {
                put(entry.key, entry.value);
                entry = entry.next;
            }
        }
    }
    
    public int size() {
        return size;
    }
    
    public boolean isEmpty() {
        return size == 0;
    }
    
    public void clear() {
        table = new Entry[capacity];
        size = 0;
    }
}
```

### Open Addressing (Linear Probing)

```java
/**
 * HashMap with open addressing (linear probing)
 */
public class OpenAddressingHashMap<K, V> {
    
    private static final int DEFAULT_CAPACITY = 16;
    private static final double LOAD_FACTOR = 0.5;  // Lower for open addressing
    
    private static class Entry<K, V> {
        K key;
        V value;
        boolean deleted;  // For lazy deletion
        
        Entry(K key, V value) {
            this.key = key;
            this.value = value;
            this.deleted = false;
        }
    }
    
    private Entry<K, V>[] table;
    private int size;
    private int capacity;
    
    @SuppressWarnings("unchecked")
    public OpenAddressingHashMap() {
        this.capacity = DEFAULT_CAPACITY;
        this.table = new Entry[capacity];
        this.size = 0;
    }
    
    private int hash(K key) {
        if (key == null) {
            return 0;
        }
        return Math.abs(key.hashCode()) % capacity;
    }
    
    /**
     * Put with linear probing
     */
    public V put(K key, V value) {
        if (size >= capacity * LOAD_FACTOR) {
            resize();
        }
        
        int index = hash(key);
        int originalIndex = index;
        
        while (table[index] != null && !table[index].deleted) {
            if (key == null ? table[index].key == null : key.equals(table[index].key)) {
                V oldValue = table[index].value;
                table[index].value = value;
                return oldValue;
            }
            
            index = (index + 1) % capacity;  // Linear probing
            
            // Table full (shouldn't happen with load factor)
            if (index == originalIndex) {
                resize();
                return put(key, value);
            }
        }
        
        table[index] = new Entry<>(key, value);
        size++;
        return null;
    }
    
    /**
     * Get with linear probing
     */
    public V get(K key) {
        int index = hash(key);
        int originalIndex = index;
        
        while (table[index] != null) {
            if (!table[index].deleted && 
                (key == null ? table[index].key == null : key.equals(table[index].key))) {
                return table[index].value;
            }
            
            index = (index + 1) % capacity;
            
            if (index == originalIndex) {
                break;
            }
        }
        
        return null;
    }
    
    /**
     * Remove with lazy deletion
     */
    public V remove(K key) {
        int index = hash(key);
        int originalIndex = index;
        
        while (table[index] != null) {
            if (!table[index].deleted && 
                (key == null ? table[index].key == null : key.equals(table[index].key))) {
                V value = table[index].value;
                table[index].deleted = true;
                size--;
                return value;
            }
            
            index = (index + 1) % capacity;
            
            if (index == originalIndex) {
                break;
            }
        }
        
        return null;
    }
    
    @SuppressWarnings("unchecked")
    private void resize() {
        int newCapacity = capacity * 2;
        Entry<K, V>[] oldTable = table;
        
        table = new Entry[newCapacity];
        capacity = newCapacity;
        size = 0;
        
        for (Entry<K, V> entry : oldTable) {
            if (entry != null && !entry.deleted) {
                put(entry.key, entry.value);
            }
        }
    }
    
    public int size() {
        return size;
    }
}
```

---

## HashSet

### Characteristics

```
✅ Unique elements only
✅ O(1) add/remove/contains
✅ Backed by HashMap (values are dummy object)
✅ Allows one null element
❌ No ordering
❌ Not thread-safe
```

### Java HashSet API

```java
HashSet<String> set = new HashSet<>();

// Basic operations
set.add("apple");               // Add: O(1)
set.remove("apple");            // Remove: O(1)
boolean exists = set.contains("apple");  // O(1)

// Size
int size = set.size();
boolean isEmpty = set.isEmpty();

// Iteration
for (String item : set) {
    System.out.println(item);
}

// Set operations
HashSet<String> set1 = new HashSet<>(Arrays.asList("a", "b", "c"));
HashSet<String> set2 = new HashSet<>(Arrays.asList("b", "c", "d"));

// Union
HashSet<String> union = new HashSet<>(set1);
union.addAll(set2);  // {a, b, c, d}

// Intersection
HashSet<String> intersection = new HashSet<>(set1);
intersection.retainAll(set2);  // {b, c}

// Difference
HashSet<String> difference = new HashSet<>(set1);
difference.removeAll(set2);  // {a}
```

### Custom HashSet Implementation

```java
/**
 * HashSet backed by custom HashMap
 */
public class MyHashSet<E> {
    
    private static final Object PRESENT = new Object();
    
    private MyHashMap<E, Object> map;
    
    public MyHashSet() {
        map = new MyHashMap<>();
    }
    
    /**
     * Add: O(1) average
     */
    public boolean add(E element) {
        return map.put(element, PRESENT) == null;
    }
    
    /**
     * Remove: O(1) average
     */
    public boolean remove(E element) {
        return map.remove(element) == PRESENT;
    }
    
    /**
     * Contains: O(1) average
     */
    public boolean contains(E element) {
        return map.containsKey(element);
    }
    
    public int size() {
        return map.size();
    }
    
    public boolean isEmpty() {
        return map.isEmpty();
    }
    
    public void clear() {
        map.clear();
    }
}
```

---

## Collision Resolution Techniques

### 1. Separate Chaining (LinkedList)

```java
/**
 * Most common in Java HashMap
 * 
 * Pros:
 * - Simple to implement
 * - Load factor can exceed 1
 * - Deletion is easy
 * 
 * Cons:
 * - Extra memory for pointers
 * - Cache-unfriendly
 */
```

### 2. Open Addressing (Linear Probing)

```java
/**
 * All entries stored in array
 * 
 * Pros:
 * - Better cache locality
 * - No extra pointers
 * 
 * Cons:
 * - Primary clustering (consecutive occupied slots)
 * - Load factor must be < 1
 * - Deletion complex (lazy deletion)
 */

// Linear Probing
index = (hash + i) % capacity

// Quadratic Probing
index = (hash + i²) % capacity

// Double Hashing
index = (hash1 + i * hash2) % capacity
```

---

## Interview Problems

### Problem 1: Two Sum (LeetCode 1)

```java
/**
 * Find two numbers that add up to target
 * 
 * Time: O(n), Space: O(n)
 */
public int[] twoSum(int[] nums, int target) {
    Map<Integer, Integer> map = new HashMap<>();
    
    for (int i = 0; i < nums.length; i++) {
        int complement = target - nums[i];
        
        if (map.containsKey(complement)) {
            return new int[] { map.get(complement), i };
        }
        
        map.put(nums[i], i);
    }
    
    return new int[] { -1, -1 };
}
```

### Problem 2: Group Anagrams (LeetCode 49)

```java
/**
 * Group strings that are anagrams
 * 
 * Example: ["eat","tea","tan","ate","nat","bat"]
 *       → [["bat"],["nat","tan"],["ate","eat","tea"]]
 * 
 * Time: O(n * k log k) where k = max string length
 * Space: O(n * k)
 */
public List<List<String>> groupAnagrams(String[] strs) {
    Map<String, List<String>> map = new HashMap<>();
    
    for (String str : strs) {
        char[] chars = str.toCharArray();
        Arrays.sort(chars);
        String sorted = new String(chars);
        
        map.computeIfAbsent(sorted, k -> new ArrayList<>()).add(str);
    }
    
    return new ArrayList<>(map.values());
}

// Alternative: Character count as key (O(n * k))
public List<List<String>> groupAnagramsOptimized(String[] strs) {
    Map<String, List<String>> map = new HashMap<>();
    
    for (String str : strs) {
        int[] count = new int[26];
        for (char c : str.toCharArray()) {
            count[c - 'a']++;
        }
        
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 26; i++) {
            sb.append('#');
            sb.append(count[i]);
        }
        String key = sb.toString();
        
        map.computeIfAbsent(key, k -> new ArrayList<>()).add(str);
    }
    
    return new ArrayList<>(map.values());
}
```

### Problem 3: Longest Substring Without Repeating Characters (LeetCode 3)

```java
/**
 * Find longest substring with unique characters
 * 
 * Example: "abcabcbb" → "abc" (length 3)
 * 
 * Time: O(n), Space: O(min(n, m)) where m = charset size
 */
public int lengthOfLongestSubstring(String s) {
    Map<Character, Integer> map = new HashMap<>();
    int maxLength = 0;
    int left = 0;
    
    for (int right = 0; right < s.length(); right++) {
        char c = s.charAt(right);
        
        if (map.containsKey(c)) {
            left = Math.max(left, map.get(c) + 1);
        }
        
        map.put(c, right);
        maxLength = Math.max(maxLength, right - left + 1);
    }
    
    return maxLength;
}

// Alternative: Using int array (faster for ASCII)
public int lengthOfLongestSubstringArray(String s) {
    int[] lastIndex = new int[128];
    Arrays.fill(lastIndex, -1);
    
    int maxLength = 0;
    int left = 0;
    
    for (int right = 0; right < s.length(); right++) {
        char c = s.charAt(right);
        
        if (lastIndex[c] >= left) {
            left = lastIndex[c] + 1;
        }
        
        lastIndex[c] = right;
        maxLength = Math.max(maxLength, right - left + 1);
    }
    
    return maxLength;
}
```

### Problem 4: Subarray Sum Equals K (LeetCode 560)

```java
/**
 * Count subarrays with sum = k
 * 
 * Time: O(n), Space: O(n)
 */
public int subarraySum(int[] nums, int k) {
    Map<Integer, Integer> prefixSumCount = new HashMap<>();
    prefixSumCount.put(0, 1);  // Empty subarray
    
    int count = 0;
    int sum = 0;
    
    for (int num : nums) {
        sum += num;
        
        // If (sum - k) exists, we found subarrays
        if (prefixSumCount.containsKey(sum - k)) {
            count += prefixSumCount.get(sum - k);
        }
        
        prefixSumCount.put(sum, prefixSumCount.getOrDefault(sum, 0) + 1);
    }
    
    return count;
}
```

### Problem 5: First Unique Character (LeetCode 387)

```java
/**
 * Find first non-repeating character
 * 
 * Time: O(n), Space: O(1) - limited charset
 */
public int firstUniqChar(String s) {
    Map<Character, Integer> count = new HashMap<>();
    
    // Count frequencies
    for (char c : s.toCharArray()) {
        count.put(c, count.getOrDefault(c, 0) + 1);
    }
    
    // Find first unique
    for (int i = 0; i < s.length(); i++) {
        if (count.get(s.charAt(i)) == 1) {
            return i;
        }
    }
    
    return -1;
}

// Alternative: Two-pass with array
public int firstUniqCharArray(String s) {
    int[] count = new int[26];
    
    for (char c : s.toCharArray()) {
        count[c - 'a']++;
    }
    
    for (int i = 0; i < s.length(); i++) {
        if (count[s.charAt(i) - 'a'] == 1) {
            return i;
        }
    }
    
    return -1;
}
```

### Problem 6: Longest Consecutive Sequence (LeetCode 128)

```java
/**
 * Find longest consecutive sequence in unsorted array
 * 
 * Example: [100,4,200,1,3,2] → 4 (sequence: 1,2,3,4)
 * 
 * Time: O(n), Space: O(n)
 */
public int longestConsecutive(int[] nums) {
    Set<Integer> set = new HashSet<>();
    for (int num : nums) {
        set.add(num);
    }
    
    int maxLength = 0;
    
    for (int num : set) {
        // Only start sequence from beginning
        if (!set.contains(num - 1)) {
            int currentNum = num;
            int currentLength = 1;
            
            while (set.contains(currentNum + 1)) {
                currentNum++;
                currentLength++;
            }
            
            maxLength = Math.max(maxLength, currentLength);
        }
    }
    
    return maxLength;
}
```

### Problem 7: LRU Cache (LeetCode 146)

```java
/**
 * LRU Cache using HashMap + Doubly Linked List
 * 
 * Time: O(1) get, O(1) put
 * Space: O(capacity)
 */
class LRUCache {
    
    private class Node {
        int key;
        int value;
        Node prev;
        Node next;
        
        Node(int key, int value) {
            this.key = key;
            this.value = value;
        }
    }
    
    private Map<Integer, Node> map;
    private Node head;
    private Node tail;
    private int capacity;
    
    public LRUCache(int capacity) {
        this.capacity = capacity;
        this.map = new HashMap<>();
        
        // Dummy head and tail
        head = new Node(0, 0);
        tail = new Node(0, 0);
        head.next = tail;
        tail.prev = head;
    }
    
    public int get(int key) {
        if (!map.containsKey(key)) {
            return -1;
        }
        
        Node node = map.get(key);
        moveToFront(node);
        return node.value;
    }
    
    public void put(int key, int value) {
        if (map.containsKey(key)) {
            Node node = map.get(key);
            node.value = value;
            moveToFront(node);
        } else {
            if (map.size() == capacity) {
                Node lru = tail.prev;
                removeNode(lru);
                map.remove(lru.key);
            }
            
            Node newNode = new Node(key, value);
            map.put(key, newNode);
            addToFront(newNode);
        }
    }
    
    private void moveToFront(Node node) {
        removeNode(node);
        addToFront(node);
    }
    
    private void addToFront(Node node) {
        node.next = head.next;
        node.prev = head;
        head.next.prev = node;
        head.next = node;
    }
    
    private void removeNode(Node node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
    }
}
```

### Problem 8: Valid Sudoku (LeetCode 36)

```java
/**
 * Validate Sudoku board
 * 
 * Time: O(1) - fixed 9x9 board
 * Space: O(1)
 */
public boolean isValidSudoku(char[][] board) {
    Set<String> seen = new HashSet<>();
    
    for (int i = 0; i < 9; i++) {
        for (int j = 0; j < 9; j++) {
            char num = board[i][j];
            
            if (num != '.') {
                // Check row, column, and box
                if (!seen.add(num + " in row " + i) ||
                    !seen.add(num + " in col " + j) ||
                    !seen.add(num + " in box " + (i/3) + "-" + (j/3))) {
                    return false;
                }
            }
        }
    }
    
    return true;
}
```

---

## Thread-Safe Variants

### 1. ConcurrentHashMap

```java
/**
 * Thread-safe HashMap without full synchronization
 * 
 * Features:
 * - Segment-level locking (Java 7) or CAS operations (Java 8+)
 * - Better concurrency than Hashtable
 * - No null keys or values
 */
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();

map.put("key", 1);
map.get("key");
map.computeIfAbsent("key", k -> k.length());

// Atomic operations
map.putIfAbsent("key", 1);
map.replace("key", 1, 2);
map.compute("key", (k, v) -> v == null ? 1 : v + 1);
map.merge("key", 1, Integer::sum);
```

### 2. Collections.synchronizedMap

```java
/**
 * Synchronized wrapper (less efficient)
 */
Map<String, Integer> syncMap = Collections.synchronizedMap(new HashMap<>());

// Must synchronize on map for iteration
synchronized (syncMap) {
    for (Map.Entry<String, Integer> entry : syncMap.entrySet()) {
        // ...
    }
}
```

---

## Real-World Use Cases

### 1. Caching in Data Pipelines

```java
/**
 * Cache for expensive transformations
 */
public class DataTransformCache {
    
    private Map<String, DataFrame> cache;
    
    public DataTransformCache() {
        this.cache = new HashMap<>();
    }
    
    public DataFrame transform(String datasetId, Supplier<DataFrame> transformer) {
        return cache.computeIfAbsent(datasetId, k -> transformer.get());
    }
    
    public void invalidate(String datasetId) {
        cache.remove(datasetId);
    }
    
    public void clear() {
        cache.clear();
    }
}
```

### 2. Deduplication in Streaming

```java
/**
 * Deduplicate events in stream
 */
public class EventDeduplicator {
    
    private Set<String> seenIds;
    
    public EventDeduplicator() {
        this.seenIds = new HashSet<>();
    }
    
    public boolean isUnique(Event event) {
        return seenIds.add(event.getId());
    }
    
    public void clear() {
        seenIds.clear();
    }
}
```

### 3. Frequency Counter

```java
/**
 * Count word frequencies in text
 */
public Map<String, Integer> countWordFrequencies(String text) {
    Map<String, Integer> frequencies = new HashMap<>();
    
    String[] words = text.toLowerCase().split("\\s+");
    
    for (String word : words) {
        frequencies.merge(word, 1, Integer::sum);
    }
    
    return frequencies;
}
```

---

## 🎯 Interview Tips

### HashMap vs HashSet vs Hashtable

| Feature | HashMap | HashSet | Hashtable |
|---------|---------|---------|-----------|
| **Type** | Map | Set | Map |
| **Null Keys** | 1 allowed | 1 allowed | Not allowed |
| **Null Values** | Multiple | N/A | Not allowed |
| **Thread-Safe** | No | No | Yes (slow) |
| **Performance** | O(1) | O(1) | O(1) |
| **Synchronized** | No | No | Yes |

### When to Use HashMap

**Use HashMap when:**
- ✅ Need key-value associations
- ✅ Fast lookups required
- ✅ Keys are unique
- ✅ Order doesn't matter
- ✅ Single-threaded or external synchronization

**Use HashSet when:**
- ✅ Need unique elements only
- ✅ Fast membership testing
- ✅ No key-value pairs needed

**Avoid HashMap when:**
- ❌ Need sorted keys → TreeMap
- ❌ Need insertion order → LinkedHashMap
- ❌ High concurrency → ConcurrentHashMap

### Common Patterns

1. **Frequency Counter**: `map.merge(key, 1, Integer::sum)`
2. **Grouping**: `map.computeIfAbsent(key, k -> new ArrayList<>())`
3. **Caching**: `map.computeIfAbsent(key, expensiveFunction)`
4. **Two Sum Pattern**: Store complements
5. **Sliding Window**: HashMap + two pointers

### Complexity Gotchas

```java
// ❌ BAD: O(n) containsValue
if (map.containsValue(value)) { ... }

// ✅ GOOD: O(1) containsKey
if (map.containsKey(key)) { ... }

// ❌ BAD: Multiple lookups
if (map.containsKey(key)) {
    value = map.get(key);
}

// ✅ GOOD: Single lookup
value = map.get(key);
if (value != null) { ... }
```

---

**Next:** [TreeMap and TreeSet](./06-TreeMap-and-TreeSet.md) — Sorted map/set implementations
