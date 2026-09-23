"""Tests for the concurrent multi-model vision client."""

from __future__ import annotations

import base64
from pathlib import Path
from unittest.mock import MagicMock, patch

from ai_influencer_studio.safe_use.multi_model import ModelResult, MultiModelClient, parse_model_ref


def test_parse_model_ref() -> None:
    assert parse_model_ref("ollama::minicpm-v:latest") == ("ollama", "minicpm-v:latest")
    assert parse_model_ref("openrouter::google/gemini:free") == ("openrouter", "google/gemini:free")
    assert parse_model_ref("bare") == ("", "bare")


def test_complete_ollama_sends_vision_images(tmp_path: Path) -> None:
    image = tmp_path / "shot.png"
    image.write_bytes(b"PNGDATA")
    response = MagicMock()
    response.json.return_value = {"message": {"content": "answer"}}
    response.raise_for_status.return_value = None

    client = MultiModelClient()
    with patch("ai_influencer_studio.safe_use.multi_model.requests.post", return_value=response) as mock_post:
        result = client.complete("ollama::minicpm-v", "describe", image_path=image)

    assert result.ok is True
    assert result.text == "answer"
    assert result.provider == "ollama"
    payload = mock_post.call_args.kwargs["json"]
    assert payload["model"] == "minicpm-v"
    assert payload["messages"][-1]["images"] == [base64.b64encode(b"PNGDATA").decode()]
    assert mock_post.call_args.kwargs["proxies"] == {"http": None, "https": None}


def test_complete_openrouter_uses_image_url(tmp_path: Path) -> None:
    image = tmp_path / "shot.png"
    image.write_bytes(b"PNGDATA")
    response = MagicMock()
    response.json.return_value = {"choices": [{"message": {"content": "answer"}}]}
    response.raise_for_status.return_value = None

    client = MultiModelClient(openrouter_api_key="k")
    with patch("ai_influencer_studio.safe_use.multi_model.requests.post", return_value=response) as mock_post:
        result = client.complete("openrouter::google/gemini:free", "describe", image_path=image)

    assert result.ok is True
    assert result.text == "answer"
    content = mock_post.call_args.kwargs["json"]["messages"][-1]["content"]
    assert content[0]["type"] == "text"
    assert content[1]["type"] == "image_url"
    assert content[1]["image_url"]["url"].startswith("data:image/png;base64,")
    assert mock_post.call_args.kwargs["headers"] == {"Authorization": "Bearer k"}


def test_complete_many_returns_in_input_order() -> None:
    client = MultiModelClient()
    refs = ["ollama::a", "ollama::b", "ollama::c", "ollama::d"]

    def fake_complete(reference: str, prompt: str, system: str | None = None, image_path: Path | str | None = None) -> ModelResult:
        return ModelResult(ref=reference, provider="ollama", model_id=reference.split("::")[1], text=reference, ok=True)

    with patch.object(client, "complete", side_effect=fake_complete):
        results = client.complete_many(refs, "hi")

    assert [result.ref for result in results] == refs


def test_complete_returns_error_result_on_failure() -> None:
    client = MultiModelClient()
    with patch("ai_influencer_studio.safe_use.multi_model.requests.post", side_effect=ConnectionError("down")):
        result = client.complete("ollama::x", "hi")

    assert result.ok is False
    assert result.error == "down"


def test_complete_unsupported_provider() -> None:
    client = MultiModelClient()
    result = client.complete("unknown::x", "hi")
    assert result.ok is False
    assert "Unsupported provider" in (result.error or "")


def test_complete_sanitizes_secret_errors() -> None:
    client = MultiModelClient()
    with patch(
        "ai_influencer_studio.safe_use.multi_model.requests.post",
        side_effect=ConnectionError("boom?token=secret-value"),
    ):
        result = client.complete("ollama::x", "hi")
    assert "secret-value" not in (result.error or "")


def test_ollama_uses_longer_timeout(tmp_path: Path) -> None:
    image = tmp_path / "shot.png"
    image.write_bytes(b"PNGDATA")
    response = MagicMock()
    response.json.return_value = {"message": {"content": "answer"}}
    response.raise_for_status.return_value = None

    client = MultiModelClient(ollama_timeout=999.0)
    with patch("ai_influencer_studio.safe_use.multi_model.requests.post", return_value=response) as mock_post:
        client.complete("ollama::minicpm-v", "describe", image_path=image)

    assert mock_post.call_args.kwargs["timeout"] == 999.0


def test_default_ollama_timeout_exceeds_hosted_timeout() -> None:
    client = MultiModelClient()
    assert client.ollama_timeout > client.timeout
