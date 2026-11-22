"""Builds the StateGraph in the spec 7b order from the node registry.

intake -> intelligence -> gate1 -> architect -> screens -> (pitch || port) -> assemble -> qa -> gate2
-> video -> repo. Agent tasks never edit this file; they register through `graph/registry.py`.
"""

from typing import Any

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from poc_studio.graph.registry import STAGES, NodeSpec, collect_nodes
from poc_studio.graph.state import RunState

MAX_SEND_BACKS = 2  # spec 7b: a run is sent back at most twice in total


def after_gate1(state: RunState) -> str:
    gate = state.get("gate1") or {}
    return "intelligence" if gate.get("decision") == "changes" else "architect"


def after_qa(state: RunState) -> str | list[str]:
    """Send-back edge. Inert until the QA agent sets `qa_send_back`; capped at MAX_SEND_BACKS."""
    target = state.get("qa_send_back")
    if not target or state.get("sent_back_count", 0) >= MAX_SEND_BACKS:
        return "gate2"
    if target == "screens":
        return "screens"
    return ["pitch", "port"]  # the join before assemble needs both branches to run again


def after_gate2(state: RunState) -> str:
    # Revisions at Gate 2 are Task 19's; until then "changes" waits at the gate again.
    gate = state.get("gate2") or {}
    return "gate2" if gate.get("decision") == "changes" else "video"


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
    g.add_conditional_edges(
        "qa", after_qa, {"gate2": "gate2", "screens": "screens", "pitch": "pitch", "port": "port"}
    )
    g.add_conditional_edges("gate2", after_gate2, {"gate2": "gate2", "video": "video"})
    g.add_edge("video", "repo")
    g.add_edge("repo", END)
    return g.compile(checkpointer=checkpointer)
