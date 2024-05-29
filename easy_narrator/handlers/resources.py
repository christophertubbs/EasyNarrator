"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import json
import typing
import pathlib
from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field

from aiohttp import web

from ..application_details import MODEL_CATALOG_PATH
from ..messages.responses import ErrorResponse
from ..utilities.common import local_only
from ..utilities import mimetypes

from easy_narrator.application_details import STATIC_DIRECTORY
from easy_narrator.application_details import RESOURCE_PATH

from ..application_logging import get_logger

_LOGGER = get_logger()

SCRIPT_DIRECTORY = STATIC_DIRECTORY / "scripts"
STYLE_DIRECTORY = STATIC_DIRECTORY / "style"
IMAGE_DIRECTORY = STATIC_DIRECTORY / "images"
SAMPLE_ROOT_DIRECTORY = RESOURCE_PATH / "samples"
FAVICON_PATH = IMAGE_DIRECTORY / "favicon.ico"

RESOURCE_MAP = {
    "scripts": SCRIPT_DIRECTORY,
    "script": SCRIPT_DIRECTORY,
    "style": STYLE_DIRECTORY,
    "styles": STYLE_DIRECTORY,
    "images": IMAGE_DIRECTORY,
    "image": IMAGE_DIRECTORY
}


@dataclass
class RouteInfo:
    path: str
    handler: typing.Callable[[web.Request], typing.Coroutine[typing.Any, typing.Any, web.Response]]
    name: typing.Optional[str]
    allow_get: typing.Optional[bool] = field(default=True)
    allow_post: typing.Optional[bool] = field(default=False)

    def is_local_only(self) -> bool:
        return getattr(self.handler, "local_only", False)

    def register(self, application: web.Application):
        if not self.is_local_only():
            raise Exception(
                f"Only local views may be registered - the view for {self.path} isn't local only. "
                f"Please decorate it with '@local_only'"
            )

        if self.allow_get:
            application.add_routes([web.get(self.path, self.handler)])

        if self.allow_post:
            application.add_routes([web.post(self.path, self.handler)])


def get_content_type(resource_type: str, filename: pathlib.Path) -> typing.Optional[str]:
    return mimetypes.get(filename.suffix)


def get_resource_directory(resource_type: str) -> pathlib.Path:
    return RESOURCE_MAP[resource_type]


@local_only
async def get_resource(request: web.Request) -> web.Response:
    resource_type: str = request.match_info['resource_type']

    if resource_type not in RESOURCE_MAP:
        return web.HTTPNotAcceptable(text=f"{resource_type} is not a valid type of resource")

    resource_name: str = request.match_info['name']
    resource_directory = get_resource_directory(resource_type)
    resource_path = resource_directory / resource_name

    if resource_path.exists():
        content_type = get_content_type(resource_type, resource_path)

        if content_type.startswith("image") or content_type.startswith("video"):
            return web.Response(
                body=resource_path.read_bytes(),
                content_type=content_type
            )
        else:
            return web.Response(
                text=resource_path.read_text(),
                content_type=content_type
            )

    return web.HTTPNotFound(text=f"No resource was found at '{resource_path}'")


@local_only
async def get_sample(request: web.Request) -> web.Response:
    if not MODEL_CATALOG_PATH.exists():
        message = (f"Cannot retrieve sample - no catalog of models has been generated. "
                   f"Generate a model catalog before attempting to listen to a sample.")
        _LOGGER.error(message)
        error_message = ErrorResponse(
            error_message=message,
            message_type="get_sample"
        )
        return web.json_response(error_message.model_dump(), status=404)

    if not SAMPLE_ROOT_DIRECTORY.exists():
        message = "Cannot retrieve list a sample - no samples have been generated"
        _LOGGER.error(message)
        error_message = ErrorResponse(
            error_message=message,
            message_type="get_sample"
        )
        return web.json_response(error_message.model_dump(), status=404)

    with MODEL_CATALOG_PATH.open() as catalog_file:
        model_catalog = json.load(catalog_file)

    contents = await request.json()
    model = contents.get('model')
    speaker = contents.get('speaker')
    language = contents.get('language')

    if model is None:
        message = f"Cannot retrieve a sample for the '{model}' model - a sample has not been generated for it"
        _LOGGER.error(message)
        error_message = ErrorResponse(
            error_message=message,
            message_type="get_sample"
        )
        return web.json_response(error_message.model_dump(), status=404)

    model_data = model_catalog[model]

    if model_data['is_multi_speaker'] and not speaker:
        message = f"Cannot retrieve a sample for the '{model}' model - no speaker was specified"
        _LOGGER.error(message)
        error_message = ErrorResponse(
            error_message=message,
            message_type="get_sample"
        )
        return web.json_response(error_message.model_dump(), status=404)

    model_sample_root = SAMPLE_ROOT_DIRECTORY / model.replace("/", "_")

    if not model_sample_root.exists():
        message = f"The directory for the '{model}' model samples could not be found"
        _LOGGER.error(message)
        error_message = ErrorResponse(
            error_message=message,
            message_type="get_sample"
        )
        return web.json_response(error_message.model_dump(), status=500)

    samples = [
        (sample_path, sample_path.stem)
        for sample_path in model_sample_root.iterdir()
        if sample_path.is_file()
            and sample_path.suffix.lower() == ".wav"
    ]

    if len(samples) == 0:
        message = f"Cannot retrieve sample - all samples for the '{model}' model are missing"
        _LOGGER.error(message)
        error_message = ErrorResponse(
            error_message=message,
            message_type="get_sample"
        )
        return web.json_response(error_message.model_dump(), status=500)

    if len(samples) == 1:
        sample_path = samples[0][0]
    else:
        matching_samples = [
            sample_path
            for sample_path, sample_speaker in samples
            if sample_speaker == speaker
        ]

        if not matching_samples:
            message = f"There are no samples for a speaker named '{speaker}' for the '{model}' model"
            _LOGGER.error(message)
            error_message = ErrorResponse(
                error_message=message,
                message_type="get_sample"
            )
            return web.json_response(error_message.model_dump(), status=404)

        sample_path = matching_samples[0]

    response = web.Response(
        body=sample_path.read_bytes(),
        content_type="audio/wave"
    )

    return response


@dataclass
class ModelSelectValues:
    value: str
    text: str
    languages: typing.Optional[typing.List[str]] = field(default=None)
    speakers: typing.Optional[typing.List[str]] = field(default=None)

    @property
    def dict(self) -> typing.Dict[str, typing.Union[str, typing.List[str]]]:
        return {
            "value": self.value,
            "text": self.text,
            "languages": self.languages,
            "speakers": self.speakers
        }


@dataclass
class DatasetSelectValues:
    value: str
    text: str
    models: typing.Optional[typing.List[ModelSelectValues]] = field(default_factory=list)

    @property
    def dict(self) -> typing.Dict[str, typing.Union[str, typing.Dict[str, typing.Union[str, typing.List[str]]]]]:
        return {
            "value": self.value,
            "text": self.text,
            "models": [
                model.dict
                for model in self.models
            ]
        }


@local_only
async def get_sample_list(request: web.Request) -> web.Response:
    if not MODEL_CATALOG_PATH.exists():
        message = ("Cannot retrieve list of samples - no catalog of models has been generated. "
                   "Generate a model catalog before attempting to listen to samples.")
        _LOGGER.error(message)
        error_message = ErrorResponse(
            error_message=message,
            message_type="get_sample_list"
        )
        return web.json_response(error_message.model_dump(), status=404)

    if not SAMPLE_ROOT_DIRECTORY.exists():
        message = "Cannot retrieve list of samples - no samples have been generated"
        _LOGGER.error(message)
        error_message = ErrorResponse(
            error_message=message,
            message_type="get_sample_list"
        )
        return web.json_response(error_message.model_dump(), status=400)

    samples = []

    with MODEL_CATALOG_PATH.open() as catalog_file:
        model_catalog = json.load(catalog_file)

    for model_name, model in model_catalog.items():
        dataset_value = model["dataset"]
        dataset_text = dataset_value.replace("_", " ")

        preexisting_candidates = [
            dataset_entry
            for dataset_entry in samples
            if dataset_entry.value == dataset_value
        ]

        if preexisting_candidates:
            dataset = preexisting_candidates[0]
        else:
            dataset = DatasetSelectValues(text=dataset_text, value=dataset_value)
            samples.append(dataset)

        model_info = ModelSelectValues(
            value=model_name,
            text=model["name"].replace("_", " "),
            speakers=model["speakers"] if model["is_multi_speaker"] else None
        )

        if model["is_multi_lingual"]:
            model_info.languages = model["languages"]

        dataset.models.append(model_info)

    return web.json_response(
        data={
            "samples": [data.dict for data in samples]
        }
    )


@local_only
async def get_favicon(request: web.Request) -> web.Response:
    return web.Response(
        body=FAVICON_PATH.read_bytes()
    )

RESOURCE_ROUTES = [
    RouteInfo(path="/static/{resource_type}/{name:.*}", handler=get_resource, name="get_resource"),
    RouteInfo(path="/sample", handler=get_sample, name="get_sample", allow_get=False, allow_post=True),
    RouteInfo(path="/sample/list", handler=get_sample_list, name="get_sample_list"),
    RouteInfo(path="/favicon.ico", handler=get_favicon, name="get_favicon"),
]


def register_resource_handlers(application: web.Application):
    for route in RESOURCE_ROUTES:
        if not route.is_local_only():
            raise Exception(
                f"Only local views may be registered - the view for {route.path} isn't local only. "
                f"Please decorate it with '@local_only'"
            )

        route.register(application=application)