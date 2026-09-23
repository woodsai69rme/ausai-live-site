"""Optional Windows UI Automation adapter backed by uiautomation."""

from __future__ import annotations

import platform
from pathlib import Path
from typing import Any

from ai_influencer_studio.safe_use.models import ActionIntent, ActionTarget, Observation


def _safe_filename(value: str, default: str) -> str:
    candidate = Path(value).name
    if candidate in {"", ".", ".."} or candidate != value or any(char in value for char in ("/", "\\")):
        return default
    return candidate

class WindowsUIUnavailable(RuntimeError):
    """Raised when Windows UI Automation is unavailable."""


class WindowsUIAutomation:
    """Conservative wrapper around Python-UIAutomation-for-Windows."""

    def __init__(self, screenshot_dir: Path | None = None) -> None:
        if platform.system() != "Windows":
            raise WindowsUIUnavailable("Windows UI Automation is available only on Windows")
        self.screenshot_dir = screenshot_dir or Path.cwd() / "safe-use-screenshots"
        try:
            import uiautomation as auto
        except ImportError as exc:
            raise WindowsUIUnavailable("Install the Windows extra: pip install -e '.[windows]'") from exc
        self.auto: Any = auto

    def observe(self, app: str | None = None, max_depth: int = 3, screenshot: bool = False) -> Observation:
        root = self.auto.GetRootControl()
        window = root
        if app:
            window = root.WindowControl(searchDepth=1, Name=app)
            if not window.Exists(2):
                raise LookupError(f"Windows application window not found: {app}")
        elements = self._walk(window, depth=max_depth)
        screenshot_path: str | None = None
        if screenshot:
            self.screenshot_dir.mkdir(parents=True, exist_ok=True)
            path = self.screenshot_dir / "windows-observation.png"
            self.auto.TakeScreenshot(str(path))
            screenshot_path = str(path)
        title = str(getattr(window, "Name", "") or "")
        return Observation(
            target=ActionTarget.WINDOWS,
            captured_at=__import__("datetime").datetime.now(__import__("datetime").UTC).isoformat(),
            title=title,
            text="\n".join(item.get("name", "") for item in elements if item.get("name")),
            screenshot=screenshot_path,
            elements=elements,
            metadata={"app": app, "max_depth": max_depth},
        )

    def execute(self, intent: ActionIntent) -> dict[str, Any]:
        params = intent.parameters
        control = self._find_control(params)
        if intent.action == "observe":
            return self.observe(app=params.get("app"), max_depth=int(params.get("max_depth", 3))).to_dict()
        if intent.action == "focus":
            control.SetFocus()
            return {"focused": True, "name": getattr(control, "Name", "")}
        if intent.action == "click":
            control.Click()
            return {"clicked": True, "name": getattr(control, "Name", "")}
        if intent.action == "type":
            value = str(params.get("value", ""))
            control.Click()
            control.SendKeys(value, interval=0.01)
            return {"typed": True, "length": len(value)}
        if intent.action == "hotkey":
            keys = str(params.get("keys", ""))
            self.auto.SendKeys(keys)
            return {"hotkey": keys}
        if intent.action == "close":
            control.GetWindowPattern().Close()
            return {"closed": True, "name": getattr(control, "Name", "")}
        if intent.action == "screenshot":
            self.screenshot_dir.mkdir(parents=True, exist_ok=True)
            path = self.screenshot_dir / _safe_filename(str(params.get("name", "windows")), "windows")
            if path.suffix.lower() != ".png":
                path = path.with_suffix(".png")
            self.auto.TakeScreenshot(str(path))
            return {"path": str(path)}
        raise ValueError(f"Unsupported Windows action: {intent.action}")

    def _find_control(self, params: dict[str, Any]) -> Any:
        root = self.auto.GetRootControl()
        app = str(params.get("app", ""))
        if not app:
            raise ValueError("Windows actions require an allowlisted app name")
        window = root.WindowControl(searchDepth=1, Name=app)
        if not window.Exists(2):
            raise LookupError(f"Windows application window not found: {app}")
        name = str(params.get("name", ""))
        control_type = str(params.get("control_type", ""))
        if not name:
            return window
        if control_type.lower() == "button":
            return window.ButtonControl(searchDepth=8, Name=name)
        if control_type.lower() == "edit":
            return window.EditControl(searchDepth=8, Name=name)
        return window.Control(searchDepth=8, Name=name)

    def _walk(self, control: Any, depth: int, current: int = 0) -> list[dict[str, Any]]:
        if current > depth:
            return []
        result = [{
            "name": str(getattr(control, "Name", "") or ""),
            "control_type": str(getattr(control, "ControlTypeName", "") or ""),
            "depth": current,
        }]
        if current == depth:
            return result
        try:
            children = control.GetChildren()
        except Exception:
            return result
        for child in children[:100]:
            result.extend(self._walk(child, depth, current + 1))
        return result
