from functools import cache
import os
from typing import Iterable
from pydantic import TypeAdapter

from reciper.recipe import Recipe

_list_adapter = TypeAdapter(list[Recipe])


class RecipeStore:
    domain: str
    _recipes: list[Recipe] = []
    _known_items: set[str] = set()
    _known_contexts: set[str] = set()

    def __init__(self, domain: str) -> None:
        self.domain = domain

    @property
    def _filename(self) -> str:
        return f".recipes/{self.domain}.json"

    @property
    def known_items(self) -> list[str]:
        return list(self._known_items)

    @property
    def known_contexts(self) -> list[str]:
        return list(self._known_contexts)

    def _load_known(self) -> None:
        for recipe in self._recipes:
            self._known_items.update(recipe.results.keys(), recipe.ingredients.keys())
            self._known_contexts.add(recipe.context)

    def load_recipes(self) -> list[Recipe]:
        if self._recipes:
            return self._recipes

        try:
            with open(self._filename, "rb") as f:
                json_data = f.read()
            self._recipes = _list_adapter.validate_json(json_data)
            self._load_known()
            return self._recipes
        except FileNotFoundError:
            return []

    def dump_recipes(self, recipes: Iterable[Recipe]) -> None:
        self._recipes = list(recipes)
        json_data = _list_adapter.dump_json(self._recipes)
        with open(self._filename, "wb") as f:
            f.write(json_data)

    def add_recipe(self, recipe: Recipe) -> None:
        recipes = self.load_recipes()
        recipes.append(recipe)
        self._known_items.update(recipe.results.keys(), recipe.ingredients.keys())

        json_data = _list_adapter.dump_json(recipes)
        with open(self._filename, "wb") as f:
            f.write(json_data)


@cache
def known_domains() -> set[str]:
    result: set[str] = set()
    for dir_ in os.listdir(".recipes"):
        name, ext = os.path.splitext(dir_)
        if ext.lower() == ".json":
            result.add(name)
    return result
