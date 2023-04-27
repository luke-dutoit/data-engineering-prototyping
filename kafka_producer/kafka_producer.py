import kafka

from faker import Faker
import random
import json
import time


def create_fake_record() -> dict:
    # Use Faker library to generate fake records.
    fake = Faker()
    return {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "phone_number": fake.phone_number(),
        "address": fake.address(),
    }


def create_topic(topic_name: str, num_partitions: int, replication_factor: int) -> None:
    print(f"Attempting to create topic '{topic_name}'.")
    try:
        admin_client = kafka.KafkaAdminClient(bootstrap_servers="host.docker.internal:9092")
        admin_client.create_topics(
            [
                kafka.admin.NewTopic(
                    name=topic_name,
                    num_partitions=num_partitions,
                    replication_factor=replication_factor,
                )
            ],
            validate_only=False,
        )
        print("Topic created successfully.")
    except kafka.errors.TopicAlreadyExistsError as e:
        print("Topic already exists.")
        print(e)
    except Exception as e:
        print("Unexpected error detected during topic creation.")
        raise e


def main() -> None:
    print("Docker container started")
    topic_name = "test_topic_1"

    create_topic(topic_name, 2, 1)

    producer = kafka.KafkaProducer(bootstrap_servers="host.docker.internal:9092")

    while True:
        record = create_fake_record()
        producer.send(topic_name, value=json.dumps(record).encode("utf-8"))
        print(record)
        time.sleep(1)


main()
