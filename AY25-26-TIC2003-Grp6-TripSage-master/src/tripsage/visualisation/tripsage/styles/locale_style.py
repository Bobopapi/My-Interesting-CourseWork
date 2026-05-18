from ..styles import (heading_style, grid_style, button_style)
from .vars import (font_vars, color_vars, size_vars)

LOCALE_DIALOG = {
    "background_color": color_vars.BACKGROUND_COLOR,
    "border": size_vars.BORDER_2,
    "padding": size_vars.SPACING_2,
    "width": "75vw",
    "max_width": "75vw",
    "height": "75vh",
}

LOCALE_CONTENT_TITLE = {
    **heading_style.HEADING_3,
    "margin": {size_vars.SPACING_3},
}

LOCALE_GRID = {
    **grid_style.GRID_5COL,
    "height": "100%",
}

LOCALE_GRID_SCROLL = {
    "flex_grow": "1",
    "height": "100%",
}

LOCALE_BUTTON = {
    **button_style.BUTTON,
    "font_size": font_vars.FONT_SIZE,
    "background_color": color_vars.BACKGROUND_COLOR,
    "color": "#000000",
    "padding": f"{size_vars.SPACING_2} {size_vars.SPACING_4}",

    "_hover": {
        "background_color": color_vars.BACKGROUND_COLOR_HOVER,
        "border": size_vars.BORDER_1,
    }
}