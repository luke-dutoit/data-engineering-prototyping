#!/bin/sh
set -e

if [ "$1" = 'master' ]; then
    echo "Starting spark-master..."
    $SPARK_HOME/bin/spark-class org.apache.spark.deploy.master.Master
elif [ "$1" = 'worker' ]; then
    echo "Starting spark-worker..."
    $SPARK_HOME/bin/spark-class org.apache.spark.deploy.worker.Worker spark://${SPARK_MASTER_HOST}:7077
else
    echo "Unknown command '$1'."
fi