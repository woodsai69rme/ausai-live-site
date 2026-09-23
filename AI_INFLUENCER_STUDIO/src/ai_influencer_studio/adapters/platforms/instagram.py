"""Instagram platform adapter."""

from __future__ import annotations

from typing import Any

from ai_influencer_studio.adapters.platforms.base import BasePlatformAdapter


class InstagramAdapter(BasePlatformAdapter):
    """Adapter for posting to Instagram via the legacy automation script."""

    platform_name = "instagram"

    def __init__(self, automation: Any) -> None:
        self._automation = automation

    def publish(self, content: str, media_paths: list[str] | None = None) -> dict[str, Any]:
        if not media_paths:
            raise ValueError("Instagram posts require a media_path")
        success = self._automation.post_to_instagram(content, media_paths[0])
        return {"platform": self.platform_name, "success": success}
