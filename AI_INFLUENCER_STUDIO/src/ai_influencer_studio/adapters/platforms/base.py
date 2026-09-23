"""Base class for platform-specific upload adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BasePlatformAdapter(ABC):
    """Abstract base class for publishing to a social media platform."""

    platform_name: str = ""

    @abstractmethod
    def publish(self, content: str, media_paths: list[str] | None = None) -> dict[str, Any]:
        """Publish content to the platform.

        Args:
            content: The text content to publish.
            media_paths: Optional list of media file paths.

        Returns:
            A dict with at least a ``success`` key.
        """
        raise NotImplementedError
