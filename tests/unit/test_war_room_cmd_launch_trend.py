"""Unit tests for cont.19 launch-trend subcommand.

Covers (no live services, real tmpdir I/O):
  - End-to-end happy path: snapshot A + sleep + snapshot B + diff + trend runs without error
  - No-transitions case: identical snapshots -> diff reports PASS no transitions
  - --json mode emits composite under 'diff' + 'trend' keys
  - Snapshot failure returns rc=1 immediately (no diff/trend)

The cmd_snapshot_doctor is mocked at the war_room module level (war_room.cmd_snapshot_doctor)
so write-mode tests don't depend on live services. cmd_diff_doctor + cmd_trend_doctor run
on real snapshot files in the tmp_path cache.
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


def _write_fake_snapshot(fake, stamp, sections, mtime_epoch, *, schema_version=None):
    """Write a fake snapshot to fake_dir with explicit mtime + schema_version."""
    payload = {
        "aggregate_ok": True,
        "sections": [{"name": n, "status": s, "detail": "fake"} for n, s in sections.items()],
        "schema_version": schema_version or war_room.DOCTOR_SNAPSHOT_SCHEMA_VERSION,
    }
    fp = os.path.join(fake, f"snapshot__{stamp}.json")
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    os.utime(fp, (mtime_epoch, mtime_epoch))
    return fp


# ---------------------------------------------------------------------------
# TestCmdLaunchTrend
# ---------------------------------------------------------------------------
class TestCmdLaunchTrend:
    def test_end_to_end_happy_path(self, tmp_path, monkeypatch, capsys):
        """snapshot A + sleep + snapshot B + diff + trend runs without error."""
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        counter = {"calls": 0}

        def fake_snapshot_doctor(_args):
            counter["calls"] += 1
            stamp = f"2026-07-10_12000{counter['calls']}"
            sections = {"health": "OK" if counter["calls"] == 1 else "FAIL"}
            _write_fake_snapshot(fake, stamp, sections, mtime_epoch=2_000_000_000 + counter["calls"])
            return 0

        monkeypatch.setattr(war_room, "cmd_snapshot_doctor", fake_snapshot_doctor)
        # Use 0s sleep to keep test fast
        rc = war_room.cmd_launch_trend(argparse.Namespace(sleep=0, window="1d", json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "[1/4] snapshot A" in out
        assert "[3/4] snapshot B" in out
        assert "[4/4] diff + trend" in out
        assert "DIFF A vs B" in out
        assert "TREND" in out
        # Diff should show 1 transition (OK -> FAIL)
        assert "FAIL" in out
        assert "->" in out
        # Should have made exactly 2 snapshot calls
        assert counter["calls"] == 2

    def test_no_transitions(self, tmp_path, monkeypatch, capsys):
        """If both snapshots are identical, diff shows PASS no transitions."""
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        counter = {"calls": 0}

        def fake_snapshot_doctor(_args):
            counter["calls"] += 1
            stamp = f"2026-07-10_12000{counter['calls']}"
            _write_fake_snapshot(fake, stamp, {"health": "OK"}, mtime_epoch=2_000_000_000 + counter["calls"])
            return 0

        monkeypatch.setattr(war_room, "cmd_snapshot_doctor", fake_snapshot_doctor)
        rc = war_room.cmd_launch_trend(argparse.Namespace(sleep=0, window="1d", json=False))
        out = capsys.readouterr().out
        assert rc == 0
        # Diff should report no transitions
        assert "[PASS] no status transitions" in out

    def test_json_mode_emits_composite(self, tmp_path, monkeypatch, capsys):
        """--json mode emits nested 'diff' + 'trend' keys (reuses existing --json shapes)."""
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        counter = {"calls": 0}

        def fake_snapshot_doctor(_args):
            counter["calls"] += 1
            stamp = f"2026-07-10_12000{counter['calls']}"
            _write_fake_snapshot(fake, stamp, {"health": "OK"}, mtime_epoch=2_000_000_000 + counter["calls"])
            return 0

        monkeypatch.setattr(war_room, "cmd_snapshot_doctor", fake_snapshot_doctor)
        rc = war_room.cmd_launch_trend(argparse.Namespace(sleep=0, window="1d", json=True))
        out = capsys.readouterr().out
        # JSON mode prints only the final JSON (no [1/4] markers)
        body = json.loads(out)
        assert "snapshots" in body
        assert body["snapshots"]["a"].endswith(".json")
        assert body["snapshots"]["b"].endswith(".json")
        # diff + trend are nested under their own keys, reusing existing --json shapes
        assert "diff" in body
        assert "trend" in body
        assert body["trend"]["window_days"] == 1
        assert body["trend"]["snapshot_count"] >= 2  # at least the 2 we just wrote

    def test_snapshot_failure_returns_rc_1(self, tmp_path, monkeypatch, capsys):
        """If snapshot A fails, return rc=1 immediately (no diff/trend attempted)."""
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)

        def fake_snapshot_doctor_fails(_args):
            return 1

        monkeypatch.setattr(war_room, "cmd_snapshot_doctor", fake_snapshot_doctor_fails)
        rc = war_room.cmd_launch_trend(argparse.Namespace(sleep=0, window="1d", json=False))
        assert rc == 1
        # Should NOT have reached the diff or trend steps
        out = capsys.readouterr().out
        assert "DIFF A vs B" not in out
        assert "TREND" not in out or "[3/4]" not in out

    def test_aggregate_rc_max(self, tmp_path, monkeypatch, capsys):
        """Return code is max(snapshot_rc, diff_rc, trend_rc) - propagates hard failures."""
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        counter = {"calls": 0}

        def fake_snapshot_doctor(_args):
            counter["calls"] += 1
            stamp = f"2026-07-10_12000{counter['calls']}"
            _write_fake_snapshot(fake, stamp, {"health": "OK"}, mtime_epoch=2_000_000_000 + counter["calls"])
            return 0

        # Make cmd_trend_doctor return rc=1 to test aggregate max
        def fake_trend_doctor(_args):
            return 1

        monkeypatch.setattr(war_room, "cmd_snapshot_doctor", fake_snapshot_doctor)
        monkeypatch.setattr(war_room, "cmd_trend_doctor", fake_trend_doctor)
        rc = war_room.cmd_launch_trend(argparse.Namespace(sleep=0, window="1d", json=False))
        # max(0, 0, 0, 1) = 1
        assert rc == 1

    def test_negative_sleep_returns_fail(self, tmp_path, monkeypatch, capsys):
        """MINOR #2 (cont.19): --sleep must be >= 0; negative values are rejected at the
        entry of cmd_launch_trend (NOT via argparse) because argparse type=int accepts them
        but time.sleep(-1) raises ValueError."""
        _patch_snapshot_dir(monkeypatch, tmp_path)
        # Snapshot must NOT be called (negative sleep should fail fast).
        def fake_snapshot_doctor_should_not_run(_args):
            raise AssertionError("cmd_snapshot_doctor should not be called when --sleep is negative")
        monkeypatch.setattr(war_room, "cmd_snapshot_doctor", fake_snapshot_doctor_should_not_run)
        rc = war_room.cmd_launch_trend(argparse.Namespace(sleep=-5, window="1d", json=False))
        out = capsys.readouterr().out
        assert rc == 1
        assert "[FAIL] --sleep must be >= 0" in out
        assert "-5" in out


# ---------------------------------------------------------------------------
# TestCaptureStdout (cont.20) - locks the _capture_stdout context manager contract
# ---------------------------------------------------------------------------
class TestCaptureStdout:
    """Locks the 3 invariants of _capture_stdout():
      1. captures sys.stdout writes within the context
      2. restores sys.stdout on normal exit
      3. restores sys.stdout on exception (try/finally guarantee)
    """

    def test_captures_stdout_within_context(self):
        import sys as _sys
        with war_room._capture_stdout() as buf:
            print("hello capture")
        assert buf.getvalue() == "hello capture\n"
        # After exit, sys.stdout is restored to the original
        assert _sys.stdout is not buf

    def test_restores_stdout_on_normal_exit(self):
        import sys as _sys
        _original = _sys.stdout
        with war_room._capture_stdout() as buf:
            assert _sys.stdout is buf  # captured during context
        assert _sys.stdout is _original  # restored after context
        assert _sys.stdout is not buf

    def test_restores_stdout_on_exception(self):
        import sys as _sys
        _original = _sys.stdout
        try:
            with war_room._capture_stdout() as buf:
                assert _sys.stdout is buf
                raise RuntimeError("simulated subcommand failure")
        except RuntimeError as _e:
            assert str(_e) == "simulated subcommand failure"
        # Even after an exception, sys.stdout is restored
        assert _sys.stdout is _original
        assert _sys.stdout is not buf
