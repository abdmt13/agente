from src.interfaces.dtos.chat_dto import ChatResponseDTO, ConversationHistoryDTO
from src.application.use_cases.send_chat_message_use_case import SendChatMessageUseCase
from src.application.use_cases.conversation_use_cases import (
    GetConversationUseCase,
    DeleteConversationUseCase,
)


class ChatService:
    def __init__(
        self,
        send_message_uc: SendChatMessageUseCase,
        get_conversation_uc: GetConversationUseCase,
        delete_conversation_uc: DeleteConversationUseCase,
    ):
        self._send_message_uc = send_message_uc
        self._get_conversation_uc = get_conversation_uc
        self._delete_conversation_uc = delete_conversation_uc

    async def send_message(self, session_id: str, message: str) -> ChatResponseDTO:
        return await self._send_message_uc.execute(session_id=session_id, message=message)

    async def get_history(self, session_id: str, recent_only: bool = False, limit: int = 20) -> ConversationHistoryDTO:
        return await self._get_conversation_uc.execute(session_id=session_id, recent_only=recent_only, limit=limit)

    async def delete_conversation(self, session_id: str) -> bool:
        return await self._delete_conversation_uc.execute(session_id=session_id)
