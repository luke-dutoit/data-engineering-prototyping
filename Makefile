.PHONY:  run_zookeeper run_kafka1 run_kafka2 run_kafka_producer build_kafka_producer

# Zookeeper is required to coordinate Kafka. We can use a prebuilt image and simply expose the required ports using -p.
# -p is for the publish ports so they are accesable using localhost on the host machine.
# Please read more here: https://docs.docker.com/engine/reference/commandline/run/

# -d is for the detach option. This runs the container in the background so its output is not written to your working terminal.
# Please see terminal output in docker desktop.

# e.g. docker run --name=name_of_container -p ports_to_publish -d image_name
run_zookeeper:
	docker run --name=zookeeper -p 2181:2181 -d zookeeper

# Kafka can also use prebuilt image.
# -e passes an environmental variable to the container.
# host.docker.internal is how to access localhost on the host machine when running the container in docker for mac.
# KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR - please ensure this number is less than or equal to the number of brokers you make.
# The backslash \ is used to split the long command into multiple lines.
run_kafka:
	docker run -p 9092:9092 \
	 --name kafka \
	-e KAFKA_ZOOKEEPER_CONNECT=host.docker.internal:2181 \
	-e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://host.docker.internal:9092 \
	-e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=2 \
	-d confluentinc/cp-kafka 

run_kafka2:
	docker run -p 9093:9093 \
	 --name kafka2 \
	-e KAFKA_ZOOKEEPER_CONNECT=host.docker.internal:2181 \
	-e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://host.docker.internal:9093 \
	-e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=2 \
	-d confluentinc/cp-kafka 

# This can be accessed at http://localhost:8080.
run_kafka_ui:
	docker run -it -d -p 8080:8080 \
	--name kafka_ui \
	-e DYNAMIC_CONFIG_ENABLED=true \
	-e KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS=host.docker.internal:9092 \
	provectuslabs/kafka-ui:master

# -t is to tag the image so it can be referenced by the identifier.
# e.g. docker build -t tag_name name_of_subfolder_containing_dockerfile
build_kafka_producer:
	docker build -t kafka_producer kafka_producer

# the build command `build_kafka_producer` is run every time this run command is run as it is referenced after the :.
# --net=host means that this container will be available in the host machine. If this setting is specified then the -p setting will be ignored.
# It can simplify some behaviours and make others more complex. 
# Id suggest experimenting with this setting to see how it affects your containers and their connections.
run_kafka_producer: build_kafka_producer
	docker run --name=kafka_producer -d kafka_producer

build_kafka_consumer:
	docker build -t kafka_consumer kafka_consumer

run_kafka_consumer: build_kafka_consumer
	docker run --name=kafka_consumer --net=host -d kafka_consumer

# for the datastore we do not need to run the datastore image. Instead we build the volume so that other containers can access it.
# in this case the exposed volume uses the /data path within the image and exposes all data within this file including the test csv.
build_spark_datastore:
	docker build -t spark_datastore spark_datastore

create_spark_datastore: build_spark_datastore
	docker create -v /data --name spark_datastore spark_datastore

# One image can be used in multiple containers with different entrypoint arguments to display different behaviours.
build_spark:
	docker build -t spark spark

# This command references the datastore volume `--volumes-from spark_datastore \`
# -p is referenced multiple times to publish multiple ports.
# after the image name `spark` is an argument `master`. This is used in the entrypoint.sh script to change the behaviour of the container at runtime.
run_spark_master:
	docker run -p 7077:7077 \
	-p 8090:8090 \
	--volumes-from spark_datastore \
	--name=spark_master \
	-d spark master


run_spark_worker:
	docker run \
	-p 8091:8091 \
	--volumes-from spark_datastore \
	--name=spark_worker \
	-d spark worker

run_spark_worker2:
	docker run \
	-p 8092:8092 \
	-e SPARK_WORKER_WEBUI_PORT=8092 \
	--volumes-from spark_datastore \
	--name=spark_worker2 \
	-d spark worker

# For easy starting of all 3 spark containers.
run_spark: run_spark_master run_spark_worker run_spark_worker2

build_kafka_spark:
	docker build -t kafka_spark kafka_spark

run_kafka_spark_consumer: build_kafka_spark
	docker run --volumes-from spark_datastore \
	--name=kafka_spark_consumer \
	--net=host \
	-d kafka_spark kafka_spark_consumer

run_kafka_spark_aggregation: build_kafka_spark
	docker run --volumes-from spark_datastore \
	--name=kafka_spark_aggregation \
	--net=host \
	-d kafka_spark kafka_spark_aggregation


run_spark_job: build_kafka_spark
	docker run --volumes-from spark_datastore \
	--name=kafka_spark_aggregation \
	--net=host \
	-d kafka_spark spark_job

build_all: build_spark_datastore build_spark build_kafka_producer build_kafka_consumer build_kafka_spark