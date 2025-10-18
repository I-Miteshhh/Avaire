# Design Patterns - Part 2

**Continued from Part 1 (11-Design-Patterns-PART1.md)**

---

## 2. Structural Patterns

**Purpose:** Compose objects into larger structures while keeping them flexible and efficient

### 2.1 Adapter Pattern

**Problem:** Need to make incompatible interfaces work together

**Intent:** Convert interface of a class into another interface clients expect

**Real-world Example: Payment Gateway Integration**

```java
// Target interface (what our application expects)
public interface PaymentProcessor {
    PaymentResponse processPayment(PaymentRequest request);
    RefundResponse refund(String transactionId, double amount);
    TransactionStatus checkStatus(String transactionId);
}

public class PaymentRequest {
    private final String orderId;
    private final double amount;
    private final String currency;
    private final String customerEmail;
    private final Map<String, String> metadata;
    
    // Constructor and getters
    public PaymentRequest(String orderId, double amount, String currency, String customerEmail) {
        this.orderId = orderId;
        this.amount = amount;
        this.currency = currency;
        this.customerEmail = customerEmail;
        this.metadata = new HashMap<>();
    }
    
    public String getOrderId() { return orderId; }
    public double getAmount() { return amount; }
    public String getCurrency() { return currency; }
    public String getCustomerEmail() { return customerEmail; }
    public Map<String, String> getMetadata() { return metadata; }
}

public class PaymentResponse {
    private final boolean success;
    private final String transactionId;
    private final String message;
    private final long timestamp;
    
    public PaymentResponse(boolean success, String transactionId, String message) {
        this.success = success;
        this.transactionId = transactionId;
        this.message = message;
        this.timestamp = System.currentTimeMillis();
    }
    
    public boolean isSuccess() { return success; }
    public String getTransactionId() { return transactionId; }
    public String getMessage() { return message; }
    public long getTimestamp() { return timestamp; }
}

// Adaptee 1: Stripe (third-party API with different interface)
public class StripeAPI {
    public StripeCharge charge(String token, long amountInCents, String currency) {
        System.out.println("Stripe: Charging " + amountInCents + " cents in " + currency);
        
        // Simulate API call
        StripeCharge charge = new StripeCharge();
        charge.id = "ch_" + UUID.randomUUID().toString().substring(0, 8);
        charge.status = "succeeded";
        charge.amount = amountInCents;
        charge.created = System.currentTimeMillis() / 1000;
        
        return charge;
    }
    
    public StripeRefund refund(String chargeId, long amountInCents) {
        System.out.println("Stripe: Refunding " + amountInCents + " cents from charge " + chargeId);
        
        StripeRefund refund = new StripeRefund();
        refund.id = "re_" + UUID.randomUUID().toString().substring(0, 8);
        refund.status = "succeeded";
        refund.amount = amountInCents;
        
        return refund;
    }
    
    public StripeCharge retrieve(String chargeId) {
        System.out.println("Stripe: Retrieving charge " + chargeId);
        
        StripeCharge charge = new StripeCharge();
        charge.id = chargeId;
        charge.status = "succeeded";
        charge.amount = 0;
        
        return charge;
    }
    
    // Stripe's proprietary classes
    public static class StripeCharge {
        public String id;
        public String status;
        public long amount;
        public long created;
    }
    
    public static class StripeRefund {
        public String id;
        public String status;
        public long amount;
    }
}

// Adapter for Stripe
public class StripeAdapter implements PaymentProcessor {
    private final StripeAPI stripeAPI;
    private final String apiKey;
    
    public StripeAdapter(String apiKey) {
        this.apiKey = apiKey;
        this.stripeAPI = new StripeAPI();
    }
    
    @Override
    public PaymentResponse processPayment(PaymentRequest request) {
        try {
            // Convert dollars to cents (Stripe uses cents)
            long amountInCents = (long) (request.getAmount() * 100);
            
            // Create token from customer email (simplified)
            String token = "tok_" + request.getCustomerEmail().hashCode();
            
            // Call Stripe API
            StripeAPI.StripeCharge charge = stripeAPI.charge(
                token, 
                amountInCents, 
                request.getCurrency()
            );
            
            // Adapt Stripe response to our PaymentResponse
            boolean success = "succeeded".equals(charge.status);
            String message = success ? "Payment successful" : "Payment failed: " + charge.status;
            
            return new PaymentResponse(success, charge.id, message);
            
        } catch (Exception e) {
            return new PaymentResponse(false, null, "Stripe error: " + e.getMessage());
        }
    }
    
    @Override
    public RefundResponse refund(String transactionId, double amount) {
        long amountInCents = (long) (amount * 100);
        StripeAPI.StripeRefund refund = stripeAPI.refund(transactionId, amountInCents);
        
        boolean success = "succeeded".equals(refund.status);
        return new RefundResponse(success, refund.id);
    }
    
    @Override
    public TransactionStatus checkStatus(String transactionId) {
        StripeAPI.StripeCharge charge = stripeAPI.retrieve(transactionId);
        return new TransactionStatus(transactionId, charge.status);
    }
}

// Adaptee 2: PayPal (different API structure)
public class PayPalSDK {
    public PayPalPayment createPayment(PayPalAmount amount, String description, String returnUrl) {
        System.out.println("PayPal: Creating payment for " + amount.total + " " + amount.currency);
        
        PayPalPayment payment = new PayPalPayment();
        payment.id = "PAY-" + UUID.randomUUID().toString().substring(0, 8);
        payment.state = "approved";
        payment.createTime = Instant.now().toString();
        
        return payment;
    }
    
    public PayPalRefund refundPayment(String paymentId, PayPalAmount amount) {
        System.out.println("PayPal: Refunding payment " + paymentId);
        
        PayPalRefund refund = new PayPalRefund();
        refund.id = "REF-" + UUID.randomUUID().toString().substring(0, 8);
        refund.state = "completed";
        
        return refund;
    }
    
    public PayPalPayment getPayment(String paymentId) {
        System.out.println("PayPal: Getting payment " + paymentId);
        
        PayPalPayment payment = new PayPalPayment();
        payment.id = paymentId;
        payment.state = "approved";
        
        return payment;
    }
    
    // PayPal's classes
    public static class PayPalPayment {
        public String id;
        public String state;
        public String createTime;
    }
    
    public static class PayPalAmount {
        public String total;
        public String currency;
        
        public PayPalAmount(String total, String currency) {
            this.total = total;
            this.currency = currency;
        }
    }
    
    public static class PayPalRefund {
        public String id;
        public String state;
    }
}

// Adapter for PayPal
public class PayPalAdapter implements PaymentProcessor {
    private final PayPalSDK paypalSDK;
    private final String clientId;
    private final String clientSecret;
    
    public PayPalAdapter(String clientId, String clientSecret) {
        this.clientId = clientId;
        this.clientSecret = clientSecret;
        this.paypalSDK = new PayPalSDK();
    }
    
    @Override
    public PaymentResponse processPayment(PaymentRequest request) {
        try {
            // Adapt our request to PayPal's format
            PayPalSDK.PayPalAmount amount = new PayPalSDK.PayPalAmount(
                String.format("%.2f", request.getAmount()),
                request.getCurrency()
            );
            
            String description = "Order " + request.getOrderId();
            String returnUrl = "https://example.com/return";
            
            // Call PayPal SDK
            PayPalSDK.PayPalPayment payment = paypalSDK.createPayment(
                amount, 
                description, 
                returnUrl
            );
            
            // Adapt PayPal response to our PaymentResponse
            boolean success = "approved".equals(payment.state);
            String message = success ? "PayPal payment approved" : "PayPal payment " + payment.state;
            
            return new PaymentResponse(success, payment.id, message);
            
        } catch (Exception e) {
            return new PaymentResponse(false, null, "PayPal error: " + e.getMessage());
        }
    }
    
    @Override
    public RefundResponse refund(String transactionId, double amount) {
        PayPalSDK.PayPalAmount refundAmount = new PayPalSDK.PayPalAmount(
            String.format("%.2f", amount),
            "USD"
        );
        
        PayPalSDK.PayPalRefund refund = paypalSDK.refundPayment(transactionId, refundAmount);
        boolean success = "completed".equals(refund.state);
        
        return new RefundResponse(success, refund.id);
    }
    
    @Override
    public TransactionStatus checkStatus(String transactionId) {
        PayPalSDK.PayPalPayment payment = paypalSDK.getPayment(transactionId);
        return new TransactionStatus(transactionId, payment.state);
    }
}

// Adaptee 3: Square (yet another different API)
public class SquareClient {
    public SquarePaymentResult pay(SquarePaymentParams params) {
        System.out.println("Square: Processing payment of " + params.amountMoney.amount + 
                          " " + params.amountMoney.currency);
        
        SquarePaymentResult result = new SquarePaymentResult();
        result.paymentId = "sq_" + UUID.randomUUID().toString().substring(0, 8);
        result.status = "COMPLETED";
        result.createdAt = Instant.now();
        
        return result;
    }
    
    public SquareRefundResult refundPayment(String paymentId, SquareMoney amount) {
        System.out.println("Square: Refunding payment " + paymentId);
        
        SquareRefundResult result = new SquareRefundResult();
        result.refundId = "sq_ref_" + UUID.randomUUID().toString().substring(0, 8);
        result.status = "COMPLETED";
        
        return result;
    }
    
    public SquarePaymentResult getPayment(String paymentId) {
        System.out.println("Square: Retrieving payment " + paymentId);
        
        SquarePaymentResult result = new SquarePaymentResult();
        result.paymentId = paymentId;
        result.status = "COMPLETED";
        
        return result;
    }
    
    // Square's classes
    public static class SquarePaymentParams {
        public SquareMoney amountMoney;
        public String sourceId;
        public String idempotencyKey;
    }
    
    public static class SquareMoney {
        public long amount; // In smallest currency unit
        public String currency;
        
        public SquareMoney(long amount, String currency) {
            this.amount = amount;
            this.currency = currency;
        }
    }
    
    public static class SquarePaymentResult {
        public String paymentId;
        public String status;
        public Instant createdAt;
    }
    
    public static class SquareRefundResult {
        public String refundId;
        public String status;
    }
}

// Adapter for Square
public class SquareAdapter implements PaymentProcessor {
    private final SquareClient squareClient;
    private final String accessToken;
    
    public SquareAdapter(String accessToken) {
        this.accessToken = accessToken;
        this.squareClient = new SquareClient();
    }
    
    @Override
    public PaymentResponse processPayment(PaymentRequest request) {
        try {
            // Adapt to Square's format
            SquareClient.SquarePaymentParams params = new SquareClient.SquarePaymentParams();
            
            // Convert to smallest currency unit (cents for USD)
            long amountInCents = (long) (request.getAmount() * 100);
            params.amountMoney = new SquareClient.SquareMoney(amountInCents, request.getCurrency());
            params.sourceId = "cnon:" + request.getCustomerEmail().hashCode();
            params.idempotencyKey = request.getOrderId();
            
            // Call Square API
            SquareClient.SquarePaymentResult result = squareClient.pay(params);
            
            // Adapt response
            boolean success = "COMPLETED".equals(result.status);
            String message = success ? "Square payment completed" : "Square payment " + result.status;
            
            return new PaymentResponse(success, result.paymentId, message);
            
        } catch (Exception e) {
            return new PaymentResponse(false, null, "Square error: " + e.getMessage());
        }
    }
    
    @Override
    public RefundResponse refund(String transactionId, double amount) {
        long amountInCents = (long) (amount * 100);
        SquareClient.SquareMoney refundAmount = new SquareClient.SquareMoney(amountInCents, "USD");
        
        SquareClient.SquareRefundResult result = squareClient.refundPayment(transactionId, refundAmount);
        boolean success = "COMPLETED".equals(result.status);
        
        return new RefundResponse(success, result.refundId);
    }
    
    @Override
    public TransactionStatus checkStatus(String transactionId) {
        SquareClient.SquarePaymentResult result = squareClient.getPayment(transactionId);
        return new TransactionStatus(transactionId, result.status);
    }
}

// Supporting classes
public class RefundResponse {
    private final boolean success;
    private final String refundId;
    
    public RefundResponse(boolean success, String refundId) {
        this.success = success;
        this.refundId = refundId;
    }
    
    public boolean isSuccess() { return success; }
    public String getRefundId() { return refundId; }
}

public class TransactionStatus {
    private final String transactionId;
    private final String status;
    
    public TransactionStatus(String transactionId, String status) {
        this.transactionId = transactionId;
        this.status = status;
    }
    
    public String getTransactionId() { return transactionId; }
    public String getStatus() { return status; }
}
```

**Client Usage:**
```java
public class PaymentService {
    private Map<String, PaymentProcessor> processors;
    
    public PaymentService() {
        processors = new HashMap<>();
        
        // Register different payment processors through adapters
        processors.put("stripe", new StripeAdapter("sk_test_stripe_key"));
        processors.put("paypal", new PayPalAdapter("paypal_client_id", "paypal_secret"));
        processors.put("square", new SquareAdapter("sq_access_token"));
    }
    
    public PaymentResponse processPayment(String gateway, PaymentRequest request) {
        PaymentProcessor processor = processors.get(gateway);
        
        if (processor == null) {
            throw new IllegalArgumentException("Unknown payment gateway: " + gateway);
        }
        
        return processor.processPayment(request);
    }
    
    public void switchGateway(String orderId, double amount) {
        // Try different gateways if one fails
        PaymentRequest request = new PaymentRequest(orderId, amount, "USD", "customer@example.com");
        
        String[] gateways = {"stripe", "paypal", "square"};
        
        for (String gateway : gateways) {
            System.out.println("\nTrying " + gateway + "...");
            PaymentResponse response = processPayment(gateway, request);
            
            if (response.isSuccess()) {
                System.out.println("✓ Payment successful via " + gateway);
                System.out.println("  Transaction ID: " + response.getTransactionId());
                return;
            } else {
                System.out.println("✗ " + gateway + " failed: " + response.getMessage());
            }
        }
        
        System.out.println("All payment gateways failed!");
    }
}

// Usage
PaymentService service = new PaymentService();
service.switchGateway("ORDER-12345", 99.99);

// Output:
// Trying stripe...
// Stripe: Charging 9999 cents in USD
// ✓ Payment successful via stripe
//   Transaction ID: ch_a7b3c9d1
```

**Benefits:**
- **Flexibility:** Switch between payment gateways without changing business logic
- **Maintainability:** Changes to third-party APIs only affect adapters
- **Testability:** Easy to mock adapters for testing
- **Consistency:** Uniform interface for different implementations

**Real-world Examples:**
- **SLF4J:** Adapter for different logging frameworks (Log4j, Logback, JUL)
- **JDBC:** Adapters for different databases (MySQL, PostgreSQL, Oracle)
- **Spring Data:** Adapters for different data stores (JPA, MongoDB, Redis)

---

### 2.2 Decorator Pattern

**Problem:** Add responsibilities to objects dynamically without affecting other objects

**Intent:** Attach additional responsibilities to an object dynamically

**Example: Coffee Shop Beverage System**

```java
// Component interface
public interface Beverage {
    String getDescription();
    double getCost();
    int getCalories();
}

// Concrete component
public class Espresso implements Beverage {
    @Override
    public String getDescription() {
        return "Espresso";
    }
    
    @Override
    public double getCost() {
        return 1.99;
    }
    
    @Override
    public int getCalories() {
        return 5;
    }
}

public class DarkRoast implements Beverage {
    @Override
    public String getDescription() {
        return "Dark Roast Coffee";
    }
    
    @Override
    public double getCost() {
        return 2.49;
    }
    
    @Override
    public int getCalories() {
        return 10;
    }
}

public class Decaf implements Beverage {
    @Override
    public String getDescription() {
        return "Decaf Coffee";
    }
    
    @Override
    public double getCost() {
        return 2.29;
    }
    
    @Override
    public int getCalories() {
        return 8;
    }
}

// Abstract decorator
public abstract class BeverageDecorator implements Beverage {
    protected Beverage beverage;
    
    public BeverageDecorator(Beverage beverage) {
        this.beverage = beverage;
    }
    
    @Override
    public String getDescription() {
        return beverage.getDescription();
    }
    
    @Override
    public double getCost() {
        return beverage.getCost();
    }
    
    @Override
    public int getCalories() {
        return beverage.getCalories();
    }
}

// Concrete decorators
public class Milk extends BeverageDecorator {
    private final MilkType type;
    
    public enum MilkType {
        WHOLE(0.50, 50),
        SKIM(0.40, 30),
        SOY(0.60, 40),
        ALMOND(0.70, 35),
        OAT(0.75, 45);
        
        final double cost;
        final int calories;
        
        MilkType(double cost, int calories) {
            this.cost = cost;
            this.calories = calories;
        }
    }
    
    public Milk(Beverage beverage, MilkType type) {
        super(beverage);
        this.type = type;
    }
    
    public Milk(Beverage beverage) {
        this(beverage, MilkType.WHOLE);
    }
    
    @Override
    public String getDescription() {
        return beverage.getDescription() + ", " + type.name().toLowerCase() + " milk";
    }
    
    @Override
    public double getCost() {
        return beverage.getCost() + type.cost;
    }
    
    @Override
    public int getCalories() {
        return beverage.getCalories() + type.calories;
    }
}

public class Mocha extends BeverageDecorator {
    private final int pumps;
    private static final double COST_PER_PUMP = 0.30;
    private static final int CALORIES_PER_PUMP = 25;
    
    public Mocha(Beverage beverage, int pumps) {
        super(beverage);
        this.pumps = pumps;
    }
    
    public Mocha(Beverage beverage) {
        this(beverage, 1);
    }
    
    @Override
    public String getDescription() {
        return beverage.getDescription() + ", mocha (" + pumps + " pump" + 
               (pumps > 1 ? "s" : "") + ")";
    }
    
    @Override
    public double getCost() {
        return beverage.getCost() + (COST_PER_PUMP * pumps);
    }
    
    @Override
    public int getCalories() {
        return beverage.getCalories() + (CALORIES_PER_PUMP * pumps);
    }
}

public class Whip extends BeverageDecorator {
    private final boolean extraWhip;
    
    public Whip(Beverage beverage, boolean extraWhip) {
        super(beverage);
        this.extraWhip = extraWhip;
    }
    
    public Whip(Beverage beverage) {
        this(beverage, false);
    }
    
    @Override
    public String getDescription() {
        return beverage.getDescription() + ", " + 
               (extraWhip ? "extra " : "") + "whipped cream";
    }
    
    @Override
    public double getCost() {
        return beverage.getCost() + (extraWhip ? 0.80 : 0.60);
    }
    
    @Override
    public int getCalories() {
        return beverage.getCalories() + (extraWhip ? 120 : 80);
    }
}

public class Caramel extends BeverageDecorator {
    private final int pumps;
    private static final double COST_PER_PUMP = 0.35;
    private static final int CALORIES_PER_PUMP = 30;
    
    public Caramel(Beverage beverage, int pumps) {
        super(beverage);
        this.pumps = pumps;
    }
    
    public Caramel(Beverage beverage) {
        this(beverage, 1);
    }
    
    @Override
    public String getDescription() {
        return beverage.getDescription() + ", caramel (" + pumps + " pump" +
               (pumps > 1 ? "s" : "") + ")";
    }
    
    @Override
    public double getCost() {
        return beverage.getCost() + (COST_PER_PUMP * pumps);
    }
    
    @Override
    public int getCalories() {
        return beverage.getCalories() + (CALORIES_PER_PUMP * pumps);
    }
}

public class SugarFree extends BeverageDecorator {
    public SugarFree(Beverage beverage) {
        super(beverage);
    }
    
    @Override
    public String getDescription() {
        return beverage.getDescription() + " (sugar-free)";
    }
    
    @Override
    public double getCost() {
        return beverage.getCost(); // No extra cost
    }
    
    @Override
    public int getCalories() {
        // Sugar-free reduces calories by 30%
        return (int) (beverage.getCalories() * 0.7);
    }
}

public class ExtraShot extends BeverageDecorator {
    private final int shots;
    private static final double COST_PER_SHOT = 0.50;
    private static final int CALORIES_PER_SHOT = 5;
    
    public ExtraShot(Beverage beverage, int shots) {
        super(beverage);
        this.shots = shots;
    }
    
    public ExtraShot(Beverage beverage) {
        this(beverage, 1);
    }
    
    @Override
    public String getDescription() {
        return beverage.getDescription() + ", " + shots + " extra shot" +
               (shots > 1 ? "s" : "");
    }
    
    @Override
    public double getCost() {
        return beverage.getCost() + (COST_PER_SHOT * shots);
    }
    
    @Override
    public int getCalories() {
        return beverage.getCalories() + (CALORIES_PER_SHOT * shots);
    }
}
```

**Usage Examples:**
```java
public class CoffeeShop {
    public void orderBeverages() {
        // Simple espresso
        Beverage beverage1 = new Espresso();
        System.out.println(beverage1.getDescription() + 
                          " $" + String.format("%.2f", beverage1.getCost()) +
                          " (" + beverage1.getCalories() + " cal)");
        
        // Dark roast with milk and sugar
        Beverage beverage2 = new DarkRoast();
        beverage2 = new Milk(beverage2);
        beverage2 = new Mocha(beverage2);
        System.out.println(beverage2.getDescription() + 
                          " $" + String.format("%.2f", beverage2.getCost()) +
                          " (" + beverage2.getCalories() + " cal)");
        
        // Decaf with soy milk, extra mocha, and whipped cream
        Beverage beverage3 = new Decaf();
        beverage3 = new Milk(beverage3, Milk.MilkType.SOY);
        beverage3 = new Mocha(beverage3, 2); // 2 pumps
        beverage3 = new Whip(beverage3);
        System.out.println(beverage3.getDescription() + 
                          " $" + String.format("%.2f", beverage3.getCost()) +
                          " (" + beverage3.getCalories() + " cal)");
        
        // Espresso with double shot, almond milk, caramel, and extra whip
        Beverage beverage4 = new Espresso();
        beverage4 = new ExtraShot(beverage4, 2);
        beverage4 = new Milk(beverage4, Milk.MilkType.ALMOND);
        beverage4 = new Caramel(beverage4, 2);
        beverage4 = new Whip(beverage4, true);
        System.out.println(beverage4.getDescription() + 
                          " $" + String.format("%.2f", beverage4.getCost()) +
                          " (" + beverage4.getCalories() + " cal)");
        
        // Sugar-free dark roast with oat milk
        Beverage beverage5 = new DarkRoast();
        beverage5 = new Milk(beverage5, Milk.MilkType.OAT);
        beverage5 = new SugarFree(beverage5);
        System.out.println(beverage5.getDescription() + 
                          " $" + String.format("%.2f", beverage5.getCost()) +
                          " (" + beverage5.getCalories() + " cal)");
    }
}

// Output:
// Espresso $1.99 (5 cal)
// Dark Roast Coffee, whole milk, mocha (1 pump) $3.29 (85 cal)
// Decaf Coffee, soy milk, mocha (2 pumps), whipped cream $4.09 (178 cal)
// Espresso, 2 extra shots, almond milk, caramel (2 pumps), extra whipped cream $4.79 (235 cal)
// Dark Roast Coffee, oat milk (sugar-free) $3.24 (38 cal)
```

**HTTP Request/Response Decorator Example:**
```java
// Component
public interface HttpClient {
    HttpResponse execute(HttpRequest request);
}

// Concrete component
public class BasicHttpClient implements HttpClient {
    @Override
    public HttpResponse execute(HttpRequest request) {
        System.out.println("Executing: " + request.getMethod() + " " + request.getUrl());
        
        // Simulate HTTP call
        try {
            Thread.sleep(100);
            return new HttpResponse(200, "Response body");
        } catch (InterruptedException e) {
            return new HttpResponse(500, "Error");
        }
    }
}

// Abstract decorator
public abstract class HttpClientDecorator implements HttpClient {
    protected HttpClient client;
    
    public HttpClientDecorator(HttpClient client) {
        this.client = client;
    }
    
    @Override
    public HttpResponse execute(HttpRequest request) {
        return client.execute(request);
    }
}

// Logging decorator
public class LoggingHttpClient extends HttpClientDecorator {
    private static final Logger logger = LoggerFactory.getLogger(LoggingHttpClient.class);
    
    public LoggingHttpClient(HttpClient client) {
        super(client);
    }
    
    @Override
    public HttpResponse execute(HttpRequest request) {
        logger.info("→ Request: {} {}", request.getMethod(), request.getUrl());
        logger.debug("  Headers: {}", request.getHeaders());
        
        long startTime = System.currentTimeMillis();
        HttpResponse response = client.execute(request);
        long duration = System.currentTimeMillis() - startTime;
        
        logger.info("← Response: {} ({}ms)", response.getStatusCode(), duration);
        
        return response;
    }
}

// Retry decorator
public class RetryHttpClient extends HttpClientDecorator {
    private final int maxRetries;
    private final long retryDelayMs;
    
    public RetryHttpClient(HttpClient client, int maxRetries, long retryDelayMs) {
        super(client);
        this.maxRetries = maxRetries;
        this.retryDelayMs = retryDelayMs;
    }
    
    @Override
    public HttpResponse execute(HttpRequest request) {
        int attempt = 0;
        
        while (attempt <= maxRetries) {
            try {
                HttpResponse response = client.execute(request);
                
                // Retry on 5xx errors
                if (response.getStatusCode() < 500 || attempt == maxRetries) {
                    return response;
                }
                
                System.out.println("Retry attempt " + (attempt + 1) + " after " + 
                                  retryDelayMs + "ms");
                Thread.sleep(retryDelayMs);
                
            } catch (Exception e) {
                if (attempt == maxRetries) {
                    throw new RuntimeException("Max retries exceeded", e);
                }
                
                try {
                    Thread.sleep(retryDelayMs);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    throw new RuntimeException("Retry interrupted", ie);
                }
            }
            
            attempt++;
        }
        
        throw new RuntimeException("Should not reach here");
    }
}

// Caching decorator
public class CachingHttpClient extends HttpClientDecorator {
    private final Map<String, CachedResponse> cache;
    private final long ttlMs;
    
    public CachingHttpClient(HttpClient client, long ttlMs) {
        super(client);
        this.cache = new ConcurrentHashMap<>();
        this.ttlMs = ttlMs;
    }
    
    @Override
    public HttpResponse execute(HttpRequest request) {
        // Only cache GET requests
        if (!"GET".equals(request.getMethod())) {
            return client.execute(request);
        }
        
        String cacheKey = request.getUrl();
        CachedResponse cached = cache.get(cacheKey);
        
        // Check if cached and not expired
        if (cached != null && !cached.isExpired()) {
            System.out.println("Cache HIT: " + cacheKey);
            return cached.response;
        }
        
        System.out.println("Cache MISS: " + cacheKey);
        HttpResponse response = client.execute(request);
        
        // Cache successful responses
        if (response.getStatusCode() == 200) {
            cache.put(cacheKey, new CachedResponse(response, System.currentTimeMillis() + ttlMs));
        }
        
        return response;
    }
    
    private static class CachedResponse {
        final HttpResponse response;
        final long expiresAt;
        
        CachedResponse(HttpResponse response, long expiresAt) {
            this.response = response;
            this.expiresAt = expiresAt;
        }
        
        boolean isExpired() {
            return System.currentTimeMillis() > expiresAt;
        }
    }
}

// Authentication decorator
public class AuthHttpClient extends HttpClientDecorator {
    private final String token;
    
    public AuthHttpClient(HttpClient client, String token) {
        super(client);
        this.token = token;
    }
    
    @Override
    public HttpResponse execute(HttpRequest request) {
        // Add authorization header
        HttpRequest authenticatedRequest = request.copy();
        authenticatedRequest.addHeader("Authorization", "Bearer " + token);
        
        return client.execute(authenticatedRequest);
    }
}

// Rate limiting decorator
public class RateLimitedHttpClient extends HttpClientDecorator {
    private final int requestsPerSecond;
    private final Queue<Long> requestTimes;
    
    public RateLimitedHttpClient(HttpClient client, int requestsPerSecond) {
        super(client);
        this.requestsPerSecond = requestsPerSecond;
        this.requestTimes = new ConcurrentLinkedQueue<>();
    }
    
    @Override
    public HttpResponse execute(HttpRequest request) {
        waitIfNecessary();
        requestTimes.offer(System.currentTimeMillis());
        return client.execute(request);
    }
    
    private void waitIfNecessary() {
        long now = System.currentTimeMillis();
        long oneSecondAgo = now - 1000;
        
        // Remove requests older than 1 second
        while (!requestTimes.isEmpty() && requestTimes.peek() < oneSecondAgo) {
            requestTimes.poll();
        }
        
        // Wait if rate limit exceeded
        if (requestTimes.size() >= requestsPerSecond) {
            long oldestRequest = requestTimes.peek();
            long waitTime = 1000 - (now - oldestRequest);
            
            if (waitTime > 0) {
                System.out.println("Rate limit: waiting " + waitTime + "ms");
                try {
                    Thread.sleep(waitTime);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
        }
    }
}
```

**Compose Multiple Decorators:**
```java
public class HttpClientExample {
    public void demonstrateDecorators() {
        // Build a fully decorated HTTP client
        HttpClient client = new BasicHttpClient();
        
        // Add logging
        client = new LoggingHttpClient(client);
        
        // Add caching (5 second TTL)
        client = new CachingHttpClient(client, 5000);
        
        // Add retries (3 attempts, 1 second delay)
        client = new RetryHttpClient(client, 3, 1000);
        
        // Add authentication
        client = new AuthHttpClient(client, "jwt_token_123");
        
        // Add rate limiting (10 requests per second)
        client = new RateLimitedHttpClient(client, 10);
        
        // Now use the client
        HttpRequest request = new HttpRequest("GET", "https://api.example.com/users");
        HttpResponse response = client.execute(request);
        
        System.out.println("Status: " + response.getStatusCode());
        System.out.println("Body: " + response.getBody());
    }
}
```

**Benefits:**
- **Flexibility:** Add/remove responsibilities at runtime
- **Open/Closed Principle:** Extend functionality without modifying existing code
- **Single Responsibility:** Each decorator has one job
- **Composability:** Stack multiple decorators

**Real-world Examples:**
- **Java I/O:** `new BufferedReader(new FileReader(file))`
- **Spring:** `@Transactional`, `@Cacheable`, `@Async` are decorators
- **Servlet Filters:** `doFilter()` wraps request/response
- **Hibernate:** Session proxies add lazy loading, caching

---

### 2.3 Proxy Pattern

**Problem:** Control access to an object, add behavior before/after accessing it

**Intent:** Provide a surrogate or placeholder for another object

**Types of Proxies:**

**1. Virtual Proxy (Lazy Loading):**
```java
// Subject interface
public interface Image {
    void display();
    int getWidth();
    int getHeight();
    long getFileSize();
}

// Real subject (expensive to create)
public class RealImage implements Image {
    private final String filename;
    private final byte[] imageData;
    private final int width;
    private final int height;
    
    public RealImage(String filename) {
        this.filename = filename;
        System.out.println("Loading image from disk: " + filename);
        
        // Simulate expensive loading operation
        try {
            Thread.sleep(2000); // 2 second load time
            
            // Simulate reading file
            this.imageData = new byte[1024 * 1024]; // 1MB
            this.width = 1920;
            this.height = 1080;
            
            System.out.println("✓ Image loaded: " + filename + " (" + imageData.length + " bytes)");
            
        } catch (InterruptedException e) {
            throw new RuntimeException("Failed to load image", e);
        }
    }
    
    @Override
    public void display() {
        System.out.println("Displaying image: " + filename + " (" + width + "x" + height + ")");
        // Actual rendering logic here
    }
    
    @Override
    public int getWidth() {
        return width;
    }
    
    @Override
    public int getHeight() {
        return height;
    }
    
    @Override
    public long getFileSize() {
        return imageData.length;
    }
}

// Virtual proxy (lazy loading)
public class ImageProxy implements Image {
    private final String filename;
    private RealImage realImage;
    
    public ImageProxy(String filename) {
        this.filename = filename;
        System.out.println("ImageProxy created for: " + filename + " (not loaded yet)");
    }
    
    @Override
    public void display() {
        // Load image only when needed
        if (realImage == null) {
            realImage = new RealImage(filename);
        }
        realImage.display();
    }
    
    @Override
    public int getWidth() {
        // For metadata, we could cache without loading full image
        // For simplicity, load the image
        if (realImage == null) {
            realImage = new RealImage(filename);
        }
        return realImage.getWidth();
    }
    
    @Override
    public int getHeight() {
        if (realImage == null) {
            realImage = new RealImage(filename);
        }
        return realImage.getHeight();
    }
    
    @Override
    public long getFileSize() {
        if (realImage == null) {
            realImage = new RealImage(filename);
        }
        return realImage.getFileSize();
    }
}

// Usage
public class ImageGallery {
    public void demonstrateLazyLoading() {
        // Create proxies instantly (no loading)
        List<Image> images = List.of(
            new ImageProxy("photo1.jpg"),
            new ImageProxy("photo2.jpg"),
            new ImageProxy("photo3.jpg"),
            new ImageProxy("photo4.jpg"),
            new ImageProxy("photo5.jpg")
        );
        
        System.out.println("\n--- All proxies created instantly ---\n");
        
        // Images load only when accessed
        System.out.println("Displaying first image:");
        images.get(0).display();
        
        System.out.println("\nDisplaying third image:");
        images.get(2).display();
        
        // Other images never loaded (saved 6 seconds!)
    }
}
```

**2. Protection Proxy (Access Control):**
```java
// Subject interface
public interface DocumentService {
    Document readDocument(String documentId);
    void updateDocument(String documentId, String content);
    void deleteDocument(String documentId);
    void shareDocument(String documentId, String userId);
}

public class Document {
    private final String id;
    private String content;
    private final String ownerId;
    private final List<String> sharedWith;
    
    public Document(String id, String content, String ownerId) {
        this.id = id;
        this.content = content;
        this.ownerId = ownerId;
        this.sharedWith = new ArrayList<>();
    }
    
    // Getters and setters
    public String getId() { return id; }
    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }
    public String getOwnerId() { return ownerId; }
    public List<String> getSharedWith() { return sharedWith; }
    public void addSharedUser(String userId) { sharedWith.add(userId); }
}

// Real subject
public class RealDocumentService implements DocumentService {
    private final Map<String, Document> documents = new HashMap<>();
    
    public RealDocumentService() {
        // Sample documents
        documents.put("doc1", new Document("doc1", "Confidential report", "user1"));
        documents.put("doc2", new Document("doc2", "Public announcement", "user2"));
        documents.put("doc3", new Document("doc3", "Team notes", "user3"));
    }
    
    @Override
    public Document readDocument(String documentId) {
        Document doc = documents.get(documentId);
        if (doc == null) {
            throw new IllegalArgumentException("Document not found: " + documentId);
        }
        return doc;
    }
    
    @Override
    public void updateDocument(String documentId, String content) {
        Document doc = documents.get(documentId);
        if (doc == null) {
            throw new IllegalArgumentException("Document not found: " + documentId);
        }
        doc.setContent(content);
        System.out.println("Document updated: " + documentId);
    }
    
    @Override
    public void deleteDocument(String documentId) {
        Document doc = documents.remove(documentId);
        if (doc == null) {
            throw new IllegalArgumentException("Document not found: " + documentId);
        }
        System.out.println("Document deleted: " + documentId);
    }
    
    @Override
    public void shareDocument(String documentId, String userId) {
        Document doc = documents.get(documentId);
        if (doc == null) {
            throw new IllegalArgumentException("Document not found: " + documentId);
        }
        doc.addSharedUser(userId);
        System.out.println("Document " + documentId + " shared with " + userId);
    }
}

// Protection proxy
public class SecureDocumentService implements DocumentService {
    private final DocumentService realService;
    private final String currentUserId;
    
    public SecureDocumentService(DocumentService realService, String currentUserId) {
        this.realService = realService;
        this.currentUserId = currentUserId;
    }
    
    @Override
    public Document readDocument(String documentId) {
        Document doc = realService.readDocument(documentId);
        
        // Check if user has access
        if (!hasReadAccess(doc)) {
            throw new SecurityException("Access denied: User " + currentUserId + 
                                       " cannot read document " + documentId);
        }
        
        System.out.println("✓ Access granted: " + currentUserId + " reading " + documentId);
        return doc;
    }
    
    @Override
    public void updateDocument(String documentId, String content) {
        Document doc = realService.readDocument(documentId);
        
        // Only owner or shared users can update
        if (!hasWriteAccess(doc)) {
            throw new SecurityException("Access denied: User " + currentUserId + 
                                       " cannot update document " + documentId);
        }
        
        System.out.println("✓ Access granted: " + currentUserId + " updating " + documentId);
        realService.updateDocument(documentId, content);
    }
    
    @Override
    public void deleteDocument(String documentId) {
        Document doc = realService.readDocument(documentId);
        
        // Only owner can delete
        if (!doc.getOwnerId().equals(currentUserId)) {
            throw new SecurityException("Access denied: Only owner can delete document " + documentId);
        }
        
        System.out.println("✓ Access granted: " + currentUserId + " deleting " + documentId);
        realService.deleteDocument(documentId);
    }
    
    @Override
    public void shareDocument(String documentId, String userId) {
        Document doc = realService.readDocument(documentId);
        
        // Only owner can share
        if (!doc.getOwnerId().equals(currentUserId)) {
            throw new SecurityException("Access denied: Only owner can share document " + documentId);
        }
        
        System.out.println("✓ Access granted: " + currentUserId + " sharing " + documentId);
        realService.shareDocument(documentId, userId);
    }
    
    private boolean hasReadAccess(Document doc) {
        return doc.getOwnerId().equals(currentUserId) || 
               doc.getSharedWith().contains(currentUserId);
    }
    
    private boolean hasWriteAccess(Document doc) {
        return doc.getOwnerId().equals(currentUserId) || 
               doc.getSharedWith().contains(currentUserId);
    }
}

// Usage
public class DocumentManagement {
    public void demonstrateAccessControl() {
        DocumentService realService = new RealDocumentService();
        
        // User1 tries to access their own document
        DocumentService user1Service = new SecureDocumentService(realService, "user1");
        try {
            Document doc = user1Service.readDocument("doc1");
            System.out.println("Content: " + doc.getContent());
        } catch (SecurityException e) {
            System.out.println("✗ " + e.getMessage());
        }
        
        // User1 tries to access user2's document (should fail)
        try {
            user1Service.readDocument("doc2");
        } catch (SecurityException e) {
            System.out.println("✗ " + e.getMessage());
        }
        
        // User2 shares document with user1
        DocumentService user2Service = new SecureDocumentService(realService, "user2");
        user2Service.shareDocument("doc2", "user1");
        
        // Now user1 can access doc2
        try {
            Document doc = user1Service.readDocument("doc2");
            System.out.println("Content: " + doc.getContent());
        } catch (SecurityException e) {
            System.out.println("✗ " + e.getMessage());
        }
        
        // User1 tries to delete doc2 (should fail - not owner)
        try {
            user1Service.deleteDocument("doc2");
        } catch (SecurityException e) {
            System.out.println("✗ " + e.getMessage());
        }
    }
}
```

**3. Remote Proxy (Network Communication):**
```java
// Subject interface
public interface UserService {
    User getUserById(long userId);
    List<User> getAllUsers();
    User createUser(User user);
    void updateUser(User user);
    void deleteUser(long userId);
}

public class User {
    private long id;
    private String name;
    private String email;
    private String role;
    
    // Constructors, getters, setters
    public User(long id, String name, String email, String role) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.role = role;
    }
    
    // Getters
    public long getId() { return id; }
    public String getName() { return name; }
    public String getEmail() { return email; }
    public String getRole() { return role; }
    
    @Override
    public String toString() {
        return "User{id=" + id + ", name='" + name + "', email='" + email + "'}";
    }
}

// Remote proxy (hides network complexity)
public class RemoteUserServiceProxy implements UserService {
    private final String baseUrl;
    private final HttpClient httpClient;
    
    public RemoteUserServiceProxy(String baseUrl) {
        this.baseUrl = baseUrl;
        this.httpClient = HttpClient.newHttpClient();
    }
    
    @Override
    public User getUserById(long userId) {
        try {
            String url = baseUrl + "/users/" + userId;
            System.out.println("→ GET " + url);
            
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .GET()
                .build();
            
            HttpResponse<String> response = httpClient.send(request, 
                HttpResponse.BodyHandlers.ofString());
            
            System.out.println("← " + response.statusCode());
            
            if (response.statusCode() == 200) {
                return parseUser(response.body());
            } else {
                throw new RuntimeException("Failed to get user: " + response.statusCode());
            }
            
        } catch (Exception e) {
            throw new RuntimeException("Network error", e);
        }
    }
    
    @Override
    public List<User> getAllUsers() {
        try {
            String url = baseUrl + "/users";
            System.out.println("→ GET " + url);
            
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .GET()
                .build();
            
            HttpResponse<String> response = httpClient.send(request, 
                HttpResponse.BodyHandlers.ofString());
            
            System.out.println("← " + response.statusCode());
            
            if (response.statusCode() == 200) {
                return parseUserList(response.body());
            } else {
                throw new RuntimeException("Failed to get users: " + response.statusCode());
            }
            
        } catch (Exception e) {
            throw new RuntimeException("Network error", e);
        }
    }
    
    @Override
    public User createUser(User user) {
        try {
            String url = baseUrl + "/users";
            System.out.println("→ POST " + url);
            
            String jsonBody = toJson(user);
            
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
                .build();
            
            HttpResponse<String> response = httpClient.send(request, 
                HttpResponse.BodyHandlers.ofString());
            
            System.out.println("← " + response.statusCode());
            
            if (response.statusCode() == 201) {
                return parseUser(response.body());
            } else {
                throw new RuntimeException("Failed to create user: " + response.statusCode());
            }
            
        } catch (Exception e) {
            throw new RuntimeException("Network error", e);
        }
    }
    
    @Override
    public void updateUser(User user) {
        try {
            String url = baseUrl + "/users/" + user.getId();
            System.out.println("→ PUT " + url);
            
            String jsonBody = toJson(user);
            
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Content-Type", "application/json")
                .PUT(HttpRequest.BodyPublishers.ofString(jsonBody))
                .build();
            
            HttpResponse<String> response = httpClient.send(request, 
                HttpResponse.BodyHandlers.ofString());
            
            System.out.println("← " + response.statusCode());
            
            if (response.statusCode() != 200) {
                throw new RuntimeException("Failed to update user: " + response.statusCode());
            }
            
        } catch (Exception e) {
            throw new RuntimeException("Network error", e);
        }
    }
    
    @Override
    public void deleteUser(long userId) {
        try {
            String url = baseUrl + "/users/" + userId;
            System.out.println("→ DELETE " + url);
            
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .DELETE()
                .build();
            
            HttpResponse<String> response = httpClient.send(request, 
                HttpResponse.BodyHandlers.ofString());
            
            System.out.println("← " + response.statusCode());
            
            if (response.statusCode() != 204) {
                throw new RuntimeException("Failed to delete user: " + response.statusCode());
            }
            
        } catch (Exception e) {
            throw new RuntimeException("Network error", e);
        }
    }
    
    private User parseUser(String json) {
        // Simplified JSON parsing (use Jackson/Gson in production)
        return new User(1, "John Doe", "john@example.com", "admin");
    }
    
    private List<User> parseUserList(String json) {
        // Simplified JSON parsing
        return List.of(
            new User(1, "John Doe", "john@example.com", "admin"),
            new User(2, "Jane Smith", "jane@example.com", "user")
        );
    }
    
    private String toJson(User user) {
        // Simplified JSON serialization
        return String.format("{\"name\":\"%s\",\"email\":\"%s\",\"role\":\"%s\"}", 
                           user.getName(), user.getEmail(), user.getRole());
    }
}

// Usage
public class RemoteServiceExample {
    public void demonstrateRemoteProxy() {
        // Client doesn't know about HTTP, JSON, network errors, etc.
        UserService userService = new RemoteUserServiceProxy("https://api.example.com");
        
        // Use service as if it's local
        User user = userService.getUserById(1);
        System.out.println("User: " + user);
        
        List<User> users = userService.getAllUsers();
        System.out.println("All users: " + users.size());
        
        User newUser = new User(0, "Bob Johnson", "bob@example.com", "user");
        User created = userService.createUser(newUser);
        System.out.println("Created: " + created);
    }
}
```

**4. Caching Proxy:**
```java
public class CachingUserServiceProxy implements UserService {
    private final UserService realService;
    private final Map<Long, CachedUser> userCache;
    private final long cacheTtlMs;
    
    public CachingUserServiceProxy(UserService realService, long cacheTtlMs) {
        this.realService = realService;
        this.userCache = new ConcurrentHashMap<>();
        this.cacheTtlMs = cacheTtlMs;
    }
    
    @Override
    public User getUserById(long userId) {
        CachedUser cached = userCache.get(userId);
        
        // Check cache
        if (cached != null && !cached.isExpired()) {
            System.out.println("Cache HIT: User " + userId);
            return cached.user;
        }
        
        // Cache miss - fetch from real service
        System.out.println("Cache MISS: User " + userId);
        User user = realService.getUserById(userId);
        
        // Store in cache
        userCache.put(userId, new CachedUser(user, System.currentTimeMillis() + cacheTtlMs));
        
        return user;
    }
    
    @Override
    public List<User> getAllUsers() {
        // Don't cache list queries (too complex)
        return realService.getAllUsers();
    }
    
    @Override
    public User createUser(User user) {
        User created = realService.createUser(user);
        // Invalidate cache on create
        userCache.clear();
        return created;
    }
    
    @Override
    public void updateUser(User user) {
        realService.updateUser(user);
        // Invalidate specific user cache
        userCache.remove(user.getId());
    }
    
    @Override
    public void deleteUser(long userId) {
        realService.deleteUser(userId);
        // Invalidate specific user cache
        userCache.remove(userId);
    }
    
    private static class CachedUser {
        final User user;
        final long expiresAt;
        
        CachedUser(User user, long expiresAt) {
            this.user = user;
            this.expiresAt = expiresAt;
        }
        
        boolean isExpired() {
            return System.currentTimeMillis() > expiresAt;
        }
    }
}

// Combine remote proxy with caching proxy
public class OptimizedUserService {
    public static UserService create(String baseUrl, long cacheTtlMs) {
        // Remote proxy handles network
        UserService remoteService = new RemoteUserServiceProxy(baseUrl);
        
        // Caching proxy reduces network calls
        return new CachingUserServiceProxy(remoteService, cacheTtlMs);
    }
}

// Usage
UserService service = OptimizedUserService.create("https://api.example.com", 60000);

// First call - network request
User user1 = service.getUserById(1); // Cache MISS

// Second call - from cache
User user2 = service.getUserById(1); // Cache HIT (no network call)

// After 60 seconds - cache expired
Thread.sleep(60000);
User user3 = service.getUserById(1); // Cache MISS (expired)
```

**Benefits:**
- **Lazy initialization:** Virtual proxy defers expensive operations
- **Access control:** Protection proxy enforces security
- **Remote access:** Remote proxy hides network complexity
- **Caching:** Caching proxy improves performance
- **Logging:** Logging proxy tracks access

**Real-world Examples:**
- **Hibernate:** Entity proxies for lazy loading
- **Spring AOP:** Method proxies for transactions, security
- **RMI/RPC:** Remote proxies for distributed systems
- **CDN:** Caching proxy for static assets

---

**End of Part 2 - Section 2**

**Coming in next section:** Facade, Flyweight, Composite patterns, then Behavioral patterns (Strategy, Observer, Command, etc.)

**Lines so far: ~2,000**