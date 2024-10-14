from typing import Annotated, Protocol

from pydantic import (
    AfterValidator,
    BaseModel,
    PositiveFloat,
    StringConstraints,
)


def _validate_item_dict(value: dict[str, PositiveFloat]) -> dict[str, PositiveFloat]:
    result = {n.lower().strip(): r for n, r in value.items()}
    for name in result.keys():
        if not name:
            raise ValueError("missing name")
    return result


class _SupportsLen(Protocol):
    def __len__(self) -> int: ...


def _at_least_one[T: _SupportsLen](value: T) -> T:
    if len(value) < 1:
        raise ValueError("Must be at least one")
    return value


class Recipe(BaseModel):
    context: Annotated[str, StringConstraints(strip_whitespace=True, to_lower=True)] = ""
    results: Annotated[
        dict[str, PositiveFloat], AfterValidator(_at_least_one), AfterValidator(_validate_item_dict)
    ]
    ingredients: Annotated[dict[str, PositiveFloat], AfterValidator(_validate_item_dict)]
    """The production requirement"""

    def __str__(self) -> str:
        ingredients = " + ".join(f"{c}x {n}" for n, c in self.ingredients.items())
        results = " + ".join(f"{c}x {n}" for n, c in self.results.items())

        return f"{self.context or ''}: {ingredients} = {results}"
