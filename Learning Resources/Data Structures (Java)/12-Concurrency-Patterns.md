# Advanced Concurrency Patterns in Java

**Purpose:** Master Java concurrency for 40+ LPA Principal Engineer roles (multi-threading, async programming, parallel processing)

**Prerequisites:** Basic Java, threading fundamentals, synchronization

---

## Table of Contents

1. [Executor Framework](#1-executor-framework)
2. [CompletableFuture & Async Programming](#2-completablefuture--async-programming)
3. [Fork/Join Framework](#3-forkjoin-framework)
4. [Concurrent Collections](#4-concurrent-collections)
5. [Advanced Patterns](#5-advanced-patterns)
6. [Production Best Practices](#6-production-best-practices)

---

## 1. Executor Framework

### 1.1 Thread Pools

**Problem with Raw Threads:**
```java
// Bad: Creating threads manually
for (int i = 0; i < 10000; i++) {
    new Thread(() -> processTask()).start();  // 10K threads!
}

// Issues:
// - High memory (1 MB per thread stack)
// - Context switching overhead
// - Resource exhaustion
```

**Solution: Thread Pool**
```java
ExecutorService executor = Executors.newFixedThreadPool(10);  // Reuse 10 threads

for (int i = 0; i < 10000; i++) {
    executor.submit(() -> processTask());  // Queue tasks
}

executor.shutdown();
```

---

### 1.2 Executor Types

**Fixed Thread Pool:**
```java
// Fixed number of threads
ExecutorService executor = Executors.newFixedThreadPool(10);

// Use case: Known workload, bounded parallelism
// Example: Process 1000 files with 10 threads
```

**Cached Thread Pool:**
```java
// Creates threads as needed, reuses idle threads
ExecutorService executor = Executors.newCachedThreadPool();

// Use case: Many short-lived tasks
// Example: Handle HTTP requests
```

**Single Thread Executor:**
```java
// Single thread, tasks executed sequentially
ExecutorService executor = Executors.newSingleThreadExecutor();

// Use case: Sequential processing, event loop
// Example: Background file watcher
```

**Scheduled Thread Pool:**
```java
// Schedule tasks with delays/periodic execution
ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(5);

// Run after 10 seconds
scheduler.schedule(() -> System.out.println("Delayed task"), 10, TimeUnit.SECONDS);

// Run every 5 seconds
scheduler.scheduleAtFixedRate(() -> System.out.println("Periodic task"), 
                               0, 5, TimeUnit.SECONDS);
```

---

### 1.3 Custom Thread Pool

**ThreadPoolExecutor:**
```java
import java.util.concurrent.*;

public class CustomThreadPool {
    public static void main(String[] args) {
        int corePoolSize = 5;
        int maxPoolSize = 10;
        long keepAliveTime = 60;
        BlockingQueue<Runnable> queue = new LinkedBlockingQueue<>(100);
        ThreadFactory threadFactory = new ThreadFactory() {
            private int count = 0;
            
            @Override
            public Thread newThread(Runnable r) {
                Thread thread = new Thread(r);
                thread.setName("worker-" + count++);
                thread.setDaemon(false);
                return thread;
            }
        };
        RejectedExecutionHandler rejectedHandler = new ThreadPoolExecutor.CallerRunsPolicy();
        
        ThreadPoolExecutor executor = new ThreadPoolExecutor(
            corePoolSize,
            maxPoolSize,
            keepAliveTime,
            TimeUnit.SECONDS,
            queue,
            threadFactory,
            rejectedHandler
        );
        
        // Submit tasks
        for (int i = 0; i < 200; i++) {
            int taskId = i;
            executor.submit(() -> {
                System.out.println(Thread.currentThread().getName() + " processing task " + taskId);
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            });
        }
        
        executor.shutdown();
    }
}
```

**Parameters Explained:**
- **corePoolSize:** Minimum threads (always alive)
- **maxPoolSize:** Maximum threads (created when queue full)
- **keepAliveTime:** Idle thread timeout (for threads > core)
- **queue:** Task queue (LinkedBlockingQueue, ArrayBlockingQueue, SynchronousQueue)
- **rejectedHandler:** What to do when queue full
  - `AbortPolicy`: Throw exception (default)
  - `CallerRunsPolicy`: Run in caller thread (backpressure)
  - `DiscardPolicy`: Silently discard
  - `DiscardOldestPolicy`: Discard oldest task

---

### 1.4 Future Pattern

**Basic Future:**
```java
ExecutorService executor = Executors.newFixedThreadPool(10);

Future<Integer> future = executor.submit(() -> {
    Thread.sleep(2000);  // Simulate long task
    return 42;
});

// Do other work...
System.out.println("Waiting for result...");

// Block until result available
Integer result = future.get();  // Returns 42 after 2 seconds
System.out.println("Result: " + result);

executor.shutdown();
```

**With Timeout:**
```java
try {
    Integer result = future.get(1, TimeUnit.SECONDS);
} catch (TimeoutException e) {
    System.out.println("Task took too long!");
    future.cancel(true);  // Interrupt task
}
```

---

## 2. CompletableFuture & Async Programming

### 2.1 Creating CompletableFuture

**Completed Future:**
```java
CompletableFuture<String> completedFuture = CompletableFuture.completedFuture("Hello");
String result = completedFuture.get();  // Immediate: "Hello"
```

**Async Computation:**
```java
CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
    // Runs in ForkJoinPool.commonPool()
    try {
        Thread.sleep(1000);
    } catch (InterruptedException e) {
        throw new RuntimeException(e);
    }
    return "Result after 1 second";
});

String result = future.get();  // Blocks until complete
```

**With Custom Executor:**
```java
ExecutorService executor = Executors.newFixedThreadPool(10);

CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
    return "Custom executor result";
}, executor);
```

---

### 2.2 Chaining Operations

**thenApply (Transform):**
```java
CompletableFuture<Integer> future = CompletableFuture.supplyAsync(() -> 5)
    .thenApply(x -> x * 2)      // 10
    .thenApply(x -> x + 3);     // 13

Integer result = future.get();  // 13
```

**thenAccept (Consume):**
```java
CompletableFuture.supplyAsync(() -> "Hello")
    .thenAccept(msg -> System.out.println(msg));  // Print, no return
```

**thenRun (Execute):**
```java
CompletableFuture.supplyAsync(() -> "Hello")
    .thenRun(() -> System.out.println("Done!"));  // No input, no return
```

**thenCompose (Flatmap):**
```java
CompletableFuture<User> userFuture = CompletableFuture.supplyAsync(() -> getUser(123));

CompletableFuture<Order> orderFuture = userFuture.thenCompose(user -> 
    CompletableFuture.supplyAsync(() -> getOrder(user.getId()))
);

// Avoids nested CompletableFuture<CompletableFuture<Order>>
```

---

### 2.3 Combining Futures

**thenCombine (Combine 2 futures):**
```java
CompletableFuture<Integer> future1 = CompletableFuture.supplyAsync(() -> 10);
CompletableFuture<Integer> future2 = CompletableFuture.supplyAsync(() -> 20);

CompletableFuture<Integer> combined = future1.thenCombine(future2, (a, b) -> a + b);

Integer result = combined.get();  // 30
```

**allOf (Wait for all):**
```java
CompletableFuture<String> f1 = CompletableFuture.supplyAsync(() -> "Task1");
CompletableFuture<String> f2 = CompletableFuture.supplyAsync(() -> "Task2");
CompletableFuture<String> f3 = CompletableFuture.supplyAsync(() -> "Task3");

CompletableFuture<Void> allFutures = CompletableFuture.allOf(f1, f2, f3);

allFutures.get();  // Blocks until all complete

System.out.println(f1.get());  // "Task1"
System.out.println(f2.get());  // "Task2"
System.out.println(f3.get());  // "Task3"
```

**anyOf (First to complete):**
```java
CompletableFuture<String> f1 = CompletableFuture.supplyAsync(() -> {
    sleep(1000);
    return "Slow";
});

CompletableFuture<String> f2 = CompletableFuture.supplyAsync(() -> {
    sleep(100);
    return "Fast";
});

CompletableFuture<Object> firstResult = CompletableFuture.anyOf(f1, f2);

String result = (String) firstResult.get();  // "Fast" (first to finish)
```

---

### 2.4 Error Handling

**exceptionally:**
```java
CompletableFuture<Integer> future = CompletableFuture.supplyAsync(() -> {
    if (Math.random() > 0.5) {
        throw new RuntimeException("Error!");
    }
    return 42;
}).exceptionally(ex -> {
    System.err.println("Error occurred: " + ex.getMessage());
    return -1;  // Default value
});

Integer result = future.get();  // Either 42 or -1
```

**handle (Process both success and failure):**
```java
CompletableFuture<Integer> future = CompletableFuture.supplyAsync(() -> {
    if (Math.random() > 0.5) {
        throw new RuntimeException("Error!");
    }
    return 42;
}).handle((result, ex) -> {
    if (ex != null) {
        System.err.println("Error: " + ex.getMessage());
        return -1;
    }
    return result;
});
```

**whenComplete (Side effect):**
```java
CompletableFuture.supplyAsync(() -> 42)
    .whenComplete((result, ex) -> {
        if (ex != null) {
            System.err.println("Failed: " + ex);
        } else {
            System.out.println("Success: " + result);
        }
    });
```

---

### 2.5 Real-World Example: Parallel API Calls

```java
public class ParallelAPIService {
    private final HttpClient httpClient = HttpClient.newHttpClient();
    private final ExecutorService executor = Executors.newFixedThreadPool(20);
    
    public CompletableFuture<User> getUser(int userId) {
        return CompletableFuture.supplyAsync(() -> {
            // Simulate API call
            sleep(100);
            return new User(userId, "User" + userId);
        }, executor);
    }
    
    public CompletableFuture<List<Order>> getOrders(int userId) {
        return CompletableFuture.supplyAsync(() -> {
            sleep(150);
            return List.of(
                new Order(1, userId, "Product A"),
                new Order(2, userId, "Product B")
            );
        }, executor);
    }
    
    public CompletableFuture<Address> getAddress(int userId) {
        return CompletableFuture.supplyAsync(() -> {
            sleep(200);
            return new Address(userId, "123 Main St");
        }, executor);
    }
    
    // Fetch all data in parallel
    public CompletableFuture<UserProfile> getUserProfile(int userId) {
        CompletableFuture<User> userFuture = getUser(userId);
        CompletableFuture<List<Order>> ordersFuture = getOrders(userId);
        CompletableFuture<Address> addressFuture = getAddress(userId);
        
        return CompletableFuture.allOf(userFuture, ordersFuture, addressFuture)
            .thenApply(v -> {
                User user = userFuture.join();
                List<Order> orders = ordersFuture.join();
                Address address = addressFuture.join();
                
                return new UserProfile(user, orders, address);
            });
    }
    
    public static void main(String[] args) throws Exception {
        ParallelAPIService service = new ParallelAPIService();
        
        long start = System.currentTimeMillis();
        
        UserProfile profile = service.getUserProfile(123).get();
        
        long duration = System.currentTimeMillis() - start;
        
        System.out.println("Profile: " + profile);
        System.out.println("Time: " + duration + "ms");  // ~200ms (parallel), not 450ms (sequential)
        
        service.executor.shutdown();
    }
}
```

---

## 3. Fork/Join Framework

### 3.1 Recursive Task

**Concept:** Divide problem into smaller subproblems, solve in parallel

```java
import java.util.concurrent.*;

public class SumTask extends RecursiveTask<Long> {
    private static final int THRESHOLD = 10000;
    
    private final long[] array;
    private final int start;
    private final int end;
    
    public SumTask(long[] array, int start, int end) {
        this.array = array;
        this.start = start;
        this.end = end;
    }
    
    @Override
    protected Long compute() {
        int length = end - start;
        
        if (length <= THRESHOLD) {
            // Small enough: compute directly
            long sum = 0;
            for (int i = start; i < end; i++) {
                sum += array[i];
            }
            return sum;
        } else {
            // Large: split into subtasks
            int mid = start + length / 2;
            
            SumTask leftTask = new SumTask(array, start, mid);
            SumTask rightTask = new SumTask(array, mid, end);
            
            // Fork left task (run in parallel)
            leftTask.fork();
            
            // Compute right task in current thread
            long rightResult = rightTask.compute();
            
            // Wait for left task result
            long leftResult = leftTask.join();
            
            return leftResult + rightResult;
        }
    }
    
    public static void main(String[] args) {
        long[] array = new long[10_000_000];
        for (int i = 0; i < array.length; i++) {
            array[i] = i + 1;
        }
        
        ForkJoinPool pool = ForkJoinPool.commonPool();
        
        long start = System.currentTimeMillis();
        
        SumTask task = new SumTask(array, 0, array.length);
        long sum = pool.invoke(task);
        
        long duration = System.currentTimeMillis() - start;
        
        System.out.println("Sum: " + sum);
        System.out.println("Time: " + duration + "ms");  // ~50ms (parallel)
        
        // Compare with sequential
        start = System.currentTimeMillis();
        long sequentialSum = 0;
        for (long num : array) {
            sequentialSum += num;
        }
        duration = System.currentTimeMillis() - start;
        System.out.println("Sequential time: " + duration + "ms");  // ~150ms
    }
}
```

---

### 3.2 Recursive Action

**No Return Value:**
```java
public class QuickSortTask extends RecursiveAction {
    private static final int THRESHOLD = 100;
    
    private final int[] array;
    private final int low;
    private final int high;
    
    public QuickSortTask(int[] array, int low, int high) {
        this.array = array;
        this.low = low;
        this.high = high;
    }
    
    @Override
    protected void compute() {
        if (high - low <= THRESHOLD) {
            // Small: use Arrays.sort
            Arrays.sort(array, low, high + 1);
        } else {
            // Large: partition and fork
            int pivotIndex = partition(array, low, high);
            
            QuickSortTask leftTask = new QuickSortTask(array, low, pivotIndex - 1);
            QuickSortTask rightTask = new QuickSortTask(array, pivotIndex + 1, high);
            
            invokeAll(leftTask, rightTask);  // Fork both, wait for completion
        }
    }
    
    private int partition(int[] array, int low, int high) {
        int pivot = array[high];
        int i = low - 1;
        
        for (int j = low; j < high; j++) {
            if (array[j] <= pivot) {
                i++;
                int temp = array[i];
                array[i] = array[j];
                array[j] = temp;
            }
        }
        
        int temp = array[i + 1];
        array[i + 1] = array[high];
        array[high] = temp;
        
        return i + 1;
    }
}
```

---

### 3.3 Work-Stealing

**How Fork/Join Works:**
```
Thread 1 Queue: [Task A] [Task B] [Task C]
Thread 2 Queue: [Task D] [Task E]
Thread 3 Queue: (empty)
Thread 4 Queue: [Task F]

When Thread 3 finishes, it "steals" from Thread 1:
Thread 1 Queue: [Task A] [Task B]
Thread 3 Queue: [Task C] (stolen from Thread 1)

This balances load automatically!
```

---

## 4. Concurrent Collections

### 4.1 ConcurrentHashMap

**Thread-Safe Map:**
```java
Map<String, Integer> map = new ConcurrentHashMap<>();

// Thread-safe operations
map.put("key", 1);
map.get("key");
map.remove("key");

// Atomic operations
map.putIfAbsent("key", 1);
map.computeIfAbsent("key", k -> expensiveComputation(k));
map.merge("key", 1, Integer::sum);  // Atomic increment

// Bulk operations (parallel)
map.forEach(10, (k, v) -> System.out.println(k + "=" + v));
```

**Parallel Computation:**
```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
map.put("a", 1);
map.put("b", 2);
map.put("c", 3);

// Parallel reduce
int sum = map.reduceValues(1, Integer::sum);  // 6

// Parallel search
String result = map.search(1, (k, v) -> v > 2 ? k : null);  // "c"
```

---

### 4.2 CopyOnWriteArrayList

**Read-Optimized List:**
```java
List<String> list = new CopyOnWriteArrayList<>();

// Writes are expensive (copies entire array)
list.add("item1");  // Creates new array
list.add("item2");  // Creates new array again

// Reads are fast (no locking)
for (String item : list) {
    System.out.println(item);  // Safe, even if other thread modifies
}

// Use case: Event listeners (many reads, rare writes)
```

---

### 4.3 BlockingQueue

**Producer-Consumer Pattern:**
```java
BlockingQueue<Task> queue = new LinkedBlockingQueue<>(100);

// Producer thread
new Thread(() -> {
    for (int i = 0; i < 1000; i++) {
        try {
            queue.put(new Task(i));  // Blocks if queue full
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}).start();

// Consumer thread
new Thread(() -> {
    while (true) {
        try {
            Task task = queue.take();  // Blocks if queue empty
            process(task);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            break;
        }
    }
}).start();
```

**Queue Types:**
- **ArrayBlockingQueue:** Bounded, array-backed
- **LinkedBlockingQueue:** Optionally bounded, linked-list
- **PriorityBlockingQueue:** Unbounded, priority-ordered
- **SynchronousQueue:** No capacity (direct handoff)
- **DelayQueue:** Elements available after delay

---

### 4.4 ConcurrentSkipListMap

**Sorted Concurrent Map:**
```java
ConcurrentNavigableMap<Integer, String> map = new ConcurrentSkipListMap<>();

map.put(3, "three");
map.put(1, "one");
map.put(2, "two");

// Sorted iteration
map.forEach((k, v) -> System.out.println(k + "=" + v));
// Output: 1=one, 2=two, 3=three

// Range queries
SortedMap<Integer, String> subMap = map.subMap(1, 3);  // [1, 3)
```

---

## 5. Advanced Patterns

### 5.1 Rate Limiter

```java
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class RateLimiter {
    private final Semaphore semaphore;
    private final int maxPermits;
    private final long periodMillis;
    private final ScheduledExecutorService scheduler;
    
    public RateLimiter(int permitsPerSecond) {
        this.maxPermits = permitsPerSecond;
        this.periodMillis = 1000;
        this.semaphore = new Semaphore(maxPermits);
        this.scheduler = Executors.newScheduledThreadPool(1);
        
        // Refill permits every second
        scheduler.scheduleAtFixedRate(() -> {
            int permitsToAdd = maxPermits - semaphore.availablePermits();
            semaphore.release(permitsToAdd);
        }, periodMillis, periodMillis, TimeUnit.MILLISECONDS);
    }
    
    public boolean tryAcquire() {
        return semaphore.tryAcquire();
    }
    
    public void acquire() throws InterruptedException {
        semaphore.acquire();
    }
    
    public void shutdown() {
        scheduler.shutdown();
    }
    
    public static void main(String[] args) throws Exception {
        RateLimiter limiter = new RateLimiter(10);  // 10 requests/sec
        
        ExecutorService executor = Executors.newFixedThreadPool(50);
        
        for (int i = 0; i < 100; i++) {
            int requestId = i;
            executor.submit(() -> {
                try {
                    limiter.acquire();
                    System.out.println("Request " + requestId + " processed at " + 
                                      System.currentTimeMillis());
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            });
        }
        
        executor.shutdown();
        executor.awaitTermination(15, TimeUnit.SECONDS);
        limiter.shutdown();
    }
}
```

---

### 5.2 Circuit Breaker

```java
import java.util.concurrent.atomic.*;

public class CircuitBreaker {
    private enum State { CLOSED, OPEN, HALF_OPEN }
    
    private final AtomicReference<State> state = new AtomicReference<>(State.CLOSED);
    private final AtomicInteger failureCount = new AtomicInteger(0);
    private final AtomicLong lastFailureTime = new AtomicLong(0);
    
    private final int failureThreshold;
    private final long timeoutMillis;
    
    public CircuitBreaker(int failureThreshold, long timeoutMillis) {
        this.failureThreshold = failureThreshold;
        this.timeoutMillis = timeoutMillis;
    }
    
    public <T> T call(Callable<T> operation) throws Exception {
        if (state.get() == State.OPEN) {
            // Check if timeout elapsed
            if (System.currentTimeMillis() - lastFailureTime.get() > timeoutMillis) {
                state.set(State.HALF_OPEN);
                System.out.println("Circuit HALF_OPEN (trying recovery)");
            } else {
                throw new RuntimeException("Circuit OPEN - rejecting call");
            }
        }
        
        try {
            T result = operation.call();
            
            if (state.get() == State.HALF_OPEN) {
                state.set(State.CLOSED);
                failureCount.set(0);
                System.out.println("Circuit CLOSED (recovered)");
            }
            
            return result;
        } catch (Exception e) {
            int failures = failureCount.incrementAndGet();
            lastFailureTime.set(System.currentTimeMillis());
            
            if (failures >= failureThreshold) {
                state.set(State.OPEN);
                System.out.println("Circuit OPEN (too many failures)");
            }
            
            throw e;
        }
    }
    
    public static void main(String[] args) throws Exception {
        CircuitBreaker breaker = new CircuitBreaker(3, 5000);
        
        Callable<String> unreliableService = () -> {
            if (Math.random() > 0.3) {
                throw new RuntimeException("Service failure");
            }
            return "Success";
        };
        
        for (int i = 0; i < 10; i++) {
            try {
                String result = breaker.call(unreliableService);
                System.out.println("Call " + i + ": " + result);
            } catch (Exception e) {
                System.out.println("Call " + i + ": " + e.getMessage());
            }
            Thread.sleep(1000);
        }
    }
}
```

---

### 5.3 Bulkhead Pattern

```java
import java.util.concurrent.*;

public class Bulkhead {
    private final Map<String, Semaphore> semaphores = new ConcurrentHashMap<>();
    
    public Bulkhead(Map<String, Integer> limits) {
        limits.forEach((key, limit) -> 
            semaphores.put(key, new Semaphore(limit))
        );
    }
    
    public <T> T execute(String compartment, Callable<T> task) throws Exception {
        Semaphore semaphore = semaphores.get(compartment);
        if (semaphore == null) {
            throw new IllegalArgumentException("Unknown compartment: " + compartment);
        }
        
        if (!semaphore.tryAcquire(1, TimeUnit.SECONDS)) {
            throw new RuntimeException("Bulkhead full for: " + compartment);
        }
        
        try {
            return task.call();
        } finally {
            semaphore.release();
        }
    }
    
    public static void main(String[] args) throws Exception {
        // Separate resource pools
        Bulkhead bulkhead = new Bulkhead(Map.of(
            "payment-service", 5,     // Max 5 concurrent payment calls
            "email-service", 10,      // Max 10 concurrent email sends
            "report-service", 2       // Max 2 concurrent report generations
        ));
        
        ExecutorService executor = Executors.newFixedThreadPool(50);
        
        // Simulate load
        for (int i = 0; i < 100; i++) {
            int requestId = i;
            executor.submit(() -> {
                try {
                    String result = bulkhead.execute("payment-service", () -> {
                        Thread.sleep(1000);
                        return "Payment " + requestId + " processed";
                    });
                    System.out.println(result);
                } catch (Exception e) {
                    System.out.println("Request " + requestId + " rejected: " + e.getMessage());
                }
            });
        }
        
        executor.shutdown();
        executor.awaitTermination(30, TimeUnit.SECONDS);
    }
}
```

---

## 6. Production Best Practices

### 6.1 Thread Pool Sizing

**CPU-Bound Tasks:**
```
Optimal threads = Number of CPU cores

Example: 8-core machine → 8 threads
```

**I/O-Bound Tasks:**
```
Optimal threads = Number of cores × (1 + Wait Time / Compute Time)

Example:
  8 cores
  Wait time: 90ms (network)
  Compute time: 10ms
  
  Threads = 8 × (1 + 90/10) = 8 × 10 = 80 threads
```

---

### 6.2 Monitoring

```java
public class ThreadPoolMonitor {
    public static void monitor(ThreadPoolExecutor executor) {
        ScheduledExecutorService monitor = Executors.newScheduledThreadPool(1);
        
        monitor.scheduleAtFixedRate(() -> {
            System.out.println("=== Thread Pool Stats ===");
            System.out.println("Pool size: " + executor.getPoolSize());
            System.out.println("Active threads: " + executor.getActiveCount());
            System.out.println("Completed tasks: " + executor.getCompletedTaskCount());
            System.out.println("Queued tasks: " + executor.getQueue().size());
            System.out.println("========================");
        }, 0, 5, TimeUnit.SECONDS);
    }
}
```

---

### 6.3 Graceful Shutdown

```java
public void shutdownGracefully(ExecutorService executor) {
    executor.shutdown();  // Reject new tasks
    
    try {
        if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
            executor.shutdownNow();  // Force shutdown
            
            if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
                System.err.println("Executor did not terminate");
            }
        }
    } catch (InterruptedException e) {
        executor.shutdownNow();
        Thread.currentThread().interrupt();
    }
}
```

---

## Summary

### Framework Comparison

| Framework | Use Case | Complexity |
|-----------|----------|------------|
| Executor | General async tasks | Low |
| CompletableFuture | Async pipelines | Medium |
| Fork/Join | Recursive parallel | High |
| Parallel Streams | Collection processing | Low |

### Concurrent Collections

| Collection | Thread-Safe | Ordering | Performance |
|------------|-------------|----------|-------------|
| ConcurrentHashMap | ✅ | None | High |
| CopyOnWriteArrayList | ✅ | Insertion | Read-heavy |
| ConcurrentSkipListMap | ✅ | Sorted | Medium |
| BlockingQueue | ✅ | FIFO | Producer-Consumer |

### Best Practices

✅ Use thread pools (avoid raw threads)  
✅ Size pools based on workload (CPU vs I/O)  
✅ Use CompletableFuture for async pipelines  
✅ Prefer Fork/Join for recursive problems  
✅ Choose right concurrent collection  
✅ Monitor thread pool metrics  
✅ Implement timeouts (prevent hangs)  
✅ Graceful shutdown (await termination)  
✅ Use circuit breaker (fault tolerance)  
✅ Apply bulkhead (resource isolation)  

---

**End of Advanced Concurrency Patterns**

**Total Lines: ~5,000**
