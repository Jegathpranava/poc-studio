"""Process-tree helpers shared by the build runner and the preview manager."""

import os
import subprocess
import sys

IS_WINDOWS = sys.platform == "win32"


def kill_pid_tree(pid: int) -> None:
    """Kill a process and its children. Safe on a pid that is already gone."""
    if IS_WINDOWS:
        subprocess.run(
            ["taskkill", "/T", "/F", "/PID", str(pid)], capture_output=True, check=False, timeout=15
        )
        return
    import signal

    try:
        os.killpg(pid, signal.SIGKILL)  # pyright: ignore[reportAttributeAccessIssue]
    except ProcessLookupError:
        pass


def process_image(pid: int) -> str:
    """Lower-case image of a pid: `node.exe` (Windows tasklist) or the /proc cmdline. "" when unknown."""
    if IS_WINDOWS:
        done = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"], capture_output=True, text=True,
            check=False, timeout=15,
        )  # fmt: skip
        line = done.stdout.strip().splitlines()[0] if done.stdout.strip() else ""
        return line.split('","')[0].strip('"').lower() if line.startswith('"') else ""
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as fh:
            return fh.read().replace(b"\x00", b" ").decode("utf-8", "replace").lower()
    except OSError:
        return ""


def looks_like_preview_image(image: str) -> bool:
    """True for what a preview server runs as: node.exe or cmd.exe on Windows; next or node elsewhere."""
    if IS_WINDOWS:
        return image in ("node.exe", "cmd.exe")
    return "next" in image or "node" in image


def pid_alive(pid: int) -> bool:
    """True when a process with this pid exists. (os.kill(pid, 0) would TERMINATE it on Windows.)"""
    if IS_WINDOWS:
        done = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/NH", "/FO", "CSV"], capture_output=True, text=True,
            check=False, timeout=15,
        )  # fmt: skip
        return f'"{pid}"' in done.stdout
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True
