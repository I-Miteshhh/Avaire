# Design Netflix-Style Recommendation System - Complete System Design

**Difficulty:** ⭐⭐⭐⭐⭐  
**Interview Frequency:** Very High (Netflix, YouTube, Spotify, Amazon, 40 LPA+)  
**Time to Complete:** 45-60 minutes  
**Real-World Examples:** Netflix Recommendations, YouTube Suggestions, Amazon Product Recommendations

---

## 📋 Problem Statement

**Design a personalized recommendation system that can:**
- Recommend relevant content to 200M users in real-time
- Support multiple recommendation types (collaborative filtering, content-based, hybrid)
- Personalize for individual user preferences
- Handle cold start (new users, new content)
- Support A/B testing for recommendation algorithms
- Process 1B user interactions daily (views, clicks, ratings)
- Generate recommendations in <100ms
- Support multiple surfaces (homepage, search, post-play)
- Explain recommendations ("Because you watched X")
- Optimize for engagement (watch time, completion rate)

**Business Goals:**
- Maximize user engagement (session duration)
- Reduce churn through relevant content
- Improve content discovery
- Increase watch time per session

---

## 🏗️ High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                RECOMMENDATION PIPELINE                        │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  ONLINE SERVING (Real-Time) - <100ms                  │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  GET /v1/recommendations?user_id=u123&context=home    │ │
│  │                                                        │ │
│  │  1. Candidate Generation (10,000 candidates)          │ │
│  │     ├─ Collaborative Filtering (matrix factorization) │ │
│  │     ├─ Content-Based (genre, actors, director)        │ │
│  │     ├─ Popular/Trending                               │ │
│  │     └─ Personalized categories                        │ │
│  │                                                        │ │
│  │  2. Candidate Filtering                               │ │
│  │     ├─ Already watched (deduplicate)                  │ │
│  │     ├─ User preferences (disliked genres)             │ │
│  │     ├─ Content restrictions (age rating, region)      │ │
│  │     └─ Diversity (mix genres)                         │ │
│  │                                                        │ │
│  │  3. Ranking (ML model - 500 candidates)               │ │
│  │     ├─ Feature extraction (200+ features)             │ │
│  │     ├─ Two-tower neural network                       │ │
│  │     └─ Score = P(user will watch > 70% of content)    │ │
│  │                                                        │ │
│  │  4. Reranking & Diversification (Top 50)              │ │
│  │     ├─ Business rules (promote new releases)          │ │
│  │     ├─ Diversity (avoid genre clustering)             │ │
│  │     └─ Freshness (mix old favorites + new content)    │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  OFFLINE BATCH (Daily Model Training)                 │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  1. Feature Engineering (Spark)                       │ │
│  │     - User features: watch history, ratings, genres   │ │
│  │     - Content features: metadata, embeddings          │ │
│  │     - Context features: time, device, location        │ │
│  │                                                        │ │
│  │  2. Collaborative Filtering (ALS)                     │ │
│  │     - Matrix Factorization                            │ │
│  │     - User embeddings (128-dim)                       │ │
│  │     - Item embeddings (128-dim)                       │ │
│  │                                                        │ │
│  │  3. Content Embeddings (Word2Vec/BERT)                │ │
│  │     - Title, description, tags → vector               │ │
│  │     - Similar content = nearby vectors                │ │
│  │                                                        │ │
│  │  4. Ranking Model Training (TensorFlow)               │ │
│  │     - Two-tower neural network                        │ │
│  │     - Optimize for watch time                         │ │
│  │     - Export to serving layer                         │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                 DATA COLLECTION PIPELINE                      │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  User Events → Kafka → Flink → Feature Store                 │
│  (clicks, plays, ratings, searches)                           │
│                                                               │
│  Real-time aggregations:                                     │
│  - User watch count last 7 days                              │
│  - Content popularity (trending)                             │
│  - Session context (binge-watching?)                         │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                     STORAGE LAYER                             │
├──────────────────────────────────────────────────────────────┤
│  Redis: User/item embeddings, trending content               │
│  PostgreSQL: User profiles, content metadata                 │
│  S3: Training datasets, model artifacts                      │
│  Cassandra: User watch history (time-series)                 │
└──────────────────────────────────────────────────────────────┘
```

---

## 💻 Core Implementation

### **1. Collaborative Filtering (Matrix Factorization)**

```python
from pyspark.ml.recommendation import ALS
from pyspark.sql import SparkSession
import numpy as np

class CollaborativeFilter:
    """
    Collaborative filtering using Alternating Least Squares (ALS)
    Learns user and item latent factors
    """
    
    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.model = None
        
        # Hyperparameters
        self.rank = 128  # Embedding dimension
        self.max_iter = 10
        self.reg_param = 0.1
    
    def train(self, interactions_df):
        """
        Train ALS model on user-item interactions
        
        Input DataFrame:
        +-------+--------+--------+
        |user_id|item_id | rating |
        +-------+--------+--------+
        | u123  | m456   |  4.5   |
        +-------+--------+--------+
        """
        
        # Build ALS model
        als = ALS(
            rank=self.rank,
            maxIter=self.max_iter,
            regParam=self.reg_param,
            userCol="user_id",
            itemCol="item_id",
            ratingCol="rating",
            coldStartStrategy="drop",  # Drop rows with unknown users/items
            implicitPrefs=False  # Explicit ratings (1-5 stars)
        )
        
        # Train
        self.model = als.fit(interactions_df)
        
        # Extract embeddings
        user_factors = self.model.userFactors  # DataFrame: id, features (128-dim vector)
        item_factors = self.model.itemFactors  # DataFrame: id, features (128-dim vector)
        
        return user_factors, item_factors
    
    def recommend_for_user(self, user_id: str, n: int = 100):
        """
        Generate top-N recommendations for user
        """
        
        from pyspark.sql.functions import col
        
        # Create DataFrame with single user
        user_df = self.spark.createDataFrame([(user_id,)], ["user_id"])
        
        # Get recommendations
        recs = self.model.recommendForUserSubset(user_df, n)
        
        # Extract item IDs and scores
        recommendations = []
        for row in recs.collect():
            uid = row['user_id']
            for rec in row['recommendations']:
                recommendations.append({
                    'item_id': rec['item_id'],
                    'score': float(rec['rating'])
                })
        
        return recommendations


### **2. Content-Based Filtering**

```python
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List

class ContentBasedFilter:
    """
    Content-based recommendations using embeddings
    Similar content = nearby in embedding space
    """
    
    def __init__(self):
        # Pre-trained model for text embeddings
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # FAISS index for fast nearest neighbor search
        self.dimension = 384  # Embedding size
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product (cosine similarity)
        
        # Mapping: index → item_id
        self.index_to_item = {}
    
    def build_index(self, content_catalog):
        """
        Build search index from content metadata
        
        content_catalog = [
            {
                'item_id': 'm123',
                'title': 'The Matrix',
                'description': 'A computer hacker learns...',
                'genres': ['Sci-Fi', 'Action'],
                'actors': ['Keanu Reeves', 'Laurence Fishburne'],
                'director': 'Wachowski Brothers'
            },
            ...
        ]
        """
        
        embeddings = []
        
        for idx, item in enumerate(content_catalog):
            # Combine metadata into text
            text = f"{item['title']}. {item['description']}. Genres: {', '.join(item['genres'])}. "
            text += f"Starring: {', '.join(item['actors'])}. Director: {item['director']}"
            
            # Generate embedding
            embedding = self.encoder.encode(text, convert_to_tensor=False)
            embeddings.append(embedding)
            
            # Store mapping
            self.index_to_item[idx] = item['item_id']
        
        # Convert to numpy
        embeddings_np = np.array(embeddings).astype('float32')
        
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings_np)
        
        # Add to index
        self.index.add(embeddings_np)
        
        print(f"Built FAISS index with {len(embeddings)} items")
    
    def find_similar(self, item_id: str, k: int = 10) -> List[str]:
        """
        Find K most similar items to given item
        """
        
        # Get item index
        item_idx = None
        for idx, iid in self.index_to_item.items():
            if iid == item_id:
                item_idx = idx
                break
        
        if item_idx is None:
            return []
        
        # Get item embedding from index
        embedding = self.index.reconstruct(item_idx).reshape(1, -1)
        
        # Search
        distances, indices = self.index.search(embedding, k + 1)  # +1 to exclude self
        
        # Convert to item IDs
        similar_items = []
        for idx in indices[0]:
            if idx != item_idx:  # Exclude self
                similar_items.append(self.index_to_item[idx])
        
        return similar_items[:k]


### **3. Two-Tower Neural Network Ranker**

```python
import tensorflow as tf
from tensorflow import keras
from typing import Dict, List

class TwoTowerRanker:
    """
    Two-tower neural network for ranking
    Learns separate embeddings for users and items
    """
    
    def __init__(self, user_feature_dim: int, item_feature_dim: int):
        self.user_feature_dim = user_feature_dim
        self.item_feature_dim = item_feature_dim
        
        # Build model
        self.model = self._build_model()
    
    def _build_model(self):
        """
        Build two-tower architecture
        """
        
        # User tower
        user_input = keras.Input(shape=(self.user_feature_dim,), name='user_features')
        user_dense1 = keras.layers.Dense(256, activation='relu')(user_input)
        user_dropout1 = keras.layers.Dropout(0.3)(user_dense1)
        user_dense2 = keras.layers.Dense(128, activation='relu')(user_dropout1)
        user_embedding = keras.layers.Dense(64, activation='relu', name='user_embedding')(user_dense2)
        
        # Item tower
        item_input = keras.Input(shape=(self.item_feature_dim,), name='item_features')
        item_dense1 = keras.layers.Dense(256, activation='relu')(item_input)
        item_dropout1 = keras.layers.Dropout(0.3)(item_dense1)
        item_dense2 = keras.layers.Dense(128, activation='relu')(item_dropout1)
        item_embedding = keras.layers.Dense(64, activation='relu', name='item_embedding')(item_dense2)
        
        # Interaction: dot product
        interaction = keras.layers.Dot(axes=1, normalize=False)([user_embedding, item_embedding])
        
        # Output: probability of positive engagement
        output = keras.layers.Dense(1, activation='sigmoid', name='engagement_score')(interaction)
        
        # Build model
        model = keras.Model(
            inputs=[user_input, item_input],
            outputs=output
        )
        
        # Compile
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['AUC', 'precision', 'recall']
        )
        
        return model
    
    def train(self, train_data, validation_data, epochs: int = 10):
        """
        Train ranking model
        
        train_data = (
            {'user_features': user_feat_array, 'item_features': item_feat_array},
            labels  # 1 if user engaged (watched >70%), 0 otherwise
        )
        """
        
        history = self.model.fit(
            train_data[0],
            train_data[1],
            validation_data=validation_data,
            epochs=epochs,
            batch_size=512,
            callbacks=[
                keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True),
                keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=2)
            ]
        )
        
        return history
    
    def predict(self, user_features: np.ndarray, item_features: np.ndarray) -> np.ndarray:
        """
        Predict engagement scores
        """
        
        scores = self.model.predict({
            'user_features': user_features,
            'item_features': item_features
        }, batch_size=1024)
        
        return scores.flatten()


### **4. Hybrid Recommendation Service**

```python
from dataclasses import dataclass
from typing import List, Dict
import redis
import numpy as np

@dataclass
class Recommendation:
    item_id: str
    title: str
    score: float
    reason: str  # Explanation

class HybridRecommender:
    """
    Combines multiple recommendation strategies
    """
    
    def __init__(self, redis_client, cf_model, cb_model, ranker):
        self.redis = redis_client
        self.cf_model = cf_model  # Collaborative filtering
        self.cb_model = cb_model  # Content-based
        self.ranker = ranker  # Neural network ranker
    
    def get_recommendations(self, user_id: str, context: str = 'home', n: int = 50) -> List[Recommendation]:
        """
        Generate personalized recommendations
        """
        
        # Step 1: Candidate Generation (10,000 candidates)
        candidates = []
        
        # 1a. Collaborative filtering candidates
        cf_candidates = self.cf_model.recommend_for_user(user_id, n=5000)
        for c in cf_candidates:
            candidates.append({
                'item_id': c['item_id'],
                'score': c['score'],
                'source': 'collaborative'
            })
        
        # 1b. Content-based candidates (based on watch history)
        watch_history = self._get_watch_history(user_id, limit=10)
        for item_id in watch_history:
            similar = self.cb_model.find_similar(item_id, k=100)
            for sim_id in similar:
                candidates.append({
                    'item_id': sim_id,
                    'score': 1.0,
                    'source': 'content',
                    'because': item_id
                })
        
        # 1c. Trending/Popular
        trending = self._get_trending(n=1000)
        for item_id, pop_score in trending:
            candidates.append({
                'item_id': item_id,
                'score': pop_score,
                'source': 'trending'
            })
        
        # Step 2: Deduplication
        seen = set()
        unique_candidates = []
        for c in candidates:
            if c['item_id'] not in seen:
                seen.add(c['item_id'])
                unique_candidates.append(c)
        
        # Step 3: Filtering
        filtered = self._filter_candidates(user_id, unique_candidates)
        
        # Step 4: Ranking (use neural network)
        ranked = self._rank_candidates(user_id, filtered)
        
        # Step 5: Diversification & Reranking
        final = self._diversify(ranked, n=n)
        
        # Convert to Recommendation objects
        recommendations = []
        for item in final:
            metadata = self._get_item_metadata(item['item_id'])
            
            # Generate explanation
            reason = self._generate_explanation(item)
            
            recommendations.append(Recommendation(
                item_id=item['item_id'],
                title=metadata['title'],
                score=item['final_score'],
                reason=reason
            ))
        
        return recommendations
    
    def _filter_candidates(self, user_id: str, candidates: List[Dict]) -> List[Dict]:
        """
        Filter out invalid candidates
        """
        
        # Get already watched
        watched = set(self._get_watch_history(user_id, limit=10000))
        
        # Get user preferences
        disliked_genres = self._get_disliked_genres(user_id)
        
        filtered = []
        for c in candidates:
            # Skip already watched
            if c['item_id'] in watched:
                continue
            
            # Check genre preferences
            item_genres = self._get_item_genres(c['item_id'])
            if any(g in disliked_genres for g in item_genres):
                continue
            
            filtered.append(c)
        
        return filtered
    
    def _rank_candidates(self, user_id: str, candidates: List[Dict]) -> List[Dict]:
        """
        Rank candidates using ML model
        """
        
        # Extract features
        user_features = self._get_user_features(user_id)
        
        # Prepare batch
        item_features_batch = []
        for c in candidates:
            item_feat = self._get_item_features(c['item_id'])
            item_features_batch.append(item_feat)
        
        # Convert to numpy
        user_feat_repeated = np.repeat([user_features], len(candidates), axis=0)
        item_feat_array = np.array(item_features_batch)
        
        # Predict
        scores = self.ranker.predict(user_feat_repeated, item_feat_array)
        
        # Add scores
        for i, c in enumerate(candidates):
            c['ml_score'] = scores[i]
        
        # Sort by ML score
        ranked = sorted(candidates, key=lambda x: x['ml_score'], reverse=True)
        
        return ranked
    
    def _diversify(self, items: List[Dict], n: int) -> List[Dict]:
        """
        Ensure genre diversity in top N
        """
        
        final = []
        genre_counts = {}
        max_per_genre = n // 5  # Max 20% per genre
        
        for item in items:
            if len(final) >= n:
                break
            
            genres = self._get_item_genres(item['item_id'])
            
            # Check if adding this item exceeds genre quota
            can_add = True
            for g in genres:
                if genre_counts.get(g, 0) >= max_per_genre:
                    can_add = False
                    break
            
            if can_add:
                final.append(item)
                for g in genres:
                    genre_counts[g] = genre_counts.get(g, 0) + 1
                
                # Recalculate final score
                item['final_score'] = item['ml_score'] * 0.9 + item['score'] * 0.1
        
        return final
    
    def _generate_explanation(self, item: Dict) -> str:
        """Generate human-readable explanation"""
        
        if item['source'] == 'collaborative':
            return "Because you might like"
        elif item['source'] == 'content' and 'because' in item:
            similar_title = self._get_item_metadata(item['because'])['title']
            return f"Because you watched {similar_title}"
        elif item['source'] == 'trending':
            return "Trending now"
        else:
            return "Recommended for you"
```

---

## 🎓 Key Interview Points

### **Capacity Estimation:**
```
Users: 200M
Daily interactions: 1B = 11,500/sec
User embeddings: 200M × 128 × 4 bytes = 102 GB
Item embeddings: 100K items × 128 × 4 bytes = 51 MB

Serving latency: <100ms
- Candidate generation: 50ms
- Ranking: 30ms  
- Filtering: 20ms
```

### **Cold Start Problem:**
1. **New users** - Use popular/trending content
2. **New content** - Use content-based (metadata)
3. **Hybrid** - Combine collaborative + content

**Essential for ML/personalization interviews!** 🎬🎯
