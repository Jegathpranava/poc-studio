"""Request and response models for every endpoint in spec section 7, plus the 7b event shape."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

RunStatus = Literal[
    "queued", "running", "waiting_gate1", "waiting_gate2", "paused_budget", "failed", "delivered"
]
ArtifactType = Literal[
    "requirements", "architecture", "prototype", "deck", "pptx", "video",
    "docs", "qa_report", "share_export", "screenpack",
]  # fmt: skip
GateScope = Literal["scope", "publish"]
RunId = Field(pattern=r"^r_[0-9a-f]{6}$")


class _Out(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# --- health -----------------------------------------------------------------
class HealthResponse(BaseModel):
    status: Literal["ok"]
    llm_provider: Literal["mock", "gateway"]
    github_mode: Literal["mock", "live"]
    db: Literal["ok"]


# --- runs -------------------------------------------------------------------
class RunSummary(_Out):
    id: str = RunId
    title: str
    client_name: str
    sector: str | None = None
    status: RunStatus
    current_step: str | None = None
    paid_usd: float
    budget_usd: float
    started_at: datetime | None = None
    finished_at: datetime | None = None


class AgentStepOut(_Out):
    id: int
    agent: str
    status: str
    attempt: int
    model: str | None = None
    tokens_in: int
    tokens_out: int
    cost_usd: float
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error_file: str | None = None
    error_line: int | None = None
    error_message: str | None = None


class ArtifactOut(_Out):
    id: int
    type: ArtifactType
    version: int
    path: str
    sha256: str | None = None
    created_at: datetime


class ArtifactJson(BaseModel):
    """The latest version of a JSON artifact, such as `requirements`."""

    type: ArtifactType
    version: int
    data: dict[str, Any]


class RunDetail(RunSummary):
    tokens_total: int
    preview_port: int | None = None
    steps: list[AgentStepOut] = []
    artifacts: list[ArtifactOut] = []


class CreateRunOptions(BaseModel):
    """Form fields sent next to the multipart `files` on POST /api/runs."""

    client_name: str = Field(min_length=1, max_length=200)
    title: str | None = None
    sector: str | None = None
    budget_usd: float | None = Field(default=None, gt=0)


class CreateRunResponse(BaseModel):
    id: str = RunId


# --- gates, revise, retry, budget ----------------------------------------------
class GateDecisionRequest(BaseModel):
    decision: Literal["approve", "changes"]
    edits: dict[str, object] | None = None
    note: str | None = None


class GateDecisionResponse(BaseModel):
    run_id: str
    gate: GateScope
    decision: Literal["approve", "changes"]
    status: RunStatus


class ReviseRequest(BaseModel):
    note: str = Field(min_length=1)


class RetryRequest(BaseModel):
    note: str | None = None
    attempts: int | None = Field(default=None, ge=1, le=5)


class BudgetRaiseRequest(BaseModel):
    budget_usd: float = Field(gt=0)


class RunActionResponse(BaseModel):
    run_id: str
    status: RunStatus


# --- artifacts, share, settings, templates ----------------------------------------
class ShareExportResponse(BaseModel):
    run_id: str
    artifact: ArtifactOut
    share_token: str | None = None


class SettingsModel(BaseModel):
    llm_provider: Literal["mock", "gateway"]
    github_mode: Literal["mock", "live"]
    run_budget_usd: float = Field(gt=0)
    monthly_cap_usd: float = Field(gt=0)
    retention_days: int = Field(ge=1)
    default_fast_model: str
    default_smart_model: str
    polish_model: str


class SettingsUpdate(BaseModel):
    run_budget_usd: float | None = Field(default=None, gt=0)
    monthly_cap_usd: float | None = Field(default=None, gt=0)
    retention_days: int | None = Field(default=None, ge=1)
    default_fast_model: str | None = None
    default_smart_model: str | None = None
    polish_model: str | None = None


class TemplateInfo(BaseModel):
    id: str
    sector: str
    label: str
    has_kit: bool
    has_app: bool


# --- SSE events (spec 7b) -----------------------------------------------------------
class EventError(BaseModel):
    file: str | None = None
    line: int | None = None
    col: int | None = None
    message: str
    excerpt: str | None = None


class RunEvent(BaseModel):
    """`data` of an SSE message. The SSE event name is `step` or `run`."""

    id: int
    ts: datetime
    run_id: str
    agent: str
    kind: Literal["status", "log", "cost", "gate", "error"]
    status: str | None = None
    message: str | None = None
    model: str | None = None
    tokens_in: int | None = None
    tokens_out: int | None = None
    cost_usd: float | None = None
    attempt: int | None = None
    error: EventError | None = None
