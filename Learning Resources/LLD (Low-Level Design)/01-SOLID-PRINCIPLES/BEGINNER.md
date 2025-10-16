# SOLID Principles - BEGINNER

**Learning Time:** 1-2 weeks  
**Prerequisites:** Basic Java/OOP knowledge  
**Difficulty:** Fundamental → Foundation of all good software design

---

## 📚 Table of Contents

1. [Introduction to SOLID](#introduction-to-solid)
2. [S - Single Responsibility Principle (SRP)](#single-responsibility-principle)
3. [O - Open/Closed Principle (OCP)](#openclosed-principle)
4. [L - Liskov Substitution Principle (LSP)](#liskov-substitution-principle)
5. [I - Interface Segregation Principle (ISP)](#interface-segregation-principle)
6. [D - Dependency Inversion Principle (DIP)](#dependency-inversion-principle)
7. [Real-World Examples](#real-world-examples)
8. [Common Violations and Fixes](#common-violations-and-fixes)

---

## Introduction to SOLID

**SOLID** is an acronym for five design principles that make software designs more:
- **Understandable:** Easy to read and maintain
- **Flexible:** Easy to change and extend
- **Maintainable:** Easy to fix bugs and add features

**Origin:** Coined by Robert C. Martin (Uncle Bob) in early 2000s

**Why SOLID matters for SDE-Data (40 LPA target):**
```
Interview Questions You'll Face:
├─ "Design a data pipeline orchestrator" → Need SRP, OCP, DIP
├─ "Implement a plugin system for data transformations" → Need OCP, DIP
├─ "Design a multi-tenant analytics platform" → Need ISP, LSP
└─ "Handle multiple data sources (SQL, NoSQL, APIs)" → Need all SOLID principles
```

---

## 1. Single Responsibility Principle (SRP)

### Definition

> **A class should have one, and only one, reason to change.**
> — Robert C. Martin

**Simplified:** Each class should do ONE thing and do it well.

### Why SRP Matters

```
Without SRP:
├─ God classes with 5000+ lines (impossible to test, maintain)
├─ Changes in one feature break unrelated features
├─ Multiple developers edit same file → merge conflicts
└─ Hard to reuse code (class does too many things)

With SRP:
├─ Small, focused classes (100-200 lines typical)
├─ Changes isolated to specific classes
├─ Easy to test (mock dependencies)
└─ Easy to reuse (compose classes)
```

### ❌ Violation Example: God Class

```java
/**
 * WRONG: Employee class has multiple responsibilities
 * - Calculate salary (business logic)
 * - Save to database (persistence)
 * - Generate reports (presentation)
 */
public class Employee {
    private String name;
    private String role;
    private double baseSalary;
    
    // Responsibility 1: Business logic
    public double calculateSalary() {
        if (role.equals("ENGINEER")) {
            return baseSalary * 1.2;
        } else if (role.equals("MANAGER")) {
            return baseSalary * 1.5;
        }
        return baseSalary;
    }
    
    // Responsibility 2: Database operations
    public void saveToDatabase() {
        Connection conn = DriverManager.getConnection(
            "jdbc:mysql://localhost:3306/company", "root", "password"
        );
        PreparedStatement stmt = conn.prepareStatement(
            "INSERT INTO employees (name, role, salary) VALUES (?, ?, ?)"
        );
        stmt.setString(1, name);
        stmt.setString(2, role);
        stmt.setDouble(3, calculateSalary());
        stmt.executeUpdate();
        conn.close();
    }
    
    // Responsibility 3: Report generation
    public String generateReport() {
        return "Employee Report\n" +
               "Name: " + name + "\n" +
               "Role: " + role + "\n" +
               "Salary: $" + calculateSalary();
    }
}

/**
 * Problems:
 * 1. Change in salary calculation → Must modify Employee class
 * 2. Change in database schema → Must modify Employee class
 * 3. Change in report format → Must modify Employee class
 * 4. Hard to test (need real database for tests)
 * 5. Violates SRP: 3 reasons to change!
 */
```

### ✅ Correct Example: Separated Responsibilities

```java
/**
 * CORRECT: Each class has single responsibility
 */

// Responsibility 1: Domain model (only data + business logic)
public class Employee {
    private final String id;
    private final String name;
    private final String role;
    private final double baseSalary;
    
    public Employee(String id, String name, String role, double baseSalary) {
        this.id = id;
        this.name = name;
        this.role = role;
        this.baseSalary = baseSalary;
    }
    
    // Getters only (immutable)
    public String getId() { return id; }
    public String getName() { return name; }
    public String getRole() { return role; }
    public double getBaseSalary() { return baseSalary; }
}

// Responsibility 2: Salary calculation (business logic)
public class SalaryCalculator {
    private static final double ENGINEER_MULTIPLIER = 1.2;
    private static final double MANAGER_MULTIPLIER = 1.5;
    
    public double calculate(Employee employee) {
        switch (employee.getRole()) {
            case "ENGINEER":
                return employee.getBaseSalary() * ENGINEER_MULTIPLIER;
            case "MANAGER":
                return employee.getBaseSalary() * MANAGER_MULTIPLIER;
            default:
                return employee.getBaseSalary();
        }
    }
}

// Responsibility 3: Database operations (persistence)
public class EmployeeRepository {
    private final DataSource dataSource;
    
    public EmployeeRepository(DataSource dataSource) {
        this.dataSource = dataSource;
    }
    
    public void save(Employee employee, double salary) {
        try (Connection conn = dataSource.getConnection();
             PreparedStatement stmt = conn.prepareStatement(
                 "INSERT INTO employees (id, name, role, salary) VALUES (?, ?, ?, ?)"
             )) {
            stmt.setString(1, employee.getId());
            stmt.setString(2, employee.getName());
            stmt.setString(3, employee.getRole());
            stmt.setDouble(4, salary);
            stmt.executeUpdate();
        } catch (SQLException e) {
            throw new RuntimeException("Failed to save employee", e);
        }
    }
    
    public Employee findById(String id) {
        // Implementation
        return null;
    }
}

// Responsibility 4: Report generation (presentation)
public class EmployeeReportGenerator {
    private final SalaryCalculator salaryCalculator;
    
    public EmployeeReportGenerator(SalaryCalculator salaryCalculator) {
        this.salaryCalculator = salaryCalculator;
    }
    
    public String generateReport(Employee employee) {
        double salary = salaryCalculator.calculate(employee);
        return String.format(
            "Employee Report\nName: %s\nRole: %s\nSalary: $%.2f",
            employee.getName(),
            employee.getRole(),
            salary
        );
    }
}

// Usage: Compose classes
public class EmployeeService {
    private final SalaryCalculator salaryCalculator;
    private final EmployeeRepository repository;
    private final EmployeeReportGenerator reportGenerator;
    
    public EmployeeService(
        SalaryCalculator salaryCalculator,
        EmployeeRepository repository,
        EmployeeReportGenerator reportGenerator
    ) {
        this.salaryCalculator = salaryCalculator;
        this.repository = repository;
        this.reportGenerator = reportGenerator;
    }
    
    public void processEmployee(Employee employee) {
        double salary = salaryCalculator.calculate(employee);
        repository.save(employee, salary);
        String report = reportGenerator.generateReport(employee);
        System.out.println(report);
    }
}

/**
 * Benefits:
 * 1. Change salary logic → Modify only SalaryCalculator
 * 2. Change database → Modify only EmployeeRepository
 * 3. Change report format → Modify only EmployeeReportGenerator
 * 4. Easy to test (mock dependencies)
 * 5. Easy to reuse (e.g., use SalaryCalculator in different contexts)
 */
```

### Real-World Example: Data Pipeline

```java
/**
 * SDE-Data scenario: Extract-Transform-Load (ETL) pipeline
 */

// ❌ WRONG: Single class does everything
public class DataPipeline {
    public void run() {
        // Extract
        List<String> rawData = readFromS3("s3://bucket/data.csv");
        
        // Transform
        List<Record> transformed = rawData.stream()
            .map(line -> line.split(","))
            .map(fields -> new Record(fields[0], fields[1]))
            .filter(record -> record.isValid())
            .collect(Collectors.toList());
        
        // Load
        Connection conn = connectToRedshift();
        for (Record record : transformed) {
            insertIntoDatabase(conn, record);
        }
        conn.close();
        
        // Monitor
        sendMetricsToCloudWatch(transformed.size());
        
        // Alert
        if (transformed.size() < 1000) {
            sendSlackAlert("Low data volume!");
        }
    }
}

// ✅ CORRECT: Separate responsibilities
public interface DataExtractor {
    List<String> extract();
}

public class S3DataExtractor implements DataExtractor {
    private final AmazonS3 s3Client;
    private final String bucketName;
    private final String key;
    
    public S3DataExtractor(AmazonS3 s3Client, String bucketName, String key) {
        this.s3Client = s3Client;
        this.bucketName = bucketName;
        this.key = key;
    }
    
    @Override
    public List<String> extract() {
        S3Object object = s3Client.getObject(bucketName, key);
        try (BufferedReader reader = new BufferedReader(
            new InputStreamReader(object.getObjectContent())
        )) {
            return reader.lines().collect(Collectors.toList());
        } catch (IOException e) {
            throw new RuntimeException("Failed to extract from S3", e);
        }
    }
}

public interface DataTransformer<I, O> {
    O transform(I input);
}

public class CsvToRecordTransformer implements DataTransformer<String, Record> {
    @Override
    public Record transform(String csvLine) {
        String[] fields = csvLine.split(",");
        return new Record(fields[0], fields[1]);
    }
}

public interface DataLoader<T> {
    void load(List<T> data);
}

public class RedshiftDataLoader implements DataLoader<Record> {
    private final DataSource dataSource;
    
    public RedshiftDataLoader(DataSource dataSource) {
        this.dataSource = dataSource;
    }
    
    @Override
    public void load(List<Record> records) {
        try (Connection conn = dataSource.getConnection()) {
            conn.setAutoCommit(false);
            
            try (PreparedStatement stmt = conn.prepareStatement(
                "INSERT INTO records (id, value) VALUES (?, ?)"
            )) {
                for (Record record : records) {
                    stmt.setString(1, record.getId());
                    stmt.setString(2, record.getValue());
                    stmt.addBatch();
                }
                stmt.executeBatch();
                conn.commit();
            } catch (SQLException e) {
                conn.rollback();
                throw e;
            }
        } catch (SQLException e) {
            throw new RuntimeException("Failed to load to Redshift", e);
        }
    }
}

public interface MetricsPublisher {
    void publish(String metricName, double value);
}

public class CloudWatchMetricsPublisher implements MetricsPublisher {
    private final AmazonCloudWatch cloudWatch;
    
    public CloudWatchMetricsPublisher(AmazonCloudWatch cloudWatch) {
        this.cloudWatch = cloudWatch;
    }
    
    @Override
    public void publish(String metricName, double value) {
        PutMetricDataRequest request = new PutMetricDataRequest()
            .withNamespace("DataPipeline")
            .withMetricData(new MetricDatum()
                .withMetricName(metricName)
                .withValue(value)
                .withTimestamp(new Date()));
        cloudWatch.putMetricData(request);
    }
}

public interface Alerter {
    void alert(String message);
}

public class SlackAlerter implements Alerter {
    private final String webhookUrl;
    
    public SlackAlerter(String webhookUrl) {
        this.webhookUrl = webhookUrl;
    }
    
    @Override
    public void alert(String message) {
        // Send to Slack webhook
        HttpPost post = new HttpPost(webhookUrl);
        String payload = String.format("{\"text\": \"%s\"}", message);
        post.setEntity(new StringEntity(payload, ContentType.APPLICATION_JSON));
        
        try (CloseableHttpClient httpClient = HttpClients.createDefault()) {
            httpClient.execute(post);
        } catch (IOException e) {
            throw new RuntimeException("Failed to send Slack alert", e);
        }
    }
}

// Orchestrator: Composes all components
public class DataPipelineOrchestrator {
    private final DataExtractor extractor;
    private final DataTransformer<String, Record> transformer;
    private final DataLoader<Record> loader;
    private final MetricsPublisher metricsPublisher;
    private final Alerter alerter;
    
    public DataPipelineOrchestrator(
        DataExtractor extractor,
        DataTransformer<String, Record> transformer,
        DataLoader<Record> loader,
        MetricsPublisher metricsPublisher,
        Alerter alerter
    ) {
        this.extractor = extractor;
        this.transformer = transformer;
        this.loader = loader;
        this.metricsPublisher = metricsPublisher;
        this.alerter = alerter;
    }
    
    public void run() {
        // Extract
        List<String> rawData = extractor.extract();
        
        // Transform
        List<Record> transformedData = rawData.stream()
            .map(transformer::transform)
            .filter(Record::isValid)
            .collect(Collectors.toList());
        
        // Load
        loader.load(transformedData);
        
        // Monitor
        metricsPublisher.publish("RecordsProcessed", transformedData.size());
        
        // Alert if needed
        if (transformedData.size() < 1000) {
            alerter.alert("Low data volume: " + transformedData.size());
        }
    }
}

/**
 * Benefits:
 * 1. Easy to swap S3 → Kafka (implement KafkaDataExtractor)
 * 2. Easy to test each component in isolation
 * 3. Easy to add new data sources (implement DataExtractor)
 * 4. Easy to change alert channel (implement Alerter for PagerDuty, email, etc.)
 * 5. Each class has single responsibility
 */
```

---

## 2. Open/Closed Principle (OCP)

### Definition

> **Software entities should be open for extension, but closed for modification.**
> — Bertrand Meyer

**Simplified:** Add new features by adding new code, not modifying existing code.

### Why OCP Matters

```
Without OCP:
├─ Every new feature requires modifying existing classes
├─ Risk of breaking existing functionality
├─ Hard to add features without full codebase understanding
└─ Regression bugs when adding features

With OCP:
├─ Add features by creating new classes (no risk to existing code)
├─ Existing code remains stable
├─ Easy to extend (plugin architecture)
└─ Low regression risk
```

### ❌ Violation Example: If-Else Hell

```java
/**
 * WRONG: Adding new payment method requires modifying PaymentProcessor
 */
public class PaymentProcessor {
    public void processPayment(String paymentType, double amount) {
        if (paymentType.equals("CREDIT_CARD")) {
            // Credit card logic
            System.out.println("Processing credit card payment: $" + amount);
            chargeCreditCard(amount);
        } else if (paymentType.equals("PAYPAL")) {
            // PayPal logic
            System.out.println("Processing PayPal payment: $" + amount);
            chargePayPal(amount);
        } else if (paymentType.equals("BITCOIN")) {
            // Bitcoin logic
            System.out.println("Processing Bitcoin payment: $" + amount);
            chargeBitcoin(amount);
        }
        // Every new payment method requires modifying this method! ❌
    }
    
    private void chargeCreditCard(double amount) { /* ... */ }
    private void chargePayPal(double amount) { /* ... */ }
    private void chargeBitcoin(double amount) { /* ... */ }
}

/**
 * Problems:
 * 1. Add Apple Pay → Modify processPayment() method
 * 2. Violates OCP (not closed for modification)
 * 3. Hard to test (need to test all payment types every time)
 * 4. Risk of breaking existing payment methods
 */
```

### ✅ Correct Example: Strategy Pattern

```java
/**
 * CORRECT: Use polymorphism for extension
 */

// Abstract interface (closed for modification)
public interface PaymentMethod {
    void processPayment(double amount);
    String getPaymentType();
}

// Concrete implementations (open for extension)
public class CreditCardPayment implements PaymentMethod {
    private final String cardNumber;
    private final String cvv;
    
    public CreditCardPayment(String cardNumber, String cvv) {
        this.cardNumber = cardNumber;
        this.cvv = cvv;
    }
    
    @Override
    public void processPayment(double amount) {
        System.out.println("Processing credit card payment: $" + amount);
        // Credit card specific logic
        validateCard();
        chargeCard(amount);
    }
    
    @Override
    public String getPaymentType() {
        return "CREDIT_CARD";
    }
    
    private void validateCard() { /* ... */ }
    private void chargeCard(double amount) { /* ... */ }
}

public class PayPalPayment implements PaymentMethod {
    private final String email;
    
    public PayPalPayment(String email) {
        this.email = email;
    }
    
    @Override
    public void processPayment(double amount) {
        System.out.println("Processing PayPal payment: $" + amount);
        // PayPal specific logic
        authenticateWithPayPal();
        transferFunds(amount);
    }
    
    @Override
    public String getPaymentType() {
        return "PAYPAL";
    }
    
    private void authenticateWithPayPal() { /* ... */ }
    private void transferFunds(double amount) { /* ... */ }
}

public class BitcoinPayment implements PaymentMethod {
    private final String walletAddress;
    
    public BitcoinPayment(String walletAddress) {
        this.walletAddress = walletAddress;
    }
    
    @Override
    public void processPayment(double amount) {
        System.out.println("Processing Bitcoin payment: $" + amount);
        // Bitcoin specific logic
        double btcAmount = convertToBTC(amount);
        sendToWallet(btcAmount);
    }
    
    @Override
    public String getPaymentType() {
        return "BITCOIN";
    }
    
    private double convertToBTC(double usdAmount) { return usdAmount / 50000; }
    private void sendToWallet(double btcAmount) { /* ... */ }
}

// Payment processor (closed for modification)
public class PaymentProcessor {
    public void processPayment(PaymentMethod paymentMethod, double amount) {
        paymentMethod.processPayment(amount);
    }
}

// Usage
public class Main {
    public static void main(String[] args) {
        PaymentProcessor processor = new PaymentProcessor();
        
        // Credit card payment
        PaymentMethod creditCard = new CreditCardPayment("1234-5678-9012-3456", "123");
        processor.processPayment(creditCard, 100.0);
        
        // PayPal payment
        PaymentMethod paypal = new PayPalPayment("user@example.com");
        processor.processPayment(paypal, 50.0);
        
        // Bitcoin payment
        PaymentMethod bitcoin = new BitcoinPayment("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa");
        processor.processPayment(bitcoin, 200.0);
    }
}

/**
 * Adding Apple Pay? Just create new class:
 */
public class ApplePayPayment implements PaymentMethod {
    private final String deviceToken;
    
    public ApplePayPayment(String deviceToken) {
        this.deviceToken = deviceToken;
    }
    
    @Override
    public void processPayment(double amount) {
        System.out.println("Processing Apple Pay payment: $" + amount);
        // Apple Pay logic
    }
    
    @Override
    public String getPaymentType() {
        return "APPLE_PAY";
    }
}

// NO modification to PaymentProcessor needed! ✅
```

### Real-World Example: Data Format Serializers

```java
/**
 * SDE-Data scenario: Support multiple data formats (JSON, Avro, Parquet, Protobuf)
 */

// ❌ WRONG: If-else for each format
public class DataSerializer {
    public byte[] serialize(Object data, String format) {
        if (format.equals("JSON")) {
            return serializeToJson(data);
        } else if (format.equals("AVRO")) {
            return serializeToAvro(data);
        } else if (format.equals("PARQUET")) {
            return serializeToParquet(data);
        }
        throw new IllegalArgumentException("Unknown format: " + format);
    }
    
    // Adding Protobuf requires modifying this class ❌
}

// ✅ CORRECT: Strategy pattern
public interface DataSerializer<T> {
    byte[] serialize(T data);
    T deserialize(byte[] bytes);
    String getFormat();
}

public class JsonDataSerializer<T> implements DataSerializer<T> {
    private final ObjectMapper objectMapper;
    private final Class<T> clazz;
    
    public JsonDataSerializer(Class<T> clazz) {
        this.objectMapper = new ObjectMapper();
        this.clazz = clazz;
    }
    
    @Override
    public byte[] serialize(T data) {
        try {
            return objectMapper.writeValueAsBytes(data);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("JSON serialization failed", e);
        }
    }
    
    @Override
    public T deserialize(byte[] bytes) {
        try {
            return objectMapper.readValue(bytes, clazz);
        } catch (IOException e) {
            throw new RuntimeException("JSON deserialization failed", e);
        }
    }
    
    @Override
    public String getFormat() {
        return "JSON";
    }
}

public class AvroDataSerializer<T extends SpecificRecordBase> implements DataSerializer<T> {
    private final Schema schema;
    
    public AvroDataSerializer(Schema schema) {
        this.schema = schema;
    }
    
    @Override
    public byte[] serialize(T data) {
        ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
        DatumWriter<T> datumWriter = new SpecificDatumWriter<>(schema);
        BinaryEncoder encoder = EncoderFactory.get().binaryEncoder(outputStream, null);
        
        try {
            datumWriter.write(data, encoder);
            encoder.flush();
            return outputStream.toByteArray();
        } catch (IOException e) {
            throw new RuntimeException("Avro serialization failed", e);
        }
    }
    
    @Override
    public T deserialize(byte[] bytes) {
        DatumReader<T> datumReader = new SpecificDatumReader<>(schema);
        BinaryDecoder decoder = DecoderFactory.get().binaryDecoder(bytes, null);
        
        try {
            return datumReader.read(null, decoder);
        } catch (IOException e) {
            throw new RuntimeException("Avro deserialization failed", e);
        }
    }
    
    @Override
    public String getFormat() {
        return "AVRO";
    }
}

// Serializer registry (open for extension)
public class SerializerFactory {
    private final Map<String, DataSerializer<?>> serializers = new ConcurrentHashMap<>();
    
    public <T> void registerSerializer(DataSerializer<T> serializer) {
        serializers.put(serializer.getFormat(), serializer);
    }
    
    @SuppressWarnings("unchecked")
    public <T> DataSerializer<T> getSerializer(String format) {
        DataSerializer<T> serializer = (DataSerializer<T>) serializers.get(format);
        if (serializer == null) {
            throw new IllegalArgumentException("No serializer for format: " + format);
        }
        return serializer;
    }
}

// Usage
public class DataPipeline {
    private final SerializerFactory serializerFactory;
    
    public DataPipeline(SerializerFactory serializerFactory) {
        this.serializerFactory = serializerFactory;
    }
    
    public byte[] serializeData(Object data, String format) {
        DataSerializer<Object> serializer = serializerFactory.getSerializer(format);
        return serializer.serialize(data);
    }
}

// Setup
SerializerFactory factory = new SerializerFactory();
factory.registerSerializer(new JsonDataSerializer<>(MyData.class));
factory.registerSerializer(new AvroDataSerializer<>(MyAvroData.getClassSchema()));

// Add Protobuf? Just create ProtobufDataSerializer and register! ✅
factory.registerSerializer(new ProtobufDataSerializer<>());
```

---

## 3. Liskov Substitution Principle (LSP)

### Definition

> **Objects of a superclass should be replaceable with objects of a subclass without breaking the application.**
> — Barbara Liskov

**Simplified:** Subclasses should behave like their parent classes. Don't surprise users!

### LSP Rules

```
1. Preconditions cannot be strengthened in subclass
   Example: Parent accepts null → Child must also accept null

2. Postconditions cannot be weakened in subclass
   Example: Parent guarantees non-null return → Child must also return non-null

3. Invariants must be preserved
   Example: Parent maintains sorted list → Child must also keep list sorted

4. History constraint (immutability)
   Example: Parent is immutable → Child must be immutable
```

### ❌ Violation Example: Rectangle-Square Problem

```java
/**
 * WRONG: Square violates LSP
 */
public class Rectangle {
    protected int width;
    protected int height;
    
    public void setWidth(int width) {
        this.width = width;
    }
    
    public void setHeight(int height) {
        this.height = height;
    }
    
    public int getArea() {
        return width * height;
    }
}

public class Square extends Rectangle {
    @Override
    public void setWidth(int width) {
        // Square must have equal sides
        this.width = width;
        this.height = width;  // ❌ Violates LSP!
    }
    
    @Override
    public void setHeight(int height) {
        this.width = height;
        this.height = height;  // ❌ Violates LSP!
    }
}

// Test code that works for Rectangle but fails for Square
public class AreaCalculator {
    public void testRectangle(Rectangle rectangle) {
        rectangle.setWidth(5);
        rectangle.setHeight(4);
        
        // Expected: 5 * 4 = 20
        int area = rectangle.getArea();
        assert area == 20 : "Expected 20, got " + area;
    }
}

// Usage
Rectangle rect = new Rectangle();
testRectangle(rect);  // ✅ Passes (area = 20)

Rectangle square = new Square();
testRectangle(square);  // ❌ Fails! (area = 16, not 20)
// Square changed behavior, violating LSP
```

### ✅ Correct Example: Separate Hierarchies

```java
/**
 * CORRECT: Don't force inheritance where it doesn't fit
 */
public interface Shape {
    int getArea();
}

public class Rectangle implements Shape {
    private final int width;
    private final int height;
    
    public Rectangle(int width, int height) {
        this.width = width;
        this.height = height;
    }
    
    public int getWidth() { return width; }
    public int getHeight() { return height; }
    
    @Override
    public int getArea() {
        return width * height;
    }
}

public class Square implements Shape {
    private final int side;
    
    public Square(int side) {
        this.side = side;
    }
    
    public int getSide() { return side; }
    
    @Override
    public int getArea() {
        return side * side;
    }
}

// No violation: Rectangle and Square are separate classes ✅
```

### Real-World Example: Data Sources

```java
/**
 * SDE-Data scenario: Different data sources (SQL, NoSQL, APIs)
 */

// ❌ WRONG: Violating LSP
public abstract class DataSource {
    public abstract List<Record> fetchData(String query);
    
    // All data sources must support transactions
    public abstract void beginTransaction();
    public abstract void commit();
    public abstract void rollback();
}

public class MySQLDataSource extends DataSource {
    @Override
    public List<Record> fetchData(String query) {
        // Execute SQL query
        return executeQuery(query);
    }
    
    @Override
    public void beginTransaction() {
        // MySQL supports transactions ✅
        connection.setAutoCommit(false);
    }
    
    @Override
    public void commit() {
        connection.commit();
    }
    
    @Override
    public void rollback() {
        connection.rollback();
    }
}

public class MongoDBDataSource extends DataSource {
    @Override
    public List<Record> fetchData(String query) {
        // Execute MongoDB query
        return executeMongoQuery(query);
    }
    
    @Override
    public void beginTransaction() {
        // MongoDB doesn't support transactions in older versions! ❌
        throw new UnsupportedOperationException("MongoDB doesn't support transactions");
    }
    
    @Override
    public void commit() {
        throw new UnsupportedOperationException("MongoDB doesn't support transactions");
    }
    
    @Override
    public void rollback() {
        throw new UnsupportedOperationException("MongoDB doesn't support transactions");
    }
}

// Violates LSP: Can't substitute MySQLDataSource with MongoDBDataSource ❌

// ✅ CORRECT: Interface segregation + composition
public interface DataSource {
    List<Record> fetchData(String query);
}

public interface TransactionalDataSource extends DataSource {
    void beginTransaction();
    void commit();
    void rollback();
}

public class MySQLDataSource implements TransactionalDataSource {
    private final Connection connection;
    
    public MySQLDataSource(Connection connection) {
        this.connection = connection;
    }
    
    @Override
    public List<Record> fetchData(String query) {
        try (Statement stmt = connection.createStatement();
             ResultSet rs = stmt.executeQuery(query)) {
            List<Record> records = new ArrayList<>();
            while (rs.next()) {
                records.add(new Record(rs.getString(1), rs.getString(2)));
            }
            return records;
        } catch (SQLException e) {
            throw new RuntimeException("Query failed", e);
        }
    }
    
    @Override
    public void beginTransaction() {
        try {
            connection.setAutoCommit(false);
        } catch (SQLException e) {
            throw new RuntimeException("Failed to begin transaction", e);
        }
    }
    
    @Override
    public void commit() {
        try {
            connection.commit();
        } catch (SQLException e) {
            throw new RuntimeException("Failed to commit", e);
        }
    }
    
    @Override
    public void rollback() {
        try {
            connection.rollback();
        } catch (SQLException e) {
            throw new RuntimeException("Failed to rollback", e);
        }
    }
}

public class MongoDBDataSource implements DataSource {
    private final MongoDatabase database;
    
    public MongoDBDataSource(MongoDatabase database) {
        this.database = database;
    }
    
    @Override
    public List<Record> fetchData(String collectionName) {
        MongoCollection<Document> collection = database.getCollection(collectionName);
        List<Record> records = new ArrayList<>();
        
        for (Document doc : collection.find()) {
            records.add(new Record(
                doc.getString("id"),
                doc.getString("value")
            ));
        }
        return records;
    }
    
    // No transaction methods → No LSP violation ✅
}

// Usage
public class DataPipeline {
    private final DataSource dataSource;
    
    public DataPipeline(DataSource dataSource) {
        this.dataSource = dataSource;
    }
    
    public void extractData(String query) {
        List<Record> data = dataSource.fetchData(query);
        processData(data);
    }
    
    private void processData(List<Record> data) {
        // Process data
    }
}

// If you need transactions, use TransactionalDataSource
public class TransactionalDataPipeline {
    private final TransactionalDataSource dataSource;
    
    public TransactionalDataPipeline(TransactionalDataSource dataSource) {
        this.dataSource = dataSource;
    }
    
    public void extractDataWithTransaction(String query) {
        dataSource.beginTransaction();
        try {
            List<Record> data = dataSource.fetchData(query);
            processData(data);
            dataSource.commit();
        } catch (Exception e) {
            dataSource.rollback();
            throw e;
        }
    }
    
    private void processData(List<Record> data) {
        // Process data
    }
}

/**
 * Now:
 * - DataPipeline works with ANY DataSource (MySQL, MongoDB, API) ✅
 * - TransactionalDataPipeline works only with TransactionalDataSource (MySQL) ✅
 * - No LSP violation ✅
 */
```

---

## 4. Interface Segregation Principle (ISP)

### Definition

> **Clients should not be forced to depend on interfaces they don't use.**
> — Robert C. Martin

**Simplified:** Many small, specific interfaces are better than one large, general interface.

### Why ISP Matters

```
Without ISP (Fat Interface):
├─ Classes implement methods they don't need
├─ Forced to throw UnsupportedOperationException
├─ Hard to understand what class actually does
└─ Changes to interface affect all implementers

With ISP (Thin Interfaces):
├─ Classes implement only what they need
├─ Clear contracts
├─ Easy to understand capabilities
└─ Changes isolated to relevant classes
```

### ❌ Violation Example: Fat Interface

```java
/**
 * WRONG: One interface for all workers
 */
public interface Worker {
    void work();
    void eat();
    void sleep();
    void getSalary();
}

public class HumanWorker implements Worker {
    @Override
    public void work() {
        System.out.println("Human working...");
    }
    
    @Override
    public void eat() {
        System.out.println("Human eating lunch...");
    }
    
    @Override
    public void sleep() {
        System.out.println("Human sleeping at night...");
    }
    
    @Override
    public void getSalary() {
        System.out.println("Human receiving monthly salary...");
    }
}

public class RobotWorker implements Worker {
    @Override
    public void work() {
        System.out.println("Robot working 24/7...");
    }
    
    @Override
    public void eat() {
        // Robots don't eat! ❌
        throw new UnsupportedOperationException("Robots don't eat");
    }
    
    @Override
    public void sleep() {
        // Robots don't sleep! ❌
        throw new UnsupportedOperationException("Robots don't sleep");
    }
    
    @Override
    public void getSalary() {
        // Robots don't get salary! ❌
        throw new UnsupportedOperationException("Robots don't get salary");
    }
}

/**
 * Problems:
 * 1. RobotWorker forced to implement eat(), sleep(), getSalary()
 * 2. UnsupportedOperationException at runtime (not compile-time safe)
 * 3. Violates ISP
 */
```

### ✅ Correct Example: Segregated Interfaces

```java
/**
 * CORRECT: Multiple small interfaces
 */
public interface Workable {
    void work();
}

public interface Eatable {
    void eat();
}

public interface Sleepable {
    void sleep();
}

public interface Payable {
    void getSalary();
}

public class HumanWorker implements Workable, Eatable, Sleepable, Payable {
    @Override
    public void work() {
        System.out.println("Human working...");
    }
    
    @Override
    public void eat() {
        System.out.println("Human eating lunch...");
    }
    
    @Override
    public void sleep() {
        System.out.println("Human sleeping at night...");
    }
    
    @Override
    public void getSalary() {
        System.out.println("Human receiving monthly salary...");
    }
}

public class RobotWorker implements Workable {
    @Override
    public void work() {
        System.out.println("Robot working 24/7...");
    }
    
    // No need to implement eat(), sleep(), getSalary() ✅
}

// Usage
public class WorkManager {
    public void manageWork(Workable worker) {
        worker.work();
    }
    
    public void manageLunch(Eatable eater) {
        eater.eat();
    }
}

WorkManager manager = new WorkManager();
manager.manageWork(new HumanWorker());  // ✅
manager.manageWork(new RobotWorker());  // ✅
manager.manageLunch(new HumanWorker());  // ✅
// manager.manageLunch(new RobotWorker());  // ❌ Compile-time error (type safety!)
```

### Real-World Example: Data Processing

```java
/**
 * SDE-Data scenario: Different data processors with different capabilities
 */

// ❌ WRONG: Fat interface
public interface DataProcessor {
    void read(String source);
    void transform();
    void validate();
    void aggregate();
    void write(String destination);
    void sendMetrics();
    void sendAlerts();
}

public class SimpleFileProcessor implements DataProcessor {
    @Override
    public void read(String source) { /* Read file */ }
    
    @Override
    public void transform() { /* Transform data */ }
    
    @Override
    public void validate() {
        throw new UnsupportedOperationException("No validation"); // ❌
    }
    
    @Override
    public void aggregate() {
        throw new UnsupportedOperationException("No aggregation"); // ❌
    }
    
    @Override
    public void write(String destination) { /* Write file */ }
    
    @Override
    public void sendMetrics() {
        throw new UnsupportedOperationException("No metrics"); // ❌
    }
    
    @Override
    public void sendAlerts() {
        throw new UnsupportedOperationException("No alerts"); // ❌
    }
}

// ✅ CORRECT: Segregated interfaces
public interface DataReader {
    void read(String source);
}

public interface DataTransformer {
    void transform();
}

public interface DataValidator {
    void validate();
}

public interface DataAggregator {
    void aggregate();
}

public interface DataWriter {
    void write(String destination);
}

public interface MetricsPublisher {
    void sendMetrics();
}

public interface AlertPublisher {
    void sendAlerts();
}

// Simple processor: Only reads and writes
public class SimpleFileProcessor implements DataReader, DataWriter {
    private List<String> data;
    
    @Override
    public void read(String source) {
        try {
            data = Files.readAllLines(Paths.get(source));
        } catch (IOException e) {
            throw new RuntimeException("Failed to read file", e);
        }
    }
    
    @Override
    public void write(String destination) {
        try {
            Files.write(Paths.get(destination), data);
        } catch (IOException e) {
            throw new RuntimeException("Failed to write file", e);
        }
    }
}

// Complex processor: Full-featured
public class ComplexDataProcessor implements 
    DataReader, DataTransformer, DataValidator, DataAggregator, 
    DataWriter, MetricsPublisher, AlertPublisher {
    
    private List<Record> data;
    private final CloudWatch cloudWatch;
    private final SlackClient slackClient;
    
    public ComplexDataProcessor(CloudWatch cloudWatch, SlackClient slackClient) {
        this.cloudWatch = cloudWatch;
        this.slackClient = slackClient;
    }
    
    @Override
    public void read(String source) {
        // Read from S3/Kafka/etc.
    }
    
    @Override
    public void transform() {
        // Apply transformations
        data = data.stream()
            .map(this::applyTransformations)
            .collect(Collectors.toList());
    }
    
    @Override
    public void validate() {
        // Validate data quality
        long invalidRecords = data.stream()
            .filter(record -> !record.isValid())
            .count();
        
        if (invalidRecords > data.size() * 0.1) {
            throw new IllegalStateException("Too many invalid records: " + invalidRecords);
        }
    }
    
    @Override
    public void aggregate() {
        // Aggregate by key
    }
    
    @Override
    public void write(String destination) {
        // Write to Redshift/S3/etc.
    }
    
    @Override
    public void sendMetrics() {
        cloudWatch.putMetricData("RecordsProcessed", data.size());
    }
    
    @Override
    public void sendAlerts() {
        if (data.size() < 1000) {
            slackClient.send("Low data volume: " + data.size());
        }
    }
    
    private Record applyTransformations(Record record) {
        // Transformation logic
        return record;
    }
}

// Pipeline can use only what it needs
public class DataPipeline {
    public void simpleETL(DataReader reader, DataWriter writer, String source, String dest) {
        reader.read(source);
        writer.write(dest);
    }
    
    public void complexETL(
        DataReader reader,
        DataTransformer transformer,
        DataValidator validator,
        DataWriter writer,
        MetricsPublisher metricsPublisher,
        String source,
        String dest
    ) {
        reader.read(source);
        transformer.transform();
        validator.validate();
        writer.write(dest);
        metricsPublisher.sendMetrics();
    }
}
```

---

## 5. Dependency Inversion Principle (DIP)

### Definition

> **1. High-level modules should not depend on low-level modules. Both should depend on abstractions.**
> **2. Abstractions should not depend on details. Details should depend on abstractions.**
> — Robert C. Martin

**Simplified:** Depend on interfaces, not concrete classes. Program to interfaces!

### Why DIP Matters

```
Without DIP:
├─ High-level classes tightly coupled to low-level classes
├─ Hard to test (can't mock dependencies)
├─ Hard to change (ripple effect)
└─ Hard to reuse (drag all dependencies)

With DIP:
├─ Loose coupling (depend on interfaces)
├─ Easy to test (mock interfaces)
├─ Easy to change (swap implementations)
└─ Easy to reuse (minimal dependencies)
```

### ❌ Violation Example: Tight Coupling

```java
/**
 * WRONG: High-level class depends on low-level class
 */
public class MySQLDatabase {
    public void save(String data) {
        System.out.println("Saving to MySQL: " + data);
        // MySQL-specific code
    }
}

public class OrderService {
    private final MySQLDatabase database;  // ❌ Depends on concrete class
    
    public OrderService() {
        this.database = new MySQLDatabase();  // ❌ Creates dependency
    }
    
    public void createOrder(String orderData) {
        // Business logic
        database.save(orderData);
    }
}

/**
 * Problems:
 * 1. OrderService tightly coupled to MySQLDatabase
 * 2. Can't swap MySQL → PostgreSQL without modifying OrderService
 * 3. Can't test OrderService without real MySQL database
 * 4. Violates DIP
 */
```

### ✅ Correct Example: Dependency Injection

```java
/**
 * CORRECT: Depend on abstraction
 */

// Abstraction (interface)
public interface Database {
    void save(String data);
    String load(String id);
}

// Low-level module (implementation)
public class MySQLDatabase implements Database {
    private final Connection connection;
    
    public MySQLDatabase(Connection connection) {
        this.connection = connection;
    }
    
    @Override
    public void save(String data) {
        try (PreparedStatement stmt = connection.prepareStatement(
            "INSERT INTO orders (data) VALUES (?)"
        )) {
            stmt.setString(1, data);
            stmt.executeUpdate();
        } catch (SQLException e) {
            throw new RuntimeException("Failed to save", e);
        }
    }
    
    @Override
    public String load(String id) {
        // Implementation
        return null;
    }
}

public class PostgreSQLDatabase implements Database {
    private final Connection connection;
    
    public PostgreSQLDatabase(Connection connection) {
        this.connection = connection;
    }
    
    @Override
    public void save(String data) {
        // PostgreSQL-specific implementation
    }
    
    @Override
    public String load(String id) {
        // Implementation
        return null;
    }
}

// High-level module (depends on abstraction)
public class OrderService {
    private final Database database;  // ✅ Depends on interface
    
    public OrderService(Database database) {  // ✅ Dependency injection
        this.database = database;
    }
    
    public void createOrder(String orderData) {
        // Business logic
        validateOrder(orderData);
        database.save(orderData);
    }
    
    private void validateOrder(String orderData) {
        // Validation logic
    }
}

// Usage (dependency injection)
public class Main {
    public static void main(String[] args) {
        // Production: Use MySQL
        Database mysqlDb = new MySQLDatabase(getMySQLConnection());
        OrderService orderService = new OrderService(mysqlDb);
        orderService.createOrder("order-123");
        
        // Switch to PostgreSQL? Just change one line!
        Database postgresDb = new PostgreSQLDatabase(getPostgreSQLConnection());
        OrderService orderService2 = new OrderService(postgresDb);
        orderService2.createOrder("order-456");
    }
}

// Testing (mock database)
public class OrderServiceTest {
    @Test
    public void testCreateOrder() {
        // Mock database (no real database needed!)
        Database mockDatabase = new MockDatabase();
        OrderService orderService = new OrderService(mockDatabase);
        
        orderService.createOrder("test-order");
        
        assertTrue(mockDatabase.wasSaveCalled());
    }
    
    private static class MockDatabase implements Database {
        private boolean saveCalled = false;
        
        @Override
        public void save(String data) {
            saveCalled = true;
        }
        
        @Override
        public String load(String id) {
            return null;
        }
        
        public boolean wasSaveCalled() {
            return saveCalled;
        }
    }
}
```

### Real-World Example: Data Pipeline with DIP

```java
/**
 * SDE-Data scenario: Data pipeline with pluggable components
 */

// ❌ WRONG: Tight coupling
public class DataPipeline {
    private final S3Client s3Client;
    private final RedshiftClient redshiftClient;
    private final CloudWatchClient cloudWatchClient;
    
    public DataPipeline() {
        // ❌ Creating dependencies inside class
        this.s3Client = S3Client.builder().build();
        this.redshiftClient = RedshiftClient.builder().build();
        this.cloudWatchClient = CloudWatchClient.builder().build();
    }
    
    public void run() {
        // Extract from S3
        String data = s3Client.getObject(/* ... */);
        
        // Load to Redshift
        redshiftClient.executeStatement(/* ... */);
        
        // Send metrics
        cloudWatchClient.putMetricData(/* ... */);
    }
    
    // Can't test without real AWS services! ❌
    // Can't swap S3 → Kafka without modifying class! ❌
}

// ✅ CORRECT: Dependency inversion
public interface DataSource {
    List<Record> extract();
}

public interface DataSink {
    void load(List<Record> records);
}

public interface MetricsPublisher {
    void publish(String metric, double value);
}

// Implementations
public class S3DataSource implements DataSource {
    private final S3Client s3Client;
    private final String bucket;
    private final String key;
    
    public S3DataSource(S3Client s3Client, String bucket, String key) {
        this.s3Client = s3Client;
        this.bucket = bucket;
        this.key = key;
    }
    
    @Override
    public List<Record> extract() {
        GetObjectResponse response = s3Client.getObject(
            GetObjectRequest.builder()
                .bucket(bucket)
                .key(key)
                .build()
        );
        
        // Parse and return records
        return parseRecords(response);
    }
    
    private List<Record> parseRecords(GetObjectResponse response) {
        // Parsing logic
        return new ArrayList<>();
    }
}

public class KafkaDataSource implements DataSource {
    private final KafkaConsumer<String, String> consumer;
    private final String topic;
    
    public KafkaDataSource(KafkaConsumer<String, String> consumer, String topic) {
        this.consumer = consumer;
        this.topic = topic;
    }
    
    @Override
    public List<Record> extract() {
        consumer.subscribe(Collections.singletonList(topic));
        
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofSeconds(10));
        List<Record> result = new ArrayList<>();
        
        for (ConsumerRecord<String, String> record : records) {
            result.add(new Record(record.key(), record.value()));
        }
        
        return result;
    }
}

public class RedshiftDataSink implements DataSink {
    private final Connection connection;
    
    public RedshiftDataSink(Connection connection) {
        this.connection = connection;
    }
    
    @Override
    public void load(List<Record> records) {
        try (PreparedStatement stmt = connection.prepareStatement(
            "INSERT INTO records (id, value) VALUES (?, ?)"
        )) {
            connection.setAutoCommit(false);
            
            for (Record record : records) {
                stmt.setString(1, record.getId());
                stmt.setString(2, record.getValue());
                stmt.addBatch();
            }
            
            stmt.executeBatch();
            connection.commit();
        } catch (SQLException e) {
            try {
                connection.rollback();
            } catch (SQLException rollbackEx) {
                // Log error
            }
            throw new RuntimeException("Failed to load to Redshift", e);
        }
    }
}

public class CloudWatchMetricsPublisher implements MetricsPublisher {
    private final CloudWatchClient cloudWatchClient;
    private final String namespace;
    
    public CloudWatchMetricsPublisher(CloudWatchClient cloudWatchClient, String namespace) {
        this.cloudWatchClient = cloudWatchClient;
        this.namespace = namespace;
    }
    
    @Override
    public void publish(String metric, double value) {
        cloudWatchClient.putMetricData(
            PutMetricDataRequest.builder()
                .namespace(namespace)
                .metricData(MetricDatum.builder()
                    .metricName(metric)
                    .value(value)
                    .timestamp(Instant.now())
                    .build())
                .build()
        );
    }
}

// High-level pipeline (depends on abstractions)
public class DataPipeline {
    private final DataSource dataSource;
    private final DataSink dataSink;
    private final MetricsPublisher metricsPublisher;
    
    public DataPipeline(
        DataSource dataSource,
        DataSink dataSink,
        MetricsPublisher metricsPublisher
    ) {
        this.dataSource = dataSource;
        this.dataSink = dataSink;
        this.metricsPublisher = metricsPublisher;
    }
    
    public void run() {
        // Extract
        List<Record> records = dataSource.extract();
        
        // Transform (if needed)
        List<Record> transformed = transform(records);
        
        // Load
        dataSink.load(transformed);
        
        // Publish metrics
        metricsPublisher.publish("RecordsProcessed", transformed.size());
    }
    
    private List<Record> transform(List<Record> records) {
        // Transformation logic
        return records.stream()
            .filter(Record::isValid)
            .collect(Collectors.toList());
    }
}

// Production configuration
public class ProductionConfig {
    public static DataPipeline createPipeline() {
        // S3 → Redshift pipeline
        DataSource s3Source = new S3DataSource(
            S3Client.builder().build(),
            "my-bucket",
            "data.csv"
        );
        
        DataSink redshiftSink = new RedshiftDataSink(
            getRedshiftConnection()
        );
        
        MetricsPublisher cloudWatch = new CloudWatchMetricsPublisher(
            CloudWatchClient.builder().build(),
            "DataPipeline"
        );
        
        return new DataPipeline(s3Source, redshiftSink, cloudWatch);
    }
    
    private static Connection getRedshiftConnection() {
        // Get connection
        return null;
    }
}

// Test configuration (mocks)
public class DataPipelineTest {
    @Test
    public void testPipeline() {
        // Mock dependencies
        DataSource mockSource = new MockDataSource();
        DataSink mockSink = new MockDataSink();
        MetricsPublisher mockMetrics = new MockMetricsPublisher();
        
        DataPipeline pipeline = new DataPipeline(mockSource, mockSink, mockMetrics);
        pipeline.run();
        
        // Verify
        assertTrue(((MockDataSink) mockSink).wasLoadCalled());
        assertTrue(((MockMetricsPublisher) mockMetrics).wasPublishCalled());
    }
    
    private static class MockDataSource implements DataSource {
        @Override
        public List<Record> extract() {
            return Arrays.asList(
                new Record("1", "test1"),
                new Record("2", "test2")
            );
        }
    }
    
    private static class MockDataSink implements DataSink {
        private boolean loadCalled = false;
        
        @Override
        public void load(List<Record> records) {
            loadCalled = true;
        }
        
        public boolean wasLoadCalled() {
            return loadCalled;
        }
    }
    
    private static class MockMetricsPublisher implements MetricsPublisher {
        private boolean publishCalled = false;
        
        @Override
        public void publish(String metric, double value) {
            publishCalled = true;
        }
        
        public boolean wasPublishCalled() {
            return publishCalled;
        }
    }
}

/**
 * Benefits:
 * 1. Easy to swap S3 → Kafka (just change DataSource implementation)
 * 2. Easy to swap Redshift → Snowflake (just change DataSink implementation)
 * 3. Easy to test (mock all dependencies)
 * 4. Loose coupling (DataPipeline doesn't know about AWS)
 * 5. Follows DIP ✅
 */
```

---

## 🎯 Key Takeaways

1. **SRP:** One class, one responsibility, one reason to change
2. **OCP:** Extend via new code, not modifying existing code (use polymorphism)
3. **LSP:** Subclasses must be substitutable for parent classes (no surprises)
4. **ISP:** Many small interfaces > one fat interface (clients use what they need)
5. **DIP:** Depend on abstractions, not concrete classes (enables testing & flexibility)

**For 40 LPA SDE-Data role:**
- Design data pipelines with SOLID principles
- Use interfaces for pluggable components (sources, sinks, transformers)
- Write testable code (DIP enables mocking)
- Design extensible systems (OCP for new data formats, sources)

---

## 📚 Further Reading

- **Clean Architecture** by Robert C. Martin
- **Design Patterns: Elements of Reusable Object-Oriented Software** by Gang of Four
- **Effective Java** by Joshua Bloch

---

**Next:** [INTERMEDIATE.md](../02-DESIGN-PATTERNS/INTERMEDIATE.md) — Design Patterns (Creational, Structural, Behavioral)
