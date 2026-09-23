"""Policy-enforcing MCP server for safe browser/computer use."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from ai_influencer_studio.safe_use.browser import PlaywrightBrowser
from ai_influencer_studio.safe_use.engine import SafeUseEngine
from ai_influencer_studio.safe_use.models import ActionIntent, ActionTarget
from ai_influencer_studio.safe_use.policy import SafePolicy
from ai_influencer_studio.safe_use.windows_ui import WindowsUIAutomation


def create_server(
    allowed_domains: set[str],
    allowed_apps: set[str],
    audit_path: Path,
    headless: bool = True,
    enable_windows: bool = False,
) -> Any:
    """Create a FastMCP server; import the optional SDK only when launched."""
    if not allowed_domains and not allowed_apps:
        raise ValueError("At least one allowed domain or app is required")
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError("Install the MCP extra: pip install -e '.[mcp,browser]'") from exc

    browser = PlaywrightBrowser(headless=headless)
    windows = WindowsUIAutomation() if enable_windows else None
    engine = SafeUseEngine(
        policy=SafePolicy(allowed_domains=allowed_domains, allowed_apps=allowed_apps),
        audit_path=audit_path,
        browser=browser,
        windows=windows,
    )
    server = FastMCP("ai-influencer-safe-use")

    def parse_intent(payload: dict[str, Any]) -> ActionIntent:
        return ActionIntent(
            target=ActionTarget(str(payload["target"])),
            action=str(payload["action"]),
            parameters=dict(payload.get("parameters", {})),
            reason=str(payload.get("reason", "")),
            requested_by=str(payload.get("requested_by", "mcp")),
            intent_id=str(payload.get("intent_id", "")),
        )

    @server.tool()
    def observe_browser(url: str, selector: str = "body", max_chars: int = 12000) -> dict[str, Any]:
        """Observe one allowlisted browser URL without mutating page state."""
        return engine.observe("browser", url=url, selector=selector, max_chars=max_chars).to_dict()

    @server.tool()
    def propose_action(intent: dict[str, Any]) -> dict[str, Any]:
        """Validate an action and return its canonical approval-ready intent."""
        return engine.propose(parse_intent(intent)).to_dict()

    @server.tool()
    def approve_action(intent: dict[str, Any]) -> dict[str, Any]:
        """Create a short-lived single-use approval for an exact intent."""
        approval = engine.approve(parse_intent(intent), approved_by="mcp-operator")
        return {
            "token": approval.token,
            "intent_id": approval.intent_id,
            "expires_at": approval.expires_at,
            "approved_by": approval.approved_by,
        }

    @server.tool()
    def execute_action(intent: dict[str, Any], approval_token: str) -> dict[str, Any]:
        """Execute one policy-checked action with a matching approval token."""
        return engine.execute(parse_intent(intent), approval_token=approval_token).to_dict()

    @server.tool()
    def run_task(task: str, models: str, url: str = "", max_steps: int = 12) -> dict[str, Any]:
        """Run a natural-language task with several concurrent vision models.

        ``models`` is a comma-separated list of ``provider::model_id`` refs.
        Every executed action still passes the safe-use policy allowlist and is
        recorded in the audit log.
        """
        return run_agent_task(engine, models, task, url, max_steps)

    return server


def run_agent_task(engine: Any, models: str, task: str, url: str = "", max_steps: int = 12) -> dict[str, Any]:
    """Run a natural-language browser task with several concurrent vision models.

    ``models`` is a comma-separated list of ``provider::model_id`` refs. This is
    separated from the MCP tool so it can be unit-tested without the FastMCP SDK.
    """
    from ai_influencer_studio.safe_use.agent import MultiModelAgent
    from ai_influencer_studio.safe_use.multi_model import MultiModelClient

    references = [ref.strip() for ref in models.split(",") if ref.strip()]
    if not references:
        raise ValueError("At least one comma-separated model reference is required")
    agent = MultiModelAgent(engine, models=references, client=MultiModelClient(), max_steps=max_steps)
    return agent.run_task(task, target="browser", url=url or None)


def main() -> int:
    parser = argparse.ArgumentParser(description="Policy-enforcing safe-use MCP server")
    parser.add_argument("--domain", action="append", default=[])
    parser.add_argument("--app", action="append", default=[])
    parser.add_argument("--audit", type=Path, default=Path("safe-use-audit.jsonl"))
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--enable-windows", action="store_true")
    args = parser.parse_args()
    if not args.domain and not args.app:
        parser.error("At least one --domain or --app allowlist entry is required")
    server = create_server(
        set(args.domain),
        set(args.app),
        args.audit,
        headless=not args.headed,
        enable_windows=args.enable_windows,
    )
    server.run(transport="stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
