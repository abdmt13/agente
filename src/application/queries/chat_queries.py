from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, kw_only=True)
class GetConversationHistoryQuery:
    session_id: str
    recent_only: bool = False
    limit: int = 20


@dataclass(frozen=True, kw_only=True)
class GetPropertiesCatalogQuery:
    limit: int = 51


@dataclass(frozen=True, kw_only=True)
class GetBusinessContextQuery:
    pass


@dataclass(frozen=True, kw_only=True)
class GetPropertyByCodeQuery:
    codigo: str


@dataclass(frozen=True, kw_only=True)
class GetUserProfileQuery:
    user_id: int
