# Week 3: SQL Deep Dive
## 🏗️ EXPERT - Advanced SQL & Database Internals

---

## 🎯 **Learning Objectives**

- Understand database storage engines (InnoDB, PostgreSQL)
- Master advanced window functions and SQL patterns
- Optimize distributed SQL queries
- Design sharding strategies
- Debug production query performance issues
- Answer FAANG-level SQL interview questions

---

## 🗄️ **1. Database Storage Internals**

### **How Databases Store Data on Disk**

**The Hierarchy:**
```
Database
  ↓
Table
  ↓
Pages (Blocks) - 8KB chunks
  ↓
Rows
  ↓
Columns
```

---

### **Storage Model 1: Row-Oriented (OLTP)**

**Used by:** MySQL, PostgreSQL, Oracle, SQL Server

**Layout on Disk:**
```
Page 1:
┌────────────────────────────────────────┐
│ Row 1: [id=1, name="Alice", age=30]    │
│ Row 2: [id=2, name="Bob", age=25]      │
│ Row 3: [id=3, name="Charlie", age=35]  │
│ ...                                    │
└────────────────────────────────────────┘

Page 2:
┌────────────────────────────────────────┐
│ Row 1001: [id=1001, name="Diana", ...]│
│ ...                                    │
└────────────────────────────────────────┘
```

**Characteristics:**
- Rows stored together (all columns adjacent)
- Good for: `SELECT * FROM users WHERE id = 123` (fetch entire row)
- Bad for: `SELECT AVG(age) FROM users` (must read all columns, even unused ones)

---

### **Storage Model 2: Column-Oriented (OLAP)**

**Used by:** Snowflake, BigQuery, Redshift, Parquet files

**Layout on Disk:**
```
id column:
┌────────────────────┐
│ 1, 2, 3, ..., 1000│
└────────────────────┘

name column:
┌──────────────────────────────────┐
│ "Alice", "Bob", "Charlie", ...   │
└──────────────────────────────────┘

age column:
┌────────────────────┐
│ 30, 25, 35, ...    │
└────────────────────┘
```

**Characteristics:**
- Columns stored separately
- Good for: `SELECT AVG(age) FROM users` (read only age column)
- Great compression (similar values grouped together)
- Bad for: `SELECT * FROM users WHERE id = 123` (must read all columns separately)

---

### **Example: Query Performance Difference**

**Query:** `SELECT AVG(revenue) FROM orders;` (10M rows, 20 columns)

**Row-Oriented:**
```
Read: 10M rows × 20 columns = 200M values
Disk I/O: 8 GB (all columns)
Time: 15 seconds
```

**Column-Oriented:**
```
Read: 10M rows × 1 column = 10M values
Disk I/O: 80 MB (only revenue column)
Compression: 80 MB → 10 MB (8x compression)
Time: 0.5 seconds ⚡
```

**Rule of Thumb:**
- **OLTP (row-oriented):** Fetch entire records (user profile, order details)
- **OLAP (column-oriented):** Aggregate specific columns (sum revenue, count users)

---

## 🔍 **2. B-Tree Internals**

### **How Indexes Work Under the Hood**

**B-Tree structure:**
```
                    [50, 100]
                   /    |    \
              /         |         \
        [10, 30]    [60, 80]    [110, 150]
       /   |   \    /  |  \      /   |   \
    [1-9][11-29]  [51-59]     [101-109]  ...
      ↓      ↓       ↓            ↓
    Rows   Rows    Rows         Rows
```

**Properties:**
- Balanced tree (all leaf nodes at same depth)
- Each node contains multiple keys (not binary!)
- Leaf nodes contain pointers to actual rows
- Height = O(log N), typically 3-4 levels for millions of rows

---

### **Index Lookup Example**

**Query:** `SELECT * FROM users WHERE id = 75;`

**Steps:**
```
Step 1: Start at root
  - Keys: [50, 100]
  - 75 is between 50 and 100
  - Go to middle child

Step 2: Middle node
  - Keys: [60, 80]
  - 75 is between 60 and 80
  - Go to middle child

Step 3: Leaf node
  - Keys: [70, 72, 75, 78]
  - Found 75!
  - Follow pointer to row

Total disk reads: 3 (root, internal node, leaf)
```

**Without index (full table scan):**
```
Read every page until we find id = 75
Total disk reads: 10,000+ pages
```

---

### **Why Indexes Speed Up Writes: The WAL**

**Myth:** "Indexes slow down writes."

**Reality:** Indexes slow down writes, but **Write-Ahead Logging (WAL)** helps.

**How WAL works:**
```
1. User: INSERT INTO users VALUES (...)

2. Database writes to WAL (sequential append):
   ┌─────────────────────────────┐
   │ WAL File (append-only)      │
   │ [INSERT user id=123 ...]    │ ← Fast sequential write!
   └─────────────────────────────┘

3. Return success to user immediately

4. Background process updates:
   - Table pages (random I/O)
   - Index pages (random I/O)
   
5. If crash occurs:
   - Replay WAL to recover uncommitted data
```

**Key insight:** WAL converts random writes → sequential writes (10x faster on HDDs).

---

## 🧠 **3. Query Optimizer Internals**

### **Cost-Based Optimization**

The optimizer estimates the **cost** of each query plan and chooses the cheapest.

**Cost formula (simplified):**
```
cost = (disk_page_reads × 1.0) + (CPU_operations × 0.01)
```

**Example:**

**Plan A: Full table scan**
```
Scan 10,000 pages (all rows)
Cost: 10,000 × 1.0 = 10,000
```

**Plan B: Index scan**
```
Scan 3 index pages (B-tree lookup)
+ Scan 100 table pages (matching rows)
Cost: (3 × 1.0) + (100 × 1.0) = 103
```

**Optimizer chooses Plan B (100x cheaper)!**

---

### **Statistics: How the Optimizer Knows**

**The optimizer maintains statistics:**

```sql
-- Table statistics
SELECT
    relname AS table_name,
    n_live_tup AS row_count,
    n_dead_tup AS dead_rows
FROM pg_stat_user_tables;
```

**Column statistics:**
```sql
-- Histogram of values
SELECT
    tablename,
    attname AS column_name,
    n_distinct AS unique_values,
    most_common_vals AS top_values
FROM pg_stats
WHERE tablename = 'users';
```

**Example:**
```
Table: users
Rows: 1,000,000

Column: country
Unique values: 195 (countries)
Most common values:
  - 'USA': 400,000 rows (40%)
  - 'India': 200,000 rows (20%)
  - 'UK': 100,000 rows (10%)
  - ...
```

**Query:** `SELECT * FROM users WHERE country = 'USA';`

**Optimizer thinks:**
```
Expected rows: 1M × 40% = 400,000 rows

Option A: Full table scan (read all 1M rows)
Cost: 10,000 disk pages

Option B: Index scan
Cost: 3 (index) + 4,000 (table pages for 400K rows) = 4,003

Decision: Use full scan! (Index scan would read almost as much data)
```

**Update statistics:**
```sql
-- Refresh statistics (run after large data changes)
ANALYZE users;
```

---

### **Query Hints (Force Optimizer)**

Sometimes the optimizer is wrong. You can force a plan:

**PostgreSQL:**
```sql
-- Disable sequential scans (force index use)
SET enable_seqscan = OFF;

SELECT * FROM users WHERE country = 'USA';

SET enable_seqscan = ON;  -- Re-enable
```

**MySQL:**
```sql
-- Force specific index
SELECT * FROM users FORCE INDEX (idx_country)
WHERE country = 'USA';

-- Ignore index
SELECT * FROM users IGNORE INDEX (idx_country)
WHERE country = 'USA';
```

**Warning:** Only use hints when you KNOW the optimizer is wrong (rare).

---

## 🌐 **4. Distributed SQL & Sharding**

### **The Problem: Single Server Limits**

**Scenario:** Your `orders` table has 10 billion rows.

**Single server issues:**
- Disk: 10TB (expensive, slow)
- RAM: 128GB (can't cache all indexes)
- Queries: Slow (must scan billions of rows)

**Solution:** **Sharding** - Split data across multiple servers.

---

### **Sharding Strategy 1: Horizontal Partitioning by Range**

**Example: Shard by date**

```
Server 1: orders_2020 (1B rows)
Server 2: orders_2021 (1.5B rows)
Server 3: orders_2022 (2B rows)
Server 4: orders_2023 (2.5B rows)
Server 5: orders_2024 (3B rows)
```

**Query routing:**
```sql
-- Query for 2024 data
SELECT * FROM orders WHERE order_date >= '2024-01-01';

-- Router sends query ONLY to Server 5
```

**Pros:**
- ✅ Simple routing logic
- ✅ Easy to add new shards (one per year)
- ✅ Queries within a range are fast

**Cons:**
- ❌ Unbalanced shards (2024 has more data than 2020)
- ❌ Cross-shard queries are slow (if querying multiple years)

---

### **Sharding Strategy 2: Horizontal Partitioning by Hash**

**Example: Shard by customer_id**

```
Shard function: shard_id = customer_id % 10

Server 1: customer_id % 10 = 0 (1B rows)
Server 2: customer_id % 10 = 1 (1B rows)
...
Server 10: customer_id % 10 = 9 (1B rows)
```

**Query routing:**
```sql
-- Query for customer 12345
SELECT * FROM orders WHERE customer_id = 12345;

-- Shard: 12345 % 10 = 5
-- Router sends query to Server 5
```

**Pros:**
- ✅ Evenly distributed data
- ✅ Fast lookups by customer_id

**Cons:**
- ❌ Queries without customer_id must scan ALL shards
  ```sql
  -- Slow (scatter-gather to all 10 shards)
  SELECT * FROM orders WHERE status = 'pending';
  ```

---

### **Sharding Strategy 3: Geo-Partitioning**

**Example: Shard by region**

```
Server US-West: customers in California, Oregon, Washington
Server US-East: customers in New York, Virginia, Florida
Server EU: customers in UK, France, Germany
Server APAC: customers in India, Singapore, Japan
```

**Pros:**
- ✅ Low latency (data close to users)
- ✅ Compliance (GDPR - EU data stays in EU)

**Cons:**
- ❌ Unbalanced shards (more users in US than EU)
- ❌ Cross-region queries are slow

---

### **Handling Cross-Shard Queries**

**Problem:** `SELECT COUNT(*) FROM orders;`  
This query needs data from ALL shards!

**Solution 1: Scatter-Gather**
```
1. Router sends query to all shards in parallel
2. Each shard executes query locally
   - Shard 1: COUNT = 1,000,000
   - Shard 2: COUNT = 1,200,000
   - ...
3. Router aggregates results
   - Total COUNT = 1,000,000 + 1,200,000 + ... = 10,000,000
```

**Solution 2: Pre-Aggregate**
```sql
-- Maintain summary table (updated nightly)
CREATE TABLE order_stats (
    shard_id INT,
    total_count BIGINT,
    total_revenue DECIMAL(20,2),
    last_updated TIMESTAMP
);

-- Fast query (reads summary, not raw data)
SELECT SUM(total_count) FROM order_stats;
```

---

## 🚀 **5. Advanced SQL Patterns**

### **Pattern 1: Running Aggregates (Running Total)**

**Problem:** Calculate cumulative revenue over time.

```sql
SELECT
    order_date,
    revenue,
    SUM(revenue) OVER (
        ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_revenue
FROM daily_sales;
```

**Result:**
```
order_date  | revenue | cumulative_revenue
------------|---------|-------------------
2024-01-01  | 1000    | 1000
2024-01-02  | 1500    | 2500
2024-01-03  | 1200    | 3700
```

---

### **Pattern 2: Moving Averages**

**Problem:** Calculate 7-day moving average.

```sql
SELECT
    order_date,
    revenue,
    AVG(revenue) OVER (
        ORDER BY order_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7day
FROM daily_sales;
```

**Explanation:**
- **6 PRECEDING:** Include 6 days before current row
- **CURRENT ROW:** Include current row
- **Total window:** 7 days (6 + 1)

---

### **Pattern 3: Top N per Group**

**Problem:** Find top 3 products by revenue in each category.

```sql
WITH ranked AS (
    SELECT
        category,
        product_name,
        revenue,
        ROW_NUMBER() OVER (
            PARTITION BY category
            ORDER BY revenue DESC
        ) AS rn
    FROM product_sales
)
SELECT category, product_name, revenue
FROM ranked
WHERE rn <= 3;
```

---

### **Pattern 4: Gap Detection (Find Missing Dates)**

**Problem:** Identify days with no sales.

```sql
WITH date_range AS (
    SELECT generate_series(
        '2024-01-01'::DATE,
        '2024-12-31'::DATE,
        '1 day'::INTERVAL
    )::DATE AS expected_date
)
SELECT
    dr.expected_date,
    COALESCE(s.revenue, 0) AS revenue
FROM date_range dr
LEFT JOIN daily_sales s ON dr.expected_date = s.order_date
WHERE s.order_date IS NULL;  -- Missing dates
```

---

### **Pattern 5: Unpivoting (Columns → Rows)**

**Problem:** Convert wide table to long format.

**Input:**
```
product_id | jan_sales | feb_sales | mar_sales
-----------|-----------|-----------|----------
1          | 1000      | 1500      | 1200
2          | 2000      | 2500      | 2200
```

**Query:**
```sql
SELECT
    product_id,
    month,
    sales
FROM products
CROSS JOIN LATERAL (
    VALUES
        ('jan', jan_sales),
        ('feb', feb_sales),
        ('mar', mar_sales)
) AS m(month, sales);
```

**Output:**
```
product_id | month | sales
-----------|-------|------
1          | jan   | 1000
1          | feb   | 1500
1          | mar   | 1200
2          | jan   | 2000
2          | feb   | 2500
2          | mar   | 2200
```

---

### **Pattern 6: Session Detection (Sessionization)**

**Problem:** Group user events into sessions (gap > 30 minutes = new session).

```sql
WITH event_gaps AS (
    SELECT
        user_id,
        event_timestamp,
        LAG(event_timestamp) OVER (
            PARTITION BY user_id
            ORDER BY event_timestamp
        ) AS prev_event_timestamp,
        CASE
            WHEN event_timestamp - LAG(event_timestamp) OVER (
                PARTITION BY user_id
                ORDER BY event_timestamp
            ) > INTERVAL '30 minutes' THEN 1
            ELSE 0
        END AS is_new_session
    FROM user_events
),
sessions AS (
    SELECT
        user_id,
        event_timestamp,
        SUM(is_new_session) OVER (
            PARTITION BY user_id
            ORDER BY event_timestamp
        ) AS session_id
    FROM event_gaps
)
SELECT
    user_id,
    session_id,
    MIN(event_timestamp) AS session_start,
    MAX(event_timestamp) AS session_end,
    COUNT(*) AS event_count
FROM sessions
GROUP BY user_id, session_id;
```

---

## 💡 **6. FAANG Interview Questions**

### **Question 1: Design a database schema for Twitter**

**Requirements:**
- Users can post tweets (280 chars)
- Users can follow other users
- Users can like tweets
- Timeline: Show tweets from users you follow

**Schema:**

```sql
-- Users table
CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_username ON users(username);

-- Tweets table
CREATE TABLE tweets (
    tweet_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    content VARCHAR(280) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_tweets_user_created ON tweets(user_id, created_at DESC);

-- Follows table (who follows whom)
CREATE TABLE follows (
    follower_id BIGINT REFERENCES users(user_id),
    followee_id BIGINT REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (follower_id, followee_id)
);
CREATE INDEX idx_follower ON follows(follower_id);
CREATE INDEX idx_followee ON follows(followee_id);

-- Likes table
CREATE TABLE likes (
    user_id BIGINT REFERENCES users(user_id),
    tweet_id BIGINT REFERENCES tweets(tweet_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, tweet_id)
);
CREATE INDEX idx_tweet_likes ON likes(tweet_id);
```

**Critical query: Get user timeline**

```sql
-- Naive approach (slow for users following 1000+ people)
SELECT
    t.tweet_id,
    t.content,
    u.username,
    t.created_at
FROM tweets t
JOIN users u ON t.user_id = u.user_id
WHERE t.user_id IN (
    SELECT followee_id
    FROM follows
    WHERE follower_id = 12345  -- Current user
)
ORDER BY t.created_at DESC
LIMIT 20;
```

**Optimized approach: Fan-out on write**

```sql
-- Pre-compute timeline (inserted when tweet is created)
CREATE TABLE timelines (
    user_id BIGINT REFERENCES users(user_id),
    tweet_id BIGINT REFERENCES tweets(tweet_id),
    created_at TIMESTAMP,
    PRIMARY KEY (user_id, created_at DESC, tweet_id)
);

-- When user tweets, insert into all followers' timelines
INSERT INTO timelines (user_id, tweet_id, created_at)
SELECT
    follower_id,
    12345,  -- New tweet ID
    CURRENT_TIMESTAMP
FROM follows
WHERE followee_id = 789;  -- User who tweeted

-- Timeline query (instant!)
SELECT
    t.content,
    u.username,
    tl.created_at
FROM timelines tl
JOIN tweets t ON tl.tweet_id = t.tweet_id
JOIN users u ON t.user_id = u.user_id
WHERE tl.user_id = 12345
ORDER BY tl.created_at DESC
LIMIT 20;
```

**Trade-off:**
- ✅ Fast reads (timeline query is simple lookup)
- ❌ Slow writes (must insert into N followers' timelines)
- Works well for celebrities (100M followers) → Use hybrid approach (fan-out for normal users, fan-in for celebrities)

---

### **Question 2: Find the second highest salary**

```sql
-- Solution 1: LIMIT OFFSET
SELECT salary
FROM employees
ORDER BY salary DESC
LIMIT 1 OFFSET 1;

-- Solution 2: Subquery
SELECT MAX(salary)
FROM employees
WHERE salary < (SELECT MAX(salary) FROM employees);

-- Solution 3: Window function
WITH ranked AS (
    SELECT
        salary,
        DENSE_RANK() OVER (ORDER BY salary DESC) AS rk
    FROM employees
)
SELECT DISTINCT salary
FROM ranked
WHERE rk = 2;
```

**Follow-up: What if there's no second highest?**

```sql
-- Returns NULL if only one distinct salary
SELECT salary
FROM employees
ORDER BY salary DESC
LIMIT 1 OFFSET 1;
```

---

### **Question 3: Find duplicate emails**

```sql
SELECT email, COUNT(*)
FROM users
GROUP BY email
HAVING COUNT(*) > 1;
```

**Follow-up: Delete duplicates, keep oldest**

```sql
WITH ranked AS (
    SELECT
        user_id,
        email,
        ROW_NUMBER() OVER (
            PARTITION BY email
            ORDER BY created_at ASC  -- Keep oldest
        ) AS rn
    FROM users
)
DELETE FROM users
WHERE user_id IN (
    SELECT user_id FROM ranked WHERE rn > 1
);
```

---

### **Question 4: Consecutive active days**

**Problem:** Find users who were active for at least 3 consecutive days.

```sql
WITH daily_activity AS (
    SELECT DISTINCT
        user_id,
        DATE(event_timestamp) AS activity_date
    FROM user_events
),
date_diff AS (
    SELECT
        user_id,
        activity_date,
        activity_date - ROW_NUMBER() OVER (
            PARTITION BY user_id
            ORDER BY activity_date
        ) * INTERVAL '1 day' AS grp
    FROM daily_activity
),
streaks AS (
    SELECT
        user_id,
        grp,
        COUNT(*) AS consecutive_days
    FROM date_diff
    GROUP BY user_id, grp
)
SELECT DISTINCT user_id
FROM streaks
WHERE consecutive_days >= 3;
```

**Explanation:**
- Subtract row number from date → Consecutive dates have same `grp`
- Example:
  ```
  activity_date | ROW_NUMBER | grp
  --------------|------------|----
  2024-01-01    | 1          | 2024-01-01 - 1 = 2023-12-31
  2024-01-02    | 2          | 2024-01-02 - 2 = 2023-12-31  ← Same grp!
  2024-01-03    | 3          | 2024-01-03 - 3 = 2023-12-31  ← Same grp!
  2024-01-05    | 4          | 2024-01-05 - 4 = 2024-01-01  ← Different grp
  ```

---

### **Question 5: Nth percentile**

**Problem:** Find the 90th percentile salary.

```sql
-- PostgreSQL
SELECT PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY salary)
FROM employees;

-- MySQL (no built-in percentile)
WITH ranked AS (
    SELECT
        salary,
        NTILE(100) OVER (ORDER BY salary) AS percentile
    FROM employees
)
SELECT MIN(salary)
FROM ranked
WHERE percentile >= 90;
```

---

### **Question 6: Running difference**

**Problem:** Calculate day-over-day revenue change.

```sql
SELECT
    order_date,
    revenue,
    revenue - LAG(revenue) OVER (ORDER BY order_date) AS daily_change,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY order_date)) * 100.0 /
        NULLIF(LAG(revenue) OVER (ORDER BY order_date), 0),
        2
    ) AS pct_change
FROM daily_sales;
```

---

### **Question 7: Cohort retention analysis**

**Problem:** What % of users active in Jan 2024 were still active in Feb 2024?

```sql
WITH jan_users AS (
    SELECT DISTINCT user_id
    FROM user_events
    WHERE event_timestamp >= '2024-01-01'
      AND event_timestamp < '2024-02-01'
),
feb_users AS (
    SELECT DISTINCT user_id
    FROM user_events
    WHERE event_timestamp >= '2024-02-01'
      AND event_timestamp < '2024-03-01'
)
SELECT
    COUNT(DISTINCT j.user_id) AS jan_users,
    COUNT(DISTINCT f.user_id) AS retained_users,
    ROUND(COUNT(DISTINCT f.user_id) * 100.0 / COUNT(DISTINCT j.user_id), 2) AS retention_rate
FROM jan_users j
LEFT JOIN feb_users f ON j.user_id = f.user_id;
```

---

### **Question 8: Cumulative sum with reset**

**Problem:** Calculate running total, but reset each month.

```sql
SELECT
    order_date,
    revenue,
    SUM(revenue) OVER (
        PARTITION BY DATE_TRUNC('month', order_date)
        ORDER BY order_date
    ) AS monthly_cumulative_revenue
FROM daily_sales;
```

---

### **Question 9: Median (without built-in function)**

```sql
WITH ranked AS (
    SELECT
        salary,
        ROW_NUMBER() OVER (ORDER BY salary) AS rn,
        COUNT(*) OVER () AS total_count
    FROM employees
)
SELECT AVG(salary) AS median
FROM ranked
WHERE rn IN (
    FLOOR((total_count + 1) / 2.0),
    CEIL((total_count + 1) / 2.0)
);
```

---

### **Question 10: Self-join to find manager hierarchy**

**Problem:** List all employees with their manager's name.

```sql
SELECT
    e.employee_id,
    e.name AS employee_name,
    m.name AS manager_name
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.employee_id;
```

**Follow-up: Find employees earning more than their manager**

```sql
SELECT
    e.name AS employee,
    e.salary AS employee_salary,
    m.name AS manager,
    m.salary AS manager_salary
FROM employees e
JOIN employees m ON e.manager_id = m.employee_id
WHERE e.salary > m.salary;
```

---

## 🎯 **Summary**

**Key Takeaways:**

1. **Storage models matter:** Row-oriented for OLTP, column-oriented for OLAP
2. **B-Tree indexes:** O(log N) lookups, critical for performance
3. **Query optimizer:** Uses statistics and cost-based optimization
4. **Sharding strategies:** Range, hash, geo-partitioning
5. **Advanced patterns:** Window functions, CTEs, recursive queries, sessionization

**Production Tips:**
- Always run EXPLAIN ANALYZE on slow queries
- Update statistics after large data changes (ANALYZE)
- Monitor index bloat (B-trees can become unbalanced over time)
- Partition large tables (> 10M rows)
- Pre-aggregate for common queries

---

**Next:** [WHITEPAPERS](./WHITEPAPERS.md) - Database research papers and academic foundations

**Previous:** [INTERMEDIATE](./INTERMEDIATE.md)

**Master Roadmap:** [00-MASTER-ROADMAP.md](../../00-MASTER-ROADMAP.md)
