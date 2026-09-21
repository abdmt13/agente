from src.application.commands.chat_commands import (
    SendMessageCommand,
    DeleteConversationCommand,
)
from src.application.queries.chat_queries import GetConversationHistoryQuery
from src.application.mediator.mediator import IRequestHandler
from src.application.services.service_factory import ServiceFactory
from src.interfaces.dtos.chat_dto import ChatResponseDTO, ConversationHistoryDTO


class SendMessageHandler(IRequestHandler):
    def __init__(self, service_factory: ServiceFactory):
        self._service_factory = service_factory

    async def handle(self, request: SendMessageCommand) -> ChatResponseDTO:
        service = self._service_factory.create_chat_service()
        return await service.send_message(
            session_id=request.session_id,
            message=request.message
        )


class GetConversationHistoryHandler(IRequestHandler):
    def __init__(self, service_factory: ServiceFactory):
        self._service_factory = service_factory

    async def handle(self, request: GetConversationHistoryQuery) -> ConversationHistoryDTO:
        service = self._service_factory.create_chat_service()
        return await service.get_history(
            session_id=request.session_id,
            recent_only=request.recent_only,
            limit=request.limit
        )


class DeleteConversationHandler(IRequestHandler):
    def __init__(self, service_factory: ServiceFactory):
        self._service_factory = service_factory

    async def handle(self, request: DeleteConversationCommand) -> bool:
        service = self._service_factory.create_chat_service()
        return await service.delete_conversation(session_id=request.session_id)
