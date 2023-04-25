#!/bin/sh
set -e

if [ "$1" = 'master' ]; then
    echo "Starting spark-master..."
    $SPARK_HOME/bin/spark-class org.apache.spark.deploy.master.Master
elif [ "$1" = 'worker' ]; then
    echo "Starting spark-worker..."
    $SPARK_HOME/bin/spark-class org.apache.spark.deploy.worker.Worker spark://host.docker.internal:7077
else
    echo "Unknown command '$1'."
fi