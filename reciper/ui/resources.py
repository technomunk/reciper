import streamlit as st

from reciper.db import RecipeStore


@st.cache_resource
def recipe_store(domain: str) -> RecipeStore:
    return RecipeStore(domain)
