from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class ITokenService(ABC):
    @abstractmethod
    def create_access_token(self, payload: Dict[str, Any], expires_delta_seconds: Optional[int] = None) -> str:
        raise NotImplementedError

    @abstractmethod
    def decode_access_token(self, token: str) -> Dict[str, Any]:
        raise NotImplementedError
