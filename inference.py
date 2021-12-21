from model import inference
from broker import BrokerService


def pub_sub_callback(data):
    result = inference(data)
    broker_service = BrokerService('result_inference', service='pub_sub')
    broker_service.send(result)
    print("Pub/Sub: Inference result for image %d sent to be consumed" % int(result['Image Number']))


def kafka_callback(data):
    result = inference(data)
    broker_service = BrokerService('topic_output', service='kafka')
    broker_service.send(result)
    print("Kafka: Inference result for image %d sent to be consumed" % int(result['Image Number']))


if __name__ == '__main__':
    import message_brokers

    print('Inference service started')
    kafka_receiver = BrokerService('topic_input', callback=kafka_callback, service='kafka')
    pub_sub_receiver = BrokerService('inference', callback=pub_sub_callback, service='pub_sub')
    kafka_receiver.receive()
    pub_sub_receiver.receive()
