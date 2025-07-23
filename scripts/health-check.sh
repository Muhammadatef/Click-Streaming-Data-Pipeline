#!/bin/bash

# Click Streaming Data Pipeline - Health Check Script

echo "🏥 Health Check - Click Streaming Data Pipeline"
echo "============================================="

# Function to check service health
check_service() {
    local service_name=$1
    local health_check_cmd=$2
    local url=$3
    
    echo -n "🔍 $service_name: "
    
    if eval $health_check_cmd > /dev/null 2>&1; then
        echo "✅ Running"
        if [ -n "$url" ]; then
            echo "   🌐 $url"
        fi
    else
        echo "❌ Not running"
    fi
}

echo ""
echo "📦 Infrastructure Services:"
check_service "Kafka" "docker exec kafka0 kafka-topics --list --bootstrap-server localhost:9092" "localhost:9092"
check_service "Schema Registry" "curl -f http://localhost:8085/subjects" "http://localhost:8085"
check_service "MinIO" "curl -f http://localhost:9000/minio/health/ready" "http://localhost:9001"

echo ""
echo "🖥️ Monitoring Services:"
check_service "Kafka UI" "curl -f http://localhost:8080" "http://localhost:8080"
check_service "KSQL Server" "curl -f http://localhost:8088/info" "http://localhost:8088"

echo ""
echo "⚡ Processing Services:"
check_service "Spark Master" "curl -f http://localhost:18080" "http://localhost:18080"
check_service "Kafka Connect" "curl -f http://localhost:8083" "http://localhost:8083"

echo ""
echo "🚀 Application Services:"
check_service "API Server" "curl -f http://localhost:60000/ping" "http://localhost:60000"

echo ""
echo "📋 Kafka Topics:"
if docker exec kafka0 kafka-topics --list --bootstrap-server localhost:9092 > /dev/null 2>&1; then
    docker exec kafka0 kafka-topics --list --bootstrap-server localhost:9092 | while read topic; do
        echo "   📝 $topic"
    done
else
    echo "   ❌ Cannot list topics (Kafka not running)"
fi

echo ""
echo "============================================="