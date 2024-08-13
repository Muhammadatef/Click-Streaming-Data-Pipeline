#!/bin/bash

# Kafka container name
KAFKA_CONTAINER="kafka0"

# Kafka bin directory path inside the container
KAFKA_BIN_PATH="/usr/bin"

# Topics configuration file path on the host
TOPICS_FILE="./topics/clickstream"

# Ensure the topics file exists
if [ ! -f "$TOPICS_FILE" ]; then
    echo "Topics file does not exist: $TOPICS_FILE"
    exit 1
fi

# Read from the topics file and create topics
while IFS=',' read -r topic partitions replicas
do
    # Check if any variable is empty
    if [ -z "$topic" ] || [ -z "$partitions" ] || [ -z "$replicas" ]; then
        echo "Invalid entry in topics file: $topic, $partitions, $replicas"
        continue
    fi

    # Construct the Kafka topic creation command
    CREATE_CMD="${KAFKA_BIN_PATH}/kafka-topics.sh --create --bootstrap-server localhost:9092 \
        --replication-factor $replicas --partitions $partitions --topic $topic"

    # Execute the command inside the Kafka container
    docker exec -it $KAFKA_CONTAINER bash -c "$CREATE_CMD"

    # Check if the topic creation was successful
    if [ $? -eq 0 ]; then
        echo "Successfully created topic: $topic"
    else
        echo "Failed to create topic: $topic"
    fi

done < "$TOPICS_FILE"
