from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional


@dataclass(kw_only=True)
class Development:
    id: Optional[int] = None
    nombre: str
    ciudad: Optional[str] = None
    estado: Optional[str] = None
    zona: Optional[str] = None
    activo: bool = True


@dataclass(kw_only=True)
class Property:
    id: Optional[int] = None
    codigo: str
    nombre: str
    tipo: str
    precio: Decimal
    recamaras: int = 0
    banos: Decimal = Decimal("0.0")
    construccion_m2: Optional[Decimal] = None
    terreno_m2: Optional[Decimal] = None
    descripcion: Optional[str] = None
    disponibilidad: str = "Disponible"
    desarrollo_id: Optional[int] = None
    desarrollo: Optional[Development] = None
