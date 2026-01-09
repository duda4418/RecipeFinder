from recipefinder.query_builder import RecipeQueryBuilder


def test_with_limit_clamps_between_1_and_configured_max() -> None:
    builder = RecipeQueryBuilder()
    max_limit = builder._settings.QUERY_MAX_LIMIT  # sanity: this is our clamp ceiling

    assert builder.with_limit(0).limit() == 1
    assert builder.with_limit(-123).limit() == 1
    assert builder.with_limit(1).limit() == 1

    mid = 10 if max_limit >= 10 else max_limit
    assert builder.with_limit(mid).limit() == mid

    assert builder.with_limit(max_limit).limit() == max_limit
    assert builder.with_limit(max_limit + 1).limit() == max_limit
    assert builder.with_limit(999).limit() == max_limit


def test_build_for_mealdb_prefers_keywords_then_ingredients() -> None:
    builder = RecipeQueryBuilder()

    assert builder.build_for_mealdb() == {"s": ""}

    builder.with_ingredients(["  chicken ", "", " rice  "])
    assert builder.requested_ingredients() == ["chicken", "rice"]
    assert builder.build_for_mealdb() == {"i": "chicken,rice"}

    builder.with_keywords("  pasta  ")
    assert builder.requested_keywords() == "pasta"
    assert builder.build_for_mealdb() == {"s": "pasta"}


def test_build_for_spoonacular_includes_limit_and_ingredients() -> None:
    builder = (
        RecipeQueryBuilder().with_keywords("tacos").with_ingredients(["beef", "onion"]).with_limit(7)
    )

    params = builder.build_for_spoonacular(api_key="abc")
    assert params["apiKey"] == "abc"
    assert params["query"] == "tacos"
    assert params["includeIngredients"] == "beef,onion"
    assert params["number"] == 7
    assert params["addRecipeInformation"] == "true"
