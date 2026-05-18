import reflex as rx
from .styles import global_style
# Required by reflex to set pages.
from .pages import *

app = rx.App(
    theme=global_style.THEME,
    style=global_style.STYLE,
    stylesheets=global_style.STYLESHEETS)