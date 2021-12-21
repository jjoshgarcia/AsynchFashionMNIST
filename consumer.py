from typing import Dict
from broker import BrokerService


def kafka_callback(data: Dict) -> None:
    print('Result from kafka:', data)
    return None


def pub_sub_callback(data):
    print('Result from pub/sub:', data)


if __name__ == '__main__':
    import message_brokers
    print('Consumer started')
    kafka_receiver = BrokerService('topic_output', callback=kafka_callback, service='kafka')
    pub_sub_receiver = BrokerService('result_inference', callback=pub_sub_callback, service='pub_sub')
    kafka_receiver.receive(wait=False)
    pub_sub_receiver.receive(wait=True)
    print('Consumer finished')

