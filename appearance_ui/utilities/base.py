"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing

import pydantic


ATTRIBUTE_VALUE = typing.Union[int, float, str, bool, None]


class TextValueEntry(pydantic.BaseModel):
    text: str = pydantic.Field(description="Text to show to a user")
    value: str = pydantic.Field(description="The value of the entry")
    attributes: typing.Optional[typing.Dict[str, ATTRIBUTE_VALUE]] = pydantic.Field(
        default_factory=dict,
        description="Values to include with the entry"
    )

    def __init__(self, text: str, value: str, attributes: typing.Dict[str, ATTRIBUTE_VALUE] = None, **kwargs):
        if attributes is None and kwargs:
            attributes = {key: value for key, value in kwargs.items()}
        elif kwargs:
            attributes.update(kwargs)

        super().__init__(text=text, value=value, attributes=attributes, **kwargs)

    def __setitem__(self, key: str, value: ATTRIBUTE_VALUE):
        self.attributes[key] = value

    def __getitem__(self, key: str) -> ATTRIBUTE_VALUE:
        return self.attributes[key]

    def get(self, key: str, default: ATTRIBUTE_VALUE) -> ATTRIBUTE_VALUE:
        return self.attributes.get(key, default)

    def __str__(self):
        return f"{self.text} => {self.value}"

    def __repr__(self):
        return self.__str__()