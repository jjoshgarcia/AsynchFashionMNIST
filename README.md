Asynchronous Fashion MNIST

Instructions:

Kafka Cluster

- Make sure docker compose is installed https://docs.docker.com/compose/install/ and running
- Clone repository
```
>>> git clone https://github.com/jjoshgarcia/kafka-cluster.git
>>> cd kafka-cluster
```
- Run the cluster
```
>>> docker-compose -f docker-compose-expose.yml up
```

Train the network

- Install requirements
```
>>> pip install -r requirements.txt
```
- Run model in terminal for default hyperparameters and Fashion MNIST dataset
```
>>> python model.py
```
- or train your own dataset with custom hyperparameters
```
from model import train

train_set = torchvision.datasets.FashionMNIST(
        root='./data/FashionMNIST',
        train=True,
        download=True,
        transform=transforms.Compose([
            transforms.ToTensor()
        ])
    )
params = OrderedDict(
    lr=[.01, ],
    batch_size=[1000],
    shuffle=[True]
)
epochs = 150

train(params,train_set,epochs, save_last_model=True)

```

Asynchronous Inference

- Run producer to start sending testing images to kafka every 3 seconds
```
>>> python producer.py
```
- Run consumer to listen to inference results in a different terminal window
```
>>> python consumer.py
```
- Run the inference service to listen to kafka and make predictions
```
>>> python inference.py
```
Results should start being printed in the consumer console