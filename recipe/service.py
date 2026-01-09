from typing import List

from .adapters import MealDBAdapter, SpoonacularAdapter
from .http_session import create_http_session
from .models import Recipe
from .query_builder import RecipeQueryBuilder
from .strategies import BestMatchStrategy, FewerMissingStrategy, RecipeStrategy

from utils.settings import Settings, get_settings


class RecipeService:
    """Coordinates API calls using the Builder and Adapters."""

    def __init__(
        self,
        spoonacular_key: str | None = None,
        settings: Settings | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._session = create_http_session(self._settings)
        self._mealdb_adapter = MealDBAdapter()
        self._spoonacular_adapter = SpoonacularAdapter()
        self._spoonacular_key = spoonacular_key or self._settings.SPOONACULAR_API_KEY
        self._strategies: List[RecipeStrategy] = [
            BestMatchStrategy(),
            FewerMissingStrategy(),
        ]
        self._default_strategy: RecipeStrategy = self._strategies[0]

    def available_strategies(self) -> List[RecipeStrategy]:
        return list(self._strategies)

    def fetch_recipes(
        self, query_builder: RecipeQueryBuilder, strategy: RecipeStrategy | None = None
    ) -> List[Recipe]:
        chosen_strategy = strategy or self._default_strategy
        recipes = self._gather_all_providers(query_builder)
        return chosen_strategy.rank(recipes, query_builder)

    def _gather_all_providers(self, query_builder: RecipeQueryBuilder) -> List[Recipe]:
        recipes: List[Recipe] = []
        recipes.extend(self._fetch_mealdb(query_builder))
        recipes.extend(self._fetch_spoonacular(query_builder))
        return recipes

    def _fetch_mealdb(self, query_builder: RecipeQueryBuilder) -> List[Recipe]:
        params = query_builder.build_for_mealdb()
        try:
            response = self._session.get(
                self._settings.MEALDB_URL,
                params=params,
                timeout=self._settings.HTTP_TIMEOUT,
            )
            response.raise_for_status()
            return self._mealdb_adapter.adapt(response.json())
        except Exception as exc:  # noqa: BLE001
            print(f"MealDB request failed: {exc}")
            return []

    def _fetch_spoonacular(self, query_builder: RecipeQueryBuilder) -> List[Recipe]:
        if not self._spoonacular_key:
            return []
        params = query_builder.build_for_spoonacular(self._spoonacular_key)
        try:
            response = self._session.get(
                self._settings.SPOONACULAR_URL,
                params=params,
                timeout=self._settings.HTTP_TIMEOUT,
            )
            response.raise_for_status()
            return self._spoonacular_adapter.adapt(response.json())
        except Exception as exc:  
            print(f"Spoonacular request failed: {exc}")
            return []
