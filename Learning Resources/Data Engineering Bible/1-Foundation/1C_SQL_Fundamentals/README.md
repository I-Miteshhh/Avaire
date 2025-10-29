# Week 3: SQL Deep Dive
## 📖 Module Overview

---

## 🎯 **What You'll Learn**

This module teaches you **advanced SQL techniques** and **database internals** that separate senior data engineers from juniors. You'll master query optimization, understand how databases work under the hood, and learn to design systems that scale to billions of rows.

**By the end of this week, you will:**
- ✅ Read and optimize EXPLAIN plans
- ✅ Design effective indexing strategies
- ✅ Understand OLTP vs OLAP architectures
- ✅ Master advanced window functions and CTEs
- ✅ Implement table partitioning for large datasets
- ✅ Debug production query performance issues
- ✅ Answer FAANG-level SQL interview questions

---

## 📚 **Learning Path**

### **Choose Your Level:**

```
🌱 BEGINNER (2-3 hours)
├─ Start here if: You know basic SQL (SELECT, WHERE, JOIN)
├─ Format: Library analogy, visual diagrams, simple examples
└─ Outcome: Understand indexes, OLTP vs OLAP, window functions

🔨 INTERMEDIATE (4-5 hours)
├─ Start here if: You want to optimize slow queries
├─ Format: EXPLAIN plans, hands-on query tuning, real scenarios
└─ Outcome: Debug and fix production performance issues

🏗️ EXPERT (6-8 hours)
├─ Start here if: You want to design databases at scale
├─ Format: Database internals, sharding strategies, system design
└─ Outcome: Architect distributed SQL systems, ace FAANG interviews

📄 WHITEPAPERS (3-4 hours)
├─ Start here if: You want theoretical foundations
├─ Format: Codd, Gray, Brewer papers digested
└─ Outcome: Understand ACID, CAP theorem, query optimization theory
```

---

## 🗺️ **Module Roadmap**

### **Phase 1: Fundamentals** (BEGINNER)

**Topics:**
- How databases execute queries (parser → optimizer → executor)
- Index types (B-tree, hash, composite)
- OLTP vs OLAP (when to use which)
- Window functions (rankings, running totals, moving averages)

**Key Analogies:**
```
Database = Library
- Index = Card catalog (find books quickly)
- Full table scan = Check every book on every shelf
- Query optimizer = GPS (finds fastest route)

OLTP = Cashier (fast transactions)
OLAP = Accountant (complex analysis)
```

**Time:** 2-3 hours  
**Prerequisites:** Basic SQL (SELECT, WHERE, JOIN, GROUP BY)

---

### **Phase 2: Performance Tuning** (INTERMEDIATE)

**Topics:**
- Reading EXPLAIN plans (Seq Scan, Index Scan, Hash Join)
- Query optimization techniques
  - Adding indexes
  - Selecting only needed columns
  - Avoiding functions on indexed columns
  - Rewriting subqueries as JOINs
- Join algorithms (Nested Loop, Hash, Merge)
- Advanced indexing (covering, partial, expression indexes)
- CTEs and recursive queries
- Table partitioning (range, list, hash)

**Hands-On Exercise:**
```sql
-- Optimize this slow query (45 seconds → <1 second)
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

-- Steps:
1. Run EXPLAIN ANALYZE
2. Identify bottlenecks (Seq Scan, missing indexes)
3. Add indexes
4. Re-run and measure improvement
```

**Time:** 4-5 hours  
**Prerequisites:** SQL proficiency, basic understanding of indexes

---

### **Phase 3: Database Internals** (EXPERT)

**Topics:**
- Storage models (row-oriented vs column-oriented)
- B-tree internals (how indexes work on disk)
- Write-Ahead Logging (WAL)
- Query optimizer cost calculations
- Sharding strategies (range, hash, geo-partitioning)
- Advanced SQL patterns
  - Running aggregates
  - Moving averages
  - Top N per group
  - Gap detection
  - Sessionization
- 10 FAANG interview questions with solutions

**Real-World Systems:**
```
Twitter Schema Design:
- Users, Tweets, Follows, Likes tables
- Fan-out on write for timeline generation
- Hybrid approach for celebrities

Sharding at Scale:
- 10 billion rows across 10 servers
- Hash sharding by customer_id
- Scatter-gather for cross-shard queries
```

**Time:** 6-8 hours  
**Prerequisites:** Database concepts, distributed systems knowledge

---

### **Phase 4: Theoretical Foundations** (WHITEPAPERS)

**Topics:**
- **Codd (1970):** Relational model, normalization
- **Gray (1981):** ACID properties, transaction isolation levels
- **Brewer (2000):** CAP theorem (Consistency vs Availability)
- **Selinger (1979):** Cost-based query optimization
- **Stonebraker (2005):** Column stores for OLAP

**Key Concepts:**
```
ACID:
- Atomicity: All or nothing
- Consistency: Valid state transitions
- Isolation: Concurrent transactions don't interfere
- Durability: Committed data persists

CAP Theorem:
- Can't have Consistency + Availability during network partition
- Choose CP (MongoDB, HBase) or AP (Cassandra, DynamoDB)
```

**Time:** 3-4 hours  
**Prerequisites:** Database fundamentals from BEGINNER/INTERMEDIATE

---

## 🎓 **Learning Outcomes**

### **By Level:**

**BEGINNER:**
- [ ] Explain how indexes speed up queries
- [ ] Identify when to use OLTP vs OLAP databases
- [ ] Write window functions (ROW_NUMBER, RANK, LAG)
- [ ] Understand full table scan vs index scan

**INTERMEDIATE:**
- [ ] Read and interpret EXPLAIN plans
- [ ] Optimize slow queries (add indexes, rewrite queries)
- [ ] Choose correct join algorithm (nested loop vs hash vs merge)
- [ ] Partition large tables (> 10M rows)
- [ ] Write complex CTEs and recursive queries

**EXPERT:**
- [ ] Explain B-tree internals and disk I/O
- [ ] Design sharding strategy for 10B rows
- [ ] Implement advanced SQL patterns (sessionization, cohort analysis)
- [ ] Debug production query performance issues
- [ ] Answer FAANG SQL interview questions

**WHITEPAPERS:**
- [ ] Explain ACID properties with examples
- [ ] Debate CP vs AP systems (CAP theorem)
- [ ] Understand cost-based query optimization
- [ ] Compare row-oriented vs column-oriented storage
- [ ] Trace evolution from OLTP to OLAP to data lakehouses

---

## 🛠️ **Hands-On Exercises**

### **Exercise 1: Add the Right Index** (BEGINNER)
```sql
-- Slow query
SELECT * FROM orders
WHERE customer_id = 123 AND status = 'shipped';

-- Task: Create an index to speed this up
-- Question: Single-column or composite? Which column first?
```

<details>
<summary>Solution</summary>

```sql
-- Composite index (customer_id first - more selective)
CREATE INDEX idx_customer_status ON orders(customer_id, status);

-- Why this order?
-- customer_id is more selective (filters to ~100 orders)
-- status is less selective (20% of orders are 'shipped')
```
</details>

---

### **Exercise 2: Optimize with EXPLAIN** (INTERMEDIATE)
```sql
-- Run EXPLAIN ANALYZE on this query
EXPLAIN ANALYZE
SELECT
    p.product_name,
    SUM(oi.quantity) AS total_sold
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
WHERE oi.order_date >= '2024-01-01'
GROUP BY p.product_name
ORDER BY total_sold DESC
LIMIT 10;

-- Tasks:
-- 1. Identify bottlenecks (Seq Scan? Missing index?)
-- 2. Add appropriate indexes
-- 3. Measure performance improvement
```

---

### **Exercise 3: Window Functions** (INTERMEDIATE)
```sql
-- Find the 2nd highest salary in each department
-- Without using LIMIT or subqueries
```

<details>
<summary>Solution</summary>

```sql
WITH ranked AS (
    SELECT
        department,
        employee_name,
        salary,
        DENSE_RANK() OVER (
            PARTITION BY department
            ORDER BY salary DESC
        ) AS rk
    FROM employees
)
SELECT department, employee_name, salary
FROM ranked
WHERE rk = 2;
```
</details>

---

### **Exercise 4: Sharding Design** (EXPERT)
**Scenario:** You have an `orders` table with 10 billion rows growing by 10M/day.

**Tasks:**
1. Choose a sharding strategy (range, hash, or geo)
2. Define shard key
3. Explain how to handle this query:
   ```sql
   SELECT COUNT(*) FROM orders WHERE status = 'pending';
   ```
4. What happens when you add a new shard?

<details>
<summary>Solution</summary>

**Sharding Strategy:** Hash by `customer_id`

**Reasoning:**
- Evenly distributes data
- Most queries filter by customer_id (fast)

**Shard key:** `customer_id % 10` (10 shards)

**Handling COUNT query:**
```
1. Scatter: Send query to all 10 shards in parallel
2. Each shard: SELECT COUNT(*) WHERE status = 'pending'
3. Gather: Sum results from all shards
4. Return total count

Note: Slower than single-customer queries (must hit all shards)
```

**Adding new shard:**
```
1. Change shard function: customer_id % 11
2. Rebalance data (expensive!)
3. Alternative: Use consistent hashing to minimize data movement
```
</details>

---

## 📊 **Success Metrics**

### **Knowledge Checks:**

**After BEGINNER:**
- ✅ "What's the difference between OLTP and OLAP?"
- ✅ "Why are indexes like a book's table of contents?"
- ✅ "Write a query to find running total using window functions"

**After INTERMEDIATE:**
- ✅ "Explain an EXPLAIN plan for a slow query"
- ✅ "When would you use a covering index?"
- ✅ "Partition a 100M row table by date range"

**After EXPERT:**
- ✅ "Design a Twitter-like schema with timeline fan-out"
- ✅ "Explain how B-trees enable O(log N) lookups"
- ✅ "Choose sharding strategy for 10B row e-commerce table"

**After WHITEPAPERS:**
- ✅ "Explain ACID with a bank transfer example"
- ✅ "Why can't we have Consistency + Availability during network partition?"
- ✅ "Compare row stores vs column stores for OLAP"

---

## 🔗 **Connections to Other Weeks**

### **Prerequisite:**
- **Week 1: MapReduce** - Understanding distributed processing helps with sharding
- **Week 2: ETL & Data Modeling** - Star schemas are optimized for OLAP queries

### **Builds Toward:**
- **Week 4: Apache Spark** - Distributed SQL with Spark SQL
- **Week 5: Data Warehousing** - Columnar storage (Parquet, BigQuery internals)
- **Weeks 6-10: Kafka** - Stream processing with SQL (KSQL, Flink SQL)

---

## 🧭 **Navigation**

**Current Module:**
- 🌱 [BEGINNER](./BEGINNER.md) - Library analogy, indexes, OLTP vs OLAP, window functions
- 🔨 [INTERMEDIATE](./INTERMEDIATE.md) - EXPLAIN plans, query optimization, partitioning
- 🏗️ [EXPERT](./EXPERT.md) - Database internals, sharding, advanced SQL patterns
- 📄 [WHITEPAPERS](./WHITEPAPERS.md) - Codd, Gray, Brewer, Selinger papers

**Other Weeks:**
- ⬅️ [Week 2: ETL & Data Modeling](../1B_ETL_Basics/README.md)
- ➡️ Week 4: Apache Spark Fundamentals (Coming next!)
- 🏠 [Master Roadmap](../../00-MASTER-ROADMAP.md)

---

## 💡 **Pro Tips**

### **For BEGINNERS:**
1. **Use visual tools** - pgAdmin, DBeaver to see EXPLAIN plans graphically
2. **Start small** - Practice on 1000-row tables first
3. **Draw diagrams** - Sketch B-tree structures, star schemas

### **For INTERMEDIATE:**
1. **Always EXPLAIN ANALYZE** - Before and after optimization
2. **Measure, don't guess** - Use actual execution time, not intuition
3. **Profile in production** - `pg_stat_statements` for PostgreSQL

### **For EXPERT:**
1. **Read source code** - PostgreSQL, MySQL are open source
2. **Benchmark everything** - Use pgbench, sysbench for load testing
3. **Know your hardware** - SSD vs HDD, RAM size affect query plans

### **For WHITEPAPERS:**
1. **Read papers sequentially** - Codd (1970) → Gray (1981) → Brewer (2000)
2. **Summarize in your own words** - Teach concepts to others
3. **Connect to practice** - How does your database implement ACID?

---

## 🚀 **Next Steps**

### **Just Finished This Module?**

**Option 1: Practice**
- Solve LeetCode SQL problems (Medium → Hard)
- Optimize queries in your own projects
- Profile a production database

**Option 2: Go Deeper**
- Read "Designing Data-Intensive Applications" (Kleppmann)
- Watch CMU Database Course videos (Andy Pavlo)
- Explore PostgreSQL internals documentation

**Option 3: Move Forward**
- Continue to **Week 4: Apache Spark Fundamentals**
- Skip to **Week 5: Data Warehousing** for columnar storage
- Jump to **Week 6: Kafka** for real-time SQL (KSQL)

---

## 📚 **Additional Resources**

### **Books:**
- Kleppmann, Martin. *Designing Data-Intensive Applications* (2017) - Chapter 2 (Data Models), Chapter 3 (Storage & Retrieval)
- Elmasri & Navathe. *Fundamentals of Database Systems* (7th Ed.)
- Garcia-Molina et al. *Database Systems: The Complete Book* (2nd Ed.)

### **Online Courses:**
- CMU 15-445: Database Systems (Andy Pavlo) - YouTube
- Stanford CS145: Introduction to Databases
- Use The Index, Luke! (https://use-the-index-luke.com/)

### **Tools:**
- **PostgreSQL:** Best for learning internals (open source)
- **pgAdmin / DBeaver:** Visual EXPLAIN plans
- **pg_stat_statements:** Query performance monitoring
- **EXPLAIN.DEPESZ.COM:** Visual query plan analyzer

### **Communities:**
- r/PostgreSQL, r/Database on Reddit
- Database Administrators Stack Exchange
- PostgreSQL Slack channel

---

## ❓ **FAQ**

**Q: Should I start with BEGINNER or INTERMEDIATE?**  
A: If you can write JOINs and GROUP BY, start with INTERMEDIATE. BEGINNER is for SQL basics review.

**Q: Do I need to read WHITEPAPERS?**  
A: Not required for practical work, but highly recommended for understanding the "why" behind database design choices.

**Q: Which database should I practice on?**  
A: PostgreSQL (open source, well-documented, powerful). MySQL is also good. Avoid proprietary DBs for learning.

**Q: How do I know if my query is slow?**  
A: 
- < 10ms: Fast (index-based lookup)
- 10-100ms: Acceptable (simple aggregation)
- 100ms-1s: Slow (needs optimization)
- \> 1s: Very slow (critical issue)

**Q: When should I add an index?**  
A: 
- Columns in WHERE clauses (especially selective ones)
- Columns in JOIN conditions
- Columns in ORDER BY (if sorting is slow)
- NOT for columns with low cardinality (gender, boolean)

**Q: What's the difference between RANK and DENSE_RANK?**  
A:
- **RANK:** Skips ranks after ties (1, 2, 2, 4)
- **DENSE_RANK:** No skipping (1, 2, 2, 3)

**Q: How do I partition a table in PostgreSQL?**  
A:
```sql
-- Create parent table
CREATE TABLE orders (
    order_id BIGINT,
    order_date DATE,
    ...
) PARTITION BY RANGE (order_date);

-- Create partitions
CREATE TABLE orders_2024 PARTITION OF orders
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

---

## 🎉 **Congratulations!**

You've completed **Week 3: SQL Deep Dive**!

You now understand:
- ✅ How databases execute queries (parser → optimizer → executor)
- ✅ Index types and when to use them
- ✅ OLTP vs OLAP architectures
- ✅ Query optimization with EXPLAIN plans
- ✅ Advanced SQL patterns (window functions, CTEs, recursive queries)
- ✅ Database internals (B-trees, WAL, storage models)
- ✅ Sharding strategies for scale
- ✅ ACID properties and CAP theorem

**You're ready for:**
- Week 4: Apache Spark (distributed SQL with Spark SQL)
- Week 5: Data Warehousing (columnar storage, Parquet, BigQuery)
- Production database optimization work

---

**Keep learning! 🚀**

**Next:** [Week 4: Apache Spark Fundamentals](../1D_Apache_Spark/README.md) (Coming next!)

**Master Roadmap:** [00-MASTER-ROADMAP.md](../../00-MASTER-ROADMAP.md)
