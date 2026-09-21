from typing import Any, Callable, Dict, Type, TypeVar
import structlog
from src.infrastructure.monitoring.prometheus import MEDIATOR_DISPATCH_COUNT

logger = structlog.get_logger()

TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")


class IRequestHandler:
    async def handle(self, request: Any) -> Any:
        raise NotImplementedError


class Mediator:
    """Implementación de Patrón Mediator / Bus asíncrono para CQRS."""

    def __init__(self):
        self._handlers: Dict[Type, Callable[[], IRequestHandler] | IRequestHandler] = {}

    def register_handler(
        self,
        request_type: Type[TRequest],
        handler: IRequestHandler | Callable[[], IRequestHandler]
    ) -> None:
        """Registra un handler para un tipo específico de Command o Query."""
        self._handlers[request_type] = handler

    async def send(self, request: Any) -> Any:
        """Despacha una petición (Command o Query) al handler correspondiente."""
        req_type = type(request)
        handler_entry = self._handlers.get(req_type)

        if not handler_entry:
            logger.error("No se encontró handler registrado para la petición", request_type=req_type.__name__)
            raise ValueError(f"No hay handler registrado para la petición de tipo '{req_type.__name__}'.")

        handler = handler_entry() if callable(handler_entry) and not isinstance(handler_entry, IRequestHandler) else handler_entry
        handler_name = handler.__class__.__name__

        MEDIATOR_DISPATCH_COUNT.labels(
            request_type=req_type.__name__,
            handler=handler_name
        ).inc()

        logger.debug("Mediator despachando petición", request=req_type.__name__, handler=handler_name)
        return await handler.handle(request)
