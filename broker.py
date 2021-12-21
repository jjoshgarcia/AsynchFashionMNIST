from typing import Protocol, Dict, Callable, final, Optional, List, ClassVar
from multiprocessing import Process


class Broker:
    processes: List[Process]
    callback: Optional[Callable[[Dict], None]]
    topic: str

    def __init__(self, topic: str, callback: Optional[Callable[[Dict], None]] = None):
        self.topic = topic
        self.callback = callback
        self.processes: List[Process] = list()


class BrokerProtocol(Protocol):
    name: ClassVar[str]

    @final  # type: ignore
    def receive_asynch(self, wait=False) -> None:
        """ Start receiver in the background """
        p = Process(target=self.receive_target)
        p.start()
        if wait:
            p.join()

    def receive_target(self) -> None:
        """ Implement method in subclass"""
        raise NotImplementedError

    def send(self, data: Dict) -> None:
        """ Send data to broker (Implement method in subclass) """
        raise NotImplementedError


broker_registry = []


def register_broker(func):
    broker_registry.append(func)
    return func


class BrokerService:

    def __init__(self, topic: str, callback=None, service: str = 'kafka'):
        filtered_brokers_class = [b for b in broker_registry if b.name == service]
        if filtered_brokers_class:
            self.broker = filtered_brokers_class[0](topic=topic, callback=callback)
        else:
            self.broker = None

    def receive(self, wait=False) -> None:
        if self.broker:
            self.broker.receive_asynch(wait=wait)

    def send(self, data: Dict) -> None:
        if self.broker:
            self.broker.send(data)

    def terminate(self):
        if self.broker:
            self.broker.stop_receiving()
