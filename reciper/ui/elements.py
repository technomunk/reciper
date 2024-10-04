import streamlit as st
import pydantic

from reciper.recipe import Recipe
from reciper.ui.resources import recipe_store


def recipe_form() -> Recipe | None:
    with st.form("recipe", enter_to_submit=False):
        context = st.text_input("Context", autocomplete=f"{st.session_state['domain']}-context")
        results = _item_input("result")
        ingredients = _item_input("ingredient")

        recipe = None
        try:
            recipe = Recipe(results=results, ingredients=ingredients, context=context)
        except (pydantic.ValidationError, TypeError):
            pass

        if st.form_submit_button(type="primary"):
            return recipe


@st.dialog("Save recipe?")
def recipe_save_prompt(recipe: Recipe) -> None:
    st.json(recipe)
    left, right = st.columns(2)
    with left:
        if st.button("Cancel"):
            st.rerun()

    with right:
        if st.button("Save", type="primary"):
            recipe_store(st.session_state["domain"]).add_recipe(recipe)
            st.rerun()


@st.fragment()
def _item_input(category: str) -> dict[str, float]:
    if f"{category}_count" not in st.session_state:
        st.session_state[f"{category}_count"] = 1
    count: int = st.session_state[f"{category}_count"]

    st.text(category.capitalize() + "s")

    ingredients: dict[str, float] = {}
    for i in range(count):
        left, right = st.columns(2)
        with left:
            rate = st.number_input("Rate", min_value=0.0, value=1.0, key=f"{category}_rate_{i}")
        with right:
            name = st.text_input("Name", key=f"{category}_name_{i}")

        if name:
            ingredients[name] = rate

    left, right = st.columns(2)
    with left:
        if st.form_submit_button(f"1 less {category}"):
            st.session_state[f"{category}_count"] = max(1, count - 1)
            st.rerun(scope="fragment")

    with right:
        if st.form_submit_button(f"1 more {category}"):
            st.session_state[f"{category}_count"] = count + 1
            st.rerun(scope="fragment")

    return ingredients
