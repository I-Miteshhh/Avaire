# TreeMap and TreeSet

**Difficulty:** Intermediate-Advanced  
**Learning Time:** 2-3 weeks  
**Interview Frequency:** ⭐⭐⭐⭐ (High)

---

## 📚 Table of Contents

1. [Red-Black Tree Fundamentals](#red-black-tree-fundamentals)
2. [TreeMap](#treemap)
3. [TreeSet](#treeset)
4. [Interview Problems](#interview-problems)
5. [TreeMap vs HashMap](#treemap-vs-hashmap)
6. [Real-World Use Cases](#real-world-use-cases)

---

## Red-Black Tree Fundamentals

### What is a Red-Black Tree?

```
Self-balancing Binary Search Tree with these properties:
1. Every node is either RED or BLACK
2. Root is always BLACK
3. All leaves (NIL) are BLACK
4. Red nodes cannot have red children (no two consecutive reds)
5. Every path from root to leaf has same number of black nodes
```

### Why Self-Balancing?

```
Regular BST worst case: O(n) for skewed tree
Red-Black Tree: O(log n) guaranteed

Example skewed BST:
    1
     \
      2
       \
        3  ← O(n) height

Red-Black Tree:
      2 (B)
     / \
   1(R) 3(R)  ← O(log n) height
```

### Time Complexity

| Operation | Average | Worst Case |
|-----------|---------|------------|
| **Search** | O(log n) | O(log n) |
| **Insert** | O(log n) | O(log n) |
| **Delete** | O(log n) | O(log n) |
| **Min/Max** | O(log n) | O(log n) |
| **Floor/Ceiling** | O(log n) | O(log n) |

---

## TreeMap

### Characteristics

```
✅ Sorted by keys (natural order or comparator)
✅ O(log n) get/put/remove
✅ Range queries (subMap, headMap, tailMap)
✅ Floor, ceiling, higher, lower operations
❌ Slower than HashMap
❌ No null keys (throws NPE)
❌ Not thread-safe
```

### Java TreeMap API

```java
TreeMap<Integer, String> map = new TreeMap<>();

// Basic operations
map.put(3, "three");         // Insert: O(log n)
map.put(1, "one");
map.put(2, "two");

String value = map.get(2);   // Get: O(log n)
map.remove(1);               // Remove: O(log n)

// Iteration (sorted order)
for (Map.Entry<Integer, String> entry : map.entrySet()) {
    System.out.println(entry.getKey() + " -> " + entry.getValue());
}

// First and last
Integer firstKey = map.firstKey();      // O(log n)
Integer lastKey = map.lastKey();        // O(log n)
Map.Entry<Integer, String> firstEntry = map.firstEntry();
Map.Entry<Integer, String> lastEntry = map.lastEntry();

// Floor and ceiling
Integer floor = map.floorKey(2);     // Largest key <= 2
Integer ceiling = map.ceilingKey(2); // Smallest key >= 2
Map.Entry<Integer, String> floorEntry = map.floorEntry(2);
Map.Entry<Integer, String> ceilingEntry = map.ceilingEntry(2);

// Higher and lower
Integer higher = map.higherKey(2);   // Smallest key > 2
Integer lower = map.lowerKey(2);     // Largest key < 2

// Poll (remove and return)
Map.Entry<Integer, String> pollFirst = map.pollFirstEntry();
Map.Entry<Integer, String> pollLast = map.pollLastEntry();

// Range views
SortedMap<Integer, String> subMap = map.subMap(1, 3);     // [1, 3)
SortedMap<Integer, String> headMap = map.headMap(3);      // [min, 3)
SortedMap<Integer, String> tailMap = map.tailMap(2);      // [2, max]

// Custom comparator
TreeMap<String, Integer> reverseMap = new TreeMap<>(Collections.reverseOrder());
TreeMap<String, Integer> customMap = new TreeMap<>((a, b) -> a.length() - b.length());
```

### TreeMap with Custom Objects

```java
class Employee {
    String name;
    int salary;
    
    Employee(String name, int salary) {
        this.name = name;
        this.salary = salary;
    }
}

// Comparator by salary
TreeMap<Employee, String> map = new TreeMap<>(
    (e1, e2) -> Integer.compare(e1.salary, e2.salary)
);

map.put(new Employee("Alice", 50000), "Engineer");
map.put(new Employee("Bob", 60000), "Manager");
map.put(new Employee("Charlie", 40000), "Intern");

// Iterate in salary order
for (Map.Entry<Employee, String> entry : map.entrySet()) {
    System.out.println(entry.getKey().name + ": " + entry.getValue());
}
// Output: Charlie: Intern, Alice: Engineer, Bob: Manager
```

---

## TreeSet

### Characteristics

```
✅ Sorted unique elements
✅ O(log n) add/remove/contains
✅ Range queries
✅ Floor, ceiling, higher, lower
❌ Slower than HashSet
❌ No null elements
```

### Java TreeSet API

```java
TreeSet<Integer> set = new TreeSet<>();

// Basic operations
set.add(3);          // Add: O(log n)
set.add(1);
set.add(2);
set.remove(1);       // Remove: O(log n)
boolean contains = set.contains(2);  // O(log n)

// Iteration (sorted)
for (int num : set) {
    System.out.println(num);  // 1, 2, 3
}

// First and last
int first = set.first();    // O(log n)
int last = set.last();      // O(log n)
int pollFirst = set.pollFirst();  // Remove and return first
int pollLast = set.pollLast();    // Remove and return last

// Floor and ceiling
int floor = set.floor(2);       // Largest element <= 2
int ceiling = set.ceiling(2);   // Smallest element >= 2

// Higher and lower
int higher = set.higher(2);     // Smallest element > 2
int lower = set.lower(2);       // Largest element < 2

// Range views
SortedSet<Integer> subset = set.subSet(1, 3);   // [1, 3)
SortedSet<Integer> headSet = set.headSet(3);    // [min, 3)
SortedSet<Integer> tailSet = set.tailSet(2);    // [2, max]

// Descending
NavigableSet<Integer> descending = set.descendingSet();
```

---

## Interview Problems

### Problem 1: Range Sum Query - Mutable (LeetCode 307)

```java
/**
 * TreeMap-based solution for range sum queries
 * 
 * Time: O(log n) update, O(log n) range sum
 */
class NumArray {
    
    private TreeMap<Integer, Integer> tree;
    private int[] nums;
    
    public NumArray(int[] nums) {
        this.nums = nums;
        this.tree = new TreeMap<>();
        
        // Build prefix sum tree
        int sum = 0;
        for (int i = 0; i < nums.length; i++) {
            sum += nums[i];
            tree.put(i, sum);
        }
    }
    
    public void update(int index, int val) {
        int diff = val - nums[index];
        nums[index] = val;
        
        // Update all entries >= index
        for (Map.Entry<Integer, Integer> entry : tree.tailMap(index).entrySet()) {
            tree.put(entry.getKey(), entry.getValue() + diff);
        }
    }
    
    public int sumRange(int left, int right) {
        int rightSum = tree.get(right);
        int leftSum = left > 0 ? tree.get(left - 1) : 0;
        return rightSum - leftSum;
    }
}
```

### Problem 2: Contains Duplicate III (LeetCode 220)

```java
/**
 * Find if there exist two indices i and j such that:
 * - abs(i - j) <= indexDiff
 * - abs(nums[i] - nums[j]) <= valueDiff
 * 
 * Time: O(n log k), Space: O(k)
 */
public boolean containsNearbyAlmostDuplicate(int[] nums, int indexDiff, int valueDiff) {
    TreeSet<Long> set = new TreeSet<>();
    
    for (int i = 0; i < nums.length; i++) {
        long num = nums[i];
        
        // Find smallest number >= (num - valueDiff)
        Long floor = set.ceiling(num - valueDiff);
        
        if (floor != null && floor <= num + valueDiff) {
            return true;
        }
        
        set.add(num);
        
        // Remove out-of-range element
        if (i >= indexDiff) {
            set.remove((long) nums[i - indexDiff]);
        }
    }
    
    return false;
}
```

### Problem 3: My Calendar I (LeetCode 729)

```java
/**
 * Implement calendar that doesn't allow double bookings
 * 
 * Time: O(log n) per booking
 */
class MyCalendar {
    
    private TreeMap<Integer, Integer> bookings;
    
    public MyCalendar() {
        bookings = new TreeMap<>();
    }
    
    public boolean book(int start, int end) {
        // Check previous booking
        Integer prevStart = bookings.floorKey(start);
        if (prevStart != null && bookings.get(prevStart) > start) {
            return false;  // Overlaps with previous
        }
        
        // Check next booking
        Integer nextStart = bookings.ceilingKey(start);
        if (nextStart != null && nextStart < end) {
            return false;  // Overlaps with next
        }
        
        bookings.put(start, end);
        return true;
    }
}
```

### Problem 4: My Calendar II (LeetCode 731)

```java
/**
 * Allow at most double bookings (no triple bookings)
 * 
 * Time: O(n) per booking
 */
class MyCalendarTwo {
    
    private TreeMap<Integer, Integer> delta;
    
    public MyCalendarTwo() {
        delta = new TreeMap<>();
    }
    
    public boolean book(int start, int end) {
        delta.put(start, delta.getOrDefault(start, 0) + 1);
        delta.put(end, delta.getOrDefault(end, 0) - 1);
        
        int active = 0;
        for (int d : delta.values()) {
            active += d;
            
            if (active >= 3) {
                // Rollback
                delta.put(start, delta.get(start) - 1);
                delta.put(end, delta.get(end) + 1);
                
                if (delta.get(start) == 0) delta.remove(start);
                if (delta.get(end) == 0) delta.remove(end);
                
                return false;
            }
        }
        
        return true;
    }
}
```

### Problem 5: Count of Range Sum (LeetCode 327)

```java
/**
 * Count number of range sums in [lower, upper]
 * 
 * Time: O(n log n), Space: O(n)
 */
public int countRangeSum(int[] nums, int lower, int upper) {
    long[] prefixSum = new long[nums.length + 1];
    
    for (int i = 0; i < nums.length; i++) {
        prefixSum[i + 1] = prefixSum[i] + nums[i];
    }
    
    return countRangeSumHelper(prefixSum, 0, prefixSum.length, lower, upper);
}

private int countRangeSumHelper(long[] sums, int start, int end, int lower, int upper) {
    if (end - start <= 1) {
        return 0;
    }
    
    int mid = (start + end) / 2;
    int count = countRangeSumHelper(sums, start, mid, lower, upper) + 
                countRangeSumHelper(sums, mid, end, lower, upper);
    
    int j = mid, k = mid, t = mid;
    long[] cache = new long[end - start];
    int r = 0;
    
    for (int i = start; i < mid; i++) {
        while (k < end && sums[k] - sums[i] < lower) k++;
        while (j < end && sums[j] - sums[i] <= upper) j++;
        count += j - k;
        
        while (t < end && sums[t] < sums[i]) {
            cache[r++] = sums[t++];
        }
        cache[r++] = sums[i];
    }
    
    System.arraycopy(cache, 0, sums, start, r);
    return count;
}
```

### Problem 6: Longest Repeating Character Replacement (LeetCode 424)

```java
/**
 * Longest substring with at most k character replacements
 * 
 * Time: O(n), Space: O(1)
 */
public int characterReplacement(String s, int k) {
    int[] count = new int[26];
    int maxCount = 0;
    int maxLength = 0;
    int left = 0;
    
    for (int right = 0; right < s.length(); right++) {
        maxCount = Math.max(maxCount, ++count[s.charAt(right) - 'A']);
        
        // If window size - most frequent char > k, shrink window
        while (right - left + 1 - maxCount > k) {
            count[s.charAt(left) - 'A']--;
            left++;
        }
        
        maxLength = Math.max(maxLength, right - left + 1);
    }
    
    return maxLength;
}
```

### Problem 7: Find K Closest Elements (LeetCode 658)

```java
/**
 * Find k closest elements to x in sorted array
 * 
 * Time: O(log n + k), Space: O(k)
 */
public List<Integer> findClosestElements(int[] arr, int k, int x) {
    int left = 0;
    int right = arr.length - k;
    
    while (left < right) {
        int mid = left + (right - left) / 2;
        
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

// Alternative: TreeMap solution
public List<Integer> findClosestElementsTreeMap(int[] arr, int k, int x) {
    TreeMap<Integer, List<Integer>> distanceMap = new TreeMap<>();
    
    for (int num : arr) {
        int distance = Math.abs(num - x);
        distanceMap.computeIfAbsent(distance, d -> new ArrayList<>()).add(num);
    }
    
    List<Integer> result = new ArrayList<>();
    
    for (List<Integer> nums : distanceMap.values()) {
        Collections.sort(nums);
        for (int num : nums) {
            if (result.size() == k) {
                break;
            }
            result.add(num);
        }
        if (result.size() == k) {
            break;
        }
    }
    
    Collections.sort(result);
    return result;
}
```

---

## TreeMap vs HashMap

### Comparison

| Feature | TreeMap | HashMap |
|---------|---------|---------|
| **Ordering** | Sorted | Unordered |
| **Time (get)** | O(log n) | O(1) |
| **Time (put)** | O(log n) | O(1) |
| **Null Keys** | No | 1 allowed |
| **Range Queries** | Yes | No |
| **Floor/Ceiling** | Yes | No |
| **Space** | O(n) | O(n) |
| **Implementation** | Red-Black Tree | Hash Table |

### When to Use TreeMap

**Use TreeMap when:**
- ✅ Need sorted keys
- ✅ Range queries (subMap, headMap, tailMap)
- ✅ Floor, ceiling, higher, lower operations
- ✅ First/last key access
- ✅ In-order iteration required

**Use HashMap when:**
- ✅ Order doesn't matter
- ✅ Need O(1) operations
- ✅ No range queries needed

---

## Real-World Use Cases

### 1. Time-Series Data (Event Log)

```java
/**
 * Store and query events by timestamp
 */
class EventLog {
    
    private TreeMap<Long, List<Event>> events;
    
    public EventLog() {
        events = new TreeMap<>();
    }
    
    public void logEvent(Event event) {
        events.computeIfAbsent(event.timestamp, k -> new ArrayList<>()).add(event);
    }
    
    /**
     * Get all events in time range
     */
    public List<Event> getEventsInRange(long startTime, long endTime) {
        List<Event> result = new ArrayList<>();
        
        for (List<Event> eventList : events.subMap(startTime, endTime + 1).values()) {
            result.addAll(eventList);
        }
        
        return result;
    }
    
    /**
     * Get most recent event before timestamp
     */
    public Event getEventBefore(long timestamp) {
        Map.Entry<Long, List<Event>> entry = events.floorEntry(timestamp);
        
        if (entry != null && !entry.getValue().isEmpty()) {
            List<Event> eventList = entry.getValue();
            return eventList.get(eventList.size() - 1);
        }
        
        return null;
    }
}

class Event {
    long timestamp;
    String type;
    String data;
    
    Event(long timestamp, String type, String data) {
        this.timestamp = timestamp;
        this.type = type;
        this.data = data;
    }
}
```

### 2. Leaderboard (Sorted Scores)

```java
/**
 * Game leaderboard with ranking
 */
class Leaderboard {
    
    private TreeMap<Integer, Set<String>> scoreToPlayers;
    private Map<String, Integer> playerToScore;
    
    public Leaderboard() {
        scoreToPlayers = new TreeMap<>(Collections.reverseOrder());
        playerToScore = new HashMap<>();
    }
    
    public void addScore(String player, int score) {
        if (playerToScore.containsKey(player)) {
            int oldScore = playerToScore.get(player);
            scoreToPlayers.get(oldScore).remove(player);
            
            if (scoreToPlayers.get(oldScore).isEmpty()) {
                scoreToPlayers.remove(oldScore);
            }
            
            score += oldScore;
        }
        
        playerToScore.put(player, score);
        scoreToPlayers.computeIfAbsent(score, k -> new HashSet<>()).add(player);
    }
    
    public int top(int k) {
        int sum = 0;
        int count = 0;
        
        for (Map.Entry<Integer, Set<String>> entry : scoreToPlayers.entrySet()) {
            int score = entry.getKey();
            Set<String> players = entry.getValue();
            
            for (String player : players) {
                sum += score;
                count++;
                
                if (count == k) {
                    return sum;
                }
            }
        }
        
        return sum;
    }
    
    public int getRank(String player) {
        if (!playerToScore.containsKey(player)) {
            return -1;
        }
        
        int playerScore = playerToScore.get(player);
        int rank = 1;
        
        for (Map.Entry<Integer, Set<String>> entry : scoreToPlayers.entrySet()) {
            if (entry.getKey() <= playerScore) {
                break;
            }
            rank += entry.getValue().size();
        }
        
        return rank;
    }
}
```

### 3. Meeting Room Scheduler

```java
/**
 * Schedule meetings without conflicts
 */
class MeetingScheduler {
    
    private TreeMap<Integer, Integer> schedule;
    
    public MeetingScheduler() {
        schedule = new TreeMap<>();
    }
    
    public boolean book(int start, int end) {
        // Check for conflicts
        Integer prevStart = schedule.floorKey(start);
        if (prevStart != null && schedule.get(prevStart) > start) {
            return false;
        }
        
        Integer nextStart = schedule.ceilingKey(start);
        if (nextStart != null && nextStart < end) {
            return false;
        }
        
        schedule.put(start, end);
        return true;
    }
    
    public List<int[]> getAvailableSlots(int start, int end) {
        List<int[]> available = new ArrayList<>();
        int currentStart = start;
        
        for (Map.Entry<Integer, Integer> entry : schedule.subMap(start, end).entrySet()) {
            if (currentStart < entry.getKey()) {
                available.add(new int[]{currentStart, entry.getKey()});
            }
            currentStart = Math.max(currentStart, entry.getValue());
        }
        
        if (currentStart < end) {
            available.add(new int[]{currentStart, end});
        }
        
        return available;
    }
}
```

### 4. Spark Partition Range Index

```java
/**
 * Track data distribution across Spark partitions
 */
class PartitionIndex {
    
    private TreeMap<Long, Integer> rangeToPartition;
    
    public PartitionIndex() {
        rangeToPartition = new TreeMap<>();
    }
    
    /**
     * Register partition with start key
     */
    public void addPartition(long startKey, int partitionId) {
        rangeToPartition.put(startKey, partitionId);
    }
    
    /**
     * Find which partition contains the key
     */
    public int findPartition(long key) {
        Map.Entry<Long, Integer> entry = rangeToPartition.floorEntry(key);
        return entry != null ? entry.getValue() : -1;
    }
    
    /**
     * Get all partitions in key range
     */
    public Set<Integer> getPartitionsInRange(long startKey, long endKey) {
        Set<Integer> partitions = new HashSet<>();
        
        for (Integer partitionId : rangeToPartition.subMap(startKey, endKey + 1).values()) {
            partitions.add(partitionId);
        }
        
        // Also check partition containing startKey
        Integer startPartition = findPartition(startKey);
        if (startPartition != -1) {
            partitions.add(startPartition);
        }
        
        return partitions;
    }
}
```

---

## 🎯 Interview Tips

### TreeMap/TreeSet Patterns

1. **Range Queries**: Use `subMap`, `headMap`, `tailMap`
2. **Floor/Ceiling**: Find closest elements
3. **Sorted Iteration**: Natural ordering
4. **Calendar Problems**: Interval scheduling
5. **Time-Series**: Events sorted by timestamp

### Common Mistakes

```java
// ❌ BAD: Null key throws NPE
TreeMap<Integer, String> map = new TreeMap<>();
map.put(null, "value");  // NullPointerException!

// ✅ GOOD: Check for null
if (key != null) {
    map.put(key, value);
}

// ❌ BAD: Inefficient value search
if (map.containsValue("value")) { ... }  // O(n)

// ✅ GOOD: Use reverse mapping if needed
Map<String, Integer> reverseMap = new HashMap<>();
```

### Performance Considerations

```java
// TreeMap is slower than HashMap
// Use TreeMap only when you need sorting/range queries

// For small datasets (< 100 elements), difference is negligible
// For large datasets, TreeMap can be 3-5x slower than HashMap
```

---

**Next:** [Trie](./07-Trie.md) — Prefix tree for string operations
