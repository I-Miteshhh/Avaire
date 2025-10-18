# Search Engine - Production Implementation

**Target Scale:** Handle **10,000+ queries/sec** with **<100ms latency** across **1B+ documents**

---

## Table of Contents
1. [Problem Statement](#1-problem-statement)
2. [Requirements](#2-requirements)
3. [Core Concepts](#3-core-concepts)
4. [Architecture](#4-architecture)
5. [Inverted Index](#5-inverted-index)
6. [Ranking Algorithms](#6-ranking-algorithms)
7. [Query Processing](#7-query-processing)

---

## 1. Problem Statement

### What is a Search Engine?

A search engine indexes and searches through large document collections to find relevant results for user queries.

**Real-World Examples:**
- **Google:** 8.5 billion searches/day, 130 trillion pages indexed
- **Elasticsearch:** 100M+ downloads, used by Uber, Netflix, GitHub
- **Solr:** Used by Apple, Netflix, eBay
- **Amazon Product Search:** 300M+ products, 100K queries/sec

---

### Use Cases

1. **Web Search:** Google, Bing
2. **E-commerce:** Product search (Amazon, eBay)
3. **Enterprise Search:** Document search, knowledge base
4. **Log Search:** Application logs, security logs (Elasticsearch)
5. **Social Media:** Tweet search, hashtag search

---

## 2. Requirements

### Functional Requirements

1. **Indexing:**
   - Crawl and index documents
   - Update index in near real-time
   - Handle 100K+ documents/sec indexing rate

2. **Search:**
   - Full-text search
   - Boolean operators (AND, OR, NOT)
   - Phrase search ("exact phrase")
   - Wildcard search (oper* → operator, operating)
   - Fuzzy search (operatr → operator)

3. **Ranking:**
   - Relevance scoring (TF-IDF, BM25)
   - Custom boosting (boost recent documents)
   - Personalization (user history, location)

4. **Filtering:**
   - Filter by fields (category, price, date)
   - Range queries (price: 100-500)
   - Geo queries (restaurants within 5km)

### Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Query Latency (P99) | <100ms |
| Indexing Throughput | 100K docs/sec |
| Query Throughput | 10K queries/sec |
| Index Size | 1B+ documents |
| Availability | 99.9% |
| Data Freshness | <1 second (near real-time) |

### Scale Estimates

```
Assumptions:
- 1 billion documents
- Average document size: 10 KB
- Average indexing expansion: 3x (inverted index overhead)

Storage:
  Raw documents: 1B × 10 KB = 10 TB
  Inverted index: 10 TB × 3 = 30 TB
  Total: 40 TB (with compression: ~20 TB)

Queries:
  10,000 queries/sec peak
  Average query: 3 terms
  Index lookups: 30,000 lookups/sec

Indexing:
  100,000 documents/sec
  Average terms per doc: 1,000
  Index updates: 100M term updates/sec
```

---

## 3. Core Concepts

### 3.1 Inverted Index

**Forward Index:** Document → Terms
```
Doc1: "quick brown fox"
Doc2: "quick blue fox"
Doc3: "slow brown dog"
```

**Inverted Index:** Term → Documents
```
quick → [Doc1, Doc2]
brown → [Doc1, Doc3]
blue  → [Doc2]
fox   → [Doc1, Doc2]
slow  → [Doc3]
dog   → [Doc3]
```

**With Positions (for phrase search):**
```
quick → [Doc1:[0], Doc2:[0]]
brown → [Doc1:[1], Doc3:[1]]
fox   → [Doc1:[2], Doc2:[2]]
```

---

### 3.2 Text Analysis Pipeline

```
Original: "The QUICK Brown fox's jumped!"
   ↓
1. Lowercase: "the quick brown fox's jumped!"
   ↓
2. Remove punctuation: "the quick brown foxs jumped"
   ↓
3. Tokenize: ["the", "quick", "brown", "foxs", "jumped"]
   ↓
4. Remove stopwords: ["quick", "brown", "foxs", "jumped"]
   ↓
5. Stemming: ["quick", "brown", "fox", "jump"]
   ↓
Final tokens: ["quick", "brown", "fox", "jump"]
```

---

### 3.3 Document Representation

```protobuf
// document.proto
message Document {
  string id = 1;
  string title = 2;
  string body = 3;
  map<string, string> fields = 4;  // category, author, etc.
  int64 timestamp = 5;
  float boost = 6;  // Manual relevance boost
}

message IndexedDocument {
  string doc_id = 1;
  repeated Term terms = 2;
  int32 doc_length = 3;  // Number of terms
  map<string, string> stored_fields = 4;
}

message Term {
  string text = 1;
  repeated Position positions = 2;
  float tf = 3;  // Term frequency in document
}

message Position {
  int32 position = 1;
  int32 start_offset = 2;
  int32 end_offset = 3;
}
```

---

## 4. Architecture

### High-Level Design

```
┌────────────────────────────────────────────────────────────┐
│                    Indexing Pipeline                        │
│                                                             │
│  Documents → Text Analysis → Inverted Index Builder        │
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────────┐        │
│  │Tokenizer │ → │ Analyzer │ → │ Index Writer │         │
│  └──────────┘    └──────────┘    └──────────────┘        │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│                   Index Storage                             │
│                                                             │
│  Shard 1              Shard 2              Shard 3         │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐ │
│  │Inverted     │     │Inverted     │     │Inverted     │ │
│  │Index        │     │Index        │     │Index        │ │
│  │             │     │             │     │             │ │
│  │[term→docs]  │     │[term→docs]  │     │[term→docs]  │ │
│  └─────────────┘     └─────────────┘     └─────────────┘ │
│         ↑                   ↑                   ↑          │
│  ┌──────┴──────┐     ┌──────┴──────┐     ┌──────┴──────┐ │
│  │Doc Store    │     │Doc Store    │     │Doc Store    │ │
│  │[id→content] │     │[id→content] │     │[id→content] │ │
│  └─────────────┘     └─────────────┘     └─────────────┘ │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│                   Query Processing                          │
│                                                             │
│  Query → Parse → Term Lookup → Score → Rank → Return      │
│                                                             │
│  "brown fox" → [brown, fox] → Merge → BM25 → Top 10       │
└────────────────────────────────────────────────────────────┘
```

---

## 5. Inverted Index Implementation

### 5.1 Core Data Structures

```go
// index/inverted_index.go
package index

import (
    "sort"
    "sync"
)

type InvertedIndex struct {
    index   map[string]*PostingList
    docStore map[string]*Document
    mu      sync.RWMutex
    docCount int
    avgDocLength float64
}

type PostingList struct {
    term      string
    docFreq   int  // Number of documents containing term
    postings  []*Posting
}

type Posting struct {
    docID     string
    termFreq  int  // Number of times term appears in document
    positions []int
}

func NewInvertedIndex() *InvertedIndex {
    return &InvertedIndex{
        index:    make(map[string]*PostingList),
        docStore: make(map[string]*Document),
    }
}

// AddDocument: Index a document
func (idx *InvertedIndex) AddDocument(doc *Document) error {
    idx.mu.Lock()
    defer idx.mu.Unlock()
    
    // Analyze document text
    terms := idx.analyze(doc.Body)
    
    // Build term frequency map
    termFreqs := make(map[string][]int)  // term → positions
    for pos, term := range terms {
        termFreqs[term] = append(termFreqs[term], pos)
    }
    
    // Update inverted index
    for term, positions := range termFreqs {
        postingList, exists := idx.index[term]
        if !exists {
            postingList = &PostingList{
                term:     term,
                postings: make([]*Posting, 0),
            }
            idx.index[term] = postingList
        }
        
        posting := &Posting{
            docID:     doc.ID,
            termFreq:  len(positions),
            positions: positions,
        }
        
        postingList.postings = append(postingList.postings, posting)
        postingList.docFreq++
    }
    
    // Store document
    idx.docStore[doc.ID] = doc
    idx.docCount++
    idx.updateAvgDocLength(len(terms))
    
    return nil
}

func (idx *InvertedIndex) analyze(text string) []string {
    // 1. Lowercase
    text = strings.ToLower(text)
    
    // 2. Tokenize
    tokens := strings.Fields(text)
    
    // 3. Remove stopwords
    filtered := make([]string, 0)
    stopwords := map[string]bool{
        "the": true, "a": true, "an": true, "and": true, "or": true,
        "but": true, "in": true, "on": true, "at": true, "to": true,
    }
    
    for _, token := range tokens {
        // Remove punctuation
        token = strings.Trim(token, ".,!?;:\"'")
        
        if !stopwords[token] && token != "" {
            // 4. Stemming (simple version)
            stemmed := idx.stem(token)
            filtered = append(filtered, stemmed)
        }
    }
    
    return filtered
}

func (idx *InvertedIndex) stem(word string) string {
    // Simple stemming: remove common suffixes
    suffixes := []string{"ing", "ed", "s"}
    
    for _, suffix := range suffixes {
        if strings.HasSuffix(word, suffix) {
            return strings.TrimSuffix(word, suffix)
        }
    }
    
    return word
}

func (idx *InvertedIndex) updateAvgDocLength(docLength int) {
    total := idx.avgDocLength * float64(idx.docCount-1)
    idx.avgDocLength = (total + float64(docLength)) / float64(idx.docCount)
}
```

---

### 5.2 Query Processing

```go
// index/search.go
package index

type SearchResult struct {
    DocID string
    Score float64
    Doc   *Document
}

// Search: Execute search query
func (idx *InvertedIndex) Search(query string, limit int) ([]*SearchResult, error) {
    idx.mu.RLock()
    defer idx.mu.RUnlock()
    
    // Analyze query
    queryTerms := idx.analyze(query)
    
    if len(queryTerms) == 0 {
        return nil, fmt.Errorf("empty query")
    }
    
    // Get posting lists for each term
    postingLists := make([]*PostingList, 0)
    for _, term := range queryTerms {
        if pl, exists := idx.index[term]; exists {
            postingLists = append(postingLists, pl)
        }
    }
    
    if len(postingLists) == 0 {
        return []*SearchResult{}, nil
    }
    
    // Merge posting lists (AND operation)
    candidates := idx.mergePostingLists(postingLists)
    
    // Score each candidate
    results := make([]*SearchResult, 0, len(candidates))
    for docID := range candidates {
        score := idx.score(docID, queryTerms)
        
        results = append(results, &SearchResult{
            DocID: docID,
            Score: score,
            Doc:   idx.docStore[docID],
        })
    }
    
    // Sort by score (descending)
    sort.Slice(results, func(i, j int) bool {
        return results[i].Score > results[j].Score
    })
    
    // Return top N
    if len(results) > limit {
        results = results[:limit]
    }
    
    return results, nil
}

// mergePostingLists: Find documents containing ALL query terms
func (idx *InvertedIndex) mergePostingLists(lists []*PostingList) map[string]bool {
    if len(lists) == 0 {
        return nil
    }
    
    // Start with shortest list (optimization)
    sort.Slice(lists, func(i, j int) bool {
        return len(lists[i].postings) < len(lists[j].postings)
    })
    
    candidates := make(map[string]bool)
    
    // Initialize with first list
    for _, posting := range lists[0].postings {
        candidates[posting.docID] = true
    }
    
    // Intersect with remaining lists
    for i := 1; i < len(lists); i++ {
        docSet := make(map[string]bool)
        for _, posting := range lists[i].postings {
            docSet[posting.docID] = true
        }
        
        // Keep only docs in both sets
        for docID := range candidates {
            if !docSet[docID] {
                delete(candidates, docID)
            }
        }
    }
    
    return candidates
}
```

---

## 6. Ranking Algorithms

### 6.1 TF-IDF (Term Frequency - Inverse Document Frequency)

**Formula:**
```
TF-IDF(term, doc) = TF(term, doc) × IDF(term)

TF(term, doc) = frequency of term in document / total terms in document

IDF(term) = log(total documents / documents containing term)
```

**Implementation:**
```go
// ranking/tfidf.go
package ranking

import (
    "math"
)

type TFIDFScorer struct {
    index *InvertedIndex
}

func (s *TFIDFScorer) Score(docID string, queryTerms []string) float64 {
    score := 0.0
    doc := s.index.docStore[docID]
    docLength := len(s.index.analyze(doc.Body))
    
    for _, term := range queryTerms {
        postingList := s.index.index[term]
        if postingList == nil {
            continue
        }
        
        // Find posting for this document
        var posting *Posting
        for _, p := range postingList.postings {
            if p.docID == docID {
                posting = p
                break
            }
        }
        
        if posting == nil {
            continue
        }
        
        // Calculate TF
        tf := float64(posting.termFreq) / float64(docLength)
        
        // Calculate IDF
        idf := math.Log(float64(s.index.docCount) / float64(postingList.docFreq))
        
        score += tf * idf
    }
    
    return score
}
```

---

### 6.2 BM25 (Best Matching 25)

**Formula:**
```
BM25(D, Q) = Σ IDF(qi) × (f(qi, D) × (k1 + 1)) / (f(qi, D) + k1 × (1 - b + b × |D| / avgdl))

Where:
- f(qi, D) = frequency of term qi in document D
- |D| = length of document D
- avgdl = average document length
- k1 = 1.2 (term frequency saturation parameter)
- b = 0.75 (length normalization parameter)
```

**Implementation:**
```go
// ranking/bm25.go
package ranking

import (
    "math"
)

type BM25Scorer struct {
    index *InvertedIndex
    k1    float64  // Term frequency saturation (default: 1.2)
    b     float64  // Length normalization (default: 0.75)
}

func NewBM25Scorer(index *InvertedIndex) *BM25Scorer {
    return &BM25Scorer{
        index: index,
        k1:    1.2,
        b:     0.75,
    }
}

func (s *BM25Scorer) Score(docID string, queryTerms []string) float64 {
    score := 0.0
    doc := s.index.docStore[docID]
    docLength := float64(len(s.index.analyze(doc.Body)))
    avgDocLength := s.index.avgDocLength
    
    for _, term := range queryTerms {
        postingList := s.index.index[term]
        if postingList == nil {
            continue
        }
        
        // Find posting for this document
        var posting *Posting
        for _, p := range postingList.postings {
            if p.docID == docID {
                posting = p
                break
            }
        }
        
        if posting == nil {
            continue
        }
        
        // IDF
        idf := math.Log((float64(s.index.docCount) - float64(postingList.docFreq) + 0.5) /
            (float64(postingList.docFreq) + 0.5))
        
        // Term frequency
        tf := float64(posting.termFreq)
        
        // Length normalization
        norm := 1 - s.b + s.b*(docLength/avgDocLength)
        
        // BM25 score
        termScore := idf * (tf * (s.k1 + 1)) / (tf + s.k1*norm)
        score += termScore
    }
    
    return score
}
```

**Why BM25 is better than TF-IDF:**
1. **Term frequency saturation:** Diminishing returns for repeated terms
2. **Length normalization:** Fair comparison between short and long documents
3. **Better empirical performance:** Used by Elasticsearch, Solr

---

**Continued in next part...**
