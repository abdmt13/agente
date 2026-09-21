from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from src.interfaces.ports.unit_of_work import IUnitOfWork
from src.interfaces.ports.repositories.user_repository import IUserRepository
from src.interfaces.ports.repositories.conversation_repository import IConversationRepository
from src.interfaces.ports.repositories.property_repository import IPropertyRepository
from src.infrastructure.database.repositories.user_repo_impl import UserRepositoryImpl
from src.infrastructure.database.repositories.conversation_repo_impl import ConversationRepositoryImpl
from src.infrastructure.database.repositories.property_repo_impl import PropertyRepositoryImpl


class SqlAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory
        self.session: Optional[AsyncSession] = None
        self._users: Optional[IUserRepository] = None
        self._conversations: Optional[IConversationRepository] = None
        self._properties: Optional[IPropertyRepository] = None

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        self.session = self._session_factory()
        self._users = UserRepositoryImpl(self.session)
        self._conversations = ConversationRepositoryImpl(self.session)
        self._properties = PropertyRepositoryImpl(self.session)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        try:
            if exc_type is not None:
                await self.rollback()
            else:
                await self.commit()
        finally:
            if self.session:
                await self.session.close()

    @property
    def users(self) -> IUserRepository:
        if self._users is None:
            raise RuntimeError("Unit of Work no ha sido iniciado con 'async with'.")
        return self._users

    @property
    def conversations(self) -> IConversationRepository:
        if self._conversations is None:
            raise RuntimeError("Unit of Work no ha sido iniciado con 'async with'.")
        return self._conversations

    @property
    def properties(self) -> IPropertyRepository:
        if self._properties is None:
            raise RuntimeError("Unit of Work no ha sido iniciado con 'async with'.")
        return self._properties

    async def commit(self) -> None:
        if self.session:
            await self.session.commit()

    async def rollback(self) -> None:
        if self.session:
            await self.session.rollback()
