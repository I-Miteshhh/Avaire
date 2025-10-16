# Design a Data Lake Architecture - Complete System Design

**Difficulty:** ⭐⭐⭐⭐⭐  
**Interview Frequency:** Very High (FAANG, 40 LPA+)  
**Time to Complete:** 45-60 minutes  
**Real-World Examples:** Netflix Data Platform, Uber's Data Lake, LinkedIn's Data Infrastructure

---

## 📋 Problem Statement

**Design a scalable data lake that can:**
- Ingest data from 1000+ sources (databases, APIs, logs, streams)
- Store petabytes of structured, semi-structured, and unstructured data
- Support both batch and real-time processing
- Enable data scientists, analysts, and ML engineers to query data
- Maintain data quality, governance, and security
- Cost-optimize storage and compute

**Scale Requirements:**
- 100 TB/day data ingestion
- 50 PB total storage
- 10,000+ daily queries
- Sub-second latency for metadata queries
- Support 1000+ concurrent users

---

## 🎯 Functional Requirements

### **Core Capabilities**
1. **Data Ingestion**
   - Batch ingestion from databases (MySQL, PostgreSQL, MongoDB)
   - Real-time streaming from Kafka, Kinesis, Event Hub
   - File uploads (CSV, JSON, Parquet, Avro)
   - API data collection
   - Log aggregation

2. **Data Storage**
   - Raw data zone (unchanged data)
   - Curated data zone (cleaned, validated)
   - Analytics-ready zone (optimized for queries)
   - Archive zone (cold storage)

3. **Data Processing**
   - Batch processing (Spark, Hive)
   - Stream processing (Flink, Spark Streaming)
   - ETL/ELT pipelines
   - Data quality checks
   - Schema evolution

4. **Data Access**
   - SQL queries (Presto, Athena, BigQuery)
   - DataFrame APIs (Spark, Pandas)
   - Direct file access (S3, HDFS)
   - REST APIs for metadata
   - ML model training

5. **Governance & Security**
   - Data catalog and discovery
   - Access control (RBAC, ABAC)
   - Data lineage tracking
   - PII detection and masking
   - Audit logging

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                             │
├─────────────────────────────────────────────────────────────────┤
│  Databases  │  APIs  │  Logs  │  Streams  │  Files  │  IoT     │
└─────┬───────┴────┬───┴────┬───┴─────┬─────┴────┬────┴──────┬───┘
      │            │        │         │          │           │
      ▼            ▼        ▼         ▼          ▼           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INGESTION LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│  CDC (Debezium)  │  Kafka Connect  │  Firehose  │  Airflow    │
│  Lambda/Functions│  Fluentd        │  Custom Connectors        │
└─────┬───────────────────────────┬──────────────────────────┬───┘
      │                           │                          │
      ▼                           ▼                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STORAGE LAYER (S3/HDFS/ADLS)                 │
├─────────────────────────────────────────────────────────────────┤
│  RAW ZONE        │  CURATED ZONE    │  ANALYTICS ZONE           │
│  (Bronze)        │  (Silver)        │  (Gold)                   │
│  - Original data │  - Validated     │  - Aggregated             │
│  - Immutable     │  - Deduplicated  │  - Denormalized           │
│  - Partitioned   │  - Enriched      │  - Optimized (Parquet)    │
│  - Compressed    │  - Quality checks│  - Indexed                │
└─────┬───────────────────────────┬──────────────────────────┬───┘
      │                           │                          │
      ▼                           ▼                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    METADATA & CATALOG                           │
├─────────────────────────────────────────────────────────────────┤
│  Glue Catalog │ Hive Metastore │ DataHub │ Atlas │ Amundsen   │
│  - Schema registry   │ - Data lineage   │ - Data discovery     │
└─────┬───────────────────────────┬──────────────────────────┬───┘
      │                           │                          │
      ▼                           ▼                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSING LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  Spark (Batch)  │  Flink (Stream)  │  Airflow (Orchestration)  │
│  Presto/Athena (SQL) │ Lambda (Serverless) │ EMR/Databricks    │
└─────┬───────────────────────────┬──────────────────────────┬───┘
      │                           │                          │
      ▼                           ▼                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ACCESS LAYER                                 │
├─────────────────────────────────────────────────────────────────┤
│  BI Tools (Tableau, Looker) │ Jupyter Notebooks │ APIs         │
│  ML Platforms (SageMaker)   │ Data Scientists   │ Applications │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                CROSS-CUTTING CONCERNS                           │
├─────────────────────────────────────────────────────────────────┤
│  Security (IAM, Encryption) │ Monitoring (CloudWatch, Datadog) │
│  Data Quality (Great Expectations) │ Cost Management          │
│  Governance (Data Catalog, Lineage) │ Disaster Recovery       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💻 Detailed Component Design

### **1. Ingestion Layer - Multi-Source Data Collection**

```python
# AWS-based ingestion architecture
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
import boto3
import json

@dataclass
class DataSource:
    source_id: str
    source_type: str  # 'database', 'stream', 'api', 'file'
    connection_config: Dict
    ingestion_schedule: str  # Cron expression
    target_bucket: str
    target_prefix: str

class DataLakeIngestionManager:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.glue_client = boto3.client('glue')
        self.kinesis_client = boto3.client('kinesis')
        self.dms_client = boto3.client('dms')  # Database Migration Service
        
    def ingest_from_database(self, source: DataSource):
        """
        Use AWS DMS for CDC-based database ingestion
        Full load + continuous replication
        """
        
        # Create DMS replication task
        replication_task_config = {
            'ReplicationTaskIdentifier': f"task-{source.source_id}",
            'SourceEndpointArn': source.connection_config['source_arn'],
            'TargetEndpointArn': self._get_s3_target_endpoint(source),
            'ReplicationInstanceArn': source.connection_config['replication_instance_arn'],
            'MigrationType': 'full-load-and-cdc',  # Full load + change data capture
            'TableMappings': json.dumps({
                'rules': [{
                    'rule-type': 'selection',
                    'rule-id': '1',
                    'rule-name': 'include-all-tables',
                    'object-locator': {
                        'schema-name': source.connection_config['schema'],
                        'table-name': '%'
                    },
                    'rule-action': 'include'
                }]
            }),
            'ReplicationTaskSettings': json.dumps({
                'TargetMetadata': {
                    'SupportLobs': True,
                    'LobMaxSize': 32  # MB
                },
                'FullLoadSettings': {
                    'TargetTablePrepMode': 'DO_NOTHING',
                    'MaxFullLoadSubTasks': 8
                },
                'ChangeProcessingTuning': {
                    'BatchApplyTimeoutMin': 1,
                    'BatchApplyTimeoutMax': 30,
                    'BatchSplitSize': 0,
                    'CommitTimeout': 1,
                    'MemoryLimitTotal': 1024,
                    'MemoryKeepTime': 60,
                    'StatementCacheSize': 50
                },
                'Logging': {
                    'EnableLogging': True
                }
            })
        }
        
        response = self.dms_client.create_replication_task(**replication_task_config)
        
        # Start replication
        self.dms_client.start_replication_task(
            ReplicationTaskArn=response['ReplicationTask']['ReplicationTaskArn'],
            StartReplicationTaskType='start-replication'
        )
        
        return response
    
    def ingest_from_stream(self, source: DataSource):
        """
        Ingest from Kinesis/Kafka using Kinesis Firehose
        Automatic batching, compression, and S3 delivery
        """
        
        firehose_config = {
            'DeliveryStreamName': f"stream-{source.source_id}",
            'DeliveryStreamType': 'KinesisStreamAsSource',
            'KinesisStreamSourceConfiguration': {
                'KinesisStreamARN': source.connection_config['stream_arn'],
                'RoleARN': source.connection_config['firehose_role_arn']
            },
            'ExtendedS3DestinationConfiguration': {
                'RoleARN': source.connection_config['firehose_role_arn'],
                'BucketARN': f"arn:aws:s3:::{source.target_bucket}",
                'Prefix': f"{source.target_prefix}/year=!{{timestamp:yyyy}}/month=!{{timestamp:MM}}/day=!{{timestamp:dd}}/",
                'ErrorOutputPrefix': f"errors/{source.target_prefix}/",
                
                # Buffering hints
                'BufferingHints': {
                    'SizeInMBs': 128,  # Buffer up to 128 MB
                    'IntervalInSeconds': 300  # Or 5 minutes
                },
                
                # Compression
                'CompressionFormat': 'GZIP',
                
                # Data transformation
                'ProcessingConfiguration': {
                    'Enabled': True,
                    'Processors': [{
                        'Type': 'Lambda',
                        'Parameters': [{
                            'ParameterName': 'LambdaArn',
                            'ParameterValue': source.connection_config['transform_lambda_arn']
                        }]
                    }]
                },
                
                # Encryption
                'EncryptionConfiguration': {
                    'KMSEncryptionConfig': {
                        'AWSKMSKeyARN': source.connection_config['kms_key_arn']
                    }
                },
                
                # CloudWatch logging
                'CloudWatchLoggingOptions': {
                    'Enabled': True,
                    'LogGroupName': f'/aws/kinesisfirehose/{source.source_id}',
                    'LogStreamName': 'S3Delivery'
                },
                
                # Data format conversion (JSON to Parquet)
                'DataFormatConversionConfiguration': {
                    'Enabled': True,
                    'SchemaConfiguration': {
                        'RoleARN': source.connection_config['firehose_role_arn'],
                        'DatabaseName': source.connection_config['glue_database'],
                        'TableName': source.connection_config['glue_table'],
                        'Region': 'us-east-1',
                        'VersionId': 'LATEST'
                    },
                    'InputFormatConfiguration': {
                        'Deserializer': {'OpenXJsonSerDe': {}}
                    },
                    'OutputFormatConfiguration': {
                        'Serializer': {
                            'ParquetSerDe': {
                                'Compression': 'SNAPPY',
                                'BlockSizeBytes': 268435456,  # 256 MB
                                'PageSizeBytes': 1048576,  # 1 MB
                                'EnableDictionaryCompression': True
                            }
                        }
                    }
                }
            }
        }
        
        firehose = boto3.client('firehose')
        response = firehose.create_delivery_stream(**firehose_config)
        
        return response
    
    def ingest_from_api(self, source: DataSource):
        """
        Scheduled API data collection using Lambda + EventBridge
        """
        
        lambda_function_code = f'''
import json
import boto3
import requests
from datetime import datetime

def lambda_handler(event, context):
    # API configuration
    api_url = "{source.connection_config['api_url']}"
    api_key = "{source.connection_config['api_key']}"
    
    # Fetch data from API
    headers = {{'Authorization': f'Bearer {{api_key}}'}}
    response = requests.get(api_url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"API request failed: {{response.status_code}}")
    
    data = response.json()
    
    # Store in S3 with partitioning
    s3_client = boto3.client('s3')
    timestamp = datetime.utcnow()
    
    s3_key = (
        f"{{'{source.target_prefix}'}}"
        f"/year={{timestamp.year}}"
        f"/month={{timestamp.month:02d}}"
        f"/day={{timestamp.day:02d}}"
        f"/hour={{timestamp.hour:02d}}"
        f"/data_{{timestamp.timestamp()}}.json.gz"
    )
    
    import gzip
    compressed_data = gzip.compress(json.dumps(data).encode())
    
    s3_client.put_object(
        Bucket='{source.target_bucket}',
        Key=s3_key,
        Body=compressed_data,
        ContentType='application/json',
        ContentEncoding='gzip',
        ServerSideEncryption='aws:kms',
        SSEKMSKeyId='{source.connection_config["kms_key_arn"]}'
    )
    
    # Update Glue Catalog
    glue_client = boto3.client('glue')
    partition_values = [
        str(timestamp.year),
        f"{{timestamp.month:02d}}",
        f"{{timestamp.day:02d}}",
        f"{{timestamp.hour:02d}}"
    ]
    
    try:
        glue_client.create_partition(
            DatabaseName='{source.connection_config["glue_database"]}',
            TableName='{source.connection_config["glue_table"]}',
            PartitionInput={{
                'Values': partition_values,
                'StorageDescriptor': {{
                    'Location': f's3://{{'{source.target_bucket}'}}/{{s3_key.rsplit("/", 1)[0]}}/',
                    'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                    'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                    'SerdeInfo': {{
                        'SerializationLibrary': 'org.openx.data.jsonserde.JsonSerDe'
                    }}
                }}
            }}
        )
    except glue_client.exceptions.AlreadyExistsException:
        pass  # Partition already exists
    
    return {{
        'statusCode': 200,
        'body': json.dumps({{
            'records_ingested': len(data),
            's3_location': f's3://{{'{source.target_bucket}'}}/{{s3_key}}'
        }})
    }}
'''
        
        # Create EventBridge rule for scheduling
        events = boto3.client('events')
        
        rule_response = events.put_rule(
            Name=f"api-ingestion-{source.source_id}",
            ScheduleExpression=source.ingestion_schedule,
            State='ENABLED',
            Description=f"Scheduled API ingestion for {source.source_id}"
        )
        
        # Add Lambda as target
        events.put_targets(
            Rule=f"api-ingestion-{source.source_id}",
            Targets=[{
                'Id': '1',
                'Arn': source.connection_config['lambda_arn'],
                'Input': json.dumps({'source_id': source.source_id})
            }]
        )
        
        return rule_response
    
    def _get_s3_target_endpoint(self, source: DataSource):
        """Create DMS S3 target endpoint"""
        
        endpoint_config = {
            'EndpointIdentifier': f"s3-target-{source.source_id}",
            'EndpointType': 'target',
            'EngineName': 's3',
            'S3Settings': {
                'BucketName': source.target_bucket,
                'BucketFolder': source.target_prefix,
                'CompressionType': 'gzip',
                'DataFormat': 'parquet',
                'DatePartitionEnabled': True,
                'DatePartitionSequence': 'YYYYMMDD',
                'EncryptionMode': 'SSE_KMS',
                'ServerSideEncryptionKmsKeyId': source.connection_config['kms_key_arn'],
                'ParquetVersion': 'parquet-2-0',
                'EnableStatistics': True,
                'CdcPath': 'cdc',
                'CdcInsertsOnly': False,
                'TimestampColumnName': 'dms_timestamp',
                'ParquetTimestampInMillisecond': True
            }
        }
        
        response = self.dms_client.create_endpoint(**endpoint_config)
        return response['Endpoint']['EndpointArn']

### **2. Storage Layer - Multi-Zone Architecture**

```python
class DataLakeStorageManager:
    """
    Manages the Bronze-Silver-Gold storage architecture
    """
    
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3')
        
        # Zone definitions
        self.zones = {
            'bronze': {
                'prefix': 'bronze',
                'description': 'Raw data - immutable, original format',
                'retention_days': 2555,  # 7 years
                'storage_class': 'STANDARD_IA',  # Infrequent Access
                'lifecycle_rules': [
                    {
                        'Id': 'bronze-to-glacier',
                        'Status': 'Enabled',
                        'Transitions': [
                            {'Days': 90, 'StorageClass': 'GLACIER'},
                            {'Days': 365, 'StorageClass': 'DEEP_ARCHIVE'}
                        ]
                    }
                ]
            },
            'silver': {
                'prefix': 'silver',
                'description': 'Curated data - validated, deduplicated, enriched',
                'retention_days': 730,  # 2 years
                'storage_class': 'STANDARD',
                'format': 'parquet',
                'compression': 'snappy',
                'partitioning': ['year', 'month', 'day']
            },
            'gold': {
                'prefix': 'gold',
                'description': 'Analytics-ready - aggregated, denormalized',
                'retention_days': 365,  # 1 year
                'storage_class': 'STANDARD',
                'format': 'parquet',
                'compression': 'snappy',
                'optimization': {
                    'enable_z_ordering': True,
                    'enable_delta_lake': True,
                    'enable_bloom_filters': True
                }
            }
        }
    
    def setup_bucket_structure(self):
        """Initialize data lake bucket with proper structure and policies"""
        
        # Create bucket if not exists
        try:
            self.s3_client.create_bucket(Bucket=self.bucket_name)
        except self.s3_client.exceptions.BucketAlreadyOwnedByYou:
            pass
        
        # Enable versioning
        self.s3_client.put_bucket_versioning(
            Bucket=self.bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        
        # Enable server-side encryption
        self.s3_client.put_bucket_encryption(
            Bucket=self.bucket_name,
            ServerSideEncryptionConfiguration={
                'Rules': [{
                    'ApplyServerSideEncryptionByDefault': {
                        'SSEAlgorithm': 'aws:kms',
                        'KMSMasterKeyID': 'arn:aws:kms:us-east-1:123456789012:key/...'
                    },
                    'BucketKeyEnabled': True
                }]
            }
        )
        
        # Configure lifecycle policies
        lifecycle_rules = []
        for zone_name, zone_config in self.zones.items():
            if 'lifecycle_rules' in zone_config:
                for rule in zone_config['lifecycle_rules']:
                    rule['Filter'] = {'Prefix': f"{zone_config['prefix']}/"}
                    lifecycle_rules.append(rule)
        
        self.s3_client.put_bucket_lifecycle_configuration(
            Bucket=self.bucket_name,
            LifecycleConfiguration={'Rules': lifecycle_rules}
        )
        
        # Set up access logging
        self.s3_client.put_bucket_logging(
            Bucket=self.bucket_name,
            BucketLoggingStatus={
                'LoggingEnabled': {
                    'TargetBucket': f"{self.bucket_name}-logs",
                    'TargetPrefix': 'access-logs/'
                }
            }
        )
        
        # Enable intelligent tiering
        self.s3_client.put_bucket_intelligent_tiering_configuration(
            Bucket=self.bucket_name,
            Id='EntireDataLake',
            IntelligentTieringConfiguration={
                'Id': 'EntireDataLake',
                'Status': 'Enabled',
                'Tierings': [
                    {'Days': 90, 'AccessTier': 'ARCHIVE_ACCESS'},
                    {'Days': 180, 'AccessTier': 'DEEP_ARCHIVE_ACCESS'}
                ]
            }
        )
    
    def optimize_storage(self, zone: str, dataset: str):
        """
        Optimize storage using compaction and file size optimization
        """
        
        # Use Spark for file compaction
        from pyspark.sql import SparkSession
        
        spark = SparkSession.builder \
            .appName("DataLake-Compaction") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.sql.files.maxPartitionBytes", "134217728") \
            .getOrCreate()
        
        zone_config = self.zones[zone]
        source_path = f"s3://{self.bucket_name}/{zone_config['prefix']}/{dataset}/"
        
        # Read data
        df = spark.read.parquet(source_path)
        
        # Optimize file size (target: 128 MB - 1 GB per file)
        df_optimized = df.repartition(
            df.count() // 1000000  # ~1M rows per partition
        )
        
        # Write back with optimization
        temp_path = f"s3://{self.bucket_name}/temp/{zone}/{dataset}/"
        
        df_optimized.write \
            .mode("overwrite") \
            .option("compression", zone_config.get('compression', 'snappy')) \
            .option("parquet.block.size", str(256 * 1024 * 1024)) \
            .parquet(temp_path)
        
        # Atomic swap
        self._atomic_swap(source_path, temp_path)
        
        return {
            'original_files': df.rdd.getNumPartitions(),
            'optimized_files': df_optimized.rdd.getNumPartitions(),
            'compression_ratio': self._calculate_compression_ratio(source_path, temp_path)
        }
    
    def _atomic_swap(self, old_path: str, new_path: str):
        """Atomically replace old data with new optimized data"""
        
        import time
        backup_path = f"{old_path.rstrip('/')}_backup_{int(time.time())}/"
        
        # Rename old to backup
        self._s3_rename(old_path, backup_path)
        
        # Rename new to production
        self._s3_rename(new_path, old_path)
        
        # Delete backup after verification
        # In production, keep backup for 24-48 hours
        self._s3_delete(backup_path)
```

### **3. Metadata & Catalog - AWS Glue Integration**

```python
class DataCatalogManager:
    """
    Manages metadata catalog using AWS Glue Data Catalog
    """
    
    def __init__(self):
        self.glue_client = boto3.client('glue')
        self.catalog_database = 'data_lake_catalog'
    
    def create_database(self):
        """Create Glue database for data lake"""
        
        try:
            self.glue_client.create_database(
                DatabaseInput={
                    'Name': self.catalog_database,
                    'Description': 'Data Lake Catalog - all datasets',
                    'LocationUri': 's3://my-data-lake/',
                    'Parameters': {
                        'created_by': 'data-platform-team',
                        'environment': 'production'
                    }
                }
            )
        except self.glue_client.exceptions.AlreadyExistsException:
            pass
    
    def register_dataset(self, zone: str, dataset_name: str, schema: List[Dict], 
                        partitions: List[str], location: str):
        """
        Register new dataset in catalog with schema and partitioning
        """
        
        # Convert schema to Glue columns
        columns = []
        for field in schema:
            columns.append({
                'Name': field['name'],
                'Type': self._map_type_to_glue(field['type']),
                'Comment': field.get('description', '')
            })
        
        # Partition keys
        partition_keys = []
        for partition in partitions:
            partition_keys.append({
                'Name': partition,
                'Type': 'string'  # Partitions are typically strings
            })
        
        # Create table
        table_input = {
            'Name': f"{zone}_{dataset_name}",
            'Description': f"{zone} zone - {dataset_name} dataset",
            'StorageDescriptor': {
                'Columns': columns,
                'Location': location,
                'InputFormat': 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat',
                'OutputFormat': 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat',
                'Compressed': True,
                'SerdeInfo': {
                    'SerializationLibrary': 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe',
                    'Parameters': {
                        'serialization.format': '1'
                    }
                },
                'StoredAsSubDirectories': False
            },
            'PartitionKeys': partition_keys,
            'TableType': 'EXTERNAL_TABLE',
            'Parameters': {
                'classification': 'parquet',
                'compressionType': 'snappy',
                'EXTERNAL': 'TRUE',
                'parquet.compression': 'SNAPPY',
                'projection.enabled': 'true',  # Partition projection for fast queries
                'projection.year.type': 'integer',
                'projection.year.range': '2020,2030',
                'projection.month.type': 'integer',
                'projection.month.range': '1,12',
                'projection.month.digits': '2',
                'projection.day.type': 'integer',
                'projection.day.range': '1,31',
                'projection.day.digits': '2',
                'storage.location.template': f"{location}/year=${{year}}/month=${{month}}/day=${{day}}"
            }
        }
        
        try:
            self.glue_client.create_table(
                DatabaseName=self.catalog_database,
                TableInput=table_input
            )
        except self.glue_client.exceptions.AlreadyExistsException:
            # Update existing table
            self.glue_client.update_table(
                DatabaseName=self.catalog_database,
                TableInput=table_input
            )
    
    def create_crawler(self, dataset_name: str, s3_path: str):
        """
        Create Glue crawler for automatic schema detection
        """
        
        crawler_config = {
            'Name': f"crawler-{dataset_name}",
            'Role': 'arn:aws:iam::123456789012:role/GlueCrawlerRole',
            'DatabaseName': self.catalog_database,
            'Targets': {
                'S3Targets': [{
                    'Path': s3_path,
                    'Exclusions': ['**_temporary/**', '**_spark_metadata/**']
                }]
            },
            'SchemaChangePolicy': {
                'UpdateBehavior': 'UPDATE_IN_DATABASE',
                'DeleteBehavior': 'LOG'
            },
            'RecrawlPolicy': {
                'RecrawlBehavior': 'CRAWL_NEW_FOLDERS_ONLY'
            },
            'LineageConfiguration': {
                'CrawlerLineageSettings': 'ENABLE'
            },
            'Configuration': json.dumps({
                'Version': 1.0,
                'CrawlerOutput': {
                    'Partitions': {'AddOrUpdateBehavior': 'InheritFromTable'},
                    'Tables': {'AddOrUpdateBehavior': 'MergeNewColumns'}
                },
                'Grouping': {
                    'TableGroupingPolicy': 'CombineCompatibleSchemas'
                }
            }),
            'Schedule': 'cron(0 */6 * * ? *)'  # Every 6 hours
        }
        
        try:
            self.glue_client.create_crawler(**crawler_config)
        except self.glue_client.exceptions.AlreadyExistsException:
            self.glue_client.update_crawler(**crawler_config)
        
        # Start crawler
        self.glue_client.start_crawler(Name=f"crawler-{dataset_name}")
    
    def _map_type_to_glue(self, data_type: str) -> str:
        """Map generic types to Glue/Hive types"""
        
        type_mapping = {
            'string': 'string',
            'int': 'int',
            'long': 'bigint',
            'float': 'float',
            'double': 'double',
            'boolean': 'boolean',
            'timestamp': 'timestamp',
            'date': 'date',
            'array': 'array<string>',
            'map': 'map<string,string>',
            'struct': 'struct<>'
        }
        
        return type_mapping.get(data_type.lower(), 'string')
```

*Due to character limits, I'll continue with the remaining critical components in the next file...*

---

## 🎓 Key Takeaways for Interviews

### **Must-Mention Points:**
1. **3-Zone Architecture** (Bronze/Silver/Gold) for data maturity
2. **Separation of storage and compute** for cost optimization
3. **Schema evolution** and backward compatibility
4. **Partition pruning** for query performance
5. **Data lifecycle management** (hot/warm/cold storage)
6. **Metadata catalog** for discoverability
7. **Security layers** (encryption, access control, audit)
8. **Cost optimization** (compression, format, storage class)

### **Common Pitfalls to Avoid:**
❌ Not partitioning data (full table scans)  
❌ Using JSON instead of Parquet (10x cost increase)  
❌ No compaction strategy (small files problem)  
❌ Missing data quality checks  
❌ No schema registry (breaking changes)  
❌ Inadequate monitoring and alerting  

### **Scale Calculations:**
```
Storage: 100 TB/day × 365 days = 36.5 PB/year
With compression (3:1): ~12 PB/year
Monthly cost (S3 Standard-IA): 12 PB × $0.0125/GB = $15,360/month
After lifecycle to Glacier: ~$3,000/month
```

**This scenario demonstrates FAANG-level data platform thinking - essential for 40 LPA interviews!** 🎯
