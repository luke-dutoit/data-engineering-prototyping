#!/bin/sh
set -e

if [ "$1" = 'kafka_spark_aggregation' ]; then
    echo "Starting kafka_spark_aggregation..."
    python kafka_spark_aggregation.py
elif [ "$1" = 'kafka_spark_consumer' ]; then
    echo "Starting kafka_spark_consumer..."
    python kafka_spark_consumer.py
else
    echo "Unknown command '$1'."
    ls
fi