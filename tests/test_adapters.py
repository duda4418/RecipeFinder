from recipe.adapters import MealDBAdapter, SpoonacularAdapter


def test_mealdb_adapter_builds_measure_and_ingredient_lines() -> None:
    data = {
        "meals": [
            {
                "strMeal": "Test Meal",
                "strMealThumb": "https://example/img.jpg",
                "strInstructions": "Cook it.",
                "strIngredient1": "Chicken",
                "strMeasure1": "1 lb",
                "strIngredient2": " Rice ",
                "strMeasure2": " 2 cups ",
                "strIngredient3": "",
                "strMeasure3": "",
            }
        ]
    }

    recipes = MealDBAdapter().adapt(data)
    assert len(recipes) == 1

    recipe = recipes[0]
    assert recipe.title == "Test Meal"
    assert recipe.source == "MealDB"
    assert recipe.instructions == "Cook it."
    assert recipe.image_url == "https://example/img.jpg"
    assert recipe.ingredients == ["1 lb Chicken", "2 cups Rice"]


def test_spoonacular_adapter_strips_html_and_decodes_entities() -> None:
    data = {
        "results": [
            {
                "title": "Spicy Tacos",
                "image": "https://example/taco.jpg",
                "summary": "<b>Spicy</b> &amp; tasty<br/>Done.",
                "extendedIngredients": [
                    {"original": "2 tortillas"},
                    {"name": "beef"},
                    {"name": ""},
                ],
            }
        ]
    }

    recipes = SpoonacularAdapter().adapt(data)
    assert len(recipes) == 1

    recipe = recipes[0]
    assert recipe.title == "Spicy Tacos"
    assert recipe.source == "Spoonacular"
    assert recipe.image_url == "https://example/taco.jpg"
    assert recipe.ingredients == ["2 tortillas", "beef"]
    assert recipe.instructions == "Spicy & tastyDone."
