from __future__ import annotations

from dataclasses import replace

from recipefinder.models import Recipe
from recipefinder.query_builder import RecipeQueryBuilder
from recipefinder.strategies import BestMatchStrategy, FewerMissingStrategy


def test_best_match_strategy_orders_by_score_and_respects_limit() -> None:
    recipes = [
        Recipe(
            title="Chicken & Rice Bowl",
            source="X",
            ingredients=["chicken", "rice", "salt"],
            instructions="spicy and good",
        ),
        Recipe(
            title="Spicy Chicken",
            source="X",
            ingredients=["chicken", "salt"],
            instructions="spicy",
        ),
        Recipe(
            title="Salt Snack",
            source="X",
            ingredients=["salt"],
            instructions="spicy",
        ),
    ]

    builder = (
        RecipeQueryBuilder()
        .with_ingredients(["chicken", "rice"])
        .with_keywords("spicy")
        .with_limit(2)
    )

    ordered = BestMatchStrategy().rank(recipes, builder)
    assert [recipe.title for recipe in ordered] == ["Chicken & Rice Bowl", "Spicy Chicken"]


def test_best_match_strategy_returns_first_n_when_no_filters() -> None:
    recipes = [
        Recipe(title="First", source="X", ingredients=["a"]),
        Recipe(title="Second", source="X", ingredients=["b"]),
        Recipe(title="Third", source="X", ingredients=["c"]),
    ]

    builder = RecipeQueryBuilder().with_limit(2)
    ordered = BestMatchStrategy().rank(recipes, builder)
    assert [recipe.title for recipe in ordered] == ["First", "Second"]


def test_fewer_missing_prefers_fewer_missing_then_shorter_lists() -> None:
    requested = ["chicken", "rice"]

    base = Recipe(title="Base", source="X", ingredients=["chicken", "rice", "salt"], instructions="")
    r1 = replace(base, title="Short", ingredients=["chicken", "rice"])  # missing 0, length 2
    r2 = replace(base, title="Long", ingredients=["chicken", "rice", "salt"])  # missing 0, length 3
    r3 = replace(base, title="MissingOne", ingredients=["chicken"])  # missing 1

    builder = RecipeQueryBuilder().with_ingredients(requested).with_keywords("").with_limit(10)

    ordered = FewerMissingStrategy().rank([r2, r3, r1], builder)
    assert [recipe.title for recipe in ordered[:3]] == ["Short", "Long", "MissingOne"]
