# Week 2: ETL Pipelines & Data Modeling
## 📖 Module Overview

---

## 🎯 **What You'll Learn**

This module teaches you how to **build production ETL pipelines** and **design dimensional data warehouses** that power business intelligence at companies like Netflix, Airbnb, and Uber.

**By the end of this week, you will:**
- ✅ Understand Extract-Transform-Load (ETL) fundamentals
- ✅ Design star and snowflake schemas for analytics
- ✅ Implement Slowly Changing Dimensions (SCD Types 1-6)
- ✅ Build end-to-end ETL pipelines in Python
- ✅ Apply Kimball's dimensional modeling methodology
- ✅ Compare Kimball vs Inmon approaches
- ✅ Design data warehouses at FAANG scale

---

## 📚 **Learning Path**

### **Choose Your Level:**

```
🌱 BEGINNER (2-3 hours)
├─ Start here if: You're new to data warehousing
├─ Format: Restaurant kitchen analogy, visual diagrams
└─ Outcome: Understand ETL concepts and star schema basics

🔨 INTERMEDIATE (4-5 hours)
├─ Start here if: You know SQL and want to build ETL pipelines
├─ Format: Hands-on Python implementation, 300+ lines of code
└─ Outcome: Build a production-ready ETL pipeline

🏗️ EXPERT (6-8 hours)
├─ Start here if: You want to design systems at scale
├─ Format: Netflix/Airbnb/Uber architectures, system design
└─ Outcome: Design enterprise data warehouses, answer FAANG interviews

📄 WHITEPAPERS (3-4 hours)
├─ Start here if: You want theoretical depth
├─ Format: Kimball & Inmon methodologies, academic foundations
└─ Outcome: Understand the "why" behind modern practices
```

---

## 🗺️ **Module Roadmap**

### **Phase 1: Fundamentals** (BEGINNER)

**Topics:**
- What is ETL? (Extract, Transform, Load)
- Star schema vs Snowflake schema
- Fact tables vs Dimension tables
- Batch vs Streaming ETL
- Data quality and idempotency

**Key Concepts:**
```
Restaurant Kitchen Analogy:
- Extract = Gathering ingredients
- Transform = Prep and cooking
- Load = Plating and serving

Star Schema:
- Facts = Measurements (revenue, quantity)
- Dimensions = Context (who, what, when, where)
```

**Time:** 2-3 hours  
**Prerequisites:** Basic SQL

---

### **Phase 2: Implementation** (INTERMEDIATE)

**Topics:**
- Building DataExtractor (PostgreSQL, APIs, S3, MongoDB)
- Implementing DataTransformer (cleaning, validation, SCD Type 2)
- Creating DataLoader (star schema, idempotent loading)
- End-to-end ETLPipeline orchestration

**Hands-On Project:**
```python
E-commerce ETL Pipeline:
- Extract: Orders, customers, products, web events
- Transform: 
  - Clean null values
  - Standardize formats
  - Implement SCD Type 2 for customer changes
  - Build star schema
- Load: 
  - Create fact_orders
  - Create dimension tables (customers, products, dates)
  - Ensure idempotency
```

**Time:** 4-5 hours  
**Prerequisites:** Python, SQL, basic data structures

---

### **Phase 3: Production Systems** (EXPERT)

**Topics:**
- Netflix viewing data warehouse (100+ PB scale)
- Airbnb listing & booking star schema
- Uber trips geospatial + temporal design
- Data Vault modeling
- Activity schema patterns
- Conformed dimensions
- 10 FAANG system design questions

**Real-World Architectures:**
```
Netflix:
- Kafka → S3 (Parquet)
- Spark batch jobs
- Redshift/Snowflake star schema
- Pre-aggregation for performance

Airbnb:
- PostgreSQL (OLTP) → Data Lake → Warehouse
- Star schema: fact_bookings, dim_listings, dim_users
- Geospatial queries for city analytics

Uber:
- Geo-sharded fact_trips
- PostGIS for spatial queries
- 5-minute pre-aggregation for surge pricing
```

**Time:** 6-8 hours  
**Prerequisites:** Distributed systems knowledge, SQL optimization

---

### **Phase 4: Theoretical Foundations** (WHITEPAPERS)

**Topics:**
- Ralph Kimball: Dimensional Modeling (1996)
  - 4-step design process
  - Star vs Snowflake debate
  - Slowly Changing Dimensions (SCD Types 0-6)
  - Conformed dimensions
  
- Bill Inmon: Corporate Information Factory (1992)
  - Subject-oriented, integrated, time-variant, non-volatile
  - 3NF enterprise data warehouse
  - Top-down vs bottom-up

- Modern Data Stack (2016+)
  - dbt (Analytics Engineering)
  - ELT vs ETL
  - Medallion architecture (Bronze/Silver/Gold)

**Time:** 3-4 hours  
**Prerequisites:** Data warehousing concepts from BEGINNER/INTERMEDIATE

---

## 🎓 **Learning Outcomes**

### **By Level:**

**BEGINNER:**
- [ ] Explain ETL in simple terms
- [ ] Identify facts vs dimensions in a business scenario
- [ ] Draw a star schema for a given use case
- [ ] Understand batch vs streaming ETL trade-offs

**INTERMEDIATE:**
- [ ] Build a Python ETL pipeline from scratch
- [ ] Extract data from multiple sources (DB, API, files)
- [ ] Implement data quality checks
- [ ] Load data into a star schema
- [ ] Handle late-arriving data
- [ ] Implement SCD Type 2

**EXPERT:**
- [ ] Design a data warehouse for a given business (e.g., food delivery)
- [ ] Partition and shard large fact tables
- [ ] Optimize queries with pre-aggregation
- [ ] Choose between star schema, Data Vault, or Activity Schema
- [ ] Answer FAANG-level system design questions

**WHITEPAPERS:**
- [ ] Compare Kimball vs Inmon methodologies
- [ ] Explain when to use each SCD type
- [ ] Understand the evolution: Kimball → Inmon → Big Data → Modern Data Stack
- [ ] Apply dbt best practices

---

## 🛠️ **Hands-On Exercises**

### **Exercise 1: Design a Star Schema** (BEGINNER)
**Scenario:** You're building analytics for a ride-sharing app (like Uber).

**Task:**
1. Identify the business process (hint: trips)
2. Declare the grain (one row per ?)
3. List dimensions (driver, rider, location, time, ...)
4. List facts (distance, duration, fare, ...)
5. Draw the star schema

**Solution:** Check BEGINNER.md

---

### **Exercise 2: Build an ETL Pipeline** (INTERMEDIATE)
**Scenario:** Extract product data from Shopify API, transform, and load to warehouse.

**Task:**
1. Write `extract_shopify_products()` function
2. Clean product names (remove HTML tags, fix encoding)
3. Implement SCD Type 2 for price changes
4. Load to `dim_products` with `effective_date`, `end_date`, `is_current`

**Starter Code:**
```python
import requests
import pandas as pd

def extract_shopify_products():
    # TODO: Call Shopify API
    pass

def transform_products(df):
    # TODO: Clean and implement SCD Type 2
    pass

def load_to_warehouse(df):
    # TODO: Upsert to dim_products
    pass
```

**Solution:** Check INTERMEDIATE.md

---

### **Exercise 3: System Design Question** (EXPERT)
**Question:** Design a data warehouse for a video streaming platform (like Netflix).

**Requirements:**
- Track viewing events (play, pause, stop)
- Support real-time dashboards (current viewers)
- Support historical analytics (viewing trends)
- Handle 500,000 events/second
- Store 7 years of history

**What to include:**
- Architecture diagram
- Data model (star schema)
- Partitioning strategy
- Pre-aggregation approach
- Query examples

**Solution:** Check EXPERT.md

---

## 📊 **Success Metrics**

### **Knowledge Checks:**

**After BEGINNER:**
- ✅ "Explain ETL to a non-technical friend"
- ✅ "Draw a star schema for an e-commerce order"
- ✅ "What's the difference between a fact and a dimension?"

**After INTERMEDIATE:**
- ✅ "Build an ETL pipeline that extracts from API and loads to database"
- ✅ "Implement SCD Type 2 in SQL or Python"
- ✅ "Handle duplicate data in an idempotent way"

**After EXPERT:**
- ✅ "Design a data warehouse for 100M users and 1B events/day"
- ✅ "Choose the right partitioning strategy for time-series data"
- ✅ "Explain when to denormalize and when to normalize"

**After WHITEPAPERS:**
- ✅ "Debate Kimball vs Inmon approaches"
- ✅ "Explain the evolution from ETL to ELT to dbt"
- ✅ "Justify SCD type choice for different scenarios"

---

## 🔗 **Connections to Other Weeks**

### **Prerequisite:**
- **Week 1: MapReduce** - Understanding distributed processing helps with large-scale ETL

### **Builds Toward:**
- **Week 3: SQL Deep Dive** - Query optimization for star schemas
- **Week 4: Apache Spark** - Distributed ETL at scale
- **Week 5: Data Warehousing** - Columnar storage (Parquet, BigQuery internals)
- **Week 6-10: Kafka** - Real-time ETL (streaming)
- **Week 13-14: Lakehouse** - Modern architecture combining ETL + data lakes

---

## 🧭 **Navigation**

**Current Module:**
- 🌱 [BEGINNER](./BEGINNER.md) - Restaurant kitchen analogy, star schema basics
- 🔨 [INTERMEDIATE](./INTERMEDIATE.md) - Python ETL pipeline implementation
- 🏗️ [EXPERT](./EXPERT.md) - Netflix/Airbnb/Uber architectures
- 📄 [WHITEPAPERS](./WHITEPAPERS.md) - Kimball & Inmon methodologies

**Other Weeks:**
- ⬅️ [Week 1: MapReduce](../1A_MapReduce/README.md)
- ➡️ Week 3: SQL Deep Dive (Coming soon)
- 🏠 [Master Roadmap](../../00-MASTER-ROADMAP.md)

---

## 💡 **Pro Tips**

### **For BEGINNERS:**
1. **Start with analogies** - Restaurant kitchen helps visualize ETL flow
2. **Draw diagrams** - Sketch star schemas by hand before coding
3. **Use real examples** - Think about your favorite apps (Uber, Netflix, Amazon)

### **For INTERMEDIATE:**
1. **Run the code** - Don't just read, execute the Python pipeline
2. **Break it** - Try loading duplicate data, see idempotency in action
3. **Extend it** - Add a new data source (CSV file, different API)

### **For EXPERT:**
1. **Think trade-offs** - Every design decision has pros/cons
2. **Estimate scale** - Calculate data volumes (rows/day × columns × bytes)
3. **Practice interviews** - Use the 10 questions to prepare for FAANG

### **For WHITEPAPERS:**
1. **Take notes** - Summarize Kimball's 4-step process in your own words
2. **Compare methodologies** - Create a table: Kimball vs Inmon vs Modern
3. **Apply to work** - Which approach does your company use? Why?

---

## 🚀 **Next Steps**

### **Just Finished This Module?**

**Option 1: Reinforce Learning**
- Build your own ETL pipeline for a personal project
- Recreate one of the architectures (Netflix/Airbnb/Uber) in a local database
- Write a blog post explaining star schema to others

**Option 2: Dive Deeper**
- Read Kimball's full book: *The Data Warehouse Toolkit*
- Explore dbt documentation: https://docs.getdbt.com/
- Watch conference talks: dbt Coalesce, Snowflake Summit

**Option 3: Move Forward**
- Continue to **Week 3: SQL Deep Dive**
- Skip to **Week 6: Kafka** if you want real-time ETL
- Jump to **Week 13: Lakehouse** for modern architectures

---

## 📚 **Additional Resources**

### **Books:**
- Kimball, Ralph. *The Data Warehouse Toolkit* (3rd Ed., 2013)
- Inmon, William H. *Building the Data Warehouse* (4th Ed., 2005)
- Kleppmann, Martin. *Designing Data-Intensive Applications* (2017)

### **Online Courses:**
- Coursera: Data Warehousing for Business Intelligence Specialization
- Udacity: Data Engineering Nanodegree
- dbt Learn: https://learn.getdbt.com/

### **Tools to Explore:**
- **Databases:** PostgreSQL, MySQL (practice SQL)
- **Cloud Warehouses:** Snowflake (free trial), BigQuery (free tier), Redshift
- **ETL Tools:** Apache Airflow, Prefect, Dagster
- **dbt:** dbt Cloud (free tier)

### **Communities:**
- dbt Slack: https://www.getdbt.com/community/
- r/dataengineering on Reddit
- Locally Optimistic Slack (analytics engineering)

---

## ❓ **FAQ**

**Q: Should I start with BEGINNER or INTERMEDIATE?**  
A: If you've never designed a data warehouse, start with BEGINNER. If you already know star schemas, skip to INTERMEDIATE.

**Q: Do I need to read WHITEPAPERS?**  
A: Not required, but highly recommended if you want to understand the "why" behind industry practices.

**Q: What tools do I need?**  
A: For INTERMEDIATE, you need Python and a database (PostgreSQL or SQLite). For EXPERT, just pen and paper for system design.

**Q: How long should this week take?**  
A: 
- BEGINNER: 2-3 hours
- INTERMEDIATE: 4-5 hours (including coding)
- EXPERT: 6-8 hours (including practice interviews)
- WHITEPAPERS: 3-4 hours
- **Total: 15-20 hours for full mastery**

**Q: Kimball or Inmon - which should I use?**  
A: Modern approach: Inmon for data lake (raw/cleaned layers), Kimball for data marts (star schemas). See WHITEPAPERS for details.

**Q: What's the difference between ETL and ELT?**  
A: 
- **ETL:** Transform before loading (traditional, Talend/Informatica)
- **ELT:** Load raw data first, transform in warehouse (modern, dbt)
- See WHITEPAPERS for evolution timeline.

---

## 🎉 **Congratulations!**

You've completed **Week 2: ETL Pipelines & Data Modeling**!

You now understand:
- ✅ How to build ETL pipelines from scratch
- ✅ Star schema design for analytics
- ✅ Slowly Changing Dimensions (SCD)
- ✅ Real-world architectures at Netflix, Airbnb, Uber
- ✅ Kimball vs Inmon methodologies
- ✅ Modern data stack (dbt, ELT, lakehouse)

**You're ready for:**
- Week 3: SQL Deep Dive (query optimization, indexes)
- Week 4: Apache Spark (distributed ETL)
- Week 6-10: Kafka (real-time streaming ETL)

---

**Keep learning! 🚀**

**Next:** [Week 3: SQL Deep Dive](../1C_SQL_Deep_Dive/README.md) (Coming soon)

**Master Roadmap:** [00-MASTER-ROADMAP.md](../../00-MASTER-ROADMAP.md)
