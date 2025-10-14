# Week 14: Orchestration (Airflow, Dagster, Prefect) — INTERMEDIATE Track

*"Dynamic DAG generation, sensors, and branching separate junior engineers from senior ones. Master these patterns and you'll design production pipelines that scale."* — Senior Engineer, Netflix

---

## 🎯 Learning Outcomes

- Generate DAGs dynamically from config files
- Implement sensors for external dependencies
- Use branching for conditional logic
- Design SubDAGs and TaskGroups for modularity
- Create custom operators
- Handle failures with callbacks
- Implement data quality checks
- Optimize DAG performance

---

## 🔄 1. Dynamic DAG Generation

### Problem: Repetitive DAGs

```python
# Bad: Copy-paste for each customer
DAG(dag_id='process_customer_A', ...)
DAG(dag_id='process_customer_B', ...)
DAG(dag_id='process_customer_C', ...)
# ... 100 more customers ❌

# Problem:
# ├─ Hard to maintain (update 1 → update 100)
# ├─ Not scalable (add new customer → copy-paste code)
# └─ Error-prone (forget to update one DAG)
```

---

### Solution: Generate DAGs Programmatically

```python
# config.yaml
customers:
  - name: customer_A
    table: customers_a
    schedule: '0 2 * * *'
  - name: customer_B
    table: customers_b
    schedule: '0 3 * * *'
  - name: customer_C
    table: customers_c
    schedule: '0 4 * * *'
```

```python
# dags/dynamic_dags.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import yaml

# Load config
with open('/opt/airflow/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

def process_customer(customer_name, table_name):
    """Generic processing function"""
    def _process(**context):
        print(f"Processing {customer_name} from table {table_name}")
        # ... actual logic
    return _process

# Generate DAG for each customer
for customer in config['customers']:
    dag_id = f"process_{customer['name']}"
    
    with DAG(
        dag_id=dag_id,
        schedule_interval=customer['schedule'],
        start_date=datetime(2023, 10, 1),
        catchup=False,
        tags=['dynamic', customer['name']],
    ) as dag:
        
        task = PythonOperator(
            task_id=f"process_{customer['name']}",
            python_callable=process_customer(customer['name'], customer['table']),
        )
        
        # Register DAG in Airflow globals
        globals()[dag_id] = dag

# Result: 3 DAGs created automatically ✅
# ├─ process_customer_A (runs at 2am)
# ├─ process_customer_B (runs at 3am)
# └─ process_customer_C (runs at 4am)
```

---

### Advanced: Generate from Database

```python
# dags/db_dynamic_dags.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import psycopg2

def get_customers_from_db():
    """Fetch customer list from database"""
    conn = psycopg2.connect("host=postgres dbname=metadata")
    cur = conn.cursor()
    cur.execute("SELECT customer_id, table_name, schedule FROM customers WHERE active = true")
    customers = cur.fetchall()
    conn.close()
    return customers

# Generate DAGs
for customer_id, table_name, schedule in get_customers_from_db():
    dag_id = f"process_customer_{customer_id}"
    
    with DAG(
        dag_id=dag_id,
        schedule_interval=schedule,
        start_date=datetime(2023, 10, 1),
        catchup=False,
    ) as dag:
        
        task = PythonOperator(
            task_id=f"process_{customer_id}",
            python_callable=lambda: print(f"Processing {table_name}"),
        )
        
        globals()[dag_id] = dag
```

---

## 👁️ 2. Sensors

### What are Sensors?

```
Sensor = Operator that waits for a condition to be true

Use cases:
├─ Wait for file to appear in S3
├─ Wait for database table to be ready
├─ Wait for external API to return success
└─ Wait for another DAG to complete

Behavior:
1. Sensor checks condition (poke)
2. If True → Succeed, downstream tasks run
3. If False → Wait, check again (poke_interval)
4. If timeout → Fail
```

---

### FileSensor

```python
from airflow.sensors.filesystem import FileSensor
from airflow.operators.python import PythonOperator

def process_file(**context):
    print("File found! Processing...")
    # ... process /data/input.csv

with DAG('wait_for_file', start_date=datetime(2023, 10, 1)) as dag:
    
    # Wait for file to appear
    wait_for_file = FileSensor(
        task_id='wait_for_input_file',
        filepath='/data/input.csv',
        fs_conn_id='fs_default',  # File system connection
        poke_interval=30,  # Check every 30 seconds
        timeout=600,  # Fail after 10 minutes
        mode='poke',  # 'poke' (blocking) or 'reschedule' (non-blocking)
    )
    
    process = PythonOperator(
        task_id='process_file',
        python_callable=process_file,
    )
    
    wait_for_file >> process

# Execution:
# 1. wait_for_file checks every 30 seconds
# 2. Once file exists → Succeed
# 3. process runs
```

---

### S3KeySensor

```python
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor

wait_for_s3 = S3KeySensor(
    task_id='wait_for_s3_file',
    bucket_name='my-bucket',
    bucket_key='data/input-{{ ds }}.csv',  # Templated (2023-10-15)
    aws_conn_id='aws_default',
    poke_interval=60,  # Check every 1 minute
    timeout=3600,  # Fail after 1 hour
)
```

---

### ExternalTaskSensor

```python
from airflow.sensors.external_task import ExternalTaskSensor

# DAG 1: Upstream pipeline
with DAG('upstream_pipeline', schedule_interval='@daily') as dag1:
    task_a = BashOperator(task_id='task_a', bash_command='echo "Upstream"')

# DAG 2: Downstream pipeline (waits for DAG 1)
with DAG('downstream_pipeline', schedule_interval='@daily') as dag2:
    
    # Wait for upstream DAG to complete
    wait_for_upstream = ExternalTaskSensor(
        task_id='wait_for_upstream',
        external_dag_id='upstream_pipeline',
        external_task_id='task_a',  # Wait for specific task (None = wait for DAG)
        poke_interval=60,
        timeout=3600,
    )
    
    task_b = BashOperator(task_id='task_b', bash_command='echo "Downstream"')
    
    wait_for_upstream >> task_b

# Execution:
# Day 1:
# ├─ upstream_pipeline runs at midnight
# ├─ task_a completes at 00:05
# ├─ downstream_pipeline starts at midnight
# ├─ wait_for_upstream checks every 60 seconds
# ├─ At 00:05: Upstream complete → wait_for_upstream succeeds
# └─ task_b runs
```

---

### Custom Sensor

```python
from airflow.sensors.base import BaseSensorOperator
from airflow.utils.decorators import apply_defaults
import requests

class ApiSensor(BaseSensorOperator):
    """Wait for API to return status=ready"""
    
    @apply_defaults
    def __init__(self, api_url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_url = api_url
    
    def poke(self, context):
        """Called every poke_interval seconds"""
        response = requests.get(self.api_url)
        data = response.json()
        
        if data['status'] == 'ready':
            self.log.info("API is ready!")
            return True  # Succeed
        else:
            self.log.info(f"API not ready: {data['status']}")
            return False  # Keep waiting

# Usage:
wait_for_api = ApiSensor(
    task_id='wait_for_api',
    api_url='https://api.example.com/status',
    poke_interval=30,
    timeout=600,
)
```

---

## 🔀 3. Branching (Conditional Logic)

### BranchPythonOperator

```python
from airflow.operators.python import BranchPythonOperator
from airflow.operators.bash import BashOperator

def decide_branch(**context):
    """Decide which branch to take"""
    execution_date = context['execution_date']
    
    # If weekend → run weekend_task
    if execution_date.weekday() in [5, 6]:  # Saturday=5, Sunday=6
        return 'weekend_task'
    else:
        return 'weekday_task'

with DAG('branching_example', start_date=datetime(2023, 10, 1)) as dag:
    
    start = BashOperator(task_id='start', bash_command='echo "Start"')
    
    branch = BranchPythonOperator(
        task_id='decide_branch',
        python_callable=decide_branch,
    )
    
    weekday_task = BashOperator(
        task_id='weekday_task',
        bash_command='echo "Running weekday processing"',
    )
    
    weekend_task = BashOperator(
        task_id='weekend_task',
        bash_command='echo "Running weekend processing"',
    )
    
    end = BashOperator(
        task_id='end',
        bash_command='echo "End"',
        trigger_rule='none_failed_or_skipped',  # Run even if branch skipped
    )
    
    start >> branch >> [weekday_task, weekend_task] >> end

# Execution (Monday):
# ├─ start runs
# ├─ branch runs → Returns 'weekday_task'
# ├─ weekday_task runs ✅
# ├─ weekend_task skipped ⏭️
# └─ end runs (trigger_rule allows skipped tasks)
```

---

### Multiple Conditions

```python
def advanced_branching(**context):
    """Branch based on multiple conditions"""
    ti = context['ti']
    execution_date = context['execution_date']
    
    # Pull data from previous task
    record_count = ti.xcom_pull(task_ids='extract_data')
    
    # Branch logic
    if record_count == 0:
        return 'skip_pipeline'  # No data to process
    elif record_count < 1000:
        return 'quick_process'  # Small dataset
    else:
        return 'full_process'  # Large dataset

branch = BranchPythonOperator(
    task_id='branch',
    python_callable=advanced_branching,
)

skip_pipeline = BashOperator(task_id='skip_pipeline', bash_command='echo "No data"')
quick_process = BashOperator(task_id='quick_process', bash_command='python quick.py')
full_process = BashOperator(task_id='full_process', bash_command='python full.py')

branch >> [skip_pipeline, quick_process, full_process]
```

---

## 📦 4. TaskGroups (SubDAGs Replacement)

### Problem: Complex DAGs are Hard to Read

```python
# 20 tasks in single DAG
task_1 >> task_2 >> task_3 >> task_4 >> task_5 >> task_6 >> ...
# Visualization: Messy spaghetti ❌
```

---

### Solution: TaskGroups

```python
from airflow.utils.task_group import TaskGroup

with DAG('etl_with_taskgroups', start_date=datetime(2023, 10, 1)) as dag:
    
    start = BashOperator(task_id='start', bash_command='echo "Start"')
    
    # Group 1: Extract
    with TaskGroup('extract_group') as extract:
        extract_db = BashOperator(task_id='extract_db', bash_command='python extract_db.py')
        extract_api = BashOperator(task_id='extract_api', bash_command='python extract_api.py')
        extract_files = BashOperator(task_id='extract_files', bash_command='python extract_files.py')
        
        # Dependencies within group
        [extract_db, extract_api, extract_files]
    
    # Group 2: Transform
    with TaskGroup('transform_group') as transform:
        clean = BashOperator(task_id='clean', bash_command='python clean.py')
        validate = BashOperator(task_id='validate', bash_command='python validate.py')
        aggregate = BashOperator(task_id='aggregate', bash_command='python aggregate.py')
        
        clean >> validate >> aggregate
    
    # Group 3: Load
    with TaskGroup('load_group') as load:
        load_warehouse = BashOperator(task_id='load_warehouse', bash_command='python load_warehouse.py')
        load_cache = BashOperator(task_id='load_cache', bash_command='python load_cache.py')
        
        [load_warehouse, load_cache]
    
    end = BashOperator(task_id='end', bash_command='echo "End"')
    
    # Dependencies between groups
    start >> extract >> transform >> load >> end

# Visualization:
# start ──> [extract_group] ──> [transform_group] ──> [load_group] ──> end
#            ├─ extract_db       ├─ clean              ├─ load_warehouse
#            ├─ extract_api      ├─ validate           └─ load_cache
#            └─ extract_files    └─ aggregate

# Benefits:
# ├─ Clean visualization (collapsed groups)
# ├─ Reusable groups
# └─ Better organization
```

---

### Nested TaskGroups

```python
with DAG('nested_taskgroups', start_date=datetime(2023, 10, 1)) as dag:
    
    with TaskGroup('processing') as processing:
        
        # Nested group: Data quality
        with TaskGroup('data_quality') as dq:
            check_nulls = BashOperator(task_id='check_nulls', bash_command='python check_nulls.py')
            check_duplicates = BashOperator(task_id='check_duplicates', bash_command='python check_duplicates.py')
            check_nulls >> check_duplicates
        
        # Nested group: Transformations
        with TaskGroup('transformations') as tf:
            transform_a = BashOperator(task_id='transform_a', bash_command='python transform_a.py')
            transform_b = BashOperator(task_id='transform_b', bash_command='python transform_b.py')
            [transform_a, transform_b]
        
        dq >> tf

# Visualization:
# processing
# ├─ data_quality
# │  ├─ check_nulls
# │  └─ check_duplicates
# └─ transformations
#    ├─ transform_a
#    └─ transform_b
```

---

## 🛠️ 5. Custom Operators

### Why Custom Operators?

```
Use cases:
├─ Reusable logic (avoid copy-paste)
├─ Encapsulate complex logic
├─ Integrate with custom systems
└─ Standardize team practices
```

---

### Example: PostgresUpsertOperator

```python
from airflow.models import BaseOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.decorators import apply_defaults

class PostgresUpsertOperator(BaseOperator):
    """Upsert data into PostgreSQL"""
    
    template_fields = ['sql']  # Allow Jinja templating
    
    @apply_defaults
    def __init__(
        self,
        table,
        records,
        conflict_columns,
        postgres_conn_id='postgres_default',
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.table = table
        self.records = records
        self.conflict_columns = conflict_columns
        self.postgres_conn_id = postgres_conn_id
    
    def execute(self, context):
        """Execute upsert"""
        hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        conn = hook.get_conn()
        cur = conn.cursor()
        
        # Build upsert SQL
        columns = ', '.join(self.records[0].keys())
        values_placeholder = ', '.join(['%s'] * len(self.records[0]))
        conflict_cols = ', '.join(self.conflict_columns)
        
        sql = f"""
            INSERT INTO {self.table} ({columns})
            VALUES ({values_placeholder})
            ON CONFLICT ({conflict_cols})
            DO UPDATE SET {', '.join([f"{k}=EXCLUDED.{k}" for k in self.records[0].keys()])}
        """
        
        for record in self.records:
            cur.execute(sql, tuple(record.values()))
        
        conn.commit()
        self.log.info(f"Upserted {len(self.records)} records into {self.table}")

# Usage:
upsert_task = PostgresUpsertOperator(
    task_id='upsert_users',
    table='users',
    records=[
        {'user_id': 1, 'name': 'Alice', 'email': 'alice@example.com'},
        {'user_id': 2, 'name': 'Bob', 'email': 'bob@example.com'},
    ],
    conflict_columns=['user_id'],
    postgres_conn_id='postgres_default',
)
```

---

## 🚨 6. Error Handling and Callbacks

### On Failure Callback

```python
def notify_failure(context):
    """Send Slack notification on failure"""
    import requests
    
    task_instance = context['task_instance']
    dag_id = context['dag'].dag_id
    task_id = task_instance.task_id
    execution_date = context['execution_date']
    exception = context['exception']
    
    message = f"""
    ❌ Task Failed!
    DAG: {dag_id}
    Task: {task_id}
    Execution Date: {execution_date}
    Error: {exception}
    """
    
    requests.post(
        'https://hooks.slack.com/services/YOUR_WEBHOOK',
        json={'text': message}
    )

# Apply to specific task
task = PythonOperator(
    task_id='risky_task',
    python_callable=lambda: 1 / 0,  # Will fail
    on_failure_callback=notify_failure,
)

# Apply to all tasks in DAG
default_args = {
    'on_failure_callback': notify_failure,
}

with DAG('monitored_dag', default_args=default_args) as dag:
    # All tasks will call notify_failure on failure
    ...
```

---

### On Success Callback

```python
def log_success(context):
    """Log metrics on success"""
    import statsd
    
    task_instance = context['task_instance']
    duration = (task_instance.end_date - task_instance.start_date).total_seconds()
    
    # Send to monitoring system
    client = statsd.StatsClient('statsd-server', 8125)
    client.timing(f'airflow.{task_instance.dag_id}.{task_instance.task_id}', duration)
    
    print(f"Task {task_instance.task_id} completed in {duration}s")

task = PythonOperator(
    task_id='monitored_task',
    python_callable=lambda: print("Success!"),
    on_success_callback=log_success,
)
```

---

### Retry Logic

```python
default_args = {
    'retries': 3,  # Retry 3 times
    'retry_delay': timedelta(minutes=5),  # Wait 5 minutes between retries
    'retry_exponential_backoff': True,  # 5min, 10min, 20min
    'max_retry_delay': timedelta(hours=1),  # Max delay
}

task = PythonOperator(
    task_id='retry_task',
    python_callable=lambda: requests.get('https://flaky-api.com'),  # Might fail
    default_args=default_args,
)

# Execution:
# Attempt 1: Fail → Wait 5 minutes
# Attempt 2: Fail → Wait 10 minutes (exponential backoff)
# Attempt 3: Fail → Wait 20 minutes
# Attempt 4: Fail → Mark as failed (max retries reached)
```

---

## ✅ 7. Data Quality Checks

### Great Expectations Integration

```python
from airflow.operators.python import PythonOperator
import great_expectations as ge

def validate_data(**context):
    """Validate data quality with Great Expectations"""
    import pandas as pd
    
    # Load data
    df = pd.read_csv('/data/users.csv')
    
    # Convert to GE DataFrame
    ge_df = ge.from_pandas(df)
    
    # Define expectations
    results = []
    results.append(ge_df.expect_column_values_to_not_be_null('user_id'))
    results.append(ge_df.expect_column_values_to_be_unique('email'))
    results.append(ge_df.expect_column_values_to_be_between('age', 0, 120))
    
    # Check if all passed
    failed = [r for r in results if not r['success']]
    
    if failed:
        raise ValueError(f"Data quality checks failed: {failed}")
    else:
        print("All data quality checks passed ✅")

validate_task = PythonOperator(
    task_id='validate_data',
    python_callable=validate_data,
)

# If validation fails → Task fails → Downstream tasks skipped
```

---

### SQL Data Quality

```python
from airflow.providers.postgres.operators.postgres import PostgresOperator

# Check for duplicates
check_duplicates = PostgresOperator(
    task_id='check_duplicates',
    postgres_conn_id='postgres_default',
    sql="""
        SELECT COUNT(*) AS dup_count
        FROM (
            SELECT email, COUNT(*)
            FROM users
            GROUP BY email
            HAVING COUNT(*) > 1
        ) dups;
        
        -- Fail if duplicates found
        DO $$
        DECLARE dup_count INT;
        BEGIN
            SELECT COUNT(*) INTO dup_count
            FROM (SELECT email FROM users GROUP BY email HAVING COUNT(*) > 1) dups;
            
            IF dup_count > 0 THEN
                RAISE EXCEPTION 'Found % duplicate emails', dup_count;
            END IF;
        END $$;
    """,
)
```

---

## 🎓 Intermediate Exercises

### Exercise 1: Dynamic DAG with Branching

```python
"""
Create a DAG that:
1. Reads customer list from config file
2. For each customer:
   - Extract data
   - Branch based on data size:
     * <1000 rows → quick_transform
     * ≥1000 rows → full_transform
   - Load to warehouse
3. Send summary email
"""

# Your solution here!
```

---

### Exercise 2: Multi-Stage Pipeline with Sensors

```python
"""
Create a pipeline:
1. Wait for S3 file (S3KeySensor)
2. Extract from S3
3. Transform (TaskGroup):
   - Clean nulls
   - Validate schema
   - Aggregate
4. Data quality checks (fail if not pass)
5. Load to PostgreSQL (custom upsert operator)
6. Trigger downstream DAG (TriggerDagRunOperator)
"""

# Your solution here!
```

---

## 📚 Summary Checklist

- [ ] Generate DAGs dynamically from config/database
- [ ] Use sensors to wait for external dependencies
- [ ] Implement branching for conditional logic
- [ ] Organize complex DAGs with TaskGroups
- [ ] Create custom operators for reusable logic
- [ ] Handle failures with callbacks (Slack, email, metrics)
- [ ] Implement data quality checks (Great Expectations, SQL)
- [ ] Optimize DAG performance (parallelism, sensors)

**Next:** [EXPERT.md →](EXPERT.md)
