from __future__ import annotations

from typing import Dict, Any, Optional
import time

from ..domain.models import RecipeQuery, RecipeSummary, RecipeDetails
from .base import RecipeProvider


class CachedProvider:
    def __init__(self, inner: RecipeProvider, ttl_seconds: int = 600) -> None:
        self.inner = inner
        self.ttl = ttl_seconds
        self._cache: Dict[str, tuple[float, Any]] = {}

    def _get_cached(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if not entry:
            return None
        ts, val = entry
        if time.time() - ts > self.ttl:
            self._cache.pop(key, None)
            return None
        return val

    def search(self, query: RecipeQuery) -> List[RecipeSummary]:
        key = f"search:{query}"
        hit = self._get_cached(key)
        if hit is not None:
            return hit
        val = self.inner.search(query)
        self._cache[key] = (time.time(), val)
        return val

    def details(self, recipe_id: str) -> RecipeDetails:
        key = f"details:{recipe_id}"
        hit = self._get_cached(key)
        if hit is not None:
            return hit
        val = self.inner.details(recipe_id)
        self._cache[key] = (time.time(), val)
        return val

