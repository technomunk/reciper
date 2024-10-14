from nicegui import ui as gui
from nicegui.elements.column import Column


def frame(domain: str) -> Column:
    """Reusable page theming"""

    with gui.left_drawer(bordered=True):
        gui.label(domain.capitalize())
        gui.link("🛠 Record recipe", f"/{domain}/record-recipe")
        gui.link("🔍 View recipe", f"/{domain}/view-recipe")
        gui.link("✅ Check recipe", f"/{domain}/check-recipe")

    return center()


def center() -> Column:
    return gui.column().classes("place-self-center min-w-80")
