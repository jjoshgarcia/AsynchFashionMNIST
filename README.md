# Asynchronous Fashion MNIST

## Message Broker's setup
### Kafka Cluster

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

### Pub/Sub Setup

- Go to Google Cloud Platform -> Service Accounts. Create a service account with Pub/Sub Publisher and subscriber role.
- Download keys in json format
- Place file in root
- Create two topics called 'inference' and 'result_inference'

## Train the network

- Install requirements
```
>>> pip install -r requirements.txt
```
- Run model in terminal for default hyperparameters and Fashion MNIST dataset
```
>>> python classifier/model.py
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

## Add a broker to the broker service
Create a subclass of Broker from broker.py with BrokerProtocol. The class will be automatically registered in the service.
```
from broker import Broker, BrokerProtocol

class ExampleBroker(Broker, BrokerProtocol):
    name = 'my_broker_name'

    def send(self, data: Dict) -> None:
        """ My implementation """

    def receive_target(self) -> None:
        """ My implementation """
```
## Use Broker Service 

Import BrokerService from broker.py and instantiate a service with topic and optional callable for receiving data. 
Set the service key to the desired service name (default='kafka', available services in this project: 'kafka', 'pub_sub').
```
from broker import BrokerService

def my_callback():
    pass
    
data={'my_data':'mydata'}
    
service=BrokerService('my topic',callback=my_callback,service='pub/sub')

service.send(data)
service.receive()
```

# PART 3

## Asynchronous Inference

Create an instance of ClassifierService with result callback and selected broker service. Call classify passing an image and optional metadata.
```
from asynch_classifier.classifier_service import ClassifierService

service = ClassifierService(result_callback, broker=broker)
service.classify(my_image, metadata={})
```

## Test it!

Run main.py passing the name of the broker service to use as parameter. It should send 3 images and get the results asynchronously.  
```
>>> python main.py pub_sub
```
