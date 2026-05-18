import reflex as rx
from .locale_dialog import locale_dialog
from ..styles.vars import color_vars, font_vars
from ..styles import sidebar_style, flex_style
from ..states import LocaleDialogState

def sidebar() -> rx.Component:
    return rx.vstack(
        rx.vstack(
            rx.vstack(
                _locale(),
                **(sidebar_style.SIDEBAR_GROUP | flex_style.FLEX_GAP_2)
            ),
            _nav(),
            **(sidebar_style.SIDEBAR_GROUP | flex_style.FLEX_GAP_3)
        ),
        **sidebar_style.SIDEBAR,
    )

def _locale() -> rx.Component:
    region = LocaleDialogState.get_selected_region
    currency = LocaleDialogState.get_selected_currency

    return locale_dialog(
        rx.button(
            rx.hstack(
                rx.text(rx.cond(region == None, "JP", region.name)),
                rx.text(rx.cond(currency == None, "USD($)", currency.description)),
            ),
            **sidebar_style.SIDEBAR_LOCALE,
        )
    )

def _nav() -> rx.Component:
    return rx.vstack(
        _nav_link("Destinations", "map-pin", "/"),
        _nav_link("Travel Log", "notebook-pen", "/travel-log"),
        _nav_link("Dashboard", "chart-bar-big", "/dashboard"),
        **sidebar_style.SIDEBAR_GROUP_STRETCH,
    )

def _nav_link(label: str, icon: str, href: str) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.icon(icon),
            rx.text(label),
        ),
        href=href,
        **sidebar_style.SIDEBAR_LINK,
    )
