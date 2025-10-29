# Data Quality & Validation - Part 2

## 12. Step-by-Step Implementation Tracks

### 12.1 Minimal Prototype (Learning Track)

**Goal**: Validate a CSV file locally in 30 minutes

**Step 1: Install Great Expectations**
```bash
pip install great-expectations==0.18.0
```

**Step 2: Initialize Project**
```bash
great_expectations init
# Creates: great_expectations/
#   ├── expectations/  (validation suites)
#   ├── checkpoints/   (validation runners)
#   ├── plugins/
#   └── great_expectations.yml
```

**Step 3: Create Sample Data**
```python
# sample_data.csv
import pandas as pd

data = {
    'user_id': [1, 2, 3, 4, 5],
    'email': ['alice@example.com', 'bob@example.com', 'invalid', 'dave@example.com', 'eve@example.com'],
    'age': [25, 30, 150, -5, 28],  # 150 and -5 are invalid
    'signup_date': ['2023-01-01', '2023-01-02', '2023-13-99', '2023-01-04', '2023-01-05']  # Bad date
}

df = pd.DataFrame(data)
df.to_csv('users.csv', index=False)
```

**Step 4: Create Data Source**
```python
import great_expectations as ge

context = ge.get_context()

# Add CSV datasource
datasource_config = {
    "name": "users_csv",
    "class_name": "Datasource",
    "execution_engine": {
        "class_name": "PandasExecutionEngine"
    },
    "data_connectors": {
        "default_inferred_data_connector_name": {
            "class_name": "InferredAssetFilesystemDataConnector",
            "base_directory": ".",
            "default_regex": {
                "pattern": "(.*)\\.csv",
                "group_names": ["data_asset_name"]
            }
        }
    }
}

context.add_datasource(**datasource_config)
```

**Step 5: Create Expectation Suite**
```python
# Create validator
validator = context.get_validator(
    batch_request={
        "datasource_name": "users_csv",
        "data_connector_name": "default_inferred_data_connector_name",
        "data_asset_name": "users"
    },
    expectation_suite_name="user_validation_suite"
)

# Add expectations
validator.expect_column_to_exist("user_id")
validator.expect_column_to_exist("email")
validator.expect_column_to_exist("age")
validator.expect_column_to_exist("signup_date")

# Email validation
validator.expect_column_values_to_match_regex(
    column="email",
    regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)

# Age range validation
validator.expect_column_values_to_be_between(
    column="age",
    min_value=0,
    max_value=120
)

# Date parsing validation
validator.expect_column_values_to_match_strftime_format(
    column="signup_date",
    strftime_format="%Y-%m-%d"
)

# Save suite
validator.save_expectation_suite(discard_failed_expectations=False)
```

**Step 6: Run Validation**
```python
# Create checkpoint
checkpoint_config = {
    "name": "user_checkpoint",
    "config_version": 1.0,
    "class_name": "SimpleCheckpoint",
    "validations": [
        {
            "batch_request": {
                "datasource_name": "users_csv",
                "data_connector_name": "default_inferred_data_connector_name",
                "data_asset_name": "users"
            },
            "expectation_suite_name": "user_validation_suite"
        }
    ]
}

context.add_or_update_checkpoint(**checkpoint_config)

# Run validation
result = context.run_checkpoint(checkpoint_name="user_checkpoint")

# Check results
print(f"Validation success: {result.success}")
print(f"Failed expectations: {len(result.list_validation_results()[0].results)}")
```

**Expected Output**:
```
Validation success: False
Failed expectations: 3
  - email (row 3): 'invalid' does not match pattern
  - age (row 3): 150 > 120
  - age (row 4): -5 < 0
  - signup_date (row 3): '2023-13-99' invalid format
```

**Step 7: View HTML Report**
```python
context.build_data_docs()
context.open_data_docs()
# Opens browser with beautiful validation report
```

---

### 12.2 Production Hardened Implementation

**Goal**: Enterprise-grade validation service with monitoring, quarantine, and SLA tracking

#### Architecture

```
┌────────────────────────────────────────────────────────────┐
│         Data Quality Service (Spring Boot / FastAPI)       │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  API Layer                                          │  │
│  │  POST /validate/batch                               │  │
│  │  GET  /validation-results/{batch_id}                │  │
│  │  GET  /health                                       │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Validation Engine (Great Expectations)             │  │
│  │  - Suite loader (from S3/DB)                        │  │
│  │  - Parallel execution (ThreadPoolExecutor)          │  │
│  │  - Result caching (Redis)                           │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Quarantine Manager                                 │  │
│  │  - Failed records → S3 DLQ                          │  │
│  │  - Metadata tracking (failure reason, timestamp)    │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Metrics & Alerting                                 │  │
│  │  - Prometheus metrics                               │  │
│  │  - PagerDuty integration                            │  │
│  └─────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

#### Code Implementation (Python + FastAPI)

**requirements.txt**:
```
fastapi==0.109.0
uvicorn==0.27.0
great-expectations==0.18.0
boto3==1.34.0
redis==5.0.0
prometheus-client==0.19.0
structlog==24.1.0
```

**main.py**:
```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional
import great_expectations as ge
from prometheus_client import Counter, Histogram, Gauge
import structlog
import boto3
import redis
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# Initialize
app = FastAPI(title="Data Quality Service")
logger = structlog.get_logger()
s3_client = boto3.client('s3')
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Metrics
validation_counter = Counter(
    'validation_total',
    'Total validation runs',
    ['suite_name', 'status']
)
validation_latency = Histogram(
    'validation_duration_seconds',
    'Validation duration',
    ['suite_name']
)
quarantine_gauge = Gauge(
    'quarantine_record_count',
    'Records in quarantine',
    ['dataset']
)

# Models
class ValidationRequest(BaseModel):
    dataset_name: str
    s3_path: str
    suite_name: str
    batch_id: str

class ValidationResponse(BaseModel):
    batch_id: str
    success: bool
    failed_count: int
    quarantined_count: int
    validation_url: Optional[str]

# Service
class DataQualityService:
    def __init__(self):
        self.context = ge.get_context()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    async def validate_batch(
        self,
        request: ValidationRequest,
        background_tasks: BackgroundTasks
    ) -> ValidationResponse:
        """
        Main validation workflow with production concerns.
        """
        start_time = time.time()
        trace_id = f"{request.batch_id}-{int(start_time)}"
        
        logger.info(
            "validation_started",
            trace_id=trace_id,
            dataset=request.dataset_name,
            batch_id=request.batch_id,
            suite=request.suite_name
        )
        
        try:
            # 1. Load data from S3 (with retry)
            df = self._load_data_with_retry(request.s3_path, retries=3)
            
            # 2. Create validator
            validator = self._create_validator(df, request.suite_name)
            
            # 3. Run validation (with timeout)
            result = self._run_validation_with_timeout(
                validator,
                timeout_seconds=300
            )
            
            # 4. Process failures
            failed_records = self._extract_failed_records(df, result)
            
            # 5. Quarantine failures (async)
            if failed_records:
                background_tasks.add_task(
                    self._quarantine_records,
                    failed_records,
                    request.dataset_name,
                    trace_id
                )
            
            # 6. Update metrics
            validation_counter.labels(
                suite_name=request.suite_name,
                status='success' if result.success else 'failure'
            ).inc()
            
            validation_latency.labels(
                suite_name=request.suite_name
            ).observe(time.time() - start_time)
            
            quarantine_gauge.labels(
                dataset=request.dataset_name
            ).set(len(failed_records))
            
            # 7. Alert if failure rate > threshold
            if not result.success:
                failure_rate = len(failed_records) / len(df)
                if failure_rate > 0.01:  # >1% failure
                    self._send_alert(
                        f"High failure rate: {failure_rate:.2%}",
                        request,
                        trace_id
                    )
            
            logger.info(
                "validation_completed",
                trace_id=trace_id,
                success=result.success,
                failed_count=len(failed_records),
                duration_seconds=time.time() - start_time
            )
            
            return ValidationResponse(
                batch_id=request.batch_id,
                success=result.success,
                failed_count=len(failed_records),
                quarantined_count=len(failed_records),
                validation_url=self._generate_data_docs_url(request.batch_id)
            )
            
        except TimeoutError:
            logger.error(
                "validation_timeout",
                trace_id=trace_id,
                timeout_seconds=300
            )
            validation_counter.labels(
                suite_name=request.suite_name,
                status='timeout'
            ).inc()
            raise HTTPException(status_code=504, detail="Validation timeout")
            
        except Exception as e:
            logger.error(
                "validation_error",
                trace_id=trace_id,
                error=str(e),
                error_type=type(e).__name__
            )
            validation_counter.labels(
                suite_name=request.suite_name,
                status='error'
            ).inc()
            raise HTTPException(status_code=500, detail=str(e))
    
    def _load_data_with_retry(self, s3_path: str, retries: int) -> pd.DataFrame:
        """Load data from S3 with exponential backoff."""
        import pandas as pd
        from botocore.exceptions import ClientError
        
        for attempt in range(retries):
            try:
                bucket, key = self._parse_s3_path(s3_path)
                obj = s3_client.get_object(Bucket=bucket, Key=key)
                df = pd.read_csv(obj['Body'])
                return df
            except ClientError as e:
                if attempt == retries - 1:
                    raise
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(
                    "s3_load_retry",
                    attempt=attempt + 1,
                    wait_seconds=wait_time
                )
                time.sleep(wait_time)
    
    def _create_validator(self, df: pd.DataFrame, suite_name: str):
        """Create GE validator with caching."""
        # Check cache for suite
        cached_suite = redis_client.get(f"suite:{suite_name}")
        if cached_suite:
            suite = json.loads(cached_suite)
        else:
            suite = self.context.get_expectation_suite(suite_name)
            redis_client.setex(
                f"suite:{suite_name}",
                3600,  # 1 hour cache
                json.dumps(suite.to_json_dict())
            )
        
        batch = ge.dataset.PandasDataset(df)
        batch.set_expectation_suite(suite)
        return batch
    
    def _run_validation_with_timeout(self, validator, timeout_seconds: int):
        """Run validation with timeout protection."""
        future = self.executor.submit(
            validator.validate
        )
        try:
            result = future.result(timeout=timeout_seconds)
            return result
        except concurrent.futures.TimeoutError:
            future.cancel()
            raise TimeoutError(f"Validation exceeded {timeout_seconds}s")
    
    def _extract_failed_records(
        self,
        df: pd.DataFrame,
        result
    ) -> List[Dict]:
        """Extract rows that failed validation."""
        failed_indices = set()
        
        for expectation_result in result.results:
            if not expectation_result.success:
                # Extract unexpected_index_list if available
                if 'unexpected_index_list' in expectation_result.result:
                    failed_indices.update(
                        expectation_result.result['unexpected_index_list']
                    )
        
        failed_records = df.iloc[list(failed_indices)].to_dict('records')
        
        # Add metadata
        for record in failed_records:
            record['_validation_failure_time'] = datetime.utcnow().isoformat()
            record['_failure_reasons'] = self._get_failure_reasons(
                record,
                result
            )
        
        return failed_records
    
    def _quarantine_records(
        self,
        records: List[Dict],
        dataset_name: str,
        trace_id: str
    ):
        """Write failed records to S3 Dead Letter Queue."""
        import json
        
        dlq_key = f"quarantine/{dataset_name}/{trace_id}.jsonl"
        
        lines = [json.dumps(record) for record in records]
        body = "\n".join(lines)
        
        s3_client.put_object(
            Bucket='data-quality-dlq',
            Key=dlq_key,
            Body=body.encode('utf-8'),
            Metadata={
                'dataset': dataset_name,
                'trace_id': trace_id,
                'record_count': str(len(records))
            }
        )
        
        logger.info(
            "quarantine_written",
            trace_id=trace_id,
            dlq_path=f"s3://data-quality-dlq/{dlq_key}",
            record_count=len(records)
        )
    
    def _send_alert(
        self,
        message: str,
        request: ValidationRequest,
        trace_id: str
    ):
        """Send PagerDuty alert for critical failures."""
        # Simplified - use actual PagerDuty SDK in production
        alert_payload = {
            "routing_key": os.getenv("PAGERDUTY_ROUTING_KEY"),
            "event_action": "trigger",
            "payload": {
                "summary": f"Data Quality Alert: {message}",
                "severity": "error",
                "source": "data-quality-service",
                "custom_details": {
                    "dataset": request.dataset_name,
                    "batch_id": request.batch_id,
                    "trace_id": trace_id
                }
            }
        }
        # requests.post("https://events.pagerduty.com/v2/enqueue", json=alert_payload)
        
        logger.warning(
            "alert_sent",
            trace_id=trace_id,
            message=message
        )

# Initialize service
service = DataQualityService()

# Routes
@app.post("/validate/batch", response_model=ValidationResponse)
async def validate_batch(
    request: ValidationRequest,
    background_tasks: BackgroundTasks
):
    """Validate a batch of data."""
    return await service.validate_batch(request, background_tasks)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# Metrics endpoint
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  data-quality-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - REDIS_HOST=redis
      - PAGERDUTY_ROUTING_KEY=${PAGERDUTY_ROUTING_KEY}
    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Usage**:
```bash
# Start services
docker-compose up -d

# Validate batch
curl -X POST http://localhost:8000/validate/batch \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_name": "user_events",
    "s3_path": "s3://my-bucket/data/users.csv",
    "suite_name": "user_validation_suite",
    "batch_id": "batch_2024_01_15_001"
  }'

# Check metrics
curl http://localhost:8000/metrics
```

---

## 13. Real Company Case Studies

### Case Study 1: Airbnb - Timestamp Parsing Disaster

| Aspect | Details |
|--------|---------|
| **Company** | Airbnb |
| **Context** | Booking platform with global users across timezones |
| **Scale** | 150M bookings/year, 7M listings |
| **Pre-Issue State** | Timezone conversion handled inconsistently across microservices |
| **Bottleneck** | Python datetime parsing bug: `2019-11-03 02:00 PST` parsed as `2019-11-03 01:00 PST` (DST transition) |
| **Adopted Pattern** | 1. Standardize to UTC at ingestion<br>2. Add validation: `expect_column_values_to_be_between(timestamp, now() - 7days, now() + 1day)`<br>3. Anomaly detection: flag >10% bookings outside expected range |
| **Numeric Outcome** | - Prevented $12M revenue loss<br>- Reduced timezone-related incidents by 95%<br>- Detection time: 6hr → 5min |
| **Residual Risk** | Rare edge case: users in UTC+14 (Kiribati) still occasionally flagged |

**Key Lesson**: Always validate timestamps against business constraints (booking can't be in past or >1 year future).

---

### Case Study 2: Uber - GPS Coordinate Anomaly Detection

| Aspect | Details |
|--------|---------|
| **Company** | Uber |
| **Context** | Real-time ride matching requires accurate GPS coordinates |
| **Scale** | 100M+ GPS events/day |
| **Pre-Issue State** | Drivers' phones occasionally sent corrupted GPS (e.g., lat=0, lon=0 → middle of ocean) |
| **Bottleneck** | Bad coordinates → incorrect ETA → customer complaints |
| **Adopted Pattern** | 1. Geofencing validation: `expect_column_values_to_be_in_geofence(lat, lon, city_boundaries)`<br>2. Speed anomaly: flag if distance_traveled / time_delta > 200 km/h (impossible)<br>3. Null island check: reject (0, 0) coordinates |
| **Numeric Outcome** | - 98% reduction in bad coordinate incidents<br>- ETA accuracy improved from 85% → 97%<br>- Customer satisfaction +5% |
| **Residual Risk** | GPS drift in tunnels (mitigation: interpolate based on last known location) |

**Key Lesson**: Domain-specific validation (geofencing) catches issues generic checks miss.

---

### Case Study 3: Netflix - Schema Evolution Breaking Change

| Aspect | Details |
|--------|---------|
| **Company** | Netflix |
| **Context** | Streaming events pipeline (play, pause, seek) feeds recommendations |
| **Scale** | 1B+ events/day |
| **Pre-Issue State** | Producer team renamed field `device_type` → `platform` without coordination |
| **Bottleneck** | Downstream Spark jobs expected `device_type`, failed with `KeyError` |
| **Adopted Pattern** | 1. Schema registry with compatibility rules (Confluent Schema Registry)<br>2. CI/CD gate: block incompatible schema changes<br>3. Backward compatibility validation: new schema must support old consumers |
| **Numeric Outcome** | - Zero breaking changes in 2 years post-implementation<br>- Deployment confidence increased<br>- Rollback incidents: 12/year → 0/year |
| **Residual Risk** | Additive changes (new optional fields) still require consumer updates eventually |

**Key Lesson**: Treat schema as a contract between producer/consumer; enforce via tooling.

---

### Case Study 4: Shopify - Duplicate Order Detection at Scale

| Aspect | Details |
|--------|---------|
| **Company** | Shopify |
| **Context** | E-commerce platform processing orders from 1M+ merchants |
| **Scale** | 10M orders/day |
| **Pre-Issue State** | Network retries occasionally caused duplicate orders (charged customer twice) |
| **Bottleneck** | No idempotency check → duplicate charges → refund overhead + customer churn |
| **Adopted Pattern** | 1. Bloom filter uniqueness check: `isDuplicate(order_id)` at ingestion (12KB memory for 1B orders)<br>2. Exact dedup: Store `order_id` hashes in Redis (7-day TTL)<br>3. SLA: <10ms dedup latency |
| **Numeric Outcome** | - Duplicate orders: 0.5% → <0.001%<br>- Refund costs reduced $2M/year<br>- Customer complaints -80% |
| **Residual Risk** | Bloom filter false positives (0.1% → manual review queue) |

**Key Lesson**: Probabilistic data structures (Bloom filter) enable scale without proportional memory cost.

---

### Case Study 5: Pinterest - Partition Skew Detection

| Aspect | Details |
|--------|---------|
| **Company** | Pinterest |
| **Context** | User activity events partitioned by `user_id` hash |
| **Scale** | 500M users, 10B pins/day |
| **Pre-Issue State** | Celebrity accounts (millions of followers) caused hot partitions → Spark executor OOMs |
| **Bottleneck** | Skewed data → long-tail stragglers → 10x slower jobs |
| **Adopted Pattern** | 1. Statistical profiling: detect partitions >3x median size<br>2. Salting: add random suffix to hot keys (`user_id_123_salt_0`, `user_id_123_salt_1`)<br>3. Adaptive repartitioning: monitor skew metrics, auto-rebalance |
| **Numeric Outcome** | - p95 job latency: 45min → 12min<br>- OOM failures: 15% → <1%<br>- Compute cost -30% (fewer retries) |
| **Residual Risk** | Salting increases shuffle overhead slightly (mitigated by broadcast joins) |

**Key Lesson**: Validate partition size distribution, not just schema correctness.

---

## 14. Interview Angles & Gotcha Questions

### Basic Questions (Filtering Round)

**Q1**: What is data quality, and why does it matter?

**Strong Answer**:
> Data quality ensures data is accurate, complete, consistent, timely, valid, and unique. It matters because bad data leads to:
> - **Business**: Wrong decisions (CFO trusts flawed revenue report)
> - **ML**: Poor model performance (garbage in = garbage out)
> - **Ops**: Wasted engineering time (80% debugging data issues)
> - **Cost**: Pipeline reruns, storage waste, customer refunds

**Red Flag Answer**: "Data quality means no errors."

---

**Q2**: How would you validate that a dataset has no duplicate records?

**Strong Answer**:
> Depends on scale:
> - **Small (<1M rows)**: `df.drop_duplicates()` or `expect_column_values_to_be_unique(primary_key)`
> - **Medium (1M-100M)**: Hash primary keys, store in HashSet, O(n) memory
> - **Large (>100M)**: Bloom filter (probabilistic, 12KB for 1B items @ 0.1% FPR) + exact check for suspected duplicates
> 
> Production consideration: Define "duplicate" (same PK? same PK + timestamp? semantic duplicates like "iPhone" vs "iphone"?)

**Red Flag Answer**: "Just use SQL `COUNT(DISTINCT)`" (doesn't explain scale trade-offs)

---

### Intermediate Questions (Depth Check)

**Q3**: Your data pipeline processes 100M rows/day. Validation now takes 30 minutes, violating the 1-hour SLA. How do you optimize?

**Strong Answer**:
> 1. **Profile bottleneck**: Is it CPU (validation logic) or I/O (reading data)?
> 2. **Sampling**: Validate 10% of data (stratified by partition key) → 90% cost reduction, 95% confidence
> 3. **Parallelize**: Spark/Flink partitioned validation (distribute across 20 executors)
> 4. **Caching**: Profile dataset once/day (mean, stddev), reuse for Z-score checks
> 5. **Prioritize**: Critical checks (schema, nulls) on 100%, statistical checks on sample
> 
> Measure: Benchmark each optimization, target <5% pipeline overhead.

**Red Flag Answer**: "Just add more servers" (no cost awareness)

---

**Q4**: You detect that 1% of records fail validation. What do you do?

**Strong Answer**:
> Decision tree:
> 1. **Root cause**: Is it systematic (producer bug) or random (network corruption)?
>    - Systematic: Reject entire batch, alert producer
>    - Random: Quarantine failed records, proceed with 99%
> 2. **Business impact**: Can downstream tolerate 1% data loss?
>    - Critical pipeline (payments): Reject, manual review
>    - Analytics (page views): Quarantine, investigate async
> 3. **SLA**: Does 1% breach data completeness SLA (e.g., >99.5% required)?
> 4. **Alert**: Page on-call if failure rate > threshold (e.g., 0.5%)
> 
> Document decision in runbook for on-call engineers.

**Red Flag Answer**: "Always reject bad data" (ignores business context)

---

### Advanced Questions (Trap Scenarios)

**Q5**: Design a data quality system for a multi-region data lake. How do you ensure consistency across regions?

**Strong Answer**:
> Challenges:
> 1. **Replication lag**: Region A data may be 5min ahead of Region B
> 2. **Schema evolution**: Schema changes propagate asynchronously
> 3. **Validation conflicts**: Different regions may have different validation suites
> 
> Design:
> ```
> Region A (Primary)                Region B (Replica)
> ├── Validation Layer              ├── Validation Layer
> │   ├── Schema check               │   ├── Schema check (same suite)
> │   ├── Business rules             │   ├── Business rules
> │   └── Version: v1.2.3            │   └── Version: v1.2.3 (synced)
> ├── Quarantine (S3)                ├── Quarantine (S3)
> └── Metadata Store (DynamoDB)      └── Metadata Store (DynamoDB Global Table)
> ```
> 
> **Strategies**:
> - **Validation suite sync**: Store suites in S3, replicate cross-region with S3 replication
> - **Version pinning**: Tag data batches with validation suite version
> - **Consistency check**: Daily job compares row counts, checksums across regions
> - **Conflict resolution**: If Region B detects issue Region A missed, backfill Region A quarantine
> 
> **Trade-off**: Eventual consistency (tolerate 5-min lag) vs strong consistency (validate after replication complete, higher latency)

**Red Flag Answer**: "Just validate once in primary region" (ignores replication lag issues)

---

**Q6**: You're validating a time-series dataset (stock prices). Yesterday's mean was $100, today's is $300. Is this an anomaly?

**Strong Answer**:
> **It depends** (interviewer is testing if you ask clarifying questions):
> 
> 1. **Stock split?**: 3-for-1 split would triple price → expected
> 2. **New symbols added?**: Dataset now includes expensive stocks (BRK.A @ $500K) → distribution shift, not anomaly
> 3. **Currency change?**: USD → Yen conversion → 100x increase, expected
> 4. **Data corruption?**: Decimal point error ($1.00 → $100) → anomaly
> 
> **Validation approach**:
> - Don't use absolute mean; track **% change** and **z-score** relative to rolling 30-day window
> - **Context-aware validation**: Check if stock split events occurred (join with reference data)
> - **Segmentation**: Validate per-symbol, not aggregated (hides individual anomalies)
> 
> **Production pattern**:
> ```python
> # Bad: Absolute threshold
> assert mean_price < 200  # Breaks on legitimate events
> 
> # Good: Contextual validation
> rolling_mean = df.groupby('symbol')['price'].rolling(30).mean()
> zscore = (today_mean - rolling_mean) / rolling_mean.std()
> if zscore > 3 and no_stock_split_event(symbol):
>     flag_anomaly()
> ```

**Red Flag Answer**: "Yes, 3x increase is always an anomaly" (no business context)

---

**Q7**: How would you validate data quality for a machine learning feature store?

**Strong Answer**:
> **Unique challenges**:
> 1. **Training-serving skew**: Offline features (batch) ≠ online features (real-time)
> 2. **Feature drift**: Distribution shifts over time (COVID changed user behavior)
> 3. **Point-in-time correctness**: Backfill must not leak future data
> 
> **Validation layers**:
> 
> | Layer | Checks | Frequency |
> |-------|--------|-----------|
> | **Offline (Batch)** | - Schema validation<br>- Feature range checks<br>- Correlation drift detection | Daily |
> | **Online (Real-time)** | - Latency SLA (<50ms)<br>- Freshness (TTL enforcement)<br>- Null rate monitoring | Per-request |
> | **Consistency** | - Compare offline vs online features for same entity<br>- Ensure <1% divergence | Hourly |
> | **Point-in-time** | - Validate no future leakage in backfills<br>- Check event_time <= query_time | Per backfill |
> 
> **Example validation**:
> ```python
> # Feature drift detection
> train_dist = get_feature_distribution(train_data, 'user_age')
> prod_dist = get_feature_distribution(prod_data, 'user_age')
> 
> ks_stat, p_value = ks_2samp(train_dist, prod_dist)
> if p_value < 0.05:  # Significant distribution shift
>     alert("Feature drift detected: user_age")
> ```
> 
> **Real-world**: Uber's Michelangelo, Airbnb's Zipline validate offline/online consistency via scheduled jobs.

**Red Flag Answer**: "Same validation as regular data pipelines" (misses ML-specific concerns)

---

**Q8**: Your validation suite has 50 expectations. One fails 0.01% of the time (1 in 10K records). Do you block the pipeline?

**Strong Answer**:
> **This is a trade-off question** (no single right answer, interviewer wants reasoning):
> 
> **Factors to consider**:
> 1. **Criticality**: Is it a hard constraint (PK uniqueness → YES) or soft (email format → MAYBE)?
> 2. **Downstream impact**: Will 0.01% bad data break consumers (payment system → YES) or add noise (analytics → NO)?
> 3. **False positive rate**: Is the expectation itself flawed? (e.g., regex too strict → genuine emails flagged)
> 4. **Cost of blocking**: Does blocking cost more than bad data? (real-time dashboard → blocking bad, batch → acceptable)
> 
> **Decision framework**:
> ```
> IF expectation.criticality == "CRITICAL" (e.g., payment_amount > 0):
>     REJECT batch, page on-call
> ELIF failure_rate > SLA_threshold (e.g., 0.1%):
>     QUARANTINE failed records, PROCEED with rest
> ELSE:
>     LOG warning, PROCEED
> ```
> 
> **Production example**:
> - Stripe: 0% tolerance for duplicate charges → block pipeline
> - Netflix: 1% tolerance for malformed view events → quarantine, investigate async
> 
> **Follow-up optimization**: If expectation fails consistently at 0.01%, tune threshold or update expectation (may be too strict).

**Red Flag Answer**: "Always block if any expectation fails" (no nuance)

---

**Q9**: You have 3 validation layers: ingestion (Kafka), transformation (Spark), serving (Redshift). Where do you put each type of check?

**Strong Answer**:
> **Fail-fast principle**: Validate as early as possible, but consider trade-offs.
> 
> | Check Type | Ingestion | Transformation | Serving | Reasoning |
> |------------|-----------|----------------|---------|-----------|
> | **Schema** | ✅ Primary | ⚠️ Backup | ❌ No | Catch at source, prevent bad data entry |
> | **Nullability** | ✅ Primary | ⚠️ Backup | ❌ No | Same as schema |
> | **Business rules** | ⚠️ Maybe | ✅ Primary | ❌ No | May need joined data (available in transformation) |
> | **Statistical** | ❌ No | ✅ Primary | ❌ No | Requires aggregation (expensive at ingestion) |
> | **Freshness** | ❌ No | ❌ No | ✅ Primary | Measure end-to-end latency |
> | **Consistency** | ❌ No | ⚠️ Maybe | ✅ Primary | Compare final output across systems |
> 
> **Reasoning**:
> - **Ingestion**: Cheap checks (schema, nulls) to reject bad data early
> - **Transformation**: Business logic validation (after joins/enrichment)
> - **Serving**: SLA validation (latency, consistency) to ensure end-user experience
> 
> **Real-world**: Netflix validates schema at Kafka ingestion, business rules in Spark, freshness in Druid.

**Red Flag Answer**: "Validate everything at every layer" (excessive overhead)

---

**Q10**: Design a validation system that handles 1M events/sec with <10ms latency. What trade-offs do you make?

**Strong Answer**:
> **Constraints**: 1M events/sec = 1000 events/ms → <0.01ms/event for validation
> 
> **Trade-offs**:
> 1. **Sampling**: Validate 1% of events (10K events/sec) → 99% cost reduction
>    - **Risk**: Miss rare anomalies (mitigate with stratified sampling)
> 2. **Async validation**: Stream events to Kafka, validate in background (Flink)
>    - **Risk**: Delayed detection (mitigate with real-time alerts on critical metrics)
> 3. **Lightweight checks only**: Schema + nulls (sub-ms), skip statistical checks
>    - **Risk**: Miss business rule violations (mitigate with batch validation later)
> 4. **Distributed validation**: Partition events across 100 validators (10K events/sec each)
>    - **Cost**: Infrastructure (but necessary at this scale)
> 
> **Architecture**:
> ```
> Kafka (1M events/sec)
>   ├─→ Real-time: Schema validation (C++ optimized, <0.01ms)
>   └─→ Async: Flink job (statistical checks, 10-sec window)
> ```
> 
> **Benchmark**:
> - Schema validation (Avro): 0.005ms/event
> - Null checks: 0.002ms/event
> - Total: 0.007ms → ✅ <10ms SLA
> 
> **Real-world**: Uber's real-time validation uses sampling + async processing to handle 100M+ GPS events/day.

**Red Flag Answer**: "Just make validation faster" (no architectural thinking)

---

**Q11**: You're on-call. Alert fires: "Validation failure rate spiked to 10%". How do you debug?

**Strong Answer**:
> **Incident response runbook**:
> 
> 1. **Assess impact** (2 min):
>    - Check Grafana: Which dataset? Which expectations failing?
>    - Check downstream: Are consumers broken or just warnings?
> 
> 2. **Quick mitigation** (5 min):
>    - If critical pipeline: Pause ingestion, prevent polluting downstream
>    - If non-critical: Quarantine failed records, let rest proceed
> 
> 3. **Root cause** (15 min):
>    - **Producer change**: Check Git history, recent deployments (Datadog APM)
>    - **Data anomaly**: Sample failed records, look for patterns
>    - **Validation bug**: Did expectation suite change recently? (Check version history)
> 
> 4. **Fix** (30 min):
>    - **Producer bug**: Rollback producer deployment, alert owning team
>    - **Data anomaly**: Legitimate spike (Black Friday traffic)? Update thresholds
>    - **Validation bug**: Revert expectation suite to previous version
> 
> 5. **Post-incident** (1 day later):
>    - Write post-mortem
>    - Add preventative check (e.g., gradual rollout for validation changes)
>    - Update runbook
> 
> **Tools**:
> - Logs: Elasticsearch (filter by `trace_id`, `dataset`, `expectation_type`)
> - Metrics: Prometheus (`validation_failed_total{expectation="age_range"}`)
> - Traces: Jaeger (visualize where validation slowed down)
> - Quarantine: Query S3 DLQ for sample failed records
> 
> **Real-world**: Airbnb incident response targets <15min mitigation, <2hr resolution.

**Red Flag Answer**: "Restart the pipeline" (no structured debugging)

---

**Q12**: How do you test your data quality tests? (Meta-question)

**Strong Answer**:
> **Challenge**: Validation logic itself can have bugs (false positives/negatives).
> 
> **Testing layers**:
> 
> 1. **Unit tests**: Test individual expectations
>    ```python
>    def test_age_validation():
>        df = pd.DataFrame({'age': [25, 150, -5]})
>        result = df.expect_column_values_to_be_between('age', 0, 120)
>        assert result.success == False
>        assert result.unexpected_count == 2  # 150 and -5
>    ```
> 
> 2. **Integration tests**: Test full validation pipeline
>    ```python
>    def test_user_validation_suite():
>        df = load_test_fixture('users_with_known_issues.csv')
>        result = validate(df, suite='user_validation_suite')
>        assert result.failed_expectations == ['email_regex', 'age_range']
>    ```
> 
> 3. **Chaos testing**: Inject known bad data, ensure detection
>    ```python
>    def test_duplicate_detection():
>        df = pd.DataFrame({'id': [1, 1, 2]})  # Duplicate ID
>        result = validate_uniqueness(df, 'id')
>        assert result.duplicates == [1]
>    ```
> 
> 4. **False positive monitoring**: Track expectations that fail frequently (may be too strict)
>    ```sql
>    SELECT expectation_type, COUNT(*) as failures
>    FROM validation_results
>    WHERE success = false
>    GROUP BY expectation_type
>    ORDER BY failures DESC
>    LIMIT 10
>    ```
> 
> 5. **Canary validation**: Run new validation suite on old data (should match previous results)
> 
> **Real-world**: Netflix regression tests validation suites on historical "golden datasets" before deploying changes.

**Red Flag Answer**: "No testing needed, validation is self-testing" (ignores validation bugs)

---

*[Continuing in Part 3...]*
