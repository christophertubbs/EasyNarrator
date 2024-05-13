"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing

from .base import AppearanceResponse
from ..base import DataMessage


class AppearanceDataResponse(AppearanceResponse, DataMessage):
    data: typing.Dict[str, typing.Any]