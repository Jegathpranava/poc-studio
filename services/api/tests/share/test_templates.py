import json

from poc_studio.config import get_settings
from tests.share.conftest import run_dir, seed_run


def _build(run_id: str, ok: bool, attempts: int) -> None:
    (run_dir(run_id)).mkdir(parents=True, exist_ok=True)
    (run_dir(run_id) / "build.json").write_text(
        json.dumps({"ok": ok, "attempts": attempts}), encoding="utf-8"
    )


def test_stats_come_from_the_runs(client) -> None:
    a = seed_run(sector="logistics")
    b = seed_run(sector="logistics")
    c = seed_run(sector="logistics")
    seed_run(sector="logistics")  # no build.json: used, but not counted
    seed_run(sector="fintech")
    _build(a, True, 1)
    _build(b, True, 2)  # needed a repair: not first time
    _build(c, False, 3)
    res = client.get("/api/templates")
    assert res.status_code == 200
    kits = {k["sector"]: k for k in res.json()}
    assert set(kits) == {"logistics", "healthcare", "e-commerce", "fintech"}
    logistics = kits["logistics"]
    assert logistics["runs_used"] == 4
    assert logistics["builds_counted"] == 3 and logistics["first_time_ok"] == 1
    assert logistics["first_time_build_rate"] == 1 / 3
    assert logistics["screens"] == 3 and logistics["app_class"] and logistics["accent"]
    assert kits["fintech"]["runs_used"] == 1 and kits["fintech"]["first_time_build_rate"] is None
    assert kits["healthcare"]["runs_used"] == 0
    assert get_settings().runs_dir  # temp dir, not the repo's runs/
