"""Tests for the FastAPI web dashboard."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from ai_influencer_studio.config import StudioConfig
from ai_influencer_studio.web.app import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@patch("ai_influencer_studio.web.app.AutomationAdapter")
def test_dashboard_renders(mock_adapter_cls: MagicMock, client: TestClient) -> None:
    mock_adapter = MagicMock()
    mock_adapter.list_scheduled_posts.return_value = []
    mock_adapter_cls.return_value = mock_adapter

    response = client.get("/")
    assert response.status_code == 200
    assert "AI Influencer Studio" in response.text


@patch("ai_influencer_studio.web.app.AutomationAdapter")
def test_factory_page_renders(mock_adapter_cls: MagicMock, client: TestClient) -> None:
    response = client.get("/factory")
    assert response.status_code == 200
    assert "Content Factory" in response.text


@patch("ai_influencer_studio.web.app.ContentAdapter")
def test_factory_generate_post(mock_adapter_cls: MagicMock, client: TestClient) -> None:
    mock_adapter = MagicMock()
    mock_adapter.generate_post.return_value = {"topic": "AI", "content": "Hello"}
    mock_adapter_cls.return_value = mock_adapter

    response = client.post("/factory/generate", data={
        "content_type": "post",
        "topic": "AI automation",
        "platform": "twitter",
    })
    assert response.status_code == 200
    assert response.json()["type"] == "post"


@patch("ai_influencer_studio.web.app.AutomationAdapter")
def test_calendar_schedule(mock_adapter_cls: MagicMock, client: TestClient) -> None:
    mock_adapter = MagicMock()
    mock_adapter.schedule_post.return_value = 1
    mock_adapter_cls.return_value = mock_adapter

    response = client.post("/calendar/schedule", data={
        "platform": "twitter",
        "content": "Hello world",
        "scheduled_at": "2026-07-17T12:00",
        "hashtags": "ai, test",
    })
    assert response.status_code == 200
    assert response.json()["id"] == 1


@patch("ai_influencer_studio.web.app.AutomationAdapter")
def test_publish_now(mock_adapter_cls: MagicMock, client: TestClient) -> None:
    mock_adapter = MagicMock()
    mock_adapter.post_via_api.return_value = {"success": True}
    mock_adapter_cls.return_value = mock_adapter

    response = client.post("/publish/now", data={
        "platform": "twitter",
        "content": "Hello world",
    })
    assert response.status_code == 200
    assert response.json()["success"] is True


@patch("ai_influencer_studio.web.app.AutomationAdapter")
def test_auth_required_when_api_key_configured(mock_adapter_cls: MagicMock, client: TestClient) -> None:
    mock_adapter = MagicMock()
    mock_adapter.list_scheduled_posts.return_value = []
    mock_adapter_cls.return_value = mock_adapter

    # Clear the cached API key before and after the test so other tests are not affected.
    from ai_influencer_studio.web.auth import _get_configured_key

    _get_configured_key.cache_clear()  # type: ignore[attr-defined]
    try:
        with patch.dict(os.environ, {"AISTUDIO_API_KEY": "secret-key"}, clear=False):
            # Request without the header should be rejected.
            response = client.get("/")
            assert response.status_code == 403

            # Request with the correct header should proceed.
            response = client.get("/", headers={"X-API-Key": "secret-key"})
            assert response.status_code == 200
    finally:
        _get_configured_key.cache_clear()  # type: ignore[attr-defined]


@patch("ai_influencer_studio.web.app.MusicVideoResearchEngine")
def test_music_video_lab_research(mock_engine_cls: MagicMock, client: TestClient) -> None:
    mock_engine = MagicMock()
    mock_engine.research_generators.return_value = [{"id": "wan21", "name": "Wan 2.1"}]
    mock_engine.fetch_youtube_trends.return_value = [{"video_id": "abc123", "title": "Trend"}]
    mock_engine_cls.return_value = mock_engine

    response = client.post("/api/music-video/research", data={"vram": "16", "max_results": "5"})
    assert response.status_code == 200
    data = response.json()
    assert data["generators"][0]["id"] == "wan21"
    assert data["trends"][0]["video_id"] == "abc123"


@patch("ai_influencer_studio.web.app.MusicVideoResearchEngine")
def test_music_video_lab_plan(mock_engine_cls: MagicMock, client: TestClient) -> None:
    mock_engine = MagicMock()
    mock_engine.save_master_plan_with_name.return_value = Path("/tmp/Song_A_music_video_plan.json")
    mock_engine.create_master_plan.return_value = {"songs": []}
    mock_engine_cls.return_value = mock_engine

    response = client.post("/api/music-video/plan", data={
        "song_name": "Song A",
        "audio_path": "/tmp/a.mp3",
        "genre": "pop",
        "mood": "upbeat",
        "duration": "120",
        "character_ref": "/tmp/hero.png",
        "generation_mode": "clip_only",
    })
    assert response.status_code == 200
    mock_engine.create_song_plan.assert_called_once_with(
        song_name="Song A",
        audio_path="/tmp/a.mp3",
        genre="pop",
        mood="upbeat",
        duration=120.0,
        character_ref="/tmp/hero.png",
        generation_mode="clip_only",
    )
    mock_engine.save_master_plan_with_name.assert_called_once_with("Song A")


@patch("ai_influencer_studio.web.app.VideoAdapter")
@patch("ai_influencer_studio.web.app._config")
def test_music_video_lab_execute(mock_config: MagicMock, mock_adapter_cls: MagicMock, client: TestClient, tmp_path: Path) -> None:
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps({"songs": [{"audio_path": str(tmp_path / "a.mp3")}]}), encoding="utf-8")
    (tmp_path / "a.mp3").write_text("audio")

    mock_config.return_value = StudioConfig(data_dir=tmp_path, media_dir=tmp_path / "media")

    mock_adapter = MagicMock()
    mock_adapter.execute_music_video_plan.return_value = {"returncode": 0}
    mock_adapter_cls.return_value = mock_adapter

    response = client.post("/api/music-video/execute", data={
        "plan": "plan.json",
        "song_index": "0",
    })
    assert response.status_code == 200
    mock_adapter.execute_music_video_plan.assert_called_once()
    assert mock_adapter.execute_music_video_plan.call_args[0][0]["audio_path"] == str(tmp_path / "a.mp3")


@patch("ai_influencer_studio.web.app.VideoAdapter")
@patch("ai_influencer_studio.web.app._config")
def test_music_video_lab_execute_full_path(mock_config: MagicMock, mock_adapter_cls: MagicMock, client: TestClient, tmp_path: Path) -> None:
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps({"songs": [{"audio_path": str(tmp_path / "a.mp3")}]}), encoding="utf-8")
    (tmp_path / "a.mp3").write_text("audio")

    mock_config.return_value = StudioConfig(data_dir=tmp_path / "other", media_dir=tmp_path / "media")

    mock_adapter = MagicMock()
    mock_adapter.execute_music_video_plan.return_value = {"returncode": 0}
    mock_adapter_cls.return_value = mock_adapter

    response = client.post("/api/music-video/execute", data={
        "plan": str(plan_path),
        "song_index": "0",
    })
    assert response.status_code == 200
    mock_adapter.execute_music_video_plan.assert_called_once()
    assert mock_adapter.execute_music_video_plan.call_args[0][0]["audio_path"] == str(tmp_path / "a.mp3")


@patch("ai_influencer_studio.web.app._config")
def test_music_video_lab_execute_not_found(mock_config: MagicMock, client: TestClient, tmp_path: Path) -> None:
    mock_config.return_value = StudioConfig(data_dir=tmp_path, media_dir=tmp_path / "media")

    response = client.post("/api/music-video/execute", data={
        "plan": "missing.json",
        "song_index": "0",
    })
    assert response.status_code == 404
    assert "Plan file not found" in response.json()["error"]


@patch("ai_influencer_studio.web.app._config")
def test_music_video_lab_execute_invalid_plan(mock_config: MagicMock, client: TestClient, tmp_path: Path) -> None:
    invalid_plan = tmp_path / "invalid.json"
    invalid_plan.write_text(json.dumps({"not_songs": []}), encoding="utf-8")
    mock_config.return_value = StudioConfig(data_dir=tmp_path, media_dir=tmp_path / "media")

    response = client.post("/api/music-video/execute", data={
        "plan": "invalid.json",
        "song_index": "0",
    })
    assert response.status_code == 400
    assert "non-empty 'songs' list" in response.json()["error"]


@patch("ai_influencer_studio.web.app._config")
def test_music_video_lab_execute_missing_audio_path(mock_config: MagicMock, client: TestClient, tmp_path: Path) -> None:
    bad_plan = tmp_path / "bad.json"
    bad_plan.write_text(json.dumps({"songs": [{"name": "Song"}]}), encoding="utf-8")
    mock_config.return_value = StudioConfig(data_dir=tmp_path, media_dir=tmp_path / "media")

    response = client.post("/api/music-video/execute", data={
        "plan": "bad.json",
        "song_index": "0",
    })
    assert response.status_code == 400
    assert "non-empty 'audio_path'" in response.json()["error"]


@patch("ai_influencer_studio.web.app._config")
def test_music_video_lab_execute_audio_file_not_found(mock_config: MagicMock, client: TestClient, tmp_path: Path) -> None:
    bad_plan = tmp_path / "bad.json"
    bad_plan.write_text(json.dumps({"songs": [{"audio_path": str(tmp_path / "missing.mp3")}]}), encoding="utf-8")
    mock_config.return_value = StudioConfig(data_dir=tmp_path, media_dir=tmp_path / "media")

    response = client.post("/api/music-video/execute", data={
        "plan": "bad.json",
        "song_index": "0",
    })
    assert response.status_code == 404
    assert "Audio file not found" in response.json()["error"]


def test_music_video_lab_submit_button_starts_disabled(client: TestClient) -> None:
    import re

    response = client.get("/music-video")
    assert response.status_code == 200
    # The submit button inside the execute form should start disabled.
    assert 'id="executeForm"' in response.text
    execute_form_match = re.search(r'<form[^>]*id="executeForm"[\s\S]*?</form>', response.text)
    assert execute_form_match is not None, "executeForm not found in response"
    execute_form = execute_form_match.group(0)
    submit_button_match = re.search(r'<button\b[^>]*type=["\']submit["\'][^>]*>', execute_form)
    assert submit_button_match is not None, "submit button not found in executeForm"
    submit_button = submit_button_match.group(0)
    assert "disabled" in submit_button, "submit button should start disabled"


@patch("ai_influencer_studio.web.app.analyze_audio")
def test_music_video_lab_analyze_audio(mock_analyze: MagicMock, client: TestClient) -> None:
    mock_analyze.return_value = {"duration": 210.5, "bpm": 128.0, "source": "librosa"}

    response = client.post("/api/music-video/analyze-audio", data={"audio_path": "/tmp/song.mp3"})
    assert response.status_code == 200
    data = response.json()
    assert data["duration"] == 210.5
    assert data["bpm"] == 128.0
    mock_analyze.assert_called_once_with("/tmp/song.mp3")


@patch("ai_influencer_studio.web.app._config")
def test_music_video_lab_delete_plan(mock_config: MagicMock, client: TestClient, tmp_path: Path) -> None:
    plan = tmp_path / "old.json"
    plan.write_text(json.dumps({"songs": []}), encoding="utf-8")
    mock_config.return_value = StudioConfig(data_dir=tmp_path, media_dir=tmp_path / "media")

    response = client.delete("/api/music-video/plans/old.json")
    assert response.status_code == 200
    assert response.json()["deleted"] == "old.json"
    assert not plan.exists()


@patch("ai_influencer_studio.web.app._config")
def test_music_video_lab_rename_plan(mock_config: MagicMock, client: TestClient, tmp_path: Path) -> None:
    plan = tmp_path / "old.json"
    plan.write_text(json.dumps({"songs": []}), encoding="utf-8")
    mock_config.return_value = StudioConfig(data_dir=tmp_path, media_dir=tmp_path / "media")

    response = client.post("/api/music-video/plans/old.json/rename", data={"new_name": "new.json"})
    assert response.status_code == 200
    data = response.json()
    assert data["renamed"]["from"] == "old.json"
    assert data["renamed"]["to"] == "new.json"
    assert not plan.exists()
    assert (tmp_path / "new.json").exists()


@patch("ai_influencer_studio.web.app.VideoAdapter")
@patch("ai_influencer_studio.web.app._config")
def test_music_video_lab_execute_websocket(
    mock_config: MagicMock,
    mock_adapter_cls: MagicMock,
    client: TestClient,
    tmp_path: Path,
) -> None:
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps({"songs": [{"audio_path": str(tmp_path / "a.mp3")}]}), encoding="utf-8")
    (tmp_path / "a.mp3").write_text("audio")
    mock_config.return_value = StudioConfig(data_dir=tmp_path, media_dir=tmp_path / "media")

    async def _stream() -> Any:
        yield {"type": "stdout", "line": "transcribing..."}
        yield {"type": "done", "returncode": 0}

    mock_adapter = MagicMock()
    mock_adapter.execute_music_video_plan_streaming.return_value = _stream()
    mock_adapter_cls.return_value = mock_adapter

    with client.websocket_connect("/ws/music-video/execute") as ws:
        ws.send_json({"plan": "plan.json", "song_index": 0})
        messages = []
        while True:
            message = ws.receive_json()
            messages.append(message)
            if message.get("type") == "done":
                break

    assert messages[0] == {"type": "status", "message": "started"}
    assert any(m.get("line") == "transcribing..." for m in messages)
    assert any(m.get("type") == "done" for m in messages)


def test_music_video_lab_execute_websocket_requires_api_key(client: TestClient) -> None:
    from starlette.websockets import WebSocketDisconnect

    from ai_influencer_studio.web.auth import _get_configured_key

    _get_configured_key.cache_clear()  # type: ignore[attr-defined]
    try:
        with patch.dict(os.environ, {"AISTUDIO_API_KEY": "secret-key"}, clear=False):
            with pytest.raises(WebSocketDisconnect):
                with client.websocket_connect("/ws/music-video/execute"):
                    pass
    finally:
        _get_configured_key.cache_clear()  # type: ignore[attr-defined]


@patch("ai_influencer_studio.web.app.AutomationAdapter")
def test_scheduler_push_n8n(mock_adapter_cls: MagicMock, client: TestClient) -> None:
    mock_adapter = MagicMock()
    mock_adapter.push_to_scheduler.return_value = {"status": 200, "body": "ok"}
    mock_adapter_cls.return_value = mock_adapter

    response = client.post("/api/scheduler/n8n/push", json={"video": "path.mp4"})
    assert response.status_code == 200
    assert response.json()["status"] == 200
    mock_adapter.push_to_scheduler.assert_called_once_with("n8n", {"video": "path.mp4"})


@patch("ai_influencer_studio.web.app.AutomationAdapter")
def test_scheduler_push_postiz(mock_adapter_cls: MagicMock, client: TestClient) -> None:
    mock_adapter = MagicMock()
    mock_adapter.push_to_scheduler.return_value = {"status": 201, "body": "created"}
    mock_adapter_cls.return_value = mock_adapter

    response = client.post("/api/scheduler/postiz/push", json={"content": "hello"})
    assert response.status_code == 200
    assert response.json()["status"] == 201
    mock_adapter.push_to_scheduler.assert_called_once_with("postiz", {"content": "hello"})


@patch("ai_influencer_studio.web.app.AutomationAdapter")
def test_scheduler_push_mixpost(mock_adapter_cls: MagicMock, client: TestClient) -> None:
    mock_adapter = MagicMock()
    mock_adapter.push_to_scheduler.return_value = {"status": 201, "body": "created"}
    mock_adapter_cls.return_value = mock_adapter

    response = client.post("/api/scheduler/mixpost/push", json={"content": "hello"})
    assert response.status_code == 200
    assert response.json()["status"] == 201
    mock_adapter.push_to_scheduler.assert_called_once_with("mixpost", {"content": "hello"})


@patch("ai_influencer_studio.web.app.AutomationAdapter")
def test_scheduler_push_invalid_scheduler(mock_adapter_cls: MagicMock, client: TestClient) -> None:
    mock_adapter = MagicMock()
    mock_adapter.push_to_scheduler.side_effect = ValueError("Unsupported scheduler: unknown")
    mock_adapter_cls.return_value = mock_adapter

    response = client.post("/api/scheduler/unknown/push", json={})
    assert response.status_code == 400
    assert "Unsupported scheduler" in response.json()["error"]


@patch("ai_influencer_studio.web.app.VideoRepurposer")
@patch("ai_influencer_studio.web.app._config")
def test_video_repurpose(mock_config: MagicMock, mock_repurposer_cls: MagicMock, client: TestClient, tmp_path: Path) -> None:
    mock_config.return_value = StudioConfig(data_dir=tmp_path, media_dir=tmp_path / "media")
    mock_repurposer = MagicMock()
    mock_repurposer.create_vertical_cut.return_value = {
        "input": "/tmp/video.mp4",
        "output": str(tmp_path / "media" / "repurposed" / "video_tiktok.mp4"),
        "platform": "tiktok",
    }
    mock_repurposer_cls.return_value = mock_repurposer

    response = client.post("/api/video/repurpose", data={
        "input_path": "/tmp/video.mp4",
        "platform": "tiktok",
        "caption": "Hello",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "tiktok"
    mock_repurposer.create_vertical_cut.assert_called_once()


@patch("ai_influencer_studio.web.app.VideoRepurposer")
@patch("ai_influencer_studio.web.app._config")
def test_video_repurpose_multi(mock_config: MagicMock, mock_repurposer_cls: MagicMock, client: TestClient, tmp_path: Path) -> None:
    mock_config.return_value = StudioConfig(data_dir=tmp_path, media_dir=tmp_path / "media")
    mock_repurposer = MagicMock()
    mock_repurposer.create_multi_clips.return_value = [
        {"platform": "tiktok", "output": "clip1.mp4"},
        {"platform": "instagram", "output": "clip2.mp4"},
    ]
    mock_repurposer_cls.return_value = mock_repurposer

    response = client.post("/api/video/repurpose/multi", data={
        "input_path": "/tmp/video.mp4",
        "platforms": "tiktok,instagram",
        "clip_duration": "15",
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data["clips"]) == 2
    mock_repurposer.create_multi_clips.assert_called_once()


@patch("ai_influencer_studio.web.app._config")
def test_gdrive_dashboard_page_renders(mock_config: MagicMock, client: TestClient, tmp_path: Path) -> None:
    mock_config.return_value = StudioConfig(data_dir=tmp_path, media_dir=tmp_path / "media")

    response = client.get("/gdrive")
    assert response.status_code == 200
    assert "Google Drive Upload" in response.text
    assert "api/gdrive/status" in response.text


@patch("ai_influencer_studio.web.app._config")
def test_gdrive_status_reports_counts(mock_config: MagicMock, client: TestClient, tmp_path: Path) -> None:
    from ai_influencer_studio.gdrive_uploader import GDriveUploader

    state_path = tmp_path / "state.json"
    uploader = GDriveUploader(state_path)
    uploader.state.pending = [
        {"path": "/a.png", "md5": "x", "size": 1_000_000, "kind": "image", "is_screenshot": False}
    ]
    uploader.state.done = [
        {"path": "/b.mp4", "md5": "y", "size": 2_000_000, "kind": "video", "uploaded_at": "now"}
    ]
    uploader.state.save(state_path)

    mock_config.return_value = StudioConfig(
        data_dir=tmp_path,
        media_dir=tmp_path / "media",
        gdrive_state_path=state_path,
        gdrive_folder_url="https://example.com/folder",
    )
    response = client.get("/api/gdrive/status")
    assert response.status_code == 200
    data = response.json()
    assert data["pending"] == 1
    assert data["done"] == 1
    assert data["folder_url"] == "https://example.com/folder"
    assert data["running"] is False


@patch("ai_influencer_studio.web.app._config")
def test_gdrive_collect_scans_sources(mock_config: MagicMock, client: TestClient, tmp_path: Path) -> None:
    state_path = tmp_path / "state.json"
    (tmp_path / "media").mkdir(exist_ok=True)
    source = tmp_path / "src"
    source.mkdir()
    (source / "hero.png").write_bytes(b"a" * 300_000)
    mock_config.return_value = StudioConfig(
        data_dir=tmp_path,
        media_dir=tmp_path / "media",
        gdrive_state_path=state_path,
    )

    response = client.post("/api/gdrive/collect", data={"sources": str(source)})
    assert response.status_code == 200
    data = response.json()
    assert data["pending"] == 1
    assert data["done"] == 0


@patch("ai_influencer_studio.web.app._config")
def test_gdrive_collect_requires_sources(mock_config: MagicMock, client: TestClient, tmp_path: Path) -> None:
    mock_config.return_value = StudioConfig(data_dir=tmp_path, media_dir=tmp_path / "media", gdrive_state_path=tmp_path / "s.json")
    response = client.post("/api/gdrive/collect", data={"sources": " , , "})
    assert response.status_code == 400
    assert "No source directories" in response.json()["error"]


def test_youtube_dashboard_page_renders(client: TestClient) -> None:
    response = client.get("/youtube")
    assert response.status_code == 200
    assert "api/youtube/status" in response.text


def test_youtube_metadata_endpoint(client: TestClient, tmp_path: Path) -> None:
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(
        json.dumps({"songs": [{"song_name": "Track", "audio_path": str(tmp_path / "t.mp3"), "genre": "pop", "bpm": 120.0, "duration": 60.0}]}),
        encoding="utf-8",
    )
    response = client.post("/api/youtube/metadata", data={"plan": str(plan_path), "song_index": "0"})
    assert response.status_code == 200
    assert response.json()["title"] == "Track | pop"


def test_youtube_metadata_missing_plan(client: TestClient, tmp_path: Path) -> None:
    response = client.post("/api/youtube/metadata", data={"plan": str(tmp_path / "nope.json"), "song_index": "0"})
    assert response.status_code == 400


@patch("ai_influencer_studio.web.app._config")
def test_youtube_metadata_invalid_song_index(mock_config: MagicMock, client: TestClient, tmp_path: Path) -> None:
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps({"songs": [{"song_name": "Track"}]}), encoding="utf-8")
    response = client.post("/api/youtube/metadata", data={"plan": str(plan_path), "song_index": "3"})
    assert response.status_code == 400


@patch("ai_influencer_studio.youtube_publish.YouTubePublisher")
@patch("ai_influencer_studio.web.app._config")
def test_youtube_upload_start_runs_in_background(
    mock_config: MagicMock, mock_pub_cls: MagicMock, client: TestClient, tmp_path: Path
) -> None:
    import time

    from ai_influencer_studio.web import app as web_app

    plan_path = tmp_path / "plan.json"
    plan_path.write_text(
        json.dumps({"songs": [{"song_name": "Track", "audio_path": str(tmp_path / "t.mp3"), "genre": "pop"}]}),
        encoding="utf-8",
    )
    video = tmp_path / "video.mp4"
    video.write_bytes(b"video")
    mock_config.return_value = StudioConfig(
        data_dir=tmp_path,
        media_dir=tmp_path / "media",
        youtube_token_path=tmp_path / "token.json",
        youtube_client_secrets_path=tmp_path / "secrets.json",
        youtube_default_privacy="private",
        youtube_category_id="10",
        youtube_playlist_title="",
    )
    mock_pub = MagicMock()
    mock_pub.publish_song.return_value = {
        "video_id": "v1",
        "url": "https://youtu.be/v1",
        "playlists": [],
        "thumbnail_uploaded": False,
        "metadata": {},
    }
    mock_pub_cls.return_value = mock_pub
    web_app._YOUTUBE_RUN.update(thread=None, running=False, started_at=None, last_error=None, result=None)

    response = client.post("/api/youtube/upload/start", data={"plan": str(plan_path), "song_index": "0", "video": str(video)})
    assert response.status_code == 202
    assert response.json()["started"] is True

    deadline = time.time() + 5
    while web_app._YOUTUBE_RUN["running"] and time.time() < deadline:
        time.sleep(0.05)
    assert web_app._YOUTUBE_RUN["result"]["video_id"] == "v1"
    mock_pub.publish_song.assert_called_once()

    # The append-only publish record is written next to the data dir.
    assert (tmp_path / "youtube_publish.jsonl").exists()


@patch("ai_influencer_studio.web.app._config")
def test_youtube_upload_start_missing_video(mock_config: MagicMock, client: TestClient, tmp_path: Path) -> None:
    from ai_influencer_studio.web import app as web_app

    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps({"songs": [{"song_name": "Track", "audio_path": str(tmp_path / "t.mp3")}]}), encoding="utf-8")
    mock_config.return_value = StudioConfig(data_dir=tmp_path, media_dir=tmp_path / "media")
    web_app._YOUTUBE_RUN.update(thread=None, running=False, started_at=None, last_error=None, result=None)

    response = client.post("/api/youtube/upload/start", data={"plan": str(plan_path), "song_index": "0"})
    assert response.status_code == 400
    assert "Video file not found" in response.json()["error"]


@patch("ai_influencer_studio.web.app._config")
def test_youtube_status_reports_result(mock_config: MagicMock, client: TestClient) -> None:
    from ai_influencer_studio.web import app as web_app

    web_app._YOUTUBE_RUN.update(
        thread=None, running=False, started_at=None, last_error=None, result={"video_id": "v1", "url": "https://youtu.be/v1"}
    )
    response = client.get("/api/youtube/status")
    assert response.status_code == 200
    assert response.json()["result"]["video_id"] == "v1"
    assert response.json()["running"] is False


def test_pipeline_dashboard_page_renders(client: TestClient) -> None:
    response = client.get("/pipeline")
    assert response.status_code == 200
    assert "api/pipeline/status" in response.text


@patch("ai_influencer_studio.web.app._gdrive_uploader")
@patch("ai_influencer_studio.web.app._config")
def test_pipeline_status_aggregates_plans_drive_and_publish(
    mock_config: MagicMock, mock_uploader_factory: MagicMock, client: TestClient, tmp_path: Path
) -> None:
    from ai_influencer_studio.web import app as web_app

    plan_path = tmp_path / "master_music_video_plan.json"
    plan_path.write_text(
        json.dumps({"created": "now", "continuity_warnings": ["warn"], "songs": [{"song_name": "A"}, {"song_name": "B"}]}),
        encoding="utf-8",
    )
    log_path = tmp_path / "youtube_publish.jsonl"
    log_path.write_text(
        json.dumps({"title": "Track", "video_id": "v1", "url": "https://youtu.be/v1", "uploaded_at": "t", "metadata": {}}) + "\n",
        encoding="utf-8",
    )
    mock_config.return_value = StudioConfig(
        data_dir=tmp_path,
        media_dir=tmp_path / "media",
        gdrive_state_path=tmp_path / "g.json",
        gdrive_folder_url="https://example.com/folder",
    )
    uploader = MagicMock()
    uploader.status.return_value = {"pending": 3, "done": 1, "folder_url": "https://example.com/folder"}
    mock_uploader_factory.return_value = uploader
    web_app._GDRIVE_RUN.update(thread=None, stop_event=None, running=False, started_at=None, last_error=None, progress=None)
    web_app._YOUTUBE_RUN.update(thread=None, running=False, started_at=None, last_error=None, result=None)

    response = client.get("/api/pipeline/status")
    assert response.status_code == 200
    data = response.json()
    assert len(data["plans"]) == 1
    assert data["plans"][0]["songs"] == 2
    assert data["plans"][0]["continuity_warnings"] == ["warn"]
    assert data["gdrive"]["pending"] == 3
    assert data["gdrive"]["done"] == 1
    assert data["youtube"]["records"][0]["video_id"] == "v1"
    assert data["youtube"]["running"] is False


@patch("ai_influencer_studio.web.app._gdrive_uploader")
@patch("ai_influencer_studio.web.app._config")
def test_pipeline_status_handles_missing_plan_and_log(
    mock_config: MagicMock, mock_uploader_factory: MagicMock, client: TestClient, tmp_path: Path
) -> None:
    mock_config.return_value = StudioConfig(
        data_dir=tmp_path,
        media_dir=tmp_path / "media",
        gdrive_state_path=tmp_path / "g.json",
    )
    uploader = MagicMock()
    uploader.status.return_value = {"pending": 0, "done": 0}
    mock_uploader_factory.return_value = uploader
    response = client.get("/api/pipeline/status")
    assert response.status_code == 200
    data = response.json()
    assert data["plans"] == []
    assert data["youtube"]["records"] == []


@patch("ai_influencer_studio.web.app._gdrive_uploader")
@patch("ai_influencer_studio.web.app._config")
def test_gdrive_upload_start_and_stop(
    mock_config: MagicMock, mock_uploader_factory: MagicMock, client: TestClient, tmp_path: Path
) -> None:
    import threading
    import time

    from ai_influencer_studio.web import app as web_app

    state_path = tmp_path / "state.json"
    mock_config.return_value = StudioConfig(
        data_dir=tmp_path,
        media_dir=tmp_path / "media",
        gdrive_state_path=state_path,
    )

    # The worker blocks until told to finish, so "running" stays true and the
    # second start reliably conflicts.
    release = threading.Event()
    mock_uploader = MagicMock()

    def _blocking_upload(**kwargs):
        stop_event = kwargs.get("stop_event")
        release.wait(timeout=10)
        if stop_event is not None and stop_event.is_set():
            return {"status": "stopped", "uploaded": 0, "batch_count": 0, "remaining_pending": 0}
        return {"status": "done", "uploaded": 0, "batch_count": 0, "remaining_pending": 0}

    mock_uploader.upload_pending.side_effect = _blocking_upload
    mock_uploader_factory.return_value = mock_uploader

    # Reset any state left over from previous tests.
    web_app._GDRIVE_RUN.update(thread=None, stop_event=None, running=False, started_at=None, last_error=None, progress=None)

    response = client.post("/api/gdrive/upload/start")
    assert response.status_code == 202
    assert response.json()["started"] is True

    # A second start while running should conflict.
    response = client.post("/api/gdrive/upload/start")
    assert response.status_code == 409

    # Stop is requested while running and observed by the worker.
    response = client.post("/api/gdrive/upload/stop")
    assert response.status_code == 200
    assert response.json()["stopped"] is True
    assert web_app._GDRIVE_RUN["stop_event"].is_set()

    # Releasing the worker lets the thread finish; then stop is a no-op.
    release.set()
    deadline = time.time() + 5
    while web_app._GDRIVE_RUN["running"] and time.time() < deadline:
        time.sleep(0.05)
    assert web_app._GDRIVE_RUN["running"] is False
    response = client.post("/api/gdrive/upload/stop")
    assert response.status_code == 200
    assert response.json()["stopped"] is False
