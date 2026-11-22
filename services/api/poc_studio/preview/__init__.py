"""Preview servers. `get_preview_manager()` is the process-wide manager that `main.py` sets at start-up,
so agents (which have no request object) can stop a run's preview before they rebuild it."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from poc_studio.preview.manager import PreviewManager

_manager: "PreviewManager | None" = None


def set_preview_manager(manager: "PreviewManager | None") -> None:
    global _manager
    _manager = manager


def get_preview_manager() -> "PreviewManager | None":
    return _manager
