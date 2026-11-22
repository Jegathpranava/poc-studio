"""Both gates, end to end, on the mock LLM, a real SQLite file and the folder sandbox.

The full case is `slow` (a real `npm ci` and `next build`). The failing-port and planted-secret cases fake
the npm steps (conftest), so they are fast. One `browser` case records a real short MP4.
"""

import functools
import json
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import select

from poc_studio.db.models import AgentStep, Artifact
from poc_studio.db.session import open_session
from poc_studio.llm.client import set_provider
from poc_studio.media import video as media_video
from poc_studio.sandbox import runner
from poc_studio.sandbox.errors import BuildError
from tests.agents.test_screens import Recorder
from tests.graph.conftest import create_run, wait_status

PLANTED = "ghp_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4"  # fake token, split so the source holds no secret
ORDER = ["intake", "intelligence", "gate1", "architect", "screens", "pitch", "port", "assemble", "qa"]
TAIL = ["gate2", "video", "repo"]


def _drive(client_for: Any, final: str, timeout: float = 300.0) -> tuple[str, dict[str, Any]]:
    set_provider(Recorder())
    try:
        with client_for() as client:
            run_id = create_run(client)
            wait_status(client, run_id, "waiting_gate1")
            client.post(f"/api/runs/{run_id}/gates/scope", json={"decision": "approve"})
            wait_status(client, run_id, "waiting_gate2", timeout=timeout)
            if final == "waiting_gate2":
                return run_id, client.get(f"/api/runs/{run_id}").json()
            res = client.post(f"/api/runs/{run_id}/gates/publish", json={"decision": "approve"})
            assert res.status_code == 200, res.text
            return run_id, wait_status(client, run_id, final, timeout=timeout)
    finally:
        set_provider(None)


def _agents(run_id: str) -> list[str]:
    with open_session() as s:
        rows = s.scalars(select(AgentStep).where(AgentStep.run_id == run_id).order_by(AgentStep.id)).all()
        return [r.agent for r in rows]


def _artifacts(run_id: str) -> dict[str, list[str]]:
    with open_session() as s:
        rows = s.scalars(select(Artifact).where(Artifact.run_id == run_id)).all()
        out: dict[str, list[str]] = {}
        for r in rows:
            out.setdefault(r.type, []).append(r.path)
        return out


def _reports(env: Path, run_id: str) -> list[dict[str, Any]]:
    paths = sorted(_artifacts(run_id).get("qa_report", []))
    return [json.loads((env / "runs" / p).read_text(encoding="utf-8")) for p in paths]


def _assert_order(agents: list[str]) -> None:
    first = {a: agents.index(a) for a in set(agents)}
    for a, b in zip(ORDER, ORDER[1:], strict=False):
        if {a, b} == {"pitch", "port"}:
            continue  # parallel branches: any order
        assert first[a] < first[b], (a, b, agents)
    assert first["screens"] < min(first["pitch"], first["port"])
    assert max(first["pitch"], first["port"]) < first["assemble"]
    tail = [a for a in agents if a in TAIL]
    assert tail == TAIL, agents


@pytest.mark.slow
def test_full_run_through_both_gates_to_delivered(
    client_for: Any, env: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("VIDEO_FAKE", "1")
    run_id, detail = _drive(client_for, "delivered")
    assert detail["status"] == "delivered" and detail["finished_at"] is not None
    agents = _agents(run_id)
    _assert_order(agents)
    assert agents.count("pitch") == 1 and agents.count("port") == 1 and agents.count("qa") == 1
    arts = _artifacts(run_id)
    for kind in ("requirements", "architecture", "screenpack", "deck", "docs", "pptx", "prototype",
                 "qa_report", "video", "repo"):  # fmt: skip
        assert arts.get(kind), f"missing artifact {kind}: {sorted(arts)}"
    assert any(p.endswith(".json") for p in arts["deck"]) and any(p.endswith(".html") for p in arts["deck"])
    assert any(p.endswith(".mp4") for p in arts["video"]) and any("chapters" in p for p in arts["video"])
    for paths in arts.values():
        for p in paths:
            assert (env / "runs" / p).exists(), p
    assert detail["paid_usd"] <= detail["budget_usd"]
    (report,) = _reports(env, run_id)
    assert report["failed"] == [] and report["block_publish"] is False
    repo = json.loads((env / "runs" / arts["repo"][0]).read_text(encoding="utf-8"))
    assert repo["private"] is True and repo["mode"] == "mock"
    assert repo["repo_url"].startswith("https://github.com/")


def test_failed_port_still_reaches_gate2_with_a_report_only_build_failure(
    client_for: Any, env: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    error = BuildError(file="app/page.tsx", line=1, col=1, message="Type error", excerpt="> 1 | x")
    builds: list[int] = []

    async def failing_build(app_dir: Path, attempt: int = 1) -> runner.BuildResult:
        builds.append(attempt)
        return runner.BuildResult(ok=False, duration_s=0.1, attempt=attempt, log_tail="log", error=error)

    monkeypatch.setattr(runner, "build", failing_build)
    run_id, detail = _drive(client_for, "waiting_gate2")
    assert detail["status"] == "waiting_gate2"
    assert builds == [1, 2, 3]
    (report,) = _reports(env, run_id)
    check = next(c for c in report["checks"] if c["name"] == "build_passed")
    assert check["ok"] is False and check["report_only"] is True
    assert "repo code did not build" in check["detail"]
    assert report["send_back"] is None and "build_passed" in report["failed"]
    agents = _agents(run_id)
    assert agents.count("pitch") == 1 and "assemble" in agents and "qa" in agents


def test_planted_secret_sends_back_port_only_and_blocks_publish(
    client_for: Any, env: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    real_install = runner.install

    async def leaky_install(app_dir: Path) -> Any:
        (app_dir / "app").mkdir(parents=True, exist_ok=True)
        (app_dir / "app" / "leak.ts").write_text(f'export const t = "{PLANTED}";\n', encoding="utf-8")
        return await real_install(app_dir)

    monkeypatch.setattr(runner, "install", leaky_install)
    run_id, _ = _drive(client_for, "waiting_gate2")
    agents = _agents(run_id)
    assert agents.count("port") == 3 and agents.count("qa") == 3
    assert agents.count("pitch") == 1 and agents.count("screens") == 1  # port-only send-back
    assert agents.count("assemble") == 3
    reports = _reports(env, run_id)
    assert [r["send_back"] for r in reports] == ["port", "port", None]
    assert reports[-1]["block_publish"] is True and "no_secrets" in reports[-1]["failed"]
    assert PLANTED not in json.dumps(reports)


@pytest.mark.browser
def test_real_short_recording_in_the_full_flow(
    client_for: Any, env: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(media_video, "record", functools.partial(media_video.record, hold_s=0.3))
    run_id, detail = _drive(client_for, "delivered", timeout=180.0)
    assert detail["status"] == "delivered"
    mp4 = [p for p in _artifacts(run_id)["video"] if p.endswith(".mp4")]
    assert mp4 and (env / "runs" / mp4[0]).stat().st_size > 2000
