class DomainException(Exception):
    """Excepción base para todas las excepciones del dominio."""
    def __init__(self, message: str = "Ocurrió un error en el dominio."):
        self.message = message
        super().__init__(self.message)


class EntityNotFoundException(DomainException):
    """Excepción cuando una entidad no es encontrada."""
    def __init__(self, entity_name: str, entity_id: str | int):
        super().__init__(f"{entity_name} con identificador '{entity_id}' no fue encontrado(a).")
        self.entity_name = entity_name
        self.entity_id = entity_id


class ValidationException(DomainException):
    """Excepción para violaciones de reglas de negocio/validaciones."""
    pass
