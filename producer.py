from time import sleep
from json import dumps
from kafka import KafkaProducer
import torchvision
from PIL import Image
import io
import numpy as np

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: dumps(v).encode('utf-8')
)

test_set = torchvision.datasets.FashionMNIST(
    root = './data/FashionMNIST',
    train = False,
    download = True,
)

def image_to_byte_array(image:Image):
  imgByteArr = io.BytesIO()
  image.save(imgByteArr, format='PNG')
  imgByteArr = imgByteArr.getvalue()
  return imgByteArr

if __name__ == '__main__':
    i=1
    for image, label,  in test_set:
        data = {'image':  np.array(image).tolist(),
                'label': label,
                'image number':i}
        producer.send('topic_input', value=data)
        print('Image number %d sent.',i)
        i += 1
        sleep(3)
