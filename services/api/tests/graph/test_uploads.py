import pytest

from poc_studio.runs import service as svc
from poc_studio.runs.service import InvalidUpload, safe_name
from tests.graph.conftest import SAMPLE_VTT


def post(client, files: list[tuple[str, bytes]]):
    return client.post(
        "/api/runs",
        files=[("files", (n, d, "text/plain")) for n, d in files],
        data={"client": "Acme"},
    )


def test_too_many_files(client_for) -> None:
    with client_for() as client:
        res = post(client, [(f"f{i}.txt", b"hello there") for i in range(svc.MAX_FILES + 1)])
        assert res.status_code == 422 and str(svc.MAX_FILES) in res.json()["detail"]


def test_total_size_limit(client_for, monkeypatch) -> None:
    monkeypatch.setattr(svc, "MAX_TOTAL_BYTES", 100)
    with client_for() as client:
        res = post(client, [("a.txt", b"x" * 60), ("b.txt", b"y" * 60)])
        assert res.status_code == 422 and "total" in res.json()["detail"]
        assert post(client, [("a.txt", b"x" * 60)]).status_code == 201


@pytest.mark.parametrize("name", ["C:evil.txt", "notes.txt:stream"])
def test_colon_names_rejected(client_for, name: str) -> None:
    with client_for() as client:
        res = post(client, [(name, b"hello")])
        assert res.status_code == 422


def test_safe_name_compares_casefolded() -> None:
    taken: set[str] = set()
    assert safe_name("A.vtt", taken) == "A.vtt"
    assert safe_name("a.VTT", taken) == "2_a.VTT"
    with pytest.raises(InvalidUpload):
        safe_name("x\x00y", taken)
    with pytest.raises(InvalidUpload):
        safe_name("C:y.txt", taken)


def test_names_differing_by_case_both_stored(client_for, env) -> None:
    data = SAMPLE_VTT.read_bytes()
    with client_for() as client:
        res = client.post(
            "/api/runs",
            files=[("files", ("A.vtt", data, "text/vtt")), ("files", ("a.vtt", data, "text/vtt"))],
            data={"client": "Acme"},
        )
        assert res.status_code == 201
        run_id = res.json()["id"]
    names = sorted(p.name for p in (env / "runs" / run_id / "input").iterdir())
    assert len(names) == 2 and len({n.casefold() for n in names}) == 2
