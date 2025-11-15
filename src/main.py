import logging
import warnings

import flet as ft
from flet.auth.providers import Auth0OAuthProvider

from tasklist.components import TodoAppView
from tasklist.configuration import Configuration
from tasklist.login import AuthenticationStatus, PreLoginView

# ignore *all* DeprecationWarnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

logging.basicConfig(level=logging.INFO)

CONFIG = Configuration()


@ft.component
def EnsureLoggedInView(auth_status: AuthenticationStatus):

    logging.info(
        f"Rendering EnsureLoggedInView -- Auth status is '{auth_status.is_authenticated}'"
    )
    # ft.context.page.auth

    if not auth_status.is_authenticated:
        logging.info(f"Rendering EnsureLoggedInView -- returning PreLoginView")
        return PreLoginView(initiate_login_flow=auth_status.initiate_login_flow)
    else:
        logging.info(f"Rendering EnsureLoggedInView -- returning TodoAppView")
        return TodoAppView(initiate_logout_flow=auth_status.initiate_logout_flow)


async def main(page: ft.Page):
    # Set up Auth0 provider
    provider = Auth0OAuthProvider(
        domain=CONFIG.auth0_domain,
        client_id=CONFIG.auth0_client_id,
        client_secret=CONFIG.auth0_client_secret,
        redirect_url="http://localhost:8550/oauth_callback",
    )
    auth_status = AuthenticationStatus(config=CONFIG, provider=provider)

    page.on_login = auth_status.on_login
    page.on_logout = auth_status.on_logout

    page.render_views(EnsureLoggedInView, auth_status=auth_status)


ft.run(main)
