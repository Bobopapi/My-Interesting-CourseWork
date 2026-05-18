from .vars import (font_vars, color_vars, size_vars)
from . import (flex_style, button_style)

SIDEBAR = {
    **flex_style.FLEX_COLUMN_CENTER_BETWEEN,
    "background_color": color_vars.PRIMARY_COLOR,
    "height": size_vars.VIEWPORT_HEIGHT,
    "min-width": "180px",
    "padding": f"{size_vars.SPACING_5} {size_vars.SPACING_2}",
}

SIDEBAR_LOCALE = {
    **button_style.BUTTON_SECONDARY,
    "font_size": font_vars.FONT_SIZE_SMALL,
}

SIDEBAR_GROUP = {
    **flex_style.FLEX_COLUMN_CENTER,
    **flex_style.FLEX_GAP_2,
}

SIDEBAR_GROUP_STRETCH = {
    **flex_style.FLEX_COLUMN_STRETCH,
    **flex_style.FLEX_GAP_2,
}

SIDEBAR_LINK = {
    "border_radius": size_vars.CORNER_RADIUS_3,
    "padding": size_vars.SPACING_2,
    "text_decoration": "none",
    "color": color_vars.ON_PRIMARY_COLOR,

    "_hover": {
        "background_color": color_vars.ON_PRIMARY_COLOR,
        "color": color_vars.PRIMARY_COLOR,
    },
}