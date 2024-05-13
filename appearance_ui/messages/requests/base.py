"""
Defines base classes for request messages
"""
from __future__ import annotations
from abc import ABC

from ..base import AppearanceMessage
from ..base import DataMessage


class AppearanceRequest(AppearanceMessage, ABC):
    ...


class AppearanceDataRequest(AppearanceRequest, DataMessage, ABC):
    ...