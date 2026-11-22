import os

import pytest

from poc_studio.config import Settings
from poc_studio.llm import RunBudget, complete_json
from poc_studio.llm.provider import GatewayProvider
from tests.llm.helpers import Answer

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(os.environ.get("EVAL_LIVE") != "1", reason="set EVAL_LIVE=1"),
]


async def test_fast_model_live() -> None:
    settings = Settings()  # pyright: ignore[reportCallIssue]
    res = await complete_json(
        agent="live",
        model="fast",
        system="Answer briefly.",
        user='Reply with {"answer": "pong"}.',
        schema=Answer,
        max_tokens=100,
        run=RunBudget("r_live00", 0.05),
        provider=GatewayProvider(settings),
    )
    print(f"model={res.model} tokens_in={res.tokens_in} tokens_out={res.tokens_out} cost=${res.cost_usd}")
    assert res.value.answer
