from poc_studio.config import Settings, get_settings
from poc_studio.llm import RunBudget, complete_json
from poc_studio.llm.provider import GatewayProvider
from tests.llm.helpers import Answer, FakeProvider


class TimeoutRecorder(FakeProvider):
    def __init__(self) -> None:
        super().__init__(['{"answer": "ok"}'])
        self.timeouts: list[float] = []

    async def chat(self, model, messages, max_tokens, timeout, agent=None):  # type: ignore[override]
        self.timeouts.append(timeout)
        return await super().chat(model, messages, max_tokens, timeout, agent)


async def _call(prov: TimeoutRecorder, timeout: float | None = None) -> None:
    await complete_json(
        agent="a", model="smart", system="s", user="hi", schema=Answer,
        max_tokens=10, run=RunBudget("r_000001", 1.0), provider=prov, timeout=timeout,
    )  # fmt: skip


async def test_timeout_defaults_to_settings() -> None:
    prov = TimeoutRecorder()
    await _call(prov)
    assert prov.timeouts == [get_settings().llm_timeout_s]


async def test_explicit_timeout_wins() -> None:
    prov = TimeoutRecorder()
    await _call(prov, timeout=12.5)
    assert prov.timeouts == [12.5]


def test_setting_defaults_to_300_and_reads_env(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.delenv("LLM_TIMEOUT_S", raising=False)
    assert Settings(_env_file=None).llm_timeout_s == 300.0  # pyright: ignore[reportCallIssue]
    monkeypatch.setenv("LLM_TIMEOUT_S", "45")
    assert Settings(_env_file=None).llm_timeout_s == 45.0  # pyright: ignore[reportCallIssue]


def test_gateway_sdk_does_not_retry() -> None:
    prov = GatewayProvider(Settings(_env_file=None))  # pyright: ignore[reportCallIssue]
    assert prov._client.max_retries == 0  # pyright: ignore[reportPrivateUsage]
