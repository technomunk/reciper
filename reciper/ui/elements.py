from functools import partial
from typing import Callable, Literal, TypedDict

import pydantic
from nicegui import ui as gui

from reciper.recipe import Recipe, RecipeTree
from reciper.ui.glue import as_dict


class _RecipeFormInputs(TypedDict):
    context: gui.input
    results: list[tuple[gui.number, gui.input]]
    ingredients: list[tuple[gui.number, gui.input]]


class RecipeForm(gui.card):
    _form: _RecipeFormInputs
    on_submit: Callable[[Recipe], None]

    def __init__(self, on_submit: Callable[[Recipe], None]) -> None:
        super().__init__()
        self.on_submit = on_submit
        with self:
            section_label("Record new recipe")

            self._form = {
                "context": gui.input("Context").classes("w-full"),
                "results": [],
                "ingredients": [],
            }

            with gui.column().classes("w-full") as self._results:
                section_label("Results")
                with gui.row().classes("w-full place-content-between"):
                    rate = positive_number("Rate")
                    item = item_title("Item")
                    self._form["results"].append((rate, item))

                with gui.row().classes("w-full place-content-around"):
                    gui.button(
                        "-1", on_click=partial(self._remove_row, "results"), color="negative"
                    )
                    gui.button("+1", on_click=partial(self._add_row, "results"), color="positive")

            gui.separator()

            with gui.column().classes("w-full") as self._ingredients:
                section_label("Ingredients")
                with gui.row().classes("w-full place-content-between"):
                    rate = positive_number("Rate")
                    item = item_title("Item")
                    self._form["ingredients"].append((rate, item))

                with gui.row().classes("w-full place-content-around"):
                    gui.button(
                        "-1", on_click=partial(self._remove_row, "ingredients"), color="negative"
                    )
                    gui.button(
                        "+1", on_click=partial(self._add_row, "ingredients"), color="positive"
                    )

            gui.separator()

            gui.button("Save", on_click=self._try_submit, color="positive").classes(
                "place-self-center"
            )

    def _try_submit(self) -> None:
        results = _gather_dict(self._form["results"])
        ingredients = _gather_dict(self._form["ingredients"])
        try:
            recipe = Recipe(
                context=self._form["context"].value or "",
                results=results,
                ingredients=ingredients,
            )
            self.on_submit(recipe)
        except pydantic.ValidationError as err:
            gui.notify(str(err), type="negative", position="top", multi_line=True)
            # TODO: forward errors to relevant element

    def _remove_row(self, section: Literal["results", "ingredients"]) -> None:
        if not self._form[section]:
            return

        next(self._form[section][-1][0].ancestors()).clear()
        self._form[section].pop()

    def _add_row(self, section: Literal["results", "ingredients"]) -> None:
        with gui.row().classes("w-full place-content-between") as row:
            rate = positive_number("Rate")
            item = item_title("Item")
            self._form[section].append((rate, item))
        if section == "results":
            row.move(self._results, len(self._form[section]))
        else:
            row.move(self._ingredients, len(self._form[section]))


def recipe_view(recipe: Recipe | RecipeTree, *, show_ticks: bool = False) -> gui.tree:
    result = gui.tree([as_dict(recipe)], tick_strategy="leaf" if show_ticks else None)
    return result


def confirm_save_dialog(recipe: Recipe, on_confirm: Callable[[], None]) -> gui.dialog:
    with gui.dialog(value=True) as result:
        def _on_confirm_click() -> None:
            on_confirm()
            _close_and_clear(result)

        with gui.card():
            recipe_view(recipe).expand()

            with gui.row().classes("w-full place-content-between"):
                gui.button("Cancel", on_click=lambda: _close_and_clear(result), color="negative")
                gui.button("Confirm", on_click=_on_confirm_click, color="positive")

    return result


def label(text: str, classes: str = "text-lg") -> gui.label:
    return gui.label(text).classes(classes)


def section_label(text: str, classes: str = "text-bold place-self-center") -> gui.label:
    return label(text).classes(classes)


def positive_number(label: str) -> gui.number:
    return gui.number(label, value=1.0, min=0.0).classes("w-auto")


def item_title(label: str) -> gui.input:
    return gui.input(label).props("clearable").classes("w-auto")


def _gather_dict(inputs: list[tuple[gui.number, gui.input]]) -> dict[str, float]:
    result: dict[str, float] = {}
    for rate, item in inputs:
        if item.value and float(rate.value) > 0:
            result[item.value] = float(rate.value)
    return result


def _close_and_clear(dialog: gui.dialog) -> None:
    dialog.close()
    dialog.clear()
