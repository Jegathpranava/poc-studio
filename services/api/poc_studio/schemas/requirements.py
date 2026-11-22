"""The `Requirements` contract produced by the Meeting Intelligence agent (spec 7)."""

from typing import Literal

from pydantic import BaseModel, Field

Sector = Literal["logistics", "healthcare", "e-commerce", "fintech", "other"]
Priority = Literal["P1", "P2", "P3"]


class Feature(BaseModel):
    name: str
    detail: str
    priority: Priority
    confidence: float = Field(ge=0, le=1)
    source_ts: str | None = None
    source_quote: str


class Constraint(BaseModel):
    text: str
    confirmed: bool
    source_quote: str | None = None


class Budget(BaseModel):
    text: str | None = None
    amount_usd: float | None = None


class Stakeholder(BaseModel):
    name: str
    role: str


class ActionItem(BaseModel):
    text: str
    owner: str | None = None
    due: str | None = None


class Requirements(BaseModel):
    client: str
    sector: Sector
    title: str = Field(min_length=1, max_length=120)
    summary: str
    goals: list[str] = Field(default_factory=list)
    pain_points: list[str] = Field(default_factory=list)
    features: list[Feature] = Field(min_length=1, max_length=20)
    constraints: list[Constraint] = Field(default_factory=list)
    budget: Budget = Field(default_factory=Budget)
    timeline: str | None = None
    stakeholders: list[Stakeholder] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list)
