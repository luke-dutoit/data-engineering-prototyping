from pyspark.sql import SparkSession
from pyspark.context import SparkContext
from pyspark import SparkFiles

import json
import time
import os

def main():
    print("Docker container started")

    print("Setting up Spark session")

    spark = SparkSession.builder \
        .appName('Spark CSV Example') \
        .master("spark://host.docker.internal:7077") \
        .getOrCreate()

    print("Create example dataframe")

    df = spark.createDataFrame([("luke", 1), ("madiha", 2), ("kevin", 3)])
    df.show()

    print("List files in directory")
    print(os.listdir('/'))
    
    print("Reading from csv")

    sdfData = spark.read.csv("/data/Business-employment-data-september-2022-quarter-csv.csv", header=True, sep=",")

    for col in sdfData.columns:
        sdfData = sdfData.withColumnRenamed(col, col.lower())

    sdfData.show()

    sdfData.createOrReplaceTempView("sample_table")
    df2 = spark.sql("SELECT period, sum(data_value) FROM sample_table group by 1 order by 1")
    df2.show()

    


main()


