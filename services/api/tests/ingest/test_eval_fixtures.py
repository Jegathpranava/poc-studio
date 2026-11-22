import json
from pathlib import Path

import pytest

from poc_studio.ingest import parse_file

EVAL_DIR = Path(__file__).resolve().parents[4] / "eval" / "fixtures"
EXPECTED = json.loads((EVAL_DIR / "expected.json").read_text(encoding="utf-8"))


def test_expected_lists_ten_with_sector_spread() -> None:
    sectors = [e["sector"] for e in EXPECTED]
    assert len(EXPECTED) == 10
    assert {s: sectors.count(s) for s in set(sectors)} == {
        "logistics": 3,
        "healthcare": 3,
        "e-commerce": 2,
        "fintech": 2,
    }
    assert all(len(e["must_have_features"]) == 3 for e in EXPECTED)


@pytest.mark.parametrize("entry", EXPECTED, ids=[e["file"] for e in EXPECTED])
def test_fixture_exists_and_parses(entry: dict) -> None:
    path = EVAL_DIR / entry["file"]
    assert path.is_file()
    assert parse_file(path).word_count >= 600
