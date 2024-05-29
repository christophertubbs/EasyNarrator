"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import os
import string
import typing
import io
import re
import enum

from easy_narrator.models import NarratorConfiguration
from easy_narrator.application_logging import get_logger

_LOGGER = get_logger()

NEWLINE_SEPARATOR = "$$NEWLINE$$"

HEADER_PATTERN = re.compile(r"^\d+\. .+(?=\n)", re.MULTILINE)
BULLET_PATTERN = re.compile(r"^([*-]|[a-zA-Z][.)]|\d+[.)]) ([^\n]|\n {4,})+")
ACRONYM_PATTERN = re.compile(r"(?P<letter>([A-Z](?=[A-Z.])|(?<=[A-Z])[.A-Z\d]))")


class PhraseType(enum.Enum):
    HEADER = "Header"
    CONTENT = "Content"
    SUBHEADER = "Subheader"
    BULLET = "Bullet"


SIMPLE_REPLACEMENTS = {
    " m ": " meters ",
    "CONUS": "Cone us",
    "~": " around ",
    "hydrologic": "hydro logic"
}


def break_down_sentences(text: str) -> typing.Sequence[typing.Tuple[PhraseType, str]]:
    sentences: typing.List[typing.Tuple[PhraseType, str]] = []

    text = ACRONYM_PATTERN.sub(lambda match: f'"{match.group()}" ' if match.group() not in string.punctuation else "", text.strip())

    for old_value, new_value in SIMPLE_REPLACEMENTS.items():
        text = text.replace(old_value, new_value)

    obvious_breaks = [
        line
        for line in re.split(r"\n{2:}", text)
        if line not in (None, '', '\t', os.linesep)
    ]

    for part in obvious_breaks:
        part_breaks: typing.List[typing.Union[str, typing.Tuple[PhraseType, str]]] = []

        while header_location := HEADER_PATTERN.match(part):
            beginning, ending = header_location.span()

            if beginning != 0:
                part_breaks.append(part[:beginning].strip())

            part_breaks.append((PhraseType.HEADER, part[beginning:ending].strip()))

            part = part[ending:].strip()

        if part:
            part_breaks.append(part)

        part_breaks = [
            content if isinstance(content, tuple) else content.replace(os.linesep, ' ')
            for content in part_breaks
        ]

        sentences.extend([
            (PhraseType.CONTENT, content) if isinstance(content, str) else content
            for content in part_breaks
        ])

    return sentences


def generate_sound(text: typing.Union[str, typing.Sequence[str]], model_configuration: NarratorConfiguration) -> typing.Union[bytes, typing.List[bytes]]:
    """
    Turn the given text into binary audio data

    :param text: The text to convert to speech
    :param model_configuration: Details on HOW it should be turned into speech
    :return: A bytes object encoded as audio/wav
    """
    model = model_configuration.get_model()

    arguments: typing.Dict[str, typing.Any] = model_configuration.get_arguments()

    if isinstance(text, str):
        text_parts = break_down_sentences(text)
    else:
        text_parts = text

    sounds: typing.List[bytes] = []

    _LOGGER.debug(f"Generating audio with {model_configuration}")

    for phrase_type, content in text_parts:
        audio_buffer = io.BytesIO()
        arguments['file_path'] = audio_buffer

        _LOGGER.debug('Generating %s audio for %s', phrase_type, content)
        model.tts_to_file(text=content, **arguments)
        audio_buffer.seek(0)
        sounds.append(audio_buffer.read())

    return sounds

