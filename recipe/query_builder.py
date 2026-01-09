from typing import Dict, List, Optional


class RecipeQueryBuilder:
    """Builder pattern for consistent query construction across providers.

    Why: Each provider expects different query params; the builder centralizes how
    we assemble them so the UI stays provider-agnostic.
    Where: Used in RecipeService.fetch_recipes() before calling each API.
    Problem solved: Keeps request construction consistent and extendable without
    duplicating parameter logic in multiple places.
    """

    def __init__(self) -> None:
        self._keywords: Optional[str] = None
        self._ingredients: List[str] = []
        self._limit: int = 10

    def with_keywords(self, keywords: str) -> "RecipeQueryBuilder":
        self._keywords = keywords.strip() if keywords else None
        return self

    def with_ingredients(self, ingredients: List[str]) -> "RecipeQueryBuilder":
        self._ingredients = [item.strip() for item in ingredients if item.strip()]
        return self

    def with_limit(self, limit: int) -> "RecipeQueryBuilder":
        self._limit = max(1, min(limit, 25))
        return self

    def limit(self) -> int:
        return self._limit

    def build_for_mealdb(self) -> Dict[str, str]:
        if self._keywords:
            return {"s": self._keywords}
        if self._ingredients:
            return {"i": ",".join(self._ingredients)}
        return {"s": ""}

    def build_for_spoonacular(self, api_key: str) -> Dict[str, str]:
        return {
            "apiKey": api_key,
            "query": self._keywords or "",
            "includeIngredients": ",".join(self._ingredients),
            "number": self._limit,
            "addRecipeInformation": "true",
        }

    def requested_ingredients(self) -> List[str]:
        return list(self._ingredients)

    def requested_keywords(self) -> str:
        return self._keywords or ""
