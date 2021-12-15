from multiprocessing import Process
from kafka_helper import consume_kafka
import json
from pub_sub_helper import consume_pub_sub, PUB_SUB_PROJECT, PUB_SUB_SUBSCRIPTION_RESULT


def kafka_callback(message):
    print('Result from kafka:', message.value)


def pub_sub_callback(message):
    print('Result from pub/sub:', json.loads(message.data))


def kaf_consume():
    consume_kafka('topic_output', kafka_callback)


def pub_consume():
    consume_pub_sub(PUB_SUB_PROJECT, PUB_SUB_SUBSCRIPTION_RESULT, pub_sub_callback)


if __name__ == '__main__':
    print('Consumer started')

    p1 = Process(target=kaf_consume)
    p1.start()
    p2 = Process(target=pub_consume)
    p2.start()
