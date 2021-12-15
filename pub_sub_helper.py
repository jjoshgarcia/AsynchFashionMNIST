import os
from google.cloud import pubsub_v1
import json

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
PUB_SUB_PROJECT = "fashionmnist-335023"

PUB_SUB_TOPIC_INFERENCE = "inference"
PUB_SUB_TOPIC_RESULT = "result_inference"

PUB_SUB_SUBSCRIPTION_INFERENCE = "inference-sub"
PUB_SUB_SUBSCRIPTION_RESULT = "result_inference-sub"


# producer function to push a message to a Pub/Sub topic
def push_payload_pub_sub(payload, topic, project):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project, topic)
    data_json = json.dumps(payload).encode("utf-8")
    publisher.publish(topic_path, data=data_json)


def consume_pub_sub(project, subscription, callback):
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project, subscription)
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    with subscriber:
        try:
            streaming_pull_future.result()
        except TimeoutError:
            streaming_pull_future.cancel()
