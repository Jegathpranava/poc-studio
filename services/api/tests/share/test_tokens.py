from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from poc_studio.db.models import ShareToken
from poc_studio.db.session import open_session
from poc_studio.share import tokens
from tests.share.conftest import DECK, seed_run


def test_token_is_stored_hashed_only(client) -> None:
    run_id = seed_run()
    res = client.post(f"/api/share/{run_id}")
    assert res.status_code == 200, res.text
    body = res.json()
    token = body["token"]
    assert len(token) >= 32 and body["path"] == f"/share/{token}"
    with open_session() as s:
        rows = s.scalars(select(ShareToken)).all()
    assert [r.token_hash for r in rows if r.run_id == run_id] == [tokens.hash_token(token)]
    assert all(token not in r.token_hash and r.token_hash != token for r in rows)
    expires = datetime.fromisoformat(body["expires_at"])
    assert timedelta(days=29) < expires - datetime.now(UTC) <= timedelta(days=30)


def test_public_json(client) -> None:
    run_id = seed_run(pain_points=["Numbers are scattered"])
    token = client.post(f"/api/share/{run_id}").json()["token"]
    res = client.get(f"/api/share/t/{token}")
    assert res.status_code == 200
    body = res.json()
    assert body["client"] == "Acme"
    assert body["pain_points"] == ["Numbers are scattered"]
    assert body["pilot"].startswith("Pilot:")
    assert body["video_url"] == f"/api/share/t/{token}/video"
    assert body["deck_url"] == f"/api/share/t/{token}/deck.html"
    assert "requirements" not in res.text and run_id not in res.text


def test_bad_token_is_404(client) -> None:
    for path in ("", "/video", "/deck.html"):
        assert client.get(f"/api/share/t/not-a-token{path}").status_code == 404


def test_expired_token_is_404_on_a_fake_clock(client, monkeypatch: pytest.MonkeyPatch) -> None:
    run_id = seed_run()
    token = client.post(f"/api/share/{run_id}").json()["token"]
    assert client.get(f"/api/share/t/{token}").status_code == 200
    later = datetime.now(UTC) + timedelta(days=31)
    monkeypatch.setattr(tokens, "clock", lambda: later)
    assert client.get(f"/api/share/t/{token}").status_code == 404
    assert client.get(f"/api/share/t/{token}/video").status_code == 404
    assert client.get(f"/api/share/t/{token}/deck.html").status_code == 404


def test_video_and_deck_need_a_valid_token(client) -> None:
    run_id = seed_run()
    token = client.post(f"/api/share/{run_id}").json()["token"]
    video = client.get(f"/api/share/t/{token}/video")
    assert video.status_code == 200 and video.headers["content-type"] == "video/mp4"
    deck = client.get(f"/api/share/t/{token}/deck.html")
    assert deck.status_code == 200 and deck.text == DECK
    assert "default-src 'none'" in deck.headers["content-security-policy"]
    assert client.get(f"/api/share/t/{token}x/deck.html").status_code == 404


def test_run_must_be_delivered_or_at_gate2_with_a_deck(client) -> None:
    assert client.post(f"/api/share/{seed_run('running')}").status_code == 409
    assert client.post(f"/api/share/{seed_run('waiting_gate1')}").status_code == 409
    assert client.post(f"/api/share/{seed_run('waiting_gate2', deck=None)}").status_code == 409
    assert client.post(f"/api/share/{seed_run('waiting_gate2')}").status_code == 200
    assert client.post("/api/share/r_ffffff").status_code == 404


def test_share_export_route_and_download(client) -> None:
    run_id = seed_run()
    assert client.get(f"/api/runs/{run_id}/share-export/download").status_code == 404
    res = client.post(f"/api/runs/{run_id}/share-export")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["download_url"] == f"/api/runs/{run_id}/share-export/download"
    assert client.get(f"/api/share/t/{body['share_token']}").status_code == 200
    zipped = client.get(body["download_url"])
    assert zipped.status_code == 200 and zipped.content[:2] == b"PK"
    assert client.post(f"/api/runs/{seed_run('running')}/share-export").status_code == 409


def test_share_export_with_a_secret_is_422_without_the_value(client) -> None:
    token = "ghp_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8"
    run_id = seed_run(pain_points=[token])
    res = client.post(f"/api/runs/{run_id}/share-export")
    assert res.status_code == 422 and token not in res.text
