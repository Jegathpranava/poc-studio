"""Gate 1 edits: the owner's corrected brief is validated and saved as a new `requirements` version."""

from typing import Any

from fastapi import HTTPException
from pydantic import ValidationError

from poc_studio.agents.intelligence import next_requirements_version, persist_requirements
from poc_studio.schemas.requirements import Requirements


def validate_requirements_edits(edits: dict[str, object]) -> Requirements:
    """Parse the edited brief, or raise a 422 whose detail lists the field errors."""
    try:
        return Requirements.model_validate(edits)
    except ValidationError as exc:
        detail: list[dict[str, Any]] = [
            {"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]}
            for e in exc.errors(include_url=False, include_context=False, include_input=False)
        ]
        raise HTTPException(422, detail) from exc


def save_requirements_edit(run_id: str, req: Requirements) -> int:
    """Write the edited brief as the next `requirements.vN.json`. Returns N."""
    version = next_requirements_version(run_id)
    persist_requirements(run_id, version, req)
    return version
