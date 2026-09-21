from dependency_injector import containers, providers
from src.infrastructure.config.settings import Settings
from src.infrastructure.database.session import DatabaseManager
from src.infrastructure.database.unit_of_work_impl import SqlAlchemyUnitOfWork
from src.infrastructure.cache.redis_cache_adapter import RedisCacheAdapter
from src.infrastructure.messaging.kafka_producer_adapter import KafkaProducerAdapter
from src.infrastructure.security.jwt_token_adapter import JwtTokenAdapter
from src.infrastructure.security.password_hasher import BcryptPasswordHasher
from src.infrastructure.ai.ai_service_adapter import AIServiceAdapter
from src.application.services.service_factory import ServiceFactory
from src.application.mediator.mediator import Mediator

# Commands and Queries
from src.application.commands.chat_commands import (
    SendMessageCommand,
    DeleteConversationCommand,
    AuthenticateUserCommand,
    RegisterUserCommand,
)
from src.application.queries.chat_queries import (
    GetConversationHistoryQuery,
    GetPropertiesCatalogQuery,
    GetBusinessContextQuery,
)

# Handlers
from src.application.mediator.handlers.chat_handlers import (
    SendMessageHandler,
    GetConversationHistoryHandler,
    DeleteConversationHandler,
)
from src.application.mediator.handlers.property_handlers import (
    GetPropertiesCatalogHandler,
    GetBusinessContextHandler,
)
from src.application.mediator.handlers.auth_handlers import (
    AuthenticateUserHandler,
    RegisterUserHandler,
)


def _init_mediator(service_factory: ServiceFactory) -> Mediator:
    """Función constructora para registrar todos los handlers CQRS en el Mediator."""
    mediator = Mediator()

    # Chat handlers
    mediator.register_handler(SendMessageCommand, SendMessageHandler(service_factory))
    mediator.register_handler(GetConversationHistoryQuery, GetConversationHistoryHandler(service_factory))
    mediator.register_handler(DeleteConversationCommand, DeleteConversationHandler(service_factory))

    # Property handlers
    mediator.register_handler(GetPropertiesCatalogQuery, GetPropertiesCatalogHandler(service_factory))
    mediator.register_handler(GetBusinessContextQuery, GetBusinessContextHandler(service_factory))

    # Auth handlers
    mediator.register_handler(AuthenticateUserCommand, AuthenticateUserHandler(service_factory))
    mediator.register_handler(RegisterUserCommand, RegisterUserHandler(service_factory))

    return mediator


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.presentation.api.dependencies.mediator_dep",
            "src.presentation.api.dependencies.auth_guard",
            "src.presentation.api.v1.controllers.chat_controller",
            "src.presentation.api.v1.controllers.property_controller",
            "src.presentation.api.v1.controllers.auth_controller",
        ]
    )

    # 1. Configuration
    settings = providers.Singleton(Settings)

    # 2. Infrastructure Database
    db_manager = providers.Singleton(DatabaseManager, settings=settings)
    
    # 3. Unit of Work
    uow = providers.Factory(
        SqlAlchemyUnitOfWork,
        session_factory=db_manager.provided.session_factory
    )

    # 4. Cache & Messaging
    cache_service = providers.Singleton(
        RedisCacheAdapter,
        host=settings.provided.REDIS_HOST,
        port=settings.provided.REDIS_PORT,
        password=settings.provided.REDIS_PASSWORD,
        db=settings.provided.REDIS_DB,
        enabled=settings.provided.REDIS_ENABLED
    )

    event_publisher = providers.Singleton(
        KafkaProducerAdapter,
        bootstrap_servers=settings.provided.KAFKA_BOOTSTRAP_SERVERS,
        enabled=settings.provided.KAFKA_ENABLED
    )

    # 5. Security & AI
    token_service = providers.Singleton(
        JwtTokenAdapter,
        secret_key=settings.provided.JWT_SECRET_KEY,
        algorithm=settings.provided.JWT_ALGORITHM,
        default_expire_minutes=settings.provided.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

    password_hasher = providers.Singleton(BcryptPasswordHasher)

    ai_service = providers.Singleton(
        AIServiceAdapter,
        provider=settings.provided.AI_PROVIDER,
        gemini_api_key=settings.provided.GEMINI_API_KEY,
        gemini_model=settings.provided.GEMINI_MODEL,
        openai_api_key=settings.provided.OPENAI_API_KEY,
        openai_model=settings.provided.OPENAI_MODEL,
        timeout_ms=settings.provided.GEMINI_TIMEOUT_MS
    )

    # 6. Service Factory
    service_factory = providers.Factory(
        ServiceFactory,
        uow=uow,
        ai_service=ai_service,
        cache_service=cache_service,
        event_publisher=event_publisher,
        token_service=token_service,
        password_hasher=password_hasher,
        settings=settings
    )

    # 7. Mediator Bus
    mediator = providers.Singleton(
        _init_mediator,
        service_factory=service_factory
    )
