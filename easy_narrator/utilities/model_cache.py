"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing
import os
import sys

from pathlib import Path

from TTS.api import TTS
from torch import cuda

from ..models import ModelInfo



class ModelCache:
    __instance: ModelCache = None

    @classmethod
    def get_model(cls, model_name: str) -> TTS:
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance.get(model_name)

    @classmethod
    def get_available_models(cls) -> typing.Sequence[ModelInfo]:
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance.available_models

    @classmethod
    def is_available(cls, model: typing.Union[ModelInfo, str]) -> bool:
        if cls.__instance is None:
            cls.__instance = cls()
        return model in cls.__instance

    def __init__(self):
        self._cache = {}
        self._tts_directory = get_tts_data_dir()

    def get(self, model_name: str) -> TTS:
        if model_name not in self._cache:
            device = "cuda" if cuda.is_available() else "cpu"
            model: TTS = TTS(model_name).to(device=device)
            self._cache[model_name] = model
        return self._cache[model_name]

    @property
    def models(self) -> typing.List[ModelInfo]:
        return [
            ModelInfo(fullname=model_name)
            for model_name in TTS.list_models()
            if model_name.startswith("tts_model")
        ]

    @property
    def available_models(self) -> typing.List[ModelInfo]:
        models = [
            ModelInfo(fullname=full_model_name)
            for full_model_name in get_downloaded_models()
        ]

        for model in models:
            model.model_cache = self

        return models

    def __contains__(self, model_name: typing.Union[str, ModelInfo]) -> bool:
        if isinstance(model_name, str):
            return model_name in [model.fullname for model in self.available_models]
        return model_name in self.available_models


def get_tts_data_dir() -> Path:
    TTS_HOME = os.environ.get("TTS_HOME")
    XDG_DATA_HOME = os.environ.get("XDG_DATA_HOME")
    if TTS_HOME is not None:
        ans = Path(TTS_HOME).expanduser().resolve(strict=False)
    elif XDG_DATA_HOME is not None:
        ans = Path(XDG_DATA_HOME).expanduser().resolve(strict=False)
    elif sys.platform == "win32":
        import winreg  # pylint: disable=import-outside-toplevel

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
        )
        dir_, _ = winreg.QueryValueEx(key, "Local AppData")
        ans = Path(dir_).resolve(strict=False)
    elif sys.platform == "darwin":
        ans = Path("~/Library/Application Support/").expanduser()
    else:
        ans = Path.home().joinpath(".local/share")
    return ans.joinpath("tts")


def get_downloaded_models() -> typing.List[str]:
    return [
        directory.stem.replace("--", "/")
        for directory in get_tts_data_dir().iterdir()
        if directory.stem.startswith("tts_model")
    ]