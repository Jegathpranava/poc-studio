"""Step bookkeeping shared by every node: an `agent_steps` row, `runs.current_step` and status events."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import func, select

from poc_studio.db.models import AgentStep, Run, now
from poc_studio.db.session import open_session
from poc_studio.events import emit
from poc_studio.llm import BudgetExceeded


@asynccontextmanager
async def step_scope(run_id: str, agent: str, *, model: str | None = None) -> AsyncIterator[int]:
    """Record one attempt of `agent`. Yields the step row id; the caller updates tokens and cost on it."""
    with open_session() as session:
        attempt = (
            session.scalar(
                select(func.count())
                .select_from(AgentStep)
                .where(AgentStep.run_id == run_id, AgentStep.agent == agent)
            )
            or 0
        ) + 1
        row = AgentStep(
            run_id=run_id, agent=agent, status="running", attempt=attempt, model=model, started_at=now()
        )
        session.add(row)
        run = session.get(Run, run_id)
        if run is not None:
            run.current_step = agent
        session.commit()
        step_id = row.id
    emit(run_id, agent, "status", status="running", attempt=attempt, model=model)
    try:
        yield step_id
    except Exception as exc:
        status = "paused" if isinstance(exc, BudgetExceeded) else "failed"
        _finish(step_id, status, str(exc))
        emit(run_id, agent, "error", status=status, attempt=attempt, error={"message": str(exc)})
        raise
    _finish(step_id, "done", None)
    emit(run_id, agent, "status", status="done", attempt=attempt)


def _finish(step_id: int, status: str, error: str | None) -> None:
    with open_session() as session:
        row = session.get(AgentStep, step_id)
        if row is not None:
            row.status = status
            row.finished_at = now()
            row.error_message = error
            session.commit()
