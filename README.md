This prototype contains dockerized spark and kafka clusters as well as some producers/consumers for testing purposes.

Note: you can view the image terminal outputs using docker desktop and opening the running containers.

### Getting started simple using  make to build images and docker-compose to run them.

1. Ensure that you have docker and make installed.
2. Run `make build_all` to build all images.
3. Run `docker compose up -d` to run all containers.
4. Cleanup: Run `docker compose down` to stop and remove containers.
    Alternatively: Run `docker rm -f $(docker ps -a -q)` to remove containers.
5. Cleanup: Run `docker volume rm $(docker volume ls -q)` to remove volumes.


### Getting started using makefile (please see makefile for additional information):
Note: This is an alternative process, please cleanup the above process containers and volumes before starting.

1. Ensure that you have docker and make installed.
2. Start Kafka - for this I am using prebuilt images.
    1. Run `make run_zookeeper` this will start the zookeeper container to coordinate Kafka.
    2. Run `make run_kafka` and `make run_kafka2` to start 2 kafka brokers. 
        Alternatively run `make run_kafka run_kafka2` to start both in a single command.
    3. Optionally run `make run_kafka_ui` to start the ui. This can be accessed at http://localhost:8080.
3. Start Kafka producer with `make run_kafka_producer` this will build the image and then start the container. This will make a topic and start producing fake events to the topic. Please view in the Kafka ui.
4. (Optional) Start Kafka consumer with `make run_kafka_consumer` this will build the image and then start the container. Make sure to check the terminal output in docker desktop to ensure messages are being consumed correctly.

5. Start Spark - This requires manually built images.
    1. Build the datastore image and volume using `make create_spark_datastore`.
    2. Build the shared image with `make build_spark`. This image is used by both master and both workers.
    3. Start Spark master with 2 workers using `make run_spark`. Master UI can be accessed at http://localhost:8090.
6. (Optional) For an example Spark job that opens a csv please run `make run_spark_job`. This will use a csv provided in the datastore.
    This container will run quickly and then exit once it has completed its task.
7. (Optional) For an example Spark job that reads a kafka topic and outputs various results - please run `make run_kafka_spark_consumer`.
8. (Optional) For an example Spark job that reads a kafka topic and then writes to another - please run `make run_kafka_spark_aggregation`.

### Inspecting the docker networks:

Run `docker network ls` to list networks.
There should be "host" and "bridge" networks listed.

The docker containers run with `--net=host` should be available in the "host" network while the others will be in the "bridge" network. Please view each network by running the following command: `docker network inspect bridge` or `docker network inspect host`.