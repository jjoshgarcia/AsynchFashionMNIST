from typing import Protocol, Dict, Callable, final, Optional, List, ClassVar
from multiprocessing import Process


class Broker:
    processes: List[Process]
    callback: Optional[Callable[[Dict], None]]
    topic: str
    subclasses: List = []
    name: str = ''

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses.append(cls)

    def __init__(self, topic: str, callback: Optional[Callable[[Dict], None]] = None):
        self.topic = topic
        self.callback = callback
        self.processes: List[Process] = list()


class BrokerProtocol(Protocol):

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
