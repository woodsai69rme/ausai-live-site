"""Adapter for the legacy AI influencer content pipeline.

Wraps ``SCRIPTS/PYTHON/ai_influencer_pipeline.py`` so the studio can reuse its
generation logic without duplicating code.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from ai_influencer_studio.config import StudioConfig


def _pipeline_module(config: StudioConfig) -> Any:
    """Import the legacy pipeline module dynamically.

    The legacy script lives outside the package, so we inject its directory into
    ``sys.path`` temporarily and import it by name.
    """
    script_path = Path(config.ai_influencer_pipeline_script)
    if not script_path.exists():
        raise FileNotFoundError(f"Legacy pipeline script not found: {script_path}")

    pipeline_dir = str(script_path.parent)
    inserted = False
    if pipeline_dir not in sys.path:
        sys.path.insert(0, pipeline_dir)
        inserted = True

    try:
        # Import module by stem so we can call its classes directly.
        import importlib.util

        spec = importlib.util.spec_from_file_location("ai_influencer_pipeline", script_path)
        if spec is None or spec.loader is None:  # pragma: no cover
            raise ImportError(f"Could not load spec for {script_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules["ai_influencer_pipeline"] = module
        spec.loader.exec_module(module)
        return module
    finally:
        if inserted:
            sys.path.remove(pipeline_dir)


_MODULE_CACHE: dict[str, Any] = {}
_PIPELINE_CACHE: dict[str, Any] = {}


class ContentAdapter:
    """High-level wrapper around ``AIInfluencerPipeline``."""

    def __init__(self, config: StudioConfig | None = None) -> None:
        self.config = config or StudioConfig.from_file()

    def _load(self) -> Any:
        script_path = str(self.config.ai_influencer_pipeline_script)
        if script_path not in _MODULE_CACHE:
            _MODULE_CACHE[script_path] = _pipeline_module(self.config)
        return _MODULE_CACHE[script_path]

    def _pipeline_instance(self) -> Any:
        config_path = str(self.config.data_dir / "ai_influencer_config.json")
        if config_path not in _PIPELINE_CACHE:
            module = self._load()
            # The legacy script writes a config file if missing; point it at the
            # studio data dir so everything is co-located.
            config_path_obj = Path(config_path)
            config_path_obj.parent.mkdir(parents=True, exist_ok=True)
            _PIPELINE_CACHE[config_path] = module.AIInfluencerPipeline(config_path)
        return _PIPELINE_CACHE[config_path]

    def generate_post(self, topic: str, platform: str = "instagram") -> dict[str, Any]:
        """Generate a complete social post package (text + hashtags + visual)."""
        pipeline = self._pipeline_instance()
        result = pipeline.generate_complete_post(topic, platform, include_visual=True)
        return dict(result)

    def generate_caption(self, summary: str, platform: str = "instagram") -> str:
        """Generate a platform-appropriate caption."""
        pipeline = self._pipeline_instance()
        return str(pipeline.generate_caption(summary, platform))

    def generate_blog(self, topic: str, word_count: int = 500) -> str:
        """Generate a blog post."""
        pipeline = self._pipeline_instance()
        return str(pipeline.generate_blog_post(topic, word_count))

    def generate_video_script(self, topic: str, duration_minutes: int = 2) -> str:
        """Generate a video script with timing cues."""
        pipeline = self._pipeline_instance()
        return str(pipeline.generate_video_script(topic, duration_minutes))

    def generate_content_calendar(
        self,
        topics: list[str],
        days: int = 7,
    ) -> list[dict[str, Any]]:
        """Generate a multi-day content calendar."""
        pipeline = self._pipeline_instance()
        calendar = pipeline.generate_content_calendar(topics, days)
        return [dict(day) for day in calendar]

    def generate_image_prompt(self, description: str, style: str = "modern") -> str:
        """Generate an image generation prompt from a description."""
        pipeline = self._pipeline_instance()
        return str(pipeline.generate_image_prompt(description, style))

    def generate_thumbnail_prompt(self, title: str, style: str = "vibrant") -> str:
        """Generate a Flux/ComfyUI-ready thumbnail prompt for a video title."""
        return self.generate_image_prompt(f"YouTube thumbnail for: {title}", style=style)

    def create_shorts(
        self,
        input_path: str,
        output_dir: str,
        platforms: list[str] | None = None,
        clip_duration: float = 15.0,
        captions: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Turn a long video into platform-native vertical Shorts/Reels/TikToks."""
        from ai_influencer_studio.repurposer import VideoRepurposer

        return VideoRepurposer().create_multi_clips(
            input_path,
            output_dir,
            platforms=platforms,
            clip_duration=clip_duration,
            captions=captions,
        )
