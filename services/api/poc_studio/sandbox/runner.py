"""Run `npm ci` and `npm run build` for a copy of a sector starter.

Folder mode (default): a child process in `runs/<id>/app` with an allow-listed environment, a timeout and a
process-tree kill. Docker mode is used when `docker info` exits 0; it is NOT exercised by the tests (Docker
is not installed on the dev machine).
"""

import asyncio
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from pydantic import BaseModel

from poc_studio.redact import redact
from poc_studio.sandbox.errors import BuildError, parse_build_error, strip_ansi
from poc_studio.screens.kits import TEMPLATES_DIR

INSTALL_TIMEOUT_S = 180.0
BUILD_TIMEOUT_S = 90.0
LOG_TAIL_CHARS = 6000
IS_WINDOWS = sys.platform == "win32"

# Only these variables reach the child. Nothing else from os.environ, and nothing from `.env`.
ENV_ALLOW = (
    "PATH", "SYSTEMROOT", "COMSPEC", "PATHEXT", "TEMP", "TMP", "HOME", "USERPROFILE", "APPDATA",
    "LOCALAPPDATA", "npm_config_cache",
)  # fmt: skip
_COPY_IGNORE = shutil.ignore_patterns("node_modules", ".next")


class StepResult(BaseModel):
    ok: bool
    duration_s: float
    timed_out: bool = False
    log_tail: str = ""


class BuildResult(StepResult):
    attempt: int = 1
    error: BuildError | None = None


def child_env() -> dict[str, str]:
    env = {k: os.environ[k] for k in ENV_ALLOW if k in os.environ}
    env["NEXT_TELEMETRY_DISABLED"] = "1"
    return env


def sandbox_mode() -> str:
    """`docker` when `docker info` exits 0, else `folder`. SANDBOX_MODE=folder|docker overrides."""
    forced = os.environ.get("SANDBOX_MODE", "").lower()
    if forced in ("folder", "docker"):
        return forced
    docker = shutil.which("docker")
    if docker is None:
        return "folder"
    try:
        done = subprocess.run([docker, "info"], capture_output=True, timeout=10, env=child_env())
    except (OSError, subprocess.SubprocessError):
        return "folder"
    return "docker" if done.returncode == 0 else "folder"


async def prepare(run_dir: Path, sector: str) -> Path:
    """Copy `templates/<sector>/app` to `<run_dir>/app` (no node_modules, no .next). Replaces an old copy."""
    src = TEMPLATES_DIR / sector / "app"
    if not src.is_dir():
        raise FileNotFoundError(f"no starter for sector {sector!r}")
    dest = run_dir / "app"

    def copy() -> None:
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest, ignore=_COPY_IGNORE)

    await asyncio.to_thread(copy)
    return dest


def _command(args: list[str], app_dir: Path) -> list[str]:
    if sandbox_mode() == "docker":  # UNTESTED: Docker is not available on the dev machine
        return [
            "docker", "run", "--rm", "-v", f"{app_dir.resolve()}:/app", "-w", "/app",
            "-e", "NEXT_TELEMETRY_DISABLED=1", "node:22", "npm", *args,
        ]  # fmt: skip
    npm = shutil.which("npm", path=os.environ.get("PATH")) or "npm"  # npm.cmd on Windows
    return [npm, *args]


def _kill_tree(proc: asyncio.subprocess.Process) -> None:
    if proc.returncode is not None:
        return
    if IS_WINDOWS:
        subprocess.run(
            ["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True, check=False, timeout=15
        )
    else:
        import signal

        try:
            os.killpg(proc.pid, signal.SIGKILL)  # pyright: ignore[reportAttributeAccessIssue]
        except ProcessLookupError:
            pass
    try:
        proc.kill()
    except ProcessLookupError:
        pass


async def _run(args: list[str], app_dir: Path, timeout_s: float) -> tuple[bool, bool, float, str]:
    """(ok, timed_out, duration, redacted output). stderr is merged into stdout."""
    started = time.monotonic()
    proc = await asyncio.create_subprocess_exec(
        *_command(args, app_dir),
        cwd=app_dir,
        env=child_env(),
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        start_new_session=not IS_WINDOWS,
    )
    timed_out = False
    try:
        out, _ = await asyncio.wait_for(proc.communicate(), timeout_s)
    except TimeoutError:
        timed_out = True
        _kill_tree(proc)
        try:
            out, _ = await asyncio.wait_for(proc.communicate(), 10)
        except TimeoutError:
            out = b""
    except asyncio.CancelledError:
        _kill_tree(proc)
        raise
    text = strip_ansi(out.decode("utf-8", errors="replace"))
    if timed_out:
        text += f"\nTimed out after {timeout_s:.0f} s"
    return proc.returncode == 0 and not timed_out, timed_out, time.monotonic() - started, redact(text)


def _tail(text: str) -> str:
    return text[-LOG_TAIL_CHARS:]


async def install(app_dir: Path) -> StepResult:
    ok, timed_out, dur, text = await _run(
        ["ci", "--prefer-offline", "--no-audit", "--no-fund"], app_dir, INSTALL_TIMEOUT_S
    )
    return StepResult(ok=ok, duration_s=round(dur, 2), timed_out=timed_out, log_tail=_tail(text))


async def build(app_dir: Path, attempt: int = 1) -> BuildResult:
    ok, timed_out, dur, text = await _run(["run", "build"], app_dir, BUILD_TIMEOUT_S)
    error = None if ok else parse_build_error(text, app_dir)
    if not ok and error is None:
        error = BuildError(file="", line=0, col=0, message="Build timed out" if timed_out else "Build failed")
    return BuildResult(
        ok=ok, duration_s=round(dur, 2), timed_out=timed_out, log_tail=_tail(text), attempt=attempt,
        error=error,
    )  # fmt: skip
