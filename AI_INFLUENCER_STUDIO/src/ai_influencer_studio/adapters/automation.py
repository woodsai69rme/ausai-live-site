"""Adapter for the legacy social media automation scripts.

Wraps ``SCRIPTS/PYTHON/social_media_automation.py`` (scheduling, posting,
engagement) and ``ComfyUI/tools/auto_poster.py`` (browser-use upload) so the
studio can reuse them without duplicating code.
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from ai_influencer_studio.adapters.platforms.base import BasePlatformAdapter
from ai_influencer_studio.adapters.platforms.facebook import FacebookAdapter
from ai_influencer_studio.adapters.platforms.instagram import InstagramAdapter
from ai_influencer_studio.adapters.platforms.tiktok import TikTokAdapter
from ai_influencer_studio.adapters.platforms.twitter import TwitterAdapter
from ai_influencer_studio.adapters.platforms.youtube import YouTubeAdapter
from ai_influencer_studio.config import StudioConfig
from ai_influencer_studio.database import ScheduledPost, StudioDatabase

_AUTOMATION_MODULE: Any | None = None


class AutomationAdapter:
    """High-level wrapper around legacy social media automation."""

    def __init__(self, config: StudioConfig | None = None) -> None:
        self.config = config or StudioConfig.from_file()
        self.db = StudioDatabase(self.config.data_dir / "studio.db")

    def schedule_post(
        self,
        platform: str,
        content: str,
        scheduled_at: datetime,
        media_paths: list[str] | None = None,
        hashtags: list[str] | None = None,
    ) -> int:
        """Store a scheduled post in the studio database."""
        post = ScheduledPost(
            platform=platform,
            content=content,
            scheduled_at=scheduled_at,
            media_paths=media_paths or [],
            hashtags=hashtags or [],
        )
        return self.db.add_scheduled_post(post)

    def list_scheduled_posts(self) -> list[ScheduledPost]:
        """Return all scheduled posts ordered by time."""
        return self.db.get_all_posts()

    def list_pending_posts(self) -> list[ScheduledPost]:
        """Return pending posts ordered by time."""
        return self.db.get_pending_posts()

    def mark_posted(self, post_id: int) -> None:
        """Mark a scheduled post as posted."""
        self.db.mark_posted(post_id)

    def _load_module(self) -> Any:
        global _AUTOMATION_MODULE
        if _AUTOMATION_MODULE is not None:
            return _AUTOMATION_MODULE

        script_path = Path(self.config.social_media_automation_script)
        if not script_path.exists():
            raise FileNotFoundError(f"Legacy automation script not found: {script_path}")

        pipeline_dir = str(script_path.parent)
        inserted = False
        if pipeline_dir not in sys.path:
            sys.path.insert(0, pipeline_dir)
            inserted = True

        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location("social_media_automation", script_path)
            if spec is None or spec.loader is None:  # pragma: no cover
                raise ImportError(f"Could not load spec for {script_path}")
            module = importlib.util.module_from_spec(spec)
            sys.modules["social_media_automation"] = module
            spec.loader.exec_module(module)
            _AUTOMATION_MODULE = module
            return module
        finally:
            if inserted:
                sys.path.remove(pipeline_dir)

    def _get_platform_adapter(self, platform: str) -> BasePlatformAdapter:
        """Return the appropriate platform adapter for the given platform name."""
        module = self._load_module()
        config_path = self.config.data_dir / "social_media_config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        automation = module.SocialMediaAutomation(str(config_path))

        adapters: dict[str, BasePlatformAdapter] = {
            "twitter": TwitterAdapter(automation),
            "instagram": InstagramAdapter(automation),
            "facebook": FacebookAdapter(automation),
            "tiktok": TikTokAdapter(self.config),
            "youtube": YouTubeAdapter(self.config),
        }
        adapter = adapters.get(platform.lower())
        if adapter is None:
            raise ValueError(f"Unsupported platform for API posting: {platform}")
        return adapter

    def post_via_api(
        self,
        platform: str,
        content: str,
        media_path: str | None = None,
    ) -> dict[str, Any]:
        """Post immediately via the appropriate platform adapter."""
        media_paths = [media_path] if media_path else []
        adapter = self._get_platform_adapter(platform)
        return adapter.publish(content, media_paths)

    def _push_to_api(self, url: str, payload: dict[str, Any], api_key: str | None = None) -> dict[str, Any]:
        """POST a JSON payload to an external API and return status info."""
        headers: dict[str, str] = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return {"status": response.status_code, "body": response.text}

    def push_to_n8n(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Push a payload to the configured n8n webhook."""
        url = self.config.n8n_webhook_url
        if not url:
            raise ValueError("n8n_webhook_url is not configured")
        return self._push_to_api(url, payload)

    def push_to_postiz(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Push a payload to the configured Postiz API."""
        url = self.config.postiz_api_url
        api_key = self.config.postiz_api_key
        if not url or not api_key:
            raise ValueError("postiz_api_url and postiz_api_key must be configured")
        return self._push_to_api(url, payload, api_key=api_key)

    def push_to_mixpost(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Push a payload to the configured Mixpost API."""
        url = self.config.mixpost_api_url
        api_key = self.config.mixpost_api_key
        if not url or not api_key:
            raise ValueError("mixpost_api_url and mixpost_api_key must be configured")
        return self._push_to_api(url, payload, api_key=api_key)

    def push_to_scheduler(
        self,
        scheduler: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Push a payload to the named external scheduler."""
        if scheduler == "n8n":
            return self.push_to_n8n(payload)
        if scheduler == "postiz":
            return self.push_to_postiz(payload)
        if scheduler == "mixpost":
            return self.push_to_mixpost(payload)
        raise ValueError(f"Unsupported scheduler: {scheduler}")

    def post_via_postiz(
        self,
        content: str,
        media_urls: list[str] | None = None,
        platforms: list[str] | None = None,
        scheduled_at: datetime | None = None,
    ) -> dict[str, Any]:
        """Schedule a post through the Postiz API.

        Builds the Postiz v2 ``/api/v1/posts`` payload shape (``text``,
        ``platforms``, ``media`` URL list, optional ``scheduledAt``). Postiz
        needs hosted media, so local paths are rejected with a clear message
        rather than silently dropped.
        """
        media_urls = media_urls or []
        platforms = platforms or []
        for media in media_urls:
            if not str(media).startswith(("http://", "https://")):
                raise ValueError(
                    f"Postiz needs hosted media URLs, got local path: {media}. "
                    "Upload the file first (e.g. via the gdrive or youtube uploader)."
                )
        if not platforms:
            raise ValueError("postiz requires at least one target platform")
        payload: dict[str, Any] = {
            "text": content,
            "platforms": platforms,
            "media": [{"url": url} for url in media_urls],
        }
        if scheduled_at:
            payload["scheduledAt"] = scheduled_at.isoformat()
        return {"scheduler": "postiz", **self.push_to_postiz(payload)}

    def post_via_mixpost(
        self,
        content: str,
        media_urls: list[str] | None = None,
        platforms: list[str] | None = None,
        scheduled_at: datetime | None = None,
    ) -> dict[str, Any]:
        """Schedule a post through the Mixpost webhook.

        Mixpost is a Laravel app; its webhook accepts a free-form post object.
        Local media paths are passed through as-is because Mixpost deployments
        commonly serve files from the same host.
        """
        payload: dict[str, Any] = {
            "name": (content[:120] or "Untitled post"),
            "content": content,
            "media": media_urls or [],
            "platforms": platforms or [],
        }
        if scheduled_at:
            payload["scheduled_at"] = scheduled_at.isoformat()
        return {"scheduler": "mixpost", **self.push_to_mixpost(payload)}

    def post_via_browser(
        self,
        platform: str,
        video_path: Path | str,
        description: str,
        hashtags: str = "",
    ) -> dict[str, Any]:
        """Upload a video via the browser-use auto poster.

        Runs ``ComfyUI/tools/auto_poster.py`` as a subprocess.
        """
        script_path = Path(self.config.auto_poster_script)
        if not script_path.exists():
            raise FileNotFoundError(f"Auto poster script not found: {script_path}")

        cmd = [
            sys.executable,
            str(script_path),
            "--platform",
            platform,
            "--video",
            str(video_path),
            "--description",
            description,
        ]
        if hashtags:
            cmd += ["--hashtags", hashtags]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1800,
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "platform": platform,
        }
