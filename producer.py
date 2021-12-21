from copy import deepcopy
from time import sleep
import torchvision
import numpy as np
from broker import BrokerService

if __name__ == '__main__':
    import message_brokers

    test_set = torchvision.datasets.FashionMNIST(
        root='./data/FashionMNIST',
        train=False,
        download=True,
    )

    i = 1
    for image, label, in test_set:
        # Send to Kafka
        data_kafka = {'image': np.array(image).tolist(),
                      'label': label,
                      'image number': i,
                      'source': 'kafka'}
        kafka_service = BrokerService('topic_input', service='kafka')
        kafka_service.send(data_kafka)
        print('Kafka: Image number %d sent.', i)
        sleep(3)

        # Send to Pub/Sub
        data_pub_sub = deepcopy(data_kafka)
        data_pub_sub['source'] = 'pub_sub'
        pub_sub_service = BrokerService('inference', service='pub_sub')
        pub_sub_service.send(data_pub_sub)
        print('Pub/Sub: Image number %d sent.', i)
        sleep(3)
        i += 1
