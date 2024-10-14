from nicegui import app
from nicegui import ui as gui

from reciper.ui.pages import router


app.include_router(router)

gui.run(title="Recipe engine", dark=None)
