This prototype contains dockerized spark and kafka clusters as well as some producers/consumers for testing purposes.

Note: you can view the image terminal outputs using docker desktop and opening the running containers.

### Getting started using makefile (please see makefile for additional information):

1. Ensure that you have docker installed.
2. Start Kafka - for this I am using prebuilt images.
    1. Run `make run_zookeeper` this will start the zookeeper container to coordinate Kafka.
    2. Run `make run_kafka` and `make run_kafka2` to start 2 kafka brokers. 
    3. Optionally run `make run_kafka_ui` to start the ui. This can be accessed at http://localhost:8080.
3. Start Kafka producer with `run_kafka_producer` this will build the image and then start the container. This will make a topic and start producing fake events to the topic. Please view in the Kafka ui.
4. Start Kafka consumer with `run_kafka_consumer` this will build the image and then start the container. Make sure to check the terminal output in docker desktop to ensure messages are being consumed correctly.

5. Start Spark - This requires manually built images.
    1. Build the datastore image and volume using `make build_spark_datastore`.
    2. Build the shared image with `make build_spark`. This image is used by both master and both workers.
    3. Start Spark master with 2 workers using `make run_spark`. Master UI can be accessed at http://localhost:8090.
6. For an example Spark job that opens a csv please run `make run_spark_job`. This will use a csv provided in the datastore.
7. For an example Spark job that reads a kafka topic and then writes to another - please run `make run_kafka_spark_consumer`.

### Inspecting the docker networks:

Run `docker network ls` to list networks.
There should be "host" and "bridge" networks listed.

The docker containers run with `--net=host` should be available in the "host" network while the others will be in the "bridge" network. Please view each network by running the following command: `docker network inspect bridge` or `docker network inspect host`.