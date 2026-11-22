from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from poc_studio.db.models import AgentStep, Artifact, Project, Run
from poc_studio.db.session import get_session
from poc_studio.ingest.parse import MAX_FILE_BYTES
from poc_studio.routes.schemas import (
    AgentStepOut,
    ArtifactOut,
    CreateRunResponse,
    RunDetail,
    RunSummary,
)
from poc_studio.runs import service as run_limits
from poc_studio.runs.service import InvalidUpload, RunOptions, RunService

router = APIRouter()


def get_service(request: Request) -> RunService:
    return request.app.state.run_service


def _summary_fields(run: Run, project: Project) -> dict[str, object]:
    return {
        "id": run.id,
        "title": run.title,
        "client_name": project.client_name,
        "sector": project.sector,
        "status": run.status,
        "current_step": run.current_step,
        "paid_usd": run.paid_usd,
        "budget_usd": run.budget_usd,
        "started_at": run.started_at,
        "finished_at": run.finished_at,
    }


@router.get("/runs", response_model=list[RunSummary])
def list_runs(session: Session = Depends(get_session)) -> list[RunSummary]:
    rows = session.execute(
        select(Run, Project)
        .join(Project, Project.id == Run.project_id)
        .order_by(Run.started_at.desc(), Run.id)
    ).all()
    return [RunSummary.model_validate(_summary_fields(run, project)) for run, project in rows]


@router.get("/runs/{run_id}", response_model=RunDetail)
def get_run(run_id: str, session: Session = Depends(get_session)) -> RunDetail:
    row = session.execute(
        select(Run, Project).join(Project, Project.id == Run.project_id).where(Run.id == run_id)
    ).first()
    if row is None:
        raise HTTPException(404, f"run {run_id} not found")
    run, project = row
    steps = session.scalars(select(AgentStep).where(AgentStep.run_id == run_id).order_by(AgentStep.id)).all()
    artifacts = session.scalars(select(Artifact).where(Artifact.run_id == run_id).order_by(Artifact.id)).all()
    return RunDetail.model_validate(
        {
            **_summary_fields(run, project),
            "tokens_total": run.tokens_total,
            "preview_port": run.preview_port,
            "steps": [AgentStepOut.model_validate(s) for s in steps],
            "artifacts": [ArtifactOut.model_validate(a) for a in artifacts],
        }
    )


def _total_message() -> str:
    return f"uploads exceed the total limit of {run_limits.MAX_TOTAL_BYTES / (1024 * 1024):g} MB"


@router.post("/runs", response_model=CreateRunResponse, status_code=201)
async def create_run(
    service: Annotated[RunService, Depends(get_service)],
    files: Annotated[list[UploadFile], File()],
    client: Annotated[str | None, Form()] = None,
    client_name: Annotated[str | None, Form()] = None,  # alias of `client`, as named in RunSummary
    sector: Annotated[str | None, Form()] = None,
    title: Annotated[str | None, Form()] = None,
    budget_usd: Annotated[float | None, Form(gt=0)] = None,
) -> CreateRunResponse:
    name = (client or client_name or "").strip()
    if not name:
        raise HTTPException(422, "client is required")
    if len(files) > run_limits.MAX_FILES:
        raise HTTPException(422, f"at most {run_limits.MAX_FILES} files per run")
    uploads: list[tuple[str, bytes]] = []
    total = 0
    for f in files:
        data = await f.read(MAX_FILE_BYTES + 1)  # one byte over the limit is enough to reject it
        total += len(data)
        if total > run_limits.MAX_TOTAL_BYTES:  # stop reading as soon as the sum is too big
            raise HTTPException(422, _total_message())
        uploads.append((f.filename or "upload", data))
    try:
        run_id = await service.create_run(
            uploads, name, sector or None, RunOptions(title=title or None, budget_usd=budget_usd)
        )
    except InvalidUpload as exc:
        raise HTTPException(422, str(exc)) from exc
    return CreateRunResponse(id=run_id)
