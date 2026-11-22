"""Chat providers: the gateway (OpenAI-compatible) and a fixture-backed mock."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from poc_studio.config import Settings

FIXTURE_DIR = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "llm"


@dataclass(frozen=True)
class ChatReply:
    text: str
    tokens_in: int | None  # None when the gateway sent no `usage`; the client then uses its estimate
    tokens_out: int | None


class ChatProvider(Protocol):
    async def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        max_tokens: int,
        timeout: float,
        agent: str | None = None,
    ) -> ChatReply: ...


class GatewayProvider:
    def __init__(self, settings: Settings) -> None:
        from openai import AsyncOpenAI

        self._client = AsyncOpenAI(
            base_url=settings.openai_base_url,
            api_key=settings.openai_api_key.get_secret_value() or "unset",
        )

    async def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        max_tokens: int,
        timeout: float,
        agent: str | None = None,
    ) -> ChatReply:
        resp = await self._client.chat.completions.create(
            model=model,
            messages=messages,  # pyright: ignore[reportArgumentType]
            max_tokens=max_tokens,
            timeout=timeout,
        )
        usage = resp.usage
        return ChatReply(
            text=resp.choices[0].message.content or "",
            tokens_in=usage.prompt_tokens if usage else None,
            tokens_out=usage.completion_tokens if usage else None,
        )


class MockProvider:
    """Canned replies from tests/fixtures/llm/<agent>.json: an object (always) or a list (in order)."""

    def __init__(self, fixture_dir: Path = FIXTURE_DIR) -> None:
        self._dir = fixture_dir
        self._calls: dict[str, int] = {}

    async def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        max_tokens: int,
        timeout: float,
        agent: str | None = None,
    ) -> ChatReply:
        name = agent or "echo"
        data: Any = json.loads((self._dir / f"{name}.json").read_text(encoding="utf-8"))
        if isinstance(data, list):
            i = self._calls.get(name, 0)
            self._calls[name] = i + 1
            data = data[min(i, len(data) - 1)]
        text = data if isinstance(data, str) else json.dumps(data)
        return ChatReply(text=text, tokens_in=0, tokens_out=0)


def get_provider(settings: Settings) -> ChatProvider:
    if settings.llm_provider == "gateway":
        return GatewayProvider(settings)
    return MockProvider()
