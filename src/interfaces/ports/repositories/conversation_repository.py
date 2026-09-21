from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.conversation import Conversation
from src.domain.entities.message import Message


class IConversationRepository(ABC):
    @abstractmethod
    async def get_by_session_id(self, session_id: str) -> Optional[Conversation]:
        raise NotImplementedError

    @abstractmethod
    async def save_turn(
        self,
        session_id: str,
        user_message: str,
        assistant_reply: str,
        previous_response_id: Optional[str] = None
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_messages(self, session_id: str, recent_only: bool = False, limit: int = 20) -> List[Message]:
        raise NotImplementedError

    @abstractmethod
    async def delete_conversation(self, session_id: str) -> bool:
        raise NotImplementedError
