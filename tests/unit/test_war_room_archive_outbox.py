"""Unit tests for war_room.cmd_archive_outbox (added cont.14).

cmd_archive_outbox rolls SLEEP_TRIPLE/outbox/* into archive/outbox_YYYY-MM-DD/.
Tests use tmp_path + monkeypatch of war_room.__file__ to redirect outbox_root and
archive_root into disposable locations, then assert file movement / dry-run / filters.
"""
import argparse
import json
import os
import shutil
import sys
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import war_room  # noqa: E402


def _ns(**kw):
    return argparse.Namespace(**kw)


def _seed_outbox(tmp_path, spec):
    """Build SLEEP_TRIPLE/outbox/<subdir>/<file> layout from spec dict.

    spec = {"a_digital_factory": ["file1.txt", "file2.png"], "b_faceless_shorts": ["script.md"]}
    Returns (outbox_root, archive_root) absolute paths.
    """
    st_root = tmp_path / "SLEEP_TRIPLE"
    outbox_root = st_root / "outbox"
    archive_root = st_root / "archive"
    for subdir, files in spec.items():
        sub = outbox_root / subdir
        sub.mkdir(parents=True)
        for fn in files:
            (sub / fn).write_text(f"contents-{fn}")
    return str(outbox_root), str(archive_root)


class TestArchiveOutboxBasic:
    """Happy-path + core behavior."""

    def test_archive_moves_all_files_across_subdirs(self, monkeypatch, tmp_path, capsys):
        monkeypatch.setattr(war_room, "__file__", os.path.join(str(tmp_path), "war_room.py"))
        _seed_outbox(tmp_path, {
            "a_digital_factory": ["file1.txt", "file2.txt"],
            "b_faceless_shorts": ["script.md"],
            "e_pod": ["design.png"],
        })

        rc = war_room.cmd_archive_outbox(_ns(dry_run=False, keep_last=None, category=None, json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "moved     : 4" in out
        assert "[PASS]" in out

        date_str = time.strftime("%Y-%m-%d")
        archive = tmp_path / "SLEEP_TRIPLE" / "archive" / f"outbox_{date_str}"
        assert (archive / "a_digital_factory" / "file1.txt").exists()
        assert (archive / "a_digital_factory" / "file2.txt").exists()
        assert (archive / "b_faceless_shorts" / "script.md").exists()
        assert (archive / "e_pod" / "design.png").exists()

        # Sources gone
        src = tmp_path / "SLEEP_TRIPLE" / "outbox"
        assert not (src / "a_digital_factory" / "file1.txt").exists()
        assert not (src / "e_pod" / "design.png").exists()

    def test_archive_dry_run_does_not_move_files(self, monkeypatch, tmp_path, capsys):
        monkeypatch.setattr(war_room, "__file__", os.path.join(str(tmp_path), "war_room.py"))
        _seed_outbox(tmp_path, {"a_digital_factory": ["d1.txt"]})

        rc = war_room.cmd_archive_outbox(_ns(dry_run=True, keep_last=None, category=None, json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "dry-run   : 1" in out
        # Source STILL exists
        assert (tmp_path / "SLEEP_TRIPLE" / "outbox" / "a_digital_factory" / "d1.txt").exists()
        # Archive dir never created (no actual move)
        archive = tmp_path / "SLEEP_TRIPLE" / "archive"
        assert not archive.exists() or not (archive / f"outbox_{time.strftime('%Y-%m-%d')}").exists()


class TestArchiveOutboxFiltering:
    """--keep-last and --category filters."""

    def test_keep_last_n_keeps_recent_files(self, monkeypatch, tmp_path):
        monkeypatch.setattr(war_room, "__file__", os.path.join(str(tmp_path), "war_room.py"))
        _seed_outbox(tmp_path, {"a_digital_factory": ["old.txt", "fresh.txt"]})
        # Make old.txt 30 days old, fresh.txt 1 day old
        old_mtime = time.time() - 30 * 24 * 3600
        fresh_mtime = time.time() - 1 * 24 * 3600
        os.utime(tmp_path / "SLEEP_TRIPLE" / "outbox" / "a_digital_factory" / "old.txt",
                 (old_mtime, old_mtime))
        os.utime(tmp_path / "SLEEP_TRIPLE" / "outbox" / "a_digital_factory" / "fresh.txt",
                 (fresh_mtime, fresh_mtime))

        rc = war_room.cmd_archive_outbox(_ns(dry_run=False, keep_last=7, category=None, json=False))
        assert rc == 0

        date_str = time.strftime("%Y-%m-%d")
        archive = tmp_path / "SLEEP_TRIPLE" / "archive" / f"outbox_{date_str}"
        # Old moved, fresh retained
        assert (archive / "a_digital_factory" / "old.txt").exists()
        assert not (archive / "a_digital_factory" / "fresh.txt").exists()
        # Fresh source still in outbox
        outbox = tmp_path / "SLEEP_TRIPLE" / "outbox" / "a_digital_factory"
        assert not (outbox / "old.txt").exists()
        assert (outbox / "fresh.txt").exists()

    def test_category_filter_only_archives_subdir(self, monkeypatch, tmp_path):
        monkeypatch.setattr(war_room, "__file__", os.path.join(str(tmp_path), "war_room.py"))
        _seed_outbox(tmp_path, {
            "a_digital_factory": ["a1.txt"],
            "e_pod": ["design.png"],
        })

        rc = war_room.cmd_archive_outbox(_ns(dry_run=False, keep_last=None, category="e_pod", json=False))
        assert rc == 0

        date_str = time.strftime("%Y-%m-%d")
        archive = tmp_path / "SLEEP_TRIPLE" / "archive" / f"outbox_{date_str}"
        # Only e_pod archived
        assert (archive / "e_pod" / "design.png").exists()
        assert "a_digital_factory" not in [p.name for p in archive.iterdir()] \
               or not (archive / "a_digital_factory").exists()
        # a_digital_factory source UNTOUCHED
        assert (tmp_path / "SLEEP_TRIPLE" / "outbox" / "a_digital_factory" / "a1.txt").exists()
        # e_pod source moved
        assert not (tmp_path / "SLEEP_TRIPLE" / "outbox" / "e_pod" / "design.png").exists()


class TestArchiveOutboxJson:
    """--json output shape contract."""

    def test_json_output_shape_is_stable(self, monkeypatch, tmp_path, capsys):
        monkeypatch.setattr(war_room, "__file__", os.path.join(str(tmp_path), "war_room.py"))
        _seed_outbox(tmp_path, {"a_digital_factory": ["x.txt"]})

        rc = war_room.cmd_archive_outbox(_ns(dry_run=False, keep_last=None, category=None, json=True))
        out = capsys.readouterr().out.strip()
        result = json.loads(out)
        assert isinstance(result, dict)
        assert rc == 0
        # Top-level keys
        assert "date_str" in result
        assert "dry_run" in result
        assert result["dry_run"] is False
        assert "outbox_root" in result
        assert "archive_root" in result
        assert "aggregate_ok" in result and result["aggregate_ok"] is True
        assert "file_counts" in result
        assert result["file_counts"]["ok"] == 1
        assert result["file_counts"]["failed"] == 0
        assert isinstance(result["results"], list)
        assert len(result["results"]) == 1
        assert result["results"][0]["status"] == "OK"


class TestArchiveOutboxSafety:
    """Edge cases that must NOT escalate to FAIL."""

    def test_missing_outbox_is_info_not_fail(self, monkeypatch, tmp_path, capsys):
        # tmp_path/SLEEP_TRIPLE/ not even created
        monkeypatch.setattr(war_room, "__file__", os.path.join(str(tmp_path), "war_room.py"))
        rc = war_room.cmd_archive_outbox(_ns(dry_run=False, keep_last=None, category=None, json=False))
        out = capsys.readouterr().out
        assert rc == 0  # INFO not FAIL -- legitimate clean-PC state (no SLEEP_TRIPLE yet)
        assert "[INFO]" in out
        assert "[FAIL]" not in out

    def test_empty_outbox_subdirs_return_zero_count(self, monkeypatch, tmp_path, capsys):
        # Create empty outbox with one subdir containing NO files
        monkeypatch.setattr(war_room, "__file__", os.path.join(str(tmp_path), "war_room.py"))
        empty = tmp_path / "SLEEP_TRIPLE" / "outbox" / "a_digital_factory"
        empty.mkdir(parents=True)

        rc = war_room.cmd_archive_outbox(_ns(dry_run=False, keep_last=None, category=None, json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "moved     : 0" in out
