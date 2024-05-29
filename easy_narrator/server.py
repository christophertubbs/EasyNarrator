#!/usr/bin/env python3
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

from easy_narrator.application_details import ALLOW_REMOTE
from easy_narrator.application_details import INDEX_PAGE
from easy_narrator.application_details import MODEL_CATALOG_PATH

from easy_narrator.handlers import navigate
from easy_narrator.handlers.http import get_model_parameters
from easy_narrator.handlers.http import get_parameters_for_all_models
from easy_narrator.handlers.http import view_sample_gallery
from easy_narrator.launch_parameters import ApplicationArguments
from easy_narrator.sample_generator import generate_samples
from easy_narrator.utilities import common
from easy_narrator.handlers import handle_index
from easy_narrator.handlers import register_resource_handlers
from easy_narrator.handlers import socket_handler
from easy_narrator.handlers import get_models

from easy_narrator.application_details import APPLICATION_NAME


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


def save_model_catalog():
    from easy_narrator.utilities.model_cache import ModelCache
    import json

    model_information = {
        model.fullname: model.dict()
        for model in ModelCache.get_available_models()
    }

    with MODEL_CATALOG_PATH.open("w") as model_catalog:
        json.dump(model_information, model_catalog, indent=4)


def serve(arguments: ApplicationArguments) -> typing.NoReturn:
    application = LocalApplication()

    if arguments.generate_model_catalog:
        save_model_catalog()
        return

    if arguments.generate_samples:
        generate_samples()
        return

    register_resource_handlers(application)

    application.add_routes([
        web.get(f"/{INDEX_PAGE}", handler=handle_index),
        web.get(f"/sample/gallery", handler=view_sample_gallery),
        web.get(f"/models/list", handler=get_models),
        web.get(f"/models/parameters", handler=get_parameters_for_all_models),
        web.get("/models/parameters/{model_name}", get_model_parameters),
        web.get("/navigate", handler=navigate),
        web.get("/ws", handler=socket_handler)
    ])

    entry_point: str = f"http://0.0.0.0:{arguments.port}/{INDEX_PAGE}"

    print(f"Access {APPLICATION_NAME} from {entry_point}")

    if arguments.open_browser:
        webbrowser.open(entry_point)

    web.run_app(application, port=arguments.port)


if __name__ == "__main__":
    serve(ApplicationArguments(*sys.argv[1:]))