"""Spend bookkeeping for nodes.

A node builds its `RunBudget` with `node_budget(state)`; every charge is added to `runs.paid_usd` at once,
so a later `BudgetExceeded` or crash cannot lose it. The node returns `{"spent_delta": budget.charged_usd}`;
the state reducer adds deltas, so parallel branches (pitch, port) both count.
"""

from poc_studio.config import get_settings
from poc_studio.db.models import Run
from poc_studio.db.session import open_session
from poc_studio.graph.state import RunState
from poc_studio.llm import RunBudget


def add_paid(run_id: str, cost: float) -> None:
    with open_session() as session:
        run = session.get(Run, run_id)
        if run is not None:
            run.paid_usd += cost
            session.commit()


def node_budget(state: RunState) -> RunBudget:
    """Limit from the state; spend is the larger of the state total and the ledger (`runs.paid_usd`).

    The ledger also holds charges of earlier attempts that never reached the state.
    """
    run_id = state["run_id"]
    with open_session() as session:
        run = session.get(Run, run_id)
        paid = run.paid_usd if run else 0.0
    spent = max(state.get("spent_delta", 0.0), paid)
    limit = state.get("limit_usd", get_settings().run_budget_usd)
    return RunBudget(run_id, limit, spent, on_charge=lambda cost: add_paid(run_id, cost))
