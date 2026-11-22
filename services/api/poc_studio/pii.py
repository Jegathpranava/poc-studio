"""Optional PII mask for text that goes to the LLM (spec 8). Off unless the run option `mask_pii` is set.

Emails (except `example.com`) become `[email]` and phone numbers `[phone]`. Names are never masked: in v1 the
stakeholders are not known at intake (they come out of the extraction itself), so `intelligence` passes an
empty `keep_names` and person names reach the model. A stakeholder's own address (`jane.doe@...` for "Jane
Doe") stays when the name is in `keep_names`, the same rule `qa.secrets.scan_pii` applies.
"""

import json
import re
from collections.abc import Callable, Iterable
from pathlib import Path

from poc_studio.config import get_settings
from poc_studio.qa.secrets import _EMAIL, _PHONE, _name_forms  # pyright: ignore[reportPrivateUsage]

OPTIONS_FILE = "options.json"


def mask_pii(text: str, keep_names: Iterable[str] = ()) -> str:
    allowed = _name_forms(keep_names)

    def email(m: re.Match[str]) -> str:
        domain = m.group(2).lower()
        if domain == "example.com" or domain.endswith(".example.com") or m.group(1).lower() in allowed:
            return m.group(0)
        return "[email]"

    def phone(m: re.Match[str]) -> str:
        return "[phone]" if 9 <= len(re.sub(r"\D", "", m.group(0))) <= 15 else m.group(0)

    return _PHONE.sub(phone, _EMAIL.sub(email, text))


def _options_path(run_id: str) -> Path:
    return get_settings().runs_dir / run_id / OPTIONS_FILE


def write_run_options(run_id: str, *, mask: bool) -> None:
    """Stored as `runs/<id>/options.json` (no schema change: the run row has no options column)."""
    path = _options_path(run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"mask_pii": mask}), encoding="utf-8")


def run_masks_pii(run_id: str) -> bool:
    try:
        data = json.loads(_options_path(run_id).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return isinstance(data, dict) and data.get("mask_pii") is True


def mask_for_run(run_id: str) -> Callable[[str], str] | None:
    """The `mask` hook for `complete_json`, or None when the run did not ask for it."""
    return (lambda t: mask_pii(t, [])) if run_masks_pii(run_id) else None
