from dataclasses import dataclass
from typing import Optional


@dataclass
class GetCatalogRequestDTO:
    limit: int = 51
