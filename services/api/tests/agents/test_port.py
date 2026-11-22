import json
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import select

from poc_studio.db.models import AgentStep, Artifact
from poc_studio.db.session import open_session
from poc_studio.events import load_events
from poc_studio.llm.client import set_provider
from poc_studio.llm.provider import FIXTURE_DIR, MockProvider
from poc_studio.sandbox import runner
from poc_studio.sandbox.errors import BuildError
from tests.agents.test_screens import Recorder
from tests.graph.conftest import create_run, wait_status

ERROR = BuildError(
    file="app/broken/page.tsx",
    line=1,
    col=1,
    message="Module not found: Can't resolve './x'",
    excerpt="> 1 | x",
)


class FakeBuild:
    """Replaces runner.install and runner.build: `outcomes` is one bool per build call."""

    def __init__(self, outcomes: list[bool]) -> None:
        self.outcomes = outcomes
        self.builds: list[int] = []
        self.installs = 0

    async def install(self, app_dir: Path) -> runner.StepResult:
        self.installs += 1
        return runner.StepResult(ok=True, duration_s=1.5)

    async def build(self, app_dir: Path, attempt: int = 1) -> runner.BuildResult:
        self.builds.append(attempt)
        ok = self.outcomes[len(self.builds) - 1]
        return runner.BuildResult(
            ok=ok, duration_s=2.0, attempt=attempt, log_tail="log", error=None if ok else ERROR
        )


def _drive(client_for: Any, fake: FakeBuild, monkeypatch: pytest.MonkeyPatch) -> tuple[str, Recorder]:
    monkeypatch.setattr(runner, "install", fake.install)
    monkeypatch.setattr(runner, "build", fake.build)
    rec = Recorder()
    set_provider(rec)
    try:
        with client_for() as client:
            run_id = create_run(client)
            wait_status(client, run_id, "waiting_gate1")
            assert (
                client.post(f"/api/runs/{run_id}/gates/scope", json={"decision": "approve"}).status_code
                == 200
            )
            wait_status(client, run_id, "waiting_gate2")
            return run_id, rec
    finally:
        set_provider(None)


def _port_step(run_id: str) -> AgentStep:
    with open_session() as s:
        step = s.scalars(select(AgentStep).where(AgentStep.run_id == run_id, AgentStep.agent == "port")).one()
        s.expunge(step)
        return step


def test_fixture_is_a_port_fix() -> None:
    data = json.loads((FIXTURE_DIR / "port.json").read_text(encoding="utf-8"))
    assert data["files"][0]["path"] == "app/broken/page.tsx"
    assert MockProvider  # the mock serves it for agent "port"


def test_fail_then_pass_costs_one_model_call(client_for, env, monkeypatch) -> None:
    fake = FakeBuild([False, True])
    run_id, rec = _drive(client_for, fake, monkeypatch)
    assert fake.installs == 1 and fake.builds == [1, 2]
    prompts = rec.prompts["port"]
    assert len(prompts) == 1
    assert (
        "<untrusted>" in prompts[0]
        and "Module not found" in prompts[0]
        and "app/broken/page.tsx" in prompts[0]
    )
    step = _port_step(run_id)
    assert step.status == "done" and step.attempt == 2 and step.model == "smart"
    app = env / "runs" / run_id / "app"
    assert (app / "app" / "page.tsx").is_file() and (app / "app" / "kit" / "product.css").is_file()
    assert (app / "app" / "broken" / "page.tsx").is_file()  # the fix from port.json was applied
    assert not (app / "node_modules").exists()
    info = json.loads((env / "runs" / run_id / "build.json").read_text(encoding="utf-8"))
    assert info["ok"] is True and info["attempts"] == 2 and info["install_s"] == 1.5
    with open_session() as s:
        arts = list(
            s.scalars(select(Artifact).where(Artifact.run_id == run_id, Artifact.type == "prototype"))
        )
    assert [(a.version, a.path) for a in arts] == [(1, f"{run_id}/app")]
    logs = [e for e in load_events(run_id) if e.agent == "port" and e.kind == "log"]
    assert [getattr(e, "attempt", None) for e in logs if "build attempt" in (e.message or "")] == [1, 2]


def test_three_failures_fail_the_step_and_still_reach_gate2(client_for, env, monkeypatch) -> None:
    fake = FakeBuild([False, False, False])
    run_id, rec = _drive(client_for, fake, monkeypatch)
    assert fake.builds == [1, 2, 3]
    assert len(rec.prompts["port"]) == 2  # a fix after attempts 1 and 2, none after the last
    step = _port_step(run_id)
    assert step.status == "failed" and step.attempt == 3
    assert "Attempt 3 of 3" in (step.error_message or "")
    errors = [e for e in load_events(run_id) if e.agent == "port" and e.kind == "error"]
    structured = [e for e in errors if e.error is not None and e.error.file]
    assert structured, errors
    err = structured[0].error
    assert err is not None
    assert (err.file, err.line, err.col) == ("app/broken/page.tsx", 1, 1)
    assert err.message.startswith("Module not found") and err.excerpt
    assert structured[0].message == "Attempt 3 of 3"
