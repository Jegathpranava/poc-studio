"""Run `npm ci` and `npm run build` for a copy of a sector starter.

Folder mode (default): a child process in `runs/<id>/app` with an allow-listed environment, a timeout and a
process-tree kill. Home directories point at `runs/<id>/.home`, so an install script cannot read the real
profile; the npm cache stays shared. Docker mode is used ONLY when SANDBOX_MODE=docker is set and
`docker info` exits 0; it is NOT exercised by the tests (Docker is not installed on the dev machine).
"""

import asyncio
import functools
import itertools
import os
import shutil
import subprocess
import time
from pathlib import Path

from pydantic import BaseModel

from poc_studio.redact import redact
from poc_studio.sandbox.errors import BuildError, parse_build_error, strip_ansi
from poc_studio.sandbox.procs import IS_WINDOWS, kill_pid_tree
from poc_studio.screens.kits import TEMPLATES_DIR

INSTALL_TIMEOUT_S = 180.0
BUILD_TIMEOUT_S = 90.0
LOG_TAIL_CHARS = 6000

# Only these variables reach the child. Nothing else from os.environ, and nothing from `.env`.
ENV_ALLOW = (
    "PATH", "SYSTEMROOT", "COMSPEC", "PATHEXT", "TEMP", "TMP", "HOME", "USERPROFILE", "APPDATA",
    "LOCALAPPDATA", "npm_config_cache",
)  # fmt: skip
# Lifecycle scripts of dependencies never run (supply chain). If a package needs its postinstall, rebuild that
# one package explicitly (`npm rebuild <pkg>`); the sector starters build without any.
INSTALL_ARGS = ["ci", "--ignore-scripts", "--prefer-offline", "--no-audit", "--no-fund"]
_COPY_IGNORE = shutil.ignore_patterns("node_modules", ".next")


class StepResult(BaseModel):
    ok: bool
    duration_s: float
    timed_out: bool = False
    log_tail: str = ""


class BuildResult(StepResult):
    attempt: int = 1
    error: BuildError | None = None


_HOME_VARS = ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA")


def shared_npm_cache() -> str | None:
    """The real npm cache, so installs stay fast although HOME moves."""
    if os.environ.get("npm_config_cache"):
        return os.environ["npm_config_cache"]
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA")
        return str(Path(base) / "npm-cache") if base else None
    return str(Path.home() / ".npm")


def child_env(home: Path | None = None) -> dict[str, str]:
    """Allow-listed environment. With `home`, HOME/USERPROFILE/APPDATA/LOCALAPPDATA point at that folder."""
    env = {k: os.environ[k] for k in ENV_ALLOW if k in os.environ}
    cache = shared_npm_cache()
    if home is not None:
        home.mkdir(parents=True, exist_ok=True)
        for var in _HOME_VARS:
            env[var] = str(home)
    if cache:
        env["npm_config_cache"] = cache
    env["NEXT_TELEMETRY_DISABLED"] = "1"
    return env


@functools.lru_cache(maxsize=1)
def sandbox_mode() -> str:
    """`docker` only when SANDBOX_MODE=docker is set explicitly and `docker info` exits 0, else `folder`.

    Cached for the process; call it through `asyncio.to_thread` (it may run `docker info`).
    """
    if os.environ.get("SANDBOX_MODE", "").lower() != "docker":
        return "folder"
    docker = shutil.which("docker")
    if docker is None:
        return "folder"
    try:
        done = subprocess.run([docker, "info"], capture_output=True, timeout=10, env=child_env())
    except (OSError, subprocess.SubprocessError):
        return "folder"
    return "docker" if done.returncode == 0 else "folder"


_container_seq = itertools.count(1)


def container_name(app_dir: Path) -> str:
    return f"poc-{app_dir.resolve().parent.name}-{next(_container_seq)}"


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


def _command(args: list[str], app_dir: Path, name: str | None = None) -> list[str]:
    if name is not None:  # docker mode. UNTESTED: Docker is not available on the dev machine
        return [
            "docker", "run", "--rm", "--name", name, "-v", f"{app_dir.resolve()}:/app", "-w", "/app",
            "-e", "NEXT_TELEMETRY_DISABLED=1", "node:22", "npm", *args,
        ]  # fmt: skip
    npm = shutil.which("npm", path=os.environ.get("PATH")) or "npm"  # npm.cmd on Windows
    return [npm, *args]


def _kill_tree(proc: asyncio.subprocess.Process) -> None:
    if proc.returncode is not None:
        return
    kill_pid_tree(proc.pid)
    try:
        proc.kill()
    except ProcessLookupError:
        pass


def _docker_kill(name: str) -> None:
    try:
        subprocess.run(["docker", "kill", name], capture_output=True, timeout=15, check=False)
    except (OSError, subprocess.SubprocessError):
        pass


async def _run(args: list[str], app_dir: Path, timeout_s: float) -> tuple[bool, bool, float, str]:
    """(ok, timed_out, duration, redacted output). stderr is merged into stdout."""
    started = time.monotonic()
    name = container_name(app_dir) if await asyncio.to_thread(sandbox_mode) == "docker" else None
    proc = await asyncio.create_subprocess_exec(
        *(_command(args, app_dir, name) if name else _command(args, app_dir)),
        cwd=app_dir,
        env=child_env(app_dir.resolve().parent / ".home"),
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
        if name:
            await asyncio.to_thread(_docker_kill, name)
        try:
            out, _ = await asyncio.wait_for(proc.communicate(), 10)
        except TimeoutError:
            out = b""
    except asyncio.CancelledError:
        _kill_tree(proc)
        if name:
            await asyncio.to_thread(_docker_kill, name)
        raise
    text = strip_ansi(out.decode("utf-8", errors="replace"))
    if timed_out:
        text += f"\nTimed out after {timeout_s:.0f} s"
    return proc.returncode == 0 and not timed_out, timed_out, time.monotonic() - started, redact(text)


def _tail(text: str) -> str:
    return text[-LOG_TAIL_CHARS:]


async def install(app_dir: Path) -> StepResult:
    ok, timed_out, dur, text = await _run(INSTALL_ARGS, app_dir, INSTALL_TIMEOUT_S)
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
