from copy import deepcopy
from time import sleep
import torchvision
import numpy as np
from kafka_helper import producer_kafka
from pub_sub_helper import push_payload_pub_sub, PUB_SUB_PROJECT, PUB_SUB_TOPIC_INFERENCE

test_set = torchvision.datasets.FashionMNIST(
    root='./data/FashionMNIST',
    train=False,
    download=True,
)

if __name__ == '__main__':
    i = 1
    for image, label, in test_set:
        # Send to Kafka
        data_kafka = {'image': np.array(image).tolist(),
                      'label': label,
                      'image number': i,
                      'source': 'kafka'}
        producer_kafka.send('topic_input', value=data_kafka)
        print('Kafka: Image number %d sent.', i)
        sleep(3)

        # Send to Pub/Sub
        data_pub_sub = deepcopy(data_kafka)
        data_pub_sub['source'] = 'pub_sub'
        push_payload_pub_sub(data_pub_sub, PUB_SUB_TOPIC_INFERENCE, PUB_SUB_PROJECT)
        print('Pub/Sub: Image number %d sent.', i)
        sleep(3)
        i += 1
