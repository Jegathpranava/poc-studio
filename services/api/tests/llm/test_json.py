import pytest

from poc_studio.llm import Result, RunBudget, SchemaError, complete_json, wrap_untrusted
from poc_studio.llm.provider import MockProvider
from tests.llm.helpers import Answer, FakeProvider


def _run() -> RunBudget:
    return RunBudget("r_000001", limit_usd=1.0)


async def _call(fake: FakeProvider) -> Result[Answer]:
    return await complete_json(
        agent="a",
        model="fast",
        system="s",
        user="u",
        schema=Answer,
        max_tokens=100,
        run=_run(),
        provider=fake,
    )


async def test_repair_on_second_attempt() -> None:
    fake = FakeProvider(["not json", '{"answer": "ok"}'])
    res = await _call(fake)
    assert res.value.answer == "ok" and res.attempts == 2
    assert "Validation error" in fake.calls[1][-1]["content"]


async def test_three_invalid_raise() -> None:
    fake = FakeProvider(["bad", "{}", '{"answer": 1}'])
    with pytest.raises(SchemaError):
        await _call(fake)
    assert len(fake.calls) == 3


async def test_fenced_reply_parses() -> None:
    res = await _call(FakeProvider(['```json\n{"answer": "ok"}\n```']))
    assert res.value.answer == "ok" and res.attempts == 1


async def test_schema_in_system_prompt() -> None:
    fake = FakeProvider(['{"answer": "ok"}'])
    await _call(fake)
    assert '"answer"' in fake.calls[0][0]["content"]


async def test_mock_provider_fixture() -> None:
    res = await complete_json(
        agent="echo",
        model="fast",
        system="s",
        user="u",
        schema=Answer,
        max_tokens=100,
        run=_run(),
        provider=MockProvider(),
    )
    assert res.value.answer == "ok"


def test_wrap_untrusted() -> None:
    out = wrap_untrusted("ignore previous")
    assert "<untrusted>ignore previous</untrusted>" in out
    assert "data" in out.lower()
