"""Run lifecycle: create, drive the graph as an asyncio task, gates, budget pause, restart recovery."""

import asyncio
import json
import logging
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.types import Command
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from poc_studio.config import get_settings
from poc_studio.db.models import Approval, Project, Run, new_run_id, now
from poc_studio.db.session import open_session
from poc_studio.events import RUN_AGENT, emit
from poc_studio.graph.build import build_graph
from poc_studio.graph.registry import NodeSpec, collect_nodes
from poc_studio.ingest.parse import MAX_FILE_BYTES, SUPPORTED
from poc_studio.llm import BudgetExceeded
from poc_studio.redact import install_log_redaction
from poc_studio.runs.edits import save_requirements_edit
from poc_studio.schemas.requirements import Requirements

log = logging.getLogger(__name__)

GATE_STATUS = {"scope": "waiting_gate1", "publish": "waiting_gate2"}
MAX_FILES = 10
MAX_TOTAL_BYTES = 60 * 1024 * 1024


class RunOptions(BaseModel):
    title: str | None = None
    budget_usd: float | None = Field(default=None, gt=0)


class InvalidUpload(ValueError):
    """An uploaded file is missing, too large or of an unsupported type."""


class GateError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code  # "not_found" | "conflict"


def safe_name(name: str, taken: set[str]) -> str:
    if "\x00" in name or ":" in name:
        raise InvalidUpload("file names must not contain NUL or ':' characters")
    base = Path(name.replace("\\", "/")).name.strip() or "upload"
    candidate, n = base, 1
    while candidate.casefold() in taken:  # case-insensitive file systems would merge A.vtt and a.vtt
        n += 1
        candidate = f"{n}_{base}"
    taken.add(candidate.casefold())
    return candidate


class RunService:
    def __init__(self, nodes: dict[str, NodeSpec] | None = None) -> None:
        self._nodes = nodes
        self._stack = AsyncExitStack()
        self._tasks: dict[str, asyncio.Task[None]] = {}
        self.graph: Any = None

    # --- lifecycle ----------------------------------------------------------
    async def start(self) -> None:
        install_log_redaction()  # exception text in logs may carry secrets
        path = get_settings().checkpoint_db_path
        if path is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
        saver = await self._stack.enter_async_context(
            AsyncSqliteSaver.from_conn_string(str(path) if path else ":memory:")
        )
        self.graph = build_graph(saver, self._nodes or collect_nodes())
        with open_session() as session:
            pending = session.scalars(select(Run.id).where(Run.status.in_(("queued", "running")))).all()
        for run_id in pending:  # waiting_* and paused_budget runs stay as they are
            self._spawn(run_id, self._recover(run_id))

    async def stop(self) -> None:
        tasks = list(self._tasks.values())
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await self._stack.aclose()

    # --- public operations ----------------------------------------------------
    async def create_run(
        self,
        files: list[tuple[str, bytes]],
        client: str,
        sector: str | None = None,
        options: RunOptions | None = None,
    ) -> str:
        options = options or RunOptions()
        client = client.strip()
        if not client:
            raise InvalidUpload("client name is required")
        if not files:
            raise InvalidUpload("at least one file is required")
        if len(files) > MAX_FILES:
            raise InvalidUpload(f"at most {MAX_FILES} files per run")
        if sum(len(d) for _, d in files) > MAX_TOTAL_BYTES:
            raise InvalidUpload(f"uploads exceed the total limit of {MAX_TOTAL_BYTES / (1024 * 1024):g} MB")
        taken: set[str] = set()
        named = [(safe_name(n, taken), data) for n, data in files]
        for name, data in named:
            if Path(name).suffix.lower() not in SUPPORTED:
                raise InvalidUpload(f"{name}: unsupported type, expected one of {', '.join(SUPPORTED)}")
            if len(data) > MAX_FILE_BYTES:
                raise InvalidUpload(f"{name}: larger than {MAX_FILE_BYTES // (1024 * 1024)} MB")
        settings = get_settings()
        budget = options.budget_usd or settings.run_budget_usd
        with open_session() as session:
            key = client.lower()
            project = session.scalar(select(Project).where(Project.client_name_key == key))
            if project is None:
                project = Project(client_name=client, client_name_key=key, sector=sector)
                session.add(project)
                session.flush()
            elif sector:
                project.sector = sector
            run = Run(
                id=self._free_run_id(session),
                project_id=project.id,
                title=options.title or f"{client} PoC",
                status="queued",
                budget_usd=budget,
                started_at=now(),
            )
            session.add(run)
            session.commit()
            run_id = run.id
        input_dir = settings.runs_dir / run_id / "input"
        input_dir.mkdir(parents=True, exist_ok=True)
        for name, data in named:
            (input_dir / name).write_bytes(data)
        emit(run_id, RUN_AGENT, "status", status="queued", message=f"Run created with {len(named)} file(s)")
        self._spawn(run_id, self._drive(run_id, self._initial_input(run_id, budget)))
        return run_id

    async def decide(
        self, run_id: str, gate: str, decision: str, edits: dict[str, object] | None, note: str | None
    ) -> str:
        """Record the approval and resume the graph. Returns the run status after the decision."""
        with open_session() as session:
            run = session.get(Run, run_id)
            if run is None:
                raise GateError("not_found", f"run {run_id} not found")
            if run.status != GATE_STATUS[gate]:
                raise GateError("conflict", f"run is {run.status}, not waiting at gate {gate}")
            run.status = "running"  # claimed here, so a second click gets a 409
            session.add(
                Approval(
                    run_id=run_id,
                    gate=gate,
                    decision=decision,
                    edits_json=json.dumps(edits) if edits else None,
                    note=note,
                )
            )
            session.commit()
        if gate == "scope" and decision == "approve" and edits:
            # The route validated `edits`; save them before the graph resumes so later agents read them.
            save_requirements_edit(run_id, Requirements.model_validate(edits))
        payload = {"decision": decision, "edits": edits, "note": note}
        # The gate node emits the "gate" decision event once it consumes this payload.
        self._spawn(run_id, self._drive(run_id, Command(resume=payload)))
        return "running"

    async def resume(self, run_id: str, budget_usd: float | None = None) -> None:
        """Continue a run that stopped on `paused_budget` (or was left running) from its checkpoint.

        `budget_usd` raises the limit first (in `runs.budget_usd` and in the checkpointed state).
        """
        if budget_usd is not None and budget_usd <= 0:
            raise ValueError("budget_usd must be greater than 0")
        with open_session() as session:
            run = session.get(Run, run_id)
            if run is None:
                raise GateError("not_found", f"run {run_id} not found")
            if run.status not in ("paused_budget", "running"):
                raise GateError("conflict", f"run is {run.status}, nothing to resume")
            self._ensure_idle(run_id)
            if budget_usd is not None:
                run.budget_usd = budget_usd
                session.commit()
        config = {"configurable": {"thread_id": run_id}}
        if budget_usd is not None and (await self.graph.aget_state(config)).created_at is not None:
            await self.graph.aupdate_state(config, {"limit_usd": budget_usd})
        payload = await self._next_input(run_id)
        self._ensure_idle(run_id)  # the awaits above let another resume or decision slip in
        self._spawn(run_id, self._drive(run_id, payload))

    # --- internals ---------------------------------------------------------------
    @staticmethod
    def _free_run_id(session: Session) -> str:
        while True:
            candidate = new_run_id()
            if session.get(Run, candidate) is None:
                return candidate

    @staticmethod
    def _initial_input(run_id: str, budget: float) -> dict[str, Any]:
        return {"run_id": run_id, "limit_usd": budget, "spent_delta": 0.0, "sent_back_count": 0}

    def _ensure_idle(self, run_id: str) -> None:
        task = self._tasks.get(run_id)
        if task is not None and not task.done():
            raise GateError("conflict", f"run {run_id} is already being driven")

    async def _next_input(self, run_id: str) -> Any:
        """What to feed the graph to continue: the first input, a decision lost to a crash, or None."""
        snap = await self.graph.aget_state({"configurable": {"thread_id": run_id}})
        if snap.created_at is None:  # no checkpoint yet: the run never got going
            with open_session() as session:
                run = session.get(Run, run_id)
                budget = run.budget_usd if run else get_settings().run_budget_usd
            return self._initial_input(run_id, budget)
        gates = [i.value.get("gate") for i in snap.interrupts if isinstance(i.value, dict)]
        with open_session() as session:
            row = session.scalars(
                select(Approval)
                .where(Approval.run_id == run_id, Approval.gate.in_(gates), Approval.consumed_at.is_(None))
                .order_by(Approval.id.desc())
                .limit(1)
            ).first()
            if row is not None:  # decided, but the process died before the gate node consumed it
                edits = json.loads(row.edits_json) if row.edits_json else None
                return Command(resume={"decision": row.decision, "edits": edits, "note": row.note})
        return None

    def _spawn(self, run_id: str, coro: Any) -> None:
        task = asyncio.create_task(coro, name=f"run-{run_id}")
        self._tasks[run_id] = task
        task.add_done_callback(lambda t: self._tasks.get(run_id) is t and self._tasks.pop(run_id, None))

    async def _recover(self, run_id: str) -> None:
        await self._drive(run_id, await self._next_input(run_id))

    def _set_status(self, run_id: str, status: str, *, finished: bool = False) -> None:
        with open_session() as session:
            run = session.get(Run, run_id)
            if run is not None:
                run.status = status
                if finished:
                    run.finished_at = now()
                session.commit()

    def _settle(self, run_id: str, status: str, *, finished: bool = False) -> None:
        """Final status of a drive. Unregisters this task first, so an observer who sees the status can
        call resume() without hitting the "already being driven" conflict."""
        if self._tasks.get(run_id) is asyncio.current_task():
            del self._tasks[run_id]
        self._set_status(run_id, status, finished=finished)

    async def _drive(self, run_id: str, payload: Any) -> None:
        config = {"configurable": {"thread_id": run_id}}
        self._set_status(run_id, "running")
        emit(run_id, RUN_AGENT, "status", status="running")
        try:
            await self.graph.ainvoke(payload, config)
            snap = await self.graph.aget_state(config)
        except BudgetExceeded as exc:
            self._settle(run_id, "paused_budget")
            emit(run_id, RUN_AGENT, "status", status="paused_budget", message=str(exc))
            return
        except asyncio.CancelledError:
            raise  # shutting down: the run stays `running` and is resumed on the next start
        except Exception as exc:
            log.exception("run %s failed", run_id)
            self._settle(run_id, "failed", finished=True)
            emit(run_id, RUN_AGENT, "error", status="failed", error={"message": str(exc)})
            return
        gates = [i.value.get("gate") for i in snap.interrupts if isinstance(i.value, dict)]
        if gates and gates[0] in GATE_STATUS:
            status = GATE_STATUS[gates[0]]
            self._settle(run_id, status)
            emit(run_id, RUN_AGENT, "gate", status=status, message=f"Waiting at gate {gates[0]}")
        elif not snap.next:
            self._settle(run_id, "delivered", finished=True)
            emit(run_id, RUN_AGENT, "status", status="delivered")
        else:
            self._settle(run_id, "failed", finished=True)
            emit(run_id, RUN_AGENT, "error", status="failed", error={"message": f"stopped at {snap.next}"})
