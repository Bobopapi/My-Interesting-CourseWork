from .vars import (font_vars, color_vars, size_vars)

BUTTON = {
    "margin": "3px", # Fix out of alignment buttons.
    "variant": "ghost",
    "font_family": font_vars.FONT_FAMILY,
    "font_size": "1.2rem",
    "border_radius": size_vars.CORNER_RADIUS_3,
    "padding": f"{size_vars.SPACING_2} {size_vars.SPACING_3}",
    "text_decoration": "none",
    "background_color": color_vars.PRIMARY_COLOR,
    "color": color_vars.ON_PRIMARY_COLOR,

    "_hover": {
        "background_color": color_vars.PRIMARY_COLOR_HOVER,
    }
}

BUTTON_SECONDARY = {
    **BUTTON,
    "background_color": color_vars.ON_PRIMARY_COLOR,
    "color": color_vars.PRIMARY_COLOR,

    "_hover": {
        "background_color": color_vars.ON_PRIMARY_COLOR_HOVER,
    },
}

BUTTON_CLEAR = {
    **BUTTON,
    "border": size_vars.BORDER_2,
    "background_color": "transparent",
    "color": "#000000",

    "_hover": {
        "background_color": color_vars.ON_PRIMARY_COLOR,
    },
}

BUTTON_CLEAR_SELECTED = {
    **BUTTON,
    "border": size_vars.BORDER_2,
    "background_color": color_vars.PRIMARY_COLOR,
    "color": color_vars.ON_PRIMARY_COLOR,
}

BUTTON_SMALL = {
    **BUTTON,
    "padding": size_vars.SPACING_1,
}