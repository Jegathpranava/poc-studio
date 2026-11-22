"""Event loop for uvicorn: `--loop poc_studio.event_loop:loop_factory`.

With `--reload` (or workers) uvicorn picks a SelectorEventLoop on Windows, which cannot start subprocesses:
`asyncio.create_subprocess_exec` raises a bare NotImplementedError, so npm, the preview server and every
other child process fail. The Proactor loop supports subprocesses; other platforms keep the default loop.
"""

import asyncio
import sys


def loop_factory() -> asyncio.AbstractEventLoop:
    if sys.platform == "win32":
        return asyncio.ProactorEventLoop()
    return asyncio.new_event_loop()
