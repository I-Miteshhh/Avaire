# Search Engine - Part 2: Advanced Features & Production

**Continued from README.md**

---

## 7. Advanced Query Features

### 7.1 Phrase Search

```go
// query/phrase_search.go
package query

// PhraseSearch: Find documents containing exact phrase
func (idx *InvertedIndex) PhraseSearch(phrase string, limit int) ([]*SearchResult, error) {
    terms := idx.analyze(phrase)
    
    if len(terms) < 2 {
        return idx.Search(phrase, limit)
    }
    
    // Get posting lists
    postingLists := make([]*PostingList, len(terms))
    for i, term := range terms {
        pl, exists := idx.index[term]
        if !exists {
            return []*SearchResult{}, nil
        }
        postingLists[i] = pl
    }
    
    // Find documents with all terms
    candidates := idx.mergePostingLists(postingLists)
    
    // Check position adjacency
    results := make([]*SearchResult, 0)
    
    for docID := range candidates {
        if idx.hasPhrase(docID, terms, postingLists) {
            score := idx.score(docID, terms) * 2.0  // Boost phrase matches
            results = append(results, &SearchResult{
                DocID: docID,
                Score: score,
                Doc:   idx.docStore[docID],
            })
        }
    }
    
    // Sort and limit
    sort.Slice(results, func(i, j int) bool {
        return results[i].Score > results[j].Score
    })
    
    if len(results) > limit {
        results = results[:limit]
    }
    
    return results, nil
}

func (idx *InvertedIndex) hasPhrase(docID string, terms []string, postingLists []*PostingList) bool {
    // Get positions for each term in this document
    termPositions := make([][]int, len(terms))
    
    for i, pl := range postingLists {
        for _, posting := range pl.postings {
            if posting.docID == docID {
                termPositions[i] = posting.positions
                break
            }
        }
    }
    
    // Check if positions are adjacent
    for _, pos0 := range termPositions[0] {
        hasPhrase := true
        for i := 1; i < len(terms); i++ {
            expectedPos := pos0 + i
            found := false
            
            for _, pos := range termPositions[i] {
                if pos == expectedPos {
                    found = true
                    break
                }
            }
            
            if !found {
                hasPhrase = false
                break
            }
        }
        
        if hasPhrase {
            return true
        }
    }
    
    return false
}
```

---

### 7.2 Fuzzy Search (Edit Distance)

```go
// query/fuzzy_search.go
package query

// FuzzySearch: Find terms within edit distance
func (idx *InvertedIndex) FuzzySearch(query string, maxDistance int, limit int) ([]*SearchResult, error) {
    queryTerms := idx.analyze(query)
    
    // For each query term, find similar terms
    expandedTerms := make([]string, 0)
    
    for _, queryTerm := range queryTerms {
        similar := idx.findSimilarTerms(queryTerm, maxDistance)
        expandedTerms = append(expandedTerms, similar...)
    }
    
    // Search with expanded terms
    return idx.Search(strings.Join(expandedTerms, " "), limit)
}

func (idx *InvertedIndex) findSimilarTerms(term string, maxDistance int) []string {
    similar := []string{term}  // Include exact match
    
    for indexedTerm := range idx.index {
        distance := levenshteinDistance(term, indexedTerm)
        if distance > 0 && distance <= maxDistance {
            similar = append(similar, indexedTerm)
        }
    }
    
    return similar
}

// Levenshtein distance (edit distance)
func levenshteinDistance(s1, s2 string) int {
    len1 := len(s1)
    len2 := len(s2)
    
    if len1 == 0 {
        return len2
    }
    if len2 == 0 {
        return len1
    }
    
    // DP matrix
    dp := make([][]int, len1+1)
    for i := range dp {
        dp[i] = make([]int, len2+1)
    }
    
    // Initialize
    for i := 0; i <= len1; i++ {
        dp[i][0] = i
    }
    for j := 0; j <= len2; j++ {
        dp[0][j] = j
    }
    
    // Fill matrix
    for i := 1; i <= len1; i++ {
        for j := 1; j <= len2; j++ {
            cost := 0
            if s1[i-1] != s2[j-1] {
                cost = 1
            }
            
            dp[i][j] = min(
                dp[i-1][j]+1,      // deletion
                dp[i][j-1]+1,      // insertion
                dp[i-1][j-1]+cost, // substitution
            )
        }
    }
    
    return dp[len1][len2]
}

func min(a, b, c int) int {
    if a < b {
        if a < c {
            return a
        }
        return c
    }
    if b < c {
        return b
    }
    return c
}
```

---

### 7.3 Faceted Search

```go
// query/faceted_search.go
package query

type Facet struct {
    Field  string
    Values map[string]int  // value → count
}

type FacetedSearchResult struct {
    Results []*SearchResult
    Facets  []*Facet
}

// FacetedSearch: Search with facets
func (idx *InvertedIndex) FacetedSearch(query string, facetFields []string, limit int) (*FacetedSearchResult, error) {
    // Execute search
    results, err := idx.Search(query, 10000)  // Get more for facet calculation
    if err != nil {
        return nil, err
    }
    
    // Calculate facets
    facets := make([]*Facet, len(facetFields))
    for i, field := range facetFields {
        facets[i] = &Facet{
            Field:  field,
            Values: make(map[string]int),
        }
        
        for _, result := range results {
            value := result.Doc.Fields[field]
            if value != "" {
                facets[i].Values[value]++
            }
        }
    }
    
    // Limit results
    if len(results) > limit {
        results = results[:limit]
    }
    
    return &FacetedSearchResult{
        Results: results,
        Facets:  facets,
    }, nil
}

// Example usage:
// Query: "laptop"
// Facets: ["brand", "price_range", "rating"]
//
// Results:
// - Brand: Apple (152), Dell (98), HP (76)
// - Price Range: $500-$1000 (203), $1000-$1500 (89), $1500+ (34)
// - Rating: 5 stars (56), 4 stars (148), 3 stars (87)
```

---

### 7.4 Boolean Queries

```go
// query/boolean_query.go
package query

type BooleanQuery struct {
    Must    []string  // AND (all must match)
    Should  []string  // OR (at least one should match)
    MustNot []string  // NOT (none should match)
}

func (idx *InvertedIndex) BooleanSearch(bq *BooleanQuery, limit int) ([]*SearchResult, error) {
    // Get candidates from MUST clauses
    var candidates map[string]bool
    
    if len(bq.Must) > 0 {
        mustLists := make([]*PostingList, 0)
        for _, term := range bq.Must {
            analyzed := idx.analyze(term)
            for _, t := range analyzed {
                if pl, exists := idx.index[t]; exists {
                    mustLists = append(mustLists, pl)
                }
            }
        }
        candidates = idx.mergePostingLists(mustLists)
    } else {
        // If no MUST, start with all docs
        candidates = make(map[string]bool)
        for docID := range idx.docStore {
            candidates[docID] = true
        }
    }
    
    // Filter by SHOULD clauses (OR)
    if len(bq.Should) > 0 {
        shouldDocs := make(map[string]bool)
        for _, term := range bq.Should {
            analyzed := idx.analyze(term)
            for _, t := range analyzed {
                if pl, exists := idx.index[t]; exists {
                    for _, posting := range pl.postings {
                        shouldDocs[posting.docID] = true
                    }
                }
            }
        }
        
        // Intersect with candidates
        for docID := range candidates {
            if !shouldDocs[docID] {
                delete(candidates, docID)
            }
        }
    }
    
    // Exclude MUST_NOT clauses
    for _, term := range bq.MustNot {
        analyzed := idx.analyze(term)
        for _, t := range analyzed {
            if pl, exists := idx.index[t]; exists {
                for _, posting := range pl.postings {
                    delete(candidates, posting.docID)
                }
            }
        }
    }
    
    // Score remaining candidates
    allTerms := append(bq.Must, bq.Should...)
    results := make([]*SearchResult, 0, len(candidates))
    
    for docID := range candidates {
        score := idx.score(docID, idx.analyze(strings.Join(allTerms, " ")))
        results = append(results, &SearchResult{
            DocID: docID,
            Score: score,
            Doc:   idx.docStore[docID],
        })
    }
    
    // Sort and limit
    sort.Slice(results, func(i, j int) bool {
        return results[i].Score > results[j].Score
    })
    
    if len(results) > limit {
        results = results[:limit]
    }
    
    return results, nil
}

// Example:
// Must: ["laptop"]
// Should: ["gaming", "programming"]
// MustNot: ["refurbished"]
//
// Finds: laptops for gaming OR programming, excluding refurbished
```

---

## 8. Distributed Search

### 8.1 Sharding

```go
// distributed/sharded_index.go
package distributed

type ShardedIndex struct {
    shards    []*Shard
    numShards int
}

type Shard struct {
    id    int
    index *InvertedIndex
}

func NewShardedIndex(numShards int) *ShardedIndex {
    shards := make([]*Shard, numShards)
    for i := 0; i < numShards; i++ {
        shards[i] = &Shard{
            id:    i,
            index: NewInvertedIndex(),
        }
    }
    
    return &ShardedIndex{
        shards:    shards,
        numShards: numShards,
    }
}

// AddDocument: Route to appropriate shard
func (si *ShardedIndex) AddDocument(doc *Document) error {
    shardID := si.getShardID(doc.ID)
    return si.shards[shardID].index.AddDocument(doc)
}

func (si *ShardedIndex) getShardID(docID string) int {
    h := fnv.New32a()
    h.Write([]byte(docID))
    return int(h.Sum32()) % si.numShards
}

// Search: Query all shards in parallel, merge results
func (si *ShardedIndex) Search(query string, limit int) ([]*SearchResult, error) {
    var wg sync.WaitGroup
    resultsChan := make(chan []*SearchResult, si.numShards)
    
    // Query all shards in parallel
    for _, shard := range si.shards {
        wg.Add(1)
        go func(s *Shard) {
            defer wg.Done()
            
            results, err := s.index.Search(query, limit)
            if err != nil {
                log.Printf("Shard %d error: %v", s.id, err)
                return
            }
            
            resultsChan <- results
        }(shard)
    }
    
    wg.Wait()
    close(resultsChan)
    
    // Merge results from all shards
    allResults := make([]*SearchResult, 0)
    for results := range resultsChan {
        allResults = append(allResults, results...)
    }
    
    // Sort by score
    sort.Slice(allResults, func(i, j int) bool {
        return allResults[i].Score > allResults[j].Score
    })
    
    // Return top N
    if len(allResults) > limit {
        allResults = allResults[:limit]
    }
    
    return allResults, nil
}
```

---

### 8.2 Replication

```go
// distributed/replicated_shard.go
package distributed

type ReplicatedShard struct {
    primary   *Shard
    replicas  []*Shard
    replFactor int
}

func (rs *ReplicatedShard) AddDocument(doc *Document) error {
    // Write to primary
    if err := rs.primary.index.AddDocument(doc); err != nil {
        return err
    }
    
    // Replicate to replicas (async)
    for _, replica := range rs.replicas {
        go func(r *Shard) {
            r.index.AddDocument(doc)
        }(replica)
    }
    
    return nil
}

func (rs *ReplicatedShard) Search(query string, limit int) ([]*SearchResult, error) {
    // Try primary first
    results, err := rs.primary.index.Search(query, limit)
    if err == nil {
        return results, nil
    }
    
    // Fallback to replicas
    log.Printf("Primary failed, trying replicas")
    for _, replica := range rs.replicas {
        results, err = replica.index.Search(query, limit)
        if err == nil {
            return results, nil
        }
    }
    
    return nil, fmt.Errorf("all shards failed")
}
```

---

## 9. Performance Optimizations

### 9.1 Caching

```go
// cache/query_cache.go
package cache

import (
    "container/list"
    "sync"
)

type QueryCache struct {
    capacity int
    cache    map[string]*list.Element
    lru      *list.List
    mu       sync.RWMutex
}

type cacheEntry struct {
    query   string
    results []*SearchResult
}

func NewQueryCache(capacity int) *QueryCache {
    return &QueryCache{
        capacity: capacity,
        cache:    make(map[string]*list.Element),
        lru:      list.New(),
    }
}

func (qc *QueryCache) Get(query string) ([]*SearchResult, bool) {
    qc.mu.Lock()
    defer qc.mu.Unlock()
    
    if elem, ok := qc.cache[query]; ok {
        qc.lru.MoveToFront(elem)
        return elem.Value.(*cacheEntry).results, true
    }
    
    return nil, false
}

func (qc *QueryCache) Put(query string, results []*SearchResult) {
    qc.mu.Lock()
    defer qc.mu.Unlock()
    
    if elem, ok := qc.cache[query]; ok {
        qc.lru.MoveToFront(elem)
        elem.Value.(*cacheEntry).results = results
        return
    }
    
    entry := &cacheEntry{query: query, results: results}
    elem := qc.lru.PushFront(entry)
    qc.cache[query] = elem
    
    if qc.lru.Len() > qc.capacity {
        oldest := qc.lru.Back()
        if oldest != nil {
            qc.lru.Remove(oldest)
            delete(qc.cache, oldest.Value.(*cacheEntry).query)
        }
    }
}
```

---

### 9.2 Skip Pointers (Fast Intersection)

```go
// index/skip_list.go
package index

type SkipPointer struct {
    position int
    docID    string
}

type PostingListWithSkips struct {
    postings    []*Posting
    skipPointers []*SkipPointer
    skipInterval int
}

func NewPostingListWithSkips(postings []*Posting) *PostingListWithSkips {
    skipInterval := int(math.Sqrt(float64(len(postings))))
    skipPointers := make([]*SkipPointer, 0)
    
    for i := skipInterval; i < len(postings); i += skipInterval {
        skipPointers = append(skipPointers, &SkipPointer{
            position: i,
            docID:    postings[i].docID,
        })
    }
    
    return &PostingListWithSkips{
        postings:     postings,
        skipPointers: skipPointers,
        skipInterval: skipInterval,
    }
}

// IntersectWithSkips: Fast intersection using skip pointers
func IntersectWithSkips(list1, list2 *PostingListWithSkips) []*Posting {
    result := make([]*Posting, 0)
    i, j := 0, 0
    
    for i < len(list1.postings) && j < len(list2.postings) {
        doc1 := list1.postings[i].docID
        doc2 := list2.postings[j].docID
        
        if doc1 == doc2 {
            result = append(result, list1.postings[i])
            i++
            j++
        } else if doc1 < doc2 {
            // Try to skip ahead in list1
            skip := list1.findNextSkip(i, doc2)
            if skip != -1 && list1.postings[skip].docID <= doc2 {
                i = skip
            } else {
                i++
            }
        } else {
            // Try to skip ahead in list2
            skip := list2.findNextSkip(j, doc1)
            if skip != -1 && list2.postings[skip].docID <= doc1 {
                j = skip
            } else {
                j++
            }
        }
    }
    
    return result
}

func (pl *PostingListWithSkips) findNextSkip(currentPos int, targetDocID string) int {
    for _, skip := range pl.skipPointers {
        if skip.position > currentPos && skip.docID <= targetDocID {
            return skip.position
        }
    }
    return -1
}
```

**Performance Gain:** O(√n) skip vs O(n) linear scan

---

**Continued in next part...**
