from model import inference
from multiprocessing import Process
import json
from kafka_helper import consume_kafka, producer_kafka
from pub_sub_helper import consume_pub_sub, PUB_SUB_PROJECT, PUB_SUB_SUBSCRIPTION_INFERENCE, push_payload_pub_sub, \
    PUB_SUB_TOPIC_RESULT


def process_payload_pub_sub(message):
    try:
        result = inference(json.loads(message.data))
    except Exception as e:
        pass
    else:
        push_payload_pub_sub(result, PUB_SUB_TOPIC_RESULT, PUB_SUB_PROJECT)
        print("Pub/Sub: Inference result for image %d sent to be consumed" % int(result['Image Number']))
    message.ack()


def kafka_callback(message):
    result = inference(message.value)
    producer_kafka.send('topic_output', value=result)
    print("Kafka: Inference result for image %d sent to be consumed" % int(result['Image Number']))


def kaf_consume():
    consume_kafka('topic_input', kafka_callback)


def pub_consume():
    consume_pub_sub(PUB_SUB_PROJECT, PUB_SUB_SUBSCRIPTION_INFERENCE, process_payload_pub_sub)


if __name__ == '__main__':
    print('Inference service started')
    p1 = Process(target=kaf_consume)
    p1.start()
    p2 = Process(target=pub_consume)
    p2.start()
