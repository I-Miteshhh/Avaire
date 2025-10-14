# Week 10-11: Apache Beam — WHITEPAPERS Track

*"The Dataflow Model paper fundamentally changed how we think about stream processing. Understanding it deeply is essential for any data engineer."* — Engineering Fellow, Microsoft

---

## 📜 1. The Dataflow Model (2015) - Google

**Citation:** Akidau, Tyler, et al. "The dataflow model: a practical approach to balancing correctness, latency, and cost in massive-scale, unbounded, out-of-order data processing." VLDB 2015.

**Link:** http://www.vldb.org/pvldb/vol8/p1792-Akidau.pdf

### Core Innovation: What/Where/When/How

```
The Four Questions Framework:

1. WHAT computations?
   → ParDo, GroupByKey, Combine transformations

2. WHERE in event time?
   → Fixed, Sliding, Session, Global windows

3. WHEN to emit results?
   → Triggers: Watermark, ProcessingTime, Count, Composite

4. HOW to refine results?
   → Accumulation: Discarding, Accumulating, Retracting
```

**Problem Solved:** Lambda architecture requires two codebases (batch + stream). Dataflow unifies them.

---

## 📜 2. MillWheel: Fault-Tolerant Stream Processing (2013) - Google

**Citation:** Akidau, Tyler, et al. "MillWheel: fault-tolerant stream processing at internet scale." VLDB 2013.

**Key Concepts:**
- Strong consistency with exactly-once delivery
- Low watermarks for progress tracking
- Persistent state with checkpointing

**Beam's Implementation:** Watermarks, exactly-once semantics, stateful processing inherited from MillWheel.

---

## 🎓 Summary

- [ ] Understand Dataflow Model's four questions
- [ ] Explain MillWheel's watermark mechanism
- [ ] Compare Lambda vs Kappa architectures

**Next:** [README.md →](README.md)
