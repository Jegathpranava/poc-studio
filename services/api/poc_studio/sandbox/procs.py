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
