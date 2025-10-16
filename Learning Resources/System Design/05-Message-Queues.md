# Message Queues - From Pub/Sub to Event Streaming

**Mastery Level:** Critical for Staff+ Data Engineers  
**Interview Weight:** 30-40% of system design interviews  
**Time to Master:** 2-3 weeks  
**Difficulty:** ⭐⭐⭐⭐⭐

---

## 🎯 Why Message Queue Mastery Matters

At **40+ LPA level**, message queues enable:
- **Decoupling services** for independent scaling
- **Handling traffic spikes** with buffering
- **Event-driven architectures** for real-time systems
- **Reliable delivery** with at-least-once guarantees
- **Stream processing** for analytics pipelines

**Without proper queuing = fragile, tightly-coupled systems. With it = resilient, scalable architectures.**

---

## 📨 Message Queue Patterns & Use Cases

### **1. Point-to-Point Queues**
```
[Producer] → [Queue] → [Consumer]
```
**Use Cases:** Task processing, order fulfillment, batch jobs

### **2. Publish-Subscribe**
```
[Publisher] → [Topic] → [Subscriber 1]
                    → [Subscriber 2]
                    → [Subscriber 3]
```
**Use Cases:** Event notifications, real-time updates, fan-out processing

### **3. Request-Reply**
```
[Client] → [Request Queue] → [Service]
      ← [Reply Queue] ←
```
**Use Cases:** RPC over messaging, microservice communication

### **4. Event Streaming**
```
[Producer] → [Partitioned Log] → [Consumer Group 1]
                              → [Consumer Group 2]
```
**Use Cases:** Data pipelines, event sourcing, real-time analytics

---

## 🛠️ Core Message Queue Technologies

### **Apache Kafka - Event Streaming Platform**

**Best For:** High-throughput event streaming, data pipelines, real-time analytics

#### **Kafka Architecture Deep Dive:**

```python
class KafkaArchitecture:
    def __init__(self):
        self.brokers = 3  # Minimum for production
        self.partitions_per_topic = 12  # Should be multiple of broker count
        self.replication_factor = 3  # For fault tolerance
        self.retention_period = "7d"  # Keep messages for 7 days
    
    def kafka_cluster_design(self):
        """Design Kafka cluster for high throughput"""
        
        cluster_config = {
            'broker_config': {
                'num.network.threads': 8,          # Network threads
                'num.io.threads': 16,              # Disk I/O threads
                'socket.send.buffer.bytes': 102400, # 100KB send buffer
                'socket.receive.buffer.bytes': 102400, # 100KB receive buffer
                'socket.request.max.bytes': 104857600, # 100MB max request
                'log.segment.bytes': 1073741824,   # 1GB log segments
                'log.retention.hours': 168,        # 7 days retention
                'log.retention.bytes': 1073741824, # 1GB per partition max
                'compression.type': 'lz4',         # Fast compression
                'batch.size': 16384,               # 16KB batch size
                'linger.ms': 5                     # 5ms batching delay
            },
            
            'topic_config': {
                'cleanup.policy': 'delete',        # Delete old messages
                'compression.type': 'lz4',
                'max.message.bytes': 1048576,      # 1MB max message
                'min.insync.replicas': 2,          # Min replicas for ack
                'unclean.leader.election.enable': False  # Prevent data loss
            }
        }
        
        return cluster_config
    
    def partition_strategy(self, topic_name: str, expected_throughput_mb_s: int):
        """Calculate optimal partitioning strategy"""
        
        # Rule of thumb: 1 partition can handle ~10MB/s
        min_partitions = max(1, expected_throughput_mb_s // 10)
        
        # Align with broker count for even distribution
        partitions = ((min_partitions + self.brokers - 1) // self.brokers) * self.brokers
        
        strategy = {
            'topic': topic_name,
            'partitions': partitions,
            'replication_factor': self.replication_factor,
            'reasoning': f'Target throughput: {expected_throughput_mb_s}MB/s, '
                        f'Partitions needed: {min_partitions}, '
                        f'Aligned to brokers: {partitions}'
        }
        
        return strategy

# Example: E-commerce event streaming
class EcommerceEventStreaming:
    def __init__(self):
        self.kafka_client = KafkaProducer(
            bootstrap_servers=['kafka1:9092', 'kafka2:9092', 'kafka3:9092'],
            value_serializer=lambda v: json.dumps(v).encode(),
            acks='all',           # Wait for all replicas
            retries=3,            # Retry failed sends
            batch_size=16384,     # 16KB batches
            linger_ms=5,          # 5ms batching delay
            compression_type='lz4'
        )
    
    def publish_order_event(self, order_data):
        """Publish order event with proper partitioning"""
        
        # Partition by customer_id for ordered processing per customer
        partition_key = str(order_data['customer_id'])
        
        event = {
            'event_type': 'order_created',
            'timestamp': time.time(),
            'order_id': order_data['order_id'],
            'customer_id': order_data['customer_id'],
            'total_amount': order_data['total_amount'],
            'items': order_data['items']
        }
        
        # Send to appropriate partition
        future = self.kafka_client.send(
            topic='orders',
            key=partition_key.encode(),
            value=event
        )
        
        # Handle success/failure
        try:
            record_metadata = future.get(timeout=10)
            print(f"Message sent to {record_metadata.topic} "
                  f"partition {record_metadata.partition} "
                  f"offset {record_metadata.offset}")
        except KafkaError as e:
            print(f"Failed to send message: {e}")
    
    def setup_consumer_group(self, group_id: str, topics: List[str]):
        """Setup consumer group with proper configuration"""
        
        consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=['kafka1:9092', 'kafka2:9092', 'kafka3:9092'],
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode()),
            auto_offset_reset='earliest',    # Start from beginning if no offset
            enable_auto_commit=False,        # Manual commit for reliability
            max_poll_records=100,           # Process 100 messages at a time
            session_timeout_ms=30000,       # 30 second session timeout
            heartbeat_interval_ms=3000      # 3 second heartbeat
        )
        
        return consumer
    
    def process_orders(self):
        """Example consumer processing orders"""
        
        consumer = self.setup_consumer_group('order-processor', ['orders'])
        
        try:
            for message in consumer:
                try:
                    # Process the order
                    order_event = message.value
                    self.process_single_order(order_event)
                    
                    # Commit offset after successful processing
                    consumer.commit()
                    
                except Exception as e:
                    print(f"Error processing order {order_event.get('order_id')}: {e}")
                    # Don't commit - message will be reprocessed
                    
        except KeyboardInterrupt:
            print("Shutting down consumer...")
        finally:
            consumer.close()
    
    def process_single_order(self, order_event):
        """Process individual order event"""
        
        # Update inventory
        for item in order_event['items']:
            self.update_inventory(item['product_id'], -item['quantity'])
        
        # Send confirmation email
        self.send_order_confirmation(order_event['customer_id'], order_event['order_id'])
        
        # Update customer analytics
        self.update_customer_metrics(order_event['customer_id'], order_event['total_amount'])
```

#### **Kafka Advanced Patterns:**

```python
class KafkaAdvancedPatterns:
    def exactly_once_processing(self):
        """Implement exactly-once semantics in Kafka"""
        
        # Producer configuration for exactly-once
        producer_config = {
            'bootstrap.servers': 'kafka1:9092,kafka2:9092,kafka3:9092',
            'transactional.id': 'unique-producer-id',  # Enables transactions
            'enable.idempotence': True,                # Prevents duplicates
            'acks': 'all',                            # Wait for all replicas
            'retries': 2147483647,                    # Retry indefinitely
            'max.in.flight.requests.per.connection': 5,
            'compression.type': 'lz4'
        }
        
        producer = KafkaProducer(**producer_config)
        
        # Initialize transactions
        producer.init_transactions()
        
        try:
            # Begin transaction
            producer.begin_transaction()
            
            # Send messages atomically
            producer.send('topic1', key='key1', value='message1')
            producer.send('topic2', key='key2', value='message2')
            
            # Commit transaction
            producer.commit_transaction()
            
        except Exception as e:
            # Abort on any error
            producer.abort_transaction()
            raise e
        
        finally:
            producer.close()
    
    def dead_letter_queue_pattern(self):
        """Implement dead letter queue for failed messages"""
        
        class DeadLetterProcessor:
            def __init__(self):
                self.producer = KafkaProducer(
                    bootstrap_servers=['kafka1:9092'],
                    value_serializer=lambda v: json.dumps(v).encode()
                )
                self.max_retries = 3
            
            def process_with_dlq(self, message, processor_func):
                """Process message with dead letter queue fallback"""
                
                retry_count = message.get('retry_count', 0)
                
                try:
                    # Attempt to process message
                    result = processor_func(message)
                    return result
                    
                except Exception as e:
                    if retry_count < self.max_retries:
                        # Increment retry count and republish
                        message['retry_count'] = retry_count + 1
                        message['last_error'] = str(e)
                        message['retry_timestamp'] = time.time()
                        
                        # Send back to original topic with delay
                        self.producer.send('original-topic', value=message)
                        
                    else:
                        # Send to dead letter queue
                        dlq_message = {
                            'original_message': message,
                            'final_error': str(e),
                            'failed_timestamp': time.time(),
                            'total_retries': retry_count
                        }
                        
                        self.producer.send('dead-letter-queue', value=dlq_message)
                        print(f"Message sent to DLQ after {retry_count} retries")
    
    def consumer_group_rebalancing(self):
        """Handle consumer group rebalancing gracefully"""
        
        class RebalanceListener(ConsumerRebalanceListener):
            def __init__(self, consumer):
                self.consumer = consumer
                self.current_partitions = set()
            
            def on_partitions_revoked(self, revoked):
                """Called before rebalancing"""
                print(f"Partitions revoked: {revoked}")
                
                # Commit any pending offsets
                self.consumer.commit()
                
                # Clean up resources for revoked partitions
                for partition in revoked:
                    self.cleanup_partition_resources(partition)
            
            def on_partitions_assigned(self, assigned):
                """Called after rebalancing"""
                print(f"Partitions assigned: {assigned}")
                
                # Initialize resources for new partitions
                for partition in assigned:
                    self.initialize_partition_resources(partition)
                
                self.current_partitions = set(assigned)
            
            def cleanup_partition_resources(self, partition):
                # Close database connections, flush caches, etc.
                pass
            
            def initialize_partition_resources(self, partition):
                # Setup database connections, load caches, etc.
                pass
        
        # Consumer with rebalance listener
        consumer = KafkaConsumer(
            'my-topic',
            group_id='my-consumer-group',
            bootstrap_servers=['kafka1:9092']
        )
        
        listener = RebalanceListener(consumer)
        consumer.subscribe(['my-topic'], listener=listener)
```

---

### **RabbitMQ - Traditional Message Broker**

**Best For:** Complex routing, reliable delivery, lower throughput scenarios

#### **RabbitMQ Patterns:**

```python
import pika
import json
from typing import Callable

class RabbitMQPatterns:
    def __init__(self, connection_url='amqp://localhost'):
        self.connection = pika.BlockingConnection(pika.URLParameters(connection_url))
        self.channel = self.connection.channel()
    
    def work_queue_pattern(self, queue_name: str, task_processor: Callable):
        """Implement work queue for task distribution"""
        
        # Declare durable queue
        self.channel.queue_declare(queue=queue_name, durable=True)
        
        # Fair dispatch - don't give worker more than 1 task at a time
        self.channel.basic_qos(prefetch_count=1)
        
        def callback(ch, method, properties, body):
            try:
                task_data = json.loads(body)
                print(f"Processing task: {task_data}")
                
                # Process the task
                result = task_processor(task_data)
                
                # Acknowledge completion
                ch.basic_ack(delivery_tag=method.delivery_tag)
                print(f"Task completed: {result}")
                
            except Exception as e:
                print(f"Task failed: {e}")
                # Reject and requeue
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        # Start consuming
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback)
        print(f"Waiting for tasks in {queue_name}. To exit press CTRL+C")
        self.channel.start_consuming()
    
    def publish_subscribe_pattern(self, exchange_name: str):
        """Implement pub/sub pattern with fanout exchange"""
        
        # Declare fanout exchange
        self.channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')
        
        def publish_message(message: dict):
            """Publish message to all subscribers"""
            self.channel.basic_publish(
                exchange=exchange_name,
                routing_key='',  # Ignored for fanout
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    timestamp=int(time.time())
                )
            )
        
        def subscribe(callback: Callable):
            """Subscribe to messages"""
            # Create temporary queue for this subscriber
            result = self.channel.queue_declare(queue='', exclusive=True)
            queue_name = result.method.queue
            
            # Bind queue to exchange
            self.channel.queue_bind(exchange=exchange_name, queue=queue_name)
            
            def wrapper(ch, method, properties, body):
                message = json.loads(body)
                callback(message)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            
            self.channel.basic_consume(queue=queue_name, on_message_callback=wrapper)
            return queue_name
        
        return publish_message, subscribe
    
    def topic_routing_pattern(self, exchange_name: str):
        """Implement topic-based routing"""
        
        # Declare topic exchange
        self.channel.exchange_declare(exchange=exchange_name, exchange_type='topic')
        
        def publish_to_topic(routing_key: str, message: dict):
            """Publish message with routing key"""
            self.channel.basic_publish(
                exchange=exchange_name,
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(delivery_mode=2)
            )
        
        def subscribe_to_pattern(pattern: str, callback: Callable):
            """Subscribe to routing pattern (e.g., 'orders.*', '*.critical')"""
            result = self.channel.queue_declare(queue='', exclusive=True)
            queue_name = result.method.queue
            
            # Bind with pattern
            self.channel.queue_bind(
                exchange=exchange_name,
                queue=queue_name,
                routing_key=pattern
            )
            
            def wrapper(ch, method, properties, body):
                message = json.loads(body)
                callback(message, method.routing_key)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            
            self.channel.basic_consume(queue=queue_name, on_message_callback=wrapper)
            return queue_name
        
        return publish_to_topic, subscribe_to_pattern
    
    def rpc_pattern(self):
        """Implement RPC over RabbitMQ"""
        
        class RPCServer:
            def __init__(self, channel, queue_name):
                self.channel = channel
                self.queue_name = queue_name
                self.channel.queue_declare(queue=queue_name)
                self.channel.basic_qos(prefetch_count=1)
            
            def register_function(self, func: Callable):
                """Register function to handle RPC calls"""
                
                def on_request(ch, method, props, body):
                    try:
                        request = json.loads(body)
                        result = func(request)
                        
                        # Send response back
                        ch.basic_publish(
                            exchange='',
                            routing_key=props.reply_to,
                            properties=pika.BasicProperties(
                                correlation_id=props.correlation_id
                            ),
                            body=json.dumps({'result': result, 'error': None})
                        )
                        
                    except Exception as e:
                        # Send error response
                        ch.basic_publish(
                            exchange='',
                            routing_key=props.reply_to,
                            properties=pika.BasicProperties(
                                correlation_id=props.correlation_id
                            ),
                            body=json.dumps({'result': None, 'error': str(e)})
                        )
                    
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                
                self.channel.basic_consume(
                    queue=self.queue_name,
                    on_message_callback=on_request
                )
            
            def start(self):
                print(f"RPC Server started on {self.queue_name}")
                self.channel.start_consuming()
        
        class RPCClient:
            def __init__(self, channel, server_queue):
                self.channel = channel
                self.server_queue = server_queue
                
                # Create callback queue for responses
                result = self.channel.queue_declare(queue='', exclusive=True)
                self.callback_queue = result.method.queue
                
                self.response = None
                self.correlation_id = None
                
                # Setup response handler
                self.channel.basic_consume(
                    queue=self.callback_queue,
                    on_message_callback=self.on_response,
                    auto_ack=True
                )
            
            def on_response(self, ch, method, props, body):
                if self.correlation_id == props.correlation_id:
                    self.response = json.loads(body)
            
            def call(self, request: dict) -> dict:
                """Make RPC call"""
                self.response = None
                self.correlation_id = str(uuid.uuid4())
                
                # Send request
                self.channel.basic_publish(
                    exchange='',
                    routing_key=self.server_queue,
                    properties=pika.BasicProperties(
                        reply_to=self.callback_queue,
                        correlation_id=self.correlation_id,
                    ),
                    body=json.dumps(request)
                )
                
                # Wait for response
                while self.response is None:
                    self.channel.connection.process_data_events()
                
                return self.response
        
        return RPCServer, RPCClient

# Example usage
rabbitmq = RabbitMQPatterns()

# Work queue for order processing
def process_order(task_data):
    order_id = task_data['order_id']
    # Process order logic here
    time.sleep(2)  # Simulate processing
    return f"Order {order_id} processed"

rabbitmq.work_queue_pattern('order_processing', process_order)
```

---

### **Amazon SQS/SNS - Managed Queuing**

**Best For:** AWS ecosystem, serverless architectures, managed infrastructure

```python
import boto3
import json
from typing import Dict, List

class AWSMessaging:
    def __init__(self):
        self.sqs = boto3.client('sqs')
        self.sns = boto3.client('sns')
    
    def setup_sqs_queue(self, queue_name: str, is_fifo: bool = False) -> str:
        """Create SQS queue with proper configuration"""
        
        queue_attributes = {
            'DelaySeconds': '0',
            'MaxReceiveCount': '3',  # Dead letter after 3 retries
            'MessageRetentionPeriod': '1209600',  # 14 days
            'ReceiveMessageWaitTimeSeconds': '20',  # Long polling
            'VisibilityTimeoutSeconds': '300'  # 5 minutes processing time
        }
        
        if is_fifo:
            queue_name += '.fifo'
            queue_attributes.update({
                'FifoQueue': 'true',
                'ContentBasedDeduplication': 'true'
            })
        
        response = self.sqs.create_queue(
            QueueName=queue_name,
            Attributes=queue_attributes
        )
        
        return response['QueueUrl']
    
    def setup_dead_letter_queue(self, main_queue_url: str, dlq_name: str) -> str:
        """Setup dead letter queue for failed messages"""
        
        # Create DLQ
        dlq_url = self.setup_sqs_queue(dlq_name)
        
        # Get DLQ ARN
        dlq_attributes = self.sqs.get_queue_attributes(
            QueueUrl=dlq_url,
            AttributeNames=['QueueArn']
        )
        dlq_arn = dlq_attributes['Attributes']['QueueArn']
        
        # Configure main queue to use DLQ
        redrive_policy = {
            'deadLetterTargetArn': dlq_arn,
            'maxReceiveCount': 3
        }
        
        self.sqs.set_queue_attributes(
            QueueUrl=main_queue_url,
            Attributes={
                'RedrivePolicy': json.dumps(redrive_policy)
            }
        )
        
        return dlq_url
    
    def batch_send_messages(self, queue_url: str, messages: List[Dict]) -> Dict:
        """Send multiple messages efficiently"""
        
        entries = []
        for i, message in enumerate(messages):
            entry = {
                'Id': str(i),
                'MessageBody': json.dumps(message)
            }
            
            # Add attributes for FIFO queues
            if queue_url.endswith('.fifo'):
                entry['MessageGroupId'] = message.get('group_id', 'default')
                if 'deduplication_id' in message:
                    entry['MessageDeduplicationId'] = message['deduplication_id']
            
            entries.append(entry)
        
        # SQS batch limit is 10 messages
        results = []
        for i in range(0, len(entries), 10):
            batch = entries[i:i+10]
            response = self.sqs.send_message_batch(
                QueueUrl=queue_url,
                Entries=batch
            )
            results.append(response)
        
        return results
    
    def process_messages_efficiently(self, queue_url: str, processor_func, max_messages=10):
        """Efficiently process SQS messages"""
        
        while True:
            # Long poll for messages
            response = self.sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=20,  # Long polling
                MessageAttributeNames=['All']
            )
            
            messages = response.get('Messages', [])
            if not messages:
                continue
            
            # Process messages in parallel
            successful_deletes = []
            
            for message in messages:
                try:
                    body = json.loads(message['Body'])
                    result = processor_func(body)
                    
                    # Mark for deletion
                    successful_deletes.append({
                        'Id': message['MessageId'],
                        'ReceiptHandle': message['ReceiptHandle']
                    })
                    
                except Exception as e:
                    print(f"Failed to process message {message['MessageId']}: {e}")
                    # Message will become visible again after visibility timeout
            
            # Batch delete successful messages
            if successful_deletes:
                self.sqs.delete_message_batch(
                    QueueUrl=queue_url,
                    Entries=successful_deletes
                )
    
    def setup_sns_fanout(self, topic_name: str, queue_urls: List[str]) -> str:
        """Setup SNS topic with SQS subscriptions"""
        
        # Create SNS topic
        response = self.sns.create_topic(Name=topic_name)
        topic_arn = response['TopicArn']
        
        # Subscribe queues to topic
        for queue_url in queue_urls:
            # Get queue ARN
            queue_attributes = self.sqs.get_queue_attributes(
                QueueUrl=queue_url,
                AttributeNames=['QueueArn']
            )
            queue_arn = queue_attributes['Attributes']['QueueArn']
            
            # Subscribe queue to topic
            self.sns.subscribe(
                TopicArn=topic_arn,
                Protocol='sqs',
                Endpoint=queue_arn
            )
            
            # Allow SNS to write to SQS
            policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "sns.amazonaws.com"},
                    "Action": "sqs:SendMessage",
                    "Resource": queue_arn,
                    "Condition": {
                        "ArnEquals": {
                            "aws:SourceArn": topic_arn
                        }
                    }
                }]
            }
            
            self.sqs.set_queue_attributes(
                QueueUrl=queue_url,
                Attributes={'Policy': json.dumps(policy)}
            )
        
        return topic_arn

# Example: E-commerce order processing with AWS
class EcommerceAWSMessaging:
    def __init__(self):
        self.aws_messaging = AWSMessaging()
        self.setup_infrastructure()
    
    def setup_infrastructure(self):
        """Setup queues and topics for order processing"""
        
        # Main order queue
        self.order_queue = self.aws_messaging.setup_sqs_queue('order-processing')
        
        # Dead letter queue
        self.dlq = self.aws_messaging.setup_dead_letter_queue(
            self.order_queue, 'order-processing-dlq'
        )
        
        # Service-specific queues
        self.inventory_queue = self.aws_messaging.setup_sqs_queue('inventory-updates')
        self.email_queue = self.aws_messaging.setup_sqs_queue('email-notifications')
        self.analytics_queue = self.aws_messaging.setup_sqs_queue('analytics-events')
        
        # SNS topic for order events
        self.order_topic = self.aws_messaging.setup_sns_fanout(
            'order-events',
            [self.inventory_queue, self.email_queue, self.analytics_queue]
        )
    
    def process_order(self, order_data: Dict):
        """Process order and trigger downstream events"""
        
        # Send to main processing queue
        self.aws_messaging.sqs.send_message(
            QueueUrl=self.order_queue,
            MessageBody=json.dumps(order_data)
        )
        
        # Publish event to all subscribers
        event = {
            'event_type': 'order_created',
            'order_id': order_data['order_id'],
            'customer_id': order_data['customer_id'],
            'timestamp': time.time()
        }
        
        self.aws_messaging.sns.publish(
            TopicArn=self.order_topic,
            Message=json.dumps(event),
            Subject='Order Created'
        )
```

---

## 🔧 Advanced Message Queue Patterns

### **Event Sourcing with Message Queues**

```python
from typing import List, Dict, Any
from abc import ABC, abstractmethod

class Event:
    def __init__(self, event_type: str, aggregate_id: str, data: Dict[Any, Any]):
        self.event_type = event_type
        self.aggregate_id = aggregate_id
        self.data = data
        self.timestamp = time.time()
        self.version = 1

class EventStore:
    def __init__(self, message_queue):
        self.message_queue = message_queue
        self.events = {}  # In practice, this would be a database
    
    def append_events(self, aggregate_id: str, events: List[Event], expected_version: int):
        """Append events to the event store"""
        
        current_version = self.get_current_version(aggregate_id)
        
        if current_version != expected_version:
            raise Exception(f"Concurrency conflict: expected {expected_version}, got {current_version}")
        
        # Store events
        if aggregate_id not in self.events:
            self.events[aggregate_id] = []
        
        for event in events:
            event.version = current_version + 1
            self.events[aggregate_id].append(event)
            current_version += 1
            
            # Publish event to message queue
            self.message_queue.publish('events', {
                'event_type': event.event_type,
                'aggregate_id': event.aggregate_id,
                'data': event.data,
                'timestamp': event.timestamp,
                'version': event.version
            })
    
    def get_events(self, aggregate_id: str, from_version: int = 0) -> List[Event]:
        """Get events for an aggregate"""
        
        events = self.events.get(aggregate_id, [])
        return [e for e in events if e.version > from_version]
    
    def get_current_version(self, aggregate_id: str) -> int:
        """Get current version of aggregate"""
        
        events = self.events.get(aggregate_id, [])
        return len(events)

class OrderAggregate:
    def __init__(self, order_id: str):
        self.order_id = order_id
        self.status = 'pending'
        self.items = []
        self.total_amount = 0
        self.version = 0
        self.pending_events = []
    
    def create_order(self, customer_id: str, items: List[Dict]):
        """Create order command"""
        
        if self.status != 'pending':
            raise Exception("Order already created")
        
        # Calculate total
        total = sum(item['price'] * item['quantity'] for item in items)
        
        # Create event
        event = Event('order_created', self.order_id, {
            'customer_id': customer_id,
            'items': items,
            'total_amount': total
        })
        
        self.pending_events.append(event)
        
        # Apply event to update state
        self.apply_event(event)
    
    def confirm_payment(self, payment_id: str):
        """Confirm payment command"""
        
        if self.status != 'created':
            raise Exception("Cannot confirm payment for order in status: " + self.status)
        
        event = Event('payment_confirmed', self.order_id, {
            'payment_id': payment_id
        })
        
        self.pending_events.append(event)
        self.apply_event(event)
    
    def apply_event(self, event: Event):
        """Apply event to update aggregate state"""
        
        if event.event_type == 'order_created':
            self.status = 'created'
            self.items = event.data['items'] 
            self.total_amount = event.data['total_amount']
            
        elif event.event_type == 'payment_confirmed':
            self.status = 'paid'
        
        self.version += 1
    
    def get_pending_events(self) -> List[Event]:
        """Get events that haven't been saved yet"""
        
        events = self.pending_events
        self.pending_events = []
        return events

# Event-driven order service
class OrderService:
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
    
    def create_order(self, order_id: str, customer_id: str, items: List[Dict]):
        """Create order using event sourcing"""
        
        # Load aggregate from events
        order = self.load_aggregate(order_id)
        
        # Execute command
        order.create_order(customer_id, items)
        
        # Save events
        pending_events = order.get_pending_events()
        self.event_store.append_events(order_id, pending_events, order.version - len(pending_events))
    
    def load_aggregate(self, order_id: str) -> OrderAggregate:
        """Reconstruct aggregate from events"""
        
        order = OrderAggregate(order_id)
        events = self.event_store.get_events(order_id)
        
        for event in events:
            order.apply_event(event)
        
        return order
```

### **SAGA Pattern for Distributed Transactions**

```python
from enum import Enum
from typing import Callable, List, Dict

class SagaStepStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATED = "compensated"

class SagaStep:
    def __init__(self, name: str, action: Callable, compensation: Callable):
        self.name = name
        self.action = action
        self.compensation = compensation
        self.status = SagaStepStatus.PENDING
        self.result = None
        self.error = None

class SagaOrchestrator:
    def __init__(self, message_queue):
        self.message_queue = message_queue
        self.sagas = {}  # Store saga state
    
    def execute_saga(self, saga_id: str, steps: List[SagaStep]) -> bool:
        """Execute saga with compensation on failure"""
        
        self.sagas[saga_id] = {
            'steps': steps,
            'current_step': 0,
            'status': 'running'
        }
        
        completed_steps = []
        
        try:
            # Execute steps in order
            for i, step in enumerate(steps):
                print(f"Executing step {i}: {step.name}")
                
                try:
                    result = step.action()
                    step.status = SagaStepStatus.COMPLETED
                    step.result = result
                    completed_steps.append(step)
                    
                    # Publish step completed event
                    self.message_queue.publish('saga_events', {
                        'saga_id': saga_id,
                        'step_name': step.name,
                        'status': 'completed',
                        'result': result
                    })
                    
                except Exception as e:
                    step.status = SagaStepStatus.FAILED
                    step.error = str(e)
                    
                    print(f"Step {step.name} failed: {e}")
                    
                    # Compensate completed steps in reverse order
                    self.compensate_saga(saga_id, completed_steps)
                    
                    return False
            
            self.sagas[saga_id]['status'] = 'completed'
            print(f"Saga {saga_id} completed successfully")
            
            return True
            
        except Exception as e:
            print(f"Saga {saga_id} failed: {e}")
            self.compensate_saga(saga_id, completed_steps)
            return False
    
    def compensate_saga(self, saga_id: str, completed_steps: List[SagaStep]):
        """Compensate completed steps in reverse order"""
        
        print(f"Compensating saga {saga_id}")
        self.sagas[saga_id]['status'] = 'compensating'
        
        # Reverse order compensation
        for step in reversed(completed_steps):
            try:
                print(f"Compensating step: {step.name}")
                step.compensation()
                step.status = SagaStepStatus.COMPENSATED
                
                # Publish compensation event
                self.message_queue.publish('saga_events', {
                    'saga_id': saga_id,
                    'step_name': step.name,
                    'status': 'compensated'
                })
                
            except Exception as e:
                print(f"Compensation failed for {step.name}: {e}")
                # Log critical error - manual intervention needed
        
        self.sagas[saga_id]['status'] = 'compensated'

# Example: E-commerce order saga
class EcommerceOrderSaga:
    def __init__(self, message_queue):
        self.orchestrator = SagaOrchestrator(message_queue)
        self.inventory_service = InventoryService()
        self.payment_service = PaymentService()
        self.shipping_service = ShippingService()
    
    def process_order(self, order_data: Dict) -> bool:
        """Process order using saga pattern"""
        
        order_id = order_data['order_id']
        customer_id = order_data['customer_id']
        items = order_data['items']
        
        # Define saga steps
        steps = [
            SagaStep(
                name="reserve_inventory",
                action=lambda: self.inventory_service.reserve_items(items),
                compensation=lambda: self.inventory_service.release_items(items)
            ),
            
            SagaStep(
                name="charge_payment",
                action=lambda: self.payment_service.charge_customer(
                    customer_id, order_data['total_amount']
                ),
                compensation=lambda: self.payment_service.refund_customer(
                    customer_id, order_data['total_amount']
                )
            ),
            
            SagaStep(
                name="create_shipment",
                action=lambda: self.shipping_service.create_shipment(order_data),
                compensation=lambda: self.shipping_service.cancel_shipment(order_id)
            ),
            
            SagaStep(
                name="update_order_status",
                action=lambda: self.update_order_status(order_id, 'confirmed'),
                compensation=lambda: self.update_order_status(order_id, 'cancelled')
            )
        ]
        
        # Execute saga
        return self.orchestrator.execute_saga(f"order_{order_id}", steps)
    
    def update_order_status(self, order_id: str, status: str):
        # Update order in database
        print(f"Order {order_id} status updated to: {status}")
        return True

# Mock services
class InventoryService:
    def reserve_items(self, items):
        print(f"Reserving inventory for items: {items}")
        # Simulate potential failure
        if len(items) > 5:
            raise Exception("Not enough inventory")
        return {"reservation_id": "inv_123"}
    
    def release_items(self, items):
        print(f"Releasing inventory for items: {items}")

class PaymentService:
    def charge_customer(self, customer_id, amount):
        print(f"Charging customer {customer_id}: ${amount}")
        # Simulate payment processing
        return {"transaction_id": "pay_456"}
    
    def refund_customer(self, customer_id, amount):
        print(f"Refunding customer {customer_id}: ${amount}")

class ShippingService:
    def create_shipment(self, order_data):
        print(f"Creating shipment for order: {order_data['order_id']}")
        return {"shipment_id": "ship_789"}
    
    def cancel_shipment(self, order_id):
        print(f"Cancelling shipment for order: {order_id}")
```

---

## 📊 Message Queue Performance & Monitoring

### **Performance Optimization:**

```python
import time
from collections import defaultdict, deque
from typing import Dict, List

class MessageQueueMetrics:
    def __init__(self):
        self.metrics = {
            'messages_sent': 0,
            'messages_received': 0,
            'messages_failed': 0,
            'avg_processing_time': 0,
            'queue_depth': 0,
            'throughput_per_second': 0
        }
        
        self.processing_times = deque(maxlen=1000)  # Keep last 1000 times
        self.throughput_window = deque(maxlen=60)   # 1 minute window
        
    def record_message_sent(self):
        self.metrics['messages_sent'] += 1
        
    def record_message_received(self, processing_time_ms: float):
        self.metrics['messages_received'] += 1
        self.processing_times.append(processing_time_ms)
        
        # Update average processing time
        if self.processing_times:
            self.metrics['avg_processing_time'] = sum(self.processing_times) / len(self.processing_times)
        
        # Update throughput
        current_second = int(time.time())
        self.throughput_window.append(current_second)
        
        # Count messages in last minute
        recent_messages = sum(1 for ts in self.throughput_window if current_second - ts <= 60)
        self.metrics['throughput_per_second'] = recent_messages / 60
        
    def record_message_failed(self):
        self.metrics['messages_failed'] += 1
        
    def get_health_status(self) -> Dict[str, str]:
        """Get system health based on metrics"""
        
        status = {
            'overall': 'healthy',
            'issues': []
        }
        
        # Check processing time
        if self.metrics['avg_processing_time'] > 5000:  # 5 seconds
            status['issues'].append('High processing time')
            status['overall'] = 'degraded'
        
        # Check error rate
        total_messages = self.metrics['messages_received'] + self.metrics['messages_failed']
        if total_messages > 0:
            error_rate = self.metrics['messages_failed'] / total_messages
            if error_rate > 0.05:  # 5% error rate
                status['issues'].append('High error rate')
                status['overall'] = 'unhealthy'
        
        # Check queue depth (if available)
        if self.metrics['queue_depth'] > 10000:
            status['issues'].append('Queue backlog')
            status['overall'] = 'degraded'
        
        return status

class MessageQueueOptimizer:
    def __init__(self):
        self.batch_sizes = defaultdict(list)
        self.optimal_batch_size = 100
        
    def optimize_batch_size(self, queue_name: str, current_throughput: float, current_latency: float):
        """Dynamically optimize batch size based on performance"""
        
        # Record current performance
        self.batch_sizes[queue_name].append({
            'batch_size': self.optimal_batch_size,
            'throughput': current_throughput,
            'latency': current_latency,
            'timestamp': time.time()
        })
        
        # Keep only recent data points
        cutoff_time = time.time() - 300  # 5 minutes
        self.batch_sizes[queue_name] = [
            data for data in self.batch_sizes[queue_name]
            if data['timestamp'] > cutoff_time
        ]
        
        # Find optimal batch size
        if len(self.batch_sizes[queue_name]) >= 5:
            best_performance = max(
                self.batch_sizes[queue_name],
                key=lambda x: x['throughput'] / (1 + x['latency'])  # Throughput/latency ratio
            )
            
            # Adjust batch size
            if best_performance['throughput'] > current_throughput * 1.1:
                self.optimal_batch_size = best_performance['batch_size']
            elif current_latency > 1000:  # > 1 second
                self.optimal_batch_size = max(10, self.optimal_batch_size - 10)
            elif current_throughput < current_throughput * 0.9:
                self.optimal_batch_size = min(1000, self.optimal_batch_size + 10)
        
        return self.optimal_batch_size
    
    def auto_scale_consumers(self, queue_depth: int, current_consumers: int) -> int:
        """Auto-scale consumers based on queue depth"""
        
        target_consumers = current_consumers
        
        # Scale up if queue is backing up
        if queue_depth > 1000:  # 1000 messages backlog
            scale_factor = min(3, queue_depth // 1000)  # Scale up to 3x
            target_consumers = min(50, current_consumers * scale_factor)
        
        # Scale down if queue is empty
        elif queue_depth < 100 and current_consumers > 1:
            target_consumers = max(1, current_consumers // 2)
        
        return target_consumers

# Example: Kafka performance monitoring
class KafkaPerformanceMonitor:
    def __init__(self, kafka_client):
        self.kafka_client = kafka_client
        self.metrics = MessageQueueMetrics()
        self.optimizer = MessageQueueOptimizer()
    
    def monitor_producer_performance(self, topic: str):
        """Monitor Kafka producer performance"""
        
        # Get producer metrics from Kafka
        producer_metrics = self.kafka_client.metrics()
        
        relevant_metrics = {
            'record_send_rate': producer_metrics.get('producer-metrics', {}).get('record-send-rate', 0),
            'record_error_rate': producer_metrics.get('producer-metrics', {}).get('record-error-rate', 0),
            'request_latency_avg': producer_metrics.get('producer-metrics', {}).get('request-latency-avg', 0),
            'batch_size_avg': producer_metrics.get('producer-metrics', {}).get('batch-size-avg', 0)
        }
        
        # Optimize batch size
        optimal_batch = self.optimizer.optimize_batch_size(
            topic,
            relevant_metrics['record_send_rate'],
            relevant_metrics['request_latency_avg']
        )
        
        return {
            'current_metrics': relevant_metrics,
            'recommended_batch_size': optimal_batch,
            'health_status': self.metrics.get_health_status()
        }
    
    def monitor_consumer_lag(self, consumer_group: str, topic: str):
        """Monitor consumer lag and recommend scaling"""
        
        # Get consumer group info
        consumer_metadata = self.kafka_client.describe_consumer_groups([consumer_group])
        
        total_lag = 0
        partition_lags = {}
        
        # Calculate lag per partition
        for partition_info in consumer_metadata[consumer_group].members:
            for topic_partition in partition_info.assignment:
                if topic_partition.topic == topic:
                    # Get high water mark and current offset
                    high_water_mark = self.kafka_client.get_partition_metadata(
                        topic, topic_partition.partition
                    ).high_water_mark
                    
                    current_offset = self.kafka_client.committed(topic_partition)
                    
                    if current_offset:
                        lag = high_water_mark - current_offset.offset
                        partition_lags[topic_partition.partition] = lag
                        total_lag += lag
        
        # Recommend scaling
        current_consumers = len(consumer_metadata[consumer_group].members)
        recommended_consumers = self.optimizer.auto_scale_consumers(total_lag, current_consumers)
        
        return {
            'total_lag': total_lag,
            'partition_lags': partition_lags,
            'current_consumers': current_consumers,
            'recommended_consumers': recommended_consumers
        }
```

---

## 🎯 Interview Scenarios & Solutions

### **Scenario 1: Design Notification System**

**Problem:** Design a notification system for 100M users supporting email, SMS, push notifications

**Solution:**
```python
class NotificationSystem:
    def __init__(self):
        # Different queues for different notification types
        self.email_queue = KafkaProducer(bootstrap_servers=['kafka1:9092'])
        self.sms_queue = KafkaProducer(bootstrap_servers=['kafka1:9092'])
        self.push_queue = KafkaProducer(bootstrap_servers=['kafka1:9092'])
        
        # Priority queues for urgent notifications
        self.urgent_queue = KafkaProducer(bootstrap_servers=['kafka1:9092'])
        
        # Dead letter queue for failed notifications
        self.dlq = KafkaProducer(bootstrap_servers=['kafka1:9092'])
    
    def send_notification(self, user_id: str, message: str, channels: List[str], priority: str = 'normal'):
        """Send notification through multiple channels"""
        
        notification = {
            'user_id': user_id,
            'message': message,
            'channels': channels,
            'priority': priority,
            'timestamp': time.time(),
            'retry_count': 0
        }
        
        # Route to appropriate queue based on priority
        if priority == 'urgent':
            topic = 'urgent-notifications'
            producer = self.urgent_queue
        else:
            topic = 'standard-notifications'
            producer = self.email_queue  # Use any producer
        
        # Partition by user_id for ordered processing per user
        producer.send(
            topic=topic,
            key=str(user_id).encode(),
            value=json.dumps(notification).encode()
        )
    
    def batch_notifications(self, notifications: List[Dict]):
        """Batch notifications efficiently"""
        
        # Group by priority and user
        batches = defaultdict(list)
        
        for notification in notifications:
            key = (notification['priority'], notification['user_id'])
            batches[key].append(notification)
        
        # Send batches
        for (priority, user_id), batch in batches.items():
            batch_message = {
                'batch_id': str(uuid.uuid4()),
                'user_id': user_id,
                'notifications': batch,
                'batch_size': len(batch)
            }
            
            topic = 'urgent-notifications' if priority == 'urgent' else 'standard-notifications'
            
            self.email_queue.send(
                topic=topic,
                key=str(user_id).encode(),
                value=json.dumps(batch_message).encode()
            )
```

### **Scenario 2: Design Chat System Message Delivery**

**Problem:** Design message delivery for a chat system with 10M concurrent users

**Solution:**
```python
class ChatMessageDelivery:
    def __init__(self):
        # Kafka for message persistence and delivery
        self.message_producer = KafkaProducer(
            bootstrap_servers=['kafka1:9092'],
            acks='all',  # Wait for all replicas
            retries=3
        )
        
        # Redis for real-time user presence
        self.redis_client = redis.Redis()
        
        # WebSocket connection manager
        self.connection_manager = WebSocketManager()
    
    def send_message(self, from_user: str, to_user: str, message: str, chat_id: str):
        """Send chat message with reliable delivery"""
        
        message_data = {
            'message_id': str(uuid.uuid4()),
            'from_user': from_user,
            'to_user': to_user,
            'chat_id': chat_id,
            'message': message,
            'timestamp': time.time(),
            'status': 'sent'
        }
        
        # Persist message to Kafka (partitioned by chat_id)
        self.message_producer.send(
            topic='chat-messages',
            key=chat_id.encode(),
            value=json.dumps(message_data).encode()
        )
        
        # Try real-time delivery
        if self.is_user_online(to_user):
            self.deliver_real_time(to_user, message_data)
        else:
            # Queue for delivery when user comes online
            self.queue_for_offline_user(to_user, message_data)
    
    def is_user_online(self, user_id: str) -> bool:
        """Check if user is online using Redis"""
        return self.redis_client.exists(f"online:{user_id}")
    
    def deliver_real_time(self, user_id: str, message_data: Dict):
        """Deliver message via WebSocket"""
        connections = self.connection_manager.get_user_connections(user_id)
        
        for connection in connections:
            try:
                connection.send(json.dumps(message_data))
                # Mark as delivered
                message_data['status'] = 'delivered'
            except:
                # Connection failed, user might be offline
                self.queue_for_offline_user(user_id, message_data)
    
    def queue_for_offline_user(self, user_id: str, message_data: Dict):
        """Queue message for offline user"""
        self.redis_client.lpush(f"offline_messages:{user_id}", json.dumps(message_data))
        self.redis_client.expire(f"offline_messages:{user_id}", 604800)  # 7 days
    
    def user_comes_online(self, user_id: str):
        """Deliver queued messages when user comes online"""
        
        # Mark user as online
        self.redis_client.setex(f"online:{user_id}", 3600, "1")  # 1 hour TTL
        
        # Get queued messages
        queued_messages = self.redis_client.lrange(f"offline_messages:{user_id}", 0, -1)
        
        # Deliver queued messages
        for message_json in queued_messages:
            message_data = json.loads(message_json)
            self.deliver_real_time(user_id, message_data)
        
        # Clear queue
        self.redis_client.delete(f"offline_messages:{user_id}")
```

---

## ✅ Message Queue Mastery Checklist

### **Core Concepts**
- [ ] Point-to-point vs pub/sub patterns
- [ ] Message ordering and partitioning strategies  
- [ ] Delivery guarantees (at-most-once, at-least-once, exactly-once)
- [ ] Dead letter queues and retry mechanisms
- [ ] Backpressure handling and flow control

### **Technology Expertise**
- [ ] Kafka architecture, partitioning, and consumer groups
- [ ] RabbitMQ exchanges, routing, and clustering
- [ ] AWS SQS/SNS configuration and best practices
- [ ] Redis pub/sub and stream capabilities
- [ ] Message serialization and schema evolution

### **Advanced Patterns**
- [ ] Event sourcing with message queues
- [ ] Saga pattern for distributed transactions
- [ ] CQRS with event-driven updates
- [ ] Message deduplication strategies
- [ ] Cross-region message replication

### **Production Readiness**
- [ ] Monitoring and alerting setup
- [ ] Performance optimization and auto-scaling
- [ ] Security (encryption, authentication, authorization)
- [ ] Disaster recovery and backup strategies
- [ ] Cost optimization techniques

**Master these patterns, and you'll build rock-solid distributed systems!** 🚀