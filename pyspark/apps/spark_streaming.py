import logging as log
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, current_timestamp, lit,struct

# Kafka and Spark Configuration
KAFKA_BROKERS = 'kafka0:29092'
KAFKA_CHECKPOINT = 'checkpoint'
ACME_PYSPARK_APP_NAME = 'AcmeSparkStreaming'
CLICKSTREAM_RAW_EVENTS_TOPIC = 'acme.clickstream.raw.events'
CLICKSTREAM_LATEST_EVENTS_TOPIC = 'acme.clickstream.latest.events'
checkpoint_directory = "/opt/spark-checkpoints/my-checkpoint"

packages = [
    'org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0',
    'org.apache.spark:spark-avro_2.12:3.3.0'
]

# Initialize logging
log.basicConfig(level=log.INFO,
                format='%(asctime)s [%(levelname)s] [%(name)8s] %(message)s')
logger = log.getLogger('acme_pyspark')

def initialize_spark_session(app_name):
    """
    Initialize the Spark Session with provided configurations.
    """
    try:
        spark = SparkSession.builder \
            .appName(app_name) \
            .master('spark://spark-master:7077') \
            .config('spark.jars.packages', ','.join(packages)) \
            .getOrCreate()

        spark.sparkContext.setLogLevel("WARN")
        logger.info('Spark session initialized successfully')
        return spark

    except Exception as e:
        logger.error(f"Spark session initialization failed. Error: {e}")
        return None

def get_streaming_dataframe(spark, brokers, topic):
    """
    Get a streaming dataframe from Kafka with considerations for potential data loss.
    """
    try:
        df = spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", brokers) \
            .option("subscribe", topic) \
            .option("startingOffsets", "latest") \
            .option("failOnDataLoss", "false") \
            .load()

        logger.info(f"Streaming DataFrame loaded for topic: {topic}")
        return df
    except Exception as e:
        logger.error(f"Failed to create streaming DataFrame: {e}")
        return None

def transform_streaming_data(df, schema_registry_url, schema_id):
    """
    Transform the initial dataframe to include additional metadata and deserialize JSON.
    """
    # Assuming schema fetch and JSON parsing setup (simplified here)
    spark= initialize_spark_session(ACME_PYSPARK_APP_NAME)
    json_schema = spark.read.format("avro").option("avroSchema", f"{schema_registry_url}/{schema_id}").load().schema

        # Transform the data by deserializing JSON from the Kafka message
    transformed_df = df.select(
        from_json(col("value").cast("string"), json_schema).alias("data"),
        col("timestamp").alias("kafka_timestamp")
    ).select(
        "data.*",
        struct(
            col("package_id").alias("correlation_id"),  # Extract and rename package_id as correlation_id
            lit(schema_id).alias("schema_id"),  # Include schema_id
            current_timestamp().alias("ingested_timestamp")  # Use current_timestamp or kafka_timestamp based on requirement
        ).alias("metadata")  # Create a structured column 'metadata' containing the above fields
    )
    
    return transformed_df

def initiate_streaming_to_topic(df, brokers, topic, checkpoint):
    """
    Start streaming the transformed data to the specified Kafka topic.
    """
    try:
        query = df \
            .writeStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", brokers) \
            .option("topic", topic) \
            .option("checkpointLocation", checkpoint) \
            .start()
        query.awaitTermination()
        logger.info("Streaming initiated...")
    except Exception as e:
        logger.error(f"Failed to initiate streaming: {e}")

def main():
    spark = SparkSession.builder \
        .appName("AcmeSparkStreamingToMinIOandKafka") \
        .getOrCreate()

    # Set up configuration to connect to MinIO, treating it like an S3 bucket
    hadoop_conf = spark._jsc.hadoopConfiguration()
    hadoop_conf.set("fs.s3a.access.key", "minioadmin")
    hadoop_conf.set("fs.s3a.secret.key", "minioadmin")
    hadoop_conf.set("fs.s3a.endpoint", "http://minio-storage:9000")
    hadoop_conf.set("fs.s3a.connection.ssl.enabled", "false")
    hadoop_conf.set("fs.s3a.path.style.access", "true")

    # Example DataFrame loading from Kafka topic
    df = spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", "kafka0:29092") \
        .option("subscribe", "acme.clickstream.raw.events") \
        .load()

    # Transform and select data as necessary
    transformed_df = df.selectExpr("CAST(value AS STRING)")

    # Write to MinIO bucket
    minio_query = transformed_df.writeStream \
        .format("parquet") \
        .option("checkpointLocation", checkpoint_directory + "/minio") \
        .option("path", "s3a://acme.eu-west-1.stg.data.lake/clickstream-data") \
        .start()

    # Write to Kafka topic
    kafka_query = transformed_df.selectExpr("CAST(value AS STRING) AS value") \
        .writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka0:29092") \
        .option("topic", "acme.clickstream.latest.events") \
        .option("checkpointLocation", checkpoint_directory + "/kafka") \
        .start()

    minio_query.awaitTermination()
    kafka_query.awaitTermination()

if __name__ == '__main__':
    main()
