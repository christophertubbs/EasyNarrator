"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing
import pydantic

from .base import NarratorRequest


class KillRequest(NarratorRequest):
    operation: typing.Literal["kill"] = pydantic.Field(
        description="Description stating that this should kill the application"
    )