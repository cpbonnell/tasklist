import flet as ft
from dataclasses import dataclass, field
from typing import Callable, cast


@ft.component
def PreLoginView(initiate_login_flow: Callable[..., None] | None = None):

    return ft.View(
        controls=[
            ft.Column(
                controls=[
                    ft.Text("Please log in to see the app."),
                    ft.Button("Log in", on_click=initiate_login_flow),
                ]
            )
        ]
    )
