# Design Uber Real-Time Pricing System - Complete System Design

**Difficulty:** ⭐⭐⭐⭐⭐  
**Interview Frequency:** Very High (Uber, Lyft, DoorDash, 40 LPA+)  
**Time to Complete:** 45-60 minutes  
**Real-World Examples:** Uber Surge Pricing, Lyft Prime Time, DoorDash Peak Pay

---

## 📋 Problem Statement

**Design a real-time dynamic pricing system that can:**
- Calculate optimal prices based on supply-demand in real-time
- Process 1 million ride requests per minute globally
- Update prices every 1-5 minutes per geographic zone
- Handle geospatial data at scale (drivers, riders, zones)
- Consider multiple pricing factors (weather, events, time, traffic)
- Provide price estimates instantly (<100ms latency)
- Support A/B testing for pricing strategies
- Prevent price manipulation and ensure fairness
- Scale globally across 10,000+ cities

**Business Goals:**
- Maximize revenue while maintaining rider satisfaction
- Balance supply (drivers) and demand (riders)
- Incentivize drivers during high-demand periods
- Maintain competitive pricing
- Comply with regulatory requirements

---

## 🎯 Functional Requirements

### **Core Features**
1. **Price Calculation**
   - Base fare calculation (distance + time)
   - Dynamic surge multiplier (supply/demand ratio)
   - Time-based pricing (rush hour, late night)
   - Location-based pricing (airport, downtown)
   - Event-based surcharges (concerts, sports)
   - Weather impact pricing

2. **Real-Time Updates**
   - Continuous driver location tracking
   - Live demand forecasting
   - Zone-level supply-demand computation
   - Price multiplier updates every 1-5 minutes
   - Instant price quotes on user request

3. **Geospatial Processing**
   - City divided into hexagonal zones (H3 system)
   - Zone-level metrics aggregation
   - Driver-rider matching optimization
   - ETA calculations
   - Multi-city support

4. **Analytics & Insights**
   - Historical pricing data
   - Revenue optimization
   - Demand prediction
   - Driver earnings analysis
   - Market elasticity modeling

---

## 🏗️ High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                              │
├──────────────────────────────────────────────────────────────┤
│  Rider Apps │ Driver Apps │ Admin Dashboard │ Partner APIs   │
└────┬─────────────┬──────────────┬──────────────────┬─────────┘
     │             │              │                  │
     ▼             ▼              ▼                  ▼
┌──────────────────────────────────────────────────────────────┐
│                 API GATEWAY (Kong/Apigee)                     │
├──────────────────────────────────────────────────────────────┤
│  - Rate limiting                                              │
│  - Authentication (JWT)                                       │
│  - Request routing                                            │
│  - Load balancing (geo-based)                                │
└────┬─────────────┬──────────────┬──────────────────┬─────────┘
     │             │              │                  │
     ▼             ▼              ▼                  ▼
┌──────────────────────────────────────────────────────────────┐
│                   PRICING SERVICES                            │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  PRICE QUOTE SERVICE (Read Path - Hot)                │ │
│  │  - GET /v1/estimate?pickup=lat,lng&dropoff=lat,lng    │ │
│  │  - <100ms latency requirement                         │ │
│  │  - Read from cache (Redis)                            │ │
│  │  - Fallback to calculation service                    │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  SURGE MULTIPLIER SERVICE (Read Path)                 │ │
│  │  - Get current surge for zone                         │ │
│  │  - Cached zone-level multipliers                      │ │
│  │  - Updated every 1-5 minutes                          │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  SURGE CALCULATION SERVICE (Write Path - Background)  │ │
│  │  - Compute supply-demand per zone                     │ │
│  │  - Apply ML model for predictions                     │ │
│  │  - Calculate surge multipliers                        │ │
│  │  - Publish updates to cache                           │ │
│  └────────────────────────────────────────────────────────┘ │
└────┬─────────────┬──────────────┬──────────────────┬─────────┘
     │             │              │                  │
     ▼             ▼              ▼                  ▼
┌──────────────────────────────────────────────────────────────┐
│                  DATA STREAMING LAYER                         │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  KAFKA TOPICS                                        │   │
│  │  - driver-locations (100K msg/sec)                   │   │
│  │  - ride-requests (50K msg/sec)                       │   │
│  │  - ride-completions (30K msg/sec)                    │   │
│  │  - driver-status-changes                             │   │
│  │  - surge-multiplier-updates                          │   │
│  └──────────────────────────────────────────────────────┘   │
└────┬─────────────┬──────────────┬──────────────────┬─────────┘
     │             │              │                  │
     ▼             ▼              ▼                  ▼
┌──────────────────────────────────────────────────────────────┐
│             STREAM PROCESSING (Apache Flink)                  │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  GEOSPATIAL AGGREGATION PIPELINE                      │ │
│  │  ┌──────────┐   ┌──────────┐   ┌──────────┐          │ │
│  │  │H3 Zone   │ → │Aggregate │ → │Compute   │          │ │
│  │  │Mapping   │   │Metrics   │   │Ratios    │          │ │
│  │  └──────────┘   └──────────┘   └──────────┘          │ │
│  │  - Map lat/lng to H3 hexagon                          │ │
│  │  - Count drivers/riders per zone                      │ │
│  │  - Calculate supply/demand ratio                      │ │
│  │  - Windowed aggregations (1-min tumbling)             │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  SURGE COMPUTATION PIPELINE                           │ │
│  │  - Apply ML model for demand prediction               │ │
│  │  - Consider weather, events, time factors             │ │
│  │  - Calculate surge multiplier (1.0x - 5.0x)           │ │
│  │  - Smooth multiplier changes (prevent spikes)         │ │
│  │  - Publish to Redis cache                             │ │
│  └────────────────────────────────────────────────────────┘ │
└────┬─────────────┬──────────────┬──────────────────┬─────────┘
     │             │              │                  │
     ▼             ▼              ▼                  ▼
┌──────────────────────────────────────────────────────────────┐
│                    STORAGE LAYER                              │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  REDIS CLUSTER (Hot Cache)                            │ │
│  │  Key: zone_id → {surge_multiplier, updated_at}       │ │
│  │  TTL: 5 minutes                                        │ │
│  │  Replication: 3x for HA                               │ │
│  │  Partitioning: By zone_id (geo-sharding)              │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  PostgreSQL (Metadata)                                │ │
│  │  - Cities, zones, pricing rules                       │ │
│  │  - Driver profiles, vehicle types                     │ │
│  │  - Base pricing configuration                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Time-Series DB (InfluxDB/TimescaleDB)               │ │
│  │  - Historical surge multipliers                       │ │
│  │  - Supply-demand metrics over time                    │ │
│  │  - Revenue per zone per hour                          │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  S3 Data Lake                                         │ │
│  │  - Raw event logs                                      │ │
│  │  - ML training datasets                               │ │
│  │  - Audit trails                                       │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                 ML & ANALYTICS LAYER                          │
├──────────────────────────────────────────────────────────────┤
│  - Demand prediction models (LSTM, XGBoost)                  │
│  - Price elasticity modeling                                 │
│  - Driver incentive optimization                             │
│  - A/B testing framework                                     │
│  - Real-time anomaly detection                               │
└──────────────────────────────────────────────────────────────┘
```

---

## 💻 Core Implementation

### **1. Geospatial Zone Management with H3**

```python
import h3
from typing import Tuple, List, Set
from dataclasses import dataclass
from datetime import datetime

@dataclass
class GeoLocation:
    latitude: float
    longitude: float

@dataclass
class Zone:
    h3_index: str
    city_id: int
    resolution: int  # H3 resolution (0-15, 5-7 typical for ride-sharing)
    center: GeoLocation
    neighbors: Set[str]

class H3ZoneManager:
    """
    Manage geographic zones using Uber's H3 hierarchical geospatial indexing
    """
    
    def __init__(self, default_resolution: int = 7):
        # Resolution 7 = ~5.16 km² per hexagon (good for city-level pricing)
        # Resolution 8 = ~0.74 km² (dense urban areas)
        # Resolution 6 = ~36 km² (sparse suburban areas)
        self.default_resolution = default_resolution
        
        # Cache for zone lookups
        self.zone_cache = {}
    
    def get_zone_for_location(self, lat: float, lng: float, resolution: int = None) -> str:
        """
        Convert lat/lng to H3 zone index
        """
        res = resolution or self.default_resolution
        
        # Cache key
        cache_key = f"{lat:.6f},{lng:.6f},{res}"
        
        if cache_key in self.zone_cache:
            return self.zone_cache[cache_key]
        
        # Convert to H3 index
        h3_index = h3.geo_to_h3(lat, lng, res)
        
        self.zone_cache[cache_key] = h3_index
        return h3_index
    
    def get_neighboring_zones(self, h3_index: str, k_rings: int = 1) -> Set[str]:
        """
        Get neighboring zones within k rings
        k=1: immediate neighbors (6 hexagons)
        k=2: second ring (12 hexagons)
        """
        
        # Get k-ring neighbors
        neighbors = h3.k_ring(h3_index, k_rings)
        
        # Remove self
        neighbors.discard(h3_index)
        
        return neighbors
    
    def get_zone_boundary(self, h3_index: str) -> List[GeoLocation]:
        """
        Get boundary coordinates of zone (hexagon vertices)
        """
        
        boundary = h3.h3_to_geo_boundary(h3_index, geo_json=False)
        
        return [GeoLocation(lat, lng) for lat, lng in boundary]
    
    def get_zone_center(self, h3_index: str) -> GeoLocation:
        """
        Get center point of zone
        """
        
        lat, lng = h3.h3_to_geo(h3_index)
        return GeoLocation(lat, lng)
    
    def calculate_distance_km(self, loc1: GeoLocation, loc2: GeoLocation) -> float:
        """
        Calculate haversine distance between two locations
        """
        
        from math import radians, cos, sin, asin, sqrt
        
        lon1, lat1, lon2, lat2 = map(radians, [loc1.longitude, loc1.latitude, 
                                                loc2.longitude, loc2.latitude])
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        
        return c * r
    
    def adaptive_resolution(self, city_id: int, demand_density: str) -> int:
        """
        Choose H3 resolution based on city characteristics
        """
        
        # Dense urban: smaller zones for granular pricing
        # Sparse suburban: larger zones to ensure enough data
        
        density_resolution_map = {
            'very_dense': 8,   # ~0.74 km² (Manhattan, Tokyo)
            'dense': 7,        # ~5.16 km² (most cities)
            'medium': 6,       # ~36 km² (suburbs)
            'sparse': 5        # ~252 km² (rural)
        }
        
        return density_resolution_map.get(demand_density, self.default_resolution)


### **2. Real-Time Supply-Demand Calculation**

```python
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window
import redis
from typing import Dict
from dataclasses import dataclass

@dataclass
class ZoneMetrics:
    zone_id: str
    available_drivers: int
    busy_drivers: int
    pending_requests: int
    completed_rides_last_hour: int
    avg_wait_time_seconds: float
    supply_demand_ratio: float
    timestamp: datetime

class SupplyDemandCalculator:
    """
    Real-time supply-demand calculation using Spark Streaming
    """
    
    def __init__(self, kafka_brokers: str, redis_host: str):
        self.spark = SparkSession.builder \
            .appName("SurgePricing-SupplyDemand") \
            .config("spark.sql.shuffle.partitions", "200") \
            .getOrCreate()
        
        self.kafka_brokers = kafka_brokers
        self.redis_client = redis.Redis(host=redis_host, port=6379, decode_responses=True)
        self.h3_manager = H3ZoneManager()
    
    def process_driver_locations(self):
        """
        Process streaming driver location updates
        """
        
        # Read from Kafka
        driver_stream = self.spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", self.kafka_brokers) \
            .option("subscribe", "driver-locations") \
            .option("startingOffsets", "latest") \
            .option("maxOffsetsPerTrigger", 100000) \
            .load()
        
        # Parse JSON
        driver_schema = StructType([
            StructField("driver_id", StringType()),
            StructField("latitude", DoubleType()),
            StructField("longitude", DoubleType()),
            StructField("status", StringType()),  # 'available', 'busy', 'offline'
            StructField("timestamp", TimestampType())
        ])
        
        driver_data = driver_stream \
            .selectExpr("CAST(value AS STRING) as json") \
            .select(from_json(col("json"), driver_schema).alias("data")) \
            .select("data.*")
        
        # Map to H3 zones
        @udf(returnType=StringType())
        def get_h3_zone(lat: float, lng: float) -> str:
            return self.h3_manager.get_zone_for_location(lat, lng)
        
        driver_with_zones = driver_data \
            .withColumn("zone_id", get_h3_zone(col("latitude"), col("longitude")))
        
        # Aggregate by zone (1-minute tumbling window)
        zone_supply = driver_with_zones \
            .withWatermark("timestamp", "2 minutes") \
            .groupBy(
                window(col("timestamp"), "1 minute"),
                col("zone_id")
            ) \
            .agg(
                countDistinct(when(col("status") == "available", col("driver_id"))).alias("available_drivers"),
                countDistinct(when(col("status") == "busy", col("driver_id"))).alias("busy_drivers"),
                countDistinct(col("driver_id")).alias("total_drivers")
            ) \
            .select(
                col("zone_id"),
                col("available_drivers"),
                col("busy_drivers"),
                col("total_drivers"),
                col("window.end").alias("window_end")
            )
        
        return zone_supply
    
    def process_ride_requests(self):
        """
        Process streaming ride requests
        """
        
        request_stream = self.spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", self.kafka_brokers) \
            .option("subscribe", "ride-requests") \
            .option("startingOffsets", "latest") \
            .load()
        
        request_schema = StructType([
            StructField("request_id", StringType()),
            StructField("rider_id", StringType()),
            StructField("pickup_latitude", DoubleType()),
            StructField("pickup_longitude", DoubleType()),
            StructField("dropoff_latitude", DoubleType()),
            StructField("dropoff_longitude", DoubleType()),
            StructField("status", StringType()),  # 'pending', 'matched', 'completed', 'cancelled'
            StructField("timestamp", TimestampType())
        ])
        
        request_data = request_stream \
            .selectExpr("CAST(value AS STRING) as json") \
            .select(from_json(col("json"), request_schema).alias("data")) \
            .select("data.*")
        
        # Map to zones
        @udf(returnType=StringType())
        def get_h3_zone(lat: float, lng: float) -> str:
            return self.h3_manager.get_zone_for_location(lat, lng)
        
        request_with_zones = request_data \
            .withColumn("zone_id", get_h3_zone(col("pickup_latitude"), col("pickup_longitude")))
        
        # Aggregate demand
        zone_demand = request_with_zones \
            .withWatermark("timestamp", "2 minutes") \
            .groupBy(
                window(col("timestamp"), "1 minute"),
                col("zone_id")
            ) \
            .agg(
                count(when(col("status") == "pending", col("request_id"))).alias("pending_requests"),
                count(when(col("status") == "completed", col("request_id"))).alias("completed_rides"),
                count(col("request_id")).alias("total_requests")
            ) \
            .select(
                col("zone_id"),
                col("pending_requests"),
                col("completed_rides"),
                col("total_requests"),
                col("window.end").alias("window_end")
            )
        
        return zone_demand
    
    def compute_supply_demand_ratio(self, supply_df: DataFrame, demand_df: DataFrame):
        """
        Join supply and demand to compute ratio
        """
        
        # Join on zone and time window
        joined = supply_df.join(
            demand_df,
            on=["zone_id", "window_end"],
            how="full_outer"
        ).fillna(0)
        
        # Calculate supply/demand ratio
        metrics = joined \
            .withColumn(
                "supply_demand_ratio",
                when(col("total_requests") > 0,
                     col("available_drivers") / col("total_requests"))
                .otherwise(10.0)  # High ratio when no demand
            ) \
            .withColumn(
                "avg_wait_time_seconds",
                when(col("available_drivers") > 0,
                     lit(60) / col("available_drivers"))  # Simplified
                .otherwise(600)  # 10 minutes default
            )
        
        return metrics
    
    def publish_to_redis(self, metrics_df: DataFrame):
        """
        Write zone metrics to Redis for fast lookups
        """
        
        def write_to_redis(partition):
            import redis
            r = redis.Redis(host='redis-cluster', port=6379, decode_responses=True)
            
            for row in partition:
                zone_id = row['zone_id']
                
                # Store as hash
                r.hset(f"zone_metrics:{zone_id}", mapping={
                    'available_drivers': row['available_drivers'],
                    'busy_drivers': row['busy_drivers'],
                    'pending_requests': row['pending_requests'],
                    'supply_demand_ratio': row['supply_demand_ratio'],
                    'avg_wait_time_seconds': row['avg_wait_time_seconds'],
                    'updated_at': row['window_end'].isoformat()
                })
                
                # Set TTL
                r.expire(f"zone_metrics:{zone_id}", 300)  # 5 minutes
        
        # Write to Redis (foreachBatch for streaming)
        query = metrics_df.writeStream \
            .foreachBatch(lambda batch_df, batch_id: batch_df.foreachPartition(write_to_redis)) \
            .outputMode("update") \
            .start()
        
        return query


### **3. Surge Multiplier Calculation**

```python
from typing import Dict, List
import math
from dataclasses import dataclass
from datetime import datetime, time

@dataclass
class SurgeMultiplier:
    zone_id: str
    multiplier: float
    base_multiplier: float
    demand_factor: float
    time_factor: float
    weather_factor: float
    event_factor: float
    calculated_at: datetime

class SurgePricingEngine:
    """
    Calculate surge pricing multipliers based on multiple factors
    """
    
    def __init__(self, redis_client, ml_model=None):
        self.redis = redis_client
        self.ml_model = ml_model
        
        # Pricing configuration
        self.min_multiplier = 1.0
        self.max_multiplier = 5.0
        self.smoothing_factor = 0.3  # Prevent sudden price jumps
    
    def calculate_surge_multiplier(self, zone_id: str, timestamp: datetime) -> SurgeMultiplier:
        """
        Calculate comprehensive surge multiplier
        """
        
        # 1. Get supply-demand metrics
        metrics = self._get_zone_metrics(zone_id)
        
        # 2. Calculate base multiplier from supply/demand ratio
        demand_factor = self._calculate_demand_factor(metrics)
        
        # 3. Time-based adjustments
        time_factor = self._calculate_time_factor(timestamp)
        
        # 4. Weather impact
        weather_factor = self._calculate_weather_factor(zone_id)
        
        # 5. Event impact (concerts, sports, conferences)
        event_factor = self._calculate_event_factor(zone_id, timestamp)
        
        # 6. ML model prediction (optional enhancement)
        ml_adjustment = self._get_ml_adjustment(zone_id, timestamp) if self.ml_model else 1.0
        
        # 7. Combine factors
        raw_multiplier = (
            demand_factor *
            time_factor *
            weather_factor *
            event_factor *
            ml_adjustment
        )
        
        # 8. Apply smoothing to prevent spikes
        current_multiplier = self._get_current_multiplier(zone_id)
        smoothed_multiplier = self._smooth_multiplier(current_multiplier, raw_multiplier)
        
        # 9. Clamp to min/max
        final_multiplier = max(self.min_multiplier, min(self.max_multiplier, smoothed_multiplier))
        
        # 10. Round to 2 decimals
        final_multiplier = round(final_multiplier, 2)
        
        return SurgeMultiplier(
            zone_id=zone_id,
            multiplier=final_multiplier,
            base_multiplier=demand_factor,
            demand_factor=demand_factor,
            time_factor=time_factor,
            weather_factor=weather_factor,
            event_factor=event_factor,
            calculated_at=timestamp
        )
    
    def _calculate_demand_factor(self, metrics: Dict) -> float:
        """
        Calculate multiplier based on supply/demand ratio
        
        Ratio > 2.0: No surge (1.0x)
        Ratio 1.0-2.0: Low surge (1.0x - 1.5x)
        Ratio 0.5-1.0: Medium surge (1.5x - 2.5x)
        Ratio < 0.5: High surge (2.5x - 5.0x)
        """
        
        ratio = metrics.get('supply_demand_ratio', 1.0)
        
        if ratio >= 2.0:
            return 1.0
        elif ratio >= 1.0:
            # Linear interpolation 1.0 to 1.5
            return 1.0 + (2.0 - ratio) * 0.5
        elif ratio >= 0.5:
            # Linear interpolation 1.5 to 2.5
            return 1.5 + (1.0 - ratio) * 2.0
        else:
            # Linear interpolation 2.5 to 5.0
            return 2.5 + (0.5 - ratio) * 5.0
    
    def _calculate_time_factor(self, timestamp: datetime) -> float:
        """
        Time-based pricing adjustments
        """
        
        hour = timestamp.hour
        day_of_week = timestamp.weekday()
        
        # Rush hours (weekdays 7-9 AM, 5-7 PM)
        is_weekday = day_of_week < 5
        is_morning_rush = is_weekday and 7 <= hour < 9
        is_evening_rush = is_weekday and 17 <= hour < 19
        
        # Weekend late nights (Fri-Sat 10 PM - 3 AM)
        is_weekend = day_of_week >= 4
        is_late_night = is_weekend and (hour >= 22 or hour < 3)
        
        if is_morning_rush or is_evening_rush:
            return 1.3  # 30% increase
        elif is_late_night:
            return 1.5  # 50% increase
        elif 3 <= hour < 6:
            return 1.2  # 20% increase (early morning)
        else:
            return 1.0  # No adjustment
    
    def _calculate_weather_factor(self, zone_id: str) -> float:
        """
        Weather impact on pricing
        """
        
        # Get weather data from cache/API
        weather = self._get_weather_data(zone_id)
        
        if not weather:
            return 1.0
        
        condition = weather.get('condition', 'clear')
        temperature = weather.get('temperature_celsius', 20)
        
        # Rain/Snow increases demand
        if condition in ['heavy_rain', 'snow', 'thunderstorm']:
            return 1.4
        elif condition in ['light_rain', 'drizzle']:
            return 1.2
        
        # Extreme temperatures
        if temperature < 0 or temperature > 35:
            return 1.2
        
        return 1.0
    
    def _calculate_event_factor(self, zone_id: str, timestamp: datetime) -> float:
        """
        Special events impact (concerts, sports, conferences)
        """
        
        # Query events database
        active_events = self._get_active_events(zone_id, timestamp)
        
        if not active_events:
            return 1.0
        
        max_factor = 1.0
        
        for event in active_events:
            event_type = event['type']
            expected_attendance = event['expected_attendance']
            
            # Large events have bigger impact
            if expected_attendance > 50000:
                factor = 2.0
            elif expected_attendance > 20000:
                factor = 1.5
            elif expected_attendance > 5000:
                factor = 1.3
            else:
                factor = 1.1
            
            max_factor = max(max_factor, factor)
        
        return max_factor
    
    def _smooth_multiplier(self, current: float, new: float) -> float:
        """
        Smooth multiplier changes to prevent sudden jumps
        Exponential moving average
        """
        
        if current is None:
            return new
        
        # Weighted average (30% new, 70% current)
        return (self.smoothing_factor * new) + ((1 - self.smoothing_factor) * current)
    
    def _get_current_multiplier(self, zone_id: str) -> float:
        """Get current multiplier from Redis"""
        
        current = self.redis.hget(f"surge:{zone_id}", "multiplier")
        return float(current) if current else None
    
    def publish_surge_multiplier(self, surge: SurgeMultiplier):
        """
        Publish surge multiplier to Redis and Kafka
        """
        
        # Store in Redis (for fast reads)
        self.redis.hset(f"surge:{surge.zone_id}", mapping={
            'multiplier': surge.multiplier,
            'updated_at': surge.calculated_at.isoformat(),
            'demand_factor': surge.demand_factor,
            'time_factor': surge.time_factor,
            'weather_factor': surge.weather_factor,
            'event_factor': surge.event_factor
        })
        
        # Set TTL
        self.redis.expire(f"surge:{surge.zone_id}", 300)  # 5 minutes
        
        # Publish update event to Kafka (for analytics)
        self._publish_to_kafka('surge-multiplier-updates', {
            'zone_id': surge.zone_id,
            'multiplier': surge.multiplier,
            'timestamp': surge.calculated_at.isoformat()
        })


### **4. Price Quote Service**

```python
from flask import Flask, request, jsonify
from typing import Dict
import redis
import time

app = Flask(__name__)

class PriceQuoteService:
    """
    Fast price quote service (<100ms latency)
    """
    
    def __init__(self, redis_client, h3_manager):
        self.redis = redis_client
        self.h3_manager = h3_manager
        
        # Base pricing configuration
        self.base_rate_per_km = 1.5  # USD
        self.base_rate_per_minute = 0.25  # USD
        self.booking_fee = 2.0  # USD
        self.minimum_fare = 5.0  # USD
    
    @app.route('/v1/estimate', methods=['GET'])
    def get_price_estimate(self):
        """
        GET /v1/estimate?pickup_lat=37.7749&pickup_lng=-122.4194&dropoff_lat=37.8044&dropoff_lng=-122.2712
        """
        
        start_time = time.time()
        
        # Parse parameters
        pickup_lat = float(request.args.get('pickup_lat'))
        pickup_lng = float(request.args.get('pickup_lng'))
        dropoff_lat = float(request.args.get('dropoff_lat'))
        dropoff_lng = float(request.args.get('dropoff_lng'))
        
        # 1. Get pickup zone
        pickup_zone = self.h3_manager.get_zone_for_location(pickup_lat, pickup_lng)
        
        # 2. Get surge multiplier from Redis (cached)
        surge = self._get_surge_multiplier(pickup_zone)
        
        # 3. Calculate distance and time
        distance_km, duration_minutes = self._calculate_route(
            pickup_lat, pickup_lng,
            dropoff_lat, dropoff_lng
        )
        
        # 4. Calculate base fare
        base_fare = self._calculate_base_fare(distance_km, duration_minutes)
        
        # 5. Apply surge
        final_fare = base_fare * surge
        final_fare = max(self.minimum_fare, final_fare)
        
        # 6. Round to 2 decimals
        final_fare = round(final_fare, 2)
        
        # Response time tracking
        response_time_ms = (time.time() - start_time) * 1000
        
        return jsonify({
            'estimated_fare': final_fare,
            'base_fare': base_fare,
            'surge_multiplier': surge,
            'distance_km': distance_km,
            'estimated_duration_minutes': duration_minutes,
            'pickup_zone': pickup_zone,
            'booking_fee': self.booking_fee,
            'minimum_fare': self.minimum_fare,
            'currency': 'USD',
            'response_time_ms': round(response_time_ms, 2)
        }), 200
    
    def _get_surge_multiplier(self, zone_id: str) -> float:
        """Get surge multiplier from Redis cache"""
        
        surge = self.redis.hget(f"surge:{zone_id}", "multiplier")
        
        if surge:
            return float(surge)
        
        # Fallback to 1.0 if not found
        return 1.0
    
    def _calculate_base_fare(self, distance_km: float, duration_minutes: float) -> float:
        """Calculate base fare before surge"""
        
        distance_fare = distance_km * self.base_rate_per_km
        time_fare = duration_minutes * self.base_rate_per_minute
        
        base_fare = self.booking_fee + distance_fare + time_fare
        
        return round(base_fare, 2)
    
    def _calculate_route(self, pickup_lat: float, pickup_lng: float,
                        dropoff_lat: float, dropoff_lng: float) -> tuple:
        """
        Calculate route distance and duration
        In production: Use Google Maps API / OSRM / Valhalla
        """
        
        # Simplified: Haversine distance
        from geopy.distance import geodesic
        
        distance_km = geodesic(
            (pickup_lat, pickup_lng),
            (dropoff_lat, dropoff_lng)
        ).kilometers
        
        # Estimate duration (assume 30 km/h average speed)
        duration_minutes = (distance_km / 30) * 60
        
        return round(distance_km, 2), round(duration_minutes, 1)
```

---

## 🎓 Key Interview Points

### **Capacity Estimation:**
```
Rides: 1M requests/minute globally
Avg ride duration: 20 minutes
Concurrent rides: 1M × 20 / 60 = 333,333

Driver locations: 1M drivers × 1 update/10sec = 100K msg/sec
Kafka throughput: 100K × 500 bytes = 50 MB/sec = 180 GB/hour

Zones: 10K cities × 500 zones/city = 5M zones
Active zones: 10% = 500K zones
Redis memory: 500K × 1KB = 500 MB

Flink cluster: 100K events/sec ÷ 10K events/core = 10 cores minimum
```

### **Critical Trade-offs:**
1. **Latency vs Accuracy** - Cache vs real-time calculation
2. **Granularity vs Data** - Zone size impacts metrics quality
3. **Price Stability vs Revenue** - Smoothing vs instant response

**This demonstrates production ride-sharing pricing - essential for FAANG mobility interviews!** 🚗💰
