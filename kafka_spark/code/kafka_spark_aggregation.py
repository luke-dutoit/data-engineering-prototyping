from pyspark.sql import SparkSession
from pyspark.sql.functions import col, get_json_object
import kafka
import json
import time

import os

# This example reads from kafka stream, aggregates and then writes back into another kafka topic.
# It is separate from the other example since the print outputs of the other example are not shown in this examples terminal output.

# The goal here is to get the first names from the kafka topic and then count them.
# The count per first name is then sent to the output topic.
# The output topic is created here with cleanup policy: compact - please see below for details.

# Since we specify checkpoints - the count is not lost when this container is restarted. 
# Additionally first names should not be counted more than once.


# Create a new topic with cleanup policy compact - this will remove duplicate keys and attempt to only keep at least latest entry for each key.
# max.compaction.lag.ms = 300000 = 5 mins. Please see kafka ui to observe compaction happening at least every 5 mins.
def create_topic(topic_name: str, num_partitions: int, replication_factor: int) -> None:
    print(f"Attempting to create topic '{topic_name}'.")
    try:
        admin_client = kafka.KafkaAdminClient(bootstrap_servers="localhost:9092")
        admin_client.create_topics(
            [
                kafka.admin.NewTopic(
                    name=topic_name,
                    num_partitions=num_partitions,
                    replication_factor=replication_factor,
                    topic_configs={
                        "cleanup.policy": "compact",
                        "max.compaction.lag.ms": 300000,
                    },
                )
            ],
            validate_only=False,
        )
        print("Topic created successfully.")
    except kafka.errors.TopicAlreadyExistsError as e:
        print("Topic already exists.")
        print(e)
    except Exception as e:
        print("Unexpected error detected during topic creation.")
        raise e


def main():
    print("Docker container started")
    print("Creating checkpoint directory if not exists")
    path = "/data/checkpoint"
    exists = os.path.exists(path)
    print(exists)
    if not exists:
        print("does not exist, create directory")
        os.makedirs(path)
    print("create directory done")

    print("Setting up Spark session")
    spark = (
        SparkSession.builder.appName("Spark KAFKA Aggregation Example")
        .master("spark://host.docker.internal:7077")
        .config(
            "spark.jars.packages",
            "org.apache.spark:spark-streaming-kafka-0-10_2.12:3.4.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0",
        )
        .getOrCreate()
    )

    print("Reading from Kafka")
    df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", "host.docker.internal:9092")
        .option("subscribe", "test_topic_1")
        .option("checkpointLocation", "/data/checkpoint")
        .load()
    )

    print("Cast value as string and then unpack first_name, last_name")
    sdf = df.selectExpr(
        "CAST(value AS STRING)", "partition", "offset", "timestamp"
    ).select(
        col("value"),
        get_json_object(col("value"), "$.first_name").alias("first_name"),
        get_json_object(col("value"), "$.last_name").alias("last_name"),
        col("partition"),
        col("offset"),
        col("timestamp"),
    )

    print(
        "Select count of rows per first_name then rename columns to key/value for use in kafka."
    )
    first_name_df = (
        sdf.groupBy("first_name")
        .count()
        .selectExpr(
            "CAST(first_name AS STRING) as key", "CAST(count AS STRING) as value"
        )
    )

    print("Write stream to kafka")
    topic_name = "pyspark_firstname_count_topic"
    create_topic(topic_name, 4, 2)
    ds = (
        first_name_df.writeStream.format("kafka")
        .option("kafka.bootstrap.servers", "host.docker.internal:9092")
        .option("topic", topic_name)
        .option("checkpointLocation", "/data/checkpoint")
        .outputMode("update")
        .start()
    )

    print(
        "Await termination - this prevents job from terminating before stream writing is complete."
    )
    ds.awaitTermination()

    print("Done")


main()
