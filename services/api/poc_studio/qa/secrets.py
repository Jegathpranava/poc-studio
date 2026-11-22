"""Secret and PII scan (spec 7b). Findings carry the kind and location only, never the matched text.

The pattern set is the one in `redact.py`. On top of it, every sizeable non-empty value in the repo `.env`
is matched by the sha256 of candidate tokens, so the plain values live only inside `env_hashes` (as hashes)
and are never printed or returned.
"""

import hashlib
import re
from collections.abc import Iterable
from functools import lru_cache
from pathlib import Path

from dotenv import dotenv_values
from pydantic import BaseModel

from poc_studio.config import Settings
from poc_studio.redact import KEY_VALUE_PATTERN, MASK, SECRET_PATTERNS

DEFAULT_EXCLUDE = ("node_modules", ".next", ".home")
SKIP_FILES = {"package-lock.json", "pnpm-lock.yaml", "yarn.lock"}
NO_PII_SUFFIXES = {".css", ".svg", ".map", ".json"}
MAX_BYTES = 1_000_000
MIN_ENV_VALUE = 8
BENIGN_ENV_VALUES = {"development", "production", "localhost", "password"}
# Settings that are not credentials (a model name such as the pitch polish model is public and shows up in
# generated docs): their values are not hashed.
NON_SECRET_KEY = re.compile(r"(?i)_(?:MODEL|BASE_URL|MODE|PROVIDER|ENV|DIR|DAYS|USD)$")

_TOKEN = re.compile(r"[^\s\"'`,;(){}<>\[\]=]+")
_EMAIL = re.compile(r"(?<![\w.+-])([A-Za-z0-9._%+-]+)@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,})\b")
_PHONE = re.compile(
    r"(?<![\w.])(?:\+\d{1,3}[ .-]?)?(?:\(\d{2,4}\)[ .-]?)?\d{2,4}[ .-]\d{3,4}[ .-]?\d{3,4}(?![\w.])"
)
_FICTIONAL_PHONE = re.compile(r"555[ .-]?01\d\d")
_ENV_STYLE = re.compile(r"^\s*(?:export\s+)?[A-Za-z_][A-Za-z0-9_]*\s*=")
_PLACEHOLDER = re.compile(
    r"(?i)^(?:your|change|xxx|example|placeholder|todo|<|\$|\.\.\.|process\.|os\.|env\b)"
)
_KINDS = (
    ("-----BEGIN", "private_key"), ("github_pat_", "github_token"), ("gh", "github_token"),
    ("sk-", "api_key"), ("AKIA", "aws_key"), ("ASIA", "aws_key"), ("xox", "slack_token"),
    ("eyJ", "jwt"), ("Bearer", "bearer_token"),
)  # fmt: skip


class Finding(BaseModel):
    file: str
    line: int
    kind: str


def _kind(matched: str) -> str:
    return next((kind for prefix, kind in _KINDS if matched.startswith(prefix)), "secret")


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def env_file_path() -> Path | None:
    """The `.env` the settings read, looked up at call time (tests point it at a temp file)."""
    env_file = Settings.model_config.get("env_file")
    return Path(str(env_file)) if env_file else None


@lru_cache(maxsize=4)
def _hashes_of(path: Path, stamp: tuple[int, int]) -> frozenset[str]:
    del stamp  # only part of the cache key: a changed file is read again
    values = (v for k, v in dotenv_values(path).items() if v and not NON_SECRET_KEY.search(k))
    return frozenset(
        _sha(v) for v in values if len(v) >= MIN_ENV_VALUE and v.lower() not in BENIGN_ENV_VALUES
    )


def env_hashes() -> frozenset[str]:
    """sha256 of every sizeable non-empty `.env` value. Only hashes leave the cached helper."""
    path = env_file_path()
    try:
        if path is None or not path.is_file():
            return frozenset()
        stat = path.stat()
        return _hashes_of(path, (stat.st_mtime_ns, stat.st_size))
    except OSError:
        return frozenset()


def _assignment_is_secret(line: str, m: re.Match[str]) -> bool:
    if "\n" in m.group(2):
        return False  # the value sits on the next line: `KEY=` is an empty assignment
    value = m.group(3)
    bare = value.strip("\"'")
    if bare == MASK or _PLACEHOLDER.match(bare):
        return False
    if value[:1] in "\"'":
        return bool(bare)  # a quoted literal
    return "=" in m.group(2) and bool(_ENV_STYLE.match(line))  # `DB_PASSWORD=x` lines only, not code


def _line_at(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def scan_text(text: str, file: str = "") -> list[Finding]:
    """Secret findings in `text` (no PII). `file` only labels the findings."""
    found: dict[tuple[int, str], Finding] = {}

    def add(pos: int, kind: str) -> None:
        line = _line_at(text, pos)
        found.setdefault((line, kind), Finding(file=file, line=line, kind=kind))

    for pattern in SECRET_PATTERNS:
        for m in pattern.finditer(text):
            add(m.start(), _kind(m.group(0)))
    for m in KEY_VALUE_PATTERN.finditer(text):
        start = text.rfind("\n", 0, m.start()) + 1
        end = text.find("\n", m.end())
        if _assignment_is_secret(text[start : len(text) if end == -1 else end], m):
            add(m.start(), "credential_assignment")
    hashes = env_hashes()
    if hashes:
        for m in _TOKEN.finditer(text):
            if len(m.group(0)) >= MIN_ENV_VALUE and _sha(m.group(0)) in hashes:
                add(m.start(), "env_value")
    return sorted(found.values(), key=lambda f: (f.line, f.kind))


def _name_forms(names: Iterable[str]) -> set[str]:
    forms: set[str] = set()
    for name in names:
        parts = re.findall(r"[a-z0-9]+", name.lower())
        if len(parts) >= 2:
            forms |= {".".join(parts), "_".join(parts), "-".join(parts), "".join(parts)}
    return forms


def scan_pii(text: str, file: str = "", allow_names: Iterable[str] = ()) -> list[Finding]:
    """Emails and phone numbers. Allowed: `example.com`, a stakeholder's own address, fictional 555-01xx.

    Stakeholder names themselves are never flagged here (they stay in the deck, spec 7b); the share-zip scan
    passes them in `allow_names` for the same reason.
    """
    allowed = _name_forms(allow_names)
    found: dict[tuple[int, str], Finding] = {}

    def add(pos: int, kind: str) -> None:
        line = _line_at(text, pos)
        found.setdefault((line, kind), Finding(file=file, line=line, kind=kind))

    for m in _EMAIL.finditer(text):
        domain = m.group(2).lower()
        if domain == "example.com" or domain.endswith(".example.com") or m.group(1).lower() in allowed:
            continue
        add(m.start(), "email")
    for m in _PHONE.finditer(text):
        if 9 <= len(re.sub(r"\D", "", m.group(0))) <= 15 and not _FICTIONAL_PHONE.search(m.group(0)):
            add(m.start(), "phone")
    return sorted(found.values(), key=lambda f: (f.line, f.kind))


def _files(root: Path, exclude: tuple[str, ...]) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if any(part in exclude for part in path.relative_to(root).parts) or path.name in SKIP_FILES:
            continue
        try:
            if path.is_file() and path.stat().st_size <= MAX_BYTES:
                yield path
        except OSError:
            continue


def scan_tree(
    root: Path,
    exclude: tuple[str, ...] = DEFAULT_EXCLUDE,
    *,
    pii: bool = False,
    allow_names: Iterable[str] = (),
) -> list[Finding]:
    """Findings in every text file under `root` (`file` is relative to it). `pii=True` adds emails/phones."""
    if not root.is_dir():
        return []
    names = list(allow_names)
    out: list[Finding] = []
    for path in _files(root, exclude):
        try:
            data = path.read_bytes()
        except OSError:
            continue
        if b"\x00" in data[:4096]:
            continue
        text = data.decode("utf-8", errors="replace")
        rel = path.relative_to(root).as_posix()
        out += scan_text(text, rel)
        if pii and path.suffix.lower() not in NO_PII_SUFFIXES:
            out += scan_pii(text, rel, names)
    return out
