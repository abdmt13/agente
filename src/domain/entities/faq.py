from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class FAQ:
    id: Optional[int] = None
    pregunta: str
    respuesta: str
    activo: bool = True
