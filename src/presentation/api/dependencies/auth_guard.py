from typing import Any, Dict, List, Optional
from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.interfaces.ports.token_service import ITokenService
from src.infrastructure.ioc.container import Container

security_scheme = HTTPBearer(auto_error=False)


@inject
def get_current_user_claims(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_scheme),
    token_service: ITokenService = Depends(Provide[Container.token_service]),
) -> Dict[str, Any]:
    """Valida el token JWT y extrae los claims del usuario."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere un token de autenticación Bearer válido.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        claims = token_service.decode_access_token(credentials.credentials)
        return claims
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_roles(allowed_roles: List[str]):
    """Guardia de seguridad basada en Roles."""
    def role_checker(claims: Dict[str, Any] = Depends(get_current_user_claims)) -> Dict[str, Any]:
        user_role = claims.get("role", "customer")
        if user_role not in allowed_roles and user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado: se requiere uno de los siguientes roles: {allowed_roles}"
            )
        return claims
    return role_checker


def require_permissions(required_permissions: List[str]):
    """Guardia de seguridad basada en Permisos."""
    def permission_checker(claims: Dict[str, Any] = Depends(get_current_user_claims)) -> Dict[str, Any]:
        user_role = claims.get("role", "")
        if user_role == "admin":
            return claims

        user_perms = claims.get("permissions", [])
        for perm in required_permissions:
            if perm not in user_perms:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Acceso denegado: falta el permiso '{perm}'"
                )
        return claims
    return permission_checker
