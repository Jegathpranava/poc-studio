import json

import pytest

from poc_studio.db.models import Event
from poc_studio.db.session import open_session
from poc_studio.events import emit
from poc_studio.redact import MASK, redact
from tests.graph.conftest import create_run, wait_status


def parse_sse(text: str) -> list[dict[str, str]]:
    out = []
    for block in text.replace("\r\n", "\n").split("\n\n"):
        fields = dict(line.split(": ", 1) for line in block.split("\n") if ": " in line)
        if "id" in fields:
            out.append(fields)
    return out


def test_sse_replays_after_last_event_id(client_for) -> None:
    with client_for() as client:
        run_id = create_run(client)
        wait_status(client, run_id, "waiting_gate1")
        url = f"/api/runs/{run_id}/events?follow=false"
        everything = parse_sse(client.get(url).text)
        ids = [int(e["id"]) for e in everything]
        assert len(ids) > 4 and ids == sorted(ids)

        replay = parse_sse(client.get(url, headers={"Last-Event-ID": "3"}).text)
        assert [int(e["id"]) for e in replay] == [i for i in ids if i > 3]
        assert int(replay[0]["id"]) == 4

        assert {e["event"] for e in everything} == {"step", "run"}
        first = json.loads(everything[0]["data"])
        assert first["run_id"] == run_id and first["kind"] == "status"
        assert client.get("/api/runs/r_000000/events").status_code == 404


def test_event_with_github_token_is_stored_redacted(client_for) -> None:
    token = "gh" + "p_" + "a1B2c3D4e5" * 3 + "xyz123"  # the prefix plus 36 characters
    assert len(token) == 40
    with client_for() as client:
        run_id = create_run(client)
        wait_status(client, run_id, "waiting_gate1")
        emit(run_id, "repo", "log", message=f"pushing with {token}", error={"message": f"bad {token}"})
        with open_session() as session:
            row = session.query(Event).filter(Event.run_id == run_id).order_by(Event.id.desc()).first()
            assert row is not None
            assert token not in row.message and MASK in row.message
            assert row.data is not None and token not in row.data
        assert token not in client.get(f"/api/runs/{run_id}/events?follow=false").text


# Built from pieces so that no real-looking secret sits in the source.
SECRETS = [
    "gh" + "o_" + "x" * 36,
    "github" + "_pat_" + "A1b2C3d4E5" * 6,
    "s" + "k-" + "abcdEFGH1234" * 3,
    "s" + "k-proj-" + "abcdEFGH1234" * 3,
    "AK" + "IA" + "IOSFODNN7EXAMPLE",
    "xo" + "xb-" + "1234567890-abcdefghij",
    "-----BEGIN " + "RSA PRIVATE KEY-----\nMIIEow\nabc\n-----END " + "RSA PRIVATE KEY-----",
    "ey" + "JhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTYifQ.SflKxwRJSMeKKF2QT4fw",
]


@pytest.mark.parametrize("secret", SECRETS)
def test_redact_masks_known_patterns(secret: str) -> None:
    assert redact(f"before {secret} after") == f"before {MASK} after"


def test_redact_key_values_and_clean_text() -> None:
    assert redact("password=hunter2 ok") == f"password={MASK} ok"
    assert redact('config api_key = "abc 123" end') == f"config api_key = {MASK} end"
    assert redact("Parsed 1 file(s): 12 segments") == "Parsed 1 file(s): 12 segments"
