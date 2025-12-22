from __future__ import annotations

from typing import Dict, Any, List

import requests

from ..domain.models import RecipeQuery, RecipeSummary, RecipeDetails


def _extract_mealdb_ingredients(meal_json: Dict[str, Any]) -> List[str]:
    out: List[str] = []
    for idx in range(1, 21):
        ing = (meal_json.get(f"strIngredient{idx}") or "").strip()
        if ing:
            out.append(ing)
    return out


class MealDbAdapter:
    """Adapts TheMealDB API to our RecipeProvider interface."""

    BASE = "https://www.themealdb.com/api/json/v1/1"
    SOURCE_NAME = "mealdb"

    def _get(self, path: str, params: Dict[str, str]) -> Dict[str, Any]:
        r = requests.get(f"{self.BASE}/{path}", params=params, timeout=10)
        r.raise_for_status()
        return r.json()

    def search(self, query: RecipeQuery) -> List[RecipeSummary]:
        kw = query.keyword or (query.have[0] if query.have else "")
        data = self._get("search.php", {"s": kw})
        meals = data.get("meals") or []
        results: List[RecipeSummary] = []

        for m in meals:
            ingredients = _extract_mealdb_ingredients(m)
            results.append(
                RecipeSummary(
                    id=str(m["idMeal"]),
                    title=m.get("strMeal", "").strip(),
                    image_url=m.get("strMealThumb"),
                    source=self.SOURCE_NAME,
                    ingredients=[i.lower() for i in ingredients],
                )
            )

        return results

    def details(self, recipe_id: str) -> RecipeDetails:
        data = self._get("lookup.php", {"i": recipe_id})
        meals = data.get("meals") or []
        if not meals:
            raise ValueError(f"Recipe id {recipe_id} not found")
        m = meals[0]
        ingredients = _extract_mealdb_ingredients(m)
        instructions = (m.get("strInstructions") or "").strip()

        return RecipeDetails(
            id=str(m["idMeal"]),
            title=(m.get("strMeal") or "").strip(),
            instructions=instructions,
            ingredients=[i.lower() for i in ingredients],
            image_url=m.get("strMealThumb"),
            source=self.SOURCE_NAME,
        )

