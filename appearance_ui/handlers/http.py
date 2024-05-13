"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import pathlib

from aiohttp import web

from ..utilities.common import local_only
from ..utilities.common import get_html_response

INDEX_PATH = (pathlib.Path(__file__).parent.parent / "static" / "markup" / "index.html").resolve()


@local_only
async def handle_index(request: web.Request) -> web.Response:
    return get_html_response(INDEX_PATH)
