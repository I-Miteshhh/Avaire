# Design Patterns - Behavioral Patterns

**Learning Time:** 3-4 weeks  
**Prerequisites:** Structural Patterns  
**Difficulty:** Advanced → How objects communicate and distribute responsibilities

---

## 📚 Table of Contents

1. [Strategy Pattern](#strategy-pattern)
2. [Observer Pattern](#observer-pattern)
3. [Command Pattern](#command-pattern)
4. [Template Method Pattern](#template-method-pattern)
5. [Iterator Pattern](#iterator-pattern)
6. [State Pattern](#state-pattern)
7. [Chain of Responsibility Pattern](#chain-of-responsibility-pattern)
8. [Mediator Pattern](#mediator-pattern)
9. [Memento Pattern](#memento-pattern)
10. [Visitor Pattern](#visitor-pattern)

---

## 1. Strategy Pattern

### Intent
Define family of algorithms, encapsulate each one, make them interchangeable. Strategy lets algorithm vary independently from clients that use it.

### When to Use (SDE-Data)
```
├─ Multiple ways to do the same thing (sort, compress, encrypt)
├─ Avoid conditional logic (if-else chains, switch statements)
├─ Runtime algorithm selection
├─ Open/Closed Principle: Add new algorithms without modifying client
```

### Example: Compression Strategies

```java
/**
 * Strategy interface
 */
public interface CompressionStrategy {
    byte[] compress(byte[] data);
    byte[] decompress(byte[] data);
    String getName();
}

// Concrete strategy: Gzip
public class GzipCompression implements CompressionStrategy {
    @Override
    public byte[] compress(byte[] data) {
        try (ByteArrayOutputStream bos = new ByteArrayOutputStream();
             GZIPOutputStream gzip = new GZIPOutputStream(bos)) {
            gzip.write(data);
            gzip.finish();
            return bos.toByteArray();
        } catch (IOException e) {
            throw new RuntimeException("Gzip compression failed", e);
        }
    }
    
    @Override
    public byte[] decompress(byte[] data) {
        try (ByteArrayInputStream bis = new ByteArrayInputStream(data);
             GZIPInputStream gzip = new GZIPInputStream(bis)) {
            return gzip.readAllBytes();
        } catch (IOException e) {
            throw new RuntimeException("Gzip decompression failed", e);
        }
    }
    
    @Override
    public String getName() {
        return "gzip";
    }
}

// Concrete strategy: Snappy (used in Hadoop, Spark)
public class SnappyCompression implements CompressionStrategy {
    @Override
    public byte[] compress(byte[] data) {
        try {
            return Snappy.compress(data);
        } catch (IOException e) {
            throw new RuntimeException("Snappy compression failed", e);
        }
    }
    
    @Override
    public byte[] decompress(byte[] data) {
        try {
            return Snappy.uncompress(data);
        } catch (IOException e) {
            throw new RuntimeException("Snappy decompression failed", e);
        }
    }
    
    @Override
    public String getName() {
        return "snappy";
    }
}

// Concrete strategy: LZ4 (fastest)
public class Lz4Compression implements CompressionStrategy {
    private final LZ4Factory factory = LZ4Factory.fastestInstance();
    
    @Override
    public byte[] compress(byte[] data) {
        LZ4Compressor compressor = factory.fastCompressor();
        int maxCompressedLength = compressor.maxCompressedLength(data.length);
        byte[] compressed = new byte[maxCompressedLength + 4];
        
        // Store original size in first 4 bytes
        compressed[0] = (byte) (data.length >>> 24);
        compressed[1] = (byte) (data.length >>> 16);
        compressed[2] = (byte) (data.length >>> 8);
        compressed[3] = (byte) data.length;
        
        int compressedLength = compressor.compress(data, 0, data.length, compressed, 4);
        return Arrays.copyOf(compressed, compressedLength + 4);
    }
    
    @Override
    public byte[] decompress(byte[] data) {
        // Read original size from first 4 bytes
        int originalSize = ((data[0] & 0xFF) << 24) |
                          ((data[1] & 0xFF) << 16) |
                          ((data[2] & 0xFF) << 8) |
                          (data[3] & 0xFF);
        
        LZ4FastDecompressor decompressor = factory.fastDecompressor();
        byte[] decompressed = new byte[originalSize];
        decompressor.decompress(data, 4, decompressed, 0, originalSize);
        return decompressed;
    }
    
    @Override
    public String getName() {
        return "lz4";
    }
}

// Context: Uses compression strategy
public class DataCompressor {
    private CompressionStrategy strategy;
    
    public DataCompressor(CompressionStrategy strategy) {
        this.strategy = strategy;
    }
    
    public void setStrategy(CompressionStrategy strategy) {
        this.strategy = strategy;
    }
    
    public byte[] compress(byte[] data) {
        long start = System.nanoTime();
        byte[] compressed = strategy.compress(data);
        long elapsed = System.nanoTime() - start;
        
        double ratio = 100.0 * (1 - (double) compressed.length / data.length);
        System.out.printf("%s: %d → %d bytes (%.1f%% reduction) in %.2fms%n",
            strategy.getName(), data.length, compressed.length, ratio, elapsed / 1_000_000.0);
        
        return compressed;
    }
    
    public byte[] decompress(byte[] data) {
        return strategy.decompress(data);
    }
}

// Usage: Switch compression algorithm at runtime
public class Main {
    public static void main(String[] args) {
        String text = "This is sample data to compress. " +
                     "In real data engineering, we compress large datasets " +
                     "to save storage and network bandwidth.";
        byte[] data = text.getBytes();
        
        System.out.println("Original size: " + data.length + " bytes\n");
        
        // Try different compression strategies
        DataCompressor compressor = new DataCompressor(new GzipCompression());
        byte[] gzipData = compressor.compress(data);
        
        compressor.setStrategy(new SnappyCompression());
        byte[] snappyData = compressor.compress(data);
        
        compressor.setStrategy(new Lz4Compression());
        byte[] lz4Data = compressor.compress(data);
        
        /*
         * Output:
         * Original size: 162 bytes
         * 
         * gzip: 162 → 115 bytes (29.0% reduction) in 2.34ms
         * snappy: 162 → 140 bytes (13.6% reduction) in 0.45ms
         * lz4: 162 → 138 bytes (14.8% reduction) in 0.23ms
         * 
         * Choose based on requirements:
         * - Best compression ratio: Gzip
         * - Best speed: LZ4
         * - Balance: Snappy
         */
    }
}
```

### Real-World: Spark Partitioning Strategies

```java
/**
 * SDE-Data: Different partitioning strategies for Spark DataFrames
 */
public interface PartitionStrategy {
    Dataset<Row> partition(Dataset<Row> df);
    String describe();
}

// Hash partitioning
public class HashPartitionStrategy implements PartitionStrategy {
    private final String[] columns;
    private final int numPartitions;
    
    public HashPartitionStrategy(int numPartitions, String... columns) {
        this.columns = columns;
        this.numPartitions = numPartitions;
    }
    
    @Override
    public Dataset<Row> partition(Dataset<Row> df) {
        return df.repartition(numPartitions, 
            Arrays.stream(columns).map(functions::col).toArray(Column[]::new)
        );
    }
    
    @Override
    public String describe() {
        return String.format("Hash partition on %s into %d partitions", 
            String.join(", ", columns), numPartitions);
    }
}

// Range partitioning
public class RangePartitionStrategy implements PartitionStrategy {
    private final String[] columns;
    private final int numPartitions;
    
    public RangePartitionStrategy(int numPartitions, String... columns) {
        this.columns = columns;
        this.numPartitions = numPartitions;
    }
    
    @Override
    public Dataset<Row> partition(Dataset<Row> df) {
        return df.repartitionByRange(numPartitions,
            Arrays.stream(columns).map(functions::col).toArray(Column[]::new)
        );
    }
    
    @Override
    public String describe() {
        return String.format("Range partition on %s into %d partitions",
            String.join(", ", columns), numPartitions);
    }
}

// Coalesce partitioning (reduce partitions without shuffle)
public class CoalesceStrategy implements PartitionStrategy {
    private final int numPartitions;
    
    public CoalesceStrategy(int numPartitions) {
        this.numPartitions = numPartitions;
    }
    
    @Override
    public Dataset<Row> partition(Dataset<Row> df) {
        return df.coalesce(numPartitions);
    }
    
    @Override
    public String describe() {
        return String.format("Coalesce to %d partitions (no shuffle)", numPartitions);
    }
}

// Context
public class DataFramePartitioner {
    private PartitionStrategy strategy;
    
    public DataFramePartitioner(PartitionStrategy strategy) {
        this.strategy = strategy;
    }
    
    public Dataset<Row> applyPartitioning(Dataset<Row> df) {
        System.out.println("Applying: " + strategy.describe());
        Dataset<Row> partitioned = strategy.partition(df);
        System.out.println("Result: " + partitioned.rdd().getNumPartitions() + " partitions");
        return partitioned;
    }
}

// Usage
public class Main {
    public static void main(String[] args) {
        SparkSession spark = SparkSession.builder()
            .appName("StrategyExample")
            .master("local[*]")
            .getOrCreate();
        
        Dataset<Row> df = spark.read()
            .format("csv")
            .option("header", "true")
            .load("users.csv");
        
        System.out.println("Original partitions: " + df.rdd().getNumPartitions());
        
        // Strategy 1: Hash partitioning for join optimization
        DataFramePartitioner partitioner = new DataFramePartitioner(
            new HashPartitionStrategy(10, "user_id")
        );
        Dataset<Row> hashPartitioned = partitioner.applyPartitioning(df);
        
        // Strategy 2: Range partitioning for ordered data
        partitioner = new DataFramePartitioner(
            new RangePartitionStrategy(5, "timestamp")
        );
        Dataset<Row> rangePartitioned = partitioner.applyPartitioning(df);
        
        // Strategy 3: Coalesce to reduce partitions
        partitioner = new DataFramePartitioner(new CoalesceStrategy(1));
        Dataset<Row> coalesced = partitioner.applyPartitioning(hashPartitioned);
        
        spark.stop();
    }
}
```

---

## 2. Observer Pattern

### Intent
Define one-to-many dependency so when one object changes state, all dependents are notified automatically.

### When to Use (SDE-Data)
```
├─ Event-driven systems (data pipeline monitoring)
├─ Publish-subscribe systems (Kafka, message queues)
├─ Real-time dashboards (update UI when data changes)
├─ Alerting systems (notify when metrics exceed threshold)
```

### Example: Data Pipeline Monitoring

```java
/**
 * Subject interface
 */
public interface DataPipeline {
    void attach(PipelineObserver observer);
    void detach(PipelineObserver observer);
    void notifyObservers(PipelineEvent event);
}

// Pipeline events
public class PipelineEvent {
    private final String pipelineId;
    private final EventType type;
    private final String message;
    private final long timestamp;
    private final Map<String, Object> metadata;
    
    public enum EventType {
        STARTED, COMPLETED, FAILED, PROGRESS
    }
    
    public PipelineEvent(String pipelineId, EventType type, String message) {
        this.pipelineId = pipelineId;
        this.type = type;
        this.message = message;
        this.timestamp = System.currentTimeMillis();
        this.metadata = new HashMap<>();
    }
    
    public PipelineEvent withMetadata(String key, Object value) {
        metadata.put(key, value);
        return this;
    }
    
    // Getters
    public String getPipelineId() { return pipelineId; }
    public EventType getType() { return type; }
    public String getMessage() { return message; }
    public long getTimestamp() { return timestamp; }
    public Map<String, Object> getMetadata() { return metadata; }
}

// Observer interface
public interface PipelineObserver {
    void onPipelineEvent(PipelineEvent event);
}

// Concrete observer: Logger
public class LoggingObserver implements PipelineObserver {
    private final Logger logger = LoggerFactory.getLogger(LoggingObserver.class);
    
    @Override
    public void onPipelineEvent(PipelineEvent event) {
        String logMessage = String.format("[%s] %s: %s",
            event.getType(),
            event.getPipelineId(),
            event.getMessage()
        );
        
        switch (event.getType()) {
            case FAILED:
                logger.error(logMessage);
                break;
            case COMPLETED:
                logger.info(logMessage);
                break;
            default:
                logger.debug(logMessage);
        }
    }
}

// Concrete observer: Metrics collector
public class MetricsObserver implements PipelineObserver {
    private final Map<String, Long> pipelineStartTimes = new ConcurrentHashMap<>();
    private final Map<String, Integer> successCount = new ConcurrentHashMap<>();
    private final Map<String, Integer> failureCount = new ConcurrentHashMap<>();
    
    @Override
    public void onPipelineEvent(PipelineEvent event) {
        String pipelineId = event.getPipelineId();
        
        switch (event.getType()) {
            case STARTED:
                pipelineStartTimes.put(pipelineId, event.getTimestamp());
                break;
                
            case COMPLETED:
                Long startTime = pipelineStartTimes.remove(pipelineId);
                if (startTime != null) {
                    long duration = event.getTimestamp() - startTime;
                    System.out.println("METRIC: " + pipelineId + " duration = " + duration + "ms");
                }
                successCount.merge(pipelineId, 1, Integer::sum);
                break;
                
            case FAILED:
                pipelineStartTimes.remove(pipelineId);
                failureCount.merge(pipelineId, 1, Integer::sum);
                break;
        }
    }
    
    public void printStats() {
        System.out.println("\n=== Pipeline Statistics ===");
        for (String pipelineId : successCount.keySet()) {
            int success = successCount.getOrDefault(pipelineId, 0);
            int failure = failureCount.getOrDefault(pipelineId, 0);
            System.out.printf("%s: %d succeeded, %d failed%n", pipelineId, success, failure);
        }
    }
}

// Concrete observer: Alerting
public class AlertingObserver implements PipelineObserver {
    private final String slackWebhook;
    
    public AlertingObserver(String slackWebhook) {
        this.slackWebhook = slackWebhook;
    }
    
    @Override
    public void onPipelineEvent(PipelineEvent event) {
        if (event.getType() == PipelineEvent.EventType.FAILED) {
            sendSlackAlert(event);
        }
    }
    
    private void sendSlackAlert(PipelineEvent event) {
        String alertMessage = String.format("🚨 Pipeline FAILED: %s - %s",
            event.getPipelineId(),
            event.getMessage()
        );
        System.out.println("ALERT: " + alertMessage);
        // In production: HTTP POST to slackWebhook
    }
}

// Concrete subject
public class SparkDataPipeline implements DataPipeline {
    private final String pipelineId;
    private final List<PipelineObserver> observers = new CopyOnWriteArrayList<>();
    
    public SparkDataPipeline(String pipelineId) {
        this.pipelineId = pipelineId;
    }
    
    @Override
    public void attach(PipelineObserver observer) {
        observers.add(observer);
    }
    
    @Override
    public void detach(PipelineObserver observer) {
        observers.remove(observer);
    }
    
    @Override
    public void notifyObservers(PipelineEvent event) {
        for (PipelineObserver observer : observers) {
            observer.onPipelineEvent(event);
        }
    }
    
    public void execute() {
        notifyObservers(new PipelineEvent(pipelineId, PipelineEvent.EventType.STARTED, "Pipeline started"));
        
        try {
            // Simulate pipeline execution
            Thread.sleep(1000);
            notifyObservers(new PipelineEvent(pipelineId, PipelineEvent.EventType.PROGRESS, "Extracted 10000 records"));
            
            Thread.sleep(500);
            notifyObservers(new PipelineEvent(pipelineId, PipelineEvent.EventType.PROGRESS, "Transformed 10000 records"));
            
            Thread.sleep(500);
            
            // Simulate random failure (20% chance)
            if (Math.random() < 0.2) {
                throw new RuntimeException("Connection timeout");
            }
            
            notifyObservers(new PipelineEvent(pipelineId, PipelineEvent.EventType.COMPLETED, "Pipeline completed successfully")
                .withMetadata("recordsProcessed", 10000));
            
        } catch (Exception e) {
            notifyObservers(new PipelineEvent(pipelineId, PipelineEvent.EventType.FAILED, e.getMessage())
                .withMetadata("error", e.getClass().getSimpleName()));
        }
    }
}

// Usage
public class Main {
    public static void main(String[] args) throws InterruptedException {
        // Create observers
        LoggingObserver logger = new LoggingObserver();
        MetricsObserver metrics = new MetricsObserver();
        AlertingObserver alerting = new AlertingObserver("https://hooks.slack.com/...");
        
        // Run multiple pipelines
        for (int i = 0; i < 5; i++) {
            SparkDataPipeline pipeline = new SparkDataPipeline("pipeline-" + i);
            
            // Attach observers
            pipeline.attach(logger);
            pipeline.attach(metrics);
            pipeline.attach(alerting);
            
            // Execute
            pipeline.execute();
            Thread.sleep(100);
        }
        
        // Print statistics
        metrics.printStats();
        
        /*
         * Benefits:
         * - Observers are decoupled from pipeline
         * - Easy to add new observers (e.g., DatabaseObserver, PrometheusObserver)
         * - No modification to pipeline code when adding observers ✅
         */
    }
}
```

---

## 3. Command Pattern

### Intent
Encapsulate request as an object, allowing parameterization of clients with different requests, queuing, logging, and undo operations.

### When to Use (SDE-Data)
```
├─ Implement undo/redo functionality
├─ Queue operations for later execution
├─ Transaction log (replay commands)
├─ Task scheduling (Airflow DAG tasks)
```

### Example: Data Transformation Commands

```java
/**
 * Command interface
 */
public interface TransformationCommand {
    void execute();
    void undo();
    String describe();
}

// Receiver: DataFrame wrapper
public class DataFrameContext {
    private Dataset<Row> dataFrame;
    private final Stack<Dataset<Row>> history = new Stack<>();
    
    public DataFrameContext(Dataset<Row> dataFrame) {
        this.dataFrame = dataFrame;
    }
    
    public Dataset<Row> getDataFrame() {
        return dataFrame;
    }
    
    public void setDataFrame(Dataset<Row> dataFrame) {
        this.dataFrame = dataFrame;
    }
    
    public void saveSnapshot() {
        history.push(dataFrame);
    }
    
    public Dataset<Row> restoreSnapshot() {
        if (!history.isEmpty()) {
            return history.pop();
        }
        throw new IllegalStateException("No snapshots to restore");
    }
}

// Concrete command: Filter
public class FilterCommand implements TransformationCommand {
    private final DataFrameContext context;
    private final String condition;
    private Dataset<Row> previousState;
    
    public FilterCommand(DataFrameContext context, String condition) {
        this.context = context;
        this.condition = condition;
    }
    
    @Override
    public void execute() {
        context.saveSnapshot();
        Dataset<Row> df = context.getDataFrame();
        previousState = df;
        context.setDataFrame(df.filter(condition));
        System.out.println("Executed: " + describe());
    }
    
    @Override
    public void undo() {
        if (previousState != null) {
            context.setDataFrame(previousState);
            System.out.println("Undid: " + describe());
        }
    }
    
    @Override
    public String describe() {
        return "Filter[" + condition + "]";
    }
}

// Concrete command: Select
public class SelectCommand implements TransformationCommand {
    private final DataFrameContext context;
    private final String[] columns;
    private Dataset<Row> previousState;
    
    public SelectCommand(DataFrameContext context, String... columns) {
        this.context = context;
        this.columns = columns;
    }
    
    @Override
    public void execute() {
        context.saveSnapshot();
        Dataset<Row> df = context.getDataFrame();
        previousState = df;
        context.setDataFrame(df.select(columns));
        System.out.println("Executed: " + describe());
    }
    
    @Override
    public void undo() {
        if (previousState != null) {
            context.setDataFrame(previousState);
            System.out.println("Undid: " + describe());
        }
    }
    
    @Override
    public String describe() {
        return "Select[" + String.join(", ", columns) + "]";
    }
}

// Concrete command: AddColumn
public class AddColumnCommand implements TransformationCommand {
    private final DataFrameContext context;
    private final String columnName;
    private final Column expression;
    private Dataset<Row> previousState;
    
    public AddColumnCommand(DataFrameContext context, String columnName, Column expression) {
        this.context = context;
        this.columnName = columnName;
        this.expression = expression;
    }
    
    @Override
    public void execute() {
        context.saveSnapshot();
        Dataset<Row> df = context.getDataFrame();
        previousState = df;
        context.setDataFrame(df.withColumn(columnName, expression));
        System.out.println("Executed: " + describe());
    }
    
    @Override
    public void undo() {
        if (previousState != null) {
            context.setDataFrame(previousState);
            System.out.println("Undid: " + describe());
        }
    }
    
    @Override
    public String describe() {
        return "AddColumn[" + columnName + "]";
    }
}

// Invoker: Manages command execution and history
public class TransformationInvoker {
    private final List<TransformationCommand> commandHistory = new ArrayList<>();
    private int currentIndex = -1;
    
    public void executeCommand(TransformationCommand command) {
        // Remove commands after current index (for redo)
        while (commandHistory.size() > currentIndex + 1) {
            commandHistory.remove(commandHistory.size() - 1);
        }
        
        command.execute();
        commandHistory.add(command);
        currentIndex++;
    }
    
    public void undo() {
        if (currentIndex >= 0) {
            TransformationCommand command = commandHistory.get(currentIndex);
            command.undo();
            currentIndex--;
        } else {
            System.out.println("Nothing to undo");
        }
    }
    
    public void redo() {
        if (currentIndex < commandHistory.size() - 1) {
            currentIndex++;
            TransformationCommand command = commandHistory.get(currentIndex);
            command.execute();
        } else {
            System.out.println("Nothing to redo");
        }
    }
    
    public void printHistory() {
        System.out.println("\n=== Command History ===");
        for (int i = 0; i < commandHistory.size(); i++) {
            String marker = (i == currentIndex) ? " <- current" : "";
            System.out.println(i + ". " + commandHistory.get(i).describe() + marker);
        }
    }
}

// Usage
public class Main {
    public static void main(String[] args) {
        SparkSession spark = SparkSession.builder()
            .appName("CommandExample")
            .master("local[*]")
            .getOrCreate();
        
        Dataset<Row> df = spark.read()
            .format("csv")
            .option("header", "true")
            .load("users.csv");
        
        DataFrameContext context = new DataFrameContext(df);
        TransformationInvoker invoker = new TransformationInvoker();
        
        // Execute commands
        invoker.executeCommand(new FilterCommand(context, "age >= 18"));
        invoker.executeCommand(new SelectCommand(context, "id", "name", "age"));
        invoker.executeCommand(new AddColumnCommand(context, "is_adult", functions.lit(true)));
        
        context.getDataFrame().show();
        invoker.printHistory();
        
        // Undo last command
        invoker.undo();
        context.getDataFrame().show();
        
        // Undo again
        invoker.undo();
        context.getDataFrame().show();
        
        // Redo
        invoker.redo();
        context.getDataFrame().show();
        
        invoker.printHistory();
        
        spark.stop();
        
        /*
         * Benefits:
         * - Commands are first-class objects
         * - Easy to implement undo/redo
         * - Can queue commands for batch execution
         * - Can log commands for audit trail
         * - Can replay commands for crash recovery
         */
    }
}
```

---

## 4. Template Method Pattern

### Intent
Define skeleton of algorithm in base class, let subclasses override specific steps without changing structure.

### When to Use (SDE-Data)
```
├─ ETL pipelines with common structure (Extract → Transform → Load)
├─ Data validation workflows
├─ Report generation with different formats
├─ Testing frameworks (setup → test → teardown)
```

### Example: ETL Pipeline Template

```java
/**
 * Abstract class: Defines ETL template
 */
public abstract class ETLPipeline {
    
    // Template method (final - cannot override)
    public final void execute() {
        try {
            // Step 1: Setup
            setup();
            
            // Step 2: Extract
            System.out.println("--- Extracting ---");
            List<Map<String, Object>> rawData = extract();
            System.out.println("Extracted " + rawData.size() + " records");
            
            // Step 3: Validate
            System.out.println("--- Validating ---");
            List<Map<String, Object>> validData = validate(rawData);
            System.out.println("Validated " + validData.size() + " records");
            
            // Step 4: Transform
            System.out.println("--- Transforming ---");
            List<Map<String, Object>> transformedData = transform(validData);
            System.out.println("Transformed " + transformedData.size() + " records");
            
            // Step 5: Load
            System.out.println("--- Loading ---");
            load(transformedData);
            System.out.println("Loaded successfully");
            
            // Step 6: Cleanup
            cleanup();
            
        } catch (Exception e) {
            handleError(e);
        }
    }
    
    // Abstract methods (must override)
    protected abstract List<Map<String, Object>> extract();
    protected abstract List<Map<String, Object>> transform(List<Map<String, Object>> data);
    protected abstract void load(List<Map<String, Object>> data);
    
    // Hook methods (optional override)
    protected void setup() {
        System.out.println("Default setup");
    }
    
    protected void cleanup() {
        System.out.println("Default cleanup");
    }
    
    protected List<Map<String, Object>> validate(List<Map<String, Object>> data) {
        // Default validation: filter out null records
        return data.stream()
            .filter(record -> record != null && !record.isEmpty())
            .collect(Collectors.toList());
    }
    
    protected void handleError(Exception e) {
        System.err.println("Pipeline failed: " + e.getMessage());
        e.printStackTrace();
    }
}

// Concrete implementation: CSV to Database ETL
public class CsvToDatabaseETL extends ETLPipeline {
    private final String csvFilePath;
    private final Connection dbConnection;
    private final String tableName;
    
    public CsvToDatabaseETL(String csvFilePath, Connection dbConnection, String tableName) {
        this.csvFilePath = csvFilePath;
        this.dbConnection = dbConnection;
        this.tableName = tableName;
    }
    
    @Override
    protected void setup() {
        System.out.println("Setting up CSV reader and DB connection");
        try {
            // Create table if not exists
            try (Statement stmt = dbConnection.createStatement()) {
                stmt.execute("CREATE TABLE IF NOT EXISTS " + tableName + " (id INT, name VARCHAR(100), age INT)");
            }
        } catch (SQLException e) {
            throw new RuntimeException("Setup failed", e);
        }
    }
    
    @Override
    protected List<Map<String, Object>> extract() {
        List<Map<String, Object>> records = new ArrayList<>();
        
        try (BufferedReader br = new BufferedReader(new FileReader(csvFilePath))) {
            String headerLine = br.readLine();
            String[] headers = headerLine.split(",");
            
            String line;
            while ((line = br.readLine()) != null) {
                String[] values = line.split(",");
                Map<String, Object> record = new HashMap<>();
                
                for (int i = 0; i < headers.length && i < values.length; i++) {
                    record.put(headers[i].trim(), values[i].trim());
                }
                records.add(record);
            }
        } catch (IOException e) {
            throw new RuntimeException("Extract failed", e);
        }
        
        return records;
    }
    
    @Override
    protected List<Map<String, Object>> validate(List<Map<String, Object>> data) {
        // Custom validation: age must be a number
        return data.stream()
            .filter(record -> {
                try {
                    Integer.parseInt(record.get("age").toString());
                    return true;
                } catch (NumberFormatException e) {
                    System.out.println("Invalid record: " + record);
                    return false;
                }
            })
            .collect(Collectors.toList());
    }
    
    @Override
    protected List<Map<String, Object>> transform(List<Map<String, Object>> data) {
        // Transform: Convert age to integer, uppercase names
        return data.stream()
            .map(record -> {
                Map<String, Object> transformed = new HashMap<>();
                transformed.put("id", Integer.parseInt(record.get("id").toString()));
                transformed.put("name", record.get("name").toString().toUpperCase());
                transformed.put("age", Integer.parseInt(record.get("age").toString()));
                return transformed;
            })
            .collect(Collectors.toList());
    }
    
    @Override
    protected void load(List<Map<String, Object>> data) {
        String sql = "INSERT INTO " + tableName + " (id, name, age) VALUES (?, ?, ?)";
        
        try (PreparedStatement pstmt = dbConnection.prepareStatement(sql)) {
            for (Map<String, Object> record : data) {
                pstmt.setInt(1, (Integer) record.get("id"));
                pstmt.setString(2, (String) record.get("name"));
                pstmt.setInt(3, (Integer) record.get("age"));
                pstmt.addBatch();
            }
            pstmt.executeBatch();
        } catch (SQLException e) {
            throw new RuntimeException("Load failed", e);
        }
    }
    
    @Override
    protected void cleanup() {
        System.out.println("Closing DB connection");
        try {
            dbConnection.close();
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}

// Another concrete implementation: JSON to S3 ETL
public class JsonToS3ETL extends ETLPipeline {
    private final String apiUrl;
    private final S3Client s3Client;
    private final String bucket;
    private final String key;
    
    public JsonToS3ETL(String apiUrl, S3Client s3Client, String bucket, String key) {
        this.apiUrl = apiUrl;
        this.s3Client = s3Client;
        this.bucket = bucket;
        this.key = key;
    }
    
    @Override
    protected List<Map<String, Object>> extract() {
        // Extract from REST API
        try {
            HttpClient client = HttpClient.newHttpClient();
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(apiUrl))
                .build();
            
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            
            ObjectMapper mapper = new ObjectMapper();
            return mapper.readValue(response.body(), new TypeReference<List<Map<String, Object>>>() {});
            
        } catch (Exception e) {
            throw new RuntimeException("Extract failed", e);
        }
    }
    
    @Override
    protected List<Map<String, Object>> transform(List<Map<String, Object>> data) {
        // Transform: Add timestamp
        return data.stream()
            .map(record -> {
                Map<String, Object> transformed = new HashMap<>(record);
                transformed.put("processed_at", System.currentTimeMillis());
                return transformed;
            })
            .collect(Collectors.toList());
    }
    
    @Override
    protected void load(List<Map<String, Object>> data) {
        try {
            ObjectMapper mapper = new ObjectMapper();
            String json = mapper.writeValueAsString(data);
            
            s3Client.putObject(
                PutObjectRequest.builder().bucket(bucket).key(key).build(),
                RequestBody.fromString(json)
            );
            
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Load failed", e);
        }
    }
}

// Usage
public class Main {
    public static void main(String[] args) throws SQLException {
        // ETL 1: CSV → Database
        Connection conn = DriverManager.getConnection("jdbc:h2:mem:test", "sa", "");
        ETLPipeline csvEtl = new CsvToDatabaseETL("users.csv", conn, "users");
        csvEtl.execute();
        
        System.out.println("\n================\n");
        
        // ETL 2: JSON API → S3
        S3Client s3 = S3Client.builder().build();
        ETLPipeline jsonEtl = new JsonToS3ETL(
            "https://api.example.com/users",
            s3,
            "my-bucket",
            "data/users.json"
        );
        jsonEtl.execute();
        
        /*
         * Benefits:
         * - Common ETL structure enforced (extract → validate → transform → load)
         * - Subclasses only implement data-source-specific logic
         * - Easy to add new ETL pipelines (just extend ETLPipeline)
         * - Hook methods allow optional customization
         */
    }
}
```

---

## 🎯 Behavioral Patterns Summary (Part 1)

| Pattern | Purpose | SDE-Data Use Case | Key Benefit |
|---------|---------|-------------------|-------------|
| **Strategy** | Interchangeable algorithms | Compression, partitioning, serialization | Runtime algorithm selection |
| **Observer** | One-to-many notification | Pipeline monitoring, alerting, metrics | Decoupled event handling |
| **Command** | Encapsulate requests as objects | Undo/redo, task queue, transaction log | Flexible request handling |
| **Template Method** | Algorithm skeleton with customizable steps | ETL pipelines, validation workflows | Code reuse + customization |

---

**Continue reading:** [State, Chain of Responsibility, Mediator, Memento, Visitor patterns below...]

---

## 5. State Pattern

### Intent
Allow object to alter its behavior when internal state changes. Object appears to change its class.

### When to Use (SDE-Data)
```
├─ State machines (pipeline states, order processing)
├─ Workflow engines (pending → running → completed → failed)
├─ Connection management (connected, disconnected, reconnecting)
```

### Example: Data Pipeline State Machine

```java
/**
 * State interface
 */
public interface PipelineState {
    void start(PipelineContext context);
    void pause(PipelineContext context);
    void resume(PipelineContext context);
    void complete(PipelineContext context);
    void fail(PipelineContext context);
    String getStateName();
}

// Context
public class PipelineContext {
    private PipelineState state;
    private final String pipelineId;
    private long startTime;
    private long endTime;
    
    public PipelineContext(String pipelineId) {
        this.pipelineId = pipelineId;
        this.state = new PendingState();  // Initial state
    }
    
    public void setState(PipelineState state) {
        System.out.println("State transition: " + this.state.getStateName() + " → " + state.getStateName());
        this.state = state;
    }
    
    public void start() {
        state.start(this);
    }
    
    public void pause() {
        state.pause(this);
    }
    
    public void resume() {
        state.resume(this);
    }
    
    public void complete() {
        state.complete(this);
    }
    
    public void fail() {
        state.fail(this);
    }
    
    public String getPipelineId() { return pipelineId; }
    public void setStartTime(long startTime) { this.startTime = startTime; }
    public void setEndTime(long endTime) { this.endTime = endTime; }
    public long getDuration() { return endTime - startTime; }
}

// Concrete state: Pending
public class PendingState implements PipelineState {
    @Override
    public void start(PipelineContext context) {
        context.setStartTime(System.currentTimeMillis());
        context.setState(new RunningState());
    }
    
    @Override
    public void pause(PipelineContext context) {
        System.out.println("Cannot pause pending pipeline");
    }
    
    @Override
    public void resume(PipelineContext context) {
        System.out.println("Cannot resume pending pipeline");
    }
    
    @Override
    public void complete(PipelineContext context) {
        System.out.println("Cannot complete pending pipeline");
    }
    
    @Override
    public void fail(PipelineContext context) {
        context.setState(new FailedState());
    }
    
    @Override
    public String getStateName() {
        return "PENDING";
    }
}

// Concrete state: Running
public class RunningState implements PipelineState {
    @Override
    public void start(PipelineContext context) {
        System.out.println("Pipeline already running");
    }
    
    @Override
    public void pause(PipelineContext context) {
        context.setState(new PausedState());
    }
    
    @Override
    public void resume(PipelineContext context) {
        System.out.println("Pipeline already running");
    }
    
    @Override
    public void complete(PipelineContext context) {
        context.setEndTime(System.currentTimeMillis());
        context.setState(new CompletedState());
        System.out.println("Pipeline completed in " + context.getDuration() + "ms");
    }
    
    @Override
    public void fail(PipelineContext context) {
        context.setEndTime(System.currentTimeMillis());
        context.setState(new FailedState());
    }
    
    @Override
    public String getStateName() {
        return "RUNNING";
    }
}

// Concrete state: Paused
public class PausedState implements PipelineState {
    @Override
    public void start(PipelineContext context) {
        System.out.println("Cannot start paused pipeline, use resume");
    }
    
    @Override
    public void pause(PipelineContext context) {
        System.out.println("Pipeline already paused");
    }
    
    @Override
    public void resume(PipelineContext context) {
        context.setState(new RunningState());
    }
    
    @Override
    public void complete(PipelineContext context) {
        System.out.println("Cannot complete paused pipeline");
    }
    
    @Override
    public void fail(PipelineContext context) {
        context.setState(new FailedState());
    }
    
    @Override
    public String getStateName() {
        return "PAUSED";
    }
}

// Concrete state: Completed
public class CompletedState implements PipelineState {
    @Override
    public void start(PipelineContext context) {
        System.out.println("Cannot restart completed pipeline");
    }
    
    @Override
    public void pause(PipelineContext context) {
        System.out.println("Cannot pause completed pipeline");
    }
    
    @Override
    public void resume(PipelineContext context) {
        System.out.println("Cannot resume completed pipeline");
    }
    
    @Override
    public void complete(PipelineContext context) {
        System.out.println("Pipeline already completed");
    }
    
    @Override
    public void fail(PipelineContext context) {
        System.out.println("Cannot fail completed pipeline");
    }
    
    @Override
    public String getStateName() {
        return "COMPLETED";
    }
}

// Concrete state: Failed
public class FailedState implements PipelineState {
    @Override
    public void start(PipelineContext context) {
        // Allow retry
        context.setState(new PendingState());
        context.start();
    }
    
    @Override
    public void pause(PipelineContext context) {
        System.out.println("Cannot pause failed pipeline");
    }
    
    @Override
    public void resume(PipelineContext context) {
        System.out.println("Cannot resume failed pipeline");
    }
    
    @Override
    public void complete(PipelineContext context) {
        System.out.println("Cannot complete failed pipeline");
    }
    
    @Override
    public void fail(PipelineContext context) {
        System.out.println("Pipeline already failed");
    }
    
    @Override
    public String getStateName() {
        return "FAILED";
    }
}

// Usage
public class Main {
    public static void main(String[] args) throws InterruptedException {
        PipelineContext pipeline = new PipelineContext("etl-pipeline-001");
        
        // State: PENDING
        pipeline.start();  // → RUNNING
        
        Thread.sleep(1000);
        
        // State: RUNNING
        pipeline.pause();  // → PAUSED
        
        // State: PAUSED
        pipeline.complete();  // Invalid, prints error
        pipeline.resume();    // → RUNNING
        
        Thread.sleep(500);
        
        // State: RUNNING
        pipeline.complete();  // → COMPLETED
        
        // State: COMPLETED
        pipeline.pause();  // Invalid
        
        System.out.println("\n=== Simulating failure ===");
        PipelineContext pipeline2 = new PipelineContext("etl-pipeline-002");
        pipeline2.start();   // → RUNNING
        pipeline2.fail();    // → FAILED
        pipeline2.start();   // Retry: FAILED → PENDING → RUNNING
        
        /*
         * Benefits:
         * - State-specific behavior encapsulated in separate classes
         * - Easy to add new states
         * - Invalid transitions prevented (fail-safe)
         * - No if-else chains for state checking
         */
    }
}
```

---

## 6. Chain of Responsibility Pattern

### Intent
Pass request along chain of handlers. Each handler decides to process or pass to next handler.

### When to Use (SDE-Data)
```
├─ Data validation chains (type check → range check → business logic check)
├─ Logging frameworks (debug → info → warn → error)
├─ Authentication/authorization filters
├─ ETL data quality checks
```

### Example: Data Validation Chain

```java
/**
 * Handler interface
 */
public abstract class ValidationHandler {
    protected ValidationHandler next;
    
    public ValidationHandler setNext(ValidationHandler next) {
        this.next = next;
        return next;
    }
    
    public abstract ValidationResult validate(Map<String, Object> record);
    
    protected ValidationResult validateNext(Map<String, Object> record) {
        if (next != null) {
            return next.validate(record);
        }
        return ValidationResult.success();
    }
}

// Validation result
public class ValidationResult {
    private final boolean valid;
    private final List<String> errors;
    
    private ValidationResult(boolean valid, List<String> errors) {
        this.valid = valid;
        this.errors = errors;
    }
    
    public static ValidationResult success() {
        return new ValidationResult(true, Collections.emptyList());
    }
    
    public static ValidationResult failure(String... errors) {
        return new ValidationResult(false, Arrays.asList(errors));
    }
    
    public boolean isValid() { return valid; }
    public List<String> getErrors() { return errors; }
}

// Concrete handler: Null check
public class NullCheckHandler extends ValidationHandler {
    private final String[] requiredFields;
    
    public NullCheckHandler(String... requiredFields) {
        this.requiredFields = requiredFields;
    }
    
    @Override
    public ValidationResult validate(Map<String, Object> record) {
        List<String> errors = new ArrayList<>();
        
        for (String field : requiredFields) {
            if (!record.containsKey(field) || record.get(field) == null) {
                errors.add("Field '" + field + "' is required");
            }
        }
        
        if (!errors.isEmpty()) {
            System.out.println("NullCheckHandler: " + errors.size() + " errors");
            return ValidationResult.failure(errors.toArray(new String[0]));
        }
        
        System.out.println("NullCheckHandler: PASS");
        return validateNext(record);
    }
}

// Concrete handler: Type check
public class TypeCheckHandler extends ValidationHandler {
    @Override
    public ValidationResult validate(Map<String, Object> record) {
        List<String> errors = new ArrayList<>();
        
        // Check age is integer
        Object age = record.get("age");
        if (age != null && !(age instanceof Integer)) {
            errors.add("Field 'age' must be an integer");
        }
        
        // Check email is string
        Object email = record.get("email");
        if (email != null && !(email instanceof String)) {
            errors.add("Field 'email' must be a string");
        }
        
        if (!errors.isEmpty()) {
            System.out.println("TypeCheckHandler: " + errors.size() + " errors");
            return ValidationResult.failure(errors.toArray(new String[0]));
        }
        
        System.out.println("TypeCheckHandler: PASS");
        return validateNext(record);
    }
}

// Concrete handler: Range check
public class RangeCheckHandler extends ValidationHandler {
    @Override
    public ValidationResult validate(Map<String, Object> record) {
        List<String> errors = new ArrayList<>();
        
        // Check age range
        Object age = record.get("age");
        if (age instanceof Integer) {
            int ageValue = (Integer) age;
            if (ageValue < 0 || ageValue > 150) {
                errors.add("Age must be between 0 and 150");
            }
        }
        
        if (!errors.isEmpty()) {
            System.out.println("RangeCheckHandler: " + errors.size() + " errors");
            return ValidationResult.failure(errors.toArray(new String[0]));
        }
        
        System.out.println("RangeCheckHandler: PASS");
        return validateNext(record);
    }
}

// Concrete handler: Format check
public class FormatCheckHandler extends ValidationHandler {
    private static final Pattern EMAIL_PATTERN = Pattern.compile("^[A-Za-z0-9+_.-]+@(.+)$");
    
    @Override
    public ValidationResult validate(Map<String, Object> record) {
        List<String> errors = new ArrayList<>();
        
        // Check email format
        Object email = record.get("email");
        if (email instanceof String) {
            if (!EMAIL_PATTERN.matcher((String) email).matches()) {
                errors.add("Invalid email format");
            }
        }
        
        if (!errors.isEmpty()) {
            System.out.println("FormatCheckHandler: " + errors.size() + " errors");
            return ValidationResult.failure(errors.toArray(new String[0]));
        }
        
        System.out.println("FormatCheckHandler: PASS");
        return validateNext(record);
    }
}

// Usage
public class DataValidator {
    public static void main(String[] args) {
        // Build validation chain
        ValidationHandler chain = new NullCheckHandler("name", "email", "age");
        chain.setNext(new TypeCheckHandler())
             .setNext(new RangeCheckHandler())
             .setNext(new FormatCheckHandler());
        
        // Test record 1: Valid
        Map<String, Object> record1 = Map.of(
            "name", "John Doe",
            "email", "john@example.com",
            "age", 30
        );
        
        System.out.println("=== Validating Record 1 ===");
        ValidationResult result1 = chain.validate(record1);
        System.out.println("Result: " + (result1.isValid() ? "VALID" : "INVALID"));
        
        // Test record 2: Missing field
        Map<String, Object> record2 = Map.of(
            "name", "Jane Doe",
            "age", 25
        );
        
        System.out.println("\n=== Validating Record 2 ===");
        ValidationResult result2 = chain.validate(record2);
        System.out.println("Result: " + (result2.isValid() ? "VALID" : "INVALID"));
        System.out.println("Errors: " + result2.getErrors());
        
        // Test record 3: Invalid age range
        Map<String, Object> record3 = Map.of(
            "name", "Bob Smith",
            "email", "bob@example.com",
            "age", 200
        );
        
        System.out.println("\n=== Validating Record 3 ===");
        ValidationResult result3 = chain.validate(record3);
        System.out.println("Result: " + (result3.isValid() ? "VALID" : "INVALID"));
        System.out.println("Errors: " + result3.getErrors());
        
        /*
         * Benefits:
         * - Easy to add/remove validators
         * - Validators are independent and reusable
         * - Short-circuit on first failure (optional)
         * - Clear separation of concerns
         */
    }
}
```

---

## 7. Iterator Pattern

### Intent
Provide way to access elements of aggregate object sequentially without exposing underlying representation.

### When to Use (SDE-Data)
```
├─ Traverse custom data structures
├─ Lazy loading of large datasets
├─ Streaming data from external sources
├─ Pagination through query results
```

### Example: Paginated Query Iterator

```java
/**
 * Iterator interface
 */
public interface DataIterator<T> {
    boolean hasNext();
    T next();
}

// Aggregate interface
public interface DataCollection<T> {
    DataIterator<T> iterator();
}

// Concrete iterator: Paginated database query
public class PaginatedQueryIterator implements DataIterator<Map<String, Object>> {
    private final Connection connection;
    private final String query;
    private final int pageSize;
    private int currentPage = 0;
    private List<Map<String, Object>> currentBatch;
    private int currentIndex = 0;
    
    public PaginatedQueryIterator(Connection connection, String query, int pageSize) {
        this.connection = connection;
        this.query = query;
        this.pageSize = pageSize;
        loadNextBatch();
    }
    
    @Override
    public boolean hasNext() {
        if (currentIndex < currentBatch.size()) {
            return true;
        }
        
        // Try to load next batch
        loadNextBatch();
        return !currentBatch.isEmpty();
    }
    
    @Override
    public Map<String, Object> next() {
        if (!hasNext()) {
            throw new NoSuchElementException("No more elements");
        }
        return currentBatch.get(currentIndex++);
    }
    
    private void loadNextBatch() {
        currentBatch = new ArrayList<>();
        currentIndex = 0;
        
        String paginatedQuery = query + " LIMIT " + pageSize + " OFFSET " + (currentPage * pageSize);
        
        try (Statement stmt = connection.createStatement();
             ResultSet rs = stmt.executeQuery(paginatedQuery)) {
            
            ResultSetMetaData metaData = rs.getMetaData();
            int columnCount = metaData.getColumnCount();
            
            while (rs.next()) {
                Map<String, Object> row = new HashMap<>();
                for (int i = 1; i <= columnCount; i++) {
                    row.put(metaData.getColumnName(i), rs.getObject(i));
                }
                currentBatch.add(row);
            }
            
            System.out.println("Loaded page " + currentPage + ": " + currentBatch.size() + " records");
            currentPage++;
            
        } catch (SQLException e) {
            throw new RuntimeException("Failed to load batch", e);
        }
    }
}

// Concrete collection
public class DatabaseTable implements DataCollection<Map<String, Object>> {
    private final Connection connection;
    private final String tableName;
    private final int pageSize;
    
    public DatabaseTable(Connection connection, String tableName, int pageSize) {
        this.connection = connection;
        this.tableName = tableName;
        this.pageSize = pageSize;
    }
    
    @Override
    public DataIterator<Map<String, Object>> iterator() {
        String query = "SELECT * FROM " + tableName;
        return new PaginatedQueryIterator(connection, query, pageSize);
    }
}

// Usage
public class Main {
    public static void main(String[] args) throws SQLException {
        Connection connection = DriverManager.getConnection("jdbc:h2:mem:test", "sa", "");
        
        // Create sample table
        try (Statement stmt = connection.createStatement()) {
            stmt.execute("CREATE TABLE users (id INT, name VARCHAR(100), age INT)");
            for (int i = 1; i <= 100; i++) {
                stmt.execute("INSERT INTO users VALUES (" + i + ", 'User" + i + "', " + (20 + i % 50) + ")");
            }
        }
        
        // Iterate with pagination (page size = 10)
        DatabaseTable table = new DatabaseTable(connection, "users", 10);
        DataIterator<Map<String, Object>> iterator = table.iterator();
        
        int count = 0;
        while (iterator.hasNext()) {
            Map<String, Object> row = iterator.next();
            System.out.println(row);
            count++;
            
            if (count >= 25) {
                System.out.println("... (showing first 25 records only)");
                break;
            }
        }
        
        System.out.println("\nTotal records read: " + count);
        
        connection.close();
        
        /*
         * Benefits:
         * - Memory efficient (loads 10 records at a time, not all 100)
         * - Client code doesn't know about pagination
         * - Can switch to different iteration strategy without changing client
         */
    }
}
```

### Real-World: S3 Object Iterator

```java
/**
 * SDE-Data: Iterate over S3 objects with pagination
 */
public class S3ObjectIterator implements Iterator<S3Object> {
    private final S3Client s3Client;
    private final String bucket;
    private final String prefix;
    private String continuationToken;
    private List<S3Object> currentBatch;
    private int currentIndex;
    private boolean hasMorePages;
    
    public S3ObjectIterator(S3Client s3Client, String bucket, String prefix) {
        this.s3Client = s3Client;
        this.bucket = bucket;
        this.prefix = prefix;
        this.hasMorePages = true;
        loadNextBatch();
    }
    
    @Override
    public boolean hasNext() {
        if (currentIndex < currentBatch.size()) {
            return true;
        }
        
        if (hasMorePages) {
            loadNextBatch();
            return !currentBatch.isEmpty();
        }
        
        return false;
    }
    
    @Override
    public S3Object next() {
        if (!hasNext()) {
            throw new NoSuchElementException();
        }
        return currentBatch.get(currentIndex++);
    }
    
    private void loadNextBatch() {
        currentBatch = new ArrayList<>();
        currentIndex = 0;
        
        ListObjectsV2Request.Builder requestBuilder = ListObjectsV2Request.builder()
            .bucket(bucket)
            .prefix(prefix)
            .maxKeys(1000);
        
        if (continuationToken != null) {
            requestBuilder.continuationToken(continuationToken);
        }
        
        ListObjectsV2Response response = s3Client.listObjectsV2(requestBuilder.build());
        currentBatch.addAll(response.contents());
        
        hasMorePages = response.isTruncated();
        continuationToken = response.nextContinuationToken();
        
        System.out.println("Loaded batch: " + currentBatch.size() + " objects, more pages: " + hasMorePages);
    }
}

// Usage
public class S3DataProcessor {
    public static void main(String[] args) {
        S3Client s3Client = S3Client.builder().build();
        
        S3ObjectIterator iterator = new S3ObjectIterator(s3Client, "my-bucket", "data/");
        
        while (iterator.hasNext()) {
            S3Object obj = iterator.next();
            System.out.println("Processing: " + obj.key() + " (" + obj.size() + " bytes)");
        }
        
        /*
         * Handles S3 pagination automatically:
         * - S3 returns max 1000 objects per request
         * - Iterator loads next page when current page exhausted
         * - Client code doesn't need to know about continuation tokens
         */
    }
}
```

---

## 8. Mediator Pattern

### Intent
Define object that encapsulates how set of objects interact. Promotes loose coupling by keeping objects from referring to each other explicitly.

### When to Use (SDE-Data)
```
├─ Complex communication between components
├─ Event bus / message broker
├─ Workflow orchestration
├─ Reduce many-to-many relationships to one-to-many
```

### Example: Data Pipeline Orchestrator

```java
/**
 * Mediator interface
 */
public interface PipelineMediator {
    void registerComponent(PipelineComponent component);
    void notify(PipelineComponent sender, String event, Map<String, Object> data);
}

// Component interface
public abstract class PipelineComponent {
    protected PipelineMediator mediator;
    protected String name;
    
    public PipelineComponent(String name) {
        this.name = name;
    }
    
    public void setMediator(PipelineMediator mediator) {
        this.mediator = mediator;
    }
    
    public String getName() {
        return name;
    }
}

// Concrete component: Data extractor
public class DataExtractor extends PipelineComponent {
    public DataExtractor() {
        super("Extractor");
    }
    
    public void extract() {
        System.out.println("[Extractor] Extracting data from source...");
        
        // Simulate extraction
        List<Map<String, Object>> data = List.of(
            Map.of("id", 1, "name", "Alice", "age", 30),
            Map.of("id", 2, "name", "Bob", "age", 25)
        );
        
        Map<String, Object> payload = new HashMap<>();
        payload.put("data", data);
        payload.put("recordCount", data.size());
        
        // Notify mediator
        mediator.notify(this, "DATA_EXTRACTED", payload);
    }
}

// Concrete component: Data transformer
public class DataTransformer extends PipelineComponent {
    public DataTransformer() {
        super("Transformer");
    }
    
    public void transform(List<Map<String, Object>> data) {
        System.out.println("[Transformer] Transforming " + data.size() + " records...");
        
        // Simulate transformation
        List<Map<String, Object>> transformed = data.stream()
            .map(record -> {
                Map<String, Object> newRecord = new HashMap<>(record);
                newRecord.put("processed", true);
                return newRecord;
            })
            .collect(Collectors.toList());
        
        Map<String, Object> payload = new HashMap<>();
        payload.put("data", transformed);
        payload.put("recordCount", transformed.size());
        
        mediator.notify(this, "DATA_TRANSFORMED", payload);
    }
}

// Concrete component: Data loader
public class DataLoader extends PipelineComponent {
    public DataLoader() {
        super("Loader");
    }
    
    public void load(List<Map<String, Object>> data) {
        System.out.println("[Loader] Loading " + data.size() + " records to destination...");
        
        // Simulate loading
        System.out.println("[Loader] Successfully loaded data");
        
        Map<String, Object> payload = new HashMap<>();
        payload.put("recordCount", data.size());
        
        mediator.notify(this, "DATA_LOADED", payload);
    }
}

// Concrete component: Metrics collector
public class MetricsCollector extends PipelineComponent {
    private int extractedCount = 0;
    private int transformedCount = 0;
    private int loadedCount = 0;
    
    public MetricsCollector() {
        super("MetricsCollector");
    }
    
    public void recordExtraction(int count) {
        extractedCount += count;
        System.out.println("[Metrics] Extraction: " + extractedCount + " total records");
    }
    
    public void recordTransformation(int count) {
        transformedCount += count;
        System.out.println("[Metrics] Transformation: " + transformedCount + " total records");
    }
    
    public void recordLoad(int count) {
        loadedCount += count;
        System.out.println("[Metrics] Load: " + loadedCount + " total records");
    }
    
    public void printSummary() {
        System.out.println("\n=== Pipeline Metrics ===");
        System.out.println("Extracted: " + extractedCount);
        System.out.println("Transformed: " + transformedCount);
        System.out.println("Loaded: " + loadedCount);
    }
}

// Concrete mediator
public class ETLPipelineMediator implements PipelineMediator {
    private DataExtractor extractor;
    private DataTransformer transformer;
    private DataLoader loader;
    private MetricsCollector metrics;
    
    @Override
    public void registerComponent(PipelineComponent component) {
        component.setMediator(this);
        
        if (component instanceof DataExtractor) {
            extractor = (DataExtractor) component;
        } else if (component instanceof DataTransformer) {
            transformer = (DataTransformer) component;
        } else if (component instanceof DataLoader) {
            loader = (DataLoader) component;
        } else if (component instanceof MetricsCollector) {
            metrics = (MetricsCollector) component;
        }
    }
    
    @Override
    public void notify(PipelineComponent sender, String event, Map<String, Object> data) {
        System.out.println("[Mediator] Received event: " + event + " from " + sender.getName());
        
        switch (event) {
            case "DATA_EXTRACTED":
                @SuppressWarnings("unchecked")
                List<Map<String, Object>> extractedData = (List<Map<String, Object>>) data.get("data");
                int extractedCount = (int) data.get("recordCount");
                
                metrics.recordExtraction(extractedCount);
                transformer.transform(extractedData);
                break;
                
            case "DATA_TRANSFORMED":
                @SuppressWarnings("unchecked")
                List<Map<String, Object>> transformedData = (List<Map<String, Object>>) data.get("data");
                int transformedCount = (int) data.get("recordCount");
                
                metrics.recordTransformation(transformedCount);
                loader.load(transformedData);
                break;
                
            case "DATA_LOADED":
                int loadedCount = (int) data.get("recordCount");
                metrics.recordLoad(loadedCount);
                metrics.printSummary();
                break;
        }
    }
}

// Usage
public class Main {
    public static void main(String[] args) {
        // Create mediator
        ETLPipelineMediator mediator = new ETLPipelineMediator();
        
        // Create components
        DataExtractor extractor = new DataExtractor();
        DataTransformer transformer = new DataTransformer();
        DataLoader loader = new DataLoader();
        MetricsCollector metrics = new MetricsCollector();
        
        // Register components with mediator
        mediator.registerComponent(extractor);
        mediator.registerComponent(transformer);
        mediator.registerComponent(loader);
        mediator.registerComponent(metrics);
        
        // Start pipeline
        extractor.extract();
        
        /*
         * Output:
         * [Extractor] Extracting data from source...
         * [Mediator] Received event: DATA_EXTRACTED from Extractor
         * [Metrics] Extraction: 2 total records
         * [Transformer] Transforming 2 records...
         * [Mediator] Received event: DATA_TRANSFORMED from Transformer
         * [Metrics] Transformation: 2 total records
         * [Loader] Loading 2 records to destination...
         * [Loader] Successfully loaded data
         * [Mediator] Received event: DATA_LOADED from Loader
         * [Metrics] Load: 2 total records
         * 
         * === Pipeline Metrics ===
         * Extracted: 2
         * Transformed: 2
         * Loaded: 2
         * 
         * Benefits:
         * - Components don't know about each other
         * - Mediator controls workflow
         * - Easy to add new components (just register with mediator)
         * - Reduced coupling (N components = N connections to mediator, not N² connections)
         */
    }
}
```

---

## 9. Memento Pattern

### Intent
Capture and externalize object's internal state so object can be restored later, without violating encapsulation.

### When to Use (SDE-Data)
```
├─ Undo/redo functionality
├─ Checkpointing (Spark, Flink)
├─ Transaction rollback
├─ Save/restore application state
```

### Example: Spark DataFrame Checkpointing

```java
/**
 * Memento: Saves DataFrame state
 */
public class DataFrameMemento {
    private final String checkpointPath;
    private final long timestamp;
    
    public DataFrameMemento(String checkpointPath) {
        this.checkpointPath = checkpointPath;
        this.timestamp = System.currentTimeMillis();
    }
    
    public String getCheckpointPath() {
        return checkpointPath;
    }
    
    public long getTimestamp() {
        return timestamp;
    }
}

// Originator: DataFrame wrapper
public class StatefulDataFrame {
    private Dataset<Row> dataFrame;
    private final SparkSession spark;
    private int version = 0;
    
    public StatefulDataFrame(SparkSession spark, Dataset<Row> dataFrame) {
        this.spark = spark;
        this.dataFrame = dataFrame;
    }
    
    public void filter(String condition) {
        dataFrame = dataFrame.filter(condition);
        version++;
        System.out.println("Applied filter: " + condition + " (version " + version + ")");
    }
    
    public void select(String... columns) {
        dataFrame = dataFrame.select(columns);
        version++;
        System.out.println("Applied select: " + String.join(", ", columns) + " (version " + version + ")");
    }
    
    public void withColumn(String columnName, Column expression) {
        dataFrame = dataFrame.withColumn(columnName, expression);
        version++;
        System.out.println("Added column: " + columnName + " (version " + version + ")");
    }
    
    public Dataset<Row> getDataFrame() {
        return dataFrame;
    }
    
    // Create memento (checkpoint)
    public DataFrameMemento save(String checkpointDir) {
        String checkpointPath = checkpointDir + "/checkpoint-" + version + "-" + System.currentTimeMillis();
        
        dataFrame.write()
            .mode("overwrite")
            .parquet(checkpointPath);
        
        System.out.println("Saved checkpoint: " + checkpointPath);
        return new DataFrameMemento(checkpointPath);
    }
    
    // Restore from memento
    public void restore(DataFrameMemento memento) {
        dataFrame = spark.read().parquet(memento.getCheckpointPath());
        System.out.println("Restored from checkpoint: " + memento.getCheckpointPath());
    }
}

// Caretaker: Manages mementos
public class CheckpointManager {
    private final Map<String, DataFrameMemento> checkpoints = new HashMap<>();
    
    public void saveCheckpoint(String name, DataFrameMemento memento) {
        checkpoints.put(name, memento);
        System.out.println("Checkpoint '" + name + "' saved");
    }
    
    public DataFrameMemento getCheckpoint(String name) {
        DataFrameMemento memento = checkpoints.get(name);
        if (memento == null) {
            throw new IllegalArgumentException("Checkpoint not found: " + name);
        }
        return memento;
    }
    
    public void listCheckpoints() {
        System.out.println("\n=== Available Checkpoints ===");
        checkpoints.forEach((name, memento) -> {
            System.out.println(name + ": " + new Date(memento.getTimestamp()));
        });
    }
}

// Usage
public class Main {
    public static void main(String[] args) {
        SparkSession spark = SparkSession.builder()
            .appName("MementoExample")
            .master("local[*]")
            .getOrCreate();
        
        Dataset<Row> df = spark.read()
            .format("csv")
            .option("header", "true")
            .load("users.csv");
        
        StatefulDataFrame statefulDf = new StatefulDataFrame(spark, df);
        CheckpointManager checkpointManager = new CheckpointManager();
        
        // Original state
        statefulDf.getDataFrame().show(5);
        
        // Transformation 1: Filter
        statefulDf.filter("age >= 18");
        DataFrameMemento checkpoint1 = statefulDf.save("/tmp/checkpoints");
        checkpointManager.saveCheckpoint("after_filter", checkpoint1);
        
        // Transformation 2: Select
        statefulDf.select("id", "name", "age");
        DataFrameMemento checkpoint2 = statefulDf.save("/tmp/checkpoints");
        checkpointManager.saveCheckpoint("after_select", checkpoint2);
        
        // Transformation 3: Add column
        statefulDf.withColumn("is_adult", functions.lit(true));
        
        statefulDf.getDataFrame().show(5);
        
        // List checkpoints
        checkpointManager.listCheckpoints();
        
        // Restore to earlier state
        System.out.println("\n=== Restoring to 'after_filter' checkpoint ===");
        statefulDf.restore(checkpointManager.getCheckpoint("after_filter"));
        statefulDf.getDataFrame().show(5);
        
        spark.stop();
        
        /*
         * Benefits:
         * - Can rollback to any previous state
         * - Originator's internal structure hidden (encapsulation)
         * - Useful for long-running Spark jobs (checkpoint intermediate results)
         * - Recover from failures (restore last checkpoint)
         */
    }
}
```

---

## 10. Visitor Pattern

### Intent
Separate algorithm from object structure. Add new operations without modifying classes.

### When to Use (SDE-Data)
```
├─ Perform operations on heterogeneous object structures
├─ Add new operations frequently (Open/Closed Principle)
├─ Schema transformations (JSON → Avro, Avro → Parquet)
├─ Query plan optimization
```

### Example: Schema Visitor

```java
/**
 * Element interface
 */
public interface SchemaElement {
    void accept(SchemaVisitor visitor);
}

// Concrete elements
public class StringField implements SchemaElement {
    private final String name;
    private final int maxLength;
    
    public StringField(String name, int maxLength) {
        this.name = name;
        this.maxLength = maxLength;
    }
    
    public String getName() { return name; }
    public int getMaxLength() { return maxLength; }
    
    @Override
    public void accept(SchemaVisitor visitor) {
        visitor.visitStringField(this);
    }
}

public class IntegerField implements SchemaElement {
    private final String name;
    
    public IntegerField(String name) {
        this.name = name;
    }
    
    public String getName() { return name; }
    
    @Override
    public void accept(SchemaVisitor visitor) {
        visitor.visitIntegerField(this);
    }
}

public class NestedField implements SchemaElement {
    private final String name;
    private final List<SchemaElement> fields;
    
    public NestedField(String name, List<SchemaElement> fields) {
        this.name = name;
        this.fields = fields;
    }
    
    public String getName() { return name; }
    public List<SchemaElement> getFields() { return fields; }
    
    @Override
    public void accept(SchemaVisitor visitor) {
        visitor.visitNestedField(this);
    }
}

/**
 * Visitor interface
 */
public interface SchemaVisitor {
    void visitStringField(StringField field);
    void visitIntegerField(IntegerField field);
    void visitNestedField(NestedField field);
}

// Concrete visitor: SQL DDL generator
public class SqlDdlVisitor implements SchemaVisitor {
    private final StringBuilder ddl = new StringBuilder();
    private int indentLevel = 0;
    
    @Override
    public void visitStringField(StringField field) {
        indent();
        ddl.append(field.getName()).append(" VARCHAR(").append(field.getMaxLength()).append(")");
    }
    
    @Override
    public void visitIntegerField(IntegerField field) {
        indent();
        ddl.append(field.getName()).append(" INT");
    }
    
    @Override
    public void visitNestedField(NestedField field) {
        indent();
        ddl.append(field.getName()).append(" STRUCT<\n");
        
        indentLevel++;
        for (int i = 0; i < field.getFields().size(); i++) {
            field.getFields().get(i).accept(this);
            if (i < field.getFields().size() - 1) {
                ddl.append(",\n");
            }
        }
        indentLevel--;
        
        ddl.append("\n");
        indent();
        ddl.append(">");
    }
    
    private void indent() {
        for (int i = 0; i < indentLevel; i++) {
            ddl.append("  ");
        }
    }
    
    public String getDdl() {
        return ddl.toString();
    }
}

// Concrete visitor: Avro schema generator
public class AvroSchemaVisitor implements SchemaVisitor {
    private final List<Map<String, Object>> fields = new ArrayList<>();
    
    @Override
    public void visitStringField(StringField field) {
        Map<String, Object> avroField = new HashMap<>();
        avroField.put("name", field.getName());
        avroField.put("type", "string");
        fields.add(avroField);
    }
    
    @Override
    public void visitIntegerField(IntegerField field) {
        Map<String, Object> avroField = new HashMap<>();
        avroField.put("name", field.getName());
        avroField.put("type", "int");
        fields.add(avroField);
    }
    
    @Override
    public void visitNestedField(NestedField field) {
        AvroSchemaVisitor nestedVisitor = new AvroSchemaVisitor();
        for (SchemaElement element : field.getFields()) {
            element.accept(nestedVisitor);
        }
        
        Map<String, Object> recordType = new HashMap<>();
        recordType.put("type", "record");
        recordType.put("name", field.getName() + "_record");
        recordType.put("fields", nestedVisitor.fields);
        
        Map<String, Object> avroField = new HashMap<>();
        avroField.put("name", field.getName());
        avroField.put("type", recordType);
        fields.add(avroField);
    }
    
    public String getAvroSchema(String recordName) {
        Map<String, Object> schema = new HashMap<>();
        schema.put("type", "record");
        schema.put("name", recordName);
        schema.put("fields", fields);
        
        try {
            ObjectMapper mapper = new ObjectMapper();
            return mapper.writerWithDefaultPrettyPrinter().writeValueAsString(schema);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Failed to generate Avro schema", e);
        }
    }
}

// Concrete visitor: Size calculator
public class SizeCalculatorVisitor implements SchemaVisitor {
    private int totalSize = 0;
    
    @Override
    public void visitStringField(StringField field) {
        totalSize += field.getMaxLength();
    }
    
    @Override
    public void visitIntegerField(IntegerField field) {
        totalSize += 4;  // 4 bytes for int
    }
    
    @Override
    public void visitNestedField(NestedField field) {
        for (SchemaElement element : field.getFields()) {
            element.accept(this);
        }
    }
    
    public int getTotalSize() {
        return totalSize;
    }
}

// Usage
public class Main {
    public static void main(String[] args) {
        // Define schema
        List<SchemaElement> schema = List.of(
            new IntegerField("id"),
            new StringField("name", 100),
            new IntegerField("age"),
            new NestedField("address", List.of(
                new StringField("street", 200),
                new StringField("city", 50),
                new StringField("zipcode", 10)
            ))
        );
        
        // Visitor 1: Generate SQL DDL
        SqlDdlVisitor sqlVisitor = new SqlDdlVisitor();
        for (SchemaElement element : schema) {
            element.accept(sqlVisitor);
            System.out.println(sqlVisitor.getDdl());
            // Reset for next field (in real code, structure better)
        }
        
        // Visitor 2: Generate Avro schema
        AvroSchemaVisitor avroVisitor = new AvroSchemaVisitor();
        for (SchemaElement element : schema) {
            element.accept(avroVisitor);
        }
        System.out.println("\n=== Avro Schema ===");
        System.out.println(avroVisitor.getAvroSchema("User"));
        
        // Visitor 3: Calculate size
        SizeCalculatorVisitor sizeVisitor = new SizeCalculatorVisitor();
        for (SchemaElement element : schema) {
            element.accept(sizeVisitor);
        }
        System.out.println("\n=== Estimated Size ===");
        System.out.println(sizeVisitor.getTotalSize() + " bytes");
        
        /*
         * Benefits:
         * - Add new operations (visitors) without modifying schema elements
         * - Separate concerns: schema structure vs operations on schema
         * - Can traverse complex object structures easily
         * 
         * Use case: Schema evolution
         * - Generate DDL for different databases (MySQL, PostgreSQL, Redshift)
         * - Convert between formats (JSON schema, Avro schema, Protobuf)
         * - Validate schema constraints
         */
    }
}
```

---

## 🎯 Final Key Takeaways

### Pattern Selection Guide for SDE-Data Interviews

**Data Processing:**
- **Strategy**: Multiple compression/serialization formats
- **Template Method**: ETL pipeline skeleton
- **Chain of Responsibility**: Data validation pipeline

**System Monitoring:**
- **Observer**: Pipeline monitoring, metrics collection, alerting
- **State**: Pipeline lifecycle management

**Flexibility:**
- **Command**: Undo/redo transformations, task queuing, transaction log

**Interview Red Flags:**
- ❌ Using if-else for algorithm selection → Use Strategy
- ❌ God class with many responsibilities → Use Observer, Chain of Responsibility
- ❌ Tight coupling between components → Use Observer, Mediator
- ❌ Copy-paste code with slight variations → Use Template Method

---

**Next:** [CASE-STUDIES.md](../03-CASE-STUDIES/README.md) — Real LLD interview problems (Parking Lot, LRU Cache, Rate Limiter, URL Shortener)

---

## 📊 Complete Pattern Comparison Matrix

| Pattern | Complexity | When to Use | Real-World Example | Thread-Safe? |
|---------|------------|-------------|-------------------|--------------|
| **Strategy** | ⭐⭐ | Multiple algorithms needed | Compression (Gzip/Snappy/LZ4) | Yes (if stateless) |
| **Observer** | ⭐⭐ | Event notification to multiple listeners | Pipeline monitoring | Use CopyOnWriteArrayList |
| **Command** | ⭐⭐⭐ | Undo/redo, queuing, logging | Transformation history | Yes (immutable commands) |
| **Template Method** | ⭐⭐ | Common algorithm structure | ETL pipelines | Yes (if stateless) |
| **Iterator** | ⭐⭐ | Traverse without exposing structure | S3 pagination | Depends on implementation |
| **State** | ⭐⭐⭐ | Object behavior changes with state | Pipeline lifecycle | Use AtomicReference |
| **Chain of Responsibility** | ⭐⭐ | Sequential request processing | Data validation | Yes (if stateless) |
| **Mediator** | ⭐⭐⭐⭐ | Complex component communication | Workflow orchestration | Synchronize mediator |
| **Memento** | ⭐⭐⭐ | Save/restore state | Spark checkpointing | Yes (immutable mementos) |
| **Visitor** | ⭐⭐⭐⭐ | Add operations to object structure | Schema transformation | Yes (if stateless) |

---

## 🔥 Production Best Practices

### 1. Strategy Pattern - Caching Strategies
```java
// Registry pattern for strategies
public class StrategyRegistry {
    private static final Map<String, CompressionStrategy> strategies = new ConcurrentHashMap<>();
    
    static {
        register("gzip", new GzipCompression());
        register("snappy", new SnappyCompression());
        register("lz4", new Lz4Compression());
    }
    
    public static void register(String name, CompressionStrategy strategy) {
        strategies.put(name, strategy);
    }
    
    public static CompressionStrategy get(String name) {
        CompressionStrategy strategy = strategies.get(name);
        if (strategy == null) {
            throw new IllegalArgumentException("Unknown strategy: " + name);
        }
        return strategy;
    }
}
```

### 2. Observer Pattern - Async Notifications
```java
// ❌ BAD: Blocking notification
public void notifyObservers(Event event) {
    for (Observer observer : observers) {
        observer.onEvent(event);  // Blocks if observer is slow!
    }
}

// ✅ GOOD: Async notification
private final ExecutorService executor = Executors.newFixedThreadPool(10);

public void notifyObservers(Event event) {
    for (Observer observer : observers) {
        executor.submit(() -> {
            try {
                observer.onEvent(event);
            } catch (Exception e) {
                logger.error("Observer failed", e);
            }
        });
    }
}
```

### 3. Command Pattern - Transaction Log
```java
// Commands can be serialized for audit trail
public interface SerializableCommand extends Command, Serializable {
    String getCommandId();
    long getTimestamp();
    String getUserId();
}

// Write to transaction log
public class TransactionLog {
    public void logCommand(SerializableCommand command) throws IOException {
        try (ObjectOutputStream oos = new ObjectOutputStream(
            new FileOutputStream("transaction.log", true))) {
            oos.writeObject(command);
        }
    }
    
    // Replay commands for disaster recovery
    public void replayLog() throws IOException, ClassNotFoundException {
        try (ObjectInputStream ois = new ObjectInputStream(
            new FileInputStream("transaction.log"))) {
            while (true) {
                SerializableCommand command = (SerializableCommand) ois.readObject();
                command.execute();
            }
        } catch (EOFException e) {
            // End of file
        }
    }
}
```

### 4. State Pattern - Finite State Machine Validation
```java
// Define valid transitions
public enum PipelineStateEnum {
    PENDING(Set.of(RUNNING, FAILED)),
    RUNNING(Set.of(PAUSED, COMPLETED, FAILED)),
    PAUSED(Set.of(RUNNING, FAILED)),
    COMPLETED(Set.of()),  // Terminal state
    FAILED(Set.of(PENDING));  // Can retry
    
    private final Set<PipelineStateEnum> allowedTransitions;
    
    PipelineStateEnum(Set<PipelineStateEnum> allowedTransitions) {
        this.allowedTransitions = allowedTransitions;
    }
    
    public boolean canTransitionTo(PipelineStateEnum newState) {
        return allowedTransitions.contains(newState);
    }
}

// Validate transitions
public void setState(PipelineState newState) {
    if (!currentState.canTransitionTo(newState.getEnum())) {
        throw new IllegalStateException("Invalid transition: " + 
            currentState + " → " + newState);
    }
    this.state = newState;
}
```

---

## 💼 Interview War Stories

### Story 1: Observer Pattern Disaster
**Problem:** Implemented Observer for pipeline monitoring. One observer (Slack alerting) had network timeout. **Entire pipeline blocked** waiting for Slack webhook!

**Fix:** 
1. Async notifications with ExecutorService
2. Timeout on each observer (fail fast)
3. Circuit breaker for external dependencies

```java
public void notifyObservers(Event event) {
    for (Observer observer : observers) {
        executor.submit(() -> {
            try {
                Future<?> future = executor.submit(() -> observer.onEvent(event));
                future.get(5, TimeUnit.SECONDS);  // 5s timeout
            } catch (TimeoutException e) {
                logger.warn("Observer timed out: " + observer.getClass().getName());
            } catch (Exception e) {
                logger.error("Observer failed", e);
            }
        });
    }
}
```

### Story 2: Command Pattern Memory Leak
**Problem:** Stored every command in history for undo/redo. After 1 week, **8GB of memory** consumed!

**Fix:**
1. Bounded history (keep last 100 commands)
2. Clear history after checkpointing
3. Use WeakReference for large data

```java
private final Deque<WeakReference<Command>> history = new ArrayDeque<>();
private static final int MAX_HISTORY = 100;

public void execute(Command cmd) {
    cmd.execute();
    history.addLast(new WeakReference<>(cmd));
    
    if (history.size() > MAX_HISTORY) {
        history.removeFirst();
    }
}
```

### Story 3: State Pattern Race Condition
**Problem:** Multiple threads transitioned pipeline state simultaneously. **Data corruption** (loaded twice)!

**Fix:** Use AtomicReference with compareAndSet

```java
private final AtomicReference<PipelineState> state = new AtomicReference<>(new PendingState());

public void complete() {
    PipelineState currentState = state.get();
    if (currentState instanceof RunningState) {
        if (state.compareAndSet(currentState, new CompletedState())) {
            // Only one thread wins
            performCleanup();
        }
    }
}
```

---

## 🎯 LeetCode-Style Practice Problems

### Problem 1: Logger System (Chain of Responsibility)
Design a logger with multiple levels (DEBUG < INFO < WARN < ERROR). Each handler decides whether to log and whether to pass to next handler.

**Expected Interface:**
```java
public interface Logger {
    void log(LogLevel level, String message);
}

public enum LogLevel {
    DEBUG(1), INFO(2), WARN(3), ERROR(4);
    private final int severity;
}
```

**Test Cases:**
- Level set to INFO: DEBUG messages ignored, INFO/WARN/ERROR logged
- Console handler logs all, File handler logs WARN+, Slack handler logs ERROR only

---

### Problem 2: Undo/Redo Text Editor (Command + Memento)
Implement text editor with operations: insert, delete, replace. Support undo/redo.

**Expected Interface:**
```java
public interface TextEditor {
    void insert(int position, String text);
    void delete(int start, int end);
    void replace(int start, int end, String text);
    void undo();
    void redo();
    String getText();
}
```

**Test Cases:**
- Multiple insert/delete, undo back to empty string
- Undo, redo, undo again
- Execute new command after undo (clear redo stack)

---

### Problem 3: State Machine for Order Processing (State)
Design order system with states: CREATED → PAID → SHIPPED → DELIVERED. Invalid transitions should throw exception.

**Expected Interface:**
```java
public interface Order {
    void pay();
    void ship();
    void deliver();
    void cancel();  // Only from CREATED or PAID
    OrderState getState();
}
```

**Test Cases:**
- Cannot ship unpaid order
- Cannot pay already paid order
- Can cancel from CREATED/PAID, not from SHIPPED
- Cannot deliver unshipped order

---

## 🏆 Final Interview Checklist

When using Behavioral Patterns in interviews:

### Step 1: Identify the Problem Type
- [ ] **Algorithms:** Multiple ways to do same thing? → **Strategy**
- [ ] **Communication:** One-to-many events? → **Observer**
- [ ] **Communication:** Many-to-many coordination? → **Mediator**
- [ ] **Operations:** Need undo/redo? → **Command** or **Memento**
- [ ] **Structure:** Common algorithm skeleton? → **Template Method**
- [ ] **Behavior:** Object behavior changes with state? → **State**
- [ ] **Processing:** Sequential checks/filters? → **Chain of Responsibility**
- [ ] **Traversal:** Iterate without exposing structure? → **Iterator**
- [ ] **Operations:** Add operations to class hierarchy? → **Visitor**

### Step 2: Explain Your Choice
```
"I'm using Observer pattern because:
1. We need to notify multiple systems (logger, metrics, alerting)
2. Systems should be decoupled (can add new observers without modifying pipeline)
3. Supports Open/Closed Principle (open for extension, closed for modification)"
```

### Step 3: Discuss Trade-offs
```
"Observer pattern benefits:
✅ Decoupled components
✅ Easy to add new observers
✅ Supports event-driven architecture

Observer pattern drawbacks:
❌ Can be hard to debug (indirect control flow)
❌ Need to handle slow/failing observers (timeouts, async)
❌ Memory leaks if observers not properly detached"
```

### Step 4: Consider Production Concerns
- [ ] **Thread safety:** CopyOnWriteArrayList, AtomicReference, synchronization
- [ ] **Performance:** Async execution, caching, lazy loading
- [ ] **Memory:** Bounded history, weak references, cleanup
- [ ] **Error handling:** Timeouts, circuit breakers, graceful degradation
- [ ] **Testing:** Mock strategies/observers, verify state transitions

### Step 5: Show Real-World Knowledge
```
"This is similar to how:
- Kafka works (Observer pattern for consumers)
- Spark partitioning works (Strategy pattern)
- Airflow DAGs work (Template Method for task structure)
- Flink checkpointing works (Memento pattern)"
```

---

## 📚 Recommended Reading Order

1. **Start Here:** Strategy, Observer, Template Method (most common)
2. **Core Patterns:** Command, State, Iterator
3. **Advanced:** Chain of Responsibility, Mediator
4. **Expert:** Memento, Visitor

---

## 🎓 Certification: You've Mastered Behavioral Patterns If...

- [ ] Can implement any pattern from memory in 20 minutes
- [ ] Can explain when to use each pattern (with real examples)
- [ ] Can combine patterns (Observer + Command, State + Strategy)
- [ ] Can discuss thread-safety for each pattern
- [ ] Can identify patterns in real systems (Spark, Kafka, Airflow)
- [ ] Can solve LeetCode-style LLD problems using these patterns

---

**Congratulations!** You've completed all 23 Gang of Four Design Patterns with production-grade SDE-Data focus. 

**Next:** [CASE-STUDIES.md](../03-CASE-STUDIES/README.md) — Apply these patterns to real interview problems (LRU Cache, Rate Limiter, Parking Lot, URL Shortener, Task Scheduler, Distributed Cache)

