from functools import singledispatch
from typing import NotRequired, TypedDict

from reciper.recipe import Recipe, RecipeTree


class RecipeDict(TypedDict):
    id: str
    label: str
    context: NotRequired[str]
    children: NotRequired[list["RecipeDict"]]


@singledispatch
def as_dict(recipe: Recipe | RecipeTree) -> RecipeDict:
    raise RuntimeError(f"Unsupported recipe type: {type(recipe)}")


@as_dict.register
def _(recipe: Recipe) -> RecipeDict:
    return {
        "id": "recipe",
        "label": f"[{recipe.context}]",
        "children": [
            {
                "id": "results",
                "label": "Results",
                "children": [
                    {
                        "id": f"result_{n}",
                        "label": f"{r}x {n.capitalize()}",
                    }
                    for n, r in recipe.results.items()
                ],
            },
            {
                "id": "ingredients",
                "label": "Ingredients",
                "children": [
                    {
                        "id": f"ingredient_{n}",
                        "label": f"{r}x {n.capitalize()}",
                    }
                    for n, r in recipe.ingredients.items()
                ],
            },
        ],
    }


@as_dict.register
def _(recipe: RecipeTree) -> RecipeDict:
    return _recipe_tree_as_dict(recipe, "")


def _recipe_tree_as_dict(tree: RecipeTree, id_prefix: str) -> RecipeDict:
    result: RecipeDict = {
        "id": id_prefix + tree.id,
        "label": f"{tree.rate}x {tree.item}",
    }
    if tree.context:
        result["context"] = tree.context
    if tree.ingredients:
        result["children"] = [
            _recipe_tree_as_dict(t, f"{id_prefix}_{tree.id}_") for t in tree.ingredients
        ]
    return result
