from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass(kw_only=True)
class Message:
    id: Optional[int] = None
    session_id: str
    role: str  # 'user' | 'assistant' | 'system'
    content: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
