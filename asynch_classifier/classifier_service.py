import numpy as np

from asynch_classifier.model_server import ModelServer
from brokers.service import BrokerService


class ClassifierService:
    def __init__(self, result_callback, broker='kafka'):
        self.broker = broker
        self.model_server = ModelServer(broker)
        receiver = BrokerService('result_inference', callback=result_callback, service=self.broker)
        receiver.receive(wait=False)

    def classify(self, image, metadata=None):
        image_data = np.array(image).tolist()
        data = {
            'image': image_data,
            'metadata': metadata,
            'broker': self.broker, }
        broker_service = BrokerService('inference', service=self.broker)
        broker_service.send(data)
