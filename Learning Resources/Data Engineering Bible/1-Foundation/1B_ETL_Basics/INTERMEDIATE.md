# Week 2: ETL Pipelines & Data Modeling
## 🛠️ INTERMEDIATE - Building Production ETL

---

## 🎯 **Learning Objectives**

By the end of this section, you will:
- Build a complete ETL pipeline in Python
- Handle schema changes and data quality issues
- Implement Slowly Changing Dimensions (SCD)
- Design star schema data warehouses
- Solve 5 ETL interview questions

---

## 🧪 **1. Hands-On Lab: Build an E-Commerce ETL Pipeline**

### **Scenario**

You work for an e-commerce company with data in multiple sources:
- **Orders:** PostgreSQL transactional database
- **Customers:** Salesforce CRM (API)
- **Products:** MongoDB catalog
- **Web Events:** JSON logs in S3

**Goal:** Build a data warehouse for analytics team to answer:
- What are our daily sales by category?
- Who are our top customers?
- Which products have highest return rates?

---

### **Lab 1: Extract - Data Ingestion**

```python
import pandas as pd
import psycopg2
import requests
from pymongo import MongoClient
import boto3
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataExtractor:
    """
    Extract data from multiple sources
    """
    
    def __init__(self, config):
        self.config = config
        self.staging_path = config['staging_path']
    
    def extract_orders(self, start_date, end_date):
        """
        Extract orders from PostgreSQL
        """
        logger.info(f"Extracting orders from {start_date} to {end_date}")
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=self.config['postgres']['host'],
            database=self.config['postgres']['database'],
            user=self.config['postgres']['user'],
            password=self.config['postgres']['password']
        )
        
        # Query with date filter
        query = f"""
            SELECT 
                order_id,
                customer_id,
                product_id,
                order_date,
                quantity,
                price,
                status
            FROM orders
            WHERE order_date >= '{start_date}'
              AND order_date < '{end_date}'
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        logger.info(f"Extracted {len(df)} orders")
        
        # Save to staging
        staging_file = f"{self.staging_path}/orders_{start_date}.parquet"
        df.to_parquet(staging_file, index=False)
        
        return df
    
    def extract_customers(self):
        """
        Extract customers from Salesforce API
        """
        logger.info("Extracting customers from Salesforce")
        
        # Salesforce API authentication
        auth_url = "https://login.salesforce.com/services/oauth2/token"
        auth_data = {
            'grant_type': 'password',
            'client_id': self.config['salesforce']['client_id'],
            'client_secret': self.config['salesforce']['client_secret'],
            'username': self.config['salesforce']['username'],
            'password': self.config['salesforce']['password']
        }
        
        auth_response = requests.post(auth_url, data=auth_data)
        access_token = auth_response.json()['access_token']
        
        # Query customers
        query_url = f"{self.config['salesforce']['instance_url']}/services/data/v52.0/query"
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {
            'q': 'SELECT Id, Name, Email, City, State, Country, CreatedDate FROM Account'
        }
        
        response = requests.get(query_url, headers=headers, params=params)
        records = response.json()['records']
        
        # Convert to DataFrame
        df = pd.DataFrame(records)
        df.rename(columns={'Id': 'customer_id'}, inplace=True)
        
        logger.info(f"Extracted {len(df)} customers")
        
        # Save to staging
        staging_file = f"{self.staging_path}/customers_{datetime.now().date()}.parquet"
        df.to_parquet(staging_file, index=False)
        
        return df
    
    def extract_products(self):
        """
        Extract products from MongoDB
        """
        logger.info("Extracting products from MongoDB")
        
        # Connect to MongoDB
        client = MongoClient(self.config['mongodb']['connection_string'])
        db = client[self.config['mongodb']['database']]
        collection = db['products']
        
        # Query all products
        cursor = collection.find({})
        products = list(cursor)
        
        # Convert to DataFrame
        df = pd.DataFrame(products)
        df.rename(columns={'_id': 'product_id'}, inplace=True)
        
        logger.info(f"Extracted {len(df)} products")
        
        # Save to staging
        staging_file = f"{self.staging_path}/products_{datetime.now().date()}.parquet"
        df.to_parquet(staging_file, index=False)
        
        return df
    
    def extract_web_events(self, date):
        """
        Extract web events from S3 JSON logs
        """
        logger.info(f"Extracting web events for {date}")
        
        # Connect to S3
        s3 = boto3.client('s3')
        bucket = self.config['s3']['bucket']
        prefix = f"logs/{date.year}/{date.month:02d}/{date.day:02d}/"
        
        # List objects
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        
        events = []
        for obj in response.get('Contents', []):
            # Download and parse JSON
            obj_data = s3.get_object(Bucket=bucket, Key=obj['Key'])
            json_data = obj_data['Body'].read().decode('utf-8')
            
            for line in json_data.split('\n'):
                if line:
                    events.append(json.loads(line))
        
        df = pd.DataFrame(events)
        
        logger.info(f"Extracted {len(df)} web events")
        
        # Save to staging
        staging_file = f"{self.staging_path}/web_events_{date}.parquet"
        df.to_parquet(staging_file, index=False)
        
        return df
```

---

### **Lab 2: Transform - Data Cleaning & Preparation**

```python
class DataTransformer:
    """
    Transform and clean data
    """
    
    def transform_orders(self, df):
        """
        Clean and enrich orders data
        """
        logger.info("Transforming orders data")
        
        # 1. DATA QUALITY CHECKS
        initial_count = len(df)
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['order_id'])
        logger.info(f"Removed {initial_count - len(df)} duplicate orders")
        
        # Remove nulls in critical columns
        df = df.dropna(subset=['order_id', 'customer_id', 'product_id'])
        
        # Validate numeric fields
        df = df[df['quantity'] > 0]
        df = df[df['price'] >= 0]
        
        # 2. DATA TYPE CONVERSIONS
        df['order_date'] = pd.to_datetime(df['order_date'])
        df['quantity'] = df['quantity'].astype(int)
        df['price'] = df['price'].astype(float)
        
        # 3. DERIVED COLUMNS
        df['total_amount'] = df['quantity'] * df['price']
        df['order_year'] = df['order_date'].dt.year
        df['order_month'] = df['order_date'].dt.month
        df['order_day'] = df['order_date'].dt.day
        
        # 4. BUSINESS LOGIC
        # Flag high-value orders
        df['is_high_value'] = df['total_amount'] > 1000
        
        # Calculate discount (if applicable)
        df['discount_percent'] = df.apply(
            lambda row: 10 if row['quantity'] >= 10 else 0,
            axis=1
        )
        
        df['final_amount'] = df['total_amount'] * (1 - df['discount_percent'] / 100)
        
        logger.info(f"Transformed {len(df)} orders")
        
        return df
    
    def transform_customers(self, df):
        """
        Clean and standardize customer data
        """
        logger.info("Transforming customers data")
        
        # 1. HANDLE NULLS
        df['email'] = df['email'].fillna('unknown@example.com')
        df['city'] = df['city'].fillna('Unknown')
        df['state'] = df['state'].fillna('Unknown')
        df['country'] = df['country'].fillna('Unknown')
        
        # 2. STANDARDIZATION
        # Lowercase emails
        df['email'] = df['email'].str.lower().str.strip()
        
        # Standardize country names
        country_mapping = {
            'USA': 'United States',
            'US': 'United States',
            'UK': 'United Kingdom',
            'U.K.': 'United Kingdom'
        }
        df['country'] = df['country'].replace(country_mapping)
        
        # Title case for names
        df['name'] = df['name'].str.title()
        
        # 3. VALIDATION
        # Valid email check (simple)
        df['email_valid'] = df['email'].str.contains('@', na=False)
        
        # 4. DERIVED COLUMNS
        df['created_date'] = pd.to_datetime(df['CreatedDate'])
        df['customer_tenure_days'] = (datetime.now() - df['created_date']).dt.days
        
        # Segment by tenure
        df['customer_segment'] = pd.cut(
            df['customer_tenure_days'],
            bins=[0, 90, 365, 730, float('inf')],
            labels=['New', 'Regular', 'Loyal', 'VIP']
        )
        
        logger.info(f"Transformed {len(df)} customers")
        
        return df
    
    def transform_products(self, df):
        """
        Clean and categorize products
        """
        logger.info("Transforming products data")
        
        # 1. HANDLE MISSING VALUES
        df['description'] = df['description'].fillna('No description')
        df['category'] = df['category'].fillna('Uncategorized')
        
        # 2. STANDARDIZATION
        df['category'] = df['category'].str.lower().str.strip()
        df['name'] = df['name'].str.strip()
        
        # 3. DERIVED COLUMNS
        # Extract brand from name (if follows pattern)
        df['brand'] = df['name'].str.split(' ').str[0]
        
        # Price tier
        df['price_tier'] = pd.cut(
            df['price'],
            bins=[0, 50, 200, 1000, float('inf')],
            labels=['Budget', 'Mid-Range', 'Premium', 'Luxury']
        )
        
        # 4. BUSINESS RULES
        # Flag out-of-stock
        df['in_stock'] = df['inventory_count'] > 0
        
        # Reorder flag
        df['needs_reorder'] = df['inventory_count'] < df['reorder_threshold']
        
        logger.info(f"Transformed {len(df)} products")
        
        return df
    
    def build_date_dimension(self, start_date, end_date):
        """
        Create a date dimension table
        """
        logger.info("Building date dimension")
        
        # Generate date range
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        df = pd.DataFrame({
            'date_id': dates.strftime('%Y%m%d').astype(int),
            'date': dates,
            'year': dates.year,
            'month': dates.month,
            'day': dates.day,
            'quarter': dates.quarter,
            'day_of_week': dates.dayofweek,
            'day_name': dates.day_name(),
            'month_name': dates.month_name(),
            'week_of_year': dates.isocalendar().week,
            'is_weekend': dates.dayofweek.isin([5, 6]),
            'is_holiday': False  # Would integrate with holiday calendar
        })
        
        logger.info(f"Built date dimension with {len(df)} days")
        
        return df
```

---

### **Lab 3: Load - Data Warehouse Loading**

```python
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, Boolean, Date, MetaData

class DataLoader:
    """
    Load transformed data into data warehouse
    """
    
    def __init__(self, config):
        self.config = config
        self.engine = create_engine(config['warehouse']['connection_string'])
        self.metadata = MetaData()
    
    def create_star_schema(self):
        """
        Create star schema tables if they don't exist
        """
        logger.info("Creating star schema")
        
        # FACT TABLE: Sales
        sales_fact = Table('fact_sales', self.metadata,
            Column('sale_id', Integer, primary_key=True),
            Column('order_id', String(50), unique=True),
            Column('customer_id', Integer),
            Column('product_id', Integer),
            Column('date_id', Integer),
            Column('quantity', Integer),
            Column('unit_price', Float),
            Column('total_amount', Float),
            Column('discount_percent', Float),
            Column('final_amount', Float),
            Column('is_high_value', Boolean),
            Column('created_at', Date)
        )
        
        # DIMENSION: Customers
        dim_customers = Table('dim_customers', self.metadata,
            Column('customer_id', Integer, primary_key=True),
            Column('name', String(200)),
            Column('email', String(200)),
            Column('city', String(100)),
            Column('state', String(100)),
            Column('country', String(100)),
            Column('customer_segment', String(50)),
            Column('customer_tenure_days', Integer),
            Column('email_valid', Boolean),
            Column('created_date', Date),
            Column('effective_date', Date),
            Column('end_date', Date),
            Column('is_current', Boolean)
        )
        
        # DIMENSION: Products
        dim_products = Table('dim_products', self.metadata,
            Column('product_id', Integer, primary_key=True),
            Column('name', String(200)),
            Column('description', String(1000)),
            Column('category', String(100)),
            Column('brand', String(100)),
            Column('price', Float),
            Column('price_tier', String(50)),
            Column('in_stock', Boolean),
            Column('needs_reorder', Boolean)
        )
        
        # DIMENSION: Date
        dim_date = Table('dim_date', self.metadata,
            Column('date_id', Integer, primary_key=True),
            Column('date', Date),
            Column('year', Integer),
            Column('month', Integer),
            Column('day', Integer),
            Column('quarter', Integer),
            Column('day_of_week', Integer),
            Column('day_name', String(20)),
            Column('month_name', String(20)),
            Column('week_of_year', Integer),
            Column('is_weekend', Boolean),
            Column('is_holiday', Boolean)
        )
        
        # Create all tables
        self.metadata.create_all(self.engine)
        logger.info("Star schema created successfully")
    
    def load_dimension(self, df, table_name, mode='replace'):
        """
        Load data into dimension table
        
        mode: 'replace' (full refresh) or 'append' (incremental)
        """
        logger.info(f"Loading {len(df)} records into {table_name} (mode: {mode})")
        
        df.to_sql(
            name=table_name,
            con=self.engine,
            if_exists=mode,
            index=False,
            method='multi'  # Batch insert for performance
        )
        
        logger.info(f"Successfully loaded {table_name}")
    
    def load_fact_incremental(self, df, table_name='fact_sales'):
        """
        Load fact table incrementally (append only new records)
        """
        logger.info(f"Loading {len(df)} records into {table_name}")
        
        # Get existing order_ids to avoid duplicates
        existing_query = f"SELECT order_id FROM {table_name}"
        existing_orders = pd.read_sql(existing_query, self.engine)
        
        # Filter out existing orders (idempotency!)
        new_records = df[~df['order_id'].isin(existing_orders['order_id'])]
        
        if len(new_records) > 0:
            new_records.to_sql(
                name=table_name,
                con=self.engine,
                if_exists='append',
                index=False,
                method='multi'
            )
            logger.info(f"Loaded {len(new_records)} new records")
        else:
            logger.info("No new records to load")
    
    def update_dimension_scd_type2(self, new_df, table_name, key_column):
        """
        Slowly Changing Dimension Type 2
        Track historical changes by creating new rows
        """
        logger.info(f"Updating {table_name} with SCD Type 2")
        
        # Read existing dimension
        existing_df = pd.read_sql(f"SELECT * FROM {table_name} WHERE is_current = TRUE", self.engine)
        
        # Find changed records
        merged = new_df.merge(
            existing_df,
            on=key_column,
            how='left',
            suffixes=('_new', '_old')
        )
        
        # Detect changes (compare all columns except metadata)
        data_columns = [col for col in new_df.columns if col not in [key_column, 'effective_date', 'end_date', 'is_current']]
        
        changed_mask = merged.apply(
            lambda row: any(row[f"{col}_new"] != row[f"{col}_old"] for col in data_columns if f"{col}_old" in row),
            axis=1
        )
        
        changed_records = merged[changed_mask]
        
        if len(changed_records) > 0:
            # Step 1: Close old records (set end_date, is_current=False)
            update_query = f"""
                UPDATE {table_name}
                SET end_date = CURRENT_DATE - 1,
                    is_current = FALSE
                WHERE {key_column} IN ({','.join(map(str, changed_records[key_column]))})
                  AND is_current = TRUE
            """
            self.engine.execute(update_query)
            
            # Step 2: Insert new records
            new_records = changed_records[list(new_df.columns)]
            new_records['effective_date'] = datetime.now().date()
            new_records['end_date'] = pd.to_datetime('9999-12-31').date()
            new_records['is_current'] = True
            
            new_records.to_sql(
                name=table_name,
                con=self.engine,
                if_exists='append',
                index=False
            )
            
            logger.info(f"Updated {len(changed_records)} records with SCD Type 2")
        else:
            logger.info("No changes detected")
```

---

### **Lab 4: Complete ETL Orchestration**

```python
class ETLPipeline:
    """
    Orchestrate the complete ETL process
    """
    
    def __init__(self, config):
        self.config = config
        self.extractor = DataExtractor(config)
        self.transformer = DataTransformer()
        self.loader = DataLoader(config)
    
    def run_full_load(self, start_date, end_date):
        """
        Full ETL pipeline execution
        """
        logger.info(f"Starting ETL pipeline for {start_date} to {end_date}")
        
        try:
            # PHASE 1: EXTRACT
            logger.info("=== PHASE 1: EXTRACT ===")
            orders_raw = self.extractor.extract_orders(start_date, end_date)
            customers_raw = self.extractor.extract_customers()
            products_raw = self.extractor.extract_products()
            
            # PHASE 2: TRANSFORM
            logger.info("=== PHASE 2: TRANSFORM ===")
            orders_clean = self.transformer.transform_orders(orders_raw)
            customers_clean = self.transformer.transform_customers(customers_raw)
            products_clean = self.transformer.transform_products(products_raw)
            date_dim = self.transformer.build_date_dimension(start_date, end_date)
            
            # PHASE 3: LOAD
            logger.info("=== PHASE 3: LOAD ===")
            
            # Create schema if needed
            self.loader.create_star_schema()
            
            # Load dimensions (full refresh for simplicity)
            self.loader.load_dimension(customers_clean, 'dim_customers', mode='replace')
            self.loader.load_dimension(products_clean, 'dim_products', mode='replace')
            self.loader.load_dimension(date_dim, 'dim_date', mode='replace')
            
            # Load facts (incremental)
            self.loader.load_fact_incremental(orders_clean, 'fact_sales')
            
            logger.info("ETL pipeline completed successfully!")
            
            return {
                'status': 'success',
                'records_processed': {
                    'orders': len(orders_clean),
                    'customers': len(customers_clean),
                    'products': len(products_clean),
                    'dates': len(date_dim)
                }
            }
            
        except Exception as e:
            logger.error(f"ETL pipeline failed: {str(e)}")
            return {'status': 'failed', 'error': str(e)}

# USAGE
if __name__ == "__main__":
    config = {
        'staging_path': '/tmp/etl_staging',
        'postgres': {
            'host': 'localhost',
            'database': 'ecommerce',
            'user': 'etl_user',
            'password': 'secret'
        },
        'salesforce': {
            'client_id': 'xxx',
            'client_secret': 'yyy',
            'username': 'user@company.com',
            'password': 'zzz',
            'instance_url': 'https://company.salesforce.com'
        },
        'mongodb': {
            'connection_string': 'mongodb://localhost:27017',
            'database': 'catalog'
        },
        's3': {
            'bucket': 'company-logs'
        },
        'warehouse': {
            'connection_string': 'postgresql://warehouse:5432/analytics'
        }
    }
    
    pipeline = ETLPipeline(config)
    
    # Run for yesterday's data
    yesterday = datetime.now() - timedelta(days=1)
    result = pipeline.run_full_load(
        start_date=yesterday.date(),
        end_date=datetime.now().date()
    )
    
    print(result)
```

---

## 🔍 **2. Mental Models: Advanced ETL Patterns**

### **Pattern 1: Slowly Changing Dimensions (SCD)**

**Problem:** Customer data changes over time. How do we track history?

**Type 1: Overwrite (No History)**
```sql
-- Customer moves from NYC to LA
UPDATE dim_customers
SET city = 'Los Angeles'
WHERE customer_id = 123

-- Old value lost!
```

**Type 2: Add New Row (Full History)** ⭐ Most Common
```sql
-- Close old record
UPDATE dim_customers
SET end_date = '2025-10-08',
    is_current = FALSE
WHERE customer_id = 123 AND is_current = TRUE

-- Insert new record
INSERT INTO dim_customers VALUES (
    123,  -- customer_id
    'John Doe',
    'Los Angeles',  -- new city
    '2025-10-09',  -- effective_date
    '9999-12-31',  -- end_date
    TRUE  -- is_current
)
```

**Type 3: Add New Column (Limited History)**
```sql
-- Keep current + previous
ALTER TABLE dim_customers
ADD COLUMN previous_city VARCHAR(100)

UPDATE dim_customers
SET previous_city = city,
    city = 'Los Angeles'
WHERE customer_id = 123
```

**When to Use Each:**

| Type | Use Case | Pros | Cons |
|------|----------|------|------|
| **Type 1** | Non-critical changes | Simple | Loses history |
| **Type 2** | Full audit trail | Complete history | More storage |
| **Type 3** | Track 1-2 changes | Balance | Limited history |

---

### **Pattern 2: Incremental vs Full Load**

**Full Load:**
```python
# Delete everything, reload from scratch
warehouse.execute("TRUNCATE TABLE dim_products")
products = extract_all_products()
load_into_warehouse(products)

# Pros: Simple, guaranteed consistency
# Cons: Slow for large tables
```

**Incremental Load:**
```python
# Load only new/changed records
last_run = get_last_run_timestamp()
products = extract_products_since(last_run)
upsert_into_warehouse(products)

# Pros: Fast, efficient
# Cons: Complex, risk of missing records
```

**Hybrid Approach (Recommended):**
```python
# Incremental daily, full weekly
if today.is_sunday():
    full_load()
else:
    incremental_load()
```

---

### **Pattern 3: Idempotent ETL Design**

**Problem:** Pipeline fails halfway. Can we safely re-run?

**❌ Non-Idempotent:**
```python
# BAD: Adds duplicates on retry
df.to_sql('fact_sales', if_exists='append')
```

**✅ Idempotent:**
```python
# GOOD: Upsert (insert or update)
def upsert(df, table, key_column):
    # Delete existing
    existing_keys = df[key_column].tolist()
    delete_query = f"DELETE FROM {table} WHERE {key_column} IN ({existing_keys})"
    warehouse.execute(delete_query)
    
    # Insert
    df.to_sql(table, if_exists='append')

# Alternative: Use unique constraints
# Database will reject duplicates
```

---

## 💡 **3. Interview Questions (Easy to Medium)**

### **Question 1: Explain the difference between ETL and ELT**

**Answer:**

**ETL (Extract, Transform, Load) - Traditional:**
```
Sources → Extract → Transform (external tool) → Load → Warehouse
```
- Transform BEFORE loading
- Uses external ETL tool (Informatica, Talend)
- Best for: Complex transformations, data quality checks

**ELT (Extract, Load, Transform) - Modern:**
```
Sources → Extract → Load (raw) → Warehouse → Transform (SQL/dbt)
```
- Load raw data FIRST, transform in warehouse
- Leverages warehouse compute power
- Best for: Cloud data warehouses (Snowflake, BigQuery)

**Why ELT is trending:**
1. Cloud warehouses have massive compute
2. Storage is cheap (can store raw + transformed)
3. SQL is powerful (dbt, Spark SQL)
4. Flexibility (re-transform without re-extracting)

**When to still use ETL:**
- Legacy on-prem systems
- Limited warehouse compute
- Sensitive data (mask before loading)

---

### **Question 2: How do you handle late-arriving data?**

**Scenario:** Order placed on Oct 5, but data arrives on Oct 10

**Solutions:**

**Solution 1: Window-Based Processing**
```python
# Process with 5-day window
def daily_etl(date):
    # Load data from date-5 to date
    data = extract_data(date - timedelta(5), date)
    
    # Upsert (handle duplicates)
    upsert_into_warehouse(data)

# Pros: Captures late data
# Cons: Reprocesses old data
```

**Solution 2: Backfill Process**
```python
# Detect late arrivals
late_data = find_data_newer_than_last_run()

if late_data:
    # Trigger backfill
    backfill_dates = late_data.get_affected_dates()
    for date in backfill_dates:
        reprocess_date(date)
```

**Solution 3: SCD Type 2 for Facts**
```python
# Treat facts like slowly changing dimensions
# Keep multiple versions with effective dates

INSERT INTO fact_sales (
    order_id,
    effective_date,
    is_current,
    ...
) VALUES (
    '12345',
    '2025-10-10',  -- When we learned about it
    TRUE,
    ...
)
```

---

### **Question 3: Design a data quality framework for ETL**

**Answer:**

**Quality Checks at Each Stage:**

```python
class DataQualityChecker:
    def check_extract(self, df, source_name):
        """
        Validate extracted data
        """
        checks = []
        
        # 1. Row count check
        if len(df) == 0:
            checks.append({'source': source_name, 'check': 'row_count', 'status': 'FAIL', 'message': 'No data extracted'})
        
        # 2. Schema validation
        expected_columns = self.get_expected_schema(source_name)
        missing_columns = set(expected_columns) - set(df.columns)
        if missing_columns:
            checks.append({'check': 'schema', 'status': 'FAIL', 'message': f'Missing columns: {missing_columns}'})
        
        # 3. Null checks for critical columns
        critical_columns = self.get_critical_columns(source_name)
        for col in critical_columns:
            null_pct = df[col].isna().mean() * 100
            if null_pct > 5:  # More than 5% nulls
                checks.append({'check': f'nulls_{col}', 'status': 'WARN', 'message': f'{null_pct:.1f}% nulls'})
        
        return checks
    
    def check_transform(self, df):
        """
        Validate transformed data
        """
        checks = []
        
        # 1. Data type validation
        if 'price' in df.columns:
            if not pd.api.types.is_numeric_dtype(df['price']):
                checks.append({'check': 'price_type', 'status': 'FAIL'})
        
        # 2. Range checks
        if 'quantity' in df.columns:
            if (df['quantity'] < 0).any():
                checks.append({'check': 'quantity_range', 'status': 'FAIL', 'message': 'Negative quantities found'})
        
        # 3. Referential integrity
        # (Check foreign keys exist in dimension tables)
        
        # 4. Business rule validation
        if 'total_amount' in df.columns:
            calculated = df['quantity'] * df['price']
            mismatch = (df['total_amount'] != calculated).sum()
            if mismatch > 0:
                checks.append({'check': 'total_amount_calc', 'status': 'FAIL', 'message': f'{mismatch} mismatches'})
        
        return checks
    
    def check_load(self, table_name, expected_count):
        """
        Validate loaded data
        """
        checks = []
        
        # 1. Row count reconciliation
        actual_count = warehouse.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        if actual_count != expected_count:
            checks.append({'check': 'row_count_reconcile', 'status': 'FAIL', 'message': f'Expected {expected_count}, got {actual_count}'})
        
        # 2. Duplicate check
        duplicate_count = warehouse.execute(f"""
            SELECT COUNT(*) FROM (
                SELECT key_column, COUNT(*) 
                FROM {table_name} 
                GROUP BY key_column 
                HAVING COUNT(*) > 1
            )
        """).fetchone()[0]
        
        if duplicate_count > 0:
            checks.append({'check': 'duplicates', 'status': 'FAIL', 'message': f'{duplicate_count} duplicates'})
        
        return checks
```

**Alerting:**
```python
def handle_quality_checks(checks):
    failures = [c for c in checks if c['status'] == 'FAIL']
    warnings = [c for c in checks if c['status'] == 'WARN']
    
    if failures:
        # Stop pipeline
        send_alert(f"ETL FAILED: {failures}")
        raise ETLException("Data quality checks failed")
    
    if warnings:
        # Continue but notify
        send_notification(f"ETL completed with warnings: {warnings}")
```

---

### **Question 4: How do you optimize ETL performance?**

**Answer:**

**Optimization Techniques:**

**1. Parallel Processing**
```python
from multiprocessing import Pool

def extract_partition(partition_id):
    # Extract one partition
    query = f"SELECT * FROM orders WHERE partition_id = {partition_id}"
    return execute_query(query)

# Process 10 partitions in parallel
with Pool(10) as pool:
    results = pool.map(extract_partition, range(10))
    
all_data = pd.concat(results)
```

**2. Incremental Extraction**
```python
# Instead of full table scan
SELECT * FROM orders  -- Scans entire table

# Use watermark
SELECT * FROM orders 
WHERE updated_at > '2025-10-08 00:00:00'  -- Only new/changed

# Requires updated_at column and index!
```

**3. Column Pruning**
```python
# BAD: Extract all columns
SELECT * FROM customers

# GOOD: Extract only needed columns
SELECT customer_id, name, email, city FROM customers

# Reduces network transfer and memory
```

**4. Push-Down Predicates**
```python
# BAD: Filter in Python
all_data = extract_all_orders()
filtered = all_data[all_data['status'] == 'completed']

# GOOD: Filter in database
query = "SELECT * FROM orders WHERE status = 'completed'"
filtered = execute_query(query)

# Database is optimized for filtering!
```

**5. Batch Inserts**
```python
# BAD: Row-by-row insert
for row in data:
    insert_row(row)  # 1000 network calls!

# GOOD: Batch insert
insert_batch(data, batch_size=1000)  # 1 network call
```

**6. Compression**
```python
# Use compressed formats
df.to_parquet('data.parquet', compression='snappy')

# vs uncompressed CSV
df.to_csv('data.csv')  # 10x larger!
```

---

### **Question 5: Explain your approach to schema evolution**

**Answer:**

**Scenario:** Source system adds a new column

**Strategies:**

**Strategy 1: Schema-On-Read (Flexible)**
```python
# Store raw data as-is (JSON, Parquet)
# Parse schema at query time

# Handles any schema changes
# No pipeline changes needed

# Trade-off: Slower queries
```

**Strategy 2: Schema Validation (Strict)**
```python
def validate_schema(df, expected_schema):
    # Check for new columns
    new_columns = set(df.columns) - set(expected_schema.keys())
    
    if new_columns:
        # Alert: Schema changed!
        send_alert(f"New columns detected: {new_columns}")
        
        # Options:
        # 1. Fail pipeline (strict)
        # 2. Drop new columns (ignore)
        # 3. Auto-add to warehouse (flexible)
        
# Choose based on governance needs
```

**Strategy 3: Schema Registry (Best Practice)**
```python
# Use Avro/Protobuf with schema registry

from confluent_kafka import avro

# Producer registers schema
schema = {
    "type": "record",
    "name": "Customer",
    "fields": [
        {"name": "id", "type": "int"},
        {"name": "name", "type": "string"},
        {"name": "email", "type": ["null", "string"], "default": null}  # Optional
    ]
}

# Consumer reads with schema
# Handles: backward/forward compatibility
```

**Backward vs Forward Compatibility:**

| Type | Meaning | Example |
|------|---------|---------|
| **Backward** | New code reads old data | Add optional column (default value) |
| **Forward** | Old code reads new data | Never remove required columns |
| **Full** | Both directions | Add only optional columns |

---

## 🎯 **Next Steps**

**You now understand:**
✅ How to build production ETL pipelines  
✅ Data quality frameworks  
✅ Slowly Changing Dimensions  
✅ Performance optimization  
✅ Schema evolution strategies  

**Next:**
- 🏗️ [EXPERT](./EXPERT.md) - Netflix/Airbnb architectures
- 📄 [WHITEPAPERS](./WHITEPAPERS.md) - Kimball vs Inmon methodologies

---

**Practice Exercise:**

Build an ETL pipeline for a music streaming service:
- **Sources:** User activity logs, song catalog, playlists
- **Warehouse:** Design star schema
- **Requirements:** Track listening history, user preferences, song popularity

*Solution in EXPERT section!* 🚀
