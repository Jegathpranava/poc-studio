"""Gate 2 revisions: which agent a "changes" decision sends the run back to, and the note it carries.

The gate node stores `{agent: note}` under `revise_note`; the owning agent reads its own note, adds it to
its prompt and clears it in the state update it returns. Only the owning agent writes the key, so the
parallel pitch and port branches never write it together.
"""

from typing import Any

from poc_studio.graph.state import RunState

REVISE_KEY = "revise_note"
# Agents a Gate 2 decision may send the run back to, and the graph node that runs them.
REVISE_TARGETS: dict[str, str] = {
    "architect": "architect",
    "screens": "screens",
    "pitch": "pitch_retry",
    "port": "port_retry",
}
MAX_NOTE_CHARS = 2000


def revise_note(state: RunState, agent: str) -> str | None:
    note = (state.get(REVISE_KEY) or {}).get(agent)
    return note.strip() or None if isinstance(note, str) else None


def clear_note(state: RunState, agent: str) -> dict[str, Any]:
    """State update that removes `agent`'s note; empty when the note belongs to nobody (or someone else)."""
    return {REVISE_KEY: None} if agent in (state.get(REVISE_KEY) or {}) else {}


def note_block(note: str | None) -> str:
    if not note:
        return ""
    return (
        "\n\nThe owner reviewed the previous version and asks for these changes. Apply them, and keep "
        f"everything else that is already right:\n{note}"
    )
