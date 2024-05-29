import typing

import pydantic

from .base import NarratorRequest

from .data import FileSelectionRequest
from .data import ReadRequest
from .management import KillRequest
from ...utilities.common import get_subclasses


def get_message_types() -> typing.Tuple[typing.Type[NarratorRequest], ...]:
    return tuple([message_type for message_type in get_subclasses(NarratorRequest)])


class MasterRequest(pydantic.BaseModel):
    request: typing.Union[get_message_types()]