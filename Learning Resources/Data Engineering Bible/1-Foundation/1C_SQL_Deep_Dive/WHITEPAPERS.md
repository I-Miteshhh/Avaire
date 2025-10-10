# Week 3: SQL Deep Dive
## 📚 WHITEPAPERS - Database Research & Academic Foundations

---

## 🎯 **Learning Objectives**

- Understand foundational database papers
- Learn ACID properties and transaction isolation
- Explore distributed database theory (CAP theorem)
- Study query optimization algorithms
- Compare OLTP vs OLAP evolution

---

## 📖 **1. The Relational Model (E.F. Codd, 1970)**

### **Context & Impact**

**Author:** Edgar F. Codd (IBM)  
**Published:** "A Relational Model of Data for Large Shared Data Banks" (1970)  
**Impact:** Created the foundation for SQL and modern databases

**Historical Context:**
- Before 1970: Hierarchical databases (IMS), network databases (CODASYL)
- Data access was procedural (navigate pointers, like a linked list)
- Codd proposed: Declarative queries (say WHAT you want, not HOW to get it)

---

### **Core Thesis**

> **"Data should be organized as relations (tables), and accessed through mathematical set theory."**

**Key Concepts:**

#### **1. Relations (Tables)**

```
Relation = Table with rows and columns

employees (relation)
┌──────────┬─────────┬────────────┬────────┐
│ emp_id   │ name    │ department │ salary │
├──────────┼─────────┼────────────┼────────┤
│ 1        │ Alice   │ Engineering│ 150000 │
│ 2        │ Bob     │ Sales      │ 120000 │
└──────────┴─────────┴────────────┴────────┘

Properties:
- Each row (tuple) is unique
- Column order doesn't matter
- No duplicate rows
```

---

#### **2. Relational Algebra**

**Operations on relations:**

**Selection (σ):** Filter rows
```sql
σ_{salary > 100000}(employees)

-- SQL equivalent:
SELECT * FROM employees WHERE salary > 100000;
```

**Projection (π):** Select columns
```sql
π_{name, salary}(employees)

-- SQL equivalent:
SELECT name, salary FROM employees;
```

**Join (⋈):** Combine tables
```sql
employees ⋈_{emp_id = employee_id} departments

-- SQL equivalent:
SELECT * FROM employees e
JOIN departments d ON e.emp_id = d.employee_id;
```

---

#### **3. Normalization (Eliminate Redundancy)**

**Before Normalization (Bad):**
```
orders
┌──────────┬──────────┬──────────┬────────────────┬──────────┐
│ order_id │ customer │ email    │ product        │ price    │
├──────────┼──────────┼──────────┼────────────────┼──────────┤
│ 1        │ Alice    │ a@ex.com │ iPhone         │ 1000     │
│ 2        │ Alice    │ a@ex.com │ MacBook        │ 2000     │  ← Email duplicated!
│ 3        │ Bob      │ b@ex.com │ iPhone         │ 1000     │
└──────────┴──────────┴──────────┴────────────────┴──────────┘

Problems:
- Email duplicated for each order
- If Alice changes email, must update multiple rows
- Waste of storage
```

**After Normalization (Good):**
```
customers
┌──────────┬──────────┬──────────┐
│ customer_id │ name  │ email    │
├──────────┼──────────┼──────────┤
│ 1        │ Alice    │ a@ex.com │
│ 2        │ Bob      │ b@ex.com │
└──────────┴──────────┴──────────┘

orders
┌──────────┬──────────────┬────────────┬──────────┐
│ order_id │ customer_id  │ product    │ price    │
├──────────┼──────────────┼────────────┼──────────┤
│ 1        │ 1            │ iPhone     │ 1000     │
│ 2        │ 1            │ MacBook    │ 2000     │
│ 3        │ 2            │ iPhone     │ 1000     │
└──────────┴──────────────┴────────────┴──────────┘

Benefits:
- Email stored once (no duplication)
- Update email in one place
- Reduced storage
```

---

### **Codd's Legacy**

**Impact:**
- SQL based on relational algebra
- MySQL, PostgreSQL, Oracle all follow relational model
- Normalization is standard practice
- Declarative querying (vs procedural navigation)

**Modern Relevance:**
- NoSQL databases reject normalization (denormalize for performance)
- But relational model still dominates transactional systems (OLTP)

---

## 📖 **2. ACID Properties (Jim Gray, 1981)**

### **Context**

**Author:** Jim Gray (IBM, later Microsoft)  
**Paper:** "The Transaction Concept" (1981)  
**Impact:** Defined how databases ensure data integrity

---

### **ACID Explained**

**ACID = Atomicity, Consistency, Isolation, Durability**

---

#### **A: Atomicity (All or Nothing)**

**Principle:** Transaction either completes fully or not at all.

**Example: Bank transfer**
```sql
BEGIN TRANSACTION;

-- Step 1: Deduct from Alice's account
UPDATE accounts SET balance = balance - 100 WHERE user_id = 1;

-- Step 2: Add to Bob's account
UPDATE accounts SET balance = balance + 100 WHERE user_id = 2;

COMMIT;
```

**What if power fails after Step 1?**
- ❌ Without atomicity: Alice loses $100, Bob gets nothing (money vanished!)
- ✅ With atomicity: Transaction rolled back, both accounts unchanged

**How databases enforce:**
- Write-Ahead Logging (WAL)
- If crash occurs, replay or rollback incomplete transactions

---

#### **C: Consistency (Valid State)**

**Principle:** Transaction moves database from one valid state to another.

**Example: Constraints**
```sql
CREATE TABLE accounts (
    user_id INT PRIMARY KEY,
    balance DECIMAL(10,2) CHECK (balance >= 0)  -- Balance can't be negative
);

BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 200 WHERE user_id = 1;
-- If Alice has $100, this violates CHECK constraint
-- Transaction aborted!
ROLLBACK;
```

**Consistency ensures:**
- Foreign keys are valid
- Unique constraints aren't violated
- CHECK constraints are satisfied

---

#### **I: Isolation (Concurrent Transactions Don't Interfere)**

**Principle:** Transactions execute as if they're the only transaction.

**Problem without isolation:**
```
Time | Transaction A          | Transaction B
-----|------------------------|------------------------
T1   | SELECT balance (100)   |
T2   |                        | SELECT balance (100)
T3   | balance -= 50          |
T4   |                        | balance -= 30
T5   | UPDATE balance = 50    |
T6   |                        | UPDATE balance = 70  ← Should be 20!

Result: Lost update! (50 + 30 = 80, but should be 100 - 50 - 30 = 20)
```

**Isolation levels (weak to strong):**

---

**Level 1: Read Uncommitted (Weakest)**

```sql
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

-- Transaction A
BEGIN;
UPDATE accounts SET balance = 1000 WHERE user_id = 1;
-- Not committed yet...

-- Transaction B (concurrent)
SELECT balance FROM accounts WHERE user_id = 1;
-- Returns 1000 (dirty read!)

-- Transaction A
ROLLBACK;  -- Undo the update

-- Transaction B saw data that never existed!
```

**Allows:** Dirty reads (read uncommitted data)

---

**Level 2: Read Committed (Default in PostgreSQL)**

```sql
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- Transaction A
BEGIN;
UPDATE accounts SET balance = 1000 WHERE user_id = 1;
-- Not committed yet...

-- Transaction B
SELECT balance FROM accounts WHERE user_id = 1;
-- Returns old value (100) until A commits

-- Transaction A
COMMIT;

-- Transaction B
SELECT balance FROM accounts WHERE user_id = 1;
-- Now returns 1000 ✅
```

**Allows:** Non-repeatable reads (value changes between two reads in same transaction)

---

**Level 3: Repeatable Read**

```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- Transaction A
BEGIN;
SELECT balance FROM accounts WHERE user_id = 1;  -- Returns 100

-- Transaction B
UPDATE accounts SET balance = 1000 WHERE user_id = 1;
COMMIT;

-- Transaction A
SELECT balance FROM accounts WHERE user_id = 1;
-- Still returns 100 (snapshot from start of transaction)
COMMIT;
```

**Allows:** Phantom reads (new rows appear in range queries)

---

**Level 4: Serializable (Strongest)**

```sql
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Transactions execute as if they ran one after another
-- No dirty reads, no non-repeatable reads, no phantom reads
-- Performance cost: Highest
```

---

#### **D: Durability (Committed Data Persists)**

**Principle:** Once committed, data survives crashes.

**How databases ensure:**

**Write-Ahead Logging (WAL):**
```
1. Transaction: UPDATE accounts SET balance = 1000 WHERE user_id = 1

2. Write to WAL (sequential disk write):
   [2024-10-09 10:30:00] UPDATE accounts SET balance = 1000 WHERE user_id = 1

3. Return success to user

4. Later (background): Update data file

5. If crash before step 4:
   - On restart, replay WAL
   - Recover committed transactions
```

**Durability guarantees:**
- fsync() to force data to disk (not just OS cache)
- Redundant storage (RAID, replication)

---

## 📖 **3. CAP Theorem (Eric Brewer, 2000)**

### **Context**

**Author:** Eric Brewer (UC Berkeley)  
**Presented:** PODC 2000  
**Formalized:** Seth Gilbert & Nancy Lynch (2002)  
**Impact:** Explained trade-offs in distributed databases

---

### **CAP Theorem Statement**

> **"In a distributed system, you can have at most TWO of these three properties: Consistency, Availability, Partition Tolerance."**

**Visual:**
```
         Consistency
              /\
             /  \
            /    \
           /  CP  \
          /________\
         /    CA    \
        /____________\
    Availability    Partition
                    Tolerance
    
Choose 2:
- CA: Consistent + Available (no partition tolerance) → Single-server databases
- CP: Consistent + Partition Tolerant → MongoDB, HBase, BigTable
- AP: Available + Partition Tolerant → Cassandra, DynamoDB, Riak
```

---

### **The Three Properties**

#### **C: Consistency**

**Definition:** All nodes see the same data at the same time.

**Example:**
```
Write to Node 1: SET balance = 1000
Read from Node 2: GET balance
→ Must return 1000 (not stale value)
```

---

#### **A: Availability**

**Definition:** Every request receives a response (success or failure).

**Example:**
```
Even if Node 1 is down, Node 2 should respond to queries
(May return stale data, but doesn't hang)
```

---

#### **P: Partition Tolerance**

**Definition:** System continues to operate despite network partitions (split-brain).

**Example:**
```
Network partition splits cluster:
Node 1, Node 2 | Network Cut | Node 3, Node 4

System must handle:
- Nodes on both sides continue to operate
- Can't communicate across partition
```

---

### **Why Can't We Have All Three?**

**Scenario: Network Partition**

```
User writes to Node 1: SET balance = 1000
Network partition occurs (Node 1 can't talk to Node 2)

User reads from Node 2: GET balance

Options:
1. Return stale data (500) → AP system (Available, but inconsistent)
2. Return error ("can't guarantee consistency") → CP system (Consistent, but unavailable)
3. Wait for network to heal → Not available (violates A)

You MUST choose: Consistency or Availability during partition.
```

---

### **Real-World Examples**

#### **CP System: MongoDB (Primary-Secondary)**

```
Normal operation:
Primary (write) ──replica──> Secondary (read)

Network partition:
Primary | Network Cut | Secondary

Decision:
- Secondary refuses reads (can't guarantee up-to-date data)
- Chooses Consistency over Availability
```

---

#### **AP System: Cassandra (Multi-Master)**

```
Normal operation:
Node 1 ──sync──> Node 2 ──sync──> Node 3

Network partition:
Node 1, Node 2 | Network Cut | Node 3

Decision:
- All nodes accept writes (even if can't sync)
- Chooses Availability over Consistency
- Eventual consistency (sync when network heals)
```

---

### **CAP in Practice**

**Modern consensus:**
- P (Partition Tolerance) is non-negotiable (networks fail)
- Real choice: **Consistency (CP) vs Availability (AP)**

**Choosing CP:**
- Banking, financial transactions
- Inventory management (prevent overselling)
- Strong consistency required

**Choosing AP:**
- Social media (Twitter feed can be stale)
- Analytics dashboards (5-minute delay acceptable)
- Shopping cart (eventual consistency okay)

---

## 📖 **4. Query Optimization (Selinger et al., 1979)**

### **Context**

**Authors:** Patricia Selinger, Morton Astrahan, et al. (IBM)  
**Paper:** "Access Path Selection in a Relational Database Management System" (1979)  
**Impact:** Invented cost-based query optimization (used in all modern databases)

---

### **The Problem**

**Query:**
```sql
SELECT *
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_date > '2024-01-01'
  AND c.country = 'USA';
```

**Multiple execution plans:**
```
Plan A:
1. Scan all orders
2. Filter by order_date
3. Join to customers
4. Filter by country

Plan B:
1. Scan all customers
2. Filter by country
3. Join to orders
4. Filter by order_date

Plan C:
1. Use index on order_date
2. Use index on country
3. Join filtered results

Which is fastest? 🤔
```

---

### **Cost-Based Optimization**

**Key Insight:** Estimate cost of each plan, choose cheapest.

**Cost formula:**
```
cost = (disk_page_reads × DISK_COST) + (CPU_operations × CPU_COST)

where:
  DISK_COST = 1.0 (reading 1 page = 1 unit)
  CPU_COST = 0.01 (CPU is 100x faster than disk)
```

---

### **Statistics-Driven Decisions**

**Optimizer uses table statistics:**

```sql
-- Table: orders (10M rows)
-- Selectivity of order_date > '2024-01-01': 20% (2M rows)

-- Table: customers (1M rows)
-- Selectivity of country = 'USA': 40% (400K rows)
```

**Plan A cost:**
```
1. Scan orders: 100,000 pages
2. Filter by date: 2M rows remain (CPU only)
3. Join to customers: 2M × 1 lookup = 2M page reads
4. Filter by country: 40% remain (CPU only)

Total cost: 100,000 + 2,000,000 = 2,100,000
```

**Plan B cost:**
```
1. Scan customers: 10,000 pages
2. Filter by country: 400K rows remain
3. Join to orders: 400K × 1 lookup = 400K page reads
4. Filter by date: 20% remain

Total cost: 10,000 + 400,000 = 410,000 ✅ (5x cheaper!)
```

**Optimizer chooses Plan B.**

---

### **Join Algorithms**

**Three algorithms, different costs:**

**1. Nested Loop Join**
```python
for customer in customers:  # 400K rows
    for order in orders:  # 2M matching rows
        if matches(customer, order):
            yield result

Cost: 400K × 2M = 800B comparisons (very slow!)
```

**2. Hash Join**
```python
# Build hash table from smaller table
hash_table = {}
for customer in customers_filtered:  # 400K rows
    hash_table[customer.id] = customer

# Probe with larger table
for order in orders_filtered:  # 2M rows
    if order.customer_id in hash_table:
        yield (order, hash_table[order.customer_id])

Cost: 400K + 2M = 2.4M operations ✅
```

**3. Merge Join**
```python
# Requires both tables sorted by join key
orders_sorted = sorted(orders_filtered, key=lambda x: x.customer_id)
customers_sorted = sorted(customers_filtered, key=lambda x: x.id)

i, j = 0, 0
while i < len(orders) and j < len(customers):
    if orders[i].customer_id == customers[j].id:
        yield (orders[i], customers[j])
        i += 1
    elif orders[i].customer_id < customers[j].id:
        i += 1
    else:
        j += 1

Cost: 2M log 2M + 400K log 400K + 2M + 400K (sort + merge)
```

---

### **Dynamic Programming for Query Plans**

**For complex queries with many joins:**
```sql
SELECT *
FROM A
JOIN B ON ...
JOIN C ON ...
JOIN D ON ...
JOIN E ON ...
```

**Possible join orders:** N! (factorial)
- 5 tables: 120 possible orders
- 10 tables: 3.6 million possible orders!

**Selinger's Solution:**
- Use dynamic programming to explore join orders
- Prune expensive branches early
- Generate optimal plan in polynomial time

---

## 📖 **5. OLTP vs OLAP Evolution**

### **Timeline**

**1970s: OLTP Databases**
- IBM System R, Oracle
- Row-oriented storage
- Optimized for transactions (INSERT/UPDATE/DELETE)

**1980s-1990s: Data Warehouses Emerge**
- Teradata (1979)
- Need for analytics separate from OLTP
- Star schema, dimensional modeling

**2000s: Column Stores**
- C-Store (2005) → Vertica
- MonetDB
- Column-oriented storage for OLAP

**2010s: Cloud Data Warehouses**
- Amazon Redshift (2012)
- Google BigQuery (2012)
- Snowflake (2014)
- Elastic scaling, separation of storage/compute

**2020s: Data Lakehouses**
- Databricks Delta Lake (2019)
- Apache Iceberg (2018)
- Apache Hudi (2019)
- Combine lake (flexibility) + warehouse (performance)

---

### **C-Store Paper (Stonebraker et al., 2005)**

**Key Contribution:** Proved column stores are 10-100x faster for OLAP.

**How column stores win:**

**Query:** `SELECT AVG(salary) FROM employees;` (100M rows)

**Row store:**
```
Read: 100M rows × 20 columns = 2B values
Disk I/O: 40 GB
Time: 60 seconds
```

**Column store:**
```
Read: 100M rows × 1 column = 100M values
Compression: 40 GB → 500 MB (salary values are similar)
Disk I/O: 500 MB
Time: 2 seconds ⚡
```

**Why compression works:**
- Columns have similar values (easier to compress)
- Run-length encoding: [1000, 1000, 1000, ...] → [1000 × 100M]
- Dictionary encoding: ["USA", "USA", "UK", ...] → [1, 1, 2, ...]

---

## 🎯 **Summary**

### **Key Papers & Concepts**

1. **Codd (1970):** Relational model, SQL, normalization
2. **Gray (1981):** ACID properties, transactions
3. **Brewer (2000):** CAP theorem (CP vs AP trade-off)
4. **Selinger (1979):** Cost-based query optimization
5. **Stonebraker (2005):** Column stores for OLAP

---

### **Modern Implications**

**OLTP (Row Stores):**
- PostgreSQL, MySQL, Oracle
- ACID transactions
- Normalized schemas
- B-tree indexes

**OLAP (Column Stores):**
- Snowflake, BigQuery, Redshift
- Eventual consistency (often)
- Denormalized (star schema)
- Columnar compression

**Distributed Systems:**
- CAP theorem: Choose CP or AP
- Consensus algorithms: Paxos, Raft
- Sharding for scale

---

## 📚 **Further Reading**

### **Foundational Papers**

1. **E.F. Codd (1970)**  
   "A Relational Model of Data for Large Shared Data Banks"  
   https://www.seas.upenn.edu/~zives/03f/cis550/codd.pdf

2. **Jim Gray (1981)**  
   "The Transaction Concept: Virtues and Limitations"  
   https://jimgray.azurewebsites.net/papers/theTransactionConcept.pdf

3. **Eric Brewer (2000)**  
   "Towards Robust Distributed Systems" (CAP Theorem)  
   https://people.eecs.berkeley.edu/~brewer/cs262b-2004/PODC-keynote.pdf

4. **Patricia Selinger et al. (1979)**  
   "Access Path Selection in a Relational Database Management System"  
   https://courses.cs.duke.edu/compsci516/cps216/spring03/papers/selinger-etal-1979.pdf

5. **Michael Stonebraker et al. (2005)**  
   "C-Store: A Column-oriented DBMS"  
   http://db.csail.mit.edu/projects/cstore/vldb.pdf

---

### **Modern Resources**

**Books:**
- Kleppmann, Martin. *Designing Data-Intensive Applications* (2017)
- Elmasri & Navathe. *Fundamentals of Database Systems* (7th Ed.)
- Garcia-Molina et al. *Database Systems: The Complete Book* (2nd Ed.)

**Online:**
- Database Internals by Alex Petrov (2019)
- CMU Database Course (Andy Pavlo): https://15445.courses.cs.cmu.edu/
- PostgreSQL Documentation: https://www.postgresql.org/docs/

---

**Next:** [README](./README.md) - Module overview

**Previous:** [EXPERT](./EXPERT.md)

**Master Roadmap:** [00-MASTER-ROADMAP.md](../../00-MASTER-ROADMAP.md)
