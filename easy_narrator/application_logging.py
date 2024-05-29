"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing
import logging

from threading import RLock

from .application_details import DATETIME_FORMAT
from .application_details import APPLICATION_NAME
from .application_details import SAFE_APPLICATION_NAME
from .application_details import ALLOW_REMOTE
from .application_details import LOG_LEVEL

_LOG_FORMAT: typing.Final[str] = '[%(asctime)s] %(levelname)s: %(message)s'


class ApplicationLog:
    __instance = None
    __lock: RLock = RLock()
    __application_logger: logging.Logger = None

    @classmethod
    def get_application_logger(cls) -> logging.Logger:
        if not cls.__application_logger:
            cls.__application_logger = cls.__create_application_logger()
        return cls.__application_logger

    @classmethod
    def __create_application_logger(cls) -> logging.Logger:
        application_logger: logging.Logger = logging.getLogger(SAFE_APPLICATION_NAME)
        application_logger.setLevel(LOG_LEVEL)

        application_logger_handler: logging.Handler = logging.StreamHandler()
        application_logger_handler.setFormatter(logging.Formatter(_LOG_FORMAT))

        application_logger.addHandler(application_logger_handler)
        return application_logger

    @classmethod
    def initialize(cls):
        cls.__instance = cls()

    def __init__(self):
        self.__configured = False
        self._setup()

    def _setup(self):
        with self.__lock:
            if self.__configured:
                return

            logging.basicConfig(
                level=logging.ERROR,
                datefmt=DATETIME_FORMAT
            )

            self.__configured = True

            if ALLOW_REMOTE:
                logging.warning(
                    f"{APPLICATION_NAME} has been configured to allow remote connections. "
                    f"Ensure https is enabled or else risk internal file inspection from remote sources."
                    f"Use at your own risk."
                )


ApplicationLog.initialize()
get_logger = ApplicationLog.get_application_logger
