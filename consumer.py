from kafka import KafkaConsumer
from json import loads

consumer = KafkaConsumer(
    'topic_output',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group-id',
    value_deserializer=lambda x: loads(x.decode('utf-8'))
)
if __name__ == '__main__':
    print('Consumer started')
    for event in consumer:
        event_data = event.value
        print(event_data)
