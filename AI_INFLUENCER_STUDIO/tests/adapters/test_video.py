"""Tests for ai_influencer_studio.adapters.video."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from ai_influencer_studio.adapters.video import VideoAdapter
from ai_influencer_studio.config import StudioConfig


def test_execute_music_video_plan_runs_orchestrator(tmp_path: Path) -> None:
    audio = tmp_path / "song.mp3"
    audio.write_text("audio")
    plan = {
        "song_name": "Song",
        "audio_path": str(audio),
        "genre": "pop",
        "mood": "upbeat",
    }

    config = StudioConfig(
        data_dir=tmp_path / "data",
        media_dir=tmp_path / "media",
        comfyui_orchestrator_script=str(tmp_path / "orchestrator.py"),
    )
    (tmp_path / "orchestrator.py").write_text("print('ok')")

    adapter = VideoAdapter(config)
    with patch("ai_influencer_studio.adapters.video.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
        result = adapter.execute_music_video_plan(plan)

    assert result["returncode"] == 0
    assert result["stdout"] == "ok"
    mock_run.assert_called_once()
    cmd = mock_run.call_args[0][0]
    assert "music" in cmd
    assert "--plan" in cmd
