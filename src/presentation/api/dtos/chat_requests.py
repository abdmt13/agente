from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel, Field


# 1. Pydantic Body Schemas
class SendMessageBody(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, description="Mensaje del usuario")
    sessionId: str = Field(..., min_length=1, max_length=100, description="Identificador de sesión")


# 2. Encapsulated Presentation DTOs with @dataclass for Depends()
@dataclass
class SendMessageRequestDTO:
    session_id: str
    message: str


@dataclass
class GetHistoryRequestDTO:
    session_id: str
    recent_only: bool = False
    limit: int = 20


@dataclass
class DeleteConversationRequestDTO:
    session_id: str
