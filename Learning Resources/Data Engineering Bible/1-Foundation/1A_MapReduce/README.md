# Week 1: MapReduce & Distributed Systems

## 📚 **Module Overview**

Welcome to Week 1 of the Data Engineering Bible! This module provides a **complete understanding** of MapReduce and distributed systems—from beginner-friendly analogies to Principal-level architectural depth.

---

## 🎯 **What You'll Learn**

By completing this module, you will:

✅ Understand why "bring compute to data" revolutionized big data  
✅ Explain the Map → Shuffle → Reduce workflow  
✅ Build a working MapReduce framework in Python  
✅ Debug data skew, stragglers, and failures  
✅ Analyze Google's production MapReduce architecture  
✅ Compare MapReduce vs Spark vs modern systems  
✅ Ace 10+ FAANG-level interview questions  

---

## 📂 **Module Structure**

This module is organized into **four progressive levels**:

### **📄 [BEGINNER.md](./BEGINNER.md)**
**Target:** Software engineers new to data engineering  
**Time:** 2-3 hours

**What's Inside:**
- Santa's Workshop analogy for MapReduce
- Prerequisites: GFS, distributed systems, "bring compute to data"
- ASCII diagrams showing Map → Shuffle → Reduce
- Fun metaphors: Pizza restaurant, library, election counting
- Key takeaways and next steps

**Start here if:**
- You've never worked with distributed systems
- You want intuitive, visual explanations
- You need a refresher on fundamentals

---

### **🛠️ [INTERMEDIATE.md](./INTERMEDIATE.md)**
**Target:** Engineers with 1-2 years experience  
**Time:** 4-5 hours

**What's Inside:**
- Build a complete MapReduce framework in Python (200+ lines)
- Hands-on labs: word count, combiners, data skew handling
- Mental models: data locality, partitioning, fault tolerance
- Debugging guide: stragglers, small files, failures
- Common patterns: filtering, joins, secondary sort
- 5 interview questions with detailed answers

**Start here if:**
- You understand the basics and want to build
- You learn best by coding
- You're preparing for mid-level interviews

---

### **🏗️ [EXPERT.md](./EXPERT.md)**
**Target:** Senior/Staff/Principal engineers  
**Time:** 6-8 hours

**What's Inside:**
- Complete MapReduce architecture breakdown
- Critical design decisions and trade-offs
- Master node implementation details
- Real-world usage: Google search indexing, Facebook logs, Yahoo grid
- Why MapReduce "failed" and evolution to Spark/Flink
- Performance optimization techniques
- 10 FAANG-level system design questions

**Start here if:**
- You're targeting Staff/Principal roles
- You want to understand production systems at scale
- You're designing distributed data platforms

---

### **📄 [WHITEPAPERS.md](./WHITEPAPERS.md)**
**Target:** Deep technical understanding  
**Time:** 3-4 hours

**What's Inside:**
- Complete summary of MapReduce (2004) paper
- Complete summary of GFS (2003) paper
- Historical context and industry impact
- Key innovations and design decisions
- Performance results and limitations
- How MapReduce + GFS work together
- Modern equivalents and follow-on research

**Start here if:**
- You want academic-level rigor
- You're curious about the "why" behind design choices
- You want to read papers without actually reading papers 😉

---

## 🎓 **Recommended Learning Paths**

### **Path 1: Sequential (Full Mastery)**
Recommended for most learners.

```
Day 1: BEGINNER (2-3 hours)
  ↓
Day 2: INTERMEDIATE Part 1 (3 hours)
  ↓
Day 3: INTERMEDIATE Part 2 + Labs (3 hours)
  ↓
Day 4: EXPERT Part 1 (4 hours)
  ↓
Day 5: EXPERT Part 2 (4 hours)
  ↓
Day 6: WHITEPAPERS (3-4 hours)
  ↓
Day 7: Review + Capstone Exercise

Total: ~25 hours
```

---

### **Path 2: Fast Track (Interview Prep)**
For experienced engineers with time constraints.

```
Hour 1-2: BEGINNER (skim, focus on diagrams)
  ↓
Hour 3-6: INTERMEDIATE (build working code)
  ↓
Hour 7-12: EXPERT (focus on interview questions)

Total: ~12 hours
```

---

### **Path 3: Deep Dive (Researcher/Architect)**
For those designing new systems.

```
Day 1: BEGINNER + INTERMEDIATE (foundations)
  ↓
Day 2-3: WHITEPAPERS (academic depth)
  ↓
Day 4-5: EXPERT (production patterns)
  ↓
Day 6: Compare with Spark/Flink/Beam

Total: ~30 hours
```

---

## 🔑 **Key Concepts**

### **Core Ideas**
- **Map:** Transform each record independently
- **Shuffle:** Group records by key (framework handles this!)
- **Reduce:** Aggregate values per key
- **Fault Tolerance:** Re-execute failed tasks
- **Data Locality:** Compute where data is stored

### **Critical Trade-offs**
- **Simplicity vs Performance:** Re-execution is simple but slower than checkpointing
- **Disk vs Network:** Store intermediate data locally (fast) but re-run if lost
- **Batch vs Stream:** Optimized for batch, not real-time

### **Evolution**
```
MapReduce (2004)
  ↓ (Limitations: Disk I/O, no iterations)
Spark (2010)
  ↓ (Limitations: Only batch)
Beam (2015)
  ↓ (Unified batch + stream)
```

---

## 📊 **Visual Learning Guide**

### **The Big Picture**

```
┌─────────────────────────────────────────────┐
│         INPUT DATA (GFS/HDFS)              │
│  Large files split into 64MB chunks        │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│           MAP PHASE (Parallel)              │
│  Each worker processes one chunk           │
│  Outputs: (key, value) pairs               │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         SHUFFLE & SORT (Automatic)          │
│  Framework groups by key                   │
│  Network transfer: M mappers → R reducers  │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         REDUCE PHASE (Parallel)             │
│  Each worker processes one key partition   │
│  Outputs: Aggregated results               │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│        OUTPUT DATA (GFS/HDFS)              │
│  Final results (replicated 3x)             │
└─────────────────────────────────────────────┘
```

---

## 🎯 **Learning Outcomes by Level**

### **After BEGINNER:**
- Explain MapReduce to a non-technical person
- Draw the Map → Shuffle → Reduce flow
- Understand why it was revolutionary

### **After INTERMEDIATE:**
- Implement word count in MapReduce
- Debug data skew and stragglers
- Optimize with combiners
- Pass junior/mid-level interviews

### **After EXPERT:**
- Design distributed grep, sort, join algorithms
- Explain Google's production architecture
- Compare MapReduce vs Spark trade-offs
- Pass Staff/Principal interviews

### **After WHITEPAPERS:**
- Discuss MapReduce paper innovations
- Understand GFS design decisions
- Know the historical evolution
- Read other distributed systems papers

---

## 💡 **Interview Question Preview**

Here are sample questions covered in this module:

**Easy (INTERMEDIATE):**
1. What is the purpose of the combiner?
2. How does MapReduce handle failures?
3. What causes data skew and how do you fix it?

**Medium (INTERMEDIATE):**
4. Implement PageRank in MapReduce
5. Compare MapReduce with traditional databases

**Hard (EXPERT):**
6. Design distributed grep for 1PB of logs
7. Handle 99/1 data skew (one key dominates)
8. Explain exactly-once vs at-least-once semantics
9. How does speculative execution work? Trade-offs?
10. Design real-time query system using MapReduce

**System Design (EXPERT):**
11. Compute top 1M words from 1PB corpus
12. Implement distributed TeraSort
13. Explain shuffle phase internals
14. Compare MapReduce vs Spark for joins

*Full answers with explanations in INTERMEDIATE and EXPERT sections!*

---

## 🧪 **Hands-On Exercises**

### **Exercise 1: Basic Implementation**
Build a working MapReduce framework in Python (from INTERMEDIATE).

**Skills:** Programming, system design  
**Time:** 2-3 hours  
**Difficulty:** Medium

---

### **Exercise 2: Optimization Challenge**
Optimize word count with combiner, measure performance improvement.

**Skills:** Performance tuning  
**Time:** 1 hour  
**Difficulty:** Easy

---

### **Exercise 3: Data Skew Simulation**
Create a dataset with 99/1 skew, implement salting solution.

**Skills:** Debugging, advanced patterns  
**Time:** 2 hours  
**Difficulty:** Hard

---

## 📈 **Success Metrics**

**You've mastered this module when you can:**

✅ **Explain** MapReduce to both engineers and non-technical stakeholders  
✅ **Implement** a working MapReduce framework from scratch  
✅ **Debug** failures, stragglers, and data skew in production  
✅ **Design** distributed algorithms (grep, sort, join, PageRank)  
✅ **Compare** MapReduce vs Spark vs Flink with specific trade-offs  
✅ **Ace** FAANG interviews on distributed data processing  

---

## 🚀 **Next Steps**

After completing Week 1:

**Option 1: Continue Foundation Phase**
- [Week 2: ETL Pipelines & Data Modeling](../1B_ETL_Basics/BEGINNER.md)

**Option 2: Deep Dive into Spark**
- [Week 4: Apache Spark Fundamentals](../1D_Spark_Fundamentals/BEGINNER.md)

**Option 3: Jump to Streaming**
- [Week 6: Apache Kafka Deep Dive](../../2-Intermediate/2A_Kafka_Fundamentals/BEGINNER.md)

---

## 📚 **Additional Resources**

### **Inside This Module:**
- [BEGINNER.md](./BEGINNER.md) - Start here!
- [INTERMEDIATE.md](./INTERMEDIATE.md) - Hands-on implementation
- [EXPERT.md](./EXPERT.md) - Production systems
- [WHITEPAPERS.md](./WHITEPAPERS.md) - Academic papers digested

### **Related Topics:**
- [GFS Architecture](./WHITEPAPERS.md#paper-2-the-google-file-system-2003)
- [Hadoop HDFS](../1D_Spark_Fundamentals/EXPERT.md) (Week 4)
- [Apache Spark](../1D_Spark_Fundamentals/BEGINNER.md) (Week 4)

---

## 🎉 **Ready to Begin?**

**Start with:** [BEGINNER.md](./BEGINNER.md)

**Remember:**
- Take breaks every hour
- Draw diagrams as you learn
- Code along with examples
- Ask "why?" at every step

**Your journey to FAANG-level data engineering mastery starts now!** 🚀

---

*Module 1 of 16 | Foundation Phase*  
*Estimated completion: 20-30 hours*
