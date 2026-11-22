from poc_studio.llm import RunBudget, complete_json
from poc_studio.llm.client import TRUNCATED_NOTE
from poc_studio.llm.provider import ChatReply
from tests.llm.helpers import Answer, FakeProvider

CUT_OFF = '{"answer": "' + "x" * 5000  # a reply that stopped mid-string


async def _call(fake: FakeProvider, **kw: str) -> Answer:
    res = await complete_json(
        agent="a", model="smart", system="s", user="the brief", schema=Answer,
        max_tokens=100, run=RunBudget("r_000001", 1.0), provider=fake, **kw,
    )  # fmt: skip
    return res.value


async def test_truncated_reply_is_not_echoed_back() -> None:
    fake = FakeProvider([CUT_OFF, '{"answer": "ok"}'])
    assert (await _call(fake)).answer == "ok"
    retry = fake.calls[1]
    assert [m["role"] for m in retry] == ["system", "user"]
    assert "x" * 100 not in "".join(m["content"] for m in retry)
    assert retry[1]["content"] == f"the brief\n\n{TRUNCATED_NOTE}"


async def test_caller_note_replaces_the_default() -> None:
    fake = FakeProvider([CUT_OFF, '{"answer": "ok"}'])
    await _call(fake, truncated_note="Shorter, please.")
    assert fake.calls[1][1]["content"].endswith("Shorter, please.")


async def test_retries_do_not_grow_after_repeated_truncation() -> None:
    fake = FakeProvider([CUT_OFF, CUT_OFF, '{"answer": "ok"}'])
    await _call(fake)
    assert len(fake.calls[2]) == 2 and fake.calls[2] == fake.calls[1]


async def test_other_broken_json_gets_a_short_note() -> None:
    fake = FakeProvider(['{"answer": "ok",, }', '{"answer": "ok"}'])
    await _call(fake)
    retry = fake.calls[1]
    assert len(retry) == 2 and "not parseable JSON" in retry[1]["content"]


async def test_schema_errors_still_show_the_reply_for_repair() -> None:
    fake = FakeProvider(['{"wrong": 1}', '{"answer": "ok"}'])
    await _call(fake)
    retry = fake.calls[1]
    assert [m["role"] for m in retry] == ["system", "user", "assistant", "user"]
    assert retry[2]["content"] == '{"wrong": 1}'


class EmptyThenOk(FakeProvider):
    """First reply is what the gateway sends when reasoning used the whole allowance."""

    def __init__(self) -> None:
        super().__init__(["", '{"answer": "ok"}'])
        self.efforts: list[str | None] = []

    async def chat(self, model, messages, max_tokens, timeout, agent=None, reasoning_effort=None):  # type: ignore[override]
        self.efforts.append(reasoning_effort)
        reply = await super().chat(model, messages, max_tokens, timeout, agent)
        if not reply.text:
            return ChatReply("", 1, max_tokens, "length")
        return ChatReply(reply.text, 1, 5, "stop")


async def test_empty_answer_retries_fresh_and_passes_reasoning_effort() -> None:
    fake = EmptyThenOk()
    assert (await _call(fake, reasoning_effort="low")).answer == "ok"
    assert fake.efforts == ["low", "low"]
    assert fake.calls[1][1]["content"].endswith(TRUNCATED_NOTE)


async def test_only_empty_answers_raise_a_clear_error() -> None:
    import pytest

    from poc_studio.llm import SchemaError

    with pytest.raises(SchemaError, match="empty answer \(finish_reason=None\).*100-token allowance"):
        await _call(FakeProvider([""]))
