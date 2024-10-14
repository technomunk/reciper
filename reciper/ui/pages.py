from typing import Any, Iterable

from nicegui import APIRouter
from nicegui import ui as gui
from nicegui.elements.tree import Tree as GUITree
from nicegui.events import ValueChangeEventArguments

from reciper.recipe import RecipeRepo

# from reciper.ui.elements import recipe_form, recipe_save_prompt
from reciper.ui.resources import recipe_store

router = APIRouter()

# @gui.page("{domain}/record-recipe")
# def record_recipe(domain: str) -> None:
#     gui.label(f"Create {domain} recipe")
#     if recipe := recipe_form():
#         recipe_save_prompt(recipe)


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
    column = gui.column().classes("place-self-center min-w-80")

    def select_item(event: ValueChangeEventArguments) -> None:
        nonlocal tree
        if tree is not None:
            tree.delete()
            tree = None

        if not event.value:
            return

        with column:
            tree = gui.tree([repo.recipe_tree(event.value).as_dict()], tick_strategy="leaf" if tick else None)
        tree.add_slot(
            "default-header",
            '<span :props="props">{{props.node.rate}}x {{props.node.label}}</span>',
        )

    with column:
        gui.select(list(repo.results.keys()), label="Item", on_change=select_item)
