"""YouTube publishing for AI Influencer Studio.

Closes the research -> plan -> execute -> **publish** loop: a song plan (as
produced by :class:`~ai_influencer_studio.music_video_researcher`) carries the
title, genre, mood, BPM, and characters, so YouTube metadata is generated from
the plan instead of being typed by hand.

Uploads use the YouTube Data API v3 with OAuth2 desktop credentials
(``InstalledAppFlow``), mirroring the Drive API backend in ``gdrive_uploader``:
a one-time consent saves a token that refreshes automatically afterwards.
Thumbnails and playlists are supported, and the append-only metadata pattern
(``uploaded`` + ``video_id`` + ``url``) matches the uploader's done-list design
so a re-run never double-publishes.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# OAuth2 token + client-secrets locations (same convention as gdrive_uploader).
YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]
DEFAULT_TOKEN_PATH = Path("~/.ai_influencer_studio/youtube_token.json").expanduser()
DEFAULT_CLIENT_SECRETS_PATH = Path("~/.ai_influencer_studio/youtube_client_secrets.json").expanduser()

DEFAULT_CATEGORY_ID = "10"  # Music
DEFAULT_PRIVACY = "private"
BASE_TAGS = ["AI", "music", "video", "generated", "AI music video"]

try:  # optional dependency (google extra, same as the Drive API backend)
    from google.oauth2.credentials import Credentials as YouTubeCredentials
    from googleapiclient.discovery import build as youtube_build
    from googleapiclient.http import MediaFileUpload
except ImportError:  # pragma: no cover - exercised only when google client absent
    YouTubeCredentials = None  # type: ignore[assignment,misc]
    youtube_build = None  # type: ignore[assignment]
    MediaFileUpload = None  # type: ignore[assignment]


def build_metadata(song: Mapping[str, Any]) -> dict[str, Any]:
    """Build YouTube title/description/tags from a SongPlan dict.

    Never touches the network; used both by the CLI/web preview and by the
    uploader itself. The plan keys follow ``SongPlan.to_dict()``.
    """
    name = str(song.get("song_name") or Path(str(song.get("audio_path") or "video")).stem)
    genre = str(song.get("genre") or "").strip()
    mood = str(song.get("mood") or "").strip()
    bpm = song.get("bpm")
    duration = song.get("duration") or 0.0

    title = f"{name} | {genre}" if genre else name

    tags = list(BASE_TAGS)
    if genre:
        tags.append(genre.lower())
    if mood:
        tags.append(mood.lower())
    if bpm:
        tags.append(f"{int(float(bpm))}bpm")
    tags = list(dict.fromkeys(tags))[:10]

    lines = [
        f"{title}",
        "",
        "🎵 AI-generated music video",
        "🤖 Produced with AI Influencer Studio",
    ]
    if genre or mood or bpm or duration:
        lines.append("")
        lines.append("Track details:")
        if genre:
            lines.append(f"- Genre: {genre}")
        if mood:
            lines.append(f"- Mood: {mood}")
        if bpm:
            lines.append(f"- BPM: {bpm}")
        if duration:
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            lines.append(f"- Length: {minutes}:{seconds:02d}")
    lines.extend(["", "#AI #MusicVideo #GeneratedArt #AIMusic"])
    description = "\n".join(lines)

    return {
        "title": title,
        "description": description,
        "tags": tags,
        "song_name": name,
        "genre": genre,
        "mood": mood,
        "bpm": bpm,
        "duration": duration,
    }


class YouTubePublisher:
    """OAuth2 YouTube uploader for song plans."""

    def __init__(
        self,
        token_path: Path | None = None,
        client_secrets_path: Path | None = None,
    ) -> None:
        self.token_path = Path(token_path) if token_path else DEFAULT_TOKEN_PATH
        self.client_secrets_path = Path(client_secrets_path) if client_secrets_path else DEFAULT_CLIENT_SECRETS_PATH

    # -- auth ----------------------------------------------------------------

    def _credentials(self) -> Any:
        """Return valid YouTube OAuth2 credentials, running the one-time flow if needed."""
        if YouTubeCredentials is None or youtube_build is None:
            raise RuntimeError(
                "YouTube publishing needs google-auth + google-api-python-client; "
                "run 'pip install google-auth google-auth-oauthlib google-api-python-client'"
            )
        from google.auth.transport.requests import Request as GAuthRequest
        from google_auth_oauthlib.flow import InstalledAppFlow

        creds = None
        if self.token_path.exists():
            creds = YouTubeCredentials.from_authorized_user_file(str(self.token_path), YOUTUBE_SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(GAuthRequest())
                except Exception:
                    creds = None
            if not creds or not creds.valid:
                if not self.client_secrets_path.exists():
                    raise RuntimeError(
                        f"YouTube OAuth client secrets not found: {self.client_secrets_path} — "
                        "download a Google Cloud OAuth Desktop client JSON (with YouTube Data API v3 "
                        "enabled) and save it there"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(str(self.client_secrets_path), YOUTUBE_SCOPES)
                creds = flow.run_local_server(port=0)
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            self.token_path.write_text(creds.to_json(), encoding="utf-8")
        return creds

    def _service(self) -> Any:
        """Build an authenticated YouTube v3 service object."""
        return youtube_build("youtube", "v3", credentials=self._credentials(), cache_discovery=False)

    # -- actions -------------------------------------------------------------

    def upload(
        self,
        video_path: str | Path,
        *,
        title: str,
        description: str = "",
        tags: list[str] | None = None,
        category_id: str = DEFAULT_CATEGORY_ID,
        privacy: str = DEFAULT_PRIVACY,
        thumbnail_path: str | Path | None = None,
        playlist_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """Upload one video (resumable), then thumbnail + playlists on success."""
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        service = self._service()

        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags or BASE_TAGS,
                "categoryId": category_id,
            },
            "status": {
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": False,
            },
        }
        media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True, chunksize=1024 * 1024)
        request = service.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            _, response = request.next_chunk()

        video_id = response.get("id")
        thumbnail_ok = False
        if thumbnail_path and Path(thumbnail_path).exists():
            thumbnail_ok = self.upload_thumbnail(service, video_id, Path(thumbnail_path))
        added_playlists: list[str] = []
        for playlist_id in playlist_ids or []:
            if self.add_to_playlist(service, video_id, playlist_id):
                added_playlists.append(playlist_id)

        return {
            "video_id": video_id,
            "url": f"https://youtu.be/{video_id}",
            "title": title,
            "thumbnail_uploaded": thumbnail_ok,
            "playlists": added_playlists,
            "privacy": privacy,
            "uploaded_at": datetime.now(UTC).isoformat(),
        }

    def upload_thumbnail(self, service: Any, video_id: str, thumbnail_path: Path) -> bool:
        """Set a custom thumbnail; returns False (not raises) on API errors."""
        try:
            media = MediaFileUpload(str(thumbnail_path), mimetype="image/jpeg")
            service.thumbnails().set(videoId=video_id, media_body=media).execute()
            return True
        except Exception:
            return False

    def add_to_playlist(self, service: Any, video_id: str, playlist_id: str) -> bool:
        """Add a video to a playlist; returns False (not raises) on API errors."""
        try:
            service.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {"kind": "youtube#video", "videoId": video_id},
                    }
                },
            ).execute()
            return True
        except Exception:
            return False

    def create_playlist(self, service: Any, title: str, description: str = "", privacy: str = DEFAULT_PRIVACY) -> str | None:
        """Create a playlist and return its id, or None on API error."""
        try:
            response = service.playlists().insert(
                part="snippet,status",
                body={
                    "snippet": {"title": title, "description": description},
                    "status": {"privacyStatus": privacy},
                },
            ).execute()
            return response.get("id")
        except Exception:
            return None

    def channel_info(self) -> dict[str, Any]:
        """Return the authenticated channel's snippet + statistics."""
        service = self._service()
        response = service.channels().list(part="snippet,statistics", mine=True).execute()
        items = response.get("items") or []
        if not items:
            return {}
        channel = items[0]
        stats = channel.get("statistics", {})
        return {
            "id": channel.get("id"),
            "title": channel.get("snippet", {}).get("title"),
            "subscribers": stats.get("subscriberCount", "0"),
            "views": stats.get("viewCount", "0"),
            "videos": stats.get("videoCount", "0"),
        }

    def publish_song(
        self,
        song: Mapping[str, Any],
        video_path: str | Path,
        *,
        thumbnail_path: str | Path | None = None,
        privacy: str = DEFAULT_PRIVACY,
        category_id: str = DEFAULT_CATEGORY_ID,
        playlist_ids: list[str] | None = None,
        create_playlist_title: str | None = None,
    ) -> dict[str, Any]:
        """Upload a finished video with metadata generated from its song plan.

        Returns the upload result plus the generated metadata so callers can
        persist an append-only ``uploaded`` record. When ``create_playlist_title``
        is given, the playlist is created first and the video filed into it.
        """
        metadata = build_metadata(song)
        effective_playlists = list(playlist_ids or [])
        if create_playlist_title:
            service = self._service()
            playlist_id = self.create_playlist(service, create_playlist_title)
            if playlist_id:
                effective_playlists.append(playlist_id)
        result = self.upload(
            video_path,
            title=metadata["title"],
            description=metadata["description"],
            tags=metadata["tags"],
            category_id=category_id,
            privacy=privacy,
            thumbnail_path=thumbnail_path,
            playlist_ids=effective_playlists,
        )
        result["metadata"] = metadata
        result["video_path"] = str(video_path)
        return result


def save_publish_record(result: dict[str, Any], path: Path) -> Path:
    """Append an upload record to a JSONL publish log (append-only)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(result) + "\n")
    return path
