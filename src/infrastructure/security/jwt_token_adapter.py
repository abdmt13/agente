from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import jwt
from src.domain.exceptions.auth import UnauthorizedException
from src.interfaces.ports.token_service import ITokenService


class JwtTokenAdapter(ITokenService):
    def __init__(self, secret_key: str, algorithm: str = "HS256", default_expire_minutes: int = 1440):
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._default_expire_minutes = default_expire_minutes

    def create_access_token(self, payload: Dict[str, Any], expires_delta_seconds: Optional[int] = None) -> str:
        to_encode = payload.copy()
        now = datetime.now(timezone.utc)
        if expires_delta_seconds:
            expire = now + timedelta(seconds=expires_delta_seconds)
        else:
            expire = now + timedelta(minutes=self._default_expire_minutes)

        to_encode.update({"exp": expire, "iat": now})
        encoded_jwt = jwt.encode(to_encode, self._secret_key, algorithm=self._algorithm)
        return encoded_jwt

    def decode_access_token(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException("El token de autenticación ha expirado.")
        except jwt.InvalidTokenError:
            raise UnauthorizedException("El token de autenticación es inválido.")
