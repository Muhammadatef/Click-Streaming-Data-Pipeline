# Click Streaming Data Pipeline
## Real-time Event Processing Platform

A comprehensive streaming data pipeline that demonstrates real-time event ingestion, validation, enrichment, and storage using modern data engineering tools. The platform handles clickstream events from web applications and processes them through a robust, scalable architecture.

## 📋 Overview

This project implements an end-to-end streaming data pipeline that:

1. **🔄 Event Ingestion**: Receives clickstream events via REST API
2. **✅ Schema Validation**: Validates events against Avro schemas
3. **📊 Stream Processing**: Enriches data using Apache Spark Streaming
4. **💾 Data Storage**: Stores processed data in MinIO (S3-compatible storage)
5. **🔍 Real-time Analytics**: Enables real-time querying with KSQL
6. **📈 Monitoring**: Provides comprehensive observability through Kafka UI                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 

## 🏗️ Architecture

### Core Components

- **🚀 Apache Kafka**: Event streaming platform and message broker
- **🗄️ MinIO**: S3-compatible object storage for data lake
- **⚡ Apache Spark**: Distributed processing engine for stream analytics
- **🔧 Schema Registry**: Centralized schema management and validation
- **🔌 Kafka Connect**: Data integration framework
- **📊 KSQL**: Stream processing with SQL semantics
- **🖥️ Kafka UI**: Web-based monitoring and management interface

### Data Flow Architecture

```
[Web App] → [REST API] → [Kafka] → [Spark Streaming] → [MinIO]
    ↓           ↓           ↓            ↓              ↓
[Events]    [Validation] [Topics]   [Enrichment]   [Storage]
```

### Service Architecture

| Service | Port | Purpose | Dependencies |
|---------|------|---------|--------------|
| **kafka0** | 9092 | Message broker and event streaming | None |
| **schema-registry0** | 8085 | Schema management and validation | kafka0 |
| **kafka-connect0** | 8083 | Data integration framework | kafka0, schema-registry0 |
| **rest-proxy** | 8082 | REST API proxy for Kafka | kafka0 |
| **ksqldb-server** | 8088 | Stream processing with SQL | kafka0, schema-registry0 |
| **kafka-ui** | 8080 | Web-based monitoring interface | kafka0, schema-registry0 |
| **minio** | 9000, 9001 | S3-compatible object storage | None |
| **spark-master** | 18080, 7077 | Spark cluster manager | None |
| **spark-worker-1** | 28081, 7001 | Spark job execution | spark-master |

## 🚀 Quick Start

### Prerequisites

- **Docker Desktop** (with Docker Compose)
- **Python 3.11+**
- **pip** or **pipenv**
- **8GB+ RAM** (recommended for Spark processing)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd Click-Streaming-Data-Pipeline-main
```

### 2. Start Infrastructure Services

```bash
# Start all services in detached mode
docker compose up -d --build

# Verify all services are running
docker compose ps
```

### 3. Create Sample Data

```bash
# Create data directory and sample events file
mkdir -p data
echo '{"id": 1, "type": "click", "package_id": "test-1", "event": {"user_agent": "Mozilla/5.0", "ip": "192.168.1.1", "customer_id": 12345, "timestamp": "2024-01-01T00:00:00Z", "page": "/home", "query": null, "product": null, "referrer": "https://google.com", "position": null}}' > data/events.json
```

### 4. Setup and Start API Server

```bash
cd api
pip install -r requirements.txt
python server.py
```
*The API server will start on http://localhost:60000*

### 5. Generate and Send Events

```bash
# In a new terminal
cd generator
pip install -r requirements.txt
python generator.py
```

### 6. Run Spark Streaming Job

```bash
# Create Kafka topics first
docker exec -it kafka0 kafka-topics --create --topic acme.clickstream.raw.events --partitions 6 --replication-factor 1 --bootstrap-server localhost:9092
docker exec -it kafka0 kafka-topics --create --topic acme.clickstream.latest.events --partitions 6 --replication-factor 1 --bootstrap-server localhost:9092

# Run Spark job
docker exec -it spark-master /opt/bitnami/spark/bin/spark-submit \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.apache.hadoop:hadoop-aws:3.2.0 \
    /opt/spark-apps/spark_streaming.py
```

## 🔍 Monitoring & Management

### Web Interfaces

- **🖥️ Kafka UI**: http://localhost:8080 - Monitor topics, consumers, and messages
- **📊 Spark UI**: http://localhost:18080 - Monitor Spark jobs and performance
- **🗄️ MinIO Console**: http://localhost:9001 - Manage object storage (admin:minioadmin)
- **⚙️ KSQL Server**: http://localhost:8088 - Stream processing queries

### Health Checks

```bash
# Check API server health
curl http://localhost:60000/ping

# List Kafka topics
docker exec -it kafka0 kafka-topics --list --bootstrap-server localhost:9092

# Check MinIO buckets
curl -u minioadmin:minioadmin http://localhost:9000/
```

## 🛠️ Development & Testing

### Project Structure

```
├── api/                    # REST API server
│   ├── pipeline/          # Event processing logic
│   ├── server.py          # Flask application
│   └── requirements.txt   # Python dependencies
├── generator/             # Event data generator
├── pyspark/              # Spark streaming applications
│   └── apps/
├── docker/               # Custom Docker images
├── schemas/              # Avro schema definitions
├── connectors/           # Kafka Connect configurations
├── topics/               # Topic creation scripts
└── docker-compose.yaml   # Service orchestration
```

### Running Tests

```bash
# Run API tests
cd api
python -m pytest test/

# Test event generation
cd generator
python generator.py --reset http://localhost:60000 ../data/events.json
```

## 📊 Data Schema

### Event Structure

```json
{
  "id": 12345,
  "type": "click|view|purchase",
  "package_id": "uuid4-correlation-id",
  "event": {
    "user_agent": "Mozilla/5.0...",
    "ip": "192.168.1.100",
    "customer_id": 98765,
    "timestamp": "2024-01-01T12:00:00Z",
    "page": "/product/123",
    "query": "search terms",
    "product": 123,
    "referrer": "https://example.com",
    "position": 1
  }
}
```

## 🔧 Configuration

### Environment Variables

```bash
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
SCHEMA_REGISTRY_URL=http://localhost:8085

# MinIO Configuration  
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_ENDPOINT=http://localhost:9000

# API Configuration
API_PORT=60000
```

## 🚨 Troubleshooting

### Common Issues

1. **Services not starting**: Check Docker resources and port conflicts
2. **Kafka connection errors**: Verify Kafka is fully started before other services
3. **Schema validation failures**: Check Avro schema compatibility
4. **Spark job failures**: Ensure adequate memory allocation

### Cleanup & Reset

```bash
# Stop all services
docker compose down

# Remove all containers and volumes
docker compose down -v

# Clean up Docker resources
docker system prune -a
```

## 🏆 Production Considerations

- **Security**: Implement proper authentication and authorization
- **Scalability**: Configure multiple Kafka partitions and Spark workers  
- **Monitoring**: Add comprehensive logging and alerting
- **Backup**: Implement data backup strategies for MinIO
- **Network**: Use proper network segmentation and security groups

