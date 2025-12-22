from __future__ import annotations

from typing import Protocol, List

from ..domain.models import RecipeQuery, RecipeSummary, RecipeDetails


class RecipeProvider(Protocol):
    def search(self, query: RecipeQuery) -> List[RecipeSummary]:
        ...

    def details(self, recipe_id: str) -> RecipeDetails:
        ...

