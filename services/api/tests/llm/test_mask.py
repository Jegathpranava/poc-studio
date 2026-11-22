from poc_studio.llm import RunBudget, complete_json
from tests.llm.helpers import Answer, FakeProvider


async def test_mask_applied_to_user_text() -> None:
    fake = FakeProvider(['{"answer": "ok"}'])
    await complete_json(
        agent="a",
        model="fast",
        system="s",
        user="mail bob@example.com",
        schema=Answer,
        max_tokens=100,
        run=RunBudget("r_000001", 1.0),
        provider=fake,
        mask=lambda t: t.replace("bob@example.com", "[EMAIL]"),
    )
    assert fake.calls[0][1]["content"] == "mail [EMAIL]"
