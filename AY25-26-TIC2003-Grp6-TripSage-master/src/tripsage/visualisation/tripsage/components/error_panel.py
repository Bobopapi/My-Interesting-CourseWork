import reflex as rx

def error_panel(errors: list[str]) -> rx.Component:
    return rx.cond(
        errors.length() > 0,
        rx.hstack(
            rx.icon("triangle-alert", color="#db3232"),
            rx.cond(
                errors.length() > 1,
                _multiple_error(errors),
                _single_error(errors[0]),
            ),
            padding="1.2rem",
            border="2px solid #db3232",
            color="#000000",
            background_color="#fde8e8",
            width="100%",
            border_radius="8px",
        ),
        rx.fragment(),
    )

def _single_error(error: str) -> rx.Component:
    return rx.text(error, font_weight="medium")

def _multiple_error(errors: list[str]) -> rx.Component:
    return rx.vstack(
        rx.text("Please fix the following errors:", font_weight="bold"),
        rx.list.unordered(
            rx.foreach(
                errors,
                lambda error: rx.list.item(error)
            ),
        ),
        align_items="start",
        spacing="1",
    )