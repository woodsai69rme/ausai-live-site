"""Safe observe/propose/execute orchestration."""

from __future__ import annotations

import hashlib
import json
import secrets
import time
import uuid
from pathlib import Path
from typing import Any

from ai_influencer_studio.safe_use.audit import AuditLogger
from ai_influencer_studio.safe_use.browser import PlaywrightBrowser
from ai_influencer_studio.safe_use.models import ActionIntent, ActionMode, ActionResult, ActionTarget, Approval
from ai_influencer_studio.safe_use.policy import PolicyDenied, SafePolicy
from ai_influencer_studio.safe_use.windows_ui import WindowsUIAutomation, WindowsUIUnavailable


class ApprovalRequired(PermissionError):
    """Raised when an execute request has no valid approval."""


class SafeUseEngine:
    """Coordinate safe browser and Windows UI operations."""

    def __init__(
        self,
        policy: SafePolicy,
        audit_path: Path,
        browser: PlaywrightBrowser | None = None,
        windows: WindowsUIAutomation | None = None,
        approval_ttl: float = 60.0,
    ) -> None:
        self.policy = policy
        self.audit = AuditLogger(audit_path)
        self.browser = browser
        self.windows = windows
        self.approval_ttl = approval_ttl
        self._approvals: dict[str, Approval] = {}

    def observe(self, target: str, **parameters: Any) -> ActionResult:
        """Capture current state through the same allowlist policy as actions."""
        if target == "browser":
            if not parameters.get("url"):
                raise PolicyDenied("Browser observation requires an explicit allowlisted URL")
            observation_url = str(parameters["url"])
            self.policy.check(ActionIntent(target=ActionTarget.BROWSER, action="navigate", parameters={"url": observation_url}))
        elif target == "windows":
            app = str(parameters.get("app", ""))
            self.policy.check(ActionIntent(target=ActionTarget.WINDOWS, action="observe", parameters={"app": app}))
        adapter = self._adapter(target)
        if target == "browser" and parameters.get("url"):
            navigation = ActionIntent(
                target=ActionTarget.BROWSER,
                action="navigate",
                parameters={"url": str(parameters.pop("url"))},
                reason="open an allowlisted page for observation",
            ).with_identity(uuid.uuid4().hex)
            self.policy.check(navigation)
            data = adapter.execute(navigation)
            redirected_url = data.get("url") if isinstance(data, dict) else None
            if redirected_url:
                self.policy.check(
                    ActionIntent(target=ActionTarget.BROWSER, action="navigate", parameters={"url": str(redirected_url)})
                )
            self.audit.record("observe_navigate", {"intent": navigation.to_dict(), "result": data})
        observation = adapter.observe(**parameters)
        self.audit.record("observe", observation.to_dict())
        return ActionResult(mode=ActionMode.OBSERVE, observation=observation, message="Observation captured")

    def propose(self, intent: ActionIntent) -> ActionResult:
        """Validate and return an intent without executing it."""
        intent = self._identity(intent)
        intent = self._attach_browser_origin(intent)
        self.policy.check(intent)
        self.audit.record("propose", {"intent": intent.to_dict(), "requires_approval": self.policy.requires_approval(intent)})
        message = "Intent approved for execution" if self.policy.requires_approval(intent) else "Intent may execute"
        return ActionResult(mode=ActionMode.PROPOSE, intent=intent, message=message)

    def approve(self, intent: ActionIntent, approved_by: str = "operator") -> Approval:
        """Create a short-lived approval for an exact proposed intent."""
        proposed = self.propose(intent).intent
        assert proposed is not None
        approval = Approval(
            token=secrets.token_urlsafe(24),
            intent_id=proposed.intent_id,
            expires_at=time.time() + self.approval_ttl,
            intent_fingerprint=self._fingerprint(proposed),
            approved_by=approved_by,
        )
        self._approvals[approval.token] = approval
        self.audit.record("approve", {"intent_id": proposed.intent_id, "approved_by": approved_by})
        return approval

    def execute(self, intent: ActionIntent, approval_token: str | None = None) -> ActionResult:
        """Execute one policy-checked action using a valid single-use approval."""
        if approval_token and not intent.intent_id:
            pending = self._approvals.get(approval_token)
            if pending is not None:
                intent = intent.with_identity(pending.intent_id)
        proposed = self.propose(intent).intent
        assert proposed is not None
        proposed = self._require_current_browser(proposed)
        if self.policy.requires_approval(proposed):
            if not approval_token:
                self.audit.record("deny", {"intent": proposed.to_dict(), "reason": "approval_required"})
                raise ApprovalRequired("This action requires an approval token")
            self._consume_approval(approval_token, proposed)
        try:
            data = self._adapter(proposed.target.value).execute(proposed)
            if proposed.target == ActionTarget.BROWSER and self.browser is not None:
                current_url = self.browser.current_url()
                if current_url:
                    self.policy.check(
                        ActionIntent(target=ActionTarget.BROWSER, action="navigate", parameters={"url": current_url})
                    )
        except Exception as exc:
            self.audit.record("execute_error", {"intent": proposed.to_dict(), "error": type(exc).__name__})
            raise
        self.audit.record("execute", {"intent": proposed.to_dict(), "result": data})
        return ActionResult(mode=ActionMode.EXECUTE, intent=proposed, executed=True, data=data, message="Action executed")

    def _identity(self, intent: ActionIntent) -> ActionIntent:
        return intent.with_identity(intent.intent_id or uuid.uuid4().hex)

    def _attach_browser_origin(self, intent: ActionIntent) -> ActionIntent:
        if intent.target.value != "browser" or intent.action == "navigate":
            return intent
        if "url" in intent.parameters:
            requested_url = str(intent.parameters["url"])
            self.policy.check(ActionIntent(target=ActionTarget.BROWSER, action="navigate", parameters={"url": requested_url}))
            return intent
        if self.browser is None:
            raise PolicyDenied("Browser actions require a configured browser adapter")
        current_url = self.browser.current_url()
        if not current_url:
            raise PolicyDenied("Browser actions require a current observed URL")
        parameters = {**intent.parameters, "current_url": current_url}
        return ActionIntent(
            target=intent.target,
            action=intent.action,
            parameters=parameters,
            reason=intent.reason,
            requested_by=intent.requested_by,
            intent_id=intent.intent_id,
            created_at=intent.created_at,
        )

    def _require_current_browser(self, intent: ActionIntent) -> ActionIntent:
        if intent.target.value != "browser" or intent.action == "navigate":
            return intent
        if self.browser is None or not self.browser.current_url():
            raise PolicyDenied("Browser action requires a current observed page")
        current_url = self.browser.current_url()
        requested_url = str(intent.parameters.get("url", current_url))
        if requested_url != current_url:
            raise PolicyDenied("Browser action URL does not match the current observed page")
        if intent.parameters.get("current_url") == current_url:
            return intent
        return ActionIntent(
            target=intent.target,
            action=intent.action,
            parameters={**intent.parameters, "current_url": current_url},
            reason=intent.reason,
            requested_by=intent.requested_by,
            intent_id=intent.intent_id,
            created_at=intent.created_at,
        )

    def _consume_approval(self, token: str, intent: ActionIntent) -> None:
        approval = self._approvals.pop(token, None)
        if (
            approval is None
            or approval.intent_id != intent.intent_id
            or approval.intent_fingerprint != self._fingerprint(intent)
            or approval.expires_at < time.time()
        ):
            self.audit.record("deny", {"intent_id": intent.intent_id, "reason": "invalid_or_expired_approval"})
            raise ApprovalRequired("Approval token is invalid, expired, or belongs to another intent")

    @staticmethod
    def _fingerprint(intent: ActionIntent) -> str:
        payload = {
            "target": intent.target.value,
            "action": intent.action,
            "parameters": {key: value for key, value in intent.parameters.items() if key != "current_url"},
            "reason": intent.reason,
            "requested_by": intent.requested_by,
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _adapter(self, target: str) -> Any:
        if target == "browser":
            if self.browser is None:
                raise RuntimeError("Browser adapter is not configured")
            return self.browser
        if target == "windows":
            if self.windows is None:
                try:
                    self.windows = WindowsUIAutomation()
                except WindowsUIUnavailable:
                    raise
            return self.windows
        raise PolicyDenied(f"Unknown automation target: {target}")

    def close(self) -> None:
        if self.browser is not None:
            self.browser.close()
