from typing import Any, Iterable
import streamlit as st

from reciper.recipe import Recipe
from reciper.tree import RecipeRepo
from reciper.ui.elements import recipe_form, recipe_save_prompt
from reciper.ui.resources import recipe_store


def record_recipe() -> None:
    st.title(f"Create {st.session_state['domain']} recipe")
    if recipe := recipe_form():
        recipe_save_prompt(recipe)


def view_recipe() -> None:
    repo = RecipeRepo(recipe_store(st.session_state["domain"]))
    item = st.selectbox("item", repo.results.keys(), index=None)
    if item:
        st.json([r.model_dump() for r in repo.results[item]])


def view_recipes() -> None:
    st.title(f"{st.session_state['domain']} recipes")
    repo = recipe_store(st.session_state["domain"])
    recipes = _order_recipes_by_context_and_result(repo.load_recipes())
    st.json(recipes, expanded=3)


def view_recipe_tree() -> None:
    repo = RecipeRepo(recipe_store(st.session_state["domain"]))
    item = st.selectbox("item", repo.results.keys(), index=None)
    if item:
        st.json([t.to_dict() for t in repo.ingredient_tree(item)])
        # st.json([asdict(t) for t in repo.ingredient_tree(item)])


def _order_recipes_by_context_and_result(
    recipes: Iterable[Recipe],
) -> dict[str, dict[str, list[dict[str, Any]]]]:
    result: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for r in recipes:
        repr_ = r.model_dump(exclude={"context"})
        for n in r.results.keys():
            result.setdefault(r.context, {}).setdefault(n, []).append(repr_)
    return result
