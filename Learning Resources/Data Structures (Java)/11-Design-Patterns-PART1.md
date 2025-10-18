# Design Patterns - Part 1

**Purpose:** Master Gang of Four (GoF) design patterns for 40+ LPA Principal Engineer roles

**Prerequisites:** OOP fundamentals, SOLID principles, Java 8+ features

---

## Table of Contents

**Part 1 (this file):**
1. [Creational Patterns](#1-creational-patterns)
   - Factory Method
   - Abstract Factory
   - Builder
   - Singleton
   - Prototype

**Part 2 (11-Design-Patterns-PART2.md):**
2. Structural Patterns
3. Behavioral Patterns
4. Production Examples & Anti-patterns

---

## 1. Creational Patterns

**Purpose:** Object creation mechanisms that increase flexibility and reuse

### 1.1 Factory Method Pattern

**Problem:** Need to create objects without specifying exact classes

**Intent:** Create objects through a common interface, letting subclasses decide which class to instantiate

**Structure:**
```java
// Product interface
public interface Payment {
    void processPayment(double amount);
    PaymentResult getResult();
}

// Concrete products
public class CreditCardPayment implements Payment {
    private String cardNumber;
    private String cvv;
    
    public CreditCardPayment(String cardNumber, String cvv) {
        this.cardNumber = cardNumber;
        this.cvv = cvv;
    }
    
    @Override
    public void processPayment(double amount) {
        // Integrate with Stripe/Square
        System.out.println("Processing $" + amount + " via Credit Card");
        // Validate card, charge amount
    }
    
    @Override
    public PaymentResult getResult() {
        return new PaymentResult("SUCCESS", "Transaction ID: " + UUID.randomUUID());
    }
}

public class PayPalPayment implements Payment {
    private String email;
    private String token;
    
    public PayPalPayment(String email, String token) {
        this.email = email;
        this.token = token;
    }
    
    @Override
    public void processPayment(double amount) {
        System.out.println("Processing $" + amount + " via PayPal");
        // PayPal API integration
    }
    
    @Override
    public PaymentResult getResult() {
        return new PaymentResult("SUCCESS", "PayPal Transaction: " + UUID.randomUUID());
    }
}

public class BitcoinPayment implements Payment {
    private String walletAddress;
    
    public BitcoinPayment(String walletAddress) {
        this.walletAddress = walletAddress;
    }
    
    @Override
    public void processPayment(double amount) {
        System.out.println("Processing $" + amount + " via Bitcoin");
        // Blockchain transaction
    }
    
    @Override
    public PaymentResult getResult() {
        return new PaymentResult("PENDING", "Bitcoin TX: " + UUID.randomUUID());
    }
}

// Creator abstract class
public abstract class PaymentFactory {
    // Factory method - subclasses implement
    protected abstract Payment createPayment(Map<String, String> params);
    
    // Template method using factory method
    public PaymentResult processPayment(double amount, Map<String, String> params) {
        Payment payment = createPayment(params);
        payment.processPayment(amount);
        return payment.getResult();
    }
}

// Concrete creators
public class CreditCardFactory extends PaymentFactory {
    @Override
    protected Payment createPayment(Map<String, String> params) {
        return new CreditCardPayment(
            params.get("cardNumber"), 
            params.get("cvv")
        );
    }
}

public class PayPalFactory extends PaymentFactory {
    @Override
    protected Payment createPayment(Map<String, String> params) {
        return new PayPalPayment(
            params.get("email"), 
            params.get("token")
        );
    }
}

public class BitcoinFactory extends PaymentFactory {
    @Override
    protected Payment createPayment(Map<String, String> params) {
        return new BitcoinPayment(params.get("walletAddress"));
    }
}
```

**Usage:**
```java
public class PaymentProcessor {
    private Map<String, PaymentFactory> factories;
    
    public PaymentProcessor() {
        factories = Map.of(
            "CREDIT_CARD", new CreditCardFactory(),
            "PAYPAL", new PayPalFactory(),
            "BITCOIN", new BitcoinFactory()
        );
    }
    
    public PaymentResult processPayment(String type, double amount, Map<String, String> params) {
        PaymentFactory factory = factories.get(type);
        if (factory == null) {
            throw new UnsupportedOperationException("Payment type not supported: " + type);
        }
        return factory.processPayment(amount, params);
    }
}

// Client code
PaymentProcessor processor = new PaymentProcessor();

// Credit card payment
Map<String, String> cardParams = Map.of(
    "cardNumber", "4111-1111-1111-1111",
    "cvv", "123"
);
PaymentResult result1 = processor.processPayment("CREDIT_CARD", 99.99, cardParams);

// PayPal payment
Map<String, String> paypalParams = Map.of(
    "email", "user@example.com",
    "token", "paypal_token_123"
);
PaymentResult result2 = processor.processPayment("PAYPAL", 149.99, paypalParams);
```

**Benefits:**
- Open/Closed Principle: Add new payment methods without changing existing code
- Single Responsibility: Each factory creates one type of payment
- Encapsulation: Client doesn't know concrete payment classes

**Real-world Examples:**
- **Spring Framework:** `BeanFactory.getBean()` creates different bean types
- **JDBC:** `DriverManager.getConnection()` returns database-specific connections
- **Collections:** `List.of()`, `Set.of()` create different implementations

---

### 1.2 Abstract Factory Pattern

**Problem:** Create families of related objects without specifying concrete classes

**Intent:** Provide interface for creating families of related/dependent objects

**Example: UI Components for Different Operating Systems**

```java
// Abstract products
public interface Button {
    void render();
    void onClick(Runnable action);
}

public interface Checkbox {
    void render();
    void setChecked(boolean checked);
    boolean isChecked();
}

public interface Dialog {
    void show();
    void close();
}

// Windows family
public class WindowsButton implements Button {
    @Override
    public void render() {
        System.out.println("Rendering Windows-style button with blue background");
    }
    
    @Override
    public void onClick(Runnable action) {
        System.out.println("Windows button clicked");
        action.run();
    }
}

public class WindowsCheckbox implements Checkbox {
    private boolean checked = false;
    
    @Override
    public void render() {
        System.out.println("Rendering Windows checkbox with square shape");
    }
    
    @Override
    public void setChecked(boolean checked) {
        this.checked = checked;
        System.out.println("Windows checkbox " + (checked ? "checked" : "unchecked"));
    }
    
    @Override
    public boolean isChecked() {
        return checked;
    }
}

public class WindowsDialog implements Dialog {
    @Override
    public void show() {
        System.out.println("Showing Windows dialog with title bar and minimize/maximize buttons");
    }
    
    @Override
    public void close() {
        System.out.println("Closing Windows dialog");
    }
}

// macOS family
public class MacButton implements Button {
    @Override
    public void render() {
        System.out.println("Rendering macOS-style button with rounded corners");
    }
    
    @Override
    public void onClick(Runnable action) {
        System.out.println("macOS button clicked");
        action.run();
    }
}

public class MacCheckbox implements Checkbox {
    private boolean checked = false;
    
    @Override
    public void render() {
        System.out.println("Rendering macOS checkbox with rounded square");
    }
    
    @Override
    public void setChecked(boolean checked) {
        this.checked = checked;
        System.out.println("macOS checkbox " + (checked ? "✓" : "☐"));
    }
    
    @Override
    public boolean isChecked() {
        return checked;
    }
}

public class MacDialog implements Dialog {
    @Override
    public void show() {
        System.out.println("Showing macOS dialog with close/minimize/maximize traffic lights");
    }
    
    @Override
    public void close() {
        System.out.println("Closing macOS dialog");
    }
}

// Linux family
public class LinuxButton implements Button {
    @Override
    public void render() {
        System.out.println("Rendering Linux button with GTK theme");
    }
    
    @Override
    public void onClick(Runnable action) {
        System.out.println("Linux button clicked");
        action.run();
    }
}

public class LinuxCheckbox implements Checkbox {
    private boolean checked = false;
    
    @Override
    public void render() {
        System.out.println("Rendering Linux checkbox with custom theme");
    }
    
    @Override
    public void setChecked(boolean checked) {
        this.checked = checked;
        System.out.println("Linux checkbox " + (checked ? "[x]" : "[ ]"));
    }
    
    @Override
    public boolean isChecked() {
        return checked;
    }
}

public class LinuxDialog implements Dialog {
    @Override
    public void show() {
        System.out.println("Showing Linux dialog with window manager decorations");
    }
    
    @Override
    public void close() {
        System.out.println("Closing Linux dialog");
    }
}

// Abstract factory
public interface UIFactory {
    Button createButton();
    Checkbox createCheckbox();
    Dialog createDialog();
}

// Concrete factories
public class WindowsUIFactory implements UIFactory {
    @Override
    public Button createButton() {
        return new WindowsButton();
    }
    
    @Override
    public Checkbox createCheckbox() {
        return new WindowsCheckbox();
    }
    
    @Override
    public Dialog createDialog() {
        return new WindowsDialog();
    }
}

public class MacUIFactory implements UIFactory {
    @Override
    public Button createButton() {
        return new MacButton();
    }
    
    @Override
    public Checkbox createCheckbox() {
        return new MacCheckbox();
    }
    
    @Override
    public Dialog createDialog() {
        return new MacDialog();
    }
}

public class LinuxUIFactory implements UIFactory {
    @Override
    public Button createButton() {
        return new LinuxButton();
    }
    
    @Override
    public Checkbox createCheckbox() {
        return new LinuxCheckbox();
    }
    
    @Override
    public Dialog createDialog() {
        return new LinuxDialog();
    }
}
```

**Application using Abstract Factory:**
```java
public class Application {
    private UIFactory uiFactory;
    private Button button;
    private Checkbox checkbox;
    private Dialog dialog;
    
    public Application(UIFactory factory) {
        this.uiFactory = factory;
        createUI();
    }
    
    private void createUI() {
        button = uiFactory.createButton();
        checkbox = uiFactory.createCheckbox();
        dialog = uiFactory.createDialog();
    }
    
    public void render() {
        button.render();
        checkbox.render();
        dialog.show();
        
        // Setup interactions
        button.onClick(() -> {
            checkbox.setChecked(!checkbox.isChecked());
        });
    }
}

// Factory provider based on OS
public class UIFactoryProvider {
    public static UIFactory getFactory() {
        String os = System.getProperty("os.name").toLowerCase();
        
        if (os.contains("win")) {
            return new WindowsUIFactory();
        } else if (os.contains("mac")) {
            return new MacUIFactory();
        } else {
            return new LinuxUIFactory();
        }
    }
}

// Client code
public class Main {
    public static void main(String[] args) {
        UIFactory factory = UIFactoryProvider.getFactory();
        Application app = new Application(factory);
        app.render();
    }
}
```

**Benefits:**
- **Consistency:** Ensures all UI components belong to same family
- **Isolation:** Concrete classes isolated from client code
- **Easy switching:** Change entire product family by changing factory

**Real-world Examples:**
- **Java Swing:** `UIManager.setLookAndFeel()` changes entire UI theme
- **Database drivers:** JDBC factories create connections, statements, result sets for specific DB
- **Game engines:** Different renderers (DirectX, OpenGL, Vulkan) with their own texture/shader factories

---

### 1.3 Builder Pattern

**Problem:** Constructing complex objects step by step

**Intent:** Separate construction of complex object from its representation

**Example: SQL Query Builder**

```java
public class SqlQuery {
    private final String table;
    private final List<String> selectColumns;
    private final List<String> whereConditions;
    private final List<String> joinClauses;
    private final List<String> orderByColumns;
    private final List<String> groupByColumns;
    private final String havingCondition;
    private final Integer limit;
    private final Integer offset;
    
    // Private constructor - only builder can create
    private SqlQuery(Builder builder) {
        this.table = builder.table;
        this.selectColumns = List.copyOf(builder.selectColumns);
        this.whereConditions = List.copyOf(builder.whereConditions);
        this.joinClauses = List.copyOf(builder.joinClauses);
        this.orderByColumns = List.copyOf(builder.orderByColumns);
        this.groupByColumns = List.copyOf(builder.groupByColumns);
        this.havingCondition = builder.havingCondition;
        this.limit = builder.limit;
        this.offset = builder.offset;
    }
    
    public String toSql() {
        StringBuilder sql = new StringBuilder();
        
        // SELECT clause
        sql.append("SELECT ");
        if (selectColumns.isEmpty()) {
            sql.append("*");
        } else {
            sql.append(String.join(", ", selectColumns));
        }
        
        // FROM clause
        sql.append(" FROM ").append(table);
        
        // JOIN clauses
        for (String join : joinClauses) {
            sql.append(" ").append(join);
        }
        
        // WHERE clause
        if (!whereConditions.isEmpty()) {
            sql.append(" WHERE ").append(String.join(" AND ", whereConditions));
        }
        
        // GROUP BY clause
        if (!groupByColumns.isEmpty()) {
            sql.append(" GROUP BY ").append(String.join(", ", groupByColumns));
        }
        
        // HAVING clause
        if (havingCondition != null) {
            sql.append(" HAVING ").append(havingCondition);
        }
        
        // ORDER BY clause
        if (!orderByColumns.isEmpty()) {
            sql.append(" ORDER BY ").append(String.join(", ", orderByColumns));
        }
        
        // LIMIT clause
        if (limit != null) {
            sql.append(" LIMIT ").append(limit);
        }
        
        // OFFSET clause
        if (offset != null) {
            sql.append(" OFFSET ").append(offset);
        }
        
        return sql.toString();
    }
    
    // Builder class
    public static class Builder {
        private String table;
        private List<String> selectColumns = new ArrayList<>();
        private List<String> whereConditions = new ArrayList<>();
        private List<String> joinClauses = new ArrayList<>();
        private List<String> orderByColumns = new ArrayList<>();
        private List<String> groupByColumns = new ArrayList<>();
        private String havingCondition;
        private Integer limit;
        private Integer offset;
        
        public Builder from(String table) {
            this.table = table;
            return this;
        }
        
        public Builder select(String... columns) {
            Collections.addAll(this.selectColumns, columns);
            return this;
        }
        
        public Builder where(String condition) {
            this.whereConditions.add(condition);
            return this;
        }
        
        public Builder whereEquals(String column, Object value) {
            if (value instanceof String) {
                this.whereConditions.add(column + " = '" + value + "'");
            } else {
                this.whereConditions.add(column + " = " + value);
            }
            return this;
        }
        
        public Builder whereIn(String column, List<?> values) {
            String valuesList = values.stream()
                .map(v -> v instanceof String ? "'" + v + "'" : v.toString())
                .collect(Collectors.joining(", "));
            this.whereConditions.add(column + " IN (" + valuesList + ")");
            return this;
        }
        
        public Builder join(String table, String condition) {
            this.joinClauses.add("JOIN " + table + " ON " + condition);
            return this;
        }
        
        public Builder leftJoin(String table, String condition) {
            this.joinClauses.add("LEFT JOIN " + table + " ON " + condition);
            return this;
        }
        
        public Builder innerJoin(String table, String condition) {
            this.joinClauses.add("INNER JOIN " + table + " ON " + condition);
            return this;
        }
        
        public Builder orderBy(String column) {
            this.orderByColumns.add(column);
            return this;
        }
        
        public Builder orderByDesc(String column) {
            this.orderByColumns.add(column + " DESC");
            return this;
        }
        
        public Builder groupBy(String... columns) {
            Collections.addAll(this.groupByColumns, columns);
            return this;
        }
        
        public Builder having(String condition) {
            this.havingCondition = condition;
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
            if (table == null) {
                throw new IllegalStateException("Table name is required");
            }
            return new SqlQuery(this);
        }
    }
    
    // Static method for convenience
    public static Builder builder() {
        return new Builder();
    }
}
```

**Usage Examples:**
```java
public class QueryExamples {
    public void simpleQuery() {
        SqlQuery query = SqlQuery.builder()
            .from("users")
            .select("id", "name", "email")
            .whereEquals("status", "active")
            .orderBy("name")
            .limit(10)
            .build();
        
        System.out.println(query.toSql());
        // SELECT id, name, email FROM users WHERE status = 'active' ORDER BY name LIMIT 10
    }
    
    public void complexQuery() {
        SqlQuery query = SqlQuery.builder()
            .from("users u")
            .select("u.name", "p.title", "COUNT(o.id) as order_count")
            .leftJoin("profiles p", "u.id = p.user_id")
            .innerJoin("orders o", "u.id = o.user_id")
            .where("u.created_at > '2023-01-01'")
            .whereIn("u.status", List.of("active", "premium"))
            .groupBy("u.id", "u.name", "p.title")
            .having("COUNT(o.id) > 5")
            .orderByDesc("order_count")
            .limit(20)
            .offset(40)
            .build();
        
        System.out.println(query.toSql());
        // Complex query with joins, grouping, having, etc.
    }
    
    public void conditionalQuery(String userRole, String department) {
        SqlQuery.Builder builder = SqlQuery.builder()
            .from("employees")
            .select("name", "salary", "department");
        
        // Conditional building
        if ("admin".equals(userRole)) {
            builder.select("ssn", "performance_rating");
        }
        
        if (department != null) {
            builder.whereEquals("department", department);
        }
        
        SqlQuery query = builder
            .orderBy("salary DESC")
            .build();
        
        System.out.println(query.toSql());
    }
}
```

**HTTP Request Builder Example:**
```java
public class HttpRequest {
    private final String url;
    private final String method;
    private final Map<String, String> headers;
    private final Map<String, String> queryParams;
    private final String body;
    private final int timeout;
    
    private HttpRequest(Builder builder) {
        this.url = builder.url;
        this.method = builder.method;
        this.headers = Map.copyOf(builder.headers);
        this.queryParams = Map.copyOf(builder.queryParams);
        this.body = builder.body;
        this.timeout = builder.timeout;
    }
    
    public static class Builder {
        private String url;
        private String method = "GET";
        private Map<String, String> headers = new HashMap<>();
        private Map<String, String> queryParams = new HashMap<>();
        private String body;
        private int timeout = 30000; // 30 seconds default
        
        public Builder url(String url) {
            this.url = url;
            return this;
        }
        
        public Builder get() {
            this.method = "GET";
            return this;
        }
        
        public Builder post() {
            this.method = "POST";
            return this;
        }
        
        public Builder put() {
            this.method = "PUT";
            return this;
        }
        
        public Builder delete() {
            this.method = "DELETE";
            return this;
        }
        
        public Builder header(String key, String value) {
            this.headers.put(key, value);
            return this;
        }
        
        public Builder bearerAuth(String token) {
            this.headers.put("Authorization", "Bearer " + token);
            return this;
        }
        
        public Builder contentType(String contentType) {
            this.headers.put("Content-Type", contentType);
            return this;
        }
        
        public Builder json() {
            return contentType("application/json");
        }
        
        public Builder queryParam(String key, String value) {
            this.queryParams.put(key, value);
            return this;
        }
        
        public Builder body(String body) {
            this.body = body;
            return this;
        }
        
        public Builder jsonBody(Object obj) {
            // In real implementation, use Jackson/Gson
            this.body = "JSON representation of " + obj.toString();
            return json();
        }
        
        public Builder timeout(int timeoutMs) {
            this.timeout = timeoutMs;
            return this;
        }
        
        public HttpRequest build() {
            if (url == null) {
                throw new IllegalStateException("URL is required");
            }
            return new HttpRequest(this);
        }
    }
    
    public static Builder builder() {
        return new Builder();
    }
    
    // Execute the request
    public HttpResponse execute() {
        String fullUrl = buildFullUrl();
        System.out.println("Executing " + method + " request to: " + fullUrl);
        System.out.println("Headers: " + headers);
        if (body != null) {
            System.out.println("Body: " + body);
        }
        
        // In real implementation, use HttpClient
        return new HttpResponse(200, "Mock response");
    }
    
    private String buildFullUrl() {
        if (queryParams.isEmpty()) {
            return url;
        }
        
        String queryString = queryParams.entrySet().stream()
            .map(entry -> entry.getKey() + "=" + entry.getValue())
            .collect(Collectors.joining("&"));
        
        return url + "?" + queryString;
    }
}

// Usage
HttpRequest request = HttpRequest.builder()
    .url("https://api.example.com/users")
    .post()
    .bearerAuth("jwt_token_here")
    .json()
    .queryParam("page", "1")
    .queryParam("limit", "50")
    .jsonBody(new User("John", "john@example.com"))
    .timeout(5000)
    .build();

HttpResponse response = request.execute();
```

**Benefits:**
- **Fluent interface:** Easy to read and write
- **Immutable objects:** Thread-safe once built
- **Validation:** Check required fields in `build()`
- **Flexibility:** Add optional parameters without many constructors

**Real-world Examples:**
- **StringBuilder:** Builds strings incrementally
- **Stream API:** `stream().filter().map().collect()` is builder pattern
- **OkHttp:** `Request.Builder` for HTTP requests
- **Maven/Gradle:** Build scripts are builder pattern
- **Lombok @Builder:** Generates builder pattern automatically

---

### 1.4 Singleton Pattern

**Problem:** Ensure only one instance of a class exists

**Intent:** Guarantee single instance and provide global access point

**Thread-Safe Implementations:**

**1. Enum Singleton (Best Practice):**
```java
public enum DatabaseConnection {
    INSTANCE;
    
    private Connection connection;
    
    DatabaseConnection() {
        // Initialize connection
        try {
            this.connection = DriverManager.getConnection(
                "jdbc:postgresql://localhost:5432/mydb", 
                "username", 
                "password"
            );
            System.out.println("Database connection initialized");
        } catch (SQLException e) {
            throw new RuntimeException("Failed to connect to database", e);
        }
    }
    
    public Connection getConnection() {
        return connection;
    }
    
    public void executeQuery(String sql) {
        try (Statement stmt = connection.createStatement()) {
            ResultSet rs = stmt.executeQuery(sql);
            // Process results
        } catch (SQLException e) {
            throw new RuntimeException("Query execution failed", e);
        }
    }
    
    public void close() {
        try {
            if (connection != null && !connection.isClosed()) {
                connection.close();
                System.out.println("Database connection closed");
            }
        } catch (SQLException e) {
            System.err.println("Error closing connection: " + e.getMessage());
        }
    }
}

// Usage
DatabaseConnection.INSTANCE.executeQuery("SELECT * FROM users");
DatabaseConnection.INSTANCE.close();
```

**2. Lazy Initialization with Double-Checked Locking:**
```java
public class ConfigurationManager {
    private static volatile ConfigurationManager instance;
    private final Properties properties;
    private final String configFile;
    
    private ConfigurationManager() {
        this.configFile = "application.properties";
        this.properties = new Properties();
        loadConfiguration();
    }
    
    public static ConfigurationManager getInstance() {
        if (instance == null) {
            synchronized (ConfigurationManager.class) {
                if (instance == null) {
                    instance = new ConfigurationManager();
                }
            }
        }
        return instance;
    }
    
    private void loadConfiguration() {
        try (InputStream input = getClass().getClassLoader()
                .getResourceAsStream(configFile)) {
            
            if (input == null) {
                System.out.println("Unable to find " + configFile);
                return;
            }
            
            properties.load(input);
            System.out.println("Configuration loaded from " + configFile);
            
        } catch (IOException e) {
            throw new RuntimeException("Failed to load configuration", e);
        }
    }
    
    public String getProperty(String key) {
        return properties.getProperty(key);
    }
    
    public String getProperty(String key, String defaultValue) {
        return properties.getProperty(key, defaultValue);
    }
    
    public int getIntProperty(String key, int defaultValue) {
        String value = properties.getProperty(key);
        try {
            return value != null ? Integer.parseInt(value) : defaultValue;
        } catch (NumberFormatException e) {
            return defaultValue;
        }
    }
    
    public void setProperty(String key, String value) {
        properties.setProperty(key, value);
    }
    
    public void reloadConfiguration() {
        properties.clear();
        loadConfiguration();
    }
}

// Usage
ConfigurationManager config = ConfigurationManager.getInstance();
String dbUrl = config.getProperty("database.url", "jdbc:h2:mem:testdb");
int poolSize = config.getIntProperty("connection.pool.size", 10);
```

**3. Bill Pugh Singleton (Initialization-on-demand):**
```java
public class Logger {
    private final String logLevel;
    private final PrintWriter writer;
    
    private Logger() {
        this.logLevel = System.getProperty("log.level", "INFO");
        try {
            this.writer = new PrintWriter(new FileWriter("application.log", true));
        } catch (IOException e) {
            throw new RuntimeException("Failed to initialize logger", e);
        }
        log("INFO", "Logger initialized with level: " + logLevel);
    }
    
    // Nested class is loaded only when getInstance() is called
    private static class LoggerHolder {
        private static final Logger INSTANCE = new Logger();
    }
    
    public static Logger getInstance() {
        return LoggerHolder.INSTANCE;
    }
    
    public void info(String message) {
        if (shouldLog("INFO")) {
            log("INFO", message);
        }
    }
    
    public void warn(String message) {
        if (shouldLog("WARN")) {
            log("WARN", message);
        }
    }
    
    public void error(String message) {
        if (shouldLog("ERROR")) {
            log("ERROR", message);
        }
    }
    
    public void error(String message, Throwable throwable) {
        if (shouldLog("ERROR")) {
            log("ERROR", message + ": " + throwable.getMessage());
            throwable.printStackTrace(writer);
        }
    }
    
    private void log(String level, String message) {
        String timestamp = Instant.now().toString();
        String logEntry = String.format("[%s] %s: %s", timestamp, level, message);
        
        System.out.println(logEntry);  // Console output
        writer.println(logEntry);      // File output
        writer.flush();
    }
    
    private boolean shouldLog(String level) {
        int currentLevel = getLogLevelValue(logLevel);
        int messageLevel = getLogLevelValue(level);
        return messageLevel >= currentLevel;
    }
    
    private int getLogLevelValue(String level) {
        switch (level) {
            case "DEBUG": return 1;
            case "INFO": return 2;
            case "WARN": return 3;
            case "ERROR": return 4;
            default: return 2; // INFO
        }
    }
    
    public void close() {
        if (writer != null) {
            writer.close();
        }
    }
}

// Usage
Logger logger = Logger.getInstance();
logger.info("Application started");
logger.warn("Low memory warning");
logger.error("Failed to connect to database");
```

**Real-world Examples:**

**Spring Framework Singleton:**
```java
@Component
@Scope("singleton")  // Default scope
public class UserService {
    private final UserRepository userRepository;
    
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
    
    public User findById(Long id) {
        return userRepository.findById(id);
    }
}

// Spring ensures only one instance per application context
```

**Cache Manager Singleton:**
```java
public class CacheManager {
    private static volatile CacheManager instance;
    private final Map<String, Cache> caches;
    private final ScheduledExecutorService cleanupExecutor;
    
    private CacheManager() {
        this.caches = new ConcurrentHashMap<>();
        this.cleanupExecutor = Executors.newSingleThreadScheduledExecutor();
        
        // Schedule cleanup every 5 minutes
        cleanupExecutor.scheduleAtFixedRate(this::cleanup, 5, 5, TimeUnit.MINUTES);
    }
    
    public static CacheManager getInstance() {
        if (instance == null) {
            synchronized (CacheManager.class) {
                if (instance == null) {
                    instance = new CacheManager();
                }
            }
        }
        return instance;
    }
    
    public <T> Cache<T> getCache(String name) {
        return caches.computeIfAbsent(name, k -> new LRUCache<>(1000));
    }
    
    private void cleanup() {
        caches.values().forEach(Cache::evictExpired);
    }
    
    public void shutdown() {
        cleanupExecutor.shutdown();
        try {
            if (!cleanupExecutor.awaitTermination(60, TimeUnit.SECONDS)) {
                cleanupExecutor.shutdownNow();
            }
        } catch (InterruptedException e) {
            cleanupExecutor.shutdownNow();
        }
    }
}
```

**Benefits:**
- **Controlled access:** Global access point to single instance
- **Reduced memory:** Only one instance exists
- **Lazy initialization:** Created only when needed

**Drawbacks:**
- **Global state:** Makes testing difficult
- **Hidden dependencies:** Hard to see what depends on singleton
- **Thread safety:** Need careful synchronization

**When to Use:**
- ✅ **Configuration management:** Application settings
- ✅ **Logging:** Single log instance for entire application
- ✅ **Database connection pools:** Manage connections centrally
- ✅ **Caching:** Single cache manager for all components
- ❌ **Avoid for business logic:** Makes testing and mocking difficult

---

### 1.5 Prototype Pattern

**Problem:** Creating objects is expensive, need to clone existing objects

**Intent:** Create new objects by cloning existing instances rather than constructing from scratch

**Implementation with Cloneable:**

```java
// Base prototype
public abstract class Shape implements Cloneable {
    protected String id;
    protected String type;
    protected int x, y;
    protected String color;
    
    public Shape() {}
    
    public Shape(Shape other) {
        this.id = other.id;
        this.type = other.type;
        this.x = other.x;
        this.y = other.y;
        this.color = other.color;
    }
    
    public abstract void draw();
    public abstract Shape clone();
    
    // Getters and setters
    public void setId(String id) { this.id = id; }
    public String getId() { return id; }
    public void setPosition(int x, int y) { this.x = x; this.y = y; }
    public void setColor(String color) { this.color = color; }
}

// Concrete prototypes
public class Circle extends Shape {
    private int radius;
    private boolean filled;
    
    public Circle() {
        this.type = "Circle";
    }
    
    public Circle(Circle other) {
        super(other);
        this.radius = other.radius;
        this.filled = other.filled;
    }
    
    @Override
    public void draw() {
        System.out.println("Drawing " + color + " circle at (" + x + "," + y + 
                          ") with radius " + radius + (filled ? " (filled)" : " (outline)"));
    }
    
    @Override
    public Shape clone() {
        return new Circle(this);
    }
    
    public void setRadius(int radius) { this.radius = radius; }
    public void setFilled(boolean filled) { this.filled = filled; }
}

public class Rectangle extends Shape {
    private int width, height;
    private String borderStyle;
    
    public Rectangle() {
        this.type = "Rectangle";
    }
    
    public Rectangle(Rectangle other) {
        super(other);
        this.width = other.width;
        this.height = other.height;
        this.borderStyle = other.borderStyle;
    }
    
    @Override
    public void draw() {
        System.out.println("Drawing " + color + " rectangle at (" + x + "," + y + 
                          ") size " + width + "x" + height + " border: " + borderStyle);
    }
    
    @Override
    public Shape clone() {
        return new Rectangle(this);
    }
    
    public void setDimensions(int width, int height) {
        this.width = width;
        this.height = height;
    }
    
    public void setBorderStyle(String borderStyle) { this.borderStyle = borderStyle; }
}

public class Polygon extends Shape {
    private List<Point> points;
    private String fillPattern;
    
    public Polygon() {
        this.type = "Polygon";
        this.points = new ArrayList<>();
    }
    
    public Polygon(Polygon other) {
        super(other);
        // Deep copy of points
        this.points = new ArrayList<>();
        for (Point point : other.points) {
            this.points.add(new Point(point.x, point.y));
        }
        this.fillPattern = other.fillPattern;
    }
    
    @Override
    public void draw() {
        System.out.println("Drawing " + color + " polygon at (" + x + "," + y + 
                          ") with " + points.size() + " points, pattern: " + fillPattern);
    }
    
    @Override
    public Shape clone() {
        return new Polygon(this);
    }
    
    public void addPoint(int x, int y) {
        points.add(new Point(x, y));
    }
    
    public void setFillPattern(String fillPattern) { this.fillPattern = fillPattern; }
    
    private static class Point {
        int x, y;
        Point(int x, int y) { this.x = x; this.y = y; }
    }
}
```

**Prototype Registry:**
```java
public class ShapeRegistry {
    private Map<String, Shape> prototypes = new HashMap<>();
    
    public ShapeRegistry() {
        loadPrototypes();
    }
    
    private void loadPrototypes() {
        // Create default circle prototype
        Circle circle = new Circle();
        circle.setId("default-circle");
        circle.setRadius(10);
        circle.setColor("blue");
        circle.setFilled(false);
        prototypes.put("circle", circle);
        
        // Create default rectangle prototype
        Rectangle rectangle = new Rectangle();
        rectangle.setId("default-rectangle");
        rectangle.setDimensions(20, 15);
        rectangle.setColor("red");
        rectangle.setBorderStyle("solid");
        prototypes.put("rectangle", rectangle);
        
        // Create default polygon prototype
        Polygon polygon = new Polygon();
        polygon.setId("default-triangle");
        polygon.addPoint(0, 0);
        polygon.addPoint(10, 0);
        polygon.addPoint(5, 8);
        polygon.setColor("green");
        polygon.setFillPattern("diagonal-lines");
        prototypes.put("triangle", polygon);
    }
    
    public Shape getShape(String type) {
        Shape prototype = prototypes.get(type);
        if (prototype == null) {
            throw new IllegalArgumentException("Unknown shape type: " + type);
        }
        return prototype.clone();
    }
    
    public void addPrototype(String key, Shape prototype) {
        prototypes.put(key, prototype);
    }
    
    public Set<String> getAvailableTypes() {
        return prototypes.keySet();
    }
}
```

**Usage Example:**
```java
public class DrawingApplication {
    private ShapeRegistry registry;
    private List<Shape> canvas;
    
    public DrawingApplication() {
        this.registry = new ShapeRegistry();
        this.canvas = new ArrayList<>();
    }
    
    public void createShapes() {
        // Create multiple circles with different properties
        Shape circle1 = registry.getShape("circle");
        circle1.setPosition(10, 20);
        circle1.setColor("yellow");
        canvas.add(circle1);
        
        Shape circle2 = registry.getShape("circle");
        circle2.setPosition(50, 60);
        circle2.setColor("purple");
        ((Circle) circle2).setRadius(25);
        ((Circle) circle2).setFilled(true);
        canvas.add(circle2);
        
        // Create rectangles
        Shape rect1 = registry.getShape("rectangle");
        rect1.setPosition(100, 100);
        ((Rectangle) rect1).setDimensions(40, 30);
        ((Rectangle) rect1).setBorderStyle("dashed");
        canvas.add(rect1);
        
        // Create triangles
        Shape triangle1 = registry.getShape("triangle");
        triangle1.setPosition(200, 150);
        triangle1.setColor("orange");
        canvas.add(triangle1);
        
        Shape triangle2 = registry.getShape("triangle");
        triangle2.setPosition(250, 200);
        triangle2.setColor("pink");
        ((Polygon) triangle2).setFillPattern("solid");
        canvas.add(triangle2);
    }
    
    public void drawAll() {
        System.out.println("Drawing canvas with " + canvas.size() + " shapes:");
        for (Shape shape : canvas) {
            shape.draw();
        }
    }
    
    public void addCustomPrototype() {
        // Create a custom hexagon prototype
        Polygon hexagon = new Polygon();
        hexagon.setId("hexagon");
        hexagon.setColor("cyan");
        hexagon.setFillPattern("dots");
        
        // Add hexagon points
        int[] xPoints = {10, 20, 25, 20, 10, 5};
        int[] yPoints = {0, 0, 10, 20, 20, 10};
        for (int i = 0; i < 6; i++) {
            hexagon.addPoint(xPoints[i], yPoints[i]);
        }
        
        registry.addPrototype("hexagon", hexagon);
        
        // Now we can clone hexagons
        Shape hex1 = registry.getShape("hexagon");
        hex1.setPosition(300, 300);
        canvas.add(hex1);
    }
}

// Usage
DrawingApplication app = new DrawingApplication();
app.createShapes();
app.addCustomPrototype();
app.drawAll();
```

**Game Object Prototype Example:**
```java
public abstract class GameUnit implements Cloneable {
    protected String name;
    protected int health, armor, damage;
    protected List<String> abilities;
    protected Equipment equipment;
    
    public GameUnit() {
        this.abilities = new ArrayList<>();
        this.equipment = new Equipment();
    }
    
    public GameUnit(GameUnit other) {
        this.name = other.name;
        this.health = other.health;
        this.armor = other.armor;
        this.damage = other.damage;
        
        // Deep copy abilities
        this.abilities = new ArrayList<>(other.abilities);
        
        // Deep copy equipment
        this.equipment = other.equipment.clone();
    }
    
    public abstract GameUnit clone();
    public abstract void attack(GameUnit target);
    
    // Getters and setters
    public void setStats(int health, int armor, int damage) {
        this.health = health;
        this.armor = armor;
        this.damage = damage;
    }
    
    public void addAbility(String ability) {
        abilities.add(ability);
    }
}

public class Warrior extends GameUnit {
    private String weaponType;
    private int shieldStrength;
    
    public Warrior() {
        super();
        this.name = "Warrior";
        this.weaponType = "sword";
    }
    
    public Warrior(Warrior other) {
        super(other);
        this.weaponType = other.weaponType;
        this.shieldStrength = other.shieldStrength;
    }
    
    @Override
    public GameUnit clone() {
        return new Warrior(this);
    }
    
    @Override
    public void attack(GameUnit target) {
        int finalDamage = damage + equipment.getWeaponDamage();
        System.out.println(name + " attacks with " + weaponType + 
                          " for " + finalDamage + " damage!");
    }
    
    public void setWeaponType(String weaponType) { this.weaponType = weaponType; }
    public void setShieldStrength(int strength) { this.shieldStrength = strength; }
}

public class Mage extends GameUnit {
    private int mana;
    private String school; // fire, ice, lightning
    
    public Mage() {
        super();
        this.name = "Mage";
        this.school = "fire";
    }
    
    public Mage(Mage other) {
        super(other);
        this.mana = other.mana;
        this.school = other.school;
    }
    
    @Override
    public GameUnit clone() {
        return new Mage(this);
    }
    
    @Override
    public void attack(GameUnit target) {
        int spellDamage = damage + equipment.getStaffPower();
        System.out.println(name + " casts " + school + " spell for " + 
                          spellDamage + " magic damage!");
    }
    
    public void setMana(int mana) { this.mana = mana; }
    public void setSchool(String school) { this.school = school; }
}

// Equipment class for deep copying
public class Equipment implements Cloneable {
    private String weapon;
    private String armor;
    private List<String> accessories;
    
    public Equipment() {
        this.accessories = new ArrayList<>();
    }
    
    public Equipment clone() {
        Equipment cloned = new Equipment();
        cloned.weapon = this.weapon;
        cloned.armor = this.armor;
        cloned.accessories = new ArrayList<>(this.accessories);
        return cloned;
    }
    
    public int getWeaponDamage() {
        return weapon != null ? 10 : 0;
    }
    
    public int getStaffPower() {
        return weapon != null ? 15 : 0;
    }
    
    // Setters
    public void setWeapon(String weapon) { this.weapon = weapon; }
    public void setArmor(String armor) { this.armor = armor; }
    public void addAccessory(String accessory) { accessories.add(accessory); }
}
```

**Benefits:**
- **Performance:** Avoid expensive object creation (especially with complex initialization)
- **Dynamic configuration:** Create objects at runtime based on prototypes
- **Reduced subclassing:** Don't need factory class for each product

**Real-world Examples:**
- **Java Object.clone():** Built-in prototype pattern
- **Spring Framework:** `@Scope("prototype")` creates new instance each time
- **Game development:** Unit templates, weapon configurations
- **Document editors:** Copy/paste functionality, style templates

**When to Use:**
- ✅ Object creation is expensive (database queries, network calls, complex calculations)
- ✅ Need many variations of similar objects
- ✅ Runtime object configuration based on user input
- ❌ Simple objects that are cheap to create
- ❌ When inheritance is more appropriate than composition

---

**End of Part 1**

**Continue to Part 2:** 11-Design-Patterns-PART2.md for Structural Patterns, Behavioral Patterns, and Production Anti-patterns.

**Lines so far: ~2,000**