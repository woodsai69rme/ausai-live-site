"""Tests for the isolated safe browser/computer-use layer."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ai_influencer_studio.safe_use.audit import AuditLogger
from ai_influencer_studio.safe_use.engine import ApprovalRequired, SafeUseEngine
from ai_influencer_studio.safe_use.mcp_config import playwright_mcp_config, write_playwright_mcp_config
from ai_influencer_studio.safe_use.mcp_server import run_agent_task
from ai_influencer_studio.safe_use.models import ActionIntent, ActionTarget, Observation
from ai_influencer_studio.safe_use.policy import PolicyDenied, SafePolicy


@dataclass
class FakeBrowser:
    executed: list[ActionIntent]

    current: str = ""

    def observe(self, **kwargs: object) -> Observation:
        self.current = "https://example.test"
        return Observation(target=ActionTarget.BROWSER, captured_at="now", url=self.current, text="hello")

    def current_url(self) -> str:
        return self.current

    def execute(self, intent: ActionIntent) -> dict[str, object]:
        self.executed.append(intent)
        return {"ok": True, "action": intent.action, "url": self.current or "https://example.test"}

    def close(self) -> None:
        return None


def _intent(action: str = "click") -> ActionIntent:
    return ActionIntent(
        target=ActionTarget.BROWSER,
        action=action,
        parameters={"selector": "button.save", "url": "https://example.test"},
    )


def test_policy_requires_allowlisted_domain() -> None:
    policy = SafePolicy(allowed_domains={"example.test"})
    policy.check(_intent("navigate"))
    with pytest.raises(PolicyDenied):
        policy.check(ActionIntent(target=ActionTarget.BROWSER, action="navigate", parameters={"url": "https://evil.test"}))


def test_policy_blocks_sensitive_fields_by_default() -> None:
    policy = SafePolicy(allowed_domains={"example.test"})
    intent = ActionIntent(
        target=ActionTarget.BROWSER,
        action="fill",
        parameters={"selector": "#password", "field": "password", "value": "secret"},
    )
    with pytest.raises(PolicyDenied):
        policy.check(intent)


def test_execute_rejects_tampered_intent_after_approval(tmp_path: Path) -> None:
    browser = FakeBrowser([])
    engine = SafeUseEngine(SafePolicy(allowed_domains={"example.test"}), tmp_path / "audit.jsonl", browser=browser)
    engine.observe("browser", url="https://example.test")
    approval = engine.approve(_intent())
    tampered = ActionIntent(
        target=ActionTarget.BROWSER,
        action="click",
        parameters={"selector": "button.delete", "url": "https://example.test"},
    )
    with pytest.raises(ApprovalRequired):
        engine.execute(tampered, approval.token)


def test_execute_requires_and_consumes_single_use_approval(tmp_path: Path) -> None:
    browser = FakeBrowser([])
    engine = SafeUseEngine(SafePolicy(allowed_domains={"example.test"}), tmp_path / "audit.jsonl", browser=browser)
    engine.observe("browser", url="https://example.test")
    with pytest.raises(ApprovalRequired):
        engine.execute(_intent())

    browser.executed.clear()
    approval = engine.approve(_intent())
    result = engine.execute(_intent(), approval.token)
    assert result.executed is True
    assert len(browser.executed) == 1
    with pytest.raises(ApprovalRequired):
        engine.execute(_intent("click"), approval.token)
    engine.close()


def test_windows_observation_requires_allowlisted_app(tmp_path: Path) -> None:
    engine = SafeUseEngine(SafePolicy(allowed_domains={"example.test"}), tmp_path / "audit.jsonl")
    with pytest.raises(PolicyDenied):
        engine.observe("windows", app="Notepad")


def test_observation_requires_browser_allowlist_and_url(tmp_path: Path) -> None:
    engine = SafeUseEngine(SafePolicy(allowed_domains={"example.test"}), tmp_path / "audit.jsonl", browser=FakeBrowser([]))
    with pytest.raises(PolicyDenied):
        engine.observe("browser")
    with pytest.raises(PolicyDenied):
        engine.observe("browser", url="https://evil.test")


def test_audit_redacts_secrets(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    AuditLogger(path).record("test", {"value": "Bearer abc password=secret https://example.test/?token=hidden"})
    text = path.read_text(encoding="utf-8")
    assert "abc" not in text
    assert "secret" not in text
    assert "hidden" not in text


def test_audit_redacts_action_values(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    AuditLogger(path).record("execute", {"intent": {"action": "fill", "parameters": {"value": "private"}}})
    assert "private" not in path.read_text(encoding="utf-8")


def test_policy_allows_expanded_browser_actions() -> None:
    policy = SafePolicy(allowed_domains={"example.test"})
    for action in ("select_option", "hover", "type", "back", "forward", "wait", "evaluate"):
        policy.check(
            ActionIntent(
                target=ActionTarget.BROWSER,
                action=action,
                parameters={"current_url": "https://example.test", "selector": "x"},
            )
        )
    assert policy.requires_approval(
        ActionIntent(target=ActionTarget.BROWSER, action="evaluate", parameters={"current_url": "https://example.test", "script": "1"})
    )
    assert "close" in policy.allowed_windows_actions


def test_mcp_config_is_isolated_and_secret_free(tmp_path: Path) -> None:
    config = playwright_mcp_config(allowed_domains=["example.test"])
    assert config["mcpServers"]["playwright-safe"]["args"] == ["-m", "ai_influencer_studio.safe_use.mcp_server", "--domain", "example.test"]
    path = write_playwright_mcp_config(tmp_path / "mcp.json", allowed_domains=["example.test"])
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["mcpServers"]["playwright-safe"]["args"] == ["-m", "ai_influencer_studio.safe_use.mcp_server", "--domain", "example.test"]
    assert "API_KEY" not in path.read_text(encoding="utf-8")


def test_run_agent_task_splits_models_and_runs_agent() -> None:
    fake_agent = MagicMock()
    fake_agent.run_task.return_value = {"status": "done"}
    with patch("ai_influencer_studio.safe_use.agent.MultiModelAgent", return_value=fake_agent) as mock_agent_cls:
        result = run_agent_task(FakeBrowser([]), "a::1, b::2", "do it", url="https://example.test", max_steps=5)

    assert result == {"status": "done"}
    mock_agent_cls.assert_called_once()
    _, kwargs = mock_agent_cls.call_args
    assert kwargs["models"] == ["a::1", "b::2"]
    assert kwargs["max_steps"] == 5
    fake_agent.run_task.assert_called_once_with("do it", target="browser", url="https://example.test")


def test_run_agent_task_requires_at_least_one_model() -> None:
    with pytest.raises(ValueError, match="At least one"):
        run_agent_task(FakeBrowser([]), "  ,  ", "do it")
