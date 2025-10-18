# Part 2: Flink Sessionization Job

**Component:** Apache Flink Streaming Job  
**Function:** User Session Analytics  
**Latency Target:** < 10 seconds  

---

## Table of Contents

1. [Session

ization Concept](#sessionization-concept)
2. [Flink Job Architecture](#flink-job-architecture)
3. [Implementation](#implementation)
4. [Watermarks & Late Data](#watermarks--late-data)
5. [State Management](#state-management)
6. [Testing](#testing)

---

## 1. Sessionization Concept

### What is Sessionization?

**Definition:** Group user events into sessions based on inactivity timeout.

```
User Events Timeline:

Event 1 ───┐
           │
Event 2 ───┤  Session 1
           │  (30 min activity)
Event 3 ───┘

           [Gap: 31 minutes - session timeout]

Event 4 ───┐
           │  Session 2
Event 5 ───┘
```

**Session Definition:**
- All events from same user
- Max 30 minutes between consecutive events
- Session ends after 30 min inactivity

**Use Cases:**
- User engagement metrics (session duration, pages per session)
- Conversion funnel analysis
- Abandoned cart detection
- User journey mapping

**Real-World Examples:**
- **Google Analytics:** Session timeout = 30 minutes
- **Amazon:** Track shopping sessions for recommendations
- **Netflix:** Watch sessions for viewing analytics

---

## 2. Flink Job Architecture

### Processing Flow

```
Kafka Source
    ↓
Parse JSON
    ↓
Extract Timestamp & Watermark
    ↓
Key By user_id
    ↓
Session Window (30 min gap)
    ↓
Aggregate Events
    ↓
Calculate Session Metrics
    ↓
Sinks: Iceberg + Redis
```

### Window Types

```
┌──────────────────────────────────────────────────────────┐
│            Session Window (Event Time)                   │
│                                                           │
│  User A:  [Event 1]──[Event 2]──[Event 3]               │
│           └──────────────30 min──────────────┘           │
│                                                           │
│           [30 min gap - session ends]                     │
│                                                           │
│           [Event 4]──[Event 5]                           │
│           └──────15 min──────┘                           │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

---

## 3. Implementation

### Maven Dependencies

```xml
<!-- flink-jobs/pom.xml -->
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.dateng</groupId>
    <artifactId>flink-jobs</artifactId>
    <version>1.0.0</version>
    
    <properties>
        <java.version>11</java.version>
        <flink.version>1.18.0</flink.version>
        <scala.binary.version>2.12</scala.binary.version>
        <kafka.version>3.5.0</kafka.version>
        <iceberg.version>1.4.0</iceberg.version>
    </properties>
    
    <dependencies>
        <!-- Flink core -->
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-streaming-java</artifactId>
            <version>${flink.version}</version>
            <scope>provided</scope>
        </dependency>
        
        <!-- Flink Kafka connector -->
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-connector-kafka</artifactId>
            <version>3.0.0-1.18</version>
        </dependency>
        
        <!-- Flink Iceberg connector -->
        <dependency>
            <groupId>org.apache.iceberg</groupId>
            <artifactId>iceberg-flink-runtime-1.18</artifactId>
            <version>${iceberg.version}</version>
        </dependency>
        
        <!-- JSON serialization -->
        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-databind</artifactId>
            <version>2.15.2</version>
        </dependency>
        
        <dependency>
            <groupId>com.fasterxml.jackson.datatype</groupId>
            <artifactId>jackson-datatype-jsr310</artifactId>
            <version>2.15.2</version>
        </dependency>
        
        <!-- Testing -->
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-test-utils</artifactId>
            <version>${flink.version}</version>
            <scope>test</scope>
        </dependency>
        
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <version>4.13.2</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-shade-plugin</artifactId>
                <version>3.5.0</version>
                <executions>
                    <execution>
                        <phase>package</phase>
                        <goals>
                            <goal>shade</goal>
                        </goals>
                        <configuration>
                            <artifactSet>
                                <excludes>
                                    <exclude>org.apache.flink:flink-shaded-force-shading</exclude>
                                    <exclude>com.google.code.findbugs:jsr305</exclude>
                                </excludes>
                            </artifactSet>
                            <filters>
                                <filter>
                                    <artifact>*:*</artifact>
                                    <excludes>
                                        <exclude>META-INF/*.SF</exclude>
                                        <exclude>META-INF/*.DSA</exclude>
                                        <exclude>META-INF/*.RSA</exclude>
                                    </excludes>
                                </filter>
                            </filters>
                            <transformers>
                                <transformer implementation="org.apache.maven.plugins.shade.resource.ManifestResourceTransformer">
                                    <mainClass>com.dateng.SessionizationJob</mainClass>
                                </transformer>
                            </transformers>
                        </configuration>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>
```

### Session Schema

```java
// flink-jobs/src/main/java/com/dateng/schema/Session.java
package com.dateng.schema;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.io.Serializable;
import java.time.Instant;
import java.util.List;

/**
 * User session aggregate
 */
public class Session implements Serializable {
    
    @JsonProperty("session_id")
    private String sessionId;
    
    @JsonProperty("user_id")
    private String userId;
    
    @JsonProperty("start_time")
    private Instant startTime;
    
    @JsonProperty("end_time")
    private Instant endTime;
    
    @JsonProperty("duration_seconds")
    private long durationSeconds;
    
    @JsonProperty("event_count")
    private int eventCount;
    
    @JsonProperty("page_view_count")
    private int pageViewCount;
    
    @JsonProperty("click_count")
    private int clickCount;
    
    @JsonProperty("purchase_count")
    private int purchaseCount;
    
    @JsonProperty("pages_visited")
    private List<String> pagesVisited;
    
    @JsonProperty("entry_page")
    private String entryPage;
    
    @JsonProperty("exit_page")
    private String exitPage;
    
    @JsonProperty("referrer")
    private String referrer;
    
    @JsonProperty("device_type")
    private String deviceType;
    
    @JsonProperty("country")
    private String country;
    
    @JsonProperty("conversion")
    private boolean conversion;  // Did user purchase?
    
    @JsonProperty("revenue")
    private double revenue;
    
    // Constructors
    public Session() {}
    
    public Session(String sessionId, String userId) {
        this.sessionId = sessionId;
        this.userId = userId;
    }
    
    // Getters and setters
    public String getSessionId() { return sessionId; }
    public void setSessionId(String sessionId) { this.sessionId = sessionId; }
    
    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }
    
    public Instant getStartTime() { return startTime; }
    public void setStartTime(Instant startTime) { this.startTime = startTime; }
    
    public Instant getEndTime() { return endTime; }
    public void setEndTime(Instant endTime) { this.endTime = endTime; }
    
    public long getDurationSeconds() { return durationSeconds; }
    public void setDurationSeconds(long durationSeconds) { this.durationSeconds = durationSeconds; }
    
    public int getEventCount() { return eventCount; }
    public void setEventCount(int eventCount) { this.eventCount = eventCount; }
    
    public int getPageViewCount() { return pageViewCount; }
    public void setPageViewCount(int pageViewCount) { this.pageViewCount = pageViewCount; }
    
    public int getClickCount() { return clickCount; }
    public void setClickCount(int clickCount) { this.clickCount = clickCount; }
    
    public int getPurchaseCount() { return purchaseCount; }
    public void setPurchaseCount(int purchaseCount) { this.purchaseCount = purchaseCount; }
    
    public List<String> getPagesVisited() { return pagesVisited; }
    public void setPagesVisited(List<String> pagesVisited) { this.pagesVisited = pagesVisited; }
    
    public String getEntryPage() { return entryPage; }
    public void setEntryPage(String entryPage) { this.entryPage = entryPage; }
    
    public String getExitPage() { return exitPage; }
    public void setExitPage(String exitPage) { this.exitPage = exitPage; }
    
    public String getReferrer() { return referrer; }
    public void setReferrer(String referrer) { this.referrer = referrer; }
    
    public String getDeviceType() { return deviceType; }
    public void setDeviceType(String deviceType) { this.deviceType = deviceType; }
    
    public String getCountry() { return country; }
    public void setCountry(String country) { this.country = country; }
    
    public boolean isConversion() { return conversion; }
    public void setConversion(boolean conversion) { this.conversion = conversion; }
    
    public double getRevenue() { return revenue; }
    public void setRevenue(double revenue) { this.revenue = revenue; }
    
    @Override
    public String toString() {
        return String.format(
            "Session{sessionId=%s, userId=%s, events=%d, duration=%ds, conversion=%s}",
            sessionId, userId, eventCount, durationSeconds, conversion
        );
    }
}
```

### Session Window Function

```java
// flink-jobs/src/main/java/com/dateng/functions/SessionAggregateFunction.java
package com.dateng.functions;

import com.dateng.schema.ClickstreamEvent;
import com.dateng.schema.Session;
import org.apache.flink.api.common.functions.AggregateFunction;

import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

/**
 * Aggregate function for session windows
 * 
 * Accumulates events into a session object
 */
public class SessionAggregateFunction 
    implements AggregateFunction<ClickstreamEvent, SessionAccumulator, Session> {
    
    @Override
    public SessionAccumulator createAccumulator() {
        return new SessionAccumulator();
    }
    
    @Override
    public SessionAccumulator add(ClickstreamEvent event, SessionAccumulator acc) {
        // First event in session
        if (acc.sessionId == null) {
            acc.sessionId = event.getSessionId();
            acc.userId = event.getUserId();
            acc.startTime = event.getTimestamp();
            acc.entryPage = event.getPageUrl();
            acc.referrer = event.getReferrer();
            acc.deviceType = event.getDevice() != null ? event.getDevice().getType() : null;
            acc.country = event.getGeo() != null ? event.getGeo().getCountry() : null;
        }
        
        // Update accumulator
        acc.eventCount++;
        acc.endTime = event.getTimestamp();
        acc.exitPage = event.getPageUrl();
        
        // Track event types
        String eventType = event.getEventType();
        if ("page_view".equals(eventType)) {
            acc.pageViewCount++;
        } else if ("click".equals(eventType)) {
            acc.clickCount++;
        } else if ("purchase".equals(eventType)) {
            acc.purchaseCount++;
            acc.conversion = true;
            
            // Extract revenue from metadata
            if (event.getMetadata() != null && event.getMetadata().containsKey("amount")) {
                try {
                    acc.revenue += Double.parseDouble(event.getMetadata().get("amount"));
                } catch (NumberFormatException e) {
                    // Ignore invalid amount
                }
            }
        }
        
        // Track pages visited
        if (!acc.pagesVisited.contains(event.getPageUrl())) {
            acc.pagesVisited.add(event.getPageUrl());
        }
        
        return acc;
    }
    
    @Override
    public Session getResult(SessionAccumulator acc) {
        Session session = new Session(acc.sessionId, acc.userId);
        session.setStartTime(acc.startTime);
        session.setEndTime(acc.endTime);
        session.setDurationSeconds(Duration.between(acc.startTime, acc.endTime).getSeconds());
        session.setEventCount(acc.eventCount);
        session.setPageViewCount(acc.pageViewCount);
        session.setClickCount(acc.clickCount);
        session.setPurchaseCount(acc.purchaseCount);
        session.setPagesVisited(new ArrayList<>(acc.pagesVisited));
        session.setEntryPage(acc.entryPage);
        session.setExitPage(acc.exitPage);
        session.setReferrer(acc.referrer);
        session.setDeviceType(acc.deviceType);
        session.setCountry(acc.country);
        session.setConversion(acc.conversion);
        session.setRevenue(acc.revenue);
        
        return session;
    }
    
    @Override
    public SessionAccumulator merge(SessionAccumulator acc1, SessionAccumulator acc2) {
        // Merge two accumulators (needed for combining partial results)
        acc1.eventCount += acc2.eventCount;
        acc1.pageViewCount += acc2.pageViewCount;
        acc1.clickCount += acc2.clickCount;
        acc1.purchaseCount += acc2.purchaseCount;
        
        if (acc2.endTime.isAfter(acc1.endTime)) {
            acc1.endTime = acc2.endTime;
            acc1.exitPage = acc2.exitPage;
        }
        
        acc1.pagesVisited.addAll(acc2.pagesVisited);
        acc1.conversion = acc1.conversion || acc2.conversion;
        acc1.revenue += acc2.revenue;
        
        return acc1;
    }
    
    /**
     * Accumulator for session aggregation
     */
    public static class SessionAccumulator {
        String sessionId;
        String userId;
        Instant startTime;
        Instant endTime;
        int eventCount = 0;
        int pageViewCount = 0;
        int clickCount = 0;
        int purchaseCount = 0;
        List<String> pagesVisited = new ArrayList<>();
        String entryPage;
        String exitPage;
        String referrer;
        String deviceType;
        String country;
        boolean conversion = false;
        double revenue = 0.0;
    }
}
```

### Main Sessionization Job

```java
// flink-jobs/src/main/java/com/dateng/SessionizationJob.java
package com.dateng;

import com.dateng.functions.SessionAggregateFunction;
import com.dateng.schema.ClickstreamEvent;
import com.dateng.schema.Session;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.windowing.assigners.EventTimeSessionWindows;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;

/**
 * Flink job for user sessionization
 * 
 * Reads clickstream events from Kafka, groups them into sessions,
 * and writes session metrics to Iceberg and Redis
 * 
 * Session definition: Events from same user with max 30 min gap
 */
public class SessionizationJob {
    
    private static final Logger LOG = LoggerFactory.getLogger(SessionizationJob.class);
    
    // Configuration
    private static final String KAFKA_BROKERS = "kafka-1:9092,kafka-2:9092,kafka-3:9092";
    private static final String KAFKA_TOPIC = "clickstream_events";
    private static final String CONSUMER_GROUP = "sessionization-job";
    private static final Duration SESSION_GAP = Duration.ofMinutes(30);
    private static final Duration MAX_OUT_OF_ORDERNESS = Duration.ofMinutes(5);
    
    public static void main(String[] args) throws Exception {
        LOG.info("Starting Sessionization Job");
        
        // Create execution environment
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        
        // Configure environment
        env.setParallelism(30);  // Match number of Kafka partitions
        env.enableCheckpointing(60000);  // Checkpoint every minute
        
        // Kafka source
        KafkaSource<String> kafkaSource = KafkaSource.<String>builder()
            .setBootstrapServers(KAFKA_BROKERS)
            .setTopics(KAFKA_TOPIC)
            .setGroupId(CONSUMER_GROUP)
            .setStartingOffsets(OffsetsInitializer.earliest())
            .setValueOnlyDeserializer(new SimpleStringSchema())
            .build();
        
        // Read from Kafka
        DataStream<String> kafkaStream = env.fromSource(
            kafkaSource,
            WatermarkStrategy.noWatermarks(),
            "Kafka Source"
        );
        
        // Parse JSON to ClickstreamEvent
        DataStream<ClickstreamEvent> eventStream = kafkaStream
            .map(json -> ClickstreamEvent.fromJson(json))
            .name("Parse JSON");
        
        // Assign watermarks (for event time processing)
        DataStream<ClickstreamEvent> eventsWithWatermarks = eventStream
            .assignTimestampsAndWatermarks(
                WatermarkStrategy
                    .<ClickstreamEvent>forBoundedOutOfOrderness(MAX_OUT_OF_ORDERNESS)
                    .withTimestampAssigner((event, timestamp) -> 
                        event.getTimestamp().toEpochMilli())
            )
            .name("Assign Watermarks");
        
        // Group by user_id and apply session window
        DataStream<Session> sessions = eventsWithWatermarks
            .keyBy(ClickstreamEvent::getUserId)
            .window(EventTimeSessionWindows.withGap(Time.minutes(30)))
            .aggregate(new SessionAggregateFunction())
            .name("Sessionize");
        
        // Write to Iceberg (for analytics)
        sessions
            .addSink(new IcebergSessionSink())
            .name("Write to Iceberg");
        
        // Write to Redis (for real-time dashboards)
        sessions
            .addSink(new RedisSessionSink())
            .name("Write to Redis");
        
        // Execute job
        env.execute("Sessionization Job");
    }
    
    /**
     * Iceberg sink for sessions
     */
    private static class IcebergSessionSink 
        implements org.apache.flink.streaming.api.functions.sink.SinkFunction<Session> {
        
        @Override
        public void invoke(Session session, Context context) {
            // TODO: Implement Iceberg write
            LOG.info("Writing session to Iceberg: {}", session);
        }
    }
    
    /**
     * Redis sink for sessions
     */
    private static class RedisSessionSink 
        implements org.apache.flink.streaming.api.functions.sink.SinkFunction<Session> {
        
        @Override
        public void invoke(Session session, Context context) {
            // TODO: Implement Redis write
            LOG.info("Writing session to Redis: {}", session);
        }
    }
}
```

---

## 4. Watermarks & Late Data

### What are Watermarks?

**Watermark:** Signal that indicates event time has progressed to a certain point.

```
Events arrive out of order:

Timeline:    10:00  10:05  10:10  10:15  10:20
Arrival:     E3     E1     E2     E5     E4
Event Time:  10:10  10:00  10:05  10:20  10:15

Watermark Strategy:
- Wait 5 minutes for late data
- Watermark(t) = max_event_time - 5 min

When event at 10:20 arrives:
  Watermark = 10:20 - 5 min = 10:15
  Trigger windows ending before 10:15
```

### Configuration

```java
WatermarkStrategy
    .<ClickstreamEvent>forBoundedOutOfOrderness(Duration.ofMinutes(5))
    .withTimestampAssigner((event, timestamp) -> 
        event.getTimestamp().toEpochMilli())
    .withIdleness(Duration.ofMinutes(1))  // Handle idle partitions
```

**Parameters:**
- `BoundedOutOfOrderness(5 min)`: Wait 5 minutes for late events
- `IdleTimeout(1 min)`: Don't wait forever for idle partitions

### Late Data Handling

```java
// Configure late data handling
DataStream<Session> sessions = eventsWithWatermarks
    .keyBy(ClickstreamEvent::getUserId)
    .window(EventTimeSessionWindows.withGap(Time.minutes(30)))
    .allowedLateness(Time.minutes(5))  // Accept events up to 5 min late
    .sideOutputLateData(lateDataTag)   // Send late data to side output
    .aggregate(new SessionAggregateFunction());

// Process late data separately
DataStream<ClickstreamEvent> lateData = sessions.getSideOutput(lateDataTag);
lateData.addSink(new KafkaSink("clickstream_events_dlq"));
```

---

## 5. State Management

### Checkpointing

**Purpose:** Enable fault tolerance and exactly-once processing.

```java
// Enable checkpointing
env.enableCheckpointing(60000);  // Every minute

// Configure checkpoint settings
env.getCheckpointConfig().setCheckpointingMode(CheckpointingMode.EXACTLY_ONCE);
env.getCheckpointConfig().setMinPauseBetweenCheckpoints(30000);  // 30 sec
env.getCheckpointConfig().setCheckpointTimeout(600000);  // 10 min
env.getCheckpointConfig().setMaxConcurrentCheckpoints(1);
env.getCheckpointConfig().enableExternalizedCheckpoints(
    ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION
);

// State backend (use RocksDB for large state)
env.setStateBackend(new EmbeddedRocksDBStateBackend());
env.getCheckpointConfig().setCheckpointStorage("s3://my-bucket/checkpoints");
```

### State Size Estimation

```
State per user:
- Session accumulator: ~1 KB
- Active users: 1M concurrent
- Total state: 1 GB

With RocksDB: State stored on disk, minimal memory overhead
```

---

## 6. Testing

### Unit Test

```java
// flink-jobs/src/test/java/com/dateng/SessionizationJobTest.java
package com.dateng;

import com.dateng.functions.SessionAggregateFunction;
import com.dateng.schema.ClickstreamEvent;
import com.dateng.schema.Session;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.windowing.assigners.EventTimeSessionWindows;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.test.util.AbstractTestBase;
import org.junit.Test;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

import static org.junit.Assert.*;

public class SessionizationJobTest extends AbstractTestBase {
    
    @Test
    public void testSessionAggregation() {
        // Create test events
        List<ClickstreamEvent> events = new ArrayList<>();
        
        Instant now = Instant.now();
        String userId = "user-123";
        String sessionId = "session-456";
        
        // Event 1: Page view
        ClickstreamEvent event1 = new ClickstreamEvent(userId, sessionId, "page_view", "/home");
        event1.setTimestamp(now);
        events.add(event1);
        
        // Event 2: Click (10 sec later)
        ClickstreamEvent event2 = new ClickstreamEvent(userId, sessionId, "click", "/products");
        event2.setTimestamp(now.plusSeconds(10));
        events.add(event2);
        
        // Event 3: Purchase (20 sec later)
        ClickstreamEvent event3 = new ClickstreamEvent(userId, sessionId, "purchase", "/checkout");
        event3.setTimestamp(now.plusSeconds(20));
        events.add(event3);
        
        // Aggregate events
        SessionAggregateFunction.SessionAccumulator acc = new SessionAggregateFunction.SessionAccumulator();
        SessionAggregateFunction function = new SessionAggregateFunction();
        
        for (ClickstreamEvent event : events) {
            acc = function.add(event, acc);
        }
        
        Session session = function.getResult(acc);
        
        // Verify session
        assertEquals(userId, session.getUserId());
        assertEquals(sessionId, session.getSessionId());
        assertEquals(3, session.getEventCount());
        assertEquals(1, session.getPageViewCount());
        assertEquals(1, session.getClickCount());
        assertEquals(1, session.getPurchaseCount());
        assertTrue(session.isConversion());
        assertEquals(20, session.getDurationSeconds());
    }
}
```

---

## Performance Characteristics

**Throughput:**
- 1M events/sec input
- 30 parallelism = 33K events/sec per task
- Session aggregation: O(1) per event

**Latency:**
- Event processing: < 100ms
- Window emission: Session gap + watermark delay = 30 + 5 = 35 min max
- For real-time: Use tumbling windows (1 min) in parallel

**State Size:**
- 1M concurrent users
- 1 KB per user
- Total: 1 GB (fits in RocksDB easily)

---

## Next Steps

Proceed to Part 3 for aggregations job:
- [03-flink-aggregations.md](./03-flink-aggregations.md)

---

**End of Part 2**
