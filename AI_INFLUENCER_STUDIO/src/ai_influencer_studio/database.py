"""SQLite persistence for scheduled posts and generated content."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class ScheduledPost:
    """A post scheduled for publishing."""

    platform: str
    content: str
    scheduled_at: datetime
    media_paths: list[str] = field(default_factory=list)
    hashtags: list[str] = field(default_factory=list)
    status: str = "pending"
    id: int | None = None
    retry_count: int = 0
    next_retry_at: datetime | None = None
    error_message: str = ""


class StudioDatabase:
    """SQLite-backed state for the studio."""

    def __init__(self, db_path: Path | str) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS scheduled_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    content TEXT NOT NULL,
                    media_paths TEXT,
                    hashtags TEXT,
                    scheduled_at TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    retry_count INTEGER DEFAULT 0,
                    next_retry_at TEXT,
                    error_message TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS generated_content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_type TEXT NOT NULL,
                    topic TEXT,
                    platform TEXT,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def add_scheduled_post(self, post: ScheduledPost) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO scheduled_posts (platform, content, media_paths, hashtags, scheduled_at, status, retry_count, next_retry_at, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    post.platform,
                    post.content,
                    json.dumps(post.media_paths),
                    json.dumps(post.hashtags),
                    post.scheduled_at.isoformat(),
                    post.status,
                    post.retry_count,
                    post.next_retry_at.isoformat() if post.next_retry_at else None,
                    post.error_message,
                ),
            )
            conn.commit()
            return cursor.lastrowid  # type: ignore[return-value]

    def get_pending_posts(self) -> list[ScheduledPost]:
        """Return posts eligible for publishing.

        Includes both pending posts and posts that are retrying. The caller
        (scheduler) is responsible for filtering by ``scheduled_at`` and
        ``next_retry_at`` to avoid timezone mismatches between SQLite and
        Python.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT * FROM scheduled_posts
                WHERE status IN ('pending', 'retrying')
                ORDER BY scheduled_at
                """
            ).fetchall()
        return [self._row_to_post(row) for row in rows]

    def get_all_posts(self) -> list[ScheduledPost]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM scheduled_posts ORDER BY scheduled_at DESC").fetchall()
        return [self._row_to_post(row) for row in rows]

    def mark_posted(self, post_id: int) -> None:
        self._mark_status(post_id, "posted")

    def _mark_status(self, post_id: int, status: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE scheduled_posts SET status = ? WHERE id = ?",
                (status, post_id),
            )
            conn.commit()

    def update_retry_state(
        self,
        post_id: int,
        retry_count: int,
        next_retry_at: datetime | None,
        error_message: str,
    ) -> None:
        """Update retry state for a scheduled post."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE scheduled_posts
                SET retry_count = ?, next_retry_at = ?, error_message = ?, status = ?
                WHERE id = ?
                """,
                (
                    retry_count,
                    next_retry_at.isoformat() if next_retry_at else None,
                    error_message,
                    "retrying" if retry_count > 0 else "pending",
                    post_id,
                ),
            )
            conn.commit()

    def save_generated_content(
        self,
        content_type: str,
        content: str,
        topic: str | None = None,
        platform: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO generated_content (content_type, topic, platform, content, metadata)
                VALUES (?, ?, ?, ?, ?)
                """,
                (content_type, topic, platform, content, json.dumps(metadata or {})),
            )
            conn.commit()
            return cursor.lastrowid  # type: ignore[return-value]

    def _row_to_post(self, row: sqlite3.Row) -> ScheduledPost:
        return ScheduledPost(
            id=row["id"],
            platform=row["platform"],
            content=row["content"],
            media_paths=json.loads(row["media_paths"] or "[]"),
            hashtags=json.loads(row["hashtags"] or "[]"),
            scheduled_at=datetime.fromisoformat(row["scheduled_at"]),
            status=row["status"],
            retry_count=row["retry_count"],
            next_retry_at=datetime.fromisoformat(row["next_retry_at"]) if row["next_retry_at"] else None,
            error_message=row["error_message"] or "",
        )
