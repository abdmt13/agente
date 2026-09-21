from typing import List, Optional
from src.domain.exceptions.base import EntityNotFoundException
from src.interfaces.ports.unit_of_work import IUnitOfWork
from src.interfaces.ports.cache_service import ICacheService
from src.interfaces.dtos.property_dto import (
    PropertyDTO,
    DevelopmentDTO,
    FAQDTO,
    BusinessContextDTO,
)


class GetCatalogUseCase:
    def __init__(self, uow: IUnitOfWork, cache_service: ICacheService):
        self._uow = uow
        self._cache_service = cache_service

    async def execute(self, limit: int = 51) -> List[PropertyDTO]:
        async with self._uow as uow:
            props, _ = await uow.properties.get_available_properties(limit=limit)
            return [
                PropertyDTO(
                    id=p.id,
                    codigo=p.codigo,
                    nombre=p.nombre,
                    tipo=p.tipo,
                    precio=p.precio,
                    recamaras=p.recamaras,
                    banos=p.banos,
                    construccion_m2=p.construccion_m2,
                    terreno_m2=p.terreno_m2,
                    descripcion=p.descripcion,
                    disponibilidad=p.disponibilidad,
                    desarrollo=DevelopmentDTO(
                        id=p.desarrollo.id,
                        nombre=p.desarrollo.nombre,
                        ciudad=p.desarrollo.ciudad,
                        estado=p.desarrollo.estado,
                        zona=p.desarrollo.zona
                    ) if p.desarrollo else None
                )
                for p in props
            ]


class GetBusinessContextUseCase:
    def __init__(self, uow: IUnitOfWork, cache_service: ICacheService):
        self._uow = uow
        self._cache_service = cache_service

    async def execute(self) -> BusinessContextDTO:
        async with self._uow as uow:
            props, truncated = await uow.properties.get_available_properties(limit=51)
            faqs = await uow.properties.get_active_faqs(limit=30)

            prop_dtos = [
                PropertyDTO(
                    id=p.id,
                    codigo=p.codigo,
                    nombre=p.nombre,
                    tipo=p.tipo,
                    precio=p.precio,
                    recamaras=p.recamaras,
                    banos=p.banos,
                    construccion_m2=p.construccion_m2,
                    terreno_m2=p.terreno_m2,
                    descripcion=p.descripcion,
                    disponibilidad=p.disponibilidad,
                    desarrollo=DevelopmentDTO(
                        id=p.desarrollo.id,
                        nombre=p.desarrollo.nombre,
                        ciudad=p.desarrollo.ciudad,
                        estado=p.desarrollo.estado,
                        zona=p.desarrollo.zona
                    ) if p.desarrollo else None
                )
                for p in props
            ]

            faq_dtos = [
                FAQDTO(
                    id=f.id,
                    pregunta=f.pregunta,
                    respuesta=f.respuesta
                )
                for f in faqs
            ]

            return BusinessContextDTO(
                properties=prop_dtos,
                faqs=faq_dtos,
                truncated=truncated
            )
