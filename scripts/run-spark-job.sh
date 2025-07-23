#!/bin/bash

# Click Streaming Data Pipeline - Spark Job Runner

set -e

echo "⚡ Running Spark Streaming Job..."

# Check if Spark Master is running
echo "🔍 Checking if Spark Master is running..."
if ! docker ps | grep -q spark-master; then
    echo "❌ Spark Master is not running"
    echo "   Please start services first using: ./scripts/start-services.sh"
    exit 1
fi

echo "✅ Spark Master is running"

# Submit the Spark job
echo "🚀 Submitting Spark streaming job..."
echo "   Monitor progress at: http://localhost:18080"

docker exec -it spark-master /opt/bitnami/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.apache.hadoop:hadoop-aws:3.2.0 \
    --conf spark.sql.adaptive.enabled=false \
    --conf spark.sql.adaptive.coalescePartitions.enabled=false \
    /opt/spark-apps/spark_streaming.py

echo "✅ Spark job completed"