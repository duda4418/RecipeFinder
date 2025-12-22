from __future__ import annotations

from typing import Optional, List

from .events import EventBus
from .models import RecipeQuery, RecipeSummary, RecipeDetails
from .strategies import RankStrategy
from ..providers.base import RecipeProvider


class RecipeAppFacade:
    def __init__(self, provider: RecipeProvider, bus: Optional[EventBus] = None) -> None:
        self.provider = provider
        self.bus = bus or EventBus()

    def search(self, query: RecipeQuery, strategy: RankStrategy, top_n: int = 5) -> List[RecipeSummary]:
        self.bus.emit("fetch_started", {"type": "search"})
        recipes = self.provider.search(query)
        self.bus.emit("fetch_succeeded", {"count": len(recipes)})

        ranked = strategy.sort(recipes, query)
        self.bus.emit("rank_completed", {"strategy": getattr(strategy, "name", "custom")})
        return ranked[:top_n]

    def details(self, recipe_id: str) -> RecipeDetails:
        self.bus.emit("fetch_started", {"type": "details", "id": recipe_id})
        d = self.provider.details(recipe_id)
        self.bus.emit("fetch_succeeded", {"id": recipe_id})
        return d

