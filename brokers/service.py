from typing import Dict
from kafka import KafkaConsumer, KafkaProducer
from google.cloud import pubsub_v1
from dotenv import load_dotenv
import os
from brokers.base import Broker, BrokerProtocol
from json import dumps, loads


class BrokerService:

    def __init__(self, topic: str, callback=None, service: str = 'kafka'):
        broker_registry=Broker.__subclasses__()
        filtered_brokers_class = [b for b in broker_registry if b.name == service]
        if filtered_brokers_class:
            self.broker = filtered_brokers_class[0](topic=topic, callback=callback)
        else:
            print('None')
            self.broker = None

    def receive(self, wait=False) -> None:
        if self.broker:
            self.broker.receive_asynch(wait=wait)

    def send(self, data: Dict) -> None:
        if self.broker:
            self.broker.send(data)

    def terminate(self):
        if self.broker:
            self.broker.stop_receiving()


load_dotenv()

# Kafka implementation
HOST = os.getenv('HOST')


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


class GooglePubSubBroker(Broker, BrokerProtocol):
    name = 'pub_sub'

    def send(self, data: Dict) -> None:
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(PUB_SUB_PROJECT, self.topic)
        data_json = dumps(data).encode("utf-8")
        publisher.publish(topic_path, data=data_json)

    def call_back(self, message):
        self.callback(loads(message.data))
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
