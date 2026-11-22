"""Request changes, retry and budget routes (spec 7, 7b).

Revisions are allowed only while the run waits at Gate 2 (the brief: at Gate 1). Each one is recorded as a
Gate "changes" decision, so it is audited like any other and survives a restart:
  - `revise`: edits = {"revise": <agent>, "note": ...}; the graph sends the run to that agent only.
  - `retry` on a run at Gate 2 whose port build failed: edits = {"revise": "port", "attempts": n}.
  - `retry` on a `failed` run: resume from the checkpoint.
  - `budget` on a `paused_budget` run: raise the limit and/or take the free model for the polish step.
"""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from poc_studio.db.models import Run
from poc_studio.db.session import get_session
from poc_studio.graph.revise import MAX_NOTE_CHARS
from poc_studio.routes.runs import get_service
from poc_studio.runs.service import GateError, RunService

router = APIRouter()

MAX_BUDGET_USD = 1.0  # a sanity cap for a raise
# artifact type in the URL -> the agent that owns it
OWNERS: dict[str, str] = {"architecture": "architect", "prototype": "screens", "deck": "pitch"}
ArtifactType = Literal["brief", "architecture", "prototype", "deck"]
Note = Annotated[str, Field(min_length=1, max_length=MAX_NOTE_CHARS)]


class ReviseRequest(BaseModel):
    note: Note


class RetryRequest(BaseModel):
    note: Annotated[str | None, Field(max_length=MAX_NOTE_CHARS)] = None
    attempts: Annotated[int, Field(ge=1, le=3)] = 3


class BudgetRequest(BaseModel):
    budget_usd: float | None = None
    use_free_model: bool = False


class ReviseResponse(BaseModel):
    run_id: str
    status: str
    agent: str | None = None  # the agent that reruns, when one is named


def _fail(exc: GateError) -> HTTPException:
    return HTTPException(404 if exc.code == "not_found" else 409, str(exc))


def _run(session: Session, run_id: str) -> Run:
    run = session.get(Run, run_id)
    if run is None:
        raise HTTPException(404, f"run {run_id} not found")
    return run


@router.post("/runs/{run_id}/artifacts/{artifact_type}/revise", response_model=ReviseResponse)
async def revise_artifact(
    run_id: str,
    artifact_type: ArtifactType,
    body: ReviseRequest,
    service: RunService = Depends(get_service),
) -> ReviseResponse:
    note = body.note.strip()
    if not note:
        raise HTTPException(422, "note must not be empty")
    try:
        if artifact_type == "brief":  # Gate 1 "changes": Meeting Intelligence extracts again
            status = await service.decide(run_id, "scope", "changes", None, note)
            return ReviseResponse(run_id=run_id, status=status, agent="intelligence")
        agent = OWNERS[artifact_type]
        status = await service.decide(run_id, "publish", "changes", {"revise": agent}, note)
    except GateError as exc:
        raise _fail(exc) from exc
    return ReviseResponse(run_id=run_id, status=status, agent=agent)


@router.post("/runs/{run_id}/retry", response_model=ReviseResponse)
async def retry_run(
    run_id: str,
    body: RetryRequest,
    service: RunService = Depends(get_service),
    session: Session = Depends(get_session),
) -> ReviseResponse:
    status = _run(session, run_id).status
    try:
        if status == "failed":
            await service.resume(run_id, allow_failed=True)
            return ReviseResponse(run_id=run_id, status="running")
        if status != "waiting_gate2" or not await _port_failed(service, run_id):
            raise HTTPException(409, f"run is {status}: only a failed run or a failed port build can retry")
        edits = {"revise": "port", "attempts": body.attempts}
        new_status = await service.decide(run_id, "publish", "changes", edits, (body.note or "").strip())
    except GateError as exc:
        raise _fail(exc) from exc
    return ReviseResponse(run_id=run_id, status=new_status, agent="port")


async def _port_failed(service: RunService, run_id: str) -> bool:
    snap = await service.graph.aget_state({"configurable": {"thread_id": run_id}})
    result = (snap.values or {}).get("build_result") or {}
    return result.get("ok") is False


@router.post("/runs/{run_id}/budget", response_model=ReviseResponse)
async def raise_budget(
    run_id: str,
    body: BudgetRequest,
    service: RunService = Depends(get_service),
    session: Session = Depends(get_session),
) -> ReviseResponse:
    run = _run(session, run_id)
    if run.status != "paused_budget":
        raise HTTPException(409, f"run is {run.status}, not paused on its budget")
    raised = body.budget_usd
    if raised is None and not body.use_free_model:
        raise HTTPException(422, "send budget_usd or use_free_model")
    if raised is not None and not run.paid_usd < raised <= MAX_BUDGET_USD:
        spent = f"${run.paid_usd:.2f}"
        raise HTTPException(
            422, f"budget_usd must be above the {spent} spent and at most ${MAX_BUDGET_USD:.2f}"
        )
    try:
        await service.resume(
            run_id, raised, state_update={"free_polish": True} if body.use_free_model else None
        )
    except GateError as exc:
        raise _fail(exc) from exc
    return ReviseResponse(run_id=run_id, status="running")
