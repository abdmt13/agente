from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from src.application.commands.chat_commands import (
    AuthenticateUserCommand,
    RegisterUserCommand,
)
from src.application.mediator.mediator import Mediator
from src.domain.exceptions.base import DomainException
from src.presentation.api.dependencies.mediator_dep import get_mediator
from src.presentation.api.dependencies.auth_guard import get_current_user_claims, require_roles
from src.presentation.api.dtos.auth_requests import (
    LoginBody,
    RegisterBody,
    LoginRequestDTO,
    RegisterRequestDTO,
)

router = APIRouter(prefix="/auth", tags=["Autenticación y Usuarios"])


def get_login_dto(body: LoginBody) -> LoginRequestDTO:
    return LoginRequestDTO(email=str(body.email), password=body.password)


def get_register_dto(body: RegisterBody) -> RegisterRequestDTO:
    return RegisterRequestDTO(
        email=str(body.email),
        password=body.password,
        full_name=body.full_name,
        role=body.role
    )


@router.post("/login", summary="Iniciar sesión y obtener token JWT stateless")
async def login(
    dto: LoginRequestDTO = Depends(get_login_dto),
    mediator: Mediator = Depends(get_mediator),
) -> Dict[str, Any]:
    """Controlador que solo despacha al Mediator."""
    try:
        command = AuthenticateUserCommand(email=dto.email, password=dto.password)
        token_dto = await mediator.send(command)
        return {
            "access_token": token_dto.access_token,
            "token_type": token_dto.token_type,
            "expires_in": token_dto.expires_in,
            "user": {
                "id": token_dto.user.id,
                "email": token_dto.user.email,
                "full_name": token_dto.user.full_name,
                "role": token_dto.user.role,
                "permissions": token_dto.user.permissions,
            }
        }
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/register", summary="Registrar nuevo usuario", status_code=status.HTTP_201_CREATED)
async def register(
    dto: RegisterRequestDTO = Depends(get_register_dto),
    mediator: Mediator = Depends(get_mediator),
) -> Dict[str, Any]:
    """Controlador que solo despacha al Mediator."""
    if dto.role != "customer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="El registro público solo permite cuentas de cliente.")
    try:
        command = RegisterUserCommand(
            email=dto.email,
            password=dto.password,
            full_name=dto.full_name,
            role=dto.role
        )
        user_dto = await mediator.send(command)
        return {
            "id": user_dto.id,
            "email": user_dto.email,
            "full_name": user_dto.full_name,
            "role": user_dto.role,
            "permissions": user_dto.permissions,
            "is_active": user_dto.is_active
        }
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/me", summary="Obtener perfil del usuario autenticado actual")
async def get_me(
    claims: Dict[str, Any] = Depends(get_current_user_claims),
) -> Dict[str, Any]:
    """Endpoint protegido con JWT stateless."""
    return {
        "user_id": claims.get("sub"),
        "email": claims.get("email"),
        "role": claims.get("role"),
        "permissions": claims.get("permissions", [])
    }
