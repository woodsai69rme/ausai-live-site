"""Tests for platform-specific upload adapters."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ai_influencer_studio.adapters.platforms.tiktok import TikTokAdapter
from ai_influencer_studio.adapters.platforms.youtube import YouTubeAdapter
from ai_influencer_studio.config import StudioConfig


def _make_config(tmp_path: Path) -> StudioConfig:
    return StudioConfig(
        data_dir=tmp_path / "data",
        media_dir=tmp_path / "media",
        auto_poster_script=tmp_path / "auto_poster.py",
    )


def test_tiktok_adapter_publishes_video(tmp_path: Path) -> None:
    config = _make_config(tmp_path)
    (tmp_path / "auto_poster.py").write_text("# placeholder")
    adapter = TikTokAdapter(config)

    with patch("ai_influencer_studio.adapters.platforms.tiktok.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
        result = adapter.publish("My TikTok", media_paths=[str(tmp_path / "video.mp4")])

    assert result["success"] is True
    assert result["platform"] == "tiktok"
    assert result["returncode"] == 0


def test_tiktok_adapter_requires_media(tmp_path: Path) -> None:
    config = _make_config(tmp_path)
    (tmp_path / "auto_poster.py").write_text("# placeholder")
    adapter = TikTokAdapter(config)

    with pytest.raises(ValueError, match="media"):
        adapter.publish("No media")


def test_youtube_adapter_publishes_video(tmp_path: Path) -> None:
    config = _make_config(tmp_path)
    (tmp_path / "auto_poster.py").write_text("# placeholder")
    adapter = YouTubeAdapter(config)

    with patch("ai_influencer_studio.adapters.platforms.youtube.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
        result = adapter.publish("My YouTube video", media_paths=[str(tmp_path / "video.mp4")])

    assert result["success"] is True
    assert result["platform"] == "youtube"
    assert result["returncode"] == 0


def test_youtube_adapter_requires_media(tmp_path: Path) -> None:
    config = _make_config(tmp_path)
    (tmp_path / "auto_poster.py").write_text("# placeholder")
    adapter = YouTubeAdapter(config)

    with pytest.raises(ValueError, match="media"):
        adapter.publish("No media")


def test_tiktok_adapter_raises_when_script_missing(tmp_path: Path) -> None:
    config = _make_config(tmp_path)
    # Do not create auto_poster.py so the script path is missing.
    adapter = TikTokAdapter(config)

    with pytest.raises(FileNotFoundError, match="Auto poster script not found"):
        adapter.publish("Video", media_paths=[str(tmp_path / "video.mp4")])
