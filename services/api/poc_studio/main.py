import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from poc_studio.extra_routes import include_extra, on_startup
from poc_studio.graph.registry import NodeSpec
from poc_studio.guard import UnsafeRequestGuard
from poc_studio.preview import set_preview_manager
from poc_studio.preview.manager import PreviewManager
from poc_studio.routes import artifacts, events, gates, health, preview, publish, revise, runs
from poc_studio.runs.service import RunService

log = logging.getLogger(__name__)


def create_app(nodes: dict[str, NodeSpec] | None = None) -> FastAPI:
    """`nodes` overrides the registry (tests inject failing or blocking nodes)."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if os.environ.get("VIDEO_FAKE"):
            log.warning("VIDEO_FAKE is set: videos are placeholder clips (ignored when APP_ENV=production)")
        service = RunService(nodes)
        await service.start()  # opens the checkpoint DB and resumes runs left `running`
        app.state.run_service = service
        previews = PreviewManager()
        await previews.kill_orphans()  # preview servers left behind by a crashed API
        previews.start_reaper()
        app.state.preview = previews
        set_preview_manager(previews)
        log.info("retention removed %d input folders", on_startup())
        try:
            yield
        finally:
            set_preview_manager(None)
            await previews.stop_all()
            await service.stop()

    app = FastAPI(title="PoC Studio API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(UnsafeRequestGuard)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "testserver"])
    api = APIRouter(prefix="/api")
    for module in (health, runs, events, gates, artifacts, preview, publish, revise):
        api.include_router(module.router)
    app.include_router(api)
    include_extra(app)
    return app


app = create_app()
