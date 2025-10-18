# Design Patterns - Part 3

**Continued from Part 2 (11-Design-Patterns-PART2.md)**

---

## 2.4 Facade Pattern

**Problem:** Complex subsystem with many classes - need simplified interface

**Intent:** Provide unified interface to a set of interfaces in a subsystem

**Example: Home Theater System**

```java
// Complex subsystem components
public class DVDPlayer {
    public void on() {
        System.out.println("DVD Player: Powering on");
    }
    
    public void off() {
        System.out.println("DVD Player: Powering off");
    }
    
    public void play(String movie) {
        System.out.println("DVD Player: Playing '" + movie + "'");
    }
    
    public void stop() {
        System.out.println("DVD Player: Stopping playback");
    }
    
    public void eject() {
        System.out.println("DVD Player: Ejecting disc");
    }
}

public class Projector {
    public void on() {
        System.out.println("Projector: Powering on");
    }
    
    public void off() {
        System.out.println("Projector: Powering off");
    }
    
    public void setInput(String input) {
        System.out.println("Projector: Setting input to " + input);
    }
    
    public void wideScreenMode() {
        System.out.println("Projector: Setting widescreen mode (16:9)");
    }
}

public class SoundSystem {
    public void on() {
        System.out.println("Sound System: Powering on");
    }
    
    public void off() {
        System.out.println("Sound System: Powering off");
    }
    
    public void setVolume(int level) {
        System.out.println("Sound System: Setting volume to " + level);
    }
    
    public void setSurroundSound() {
        System.out.println("Sound System: Setting 5.1 surround sound");
    }
}

public class Lights {
    public void dim(int level) {
        System.out.println("Lights: Dimming to " + level + "%");
    }
    
    public void on() {
        System.out.println("Lights: Turning on to 100%");
    }
}

public class Screen {
    public void down() {
        System.out.println("Screen: Lowering screen");
    }
    
    public void up() {
        System.out.println("Screen: Raising screen");
    }
}

public class PopcornMaker {
    public void on() {
        System.out.println("Popcorn Maker: Powering on");
    }
    
    public void off() {
        System.out.println("Popcorn Maker: Powering off");
    }
    
    public void pop() {
        System.out.println("Popcorn Maker: Popping corn");
    }
}

// Facade - simplified interface
public class HomeTheaterFacade {
    private final DVDPlayer dvd;
    private final Projector projector;
    private final SoundSystem sound;
    private final Lights lights;
    private final Screen screen;
    private final PopcornMaker popcorn;
    
    public HomeTheaterFacade(DVDPlayer dvd, Projector projector, SoundSystem sound,
                             Lights lights, Screen screen, PopcornMaker popcorn) {
        this.dvd = dvd;
        this.projector = projector;
        this.sound = sound;
        this.lights = lights;
        this.screen = screen;
        this.popcorn = popcorn;
    }
    
    // Simple method hides complex subsystem interactions
    public void watchMovie(String movie) {
        System.out.println("\n=== Get ready to watch a movie ===\n");
        
        popcorn.on();
        popcorn.pop();
        
        lights.dim(10);
        
        screen.down();
        
        projector.on();
        projector.setInput("DVD");
        projector.wideScreenMode();
        
        sound.on();
        sound.setSurroundSound();
        sound.setVolume(50);
        
        dvd.on();
        dvd.play(movie);
        
        System.out.println("\n=== Enjoy your movie! ===\n");
    }
    
    public void endMovie() {
        System.out.println("\n=== Shutting down theater ===\n");
        
        popcorn.off();
        lights.on();
        screen.up();
        
        dvd.stop();
        dvd.eject();
        dvd.off();
        
        sound.off();
        projector.off();
        
        System.out.println("\n=== Movie time is over ===\n");
    }
    
    // Additional convenience methods
    public void watchTV() {
        System.out.println("\n=== Setting up TV mode ===\n");
        
        lights.dim(30);
        projector.on();
        projector.setInput("HDMI");
        sound.on();
        sound.setVolume(30);
    }
    
    public void listenToMusic() {
        System.out.println("\n=== Setting up music mode ===\n");
        
        lights.dim(50);
        sound.on();
        sound.setVolume(40);
    }
}

// Client usage
public class MovieNight {
    public static void main(String[] args) {
        // Create subsystem components
        DVDPlayer dvd = new DVDPlayer();
        Projector projector = new Projector();
        SoundSystem sound = new SoundSystem();
        Lights lights = new Lights();
        Screen screen = new Screen();
        PopcornMaker popcorn = new PopcornMaker();
        
        // Create facade
        HomeTheaterFacade homeTheater = new HomeTheaterFacade(
            dvd, projector, sound, lights, screen, popcorn
        );
        
        // Simple interface - one method instead of 10+
        homeTheater.watchMovie("The Matrix");
        
        // ... movie plays ...
        
        homeTheater.endMovie();
    }
}
```

**Banking System Facade Example:**

```java
// Subsystem classes
public class AccountService {
    public boolean accountExists(String accountNumber) {
        System.out.println("Checking if account " + accountNumber + " exists");
        return true;
    }
    
    public double getBalance(String accountNumber) {
        System.out.println("Getting balance for account " + accountNumber);
        return 1000.0;
    }
    
    public void debit(String accountNumber, double amount) {
        System.out.println("Debiting $" + amount + " from account " + accountNumber);
    }
    
    public void credit(String accountNumber, double amount) {
        System.out.println("Crediting $" + amount + " to account " + accountNumber);
    }
}

public class SecurityService {
    public boolean authenticateUser(String username, String password) {
        System.out.println("Authenticating user: " + username);
        return true; // Simplified
    }
    
    public boolean authorizeTransaction(String username, String transactionType, double amount) {
        System.out.println("Authorizing " + transactionType + " of $" + amount + " for " + username);
        return amount <= 10000; // Daily limit
    }
}

public class FraudDetectionService {
    public boolean checkForFraud(String accountNumber, double amount, String location) {
        System.out.println("Checking for fraud: Account " + accountNumber + 
                          ", Amount $" + amount + ", Location " + location);
        
        // Suspicious if large amount from unusual location
        return amount > 5000 && location.contains("Nigeria");
    }
}

public class NotificationService {
    public void sendEmail(String email, String message) {
        System.out.println("Sending email to " + email + ": " + message);
    }
    
    public void sendSMS(String phone, String message) {
        System.out.println("Sending SMS to " + phone + ": " + message);
    }
}

public class TransactionLogger {
    public void logTransaction(String accountNumber, String type, double amount, boolean success) {
        System.out.println("Logging transaction: " + type + " $" + amount + 
                          " for account " + accountNumber + " - " + 
                          (success ? "SUCCESS" : "FAILED"));
    }
}

// Facade
public class BankingFacade {
    private final AccountService accountService;
    private final SecurityService securityService;
    private final FraudDetectionService fraudDetection;
    private final NotificationService notificationService;
    private final TransactionLogger transactionLogger;
    
    public BankingFacade() {
        this.accountService = new AccountService();
        this.securityService = new SecurityService();
        this.fraudDetection = new FraudDetectionService();
        this.notificationService = new NotificationService();
        this.transactionLogger = new TransactionLogger();
    }
    
    public TransferResult transfer(String username, String password, 
                                   String fromAccount, String toAccount, 
                                   double amount, String location) {
        
        System.out.println("\n=== Processing Transfer ===\n");
        
        // Step 1: Authenticate user
        if (!securityService.authenticateUser(username, password)) {
            transactionLogger.logTransaction(fromAccount, "TRANSFER", amount, false);
            return new TransferResult(false, "Authentication failed");
        }
        
        // Step 2: Check account exists
        if (!accountService.accountExists(fromAccount) || !accountService.accountExists(toAccount)) {
            transactionLogger.logTransaction(fromAccount, "TRANSFER", amount, false);
            return new TransferResult(false, "Invalid account");
        }
        
        // Step 3: Check balance
        double balance = accountService.getBalance(fromAccount);
        if (balance < amount) {
            transactionLogger.logTransaction(fromAccount, "TRANSFER", amount, false);
            return new TransferResult(false, "Insufficient funds");
        }
        
        // Step 4: Authorize transaction
        if (!securityService.authorizeTransaction(username, "TRANSFER", amount)) {
            transactionLogger.logTransaction(fromAccount, "TRANSFER", amount, false);
            return new TransferResult(false, "Transaction not authorized (limit exceeded)");
        }
        
        // Step 5: Fraud detection
        if (fraudDetection.checkForFraud(fromAccount, amount, location)) {
            transactionLogger.logTransaction(fromAccount, "TRANSFER", amount, false);
            notificationService.sendEmail(username + "@bank.com", 
                                         "Suspicious transaction blocked");
            return new TransferResult(false, "Transaction blocked - possible fraud");
        }
        
        // Step 6: Execute transfer
        accountService.debit(fromAccount, amount);
        accountService.credit(toAccount, amount);
        
        // Step 7: Log and notify
        transactionLogger.logTransaction(fromAccount, "TRANSFER", amount, true);
        notificationService.sendEmail(username + "@bank.com", 
                                     "Transfer of $" + amount + " completed");
        
        System.out.println("\n=== Transfer Successful ===\n");
        return new TransferResult(true, "Transfer completed successfully");
    }
    
    public double checkBalance(String username, String password, String accountNumber) {
        if (!securityService.authenticateUser(username, password)) {
            throw new SecurityException("Authentication failed");
        }
        
        return accountService.getBalance(accountNumber);
    }
}

public class TransferResult {
    private final boolean success;
    private final String message;
    
    public TransferResult(boolean success, String message) {
        this.success = success;
        this.message = message;
    }
    
    public boolean isSuccess() { return success; }
    public String getMessage() { return message; }
}

// Usage
public class BankingApp {
    public static void main(String[] args) {
        BankingFacade bank = new BankingFacade();
        
        // Simple interface - one method instead of calling 7+ services
        TransferResult result = bank.transfer(
            "john_doe", "password123",
            "ACC-001", "ACC-002",
            500.0, "New York"
        );
        
        System.out.println("Result: " + result.getMessage());
        
        // Check balance
        double balance = bank.checkBalance("john_doe", "password123", "ACC-001");
        System.out.println("New balance: $" + balance);
    }
}
```

**Benefits:**
- **Simplified interface:** Hide complex subsystem
- **Decoupling:** Client doesn't depend on subsystem classes
- **Layered architecture:** Facade provides entry point to each layer
- **Flexibility:** Can change subsystem without affecting clients

**Real-world Examples:**
- **SLF4J:** Facade for logging frameworks
- **JDBC:** Facade for database access
- **Spring Framework:** Many facades (`JdbcTemplate`, `RestTemplate`)
- **javax.faces:** JSF is facade for Servlet API

---

### 2.5 Flyweight Pattern

**Problem:** Too many objects consuming memory, many share common state

**Intent:** Share common state (intrinsic) among multiple objects to save memory

**Example: Text Editor Character Rendering**

```java
// Flyweight interface
public interface CharacterStyle {
    void render(char character, int x, int y);
}

// Concrete flyweight (intrinsic state - shared)
public class CharacterStyleImpl implements CharacterStyle {
    private final String fontFamily;
    private final int fontSize;
    private final String color;
    private final boolean bold;
    private final boolean italic;
    
    public CharacterStyleImpl(String fontFamily, int fontSize, String color, 
                             boolean bold, boolean italic) {
        this.fontFamily = fontFamily;
        this.fontSize = fontSize;
        this.color = color;
        this.bold = bold;
        this.italic = italic;
        
        // Simulate expensive object creation
        System.out.println("Creating new CharacterStyle: " + this);
    }
    
    @Override
    public void render(char character, int x, int y) {
        // Extrinsic state (position, character) passed as parameters
        String style = (bold ? "bold " : "") + (italic ? "italic " : "");
        System.out.printf("Rendering '%c' at (%d,%d) with %s%s %dpt in %s%n",
                         character, x, y, style, fontFamily, fontSize, color);
    }
    
    @Override
    public String toString() {
        return String.format("%s %dpt %s%s%s", 
                           fontFamily, fontSize, color,
                           bold ? " bold" : "",
                           italic ? " italic" : "");
    }
    
    // Getters
    public String getFontFamily() { return fontFamily; }
    public int getFontSize() { return fontSize; }
    public String getColor() { return color; }
    public boolean isBold() { return bold; }
    public boolean isItalic() { return italic; }
}

// Flyweight factory
public class CharacterStyleFactory {
    private final Map<String, CharacterStyle> styles = new HashMap<>();
    
    public CharacterStyle getStyle(String fontFamily, int fontSize, String color,
                                   boolean bold, boolean italic) {
        String key = makeKey(fontFamily, fontSize, color, bold, italic);
        
        return styles.computeIfAbsent(key, k -> 
            new CharacterStyleImpl(fontFamily, fontSize, color, bold, italic)
        );
    }
    
    private String makeKey(String fontFamily, int fontSize, String color, 
                          boolean bold, boolean italic) {
        return String.format("%s|%d|%s|%b|%b", fontFamily, fontSize, color, bold, italic);
    }
    
    public int getStyleCount() {
        return styles.size();
    }
    
    public void printStatistics() {
        System.out.println("\n=== Flyweight Statistics ===");
        System.out.println("Total unique styles: " + styles.size());
        System.out.println("Styles in cache:");
        styles.values().forEach(style -> System.out.println("  - " + style));
    }
}

// Client class using flyweight
public class TextCharacter {
    private final char character;
    private final int x, y;
    private final CharacterStyle style;
    
    public TextCharacter(char character, int x, int y, CharacterStyle style) {
        this.character = character;
        this.x = x;
        this.y = y;
        this.style = style;
    }
    
    public void draw() {
        style.render(character, x, y);
    }
}

// Text document
public class TextDocument {
    private final List<TextCharacter> characters = new ArrayList<>();
    private final CharacterStyleFactory styleFactory = new CharacterStyleFactory();
    
    public void addText(String text, int startX, int startY, 
                       String fontFamily, int fontSize, String color,
                       boolean bold, boolean italic) {
        
        // Get shared style (flyweight)
        CharacterStyle style = styleFactory.getStyle(fontFamily, fontSize, color, bold, italic);
        
        // Create character objects with extrinsic state (position, character)
        int x = startX;
        for (char c : text.toCharArray()) {
            characters.add(new TextCharacter(c, x, startY, style));
            x += fontSize; // Simple spacing
        }
    }
    
    public void render() {
        System.out.println("\n=== Rendering Document ===\n");
        characters.forEach(TextCharacter::draw);
        styleFactory.printStatistics();
    }
    
    public void printMemoryUsage() {
        // Without flyweight: Each character would have its own style object
        // With flyweight: Characters share style objects
        
        int charactersCount = characters.size();
        int uniqueStyles = styleFactory.getStyleCount();
        
        // Assume each style object is 100 bytes
        int styleMemory = 100;
        
        long withoutFlyweight = charactersCount * styleMemory;
        long withFlyweight = uniqueStyles * styleMemory + (charactersCount * 20); // 20 bytes per character
        
        System.out.println("\n=== Memory Savings ===");
        System.out.println("Characters: " + charactersCount);
        System.out.println("Unique styles: " + uniqueStyles);
        System.out.println("Memory without flyweight: " + withoutFlyweight + " bytes");
        System.out.println("Memory with flyweight: " + withFlyweight + " bytes");
        System.out.println("Savings: " + (withoutFlyweight - withFlyweight) + " bytes " +
                          "(" + (100 * (withoutFlyweight - withFlyweight) / withoutFlyweight) + "%)");
    }
}

// Usage
public class TextEditorDemo {
    public static void main(String[] args) {
        TextDocument doc = new TextDocument();
        
        // Title - Arial 24pt, blue, bold
        doc.addText("Design Patterns", 10, 10, "Arial", 24, "blue", true, false);
        
        // Subtitle - Arial 18pt, gray, italic
        doc.addText("Flyweight Pattern", 10, 40, "Arial", 18, "gray", false, true);
        
        // Body paragraph 1 - Times New Roman 12pt, black, normal
        doc.addText("The flyweight pattern is used to minimize memory usage ", 
                   10, 70, "Times New Roman", 12, "black", false, false);
        doc.addText("by sharing common state among multiple objects.", 
                   10, 85, "Times New Roman", 12, "black", false, false);
        
        // Body paragraph 2 - Times New Roman 12pt, black, normal (same style!)
        doc.addText("This is particularly useful when creating a large number ", 
                   10, 110, "Times New Roman", 12, "black", false, false);
        doc.addText("of similar objects.", 
                   10, 125, "Times New Roman", 12, "black", false, false);
        
        // Highlight - Times New Roman 12pt, red, bold
        doc.addText("Important: ", 10, 150, "Times New Roman", 12, "red", true, false);
        doc.addText("Only creates unique style objects!", 
                   100, 150, "Times New Roman", 12, "black", false, false);
        
        // Render document
        doc.render();
        
        // Print memory savings
        doc.printMemoryUsage();
    }
}
```

**Forest/Tree Example (Classic Flyweight):**

```java
// Flyweight interface
public interface TreeType {
    void draw(int x, int y, int age);
}

// Concrete flyweight
public class TreeTypeImpl implements TreeType {
    private final String name;
    private final String color;
    private final String texture;
    
    public TreeTypeImpl(String name, String color, String texture) {
        this.name = name;
        this.color = color;
        this.texture = texture;
        
        System.out.println("Creating new TreeType: " + name);
    }
    
    @Override
    public void draw(int x, int y, int age) {
        System.out.printf("Drawing %s tree (%s, %s) at (%d,%d), age %d years%n",
                         name, color, texture, x, y, age);
    }
    
    @Override
    public String toString() {
        return name + " (" + color + ", " + texture + ")";
    }
}

// Flyweight factory
public class TreeFactory {
    private static final Map<String, TreeType> treeTypes = new HashMap<>();
    
    public static TreeType getTreeType(String name, String color, String texture) {
        String key = name + "|" + color + "|" + texture;
        
        return treeTypes.computeIfAbsent(key, k -> 
            new TreeTypeImpl(name, color, texture)
        );
    }
    
    public static int getTreeTypeCount() {
        return treeTypes.size();
    }
}

// Tree (contains extrinsic state)
public class Tree {
    private final int x, y; // Position (extrinsic - unique to each tree)
    private final int age;  // Age (extrinsic - unique to each tree)
    private final TreeType type; // Type (intrinsic - shared)
    
    public Tree(int x, int y, int age, TreeType type) {
        this.x = x;
        this.y = y;
        this.age = age;
        this.type = type;
    }
    
    public void draw() {
        type.draw(x, y, age);
    }
}

// Forest (client)
public class Forest {
    private final List<Tree> trees = new ArrayList<>();
    
    public void plantTree(int x, int y, int age, String name, String color, String texture) {
        // Get shared tree type (flyweight)
        TreeType type = TreeFactory.getTreeType(name, color, texture);
        
        // Create tree with extrinsic state
        Tree tree = new Tree(x, y, age, type);
        trees.add(tree);
    }
    
    public void draw() {
        System.out.println("\n=== Drawing Forest ===\n");
        trees.forEach(Tree::draw);
        
        System.out.println("\n=== Statistics ===");
        System.out.println("Total trees: " + trees.size());
        System.out.println("Unique tree types: " + TreeFactory.getTreeTypeCount());
        
        // Calculate memory savings
        int treeTypeMemory = 1000; // bytes per tree type (texture data)
        int treeMemory = 50; // bytes per tree (position, age)
        
        long withoutFlyweight = trees.size() * treeTypeMemory;
        long withFlyweight = (TreeFactory.getTreeTypeCount() * treeTypeMemory) + 
                            (trees.size() * treeMemory);
        
        System.out.println("Memory without flyweight: " + withoutFlyweight + " bytes");
        System.out.println("Memory with flyweight: " + withFlyweight + " bytes");
        System.out.println("Savings: " + ((withoutFlyweight - withFlyweight) * 100 / withoutFlyweight) + "%");
    }
}

// Usage
public class ForestSimulation {
    public static void main(String[] args) {
        Forest forest = new Forest();
        
        // Plant 1 million trees (only a few types)
        Random random = new Random(42);
        
        String[] treeTypes = {
            "Oak", "Pine", "Birch", "Maple", "Spruce"
        };
        
        String[] colors = {
            "dark-green", "light-green", "yellow-green"
        };
        
        String[] textures = {
            "rough", "smooth", "scaly"
        };
        
        System.out.println("Planting 1 million trees...\n");
        
        for (int i = 0; i < 1_000_000; i++) {
            int x = random.nextInt(10000);
            int y = random.nextInt(10000);
            int age = random.nextInt(100);
            
            String type = treeTypes[random.nextInt(treeTypes.length)];
            String color = colors[random.nextInt(colors.length)];
            String texture = textures[random.nextInt(textures.length)];
            
            forest.plantTree(x, y, age, type, color, texture);
        }
        
        // Draw first 10 trees
        System.out.println("Drawing sample trees:");
        for (int i = 0; i < 10; i++) {
            forest.trees.get(i).draw();
        }
        
        forest.draw();
    }
}

// Output shows:
// Creating new TreeType: Oak (dark-green, rough)
// Creating new TreeType: Pine (light-green, smooth)
// ... (only ~45 unique tree types created for 1M trees)
// Memory savings: ~95% (from 1GB to 50MB)
```

**Benefits:**
- **Memory savings:** Share common state among many objects
- **Performance:** Reduce number of objects created
- **Scalability:** Support large number of fine-grained objects

**Real-world Examples:**
- **String pool:** Java strings are flyweights
- **Integer cache:** `Integer.valueOf()` caches -128 to 127
- **Game engines:** Share textures, models among game objects
- **GUI toolkits:** Share fonts, colors, icons

**When to Use:**
- ✅ Application uses large number of objects
- ✅ Storage costs are high due to quantity
- ✅ Most object state can be made extrinsic
- ✅ Many groups of objects can be replaced by few shared objects
- ❌ Few objects or objects don't share much state

---

## 3. Behavioral Patterns

**Purpose:** Communication between objects, assigning responsibilities

### 3.1 Strategy Pattern

**Problem:** Need different algorithms for same task, switch at runtime

**Intent:** Define family of algorithms, encapsulate each, make them interchangeable

**Example: Payment Processing**

```java
// Strategy interface
public interface PaymentStrategy {
    boolean pay(double amount);
    String getPaymentMethod();
}

// Concrete strategies
public class CreditCardStrategy implements PaymentStrategy {
    private final String cardNumber;
    private final String cvv;
    private final String expiryDate;
    
    public CreditCardStrategy(String cardNumber, String cvv, String expiryDate) {
        this.cardNumber = cardNumber;
        this.cvv = cvv;
        this.expiryDate = expiryDate;
    }
    
    @Override
    public boolean pay(double amount) {
        System.out.println("Processing credit card payment of $" + amount);
        System.out.println("Card: **** **** **** " + cardNumber.substring(cardNumber.length() - 4));
        
        // Validate card
        if (!validateCard()) {
            System.out.println("✗ Card validation failed");
            return false;
        }
        
        // Process payment
        System.out.println("✓ Payment successful");
        return true;
    }
    
    private boolean validateCard() {
        // Simplified validation
        return cardNumber.length() == 16 && cvv.length() == 3;
    }
    
    @Override
    public String getPaymentMethod() {
        return "Credit Card";
    }
}

public class PayPalStrategy implements PaymentStrategy {
    private final String email;
    private final String password;
    
    public PayPalStrategy(String email, String password) {
        this.email = email;
        this.password = password;
    }
    
    @Override
    public boolean pay(double amount) {
        System.out.println("Processing PayPal payment of $" + amount);
        System.out.println("Email: " + email);
        
        // Authenticate
        if (!authenticate()) {
            System.out.println("✗ PayPal authentication failed");
            return false;
        }
        
        // Process payment
        System.out.println("✓ Payment successful via PayPal");
        return true;
    }
    
    private boolean authenticate() {
        // Simplified authentication
        return email.contains("@") && password.length() >= 8;
    }
    
    @Override
    public String getPaymentMethod() {
        return "PayPal";
    }
}

public class BitcoinStrategy implements PaymentStrategy {
    private final String walletAddress;
    
    public BitcoinStrategy(String walletAddress) {
        this.walletAddress = walletAddress;
    }
    
    @Override
    public boolean pay(double amount) {
        System.out.println("Processing Bitcoin payment of $" + amount);
        System.out.println("Wallet: " + walletAddress);
        
        // Convert USD to BTC
        double btcAmount = amount / 45000.0; // Simplified exchange rate
        System.out.println("Amount in BTC: " + String.format("%.8f", btcAmount));
        
        // Create blockchain transaction
        System.out.println("Creating blockchain transaction...");
        System.out.println("✓ Payment successful via Bitcoin");
        
        return true;
    }
    
    @Override
    public String getPaymentMethod() {
        return "Bitcoin";
    }
}

public class BankTransferStrategy implements PaymentStrategy {
    private final String accountNumber;
    private final String routingNumber;
    
    public BankTransferStrategy(String accountNumber, String routingNumber) {
        this.accountNumber = accountNumber;
        this.routingNumber = routingNumber;
    }
    
    @Override
    public boolean pay(double amount) {
        System.out.println("Processing bank transfer of $" + amount);
        System.out.println("Account: *****" + accountNumber.substring(accountNumber.length() - 4));
        System.out.println("Routing: " + routingNumber);
        
        // Initiate ACH transfer
        System.out.println("Initiating ACH transfer...");
        System.out.println("✓ Transfer initiated (will complete in 1-3 business days)");
        
        return true;
    }
    
    @Override
    public String getPaymentMethod() {
        return "Bank Transfer";
    }
}

// Context
public class ShoppingCart {
    private final List<Item> items = new ArrayList<>();
    private PaymentStrategy paymentStrategy;
    
    public void addItem(Item item) {
        items.add(item);
    }
    
    public void setPaymentStrategy(PaymentStrategy strategy) {
        this.paymentStrategy = strategy;
    }
    
    public double calculateTotal() {
        return items.stream()
            .mapToDouble(Item::getPrice)
            .sum();
    }
    
    public boolean checkout() {
        if (items.isEmpty()) {
            System.out.println("Cart is empty!");
            return false;
        }
        
        if (paymentStrategy == null) {
            System.out.println("Please select a payment method!");
            return false;
        }
        
        double total = calculateTotal();
        System.out.println("\n=== Checkout ===");
        System.out.println("Items: " + items.size());
        System.out.println("Total: $" + String.format("%.2f", total));
        System.out.println("Payment method: " + paymentStrategy.getPaymentMethod());
        System.out.println();
        
        boolean success = paymentStrategy.pay(total);
        
        if (success) {
            items.clear();
        }
        
        return success;
    }
}

public class Item {
    private final String name;
    private final double price;
    
    public Item(String name, double price) {
        this.name = name;
        this.price = price;
    }
    
    public String getName() { return name; }
    public double getPrice() { return price; }
}

// Usage
public class ECommerceDemo {
    public static void main(String[] args) {
        ShoppingCart cart = new ShoppingCart();
        
        cart.addItem(new Item("Laptop", 999.99));
        cart.addItem(new Item("Mouse", 29.99));
        cart.addItem(new Item("Keyboard", 79.99));
        
        // Try with credit card
        cart.setPaymentStrategy(new CreditCardStrategy(
            "1234567812345678", "123", "12/25"
        ));
        cart.checkout();
        
        // Add more items
        cart.addItem(new Item("Monitor", 299.99));
        cart.addItem(new Item("Webcam", 89.99));
        
        // Switch to PayPal
        cart.setPaymentStrategy(new PayPalStrategy(
            "user@example.com", "securepassword123"
        ));
        cart.checkout();
        
        // Add more items
        cart.addItem(new Item("Headphones", 149.99));
        
        // Switch to Bitcoin
        cart.setPaymentStrategy(new BitcoinStrategy(
            "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        ));
        cart.checkout();
    }
}
```

**Sorting Strategy Example:**

```java
// Strategy interface
public interface SortStrategy<T> {
    void sort(List<T> list, Comparator<T> comparator);
    String getAlgorithmName();
}

// Concrete strategies
public class BubbleSortStrategy<T> implements SortStrategy<T> {
    @Override
    public void sort(List<T> list, Comparator<T> comparator) {
        int n = list.size();
        for (int i = 0; i < n - 1; i++) {
            for (int j = 0; j < n - i - 1; j++) {
                if (comparator.compare(list.get(j), list.get(j + 1)) > 0) {
                    T temp = list.get(j);
                    list.set(j, list.get(j + 1));
                    list.set(j + 1, temp);
                }
            }
        }
    }
    
    @Override
    public String getAlgorithmName() {
        return "Bubble Sort";
    }
}

public class QuickSortStrategy<T> implements SortStrategy<T> {
    @Override
    public void sort(List<T> list, Comparator<T> comparator) {
        quickSort(list, 0, list.size() - 1, comparator);
    }
    
    private void quickSort(List<T> list, int low, int high, Comparator<T> comparator) {
        if (low < high) {
            int pi = partition(list, low, high, comparator);
            quickSort(list, low, pi - 1, comparator);
            quickSort(list, pi + 1, high, comparator);
        }
    }
    
    private int partition(List<T> list, int low, int high, Comparator<T> comparator) {
        T pivot = list.get(high);
        int i = low - 1;
        
        for (int j = low; j < high; j++) {
            if (comparator.compare(list.get(j), pivot) <= 0) {
                i++;
                T temp = list.get(i);
                list.set(i, list.get(j));
                list.set(j, temp);
            }
        }
        
        T temp = list.get(i + 1);
        list.set(i + 1, list.get(high));
        list.set(high, temp);
        
        return i + 1;
    }
    
    @Override
    public String getAlgorithmName() {
        return "Quick Sort";
    }
}

public class MergeSortStrategy<T> implements SortStrategy<T> {
    @Override
    public void sort(List<T> list, Comparator<T> comparator) {
        if (list.size() > 1) {
            mergeSort(list, 0, list.size() - 1, comparator);
        }
    }
    
    private void mergeSort(List<T> list, int left, int right, Comparator<T> comparator) {
        if (left < right) {
            int mid = (left + right) / 2;
            mergeSort(list, left, mid, comparator);
            mergeSort(list, mid + 1, right, comparator);
            merge(list, left, mid, right, comparator);
        }
    }
    
    private void merge(List<T> list, int left, int mid, int right, Comparator<T> comparator) {
        List<T> leftList = new ArrayList<>(list.subList(left, mid + 1));
        List<T> rightList = new ArrayList<>(list.subList(mid + 1, right + 1));
        
        int i = 0, j = 0, k = left;
        
        while (i < leftList.size() && j < rightList.size()) {
            if (comparator.compare(leftList.get(i), rightList.get(j)) <= 0) {
                list.set(k++, leftList.get(i++));
            } else {
                list.set(k++, rightList.get(j++));
            }
        }
        
        while (i < leftList.size()) {
            list.set(k++, leftList.get(i++));
        }
        
        while (j < rightList.size()) {
            list.set(k++, rightList.get(j++));
        }
    }
    
    @Override
    public String getAlgorithmName() {
        return "Merge Sort";
    }
}

// Context
public class Sorter<T> {
    private SortStrategy<T> strategy;
    
    public void setStrategy(SortStrategy<T> strategy) {
        this.strategy = strategy;
    }
    
    public void sort(List<T> list, Comparator<T> comparator) {
        if (strategy == null) {
            throw new IllegalStateException("Sort strategy not set");
        }
        
        long startTime = System.nanoTime();
        strategy.sort(list, comparator);
        long endTime = System.nanoTime();
        
        double durationMs = (endTime - startTime) / 1_000_000.0;
        System.out.println(strategy.getAlgorithmName() + " completed in " + 
                          String.format("%.2f", durationMs) + " ms");
    }
    
    // Automatic strategy selection based on list size
    public void sortAuto(List<T> list, Comparator<T> comparator) {
        if (list.size() < 10) {
            setStrategy(new BubbleSortStrategy<>());
        } else if (list.size() < 1000) {
            setStrategy(new QuickSortStrategy<>());
        } else {
            setStrategy(new MergeSortStrategy<>());
        }
        
        System.out.println("Auto-selected: " + strategy.getAlgorithmName() + 
                          " for " + list.size() + " elements");
        sort(list, comparator);
    }
}

// Usage
public class SortingDemo {
    public static void main(String[] args) {
        Sorter<Integer> sorter = new Sorter<>();
        
        // Small list - use bubble sort
        List<Integer> smallList = new ArrayList<>(List.of(5, 2, 8, 1, 9));
        System.out.println("Original: " + smallList);
        sorter.sortAuto(smallList, Integer::compareTo);
        System.out.println("Sorted: " + smallList + "\n");
        
        // Medium list - use quick sort
        List<Integer> mediumList = new ArrayList<>();
        Random random = new Random();
        for (int i = 0; i < 100; i++) {
            mediumList.add(random.nextInt(1000));
        }
        System.out.println("Sorting medium list (" + mediumList.size() + " elements)");
        sorter.sortAuto(mediumList, Integer::compareTo);
        
        // Large list - use merge sort
        List<Integer> largeList = new ArrayList<>();
        for (int i = 0; i < 10000; i++) {
            largeList.add(random.nextInt(100000));
        }
        System.out.println("\nSorting large list (" + largeList.size() + " elements)");
        sorter.sortAuto(largeList, Integer::compareTo);
    }
}
```

**Benefits:**
- **Open/Closed Principle:** Add new algorithms without changing context
- **Runtime flexibility:** Switch algorithms dynamically
- **Eliminate conditionals:** Replace if-else chains with strategy objects
- **Encapsulation:** Hide algorithm implementation details

**Real-world Examples:**
- **Java Comparator:** Different sorting strategies
- **Collections.sort():** Uses different algorithms based on input
- **Spring Security:** Different authentication strategies
- **Compression algorithms:** ZIP, GZIP, BZIP2

---

**End of Part 3**

**Coming next:** Observer, Command, Template Method, Iterator, State patterns + Production anti-patterns

**Lines so far: ~2,000**