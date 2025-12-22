from __future__ import annotations

from typing import List, Any, Optional

from ..domain.models import RecipeQuery, RecipeSummary, RecipeDetails
from .base import RecipeProvider


class CombinedProvider:
    """Calls multiple RecipeProviders and merges results."""

    def __init__(self, providers: List[RecipeProvider]) -> None:
        self.providers = providers

    def search(self, query: RecipeQuery) -> List[RecipeSummary]:
        merged: List[RecipeSummary] = []

        for provider in self.providers:
            source_name = getattr(provider, "SOURCE_NAME", provider.__class__.__name__.lower())
            summaries = provider.search(query)
            for s in summaries:
                global_id = f"{source_name}:{s.id}"
                merged.append(
                    RecipeSummary(
                        id=global_id,
                        title=s.title,
                        image_url=s.image_url,
                        source=source_name,
                        ingredients=s.ingredients,
                    )
                )

        seen: set[tuple[str, str]] = set()
        deduped: List[RecipeSummary] = []
        for r in merged:
            key = (r.title.lower(), r.source)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(r)

        return deduped

    def details(self, recipe_id: str) -> RecipeDetails:
        try:
            source, local_id = recipe_id.split(":", 1)
        except ValueError:
            raise ValueError(
                f"Invalid recipe id '{recipe_id}'. "
                "Expected format '<source>:<id>', e.g. 'mealdb:52795' or 'spoon:12345'."
            )

        for provider in self.providers:
            if getattr(provider, "SOURCE_NAME", None) == source:
                d = provider.details(local_id)
                return RecipeDetails(
                    id=recipe_id,
                    title=d.title,
                    instructions=d.instructions,
                    ingredients=d.ingredients,
                    image_url=d.image_url,
                    source=source,
                )

        raise ValueError(f"No provider registered for source '{source}'")

