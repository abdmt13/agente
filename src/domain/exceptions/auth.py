from src.domain.exceptions.base import DomainException


class AuthenticationException(DomainException):
    def __init__(self, message: str = "Credenciales de autenticación inválidas."):
        super().__init__(message)


class UnauthorizedException(DomainException):
    def __init__(self, message: str = "No tiene permisos para realizar esta acción."):
        super().__init__(message)


class UserAlreadyExistsException(DomainException):
    def __init__(self, email: str):
        super().__init__(f"El usuario con correo '{email}' ya existe.")
