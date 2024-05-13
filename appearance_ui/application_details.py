"""
Application specific metadata values used to convey basic operating parameters
"""
import logging
import os
import typing

APPLICATION_NAME: typing.Final[str] = os.environ.get("APPEARANCE_APPLICATION_NAME", "Appearance UI")
APPLICATION_DESCRIPTION: typing.Final[str] = os.environ.get(
    "APPEARANCE_APPLICATION_DESCRIPTION",
    """A local python application"""
)
DEFAULT_PORT: typing.Final[int] = int(os.environ.get("APPEARANCE_DEFAULT_PORT", 10324))
ALLOW_REMOTE: typing.Final[bool] = os.environ.get("APPEARANCE_ALLOW_REMOTE", "no").lower() in ('t', 'true', 'y', 'yes', '1')
INDEX_PAGE: typing.Final[str] = os.environ.get("APPEARANCE_INDEX_PAGE", "")

if ALLOW_REMOTE:
    logging.warning(
        f"{APPLICATION_NAME} has been configured to allow remote connections. "
        f"Ensure https is enabled or else risk internal file inspection from remote sources."
        f"Use at your own risk."
    )