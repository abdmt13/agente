from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass(kw_only=True)
class UserDTO:
    id: Optional[int] = None
    email: str
    full_name: str
    role: str
    permissions: List[str] = field(default_factory=list)
    is_active: bool = True
    created_at: Optional[datetime] = None


@dataclass(kw_only=True)
class TokenDTO:
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserDTO
