import logging
from pathlib import Path

import pytest

from poc_studio.safety import node_access_problem
from poc_studio.sandbox.fix import FixFile, PortFix, apply_fix
from poc_studio.sandbox.jsx import page_source

PATH = "app/x/page.tsx"
BAD = {
    "require": 'const a = require("fs");',
    "import()": 'const m = await import("./x");',
    "fs": 'import { readFileSync } from "fs";',
    "node:fs": "import fs from 'node:fs';",
    "fs/promises": 'import { readFile } from "fs/promises";',
    "child_process": 'import { exec } from "child_process";',
    "net": 'import net from "net";',
    "http": 'import http from "http";',
    "https": 'import https from "https";',
    "os": 'import os from "os";',
    "worker_threads": 'import { Worker } from "worker_threads";',
    "vm": 'import vm from "vm";',
    "side-effect import": 'import "fs";',
    "process.env": "const k = process.env.SECRET;",
    "process.binding": 'process.binding("fs");',
    "eval": "eval('1+1');",
    "new Function": "const f = new Function('return 1');",
    "fetch": 'fetch("https://evil.example/x");',
    "fetch protocol-relative": "fetch('//evil.example/x');",
    "XMLHttpRequest": "const x = new XMLHttpRequest();",
    "WebSocket": 'const w = new WebSocket("ws://x");',
    "../ out of app": 'import x from "../../lib/secret";',
    "../ out of repo": 'import x from "../../../../etc/passwd";',
}


@pytest.mark.parametrize("name", list(BAD))
def test_each_pattern_is_rejected(name: str) -> None:
    assert node_access_problem(PATH, BAD[name]) is not None


GOOD = [
    'import Link from "next/link";',
    'import "./x.css";',
    'import React, { useState } from "react";',
    'import Nav from "../../components/Nav";',
    'import Nav from "@/components/Nav";',
    'fetch("/api/x");',
    "export default function P() { return <div>process of elimination</div>; }",
]


@pytest.mark.parametrize("src", GOOD)
def test_normal_code_passes(src: str) -> None:
    assert node_access_problem(PATH, src) is None


def test_apply_fix_skips_a_rejected_file_with_a_reason_and_applies_the_rest(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    fix = PortFix(
        files=[
            FixFile(
                path="app/ok/page.tsx", content='import Link from "next/link";\nexport default () => null;'
            ),
            FixFile(path="app/bad/page.tsx", content='import fs from "fs";'),
        ]
    )
    with caplog.at_level(logging.WARNING):
        written, rejected = apply_fix(tmp_path, fix)
    assert written == ["app/ok/page.tsx"] and rejected == ["app/bad/page.tsx"]
    assert not (tmp_path / "app/bad/page.tsx").exists()
    assert "app/bad/page.tsx" in caplog.text and "uses" in caplog.text


def test_deterministic_jsx_output_is_clean() -> None:
    src = page_source("fleet", '<h1>Fleet</h1><a href="/x">Go</a><p>Ready</p>')
    assert node_access_problem("app/fleet/page.tsx", src) is None


def test_jsx_with_a_banned_text_is_refused() -> None:
    with pytest.raises(ValueError, match="node or system access"):
        page_source("fleet", "<p>process.env.SECRET</p>")
