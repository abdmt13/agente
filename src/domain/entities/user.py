from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


@dataclass(kw_only=True)
class User:
    id: Optional[int] = None
    email: str
    password_hash: str
    full_name: str
    role: str = "customer"  # e.g., 'admin', 'agent', 'customer'
    permissions: List[str] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions or self.role == "admin"
