from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class RecipeSummary:
    id: str
    title: str
    image_url: Optional[str]
    source: str
    ingredients: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class RecipeDetails:
    id: str
    title: str
    instructions: str
    ingredients: List[str]
    image_url: Optional[str]
    source: str


@dataclass(frozen=True)
class RecipeQuery:
    have: List[str]
    exclude: List[str] = field(default_factory=list)
    keyword: Optional[str] = None

