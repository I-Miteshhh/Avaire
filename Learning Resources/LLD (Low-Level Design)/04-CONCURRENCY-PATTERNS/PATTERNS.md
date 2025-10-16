# Concurrency Patterns for Data Engineering

**Difficulty:** Advanced  
**Learning Time:** 2 weeks  
**Interview Frequency:** ⭐⭐⭐⭐⭐ (Critical for 40 LPA)  
**Real-World Relevance:** Essential for distributed data pipelines

---

## 📚 Table of Contents

1. [Producer-Consumer Pattern](#producer-consumer-pattern)
2. [Thread Pool Pattern](#thread-pool-pattern)
3. [Read-Write Lock Pattern](#read-write-lock-pattern)
4. [Semaphore Pattern](#semaphore-pattern)
5. [Barrier and Latch Patterns](#barrier-and-latch-patterns)
6. [Actor Model](#actor-model)
7. [Future and Promise Pattern](#future-and-promise-pattern)
8. [Real-World Data Engineering Examples](#real-world-data-engineering-examples)

---

## Producer-Consumer Pattern

### Problem

Multiple producers generate data, multiple consumers process it. Need thread-safe buffer with blocking behavior.

### Solution

Use `BlockingQueue` for thread-safe producer-consumer communication.

### Complete Implementation

```java
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

// ============================================
// 1. BASIC PRODUCER-CONSUMER
// ============================================

class Message {
    private final int id;
    private final String content;
    private final long timestamp;
    
    public Message(int id, String content) {
        this.id = id;
        this.content = content;
        this.timestamp = System.currentTimeMillis();
    }
    
    public int getId() {
        return id;
    }
    
    public String getContent() {
        return content;
    }
    
    @Override
    public String toString() {
        return "Message{id=" + id + ", content='" + content + "'}";
    }
}

class Producer implements Runnable {
    private final BlockingQueue<Message> queue;
    private final String name;
    private final AtomicInteger messageCounter;
    
    public Producer(BlockingQueue<Message> queue, String name) {
        this.queue = queue;
        this.name = name;
        this.messageCounter = new AtomicInteger(0);
    }
    
    @Override
    public void run() {
        try {
            while (!Thread.currentThread().isInterrupted()) {
                Message message = produceMessage();
                queue.put(message);  // Blocks if queue is full
                System.out.println(name + " produced: " + message);
                Thread.sleep(100);  // Simulate work
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
    
    private Message produceMessage() {
        int id = messageCounter.incrementAndGet();
        String content = name + " - Message #" + id;
        return new Message(id, content);
    }
}

class Consumer implements Runnable {
    private final BlockingQueue<Message> queue;
    private final String name;
    
    public Consumer(BlockingQueue<Message> queue, String name) {
        this.queue = queue;
        this.name = name;
    }
    
    @Override
    public void run() {
        try {
            while (!Thread.currentThread().isInterrupted()) {
                Message message = queue.take();  // Blocks if queue is empty
                processMessage(message);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
    
    private void processMessage(Message message) throws InterruptedException {
        System.out.println(name + " processing: " + message);
        Thread.sleep(200);  // Simulate processing
        System.out.println(name + " finished: " + message);
    }
}

// ============================================
// 2. KAFKA-LIKE MESSAGE BROKER
// ============================================

/**
 * Multi-topic message broker with partitioning
 * Simulates Kafka consumer groups
 */
class MessageBroker {
    private final Map<String, BlockingQueue<Message>> topics;
    private final int queueCapacity;
    
    public MessageBroker(int queueCapacity) {
        this.topics = new ConcurrentHashMap<>();
        this.queueCapacity = queueCapacity;
    }
    
    /**
     * Create topic with partitioned queues
     */
    public void createTopic(String topicName, int partitions) {
        for (int i = 0; i < partitions; i++) {
            String partitionKey = topicName + "-partition-" + i;
            topics.put(partitionKey, new ArrayBlockingQueue<>(queueCapacity));
        }
    }
    
    /**
     * Publish message to topic (partitioned by message ID)
     */
    public void publish(String topicName, Message message) throws InterruptedException {
        int partitionCount = getPartitionCount(topicName);
        int partition = Math.abs(message.getId() % partitionCount);
        String partitionKey = topicName + "-partition-" + partition;
        
        BlockingQueue<Message> queue = topics.get(partitionKey);
        if (queue != null) {
            queue.put(message);
        }
    }
    
    /**
     * Subscribe to topic partition
     */
    public Message consume(String topicName, int partition) throws InterruptedException {
        String partitionKey = topicName + "-partition-" + partition;
        BlockingQueue<Message> queue = topics.get(partitionKey);
        
        if (queue != null) {
            return queue.take();
        }
        
        return null;
    }
    
    private int getPartitionCount(String topicName) {
        return (int) topics.keySet().stream()
                .filter(key -> key.startsWith(topicName))
                .count();
    }
}

class KafkaStyleProducer implements Runnable {
    private final MessageBroker broker;
    private final String topic;
    private final AtomicInteger messageCounter;
    
    public KafkaStyleProducer(MessageBroker broker, String topic) {
        this.broker = broker;
        this.topic = topic;
        this.messageCounter = new AtomicInteger(0);
    }
    
    @Override
    public void run() {
        try {
            while (!Thread.currentThread().isInterrupted()) {
                Message message = new Message(messageCounter.incrementAndGet(), 
                                            "Event data");
                broker.publish(topic, message);
                Thread.sleep(50);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}

class KafkaStyleConsumer implements Runnable {
    private final MessageBroker broker;
    private final String topic;
    private final int partition;
    private final String consumerGroup;
    
    public KafkaStyleConsumer(MessageBroker broker, String topic, int partition, 
                             String consumerGroup) {
        this.broker = broker;
        this.topic = topic;
        this.partition = partition;
        this.consumerGroup = consumerGroup;
    }
    
    @Override
    public void run() {
        try {
            while (!Thread.currentThread().isInterrupted()) {
                Message message = broker.consume(topic, partition);
                if (message != null) {
                    System.out.println(consumerGroup + " [partition=" + partition + 
                                     "] consumed: " + message);
                    Thread.sleep(100);
                }
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}

// ============================================
// 3. PRIORITY-BASED PRODUCER-CONSUMER
// ============================================

class PriorityMessage implements Comparable<PriorityMessage> {
    private final String content;
    private final int priority;  // Higher = more important
    private final long timestamp;
    
    public PriorityMessage(String content, int priority) {
        this.content = content;
        this.priority = priority;
        this.timestamp = System.currentTimeMillis();
    }
    
    @Override
    public int compareTo(PriorityMessage other) {
        // Higher priority first, then older timestamp
        int priorityCompare = Integer.compare(other.priority, this.priority);
        if (priorityCompare != 0) {
            return priorityCompare;
        }
        return Long.compare(this.timestamp, other.timestamp);
    }
    
    @Override
    public String toString() {
        return "PriorityMessage{priority=" + priority + ", content='" + content + "'}";
    }
}

class PriorityProducerConsumer {
    private final PriorityBlockingQueue<PriorityMessage> queue;
    
    public PriorityProducerConsumer() {
        this.queue = new PriorityBlockingQueue<>(100);
    }
    
    public void produce(String content, int priority) {
        queue.offer(new PriorityMessage(content, priority));
    }
    
    public PriorityMessage consume() throws InterruptedException {
        return queue.take();
    }
}
```

---

## Thread Pool Pattern

### Problem

Creating threads is expensive. Need to reuse threads for multiple tasks.

### Solution

Use `ExecutorService` with thread pool for task execution.

### Complete Implementation

```java
// ============================================
// 1. BASIC THREAD POOL
// ============================================

class TaskExecutor {
    private final ExecutorService executor;
    
    public TaskExecutor(int threadPoolSize) {
        this.executor = Executors.newFixedThreadPool(threadPoolSize);
    }
    
    public <T> Future<T> submit(Callable<T> task) {
        return executor.submit(task);
    }
    
    public void shutdown() {
        executor.shutdown();
        try {
            if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
                executor.shutdownNow();
            }
        } catch (InterruptedException e) {
            executor.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}

// ============================================
// 2. CUSTOM THREAD POOL IMPLEMENTATION
// ============================================

/**
 * Custom thread pool with work-stealing
 * Simulates Java's ForkJoinPool
 */
class CustomThreadPool {
    private final int poolSize;
    private final BlockingQueue<Runnable> taskQueue;
    private final List<WorkerThread> workers;
    private volatile boolean isShutdown;
    
    public CustomThreadPool(int poolSize, int queueCapacity) {
        this.poolSize = poolSize;
        this.taskQueue = new LinkedBlockingQueue<>(queueCapacity);
        this.workers = new ArrayList<>(poolSize);
        this.isShutdown = false;
        
        startWorkers();
    }
    
    private void startWorkers() {
        for (int i = 0; i < poolSize; i++) {
            WorkerThread worker = new WorkerThread("Worker-" + i);
            workers.add(worker);
            worker.start();
        }
    }
    
    public void execute(Runnable task) {
        if (isShutdown) {
            throw new RejectedExecutionException("ThreadPool is shutdown");
        }
        
        try {
            taskQueue.put(task);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RejectedExecutionException("Task submission interrupted", e);
        }
    }
    
    public void shutdown() {
        isShutdown = true;
        
        for (WorkerThread worker : workers) {
            worker.interrupt();
        }
    }
    
    /**
     * Worker thread that pulls tasks from queue
     */
    private class WorkerThread extends Thread {
        
        public WorkerThread(String name) {
            super(name);
        }
        
        @Override
        public void run() {
            while (!isShutdown || !taskQueue.isEmpty()) {
                try {
                    Runnable task = taskQueue.poll(1, TimeUnit.SECONDS);
                    
                    if (task != null) {
                        task.run();
                    }
                } catch (InterruptedException e) {
                    if (isShutdown) {
                        break;
                    }
                } catch (Exception e) {
                    System.err.println(getName() + " task execution failed: " + e.getMessage());
                }
            }
            
            System.out.println(getName() + " terminated");
        }
    }
}

// ============================================
// 3. SPARK-LIKE TASK EXECUTOR
// ============================================

/**
 * Simulates Spark task execution with stages
 */
class SparkLikeExecutor {
    private final ExecutorService executorService;
    private final int parallelism;
    
    public SparkLikeExecutor(int parallelism) {
        this.parallelism = parallelism;
        this.executorService = Executors.newFixedThreadPool(parallelism);
    }
    
    /**
     * Execute stage (collection of tasks in parallel)
     */
    public <T, R> List<R> executeStage(List<T> partitions, Function<T, R> task) {
        List<Future<R>> futures = new ArrayList<>();
        
        // Submit all tasks
        for (T partition : partitions) {
            Future<R> future = executorService.submit(() -> task.apply(partition));
            futures.add(future);
        }
        
        // Collect results
        List<R> results = new ArrayList<>();
        for (Future<R> future : futures) {
            try {
                results.add(future.get());
            } catch (InterruptedException | ExecutionException e) {
                throw new RuntimeException("Stage execution failed", e);
            }
        }
        
        return results;
    }
    
    public void shutdown() {
        executorService.shutdown();
    }
}

// Usage example: Map-Reduce
class MapReduceExample {
    public static void main(String[] args) {
        SparkLikeExecutor executor = new SparkLikeExecutor(4);
        
        // Input data partitions
        List<List<String>> partitions = List.of(
            List.of("apple", "banana", "apple"),
            List.of("banana", "cherry", "apple"),
            List.of("cherry", "cherry", "date")
        );
        
        // Map phase: Count words in each partition
        List<Map<String, Integer>> mapResults = executor.executeStage(partitions, partition -> {
            Map<String, Integer> counts = new HashMap<>();
            for (String word : partition) {
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        });
        
        System.out.println("Map results: " + mapResults);
        
        // Reduce phase: Merge counts
        Map<String, Integer> finalCounts = new HashMap<>();
        for (Map<String, Integer> partitionCounts : mapResults) {
            partitionCounts.forEach((word, count) -> 
                finalCounts.merge(word, count, Integer::sum));
        }
        
        System.out.println("Final counts: " + finalCounts);
        
        executor.shutdown();
    }
}
```

---

## Read-Write Lock Pattern

### Problem

Multiple readers can access data simultaneously, but writers need exclusive access.

### Solution

Use `ReadWriteLock` for concurrent reads, exclusive writes.

### Complete Implementation

```java
// ============================================
// 1. THREAD-SAFE CACHE WITH READ-WRITE LOCK
// ============================================

class ConcurrentCache<K, V> {
    private final Map<K, V> cache;
    private final ReadWriteLock lock;
    private final Lock readLock;
    private final Lock writeLock;
    
    public ConcurrentCache() {
        this.cache = new HashMap<>();
        this.lock = new ReentrantReadWriteLock();
        this.readLock = lock.readLock();
        this.writeLock = lock.writeLock();
    }
    
    /**
     * Read operation - allows multiple concurrent readers
     * Time: O(1) for HashMap
     */
    public V get(K key) {
        readLock.lock();
        try {
            return cache.get(key);
        } finally {
            readLock.unlock();
        }
    }
    
    /**
     * Write operation - exclusive access
     * Time: O(1) for HashMap
     */
    public void put(K key, V value) {
        writeLock.lock();
        try {
            cache.put(key, value);
        } finally {
            writeLock.unlock();
        }
    }
    
    /**
     * Delete operation - exclusive access
     */
    public V remove(K key) {
        writeLock.lock();
        try {
            return cache.remove(key);
        } finally {
            writeLock.unlock();
        }
    }
    
    /**
     * Bulk read operation
     */
    public Map<K, V> getAll() {
        readLock.lock();
        try {
            return new HashMap<>(cache);
        } finally {
            readLock.unlock();
        }
    }
}

// ============================================
// 2. TIME-SERIES DATABASE WITH VERSIONING
// ============================================

/**
 * Thread-safe time-series data store
 * Simulates metrics aggregation in data pipelines
 */
class TimeSeriesDatabase {
    private final Map<String, NavigableMap<Long, Double>> timeSeries;
    private final ReadWriteLock lock;
    
    public TimeSeriesDatabase() {
        this.timeSeries = new HashMap<>();
        this.lock = new ReentrantReadWriteLock();
    }
    
    /**
     * Write data point
     */
    public void write(String metric, long timestamp, double value) {
        lock.writeLock().lock();
        try {
            timeSeries.computeIfAbsent(metric, k -> new TreeMap<>())
                     .put(timestamp, value);
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    /**
     * Read data points in time range
     */
    public Map<Long, Double> read(String metric, long startTime, long endTime) {
        lock.readLock().lock();
        try {
            NavigableMap<Long, Double> data = timeSeries.get(metric);
            if (data == null) {
                return Collections.emptyMap();
            }
            
            return new TreeMap<>(data.subMap(startTime, true, endTime, true));
        } finally {
            lock.readLock().unlock();
        }
    }
    
    /**
     * Aggregate over time range (e.g., sum, avg, max)
     */
    public double aggregate(String metric, long startTime, long endTime, 
                          String aggregation) {
        lock.readLock().lock();
        try {
            Map<Long, Double> data = read(metric, startTime, endTime);
            
            switch (aggregation.toLowerCase()) {
                case "sum":
                    return data.values().stream().mapToDouble(Double::doubleValue).sum();
                case "avg":
                    return data.values().stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
                case "max":
                    return data.values().stream().mapToDouble(Double::doubleValue).max().orElse(Double.MIN_VALUE);
                case "min":
                    return data.values().stream().mapToDouble(Double::doubleValue).min().orElse(Double.MAX_VALUE);
                default:
                    throw new IllegalArgumentException("Unknown aggregation: " + aggregation);
            }
        } finally {
            lock.readLock().unlock();
        }
    }
}

// ============================================
// 3. LOCK UPGRADE/DOWNGRADE
// ============================================

/**
 * Configuration manager with lock upgrade
 */
class ConfigurationManager {
    private final Map<String, String> config;
    private final ReentrantReadWriteLock rwLock;
    
    public ConfigurationManager() {
        this.config = new HashMap<>();
        this.rwLock = new ReentrantReadWriteLock();
    }
    
    /**
     * Get or compute configuration
     * Demonstrates lock upgrade pattern
     */
    public String getOrCompute(String key, Supplier<String> defaultValueSupplier) {
        // Try read lock first
        rwLock.readLock().lock();
        try {
            String value = config.get(key);
            
            if (value != null) {
                return value;
            }
            
            // Need to write - upgrade to write lock
            rwLock.readLock().unlock();
            rwLock.writeLock().lock();
            
            try {
                // Double-check after acquiring write lock
                value = config.get(key);
                if (value == null) {
                    value = defaultValueSupplier.get();
                    config.put(key, value);
                }
                
                // Downgrade to read lock
                rwLock.readLock().lock();
                return value;
            } finally {
                rwLock.writeLock().unlock();
            }
        } finally {
            rwLock.readLock().unlock();
        }
    }
}
```

---

## Semaphore Pattern

### Problem

Limit concurrent access to a resource (e.g., database connections, API rate limiting).

### Solution

Use `Semaphore` to control permits.

### Complete Implementation

```java
// ============================================
// 1. CONNECTION POOL WITH SEMAPHORE
// ============================================

class Connection {
    private final String id;
    private boolean inUse;
    
    public Connection(String id) {
        this.id = id;
        this.inUse = false;
    }
    
    public void execute(String query) throws InterruptedException {
        System.out.println("Executing query on " + id + ": " + query);
        Thread.sleep(500);  // Simulate query execution
    }
    
    public String getId() {
        return id;
    }
    
    public boolean isInUse() {
        return inUse;
    }
    
    public void setInUse(boolean inUse) {
        this.inUse = inUse;
    }
}

class ConnectionPool {
    private final Semaphore semaphore;
    private final List<Connection> connections;
    
    public ConnectionPool(int poolSize) {
        this.semaphore = new Semaphore(poolSize, true);  // Fair semaphore
        this.connections = new ArrayList<>(poolSize);
        
        for (int i = 0; i < poolSize; i++) {
            connections.add(new Connection("Connection-" + i));
        }
    }
    
    /**
     * Acquire connection (blocks if none available)
     */
    public Connection acquire() throws InterruptedException {
        semaphore.acquire();
        
        synchronized (connections) {
            for (Connection conn : connections) {
                if (!conn.isInUse()) {
                    conn.setInUse(true);
                    System.out.println("Acquired: " + conn.getId());
                    return conn;
                }
            }
        }
        
        throw new IllegalStateException("No available connections");
    }
    
    /**
     * Release connection
     */
    public void release(Connection connection) {
        synchronized (connections) {
            connection.setInUse(false);
        }
        
        semaphore.release();
        System.out.println("Released: " + connection.getId());
    }
}

// ============================================
// 2. RATE LIMITER WITH SEMAPHORE
// ============================================

/**
 * Token bucket rate limiter
 * Allows N requests per time window
 */
class RateLimiter {
    private final Semaphore semaphore;
    private final int maxPermits;
    private final long refillPeriodMs;
    
    public RateLimiter(int maxPermits, long refillPeriodMs) {
        this.semaphore = new Semaphore(maxPermits);
        this.maxPermits = maxPermits;
        this.refillPeriodMs = refillPeriodMs;
        
        startRefillThread();
    }
    
    /**
     * Try to acquire permit (non-blocking)
     */
    public boolean tryAcquire() {
        return semaphore.tryAcquire();
    }
    
    /**
     * Acquire permit (blocking)
     */
    public void acquire() throws InterruptedException {
        semaphore.acquire();
    }
    
    /**
     * Background thread to refill permits
     */
    private void startRefillThread() {
        ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();
        
        scheduler.scheduleAtFixedRate(() -> {
            int permitsToAdd = maxPermits - semaphore.availablePermits();
            if (permitsToAdd > 0) {
                semaphore.release(permitsToAdd);
            }
        }, refillPeriodMs, refillPeriodMs, TimeUnit.MILLISECONDS);
    }
}

// ============================================
// 3. RESOURCE LIMITER FOR SPARK TASKS
// ============================================

/**
 * Limit concurrent Spark tasks to prevent OOM
 */
class SparkTaskLimiter {
    private final Semaphore cpuSemaphore;
    private final Semaphore memorySemaphore;
    
    public SparkTaskLimiter(int maxConcurrentTasks, int maxMemoryMB) {
        this.cpuSemaphore = new Semaphore(maxConcurrentTasks);
        this.memorySemaphore = new Semaphore(maxMemoryMB);
    }
    
    /**
     * Execute task with resource limits
     */
    public <T> T executeTask(Callable<T> task, int requiredMemoryMB) throws Exception {
        // Acquire CPU permit
        cpuSemaphore.acquire();
        
        // Acquire memory permits
        memorySemaphore.acquire(requiredMemoryMB);
        
        try {
            return task.call();
        } finally {
            memorySemaphore.release(requiredMemoryMB);
            cpuSemaphore.release();
        }
    }
}
```

---

## Barrier and Latch Patterns

### Problem

Coordinate multiple threads to wait for each other or for a condition.

### Solution

Use `CyclicBarrier`, `CountDownLatch`, `Phaser`.

### Complete Implementation

```java
// ============================================
// 1. CYCLICBARRIER FOR ITERATIVE ALGORITHMS
// ============================================

/**
 * Simulates parallel gradient descent
 * All threads must sync after each iteration
 */
class ParallelGradientDescent {
    private final int numWorkers;
    private final CyclicBarrier barrier;
    private final double[] globalGradient;
    
    public ParallelGradientDescent(int numWorkers, int dimensions) {
        this.numWorkers = numWorkers;
        this.globalGradient = new double[dimensions];
        this.barrier = new CyclicBarrier(numWorkers, () -> {
            // Barrier action: Aggregate gradients
            System.out.println("All workers completed iteration. Aggregating gradients...");
        });
    }
    
    public void train(List<double[]> dataPartitions, int iterations) {
        ExecutorService executor = Executors.newFixedThreadPool(numWorkers);
        
        for (int i = 0; i < numWorkers; i++) {
            final int workerIdx = i;
            executor.submit(() -> {
                double[] partition = dataPartitions.get(workerIdx);
                
                for (int iter = 0; iter < iterations; iter++) {
                    // Compute local gradient
                    double[] localGradient = computeGradient(partition);
                    
                    // Update global gradient (synchronized)
                    synchronized (globalGradient) {
                        for (int j = 0; j < globalGradient.length; j++) {
                            globalGradient[j] += localGradient[j];
                        }
                    }
                    
                    try {
                        // Wait for all workers to complete iteration
                        barrier.await();
                    } catch (InterruptedException | BrokenBarrierException e) {
                        Thread.currentThread().interrupt();
                        return;
                    }
                }
            });
        }
        
        executor.shutdown();
    }
    
    private double[] computeGradient(double[] data) {
        // Placeholder: Actual gradient computation
        return new double[globalGradient.length];
    }
}

// ============================================
// 2. COUNTDOWNLATCH FOR DEPENDENCY MANAGEMENT
// ============================================

/**
 * Simulates Spark DAG execution
 * Stage 2 waits for Stage 1 completion
 */
class DAGExecutor {
    
    static class Stage {
        private final String name;
        private final List<Runnable> tasks;
        private final CountDownLatch latch;
        
        public Stage(String name, int taskCount) {
            this.name = name;
            this.tasks = new ArrayList<>();
            this.latch = new CountDownLatch(taskCount);
        }
        
        public void addTask(Runnable task) {
            tasks.add(task);
        }
        
        public void execute(ExecutorService executor) {
            System.out.println("Executing stage: " + name);
            
            for (Runnable task : tasks) {
                executor.submit(() -> {
                    try {
                        task.run();
                    } finally {
                        latch.countDown();
                    }
                });
            }
        }
        
        public void await() throws InterruptedException {
            latch.await();
            System.out.println("Stage completed: " + name);
        }
    }
    
    public static void main(String[] args) throws InterruptedException {
        ExecutorService executor = Executors.newFixedThreadPool(4);
        
        // Stage 1: Read data from multiple sources
        Stage stage1 = new Stage("Stage-1: Data Ingestion", 3);
        stage1.addTask(() -> System.out.println("Reading from S3..."));
        stage1.addTask(() -> System.out.println("Reading from Database..."));
        stage1.addTask(() -> System.out.println("Reading from Kafka..."));
        
        // Stage 2: Transform data (depends on Stage 1)
        Stage stage2 = new Stage("Stage-2: Transformation", 2);
        stage2.addTask(() -> System.out.println("Applying map transformation..."));
        stage2.addTask(() -> System.out.println("Applying filter transformation..."));
        
        // Execute Stage 1
        stage1.execute(executor);
        stage1.await();
        
        // Execute Stage 2 (after Stage 1 completes)
        stage2.execute(executor);
        stage2.await();
        
        System.out.println("DAG execution complete");
        
        executor.shutdown();
    }
}

// ============================================
// 3. PHASER FOR DYNAMIC PARALLELISM
// ============================================

/**
 * Phaser allows dynamic registration/deregistration
 * Unlike CyclicBarrier which has fixed party count
 */
class DynamicTaskCoordinator {
    private final Phaser phaser;
    
    public DynamicTaskCoordinator() {
        this.phaser = new Phaser(1);  // Register main thread
    }
    
    public void addTask(Runnable task) {
        phaser.register();
        
        new Thread(() -> {
            try {
                task.run();
            } finally {
                phaser.arriveAndDeregister();
            }
        }).start();
    }
    
    public void waitForCompletion() {
        phaser.arriveAndAwaitAdvance();
    }
}
```

---

## Real-World Data Engineering Examples

### 1. Kafka Consumer Group

```java
/**
 * Simulates Kafka consumer group with rebalancing
 */
class KafkaConsumerGroup {
    private final String groupId;
    private final List<String> topics;
    private final ConcurrentHashMap<Integer, String> partitionAssignment;
    private final ExecutorService executorService;
    
    public KafkaConsumerGroup(String groupId, List<String> topics, int consumerCount) {
        this.groupId = groupId;
        this.topics = topics;
        this.partitionAssignment = new ConcurrentHashMap<>();
        this.executorService = Executors.newFixedThreadPool(consumerCount);
    }
    
    public void start(int totalPartitions) {
        CountDownLatch allConsumersReady = new CountDownLatch(executorService.getMaximumPoolSize());
        
        for (int i = 0; i < executorService.getMaximumPoolSize(); i++) {
            final int consumerId = i;
            
            executorService.submit(() -> {
                // Assign partitions to this consumer
                List<Integer> assignedPartitions = assignPartitions(consumerId, totalPartitions);
                
                allConsumersReady.countDown();
                
                try {
                    allConsumersReady.await();  // Wait for all consumers to be ready
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return;
                }
                
                // Start consuming
                consumePartitions(consumerId, assignedPartitions);
            });
        }
    }
    
    private List<Integer> assignPartitions(int consumerId, int totalPartitions) {
        int consumersCount = executorService.getMaximumPoolSize();
        List<Integer> partitions = new ArrayList<>();
        
        for (int i = consumerId; i < totalPartitions; i += consumersCount) {
            partitions.add(i);
            partitionAssignment.put(i, "Consumer-" + consumerId);
        }
        
        return partitions;
    }
    
    private void consumePartitions(int consumerId, List<Integer> partitions) {
        System.out.println("Consumer-" + consumerId + " assigned partitions: " + partitions);
        
        // Simulate consumption
        while (!Thread.currentThread().isInterrupted()) {
            for (int partition : partitions) {
                // Poll messages from partition
                System.out.println("Consumer-" + consumerId + " polling partition-" + partition);
            }
            
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }
}
```

### 2. Spark Shuffle with Backpressure

```java
/**
 * Simulates Spark shuffle with backpressure
 */
class ShuffleManager {
    private final int numPartitions;
    private final List<BlockingQueue<byte[]>> shuffleBuffers;
    private final Semaphore backpressure;
    
    public ShuffleManager(int numPartitions, int bufferSizePerPartition) {
        this.numPartitions = numPartitions;
        this.shuffleBuffers = new ArrayList<>(numPartitions);
        this.backpressure = new Semaphore(bufferSizePerPartition * numPartitions);
        
        for (int i = 0; i < numPartitions; i++) {
            shuffleBuffers.add(new ArrayBlockingQueue<>(bufferSizePerPartition));
        }
    }
    
    /**
     * Write shuffle data (map output)
     */
    public void write(int partitionId, byte[] data) throws InterruptedException {
        backpressure.acquire();  // Apply backpressure
        
        try {
            shuffleBuffers.get(partitionId).put(data);
        } catch (InterruptedException e) {
            backpressure.release();
            throw e;
        }
    }
    
    /**
     * Read shuffle data (reduce input)
     */
    public byte[] read(int partitionId) throws InterruptedException {
        byte[] data = shuffleBuffers.get(partitionId).take();
        backpressure.release();  // Release backpressure
        return data;
    }
}
```

---

## 🎯 Interview Tips

### Common Concurrency Questions

1. **"What's the difference between synchronized and ReentrantLock?"**
   - Synchronized: Built-in, automatic release, no fairness option
   - ReentrantLock: Explicit, try lock with timeout, fairness option, lock interruptibly

2. **"How to prevent deadlock?"**
   - Lock ordering: Always acquire locks in same order
   - Try-lock with timeout
   - Use java.util.concurrent abstractions

3. **"When to use CountDownLatch vs CyclicBarrier?"**
   - CountDownLatch: One-time event, tasks don't wait for each other
   - CyclicBarrier: Reusable, all tasks wait at barrier point

4. **"How does ConcurrentHashMap achieve thread-safety?"**
   - Segment locking (Java 7): Divide into 16 segments
   - CAS + synchronized (Java 8+): Lock only on writes, CAS for updates

---

**Next:** [LLD README](../README.md) — Module overview and learning path
