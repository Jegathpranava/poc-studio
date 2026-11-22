"""GET /api/runs/{id}/artifacts/{type}: the latest version of a JSON artifact.

`/markdown` downloads its rendered `.md` sibling. `/files` lists the prototype app's file tree and `/build`
returns its `build.json`.
"""

import json
import os
from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
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
        .where(Artifact.run_id == run_id, Artifact.type == artifact_type)
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
