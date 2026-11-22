import sys
from pathlib import Path

import pytest

from poc_studio.sandbox import runner

FAKE_GH = "gh" + "p_" + "a1" * 18  # built at runtime, not a real token


def test_child_env_has_no_secrets_and_keeps_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-" + "x" * 24)
    monkeypatch.setenv("GITHUB_TOKEN", FAKE_GH)
    monkeypatch.setenv("SOME_OTHER_VAR", "x")
    env = runner.child_env()
    assert "OPENAI_API_KEY" not in env and "GITHUB_TOKEN" not in env and "SOME_OTHER_VAR" not in env
    assert "PATH" in env
    assert env["NEXT_TELEMETRY_DISABLED"] == "1"
    assert set(env) <= {*runner.ENV_ALLOW, "NEXT_TELEMETRY_DISABLED"}


def _python(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(runner, "_command", lambda args, app_dir: [sys.executable, "-c", args[0]])


async def test_secrets_do_not_reach_the_process(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-" + "x" * 24)
    _python(monkeypatch)
    code = "import os; print('LEAK' if 'OPENAI_API_KEY' in os.environ else 'CLEAN')"
    ok, timed_out, _, out = await runner._run([code], tmp_path, 30)  # pyright: ignore[reportPrivateUsage]
    assert ok and not timed_out and "CLEAN" in out


async def test_timeout_kills_the_process(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    _python(monkeypatch)
    ok, timed_out, dur, out = await runner._run(  # pyright: ignore[reportPrivateUsage]
        ["import time; time.sleep(60)"], tmp_path, 1.0
    )
    assert not ok and timed_out and dur < 15 and "Timed out" in out


async def test_output_is_redacted(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    _python(monkeypatch)
    code = f"print('token {FAKE_GH} end')"
    _, _, _, out = await runner._run([code], tmp_path, 30)  # pyright: ignore[reportPrivateUsage]
    assert "ghp_" not in out and "[REDACTED]" in out


def test_child_env_points_home_dirs_at_the_run_folder(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setenv("npm_config_cache", str(tmp_path / "shared-cache"))
    home = tmp_path / "run1" / ".home"
    env = runner.child_env(home)
    for var in ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA"):
        assert env[var] == str(home)
    assert home.is_dir()
    assert env["npm_config_cache"] == str(tmp_path / "shared-cache")  # installs stay fast


async def test_the_child_sees_the_per_run_home(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    _python(monkeypatch)
    app = tmp_path / "runs" / "r1" / "app"
    app.mkdir(parents=True)
    code = "import os; print('HOME=' + os.environ['USERPROFILE'] + '|' + os.environ['APPDATA'])"
    ok, _, _, out = await runner._run([code], app, 30)  # pyright: ignore[reportPrivateUsage]
    home = str((tmp_path / "runs" / "r1" / ".home").resolve())
    assert ok and f"HOME={home}|{home}" in out


def test_install_skips_lifecycle_scripts() -> None:
    assert runner.INSTALL_ARGS[:2] == ["ci", "--ignore-scripts"]
    cmd = runner._command(runner.INSTALL_ARGS, Path("x"))  # pyright: ignore[reportPrivateUsage]
    assert "--ignore-scripts" in cmd


def test_docker_is_never_used_unless_asked(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SANDBOX_MODE", raising=False)
    runner.sandbox_mode.cache_clear()
    try:
        assert runner.sandbox_mode() == "folder"
    finally:
        runner.sandbox_mode.cache_clear()


def test_docker_command_is_named_and_a_timeout_kills_it(tmp_path) -> None:
    app = tmp_path / "run7" / "app"
    app.mkdir(parents=True)
    name = runner.container_name(app)
    assert name.startswith("poc-run7-")
    cmd = runner._command(["ci"], app, name)  # pyright: ignore[reportPrivateUsage]
    assert cmd[:5] == ["docker", "run", "--rm", "--name", name]
