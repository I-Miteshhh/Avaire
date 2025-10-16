# Design Real-Time Gaming Leaderboard - Complete System Design

**Difficulty:** ⭐⭐⭐⭐  
**Interview Frequency:** High (Gaming companies, DraftKings, Roblox, 40 LPA+)  
**Time to Complete:** 30-45 minutes  
**Real-World Examples:** Fortnite Leaderboard, Call of Duty Rankings, Clash Royale Trophy System

---

## 📋 Problem Statement

**Design a real-time leaderboard system that can:**
- Support 100 million active players globally
- Update rankings in real-time (<100ms latency)
- Support multiple leaderboard types (global, friends, regional, seasonal)
- Handle 1 million score updates per second
- Provide ranking queries (get top N, get player rank, get nearby players)
- Support time-based leaderboards (hourly, daily, weekly, all-time)
- Prevent cheating and score manipulation
- Scale to thousands of concurrent tournaments
- Support reward distribution based on rankings

**Business Goals:**
- Maximize player engagement through competitive rankings
- Ensure fair gameplay
- Support viral growth (friend competition)
- Monetize through ranked tournaments

---

## 🎯 Functional Requirements

### **Core Features**
1. **Score Updates**
   - Submit score (player_id, score, timestamp)
   - Validate score integrity (anti-cheat)
   - Update all relevant leaderboards atomically
   - Return new rank after update

2. **Leaderboard Queries**
   - Get top N players (top 10, top 100)
   - Get player's current rank
   - Get player's neighbors (rank ±10 positions)
   - Get player's percentile (top 1%, top 10%)
   - Paginated leaderboard browsing

3. **Leaderboard Types**
   - Global leaderboard (all players)
   - Friends leaderboard (player's social graph)
   - Regional leaderboards (country, state, city)
   - Time-based (hourly, daily, weekly, monthly, all-time)
   - Tournament leaderboards (with start/end times)

4. **Rewards & Notifications**
   - Distribute rewards at season end
   - Real-time notifications for rank changes
   - Achievement unlocks (reached top 100)

---

## 🏗️ High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                              │
├──────────────────────────────────────────────────────────────┤
│  Game Clients │ Web Dashboard │ Mobile Apps │ Admin Panel    │
└────┬─────────────┬──────────────┬──────────────────┬─────────┘
     │             │              │                  │
     ▼             ▼              ▼                  ▼
┌──────────────────────────────────────────────────────────────┐
│                 API GATEWAY (Kong)                            │
├──────────────────────────────────────────────────────────────┤
│  - Rate limiting (100 req/sec per player)                    │
│  - Authentication (JWT)                                       │
│  - Request validation                                         │
└────┬─────────────┬──────────────┬──────────────────┬─────────┘
     │             │              │                  │
     ▼             ▼              ▼                  ▼
┌──────────────────────────────────────────────────────────────┐
│                 LEADERBOARD SERVICES                          │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  SCORE UPDATE SERVICE (Write Path)                    │ │
│  │  POST /v1/scores                                       │ │
│  │  {                                                     │ │
│  │    "player_id": "p123",                                │ │
│  │    "score": 1500,                                      │ │
│  │    "match_id": "m456",                                 │ │
│  │    "timestamp": "2024-01-01T12:00:00Z"                 │ │
│  │  }                                                     │ │
│  │                                                        │ │
│  │  Steps:                                                │ │
│  │  1. Validate score (anti-cheat checks)                │ │
│  │  2. Publish to Kafka (async)                          │ │
│  │  3. Update Redis sorted sets (sync)                   │ │
│  │  4. Return new rank                                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  LEADERBOARD QUERY SERVICE (Read Path - Hot)          │ │
│  │                                                        │ │
│  │  GET /v1/leaderboards/{type}/top?limit=100            │ │
│  │  → Returns top N players                              │ │
│  │                                                        │ │
│  │  GET /v1/leaderboards/{type}/rank?player_id=p123      │ │
│  │  → Returns player's rank and neighbors                │ │
│  │                                                        │ │
│  │  GET /v1/leaderboards/{type}/friends?player_id=p123   │ │
│  │  → Returns friends' rankings                          │ │
│  │                                                        │ │
│  │  All queries: <50ms latency (Redis cached)            │ │
│  └────────────────────────────────────────────────────────┘ │
└────┬─────────────┬──────────────┬──────────────────┬─────────┘
     │             │              │                  │
     ▼             ▼              ▼                  ▼
┌──────────────────────────────────────────────────────────────┐
│              STORAGE LAYER - REDIS CLUSTER                    │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Data Structure: SORTED SETS (ZSET)                          │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                               │
│  Key Pattern: leaderboard:{type}:{period}:{region}           │
│                                                               │
│  Examples:                                                    │
│  - leaderboard:global:all_time:all                           │
│  - leaderboard:global:daily:2024-01-15                       │
│  - leaderboard:friends:weekly:player_p123                    │
│  - leaderboard:regional:monthly:US                           │
│  - leaderboard:tournament:event:tournament_123               │
│                                                               │
│  ZSET Operations (O(log N)):                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ZADD leaderboard:global:all_time:all 1500 "p123"   │   │
│  │  → Add/Update player score                           │   │
│  │                                                       │   │
│  │  ZREVRANK leaderboard:global:all_time:all "p123"     │   │
│  │  → Get player rank (0-indexed, descending)           │   │
│  │                                                       │   │
│  │  ZREVRANGE leaderboard:global:all_time:all 0 99      │   │
│  │  WITHSCORES                                           │   │
│  │  → Get top 100 players with scores                   │   │
│  │                                                       │   │
│  │  ZREVRANGE leaderboard:global:all_time:all           │   │
│  │  (rank-10) (rank+10) WITHSCORES                      │   │
│  │  → Get neighbors (20 players around user)            │   │
│  │                                                       │   │
│  │  ZCARD leaderboard:global:all_time:all               │   │
│  │  → Get total player count                            │   │
│  │                                                       │   │
│  │  ZCOUNT leaderboard:global:all_time:all 1000 +inf    │   │
│  │  → Count players with score >= 1000                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  Sharding Strategy:                                          │
│  - Shard by leaderboard type (global, regional, tournament)  │
│  - Each shard: 100M players × 16 bytes = 1.6 GB             │
│  - Replication: 3x for high availability                     │
│                                                               │
│  Persistence:                                                │
│  - RDB snapshots every 5 minutes                             │
│  - AOF for durability                                        │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│            STREAMING PIPELINE (Kafka + Flink)                 │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Kafka Topic: score-updates                                  │
│  Throughput: 1M updates/sec                                   │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  FLINK AGGREGATION JOB                                │ │
│  │                                                        │ │
│  │  1. Time-Based Leaderboards:                          │ │
│  │     - Tumbling window (1 hour, 1 day, 1 week)         │ │
│  │     - Aggregate max score per player                  │ │
│  │     - Write to Redis at window close                  │ │
│  │                                                        │ │
│  │  2. Anti-Cheat Detection:                             │ │
│  │     - Velocity checks (scores increasing too fast)    │ │
│  │     - Anomaly detection (impossible scores)           │ │
│  │     - Pattern matching (bot behavior)                 │ │
│  │                                                        │ │
│  │  3. Historical Analytics:                             │ │
│  │     - Write to S3 data lake                           │ │
│  │     - Aggregate to ClickHouse for analytics           │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                 METADATA STORE (PostgreSQL)                   │
├──────────────────────────────────────────────────────────────┤
│  - Player profiles (username, country, avatar)               │
│  - Tournament definitions (start_time, end_time, rules)      │
│  - Friend relationships (player_id, friend_id)               │
│  - Reward configurations (tier thresholds, prizes)           │
│  - Ban list (cheaters)                                       │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│              NOTIFICATION SERVICE (WebSocket + FCM)           │
├──────────────────────────────────────────────────────────────┤
│  - Real-time rank updates                                    │
│  - Friend overtook you notification                          │
│  - New high score achieved                                   │
│  - Tournament starting soon                                  │
└──────────────────────────────────────────────────────────────┘
```

---

## 💻 Core Implementation

### **1. Redis Sorted Set Leaderboard**

```python
import redis
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

class LeaderboardType(Enum):
    GLOBAL = "global"
    FRIENDS = "friends"
    REGIONAL = "regional"
    TOURNAMENT = "tournament"

class LeaderboardPeriod(Enum):
    ALL_TIME = "all_time"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    HOURLY = "hourly"

@dataclass
class PlayerScore:
    player_id: str
    score: int
    rank: int
    username: str
    country: str

@dataclass
class LeaderboardEntry:
    rank: int
    player_id: str
    username: str
    score: int
    country: str
    is_friend: bool = False

class RedisLeaderboard:
    """
    High-performance leaderboard using Redis Sorted Sets
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def _get_key(self, lb_type: LeaderboardType, period: LeaderboardPeriod, 
                 identifier: str = "all") -> str:
        """
        Generate Redis key for leaderboard
        
        Examples:
        - leaderboard:global:all_time:all
        - leaderboard:regional:daily:2024-01-15:US
        - leaderboard:friends:weekly:2024-W03:player_p123
        - leaderboard:tournament:event:tournament_123
        """
        
        if period == LeaderboardPeriod.DAILY:
            period_key = datetime.now().strftime("%Y-%m-%d")
        elif period == LeaderboardPeriod.WEEKLY:
            period_key = datetime.now().strftime("%Y-W%U")
        elif period == LeaderboardPeriod.MONTHLY:
            period_key = datetime.now().strftime("%Y-%m")
        elif period == LeaderboardPeriod.HOURLY:
            period_key = datetime.now().strftime("%Y-%m-%dT%H")
        else:  # ALL_TIME
            period_key = period.value
        
        return f"leaderboard:{lb_type.value}:{period_key}:{identifier}"
    
    def update_score(self, player_id: str, score: int, 
                    lb_type: LeaderboardType = LeaderboardType.GLOBAL,
                    period: LeaderboardPeriod = LeaderboardPeriod.ALL_TIME,
                    identifier: str = "all") -> int:
        """
        Update player score in leaderboard
        Returns new rank
        
        Time Complexity: O(log N)
        """
        
        key = self._get_key(lb_type, period, identifier)
        
        # ZADD adds or updates score
        # Use NX to only add if not exists, or XX to only update if exists
        # Default: update if exists, add if not exists
        self.redis.zadd(key, {player_id: score})
        
        # Get new rank (0-indexed, descending order)
        rank = self.redis.zrevrank(key, player_id)
        
        # Convert to 1-indexed
        return rank + 1 if rank is not None else None
    
    def increment_score(self, player_id: str, increment: int,
                       lb_type: LeaderboardType = LeaderboardType.GLOBAL,
                       period: LeaderboardPeriod = LeaderboardPeriod.ALL_TIME,
                       identifier: str = "all") -> int:
        """
        Increment player score (useful for kill counts, etc.)
        
        Time Complexity: O(log N)
        """
        
        key = self._get_key(lb_type, period, identifier)
        
        # ZINCRBY increments score
        new_score = self.redis.zincrby(key, increment, player_id)
        
        # Get new rank
        rank = self.redis.zrevrank(key, player_id)
        
        return rank + 1 if rank is not None else None
    
    def get_top_n(self, n: int = 100,
                  lb_type: LeaderboardType = LeaderboardType.GLOBAL,
                  period: LeaderboardPeriod = LeaderboardPeriod.ALL_TIME,
                  identifier: str = "all") -> List[LeaderboardEntry]:
        """
        Get top N players
        
        Time Complexity: O(log N + M) where M = n
        """
        
        key = self._get_key(lb_type, period, identifier)
        
        # ZREVRANGE returns members in descending order
        # Returns list of tuples: [(player_id, score), ...]
        results = self.redis.zrevrange(key, 0, n - 1, withscores=True)
        
        entries = []
        for rank, (player_id, score) in enumerate(results, start=1):
            # Fetch player metadata from cache/database
            player_data = self._get_player_metadata(player_id)
            
            entries.append(LeaderboardEntry(
                rank=rank,
                player_id=player_id,
                username=player_data['username'],
                score=int(score),
                country=player_data['country']
            ))
        
        return entries
    
    def get_player_rank(self, player_id: str,
                       lb_type: LeaderboardType = LeaderboardType.GLOBAL,
                       period: LeaderboardPeriod = LeaderboardPeriod.ALL_TIME,
                       identifier: str = "all") -> Optional[PlayerScore]:
        """
        Get player's current rank and score
        
        Time Complexity: O(log N)
        """
        
        key = self._get_key(lb_type, period, identifier)
        
        # Get rank (0-indexed)
        rank = self.redis.zrevrank(key, player_id)
        
        if rank is None:
            return None
        
        # Get score
        score = self.redis.zscore(key, player_id)
        
        # Get player metadata
        player_data = self._get_player_metadata(player_id)
        
        return PlayerScore(
            player_id=player_id,
            score=int(score),
            rank=rank + 1,  # 1-indexed
            username=player_data['username'],
            country=player_data['country']
        )
    
    def get_neighbors(self, player_id: str, distance: int = 10,
                     lb_type: LeaderboardType = LeaderboardType.GLOBAL,
                     period: LeaderboardPeriod = LeaderboardPeriod.ALL_TIME,
                     identifier: str = "all") -> List[LeaderboardEntry]:
        """
        Get players around user (rank ± distance)
        Useful for showing "You're 5 spots away from top 100!"
        
        Time Complexity: O(log N + M) where M = 2*distance
        """
        
        key = self._get_key(lb_type, period, identifier)
        
        # Get player's rank
        player_rank = self.redis.zrevrank(key, player_id)
        
        if player_rank is None:
            return []
        
        # Calculate range
        start = max(0, player_rank - distance)
        end = player_rank + distance
        
        # Get range
        results = self.redis.zrevrange(key, start, end, withscores=True)
        
        entries = []
        for idx, (pid, score) in enumerate(results):
            rank = start + idx + 1
            player_data = self._get_player_metadata(pid)
            
            entries.append(LeaderboardEntry(
                rank=rank,
                player_id=pid,
                username=player_data['username'],
                score=int(score),
                country=player_data['country'],
                is_friend=False  # Would check friendship
            ))
        
        return entries
    
    def get_player_percentile(self, player_id: str,
                             lb_type: LeaderboardType = LeaderboardType.GLOBAL,
                             period: LeaderboardPeriod = LeaderboardPeriod.ALL_TIME,
                             identifier: str = "all") -> float:
        """
        Get player's percentile (e.g., top 5%)
        
        Time Complexity: O(log N)
        """
        
        key = self._get_key(lb_type, period, identifier)
        
        # Get player rank
        rank = self.redis.zrevrank(key, player_id)
        
        if rank is None:
            return None
        
        # Get total players
        total = self.redis.zcard(key)
        
        # Calculate percentile
        percentile = (rank / total) * 100
        
        return round(percentile, 2)
    
    def get_players_above_score(self, min_score: int,
                               lb_type: LeaderboardType = LeaderboardType.GLOBAL,
                               period: LeaderboardPeriod = LeaderboardPeriod.ALL_TIME,
                               identifier: str = "all") -> int:
        """
        Count players above a score threshold
        Useful for: "You need 500 more points to reach top tier"
        
        Time Complexity: O(log N)
        """
        
        key = self._get_key(lb_type, period, identifier)
        
        # ZCOUNT counts members in score range
        count = self.redis.zcount(key, min_score, '+inf')
        
        return count
    
    def remove_player(self, player_id: str,
                     lb_type: LeaderboardType = LeaderboardType.GLOBAL,
                     period: LeaderboardPeriod = LeaderboardPeriod.ALL_TIME,
                     identifier: str = "all") -> bool:
        """
        Remove player from leaderboard (e.g., banned for cheating)
        
        Time Complexity: O(log N)
        """
        
        key = self._get_key(lb_type, period, identifier)
        
        # ZREM removes member
        removed = self.redis.zrem(key, player_id)
        
        return removed > 0
    
    def get_friends_leaderboard(self, player_id: str, friend_ids: List[str],
                               period: LeaderboardPeriod = LeaderboardPeriod.ALL_TIME) -> List[LeaderboardEntry]:
        """
        Get leaderboard for player and friends
        
        Time Complexity: O(M * log N) where M = number of friends
        """
        
        key = self._get_key(LeaderboardType.GLOBAL, period, "all")
        
        # Include player in list
        all_players = [player_id] + friend_ids
        
        # Get scores for all
        pipeline = self.redis.pipeline()
        for pid in all_players:
            pipeline.zscore(key, pid)
            pipeline.zrevrank(key, pid)
        
        results = pipeline.execute()
        
        # Parse results
        entries = []
        for i in range(0, len(results), 2):
            pid = all_players[i // 2]
            score = results[i]
            rank = results[i + 1]
            
            if score is not None:
                player_data = self._get_player_metadata(pid)
                entries.append(LeaderboardEntry(
                    rank=rank + 1,
                    player_id=pid,
                    username=player_data['username'],
                    score=int(score),
                    country=player_data['country'],
                    is_friend=(pid != player_id)
                ))
        
        # Sort by score
        entries.sort(key=lambda x: x.score, reverse=True)
        
        # Update local ranks
        for idx, entry in enumerate(entries, start=1):
            entry.rank = idx
        
        return entries
    
    def _get_player_metadata(self, player_id: str) -> Dict:
        """Get player metadata (cached in Redis)"""
        
        # Check cache
        cached = self.redis.hgetall(f"player:{player_id}")
        
        if cached:
            return {
                'username': cached.get(b'username', b'').decode('utf-8'),
                'country': cached.get(b'country', b'').decode('utf-8')
            }
        
        # Fallback (would query PostgreSQL)
        return {'username': f'Player{player_id[-4:]}', 'country': 'US'}


### **2. Anti-Cheat Score Validation**

```python
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib

@dataclass
class ScoreValidationResult:
    is_valid: bool
    reason: Optional[str]
    risk_score: float  # 0-100

class AntiCheatValidator:
    """
    Validate score submissions to prevent cheating
    """
    
    def __init__(self, redis_client):
        self.redis = redis_client
        
        # Thresholds
        self.MAX_SCORE_PER_MATCH = 10000
        self.MAX_SCORE_INCREASE_PER_HOUR = 50000
        self.MIN_MATCH_DURATION_SECONDS = 60
    
    def validate_score(self, player_id: str, score: int, 
                      match_id: str, match_duration_seconds: int,
                      game_hash: str) -> ScoreValidationResult:
        """
        Comprehensive score validation
        """
        
        # 1. Check if score is within reasonable bounds
        if score > self.MAX_SCORE_PER_MATCH:
            return ScoreValidationResult(
                is_valid=False,
                reason=f"Score {score} exceeds maximum {self.MAX_SCORE_PER_MATCH}",
                risk_score=100.0
            )
        
        # 2. Check match duration (too short = bot)
        if match_duration_seconds < self.MIN_MATCH_DURATION_SECONDS:
            return ScoreValidationResult(
                is_valid=False,
                reason=f"Match too short: {match_duration_seconds}s",
                risk_score=90.0
            )
        
        # 3. Velocity check: score increase rate
        hour_key = datetime.now().strftime("%Y-%m-%dT%H")
        score_this_hour_key = f"player:{player_id}:score_increase:{hour_key}"
        
        score_this_hour = int(self.redis.get(score_this_hour_key) or 0)
        
        if score_this_hour + score > self.MAX_SCORE_INCREASE_PER_HOUR:
            return ScoreValidationResult(
                is_valid=False,
                reason=f"Score increase too fast: {score_this_hour + score} in 1 hour",
                risk_score=95.0
            )
        
        # Update velocity counter
        pipeline = self.redis.pipeline()
        pipeline.incrby(score_this_hour_key, score)
        pipeline.expire(score_this_hour_key, 3600)  # 1 hour TTL
        pipeline.execute()
        
        # 4. Game client hash verification
        expected_hash = self._compute_game_hash(player_id, score, match_id)
        
        if game_hash != expected_hash:
            return ScoreValidationResult(
                is_valid=False,
                reason="Invalid game client hash - possible tampering",
                risk_score=100.0
            )
        
        # 5. Check duplicate match submission
        match_key = f"match:{match_id}:submitted"
        if self.redis.exists(match_key):
            return ScoreValidationResult(
                is_valid=False,
                reason="Duplicate match submission",
                risk_score=100.0
            )
        
        # Mark match as submitted
        self.redis.setex(match_key, 86400, "1")  # 24 hour TTL
        
        return ScoreValidationResult(
            is_valid=True,
            reason=None,
            risk_score=0.0
        )
    
    def _compute_game_hash(self, player_id: str, score: int, match_id: str) -> str:
        """
        Compute tamper-proof hash
        In production: use HMAC with server-side secret
        """
        
        secret = "server_secret_key"
        data = f"{player_id}{score}{match_id}{secret}"
        
        return hashlib.sha256(data.encode()).hexdigest()


### **3. Leaderboard API Service**

```python
from flask import Flask, request, jsonify
from typing import Dict

app = Flask(__name__)

class LeaderboardAPI:
    """
    RESTful API for leaderboard operations
    """
    
    def __init__(self, redis_client, postgres_conn):
        self.leaderboard = RedisLeaderboard(redis_client)
        self.validator = AntiCheatValidator(redis_client)
        self.postgres = postgres_conn
    
    @app.route('/v1/scores', methods=['POST'])
    def submit_score(self):
        """
        POST /v1/scores
        {
            "player_id": "p123",
            "score": 1500,
            "match_id": "m456",
            "match_duration_seconds": 300,
            "game_hash": "abc123..."
        }
        """
        
        data = request.json
        
        player_id = data['player_id']
        score = data['score']
        match_id = data['match_id']
        match_duration = data['match_duration_seconds']
        game_hash = data['game_hash']
        
        # 1. Validate score
        validation = self.validator.validate_score(
            player_id, score, match_id, match_duration, game_hash
        )
        
        if not validation.is_valid:
            return jsonify({
                'success': False,
                'error': validation.reason,
                'risk_score': validation.risk_score
            }), 400
        
        # 2. Update leaderboards (multiple)
        global_rank = self.leaderboard.update_score(
            player_id, score, LeaderboardType.GLOBAL, LeaderboardPeriod.ALL_TIME
        )
        
        daily_rank = self.leaderboard.update_score(
            player_id, score, LeaderboardType.GLOBAL, LeaderboardPeriod.DAILY
        )
        
        # 3. Get player's new percentile
        percentile = self.leaderboard.get_player_percentile(player_id)
        
        return jsonify({
            'success': True,
            'new_rank': global_rank,
            'daily_rank': daily_rank,
            'percentile': percentile,
            'message': f'Ranked #{global_rank} globally!'
        }), 200
    
    @app.route('/v1/leaderboards/<leaderboard_type>/top', methods=['GET'])
    def get_top_players(self, leaderboard_type: str):
        """
        GET /v1/leaderboards/global/top?limit=100&period=all_time
        """
        
        limit = int(request.args.get('limit', 100))
        period = LeaderboardPeriod(request.args.get('period', 'all_time'))
        
        lb_type = LeaderboardType(leaderboard_type)
        
        entries = self.leaderboard.get_top_n(limit, lb_type, period)
        
        return jsonify({
            'leaderboard_type': leaderboard_type,
            'period': period.value,
            'entries': [
                {
                    'rank': e.rank,
                    'player_id': e.player_id,
                    'username': e.username,
                    'score': e.score,
                    'country': e.country
                }
                for e in entries
            ]
        }), 200
```

---

## 🎓 Key Interview Points

### **Capacity Estimation:**
```
Players: 100M active
Score updates: 1M/sec
Redis memory: 100M players × 16 bytes/entry = 1.6 GB per leaderboard
Total leaderboards: 100 (global, regional, time-based) = 160 GB

Read QPS: 100K requests/sec (get rank queries)
Write QPS: 1M updates/sec

Redis cluster: 10 shards × 16 GB = 160 GB total
```

### **Why Redis Sorted Sets?**
- O(log N) updates and queries (fast!)
- Native ranking support (ZREVRANK)
- Atomic operations (no race conditions)
- Persistence (RDB + AOF)

**Perfect for gaming/competitive ranking interviews!** 🎮🏆
