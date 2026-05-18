import reflex as rx
from ..states import DestinationsState
from ..layouts import main_layout

@rx.page(route="/travel-log", title="Travel Log")
@main_layout
def travel_log():
    return rx.vstack(
        rx.heading("Travel Log", size="7"),
        rx.cond(
            DestinationsState.visited_items.length() == 0,
            rx.text("No visited places yet. Open a detail page and mark one as visited."),
            rx.scroll_area(
                rx.vstack(
                    rx.foreach(
                        DestinationsState.visited_items,
                        lambda item: rx.card(
                            rx.vstack(
                                rx.hstack(
                                    rx.badge(item.entity_type.title(), color_scheme="blue"),
                                    rx.text(item.name, font_weight="600"),
                                    width="100%",
                                    justify="between",
                                ),
                                rx.text(f"{item.city}, {item.country}"),
                                rx.text(f"Reviews: {item.review_count}"),
                                rx.button(
                                    "Open Details",
                                    on_click=lambda: DestinationsState.open_detail(item.id),
                                ),
                                align="start",
                                spacing="2",
                                width="100%",
                            ),
                            width="100%",
                        ),
                    ),
                    width="100%",
                    spacing="3",
                ),
                scrollbars="vertical",
                height="calc(100vh - 300px)",
            )
        ),
        width="100%",
        spacing="4",
    )