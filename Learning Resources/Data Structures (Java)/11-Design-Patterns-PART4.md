# Design Patterns - Part 4 (Final)

**Continued from Part 3 (11-Design-Patterns-PART3.md)**

---

### 3.2 Observer Pattern

**Problem:** One-to-many dependency - when one object changes, notify all dependents

**Intent:** Define subscription mechanism to notify multiple objects about events

**Example: Stock Market Monitoring**

```java
// Subject interface
public interface Stock {
    void attach(Observer observer);
    void detach(Observer observer);
    void notifyObservers();
    
    String getSymbol();
    double getPrice();
    void setPrice(double price);
}

// Concrete subject
public class StockImpl implements Stock {
    private final String symbol;
    private double price;
    private final List<Observer> observers = new ArrayList<>();
    
    public StockImpl(String symbol, double initialPrice) {
        this.symbol = symbol;
        this.price = initialPrice;
    }
    
    @Override
    public void attach(Observer observer) {
        observers.add(observer);
        System.out.println(observer.getName() + " subscribed to " + symbol);
    }
    
    @Override
    public void detach(Observer observer) {
        observers.remove(observer);
        System.out.println(observer.getName() + " unsubscribed from " + symbol);
    }
    
    @Override
    public void notifyObservers() {
        System.out.println("\n" + symbol + " price changed to $" + price + " - notifying " + 
                          observers.size() + " observers");
        
        for (Observer observer : observers) {
            observer.update(this);
        }
    }
    
    @Override
    public String getSymbol() {
        return symbol;
    }
    
    @Override
    public double getPrice() {
        return price;
    }
    
    @Override
    public void setPrice(double newPrice) {
        if (this.price != newPrice) {
            double oldPrice = this.price;
            this.price = newPrice;
            
            System.out.println("\n" + symbol + ": $" + oldPrice + " → $" + newPrice);
            notifyObservers();
        }
    }
}

// Observer interface
public interface Observer {
    void update(Stock stock);
    String getName();
}

// Concrete observers
public class InvestorObserver implements Observer {
    private final String name;
    private final Map<String, Double> portfolio = new HashMap<>();
    private final double buyThreshold;
    private final double sellThreshold;
    
    public InvestorObserver(String name, double buyThreshold, double sellThreshold) {
        this.name = name;
        this.buyThreshold = buyThreshold;
        this.sellThreshold = sellThreshold;
    }
    
    @Override
    public void update(Stock stock) {
        double price = stock.getPrice();
        String symbol = stock.getSymbol();
        
        System.out.println("  [" + name + "] Received update: " + symbol + " @ $" + price);
        
        if (price < buyThreshold) {
            System.out.println("  [" + name + "] 🟢 BUY signal for " + symbol + 
                             " (price below $" + buyThreshold + ")");
            portfolio.put(symbol, price);
        } else if (price > sellThreshold && portfolio.containsKey(symbol)) {
            double boughtAt = portfolio.remove(symbol);
            double profit = price - boughtAt;
            System.out.println("  [" + name + "] 🔴 SELL signal for " + symbol + 
                             " (price above $" + sellThreshold + ") - Profit: $" + 
                             String.format("%.2f", profit));
        } else {
            System.out.println("  [" + name + "] ⚪ HOLD " + symbol);
        }
    }
    
    @Override
    public String getName() {
        return name;
    }
}

public class DisplayBoardObserver implements Observer {
    private final String boardName;
    
    public DisplayBoardObserver(String boardName) {
        this.boardName = boardName;
    }
    
    @Override
    public void update(Stock stock) {
        System.out.println("  [" + boardName + "] 📊 Displaying: " + 
                          stock.getSymbol() + " = $" + stock.getPrice());
    }
    
    @Override
    public String getName() {
        return boardName;
    }
}

public class AlertObserver implements Observer {
    private final String name;
    private final Map<String, PriceAlert> alerts = new HashMap<>();
    
    public AlertObserver(String name) {
        this.name = name;
    }
    
    public void setAlert(String symbol, double targetPrice, boolean alertAbove) {
        alerts.put(symbol, new PriceAlert(targetPrice, alertAbove));
        System.out.println("[" + name + "] Alert set for " + symbol + 
                          (alertAbove ? " above " : " below ") + "$" + targetPrice);
    }
    
    @Override
    public void update(Stock stock) {
        PriceAlert alert = alerts.get(stock.getSymbol());
        
        if (alert != null) {
            double price = stock.getPrice();
            
            if ((alert.alertAbove && price >= alert.targetPrice) ||
                (!alert.alertAbove && price <= alert.targetPrice)) {
                
                System.out.println("  [" + name + "] 🔔 ALERT: " + stock.getSymbol() + 
                                 " reached $" + price + " (target: $" + alert.targetPrice + ")");
                
                // Remove alert after triggering
                alerts.remove(stock.getSymbol());
            }
        }
    }
    
    @Override
    public String getName() {
        return name;
    }
    
    private static class PriceAlert {
        final double targetPrice;
        final boolean alertAbove;
        
        PriceAlert(double targetPrice, boolean alertAbove) {
            this.targetPrice = targetPrice;
            this.alertAbove = alertAbove;
        }
    }
}

// Usage
public class StockMarketDemo {
    public static void main(String[] args) throws InterruptedException {
        // Create stocks
        Stock apple = new StockImpl("AAPL", 150.00);
        Stock google = new StockImpl("GOOGL", 2800.00);
        
        // Create observers
        InvestorObserver warren = new InvestorObserver("Warren", 140.00, 160.00);
        InvestorObserver nancy = new InvestorObserver("Nancy", 145.00, 155.00);
        DisplayBoardObserver board = new DisplayBoardObserver("Times Square Board");
        AlertObserver alertSystem = new AlertObserver("Alert System");
        
        // Subscribe observers to stocks
        apple.attach(warren);
        apple.attach(nancy);
        apple.attach(board);
        apple.attach(alertSystem);
        
        google.attach(warren);
        google.attach(board);
        
        // Set price alerts
        alertSystem.setAlert("AAPL", 155.00, true);  // Alert when above $155
        alertSystem.setAlert("GOOGL", 2750.00, false); // Alert when below $2750
        
        // Simulate price changes
        System.out.println("\n=== Market Opens ===");
        
        Thread.sleep(1000);
        apple.setPrice(148.50);  // Drop - buy signal for Warren
        
        Thread.sleep(1000);
        apple.setPrice(152.00);  // Rise - hold
        
        Thread.sleep(1000);
        apple.setPrice(156.00);  // Above threshold - sell signal + alert triggers
        
        Thread.sleep(1000);
        google.setPrice(2740.00); // Drop - alert triggers
        
        // Nancy unsubscribes
        System.out.println("\n=== Nancy leaves ===");
        apple.detach(nancy);
        
        Thread.sleep(1000);
        apple.setPrice(160.00);  // Nancy won't receive this
    }
}
```

**Event-Driven System Example:**

```java
// Event types
public interface Event {
    String getType();
    Object getData();
    long getTimestamp();
}

public class GenericEvent implements Event {
    private final String type;
    private final Object data;
    private final long timestamp;
    
    public GenericEvent(String type, Object data) {
        this.type = type;
        this.data = data;
        this.timestamp = System.currentTimeMillis();
    }
    
    @Override
    public String getType() { return type; }
    
    @Override
    public Object getData() { return data; }
    
    @Override
    public long getTimestamp() { return timestamp; }
}

// Event listener interface
public interface EventListener {
    void onEvent(Event event);
    String getListenerId();
}

// Event manager (Subject)
public class EventManager {
    private final Map<String, List<EventListener>> listeners = new ConcurrentHashMap<>();
    
    public void subscribe(String eventType, EventListener listener) {
        listeners.computeIfAbsent(eventType, k -> new CopyOnWriteArrayList<>())
                .add(listener);
        
        System.out.println(listener.getListenerId() + " subscribed to " + eventType);
    }
    
    public void unsubscribe(String eventType, EventListener listener) {
        List<EventListener> eventListeners = listeners.get(eventType);
        if (eventListeners != null) {
            eventListeners.remove(listener);
            System.out.println(listener.getListenerId() + " unsubscribed from " + eventType);
        }
    }
    
    public void publish(Event event) {
        List<EventListener> eventListeners = listeners.get(event.getType());
        
        if (eventListeners == null || eventListeners.isEmpty()) {
            System.out.println("No listeners for event: " + event.getType());
            return;
        }
        
        System.out.println("\nPublishing " + event.getType() + " to " + 
                          eventListeners.size() + " listener(s)");
        
        for (EventListener listener : eventListeners) {
            try {
                listener.onEvent(event);
            } catch (Exception e) {
                System.err.println("Error notifying " + listener.getListenerId() + 
                                 ": " + e.getMessage());
            }
        }
    }
}

// Concrete listeners
public class EmailNotificationListener implements EventListener {
    @Override
    public void onEvent(Event event) {
        System.out.println("  [Email] Sending email notification for " + event.getType());
        System.out.println("  [Email] Data: " + event.getData());
    }
    
    @Override
    public String getListenerId() {
        return "EmailNotificationListener";
    }
}

public class LoggingListener implements EventListener {
    @Override
    public void onEvent(Event event) {
        System.out.println("  [Logger] Event logged: " + event.getType() + 
                          " at " + new Date(event.getTimestamp()));
        System.out.println("  [Logger] Payload: " + event.getData());
    }
    
    @Override
    public String getListenerId() {
        return "LoggingListener";
    }
}

public class AnalyticsListener implements EventListener {
    private int eventCount = 0;
    
    @Override
    public void onEvent(Event event) {
        eventCount++;
        System.out.println("  [Analytics] Event #" + eventCount + " tracked: " + 
                          event.getType());
    }
    
    @Override
    public String getListenerId() {
        return "AnalyticsListener";
    }
}

// Usage
public class EventSystemDemo {
    public static void main(String[] args) {
        EventManager eventManager = new EventManager();
        
        // Create listeners
        EmailNotificationListener emailListener = new EmailNotificationListener();
        LoggingListener loggingListener = new LoggingListener();
        AnalyticsListener analyticsListener = new AnalyticsListener();
        
        // Subscribe to events
        eventManager.subscribe("USER_REGISTERED", emailListener);
        eventManager.subscribe("USER_REGISTERED", loggingListener);
        eventManager.subscribe("USER_REGISTERED", analyticsListener);
        
        eventManager.subscribe("ORDER_PLACED", emailListener);
        eventManager.subscribe("ORDER_PLACED", loggingListener);
        eventManager.subscribe("ORDER_PLACED", analyticsListener);
        
        eventManager.subscribe("PAYMENT_FAILED", emailListener);
        eventManager.subscribe("PAYMENT_FAILED", loggingListener);
        
        // Publish events
        eventManager.publish(new GenericEvent("USER_REGISTERED", 
                                              Map.of("userId", "12345", "email", "user@example.com")));
        
        eventManager.publish(new GenericEvent("ORDER_PLACED", 
                                              Map.of("orderId", "ORD-789", "amount", 299.99)));
        
        eventManager.publish(new GenericEvent("PAYMENT_FAILED", 
                                              Map.of("orderId", "ORD-790", "reason", "Insufficient funds")));
        
        // Unsubscribe
        eventManager.unsubscribe("PAYMENT_FAILED", emailListener);
        
        eventManager.publish(new GenericEvent("PAYMENT_FAILED", 
                                              Map.of("orderId", "ORD-791", "reason", "Card expired")));
    }
}
```

**Benefits:**
- **Loose coupling:** Subject doesn't know concrete observers
- **Dynamic relationships:** Add/remove observers at runtime
- **Broadcast communication:** Single notification to many
- **Open/Closed:** Add new observers without changing subject

**Real-world Examples:**
- **Java Swing:** ActionListener, MouseListener
- **Spring Events:** ApplicationEvent, ApplicationListener
- **RxJava:** Observable, Observer pattern
- **Message queues:** Pub/Sub messaging (Kafka, RabbitMQ)

---

### 3.3 Command Pattern

**Problem:** Encapsulate requests as objects, parameterize clients with different requests

**Intent:** Turn requests into stand-alone objects containing all request information

**Example: Smart Home Automation**

```java
// Command interface
public interface Command {
    void execute();
    void undo();
    String getDescription();
}

// Receiver - Light
public class Light {
    private final String location;
    private int brightness = 0; // 0 = off, 100 = max
    
    public Light(String location) {
        this.location = location;
    }
    
    public void on() {
        brightness = 100;
        System.out.println(location + " light is ON (100%)");
    }
    
    public void off() {
        brightness = 0;
        System.out.println(location + " light is OFF");
    }
    
    public void dim(int level) {
        brightness = level;
        System.out.println(location + " light dimmed to " + level + "%");
    }
    
    public int getBrightness() {
        return brightness;
    }
    
    public String getLocation() {
        return location;
    }
}

// Concrete commands
public class LightOnCommand implements Command {
    private final Light light;
    private int previousBrightness;
    
    public LightOnCommand(Light light) {
        this.light = light;
    }
    
    @Override
    public void execute() {
        previousBrightness = light.getBrightness();
        light.on();
    }
    
    @Override
    public void undo() {
        light.dim(previousBrightness);
    }
    
    @Override
    public String getDescription() {
        return "Turn on " + light.getLocation() + " light";
    }
}

public class LightOffCommand implements Command {
    private final Light light;
    private int previousBrightness;
    
    public LightOffCommand(Light light) {
        this.light = light;
    }
    
    @Override
    public void execute() {
        previousBrightness = light.getBrightness();
        light.off();
    }
    
    @Override
    public void undo() {
        light.dim(previousBrightness);
    }
    
    @Override
    public String getDescription() {
        return "Turn off " + light.getLocation() + " light";
    }
}

public class DimLightCommand implements Command {
    private final Light light;
    private final int level;
    private int previousBrightness;
    
    public DimLightCommand(Light light, int level) {
        this.light = light;
        this.level = level;
    }
    
    @Override
    public void execute() {
        previousBrightness = light.getBrightness();
        light.dim(level);
    }
    
    @Override
    public void undo() {
        light.dim(previousBrightness);
    }
    
    @Override
    public String getDescription() {
        return "Dim " + light.getLocation() + " light to " + level + "%";
    }
}

// Receiver - Thermostat
public class Thermostat {
    private int temperature = 72; // Fahrenheit
    
    public void setTemperature(int temp) {
        temperature = temp;
        System.out.println("Thermostat set to " + temp + "°F");
    }
    
    public int getTemperature() {
        return temperature;
    }
}

public class SetTemperatureCommand implements Command {
    private final Thermostat thermostat;
    private final int temperature;
    private int previousTemperature;
    
    public SetTemperatureCommand(Thermostat thermostat, int temperature) {
        this.thermostat = thermostat;
        this.temperature = temperature;
    }
    
    @Override
    public void execute() {
        previousTemperature = thermostat.getTemperature();
        thermostat.setTemperature(temperature);
    }
    
    @Override
    public void undo() {
        thermostat.setTemperature(previousTemperature);
    }
    
    @Override
    public String getDescription() {
        return "Set temperature to " + temperature + "°F";
    }
}

// Macro command (composite)
public class MacroCommand implements Command {
    private final List<Command> commands;
    private final String description;
    
    public MacroCommand(String description, Command... commands) {
        this.description = description;
        this.commands = Arrays.asList(commands);
    }
    
    @Override
    public void execute() {
        System.out.println("\n=== Executing Macro: " + description + " ===");
        for (Command command : commands) {
            command.execute();
        }
    }
    
    @Override
    public void undo() {
        System.out.println("\n=== Undoing Macro: " + description + " ===");
        // Undo in reverse order
        for (int i = commands.size() - 1; i >= 0; i--) {
            commands.get(i).undo();
        }
    }
    
    @Override
    public String getDescription() {
        return description;
    }
}

// Invoker
public class RemoteControl {
    private final Map<Integer, Command> commands = new HashMap<>();
    private final Stack<Command> history = new Stack<>();
    
    public void setCommand(int slot, Command command) {
        commands.put(slot, command);
        System.out.println("Slot " + slot + ": " + command.getDescription());
    }
    
    public void pressButton(int slot) {
        Command command = commands.get(slot);
        
        if (command == null) {
            System.out.println("No command assigned to slot " + slot);
            return;
        }
        
        System.out.println("\nExecuting: " + command.getDescription());
        command.execute();
        history.push(command);
    }
    
    public void pressUndo() {
        if (history.isEmpty()) {
            System.out.println("Nothing to undo");
            return;
        }
        
        Command command = history.pop();
        System.out.println("\nUndoing: " + command.getDescription());
        command.undo();
    }
    
    public void showCommands() {
        System.out.println("\n=== Remote Control ===");
        commands.forEach((slot, command) -> 
            System.out.println("Slot " + slot + ": " + command.getDescription())
        );
    }
}

// Usage
public class SmartHomeDemo {
    public static void main(String[] args) {
        // Create receivers
        Light livingRoomLight = new Light("Living Room");
        Light bedroomLight = new Light("Bedroom");
        Thermostat thermostat = new Thermostat();
        
        // Create commands
        Command livingRoomOn = new LightOnCommand(livingRoomLight);
        Command livingRoomOff = new LightOffCommand(livingRoomLight);
        Command livingRoomDim = new DimLightCommand(livingRoomLight, 30);
        
        Command bedroomOn = new LightOnCommand(bedroomLight);
        Command bedroomOff = new LightOffCommand(bedroomLight);
        
        Command setTemp68 = new SetTemperatureCommand(thermostat, 68);
        Command setTemp72 = new SetTemperatureCommand(thermostat, 72);
        
        // Create macro commands
        Command goodMorning = new MacroCommand("Good Morning",
            livingRoomOn,
            setTemp72
        );
        
        Command goodNight = new MacroCommand("Good Night",
            livingRoomOff,
            bedroomDim,
            setTemp68
        );
        
        Command bedroomDim = new DimLightCommand(bedroomLight, 20);
        
        // Create remote control
        RemoteControl remote = new RemoteControl();
        
        // Assign commands to slots
        remote.setCommand(1, livingRoomOn);
        remote.setCommand(2, livingRoomOff);
        remote.setCommand(3, bedroomOn);
        remote.setCommand(4, bedroomOff);
        remote.setCommand(5, goodMorning);
        remote.setCommand(6, goodNight);
        
        remote.showCommands();
        
        // Use remote control
        remote.pressButton(5); // Good morning macro
        
        remote.pressButton(3); // Bedroom on
        
        remote.pressButton(6); // Good night macro
        
        remote.pressUndo(); // Undo good night
        
        remote.pressUndo(); // Undo bedroom on
    }
}
```

**Text Editor with Undo/Redo:**

```java
// Command interface
public interface TextCommand {
    void execute();
    void undo();
}

// Receiver
public class TextEditor {
    private StringBuilder content = new StringBuilder();
    
    public void insert(int position, String text) {
        content.insert(position, text);
        System.out.println("Inserted: \"" + text + "\" at position " + position);
    }
    
    public void delete(int start, int end) {
        String deleted = content.substring(start, end);
        content.delete(start, end);
        System.out.println("Deleted: \"" + deleted + "\" from " + start + " to " + end);
    }
    
    public String getContent() {
        return content.toString();
    }
    
    public void printContent() {
        System.out.println("Content: \"" + content + "\"");
    }
}

// Concrete commands
public class InsertCommand implements TextCommand {
    private final TextEditor editor;
    private final int position;
    private final String text;
    
    public InsertCommand(TextEditor editor, int position, String text) {
        this.editor = editor;
        this.position = position;
        this.text = text;
    }
    
    @Override
    public void execute() {
        editor.insert(position, text);
    }
    
    @Override
    public void undo() {
        editor.delete(position, position + text.length());
    }
}

public class DeleteCommand implements TextCommand {
    private final TextEditor editor;
    private final int start;
    private final int end;
    private String deletedText;
    
    public DeleteCommand(TextEditor editor, int start, int end) {
        this.editor = editor;
        this.start = start;
        this.end = end;
    }
    
    @Override
    public void execute() {
        deletedText = editor.getContent().substring(start, end);
        editor.delete(start, end);
    }
    
    @Override
    public void undo() {
        editor.insert(start, deletedText);
    }
}

// Command manager with undo/redo
public class CommandManager {
    private final Stack<TextCommand> undoStack = new Stack<>();
    private final Stack<TextCommand> redoStack = new Stack<>();
    
    public void executeCommand(TextCommand command) {
        command.execute();
        undoStack.push(command);
        redoStack.clear(); // Clear redo stack on new command
    }
    
    public void undo() {
        if (undoStack.isEmpty()) {
            System.out.println("Nothing to undo");
            return;
        }
        
        TextCommand command = undoStack.pop();
        command.undo();
        redoStack.push(command);
        System.out.println("Undo successful");
    }
    
    public void redo() {
        if (redoStack.isEmpty()) {
            System.out.println("Nothing to redo");
            return;
        }
        
        TextCommand command = redoStack.pop();
        command.execute();
        undoStack.push(command);
        System.out.println("Redo successful");
    }
}

// Usage
public class TextEditorDemo {
    public static void main(String[] args) {
        TextEditor editor = new TextEditor();
        CommandManager manager = new CommandManager();
        
        // Type some text
        manager.executeCommand(new InsertCommand(editor, 0, "Hello "));
        editor.printContent();
        
        manager.executeCommand(new InsertCommand(editor, 6, "World"));
        editor.printContent();
        
        manager.executeCommand(new InsertCommand(editor, 11, "!"));
        editor.printContent();
        
        // Delete some text
        manager.executeCommand(new DeleteCommand(editor, 6, 11));
        editor.printContent();
        
        // Undo delete
        manager.undo();
        editor.printContent();
        
        // Undo insert
        manager.undo();
        editor.printContent();
        
        // Redo
        manager.redo();
        editor.printContent();
    }
}
```

**Benefits:**
- **Decoupling:** Invoker doesn't know about receiver
- **Undo/Redo:** Commands store state for reversal
- **Queuing:** Commands can be queued and executed later
- **Logging:** Commands can be logged for audit trail
- **Transactions:** Compose commands into transactions

**Real-world Examples:**
- **Swing Actions:** AbstractAction in GUI applications
- **Spring @Transactional:** Transaction commands
- **Job schedulers:** Quartz jobs are commands
- **Version control:** Git commits are commands

---

### 3.4 Template Method Pattern

**Problem:** Define skeleton of algorithm, let subclasses override specific steps

**Intent:** Define algorithm structure in base class, defer some steps to subclasses

**Example: Data Processing Pipeline**

```java
// Abstract class with template method
public abstract class DataProcessor {
    
    // Template method - defines algorithm skeleton
    public final void process() {
        System.out.println("\n=== Starting Data Processing ===");
        
        // Step 1: Read data
        List<String> data = readData();
        System.out.println("Read " + data.size() + " records");
        
        // Step 2: Validate (optional hook)
        if (shouldValidate()) {
            validateData(data);
        }
        
        // Step 3: Transform
        List<String> transformed = transformData(data);
        System.out.println("Transformed " + transformed.size() + " records");
        
        // Step 4: Filter (optional hook)
        if (shouldFilter()) {
            transformed = filterData(transformed);
            System.out.println("Filtered to " + transformed.size() + " records");
        }
        
        // Step 5: Write data
        writeData(transformed);
        
        System.out.println("=== Processing Complete ===\n");
    }
    
    // Abstract methods - must be implemented by subclasses
    protected abstract List<String> readData();
    protected abstract List<String> transformData(List<String> data);
    protected abstract void writeData(List<String> data);
    
    // Hook methods - optional, subclasses can override
    protected boolean shouldValidate() {
        return true;
    }
    
    protected boolean shouldFilter() {
        return false;
    }
    
    protected void validateData(List<String> data) {
        System.out.println("Validating data...");
        // Default validation logic
    }
    
    protected List<String> filterData(List<String> data) {
        System.out.println("Filtering data...");
        return data; // Default: no filtering
    }
}

// Concrete implementation - CSV to JSON
public class CsvToJsonProcessor extends DataProcessor {
    private final String inputFile;
    private final String outputFile;
    
    public CsvToJsonProcessor(String inputFile, String outputFile) {
        this.inputFile = inputFile;
        this.outputFile = outputFile;
    }
    
    @Override
    protected List<String> readData() {
        System.out.println("Reading CSV from: " + inputFile);
        // Simulate reading CSV
        return List.of(
            "id,name,age",
            "1,John,30",
            "2,Jane,25",
            "3,Bob,35"
        );
    }
    
    @Override
    protected List<String> transformData(List<String> data) {
        System.out.println("Transforming CSV to JSON...");
        List<String> json = new ArrayList<>();
        
        // Skip header
        for (int i = 1; i < data.size(); i++) {
            String[] parts = data.get(i).split(",");
            String jsonObj = String.format("{\"id\":%s,\"name\":\"%s\",\"age\":%s}", 
                                          parts[0], parts[1], parts[2]);
            json.add(jsonObj);
        }
        
        return json;
    }
    
    @Override
    protected void writeData(List<String> data) {
        System.out.println("Writing JSON to: " + outputFile);
        System.out.println("Data: " + data);
    }
    
    @Override
    protected boolean shouldFilter() {
        return true; // Enable filtering
    }
    
    @Override
    protected List<String> filterData(List<String> data) {
        // Filter: only people over 25
        System.out.println("Filtering: age > 25");
        return data.stream()
            .filter(json -> !json.contains("\"age\":25"))
            .collect(Collectors.toList());
    }
}

// Concrete implementation - Database to XML
public class DatabaseToXmlProcessor extends DataProcessor {
    private final String tableName;
    private final String outputFile;
    
    public DatabaseToXmlProcessor(String tableName, String outputFile) {
        this.tableName = tableName;
        this.outputFile = outputFile;
    }
    
    @Override
    protected List<String> readData() {
        System.out.println("Reading from database table: " + tableName);
        // Simulate database query
        return List.of(
            "Product: Laptop, Price: 999",
            "Product: Mouse, Price: 29",
            "Product: Keyboard, Price: 79"
        );
    }
    
    @Override
    protected List<String> transformData(List<String> data) {
        System.out.println("Transforming to XML...");
        return data.stream()
            .map(row -> {
                String[] parts = row.split(", ");
                String product = parts[0].split(": ")[1];
                String price = parts[1].split(": ")[1];
                return String.format("<product><name>%s</name><price>%s</price></product>", 
                                   product, price);
            })
            .collect(Collectors.toList());
    }
    
    @Override
    protected void writeData(List<String> data) {
        System.out.println("Writing XML to: " + outputFile);
        System.out.println("<products>");
        data.forEach(xml -> System.out.println("  " + xml));
        System.out.println("</products>");
    }
    
    @Override
    protected boolean shouldValidate() {
        return false; // Skip validation
    }
}

// Usage
public class DataProcessingDemo {
    public static void main(String[] args) {
        // CSV to JSON processing
        DataProcessor csvProcessor = new CsvToJsonProcessor("users.csv", "users.json");
        csvProcessor.process();
        
        // Database to XML processing
        DataProcessor dbProcessor = new DatabaseToXmlProcessor("products", "products.xml");
        dbProcessor.process();
    }
}
```

**Game AI Template:**

```java
public abstract class GameAI {
    
    // Template method
    public final void takeTurn() {
        collectResources();
        buildStructures();
        trainUnits();
        
        if (shouldAttack()) {
            attack();
        } else {
            defend();
        }
        
        endTurn();
    }
    
    // Common methods
    protected void collectResources() {
        System.out.println("[AI] Collecting resources...");
    }
    
    protected void endTurn() {
        System.out.println("[AI] Turn ended");
    }
    
    // Abstract methods - different for each AI
    protected abstract void buildStructures();
    protected abstract void trainUnits();
    protected abstract void attack();
    protected abstract void defend();
    
    // Hook method
    protected boolean shouldAttack() {
        return Math.random() > 0.5;
    }
}

public class AggressiveAI extends GameAI {
    @Override
    protected void buildStructures() {
        System.out.println("[Aggressive AI] Building barracks and weapon factories");
    }
    
    @Override
    protected void trainUnits() {
        System.out.println("[Aggressive AI] Training offensive units (soldiers, tanks)");
    }
    
    @Override
    protected void attack() {
        System.out.println("[Aggressive AI] 🔥 ALL-OUT ATTACK!");
    }
    
    @Override
    protected void defend() {
        System.out.println("[Aggressive AI] Minimal defense, preparing next attack");
    }
    
    @Override
    protected boolean shouldAttack() {
        return true; // Always attack!
    }
}

public class DefensiveAI extends GameAI {
    @Override
    protected void buildStructures() {
        System.out.println("[Defensive AI] Building walls and towers");
    }
    
    @Override
    protected void trainUnits() {
        System.out.println("[Defensive AI] Training defensive units (archers, shields)");
    }
    
    @Override
    protected void attack() {
        System.out.println("[Defensive AI] Counter-attack with minimal force");
    }
    
    @Override
    protected void defend() {
        System.out.println("[Defensive AI] 🛡️ FORTIFYING DEFENSES!");
    }
    
    @Override
    protected boolean shouldAttack() {
        return Math.random() > 0.8; // Rarely attack
    }
}

// Usage
public class GameAIDemo {
    public static void main(String[] args) {
        GameAI aggressive = new AggressiveAI();
        GameAI defensive = new DefensiveAI();
        
        System.out.println("=== Aggressive AI Turn ===");
        aggressive.takeTurn();
        
        System.out.println("\n=== Defensive AI Turn ===");
        defensive.takeTurn();
    }
}
```

**Benefits:**
- **Code reuse:** Common algorithm in base class
- **Controlled extension:** Subclasses override specific steps
- **Inversion of control:** Framework calls subclass methods
- **Consistency:** Algorithm structure enforced

**Real-world Examples:**
- **Servlet HttpServlet:** `doGet()`, `doPost()` template
- **Spring AbstractPlatformTransactionManager:** Transaction template
- **JUnit @Before, @Test, @After:** Test execution template
- **Android Activity lifecycle:** `onCreate()`, `onStart()`, etc.

---

## 4. Production Anti-patterns

**What NOT to do - Common mistakes that look like patterns but cause problems**

### 4.1 God Object Anti-pattern

**Problem:** One class knows/does too much

```java
// ❌ BAD - God Object
public class OrderManager {
    // Handles EVERYTHING
    public void processOrder(Order order) {
        // Validate order
        if (order.getItems().isEmpty()) throw new Exception();
        
        // Calculate price
        double total = 0;
        for (Item item : order.getItems()) {
            total += item.getPrice() * item.getQuantity();
        }
        
        // Apply discount
        if (order.getCustomer().isPremium()) {
            total *= 0.9;
        }
        
        // Process payment
        CreditCard card = order.getPaymentMethod();
        // ... payment logic
        
        // Update inventory
        for (Item item : order.getItems()) {
            // ... inventory logic
        }
        
        // Send email
        String email = order.getCustomer().getEmail();
        // ... email logic
        
        // Log to database
        // ... logging logic
        
        // Update analytics
        // ... analytics logic
    }
}

// ✅ GOOD - Separate responsibilities
public class OrderService {
    private final OrderValidator validator;
    private final PriceCalculator calculator;
    private final PaymentProcessor paymentProcessor;
    private final InventoryService inventoryService;
    private final NotificationService notificationService;
    private final OrderRepository orderRepository;
    
    public void processOrder(Order order) {
        validator.validate(order);
        double total = calculator.calculate(order);
        paymentProcessor.process(order, total);
        inventoryService.updateStock(order);
        notificationService.sendConfirmation(order);
        orderRepository.save(order);
    }
}
```

### 4.2 Singleton Abuse

```java
// ❌ BAD - Singleton for everything
public class UserService {
    private static UserService instance;
    
    private UserService() {}
    
    public static UserService getInstance() {
        if (instance == null) {
            instance = new UserService();
        }
        return instance;
    }
}

// Problems:
// - Hard to test (can't mock)
// - Hidden dependencies
// - Global state
// - Thread-safety issues

// ✅ GOOD - Dependency injection
@Service
public class UserService {
    private final UserRepository repository;
    
    public UserService(UserRepository repository) {
        this.repository = repository;
    }
}

// Spring creates single instance, but testable
```

### 4.3 Cargo Cult Programming

**Problem:** Using patterns without understanding why

```java
// ❌ BAD - Factory for everything
public class StringFactory {
    public String createString(String value) {
        return new String(value); // Pointless factory!
    }
}

// ✅ GOOD - Use factory only when needed
String s = "Hello"; // Simple is better
```

---

## 5. Pattern Selection Guide

**When to use which pattern:**

| Problem | Pattern | When to Use |
|---------|---------|-------------|
| Need to create objects without specifying exact class | **Factory Method** | Multiple product types, creation logic varies |
| Need families of related objects | **Abstract Factory** | Multiple product families that work together |
| Complex object construction | **Builder** | Many optional parameters, step-by-step creation |
| Only one instance needed | **Singleton** | Shared resource (config, cache, pool) |
| Expensive object creation | **Prototype** | Cloning cheaper than creation |
| Incompatible interfaces | **Adapter** | Integrate third-party libraries, legacy code |
| Add responsibilities dynamically | **Decorator** | Need flexible, composable behaviors |
| Control access to object | **Proxy** | Lazy loading, access control, remote access |
| Simplify complex subsystem | **Facade** | Multiple subsystems, hide complexity |
| Many similar objects | **Flyweight** | Memory optimization, shared state |
| Runtime algorithm selection | **Strategy** | Multiple algorithms, switch at runtime |
| One-to-many notification | **Observer** | Event handling, publish-subscribe |
| Encapsulate requests | **Command** | Undo/redo, queuing, logging |
| Algorithm skeleton | **Template Method** | Algorithm structure common, steps vary |

---

**End of Design Patterns Module**

**Total Lines (All 4 Parts): ~8,000**

**Next Module:** Move to remaining tasks (Data Lineage, Data Quality, Observability, Cost Optimization)