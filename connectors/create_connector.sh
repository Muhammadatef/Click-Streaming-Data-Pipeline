#!/bin/bash

# Check if the configuration file path is provided as an argument
if [ $# -eq 0 ]; then
    echo "Usage: $0 <connector_config_file>"
    exit 1
fi

# Extract the configuration file path from the command line arguments
CONFIG_FILE="$1"

# Check if the configuration file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Configuration file '$CONFIG_FILE' not found"
    exit 1
fi

# Send a POST request to create the connector using curl
curl -X POST -H "Content-Type: application/json" --data @"$CONFIG_FILE" http://localhost:8083/connectors

