"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing

import pydantic

from .base import NarratorResponse


class KillResponse(NarratorResponse):
    operation: typing.Literal['kill'] = pydantic.Field(description='Description stating that the application is being killed')