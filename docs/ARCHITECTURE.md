# System Architecture

## Overview

The Click Streaming Data Pipeline is designed as a modern, scalable event processing system that handles real-time clickstream data from web applications.

## Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Client    │    │   REST API      │    │   Apache Kafka  │
│                 │───▶│   (Flask)       │───▶│   (Events)      │
│   Clickstream   │    │   Port: 60000   │    │   Port: 9092    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MinIO         │◀───│  Apache Spark   │◀───│ Schema Registry │
│   (S3 Storage)  │    │  (Processing)   │    │  Port: 8085     │
│   Port: 9000    │    │  Port: 18080    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Lake     │    │   Kafka UI      │    │   KSQL Server   │
│   (Parquet)     │    │   (Monitoring)  │    │   (Analytics)   │
│                 │    │   Port: 8080    │    │   Port: 8088    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Component Responsibilities

### Data Ingestion Layer
- **Flask API Server**: Receives HTTP POST requests with clickstream events
- **Event Validation**: Validates incoming events against Avro schema
- **Kafka Producer**: Publishes validated events to Kafka topics

### Stream Processing Layer
- **Apache Kafka**: Distributed event streaming platform
- **Schema Registry**: Centralized schema management for Avro serialization
- **Kafka Topics**:
  - `acme.clickstream.raw.events`: Raw validated events
  - `acme.clickstream.latest.events`: Processed/enriched events
  - `acme.clickstream.invalid.events`: Schema validation failures

### Data Processing Layer
- **Apache Spark Streaming**: Real-time stream processing engine
- **Data Enrichment**: Adds metadata and correlation IDs
- **Data Transformation**: Converts and structures data for analytics

### Storage Layer
- **MinIO**: S3-compatible object storage for data lake
- **Parquet Format**: Columnar storage format for efficient analytics
- **Data Partitioning**: Time-based partitioning for query optimization

### Monitoring & Analytics Layer
- **Kafka UI**: Web-based monitoring for Kafka ecosystem
- **Spark UI**: Monitoring for Spark jobs and performance
- **KSQL Server**: Stream processing with SQL semantics

## Data Flow

1. **Event Generation**: Web clients generate clickstream events
2. **API Ingestion**: Flask API receives and validates events
3. **Schema Validation**: Events validated against Avro schema
4. **Topic Publishing**: Valid events → raw topic, invalid → invalid topic
5. **Stream Processing**: Spark consumes from raw topic, enriches data
6. **Data Storage**: Processed events stored in MinIO as Parquet files
7. **Analytics Ready**: Data available for real-time and batch analytics

## Scalability Considerations

### Horizontal Scaling
- **Kafka Partitioning**: 6 partitions per topic for parallel processing
- **Spark Workers**: Can scale worker nodes based on processing load
- **API Instances**: Multiple Flask API instances behind load balancer

### Performance Optimization
- **Batch Processing**: Kafka producer batching for throughput
- **Compression**: ZSTD compression for storage efficiency
- **Checkpointing**: Spark checkpointing for fault tolerance

### Fault Tolerance
- **Kafka Replication**: Topic replication for data durability
- **Spark Checkpointing**: Automatic recovery from failures
- **Schema Evolution**: Backward compatible schema changes

## Security Architecture

### Data Protection
- **Schema Validation**: Prevents malformed data injection
- **Network Segmentation**: Services isolated in Docker network
- **Access Control**: MinIO with credential-based access

### Monitoring & Alerting
- **Health Checks**: Automated service health monitoring
- **Log Aggregation**: Centralized logging for troubleshooting
- **Metrics Collection**: Performance and business metrics

## Technology Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| API | Flask | 3.0.3 | REST API server |
| Messaging | Apache Kafka | 7.6.1 | Event streaming |
| Processing | Apache Spark | 3.3.0 | Stream processing |
| Storage | MinIO | Latest | Object storage |
| Schema | Confluent Schema Registry | 7.6.1 | Schema management |
| Monitoring | Kafka UI | Latest | System monitoring |
| Analytics | KSQL | 0.29.0 | Stream analytics |