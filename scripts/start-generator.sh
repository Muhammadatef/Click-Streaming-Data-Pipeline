#!/bin/bash

# Click Streaming Data Pipeline - Data Generator Startup Script

set -e

echo "📊 Starting Data Generator..."

cd "$(dirname "$0")/../generator"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📋 Installing dependencies..."
pip install -r requirements.txt

# Check if API server is running
echo "🔍 Checking if API server is running..."
if ! curl -s http://localhost:60000/ping > /dev/null; then
    echo "❌ API server is not running at http://localhost:60000"
    echo "   Please start the API server first using: ./scripts/start-api.sh"
    exit 1
fi

echo "✅ API server is running"

# Start the generator
echo "🚀 Starting event generator..."
echo "   Sending events to: http://localhost:60000"
echo "   Reading from: ../data/events.json"
echo ""
echo "Press Ctrl+C to stop the generator"

python generator.py http://localhost:60000 ../data/events.json