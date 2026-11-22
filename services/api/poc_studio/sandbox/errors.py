"""Turn `next build` / `tsc` output into one structured error: file, line, column, message, excerpt."""

import re
from pathlib import Path

from pydantic import BaseModel

_ANSI = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")
# Next.js: `./app/page.tsx:5:7` on its own line (a webpack-style `ts(5,7)` is handled below).
_NEXT_LOC = re.compile(r"^\s*(?:\./)?([^\s:()<>|]+\.(?:tsx?|jsx?|mjs|cjs|css|json)):(\d+):(\d+)\s*$")
# tsc: `app/page.tsx(5,7): error TS2322: message`
_TSC = re.compile(r"^\s*(?:\./)?(\S+?\.(?:tsx?|jsx?))\((\d+),(\d+)\):\s*error\s+TS\d+:\s*(.+)$")
_FRAME = re.compile(r"^\s*>?\s*\d+\s*\|")  # `> 5 |   code` or `  3 | code`
_CARET = re.compile(r"^\s*\|\s*\^")
_STOP = re.compile(
    r"^(Import trace|Next\.js build worker|npm (?:ERR|error)|Build error|Error: Turbopack)", re.I
)
_HEADING = re.compile(r"^(Parsing|Syntax|Ecmascript|Expected|Unexpected|Module parse failed)", re.I)
_CONTEXT = 2


class BuildError(BaseModel):
    file: str
    line: int
    col: int
    message: str
    excerpt: str = ""


def strip_ansi(text: str) -> str:
    return _ANSI.sub("", text)


def excerpt_from_file(app_dir: Path, file: str, line: int) -> str:
    """`line` plus 2 lines either side from the file on disk; the error line is marked with `>`."""
    path = app_dir / file
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return ""
    if not 1 <= line <= len(lines):
        return ""
    lo, hi = max(1, line - _CONTEXT), min(len(lines), line + _CONTEXT)
    width = len(str(hi))
    return "\n".join(f"{'>' if n == line else ' '} {n:>{width}} | {lines[n - 1]}" for n in range(lo, hi + 1))


def _clean(message: str) -> str:
    message = re.sub(r"^(?:Type error|Error):\s*", "", message.strip())
    return re.sub(r"\s+", " ", message).strip()


def _next_block(lines: list[str], i: int) -> tuple[str, str]:
    """From the line after a location: (message, code frame text from the output)."""
    head: list[str] = []
    frame: list[str] = []
    tail: list[str] = []
    for line in lines[i:]:
        if _STOP.match(line.strip()):
            break
        if _FRAME.match(line) or _CARET.match(line):
            frame.append(line.rstrip())
        elif not line.strip():
            if tail:
                break  # a blank line after the trailing text ends the block
        elif frame:
            tail.append(line.strip())
        else:
            head.append(line.strip())
    message = " ".join(head)
    if head and tail and (_HEADING.match(head[0]) or not message.rstrip().endswith((".", "'", "`"))):
        message = f"{message} {' '.join(tail)}"
    elif not head:
        message = " ".join(tail)
    return _clean(message), "\n".join(frame)


def parse_build_error(output: str, app_dir: Path | None = None) -> BuildError | None:
    text = strip_ansi(output).replace("\r\n", "\n")
    lines = text.split("\n")
    for i, line in enumerate(lines):
        m = _TSC.match(line)
        if m:
            file, ln, col = m.group(1), int(m.group(2)), int(m.group(3))
            return BuildError(
                file=file, line=ln, col=col, message=_clean(m.group(4)),
                excerpt=excerpt_from_file(app_dir, file, ln) if app_dir else "",
            )  # fmt: skip
        m = _NEXT_LOC.match(line)
        if m:
            file, ln, col = m.group(1), int(m.group(2)), int(m.group(3))
            message, frame = _next_block(lines, i + 1)
            excerpt = excerpt_from_file(app_dir, file, ln) if app_dir else ""
            return BuildError(
                file=file, line=ln, col=col, message=message or "Build failed", excerpt=excerpt or frame
            )
    if re.search(r"(Failed to compile|Build error occurred|Build failed|npm error)", text, re.I):
        # No location: keep the first line that looks like the reason.
        for line in lines:
            s = line.strip()
            if re.match(r"^(Error|Type error|Module not found|npm error)", s, re.I):
                return BuildError(file="", line=0, col=0, message=_clean(s))
        return BuildError(file="", line=0, col=0, message="Build failed")
    return None
