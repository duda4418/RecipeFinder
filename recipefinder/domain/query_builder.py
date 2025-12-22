from __future__ import annotations

from typing import List, Optional

from .models import RecipeQuery


class RecipeQueryBuilder:
    def __init__(self) -> None:
        self._have: List[str] = []
        self._exclude: List[str] = []
        self._keyword: Optional[str] = None

    def have(self, ingredients_csv: str) -> "RecipeQueryBuilder":
        self._have = [x.strip().lower() for x in ingredients_csv.split(",") if x.strip()]
        return self

    def exclude(self, ingredients_csv: str) -> "RecipeQueryBuilder":
        self._exclude = [x.strip().lower() for x in ingredients_csv.split(",") if x.strip()]
        return self

    def keyword(self, kw: str) -> "RecipeQueryBuilder":
        self._keyword = kw.strip() or None
        return self

    def build(self) -> RecipeQuery:
        if not self._have and not self._keyword:
            raise ValueError("Provide at least --have or --keyword")
        return RecipeQuery(have=self._have, exclude=self._exclude, keyword=self._keyword)

