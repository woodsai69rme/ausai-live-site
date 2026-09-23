"""Tests for text-based platform adapters (Twitter, Instagram, Facebook)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ai_influencer_studio.adapters.platforms.facebook import FacebookAdapter
from ai_influencer_studio.adapters.platforms.instagram import InstagramAdapter
from ai_influencer_studio.adapters.platforms.twitter import TwitterAdapter


@pytest.fixture
def automation() -> MagicMock:
    return MagicMock()


def test_twitter_adapter_publishes_text(automation: MagicMock) -> None:
    adapter = TwitterAdapter(automation)
    automation.post_to_twitter.return_value = True

    result = adapter.publish("Hello Twitter!")

    automation.post_to_twitter.assert_called_once_with("Hello Twitter!", None)
    assert result["success"] is True
    assert result["platform"] == "twitter"


def test_twitter_adapter_publishes_with_media(automation: MagicMock) -> None:
    adapter = TwitterAdapter(automation)
    automation.post_to_twitter.return_value = True

    result = adapter.publish("Hello Twitter!", media_paths=["/tmp/image.png"])

    automation.post_to_twitter.assert_called_once_with("Hello Twitter!", "/tmp/image.png")
    assert result["success"] is True


def test_instagram_adapter_publishes_with_media(automation: MagicMock) -> None:
    adapter = InstagramAdapter(automation)
    automation.post_to_instagram.return_value = True

    result = adapter.publish("Hello Instagram!", media_paths=["/tmp/image.png"])

    automation.post_to_instagram.assert_called_once_with("Hello Instagram!", "/tmp/image.png")
    assert result["success"] is True


def test_instagram_adapter_requires_media(automation: MagicMock) -> None:
    adapter = InstagramAdapter(automation)

    with pytest.raises(ValueError, match="media"):
        adapter.publish("Hello Instagram!")


def test_facebook_adapter_publishes_text(automation: MagicMock) -> None:
    adapter = FacebookAdapter(automation)
    automation.post_to_facebook.return_value = True

    result = adapter.publish("Hello Facebook!")

    automation.post_to_facebook.assert_called_once_with("Hello Facebook!", None)
    assert result["success"] is True


def test_facebook_adapter_publishes_with_media(automation: MagicMock) -> None:
    adapter = FacebookAdapter(automation)
    automation.post_to_facebook.return_value = True

    result = adapter.publish("Hello Facebook!", media_paths=["/tmp/image.png"])

    automation.post_to_facebook.assert_called_once_with("Hello Facebook!", "/tmp/image.png")
    assert result["success"] is True


def test_twitter_adapter_reports_failure(automation: MagicMock) -> None:
    adapter = TwitterAdapter(automation)
    automation.post_to_twitter.return_value = False

    result = adapter.publish("Hello Twitter!")

    automation.post_to_twitter.assert_called_once_with("Hello Twitter!", None)
    assert result["success"] is False
    assert result["platform"] == "twitter"


def test_instagram_adapter_reports_failure(automation: MagicMock) -> None:
    adapter = InstagramAdapter(automation)
    automation.post_to_instagram.return_value = False

    result = adapter.publish("Hello Instagram!", media_paths=["/tmp/image.png"])

    automation.post_to_instagram.assert_called_once_with("Hello Instagram!", "/tmp/image.png")
    assert result["success"] is False
    assert result["platform"] == "instagram"


def test_facebook_adapter_reports_failure(automation: MagicMock) -> None:
    adapter = FacebookAdapter(automation)
    automation.post_to_facebook.return_value = False

    result = adapter.publish("Hello Facebook!")

    automation.post_to_facebook.assert_called_once_with("Hello Facebook!", None)
    assert result["success"] is False
    assert result["platform"] == "facebook"
