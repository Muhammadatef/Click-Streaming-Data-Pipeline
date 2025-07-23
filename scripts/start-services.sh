#!/bin/bash

# Click Streaming Data Pipeline - Service Startup Script
# This script starts the services in the correct order

set -e

echo "🚀 Starting Click Streaming Data Pipeline..."

# Function to check if a service is healthy
wait_for_service() {
    local service_name=$1
    local health_check_cmd=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if eval $health_check_cmd > /dev/null 2>&1; then
            echo "✅ $service_name is ready"
            return 0
        fi
        echo "   Attempt $attempt/$max_attempts - $service_name not ready yet..."
        sleep 10
        ((attempt++))
    done
    
    echo "❌ $service_name failed to start within expected time"
    return 1
}

# Step 1: Start core infrastructure services
echo "📦 Starting core infrastructure..."
docker compose up -d kafka0 schema-registry0 minio

# Wait for Kafka to be ready
wait_for_service "Kafka" "docker exec kafka0 kafka-topics --list --bootstrap-server localhost:9092"

# Wait for Schema Registry to be ready  
wait_for_service "Schema Registry" "curl -f http://localhost:8085/subjects"

# Wait for MinIO to be ready
wait_for_service "MinIO" "curl -f http://localhost:9000/minio/health/ready"

# Step 2: Create Kafka topics
echo "📋 Creating Kafka topics..."
docker exec kafka0 kafka-topics --create --topic acme.clickstream.raw.events --partitions 6 --replication-factor 1 --bootstrap-server localhost:9092 --if-not-exists
docker exec kafka0 kafka-topics --create --topic acme.clickstream.latest.events --partitions 6 --replication-factor 1 --bootstrap-server localhost:9092 --if-not-exists
docker exec kafka0 kafka-topics --create --topic acme.clickstream.invalid.events --partitions 6 --replication-factor 1 --bootstrap-server localhost:9092 --if-not-exists

# Step 3: Start monitoring services
echo "🖥️ Starting monitoring services..."
docker compose up -d kafka-ui rest-proxy ksqldb-server

# Step 4: Build and start custom services (if needed)
echo "🔧 Building custom services..."
if [ ! "$(docker images -q acme-kafka-connect 2> /dev/null)" ]; then
    echo "Building Kafka Connect image..."
    docker compose build kafka-connect-builder
fi

if [ ! "$(docker images -q acme-spark 2> /dev/null)" ]; then
    echo "Building Spark image..."
    docker compose build spark-builder
fi

# Step 5: Start Kafka Connect and Spark services
echo "⚡ Starting processing services..."
docker compose up -d kafka-connect0 spark-master spark-worker-1

echo "🎉 All services started successfully!"
echo ""
echo "🔍 Service URLs:"
echo "   - Kafka UI: http://localhost:8080"
echo "   - MinIO Console: http://localhost:9001 (admin:minioadmin)"
echo "   - Spark UI: http://localhost:18080"
echo "   - Schema Registry: http://localhost:8085"
echo "   - KSQL Server: http://localhost:8088"
echo ""
echo "🚀 You can now start the API server and data generator!"