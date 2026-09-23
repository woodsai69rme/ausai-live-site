"""Tests for ai_influencer_studio.repurposer."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ai_influencer_studio.repurposer import PLATFORM_SPECS, VideoRepurposer


@pytest.fixture
def repurposer() -> VideoRepurposer:
    return VideoRepurposer(ffmpeg_path="ffmpeg")


def test_platform_specs_define_common_platforms() -> None:
    assert "tiktok" in PLATFORM_SPECS
    assert "instagram" in PLATFORM_SPECS
    assert "youtube" in PLATFORM_SPECS
    assert PLATFORM_SPECS["tiktok"].width == 1080
    assert PLATFORM_SPECS["tiktok"].height == 1920


def test_get_video_info_parses_ffprobe_output(repurposer: VideoRepurposer) -> None:
    fake_output = '{"streams": [{"width": 1920, "height": 1080, "duration": "120.5"}]}'
    with patch("ai_influencer_studio.repurposer.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout=fake_output, stderr="")
        info = repurposer.get_video_info("/tmp/video.mp4")
    assert info["width"] == 1920
    assert info["height"] == 1080
    assert info["duration"] == 120.5


def test_get_video_info_raises_on_ffprobe_failure(repurposer: VideoRepurposer) -> None:
    with patch("ai_influencer_studio.repurposer.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="boom")
        with pytest.raises(RuntimeError, match="ffprobe failed"):
            repurposer.get_video_info("/tmp/video.mp4")


def test_create_vertical_cut_builds_ffmpeg_command(repurposer: VideoRepurposer, tmp_path: Path) -> None:
    input_path = tmp_path / "input.mp4"
    input_path.write_text("video")
    output_path = tmp_path / "output.mp4"

    fake_info = '{"streams": [{"width": 1920, "height": 1080, "duration": "60.0"}]}'
    with patch("ai_influencer_studio.repurposer.subprocess.run") as mock_run:
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=fake_info, stderr=""),
            MagicMock(returncode=0, stdout="", stderr=""),
        ]
        result = repurposer.create_vertical_cut(input_path, output_path, platform="tiktok", caption="Hello")

    assert result["platform"] == "tiktok"
    assert result["caption"] == "Hello"
    assert result["input"] == str(input_path)
    assert result["output"] == str(output_path)
    assert mock_run.call_count == 2


def test_create_vertical_cut_rejects_unsupported_platform(repurposer: VideoRepurposer, tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unsupported platform"):
        repurposer.create_vertical_cut(tmp_path / "input.mp4", tmp_path / "output.mp4", platform="unknown")


def test_create_multi_clips_splits_video(repurposer: VideoRepurposer, tmp_path: Path) -> None:
    input_path = tmp_path / "input.mp4"
    input_path.write_text("video")
    output_dir = tmp_path / "out"

    fake_info = '{"streams": [{"width": 1920, "height": 1080, "duration": "30.0"}]}'
    with patch("ai_influencer_studio.repurposer.subprocess.run") as mock_run:
        # create_multi_clips calls get_video_info once, then for each of the
        # two 15-second clips it calls create_vertical_cut which calls
        # get_video_info and ffmpeg: 1 + 2*2 = 5 subprocess.run calls.
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=fake_info, stderr=""),
            MagicMock(returncode=0, stdout=fake_info, stderr=""),
            MagicMock(returncode=0, stdout="", stderr=""),
            MagicMock(returncode=0, stdout=fake_info, stderr=""),
            MagicMock(returncode=0, stdout="", stderr=""),
        ]
        results = repurposer.create_multi_clips(
            input_path,
            output_dir,
            platforms=["tiktok"],
            clip_duration=15.0,
        )

    assert len(results) == 2
    assert all(r["platform"] == "tiktok" for r in results)
