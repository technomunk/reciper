from functools import cache

from reciper.db import RecipeStore


@cache
def recipe_store(domain: str) -> RecipeStore:
    return RecipeStore(domain)
