import kafka

import json
import os
import time


def main():
    print("Docker container started")

    consumer = kafka.KafkaConsumer(
        "test_topic_1",
        group_id="python-test-consumer",
        bootstrap_servers=os.environ["KAFKA_BOOTSTRAP_SERVERS"],
    )

    for message in consumer:
        value = json.loads(message.value.decode("utf-8"))
        print(
            value,
            message.partition,
            message.offset,
            message.timestamp,
            message.key,
            message.topic,
        )


main()
