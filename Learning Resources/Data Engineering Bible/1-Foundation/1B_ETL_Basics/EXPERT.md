# Week 2: ETL Pipelines & Data Modeling
## 🏗️ EXPERT - Enterprise Data Warehouse Architecture

---

## 🎯 **Learning Objectives**

This section covers Principal/Staff-level understanding:
- Design enterprise data warehouses at scale
- Real-world architectures (Netflix, Airbnb, Uber)
- Advanced dimensional modeling patterns
- Data vault and anchor modeling
- 10 FAANG-level system design questions

---

## 🧩 **1. Principal Architect Depth: Dimensional Modeling**

### **The Kimball vs Inmon Debate**

**Two philosophies that shaped data warehousing:**

---

### **Ralph Kimball: Bottom-Up, Dimensional**

**Philosophy:** Build data marts first, integrate later

**Architecture:**
```
┌────────────────────────────────────────────┐
│         DATA SOURCES                       │
│  OLTP | SaaS | Files | APIs               │
└────────────────────────────────────────────┘
                 ↓
┌────────────────────────────────────────────┐
│         ETL LAYER                          │
└────────────────────────────────────────────┘
                 ↓
┌─────────────┬──────────────┬──────────────┐
│ Sales Mart  │ Finance Mart │ Marketing    │
│ (Star)      │ (Star)       │ Mart (Star)  │
│             │              │              │
│ ┌─────────┐ │ ┌──────────┐│ ┌──────────┐│
│ │ Facts   │ │ │ Facts    ││ │ Facts    ││
│ └─────────┘ │ └──────────┘│ └──────────┘│
│ ┌─────────┐ │ ┌──────────┐│ ┌──────────┐│
│ │ Dims    │ │ │ Dims     ││ │ Dims     ││
│ └─────────┘ │ └──────────┘│ └──────────┘│
└─────────────┴──────────────┴──────────────┘
```

**Key Principles:**

1. **Dimensional Modeling (Star/Snowflake)**
   - Facts: Measurements
   - Dimensions: Context
   - Denormalized for query performance

2. **Conformed Dimensions**
   - Shared across data marts
   - Example: Customer dimension used by Sales, Marketing, Support

3. **Business Process Orientation**
   - Each data mart represents a business process
   - Example: Order fulfillment, customer support, marketing campaigns

**Advantages:**
- ✅ Fast to implement (build one mart at a time)
- ✅ Business-focused (aligned with departments)
- ✅ High query performance (optimized for BI)
- ✅ Easy for analysts to understand

**Disadvantages:**
- ❌ Data duplication across marts
- ❌ Risk of inconsistent metrics
- ❌ Difficult to add new data sources later

**Best For:** BI and reporting use cases, analytics teams

---

### **Bill Inmon: Top-Down, Normalized**

**Philosophy:** Build enterprise data warehouse first, derive data marts

**Architecture:**
```
┌────────────────────────────────────────────┐
│         DATA SOURCES                       │
│  OLTP | SaaS | Files | APIs               │
└────────────────────────────────────────────┘
                 ↓
┌────────────────────────────────────────────┐
│         ETL LAYER                          │
└────────────────────────────────────────────┘
                 ↓
┌────────────────────────────────────────────┐
│   ENTERPRISE DATA WAREHOUSE (EDW)          │
│   (3NF - Normalized, Subject-Oriented)     │
│                                            │
│   ┌───────────┐  ┌───────────┐           │
│   │ Customers │  │ Products  │           │
│   └───────────┘  └───────────┘           │
│   ┌───────────┐  ┌───────────┐           │
│   │ Orders    │  │ Inventory │           │
│   └───────────┘  └───────────┘           │
└────────────────────────────────────────────┘
                 ↓
┌─────────────┬──────────────┬──────────────┐
│ Sales Mart  │ Finance Mart │ Marketing    │
│ (Derived)   │ (Derived)    │ Mart         │
└─────────────┴──────────────┴──────────────┘
```

**Key Principles:**

1. **Normalization (3NF)**
   - Eliminate redundancy
   - Enforce referential integrity
   - Single source of truth

2. **Subject-Oriented**
   - Organized by entity (Customer, Product, Order)
   - Not by department

3. **Integrated & Historical**
   - All data integrated into one model
   - Full history preserved

**Advantages:**
- ✅ Single source of truth
- ✅ Flexible (easy to add new marts)
- ✅ Data consistency
- ✅ Future-proof

**Disadvantages:**
- ❌ Slow to build (need complete model upfront)
- ❌ Complex for analysts (many joins)
- ❌ Lower query performance

**Best For:** Enterprise-scale, long-term strategic initiatives

---

### **Modern Hybrid Approach (Data Lakehouse)**

**What companies actually do in 2025:**

```
┌────────────────────────────────────────────┐
│         DATA SOURCES                       │
└────────────────────────────────────────────┘
                 ↓
┌────────────────────────────────────────────┐
│   DATA LAKE (Raw - Bronze Layer)           │
│   S3/GCS/ADLS - Parquet/Avro               │
│   - Schema-on-read                         │
│   - All historical data                    │
└────────────────────────────────────────────┘
                 ↓
┌────────────────────────────────────────────┐
│   CLEANED LAYER (Silver)                   │
│   - Deduplicated                           │
│   - Standardized schemas                   │
│   - Quality checked                        │
└────────────────────────────────────────────┘
                 ↓
┌────────────────────────────────────────────┐
│   CURATED LAYER (Gold)                     │
│   - Star schema data marts                 │
│   - Aggregated tables                      │
│   - Business logic applied                 │
└────────────────────────────────────────────┘
                 ↓
┌─────────────┬──────────────┬──────────────┐
│  BI Tools   │  ML Models   │  Data Apps   │
└─────────────┴──────────────┴──────────────┘
```

**Combines best of both:**
- Kimball: Star schemas for analytics
- Inmon: Normalized layer for integration
- Plus: Raw layer for flexibility

---

## 🌍 **2. Real-World Implementations**

### **Netflix: Viewing Data Warehouse**

**Scale:**
- 200+ million subscribers
- Billions of viewing events per day
- 100+ PB of data

**Architecture:**

```
┌────────────────────────────────────────────┐
│   EVENT SOURCES                            │
│  - Client devices (apps, web, smart TV)    │
│  - Streaming servers                       │
│  - CDN logs                                │
└────────────────────────────────────────────┘
                 ↓ (Kafka)
┌────────────────────────────────────────────┐
│   RAW EVENT STREAM                         │
│  - 500,000 events/second                   │
│  - JSON format                             │
│  - Partitioned by user_id                  │
└────────────────────────────────────────────┘
                 ↓ (Spark Streaming)
┌────────────────────────────────────────────┐
│   DATA LAKE (S3)                           │
│  - Parquet format                          │
│  - Partitioned: /year/month/day/hour       │
│  - Compressed with Snappy                  │
└────────────────────────────────────────────┘
                 ↓ (Spark batch jobs)
┌────────────────────────────────────────────┐
│   HIVE METASTORE                           │
│  - Table schemas                           │
│  - Partition metadata                      │
└────────────────────────────────────────────┘
                 ↓
┌────────────────────────────────────────────┐
│   DATA WAREHOUSE (Redshift/Snowflake)      │
│                                            │
│   FACT: viewing_events                     │
│   ┌──────────────────────────────────┐    │
│   │ event_id                         │    │
│   │ user_id → dim_users              │    │
│   │ content_id → dim_content         │    │
│   │ device_id → dim_devices          │    │
│   │ timestamp                        │    │
│   │ play_duration_sec                │    │
│   │ buffer_events                    │    │
│   │ quality (720p/1080p/4K)          │    │
│   └──────────────────────────────────┘    │
│                                            │
│   DIM: dim_content                         │
│   ┌──────────────────────────────────┐    │
│   │ content_id                       │    │
│   │ title                            │    │
│   │ genre                            │    │
│   │ release_date                     │    │
│   │ duration_minutes                 │    │
│   │ rating (G/PG/R)                  │    │
│   └──────────────────────────────────┘    │
└────────────────────────────────────────────┘
```

**Key Design Decisions:**

**1. Partitioning Strategy**
```python
# Partition by date for time-series queries
/s3/viewing_events/year=2025/month=10/day=09/hour=14/

# Benefits:
- Query only relevant partitions
- Lifecycle management (delete old data)
- Parallel processing

# Trade-off:
- Not good for user_id queries
- Solution: Secondary index or denormalize
```

**2. Pre-Aggregation**
```sql
-- Don't query raw events every time (billions of rows!)
-- Pre-aggregate to hourly/daily tables

CREATE TABLE viewing_summary_daily AS
SELECT
    DATE(timestamp) as view_date,
    content_id,
    COUNT(DISTINCT user_id) as unique_viewers,
    SUM(play_duration_sec) as total_watch_time_sec,
    AVG(buffer_events) as avg_buffer_events
FROM viewing_events
GROUP BY DATE(timestamp), content_id;

-- Now queries are 1000x faster!
```

**3. Data Retention**
```python
# Raw events: 90 days (detailed debugging)
# Aggregated data: 7 years (trend analysis)
# Anonymized data: Forever (ML training)

# Saves costs: 1PB → 10TB
```

**4. Slowly Changing Dimensions**
```sql
-- Content metadata changes (new genre, rating update)
-- Use SCD Type 2 to track history

-- Example: Show was "TV-14", now "TV-MA"
INSERT INTO dim_content (
    content_id,
    title,
    rating,
    effective_date,
    end_date,
    is_current
) VALUES (
    12345,
    'Stranger Things',
    'TV-MA',  -- New rating
    '2025-10-01',
    '9999-12-31',
    TRUE
);

UPDATE dim_content
SET end_date = '2025-09-30',
    is_current = FALSE
WHERE content_id = 12345 AND is_current = TRUE;
```

---

### **Airbnb: Listing & Booking Warehouse**

**Scale:**
- 7 million listings
- 100+ million users
- Billions of search/booking events

**Star Schema Design:**

```sql
-- FACT: bookings
CREATE TABLE fact_bookings (
    booking_id BIGINT PRIMARY KEY,
    
    -- Foreign keys (dimensions)
    listing_id BIGINT REFERENCES dim_listings,
    guest_id BIGINT REFERENCES dim_users,
    host_id BIGINT REFERENCES dim_users,
    check_in_date_id INT REFERENCES dim_date,
    check_out_date_id INT REFERENCES dim_date,
    booking_date_id INT REFERENCES dim_date,
    
    -- Degenerate dimensions (attributes without separate table)
    booking_channel VARCHAR(50),  -- web, mobile_app, api
    payment_method VARCHAR(50),
    
    -- Measures (facts)
    nights INT,
    guests INT,
    total_price_usd DECIMAL(10,2),
    cleaning_fee_usd DECIMAL(10,2),
    service_fee_usd DECIMAL(10,2),
    host_payout_usd DECIMAL(10,2),
    
    -- Flags
    is_instant_book BOOLEAN,
    is_first_booking BOOLEAN,
    is_canceled BOOLEAN,
    
    -- Audit
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- DIMENSION: listings
CREATE TABLE dim_listings (
    listing_id BIGINT PRIMARY KEY,
    
    -- Attributes
    title VARCHAR(500),
    description TEXT,
    property_type VARCHAR(100),  -- apartment, house, room
    room_type VARCHAR(50),  -- entire_place, private_room, shared_room
    
    -- Location hierarchy
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    
    -- Amenities (normalized elsewhere, but denormalized here for speed)
    has_wifi BOOLEAN,
    has_kitchen BOOLEAN,
    has_parking BOOLEAN,
    has_pool BOOLEAN,
    
    -- Pricing
    nightly_rate_usd DECIMAL(10,2),
    cleaning_fee_usd DECIMAL(10,2),
    
    -- Capacity
    max_guests INT,
    bedrooms INT,
    beds INT,
    bathrooms DECIMAL(3,1),
    
    -- SCD Type 2 fields
    effective_date DATE,
    end_date DATE,
    is_current BOOLEAN
);

-- DIMENSION: users (guests and hosts)
CREATE TABLE dim_users (
    user_id BIGINT PRIMARY KEY,
    
    -- Profile
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(200),
    phone VARCHAR(50),
    
    -- Demographics
    age_range VARCHAR(20),  -- 18-24, 25-34, etc.
    gender VARCHAR(20),
    
    -- Location
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    
    -- Host-specific (NULL for non-hosts)
    is_superhost BOOLEAN,
    host_since DATE,
    host_response_time VARCHAR(50),
    host_response_rate DECIMAL(5,2),
    
    -- Verification
    is_verified BOOLEAN,
    verified_methods VARCHAR(500),  -- email, phone, govt_id
    
    -- SCD Type 2
    effective_date DATE,
    end_date DATE,
    is_current BOOLEAN
);
```

**Advanced Query Patterns:**

```sql
-- Question: "Which cities have highest booking growth month-over-month?"

WITH monthly_bookings AS (
    SELECT
        l.city,
        d.year,
        d.month,
        COUNT(*) as bookings,
        SUM(f.total_price_usd) as revenue
    FROM fact_bookings f
    JOIN dim_listings l ON f.listing_id = l.listing_id AND l.is_current = TRUE
    JOIN dim_date d ON f.check_in_date_id = d.date_id
    WHERE d.year >= 2024
    GROUP BY l.city, d.year, d.month
),
growth AS (
    SELECT
        city,
        year,
        month,
        bookings,
        LAG(bookings) OVER (PARTITION BY city ORDER BY year, month) as prev_month_bookings,
        (bookings - LAG(bookings) OVER (PARTITION BY city ORDER BY year, month)) * 100.0 / 
            NULLIF(LAG(bookings) OVER (PARTITION BY city ORDER BY year, month), 0) as growth_pct
    FROM monthly_bookings
)
SELECT
    city,
    year,
    month,
    bookings,
    prev_month_bookings,
    growth_pct
FROM growth
WHERE growth_pct IS NOT NULL
ORDER BY growth_pct DESC
LIMIT 10;
```

**Performance Optimization:**

```sql
-- Materialized aggregate tables (refresh daily)
CREATE TABLE agg_city_metrics_daily AS
SELECT
    l.city,
    d.date,
    COUNT(DISTINCT f.listing_id) as active_listings,
    COUNT(*) as bookings,
    AVG(f.nights) as avg_nights,
    SUM(f.total_price_usd) as revenue,
    COUNT(DISTINCT f.guest_id) as unique_guests
FROM fact_bookings f
JOIN dim_listings l ON f.listing_id = l.listing_id
JOIN dim_date d ON f.check_in_date_id = d.date_id
GROUP BY l.city, d.date;

-- Indexes for common access patterns
CREATE INDEX idx_bookings_check_in_date ON fact_bookings(check_in_date_id);
CREATE INDEX idx_bookings_listing ON fact_bookings(listing_id);
CREATE INDEX idx_listings_city ON dim_listings(city) WHERE is_current = TRUE;
```

---

### **Uber: Trips Data Warehouse**

**Scale:**
- 100+ million trips per day
- Real-time surge pricing
- Geospatial analytics

**Unique Challenge: Geospatial + Temporal**

```sql
-- FACT: trips (partitioned by city for geo-sharding)
CREATE TABLE fact_trips (
    trip_id BIGINT PRIMARY KEY,
    
    -- Dimensions
    driver_id BIGINT,
    rider_id BIGINT,
    city_id INT,
    pickup_date_id INT,
    dropoff_date_id INT,
    
    -- Geospatial (denormalized for performance)
    pickup_lat DECIMAL(9,6),
    pickup_lon DECIMAL(9,6),
    pickup_geohash VARCHAR(12),  -- For spatial queries
    dropoff_lat DECIMAL(9,6),
    dropoff_lon DECIMAL(9,6),
    dropoff_geohash VARCHAR(12),
    
    -- Temporal
    pickup_timestamp TIMESTAMP,
    dropoff_timestamp TIMESTAMP,
    
    -- Measures
    distance_km DECIMAL(10,2),
    duration_minutes INT,
    base_fare_usd DECIMAL(10,2),
    surge_multiplier DECIMAL(3,2),  -- 1.0 = no surge, 2.5 = 2.5x
    total_fare_usd DECIMAL(10,2),
    tip_usd DECIMAL(10,2),
    driver_payout_usd DECIMAL(10,2),
    
    -- Categorical
    trip_type VARCHAR(50),  -- uberX, uberXL, uberBLACK
    payment_method VARCHAR(50),
    
    -- Flags
    is_canceled BOOLEAN,
    is_shared BOOLEAN,
    is_scheduled BOOLEAN
    
) PARTITION BY LIST (city_id);  -- Geo-sharding

-- Partition examples
CREATE TABLE fact_trips_sf PARTITION OF fact_trips FOR VALUES IN (1);  -- San Francisco
CREATE TABLE fact_trips_nyc PARTITION OF fact_trips FOR VALUES IN (2);  -- New York
CREATE TABLE fact_trips_london PARTITION OF fact_trips FOR VALUES IN (3);  -- London
```

**Geospatial Indexing:**

```sql
-- Use PostGIS for geospatial queries
CREATE EXTENSION postgis;

-- Add geometry columns
ALTER TABLE fact_trips
ADD COLUMN pickup_point GEOMETRY(POINT, 4326),
ADD COLUMN dropoff_point GEOMETRY(POINT, 4326);

-- Create spatial index
CREATE INDEX idx_trips_pickup_point ON fact_trips USING GIST(pickup_point);

-- Query: "Find all trips within 1km of downtown SF"
SELECT
    trip_id,
    distance_km,
    total_fare_usd
FROM fact_trips
WHERE city_id = 1  -- San Francisco
  AND ST_DWithin(
      pickup_point,
      ST_SetSRID(ST_MakePoint(-122.4194, 37.7749), 4326),  -- Downtown SF
      1000  -- 1000 meters = 1km
  );
```

**Time-Series Optimization:**

```sql
-- Pre-aggregate to 5-minute windows for surge pricing
CREATE TABLE agg_surge_metrics_5min AS
SELECT
    city_id,
    DATE_TRUNC('minute', pickup_timestamp) - 
        (EXTRACT(MINUTE FROM pickup_timestamp)::INT % 5) * INTERVAL '1 minute' as time_window,
    pickup_geohash,  -- Spatial bucket
    COUNT(*) as trip_count,
    AVG(surge_multiplier) as avg_surge,
    COUNT(DISTINCT driver_id) as active_drivers,
    COUNT(DISTINCT rider_id) as active_riders
FROM fact_trips
GROUP BY city_id, time_window, pickup_geohash;
```

---

## 🔬 **3. Advanced Modeling Patterns**

### **Pattern 1: Data Vault Modeling**

**When Kimball/Inmon aren't enough:**

**Problem:** 
- Sources change frequently
- Need full auditability
- Want to track every change

**Data Vault Components:**

```sql
-- HUB: Business keys (entities)
CREATE TABLE hub_customer (
    customer_key BIGSERIAL PRIMARY KEY,  -- Surrogate key
    customer_id VARCHAR(50) UNIQUE,  -- Business key
    load_date TIMESTAMP,
    source_system VARCHAR(100)
);

-- SATELLITE: Descriptive attributes (track changes)
CREATE TABLE sat_customer_profile (
    customer_key BIGINT REFERENCES hub_customer,
    load_date TIMESTAMP,
    name VARCHAR(200),
    email VARCHAR(200),
    phone VARCHAR(50),
    city VARCHAR(100),
    
    -- Audit
    hash_diff VARCHAR(64),  -- Detect changes
    source_system VARCHAR(100),
    
    PRIMARY KEY (customer_key, load_date)
);

-- LINK: Relationships
CREATE TABLE link_customer_order (
    link_key BIGSERIAL PRIMARY KEY,
    customer_key BIGINT REFERENCES hub_customer,
    order_key BIGINT REFERENCES hub_order,
    load_date TIMESTAMP,
    source_system VARCHAR(100)
);
```

**Benefits:**
- ✅ Audit trail of every change
- ✅ Easy to integrate new sources
- ✅ Parallel loading (no foreign keys!)

**Downsides:**
- ❌ Complex queries (many joins)
- ❌ Slower than star schema
- ❌ Not analyst-friendly

**Use Case:** Highly regulated industries (finance, healthcare)

---

### **Pattern 2: Activity Schema**

**Alternative to fact tables for event data:**

```sql
-- Traditional: Multiple fact tables
fact_page_views
fact_clicks
fact_purchases
fact_sign_ups

-- Activity Schema: One universal table
CREATE TABLE activity_stream (
    activity_id BIGINT PRIMARY KEY,
    user_id BIGINT,
    timestamp TIMESTAMP,
    activity_type VARCHAR(50),  -- page_view, click, purchase, sign_up
    
    -- Flexible attributes (JSONB)
    properties JSONB,
    
    -- Common dimensions
    device_type VARCHAR(50),
    platform VARCHAR(50),
    country VARCHAR(50)
);

-- Example queries
-- Page views
SELECT * FROM activity_stream
WHERE activity_type = 'page_view'
  AND properties->>'page_url' LIKE '%product%';

-- Purchases
SELECT
    properties->>'product_id',
    SUM((properties->>'amount')::DECIMAL) as total_revenue
FROM activity_stream
WHERE activity_type = 'purchase'
GROUP BY properties->>'product_id';
```

**Benefits:**
- ✅ Schema-on-read flexibility
- ✅ Easy to add new event types
- ✅ Good for product analytics

**Downsides:**
- ❌ Slower queries (JSON parsing)
- ❌ No type safety
- ❌ Difficult to optimize

---

### **Pattern 3: Conformed Dimensions**

**Challenge:** Same entity appears in multiple data marts

**Bad Approach:**
```
Sales Mart:
  dim_customer (customer_id, name, city)

Marketing Mart:
  dim_customer (customer_id, name, email, segment)

Support Mart:
  dim_customer (customer_id, name, phone)

❌ Three different definitions!
❌ Inconsistent metrics across departments
```

**Conformed Dimension (Good Approach):**
```sql
-- Single shared dimension
CREATE TABLE dim_customer_master (
    customer_key BIGSERIAL PRIMARY KEY,  -- Surrogate key
    customer_id VARCHAR(50) UNIQUE,  -- Business key
    
    -- All attributes from all marts
    name VARCHAR(200),
    email VARCHAR(200),
    phone VARCHAR(50),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    segment VARCHAR(50),
    lifetime_value_usd DECIMAL(10,2),
    
    -- SCD Type 2
    effective_date DATE,
    end_date DATE,
    is_current BOOLEAN
);

-- All marts reference same dimension
fact_sales → dim_customer_master
fact_marketing_campaigns → dim_customer_master
fact_support_tickets → dim_customer_master

✅ Single source of truth
✅ Consistent metrics
```

---

## 💡 **4. FAANG-Level Interview Questions**

### **Question 1: Design a data warehouse for a food delivery platform (like DoorDash)**

**Answer:**

**Requirements:**
- Track orders, restaurants, drivers, customers
- Real-time dashboards (order status, driver location)
- Historical analytics (trends, forecasts)

**Proposed Architecture:**

```
┌─────────────────────────────────────────────┐
│  OPERATIONAL DATABASES (OLTP)               │
│  - Orders (PostgreSQL)                      │
│  - Users (PostgreSQL)                       │
│  - Restaurants (MongoDB)                    │
│  - Driver locations (Redis + Kafka)         │
└─────────────────────────────────────────────┘
           ↓                      ↓
    (Batch ETL)            (Stream CDC)
           ↓                      ↓
┌──────────────────┐    ┌────────────────────┐
│  DATA LAKE (S3)  │    │ KAFKA STREAMS      │
│  - Daily dumps   │    │ - Real-time events │
│  - Parquet       │    │ - Order updates    │
└──────────────────┘    │ - Driver positions │
           ↓             └────────────────────┘
           ↓                      ↓
┌─────────────────────────────────────────────┐
│   DATA WAREHOUSE (Snowflake)                │
│                                             │
│   FACT: orders                              │
│   ┌───────────────────────────────────┐    │
│   │ order_id                          │    │
│   │ customer_id → dim_customers       │    │
│   │ restaurant_id → dim_restaurants   │    │
│   │ driver_id → dim_drivers           │    │
│   │ order_time_id → dim_date_time     │    │
│   │ delivery_time_id                  │    │
│   │ subtotal_usd                      │    │
│   │ delivery_fee_usd                  │    │
│   │ tip_usd                           │    │
│   │ total_usd                         │    │
│   │ delivery_distance_km              │    │
│   │ prep_time_minutes                 │    │
│   │ delivery_time_minutes             │    │
│   │ status (placed/accepted/picked/   │    │
│   │         delivered/canceled)       │    │
│   └───────────────────────────────────┘    │
│                                             │
│   DIM: restaurants                          │
│   ┌───────────────────────────────────┐    │
│   │ restaurant_id                     │    │
│   │ name, cuisine_type                │    │
│   │ rating, review_count              │    │
│   │ address, lat, lon                 │    │
│   │ is_partner, commission_rate       │    │
│   └───────────────────────────────────┘    │
└─────────────────────────────────────────────┘
           ↓                      ↓
┌──────────────────┐    ┌────────────────────┐
│  BI DASHBOARDS   │    │ ML MODELS          │
│  - Tableau       │    │ - ETA prediction   │
│  - Looker        │    │ - Demand forecast  │
└──────────────────┘    └────────────────────┘
```

**Key Design Decisions:**

**1. Hybrid Batch + Stream:**
```python
# Batch (daily): Historical analysis
# - Full table dumps overnight
# - Used for BI reports, trend analysis

# Stream (real-time): Operational dashboards
# - Kafka CDC from OLTP databases
# - Used for live driver maps, order tracking
```

**2. Fact Table Granularity:**
```sql
-- One row per order (not per order item!)
-- Why? Most analytics are order-level

-- For item-level analysis, use separate fact:
CREATE TABLE fact_order_items (
    order_item_id BIGINT PRIMARY KEY,
    order_id BIGINT REFERENCES fact_orders,
    menu_item_id BIGINT,
    quantity INT,
    price_usd DECIMAL(10,2),
    customizations JSONB  -- "no onions", "extra cheese"
);
```

**3. Geospatial Considerations:**
```sql
-- Add geohash for efficient spatial queries
ALTER TABLE fact_orders
ADD COLUMN delivery_geohash VARCHAR(12);

-- Query: "How many orders in this neighborhood?"
SELECT COUNT(*)
FROM fact_orders
WHERE delivery_geohash LIKE 'xyz123%'  -- Prefix match
  AND status = 'delivered';
```

**4. Time Dimensions:**
```sql
-- Two time dimensions for complex queries
dim_date_time (order_time_id)
dim_date_time (delivery_time_id)

-- Query: "Average delivery time by hour of day"
SELECT
    order_time.hour,
    AVG(delivery_time.timestamp - order_time.timestamp) as avg_delivery_time
FROM fact_orders f
JOIN dim_date_time order_time ON f.order_time_id = order_time.id
JOIN dim_date_time delivery_time ON f.delivery_time_id = delivery_time.id
GROUP BY order_time.hour;
```

---

### **Question 2: How would you handle a dimension with 1 billion rows?**

**Scenario:** User dimension for a social media platform (like Facebook)

**Problem:** 
- dim_users has 1 billion rows
- Joins are slow
- Updates are expensive (SCD Type 2)

**Solutions:**

**Solution 1: Mini-Dimensions**
```sql
-- Split rarely-changing from frequently-changing attributes

-- Core dimension (rarely changes)
CREATE TABLE dim_users_core (
    user_id BIGINT PRIMARY KEY,
    name VARCHAR(200),
    email VARCHAR(200),
    signup_date DATE,
    country VARCHAR(100)
    -- 1 billion rows, but stable
);

-- Mini-dimension (changes frequently)
CREATE TABLE dim_user_demographics (
    demographic_key SERIAL PRIMARY KEY,
    age_range VARCHAR(20),
    gender VARCHAR(20),
    education VARCHAR(50),
    -- Only ~1000 unique combinations!
);

-- Fact table references both
CREATE TABLE fact_posts (
    post_id BIGINT PRIMARY KEY,
    user_id BIGINT REFERENCES dim_users_core,
    demographic_key INT REFERENCES dim_user_demographics,
    post_date DATE,
    likes INT,
    shares INT
);
```

**Benefits:**
- Small demographic dimension (fast joins)
- Core dimension rarely changes (no SCD overhead)
- Fact table smaller (demographic_key vs all attributes)

---

**Solution 2: Sharding/Partitioning**
```sql
-- Partition by geography
CREATE TABLE dim_users (
    user_id BIGINT,
    ...
) PARTITION BY LIST (country);

CREATE TABLE dim_users_us PARTITION OF dim_users FOR VALUES IN ('US');
CREATE TABLE dim_users_india PARTITION OF dim_users FOR VALUES IN ('India');
-- etc.

-- Queries only scan relevant partition
SELECT * FROM dim_users WHERE country = 'US';  -- Only scans dim_users_us
```

---

**Solution 3: Denormalization (Trade Storage for Speed)**
```sql
-- Copy user attributes directly into fact table
CREATE TABLE fact_posts (
    post_id BIGINT PRIMARY KEY,
    
    -- User dimension denormalized
    user_id BIGINT,
    user_name VARCHAR(200),
    user_country VARCHAR(100),
    user_age_range VARCHAR(20),
    
    -- Post attributes
    post_date DATE,
    likes INT,
    shares INT
);

-- No join needed!
SELECT user_country, SUM(likes)
FROM fact_posts
GROUP BY user_country;
```

**Trade-off:**
- ✅ Fast queries (no joins)
- ❌ More storage
- ❌ Stale data if user updates

---

### **Question 3: Design an ETL pipeline for GDPR compliance**

**Requirements:**
- Users can request data deletion (Right to be Forgotten)
- Must delete from all systems within 30 days
- Must maintain analytics integrity

**Challenge:** 
- Can't just delete fact table rows (breaks metrics!)
- Need to anonymize, not delete

**Solution:**

```sql
-- 1. Soft delete in dimension
UPDATE dim_users
SET email = 'deleted@example.com',
    name = 'User Deleted',
    phone = NULL,
    address = NULL,
    is_deleted = TRUE,
    deletion_date = CURRENT_DATE
WHERE user_id = 12345;

-- 2. Fact tables: Keep aggregates, remove details
UPDATE fact_orders
SET customer_id = -1  -- Special "Anonymous" ID
WHERE customer_id = 12345;

-- 3. Remove from raw data lake
-- Mark for deletion (Iceberg/Delta support row-level deletes)
DELETE FROM bronze_layer.user_events
WHERE user_id = 12345;

-- 4. Update ML training data
-- Replace with synthetic user
INSERT INTO ml_training_users (
    user_id, age_range, country, ...
) VALUES (
    -1,  -- Synthetic
    'ANONYMIZED',
    'ANONYMIZED',
    ...
);
```

**Audit Trail:**
```sql
CREATE TABLE gdpr_deletion_log (
    request_id SERIAL PRIMARY KEY,
    user_id BIGINT,
    request_date DATE,
    completed_date DATE,
    tables_affected TEXT[],
    rows_deleted INT,
    rows_anonymized INT
);
```

---

### **Question 4: Optimize a slow-running ETL pipeline**

**Scenario:** 
- Nightly ETL takes 8 hours (SLA: 4 hours)
- Processes 100GB of data
- Simple transformations (joins, aggregations)

**Diagnosis & Solutions:**

**1. Profiling:**
```python
import time

def profile_etl():
    start = time.time()
    
    # Extract
    extract_start = time.time()
    data = extract_from_source()
    print(f"Extract: {time.time() - extract_start:.2f}s")
    
    # Transform
    transform_start = time.time()
    clean_data = transform(data)
    print(f"Transform: {time.time() - transform_start:.2f}s")
    
    # Load
    load_start = time.time()
    load_to_warehouse(clean_data)
    print(f"Load: {time.time() - load_start:.2f}s")
    
    print(f"Total: {time.time() - start:.2f}s")

# Output:
# Extract: 120s
# Transform: 25200s (7 hours!!) ← BOTTLENECK
# Load: 480s
```

**2. Optimize Transform (Bottleneck):**

**Problem: Row-by-row processing**
```python
# SLOW (iterates 100M rows)
for row in data:
    row['total'] = row['price'] * row['quantity']
```

**Solution: Vectorized operations**
```python
# FAST (pandas/numpy)
data['total'] = data['price'] * data['quantity']
```

**Problem: Large joins in memory**
```python
# SLOW (joins 100M × 50M rows in RAM)
result = orders.merge(customers, on='customer_id')
```

**Solution: Database join**
```sql
-- Let database handle join (optimized!)
SELECT o.*, c.name, c.email
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
```

**Problem: Sequential processing**
```python
# SLOW (one day at a time)
for date in date_range:
    process_date(date)
```

**Solution: Parallel processing**
```python
from multiprocessing import Pool

# FAST (process 8 days in parallel)
with Pool(8) as pool:
    pool.map(process_date, date_range)
```

**3. Incremental Loading:**
```python
# Instead of full refresh
last_run = get_last_run_timestamp()
new_data = extract_since(last_run)

# Only process new data (10GB vs 100GB)
```

**Result:** 8 hours → 90 minutes ✅

---

### **Question 5: Compare star schema vs OBT (One Big Table)**

**Answer:**

**Star Schema:**
```sql
fact_sales (100M rows)
  → dim_customer (1M rows)
  → dim_product (100K rows)
  → dim_date (10K rows)

-- Query requires 3 joins
SELECT
    c.country,
    p.category,
    SUM(f.amount) as revenue
FROM fact_sales f
JOIN dim_customer c ON f.customer_id = c.customer_id
JOIN dim_product p ON f.product_id = p.product_id
JOIN dim_date d ON f.date_id = d.date_id
WHERE d.year = 2025
GROUP BY c.country, p.category;
```

**One Big Table (Denormalized):**
```sql
sales_obt (100M rows with all attributes)

-- Query is simple
SELECT
    country,
    category,
    SUM(amount) as revenue
FROM sales_obt
WHERE year = 2025
GROUP BY country, category;
```

**Comparison:**

| Aspect | Star Schema | OBT |
|--------|-------------|-----|
| **Query Speed** | Slower (joins) | Faster (no joins) |
| **Storage** | Less (normalized) | More (redundant) |
| **Updates** | Complex (SCD) | Simple (full refresh) |
| **Flexibility** | High (reusable dimensions) | Low (specific to use case) |
| **BI Tool Friendly** | Need semantic layer | Direct querying |

**Modern Approach: Hybrid**
```sql
-- Store both!

-- Star schema for flexibility
dim_* tables

-- Materialized OBT for performance
CREATE MATERIALIZED VIEW sales_obt AS
SELECT
    f.*,
    c.name, c.country, c.segment,
    p.name, p.category, p.brand,
    d.year, d.month, d.quarter
FROM fact_sales f
JOIN dim_customer c ON ...
JOIN dim_product p ON ...
JOIN dim_date d ON ...;

-- Refresh nightly
REFRESH MATERIALIZED VIEW sales_obt;
```

---

## 🎯 **Summary: Principal-Level Insights**

**Key Takeaways:**

1. **Kimball vs Inmon:** Most companies use hybrid (lakehouse approach)
2. **Real-world scale:** Partition, pre-aggregate, denormalize strategically
3. **Advanced patterns:** Data Vault for auditability, Activity Schema for events
4. **Conformed dimensions:** Essential for enterprise consistency
5. **Performance:** Profile first, optimize bottlenecks, consider trade-offs

**When designing data warehouses:**
- Start with business questions
- Design for query patterns
- Plan for scale from day 1
- Balance flexibility vs performance
- Always consider data governance

---

**Next:**
- 📄 [WHITEPAPERS](./WHITEPAPERS.md) - Kimball & Inmon methodologies deep dive

**Congratulations!** You now understand enterprise data warehousing at a Principal Engineer level. 🎉
