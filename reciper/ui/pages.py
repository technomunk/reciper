from typing import Any, Iterable

from nicegui import APIRouter
from nicegui import ui as gui
from nicegui.elements.tree import Tree as GUITree
from nicegui.events import ValueChangeEventArguments

from reciper.db import known_domains
from reciper.recipe import Recipe, RecipeRepo
from reciper.ui.elements import RecipeForm, confirm_save_dialog, recipe_view
from reciper.ui.resources import recipe_store
from reciper.ui.theme import center, frame

router = APIRouter()


@router.page("/")
def pick_domain() -> None:
    domains = known_domains()

    def on_change(event: ValueChangeEventArguments) -> None:
        if not event.value:
            return
        domain: str = event.value.lower()
        domains.add(domain)
        gui.navigate.to(f"/{domain}/record-recipe")

    with center():
        gui.select(list(domains), label="Domain", on_change=on_change)


@router.page("/{domain}/record-recipe")
def record_recipe(domain: str) -> None:
    gui.page_title(f"Record {domain} recipe")

    def on_submit(recipe: Recipe) -> None:
        confirm_save_dialog(recipe, lambda: recipe_store(domain).add_recipe(recipe))

    with frame(domain).classes("w-1/2"):
        RecipeForm(on_submit).classes("w-full")


@router.page("/{domain}/view-recipe")
def view_recipe(domain: str) -> None:
    gui.page_title(f"View {domain} recipe")
    _recipe_view(domain, False)


# def view_recipes() -> None:
#     st.title(f"{st.session_state['domain']} recipes")
#     repo = recipe_store(st.session_state["domain"])
#     recipes = _order_recipes_by_context_and_result(repo.load_recipes())
#     st.json(recipes, expanded=3)


# def view_recipe_tree() -> None:
#     repo = RecipeRepo(recipe_store(st.session_state["domain"]))
#     item = st.selectbox("item", repo.results.keys(), index=None)
#     if item:
#         st.json([t.to_dict() for t in repo.ingredient_tree(item)])


# def view_totals_for_recipe() -> None:
#     repo = RecipeRepo(recipe_store(st.session_state["domain"]))
#     left, right = st.columns(2)
#     with left:
#         count = st.number_input("Rate", min_value=0.0, value=1.0)
#     with right:
#         item = st.selectbox("Item", repo.results.keys(), index=None)

#     if item:
#         st.json([t.totals(count) for t in repo.ingredient_tree(item)])


@router.page("/{domain}/check-recipe")
def recipe_step_by_step(domain: str) -> None:
    gui.page_title(f"Check {domain} recipe")
    _recipe_view(domain, True)


# def _order_recipes_by_context_and_result(
#     recipes: Iterable[Recipe],
# ) -> dict[str, dict[str, list[dict[str, Any]]]]:
#     result: dict[str, dict[str, list[dict[str, Any]]]] = {}
#     for r in recipes:
#         repr_ = r.model_dump(exclude={"context"})
#         for n in r.results.keys():
#             result.setdefault(r.context, {}).setdefault(n, []).append(repr_)
#     return result


# def _present_steps(steps: RecursiveSteps) -> None:
#     st.markdown()


def _recipe_view(domain: str, tick: bool) -> None:
    repo = RecipeRepo(recipe_store(domain))

    tree: GUITree | None = None
    frame_ = frame(domain)

    def select_item(event: ValueChangeEventArguments) -> None:
        nonlocal tree
        if tree is not None:
            tree.clear()
            tree = None

        if not event.value:
            return

        recipe = repo.recipe_tree(event.value)
        with frame_:
            recipe_view(recipe, show_ticks=tick).expand()

    with frame_:
        gui.select(list(repo.results.keys()), label="Item", on_change=select_item).classes("w-full")
