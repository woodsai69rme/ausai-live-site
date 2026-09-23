"""Facebook platform adapter."""

from __future__ import annotations

from typing import Any

from ai_influencer_studio.adapters.platforms.base import BasePlatformAdapter


class FacebookAdapter(BasePlatformAdapter):
    """Adapter for posting to Facebook via the legacy automation script."""

    platform_name = "facebook"

    def __init__(self, automation: Any) -> None:
        self._automation = automation

    def publish(self, content: str, media_paths: list[str] | None = None) -> dict[str, Any]:
        media_path = media_paths[0] if media_paths else None
        success = self._automation.post_to_facebook(content, media_path)
        return {"platform": self.platform_name, "success": success}
