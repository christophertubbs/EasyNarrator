"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import inspect
import json
import logging
import random
import string
import sys
import typing

from dataclasses import dataclass
from dataclasses import field
from pprint import pprint

from aiohttp import WSMessage
from aiohttp import web

from ..messages.responses import AudioResponse
from ..messages.responses import invalid_message_response
from ..messages.responses.data import LoadMessageResponse
from ..messages.responses.data import TransferCompleteResponse
from ..narrate import break_down_sentences
from ..narrate import generate_sound
from ..utilities.common import local_only
from ..backend.base import BaseBackend
from ..backend.file import FileBackend
from ..messages.base import NarratorMessage
from ..messages.requests import FileSelectionRequest
from ..messages.requests import MasterRequest
from ..messages.requests import NarratorRequest
from ..messages.requests import ReadRequest
from ..messages.responses import ErrorResponse
from ..messages.responses import AcknowledgementResponse
from ..messages.responses import OpenResponse
from ..messages.responses import NoHandlerResponse
from ..messages.responses.data import NarratorDataResponse
from ..messages.requests import KillRequest
from ..messages.responses import KillResponse

from ..application_logging import get_logger

_LOGGER: logging.Logger = get_logger()

CONNECTION_ID_LENGTH = 10
CONNECTION_ID_CHARACTER_SET = string.hexdigits

REQUEST_TYPE = typing.TypeVar("REQUEST_TYPE", bound=NarratorRequest, covariant=True)
RESPONSE_TYPE = typing.TypeVar("RESPONSE_TYPE", bound=NarratorMessage, covariant=True)

_KILL_SYMBOL = object()


@dataclass
class SocketState:
    """
    The state for the single page app
    """
    connection: web.WebSocketResponse
    backend: BaseBackend = field(default_factory=FileBackend)
    data: typing.Dict[str, typing.Any] = field(default_factory=dict)


HANDLER = typing.Callable[[REQUEST_TYPE, SocketState], typing.Union[RESPONSE_TYPE, typing.Sequence[RESPONSE_TYPE]]]


def load_file(request: FileSelectionRequest, state: SocketState) -> NarratorDataResponse:
    data = state.backend.load(request.path)
    name = "::".join(
        [
            part.replace(" ", "-")
            for part in str(request.path).split("/")
            if part
        ][-3:]
    )
    response = NarratorDataResponse(
        operation=request.operation,
        data_id=name,
        data={"content": data},
        message_id=request.message_id
    )

    return response


def kill_application(request: KillRequest, state: SocketState) -> KillResponse:
    return KillResponse(operation="kill")


async def read_text(request: ReadRequest, state: SocketState) -> TransferCompleteResponse:
    if not request.text:
        raise ValueError("Cannot generate sound - no text provided")

    text = break_down_sentences(request.text)

    item_count = len(text) * 3
    items_complete = 0

    await LoadMessageResponse(
        percent_complete=items_complete / item_count,
        item_count=item_count,
        message=f"Generating sound..."
    ).send(state.connection)

    audio = generate_sound(request.text, request.configuration)

    items_complete += len(text)

    await LoadMessageResponse(
        message="Sound generated...",
        percent_complete=(items_complete / item_count) * 100.0,
    ).send(state.connection)

    if not isinstance(audio, typing.List):
        audio = [audio]

    for sound_index, sound in enumerate(audio):
        items_complete += 1
        await LoadMessageResponse(
            percent_complete=(items_complete / item_count) * 100.0,
            item_count=item_count,
            count_complete=items_complete + sound_index,
            message=f"Sending track {sound_index + 1} of {len(audio)}..."
        ).send(state.connection)
        await state.connection.send_bytes(sound)

    await LoadMessageResponse(
        message_id=request.message_id,
        percent_complete=100.0,
        item_count=item_count,
        count_complete=items_complete,
        message="All audio sent"
    ).send(state.connection)

    return TransferCompleteResponse(message_id=request.message_id, item_count=len(audio))


MESSAGE_HANDLERS: typing.Mapping[typing.Type[REQUEST_TYPE], typing.Union[HANDLER, typing.Sequence[HANDLER]]] = {
    FileSelectionRequest: load_file,
    KillRequest: kill_application,
    ReadRequest: read_text
}


def default_message_handler(request: NarratorRequest, state: SocketState) -> RESPONSE_TYPE:
    return NoHandlerResponse(message_id=request.message_id)


async def handle_message(
    connection: web.WebSocketResponse,
    message: typing.Union[str, bytes, dict],
    state: SocketState
):
    if isinstance(message, (str, bytes)):
        message = json.loads(message)

    request: typing.Optional[NarratorRequest] = None
    responses: typing.List[typing.Union[RESPONSE_TYPE, str, dict, bytes, None, BaseException]] = []

    try:
        request_wrapper = MasterRequest.model_validate({"request": message})
        request = request_wrapper.request
        _LOGGER.debug(f"Parsed request as {type(request)}")
    except Exception as error:
        print(error)
        print("Could not deserialize incoming message:")
        pprint(message)
        responses.append(invalid_message_response())

    if isinstance(request, NarratorRequest):
        handler = MESSAGE_HANDLERS.get(type(request), default_message_handler)

        if isinstance(handler, typing.Sequence):
            handlers: typing.Sequence[HANDLER] = handler
        else:
            handlers: typing.Sequence[HANDLER] = [handler]

        for function in handlers:
            try:
                response = function(request, state)

                while inspect.isawaitable(response):
                    response = await response

                if isinstance(response, typing.Iterable) and not isinstance(response, NarratorMessage):
                    responses.extend(response)
                else:
                    responses.append(response)
            except BaseException as error:
                message = f"An error occurred while handling a `{type(request).__name__}` message: {str(error)}"
                _LOGGER.error(
                    message,
                    exc_info=error,
                    stack_info=True
                )
                responses.append(
                    ErrorResponse(
                        message_id=request.message_id,
                        message_type=type(request).__name__,
                        error_message=message
                    )
                )

    for response in responses:
        try:
            if isinstance(response, bytes):
                await connection.send_bytes(data=response)
            elif isinstance(response, str):
                await connection.send_str(data=response)
            elif isinstance(response, dict):
                await connection.send_json(data=response)
            elif isinstance(response, NarratorMessage):
                await response.send(connection=connection)
            elif isinstance(response, BaseException):
                error_response = ErrorResponse(
                    message_id=request.message_id,
                    message_type=type(request).__name__,
                    error_message=str(response)
                )
                await error_response.send(connection=connection)
            elif response is not None:
                message = (f"Cannot send a response for an '{request.operation}' operation - "
                           f"the resulting value was a {type(response).__name__}, which cannot be transmitted")
                _LOGGER.error(message)
                error_message = ErrorResponse(
                    message_id=request.message_id,
                    message_type=type(request).__name__,
                    error_message=message
                )
                await error_message.send(connection=connection)
            else:
                acknowledgement = AcknowledgementResponse(message_id=request.message_id)
                await acknowledgement.send(connection=connection)
        except TypeError as error:
            error_response = ErrorResponse(
                message_id=request.message_id,
                message_type=type(request).__name__,
                error_message=str(error)
            )
            await error_response.send(connection=connection)

    if isinstance(request, KillRequest):
        return _KILL_SYMBOL


@local_only
async def socket_handler(request: web.Request) -> web.WebSocketResponse:
    connection = web.WebSocketResponse()

    connection_id = ''.join(random.choices(population=CONNECTION_ID_CHARACTER_SET, k=CONNECTION_ID_LENGTH))

    await connection.prepare(request=request)
    state = SocketState(connection=connection)

    print(f"Connected to socket {connection_id} from {request.remote}")

    open_response = OpenResponse()

    await connection.send_json(open_response.model_dump())
    result = None
    async for message in connection:  # type: WSMessage
        _LOGGER.info(f"Received {message.data} from socket")
        result = await handle_message(connection, message=message.data, state=state)

        if result == _KILL_SYMBOL:
            print(f"Instructed to kill the application")
            break

    print(f"Connection to Socket {connection_id} closing")

    if result == _KILL_SYMBOL:
        sys.exit(0)

    return connection