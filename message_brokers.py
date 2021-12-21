import os
from typing import Dict, Callable, Optional, List
from dotenv import load_dotenv
from broker import Broker, BrokerProtocol, register_broker
from kafka import KafkaConsumer, KafkaProducer  # type: ignore
from json import loads, dumps
from google.cloud import pubsub_v1  # type: ignore # Google Pub/Sub
import json

load_dotenv()

# Kafka implementation
HOST = os.getenv('HOST')


@register_broker
class KafkaBroker(Broker, BrokerProtocol):
    name = 'kafka'

    def call_back(self, message):
        self.callback(message.value)

    def send(self, data: Dict) -> None:
        producer = KafkaProducer(
            bootstrap_servers=[HOST],
            value_serializer=lambda v: dumps(v).encode('utf-8')
        )
        producer.send(self.topic, value=data)

    def receive_target(self) -> None:
        consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=[HOST],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='my-group-id',
            value_deserializer=lambda x: loads(x.decode('utf-8'))
        )
        if self.callback:  # type: ignore
            for event in consumer:
                self.call_back(event)  # type: ignore


# Google Pub/Sub implementation

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
PUB_SUB_PROJECT = "fashionmnist-335023"


@register_broker
class GooglePubSubBroker(Broker, BrokerProtocol):
    name = 'pub_sub'

    def send(self, data: Dict) -> None:
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(PUB_SUB_PROJECT, self.topic)
        data_json = json.dumps(data).encode("utf-8")
        publisher.publish(topic_path, data=data_json)

    def call_back(self, message):
        self.callback(json.loads(message.data))
        message.ack()

    def receive_target(self) -> None:
        subscriber = pubsub_v1.SubscriberClient()
        subscription_path = subscriber.subscription_path(PUB_SUB_PROJECT, self.topic + "-sub")
        streaming_pull_future = subscriber.subscribe(subscription_path, callback=self.call_back)
        with subscriber:
            try:
                streaming_pull_future.result()
            except TimeoutError:
                streaming_pull_future.cancel()
