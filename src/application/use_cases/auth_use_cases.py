from datetime import datetime, timezone
from src.domain.entities.user import User
from src.domain.exceptions.auth import (
    AuthenticationException,
    UserAlreadyExistsException,
)
from src.domain.exceptions.base import EntityNotFoundException
from src.interfaces.ports.unit_of_work import IUnitOfWork
from src.interfaces.ports.token_service import ITokenService
from src.interfaces.ports.password_hasher_port import IPasswordHasher
from src.interfaces.ports.event_publisher import IEventPublisher
from src.interfaces.dtos.user_dto import UserDTO, TokenDTO
from src.infrastructure.config.settings import Settings


class AuthenticateUserUseCase:
    def __init__(
        self,
        uow: IUnitOfWork,
        token_service: ITokenService,
        password_hasher: IPasswordHasher,
        event_publisher: IEventPublisher,
        settings: Settings
    ):
        self._uow = uow
        self._token_service = token_service
        self._password_hasher = password_hasher
        self._event_publisher = event_publisher
        self._settings = settings

    async def execute(self, email: str, password: str) -> TokenDTO:
        email = email.strip().lower()
        async with self._uow as uow:
            user = await uow.users.get_by_email(email)
            if not user or not user.is_active:
                raise AuthenticationException("Credenciales incorrectas o usuario inactivo.")

            if not self._password_hasher.verify_password(password, user.password_hash):
                raise AuthenticationException("Credenciales incorrectas.")

            # Generar token JWT stateless con claims
            payload = {
                "sub": str(user.id),
                "email": user.email,
                "role": user.role,
                "permissions": user.permissions
            }
            token = self._token_service.create_access_token(
                payload,
                expires_delta_seconds=self._settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )

            await self._event_publisher.publish(
                topic=self._settings.KAFKA_TOPIC_AUTH_EVENTS,
                event_type="user_logged_in",
                data={"user_id": user.id, "email": user.email, "role": user.role}
            )

            user_dto = UserDTO(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                permissions=user.permissions,
                is_active=user.is_active,
                created_at=user.created_at
            )

            return TokenDTO(
                access_token=token,
                token_type="bearer",
                expires_in=self._settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=user_dto
            )


class RegisterUserUseCase:
    def __init__(
        self,
        uow: IUnitOfWork,
        password_hasher: IPasswordHasher,
        event_publisher: IEventPublisher,
        settings: Settings
    ):
        self._uow = uow
        self._password_hasher = password_hasher
        self._event_publisher = event_publisher
        self._settings = settings

    async def execute(self, email: str, password: str, full_name: str, role: str = "customer") -> UserDTO:
        email = email.strip().lower()
        async with self._uow as uow:
            existing = await uow.users.get_by_email(email)
            if existing:
                raise UserAlreadyExistsException(email)

            hashed_pwd = self._password_hasher.hash_password(password)
            user_entity = User(
                email=email,
                password_hash=hashed_pwd,
                full_name=full_name,
                role=role,
                permissions=["chat:read", "chat:write"] if role == "customer" else ["*"],
                is_active=True,
                created_at=datetime.now(timezone.utc)
            )

            saved_user = await uow.users.save(user_entity)
            await uow.commit()

            await self._event_publisher.publish(
                topic=self._settings.KAFKA_TOPIC_AUTH_EVENTS,
                event_type="user_registered",
                data={"user_id": saved_user.id, "email": saved_user.email, "role": saved_user.role}
            )

            return UserDTO(
                id=saved_user.id,
                email=saved_user.email,
                full_name=saved_user.full_name,
                role=saved_user.role,
                permissions=saved_user.permissions,
                is_active=saved_user.is_active,
                created_at=saved_user.created_at
            )
