# Design Low-Latency Stock Trading Platform - Complete System Design

**Difficulty:** ⭐⭐⭐⭐⭐  
**Interview Frequency:** Very High (Trading firms, Bloomberg, Robinhood, 40 LPA+)  
**Time to Complete:** 45-60 minutes  
**Real-World Examples:** Interactive Brokers, TD Ameritrade, Robinhood, E*TRADE

---

## 📋 Problem Statement

**Design a low-latency stock trading platform that can:**
- Execute trades in <10ms (ultra-low latency)
- Process 1 million orders per second
- Support real-time market data streaming (quotes, trades, orderbook)
- Ensure ACID guarantees for transactions
- Handle order matching (market, limit, stop-loss orders)
- Provide real-time portfolio updates
- Support risk management (margin checks, circuit breakers)
- Maintain order audit trail for compliance
- Handle market data from 50+ exchanges globally
- Support high-frequency trading (HFT) strategies

**Business Goals:**
- Minimize trade execution latency
- Maximize order throughput
- Ensure regulatory compliance (SEC, FINRA)
- Prevent fraud and market manipulation
- Provide best execution price

---

## 🎯 Functional Requirements

### **Core Features**
1. **Order Management**
   - Place orders (market, limit, stop-loss, stop-limit)
   - Cancel/modify pending orders
   - Order validation (sufficient funds, valid symbols)
   - Order routing to exchanges

2. **Order Matching**
   - Price-time priority matching
   - Continuous matching (no batching for latency)
   - Partial fills support
   - Support multiple order types

3. **Market Data**
   - Real-time quotes (bid/ask prices)
   - Trade execution stream
   - Level 2 orderbook depth
   - Historical OHLCV data

4. **Portfolio Management**
   - Real-time position tracking
   - P&L calculation
   - Margin requirements
   - Risk exposure monitoring

---

## 🏗️ High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                 CLIENT APPLICATIONS                           │
├──────────────────────────────────────────────────────────────┤
│  Trading UI │ Mobile Apps │ FIX Protocol │ Algorithmic APIs  │
└────┬─────────────┬──────────────┬──────────────────┬─────────┘
     │             │              │                  │
     ▼             ▼              ▼                  ▼
┌──────────────────────────────────────────────────────────────┐
│              API GATEWAY (Ultra-Low Latency)                  │
├──────────────────────────────────────────────────────────────┤
│  - Co-located with exchanges (reduce network latency)        │
│  - Kernel bypass networking (DPDK)                           │
│  - Connection pooling                                        │
│  - FIX protocol support                                      │
└────┬─────────────┬──────────────┬──────────────────┬─────────┘
     │             │              │                  │
     ▼             ▼              ▼                  ▼
┌──────────────────────────────────────────────────────────────┐
│                  ORDER PROCESSING PIPELINE                    │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  ORDER VALIDATOR (<1ms)                               │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  Checks:                                              │ │
│  │  1. Symbol valid? (in-memory cache)                   │ │
│  │  2. Market hours? (trading halted?)                   │ │
│  │  3. Sufficient buying power?                          │ │
│  │  4. Order size within limits?                         │ │
│  │  5. Price within circuit breaker bands?               │ │
│  │  6. User not flagged/suspended?                       │ │
│  │                                                        │ │
│  │  → Reject invalid orders immediately                  │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  MATCHING ENGINE (<5ms)                               │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  Data Structure: In-Memory Orderbook                  │ │
│  │                                                        │ │
│  │  Buy Orders (Bids):  Priority Queue (Max Heap)        │ │
│  │  ┌───────────────────────────────────────┐           │ │
│  │  │  Price: $150.50  Size: 100  Time: t1  │ ← Best    │ │
│  │  │  Price: $150.25  Size: 200  Time: t2  │           │ │
│  │  │  Price: $150.00  Size: 500  Time: t3  │           │ │
│  │  └───────────────────────────────────────┘           │ │
│  │                                                        │ │
│  │  Sell Orders (Asks): Priority Queue (Min Heap)        │ │
│  │  ┌───────────────────────────────────────┐           │ │
│  │  │  Price: $150.75  Size: 150  Time: t4  │ ← Best    │ │
│  │  │  Price: $151.00  Size: 300  Time: t5  │           │ │
│  │  │  Price: $151.25  Size: 400  Time: t6  │           │ │
│  │  └───────────────────────────────────────┘           │ │
│  │                                                        │ │
│  │  Matching Logic:                                      │ │
│  │  1. Market Buy → Match with best ask                 │ │
│  │  2. Limit Buy @ $150.75 → Match if ask <= $150.75    │ │
│  │  3. Price-Time Priority (FIFO at same price)         │ │
│  │  4. Partial fills if insufficient volume             │ │
│  │                                                        │ │
│  │  Optimizations:                                       │ │
│  │  - Lock-free data structures (no mutex contention)   │ │
│  │  - Single-threaded per symbol (no locks!)            │ │
│  │  - Memory pools (avoid allocations)                  │ │
│  │  - CPU pinning (avoid context switches)              │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  RISK MANAGER (<2ms)                                  │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  Pre-Trade Checks:                                    │ │
│  │  - Margin requirements (Reg T: 50% for stocks)        │ │
│  │  - Pattern day trader rules (4 trades in 5 days)      │ │
│  │  - Position limits (max shares per symbol)            │ │
│  │  - Exposure limits (max % of portfolio)               │ │
│  │                                                        │ │
│  │  Post-Trade Updates:                                  │ │
│  │  - Update buying power                                │ │
│  │  - Recalculate margin                                 │ │
│  │  - Mark positions                                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  EXECUTION ENGINE (<2ms)                              │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  1. Write to WAL (Write-Ahead Log) for durability    │ │
│  │  2. Update positions (in-memory)                      │ │
│  │  3. Publish fill notifications (Kafka)                │ │
│  │  4. Send confirmations to clients (WebSocket)         │ │
│  │  5. Async: Persist to database                        │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│             MARKET DATA PIPELINE (Real-Time)                  │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Exchange Feeds → Multicast UDP → Market Data Processor      │
│  (NYSE, NASDAQ)                    (C++, Kernel Bypass)       │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  MARKET DATA NORMALIZATION                            │ │
│  │  - Parse exchange-specific protocols (ITCH, OUCH)     │ │
│  │  - Normalize to common format                         │ │
│  │  - Conflate (merge updates within 1ms)                │ │
│  │  - Publish to Redis + Kafka                           │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  ORDERBOOK RECONSTRUCTION                             │ │
│  │  - Maintain Level 2 depth (top 10 bids/asks)          │ │
│  │  - Handle add/modify/delete messages                  │ │
│  │  - Snapshot + incremental updates                     │ │
│  │  - Publish to WebSocket subscribers                   │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                    STORAGE LAYER                              │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  IN-MEMORY (Redis/Memcached)                          │ │
│  │  - Current positions (user_id → {symbol → quantity})  │ │
│  │  - Buying power cache                                 │ │
│  │  - Latest market data (quotes, last prices)           │ │
│  │  - Orderbook snapshots                                │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  WRITE-AHEAD LOG (RocksDB/LMDB)                       │ │
│  │  - Append-only log for all orders/fills              │ │
│  │  - Crash recovery (replay WAL)                        │ │
│  │  - Millisecond-level persistence                      │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  TRANSACTIONAL DB (PostgreSQL with Citus)             │ │
│  │  - Orders table (order_id, user_id, symbol, ...)     │ │
│  │  - Fills table (fill_id, order_id, price, quantity)  │ │
│  │  - Positions table (user_id, symbol, quantity, ...)  │ │
│  │  - Accounts table (user_id, buying_power, margin)    │ │
│  │  - Sharded by user_id                                 │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  TIME-SERIES DB (TimescaleDB/InfluxDB)                │ │
│  │  - OHLCV bars (1min, 5min, 1hour, 1day)              │ │
│  │  - Tick data (every trade)                            │ │
│  │  - Quote data (bid/ask snapshots)                     │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## 💻 Core Implementation

### **1. In-Memory Orderbook Matching Engine**

```python
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import heapq
from collections import deque

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    STOP_LIMIT = "stop_limit"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

@dataclass(order=True)
class Order:
    # Price-time priority: sort by price, then timestamp
    priority: Tuple[float, int] = field(init=False, repr=False)
    
    order_id: str = field(compare=False)
    user_id: str = field(compare=False)
    symbol: str = field(compare=False)
    side: OrderSide = field(compare=False)
    order_type: OrderType = field(compare=False)
    quantity: int = field(compare=False)
    filled_quantity: int = field(compare=False, default=0)
    price: Optional[float] = field(compare=False, default=None)  # None for market orders
    stop_price: Optional[float] = field(compare=False, default=None)
    timestamp: datetime = field(compare=False, default_factory=datetime.now)
    status: OrderStatus = field(compare=False, default=OrderStatus.PENDING)
    
    def __post_init__(self):
        # For buy orders: higher price = higher priority (use negative for max heap)
        # For sell orders: lower price = higher priority (use positive for min heap)
        # Secondary: earlier timestamp = higher priority
        
        timestamp_ns = int(self.timestamp.timestamp() * 1_000_000_000)
        
        if self.side == OrderSide.BUY:
            # Max heap: negate price (higher price first)
            self.priority = (-self.price if self.price else float('-inf'), timestamp_ns)
        else:  # SELL
            # Min heap: positive price (lower price first)
            self.priority = (self.price if self.price else float('inf'), timestamp_ns)
    
    @property
    def remaining_quantity(self) -> int:
        return self.quantity - self.filled_quantity
    
    @property
    def is_fully_filled(self) -> bool:
        return self.filled_quantity >= self.quantity

@dataclass
class Fill:
    fill_id: str
    buy_order_id: str
    sell_order_id: str
    symbol: str
    price: float
    quantity: int
    timestamp: datetime

class Orderbook:
    """
    In-memory orderbook with price-time priority matching
    
    Time Complexity:
    - Insert: O(log N)
    - Match: O(log N) per match
    - Cancel: O(N) worst case (need to find order)
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        
        # Priority queues
        self.bids: List[Order] = []  # Buy orders (max heap by price)
        self.asks: List[Order] = []  # Sell orders (min heap by price)
        
        # Order lookup (for cancellations)
        self.orders: Dict[str, Order] = {}
        
        # Market data
        self.last_price: Optional[float] = None
        self.last_trade_time: Optional[datetime] = None
    
    def add_order(self, order: Order) -> List[Fill]:
        """
        Add order to orderbook and attempt matching
        Returns list of fills
        """
        
        fills = []
        
        # Market orders: match immediately
        if order.order_type == OrderType.MARKET:
            fills = self._match_market_order(order)
        
        # Limit orders: try to match, then add to book
        elif order.order_type == OrderType.LIMIT:
            fills = self._match_limit_order(order)
            
            # If not fully filled, add to orderbook
            if not order.is_fully_filled:
                self._add_to_book(order)
        
        return fills
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel pending order
        Time Complexity: O(N) to find in heap, O(log N) to remove
        """
        
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        order.status = OrderStatus.CANCELLED
        
        # Remove from orderbook (mark as cancelled, lazy removal)
        # Actual removal happens during matching
        
        del self.orders[order_id]
        
        return True
    
    def _match_market_order(self, order: Order) -> List[Fill]:
        """
        Match market order against best available prices
        """
        
        fills = []
        
        if order.side == OrderSide.BUY:
            # Match against asks (sell orders)
            while not order.is_fully_filled and self.asks:
                fills.extend(self._execute_match(order, self.asks))
        
        else:  # SELL
            # Match against bids (buy orders)
            while not order.is_fully_filled and self.bids:
                fills.extend(self._execute_match(order, self.bids))
        
        if order.is_fully_filled:
            order.status = OrderStatus.FILLED
        else:
            order.status = OrderStatus.PARTIAL
        
        return fills
    
    def _match_limit_order(self, order: Order) -> List[Fill]:
        """
        Match limit order if price crosses spread
        """
        
        fills = []
        
        if order.side == OrderSide.BUY:
            # Match against asks if ask price <= bid price
            while (not order.is_fully_filled and 
                   self.asks and 
                   self.asks[0].price <= order.price):
                fills.extend(self._execute_match(order, self.asks))
        
        else:  # SELL
            # Match against bids if bid price >= ask price
            while (not order.is_fully_filled and 
                   self.bids and 
                   self.bids[0].price >= order.price):
                fills.extend(self._execute_match(order, self.bids))
        
        if order.is_fully_filled:
            order.status = OrderStatus.FILLED
        elif fills:
            order.status = OrderStatus.PARTIAL
        
        return fills
    
    def _execute_match(self, incoming_order: Order, book: List[Order]) -> List[Fill]:
        """
        Execute match between incoming order and best order in book
        """
        
        fills = []
        
        # Get best order
        while book and book[0].status == OrderStatus.CANCELLED:
            # Remove cancelled orders (lazy deletion)
            heapq.heappop(book)
        
        if not book:
            return fills
        
        resting_order = book[0]
        
        # Calculate fill quantity
        fill_quantity = min(incoming_order.remaining_quantity, 
                           resting_order.remaining_quantity)
        
        # Execute fill at resting order's price (price-time priority)
        fill_price = resting_order.price
        
        # Create fill
        fill = Fill(
            fill_id=f"fill_{len(fills)}",
            buy_order_id=incoming_order.order_id if incoming_order.side == OrderSide.BUY else resting_order.order_id,
            sell_order_id=resting_order.order_id if incoming_order.side == OrderSide.BUY else incoming_order.order_id,
            symbol=self.symbol,
            price=fill_price,
            quantity=fill_quantity,
            timestamp=datetime.now()
        )
        
        fills.append(fill)
        
        # Update order quantities
        incoming_order.filled_quantity += fill_quantity
        resting_order.filled_quantity += fill_quantity
        
        # Update market data
        self.last_price = fill_price
        self.last_trade_time = fill.timestamp
        
        # Remove fully filled resting order
        if resting_order.is_fully_filled:
            heapq.heappop(book)
            resting_order.status = OrderStatus.FILLED
            if resting_order.order_id in self.orders:
                del self.orders[resting_order.order_id]
        
        return fills
    
    def _add_to_book(self, order: Order):
        """Add order to orderbook"""
        
        if order.side == OrderSide.BUY:
            heapq.heappush(self.bids, order)
        else:
            heapq.heappush(self.asks, order)
        
        self.orders[order.order_id] = order
    
    def get_best_bid(self) -> Optional[float]:
        """Get best bid price"""
        while self.bids and self.bids[0].status == OrderStatus.CANCELLED:
            heapq.heappop(self.bids)
        return self.bids[0].price if self.bids else None
    
    def get_best_ask(self) -> Optional[float]:
        """Get best ask price"""
        while self.asks and self.asks[0].status == OrderStatus.CANCELLED:
            heapq.heappop(self.asks)
        return self.asks[0].price if self.asks else None
    
    def get_spread(self) -> Optional[float]:
        """Get bid-ask spread"""
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        
        if best_bid and best_ask:
            return best_ask - best_bid
        return None
    
    def get_depth(self, levels: int = 10) -> Dict:
        """
        Get Level 2 market depth
        """
        
        # Aggregate by price level
        bid_levels = {}
        ask_levels = {}
        
        for order in self.bids:
            if order.status != OrderStatus.CANCELLED:
                price = order.price
                bid_levels[price] = bid_levels.get(price, 0) + order.remaining_quantity
        
        for order in self.asks:
            if order.status != OrderStatus.CANCELLED:
                price = order.price
                ask_levels[price] = ask_levels.get(price, 0) + order.remaining_quantity
        
        # Sort and limit
        top_bids = sorted(bid_levels.items(), reverse=True)[:levels]
        top_asks = sorted(ask_levels.items())[:levels]
        
        return {
            'bids': [{'price': p, 'size': s} for p, s in top_bids],
            'asks': [{'price': p, 'size': s} for p, s in top_asks],
            'last_price': self.last_price,
            'spread': self.get_spread()
        }


### **2. Risk Manager**

```python
class RiskManager:
    """
    Pre-trade risk checks
    """
    
    def __init__(self, redis_client):
        self.redis = redis_client
        
        # Regulatory requirements
        self.INITIAL_MARGIN = 0.50  # Reg T: 50% initial margin
        self.MAINTENANCE_MARGIN = 0.25  # 25% maintenance margin
        self.PDT_THRESHOLD = 4  # Pattern Day Trader: 4 trades in 5 days
        self.MIN_ACCOUNT_EQUITY = 25000  # PDT minimum equity
    
    def validate_order(self, user_id: str, order: Order, current_price: float) -> Tuple[bool, Optional[str]]:
        """
        Pre-trade risk validation
        """
        
        # 1. Check buying power
        order_value = current_price * order.quantity
        
        buying_power = self._get_buying_power(user_id)
        
        if order.side == OrderSide.BUY:
            # Need 50% margin for stock purchases
            required_margin = order_value * self.INITIAL_MARGIN
            
            if buying_power < required_margin:
                return False, f"Insufficient buying power: ${buying_power:.2f} < ${required_margin:.2f}"
        
        # 2. Check Pattern Day Trader rules
        if self._is_day_trade(user_id, order):
            trade_count = self._get_day_trade_count(user_id)
            
            if trade_count >= self.PDT_THRESHOLD:
                account_equity = self._get_account_equity(user_id)
                
                if account_equity < self.MIN_ACCOUNT_EQUITY:
                    return False, f"Pattern Day Trader violation: Need ${self.MIN_ACCOUNT_EQUITY} equity"
        
        # 3. Check position limits
        current_position = self._get_position(user_id, order.symbol)
        max_position = 10000  # Example: max 10,000 shares
        
        if order.side == OrderSide.BUY:
            new_position = current_position + order.quantity
            if new_position > max_position:
                return False, f"Position limit exceeded: {new_position} > {max_position}"
        
        return True, None
    
    def _get_buying_power(self, user_id: str) -> float:
        """Get user's available buying power"""
        bp = self.redis.get(f"user:{user_id}:buying_power")
        return float(bp) if bp else 0.0
```

---

## 🎓 Key Interview Points

### **Capacity Estimation:**
```
Orders: 1M/sec
Latency: <10ms end-to-end
Matching engine: Single-threaded per symbol (no locks!)
Symbols: 10,000 stocks × 100 KB/orderbook = 1 GB memory

Write-Ahead Log: 1M orders/sec × 200 bytes = 200 MB/sec = 17 TB/day
```

### **Low-Latency Techniques:**
1. **Lock-free algorithms** - Single thread per symbol
2. **Kernel bypass** - DPDK networking
3. **CPU pinning** - Avoid context switches
4. **Memory pools** - Pre-allocated objects
5. **Co-location** - Servers near exchanges

**Perfect for HFT/trading firm interviews!** 📈💹
