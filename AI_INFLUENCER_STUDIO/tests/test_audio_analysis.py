"""Tests for ai_influencer_studio.audio_analysis."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ai_influencer_studio.audio_analysis import analyze_audio


def test_analyze_audio_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        analyze_audio("/nonexistent/path/song.mp3")


def test_analyze_audio_uses_librosa(tmp_path: Path) -> None:
    audio_path = tmp_path / "song.mp3"
    audio_path.write_text("fake audio")

    mock_librosa = MagicMock()
    mock_librosa.load.return_value = ([0.0] * 1000, 22050)
    mock_librosa.get_duration.return_value = 210.5
    mock_librosa.beat.beat_track.return_value = (128.0, None)

    with patch("ai_influencer_studio.audio_analysis.librosa", mock_librosa):
        result = analyze_audio(str(audio_path))

    assert result["duration"] == 210.5
    assert result["bpm"] == 128.0
    assert result["source"] == "librosa"


def test_analyze_audio_falls_back_to_mutagen(tmp_path: Path) -> None:
    audio_path = tmp_path / "song.mp3"
    audio_path.write_text("fake audio")

    mock_info = MagicMock()
    mock_info.length = 180.0
    mock_audio = MagicMock()
    mock_audio.info = mock_info
    mock_mutagen = MagicMock()
    mock_mutagen.return_value = mock_audio

    with patch("ai_influencer_studio.audio_analysis.librosa", None), patch(
        "ai_influencer_studio.audio_analysis.MutagenFile", mock_mutagen
    ):
        result = analyze_audio(str(audio_path))

    assert result["duration"] == 180.0
    assert result["bpm"] == 120.0
    assert "mutagen" in result["source"]
