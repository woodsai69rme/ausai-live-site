"""Tests for ai_influencer_studio.youtube_publish."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ai_influencer_studio.youtube_publish import (
    YouTubePublisher,
    build_metadata,
    save_publish_record,
)


def test_build_metadata_from_song_plan() -> None:
    song = {
        "song_name": "Midnight Drive",
        "audio_path": "/tmp/midnight.mp3",
        "genre": "synthwave",
        "mood": "night",
        "bpm": 128.0,
        "duration": 210.0,
    }
    meta = build_metadata(song)
    assert meta["title"] == "Midnight Drive | synthwave"
    assert "Genre: synthwave" in meta["description"]
    assert "Mood: night" in meta["description"]
    assert "BPM: 128.0" in meta["description"]
    assert "3:30" in meta["description"]  # 210 seconds
    assert "synthwave" in meta["tags"]
    assert "128bpm" in meta["tags"]
    assert len(meta["tags"]) <= 10


def test_build_metadata_empty_song_defaults() -> None:
    meta = build_metadata({"audio_path": "/tmp/song.mp3"})
    assert meta["title"] == "song"
    assert meta["genre"] == ""
    assert meta["mood"] == ""
    assert meta["tags"]


def test_publish_song_uploads_thumbnail_and_playlists(tmp_path: Path) -> None:
    with patch("ai_influencer_studio.youtube_publish.youtube_build") as mock_build, patch(
        "ai_influencer_studio.youtube_publish.YouTubeCredentials"
    ) as mock_creds, patch("ai_influencer_studio.youtube_publish.MediaFileUpload"):
        mock_creds.from_authorized_user_file.return_value = MagicMock(valid=True)
        (tmp_path / "token.json").write_text("{}", encoding="utf-8")

        service = MagicMock()
        request = MagicMock()
        request.next_chunk.side_effect = [(None, {"id": "vid-1"})]
        service.videos().insert.return_value = request
        mock_build.return_value = service

        video = tmp_path / "video.mp4"
        video.write_bytes(b"video")
        thumb = tmp_path / "thumb.jpg"
        thumb.write_bytes(b"jpg")

        publisher = YouTubePublisher(
            token_path=tmp_path / "token.json",
            client_secrets_path=tmp_path / "secrets.json",
        )
        song = {"song_name": "Track", "audio_path": str(video), "genre": "pop", "bpm": 120.0, "duration": 60.0}
        result = publisher.publish_song(song, video, thumbnail_path=thumb, playlist_ids=["PL1"], create_playlist_title="My Videos")

        assert result["video_id"] == "vid-1"
        assert result["url"] == "https://youtu.be/vid-1"
        assert result["thumbnail_uploaded"] is True
        assert "PL1" in result["playlists"]
        assert result["metadata"]["title"] == "Track | pop"
        service.playlists().insert.assert_called_once()  # playlist creation


def test_upload_missing_video_raises(tmp_path: Path) -> None:
    publisher = YouTubePublisher(token_path=tmp_path / "t.json", client_secrets_path=tmp_path / "s.json")
    with pytest.raises(FileNotFoundError, match="Video file not found"):
        publisher.upload(tmp_path / "nope.mp4", title="X")


def test_missing_client_secrets_raises_clear_error(tmp_path: Path) -> None:
    publisher = YouTubePublisher(
        token_path=tmp_path / "missing_token.json",
        client_secrets_path=tmp_path / "missing_secrets.json",
    )
    with pytest.raises(RuntimeError, match="client secrets not found"):
        publisher._credentials()


def test_channel_info_parses_stats(tmp_path: Path) -> None:
    with patch("ai_influencer_studio.youtube_publish.youtube_build") as mock_build, patch(
        "ai_influencer_studio.youtube_publish.YouTubeCredentials"
    ) as mock_creds:
        mock_creds.from_authorized_user_file.return_value = MagicMock(valid=True)
        (tmp_path / "token.json").write_text("{}", encoding="utf-8")

        service = MagicMock()
        service.channels().list.return_value.execute.return_value = {
            "items": [
                {
                    "id": "CH1",
                    "snippet": {"title": "My Channel"},
                    "statistics": {"subscriberCount": "5", "viewCount": "10", "videoCount": "3"},
                }
            ]
        }
        mock_build.return_value = service

        publisher = YouTubePublisher(token_path=tmp_path / "token.json", client_secrets_path=tmp_path / "secrets.json")
        info = publisher.channel_info()
        assert info["id"] == "CH1"
        assert info["title"] == "My Channel"
        assert info["subscribers"] == "5"
        assert info["videos"] == "3"


def test_thumbnail_and_playlist_errors_do_not_raise(tmp_path: Path) -> None:
    with patch("ai_influencer_studio.youtube_publish.youtube_build") as mock_build, patch(
        "ai_influencer_studio.youtube_publish.YouTubeCredentials"
    ) as mock_creds:
        mock_creds.from_authorized_user_file.return_value = MagicMock(valid=True)
        (tmp_path / "token.json").write_text("{}", encoding="utf-8")

        service = MagicMock()
        request = MagicMock()
        request.next_chunk.side_effect = [(None, {"id": "vid-2"})]
        service.videos().insert.return_value = request
        # thumbnails + playlistItems raise API errors -> swallowed into flags
        thumb_mock = MagicMock()
        thumb_mock.set.side_effect = RuntimeError("403")
        service.thumbnails.return_value = thumb_mock
        playlist_mock = MagicMock()
        playlist_mock.insert.side_effect = RuntimeError("quota")
        service.playlistItems.return_value = playlist_mock
        mock_build.return_value = service

        video = tmp_path / "video.mp4"
        video.write_bytes(b"video")
        publisher = YouTubePublisher(token_path=tmp_path / "token.json", client_secrets_path=tmp_path / "secrets.json")
        result = publisher.upload(
            video,
            title="T",
            thumbnail_path=video,  # exists -> attempted
            playlist_ids=["PL1"],
        )
        assert result["video_id"] == "vid-2"
        assert result["thumbnail_uploaded"] is False
        assert result["playlists"] == []


def test_save_publish_record_appends(tmp_path: Path) -> None:
    path = tmp_path / "log.jsonl"
    save_publish_record({"video_id": "a"}, path)
    save_publish_record({"video_id": "b"}, path)
    lines = [line for line in path.read_text(encoding="utf-8").strip().splitlines() if line]
    assert len(lines) == 2
    assert json.loads(lines[0])["video_id"] == "a"


def test_cli_youtube_metadata(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    from ai_influencer_studio.cli import main

    plan_path = tmp_path / "plan.json"
    plan_path.write_text(
        json.dumps({"songs": [{"song_name": "Track", "audio_path": "/tmp/t.mp3", "genre": "pop", "mood": "bright"}]}),
        encoding="utf-8",
    )
    with patch("ai_influencer_studio.cli.StudioConfig"):
        main(["youtube", "metadata", "--plan", str(plan_path), "--song-index", "0"])
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert output["title"] == "Track | pop"
    assert "bright" in output["description"]


def test_cli_youtube_upload(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    from ai_influencer_studio.cli import main

    plan_path = tmp_path / "plan.json"
    plan_path.write_text(
        json.dumps({"songs": [{"song_name": "Track", "audio_path": str(tmp_path / "t.mp3"), "genre": "pop"}]}),
        encoding="utf-8",
    )
    video = tmp_path / "video.mp4"
    video.write_bytes(b"video")

    with patch("ai_influencer_studio.cli.StudioConfig") as mock_config, patch(
        "ai_influencer_studio.youtube_publish.YouTubePublisher"
    ) as mock_pub_cls:
        mock_config.from_file.return_value.data_dir = tmp_path
        mock_config.from_file.return_value.youtube_token_path = tmp_path / "token.json"
        mock_config.from_file.return_value.youtube_client_secrets_path = tmp_path / "secrets.json"
        mock_config.from_file.return_value.youtube_default_privacy = "private"
        mock_config.from_file.return_value.youtube_category_id = "10"
        mock_config.from_file.return_value.youtube_playlist_title = ""
        mock_pub = MagicMock()
        mock_pub.publish_song.return_value = {"video_id": "v1", "url": "https://youtu.be/v1", "playlists": [], "metadata": {}}
        mock_pub_cls.return_value = mock_pub

        main(["youtube", "upload", "--plan", str(plan_path), "--video", str(video)])
        mock_pub.publish_song.assert_called_once()
        assert mock_pub.publish_song.call_args.kwargs["privacy"] == "private"
    captured = capsys.readouterr()
    assert "https://youtu.be/v1" in captured.out
    assert "youtube_publish.jsonl" in captured.out


def test_cli_youtube_missing_plan(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    from ai_influencer_studio.cli import main

    result = main(["youtube", "metadata", "--plan", str(tmp_path / "nope.json"), "--song-index", "0"])
    assert result == 1
    assert "Plan file not found" in capsys.readouterr().err
