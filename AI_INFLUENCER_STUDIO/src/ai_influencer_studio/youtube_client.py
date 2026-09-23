"""YouTube Data API v3 client for music-video trend research.

Provides a small wrapper around the official YouTube Data API search endpoint,
with a best-effort fallback to public jina.ai scraping when no API key is
configured.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any

import requests

logger = logging.getLogger(__name__)

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_CHANNELS_URL = "https://www.googleapis.com/youtube/v3/channels"
JINA_PROXY_URL = "https://r.jina.ai/http://youtube.com/results"


class YouTubeDataClient:
    """Fetch trending music-video metadata from YouTube.

    Uses the YouTube Data API v3 when ``api_key`` is provided; otherwise falls
    back to jina.ai-based scraping.
    """

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.environ.get("YOUTUBE_API_KEY", "")

    def fetch_trends(
        self,
        keywords: list[str] | None = None,
        max_results: int = 10,
    ) -> list[dict[str, Any]]:
        """Return trending video metadata for the given keywords."""
        if self.api_key:
            return self._fetch_with_api(keywords, max_results)
        return self._fetch_with_scrape(keywords, max_results)

    def _fetch_with_api(
        self,
        keywords: list[str] | None,
        max_results: int,
    ) -> list[dict[str, Any]]:
        trends: list[dict[str, Any]] = []
        per_kw = max(1, max_results // max(len(keywords) or 1, 1))
        for kw in keywords or ["music video"]:
            try:
                params = {
                    "part": "snippet",
                    "q": kw,
                    "type": "video",
                    "maxResults": per_kw,
                    "key": self.api_key,
                }
                resp = requests.get(YOUTUBE_SEARCH_URL, params=params, timeout=15)
                resp.raise_for_status()
                data = resp.json()
                for item in data.get("items", []):
                    vid = item.get("id", {}).get("videoId")
                    snippet = item.get("snippet", {})
                    if vid:
                        trends.append({
                            "keyword": kw,
                            "video_id": vid,
                            "title": snippet.get("title", "Unknown"),
                            "url": f"https://youtube.com/watch?v={vid}",
                        })
            except Exception as exc:
                logger.warning("YouTube API trend fetch failed for %r: %s", kw, exc)
                trends.append({"keyword": kw, "error": str(exc)})
        return self._dedupe(trends)[:max_results]

    def _fetch_with_scrape(
        self,
        keywords: list[str] | None,
        max_results: int,
    ) -> list[dict[str, Any]]:
        trends: list[dict[str, Any]] = []
        for kw in keywords or ["music video"]:
            try:
                url = f"{JINA_PROXY_URL}?search_query={requests.utils.quote(kw)}"
                resp = requests.get(url, timeout=15)
                resp.raise_for_status()
                content = resp.text
                video_ids = re.findall(r"watch\?v=([A-Za-z0-9_-]{11})", content)
                titles = re.findall(r'"title":\s*"([^"]+)"', content)
                for i, vid in enumerate(video_ids[:5]):
                    trends.append({
                        "keyword": kw,
                        "video_id": vid,
                        "title": titles[i] if i < len(titles) else "Unknown",
                        "url": f"https://youtube.com/watch?v={vid}",
                    })
            except Exception as exc:
                logger.warning("jina.ai trend fetch failed for %r: %s", kw, exc)
                trends.append({"keyword": kw, "error": str(exc)})
        return self._dedupe(trends)[:max_results]

    def fetch_channel_stats(self, channel_id: str) -> dict[str, Any]:
        """Return a channel's snippet + statistics (public data via API key).

        Returns an empty dict when the API key is missing or the channel is
        unknown, so the researcher can skip silently instead of crashing.
        """
        if not self.api_key or not channel_id:
            return {}
        try:
            params = {
                "part": "snippet,statistics",
                "id": channel_id,
                "key": self.api_key,
            }
            resp = requests.get(YOUTUBE_CHANNELS_URL, params=params, timeout=15)
            resp.raise_for_status()
            items = resp.json().get("items", [])
            if not items:
                return {}
            channel = items[0]
            stats = channel.get("statistics", {})
            return {
                "channel_id": channel_id,
                "title": channel.get("snippet", {}).get("title", ""),
                "description": channel.get("snippet", {}).get("description", ""),
                "subscribers": stats.get("subscriberCount", "0"),
                "views": stats.get("viewCount", "0"),
                "videos": stats.get("videoCount", "0"),
            }
        except Exception as exc:
            logger.warning("YouTube channel stats fetch failed: %s", exc)
            return {}

    def fetch_top_videos(self, channel_id: str, max_results: int = 10) -> list[dict[str, Any]]:
        """Return a channel's most-viewed videos (search ordered by viewCount).

        Public data, so it works with just an API key. Empty list when the key
        or channel is missing.
        """
        if not self.api_key or not channel_id:
            return []
        try:
            params = {
                "part": "snippet",
                "channelId": channel_id,
                "order": "viewCount",
                "type": "video",
                "maxResults": max_results,
                "key": self.api_key,
            }
            resp = requests.get(YOUTUBE_SEARCH_URL, params=params, timeout=15)
            resp.raise_for_status()
            videos: list[dict[str, Any]] = []
            for item in resp.json().get("items", []):
                vid = item.get("id", {}).get("videoId")
                snippet = item.get("snippet", {})
                if vid:
                    videos.append({
                        "video_id": vid,
                        "title": snippet.get("title", "Unknown"),
                        "url": f"https://youtube.com/watch?v={vid}",
                    })
            return videos
        except Exception as exc:
            logger.warning("YouTube top-videos fetch failed: %s", exc)
            return []

    @staticmethod
    def _dedupe(trends: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[str] = set()
        unique: list[dict[str, Any]] = []
        for trend in trends:
            vid = trend.get("video_id")
            if vid and vid not in seen:
                seen.add(vid)
                unique.append(trend)
        return unique
