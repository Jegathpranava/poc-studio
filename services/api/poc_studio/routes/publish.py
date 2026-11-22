"""GET /api/runs/{id}/publish: where the Gate 2 publish stands, and its result once delivered."""

import json
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from poc_studio.config import get_settings
from poc_studio.db.models import AgentStep, Approval, Artifact, Run
from poc_studio.db.session import get_session
from poc_studio.github.publish import PublishResult, latest_qa_report

router = APIRouter()


class PublishStatus(BaseModel):
    status: Literal["pending", "publishing", "delivered", "failed"]
    mode: Literal["mock", "live"]
    blocked: bool  # the latest QA report says block_publish
    options: dict[str, Any] | None = None  # the options approved at Gate 2
    result: PublishResult | None = None
    error: str | None = None


def _approved_options(session: Session, run_id: str) -> dict[str, Any] | None:
    row = session.scalars(
        select(Approval)
        .where(Approval.run_id == run_id, Approval.gate == "publish", Approval.decision == "approve")
        .order_by(Approval.id.desc())
    ).first()
    if row is None:
        return None
    return json.loads(row.edits_json) if row.edits_json else {}


def _result(session: Session, run_id: str) -> PublishResult | None:
    row = session.scalars(
        select(Artifact)
        .where(Artifact.run_id == run_id, Artifact.type == "repo", Artifact.path.like("%.json"))
        .order_by(Artifact.version.desc())
    ).first()
    file = get_settings().runs_dir / row.path if row else None
    if file is None or not file.is_file():
        return None
    return PublishResult.model_validate_json(file.read_text(encoding="utf-8"))


def _failure(session: Session, run_id: str) -> str:
    step = session.scalars(
        select(AgentStep)
        .where(AgentStep.run_id == run_id, AgentStep.status == "failed")
        .order_by(AgentStep.id.desc())
    ).first()
    return (
        step.error_message if step and step.error_message else None
    ) or "The run failed before it was delivered."


@router.get("/runs/{run_id}/publish", response_model=PublishStatus)
def get_publish(run_id: str, session: Session = Depends(get_session)) -> PublishStatus:
    run = session.get(Run, run_id)
    if run is None:
        raise HTTPException(404, f"run {run_id} not found")
    report = latest_qa_report(run_id)
    options = _approved_options(session, run_id)
    base: dict[str, Any] = {
        "mode": get_settings().github_mode,
        "blocked": bool(report and report.get("block_publish")),
        "options": options,
    }
    if run.status == "delivered":
        return PublishStatus(status="delivered", result=_result(session, run_id), **base)
    if options is not None and run.status == "failed":
        return PublishStatus(status="failed", error=_failure(session, run_id), **base)
    if options is not None and run.status == "running":
        return PublishStatus(status="publishing", **base)
    return PublishStatus(status="pending", **base)
