# RecipeFinder

Desktop (Tkinter) app that searches for recipes from multiple providers and shows results in a simple UI.

Providers supported:
- TheMealDB (no API key required)
- Spoonacular (requires an API key; if missing, Spoonacular calls are skipped)

## How to run the project

### 1) Create & activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

```powershell
pip install -r requirements.txt
```

### 3) Configure environment variables (optional but recommended)

Create a `.env` file in the project root (there is already an example in this repo). Supported variables:

```env
# Optional: if empty, Spoonacular is disabled
SPOONACULAR_API_KEY=your_key_here

MEALDB_URL=https://www.themealdb.com/api/json/v1/1/search.php
SPOONACULAR_URL=https://api.spoonacular.com/recipes/complexSearch

HTTP_TIMEOUT=10
HTTP_MAX_RETRIES=3
HTTP_BACKOFF=0.5
```

Notes:
- If `SPOONACULAR_API_KEY` is not set, the app still works using TheMealDB.
- Images in the UI require `pillow` (already listed in `requirements.txt`).

### 4) Start the app

```powershell
python main.py
```

## Design patterns used

This project intentionally uses a few patterns that fit naturally with “multiple providers + a single UI”.

### 1) Strategy Pattern

**Where:** `recipe/strategies.py`

**What it does here:** Encapsulates different ways to rank/sort recipes after they are fetched.

**Role in the app:**
- The UI lets the user choose a ranking method.
- `RecipeService.fetch_recipes(...)` accepts a `RecipeStrategy` and uses it to rank results.

**Examples in code:**
- `BestMatchStrategy` (prioritizes ingredient + keyword hits)
- `FewerMissingStrategy` (prioritizes fewer missing ingredients)

Why it fits: ranking logic changes often and is easy to swap without changing the fetching code or UI.

### 2) Adapter Pattern

**Where:** `recipe/adapters.py`

**What it does here:** Converts provider-specific JSON payloads into a single internal model: `Recipe`.

**Role in the app:**
- Each API returns a different response shape.
- Adapters normalize both MealDB and Spoonacular output into `recipe/models.py: Recipe`.

**Examples in code:**
- `MealDBAdapter.adapt(...)`
- `SpoonacularAdapter.adapt(...)`

Why it fits: the UI and ranking strategies operate on a consistent `Recipe` object and never need to know provider field names.

### 3) Builder Pattern

**Where:** `recipe/query_builder.py`

**What it does here:** Builds provider-specific query parameter dictionaries from a single user intent (keywords, ingredients, limit).

**Role in the app:**
- The UI constructs a `RecipeQueryBuilder` and sets keywords/ingredients/limit.
- The service uses the builder to generate request parameters for each provider:
	- `build_for_mealdb()`
	- `build_for_spoonacular(api_key)`

Why it fits: request construction is a “many small options” problem; a builder keeps it readable and prevents parameter logic from leaking into UI/service code.

### 4) Factory (Factory Function) for HTTP sessions

**Where:** `recipe/http_session.py`

**What it does here:** Centralizes creation of a configured `requests.Session` with retry/backoff behavior.

**Role in the app:**
- `create_http_session(settings)` returns a ready-to-use session.
- Both the service and UI use sessions configured the same way.

Why it fits: avoids duplicating retry/backoff setup and makes HTTP behavior consistent.

### 5) Singleton-like Settings access

**Where:** `utils/settings.py`

**What it does here:** Ensures the app uses one shared settings object (cached via `@lru_cache(maxsize=1)`).

**Role in the app:**
- `get_settings()` returns the same `Settings` instance across the app.
- Settings are environment-backed (Pydantic Settings + `.env`).

Why it fits: config should be consistent across UI/service and shouldn’t be re-parsed repeatedly.

## Where each pattern fits (text diagram)

```
UI (ui/app.py)
	| creates
	v
RecipeQueryBuilder (Builder)
	| passed into
	v
RecipeService (coordinates workflow)
	| uses                | uses
	v                     v
Adapters (Adapter)    Strategy (Strategy)
	| normalize JSON       | ranks unified Recipe list
	v                     v
Recipe model (recipe/models.py)

Also used across layers:
	- create_http_session(...) (Factory function)
	- get_settings() (Singleton-like cached Settings)
```

## Running tests (optional)

If/when you add tests:

```powershell
pytest
```
