"""Artifact helpers shared by the pitch and assemble nodes."""

import hashlib
import re
from pathlib import Path

from pydantic import BaseModel
from sqlalchemy import func, select

from poc_studio.config import get_settings
from poc_studio.db.models import Artifact
from poc_studio.db.session import open_session
from poc_studio.graph.state import RunState


def latest_json[T: BaseModel](state: RunState, kind: str, schema: type[T]) -> T | None:
    """Latest artifact of `kind` (its .json file); falls back to the run state."""
    with open_session() as session:
        row = session.scalars(
            select(Artifact)
            .where(Artifact.run_id == state["run_id"], Artifact.type == kind, Artifact.path.like("%.json"))
            .order_by(Artifact.version.desc())
        ).first()
        path = row.path if row else None
    if path is not None:
        file = get_settings().runs_dir / path
        if file.is_file():
            return schema.model_validate_json(file.read_text(encoding="utf-8"))
    in_state = state.get(kind)  # type: ignore[misc]
    return schema.model_validate(in_state) if in_state else None


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "deck"


def next_version(run_id: str, kind: str) -> int:
    with open_session() as session:
        top = session.scalar(
            select(func.max(Artifact.version)).where(Artifact.run_id == run_id, Artifact.type == kind)
        )
    return (top or 0) + 1


def record(run_id: str, kind: str, version: int, rel: str, data: bytes) -> Path:
    """Write runs/<run_id>/<rel> and add its artifact row."""
    target = get_settings().runs_dir / run_id / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    with open_session() as session:
        session.add(
            Artifact(
                run_id=run_id, type=kind, version=version, path=f"{run_id}/{rel}",
                sha256=hashlib.sha256(data).hexdigest(),
            )
        )  # fmt: skip
        session.commit()
    return target
