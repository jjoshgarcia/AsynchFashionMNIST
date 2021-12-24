import torchvision
from asynch_classifier.classifier_service import ClassifierService
import sys
from time import sleep


def result_callback(data):
    print(f'Inference Result: {data}')


if __name__ == '__main__':
    if len(sys.argv)==2:
        broker = sys.argv[1]
    else:
        broker = 'kafka'
    test_set = torchvision.datasets.FashionMNIST(
        root='./data/FashionMNIST',
        train=False,
        download=True,
    )
    i = 1
    service = ClassifierService(result_callback, broker=broker)
    for image, label, in test_set:
        service.classify(image, metadata={'number': i, 'label':label})
        print(f'Image number {i} sent')
        if i == 3:
            break
        else:
            i += 1
    while True:
        print('waiting for all processes to complete...')
        sleep(3)
