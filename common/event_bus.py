from abc import ABC, abstractmethod
from collections import deque, defaultdict


class EventHandler(ABC):
    @abstractmethod
    def handle(self, payload: dict) -> None:
        pass


class EventBus:
    def __init__(self):
        self.handlers: dict[str, EventHandler] = {}
        self.queue: dict[str, deque[dict]] = defaultdict(deque)

    def subscribe(self, topic: str, handler_cls: EventHandler) -> None:
        self.handlers[topic] = handler_cls

    def publish(self, topic: str, payload: dict) -> None:
        self.queue[topic].append(payload)

    def consume(self) -> None:
        for topic, topic_queue in self.queue.items():
            while topic_queue:
                self.handlers[topic].handle(topic_queue.popleft())


event_bus = EventBus()
NEW_POST_TOPIC = 'new-post'
