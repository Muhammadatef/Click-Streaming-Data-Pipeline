#!/bin/bash

# Click Streaming Data Pipeline - API Server Startup Script

set -e

echo "🔧 Starting API Server..."

cd "$(dirname "$0")/../api"

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

# Start the server
echo "🚀 Starting Flask API server on port 60000..."
echo "   Health check: http://localhost:60000/ping"
echo "   Event endpoint: http://localhost:60000/collect"
echo ""
echo "Press Ctrl+C to stop the server"

python server.py