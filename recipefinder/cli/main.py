import argparse
import os

from dotenv import load_dotenv

from ..domain.query_builder import RecipeQueryBuilder
from ..domain.facade import RecipeAppFacade
from ..domain.strategies import STRATEGIES
from ..providers.mealdb import MealDbAdapter
from ..providers.spoonacular import SpoonacularAdapter
from ..providers.combined import CombinedProvider
from ..providers.cached import CachedProvider


load_dotenv()


def build_provider() -> CachedProvider:
    spoon_key = os.getenv("SPOONACULAR_API_KEY")

    providers = [MealDbAdapter()]

    if spoon_key:
        providers.append(SpoonacularAdapter(spoon_key))

    base_provider = CombinedProvider(providers)
    return CachedProvider(base_provider, ttl_seconds=600)


def main() -> None:
    p = argparse.ArgumentParser(prog="recipe-cli")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search")
    s.add_argument("--have", default="")
    s.add_argument("--exclude", default="")
    s.add_argument("--keyword", default="")
    s.add_argument("--strategy", default="fewest_missing", choices=STRATEGIES.keys())
    s.add_argument("--top", type=int, default=5)

    d = sub.add_parser("details")
    d.add_argument("--id", required=True)

    args = p.parse_args()

    provider = build_provider()
    app = RecipeAppFacade(provider)

    app.bus.subscribe(lambda e, pl: print(f"[EVENT] {e}: {pl}"))

    if args.cmd == "search":
        qb = RecipeQueryBuilder().have(args.have).exclude(args.exclude)
        if args.keyword:
            qb.keyword(args.keyword)

        query = qb.build()
        strategy = STRATEGIES[args.strategy]
        results = app.search(query, strategy, top_n=args.top)

        if not results:
            print("No recipes found.")
            return

        for r in results:
            print(f"- {r.title} (id={r.id}, source={r.source})")

    elif args.cmd == "details":
        det = app.details(args.id)
        print(det.title)
        print(f"Source: {det.source}")
        print("\nIngredients:")
        for i in det.ingredients:
            print(f"  - {i}")
        print("\nInstructions:")
        print(det.instructions)

