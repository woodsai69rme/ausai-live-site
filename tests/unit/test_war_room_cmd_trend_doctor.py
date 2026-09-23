"""Unit tests for cont.18 trend-doctor subcommand.

Covers (no live services, real tmpdir I/O):
  - Empty window returns [INFO] + rc=0
  - Single section with constant status -> 0 transitions
  - Section with status flips -> N transitions counted
  - --json output shape (window_days, snapshot_count, sections keyed by name)
  - Invalid --window format -> [FAIL] + rc=1
  - Section-list drift (added/removed mid-window) -> MISSING status + transition counted
"""
import argparse
import json
import os
import pytest

import war_room


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _patch_snapshot_dir(monkeypatch, tmp_path):
    fake = tmp_path / "snapshots"
    fake.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(war_room, "_snapshot_dir", lambda: str(fake))
    return str(fake)


def _seed(fake, stamp, sections, mtime_epoch):
    """Write a fake snapshot__<stamp>.json with the given sections + mtime."""
    payload = {
        "aggregate_ok": True,
        "sections": [{"name": n, "status": s, "detail": "fake"} for n, s in sections.items()],
        "schema_version": war_room.DOCTOR_SNAPSHOT_SCHEMA_VERSION,
    }
    fp = os.path.join(fake, f"snapshot__{stamp}.json")
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    os.utime(fp, (mtime_epoch, mtime_epoch))
    return fp


# ---------------------------------------------------------------------------
# TestCmdTrendDoctor
# ---------------------------------------------------------------------------
class TestCmdTrendDoctor:
    def test_empty_window_returns_info(self, tmp_path, monkeypatch, capsys):
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        rc = war_room.cmd_trend_doctor(argparse.Namespace(window="7d", json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "snapshots: 0" in out
        assert "[INFO] no snapshots in last 7d window" in out

    def test_single_section_no_transitions(self, tmp_path, monkeypatch, capsys):
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        # 3 snapshots, all health=OK -> 0 transitions
        for i, stamp in enumerate(["2026-07-08_120000", "2026-07-09_120000", "2026-07-10_120000"]):
            _seed(fake, stamp, {"health": "OK"}, mtime_epoch=2_000_000_000 + i * 100)
        rc = war_room.cmd_trend_doctor(argparse.Namespace(window="7d", json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "snapshots: 3" in out
        assert "health" in out
        assert "OK: 3" in out
        # Column-precise line extraction (MINOR cont.19, matches sibling test pattern)
        health_line = [line for line in out.splitlines() if line.strip().startswith("health")][0]
        assert health_line.strip().endswith("0"), f"expected health line to end with 0, got: {health_line!r}"

    def test_transitions_counted(self, tmp_path, monkeypatch, capsys):
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        # 4 snapshots: OK -> FAIL -> OK -> FAIL (3 transitions)
        for i, (stamp, status) in enumerate([
            ("2026-07-08_120000", "OK"),
            ("2026-07-09_120000", "FAIL"),
            ("2026-07-10_120000", "OK"),
            ("2026-07-10_140000", "FAIL"),
        ]):
            _seed(fake, stamp, {"health": status}, mtime_epoch=2_000_000_000 + i * 100)
        rc = war_room.cmd_trend_doctor(argparse.Namespace(window="7d", json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "OK: 2" in out
        assert "FAIL: 2" in out
        # 3 transitions (OK->FAIL, FAIL->OK, OK->FAIL)
        # The transitions column is the last column; check by looking for "3" in the right place
        # Simplest: assert "3" appears after "health"
        # Split output by lines and find the health line
        health_line = [line for line in out.splitlines() if "health" in line][0]
        assert health_line.strip().endswith("3"), f"expected health line to end with 3, got: {health_line!r}"

    def test_json_output_shape(self, tmp_path, monkeypatch, capsys):
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        for i, stamp in enumerate(["2026-07-09_120000", "2026-07-10_120000"]):
            _seed(fake, stamp, {"health": "OK"}, mtime_epoch=2_000_000_000 + i * 100)
        rc = war_room.cmd_trend_doctor(argparse.Namespace(window="7d", json=True))
        out = capsys.readouterr().out
        assert rc == 0
        body = json.loads(out)
        assert body["window_days"] == 7
        assert body["snapshot_count"] == 2
        assert "health" in body["sections"]
        assert body["sections"]["health"]["status_counts"] == {"OK": 2}
        assert body["sections"]["health"]["transitions"] == 0
        assert body["sections"]["health"]["snapshot_count"] == 2

    def test_invalid_window_format_returns_fail(self, tmp_path, monkeypatch, capsys):
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        rc = war_room.cmd_trend_doctor(argparse.Namespace(window="7", json=False))
        out = capsys.readouterr().out
        assert rc == 1
        assert "[FAIL] --window must be Nd format" in out
        # Also test other bad formats
        for bad in ["abc", "7days", "1.5d", ""]:
            rc = war_room.cmd_trend_doctor(argparse.Namespace(window=bad, json=False))
            assert rc == 1, f"expected rc=1 for window={bad!r}"

    def test_section_drift_marked_missing(self, tmp_path, monkeypatch, capsys):
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        # Snapshot 1: has both health + tools (OK)
        # Snapshot 2: only has health (tools removed) -> tools gets MISSING status
        for i, (stamp, sections) in enumerate([
            ("2026-07-09_120000", {"health": "OK", "tools": "OK"}),
            ("2026-07-10_120000", {"health": "OK"}),
        ]):
            _seed(fake, stamp, sections, mtime_epoch=2_000_000_000 + i * 100)
        rc = war_room.cmd_trend_doctor(argparse.Namespace(window="7d", json=False))
        out = capsys.readouterr().out
        assert rc == 0
        # tools should appear with MISSING status + 1 transition (OK -> MISSING)
        tools_line = [line for line in out.splitlines() if line.strip().startswith("tools")][0]
        assert "MISSING" in tools_line, f"expected MISSING in tools line, got: {tools_line!r}"
        # 1 transition for tools (OK -> MISSING)
        assert tools_line.strip().endswith("1"), f"expected tools to end with 1, got: {tools_line!r}"
        # health should still show OK:2 with 0 transitions
        health_line = [line for line in out.splitlines() if line.strip().startswith("health")][0]
        assert "OK: 2" in health_line
        assert health_line.strip().endswith("0"), f"expected health to end with 0, got: {health_line!r}"

    def test_30d_window_includes_older_snapshots(self, tmp_path, monkeypatch, capsys):
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        import time as _time
        now = int(_time.time())
        # Snapshot from 20 days ago (within 30d window, outside 7d window)
        _seed(fake, "2026-06-20_120000", {"health": "OK"}, mtime_epoch=now - 20 * 24 * 3600)
        rc = war_room.cmd_trend_doctor(argparse.Namespace(window="30d", json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "snapshots: 1" in out
        assert "health" in out
        # 7d window should miss it
        rc2 = war_room.cmd_trend_doctor(argparse.Namespace(window="7d", json=False))
        out2 = capsys.readouterr().out
        assert rc2 == 0
        assert "snapshots: 0" in out2
