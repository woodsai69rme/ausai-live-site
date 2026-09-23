"""Tests for the content pipeline adapter's thumbnail + shorts helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from ai_influencer_studio.adapters.content import ContentAdapter
from ai_influencer_studio.config import StudioConfig


def _adapter(tmp_path: Path) -> ContentAdapter:
    return ContentAdapter(config=StudioConfig(data_dir=tmp_path, media_dir=tmp_path / "media"))


def test_generate_thumbnail_prompt_delegates_to_image_prompt(tmp_path: Path) -> None:
    adapter = _adapter(tmp_path)
    with patch.object(adapter, "generate_image_prompt", return_value="flux prompt") as mock:
        result = adapter.generate_thumbnail_prompt("My Title", style="vibrant")

    assert result == "flux prompt"
    mock.assert_called_once()


def test_create_shorts_delegates_to_repurposer(tmp_path: Path) -> None:
    adapter = _adapter(tmp_path)
    with patch("ai_influencer_studio.repurposer.VideoRepurposer") as mock_cls:
        mock_cls.return_value.create_multi_clips.return_value = [{"platform": "tiktok"}]

        result = adapter.create_shorts(
            "in.mp4",
            "out",
            platforms=["tiktok"],
            clip_duration=10.0,
            captions=["hello"],
        )

    assert result == [{"platform": "tiktok"}]
    mock_cls.return_value.create_multi_clips.assert_called_once_with(
        "in.mp4",
        "out",
        platforms=["tiktok"],
        clip_duration=10.0,
        captions=["hello"],
    )
