#!/usr/bin/env python3
"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing
import json

from easy_narrator.application_details import RESOURCE_PATH
from easy_narrator.application_details import MODEL_CATALOG_PATH

from easy_narrator.application_logging import get_logger

_LOGGER = get_logger()


SAMPLE_TEXT = """Hello, this is a sample for the {} voice for the {} model using the {} dataset.
I hope you like it and find it helpful."""


def get_model_catalog() -> typing.Dict[str, typing.Dict[str, typing.Any]]:
    if MODEL_CATALOG_PATH.exists():
        with MODEL_CATALOG_PATH.open() as model_catalog:
            return json.load(model_catalog)
    else:
        from easy_narrator.utilities.model_cache import ModelCache

        return {
            model.fullname: model.dict()
            for model in ModelCache.get_available_models()
        }


def generate_samples():
    sample_path = RESOURCE_PATH / "samples"
    sample_path.mkdir(parents=True, exist_ok=True)

    model_catalog = get_model_catalog()

    sample_count = sum(
        len(data['speakers']) or 1
        for data in model_catalog.values()
    )

    counted_samples = 0

    failed_writes = 0
    preexisting_samples = 0
    written_samples = 0

    from easy_narrator.utilities.model_cache import ModelCache

    for model_name, model_details in model_catalog.items():
        model_type, language, dataset, model = model_name.split("/")
        safe_model_name = "_".join([model_type, language, dataset, model])
        model_directory = sample_path / safe_model_name
        model_directory.mkdir(parents=True, exist_ok=True)

        if model_details.get("is_multi_speaker", False):
            speakers_to_filenames = [
                (speaker, model_directory / f"{speaker}.wav")
                for speaker in model_details["speakers"]
            ]
        else:
            speakers_to_filenames = [
                (None, model_directory / f"{safe_model_name}.wav")
            ]

        model = ModelCache.get_model(model_name)

        for index, (speaker, filename) in enumerate(speakers_to_filenames, start=1):
            counted_samples += 1
            if filename.exists():
                preexisting_samples += 1
                continue

            text = SAMPLE_TEXT.format(speaker, model_name, dataset)

            _LOGGER.info(f"Writing a sample to {filename} ({counted_samples}/{sample_count})")
            try:
                model.tts_to_file(
                    text,
                    speaker=speaker,
                    language="en" if model_details["is_multi_lingual"] else None,
                    file_path=str(filename)
                )
                written_samples += 1
            except Exception as e:
                _LOGGER.error(f"Count not write a sample to {filename}: {e}")
                failed_writes += 1

    if preexisting_samples:
        _LOGGER.info(f"{preexisting_samples} samples were already written and didn't have to be replaced")

    if failed_writes:
        _LOGGER.info(f"Failed to write {failed_writes} samples")

    if written_samples:
        _LOGGER.info(f"{written_samples} samples were written")


if __name__ == "__main__":
    generate_samples()
