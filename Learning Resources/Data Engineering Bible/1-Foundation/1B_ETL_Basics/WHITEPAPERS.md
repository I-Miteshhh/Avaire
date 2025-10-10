# Week 2: ETL Pipelines & Data Modeling
## 📚 WHITEPAPERS - The Theoretical Foundations

---

## 🎯 **Learning Objectives**

This section digests the seminal academic and industry papers:
- Ralph Kimball's dimensional modeling methodology
- Bill Inmon's Corporate Information Factory
- Modern data warehousing evolution
- dbt's analytics engineering paradigm

---

## 📖 **1. Ralph Kimball: The Data Warehouse Toolkit (1996)**

### **Context & Impact**

**Author:** Ralph Kimball  
**Published:** 1996 (4th Edition: 2013)  
**Citations:** 10,000+ (most influential data warehousing book)  
**Impact:** Defined dimensional modeling for an entire generation

**Historical Context:**
- Mid-1990s: Businesses drowning in OLTP data
- BI tools emerging (Business Objects, Cognos)
- Need for "query-friendly" data structures
- Kimball: "Make data warehouses that business users can understand"

---

### **Core Thesis**

> **"Dimensional modeling is the only viable technique for databases that are designed to support end-user queries in a data warehouse."**

**Key Principle:** Optimize for query performance and business understanding, not normalized elegance.

---

### **1.1 The Four-Step Dimensional Design Process**

**Step 1: Select the Business Process**

**Definition:** Identify a single operational activity to model

**Examples:**
- Retail: Order fulfillment, inventory management, customer support
- Healthcare: Patient admissions, lab tests, prescriptions
- Finance: Loan applications, credit card transactions

**Anti-pattern:**
```
❌ Bad: "Build a customer data warehouse"
   (Too broad, not a process)

✅ Good: "Model the order fulfillment process"
   (Specific, measurable activity)
```

**Kimball's Insight:**  
Each business process becomes a separate fact table. Don't try to model everything at once.

---

**Step 2: Declare the Grain**

**Definition:** What does one row in the fact table represent?

**Example: Retail Sales**

```
Option A: One row per order
┌────────┬─────────┬────────┬────────┐
│order_id│ date    │customer│ total  │
├────────┼─────────┼────────┼────────┤
│  1001  │2025-01-10│  Alice │ $150   │
└────────┴─────────┴────────┴────────┘

Option B: One row per line item
┌────────┬──────────┬────────┬────────┬──────┬──────┐
│order_id│line_item │ date   │customer│product│ price│
├────────┼──────────┼────────┼────────┼──────┼──────┤
│  1001  │    1     │2025-01-10│ Alice │ iPhone│ $1200│
│  1001  │    2     │2025-01-10│ Alice │ Case  │ $50  │
└────────┴──────────┴────────┴────────┴──────┴──────┘
```

**Which is correct?** Depends on business questions!

- Want to analyze product mix? → Line item grain
- Only care about order totals? → Order grain

**Kimball's Rule:**  
> "Choose the most atomic (granular) level that answers the business questions."

**Why?**  
You can always aggregate up (line items → orders), but can't disaggregate down.

---

**Step 3: Identify the Dimensions**

**Definition:** The "who, what, where, when, why" context for facts

**Example:**

```
Business Question: "What was our revenue by product category in Q4 2024?"

Required dimensions:
- Product (contains category)
- Date (contains quarter)

Fact: revenue
```

**Kimball's Dimensions Checklist:**

| Dimension | Examples |
|-----------|----------|
| **Who** | Customer, Salesperson, Supplier |
| **What** | Product, Service, Campaign |
| **Where** | Store, Warehouse, Region |
| **When** | Date, Time, Fiscal Period |
| **Why** | Promotion, Return Reason |
| **How** | Payment Method, Shipping Method |

**Common Mistake:**
```sql
-- ❌ Bad: Dimension attributes in fact table
CREATE TABLE fact_sales (
    sale_id BIGINT,
    customer_name VARCHAR(200),  -- Should be in dim_customer!
    product_name VARCHAR(200),   -- Should be in dim_product!
    amount DECIMAL(10,2)
);

-- ✅ Good: Foreign keys to dimensions
CREATE TABLE fact_sales (
    sale_id BIGINT,
    customer_id BIGINT REFERENCES dim_customer,
    product_id BIGINT REFERENCES dim_product,
    amount DECIMAL(10,2)
);
```

---

**Step 4: Identify the Facts**

**Definition:** Numeric measurements that answer business questions

**Types of Facts:**

**1. Additive Facts (can sum across all dimensions)**
```sql
revenue, quantity, cost, profit
-- "What's total revenue by region?" ✅
SELECT region, SUM(revenue) FROM fact_sales GROUP BY region;
```

**2. Semi-Additive Facts (can sum across some dimensions)**
```sql
account_balance, inventory_level
-- ❌ Can't sum across time: SUM(balance) across months is meaningless
-- ✅ Can average across time: AVG(balance)
```

**3. Non-Additive Facts (can't sum at all)**
```sql
percentages, ratios, unit_price
-- ❌ SUM(unit_price) is meaningless
-- ✅ AVG(unit_price) or weighted average
```

**Kimball's Rule:**  
> "Facts should be numeric and additive. Everything else is a dimension."

---

### **1.2 Star Schema vs Snowflake Schema**

**Star Schema (Kimball's Preference):**

```
           ┌──────────────┐
           │ dim_product  │
           │─────────────│
           │ product_id   │
           │ name         │
           │ category  ◄──┼─┐
           │ brand        │ │
           └──────────────┘ │
                            │
           ┌──────────────┐ │
           │ dim_customer │ │
           │─────────────│ │
           │ customer_id  │ │
           │ name      ◄──┼─┼───┐
           │ city         │ │   │
           └──────────────┘ │   │
                            │   │
           ┌────────────────┼───┼────────┐
           │   fact_sales   │   │        │
           │───────────────│   │        │
           │ product_id ────┘   │        │
           │ customer_id ───────┘        │
           │ date_id ────────────────────┘
           │ amount                      │
           │ quantity                    │
           └────────────────────────────┘
                            │
           ┌──────────────┐ │
           │ dim_date     │ │
           │─────────────│ │
           │ date_id      │ │
           │ year      ◄──┼─┘
           │ quarter      │
           │ month        │
           └──────────────┘
```

**Snowflake Schema (Normalized):**

```
           ┌──────────────┐
           │ dim_category │
           │─────────────│
           │ category_id  │
           │ category_name│
           └──────┬───────┘
                  │
           ┌──────▼───────┐
           │ dim_product  │
           │─────────────│
           │ product_id   │
           │ name         │
           │ category_id◄─┼─┐
           │ brand_id     │ │
           └──────┬───────┘ │
                  │         │
           ┌──────▼───────┐ │
           │ dim_brand    │ │
           │─────────────│ │
           │ brand_id     │ │
           │ brand_name   │ │
           └──────────────┘ │
                            │
           ┌────────────────┼────────┐
           │   fact_sales   │        │
           │───────────────│        │
           │ product_id ────┘        │
           │ customer_id ────────────┘
           │ date_id                 │
           │ amount                  │
           └─────────────────────────┘
```

**Kimball's Verdict:**

> **"Always denormalize dimensions into star schemas."**

**Why?**

| Aspect | Star Schema | Snowflake Schema |
|--------|-------------|------------------|
| **Queries** | Simple (fewer joins) | Complex (many joins) |
| **Performance** | Faster | Slower |
| **Storage** | More (denormalized) | Less (normalized) |
| **ETL** | Simpler | Complex |
| **User-Friendly** | Yes | No |

**When to Snowflake?**
- Dimension is massive (100M+ rows)
- Hierarchy changes frequently (organizational chart)
- Storage cost is critical

**Kimball's Rule:** "Only snowflake when you have a really good reason."

---

### **1.3 Slowly Changing Dimensions (SCD)**

**Problem:**  
Dimension attributes change over time. How do you track history?

**Type 0: Retain Original (Never Change)**
```sql
CREATE TABLE dim_customer (
    customer_id BIGINT PRIMARY KEY,
    birth_date DATE,  -- Never changes
    social_security_number VARCHAR(11)  -- Never changes
);

-- Updates are ignored
```

**Use Case:** Immutable attributes

---

**Type 1: Overwrite (No History)**
```sql
-- Before
customer_id | name  | city
123         | Alice | Boston

-- Alice moves to NYC
UPDATE dim_customer
SET city = 'NYC'
WHERE customer_id = 123;

-- After
customer_id | name  | city
123         | Alice | NYC  ← History lost!
```

**Use Case:** 
- Corrections (fix typos)
- Attributes where history doesn't matter

**Downside:** Can't analyze historical trends

---

**Type 2: Add New Row (Track Full History)**
```sql
-- Before
customer_key | customer_id | name  | city   | effective_date | end_date   | is_current
1            | 123         | Alice | Boston | 2020-01-01     | 9999-12-31 | TRUE

-- Alice moves to NYC on 2025-10-01
INSERT INTO dim_customer VALUES (
    2,           -- New surrogate key
    123,         -- Same business key
    'Alice',
    'NYC',
    '2025-10-01',
    '9999-12-31',
    TRUE
);

UPDATE dim_customer
SET end_date = '2025-09-30',
    is_current = FALSE
WHERE customer_key = 1;

-- After
customer_key | customer_id | name  | city   | effective_date | end_date   | is_current
1            | 123         | Alice | Boston | 2020-01-01     | 2025-09-30 | FALSE
2            | 123         | Alice | NYC    | 2025-10-01     | 9999-12-31 | TRUE
```

**Querying:**
```sql
-- Current snapshot
SELECT * FROM dim_customer WHERE is_current = TRUE;

-- Historical query: "Where did Alice live on 2024-06-15?"
SELECT city
FROM dim_customer
WHERE customer_id = 123
  AND '2024-06-15' BETWEEN effective_date AND end_date;
```

**Use Case:**
- Customer demographics
- Product pricing
- Store locations

---

**Type 3: Add New Column (Track Limited History)**
```sql
CREATE TABLE dim_customer (
    customer_id BIGINT PRIMARY KEY,
    name VARCHAR(200),
    current_city VARCHAR(100),
    previous_city VARCHAR(100),  -- Only track one previous value
    city_change_date DATE
);

-- Alice moves Boston → NYC → LA
customer_id | name  | current_city | previous_city | city_change_date
123         | Alice | LA           | NYC           | 2025-10-01
```

**Use Case:**
- A/B test group assignments (current vs previous)
- Product versions

**Downside:** Only tracks last change

---

**Type 4: Add Mini-Dimension (Separate History Table)**
```sql
-- Main dimension (current only)
CREATE TABLE dim_customer (
    customer_id BIGINT PRIMARY KEY,
    name VARCHAR(200),
    current_city VARCHAR(100)
);

-- History table
CREATE TABLE dim_customer_history (
    history_key SERIAL PRIMARY KEY,
    customer_id BIGINT,
    city VARCHAR(100),
    effective_date DATE,
    end_date DATE
);

-- Fact table references both
CREATE TABLE fact_orders (
    order_id BIGINT PRIMARY KEY,
    customer_id BIGINT REFERENCES dim_customer,
    customer_history_key INT REFERENCES dim_customer_history,
    ...
);
```

**Use Case:** Rapidly changing attributes (demographics, segments)

---

**Type 6: Hybrid (1+2+3)**
```sql
CREATE TABLE dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id BIGINT,
    name VARCHAR(200),
    
    -- Type 1: Current value
    current_city VARCHAR(100),
    
    -- Type 2: Historical rows
    historical_city VARCHAR(100),
    effective_date DATE,
    end_date DATE,
    is_current BOOLEAN,
    
    -- Type 3: Previous value
    previous_city VARCHAR(100)
);
```

**Use Case:** Need both current and historical analysis

---

### **1.4 Conformed Dimensions**

**Problem:**  
Multiple data marts need to share dimensions

**Bad: Stovepipe Marts**
```
Sales Mart:
  dim_customer (id, name, city)
  
Marketing Mart:
  dim_customer (id, name, email, segment)  ← Different attributes!
  
Support Mart:
  dim_customer (id, name, phone)  ← Different attributes!

❌ Result: Inconsistent metrics across departments
```

**Good: Conformed Dimensions**
```
Shared Dimension:
  dim_customer_master (id, name, city, email, phone, segment)
  
All marts reference the same dimension:
  fact_sales → dim_customer_master
  fact_marketing_campaigns → dim_customer_master
  fact_support_tickets → dim_customer_master

✅ Result: Consistent metrics enterprise-wide
```

**Kimball's Enterprise Data Warehouse Bus Architecture:**

```
                  Conformed Dimensions
                           ↓
┌────────────────────────────────────────────────────────┐
│  Customer │ Product │ Date │ Location │ Promotion     │
│  Dimension│Dimension│ Dim  │ Dimension│ Dimension     │
└────────────────────────────────────────────────────────┘
       ↓         ↓        ↓        ↓          ↓
┌──────┴─────────┴────────┴────────┴──────────┴─────────┐
│                    Data Marts                          │
├────────────────────────────────────────────────────────┤
│  Retail Sales          │ Uses: Customer, Product, Date │
│  Inventory             │ Uses: Product, Location, Date │
│  Marketing Campaigns   │ Uses: Customer, Promotion     │
│  Customer Support      │ Uses: Customer, Product, Date │
└────────────────────────────────────────────────────────┘
```

**Building Conformed Dimensions:**

**Step 1: Define Master Dimension**
```sql
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
    segment VARCHAR(50),  -- From marketing
    lifetime_value_usd DECIMAL(10,2),  -- From sales
    support_tier VARCHAR(20),  -- From support
    
    -- SCD Type 2
    effective_date DATE,
    end_date DATE,
    is_current BOOLEAN
);
```

**Step 2: ETL Process**
```python
def build_conformed_dimension():
    # Extract from all source systems
    sales_customers = extract_from_sales_db()
    marketing_customers = extract_from_marketing_db()
    support_customers = extract_from_support_db()
    
    # Merge on business key (customer_id)
    merged = sales_customers.merge(
        marketing_customers, on='customer_id', how='outer'
    ).merge(
        support_customers, on='customer_id', how='outer'
    )
    
    # Handle conflicts (different source systems have different values)
    merged['name'] = merged['name_sales'].fillna(merged['name_marketing'])
    
    # Load to master dimension
    load_to_master_dimension(merged)
```

**Benefits:**
- ✅ Single source of truth
- ✅ Consistent metrics
- ✅ Cross-functional analysis

**Challenges:**
- Requires organizational alignment
- Different systems may have conflicting data
- Politics (who owns the dimension?)

---

## 📖 **2. Bill Inmon: Corporate Information Factory (1992)**

### **Context & Impact**

**Author:** Bill Inmon (the "Father of Data Warehousing")  
**Published:** 1992  
**Impact:** Defined enterprise data warehouse architecture

---

### **Core Thesis**

> **"A data warehouse is a subject-oriented, integrated, time-variant, and non-volatile collection of data in support of management's decision-making process."**

**Four Characteristics:**

**1. Subject-Oriented**
- Organized by business subject (Customer, Product, Order)
- Not by application or department

**Contrast:**
```
OLTP (Application-Oriented):
  - Order Entry System
  - Inventory Management System
  - CRM System

Data Warehouse (Subject-Oriented):
  - Customer subject area
  - Product subject area
  - Order subject area
```

---

**2. Integrated**
- Consolidates data from multiple sources
- Standardizes formats, naming, encoding

**Example:**
```
Source 1 (OLTP): gender = 'M', 'F'
Source 2 (CRM):  gender = '1', '2'
Source 3 (ERP):  gender = 'Male', 'Female'

Data Warehouse: gender = 'Male', 'Female' (standardized)
```

---

**3. Time-Variant**
- Every record has a timestamp
- Tracks history over long periods

**Contrast:**
```
OLTP: Current state only
  customer_id | name  | city
  123         | Alice | NYC  ← Overwrites previous value

Data Warehouse: Full history
  customer_id | name  | city   | valid_from  | valid_to
  123         | Alice | Boston | 2020-01-01  | 2025-09-30
  123         | Alice | NYC    | 2025-10-01  | 9999-12-31
```

---

**4. Non-Volatile**
- Data is read-only (no updates or deletes)
- Only inserts and queries

**Contrast:**
```
OLTP: Frequent updates
  UPDATE orders SET status = 'shipped' WHERE order_id = 123;

Data Warehouse: Append-only
  INSERT INTO fact_orders VALUES (123, 'shipped', CURRENT_TIMESTAMP);
```

---

### **2.1 Corporate Information Factory (CIF) Architecture**

**The Big Picture:**

```
┌────────────────────────────────────────────────────────┐
│                  OPERATIONAL SYSTEMS                   │
│  ERP │ CRM │ SCM │ OLTP │ SaaS │ Files                │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│                    ETL LAYER                           │
│  - Extract from sources                                │
│  - Transform (clean, standardize, integrate)           │
│  - Load to EDW                                         │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│        ENTERPRISE DATA WAREHOUSE (EDW)                 │
│        (3NF - Normalized, Subject-Oriented)            │
│                                                        │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│   │ Customer │  │ Product  │  │  Order   │           │
│   │ (3NF)    │  │  (3NF)   │  │  (3NF)   │           │
│   └──────────┘  └──────────┘  └──────────┘           │
│                                                        │
│   - Single source of truth                             │
│   - Integrated from all sources                        │
│   - Minimal redundancy                                 │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│                  DATA MARTS                            │
│  (Dimensional - Star Schema for BI)                    │
│                                                        │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐         │
│  │   Sales   │  │  Finance  │  │ Marketing │         │
│  │   Mart    │  │   Mart    │  │   Mart    │         │
│  └───────────┘  └───────────┘  └───────────┘         │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│                  BI TOOLS & REPORTS                    │
│  Tableau │ Power BI │ Looker │ Custom Apps            │
└────────────────────────────────────────────────────────┘
```

**Key Principles:**

**1. Build EDW First (Top-Down)**
```
❌ Kimball: Build data marts first, integrate later
✅ Inmon: Build EDW first, derive data marts
```

**Rationale:**
- EDW is single source of truth
- Data marts are derived views
- Changes to data marts don't affect EDW
- Future-proof (easy to add new marts)

---

**2. 3NF in EDW (Normalized)**

**Why normalize?**
- Eliminate redundancy
- Ensure data integrity
- Easier to integrate new sources

**Example:**

**3NF Tables:**
```sql
-- Customer table
CREATE TABLE customer (
    customer_id BIGINT PRIMARY KEY,
    name VARCHAR(200),
    email VARCHAR(200),
    city_id INT REFERENCES city
);

-- City table (separate to avoid redundancy)
CREATE TABLE city (
    city_id INT PRIMARY KEY,
    city_name VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100)
);

-- Order table
CREATE TABLE order (
    order_id BIGINT PRIMARY KEY,
    customer_id BIGINT REFERENCES customer,
    order_date DATE,
    total_amount DECIMAL(10,2)
);
```

**Denormalized (Kimball would do this in data mart):**
```sql
CREATE TABLE fact_orders (
    order_id BIGINT PRIMARY KEY,
    customer_id BIGINT,
    customer_name VARCHAR(200),  -- Denormalized!
    customer_email VARCHAR(200),  -- Denormalized!
    customer_city VARCHAR(100),  -- Denormalized!
    customer_state VARCHAR(100),  -- Denormalized!
    order_date DATE,
    total_amount DECIMAL(10,2)
);
```

---

**3. Atomic Data (Most Granular)**

**Inmon's Rule:**
> "Store data at the most atomic level. Aggregations can always be derived."

**Example:**
```sql
-- ✅ Atomic: One row per line item
CREATE TABLE order_line_item (
    line_item_id BIGINT PRIMARY KEY,
    order_id BIGINT,
    product_id BIGINT,
    quantity INT,
    price_usd DECIMAL(10,2)
);

-- ❌ Summarized: One row per order
CREATE TABLE order_summary (
    order_id BIGINT PRIMARY KEY,
    total_items INT,  -- Can't reconstruct individual items!
    total_amount DECIMAL(10,2)
);
```

---

### **2.2 Comparison: Inmon vs Kimball**

| Aspect | Inmon (CIF) | Kimball (Dimensional) |
|--------|-------------|----------------------|
| **Approach** | Top-down | Bottom-up |
| **Start** | Build EDW first | Build data marts first |
| **EDW Model** | 3NF (normalized) | Star schema (denormalized) |
| **Data Marts** | Derived from EDW | Built independently |
| **Time to Value** | Slow (6-12 months) | Fast (1-3 months) |
| **Flexibility** | High (easy to add marts) | Low (marts are siloed) |
| **Query Speed** | Slower (many joins) | Faster (denormalized) |
| **Storage** | Less (normalized) | More (redundant) |
| **Complexity** | High (many tables) | Low (star schema) |
| **Best For** | Enterprise-wide integration | Department-specific BI |

---

### **2.3 Modern Consensus: Hybrid Approach**

**What companies actually do in 2025:**

```
┌────────────────────────────────────────────────────────┐
│                  OPERATIONAL SYSTEMS                   │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│              DATA LAKE (Bronze Layer)                  │
│  - Raw data, schema-on-read                            │
│  - S3/GCS/ADLS, Parquet format                         │
│  - Inmon: Atomic, integrated                           │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│             CLEANED LAYER (Silver)                     │
│  - Deduplicated, standardized                          │
│  - Inmon: Subject-oriented (Customer, Product, Order)  │
│  - May be normalized (3NF) or semi-structured          │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│             CURATED LAYER (Gold)                       │
│  - Kimball: Star schema data marts                     │
│  - Aggregated, business-friendly                       │
│  - Optimized for BI tools                              │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│              BI TOOLS & ML MODELS                      │
└────────────────────────────────────────────────────────┘
```

**Best of both worlds:**
- **Inmon:** Atomic data lake (Bronze), integrated layer (Silver)
- **Kimball:** Star schema marts (Gold) for BI

---

## 📖 **3. Modern Data Stack: dbt & Analytics Engineering**

### **The Rise of Analytics Engineering (2016+)**

**Problem:**
- Traditional BI: Analysts write SQL, but code quality is poor
- Traditional Data Engineering: Engineers build pipelines, but don't understand business
- Gap: Who transforms raw data into analytics-ready datasets?

**Solution: Analytics Engineers**

**Role:**
- Write SQL transformations (like analysts)
- Use software engineering best practices (like engineers)
  - Version control (Git)
  - Testing (data quality checks)
  - CI/CD (automated deployments)
  - Documentation

---

### **3.1 dbt (Data Build Tool)**

**Developed:** Fishtown Analytics (2016), now dbt Labs  
**Impact:** Redefined how transformations are built

**Philosophy:**

```
Extract → Load → Transform (ELT)
          ↑
     Modern approach (vs ETL)
```

**Why ELT?**
- Cloud data warehouses are powerful (Snowflake, BigQuery, Redshift)
- Push transformations to warehouse (leverage compute)
- Analysts can write SQL (no Python/Spark needed)

---

### **3.2 dbt Workflow**

**Directory Structure:**
```
my_dbt_project/
├── models/
│   ├── staging/
│   │   ├── stg_orders.sql  ← Clean raw data
│   │   ├── stg_customers.sql
│   │   └── stg_products.sql
│   ├── intermediate/
│   │   └── int_order_items.sql  ← Business logic
│   └── marts/
│       ├── fct_orders.sql  ← Star schema fact
│       ├── dim_customers.sql  ← Star schema dimension
│       └── dim_products.sql
├── tests/
│   └── assert_order_totals_positive.sql
└── dbt_project.yml
```

**Example Model:**
```sql
-- models/staging/stg_orders.sql
WITH source AS (
    SELECT * FROM {{ source('ecommerce', 'raw_orders') }}
),

cleaned AS (
    SELECT
        order_id,
        customer_id,
        order_date,
        CAST(total_amount AS DECIMAL(10,2)) AS total_amount,
        status,
        
        -- Add metadata
        CURRENT_TIMESTAMP AS loaded_at
    FROM source
    WHERE order_date IS NOT NULL  -- Data quality
)

SELECT * FROM cleaned
```

**Ref Macro (Dependencies):**
```sql
-- models/marts/fct_orders.sql
SELECT
    o.order_id,
    o.customer_id,
    o.order_date,
    c.customer_name,  -- Join from staging model
    o.total_amount
FROM {{ ref('stg_orders') }} o  ← References another model
LEFT JOIN {{ ref('stg_customers') }} c
    ON o.customer_id = c.customer_id
```

**dbt automatically builds dependency graph:**
```
stg_orders ────┐
               ├─→ fct_orders
stg_customers ─┘
```

---

### **3.3 dbt Best Practices**

**1. Layered Architecture (Medallion)**

```
Staging (Bronze):
  - One model per source table
  - Minimal transformations (rename columns, fix types)
  - stg_orders.sql, stg_customers.sql

Intermediate (Silver):
  - Business logic transformations
  - Join staging models
  - int_order_items_with_revenue.sql

Marts (Gold):
  - Star schema for BI
  - Aggregated tables
  - fct_orders.sql, dim_customers.sql
```

**2. Tests**
```yaml
# models/schema.yml
models:
  - name: fct_orders
    columns:
      - name: order_id
        tests:
          - unique  # No duplicates
          - not_null  # No missing values
      
      - name: total_amount
        tests:
          - dbt_utils.expression_is_true:
              expression: ">= 0"  # No negative amounts
      
      - name: customer_id
        tests:
          - relationships:  # Foreign key check
              to: ref('dim_customers')
              field: customer_id
```

**3. Documentation**
```yaml
# models/schema.yml
models:
  - name: fct_orders
    description: "Order fact table with one row per order"
    columns:
      - name: order_id
        description: "Unique order identifier from Shopify"
      - name: total_amount
        description: "Total order amount in USD (includes tax and shipping)"
```

**Generate docs:**
```bash
dbt docs generate
dbt docs serve  # Opens browser with documentation
```

---

### **3.4 dbt + Kimball**

**dbt implements Kimball's methodology:**

**Staging Models = Extract + Clean**
```sql
-- stg_customers.sql
SELECT
    customer_id,
    TRIM(UPPER(name)) AS name,  -- Standardize
    email,
    city,
    created_at
FROM {{ source('ecommerce', 'raw_customers') }}
WHERE created_at IS NOT NULL
```

**Mart Models = Star Schema**
```sql
-- dim_customers.sql (SCD Type 2)
WITH source AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

add_scd_fields AS (
    SELECT
        {{ dbt_utils.surrogate_key(['customer_id', 'updated_at']) }} AS customer_key,
        customer_id,
        name,
        email,
        city,
        updated_at AS effective_date,
        LEAD(updated_at) OVER (
            PARTITION BY customer_id ORDER BY updated_at
        ) AS end_date,
        CASE 
            WHEN LEAD(updated_at) OVER (
                PARTITION BY customer_id ORDER BY updated_at
            ) IS NULL THEN TRUE
            ELSE FALSE
        END AS is_current
    FROM source
)

SELECT * FROM add_scd_fields
```

---

## 🎯 **4. Summary: The Evolution**

### **Timeline:**

**1992: Inmon**
- Enterprise Data Warehouse
- Top-down, 3NF
- Rigid, slow, comprehensive

**1996: Kimball**
- Dimensional Modeling
- Bottom-up, star schema
- Fast, flexible, business-focused

**2010s: Big Data**
- Hadoop, Spark
- Data lakes
- Schema-on-read

**2016+: Modern Data Stack**
- Cloud warehouses (Snowflake, BigQuery)
- ELT (Extract-Load-Transform)
- dbt (Analytics Engineering)
- Reverse ETL (warehouse → operational systems)

**2020s: Data Lakehouse**
- Delta Lake, Iceberg, Hudi
- Combines lake (flexibility) + warehouse (performance)
- ACID transactions on data lakes

---

### **Lessons for 2025:**

**1. Use Kimball for BI**
- Star schemas are still the best for BI tools
- Denormalize for query performance
- dbt makes this easy

**2. Use Inmon for Integration**
- Atomic data lake (Bronze/Silver layers)
- Normalized for flexibility
- Easy to add new use cases

**3. Embrace Modern Tools**
- Cloud warehouses (Snowflake, BigQuery, Databricks)
- dbt for transformations
- Git for version control
- CI/CD for deployments

**4. Focus on Business Value**
- Start with business questions
- Build incrementally (ship weekly, not yearly)
- Test data quality
- Document everything

---

## 📚 **Further Reading**

**Books:**
- Kimball, Ralph. *The Data Warehouse Toolkit* (3rd Ed., 2013)
- Inmon, William H. *Building the Data Warehouse* (4th Ed., 2005)
- Kleppmann, Martin. *Designing Data-Intensive Applications* (2017)

**Papers:**
- Kimball, Ralph. "The Data Warehouse Toolkit" (1996)
- Inmon, William H. "Building the Data Warehouse" (1992)

**Modern Resources:**
- dbt Documentation: https://docs.getdbt.com/
- Locally Optimistic: Analytics engineering blog
- Data Engineering Weekly: Newsletter

---

**Next:**
- 📖 [README](./README.md) - Module overview and learning paths

**Congratulations!** You now understand the theoretical foundations of data warehousing. 🎉
