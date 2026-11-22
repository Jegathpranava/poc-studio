"""GET /api/runs/{id}/artifacts/{type}: the latest version of a JSON artifact.

Downloads join this file in Task 13.
"""

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
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
