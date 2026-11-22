"""Builds the StateGraph in the spec 7b order from the node registry.

intake -> intelligence -> gate1 -> architect -> screens -> (pitch || port) -> assemble -> qa -> gate2
-> video -> repo. Agent tasks never edit this file; they register through `graph/registry.py`.

QA send-backs (at most MAX_SEND_BACKS executed, then the run goes on to Gate 2 with the report):
  screens -> screens, then both branches and the join as usual
  pitch   -> pitch_retry -> assemble     (the port result stays in state; port is not re-run)
  port    -> port_retry  -> assemble     (pitch is not re-run)
Gate 2 "changes" with `revise` (Task 19) goes to architect (then the normal path), screens (then both
branches), or pitch_retry / port_retry (then assemble, QA, Gate 2 again).
`pitch_retry` and `port_retry` reuse the pitch and port functions; they exist because the
`["pitch", "port"] -> assemble` join would wait forever for the branch that did not run again.
Step rows are still written as `pitch` and `port` (the agents name their own step).
"""

from typing import Any

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from poc_studio.graph.registry import STAGES, NodeSpec, collect_nodes
from poc_studio.graph.revise import REVISE_TARGETS
from poc_studio.graph.state import RunState

MAX_SEND_BACKS = 2  # spec 7b: a run is sent back at most twice in total


def after_gate1(state: RunState) -> str:
    gate = state.get("gate1") or {}
    return "intelligence" if gate.get("decision") == "changes" else "architect"


def after_qa(state: RunState) -> str:
    """Send-back edge: the node QA named, capped at MAX_SEND_BACKS. A lone branch uses a retry node."""
    target = state.get("qa_send_back")
    if not target or state.get("sent_back_count", 0) >= MAX_SEND_BACKS:
        return "gate2"
    return {"screens": "screens", "pitch": "pitch_retry", "port": "port_retry"}.get(target, "gate2")


def after_gate2(state: RunState) -> str:
    """ "changes" with `revise` goes to the owning agent; without it the run waits at the gate again."""
    gate = state.get("gate2") or {}
    if gate.get("decision") != "changes":
        return "video"
    agent = (gate.get("edits") or {}).get("revise")
    return REVISE_TARGETS.get(agent, "gate2") if isinstance(agent, str) else "gate2"


def build_graph(
    checkpointer: BaseCheckpointSaver[Any], nodes: dict[str, NodeSpec] | None = None
) -> CompiledStateGraph[Any, Any, Any, Any]:
    nodes = nodes or collect_nodes()
    g = StateGraph(RunState)
    for name in STAGES:
        g.add_node(name, nodes[name].fn)
    g.add_edge(START, "intake")
    g.add_edge("intake", "intelligence")
    g.add_edge("intelligence", "gate1")
    g.add_conditional_edges("gate1", after_gate1, {"intelligence": "intelligence", "architect": "architect"})
    g.add_edge("architect", "screens")
    g.add_edge("screens", "pitch")
    g.add_edge("screens", "port")
    g.add_edge(["pitch", "port"], "assemble")
    g.add_edge("assemble", "qa")
    g.add_node("pitch_retry", nodes["pitch"].fn)
    g.add_node("port_retry", nodes["port"].fn)
    g.add_edge("pitch_retry", "assemble")
    g.add_edge("port_retry", "assemble")
    g.add_conditional_edges(
        "qa",
        after_qa,
        {"gate2": "gate2", "screens": "screens", "pitch_retry": "pitch_retry", "port_retry": "port_retry"},
    )
    g.add_conditional_edges(
        "gate2",
        after_gate2,
        {"gate2": "gate2", "video": "video", **{t: t for t in set(REVISE_TARGETS.values())}},
    )
    g.add_edge("video", "repo")
    g.add_edge("repo", END)
    return g.compile(checkpointer=checkpointer)
