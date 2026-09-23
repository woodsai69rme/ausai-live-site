"""Append-only audit logging for safe automation actions."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_SECRET_PATTERNS = (
    re.compile(r"(?i)(bearer\s+)[^\s,;]+"),
    re.compile(r"(?i)(password|passwd|secret|token|api[_-]?key)\s*[:=]\s*[^\s,;]+"),
    re.compile(r"(?i)(https?://[^\s?]+)\?[^\s]+"),
)


def redact(value: Any) -> Any:
    """Recursively redact likely credentials from audit payloads."""
    if isinstance(value, str):
        result = value
        for pattern in _SECRET_PATTERNS:
            result = pattern.sub(lambda match: f"{match.group(1)}[REDACTED]" if match.lastindex else "[REDACTED]", result)
        return result[:4000]
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key).lower()
            if any(word in key_text for word in ("value", "password", "secret", "token", "api_key", "authorization")):
                redacted[str(key)] = "[REDACTED]"
            else:
                redacted[str(key)] = redact(item)
        return redacted
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


class AuditLogger:
    """Write one redacted JSON record per safe-use event."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, event: str, payload: dict[str, Any]) -> None:
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "event": event,
            "payload": redact(payload),
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
