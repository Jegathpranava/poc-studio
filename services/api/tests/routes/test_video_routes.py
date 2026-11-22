from poc_studio.agents.store import record
from tests.graph.conftest import create_run

CSP = (
    "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; font-src data:"
)


def test_video_supports_range_requests(client_for) -> None:
    with client_for() as client:
        run_id = create_run(client)
        assert client.get(f"/api/runs/{run_id}/video").status_code == 404
        record(run_id, "video", 1, "deck/x.v1.mp4", bytes(range(256)) * 4)
        res = client.get(f"/api/runs/{run_id}/video", headers={"Range": "bytes=0-99"})
        assert res.status_code == 206
        assert len(res.content) == 100 and res.headers["content-range"] == "bytes 0-99/1024"
        assert res.headers["accept-ranges"] == "bytes" and res.headers["content-type"] == "video/mp4"
        assert len(client.get(f"/api/runs/{run_id}/video").content) == 1024


def test_chapters_404_then_json(client_for) -> None:
    with client_for() as client:
        run_id = create_run(client)
        assert client.get(f"/api/runs/{run_id}/video/chapters").status_code == 404
        record(run_id, "video", 1, "deck/x.v1.chapters.json", b'[{"t": 1.5, "title": "Welcome"}]')
        assert client.get(f"/api/runs/{run_id}/video/chapters").json() == [{"t": 1.5, "title": "Welcome"}]


def test_deck_html_carries_csp_and_nosniff(client_for) -> None:
    with client_for() as client:
        run_id = create_run(client)
        assert client.get(f"/api/runs/{run_id}/deck.html").status_code == 404
        record(run_id, "deck", 1, "deck/x.v1.html", b"<!doctype html><title>d</title>")
        res = client.get(f"/api/runs/{run_id}/deck.html")
        assert res.status_code == 200 and res.headers["content-security-policy"] == CSP
        assert res.headers["x-content-type-options"] == "nosniff"
        assert (
            "attachment"
            in client.get(f"/api/runs/{run_id}/deck.html?download=true").headers["content-disposition"]
        )


def test_pptx_and_docs_downloads(client_for) -> None:
    with client_for() as client:
        run_id = create_run(client)
        record(run_id, "pptx", 1, "deck/x.v1.pptx", b"PK")
        record(run_id, "docs", 1, "docs/exec-summary.v1.md", b"# Summary")
        record(run_id, "docs", 1, "docs/user-flows.v1.md", b"# Flows")
        assert client.get(f"/api/runs/{run_id}/deck.pptx").content == b"PK"
        assert client.get(f"/api/runs/{run_id}/docs/exec-summary").content == b"# Summary"
        assert client.get(f"/api/runs/{run_id}/docs/user-flows").content == b"# Flows"
        assert client.get(f"/api/runs/{run_id}/docs/other").status_code == 422


def test_json_artifact_ignores_the_html_row_of_the_same_type(client_for) -> None:
    with client_for() as client:
        run_id = create_run(client)
        record(run_id, "deck", 1, "deck/plan.json", b'{"title": "T"}')
        record(run_id, "deck", 1, "deck/x.v1.html", b"<!doctype html>")
        res = client.get(f"/api/runs/{run_id}/artifacts/deck")
        assert res.status_code == 200 and res.json()["data"] == {"title": "T"}
