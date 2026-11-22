"""Built-in nodes: intake and the two gates. Every other node comes from an agent module."""

from typing import Any

from langgraph.types import interrupt
from sqlalchemy import select

from poc_studio.config import get_settings
from poc_studio.db.models import Approval, now
from poc_studio.db.session import open_session
from poc_studio.events import RUN_AGENT, emit
from poc_studio.graph.registry import NodeFn, NodeSpec
from poc_studio.graph.state import RunState
from poc_studio.graph.steps import step_scope
from poc_studio.ingest import parse_files


async def intake(state: RunState) -> dict[str, Any]:
    """Parse the uploaded files once, so a bad file fails the run early. Stores their relative paths."""
    run_id = state["run_id"]
    async with step_scope(run_id, "intake"):
        run_dir = get_settings().runs_dir / run_id
        files = sorted(p for p in (run_dir / "input").iterdir() if p.is_file())
        transcript = parse_files(files)
        summary = f"{len(transcript.segments)} segments, {transcript.word_count} words"
        emit(run_id, "intake", "log", message=f"Parsed {len(files)} file(s): {summary}")
        return {"transcript_refs": [p.relative_to(run_dir).as_posix() for p in files]}


def mark_consumed(run_id: str, gate: str) -> None:
    """The gate node took its decision: stamp the newest open Approval so a restart does not replay it."""
    with open_session() as session:
        row = session.scalars(
            select(Approval)
            .where(Approval.run_id == run_id, Approval.gate == gate, Approval.consumed_at.is_(None))
            .order_by(Approval.id.desc())
            .limit(1)
        ).first()
        if row is not None:
            row.consumed_at = now()
            session.commit()


def _gate_node(name: str, gate: str, key: str) -> NodeFn:
    async def gate_node(state: RunState) -> dict[str, Any]:
        # interrupt() re-runs this node from the top on resume, so nothing before it may have side effects.
        decision = interrupt({"gate": gate})
        run_id = state["run_id"]
        mark_consumed(run_id, gate)
        async with step_scope(run_id, name):
            verdict = decision["decision"]
            emit(run_id, RUN_AGENT, "gate", status=verdict, message=f"Gate {gate}: {verdict}")
            update: dict[str, Any] = {key: decision}
            if name == "gate1" and verdict == "approve" and decision.get("edits"):
                update["requirements"] = decision[
                    "edits"
                ]  # later agents see the owner's brief, not the draft
            if name == "gate1":
                update["intelligence_note"] = decision.get("note") if verdict == "changes" else None
            return update

    return gate_node


def builtin_nodes() -> list[NodeSpec]:
    specs = [
        NodeSpec("intake", intake, "orchestrator"),
        NodeSpec("gate1", _gate_node("gate1", "scope", "gate1"), "orchestrator"),
        NodeSpec("gate2", _gate_node("gate2", "publish", "gate2"), "orchestrator"),
    ]
    return specs
