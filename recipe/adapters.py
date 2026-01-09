import html
import re
from typing import Dict, List

from .models import Recipe


class RecipeAdapter:
    """Base adapter interface for unified recipe mapping."""

    def adapt(self, data: Dict) -> List[Recipe]:
        raise NotImplementedError


class MealDBAdapter(RecipeAdapter):
    """Adapter pattern for MealDB responses.

    Why: MealDB response shape differs from Spoonacular; adapter normalizes to Recipe.
    Where: RecipeService._fetch_mealdb uses this to map API output.
    Problem solved: Shields the rest of the app from provider-specific JSON layouts.
    """

    def adapt(self, data: Dict) -> List[Recipe]:
        meals = data.get("meals") or []
        recipes: List[Recipe] = []
        for meal in meals:
            ingredients = []
            for idx in range(1, 21):
                ingredient = meal.get(f"strIngredient{idx}") or ""
                measure = meal.get(f"strMeasure{idx}") or ""
                combined = f"{measure.strip()} {ingredient.strip()}".strip()
                if combined:
                    ingredients.append(combined)
            recipes.append(
                Recipe(
                    title=meal.get("strMeal", "Unknown Meal"),
                    source="MealDB",
                    ingredients=ingredients,
                    instructions=meal.get("strInstructions", ""),
                    image_url=meal.get("strMealThumb"),
                )
            )
        return recipes


class SpoonacularAdapter(RecipeAdapter):
    """Adapter pattern for Spoonacular responses.

    Why: Converts Spoonacular complexSearch results into the unified Recipe model.
    Where: RecipeService._fetch_spoonacular uses this to map API output.
    Problem solved: Avoids leaking Spoonacular field names into UI/rendering code.
    """

    def adapt(self, data: Dict) -> List[Recipe]:
        results = data.get("results") or []
        recipes: List[Recipe] = []
        for item in results:
            ingredients = []
            for ing in item.get("extendedIngredients", []) or []:
                name = ing.get("original") or ing.get("name") or ""
                if name:
                    ingredients.append(name)
            recipes.append(
                Recipe(
                    title=item.get("title", "Unknown Recipe"),
                    source="Spoonacular",
                    ingredients=ingredients,
                    instructions=_strip_html(item.get("summary", "")),
                    image_url=item.get("image"),
                )
            )
        return recipes


def _strip_html(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"<[^>]+>", "", text)
    return html.unescape(cleaned).strip()


if __name__ == "__main__":
    raise SystemExit(
        "This file is a package module. Run the app with: python main.py\n"
        "Or run this module with: python -m recipe.adapters"
    )
