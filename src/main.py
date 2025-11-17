import warnings
from typing import Callable, Union

import logging
import warnings
from typing import Callable, Union

import flet as ft
from flet.auth.authorization_service import AuthorizationService
from flet.auth.providers import Auth0OAuthProvider
from flet.security import decrypt, encrypt

from tasklist.components import TodoAppView
from tasklist.configuration import Configuration
from tasklist.login import PreLoginView

# ignore *all* DeprecationWarnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

logging.basicConfig(level=logging.INFO)

CONFIG = Configuration()


@ft.component
def LandingView(auth_status: AuthManager):

    logging.info(
        f"Rendering EnsureLoggedInView -- Auth status is '{auth_status.is_authenticated}'"
    )

    if not auth_status.is_authenticated:
        logging.info(f"Rendering EnsureLoggedInView -- returning PreLoginView")
        return PreLoginView(initiate_login_flow=auth_status.initiate_login_flow)
    else:
        logging.info(f"Rendering EnsureLoggedInView -- returning TodoAppView")
        return TodoAppView(initiate_logout_flow=auth_status.initiate_logout_flow)


class AuthManager:
    """
    A class for managing the state needed by the auth flow callbacks.
    """

    def __init__(
        self,
        page: ft.Page,
        config: Configuration,
        provider: Auth0OAuthProvider,
        default_view: Callable[
            ..., Union[list[ft.View], ft.View, list[ft.Control], ft.Control]
        ],
    ):
        self.page = page
        self.config = config
        self.provider = provider
        self.default_view = default_view
        self.AUTH_TOKEN_KEY = "app.auth_token"

    # ========================================
    # These methods initiate auth workflows
    async def initiate_login_flow(self, e: ft.Event[ft.EventControlType]):
        logging.info(f"Initiating login flow with Auth0, event {e}")

        saved_token = None
        ejt = await self.page.shared_preferences.get(self.AUTH_TOKEN_KEY)
        if ejt:
            logging.info(f"Using stored auth token: {ejt}")
            saved_token = decrypt(ejt, self.config.app_secret_key)

        await self.page.login(self.provider, saved_token=saved_token)

    async def initiate_logout_flow(self):
        # other login stuff goes here
        logging.info("Initiating logout flow with Auth0")
        await self.page.shared_preferences.remove(self.AUTH_TOKEN_KEY)
        self.page.logout()

    async def initiate_stored_token_only_login(self):
        ejt = await self.page.shared_preferences.get(self.AUTH_TOKEN_KEY)
        if ejt:
            logging.info(f"Using stored auth token: {ejt}")
            saved_token = decrypt(ejt, self.config.app_secret_key)
            await self.page.login(self.provider, saved_token=saved_token)

    # ========================================
    # These methods are called in response to events in the auth workflow
    async def on_login_succeeded(self, e: ft.LoginEvent):
        logging.info("Login succeeded")

        # save token in a client storage
        auth = self.page.auth
        assert isinstance(
            auth, AuthorizationService
        ), f"Expected a page.auth of type AuthorizationService but got {type(auth)}"

        token = await auth.get_token()
        jt = token.to_json()
        ejt = encrypt(jt, self.config.app_secret_key)

        logging.info(f"Storing auth token: {ejt}")
        await self.page.shared_preferences.set(self.AUTH_TOKEN_KEY, ejt)

    async def on_login_failed(self, e: ft.LoginEvent):
        logging.info("Login failed")

    async def on_login(self, e: ft.LoginEvent):
        if e.error:
            await self.on_login_failed(e)
        else:
            await self.on_login_succeeded(e)

        self.page.render_views(self.default_view, auth_status=self)

    def on_logout(self, e):
        logging.info("Logout successful")
        self.page.shared_preferences.remove(self.AUTH_TOKEN_KEY)
        self.page.render_views(self.default_view, auth_status=self)

    # ========================================
    # Utility functions

    @property
    def is_authenticated(self) -> bool:
        return ft.context.page.auth is not None


async def main(page: ft.Page):
    # Set up Auth0 provider
    provider = Auth0OAuthProvider(
        domain=CONFIG.auth0_domain,
        client_id=CONFIG.auth0_client_id,
        client_secret=CONFIG.auth0_client_secret,
        redirect_url="http://localhost:8550/oauth_callback",
    )

    auth_manager = AuthManager(
        page=page, config=CONFIG, provider=provider, default_view=LandingView
    )

    page.on_login = auth_manager.on_login
    page.on_logout = auth_manager.on_logout

    # If we have a stored token. try to login using it (but don't bring up a new Auth0 screen)
    await auth_manager.initiate_stored_token_only_login()

    page.render_views(LandingView, auth_status=auth_manager)


ft.run(main)
