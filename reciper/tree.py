from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Generator, Self, cast

from reciper.db import RecipeStore
from reciper.recipe import Recipe


@dataclass
class _ItemSubTree:
    rate: float
    context: str
    ingredients: dict[str, list["_ItemSubTree"] | float]

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"rate": self.rate}
        if self.context:
            result["context"] = self.context
        if self.ingredients:
            result["ingredients"] = self._ingr_to_dict(self.ingredients)
        return result

    def with_rate(self, rate: float) -> Self:
        return self._with_rate_ratio(rate / self.rate)

    def gather_totals(self, result: defaultdict[str, float], multiplier: float) -> None:
        for name, subtree in self.ingredients.items():
            if isinstance(subtree, list):
                for st in subtree:
                    st.gather_totals(result, multiplier)
            else:
                result[name] += subtree * multiplier

    def gather_steps(self, name: str, result: list[tuple[str, float]], multiplier: float) -> None:
        for name, subtree in self.ingredients.items():
            if isinstance(subtree, list):
                for st in subtree:
                    st.gather_steps(name, result, multiplier)
            else:
                result.append((name, self.rate * multiplier))

    def _with_rate_ratio(self, ratio: float) -> Self:
        return type(self)(
            self.rate * ratio,
            self.context,
            {
                n: [ii._with_rate_ratio(ratio) for ii in i] if isinstance(i, list) else ratio * i
                for n, i in self.ingredients.items()
            },
        )

    @classmethod
    def _ingr_to_dict(cls, ingrs: dict[str, list["_ItemSubTree"] | float]) -> dict[str, Any]:
        return {
            n: (
                (t[0].to_dict() if len(t) == 1 else [st.to_dict() for st in t])
                if isinstance(t, list)
                else t
            )
            for n, t in ingrs.items()
        }


@dataclass
class ItemTree(_ItemSubTree):
    item: str

    def to_dict(self) -> dict[str, Any]:
        result = {"item": self.item}
        result.update(super().to_dict())
        return result

    def totals(self, required_rate: float) -> defaultdict[str, float]:
        multiplier = required_rate / self.rate
        result: defaultdict[str, float] = defaultdict(float)
        self.gather_totals(result, multiplier)
        return result

    def as_steps(self, required_rate: float) -> list[tuple[str, float]]:
        result: list[tuple[str, float]] = []
        multiplier = required_rate / self.rate
        self.gather_steps(self.item, result, multiplier)
        return result


class RecipeRepo:
    results: dict[str, list[Recipe]]
    ingredients: dict[str, list[Recipe]]
    items: set[str]

    _subtrees: dict[str, list[_ItemSubTree]] = {}
    _seen_ingredients: set[str] = set()

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

    def ingredient_tree(self, item: str) -> Generator[ItemTree, None, None]:
        for recipe in self.results.get(item, []):
            ingredients = {
                in_: self._get_subtrees(in_, ir) or ir for in_, ir in recipe.ingredients.items()
            }
            yield ItemTree(recipe.results[item], recipe.context, ingredients, item)

    def _get_subtrees(self, item: str, expected_rate: float) -> list[_ItemSubTree]:
        if subtrees := self._subtrees_with_rate(item, expected_rate):
            return subtrees

        subtrees = cast(list[_ItemSubTree], [])
        for recipe in self.results.get(item, []):
            rate_ratio = expected_rate / recipe.results[item]
            ingredients: dict[str, list[_ItemSubTree] | float] = {}
            for in_, ir in recipe.ingredients.items():
                if in_ in self._seen_ingredients:
                    ingredients[in_] = (
                        self._subtrees_with_rate(in_, ir * rate_ratio) or ir * rate_ratio
                    )
                else:
                    self._seen_ingredients.add(in_)
                    ingredients[in_] = self._get_subtrees(in_, rate_ratio * ir) or ir * rate_ratio
            subtrees.append(_ItemSubTree(expected_rate, recipe.context, ingredients))

        self._subtrees[item] = subtrees
        return subtrees

    def _subtrees_with_rate(self, item: str, rate: float) -> list[_ItemSubTree] | None:
        if subtrees := self._subtrees.get(item):
            return [st.with_rate(rate) for st in subtrees]
        return None
