"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing
import pydantic

from .base import AppearanceRequest


class KillRequest(AppearanceRequest):
    operation: typing.Literal["kill"] = pydantic.Field(
        description="Description stating that this should kill the application"
    )