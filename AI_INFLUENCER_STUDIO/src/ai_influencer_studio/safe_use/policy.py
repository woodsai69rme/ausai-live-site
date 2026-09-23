"""Safety policy for browser and Windows UI actions."""

from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urlparse

from ai_influencer_studio.safe_use.models import ActionIntent, ActionTarget


class PolicyDenied(PermissionError):
    """Raised when an intent violates the configured safe-use policy."""


@dataclass
class SafePolicy:
    """Explicit allowlists and action restrictions for automation."""

    allowed_domains: set[str] = field(default_factory=set)
    allowed_apps: set[str] = field(default_factory=set)
    allowed_browser_actions: set[str] = field(
        default_factory=lambda: {
            "navigate", "observe", "click", "fill", "press", "scroll", "screenshot",
            "select_option", "hover", "type", "back", "forward", "wait", "evaluate",
        }
    )
    allowed_windows_actions: set[str] = field(
        default_factory=lambda: {"observe", "focus", "click", "type", "hotkey", "screenshot", "close"}
    )
    require_approval_for: set[str] = field(
        default_factory=lambda: {"click", "fill", "press", "focus", "type", "hotkey", "evaluate", "close"}
    )
    allow_sensitive_fields: bool = False

    def check(self, intent: ActionIntent) -> None:
        """Raise PolicyDenied unless the intent is permitted."""
        if intent.target == ActionTarget.BROWSER:
            if intent.action not in self.allowed_browser_actions:
                raise PolicyDenied(f"Browser action is not allowed: {intent.action}")
            if intent.action == "navigate":
                self._check_domain(str(intent.parameters.get("url", "")))
            elif "url" in intent.parameters:
                self._check_domain(str(intent.parameters["url"]))
            elif intent.action in {
                "click", "fill", "press", "scroll", "screenshot", "observe",
                "select_option", "hover", "type", "back", "forward", "wait", "evaluate",
            }:
                current_url = str(intent.parameters.get("current_url", ""))
                self._check_domain(current_url)
            if not self.allow_sensitive_fields and intent.action in {"fill", "type"}:
                field_name = str(intent.parameters.get("field", "")).lower()
                if any(word in field_name for word in ("password", "token", "secret", "api_key", "credit")):
                    raise PolicyDenied("Sensitive form fields require an explicit policy override")
        elif intent.target == ActionTarget.WINDOWS:
            if intent.action not in self.allowed_windows_actions:
                raise PolicyDenied(f"Windows action is not allowed: {intent.action}")
            app = str(intent.parameters.get("app", "")).lower()
            allowed_apps = {item.lower() for item in self.allowed_apps}
            if not app or not allowed_apps or app not in allowed_apps:
                raise PolicyDenied(f"Windows application is not allowlisted: {app or '(missing)'}")
        else:
            raise PolicyDenied(f"Unknown automation target: {intent.target}")

    def requires_approval(self, intent: ActionIntent) -> bool:
        """Return whether this action needs a one-shot operator approval."""
        return intent.action in self.require_approval_for

    def _check_domain(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise PolicyDenied("Only absolute HTTP(S) URLs are allowed")
        hostname = parsed.hostname.lower().rstrip(".")
        allowed = {domain.lower().lstrip(".") for domain in self.allowed_domains}
        if not allowed:
            raise PolicyDenied("No browser domains are allowlisted")
        if not any(hostname == domain or hostname.endswith(f".{domain}") for domain in allowed):
            raise PolicyDenied(f"Browser domain is not allowlisted: {hostname}")
