"""Focused CLI tests for model-registry documentation export."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from ai_influencer_studio.cli import main
from ai_influencer_studio.model_registry import ModelRecord, ModelRegistry, RegistrySnapshot


def test_export_docs_cli_writes_report(tmp_path: Path, monkeypatch) -> None:
    snapshot_path = tmp_path / "snapshot.json"
    report_path = tmp_path / "report.md"
    model = ModelRecord(
        model_id="demo/model",
        display_name="Demo",
        provider="openrouter",
        source="openrouter",
        local=False,
        checked_at=datetime.now(UTC).isoformat(),
        prompt_price=0,
        completion_price=0,
        cost_class="hosted_free",
    )
    ModelRegistry.save_snapshot(
        RegistrySnapshot(
            checked_at=datetime.now(UTC).isoformat(),
            models=[model],
            aliases={"general": ["openrouter::demo/model"]},
            provider_status={"openrouter": "verified"},
            source_urls={"openrouter": "https://openrouter.ai/api/v1/models"},
            verification_status="verified",
            verified=True,
        ),
        snapshot_path,
    )
    monkeypatch.setenv("AISTUDIO_API_KEY", "")
    assert main(["model-registry", "export-docs", "--snapshot", str(snapshot_path), "--output", str(report_path)]) == 0
    text = report_path.read_text(encoding="utf-8")
    assert "Demo" in text
    assert "openrouter.ai/api/v1/models" in text


def test_probe_cli_wires_snapshot_and_preserves_catalog_fields(tmp_path: Path, capsys) -> None:
    snapshot_path = tmp_path / "snapshot.json"
    model = MagicMock(
        provider="ollama",
        model_id="demo",
        health_status="healthy",
        health_checked_at="now",
        health_latency_ms=2.5,
        health_error=None,
    )
    probed = MagicMock(models=[model])
    with patch("ai_influencer_studio.cli.StudioConfig") as config_cls, patch(
        "ai_influencer_studio.cli.ModelRegistry.load_snapshot", return_value=MagicMock()
    ) as load_snapshot, patch(
        "ai_influencer_studio.cli.ModelRegistry.save_snapshot"
    ) as save_snapshot, patch("ai_influencer_studio.cli.ModelRegistry.probe_health", return_value=probed) as probe:
        config_cls.from_file.return_value.data_dir = tmp_path
        assert main(["model-registry", "probe", "--snapshot", str(snapshot_path), "--model-ref", "ollama::demo"]) == 0

    load_snapshot.assert_called_once_with(snapshot_path)
    probe.assert_called_once()
    save_snapshot.assert_called_once_with(probed, snapshot_path)
    assert "catalog_availability_unchanged" in capsys.readouterr().out


def test_health_cli_is_local_and_reports_snapshot_state(tmp_path: Path, capsys) -> None:
    snapshot = MagicMock(
        fresh_until="later",
        verification_status="verified",
        provider_status={"ollama": "verified"},
        models=[MagicMock(health_status="healthy"), MagicMock(health_status="unknown")],
    )
    with patch("ai_influencer_studio.cli.StudioConfig") as config_cls, patch(
        "ai_influencer_studio.cli.ModelRegistry.load_snapshot", return_value=snapshot
    ) as load_snapshot, patch("ai_influencer_studio.cli._snapshot_is_fresh", return_value=True):
        config_cls.from_file.return_value.data_dir = tmp_path
        snapshot_path = tmp_path / "model_registry.json"
        snapshot_path.write_text("{}", encoding="utf-8")
        assert main(["health"]) == 0

    load_snapshot.assert_called_once()
    output = capsys.readouterr().out
    assert '"catalog_fresh": true' in output
    assert '"healthy_models": 1' in output


def test_doctor_cli_checks_all_required_runtime_dependencies(capsys) -> None:
    with patch("ai_influencer_studio.cli.importlib.metadata.version", return_value="1.0"), patch(
        "ai_influencer_studio.cli.importlib.import_module", return_value=MagicMock()
    ):
        assert main(["doctor"]) == 0
    report = __import__("json").loads(capsys.readouterr().out)
    assert {
        "fastapi", "uvicorn", "jinja2", "pydantic", "requests", "python-multipart", "schedule",
        "Pillow", "openai", "librosa", "mutagen",
    } == set(report["required"])
    assert {"playwright", "pypdf", "python-docx", "uiautomation", "mcp"} == set(report["optional"])
    assert "mutagen" not in report["optional"]
    assert "Pillow" not in report["optional"]


def test_style_bible_template_cli_writes_file(tmp_path: Path, capsys) -> None:
    output = tmp_path / "style-bible.json"
    assert main(["music-video", "style-bible-template", "--output", str(output)]) == 0
    assert output.exists()
    assert "Style bible template written to:" in capsys.readouterr().out
