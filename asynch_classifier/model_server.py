from classifier.model import inference
from brokers.service import BrokerService


class ModelServer:
    def __init__(self, broker):
        self.broker = broker
        self.receiver = BrokerService('inference', callback=self.classify, service=broker)
        self.receiver.receive(wait=False)

    def classify(self, data):
        result = inference(data)
        if 'metadata' in data:
            result['metadata'] = data['metadata']
            if 'number' in data['metadata'] and 'broker' in data:
                broker = data['broker']
                number = data['metadata']['number']
                print(f"{broker}: Inference result for image {number} sent back to the broker")
        broker_service = BrokerService('result_inference', service=self.broker)
        broker_service.send(result)
