# OOP & SOLID Principles - Part 1

**Purpose:** Master object-oriented design for 40+ LPA Principal Engineer roles (FAANG-level interviews)

**Prerequisites:** Basic Java/OOP knowledge, design patterns awareness

---

## Table of Contents

**Part 1 (this file):**
1. [OOP Fundamentals](#1-oop-fundamentals)
2. [SOLID Principles](#2-solid-principles)

**Part 2 (01-OOP-Principles-PART2.md):**
3. Dependency Injection
4. Design by Contract
5. Composition over Inheritance
6. Production Patterns

---

## 1. OOP Fundamentals

### 1.1 Four Pillars

**1. Encapsulation**
```java
// Bad: Public fields
public class BankAccount {
    public double balance;  // Anyone can modify!
}

// Client code
account.balance = 1000000;  // Direct access - no validation!

// Good: Private fields + public methods
public class BankAccount {
    private double balance;  // Protected
    
    public void deposit(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("Amount must be positive");
        }
        balance += amount;
    }
    
    public void withdraw(double amount) {
        if (amount > balance) {
            throw new InsufficientFundsException();
        }
        balance -= amount;
    }
    
    public double getBalance() {
        return balance;
    }
}
```

**Benefits:**
- Data hiding (internal state protected)
- Validation (enforce business rules)
- Flexibility (change implementation without breaking clients)

---

**2. Abstraction**
```java
// Abstract away complexity
public interface PaymentProcessor {
    void processPayment(Order order, PaymentMethod method);
}

// Client doesn't need to know HOW payment is processed
public class OrderService {
    private final PaymentProcessor paymentProcessor;
    
    public void checkout(Order order) {
        // Abstract: Don't care if it's Stripe, PayPal, or Bitcoin
        paymentProcessor.processPayment(order, order.getPaymentMethod());
    }
}

// Multiple implementations
public class StripePaymentProcessor implements PaymentProcessor {
    @Override
    public void processPayment(Order order, PaymentMethod method) {
        // Stripe-specific logic
        StripeAPI.charge(method.getToken(), order.getTotal());
    }
}

public class PayPalPaymentProcessor implements PaymentProcessor {
    @Override
    public void processPayment(Order order, PaymentMethod method) {
        // PayPal-specific logic
        PayPalAPI.createTransaction(method.getEmail(), order.getTotal());
    }
}
```

**Benefits:**
- Hide implementation details
- Focus on WHAT, not HOW
- Easy to swap implementations

---

**3. Inheritance**
```java
// Base class
public abstract class Animal {
    protected String name;
    protected int age;
    
    public Animal(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    public abstract void makeSound();
    
    public void sleep() {
        System.out.println(name + " is sleeping");
    }
}

// Derived classes
public class Dog extends Animal {
    public Dog(String name, int age) {
        super(name, age);
    }
    
    @Override
    public void makeSound() {
        System.out.println("Woof!");
    }
    
    public void fetch() {
        System.out.println(name + " is fetching");
    }
}

public class Cat extends Animal {
    public Cat(String name, int age) {
        super(name, age);
    }
    
    @Override
    public void makeSound() {
        System.out.println("Meow!");
    }
}
```

**Benefits:**
- Code reuse (common behavior in base class)
- Polymorphism (treat Dog/Cat as Animal)

**Warning:** Favor composition over inheritance (see section 5)

---

**4. Polymorphism**
```java
public class AnimalShelter {
    private List<Animal> animals = new ArrayList<>();
    
    public void addAnimal(Animal animal) {
        animals.add(animal);
    }
    
    public void makeAllSoundsAtNight() {
        for (Animal animal : animals) {
            animal.makeSound();  // Runtime polymorphism!
            // Calls Dog.makeSound() or Cat.makeSound() based on actual type
        }
    }
}

// Usage
AnimalShelter shelter = new AnimalShelter();
shelter.addAnimal(new Dog("Buddy", 3));
shelter.addAnimal(new Cat("Whiskers", 2));
shelter.addAnimal(new Dog("Max", 5));

shelter.makeAllSoundsAtNight();
// Output:
// Woof!
// Meow!
// Woof!
```

**Types:**
- **Compile-time (Method Overloading):** Same method name, different parameters
- **Runtime (Method Overriding):** Subclass overrides superclass method

---

## 2. SOLID Principles

### 2.1 Single Responsibility Principle (SRP)

**Definition:** A class should have only ONE reason to change

**Bad Example:**
```java
// Violates SRP: 3 responsibilities!
public class Employee {
    private String name;
    private double salary;
    
    // Responsibility 1: Business logic
    public double calculateSalary() {
        return salary * 1.1;  // 10% bonus
    }
    
    // Responsibility 2: Persistence
    public void saveToDatabase() {
        Database.execute("INSERT INTO employees ...");
    }
    
    // Responsibility 3: Reporting
    public void generatePayslip() {
        System.out.println("Payslip for " + name);
        System.out.println("Salary: " + calculateSalary());
    }
}

// Problem: If database schema changes, or payslip format changes,
// we need to modify Employee class!
```

**Good Example:**
```java
// Each class has ONE responsibility

// Business logic
public class Employee {
    private String name;
    private double salary;
    
    public double calculateSalary() {
        return salary * 1.1;
    }
    
    // Getters/setters only
    public String getName() { return name; }
    public double getSalary() { return salary; }
}

// Persistence
public class EmployeeRepository {
    public void save(Employee employee) {
        Database.execute("INSERT INTO employees ...");
    }
    
    public Employee findById(int id) {
        // Query database
        return employee;
    }
}

// Reporting
public class PayslipGenerator {
    public void generate(Employee employee) {
        System.out.println("Payslip for " + employee.getName());
        System.out.println("Salary: " + employee.calculateSalary());
    }
}
```

**Benefits:**
- Easy to understand (each class does one thing)
- Easy to test (mock dependencies)
- Easy to change (changing DB doesn't affect payslip logic)

---

**Real-World Example: Order Processing**
```java
// Bad: God class with 5 responsibilities
public class OrderService {
    public void processOrder(Order order) {
        // 1. Validate
        if (order.getItems().isEmpty()) throw new Exception();
        
        // 2. Calculate total
        double total = 0;
        for (Item item : order.getItems()) {
            total += item.getPrice() * item.getQuantity();
        }
        
        // 3. Process payment
        StripeAPI.charge(order.getPaymentToken(), total);
        
        // 4. Update inventory
        for (Item item : order.getItems()) {
            Database.execute("UPDATE inventory SET quantity = quantity - " + item.getQuantity());
        }
        
        // 5. Send notification
        EmailAPI.send(order.getCustomer().getEmail(), "Order confirmed!");
    }
}

// Good: Separate responsibilities
public class OrderValidator {
    public void validate(Order order) {
        if (order.getItems().isEmpty()) {
            throw new InvalidOrderException("Order must have items");
        }
    }
}

public class PriceCalculator {
    public double calculateTotal(Order order) {
        return order.getItems().stream()
            .mapToDouble(item -> item.getPrice() * item.getQuantity())
            .sum();
    }
}

public class PaymentProcessor {
    private final StripeClient stripeClient;
    
    public void processPayment(Order order, double amount) {
        stripeClient.charge(order.getPaymentToken(), amount);
    }
}

public class InventoryService {
    public void decreaseStock(List<Item> items) {
        for (Item item : items) {
            inventoryRepository.decreaseQuantity(item.getId(), item.getQuantity());
        }
    }
}

public class NotificationService {
    private final EmailClient emailClient;
    
    public void sendOrderConfirmation(Order order) {
        emailClient.send(order.getCustomer().getEmail(), 
                        "Order #" + order.getId() + " confirmed!");
    }
}

// Orchestrator (coordinates, but delegates work)
public class OrderService {
    private final OrderValidator validator;
    private final PriceCalculator calculator;
    private final PaymentProcessor paymentProcessor;
    private final InventoryService inventoryService;
    private final NotificationService notificationService;
    
    public void processOrder(Order order) {
        validator.validate(order);
        
        double total = calculator.calculateTotal(order);
        paymentProcessor.processPayment(order, total);
        
        inventoryService.decreaseStock(order.getItems());
        notificationService.sendOrderConfirmation(order);
    }
}
```

---

### 2.2 Open/Closed Principle (OCP)

**Definition:** Classes should be OPEN for extension, but CLOSED for modification

**Bad Example:**
```java
// Must modify class to add new shapes
public class AreaCalculator {
    public double calculateArea(Object shape) {
        if (shape instanceof Circle) {
            Circle circle = (Circle) shape;
            return Math.PI * circle.getRadius() * circle.getRadius();
        } else if (shape instanceof Rectangle) {
            Rectangle rect = (Rectangle) shape;
            return rect.getWidth() * rect.getHeight();
        } else if (shape instanceof Triangle) {  // Add new shape = modify class!
            Triangle tri = (Triangle) shape;
            return 0.5 * tri.getBase() * tri.getHeight();
        }
        throw new IllegalArgumentException("Unknown shape");
    }
}
```

**Good Example:**
```java
// Use polymorphism
public interface Shape {
    double calculateArea();
}

public class Circle implements Shape {
    private double radius;
    
    @Override
    public double calculateArea() {
        return Math.PI * radius * radius;
    }
}

public class Rectangle implements Shape {
    private double width;
    private double height;
    
    @Override
    public double calculateArea() {
        return width * height;
    }
}

public class Triangle implements Shape {
    private double base;
    private double height;
    
    @Override
    public double calculateArea() {
        return 0.5 * base * height;
    }
}

// No need to modify! Just use interface
public class AreaCalculator {
    public double calculateTotalArea(List<Shape> shapes) {
        return shapes.stream()
            .mapToDouble(Shape::calculateArea)
            .sum();
    }
}

// Add new shape: NO modification needed!
public class Pentagon implements Shape {
    // ... fields
    
    @Override
    public double calculateArea() {
        // Pentagon formula
        return 0.0;
    }
}
```

---

**Real-World Example: Discount System**
```java
// Bad: Modify class for new discount types
public class DiscountCalculator {
    public double applyDiscount(Order order, String discountType) {
        double total = order.getTotal();
        
        if (discountType.equals("SEASONAL")) {
            return total * 0.9;  // 10% off
        } else if (discountType.equals("LOYALTY")) {
            return total * 0.85;  // 15% off
        } else if (discountType.equals("FLASH_SALE")) {  // New type = modification!
            return total * 0.7;  // 30% off
        }
        
        return total;
    }
}

// Good: Strategy pattern
public interface DiscountStrategy {
    double apply(double amount);
}

public class SeasonalDiscount implements DiscountStrategy {
    @Override
    public double apply(double amount) {
        return amount * 0.9;
    }
}

public class LoyaltyDiscount implements DiscountStrategy {
    @Override
    public double apply(double amount) {
        return amount * 0.85;
    }
}

public class FlashSaleDiscount implements DiscountStrategy {
    @Override
    public double apply(double amount) {
        return amount * 0.7;
    }
}

public class DiscountCalculator {
    public double applyDiscount(Order order, DiscountStrategy strategy) {
        return strategy.apply(order.getTotal());
    }
}

// Usage
DiscountCalculator calculator = new DiscountCalculator();
double finalPrice = calculator.applyDiscount(order, new FlashSaleDiscount());
```

---

### 2.3 Liskov Substitution Principle (LSP)

**Definition:** Objects of a superclass should be replaceable with objects of a subclass without breaking the application

**Bad Example:**
```java
public class Bird {
    public void fly() {
        System.out.println("Flying...");
    }
}

public class Penguin extends Bird {
    @Override
    public void fly() {
        throw new UnsupportedOperationException("Penguins can't fly!");
    }
}

// Violates LSP: Substituting Bird with Penguin breaks code
public void makeBirdFly(Bird bird) {
    bird.fly();  // Throws exception if bird is Penguin!
}

makeBirdFly(new Penguin());  // CRASH!
```

**Good Example:**
```java
// Proper abstraction
public interface Animal {
    void move();
}

public interface Flyable {
    void fly();
}

public class Sparrow implements Animal, Flyable {
    @Override
    public void move() {
        fly();
    }
    
    @Override
    public void fly() {
        System.out.println("Sparrow flying...");
    }
}

public class Penguin implements Animal {
    @Override
    public void move() {
        swim();
    }
    
    public void swim() {
        System.out.println("Penguin swimming...");
    }
}

// Now safe
public void makeAnimalMove(Animal animal) {
    animal.move();  // Works for both Sparrow and Penguin
}
```

---

**Real-World Example: Payment Processing**
```java
// Bad: Violates LSP
public class PaymentProcessor {
    public void processPayment(double amount) {
        // Charge credit card
        creditCardAPI.charge(amount);
    }
}

public class CashPaymentProcessor extends PaymentProcessor {
    @Override
    public void processPayment(double amount) {
        throw new UnsupportedOperationException("Cash payments not supported!");
        // Violates LSP: Can't substitute PaymentProcessor with CashPaymentProcessor
    }
}

// Good: Proper abstraction
public interface PaymentMethod {
    void processPayment(double amount);
}

public class CreditCardPayment implements PaymentMethod {
    @Override
    public void processPayment(double amount) {
        creditCardAPI.charge(amount);
    }
}

public class CashPayment implements PaymentMethod {
    @Override
    public void processPayment(double amount) {
        // Record cash payment
        cashRegister.recordPayment(amount);
    }
}

public class PayPalPayment implements PaymentMethod {
    @Override
    public void processPayment(double amount) {
        paypalAPI.charge(amount);
    }
}

// Safe substitution
public void checkout(Order order, PaymentMethod paymentMethod) {
    double total = order.getTotal();
    paymentMethod.processPayment(total);  // Works with any PaymentMethod!
}
```

---

**LSP Rules:**
1. **Preconditions cannot be strengthened** (subclass can't require MORE than parent)
2. **Postconditions cannot be weakened** (subclass must deliver AT LEAST what parent promises)
3. **Invariants must be preserved** (class invariants must hold in subclass)
4. **No new exceptions** (subclass can't throw new checked exceptions)

---

### 2.4 Interface Segregation Principle (ISP)

**Definition:** Clients should not be forced to depend on interfaces they don't use

**Bad Example:**
```java
// Fat interface
public interface Worker {
    void work();
    void eat();
    void sleep();
    void getPaid();
}

public class HumanWorker implements Worker {
    @Override
    public void work() { /* ... */ }
    
    @Override
    public void eat() { /* ... */ }
    
    @Override
    public void sleep() { /* ... */ }
    
    @Override
    public void getPaid() { /* ... */ }
}

public class RobotWorker implements Worker {
    @Override
    public void work() { /* ... */ }
    
    @Override
    public void eat() {
        // Robots don't eat! Forced to implement useless method
        throw new UnsupportedOperationException();
    }
    
    @Override
    public void sleep() {
        // Robots don't sleep!
        throw new UnsupportedOperationException();
    }
    
    @Override
    public void getPaid() {
        // Robots don't get paid!
        throw new UnsupportedOperationException();
    }
}
```

**Good Example:**
```java
// Segregated interfaces
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
    void getPaid();
}

public class HumanWorker implements Workable, Eatable, Sleepable, Payable {
    @Override
    public void work() { /* ... */ }
    
    @Override
    public void eat() { /* ... */ }
    
    @Override
    public void sleep() { /* ... */ }
    
    @Override
    public void getPaid() { /* ... */ }
}

public class RobotWorker implements Workable {
    @Override
    public void work() { /* ... */ }
    // No need to implement eat(), sleep(), getPaid()!
}
```

---

**Real-World Example: Document Handling**
```java
// Bad: Fat interface
public interface Document {
    void open();
    void save();
    void print();
    void fax();
    void scan();
}

public class PDFDocument implements Document {
    @Override
    public void open() { /* ... */ }
    
    @Override
    public void save() { /* ... */ }
    
    @Override
    public void print() { /* ... */ }
    
    @Override
    public void fax() {
        throw new UnsupportedOperationException("PDF can't fax");
    }
    
    @Override
    public void scan() {
        throw new UnsupportedOperationException("PDF can't scan");
    }
}

// Good: Segregated
public interface Openable {
    void open();
}

public interface Saveable {
    void save();
}

public interface Printable {
    void print();
}

public interface Faxable {
    void fax();
}

public interface Scannable {
    void scan();
}

public class PDFDocument implements Openable, Saveable, Printable {
    @Override
    public void open() { /* ... */ }
    
    @Override
    public void save() { /* ... */ }
    
    @Override
    public void print() { /* ... */ }
}

public class ScannedDocument implements Openable, Saveable, Scannable {
    @Override
    public void open() { /* ... */ }
    
    @Override
    public void save() { /* ... */ }
    
    @Override
    public void scan() { /* ... */ }
}
```

---

### 2.5 Dependency Inversion Principle (DIP)

**Definition:** 
1. High-level modules should not depend on low-level modules. Both should depend on abstractions.
2. Abstractions should not depend on details. Details should depend on abstractions.

**Bad Example:**
```java
// High-level module depends on low-level module directly
public class EmailService {
    public void sendEmail(String to, String message) {
        // Send via Gmail
        System.out.println("Sending email via Gmail to " + to);
    }
}

public class UserService {
    private EmailService emailService = new EmailService();  // Tight coupling!
    
    public void registerUser(User user) {
        // Register user
        saveToDatabase(user);
        
        // Send welcome email
        emailService.sendEmail(user.getEmail(), "Welcome!");
    }
}

// Problem: Can't switch to SendGrid or AWS SES without modifying UserService
```

**Good Example:**
```java
// Abstraction (interface)
public interface MessageService {
    void sendMessage(String to, String message);
}

// Low-level implementations
public class EmailService implements MessageService {
    @Override
    public void sendMessage(String to, String message) {
        System.out.println("Email sent to " + to);
    }
}

public class SMSService implements MessageService {
    @Override
    public void sendMessage(String to, String message) {
        System.out.println("SMS sent to " + to);
    }
}

public class SlackService implements MessageService {
    @Override
    public void sendMessage(String to, String message) {
        System.out.println("Slack message sent to " + to);
    }
}

// High-level module depends on abstraction
public class UserService {
    private final MessageService messageService;
    
    // Dependency injection
    public UserService(MessageService messageService) {
        this.messageService = messageService;
    }
    
    public void registerUser(User user) {
        saveToDatabase(user);
        
        // Send welcome message (Email, SMS, or Slack - we don't care!)
        messageService.sendMessage(user.getContact(), "Welcome!");
    }
}

// Usage
MessageService emailService = new EmailService();
UserService userService = new UserService(emailService);

// Easy to switch
MessageService smsService = new SMSService();
UserService userServiceWithSMS = new UserService(smsService);
```

---

**Real-World Example: Payment Processing**
```java
// Bad: High-level depends on low-level
public class StripePaymentGateway {
    public void charge(String token, double amount) {
        System.out.println("Charging $" + amount + " via Stripe");
    }
}

public class OrderService {
    private StripePaymentGateway paymentGateway = new StripePaymentGateway();
    
    public void checkout(Order order) {
        paymentGateway.charge(order.getPaymentToken(), order.getTotal());
    }
    // Tightly coupled to Stripe! Can't switch to PayPal
}

// Good: Depend on abstraction
public interface PaymentGateway {
    void charge(String token, double amount);
}

public class StripePaymentGateway implements PaymentGateway {
    @Override
    public void charge(String token, double amount) {
        stripeAPI.charge(token, amount);
    }
}

public class PayPalPaymentGateway implements PaymentGateway {
    @Override
    public void charge(String token, double amount) {
        paypalAPI.charge(token, amount);
    }
}

public class CryptoPaymentGateway implements PaymentGateway {
    @Override
    public void charge(String token, double amount) {
        bitcoinAPI.transfer(token, amount);
    }
}

public class OrderService {
    private final PaymentGateway paymentGateway;
    
    public OrderService(PaymentGateway paymentGateway) {
        this.paymentGateway = paymentGateway;
    }
    
    public void checkout(Order order) {
        paymentGateway.charge(order.getPaymentToken(), order.getTotal());
    }
}

// Configuration (Spring example)
@Configuration
public class AppConfig {
    @Bean
    public PaymentGateway paymentGateway() {
        String provider = System.getenv("PAYMENT_PROVIDER");
        
        switch (provider) {
            case "stripe":
                return new StripePaymentGateway();
            case "paypal":
                return new PayPalPaymentGateway();
            case "crypto":
                return new CryptoPaymentGateway();
            default:
                throw new IllegalArgumentException("Unknown provider");
        }
    }
    
    @Bean
    public OrderService orderService(PaymentGateway paymentGateway) {
        return new OrderService(paymentGateway);
    }
}
```

---

## SOLID Summary

### Quick Reference

| Principle | What | Why | How |
|-----------|------|-----|-----|
| **SRP** | One class = One responsibility | Easy to understand, test, change | Extract into separate classes |
| **OCP** | Open for extension, Closed for modification | Add features without changing existing code | Use interfaces, polymorphism |
| **LSP** | Subclass substitutable for parent | Polymorphism works correctly | Proper abstraction, no exceptions in overrides |
| **ISP** | Small, focused interfaces | Clients don't depend on unused methods | Split fat interfaces |
| **DIP** | Depend on abstractions | Easy to swap implementations | Use interfaces, dependency injection |

---

### Mnemonic: SOLID

```
S - Single Responsibility
O - Open/Closed
L - Liskov Substitution
I - Interface Segregation
D - Dependency Inversion
```

---

### Interview Tips

**For 40+ LPA roles:**

1. **Know violations:** Identify when SOLID is violated in code samples
2. **Refactor examples:** Be ready to refactor bad code to follow SOLID
3. **Trade-offs:** Discuss when it's okay to violate (e.g., premature abstraction)
4. **Real-world:** Give examples from your projects
5. **Design patterns:** Connect SOLID to patterns (Strategy, Factory, etc.)

**Common Questions:**
- "Refactor this code to follow SRP"
- "How would you make this extensible without modification?"
- "What's wrong with this inheritance hierarchy?"
- "Why is this interface bad?"
- "How do you inject dependencies in production?"

---

**End of Part 1**

**Continue to Part 2:** 01-OOP-Principles-PART2.md for Dependency Injection, Design by Contract, Composition over Inheritance, and Production Patterns.

**Lines so far: ~3,000**
