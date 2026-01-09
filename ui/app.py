import io
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, List, Optional

from recipefinder.models import Recipe
from recipefinder.query_builder import RecipeQueryBuilder
from recipefinder.http_session import create_http_session
from recipefinder.service import RecipeService
from utils.settings import get_settings

try:
    from PIL import Image, ImageTk  # type: ignore

    PIL_AVAILABLE = True
except ImportError:
    Image = None  # type: ignore
    ImageTk = None  # type: ignore
    PIL_AVAILABLE = False


class RecipeApp(tk.Tk):
    """Simple ttk UI that consumes the recipefinder service."""

    def __init__(self, service: RecipeService) -> None:
        super().__init__()
        self.title("Recipe Finder")
        self.geometry("720x600")
        self._service = service
        self._settings = get_settings()
        self._session = create_http_session(self._settings)
        self._strategies = {strategy.name: strategy for strategy in service.available_strategies()}
        self._recipes: List[Recipe] = []
        self._image_photo: Optional[Any] = None
        self._build_ui()

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=12)
        root.pack(fill=tk.BOTH, expand=True)

        search_frame = ttk.Frame(root)
        search_frame.pack(fill=tk.X, pady=(0, 4))

        ttk.Label(search_frame, text="Keywords:").pack(side=tk.LEFT)
        self.keywords_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.keywords_var, width=30).pack(
            side=tk.LEFT, padx=(6, 12)
        )

        ttk.Label(search_frame, text="Ingredients (comma):").pack(side=tk.LEFT)
        self.ingredients_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.ingredients_var, width=25).pack(
            side=tk.LEFT, padx=(6, 12)
        )

        ttk.Button(search_frame, text="Search", command=self._on_search).pack(side=tk.LEFT)

        options_frame = ttk.Frame(root)
        options_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(options_frame, text="Max results:").pack(side=tk.LEFT)
        self.limit_var = tk.StringVar(value=str(self._settings.QUERY_DEFAULT_LIMIT))
        ttk.Spinbox(
            options_frame,
            from_=1,
            to=self._settings.QUERY_MAX_LIMIT,
            textvariable=self.limit_var,
            width=4,
            wrap=True,
        ).pack(side=tk.LEFT, padx=(6, 12))

        ttk.Label(options_frame, text="Provider strategy:").pack(side=tk.LEFT)
        self.strategy_var = tk.StringVar(value=next(iter(self._strategies)))
        ttk.Combobox(
            options_frame,
            textvariable=self.strategy_var,
            values=list(self._strategies.keys()),
            width=20,
            state="readonly",
        ).pack(side=tk.LEFT, padx=(6, 12))

        self.status_var = tk.StringVar(value="Idle")
        ttk.Label(root, textvariable=self.status_var).pack(anchor=tk.W)

        columns = ("title", "source")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", height=12)
        self.tree.heading("title", text="Title")
        self.tree.heading("source", text="Source")
        self.tree.column("title", width=420)
        self.tree.column("source", width=120)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=(8, 8))
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        detail_frame = ttk.Frame(root)
        detail_frame.pack(fill=tk.BOTH, expand=False)

        self.image_label = ttk.Label(detail_frame, text="No image", anchor=tk.CENTER)
        self.image_label.pack(side=tk.LEFT, padx=(0, 12))

        self.details = tk.Text(detail_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.details.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _on_search(self) -> None:
        builder = RecipeQueryBuilder()
        builder.with_keywords(self.keywords_var.get())
        ingredients = [item.strip() for item in self.ingredients_var.get().split(",")]
        builder.with_ingredients(ingredients)
        try:
            builder.with_limit(int(self.limit_var.get()))
        except ValueError:
            builder.with_limit(self._settings.QUERY_DEFAULT_LIMIT)

        self.status_var.set("Searching...")
        self.tree.delete(*self.tree.get_children())
        self._recipes = []

        thread = threading.Thread(target=self._run_search, args=(builder,), daemon=True)
        thread.start()

    def _run_search(self, builder: RecipeQueryBuilder) -> None:
        try:
            strategy = self._strategies.get(self.strategy_var.get())
            recipes = self._service.fetch_recipes(builder, strategy)
            self.after(0, self._update_results, recipes)
        except Exception as exc:  # noqa: BLE001
            self.after(0, messagebox.showerror, "Error", str(exc))

    def _update_results(self, recipes: List[Recipe]) -> None:
        self._recipes = recipes
        for idx, recipe in enumerate(recipes):
            self.tree.insert("", tk.END, iid=str(idx), values=(recipe.title, recipe.source))
        self.status_var.set(f"Found {len(recipes)} recipes")
        if recipes:
            self.tree.selection_set("0")

    def _on_select(self, event: tk.Event) -> None:  
        selection = self.tree.selection()
        if not selection:
            return
        idx = int(selection[0])
        recipe = self._recipes[idx]
        self.details.configure(state=tk.NORMAL)
        self.details.delete("1.0", tk.END)
        self.details.insert(
            tk.END,
            f"Title: {recipe.title}\nSource: {recipe.source}\n\nIngredients:\n- "
            + "\n- ".join(recipe.ingredients)
            + "\n\nInstructions:\n"
            + (recipe.instructions or "No instructions available."),
        )
        self.details.configure(state=tk.DISABLED)

        # Load image asynchronously to keep UI responsive
        threading.Thread(target=self._load_image, args=(recipe.image_url,), daemon=True).start()

    def _load_image(self, url: Optional[str]) -> None:
        if not PIL_AVAILABLE:
            self.after(0, self._set_image, None, "Install pillow for images")
            return
        if not url:
            self.after(0, self._set_image, None, "No image")
            return
        try:
            resp = self._session.get(url, timeout=self._settings.HTTP_TIMEOUT)
            resp.raise_for_status()
            img = Image.open(io.BytesIO(resp.content))
            img.thumbnail((240, 240))
            photo = ImageTk.PhotoImage(img)
            self.after(0, self._set_image, photo, "")
        except Exception as exc:  # noqa: BLE001
            self.after(0, self._set_image, None, "Image load failed")

    def _set_image(self, photo: Optional[Any], fallback_text: str) -> None:
        self._image_photo = photo
        if photo:
            self.image_label.configure(image=photo, text="")
        else:
            self.image_label.configure(image="", text=fallback_text)
