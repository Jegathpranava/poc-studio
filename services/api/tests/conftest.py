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


@pytest.fixture(autouse=True)
def _no_real_recorder(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    """Graph tests reach the video node: the recorder is a fake unless the test is `browser` or `slow`."""
    if request.node.get_closest_marker("browser") or request.node.get_closest_marker("slow"):
        return
    from poc_studio.media import video

    def fake_record(deck_html_path, out_mp4, hold_s=None, size=(1280, 720)):  # noqa: ANN001, ANN202
        out_mp4.parent.mkdir(parents=True, exist_ok=True)
        out_mp4.write_bytes(b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 600)
        chapters = [video.Chapter(t=0.0, title="Welcome")]
        (out_mp4.parent / "chapters.json").write_text('[{"t": 0.0, "title": "Welcome"}]', encoding="utf-8")
        return video.VideoResult(path=out_mp4, duration_s=12.0, chapters=chapters)

    monkeypatch.setattr(video, "record", fake_record)
