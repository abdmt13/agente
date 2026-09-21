from abc import ABC, abstractmethod
from typing import Any, Dict


class IEventPublisher(ABC):
    @abstractmethod
    async def publish(self, topic: str, event_type: str, data: Dict[str, Any]) -> None:
        raise NotImplementedError
