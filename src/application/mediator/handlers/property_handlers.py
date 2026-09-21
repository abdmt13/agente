from typing import List
from src.application.queries.chat_queries import (
    GetPropertiesCatalogQuery,
    GetBusinessContextQuery,
)
from src.application.mediator.mediator import IRequestHandler
from src.application.services.service_factory import ServiceFactory
from src.interfaces.dtos.property_dto import PropertyDTO, BusinessContextDTO


class GetPropertiesCatalogHandler(IRequestHandler):
    def __init__(self, service_factory: ServiceFactory):
        self._service_factory = service_factory

    async def handle(self, request: GetPropertiesCatalogQuery) -> List[PropertyDTO]:
        service = self._service_factory.create_property_service()
        return await service.get_catalog(limit=request.limit)


class GetBusinessContextHandler(IRequestHandler):
    def __init__(self, service_factory: ServiceFactory):
        self._service_factory = service_factory

    async def handle(self, request: GetBusinessContextQuery) -> BusinessContextDTO:
        service = self._service_factory.create_property_service()
        return await service.get_business_context()
