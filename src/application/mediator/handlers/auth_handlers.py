from src.application.commands.chat_commands import (
    AuthenticateUserCommand,
    RegisterUserCommand,
)
from src.application.mediator.mediator import IRequestHandler
from src.application.services.service_factory import ServiceFactory
from src.interfaces.dtos.user_dto import UserDTO, TokenDTO


class AuthenticateUserHandler(IRequestHandler):
    def __init__(self, service_factory: ServiceFactory):
        self._service_factory = service_factory

    async def handle(self, request: AuthenticateUserCommand) -> TokenDTO:
        service = self._service_factory.create_auth_service()
        return await service.authenticate(
            email=request.email,
            password=request.password
        )


class RegisterUserHandler(IRequestHandler):
    def __init__(self, service_factory: ServiceFactory):
        self._service_factory = service_factory

    async def handle(self, request: RegisterUserCommand) -> UserDTO:
        service = self._service_factory.create_auth_service()
        return await service.register(
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            role=request.role
        )
