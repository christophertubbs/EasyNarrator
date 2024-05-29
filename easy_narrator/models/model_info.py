"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing
from typing import Any

from pydantic import BaseModel
from pydantic import Field
from pydantic import PrivateAttr
from pydantic.main import IncEx


class ModelProtocol(typing.Protocol):
    @property
    def is_multi_lingual(self) -> bool:
        ...

    @property
    def is_multi_speaker(self) -> bool:
        ...

    @property
    def speakers(self) -> typing.List[str]:
        ...

    @property
    def languages(self) -> typing.Optional[typing.List[str]]:
        ...


class CacheProtocol(typing.Protocol):
    @classmethod
    def get_model(cls, model_name: str) -> ModelProtocol:
        pass

    def get(self, model_name: str) -> ModelProtocol:
        pass

    @property
    def models(self) -> typing.List[ModelInfo]:
        ...

    @property
    def available_models(self) -> typing.List[ModelInfo]:
        ...


class ModelInfo(BaseModel):
    fullname: str
    name: str = Field(default=None)
    language: str = Field(default=None)
    dataset: str = Field(default=None)
    _cache: CacheProtocol = PrivateAttr(default=None)

    def __init__(self, fullname: str, **kwargs):
        fullname = fullname.strip().replace("--", "/")
        _, formed_language, formed_dataset, formed_name = fullname.split("/")

        if 'name' not in kwargs:
            kwargs['name'] = formed_name

        if 'language' not in kwargs:
            kwargs['language'] = formed_language

        if "dataset" not in kwargs:
            kwargs['dataset'] = formed_dataset

        super().__init__(fullname=fullname, **kwargs)

    def dict(  # noqa: D102
        self,
        *,
        include: IncEx = None,
        exclude: IncEx = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> typing.Dict[str, Any]:
        generated_dictionary = super().dict()
        generated_dictionary.update(
            is_available=self.is_available,
            is_multi_lingual=self.is_multi_lingual,
            is_multi_speaker=self.is_multi_speaker,
            languages=self.languages,
            speakers=self.speakers
        )
        return generated_dictionary

    @property
    def model_cache(self) -> typing.Optional[CacheProtocol]:
        return self._cache

    @model_cache.setter
    def model_cache(self, cache: CacheProtocol):
        self._cache = cache

    @property
    def model(self) -> typing.Optional[ModelProtocol]:
        if self.is_available:
            return self.model_cache.get_model(self.fullname)
        raise Exception(f"Cannot get a model for {self.fullname}; it is not available and must be downloaded.")

    @property
    def is_available(self) -> bool:
        return self.model_cache is not None and self in self.model_cache.available_models

    @property
    def is_multi_lingual(self) -> typing.Optional[bool]:
        if not self.is_available:
            return None
        return self.model.is_multi_lingual

    @property
    def is_multi_speaker(self) -> typing.Optional[bool]:
        if not self.is_available:
            return None
        return self.model.is_multi_speaker

    @property
    def speakers(self) -> typing.Optional[typing.List[str]]:
        if not self.is_available:
            return None
        return self.model.speakers or []

    @property
    def languages(self) -> typing.Optional[typing.List[str]]:
        if not self.is_available:
            return [self.language] if self.language != 'multilingual' else None
        return self.model.languages or [self.language]

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash((self.fullname, self.name, self.dataset, self.language))

