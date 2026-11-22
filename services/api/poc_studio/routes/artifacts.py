"""GET /api/runs/{id}/artifacts/{type}: the latest version of a JSON artifact.

`/markdown` downloads its rendered `.md` sibling. `/files` lists the prototype app's file tree and `/build`
returns its `build.json`. `/video` streams the walkthrough MP4 (HTTP Range), `/video/chapters` its chapters,
`/deck.html` the self-contained deck with a locking CSP (it is iframed), `/deck.pptx` and `/docs/{name}` the
other exports.
"""

import json
import os
from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from poc_studio.config import get_settings
from poc_studio.db.models import Artifact, Run
from poc_studio.db.session import get_session
from poc_studio.routes.schemas import ArtifactJson, ArtifactType

router = APIRouter()


@router.get("/runs/{run_id}/artifacts/{artifact_type}", response_model=ArtifactJson)
def get_json_artifact(
    run_id: str, artifact_type: ArtifactType, session: Session = Depends(get_session)
) -> ArtifactJson:
    if session.get(Run, run_id) is None:
        raise HTTPException(404, f"run {run_id} not found")
    row = session.scalars(
        select(Artifact)
        .where(Artifact.run_id == run_id, Artifact.type == artifact_type, Artifact.path.like("%.json"))
        .order_by(Artifact.version.desc())
    ).first()
    if row is None:
        raise HTTPException(404, f"run {run_id} has no {artifact_type} artifact yet")
    path = get_settings().runs_dir / row.path
    if path.suffix != ".json":
        raise HTTPException(415, f"{artifact_type} is not a JSON artifact")
    if not path.is_file():
        raise HTTPException(404, f"{artifact_type} v{row.version} is missing on disk")
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return ArtifactJson(type=artifact_type, version=row.version, data=data)


@router.get("/runs/{run_id}/artifacts/{artifact_type}/markdown")
def download_markdown_artifact(
    run_id: str, artifact_type: ArtifactType, session: Session = Depends(get_session)
) -> FileResponse:
    """Latest `.md` of an artifact type. The type is from the allow-list; the path comes from the DB row."""
    row = session.scalars(
        select(Artifact)
        .where(Artifact.run_id == run_id, Artifact.type == artifact_type, Artifact.path.like("%.md"))
        .order_by(Artifact.version.desc())
    ).first()
    if row is None:
        raise HTTPException(404, f"run {run_id} has no markdown {artifact_type} artifact")
    root = get_settings().runs_dir.resolve()
    path = (root / row.path).resolve()
    if not path.is_relative_to(root / run_id) or not path.is_file():
        raise HTTPException(404, f"{artifact_type} markdown is missing on disk")
    return FileResponse(path, media_type="text/markdown", filename=f"{artifact_type}.v{row.version}.md")


TREE_SKIP = {"node_modules", ".next"}
TREE_MAX_DEPTH = 6
TREE_MAX_ENTRIES = 3000


class FileNode(BaseModel):
    name: str
    path: str
    type: Literal["file", "dir"]
    children: list["FileNode"] | None = None


def _walk(root: Path, rel: str, depth: int, budget: list[int]) -> list[FileNode]:
    """Entries of `root/rel`, dirs first. No dotfiles, no node_modules or .next, no symlinks."""
    here = root / rel if rel else root
    nodes: list[FileNode] = []
    with os.scandir(here) as it:
        entries = sorted(it, key=lambda e: (not e.is_dir(follow_symlinks=False), e.name.lower()))
    for entry in entries:
        if entry.name.startswith(".") or entry.name in TREE_SKIP or entry.is_symlink() or budget[0] <= 0:
            continue
        budget[0] -= 1
        path = f"{rel}/{entry.name}" if rel else entry.name
        if entry.is_dir(follow_symlinks=False):
            kids = _walk(root, path, depth + 1, budget) if depth < TREE_MAX_DEPTH else []
            nodes.append(FileNode(name=entry.name, path=path, type="dir", children=kids))
        else:
            nodes.append(FileNode(name=entry.name, path=path, type="file"))
    return nodes


@router.get("/runs/{run_id}/files", response_model=list[FileNode])
def get_file_tree(run_id: str, session: Session = Depends(get_session)) -> list[FileNode]:
    """The prototype app's file tree. There is no path input: the root is always `runs/<id>/app`."""
    if session.get(Run, run_id) is None:
        raise HTTPException(404, f"run {run_id} not found")
    app_dir = get_settings().runs_dir / run_id / "app"
    if not app_dir.is_dir():
        raise HTTPException(404, "Prototype not built")
    return _walk(app_dir, "", 1, [TREE_MAX_ENTRIES])


def read_build(run_id: str) -> dict[str, Any] | None:
    path = get_settings().runs_dir / run_id / "build.json"
    if not path.is_file():
        return None
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


@router.get("/runs/{run_id}/build")
def get_build(run_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """`build.json`: ok, duration_s, attempts, error, log_tail."""
    if session.get(Run, run_id) is None:
        raise HTTPException(404, f"run {run_id} not found")
    info = read_build(run_id)
    if info is None:
        raise HTTPException(404, "Prototype not built")
    return info


DECK_CSP = (
    "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; font-src data:"
)
DocName = Literal["exec-summary", "user-flows"]


def _latest_file(
    session: Session, run_id: str, kind: str, suffix: str, what: str, name: str = ""
) -> tuple[Path, int]:
    """Latest artifact row of `kind` whose path ends with `suffix` (and `name`, if given), as a file under
    the run's folder. The path comes from the DB row, never from the request."""
    if session.get(Run, run_id) is None:
        raise HTTPException(404, f"run {run_id} not found")
    row = session.scalars(
        select(Artifact)
        .where(Artifact.run_id == run_id, Artifact.type == kind, Artifact.path.like(f"%{name}%{suffix}"))
        .order_by(Artifact.version.desc())
    ).first()
    if row is None:
        raise HTTPException(404, f"run {run_id} has no {what} yet")
    root = get_settings().runs_dir.resolve()
    path = (root / row.path).resolve()
    if not path.is_relative_to(root / run_id) or not path.is_file():
        raise HTTPException(404, f"the {what} is missing on disk")
    return path, row.version


@router.get("/runs/{run_id}/video")
def get_video(run_id: str, session: Session = Depends(get_session)) -> FileResponse:
    """The latest walkthrough MP4. FileResponse answers Range requests with 206 and Accept-Ranges."""
    path, _ = _latest_file(session, run_id, "video", ".mp4", "video")
    return FileResponse(path, media_type="video/mp4", filename=path.name, content_disposition_type="inline")


@router.get("/runs/{run_id}/video/chapters")
def get_video_chapters(run_id: str, session: Session = Depends(get_session)) -> list[dict[str, Any]]:
    path, _ = _latest_file(session, run_id, "video", ".chapters.json", "video chapters")
    chapters: list[dict[str, Any]] = json.loads(path.read_text(encoding="utf-8"))
    return chapters


@router.get("/runs/{run_id}/deck.html")
def get_deck_html(run_id: str, download: bool = False, session: Session = Depends(get_session)) -> Response:
    """The latest assembled deck. The CSP allows only inline styles and scripts and data: images, so the page
    can make no network request and is safe to iframe."""
    path, _ = _latest_file(session, run_id, "deck", ".html", "deck")
    headers = {"Content-Security-Policy": DECK_CSP, "X-Content-Type-Options": "nosniff"}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="{path.name}"'
    return Response(path.read_bytes(), media_type="text/html; charset=utf-8", headers=headers)


@router.get("/runs/{run_id}/deck.pptx")
def get_deck_pptx(run_id: str, session: Session = Depends(get_session)) -> FileResponse:
    path, _ = _latest_file(session, run_id, "pptx", ".pptx", "pptx")
    media = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    return FileResponse(path, media_type=media, filename=path.name)


@router.get("/runs/{run_id}/docs/{name}")
def get_doc(run_id: str, name: DocName, session: Session = Depends(get_session)) -> FileResponse:
    path, _ = _latest_file(session, run_id, "docs", ".md", name, name)
    return FileResponse(path, media_type="text/markdown", filename=path.name)
