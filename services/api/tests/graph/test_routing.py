from typing import Any

from poc_studio.graph.build import MAX_SEND_BACKS, after_qa


def state(target: str | None, count: int) -> Any:
    return {"run_id": "r_000000", "qa_send_back": target, "sent_back_count": count}


def test_send_back_cap_is_at_most_two() -> None:
    assert MAX_SEND_BACKS == 2
    assert after_qa(state("screens", 0)) == "screens"
    assert after_qa(state("screens", 1)) == "screens"
    assert after_qa(state("screens", 2)) == "gate2"
    assert after_qa(state("pitch", 1)) == "pitch_retry"
    assert after_qa(state("port", 1)) == "port_retry"
    assert after_qa(state(None, 0)) == "gate2"


def test_default_app_has_no_stub_nodes() -> None:
    from poc_studio.graph.registry import STAGES, collect_nodes

    nodes = collect_nodes()
    assert set(nodes) == set(STAGES)
    for name, spec in nodes.items():
        assert spec.name == name
        assert spec.owner_agent != "test"
        assert spec.fn.__module__.startswith("poc_studio."), name
        assert spec.fn.__module__ != "poc_studio.graph.nodes" or name in {"intake", "gate1", "gate2"}, name
