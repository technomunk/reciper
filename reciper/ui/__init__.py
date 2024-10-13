import streamlit as st

from reciper.ui.pages import (
    recipe_step_by_step,
    record_recipe,
    view_recipe,
    view_recipe_tree,
    view_recipes,
    view_totals_for_recipe,
)


@st.fragment()
def _domain_prompt() -> None:
    domain = st.text_input("Domain")
    if domain:
        st.session_state["domain"] = domain.lower()
        st.rerun()


if "domain" in st.session_state and st.session_state["domain"]:
    st.navigation(
        [
            st.Page(record_recipe),
            st.Page(view_recipes),
            st.Page(view_recipe),
            st.Page(view_recipe_tree),
            st.Page(view_totals_for_recipe),
            st.Page(recipe_step_by_step)
        ]
    ).run()
else:
    st.title("Reciper")
    _domain_prompt()
