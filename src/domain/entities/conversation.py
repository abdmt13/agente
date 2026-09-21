from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional
from src.domain.entities.message import Message


@dataclass(kw_only=True)
class Conversation:
    session_id: str
    previous_response_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    messages: List[Message] = field(default_factory=list)

    def add_message(self, role: str, content: str) -> Message:
        msg = Message(
            session_id=self.session_id,
            role=role,
            content=content,
            created_at=datetime.now(timezone.utc)
        )
        self.messages.append(msg)
        return msg
