"""Tests for ai_influencer_studio.beat_assembly."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from ai_influencer_studio.beat_assembly import (
    assemble,
    beat_times,
    build_ffmpeg_command,
    scene_cut_points,
    snap_cut_times,
    snap_to_beat,
)


def test_beat_times_60bpm() -> None:
    assert beat_times(60.0, 3.5) == [0.0, 1.0, 2.0, 3.0]


def test_beat_times_120bpm() -> None:
    assert beat_times(120.0, 1.0) == [0.0, 0.5]


def test_beat_times_invalid_inputs() -> None:
    assert beat_times(0, 10) == []
    assert beat_times(120, 0) == []


def test_snap_to_beat() -> None:
    beats = [0.0, 1.0, 2.0]
    assert snap_to_beat(0.2, beats) == 0.0
    assert snap_to_beat(0.6, beats) == 1.0
    assert snap_to_beat(5.0, beats) == 2.0  # clamps to the last beat
    assert snap_to_beat(0.5, []) == 0.5  # no grid -> unchanged


def test_snap_cut_times() -> None:
    assert snap_cut_times([0.4, 1.6, 3.2], 60.0, 10.0) == [0.0, 2.0, 3.0]


def test_scene_cut_points_from_plan() -> None:
    song = {
        "duration": 160.0,
        "bpm": 60.0,
        "scenes": [{"end_time": 20.0}, {"end_time": 40.0}, {"end_time": 160.0}],
    }
    assert scene_cut_points(song) == [20.0, 40.0]
    assert scene_cut_points(song, beat_snap=False) == [20.0, 40.0]

    # Non-grid boundaries snap to the nearest beat of a 70 BPM grid.
    off_grid = dict(song, bpm=70.0)
    snapped = scene_cut_points(off_grid)
    assert snapped[0] != 20.0
    assert 19.0 <= snapped[0] <= 21.0


def test_build_ffmpeg_command_trims_and_concats(tmp_path: Path) -> None:
    clip_a = tmp_path / "a.mp4"
    clip_a.write_bytes(b"video")
    clip_b = tmp_path / "b.mp4"
    clip_b.write_bytes(b"video")
    audio = tmp_path / "song.mp3"
    audio.write_bytes(b"audio")

    song = {
        "audio_path": str(audio),
        "duration": 12.0,
        "bpm": 60.0,
        "scenes": [
            {"suggested_clip": str(clip_a), "end_time": 6.0},
            {"suggested_clip": str(clip_b), "end_time": 12.0},
        ],
    }
    spec = build_ffmpeg_command(song, out_path=tmp_path / "out.mp4")

    assert spec["scene_clips"] == [str(clip_a), str(clip_b)]
    assert spec["cuts"] == [6.0]
    assert spec["segments"] == [[0.0, 6.0], [6.0, 12.0]]
    assert spec["audio"] == str(audio)

    command = spec["command"]
    assert "-filter_complex" in command
    filter_complex = command[command.index("-filter_complex") + 1]
    assert "[0:v]trim=start=0:end=6.000" in filter_complex
    assert "[1:v]trim=start=0:end=6.000" in filter_complex
    assert "scale=1280:720:force_original_aspect_ratio=decrease" in filter_complex
    assert "pad=1280:720:(ow-iw)/2:(oh-ih)/2" in filter_complex
    assert "concat=n=2:v=1:a=0[outv]" in filter_complex
    assert "-map" in command
    assert command[-1] == str(tmp_path / "out.mp4")


def test_build_ffmpeg_command_uses_custom_canvas(tmp_path: Path) -> None:
    clip_a = tmp_path / "a.mp4"
    clip_a.write_bytes(b"video")
    song = {
        "duration": 6.0,
        "bpm": 60.0,
        "scenes": [{"suggested_clip": str(clip_a), "end_time": 6.0}],
    }
    spec = build_ffmpeg_command(
        song, out_path=tmp_path / "out.mp4", target_resolution=(1080, 1080)
    )
    filter_complex = spec["command"][spec["command"].index("-filter_complex") + 1]
    assert "scale=1080:1080:force_original_aspect_ratio=decrease" in filter_complex
    assert "pad=1080:1080:(ow-iw)/2:(oh-ih)/2" in filter_complex


def test_build_ffmpeg_command_missing_clip_raises(tmp_path: Path) -> None:
    song = {
        "duration": 10.0,
        "scenes": [
            {"suggested_clip": str(tmp_path / "ghost.mp4"), "end_time": 5.0},
            {"suggested_clip": str(tmp_path / "ghost2.mp4"), "end_time": 10.0},
        ],
    }
    with pytest.raises(FileNotFoundError, match="Missing scene clips"):
        build_ffmpeg_command(song, out_path=tmp_path / "out.mp4")


def test_scene_without_suggested_clip_raises() -> None:
    song = {"duration": 10.0, "scenes": [{"end_time": 10.0}]}
    with pytest.raises(ValueError, match="suggested_clip"):
        build_ffmpeg_command(song, out_path="out.mp4")


def test_assemble_missing_ffmpeg_raises(tmp_path: Path) -> None:
    clip_a = tmp_path / "a.mp4"
    clip_a.write_bytes(b"video")
    clip_b = tmp_path / "b.mp4"
    clip_b.write_bytes(b"video")
    song = {
        "duration": 12.0,
        "bpm": 60.0,
        "scenes": [
            {"suggested_clip": str(clip_a), "end_time": 6.0},
            {"suggested_clip": str(clip_b), "end_time": 12.0},
        ],
    }
    with patch("ai_influencer_studio.beat_assembly.find_ffmpeg", side_effect=RuntimeError("ffmpeg not found")):
        with pytest.raises(RuntimeError, match="ffmpeg not found"):
            assemble(song, out_path=tmp_path / "out.mp4")


def test_assemble_runs_ffmpeg(tmp_path: Path) -> None:
    clip_a = tmp_path / "a.mp4"
    clip_a.write_bytes(b"video")
    clip_b = tmp_path / "b.mp4"
    clip_b.write_bytes(b"video")
    song = {
        "duration": 12.0,
        "bpm": 60.0,
        "scenes": [
            {"suggested_clip": str(clip_a), "end_time": 6.0},
            {"suggested_clip": str(clip_b), "end_time": 12.0},
        ],
    }
    with patch("ai_influencer_studio.beat_assembly.find_ffmpeg", return_value="ffmpeg"), patch(
        "ai_influencer_studio.beat_assembly.subprocess.run"
    ) as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        result = assemble(song, out_path=tmp_path / "out.mp4")

    assert result["returncode"] == 0
    assert result["output"] == str(tmp_path / "out.mp4")
    command = mock_run.call_args.args[0]
    assert command[0] == "ffmpeg"
    assert "-filter_complex" in command


def test_cli_music_video_assemble(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    from ai_influencer_studio.cli import main

    plan_path = tmp_path / "plan.json"
    plan_path.write_text(
        json.dumps(
            {
                "songs": [
                    {
                        "song_name": "T",
                        "audio_path": "/tmp/t.mp3",
                        "duration": 12.0,
                        "bpm": 60.0,
                        "scenes": [
                            {"suggested_clip": str(tmp_path / "a.mp4"), "end_time": 6.0},
                            {"suggested_clip": str(tmp_path / "b.mp4"), "end_time": 12.0},
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    with patch("ai_influencer_studio.cli.StudioConfig"), patch(
        "ai_influencer_studio.beat_assembly.assemble"
    ) as mock_assemble:
        mock_assemble.return_value = {
            "scene_clips": [],
            "cuts": [6.0],
            "segments": [],
            "duration": 12.0,
            "audio": None,
            "returncode": 0,
            "output": str(tmp_path / "out.mp4"),
        }
        main(["music-video", "assemble", "--plan", str(plan_path), "--song-index", "0", "--output", str(tmp_path / "out.mp4")])
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert output["cuts"] == [6.0]


def test_cli_music_video_assemble_missing_plan(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    from ai_influencer_studio.cli import main

    result = main(["music-video", "assemble", "--plan", str(tmp_path / "nope.json"), "--song-index", "0", "--output", str(tmp_path / "o.mp4")])
    assert result == 1
    assert "Plan file not found" in capsys.readouterr().err
