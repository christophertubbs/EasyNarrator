"""
@TODO: Put a module wide description here
"""
import typing
import inspect

from .narration_config import NarrationConfig
from .narration_config import VCTKVITSConfig
from .narration_config import XTTSv2Config
from .narration_config import GenericSpeakerLanguageConfig

from ..utilities.common import get_subclasses
from .model_info import ModelInfo


NarratorConfiguration = typing.TypeVar('NarratorConfiguration', bound=NarrationConfig)


def get_narration_config_types() -> typing.Type[typing.Union[NarratorConfiguration, ...]]:
    """
    Create a Union of all concrete NarrationConfig types

    Helps define all possible objects that are allowable/parseable as a config in requests for reading
    """
    types = tuple([GenericSpeakerLanguageConfig, NarrationConfig])
    return typing.Union[tuple(types)]
