"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import sys
import typing
import webbrowser

from aiohttp import web
from aiohttp.web_routedef import AbstractRoute
from aiohttp.web_routedef import RouteDef

from appearance_ui.application_details import ALLOW_REMOTE
from appearance_ui.application_details import INDEX_PAGE
from appearance_ui.handlers import navigate
from appearance_ui.launch_parameters import ApplicationArguments
from appearance_ui.utilities import common
from appearance_ui.handlers import handle_index
from appearance_ui.handlers import register_resource_handlers
from appearance_ui.handlers import socket_handler

from appearance_ui.application_details import APPLICATION_NAME


class LocalApplication(web.Application):
    """
    A webserver application that may only serve data accessible exclusively to the local environment
    """
    def add_routes(self, routes: typing.Iterable[RouteDef]) -> typing.List[AbstractRoute]:
        if not ALLOW_REMOTE:
            invalid_routes: typing.List[str] = list()
            for route in routes:
                handler = route.handler

                if not getattr(handler, common.LOCAL_ONLY_IDENTIFIER, False):
                    invalid_routes.append(route.path)

            if len(invalid_routes) > 0:
                message = f"Cannot register routes - " \
                          f"the following routes were not marked as local only: {', '.join(invalid_routes)}"
                raise ValueError(message)

        return super().add_routes(routes)


def serve(arguments: ApplicationArguments) -> typing.NoReturn:
    application = LocalApplication()

    register_resource_handlers(application)

    application.add_routes([
        web.get(f"/{INDEX_PAGE}", handler=handle_index),
        web.get("/navigate", handler=navigate),
        web.get("/ws", handler=socket_handler)
    ])

    entry_point: str = f"http://0.0.0.0:{arguments.port}/{INDEX_PAGE}"

    print(f"Access {APPLICATION_NAME} from {entry_point}")
    webbrowser.open(entry_point)
    web.run_app(application, port=arguments.port)


if __name__ == "__main__":
    serve(ApplicationArguments(*sys.argv[1:]))