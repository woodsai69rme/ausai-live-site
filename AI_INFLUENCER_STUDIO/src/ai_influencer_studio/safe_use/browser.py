"""Playwright browser adapter used by the safe-use engine."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_influencer_studio.safe_use.models import ActionIntent, ActionTarget, Observation


def _safe_filename(value: str, default: str) -> str:
    candidate = Path(value).name
    if candidate in {"", ".", ".."} or candidate != value or any(char in value for char in ("/", "\\")):
        return default
    return candidate


def _flatten_accessibility(node: Any, limit: int, depth: int = 0) -> list[dict[str, Any]]:
    """Recursively flatten a Playwright accessibility snapshot."""
    if not isinstance(node, dict) or len(node) == 0:
        return []
    rows: list[dict[str, Any]] = [
        {"role": str(node.get("role", "")), "name": str(node.get("name", "") or ""), "value": str(node.get("value", "") or "")}
    ]
    for child in node.get("children", []) or []:
        if len(rows) >= limit:
            break
        rows.extend(_flatten_accessibility(child, limit, depth + 1))
    return rows[:limit]


class BrowserUnavailable(RuntimeError):
    """Raised when Playwright is not installed or cannot start."""


class PlaywrightBrowser:
    """Small synchronous Playwright wrapper with no LLM or policy decisions."""

    def __init__(self, headless: bool = True, screenshot_dir: Path | None = None) -> None:
        self.headless = headless
        self.screenshot_dir = screenshot_dir or Path.cwd() / "safe-use-screenshots"
        self._playwright: Any = None
        self._browser: Any = None
        self._context: Any = None
        self._page: Any = None

    def _ensure_page(self) -> Any:
        if self._page is not None:
            return self._page
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise BrowserUnavailable("Install the browser extra: pip install -e '.[browser]'") from exc
        try:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(headless=self.headless)
            self._context = self._browser.new_context()
            self._page = self._context.new_page()
        except Exception as exc:
            self.close()
            raise BrowserUnavailable(f"Playwright could not start: {exc}") from exc
        return self._page

    def observe(self, selector: str = "body", max_chars: int = 12000, screenshot: bool = False) -> Observation:
        page = self._ensure_page()
        element = page.query_selector(selector)
        text = element.inner_text() if element else ""
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text).strip()[:max_chars]
        elements = self._accessibility_tree(page)
        screenshot_path: str | None = None
        if screenshot:
            self.screenshot_dir.mkdir(parents=True, exist_ok=True)
            path = self.screenshot_dir / "observation.png"
            page.screenshot(path=str(path), full_page=True)
            screenshot_path = str(path)
        return Observation(
            target=ActionTarget.BROWSER,
            captured_at=datetime.now(UTC).isoformat(),
            title=page.title(),
            url=page.url,
            text=text,
            screenshot=screenshot_path,
            elements=elements,
            metadata={"selector": selector},
        )

    @staticmethod
    def _accessibility_tree(page: Any, limit: int = 200) -> list[dict[str, Any]]:
        """Flatten the Playwright accessibility tree into role/name/value rows."""
        try:
            snapshot = page.accessibility.snapshot()
        except Exception:
            return []
        return _flatten_accessibility(snapshot, limit)

    def current_url(self) -> str:
        """Return the active page URL, if a page has been started."""
        return str(self._page.url) if self._page is not None else ""

    def execute(self, intent: ActionIntent) -> dict[str, Any]:
        page = self._ensure_page()
        params = intent.parameters
        if intent.action == "navigate":
            response = page.goto(str(params["url"]), wait_until="domcontentloaded", timeout=60000)
            return {"url": page.url, "title": page.title(), "status": response.status if response else None}
        if intent.action == "observe":
            return self.observe(
                selector=str(params.get("selector", "body")),
                max_chars=int(params.get("max_chars", 12000)),
                screenshot=bool(params.get("screenshot", False)),
            ).to_dict()
        if intent.action == "click":
            if "x" in params and "y" in params:
                page.mouse.click(int(params["x"]), int(params["y"]))
                return {"x": int(params["x"]), "y": int(params["y"]), "url": page.url}
            page.locator(str(params["selector"])).click(timeout=15000)
            return {"selector": str(params["selector"]), "url": page.url}
        if intent.action == "fill":
            page.locator(str(params["selector"])).fill(str(params.get("value", "")), timeout=15000)
            return {"selector": str(params["selector"]), "filled": True}
        if intent.action == "press":
            page.locator(str(params["selector"])).press(str(params["key"]), timeout=15000)
            return {"selector": str(params["selector"]), "key": str(params["key"])}
        if intent.action == "select_option":
            page.locator(str(params["selector"])).select_option(str(params.get("value", "")), timeout=15000)
            return {"selector": str(params["selector"]), "value": str(params.get("value", ""))}
        if intent.action == "hover":
            page.locator(str(params["selector"])).hover(timeout=15000)
            return {"selector": str(params["selector"])}
        if intent.action == "type":
            page.keyboard.type(str(params.get("text", "")))
            return {"typed": str(params.get("text", ""))}
        if intent.action == "back":
            page.go_back()
            return {"url": page.url}
        if intent.action == "forward":
            page.go_forward()
            return {"url": page.url}
        if intent.action == "wait":
            page.wait_for_timeout(int(params.get("ms", 1000)))
            return {"ms": int(params.get("ms", 1000))}
        if intent.action == "evaluate":
            result = page.evaluate(str(params["script"]))
            return {"result": result}
        if intent.action == "scroll":
            page.mouse.wheel(0, int(params.get("delta_y", 700)))
            return {"delta_y": int(params.get("delta_y", 700))}
        if intent.action == "screenshot":
            self.screenshot_dir.mkdir(parents=True, exist_ok=True)
            path = self.screenshot_dir / _safe_filename(str(params.get("name", "action")), "action")
            if path.suffix.lower() != ".png":
                path = path.with_suffix(".png")
            page.screenshot(path=str(path), full_page=bool(params.get("full_page", False)))
            return {"path": str(path)}
        raise ValueError(f"Unsupported browser action: {intent.action}")

    def close(self) -> None:
        if self._context is not None:
            self._context.close()
        if self._browser is not None:
            self._browser.close()
        if self._playwright is not None:
            self._playwright.stop()
        self._page = None
        self._context = None
        self._browser = None
        self._playwright = None
