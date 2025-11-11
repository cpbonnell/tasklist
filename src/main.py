import logging
from dataclasses import dataclass, field
from typing import Callable, cast

import warnings


from tasklist.components import TodoAppView
from tasklist.login import PreLoginView, AuthenticationStatus
from tasklist.configuration import Configuration

import flet as ft

# ignore *all* DeprecationWarnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

logging.basicConfig(level=logging.INFO)

config = Configuration()


@ft.component
def EnsureLoggedInView():
    auth_status, _ = ft.use_state(AuthenticationStatus())

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


@ft.component
def App():
    return ft.Text("Hello, Flet!")


def main(page: ft.Page):
    page.render_views(EnsureLoggedInView)


ft.run(main)
