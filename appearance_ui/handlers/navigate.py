"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

from pathlib import Path

from aiohttp import web

from ..utilities.common import local_only


@local_only
async def navigate(request: web.Request) -> web.Response:
    paths = []

    term = request.query.get("term")

    if term:
        term_path = Path(term)

        if term_path.exists() and term_path.is_dir():
            paths.extend([
                str(child)
                for child in term_path.iterdir()
                if (child.is_dir() or str(child).endswith("nc"))
                   and not str(child.name).startswith(".")
            ])
        elif not term_path.exists():
            match_name = str(term_path)
            term_path = term_path.parent

            if term_path.exists():
                paths.extend([
                    str(child)
                    for child in term_path.iterdir()
                    if str(child).startswith(match_name)
                        and (child.is_dir() or str(child).endswith("nc"))
                ])

    return web.json_response(data=paths)
