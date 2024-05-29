"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

from os import PathLike

from .base import BaseBackend


class FileBackend(BaseBackend[bytes]):
    def load(self, path: PathLike, *args, **kwargs) -> bytes:
        with open(path, 'rb') as source:
            data = source.read()

        return data