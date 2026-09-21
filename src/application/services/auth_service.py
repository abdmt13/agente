from src.interfaces.dtos.user_dto import UserDTO, TokenDTO
from src.application.use_cases.auth_use_cases import (
    AuthenticateUserUseCase,
    RegisterUserUseCase,
)


class AuthService:
    def __init__(
        self,
        authenticate_uc: AuthenticateUserUseCase,
        register_uc: RegisterUserUseCase,
    ):
        self._authenticate_uc = authenticate_uc
        self._register_uc = register_uc

    async def authenticate(self, email: str, password: str) -> TokenDTO:
        return await self._authenticate_uc.execute(email=email, password=password)

    async def register(self, email: str, password: str, full_name: str, role: str = "customer") -> UserDTO:
        return await self._register_uc.execute(email=email, password=password, full_name=full_name, role=role)
