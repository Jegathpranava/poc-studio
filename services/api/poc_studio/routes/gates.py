from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from poc_studio.db.models import Project, Run
from poc_studio.db.session import get_session
from poc_studio.github.publish import PublishOptions, default_repo_name, latest_qa_report
from poc_studio.routes.runs import get_service
from poc_studio.routes.schemas import GateDecisionRequest, GateDecisionResponse, GateScope
from poc_studio.runs.edits import load_latest_requirements, validate_requirements_edits
from poc_studio.runs.service import GateError, RunService

router = APIRouter()

BLOCKED = "QA blocked the publish: a secret was found in the generated files. Fix it and run QA again."


def _publish_options(session: Session, run_id: str, body: GateDecisionRequest) -> dict[str, Any]:
    """Validated Gate 2 options, as stored with the approval. `repo_name` defaults from client and title."""
    asked = body.options
    name = asked.repo_name if asked else None
    if name is None:
        row = session.execute(
            select(Project.client_name, Run.title)
            .join(Run, Run.project_id == Project.id)
            .where(Run.id == run_id)
        ).first()
        if row is None:
            raise HTTPException(404, f"run {run_id} not found")
        name = default_repo_name(row[0], row[1])
    fields = asked.model_dump(exclude={"repo_name"}) if asked else {}
    return PublishOptions(repo_name=name, **fields).model_dump()


@router.post("/runs/{run_id}/gates/{gate}", response_model=GateDecisionResponse)
async def decide_gate(
    run_id: str,
    gate: GateScope,
    body: GateDecisionRequest,
    service: RunService = Depends(get_service),
    session: Session = Depends(get_session),
) -> GateDecisionResponse:
    edits = body.edits
    if gate == "scope" and body.decision == "approve" and edits:
        edits = validate_requirements_edits(edits, load_latest_requirements(run_id)).model_dump(
            mode="json"
        )  # 422 with field errors
    if gate == "publish" and body.decision == "approve":
        report = latest_qa_report(run_id)
        if report and report.get("block_publish"):
            raise HTTPException(409, BLOCKED)
        edits = _publish_options(session, run_id, body)  # stored in the approval; the repo node reads it
    try:
        status = await service.decide(run_id, gate, body.decision, edits, body.note)
    except GateError as exc:
        codes = {"not_found": 404, "save_failed": 500}
        raise HTTPException(codes.get(exc.code, 409), str(exc)) from exc
    return GateDecisionResponse.model_validate(
        {"run_id": run_id, "gate": gate, "decision": body.decision, "status": status}
    )
