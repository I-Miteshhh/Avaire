# LinkedList - Singly, Doubly, Circular

**Difficulty:** Fundamental  
**Learning Time:** 1-2 weeks  
**Interview Frequency:** ⭐⭐⭐⭐⭐ (Very High)

---

## 📚 Table of Contents

1. [Singly Linked List](#singly-linked-list)
2. [Doubly Linked List](#doubly-linked-list)
3. [Circular Linked List](#circular-linked-list)
4. [Time & Space Complexity](#time--space-complexity)
5. [Interview Problems](#interview-problems)
6. [Advanced Techniques](#advanced-techniques)

---

## Singly Linked List

### Characteristics
```
✅ Dynamic size (grow/shrink as needed)
✅ Efficient insertion/deletion at head: O(1)
✅ No memory waste for unused capacity
✅ No need to resize like arrays
❌ No random access (O(n) to access middle)
❌ Extra memory for pointers
❌ Not cache-friendly (scattered in memory)
```

### Node Structure

```java
public class ListNode {
    int val;
    ListNode next;
    
    public ListNode(int val) {
        this.val = val;
        this.next = null;
    }
    
    public ListNode(int val, ListNode next) {
        this.val = val;
        this.next = next;
    }
}
```

### Custom Singly Linked List Implementation

```java
/**
 * Production-Grade Singly Linked List
 */
public class SinglyLinkedList<T> {
    
    private static class Node<T> {
        T data;
        Node<T> next;
        
        Node(T data) {
            this.data = data;
            this.next = null;
        }
    }
    
    private Node<T> head;
    private Node<T> tail;
    private int size;
    
    public SinglyLinkedList() {
        this.head = null;
        this.tail = null;
        this.size = 0;
    }
    
    /**
     * Add at beginning: O(1)
     */
    public void addFirst(T data) {
        Node<T> newNode = new Node<>(data);
        newNode.next = head;
        head = newNode;
        
        if (tail == null) {
            tail = newNode;
        }
        
        size++;
    }
    
    /**
     * Add at end: O(1) with tail pointer
     */
    public void addLast(T data) {
        Node<T> newNode = new Node<>(data);
        
        if (tail == null) {
            head = tail = newNode;
        } else {
            tail.next = newNode;
            tail = newNode;
        }
        
        size++;
    }
    
    /**
     * Add at index: O(n)
     */
    public void add(int index, T data) {
        checkIndexForAdd(index);
        
        if (index == 0) {
            addFirst(data);
            return;
        }
        
        if (index == size) {
            addLast(data);
            return;
        }
        
        Node<T> newNode = new Node<>(data);
        Node<T> prev = getNode(index - 1);
        
        newNode.next = prev.next;
        prev.next = newNode;
        
        size++;
    }
    
    /**
     * Remove first: O(1)
     */
    public T removeFirst() {
        if (head == null) {
            throw new NoSuchElementException("List is empty");
        }
        
        T data = head.data;
        head = head.next;
        
        if (head == null) {
            tail = null;
        }
        
        size--;
        return data;
    }
    
    /**
     * Remove last: O(n) - need to traverse to second-last node
     */
    public T removeLast() {
        if (head == null) {
            throw new NoSuchElementException("List is empty");
        }
        
        if (head == tail) {
            T data = head.data;
            head = tail = null;
            size--;
            return data;
        }
        
        // Find second-last node
        Node<T> current = head;
        while (current.next != tail) {
            current = current.next;
        }
        
        T data = tail.data;
        tail = current;
        tail.next = null;
        size--;
        
        return data;
    }
    
    /**
     * Remove at index: O(n)
     */
    public T remove(int index) {
        checkIndex(index);
        
        if (index == 0) {
            return removeFirst();
        }
        
        Node<T> prev = getNode(index - 1);
        Node<T> toRemove = prev.next;
        T data = toRemove.data;
        
        prev.next = toRemove.next;
        
        if (toRemove == tail) {
            tail = prev;
        }
        
        size--;
        return data;
    }
    
    /**
     * Get element at index: O(n)
     */
    public T get(int index) {
        checkIndex(index);
        return getNode(index).data;
    }
    
    /**
     * Set element at index: O(n)
     */
    public T set(int index, T data) {
        checkIndex(index);
        Node<T> node = getNode(index);
        T oldData = node.data;
        node.data = data;
        return oldData;
    }
    
    /**
     * Get node at index: O(n)
     */
    private Node<T> getNode(int index) {
        Node<T> current = head;
        for (int i = 0; i < index; i++) {
            current = current.next;
        }
        return current;
    }
    
    /**
     * Find index of element: O(n)
     */
    public int indexOf(T data) {
        Node<T> current = head;
        int index = 0;
        
        while (current != null) {
            if ((data == null && current.data == null) || 
                (data != null && data.equals(current.data))) {
                return index;
            }
            current = current.next;
            index++;
        }
        
        return -1;
    }
    
    /**
     * Check if contains element: O(n)
     */
    public boolean contains(T data) {
        return indexOf(data) >= 0;
    }
    
    /**
     * Size: O(1)
     */
    public int size() {
        return size;
    }
    
    /**
     * Is empty: O(1)
     */
    public boolean isEmpty() {
        return size == 0;
    }
    
    /**
     * Clear: O(1) - Java GC handles rest
     */
    public void clear() {
        head = tail = null;
        size = 0;
    }
    
    /**
     * Reverse list: O(n)
     */
    public void reverse() {
        Node<T> prev = null;
        Node<T> current = head;
        tail = head;
        
        while (current != null) {
            Node<T> next = current.next;
            current.next = prev;
            prev = current;
            current = next;
        }
        
        head = prev;
    }
    
    private void checkIndex(int index) {
        if (index < 0 || index >= size) {
            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
        }
    }
    
    private void checkIndexForAdd(int index) {
        if (index < 0 || index > size) {
            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
        }
    }
    
    @Override
    public String toString() {
        if (head == null) {
            return "[]";
        }
        
        StringBuilder sb = new StringBuilder("[");
        Node<T> current = head;
        
        while (current != null) {
            sb.append(current.data);
            if (current.next != null) {
                sb.append(" -> ");
            }
            current = current.next;
        }
        
        sb.append("]");
        return sb.toString();
    }
}
```

---

## Doubly Linked List

### Characteristics
```
✅ Can traverse backward (has prev pointer)
✅ Efficient insertion/deletion at both ends: O(1)
✅ Remove last in O(1) (unlike singly linked list)
❌ Extra memory for prev pointer
❌ More complex to maintain
```

### Node Structure

```java
public class DoublyListNode<T> {
    T data;
    DoublyListNode<T> prev;
    DoublyListNode<T> next;
    
    public DoublyListNode(T data) {
        this.data = data;
        this.prev = null;
        this.next = null;
    }
}
```

### Custom Doubly Linked List Implementation

```java
/**
 * Production-Grade Doubly Linked List
 */
public class DoublyLinkedList<T> {
    
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
    
    public DoublyLinkedList() {
        this.head = null;
        this.tail = null;
        this.size = 0;
    }
    
    /**
     * Add at beginning: O(1)
     */
    public void addFirst(T data) {
        Node<T> newNode = new Node<>(data);
        
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
     * Add at end: O(1)
     */
    public void addLast(T data) {
        Node<T> newNode = new Node<>(data);
        
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
     * Add at index: O(n)
     */
    public void add(int index, T data) {
        checkIndexForAdd(index);
        
        if (index == 0) {
            addFirst(data);
            return;
        }
        
        if (index == size) {
            addLast(data);
            return;
        }
        
        Node<T> newNode = new Node<>(data);
        Node<T> current = getNode(index);
        
        newNode.next = current;
        newNode.prev = current.prev;
        current.prev.next = newNode;
        current.prev = newNode;
        
        size++;
    }
    
    /**
     * Remove first: O(1)
     */
    public T removeFirst() {
        if (head == null) {
            throw new NoSuchElementException("List is empty");
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
     * Remove last: O(1) - advantage over singly linked list!
     */
    public T removeLast() {
        if (tail == null) {
            throw new NoSuchElementException("List is empty");
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
     * Remove at index: O(n)
     */
    public T remove(int index) {
        checkIndex(index);
        
        if (index == 0) {
            return removeFirst();
        }
        
        if (index == size - 1) {
            return removeLast();
        }
        
        Node<T> toRemove = getNode(index);
        T data = toRemove.data;
        
        toRemove.prev.next = toRemove.next;
        toRemove.next.prev = toRemove.prev;
        
        size--;
        return data;
    }
    
    /**
     * Get element: O(n) - but optimized to search from closer end
     */
    public T get(int index) {
        checkIndex(index);
        return getNode(index).data;
    }
    
    /**
     * Get node at index: O(n) - optimized
     */
    private Node<T> getNode(int index) {
        // Search from head or tail, whichever is closer
        if (index < size / 2) {
            Node<T> current = head;
            for (int i = 0; i < index; i++) {
                current = current.next;
            }
            return current;
        } else {
            Node<T> current = tail;
            for (int i = size - 1; i > index; i--) {
                current = current.prev;
            }
            return current;
        }
    }
    
    /**
     * Reverse list: O(n)
     */
    public void reverse() {
        Node<T> current = head;
        Node<T> temp = null;
        
        while (current != null) {
            temp = current.prev;
            current.prev = current.next;
            current.next = temp;
            current = current.prev;
        }
        
        if (temp != null) {
            Node<T> oldHead = head;
            head = tail;
            tail = oldHead;
        }
    }
    
    public int size() {
        return size;
    }
    
    public boolean isEmpty() {
        return size == 0;
    }
    
    private void checkIndex(int index) {
        if (index < 0 || index >= size) {
            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
        }
    }
    
    private void checkIndexForAdd(int index) {
        if (index < 0 || index > size) {
            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
        }
    }
    
    @Override
    public String toString() {
        if (head == null) {
            return "[]";
        }
        
        StringBuilder sb = new StringBuilder("[");
        Node<T> current = head;
        
        while (current != null) {
            sb.append(current.data);
            if (current.next != null) {
                sb.append(" <-> ");
            }
            current = current.next;
        }
        
        sb.append("]");
        return sb.toString();
    }
}
```

---

## Circular Linked List

### Characteristics
```
✅ Last node points back to first node (circular)
✅ Useful for round-robin scheduling
✅ Can start from any node
❌ Need special care to avoid infinite loops
❌ Harder to detect end
```

### Implementation

```java
public class CircularLinkedList<T> {
    
    private static class Node<T> {
        T data;
        Node<T> next;
        
        Node(T data) {
            this.data = data;
        }
    }
    
    private Node<T> tail;  // Points to last node (whose next is first)
    private int size;
    
    public CircularLinkedList() {
        this.tail = null;
        this.size = 0;
    }
    
    /**
     * Add at end: O(1)
     */
    public void add(T data) {
        Node<T> newNode = new Node<>(data);
        
        if (tail == null) {
            newNode.next = newNode;  // Points to itself
            tail = newNode;
        } else {
            newNode.next = tail.next;  // New node points to head
            tail.next = newNode;       // Old tail points to new node
            tail = newNode;            // Update tail
        }
        
        size++;
    }
    
    /**
     * Add at beginning: O(1)
     */
    public void addFirst(T data) {
        Node<T> newNode = new Node<>(data);
        
        if (tail == null) {
            newNode.next = newNode;
            tail = newNode;
        } else {
            newNode.next = tail.next;
            tail.next = newNode;
            // Don't update tail!
        }
        
        size++;
    }
    
    /**
     * Remove first: O(1)
     */
    public T removeFirst() {
        if (tail == null) {
            throw new NoSuchElementException("List is empty");
        }
        
        Node<T> head = tail.next;
        T data = head.data;
        
        if (head == tail) {
            tail = null;
        } else {
            tail.next = head.next;
        }
        
        size--;
        return data;
    }
    
    /**
     * Traverse list: O(n)
     */
    public void traverse() {
        if (tail == null) {
            System.out.println("[]");
            return;
        }
        
        Node<T> current = tail.next;  // Start from head
        System.out.print("[");
        
        do {
            System.out.print(current.data);
            if (current.next != tail.next) {
                System.out.print(" -> ");
            }
            current = current.next;
        } while (current != tail.next);
        
        System.out.println("] (circular)");
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

## Time & Space Complexity

### Singly Linked List

| Operation | Time Complexity | Notes |
|-----------|-----------------|-------|
| **Access** | O(n) | Must traverse from head |
| **Search** | O(n) | Linear search |
| **Insert at head** | O(1) | Just update head |
| **Insert at tail** | O(1) | If tail pointer exists |
| **Insert at index** | O(n) | Need to traverse |
| **Delete at head** | O(1) | Just update head |
| **Delete at tail** | O(n) | Need to find second-last |
| **Delete at index** | O(n) | Need to traverse |

### Doubly Linked List

| Operation | Time Complexity | Notes |
|-----------|-----------------|-------|
| **Access** | O(n) | Can search from closer end (optimization) |
| **Search** | O(n) | Linear search |
| **Insert at head** | O(1) | Update head and prev |
| **Insert at tail** | O(1) | Update tail and prev |
| **Insert at index** | O(n) | Need to traverse |
| **Delete at head** | O(1) | Update head and prev |
| **Delete at tail** | O(1) | **Better than singly!** |
| **Delete at index** | O(n) | Need to traverse |

**Space Complexity:**
- Singly Linked List: O(n) — one pointer per node
- Doubly Linked List: O(n) — two pointers per node (more overhead)

---

## Interview Problems

### Problem 1: Reverse Linked List (LeetCode 206)

```java
/**
 * Reverse singly linked list
 * 
 * Example: 1 -> 2 -> 3 -> 4 -> 5 → 5 -> 4 -> 3 -> 2 -> 1
 * 
 * Time: O(n), Space: O(1)
 */

// Iterative approach
public ListNode reverseList(ListNode head) {
    ListNode prev = null;
    ListNode current = head;
    
    while (current != null) {
        ListNode next = current.next;  // Save next
        current.next = prev;           // Reverse link
        prev = current;                // Move prev forward
        current = next;                // Move current forward
    }
    
    return prev;
}

// Recursive approach
public ListNode reverseListRecursive(ListNode head) {
    if (head == null || head.next == null) {
        return head;
    }
    
    ListNode newHead = reverseListRecursive(head.next);
    head.next.next = head;
    head.next = null;
    
    return newHead;
}
```

### Problem 2: Detect Cycle (LeetCode 141)

```java
/**
 * Detect if linked list has cycle
 * 
 * Floyd's Cycle Detection (Tortoise and Hare)
 * Time: O(n), Space: O(1)
 */
public boolean hasCycle(ListNode head) {
    if (head == null) return false;
    
    ListNode slow = head;
    ListNode fast = head;
    
    while (fast != null && fast.next != null) {
        slow = slow.next;
        fast = fast.next.next;
        
        if (slow == fast) {
            return true;  // Cycle detected
        }
    }
    
    return false;
}
```

### Problem 3: Find Cycle Start (LeetCode 142)

```java
/**
 * Find node where cycle begins
 * 
 * Time: O(n), Space: O(1)
 */
public ListNode detectCycle(ListNode head) {
    if (head == null) return null;
    
    // Phase 1: Detect cycle
    ListNode slow = head;
    ListNode fast = head;
    boolean hasCycle = false;
    
    while (fast != null && fast.next != null) {
        slow = slow.next;
        fast = fast.next.next;
        
        if (slow == fast) {
            hasCycle = true;
            break;
        }
    }
    
    if (!hasCycle) return null;
    
    // Phase 2: Find cycle start
    slow = head;
    while (slow != fast) {
        slow = slow.next;
        fast = fast.next;
    }
    
    return slow;
}
```

### Problem 4: Merge Two Sorted Lists (LeetCode 21)

```java
/**
 * Merge two sorted linked lists
 * 
 * Example: 1->2->4, 1->3->4 → 1->1->2->3->4->4
 * 
 * Time: O(m + n), Space: O(1)
 */
public ListNode mergeTwoLists(ListNode l1, ListNode l2) {
    ListNode dummy = new ListNode(0);
    ListNode current = dummy;
    
    while (l1 != null && l2 != null) {
        if (l1.val < l2.val) {
            current.next = l1;
            l1 = l1.next;
        } else {
            current.next = l2;
            l2 = l2.next;
        }
        current = current.next;
    }
    
    // Attach remaining nodes
    current.next = (l1 != null) ? l1 : l2;
    
    return dummy.next;
}

// Recursive approach
public ListNode mergeTwoListsRecursive(ListNode l1, ListNode l2) {
    if (l1 == null) return l2;
    if (l2 == null) return l1;
    
    if (l1.val < l2.val) {
        l1.next = mergeTwoListsRecursive(l1.next, l2);
        return l1;
    } else {
        l2.next = mergeTwoListsRecursive(l1, l2.next);
        return l2;
    }
}
```

### Problem 5: Remove Nth Node from End (LeetCode 19)

```java
/**
 * Remove nth node from end of list
 * 
 * Example: 1->2->3->4->5, n=2 → 1->2->3->5
 * 
 * Time: O(n), Space: O(1)
 */
public ListNode removeNthFromEnd(ListNode head, int n) {
    ListNode dummy = new ListNode(0);
    dummy.next = head;
    
    ListNode fast = dummy;
    ListNode slow = dummy;
    
    // Move fast n+1 steps ahead
    for (int i = 0; i <= n; i++) {
        fast = fast.next;
    }
    
    // Move both until fast reaches end
    while (fast != null) {
        slow = slow.next;
        fast = fast.next;
    }
    
    // Remove node
    slow.next = slow.next.next;
    
    return dummy.next;
}
```

### Problem 6: Find Middle Node (LeetCode 876)

```java
/**
 * Find middle node of linked list
 * If two middle nodes, return second middle
 * 
 * Example: 1->2->3->4->5 → 3
 *          1->2->3->4 → 3
 * 
 * Time: O(n), Space: O(1)
 */
public ListNode middleNode(ListNode head) {
    ListNode slow = head;
    ListNode fast = head;
    
    while (fast != null && fast.next != null) {
        slow = slow.next;
        fast = fast.next.next;
    }
    
    return slow;
}
```

### Problem 7: Palindrome Linked List (LeetCode 234)

```java
/**
 * Check if linked list is palindrome
 * 
 * Example: 1->2->2->1 → true
 * 
 * Time: O(n), Space: O(1)
 */
public boolean isPalindrome(ListNode head) {
    if (head == null || head.next == null) {
        return true;
    }
    
    // Find middle
    ListNode slow = head;
    ListNode fast = head;
    
    while (fast.next != null && fast.next.next != null) {
        slow = slow.next;
        fast = fast.next.next;
    }
    
    // Reverse second half
    ListNode secondHalf = reverseList(slow.next);
    
    // Compare first half and reversed second half
    ListNode p1 = head;
    ListNode p2 = secondHalf;
    
    while (p2 != null) {
        if (p1.val != p2.val) {
            return false;
        }
        p1 = p1.next;
        p2 = p2.next;
    }
    
    return true;
}

private ListNode reverseList(ListNode head) {
    ListNode prev = null;
    ListNode current = head;
    
    while (current != null) {
        ListNode next = current.next;
        current.next = prev;
        prev = current;
        current = next;
    }
    
    return prev;
}
```

---

## Advanced Techniques

### 1. Fast and Slow Pointers (Floyd's Algorithm)

```java
/**
 * Use cases:
 * - Detect cycle
 * - Find middle node
 * - Find nth node from end
 */

// Find middle
public ListNode findMiddle(ListNode head) {
    ListNode slow = head;
    ListNode fast = head;
    
    while (fast != null && fast.next != null) {
        slow = slow.next;
        fast = fast.next.next;
    }
    
    return slow;
}
```

### 2. Dummy Node Trick

```java
/**
 * Use dummy node to simplify edge cases
 * - Removing head node
 * - Merging lists
 * - Inserting at beginning
 */

public ListNode removeElements(ListNode head, int val) {
    ListNode dummy = new ListNode(0);
    dummy.next = head;
    
    ListNode current = dummy;
    
    while (current.next != null) {
        if (current.next.val == val) {
            current.next = current.next.next;
        } else {
            current = current.next;
        }
    }
    
    return dummy.next;
}
```

### 3. Recursion for Linked Lists

```java
/**
 * Recursive patterns for linked lists
 */

// Reverse list recursively
public ListNode reverse(ListNode head) {
    if (head == null || head.next == null) {
        return head;
    }
    
    ListNode newHead = reverse(head.next);
    head.next.next = head;
    head.next = null;
    return newHead;
}

// Print list in reverse order
public void printReverse(ListNode head) {
    if (head == null) return;
    
    printReverse(head.next);
    System.out.print(head.val + " ");
}
```

---

## 🎯 Interview Tips

### When to Use Linked List vs Array

**Use Linked List:**
- ✅ Frequent insertions/deletions at beginning
- ✅ Unknown size or frequently changing size
- ✅ Don't need random access
- ✅ Memory fragmentation okay

**Use Array/ArrayList:**
- ✅ Need random access (O(1) by index)
- ✅ Fixed or predictable size
- ✅ Frequent access operations
- ✅ Memory locality important (cache-friendly)

### Common Patterns

1. **Two Pointers**: slow/fast for middle, cycle detection
2. **Dummy Node**: Simplify edge cases
3. **Recursion**: Natural for linked lists
4. **Reverse**: Many problems involve reversing
5. **Merge**: Combine sorted lists

### Common Mistakes

```java
// ❌ BAD: Losing reference to next node
current.next = newNode;
current = current.next.next;  // Lost reference!

// ✅ GOOD: Save reference first
ListNode next = current.next;
current.next = newNode;
newNode.next = next;

// ❌ BAD: Null pointer exception
while (fast.next.next != null)  // Crash if fast.next is null

// ✅ GOOD: Check both conditions
while (fast != null && fast.next != null)
```

---

**Next:** [Stack and Queue](./03-Stack-and-Queue.md) — Array-based and linked-list-based implementations
