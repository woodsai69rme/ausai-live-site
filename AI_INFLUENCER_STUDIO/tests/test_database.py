"""Tests for ai_influencer_studio.database."""

from datetime import datetime, timedelta
from pathlib import Path

from ai_influencer_studio.database import ScheduledPost, StudioDatabase


def test_add_and_retrieve_post(tmp_path: Path) -> None:
    db = StudioDatabase(tmp_path / "studio.db")
    post = ScheduledPost(
        platform="twitter",
        content="Hello world",
        scheduled_at=datetime.now() + timedelta(hours=1),
        hashtags=["ai", "test"],
    )
    post_id = db.add_scheduled_post(post)
    assert post_id is not None

    pending = db.get_pending_posts()
    assert len(pending) == 1
    assert pending[0].platform == "twitter"
    assert pending[0].hashtags == ["ai", "test"]


def test_mark_posted(tmp_path: Path) -> None:
    db = StudioDatabase(tmp_path / "studio.db")
    post = ScheduledPost(
        platform="instagram",
        content="Test post",
        scheduled_at=datetime.now() - timedelta(minutes=1),
    )
    post_id = db.add_scheduled_post(post)
    db.mark_posted(post_id)

    pending = db.get_pending_posts()
    assert len(pending) == 0

    all_posts = db.get_all_posts()
    assert all_posts[0].status == "posted"


def test_save_generated_content(tmp_path: Path) -> None:
    db = StudioDatabase(tmp_path / "studio.db")
    content_id = db.save_generated_content(
        content_type="post",
        content="Generated content",
        topic="AI",
        platform="twitter",
        metadata={"model": "gpt-4o-mini"},
    )
    assert content_id is not None
