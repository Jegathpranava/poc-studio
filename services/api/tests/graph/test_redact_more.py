import logging

import pytest

from poc_studio.redact import MASK, install_log_redaction, redact, redact_obj


@pytest.mark.parametrize(
    ("text", "secret"),
    [
        ("DB_PASSWORD=hunter2", "hunter2"),
        ('{"password": "hunter2"}', "hunter2"),
        ("Authorization: Bearer abcdef1234567890", "abcdef1234567890"),
        ("openai_api_key=zzz", "zzz"),
        ("MY-SECRET: s3cr3t!", "s3cr3t"),
    ],
)
def test_more_secret_shapes_are_masked(text: str, secret: str) -> None:
    out = redact(text)
    assert secret not in out and MASK in out


def test_dict_key_masks_whole_value() -> None:
    out = redact_obj({"password": "x", "nested": [{"api_key": {"a": 1}}], "ok": "fine", "max_tokens": 5})
    assert out["password"] == MASK
    assert out["nested"][0]["api_key"] == MASK
    assert out["ok"] == "fine" and out["max_tokens"] == 5


def test_plain_words_are_left_alone() -> None:
    assert redact("tokens: 100 and a secretary") == "tokens: 100 and a secretary"


def test_log_records_from_child_loggers_are_redacted(caplog: pytest.LogCaptureFixture) -> None:
    install_log_redaction()
    install_log_redaction()  # idempotent
    caplog.set_level(logging.INFO)
    try:
        raise RuntimeError("boom password=hunter2")
    except RuntimeError:
        logging.getLogger("poc_studio.runs.service").exception("failed %s", "DB_PASSWORD=hunter2")
    assert "hunter2" not in caplog.text and MASK in caplog.text
