from recipe.env_loader import load_dotenv_if_present
from recipe.service import RecipeService
from ui.app import RecipeApp


def main() -> None:
    load_dotenv_if_present()
    service = RecipeService()
    app = RecipeApp(service)
    app.mainloop()


if __name__ == "__main__":
    main()
