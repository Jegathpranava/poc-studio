"""Preview endpoints. The prototype is NOT proxied: the UI iframes `http://127.0.0.1:<port>/` directly.

A reverse proxy would need a Next `basePath` (assets live under `/_next/`) baked in at port time, which breaks
the build cache and the starter. Direct URLs are simpler and need no rewriting. `POST /preview` starts (or
reuses) the server and returns `{url, port}`; calling it again counts as activity (it resets the 30-minute
idle clock). `GET|HEAD /preview/{path}` answers 307 to the direct URL so the spec's path still works.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from poc_studio.db.models import Run
from poc_studio.db.session import get_session
from poc_studio.preview.manager import HOST, PreviewError, PreviewManager
from poc_studio.routes.artifacts import read_build

router = APIRouter()


class PreviewInfo(BaseModel):
    url: str
    port: int


async def _ensure(request: Request, run_id: str, session: Session) -> int:
    if session.get(Run, run_id) is None:
        raise HTTPException(404, f"run {run_id} not found")
    info = read_build(run_id)
    if info is None or not info.get("ok"):
        raise HTTPException(409, "Prototype not built")
    manager: PreviewManager = request.app.state.preview
    try:
        return await manager.ensure(run_id)
    except PreviewError as exc:
        raise HTTPException(502, str(exc)) from exc


@router.post("/runs/{run_id}/preview", response_model=PreviewInfo)
async def start_preview(
    run_id: str, request: Request, session: Session = Depends(get_session)
) -> PreviewInfo:
    port = await _ensure(request, run_id, session)
    return PreviewInfo(url=f"http://{HOST}:{port}/", port=port)


@router.api_route("/runs/{run_id}/preview/{path:path}", methods=["GET", "HEAD"], include_in_schema=False)
async def redirect_preview(
    run_id: str, path: str, request: Request, session: Session = Depends(get_session)
) -> RedirectResponse:
    port = await _ensure(request, run_id, session)
    query = f"?{request.url.query}" if request.url.query else ""
    return RedirectResponse(f"http://{HOST}:{port}/{path.lstrip('/')}{query}", status_code=307)
