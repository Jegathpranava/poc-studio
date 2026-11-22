from fastapi import APIRouter, Depends, HTTPException

from poc_studio.routes.runs import get_service
from poc_studio.routes.schemas import GateDecisionRequest, GateDecisionResponse, GateScope
from poc_studio.runs.edits import validate_requirements_edits
from poc_studio.runs.service import GateError, RunService

router = APIRouter()


@router.post("/runs/{run_id}/gates/{gate}", response_model=GateDecisionResponse)
async def decide_gate(
    run_id: str,
    gate: GateScope,
    body: GateDecisionRequest,
    service: RunService = Depends(get_service),
) -> GateDecisionResponse:
    edits = body.edits
    if gate == "scope" and body.decision == "approve" and edits:
        edits = validate_requirements_edits(edits).model_dump(mode="json")  # 422 with field errors
    try:
        status = await service.decide(run_id, gate, body.decision, edits, body.note)
    except GateError as exc:
        raise HTTPException(404 if exc.code == "not_found" else 409, str(exc)) from exc
    return GateDecisionResponse.model_validate(
        {"run_id": run_id, "gate": gate, "decision": body.decision, "status": status}
    )
