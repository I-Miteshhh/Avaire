# Design Patterns - Structural Patterns

**Learning Time:** 2-3 weeks  
**Prerequisites:** Creational Patterns  
**Difficulty:** Intermediate → How to compose objects and classes

---

## 📚 Table of Contents

1. [Adapter Pattern](#adapter-pattern)
2. [Decorator Pattern](#decorator-pattern)
3. [Proxy Pattern](#proxy-pattern)
4. [Composite Pattern](#composite-pattern)
5. [Facade Pattern](#facade-pattern)
6. [Bridge Pattern](#bridge-pattern)
7. [Flyweight Pattern](#flyweight-pattern)

---

## 1. Adapter Pattern

### Intent
Convert interface of a class into another interface clients expect. Allows incompatible interfaces to work together.

### When to Use (SDE-Data)
```
├─ Integrate third-party libraries with different APIs
├─ Migrate from old API to new API gradually
├─ Support multiple data formats (CSV → JSON, JSON → Avro)
├─ Wrap legacy code with modern interfaces
```

### Example: Data Source Adapters

```java
/**
 * Scenario: You have legacy CSV reader, but new system expects JSON
 */

// Target interface (what client expects)
public interface JsonDataSource {
    Map<String, Object> readAsJson();
}

// Adaptee (existing CSV reader)
public class CsvReader {
    private final String filePath;
    
    public CsvReader(String filePath) {
        this.filePath = filePath;
    }
    
    public List<String[]> readCsv() {
        List<String[]> rows = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
            String line;
            while ((line = br.readLine()) != null) {
                rows.add(line.split(","));
            }
        } catch (IOException e) {
            throw new RuntimeException("Failed to read CSV", e);
        }
        return rows;
    }
}

// Adapter: CSV → JSON
public class CsvToJsonAdapter implements JsonDataSource {
    private final CsvReader csvReader;
    private final String[] headers;
    
    public CsvToJsonAdapter(CsvReader csvReader, String[] headers) {
        this.csvReader = csvReader;
        this.headers = headers;
    }
    
    @Override
    public Map<String, Object> readAsJson() {
        List<String[]> rows = csvReader.readCsv();
        
        List<Map<String, String>> records = new ArrayList<>();
        for (int i = 1; i < rows.size(); i++) {  // Skip header row
            String[] row = rows.get(i);
            Map<String, String> record = new HashMap<>();
            
            for (int j = 0; j < headers.length && j < row.length; j++) {
                record.put(headers[j], row[j]);
            }
            records.add(record);
        }
        
        return Map.of("data", records, "count", records.size());
    }
}

// Client code (works with JSON interface)
public class DataProcessor {
    public void process(JsonDataSource dataSource) {
        Map<String, Object> json = dataSource.readAsJson();
        System.out.println("Processing " + json.get("count") + " records");
        
        @SuppressWarnings("unchecked")
        List<Map<String, String>> data = (List<Map<String, String>>) json.get("data");
        
        for (Map<String, String> record : data) {
            System.out.println(record);
        }
    }
}

// Usage
public class Main {
    public static void main(String[] args) {
        // Legacy CSV reader
        CsvReader csvReader = new CsvReader("data.csv");
        
        // Adapt to JSON interface
        String[] headers = {"id", "name", "age", "country"};
        JsonDataSource jsonAdapter = new CsvToJsonAdapter(csvReader, headers);
        
        // Client works with JSON interface, doesn't know about CSV! ✅
        DataProcessor processor = new DataProcessor();
        processor.process(jsonAdapter);
    }
}
```

### Real-World: Kafka → Kinesis Adapter

```java
/**
 * SDE-Data: Adapt Kafka consumer to Kinesis-like interface
 */

// Target interface (Kinesis-style)
public interface StreamConsumer {
    List<Record> getRecords(int maxRecords);
    void commitCheckpoint(String sequenceNumber);
}

// Record class
public class Record {
    private final String sequenceNumber;
    private final byte[] data;
    private final long timestamp;
    
    public Record(String sequenceNumber, byte[] data, long timestamp) {
        this.sequenceNumber = sequenceNumber;
        this.data = data;
        this.timestamp = timestamp;
    }
    
    public String getSequenceNumber() { return sequenceNumber; }
    public byte[] getData() { return data; }
    public long getTimestamp() { return timestamp; }
}

// Kafka adapter
public class KafkaStreamAdapter implements StreamConsumer {
    private final KafkaConsumer<String, byte[]> kafkaConsumer;
    private final Duration pollTimeout;
    
    public KafkaStreamAdapter(KafkaConsumer<String, byte[]> kafkaConsumer) {
        this.kafkaConsumer = kafkaConsumer;
        this.pollTimeout = Duration.ofSeconds(1);
    }
    
    @Override
    public List<Record> getRecords(int maxRecords) {
        ConsumerRecords<String, byte[]> kafkaRecords = kafkaConsumer.poll(pollTimeout);
        
        List<Record> records = new ArrayList<>();
        for (ConsumerRecord<String, byte[]> kafkaRecord : kafkaRecords) {
            if (records.size() >= maxRecords) break;
            
            // Convert Kafka offset to sequence number
            String sequenceNumber = kafkaRecord.topic() + "-" + 
                                   kafkaRecord.partition() + "-" + 
                                   kafkaRecord.offset();
            
            records.add(new Record(
                sequenceNumber,
                kafkaRecord.value(),
                kafkaRecord.timestamp()
            ));
        }
        
        return records;
    }
    
    @Override
    public void commitCheckpoint(String sequenceNumber) {
        // Parse sequence number to get offset
        String[] parts = sequenceNumber.split("-");
        String topic = parts[0];
        int partition = Integer.parseInt(parts[1]);
        long offset = Long.parseLong(parts[2]);
        
        // Commit offset
        Map<TopicPartition, OffsetAndMetadata> offsets = new HashMap<>();
        offsets.put(
            new TopicPartition(topic, partition),
            new OffsetAndMetadata(offset + 1)
        );
        kafkaConsumer.commitSync(offsets);
    }
}

// Client code (stream-processing logic, agnostic to Kafka/Kinesis)
public class StreamProcessor {
    private final StreamConsumer consumer;
    
    public StreamProcessor(StreamConsumer consumer) {
        this.consumer = consumer;
    }
    
    public void processStream() {
        while (true) {
            List<Record> records = consumer.getRecords(100);
            
            if (records.isEmpty()) {
                continue;
            }
            
            for (Record record : records) {
                processRecord(record);
            }
            
            // Checkpoint last record
            String lastSequenceNumber = records.get(records.size() - 1).getSequenceNumber();
            consumer.commitCheckpoint(lastSequenceNumber);
        }
    }
    
    private void processRecord(Record record) {
        // Process record
        String data = new String(record.getData());
        System.out.println("Processing: " + data);
    }
}

// Usage: Switch between Kafka and Kinesis easily
public class Main {
    public static void main(String[] args) {
        // Use Kafka
        KafkaConsumer<String, byte[]> kafkaConsumer = new KafkaConsumer<>(getKafkaProps());
        kafkaConsumer.subscribe(Collections.singletonList("my-topic"));
        
        StreamConsumer kafkaAdapter = new KafkaStreamAdapter(kafkaConsumer);
        StreamProcessor processor = new StreamProcessor(kafkaAdapter);
        processor.processStream();
        
        // Switch to Kinesis? Just create KinesisStreamAdapter!
        // StreamConsumer kinesisAdapter = new KinesisStreamAdapter(...);
        // processor = new StreamProcessor(kinesisAdapter);
    }
    
    private static Properties getKafkaProps() {
        Properties props = new Properties();
        props.put("bootstrap.servers", "localhost:9092");
        props.put("group.id", "my-group");
        props.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        props.put("value.deserializer", "org.apache.kafka.common.serialization.ByteArrayDeserializer");
        return props;
    }
}
```

---

## 2. Decorator Pattern

### Intent
Attach additional responsibilities to an object dynamically. Provides flexible alternative to subclassing for extending functionality.

### When to Use (SDE-Data)
```
├─ Add logging, caching, compression, encryption without modifying original class
├─ Combine multiple behaviors (cache + compress + encrypt)
├─ Add features to objects at runtime
```

### Example: Data Stream Decorators

```java
/**
 * Component interface
 */
public interface DataStream {
    void write(byte[] data);
    byte[] read();
}

// Concrete component (basic implementation)
public class FileDataStream implements DataStream {
    private final String filePath;
    private byte[] buffer;
    
    public FileDataStream(String filePath) {
        this.filePath = filePath;
    }
    
    @Override
    public void write(byte[] data) {
        try {
            Files.write(Paths.get(filePath), data);
            this.buffer = data;
        } catch (IOException e) {
            throw new RuntimeException("Failed to write file", e);
        }
    }
    
    @Override
    public byte[] read() {
        try {
            return Files.readAllBytes(Paths.get(filePath));
        } catch (IOException e) {
            throw new RuntimeException("Failed to read file", e);
        }
    }
}

// Base decorator
public abstract class DataStreamDecorator implements DataStream {
    protected final DataStream wrappedStream;
    
    public DataStreamDecorator(DataStream wrappedStream) {
        this.wrappedStream = wrappedStream;
    }
    
    @Override
    public void write(byte[] data) {
        wrappedStream.write(data);
    }
    
    @Override
    public byte[] read() {
        return wrappedStream.read();
    }
}

// Concrete decorator: Compression
public class CompressionDecorator extends DataStreamDecorator {
    public CompressionDecorator(DataStream wrappedStream) {
        super(wrappedStream);
    }
    
    @Override
    public void write(byte[] data) {
        byte[] compressed = compress(data);
        System.out.println("Compressed: " + data.length + " → " + compressed.length + " bytes");
        wrappedStream.write(compressed);
    }
    
    @Override
    public byte[] read() {
        byte[] compressed = wrappedStream.read();
        byte[] decompressed = decompress(compressed);
        System.out.println("Decompressed: " + compressed.length + " → " + decompressed.length + " bytes");
        return decompressed;
    }
    
    private byte[] compress(byte[] data) {
        try {
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            GZIPOutputStream gzip = new GZIPOutputStream(bos);
            gzip.write(data);
            gzip.close();
            return bos.toByteArray();
        } catch (IOException e) {
            throw new RuntimeException("Compression failed", e);
        }
    }
    
    private byte[] decompress(byte[] data) {
        try {
            ByteArrayInputStream bis = new ByteArrayInputStream(data);
            GZIPInputStream gzip = new GZIPInputStream(bis);
            return gzip.readAllBytes();
        } catch (IOException e) {
            throw new RuntimeException("Decompression failed", e);
        }
    }
}

// Concrete decorator: Encryption
public class EncryptionDecorator extends DataStreamDecorator {
    private final String key;
    
    public EncryptionDecorator(DataStream wrappedStream, String key) {
        super(wrappedStream);
        this.key = key;
    }
    
    @Override
    public void write(byte[] data) {
        byte[] encrypted = encrypt(data, key);
        System.out.println("Encrypted data");
        wrappedStream.write(encrypted);
    }
    
    @Override
    public byte[] read() {
        byte[] encrypted = wrappedStream.read();
        byte[] decrypted = decrypt(encrypted, key);
        System.out.println("Decrypted data");
        return decrypted;
    }
    
    private byte[] encrypt(byte[] data, String key) {
        try {
            Cipher cipher = Cipher.getInstance("AES");
            SecretKeySpec keySpec = new SecretKeySpec(key.getBytes(), "AES");
            cipher.init(Cipher.ENCRYPT_MODE, keySpec);
            return cipher.doFinal(data);
        } catch (Exception e) {
            throw new RuntimeException("Encryption failed", e);
        }
    }
    
    private byte[] decrypt(byte[] data, String key) {
        try {
            Cipher cipher = Cipher.getInstance("AES");
            SecretKeySpec keySpec = new SecretKeySpec(key.getBytes(), "AES");
            cipher.init(Cipher.DECRYPT_MODE, keySpec);
            return cipher.doFinal(data);
        } catch (Exception e) {
            throw new RuntimeException("Decryption failed", e);
        }
    }
}

// Concrete decorator: Logging
public class LoggingDecorator extends DataStreamDecorator {
    public LoggingDecorator(DataStream wrappedStream) {
        super(wrappedStream);
    }
    
    @Override
    public void write(byte[] data) {
        System.out.println("[LOG] Writing " + data.length + " bytes");
        long start = System.currentTimeMillis();
        wrappedStream.write(data);
        long elapsed = System.currentTimeMillis() - start;
        System.out.println("[LOG] Write completed in " + elapsed + "ms");
    }
    
    @Override
    public byte[] read() {
        System.out.println("[LOG] Reading data");
        long start = System.currentTimeMillis();
        byte[] data = wrappedStream.read();
        long elapsed = System.currentTimeMillis() - start;
        System.out.println("[LOG] Read " + data.length + " bytes in " + elapsed + "ms");
        return data;
    }
}

// Usage: Stack decorators dynamically
public class Main {
    public static void main(String[] args) {
        String data = "This is sensitive data that needs to be compressed and encrypted!";
        
        // Base stream
        DataStream stream = new FileDataStream("output.dat");
        
        // Add logging
        stream = new LoggingDecorator(stream);
        
        // Add compression
        stream = new CompressionDecorator(stream);
        
        // Add encryption
        stream = new EncryptionDecorator(stream, "16ByteSecretKey");
        
        // Write: File ← Logging ← Compression ← Encryption
        stream.write(data.getBytes());
        
        // Read: File → Logging → Compression → Encryption
        byte[] readData = stream.read();
        System.out.println("Final data: " + new String(readData));
        
        /*
         * Output:
         * [LOG] Writing X bytes
         * Compressed: X → Y bytes
         * Encrypted data
         * [LOG] Write completed in Zms
         * 
         * [LOG] Reading data
         * Decrypted data
         * Decompressed: Y → X bytes
         * [LOG] Read X bytes in Zms
         * Final data: This is sensitive data...
         */
    }
}
```

### Real-World: Spark DataFrame Decorators

```java
/**
 * SDE-Data: Add transformations to Spark DataFrame dynamically
 */
public interface DataFrameProcessor {
    Dataset<Row> process(Dataset<Row> df);
}

// Base processor (no-op)
public class BaseProcessor implements DataFrameProcessor {
    @Override
    public Dataset<Row> process(Dataset<Row> df) {
        return df;
    }
}

// Filter decorator
public class FilterDecorator implements DataFrameProcessor {
    private final DataFrameProcessor wrapped;
    private final String condition;
    
    public FilterDecorator(DataFrameProcessor wrapped, String condition) {
        this.wrapped = wrapped;
        this.condition = condition;
    }
    
    @Override
    public Dataset<Row> process(Dataset<Row> df) {
        Dataset<Row> processed = wrapped.process(df);
        return processed.filter(condition);
    }
}

// Select decorator
public class SelectDecorator implements DataFrameProcessor {
    private final DataFrameProcessor wrapped;
    private final String[] columns;
    
    public SelectDecorator(DataFrameProcessor wrapped, String... columns) {
        this.wrapped = wrapped;
        this.columns = columns;
    }
    
    @Override
    public Dataset<Row> process(Dataset<Row> df) {
        Dataset<Row> processed = wrapped.process(df);
        return processed.select(columns);
    }
}

// Aggregation decorator
public class AggregateDecorator implements DataFrameProcessor {
    private final DataFrameProcessor wrapped;
    private final String groupByColumn;
    private final Map<String, String> aggregations;
    
    public AggregateDecorator(DataFrameProcessor wrapped, String groupByColumn, Map<String, String> aggregations) {
        this.wrapped = wrapped;
        this.groupByColumn = groupByColumn;
        this.aggregations = aggregations;
    }
    
    @Override
    public Dataset<Row> process(Dataset<Row> df) {
        Dataset<Row> processed = wrapped.process(df);
        
        RelationalGroupedDataset grouped = processed.groupBy(groupByColumn);
        
        // Build aggregation expressions
        Map<String, String> aggExprs = new HashMap<>(aggregations);
        return grouped.agg(aggExprs);
    }
}

// Usage: Build processing pipeline dynamically
public class DataPipeline {
    public static void main(String[] args) {
        SparkSession spark = SparkSession.builder()
            .appName("DecoratorExample")
            .master("local[*]")
            .getOrCreate();
        
        // Read data
        Dataset<Row> df = spark.read()
            .format("csv")
            .option("header", "true")
            .load("users.csv");
        
        // Build processing pipeline
        DataFrameProcessor processor = new BaseProcessor();
        
        // Filter: age >= 18
        processor = new FilterDecorator(processor, "age >= 18");
        
        // Select columns
        processor = new SelectDecorator(processor, "country", "age", "income");
        
        // Aggregate by country
        Map<String, String> aggr = Map.of(
            "age", "avg",
            "income", "sum"
        );
        processor = new AggregateDecorator(processor, "country", aggr);
        
        // Execute pipeline
        Dataset<Row> result = processor.process(df);
        result.show();
        
        spark.stop();
    }
}
```

---

## 3. Proxy Pattern

### Intent
Provide surrogate/placeholder for another object to control access to it.

### Types of Proxies
```
1. Virtual Proxy: Lazy initialization (create expensive object only when needed)
2. Protection Proxy: Access control (check permissions before delegating)
3. Remote Proxy: Represent object in different address space (RPC, REST)
4. Caching Proxy: Cache results of expensive operations
```

### Example: Caching Proxy for Data Queries

```java
/**
 * Subject interface
 */
public interface DataQuery {
    List<Map<String, Object>> execute(String query);
}

// Real subject (expensive database queries)
public class DatabaseQuery implements DataQuery {
    private final Connection connection;
    
    public DatabaseQuery(Connection connection) {
        this.connection = connection;
    }
    
    @Override
    public List<Map<String, Object>> execute(String query) {
        System.out.println("Executing database query: " + query);
        
        List<Map<String, Object>> results = new ArrayList<>();
        try (Statement stmt = connection.createStatement();
             ResultSet rs = stmt.executeQuery(query)) {
            
            ResultSetMetaData metaData = rs.getMetaData();
            int columnCount = metaData.getColumnCount();
            
            while (rs.next()) {
                Map<String, Object> row = new HashMap<>();
                for (int i = 1; i <= columnCount; i++) {
                    row.put(metaData.getColumnName(i), rs.getObject(i));
                }
                results.add(row);
            }
        } catch (SQLException e) {
            throw new RuntimeException("Query failed", e);
        }
        
        return results;
    }
}

// Caching proxy
public class CachingQueryProxy implements DataQuery {
    private final DataQuery realQuery;
    private final Map<String, CacheEntry> cache;
    private final long cacheTtlMillis;
    
    public CachingQueryProxy(DataQuery realQuery, long cacheTtlMillis) {
        this.realQuery = realQuery;
        this.cache = new ConcurrentHashMap<>();
        this.cacheTtlMillis = cacheTtlMillis;
    }
    
    @Override
    public List<Map<String, Object>> execute(String query) {
        // Check cache
        CacheEntry entry = cache.get(query);
        if (entry != null && !entry.isExpired()) {
            System.out.println("Cache hit for query: " + query);
            return entry.getResults();
        }
        
        // Cache miss, execute real query
        System.out.println("Cache miss for query: " + query);
        List<Map<String, Object>> results = realQuery.execute(query);
        
        // Store in cache
        cache.put(query, new CacheEntry(results, System.currentTimeMillis() + cacheTtlMillis));
        
        return results;
    }
    
    private static class CacheEntry {
        private final List<Map<String, Object>> results;
        private final long expirationTime;
        
        public CacheEntry(List<Map<String, Object>> results, long expirationTime) {
            this.results = new ArrayList<>(results);  // Defensive copy
            this.expirationTime = expirationTime;
        }
        
        public List<Map<String, Object>> getResults() {
            return new ArrayList<>(results);  // Return copy
        }
        
        public boolean isExpired() {
            return System.currentTimeMillis() > expirationTime;
        }
    }
}

// Usage
public class Main {
    public static void main(String[] args) throws Exception {
        Connection connection = DriverManager.getConnection(
            "jdbc:postgresql://localhost:5432/mydb", "user", "password"
        );
        
        // Real query
        DataQuery realQuery = new DatabaseQuery(connection);
        
        // Add caching proxy (5 minute TTL)
        DataQuery cachedQuery = new CachingQueryProxy(realQuery, 5 * 60 * 1000);
        
        // First execution: Cache miss, executes real query
        List<Map<String, Object>> results1 = cachedQuery.execute("SELECT * FROM users");
        
        // Second execution: Cache hit, no database query!
        List<Map<String, Object>> results2 = cachedQuery.execute("SELECT * FROM users");
        
        // Different query: Cache miss
        List<Map<String, Object>> results3 = cachedQuery.execute("SELECT * FROM orders");
        
        connection.close();
    }
}
```

### Real-World: S3 Virtual Proxy (Lazy Loading)

```java
/**
 * SDE-Data: Lazy load large S3 objects only when accessed
 */
public interface S3Object {
    byte[] getContent();
    long getSize();
    String getKey();
}

// Real S3 object (expensive to load)
public class RealS3Object implements S3Object {
    private final S3Client s3Client;
    private final String bucket;
    private final String key;
    private byte[] content;
    
    public RealS3Object(S3Client s3Client, String bucket, String key) {
        this.s3Client = s3Client;
        this.bucket = bucket;
        this.key = key;
    }
    
    @Override
    public byte[] getContent() {
        if (content == null) {
            System.out.println("Loading S3 object: s3://" + bucket + "/" + key);
            
            ResponseBytes<GetObjectResponse> responseBytes = s3Client.getObjectAsBytes(
                GetObjectRequest.builder()
                    .bucket(bucket)
                    .key(key)
                    .build()
            );
            
            content = responseBytes.asByteArray();
            System.out.println("Loaded " + content.length + " bytes");
        }
        return content;
    }
    
    @Override
    public long getSize() {
        HeadObjectResponse response = s3Client.headObject(
            HeadObjectRequest.builder()
                .bucket(bucket)
                .key(key)
                .build()
        );
        return response.contentLength();
    }
    
    @Override
    public String getKey() {
        return key;
    }
}

// Virtual proxy (lazy initialization)
public class LazyS3ObjectProxy implements S3Object {
    private final S3Client s3Client;
    private final String bucket;
    private final String key;
    private RealS3Object realObject;
    
    public LazyS3ObjectProxy(S3Client s3Client, String bucket, String key) {
        this.s3Client = s3Client;
        this.bucket = bucket;
        this.key = key;
    }
    
    @Override
    public byte[] getContent() {
        if (realObject == null) {
            realObject = new RealS3Object(s3Client, bucket, key);
        }
        return realObject.getContent();
    }
    
    @Override
    public long getSize() {
        if (realObject == null) {
            // Don't load entire object just to get size
            HeadObjectResponse response = s3Client.headObject(
                HeadObjectRequest.builder()
                    .bucket(bucket)
                    .key(key)
                    .build()
            );
            return response.contentLength();
        }
        return realObject.getSize();
    }
    
    @Override
    public String getKey() {
        return key;
    }
}

// Usage: Load objects only when content is accessed
public class S3DataProcessor {
    public static void main(String[] args) {
        S3Client s3Client = S3Client.builder().build();
        
        // Create proxies for 1000 objects (lightweight)
        List<S3Object> objects = new ArrayList<>();
        for (int i = 0; i < 1000; i++) {
            objects.add(new LazyS3ObjectProxy(s3Client, "my-bucket", "file-" + i + ".json"));
        }
        
        // Filter by size without loading content ✅
        List<S3Object> largeObjects = objects.stream()
            .filter(obj -> obj.getSize() > 1024 * 1024)  // > 1 MB
            .collect(Collectors.toList());
        
        System.out.println("Found " + largeObjects.size() + " large objects");
        
        // Now load content only for large objects
        for (S3Object obj : largeObjects) {
            byte[] content = obj.getContent();  // Loaded here!
            processContent(content);
        }
    }
    
    private static void processContent(byte[] content) {
        // Process content
    }
}
```

---

## 4. Composite Pattern

### Intent
Compose objects into tree structures to represent part-whole hierarchies. Lets clients treat individual objects and compositions uniformly.

### When to Use (SDE-Data)
```
├─ File system (files and directories)
├─ Query expressions (AND, OR, NOT combinations)
├─ Data transformation pipelines (nested transformations)
├─ Organization charts (employees and departments)
```

### Example: Query Expression Tree

```java
/**
 * Component interface
 */
public interface QueryExpression {
    boolean evaluate(Map<String, Object> record);
    String toSql();
}

// Leaf: Simple condition
public class SimpleCondition implements QueryExpression {
    private final String column;
    private final String operator;
    private final Object value;
    
    public SimpleCondition(String column, String operator, Object value) {
        this.column = column;
        this.operator = operator;
        this.value = value;
    }
    
    @Override
    public boolean evaluate(Map<String, Object> record) {
        Object columnValue = record.get(column);
        if (columnValue == null) return false;
        
        switch (operator) {
            case "=":
                return columnValue.equals(value);
            case ">":
                return ((Comparable) columnValue).compareTo(value) > 0;
            case "<":
                return ((Comparable) columnValue).compareTo(value) < 0;
            case ">=":
                return ((Comparable) columnValue).compareTo(value) >= 0;
            case "<=":
                return ((Comparable) columnValue).compareTo(value) <= 0;
            default:
                throw new IllegalArgumentException("Unknown operator: " + operator);
        }
    }
    
    @Override
    public String toSql() {
        String valueStr = value instanceof String ? "'" + value + "'" : value.toString();
        return column + " " + operator + " " + valueStr;
    }
}

// Composite: AND
public class AndExpression implements QueryExpression {
    private final List<QueryExpression> expressions;
    
    public AndExpression(QueryExpression... expressions) {
        this.expressions = Arrays.asList(expressions);
    }
    
    @Override
    public boolean evaluate(Map<String, Object> record) {
        return expressions.stream().allMatch(expr -> expr.evaluate(record));
    }
    
    @Override
    public String toSql() {
        return expressions.stream()
            .map(QueryExpression::toSql)
            .collect(Collectors.joining(" AND ", "(", ")"));
    }
}

// Composite: OR
public class OrExpression implements QueryExpression {
    private final List<QueryExpression> expressions;
    
    public OrExpression(QueryExpression... expressions) {
        this.expressions = Arrays.asList(expressions);
    }
    
    @Override
    public boolean evaluate(Map<String, Object> record) {
        return expressions.stream().anyMatch(expr -> expr.evaluate(record));
    }
    
    @Override
    public String toSql() {
        return expressions.stream()
            .map(QueryExpression::toSql)
            .collect(Collectors.joining(" OR ", "(", ")"));
    }
}

// Composite: NOT
public class NotExpression implements QueryExpression {
    private final QueryExpression expression;
    
    public NotExpression(QueryExpression expression) {
        this.expression = expression;
    }
    
    @Override
    public boolean evaluate(Map<String, Object> record) {
        return !expression.evaluate(record);
    }
    
    @Override
    public String toSql() {
        return "NOT " + expression.toSql();
    }
}

// Usage: Build complex query trees
public class QueryBuilder {
    public static void main(String[] args) {
        // (age >= 18 AND country = 'USA') OR (vip = true)
        QueryExpression query = new OrExpression(
            new AndExpression(
                new SimpleCondition("age", ">=", 18),
                new SimpleCondition("country", "=", "USA")
            ),
            new SimpleCondition("vip", "=", true)
        );
        
        // Test with data
        Map<String, Object> record1 = Map.of("age", 25, "country", "USA", "vip", false);
        Map<String, Object> record2 = Map.of("age", 16, "country", "USA", "vip", false);
        Map<String, Object> record3 = Map.of("age", 30, "country", "UK", "vip", true);
        
        System.out.println("Record 1: " + query.evaluate(record1));  // true (age >= 18 AND country = 'USA')
        System.out.println("Record 2: " + query.evaluate(record2));  // false
        System.out.println("Record 3: " + query.evaluate(record3));  // true (vip = true)
        
        // Generate SQL
        System.out.println("SQL: " + query.toSql());
        // ((age >= 18 AND country = 'USA') OR (vip = true))
    }
}
```

### Real-World: Data Transformation Pipeline

```java
/**
 * SDE-Data: Composite pattern for nested data transformations
 */
public interface Transformation {
    Dataset<Row> apply(Dataset<Row> df);
    String describe();
}

// Leaf transformations
public class FilterTransformation implements Transformation {
    private final String condition;
    
    public FilterTransformation(String condition) {
        this.condition = condition;
    }
    
    @Override
    public Dataset<Row> apply(Dataset<Row> df) {
        return df.filter(condition);
    }
    
    @Override
    public String describe() {
        return "Filter: " + condition;
    }
}

public class SelectTransformation implements Transformation {
    private final String[] columns;
    
    public SelectTransformation(String... columns) {
        this.columns = columns;
    }
    
    @Override
    public Dataset<Row> apply(Dataset<Row> df) {
        return df.select(columns);
    }
    
    @Override
    public String describe() {
        return "Select: " + String.join(", ", columns);
    }
}

// Composite transformation
public class CompositeTransformation implements Transformation {
    private final List<Transformation> transformations;
    private final String name;
    
    public CompositeTransformation(String name) {
        this.transformations = new ArrayList<>();
        this.name = name;
    }
    
    public void add(Transformation transformation) {
        transformations.add(transformation);
    }
    
    @Override
    public Dataset<Row> apply(Dataset<Row> df) {
        Dataset<Row> result = df;
        for (Transformation transformation : transformations) {
            result = transformation.apply(result);
        }
        return result;
    }
    
    @Override
    public String describe() {
        StringBuilder sb = new StringBuilder(name + ":\n");
        for (Transformation transformation : transformations) {
            sb.append("  - ").append(transformation.describe()).append("\n");
        }
        return sb.toString();
    }
}

// Usage: Nest transformations
public class DataPipeline {
    public static void main(String[] args) {
        SparkSession spark = SparkSession.builder()
            .appName("CompositeExample")
            .master("local[*]")
            .getOrCreate();
        
        Dataset<Row> df = spark.read()
            .format("csv")
            .option("header", "true")
            .load("users.csv");
        
        // Build transformation pipeline
        CompositeTransformation cleaningStage = new CompositeTransformation("Cleaning");
        cleaningStage.add(new FilterTransformation("age IS NOT NULL"));
        cleaningStage.add(new FilterTransformation("email IS NOT NULL"));
        
        CompositeTransformation transformationStage = new CompositeTransformation("Transformation");
        transformationStage.add(new SelectTransformation("id", "name", "age", "country"));
        transformationStage.add(new FilterTransformation("age >= 18"));
        
        CompositeTransformation fullPipeline = new CompositeTransformation("Full Pipeline");
        fullPipeline.add(cleaningStage);      // Nested composite!
        fullPipeline.add(transformationStage); // Nested composite!
        
        // Execute pipeline
        Dataset<Row> result = fullPipeline.apply(df);
        result.show();
        
        // Describe pipeline
        System.out.println(fullPipeline.describe());
        /*
         * Full Pipeline:
         *   - Cleaning:
         *     - Filter: age IS NOT NULL
         *     - Filter: email IS NOT NULL
         *   - Transformation:
         *     - Select: id, name, age, country
         *     - Filter: age >= 18
         */
        
        spark.stop();
    }
}
```

---

## 5. Facade Pattern

### Intent
Provide unified, simplified interface to a complex subsystem. Makes subsystem easier to use.

### When to Use (SDE-Data)
```
├─ Hide complexity of multiple AWS SDK calls
├─ Simplify complex data pipeline operations
├─ Provide high-level API over low-level libraries
├─ Create layer of abstraction over third-party APIs
```

### Example: Data Pipeline Facade

```java
/**
 * Complex subsystem with many classes
 */

// S3 operations
public class S3Service {
    private final S3Client s3Client;
    
    public S3Service() {
        this.s3Client = S3Client.builder().build();
    }
    
    public void uploadFile(String bucket, String key, byte[] data) {
        s3Client.putObject(
            PutObjectRequest.builder().bucket(bucket).key(key).build(),
            RequestBody.fromBytes(data)
        );
        System.out.println("Uploaded to S3: s3://" + bucket + "/" + key);
    }
    
    public byte[] downloadFile(String bucket, String key) {
        ResponseBytes<GetObjectResponse> response = s3Client.getObjectAsBytes(
            GetObjectRequest.builder().bucket(bucket).key(key).build()
        );
        System.out.println("Downloaded from S3: s3://" + bucket + "/" + key);
        return response.asByteArray();
    }
}

// Glue operations
public class GlueService {
    private final GlueClient glueClient;
    
    public GlueService() {
        this.glueClient = GlueClient.builder().build();
    }
    
    public void startCrawler(String crawlerName) {
        glueClient.startCrawler(
            StartCrawlerRequest.builder().name(crawlerName).build()
        );
        System.out.println("Started Glue crawler: " + crawlerName);
    }
    
    public void waitForCrawler(String crawlerName) throws InterruptedException {
        while (true) {
            GetCrawlerResponse response = glueClient.getCrawler(
                GetCrawlerRequest.builder().name(crawlerName).build()
            );
            
            CrawlerState state = response.crawler().state();
            if (state == CrawlerState.READY) {
                System.out.println("Crawler completed");
                break;
            }
            
            Thread.sleep(5000);
        }
    }
}

// Athena operations
public class AthenaService {
    private final AthenaClient athenaClient;
    private final String outputLocation;
    
    public AthenaService(String outputLocation) {
        this.athenaClient = AthenaClient.builder().build();
        this.outputLocation = outputLocation;
    }
    
    public List<Map<String, String>> executeQuery(String query) {
        // Start query execution
        StartQueryExecutionResponse response = athenaClient.startQueryExecution(
            StartQueryExecutionRequest.builder()
                .queryString(query)
                .resultConfiguration(
                    ResultConfiguration.builder()
                        .outputLocation(outputLocation)
                        .build()
                )
                .build()
        );
        
        String queryExecutionId = response.queryExecutionId();
        System.out.println("Started Athena query: " + queryExecutionId);
        
        // Wait for completion
        waitForQuery(queryExecutionId);
        
        // Get results
        return getQueryResults(queryExecutionId);
    }
    
    private void waitForQuery(String queryExecutionId) {
        while (true) {
            GetQueryExecutionResponse response = athenaClient.getQueryExecution(
                GetQueryExecutionRequest.builder()
                    .queryExecutionId(queryExecutionId)
                    .build()
            );
            
            QueryExecutionState state = response.queryExecution().status().state();
            if (state == QueryExecutionState.SUCCEEDED) {
                System.out.println("Query succeeded");
                break;
            } else if (state == QueryExecutionState.FAILED || state == QueryExecutionState.CANCELLED) {
                throw new RuntimeException("Query failed: " + response.queryExecution().status().stateChangeReason());
            }
            
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new RuntimeException(e);
            }
        }
    }
    
    private List<Map<String, String>> getQueryResults(String queryExecutionId) {
        GetQueryResultsResponse response = athenaClient.getQueryResults(
            GetQueryResultsRequest.builder()
                .queryExecutionId(queryExecutionId)
                .build()
        );
        
        List<Map<String, String>> results = new ArrayList<>();
        List<Row> rows = response.resultSet().rows();
        
        if (rows.isEmpty()) return results;
        
        // Extract column names
        Row headerRow = rows.get(0);
        List<String> columns = headerRow.data().stream()
            .map(Datum::varCharValue)
            .collect(Collectors.toList());
        
        // Extract data rows
        for (int i = 1; i < rows.size(); i++) {
            Row dataRow = rows.get(i);
            Map<String, String> record = new HashMap<>();
            
            for (int j = 0; j < columns.size(); j++) {
                record.put(columns.get(j), dataRow.data().get(j).varCharValue());
            }
            results.add(record);
        }
        
        return results;
    }
}

/**
 * FACADE: Simplified interface to the complex subsystem
 */
public class DataPipelineFacade {
    private final S3Service s3Service;
    private final GlueService glueService;
    private final AthenaService athenaService;
    private final String bucketName;
    
    public DataPipelineFacade(String bucketName, String athenaOutputLocation) {
        this.s3Service = new S3Service();
        this.glueService = new GlueService();
        this.athenaService = new AthenaService(athenaOutputLocation);
        this.bucketName = bucketName;
    }
    
    /**
     * Single method to ingest, catalog, and query data
     * Hides complexity of S3 + Glue + Athena interactions
     */
    public List<Map<String, String>> ingestAndQuery(
        String fileName, 
        byte[] fileData, 
        String crawlerName, 
        String query
    ) throws InterruptedException {
        
        // Step 1: Upload to S3
        String s3Key = "data/" + fileName;
        s3Service.uploadFile(bucketName, s3Key, fileData);
        
        // Step 2: Catalog with Glue
        glueService.startCrawler(crawlerName);
        glueService.waitForCrawler(crawlerName);
        
        // Step 3: Query with Athena
        List<Map<String, String>> results = athenaService.executeQuery(query);
        
        System.out.println("Pipeline completed successfully!");
        return results;
    }
    
    /**
     * Simplified upload method
     */
    public void uploadData(String fileName, byte[] data) {
        s3Service.uploadFile(bucketName, "data/" + fileName, data);
    }
    
    /**
     * Simplified query method
     */
    public List<Map<String, String>> queryData(String sql) {
        return athenaService.executeQuery(sql);
    }
}

// Usage: Client uses simple facade instead of complex subsystem
public class Main {
    public static void main(String[] args) throws Exception {
        // Without facade ❌ (complex, many steps)
        S3Service s3 = new S3Service();
        GlueService glue = new GlueService();
        AthenaService athena = new AthenaService("s3://my-bucket/athena-results/");
        
        s3.uploadFile("my-bucket", "data/file.csv", "id,name\n1,John".getBytes());
        glue.startCrawler("my-crawler");
        glue.waitForCrawler("my-crawler");
        List<Map<String, String>> results1 = athena.executeQuery("SELECT * FROM my_table");
        
        // With facade ✅ (simple, one method call)
        DataPipelineFacade pipeline = new DataPipelineFacade(
            "my-bucket", 
            "s3://my-bucket/athena-results/"
        );
        
        List<Map<String, String>> results2 = pipeline.ingestAndQuery(
            "file.csv",
            "id,name\n1,John".getBytes(),
            "my-crawler",
            "SELECT * FROM my_table"
        );
        
        System.out.println("Results: " + results2);
    }
}
```

---

## 6. Bridge Pattern

### Intent
Decouple abstraction from implementation so both can vary independently.

### When to Use (SDE-Data)
```
├─ Support multiple data formats (JSON, XML, Avro) with multiple storage backends (S3, HDFS, Local)
├─ Separate business logic from platform-specific code
├─ Avoid explosion of subclasses (N abstractions × M implementations = N+M classes instead of N×M)
```

### Example: Data Storage Bridge

```java
/**
 * Implementation interface (backend)
 */
public interface StorageImplementation {
    void writeBytes(String path, byte[] data);
    byte[] readBytes(String path);
    void delete(String path);
}

// Concrete implementation: S3
public class S3Storage implements StorageImplementation {
    private final S3Client s3Client;
    private final String bucket;
    
    public S3Storage(String bucket) {
        this.s3Client = S3Client.builder().build();
        this.bucket = bucket;
    }
    
    @Override
    public void writeBytes(String path, byte[] data) {
        s3Client.putObject(
            PutObjectRequest.builder().bucket(bucket).key(path).build(),
            RequestBody.fromBytes(data)
        );
        System.out.println("S3: Wrote " + data.length + " bytes to s3://" + bucket + "/" + path);
    }
    
    @Override
    public byte[] readBytes(String path) {
        ResponseBytes<GetObjectResponse> response = s3Client.getObjectAsBytes(
            GetObjectRequest.builder().bucket(bucket).key(path).build()
        );
        System.out.println("S3: Read from s3://" + bucket + "/" + path);
        return response.asByteArray();
    }
    
    @Override
    public void delete(String path) {
        s3Client.deleteObject(
            DeleteObjectRequest.builder().bucket(bucket).key(path).build()
        );
        System.out.println("S3: Deleted s3://" + bucket + "/" + path);
    }
}

// Concrete implementation: Local file system
public class LocalStorage implements StorageImplementation {
    private final String basePath;
    
    public LocalStorage(String basePath) {
        this.basePath = basePath;
    }
    
    @Override
    public void writeBytes(String path, byte[] data) {
        try {
            Path fullPath = Paths.get(basePath, path);
            Files.createDirectories(fullPath.getParent());
            Files.write(fullPath, data);
            System.out.println("Local: Wrote " + data.length + " bytes to " + fullPath);
        } catch (IOException e) {
            throw new RuntimeException("Failed to write file", e);
        }
    }
    
    @Override
    public byte[] readBytes(String path) {
        try {
            Path fullPath = Paths.get(basePath, path);
            System.out.println("Local: Read from " + fullPath);
            return Files.readAllBytes(fullPath);
        } catch (IOException e) {
            throw new RuntimeException("Failed to read file", e);
        }
    }
    
    @Override
    public void delete(String path) {
        try {
            Path fullPath = Paths.get(basePath, path);
            Files.delete(fullPath);
            System.out.println("Local: Deleted " + fullPath);
        } catch (IOException e) {
            throw new RuntimeException("Failed to delete file", e);
        }
    }
}

/**
 * Abstraction (data format layer)
 */
public abstract class DataStore {
    protected final StorageImplementation storage;
    
    protected DataStore(StorageImplementation storage) {
        this.storage = storage;
    }
    
    public abstract void save(String path, Object data);
    public abstract <T> T load(String path, Class<T> type);
    public void delete(String path) {
        storage.delete(path);
    }
}

// Refined abstraction: JSON
public class JsonDataStore extends DataStore {
    private final ObjectMapper objectMapper;
    
    public JsonDataStore(StorageImplementation storage) {
        super(storage);
        this.objectMapper = new ObjectMapper();
    }
    
    @Override
    public void save(String path, Object data) {
        try {
            byte[] json = objectMapper.writeValueAsBytes(data);
            storage.writeBytes(path, json);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Failed to serialize JSON", e);
        }
    }
    
    @Override
    public <T> T load(String path, Class<T> type) {
        byte[] json = storage.readBytes(path);
        try {
            return objectMapper.readValue(json, type);
        } catch (IOException e) {
            throw new RuntimeException("Failed to deserialize JSON", e);
        }
    }
}

// Refined abstraction: Avro
public class AvroDataStore extends DataStore {
    public AvroDataStore(StorageImplementation storage) {
        super(storage);
    }
    
    @Override
    public void save(String path, Object data) {
        // Avro serialization
        if (!(data instanceof SpecificRecord)) {
            throw new IllegalArgumentException("Data must be Avro SpecificRecord");
        }
        
        SpecificRecord record = (SpecificRecord) data;
        DatumWriter<SpecificRecord> datumWriter = new SpecificDatumWriter<>(record.getSchema());
        
        try (ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            BinaryEncoder encoder = EncoderFactory.get().binaryEncoder(out, null);
            datumWriter.write(record, encoder);
            encoder.flush();
            storage.writeBytes(path, out.toByteArray());
        } catch (IOException e) {
            throw new RuntimeException("Failed to serialize Avro", e);
        }
    }
    
    @Override
    public <T> T load(String path, Class<T> type) {
        byte[] avroData = storage.readBytes(path);
        
        try {
            SpecificRecord record = (SpecificRecord) type.getDeclaredConstructor().newInstance();
            DatumReader<SpecificRecord> datumReader = new SpecificDatumReader<>(record.getSchema());
            BinaryDecoder decoder = DecoderFactory.get().binaryDecoder(avroData, null);
            
            @SuppressWarnings("unchecked")
            T result = (T) datumReader.read(null, decoder);
            return result;
        } catch (Exception e) {
            throw new RuntimeException("Failed to deserialize Avro", e);
        }
    }
}

// Usage: Mix and match formats and storage
public class Main {
    public static void main(String[] args) {
        // User POJO
        class User {
            public String name;
            public int age;
            
            public User() {}
            public User(String name, int age) {
                this.name = name;
                this.age = age;
            }
        }
        
        User user = new User("Alice", 30);
        
        // JSON + S3
        DataStore jsonS3 = new JsonDataStore(new S3Storage("my-bucket"));
        jsonS3.save("users/alice.json", user);
        User loaded1 = jsonS3.load("users/alice.json", User.class);
        
        // JSON + Local
        DataStore jsonLocal = new JsonDataStore(new LocalStorage("/tmp/data"));
        jsonLocal.save("users/alice.json", user);
        User loaded2 = jsonLocal.load("users/alice.json", User.class);
        
        // Avro + S3
        // DataStore avroS3 = new AvroDataStore(new S3Storage("my-bucket"));
        // avroS3.save("users/alice.avro", avroRecord);
        
        /*
         * Without Bridge: Need 6 classes
         *   - JsonS3Store, JsonLocalStore, JsonHdfsStore
         *   - AvroS3Store, AvroLocalStore, AvroHdfsStore
         * 
         * With Bridge: Need 5 classes (2 formats + 3 storages)
         *   - JsonDataStore, AvroDataStore
         *   - S3Storage, LocalStorage, HdfsStorage
         */
    }
}
```

---

## 7. Flyweight Pattern

### Intent
Share common state among many objects to save memory. Separate intrinsic (shared) and extrinsic (unique) state.

### When to Use (SDE-Data)
```
├─ Many similar objects with shared state (e.g., coordinate pairs, product catalog)
├─ Memory constrained environments
├─ Connection pooling, thread pooling
├─ String interning (Java does this automatically)
```

### Example: Geolocation Flyweight

```java
/**
 * Scenario: Store millions of user locations
 * Problem: Each User object stores city, country strings → high memory
 * Solution: Share Location objects (Flyweight)
 */

// Flyweight: Location (intrinsic state - shared)
public class Location {
    private final String city;
    private final String country;
    private final double latitude;
    private final double longitude;
    
    public Location(String city, String country, double latitude, double longitude) {
        this.city = city;
        this.country = country;
        this.latitude = latitude;
        this.longitude = longitude;
    }
    
    public String getCity() { return city; }
    public String getCountry() { return country; }
    public double getLatitude() { return latitude; }
    public double getLongitude() { return longitude; }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Location)) return false;
        Location location = (Location) o;
        return Double.compare(location.latitude, latitude) == 0 &&
               Double.compare(location.longitude, longitude) == 0 &&
               city.equals(location.city) &&
               country.equals(location.country);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(city, country, latitude, longitude);
    }
}

// Flyweight factory
public class LocationFactory {
    private static final Map<String, Location> locations = new ConcurrentHashMap<>();
    
    public static Location getLocation(String city, String country, double latitude, double longitude) {
        String key = city + "," + country;
        
        return locations.computeIfAbsent(key, k -> {
            System.out.println("Creating new Location: " + city + ", " + country);
            return new Location(city, country, latitude, longitude);
        });
    }
    
    public static int getLocationCount() {
        return locations.size();
    }
}

// Context: User (extrinsic state - unique)
public class User {
    private final String id;
    private final String name;
    private final Location location;  // Reference to shared flyweight
    
    public User(String id, String name, Location location) {
        this.id = id;
        this.name = name;
        this.location = location;
    }
    
    public String getId() { return id; }
    public String getName() { return name; }
    public Location getLocation() { return location; }
}

// Usage
public class Main {
    public static void main(String[] args) {
        // Create 1 million users, but only ~100 unique locations
        List<User> users = new ArrayList<>();
        
        for (int i = 0; i < 1_000_000; i++) {
            String city = "City" + (i % 100);
            String country = "Country" + (i % 10);
            double lat = 40.0 + (i % 100) * 0.1;
            double lon = -74.0 + (i % 100) * 0.1;
            
            Location location = LocationFactory.getLocation(city, country, lat, lon);
            users.add(new User("user-" + i, "User " + i, location));
        }
        
        System.out.println("Created " + users.size() + " users");
        System.out.println("Unique locations: " + LocationFactory.getLocationCount());
        // Output: Created 1000000 users, Unique locations: 100
        
        /*
         * Memory savings:
         * - Without flyweight: 1M users × (city + country strings) = ~32 MB
         * - With flyweight: 100 locations × (city + country strings) = ~3.2 KB
         * - Savings: ~99.99% ✅
         */
    }
}
```

### Real-World: Connection Pool (Flyweight)

```java
/**
 * SDE-Data: Database connection pool (reuse expensive connections)
 */
public class DatabaseConnection {
    private final String url;
    private final Connection connection;
    private boolean inUse;
    
    public DatabaseConnection(String url) throws SQLException {
        this.url = url;
        this.connection = DriverManager.getConnection(url);
        this.inUse = false;
        System.out.println("Created new DB connection to " + url);
    }
    
    public Connection getConnection() {
        return connection;
    }
    
    public boolean isInUse() {
        return inUse;
    }
    
    public void setInUse(boolean inUse) {
        this.inUse = inUse;
    }
}

public class ConnectionPool {
    private final String url;
    private final List<DatabaseConnection> pool;
    private final int maxSize;
    
    public ConnectionPool(String url, int maxSize) {
        this.url = url;
        this.pool = new ArrayList<>();
        this.maxSize = maxSize;
    }
    
    public synchronized Connection acquireConnection() throws SQLException {
        // Try to find available connection
        for (DatabaseConnection dbConn : pool) {
            if (!dbConn.isInUse()) {
                dbConn.setInUse(true);
                System.out.println("Reusing connection from pool");
                return dbConn.getConnection();
            }
        }
        
        // Create new connection if pool not full
        if (pool.size() < maxSize) {
            DatabaseConnection dbConn = new DatabaseConnection(url);
            dbConn.setInUse(true);
            pool.add(dbConn);
            return dbConn.getConnection();
        }
        
        throw new SQLException("Connection pool exhausted");
    }
    
    public synchronized void releaseConnection(Connection connection) {
        for (DatabaseConnection dbConn : pool) {
            if (dbConn.getConnection() == connection) {
                dbConn.setInUse(false);
                System.out.println("Released connection to pool");
                return;
            }
        }
    }
    
    public synchronized int getPoolSize() {
        return pool.size();
    }
}

// Usage
public class Main {
    public static void main(String[] args) throws SQLException {
        ConnectionPool pool = new ConnectionPool("jdbc:postgresql://localhost:5432/mydb", 5);
        
        // Acquire connections
        Connection conn1 = pool.acquireConnection();  // Creates new connection
        Connection conn2 = pool.acquireConnection();  // Creates new connection
        Connection conn3 = pool.acquireConnection();  // Creates new connection
        
        // Release connections
        pool.releaseConnection(conn1);
        pool.releaseConnection(conn2);
        
        // Reuse connections ✅
        Connection conn4 = pool.acquireConnection();  // Reuses conn1 or conn2
        Connection conn5 = pool.acquireConnection();  // Reuses conn1 or conn2
        
        System.out.println("Pool size: " + pool.getPoolSize());  // 3 (not 5)
        
        /*
         * Flyweight benefits:
         * - Expensive connections created once
         * - Reused many times
         * - Memory and latency savings
         */
    }
}
```

---

## 🎯 Key Takeaways

| Pattern | Purpose | SDE-Data Use Case | Memory/Performance Impact |
|---------|---------|-------------------|---------------------------|
| **Adapter** | Make incompatible interfaces work together | Kafka ↔ Kinesis, CSV ↔ JSON | No overhead |
| **Decorator** | Add responsibilities dynamically | Logging, caching, compression, encryption | Minimal (wrapper objects) |
| **Proxy** | Control access to object | Lazy loading S3 objects, query caching | Saves memory/network |
| **Composite** | Tree structures, treat individual/composite uniformly | Query expressions, transformation pipelines | No overhead |
| **Facade** | Simplified interface to complex system | Multi-step AWS operations | No overhead |
| **Bridge** | Separate abstraction from implementation | Different data formats + storage backends | Reduces class explosion |
| **Flyweight** | Share common state to save memory | String interning, connection pooling | **Huge memory savings** |

---

### Interview Tips: Structural Patterns

**Adapter vs Bridge:**
- **Adapter**: Convert existing interface (works with legacy code)
- **Bridge**: Design new system to separate abstraction/implementation

**Decorator vs Proxy:**
- **Decorator**: Add new functionality (enhance behavior)
- **Proxy**: Control access to existing functionality (lazy loading, caching, security)

**Composite Pattern Identification:**
- Any time you see tree structures: file systems, organization charts, UI components
- Classic interview: "Implement file system with files and directories"

**Flyweight Pattern Identification:**
- Memory optimization question
- "Store 1 million user locations" → Use flyweight for shared city/country data
- Connection pooling is flyweight!

---

**Next:** [BEHAVIORAL-PATTERNS.md](BEHAVIORAL-PATTERNS.md) — Strategy, Observer, Command, Template Method, Chain of Responsibility
