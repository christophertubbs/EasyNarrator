"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing

import pydantic
from aiohttp import web

from .base import NarratorResponse
from ..base import DataMessage


class NarratorDataResponse(NarratorResponse, DataMessage):
    data: typing.Dict[str, typing.Any]


class ReadResponse(NarratorResponse):
    narration: bytes

    async def send(self, connection: web.WebSocketResponse):
        await connection.send_bytes(self.narration)


class AudioResponse(NarratorResponse):
    audio: str
    audio_index: typing.Optional[int] = pydantic.Field(
        default=0,
        description="The index of the audio in case of multiple parts"
    )
    audio_count: typing.Optional[int] = pydantic.Field(
        default=1,
        description="The expected number of audio tracks to transfer"
    )


class TransferCompleteResponse(NarratorResponse):
    operation: typing.Optional[typing.Literal['transfer_complete']] = pydantic.Field(default='transfer_complete')
    item_count: typing.Optional[int] = pydantic.Field(default=1, description="The number of items transferred")


class LoadMessageResponse(NarratorResponse):
    percent_complete: float = pydantic.Field(description="How complete the loading process is")
    message: str = pydantic.Field(description="A message describing what is happening")
    item_count: typing.Optional[int] = pydantic.Field(default=1, description="The number of items being loaded")
    count_complete: typing.Optional[int] = pydantic.Field(default=0, description="The number of items that are done loading")
    operation: typing.Optional[typing.Literal['load']] = pydantic.Field(default='load')