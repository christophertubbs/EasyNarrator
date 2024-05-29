"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import abc
import typing
from os import PathLike


T = typing.TypeVar("T")


class BaseBackend(abc.ABC, typing.Generic[T]):
    @abc.abstractmethod
    def load(self, path: PathLike, *args, **kwargs) -> T:
        ...