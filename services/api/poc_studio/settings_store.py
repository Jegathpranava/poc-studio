"""Owner-editable, non-secret settings in one JSON file (`settings.json` next to the app database).

Keys and tokens are never stored here and `.env` is never written: they stay in the environment. A JSON file
is the simplest fit for six scalar values, and needs no migration. `apply_overrides` copies the saved values
onto the live `Settings` object (models, budgets, retention take effect at once; the gateway base URL is read
when the LLM provider is first built, so it needs an API restart).
"""

import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from poc_studio.config import REPO_ROOT, Settings, get_settings

DEFAULT_HOURS_SAVED = 5.5


class StoredSettings(BaseModel):
    """Everything is optional: a missing value means "use the environment default"."""

    model_config = ConfigDict(extra="forbid")

    base_url: str | None = Field(default=None, pattern=r"^https?://\S+$", max_length=300)
    fast_model: str | None = Field(default=None, min_length=1, max_length=80)
    smart_model: str | None = Field(default=None, min_length=1, max_length=80)
    polish_model: str | None = Field(default=None, min_length=1, max_length=80)
    run_limit_usd: float | None = Field(default=None, gt=0, le=1000)
    monthly_cap_usd: float | None = Field(default=None, gt=0, le=100000)
    hours_saved_per_run: float | None = Field(default=None, ge=0, le=1000)
    retention_days: int | None = Field(default=None, ge=0, le=3650)


def settings_path() -> Path:
    url = get_settings().resolved_database_url
    prefix = "sqlite:///"
    if url.startswith(prefix) and not url.endswith(":memory:"):
        return Path(url.removeprefix(prefix)).with_name("settings.json")
    return REPO_ROOT / "data" / "settings.json"


def load() -> StoredSettings:
    try:
        return StoredSettings.model_validate_json(settings_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return StoredSettings()


def save(patch: StoredSettings) -> StoredSettings:
    """Merge the fields that were sent into the stored file (atomic replace)."""
    merged: dict[str, Any] = load().model_dump()
    merged.update(patch.model_dump(exclude_unset=True))
    stored = StoredSettings.model_validate(merged)
    path = settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(stored.model_dump_json(indent=2), encoding="utf-8")
    os.replace(tmp, path)
    return stored


def apply_overrides(settings: Settings | None = None) -> Settings:
    """Copy the saved values onto `settings` (the process-wide one by default)."""
    target = settings or get_settings()
    stored = load()
    mapping = {
        "openai_base_url": stored.base_url,
        "default_fast_model": stored.fast_model,
        "default_smart_model": stored.smart_model,
        "polish_model": stored.polish_model,
        "run_budget_usd": stored.run_limit_usd,
        "monthly_cap_usd": stored.monthly_cap_usd,
        "retention_days": stored.retention_days,
    }
    for name, value in mapping.items():
        if value is not None:
            setattr(target, name, value)
    return target


def effective_hours_saved() -> float:
    value = load().hours_saved_per_run
    return DEFAULT_HOURS_SAVED if value is None else value
