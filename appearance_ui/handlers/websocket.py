"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import json
import logging
import os
import random
import string
import sys
import typing
import inspect

from dataclasses import dataclass
from dataclasses import field
from pprint import pprint

from aiohttp import WSMessage
from aiohttp import web

from ..messages.responses import invalid_message_response
from ..utilities.common import local_only
from ..backend.base import BaseBackend
from ..backend.file import FileBackend
from ..messages.base import AppearanceMessage
from ..messages.requests import FileSelectionRequest
from ..messages.requests import MasterRequest
from ..messages.requests import AppearanceRequest
from ..messages.responses import ErrorResponse
from ..messages.responses.base import AcknowledgementResponse
from ..messages.responses.base import OpenResponse
from ..messages.responses.data import AppearanceDataResponse
from ..messages.requests import KillRequest
from ..messages.responses import KillResponse

CONNECTION_ID_LENGTH = 10
CONNECTION_ID_CHARACTER_SET = string.hexdigits

REQUEST_TYPE = typing.TypeVar("REQUEST_TYPE", bound=AppearanceRequest, covariant=True)
RESPONSE_TYPE = typing.TypeVar("RESPONSE_TYPE", bound=AppearanceMessage, covariant=True)

_KILL_SYMBOL = object()


@dataclass
class SocketState:
    """
    The state for the single page app
    """
    backend: BaseBackend = field(default_factory=FileBackend)
    data: typing.Dict[str, typing.Any] = field(default_factory=dict)


HANDLER = typing.Callable[[REQUEST_TYPE, SocketState], RESPONSE_TYPE]


def load_file(request: FileSelectionRequest, state: SocketState) -> AppearanceDataResponse:
    data = state.backend.load(request.path)
    name = "::".join(
        [
            part.replace(" ", "-")
            for part in str(request.path).split("/")
            if part
        ][-3:]
    )
    response = AppearanceDataResponse(
        operation=request.operation,
        data_id=name,
        data={"content": data},
        message_id=request.message_id
    )

    return response


def kill_application(request: KillRequest, state: SocketState) -> KillResponse:
    return KillResponse(operation="kill")


MESSAGE_HANDLERS: typing.Mapping[typing.Type[REQUEST_TYPE], typing.Union[HANDLER, typing.Sequence[HANDLER]]] = {
    FileSelectionRequest: load_file,
    KillRequest: kill_application
}


def default_message_handler(request: AppearanceRequest, state: SocketState) -> RESPONSE_TYPE:
    return AcknowledgementResponse(message_id=request.message_id)


async def handle_message(
    connection: web.WebSocketResponse,
    message: typing.Union[str, bytes, dict],
    state: SocketState
):
    if isinstance(message, (str, bytes)):
        message = json.loads(message)

    request: typing.Optional[AppearanceRequest] = None
    response = None

    try:
        request_wrapper = MasterRequest.model_validate({"request": message})
        request = request_wrapper.request
    except Exception as error:
        print(error)
        print("Could not deserialize incoming message:")
        pprint(message)
        response = invalid_message_response()

    if isinstance(request, AppearanceRequest):
        try:
            handler = MESSAGE_HANDLERS.get(type(request), default_message_handler)

            if isinstance(handler, typing.Sequence):
                handlers: typing.Sequence[HANDLER] = handler
            else:
                handlers: typing.Sequence[HANDLER] = [handler]

            for function in handlers:
                response = function(request, state)

            if response is None:
                response = default_message_handler(request, state)

        except BaseException as error:
            message = f"An error occurred while handling a `{type(request).__name__}` message: {str(error)}"
            logging.error(
                message,
                exc_info=error,
                stack_info=True
            )
            response = ErrorResponse(
                message_id=request.message_id,
                message_type=type(request).__name__,
                error_message=message
            )

    try:
        await connection.send_json(response.model_dump())
    except TypeError as error:
        error = ErrorResponse(
            message_id=request.message_id,
            message_type=type(request).__name__,
            error_message=str(error)
        )
        await connection.send_json(error.model_dump())

    if isinstance(request, KillRequest):
        return _KILL_SYMBOL


@local_only
async def socket_handler(request: web.Request) -> web.WebSocketResponse:
    connection = web.WebSocketResponse()

    connection_id = ''.join(random.choices(population=CONNECTION_ID_CHARACTER_SET, k=CONNECTION_ID_LENGTH))

    await connection.prepare(request=request)
    state = SocketState()

    print(f"Connected to socket {connection_id} from {request.remote}")

    open_response = OpenResponse()

    await connection.send_json(open_response.model_dump())
    result = None
    async for message in connection:  # type: WSMessage
        result = await handle_message(connection, message=message.data, state=state)

        if result == _KILL_SYMBOL:
            print(f"Instructed to kill the application")
            break

    print(f"Connection to Socket {connection_id} closing")

    if result == _KILL_SYMBOL:
        sys.exit(0)

    return connection