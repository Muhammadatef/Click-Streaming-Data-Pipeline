import logging
from uuid import uuid4
from confluent_kafka.avro import AvroProducer
from confluent_kafka.avro.serializer import SerializerError
import json
import avro.schema
from io import BytesIO
import fastavro
import time
import zstandard as zstd
from avro.io import DatumWriter, BinaryEncoder

OK = {"status": "success"}

# Avro schema for the data
key_schema = """
{
  "type": "record",
  "name": "EventKey",
  "fields": [
    {
      "name": "id",
      "type": "long"
    }
  ]
}
"""
value_schema = """
{
  "type": "record",
  "name": "EventValue",
  "fields": [
    {
      "name": "type",
      "type": "string"
    },
    {
      "name": "package_id",
      "type": "string"
    },
    {
      "name": "event",
      "type": {
        "type": "record",
        "name": "EventDetails",
        "fields": [
          {
            "name": "user_agent",
            "type": "string"
          },
          {
            "name": "ip",
            "type": "string"
          },
          {
            "name": "customer_id",
            "type": ["long", "null"],
            "default": null
          },
          {
            "name": "timestamp",
            "type": "string"
          },
          {
            "name": "page",
            "type": ["string", "null"],
            "default": null
          },
          {
            "name": "query",
            "type": ["string", "null"],
            "default": null
          },
          {
            "name": "product",
            "type": ["long", "null"],
            "default": null
          },
          {
            "name": "referrer",
            "type": ["string", "null"],
            "default": null
          },
          {
            "name": "position",
            "type": ["long", "null"],
            "default": null
          }
        ]
      }
    }
  ]
}
"""


# Parse schemas
key_schema = avro.schema.parse(key_schema)
value_schema = avro.schema.parse(value_schema)

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
raw_topic = 'acme.clickstream.raw.events'
invalid_topic = 'acme.clickstream.invalid.events'
SCHEMA_REGISTRY_URL = 'http://localhost:8085'

# Create AvroProducer with both key and value schemas
avro_producer = AvroProducer({
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'schema.registry.url': SCHEMA_REGISTRY_URL,
    'queue.buffering.max.messages': 200000,
    'queue.buffering.max.kbytes': 1024000,
    'batch.size': 500000,
    'linger.ms': 100,
    'compression.type': 'zstd',
    'message.timeout.ms': 300000,
    'acks': 'all',
    'max.in.flight.requests.per.connection': 5,
    'retries': 10,
    'retry.backoff.ms': 200
}, default_key_schema=key_schema, default_value_schema=value_schema)

def is_valid(data, schema):
    """ Validate data against schema. """
    try:
        bytes_writer = BytesIO()
        writer = DatumWriter(schema)
        encoder = BinaryEncoder(bytes_writer)
        writer.write(data, encoder)
        return True
    except Exception as e:
        logging.error(f'Error validating data: {e}')
        return False

def collect(events):
    correlation_id = str(uuid4())
    logging.info(f'Collecting data with correlation ID: {correlation_id}')
    start_time = time.time()

    for data in events:
        key = {"id": data['id']}
        value = {k: v for k, v in data.items() if k != 'id'}

        # Print the row data before sending to Kafka
        print("Sending data to Kafka:", {"key": key, "value": value})

        # Validate both key and value against their respective schemas
        if is_valid(key, key_schema) and is_valid(value, value_schema):
            avro_producer.produce(topic=raw_topic, key=key, value=value)
            logging.info(f"Data sent to raw_topic: {value}")
        else:
            avro_producer.produce(topic=invalid_topic, key=key, value=value)
            logging.info(f"Data sent to invalid_topic: {value}")

        avro_producer.poll(0)  # Poll to process delivery callback

    avro_producer.flush()  # Ensure all messages are sent before finishing
    elapsed_time = time.time() - start_time
    logging.info(f"Elapsed time: {elapsed_time}")
    return {"status": "success"}

