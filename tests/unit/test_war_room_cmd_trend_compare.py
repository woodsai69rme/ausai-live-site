"""Unit tests for cont.21 trend-compare subcommand.

Covers (no live services, real tmpdir I/O):
  - Text mode renders per-section RATE-based verdict (MORE_FLAPPING / STABLE / MORE_STABLE)
  - --json output shape includes rate_a_per_day, rate_b_per_day, transitions counts
  - Invalid --a or --b format -> [FAIL] + rc=1
  - Empty windows (no snapshots) -> [INFO] no sections + rc=0

NOTE on RATE-BASED verdict (cont.21): cmd_trend_compare classifies sections by
transitions/day, NOT raw transition count. This makes the default --a=1d --b=7d
useful (raw comparison would be degenerate since 1d snapshots are a subset of 7d
snapshots, so 1d transitions can never exceed 7d transitions).
"""
import argparse
import json
import os
import time
import pytest

import war_room


# ---------------------------------------------------------------------------
# Helpers (mirror test_war_room_cmd_trend_doctor.py pattern)
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
# TestCmdTrendCompare
# ---------------------------------------------------------------------------
class TestCmdTrendCompare:
    def test_text_mode_renders_per_section_verdict(self, tmp_path, monkeypatch, capsys):
        """1d with 2 transitions vs 7d with 2 transitions -> MORE_FLAPPING (rate 2/day vs 0.29/day).

        Test data design (offsets use 23h / 20h / 1h inside the 1d window — NOT
        exact 24h — so wall-clock drift between seed and cmd_trend_compare cannot
        drop the boundary snap via `mt >= now - 86400`):
          - 6, 5, 4 days ago: {health: OK, tools: OK/FAIL} (within 7d, outside 1d)
          - 20h, 12h, 1h ago: {health: OK/FAIL/OK, tools: OK/OK/OK} (within both)
        Expected:
          - health: 1d=2 transitions, 7d=2 transitions; rate_a=2.0, rate_b=0.286; MORE_FLAPPING
          - tools:  1d=0 transitions, 7d=2 transitions; rate_a=0.0, rate_b=0.286; MORE_STABLE
        """
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        now = int(time.time())
        # 6 days ago: tools OK
        _seed(fake, "2026-07-04_120000", {"health": "OK", "tools": "OK"}, mtime_epoch=now - 6 * 24 * 3600)
        # 5 days ago: tools OK
        _seed(fake, "2026-07-05_120000", {"health": "OK", "tools": "OK"}, mtime_epoch=now - 5 * 24 * 3600)
        # 4 days ago: tools FAIL (the only flapping outside the 1d window)
        _seed(fake, "2026-07-06_120000", {"health": "OK", "tools": "FAIL"}, mtime_epoch=now - 4 * 24 * 3600)
        # 20h ago: health OK (safely inside 1d window)
        _seed(fake, "2026-07-09_120000", {"health": "OK", "tools": "OK"}, mtime_epoch=now - 20 * 3600)
        # 12h ago: health FAIL (flapping inside the 1d window)
        _seed(fake, "2026-07-09_180000", {"health": "FAIL", "tools": "OK"}, mtime_epoch=now - 12 * 3600)
        # 1h ago: health OK
        _seed(fake, "2026-07-10_060000", {"health": "OK", "tools": "OK"}, mtime_epoch=now - 1 * 3600)

        rc = war_room.cmd_trend_compare(argparse.Namespace(a="1d", b="7d", json=False))
        out = capsys.readouterr().out
        assert rc == 0
        # Header (locks the table column layout — prevents silent layout drift)
        assert "TREND COMPARE" in out
        assert "a: 1d" in out
        assert "b: 7d" in out
        assert "SECTION" in out and "A (rate)" in out and "B (rate)" in out and "VERDICT" in out
        # health section: rate 2/1d vs 2/7d, verdict MORE_FLAPPING
        health_line = [line for line in out.splitlines() if line.strip().startswith("health")][0]
        assert "2/1d" in health_line, f"expected '2/1d' in health line, got: {health_line!r}"
        assert "2/7d" in health_line, f"expected '2/7d' in health line, got: {health_line!r}"
        assert health_line.strip().endswith("MORE_FLAPPING"), f"expected MORE_FLAPPING, got: {health_line!r}"
        # tools section: rate 0/1d vs 2/7d, verdict MORE_STABLE
        tools_line = [line for line in out.splitlines() if line.strip().startswith("tools")][0]
        assert "0/1d" in tools_line, f"expected '0/1d' in tools line, got: {tools_line!r}"
        assert "2/7d" in tools_line, f"expected '2/7d' in tools line, got: {tools_line!r}"
        assert tools_line.strip().endswith("MORE_STABLE"), f"expected MORE_STABLE, got: {tools_line!r}"

    def test_json_mode_emits_composite_with_rates(self, tmp_path, monkeypatch, capsys):
        """--json output includes window_a_days, window_b_days, sections with rate_a_per_day + rate_b_per_day + verdict."""
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        now = int(time.time())
        # Use 20h / 12h / 1h offsets (not exact 24h) so wall-clock drift cannot
        # drop the oldest snap out of the 1d window via `mt >= now - 86400`.
        _seed(fake, "2026-07-09_120000", {"health": "OK"}, mtime_epoch=now - 20 * 3600)
        _seed(fake, "2026-07-09_180000", {"health": "FAIL"}, mtime_epoch=now - 12 * 3600)
        _seed(fake, "2026-07-10_060000", {"health": "OK"}, mtime_epoch=now - 1 * 3600)

        rc = war_room.cmd_trend_compare(argparse.Namespace(a="1d", b="7d", json=True))
        out = capsys.readouterr().out
        assert rc == 0
        body = json.loads(out)
        assert body["window_a_days"] == 1
        assert body["window_b_days"] == 7
        # 3 snapshots all within 1d (so 1d count == 7d count == 3)
        assert body["snapshot_count_a"] == 3
        assert body["snapshot_count_b"] == 3
        # health section with rate fields + verdict
        assert "health" in body["sections"]
        h = body["sections"]["health"]
        assert h["transitions_a"] == 2  # OK -> FAIL -> OK = 2 transitions in 1d
        assert h["transitions_b"] == 2  # same 2 transitions in 7d (no older snapshots to add)
        assert h["rate_a_per_day"] == 2.0
        # 2 transitions / 7 days = 0.2857
        assert 0.28 < h["rate_b_per_day"] < 0.29, f"expected rate_b ~0.286, got {h['rate_b_per_day']}"
        # 2.0 > 0.286 -> MORE_FLAPPING
        assert h["verdict"] == "MORE_FLAPPING"

    def test_invalid_format_returns_fail(self, tmp_path, monkeypatch, capsys):
        """Bad --a or --b format -> [FAIL] + rc=1 (strict Nd format like cmd_trend_doctor)."""
        _patch_snapshot_dir(monkeypatch, tmp_path)
        # Bad --a
        rc = war_room.cmd_trend_compare(argparse.Namespace(a="abc", b="7d", json=False))
        out = capsys.readouterr().out
        assert rc == 1
        assert "[FAIL] --a must be Nd format" in out
        assert "'abc'" in out
        # Bad --b
        rc = war_room.cmd_trend_compare(argparse.Namespace(a="1d", b="7", json=False))
        out = capsys.readouterr().out
        assert rc == 1
        assert "[FAIL] --b must be Nd format" in out
        # Also exercise other invalid formats
        for bad in ["", "7days", "1.5d", "d", "0d"]:
            rc = war_room.cmd_trend_compare(argparse.Namespace(a=bad, b="7d", json=False))
            assert rc == 1, f"expected rc=1 for --a={bad!r}"
            rc = war_room.cmd_trend_compare(argparse.Namespace(a="1d", b=bad, json=False))
            assert rc == 1, f"expected rc=1 for --b={bad!r}"

    def test_empty_windows_returns_info(self, tmp_path, monkeypatch, capsys):
        """Both windows empty (no snapshots) -> [INFO] no sections to compare + rc=0."""
        _patch_snapshot_dir(monkeypatch, tmp_path)
        # Text mode
        rc = war_room.cmd_trend_compare(argparse.Namespace(a="1d", b="7d", json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "TREND COMPARE" in out
        assert "[INFO] no sections to compare" in out
        # JSON mode: empty sections dict
        rc = war_room.cmd_trend_compare(argparse.Namespace(a="1d", b="7d", json=True))
        out = capsys.readouterr().out
        assert rc == 0
        body = json.loads(out)
        assert body["window_a_days"] == 1
        assert body["window_b_days"] == 7
        assert body["snapshot_count_a"] == 0
        assert body["snapshot_count_b"] == 0
        assert body["sections"] == {}

    def test_stable_verdict_when_rates_equal(self, tmp_path, monkeypatch, capsys):
        """Equal transition rates across equal-length windows -> STABLE."""
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        now = int(time.time())
        # Two 1d-ish windows of equal length: use --a 1d --b 1d so rate_a == rate_b
        # whenever transitions_a == transitions_b (same snap set for both).
        _seed(fake, "2026-07-09_120000", {"health": "OK"}, mtime_epoch=now - 20 * 3600)
        _seed(fake, "2026-07-09_180000", {"health": "FAIL"}, mtime_epoch=now - 12 * 3600)
        _seed(fake, "2026-07-10_060000", {"health": "OK"}, mtime_epoch=now - 1 * 3600)

        rc = war_room.cmd_trend_compare(argparse.Namespace(a="1d", b="1d", json=True))
        out = capsys.readouterr().out
        assert rc == 0
        body = json.loads(out)
        h = body["sections"]["health"]
        assert h["transitions_a"] == h["transitions_b"] == 2
        assert h["rate_a_per_day"] == h["rate_b_per_day"]
        assert h["verdict"] == "STABLE"

    def test_section_only_in_baseline_window(self, tmp_path, monkeypatch, capsys):
        """Section appears only in --b baseline window -> ta=0, tb>0 -> rate_a < rate_b -> MORE_STABLE.

        Models section-discovered-mid-stream: an operator adds a new check to cmd_doctor
        and trend-compare should classify the new section as MORE_STABLE (it has 0
        transitions in 'today' because the check didn't exist yet).
        """
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        now = int(time.time())
        # 6 days ago: tools section exists (within 7d --b window, outside 1d --a window)
        _seed(fake, "2026-07-04_120000", {"health": "OK", "tools": "OK"}, mtime_epoch=now - 6 * 24 * 3600)
        _seed(fake, "2026-07-05_120000", {"health": "OK", "tools": "FAIL"}, mtime_epoch=now - 5 * 24 * 3600)
        _seed(fake, "2026-07-06_120000", {"health": "OK", "tools": "OK"}, mtime_epoch=now - 4 * 24 * 3600)
        # 1d window (--a): only health section present, no tools
        _seed(fake, "2026-07-09_180000", {"health": "OK"}, mtime_epoch=now - 12 * 3600)
        _seed(fake, "2026-07-10_060000", {"health": "OK"}, mtime_epoch=now - 1 * 3600)

        rc = war_room.cmd_trend_compare(argparse.Namespace(a="1d", b="7d", json=True))
        out = capsys.readouterr().out
        assert rc == 0
        body = json.loads(out)
        # tools section exists (was found in the 7d baseline snaps)
        assert "tools" in body["sections"]
        t = body["sections"]["tools"]
        assert t["transitions_a"] == 0  # no tools snaps within 1d
        # In 7d the tools history is [OK, FAIL, OK, MISSING, MISSING] = 3 transitions:
        # OK->FAIL (1), FAIL->OK (2), OK->MISSING (3).
        # MISSING is a real status (section disappeared mid-window), so OK->MISSING counts.
        # MISSING->MISSING at idx 3->4 is correctly excluded (no change).
        assert t["transitions_b"] == 3
        assert t["rate_a_per_day"] == 0.0
        # 3 transitions / 7 days = 0.4286
        assert 0.42 < t["rate_b_per_day"] < 0.44, f"expected rate_b ~0.4286, got {t['rate_b_per_day']}"
        assert t["verdict"] == "MORE_STABLE"
