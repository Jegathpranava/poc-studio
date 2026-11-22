"""Node registry. Each agent module exposes `NODE = NodeSpec(name, fn, owner_agent)`.

To add an agent, append its module path to `AGENT_MODULES`. Its NODE replaces the stub of the same name.
`graph/build.py` is never edited for that.
"""

import importlib
from dataclasses import dataclass
from typing import Any, Protocol

from poc_studio.graph.state import RunState


class NodeFn(Protocol):
    async def __call__(self, state: RunState) -> dict[str, Any]: ...


# Spec 7b order. pitch and port run in parallel after screens.
STAGES: tuple[str, ...] = (
    "intake", "intelligence", "gate1", "architect", "screens", "pitch", "port",
    "assemble", "qa", "gate2", "video", "repo",
)  # fmt: skip

# The one place to extend: modules that define `NODE`.
AGENT_MODULES: tuple[str, ...] = (
    "poc_studio.agents.intelligence",
    "poc_studio.agents.architect",
    "poc_studio.agents.screens",
    "poc_studio.agents.port",
    "poc_studio.agents.pitch",
    "poc_studio.agents.assemble",
    "poc_studio.agents.qa",
    "poc_studio.agents.video",
)


@dataclass(frozen=True)
class NodeSpec:
    name: str
    fn: NodeFn
    owner_agent: str


def collect_nodes(modules: tuple[str, ...] | None = None) -> dict[str, NodeSpec]:
    """Built-in nodes and stubs, overridden by each module's NODE. Every stage ends up with a node."""
    from poc_studio.graph.nodes import builtin_nodes

    nodes = {spec.name: spec for spec in builtin_nodes()}
    for module_path in AGENT_MODULES if modules is None else modules:
        spec = getattr(importlib.import_module(module_path), "NODE", None)
        if not isinstance(spec, NodeSpec):
            raise TypeError(f"{module_path} has no NODE = NodeSpec(...)")
        if spec.name not in STAGES:
            raise ValueError(f"{module_path}: unknown node {spec.name!r}")
        nodes[spec.name] = spec
    missing = [s for s in STAGES if s not in nodes]
    if missing:
        raise RuntimeError(f"no node for stages {missing}")
    return nodes
