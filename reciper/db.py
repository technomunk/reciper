from collections import deque
from itertools import chain
from typing import Iterable, Self, TypedDict

from pydantic import TypeAdapter

from reciper.recipe import Recipe

_list_adapter = TypeAdapter(list[Recipe])


class RecipeStore:
    domain: str
    _recipes: list[Recipe] = []

    def __init__(self, domain: str) -> None:
        self.domain = domain

    @property
    def _filename(self) -> str:
        return f".recipes/{self.domain}.json"

    def load_recipes(self) -> list[Recipe]:
        if self._recipes:
            return self._recipes

        try:
            with open(self._filename, "rb") as f:
                json_data = f.read()
            self._recipes = _list_adapter.validate_json(json_data)
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

        json_data = _list_adapter.dump_json(recipes)
        with open(self._filename, "wb") as f:
            f.write(json_data)
