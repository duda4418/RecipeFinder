from __future__ import annotations

import logging
import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List

from dotenv import load_dotenv

from ..domain.query_builder import RecipeQueryBuilder
from ..domain.facade import RecipeAppFacade
from ..domain.strategies import STRATEGIES
from ..providers.mealdb import MealDbAdapter
from ..providers.spoonacular import SpoonacularAdapter
from ..providers.combined import CombinedProvider
from ..providers.cached import CachedProvider
from ..domain.models import RecipeSummary


def build_provider() -> CachedProvider:
    load_dotenv()
    spoon_key = os.getenv("SPOONACULAR_API_KEY")

    providers = [MealDbAdapter()]
    if spoon_key:
        providers.append(SpoonacularAdapter(spoon_key))

    base_provider = CombinedProvider(providers)
    return CachedProvider(base_provider, ttl_seconds=600)


class RecipeTkApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Recipe Finder")
        self.geometry("900x600")
        self.app = RecipeAppFacade(build_provider())
        self.results: List[RecipeSummary] = []
        self._build_ui()
        logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
        self.app.bus.subscribe(self._on_event)

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=10)
        container.pack(fill=tk.BOTH, expand=True)

        form = ttk.Frame(container)
        form.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(form, text="Have (csv)").grid(row=0, column=0, sticky=tk.W)
        self.have_var = tk.StringVar(value="")
        ttk.Entry(form, textvariable=self.have_var, width=40).grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(form, text="Exclude (csv)").grid(row=0, column=2, sticky=tk.W)
        self.exclude_var = tk.StringVar(value="")
        ttk.Entry(form, textvariable=self.exclude_var, width=30).grid(row=0, column=3, sticky=tk.W, padx=5)

        ttk.Label(form, text="Keyword").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.keyword_var = tk.StringVar(value="")
        ttk.Entry(form, textvariable=self.keyword_var, width=40).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(form, text="Strategy").grid(row=1, column=2, sticky=tk.W, pady=5)
        self.strategy_var = tk.StringVar(value=list(STRATEGIES.keys())[0])
        ttk.Combobox(form, textvariable=self.strategy_var, values=list(STRATEGIES.keys()), state="readonly", width=27).grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)

        ttk.Label(form, text="Top N").grid(row=0, column=4, sticky=tk.W)
        self.top_var = tk.IntVar(value=5)
        ttk.Spinbox(form, from_=1, to=50, textvariable=self.top_var, width=5).grid(row=0, column=5, sticky=tk.W, padx=5)

        ttk.Button(form, text="Search", command=self.on_search).grid(row=1, column=4, columnspan=2, sticky=tk.EW, padx=5)

        # Results list
        list_frame = ttk.Frame(container)
        list_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(list_frame, text="Results").pack(anchor=tk.W)
        self.listbox = tk.Listbox(list_frame, height=12)
        self.listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        btns = ttk.Frame(list_frame)
        btns.pack(fill=tk.X)
        ttk.Button(btns, text="View Details", command=self.on_details).pack(side=tk.LEFT)

        # Details panel
        detail_frame = ttk.Frame(container)
        detail_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(detail_frame, text="Details").pack(anchor=tk.W)
        self.details_text = tk.Text(detail_frame, height=12, wrap=tk.WORD)
        self.details_text.configure(state=tk.DISABLED)
        self.details_text.pack(fill=tk.BOTH, expand=True)

    def on_search(self) -> None:
        try:
            qb = RecipeQueryBuilder().have(self.have_var.get()).exclude(self.exclude_var.get())
            if self.keyword_var.get().strip():
                qb.keyword(self.keyword_var.get())
            query = qb.build()
            strategy = STRATEGIES[self.strategy_var.get()]
            results = self.app.search(query, strategy, top_n=self.top_var.get())
        except Exception as exc:  # pragma: no cover - GUI error path
            messagebox.showerror("Error", str(exc))
            return

        self.results = results
        self.listbox.delete(0, tk.END)
        for r in results:
            self.listbox.insert(tk.END, f"{r.title} (source={r.source}, id={r.id})")

        self._set_details("Select a recipe and click 'View Details'.")

    def on_details(self) -> None:
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Select a recipe first.")
            return
        idx = selection[0]
        recipe = self.results[idx]
        try:
            details = self.app.details(recipe.id)
        except Exception as exc:  # pragma: no cover - GUI error path
            messagebox.showerror("Error", str(exc))
            return

        ingredients = "\n".join(f"- {i}" for i in details.ingredients)
        text = (
            f"Title: {details.title}\n"
            f"Source: {details.source}\n"
            f"ID: {details.id}\n\n"
            f"Ingredients:\n{ingredients}\n\n"
            f"Instructions:\n{details.instructions}"
        )
        self._set_details(text)

    def _set_details(self, text: str) -> None:
        self.details_text.configure(state=tk.NORMAL)
        self.details_text.delete("1.0", tk.END)
        self.details_text.insert(tk.END, text)
        self.details_text.configure(state=tk.DISABLED)

    def _on_event(self, event: str, payload: dict) -> None:
        # Logs emitted events to console for debugging/telemetry without touching UI
        logging.info("%s: %s", event, payload)


def run() -> None:
    app = RecipeTkApp()
    app.mainloop()


if __name__ == "__main__":
    run()
