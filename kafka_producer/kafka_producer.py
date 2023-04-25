import kafka

from faker import Faker
import random
import json
import time

def create_fake_record():
    fake = Faker()
    return {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "phone_number": fake.phone_number(),
        "address": fake.address(),
    }

def main():
    print("Docker container started")
    try:
        admin_client = kafka.KafkaAdminClient(bootstrap_servers='localhost:9092')
        admin_client.create_topics([
            kafka.admin.NewTopic(name="test_topic_1", num_partitions=2, replication_factor=1)
        ], validate_only=False)
    except kafka.errors.TopicAlreadyExistsError as e:
        print(e)
    except Exception as e:
        raise e

    producer = kafka.KafkaProducer(bootstrap_servers='localhost:9092')
    
    while True:
        record = create_fake_record()
        producer.send('test_topic_1', value=json.dumps(record).encode('utf-8'))
        print(record)
        time.sleep(1)




main()