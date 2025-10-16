# Design Patterns - Creational Patterns

**Learning Time:** 2-3 weeks  
**Prerequisites:** SOLID Principles  
**Difficulty:** Intermediate → Core patterns for object creation

---

## 📚 Table of Contents

1. [Introduction to Creational Patterns](#introduction)
2. [Singleton Pattern](#singleton-pattern)
3. [Factory Method Pattern](#factory-method-pattern)
4. [Abstract Factory Pattern](#abstract-factory-pattern)
5. [Builder Pattern](#builder-pattern)
6. [Prototype Pattern](#prototype-pattern)
7. [Real-World Examples for SDE-Data](#real-world-examples)

---

## Introduction

**Creational Patterns** deal with object creation mechanisms, trying to create objects in a manner suitable to the situation.

**Why Important for 40 LPA SDE-Data:**
```
Interview Questions:
├─ "Design a connection pool for database connections" → Singleton/Object Pool
├─ "Create different data parsers (JSON, XML, Avro)" → Factory
├─ "Build complex query objects with optional parameters" → Builder
└─ "Clone data processing configurations" → Prototype
```

---

## 1. Singleton Pattern

### Intent
Ensure a class has only one instance and provide global access to it.

### When to Use
```
Use Singleton when:
├─ Exactly one instance needed (database connection pool, logger, config)
├─ Instance must be accessible globally
├─ Lazy initialization required (create only when needed)

Don't use when:
├─ You need multiple instances
├─ Testing is important (Singleton makes testing hard)
└─ Multithreading without proper synchronization
```

### ❌ Naive Implementation (Not Thread-Safe)

```java
/**
 * WRONG: Not thread-safe
 */
public class DatabaseConnection {
    private static DatabaseConnection instance;
    
    private DatabaseConnection() {
        // Private constructor
    }
    
    public static DatabaseConnection getInstance() {
        if (instance == null) {
            instance = new DatabaseConnection();  // ❌ Race condition!
        }
        return instance;
    }
}

/**
 * Problem: Two threads can create two instances
 * 
 * Thread 1: if (instance == null) → true
 * Thread 2: if (instance == null) → true (still null!)
 * Thread 1: instance = new DatabaseConnection()
 * Thread 2: instance = new DatabaseConnection()
 * 
 * Result: Two instances! ❌
 */
```

### ✅ Thread-Safe Implementations

#### Approach 1: Eager Initialization

```java
/**
 * Thread-safe: Instance created at class loading time
 */
public class DatabaseConnectionPool {
    // Eagerly created (when class is loaded)
    private static final DatabaseConnectionPool INSTANCE = new DatabaseConnectionPool();
    
    private final List<Connection> connections;
    private final int maxConnections;
    
    private DatabaseConnectionPool() {
        this.maxConnections = 10;
        this.connections = new ArrayList<>();
        
        // Initialize connection pool
        for (int i = 0; i < maxConnections; i++) {
            connections.add(createConnection());
        }
    }
    
    public static DatabaseConnectionPool getInstance() {
        return INSTANCE;
    }
    
    public synchronized Connection getConnection() {
        if (connections.isEmpty()) {
            throw new RuntimeException("No available connections");
        }
        return connections.remove(0);
    }
    
    public synchronized void releaseConnection(Connection connection) {
        if (connections.size() < maxConnections) {
            connections.add(connection);
        }
    }
    
    private Connection createConnection() {
        try {
            return DriverManager.getConnection(
                "jdbc:postgresql://localhost:5432/mydb",
                "user",
                "password"
            );
        } catch (SQLException e) {
            throw new RuntimeException("Failed to create connection", e);
        }
    }
}

// Usage
public class DataPipeline {
    public void run() {
        DatabaseConnectionPool pool = DatabaseConnectionPool.getInstance();
        Connection conn = pool.getConnection();
        
        try {
            // Use connection
            PreparedStatement stmt = conn.prepareStatement("SELECT * FROM users");
            ResultSet rs = stmt.executeQuery();
            // Process results
        } catch (SQLException e) {
            // Handle error
        } finally {
            pool.releaseConnection(conn);
        }
    }
}
```

**Pros:**
- Thread-safe (class loading is thread-safe in Java)
- Simple implementation

**Cons:**
- Instance created even if never used (waste of resources)
- No control over instantiation time

#### Approach 2: Lazy Initialization with Double-Checked Locking

```java
/**
 * Thread-safe + lazy initialization (best approach)
 */
public class ConfigurationManager {
    private static volatile ConfigurationManager instance;  // volatile is crucial!
    
    private final Properties properties;
    
    private ConfigurationManager() {
        properties = new Properties();
        try (InputStream input = new FileInputStream("config.properties")) {
            properties.load(input);
        } catch (IOException e) {
            throw new RuntimeException("Failed to load configuration", e);
        }
    }
    
    public static ConfigurationManager getInstance() {
        if (instance == null) {  // First check (no locking)
            synchronized (ConfigurationManager.class) {
                if (instance == null) {  // Second check (with locking)
                    instance = new ConfigurationManager();
                }
            }
        }
        return instance;
    }
    
    public String getProperty(String key) {
        return properties.getProperty(key);
    }
    
    public String getProperty(String key, String defaultValue) {
        return properties.getProperty(key, defaultValue);
    }
}

/**
 * Why volatile?
 * - Prevents reordering of instructions
 * - Without volatile, Thread 2 might see partially constructed object
 * 
 * Thread 1: instance = new ConfigurationManager()
 *           Step 1: Allocate memory
 *           Step 2: Call constructor
 *           Step 3: Assign to instance
 * 
 * Without volatile, JVM might reorder to: Step 1 → Step 3 → Step 2
 * Thread 2 sees instance != null (Step 3) but constructor not finished (Step 2)!
 */
```

#### Approach 3: Bill Pugh Singleton (Recommended)

```java
/**
 * Best approach: Thread-safe + lazy + no synchronization overhead
 */
public class Logger {
    private Logger() {
        // Private constructor
    }
    
    // Inner static class (loaded only when getInstance() is called)
    private static class LoggerHolder {
        private static final Logger INSTANCE = new Logger();
    }
    
    public static Logger getInstance() {
        return LoggerHolder.INSTANCE;
    }
    
    public void log(String message) {
        System.out.println("[" + LocalDateTime.now() + "] " + message);
    }
    
    public void error(String message) {
        System.err.println("[" + LocalDateTime.now() + "] ERROR: " + message);
    }
}

/**
 * How it works:
 * 1. LoggerHolder class not loaded until getInstance() called (lazy)
 * 2. Class loading is thread-safe in Java (no synchronization needed)
 * 3. INSTANCE created when LoggerHolder loaded (thread-safe)
 * 
 * Best of all worlds! ✅
 */
```

#### Approach 4: Enum Singleton (Most Robust)

```java
/**
 * Enum singleton: Handles serialization + reflection attacks
 */
public enum MetricsCollector {
    INSTANCE;
    
    private final Map<String, Long> metrics;
    
    MetricsCollector() {
        metrics = new ConcurrentHashMap<>();
    }
    
    public void increment(String metric) {
        metrics.merge(metric, 1L, Long::sum);
    }
    
    public void recordValue(String metric, long value) {
        metrics.put(metric, value);
    }
    
    public long getMetric(String metric) {
        return metrics.getOrDefault(metric, 0L);
    }
    
    public Map<String, Long> getAllMetrics() {
        return new HashMap<>(metrics);
    }
}

// Usage
MetricsCollector.INSTANCE.increment("requests");
MetricsCollector.INSTANCE.recordValue("latency_ms", 150);
```

**Advantages of Enum:**
- Serialization handled automatically (no extra code needed)
- Prevents reflection attacks (can't create second instance)
- Thread-safe
- Concise

**Disadvantage:**
- Can't extend a class (but can implement interfaces)

### Real-World Example: Spark Session Manager

```java
/**
 * SDE-Data: Singleton for SparkSession (expensive to create)
 */
public class SparkSessionManager {
    private static volatile SparkSessionManager instance;
    private final SparkSession sparkSession;
    
    private SparkSessionManager() {
        this.sparkSession = SparkSession.builder()
            .appName("DataPipeline")
            .master("local[*]")
            .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse")
            .config("spark.executor.memory", "4g")
            .config("spark.driver.memory", "2g")
            .enableHiveSupport()
            .getOrCreate();
    }
    
    public static SparkSessionManager getInstance() {
        if (instance == null) {
            synchronized (SparkSessionManager.class) {
                if (instance == null) {
                    instance = new SparkSessionManager();
                }
            }
        }
        return instance;
    }
    
    public SparkSession getSparkSession() {
        return sparkSession;
    }
    
    public void stop() {
        if (sparkSession != null) {
            sparkSession.stop();
        }
    }
}

// Usage in data pipeline
public class DataProcessor {
    public void processData(String inputPath, String outputPath) {
        SparkSession spark = SparkSessionManager.getInstance().getSparkSession();
        
        Dataset<Row> df = spark.read()
            .format("parquet")
            .load(inputPath);
        
        // Transform data
        Dataset<Row> transformed = df
            .filter(col("age").gt(18))
            .groupBy("country")
            .agg(count("*").as("count"));
        
        // Write results
        transformed.write()
            .mode("overwrite")
            .parquet(outputPath);
    }
}
```

---

## 2. Factory Method Pattern

### Intent
Define an interface for creating objects, but let subclasses decide which class to instantiate.

### When to Use
```
Use Factory Method when:
├─ You don't know exact types ahead of time
├─ Object creation logic is complex
├─ You want to delegate object creation to subclasses

Example scenarios:
├─ Different data parsers (JSON, XML, Avro, Protobuf)
├─ Different database connections (MySQL, PostgreSQL, MongoDB)
├─ Different notification channels (Email, SMS, Slack, PagerDuty)
```

### ❌ Without Factory Method

```java
/**
 * WRONG: Client code tightly coupled to concrete classes
 */
public class DataPipeline {
    public void processData(String format, String data) {
        if (format.equals("JSON")) {
            JsonParser parser = new JsonParser();  // ❌ Tight coupling
            parser.parse(data);
        } else if (format.equals("XML")) {
            XmlParser parser = new XmlParser();  // ❌ Tight coupling
            parser.parse(data);
        } else if (format.equals("AVRO")) {
            AvroParser parser = new AvroParser();  // ❌ Tight coupling
            parser.parse(data);
        }
        // Adding new format requires modifying this code! ❌
    }
}
```

### ✅ With Factory Method

```java
/**
 * CORRECT: Factory method delegates object creation
 */

// Product interface
public interface DataParser {
    Map<String, Object> parse(String data);
    String getFormat();
}

// Concrete products
public class JsonParser implements DataParser {
    private final ObjectMapper objectMapper = new ObjectMapper();
    
    @Override
    public Map<String, Object> parse(String data) {
        try {
            return objectMapper.readValue(data, new TypeReference<Map<String, Object>>() {});
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Failed to parse JSON", e);
        }
    }
    
    @Override
    public String getFormat() {
        return "JSON";
    }
}

public class XmlParser implements DataParser {
    @Override
    public Map<String, Object> parse(String data) {
        try {
            DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
            DocumentBuilder builder = factory.newDocumentBuilder();
            Document doc = builder.parse(new InputSource(new StringReader(data)));
            
            // Convert XML to Map
            return xmlToMap(doc.getDocumentElement());
        } catch (Exception e) {
            throw new RuntimeException("Failed to parse XML", e);
        }
    }
    
    @Override
    public String getFormat() {
        return "XML";
    }
    
    private Map<String, Object> xmlToMap(Element element) {
        // XML to Map conversion logic
        return new HashMap<>();
    }
}

public class AvroParser implements DataParser {
    private final Schema schema;
    
    public AvroParser(Schema schema) {
        this.schema = schema;
    }
    
    @Override
    public Map<String, Object> parse(String data) {
        try {
            DatumReader<GenericRecord> datumReader = new GenericDatumReader<>(schema);
            BinaryDecoder decoder = DecoderFactory.get().binaryDecoder(
                data.getBytes(), null
            );
            GenericRecord record = datumReader.read(null, decoder);
            
            // Convert GenericRecord to Map
            return avroToMap(record);
        } catch (IOException e) {
            throw new RuntimeException("Failed to parse Avro", e);
        }
    }
    
    @Override
    public String getFormat() {
        return "AVRO";
    }
    
    private Map<String, Object> avroToMap(GenericRecord record) {
        Map<String, Object> map = new HashMap<>();
        for (Schema.Field field : record.getSchema().getFields()) {
            map.put(field.name(), record.get(field.name()));
        }
        return map;
    }
}

// Factory class
public class DataParserFactory {
    public static DataParser createParser(String format) {
        switch (format.toUpperCase()) {
            case "JSON":
                return new JsonParser();
            case "XML":
                return new XmlParser();
            case "AVRO":
                // In real scenario, schema would come from Schema Registry
                Schema schema = new Schema.Parser().parse("{\"type\":\"record\",...}");
                return new AvroParser(schema);
            default:
                throw new IllegalArgumentException("Unsupported format: " + format);
        }
    }
}

// Client code (decoupled from concrete classes)
public class DataPipeline {
    public void processData(String format, String data) {
        DataParser parser = DataParserFactory.createParser(format);  // ✅ Factory
        Map<String, Object> parsed = parser.parse(data);
        
        // Process parsed data
        processMap(parsed);
    }
    
    private void processMap(Map<String, Object> data) {
        // Processing logic
    }
}

/**
 * Adding Protobuf? Just create ProtobufParser and update factory! ✅
 * No changes to client code (DataPipeline)
 */
```

### Advanced: Registry-Based Factory (More Flexible)

```java
/**
 * Registry-based factory: Register parsers dynamically
 */
public class DataParserRegistry {
    private static final Map<String, Supplier<DataParser>> registry = new ConcurrentHashMap<>();
    
    static {
        // Register default parsers
        register("JSON", JsonParser::new);
        register("XML", XmlParser::new);
        register("AVRO", () -> new AvroParser(getDefaultSchema()));
    }
    
    public static void register(String format, Supplier<DataParser> supplier) {
        registry.put(format.toUpperCase(), supplier);
    }
    
    public static DataParser createParser(String format) {
        Supplier<DataParser> supplier = registry.get(format.toUpperCase());
        if (supplier == null) {
            throw new IllegalArgumentException("Unsupported format: " + format);
        }
        return supplier.get();
    }
    
    private static Schema getDefaultSchema() {
        return new Schema.Parser().parse("{\"type\":\"record\",...}");
    }
}

// Plugin system: Register custom parser at runtime
public class CustomCsvParser implements DataParser {
    @Override
    public Map<String, Object> parse(String data) {
        // CSV parsing logic
        return new HashMap<>();
    }
    
    @Override
    public String getFormat() {
        return "CSV";
    }
}

// Register custom parser
DataParserRegistry.register("CSV", CustomCsvParser::new);

// Now client can use CSV parser without modifying factory code! ✅
DataParser csvParser = DataParserRegistry.createParser("CSV");
```

---

## 3. Abstract Factory Pattern

### Intent
Provide an interface for creating families of related objects without specifying their concrete classes.

### When to Use
```
Use Abstract Factory when:
├─ System needs to work with multiple families of related objects
├─ You want to ensure objects from same family are used together
├─ You want to hide implementation details from client

Example:
├─ Different cloud providers (AWS, Azure, GCP)
│   ├─ Each has: Storage, Compute, Messaging
│   └─ Ensure all components from same cloud
```

### Example: Multi-Cloud Data Platform

```java
/**
 * SDE-Data: Abstract factory for multi-cloud data platform
 */

// Abstract products
public interface CloudStorage {
    void upload(String path, byte[] data);
    byte[] download(String path);
    void delete(String path);
}

public interface CloudCompute {
    String submitJob(String jobConfig);
    String getJobStatus(String jobId);
    void cancelJob(String jobId);
}

public interface CloudMessaging {
    void sendMessage(String topic, String message);
    List<String> receiveMessages(String topic, int maxMessages);
}

// AWS family
public class S3Storage implements CloudStorage {
    private final S3Client s3Client;
    
    public S3Storage(S3Client s3Client) {
        this.s3Client = s3Client;
    }
    
    @Override
    public void upload(String path, byte[] data) {
        String[] parts = path.split("/", 2);
        String bucket = parts[0];
        String key = parts[1];
        
        s3Client.putObject(
            PutObjectRequest.builder()
                .bucket(bucket)
                .key(key)
                .build(),
            RequestBody.fromBytes(data)
        );
    }
    
    @Override
    public byte[] download(String path) {
        String[] parts = path.split("/", 2);
        String bucket = parts[0];
        String key = parts[1];
        
        ResponseBytes<GetObjectResponse> responseBytes = s3Client.getObjectAsBytes(
            GetObjectRequest.builder()
                .bucket(bucket)
                .key(key)
                .build()
        );
        
        return responseBytes.asByteArray();
    }
    
    @Override
    public void delete(String path) {
        String[] parts = path.split("/", 2);
        String bucket = parts[0];
        String key = parts[1];
        
        s3Client.deleteObject(
            DeleteObjectRequest.builder()
                .bucket(bucket)
                .key(key)
                .build()
        );
    }
}

public class EMRCompute implements CloudCompute {
    private final EmrClient emrClient;
    
    public EMRCompute(EmrClient emrClient) {
        this.emrClient = emrClient;
    }
    
    @Override
    public String submitJob(String jobConfig) {
        RunJobFlowResponse response = emrClient.runJobFlow(
            RunJobFlowRequest.builder()
                .name("DataProcessingJob")
                .releaseLabel("emr-6.10.0")
                .applications(Application.builder().name("Spark").build())
                // More configuration
                .build()
        );
        return response.jobFlowId();
    }
    
    @Override
    public String getJobStatus(String jobId) {
        DescribeClusterResponse response = emrClient.describeCluster(
            DescribeClusterRequest.builder()
                .clusterId(jobId)
                .build()
        );
        return response.cluster().status().state().toString();
    }
    
    @Override
    public void cancelJob(String jobId) {
        emrClient.terminateJobFlows(
            TerminateJobFlowsRequest.builder()
                .jobFlowIds(jobId)
                .build()
        );
    }
}

public class SNSMessaging implements CloudMessaging {
    private final SnsClient snsClient;
    
    public SNSMessaging(SnsClient snsClient) {
        this.snsClient = snsClient;
    }
    
    @Override
    public void sendMessage(String topic, String message) {
        snsClient.publish(
            PublishRequest.builder()
                .topicArn(topic)
                .message(message)
                .build()
        );
    }
    
    @Override
    public List<String> receiveMessages(String topic, int maxMessages) {
        // SNS is pub-sub, not queue. Use SQS for receiving.
        throw new UnsupportedOperationException("Use SQS for receiving messages");
    }
}

// GCP family
public class GCSStorage implements CloudStorage {
    private final Storage storage;
    
    public GCSStorage(Storage storage) {
        this.storage = storage;
    }
    
    @Override
    public void upload(String path, byte[] data) {
        String[] parts = path.split("/", 2);
        String bucket = parts[0];
        String objectName = parts[1];
        
        BlobId blobId = BlobId.of(bucket, objectName);
        BlobInfo blobInfo = BlobInfo.newBuilder(blobId).build();
        storage.create(blobInfo, data);
    }
    
    @Override
    public byte[] download(String path) {
        String[] parts = path.split("/", 2);
        String bucket = parts[0];
        String objectName = parts[1];
        
        Blob blob = storage.get(BlobId.of(bucket, objectName));
        return blob.getContent();
    }
    
    @Override
    public void delete(String path) {
        String[] parts = path.split("/", 2);
        String bucket = parts[0];
        String objectName = parts[1];
        
        storage.delete(BlobId.of(bucket, objectName));
    }
}

public class DataprocCompute implements CloudCompute {
    private final JobControllerClient jobControllerClient;
    private final String projectId;
    private final String region;
    
    public DataprocCompute(JobControllerClient jobControllerClient, String projectId, String region) {
        this.jobControllerClient = jobControllerClient;
        this.projectId = projectId;
        this.region = region;
    }
    
    @Override
    public String submitJob(String jobConfig) {
        Job job = Job.newBuilder()
            .setPlacement(JobPlacement.newBuilder().setClusterName("my-cluster").build())
            .setSparkJob(SparkJob.newBuilder()
                .setMainClass("com.example.DataProcessor")
                .build())
            .build();
        
        Job response = jobControllerClient.submitJob(projectId, region, job);
        return response.getReference().getJobId();
    }
    
    @Override
    public String getJobStatus(String jobId) {
        Job job = jobControllerClient.getJob(projectId, region, jobId);
        return job.getStatus().getState().toString();
    }
    
    @Override
    public void cancelJob(String jobId) {
        jobControllerClient.cancelJob(projectId, region, jobId);
    }
}

public class PubSubMessaging implements CloudMessaging {
    private final Publisher publisher;
    private final Subscriber subscriber;
    
    public PubSubMessaging(Publisher publisher, Subscriber subscriber) {
        this.publisher = publisher;
        this.subscriber = subscriber;
    }
    
    @Override
    public void sendMessage(String topic, String message) {
        ByteString data = ByteString.copyFromUtf8(message);
        PubsubMessage pubsubMessage = PubsubMessage.newBuilder().setData(data).build();
        
        try {
            publisher.publish(pubsubMessage).get();
        } catch (Exception e) {
            throw new RuntimeException("Failed to publish message", e);
        }
    }
    
    @Override
    public List<String> receiveMessages(String topic, int maxMessages) {
        // Subscriber receives messages asynchronously
        List<String> messages = new ArrayList<>();
        // Implementation using MessageReceiver
        return messages;
    }
}

// Abstract Factory interface
public interface CloudPlatformFactory {
    CloudStorage createStorage();
    CloudCompute createCompute();
    CloudMessaging createMessaging();
}

// Concrete factories
public class AWSFactory implements CloudPlatformFactory {
    @Override
    public CloudStorage createStorage() {
        return new S3Storage(S3Client.builder().build());
    }
    
    @Override
    public CloudCompute createCompute() {
        return new EMRCompute(EmrClient.builder().build());
    }
    
    @Override
    public CloudMessaging createMessaging() {
        return new SNSMessaging(SnsClient.builder().build());
    }
}

public class GCPFactory implements CloudPlatformFactory {
    @Override
    public CloudStorage createStorage() {
        return new GCSStorage(StorageOptions.getDefaultInstance().getService());
    }
    
    @Override
    public CloudCompute createCompute() {
        try {
            JobControllerClient client = JobControllerClient.create();
            return new DataprocCompute(client, "my-project", "us-central1");
        } catch (IOException e) {
            throw new RuntimeException("Failed to create Dataproc client", e);
        }
    }
    
    @Override
    public CloudMessaging createMessaging() {
        try {
            Publisher publisher = Publisher.newBuilder("projects/my-project/topics/my-topic").build();
            return new PubSubMessaging(publisher, null);
        } catch (IOException e) {
            throw new RuntimeException("Failed to create Pub/Sub publisher", e);
        }
    }
}

// Client code (cloud-agnostic)
public class DataPlatform {
    private final CloudStorage storage;
    private final CloudCompute compute;
    private final CloudMessaging messaging;
    
    public DataPlatform(CloudPlatformFactory factory) {
        this.storage = factory.createStorage();
        this.compute = factory.createCompute();
        this.messaging = factory.createMessaging();
    }
    
    public void runDataPipeline(String inputPath, String outputPath) {
        // 1. Download data
        byte[] data = storage.download(inputPath);
        
        // 2. Submit processing job
        String jobId = compute.submitJob("process-data-job");
        
        // 3. Wait for job completion
        String status;
        do {
            status = compute.getJobStatus(jobId);
            try {
                Thread.sleep(5000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        } while (status.equals("RUNNING"));
        
        // 4. Upload results
        storage.upload(outputPath, data);
        
        // 5. Send notification
        messaging.sendMessage("data-pipeline-topic", "Pipeline completed: " + jobId);
    }
}

// Usage: Switch cloud providers with one line!
public class Main {
    public static void main(String[] args) {
        // Use AWS
        CloudPlatformFactory awsFactory = new AWSFactory();
        DataPlatform awsPlatform = new DataPlatform(awsFactory);
        awsPlatform.runDataPipeline("s3://input/data.csv", "s3://output/results.parquet");
        
        // Switch to GCP? Just change factory!
        CloudPlatformFactory gcpFactory = new GCPFactory();
        DataPlatform gcpPlatform = new DataPlatform(gcpFactory);
        gcpPlatform.runDataPipeline("gs://input/data.csv", "gs://output/results.parquet");
        
        // All components (storage, compute, messaging) guaranteed to be from same cloud ✅
    }
}
```

---

## 4. Builder Pattern

### Intent
Separate construction of complex object from its representation, allowing same construction process to create different representations.

### When to Use
```
Use Builder when:
├─ Object has many optional parameters (4+ parameters)
├─ Construction process is complex (multiple steps)
├─ Want immutable objects with many fields

Example:
├─ Building complex queries (SELECT ... FROM ... WHERE ... GROUP BY ... HAVING ... ORDER BY ... LIMIT)
├─ Building HTTP requests with optional headers, body, params
├─ Configuring data pipelines with optional transformations, filters
```

### ❌ Without Builder (Telescoping Constructor)

```java
/**
 * WRONG: Telescoping constructor anti-pattern
 */
public class DataPipelineConfig {
    private final String name;
    private final String source;
    private final String destination;
    private final String format;
    private final boolean compression;
    private final String compressionType;
    private final boolean encryption;
    private final String encryptionKey;
    private final int parallelism;
    private final int retryAttempts;
    private final long timeoutSeconds;
    
    // Constructor with all parameters
    public DataPipelineConfig(
        String name, String source, String destination, String format,
        boolean compression, String compressionType,
        boolean encryption, String encryptionKey,
        int parallelism, int retryAttempts, long timeoutSeconds
    ) {
        this.name = name;
        this.source = source;
        this.destination = destination;
        this.format = format;
        this.compression = compression;
        this.compressionType = compressionType;
        this.encryption = encryption;
        this.encryptionKey = encryptionKey;
        this.parallelism = parallelism;
        this.retryAttempts = retryAttempts;
        this.timeoutSeconds = timeoutSeconds;
    }
    
    // Constructor with fewer parameters
    public DataPipelineConfig(String name, String source, String destination) {
        this(name, source, destination, "JSON", false, null, false, null, 1, 3, 3600);
    }
    
    // More constructors...
}

// Usage: Hard to read!
DataPipelineConfig config = new DataPipelineConfig(
    "my-pipeline",
    "s3://input",
    "s3://output",
    "PARQUET",
    true,
    "GZIP",
    true,
    "AES256_KEY",
    10,
    5,
    7200
);  // ❌ What does each parameter mean?
```

### ✅ With Builder Pattern

```java
/**
 * CORRECT: Builder pattern for complex object construction
 */
public class DataPipelineConfig {
    // All fields final (immutable)
    private final String name;
    private final String source;
    private final String destination;
    private final String format;
    private final boolean compression;
    private final String compressionType;
    private final boolean encryption;
    private final String encryptionKey;
    private final int parallelism;
    private final int retryAttempts;
    private final long timeoutSeconds;
    
    // Private constructor (only builder can create)
    private DataPipelineConfig(Builder builder) {
        this.name = builder.name;
        this.source = builder.source;
        this.destination = builder.destination;
        this.format = builder.format;
        this.compression = builder.compression;
        this.compressionType = builder.compressionType;
        this.encryption = builder.encryption;
        this.encryptionKey = builder.encryptionKey;
        this.parallelism = builder.parallelism;
        this.retryAttempts = builder.retryAttempts;
        this.timeoutSeconds = builder.timeoutSeconds;
    }
    
    // Getters only (immutable)
    public String getName() { return name; }
    public String getSource() { return source; }
    public String getDestination() { return destination; }
    // ... more getters
    
    // Builder class
    public static class Builder {
        // Required parameters
        private final String name;
        private final String source;
        private final String destination;
        
        // Optional parameters with default values
        private String format = "JSON";
        private boolean compression = false;
        private String compressionType = null;
        private boolean encryption = false;
        private String encryptionKey = null;
        private int parallelism = 1;
        private int retryAttempts = 3;
        private long timeoutSeconds = 3600;
        
        public Builder(String name, String source, String destination) {
            this.name = name;
            this.source = source;
            this.destination = destination;
        }
        
        public Builder format(String format) {
            this.format = format;
            return this;  // Return this for method chaining
        }
        
        public Builder compression(boolean enabled, String type) {
            this.compression = enabled;
            this.compressionType = type;
            return this;
        }
        
        public Builder encryption(boolean enabled, String key) {
            this.encryption = enabled;
            this.encryptionKey = key;
            return this;
        }
        
        public Builder parallelism(int parallelism) {
            this.parallelism = parallelism;
            return this;
        }
        
        public Builder retryAttempts(int attempts) {
            this.retryAttempts = attempts;
            return this;
        }
        
        public Builder timeoutSeconds(long seconds) {
            this.timeoutSeconds = seconds;
            return this;
        }
        
        public DataPipelineConfig build() {
            // Validation before building
            if (compression && compressionType == null) {
                throw new IllegalStateException("Compression enabled but no type specified");
            }
            if (encryption && encryptionKey == null) {
                throw new IllegalStateException("Encryption enabled but no key specified");
            }
            if (parallelism < 1) {
                throw new IllegalArgumentException("Parallelism must be >= 1");
            }
            
            return new DataPipelineConfig(this);
        }
    }
}

// Usage: Clear and readable! ✅
DataPipelineConfig config = new DataPipelineConfig.Builder(
        "my-pipeline",
        "s3://input",
        "s3://output"
    )
    .format("PARQUET")
    .compression(true, "GZIP")
    .encryption(true, "AES256_KEY")
    .parallelism(10)
    .retryAttempts(5)
    .timeoutSeconds(7200)
    .build();

// Minimal configuration (defaults used)
DataPipelineConfig simpleConfig = new DataPipelineConfig.Builder(
        "simple-pipeline",
        "s3://input",
        "s3://output"
    )
    .build();  // Uses default values ✅
```

### Real-World Example: SQL Query Builder

```java
/**
 * SDE-Data: Build complex SQL queries programmatically
 */
public class SqlQuery {
    private final String select;
    private final String from;
    private final String where;
    private final String groupBy;
    private final String having;
    private final String orderBy;
    private final Integer limit;
    private final Integer offset;
    
    private SqlQuery(Builder builder) {
        this.select = builder.select;
        this.from = builder.from;
        this.where = builder.where;
        this.groupBy = builder.groupBy;
        this.having = builder.having;
        this.orderBy = builder.orderBy;
        this.limit = builder.limit;
        this.offset = builder.offset;
    }
    
    public String toSql() {
        StringBuilder sql = new StringBuilder();
        sql.append("SELECT ").append(select).append("\n");
        sql.append("FROM ").append(from);
        
        if (where != null) {
            sql.append("\nWHERE ").append(where);
        }
        if (groupBy != null) {
            sql.append("\nGROUP BY ").append(groupBy);
        }
        if (having != null) {
            sql.append("\nHAVING ").append(having);
        }
        if (orderBy != null) {
            sql.append("\nORDER BY ").append(orderBy);
        }
        if (limit != null) {
            sql.append("\nLIMIT ").append(limit);
        }
        if (offset != null) {
            sql.append("\nOFFSET ").append(offset);
        }
        
        return sql.toString();
    }
    
    public static class Builder {
        private String select = "*";
        private String from;
        private String where;
        private String groupBy;
        private String having;
        private String orderBy;
        private Integer limit;
        private Integer offset;
        
        public Builder from(String table) {
            this.from = table;
            return this;
        }
        
        public Builder select(String... columns) {
            this.select = String.join(", ", columns);
            return this;
        }
        
        public Builder where(String condition) {
            this.where = condition;
            return this;
        }
        
        public Builder and(String condition) {
            if (this.where == null) {
                this.where = condition;
            } else {
                this.where += " AND " + condition;
            }
            return this;
        }
        
        public Builder or(String condition) {
            if (this.where == null) {
                this.where = condition;
            } else {
                this.where = "(" + this.where + ") OR (" + condition + ")";
            }
            return this;
        }
        
        public Builder groupBy(String... columns) {
            this.groupBy = String.join(", ", columns);
            return this;
        }
        
        public Builder having(String condition) {
            this.having = condition;
            return this;
        }
        
        public Builder orderBy(String column, String direction) {
            this.orderBy = column + " " + direction;
            return this;
        }
        
        public Builder limit(int limit) {
            this.limit = limit;
            return this;
        }
        
        public Builder offset(int offset) {
            this.offset = offset;
            return this;
        }
        
        public SqlQuery build() {
            if (from == null) {
                throw new IllegalStateException("FROM clause is required");
            }
            return new SqlQuery(this);
        }
    }
}

// Usage: Build complex queries programmatically
SqlQuery query = new SqlQuery.Builder()
    .select("country", "COUNT(*) as user_count", "AVG(age) as avg_age")
    .from("users")
    .where("age >= 18")
    .and("status = 'ACTIVE'")
    .groupBy("country")
    .having("user_count > 100")
    .orderBy("user_count", "DESC")
    .limit(10)
    .build();

System.out.println(query.toSql());
/*
Output:
SELECT country, COUNT(*) as user_count, AVG(age) as avg_age
FROM users
WHERE age >= 18 AND status = 'ACTIVE'
GROUP BY country
HAVING user_count > 100
ORDER BY user_count DESC
LIMIT 10
*/

// Simple query
SqlQuery simpleQuery = new SqlQuery.Builder()
    .from("orders")
    .where("total > 1000")
    .limit(5)
    .build();
```

### Advanced: Fluent Builder with Type Safety

```java
/**
 * Type-safe builder: Enforce correct order of method calls
 */
public class DataFrameQuery {
    private final String dataSource;
    private final String filter;
    private final String aggregation;
    
    private DataFrameQuery(String dataSource, String filter, String aggregation) {
        this.dataSource = dataSource;
        this.filter = filter;
        this.aggregation = aggregation;
    }
    
    // Step 1: Select data source (required)
    public static DataSourceStep builder() {
        return new Builder();
    }
    
    public interface DataSourceStep {
        FilterStep from(String dataSource);
    }
    
    public interface FilterStep {
        AggregationStep filter(String condition);
        AggregationStep noFilter();
    }
    
    public interface AggregationStep {
        BuildStep aggregate(String aggregation);
        BuildStep noAggregation();
    }
    
    public interface BuildStep {
        DataFrameQuery build();
    }
    
    private static class Builder implements DataSourceStep, FilterStep, AggregationStep, BuildStep {
        private String dataSource;
        private String filter;
        private String aggregation;
        
        @Override
        public FilterStep from(String dataSource) {
            this.dataSource = dataSource;
            return this;
        }
        
        @Override
        public AggregationStep filter(String condition) {
            this.filter = condition;
            return this;
        }
        
        @Override
        public AggregationStep noFilter() {
            return this;
        }
        
        @Override
        public BuildStep aggregate(String aggregation) {
            this.aggregation = aggregation;
            return this;
        }
        
        @Override
        public BuildStep noAggregation() {
            return this;
        }
        
        @Override
        public DataFrameQuery build() {
            return new DataFrameQuery(dataSource, filter, aggregation);
        }
    }
}

// Usage: Type-safe! Compiler enforces correct order
DataFrameQuery query = DataFrameQuery.builder()
    .from("users")          // Must call from() first
    .filter("age > 18")     // Then filter() or noFilter()
    .aggregate("COUNT(*)")  // Then aggregate() or noAggregation()
    .build();               // Finally build()

// Compile error if wrong order:
// DataFrameQuery invalid = DataFrameQuery.builder()
//     .filter("age > 18")  // ❌ Compile error! Must call from() first
//     .from("users")
//     .build();
```

---

## 5. Prototype Pattern

### Intent
Specify kinds of objects to create using prototypical instance, and create new objects by copying this prototype.

### When to Use
```
Use Prototype when:
├─ Creating object is expensive (complex initialization, database queries)
├─ Need to clone existing object rather than create from scratch
├─ Want to hide complexity of creating new instances

Example:
├─ Clone Spark DataFrame configuration
├─ Clone data processing pipeline with slight modifications
├─ Copy complex nested objects
```

### Implementation

```java
/**
 * Prototype pattern: Clone objects instead of creating from scratch
 */

// Prototype interface
public interface Prototype<T> {
    T clone();
}

// Concrete prototype
public class DataProcessingConfig implements Prototype<DataProcessingConfig> {
    private String name;
    private String inputFormat;
    private String outputFormat;
    private List<String> transformations;
    private Map<String, String> properties;
    
    public DataProcessingConfig(String name, String inputFormat, String outputFormat) {
        this.name = name;
        this.inputFormat = inputFormat;
        this.outputFormat = outputFormat;
        this.transformations = new ArrayList<>();
        this.properties = new HashMap<>();
    }
    
    // Copy constructor
    private DataProcessingConfig(DataProcessingConfig other) {
        this.name = other.name;
        this.inputFormat = other.inputFormat;
        this.outputFormat = other.outputFormat;
        // Deep copy collections
        this.transformations = new ArrayList<>(other.transformations);
        this.properties = new HashMap<>(other.properties);
    }
    
    @Override
    public DataProcessingConfig clone() {
        return new DataProcessingConfig(this);
    }
    
    public void addTransformation(String transformation) {
        transformations.add(transformation);
    }
    
    public void setProperty(String key, String value) {
        properties.put(key, value);
    }
    
    // Getters and setters
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    // ... more getters/setters
}

// Prototype registry
public class ConfigurationRegistry {
    private final Map<String, DataProcessingConfig> prototypes = new HashMap<>();
    
    public void registerPrototype(String key, DataProcessingConfig prototype) {
        prototypes.put(key, prototype);
    }
    
    public DataProcessingConfig getPrototype(String key) {
        DataProcessingConfig prototype = prototypes.get(key);
        if (prototype == null) {
            throw new IllegalArgumentException("No prototype for key: " + key);
        }
        return prototype.clone();  // Return clone, not original!
    }
}

// Usage
public class Main {
    public static void main(String[] args) {
        // Create base configuration (expensive operation)
        DataProcessingConfig baseConfig = new DataProcessingConfig(
            "base-config",
            "JSON",
            "PARQUET"
        );
        baseConfig.addTransformation("FILTER_NULLS");
        baseConfig.addTransformation("DEDUPLICATE");
        baseConfig.setProperty("spark.executor.memory", "4g");
        baseConfig.setProperty("spark.driver.memory", "2g");
        
        // Register as prototype
        ConfigurationRegistry registry = new ConfigurationRegistry();
        registry.registerPrototype("standard", baseConfig);
        
        // Clone for different pipelines (fast!)
        DataProcessingConfig pipeline1Config = registry.getPrototype("standard");
        pipeline1Config.setName("pipeline-1");
        pipeline1Config.addTransformation("AGGREGATE_BY_DATE");
        
        DataProcessingConfig pipeline2Config = registry.getPrototype("standard");
        pipeline2Config.setName("pipeline-2");
        pipeline2Config.addTransformation("JOIN_WITH_REFERENCE_DATA");
        
        // Both clones independent of each other and base config ✅
        System.out.println(baseConfig.getName());       // "base-config"
        System.out.println(pipeline1Config.getName());  // "pipeline-1"
        System.out.println(pipeline2Config.getName());  // "pipeline-2"
    }
}
```

### Real-World Example: Cloning Spark Configurations

```java
/**
 * SDE-Data: Clone Spark configurations for different environments
 */
public class SparkConfig implements Cloneable {
    private String appName;
    private String master;
    private Map<String, String> sparkConf;
    private List<String> jars;
    
    public SparkConfig(String appName, String master) {
        this.appName = appName;
        this.master = master;
        this.sparkConf = new HashMap<>();
        this.jars = new ArrayList<>();
    }
    
    @Override
    public SparkConfig clone() {
        try {
            SparkConfig cloned = (SparkConfig) super.clone();
            // Deep copy mutable fields
            cloned.sparkConf = new HashMap<>(this.sparkConf);
            cloned.jars = new ArrayList<>(this.jars);
            return cloned;
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException("Clone not supported", e);
        }
    }
    
    public void setConfig(String key, String value) {
        sparkConf.put(key, value);
    }
    
    public void addJar(String jar) {
        jars.add(jar);
    }
    
    public SparkSession createSession() {
        SparkSession.Builder builder = SparkSession.builder()
            .appName(appName)
            .master(master);
        
        for (Map.Entry<String, String> entry : sparkConf.entrySet()) {
            builder.config(entry.getKey(), entry.getValue());
        }
        
        return builder.getOrCreate();
    }
    
    // Getters
    public String getAppName() { return appName; }
    public void setAppName(String appName) { this.appName = appName; }
}

// Usage: Clone base config for different environments
public class SparkConfigFactory {
    public static void main(String[] args) {
        // Base production config
        SparkConfig prodConfig = new SparkConfig("DataPipeline", "yarn");
        prodConfig.setConfig("spark.executor.memory", "8g");
        prodConfig.setConfig("spark.executor.cores", "4");
        prodConfig.setConfig("spark.sql.shuffle.partitions", "200");
        prodConfig.addJar("s3://jars/pipeline-1.0.jar");
        
        // Clone for dev environment (modify slightly)
        SparkConfig devConfig = prodConfig.clone();
        devConfig.setAppName("DataPipeline-Dev");
        devConfig.setConfig("spark.executor.memory", "2g");  // Less memory in dev
        devConfig.setConfig("spark.executor.cores", "2");
        
        // Clone for staging
        SparkConfig stagingConfig = prodConfig.clone();
        stagingConfig.setAppName("DataPipeline-Staging");
        stagingConfig.setConfig("spark.executor.memory", "4g");
        
        // All configs independent ✅
        System.out.println(prodConfig.getAppName());     // "DataPipeline"
        System.out.println(devConfig.getAppName());      // "DataPipeline-Dev"
        System.out.println(stagingConfig.getAppName());  // "DataPipeline-Staging"
    }
}
```

---

## 🎯 Summary: When to Use Each Pattern

| Pattern | Use When | Example |
|---------|----------|---------|
| **Singleton** | Need exactly one instance | Connection pool, Logger, Config |
| **Factory Method** | Don't know exact type at compile time | Data parsers (JSON, XML, Avro) |
| **Abstract Factory** | Need families of related objects | Multi-cloud (AWS, GCP, Azure) |
| **Builder** | Object has many optional parameters | Complex queries, configurations |
| **Prototype** | Creating object is expensive | Clone Spark configs, deep copies |

---

## 🎓 For 40 LPA SDE-Data Interviews

**Common Questions:**
1. "Design a data pipeline that supports multiple formats" → Factory/Abstract Factory
2. "Implement connection pooling" → Singleton (with proper synchronization)
3. "Build complex SQL queries programmatically" → Builder
4. "Clone Spark configurations for different environments" → Prototype
5. "Support multiple cloud providers" → Abstract Factory

**Key Points:**
- Always consider thread-safety (use volatile, synchronized, or enum)
- Prefer composition over inheritance
- Make objects immutable when possible (Builder pattern)
- Use dependency injection (easier to test)

---

**Next:** [STRUCTURAL-PATTERNS.md](STRUCTURAL-PATTERNS.md) — Adapter, Decorator, Proxy, Composite patterns
