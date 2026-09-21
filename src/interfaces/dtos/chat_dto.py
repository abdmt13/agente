from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass(kw_only=True)
class ChatMessageDTO:
    id: Optional[int] = None
    session_id: str
    role: str
    content: str
    created_at: Optional[datetime] = None


@dataclass(kw_only=True)
class ChatResponseDTO:
    reply: str
    session_id: str
    demo: bool = False
    response_id: Optional[str] = None


@dataclass(kw_only=True)
class ConversationHistoryDTO:
    session_id: str
    messages: List[ChatMessageDTO] = field(default_factory=list)
