import flet as ft
from dataclasses import dataclass, field
from typing import Callable, cast

import logging


@dataclass
class AuthenticationStatus(ft.Observable):
    is_authenticated: bool = False
    user: str | None = None

    def initiate_login_flow(self):
        # other login stuff goes here
        self.user = "Someone"
        self.is_authenticated = True
        logging.info("Login successful")

    def initiate_logout_flow(self):
        # other login stuff goes here
        self.user = None
        self.is_authenticated = False
        logging.info("Logout successful")


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
