"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import pathlib
import typing
from datetime import datetime

import pydantic

from .base import AppearanceRequest

_INDEX_TYPE = typing.Union[datetime, str, float, int]


class FileSelectionRequest(AppearanceRequest):
    """
    A message asking for a netcdf file at a given location
    """
    operation: typing.Literal['load'] = pydantic.Field(description="Description stating that this should be loading data")
    path: pathlib.Path = pydantic.Field(description="The path to the requested file")