from pyspark.sql import SparkSession
from pyspark.sql.types import MapType, StringType
from pyspark.sql.functions import col, get_json_object

import json
import time

import os


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
        SparkSession.builder.appName("Spark KAFKA Example")
        .master("spark://host.docker.internal:7077")
        .config(
            "spark.jars.packages",
            "org.apache.spark:spark-streaming-kafka-0-10_2.12:3.4.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0",
        )
        .getOrCreate()
    )

    print("spark version:", spark.version)

    print("Reading from Kafka")

    df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", "host.docker.internal:9092")
        .option("subscribe", "test_topic_1")
        .option("checkpointLocation", "/data/checkpoint")
        .load()
    )

    print("vast value as string")
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

    print("write stream")
    sq = (
        sdf.writeStream.format("memory")
        .queryName("this_query")
        .outputMode("append")
        .start()
    )

    print("Select count of rows per first_name")
    first_name_df = (
        sdf.groupBy("first_name")
        .count()
        .selectExpr(
            "CAST(first_name AS STRING) as key", "CAST(count AS STRING) as value"
        )
    )

    print("write stream")
    sq2 = (
        first_name_df.writeStream.format("memory")
        .queryName("this_query2")
        .outputMode("update")
        .start()
    )

    print("write stream to kafka")
    ds = (
        first_name_df.writeStream.format("kafka")
        .option("kafka.bootstrap.servers", "host.docker.internal:9092")
        .option("topic", "pyspark_firstname_count_topic")
        .option("checkpointLocation", "/data/checkpoint")
        .outputMode("update")
        .start()
    )

    print("sleep 30 sec")
    time.sleep(30)

    # print("recent progress")
    # print(sq.recentProgress)

    spark.sql("select * from this_query limit 10").show()
    spark.sql("select * from this_query2 order by value desc limit 10").show()

    print("sleep 30 sec")
    time.sleep(30)

    spark.sql("select * from this_query2 order by value desc limit 10").show()

    print("await termination")
    ds.awaitTermination()

    print("done")


main()