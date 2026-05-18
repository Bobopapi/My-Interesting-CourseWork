import reflex as rx
from ..states import LocaleDialogState
from ..styles import (locale_style, flex_style)
from ..models import (LocaleGroup, LocaleItem)

def locale_dialog(trigger: rx.Component) -> rx.Component:
    region_trigger, region_content = _build_tab(
        LocaleDialogState.region_group,
        LocaleDialogState.region_items,
        LocaleDialogState.set_region_item,
    )
    currency_trigger, currency_content = _build_tab(
        LocaleDialogState.currency_group,
        LocaleDialogState.currency_items,
        LocaleDialogState.set_currency_item,
    )

    return rx.dialog.root(
        rx.dialog.trigger(trigger),
        rx.dialog.content(
            rx.tabs.root(
                rx.tabs.list(
                    region_trigger,
                    currency_trigger,
                ),
                region_content,
                currency_content,
                default_value = LocaleDialogState.tab_default_value,
            ),
            **locale_style.LOCALE_DIALOG,
        ),
    )

def _build_tab(group: LocaleGroup, items: list[LocaleItem], setter_method) -> tuple[rx.Component, rx.Component]:
    trigger = _build_tab_trigger(group)
    content = _build_tab_content(group, items, setter_method)

    return trigger, content

def _build_tab_trigger(group: LocaleGroup) -> rx.Component:
    return rx.tabs.trigger(
        group.tab_name,
        value = group.tab_value
    )

def _build_tab_content(group: LocaleGroup, items: list[LocaleItem], setter_method) -> rx.Component:
    return rx.tabs.content(
        rx.dialog.title(
            group.content_title, 
            **locale_style.LOCALE_CONTENT_TITLE,
        ),
        rx.scroll_area(
            rx.grid(
                rx.foreach(
                    items,
                    lambda item: _build_grid_item(item, setter_method)
                ),
                **locale_style.LOCALE_GRID,
            ),
            **locale_style.LOCALE_GRID_SCROLL,
        ),
        value = group.tab_value,
    )

def _build_grid_item(item: LocaleItem, setter_method) -> rx.Component:
    return rx.dialog.close(
        rx.button(
            rx.vstack(
                rx.text(item.name),
                rx.text(item.description),
                **flex_style.FLEX_GAP_0,
            ),
            on_click=setter_method(item),
            **locale_style.LOCALE_BUTTON,
        )
    )