import json
import re
import zipfile

import pytest

from poc_studio.share import export, page
from poc_studio.share.export import ShareBlocked, build_share_zip
from tests.share.conftest import run_dir, seed_run


def _names(path) -> list[str]:  # noqa: ANN001
    with zipfile.ZipFile(path) as zf:
        return zf.namelist()


@pytest.mark.browser
def test_zip_has_all_four_files_and_a_real_pdf(env) -> None:
    run_id = seed_run()
    target = build_share_zip(run_id)
    assert target == run_dir(run_id) / "share" / f"{target.name}"
    assert target.name.endswith("-share.zip")
    assert _names(target) == ["index.html", "deck.html", "walkthrough.mp4", "summary.pdf"]
    with zipfile.ZipFile(target) as zf:
        assert zf.read("summary.pdf").startswith(b"%PDF-")


def test_index_is_self_contained(env) -> None:
    run_id = seed_run(pain_points=["Weekly numbers are scattered, see http://example.org/x for more"])
    target = build_share_zip(run_id)
    with zipfile.ZipFile(target) as zf:
        index = zf.read("index.html").decode()
    assert page.external_refs(index) == []
    assert not re.search(r"""(?:src|href|poster)\s*=\s*["']\s*(?:https?:)?//""", index)
    assert '<video class="player" controls' in index
    assert 'src="walkthrough.mp4"' in index
    assert 'href="deck.html"' in index
    assert "What we heard" in index
    assert "Pilot:" in index
    assert re.search(r"expires on \d{1,2} \w+ \d{4}", index)


def test_external_assets_are_refused() -> None:
    bad = '<img src="https://cdn.example.org/a.png"><div style="background:url(http://x/y.png)"></div>'
    assert page.external_refs(bad)
    assert page.external_refs('<a href="deck.html">x</a><video src="walkthrough.mp4"></video>') == []


def test_planted_secret_blocks_the_export(env) -> None:
    token = "ghp_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8"
    run_id = seed_run(pain_points=[f"Our token is {token}"])
    with pytest.raises(ShareBlocked) as caught:
        build_share_zip(run_id)
    assert token not in str(caught.value)
    assert not list((run_dir(run_id) / "share").glob("*.zip"))


def test_secret_in_deck_blocks_too(env) -> None:
    token = "ghp_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8"
    run_id = seed_run(deck=f"<html><body>{token}</body></html>")
    with pytest.raises(ShareBlocked):
        build_share_zip(run_id)


def test_stakeholder_names_pass_and_foreign_email_is_a_warning(env) -> None:
    run_id = seed_run(
        pain_points=["Alice Smith and Bob Jones lose hours to this", "Write to jane@acme-corp.io"]
    )
    target = build_share_zip(run_id)  # no exception: PII is a warning
    manifest = json.loads((run_dir(run_id) / "share" / "manifest.json").read_text(encoding="utf-8"))
    assert any(w.startswith("email in index.html") for w in manifest["warnings"])
    assert not any("Alice" in w or "Bob" in w for w in manifest["warnings"])
    assert "manifest.json" not in _names(target)


def test_stakeholder_own_address_is_allowed(env) -> None:
    run_id = seed_run(pain_points=["Reach alice.smith@acme-corp.io"])
    build_share_zip(run_id)
    manifest = json.loads((run_dir(run_id) / "share" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["warnings"] == []


def test_no_video_means_no_mp4_and_no_player(env) -> None:
    run_id = seed_run(video=False)
    target = build_share_zip(run_id)
    assert "walkthrough.mp4" not in _names(target)
    with zipfile.ZipFile(target) as zf:
        assert "<video" not in zf.read("index.html").decode()


def test_export_is_recorded_once_per_path(env) -> None:
    from sqlalchemy import select

    from poc_studio.db.models import Artifact
    from poc_studio.db.session import open_session

    run_id = seed_run()
    build_share_zip(run_id)
    build_share_zip(run_id)
    with open_session() as s:
        rows = s.scalars(
            select(Artifact).where(Artifact.run_id == run_id, Artifact.type == "share_export")
        ).all()
    assert len(rows) == 1 and rows[0].sha256


def test_pdf_failure_is_a_warning_not_a_crash(env, monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(html: str, out) -> None:  # noqa: ANN001
        raise RuntimeError("no chromium")

    monkeypatch.setattr(export, "render_pdf", boom)
    run_id = seed_run()
    target = build_share_zip(run_id)
    assert "summary.pdf" not in _names(target)
    manifest = json.loads((run_dir(run_id) / "share" / "manifest.json").read_text(encoding="utf-8"))
    assert any("summary.pdf was not made" in w for w in manifest["warnings"])
