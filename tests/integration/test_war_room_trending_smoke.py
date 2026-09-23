"""End-to-end smoke test for cont.16 trending pipeline (synthetic data).

Exercises the full pipeline: write snapshot A, mutate underlying state, write
snapshot B, diff A vs B. All in tmp_path. No live services, no live SLEEP_TRIPLE.

The 4 tests cover:
  1. Status transition is reported (FAIL -> OK between snapshots)
  2. Identical payloads print PASS no-transitions
  3. --a == --b (auto-pick same file as --a) emits INFO no-op
  4. Missing section in B (drift in section list) reported as MISSING transition

Module-level war_room import (see test_war_room_cmd_doctor_trend.py for the
WARNING about MOBILE_FILTERED import-time coupling).
"""
import argparse
import json
import os
import sys

import war_room


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _patch_snapshot_dir(monkeypatch, tmp_path):
    fake = tmp_path / "snapshots"
    fake.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(war_room, "_snapshot_dir", lambda: str(fake))
    return str(fake)


def _fake_cmd_doctor_payload(sections, aggregate_ok=True):
    """Build a fake cmd_doctor --json payload (matches real schema)."""
    return {
        "aggregate_ok": aggregate_ok,
        "sections": [{"name": n, "status": s, "detail": f"fake {n}"} for n, s in sections.items()],
    }


def _write_snapshot_via_mock(monkeypatch, sections, aggregate_ok=True):
    """Patch cmd_doctor + invoke cmd_snapshot_doctor. Returns the file written."""
    payload = _fake_cmd_doctor_payload(sections, aggregate_ok)

    def fake_cmd_doctor(_args):
        sys.stdout.write(json.dumps(payload))
        return 0

    monkeypatch.setattr(war_room, "cmd_doctor", fake_cmd_doctor)
    rc = war_room.cmd_snapshot_doctor(argparse.Namespace(list=False, keep_last=None, json=False))
    assert rc == 0
    return payload


# ---------------------------------------------------------------------------
# TestTrendingSmokePipeline - 4 synthetic end-to-end tests
# ---------------------------------------------------------------------------
class TestTrendingSmokePipeline:
    def test_status_transition_a_to_b_reported(self, tmp_path, monkeypatch, capsys):
        """Pipeline: write A (health=FAIL), write B (health=OK), diff -> 1 transition."""
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        # Snapshot A: health=FAIL
        _write_snapshot_via_mock(monkeypatch, {"health": "FAIL"}, aggregate_ok=False)
        a_files = sorted(fn for fn in os.listdir(fake) if fn.endswith(".json"))
        assert len(a_files) == 1
        # Force mtime ordering
        os.utime(os.path.join(fake, a_files[0]), (2_000_000_000, 2_000_000_000))
        # Snapshot B: health=OK
        _write_snapshot_via_mock(monkeypatch, {"health": "OK"}, aggregate_ok=True)
        b_files = sorted(fn for fn in os.listdir(fake) if fn.endswith(".json"))
        assert len(b_files) == 2
        os.utime(os.path.join(fake, b_files[1]), (2_000_000_002, 2_000_000_002))
        # Diff A vs B
        rc = war_room.cmd_diff_doctor(argparse.Namespace(a=a_files[0], b=b_files[1], json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "1 section status transition" in out
        assert "health" in out and "FAIL" in out and "OK" in out

    def test_identical_payloads_print_pass(self, tmp_path, monkeypatch, capsys):
        """Pipeline: write A, write B (same), diff -> PASS no transitions."""
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        _write_snapshot_via_mock(monkeypatch, {"git": "OK", "health": "OK"})
        a_files = sorted(fn for fn in os.listdir(fake) if fn.endswith(".json"))
        os.utime(os.path.join(fake, a_files[0]), (2_000_000_000, 2_000_000_000))
        _write_snapshot_via_mock(monkeypatch, {"git": "OK", "health": "OK"})
        b_files = sorted(fn for fn in os.listdir(fake) if fn.endswith(".json"))
        os.utime(os.path.join(fake, b_files[1]), (2_000_000_002, 2_000_000_002))
        rc = war_room.cmd_diff_doctor(argparse.Namespace(a=a_files[0], b=b_files[1], json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "[PASS] no status transitions" in out

    def test_a_equals_b_auto_pick_emits_info(self, tmp_path, monkeypatch, capsys):
        """Pipeline: write only ONE snapshot, diff with --a=exact, --b auto-picks same file -> INFO."""
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        _write_snapshot_via_mock(monkeypatch, {"git": "OK"})
        a_files = sorted(fn for fn in os.listdir(fake) if fn.endswith(".json"))
        # Use the exact filename for --a; --b=None auto-picks the same file
        rc = war_room.cmd_diff_doctor(argparse.Namespace(a=a_files[0], b=None, json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "[INFO] --a and --b resolve to the SAME snapshot" in out

    def test_missing_section_in_b_reported_as_missing(self, tmp_path, monkeypatch, capsys):
        """Pipeline: A has 3 sections, B has 2 (one removed) -> 'tools' shows OK -> MISSING transition."""
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        # A: 3 sections
        _write_snapshot_via_mock(monkeypatch, {"health": "OK", "git": "OK", "tools": "OK"})
        a_files = sorted(fn for fn in os.listdir(fake) if fn.endswith(".json"))
        os.utime(os.path.join(fake, a_files[0]), (2_000_000_000, 2_000_000_000))
        # B: 2 sections (removed "tools")
        _write_snapshot_via_mock(monkeypatch, {"health": "OK", "git": "OK"})
        b_files = sorted(fn for fn in os.listdir(fake) if fn.endswith(".json"))
        os.utime(os.path.join(fake, b_files[1]), (2_000_000_002, 2_000_000_002))
        rc = war_room.cmd_diff_doctor(argparse.Namespace(a=a_files[0], b=b_files[1], json=False))
        out = capsys.readouterr().out
        assert rc == 0
        # tools was OK in A, MISSING in B -> transition reported
        assert "tools" in out and "OK" in out and "MISSING" in out
