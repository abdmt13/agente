from typing import List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.domain.entities.property import Property, Development
from src.domain.entities.faq import FAQ
from src.infrastructure.database.models.property_model import (
    PropertyModel,
    DevelopmentModel,
    FAQModel,
)
from src.interfaces.ports.repositories.property_repository import IPropertyRepository


class PropertyRepositoryImpl(IPropertyRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_property_entity(self, model: PropertyModel) -> Property:
        dev_entity = None
        if model.desarrollo:
            dev_entity = Development(
                id=model.desarrollo.id,
                nombre=model.desarrollo.nombre,
                ciudad=model.desarrollo.ciudad,
                estado=model.desarrollo.estado,
                zona=model.desarrollo.zona,
                activo=model.desarrollo.activo
            )
        return Property(
            id=model.id,
            codigo=model.codigo,
            nombre=model.nombre,
            tipo=model.tipo,
            precio=model.precio,
            recamaras=model.recamaras,
            banos=model.banos,
            construccion_m2=model.construccion_m2,
            terreno_m2=model.terreno_m2,
            descripcion=model.descripcion,
            disponibilidad=model.disponibilidad,
            desarrollo_id=model.desarrollo_id,
            desarrollo=dev_entity
        )

    async def get_available_properties(self, limit: int = 51) -> Tuple[List[Property], bool]:
        stmt = (
            select(PropertyModel)
            .outerjoin(DevelopmentModel, DevelopmentModel.id == PropertyModel.desarrollo_id)
            .options(selectinload(PropertyModel.desarrollo))
            .where(PropertyModel.disponibilidad == "Disponible")
            .where((DevelopmentModel.id.is_(None)) | (DevelopmentModel.activo == True))
            .order_by(PropertyModel.precio, PropertyModel.id)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        truncated = len(models) >= limit
        properties = [self._to_property_entity(m) for m in models[:50]]
        return properties, truncated

    async def get_by_codigo(self, codigo: str) -> Optional[Property]:
        stmt = (
            select(PropertyModel)
            .options(selectinload(PropertyModel.desarrollo))
            .where(PropertyModel.codigo == codigo)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_property_entity(model) if model else None

    async def get_active_faqs(self, limit: int = 30) -> List[FAQ]:
        stmt = (
            select(FAQModel)
            .where(FAQModel.activo == True)
            .order_by(FAQModel.id)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [
            FAQ(
                id=m.id,
                pregunta=m.pregunta,
                respuesta=m.respuesta,
                activo=m.activo
            )
            for m in models
        ]
