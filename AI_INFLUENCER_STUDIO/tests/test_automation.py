"""Tests for ai_influencer_studio.adapters.automation."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ai_influencer_studio.adapters.automation import AutomationAdapter
from ai_influencer_studio.config import StudioConfig


@pytest.fixture
def adapter(tmp_path: Path) -> AutomationAdapter:
    config = StudioConfig(data_dir=tmp_path, media_dir=tmp_path / "media")
    return AutomationAdapter(config)


def test_push_to_n8n_raises_when_url_missing(tmp_path: Path) -> None:
    config = StudioConfig(
        data_dir=tmp_path,
        media_dir=tmp_path / "media",
        n8n_webhook_url="",
    )
    adapter = AutomationAdapter(config)
    with pytest.raises(ValueError, match="n8n_webhook_url is not configured"):
        adapter.push_to_n8n({"key": "value"})


@patch("ai_influencer_studio.adapters.automation.requests.post")
def test_push_to_n8n_sends_payload(mock_post: MagicMock, tmp_path: Path) -> None:
    config = StudioConfig(
        data_dir=tmp_path,
        media_dir=tmp_path / "media",
        n8n_webhook_url="http://localhost:5678/webhook/test",
    )
    adapter = AutomationAdapter(config)
    mock_post.return_value = MagicMock(status_code=200, text="ok")
    mock_post.return_value.raise_for_status = lambda: None

    result = adapter.push_to_n8n({"video": "path.mp4"})

    assert result["status"] == 200
    mock_post.assert_called_once()


@patch("ai_influencer_studio.adapters.automation.requests.post")
def test_push_to_postiz_sends_payload(mock_post: MagicMock, tmp_path: Path) -> None:
    config = StudioConfig(
        data_dir=tmp_path,
        media_dir=tmp_path / "media",
        postiz_api_url="http://localhost:4200/api/posts",
        postiz_api_key="secret",
    )
    adapter = AutomationAdapter(config)
    mock_post.return_value = MagicMock(status_code=201, text="created")
    mock_post.return_value.raise_for_status = lambda: None

    result = adapter.push_to_postiz({"content": "hello"})

    assert result["status"] == 201
    mock_post.assert_called_once()


@patch("ai_influencer_studio.adapters.automation.requests.post")
def test_push_to_mixpost_sends_payload(mock_post: MagicMock, tmp_path: Path) -> None:
    config = StudioConfig(
        data_dir=tmp_path,
        media_dir=tmp_path / "media",
        mixpost_api_url="http://localhost:8080/api/posts",
        mixpost_api_key="secret",
    )
    adapter = AutomationAdapter(config)
    mock_post.return_value = MagicMock(status_code=201, text="created")
    mock_post.return_value.raise_for_status = lambda: None

    result = adapter.push_to_mixpost({"content": "hello"})

    assert result["status"] == 201
    mock_post.assert_called_once()


def test_push_to_scheduler_routes_to_n8n(adapter: AutomationAdapter) -> None:
    with patch.object(adapter, "push_to_n8n", return_value={"status": 200}) as mock_n8n:
        result = adapter.push_to_scheduler("n8n", {"video": "path.mp4"})
    assert result["status"] == 200
    mock_n8n.assert_called_once_with({"video": "path.mp4"})


def test_push_to_scheduler_routes_to_postiz(adapter: AutomationAdapter) -> None:
    with patch.object(adapter, "push_to_postiz", return_value={"status": 201}) as mock_postiz:
        result = adapter.push_to_scheduler("postiz", {"content": "hello"})
    assert result["status"] == 201
    mock_postiz.assert_called_once()


def test_push_to_scheduler_routes_to_mixpost(adapter: AutomationAdapter) -> None:
    with patch.object(adapter, "push_to_mixpost", return_value={"status": 201}) as mock_mixpost:
        result = adapter.push_to_scheduler("mixpost", {"content": "hello"})
    assert result["status"] == 201
    mock_mixpost.assert_called_once()


def test_push_to_scheduler_rejects_unknown_scheduler(adapter: AutomationAdapter) -> None:
    with pytest.raises(ValueError, match="Unsupported scheduler"):
        adapter.push_to_scheduler("unknown", {})


def test_push_to_postiz_raises_when_unconfigured(tmp_path: Path) -> None:
    config = StudioConfig(
        data_dir=tmp_path,
        media_dir=tmp_path / "media",
        postiz_api_url="",
        postiz_api_key="",
    )
    adapter = AutomationAdapter(config)
    with pytest.raises(ValueError, match="postiz_api_url and postiz_api_key must be configured"):
        adapter.push_to_postiz({"content": "hello"})


def test_push_to_mixpost_raises_when_unconfigured(tmp_path: Path) -> None:
    config = StudioConfig(
        data_dir=tmp_path,
        media_dir=tmp_path / "media",
        mixpost_api_url="",
        mixpost_api_key="",
    )
    adapter = AutomationAdapter(config)
    with pytest.raises(ValueError, match="mixpost_api_url and mixpost_api_key must be configured"):
        adapter.push_to_mixpost({"content": "hello"})


def test_post_via_postiz_rejects_local_media_paths(adapter: AutomationAdapter) -> None:
    with pytest.raises(ValueError, match="needs hosted media URLs"):
        adapter.post_via_postiz(
            "hello world",
            media_urls=["C:/Users/karma/clip.mp4"],
            platforms=["youtube"],
        )


def test_post_via_postiz_builds_v2_payload(tmp_path: Path) -> None:
    config = StudioConfig(
        data_dir=tmp_path,
        media_dir=tmp_path / "media",
        postiz_api_url="http://localhost:5000/api/v1/posts",
        postiz_api_key="postiz-key",
    )
    adapter = AutomationAdapter(config)
    with patch("ai_influencer_studio.adapters.automation.requests.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=201, text="created")
        mock_post.return_value.raise_for_status = lambda: None
        result = adapter.post_via_postiz(
            "check out this video",
            media_urls=["https://cdn.example.com/clip.mp4"],
            platforms=["youtube", "tiktok"],
        )

    assert result["scheduler"] == "postiz"
    assert result["status"] == 201
    payload = mock_post.call_args.kwargs["json"]
    assert payload["text"] == "check out this video"
    assert payload["platforms"] == ["youtube", "tiktok"]
    assert payload["media"] == [{"url": "https://cdn.example.com/clip.mp4"}]
    assert mock_post.call_args.kwargs["headers"] == {"Authorization": "Bearer postiz-key"}


def test_post_via_mixpost_passes_local_media_through(tmp_path: Path) -> None:
    config = StudioConfig(
        data_dir=tmp_path,
        media_dir=tmp_path / "media",
        mixpost_api_url="http://localhost:8080/api/webhooks/post",
        mixpost_api_key="mixpost-key",
    )
    adapter = AutomationAdapter(config)
    with patch("ai_influencer_studio.adapters.automation.requests.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=200, text="ok")
        mock_post.return_value.raise_for_status = lambda: None
        result = adapter.post_via_mixpost(
            "local file post",
            media_urls=["C:/media/clip.mp4"],
            platforms=["instagram"],
        )

    assert result["scheduler"] == "mixpost"
    payload = mock_post.call_args.kwargs["json"]
    assert payload["media"] == ["C:/media/clip.mp4"]
    assert payload["name"] == "local file post"
