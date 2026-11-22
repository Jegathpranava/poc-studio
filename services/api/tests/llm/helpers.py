from pydantic import BaseModel

from poc_studio.llm.provider import ChatReply


class Answer(BaseModel):
    answer: str


class FakeProvider:
    """Replies in order (last one repeats) and records every call."""

    def __init__(self, replies: list[str], tokens: tuple[int, int] = (10, 5)) -> None:
        self.replies = replies
        self.tokens = tokens
        self.calls: list[list[dict[str, str]]] = []

    async def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        max_tokens: int,
        timeout: float,
        agent: str | None = None,
    ) -> ChatReply:
        self.calls.append([dict(m) for m in messages])
        text = self.replies[min(len(self.calls) - 1, len(self.replies) - 1)]
        return ChatReply(text, *self.tokens)
