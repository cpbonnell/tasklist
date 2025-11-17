from typing import Coroutine

import flet as ft


@ft.component
def PreLoginView(initiate_login_flow: Coroutine | None = None):

    return ft.View(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            ft.Column(
                controls=[
                    ft.Text("Please log in to see the app."),
                    ft.Button("Log in", on_click=initiate_login_flow),
                ]
            )
        ],
    )
