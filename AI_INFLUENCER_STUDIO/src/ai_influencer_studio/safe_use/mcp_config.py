"""Playwright MCP configuration generation."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def playwright_mcp_config(
    headless: bool = True,
    isolated: bool = True,
    safe_wrapper: str | None = "ai_influencer_studio.safe_use.mcp_server",
    allowed_domains: list[str] | None = None,
    allowed_apps: list[str] | None = None,
    enable_windows: bool = False,
) -> dict[str, object]:
    """Return a client config for the policy-enforcing Playwright MCP wrapper."""
    if safe_wrapper:
        if not allowed_domains and not allowed_apps:
            raise ValueError("At least one allowed domain or app is required for the safe MCP bridge")
        args = ["-m", safe_wrapper]
        for domain in allowed_domains or []:
            args.extend(["--domain", domain])
        for app in allowed_apps or []:
            args.extend(["--app", app])
        if enable_windows:
            args.append("--enable-windows")
        if not headless:
            args.append("--headed")
        return {"mcpServers": {"playwright-safe": {"command": sys.executable, "args": args}}}

    args = ["-y", "@playwright/mcp@latest"]
    if isolated:
        args.append("--isolated")
    if headless:
        args.append("--headless")
    return {"mcpServers": {"playwright": {"command": "npx", "args": args}}}


def write_playwright_mcp_config(
    path: Path,
    headless: bool = True,
    isolated: bool = True,
    safe_wrapper: str | None = "ai_influencer_studio.safe_use.mcp_server",
    allowed_domains: list[str] | None = None,
    allowed_apps: list[str] | None = None,
    enable_windows: bool = False,
) -> Path:
    """Write a JSON MCP config atomically and without credentials."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(
            playwright_mcp_config(
                headless=headless,
                isolated=isolated,
                safe_wrapper=safe_wrapper,
                allowed_domains=allowed_domains,
                allowed_apps=allowed_apps,
                enable_windows=enable_windows,
            ),
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return path
