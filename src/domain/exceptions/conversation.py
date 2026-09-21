from src.domain.exceptions.base import DomainException


class InvalidSessionException(DomainException):
    def __init__(self, session_id: str):
        super().__init__(f"El identificador de sesión '{session_id}' no es válido.")


class MessageTooLongException(DomainException):
    def __init__(self, max_length: int = 4000):
        super().__init__(f"El mensaje excede el límite máximo permitido de {max_length} caracteres.")
