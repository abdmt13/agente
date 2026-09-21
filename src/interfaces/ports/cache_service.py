from abc import ABC, abstractmethod
from typing import Any, Optional


class ICacheService(ABC):
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError

    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> None:
        raise NotImplementedError
