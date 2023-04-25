.PHONY:  run_zookeeper run_kafka1 run_kafka2 run_kafka_producer build_kafka_producer

run_zookeeper:
	docker run --name=zookeeper -p 2181:2181 -d zookeeper

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

run_kafka_ui:
	docker run -it -d -p 8080:8080 \
	--name kafka_ui \
	-e DYNAMIC_CONFIG_ENABLED=true \
	-e KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS=host.docker.internal:9092 \
	provectuslabs/kafka-ui:master

build_kafka_producer:
	docker build -t kafka_producer kafka_producer

run_kafka_producer:
	docker run --name=kafka_producer --net=host -d kafka_producer

build_kafka_consumer:
	docker build -t kafka_consumer kafka_consumer

run_kafka_consumer:
	docker run --name=kafka_consumer --net=host -d kafka_consumer

build_spark_datastore:
	docker build -t spark_datastore spark_datastore
	docker create -v /data --name spark_datastore spark_datastore

build_spark:
	docker build -t spark spark

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

run_spark: run_spark_master run_spark_worker run_spark_worker2

build_kafka_spark_consumer:
	docker build -t kafka_spark_consumer kafka_spark_consumer

run_kafka_spark_consumer: build_kafka_spark_consumer
	docker run --volumes-from spark_datastore \
	--name=kafka_spark_consumer \
	--net=host \
	-d kafka_spark_consumer

build_spark_job:
	docker build -t spark_job spark_job

run_spark_job: build_spark_job
	docker run --net=host \
	--volumes-from spark_datastore \
	--name=spark_job \
	-d spark_job