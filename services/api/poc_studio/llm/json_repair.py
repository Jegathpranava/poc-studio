"""Fence stripping and the repair prompt."""

import re

_FENCE = re.compile(r"^\s*```[a-zA-Z0-9_-]*\s*\n?(.*?)\n?\s*```\s*$", re.DOTALL)


def strip_fences(text: str) -> str:
    m = _FENCE.match(text)
    return (m.group(1) if m else text).strip()


def repair_prompt(error: str) -> str:
    return (
        "Your previous reply was not valid for the required JSON schema.\n"
        f"Validation error:\n{error}\n\n"
        "Reply again with only the corrected JSON object. No prose, no code fences."
    )
