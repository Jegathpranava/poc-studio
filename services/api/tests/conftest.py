import os

# Test defaults must be set before poc_studio.config is imported.
os.environ["LLM_PROVIDER"] = "mock"
os.environ["GITHUB_MODE"] = "mock"
os.environ["APP_ENV"] = "test"
os.environ["POC_DATABASE_URL"] = "sqlite:///:memory:"

import pytest  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _create_tables() -> None:
    from poc_studio.db import models  # noqa: F401
    from poc_studio.db.base import Base
    from poc_studio.db.session import get_engine

    Base.metadata.create_all(get_engine())


@pytest.fixture(autouse=True)
def _no_real_npm(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    """Graph tests reach the port node: its install and build are fakes unless the test is `slow`."""
    if request.node.get_closest_marker("slow"):
        return
    from poc_studio.sandbox import runner

    async def fake_install(app_dir):  # noqa: ANN001, ANN202
        return runner.StepResult(ok=True, duration_s=0.0)

    async def fake_build(app_dir, attempt=1):  # noqa: ANN001, ANN202
        return runner.BuildResult(ok=True, duration_s=0.0, attempt=attempt)

    monkeypatch.setattr(runner, "install", fake_install)
    monkeypatch.setattr(runner, "build", fake_build)
