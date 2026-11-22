"""Gate 1 edits: the owner's corrected brief is validated here and saved as a new `requirements` version
by `RunService.decide`, in the same transaction that claims the gate."""

from typing import Any

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import select

from poc_studio.config import get_settings
from poc_studio.db.models import Artifact
from poc_studio.db.session import open_session
from poc_studio.schemas.requirements import Requirements


def load_latest_requirements(run_id: str) -> Requirements | None:
    with open_session() as session:
        path = session.scalar(
            select(Artifact.path)
            .where(Artifact.run_id == run_id, Artifact.type == "requirements")
            .order_by(Artifact.version.desc())
            .limit(1)
        )
    if path is None:
        return None
    file = get_settings().runs_dir / path
    return Requirements.model_validate_json(file.read_text(encoding="utf-8")) if file.is_file() else None


def validate_requirements_edits(edits: dict[str, object], latest: Requirements | None) -> Requirements:
    """Parse the edited brief, or raise a 422 whose detail lists the field errors.

    `client` and `sector` identify the project, so they must equal the latest saved brief: the owner picks
    the sector at New run, and changing it at Gate 1 is not supported in v1.
    """
    try:
        edited = Requirements.model_validate(edits)
    except ValidationError as exc:
        detail: list[dict[str, Any]] = [
            {"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]}
            for e in exc.errors(include_url=False, include_context=False, include_input=False)
        ]
        raise HTTPException(422, detail) from exc
    if latest is not None:
        problems = [
            {"loc": [field], "msg": f"{field} cannot be changed at Gate 1", "type": "value_error"}
            for field in ("client", "sector")
            if getattr(edited, field) != getattr(latest, field)
        ]
        if problems:
            raise HTTPException(422, problems)
    return edited
