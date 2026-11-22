"""GET /api/runs/{id}/artifacts/{type}: the latest version of a JSON artifact.

`/markdown` downloads its rendered `.md` sibling. Other downloads join this file in Task 13.
"""

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
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
