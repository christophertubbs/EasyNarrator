"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing

import pydantic

from .base import AppearanceMessage


class KillResponse(AppearanceMessage):
    operation: typing.Literal['kill'] = pydantic.Field(description='Description stating that the application is being killed')