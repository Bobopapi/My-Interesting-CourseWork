import reflex as rx

from ..layouts import main_layout
from ..states import DestinationsState


@rx.page(route="/details/[item_id]", title="Details", on_load=DestinationsState.load_detail_page)
@main_layout
def details():
    return rx.vstack(
        rx.cond(
            DestinationsState.selected_item == None,
            rx.text("Place not found."),
            _details_content(),
        ),
        width="100%",
    )


def _details_content():
    return rx.vstack(
        rx.heading(DestinationsState.selected_item.name, size="7"),
        rx.hstack(
            rx.badge(DestinationsState.selected_item.entity_type.title(), color_scheme="green"),
            rx.badge(
                "Visited",
                color_scheme="blue",
                display=rx.cond(DestinationsState.selected_item.visited, "inline-flex", "none"),
            ),
            spacing="2",
        ),
        rx.text(f"{DestinationsState.selected_item.city}, {DestinationsState.selected_item.country}"),
        rx.text(f"Reviews: {DestinationsState.selected_item.review_count}"),
        rx.text(f"Source: {DestinationsState.selected_item.source_url}"),
        rx.hstack(
            rx.button(
                rx.cond(DestinationsState.selected_item.liked, "Unlike", "Like"),
                on_click=DestinationsState.toggle_selected_like,
                color_scheme="red",
                variant=rx.cond(DestinationsState.selected_item.liked, "solid", "outline"),
            ),
            rx.button(
                rx.cond(DestinationsState.selected_item.visited, "Unvisit", "Visited"),
                on_click=DestinationsState.toggle_selected_visited,
                color_scheme="blue",
                variant=rx.cond(DestinationsState.selected_item.visited, "solid", "outline"),
            ),
            rx.button("Back", on_click=lambda: rx.redirect("/"), variant="soft"),
            spacing="3",
        ),
        rx.divider(),
        rx.vstack(
            rx.heading("Review Wordcloud", size="5"),
            rx.cond(
                DestinationsState.detail_wordcloud.length() == 0,
                rx.text("No keyword data available for this place yet."),
                rx.box(
                    rx.flex(
                        rx.foreach(
                            DestinationsState.detail_wordcloud,
                            lambda word: rx.text(
                                word["keyword"],
                                font_size=word["font_size"],
                                font_weight=word["font_weight"],
                                color=word["color"],
                                opacity=word["opacity"],
                                display="inline-block",
                                margin="0.25rem 0.4rem",
                                line_height="1.05",
                                _hover={"opacity": "1", "text_decoration": "underline"},
                            ),
                        ),
                        wrap="wrap",
                        justify="center",
                        align="center",
                        width="100%",
                    ),
                    border="1px solid #d6dce2",
                    border_radius="12px",
                    background="linear-gradient(135deg, #f8fafc 0%, #eef4f8 100%)",
                    min_height="260px",
                    width="100%",
                    padding="0.75rem",
                ),
            ),
            width="100%",
            spacing="3",
        ),
        align="start",
        spacing="4",
        width="100%",
    )
