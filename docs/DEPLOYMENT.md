# Deployment Guide

## Quick Start

### 1. Prerequisites
```bash
# Check Docker installation
docker --version
docker compose --version

# Ensure minimum resources
# RAM: 8GB+ recommended
# CPU: 4 cores+ recommended
# Disk: 10GB+ free space
```

### 2. Start Infrastructure
```bash
# Clone repository
git clone <repository-url>
cd Click-Streaming-Data-Pipeline-main

# Start all services
make start-services

# Check service health
make health-check
```

### 3. Start Application Components
```bash
# Terminal 1: Start API server
make start-api

# Terminal 2: Start data generator
make start-generator

# Terminal 3: Run Spark streaming job
make run-spark
```

### 4. Verify Deployment
```bash
# Check all services are running
make health-check

# View service logs
make logs

# Test API endpoint
curl http://localhost:60000/ping
```

## Service Startup Order

The services must be started in the correct order due to dependencies:

1. **Core Infrastructure** (parallel startup)
   - Kafka broker
   - MinIO storage
   - Schema Registry

2. **Dependent Services** (after core is ready)
   - Kafka UI
   - KSQL Server
   - REST Proxy

3. **Processing Services** (after Kafka is ready)
   - Kafka Connect
   - Spark Master & Workers

4. **Application Services** (after infrastructure is ready)
   - Flask API Server
   - Data Generator

## Environment Configuration

### Docker Compose Override
Create `docker-compose.override.yml` for environment-specific settings:

```yaml
services:
  kafka0:
    environment:
      KAFKA_JVM_PERFORMANCE_OPTS: "-Xmx2G -Xms2G"
  
  spark-master:
    environment:
      SPARK_MASTER_MEMORY: "2g"
      SPARK_DRIVER_MEMORY: "1g"
```

### Resource Allocation

#### Minimum Requirements
- **RAM**: 4GB
- **CPU**: 2 cores
- **Disk**: 5GB

#### Recommended Production
- **RAM**: 16GB+
- **CPU**: 8 cores+
- **Disk**: 100GB+ SSD

### Port Configuration

| Service | Default Port | Override Environment |
|---------|--------------|---------------------|
| Kafka | 9092 | KAFKA_PORT |
| Schema Registry | 8085 | SCHEMA_REGISTRY_PORT |
| Kafka UI | 8080 | KAFKA_UI_PORT |
| MinIO | 9000, 9001 | MINIO_PORT |
| Spark UI | 18080 | SPARK_UI_PORT |
| API Server | 60000 | API_PORT |

## Production Deployment

### 1. Infrastructure Setup
```bash
# Create production network
docker network create --driver bridge click-streaming-prod

# Set up persistent volumes
docker volume create kafka-data
docker volume create minio-data
docker volume create spark-checkpoints
```

### 2. Security Configuration
```bash
# Generate SSL certificates
mkdir -p ssl/
openssl req -new -x509 -keyout ssl/server.key -out ssl/server.crt -days 365 -nodes

# Set up authentication
export MINIO_ROOT_USER="admin"
export MINIO_ROOT_PASSWORD="secure-password-123"
```

### 3. Monitoring Setup
```bash
# Enable JMX monitoring
export KAFKA_JMX_OPTS="-Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.authenticate=false"

# Configure log aggregation
export LOG_LEVEL="INFO"
export LOG_FORMAT="json"
```

## Scaling Configuration

### Horizontal Scaling

#### Kafka Scaling
```yaml
# Add more Kafka brokers
kafka1:
  image: confluentinc/cp-kafka:7.6.1
  environment:
    KAFKA_NODE_ID: 2
    KAFKA_CONTROLLER_QUORUM_VOTERS: '1@kafka0:29093,2@kafka1:29093'
```

#### Spark Scaling
```yaml
# Add more Spark workers
spark-worker-2:
  image: acme-spark
  environment:
    SPARK_WORKER_CORES: 4
    SPARK_WORKER_MEMORY: 4g
```

### Vertical Scaling
```yaml
# Increase resource limits
services:
  kafka0:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2'
```

## Health Monitoring

### Service Health Checks
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Monitoring Endpoints

| Service | Health Check URL |
|---------|------------------|
| Kafka UI | http://localhost:8080 |
| Schema Registry | http://localhost:8085/subjects |
| MinIO | http://localhost:9000/minio/health/ready |
| API Server | http://localhost:60000/ping |

## Backup & Recovery

### Data Backup
```bash
# Backup MinIO data
docker exec minio-storage mc mirror /data /backup/minio-$(date +%Y%m%d)

# Backup Kafka topics
docker exec kafka0 kafka-mirror-maker.sh --consumer.config consumer.properties --producer.config producer.properties --whitelist=".*"
```

### Disaster Recovery
```bash
# Stop all services
docker compose down

# Restore from backup
docker volume create minio-data-restored
docker run --rm -v /backup/minio-20240115:/backup -v minio-data-restored:/data alpine cp -r /backup/* /data/

# Start with restored data
docker compose up -d
```

## Troubleshooting

### Common Issues

#### Services Won't Start
```bash
# Check system resources
docker system df
docker system prune

# Check port conflicts
netstat -tulpn | grep :9092
```

#### Performance Issues
```bash
# Monitor resource usage
docker stats

# Check Kafka lag
docker exec kafka0 kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --all-groups
```

#### Data Loss Prevention
```bash
# Enable Kafka durability
export KAFKA_FLUSH_INTERVAL_MS=1000
export KAFKA_LOG_RETENTION_HOURS=168

# Configure Spark checkpointing
export SPARK_CHECKPOINT_INTERVAL=10s
```

## Maintenance

### Regular Tasks
- Monitor disk usage
- Rotate log files
- Update security patches
- Backup critical data

### Performance Tuning
- Adjust JVM heap sizes based on usage
- Optimize Kafka partition count
- Configure Spark parallelism
- Monitor and adjust retention policies