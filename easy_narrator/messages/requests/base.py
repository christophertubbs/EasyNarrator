"""
Defines base classes for request messages
"""
from __future__ import annotations
from abc import ABC

from ..base import NarratorMessage
from ..base import DataMessage


class NarratorRequest(NarratorMessage, ABC):
    ...


class NarratorDataRequest(NarratorRequest, DataMessage, ABC):
    ...