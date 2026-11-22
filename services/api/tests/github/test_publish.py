import json
import subprocess
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import select

from poc_studio.db.models import Artifact
from poc_studio.db.session import open_session
from poc_studio.github.client import MockGitHub
from poc_studio.github.publish import (
    PublishBlocked,
    PublishOptions,
    default_repo_name,
    prepare_repo_dir,
    publish,
)
from poc_studio.llm.client import set_provider
from tests.agents.test_screens import Recorder
from tests.graph.conftest import create_run, wait_status

FAKE_TOKEN = "ghp_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4"  # fake token, split so the source holds no secret
OPTIONS = PublishOptions(repo_name="acme-poc")


@pytest.fixture
def run_id(client_for: Any, env: Path) -> str:
    """A mock run parked at Gate 2: real artifacts, an app folder with fake node_modules and caches."""
    set_provider(Recorder())
    try:
        with client_for() as client:
            rid = create_run(client)
            wait_status(client, rid, "waiting_gate1")
            client.post(f"/api/runs/{rid}/gates/scope", json={"decision": "approve"})
            wait_status(client, rid, "waiting_gate2")
    finally:
        set_provider(None)
    app = env / "runs" / rid / "app"
    for rel in ("node_modules/pkg/index.js", ".next/cache/x.txt", ".home/.npmrc"):
        (app / rel).parent.mkdir(parents=True, exist_ok=True)
        (app / rel).write_text("x", encoding="utf-8")
    return rid


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout


def test_prepare_repo_dir_contents(run_id: str) -> None:
    out = prepare_repo_dir(run_id)
    names = {p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file()}
    assert not any(n.startswith(("node_modules", ".next", ".home")) for n in names)
    assert {"README.md", ".env.example", ".github/workflows/ci.yml", "package.json"} <= names
    assert {"docs/exec-summary.md", "docs/user-flows.md", "deck/deck.html"} <= names
    assert any(n.startswith("app/") for n in names)  # the ported pages
    readme = (out / "README.md").read_text(encoding="utf-8")
    assert "```mermaid" in readme and "Run locally" in readme and "Monthly cost" in readme
    assert "(docs/exec-summary.md)" in readme and "(deck/deck.html)" in readme
    ci = (out / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "node-version: 24" in ci and "npm ci --ignore-scripts" in ci and "npm run build" in ci
    assert "actions/checkout@v4" in ci and "actions/setup-node@v4" in ci


def test_add_ci_off_skips_the_workflow(run_id: str) -> None:
    assert not (prepare_repo_dir(run_id, add_ci=False) / ".github").exists()


def test_planted_token_blocks_without_leaking_it(run_id: str, env: Path) -> None:
    (env / "runs" / run_id / "app" / "app" / "leak.ts").write_text(f'export const t = "{FAKE_TOKEN}";\n')
    with pytest.raises(PublishBlocked) as info:
        publish(run_id, OPTIONS, github=MockGitHub())
    assert "app/leak.ts:1 github_token" in str(info.value)
    assert FAKE_TOKEN not in str(info.value)
    assert not (env / "runs" / run_id / "publish.mock.json").exists()  # nothing was planned


def _artifact_json(env: Path, run_id: str, kind: str) -> dict[str, Any]:
    with open_session() as s:
        rows = s.scalars(
            select(Artifact).where(
                Artifact.run_id == run_id, Artifact.type == kind, Artifact.path.like("%.json")
            )
        ).all()
        path = env / "runs" / max(rows, key=lambda r: r.version).path
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def _qa_report(env: Path, run_id: str, **fields: Any) -> None:
    with open_session() as s:
        rows = list(
            s.scalars(select(Artifact).where(Artifact.run_id == run_id, Artifact.type == "qa_report"))
        )
        path = env / "runs" / max(rows, key=lambda r: r.version).path
    report = json.loads(path.read_text(encoding="utf-8")) | fields
    path.write_text(json.dumps(report), encoding="utf-8")


def test_block_publish_in_the_qa_report_blocks(run_id: str, env: Path) -> None:
    _qa_report(env, run_id, block_publish=True)
    gh = MockGitHub()
    with pytest.raises(PublishBlocked, match="QA blocked"):
        publish(run_id, OPTIONS, github=gh)
    assert gh.calls == []  # blocked before any call


def test_mock_publish_records_calls_and_commits_locally(run_id: str, env: Path) -> None:
    gh = MockGitHub()
    result = publish(run_id, OPTIONS, github=gh)
    assert result.mode == "mock" and result.pushed is False and result.private is True
    assert result.repo_url == "https://github.com/Jegathpranava/acme-poc"
    create = next(c for c in gh.calls if c["call"] == "create_repo")
    assert create["private"] is True and create["path"] == "/user/repos"
    assert any(c["call"] == "push" and c["would_push"] for c in gh.calls)

    requirements = _artifact_json(env, run_id, "requirements")
    assert len(result.issues) == len(requirements["action_items"])
    assert all(u.startswith("https://github.com/Jegathpranava/acme-poc/issues/") for u in result.issues)

    recorded = json.loads((env / "runs" / run_id / "publish.mock.json").read_text(encoding="utf-8"))
    assert recorded["mode"] == "mock" and len(recorded["calls"]) == len(gh.calls)

    out = env / "runs" / run_id / "publish"
    assert _git(out, "log", "--format=%an <%ae>").strip() == "PoC Studio <noreply@example.com>"
    assert _git(out, "branch", "--show-current").strip() == "main"
    config = (out / ".git" / "config").read_text(encoding="utf-8")
    assert "extraheader" not in config.lower() and "bearer" not in config.lower() and "ghp_" not in config
    assert _git(out, "remote").strip() == ""  # mock never adds a remote
    with open_session() as s:
        repo = s.scalars(select(Artifact).where(Artifact.run_id == run_id, Artifact.type == "repo")).one()
    assert repo.path.endswith("publish.v1.json")


def test_issues_can_be_turned_off(run_id: str) -> None:
    result = publish(
        run_id, PublishOptions(repo_name="acme-poc", open_issues=False, private=False), github=MockGitHub()
    )
    assert result.issues == [] and result.private is False


def test_name_conflict_gets_a_suffix(run_id: str) -> None:
    gh = MockGitHub(existing={"acme-poc", "acme-poc-2"})
    assert publish(run_id, OPTIONS, github=gh).name == "acme-poc-3"


def test_default_repo_name() -> None:
    assert default_repo_name("Acme Freight", "Acme Freight PoC") == "acme-freight-poc"
    assert default_repo_name("Acme", "Dock scheduling") == "acme-dock-scheduling-poc"


def test_options_validation() -> None:
    for bad in ("", "has space", "a/b", "x" * 101, "..", "repo.git"):
        with pytest.raises(ValueError):
            PublishOptions(repo_name=bad)


def test_live_push_keeps_the_token_out_of_config_and_url(
    run_id: str, env: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Push to a local bare repo as the 'remote': the token header goes through the env, not the files."""
    from poc_studio.github import publish as mod

    bare = env / "remote.git"
    _git(env, "init", "--bare", "-b", "main", str(bare))
    out = prepare_repo_dir(run_id)
    seen: list[dict[str, str]] = []
    real = mod._git_env

    def spy(token: str | None) -> dict[str, str]:
        e = real(token)
        seen.append(e)
        return e

    monkeypatch.setattr(mod, "_git_env", spy)
    pushed, sha = mod.push(out, bare.as_posix(), FAKE_TOKEN)
    assert pushed and len(sha) == 40
    assert any(e.get("GIT_CONFIG_VALUE_0") == f"AUTHORIZATION: bearer {FAKE_TOKEN}" for e in seen)
    assert FAKE_TOKEN not in (out / ".git" / "config").read_text(encoding="utf-8")
    assert FAKE_TOKEN not in _git(out, "remote", "-v")
    assert _git(bare, "log", "--oneline", "main").strip()


def test_git_failure_is_redacted(run_id: str) -> None:
    from poc_studio.github.publish import PublishFailed, push

    out = prepare_repo_dir(run_id)
    with pytest.raises(PublishFailed) as info:
        push(out, "https://127.0.0.1:9/none.git", FAKE_TOKEN)  # nothing listens on port 9
    assert FAKE_TOKEN not in str(info.value)
