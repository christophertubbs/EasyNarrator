import typing

import pydantic

from .base import AppearanceRequest

from .data import FileSelectionRequest
from .management import KillRequest
from ...utilities.common import get_subclasses


def get_message_types() -> typing.Tuple[typing.Type[AppearanceRequest], ...]:
    return tuple([message_type for message_type in get_subclasses(AppearanceRequest)])


class MasterRequest(pydantic.BaseModel):
    request: typing.Union[get_message_types()]