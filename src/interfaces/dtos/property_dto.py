from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional


@dataclass(kw_only=True)
class FAQDTO:
    id: Optional[int] = None
    pregunta: str
    respuesta: str


@dataclass(kw_only=True)
class DevelopmentDTO:
    id: Optional[int] = None
    nombre: str
    ciudad: Optional[str] = None
    estado: Optional[str] = None
    zona: Optional[str] = None


@dataclass(kw_only=True)
class PropertyDTO:
    id: Optional[int] = None
    codigo: str
    nombre: str
    tipo: str
    precio: Decimal
    recamaras: int
    banos: Decimal
    construccion_m2: Optional[Decimal] = None
    terreno_m2: Optional[Decimal] = None
    descripcion: Optional[str] = None
    disponibilidad: str
    desarrollo: Optional[DevelopmentDTO] = None


@dataclass(kw_only=True)
class BusinessContextDTO:
    properties: List[PropertyDTO] = field(default_factory=list)
    faqs: List[FAQDTO] = field(default_factory=list)
    truncated: bool = False
