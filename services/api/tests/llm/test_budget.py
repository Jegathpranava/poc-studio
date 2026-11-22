import pytest

from poc_studio.llm import BudgetExceeded, InputTooLarge, RunBudget, complete_json
from poc_studio.llm.pricing import cost_usd
from tests.llm.helpers import Answer, FakeProvider


def test_free_models_cost_zero() -> None:
    for m in ("fast", "smart", "vision", "embed", "guard"):
        assert cost_usd(m, 1_000_000, 1_000_000) == 0.0


def test_claude_cost_nonzero() -> None:
    assert cost_usd("claude-haiku-5-5", 1_000_000, 0) > 0


async def test_over_budget_raises_before_any_call() -> None:
    fake = FakeProvider(['{"answer": "x"}'])
    run = RunBudget("r_000001", limit_usd=0.0001)
    with pytest.raises(BudgetExceeded) as ei:
        await complete_json(
            agent="a",
            model="claude-haiku-5-5",
            system="s",
            user="hello",
            schema=Answer,
            max_tokens=4000,
            run=run,
            provider=fake,
        )
    assert ei.value.needed_usd > ei.value.remaining_usd
    assert fake.calls == []


async def test_free_model_ignores_budget() -> None:
    fake = FakeProvider(['{"answer": "x"}'])
    run = RunBudget("r_000001", limit_usd=0.0)
    res = await complete_json(
        agent="a",
        model="fast",
        system="s",
        user="hi",
        schema=Answer,
        max_tokens=4000,
        run=run,
        provider=fake,
    )
    assert res.cost_usd == 0.0 and run.spent_usd == 0.0


def test_claude_input_over_12k_tokens() -> None:
    run = RunBudget("r_000001", limit_usd=10.0)
    with pytest.raises(InputTooLarge):
        run.estimate("claude-haiku-5-5", "word " * 13_000, 100)
    run.estimate("fast", "word " * 13_000, 100)  # free models are not capped


async def test_paid_call_is_charged() -> None:
    fake = FakeProvider(['{"answer": "x"}'], tokens=(1000, 500))
    run = RunBudget("r_000001", limit_usd=1.0)
    res = await complete_json(
        agent="a",
        model="claude-haiku-5-5",
        system="s",
        user="hi",
        schema=Answer,
        max_tokens=500,
        run=run,
        provider=fake,
    )
    assert res.cost_usd == pytest.approx(cost_usd("claude-haiku-5-5", 1000, 500))
    assert run.spent_usd == pytest.approx(res.cost_usd)
