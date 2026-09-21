from abc import ABC, abstractmethod
from typing import Any
from src.interfaces.ports.repositories.user_repository import IUserRepository
from src.interfaces.ports.repositories.conversation_repository import IConversationRepository
from src.interfaces.ports.repositories.property_repository import IPropertyRepository


class IUnitOfWork(ABC):
    """Interfaz abstracta para el patrón Unit of Work."""

    @property
    @abstractmethod
    def users(self) -> IUserRepository:
        """Repositorio de usuarios."""
        raise NotImplementedError

    @property
    @abstractmethod
    def conversations(self) -> IConversationRepository:
        """Repositorio de conversaciones y mensajes."""
        raise NotImplementedError

    @property
    @abstractmethod
    def properties(self) -> IPropertyRepository:
        """Repositorio de propiedades inmobiliarias."""
        raise NotImplementedError

    async def __aenter__(self) -> "IUnitOfWork":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()

    @abstractmethod
    async def commit(self) -> None:
        """Confirma los cambios en la transacción actual."""
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        """Revierte los cambios de la transacción actual."""
        raise NotImplementedError

