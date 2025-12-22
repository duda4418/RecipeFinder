from __future__ import annotations

from typing import Protocol, List, Dict

from .models import RecipeSummary, RecipeQuery


class RankStrategy(Protocol):
    name: str

    def sort(self, recipes: List[RecipeSummary], query: RecipeQuery) -> List[RecipeSummary]:
        ...


class FewestMissingStrategy:
    name = "fewest_missing"

    def sort(self, recipes: List[RecipeSummary], query: RecipeQuery) -> List[RecipeSummary]:
        have = set(query.have)
        exclude = set(query.exclude)

        def key(r: RecipeSummary):
            ings = set(r.ingredients)
            if ings & exclude:
                return (10_000, 10_000)
            missing = len([i for i in ings if i and i not in have])
            matching = len([i for i in ings if i in have])
            return (missing, -matching)

        return sorted(recipes, key=key)


class MostMatchingStrategy:
    name = "most_matching"

    def sort(self, recipes: List[RecipeSummary], query: RecipeQuery) -> List[RecipeSummary]:
        have = set(query.have)
        exclude = set(query.exclude)

        def key(r: RecipeSummary):
            ings = set(r.ingredients)
            if ings & exclude:
                return -1
            return len([i for i in ings if i in have])

        return sorted(recipes, key=key, reverse=True)


STRATEGIES: Dict[str, RankStrategy] = {
    FewestMissingStrategy.name: FewestMissingStrategy(),
    MostMatchingStrategy.name: MostMatchingStrategy(),
}

