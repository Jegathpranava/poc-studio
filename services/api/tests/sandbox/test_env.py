import sys

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
