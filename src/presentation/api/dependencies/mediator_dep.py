from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from src.application.mediator.mediator import Mediator
from src.infrastructure.ioc.container import Container


@inject
def get_mediator(
    mediator: Mediator = Depends(Provide[Container.mediator])
) -> Mediator:
    """Inyecta la instancia singleton del Mediator."""
    return mediator
