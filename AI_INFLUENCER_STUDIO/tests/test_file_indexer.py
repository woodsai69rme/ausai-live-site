"""Tests for the local multimodal file indexer."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from ai_influencer_studio.file_indexer import (
    IndexerError,
    LocalFileIndexer,
    UnsafePathError,
    _extract_keyframe,
    extract_metadata,
    ocr_hook,
    vision_caption_hook,
)


def test_analysis_hooks_are_additive_and_errors_are_recorded(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    path = source / "notes.txt"
    path.write_text("hook me", encoding="utf-8")

    def hook(file_path: Path, modality: str, metadata: dict) -> dict:
        assert file_path == path
        assert modality == "document"
        return {"label": "smoke"}

    def broken_hook(file_path: Path, modality: str, metadata: dict) -> dict:
        raise RuntimeError("optional failure")

    indexer = LocalFileIndexer(tmp_path / "index.sqlite", analysis_hooks=[hook, broken_hook])
    result = indexer.scan(source, tmp_path / "target")
    metadata = result["records"][0]["metadata"]
    assert metadata["analysis_hooks"]["label"] == "smoke"
    assert metadata["analysis_hook_errors"] == ["RuntimeError"]
    assert path.exists()


def test_scan_indexes_modalities_without_moving_files(tmp_path: Path) -> None:
    source = tmp_path / "incoming"
    target = tmp_path / "organized"
    source.mkdir()
    (source / "notes.txt").write_text("local notes", encoding="utf-8")
    (source / "photo.png").write_bytes(b"not-a-real-image")
    (source / "track.mp3").write_bytes(b"audio bytes")
    (source / "clip.mp4").write_bytes(b"video bytes")
    (source / "ignore.bin").write_bytes(b"ignored")

    indexer = LocalFileIndexer(tmp_path / "index.sqlite")
    result = indexer.scan(source, target)

    assert result["scanned"] == 4
    assert result["pending"] == 4
    assert (source / "notes.txt").exists()
    assert not target.exists() or not any(target.rglob("*"))
    records = indexer.list_queue()
    assert {record.modality for record in records} == {"document", "image", "music", "video"}


def test_scan_is_idempotent_for_same_source_hash(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "one.txt").write_text("same", encoding="utf-8")
    indexer = LocalFileIndexer(tmp_path / "index.sqlite")
    indexer.scan(source, tmp_path / "target")
    indexer.scan(source, tmp_path / "target")
    assert len(indexer.list_queue()) == 1


def test_duplicate_hash_is_queued_as_duplicate(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.txt").write_text("same", encoding="utf-8")
    (source / "b.txt").write_text("same", encoding="utf-8")
    indexer = LocalFileIndexer(tmp_path / "index.sqlite")
    indexer.scan(source, tmp_path / "target")
    assert [record.status for record in indexer.list_queue()].count("DUPLICATE") == 1


def test_review_transitions_do_not_touch_files(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    file_path = source / "one.md"
    file_path.write_text("review me", encoding="utf-8")
    indexer = LocalFileIndexer(tmp_path / "index.sqlite")
    indexer.scan(source, tmp_path / "target")
    record = indexer.list_queue()[0]
    assert indexer.approve([record.id]) == 1
    assert file_path.exists()
    assert indexer.list_queue()[0].status == "APPROVED"
    assert indexer.reject([record.id]) == 0


def test_apply_requires_confirmation_and_verifies_copy(tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    file_path = source / "one.md"
    file_path.write_text("apply me", encoding="utf-8")
    indexer = LocalFileIndexer(tmp_path / "index.sqlite")
    indexer.scan(source, target)
    record = indexer.list_queue()[0]
    indexer.approve([record.id])
    with pytest.raises(IndexerError):
        indexer.apply(confirm=False)
    result = indexer.apply(confirm=True)
    assert result["count"] == 1
    assert not file_path.exists()
    applied = indexer.list_queue()[0]
    assert applied.status == "APPLIED"
    assert Path(applied.target_path).read_text(encoding="utf-8") == "apply me"


def test_rescan_supersedes_changed_pending_record(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    file_path = source / "one.txt"
    file_path.write_text("old", encoding="utf-8")
    indexer = LocalFileIndexer(tmp_path / "index.sqlite")
    indexer.scan(source, tmp_path / "target")
    file_path.write_text("new", encoding="utf-8")
    indexer.scan(source, tmp_path / "target")
    statuses = [record.status for record in indexer.list_queue()]
    assert "SUPERSEDED" in statuses
    assert statuses.count("PENDING") == 1


def test_apply_rejects_tampered_database_path(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    file_path = source / "one.txt"
    file_path.write_text("safe", encoding="utf-8")
    indexer = LocalFileIndexer(tmp_path / "index.sqlite")
    indexer.scan(source, tmp_path / "target")
    record = indexer.list_queue()[0]
    indexer.approve([record.id])
    with indexer._connect() as connection:
        connection.execute("UPDATE indexed_files SET source_path=? WHERE id=?", (str(tmp_path / "../outside.txt"), record.id))
    result = indexer.apply(confirm=True)
    assert result["failed"]
    assert file_path.exists()


def test_safe_child_rejects_escape(tmp_path: Path) -> None:
    with pytest.raises(UnsafePathError):
        LocalFileIndexer._safe_child(tmp_path.parent / "escape.txt", tmp_path)


def test_metadata_extraction_reports_optional_parser(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")
    metadata = extract_metadata(path, "document")
    assert metadata["text_preview"] == "hello"
    assert json.dumps(metadata)


def test_ocr_hook_ignores_non_image_modalities(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("x", encoding="utf-8")
    assert ocr_hook()(path, "music", {}) == {}


def test_ocr_hook_extracts_text(tmp_path: Path) -> None:
    import sys

    path = tmp_path / "photo.png"
    path.write_bytes(b"fake")

    fake_image = MagicMock()
    fake_pytesseract = MagicMock()
    fake_pytesseract.image_to_string.return_value = " OCR TEXT "

    with patch.dict(sys.modules, {"pytesseract": fake_pytesseract}):
        with patch("PIL.Image.open") as mock_open:
            mock_open.return_value.__enter__.return_value = fake_image
            result = ocr_hook()(path, "image", {})

    assert result["ocr_text"] == "OCR TEXT"
    assert result["ocr_parser"] == "pytesseract"
    fake_pytesseract.image_to_string.assert_called_once()


def test_ocr_hook_records_unavailable_when_import_missing(tmp_path: Path) -> None:
    path = tmp_path / "photo.png"
    path.write_bytes(b"fake")

    real_import = __import__

    def fake_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "pytesseract":
            raise ImportError("no pytesseract")
        return real_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=fake_import):
        result = ocr_hook()(path, "image", {})

    assert result["ocr_parser"] == "unavailable:pytesseract"


def test_extract_keyframe_returns_none_without_ffmpeg(tmp_path: Path) -> None:
    with patch("ai_influencer_studio.file_indexer.shutil.which", return_value=None):
        assert _extract_keyframe(tmp_path / "clip.mp4") is None


def test_vision_caption_hook_captions_image(tmp_path: Path) -> None:
    path = tmp_path / "photo.png"
    path.write_bytes(b"fake")

    class FakeClient:
        def __init__(self) -> None:
            self.calls: list[tuple[str, str, Path | None]] = []

        def complete(self, reference: str, prompt: str, image_path: Path | None = None) -> SimpleNamespace:
            self.calls.append((reference, prompt, image_path))
            return SimpleNamespace(ok=True, text="a red car")

    client = FakeClient()
    result = vision_caption_hook(client, "ollama::minicpm-v")(path, "image", {})
    assert result["caption"] == "a red car"
    assert client.calls[0][2] == path


def test_vision_caption_hook_ignores_non_visual_modalities(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("x", encoding="utf-8")

    class FakeClient:
        def complete(self, *args: object, **kwargs: object) -> object:
            raise AssertionError("should not be called")

    assert vision_caption_hook(FakeClient(), "x::y")(path, "document", {}) == {}


def test_vision_caption_hook_records_client_error(tmp_path: Path) -> None:
    path = tmp_path / "photo.png"
    path.write_bytes(b"fake")

    class FakeClient:
        def complete(self, *args: object, **kwargs: object) -> SimpleNamespace:
            return SimpleNamespace(ok=False, error="timeout")

    result = vision_caption_hook(FakeClient(), "x::y")(path, "image", {})
    assert result["caption_error"] == "timeout"


def test_vision_caption_hook_captions_video_keyframe_and_cleans_up(tmp_path: Path) -> None:
    path = tmp_path / "clip.mp4"
    path.write_bytes(b"fake")
    frame = tmp_path / "frame.png"
    frame.write_bytes(b"frame")

    class FakeClient:
        def __init__(self) -> None:
            self.calls: list[Path | None] = []

        def complete(self, reference: str, prompt: str, image_path: Path | None = None) -> SimpleNamespace:
            self.calls.append(image_path)
            return SimpleNamespace(ok=True, text="a dance scene")

    client = FakeClient()
    with patch("ai_influencer_studio.file_indexer._extract_keyframe", return_value=frame):
        result = vision_caption_hook(client, "x::y")(path, "video", {})

    assert result["caption"] == "a dance scene"
    assert client.calls[0] == frame
    assert not frame.exists()  # temp keyframe cleaned up
