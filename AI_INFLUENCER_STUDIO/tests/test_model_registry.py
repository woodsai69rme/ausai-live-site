"""Tests for the live Ollama/OpenRouter model registry."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from ai_influencer_studio.model_registry import ModelRecord, ModelRegistry, RegistrySnapshot


def test_fetch_ollama_normalizes_local_models() -> None:
    response = MagicMock()
    response.json.return_value = {
        "models": [
            {
                "name": "qwen2.5-coder:latest",
                "size": 123,
                "digest": "sha256:test",
                "details": {"parameter_size": "7B", "quantization_level": "Q4_K_M"},
            }
        ]
    }
    response.raise_for_status.return_value = None
    with patch("ai_influencer_studio.model_registry.requests.get", return_value=response):
        records = ModelRegistry()._fetch_ollama("2026-08-06T00:00:00+00:00")

    assert records[0].provider == "ollama"
    assert records[0].local is True
    assert records[0].cost_class == "local_free"
    assert records[0].size_bytes == 123
    assert records[0].quantization == "Q4_K_M"


def test_fetch_openrouter_normalizes_price_modalities_and_tools() -> None:
    response = MagicMock()
    response.json.return_value = {
        "data": [
            {
                "id": "example/vision:free",
                "name": "Example Vision",
                "context_length": 128000,
                "architecture": {"input_modalities": ["text", "image"], "output_modalities": ["text"]},
                "pricing": {"prompt": "0", "completion": "0"},
                "supported_parameters": ["tools", "structured_outputs"],
            }
        ]
    }
    response.raise_for_status.return_value = None
    with patch("ai_influencer_studio.model_registry.requests.get", return_value=response) as mock_get:
        records = ModelRegistry(openrouter_api_key="secret")._fetch_openrouter("2026-08-06T00:00:00+00:00")

    assert records[0].provider == "openrouter"
    assert records[0].is_free_hosted is True
    assert records[0].supports("vision") is True
    assert records[0].supports_tools is True
    assert mock_get.call_args.kwargs["headers"] == {"Authorization": "Bearer secret"}


def test_refresh_records_provider_errors_without_fake_models() -> None:
    with patch(
        "ai_influencer_studio.model_registry.requests.get",
        side_effect=ConnectionError("offline"),
    ):
        snapshot = ModelRegistry().refresh()

    assert snapshot.models == []
    assert {error["provider"] for error in snapshot.errors} == {"ollama", "openrouter"}


def test_refresh_records_malformed_provider_payloads() -> None:
    response = MagicMock()
    response.json.return_value = {"wrong": []}
    response.raise_for_status.return_value = None
    with patch("ai_influencer_studio.model_registry.requests.get", return_value=response):
        snapshot = ModelRegistry().refresh()

    assert snapshot.models == []
    assert {error["provider"] for error in snapshot.errors} == {"ollama", "openrouter"}


def test_select_aliases_prefers_local_then_free_hosted() -> None:
    local = ModelRecord(
        model_id="qwen2.5-coder:latest",
        display_name="Qwen coder",
        provider="ollama",
        source="ollama",
        local=True,
        checked_at="now",
    )
    hosted = ModelRecord(
        model_id="cohere/north-mini-code:free",
        display_name="North Mini Code",
        provider="openrouter",
        source="openrouter",
        local=False,
        checked_at="now",
        prompt_price=0,
        completion_price=0,
        cost_class="hosted_free",
    )
    aliases = ModelRegistry.select_aliases([hosted, local])
    assert aliases["coding"][0] == "ollama::qwen2.5-coder:latest"
    assert "openrouter::cohere/north-mini-code:free" in aliases["coding"]


def test_emit_litellm_config_keeps_all_fallbacks(tmp_path: Path) -> None:
    models = [
        ModelRecord(
            model_id=f"coder-{index}",
            display_name=f"Coder {index}",
            provider="ollama",
            source="ollama",
            local=True,
            checked_at="now",
        )
        for index in range(4)
    ]
    snapshot = RegistrySnapshot(checked_at="now", models=models, aliases=ModelRegistry.select_aliases(models))
    output = tmp_path / "all-fallbacks.yaml"
    ModelRegistry.emit_litellm_config(snapshot, output)
    text = output.read_text(encoding="utf-8")
    for index in range(4):
        assert f'"ollama_chat/coder-{index}"' in text
    assert "coding-fallback-3" in text


def test_emit_litellm_config_is_secret_free_and_has_fallback(tmp_path: Path) -> None:
    models = [
        ModelRecord(
            model_id="qwen2.5-coder:latest",
            display_name="Qwen coder",
            provider="ollama",
            source="ollama",
            local=True,
            checked_at="now",
        ),
        ModelRecord(
            model_id="cohere/north-mini-code:free",
            display_name="North Mini Code",
            provider="openrouter",
            source="openrouter",
            local=False,
            checked_at="now",
            prompt_price=0,
            completion_price=0,
            cost_class="hosted_free",
        ),
    ]
    snapshot = RegistrySnapshot(checked_at="now", models=models, aliases=ModelRegistry.select_aliases(models))
    output = tmp_path / "litellm.yaml"
    ModelRegistry.emit_litellm_config(snapshot, output)
    text = output.read_text(encoding="utf-8")

    assert "OPENROUTER_API_KEY" in text
    assert "qwen2.5-coder:latest" in text
    assert "cohere/north-mini-code:free" in text
    assert "ollama_chat/" in text
    assert "openrouter/cohere/north-mini-code:free" in text
    assert "router_settings:" in text
    assert "secret" not in text


def test_provider_error_is_sanitized() -> None:
    response = MagicMock()
    response.raise_for_status.side_effect = requests.RequestException("request failed?token=secret-value")
    with patch("ai_influencer_studio.model_registry.requests.get", return_value=response):
        snapshot = ModelRegistry().refresh(include_openrouter=False)

    assert snapshot.errors[0]["error"] == "request failed [redacted]"
    assert "secret-value" not in json.dumps(snapshot.to_dict())


def test_save_snapshot_is_valid_json(tmp_path: Path) -> None:
    model = ModelRecord(
        model_id="local",
        display_name="Local",
        provider="ollama",
        source="ollama",
        local=True,
        checked_at="now",
    )
    snapshot = RegistrySnapshot(checked_at="now", models=[model], aliases=ModelRegistry.select_aliases([model]))
    path = ModelRegistry.save_snapshot(snapshot, tmp_path / "registry.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["models"][0]["model_id"] == "local"
    assert data["aliases"]["coding"][0] == "ollama::local"


def test_openrouter_free_model_gets_free_tier_limits() -> None:
    response = MagicMock()
    response.json.return_value = {
        "data": [{"id": "example/model:free", "name": "Free", "pricing": {"prompt": "0", "completion": "0"}}]
    }
    response.raise_for_status.return_value = None
    with patch("ai_influencer_studio.model_registry.requests.get", return_value=response):
        records = ModelRegistry()._fetch_openrouter("2026-08-06T00:00:00+00:00")

    assert records[0].free_tier_limits["requests_per_day"] == 50
    assert records[0].free_tier_limits["requests_per_minute"] == 20
    assert records[0].maintenance_status == "active"


def test_openrouter_prompt_caching_flag() -> None:
    response = MagicMock()
    response.json.return_value = {
        "data": [
            {
                "id": "example/cache",
                "name": "Cache",
                "pricing": {"prompt": "0.000001", "completion": "0.000001"},
                "supported_parameters": ["prompt_cache_key"],
            }
        ]
    }
    response.raise_for_status.return_value = None
    with patch("ai_influencer_studio.model_registry.requests.get", return_value=response):
        records = ModelRegistry()._fetch_openrouter("2026-08-06T00:00:00+00:00")

    assert records[0].supports_prompt_caching is True


def test_cost_per_million_returns_none_for_unknown() -> None:
    local = ModelRecord(model_id="x", display_name="X", provider="ollama", source="ollama", local=True, checked_at="now")
    assert local.cost_per_million() == (None, None)

    paid = ModelRecord(
        model_id="p",
        display_name="P",
        provider="openrouter",
        source="openrouter",
        local=False,
        checked_at="now",
        prompt_price=0.000001,
        completion_price=0.000002,
    )
    assert paid.cost_per_million() == (1.0, 2.0)


def test_emit_litellm_config_has_retry_policy(tmp_path: Path) -> None:
    model = ModelRecord(model_id="local", display_name="Local", provider="ollama", source="ollama", local=True, checked_at="now")
    snapshot = RegistrySnapshot(checked_at="now", models=[model], aliases=ModelRegistry.select_aliases([model]))
    output = tmp_path / "litellm.yaml"
    ModelRegistry.emit_litellm_config(snapshot, output)
    text = output.read_text(encoding="utf-8")

    assert "cooldown_time: 30" in text
    assert "allowed_fails: 3" in text
    assert "Retries may bill twice" in text


def test_fetch_extra_provider_normalizes_catalog() -> None:
    response = MagicMock()
    response.json.return_value = {
        "data": [
            {
                "id": "groq/llama-3.3-70b-versatile",
                "name": "Llama 3.3 70B Versatile",
                "pricing": {"prompt": 0, "completion": 0},
                "context_length": 131072,
                "architecture": {"input_modalities": ["text"], "output_modalities": ["text"]},
                "supported_parameters": ["tools"],
            }
        ]
    }
    response.raise_for_status.return_value = None
    config = {
        "name": "groq",
        "base_url": "https://api.groq.com/openai/v1",
        "api_key": "gk-secret",
        "api_key_env": "GROQ_API_KEY",
    }
    with patch("ai_influencer_studio.model_registry.requests.get", return_value=response) as mock_get:
        records = ModelRegistry()._fetch_extra_provider(config, "2026-08-20T00:00:00+00:00")

    assert len(records) == 1
    record = records[0]
    assert record.provider == "groq"
    assert record.local is False
    assert record.cost_class == "hosted_free"
    assert record.supports_tools is True
    assert record.context_length == 131072
    assert record.metadata["api_base"] == "https://api.groq.com/openai/v1"
    assert record.metadata["api_key_env"] == "GROQ_API_KEY"
    assert mock_get.call_args.kwargs["headers"] == {"Authorization": "Bearer gk-secret"}


def test_fetch_extra_provider_requires_data_key() -> None:
    response = MagicMock()
    response.json.return_value = {"object": "list"}
    response.raise_for_status.return_value = None
    config = {"name": "cerebras", "base_url": "https://api.cerebras.ai/v1"}
    with patch("ai_influencer_studio.model_registry.requests.get", return_value=response):
        with pytest.raises(ValueError, match="missing 'data'"):
            ModelRegistry()._fetch_extra_provider(config, "2026-08-20T00:00:00+00:00")
