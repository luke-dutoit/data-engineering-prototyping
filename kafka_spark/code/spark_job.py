from pyspark.sql import SparkSession
from pyspark.context import SparkContext
from pyspark import SparkFiles

import json
import time
import os


def main():
    print("Docker container started")

    print("Setting up Spark session")


    spark_session = (
            SparkSession.builder.appName("Spark CSV Example")
            .master(os.environ["SPARK_MASTER"])
            .config(
                "spark.cores.max", "2"
            )  # By default this will use all 10 cores available from the spark workers. This will prevent other jobs from running properly as there will be no available cores for them to use.
        )
    
    # These are needed for deployment to kubernetes to allow driver to communicate with workers.
    if os.environ.get("SPARK_DRIVER_HOST"):
        spark_session.config("spark.driver.bindAddress", "0.0.0.0")
        spark_session.config("spark.driver.host", os.environ["SPARK_DRIVER_HOST"])
        spark_session.config("spark.driver.port", os.environ["SPARK_DRIVER_PORT"])
        spark_session.config("spark.driver.blockManager", os.environ["SPARK_DRIVER_PORT"])
        # spark_session.config("spark.submit.deployMode", "client")

    spark = spark_session.getOrCreate()

    print("Create example dataframe")

    df = spark.createDataFrame([("abc", 1), ("def", 2), ("xyz", 3)])
    df.show()

    print("List files in directory")
    print(os.listdir("/"))

    print("Reading from csv")
    # CSV is stored in datastore so it is available to all spark workers.

    sdfData = spark.read.csv(
        "/data/Business-employment-data-september-2022-quarter-csv.csv",
        header=True,
        sep=",",
    )

    print("Rename all columns in csv to be lowercase.")
    for col in sdfData.columns:
        sdfData = sdfData.withColumnRenamed(col, col.lower())

    sdfData.show()

    print("Create temp view and query it using sql.")
    sdfData.createOrReplaceTempView("sample_view")
    df2 = spark.sql(
        "SELECT period, sum(data_value) FROM sample_view group by 1 order by 1"
    )
    df2.show()


main()
