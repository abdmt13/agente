from src.interfaces.ports.unit_of_work import IUnitOfWork
from src.interfaces.ports.ai_service import IAIService
from src.interfaces.ports.cache_service import ICacheService
from src.interfaces.ports.event_publisher import IEventPublisher
from src.interfaces.ports.token_service import ITokenService
from src.interfaces.ports.password_hasher_port import IPasswordHasher
from src.infrastructure.config.settings import Settings

from src.application.use_cases.send_chat_message_use_case import SendChatMessageUseCase
from src.application.use_cases.conversation_use_cases import (
    GetConversationUseCase,
    DeleteConversationUseCase,
)
from src.application.use_cases.property_use_cases import (
    GetCatalogUseCase,
    GetBusinessContextUseCase,
)
from src.application.use_cases.auth_use_cases import (
    AuthenticateUserUseCase,
    RegisterUserUseCase,
)
from src.application.services.chat_service import ChatService
from src.application.services.property_service import PropertyService
from src.application.services.auth_service import AuthService


class ServiceFactory:
    """Factory para crear y proveer instancias de servicios orquestadores."""

    def __init__(
        self,
        uow: IUnitOfWork,
        ai_service: IAIService,
        cache_service: ICacheService,
        event_publisher: IEventPublisher,
        token_service: ITokenService,
        password_hasher: IPasswordHasher,
        settings: Settings,
    ):
        self._uow = uow
        self._ai_service = ai_service
        self._cache_service = cache_service
        self._event_publisher = event_publisher
        self._token_service = token_service
        self._password_hasher = password_hasher
        self._settings = settings

    def create_chat_service(self) -> ChatService:
        send_msg_uc = SendChatMessageUseCase(
            uow=self._uow,
            ai_service=self._ai_service,
            cache_service=self._cache_service,
            event_publisher=self._event_publisher,
            settings=self._settings,
        )
        get_conv_uc = GetConversationUseCase(
            uow=self._uow,
            cache_service=self._cache_service,
        )
        delete_conv_uc = DeleteConversationUseCase(
            uow=self._uow,
            cache_service=self._cache_service,
        )
        return ChatService(
            send_message_uc=send_msg_uc,
            get_conversation_uc=get_conv_uc,
            delete_conversation_uc=delete_conv_uc,
        )

    def create_property_service(self) -> PropertyService:
        get_catalog_uc = GetCatalogUseCase(
            uow=self._uow,
            cache_service=self._cache_service,
        )
        get_context_uc = GetBusinessContextUseCase(
            uow=self._uow,
            cache_service=self._cache_service,
        )
        return PropertyService(
            get_catalog_uc=get_catalog_uc,
            get_business_context_uc=get_context_uc,
        )

    def create_auth_service(self) -> AuthService:
        auth_uc = AuthenticateUserUseCase(
            uow=self._uow,
            token_service=self._token_service,
            password_hasher=self._password_hasher,
            event_publisher=self._event_publisher,
            settings=self._settings,
        )
        reg_uc = RegisterUserUseCase(
            uow=self._uow,
            password_hasher=self._password_hasher,
            event_publisher=self._event_publisher,
            settings=self._settings,
        )
        return AuthService(
            authenticate_uc=auth_uc,
            register_uc=reg_uc,
        )
