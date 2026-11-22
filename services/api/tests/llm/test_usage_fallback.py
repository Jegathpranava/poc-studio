import pytest

from poc_studio.llm import BudgetExceeded, ChatReply, RunBudget, complete_json
from tests.llm.helpers import Answer, FakeProvider


class NoUsageProvider(FakeProvider):
    async def chat(self, model, messages, max_tokens, timeout, agent=None):  # type: ignore[override]
        reply = await super().chat(model, messages, max_tokens, timeout, agent)
        return ChatReply(reply.text, None, None)  # the gateway sent no `usage`


async def test_missing_usage_falls_back_to_the_estimate() -> None:
    run = RunBudget("r_000001", 1.0)
    res = await complete_json(
        agent="a", model="claude-haiku-5-5", system="s", user="hello", schema=Answer,
        max_tokens=100, run=run, provider=NoUsageProvider(['{"answer": "ok"}']),
    )  # fmt: skip
    assert res.cost_usd > 0 and run.spent_usd == res.cost_usd
    assert res.tokens_in > 0 and res.tokens_out == 100


async def test_charge_hook_runs_before_budget_exceeded() -> None:
    charges: list[float] = []
    run = RunBudget("r_000001", 8e-5, on_charge=charges.append)
    fake = FakeProvider(['{"wrong": "' + "word " * 300 + '"}'], tokens=(10, 5))  # echoed back
    with pytest.raises(BudgetExceeded):
        await complete_json(
            agent="a", model="claude-haiku-5-5", system="s", user="hi", schema=Answer,
            max_tokens=100, run=run, provider=fake,
        )  # fmt: skip
    assert len(charges) == 1 and charges[0] > 0
