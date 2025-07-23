#!/bin/bash

# Click Streaming Data Pipeline - Cleanup Script

echo "🧹 Cleaning up Click Streaming Data Pipeline..."

# Stop all containers
echo "🛑 Stopping all containers..."
docker compose down

# Remove volumes if requested
if [ "$1" = "--volumes" ] || [ "$1" = "-v" ]; then
    echo "🗑️ Removing volumes..."
    docker compose down -v
    
    echo "🧼 Removing Docker images..."
    docker rmi acme-kafka-connect acme-spark 2>/dev/null || true
fi

# Clean up logs
if [ -d "logs" ]; then
    echo "📝 Cleaning up logs..."
    rm -rf logs/*
fi

echo "✅ Cleanup completed!"

if [ "$1" = "--volumes" ] || [ "$1" = "-v" ]; then
    echo ""
    echo "⚠️ All data has been removed. You'll need to rebuild custom images on next startup."
fi