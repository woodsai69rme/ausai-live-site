"""Audio Processing Service — Voice Hub Transcriptions."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def transcribe_audio(
    file_bytes: bytes,
    file_name: str = "audio.wav",
    api_key: str | None = None,
) -> dict[str, Any]:
    """Transcribe audio bytes using OpenRouter / Groq / OpenAI Whisper API."""
    key = api_key or settings.OPENROUTER_API_KEY
    if not key:
        return {"error": "API key required for audio transcription", "text": ""}

    headers = {
        "Authorization": f"Bearer {key}",
    }

    files = {
        "file": (file_name, file_bytes, "audio/wav"),
        "model": (None, "whisper-large-v3"),
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.OPENROUTER_API_BASE}/audio/transcriptions",
                headers=headers,
                files=files,
            )
            response.raise_for_status()
            data = response.json()
            return {"text": data.get("text", ""), "raw": data}
    except Exception as e:
        logger.error(f"Audio transcription failed: {e}")
        return {"error": str(e), "text": ""}
