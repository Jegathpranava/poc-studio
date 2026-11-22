"""Settings from the environment and the repo-root .env. Secrets are SecretStr and never logged."""

from functools import lru_cache
from pathlib import Path
from typing import Literal, Self

from pydantic import AliasChoices, Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DB_URL = "sqlite:///./data/poc-studio.sqlite"


def _a(name: str) -> AliasChoices:
    return AliasChoices(name, name.lower())


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=REPO_ROOT / ".env", extra="ignore")

    app_env: Literal["development", "test", "production"] = Field(
        "development", validation_alias=_a("APP_ENV")
    )
    llm_provider: Literal["mock", "gateway"] = Field("mock", validation_alias=_a("LLM_PROVIDER"))
    github_mode: Literal["mock", "live"] = Field("mock", validation_alias=_a("GITHUB_MODE"))

    openai_base_url: str = Field(
        "https://gateway.ai.skyformit.com/v1", validation_alias=_a("OPENAI_BASE_URL")
    )
    openai_api_key: SecretStr = Field(SecretStr(""), validation_alias=_a("OPENAI_API_KEY"))
    default_fast_model: str = Field("fast", validation_alias=_a("DEFAULT_FAST_MODEL"))
    default_smart_model: str = Field("smart", validation_alias=_a("DEFAULT_SMART_MODEL"))
    polish_model: str = Field("claude-haiku-5-5", validation_alias=_a("POLISH_MODEL"))
    github_token: SecretStr = Field(SecretStr(""), validation_alias=_a("GITHUB_TOKEN"))

    database_url: str = Field(DEFAULT_DB_URL, validation_alias=_a("POC_DATABASE_URL"))
    run_budget_usd: float = Field(0.05, validation_alias=_a("RUN_BUDGET_USD"))
    monthly_cap_usd: float = Field(5.0, validation_alias=_a("MONTHLY_CAP_USD"))
    eval_live: bool = Field(False, validation_alias=_a("EVAL_LIVE"))
    retention_days: int = Field(30, validation_alias=_a("RETENTION_DAYS"))
    runs_dir_setting: str = Field("runs", validation_alias=_a("RUNS_DIR"))

    @model_validator(mode="after")
    def _no_mocks_in_production(self) -> Self:
        if self.app_env == "production":
            if self.llm_provider == "mock":
                raise ValueError("LLM_PROVIDER=mock is refused when APP_ENV=production")
            if self.github_mode == "mock":
                raise ValueError("GITHUB_MODE=mock is refused when APP_ENV=production")
        return self

    @property
    def runs_dir(self) -> Path:
        path = Path(self.runs_dir_setting)
        return path if path.is_absolute() else REPO_ROOT / path

    @property
    def checkpoint_db_path(self) -> Path | None:
        """LangGraph checkpoints live in a file next to the app DB (data/checkpoints.sqlite).
        None means the app DB is in memory, so the checkpoints are too."""
        prefix = "sqlite:///"
        url = self.resolved_database_url
        if url.startswith(prefix) and not url.endswith(":memory:"):
            return Path(url.removeprefix(prefix)).with_name("checkpoints.sqlite")
        return None

    @property
    def resolved_database_url(self) -> str:
        """Relative sqlite paths resolve against the repo root, so cwd never matters."""
        prefix = "sqlite:///"
        if not self.database_url.startswith(prefix):
            return self.database_url
        path = self.database_url[len(prefix) :]
        if path == ":memory:" or Path(path).is_absolute():
            return self.database_url
        return prefix + (REPO_ROOT / path).resolve().as_posix()


@lru_cache
def get_settings() -> Settings:
    return Settings()  # pyright: ignore[reportCallIssue]  (fields are filled from the environment)
