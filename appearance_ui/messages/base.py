"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import abc
import typing

import pydantic


class AppearanceMessage(pydantic.BaseModel, abc.ABC):
    """
    A common base class for all messages
    """
    operation: str = pydantic.Field(description="The name of the operation to perform")
    message_id: typing.Optional[str] = pydantic.Field(default=None, description="A trackable ID for the message")


class DataMessage(pydantic.BaseModel):
    data_id: str = pydantic.Field(description="The ID of the data to pass back and forth")