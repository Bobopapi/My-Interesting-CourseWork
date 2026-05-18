import reflex as rx
from typing import Callable
from functools import wraps
from ..states import LocaleDialogState
from ..components import sidebar
from ..styles.vars import (size_vars, color_vars)

def main_layout(page: Callable[[], rx.Component]) -> Callable[[], rx.Component]:
    @wraps(page)
    def layout() -> rx.Component:
        return rx.hstack(
            sidebar(),
            rx.container(
                rx.hstack(
                    rx.image(
                        src="/logo.png",
                        height="7rem",
                        width="auto",
                        margin_bottom="4rem",
                    ),
                    width="100%",
                    padding_x="1rem",
                    justify="center",
                ),
                page(),
                padding=f"{size_vars.SPACING_5} {size_vars.SPACING_4}",
                on_mount=LocaleDialogState.load_locales
            ),
            background_color=color_vars.BACKGROUND_COLOR,
            width="100%",
            height="100vh",
        )
    
    return layout