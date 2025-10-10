# Week 3: SQL Deep Dive
## 🔨 INTERMEDIATE - Query Optimization & Performance Tuning

---

## 🎯 **Learning Objectives**

- Read and interpret EXPLAIN plans
- Optimize slow queries systematically
- Master advanced indexing strategies
- Understand join algorithms (Nested Loop, Hash, Merge)
- Write performant CTEs and subqueries
- Implement partitioning for large tables

---

## 🔍 **1. EXPLAIN: Your X-Ray Vision for Queries**

### **What is EXPLAIN?**

> **EXPLAIN shows you the database's execution plan - how it will find and return data.**

Think of it like asking a GPS:  
- **Without EXPLAIN:** "Take me to the airport" → Just follow directions
- **With EXPLAIN:** "Show me the route first" → See highways vs backroads, traffic, ETA

---

### **Basic EXPLAIN Syntax**

**PostgreSQL:**
```sql
EXPLAIN
SELECT * FROM orders WHERE customer_id = 123;
```

**Output:**
```
Seq Scan on orders  (cost=0.00..1825.00 rows=100 width=56)
  Filter: (customer_id = 123)
```

**What this means:**
- **Seq Scan:** Sequential scan (full table scan) ❌ Slow!
- **cost=0.00..1825.00:** Estimated cost (lower = better)
- **rows=100:** Expected rows returned
- **width=56:** Average row size in bytes

---

### **EXPLAIN ANALYZE: See Actual Performance**

```sql
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 123;
```

**Output:**
```
Seq Scan on orders  (cost=0.00..1825.00 rows=100 width=56) 
                    (actual time=0.123..45.678 rows=97 loops=1)
  Filter: (customer_id = 123)
  Rows Removed by Filter: 9903
Planning Time: 0.234 ms
Execution Time: 45.901 ms
```

**Key differences:**
- **actual time:** Real execution time (not estimate)
- **actual rows=97:** Actual rows returned (vs estimated 100)
- **Rows Removed:** How many rows were scanned but filtered out (9,903!)

---

### **Reading EXPLAIN Plans**

#### **Good Plan (Uses Index):**
```sql
CREATE INDEX idx_customer ON orders(customer_id);

EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 123;
```

**Output:**
```
Index Scan using idx_customer on orders
  (cost=0.29..8.31 rows=100 width=56)
  (actual time=0.012..0.034 rows=97 loops=1)
  Index Cond: (customer_id = 123)
Execution Time: 0.056 ms  ← 800x faster!
```

**What changed:**
- **Seq Scan** → **Index Scan** ✅
- **45.901 ms** → **0.056 ms** ⚡
- No "Rows Removed" (index went straight to matching rows)

---

### **Common Operations in EXPLAIN Plans**

| Operation | What It Means | Speed |
|-----------|---------------|-------|
| **Seq Scan** | Full table scan (reads every row) | ❌ Slow |
| **Index Scan** | Uses index to find rows | ✅ Fast |
| **Index Only Scan** | Gets data from index only (no table lookup) | ⚡ Fastest |
| **Bitmap Index Scan** | Uses multiple indexes, combines results | ✅ Fast |
| **Nested Loop Join** | For each row in A, scan B (good for small tables) | 🟡 Depends |
| **Hash Join** | Build hash table from smaller table, probe with larger | ✅ Fast (large tables) |
| **Merge Join** | Sort both tables, merge (good for sorted data) | ✅ Fast (sorted data) |
| **Sort** | Sorts rows (expensive for large datasets) | ❌ Slow |
| **Aggregate** | GROUP BY, COUNT, SUM, etc. | 🟡 Depends |

---

## 🚀 **2. Query Optimization Techniques**

### **Technique 1: Add Indexes for WHERE Clauses**

**Before (Slow):**
```sql
-- 10M rows, no index
SELECT * FROM orders
WHERE customer_id = 123 AND status = 'shipped';

-- Execution Time: 3500 ms (full table scan)
```

**After (Fast):**
```sql
-- Add composite index
CREATE INDEX idx_customer_status ON orders(customer_id, status);

SELECT * FROM orders
WHERE customer_id = 123 AND status = 'shipped';

-- Execution Time: 2 ms ⚡
```

**Why it works:**
- Index filters on both columns at once
- Database skips 99.999% of rows

---

### **Technique 2: SELECT Only What You Need**

**Bad:**
```sql
-- Fetches all columns (even large JSONB fields)
SELECT * FROM products
WHERE category = 'Electronics';

-- Reads 500 MB from disk
```

**Good:**
```sql
-- Only fetch required columns
SELECT id, name, price FROM products
WHERE category = 'Electronics';

-- Reads 50 MB from disk (10x less I/O)
```

**Bonus: Index-Only Scans**
```sql
-- Create covering index (includes all queried columns)
CREATE INDEX idx_category_covering ON products(category, id, name, price);

SELECT id, name, price FROM products
WHERE category = 'Electronics';

-- Database reads ONLY the index (not the table)
-- Execution Time: 10 ms → 1 ms ⚡
```

---

### **Technique 3: Avoid Functions on Indexed Columns**

**Bad (Can't Use Index):**
```sql
CREATE INDEX idx_email ON users(email);

-- ❌ Function on indexed column breaks index
SELECT * FROM users
WHERE LOWER(email) = 'alice@example.com';

-- Still does full table scan!
```

**Good:**
```sql
-- Store lowercase email, or use functional index
CREATE INDEX idx_email_lower ON users(LOWER(email));

SELECT * FROM users
WHERE LOWER(email) = 'alice@example.com';

-- Now uses index ✅
```

---

### **Technique 4: Rewrite Subqueries as JOINs**

**Bad (Subquery):**
```sql
-- For each order, run a subquery (N+1 query problem)
SELECT
    order_id,
    (SELECT name FROM customers WHERE id = orders.customer_id) AS customer_name
FROM orders;

-- Runs 1 + N queries (1 for orders, N for each customer)
```

**Good (JOIN):**
```sql
-- One query with join
SELECT
    o.order_id,
    c.name AS customer_name
FROM orders o
JOIN customers c ON o.customer_id = c.id;

-- Runs 1 query total ✅
```

---

### **Technique 5: Use EXISTS Instead of IN for Large Lists**

**Slow:**
```sql
-- IN clause with subquery
SELECT * FROM orders
WHERE customer_id IN (
    SELECT id FROM customers WHERE country = 'USA'
);

-- May not optimize well
```

**Fast:**
```sql
-- EXISTS checks for existence, stops at first match
SELECT * FROM orders o
WHERE EXISTS (
    SELECT 1 FROM customers c
    WHERE c.id = o.customer_id AND c.country = 'USA'
);

-- Can short-circuit (stop early)
```

---

## 🔗 **3. Join Algorithms**

### **How Databases Join Tables**

When you write:
```sql
SELECT *
FROM orders o
JOIN customers c ON o.customer_id = c.id;
```

The database chooses one of these algorithms:

---

### **Algorithm 1: Nested Loop Join**

**How it works:**
```python
for order in orders:  # Outer loop
    for customer in customers:  # Inner loop
        if order.customer_id == customer.id:
            yield (order, customer)
```

**Complexity:** O(N × M) where N = orders, M = customers

**Example:**
```
Orders: 1000 rows
Customers: 100 rows
Total comparisons: 1000 × 100 = 100,000
```

**When to use:**
- Small tables (< 1000 rows)
- Inner table has an index on join key

**EXPLAIN output:**
```
Nested Loop  (cost=0.29..1234.56 rows=1000 width=128)
  ->  Seq Scan on orders o
  ->  Index Scan using idx_customer_id on customers c
        Index Cond: (id = o.customer_id)
```

---

### **Algorithm 2: Hash Join**

**How it works:**
```python
# Step 1: Build hash table from smaller table
hash_table = {}
for customer in customers:
    hash_table[customer.id] = customer

# Step 2: Probe hash table with larger table
for order in orders:
    if order.customer_id in hash_table:
        yield (order, hash_table[order.customer_id])
```

**Complexity:** O(N + M) - linear!

**Example:**
```
Orders: 1M rows
Customers: 100K rows
Total operations: 1M + 100K = 1.1M (vs 100B for nested loop!)
```

**When to use:**
- Large tables
- No index on join key
- Enough memory for hash table

**EXPLAIN output:**
```
Hash Join  (cost=3500.00..85000.00 rows=1000000 width=128)
  Hash Cond: (o.customer_id = c.id)
  ->  Seq Scan on orders o
  ->  Hash  (cost=2500.00..2500.00 rows=100000 width=64)
        ->  Seq Scan on customers c
```

---

### **Algorithm 3: Merge Join**

**How it works:**
```python
# Precondition: Both tables sorted by join key
orders_sorted = sorted(orders, key=lambda x: x.customer_id)
customers_sorted = sorted(customers, key=lambda x: x.id)

# Step through both in parallel
i, j = 0, 0
while i < len(orders) and j < len(customers):
    if orders[i].customer_id == customers[j].id:
        yield (orders[i], customers[j])
        i += 1
    elif orders[i].customer_id < customers[j].id:
        i += 1
    else:
        j += 1
```

**Complexity:** O(N log N + M log M) for sorting, then O(N + M) for merge

**When to use:**
- Both tables already sorted (or have indexes)
- Large tables with clustered indexes

**EXPLAIN output:**
```
Merge Join  (cost=0.85..12345.67 rows=1000000 width=128)
  Merge Cond: (o.customer_id = c.id)
  ->  Index Scan using idx_orders_customer on orders o
  ->  Index Scan using idx_customers_id on customers c
```

---

## 📊 **4. Advanced Indexing Strategies**

### **Strategy 1: Covering Indexes**

**Goal:** Get all data from index without touching the table.

**Example:**
```sql
-- Common query
SELECT product_id, product_name, price
FROM products
WHERE category = 'Electronics'
  AND stock > 0;

-- Regular index (needs table lookup)
CREATE INDEX idx_category ON products(category);

-- Covering index (includes all queried columns)
CREATE INDEX idx_category_covering ON products(category, stock, product_id, product_name, price);

-- Now query reads ONLY the index (Index Only Scan)
```

**EXPLAIN before:**
```
Index Scan using idx_category on products
  (cost=0.42..8500.00 rows=10000 width=128)
  Filter: (stock > 0)
```

**EXPLAIN after:**
```
Index Only Scan using idx_category_covering on products
  (cost=0.42..500.00 rows=10000 width=128)
  Index Cond: (category = 'Electronics' AND stock > 0)
```

**Trade-off:**
- ✅ Faster queries (no table lookup)
- ❌ Larger index size
- ❌ Slower writes (more index updates)

---

### **Strategy 2: Partial Indexes**

**Goal:** Index only a subset of rows to save space.

**Example:**
```sql
-- Most queries filter on active users
SELECT * FROM users WHERE status = 'active' AND city = 'NYC';

-- Regular index (indexes ALL users, even inactive)
CREATE INDEX idx_city ON users(city);  -- 10M rows

-- Partial index (only active users)
CREATE INDEX idx_city_active ON users(city)
WHERE status = 'active';  -- 2M rows (80% smaller!)
```

**Benefits:**
- Smaller index (faster, less disk I/O)
- Faster writes (fewer rows to index)
- Still fast for filtered queries

---

### **Strategy 3: Expression Indexes (Functional Indexes)**

**Goal:** Index computed values.

**Example:**
```sql
-- Common query: case-insensitive email lookup
SELECT * FROM users
WHERE LOWER(email) = 'alice@example.com';

-- Regular index won't work (function on column)
CREATE INDEX idx_email ON users(email);  -- ❌ Not used!

-- Expression index (indexes LOWER(email))
CREATE INDEX idx_email_lower ON users(LOWER(email));  -- ✅ Used!
```

**Another example: Date ranges**
```sql
-- Query by month
SELECT * FROM orders
WHERE EXTRACT(MONTH FROM order_date) = 10;

-- Index on month
CREATE INDEX idx_order_month ON orders(EXTRACT(MONTH FROM order_date));
```

---

### **Strategy 4: Multi-Column Index Ordering**

**Rule:** Most selective column first.

**Example:**
```sql
-- Table: 10M orders
-- - customer_id: 100K unique values (selectivity: 1%)
-- - status: 5 unique values ('pending', 'shipped', etc.) (selectivity: 20%)

-- ✅ Good: customer_id first (more selective)
CREATE INDEX idx_customer_status ON orders(customer_id, status);

-- ❌ Bad: status first (less selective)
CREATE INDEX idx_status_customer ON orders(status, customer_id);
```

**Why?**
```sql
SELECT * FROM orders
WHERE customer_id = 123 AND status = 'shipped';

-- Good index filters to ~100 rows (customer_id) → ~10 rows (status)
-- Bad index filters to ~2M rows (status) → ~1 row (customer_id)
```

---

## 🧩 **5. Common Table Expressions (CTEs)**

### **What are CTEs?**

**CTEs** (WITH clause) are named temporary result sets.

**Basic syntax:**
```sql
WITH cte_name AS (
    SELECT ... FROM ...
)
SELECT * FROM cte_name;
```

---

### **Use Case 1: Improve Readability**

**Without CTE (Ugly):**
```sql
SELECT
    orders.order_id,
    orders.total,
    customers.name
FROM orders
JOIN customers ON orders.customer_id = customers.id
WHERE orders.order_id IN (
    SELECT order_id
    FROM order_items
    WHERE product_id IN (
        SELECT product_id
        FROM products
        WHERE category = 'Electronics'
    )
);
```

**With CTE (Clean):**
```sql
WITH electronic_products AS (
    SELECT product_id
    FROM products
    WHERE category = 'Electronics'
),
electronic_orders AS (
    SELECT DISTINCT order_id
    FROM order_items
    WHERE product_id IN (SELECT product_id FROM electronic_products)
)
SELECT
    o.order_id,
    o.total,
    c.name
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.order_id IN (SELECT order_id FROM electronic_orders);
```

---

### **Use Case 2: Reuse CTEs**

```sql
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', order_date) AS month,
        SUM(total) AS revenue
    FROM orders
    GROUP BY month
)
SELECT
    month,
    revenue,
    revenue - LAG(revenue) OVER (ORDER BY month) AS month_over_month_growth,
    AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS rolling_3month_avg
FROM monthly_revenue;
```

---

### **Use Case 3: Recursive CTEs (Hierarchies)**

**Example: Organization chart**
```sql
WITH RECURSIVE org_hierarchy AS (
    -- Base case: CEO (no manager)
    SELECT
        employee_id,
        name,
        manager_id,
        1 AS level
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- Recursive case: employees reporting to current level
    SELECT
        e.employee_id,
        e.name,
        e.manager_id,
        oh.level + 1
    FROM employees e
    JOIN org_hierarchy oh ON e.manager_id = oh.employee_id
)
SELECT * FROM org_hierarchy
ORDER BY level, employee_id;
```

**Result:**
```
employee_id | name    | manager_id | level
------------|---------|------------|------
1           | Alice   | NULL       | 1  (CEO)
2           | Bob     | 1          | 2  (Reports to Alice)
3           | Charlie | 1          | 2  (Reports to Alice)
4           | Diana   | 2          | 3  (Reports to Bob)
5           | Eve     | 2          | 3  (Reports to Bob)
```

---

### **CTE Performance: Materialized vs Inline**

**PostgreSQL 12+:**
```sql
-- Inline (default): CTE is expanded into main query
WITH recent_orders AS (
    SELECT * FROM orders WHERE order_date > '2024-01-01'
)
SELECT * FROM recent_orders;

-- Materialized: CTE is executed once, results cached
WITH recent_orders AS MATERIALIZED (
    SELECT * FROM orders WHERE order_date > '2024-01-01'
)
SELECT * FROM recent_orders
UNION ALL
SELECT * FROM recent_orders;  -- Reuses cached results
```

---

## 🗂️ **6. Partitioning Large Tables**

### **What is Partitioning?**

> **Partitioning splits a large table into smaller, more manageable pieces.**

**Analogy:** Instead of one giant filing cabinet, you have separate drawers for each year.

---

### **When to Partition?**

**Partition when:**
- Table > 10 million rows
- Queries filter on a specific column (date, region, status)
- Want to archive/delete old data easily

**Don't partition when:**
- Table is small (< 1M rows)
- No clear partition key
- Queries span many partitions

---

### **Types of Partitioning**

#### **1. Range Partitioning (Most Common)**

**Use case:** Time-series data (orders, events, logs)

```sql
-- Parent table
CREATE TABLE orders (
    order_id BIGINT,
    customer_id BIGINT,
    order_date DATE,
    total DECIMAL(10,2)
) PARTITION BY RANGE (order_date);

-- Child partitions (one per year)
CREATE TABLE orders_2022 PARTITION OF orders
    FOR VALUES FROM ('2022-01-01') TO ('2023-01-01');

CREATE TABLE orders_2023 PARTITION OF orders
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE orders_2024 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

**Query automatically uses correct partition:**
```sql
-- Only scans orders_2024 partition
SELECT * FROM orders
WHERE order_date BETWEEN '2024-06-01' AND '2024-06-30';
```

**EXPLAIN:**
```
Seq Scan on orders_2024
  (cost=0.00..1000.00 rows=5000 width=128)
  Filter: (order_date >= '2024-06-01' AND order_date <= '2024-06-30')

-- Skips orders_2022 and orders_2023 entirely!
```

---

#### **2. List Partitioning**

**Use case:** Partition by categorical values (country, status, region)

```sql
CREATE TABLE users (
    user_id BIGINT,
    name VARCHAR(200),
    country VARCHAR(50)
) PARTITION BY LIST (country);

CREATE TABLE users_usa PARTITION OF users
    FOR VALUES IN ('USA');

CREATE TABLE users_europe PARTITION OF users
    FOR VALUES IN ('UK', 'France', 'Germany', 'Spain');

CREATE TABLE users_asia PARTITION OF users
    FOR VALUES IN ('India', 'China', 'Japan');
```

---

#### **3. Hash Partitioning**

**Use case:** Even distribution when no natural partition key

```sql
CREATE TABLE sessions (
    session_id BIGINT,
    user_id BIGINT,
    created_at TIMESTAMP
) PARTITION BY HASH (user_id);

-- Create 4 partitions (evenly distributed by hash(user_id))
CREATE TABLE sessions_0 PARTITION OF sessions
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);

CREATE TABLE sessions_1 PARTITION OF sessions
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);

CREATE TABLE sessions_2 PARTITION OF sessions
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);

CREATE TABLE sessions_3 PARTITION OF sessions
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

---

### **Partition Maintenance**

**Add new partition:**
```sql
-- Add 2025 partition
CREATE TABLE orders_2025 PARTITION OF orders
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

**Drop old partition (archive):**
```sql
-- Delete all 2022 data instantly (no DELETE statement needed)
DROP TABLE orders_2022;
```

**Detach for archival:**
```sql
-- Keep data but remove from main table
ALTER TABLE orders DETACH PARTITION orders_2022;

-- Now orders_2022 is a standalone table
-- Can move to slower storage or export
```

---

## 🎯 **7. Hands-On: Optimizing a Slow Query**

### **Scenario**

You're a data engineer at an e-commerce company. Analysts complain this query is slow:

```sql
SELECT
    customers.name,
    COUNT(*) AS order_count,
    SUM(orders.total) AS total_spent
FROM customers
JOIN orders ON customers.id = orders.customer_id
WHERE orders.status = 'completed'
  AND orders.order_date >= '2024-01-01'
GROUP BY customers.name
ORDER BY total_spent DESC
LIMIT 10;
```

**Current performance:** 45 seconds ❌

**Your goal:** Get it under 1 second ✅

---

### **Step 1: Run EXPLAIN ANALYZE**

```sql
EXPLAIN ANALYZE
SELECT ...;
```

**Output:**
```
Sort  (cost=850000.00..850010.00 rows=4000 width=64)
      (actual time=44523.123..44523.145 rows=10 loops=1)
  ->  HashAggregate  (cost=840000.00..845000.00 rows=50000 width=64)
                      (actual time=44520.234..44522.567 rows=95342 loops=1)
        ->  Hash Join  (cost=35000.00..820000.00 rows=2000000 width=56)
                        (actual time=234.567..42000.123 rows=1987654 loops=1)
              Hash Cond: (orders.customer_id = customers.id)
              ->  Seq Scan on orders  (cost=0.00..750000.00 rows=2000000 width=32)
                                      (actual time=0.012..38000.234 rows=5000000 loops=1)
                    Filter: (status = 'completed' AND order_date >= '2024-01-01')
                    Rows Removed by Filter: 3012346  ← Problem!
              ->  Hash  (cost=25000.00..25000.00 rows=100000 width=24)
                         (actual time=230.123..230.124 rows=100000 loops=1)
                    ->  Seq Scan on customers
```

**Problems identified:**
1. **Seq Scan on orders** (38 seconds!) - No index on status or order_date
2. **Rows Removed by Filter: 3M** - Scanning 5M rows to get 2M

---

### **Step 2: Add Indexes**

```sql
-- Index on filtered columns
CREATE INDEX idx_orders_status_date ON orders(status, order_date);

-- Index on join key (if not already a primary key)
CREATE INDEX idx_orders_customer ON orders(customer_id);
```

---

### **Step 3: Re-run EXPLAIN ANALYZE**

```sql
EXPLAIN ANALYZE
SELECT ...;
```

**Output:**
```
Sort  (cost=12000.00..12010.00 rows=4000 width=64)
      (actual time=850.123..850.145 rows=10 loops=1)
  ->  HashAggregate  (cost=11000.00..11500.00 rows=50000 width=64)
                      (actual time=848.234..849.567 rows=95342 loops=1)
        ->  Hash Join  (cost=3500.00..10000.00 rows=2000000 width=56)
                        (actual time=12.567..650.123 rows=1987654 loops=1)
              Hash Cond: (orders.customer_id = customers.id)
              ->  Index Scan using idx_orders_status_date on orders
                    (cost=0.43..5000.00 rows=2000000 width=32)
                    (actual time=0.012..450.234 rows=1987654 loops=1)
                    Index Cond: (status = 'completed' AND order_date >= '2024-01-01')
              ->  Hash  (cost=25000.00..25000.00 rows=100000 width=24)
                         (actual time=230.123..230.124 rows=100000 loops=1)
                    ->  Seq Scan on customers
Execution Time: 850.234 ms  ← 53x faster! ⚡
```

**Improvement:** 45 seconds → 850 ms ✅

---

### **Step 4: Further optimization (Covering Index)**

```sql
-- Include all queried columns in index
CREATE INDEX idx_orders_covering ON orders(status, order_date, customer_id, total);

-- Now database doesn't need to look up the table at all
```

**Final performance:** 120 ms ⚡⚡

---

## 📝 **Interview Questions**

### **Question 1: Explain the difference between OLTP and OLAP databases.**

<details>
<summary>Answer</summary>

**OLTP (Online Transaction Processing):**
- Purpose: Run applications (e.g., e-commerce checkout)
- Queries: Simple, fast lookups (SELECT * FROM users WHERE id = 123)
- Writes: Frequent (INSERT/UPDATE/DELETE)
- Schema: Normalized (3NF)
- Examples: PostgreSQL, MySQL

**OLAP (Online Analytical Processing):**
- Purpose: Answer business questions (e.g., monthly revenue by region)
- Queries: Complex, scan millions of rows (aggregations, JOINs)
- Writes: Rare (batch ETL)
- Schema: Denormalized (star schema)
- Examples: Snowflake, BigQuery, Redshift

</details>

---

### **Question 2: When would you use a hash join vs nested loop join?**

<details>
<summary>Answer</summary>

**Nested Loop Join:**
- **When:** Small tables (< 1000 rows) OR inner table has index on join key
- **How:** For each row in outer table, scan inner table
- **Complexity:** O(N × M)

**Hash Join:**
- **When:** Large tables (> 100K rows) with no indexes
- **How:** Build hash table from smaller table, probe with larger table
- **Complexity:** O(N + M)
- **Requirement:** Enough memory for hash table

</details>

---

### **Question 3: How would you optimize this query?**

```sql
SELECT * FROM orders
WHERE YEAR(order_date) = 2024 AND MONTH(order_date) = 10;
```

<details>
<summary>Answer</summary>

**Problems:**
1. Functions on indexed column prevent index usage
2. SELECT * fetches unnecessary columns

**Optimized:**
```sql
-- Rewrite to use date range (index-friendly)
SELECT order_id, customer_id, total
FROM orders
WHERE order_date >= '2024-10-01'
  AND order_date < '2024-11-01';

-- Add index
CREATE INDEX idx_order_date ON orders(order_date);
```

</details>

---

### **Question 4: Explain what a covering index is and when to use it.**

<details>
<summary>Answer</summary>

**Covering Index:**
An index that includes all columns needed by a query, so the database can satisfy the query from the index alone without accessing the table.

**Example:**
```sql
-- Query
SELECT product_id, name, price
FROM products
WHERE category = 'Electronics';

-- Covering index
CREATE INDEX idx_covering ON products(category, product_id, name, price);

-- Result: Index Only Scan (no table lookup needed)
```

**When to use:**
- Frequent queries that access same columns
- Read-heavy workloads
- Query performance is critical

**Trade-offs:**
- Larger index size
- Slower writes (more index maintenance)

</details>

---

### **Question 5: How do you handle a table with 1 billion rows?**

<details>
<summary>Answer</summary>

**Strategies:**

1. **Partitioning:**
   - Range partitioning by date (one partition per month/year)
   - List partitioning by region/country
   - Hash partitioning for even distribution

2. **Indexing:**
   - Create indexes on frequently filtered columns
   - Use partial indexes (only index active rows)
   - Covering indexes for common queries

3. **Archival:**
   - Move old data to separate archive tables
   - Drop old partitions after retention period

4. **Denormalization:**
   - Pre-aggregate common queries into summary tables
   - Refresh summary tables nightly

5. **Sharding:**
   - Split across multiple database servers
   - Route queries to correct shard

</details>

---

**Next:** [EXPERT](./EXPERT.md) - Advanced query patterns, database internals, and distributed SQL

**Previous:** [BEGINNER](./BEGINNER.md)

**Master Roadmap:** [00-MASTER-ROADMAP.md](../../00-MASTER-ROADMAP.md)
