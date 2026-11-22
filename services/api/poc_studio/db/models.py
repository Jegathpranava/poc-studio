"""Tables from spec sections 7 and 7b."""

import secrets
from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from poc_studio.db.base import Base

RUN_STATUSES = ("queued", "running", "waiting_gate1", "waiting_gate2", "paused_budget", "failed", "delivered")
ARTIFACT_TYPES = (
    "requirements",
    "architecture",
    "prototype",
    "deck",
    "pptx",
    "video",
    "docs",
    "qa_report",
    "share_export",
    "screenpack",
)
GATES = ("scope", "publish")
DECISIONS = ("approve", "changes")


def _in(col: str, values: tuple[str, ...]) -> str:
    return f"{col} IN ({', '.join(repr(v) for v in values)})"


def now() -> datetime:
    return datetime.now(UTC)


def new_run_id() -> str:
    return "r_" + secrets.token_hex(3)


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (UniqueConstraint("client_name_key"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_name: Mapped[str] = mapped_column(String(200))
    client_name_key: Mapped[str] = mapped_column(String(200))  # lower-cased, for case-insensitive reuse
    sector: Mapped[str | None] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Run(Base):
    __tablename__ = "runs"
    __table_args__ = (
        CheckConstraint(_in("status", RUN_STATUSES), name="ck_runs_status"),
        CheckConstraint("id GLOB 'r_[0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f]'", name="ck_runs_id"),
    )

    id: Mapped[str] = mapped_column(String(8), primary_key=True, default=new_run_id)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    title: Mapped[str] = mapped_column(String(300))
    status: Mapped[str] = mapped_column(String(20), default="queued")
    current_step: Mapped[str | None] = mapped_column(String(40))
    paid_usd: Mapped[float] = mapped_column(Float, default=0.0)
    tokens_total: Mapped[int] = mapped_column(Integer, default=0)
    budget_usd: Mapped[float] = mapped_column(Float, default=0.05)
    preview_pid: Mapped[int | None] = mapped_column(Integer)
    preview_port: Mapped[int | None] = mapped_column(Integer)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AgentStep(Base):
    __tablename__ = "agent_steps"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    agent: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(20))
    attempt: Mapped[int] = mapped_column(Integer, default=1)
    model: Mapped[str | None] = mapped_column(String(80))
    tokens_in: Mapped[int] = mapped_column(Integer, default=0)
    tokens_out: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_file: Mapped[str | None] = mapped_column(String(500))
    error_line: Mapped[int | None] = mapped_column(Integer)
    error_message: Mapped[str | None] = mapped_column(Text)


class Artifact(Base):
    __tablename__ = "artifacts"
    __table_args__ = (CheckConstraint(_in("type", ARTIFACT_TYPES), name="ck_artifacts_type"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    type: Mapped[str] = mapped_column(String(20))
    version: Mapped[int] = mapped_column(Integer, default=1)
    path: Mapped[str] = mapped_column(String(500))
    sha256: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Approval(Base):
    __tablename__ = "approvals"
    __table_args__ = (
        CheckConstraint(_in("gate", GATES), name="ck_approvals_gate"),
        CheckConstraint(_in("decision", DECISIONS), name="ck_approvals_decision"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    gate: Mapped[str] = mapped_column(String(10))
    decision: Mapped[str] = mapped_column(String(10))
    edits_json: Mapped[str | None] = mapped_column(Text)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Event(Base):
    """Replayed by SSE from Last-Event-ID, so ids increase monotonically."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    agent: Mapped[str] = mapped_column(String(40))
    level: Mapped[str] = mapped_column(String(10), default="info")
    message: Mapped[str] = mapped_column(Text)
