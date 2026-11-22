"""The Task 20 routers and the startup hook, kept out of `main.py` (owned by Task 19).

`include_extra(app)` adds the share, settings and templates routers under `/api`. `create_app` calls
it after the existing routers, and calls `on_startup` from the lifespan.
"""

import logging

from fastapi import APIRouter, FastAPI

from poc_studio import settings_store
from poc_studio.config import get_settings
from poc_studio.retention import apply_retention
from poc_studio.routes import settings as settings_routes
from poc_studio.routes import share, templates

log = logging.getLogger(__name__)


def include_extra(app: FastAPI) -> None:
    api = APIRouter(prefix="/api")
    for module in (share, settings_routes, templates):
        api.include_router(module.router)
    app.include_router(api)


def on_startup() -> int:
    """Apply the saved settings, then the retention policy. Returns the number of input folders deleted."""
    settings = settings_store.apply_overrides(get_settings())
    return apply_retention(settings)
