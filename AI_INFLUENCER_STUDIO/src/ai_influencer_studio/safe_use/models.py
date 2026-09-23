"""Data contracts for safe browser and Windows UI automation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class ActionMode(StrEnum):
    """Permission level for a safe-use request."""

    OBSERVE = "observe"
    PROPOSE = "propose"
    EXECUTE = "execute"


class ActionTarget(StrEnum):
    """Supported automation surfaces."""

    BROWSER = "browser"
    WINDOWS = "windows"


@dataclass(frozen=True)
class Observation:
    """Sanitized state captured before planning or execution."""

    target: ActionTarget
    captured_at: str
    title: str = ""
    url: str = ""
    text: str = ""
    screenshot: str | None = None
    elements: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target.value,
            "captured_at": self.captured_at,
            "title": self.title,
            "url": self.url,
            "text": self.text,
            "screenshot": self.screenshot,
            "elements": self.elements,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class ActionIntent:
    """A proposed action that must pass policy before execution."""

    target: ActionTarget
    action: str
    parameters: dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    requested_by: str = "operator"
    intent_id: str = ""
    created_at: str = ""

    def with_identity(self, intent_id: str) -> ActionIntent:
        return ActionIntent(
            target=self.target,
            action=self.action,
            parameters=self.parameters,
            reason=self.reason,
            requested_by=self.requested_by,
            intent_id=intent_id,
            created_at=self.created_at or datetime.now(UTC).isoformat(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target.value,
            "action": self.action,
            "parameters": self.parameters,
            "reason": self.reason,
            "requested_by": self.requested_by,
            "intent_id": self.intent_id,
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class Approval:
    """Short-lived, single-use approval for one exact intent."""

    token: str
    intent_id: str
    intent_fingerprint: str
    expires_at: float
    approved_by: str = "operator"


@dataclass(frozen=True)
class ActionResult:
    """Result of an observe, propose, or execute operation."""

    mode: ActionMode
    intent: ActionIntent | None = None
    observation: Observation | None = None
    executed: bool = False
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode.value,
            "intent": self.intent.to_dict() if self.intent else None,
            "observation": self.observation.to_dict() if self.observation else None,
            "executed": self.executed,
            "message": self.message,
            "data": self.data,
        }
