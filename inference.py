from kafka import KafkaConsumer
from json import loads, dumps
from model import inference
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda x: dumps(x).encode('utf-8')
)

input = KafkaConsumer(
    'topic_input',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group-id',
    value_deserializer=lambda x: loads(x.decode('utf-8'))
)
if __name__ == '__main__':
    print('Inference service started')
    for event in input:
        result=inference(event.value)
        producer.send('topic_output', value=result)
        print("Inference result for image number %d sent to be consumed",result['Image Number'])