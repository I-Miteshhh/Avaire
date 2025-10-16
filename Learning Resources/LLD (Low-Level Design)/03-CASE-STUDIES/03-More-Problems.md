# Additional LLD Case Studies

**Difficulty:** Medium to Hard  
**Interview Frequency:** ⭐⭐⭐⭐⭐ (Extremely High)  
**Real-World Relevance:** Critical for 40 LPA SDE-Data roles

---

## 📚 Table of Contents

1. [Parking Lot System](#parking-lot-system)
2. [URL Shortener](#url-shortener)
3. [Notification System](#notification-system)
4. [Distributed Cache](#distributed-cache)

---

## Parking Lot System

### Problem Statement

Design a parking lot system that supports:
- Multiple floors
- Different vehicle types (motorcycle, car, truck)
- Different parking spot sizes
- Entry/exit tracking
- Pricing based on time
- Available spot count

### Requirements

**Functional:**
1. Park vehicle (find appropriate spot)
2. Remove vehicle (calculate fee)
3. Get available spots count
4. Handle multiple floors

**Non-Functional:**
1. Thread-safe (concurrent entry/exit)
2. Efficient spot finding
3. Accurate billing

### Design Patterns Used

- **Factory Pattern:** Create different vehicle types
- **Strategy Pattern:** Different pricing strategies
- **State Pattern:** Parking spot states (available, occupied)
- **Singleton Pattern:** Parking lot instance

### Complete Implementation

```java
// ============================================
// 1. ENUMS
// ============================================

enum VehicleType {
    MOTORCYCLE,
    CAR,
    TRUCK
}

enum SpotSize {
    SMALL,    // Motorcycle
    MEDIUM,   // Car
    LARGE     // Truck
}

enum SpotStatus {
    AVAILABLE,
    OCCUPIED,
    RESERVED
}

// ============================================
// 2. VEHICLE HIERARCHY
// ============================================

abstract class Vehicle {
    protected String licensePlate;
    protected VehicleType type;
    
    public Vehicle(String licensePlate, VehicleType type) {
        this.licensePlate = licensePlate;
        this.type = type;
    }
    
    public abstract SpotSize getRequiredSpotSize();
    
    public String getLicensePlate() {
        return licensePlate;
    }
    
    public VehicleType getType() {
        return type;
    }
}

class Motorcycle extends Vehicle {
    public Motorcycle(String licensePlate) {
        super(licensePlate, VehicleType.MOTORCYCLE);
    }
    
    @Override
    public SpotSize getRequiredSpotSize() {
        return SpotSize.SMALL;
    }
}

class Car extends Vehicle {
    public Car(String licensePlate) {
        super(licensePlate, VehicleType.CAR);
    }
    
    @Override
    public SpotSize getRequiredSpotSize() {
        return SpotSize.MEDIUM;
    }
}

class Truck extends Vehicle {
    public Truck(String licensePlate) {
        super(licensePlate, VehicleType.TRUCK);
    }
    
    @Override
    public SpotSize getRequiredSpotSize() {
        return SpotSize.LARGE;
    }
}

// ============================================
// 3. PARKING SPOT
// ============================================

class ParkingSpot {
    private final int id;
    private final SpotSize size;
    private SpotStatus status;
    private Vehicle currentVehicle;
    
    public ParkingSpot(int id, SpotSize size) {
        this.id = id;
        this.size = size;
        this.status = SpotStatus.AVAILABLE;
    }
    
    public synchronized boolean isAvailable() {
        return status == SpotStatus.AVAILABLE;
    }
    
    public synchronized boolean canFit(Vehicle vehicle) {
        if (!isAvailable()) {
            return false;
        }
        
        SpotSize requiredSize = vehicle.getRequiredSpotSize();
        
        // Large spot can fit any vehicle
        // Medium spot can fit car or motorcycle
        // Small spot can only fit motorcycle
        return size.ordinal() >= requiredSize.ordinal();
    }
    
    public synchronized void parkVehicle(Vehicle vehicle) {
        if (!canFit(vehicle)) {
            throw new IllegalStateException("Vehicle cannot fit in this spot");
        }
        
        this.currentVehicle = vehicle;
        this.status = SpotStatus.OCCUPIED;
    }
    
    public synchronized Vehicle removeVehicle() {
        if (status != SpotStatus.OCCUPIED) {
            throw new IllegalStateException("No vehicle in this spot");
        }
        
        Vehicle vehicle = this.currentVehicle;
        this.currentVehicle = null;
        this.status = SpotStatus.AVAILABLE;
        return vehicle;
    }
    
    public int getId() {
        return id;
    }
    
    public SpotSize getSize() {
        return size;
    }
}

// ============================================
// 4. FLOOR
// ============================================

class ParkingFloor {
    private final int floorNumber;
    private final List<ParkingSpot> spots;
    private final Map<SpotSize, List<ParkingSpot>> spotsBySize;
    
    public ParkingFloor(int floorNumber, int smallSpots, int mediumSpots, int largeSpots) {
        this.floorNumber = floorNumber;
        this.spots = new ArrayList<>();
        this.spotsBySize = new EnumMap<>(SpotSize.class);
        
        for (SpotSize size : SpotSize.values()) {
            spotsBySize.put(size, new ArrayList<>());
        }
        
        int spotId = 0;
        
        // Create small spots
        for (int i = 0; i < smallSpots; i++) {
            ParkingSpot spot = new ParkingSpot(spotId++, SpotSize.SMALL);
            spots.add(spot);
            spotsBySize.get(SpotSize.SMALL).add(spot);
        }
        
        // Create medium spots
        for (int i = 0; i < mediumSpots; i++) {
            ParkingSpot spot = new ParkingSpot(spotId++, SpotSize.MEDIUM);
            spots.add(spot);
            spotsBySize.get(SpotSize.MEDIUM).add(spot);
        }
        
        // Create large spots
        for (int i = 0; i < largeSpots; i++) {
            ParkingSpot spot = new ParkingSpot(spotId++, SpotSize.LARGE);
            spots.add(spot);
            spotsBySize.get(SpotSize.LARGE).add(spot);
        }
    }
    
    /**
     * Find available spot for vehicle
     * Strategy: Try exact size first, then larger sizes
     */
    public ParkingSpot findAvailableSpot(Vehicle vehicle) {
        SpotSize requiredSize = vehicle.getRequiredSpotSize();
        
        // Try exact size first
        for (ParkingSpot spot : spotsBySize.get(requiredSize)) {
            if (spot.isAvailable()) {
                return spot;
            }
        }
        
        // Try larger sizes
        for (SpotSize size : SpotSize.values()) {
            if (size.ordinal() > requiredSize.ordinal()) {
                for (ParkingSpot spot : spotsBySize.get(size)) {
                    if (spot.isAvailable()) {
                        return spot;
                    }
                }
            }
        }
        
        return null;  // No spot available
    }
    
    public int getAvailableSpots() {
        return (int) spots.stream().filter(ParkingSpot::isAvailable).count();
    }
    
    public int getFloorNumber() {
        return floorNumber;
    }
}

// ============================================
// 5. TICKET
// ============================================

class ParkingTicket {
    private final String ticketId;
    private final Vehicle vehicle;
    private final ParkingSpot spot;
    private final int floorNumber;
    private final LocalDateTime entryTime;
    private LocalDateTime exitTime;
    
    public ParkingTicket(String ticketId, Vehicle vehicle, ParkingSpot spot, int floorNumber) {
        this.ticketId = ticketId;
        this.vehicle = vehicle;
        this.spot = spot;
        this.floorNumber = floorNumber;
        this.entryTime = LocalDateTime.now();
    }
    
    public void setExitTime(LocalDateTime exitTime) {
        this.exitTime = exitTime;
    }
    
    public long getParkedHours() {
        LocalDateTime exit = exitTime != null ? exitTime : LocalDateTime.now();
        return ChronoUnit.HOURS.between(entryTime, exit);
    }
    
    public String getTicketId() {
        return ticketId;
    }
    
    public Vehicle getVehicle() {
        return vehicle;
    }
    
    public ParkingSpot getSpot() {
        return spot;
    }
    
    public int getFloorNumber() {
        return floorNumber;
    }
    
    public LocalDateTime getEntryTime() {
        return entryTime;
    }
}

// ============================================
// 6. PRICING STRATEGY
// ============================================

interface PricingStrategy {
    double calculateFee(ParkingTicket ticket);
}

class HourlyPricingStrategy implements PricingStrategy {
    private static final Map<VehicleType, Double> HOURLY_RATES = Map.of(
        VehicleType.MOTORCYCLE, 10.0,
        VehicleType.CAR, 20.0,
        VehicleType.TRUCK, 30.0
    );
    
    @Override
    public double calculateFee(ParkingTicket ticket) {
        long hours = Math.max(1, ticket.getParkedHours());  // Minimum 1 hour
        double hourlyRate = HOURLY_RATES.get(ticket.getVehicle().getType());
        return hours * hourlyRate;
    }
}

class FlatPricingStrategy implements PricingStrategy {
    private static final Map<VehicleType, Double> FLAT_RATES = Map.of(
        VehicleType.MOTORCYCLE, 50.0,
        VehicleType.CAR, 100.0,
        VehicleType.TRUCK, 150.0
    );
    
    @Override
    public double calculateFee(ParkingTicket ticket) {
        return FLAT_RATES.get(ticket.getVehicle().getType());
    }
}

// ============================================
// 7. PARKING LOT (SINGLETON)
// ============================================

class ParkingLot {
    private static volatile ParkingLot instance;
    
    private final List<ParkingFloor> floors;
    private final Map<String, ParkingTicket> activeTickets;
    private final PricingStrategy pricingStrategy;
    private final AtomicInteger ticketCounter;
    
    private ParkingLot(int numFloors, int smallSpots, int mediumSpots, int largeSpots, 
                       PricingStrategy pricingStrategy) {
        this.floors = new ArrayList<>();
        this.activeTickets = new ConcurrentHashMap<>();
        this.pricingStrategy = pricingStrategy;
        this.ticketCounter = new AtomicInteger(0);
        
        for (int i = 0; i < numFloors; i++) {
            floors.add(new ParkingFloor(i, smallSpots, mediumSpots, largeSpots));
        }
    }
    
    public static ParkingLot getInstance(int numFloors, int smallSpots, int mediumSpots, 
                                         int largeSpots, PricingStrategy pricingStrategy) {
        if (instance == null) {
            synchronized (ParkingLot.class) {
                if (instance == null) {
                    instance = new ParkingLot(numFloors, smallSpots, mediumSpots, 
                                              largeSpots, pricingStrategy);
                }
            }
        }
        return instance;
    }
    
    /**
     * Park vehicle - thread-safe
     * Time: O(F * S) where F = floors, S = spots per floor
     */
    public synchronized ParkingTicket parkVehicle(Vehicle vehicle) {
        // Find available spot across all floors
        for (ParkingFloor floor : floors) {
            ParkingSpot spot = floor.findAvailableSpot(vehicle);
            
            if (spot != null) {
                spot.parkVehicle(vehicle);
                
                String ticketId = "T" + ticketCounter.incrementAndGet();
                ParkingTicket ticket = new ParkingTicket(ticketId, vehicle, spot, 
                                                         floor.getFloorNumber());
                activeTickets.put(ticketId, ticket);
                
                return ticket;
            }
        }
        
        throw new IllegalStateException("No available parking spots");
    }
    
    /**
     * Remove vehicle and calculate fee
     * Time: O(1)
     */
    public synchronized double removeVehicle(String ticketId) {
        ParkingTicket ticket = activeTickets.remove(ticketId);
        
        if (ticket == null) {
            throw new IllegalArgumentException("Invalid ticket ID");
        }
        
        ticket.setExitTime(LocalDateTime.now());
        ticket.getSpot().removeVehicle();
        
        return pricingStrategy.calculateFee(ticket);
    }
    
    /**
     * Get total available spots
     */
    public int getAvailableSpots() {
        return floors.stream()
                .mapToInt(ParkingFloor::getAvailableSpots)
                .sum();
    }
}

// ============================================
// 8. USAGE EXAMPLE
// ============================================

class ParkingLotDemo {
    public static void main(String[] args) {
        // Initialize parking lot: 3 floors, 10 small, 20 medium, 5 large spots per floor
        ParkingLot parkingLot = ParkingLot.getInstance(3, 10, 20, 5, 
                                                       new HourlyPricingStrategy());
        
        // Park vehicles
        Vehicle motorcycle = new Motorcycle("MH01AB1234");
        Vehicle car = new Car("MH02CD5678");
        Vehicle truck = new Truck("MH03EF9012");
        
        ParkingTicket ticket1 = parkingLot.parkVehicle(motorcycle);
        ParkingTicket ticket2 = parkingLot.parkVehicle(car);
        ParkingTicket ticket3 = parkingLot.parkVehicle(truck);
        
        System.out.println("Available spots: " + parkingLot.getAvailableSpots());
        
        // Remove vehicle and calculate fee
        double fee = parkingLot.removeVehicle(ticket1.getTicketId());
        System.out.println("Fee for motorcycle: " + fee);
    }
}
```

### Key Design Decisions

1. **Synchronized Methods:** Thread-safe parking/removal
2. **Spot Finding Strategy:** Try exact size first, then larger
3. **Strategy Pattern:** Flexible pricing (hourly vs flat)
4. **ConcurrentHashMap:** Thread-safe ticket storage
5. **AtomicInteger:** Thread-safe ticket ID generation

---

## URL Shortener

### Problem Statement

Design a URL shortener service like bit.ly that:
- Converts long URL to short URL
- Redirects short URL to original long URL
- Handles high throughput (millions of requests/sec)
- Generates unique short URLs
- Supports custom aliases (optional)
- Tracks click analytics

### Requirements

**Functional:**
1. Create short URL from long URL
2. Redirect short URL to long URL
3. Custom short URL (if available)
4. Analytics (click count, timestamps)

**Non-Functional:**
1. Highly available (99.99% uptime)
2. Low latency (<10ms for redirect)
3. Scalable (millions of URLs)
4. Unique short URLs (no collisions)

### Design Patterns Used

- **Factory Pattern:** URL encoder factory
- **Strategy Pattern:** Different encoding strategies (Base62, MD5+Base62)
- **Repository Pattern:** URL storage abstraction
- **Cache-Aside Pattern:** Redis caching for hot URLs

### Complete Implementation

```java
// ============================================
// 1. DOMAIN MODELS
// ============================================

class URL {
    private final String longUrl;
    private final String shortCode;
    private final LocalDateTime createdAt;
    private final LocalDateTime expiresAt;
    private long clickCount;
    
    public URL(String longUrl, String shortCode, LocalDateTime expiresAt) {
        this.longUrl = longUrl;
        this.shortCode = shortCode;
        this.createdAt = LocalDateTime.now();
        this.expiresAt = expiresAt;
        this.clickCount = 0;
    }
    
    public void incrementClickCount() {
        this.clickCount++;
    }
    
    public boolean isExpired() {
        return expiresAt != null && LocalDateTime.now().isAfter(expiresAt);
    }
    
    // Getters
    public String getLongUrl() { return longUrl; }
    public String getShortCode() { return shortCode; }
    public long getClickCount() { return clickCount; }
}

// ============================================
// 2. DISTRIBUTED ID GENERATOR (SNOWFLAKE-LIKE)
// ============================================

/**
 * Generate unique IDs in distributed system
 * 
 * Format (64 bits):
 * - 1 bit: unused (always 0)
 * - 41 bits: timestamp (milliseconds since epoch)
 * - 10 bits: machine ID (supports 1024 machines)
 * - 12 bits: sequence number (4096 IDs per millisecond per machine)
 */
class DistributedIdGenerator {
    private static final long EPOCH = 1609459200000L;  // 2021-01-01 00:00:00 UTC
    private static final long MACHINE_ID_BITS = 10L;
    private static final long SEQUENCE_BITS = 12L;
    private static final long MAX_MACHINE_ID = (1L << MACHINE_ID_BITS) - 1;
    private static final long MAX_SEQUENCE = (1L << SEQUENCE_BITS) - 1;
    
    private final long machineId;
    private long sequence = 0L;
    private long lastTimestamp = -1L;
    
    public DistributedIdGenerator(long machineId) {
        if (machineId > MAX_MACHINE_ID || machineId < 0) {
            throw new IllegalArgumentException("Machine ID must be between 0 and " + MAX_MACHINE_ID);
        }
        this.machineId = machineId;
    }
    
    public synchronized long nextId() {
        long timestamp = System.currentTimeMillis();
        
        if (timestamp < lastTimestamp) {
            throw new RuntimeException("Clock moved backwards");
        }
        
        if (timestamp == lastTimestamp) {
            // Same millisecond - increment sequence
            sequence = (sequence + 1) & MAX_SEQUENCE;
            
            if (sequence == 0) {
                // Sequence exhausted - wait for next millisecond
                timestamp = waitNextMillis(lastTimestamp);
            }
        } else {
            // New millisecond - reset sequence
            sequence = 0L;
        }
        
        lastTimestamp = timestamp;
        
        // Combine: timestamp | machineId | sequence
        return ((timestamp - EPOCH) << (MACHINE_ID_BITS + SEQUENCE_BITS))
                | (machineId << SEQUENCE_BITS)
                | sequence;
    }
    
    private long waitNextMillis(long lastTimestamp) {
        long timestamp = System.currentTimeMillis();
        while (timestamp <= lastTimestamp) {
            timestamp = System.currentTimeMillis();
        }
        return timestamp;
    }
}

// ============================================
// 3. BASE62 ENCODER
// ============================================

class Base62Encoder {
    private static final String BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
    private static final int BASE = BASE62.length();
    
    /**
     * Encode long to Base62 string
     * Example: 125 → "2d"
     */
    public static String encode(long num) {
        if (num == 0) {
            return String.valueOf(BASE62.charAt(0));
        }
        
        StringBuilder sb = new StringBuilder();
        
        while (num > 0) {
            sb.append(BASE62.charAt((int) (num % BASE)));
            num /= BASE;
        }
        
        return sb.reverse().toString();
    }
    
    /**
     * Decode Base62 string to long
     * Example: "2d" → 125
     */
    public static long decode(String str) {
        long num = 0;
        
        for (char c : str.toCharArray()) {
            num = num * BASE + BASE62.indexOf(c);
        }
        
        return num;
    }
}

// ============================================
// 4. URL REPOSITORY (ABSTRACTION)
// ============================================

interface URLRepository {
    void save(URL url);
    URL findByShortCode(String shortCode);
    URL findByLongUrl(String longUrl);
    boolean exists(String shortCode);
}

/**
 * In-memory implementation (for demo)
 * In production: Use MySQL/PostgreSQL + Redis
 */
class InMemoryURLRepository implements URLRepository {
    private final Map<String, URL> shortCodeToUrl = new ConcurrentHashMap<>();
    private final Map<String, URL> longUrlToShortUrl = new ConcurrentHashMap<>();
    
    @Override
    public void save(URL url) {
        shortCodeToUrl.put(url.getShortCode(), url);
        longUrlToShortUrl.put(url.getLongUrl(), url);
    }
    
    @Override
    public URL findByShortCode(String shortCode) {
        return shortCodeToUrl.get(shortCode);
    }
    
    @Override
    public URL findByLongUrl(String longUrl) {
        return longUrlToShortUrl.get(longUrl);
    }
    
    @Override
    public boolean exists(String shortCode) {
        return shortCodeToUrl.containsKey(shortCode);
    }
}

// ============================================
// 5. CACHE LAYER
// ============================================

/**
 * Cache-aside pattern for hot URLs
 */
class URLCache {
    private final Cache<String, String> cache;
    
    public URLCache(int maxSize, int expirationMinutes) {
        this.cache = CacheBuilder.newBuilder()
                .maximumSize(maxSize)
                .expireAfterAccess(expirationMinutes, TimeUnit.MINUTES)
                .build();
    }
    
    public String get(String shortCode) {
        return cache.getIfPresent(shortCode);
    }
    
    public void put(String shortCode, String longUrl) {
        cache.put(shortCode, longUrl);
    }
    
    public void invalidate(String shortCode) {
        cache.invalidate(shortCode);
    }
}

// ============================================
// 6. URL SHORTENER SERVICE
// ============================================

class URLShortenerService {
    private final URLRepository repository;
    private final URLCache cache;
    private final DistributedIdGenerator idGenerator;
    private static final int SHORT_CODE_LENGTH = 7;  // 62^7 = 3.5 trillion URLs
    
    public URLShortenerService(URLRepository repository, URLCache cache, long machineId) {
        this.repository = repository;
        this.cache = cache;
        this.idGenerator = new DistributedIdGenerator(machineId);
    }
    
    /**
     * Create short URL
     * Time: O(1) amortized
     */
    public String createShortUrl(String longUrl, String customAlias, LocalDateTime expiresAt) {
        // Validate long URL
        if (!isValidUrl(longUrl)) {
            throw new IllegalArgumentException("Invalid URL");
        }
        
        // Check if already shortened
        URL existingUrl = repository.findByLongUrl(longUrl);
        if (existingUrl != null && !existingUrl.isExpired()) {
            return existingUrl.getShortCode();
        }
        
        String shortCode;
        
        if (customAlias != null && !customAlias.isEmpty()) {
            // Custom alias
            if (repository.exists(customAlias)) {
                throw new IllegalArgumentException("Custom alias already exists");
            }
            shortCode = customAlias;
        } else {
            // Generate unique short code
            shortCode = generateShortCode();
            
            // Handle collision (rare with 62^7 space)
            while (repository.exists(shortCode)) {
                shortCode = generateShortCode();
            }
        }
        
        URL url = new URL(longUrl, shortCode, expiresAt);
        repository.save(url);
        cache.put(shortCode, longUrl);
        
        return shortCode;
    }
    
    /**
     * Redirect short URL to long URL
     * Time: O(1) with cache, O(log n) without cache
     */
    public String getLongUrl(String shortCode) {
        // Check cache first (hot URLs)
        String cachedUrl = cache.get(shortCode);
        if (cachedUrl != null) {
            return cachedUrl;
        }
        
        // Check database
        URL url = repository.findByShortCode(shortCode);
        
        if (url == null) {
            throw new IllegalArgumentException("Short URL not found");
        }
        
        if (url.isExpired()) {
            throw new IllegalArgumentException("Short URL expired");
        }
        
        // Update analytics
        url.incrementClickCount();
        repository.save(url);
        
        // Update cache
        cache.put(shortCode, url.getLongUrl());
        
        return url.getLongUrl();
    }
    
    /**
     * Generate short code using distributed ID
     */
    private String generateShortCode() {
        long id = idGenerator.nextId();
        String encoded = Base62Encoder.encode(id);
        
        // Pad to fixed length (optional)
        if (encoded.length() < SHORT_CODE_LENGTH) {
            encoded = "0".repeat(SHORT_CODE_LENGTH - encoded.length()) + encoded;
        }
        
        return encoded;
    }
    
    private boolean isValidUrl(String url) {
        try {
            new java.net.URL(url);
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}

// ============================================
// 7. USAGE EXAMPLE
// ============================================

class URLShortenerDemo {
    public static void main(String[] args) {
        URLRepository repository = new InMemoryURLRepository();
        URLCache cache = new URLCache(10000, 60);
        URLShortenerService service = new URLShortenerService(repository, cache, 1);
        
        // Create short URL
        String longUrl = "https://www.example.com/very/long/url/path?param1=value1&param2=value2";
        String shortCode = service.createShortUrl(longUrl, null, null);
        
        System.out.println("Short URL: https://short.url/" + shortCode);
        
        // Redirect
        String redirectUrl = service.getLongUrl(shortCode);
        System.out.println("Redirect to: " + redirectUrl);
        
        // Custom alias
        String customCode = service.createShortUrl(longUrl, "my-custom-link", null);
        System.out.println("Custom short URL: https://short.url/" + customCode);
    }
}
```

### System Design Considerations

**1. Scalability:**
- **Horizontal scaling:** Multiple app servers behind load balancer
- **Database sharding:** Shard by short code hash (consistent hashing)
- **Read replicas:** Handle read-heavy workload

**2. High Availability:**
- **Redis cluster:** Cache with replication
- **Database replication:** Master-slave for reads
- **CDN:** Serve redirects from edge locations

**3. Analytics:**
```java
class URLAnalytics {
    private final String shortCode;
    private final Map<LocalDate, Long> clicksByDate;
    private final Map<String, Long> clicksByCountry;
    private final Map<String, Long> clicksByReferrer;
    
    // Track clicks over time
    public void recordClick(String country, String referrer) {
        LocalDate today = LocalDate.now();
        clicksByDate.merge(today, 1L, Long::sum);
        clicksByCountry.merge(country, 1L, Long::sum);
        clicksByReferrer.merge(referrer, 1L, Long::sum);
    }
}
```

---

## Notification System

### Problem Statement

Design a notification system that supports:
- Multiple channels (email, SMS, push, in-app)
- Priority levels (urgent, high, normal, low)
- User preferences (opt-in/opt-out per channel)
- Retry logic for failed deliveries
- Rate limiting to prevent spam
- Template-based messages

### Requirements

**Functional:**
1. Send notification via multiple channels
2. Support priority-based delivery
3. Respect user preferences
4. Track delivery status
5. Retry failed deliveries

**Non-Functional:**
1. Highly available
2. Low latency for urgent notifications
3. Scalable (millions of notifications/day)
4. Fault-tolerant

### Design Patterns Used

- **Observer Pattern:** Notify subscribers
- **Strategy Pattern:** Different delivery channels
- **Template Method:** Common notification flow
- **Chain of Responsibility:** Retry logic with exponential backoff
- **Factory Pattern:** Create channel-specific senders

### Complete Implementation

```java
// ============================================
// 1. ENUMS AND MODELS
// ============================================

enum NotificationChannel {
    EMAIL,
    SMS,
    PUSH,
    IN_APP
}

enum NotificationPriority {
    URGENT(1),
    HIGH(2),
    NORMAL(3),
    LOW(4);
    
    private final int level;
    
    NotificationPriority(int level) {
        this.level = level;
    }
    
    public int getLevel() {
        return level;
    }
}

enum NotificationStatus {
    PENDING,
    SENT,
    FAILED,
    RETRYING
}

class User {
    private final String userId;
    private final String email;
    private final String phone;
    private final String pushToken;
    private final Set<NotificationChannel> preferences;
    
    public User(String userId, String email, String phone, String pushToken) {
        this.userId = userId;
        this.email = email;
        this.phone = phone;
        this.pushToken = pushToken;
        this.preferences = EnumSet.allOf(NotificationChannel.class);
    }
    
    public void disableChannel(NotificationChannel channel) {
        preferences.remove(channel);
    }
    
    public void enableChannel(NotificationChannel channel) {
        preferences.add(channel);
    }
    
    public boolean isChannelEnabled(NotificationChannel channel) {
        return preferences.contains(channel);
    }
    
    // Getters
    public String getUserId() { return userId; }
    public String getEmail() { return email; }
    public String getPhone() { return phone; }
    public String getPushToken() { return pushToken; }
}

class Notification {
    private final String id;
    private final String userId;
    private final String title;
    private final String message;
    private final NotificationChannel channel;
    private final NotificationPriority priority;
    private NotificationStatus status;
    private int retryCount;
    private final LocalDateTime createdAt;
    private LocalDateTime sentAt;
    
    public Notification(String id, String userId, String title, String message,
                       NotificationChannel channel, NotificationPriority priority) {
        this.id = id;
        this.userId = userId;
        this.title = title;
        this.message = message;
        this.channel = channel;
        this.priority = priority;
        this.status = NotificationStatus.PENDING;
        this.retryCount = 0;
        this.createdAt = LocalDateTime.now();
    }
    
    public void markSent() {
        this.status = NotificationStatus.SENT;
        this.sentAt = LocalDateTime.now();
    }
    
    public void markFailed() {
        this.status = NotificationStatus.FAILED;
    }
    
    public void incrementRetry() {
        this.retryCount++;
        this.status = NotificationStatus.RETRYING;
    }
    
    // Getters
    public String getId() { return id; }
    public String getUserId() { return userId; }
    public String getTitle() { return title; }
    public String getMessage() { return message; }
    public NotificationChannel getChannel() { return channel; }
    public NotificationPriority getPriority() { return priority; }
    public NotificationStatus getStatus() { return status; }
    public int getRetryCount() { return retryCount; }
}

// ============================================
// 2. CHANNEL SENDERS (STRATEGY PATTERN)
// ============================================

interface NotificationSender {
    boolean send(User user, Notification notification);
}

class EmailSender implements NotificationSender {
    @Override
    public boolean send(User user, Notification notification) {
        try {
            // Simulate sending email via AWS SES
            System.out.println("Sending email to " + user.getEmail());
            System.out.println("Subject: " + notification.getTitle());
            System.out.println("Body: " + notification.getMessage());
            
            // Actual implementation:
            // AmazonSimpleEmailService sesClient = AmazonSimpleEmailServiceClientBuilder.defaultClient();
            // SendEmailRequest request = new SendEmailRequest()
            //     .withDestination(new Destination().withToAddresses(user.getEmail()))
            //     .withMessage(new Message()
            //         .withSubject(new Content().withData(notification.getTitle()))
            //         .withBody(new Body().withText(new Content().withData(notification.getMessage()))))
            //     .withSource("noreply@example.com");
            // sesClient.sendEmail(request);
            
            return true;
        } catch (Exception e) {
            System.err.println("Email send failed: " + e.getMessage());
            return false;
        }
    }
}

class SMSSender implements NotificationSender {
    @Override
    public boolean send(User user, Notification notification) {
        try {
            // Simulate sending SMS via AWS SNS
            System.out.println("Sending SMS to " + user.getPhone());
            System.out.println("Message: " + notification.getMessage());
            
            // Actual implementation:
            // AmazonSNS snsClient = AmazonSNSClientBuilder.defaultClient();
            // PublishRequest publishRequest = new PublishRequest()
            //     .withPhoneNumber(user.getPhone())
            //     .withMessage(notification.getMessage());
            // snsClient.publish(publishRequest);
            
            return true;
        } catch (Exception e) {
            System.err.println("SMS send failed: " + e.getMessage());
            return false;
        }
    }
}

class PushNotificationSender implements NotificationSender {
    @Override
    public boolean send(User user, Notification notification) {
        try {
            // Simulate sending push via Firebase Cloud Messaging
            System.out.println("Sending push to token " + user.getPushToken());
            System.out.println("Title: " + notification.getTitle());
            System.out.println("Body: " + notification.getMessage());
            
            // Actual implementation:
            // Message message = Message.builder()
            //     .setNotification(com.google.firebase.messaging.Notification.builder()
            //         .setTitle(notification.getTitle())
            //         .setBody(notification.getMessage())
            //         .build())
            //     .setToken(user.getPushToken())
            //     .build();
            // FirebaseMessaging.getInstance().send(message);
            
            return true;
        } catch (Exception e) {
            System.err.println("Push send failed: " + e.getMessage());
            return false;
        }
    }
}

class InAppNotificationSender implements NotificationSender {
    private final Map<String, List<Notification>> userInbox = new ConcurrentHashMap<>();
    
    @Override
    public boolean send(User user, Notification notification) {
        userInbox.computeIfAbsent(user.getUserId(), k -> new CopyOnWriteArrayList<>())
                 .add(notification);
        System.out.println("In-app notification added to inbox for user " + user.getUserId());
        return true;
    }
    
    public List<Notification> getInbox(String userId) {
        return userInbox.getOrDefault(userId, Collections.emptyList());
    }
}

// ============================================
// 3. SENDER FACTORY
// ============================================

class NotificationSenderFactory {
    private static final Map<NotificationChannel, NotificationSender> senders = new EnumMap<>(NotificationChannel.class);
    
    static {
        senders.put(NotificationChannel.EMAIL, new EmailSender());
        senders.put(NotificationChannel.SMS, new SMSSender());
        senders.put(NotificationChannel.PUSH, new PushNotificationSender());
        senders.put(NotificationChannel.IN_APP, new InAppNotificationSender());
    }
    
    public static NotificationSender getSender(NotificationChannel channel) {
        return senders.get(channel);
    }
}

// ============================================
// 4. RATE LIMITER (TOKEN BUCKET)
// ============================================

class RateLimiter {
    private final int maxTokens;
    private final long refillIntervalMs;
    private final Map<String, TokenBucket> userBuckets;
    
    static class TokenBucket {
        private int tokens;
        private long lastRefillTime;
        
        TokenBucket(int maxTokens) {
            this.tokens = maxTokens;
            this.lastRefillTime = System.currentTimeMillis();
        }
    }
    
    public RateLimiter(int maxTokens, long refillIntervalMs) {
        this.maxTokens = maxTokens;
        this.refillIntervalMs = refillIntervalMs;
        this.userBuckets = new ConcurrentHashMap<>();
    }
    
    public boolean allowNotification(String userId) {
        TokenBucket bucket = userBuckets.computeIfAbsent(userId, k -> new TokenBucket(maxTokens));
        
        synchronized (bucket) {
            refillTokens(bucket);
            
            if (bucket.tokens > 0) {
                bucket.tokens--;
                return true;
            }
            
            return false;
        }
    }
    
    private void refillTokens(TokenBucket bucket) {
        long now = System.currentTimeMillis();
        long timeSinceLastRefill = now - bucket.lastRefillTime;
        
        if (timeSinceLastRefill >= refillIntervalMs) {
            bucket.tokens = maxTokens;
            bucket.lastRefillTime = now;
        }
    }
}

// ============================================
// 5. NOTIFICATION SERVICE
// ============================================

class NotificationService {
    private final Map<String, User> users;
    private final PriorityBlockingQueue<Notification> notificationQueue;
    private final ExecutorService executorService;
    private final RateLimiter rateLimiter;
    private final int maxRetries;
    
    public NotificationService(int threadPoolSize, int maxRetries) {
        this.users = new ConcurrentHashMap<>();
        this.notificationQueue = new PriorityBlockingQueue<>(1000, 
            Comparator.comparing(Notification::getPriority, 
                Comparator.comparingInt(NotificationPriority::getLevel)));
        this.executorService = Executors.newFixedThreadPool(threadPoolSize);
        this.rateLimiter = new RateLimiter(10, 60000);  // 10 notifications per minute
        this.maxRetries = maxRetries;
        
        startWorkers(threadPoolSize);
    }
    
    public void registerUser(User user) {
        users.put(user.getUserId(), user);
    }
    
    /**
     * Send notification (async)
     */
    public void sendNotification(Notification notification) {
        notificationQueue.offer(notification);
    }
    
    /**
     * Worker threads process queue
     */
    private void startWorkers(int threadCount) {
        for (int i = 0; i < threadCount; i++) {
            executorService.submit(() -> {
                while (!Thread.currentThread().isInterrupted()) {
                    try {
                        Notification notification = notificationQueue.take();
                        processNotification(notification);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                        break;
                    }
                }
            });
        }
    }
    
    /**
     * Process single notification
     */
    private void processNotification(Notification notification) {
        User user = users.get(notification.getUserId());
        
        if (user == null) {
            System.err.println("User not found: " + notification.getUserId());
            notification.markFailed();
            return;
        }
        
        // Check user preferences
        if (!user.isChannelEnabled(notification.getChannel())) {
            System.out.println("Channel disabled for user: " + notification.getChannel());
            notification.markFailed();
            return;
        }
        
        // Check rate limit
        if (!rateLimiter.allowNotification(user.getUserId())) {
            System.out.println("Rate limit exceeded for user: " + user.getUserId());
            // Requeue with delay
            scheduleRetry(notification, 60000);  // Retry in 1 minute
            return;
        }
        
        // Send notification
        NotificationSender sender = NotificationSenderFactory.getSender(notification.getChannel());
        boolean success = sender.send(user, notification);
        
        if (success) {
            notification.markSent();
            System.out.println("Notification sent successfully: " + notification.getId());
        } else {
            handleFailure(notification);
        }
    }
    
    /**
     * Retry logic with exponential backoff
     */
    private void handleFailure(Notification notification) {
        if (notification.getRetryCount() < maxRetries) {
            notification.incrementRetry();
            
            // Exponential backoff: 1s, 2s, 4s, 8s, ...
            long delayMs = (long) Math.pow(2, notification.getRetryCount()) * 1000;
            scheduleRetry(notification, delayMs);
            
            System.out.println("Scheduling retry " + notification.getRetryCount() + 
                             " after " + delayMs + "ms for notification: " + notification.getId());
        } else {
            notification.markFailed();
            System.err.println("Notification failed after " + maxRetries + " retries: " + 
                             notification.getId());
        }
    }
    
    private void scheduleRetry(Notification notification, long delayMs) {
        ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();
        scheduler.schedule(() -> notificationQueue.offer(notification), delayMs, TimeUnit.MILLISECONDS);
        scheduler.shutdown();
    }
    
    public void shutdown() {
        executorService.shutdownNow();
    }
}

// ============================================
// 6. USAGE EXAMPLE
// ============================================

class NotificationSystemDemo {
    public static void main(String[] args) throws InterruptedException {
        NotificationService service = new NotificationService(4, 3);
        
        // Register users
        User user1 = new User("user1", "user1@example.com", "+1234567890", "fcm-token-123");
        User user2 = new User("user2", "user2@example.com", "+0987654321", "fcm-token-456");
        
        service.registerUser(user1);
        service.registerUser(user2);
        
        // Send notifications
        Notification urgentEmail = new Notification(
            UUID.randomUUID().toString(),
            "user1",
            "Security Alert",
            "Suspicious login detected",
            NotificationChannel.EMAIL,
            NotificationPriority.URGENT
        );
        
        Notification normalPush = new Notification(
            UUID.randomUUID().toString(),
            "user2",
            "New Message",
            "You have a new message",
            NotificationChannel.PUSH,
            NotificationPriority.NORMAL
        );
        
        service.sendNotification(urgentEmail);
        service.sendNotification(normalPush);
        
        // Wait for processing
        Thread.sleep(5000);
        
        service.shutdown();
    }
}
```

### Key Features

1. **Priority Queue:** Urgent notifications processed first
2. **Rate Limiting:** Token bucket prevents spam
3. **Retry Logic:** Exponential backoff for failed deliveries
4. **User Preferences:** Respect opt-in/opt-out
5. **Multi-Channel:** Email, SMS, Push, In-App

---

## Distributed Cache

### Problem Statement

Design a distributed cache system like Redis/Memcached that:
- Stores key-value pairs in memory
- Supports TTL (time-to-live) for entries
- Handles cache eviction (LRU, LFU, FIFO)
- Distributes data across multiple nodes
- Supports high throughput (millions of operations/sec)
- Provides eventual consistency

### Requirements

**Functional:**
1. `get(key)` - retrieve value
2. `put(key, value, ttl)` - store with TTL
3. `delete(key)` - remove entry
4. Cache eviction when full

**Non-Functional:**
1. High availability (99.99% uptime)
2. Low latency (<1ms for get)
3. Scalable (add/remove nodes dynamically)
4. Fault-tolerant (data replication)

### Design Patterns Used

- **Strategy Pattern:** Different eviction policies (LRU, LFU)
- **Singleton Pattern:** Cache instance per node
- **Proxy Pattern:** Cache client with routing logic
- **Observer Pattern:** Notify on cache events

### Complete Implementation

```java
// ============================================
// 1. CACHE ENTRY
// ============================================

class CacheEntry<V> {
    private final V value;
    private final long createdAt;
    private final long ttlMs;
    private long lastAccessTime;
    private int accessCount;
    
    public CacheEntry(V value, long ttlMs) {
        this.value = value;
        this.createdAt = System.currentTimeMillis();
        this.ttlMs = ttlMs;
        this.lastAccessTime = createdAt;
        this.accessCount = 1;
    }
    
    public boolean isExpired() {
        return ttlMs > 0 && (System.currentTimeMillis() - createdAt) > ttlMs;
    }
    
    public void access() {
        this.lastAccessTime = System.currentTimeMillis();
        this.accessCount++;
    }
    
    public V getValue() {
        return value;
    }
    
    public long getLastAccessTime() {
        return lastAccessTime;
    }
    
    public int getAccessCount() {
        return accessCount;
    }
}

// ============================================
// 2. EVICTION POLICY (STRATEGY PATTERN)
// ============================================

interface EvictionPolicy<K> {
    void recordAccess(K key);
    K evict();
}

/**
 * LRU (Least Recently Used) Eviction
 * Uses LinkedHashMap with access order
 */
class LRUEvictionPolicy<K> implements EvictionPolicy<K> {
    private final LinkedHashMap<K, Long> accessOrder;
    
    public LRUEvictionPolicy() {
        this.accessOrder = new LinkedHashMap<>(16, 0.75f, true);  // Access order
    }
    
    @Override
    public void recordAccess(K key) {
        accessOrder.put(key, System.currentTimeMillis());
    }
    
    @Override
    public K evict() {
        if (accessOrder.isEmpty()) {
            return null;
        }
        
        // Remove oldest entry (first in LinkedHashMap)
        Iterator<K> iterator = accessOrder.keySet().iterator();
        K oldest = iterator.next();
        iterator.remove();
        return oldest;
    }
}

/**
 * LFU (Least Frequently Used) Eviction
 * Uses min heap by access count
 */
class LFUEvictionPolicy<K> implements EvictionPolicy<K> {
    private final Map<K, Integer> frequency;
    private final PriorityQueue<Map.Entry<K, Integer>> minHeap;
    
    public LFUEvictionPolicy() {
        this.frequency = new ConcurrentHashMap<>();
        this.minHeap = new PriorityQueue<>(Map.Entry.comparingByValue());
    }
    
    @Override
    public void recordAccess(K key) {
        frequency.merge(key, 1, Integer::sum);
    }
    
    @Override
    public K evict() {
        // Rebuild heap (in production, use more efficient data structure)
        minHeap.clear();
        minHeap.addAll(frequency.entrySet());
        
        if (minHeap.isEmpty()) {
            return null;
        }
        
        Map.Entry<K, Integer> leastFrequent = minHeap.poll();
        frequency.remove(leastFrequent.getKey());
        return leastFrequent.getKey();
    }
}

// ============================================
// 3. LOCAL CACHE (SINGLE NODE)
// ============================================

class LocalCache<K, V> {
    private final int maxSize;
    private final ConcurrentHashMap<K, CacheEntry<V>> cache;
    private final EvictionPolicy<K> evictionPolicy;
    private final ReadWriteLock lock;
    
    public LocalCache(int maxSize, EvictionPolicy<K> evictionPolicy) {
        this.maxSize = maxSize;
        this.cache = new ConcurrentHashMap<>();
        this.evictionPolicy = evictionPolicy;
        this.lock = new ReentrantReadWriteLock();
        
        startEvictionThread();
    }
    
    /**
     * Get value from cache
     * Time: O(1)
     */
    public V get(K key) {
        lock.readLock().lock();
        try {
            CacheEntry<V> entry = cache.get(key);
            
            if (entry == null) {
                return null;  // Cache miss
            }
            
            if (entry.isExpired()) {
                cache.remove(key);
                return null;  // Expired
            }
            
            entry.access();
            evictionPolicy.recordAccess(key);
            
            return entry.getValue();
        } finally {
            lock.readLock().unlock();
        }
    }
    
    /**
     * Put value in cache
     * Time: O(1) amortized
     */
    public void put(K key, V value, long ttlMs) {
        lock.writeLock().lock();
        try {
            // Evict if at capacity
            if (cache.size() >= maxSize && !cache.containsKey(key)) {
                K evictKey = evictionPolicy.evict();
                if (evictKey != null) {
                    cache.remove(evictKey);
                }
            }
            
            CacheEntry<V> entry = new CacheEntry<>(value, ttlMs);
            cache.put(key, entry);
            evictionPolicy.recordAccess(key);
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    /**
     * Delete from cache
     */
    public void delete(K key) {
        lock.writeLock().lock();
        try {
            cache.remove(key);
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    /**
     * Background thread to clean expired entries
     */
    private void startEvictionThread() {
        ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();
        
        scheduler.scheduleAtFixedRate(() -> {
            cache.entrySet().removeIf(entry -> entry.getValue().isExpired());
        }, 1, 1, TimeUnit.MINUTES);
    }
    
    public int size() {
        return cache.size();
    }
}

// ============================================
// 4. CONSISTENT HASHING (DISTRIBUTION)
// ============================================

class ConsistentHashing<T> {
    private final int virtualNodes;
    private final TreeMap<Integer, T> ring;
    private final MessageDigest md;
    
    public ConsistentHashing(int virtualNodes) {
        this.virtualNodes = virtualNodes;
        this.ring = new TreeMap<>();
        
        try {
            this.md = MessageDigest.getInstance("MD5");
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("MD5 not available", e);
        }
    }
    
    /**
     * Add node to ring
     */
    public void addNode(T node) {
        for (int i = 0; i < virtualNodes; i++) {
            int hash = hash(node.toString() + i);
            ring.put(hash, node);
        }
    }
    
    /**
     * Remove node from ring
     */
    public void removeNode(T node) {
        for (int i = 0; i < virtualNodes; i++) {
            int hash = hash(node.toString() + i);
            ring.remove(hash);
        }
    }
    
    /**
     * Get node for key
     */
    public T getNode(String key) {
        if (ring.isEmpty()) {
            return null;
        }
        
        int hash = hash(key);
        
        // Find first node >= hash (clockwise)
        Map.Entry<Integer, T> entry = ring.ceilingEntry(hash);
        
        if (entry == null) {
            // Wrap around to first node
            entry = ring.firstEntry();
        }
        
        return entry.getValue();
    }
    
    private int hash(String key) {
        md.reset();
        md.update(key.getBytes());
        byte[] digest = md.digest();
        
        // Use first 4 bytes as int
        return ((digest[0] & 0xFF) << 24)
             | ((digest[1] & 0xFF) << 16)
             | ((digest[2] & 0xFF) << 8)
             | (digest[3] & 0xFF);
    }
}

// ============================================
// 5. DISTRIBUTED CACHE
// ============================================

class CacheNode {
    private final String nodeId;
    private final LocalCache<String, String> localCache;
    
    public CacheNode(String nodeId, int maxSize) {
        this.nodeId = nodeId;
        this.localCache = new LocalCache<>(maxSize, new LRUEvictionPolicy<>());
    }
    
    public String get(String key) {
        return localCache.get(key);
    }
    
    public void put(String key, String value, long ttlMs) {
        localCache.put(key, value, ttlMs);
    }
    
    public void delete(String key) {
        localCache.delete(key);
    }
    
    public String getNodeId() {
        return nodeId;
    }
    
    @Override
    public String toString() {
        return nodeId;
    }
}

class DistributedCache {
    private final ConsistentHashing<CacheNode> consistentHashing;
    private final Map<String, CacheNode> nodes;
    
    public DistributedCache() {
        this.consistentHashing = new ConsistentHashing<>(150);  // 150 virtual nodes
        this.nodes = new ConcurrentHashMap<>();
    }
    
    /**
     * Add cache node
     */
    public void addNode(String nodeId, int maxSize) {
        CacheNode node = new CacheNode(nodeId, maxSize);
        nodes.put(nodeId, node);
        consistentHashing.addNode(node);
        System.out.println("Added node: " + nodeId);
    }
    
    /**
     * Remove cache node
     */
    public void removeNode(String nodeId) {
        CacheNode node = nodes.remove(nodeId);
        if (node != null) {
            consistentHashing.removeNode(node);
            System.out.println("Removed node: " + nodeId);
        }
    }
    
    /**
     * Get value (routes to appropriate node)
     */
    public String get(String key) {
        CacheNode node = consistentHashing.getNode(key);
        
        if (node == null) {
            return null;
        }
        
        return node.get(key);
    }
    
    /**
     * Put value (routes to appropriate node)
     */
    public void put(String key, String value, long ttlMs) {
        CacheNode node = consistentHashing.getNode(key);
        
        if (node == null) {
            throw new IllegalStateException("No cache nodes available");
        }
        
        node.put(key, value, ttlMs);
    }
    
    /**
     * Delete value
     */
    public void delete(String key) {
        CacheNode node = consistentHashing.getNode(key);
        
        if (node != null) {
            node.delete(key);
        }
    }
}

// ============================================
// 6. USAGE EXAMPLE
// ============================================

class DistributedCacheDemo {
    public static void main(String[] args) {
        DistributedCache cache = new DistributedCache();
        
        // Add 3 nodes
        cache.addNode("node1", 1000);
        cache.addNode("node2", 1000);
        cache.addNode("node3", 1000);
        
        // Put values
        cache.put("user:1", "Alice", 60000);  // 1 minute TTL
        cache.put("user:2", "Bob", 60000);
        cache.put("user:3", "Charlie", 60000);
        
        // Get values
        System.out.println("user:1 = " + cache.get("user:1"));
        System.out.println("user:2 = " + cache.get("user:2"));
        
        // Remove node (data redistributed)
        cache.removeNode("node2");
        
        System.out.println("user:1 = " + cache.get("user:1"));  // May miss
    }
}
```

### System Design Considerations

**1. Replication:**
```java
class ReplicatedCache {
    private final DistributedCache cache;
    private final int replicationFactor;
    
    public void put(String key, String value, long ttlMs) {
        // Write to primary and replicas
        List<CacheNode> nodes = getNodesForKey(key, replicationFactor);
        
        for (CacheNode node : nodes) {
            node.put(key, value, ttlMs);
        }
    }
}
```

**2. Monitoring:**
```java
class CacheMetrics {
    private final AtomicLong hits = new AtomicLong(0);
    private final AtomicLong misses = new AtomicLong(0);
    
    public double getHitRate() {
        long totalRequests = hits.get() + misses.get();
        return totalRequests > 0 ? (double) hits.get() / totalRequests : 0.0;
    }
}
```

---

## 🎯 Interview Tips

### Common Questions

1. **"How would you handle cache invalidation in distributed system?"**
   - Use TTL for automatic expiration
   - Implement cache-aside pattern (application manages)
   - Use publish-subscribe for invalidation events

2. **"How to ensure consistency between cache and database?"**
   - Write-through: Write to cache and DB synchronously
   - Write-behind: Write to cache, async to DB
   - Cache-aside: Application manages both

3. **"How to handle hot keys in distributed cache?"**
   - Replicate hot keys across multiple nodes
   - Use local cache (L1) + distributed cache (L2)
   - Implement rate limiting per key

---

**Next:** [Concurrency Patterns](../04-CONCURRENCY-PATTERNS/PATTERNS.md)
