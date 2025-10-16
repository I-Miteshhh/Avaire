# Design ETL Pipeline at Scale - Complete System Design

**Difficulty:** ⭐⭐⭐⭐  
**Interview Frequency:** Very High (Data Engineering roles, 40 LPA+)  
**Time to Complete:** 45-60 minutes  
**Real-World Examples:** Airbnb's Data Pipeline, Spotify's Event Delivery, Netflix's Data Infrastructure

---

## 📋 Problem Statement

**Design a scalable ETL (Extract, Transform, Load) pipeline that can:**
- Extract data from 500+ heterogeneous sources (databases, APIs, files, streams)
- Transform data at 10 TB/day throughput
- Load into multiple destinations (data warehouse, data lake, analytics DBs)
- Support both batch and real-time processing
- Handle schema evolution and data quality checks
- Provide data lineage and governance
- Enable reprocessing and backfilling
- Cost-optimize at petabyte scale

**Requirements:**
- Process 100 million records/hour
- End-to-end latency < 15 minutes for critical pipelines
- 99.9% pipeline reliability
- Support for incremental loads
- Auto-recovery from failures
- Monitoring and alerting

---

## 🎯 Functional Requirements

### **1. Extract (Data Ingestion)**
- **Database CDC** - Capture changes from MySQL, PostgreSQL, MongoDB
- **API Polling** - REST/GraphQL endpoints with pagination
- **File Processing** - S3, HDFS, FTP (CSV, JSON, Parquet, Avro)
- **Stream Ingestion** - Kafka, Kinesis, Pub/Sub
- **Log Collection** - Application logs, system logs
- **Webhook Receivers** - Real-time event ingestion

### **2. Transform (Data Processing)**
- **Data Cleansing** - Handle nulls, duplicates, invalid formats
- **Data Enrichment** - Join with reference data, API lookups
- **Aggregations** - Summarize, rollup, window functions
- **Data Validation** - Schema validation, business rules
- **PII Detection** - Identify and mask sensitive data
- **Denormalization** - Optimize for analytics queries

### **3. Load (Data Delivery)**
- **Data Warehouse** - Snowflake, Redshift, BigQuery
- **Data Lake** - S3, HDFS, ADLS (Parquet/ORC format)
- **OLAP Databases** - ClickHouse, Druid
- **Search Engines** - Elasticsearch
- **Cache Layers** - Redis for real-time access
- **Downstream Services** - Kafka topics, APIs

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      DATA SOURCES (500+)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │PostgreSQL│  │   MySQL  │  │ MongoDB  │  │  APIs    │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │             │             │               │
│  ┌────▼─────┐  ┌───▼──────┐  ┌───▼──────┐  ┌───▼──────┐       │
│  │   Logs   │  │  Files   │  │ Streams  │  │Webhooks  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└────┬──────────────┬─────────────┬─────────────┬────────────┬───┘
     │              │             │             │            │
     ▼              ▼             ▼             ▼            ▼
┌─────────────────────────────────────────────────────────────────┐
│              INGESTION LAYER (Extraction)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │  Debezium CDC  │  │ Airbyte/Fivetran│  │ Custom         │   │
│  │  - MySQL bin   │  │ - API connectors│  │ Connectors     │   │
│  │  - PostgreSQL  │  │ - SaaS tools    │  │ - Python/Scala │   │
│  │  - MongoDB     │  │ - Managed ETL   │  │ - Lambda/Cloud │   │
│  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘   │
│          │                   │                    │             │
│          └───────────────────┴────────────────────┘             │
│                              ▼                                   │
│                    ┌──────────────────┐                         │
│                    │  Raw Data Queue  │                         │
│                    │  (Kafka Topics)  │                         │
│                    │  - raw_events    │                         │
│                    │  - raw_changes   │                         │
│                    │  - raw_files     │                         │
│                    └─────────┬────────┘                         │
└──────────────────────────────┼──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│           ORCHESTRATION LAYER (Airflow/Prefect)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  DAG Scheduler                                           │  │
│  │  - Batch jobs (hourly, daily, weekly)                   │  │
│  │  - Dependencies & SLAs                                   │  │
│  │  - Retry logic & backfill                               │  │
│  │  - Resource allocation                                   │  │
│  └──────────────────┬───────────────────────────────────────┘  │
│                     │                                           │
└─────────────────────┼───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│          PROCESSING LAYER (Transformation)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  BATCH PROCESSING (Spark on EMR/Databricks)           │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │    │
│  │  │ Cleanse  │→ │ Enrich   │→ │Aggregate │            │    │
│  │  └──────────┘  └──────────┘  └──────────┘            │    │
│  │  - Deduplication  - Joins      - Rollups              │    │
│  │  - Validation     - Lookups    - Windows              │    │
│  │  - Formatting     - API calls  - Pivoting             │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  STREAM PROCESSING (Flink/Spark Streaming)            │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │    │
│  │  │ Filter   │→ │Transform │→ │ Window   │            │    │
│  │  └──────────┘  └──────────┘  └──────────┘            │    │
│  │  - Low latency    - Enrichment  - Aggregation         │    │
│  │  - Stateful       - Validation   - Join streams       │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  DATA QUALITY CHECKS (Great Expectations)             │    │
│  │  - Schema validation                                   │    │
│  │  - Null checks, range checks                          │    │
│  │  - Uniqueness constraints                             │    │
│  │  - Referential integrity                              │    │
│  │  - Custom business rules                              │    │
│  └────────────────────────────────────────────────────────┘    │
└────┬──────────────┬─────────────┬─────────────┬────────────┬───┘
     │              │             │             │            │
     ▼              ▼             ▼             ▼            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  LOADING LAYER (Targets)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Snowflake    │  │   Redshift   │  │  BigQuery    │         │
│  │ (OLAP/DWH)   │  │  (OLAP/DWH)  │  │  (OLAP/DWH)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ S3 Data Lake │  │ ClickHouse   │  │Elasticsearch │         │
│  │ (Parquet)    │  │ (Real-time)  │  │  (Search)    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   METADATA & GOVERNANCE                          │
├─────────────────────────────────────────────────────────────────┤
│  - Data Catalog (DataHub, Amundsen)                            │
│  - Lineage Tracking (OpenLineage)                              │
│  - Schema Registry (Confluent Schema Registry)                 │
│  - Data Quality Metrics                                        │
│  - Cost Attribution                                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                 MONITORING & ALERTING                            │
├─────────────────────────────────────────────────────────────────┤
│  - Pipeline Health (Datadog, Prometheus)                       │
│  - Data Freshness SLAs                                         │
│  - Data Quality Alerts                                         │
│  - Cost Monitoring                                             │
│  - Anomaly Detection                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💻 Detailed Implementation

### **1. CDC-Based Database Ingestion with Debezium**

```python
from kafka import KafkaProducer, KafkaConsumer
import json
from typing import Dict, List
from datetime import datetime
import psycopg2
from dataclasses import dataclass

@dataclass
class CDCEvent:
    operation: str  # 'c' (create), 'u' (update), 'd' (delete), 'r' (read/snapshot)
    before: Dict
    after: Dict
    source: Dict
    timestamp: int

class DebeziumCDCManager:
    """
    Manage Change Data Capture from databases using Debezium
    """
    
    def __init__(self, kafka_bootstrap_servers: str):
        self.kafka_servers = kafka_bootstrap_servers
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            compression_type='snappy',
            batch_size=16384,
            linger_ms=10,
            acks='all'
        )
    
    def setup_postgres_connector(self, db_config: Dict):
        """
        Configure Debezium PostgreSQL connector
        """
        
        connector_config = {
            "name": f"postgres-{db_config['database']}-connector",
            "config": {
                "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
                "plugin.name": "pgoutput",
                "database.hostname": db_config['host'],
                "database.port": db_config['port'],
                "database.user": db_config['user'],
                "database.password": db_config['password'],
                "database.dbname": db_config['database'],
                "database.server.name": db_config['server_name'],
                
                # Tables to capture
                "table.include.list": db_config.get('tables', 'public.*'),
                
                # Snapshot configuration
                "snapshot.mode": "initial",  # initial, never, always
                
                # Change events configuration
                "publication.autocreate.mode": "filtered",
                "slot.name": f"debezium_{db_config['database']}",
                
                # Kafka topic configuration
                "topic.prefix": f"cdc.{db_config['database']}",
                "topic.creation.enable": "true",
                "topic.creation.default.replication.factor": 3,
                "topic.creation.default.partitions": 10,
                "topic.creation.default.cleanup.policy": "delete",
                "topic.creation.default.retention.ms": 604800000,  # 7 days
                
                # Performance tuning
                "max.batch.size": 2048,
                "max.queue.size": 8192,
                "poll.interval.ms": 1000,
                
                # Schema changes
                "include.schema.changes": "true",
                "schema.history.internal.kafka.topic": f"schema-changes.{db_config['database']}",
                "schema.history.internal.kafka.bootstrap.servers": self.kafka_servers,
                
                # Transformations
                "transforms": "unwrap,addMetadata",
                "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
                "transforms.unwrap.drop.tombstones": "false",
                "transforms.unwrap.delete.handling.mode": "rewrite",
                "transforms.addMetadata.type": "org.apache.kafka.connect.transforms.InsertField$Value",
                "transforms.addMetadata.timestamp.field": "extracted_at"
            }
        }
        
        # Register connector with Kafka Connect
        self._register_connector(connector_config)
        
        return connector_config
    
    def setup_mysql_connector(self, db_config: Dict):
        """
        Configure Debezium MySQL connector with binlog
        """
        
        connector_config = {
            "name": f"mysql-{db_config['database']}-connector",
            "config": {
                "connector.class": "io.debezium.connector.mysql.MySqlConnector",
                "database.hostname": db_config['host'],
                "database.port": db_config['port'],
                "database.user": db_config['user'],
                "database.password": db_config['password'],
                "database.server.id": db_config.get('server_id', 184054),
                "database.server.name": db_config['server_name'],
                
                # Binlog configuration
                "database.include.list": db_config['database'],
                "table.include.list": db_config.get('tables', '.*'),
                
                # Snapshot
                "snapshot.mode": "when_needed",
                "snapshot.locking.mode": "minimal",
                
                # Binlog reader
                "binlog.buffer.size": 8192,
                
                # GTIDs
                "gtid.source.includes": ".*",
                
                # Topic routing
                "topic.prefix": f"cdc.{db_config['database']}",
                
                # Include DDL changes
                "include.schema.changes": "true",
                "database.history.kafka.topic": f"schema-changes.{db_config['database']}",
                "database.history.kafka.bootstrap.servers": self.kafka_servers,
                
                # Performance
                "max.batch.size": 2048,
                "max.queue.size": 8192,
                
                # Incremental snapshots
                "incremental.snapshot.allow.schema.changes": "true"
            }
        }
        
        self._register_connector(connector_config)
        return connector_config
    
    def consume_cdc_events(self, topic: str, consumer_group: str):
        """
        Consume CDC events from Kafka topic
        """
        
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=self.kafka_servers,
            group_id=consumer_group,
            auto_offset_reset='earliest',
            enable_auto_commit=False,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        for message in consumer:
            try:
                event = self._parse_cdc_event(message.value)
                
                # Process based on operation type
                if event.operation == 'c':  # Create/Insert
                    self._handle_insert(event)
                elif event.operation == 'u':  # Update
                    self._handle_update(event)
                elif event.operation == 'd':  # Delete
                    self._handle_delete(event)
                elif event.operation == 'r':  # Read (snapshot)
                    self._handle_snapshot(event)
                
                # Commit offset after successful processing
                consumer.commit()
                
            except Exception as e:
                print(f"Error processing CDC event: {e}")
                # Send to dead letter queue
                self._send_to_dlq(message, str(e))
    
    def _parse_cdc_event(self, event_data: Dict) -> CDCEvent:
        """Parse Debezium CDC event"""
        
        payload = event_data.get('payload', {})
        
        return CDCEvent(
            operation=payload.get('op'),
            before=payload.get('before', {}),
            after=payload.get('after', {}),
            source=payload.get('source', {}),
            timestamp=payload.get('ts_ms', 0)
        )
    
    def _handle_insert(self, event: CDCEvent):
        """Handle INSERT operations"""
        
        table = event.source.get('table')
        data = event.after
        
        # Transform and load to destination
        transformed_data = self._transform_data(data, table)
        self._load_to_warehouse(transformed_data, table, operation='insert')
    
    def _handle_update(self, event: CDCEvent):
        """Handle UPDATE operations"""
        
        table = event.source.get('table')
        old_data = event.before
        new_data = event.after
        
        # Detect which fields changed
        changed_fields = {
            k: {'old': old_data.get(k), 'new': new_data.get(k)}
            for k in new_data.keys()
            if old_data.get(k) != new_data.get(k)
        }
        
        transformed_data = self._transform_data(new_data, table)
        self._load_to_warehouse(transformed_data, table, operation='update')
    
    def _handle_delete(self, event: CDCEvent):
        """Handle DELETE operations"""
        
        table = event.source.get('table')
        data = event.before
        
        # Soft delete in warehouse
        self._load_to_warehouse(data, table, operation='delete')


### **2. Spark ETL Pipeline with Data Quality**

```python
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *
from typing import List, Dict
import great_expectations as gx
from datetime import datetime

class SparkETLPipeline:
    """
    Production-grade Spark ETL pipeline with data quality checks
    """
    
    def __init__(self, app_name: str = "ProductionETL"):
        self.spark = SparkSession.builder \
            .appName(app_name) \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.sql.adaptive.skewJoin.enabled", "true") \
            .config("spark.sql.files.maxPartitionBytes", "134217728") \
            .config("spark.sql.shuffle.partitions", "200") \
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
            .config("spark.sql.sources.partitionOverwriteMode", "dynamic") \
            .getOrCreate()
        
        # Set log level
        self.spark.sparkContext.setLogLevel("WARN")
        
        # Initialize Great Expectations
        self.gx_context = gx.get_context()
    
    def extract_from_source(self, source_config: Dict) -> DataFrame:
        """
        Extract data from various sources
        """
        
        source_type = source_config['type']
        
        if source_type == 'jdbc':
            return self._extract_from_jdbc(source_config)
        elif source_type == 's3':
            return self._extract_from_s3(source_config)
        elif source_type == 'kafka':
            return self._extract_from_kafka(source_config)
        elif source_type == 'delta':
            return self._extract_from_delta(source_config)
        else:
            raise ValueError(f"Unsupported source type: {source_type}")
    
    def _extract_from_jdbc(self, config: Dict) -> DataFrame:
        """Extract from JDBC source with partitioning"""
        
        return self.spark.read \
            .format("jdbc") \
            .option("url", config['jdbc_url']) \
            .option("dbtable", config['table']) \
            .option("user", config['user']) \
            .option("password", config['password']) \
            .option("driver", config.get('driver', 'org.postgresql.Driver')) \
            .option("numPartitions", config.get('num_partitions', 10)) \
            .option("partitionColumn", config.get('partition_column', 'id')) \
            .option("lowerBound", config.get('lower_bound', 0)) \
            .option("upperBound", config.get('upper_bound', 1000000)) \
            .option("fetchsize", config.get('fetch_size', 10000)) \
            .load()
    
    def _extract_from_s3(self, config: Dict) -> DataFrame:
        """Extract from S3 with partition pruning"""
        
        format_type = config.get('format', 'parquet')
        
        df = self.spark.read \
            .format(format_type) \
            .option("mergeSchema", "true") \
            .option("pathGlobFilter", config.get('path_filter', '*.parquet'))
        
        # Add partition filters if specified
        if 'partition_filters' in config:
            df = df.option("partitionFilter", config['partition_filters'])
        
        return df.load(config['path'])
    
    def _extract_from_kafka(self, config: Dict) -> DataFrame:
        """Extract from Kafka stream"""
        
        return self.spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", config['brokers']) \
            .option("subscribe", config['topic']) \
            .option("startingOffsets", config.get('starting_offsets', 'latest')) \
            .option("maxOffsetsPerTrigger", config.get('max_offsets', 10000)) \
            .option("kafka.security.protocol", config.get('security_protocol', 'PLAINTEXT')) \
            .load() \
            .selectExpr("CAST(value AS STRING) as json_data") \
            .select(from_json(col("json_data"), config['schema']).alias("data")) \
            .select("data.*")
    
    def transform_data(self, df: DataFrame, transformations: List[Dict]) -> DataFrame:
        """
        Apply transformations with comprehensive data quality checks
        """
        
        # 1. Data Cleansing
        df = self._cleanse_data(df)
        
        # 2. Deduplication
        df = self._deduplicate(df, transformations)
        
        # 3. Schema Evolution
        df = self._handle_schema_evolution(df, transformations)
        
        # 4. Custom Transformations
        for transform in transformations:
            transform_type = transform['type']
            
            if transform_type == 'filter':
                df = df.filter(transform['condition'])
            
            elif transform_type == 'enrich':
                df = self._enrich_data(df, transform)
            
            elif transform_type == 'aggregate':
                df = self._aggregate_data(df, transform)
            
            elif transform_type == 'pivot':
                df = self._pivot_data(df, transform)
            
            elif transform_type == 'unpivot':
                df = self._unpivot_data(df, transform)
        
        # 5. Data Quality Validation
        self._validate_data_quality(df, transformations)
        
        return df
    
    def _cleanse_data(self, df: DataFrame) -> DataFrame:
        """
        Comprehensive data cleansing
        """
        
        # Remove duplicates based on all columns
        df = df.dropDuplicates()
        
        # Trim whitespace from string columns
        string_cols = [f.name for f in df.schema.fields if isinstance(f.dataType, StringType)]
        for col_name in string_cols:
            df = df.withColumn(col_name, trim(col(col_name)))
        
        # Replace empty strings with null
        for col_name in string_cols:
            df = df.withColumn(
                col_name,
                when(col(col_name) == "", None).otherwise(col(col_name))
            )
        
        # Handle special null values
        for col_name in df.columns:
            df = df.withColumn(
                col_name,
                when(col(col_name).isin(['NULL', 'null', 'N/A', 'NA', 'None']), None)
                .otherwise(col(col_name))
            )
        
        return df
    
    def _deduplicate(self, df: DataFrame, config: List[Dict]) -> DataFrame:
        """
        Remove duplicates with configurable strategy
        """
        
        dedup_config = next((t for t in config if t['type'] == 'deduplicate'), None)
        
        if not dedup_config:
            return df
        
        key_columns = dedup_config['key_columns']
        order_column = dedup_config.get('order_column', 'updated_at')
        
        # Window function to keep latest record
        from pyspark.sql.window import Window
        
        window_spec = Window.partitionBy(key_columns).orderBy(col(order_column).desc())
        
        df = df.withColumn("row_num", row_number().over(window_spec)) \
            .filter(col("row_num") == 1) \
            .drop("row_num")
        
        return df
    
    def _enrich_data(self, df: DataFrame, config: Dict) -> DataFrame:
        """
        Enrich data with lookups and joins
        """
        
        enrich_type = config.get('enrich_type')
        
        if enrich_type == 'lookup':
            # Load lookup table
            lookup_df = self.spark.read.parquet(config['lookup_path'])
            
            # Join with main dataframe
            join_keys = config['join_keys']
            df = df.join(
                broadcast(lookup_df) if config.get('broadcast', True) else lookup_df,
                on=join_keys,
                how=config.get('join_type', 'left')
            )
        
        elif enrich_type == 'api':
            # Enrich using API calls (use UDF)
            @udf(returnType=StringType())
            def api_enrich(key):
                # Call external API
                import requests
                response = requests.get(f"{config['api_url']}/{key}")
                return response.json().get(config['return_field'])
            
            df = df.withColumn(
                config['new_column'],
                api_enrich(col(config['key_column']))
            )
        
        return df
    
    def _aggregate_data(self, df: DataFrame, config: Dict) -> DataFrame:
        """
        Aggregate data with grouping and windowing
        """
        
        group_cols = config['group_by']
        agg_exprs = []
        
        for agg in config['aggregations']:
            agg_func = agg['function']  # 'sum', 'avg', 'count', etc.
            col_name = agg['column']
            alias = agg.get('alias', f"{agg_func}_{col_name}")
            
            if agg_func == 'sum':
                agg_exprs.append(sum(col(col_name)).alias(alias))
            elif agg_func == 'avg':
                agg_exprs.append(avg(col(col_name)).alias(alias))
            elif agg_func == 'count':
                agg_exprs.append(count(col(col_name)).alias(alias))
            elif agg_func == 'min':
                agg_exprs.append(min(col(col_name)).alias(alias))
            elif agg_func == 'max':
                agg_exprs.append(max(col(col_name)).alias(alias))
            elif agg_func == 'count_distinct':
                agg_exprs.append(countDistinct(col(col_name)).alias(alias))
        
        return df.groupBy(group_cols).agg(*agg_exprs)
    
    def _validate_data_quality(self, df: DataFrame, config: List[Dict]):
        """
        Comprehensive data quality validation using Great Expectations
        """
        
        quality_config = next((t for t in config if t['type'] == 'quality_check'), None)
        
        if not quality_config:
            return
        
        # Convert Spark DataFrame to Pandas for Great Expectations
        # (In production, use Great Expectations Spark integration)
        sample_df = df.limit(10000).toPandas()
        
        # Create expectations suite
        suite_name = quality_config.get('suite_name', 'default_suite')
        
        expectations = quality_config.get('expectations', [])
        
        for expectation in expectations:
            exp_type = expectation['type']
            
            if exp_type == 'not_null':
                # Expect column to not be null
                null_count = df.filter(col(expectation['column']).isNull()).count()
                if null_count > 0:
                    raise ValueError(f"Found {null_count} null values in {expectation['column']}")
            
            elif exp_type == 'unique':
                # Expect column to be unique
                total_count = df.count()
                distinct_count = df.select(expectation['column']).distinct().count()
                if total_count != distinct_count:
                    raise ValueError(f"Column {expectation['column']} is not unique")
            
            elif exp_type == 'range':
                # Expect values to be in range
                col_name = expectation['column']
                min_val = expectation['min']
                max_val = expectation['max']
                
                out_of_range = df.filter(
                    (col(col_name) < min_val) | (col(col_name) > max_val)
                ).count()
                
                if out_of_range > 0:
                    raise ValueError(
                        f"Found {out_of_range} values outside range [{min_val}, {max_val}]"
                    )
    
    def load_to_destination(self, df: DataFrame, destination_config: Dict):
        """
        Load data to destination with optimization
        """
        
        dest_type = destination_config['type']
        
        if dest_type == 'snowflake':
            self._load_to_snowflake(df, destination_config)
        elif dest_type == 'redshift':
            self._load_to_redshift(df, destination_config)
        elif dest_type == 'delta':
            self._load_to_delta(df, destination_config)
        elif dest_type == 's3':
            self._load_to_s3(df, destination_config)
        elif dest_type == 'jdbc':
            self._load_to_jdbc(df, destination_config)
    
    def _load_to_delta(self, df: DataFrame, config: Dict):
        """
        Load to Delta Lake with ACID transactions and optimization
        """
        
        from delta.tables import DeltaTable
        
        target_path = config['path']
        write_mode = config.get('mode', 'append')  # append, overwrite, merge
        partition_cols = config.get('partition_by', [])
        
        if write_mode == 'merge':
            # Upsert operation
            merge_keys = config['merge_keys']
            
            if DeltaTable.isDeltaTable(self.spark, target_path):
                delta_table = DeltaTable.forPath(self.spark, target_path)
                
                # Build merge condition
                merge_condition = " AND ".join([
                    f"target.{k} = source.{k}" for k in merge_keys
                ])
                
                delta_table.alias("target").merge(
                    df.alias("source"),
                    merge_condition
                ).whenMatchedUpdateAll() \
                 .whenNotMatchedInsertAll() \
                 .execute()
            else:
                # First time - just write
                df.write \
                    .format("delta") \
                    .partitionBy(partition_cols) \
                    .save(target_path)
        else:
            # Regular write
            writer = df.write \
                .format("delta") \
                .mode(write_mode)
            
            if partition_cols:
                writer = writer.partitionBy(partition_cols)
            
            writer.save(target_path)
        
        # Optimize Delta table
        if config.get('optimize', False):
            self.spark.sql(f"OPTIMIZE delta.`{target_path}`")
        
        # Z-order if specified
        if 'zorder_cols' in config:
            zorder_cols = ','.join(config['zorder_cols'])
            self.spark.sql(f"OPTIMIZE delta.`{target_path}` ZORDER BY ({zorder_cols})")
    
    def _load_to_snowflake(self, df: DataFrame, config: Dict):
        """
        Load to Snowflake with optimization
        """
        
        sfOptions = {
            "sfURL": config['url'],
            "sfUser": config['user'],
            "sfPassword": config['password'],
            "sfDatabase": config['database'],
            "sfSchema": config['schema'],
            "sfWarehouse": config['warehouse'],
            "sfRole": config.get('role', 'SYSADMIN')
        }
        
        df.write \
            .format("snowflake") \
            .options(**sfOptions) \
            .option("dbtable", config['table']) \
            .mode(config.get('mode', 'append')) \
            .save()


### **3. Airflow DAG Orchestration**

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.utils.dates import days_ago
from datetime import timedelta

# Define DAG
default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'email': ['alerts@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
    'sla': timedelta(hours=6)
}

dag = DAG(
    'daily_etl_pipeline',
    default_args=default_args,
    description='Daily ETL pipeline with data quality checks',
    schedule_interval='0 2 * * *',  # 2 AM daily
    start_date=days_ago(1),
    catchup=False,
    max_active_runs=1,
    tags=['production', 'etl', 'daily']
)

# Task 1: Wait for source data
wait_for_source = S3KeySensor(
    task_id='wait_for_source_data',
    bucket_name='source-data',
    bucket_key='raw/{{ ds }}/*.parquet',
    timeout=3600,
    poke_interval=60,
    dag=dag
)

# Task 2: Extract and validate
extract_task = SparkSubmitOperator(
    task_id='extract_data',
    application='/opt/airflow/dags/scripts/extract.py',
    conf={
        'spark.executor.memory': '4g',
        'spark.executor.cores': '2',
        'spark.executor.instances': '10'
    },
    application_args=[
        '--date', '{{ ds }}',
        '--source', 's3://source-data/raw/{{ ds }}/'
    ],
    dag=dag
)

# Task 3: Transform and quality check
transform_task = SparkSubmitOperator(
    task_id='transform_data',
    application='/opt/airflow/dags/scripts/transform.py',
    conf={
        'spark.executor.memory': '8g',
        'spark.executor.cores': '4',
        'spark.executor.instances': '20'
    },
    application_args=[
        '--date', '{{ ds }}',
        '--input', 's3://staging/extracted/{{ ds }}/',
        '--output', 's3://staging/transformed/{{ ds }}/'
    ],
    dag=dag
)

# Task 4: Load to warehouse
load_task = SparkSubmitOperator(
    task_id='load_to_warehouse',
    application='/opt/airflow/dags/scripts/load.py',
    application_args=[
        '--date', '{{ ds }}',
        '--input', 's3://staging/transformed/{{ ds }}/',
        '--warehouse', 'snowflake'
    ],
    dag=dag
)

# Task dependencies
wait_for_source >> extract_task >> transform_task >> load_task
```

---

## 🎓 Key Interview Points

### **Capacity Estimation:**
```
Input: 100M records/hour = 27,777 records/sec
Record size: 1 KB average
Throughput: 27.7 MB/sec input = 100 GB/hour

Spark cluster sizing:
- 100 GB/hour ÷ 10 executors = 10 GB/executor/hour
- With 3x processing overhead = 30 GB memory/executor
- Total: 10 executors × 30 GB = 300 GB cluster memory

Cost (AWS EMR):
- r5.4xlarge (16 vCPU, 128 GB RAM) = $1.008/hour
- 10 instances × $1.008 = $10.08/hour × 24 = $242/day
- Monthly: $7,260
```

### **Trade-offs:**
1. **Batch vs Stream Processing**
2. **Schema-on-write vs Schema-on-read**
3. **Full vs Incremental loads**
4. **Cost vs Performance**

**This demonstrates production ETL design - critical for data engineering roles!** 🚀
