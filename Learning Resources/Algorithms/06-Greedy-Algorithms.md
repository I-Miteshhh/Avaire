# Greedy Algorithms

**Difficulty:** Medium  
**Learning Time:** 3-5 days  
**Interview Frequency:** ⭐⭐⭐⭐ (High)  
**Common In:** Optimization problems, scheduling, interval problems

---

## 📚 Table of Contents

1. [Greedy Algorithm Fundamentals](#greedy-algorithm-fundamentals)
2. [Interval Scheduling](#interval-scheduling)
3. [Jump Problems](#jump-problems)
4. [Partitioning Problems](#partitioning-problems)
5. [Huffman Coding](#huffman-coding)
6. [Real-World Applications](#real-world-applications)

---

## Greedy Algorithm Fundamentals

### Definition

Make **locally optimal choice** at each step, hoping to find global optimum.

### When Greedy Works

1. **Greedy Choice Property:** Locally optimal choice leads to globally optimal solution
2. **Optimal Substructure:** Optimal solution contains optimal solutions to subproblems

### Greedy vs Dynamic Programming

| Greedy | Dynamic Programming |
|--------|-------------------|
| Makes choice without looking ahead | Considers all possibilities |
| O(n) or O(n log n) typically | O(n²) or higher typically |
| Works only for specific problems | Works for more general problems |
| No backtracking | May need to backtrack |

---

## Interval Scheduling

### Problem 1: Activity Selection

**Classic greedy problem**

```java
/**
 * Select maximum number of non-overlapping activities
 * Sort by end time, greedily select earliest ending
 * 
 * Time: O(n log n), Space: O(1)
 */
class Solution {
    static class Activity {
        int start;
        int end;
        
        Activity(int start, int end) {
            this.start = start;
            this.end = end;
        }
    }
    
    public int activitySelection(Activity[] activities) {
        // Sort by end time (greedy choice)
        Arrays.sort(activities, (a, b) -> Integer.compare(a.end, b.end));
        
        int count = 1;
        int lastEndTime = activities[0].end;
        
        for (int i = 1; i < activities.length; i++) {
            if (activities[i].start >= lastEndTime) {
                count++;
                lastEndTime = activities[i].end;
            }
        }
        
        return count;
    }
}
```

**Why greedy works:**
- Activity ending earliest leaves most room for future activities
- Optimal substructure: After choosing first activity, solve same problem on remaining

---

### Problem 2: Non-overlapping Intervals

**LeetCode 435**

```java
/**
 * Minimum number of intervals to remove to make rest non-overlapping
 * Time: O(n log n), Space: O(log n) for sorting
 */
class Solution {
    public int eraseOverlapIntervals(int[][] intervals) {
        if (intervals.length == 0) return 0;
        
        // Sort by end time
        Arrays.sort(intervals, (a, b) -> Integer.compare(a[1], b[1]));
        
        int count = 0;
        int end = intervals[0][1];
        
        for (int i = 1; i < intervals.length; i++) {
            if (intervals[i][0] < end) {
                // Overlapping - remove current interval
                count++;
            } else {
                // Non-overlapping - update end
                end = intervals[i][1];
            }
        }
        
        return count;
    }
}
```

---

### Problem 3: Merge Intervals

**LeetCode 56**

```java
/**
 * Merge overlapping intervals
 * Time: O(n log n), Space: O(n)
 */
class Solution {
    public int[][] merge(int[][] intervals) {
        if (intervals.length <= 1) {
            return intervals;
        }
        
        // Sort by start time
        Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));
        
        List<int[]> result = new ArrayList<>();
        int[] current = intervals[0];
        result.add(current);
        
        for (int i = 1; i < intervals.length; i++) {
            if (intervals[i][0] <= current[1]) {
                // Overlapping - merge
                current[1] = Math.max(current[1], intervals[i][1]);
            } else {
                // Non-overlapping - add new interval
                current = intervals[i];
                result.add(current);
            }
        }
        
        return result.toArray(new int[result.size()][]);
    }
}
```

---

### Problem 4: Meeting Rooms II

**LeetCode 253**

```java
/**
 * Minimum number of conference rooms required
 * Time: O(n log n), Space: O(n)
 */
class Solution {
    public int minMeetingRooms(int[][] intervals) {
        if (intervals.length == 0) return 0;
        
        // Separate start and end times
        int[] starts = new int[intervals.length];
        int[] ends = new int[intervals.length];
        
        for (int i = 0; i < intervals.length; i++) {
            starts[i] = intervals[i][0];
            ends[i] = intervals[i][1];
        }
        
        Arrays.sort(starts);
        Arrays.sort(ends);
        
        int rooms = 0;
        int endIdx = 0;
        
        for (int i = 0; i < starts.length; i++) {
            if (starts[i] < ends[endIdx]) {
                // Meeting starts before previous ends - need new room
                rooms++;
            } else {
                // Previous meeting ended - can reuse room
                endIdx++;
            }
        }
        
        return rooms;
    }
}

/**
 * Alternative: Using min heap
 */
class SolutionHeap {
    public int minMeetingRooms(int[][] intervals) {
        if (intervals.length == 0) return 0;
        
        // Sort by start time
        Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));
        
        // Min heap to track end times
        PriorityQueue<Integer> heap = new PriorityQueue<>();
        heap.offer(intervals[0][1]);
        
        for (int i = 1; i < intervals.length; i++) {
            // If earliest ending meeting finished, reuse room
            if (intervals[i][0] >= heap.peek()) {
                heap.poll();
            }
            
            heap.offer(intervals[i][1]);
        }
        
        return heap.size();
    }
}
```

---

## Jump Problems

### Problem 5: Jump Game

**LeetCode 55**

```java
/**
 * Determine if can jump to last index
 * nums[i] = max jump length from index i
 * 
 * Time: O(n), Space: O(1)
 */
class Solution {
    public boolean canJump(int[] nums) {
        int maxReach = 0;
        
        for (int i = 0; i < nums.length; i++) {
            if (i > maxReach) {
                return false;  // Can't reach this position
            }
            
            maxReach = Math.max(maxReach, i + nums[i]);
            
            if (maxReach >= nums.length - 1) {
                return true;  // Can reach end
            }
        }
        
        return true;
    }
}
```

**Greedy choice:** Track furthest reachable position.

---

### Problem 6: Jump Game II

**LeetCode 45**

```java
/**
 * Minimum number of jumps to reach last index
 * Time: O(n), Space: O(1)
 */
class Solution {
    public int jump(int[] nums) {
        if (nums.length <= 1) return 0;
        
        int jumps = 0;
        int currentEnd = 0;
        int furthest = 0;
        
        for (int i = 0; i < nums.length - 1; i++) {
            furthest = Math.max(furthest, i + nums[i]);
            
            if (i == currentEnd) {
                // Must jump now
                jumps++;
                currentEnd = furthest;
                
                if (currentEnd >= nums.length - 1) {
                    break;
                }
            }
        }
        
        return jumps;
    }
}
```

**Greedy strategy:** Jump to position that allows furthest reach next.

---

## Partitioning Problems

### Problem 7: Partition Labels

**LeetCode 763**

```java
/**
 * Partition string so each letter appears in at most one part
 * Time: O(n), Space: O(26) = O(1)
 */
class Solution {
    public List<Integer> partitionLabels(String s) {
        // Find last occurrence of each character
        int[] lastOccurrence = new int[26];
        for (int i = 0; i < s.length(); i++) {
            lastOccurrence[s.charAt(i) - 'a'] = i;
        }
        
        List<Integer> result = new ArrayList<>();
        int start = 0;
        int end = 0;
        
        for (int i = 0; i < s.length(); i++) {
            end = Math.max(end, lastOccurrence[s.charAt(i) - 'a']);
            
            if (i == end) {
                // Can make partition here
                result.add(end - start + 1);
                start = i + 1;
            }
        }
        
        return result;
    }
}
```

---

### Problem 8: Gas Station

**LeetCode 134**

```java
/**
 * Find starting gas station to complete circular route
 * Time: O(n), Space: O(1)
 */
class Solution {
    public int canCompleteCircuit(int[] gas, int[] cost) {
        int totalGas = 0;
        int totalCost = 0;
        int currentGas = 0;
        int start = 0;
        
        for (int i = 0; i < gas.length; i++) {
            totalGas += gas[i];
            totalCost += cost[i];
            currentGas += gas[i] - cost[i];
            
            if (currentGas < 0) {
                // Can't reach from current start - try next station
                start = i + 1;
                currentGas = 0;
            }
        }
        
        return totalGas >= totalCost ? start : -1;
    }
}
```

**Greedy insight:** If can't reach station i from start, can't reach from any station before i.

---

### Problem 9: Task Scheduler

**LeetCode 621**

```java
/**
 * Minimum time to complete all tasks with cooling period
 * Time: O(n), Space: O(26) = O(1)
 */
class Solution {
    public int leastInterval(char[] tasks, int n) {
        // Count frequency of each task
        int[] freq = new int[26];
        int maxFreq = 0;
        int maxCount = 0;
        
        for (char task : tasks) {
            freq[task - 'A']++;
            if (freq[task - 'A'] > maxFreq) {
                maxFreq = freq[task - 'A'];
                maxCount = 1;
            } else if (freq[task - 'A'] == maxFreq) {
                maxCount++;
            }
        }
        
        // Calculate minimum time
        int partCount = maxFreq - 1;
        int partLength = n - (maxCount - 1);
        int emptySlots = partCount * partLength;
        int availableTasks = tasks.length - maxFreq * maxCount;
        int idles = Math.max(0, emptySlots - availableTasks);
        
        return tasks.length + idles;
    }
}

/**
 * Alternative: Using max heap
 */
class SolutionHeap {
    public int leastInterval(char[] tasks, int n) {
        int[] freq = new int[26];
        for (char task : tasks) {
            freq[task - 'A']++;
        }
        
        PriorityQueue<Integer> maxHeap = new PriorityQueue<>((a, b) -> b - a);
        for (int f : freq) {
            if (f > 0) {
                maxHeap.offer(f);
            }
        }
        
        int time = 0;
        
        while (!maxHeap.isEmpty()) {
            List<Integer> temp = new ArrayList<>();
            
            for (int i = 0; i <= n; i++) {
                if (!maxHeap.isEmpty()) {
                    int count = maxHeap.poll();
                    if (count > 1) {
                        temp.add(count - 1);
                    }
                }
                
                time++;
                
                if (maxHeap.isEmpty() && temp.isEmpty()) {
                    break;
                }
            }
            
            for (int count : temp) {
                maxHeap.offer(count);
            }
        }
        
        return time;
    }
}
```

---

## Huffman Coding

### Problem 10: Huffman Encoding

```java
/**
 * Huffman coding for data compression
 * Time: O(n log n), Space: O(n)
 */
class HuffmanCoding {
    
    static class Node implements Comparable<Node> {
        char ch;
        int freq;
        Node left;
        Node right;
        
        Node(char ch, int freq) {
            this.ch = ch;
            this.freq = freq;
        }
        
        boolean isLeaf() {
            return left == null && right == null;
        }
        
        @Override
        public int compareTo(Node other) {
            return Integer.compare(this.freq, other.freq);
        }
    }
    
    /**
     * Build Huffman tree
     */
    public Node buildHuffmanTree(Map<Character, Integer> freqMap) {
        PriorityQueue<Node> pq = new PriorityQueue<>();
        
        // Create leaf nodes
        for (Map.Entry<Character, Integer> entry : freqMap.entrySet()) {
            pq.offer(new Node(entry.getKey(), entry.getValue()));
        }
        
        // Build tree bottom-up
        while (pq.size() > 1) {
            Node left = pq.poll();
            Node right = pq.poll();
            
            Node parent = new Node('\0', left.freq + right.freq);
            parent.left = left;
            parent.right = right;
            
            pq.offer(parent);
        }
        
        return pq.poll();
    }
    
    /**
     * Generate codes
     */
    public Map<Character, String> generateCodes(Node root) {
        Map<Character, String> codes = new HashMap<>();
        generateCodesHelper(root, "", codes);
        return codes;
    }
    
    private void generateCodesHelper(Node node, String code, Map<Character, String> codes) {
        if (node == null) return;
        
        if (node.isLeaf()) {
            codes.put(node.ch, code);
            return;
        }
        
        generateCodesHelper(node.left, code + "0", codes);
        generateCodesHelper(node.right, code + "1", codes);
    }
    
    /**
     * Encode string
     */
    public String encode(String text, Map<Character, String> codes) {
        StringBuilder encoded = new StringBuilder();
        for (char ch : text.toCharArray()) {
            encoded.append(codes.get(ch));
        }
        return encoded.toString();
    }
    
    /**
     * Decode string
     */
    public String decode(String encoded, Node root) {
        StringBuilder decoded = new StringBuilder();
        Node current = root;
        
        for (char bit : encoded.toCharArray()) {
            current = (bit == '0') ? current.left : current.right;
            
            if (current.isLeaf()) {
                decoded.append(current.ch);
                current = root;
            }
        }
        
        return decoded.toString();
    }
}

/**
 * Usage example
 */
class HuffmanDemo {
    public static void main(String[] args) {
        String text = "huffman coding example";
        
        // Calculate frequencies
        Map<Character, Integer> freqMap = new HashMap<>();
        for (char ch : text.toCharArray()) {
            freqMap.put(ch, freqMap.getOrDefault(ch, 0) + 1);
        }
        
        HuffmanCoding huffman = new HuffmanCoding();
        
        // Build tree and generate codes
        Node root = huffman.buildHuffmanTree(freqMap);
        Map<Character, String> codes = huffman.generateCodes(root);
        
        System.out.println("Codes: " + codes);
        
        // Encode
        String encoded = huffman.encode(text, codes);
        System.out.println("Encoded: " + encoded);
        
        // Decode
        String decoded = huffman.decode(encoded, root);
        System.out.println("Decoded: " + decoded);
    }
}
```

---

## Real-World Data Engineering Applications

### 1. Task Scheduling in Spark

```java
/**
 * Schedule Spark tasks to minimize total execution time
 */
class SparkTaskScheduler {
    
    static class Task {
        String id;
        int duration;
        int priority;
        
        Task(String id, int duration, int priority) {
            this.id = id;
            this.duration = duration;
            this.priority = priority;
        }
    }
    
    /**
     * Schedule tasks by priority (greedy)
     */
    public List<Task> scheduleTasks(List<Task> tasks) {
        // Sort by priority (higher first)
        tasks.sort((a, b) -> Integer.compare(b.priority, a.priority));
        return tasks;
    }
}
```

### 2. Data Compression in Storage

```java
/**
 * Compress data before storing in S3
 */
class DataCompressor {
    
    public byte[] compressWithHuffman(String data) {
        // Calculate frequencies
        Map<Character, Integer> freqMap = new HashMap<>();
        for (char ch : data.toCharArray()) {
            freqMap.put(ch, freqMap.getOrDefault(ch, 0) + 1);
        }
        
        // Build Huffman tree
        HuffmanCoding huffman = new HuffmanCoding();
        HuffmanCoding.Node root = huffman.buildHuffmanTree(freqMap);
        Map<Character, String> codes = huffman.generateCodes(root);
        
        // Encode
        String encoded = huffman.encode(data, codes);
        
        // Convert to bytes (actual implementation would be more complex)
        return encoded.getBytes();
    }
}
```

---

## 🎯 Interview Tips

### Recognizing Greedy Problems

**Keywords:**
- "Minimum/Maximum"
- "Optimal"
- "Scheduling"
- "Interval"

**Patterns:**
- Sorting helps
- Local choice leads to global optimum
- No need to reconsider past choices

### Proving Greedy is Correct

1. **Greedy choice property:** Show local optimum leads to global
2. **Optimal substructure:** Problem has optimal subproblems
3. **Exchange argument:** Show greedy solution is at least as good as any other

### Common Mistakes

1. **Assuming greedy always works:**
   ```java
   // Coin change with coins [1, 3, 4] and amount 6
   // Greedy: 4 + 1 + 1 = 3 coins
   // Optimal: 3 + 3 = 2 coins
   // Greedy FAILS!
   ```

2. **Wrong sorting criteria:**
   ```java
   // ❌ Wrong - sort by start time for activity selection
   Arrays.sort(activities, (a, b) -> a.start - b.start);
   
   // ✅ Correct - sort by end time
   Arrays.sort(activities, (a, b) -> a.end - b.end);
   ```

---

## 📊 Complexity Summary

| Problem | Time | Space | Key Insight |
|---------|------|-------|-------------|
| Activity Selection | O(n log n) | O(1) | Sort by end time |
| Jump Game | O(n) | O(1) | Track max reach |
| Gas Station | O(n) | O(1) | Reset start on failure |
| Task Scheduler | O(n) | O(1) | Greedy fill slots |
| Huffman Coding | O(n log n) | O(n) | Min heap |

---

**Next:** [String Algorithms](./12-String-Algorithms.md)
