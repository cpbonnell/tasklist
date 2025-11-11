import logging
from dataclasses import dataclass, field
from typing import Callable, cast

import warnings


from tasklist.components import TodoAppView
from tasklist.login import PreLoginView
from tasklist.configuration import Configuration

import flet as ft

# ignore *all* DeprecationWarnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

logging.basicConfig(level=logging.INFO)

config = Configuration()


@ft.component
def EnsureLoggedInView():
    is_authenticated, set_is_authenticated = ft.use_state(False)
    user, set_user = ft.use_state(None)

    def initiate_login_flow():
        # other login stuff goes here
        set_user("Someone")
        set_is_authenticated(True)
        logging.info("Login successful")

    def initiate_logout_flow():
        # other login stuff goes here
        set_user(None)
        set_is_authenticated(False)
        logging.info("Logout successful")

    logging.info(f"Rendering EnsureLoggedInView -- Auth status is '{is_authenticated}'")
    # ft.context.page.auth

    if not is_authenticated:
        logging.info(f"Rendering EnsureLoggedInView -- returning PreLoginView")
        return PreLoginView(initiate_login_flow=initiate_login_flow)
    else:
        logging.info(f"Rendering EnsureLoggedInView -- returning TodoAppView")
        return TodoAppView(initiate_logout_flow=initiate_logout_flow)


@ft.component
def App():
    return ft.Text("Hello, Flet!")


def main(page: ft.Page):
    page.render_views(EnsureLoggedInView)


ft.run(main)
