"""Mask known secret patterns (spec 7b "Secrets and PII scan") before text is stored or streamed."""

import logging
import re
from typing import Any

MASK = "[REDACTED]"

_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?(?:-----END [A-Z ]*PRIVATE KEY-----|\Z)", re.DOTALL),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"\bsk-[A-Za-z0-9_\-]{16,}"),
    re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}"),
    re.compile(r"\beyJ[A-Za-z0-9_\-]{5,}\.eyJ[A-Za-z0-9_\-]{5,}\.[A-Za-z0-9_\-]{5,}"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{16,}"),
)
# Names such as DB_PASSWORD or openai_api_key: any prefix words, then a sensitive word.
_KEY_NAME = r"(?:[A-Za-z0-9]+[_-])*(?:password|passwd|secret|token|api[_-]?key)"
_KEY_VALUE = re.compile(
    rf"""(?i)(?<![A-Za-z])({_KEY_NAME})("?\s*[=:]\s*)("[^"\r\n]*"|'[^'\r\n]*'|[^\s,;"']+)"""
)
_SENSITIVE_KEY = re.compile(rf"(?i){_KEY_NAME}")


def redact(text: str) -> str:
    for pattern in _PATTERNS:
        text = pattern.sub(MASK, text)
    return _KEY_VALUE.sub(lambda m: f"{m.group(1)}{m.group(2)}{MASK}", text)


def redact_obj(value: Any) -> Any:
    """Redact every string inside nested dicts and lists."""
    if isinstance(value, str):
        return redact(value)
    if isinstance(value, dict):
        return {
            k: MASK if isinstance(k, str) and _SENSITIVE_KEY.fullmatch(k) and v is not None else redact_obj(v)
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [redact_obj(v) for v in value]
    return value


class RedactingFilter(logging.Filter):
    """Masks secrets in a log record's message, args and traceback text."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()  # formats args too, so exception objects in args are covered
        except Exception:
            message = str(record.msg)
        record.msg, record.args = redact(message), None
        if record.exc_info and not record.exc_text:
            record.exc_text = logging.Formatter().formatException(record.exc_info)
        if record.exc_text:
            record.exc_text = redact(record.exc_text)
        return True


_installed = False


def install_log_redaction() -> None:
    """Redact every record logged under `poc_studio` or a child of it. Idempotent.

    A logger-level filter only sees records logged directly on that logger, so the same filter also runs
    from a record factory for `poc_studio.*` children.
    """
    global _installed
    if _installed:
        return
    _installed = True
    flt = RedactingFilter()
    logging.getLogger("poc_studio").addFilter(flt)
    previous = logging.getLogRecordFactory()

    def factory(*args: Any, **kwargs: Any) -> logging.LogRecord:
        record = previous(*args, **kwargs)
        if record.name.startswith("poc_studio"):
            flt.filter(record)
        return record

    logging.setLogRecordFactory(factory)
