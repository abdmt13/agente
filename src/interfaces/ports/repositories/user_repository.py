from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.user import User


class IUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def save(self, user: User) -> User:
        raise NotImplementedError
