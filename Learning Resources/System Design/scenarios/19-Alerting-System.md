# Design Intelligent Alerting System - Complete System Design

**Difficulty:** ⭐⭐⭐⭐⭐  
**Interview Frequency:** High (SRE/Infrastructure roles, 40 LPA+)  
**Time to Complete:** 35-40 minutes  
**Real-World Examples:** PagerDuty, Opsgenie, VictorOps

---

## 📋 Problem Statement

**Design an intelligent alerting system that can:**
- Process 1 million alert events per day
- Reduce alert noise (deduplication, correlation)
- Support escalation policies (on-call rotation)
- Prevent alert fatigue with ML-based anomaly detection
- Provide multi-channel notifications (SMS, email, phone, Slack)
- Track alert lifecycle (acknowledged, resolved)
- Support dependency-based alert suppression
- Provide on-call scheduling and incident management
- Handle alert storms gracefully

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    ALERT PROCESSING PIPELINE                  │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Alert Sources:                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Prometheus  │  │  Datadog    │  │   Custom    │         │
│  │  Alerts     │  │  Monitors   │  │   Scripts   │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                  │
│         └────────────────┼────────────────┘                  │
│                          ▼                                    │
│              ┌───────────────────────┐                       │
│              │   ALERT RECEIVER      │                       │
│              │   ━━━━━━━━━━━━━━━━━   │                       │
│              │   POST /alerts        │                       │
│              │   {                    │                       │
│              │     "alert_id": "...", │                       │
│              │     "severity": "...", │                       │
│              │     "message": "...",  │                       │
│              │     "labels": {...}    │                       │
│              │   }                    │                       │
│              └───────────┬───────────┘                       │
│                          │                                    │
│                          ▼                                    │
│              ┌───────────────────────────────────┐           │
│              │   PREPROCESSING                   │           │
│              │   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │           │
│              │   1. Validate schema              │           │
│              │   2. Enrich with metadata         │           │
│              │   3. Add fingerprint (for dedup)  │           │
│              │   4. Check blacklist/whitelist    │           │
│              └───────────┬───────────────────────┘           │
│                          │                                    │
│                          ▼                                    │
│              ┌───────────────────────────────────┐           │
│              │   DEDUPLICATION ENGINE            │           │
│              │   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │           │
│              │   Fingerprint: hash(labels)       │           │
│              │                                    │           │
│              │   If fingerprint exists:          │           │
│              │   - Update existing alert         │           │
│              │   - Increment counter             │           │
│              │   - Update last_seen              │           │
│              │   Else:                            │           │
│              │   - Create new alert              │           │
│              └───────────┬───────────────────────┘           │
│                          │                                    │
│                          ▼                                    │
│              ┌───────────────────────────────────┐           │
│              │   CORRELATION ENGINE              │           │
│              │   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │           │
│              │   Group related alerts:           │           │
│              │   - Same service                  │           │
│              │   - Time proximity (5 min window) │           │
│              │   - Dependency graph              │           │
│              │                                    │           │
│              │   Example:                         │           │
│              │   "Database down" +               │           │
│              │   "API errors" +                  │           │
│              │   "User complaints"               │           │
│              │   → Root cause: Database          │           │
│              └───────────┬───────────────────────┘           │
│                          │                                    │
│                          ▼                                    │
│              ┌───────────────────────────────────┐           │
│              │   SUPPRESSION RULES               │           │
│              │   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │           │
│              │   IF parent alert firing:         │           │
│              │   - Suppress child alerts         │           │
│              │                                    │           │
│              │   IF maintenance window:          │           │
│              │   - Suppress all alerts           │           │
│              │                                    │           │
│              │   IF similar alert resolved <5min:│           │
│              │   - Suppress (flapping)           │           │
│              └───────────┬───────────────────────┘           │
│                          │                                    │
│                          ▼                                    │
│              ┌───────────────────────────────────┐           │
│              │   SEVERITY SCORING (ML)           │           │
│              │   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │           │
│              │   Features:                        │           │
│              │   - Alert frequency                │           │
│              │   - Affected services              │           │
│              │   - Error rate spike               │           │
│              │   - Historical impact              │           │
│              │                                    │           │
│              │   Model: XGBoost classifier       │           │
│              │   Output: P0/P1/P2/P3             │           │
│              └───────────┬───────────────────────┘           │
│                          │                                    │
│                          ▼                                    │
│              ┌───────────────────────────────────┐           │
│              │   ROUTING ENGINE                  │           │
│              │   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │           │
│              │   Match alert to team:            │           │
│              │   - Label: team=backend           │           │
│              │   - Service ownership             │           │
│              │   - On-call schedule              │           │
│              └───────────┬───────────────────────┘           │
│                          │                                    │
│                          ▼                                    │
│              ┌───────────────────────────────────┐           │
│              │   NOTIFICATION DISPATCHER         │           │
│              │   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │           │
│              │   Escalation policy:              │           │
│              │   - 0 min: Slack                  │           │
│              │   - 5 min: SMS (if not ack'd)     │           │
│              │   - 10 min: Phone call            │           │
│              │   - 15 min: Escalate to manager   │           │
│              └───────────────────────────────────┘           │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                 ON-CALL SCHEDULING                            │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Schedule (iCal format):                                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Week 1: Alice (primary), Bob (backup)                 │ │
│  │  Week 2: Bob (primary), Carol (backup)                 │ │
│  │  Week 3: Carol (primary), Alice (backup)               │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  Override:                                                   │
│  - Manual override (vacation, sick leave)                    │
│  - Shift swap between engineers                             │
└──────────────────────────────────────────────────────────────┘
```

---

## 💻 Implementation

### **1. Alert Deduplication**

```python
import hashlib
import json
from typing import Dict
from datetime import datetime, timedelta

class AlertDeduplicator:
    """
    Deduplicate alerts based on fingerprint
    """
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.dedup_window = 3600  # 1 hour
    
    def process_alert(self, alert: Dict) -> Dict:
        """
        Process alert and deduplicate
        """
        
        # Generate fingerprint
        fingerprint = self._generate_fingerprint(alert)
        
        # Check if alert exists
        key = f"alert:{fingerprint}"
        existing = self.redis.get(key)
        
        if existing:
            # Update existing
            existing_alert = json.loads(existing)
            existing_alert['count'] += 1
            existing_alert['last_seen'] = datetime.now().isoformat()
            
            self.redis.setex(key, self.dedup_window, json.dumps(existing_alert))
            
            return {
                'action': 'updated',
                'alert': existing_alert
            }
        else:
            # New alert
            alert['count'] = 1
            alert['first_seen'] = datetime.now().isoformat()
            alert['last_seen'] = datetime.now().isoformat()
            alert['fingerprint'] = fingerprint
            
            self.redis.setex(key, self.dedup_window, json.dumps(alert))
            
            return {
                'action': 'created',
                'alert': alert
            }
    
    def _generate_fingerprint(self, alert: Dict) -> str:
        """
        Generate unique fingerprint from alert labels
        """
        
        # Sort labels for consistent hash
        labels = alert.get('labels', {})
        sorted_labels = sorted(labels.items())
        
        # Hash
        fingerprint_str = json.dumps(sorted_labels, sort_keys=True)
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()[:16]


### **2. Alert Correlation**

```python
from collections import defaultdict
from datetime import datetime, timedelta

class AlertCorrelator:
    """
    Correlate related alerts using dependency graph
    """
    
    def __init__(self, dependency_graph):
        self.graph = dependency_graph
        self.correlation_window = 300  # 5 minutes
    
    def correlate(self, alerts: list) -> list:
        """
        Group correlated alerts
        """
        
        # Group by time window
        time_groups = self._group_by_time(alerts)
        
        correlated = []
        
        for group in time_groups:
            # Find root cause
            root_cause = self._find_root_cause(group)
            
            if root_cause:
                # Create incident
                incident = {
                    'root_cause': root_cause,
                    'related_alerts': group,
                    'affected_services': self._get_affected_services(group),
                    'severity': max(a['severity'] for a in group)
                }
                correlated.append(incident)
            else:
                # No correlation, treat independently
                correlated.extend(group)
        
        return correlated
    
    def _group_by_time(self, alerts: list) -> list:
        """
        Group alerts by time proximity
        """
        
        if not alerts:
            return []
        
        # Sort by timestamp
        sorted_alerts = sorted(alerts, key=lambda a: a['timestamp'])
        
        groups = []
        current_group = [sorted_alerts[0]]
        
        for alert in sorted_alerts[1:]:
            last_alert = current_group[-1]
            
            # Check time difference
            if (alert['timestamp'] - last_alert['timestamp']) < self.correlation_window:
                current_group.append(alert)
            else:
                groups.append(current_group)
                current_group = [alert]
        
        groups.append(current_group)
        return groups
    
    def _find_root_cause(self, alerts: list) -> dict:
        """
        Find root cause using dependency graph
        
        Example:
        Database → API → Frontend
        If database fails, API and Frontend fail too
        Root cause: Database
        """
        
        services = {a['service'] for a in alerts}
        
        # Find service with no dependencies (leaf node)
        for service in services:
            dependencies = self.graph.get_dependencies(service)
            
            if not dependencies or all(dep in services for dep in dependencies):
                # This is likely the root cause
                return next(a for a in alerts if a['service'] == service)
        
        return None


### **3. Escalation Policy Engine**

```python
import time
from enum import Enum

class EscalationLevel(Enum):
    L1 = 1  # Primary on-call
    L2 = 2  # Backup on-call
    L3 = 3  # Manager
    L4 = 4  # Director

class EscalationPolicy:
    """
    Escalate alerts based on time and acknowledgment
    """
    
    def __init__(self, schedule_service, notification_service):
        self.schedule = schedule_service
        self.notifier = notification_service
    
    def escalate(self, alert: dict):
        """
        Execute escalation policy
        """
        
        policy = [
            {'level': EscalationLevel.L1, 'delay': 0, 'channel': 'slack'},
            {'level': EscalationLevel.L1, 'delay': 300, 'channel': 'sms'},
            {'level': EscalationLevel.L1, 'delay': 600, 'channel': 'phone'},
            {'level': EscalationLevel.L2, 'delay': 900, 'channel': 'phone'},
            {'level': EscalationLevel.L3, 'delay': 1800, 'channel': 'phone'}
        ]
        
        alert_id = alert['id']
        
        for step in policy:
            # Wait for delay
            time.sleep(step['delay'])
            
            # Check if alert was acknowledged
            if self._is_acknowledged(alert_id):
                print(f"Alert {alert_id} acknowledged, stopping escalation")
                return
            
            # Get on-call person
            on_call = self.schedule.get_on_call(
                team=alert['team'],
                level=step['level']
            )
            
            # Send notification
            self.notifier.send(
                recipient=on_call,
                channel=step['channel'],
                message=alert['message']
            )
            
            print(f"Escalated to {on_call} via {step['channel']}")
    
    def _is_acknowledged(self, alert_id: str) -> bool:
        """
        Check if alert was acknowledged
        """
        # Query database
        result = db.query(
            "SELECT status FROM alerts WHERE id = ?",
            (alert_id,)
        )
        return result[0]['status'] == 'acknowledged' if result else False


### **4. ML-Based Severity Scoring**

```python
import xgboost as xgb
import numpy as np

class SeverityScorer:
    """
    ML model to predict alert severity
    """
    
    def __init__(self, model_path: str):
        self.model = xgb.Booster()
        self.model.load_model(model_path)
    
    def predict_severity(self, alert: dict) -> str:
        """
        Predict severity: P0/P1/P2/P3
        """
        
        # Extract features
        features = self._extract_features(alert)
        
        # Convert to DMatrix
        dmatrix = xgb.DMatrix(np.array([features]))
        
        # Predict
        probs = self.model.predict(dmatrix)[0]
        
        # Map to severity
        severities = ['P0', 'P1', 'P2', 'P3']
        predicted = severities[np.argmax(probs)]
        
        return predicted
    
    def _extract_features(self, alert: dict) -> list:
        """
        Extract features for ML model
        """
        
        # Historical alert rate
        alert_rate = self._get_alert_rate(alert['service'])
        
        # Error rate spike
        error_spike = self._get_error_spike(alert['service'])
        
        # Affected users
        affected_users = alert.get('affected_users', 0)
        
        # Service criticality
        criticality = self._get_service_criticality(alert['service'])
        
        # Time of day (higher severity during business hours)
        hour = datetime.now().hour
        is_business_hours = 1 if 9 <= hour <= 17 else 0
        
        return [
            alert_rate,
            error_spike,
            affected_users,
            criticality,
            is_business_hours
        ]


### **5. On-Call Scheduler**

```python
from datetime import datetime, timedelta

class OnCallScheduler:
    """
    Manage on-call rotations
    """
    
    def __init__(self, db):
        self.db = db
    
    def get_on_call(self, team: str, level: EscalationLevel) -> str:
        """
        Get current on-call person
        """
        
        now = datetime.now()
        
        # Query schedule
        result = self.db.query("""
            SELECT user_id
            FROM on_call_schedule
            WHERE team = ?
            AND level = ?
            AND start_time <= ?
            AND end_time >= ?
            ORDER BY priority ASC
            LIMIT 1
        """, (team, level.value, now, now))
        
        if result:
            return result[0]['user_id']
        else:
            # Fallback to manager
            return self._get_team_manager(team)
    
    def create_rotation(self, team: str, members: list, rotation_days: int = 7):
        """
        Create rotating schedule
        """
        
        start_date = datetime.now()
        
        for i, member in enumerate(members):
            start_time = start_date + timedelta(days=i * rotation_days)
            end_time = start_time + timedelta(days=rotation_days)
            
            self.db.execute("""
                INSERT INTO on_call_schedule
                (team, user_id, level, start_time, end_time)
                VALUES (?, ?, ?, ?, ?)
            """, (team, member, EscalationLevel.L1.value, start_time, end_time))


### **6. Alert Storm Detection**

```python
class AlertStormDetector:
    """
    Detect and handle alert storms
    """
    
    def __init__(self, threshold: int = 100):
        self.threshold = threshold  # alerts per minute
        self.window = 60  # seconds
    
    def is_storm(self, alerts: list) -> bool:
        """
        Check if current rate exceeds threshold
        """
        
        now = time.time()
        recent_alerts = [
            a for a in alerts
            if (now - a['timestamp']) < self.window
        ]
        
        rate = len(recent_alerts) / (self.window / 60)
        
        return rate > self.threshold
    
    def handle_storm(self, alerts: list):
        """
        Aggregate alerts during storm
        """
        
        # Group by service
        by_service = defaultdict(list)
        for alert in alerts:
            by_service[alert['service']].append(alert)
        
        # Create summary alert
        summary = {
            'type': 'alert_storm',
            'affected_services': list(by_service.keys()),
            'total_alerts': len(alerts),
            'breakdown': {
                service: len(alerts)
                for service, alerts in by_service.items()
            }
        }
        
        return summary
```

---

## 🎓 Interview Points

**Capacity:**
```
Alerts: 1M/day = 11.6/sec
Peak (incident): 1000/sec

Deduplication: 90% reduction
Correlated incidents: 100/day
```

**Key challenges:** Deduplication, correlation, escalation, ML severity scoring, on-call management!
