"""Step bookkeeping shared by every node: an `agent_steps` row, `runs.current_step` and status events."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import func, select

from poc_studio.db.models import AgentStep, Run, now
from poc_studio.db.session import open_session
from poc_studio.events import emit
from poc_studio.llm import BudgetExceeded
from poc_studio.redact import redact


@asynccontextmanager
async def step_scope(
    run_id: str, agent: str, *, model: str | None = None, reason: str | None = None
) -> AsyncIterator[int]:
    """Record one run of `agent`. Yields the step row id; the caller updates tokens and cost on it.

    A rerun is a "send_back" when the caller says so (see `graph.revise.rerun_reason`); otherwise it is a
    "retry" when the previous run of the step did not finish and a "revise" when it did.
    """
    with open_session() as session:
        attempt = (
            session.scalar(
                select(func.count())
                .select_from(AgentStep)
                .where(AgentStep.run_id == run_id, AgentStep.agent == agent)
            )
            or 0
        ) + 1
        if attempt == 1:
            reason = None
        elif reason != "send_back":
            last = session.scalar(
                select(AgentStep.status)
                .where(AgentStep.run_id == run_id, AgentStep.agent == agent)
                .order_by(AgentStep.id.desc())
                .limit(1)
            )
            reason = "revise" if last == "done" else "retry"  # a rerun of an unfinished step is a retry
        row = AgentStep(
            run_id=run_id, agent=agent, status="running", attempt=attempt, reason=reason, model=model,
            started_at=now(),
        )  # fmt: skip
        session.add(row)
        run = session.get(Run, run_id)
        if run is not None:
            run.current_step = agent
        session.commit()
        step_id = row.id
    emit(run_id, agent, "status", status="running", attempt=attempt, reason=reason, model=model)
    try:
        yield step_id
    except asyncio.CancelledError:  # shutdown or cancel: the run is resumed later and gets a new attempt
        _finish(step_id, "interrupted", None)
        emit(run_id, agent, "status", status="interrupted", attempt=attempt)
        raise
    except Exception as exc:
        status = "paused" if isinstance(exc, BudgetExceeded) else "failed"
        message = redact(str(exc))[:500]
        _finish(step_id, status, message)
        emit(run_id, agent, "error", status=status, attempt=attempt, error={"message": message})
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
