"""Tests for ai_influencer_studio.core.scheduler."""

from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock

from ai_influencer_studio.config import StudioConfig
from ai_influencer_studio.core.scheduler import PublishScheduler
from ai_influencer_studio.database import ScheduledPost, StudioDatabase


def test_scheduler_tick_publishes_due_post(tmp_path: Path) -> None:
    config = StudioConfig(
        data_dir=tmp_path,
        media_dir=tmp_path / "media",
    )
    config.save(tmp_path / "config.json")

    db = StudioDatabase(tmp_path / "studio.db")
    post = ScheduledPost(
        platform="twitter",
        content="Due post",
        scheduled_at=datetime.now() - timedelta(minutes=1),
    )
    db.add_scheduled_post(post)

    scheduler = PublishScheduler(config, poll_interval=1)

    # Mock the automation adapter so we never touch the legacy module.
    mock_adapter = MagicMock()
    mock_adapter.post_via_api.return_value = {"success": True}
    scheduler.adapter = mock_adapter  # type: ignore[assignment]

    results = scheduler.tick()

    assert len(results) == 1
    assert results[0]["post_id"] is not None
    assert results[0]["platform"] == "twitter"
    assert results[0]["success"] is True

    # Verify the post was marked as posted in the database.
    all_posts = db.get_all_posts()
    assert len(all_posts) == 1
    assert all_posts[0].status == "posted"


def test_scheduler_tick_marks_failed_on_error(tmp_path: Path) -> None:
    config = StudioConfig(
        data_dir=tmp_path,
        media_dir=tmp_path / "media",
    )
    config.save(tmp_path / "config.json")

    db = StudioDatabase(tmp_path / "studio.db")
    post = ScheduledPost(
        platform="instagram",
        content="Failing post",
        scheduled_at=datetime.now() - timedelta(minutes=1),
    )
    db.add_scheduled_post(post)

    scheduler = PublishScheduler(config, poll_interval=1)
    # Force immediate failure without retries for this test.
    scheduler.MAX_RETRIES = 0

    # Simulate a publishing failure.
    mock_adapter = MagicMock()
    mock_adapter.post_via_api.side_effect = RuntimeError("API error")
    scheduler.adapter = mock_adapter  # type: ignore[assignment]

    results = scheduler.tick()

    assert len(results) == 1
    assert results[0]["success"] is False
    assert "API error" in str(results[0]["error"])

    # Verify the post was marked as failed in the database.
    all_posts = db.get_all_posts()
    assert len(all_posts) == 1
    assert all_posts[0].status == "failed"


def test_scheduler_retries_failed_post(tmp_path: Path) -> None:
    config = StudioConfig(
        data_dir=tmp_path,
        media_dir=tmp_path / "media",
    )
    config.save(tmp_path / "config.json")

    db = StudioDatabase(tmp_path / "studio.db")
    post = ScheduledPost(
        platform="twitter",
        content="Retry post",
        scheduled_at=datetime.now() - timedelta(minutes=1),
    )
    post_id = db.add_scheduled_post(post)

    scheduler = PublishScheduler(config, poll_interval=1)
    scheduler.MAX_RETRIES = 2

    mock_adapter = MagicMock()
    mock_adapter.post_via_api.side_effect = RuntimeError("API error")
    scheduler.adapter = mock_adapter  # type: ignore[assignment]

    # First tick: post fails and is scheduled for retry.
    results = scheduler.tick()
    assert len(results) == 1
    assert results[0]["success"] is False

    posts = db.get_all_posts()
    assert len(posts) == 1
    assert posts[0].status == "retrying"
    assert posts[0].retry_count == 1
    assert posts[0].next_retry_at is not None
    # Backoff is 2^retry_count minutes = 2 minutes after the first failure.
    assert posts[0].next_retry_at > datetime.now()

    # Simulate that the retry time has passed and trigger a second failure.
    db.update_retry_state(post_id, 1, datetime.now() - timedelta(minutes=1), "API error")

    results = scheduler.tick()
    assert len(results) == 1
    assert results[0]["success"] is False

    posts = db.get_all_posts()
    assert posts[0].retry_count == 2

    # Simulate that the retry time has passed; this failure exhausts retries.
    db.update_retry_state(post_id, 2, datetime.now() - timedelta(minutes=1), "API error")

    results = scheduler.tick()
    assert len(results) == 1
    assert results[0]["success"] is False

    posts = db.get_all_posts()
    assert posts[0].status == "failed"
