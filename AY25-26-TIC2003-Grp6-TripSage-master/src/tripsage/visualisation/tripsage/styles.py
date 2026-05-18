"""Shared styles and colors for TripSage Reflex app."""

# Color palette matching the React app
SAGE = "#90BEAB"
SAGE_LIGHT = "#C5DDD3"
SAGE_DARK = "#4B9E7B"
WARM_BG = "#EDE4D9"
WARM_CARD = "#F0EDE8"
GREEN_CARD = "#E8F0EC"
WHITE = "#FFFFFF"
FOREGROUND = "#1F2937"
MUTED = "#6B7280"

# Font families
FONT_DISPLAY = "'Inter', sans-serif"
FONT_BODY = "'Source Sans 3', sans-serif"

# Common style dicts
sidebar_style = {
    "width": "240px",
    "min_height": "100vh",
    "background": SAGE_LIGHT,
    "padding": "24px",
    "display": "flex",
    "flex_direction": "column",
}

card_style = {
    "background": GREEN_CARD,
    "border_radius": "16px",
    "padding": "20px",
}

page_style = {
    "flex": "1",
    "padding": "24px",
    "background": WARM_BG,
    "min_height": "100vh",
    "overflow_y": "auto",
}

pill_active = {
    "background": SAGE,
    "color": FOREGROUND,
    "padding": "8px 20px",
    "border_radius": "9999px",
    "font_size": "14px",
    "font_weight": "500",
    "cursor": "pointer",
    "border": "none",
}

pill_inactive = {
    "background": GREEN_CARD,
    "color": MUTED,
    "padding": "8px 20px",
    "border_radius": "9999px",
    "font_size": "14px",
    "font_weight": "500",
    "cursor": "pointer",
    "border": "none",
    "_hover": {"background": "#D5E0DA"},
}

input_style = {
    "background": WHITE,
    "border": "none",
    "border_radius": "8px",
    "padding": "10px 16px",
    "font_size": "14px",
    "outline": "none",
    "width": "100%",
}

btn_primary = {
    "background": SAGE,
    "color": FOREGROUND,
    "padding": "10px 24px",
    "border_radius": "8px",
    "font_size": "14px",
    "font_weight": "500",
    "cursor": "pointer",
    "border": "none",
    "_hover": {"opacity": "0.9"},
}
