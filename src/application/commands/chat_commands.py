from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, kw_only=True)
class SendMessageCommand:
    session_id: str
    message: str


@dataclass(frozen=True, kw_only=True)
class DeleteConversationCommand:
    session_id: str


@dataclass(frozen=True, kw_only=True)
class AuthenticateUserCommand:
    email: str
    password: str


@dataclass(frozen=True, kw_only=True)
class RegisterUserCommand:
    email: str
    password: str
    full_name: str
    role: str = "customer"
