from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from poc_studio.graph.registry import NodeSpec
from poc_studio.preview.manager import PreviewManager
from poc_studio.routes import artifacts, events, gates, health, preview, runs
from poc_studio.runs.service import RunService


def create_app(nodes: dict[str, NodeSpec] | None = None) -> FastAPI:
    """`nodes` overrides the registry (tests inject failing or blocking nodes)."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        service = RunService(nodes)
        await service.start()  # opens the checkpoint DB and resumes runs left `running`
        app.state.run_service = service
        previews = PreviewManager()
        await previews.kill_orphans()  # preview servers left behind by a crashed API
        previews.start_reaper()
        app.state.preview = previews
        try:
            yield
        finally:
            await previews.stop_all()
            await service.stop()

    app = FastAPI(title="PoC Studio API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    api = APIRouter(prefix="/api")
    for module in (health, runs, events, gates, artifacts, preview):
        api.include_router(module.router)
    app.include_router(api)
    return app


app = create_app()
