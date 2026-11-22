"""QA routing (spec 7b): which agent, if any, a failed check sends the run back to.

`decide` returns `{"send_back": "pitch" | "screens" | "port" | None, "block_publish": bool}`. The graph edge
`after_qa` (graph/build.py) reads the agent name from state key `qa_send_back` and stops at MAX_SEND_BACKS,
and it sends "port" and "pitch" back alone through `port_retry` / `pitch_retry`, then on to assemble.
"""

from typing import TypedDict

from poc_studio.graph.build import MAX_SEND_BACKS
from poc_studio.qa.checks import Check

SEND_BACK_OWNERS = ("pitch", "screens")
SECRETS_CHECK = "no_secrets"


class Decision(TypedDict):
    send_back: str | None
    block_publish: bool


def decide(checks: list[Check], sent_back_count: int) -> Decision:
    failing = [c for c in checks if not c.ok and not c.report_only]
    block = any(c.name == SECRETS_CHECK and not c.ok for c in checks)
    if sent_back_count >= MAX_SEND_BACKS:
        return {"send_back": None, "block_publish": block}
    for c in failing:  # check order is the priority order
        if c.owner_agent in SEND_BACK_OWNERS or (c.name == SECRETS_CHECK and c.owner_agent == "port"):
            return {"send_back": c.owner_agent, "block_publish": block}
    return {"send_back": None, "block_publish": block}
