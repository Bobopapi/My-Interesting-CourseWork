import reflex as rx
from .vars import font_vars

STYLE = {
    "font_family": font_vars.FONT_FAMILY,
    "font_size": font_vars.FONT_SIZE,
}

STYLESHEETS = [
    "https://fonts.googleapis.com/css2?family=Lexend+Deca:wght@100..900&family=Lexend:wght@100..900&display=swap"
]

THEME = rx.theme(
    appearance="light"
)