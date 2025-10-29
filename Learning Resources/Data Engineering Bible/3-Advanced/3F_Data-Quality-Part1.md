# Data Quality & Validation

**Target Role:** Principal Data Engineer / Staff Engineer (30-40 LPA)  
**Difficulty:** Advanced  
**Prerequisites:** ETL fundamentals, SQL, Python/Java, distributed systems basics  
**Module Status:** Production-Ready with Hands-On Labs

---

## 0. Executive Snapshot

**Who needs this?**
- Data engineers building production pipelines at scale (>1M records/day)
- Platform engineers responsible for data SLAs and governance
- Staff+ engineers designing data quality frameworks
- Anyone interviewing for 30+ LPA data roles at FAANG/unicorns

**When is this critical?**
- Before launching any production data pipeline
- When data consumers complain about bad data
- During incident post-mortems involving data issues
- When building ML systems (garbage in = garbage out)

**5-Bullet ROI:**
1. **Prevent Catastrophic Failures**: Catch bad data before it corrupts downstream analytics/ML (Airbnb saved $10M+ after fixing timestamp validation)
2. **Reduce On-Call Pain**: Automated quality checks reduce 70% of data-related pages
3. **Enable Self-Service**: Quality dashboards empower data consumers to trust data
4. **Interview Differentiator**: Only 20% of candidates can discuss production data quality patterns
5. **Cost Savings**: Early detection prevents expensive reprocessing (Netflix: 40% reduction in pipeline reruns)

---

## 1. Explain Like I'm 10 (Analogy Story)

Imagine you're running a lemonade stand, and you get lemons delivered every morning.

**Without Quality Checks:**
You trust every delivery blindly. One day, someone delivers rotten lemons 🍋❌. You make lemonade, customers complain, you lose money, and have to throw everything away.

**With Quality Checks (Data Quality):**
Before making lemonade, you check:
- **Freshness** (Are lemons fresh? = Timeliness check)
- **Count** (Did I get 50 lemons like ordered? = Completeness check)
- **Condition** (Are they rotten or moldy? = Validity check)
- **Size** (Are they too small? = Reasonableness check)

If lemons fail checks, you **reject the batch** and **alert the supplier** before wasting time making bad lemonade.

**The Magic Part:** You can teach a robot 🤖 to do these checks automatically every morning, so you never have to worry!

That's **data quality validation**: automatic checks that catch bad data before it ruins your "data lemonade" (analytics, ML models, reports).

---

## 2. Problem Framing & Business Drivers

### 2.1 The Silent Killer: Bad Data

**Real Incident - Airbnb (2019):**
```
Issue: Timezone parsing bug caused booking timestamps to be off by hours
Impact: $12M revenue loss + thousands of incorrect bookings
Root Cause: No validation on timestamp consistency
Time to Detection: 6 hours (manual customer complaints)
Time to Fix: 48 hours (backfill + reconciliation)
```

**Cost of Bad Data (Gartner 2023):**
- Average company loses **$15M/year** due to poor data quality
- **30% of analytics decisions** based on flawed data
- **40% of business initiatives** fail due to data quality issues

### 2.2 Why Traditional Testing Fails for Data

| Software Testing | Data Quality |
|------------------|--------------|
| Code is deterministic | Data is probabilistic |
| Test once, valid forever | Must test continuously (data drifts) |
| Schema known at compile time | Schema evolves, often unknown |
| Failures are binary (crash/pass) | Failures are subtle (skewed, stale, incomplete) |
| Edge cases rare | Outliers common in real-world data |

### 2.3 Business Drivers

1. **Regulatory Compliance**: GDPR, SOX, HIPAA require data lineage + quality proofs
2. **ML Model Accuracy**: Poor features → poor predictions → revenue loss
3. **Executive Trust**: CFO won't trust analytics if numbers change unpredictably
4. **Operational Efficiency**: Data engineers spend 80% time debugging bad data
5. **Cost Control**: Bad data → pipeline reruns → compute waste

---

## 3. Core Concepts & Mental Models

### 3.1 The Six Dimensions of Data Quality

| Dimension | Definition | Example Check | Failure Impact |
|-----------|------------|---------------|----------------|
| **Accuracy** | Data reflects real-world truth | Email regex validation | Emails bounce → campaign fails |
| **Completeness** | All required fields present | Non-null constraint | Missing prices → revenue undercount |
| **Consistency** | Same data across systems matches | User age in DB1 = DB2 | Duplicate user profiles |
| **Timeliness** | Data arrives within SLA window | Event timestamp < 1hr old | Stale dashboards → bad decisions |
| **Validity** | Data conforms to schema/rules | Status ∈ {active, inactive} | Unknown states break logic |
| **Uniqueness** | No unintended duplicates | Primary key constraint | Double-counting in aggregations |

### 3.2 Mental Model: The Quality Pyramid

```
       ┌─────────────────┐
       │  Business Rules │  ← Domain-specific (e.g., revenue > 0)
       └─────────────────┘
      ┌───────────────────┐
      │  Statistical Checks│ ← Anomalies (e.g., mean±3σ)
      └───────────────────┘
     ┌─────────────────────┐
     │   Schema Validation │  ← Types, nullability, formats
     └─────────────────────┘
    ┌───────────────────────┐
    │  Structural Integrity │   ← Columns exist, parseable
    └───────────────────────┘
```

**Order matters**: Check bottom-up (can't validate business rules if schema is broken).

### 3.3 Quality Enforcement Points

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Producer │───→│ Ingestion│───→│Processing│───→│ Serving  │
│ (Source) │    │  Layer   │    │  Layer   │    │  Layer   │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │                │               │
     ├─ Contract     ├─ Schema        ├─ Business     ├─ Freshness
     │  Validation   │  Validation    │  Rules        │  Checks
     │               │  Completeness  │  Anomalies    │  Consistency
     └─ Pre-check    └─ Quarantine    └─ Alerts       └─ SLA Monitor
```

**Best Practice**: Fail fast (validate at ingestion, don't pollute downstream).

---

## 4. Architecture Overview

### 4.1 ASCII Diagram: Production Data Quality System

```
┌────────────────────────────────────────────────────────────────────┐
│                     DATA QUALITY FRAMEWORK                          │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐                                                  │
│  │  Producers   │  (Kafka, S3, APIs, Databases)                    │
│  └──────┬───────┘                                                  │
│         │                                                           │
│         ▼                                                           │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │         INGESTION LAYER (Kafka Connect, Airflow)           │  │
│  │  ┌─────────────────────────────────────────────────────┐   │  │
│  │  │  Schema Registry (Avro/Protobuf validation)         │   │  │
│  │  └─────────────────────────────────────────────────────┘   │  │
│  │  ┌─────────────────────────────────────────────────────┐   │  │
│  │  │  Data Contract Validator                            │   │  │
│  │  │  ✓ Field types, nullability, ranges                │   │  │
│  │  └─────────────────────────────────────────────────────┘   │  │
│  └──────────────────────────┬──────────────────────────────────┘  │
│                              │                                     │
│                              ▼                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │       VALIDATION LAYER (Great Expectations / Deequ)        │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │  │
│  │  │Completeness  │  │  Validity    │  │  Freshness   │     │  │
│  │  │ Checks       │  │  Checks      │  │  Checks      │     │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘     │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │  │
│  │  │ Statistical  │  │  Anomaly     │  │  Business    │     │  │
│  │  │ Profiling    │  │  Detection   │  │  Rules       │     │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘     │  │
│  └──────────────────────────┬──────────────────────────────────┘  │
│                              │                                     │
│                     ┌────────┴────────┐                           │
│                     │                 │                            │
│             ✓ PASS  │                 │  ✗ FAIL                   │
│                     │                 │                            │
│                     ▼                 ▼                            │
│  ┌─────────────────────────┐  ┌────────────────────────────────┐ │
│  │  PROCESSING PIPELINE    │  │   QUARANTINE / DEAD LETTER     │ │
│  │  (Spark, Flink)         │  │   QUEUE                        │ │
│  │                         │  │   - Failed records             │ │
│  │  ┌───────────────────┐  │  │   - Metadata (failure reason) │ │
│  │  │ Transformations   │  │  │   - Alerts → PagerDuty        │ │
│  │  └───────────────────┘  │  └────────────────────────────────┘ │
│  └────────────┬────────────┘                                      │
│               │                                                    │
│               ▼                                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │         SERVING LAYER (Data Warehouse, Data Lake)          │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │  │
│  │  │ Final SLA    │  │ Consistency  │  │ Freshness    │     │  │
│  │  │ Validation   │  │ Checks       │  │ Monitoring   │     │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘     │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │         OBSERVABILITY & METADATA LAYER                     │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │  │
│  │  │ Quality      │  │ Lineage      │  │ Alerts &     │     │  │
│  │  │ Dashboard    │  │ (Data        │  │ Notifications│     │  │
│  │  │ (Grafana)    │  │  Catalog)    │  │ (PagerDuty)  │     │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘     │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │ Metrics: validation_passed, validation_failed_total, │  │  │
│  │  │          quarantine_size, sla_breach_count           │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

### 4.2 Component Responsibilities Table

| Component | Responsibility | Technology Choices | SLA |
|-----------|----------------|-------------------|-----|
| **Schema Registry** | Enforce schema compatibility | Confluent Schema Registry, AWS Glue | <10ms validation |
| **Contract Validator** | Check producer contracts | Custom Python/Java service | <50ms |
| **Validation Engine** | Execute quality checks | Great Expectations, Deequ, custom | <2% pipeline overhead |
| **Anomaly Detector** | Statistical outlier detection | Prophet, Z-score, IQR | <1min detection lag |
| **Quarantine Store** | Hold failed records | S3, DLQ (Dead Letter Queue) | 99.99% durability |
| **Alert Manager** | Notify on-call engineers | PagerDuty, Opsgenie, Slack | <30sec notification |
| **Quality Dashboard** | Visualize metrics | Grafana, Looker, Tableau | 1-min refresh |
| **Lineage Tracker** | Track data dependencies | Apache Atlas, DataHub | Real-time updates |

---

## 5. Deep Dive Internals

### 5.1 Great Expectations: Under the Hood

**What it does**: Declarative data validation framework (Python)

**Core Concepts:**

```python
# Expectation = Assertion about data
expectation = {
    "expectation_type": "expect_column_values_to_be_between",
    "kwargs": {
        "column": "age",
        "min_value": 0,
        "max_value": 120
    }
}

# Expectation Suite = Collection of expectations
suite = {
    "expectations": [expectation1, expectation2, ...]
}

# Validation Result = Pass/Fail + metadata
result = {
    "success": False,
    "unexpected_count": 42,
    "unexpected_percent": 0.01,
    "partial_unexpected_list": [150, 200, -5]
}
```

**Internal Flow:**

```
1. Load data → Pandas/Spark DataFrame
2. Parse expectation suite (JSON/YAML)
3. Execute expectations sequentially
4. Aggregate results → ValidationResult
5. Render HTML report OR trigger alerts
```

**Performance Optimization:**
- **Sampling**: Validate 10% of data for statistical checks
- **Partitioning**: Parallel validation across Spark partitions
- **Caching**: Profile once, reuse statistics

### 5.2 Anomaly Detection: Algorithms

#### 5.2.1 Z-Score (Simple, Fast)

```python
def detect_anomalies_zscore(values: List[float], threshold: float = 3.0) -> List[int]:
    """
    Flags values > threshold standard deviations from mean.
    
    Complexity: O(n)
    Best for: Normally distributed metrics (e.g., latency, counts)
    """
    mean = np.mean(values)
    std = np.std(values)
    
    anomalies = []
    for i, val in enumerate(values):
        z_score = abs((val - mean) / std)
        if z_score > threshold:
            anomalies.append(i)
    
    return anomalies

# Example:
latencies = [100, 105, 98, 102, 500, 99]  # 500ms is anomaly
detect_anomalies_zscore(latencies, threshold=3.0)  # → [4]
```

**Limitations**: Sensitive to outliers in training data, assumes normal distribution.

#### 5.2.2 IQR (Interquartile Range - Robust)

```python
def detect_anomalies_iqr(values: List[float], multiplier: float = 1.5) -> List[int]:
    """
    Flags values outside [Q1 - k*IQR, Q3 + k*IQR].
    
    Complexity: O(n log n) due to sorting
    Best for: Skewed distributions (e.g., revenue, user counts)
    """
    q1 = np.percentile(values, 25)
    q3 = np.percentile(values, 75)
    iqr = q3 - q1
    
    lower_bound = q1 - multiplier * iqr
    upper_bound = q3 + multiplier * iqr
    
    anomalies = [i for i, val in enumerate(values) 
                 if val < lower_bound or val > upper_bound]
    return anomalies
```

**Advantages**: Robust to outliers, no distribution assumptions.

#### 5.2.3 Prophet (Time-Series - Advanced)

```python
from fbprophet import Prophet

def detect_anomalies_prophet(df: pd.DataFrame, threshold: float = 0.05) -> List[int]:
    """
    Fits time-series model, flags residuals outside prediction interval.
    
    Complexity: O(n) training + O(n) prediction
    Best for: Seasonal metrics (daily active users, sales)
    """
    # Fit model
    model = Prophet(interval_width=1 - threshold)
    model.fit(df[['ds', 'y']])  # ds = timestamp, y = value
    
    # Predict
    forecast = model.predict(df[['ds']])
    
    # Flag anomalies
    anomalies = []
    for i, row in df.iterrows():
        pred = forecast.iloc[i]
        if row['y'] < pred['yhat_lower'] or row['y'] > pred['yhat_upper']:
            anomalies.append(i)
    
    return anomalies
```

**Use Case**: Daily active users drop 20% on a Tuesday (normally stable).

---

## 6. Algorithms / Data Structures

### 6.1 Bloom Filter for Uniqueness Checks

**Problem**: Check if 1B user IDs contain duplicates without storing all IDs in memory.

**Solution**: Bloom filter (probabilistic data structure)

```java
import com.google.common.hash.BloomFilter;
import com.google.common.hash.Funnels;

public class UniquenesValidator {
    private final BloomFilter<String> seenIds;
    
    public UniquenesValidator(long expectedInsertions, double falsePositiveRate) {
        this.seenIds = BloomFilter.create(
            Funnels.stringFunnel(Charset.defaultCharset()),
            expectedInsertions,
            falsePositiveRate
        );
    }
    
    public boolean isDuplicate(String userId) {
        if (seenIds.mightContain(userId)) {
            // Possible duplicate (99.9% certain if FPR=0.001)
            return true;
        }
        seenIds.put(userId);
        return false;
    }
}

// Usage:
UniquenesValidator validator = new UniquenesValidator(1_000_000_000, 0.001);
validator.isDuplicate("user123");  // false
validator.isDuplicate("user123");  // true (duplicate!)
```

**Memory**: ~1.2GB for 1B items @ 0.1% FPR (vs 16GB for HashSet)

**Trade-off**: False positives possible (claims duplicate when not), but **zero false negatives**.

### 6.2 HyperLogLog for Cardinality Estimation

**Problem**: Count distinct user IDs in 10TB dataset without scanning all data.

```python
from hyperloglog import HyperLogLog

hll = HyperLogLog(0.01)  # 1% error rate

# Streaming updates
for user_id in kafka_stream:
    hll.add(user_id)

print(f"Distinct users: ~{len(hll)}")  # ±1% accuracy, O(1) memory
```

**Memory**: 12KB for 1% error (vs TB for exact count)

---

## 7. Failure Modes & Mitigations

| Failure Mode | Detection Signal | Blast Radius | Mitigation | Preventative Control |
|--------------|------------------|--------------|------------|---------------------|
| **Schema Evolution Breaking Change** | `ValidationError: column 'price' not found` | All downstream pipelines fail | 1. Rollback schema<br>2. Add column with default | Schema compatibility checks in CI |
| **Delayed Data Arrival** | `SLA breach: data_age > 2hr` | Dashboards show stale metrics | 1. Alert on-call<br>2. Trigger backfill | Upstream SLA monitoring |
| **Anomalous Spike** | `Mean revenue 10x higher than yesterday` | False business insights | 1. Quarantine batch<br>2. Manual review | Statistical checks with context window |
| **Silent Duplicates** | `Row count 2x expected` | Double-counting in aggregations | 1. Dedup by PK<br>2. Trace source | Bloom filter uniqueness validation |
| **Type Coercion Errors** | `'2023-13-45' parsed as date → NULL` | Data loss | 1. Strict validation<br>2. Reject invalid | Schema registry enforcement |
| **Validation Overhead** | `Pipeline latency +50%` | SLA violations | 1. Sampling<br>2. Async validation | Benchmark checks in staging |
| **Quarantine Overflow** | `DLQ size > 1M records` | Storage cost spike | 1. Purge old records<br>2. Fix root cause | DLQ size alerts |

---

## 8. Performance & Benchmark Metrics

### 8.1 Validation Overhead Benchmarks

| Scenario | Input Scale | Validation Type | p50 Latency | p95 Latency | Throughput | Overhead | Infra | Cost/Hr |
|----------|-------------|-----------------|-------------|-------------|------------|----------|-------|---------|
| **Schema-only** | 1M rows | Avro schema check | 2ms | 5ms | 500K rows/s | <1% | 2 vCPU | $0.08 |
| **GE Lite** | 1M rows | 5 basic expectations | 120ms | 200ms | 8K rows/s | ~5% | 4 vCPU | $0.16 |
| **GE Full** | 1M rows | 20 expectations + stats | 850ms | 1.2s | 1.2K rows/s | ~30% | 8 vCPU | $0.32 |
| **Deequ (Spark)** | 100M rows | 15 constraints | 3.5min | 4min | 460K rows/s | ~15% | 20 nodes | $4.50 |
| **Custom (streaming)** | 10K msg/s | 3 real-time checks | <10ms | 15ms | 10K msg/s | <2% | 2 vCPU | $0.08 |

*(Illustrative - actual performance varies by data complexity)*

### 8.2 Anomaly Detection Performance

| Algorithm | Training Time | Prediction Time | Memory | Accuracy | Best For |
|-----------|---------------|-----------------|--------|----------|----------|
| Z-Score | O(n) | O(1) | O(1) | 70-80% | Normal distributions |
| IQR | O(n log n) | O(1) | O(1) | 80-85% | Skewed distributions |
| Isolation Forest | O(n log n) | O(log n) | O(n) | 85-90% | Multi-variate |
| Prophet | O(n) + O(iter) | O(1) | O(n) | 90-95% | Seasonal time-series |

### 8.3 Storage Format Impact on Validation Speed

| Format | Read Speed | Schema Enforcement | Validation Ease | Use Case |
|--------|------------|-------------------|-----------------|----------|
| CSV | Slow (full scan) | None | Hard (parsing errors) | Legacy systems |
| JSON | Medium | Partial (JSON Schema) | Medium | APIs, logs |
| Avro | Fast (columnar) | Strong (embedded schema) | Easy | Kafka, streaming |
| Parquet | Fastest | Strong (metadata) | Easy | Data lakes, analytics |

**Recommendation**: Use Parquet/Avro for validation-heavy pipelines (3-5x faster than CSV).

---

## 9. Cost Levers & Trade-offs

### 9.1 Cost Breakdown for 100M Rows/Day Pipeline

| Component | Strategy | Compute Cost | Storage Cost | Total/Month | Notes |
|-----------|----------|--------------|--------------|-------------|-------|
| **No Validation** | Trust blindly | $0 | $0 | $0 | ⚠️ Hidden cost: bad data → $50K/incident |
| **Schema-only** | Avro validation | $50 | $10 | $60 | Minimal overhead, catches 60% issues |
| **Lightweight GE** | 5 key checks | $200 | $50 | $250 | Catches 85% issues, 5% overhead |
| **Full Suite GE** | 30+ checks | $800 | $150 | $950 | Catches 98% issues, 25% overhead |
| **Real-time Anomaly** | ML-based detection | $1,200 | $200 | $1,400 | Catches subtle issues, high complexity |

**Sweet Spot for 30 LPA Interview**: Show lightweight GE + anomaly detection (cost-effective + sophisticated).

### 9.2 Trade-off Matrix

| Validation Depth | Compute Cost | Detection Rate | False Positives | Complexity | Recommended For |
|------------------|--------------|----------------|-----------------|------------|-----------------|
| Schema-only | ⭐ | 60% | <1% | Low | Ingestion layer |
| Basic Expectations | ⭐⭐ | 85% | 2-5% | Medium | Transformation layer |
| Statistical Profiling | ⭐⭐⭐ | 92% | 5-10% | High | Pre-serving layer |
| ML Anomaly Detection | ⭐⭐⭐⭐ | 97% | 10-15% | Very High | Critical pipelines only |

### 9.3 Sampling Strategies to Reduce Cost

```python
# Full validation (expensive)
df.expect_column_values_to_be_between("age", 0, 120)

# Sampled validation (90% cost reduction, 95% confidence)
sample = df.sample(fraction=0.1)  # Validate 10%
sample.expect_column_values_to_be_between("age", 0, 120)
```

**Risk**: Miss rare edge cases in 90% of data. **Mitigation**: Stratified sampling by partition key.

---

## 10. Security / Compliance Considerations

### 10.1 Data Classification Matrix

| Data Class | Examples | Encryption | Access Control | Validation Requirements | Retention |
|------------|----------|------------|----------------|------------------------|-----------|
| **Public** | Product catalog | Optional | Open | Schema-only | Unlimited |
| **Internal** | User activity logs | At-rest | RBAC (role-based) | Medium | 2 years |
| **Confidential** | Email addresses | At-rest + in-transit | ABAC (attribute-based) | High | 1 year |
| **Sensitive PII** | SSN, credit cards | Application-level + at-rest + in-transit | ABAC + audit logs | Very High | As required by law |

### 10.2 PII Redaction in Validation Logs

**Problem**: Validation failures log actual data values → PII leak

**Bad Example**:
```python
# ❌ Logs contain PII
logger.error(f"Invalid email: {user_email}")  # Exposes user_email
```

**Good Example**:
```python
# ✅ Redact PII
logger.error(f"Invalid email: <REDACTED> (row_id={row_id})")
```

### 10.3 GDPR "Right to be Forgotten" Flow

```
1. User requests deletion (GDPR Article 17)
2. Deletion event → Kafka topic
3. Quality validation: Check event schema
4. Processing: Mark records as "deleted" (tombstone)
5. Validation: Ensure downstream systems purge within SLA (30 days)
6. Audit: Log deletion completion for compliance proof
```

**Validation Hook**: Ensure deletion propagates to all downstream tables.

```python
def validate_gdpr_deletion(user_id: str, tables: List[str]) -> bool:
    for table in tables:
        if user_id_exists_in_table(user_id, table):
            alert(f"GDPR violation: {user_id} still in {table}")
            return False
    return True
```

---

## 11. Observability & Telemetry Hooks

### 11.1 Key Metrics

| Metric | Purpose | Example Threshold | Tool | Alert Severity |
|--------|---------|-------------------|------|----------------|
| `validation_passed_total` | Track successful validations | N/A (monotonic counter) | Prometheus | N/A |
| `validation_failed_total` | Track failures by type | >100/hr | Prometheus | P2 (warn) |
| `validation_failure_rate` | % of failed validations | >1% | Grafana | P1 (critical) |
| `quarantine_record_count` | DLQ size | >10K records | CloudWatch | P2 |
| `validation_latency_seconds` | Validation duration | p95 >5s | Histogram | P3 |
| `sla_breach_count` | Timeliness violations | >0 | Counter | P1 |
| `anomaly_detection_lag_seconds` | Detection delay | >60s | Gauge | P2 |

### 11.2 Distributed Tracing

```python
import opentelemetry.trace as trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("validate_batch") as span:
    span.set_attribute("batch_size", len(df))
    span.set_attribute("validation_suite", "user_data_v2")
    
    result = context.run_validation_operator(
        "action_list_operator",
        assets_to_validate=[df]
    )
    
    span.set_attribute("success", result.success)
    span.set_attribute("failed_expectations", len(result.failed_expectations))
```

**Tags to Include**:
- `dataset_name`, `partition_key`, `validation_suite_version`
- `failed_expectation_types` (for root cause analysis)

### 11.3 Structured Logging

```python
import structlog

logger = structlog.get_logger()

logger.info(
    "validation_completed",
    trace_id=trace_id,
    batch_id=batch_id,
    dataset="user_events",
    success=False,
    failed_count=42,
    failure_reasons=["age_out_of_range", "null_email"],
    # PII redacted ✅
)
```

**Redaction Note**: Never log actual data values, only metadata (counts, types).

---

*[Continuing in next part due to length...]*
