# Design Notification System (Multi-Channel) - Complete System Design

**Difficulty:** ⭐⭐⭐⭐  
**Interview Frequency:** High (All tech companies, 40 LPA+)  
**Time to Complete:** 35-40 minutes  
**Real-World Examples:** Airbnb Notifications, Uber Alerts, Amazon Order Updates

---

## 📋 Problem Statement

**Design a notification system that can:**
- Send 1 billion notifications daily across channels (push, email, SMS, in-app)
- Support user preferences (opt-in/opt-out per channel)
- Handle priority levels (critical, high, normal, low)
- Prevent notification fatigue (rate limiting, batching)
- Support template management
- Track delivery status and analytics
- Handle failures and retries
- Support A/B testing for notification content
- Provide real-time notifications (WebSocket)
- Scale globally

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│            NOTIFICATION GENERATION PIPELINE                   │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Trigger Sources:                                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   User      │  │  System     │  │  Scheduled  │         │
│  │   Actions   │  │  Events     │  │  Campaigns  │         │
│  │ (follow,    │  │ (payment    │  │ (marketing) │         │
│  │  comment)   │  │  success)   │  │             │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                  │
│         └────────────────┼────────────────┘                  │
│                          ▼                                    │
│              ┌───────────────────────┐                       │
│              │  NOTIFICATION SERVICE │                       │
│              │  ━━━━━━━━━━━━━━━━━━━  │                       │
│              │                       │                       │
│              │  1. Event validation  │                       │
│              │  2. User lookup       │                       │
│              │  3. Preference check  │                       │
│              │  4. Rate limiting     │                       │
│              │  5. Template render   │                       │
│              │  6. Queue for send    │                       │
│              └───────────┬───────────┘                       │
│                          │                                    │
│                          ▼                                    │
│              ┌───────────────────────┐                       │
│              │   KAFKA (Fan-out)     │                       │
│              └───────────┬───────────┘                       │
│                          │                                    │
│       ┌──────────────────┼──────────────────┐               │
│       │                  │                  │                │
│       ▼                  ▼                  ▼                │
│  ┌─────────┐      ┌──────────┐      ┌──────────┐           │
│  │  Push   │      │  Email   │      │   SMS    │           │
│  │ Sender  │      │ Sender   │      │ Sender   │           │
│  └─────────┘      └──────────┘      └──────────┘           │
│       │                  │                  │                │
│       ▼                  ▼                  ▼                │
│  ┌─────────┐      ┌──────────┐      ┌──────────┐           │
│  │  FCM/   │      │ SendGrid │      │  Twilio  │           │
│  │  APNS   │      │          │      │          │           │
│  └─────────┘      └──────────┘      └──────────┘           │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│               NOTIFICATION PROCESSING                         │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  PREFERENCE ENGINE                                     │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  User Preferences (PostgreSQL):                       │ │
│  │  ┌───────────────────────────────────────────────┐   │ │
│  │  │ user_id | channel | notification_type | enabled│   │ │
│  │  ├───────────────────────────────────────────────┤   │ │
│  │  │ u123    | push    | order_update     | true   │   │ │
│  │  │ u123    | email   | order_update     | true   │   │ │
│  │  │ u123    | sms     | order_update     | false  │   │ │
│  │  │ u123    | push    | marketing        | false  │   │ │
│  │  └───────────────────────────────────────────────┘   │ │
│  │                                                        │ │
│  │  Logic:                                                │ │
│  │  - Skip if user opted out                             │ │
│  │  - Respect quiet hours (9 PM - 8 AM)                  │ │
│  │  - Honor do-not-disturb mode                          │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  RATE LIMITER (Anti-Spam)                             │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  Rules:                                                │ │
│  │  - Max 10 push notifications per hour                 │ │
│  │  - Max 5 emails per day                               │ │
│  │  - Max 3 SMS per day                                  │ │
│  │  - Batch similar notifications (5-minute window)      │ │
│  │                                                        │ │
│  │  Example Batching:                                     │ │
│  │  "Alice liked your post" +                            │ │
│  │  "Bob liked your post" +                              │ │
│  │  "Carol liked your post"                              │ │
│  │  → "Alice, Bob, and Carol liked your post"           │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  TEMPLATE ENGINE                                       │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                        │ │
│  │  Template (Jinja2):                                    │ │
│  │  ┌──────────────────────────────────────────────────┐│ │
│  │  │ Subject: Order {{order_id}} confirmed            ││ │
│  │  │                                                   ││ │
│  │  │ Hi {{user_name}},                                ││ │
│  │  │                                                   ││ │
│  │  │ Your order #{{order_id}} has been confirmed!    ││ │
│  │  │ Total: ${{total_amount}}                         ││ │
│  │  │                                                   ││ │
│  │  │ {% if delivery_date %}                           ││ │
│  │  │ Estimated delivery: {{delivery_date}}            ││ │
│  │  │ {% endif %}                                       ││ │
│  │  └──────────────────────────────────────────────────┘│ │
│  │                                                        │ │
│  │  Rendered:                                             │ │
│  │  "Hi John, Your order #12345 has been confirmed!"    │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                 DELIVERY & TRACKING                           │
├──────────────────────────────────────────────────────────────┤
│  States: PENDING → SENT → DELIVERED → READ                  │
│                                                               │
│  Storage (Cassandra):                                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ notification_id | user_id | status    | timestamp    │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ n123           | u456    | delivered | 2024-01-15..  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  Retry Logic:                                                │
│  - Failed delivery → Retry after 1min, 5min, 15min          │
│  - Max 3 retries                                             │
│  - Dead letter queue for permanent failures                 │
└──────────────────────────────────────────────────────────────┘
```

---

## 💻 Implementation

### **1. Notification Service**

```python
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List
import json

class NotificationChannel(Enum):
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"
    WEBHOOK = "webhook"

class Priority(Enum):
    CRITICAL = 4  # Immediate delivery
    HIGH = 3
    NORMAL = 2
    LOW = 1

@dataclass
class Notification:
    user_id: str
    notification_type: str
    title: str
    body: str
    data: Dict
    priority: Priority
    channels: List[NotificationChannel]

class NotificationService:
    """
    Orchestrate notification delivery
    """
    
    def __init__(self, kafka_producer, preference_service, template_engine):
        self.kafka = kafka_producer
        self.preferences = preference_service
        self.templates = template_engine
    
    def send(self, notification: Notification):
        """
        Send notification through appropriate channels
        """
        
        # 1. Check user preferences
        enabled_channels = self.preferences.get_enabled_channels(
            notification.user_id,
            notification.notification_type
        )
        
        # Filter channels
        channels_to_send = [
            ch for ch in notification.channels
            if ch in enabled_channels
        ]
        
        if not channels_to_send:
            print(f"User {notification.user_id} opted out of {notification.notification_type}")
            return
        
        # 2. Rate limiting check
        if not self._check_rate_limit(notification.user_id, channels_to_send):
            # Batch for later
            self._add_to_batch(notification)
            return
        
        # 3. Render templates for each channel
        for channel in channels_to_send:
            rendered = self.templates.render(
                channel=channel,
                template_name=notification.notification_type,
                data=notification.data
            )
            
            # 4. Queue for delivery
            self._queue_for_delivery(
                channel=channel,
                user_id=notification.user_id,
                content=rendered,
                priority=notification.priority
            )
    
    def _queue_for_delivery(self, channel, user_id, content, priority):
        """
        Send to Kafka topic based on channel and priority
        """
        
        # Topic naming: notifications_{channel}_{priority}
        topic = f"notifications_{channel.value}_{priority.name.lower()}"
        
        message = {
            'user_id': user_id,
            'content': content,
            'timestamp': int(time.time() * 1000),
            'priority': priority.value
        }
        
        self.kafka.send(topic, json.dumps(message).encode())


### **2. Push Notification Sender**

```python
from pyfcm import FCMNotification
import apns2

class PushNotificationSender:
    """
    Send push notifications via FCM (Android) and APNS (iOS)
    """
    
    def __init__(self, fcm_api_key, apns_cert_path):
        self.fcm = FCMNotification(api_key=fcm_api_key)
        self.apns = apns2.APNsClient(
            credentials=apns_cert_path,
            use_sandbox=False
        )
    
    def send(self, user_id: str, title: str, body: str, data: Dict):
        """
        Send push notification
        """
        
        # Get device tokens from database
        devices = self._get_user_devices(user_id)
        
        for device in devices:
            if device['platform'] == 'android':
                self._send_fcm(device['token'], title, body, data)
            elif device['platform'] == 'ios':
                self._send_apns(device['token'], title, body, data)
    
    def _send_fcm(self, token: str, title: str, body: str, data: Dict):
        """Send via Firebase Cloud Messaging"""
        
        try:
            result = self.fcm.notify_single_device(
                registration_id=token,
                message_title=title,
                message_body=body,
                data_message=data,
                time_to_live=86400  # 24 hours
            )
            
            if result['success']:
                print(f"FCM sent successfully to {token}")
            else:
                print(f"FCM failed: {result}")
        
        except Exception as e:
            print(f"FCM error: {e}")
            # Queue for retry
            self._queue_retry(token, title, body, data)
    
    def _send_apns(self, token: str, title: str, body: str, data: Dict):
        """Send via Apple Push Notification Service"""
        
        from apns2.payload import Payload
        
        payload = Payload(
            alert={'title': title, 'body': body},
            sound='default',
            badge=1,
            custom=data
        )
        
        try:
            self.apns.send_notification(token, payload)
            print(f"APNS sent successfully to {token}")
        
        except Exception as e:
            print(f"APNS error: {e}")
            self._queue_retry(token, title, body, data)


### **3. Email Sender (SendGrid)**

```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class EmailSender:
    """
    Send emails via SendGrid
    """
    
    def __init__(self, sendgrid_api_key):
        self.sg = SendGridAPIClient(sendgrid_api_key)
    
    def send(self, to_email: str, subject: str, html_content: str):
        """
        Send email
        """
        
        message = Mail(
            from_email='noreply@example.com',
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        
        try:
            response = self.sg.send(message)
            print(f"Email sent: {response.status_code}")
            
            return response.status_code == 202
        
        except Exception as e:
            print(f"Email error: {e}")
            return False


### **4. Notification Batching**

```python
from collections import defaultdict
from datetime import datetime, timedelta

class NotificationBatcher:
    """
    Batch similar notifications to reduce spam
    """
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.batch_window = 300  # 5 minutes
    
    def add_to_batch(self, user_id: str, notification_type: str, data: Dict):
        """
        Add notification to batch
        """
        
        batch_key = f"batch:{user_id}:{notification_type}"
        
        # Add to list
        self.redis.rpush(batch_key, json.dumps(data))
        
        # Set expiry if first item
        if self.redis.llen(batch_key) == 1:
            self.redis.expire(batch_key, self.batch_window)
    
    def process_batches(self):
        """
        Process expired batches (cron job every minute)
        """
        
        # Scan for batch keys
        for key in self.redis.scan_iter("batch:*"):
            # Check if expired (ready to send)
            ttl = self.redis.ttl(key)
            
            if ttl <= 0:
                # Get all items
                items = self.redis.lrange(key, 0, -1)
                
                if items:
                    # Aggregate
                    aggregated = self._aggregate_notifications(items)
                    
                    # Send batched notification
                    self._send_batched(key, aggregated)
                    
                    # Delete batch
                    self.redis.delete(key)
    
    def _aggregate_notifications(self, items: List[str]) -> Dict:
        """
        Aggregate multiple notifications into one
        
        Example:
        ["Alice liked your post", "Bob liked your post"]
        → "Alice and Bob liked your post"
        """
        
        count = len(items)
        
        if count == 1:
            return json.loads(items[0])
        
        # Parse first item
        first = json.loads(items[0])
        
        # Aggregate message
        if count == 2:
            second = json.loads(items[1])
            message = f"{first['actor']} and {second['actor']} {first['action']}"
        else:
            message = f"{first['actor']} and {count-1} others {first['action']}"
        
        return {
            'message': message,
            'count': count,
            'actors': [json.loads(item)['actor'] for item in items]
        }
```

---

## 🎓 Interview Points

**Capacity:**
```
Notifications: 1B/day = 11,574/sec
Channels: 40% push, 40% email, 20% SMS
Peak QPS: 50K/sec

Kafka: 50K msg/sec × 1KB = 50 MB/sec
Storage: 1B × 500 bytes × 30 days = 15 TB
```

**Key challenges:** Rate limiting, batching, multi-channel delivery, retry logic!
