"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from ai_influencer_studio.config import StudioConfig
from ai_influencer_studio.web.auth import _get_configured_key


@pytest.fixture(autouse=True)
def _clear_auth_cache() -> None:
    """Clear the cached API key before every test.

    ``web.auth._get_configured_key`` is decorated with ``lru_cache``; without
    clearing it, tests that set ``AISTUDIO_API_KEY`` would leak into later
    tests.
    """
    _get_configured_key.cache_clear()  # type: ignore[attr-defined]
    yield
    _get_configured_key.cache_clear()  # type: ignore[attr-defined]


@pytest.fixture
def studio_config(tmp_path: pytest.TempPathFactory) -> StudioConfig:
    """Return a StudioConfig that uses a temporary data directory."""
    return StudioConfig(
        data_dir=tmp_path / "data",
        media_dir=tmp_path / "media",
    )
