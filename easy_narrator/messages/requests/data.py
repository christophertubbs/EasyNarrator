"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import pathlib
import typing
from datetime import datetime

import pydantic

from .base import NarratorRequest
from ...models.narration_config import NarrationConfig
from ...models import get_narration_config_types

_INDEX_TYPE = typing.Union[datetime, str, float, int]


class FileSelectionRequest(NarratorRequest):
    """
    A message asking for a netcdf file at a given location
    """
    operation: typing.Literal['load'] = pydantic.Field(description="Description stating that this should be loading data")
    path: pathlib.Path = pydantic.Field(description="The path to the requested file")


class ReadRequest(NarratorRequest):
    """
    A message asking to generate sound reading the given text
    """
    operation: typing.Literal['read'] = pydantic.Field(
        description="Description stating that this should be reading text"
    )
    text: str = pydantic.Field(description="The text to read")
    configuration: typing.Optional[get_narration_config_types()] = pydantic.Field(
        default_factory=NarrationConfig,
        description="Values for how to configure models for narrating the given text"
    )