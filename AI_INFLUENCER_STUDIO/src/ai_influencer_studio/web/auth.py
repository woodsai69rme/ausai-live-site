"""Basic API-key authentication for the web dashboard.

The dashboard is intended for local use. Set ``AISTUDIO_API_KEY`` in the
environment or in ``config.json`` to require a key on every request.
"""

from __future__ import annotations

import os
from functools import lru_cache

from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

from ai_influencer_studio.config import StudioConfig

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


@lru_cache(maxsize=1)
def _get_configured_key() -> str | None:
    """Return the configured API key, if any."""
    env_key = os.environ.get("AISTUDIO_API_KEY")
    if env_key:
        return env_key
    config = StudioConfig.from_file()
    return config.platforms.get("api_key", "")  # type: ignore[return-value]


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:  # type: ignore[assignment]
    """FastAPI dependency that validates the API key header.

    If no API key is configured, all requests are allowed.
    """
    expected = _get_configured_key()
    if not expected:
        return api_key
    if api_key != expected:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return api_key
