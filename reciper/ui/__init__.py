import streamlit as st

from reciper.ui.pages import record_recipe, view_recipe, view_recipe_tree, view_recipes


@st.fragment()
def _domain_prompt() -> None:
    domain = st.text_input("Domain")
    if domain:
        st.session_state["domain"] = domain.lower()
        st.rerun()


if "domain" in st.session_state and st.session_state["domain"]:
    st.navigation([st.Page(record_recipe), st.Page(view_recipes), st.Page(view_recipe), st.Page(view_recipe_tree)]).run()
else:
    st.title("Reciper")
    _domain_prompt()
