"""
The argument parser for the application
"""
from __future__ import annotations

import argparse
import typing

from easy_narrator import application_details


class ApplicationArguments:
    def __init__(self, *argv):
        self.__port: typing.Optional[int] = None
        self.__index_page: typing.Optional[str] = None
        self.__open_browser: bool = False
        self.__generate_model_catalog: bool = False
        self.__generate_models: bool = False

        self.__parse_arguments(*argv)

    @property
    def port(self) -> int:
        return self.__port

    @property
    def generate_model_catalog(self) -> bool:
        return self.__generate_model_catalog

    @property
    def index_page(self) -> str:
        return self.__index_page

    @property
    def open_browser(self) -> bool:
        return self.__open_browser

    @property
    def generate_samples(self) -> bool:
        return self.__generate_samples

    def __parse_arguments(self, *argv):
        parser = argparse.ArgumentParser(
            prog=application_details.APPLICATION_NAME,
            description=application_details.APPLICATION_DESCRIPTION
        )

        parser.add_argument(
            "--generate-model-catalog",
            action="store_true",
            dest="generate_model_catalog",
            help="Generate a listing of available models, their languages, and their speakers"
        )

        parser.add_argument(
            "--generate-samples",
            action="store_true",
            dest="generate_samples",
            help="Generate samples for each voice for each model"
        )

        parser.add_argument(
            "-p",
            "--port",
            dest="port",
            default=application_details.DEFAULT_PORT,
            help="The port to run the application on"
        )

        parser.add_argument(
            "--open-browser",
            dest="open_browser",
            action="store_true",
            default=False,
            help="Open a new tab to show the application in the default browser"
        )

        parser.add_argument(
            "-i",
            "--index",
            dest="index_page",
            default=application_details.INDEX_PAGE,
            help="The path to the index page"
        )

        parameters = parser.parse_args(argv)

        self.__port = parameters.port
        self.__index_page = parameters.index_page
        self.__open_browser = parameters.open_browser
        self.__generate_model_catalog = parameters.generate_model_catalog
        self.__generate_samples = parameters.generate_samples

