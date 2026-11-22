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
