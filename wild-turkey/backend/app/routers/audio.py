"""Audio & Voice Hub Router."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, File, Header, UploadFile

from app.services.audio_service import transcribe_audio

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/transcribe")
async def transcribe_voice_note(
    file: UploadFile = File(...),
    authorization: str | None = Header(None),
) -> dict[str, Any]:
    """Transcribe an audio file using Whisper."""
    api_key = None
    if authorization and authorization.startswith("Bearer "):
        api_key = authorization.replace("Bearer ", "").strip()
        
    file_bytes = await file.read()
    result = await transcribe_audio(
        file_bytes=file_bytes,
        file_name=file.filename or "audio.wav",
        api_key=api_key,
    )
    return result
