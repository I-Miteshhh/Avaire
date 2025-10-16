# Design Elasticsearch-Based Search Engine - Complete System Design

**Difficulty:** ⭐⭐⭐⭐  
**Interview Frequency:** Very High (Elastic, Google, Airbnb, Amazon, 40 LPA+)  
**Time to Complete:** 40-45 minutes  
**Real-World Examples:** Airbnb Search, Amazon Product Search, Google Search, GitHub Code Search

---

## 📋 Problem Statement

**Design a full-text search engine that can:**
- Index 100 billion documents
- Support 100K search queries per second
- Return results in <100ms (p99 latency)
- Handle typos and misspellings (fuzzy matching)
- Support advanced queries (filters, facets, aggregations, geo-search)
- Rank results by relevance (BM25, ML ranking)
- Support autocomplete and suggestions
- Handle real-time indexing (new documents appear instantly)
- Scale horizontally across datacenters
- Provide search analytics and insights

**Business Goals:**
- High search quality (relevant results)
- Fast response time (<100ms)
- High availability (99.99% uptime)
- Support personalization

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                  SEARCH REQUEST FLOW                          │
├──────────────────────────────────────────────────────────────┤
│  GET /search?q=machine+learning&filters=category:books       │
│  Response: <100ms                                             │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│              ELASTICSEARCH CLUSTER (50 nodes)                 │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Sharding: 100 shards × 3 replicas = 300 shard copies        │
│  Each shard: 1B documents / 100 = 10M docs                   │
│                                                               │
│  Index Structure:                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Inverted Index                                        │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │  Term        → Document IDs + Positions                │ │
│  │  ──────────────────────────────────────────────────    │ │
│  │  "machine"   → [doc1:pos[0,15], doc5:pos[3], ...]     │ │
│  │  "learning"  → [doc1:pos[1,16], doc3:pos[8], ...]     │ │
│  │  "python"    → [doc2:pos[0], doc7:pos[12], ...]       │ │
│  │                                                        │ │
│  │  Enables:                                              │ │
│  │  - Fast term lookups (O(1) hash lookup)               │ │
│  │  - Phrase queries ("machine learning")                │ │
│  │  - Proximity queries (terms within N words)            │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  Scoring Algorithm: BM25 (Best Match 25)                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  score(d,q) = Σ IDF(qi) × TF(qi,d) × boost           │ │
│  │                                                        │ │
│  │  IDF (Inverse Document Frequency):                    │ │
│  │  - Rare terms → higher weight                         │ │
│  │  - log((N - df + 0.5) / (df + 0.5))                   │ │
│  │                                                        │ │
│  │  TF (Term Frequency):                                 │ │
│  │  - Frequency in document (with saturation)            │ │
│  │  - (k1 + 1) × tf / (k1 × (1 - b + b × dl/avgdl) + tf)│ │
│  │                                                        │ │
│  │  Field Boosts:                                        │ │
│  │  - title: 3x                                           │ │
│  │  - description: 1x                                     │ │
│  │  - content: 0.5x                                       │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                  QUERY PROCESSING PIPELINE                    │
├──────────────────────────────────────────────────────────────┤
│  1. Query Parsing                                            │
│     "machine learning python" →                               │
│     [term: machine, term: learning, term: python]            │
│                                                               │
│  2. Query Expansion                                          │
│     - Synonyms: machine → computer, device                   │
│     - Stemming: learning → learn                             │
│     - Spell correction: pythn → python                       │
│                                                               │
│  3. Distributed Search                                       │
│     - Scatter: Query all 100 shards in parallel              │
│     - Gather: Merge top-K results from each shard            │
│     - Coordination node aggregates                           │
│                                                               │
│  4. Ranking & Reranking                                      │
│     - Phase 1: BM25 scoring (Elasticsearch)                  │
│     - Phase 2: ML reranking (top 100 results)                │
│     - Phase 3: Personalization (user history)                │
│                                                               │
│  5. Result Formatting                                        │
│     - Highlighting (bold matched terms)                      │
│     - Snippets (preview with context)                        │
│     - Facets (category counts)                               │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                   INDEXING PIPELINE                           │
├──────────────────────────────────────────────────────────────┤
│  Document → Kafka → Logstash → Elasticsearch                 │
│                                                               │
│  Logstash Pipeline:                                          │
│  1. Parse document (JSON, XML, PDF, etc.)                    │
│  2. Extract text content                                     │
│  3. Enrich metadata                                          │
│  4. Analyze text:                                            │
│     - Tokenization (split into words)                        │
│     - Lowercasing                                            │
│     - Stop word removal (the, a, an)                         │
│     - Stemming (running → run)                               │
│     - N-gram generation (for autocomplete)                   │
│  5. Index in Elasticsearch                                   │
│                                                               │
│  Real-time: <1 second from publish to searchable             │
└──────────────────────────────────────────────────────────────┘
```

---

## 💻 Implementation

### **1. Elasticsearch Index Configuration**

```json
{
  "settings": {
    "number_of_shards": 100,
    "number_of_replicas": 2,
    "refresh_interval": "1s",
    "analysis": {
      "analyzer": {
        "english_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "english_stop",
            "english_stemmer",
            "asciifolding"
          ]
        },
        "autocomplete_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "edge_ngram_filter"
          ]
        }
      },
      "filter": {
        "english_stop": {
          "type": "stop",
          "stopwords": "_english_"
        },
        "english_stemmer": {
          "type": "stemmer",
          "language": "english"
        },
        "edge_ngram_filter": {
          "type": "edge_ngram",
          "min_gram": 2,
          "max_gram": 10
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "english_analyzer",
        "fields": {
          "autocomplete": {
            "type": "text",
            "analyzer": "autocomplete_analyzer",
            "search_analyzer": "standard"
          },
          "keyword": {
            "type": "keyword"
          }
        },
        "boost": 3.0
      },
      "description": {
        "type": "text",
        "analyzer": "english_analyzer"
      },
      "content": {
        "type": "text",
        "analyzer": "english_analyzer",
        "index_options": "positions"
      },
      "category": {
        "type": "keyword"
      },
      "tags": {
        "type": "keyword"
      },
      "author": {
        "type": "keyword"
      },
      "created_at": {
        "type": "date"
      },
      "price": {
        "type": "float"
      },
      "rating": {
        "type": "float"
      },
      "popularity_score": {
        "type": "float"
      },
      "location": {
        "type": "geo_point"
      }
    }
  }
}
```

### **2. Advanced Search Query**

```python
from elasticsearch import Elasticsearch
from typing import List, Dict, Optional

class SearchEngine:
    """
    Production search engine with Elasticsearch
    """
    
    def __init__(self, es_hosts: List[str]):
        self.es = Elasticsearch(
            es_hosts,
            max_retries=3,
            retry_on_timeout=True,
            request_timeout=30
        )
        
        self.index_name = "documents"
    
    def search(self, query: str, filters: Dict = None, 
              page: int = 0, size: int = 20,
              sort_by: str = "relevance") -> Dict:
        """
        Advanced search with filters, facets, and highlighting
        """
        
        # Build Elasticsearch query
        es_query = {
            "query": {
                "function_score": {
                    "query": self._build_text_query(query, filters),
                    "functions": self._build_scoring_functions(),
                    "score_mode": "sum",
                    "boost_mode": "multiply"
                }
            },
            "highlight": {
                "fields": {
                    "title": {},
                    "description": {},
                    "content": {
                        "fragment_size": 150,
                        "number_of_fragments": 3
                    }
                },
                "pre_tags": ["<b>"],
                "post_tags": ["</b>"]
            },
            "aggs": {
                "categories": {
                    "terms": {"field": "category", "size": 10}
                },
                "price_ranges": {
                    "range": {
                        "field": "price",
                        "ranges": [
                            {"to": 10},
                            {"from": 10, "to": 50},
                            {"from": 50, "to": 100},
                            {"from": 100}
                        ]
                    }
                },
                "avg_rating": {
                    "avg": {"field": "rating"}
                }
            },
            "from": page * size,
            "size": size,
            "_source": ["title", "description", "price", "rating", "category"]
        }
        
        # Add sorting
        if sort_by == "price_asc":
            es_query["sort"] = [{"price": "asc"}]
        elif sort_by == "price_desc":
            es_query["sort"] = [{"price": "desc"}]
        elif sort_by == "rating":
            es_query["sort"] = [{"rating": "desc"}]
        elif sort_by == "date":
            es_query["sort"] = [{"created_at": "desc"}]
        # Default: relevance (no explicit sort)
        
        # Execute search
        response = self.es.search(
            index=self.index_name,
            body=es_query
        )
        
        # Parse results
        results = {
            "total": response["hits"]["total"]["value"],
            "took_ms": response["took"],
            "results": [],
            "facets": {
                "categories": [
                    {"name": bucket["key"], "count": bucket["doc_count"]}
                    for bucket in response["aggregations"]["categories"]["buckets"]
                ],
                "price_ranges": [
                    {"range": f"{bucket.get('from', 0)}-{bucket.get('to', '∞')}", "count": bucket["doc_count"]}
                    for bucket in response["aggregations"]["price_ranges"]["buckets"]
                ],
                "avg_rating": response["aggregations"]["avg_rating"]["value"]
            }
        }
        
        # Format results
        for hit in response["hits"]["hits"]:
            result = {
                "id": hit["_id"],
                "score": hit["_score"],
                "data": hit["_source"]
            }
            
            # Add highlights
            if "highlight" in hit:
                result["highlights"] = hit["highlight"]
            
            results["results"].append(result)
        
        return results
    
    def _build_text_query(self, query: str, filters: Dict = None):
        """
        Build multi-field text query with filters
        """
        
        # Multi-match query across multiple fields
        text_query = {
            "multi_match": {
                "query": query,
                "fields": [
                    "title^3",        # 3x boost
                    "description^1",  # 1x boost
                    "content^0.5"     # 0.5x boost
                ],
                "type": "best_fields",
                "fuzziness": "AUTO",  # Handle typos
                "operator": "or",
                "minimum_should_match": "75%"
            }
        }
        
        # Add filters
        if filters:
            filter_clauses = []
            
            if "category" in filters:
                filter_clauses.append({
                    "term": {"category": filters["category"]}
                })
            
            if "price_min" in filters or "price_max" in filters:
                price_range = {}
                if "price_min" in filters:
                    price_range["gte"] = filters["price_min"]
                if "price_max" in filters:
                    price_range["lte"] = filters["price_max"]
                
                filter_clauses.append({
                    "range": {"price": price_range}
                })
            
            if "tags" in filters:
                filter_clauses.append({
                    "terms": {"tags": filters["tags"]}
                })
            
            # Geo-search
            if "location" in filters and "radius" in filters:
                filter_clauses.append({
                    "geo_distance": {
                        "distance": filters["radius"],
                        "location": {
                            "lat": filters["location"]["lat"],
                            "lon": filters["location"]["lon"]
                        }
                    }
                })
            
            # Combine with bool query
            if filter_clauses:
                return {
                    "bool": {
                        "must": [text_query],
                        "filter": filter_clauses
                    }
                }
        
        return text_query
    
    def _build_scoring_functions(self) -> List[Dict]:
        """
        Custom scoring functions to boost relevance
        """
        
        return [
            # Boost recent documents
            {
                "exp": {
                    "created_at": {
                        "origin": "now",
                        "scale": "30d",
                        "decay": 0.5
                    }
                },
                "weight": 2.0
            },
            # Boost popular documents
            {
                "field_value_factor": {
                    "field": "popularity_score",
                    "modifier": "log1p",
                    "missing": 1
                },
                "weight": 1.5
            },
            # Boost high-rated documents
            {
                "field_value_factor": {
                    "field": "rating",
                    "modifier": "sqrt",
                    "missing": 3.0
                },
                "weight": 1.2
            }
        ]
    
    def autocomplete(self, prefix: str, size: int = 10) -> List[str]:
        """
        Autocomplete suggestions
        """
        
        query = {
            "query": {
                "match": {
                    "title.autocomplete": {
                        "query": prefix,
                        "operator": "and"
                    }
                }
            },
            "size": size,
            "_source": ["title"]
        }
        
        response = self.es.search(
            index=self.index_name,
            body=query
        )
        
        suggestions = [hit["_source"]["title"] for hit in response["hits"]["hits"]]
        
        return suggestions
    
    def suggest_corrections(self, query: str) -> List[str]:
        """
        Spelling suggestions using phrase suggester
        """
        
        suggest_query = {
            "suggest": {
                "text": query,
                "phrase_suggestion": {
                    "phrase": {
                        "field": "title",
                        "size": 3,
                        "gram_size": 2,
                        "confidence": 0.5,
                        "max_errors": 2,
                        "collate": {
                            "query": {
                                "source": {
                                    "match": {"{{field_name}}": "{{suggestion}}"}
                                }
                            },
                            "params": {"field_name": "title"},
                            "prune": True
                        }
                    }
                }
            }
        }
        
        response = self.es.search(
            index=self.index_name,
            body=suggest_query
        )
        
        corrections = []
        for option in response["suggest"]["phrase_suggestion"][0]["options"]:
            corrections.append(option["text"])
        
        return corrections


### **3. ML Reranking (Learning to Rank)**

```python
import lightgbm as lgb
import numpy as np

class MLReranker:
    """
    Machine learning reranking for search results
    """
    
    def __init__(self, model_path: str = None):
        if model_path:
            self.model = lgb.Booster(model_file=model_path)
        else:
            self.model = None
    
    def train(self, training_data, labels):
        """
        Train LambdaMART model (Learning to Rank)
        """
        
        # Group data by query
        train_data = lgb.Dataset(
            training_data,
            label=labels,
            group=self._get_query_groups(training_data)
        )
        
        params = {
            'objective': 'lambdarank',
            'metric': 'ndcg',
            'ndcg_eval_at': [1, 3, 5, 10],
            'learning_rate': 0.05,
            'num_leaves': 31,
            'max_depth': -1
        }
        
        self.model = lgb.train(
            params,
            train_data,
            num_boost_round=100
        )
    
    def rerank(self, search_results, user_context):
        """
        Rerank top K results using ML model
        """
        
        # Extract features for each result
        features = []
        for result in search_results:
            feat = self._extract_features(result, user_context)
            features.append(feat)
        
        # Predict scores
        scores = self.model.predict(np.array(features))
        
        # Rerank
        ranked = sorted(
            zip(search_results, scores),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [r[0] for r in ranked]
    
    def _extract_features(self, result, user_context):
        """Extract 100+ features for ML ranking"""
        
        features = []
        
        # BM25 score from Elasticsearch
        features.append(result['score'])
        
        # Document features
        features.append(result['data'].get('rating', 3.0))
        features.append(result['data'].get('popularity_score', 0.0))
        features.append(len(result['data'].get('description', '')))
        
        # User-document affinity
        features.append(self._user_category_affinity(user_context, result))
        features.append(self._user_price_affinity(user_context, result))
        
        # Query-document features
        features.append(len(result.get('highlights', {})))
        
        return features
```

---

## 🎓 Interview Points

**Capacity:**
```
Documents: 100B
Shards: 100 (1B docs each)
Replicas: 2x
Storage: 100B × 1KB = 100 TB × 3 = 300 TB
QPS: 100K/sec
```

**Key optimizations:** Inverted index, BM25, sharding, caching, ML reranking!
