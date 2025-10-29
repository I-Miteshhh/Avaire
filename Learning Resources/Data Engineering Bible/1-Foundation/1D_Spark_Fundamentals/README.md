# Week 4: Apache Spark Fundamentals 🚀

---

## 📖 **Module Overview**

Apache Spark is the **de facto standard for big data processing**, powering data pipelines at Netflix, Uber, Airbnb, and every major tech company. This module teaches you Spark from fundamentals to production expertise.

**What you'll learn:**
- Build production ETL pipelines with PySpark
- Optimize Spark jobs (10-100x performance gains)
- Understand Catalyst optimizer and Tungsten internals
- Handle 100 TB+ datasets efficiently
- Ace FAANG Spark interviews

---

## 🎯 **Learning Paths**

### **Path 1: Beginner (First-time Spark users)**

**Time:** 8-12 hours  
**Prerequisites:** Python basics, SQL knowledge

**Recommended flow:**
1. Read [BEGINNER.md](./BEGINNER.md) - Core concepts and first Spark job
2. Complete practice exercises (word count, sales analysis)
3. Set up local Spark (see setup section below)
4. Run all code examples from BEGINNER.md

**Success metrics:**
- ✅ Understand RDD vs DataFrame
- ✅ Can write basic PySpark transformations (filter, select, groupBy)
- ✅ Know when Spark executes (lazy evaluation)
- ✅ Successfully run Spark job locally

---

### **Path 2: Intermediate (Data Engineers with 1-2 years experience)**

**Time:** 12-16 hours  
**Prerequisites:** Path 1 + production ETL experience

**Recommended flow:**
1. Review BEGINNER.md (focus on lazy evaluation, DAG)
2. Deep dive [INTERMEDIATE.md](./INTERMEDIATE.md) - Production patterns
3. Build complete ETL pipeline (see code examples)
4. Practice performance optimization (caching, broadcast joins)
5. Implement SCD Type 2 pattern in Spark

**Success metrics:**
- ✅ Can build production ETL pipeline with data quality checks
- ✅ Know how to optimize Spark jobs (partitioning, caching, broadcast)
- ✅ Understand when/why shuffles occur
- ✅ Can read Spark UI to debug performance issues

---

### **Path 3: Expert (Senior Engineers, System Designers)**

**Time:** 16-20 hours  
**Prerequisites:** Paths 1 & 2 + distributed systems knowledge

**Recommended flow:**
1. Study [EXPERT.md](./EXPERT.md) - Internals and advanced optimization
2. Read [WHITEPAPERS.md](./WHITEPAPERS.md) - Original research papers
3. Design production Spark cluster (sizing, configuration)
4. Practice FAANG interview questions (10 questions in EXPERT.md)
5. Build custom data source (see example code)

**Success metrics:**
- ✅ Understand Catalyst optimizer phases
- ✅ Can explain Tungsten memory management
- ✅ Know how to handle data skew in production
- ✅ Can design Spark cluster for 100 TB+ workloads
- ✅ Ready for L4+ (Staff Engineer) Spark interviews

---

## 🛠️ **Setup Instructions**

### **Option 1: Local Setup (Recommended for learning)**

**Install PySpark:**

```bash
# Windows (PowerShell)
pip install pyspark

# Verify installation
python -c "from pyspark.sql import SparkSession; print(SparkSession.builder.appName('test').getOrCreate().version)"
```

**First Spark script:**

```python
# hello_spark.py
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Hello Spark") \
    .master("local[*]") \
    .getOrCreate()

data = [("Alice", 30), ("Bob", 25), ("Charlie", 35)]
df = spark.createDataFrame(data, ["name", "age"])

df.filter(df.age > 28).show()

spark.stop()
```

**Run:**

```bash
python hello_spark.py
```

**Expected output:**

```
+-------+---+
|   name|age|
+-------+---+
|  Alice| 30|
|Charlie| 35|
+-------+---+
```

---

### **Option 2: Docker (Isolated environment)**

**Create `docker-compose.yml`:**

```yaml
version: '3'
services:
  spark:
    image: jupyter/pyspark-notebook:latest
    ports:
      - "8888:8888"
      - "4040:4040"
    volumes:
      - ./data:/home/jovyan/data
      - ./notebooks:/home/jovyan/notebooks
```

**Start:**

```bash
docker-compose up -d
```

**Access Jupyter:** http://localhost:8888 (check logs for token)

---

### **Option 3: Databricks Community Edition (Cloud)**

**Steps:**
1. Sign up: https://databricks.com/try-databricks
2. Create cluster (free tier: 15 GB RAM, 2 cores)
3. Create notebook
4. Run Spark code

**Advantages:**
- No local setup
- Access to Spark UI
- Collaborative notebooks
- Pre-installed libraries

---

## 📂 **Module Structure**

```
1D_Apache_Spark/
├── README.md (this file)
├── BEGINNER.md (~4,500 words)
│   ├── What is Spark?
│   ├── RDDs vs DataFrames
│   ├── First Spark job (word count)
│   ├── Reading/writing data
│   ├── Common transformations
│   └── Practice exercises
│
├── INTERMEDIATE.md (~5,000 words)
│   ├── Production ETL pipeline (500+ lines)
│   ├── Performance optimization
│   ├── Complex data types (arrays, structs, JSON)
│   ├── SCD Type 2 implementation
│   ├── Error handling
│   └── Spark UI debugging
│
├── EXPERT.md (~6,000 words)
│   ├── Catalyst optimizer internals
│   ├── Tungsten execution engine
│   ├── Handling data skew
│   ├── Memory tuning
│   ├── Production cluster design
│   ├── Custom data sources
│   └── 10 FAANG interview questions
│
└── WHITEPAPERS.md (~4,000 words)
    ├── Spark: Cluster Computing (2010)
    ├── Resilient Distributed Datasets (2012)
    ├── Spark SQL (2015)
    ├── Structured Streaming (2018)
    └── Photon (2022)
```

---

## 🎓 **Practice Projects**

### **Project 1: E-Commerce Analytics**

**Level:** Beginner  
**Time:** 4-6 hours

**Goal:** Analyze e-commerce data (orders, customers, products)

**Tasks:**
1. Read CSV files into DataFrames
2. Calculate total revenue per customer
3. Find top 10 products by sales
4. Join orders with customers to get customer names
5. Write results to Parquet

**Starter code:** See BEGINNER.md practice exercises

---

### **Project 2: Real-Time Fraud Detection**

**Level:** Intermediate  
**Time:** 8-12 hours

**Goal:** Detect suspicious transactions in real-time

**Tasks:**
1. Set up Kafka (or use mock stream)
2. Read transaction stream with Structured Streaming
3. Implement windowed aggregations (count txns per user per 5 min)
4. Flag suspicious patterns (> 10 txns or avg > $1000)
5. Write alerts to output sink

**Starter code:** See EXPERT.md Question 6

---

### **Project 3: Data Warehouse ETL**

**Level:** Intermediate/Expert  
**Time:** 12-16 hours

**Goal:** Build production ETL pipeline with SCD Type 2

**Tasks:**
1. Extract from multiple sources (CSV, Parquet, JDBC)
2. Implement data quality checks
3. Build star schema (fact + dimensions)
4. Implement SCD Type 2 for customer dimension
5. Partition output by date
6. Monitor with Spark UI

**Starter code:** See INTERMEDIATE.md Production ETL example

---

## 📚 **Resources**

### **Official Documentation**
- [Spark Programming Guide](https://spark.apache.org/docs/latest/rdd-programming-guide.html)
- [Spark SQL Guide](https://spark.apache.org/docs/latest/sql-programming-guide.html)
- [PySpark API Docs](https://spark.apache.org/docs/latest/api/python/)

### **Books**
- **"Learning Spark" (2nd Edition, 2020)** - Best for beginners
- **"Spark: The Definitive Guide" (2018)** - Comprehensive reference
- **"High Performance Spark" (2017)** - Advanced optimization

### **Video Courses**
- Databricks Academy (free courses)
- Udemy: "Apache Spark with Python - Big Data with PySpark"
- Coursera: "Big Data Analysis with Scala and Spark"

### **Research Papers**
- See [WHITEPAPERS.md](./WHITEPAPERS.md) for full list with summaries

---

## 🧪 **Sample Data**

### **Generate test data:**

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import expr

spark = SparkSession.builder.appName("Generate Data").getOrCreate()

# Generate 1 million orders
orders = spark.range(0, 1000000) \
    .withColumn("customer_id", (expr("id % 10000")).cast("string")) \
    .withColumn("product_id", (expr("id % 1000")).cast("string")) \
    .withColumn("quantity", expr("int(rand() * 10) + 1")) \
    .withColumn("price", expr("round(rand() * 1000, 2)"))

orders.write.mode("overwrite").parquet("data/orders.parquet")

print("Generated 1M orders")
```

---

## ❓ **FAQ**

**Q: Spark vs Pandas - when to use which?**

**A:**
- **Pandas:** < 5 GB data (fits in RAM), single machine, interactive analysis
- **Spark:** > 5 GB data, distributed processing, production ETL pipelines

---

**Q: Should I learn RDDs or DataFrames first?**

**A:** Start with **DataFrames**! RDDs are low-level and rarely used in modern Spark (except for ML algorithms). DataFrames are:
- Easier to learn (SQL-like API)
- Optimized by Catalyst (faster)
- Standard in production

---

**Q: How many partitions should I use?**

**A:** Rule of thumb:
- **Size:** 128 MB - 1 GB per partition
- **Formula:** `num_partitions = total_data_size_MB / 128`
- **Example:** 10 GB data → ~80 partitions

---

**Q: When does Spark execute my code?**

**A:** Spark uses **lazy evaluation**. Execution happens only when you call an **action**:
- **Transformations (lazy):** `filter`, `select`, `groupBy`, `join`
- **Actions (trigger execution):** `count`, `show`, `write`, `collect`

---

**Q: How to debug slow Spark jobs?**

**A:**
1. Check **Spark UI** (http://localhost:4040)
2. Look at **Stages** tab → identify long-running stages
3. Check for **shuffle spill** (data written to disk)
4. Look for **data skew** (one task much slower than others)
5. Read execution plan: `df.explain("extended")`

---

## 🚀 **Next Steps**

After completing this module:

1. **Practice:** Build at least one project from the practice section
2. **Optimize:** Take an existing Spark job and optimize it (10x speedup is achievable!)
3. **Production:** Deploy Spark job to cloud (AWS EMR, Databricks, GCP Dataproc)
4. **Interview:** Practice FAANG questions in EXPERT.md

**Next week:** [Week 5: Data Warehousing & Columnar Storage](../1E_Data_Warehousing/README.md)

**Previous week:** [Week 3: SQL Deep Dive](../1C_SQL_Deep_Dive/README.md)

**Master Roadmap:** [00-MASTER-ROADMAP.md](../../00-MASTER-ROADMAP.md)

---

## 📊 **Success Checklist**

Track your progress:

- [ ] Installed PySpark locally
- [ ] Ran first Spark job (word count)
- [ ] Completed BEGINNER.md practice exercises
- [ ] Built production ETL pipeline (INTERMEDIATE.md)
- [ ] Optimized Spark job (10x+ speedup)
- [ ] Read Spark UI to debug performance
- [ ] Implemented SCD Type 2 in Spark
- [ ] Understood Catalyst optimizer (EXPERT.md)
- [ ] Read at least 2 research papers (WHITEPAPERS.md)
- [ ] Solved 5+ FAANG interview questions

**Target:** Complete 80%+ before moving to next week

---

**Good luck! You're on your way to becoming a Spark expert! 🎉**
