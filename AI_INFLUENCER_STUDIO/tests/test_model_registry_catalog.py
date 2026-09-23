"""Focused tests for verified daily catalog persistence."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from ai_influencer_studio.model_registry import ModelRecord, ModelRegistry, RegistrySnapshot, _normalize_availability


def _openrouter_response(items: list[dict]) -> MagicMock:
    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"data": items}
    return response


def test_probe_health_updates_health_only(tmp_path: Path) -> None:
    model = ModelRecord(
        model_id="local/demo", display_name="Demo", provider="ollama", source="ollama",
        local=True, checked_at="now", availability_status="listed",
    )
    snapshot = RegistrySnapshot(checked_at="now", models=[model], aliases={"general": ["ollama::local/demo"]})
    response = MagicMock()
    response.raise_for_status.return_value = None
    with patch("ai_influencer_studio.model_registry.requests.post", return_value=response):
        probed = ModelRegistry().probe_health(snapshot, model_refs={"ollama::local/demo"})
    assert probed.models[0].health_status == "healthy"
    assert probed.models[0].availability_status == "listed"
    assert probed.aliases == snapshot.aliases


def test_probe_health_records_failure_without_changing_catalog() -> None:
    model = ModelRecord(
        model_id="local/demo", display_name="Demo", provider="ollama", source="ollama",
        local=True, checked_at="now", availability_status="listed",
    )
    snapshot = RegistrySnapshot(checked_at="now", models=[model])
    with patch("ai_influencer_studio.model_registry.requests.post", side_effect=requests.ConnectionError("offline")):
        probed = ModelRegistry().probe_health(snapshot)
    assert probed.models[0].health_status == "unhealthy"
    assert probed.models[0].availability_status == "listed"


def test_probe_health_uses_show_endpoint_and_bypasses_proxy() -> None:
    model = ModelRecord(
        model_id="local/demo", display_name="Demo", provider="ollama", source="ollama",
        local=True, checked_at="now", availability_status="listed",
    )
    snapshot = RegistrySnapshot(checked_at="now", models=[model])
    response = MagicMock()
    response.raise_for_status.return_value = None
    with patch("ai_influencer_studio.model_registry.requests.post", return_value=response) as mock_post:
        ModelRegistry().probe_health(snapshot, model_refs={"ollama::local/demo"})
    call = mock_post.call_args
    assert call.args[0].endswith("/api/show")
    assert call.kwargs["json"] == {"model": "local/demo"}
    assert call.kwargs["proxies"] == {"http": None, "https": None}


def test_normalize_availability_handles_naive_expiration_dates() -> None:
    # OpenRouter can return a naive (no timezone) expiration_date; comparing it
    # against an aware now must not raise TypeError.
    assert _normalize_availability({"expiration_date": "2000-01-01T00:00:00"}) == "expired"
    assert _normalize_availability({"expiration_date": "2999-01-01T00:00:00"}) == "listed"
    assert _normalize_availability({"expiration_date": "2999-01-01T00:00:00Z"}) == "listed"
    assert _normalize_availability({"is_active": False}) == "unavailable"
    assert _normalize_availability({}) == "listed"


def test_ollama_catalog_includes_source_provenance() -> None:
    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"models": [{"name": "qwen2.5:latest", "size": 10, "details": {}}]}
    with patch("ai_influencer_studio.model_registry.requests.get", return_value=response):
        record = ModelRegistry()._fetch_ollama("2026-08-06T00:00:00+00:00")[0]
    assert record.field_sources["model_id"] == "ollama-tags"
    assert record.field_sources["modalities"] == "unknown"


def test_openrouter_catalog_keeps_license_availability_and_provenance() -> None:
    item = {
        "id": "example/model",
        "name": "Example",
        "context_length": 32768,
        "architecture": {"input_modalities": ["text", "image"], "output_modalities": ["text"]},
        "pricing": {"prompt": "0.000001", "completion": "0.000002"},
        "supported_parameters": ["tools"],
        "license": "apache-2.0",
    }
    with patch("ai_influencer_studio.model_registry.requests.get", return_value=_openrouter_response([item])):
        record = ModelRegistry()._fetch_openrouter("2026-08-06T00:00:00+00:00")[0]
    assert record.license == "apache-2.0"
    assert record.availability_status == "listed"
    assert record.supported_parameters == ["tools"]
    assert record.field_sources["pricing"] == "openrouter-models"
    assert record.is_available is True


def test_daily_refresh_preserves_last_known_good_on_provider_failure(tmp_path: Path) -> None:
    path = tmp_path / "catalog.json"
    model = ModelRecord(
        model_id="example/model",
        display_name="Example",
        provider="openrouter",
        source="openrouter",
        local=False,
        checked_at="old",
        prompt_price=0,
        completion_price=0,
        cost_class="hosted_free",
        availability_status="listed",
    )
    previous = RegistrySnapshot(
        checked_at=(datetime.now(UTC) - timedelta(days=2)).isoformat(),
        models=[model],
        aliases={"general": ["openrouter::example/model"]},
        verification_status="verified",
        verified=True,
        fresh_until=(datetime.now(UTC) - timedelta(days=1)).isoformat(),
    )
    ModelRegistry.save_snapshot(previous, path)
    with patch("ai_influencer_studio.model_registry.requests.get", side_effect=requests.ConnectionError("offline")):
        snapshot = ModelRegistry().refresh_daily(path, include_ollama=False, include_openrouter=True)
    assert snapshot.verification_status == "degraded"
    assert snapshot.provider_status["openrouter"] == "stale"
    assert snapshot.models[0].metadata["stale"] is True
    assert snapshot.models[0].availability_status == "stale"


def test_daily_refresh_skips_fresh_snapshot(tmp_path: Path) -> None:
    path = tmp_path / "catalog.json"
    snapshot = RegistrySnapshot(
        checked_at=datetime.now(UTC).isoformat(),
        models=[],
        verification_status="verified",
        verified=True,
        fresh_until=(datetime.now(UTC) + timedelta(hours=12)).isoformat(),
    )
    ModelRegistry.save_snapshot(snapshot, path)
    with patch("ai_influencer_studio.model_registry.requests.get") as mock_get:
        result = ModelRegistry().refresh_daily(path, include_ollama=False, include_openrouter=True)
    mock_get.assert_not_called()
    assert result.checked_at == snapshot.checked_at


def test_stale_and_expired_models_are_excluded_from_aliases() -> None:
    model = ModelRecord(
        model_id="stale/model",
        display_name="Stale",
        provider="openrouter",
        source="openrouter",
        local=False,
        checked_at="now",
        prompt_price=0,
        completion_price=0,
        cost_class="hosted_free",
        availability_status="stale",
    )
    assert "openrouter::stale/model" not in json.dumps(ModelRegistry.select_aliases([model]))


def test_disappeared_model_is_unlisted_and_excluded_from_aliases(tmp_path: Path) -> None:
    path = tmp_path / "catalog.json"
    old_model = ModelRecord(
        model_id="old/model",
        display_name="Old",
        provider="openrouter",
        source="openrouter",
        local=False,
        checked_at="old",
        prompt_price=0,
        completion_price=0,
        cost_class="hosted_free",
        availability_status="listed",
    )
    previous = RegistrySnapshot(checked_at="old", models=[old_model], verification_status="verified", verified=True)
    ModelRegistry.save_snapshot(previous, path)
    current_item = {"id": "new/model", "name": "New", "pricing": {"prompt": "0", "completion": "0"}}
    with patch("ai_influencer_studio.model_registry.requests.get", return_value=_openrouter_response([current_item])):
        snapshot = ModelRegistry().refresh(previous_snapshot=previous, include_ollama=False, include_openrouter=True)
    old = next(model for model in snapshot.models if model.model_id == "old/model")
    assert old.availability_status == "unlisted"
    assert "openrouter::old/model" not in json.dumps(snapshot.aliases)
    assert "openrouter::new/model" in json.dumps(snapshot.aliases)


def test_export_catalog_markdown_is_offline_and_secret_free(tmp_path: Path) -> None:
    model = ModelRecord(
        model_id="example/model",
        display_name="Example | Model",
        provider="openrouter",
        source="openrouter",
        local=False,
        checked_at="now",
        prompt_price=0,
        completion_price=0,
        cost_class="hosted_free",
        availability_status="listed",
        license="apache-2.0",
        supports_tools=True,
    )
    snapshot = RegistrySnapshot(
        checked_at="now",
        models=[model],
        aliases={"general": ["openrouter::example/model"]},
        provider_status={"openrouter": "verified"},
        source_urls={"openrouter": "https://openrouter.ai/api/v1/models"},
        verification_status="verified",
        verified=True,
    )
    output = tmp_path / "report.md"
    ModelRegistry.export_catalog_markdown(snapshot, output)
    text = output.read_text(encoding="utf-8")
    assert "Model Registry Snapshot Report" in text
    assert "Example \\| Model" in text
    assert "`" not in text.split("## Models", 1)[1].split("## Routing aliases", 1)[0]
    assert "https://openrouter.ai/api/v1/models" in text
    assert "OPENROUTER_API_KEY" not in text


def test_refresh_source_urls_include_only_enabled_providers() -> None:
    with patch("ai_influencer_studio.model_registry.requests.get", return_value=_openrouter_response([{"id": "new/model"}])):
        snapshot = ModelRegistry().refresh(include_ollama=False, include_openrouter=True)
    assert "openrouter" in snapshot.source_urls
    assert "ollama" not in snapshot.source_urls


def test_extra_provider_preserves_endpoint_and_secret_free_route(tmp_path: Path) -> None:
    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "data": [
            {
                "id": "demo/model",
                "name": "Demo",
                "pricing": {"prompt": "0", "completion": "0"},
            }
        ]
    }
    config = {
        "name": "groq",
        "base_url": "https://api.groq.com/openai/v1",
        "models_path": "/models",
        "api_key": "secret",
        "api_key_env": "GROQ_API_KEY",
        "enabled": True,
    }
    with patch("ai_influencer_studio.model_registry.requests.get", return_value=response):
        snapshot = ModelRegistry().refresh(
            include_ollama=False,
            include_openrouter=False,
            extra_providers=[config],
        )

    model = snapshot.models[0]
    assert model.provider == "groq"
    assert model.metadata["api_base"] == "https://api.groq.com/openai/v1"
    assert model.metadata["api_key_env"] == "GROQ_API_KEY"
    output = tmp_path / "litellm.yaml"
    ModelRegistry.emit_litellm_config(snapshot, output)
    text = output.read_text(encoding="utf-8")
    assert "openai/demo/model" in text
    assert "api.groq.com/openai/v1" in text
    assert "os.environ/GROQ_API_KEY" in text
    assert "secret" not in text


def test_extra_provider_health_probe_uses_saved_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    model = ModelRecord(
        model_id="demo/model",
        display_name="Demo",
        provider="groq",
        source="groq",
        local=False,
        checked_at="now",
        metadata={"api_base": "https://api.groq.com/openai/v1", "api_key_env": "GROQ_API_KEY"},
    )
    snapshot = RegistrySnapshot(checked_at="now", models=[model])
    response = MagicMock()
    response.raise_for_status.return_value = None
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    with patch("ai_influencer_studio.model_registry.requests.post", return_value=response) as mock_post:
        ModelRegistry().probe_health(snapshot, model_refs={"groq::demo/model"}, include_hosted=True)
    assert mock_post.call_args.args[0] == "https://api.groq.com/openai/v1/chat/completions"
    assert mock_post.call_args.kwargs["headers"] == {"Authorization": "Bearer test-key"}


def test_skipped_provider_is_not_marked_unlisted() -> None:
    old = ModelRecord(
        model_id="local/model",
        display_name="Local",
        provider="ollama",
        source="ollama",
        local=True,
        checked_at="old",
        availability_status="listed",
    )
    previous = RegistrySnapshot(checked_at="old", models=[old], verification_status="verified", verified=True)
    with patch("ai_influencer_studio.model_registry.requests.get", return_value=_openrouter_response([{"id": "new/model"}])):
        snapshot = ModelRegistry().refresh(previous_snapshot=previous, include_ollama=False, include_openrouter=True)
    assert snapshot.models[0].provider == "openrouter"
    assert not any(model.availability_status == "unlisted" for model in snapshot.models)
