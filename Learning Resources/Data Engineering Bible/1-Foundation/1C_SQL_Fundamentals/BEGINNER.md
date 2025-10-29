# Week 3: SQL Deep Dive
## 🌱 BEGINNER - SQL for Data Engineers (The Fun Way!)

---

## 🎯 **What You'll Learn**

- How databases execute queries (behind the scenes)
- Why some queries are fast and others are slow
- Indexes: The "table of contents" for databases
- OLTP vs OLAP: Why your app database ≠ analytics database
- Window functions: The superpower for analytics

---

## 📖 **The Library Analogy: How Databases Work**

### **Your Database is a Giant Library**

Imagine you walk into a library with **10 million books** (rows of data).

**You ask:** *"Find me all books by Stephen King published after 2000."*

**Two librarians approach:**

---

### **Librarian A: "The Brute Force Searcher"**

```
🧑 "I'll check EVERY book in the library!"

Step 1: Pick up Book 1 → Check author → Check year → Not a match
Step 2: Pick up Book 2 → Check author → Check year → Not a match
Step 3: Pick up Book 3 → Check author → Check year → MATCH! (Add to cart)
...
Step 10,000,000: Finally done! 🥵

Time: 3 days
```

**In SQL terms:** This is a **FULL TABLE SCAN**.

```sql
-- Slow query (scans all 10M rows)
SELECT * FROM books
WHERE author = 'Stephen King' AND year > 2000;
```

---

### **Librarian B: "The Index Master"**

```
🧑 "Let me check the card catalog!"

Step 1: Look up "Stephen King" in Author Index
        → Points to shelves 42, 87, 103
        
Step 2: Go to Shelf 42 → Grab all books → Check year > 2000
        Go to Shelf 87 → Grab all books → Check year > 2000
        Go to Shelf 103 → Grab all books → Check year > 2000

Time: 5 minutes ⚡
```

**In SQL terms:** This uses an **INDEX**.

```sql
-- Fast query (uses index on author column)
CREATE INDEX idx_author ON books(author);

SELECT * FROM books
WHERE author = 'Stephen King' AND year > 2000;
```

---

**The Lesson:**

> **Indexes are like "card catalogs" that help databases skip directly to relevant data instead of checking every row.**

---

## 🔍 **1. How Databases Execute Queries**

### **The Query Execution Pipeline**

When you run a SQL query, the database goes through these steps:

```
┌──────────────────────────────────────────────┐
│  1. PARSER                                   │
│  - Check syntax: Is this valid SQL?          │
│  - "SELECT * FORM users" → ❌ Error!         │
└──────────────────────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────┐
│  2. QUERY OPTIMIZER                          │
│  - Find the fastest way to get results       │
│  - Should we use an index?                   │
│  - Which table to scan first?                │
│  - Cost estimation: Plan A vs Plan B         │
└──────────────────────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────┐
│  3. EXECUTION PLAN                           │
│  - Step-by-step instructions                 │
│  - "Scan index X → Join table Y → Filter Z"  │
└──────────────────────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────┐
│  4. EXECUTOR                                 │
│  - Actually read data from disk              │
│  - Return results to user                    │
└──────────────────────────────────────────────┘
```

---

### **Example: Behind the Scenes**

**Query:**
```sql
SELECT customers.name, SUM(orders.total)
FROM customers
JOIN orders ON customers.id = orders.customer_id
WHERE orders.status = 'completed'
GROUP BY customers.name;
```

**What the optimizer thinks:**

```
Option 1: "Scan all customers, then join orders"
  - Read 1M customers
  - For each customer, find their orders (1M × 5 lookups = 5M reads)
  - Cost: HIGH 💸

Option 2: "Scan completed orders first, then join customers"
  - Read only completed orders (100K rows)
  - Join to customers (100K × 1 lookup = 100K reads)
  - Cost: LOW ✅

Decision: Use Option 2!
```

**The optimizer is like a GPS:**  
It finds the fastest route, even if you didn't ask for it.

---

## 📇 **2. Indexes: The Superpower**

### **What is an Index?**

**Think of a textbook:**
- Without an index: Flip through 500 pages to find "MapReduce"
- With an index: Turn to page 789 (check index at back)

**Indexes in databases:**
- Extra data structure that points to rows
- Trade-off: Faster reads, slower writes

---

### **Types of Indexes**

#### **1. B-Tree Index (Most Common)**

**Visual:**
```
         [M]
        /   \
    [D, G]  [P, T]
    /  |  \    |  \
  [A] [E] [J] [N] [U]
   ↓   ↓   ↓   ↓   ↓
 Rows Rows Rows Rows Rows
```

**How it works:**
- Sorted tree structure
- Fast lookups: O(log N)
- Good for: `=`, `>`, `<`, `BETWEEN`, `LIKE 'abc%'`

**Example:**
```sql
CREATE INDEX idx_email ON users(email);

-- Fast (uses index)
SELECT * FROM users WHERE email = 'alice@example.com';

-- Fast (uses index)
SELECT * FROM users WHERE email LIKE 'alice%';

-- Slow (can't use index - wildcard at start)
SELECT * FROM users WHERE email LIKE '%alice%';
```

---

#### **2. Hash Index**

**Visual:**
```
Hash('alice@example.com') = 42
  → Points to Row 1337

Hash('bob@example.com') = 87
  → Points to Row 9001
```

**How it works:**
- Hash function converts value → bucket number
- Ultra-fast lookups: O(1)
- Limitation: Only works for `=` (not `>`, `<`, `LIKE`)

**Example:**
```sql
CREATE INDEX idx_user_id USING HASH ON users(id);

-- Fast (exact match)
SELECT * FROM users WHERE id = 12345;

-- Can't use hash index (range query)
SELECT * FROM users WHERE id > 1000;
```

---

#### **3. Composite Index (Multi-Column)**

**When to use:**  
Your queries filter on multiple columns together.

**Example:**
```sql
-- Your common query
SELECT * FROM orders
WHERE customer_id = 123 AND status = 'completed';

-- Create composite index
CREATE INDEX idx_customer_status ON orders(customer_id, status);
```

**Column order matters!**

```sql
-- Index on (customer_id, status)

-- ✅ Uses index (filters on first column)
SELECT * FROM orders WHERE customer_id = 123;

-- ✅ Uses index (filters on both columns)
SELECT * FROM orders WHERE customer_id = 123 AND status = 'completed';

-- ❌ Can't use index efficiently (skips first column)
SELECT * FROM orders WHERE status = 'completed';
```

**Rule of Thumb:**  
Put the most selective column first (the one that filters out the most rows).

---

### **When NOT to Use Indexes**

**Indexes aren't free:**

1. **Writes become slower**
   ```sql
   INSERT INTO users VALUES (...);
   
   -- Database must update:
   -- 1. The table itself
   -- 2. Index on email
   -- 3. Index on created_at
   -- 4. Index on city
   -- ... (every index!)
   ```

2. **Small tables don't need indexes**
   ```sql
   -- If table has 100 rows, full scan is instant
   -- Index overhead is wasted
   ```

3. **Low selectivity columns**
   ```sql
   -- Bad index (only 2 unique values)
   CREATE INDEX idx_gender ON users(gender);  -- 'M' or 'F'
   
   -- Database will scan ~50% of table anyway!
   ```

---

## 🏢 **3. OLTP vs OLAP: Two Different Worlds**

### **OLTP: Online Transaction Processing**

**Purpose:** Run your app (process orders, user logins, payments)

**Characteristics:**
- **Fast writes** (many INSERT/UPDATE/DELETE)
- **Simple queries** (lookup by ID)
- **Small transactions** (1-100 rows at a time)
- **Normalized schema** (3NF - no redundancy)

**Example:**
```sql
-- E-commerce app (OLTP)
INSERT INTO orders (customer_id, total, status)
VALUES (123, 99.99, 'pending');

UPDATE inventory
SET quantity = quantity - 1
WHERE product_id = 456;

SELECT * FROM users WHERE id = 789;
```

**Database:** PostgreSQL, MySQL, SQL Server

---

### **OLAP: Online Analytical Processing**

**Purpose:** Answer business questions (revenue trends, customer analytics)

**Characteristics:**
- **Fast reads** (complex queries scanning millions of rows)
- **Few writes** (batch ETL once a day)
- **Complex queries** (JOINs, aggregations, GROUP BY)
- **Denormalized schema** (star schema - optimized for reads)

**Example:**
```sql
-- Data warehouse (OLAP)
SELECT
    DATE_TRUNC('month', order_date) AS month,
    product_category,
    SUM(total) AS revenue,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM fact_orders
JOIN dim_products ON fact_orders.product_id = dim_products.product_id
JOIN dim_date ON fact_orders.date_id = dim_date.date_id
WHERE dim_date.year = 2024
GROUP BY month, product_category
ORDER BY revenue DESC;
```

**Database:** Snowflake, BigQuery, Redshift, Databricks

---

### **Comparison Table**

| Aspect | OLTP (App DB) | OLAP (Data Warehouse) |
|--------|---------------|------------------------|
| **Purpose** | Run application | Answer questions |
| **Users** | Thousands (customers) | Tens (analysts) |
| **Queries** | Simple (SELECT by ID) | Complex (aggregations) |
| **Data Volume** | MB to GB | TB to PB |
| **Schema** | Normalized (3NF) | Denormalized (star) |
| **Writes** | Frequent | Rare (batch ETL) |
| **Reads** | Few rows | Millions of rows |
| **Latency** | Milliseconds | Seconds to minutes |
| **Example** | "Get user profile" | "Monthly revenue by region" |

---

### **The Coffee Shop Analogy**

**OLTP = Cashier:**
- Fast transactions: "One latte, please!" → Done in 10 seconds
- Many customers per hour
- Simple operations (take order, charge card)

**OLAP = Accountant:**
- Slow analysis: "What's our total revenue this quarter by product and location?"
- Runs once per month
- Complex calculations (aggregations, trends, forecasts)

---

## 🪟 **4. Window Functions: Analytics Superpowers**

### **The Problem Window Functions Solve**

**Scenario:** Show each employee's salary and the average salary in their department.

**Bad approach (without window functions):**
```sql
-- Requires self-join (slow and ugly)
SELECT
    e.name,
    e.salary,
    dept_avg.avg_salary
FROM employees e
JOIN (
    SELECT department_id, AVG(salary) AS avg_salary
    FROM employees
    GROUP BY department_id
) dept_avg ON e.department_id = dept_avg.department_id;
```

**Good approach (with window functions):**
```sql
SELECT
    name,
    salary,
    AVG(salary) OVER (PARTITION BY department_id) AS dept_avg_salary
FROM employees;
```

✨ **One query, no join!**

---

### **What are Window Functions?**

> **Window functions perform calculations across a "window" of rows related to the current row.**

**Think of it like Excel:**
- You have a column of numbers
- You want to show a running total next to each row
- Window functions do this in SQL!

---

### **Common Window Functions**

#### **1. ROW_NUMBER(): Assign row numbers**

```sql
SELECT
    name,
    department,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) AS salary_rank
FROM employees;
```

**Result:**
```
name     | department | salary  | salary_rank
---------|------------|---------|------------
Alice    | Engineering| 150000  | 1
Bob      | Engineering| 120000  | 2
Charlie  | Sales      | 110000  | 3
Diana    | Sales      | 105000  | 4
```

---

#### **2. RANK(): Rank with ties**

```sql
SELECT
    name,
    department,
    salary,
    RANK() OVER (ORDER BY salary DESC) AS salary_rank
FROM employees;
```

**Result:**
```
name     | department | salary  | salary_rank
---------|------------|---------|------------
Alice    | Engineering| 150000  | 1
Bob      | Engineering| 120000  | 2
Charlie  | Sales      | 120000  | 2  ← Same salary = same rank
Diana    | Sales      | 105000  | 4  ← Skips rank 3!
```

---

#### **3. PARTITION BY: Group within window**

```sql
-- Rank employees within each department
SELECT
    name,
    department,
    salary,
    RANK() OVER (
        PARTITION BY department  -- Separate ranking per dept
        ORDER BY salary DESC
    ) AS dept_rank
FROM employees;
```

**Result:**
```
name     | department  | salary  | dept_rank
---------|-------------|---------|----------
Alice    | Engineering | 150000  | 1  ← Rank 1 in Engineering
Bob      | Engineering | 120000  | 2  ← Rank 2 in Engineering
Charlie  | Sales       | 110000  | 1  ← Rank 1 in Sales
Diana    | Sales       | 105000  | 2  ← Rank 2 in Sales
```

**Notice:** Rankings restart for each department!

---

#### **4. Running Totals (SUM OVER)**

```sql
-- Calculate cumulative revenue
SELECT
    order_date,
    revenue,
    SUM(revenue) OVER (ORDER BY order_date) AS cumulative_revenue
FROM daily_sales;
```

**Result:**
```
order_date  | revenue | cumulative_revenue
------------|---------|-------------------
2024-01-01  | 1000    | 1000
2024-01-02  | 1500    | 2500  (1000 + 1500)
2024-01-03  | 1200    | 3700  (2500 + 1200)
```

---

#### **5. LAG/LEAD: Access previous/next rows**

```sql
-- Compare today's revenue to yesterday's
SELECT
    order_date,
    revenue,
    LAG(revenue) OVER (ORDER BY order_date) AS yesterday_revenue,
    revenue - LAG(revenue) OVER (ORDER BY order_date) AS daily_change
FROM daily_sales;
```

**Result:**
```
order_date  | revenue | yesterday_revenue | daily_change
------------|---------|-------------------|-------------
2024-01-01  | 1000    | NULL              | NULL
2024-01-02  | 1500    | 1000              | +500
2024-01-03  | 1200    | 1500              | -300
```

---

### **Real-World Use Case: Top 3 Products per Category**

```sql
WITH ranked_products AS (
    SELECT
        category,
        product_name,
        revenue,
        ROW_NUMBER() OVER (
            PARTITION BY category
            ORDER BY revenue DESC
        ) AS rank
    FROM product_sales
)
SELECT
    category,
    product_name,
    revenue
FROM ranked_products
WHERE rank <= 3  -- Top 3 per category
ORDER BY category, rank;
```

**Result:**
```
category      | product_name | revenue
--------------|--------------|--------
Electronics   | iPhone 15    | 500000  (Rank 1)
Electronics   | MacBook Pro  | 450000  (Rank 2)
Electronics   | AirPods      | 300000  (Rank 3)
Clothing      | Nike Shoes   | 200000  (Rank 1)
Clothing      | Levi's Jeans | 180000  (Rank 2)
Clothing      | Adidas Shirt | 150000  (Rank 3)
```

---

## 🎨 **5. Query Patterns for Data Engineers**

### **Pattern 1: Deduplication**

**Problem:** Your data has duplicates (common in ETL pipelines).

```sql
-- Remove duplicates, keep most recent record
WITH ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY user_id
            ORDER BY updated_at DESC
        ) AS rn
    FROM user_events
)
SELECT *
FROM ranked
WHERE rn = 1;  -- Keep only the most recent
```

---

### **Pattern 2: Gap Detection**

**Problem:** Find missing dates in time-series data.

```sql
WITH date_range AS (
    SELECT generate_series(
        '2024-01-01'::DATE,
        '2024-12-31'::DATE,
        '1 day'::INTERVAL
    )::DATE AS expected_date
)
SELECT expected_date
FROM date_range
LEFT JOIN daily_sales ON expected_date = order_date
WHERE order_date IS NULL;  -- Dates with no data
```

---

### **Pattern 3: Pivoting (Rows → Columns)**

**Problem:** Convert rows to columns for reporting.

```sql
-- Convert monthly revenue into columns
SELECT
    product_name,
    SUM(CASE WHEN month = 1 THEN revenue ELSE 0 END) AS jan_revenue,
    SUM(CASE WHEN month = 2 THEN revenue ELSE 0 END) AS feb_revenue,
    SUM(CASE WHEN month = 3 THEN revenue ELSE 0 END) AS mar_revenue
FROM monthly_product_sales
GROUP BY product_name;
```

---

## 🎯 **Summary: Key Takeaways**

1. **Indexes are like library card catalogs** - They help databases skip to relevant data instead of scanning everything.

2. **Query optimizer finds the fastest route** - Like a GPS, it evaluates multiple plans and picks the best one.

3. **OLTP ≠ OLAP** - Your app database is optimized for fast writes; your data warehouse is optimized for complex reads.

4. **Window functions are analytics superpowers** - They let you do rankings, running totals, and comparisons without complex joins.

5. **Choose the right index type** - B-tree for ranges, hash for exact matches, composite for multi-column filters.

---

## ✅ **Practice Exercises**

### **Exercise 1: Create an index**
```sql
-- Given this slow query, add an index
SELECT * FROM orders
WHERE customer_id = 123 AND status = 'shipped';

-- Your task: What index would you create?
```

<details>
<summary>Solution</summary>

```sql
CREATE INDEX idx_customer_status ON orders(customer_id, status);
```
</details>

---

### **Exercise 2: Window function**
```sql
-- Find the 2nd highest salary in each department
SELECT
    department,
    name,
    salary
FROM employees
WHERE _____  -- Fill in the blank
```

<details>
<summary>Solution</summary>

```sql
WITH ranked AS (
    SELECT
        department,
        name,
        salary,
        RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS rk
    FROM employees
)
SELECT department, name, salary
FROM ranked
WHERE rk = 2;
```
</details>

---

**Next:** [INTERMEDIATE](./INTERMEDIATE.md) - Query optimization, EXPLAIN plans, and advanced indexing strategies

**Master Roadmap:** [00-MASTER-ROADMAP.md](../../00-MASTER-ROADMAP.md)
