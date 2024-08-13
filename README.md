# ClickStreaming-Pipeline
## Streaming Data Platform

This project implements a comprehensive data processing pipeline for handling streaming data. It demonstrates how to ingest, validate, enrich, and store streaming events using Kafka, Minio, and Spark Streaming.

## Overview

The platform processes events received in JSON format via a REST API and performs the following tasks:

1. **Ingest Events**: Receive events through a REST API endpoint and send them to Kafka topics.
2. **Validate and Store Events**: Validate events against a predefined schema and store them in Minio.
3. **Enrich and Process Events**: Enrich events with metadata using Spark Streaming and store the enriched events back in Minio.
4. **Optional**: Calculate unique users per day using KSQL and store the results in Minio.

## Architecture

The architecture consists of the following components:

- **Kafka**: For event streaming and processing.
- **Minio**: Local S3-compatible storage service for storing events.
- **Spark**: For processing and enriching events.
- **Schema Registry**: For managing and validating schemas.
- **Kafka Connect**: For integrating with external systems (optional).
- **KSQL**: For stream processing queries (optional).
- **Kafka UI**: For monitoring Kafka topics and messages.

### Docker Compose Services

- **Kafka Broker (`kafka0`)**: The Kafka broker for managing event streams.
- **Schema Registry (`schema-registry0`)**: Manages and validates event schemas.
- **Kafka Connect (`kafka-connect0`)**: Optional service for Kafka Connectors.
- **REST Proxy (`rest-proxy`)**: REST API proxy for Kafka.
- **KSQLDB Server (`ksqldb-server`)**: For executing streaming SQL queries.
- **Kafka UI (`kafka-ui`)**: Web interface for Kafka management.
- **Minio (`minio`)**: S3-compatible storage service for storing events.
- **Spark Master (`spark-master`)**: Manages Spark jobs.
- **Spark Workers (`spark-worker-1`)**: Execute Spark jobs.

## Getting Started

### Prerequisites

- Docker Desktop
- `pipenv` or another virtual environment tool

### Deployment

1. **Start the Platform**

   Run the following command to build and start all services using Docker Compose:

   ```bash
   $ docker compose up -d --build

API Server

    Navigate to the api directory:

    $ cd api

Install dependencies and start the server:

bash

    $ pipenv --python 3.11
    $ pipenv shell
    $ pip install -r requirements.txt
    $ python server

    The server will listen on port 60000 by default.

Generate Data

    Navigate to the generator directory:

    $ cd generator

Install dependencies and run the data generator:

    $ pipenv --python 3.11
    $ pipenv shell
    $ pip install -r requirements.txt
    $ python generator.py

    By default, it will send data to localhost:60000 and read from ../data/events.json. Ensure events.json is unzipped.

Run Spark Streaming

    Access the Spark Master container:

       $ docker exec -it spark-master bash

Run the Spark Streaming job:

    /opt/bitnami/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0 /opt/spark-apps/spark_streaming.py

    You can monitor Spark jobs at http://localhost:18080.

Shutdown the Platform

    To stop and remove all containers, run:

        $ docker compose down

Monitoring

    Kafka UI: http://localhost:8080 for managing and monitoring Kafka topics.
    Minio: http://localhost:9000 for accessing stored events.

Additional Notes

    Schema Validation: Ensure that schema definitions are properly registered in the Schema Registry.
    Kafka Connect: Create and configure Kafka connectors as needed for data integration.
    KSQL: Use KSQL for additional stream processing and querying capabilities.

Requirements

    Docker Desktop
    pipenv or another virtual environment tool

Evaluation Criteria

    Functionality: Ensure all components work as expected.
    Code Quality: Apply good practices and ensure clarity in code.
    Testing: Include tests to validate the functionality.
    Documentation: Provide clear explanations of decisions and instructions for running the project.

Feel free to modify the configurations and implementations according to your requirements. The provided Docker Compose setup allows for easy deployment and testing of the streaming data platform.




This `README.md` includes all essential information for setting up, running, and managing your streaming data platform project. It offers a clear structure and comprehensive instructions for each step of the process.

