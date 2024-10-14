from dataclasses import dataclass
from typing import NotRequired, Self, TypedDict, Union

from reciper.db import RecipeStore
from reciper.recipe.recipe import Recipe

RecursiveSteps = list[Union[str, tuple[str, "RecursiveSteps"]]]


class TreeDict(TypedDict):
    id: str
    label: str
    rate: float
    context: NotRequired[str]
    children: NotRequired[list["TreeDict"]]


@dataclass
class RecipeTree:
    """
    Single recipe tree.
    Does NOT support multiple recipes for the same item.
    """

    item: str
    rate: float
    context: str
    ingredients: list[Self]

    @property
    def id(self) ->str:
        return self.item.lower().replace(" ", "-")

    def as_dict(self, id_prefix: str = "") -> TreeDict:
        result: TreeDict = {
            "id": id_prefix + self.id,
            "rate": self.rate,
            "label": self.item,
        }
        if self.context:
            result["context"] = self.context
        if self.ingredients:
            result["children"] = [i.as_dict(f"{id_prefix}_{self.id}_") for i in self.ingredients]
        return result


class RecipeRepo:
    results: dict[str, list[Recipe]]
    ingredients: dict[str, list[Recipe]]
    items: set[str]

    def __init__(self, store: RecipeStore) -> None:
        self.results = {}
        self.ingredients = {}
        self.items = set()

        for recipe in store.load_recipes():
            for name in recipe.results.keys():
                self.results.setdefault(name, []).append(recipe)
                self.items.add(name)

            for name in recipe.ingredients.keys():
                self.ingredients.setdefault(name, []).append(recipe)
                self.items.add(name)

    def recipe_tree(self, item: str, rate: float | None = None) -> RecipeTree:
        if item not in self.results:
            raise ValueError(f"{item} is not a known recipe")
        if rate is None:
            rate = self.results[item][0].results[item]
        return self._as_tree(self.results[item][0], item, rate)

    def _as_tree(self, recipe: Recipe, item: str, expected_rate: float) -> RecipeTree:
        rate_multiplier = expected_rate / recipe.results[item]
        subtrees: list[RecipeTree] = []
        for name, rate in recipe.ingredients.items():
            if sub_recipes := self.results.get(name):
                subtrees.append(self._as_tree(sub_recipes[0], name, rate * rate_multiplier))
            else:
                subtrees.append(RecipeTree(name, rate * rate_multiplier, "", []))
        return RecipeTree(item, expected_rate, recipe.context, subtrees)
