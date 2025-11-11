import flet as ft
from dataclasses import dataclass, field
from typing import Callable, cast
from tasklist.configuration import Configuration
from flet.auth.providers import Auth0OAuthProvider

import logging


@dataclass
class AuthenticationStatus(ft.Observable):
    provider: Auth0OAuthProvider | None = None
    is_authenticated: bool = False

    # ========================================
    # These methods initiate auth workflows
    def initiate_login_flow(self):
        logging.info("Initiating login flow with Auth0")
        ft.context.page.login(self.provider)

    def initiate_logout_flow(self):
        # other login stuff goes here
        logging.info("Initiating logout flow with Auth0")
        raise NotImplementedError("Logout is not implemented")

    # ========================================
    # These methods are called in response to events in the auth workflow
    def on_login_succeeded(self, e: ft.Event):
        logging.info("Login succeeded")
        self.is_authenticated = True

    def on_login_failed(self, e: ft.Event):
        logging.info("Login failed")
        pass

    def on_login(self, e: ft.Event):
        if e.error:
            self.on_login_failed(e)
        else:
            self.on_login_succeeded(e)

    def on_logout(self, e: ft.Event):
        logging.info("Logout successful")
        self.is_authenticated = False


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
