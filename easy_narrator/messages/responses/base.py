"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing

import pydantic
from aiohttp import web

from ..base import NarratorMessage


class NarratorResponse(NarratorMessage):
    async def send(self, connection: web.WebSocketResponse):
        return await connection.send_json(self.model_dump())


class OpenResponse(NarratorResponse):
    operation: typing.Literal['connection_opened'] = pydantic.Field(default="connection_opened")


class AcknowledgementResponse(NarratorResponse):
    operation: typing.Literal['acknowledgement'] = pydantic.Field(default="acknowledgement")


class NoHandlerResponse(NarratorResponse):
    operation: typing.Literal['no_handler'] = pydantic.Field(default="no_handler")
    message: typing.Optional[str] = pydantic.Field(default="The received message does not have a handler")