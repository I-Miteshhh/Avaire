# Stack and Queue

**Difficulty:** Fundamental  
**Learning Time:** 1 week  
**Interview Frequency:** ⭐⭐⭐⭐⭐ (Very High)

---

## 📚 Table of Contents

1. [Stack](#stack)
2. [Queue](#queue)
3. [Custom Implementations](#custom-implementations)
4. [Interview Problems](#interview-problems)
5. [Real-World Use Cases](#real-world-use-cases)

---

## Stack

### Characteristics (LIFO - Last In First Out)

```
✅ O(1) push, pop, peek
✅ Simple and efficient
✅ Great for function calls, undo/redo
❌ No random access (can only access top)
❌ Fixed size (if array-based)
```

### Java Stack API

```java
Stack<Integer> stack = new Stack<>();

// Basic operations
stack.push(10);           // Add to top: O(1)
int top = stack.pop();    // Remove from top: O(1)
int peek = stack.peek();  // View top without removing: O(1)
boolean isEmpty = stack.isEmpty();
int size = stack.size();

// Search (from top, 1-indexed)
int position = stack.search(10);  // O(n)
```

⚠️ **Note:** `Stack` extends `Vector` (legacy, synchronized). For modern code, use `Deque`:

```java
Deque<Integer> stack = new ArrayDeque<>();
stack.push(10);
int top = stack.pop();
int peek = stack.peek();
```

---

## Custom Stack Implementation

### Array-Based Stack

```java
/**
 * Fixed-size stack using array
 * 
 * Time Complexity: O(1) for push, pop, peek
 * Space Complexity: O(n)
 */
public class ArrayStack<T> {
    private static final int DEFAULT_CAPACITY = 10;
    
    private Object[] elements;
    private int top;  // Index of top element
    private int capacity;
    
    @SuppressWarnings("unchecked")
    public ArrayStack() {
        this.capacity = DEFAULT_CAPACITY;
        this.elements = new Object[capacity];
        this.top = -1;  // Empty stack
    }
    
    @SuppressWarnings("unchecked")
    public ArrayStack(int capacity) {
        this.capacity = capacity;
        this.elements = new Object[capacity];
        this.top = -1;
    }
    
    /**
     * Push element onto stack: O(1)
     */
    public void push(T element) {
        if (isFull()) {
            throw new StackOverflowError("Stack is full");
        }
        
        elements[++top] = element;
    }
    
    /**
     * Pop element from stack: O(1)
     */
    @SuppressWarnings("unchecked")
    public T pop() {
        if (isEmpty()) {
            throw new EmptyStackException();
        }
        
        T element = (T) elements[top];
        elements[top] = null;  // Help GC
        top--;
        
        return element;
    }
    
    /**
     * Peek at top element: O(1)
     */
    @SuppressWarnings("unchecked")
    public T peek() {
        if (isEmpty()) {
            throw new EmptyStackException();
        }
        
        return (T) elements[top];
    }
    
    public boolean isEmpty() {
        return top == -1;
    }
    
    public boolean isFull() {
        return top == capacity - 1;
    }
    
    public int size() {
        return top + 1;
    }
    
    public void clear() {
        while (!isEmpty()) {
            pop();
        }
    }
}
```

### Dynamic Array-Based Stack (Auto-Resizing)

```java
/**
 * Dynamic stack with automatic resizing
 */
public class DynamicArrayStack<T> {
    private static final int DEFAULT_CAPACITY = 10;
    private static final double GROWTH_FACTOR = 1.5;
    
    private Object[] elements;
    private int top;
    private int capacity;
    
    @SuppressWarnings("unchecked")
    public DynamicArrayStack() {
        this.capacity = DEFAULT_CAPACITY;
        this.elements = new Object[capacity];
        this.top = -1;
    }
    
    /**
     * Push with automatic resizing: Amortized O(1)
     */
    public void push(T element) {
        if (isFull()) {
            resize();
        }
        
        elements[++top] = element;
    }
    
    /**
     * Resize array: O(n)
     */
    @SuppressWarnings("unchecked")
    private void resize() {
        int newCapacity = (int) (capacity * GROWTH_FACTOR);
        Object[] newElements = new Object[newCapacity];
        
        System.arraycopy(elements, 0, newElements, 0, capacity);
        
        elements = newElements;
        capacity = newCapacity;
    }
    
    @SuppressWarnings("unchecked")
    public T pop() {
        if (isEmpty()) {
            throw new EmptyStackException();
        }
        
        T element = (T) elements[top];
        elements[top] = null;
        top--;
        
        return element;
    }
    
    @SuppressWarnings("unchecked")
    public T peek() {
        if (isEmpty()) {
            throw new EmptyStackException();
        }
        
        return (T) elements[top];
    }
    
    public boolean isEmpty() {
        return top == -1;
    }
    
    private boolean isFull() {
        return top == capacity - 1;
    }
    
    public int size() {
        return top + 1;
    }
}
```

### LinkedList-Based Stack

```java
/**
 * Stack using linked list
 * No size limit, O(1) operations
 */
public class LinkedStack<T> {
    
    private static class Node<T> {
        T data;
        Node<T> next;
        
        Node(T data) {
            this.data = data;
        }
    }
    
    private Node<T> top;
    private int size;
    
    public LinkedStack() {
        this.top = null;
        this.size = 0;
    }
    
    /**
     * Push: O(1)
     */
    public void push(T element) {
        Node<T> newNode = new Node<>(element);
        newNode.next = top;
        top = newNode;
        size++;
    }
    
    /**
     * Pop: O(1)
     */
    public T pop() {
        if (isEmpty()) {
            throw new EmptyStackException();
        }
        
        T data = top.data;
        top = top.next;
        size--;
        
        return data;
    }
    
    /**
     * Peek: O(1)
     */
    public T peek() {
        if (isEmpty()) {
            throw new EmptyStackException();
        }
        
        return top.data;
    }
    
    public boolean isEmpty() {
        return top == null;
    }
    
    public int size() {
        return size;
    }
    
    public void clear() {
        top = null;
        size = 0;
    }
}
```

---

## Queue

### Characteristics (FIFO - First In First Out)

```
✅ O(1) enqueue, dequeue
✅ Fair processing (first come first served)
✅ Great for BFS, task scheduling
❌ No random access
❌ Circular array implementation complex
```

### Java Queue API

```java
Queue<Integer> queue = new LinkedList<>();

// Basic operations
queue.offer(10);          // Add to rear: O(1)
int front = queue.poll(); // Remove from front: O(1)
int peek = queue.peek();  // View front without removing: O(1)
boolean isEmpty = queue.isEmpty();
int size = queue.size();
```

**Better Alternative:** Use `Deque` interface

```java
Deque<Integer> queue = new ArrayDeque<>();
queue.offer(10);          // Same as add()
int front = queue.poll(); // Same as remove()
int peek = queue.peek();  // Same as element()
```

---

## Custom Queue Implementation

### Array-Based Queue (Circular Buffer)

```java
/**
 * Circular queue using array
 * Efficient O(1) operations without shifting
 */
public class CircularArrayQueue<T> {
    private static final int DEFAULT_CAPACITY = 10;
    
    private Object[] elements;
    private int front;
    private int rear;
    private int size;
    private int capacity;
    
    @SuppressWarnings("unchecked")
    public CircularArrayQueue() {
        this.capacity = DEFAULT_CAPACITY;
        this.elements = new Object[capacity];
        this.front = 0;
        this.rear = -1;
        this.size = 0;
    }
    
    /**
     * Enqueue: Add to rear: O(1)
     */
    public void enqueue(T element) {
        if (isFull()) {
            throw new IllegalStateException("Queue is full");
        }
        
        rear = (rear + 1) % capacity;  // Circular increment
        elements[rear] = element;
        size++;
    }
    
    /**
     * Dequeue: Remove from front: O(1)
     */
    @SuppressWarnings("unchecked")
    public T dequeue() {
        if (isEmpty()) {
            throw new NoSuchElementException("Queue is empty");
        }
        
        T element = (T) elements[front];
        elements[front] = null;  // Help GC
        front = (front + 1) % capacity;  // Circular increment
        size--;
        
        return element;
    }
    
    /**
     * Peek at front: O(1)
     */
    @SuppressWarnings("unchecked")
    public T peek() {
        if (isEmpty()) {
            throw new NoSuchElementException("Queue is empty");
        }
        
        return (T) elements[front];
    }
    
    public boolean isEmpty() {
        return size == 0;
    }
    
    public boolean isFull() {
        return size == capacity;
    }
    
    public int size() {
        return size;
    }
}
```

### Dynamic Circular Queue (Auto-Resizing)

```java
/**
 * Dynamic circular queue with automatic resizing
 */
public class DynamicCircularQueue<T> {
    private static final int DEFAULT_CAPACITY = 10;
    private static final double GROWTH_FACTOR = 1.5;
    
    private Object[] elements;
    private int front;
    private int rear;
    private int size;
    private int capacity;
    
    @SuppressWarnings("unchecked")
    public DynamicCircularQueue() {
        this.capacity = DEFAULT_CAPACITY;
        this.elements = new Object[capacity];
        this.front = 0;
        this.rear = -1;
        this.size = 0;
    }
    
    /**
     * Enqueue with auto-resize: Amortized O(1)
     */
    public void enqueue(T element) {
        if (isFull()) {
            resize();
        }
        
        rear = (rear + 1) % capacity;
        elements[rear] = element;
        size++;
    }
    
    /**
     * Resize array: O(n)
     */
    @SuppressWarnings("unchecked")
    private void resize() {
        int newCapacity = (int) (capacity * GROWTH_FACTOR);
        Object[] newElements = new Object[newCapacity];
        
        // Copy elements in order from front to rear
        for (int i = 0; i < size; i++) {
            newElements[i] = elements[(front + i) % capacity];
        }
        
        elements = newElements;
        front = 0;
        rear = size - 1;
        capacity = newCapacity;
    }
    
    @SuppressWarnings("unchecked")
    public T dequeue() {
        if (isEmpty()) {
            throw new NoSuchElementException("Queue is empty");
        }
        
        T element = (T) elements[front];
        elements[front] = null;
        front = (front + 1) % capacity;
        size--;
        
        return element;
    }
    
    @SuppressWarnings("unchecked")
    public T peek() {
        if (isEmpty()) {
            throw new NoSuchElementException("Queue is empty");
        }
        
        return (T) elements[front];
    }
    
    public boolean isEmpty() {
        return size == 0;
    }
    
    private boolean isFull() {
        return size == capacity;
    }
    
    public int size() {
        return size;
    }
}
```

### LinkedList-Based Queue

```java
/**
 * Queue using linked list
 * No size limit, O(1) operations
 */
public class LinkedQueue<T> {
    
    private static class Node<T> {
        T data;
        Node<T> next;
        
        Node(T data) {
            this.data = data;
        }
    }
    
    private Node<T> front;
    private Node<T> rear;
    private int size;
    
    public LinkedQueue() {
        this.front = null;
        this.rear = null;
        this.size = 0;
    }
    
    /**
     * Enqueue: Add to rear: O(1)
     */
    public void enqueue(T element) {
        Node<T> newNode = new Node<>(element);
        
        if (rear == null) {
            front = rear = newNode;
        } else {
            rear.next = newNode;
            rear = newNode;
        }
        
        size++;
    }
    
    /**
     * Dequeue: Remove from front: O(1)
     */
    public T dequeue() {
        if (isEmpty()) {
            throw new NoSuchElementException("Queue is empty");
        }
        
        T data = front.data;
        front = front.next;
        
        if (front == null) {
            rear = null;
        }
        
        size--;
        return data;
    }
    
    /**
     * Peek: O(1)
     */
    public T peek() {
        if (isEmpty()) {
            throw new NoSuchElementException("Queue is empty");
        }
        
        return front.data;
    }
    
    public boolean isEmpty() {
        return front == null;
    }
    
    public int size() {
        return size;
    }
    
    public void clear() {
        front = rear = null;
        size = 0;
    }
}
```

---

## Interview Problems

### Problem 1: Valid Parentheses (LeetCode 20)

```java
/**
 * Check if string has valid parentheses
 * 
 * Example: "()[]{}" → true
 *          "(]" → false
 *          "([)]" → false
 * 
 * Time: O(n), Space: O(n)
 */
public boolean isValid(String s) {
    Stack<Character> stack = new Stack<>();
    
    for (char c : s.toCharArray()) {
        // Opening brackets
        if (c == '(' || c == '[' || c == '{') {
            stack.push(c);
        }
        // Closing brackets
        else {
            if (stack.isEmpty()) {
                return false;
            }
            
            char top = stack.pop();
            
            if (c == ')' && top != '(') return false;
            if (c == ']' && top != '[') return false;
            if (c == '}' && top != '{') return false;
        }
    }
    
    return stack.isEmpty();
}

// Alternative: Using map
public boolean isValidMap(String s) {
    Map<Character, Character> map = new HashMap<>();
    map.put(')', '(');
    map.put(']', '[');
    map.put('}', '{');
    
    Stack<Character> stack = new Stack<>();
    
    for (char c : s.toCharArray()) {
        if (map.containsKey(c)) {
            if (stack.isEmpty() || stack.pop() != map.get(c)) {
                return false;
            }
        } else {
            stack.push(c);
        }
    }
    
    return stack.isEmpty();
}
```

### Problem 2: Min Stack (LeetCode 155)

```java
/**
 * Stack with O(1) getMin() operation
 * 
 * Time: O(1) for all operations
 * Space: O(n)
 */
class MinStack {
    
    private Stack<Integer> stack;
    private Stack<Integer> minStack;
    
    public MinStack() {
        stack = new Stack<>();
        minStack = new Stack<>();
    }
    
    public void push(int val) {
        stack.push(val);
        
        if (minStack.isEmpty() || val <= minStack.peek()) {
            minStack.push(val);
        }
    }
    
    public void pop() {
        int val = stack.pop();
        
        if (val == minStack.peek()) {
            minStack.pop();
        }
    }
    
    public int top() {
        return stack.peek();
    }
    
    public int getMin() {
        return minStack.peek();
    }
}

// Alternative: Single stack with pairs
class MinStack2 {
    
    private Stack<int[]> stack;  // [value, currentMin]
    
    public MinStack2() {
        stack = new Stack<>();
    }
    
    public void push(int val) {
        if (stack.isEmpty()) {
            stack.push(new int[]{val, val});
        } else {
            int currentMin = Math.min(val, stack.peek()[1]);
            stack.push(new int[]{val, currentMin});
        }
    }
    
    public void pop() {
        stack.pop();
    }
    
    public int top() {
        return stack.peek()[0];
    }
    
    public int getMin() {
        return stack.peek()[1];
    }
}
```

### Problem 3: Evaluate Reverse Polish Notation (LeetCode 150)

```java
/**
 * Evaluate postfix expression
 * 
 * Example: ["2","1","+","3","*"] → ((2 + 1) * 3) = 9
 * 
 * Time: O(n), Space: O(n)
 */
public int evalRPN(String[] tokens) {
    Stack<Integer> stack = new Stack<>();
    
    for (String token : tokens) {
        if (isOperator(token)) {
            int b = stack.pop();
            int a = stack.pop();
            
            int result = applyOperator(a, b, token);
            stack.push(result);
        } else {
            stack.push(Integer.parseInt(token));
        }
    }
    
    return stack.pop();
}

private boolean isOperator(String token) {
    return token.equals("+") || token.equals("-") || 
           token.equals("*") || token.equals("/");
}

private int applyOperator(int a, int b, String op) {
    switch (op) {
        case "+": return a + b;
        case "-": return a - b;
        case "*": return a * b;
        case "/": return a / b;
        default: throw new IllegalArgumentException("Invalid operator: " + op);
    }
}
```

### Problem 4: Implement Queue using Stacks (LeetCode 232)

```java
/**
 * Implement queue using two stacks
 * 
 * Time: Amortized O(1) for all operations
 * Space: O(n)
 */
class MyQueue {
    
    private Stack<Integer> input;   // For enqueue
    private Stack<Integer> output;  // For dequeue
    
    public MyQueue() {
        input = new Stack<>();
        output = new Stack<>();
    }
    
    /**
     * Push to back of queue: O(1)
     */
    public void push(int x) {
        input.push(x);
    }
    
    /**
     * Remove from front: Amortized O(1)
     */
    public int pop() {
        peek();  // Ensure output stack has elements
        return output.pop();
    }
    
    /**
     * Get front element: Amortized O(1)
     */
    public int peek() {
        if (output.isEmpty()) {
            while (!input.isEmpty()) {
                output.push(input.pop());
            }
        }
        return output.peek();
    }
    
    public boolean empty() {
        return input.isEmpty() && output.isEmpty();
    }
}
```

### Problem 5: Implement Stack using Queues (LeetCode 225)

```java
/**
 * Implement stack using one queue
 * 
 * Time: O(1) pop/top, O(n) push
 * Space: O(n)
 */
class MyStack {
    
    private Queue<Integer> queue;
    
    public MyStack() {
        queue = new LinkedList<>();
    }
    
    /**
     * Push: O(n) - rotate queue
     */
    public void push(int x) {
        queue.offer(x);
        
        int size = queue.size();
        for (int i = 0; i < size - 1; i++) {
            queue.offer(queue.poll());
        }
    }
    
    /**
     * Pop: O(1)
     */
    public int pop() {
        return queue.poll();
    }
    
    /**
     * Top: O(1)
     */
    public int top() {
        return queue.peek();
    }
    
    public boolean empty() {
        return queue.isEmpty();
    }
}
```

### Problem 6: Daily Temperatures (LeetCode 739)

```java
/**
 * Find next warmer day for each temperature
 * 
 * Example: [73,74,75,71,69,72,76,73] → [1,1,4,2,1,1,0,0]
 * 
 * Time: O(n), Space: O(n)
 */
public int[] dailyTemperatures(int[] temperatures) {
    int n = temperatures.length;
    int[] result = new int[n];
    Stack<Integer> stack = new Stack<>();  // Store indices
    
    for (int i = 0; i < n; i++) {
        while (!stack.isEmpty() && temperatures[i] > temperatures[stack.peek()]) {
            int prevIndex = stack.pop();
            result[prevIndex] = i - prevIndex;
        }
        stack.push(i);
    }
    
    return result;
}
```

### Problem 7: Sliding Window Maximum (LeetCode 239)

```java
/**
 * Find maximum in each sliding window of size k
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
        
        // Remove smaller elements (not useful)
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

---

## Real-World Use Cases

### 1. Function Call Stack

```java
/**
 * Java uses stack for method calls
 */
public class CallStackExample {
    
    public static void main(String[] args) {
        methodA();
    }
    
    static void methodA() {
        System.out.println("A start");
        methodB();
        System.out.println("A end");
    }
    
    static void methodB() {
        System.out.println("B start");
        methodC();
        System.out.println("B end");
    }
    
    static void methodC() {
        System.out.println("C");
    }
}

/**
 * Call Stack:
 * 
 * [main]
 * [main, methodA]
 * [main, methodA, methodB]
 * [main, methodA, methodB, methodC]  <- Execute C
 * [main, methodA, methodB]           <- Return from C
 * [main, methodA]                    <- Return from B
 * [main]                             <- Return from A
 * []                                 <- Program ends
 */
```

### 2. Undo/Redo in Text Editors

```java
/**
 * Undo/Redo functionality
 */
public class TextEditor {
    
    private Stack<String> undoStack;
    private Stack<String> redoStack;
    private String currentText;
    
    public TextEditor() {
        undoStack = new Stack<>();
        redoStack = new Stack<>();
        currentText = "";
    }
    
    public void write(String text) {
        undoStack.push(currentText);
        currentText = text;
        redoStack.clear();  // Clear redo when new action
    }
    
    public void undo() {
        if (undoStack.isEmpty()) {
            return;
        }
        
        redoStack.push(currentText);
        currentText = undoStack.pop();
    }
    
    public void redo() {
        if (redoStack.isEmpty()) {
            return;
        }
        
        undoStack.push(currentText);
        currentText = redoStack.pop();
    }
    
    public String getText() {
        return currentText;
    }
}
```

### 3. Task Scheduling (Queue)

```java
/**
 * Simple task scheduler using queue
 */
public class TaskScheduler {
    
    private Queue<Task> taskQueue;
    
    public TaskScheduler() {
        taskQueue = new LinkedList<>();
    }
    
    public void addTask(Task task) {
        taskQueue.offer(task);
    }
    
    public void processTasks() {
        while (!taskQueue.isEmpty()) {
            Task task = taskQueue.poll();
            task.execute();
        }
    }
}

class Task {
    private String name;
    
    public Task(String name) {
        this.name = name;
    }
    
    public void execute() {
        System.out.println("Executing task: " + name);
    }
}
```

### 4. BFS (Queue) vs DFS (Stack)

```java
/**
 * Graph traversal
 */
public class GraphTraversal {
    
    /**
     * BFS using Queue
     */
    public void bfs(Graph graph, int start) {
        boolean[] visited = new boolean[graph.vertices];
        Queue<Integer> queue = new LinkedList<>();
        
        visited[start] = true;
        queue.offer(start);
        
        while (!queue.isEmpty()) {
            int vertex = queue.poll();
            System.out.print(vertex + " ");
            
            for (int neighbor : graph.getNeighbors(vertex)) {
                if (!visited[neighbor]) {
                    visited[neighbor] = true;
                    queue.offer(neighbor);
                }
            }
        }
    }
    
    /**
     * DFS using Stack (iterative)
     */
    public void dfs(Graph graph, int start) {
        boolean[] visited = new boolean[graph.vertices];
        Stack<Integer> stack = new Stack<>();
        
        stack.push(start);
        
        while (!stack.isEmpty()) {
            int vertex = stack.pop();
            
            if (!visited[vertex]) {
                visited[vertex] = true;
                System.out.print(vertex + " ");
                
                for (int neighbor : graph.getNeighbors(vertex)) {
                    if (!visited[neighbor]) {
                        stack.push(neighbor);
                    }
                }
            }
        }
    }
}
```

---

## 🎯 Interview Tips

### Stack vs Queue Decision Tree

**Use Stack when:**
- ✅ Need LIFO (Last In First Out) behavior
- ✅ Recursion simulation, backtracking
- ✅ Expression evaluation, syntax parsing
- ✅ Undo/redo functionality
- ✅ DFS traversal

**Use Queue when:**
- ✅ Need FIFO (First In First Out) behavior
- ✅ BFS traversal
- ✅ Task scheduling, job queuing
- ✅ Message buffering
- ✅ Level-order tree traversal

### Common Patterns

1. **Monotonic Stack**: Daily Temperatures, Next Greater Element
2. **Two Stacks**: Implement Queue using Stacks
3. **Stack for Parsing**: Valid Parentheses, Expression Evaluation
4. **Deque for Sliding Window**: Sliding Window Maximum

### Stack/Queue Complexity Summary

| Implementation | Push/Enqueue | Pop/Dequeue | Peek | Space |
|----------------|--------------|-------------|------|-------|
| Array Stack | O(1) | O(1) | O(1) | O(n) |
| Linked Stack | O(1) | O(1) | O(1) | O(n) |
| Circular Queue (Array) | O(1) | O(1) | O(1) | O(n) |
| Linked Queue | O(1) | O(1) | O(1) | O(n) |

---

**Next:** [Deque and PriorityQueue](./04-Deque-and-PriorityQueue.md) — Advanced queue variants
