from functools import cache

from reciper.db import RecipeStore


@cache
def recipe_store(domain: str) -> RecipeStore:
    result = RecipeStore(domain)
    result.load_recipes()
    return result
