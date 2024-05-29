"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing
import json

import pydantic

from easy_narrator.application_details import MODEL_CATALOG_PATH
from easy_narrator.application_details import RESOURCE_PATH


def get_vctk_speakers() -> typing.Type[typing.Union[typing.Literal, ...]]:
    """
    Get a type hint of all available vctk speakers
    """
    from pandas import read_csv
    vctk_speaker_metadata = read_csv(RESOURCE_PATH / "vits_speakers.csv")
    speakers = tuple(typing.Literal[name] for name in vctk_speaker_metadata.ID)
    return typing.Union[speakers]


def get_xtts_v2_speakers() -> typing.Type[typing.Union[typing.Literal, ...]]:
    from pandas import read_csv
    xtts_v2_speaker_metadata = read_csv(RESOURCE_PATH / "xtts_v2_speakers.csv")
    speakers = tuple(typing.Literal[name] for name in xtts_v2_speaker_metadata.ID)
    return typing.Union[speakers]


def get_model_names() -> typing.Type[typing.Union[typing.Literal, ...]]:
    """
    Get a type hint for all valid model names
    """
    if MODEL_CATALOG_PATH.exists():
        with MODEL_CATALOG_PATH.open("r") as model_catalog_file:
            names = tuple([typing.Literal[name] for name in json.load(model_catalog_file).keys()])
    else:
        from TTS.api import TTS
        names = tuple(typing.Literal[name] for name in TTS.list_models())
    return typing.Union[names]


class NarrationConfig(pydantic.BaseModel):
    """
    A basic configuration describing how text should be read aloud
    """
    name: get_model_names() = pydantic.Field(
        default="tts_models/en/ljspeech/tacotron2-DDC_ph",
        description="The name of the preconfigured model to use to narrate text"
    )
    speed: typing.Optional[float] = pydantic.Field(
        default=1.0,
        gt=0.0,
        le=2.0,
        description="The speed of speech. May not be respected."
    )

    def get_model(self):
        from TTS.api import TTS
        from torch import cuda
        device = "cuda" if cuda.is_available() else "cpu"
        return TTS(self.name).to(device=device)

    def get_arguments(self) -> typing.Dict[str, typing.Any]:
        return {
            field_name: getattr(self, field_name)
            for field_name, field in self.__fields__.items()
            if field_name != 'model_name'
               and getattr(self, field_name)
        }

    @property
    def description(self) -> str:
        return f'{self.name} played at {self.speed * 100.0}% speed'


class GenericSpeakerLanguageConfig(NarrationConfig):
    speaker: typing.Optional[str] = pydantic.Field(
        default=None,
        description="The speaker for the model"
    )
    language: typing.Optional[str] = pydantic.Field(
        default=None,
        description="The language for the generated model to speak"
    )


class XTTSv2Config(NarrationConfig):
    name: typing.Literal["tts_models/multilingual/multi-dataset/xtts_v2"] = pydantic.Field(
        description="The name of the preconfigured model to use to narrate text"
    )
    speaker: typing.Optional[get_xtts_v2_speakers()] = pydantic.Field(
        default="Claribel Dervla",
        description="The voice of the generated model (Only valid with models that support multiple speakers)"
    )
    language: str = pydantic.Field(default="en", description="The language for the generated model to speak")


class VCTKVITSConfig(NarrationConfig):
    """
    Configuration for setting up a model that uses the VCTK dataset and a VITS model in english
    """
    name: typing.Literal["tts_models/en/vctk/vits"] = pydantic.Field(
        description="The name of the preconfigured model to use to narrate text"
    )

    speaker: typing.Optional[get_vctk_speakers()] = pydantic.Field(
        default="p308",
        description="The voice of the generated model (Only valid with models that support multiple speakers)"
    )

    @property
    def description(self) -> str:
        return f'{self.model_name} with the {self.speaker} speaker played at {self.speed * 100.0}% speed'