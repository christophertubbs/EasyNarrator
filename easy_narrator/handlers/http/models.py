"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing
import json

from aiohttp import web

from easy_narrator.utilities.common import local_only
from easy_narrator.application_details import MODEL_CATALOG_PATH
from easy_narrator.messages.responses import ErrorResponse



@local_only
async def get_models(request: web.Request) -> web.Response:
    from easy_narrator.utilities.model_cache import ModelCache
    return web.json_response({
        "models": [
            model.fullname
            for model in ModelCache.get_available_models()
        ]
    })


@local_only
async def get_model_parameters(request: web.Request) -> web.Response:
    from easy_narrator.utilities.model_cache import ModelCache
    model_name = request.match_info.get("model_name")

    if model_name is None:
        response = ErrorResponse(
            message=f"A model name is required if a list of languages is requested",
            operation="get_langauges"
        )
        return web.json_response(
            response.dict(),
            status=400
        )

    if not ModelCache.is_available(model_name):
        response = ErrorResponse(
            message=f"The {model_name} model is not available for use",
            operation="get_langauges"
        )
        return web.json_response(
            response.dict(),
            status=404
        )

    model = ModelCache.get_model(model_name)

    return web.json_response({
        "languages": model.languages,
        "has_languages": model.is_multi_lingual,
        "speakers": model.speakers,
        "has_speakers": model.is_multi_speaker
    })


@local_only
async def get_parameters_for_all_models(request: web.Request) -> web.Response:
    if MODEL_CATALOG_PATH.exists():
        with MODEL_CATALOG_PATH.open() as model_cache_file:
            model_to_parameters = json.load(model_cache_file)
    else:
        from easy_narrator.utilities.model_cache import ModelCache
        model_to_parameters: typing.Dict[str, typing.Dict[str, typing.Any]] = {
            model.fullname: model.dict()
            for model in ModelCache.get_available_models()
        }

    return web.json_response(model_to_parameters)