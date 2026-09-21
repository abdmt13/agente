from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from src.domain.entities.property import Property
from src.domain.entities.faq import FAQ


class IPropertyRepository(ABC):
    @abstractmethod
    async def get_available_properties(self, limit: int = 51) -> Tuple[List[Property], bool]:
        """Retorna lista de propiedades disponibles y booleano indicando si fue truncado."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_codigo(self, codigo: str) -> Optional[Property]:
        raise NotImplementedError

    @abstractmethod
    async def get_active_faqs(self, limit: int = 30) -> List[FAQ]:
        raise NotImplementedError
