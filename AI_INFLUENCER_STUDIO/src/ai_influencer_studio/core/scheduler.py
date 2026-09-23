"""Background scheduler for publishing due posts.

The scheduler is intentionally simple: it polls the SQLite database for
pending posts whose ``scheduled_at`` time has passed, then dispatches them
through the appropriate adapter.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from threading import Event, Thread
from typing import Any

from ai_influencer_studio.adapters.automation import AutomationAdapter
from ai_influencer_studio.config import StudioConfig
from ai_influencer_studio.database import ScheduledPost, StudioDatabase

logger = logging.getLogger(__name__)


class PublishScheduler:
    """Polls the database and publishes due scheduled posts."""

    MAX_RETRIES = 3

    def __init__(
        self,
        config: StudioConfig | None = None,
        poll_interval: int = 60,
    ) -> None:
        self.config = config or StudioConfig.from_file()
        self.poll_interval = poll_interval
        self.db = StudioDatabase(self.config.data_dir / "studio.db")
        self.adapter = AutomationAdapter(self.config)
        self._stop_event = Event()
        self._thread: Thread | None = None

    def start(self) -> None:
        """Start the scheduler in a background thread."""
        if self._thread is not None and self._thread.is_alive():
            logger.warning("Scheduler already running")
            return

        self._stop_event.clear()
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("Scheduler started")

    def stop(self) -> None:
        """Signal the scheduler to stop."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5)
        logger.info("Scheduler stopped")

    def is_running(self) -> bool:
        """Return whether the scheduler thread is active."""
        return self._thread is not None and self._thread.is_alive()

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                self.tick()
            except Exception as exc:  # pragma: no cover
                logger.exception("Scheduler tick failed: %s", exc)
            self._stop_event.wait(self.poll_interval)

    def tick(self) -> list[dict[str, Any]]:
        """Publish any posts that are due.

        Returns a list of result dicts for posts processed in this tick.
        """
        now = datetime.now()
        pending = self.db.get_pending_posts()
        results: list[dict[str, Any]] = []

        for post in pending:
            if post.scheduled_at <= now and (post.next_retry_at is None or post.next_retry_at <= now):
                result = self._publish(post)
                results.append(result)

        return results

    def _publish(self, post: ScheduledPost) -> dict[str, Any]:
        """Attempt to publish a single scheduled post."""
        result: dict[str, Any] = {
            "post_id": post.id,
            "platform": post.platform,
            "success": False,
            "error": None,
        }
        try:
            media_path = post.media_paths[0] if post.media_paths else None
            self.adapter.post_via_api(
                platform=post.platform,
                content=post.content,
                media_path=media_path,
            )
            self.db.mark_posted(post.id)
            result["success"] = True
            logger.info("Published post %s to %s", post.id, post.platform)
        except Exception as exc:  # pragma: no cover
            error_message = str(exc)
            result["error"] = error_message
            logger.error("Failed to publish post %s: %s", post.id, exc)

            if post.retry_count < self.MAX_RETRIES:
                next_retry = datetime.now() + timedelta(minutes=2 ** post.retry_count)
                self.db.update_retry_state(
                    post.id,
                    post.retry_count + 1,
                    next_retry,
                    error_message,
                )
                logger.info("Scheduled retry %s for post %s at %s", post.retry_count + 1, post.id, next_retry)
            else:
                self.db._mark_status(post.id, "failed")
                logger.error("Post %s exceeded max retries and is now failed", post.id)

        return result
