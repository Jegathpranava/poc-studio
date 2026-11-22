"""Chat providers: the gateway (OpenAI-compatible) and a fixture-backed mock."""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from openai import omit

from poc_studio.config import Settings

FIXTURE_DIR = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "llm"


@dataclass(frozen=True)
class ChatReply:
    text: str
    tokens_in: int | None  # None when the gateway sent no `usage`; the client then uses its estimate
    tokens_out: int | None
    finish_reason: str | None = None  # "length" means the max_tokens cap cut the reply (reasoning counts)


class ChatProvider(Protocol):
    async def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        max_tokens: int,
        timeout: float,
        agent: str | None = None,
        reasoning_effort: str | None = None,
    ) -> ChatReply: ...


class GatewayProvider:
    def __init__(self, settings: Settings) -> None:
        from openai import AsyncOpenAI

        self._client = AsyncOpenAI(
            base_url=settings.openai_base_url,
            api_key=settings.openai_api_key.get_secret_value() or "unset",
            max_retries=0,  # complete_json owns retries; SDK retries tripled every timeout
        )

    async def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        max_tokens: int,
        timeout: float,
        agent: str | None = None,
        reasoning_effort: str | None = None,
    ) -> ChatReply:
        resp = await self._client.chat.completions.create(
            model=model,
            messages=messages,  # pyright: ignore[reportArgumentType]
            max_tokens=max_tokens,
            timeout=timeout,
            reasoning_effort=omit if reasoning_effort is None else reasoning_effort,  # pyright: ignore[reportArgumentType]
        )
        usage = resp.usage
        return ChatReply(
            text=resp.choices[0].message.content or "",
            tokens_in=usage.prompt_tokens if usage else None,
            tokens_out=usage.completion_tokens if usage else None,
            finish_reason=resp.choices[0].finish_reason,
        )


_PROMPT_KIT = re.compile(r"app_class `([^`]+)`; accent `([^`]+)`")
_PROMPT_CLIENT = re.compile(r"^Client: (.+?)\. Accent colour", re.MULTILINE)
_PROMPT_CSS = re.compile(r"```css\n(.*?)\n```", re.DOTALL)
_ICON_CLASS = re.compile(r" ic-[\w-]+")


def _reskin_screens(pack: dict[str, Any], kit: tuple[str, str, str]) -> dict[str, Any]:
    """The canned ScreenPack is the logistics one. When the prompt named another sector kit (the owner picked
    the sector), swap in that kit's app class, accent and CSS so the reply still validates. Mock only."""
    app_class, accent, kit_css = kit
    old = str(pack["app_class"])
    if app_class == old:
        return pack

    def rename(text: str) -> str:
        return text.replace(f".{old}", f".{app_class}").replace(f'class="{old}"', f'class="{app_class}"')

    out = dict(pack, app_class=app_class, accent=accent)
    out["product_css"] = kit_css + "\n" + rename(str(pack["product_css"]))  # the kit, plus the canned extras
    out["step_css"] = rename(str(pack.get("step_css", "")))
    out["screens"] = [dict(sc, html=_ICON_CLASS.sub("", rename(str(sc["html"])))) for sc in pack["screens"]]
    return out


class MockProvider:
    """Canned replies from tests/fixtures/llm/<agent>.json: an object (always) or a list (in order)."""

    def __init__(self, fixture_dir: Path = FIXTURE_DIR) -> None:
        self._dir = fixture_dir
        self._calls: dict[str, int] = {}
        self._client: str | None = None
        self._kit: tuple[str, str, str] | None = (
            None  # (app_class, accent, css) of the sector kit last asked for
        )

    async def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        max_tokens: int,
        timeout: float,
        agent: str | None = None,
        reasoning_effort: str | None = None,
    ) -> ChatReply:
        name = agent or "echo"
        data: Any = json.loads((self._dir / f"{name}.json").read_text(encoding="utf-8"))
        if isinstance(data, list):
            i = self._calls.get(name, 0)
            self._calls[name] = i + 1
            data = data[min(i, len(data) - 1)]
        if name == "screens" and isinstance(data, dict):
            prompt = "\n".join(m["content"] for m in messages)
            found, css = _PROMPT_KIT.search(prompt), _PROMPT_CSS.search(prompt)
            if found and css:  # a repair prompt carries no kit: keep the last one
                self._kit = (found.group(1), found.group(2), css.group(1))
            if self._kit:
                data = _reskin_screens(data, self._kit)
        text = data if isinstance(data, str) else json.dumps(data)
        if name == "pitch":  # the canned deck names "Acme"; the owner's client name wins
            found_client = _PROMPT_CLIENT.search("\n".join(m["content"] for m in messages))
            self._client = found_client.group(1) if found_client else self._client
            if self._client and self._client != "Acme":
                text = text.replace("Acme", json.dumps(self._client)[1:-1])
        return ChatReply(text=text, tokens_in=0, tokens_out=0)


def get_provider(settings: Settings) -> ChatProvider:
    if settings.llm_provider == "gateway":
        return GatewayProvider(settings)
    return MockProvider()
