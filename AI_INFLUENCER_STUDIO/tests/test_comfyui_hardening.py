"""Tests for the ComfyUI execution hardening module (E2)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from ai_influencer_studio.comfyui_hardening import (
    ComfyUIRuntimeCheck,
    validate_workflow,
    vram_budget_report,
)


def _api_workflow() -> dict:
    """A minimal valid API-format workflow: load checkpoint, sample, save."""
    return {
        "nodes": [
            {"id": 4, "class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "model.safetensors"}},
            {"id": 8, "class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": "a cat"}},
            {"id": 9, "class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": "blurry"}},
            {"id": 10, "class_type": "EmptyLatentImage", "inputs": {"width": 896, "height": 512, "batch_size": 1}},
            {
                "id": 11,
                "class_type": "KSampler",
                "inputs": {
                    "model": ["4", 0],
                    "positive": ["8", 0],
                    "negative": ["9", 0],
                    "latent_image": ["10", 0],
                },
            },
            {"id": 12, "class_type": "VAEDecode", "inputs": {"samples": ["11", 0], "vae": ["4", 2]}},
            {"id": 13, "class_type": "SaveImage", "inputs": {"images": ["12", 0]}},
        ]
    }


def test_validate_workflow_accepts_valid_api_format() -> None:
    result = validate_workflow(_api_workflow())
    assert result["valid"] is True
    assert result["errors"] == []
    # Without object_info the required-input check is skipped, so expect a warning.
    assert any("object_info" in warning for warning in result["warnings"])


def test_validate_workflow_rejects_non_object() -> None:
    result = validate_workflow("nope")  # type: ignore[arg-type]
    assert result["valid"] is False
    assert "JSON object" in result["errors"][0]


def test_validate_workflow_rejects_missing_and_duplicate_ids() -> None:
    workflow = {
        "nodes": [
            {"type": "KSampler", "inputs": {}},
            {"id": 2, "class_type": "KSampler", "inputs": {}},
            {"id": 2, "class_type": "VAEDecode", "inputs": {}},
        ]
    }
    result = validate_workflow(workflow)
    assert result["valid"] is False
    messages = " ".join(result["errors"])
    assert "missing an 'id'" in messages
    assert "duplicate node id: 2" in messages


def test_validate_workflow_catches_dangling_api_link() -> None:
    workflow = {
        "nodes": [
            {"id": 1, "class_type": "KSampler", "inputs": {"model": ["99", 0]}},
        ]
    }
    result = validate_workflow(workflow)
    assert result["valid"] is False
    assert any("references missing node 99" in error for error in result["errors"])


def test_validate_workflow_catches_dangling_legacy_link() -> None:
    workflow = {
        "nodes": [
            {"id": 1, "type": "KSampler", "inputs": []},
            {"id": 2, "type": "SaveImage", "inputs": []},
        ],
        "links": [[0, 1, 0, 42, 0, 0]],
    }
    result = validate_workflow(workflow)
    assert result["valid"] is False
    assert any("missing to node 42" in error for error in result["errors"])


def test_validate_workflow_checks_required_inputs_with_catalog() -> None:
    workflow = {
        "nodes": [
            {"id": 1, "class_type": "KSampler", "inputs": {"positive": ["2", 0]}},
        ]
    }
    object_info = {
        "KSampler": {
            "input": {
                "required": {"model": {}, "positive": {}, "negative": {}, "latent_image": {}}
            }
        }
    }
    result = validate_workflow(workflow, object_info=object_info)
    assert result["valid"] is False
    messages = " ".join(result["errors"])
    assert "missing required input 'model'" in messages
    assert "missing required input 'negative'" in messages


def test_vram_budget_report_verdicts() -> None:
    workflows = [
        # Single KSampler: 2.5 base + 1.5 = 4.0 GB on 8GB -> green.
        {"nodes": [{"class_type": "KSampler"}]},
        # Checkpoint + two samplers: 2.5 + 4.0 + 3.0 = 9.5 GB on 8GB -> red.
        {
            "nodes": [
                {"class_type": "CheckpointLoaderSimple"},
                {"class_type": "KSampler"},
                {"class_type": "KSampler"},
            ]
        },
    ]
    report = vram_budget_report({"vram_total_gb": 8.0}, workflows)
    assert report["verdict"] == "red"
    assert report["estimates"][0]["verdict"] == "green"
    assert report["estimates"][1]["verdict"] == "red"


def test_vram_budget_report_unknown_without_vram() -> None:
    report = vram_budget_report({"vram_total_gb": None}, [])
    assert report["verdict"] == "unknown"


def test_vram_budget_report_resolution_scaling() -> None:
    workflow = {
        "nodes": [
            {
                "class_type": "KSampler",
                "inputs": {"width": 2048, "height": 2048},
            }
        ]
    }
    report = vram_budget_report({"vram_total_gb": 8.0}, [workflow])
    estimate = report["estimates"][0]
    # 2048x2048 is 4x the 1024x1024 baseline -> scaled estimate well above the plain sum.
    assert estimate["estimated_gb"] > 6.0


@patch("ai_influencer_studio.comfyui_hardening.requests.get")
def test_runtime_check_server_status(mock_get: MagicMock) -> None:
    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "system": {"name": "Windows", "torch_version": "2.4.0", "python_version": "3.12"},
        "devices": [{"name": "RTX 4060", "vram_total": 8589934592, "vram_free": 2147483648}],
    }
    mock_get.return_value = response

    check = ComfyUIRuntimeCheck.__new__(ComfyUIRuntimeCheck)
    check.config = None
    check.url = "http://localhost:8188"
    check.timeout = 10.0
    status = check.server_status()

    assert status["online"] is True
    assert status["device"] == "RTX 4060"
    assert status["vram_total_gb"] == 8.6
    assert status["vram_free_gb"] == 2.1
    assert status["torch_version"] == "2.4.0"
    mock_get.assert_called_once()


@patch("ai_influencer_studio.comfyui_hardening.requests.get")
def test_runtime_check_surfaces_connection_failure(mock_get: MagicMock) -> None:
    mock_get.side_effect = requests.ConnectionError("connection refused")

    check = ComfyUIRuntimeCheck.__new__(ComfyUIRuntimeCheck)
    check.config = None
    check.url = "http://localhost:8188"
    check.timeout = 10.0

    with pytest.raises(requests.RequestException):
        check.server_status()


@patch("ai_influencer_studio.comfyui_hardening.requests.get")
def test_runtime_check_check_degrades_gracefully_without_catalog(mock_get: MagicMock) -> None:
    first = MagicMock()
    first.raise_for_status.return_value = None
    first.json.return_value = {"system": {"name": "Windows"}, "devices": []}
    second = MagicMock()
    second.raise_for_status.side_effect = requests.ConnectionError("catalog down")

    mock_get.side_effect = [first, second]

    check = ComfyUIRuntimeCheck.__new__(ComfyUIRuntimeCheck)
    check.config = None
    check.url = "http://localhost:8188"
    check.timeout = 10.0

    result = check.check()
    assert result["online"] is True
    assert result["catalog_available"] is False
    assert "catalog down" in result["catalog_error"]
