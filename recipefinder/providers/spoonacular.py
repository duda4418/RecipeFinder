from __future__ import annotations

from typing import Dict, Any, List

import requests

from ..domain.models import RecipeQuery, RecipeSummary, RecipeDetails


class SpoonacularAdapter:
    """Adapts Spoonacular API to our RecipeProvider interface."""

    BASE = "https://api.spoonacular.com"
    SOURCE_NAME = "spoon"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def _get(self, path: str, params: Dict[str, str]) -> Dict[str, Any]:
        params = {**params, "apiKey": self.api_key}
        r = requests.get(f"{self.BASE}{path}", params=params, timeout=10)
        r.raise_for_status()
        return r.json()

    def search(self, query: RecipeQuery) -> List[RecipeSummary]:
        params: Dict[str, str] = {
            "number": "10",
            "addRecipeInformation": "true",
        }

        if query.keyword:
            params["query"] = query.keyword

        if query.have:
            params["includeIngredients"] = ",".join(query.have)

        if query.exclude:
            params["excludeIngredients"] = ",".join(query.exclude)

        data = self._get("/recipes/complexSearch", params)
        results: List[RecipeSummary] = []

        for item in data.get("results", []):
            rid = str(item["id"])
            title = item.get("title", "").strip()
            image = item.get("image")

            ex_ings = item.get("extendedIngredients") or []
            ingredients = [
                (ing.get("name") or "").strip().lower()
                for ing in ex_ings
                if (ing.get("name") or "").strip()
            ]

            results.append(
                RecipeSummary(
                    id=rid,
                    title=title,
                    image_url=image,
                    source=self.SOURCE_NAME,
                    ingredients=ingredients,
                )
            )

        return results

    def details(self, recipe_id: str) -> RecipeDetails:
        data = self._get(f"/recipes/{recipe_id}/information", {})
        title = (data.get("title") or "").strip()
        image = data.get("image")

        ex_ings = data.get("extendedIngredients") or []
        ingredients = [
            (ing.get("name") or "").strip().lower()
            for ing in ex_ings
            if (ing.get("name") or "").strip()
        ]

        instructions = data.get("instructions") or ""
        if not instructions:
            instructions = data.get("summary") or ""

        return RecipeDetails(
            id=str(data.get("id")),
            title=title,
            instructions=instructions.strip(),
            ingredients=ingredients,
            image_url=image,
            source=self.SOURCE_NAME,
        )

