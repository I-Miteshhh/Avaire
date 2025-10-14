# Week 14: Orchestration (Airflow, Dagster, Prefect) — BEGINNER Track

*"Airflow isn't just a scheduler—it's the nervous system of your data platform. Understanding DAGs, operators, and XCom is essential for L4+ data engineers."* — Staff Engineer, Airbnb

---

## 🎯 Learning Outcomes

- Understand workflow orchestration fundamentals
- Master Apache Airflow DAG structure
- Implement task dependencies and scheduling
- Use operators (BashOperator, PythonOperator, etc.)
- Handle data passing with XCom
- Configure executors (SequentialExecutor, LocalExecutor)
- Debug failed tasks and view logs
- Design basic data pipelines with Airflow

---

## 🔷 1. Why Workflow Orchestration?

### The Problem: Manual Execution

```
Manual Data Pipeline (WITHOUT orchestration):

1. ssh data-server
2. python extract_data.py
3. Wait for completion... ⏳
4. python transform_data.py
5. Wait again... ⏳
6. python load_to_warehouse.py
7. Check for errors manually 🔍
8. If failed: Restart from scratch ❌

Problems:
├─ Manual intervention (not scalable)
├─ No dependency management (what runs first?)
├─ No retry logic (failures require manual restart)
├─ No monitoring (how do I know if it failed?)
└─ No scheduling (must run manually every day)
```

---

### The Solution: Workflow Orchestration

```
Orchestrated Pipeline (WITH Airflow):

DAG (Directed Acyclic Graph):
┌────────────┐
│ extract_   │
│ data       │
└─────┬──────┘
      │
      ▼
┌────────────┐
│ transform_ │
│ data       │
└─────┬──────┘
      │
      ▼
┌────────────┐
│ load_to_   │
│ warehouse  │
└────────────┘

Features:
├─ ✅ Automatic scheduling (runs daily at 2am)
├─ ✅ Dependency management (transform waits for extract)
├─ ✅ Retry logic (auto-retry 3 times on failure)
├─ ✅ Monitoring (email alerts on failure)
└─ ✅ Logging (view task logs in web UI)
```

---

## 🏗️ Airflow Architecture

```
┌──────────────────────────────────────────────────────────────┐
│ Airflow Components                                           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ 1. Web Server (Flask app):                                  │
│    ├─ UI for viewing DAGs, tasks, logs                      │
│    ├─ Runs on port 8080                                     │
│    └─ Access: http://localhost:8080                         │
│                                                              │
│ 2. Scheduler:                                               │
│    ├─ Reads DAG files (~/airflow/dags/)                     │
│    ├─ Schedules tasks based on cron expressions            │
│    ├─ Submits tasks to executor                            │
│    └─ Monitors task state (running, success, failed)       │
│                                                              │
│ 3. Executor:                                                │
│    ├─ Runs tasks (executes Python code)                     │
│    ├─ Types:                                                │
│    │  ├─ SequentialExecutor (1 task at a time, dev only)   │
│    │  ├─ LocalExecutor (parallel on single machine)        │
│    │  ├─ CeleryExecutor (distributed workers)              │
│    │  └─ KubernetesExecutor (each task = K8s pod)          │
│    └─ Reports task status back to scheduler                │
│                                                              │
│ 4. Metadata Database (PostgreSQL/MySQL):                    │
│    ├─ Stores DAG state, task history, logs                  │
│    ├─ Example: "Task extract_data ran at 2023-10-15 02:00" │
│    └─ Queried by web server and scheduler                  │
│                                                              │
│ 5. DAG Files (Python scripts):                              │
│    ├─ Location: ~/airflow/dags/                            │
│    ├─ Define workflow logic (tasks, dependencies)          │
│    └─ Parsed by scheduler every 30 seconds                 │
└──────────────────────────────────────────────────────────────┘

Workflow:
1. User writes DAG file → ~/airflow/dags/my_pipeline.py
2. Scheduler reads DAG → Parses tasks and dependencies
3. Scheduler submits task to executor → "Run extract_data"
4. Executor runs task → Executes Python function
5. Task completes → Executor reports "success" to scheduler
6. Scheduler schedules next task → "Run transform_data"
7. Web server displays status → User views in UI
```

---

## 📝 Your First DAG

### Hello World Example

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Default arguments (applied to all tasks)
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['alerts@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# Define DAG
with DAG(
    dag_id='hello_world',
    default_args=default_args,
    description='My first Airflow DAG',
    schedule_interval='@daily',  # Run every day at midnight
    start_date=datetime(2023, 10, 1),
    catchup=False,  # Don't backfill past dates
    tags=['example'],
) as dag:

    # Task 1: Print hello
    task_hello = BashOperator(
        task_id='say_hello',
        bash_command='echo "Hello from Airflow!"',
    )

    # Task 2: Print date
    task_date = BashOperator(
        task_id='print_date',
        bash_command='date',
    )

    # Task 3: Sleep
    task_sleep = BashOperator(
        task_id='sleep_5_seconds',
        bash_command='sleep 5',
    )

    # Define dependencies
    task_hello >> task_date >> task_sleep
    # Equivalent to:
    # task_hello.set_downstream(task_date)
    # task_date.set_downstream(task_sleep)
```

**DAG Visualization:**

```
say_hello ──> print_date ──> sleep_5_seconds

Execution Flow:
1. say_hello runs → "Hello from Airflow!"
2. print_date runs → "Sat Oct 15 02:00:00 UTC 2023"
3. sleep_5_seconds runs → Sleeps for 5 seconds
4. DAG succeeds ✅
```

---

### DAG Parameters Explained

```python
DAG(
    dag_id='hello_world',  # Unique identifier (must be unique across all DAGs)
    
    default_args={...},  # Default args for all tasks (retries, owner, etc.)
    
    schedule_interval='@daily',  # When to run
    # Options:
    # ├─ '@once': Run once
    # ├─ '@hourly': Every hour
    # ├─ '@daily': Every day at midnight
    # ├─ '@weekly': Every Sunday at midnight
    # ├─ '@monthly': First day of month at midnight
    # ├─ Cron: '0 2 * * *' (2am daily)
    # └─ None: Manual trigger only
    
    start_date=datetime(2023, 10, 1),  # First run date
    # If today is 2023-10-15:
    # ├─ start_date=2023-10-01, catchup=False → Runs once on 2023-10-15
    # └─ start_date=2023-10-01, catchup=True → Runs 15 times (backfill 10/01 to 10/15)
    
    catchup=False,  # Don't backfill past runs (usually False in production)
    
    tags=['example'],  # Tags for filtering in UI
)
```

---

## 🔧 Common Operators

### 1. BashOperator

```python
from airflow.operators.bash import BashOperator

# Run shell command
run_script = BashOperator(
    task_id='run_etl_script',
    bash_command='python /opt/airflow/scripts/etl.py',
    dag=dag,
)

# Multiple commands (use semicolon)
multi_cmd = BashOperator(
    task_id='multi_command',
    bash_command='cd /data && ls -la && wc -l file.csv',
    dag=dag,
)

# Environment variables
with_env = BashOperator(
    task_id='with_env',
    bash_command='echo "Processing date: $EXECUTION_DATE"',
    env={'EXECUTION_DATE': '{{ ds }}'},  # Jinja template (explained later)
    dag=dag,
)
```

---

### 2. PythonOperator

```python
from airflow.operators.python import PythonOperator

# Define Python function
def extract_data(**context):
    """Extract data from API"""
    import requests
    response = requests.get('https://api.example.com/data')
    data = response.json()
    print(f"Extracted {len(data)} records")
    return data  # Return value stored in XCom

def transform_data(**context):
    """Transform data"""
    # Get data from previous task (XCom pull)
    ti = context['ti']
    data = ti.xcom_pull(task_ids='extract_data')
    
    # Transform
    transformed = [record.upper() for record in data]
    print(f"Transformed {len(transformed)} records")
    return transformed

# Create tasks
task_extract = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    provide_context=True,  # Pass context to function
    dag=dag,
)

task_transform = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    provide_context=True,
    dag=dag,
)

task_extract >> task_transform
```

---

### 3. PythonVirtualenvOperator

```python
from airflow.operators.python import PythonVirtualenvOperator

# Run in isolated virtualenv (useful for conflicting dependencies)
task_with_venv = PythonVirtualenvOperator(
    task_id='run_ml_model',
    python_callable=lambda: __import__('sklearn').ensemble.RandomForestClassifier(),
    requirements=['scikit-learn==1.0.2'],  # Install packages in venv
    system_site_packages=False,  # Don't inherit system packages
    dag=dag,
)
```

---

### 4. EmailOperator

```python
from airflow.operators.email import EmailOperator

# Send email
send_email = EmailOperator(
    task_id='send_success_email',
    to='team@company.com',
    subject='ETL Pipeline Success',
    html_content='<h3>Pipeline completed successfully!</h3>',
    dag=dag,
)
```

---

## 📊 Task Dependencies

### Linear Dependencies

```python
# Method 1: Bitshift operators (recommended)
task_a >> task_b >> task_c >> task_d

# Method 2: set_downstream
task_a.set_downstream(task_b)
task_b.set_downstream(task_c)
task_c.set_downstream(task_d)

# Method 3: set_upstream
task_d.set_upstream(task_c)
task_c.set_upstream(task_b)
task_b.set_upstream(task_a)

# Visualization:
# task_a ──> task_b ──> task_c ──> task_d
```

---

### Parallel Dependencies

```python
# Run tasks in parallel
task_start >> [task_a, task_b, task_c] >> task_end

# Visualization:
#            ┌──> task_a ──┐
#            │             │
# task_start ├──> task_b ──┤──> task_end
#            │             │
#            └──> task_c ──┘

# Execution:
# 1. task_start runs
# 2. task_a, task_b, task_c run in parallel
# 3. task_end waits for all 3 to complete
# 4. task_end runs
```

---

### Complex Dependencies

```python
# Diamond pattern
task_extract >> [task_transform_a, task_transform_b]
task_transform_a >> task_merge
task_transform_b >> task_merge
task_merge >> task_load

# Visualization:
#                  ┌──> transform_a ──┐
#                  │                  │
# extract ─────────┤                  ├──> merge ──> load
#                  │                  │
#                  └──> transform_b ──┘

# Execution:
# 1. extract runs
# 2. transform_a and transform_b run in parallel
# 3. merge waits for BOTH to complete
# 4. merge runs
# 5. load runs
```

---

## 📦 XCom (Cross-Communication)

### What is XCom?

```
XCom = Mechanism for tasks to exchange small data

How it works:
1. Task A returns value → Stored in metadata DB
2. Task B pulls value → Reads from metadata DB

Limitation:
├─ Max size: 1 MB (SQLite), 64 MB (PostgreSQL)
└─ For large data: Use external storage (S3, HDFS)
```

---

### XCom Push

```python
from airflow.operators.python import PythonOperator

def task_push_xcom(**context):
    """Push value to XCom"""
    data = {'records': 1000, 'timestamp': '2023-10-15'}
    
    # Method 1: Return value (automatically pushed)
    return data
    
    # Method 2: Explicit push
    context['ti'].xcom_push(key='my_data', value=data)

task_a = PythonOperator(
    task_id='push_xcom',
    python_callable=task_push_xcom,
    provide_context=True,
    dag=dag,
)
```

---

### XCom Pull

```python
def task_pull_xcom(**context):
    """Pull value from XCom"""
    ti = context['ti']
    
    # Method 1: Pull from specific task (default key 'return_value')
    data = ti.xcom_pull(task_ids='push_xcom')
    print(f"Received: {data}")  # {'records': 1000, 'timestamp': '2023-10-15'}
    
    # Method 2: Pull with custom key
    data = ti.xcom_pull(task_ids='push_xcom', key='my_data')
    
    # Method 3: Pull from multiple tasks
    data_list = ti.xcom_pull(task_ids=['task_a', 'task_b'])
    print(f"Received: {data_list}")  # [data_from_task_a, data_from_task_b]

task_b = PythonOperator(
    task_id='pull_xcom',
    python_callable=task_pull_xcom,
    provide_context=True,
    dag=dag,
)

task_a >> task_b
```

---

### XCom Example: ETL Pipeline

```python
def extract(**context):
    import requests
    response = requests.get('https://api.example.com/users')
    data = response.json()
    return data  # Push to XCom

def transform(**context):
    ti = context['ti']
    data = ti.xcom_pull(task_ids='extract')  # Pull from XCom
    
    transformed = []
    for record in data:
        transformed.append({
            'user_id': record['id'],
            'full_name': f"{record['first_name']} {record['last_name']}",
            'email': record['email'].lower(),
        })
    
    return transformed  # Push to XCom

def load(**context):
    ti = context['ti']
    data = ti.xcom_pull(task_ids='transform')  # Pull from XCom
    
    # Write to database
    import psycopg2
    conn = psycopg2.connect("host=postgres dbname=warehouse")
    cur = conn.cursor()
    
    for record in data:
        cur.execute("""
            INSERT INTO users (user_id, full_name, email)
            VALUES (%(user_id)s, %(full_name)s, %(email)s)
        """, record)
    
    conn.commit()
    conn.close()
    print(f"Loaded {len(data)} records")

# Create DAG
extract_task = PythonOperator(task_id='extract', python_callable=extract)
transform_task = PythonOperator(task_id='transform', python_callable=transform)
load_task = PythonOperator(task_id='load', python_callable=load)

extract_task >> transform_task >> load_task
```

---

## 🕒 Scheduling and Cron Expressions

### Preset Schedules

```python
schedule_interval='@once'      # Run once (manual trigger only)
schedule_interval='@hourly'    # 0 * * * * (every hour)
schedule_interval='@daily'     # 0 0 * * * (midnight daily)
schedule_interval='@weekly'    # 0 0 * * 0 (Sunday midnight)
schedule_interval='@monthly'   # 0 0 1 * * (1st day of month)
schedule_interval='@yearly'    # 0 0 1 1 * (Jan 1st)
```

---

### Cron Expressions

```
Cron format: minute hour day_of_month month day_of_week

Examples:
'0 2 * * *'     # 2am daily
'0 */6 * * *'   # Every 6 hours (0am, 6am, 12pm, 6pm)
'30 8 * * 1-5'  # 8:30am Monday-Friday
'0 0 1 * *'     # 1st day of month at midnight
'0 0 * * 0'     # Every Sunday at midnight

Field ranges:
├─ minute: 0-59
├─ hour: 0-23
├─ day_of_month: 1-31
├─ month: 1-12
└─ day_of_week: 0-6 (0=Sunday)

Special characters:
├─ *: Any value
├─ */N: Every N units
├─ 1-5: Range (1 to 5)
└─ 1,3,5: List (1, 3, 5)
```

**Example:**

```python
# Run every 15 minutes during business hours (9am-5pm, Mon-Fri)
DAG(
    dag_id='frequent_pipeline',
    schedule_interval='*/15 9-17 * * 1-5',
    start_date=datetime(2023, 10, 1),
    catchup=False,
)
```

---

## 🐛 Debugging and Logging

### View Logs in Web UI

```
1. Open Airflow UI: http://localhost:8080
2. Click on DAG → Click on task → Click "Log"

Example log:
[2023-10-15 02:00:00] {python.py:123} INFO - Extracted 1000 records
[2023-10-15 02:00:05] {python.py:456} INFO - Transformed 1000 records
[2023-10-15 02:00:10] {python.py:789} INFO - Loaded 1000 records
[2023-10-15 02:00:11] {taskinstance.py:1234} INFO - Task succeeded
```

---

### Print Debugging

```python
def my_task(**context):
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("Starting task")  # INFO level
    logger.warning("This is a warning")  # WARNING level
    logger.error("This is an error")  # ERROR level
    
    # Regular print also works (but logger is preferred)
    print("Regular print statement")
```

---

### Task Instance Context

```python
def debug_task(**context):
    """Print all context variables"""
    import json
    
    # Available context variables:
    print(f"Execution date: {context['execution_date']}")  # 2023-10-15 00:00:00
    print(f"DAG ID: {context['dag'].dag_id}")  # hello_world
    print(f"Task ID: {context['task'].task_id}")  # debug_task
    print(f"Run ID: {context['run_id']}")  # scheduled__2023-10-15T00:00:00+00:00
    
    # Task instance (for XCom)
    ti = context['ti']
    print(f"Task instance: {ti}")
    
    # Params (user-defined parameters)
    print(f"Params: {context['params']}")
    
    # Templates (Jinja variables)
    print(f"Execution date (ds): {context['ds']}")  # 2023-10-15
    print(f"Execution date (ds_nodash): {context['ds_nodash']}")  # 20231015
```

---

## 🎓 Beginner Exercises

### Exercise 1: Daily ETL Pipeline

```python
"""
Create a DAG that runs daily at 3am:
1. Extract data from CSV file
2. Transform: Filter rows where age > 18
3. Load to PostgreSQL
4. Send email on success
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from datetime import datetime, timedelta
import pandas as pd
import psycopg2

default_args = {
    'owner': 'data_team',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

def extract(**context):
    df = pd.read_csv('/data/users.csv')
    return df.to_dict('records')  # Convert to list of dicts for XCom

def transform(**context):
    ti = context['ti']
    data = ti.xcom_pull(task_ids='extract')
    
    filtered = [record for record in data if record['age'] > 18]
    return filtered

def load(**context):
    ti = context['ti']
    data = ti.xcom_pull(task_ids='transform')
    
    conn = psycopg2.connect("host=postgres dbname=warehouse")
    cur = conn.cursor()
    
    for record in data:
        cur.execute("INSERT INTO users (id, name, age) VALUES (%s, %s, %s)",
                    (record['id'], record['name'], record['age']))
    
    conn.commit()
    conn.close()

with DAG(
    dag_id='daily_etl',
    default_args=default_args,
    schedule_interval='0 3 * * *',  # 3am daily
    start_date=datetime(2023, 10, 1),
    catchup=False,
) as dag:
    
    extract_task = PythonOperator(task_id='extract', python_callable=extract)
    transform_task = PythonOperator(task_id='transform', python_callable=transform)
    load_task = PythonOperator(task_id='load', python_callable=load)
    email_task = EmailOperator(
        task_id='send_email',
        to='team@company.com',
        subject='ETL Success',
        html_content='Pipeline completed!'
    )
    
    extract_task >> transform_task >> load_task >> email_task
```

---

### Exercise 2: Parallel Processing

```python
"""
Create a DAG that processes 3 regions in parallel:
1. extract_all: Fetch data
2. process_us, process_eu, process_asia: Process in parallel
3. merge_results: Combine results
4. send_report: Email final report
"""

# Your solution here!
```

---

## 📚 Summary Checklist

- [ ] Understand why orchestration is needed
- [ ] Explain Airflow architecture (scheduler, executor, web server, metadata DB)
- [ ] Create basic DAG with BashOperator and PythonOperator
- [ ] Define task dependencies (linear, parallel, diamond)
- [ ] Use XCom to pass data between tasks
- [ ] Configure scheduling with cron expressions
- [ ] View logs and debug failed tasks
- [ ] Build end-to-end ETL pipeline

**Next:** [INTERMEDIATE.md →](INTERMEDIATE.md)
