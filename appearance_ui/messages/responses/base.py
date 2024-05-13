"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing

import pydantic

from ..base import AppearanceMessage


class AppearanceResponse(AppearanceMessage):
    ...


class OpenResponse(AppearanceResponse):
    operation: typing.Literal['connection_opened'] = pydantic.Field(default="connection_opened")


class AcknowledgementResponse(AppearanceResponse):
    operation: typing.Literal['acknowledgement'] = pydantic.Field(default="acknowledgement")