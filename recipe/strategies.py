from __future__ import annotations

from typing import List, Protocol, Tuple

from .models import Recipe
from .query_builder import RecipeQueryBuilder


class RecipeStrategy(Protocol):
    """Strategy interface that ranks recipes based on the user's query."""

    name: str

    def rank(self, recipes: List[Recipe], builder: RecipeQueryBuilder) -> List[Recipe]:
        ...


class BestMatchStrategy:
    name = "Best match (most hits)"

    def rank(self, recipes: List[Recipe], builder: RecipeQueryBuilder) -> List[Recipe]:
        requested_ing = [item.lower() for item in builder.requested_ingredients() if item]
        requested_kw = [kw.lower() for kw in builder.requested_keywords().split() if kw]
        if not requested_ing and not requested_kw:
            return recipes[: builder.limit()]

        def score(recipe: Recipe) -> Tuple[int, int, int, int]:
            ing_matches = sum(
                1 for req in requested_ing if any(req in ing.lower() for ing in recipe.ingredients)
            )
            missing = max(0, len(requested_ing) - ing_matches) if requested_ing else 0
            kw_hits = 0
            text_blob = (recipe.title + "\n" + (recipe.instructions or "")).lower()
            for kw in requested_kw:
                if kw in text_blob:
                    kw_hits += 1
            total_score = ing_matches * 2 + kw_hits  # weight ingredients higher than keywords
            return total_score, ing_matches, kw_hits, missing

        scored = []
        for recipe in recipes:
            total_score, ing_matches, kw_hits, missing = score(recipe)
            scored.append((total_score, ing_matches, kw_hits, missing, len(recipe.ingredients), recipe))

        scored.sort(
            key=lambda item: (
                -item[0],  # overall score
                -item[1],  # ingredient matches
                -item[2],  # keyword hits
                item[3],   # missing ingredients
                item[4],   # shorter ingredient lists first
                item[5].title.lower(),
            )
        )
        return [item[5] for item in scored[: builder.limit()]]


class FewerMissingStrategy:
    name = "Fewer missing ingredients"

    def rank(self, recipes: List[Recipe], builder: RecipeQueryBuilder) -> List[Recipe]:
        requested_ing = [item.lower() for item in builder.requested_ingredients() if item]
        requested_kw = [kw.lower() for kw in builder.requested_keywords().split() if kw]
        if not requested_ing and not requested_kw:
            return recipes[: builder.limit()]

        def score(recipe: Recipe) -> Tuple[int, int, int, int]:
            ing_matches = sum(
                1 for req in requested_ing if any(req in ing.lower() for ing in recipe.ingredients)
            )
            missing = max(0, len(requested_ing) - ing_matches) if requested_ing else 0
            kw_hits = 0
            text_blob = (recipe.title + "\n" + (recipe.instructions or "")).lower()
            for kw in requested_kw:
                if kw in text_blob:
                    kw_hits += 1
            return missing, ing_matches, kw_hits, len(recipe.ingredients)

        scored = []
        for recipe in recipes:
            missing, ing_matches, kw_hits, ing_length = score(recipe)
            scored.append((missing, ing_matches, kw_hits, ing_length, recipe))

        scored.sort(
            key=lambda item: (
                item[0],   # fewest missing first
                item[3],   # shorter recipes next
                -item[2],  # then keyword hits
                -item[1],  # then ingredient matches
                item[4].title.lower(),
            )
        )
        return [item[4] for item in scored[: builder.limit()]]
