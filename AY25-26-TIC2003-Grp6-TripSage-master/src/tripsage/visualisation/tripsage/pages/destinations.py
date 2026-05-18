import reflex as rx

from ..models import DestinationItem
from ..states import DestinationsState
from ..styles import flex_style, button_style, grid_style
from ..styles.vars import font_vars, size_vars, color_vars
from ..layouts import main_layout

@rx.page(route="/", title="Destinations", on_load=DestinationsState.load_page)
@main_layout
def destinations():
    return rx.vstack(
        rx.vstack(
            _search_bar(),
            _sort_bar(),
            spacing="3"
        ),
        rx.vstack(
            _category_bar(),
            _destination_grid(),
            spacing="3",
        ),
        spacing="7",
    )

def _search_bar():
    return rx.form(
        rx.hstack(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "Country",
                        font_size=font_vars.FONT_SIZE_SMALL,
                    ),
                    rx.input(
                        rx.input.slot(
                            rx.icon("globe"),
                            slide="left",
                        ),
                        placeholder="Japan",
                        name="country",
                        type="text",
                    ),
                    **flex_style.FLEX_GAP_0
                ),
                rx.vstack(
                    rx.text(
                        "City",
                        font_size=font_vars.FONT_SIZE_SMALL,
                    ),
                    rx.input(
                        rx.input.slot(
                            rx.icon("building-2"),
                            slide="left",
                        ),
                        name="city",
                        type="text",
                    ),
                    **flex_style.FLEX_GAP_0
                ),
            ),
            rx.button(
                "Search",
                type="submit",
                **(
                    button_style.BUTTON | 
                    {"border_radius": size_vars.CORNER_RADIUS_5} |
                    {"font_size": font_vars.FONT_SIZE_SMALL}
                ),
            ),
            spacing="4",
            align="end"
        ),
        on_submit=DestinationsState.submit_search
    )

def _sort_bar():
    return rx.hstack(
        _sort_button("Highlights", "Highlight of our most popular pieces.", "highlights"),
        _sort_button("Trending Now", "Events currently driving high engagement.", "trending"),
        **flex_style.FLEX_ROW_STRETCH,
    )

def _category_bar():
    return rx.hstack(
        _category_button("All", "all"),
        _category_button("Attractions", "attractions"),
        _category_button("Food", "food"),
        _category_button("Liked", "liked"),
        **flex_style.FLEX_ROW,
    )

def _destination_grid():
    return rx.scroll_area(
        rx.grid(
            rx.foreach(
                DestinationsState.display_item,
                _destination_item,
            ),
            **grid_style.GRID,
        ),
        scrollbars="vertical",
        height="calc(100vh - 500px)",
    )

def _destination_item(item: DestinationItem):
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.badge(item.entity_type.title(), color_scheme="green"),
                    rx.text(item.name, font_weight="600"),
                    spacing="2",
                ),
                rx.icon(
                    "heart",
                    color=rx.cond(item.liked, "red", "gray"),
                    size=20,
                    on_click=lambda: DestinationsState.toggle_like(item.id),
                ),
                justify="between",
                width="100%",
            ),
            rx.vstack(
                rx.text(
                    f"{item.city}, {item.country}",
                    font_size=font_vars.FONT_SIZE_SMALL,
                ),
                rx.text(
                    f"Reviews: {item.review_count}",
                    font_size=font_vars.FONT_SIZE_SMALL,
                ),
                rx.text(
                    f"Highlights: {item.highlights_rating:.2f} | Trending: {item.trending_rating:.2f}",
                    font_size=font_vars.FONT_SIZE_SMALL,
                    color=color_vars.PRIMARY_COLOR,
                ),
                rx.hstack(
                    rx.button(
                        "View Details",
                        on_click=lambda: DestinationsState.open_detail(item.id),
                        **(button_style.BUTTON_SECONDARY | {"font_size": font_vars.FONT_SIZE_SMALL}),
                    ),
                    rx.badge(
                        "Visited",
                        color_scheme="blue",
                        variant="solid",
                        display=rx.cond(item.visited, "inline-flex", "none"),
                    ),
                    width="100%",
                    justify="between",
                ),
                spacing="1",
            ),
            width="100%",
            height="100%",
        ),
        width="100%",
        height="100%",
    )

def _category_button(label: str, category: str):
    return rx.cond(
        DestinationsState.selected_category == category,
        rx.button(
            label,
            on_click=lambda: DestinationsState.change_category(category),
            **(button_style.BUTTON_CLEAR_SELECTED | {"font_size": font_vars.FONT_SIZE_SMALL}),
        ),
        rx.button(
            label,
            on_click=lambda: DestinationsState.change_category(category),
            **(button_style.BUTTON_CLEAR | {"font_size": font_vars.FONT_SIZE_SMALL}),
        ),
    )

def _sort_button(title: str, subtitle: str, sort_key: str):
    return rx.cond(
        DestinationsState.sort_by == sort_key,
        rx.button(
            rx.vstack(
                rx.text(
                    title,
                    font_size=font_vars.FONT_SIZE,
                ),
                rx.text(
                    subtitle,
                    font_size=font_vars.FONT_SIZE_SMALL,
                ),
                **flex_style.FLEX_GAP_0
            ),
            on_click=lambda: DestinationsState.change_sort_by(sort_key),
            **button_style.BUTTON_CLEAR_SELECTED
        ),
        rx.button(
            rx.vstack(
                rx.text(
                    title,
                    font_size=font_vars.FONT_SIZE,
                ),
                rx.text(
                    subtitle,
                    font_size=font_vars.FONT_SIZE_SMALL,
                ),
                **flex_style.FLEX_GAP_0
            ),
            on_click=lambda: DestinationsState.change_sort_by(sort_key),
            **button_style.BUTTON_CLEAR
        ),
    )