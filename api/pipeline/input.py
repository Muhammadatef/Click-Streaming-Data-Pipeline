import logging
from uuid import uuid4
import json
import time

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


# Simplified validation for testing without Kafka
def is_valid(data, schema=None):
    """ Simple validation - just check if data has required fields. """
    try:
        if isinstance(data, dict):
            # Basic validation - check for essential fields
            required_fields = ['type', 'package_id', 'event']
            return all(field in data for field in required_fields)
        return False
    except Exception as e:
        logging.error(f'Error validating data: {e}')
        return False

def collect(events):
    correlation_id = str(uuid4())
    logging.info(f'Collecting data with correlation ID: {correlation_id}')
    start_time = time.time()
    
    processed_events = []
    valid_count = 0
    invalid_count = 0

    for data in events:
        # Print the received data
        print("Processing event:", data)

        # Simple validation
        if is_valid(data):
            valid_count += 1
            processed_events.append({
                "status": "valid",
                "data": data,
                "correlation_id": correlation_id
            })
            logging.info(f"Valid event processed: {data.get('id', 'no-id')}")
        else:
            invalid_count += 1
            processed_events.append({
                "status": "invalid",
                "data": data,
                "correlation_id": correlation_id,
                "error": "Missing required fields"
            })
            logging.info(f"Invalid event rejected: {data}")

    elapsed_time = time.time() - start_time
    logging.info(f"Processed {valid_count} valid and {invalid_count} invalid events in {elapsed_time:.3f}s")
    
    return {
        "status": "success",
        "correlation_id": correlation_id,
        "processed_count": len(events),
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "elapsed_time": elapsed_time
    }

