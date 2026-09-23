"""Local end-to-end smoke coverage with external side effects disabled."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from ai_influencer_studio.config import StudioConfig
from ai_influencer_studio.database import ScheduledPost, StudioDatabase
from ai_influencer_studio.file_indexer import LocalFileIndexer
from ai_influencer_studio.model_registry import ModelRecord, ModelRegistry, RegistrySnapshot
from ai_influencer_studio.music_video_researcher import MusicVideoResearchEngine
from ai_influencer_studio.safe_use.engine import SafeUseEngine
from ai_influencer_studio.safe_use.models import ActionIntent, ActionTarget
from ai_influencer_studio.safe_use.policy import SafePolicy


def test_local_end_to_end_smoke(tmp_path: Path) -> None:
    config = StudioConfig(data_dir=tmp_path / "data", media_dir=tmp_path / "media")
    config.save(tmp_path / "config.json")
    assert StudioConfig.from_file(tmp_path / "config.json").data_dir == config.data_dir

    model = ModelRecord(
        model_id="local/demo",
        display_name="Local Demo",
        provider="ollama",
        source="ollama",
        local=True,
        checked_at="now",
    )
    snapshot_path = config.data_dir / "model_registry.json"
    ModelRegistry.save_snapshot(
        RegistrySnapshot(
            checked_at="now",
            models=[model],
            aliases={"general": ["ollama::local/demo"]},
            verification_status="verified",
            verified=True,
            fresh_until=(datetime.now(UTC) + timedelta(hours=1)).isoformat(),
        ),
        snapshot_path,
    )
    report_path = config.data_dir / "model_registry_report.md"
    ModelRegistry.export_catalog_markdown(ModelRegistry.load_snapshot(snapshot_path), report_path)
    assert report_path.exists()

    source = tmp_path / "incoming"
    source.mkdir()
    (source / "notes.txt").write_text("local smoke", encoding="utf-8")
    indexer = LocalFileIndexer(config.data_dir / "file_indexer.sqlite")
    result = indexer.scan(source, tmp_path / "organized")
    assert result["pending"] == 1
    assert (source / "notes.txt").exists()

    engine = SafeUseEngine(
        SafePolicy(allowed_domains={"example.com"}),
        audit_path=config.data_dir / "safe-use-audit.jsonl",
    )
    proposal = engine.propose(ActionIntent(
        target=ActionTarget.BROWSER,
        action="navigate",
        parameters={"url": "https://example.com"},
        reason="smoke test",
    ))
    assert proposal.intent is not None
    engine.close()

    music = MusicVideoResearchEngine(data_dir=config.data_dir)
    plan = music.create_song_plan("Smoke Song", str(source / "song.mp3"))
    assert len(plan.scenes) == 8

    database = StudioDatabase(config.data_dir / "studio.db")
    post_id = database.add_scheduled_post(ScheduledPost(
        platform="test",
        content="smoke",
        scheduled_at=datetime.now(),
    ))
    assert post_id > 0
    assert "Model Registry Snapshot Report" in report_path.read_text(encoding="utf-8")
