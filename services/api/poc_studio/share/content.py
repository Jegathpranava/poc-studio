"""What the client sees: read from the run's latest requirements and architecture artifacts."""

from pathlib import Path

from pydantic import BaseModel
from sqlalchemy import select

from poc_studio.agents.store import latest_json
from poc_studio.config import get_settings
from poc_studio.db.models import Artifact, Project, Run
from poc_studio.db.session import open_session
from poc_studio.graph.state import RunState
from poc_studio.schemas.architecture import Architecture
from poc_studio.schemas.requirements import Requirements

MAX_POINTS = 6


class ShareContent(BaseModel):
    title: str
    client: str
    summary: str
    pain_points: list[str]
    pilot: str | None
    stakeholders: list[str]
    has_video: bool
    has_deck: bool


def pilot_line(arch: Architecture | None) -> str | None:
    """ "Pilot: 4 weeks, about $186 a month to run." from the phases and the monthly cost."""
    if arch is None:
        return None
    weeks = sum(p.weeks for p in arch.phases)
    cost = f"about ${arch.monthly_cost.total_usd:,.0f} a month to run"
    return f"Pilot: {weeks:g} weeks, {cost}." if weeks else f"Pilot: {cost}."


def latest_path(run_id: str, kind: str, suffix: str) -> Path | None:
    """The latest artifact file of `kind` ending in `suffix`, if it is on disk. Paths come from the DB."""
    with open_session() as session:
        row = session.scalars(
            select(Artifact)
            .where(Artifact.run_id == run_id, Artifact.type == kind, Artifact.path.like(f"%{suffix}"))
            .order_by(Artifact.version.desc())
        ).first()
    path = get_settings().runs_dir / row.path if row else None
    return path if path is not None and path.is_file() else None


def load_content(run_id: str) -> ShareContent:
    state: RunState = {"run_id": run_id}
    req = latest_json(state, "requirements", Requirements)
    if req is None:
        raise LookupError(f"run {run_id} has no requirements")
    arch = latest_json(state, "architecture", Architecture)
    with open_session() as session:
        run = session.get(Run, run_id)
        project = session.get(Project, run.project_id) if run else None
        client = project.client_name if project else req.client
    return ShareContent(
        title=req.title,
        client=client,
        summary=req.summary,
        pain_points=req.pain_points[:MAX_POINTS],
        pilot=pilot_line(arch),
        stakeholders=[s.name for s in req.stakeholders],
        has_video=latest_path(run_id, "video", ".mp4") is not None,
        has_deck=latest_path(run_id, "deck", ".html") is not None,
    )
