from typing import Generator
import click
from reciper.recipe.recipe import Recipe


class RecipePrompt[T: Recipe]:
    recipe_cls: type[T]

    def __init__(self, recipe_cls: type[T] = Recipe) -> None:
        self.recipe_cls = recipe_cls

    def prompt(self) -> Generator[T, None, None]:
        context: str | None = click.prompt("Context", type=str, default="") or None
        yield from self._prompt(context)

    def _prompt(self, context: str | None) -> Generator[T, None, None]:
        while True:
            result, rate = _prompt_for_item("Result")
            ingredients = _prompt_for_ingredients()
            recipe = self.recipe_cls(ingredients, result, rate, context)
            click.echo(recipe)
            yield recipe

            if not click.confirm("Another recipe?", default=True):
                break


def _prompt_for_item(prompt: str) -> tuple[str, float]:
    return click.prompt(prompt, value_proc=_parse_item)


def _parse_item(s: str) -> tuple[str, float]:
    if not s.find(" "):
        return s, 1
    count, rest = s.split(" ", maxsplit=1)
    try:
        return rest, float(count)
    except ValueError:
        return s, 1


def _prompt_for_ingredients() -> dict[str, float]:
    return click.prompt("Ingredients", value_proc=_parse_ingredients)


def _parse_ingredients(s: str) -> dict[str, float]:
    return dict(_parse_item(x.strip()) for x in s.split(","))
