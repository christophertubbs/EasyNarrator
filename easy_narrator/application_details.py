"""
Application specific metadata values used to convey basic operating parameters
"""
import logging
import os
import typing
import re

from pathlib import Path

APPLICATION_NAME: typing.Final[str] = os.environ.get("NARRATOR_APPLICATION_NAME", "Easy Narrator")
SAFE_APPLICATION_NAME: typing.Final[str] = re.sub(
    r"_{2,}",
    "_",
    re.sub(
        r"[^a-zA-Z0-9_]",
        "_",
        APPLICATION_NAME
    )
).lower()
APPLICATION_DESCRIPTION: typing.Final[str] = os.environ.get(
    "NARRATOR_APPLICATION_DESCRIPTION",
    """A local document reader"""
)
DEFAULT_PORT: typing.Final[int] = int(os.environ.get("NARRATOR_DEFAULT_PORT", 10324))
ALLOW_REMOTE: typing.Final[bool] = os.environ.get("NARRATOR_ALLOW_REMOTE", "no").lower() in ('t', 'true', 'y', 'yes', '1')
DEBUG_MODE: typing.Final[bool] = os.environ.get("NARRATOR_DEBUG_MODE", "yes").lower() in ('t', 'true', 'y', 'yes', '1')
LOG_LEVEL: typing.Final[int] = logging.getLevelName(os.environ.get("NARRATOR_LOG_LEVEL", "DEBUG" if DEBUG_MODE else "INFO"))
INDEX_PAGE: typing.Final[str] = os.environ.get("NARRATOR_INDEX_PAGE", "")
BASE_DIRECTORY: typing.Final[Path] = Path(__file__).parent.absolute()
STATIC_DIRECTORY: typing.Final[Path] = BASE_DIRECTORY / "static"
RESOURCE_PATH: typing.Final[Path] = Path(
    os.environ.get("NARRATOR_RESOURCE_PATH", STATIC_DIRECTORY / "resources")
).absolute()
MODEL_CATALOG_PATH: typing.Final[Path] = Path(
    os.environ.get("NARRATOR_MODEL_CATALOG_PATH", RESOURCE_PATH / "model_catalog.json")
)
DATETIME_FORMAT: typing.Final[str] = os.environ.get("NARRATOR_DATETIME_FORMAT", "%Y-%m-%d %H:%M%z")