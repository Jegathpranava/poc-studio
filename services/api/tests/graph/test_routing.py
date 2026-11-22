from typing import Any

from poc_studio.graph.build import MAX_SEND_BACKS, after_qa


def state(target: str | None, count: int) -> Any:
    return {"run_id": "r_000000", "qa_send_back": target, "sent_back_count": count}


def test_send_back_cap_is_at_most_two() -> None:
    assert MAX_SEND_BACKS == 2
    assert after_qa(state("screens", 0)) == "screens"
    assert after_qa(state("screens", 1)) == "screens"
    assert after_qa(state("screens", 2)) == "gate2"
    assert after_qa(state("pitch", 1)) == ["pitch", "port"]
    assert after_qa(state(None, 0)) == "gate2"
