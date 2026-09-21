from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.message import Message


class IAIService(ABC):
    @abstractmethod
    async def generate_reply(
        self,
        user_message: str,
        history: List[Message],
        system_instruction: str,
        previous_response_id: Optional[str] = None
    ) -> tuple[str, Optional[str]]:
        """Retorna (reply_text, response_id)."""
        raise NotImplementedError
