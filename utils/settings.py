from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
		"""Strongly typed environment-backed settings for the Recipe Finder app.

		Values are read from environment variables and (by default) from a local
		`.env` file in the project root.

		Optional:
			- SPOONACULAR_API_KEY (if empty, Spoonacular calls are skipped)

		URLs / behavior:
			- MEALDB_URL
			- SPOONACULAR_URL
			- HTTP_TIMEOUT
			- HTTP_MAX_RETRIES
			- HTTP_BACKOFF
			- APP_ENV
		"""

		model_config = SettingsConfigDict(
				env_file=".env",
				env_file_encoding="utf-8",
				extra="ignore",
		)

		SPOONACULAR_API_KEY: str = ""

		# Safe defaults; override via .env as needed.
		MEALDB_URL: str = ""
		SPOONACULAR_URL: str = ""
		HTTP_TIMEOUT: float = Field(default=10.0, gt=0)

		# Retries apply only to safe/idempotent requests (GET).
		HTTP_MAX_RETRIES: int = Field(default=5, ge=0, le=10)
		HTTP_BACKOFF: float = Field(default=0.5, ge=0)

		APP_ENV: str = "local"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

