from pathlib import Path

import pytest

from poc_studio.config import Settings
from poc_studio.qa.secrets import scan_pii, scan_text, scan_tree

# Fake values, assembled from parts so no real-looking secret sits in the source.
GHP = "ghp_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4"
PAT = "github_pat_" + "11AAAAAAA0abcdefghijklmnop"
SK = "sk-" + "proj1234567890abcdefgh"
JWT = ".".join(["eyJhbGciOiJIUzI1NiJ9", "eyJzdWIiOiIxMjM0NTYifQ", "abcdefghijk123"])
KEY_BLOCK = "-----BEGIN RSA " + "PRIVATE KEY-----\nMIIEowIBAAKCAQEA\n-----END RSA " + "PRIVATE KEY-----"
ENV_VALUE = "Zq9-unit-test-env-value-7731"


@pytest.fixture
def temp_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    env = tmp_path / ".env"
    env.write_text(f"SOME_SERVICE_KEY={ENV_VALUE}\nEMPTY=\nMODE=mock\n", encoding="utf-8")
    monkeypatch.setitem(Settings.model_config, "env_file", env)
    return env


@pytest.mark.parametrize(
    ("text", "kind"),
    [
        (f"const t = '{GHP}'", "github_token"),
        (f"token {PAT}", "github_token"),
        (f"OPENAI={SK}", "api_key"),
        (KEY_BLOCK, "private_key"),
        (f"jwt: {JWT}", "jwt"),
        ("DB_PASSWORD=x", "credential_assignment"),
        ('const config = { apiKey: "abc123" }', "credential_assignment"),
    ],
)
def test_flags_each_secret_kind_without_echoing_it(text: str, kind: str) -> None:
    findings = scan_text("line one\n" + text, "app/x.ts")
    assert [(f.file, f.line, f.kind) for f in findings if f.kind == kind] == [("app/x.ts", 2, kind)]
    dumped = " ".join(f.model_dump_json() for f in findings)
    for secret in (GHP, PAT, SK, JWT, "MIIEowIBAAKCAQEA", "abc123", "DB_PASSWORD=x"):
        assert secret not in dumped


def test_code_that_merely_names_a_secret_is_not_flagged() -> None:
    clean = (
        "const apiKey = process.env.KEY;\ntoken: string;\nOPENAI_API_KEY=\nDB_PASSWORD=your-password-here\n"
    )
    assert scan_text(clean) == []


def test_env_value_is_matched_by_hash(temp_env: Path) -> None:
    findings = scan_text(f"line1\nfetch('x', {{ headers: {{ k: '{ENV_VALUE}' }} }})", "app/a.ts")
    assert [(f.line, f.kind) for f in findings] == [(2, "env_value")]
    assert ENV_VALUE not in findings[0].model_dump_json()
    assert scan_text("MODE=mock and nothing else") == []  # short values are never matched


def test_env_file_is_read_at_call_time(temp_env: Path) -> None:
    assert scan_text(ENV_VALUE) != []
    temp_env.write_text("SOME_SERVICE_KEY=changed-value-123456\n", encoding="utf-8")
    assert scan_text(ENV_VALUE) == []


def test_scan_tree_excludes_node_modules_and_home(tmp_path: Path) -> None:
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "a.ts").write_text(f"x = '{GHP}'", encoding="utf-8")
    for skipped in ("node_modules/pkg", ".next", ".home/.npm"):
        (tmp_path / skipped).mkdir(parents=True)
        (tmp_path / skipped / "leak.js").write_text(f"x = '{SK}'", encoding="utf-8")
    (tmp_path / "bin.dat").write_bytes(b"\x00\x01" + SK.encode())
    findings = scan_tree(tmp_path)
    assert [(f.file, f.kind) for f in findings] == [("app/a.ts", "github_token")]
    assert scan_tree(tmp_path / "missing") == []


def test_example_com_and_stakeholder_emails_are_allowed_but_real_looking_ones_are_not() -> None:
    names = ["Maria Lopez"]
    ok = "write to demo@example.com or maria.lopez@acme-corp.io"
    assert scan_pii(ok, allow_names=names) == []
    found = scan_pii("contact jane@acme-corp.io today", "deck/x.html", names)
    assert [(f.file, f.line, f.kind) for f in found] == [("deck/x.html", 1, "email")]
    assert "jane@acme-corp.io" not in found[0].model_dump_json()


def test_stakeholder_names_are_not_flagged_and_phones_are(tmp_path: Path) -> None:
    (tmp_path / "page.html").write_text(
        "<p>Maria Lopez from Acme</p>\n<p>Call +44 7700 900123 or 555-0142</p>", encoding="utf-8"
    )
    findings = scan_tree(tmp_path, pii=True, allow_names=["Maria Lopez"])
    assert [(f.line, f.kind) for f in findings] == [(2, "phone")]
