# Design Social Media News Feed Ranking System - Complete System Design

**Difficulty:** ⭐⭐⭐⭐⭐  
**Interview Frequency:** Very High (Facebook, Twitter, LinkedIn, Instagram, 40 LPA+)  
**Time to Complete:** 45-60 minutes  
**Real-World Examples:** Facebook News Feed, Twitter Timeline, LinkedIn Feed, Instagram Feed

---

## 📋 Problem Statement

**Design a personalized news feed ranking system that can:**
- Serve 2 billion users with personalized feeds
- Rank 1,000+ potential posts per user in real-time (<200ms)
- Process 100 million new posts per day
- Handle 10 billion feed impressions daily
- Support multiple engagement types (like, comment, share, click)
- Optimize for user engagement and session time
- Prevent echo chambers (diversity of content)
- Filter spam, misinformation, and low-quality content
- Support real-time updates (new posts appear dynamically)
- A/B test ranking algorithms at scale

**Business Goals:**
- Maximize time spent on platform
- Increase user engagement (likes, comments, shares)
- Improve content quality and relevance
- Reduce churn through personalized experience
- Balance user interests with platform goals

---

## 🏗️ High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                  FEED GENERATION PIPELINE                     │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  GET /v1/feed?user_id=u123&offset=0&limit=20                │
│  Response time: <200ms                                        │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  STEP 1: CANDIDATE GENERATION (1000+ posts)           │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  Sources:                                              │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │ 1. Social Graph (Friends' Posts)                 │ │ │
│  │  │    - Recent posts from friends (last 7 days)     │ │ │
│  │  │    - Query: Cassandra (user_id → friend_posts)   │ │ │
│  │  │    - Result: ~500 posts                          │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  │                                                        │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │ 2. Interest Graph (Pages/Topics User Follows)    │ │ │
│  │  │    - Posts from followed pages                   │ │ │
│  │  │    - Query: Redis (user_interests → posts)       │ │ │
│  │  │    - Result: ~300 posts                          │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  │                                                        │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │ 3. Viral/Trending Posts                          │ │ │
│  │  │    - High engagement posts (global trending)     │ │ │
│  │  │    - Query: Redis sorted set (engagement_score)  │ │ │
│  │  │    - Result: ~200 posts                          │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  │                                                        │ │
│  │  Total: ~1000 candidate posts                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  STEP 2: FEATURE EXTRACTION (Parallel - 50ms)        │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  For each candidate post, extract 500+ features:     │ │
│  │                                                        │ │
│  │  Post Features:                                       │ │
│  │  - Post age (freshness)                               │ │
│  │  - Content type (text, image, video, link)            │ │
│  │  - Media quality score                                │ │
│  │  - Text length, sentiment                             │ │
│  │  - Topic/category (ML classification)                 │ │
│  │                                                        │ │
│  │  Engagement Features:                                 │ │
│  │  - Like count, comment count, share count            │ │
│  │  - Engagement velocity (likes per hour)               │ │
│  │  - Click-through rate (CTR)                           │ │
│  │  - Dwell time (avg time spent viewing)                │ │
│  │  - Negative feedback (hide, report)                   │ │
│  │                                                        │ │
│  │  Author Features:                                     │ │
│  │  - Author credibility score                           │ │
│  │  - Follower count                                     │ │
│  │  - Historical engagement rate                         │ │
│  │  - Account age, verification status                   │ │
│  │                                                        │ │
│  │  User-Post Affinity:                                  │ │
│  │  - User's past engagement with author                 │ │
│  │  - User's interest in post topic                      │ │
│  │  - Social distance (friend, friend-of-friend)         │ │
│  │  - Similar posts user engaged with                    │ │
│  │                                                        │ │
│  │  Contextual Features:                                 │ │
│  │  - Time of day, day of week                           │ │
│  │  - Device type (mobile, desktop)                      │ │
│  │  - Location (country, city)                           │ │
│  │  - Session context (scroll depth, time on platform)   │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  STEP 3: RANKING (ML Model - 100ms)                  │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  Ranking Model: Gradient Boosted Trees (LightGBM)     │ │
│  │                                                        │ │
│  │  Objective: Predict P(user will engage with post)     │ │
│  │                                                        │ │
│  │  Engagement defined as:                               │ │
│  │  - Like: +1 point                                     │ │
│  │  - Comment: +3 points                                 │ │
│  │  - Share: +5 points                                   │ │
│  │  - Click: +2 points                                   │ │
│  │  - Dwell time >30s: +2 points                         │ │
│  │  - Hide/Report: -10 points                            │ │
│  │                                                        │ │
│  │  Model Training:                                      │ │
│  │  - Train on last 7 days of data                       │ │
│  │  - 1 billion training samples daily                   │ │
│  │  - Features: 500+ dimensions                          │ │
│  │  - Retrain every 6 hours                              │ │
│  │  - A/B test new models (shadow mode)                  │ │
│  │                                                        │ │
│  │  Output: Engagement score (0-1) per post              │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  STEP 4: RERANKING & DIVERSIFICATION (20ms)          │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  Business Rules:                                      │ │
│  │  1. Freshness boost: Newer posts get +10% score      │ │
│  │  2. Diversity: Max 2 posts from same author in top20 │ │
│  │  3. Topic diversity: Mix topics (news, sports, tech) │ │
│  │  4. Media mix: Balance text, image, video posts      │ │
│  │  5. Sponsored content: Insert ads at positions 3,7,12│ │
│  │  6. Demote clickbait: Penalize low dwell time posts  │ │
│  │  7. Friend posts: Boost posts from close friends     │ │
│  │                                                        │ │
│  │  Quality Filters:                                     │ │
│  │  - Remove spam (ML spam classifier)                   │ │
│  │  - Filter misinformation (fact-check score)           │ │
│  │  - Block NSFW content (image classifier)              │ │
│  │  - Remove duplicate/similar posts (MinHash)           │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  STEP 5: PAGINATION & CACHING (10ms)                 │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  - Cache top 100 ranked posts in Redis               │ │
│  │  - TTL: 5 minutes (to incorporate new posts)          │ │
│  │  - Return requested page (e.g., posts 0-19)           │ │
│  │  - Track impressions (for future ranking)             │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│              REAL-TIME ENGAGEMENT TRACKING                    │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  User Actions → Kafka → Flink → Redis/Cassandra              │
│                                                               │
│  Flink Streaming Jobs:                                       │
│  1. Update post engagement counters (like count, etc.)       │
│  2. Compute engagement velocity (likes per hour)             │
│  3. Detect viral posts (exponential growth)                  │
│  4. Update user interest profiles                            │
│  5. Feed training data pipeline                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 💻 Core Implementation

### **1. Candidate Generation**

```python
import redis
from cassandra.cluster import Cluster
from typing import List, Dict
from datetime import datetime, timedelta

class FeedCandidateGenerator:
    """
    Generate candidate posts from multiple sources
    """
    
    def __init__(self, redis_client, cassandra_session):
        self.redis = redis_client
        self.cassandra = cassandra_session
    
    def generate_candidates(self, user_id: str, limit: int = 1000) -> List[Dict]:
        """
        Generate candidate posts from all sources
        """
        
        candidates = []
        
        # 1. Friends' posts (social graph)
        friends_posts = self._get_friends_posts(user_id, limit=500)
        candidates.extend(friends_posts)
        
        # 2. Followed pages/topics (interest graph)
        interest_posts = self._get_interest_posts(user_id, limit=300)
        candidates.extend(interest_posts)
        
        # 3. Trending/viral posts
        trending_posts = self._get_trending_posts(limit=200)
        candidates.extend(trending_posts)
        
        # Deduplicate
        seen = set()
        unique_candidates = []
        for post in candidates:
            if post['post_id'] not in seen:
                seen.add(post['post_id'])
                unique_candidates.append(post)
        
        return unique_candidates[:limit]
    
    def _get_friends_posts(self, user_id: str, limit: int) -> List[Dict]:
        """
        Get recent posts from user's friends
        """
        
        # Get friend list (cached in Redis)
        friends = self.redis.smembers(f"user:{user_id}:friends")
        
        if not friends:
            # Fallback: query from Cassandra
            query = "SELECT friend_id FROM friendships WHERE user_id = %s"
            rows = self.cassandra.execute(query, (user_id,))
            friends = [row.friend_id for row in rows]
            
            # Cache for 1 hour
            if friends:
                self.redis.sadd(f"user:{user_id}:friends", *friends)
                self.redis.expire(f"user:{user_id}:friends", 3600)
        
        # Get recent posts from friends
        posts = []
        
        # Time window: last 7 days
        since = datetime.now() - timedelta(days=7)
        
        # Query Cassandra (posts partitioned by author_id)
        query = """
            SELECT post_id, author_id, content, created_at, media_type
            FROM posts_by_author
            WHERE author_id = %s AND created_at >= %s
            LIMIT 20
        """
        
        for friend_id in list(friends)[:100]:  # Limit friends to query
            rows = self.cassandra.execute(query, (friend_id, since))
            
            for row in rows:
                posts.append({
                    'post_id': str(row.post_id),
                    'author_id': str(row.author_id),
                    'content': row.content,
                    'created_at': row.created_at,
                    'media_type': row.media_type,
                    'source': 'friends'
                })
        
        # Sort by recency
        posts.sort(key=lambda x: x['created_at'], reverse=True)
        
        return posts[:limit]
    
    def _get_interest_posts(self, user_id: str, limit: int) -> List[Dict]:
        """
        Get posts from pages/topics user follows
        """
        
        # Get user interests (cached)
        interests = self.redis.smembers(f"user:{user_id}:interests")
        
        posts = []
        
        # For each interest, get recent high-quality posts
        for interest in list(interests)[:20]:  # Limit interests
            # Get top posts for this interest from Redis sorted set
            # Sorted by engagement score
            post_ids = self.redis.zrevrange(
                f"interest:{interest}:posts",
                0, 20,
                withscores=False
            )
            
            for post_id in post_ids:
                post_data = self._get_post_metadata(post_id)
                if post_data:
                    post_data['source'] = f'interest:{interest}'
                    posts.append(post_data)
        
        return posts[:limit]
    
    def _get_trending_posts(self, limit: int) -> List[Dict]:
        """
        Get globally trending posts
        """
        
        # Redis sorted set: trending posts by engagement velocity
        # Score = (likes + 3*comments + 5*shares) / age_hours
        
        trending_ids = self.redis.zrevrange(
            "trending:posts:global",
            0, limit - 1,
            withscores=True
        )
        
        posts = []
        for post_id, score in trending_ids:
            post_data = self._get_post_metadata(post_id)
            if post_data:
                post_data['source'] = 'trending'
                post_data['trending_score'] = score
                posts.append(post_data)
        
        return posts
    
    def _get_post_metadata(self, post_id: str) -> Dict:
        """
        Get post metadata from cache or database
        """
        
        # Try Redis cache first
        cached = self.redis.hgetall(f"post:{post_id}")
        
        if cached:
            return {
                'post_id': post_id,
                'author_id': cached.get(b'author_id', b'').decode(),
                'content': cached.get(b'content', b'').decode(),
                'media_type': cached.get(b'media_type', b'').decode(),
                'created_at': cached.get(b'created_at', b'').decode()
            }
        
        # Fallback: query Cassandra
        query = "SELECT * FROM posts WHERE post_id = %s"
        row = self.cassandra.execute(query, (post_id,)).one()
        
        if row:
            return {
                'post_id': post_id,
                'author_id': str(row.author_id),
                'content': row.content,
                'media_type': row.media_type,
                'created_at': row.created_at
            }
        
        return None


### **2. Feature Extraction**

```python
import numpy as np
from datetime import datetime
from typing import Dict

class FeedFeatureExtractor:
    """
    Extract 500+ features for ranking model
    """
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def extract_features(self, user_id: str, post: Dict) -> np.ndarray:
        """
        Extract feature vector for user-post pair
        """
        
        features = []
        
        # POST FEATURES (100 features)
        features.extend(self._extract_post_features(post))
        
        # ENGAGEMENT FEATURES (50 features)
        features.extend(self._extract_engagement_features(post['post_id']))
        
        # AUTHOR FEATURES (50 features)
        features.extend(self._extract_author_features(post['author_id']))
        
        # USER-POST AFFINITY (100 features)
        features.extend(self._extract_affinity_features(user_id, post))
        
        # CONTEXTUAL FEATURES (50 features)
        features.extend(self._extract_contextual_features(user_id))
        
        # HISTORICAL FEATURES (150 features)
        features.extend(self._extract_historical_features(user_id, post))
        
        return np.array(features, dtype=np.float32)
    
    def _extract_post_features(self, post: Dict) -> List[float]:
        """Post-level features"""
        
        features = []
        
        # Age in hours
        age_hours = (datetime.now() - post['created_at']).total_seconds() / 3600
        features.append(age_hours)
        features.append(np.log1p(age_hours))  # Log-transformed
        
        # Content type (one-hot)
        media_types = ['text', 'image', 'video', 'link', 'poll']
        for mt in media_types:
            features.append(1.0 if post['media_type'] == mt else 0.0)
        
        # Content length
        content_length = len(post.get('content', ''))
        features.append(content_length)
        features.append(np.log1p(content_length))
        
        # Sentiment score (from NLP model)
        sentiment = self._get_sentiment(post.get('content', ''))
        features.append(sentiment)
        
        # Topic probabilities (from classifier)
        topic_probs = self._get_topic_probabilities(post.get('content', ''))
        features.extend(topic_probs)  # e.g., 10 topics
        
        # Media quality score (for images/videos)
        if post['media_type'] in ['image', 'video']:
            quality = self._get_media_quality_score(post['post_id'])
            features.append(quality)
        else:
            features.append(0.0)
        
        return features
    
    def _extract_engagement_features(self, post_id: str) -> List[float]:
        """Engagement metrics"""
        
        features = []
        
        # Get engagement counts from Redis
        engagement = self.redis.hgetall(f"post:{post_id}:engagement")
        
        like_count = int(engagement.get(b'like_count', 0))
        comment_count = int(engagement.get(b'comment_count', 0))
        share_count = int(engagement.get(b'share_count', 0))
        click_count = int(engagement.get(b'click_count', 0))
        hide_count = int(engagement.get(b'hide_count', 0))
        
        # Raw counts
        features.extend([like_count, comment_count, share_count, click_count, hide_count])
        
        # Log-transformed counts
        features.extend([
            np.log1p(like_count),
            np.log1p(comment_count),
            np.log1p(share_count),
            np.log1p(click_count)
        ])
        
        # Engagement rates
        impression_count = int(engagement.get(b'impression_count', 1))
        features.append(like_count / impression_count)  # Like rate
        features.append(comment_count / impression_count)  # Comment rate
        features.append(share_count / impression_count)  # Share rate
        features.append(click_count / impression_count)  # CTR
        
        # Engagement velocity (counts per hour)
        post_age_hours = float(engagement.get(b'age_hours', 1))
        features.append(like_count / post_age_hours)
        features.append(comment_count / post_age_hours)
        
        # Negative feedback rate
        features.append(hide_count / impression_count if impression_count > 0 else 0)
        
        return features
    
    def _extract_affinity_features(self, user_id: str, post: Dict) -> List[float]:
        """User-post affinity features"""
        
        features = []
        
        author_id = post['author_id']
        
        # Historical engagement with author
        past_engagement = self.redis.hgetall(f"user:{user_id}:author:{author_id}")
        
        past_likes = int(past_engagement.get(b'like_count', 0))
        past_comments = int(past_engagement.get(b'comment_count', 0))
        past_shares = int(past_engagement.get(b'share_count', 0))
        
        features.extend([past_likes, past_comments, past_shares])
        features.extend([np.log1p(past_likes), np.log1p(past_comments), np.log1p(past_shares)])
        
        # Social distance (friend, friend-of-friend, stranger)
        distance = self._get_social_distance(user_id, author_id)
        features.append(distance)
        
        # Is following author?
        is_following = self.redis.sismember(f"user:{user_id}:following", author_id)
        features.append(1.0 if is_following else 0.0)
        
        return features
```

---

## 🎓 Key Interview Points

### **Capacity Estimation:**
```
Users: 2B
Feed requests: 10B/day = 115K/sec
Candidates per request: 1000 posts
Ranking: 1000 × 115K = 115M predictions/sec

Redis memory: 2B users × 1KB = 2 TB
Model serving: 10K QPS/server → 12 servers
```

### **Ranking Challenges:**
1. **Real-time** - Must rank in <200ms
2. **Personalization** - Different feed per user
3. **Diversity** - Avoid filter bubbles
4. **Quality** - Filter spam/misinformation

**Critical for social media interviews!** 📱👥
