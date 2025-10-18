# OOP & SOLID Principles - Part 2

**Continued from Part 1 (01-OOP-Principles.md)**

---

## 3. Dependency Injection

### 3.1 What is Dependency Injection?

**Definition:** Pass dependencies to a class from outside rather than creating them inside

**Without DI (Bad):**
```java
public class UserService {
    private UserRepository repository = new UserRepository();  // Hard-coded!
    private EmailService emailService = new EmailService();    // Hard-coded!
    
    public void registerUser(User user) {
        repository.save(user);
        emailService.send(user.getEmail(), "Welcome!");
    }
}

// Problems:
// 1. Can't test (can't mock repository or email)
// 2. Tightly coupled (changing implementation requires changing UserService)
// 3. Can't reuse with different implementations
```

**With DI (Good):**
```java
public class UserService {
    private final UserRepository repository;
    private final EmailService emailService;
    
    // Dependencies injected via constructor
    public UserService(UserRepository repository, EmailService emailService) {
        this.repository = repository;
        this.emailService = emailService;
    }
    
    public void registerUser(User user) {
        repository.save(user);
        emailService.send(user.getEmail(), "Welcome!");
    }
}

// Usage
UserRepository repository = new PostgresUserRepository();
EmailService emailService = new SMTPEmailService();
UserService userService = new UserService(repository, emailService);

// Testing (easy to mock)
UserRepository mockRepo = mock(UserRepository.class);
EmailService mockEmail = mock(EmailService.class);
UserService userService = new UserService(mockRepo, mockEmail);
```

---

### 3.2 Types of Dependency Injection

**1. Constructor Injection (Recommended)**
```java
public class OrderService {
    private final PaymentGateway paymentGateway;
    private final InventoryService inventoryService;
    
    public OrderService(PaymentGateway paymentGateway, 
                       InventoryService inventoryService) {
        this.paymentGateway = paymentGateway;
        this.inventoryService = inventoryService;
    }
}

// Benefits:
// - Immutable (final fields)
// - Clear dependencies (visible in constructor)
// - Fail fast (if dependency missing, won't compile)
```

**2. Setter Injection**
```java
public class OrderService {
    private PaymentGateway paymentGateway;
    private InventoryService inventoryService;
    
    public void setPaymentGateway(PaymentGateway paymentGateway) {
        this.paymentGateway = paymentGateway;
    }
    
    public void setInventoryService(InventoryService inventoryService) {
        this.inventoryService = inventoryService;
    }
}

// Use case: Optional dependencies, reconfiguration at runtime
```

**3. Field Injection (Spring)**
```java
public class OrderService {
    @Autowired
    private PaymentGateway paymentGateway;
    
    @Autowired
    private InventoryService inventoryService;
}

// Avoid: Hard to test, hides dependencies
```

---

### 3.3 DI Frameworks

**Spring Framework:**
```java
// Define beans
@Configuration
public class AppConfig {
    @Bean
    public UserRepository userRepository() {
        return new PostgresUserRepository();
    }
    
    @Bean
    public EmailService emailService() {
        return new SMTPEmailService();
    }
    
    @Bean
    public UserService userService(UserRepository repository, 
                                   EmailService emailService) {
        return new UserService(repository, emailService);
    }
}

// Use
@Service
public class UserController {
    private final UserService userService;
    
    @Autowired
    public UserController(UserService userService) {
        this.userService = userService;
    }
    
    @PostMapping("/register")
    public void register(@RequestBody User user) {
        userService.registerUser(user);
    }
}
```

**Guice (Google):**
```java
// Module
public class AppModule extends AbstractModule {
    @Override
    protected void configure() {
        bind(UserRepository.class).to(PostgresUserRepository.class);
        bind(EmailService.class).to(SMTPEmailService.class);
    }
}

// Inject
public class UserService {
    private final UserRepository repository;
    private final EmailService emailService;
    
    @Inject
    public UserService(UserRepository repository, EmailService emailService) {
        this.repository = repository;
        this.emailService = emailService;
    }
}

// Bootstrap
Injector injector = Guice.createInjector(new AppModule());
UserService userService = injector.getInstance(UserService.class);
```

**Manual DI (Poor Man's DI):**
```java
// Factory method
public class ServiceFactory {
    public static UserService createUserService() {
        UserRepository repository = new PostgresUserRepository();
        EmailService emailService = new SMTPEmailService();
        return new UserService(repository, emailService);
    }
}

// Usage
UserService userService = ServiceFactory.createUserService();
```

---

### 3.4 Real-World Example: E-Commerce

```java
// Interfaces
public interface PaymentGateway {
    void processPayment(String token, double amount);
}

public interface InventoryService {
    void decreaseStock(int productId, int quantity);
}

public interface NotificationService {
    void sendNotification(String email, String message);
}

public interface OrderRepository {
    void save(Order order);
}

// Implementations
public class StripePaymentGateway implements PaymentGateway {
    @Override
    public void processPayment(String token, double amount) {
        // Stripe API call
    }
}

public class DatabaseInventoryService implements InventoryService {
    @Override
    public void decreaseStock(int productId, int quantity) {
        // Update database
    }
}

public class EmailNotificationService implements NotificationService {
    @Override
    public void sendNotification(String email, String message) {
        // Send email
    }
}

public class PostgresOrderRepository implements OrderRepository {
    @Override
    public void save(Order order) {
        // Save to PostgreSQL
    }
}

// Service with DI
public class OrderService {
    private final PaymentGateway paymentGateway;
    private final InventoryService inventoryService;
    private final NotificationService notificationService;
    private final OrderRepository orderRepository;
    
    public OrderService(PaymentGateway paymentGateway,
                       InventoryService inventoryService,
                       NotificationService notificationService,
                       OrderRepository orderRepository) {
        this.paymentGateway = paymentGateway;
        this.inventoryService = inventoryService;
        this.notificationService = notificationService;
        this.orderRepository = orderRepository;
    }
    
    public void placeOrder(Order order) {
        // Process payment
        paymentGateway.processPayment(order.getPaymentToken(), order.getTotal());
        
        // Decrease inventory
        for (OrderItem item : order.getItems()) {
            inventoryService.decreaseStock(item.getProductId(), item.getQuantity());
        }
        
        // Save order
        orderRepository.save(order);
        
        // Notify customer
        notificationService.sendNotification(
            order.getCustomer().getEmail(),
            "Order placed successfully!"
        );
    }
}

// Spring Configuration
@Configuration
public class OrderConfig {
    @Bean
    public PaymentGateway paymentGateway() {
        return new StripePaymentGateway();
    }
    
    @Bean
    public InventoryService inventoryService() {
        return new DatabaseInventoryService();
    }
    
    @Bean
    public NotificationService notificationService() {
        return new EmailNotificationService();
    }
    
    @Bean
    public OrderRepository orderRepository() {
        return new PostgresOrderRepository();
    }
    
    @Bean
    public OrderService orderService(PaymentGateway paymentGateway,
                                     InventoryService inventoryService,
                                     NotificationService notificationService,
                                     OrderRepository orderRepository) {
        return new OrderService(
            paymentGateway,
            inventoryService,
            notificationService,
            orderRepository
        );
    }
}
```

---

## 4. Design by Contract

### 4.1 Concept

**Definition:** Define formal, precise specifications for components

**Three parts:**
1. **Preconditions:** What must be true before method executes
2. **Postconditions:** What must be true after method executes
3. **Invariants:** What must always be true for the class

---

### 4.2 Preconditions

```java
public class BankAccount {
    private double balance;
    
    /**
     * Withdraw money from account
     * 
     * @param amount Amount to withdraw
     * @precondition amount > 0 && amount <= balance
     * @postcondition balance == old(balance) - amount
     * @throws IllegalArgumentException if amount <= 0
     * @throws InsufficientFundsException if amount > balance
     */
    public void withdraw(double amount) {
        // Precondition checks
        if (amount <= 0) {
            throw new IllegalArgumentException("Amount must be positive");
        }
        if (amount > balance) {
            throw new InsufficientFundsException("Insufficient funds");
        }
        
        // Execute
        balance -= amount;
        
        // Postcondition: balance decreased by amount (verified in tests)
    }
}
```

---

### 4.3 Assertions

```java
public class Stack<T> {
    private List<T> elements = new ArrayList<>();
    
    public void push(T item) {
        // Precondition
        assert item != null : "Cannot push null";
        
        elements.add(item);
        
        // Postcondition
        assert !elements.isEmpty() : "Stack should not be empty after push";
    }
    
    public T pop() {
        // Precondition
        assert !elements.isEmpty() : "Cannot pop from empty stack";
        
        T item = elements.remove(elements.size() - 1);
        
        // Postcondition
        assert item != null : "Popped item should not be null";
        
        return item;
    }
    
    // Invariant: elements should never be null
    private void checkInvariant() {
        assert elements != null : "Elements list should never be null";
    }
}

// Run with: java -ea (enable assertions)
```

---

### 4.4 Java Bean Validation

```java
import javax.validation.constraints.*;

public class User {
    @NotNull(message = "Name is required")
    @Size(min = 2, max = 50, message = "Name must be between 2 and 50 characters")
    private String name;
    
    @NotNull(message = "Email is required")
    @Email(message = "Invalid email format")
    private String email;
    
    @Min(value = 18, message = "Must be at least 18 years old")
    @Max(value = 120, message = "Age must be less than 120")
    private int age;
    
    @Pattern(regexp = "^\\+?[1-9]\\d{1,14}$", message = "Invalid phone number")
    private String phone;
}

// Validation
ValidatorFactory factory = Validation.buildDefaultValidatorFactory();
Validator validator = factory.getValidator();

User user = new User("A", "invalid-email", 15, "123");
Set<ConstraintViolation<User>> violations = validator.validate(user);

for (ConstraintViolation<User> violation : violations) {
    System.out.println(violation.getMessage());
}
// Output:
// Name must be between 2 and 50 characters
// Invalid email format
// Must be at least 18 years old
```

---

### 4.5 Contract Testing

```java
public class BankAccountTest {
    @Test
    public void testWithdrawContract() {
        BankAccount account = new BankAccount(1000);
        
        // Precondition: amount > 0 && amount <= balance
        assertThrows(IllegalArgumentException.class, 
                    () -> account.withdraw(-100));
        assertThrows(InsufficientFundsException.class, 
                    () -> account.withdraw(2000));
        
        // Valid withdrawal
        double initialBalance = account.getBalance();
        account.withdraw(500);
        
        // Postcondition: balance decreased by amount
        assertEquals(initialBalance - 500, account.getBalance(), 0.01);
    }
    
    @Test
    public void testInvariant() {
        BankAccount account = new BankAccount(1000);
        
        // Invariant: balance >= 0 always
        assertTrue(account.getBalance() >= 0);
        
        account.withdraw(500);
        assertTrue(account.getBalance() >= 0);
        
        // After any operation, invariant must hold
    }
}
```

---

## 5. Composition over Inheritance

### 5.1 Problem with Inheritance

**Brittle Base Class:**
```java
// Base class
public class Vehicle {
    public void start() {
        System.out.println("Starting engine...");
    }
    
    public void stop() {
        System.out.println("Stopping engine...");
    }
}

public class Car extends Vehicle {
    public void drive() {
        start();
        System.out.println("Driving...");
        stop();
    }
}

public class ElectricCar extends Vehicle {
    @Override
    public void start() {
        // Electric cars don't have engines!
        System.out.println("Powering on...");
    }
    
    @Override
    public void stop() {
        System.out.println("Powering off...");
    }
}

// Problem: What about Bicycle? It doesn't have an engine!
public class Bicycle extends Vehicle {
    @Override
    public void start() {
        // Bicycles don't have engines!
        throw new UnsupportedOperationException();
    }
    
    @Override
    public void stop() {
        throw new UnsupportedOperationException();
    }
}

// Inheritance hierarchy is wrong!
```

---

### 5.2 Solution: Composition

```java
// Components (composition)
public interface Engine {
    void start();
    void stop();
}

public class GasEngine implements Engine {
    @Override
    public void start() {
        System.out.println("Starting gas engine...");
    }
    
    @Override
    public void stop() {
        System.out.println("Stopping gas engine...");
    }
}

public class ElectricMotor implements Engine {
    @Override
    public void start() {
        System.out.println("Powering on electric motor...");
    }
    
    @Override
    public void stop() {
        System.out.println("Powering off electric motor...");
    }
}

// Compose vehicles from components
public class Car {
    private Engine engine;
    
    public Car(Engine engine) {
        this.engine = engine;
    }
    
    public void drive() {
        engine.start();
        System.out.println("Driving...");
        engine.stop();
    }
}

public class Bicycle {
    // No engine!
    
    public void ride() {
        System.out.println("Pedaling...");
    }
}

// Usage
Car gasCar = new Car(new GasEngine());
gasCar.drive();

Car electricCar = new Car(new ElectricMotor());
electricCar.drive();

Bicycle bike = new Bicycle();
bike.ride();  // No engine methods!
```

---

### 5.3 Real-World Example: Logging

**Bad (Inheritance):**
```java
public class BaseService {
    protected void log(String message) {
        System.out.println(message);
    }
}

public class UserService extends BaseService {
    public void createUser(User user) {
        log("Creating user: " + user.getName());
        // ...
    }
}

public class OrderService extends BaseService {
    public void createOrder(Order order) {
        log("Creating order: " + order.getId());
        // ...
    }
}

// Problem: All services MUST extend BaseService to get logging
// Can't inherit from another class (single inheritance in Java)
```

**Good (Composition):**
```java
public interface Logger {
    void log(String message);
}

public class ConsoleLogger implements Logger {
    @Override
    public void log(String message) {
        System.out.println(message);
    }
}

public class FileLogger implements Logger {
    @Override
    public void log(String message) {
        // Write to file
    }
}

public class UserService {
    private final Logger logger;
    
    public UserService(Logger logger) {
        this.logger = logger;
    }
    
    public void createUser(User user) {
        logger.log("Creating user: " + user.getName());
        // ...
    }
}

public class OrderService {
    private final Logger logger;
    
    public OrderService(Logger logger) {
        this.logger = logger;
    }
    
    public void createOrder(Order order) {
        logger.log("Creating order: " + order.getId());
        // ...
    }
}

// Benefits:
// - Services can inherit from any class
// - Easy to swap logger implementation
// - Can inject different loggers for different services
```

---

### 5.4 Decorator Pattern (Composition)

```java
// Component interface
public interface Coffee {
    double getCost();
    String getDescription();
}

// Base component
public class SimpleCoffee implements Coffee {
    @Override
    public double getCost() {
        return 2.0;
    }
    
    @Override
    public String getDescription() {
        return "Simple coffee";
    }
}

// Decorators (composition)
public class MilkDecorator implements Coffee {
    private Coffee coffee;
    
    public MilkDecorator(Coffee coffee) {
        this.coffee = coffee;
    }
    
    @Override
    public double getCost() {
        return coffee.getCost() + 0.5;
    }
    
    @Override
    public String getDescription() {
        return coffee.getDescription() + ", milk";
    }
}

public class SugarDecorator implements Coffee {
    private Coffee coffee;
    
    public SugarDecorator(Coffee coffee) {
        this.coffee = coffee;
    }
    
    @Override
    public double getCost() {
        return coffee.getCost() + 0.2;
    }
    
    @Override
    public String getDescription() {
        return coffee.getDescription() + ", sugar";
    }
}

// Usage
Coffee coffee = new SimpleCoffee();
coffee = new MilkDecorator(coffee);
coffee = new SugarDecorator(coffee);

System.out.println(coffee.getDescription());  // "Simple coffee, milk, sugar"
System.out.println(coffee.getCost());  // 2.7
```

---

## 6. Production Patterns

### 6.1 Repository Pattern

```java
// Entity
public class User {
    private Long id;
    private String name;
    private String email;
    // getters/setters
}

// Repository interface
public interface UserRepository {
    User findById(Long id);
    List<User> findAll();
    User save(User user);
    void delete(Long id);
    List<User> findByEmail(String email);
}

// Implementation
public class JpaUserRepository implements UserRepository {
    private final EntityManager entityManager;
    
    public JpaUserRepository(EntityManager entityManager) {
        this.entityManager = entityManager;
    }
    
    @Override
    public User findById(Long id) {
        return entityManager.find(User.class, id);
    }
    
    @Override
    public List<User> findAll() {
        return entityManager.createQuery("SELECT u FROM User u", User.class)
                           .getResultList();
    }
    
    @Override
    public User save(User user) {
        if (user.getId() == null) {
            entityManager.persist(user);
            return user;
        } else {
            return entityManager.merge(user);
        }
    }
    
    @Override
    public void delete(Long id) {
        User user = findById(id);
        if (user != null) {
            entityManager.remove(user);
        }
    }
    
    @Override
    public List<User> findByEmail(String email) {
        return entityManager.createQuery(
            "SELECT u FROM User u WHERE u.email = :email", User.class)
            .setParameter("email", email)
            .getResultList();
    }
}

// Service layer
public class UserService {
    private final UserRepository userRepository;
    
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
    
    public User getUser(Long id) {
        return userRepository.findById(id);
    }
    
    public void registerUser(User user) {
        // Business logic
        validateUser(user);
        userRepository.save(user);
    }
}
```

---

### 6.2 Service Layer Pattern

```java
// DTOs (Data Transfer Objects)
public class CreateOrderRequest {
    private Long customerId;
    private List<OrderItemDTO> items;
    // getters/setters
}

public class OrderItemDTO {
    private Long productId;
    private int quantity;
    // getters/setters
}

public class OrderResponse {
    private Long orderId;
    private double total;
    private String status;
    // getters/setters
}

// Service
@Service
@Transactional
public class OrderService {
    private final OrderRepository orderRepository;
    private final ProductRepository productRepository;
    private final PaymentService paymentService;
    private final InventoryService inventoryService;
    
    public OrderService(OrderRepository orderRepository,
                       ProductRepository productRepository,
                       PaymentService paymentService,
                       InventoryService inventoryService) {
        this.orderRepository = orderRepository;
        this.productRepository = productRepository;
        this.paymentService = paymentService;
        this.inventoryService = inventoryService;
    }
    
    public OrderResponse createOrder(CreateOrderRequest request) {
        // Validate
        validateRequest(request);
        
        // Calculate total
        double total = 0;
        List<OrderItem> orderItems = new ArrayList<>();
        for (OrderItemDTO itemDTO : request.getItems()) {
            Product product = productRepository.findById(itemDTO.getProductId())
                .orElseThrow(() -> new ProductNotFoundException());
            
            OrderItem orderItem = new OrderItem(product, itemDTO.getQuantity());
            orderItems.add(orderItem);
            total += product.getPrice() * itemDTO.getQuantity();
        }
        
        // Create order
        Order order = new Order(request.getCustomerId(), orderItems, total);
        order = orderRepository.save(order);
        
        // Process payment
        paymentService.processPayment(order);
        
        // Update inventory
        inventoryService.decreaseStock(orderItems);
        
        // Return response
        return new OrderResponse(order.getId(), total, "CONFIRMED");
    }
}
```

---

### 6.3 Factory Pattern

```java
// Product interface
public interface PaymentProcessor {
    void processPayment(Order order);
}

// Concrete products
public class CreditCardProcessor implements PaymentProcessor {
    @Override
    public void processPayment(Order order) {
        System.out.println("Processing credit card payment");
    }
}

public class PayPalProcessor implements PaymentProcessor {
    @Override
    public void processPayment(Order order) {
        System.out.println("Processing PayPal payment");
    }
}

public class CryptoProcessor implements PaymentProcessor {
    @Override
    public void processPayment(Order order) {
        System.out.println("Processing crypto payment");
    }
}

// Factory
public class PaymentProcessorFactory {
    public PaymentProcessor createProcessor(PaymentMethod method) {
        switch (method) {
            case CREDIT_CARD:
                return new CreditCardProcessor();
            case PAYPAL:
                return new PayPalProcessor();
            case CRYPTO:
                return new CryptoProcessor();
            default:
                throw new IllegalArgumentException("Unknown payment method");
        }
    }
}

// Usage
PaymentProcessorFactory factory = new PaymentProcessorFactory();
PaymentProcessor processor = factory.createProcessor(PaymentMethod.CREDIT_CARD);
processor.processPayment(order);
```

---

### 6.4 Builder Pattern

```java
// Complex object
public class User {
    private final String name;          // Required
    private final String email;         // Required
    private final String phone;         // Optional
    private final String address;       // Optional
    private final int age;              // Optional
    private final boolean isActive;     // Optional
    
    private User(Builder builder) {
        this.name = builder.name;
        this.email = builder.email;
        this.phone = builder.phone;
        this.address = builder.address;
        this.age = builder.age;
        this.isActive = builder.isActive;
    }
    
    public static class Builder {
        // Required
        private final String name;
        private final String email;
        
        // Optional (defaults)
        private String phone = "";
        private String address = "";
        private int age = 0;
        private boolean isActive = true;
        
        public Builder(String name, String email) {
            this.name = name;
            this.email = email;
        }
        
        public Builder phone(String phone) {
            this.phone = phone;
            return this;
        }
        
        public Builder address(String address) {
            this.address = address;
            return this;
        }
        
        public Builder age(int age) {
            this.age = age;
            return this;
        }
        
        public Builder isActive(boolean isActive) {
            this.isActive = isActive;
            return this;
        }
        
        public User build() {
            return new User(this);
        }
    }
}

// Usage
User user = new User.Builder("John", "john@example.com")
    .phone("+1234567890")
    .age(30)
    .address("123 Main St")
    .build();
```

---

## Summary

### Best Practices

✅ **SOLID Principles:**
- SRP: One class, one responsibility
- OCP: Extend without modification
- LSP: Substitutable subclasses
- ISP: Small, focused interfaces
- DIP: Depend on abstractions

✅ **Dependency Injection:**
- Use constructor injection (preferred)
- Depend on interfaces, not implementations
- Use DI frameworks (Spring, Guice) in production

✅ **Design by Contract:**
- Document preconditions, postconditions, invariants
- Use assertions for internal checks
- Use validation frameworks for user input

✅ **Composition over Inheritance:**
- Prefer composition for flexibility
- Use inheritance only for true "is-a" relationships
- Avoid deep inheritance hierarchies

✅ **Production Patterns:**
- Repository: Data access abstraction
- Service: Business logic layer
- Factory: Object creation
- Builder: Complex object construction

---

### Interview Preparation

**For 40+ LPA roles:**

1. **Code Review:** Identify violations in code samples
2. **Refactoring:** Transform bad code to follow principles
3. **Design Discussion:** Justify design decisions
4. **Trade-offs:** When to break rules (pragmatism vs purity)
5. **Real Examples:** Share from your projects

**Common Questions:**
- "How do you ensure your code follows SOLID?"
- "When would you use composition vs inheritance?"
- "Explain dependency injection with an example"
- "How do you test code with many dependencies?"
- "Design a payment processing system following SOLID"

---

**End of OOP & SOLID Principles Module**

**Total Lines (Part 1 + Part 2): ~6,000**
