"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import pathlib

from aiohttp import web

from easy_narrator.application_details import STATIC_DIRECTORY
from easy_narrator.messages.responses import ErrorResponse
from easy_narrator.utilities.common import local_only
from easy_narrator.utilities.common import get_html_response

MARKUP_DIRECTORY = STATIC_DIRECTORY / "markup"

INDEX_PATH = MARKUP_DIRECTORY / "index.html"
SAMPLE_GALLERY_PATH = MARKUP_DIRECTORY / "sample_gallery.html"


@local_only
async def handle_index(request: web.Request) -> web.Response:
    return get_html_response(INDEX_PATH)


@local_only
async def view_sample_gallery(request: web.Request) -> web.Response:
    return get_html_response(SAMPLE_GALLERY_PATH)
