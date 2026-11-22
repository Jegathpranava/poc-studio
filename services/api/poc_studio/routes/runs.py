from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from poc_studio.db.models import Project, Run
from poc_studio.db.session import get_session
from poc_studio.routes.schemas import RunSummary

router = APIRouter()


@router.get("/runs", response_model=list[RunSummary])
def list_runs(session: Session = Depends(get_session)) -> list[RunSummary]:
    rows = session.execute(
        select(Run, Project)
        .join(Project, Project.id == Run.project_id)
        .order_by(Run.started_at.desc(), Run.id)
    ).all()
    return [
        RunSummary.model_validate(
            {
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
        )
        for run, project in rows
    ]
