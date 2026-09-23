"""Tests for ai_influencer_studio.gdrive_uploader."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ai_influencer_studio.gdrive_uploader import (
    GDriveUploader,
    UploadState,
    is_eligible,
    is_screenshot_name,
    scan_source_dirs,
)


def _make_file(path: Path, size: int, mtime: datetime | None = None) -> Path:
    path.write_bytes(b"x" * size)
    if mtime is not None:
        import os

        os.utime(path, (mtime.timestamp(), mtime.timestamp()))
    return path


def test_is_screenshot_name() -> None:
    assert is_screenshot_name("Screenshot 2026-08-19 123456.png")
    assert is_screenshot_name("screenshot_ui.png")
    assert is_screenshot_name("screen-shot-1.png")
    assert not is_screenshot_name("chloe-hero.jpg")
    assert not is_screenshot_name("clip_001.mp4")


def test_is_eligible_filters(tmp_path: Path) -> None:
    good = _make_file(tmp_path / "hero.png", 300_000)
    ok, reason = is_eligible(good)
    assert ok and reason == ""

    small = _make_file(tmp_path / "tiny.png", 100_000)
    ok, reason = is_eligible(small)
    assert not ok and "250 KB" in reason

    big = _make_file(tmp_path / "big.mp4", 16 * 1024 * 1024)
    ok, reason = is_eligible(big)
    assert not ok and "15 MB" in reason

    svg = _make_file(tmp_path / "logo.svg", 300_000)
    ok, reason = is_eligible(svg)
    assert not ok and "banned" in reason

    txt = _make_file(tmp_path / "notes.txt", 300_000)
    ok, reason = is_eligible(txt)
    assert not ok and "unsupported" in reason


def test_is_eligible_skips_stale_screenshots(tmp_path: Path) -> None:
    now = datetime.now(UTC)
    old_screenshot = _make_file(
        tmp_path / "Screenshot 2026-08-01 100000.png",
        300_000,
        now - timedelta(days=10),
    )
    ok, reason = is_eligible(old_screenshot, now=now)
    assert not ok and "screenshot older" in reason

    fresh_screenshot = _make_file(
        tmp_path / "Screenshot 2026-08-19 100000.png",
        300_000,
        now - timedelta(days=1),
    )
    ok, _ = is_eligible(fresh_screenshot, now=now)
    assert ok

    # Non-screenshot old files are still eligible.
    old_image = _make_file(tmp_path / "chloe-hero.png", 300_000, now - timedelta(days=30))
    ok, _ = is_eligible(old_image, now=now)
    assert ok


def test_scan_source_dirs_dedupes_by_content(tmp_path: Path) -> None:
    a = _make_file(tmp_path / "dup_a.png", 300_000)
    b = _make_file(tmp_path / "dup_b.png", 300_000)  # identical content, different name
    b.write_bytes(a.read_bytes())
    _make_file(tmp_path / "clip.mp4", 400_000)

    candidates = scan_source_dirs([tmp_path])
    by_md5 = {c["md5"]: c for c in candidates}
    assert len(by_md5) == 2  # one of the dupes dropped
    paths = [c["path"] for c in candidates]
    assert len([p for p in paths if p.endswith(".png")]) == 1
    assert any(p.endswith("clip.mp4") for p in paths)
    kinds = {c["kind"] for c in candidates}
    assert kinds == {"image", "video"}


def test_upload_state_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    state = UploadState(folder_url="https://example.com")
    state.pending = [{"path": "/a.png", "md5": "abc", "size": 1, "kind": "image", "is_screenshot": False}]
    state.done = [{"path": "/b.mp4", "md5": "def", "size": 2, "kind": "video", "uploaded_at": "now"}]
    state.save(path)

    loaded = UploadState.load(path)
    assert loaded.folder_url == "https://example.com"
    assert loaded.done_md5s == {"def"}
    assert loaded.is_done("def")
    assert not loaded.is_done("zzz")


def test_collect_skips_done_and_preserves_pending(tmp_path: Path) -> None:
    state_path = tmp_path / "state.json"
    uploader = GDriveUploader(state_path)

    hero = _make_file(tmp_path / "hero.png", 300_000)
    _make_file(tmp_path / "clip.mp4", 400_000)

    result = uploader.collect([tmp_path])
    assert result["pending"] == 2
    assert result["done"] == 0

    # Mark the hero done by md5, then re-collect.
    hero_md5 = next(c["md5"] for c in uploader.state.pending if c["path"].endswith("hero.png"))
    uploader.state.done.append({"path": str(hero), "md5": hero_md5, "uploaded_at": "now"})
    uploader.state.save(state_path)

    uploader2 = GDriveUploader(state_path)
    result = uploader2.collect([tmp_path])
    assert result["already_done"] == 1
    assert result["pending"] == 1
    assert all(not item["path"].endswith("hero.png") for item in uploader2.state.pending)


def test_collect_drops_missing_pending(tmp_path: Path) -> None:
    state_path = tmp_path / "state.json"
    uploader = GDriveUploader(state_path)
    uploader.state.pending = [
        {"path": str(tmp_path / "ghost.png"), "md5": "abc", "size": 1, "kind": "image", "is_screenshot": False}
    ]
    uploader.state.save(state_path)

    _make_file(tmp_path / "real.png", 300_000)
    uploader2 = GDriveUploader(state_path)
    uploader2.collect([tmp_path])
    assert all(not item["path"].endswith("ghost.png") for item in uploader2.state.pending)
    assert any(item["path"].endswith("real.png") for item in uploader2.state.pending)


def test_status_reports_counts(tmp_path: Path) -> None:
    uploader = GDriveUploader(tmp_path / "state.json")
    uploader.state.pending = [{"path": "/a.png", "md5": "x", "size": 2_000_000, "kind": "image", "is_screenshot": False}]
    uploader.state.done = [{"path": "/b.mp4", "md5": "y", "size": 3_000_000, "kind": "video", "uploaded_at": "now"}]
    status = uploader.status()
    assert status["pending"] == 1
    assert status["done"] == 1
    assert status["pending_mb"] == 2.0


def test_uploader_passes_user_data_dir_and_cdp_to_playwright(tmp_path: Path) -> None:
    with patch("ai_influencer_studio.gdrive_uploader.sync_playwright") as mock_playwright:
        file_input = MagicMock()
        page = MagicMock()
        page.locator.return_value.all.return_value = [file_input]
        context = MagicMock()
        context.new_page.return_value = page
        launch = MagicMock(return_value=context)
        connect = MagicMock()
        connect.return_value.contexts = [context]
        mock_playwright.return_value.__enter__.return_value.chromium.launch_persistent_context = launch
        mock_playwright.return_value.__enter__.return_value.chromium.connect_over_cdp = connect

        # Persistent-context path with an explicit user_data_dir.
        uploader = GDriveUploader(tmp_path / "s1.json", user_data_dir=r"C:\Profiles\Main", cdp_url=None)
        uploader.state.pending = [
            {"path": str(tmp_path / "a.png"), "md5": "aaa", "size": 1, "kind": "image", "is_screenshot": False}
        ]
        uploader.upload_pending(batch_size=1, delay_seconds=0, user_data_dir=r"C:\Profiles\Main", cdp_url=None)
        launch.assert_called_once()
        assert launch.call_args.kwargs["user_data_dir"] == r"C:\Profiles\Main"
        assert not connect.called

        # CDP path attaches to a running browser.
        uploader2 = GDriveUploader(tmp_path / "s2.json", user_data_dir=None, cdp_url="http://127.0.0.1:9222")
        uploader2.state.pending = [
            {"path": str(tmp_path / "b.png"), "md5": "bbb", "size": 1, "kind": "image", "is_screenshot": False}
        ]
        uploader2.upload_pending(batch_size=1, delay_seconds=0)
        connect.assert_called_once_with("http://127.0.0.1:9222")


def test_upload_pending_stop_event_and_progress(tmp_path: Path) -> None:
    import threading

    with patch("ai_influencer_studio.gdrive_uploader.sync_playwright") as mock_playwright:
        file_input = MagicMock()
        page = MagicMock()
        page.locator.return_value.all.return_value = [file_input]
        context = MagicMock()
        context.new_page.return_value = page
        mock_playwright.return_value.__enter__.return_value.chromium.launch_persistent_context.return_value = context

        uploader = GDriveUploader(tmp_path / "s.json")
        for i, name in enumerate(("a.png", "b.mp4", "c.png")):
            (tmp_path / name).write_bytes(bytes([i + 1]) * 300_000)
        uploader.collect([tmp_path])
        assert len(uploader.state.pending) == 3

        stop_event = threading.Event()
        snapshots: list[dict] = []
        result = uploader.upload_pending(
            batch_size=1,
            delay_seconds=0,
            stop_event=stop_event,
            on_progress=snapshots.append,
        )
        assert result["uploaded"] == 3
        assert result["status"] == "done"
        assert len(snapshots) == 3
        assert snapshots[0]["uploaded"] == 1
        assert snapshots[-1]["done"] == 3

        # A pre-set stop event stops before the first batch.
        uploader2 = GDriveUploader(tmp_path / "s2.json")
        uploader2.state.pending = [
            {"path": str(tmp_path / "a.png"), "md5": "aaa", "size": 1, "kind": "image", "is_screenshot": False}
        ]
        stopped = threading.Event()
        stopped.set()
        result = uploader2.upload_pending(batch_size=1, delay_seconds=0, stop_event=stopped)
        assert result["status"] == "stopped"
        assert result["uploaded"] == 0


@patch("ai_influencer_studio.gdrive_uploader.sync_playwright")
def test_upload_pending_marks_done_and_drains(mock_playwright: MagicMock, tmp_path: Path) -> None:
    state_path = tmp_path / "state.json"
    uploader = GDriveUploader(state_path)
    for i, name in enumerate(("a.png", "b.mp4", "c.png")):
        (tmp_path / name).write_bytes(bytes([i + 1]) * 300_000)  # distinct content
    uploader.collect([tmp_path])
    assert len(uploader.state.pending) == 3

    # Fake playwright objects with the minimal surface _upload_batch touches.
    file_input = MagicMock()
    page = MagicMock()
    page.locator.return_value.all.return_value = [file_input]
    context = MagicMock()
    context.new_page.return_value = page
    mock_playwright.return_value.__enter__.return_value.chromium.launch_persistent_context.return_value = context

    result = uploader.upload_pending(batch_size=2, delay_seconds=0, headless=True)

    assert result["uploaded"] == 3
    assert result["batch_count"] == 2
    assert uploader.state.pending == []
    assert len(uploader.state.done) == 3
    # Content hashes recorded, not just paths.
    assert all("md5" in item and item["md5"] for item in uploader.state.done)

    # Done list survives a reload and blocks re-upload.
    reloaded = GDriveUploader(state_path)
    assert reloaded.state.done_md5s == {item["md5"] for item in uploader.state.done}


@patch("ai_influencer_studio.gdrive_uploader.sync_playwright")
def test_upload_pending_keeps_failed_batch_pending(mock_playwright: MagicMock, tmp_path: Path) -> None:
    state_path = tmp_path / "state.json"
    uploader = GDriveUploader(state_path)
    (tmp_path / "a.png").write_bytes(b"a" * 300_000)
    (tmp_path / "b.mp4").write_bytes(b"b" * 300_000)
    uploader.collect([tmp_path])

    def fail_once(locator):
        class _All:
            def all(self):
                return []

        return _All()

    page = MagicMock()
    page.locator.side_effect = fail_once  # no file input, no '+ New' -> RuntimeError
    context = MagicMock()
    context.new_page.return_value = page
    mock_playwright.return_value.__enter__.return_value.chromium.launch_persistent_context.return_value = context

    result = uploader.upload_pending(batch_size=2, delay_seconds=0, headless=True)
    assert result["uploaded"] == 0
    assert len(uploader.state.pending) == 2  # batch stays pending for retry
    assert uploader.state.done == []


def test_state_load_missing_file_returns_defaults(tmp_path: Path) -> None:
    state = UploadState.load(tmp_path / "nope.json")
    assert state.pending == []
    assert state.done == []
    assert state.folder_id


def test_state_save_writes_updated_at(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    UploadState().save(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["updated_at"]


def test_folder_id_extracted_from_url() -> None:
    from ai_influencer_studio.gdrive_uploader import _folder_id_from_url

    assert _folder_id_from_url("https://drive.google.com/drive/folders/abc123XYZ?usp=sharing") == "abc123XYZ"
    assert _folder_id_from_url("https://example.com/no-folder") == "13Ck6VKzc2pVIPBNW33wWjSTSDmRjYP2f"


def test_uploader_backend_router_selects_api(tmp_path: Path) -> None:
    uploader = GDriveUploader(tmp_path / "state.json")
    with patch.object(uploader, "upload_pending_via_api") as mock_api, patch.object(
        uploader, "_upload_pending_browser"
    ) as mock_browser:
        uploader.upload_pending(backend="drive_api")
        mock_api.assert_called_once()
        assert not mock_browser.called
        uploader.upload_pending(backend="browser")
        mock_browser.assert_called_once()


def test_uploader_backend_router_selects_rclone(tmp_path: Path) -> None:
    uploader = GDriveUploader(tmp_path / "state.json")
    with patch.object(uploader, "upload_pending_via_rclone") as mock_rclone, patch.object(
        uploader, "_upload_pending_browser"
    ) as mock_browser:
        uploader.upload_pending(backend="rclone")
        mock_rclone.assert_called_once()
        assert not mock_browser.called


def test_upload_pending_via_rclone_missing_remote_raises_clear_error(tmp_path: Path) -> None:
    uploader = GDriveUploader(tmp_path / "state.json", rclone_remote="")
    (tmp_path / "a.png").write_bytes(b"a" * 300_000)
    uploader.collect([tmp_path])
    with pytest.raises(RuntimeError, match="configured remote"):
        uploader.upload_pending_via_rclone()


def test_upload_pending_via_rclone_missing_executable_raises_clear_error(tmp_path: Path) -> None:
    with patch("ai_influencer_studio.gdrive_uploader.shutil.which", return_value=None):
        uploader = GDriveUploader(tmp_path / "state.json", rclone_remote="gdrive:")
        (tmp_path / "a.png").write_bytes(b"a" * 300_000)
        uploader.collect([tmp_path])
        with pytest.raises(RuntimeError, match="rclone is not installed"):
            uploader.upload_pending_via_rclone()


def test_upload_pending_via_rclone_marks_done_on_success(tmp_path: Path) -> None:
    uploader = GDriveUploader(tmp_path / "state.json", rclone_remote="gdrive:", rclone_path="refmedia")
    (tmp_path / "a.png").write_bytes(b"a" * 300_000)
    uploader.collect([tmp_path])
    assert len(uploader.state.pending) == 1

    with patch("ai_influencer_studio.gdrive_uploader.shutil.which", return_value="rclone"), patch(
        "ai_influencer_studio.gdrive_uploader.subprocess.run"
    ) as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        result = uploader.upload_pending_via_rclone(batch_size=5, delay_seconds=0)

    assert result["uploaded"] == 1
    assert result["failed"] == 0
    assert uploader.state.pending == []
    assert len(uploader.state.done) == 1
    assert uploader.state.done[0]["remote"] == "gdrive:/refmedia/a.png"
    cmd = mock_run.call_args.args[0]
    assert cmd[0] == "rclone"
    assert "copyto" in cmd
    assert "--checksum" in cmd
    assert cmd[-2] == "gdrive:/refmedia/a.png"


def test_upload_pending_via_rclone_keeps_failed_pending(tmp_path: Path) -> None:
    uploader = GDriveUploader(tmp_path / "state.json", rclone_remote="gdrive:")
    (tmp_path / "a.png").write_bytes(b"a" * 300_000)
    uploader.collect([tmp_path])

    with patch("ai_influencer_studio.gdrive_uploader.shutil.which", return_value="rclone"), patch(
        "ai_influencer_studio.gdrive_uploader.subprocess.run"
    ) as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "403 quota exceeded"
        result = uploader.upload_pending_via_rclone(batch_size=5, delay_seconds=0)

    assert result["uploaded"] == 0
    assert result["failed"] == 1
    assert len(uploader.state.pending) == 1  # kept for retry
    assert uploader.state.done == []


def test_upload_pending_via_api_marks_done_with_drive_ids(tmp_path: Path) -> None:
    from unittest.mock import patch as _patch

    with _patch("ai_influencer_studio.gdrive_uploader.gdrive_build") as mock_build, _patch(
        "ai_influencer_studio.gdrive_uploader.GDriveCredentials"
    ) as mock_creds:
        mock_creds.from_authorized_user_file.return_value = MagicMock(valid=True)
        (tmp_path / "token.json").write_text('{"fake": "token"}', encoding="utf-8")

        service = MagicMock()
        request = MagicMock()
        request.next_chunk.side_effect = [(None, {"id": "file-1", "name": "a.png"})]
        service.files().create.return_value = request
        mock_build.return_value = service

        uploader = GDriveUploader(
            tmp_path / "state.json",
            token_path=tmp_path / "token.json",
            client_secrets_path=tmp_path / "secrets.json",
        )
        (tmp_path / "a.png").write_bytes(b"a" * 300_000)
        uploader.collect([tmp_path])
        assert len(uploader.state.pending) == 1

        result = uploader.upload_pending_via_api(batch_size=5, delay_seconds=0)
        assert result["uploaded"] == 1
        assert result["failed"] == 0
        assert uploader.state.pending == []
        assert len(uploader.state.done) == 1
        assert uploader.state.done[0]["drive_file_id"] == "file-1"


def test_upload_pending_via_api_keeps_failed_file_pending(tmp_path: Path) -> None:
    from unittest.mock import patch as _patch

    with _patch("ai_influencer_studio.gdrive_uploader.gdrive_build") as mock_build, _patch(
        "ai_influencer_studio.gdrive_uploader.GDriveCredentials"
    ) as mock_creds:
        mock_creds.from_authorized_user_file.return_value = MagicMock(valid=True)
        (tmp_path / "token.json").write_text('{"fake": "token"}', encoding="utf-8")

        service = MagicMock()
        request = MagicMock()
        request.next_chunk.side_effect = RuntimeError("quota")
        service.files().create.return_value = request
        mock_build.return_value = service

        uploader = GDriveUploader(
            tmp_path / "state.json",
            token_path=tmp_path / "token.json",
            client_secrets_path=tmp_path / "secrets.json",
        )
        (tmp_path / "a.png").write_bytes(b"a" * 300_000)
        uploader.collect([tmp_path])

        result = uploader.upload_pending_via_api(batch_size=5, delay_seconds=0)
        assert result["uploaded"] == 0
        assert result["failed"] == 1
        assert len(uploader.state.pending) == 1  # kept for retry
        assert uploader.state.done == []


def test_upload_pending_via_api_missing_token_raises_clear_error(tmp_path: Path) -> None:
    uploader = GDriveUploader(
        tmp_path / "state.json",
        token_path=tmp_path / "missing_token.json",
        client_secrets_path=tmp_path / "missing_secrets.json",
    )
    (tmp_path / "a.png").write_bytes(b"a" * 300_000)
    uploader.collect([tmp_path])

    with pytest.raises(RuntimeError, match="OAuth client secrets not found"):
        uploader.upload_pending_via_api()


def test_cli_gdrive_upload_backend_flag(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    from ai_influencer_studio.cli import main

    state_path = tmp_path / "state.json"
    UploadState(folder_url="https://example.com").save(state_path)
    with patch("ai_influencer_studio.cli.StudioConfig") as mock_config, patch(
        "ai_influencer_studio.gdrive_uploader.GDriveUploader.upload_pending"
    ) as mock_upload:
        mock_config.from_file.return_value.gdrive_folder_url = "https://example.com"
        mock_config.from_file.return_value.gdrive_state_path = state_path
        mock_config.from_file.return_value.gdrive_backend = "browser"
        mock_config.from_file.return_value.gdrive_token_path = tmp_path / "token.json"
        mock_config.from_file.return_value.gdrive_client_secrets_path = tmp_path / "secrets.json"
        mock_upload.return_value = {"status": "done", "uploaded": 0, "batch_count": 0, "remaining_pending": 0}
        main(["gdrive", "upload", "--backend", "drive_api"])
        assert mock_upload.call_args.kwargs["backend"] == "drive_api"


def test_cli_gdrive_upload_rclone_backend_flag(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    from ai_influencer_studio.cli import main

    state_path = tmp_path / "state.json"
    UploadState(folder_url="https://example.com").save(state_path)
    with patch("ai_influencer_studio.cli.StudioConfig") as mock_config, patch(
        "ai_influencer_studio.gdrive_uploader.GDriveUploader.upload_pending"
    ) as mock_upload:
        mock_config.from_file.return_value.gdrive_folder_url = "https://example.com"
        mock_config.from_file.return_value.gdrive_state_path = state_path
        mock_config.from_file.return_value.gdrive_backend = "browser"
        mock_config.from_file.return_value.gdrive_token_path = tmp_path / "token.json"
        mock_config.from_file.return_value.gdrive_client_secrets_path = tmp_path / "secrets.json"
        mock_config.from_file.return_value.gdrive_rclone_remote = "gdrive:"
        mock_config.from_file.return_value.gdrive_rclone_path = "refmedia"
        mock_upload.return_value = {"status": "done", "uploaded": 0, "batch_count": 0, "remaining_pending": 0}
        main(["gdrive", "upload", "--backend", "rclone", "--rclone-remote", "backup:"])
        assert mock_upload.call_args.kwargs["backend"] == "rclone"


def test_cli_gdrive_collect(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    from ai_influencer_studio.cli import main

    _make_file(tmp_path / "hero.png", 300_000)
    state_path = tmp_path / "state.json"
    with patch("ai_influencer_studio.cli.StudioConfig") as mock_config:
        mock_config.from_file.return_value.gdrive_folder_url = "https://example.com"
        mock_config.from_file.return_value.gdrive_state_path = state_path
        main(["gdrive", "collect", "--source", str(tmp_path)])
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert output["pending"] == 1
    assert output["done"] == 0
    assert state_path.exists()


def test_cli_gdrive_status(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    from ai_influencer_studio.cli import main

    state_path = tmp_path / "state.json"
    UploadState(folder_url="https://example.com").save(state_path)
    with patch("ai_influencer_studio.cli.StudioConfig") as mock_config:
        mock_config.from_file.return_value.gdrive_folder_url = "https://example.com"
        mock_config.from_file.return_value.gdrive_state_path = state_path
        main(["gdrive", "status"])
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert output["folder_url"] == "https://example.com"
    assert output["pending"] == 0
    assert output["done"] == 0


def test_cli_gdrive_upload_uses_paced_batches(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    from ai_influencer_studio.cli import main

    state_path = tmp_path / "state.json"
    uploader = GDriveUploader(state_path)
    uploader.state.pending = [
        {"path": str(tmp_path / "a.png"), "md5": "aaa", "size": 1, "kind": "image", "is_screenshot": False},
        {"path": str(tmp_path / "b.mp4"), "md5": "bbb", "size": 1, "kind": "video", "is_screenshot": False},
    ]
    uploader.state.save(state_path)
    # Ensure the mocked uploader under test gets the pending entries.
    _loaded = GDriveUploader(state_path)
    assert len(_loaded.state.pending) == 2

    with patch("ai_influencer_studio.cli.StudioConfig") as mock_config, patch(
        "ai_influencer_studio.gdrive_uploader.GDriveUploader.upload_pending"
    ) as mock_upload:
        mock_config.from_file.return_value.gdrive_folder_url = "https://example.com"
        mock_config.from_file.return_value.gdrive_state_path = state_path
        mock_config.from_file.return_value.gdrive_backend = "browser"
        mock_config.from_file.return_value.gdrive_token_path = tmp_path / "token.json"
        mock_config.from_file.return_value.gdrive_client_secrets_path = tmp_path / "secrets.json"
        mock_upload.return_value = {"status": "done", "uploaded": 2, "batch_count": 1, "remaining_pending": 0}
        main(["gdrive", "upload", "--batch-size", "2", "--delay", "5"])
        mock_upload.assert_called_once_with(
            batch_size=2, delay_seconds=5, headless=True, max_batches=None, backend="browser"
        )
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert output["status"] == "done"
