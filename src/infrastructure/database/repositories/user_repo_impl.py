from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.entities.user import User
from src.infrastructure.database.models.user_model import UserModel
from src.interfaces.ports.repositories.user_repository import IUserRepository


class UserRepositoryImpl(IUserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            full_name=model.full_name,
            role=model.role,
            permissions=model.permissions or [],
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    async def get_by_id(self, user_id: int) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def save(self, user: User) -> User:
        if user.id:
            stmt = select(UserModel).where(UserModel.id == user.id)
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()
            if model:
                model.email = user.email
                model.password_hash = user.password_hash
                model.full_name = user.full_name
                model.role = user.role
                model.permissions = user.permissions
                model.is_active = user.is_active
                await self._session.flush()
                return self._to_entity(model)

        model = UserModel(
            email=user.email,
            password_hash=user.password_hash,
            full_name=user.full_name,
            role=user.role,
            permissions=user.permissions,
            is_active=user.is_active
        )
        self._session.add(model)
        await self._session.flush()
        user.id = model.id
        return self._to_entity(model)
