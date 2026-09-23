"""YouTube platform adapter."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

from ai_influencer_studio.adapters.platforms.base import BasePlatformAdapter
from ai_influencer_studio.config import StudioConfig


class YouTubeAdapter(BasePlatformAdapter):
    """Adapter for uploading videos to YouTube via the browser-use auto poster."""

    platform_name = "youtube"

    def __init__(self, config: StudioConfig) -> None:
        self._config = config

    def publish(self, content: str, media_paths: list[str] | None = None) -> dict[str, Any]:
        if not media_paths:
            raise ValueError("YouTube posts require a media_path")
        script_path = Path(self._config.auto_poster_script)
        if not script_path.exists():
            raise FileNotFoundError(f"Auto poster script not found: {script_path}")

        result = subprocess.run(
            [
                sys.executable,
                str(script_path),
                "--platform",
                "youtube",
                "--video",
                media_paths[0],
                "--description",
                content,
            ],
            capture_output=True,
            text=True,
            timeout=1800,
        )
        return {
            "platform": self.platform_name,
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
