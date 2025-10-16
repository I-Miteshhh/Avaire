# Design Real-Time Fraud Detection System - Complete System Design

**Difficulty:** ⭐⭐⭐⭐⭐  
**Interview Frequency:** Very High (PayPal, Stripe, Square, 40 LPA+)  
**Time to Complete:** 45-60 minutes  
**Real-World Examples:** PayPal Fraud Detection, Stripe Radar, Square Risk Engine

---

## 📋 Problem Statement

**Design a real-time fraud detection system that can:**
- Detect fraudulent transactions within milliseconds (<100ms)
- Process 1 million transactions per minute
- Identify multiple fraud patterns (card testing, account takeover, money laundering)
- Minimize false positives (<1% legitimate transactions flagged)
- Support ML model updates without downtime
- Handle graph-based fraud detection (fraud rings, networks)
- Provide real-time risk scores (0-100)
- Support manual review workflow for suspicious transactions
- Comply with regulations (PCI-DSS, AML, KYC)

**Business Goals:**
- Reduce fraud loss to <0.1% of transaction volume
- Maintain <0.5% false positive rate
- Provide explainable fraud decisions
- Minimize friction for legitimate users
- Support A/B testing for fraud rules

---

## 🎯 Functional Requirements

### **Core Features**
1. **Real-Time Scoring**
   - Transaction risk score (0-100) in <100ms
   - Multi-model ensemble (rules + ML)
   - Feature engineering in real-time
   - Decision: allow, block, review

2. **Fraud Pattern Detection**
   - Card testing attacks (multiple small transactions)
   - Account takeover (login from new device/location)
   - Velocity checks (too many transactions too fast)
   - Amount anomalies (unusual transaction sizes)
   - Merchant fraud (fake merchants)
   - Collusion detection (buyer-seller fraud rings)

3. **Entity Resolution**
   - Link users, cards, devices, IP addresses
   - Build fraud graphs (connected entities)
   - Detect fraud rings and networks
   - Shared attribute analysis

4. **Manual Review**
   - Queue suspicious transactions
   - Analyst dashboard with context
   - Decision feedback loop to ML models
   - Case management system

---

## 🏗️ High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     TRANSACTION FLOW                          │
├──────────────────────────────────────────────────────────────┤
│  Payment Gateway → API → Fraud Check → Decision → Response   │
│       (Stripe)      (100ms SLA)    (<50ms)                   │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│               FRAUD DETECTION PIPELINE                        │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  REAL-TIME SCORING SERVICE (Hot Path)                 │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  Transaction     Feature         Model         Risk   │ │
│  │  Request    →   Extraction  →   Ensemble  →   Score   │ │
│  │  (JSON)         (<20ms)         (<30ms)       (0-100) │ │
│  │                                                        │ │
│  │  Features (200+):                                     │ │
│  │  - Transaction amount, currency, merchant             │ │
│  │  - User history (lifetime spend, avg transaction)     │ │
│  │  - Velocity (transactions in last 1h, 24h, 7d)       │ │
│  │  - Device fingerprint, IP geolocation                 │ │
│  │  - Time patterns (hour of day, day of week)           │ │
│  │  - Graph features (entity connections)                │ │
│  │                                                        │ │
│  │  Models:                                              │ │
│  │  1. Rule Engine (blocklist, velocity limits)          │ │
│  │  2. Gradient Boosting (XGBoost)                      │ │
│  │  3. Neural Network (anomaly detection)                │ │
│  │  4. Graph Neural Network (fraud rings)                │ │
│  │                                                        │ │
│  │  Decision Logic:                                      │ │
│  │  - Score 0-30:   Allow (low risk)                    │ │
│  │  - Score 30-70:  Review (medium risk)                │ │
│  │  - Score 70-100: Block (high risk)                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  FEATURE STORE (Redis + PostgreSQL)                   │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  Hot Features (Redis):                                │ │
│  │  - user_txn_count_1h                                  │ │
│  │  - user_txn_count_24h                                 │ │
│  │  - card_decline_count_1h                              │ │
│  │  - ip_txn_count_1h                                    │ │
│  │  - device_user_count (device shared by N users)       │ │
│  │                                                        │ │
│  │  Cold Features (PostgreSQL):                          │ │
│  │  - user_lifetime_spend                                │ │
│  │  - user_account_age_days                              │ │
│  │  - user_chargeback_count                              │ │
│  │  - merchant_fraud_rate                                │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  STREAMING FEATURE COMPUTATION (Flink)                │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  Kafka → Flink → Redis                                │ │
│  │                                                        │ │
│  │  Velocity Features:                                   │ │
│  │  - Tumbling windows (1h, 24h, 7d)                     │ │
│  │  - Session windows (user activity sessions)           │ │
│  │  - Sliding windows (rolling 1h count)                 │ │
│  │                                                        │ │
│  │  Aggregations:                                        │ │
│  │  - COUNT, SUM, AVG, MAX, MIN                          │ │
│  │  - DISTINCT COUNT (unique merchants, IPs)             │ │
│  │  - PERCENTILE (95th percentile transaction amount)    │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                  GRAPH ANALYSIS (Neo4j)                       │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Entity Graph:                                                │
│  ┌──────┐    uses     ┌──────┐    from      ┌──────┐       │
│  │ User │ ─────────→  │ Card │ ←────────────│  IP  │       │
│  └──────┘             └──────┘              └──────┘       │
│      │                   │                      │           │
│      │ transacts_with    │ issued_by            │           │
│      ▼                   ▼                      ▼           │
│  ┌──────┐             ┌──────┐              ┌──────┐       │
│  │Merchant│            │ Bank │              │Device│       │
│  └──────┘             └──────┘              └──────┘       │
│                                                               │
│  Fraud Ring Detection:                                       │
│  - PageRank (identify central fraud nodes)                   │
│  - Community Detection (find fraud clusters)                 │
│  - Shortest Path (connection between entities)               │
│  - Pattern Matching (known fraud patterns)                   │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                   ML MODEL SERVING                            │
├──────────────────────────────────────────────────────────────┤
│  - Model Registry (MLflow)                                   │
│  - A/B Testing (shadow mode, canary deployment)              │
│  - Feature importance tracking                               │
│  - Model performance monitoring (precision, recall, F1)      │
│  - Explainability (SHAP values for decisions)                │
└──────────────────────────────────────────────────────────────┘
```

---

## 💻 Core Implementation

### **1. Real-Time Feature Extraction**

```python
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import redis
import psycopg2
from geopy.geocoders import Nominatim
import hashlib

@dataclass
class Transaction:
    transaction_id: str
    user_id: str
    card_id: str
    merchant_id: str
    amount: float
    currency: str
    ip_address: str
    device_id: str
    timestamp: datetime
    merchant_category: str
    card_type: str  # credit, debit

@dataclass
class FeatureVector:
    # Transaction features
    amount: float
    hour_of_day: int
    day_of_week: int
    is_international: bool
    
    # User features
    user_account_age_days: int
    user_lifetime_spend: float
    user_avg_transaction: float
    user_txn_count_1h: int
    user_txn_count_24h: int
    user_txn_count_7d: int
    user_chargeback_count: int
    
    # Card features
    card_txn_count_1h: int
    card_decline_count_1h: int
    card_is_new: bool  # First transaction
    
    # Velocity features
    amount_vs_user_avg_ratio: float
    distinct_merchants_24h: int
    distinct_ips_24h: int
    
    # Device features
    device_user_count: int  # How many users share this device
    device_txn_count_1h: int
    
    # IP features
    ip_country: str
    ip_txn_count_1h: int
    ip_user_count: int
    
    # Graph features
    user_fraud_neighbor_count: int  # Connected to known fraudsters

class FeatureExtractor:
    """
    Extract 200+ features for fraud detection in <20ms
    """
    
    def __init__(self, redis_client, postgres_conn):
        self.redis = redis_client
        self.postgres = postgres_conn
        self.geolocator = Nominatim(user_agent="fraud_detection")
    
    def extract_features(self, txn: Transaction) -> FeatureVector:
        """
        Extract all features in parallel
        """
        
        # Parallel feature extraction
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all feature extraction tasks
            future_txn = executor.submit(self._extract_transaction_features, txn)
            future_user = executor.submit(self._extract_user_features, txn.user_id)
            future_card = executor.submit(self._extract_card_features, txn.card_id)
            future_velocity = executor.submit(self._extract_velocity_features, txn)
            future_graph = executor.submit(self._extract_graph_features, txn.user_id)
            
            # Wait for all
            txn_features = future_txn.result()
            user_features = future_user.result()
            card_features = future_card.result()
            velocity_features = future_velocity.result()
            graph_features = future_graph.result()
        
        # Combine all features
        return FeatureVector(
            **txn_features,
            **user_features,
            **card_features,
            **velocity_features,
            **graph_features
        )
    
    def _extract_transaction_features(self, txn: Transaction) -> Dict:
        """Extract features from transaction itself"""
        
        return {
            'amount': txn.amount,
            'hour_of_day': txn.timestamp.hour,
            'day_of_week': txn.timestamp.weekday(),
            'is_international': self._is_international_txn(txn),
        }
    
    def _extract_user_features(self, user_id: str) -> Dict:
        """Extract user historical features"""
        
        # Hot features from Redis
        user_txn_1h = int(self.redis.get(f"user:{user_id}:txn_count_1h") or 0)
        user_txn_24h = int(self.redis.get(f"user:{user_id}:txn_count_24h") or 0)
        user_txn_7d = int(self.redis.get(f"user:{user_id}:txn_count_7d") or 0)
        
        # Cold features from PostgreSQL
        cursor = self.postgres.cursor()
        cursor.execute("""
            SELECT 
                EXTRACT(DAY FROM NOW() - created_at) as account_age_days,
                lifetime_spend,
                avg_transaction_amount,
                chargeback_count
            FROM users
            WHERE user_id = %s
        """, (user_id,))
        
        row = cursor.fetchone()
        
        if not row:
            # New user - high risk
            return {
                'user_account_age_days': 0,
                'user_lifetime_spend': 0.0,
                'user_avg_transaction': 0.0,
                'user_txn_count_1h': user_txn_1h,
                'user_txn_count_24h': user_txn_24h,
                'user_txn_count_7d': user_txn_7d,
                'user_chargeback_count': 0
            }
        
        return {
            'user_account_age_days': int(row[0]),
            'user_lifetime_spend': float(row[1]),
            'user_avg_transaction': float(row[2]),
            'user_txn_count_1h': user_txn_1h,
            'user_txn_count_24h': user_txn_24h,
            'user_txn_count_7d': user_txn_7d,
            'user_chargeback_count': int(row[3])
        }
    
    def _extract_card_features(self, card_id: str) -> Dict:
        """Extract card features"""
        
        card_txn_1h = int(self.redis.get(f"card:{card_id}:txn_count_1h") or 0)
        card_decline_1h = int(self.redis.get(f"card:{card_id}:decline_count_1h") or 0)
        
        # Check if first transaction
        card_first_txn = self.redis.get(f"card:{card_id}:first_txn_timestamp")
        card_is_new = card_first_txn is None
        
        return {
            'card_txn_count_1h': card_txn_1h,
            'card_decline_count_1h': card_decline_1h,
            'card_is_new': card_is_new
        }
    
    def _extract_velocity_features(self, txn: Transaction) -> Dict:
        """Extract velocity-based features"""
        
        # Get user's average transaction amount
        user_avg = float(self.redis.get(f"user:{txn.user_id}:avg_amount") or 100.0)
        amount_ratio = txn.amount / user_avg if user_avg > 0 else 10.0
        
        # Get distinct merchants in 24h
        merchants_24h = self.redis.scard(f"user:{txn.user_id}:merchants_24h")
        
        # Get distinct IPs in 24h
        ips_24h = self.redis.scard(f"user:{txn.user_id}:ips_24h")
        
        return {
            'amount_vs_user_avg_ratio': amount_ratio,
            'distinct_merchants_24h': merchants_24h,
            'distinct_ips_24h': ips_24h,
        }
    
    def _extract_device_ip_features(self, txn: Transaction) -> Dict:
        """Extract device and IP features"""
        
        # Device features
        device_user_count = self.redis.scard(f"device:{txn.device_id}:users")
        device_txn_1h = int(self.redis.get(f"device:{txn.device_id}:txn_count_1h") or 0)
        
        # IP features
        ip_txn_1h = int(self.redis.get(f"ip:{txn.ip_address}:txn_count_1h") or 0)
        ip_user_count = self.redis.scard(f"ip:{txn.ip_address}:users")
        
        # IP geolocation
        ip_country = self._get_ip_country(txn.ip_address)
        
        return {
            'device_user_count': device_user_count,
            'device_txn_count_1h': device_txn_1h,
            'ip_country': ip_country,
            'ip_txn_count_1h': ip_txn_1h,
            'ip_user_count': ip_user_count
        }
    
    def _extract_graph_features(self, user_id: str) -> Dict:
        """Extract graph-based features (fraud network)"""
        
        # Query Neo4j for fraud connections
        fraud_neighbor_count = self._count_fraud_neighbors(user_id)
        
        return {
            'user_fraud_neighbor_count': fraud_neighbor_count
        }
    
    def _count_fraud_neighbors(self, user_id: str) -> int:
        """Count how many known fraudsters are connected to this user"""
        
        # Cached in Redis
        cached = self.redis.get(f"user:{user_id}:fraud_neighbors")
        if cached:
            return int(cached)
        
        # Query Neo4j (expensive operation, cache result)
        # This would be a Cypher query in production
        # MATCH (u:User {id: $user_id})-[:CONNECTED_TO*1..2]-(f:User {is_fraud: true})
        # RETURN count(DISTINCT f)
        
        return 0  # Placeholder


### **2. Real-Time Fraud Scoring**

```python
import xgboost as xgb
import numpy as np
from typing import Dict, List, Tuple
from enum import Enum

class FraudDecision(Enum):
    ALLOW = "allow"
    REVIEW = "review"
    BLOCK = "block"

@dataclass
class FraudScore:
    transaction_id: str
    risk_score: float  # 0-100
    decision: FraudDecision
    contributing_factors: List[str]
    model_version: str
    processing_time_ms: float

class FraudScoringEngine:
    """
    Ensemble of fraud detection models
    """
    
    def __init__(self, model_path: str):
        # Load models
        self.xgboost_model = xgb.Booster()
        self.xgboost_model.load_model(f"{model_path}/xgboost_v1.model")
        
        # Rule thresholds
        self.VELOCITY_THRESHOLD_1H = 10  # Max 10 transactions per hour
        self.AMOUNT_THRESHOLD = 10000  # Max $10,000 per transaction
        self.NEW_CARD_HIGH_AMOUNT = 500  # New card max $500
        
        # Decision thresholds
        self.REVIEW_THRESHOLD = 30
        self.BLOCK_THRESHOLD = 70
    
    def score_transaction(self, features: FeatureVector) -> FraudScore:
        """
        Score transaction using ensemble of models
        """
        
        import time
        start_time = time.time()
        
        # 1. Rule-based scoring (fast, explainable)
        rule_score, rule_factors = self._apply_rules(features)
        
        # 2. ML model scoring (accurate)
        ml_score = self._apply_ml_model(features)
        
        # 3. Combine scores (weighted average)
        final_score = (0.4 * rule_score) + (0.6 * ml_score)
        final_score = min(100, max(0, final_score))
        
        # 4. Make decision
        decision = self._make_decision(final_score)
        
        # Processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        return FraudScore(
            transaction_id="txn_123",  # Would come from transaction
            risk_score=round(final_score, 2),
            decision=decision,
            contributing_factors=rule_factors,
            model_version="v1.2.3",
            processing_time_ms=round(processing_time_ms, 2)
        )
    
    def _apply_rules(self, features: FeatureVector) -> Tuple[float, List[str]]:
        """
        Hard-coded business rules
        """
        
        score = 0.0
        factors = []
        
        # Rule 1: Velocity check
        if features.user_txn_count_1h > self.VELOCITY_THRESHOLD_1H:
            score += 40
            factors.append(f"High velocity: {features.user_txn_count_1h} txns in 1h")
        
        # Rule 2: Large amount
        if features.amount > self.AMOUNT_THRESHOLD:
            score += 30
            factors.append(f"Large amount: ${features.amount}")
        
        # Rule 3: New card with high amount
        if features.card_is_new and features.amount > self.NEW_CARD_HIGH_AMOUNT:
            score += 50
            factors.append(f"New card with ${features.amount} transaction")
        
        # Rule 4: Amount anomaly
        if features.amount_vs_user_avg_ratio > 10:
            score += 35
            factors.append(f"Amount {features.amount_vs_user_avg_ratio}x user average")
        
        # Rule 5: Multiple declined transactions
        if features.card_decline_count_1h > 3:
            score += 45
            factors.append(f"Card testing: {features.card_decline_count_1h} declines")
        
        # Rule 6: Device shared by many users
        if features.device_user_count > 5:
            score += 25
            factors.append(f"Device shared by {features.device_user_count} users")
        
        # Rule 7: New account
        if features.user_account_age_days < 7:
            score += 20
            factors.append(f"New account: {features.user_account_age_days} days old")
        
        # Rule 8: International transaction
        if features.is_international:
            score += 15
            factors.append("International transaction")
        
        # Rule 9: Connected to fraudsters
        if features.user_fraud_neighbor_count > 0:
            score += 60
            factors.append(f"Connected to {features.user_fraud_neighbor_count} fraudsters")
        
        # Cap at 100
        score = min(100, score)
        
        return score, factors
    
    def _apply_ml_model(self, features: FeatureVector) -> float:
        """
        Apply XGBoost model
        """
        
        # Convert features to array
        feature_array = np.array([
            features.amount,
            features.hour_of_day,
            features.day_of_week,
            float(features.is_international),
            features.user_account_age_days,
            features.user_lifetime_spend,
            features.user_avg_transaction,
            features.user_txn_count_1h,
            features.user_txn_count_24h,
            features.user_txn_count_7d,
            features.user_chargeback_count,
            features.card_txn_count_1h,
            features.card_decline_count_1h,
            float(features.card_is_new),
            features.amount_vs_user_avg_ratio,
            features.distinct_merchants_24h,
            features.distinct_ips_24h,
            features.device_user_count,
            features.device_txn_count_1h,
            features.ip_txn_count_1h,
            features.ip_user_count,
            features.user_fraud_neighbor_count
        ]).reshape(1, -1)
        
        # Predict
        dmatrix = xgb.DMatrix(feature_array)
        prediction = self.xgboost_model.predict(dmatrix)[0]
        
        # Convert probability to score (0-100)
        score = prediction * 100
        
        return score
    
    def _make_decision(self, score: float) -> FraudDecision:
        """Convert score to decision"""
        
        if score >= self.BLOCK_THRESHOLD:
            return FraudDecision.BLOCK
        elif score >= self.REVIEW_THRESHOLD:
            return FraudDecision.REVIEW
        else:
            return FraudDecision.ALLOW


### **3. Streaming Velocity Feature Computation**

```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment
from pyflink.table.window import Tumble

def create_velocity_pipeline():
    """
    Flink pipeline to compute real-time velocity features
    """
    
    env = StreamExecutionEnvironment.get_execution_environment()
    t_env = StreamTableEnvironment.create(env)
    
    # Read from Kafka
    t_env.execute_sql("""
        CREATE TABLE transactions (
            transaction_id STRING,
            user_id STRING,
            card_id STRING,
            ip_address STRING,
            device_id STRING,
            merchant_id STRING,
            amount DOUBLE,
            currency STRING,
            status STRING,
            event_time TIMESTAMP(3),
            WATERMARK FOR event_time AS event_time - INTERVAL '30' SECOND
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'transactions',
            'properties.bootstrap.servers' = 'kafka:9092',
            'properties.group.id' = 'fraud-detection',
            'scan.startup.mode' = 'latest-offset',
            'format' = 'json'
        )
    """)
    
    # User transaction count (1-hour tumbling window)
    t_env.execute_sql("""
        CREATE TABLE user_txn_count_1h (
            user_id STRING,
            window_start TIMESTAMP(3),
            window_end TIMESTAMP(3),
            txn_count BIGINT,
            total_amount DOUBLE,
            distinct_merchants BIGINT,
            distinct_ips BIGINT
        ) WITH (
            'connector' = 'redis',
            'host' = 'redis-cluster',
            'port' = '6379',
            'key-pattern' = 'user:${user_id}:txn_count_1h',
            'ttl' = '3600'
        )
    """)
    
    # Compute aggregations
    t_env.execute_sql("""
        INSERT INTO user_txn_count_1h
        SELECT 
            user_id,
            TUMBLE_START(event_time, INTERVAL '1' HOUR) as window_start,
            TUMBLE_END(event_time, INTERVAL '1' HOUR) as window_end,
            COUNT(*) as txn_count,
            SUM(amount) as total_amount,
            COUNT(DISTINCT merchant_id) as distinct_merchants,
            COUNT(DISTINCT ip_address) as distinct_ips
        FROM transactions
        WHERE status = 'completed'
        GROUP BY 
            user_id,
            TUMBLE(event_time, INTERVAL '1' HOUR)
    """)
    
    # Card decline count (card testing detection)
    t_env.execute_sql("""
        CREATE TABLE card_decline_count_1h (
            card_id STRING,
            decline_count BIGINT
        ) WITH (
            'connector' = 'redis',
            'key-pattern' = 'card:${card_id}:decline_count_1h',
            'ttl' = '3600'
        )
    """)
    
    t_env.execute_sql("""
        INSERT INTO card_decline_count_1h
        SELECT 
            card_id,
            COUNT(*) as decline_count
        FROM transactions
        WHERE status = 'declined'
        GROUP BY 
            card_id,
            TUMBLE(event_time, INTERVAL '1' HOUR)
    """)
    
    env.execute("Fraud Detection Velocity Features")
```

---

## 🎓 Key Interview Points

### **Capacity Estimation:**
```
Transactions: 1M/minute = 16,666/sec
Feature extraction: 200 features × 20ms = <100ms total
Redis memory: 10M users × 20 features × 100 bytes = 20 GB
Flink: 16K events/sec ÷ 1K events/core = 16 cores

False positive rate: 0.5% × 1M txn/min = 5,000 manual reviews/min
Cost of fraud: $100M revenue × 0.1% = $100K/month fraud loss
```

### **Critical Trade-offs:**
1. **Latency vs Accuracy** - Simple rules vs complex ML
2. **False Positives vs False Negatives** - Block fraud vs allow legit
3. **Real-time vs Batch** - Fresh features vs comprehensive analysis

**This demonstrates production fraud detection - essential for fintech interviews!** 🛡️💳
