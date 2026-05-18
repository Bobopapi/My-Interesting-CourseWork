import reflex as rx
from ..states import DestinationsState
from ..layouts import main_layout

@rx.page(route="/dashboard", title="Dashboard", on_load=DestinationsState.load_dashboard_page)
@main_layout
def dashboard():
    return rx.vstack(
        rx.heading("Dashboard", size="7"),
        rx.grid(
            rx.foreach(
                DestinationsState.dashboard_stats,
                lambda stat: rx.card(
                    rx.vstack(
                        rx.text(stat["label"], size="2"),
                        rx.heading(stat["value"], size="6"),
                        spacing="1",
                    )
                ),
            ),
            columns="4",
            spacing="4",
            width="100%",
        ),
        rx.vstack(
            rx.heading("By Category", size="5"),
            rx.foreach(
                DestinationsState.dashboard_category_rows,
                lambda row: rx.hstack(
                    rx.text(row["entity_type"], width="20%"),
                    rx.text(f"Entities: {row['entity_count']}", width="25%"),
                    rx.text(f"Reviews: {row['total_reviews']}", width="25%"),
                    rx.text(f"Avg score: {row['avg_score']}", width="30%"),
                    width="100%",
                ),
            ),
            width="100%",
            spacing="2",
        ),
        rx.vstack(
            rx.heading("Monthly Review Activity", size="5"),
            rx.foreach(
                DestinationsState.dashboard_monthly_rows,
                lambda row: rx.hstack(
                    rx.text(row["month"], width="20%"),
                    rx.text(row["entity_type"], width="20%"),
                    rx.text(f"Reviews: {row['review_count']}", width="30%"),
                    rx.text(f"Avg rating: {row['avg_rating']}", width="30%"),
                    width="100%",
                ),
            ),
            width="100%",
            spacing="2",
        ),
        width="100%",
        spacing="5",
    )