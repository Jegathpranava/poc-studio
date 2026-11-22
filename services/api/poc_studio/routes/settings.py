"""GET/PUT /api/settings and POST /api/settings/test-gateway. Key values never leave the process."""

from typing import Literal

import httpx
from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

from poc_studio import settings_store
from poc_studio.config import get_settings
from poc_studio.settings_store import StoredSettings

router = APIRouter()
GATEWAY_TIMEOUT_S = 10.0


class GatewaySettings(BaseModel):
    base_url: str
    fast_model: str
    smart_model: str
    polish_model: str
    api_key_set: bool


class GithubSettings(BaseModel):
    mode: Literal["mock", "live"]
    token_set: bool
    private_default: Literal[True] = True


class BudgetSettings(BaseModel):
    run_limit_usd: float
    monthly_cap_usd: float
    hours_saved_per_run: float


class SettingsOut(BaseModel):
    gateway: GatewaySettings
    github: GithubSettings
    budget: BudgetSettings
    retention_days: int


class GatewayPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    base_url: str | None = Field(default=None, pattern=r"^https?://\S+$", max_length=300)
    fast_model: str | None = Field(default=None, min_length=1, max_length=80)
    smart_model: str | None = Field(default=None, min_length=1, max_length=80)
    polish_model: str | None = Field(default=None, min_length=1, max_length=80)


class BudgetPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    run_limit_usd: float | None = Field(default=None, gt=0, le=1000)
    monthly_cap_usd: float | None = Field(default=None, gt=0, le=100000)
    hours_saved_per_run: float | None = Field(default=None, ge=0, le=1000)


class SettingsPatch(BaseModel):
    """Only these fields can change. There is no field for a key or token; unknown fields are refused."""

    model_config = ConfigDict(extra="forbid")
    gateway: GatewayPatch | None = None
    budget: BudgetPatch | None = None
    retention_days: int | None = Field(default=None, ge=0, le=3650)


class GatewayTest(BaseModel):
    ok: bool
    models: list[str] = []
    error: str | None = None


def current() -> SettingsOut:
    s = get_settings()
    return SettingsOut(
        gateway=GatewaySettings(
            base_url=s.openai_base_url,
            fast_model=s.default_fast_model,
            smart_model=s.default_smart_model,
            polish_model=s.polish_model,
            api_key_set=bool(s.openai_api_key.get_secret_value()),
        ),
        github=GithubSettings(mode=s.github_mode, token_set=bool(s.github_token.get_secret_value())),
        budget=BudgetSettings(
            run_limit_usd=s.run_budget_usd,
            monthly_cap_usd=s.monthly_cap_usd,
            hours_saved_per_run=settings_store.effective_hours_saved(),
        ),
        retention_days=s.retention_days,
    )


@router.get("/settings", response_model=SettingsOut)
def get_current_settings() -> SettingsOut:
    return current()


@router.put("/settings", response_model=SettingsOut)
def update_settings(patch: SettingsPatch) -> SettingsOut:
    flat: dict[str, object] = {}
    for part in (patch.gateway, patch.budget):
        if part is not None:
            flat.update(part.model_dump(exclude_none=True))
    if patch.retention_days is not None:
        flat["retention_days"] = patch.retention_days
    settings_store.save(StoredSettings.model_validate(flat))
    settings_store.apply_overrides()
    return current()


def _client() -> httpx.Client:
    return httpx.Client(timeout=GATEWAY_TIMEOUT_S)


@router.post("/settings/test-gateway", response_model=GatewayTest)
def test_gateway() -> GatewayTest:
    """Mock mode answers at once. Gateway mode lists the models (`GET /models`): no completion, so $0."""
    s = get_settings()
    if s.llm_provider == "mock":
        return GatewayTest(ok=True, models=[s.default_fast_model, s.default_smart_model, s.polish_model])
    key = s.openai_api_key.get_secret_value()
    if not key:
        return GatewayTest(ok=False, error="OPENAI_API_KEY is not set in .env")
    try:
        with _client() as client:
            res = client.get(
                f"{s.openai_base_url.rstrip('/')}/models", headers={"Authorization": f"Bearer {key}"}
            )
        if res.status_code != 200:
            return GatewayTest(ok=False, error=f"The gateway answered {res.status_code}.")
        data = res.json().get("data", [])
        return GatewayTest(ok=True, models=[str(m["id"]) for m in data if isinstance(m, dict) and "id" in m])
    except (httpx.HTTPError, ValueError, AttributeError):
        return GatewayTest(ok=False, error="The gateway is not reachable.")
