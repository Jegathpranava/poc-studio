"""Client sharing. Nothing is hosted (amendment 11): the owner sends the zip, and the token page below is the
owner's local preview of exactly what the client sees. It is served on 127.0.0.1 only.

- POST /api/runs/{id}/share-export, GET /api/runs/{id}/share-export/download: the share zip.
- POST /api/share/{run_id}: a share token (24 random bytes, stored hashed, valid 30 days).
- GET /api/share/t/{token}[/video|/deck.html]: the read-only view behind a valid token; 404 otherwise.
"""

import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from poc_studio.db.models import Run
from poc_studio.db.session import get_session
from poc_studio.routes.artifacts import DECK_CSP, _latest_file  # pyright: ignore[reportPrivateUsage]
from poc_studio.share import tokens
from poc_studio.share.content import latest_path, load_content
from poc_studio.share.export import ShareBlocked, ShareUnavailable, build_share_zip, latest_zip, share_dir

router = APIRouter()
NOT_VALID = "This link has expired or is not valid"


class ShareExportOut(BaseModel):
    run_id: str
    download_url: str
    share_token: str
    expires_at: datetime
    warnings: list[str] = []


class ShareTokenOut(BaseModel):
    token: str
    path: str  # the page path on the web app, `/share/<token>`
    expires_at: datetime


class SharePageOut(BaseModel):
    title: str
    client: str
    summary: str
    pain_points: list[str]
    pilot: str | None
    expires_at: datetime
    video_url: str | None
    deck_url: str | None


def _shareable_run(session: Session, run_id: str) -> Run:
    """Delivered runs, or a run waiting at Gate 2 that already has a deck. 409 otherwise."""
    run = session.get(Run, run_id)
    if run is None:
        raise HTTPException(404, f"run {run_id} not found")
    ok = run.status == "delivered" or (run.status == "waiting_gate2" and latest_path(run_id, "deck", ".html"))
    if not ok:
        raise HTTPException(409, "Sharing opens once the run is delivered, or at Gate 2 with a deck")
    return run


def _manifest_warnings(run_id: str) -> list[str]:
    try:
        data = json.loads((share_dir(run_id) / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return [str(w) for w in data.get("warnings", [])]


@router.post("/runs/{run_id}/share-export", response_model=ShareExportOut)
def export_share(run_id: str, session: Session = Depends(get_session)) -> ShareExportOut:
    _shareable_run(session, run_id)
    try:
        build_share_zip(run_id)
    except ShareBlocked as exc:
        raise HTTPException(422, str(exc)) from exc
    except (ShareUnavailable, LookupError) as exc:
        raise HTTPException(409, str(exc)) from exc
    token, expires = tokens.create_token(session, run_id)
    return ShareExportOut(
        run_id=run_id,
        download_url=f"/api/runs/{run_id}/share-export/download",
        share_token=token,
        expires_at=expires,
        warnings=_manifest_warnings(run_id),
    )


@router.get("/runs/{run_id}/share-export/download")
def download_share_zip(run_id: str, session: Session = Depends(get_session)) -> FileResponse:
    if session.get(Run, run_id) is None:
        raise HTTPException(404, f"run {run_id} not found")
    path = latest_zip(run_id)
    if path is None:
        raise HTTPException(404, "No share zip yet. Export it first.")
    return FileResponse(path, media_type="application/zip", filename=path.name)


@router.post("/share/{run_id}", response_model=ShareTokenOut)
def create_share_token(run_id: str, session: Session = Depends(get_session)) -> ShareTokenOut:
    _shareable_run(session, run_id)
    token, expires = tokens.create_token(session, run_id)
    return ShareTokenOut(token=token, path=f"/share/{token}", expires_at=expires)


def _valid(session: Session, token: str) -> str:
    row = tokens.resolve_token(session, token)
    if row is None:
        raise HTTPException(404, NOT_VALID)
    return row.run_id


@router.get("/share/t/{token}", response_model=SharePageOut)
def get_share_page(token: str, session: Session = Depends(get_session)) -> SharePageOut:
    row = tokens.resolve_token(session, token)
    if row is None:
        raise HTTPException(404, NOT_VALID)
    try:
        content = load_content(row.run_id)
    except LookupError as exc:
        raise HTTPException(404, NOT_VALID) from exc
    base = f"/api/share/t/{token}"
    return SharePageOut(
        title=content.title,
        client=content.client,
        summary=content.summary,
        pain_points=content.pain_points,
        pilot=content.pilot,
        expires_at=row.expires_at,
        video_url=f"{base}/video" if content.has_video else None,
        deck_url=f"{base}/deck.html" if content.has_deck else None,
    )


@router.get("/share/t/{token}/video")
def get_share_video(token: str, session: Session = Depends(get_session)) -> FileResponse:
    run_id = _valid(session, token)
    path, _ = _latest_file(session, run_id, "video", ".mp4", "video")
    return FileResponse(path, media_type="video/mp4", filename=path.name, content_disposition_type="inline")


@router.get("/share/t/{token}/deck.html")
def get_share_deck(token: str, session: Session = Depends(get_session)) -> Response:
    run_id = _valid(session, token)
    path, _ = _latest_file(session, run_id, "deck", ".html", "deck")
    headers = {"Content-Security-Policy": DECK_CSP, "X-Content-Type-Options": "nosniff"}
    return Response(path.read_bytes(), media_type="text/html; charset=utf-8", headers=headers)
