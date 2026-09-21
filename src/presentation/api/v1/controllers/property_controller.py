from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from src.application.queries.chat_queries import (
    GetPropertiesCatalogQuery,
    GetBusinessContextQuery,
)
from src.application.mediator.mediator import Mediator
from src.domain.exceptions.base import DomainException
from src.presentation.api.dependencies.mediator_dep import get_mediator
from src.presentation.api.dtos.property_responses import GetCatalogRequestDTO

router = APIRouter(tags=["Propiedades y Catálogo"])


def get_catalog_dto(
    limit: int = Query(51, ge=1, le=200, description="Límite de propiedades")
) -> GetCatalogRequestDTO:
    return GetCatalogRequestDTO(limit=limit)


@router.get("/properties", summary="Obtener catálogo de propiedades disponibles")
async def get_properties(
    dto: GetCatalogRequestDTO = Depends(get_catalog_dto),
    mediator: Mediator = Depends(get_mediator),
) -> List[Dict[str, Any]]:
    """Controlador que solo despacha al Mediator."""
    try:
        query = GetPropertiesCatalogQuery(limit=dto.limit)
        properties = await mediator.send(query)
        return [
            {
                "id": p.id,
                "codigo": p.codigo,
                "nombre": p.nombre,
                "tipo": p.tipo,
                "precio": float(p.precio),
                "recamaras": p.recamaras,
                "banos": float(p.banos),
                "construccion_m2": float(p.construccion_m2) if p.construccion_m2 else None,
                "terreno_m2": float(p.terreno_m2) if p.terreno_m2 else None,
                "descripcion": p.descripcion,
                "disponibilidad": p.disponibilidad,
                "desarrollo": {
                    "id": p.desarrollo.id,
                    "nombre": p.desarrollo.nombre,
                    "ciudad": p.desarrollo.ciudad,
                    "estado": p.desarrollo.estado,
                    "zona": p.desarrollo.zona,
                } if p.desarrollo else None
            }
            for p in properties
        ]
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/business-context", summary="Obtener contexto completo del negocio (propiedades y faqs)")
async def get_business_context(
    mediator: Mediator = Depends(get_mediator),
) -> Dict[str, Any]:
    """Controlador que solo despacha al Mediator."""
    try:
        query = GetBusinessContextQuery()
        context = await mediator.send(query)
        return {
            "properties": [
                {
                    "id": p.id,
                    "codigo": p.codigo,
                    "nombre": p.nombre,
                    "tipo": p.tipo,
                    "precio": float(p.precio),
                    "recamaras": p.recamaras,
                    "banos": float(p.banos),
                    "construccion_m2": float(p.construccion_m2) if p.construccion_m2 else None,
                    "terreno_m2": float(p.terreno_m2) if p.terreno_m2 else None,
                    "descripcion": p.descripcion,
                    "disponibilidad": p.disponibilidad,
                    "desarrollo": p.desarrollo.nombre if p.desarrollo else None,
                    "ciudad": p.desarrollo.ciudad if p.desarrollo else None,
                    "zona": p.desarrollo.zona if p.desarrollo else None,
                }
                for p in context.properties
            ],
            "faqs": [
                {
                    "id": f.id,
                    "pregunta": f.pregunta,
                    "respuesta": f.respuesta
                }
                for f in context.faqs
            ],
            "truncated": context.truncated
        }
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
