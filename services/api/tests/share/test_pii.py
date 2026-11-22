from fastapi.testclient import TestClient

from poc_studio.llm import client as llm_client
from poc_studio.llm.provider import MockProvider
from poc_studio.pii import mask_pii, run_masks_pii, write_run_options
from tests.graph.conftest import wait_status


def test_masks_emails_and_phones() -> None:
    text = "Mail jane@acme-corp.io or call +1 415 555 0132 and +44 20 7946 0958 today."
    out = mask_pii(text, [])
    assert "[email]" in out and "[phone]" in out
    assert "acme-corp" not in out and "415" not in out and "7946" not in out


def test_keeps_example_com_names_and_timestamps() -> None:
    text = "[00:01:23] Alice Smith: write to demo@example.com on 2026-11-22"
    assert mask_pii(text, []) == text


def test_keeps_a_stakeholders_own_address_only_when_named() -> None:
    text = "alice.smith@acme-corp.io"
    assert mask_pii(text, ["Alice Smith"]) == text
    assert mask_pii(text, []) == "[email]"


def test_run_option_roundtrip(env) -> None:
    assert run_masks_pii("r_aaaaaa") is False
    write_run_options("r_aaaaaa", mask=True)
    assert run_masks_pii("r_aaaaaa") is True
    write_run_options("r_aaaaaa", mask=False)
    assert run_masks_pii("r_aaaaaa") is False


class Recorder:
    def __init__(self) -> None:
        self.inner = MockProvider()
        self.prompts: list[str] = []

    async def chat(self, model, messages, max_tokens, timeout, agent=None):  # noqa: ANN001, ANN201
        self.prompts.append("\n".join(m["content"] for m in messages))
        return await self.inner.chat(model, messages, max_tokens, timeout, agent)


def _run_with(client: TestClient, mask: str | None, data: bytes) -> str:
    form = {"client": "Acme", "sector": "logistics"}
    if mask is not None:
        form["mask_pii"] = mask
    res = client.post("/api/runs", files=[("files", ("call.txt", data, "text/plain"))], data=form)
    assert res.status_code == 201, res.text
    return res.json()["id"]


TRANSCRIPT = (
    b"Alice Smith: We need a dashboard for weekly sales.\n"
    b"Alice Smith: Reach me at jane.private@acme-corp.io or +1 415 555 0132 about it.\n"
)


def test_intelligence_sends_a_masked_prompt_when_the_option_is_on(client_for) -> None:
    recorder = Recorder()
    llm_client.set_provider(recorder)  # type: ignore[arg-type]
    try:
        with client_for() as client:
            run_id = _run_with(client, "true", TRANSCRIPT)
            wait_status(client, run_id, "waiting_gate1")
    finally:
        llm_client.set_provider(None)
    prompt = next(p for p in recorder.prompts if "Meeting Intelligence" in p)
    assert "jane.private" not in prompt and "415 555" not in prompt
    assert "[email]" in prompt and "[phone]" in prompt
    assert "Alice Smith" in prompt  # names stay in v1


def test_intelligence_is_unmasked_by_default(client_for) -> None:
    recorder = Recorder()
    llm_client.set_provider(recorder)  # type: ignore[arg-type]
    try:
        with client_for() as client:
            run_id = _run_with(client, None, TRANSCRIPT)
            wait_status(client, run_id, "waiting_gate1")
    finally:
        llm_client.set_provider(None)
    prompt = next(p for p in recorder.prompts if "Meeting Intelligence" in p)
    assert "jane.private@acme-corp.io" in prompt
