#!/usr/bin/env python3
"""
Looks for .wav files and compiles information about each into a dataframe/csv for later analysis
@author: christopher.tubbs
"""
import math
import typing
import asyncio
import multiprocessing

from argparse import ArgumentParser
from functools import lru_cache
from pathlib import Path

import numpy
import pandas

from scipy.io import wavfile
from scipy import ndimage

from easy_narrator.application_details import RESOURCE_PATH

SampleRate = int
SoundData = numpy.ndarray


PAUSE_THRESHOLD = 50


class Arguments:
    def __init__(self, *args):
        self.__root_directory: Path = RESOURCE_PATH / "samples"
        self.__output_path: Path = RESOURCE_PATH / "sample_analysis.csv"
        self.__write_recommended_speakers: bool = True

        self.__include_models: typing.List[str] = []
        self.__include_datasets: typing.List[str] = []

        self.__parse_command_line(*args)

    @property
    def root_directory(self) -> Path:
        return self.__root_directory

    @property
    def output_path(self) -> Path:
        return self.__output_path

    @property
    def write_recommended_speakers(self) -> bool:
        return self.__write_recommended_speakers

    @property
    def include_models(self) -> typing.List[str]:
        return self.__include_models

    @property
    def include_datasets(self) -> typing.List[str]:
        return self.__include_datasets

    def __parse_command_line(self, *args):
        parser = ArgumentParser("Create metadata about available audio samples")

        # Add Arguments
        parser.add_argument(
            "-d",
            metavar="path/to/sample/directory",
            type=Path,
            dest="root_directory",
            default=self.__root_directory,
            help="Where to start looking for audio files"
        )

        parser.add_argument(
            "-o",
            metavar="path/to/output.csv",
            dest="output_path",
            type=str,
            default=self.__output_path,
            help="Where the generated analysis should be written"
        )

        parser.add_argument(
            "--recommended",
            action="store_true",
            dest="write_recommended_speakers",
            help="Write details about speakers that are recommended for use"
        )

        parser.add_argument(
            "--include-models",
            metavar="model_name model_name",
            dest="include_models",
            default=[],
            nargs="*",
            help="Which models to consider"
        )

        parser.add_argument(
            "--include-datasets",
            metavar="dataset dataset",
            dest="include_datasets",
            default=[],
            nargs="*",
            help="Which datasets to consider"
        )

        # Parse the list of args if one is passed instead of args passed to the script
        if args:
            parameters = parser.parse_args(args)
        else:
            parameters = parser.parse_args()

        # Assign parsed parameters to member variables
        self.__root_directory = parameters.root_directory
        self.__output_path = parameters.output_path
        self.__write_recommended_speakers = parameters.write_recommended_speakers
        self.__include_models = parameters.include_models
        self.__include_datasets = parameters.include_datasets


def count_pauses(path: Path, sample_rate: SampleRate, sound_data: SoundData) -> float:
    normalized_sound_data = numpy.array([
        0 if value > PAUSE_THRESHOLD or value < PAUSE_THRESHOLD * -1 else 1
        for value in sound_data
    ])
    label, number_of_features = ndimage.label(normalized_sound_data)
    pauses = [
        part
        for part in "".join(str(value) for value in label).split("0")
        if part
           and len(part) > sample_rate / 2
    ]
    return len(pauses)


@lru_cache
def get_sound_metadata(path: Path) -> typing.Dict[typing.Literal['speaker', 'model', 'dataset', 'language'], str]:
    if not path.exists():
        raise FileNotFoundError(f"There are no files at {path}")

    if not path.is_file() or not path.suffix.lower() == ".wav":
        raise ValueError(f"The path '{path}' does not point at a .wav file")

    metadata_part = None

    for part in path.parts:
        if part.startswith('tts_models_'):
            metadata_part = part.strip().replace("tts_models_", "")
            break

    if metadata_part is None:
        raise ValueError(f"The path at '{path}' does not contain sound metadata")

    raw_parts = [
        part
        for part in metadata_part.split('_')
        if part
    ]

    return {
        'speaker': path.stem,
        'model': "".join(raw_parts[2:]),
        'dataset': raw_parts[1],
        'language': raw_parts[0]
    }


def get_speaker(path: Path, *args, **kwargs) -> str:
    return get_sound_metadata(path).get("speaker").strip()


def get_dataset(path: Path, *args, **kwargs) -> str:
    return get_sound_metadata(path).get("dataset")


def get_model(path: Path, *args, **kwargs) -> str:
    return get_sound_metadata(path).get("model")


def get_language(path: Path, *args, **kwargs) -> str:
    return get_sound_metadata(path).get("language")


def get_amplitude_range(path: Path, sample_rate: SampleRate, sound_data: SoundData) -> float:
    maximum_amplitude = sound_data.max()
    minimum_amplitude = sound_data.min()
    return int(maximum_amplitude) + int(abs(minimum_amplitude))


def get_value_transformations() -> typing.Dict[str, typing.Callable[[Path, SampleRate, SoundData], typing.Any]]:
    return {
        "speaker": get_speaker,
        "dataset": get_dataset,
        "model": get_model,
        "path": lambda path, sample_rate, sound_data: str(Path(path).relative_to(RESOURCE_PATH)),
        "duration": lambda path, sample_rate, sound_data: sound_data.shape[0] / float(sample_rate),
        "pauses": count_pauses,
        "minimum_amplitude": lambda path, sample_rate, sound_data: sound_data.min(),
        "maximum_amplitude": lambda path, sample_rate, sound_data: sound_data.max(),
        "amplitude_range": get_amplitude_range,
        "amplitude_std": lambda path, sample_rate, sound_data: sound_data.std(),
    }


def get_audio_characteristics(path: Path) -> typing.Dict[str, typing.Any]:
    print(f"Getting audio characteristics from {path}")
    sample_rate, sound_data = wavfile.read(str(path))
    return {
        column_name: function(path, sample_rate, sound_data)
        for column_name, function in get_value_transformations().items()
    }


def find_wav_files(root_dir: Path = None) -> typing.List[Path]:
    if root_dir is None:
        root_dir = Path.cwd()

    if not root_dir.exists():
        raise NotADirectoryError(f"The path at '{root_dir}' does not exist")

    if root_dir.is_file():
        if root_dir.suffix == ".wav":
            return [root_dir]
        return []

    wav_files: typing.List[Path] = []

    for current_directory, child_directory_names, filenames in root_dir.walk():
        for filename in filenames:
            if filename.endswith(".wav"):
                wav_files.append(current_directory / filename)

    return wav_files


def get_sample_characteristics(root_directory: Path = None) -> pandas.DataFrame:
    wave_file_paths = find_wav_files(root_directory)
    with multiprocessing.Pool() as pool:
        results = pool.map(get_audio_characteristics, wave_file_paths)

    return pandas.DataFrame(results)


def write_recommended_speakers(output_path: Path, characteristics: pandas.DataFrame):
    average_pauses = math.floor(characteristics.pauses.mean())

    average_duration = characteristics.duration.mean()
    duration_std = characteristics.duration.std()

    recommendations = characteristics[characteristics.duration > average_duration - duration_std]
    recommendations = recommendations[recommendations.duration < average_duration + duration_std]

    recommendations = recommendations[recommendations.pauses >= average_pauses]

    sorted_recommendations = recommendations.sort_values(by=['amplitude_std', 'duration'], axis=0, ascending=[False, True])
    sorted_recommendations = sorted_recommendations[['speaker', 'model', 'dataset', 'duration', 'pauses', 'amplitude_std']]
    recommendation_path = output_path.parent / f"{output_path.stem}_recommendations.csv"

    print(f"Writing recommended narrators to {recommendation_path}")
    sorted_recommendations.to_csv(recommendation_path, index=False)


async def main():
    """
    Define your main function here
    """
    arguments = Arguments()

    sample_characteristics = get_sample_characteristics(arguments.root_directory)

    if arguments.include_models:
        print(f"Only including the models: {arguments.include_models}")
        sample_characteristics = sample_characteristics[sample_characteristics.model.isin(arguments.include_models)]

    if arguments.include_datasets:
        sample_characteristics = sample_characteristics[sample_characteristics.dataset.isin(arguments.include_datasets)]

    print(sample_characteristics.head())

    print(f"Writing output to {arguments.output_path}")
    sample_characteristics.to_csv(arguments.output_path, index=False)

    if arguments.write_recommended_speakers:
        write_recommended_speakers(arguments.output_path, sample_characteristics)

if __name__ == "__main__":
    asyncio.run(main())
