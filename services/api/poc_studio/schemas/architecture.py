"""The `Architecture` contract produced by the Solution Architect agent (spec 7)."""

from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator

UseCaseClass = Literal["rag", "agent", "classifier", "vision", "forecasting", "other"]


class Component(BaseModel):
    name: str
    kind: str
    detail: str


class ModelPick(BaseModel):
    job: str
    model: str
    cost_per_1k_calls_usd: float = Field(ge=0)


class CostLine(BaseModel):
    item: str
    usd: float = Field(ge=0)


class MonthlyCost(BaseModel):
    lines: list[CostLine] = Field(min_length=1)
    total_usd: float = Field(ge=0)
    assumptions: str

    @model_validator(mode="after")
    def _total_matches_lines(self) -> Self:
        expected = sum(line.usd for line in self.lines)
        if abs(self.total_usd - expected) > 0.01:
            raise ValueError(f"total_usd {self.total_usd} does not match the sum of lines {expected:.2f}")
        return self


class Phase(BaseModel):
    name: str
    weeks: float = Field(gt=0)
    detail: str


class Architecture(BaseModel):
    use_case_class: UseCaseClass
    components: list[Component] = Field(min_length=3, max_length=12)
    mermaid: str
    models: list[ModelPick] = Field(min_length=1, max_length=8)
    monthly_cost: MonthlyCost
    phases: list[Phase] = Field(default_factory=list)
    rationale: str

    @model_validator(mode="after")
    def _mermaid_is_a_diagram(self) -> Self:
        if not self.mermaid.lstrip().startswith(("flowchart", "graph")):
            raise ValueError("mermaid must start with 'flowchart' or 'graph'")
        return self
