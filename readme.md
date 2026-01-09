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

QUERY_DEFAULT_LIMIT=10
QUERY_MAX_LIMIT=25
```

Notes:
- If `SPOONACULAR_API_KEY` is not set, the app still works using TheMealDB.
- Images in the UI require `pillow` (already listed in `requirements.txt`).
- `RecipeQueryBuilder.with_limit(n)` always clamps the value to `1..QUERY_MAX_LIMIT`.

### 4) Start the app

```powershell
python main.py
```

## Design patterns used

This project intentionally uses a few patterns that fit naturally with “multiple providers + a single UI”.

### 1) Builder Pattern

**Where:** `recipe/query_builder.py`

**What it does here:** Builds provider-specific query parameter dictionaries from a single user intent (keywords, ingredients, limit).

**Role in the app:**
- The UI constructs a `RecipeQueryBuilder` and sets keywords/ingredients/limit.
- The service uses the builder to generate request parameters for each provider:
	- `build_for_mealdb()`
	- `build_for_spoonacular(api_key)`

Why it fits: request construction is a “many small options” problem; a builder keeps it readable and prevents parameter logic from leaking into UI/service code.

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

### 3) Strategy Pattern

**Where:** `recipe/strategies.py`

**What it does here:** Encapsulates different ways to rank/sort recipes after they are fetched.

**Role in the app:**
- The UI lets the user choose a ranking method.
- `RecipeService.fetch_recipes(...)` accepts a `RecipeStrategy` and uses it to rank results.

**Examples in code:**
- `BestMatchStrategy` (prioritizes ingredient + keyword hits)
- `FewerMissingStrategy` (prioritizes fewer missing ingredients)

Why it fits: ranking logic changes often and is easy to swap without changing the fetching code or UI.

## Where each pattern fits

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
```

## Running tests

```powershell
python -m pytest 
```
