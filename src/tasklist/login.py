import os

import flet as ft
from dataclasses import dataclass, field
from typing import Callable, cast, Coroutine
from tasklist.configuration import Configuration
from flet.auth.providers import Auth0OAuthProvider
from flet.security import encrypt, decrypt
from flet.controls.control_event import Event, EventControlType
from tasklist.configuration import Configuration

import logging


@dataclass
class AuthenticationStatus(ft.Observable):
    config: Configuration
    provider: Auth0OAuthProvider | None = None
    is_authenticated: bool = False
    AUTH_TOKEN_KEY = "app.auth_token"

    # ========================================
    # These methods initiate auth workflows
    async def initiate_login_flow(self, e: Event[EventControlType]):
        logging.info(f"Initiating login flow with Auth0, event {e}")
        page = ft.context.page

        saved_token = None
        ejt = await page.shared_preferences.get(self.AUTH_TOKEN_KEY)
        if ejt:
            logging.info(f"Using stored auth token: {ejt}")
            saved_token = decrypt(ejt, self.config.app_secret_key)

        if e is not None or saved_token is not None:
            await page.login(self.provider, saved_token=saved_token)

    async def initiate_logout_flow(self):
        # other login stuff goes here
        logging.info("Initiating logout flow with Auth0")
        page = ft.context.page
        await page.shared_preferences.remove(self.AUTH_TOKEN_KEY)
        page.logout()

    # ========================================
    # These methods are called in response to events in the auth workflow
    async def on_login_succeeded(self, e: ft.LoginEvent):
        logging.info("Login succeeded")
        page = ft.context.page

        # save token in a client storage
        jt = page.auth.token.to_json()
        ejt = encrypt(jt, self.config.app_secret_key)
        logging.info(f"Storing auth token: {ejt}")
        await page.shared_preferences.set(self.AUTH_TOKEN_KEY, ejt)
        self.is_authenticated = True

    async def on_login_failed(self, e: ft.LoginEvent):
        logging.info("Login failed")

    async def on_login(self, e: ft.LoginEvent):
        if e.error:
            await self.on_login_failed(e)
        else:
            await self.on_login_succeeded(e)

    def on_logout(self, e):
        logging.info("Logout successful")
        self.is_authenticated = False


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
