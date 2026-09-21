from typing import List
from src.interfaces.dtos.property_dto import PropertyDTO, BusinessContextDTO
from src.application.use_cases.property_use_cases import (
    GetCatalogUseCase,
    GetBusinessContextUseCase,
)


class PropertyService:
    def __init__(
        self,
        get_catalog_uc: GetCatalogUseCase,
        get_business_context_uc: GetBusinessContextUseCase,
    ):
        self._get_catalog_uc = get_catalog_uc
        self._get_business_context_uc = get_business_context_uc

    async def get_catalog(self, limit: int = 51) -> List[PropertyDTO]:
        return await self._get_catalog_uc.execute(limit=limit)

    async def get_business_context(self) -> BusinessContextDTO:
        return await self._get_business_context_uc.execute()
