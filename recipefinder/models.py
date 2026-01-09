from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Recipe:
    """Unified recipefinder model produced by adapters."""

    title: str
    source: str
    ingredients: List[str] = field(default_factory=list)
    instructions: str = ""
    image_url: Optional[str] = None
