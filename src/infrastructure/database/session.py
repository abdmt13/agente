from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from src.infrastructure.config.settings import Settings
from src.infrastructure.database.models.base import Base


class DatabaseManager:
    def __init__(self, settings: Settings):
        self._settings = settings
        url = settings.async_database_url
        is_sqlite = "sqlite" in url
        connect_args = {"check_same_thread": False} if is_sqlite else {}

        self._engine: AsyncEngine = create_async_engine(
            url,
            echo=settings.DB_ECHO,
            pool_pre_ping=True,
            connect_args=connect_args,
            **({} if is_sqlite else {"pool_size": settings.DB_POOL_SIZE, "max_overflow": settings.DB_MAX_OVERFLOW})
        )

        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False
        )

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        return self._session_factory

    async def create_tables(self) -> None:
        """Crea todas las tablas declaradas si no existen."""
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        """Cierra el pool de conexiones."""
        await self._engine.dispose()
