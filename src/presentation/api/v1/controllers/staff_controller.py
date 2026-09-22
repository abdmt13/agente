from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.presentation.api.dependencies.auth_guard import require_roles
from src.infrastructure.database.models.property_model import DevelopmentModel, PropertyModel, FAQModel

router = APIRouter(prefix="/staff", tags=["Captura del personal"], dependencies=[Depends(require_roles(["agent", "admin"]))])


class DevelopmentBody(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    ciudad: str = Field(min_length=2, max_length=100)
    estado: str = Field(min_length=2, max_length=100)
    zona: Optional[str] = Field(default=None, max_length=150)
    activo: bool = True


class PropertyBody(BaseModel):
    codigo: str = Field(min_length=1, max_length=50)
    nombre: str = Field(min_length=2, max_length=150)
    tipo: str = Field(pattern="^(Casa|Departamento|Terreno)$")
    precio: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    recamaras: int = Field(default=0, ge=0)
    banos: Decimal = Field(default=Decimal("0"), ge=0, max_digits=3, decimal_places=1)
    construccion_m2: Optional[Decimal] = Field(default=None, ge=0, max_digits=8, decimal_places=2)
    terreno_m2: Optional[Decimal] = Field(default=None, ge=0, max_digits=8, decimal_places=2)
    descripcion: Optional[str] = None
    disponibilidad: str = Field(default="Disponible", pattern="^(Disponible|Apartada|Vendida|No disponible)$")
    desarrollo_id: Optional[int] = None


class FAQBody(BaseModel):
    categoria: str = Field(min_length=2, max_length=100)
    pregunta: str = Field(min_length=2, max_length=500)
    respuesta: str = Field(min_length=2)
    activo: bool = True


def _serialize(model):
    return {column.name: getattr(model, column.name) for column in model.__table__.columns}


@router.get("/catalog")
async def list_catalog(request: Request):
    async with request.app.state.container.db_manager().session_factory() as session:
        developments = (await session.execute(select(DevelopmentModel).order_by(DevelopmentModel.id.desc()))).scalars().all()
        properties = (await session.execute(select(PropertyModel).order_by(PropertyModel.id.desc()))).scalars().all()
        faqs = (await session.execute(select(FAQModel).order_by(FAQModel.id.desc()))).scalars().all()
        return {"developments": [_serialize(x) for x in developments], "properties": [_serialize(x) for x in properties], "faqs": [_serialize(x) for x in faqs]}


async def _save(request: Request, model_type, body, item_id=None):
    async with request.app.state.container.db_manager().session_factory() as session:
        model = await session.get(model_type, item_id) if item_id is not None else model_type()
        if model is None:
            raise HTTPException(status_code=404, detail="Registro no encontrado")
        for key, value in body.model_dump().items():
            setattr(model, key, value)
        if isinstance(model, PropertyModel) and model.desarrollo_id is not None:
            if await session.get(DevelopmentModel, model.desarrollo_id) is None:
                raise HTTPException(status_code=400, detail="El desarrollo no existe")
        session.add(model)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=409, detail="Código duplicado o referencia inválida")
        await session.refresh(model)
        return _serialize(model)


@router.post("/developments", status_code=status.HTTP_201_CREATED)
async def create_development(body: DevelopmentBody, request: Request):
    return await _save(request, DevelopmentModel, body)


@router.put("/developments/{item_id}")
async def update_development(item_id: int, body: DevelopmentBody, request: Request):
    return await _save(request, DevelopmentModel, body, item_id)


@router.post("/properties", status_code=status.HTTP_201_CREATED)
async def create_property(body: PropertyBody, request: Request):
    return await _save(request, PropertyModel, body)


@router.put("/properties/{item_id}")
async def update_property(item_id: int, body: PropertyBody, request: Request):
    return await _save(request, PropertyModel, body, item_id)


@router.post("/faqs", status_code=status.HTTP_201_CREATED)
async def create_faq(body: FAQBody, request: Request):
    return await _save(request, FAQModel, body)


@router.put("/faqs/{item_id}")
async def update_faq(item_id: int, body: FAQBody, request: Request):
    return await _save(request, FAQModel, body, item_id)
