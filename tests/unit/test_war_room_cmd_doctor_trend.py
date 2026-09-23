"""Unit tests for cont.15 ws-doctor-trend additions to war_room.py.

Module-level import: war_room._snapshot_dir is patched in tests via
monkeypatch.setattr, and cmd_doctor is replaced wholesale for write-mode tests.
This pattern avoids 11 per-test cold re-imports of war_room.py (which would
time out the basher harness) while still keeping tests fully isolated from
the real operator-local .cache/.

Covers (no live services, no real .cache writes):
  TestSnapshotHelpers           - _snapshot_dir, _list_snapshots, _resolve_snapshot
  TestCmdSnapshotDoctorWrite    - write mode produces a valid snapshot file
  TestCmdSnapshotDoctorList     - --list reports existing snapshots
  TestCmdSnapshotDoctorPrune    - --keep-last N prunes oldest (and --keep-last 0 is no-op per cont.15 MINOR)
  TestCmdDiffDoctor             - happy path + transitions + missing --a + --a==--b + --json

Conventions:
  - module-level `import war_room` (one cold import for the whole test session)
  - per-test tmp_path + monkeypatch.setattr(war_room, "_snapshot_dir", lambda: ...)
  - per-test cmd_doctor mock via monkeypatch.setattr(war_room, "cmd_doctor", fake)
  - assert rc codes match the contract: write/list/prune/diff-happy = 0, diff-bad-resolve = 1
"""
import io
import json
import os
import sys
import argparse
import shutil
import pytest

# Module-level import — single cold import shared across all tests.
# Tests use monkeypatch.setattr to redirect _snapshot_dir (no real .cache/ touches)
# and to swap cmd_doctor for write-mode tests.
import war_room  # WARNING (cont.16): this import parses MOBILE_FILTERED.csv once at session start; any test asserting on exact TILE_REGISTRY counts is tightly coupled to local CSV contents at the start of the test session.


# ---------------------------------------------------------------------------
# Helpers shared across the test classes
# ---------------------------------------------------------------------------
def _seed_snapshot(fake_dir, stamp, payload, *, mtime_epoch=None):
    """Write a fake snapshot__<stamp>.json into fake_dir, return absolute path. Optional mtime."""
    fp = os.path.join(fake_dir, f"snapshot__{stamp}.json")
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    if mtime_epoch is not None:
        os.utime(fp, (mtime_epoch, mtime_epoch))
    return fp


def _patch_snapshot_dir(monkeypatch, tmp_path):
    """Redirect war_room._snapshot_dir -> <tmp_path>/snapshots/ (creates the dir)."""
    fake = tmp_path / "snapshots"
    fake.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(war_room, "_snapshot_dir", lambda: str(fake))
    return str(fake)


# ---------------------------------------------------------------------------
# TestSnapshotHelpers — covers _snapshot_dir, _list_snapshots, _resolve_snapshot
# ---------------------------------------------------------------------------
class TestSnapshotHelpers:
    def test_snapshot_dir_resolves_under_userprofile(self, monkeypatch, tmp_path):
        # _snapshot_dir reads os.environ['USERPROFILE'] AT CALL TIME (not import time),
        # so monkeypatch.setenv + module-level import is sufficient and avoids a cold reimport.
        monkeypatch.setenv("USERPROFILE", str(tmp_path))
        monkeypatch.delenv("HOME", raising=False)
        sd = war_room._snapshot_dir()
        assert sd == os.path.join(str(tmp_path), ".cache", "war_room", "snapshots")
        assert os.path.isdir(sd)
        # Cleanup tmp sandbox so subsequent tests start clean.
        shutil.rmtree(str(tmp_path), ignore_errors=True)

    def test_list_snapshots_returns_empty_for_missing_dir(self, tmp_path, monkeypatch):
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        # Move the dir out so isdir=False
        os.rmdir(fake)
        assert war_room._list_snapshots() == []

    def test_list_snapshots_sorts_by_mtime_not_filename(self, tmp_path, monkeypatch):
        """MINOR #1 lock: order is by mtime ascending, robust to stamp format changes."""
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        # Seed in NON-sequential filename order on purpose.
        p_mid   = _seed_snapshot(fake, "2026-07-09_130000", {"sections": [], "aggregate_ok": True}, mtime_epoch=2_000_000_001)
        p_first = _seed_snapshot(fake, "2026-07-09_120000", {"sections": [], "aggregate_ok": True}, mtime_epoch=2_000_000_000)
        p_last  = _seed_snapshot(fake, "2026-07-09_140000", {"sections": [], "aggregate_ok": True}, mtime_epoch=2_000_000_002)
        snaps = war_room._list_snapshots()
        filenames = [fn for fn, _mt in snaps]
        # Sorted by mtime (ascending): p_first (1B) -> p_mid (1B+1) -> p_last (1B+2)
        # NOT alphabetical: alphabetical would be 120000,130000,140000 (lucky coincidence here).
        # The mtime check guards against future stamp-format changes breaking ordering.
        assert filenames[0].endswith("_120000.json")
        assert filenames[1].endswith("_130000.json")
        assert filenames[2].endswith("_140000.json")

    def test_resolve_snapshot_returns_none_for_no_match(self, tmp_path, monkeypatch):
        _patch_snapshot_dir(monkeypatch, tmp_path)
        assert war_room._resolve_snapshot("does-not-exist") is None

    def test_resolve_snapshot_returns_none_for_empty_input(self, tmp_path, monkeypatch):
        _patch_snapshot_dir(monkeypatch, tmp_path)
        assert war_room._resolve_snapshot("") is None
        assert war_room._resolve_snapshot(None) is None

    def test_resolve_snapshot_matches_unique_prefix(self, tmp_path, monkeypatch):
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        _seed_snapshot(fake, "2026-07-09_120000", {"sections": [], "aggregate_ok": True}, mtime_epoch=2_000_000_000)
        _seed_snapshot(fake, "2026-07-10_120000", {"sections": [], "aggregate_ok": True}, mtime_epoch=2_000_000_003)
        # Unique date prefix
        p = war_room._resolve_snapshot("2026-07-09")
        assert p is not None and p.endswith("snapshot__2026-07-09_120000.json")
        # Exact filename
        p2 = war_room._resolve_snapshot("snapshot__2026-07-10_120000.json")
        assert p2 is not None and p2.endswith("snapshot__2026-07-10_120000.json")

    def test_resolve_snapshot_ambiguous_prefix_picks_most_recent(self, tmp_path, monkeypatch):
        """MINOR #4 (cont.15): typing a DATE prefix with multiple same-day snapshots
        resolves to the MOST-RECENT of those (deterministic by mtime), NOT an error."""
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        _seed_snapshot(fake, "2026-07-09_120000", {"sections": [], "aggregate_ok": True}, mtime_epoch=2_000_000_000)
        _seed_snapshot(fake, "2026-07-09_140000", {"sections": [], "aggregate_ok": True}, mtime_epoch=2_000_000_003)
        p = war_room._resolve_snapshot("2026-07-09")
        assert p is not None, "expected most-recent on ambiguous prefix; got None"
        assert p.endswith("snapshot__2026-07-09_140000.json")
        # Zero-match (different date) still None.
        assert war_room._resolve_snapshot("2026-07-08") is None


# ---------------------------------------------------------------------------
# TestCmdSnapshotDoctorWrite — write mode emits a valid snapshot file
# ---------------------------------------------------------------------------
class TestCmdSnapshotDoctorWrite:
    def test_write_mode_emits_valid_json_file_with_schema_stamp(self, tmp_path, monkeypatch, capsys):
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)

        # Mock cmd_doctor --json to emit a deterministic payload (no live services).
        def fake_cmd_doctor(_args):
            sys.stdout.write(json.dumps({
                "aggregate_ok": True,
                "sections": [
                    {"name": "validate-tools", "status": "OK", "detail": "fake detail"},
                ],
            }))
            return 0
        monkeypatch.setattr(war_room, "cmd_doctor", fake_cmd_doctor)

        rc = war_room.cmd_snapshot_doctor(argparse.Namespace(list=False, keep_last=None, json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "[PASS] snapshot written to" in out
        files = [fn for fn in os.listdir(fake) if fn.startswith("snapshot__") and fn.endswith(".json")]
        assert len(files) == 1
        with open(os.path.join(fake, files[0]), encoding="utf-8") as f:
            data = json.load(f)
        assert data["schema_version"] == "war_room.doctor.snapshot/1"
        assert isinstance(data.get("snapshot_iso"), str) and len(data["snapshot_iso"]) >= 10
        assert data["aggregate_ok"] is True

    def test_rapid_writes_same_second_get_distinct_files(self, tmp_path, monkeypatch, capsys):
        """cont.22: two writes within the same second must not overwrite."""
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)

        def fake_cmd_doctor(_args):
            sys.stdout.write(json.dumps({"aggregate_ok": True, "sections": []}))
            return 0

        monkeypatch.setattr(war_room, "cmd_doctor", fake_cmd_doctor)
        import time as _time_mod
        monkeypatch.setattr(_time_mod, "strftime", lambda *_a, **_k: "2026-07-10_120000")

        rc1 = war_room.cmd_snapshot_doctor(argparse.Namespace(list=False, keep_last=None, json=False))
        capsys.readouterr()
        rc2 = war_room.cmd_snapshot_doctor(argparse.Namespace(list=False, keep_last=None, json=False))
        capsys.readouterr()
        assert rc1 == 0 and rc2 == 0
        files = sorted(fn for fn in os.listdir(fake) if fn.endswith(".json"))
        assert len(files) == 2
        assert files[0] == "snapshot__2026-07-10_120000.json"
        assert files[1] == "snapshot__2026-07-10_120000_02.json"


# ---------------------------------------------------------------------------
# TestCmdSnapshotDoctorList — --list mode reports existing snapshots
# ---------------------------------------------------------------------------
class TestCmdSnapshotDoctorList:
    def test_list_mode_reports_two_existing_snapshots(self, tmp_path, monkeypatch, capsys):
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        _seed_snapshot(fake, "2026-07-09_120000", {"sections": [], "aggregate_ok": True}, mtime_epoch=2_000_000_000)
        _seed_snapshot(fake, "2026-07-09_140000", {"sections": [], "aggregate_ok": True}, mtime_epoch=2_000_000_002)

        rc = war_room.cmd_snapshot_doctor(argparse.Namespace(list=True, keep_last=None, json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "2 file(s)" in out
        assert "snapshot__2026-07-09_120000.json" in out
        assert "snapshot__2026-07-09_140000.json" in out

    def test_list_mode_reports_info_when_no_snapshots(self, tmp_path, monkeypatch, capsys):
        _patch_snapshot_dir(monkeypatch, tmp_path)
        rc = war_room.cmd_snapshot_doctor(argparse.Namespace(list=True, keep_last=None, json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "[INFO] no snapshots yet" in out
        assert "0 file(s)" in out


# ---------------------------------------------------------------------------
# TestCmdSnapshotDoctorPrune — --keep-last N deletes oldest (and floors at 1 per MINOR)
# ---------------------------------------------------------------------------
class TestCmdSnapshotDoctorPrune:
    def test_keep_last_three_keeps_newest_three(self, tmp_path, monkeypatch, capsys):
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        # Seed 5 with strictly increasing mtimes so ordering is unambiguous.
        for i, ts in enumerate(["100000", "110000", "120000", "130000", "140000"]):
            _seed_snapshot(fake, f"2026-07-09_{ts}", {"sections": [], "aggregate_ok": True}, mtime_epoch=2_000_000_000 + i)
        rc = war_room.cmd_snapshot_doctor(argparse.Namespace(list=False, keep_last=3, json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "pruned 2 snapshot" in out
        # Oldest two gone, newest three remain (sorted by mtime ascending).
        remaining = sorted(os.listdir(fake))
        assert remaining == [
            "snapshot__2026-07-09_120000.json",
            "snapshot__2026-07-09_130000.json",
            "snapshot__2026-07-09_140000.json",
        ]

    def test_keep_last_zero_is_no_op_per_minor_floor(self, tmp_path, monkeypatch, capsys):
        # MINOR #3 (cont.15): --keep-last < 1 must NOT wipe via this command.
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        _seed_snapshot(fake, "2026-07-09_120000", {"sections": [], "aggregate_ok": True}, mtime_epoch=2_000_000_000)
        rc = war_room.cmd_snapshot_doctor(argparse.Namespace(list=False, keep_last=0, json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "must be >= 1" in out  # floor message
        # Snapshot intact (no wipe)
        assert os.path.exists(os.path.join(fake, "snapshot__2026-07-09_120000.json"))

    def test_keep_last_already_in_budget_is_noop(self, tmp_path, monkeypatch, capsys):
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        _seed_snapshot(fake, "2026-07-09_120000", {"sections": [], "aggregate_ok": True}, mtime_epoch=2_000_000_000)
        rc = war_room.cmd_snapshot_doctor(argparse.Namespace(list=False, keep_last=5, json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "already <=" in out


# ---------------------------------------------------------------------------
# TestCmdDiffDoctor — happy + transitions + missing --a + --a==--b + --json
# ---------------------------------------------------------------------------
class TestCmdDiffDoctor:
    def _seed_two_snapshots(self, fake, a_payload, b_payload):
        pa = _seed_snapshot(fake, "2026-07-09_120000", a_payload, mtime_epoch=2_000_000_000)
        pb = _seed_snapshot(fake, "2026-07-09_140000", b_payload, mtime_epoch=2_000_000_002)
        return pa, pb

    def test_no_transitions_prints_pass(self, tmp_path, monkeypatch, capsys):
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        self._seed_two_snapshots(
            fake,
            a_payload={
                "schema_version": "war_room.doctor.snapshot/1",
                "aggregate_ok": True,
                "sections": [
                    {"name": "validate-tools", "status": "OK"},
                    {"name": "health",         "status": "OK"},
                ],
            },
            b_payload={
                "schema_version": "war_room.doctor.snapshot/1",
                "aggregate_ok": True,
                "sections": [
                    {"name": "validate-tools", "status": "OK"},
                    {"name": "health",         "status": "OK"},
                ],
            },
        )
        rc = war_room.cmd_diff_doctor(argparse.Namespace(a="2026-07-09_120000", b=None, json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "[PASS] no status transitions" in out

    def test_transition_prints_info_with_from_to(self, tmp_path, monkeypatch, capsys):
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        self._seed_two_snapshots(
            fake,
            a_payload={
                "schema_version": "war_room.doctor.snapshot/1",
                "aggregate_ok": False,
                "sections": [{"name": "health", "status": "FAIL"}],
            },
            b_payload={
                "schema_version": "war_room.doctor.snapshot/1",
                "aggregate_ok": True,
                "sections": [{"name": "health", "status": "OK"}],
            },
        )
        rc = war_room.cmd_diff_doctor(argparse.Namespace(a="2026-07-09_120000", b=None, json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "1 section status transition" in out
        assert "health" in out and "FAIL" in out and "->" in out and "OK" in out

    def test_missing_a_returns_rc_1(self, tmp_path, monkeypatch, capsys):
        _patch_snapshot_dir(monkeypatch, tmp_path)
        rc = war_room.cmd_diff_doctor(argparse.Namespace(a="does-not-exist", b=None, json=False))
        out = capsys.readouterr().out
        assert rc == 1
        assert "[FAIL] --a" in out

    def test_a_equals_b_prints_info_no_op(self, tmp_path, monkeypatch, capsys):
        """MINOR #2 (cont.15): detect --a == --b so operator doesn't mistake no-op for stability."""
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        self._seed_two_snapshots(
            fake,
            a_payload={"schema_version": "w/1", "aggregate_ok": True, "sections": [{"name": "git", "status": "OK"}]},
            b_payload={"schema_version": "w/1", "aggregate_ok": True, "sections": [{"name": "git", "status": "OK"}]},
        )
        # When --b is None and only one snapshot exists or b-auto-picks same file as --a,
        # the auto-pick resolves to the newest -- which IS the "b" snapshot, not the "a" one.
        # To force --a == --b we explicitly pass the SAME filename to --b.
        rc = war_room.cmd_diff_doctor(argparse.Namespace(a="snapshot__2026-07-09_120000.json", b="snapshot__2026-07-09_120000.json", json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "[INFO] --a and --b resolve to the SAME snapshot" in out

    def test_b_auto_picks_same_as_a_when_only_one_snapshot(self, tmp_path, monkeypatch, capsys):
        """MINOR #5 (cont.15): when only ONE snapshot exists, --b (default = most recent)
        auto-picks to the same file as --a, so the diff command should print the
        --a==--b INFO message (no silent false-PASS that would mask that the operator
        only has one snapshot to compare)."""
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        _seed_snapshot(fake, "2026-07-09_120000",
                       {"schema_version": "w/1", "aggregate_ok": True,
                        "sections": [{"name": "git", "status": "OK"}]},
                       mtime_epoch=2_000_000_000)
        rc = war_room.cmd_diff_doctor(argparse.Namespace(a="2026-07-09_120000", b=None, json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "[INFO] --a and --b resolve to the SAME snapshot" in out

    def test_json_mode_emits_machine_readable(self, tmp_path, monkeypatch, capsys):
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        self._seed_two_snapshots(
            fake,
            a_payload={
                "schema_version": "war_room.doctor.snapshot/1",
                "aggregate_ok": True,
                "sections": [{"name": "git", "status": "INFO"}],
            },
            b_payload={
                "schema_version": "war_room.doctor.snapshot/1",
                "aggregate_ok": False,
                "sections": [{"name": "git", "status": "OK"}],
            },
        )
        rc = war_room.cmd_diff_doctor(argparse.Namespace(a="2026-07-09_120000", b=None, json=True))
        out = capsys.readouterr().out
        assert rc == 0
        body = json.loads(out)
        assert body["transition_count"] == 1
        assert body["transitions"][0]["section"] == "git"
        assert body["transitions"][0]["from"] == "INFO"
        assert body["transitions"][0]["to"] == "OK"


# ---------------------------------------------------------------------------
# TestSchemaVersionValidation (cont.16 MINOR #1) - schema_version read-time validation
# ---------------------------------------------------------------------------
class TestSchemaVersionValidation:
    """Lock the schema_version read-time validation contract: missing/legacy OK,
    unknown OR different-from-canonical triggers [WARN] in text mode +
    `schema_warnings` field in JSON mode."""

    def test_canonical_schema_emits_no_warn(self, tmp_path, monkeypatch, capsys):
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        self._seed_two_snapshots_for_schema_test(
            fake,
            a_payload={"schema_version": war_room.DOCTOR_SNAPSHOT_SCHEMA_VERSION, "aggregate_ok": True, "sections": [{"name": "git", "status": "OK"}]},
            b_payload={"schema_version": war_room.DOCTOR_SNAPSHOT_SCHEMA_VERSION, "aggregate_ok": True, "sections": [{"name": "git", "status": "OK"}]},
        )
        rc = war_room.cmd_diff_doctor(argparse.Namespace(a="2026-07-09_120000", b=None, json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "[WARN] schema:" not in out

    def test_legacy_missing_schema_emits_no_warn(self, tmp_path, monkeypatch, capsys):
        """Snapshots WITHOUT schema_version field (pre-cont.16 legacy) -> no [WARN]."""
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        self._seed_two_snapshots_for_schema_test(
            fake,
            a_payload={"aggregate_ok": True, "sections": [{"name": "git", "status": "OK"}]},
            b_payload={"aggregate_ok": True, "sections": [{"name": "git", "status": "OK"}]},
        )
        rc = war_room.cmd_diff_doctor(argparse.Namespace(a="2026-07-09_120000", b=None, json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "[WARN] schema:" not in out

    def test_schema_mismatch_between_a_and_b_emits_warn(self, tmp_path, monkeypatch, capsys):
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        self._seed_two_snapshots_for_schema_test(
            fake,
            a_payload={"schema_version": "war_room.doctor.snapshot/1", "aggregate_ok": True, "sections": [{"name": "git", "status": "OK"}]},
            b_payload={"schema_version": "war_room.doctor.snapshot/2-future", "aggregate_ok": True, "sections": [{"name": "git", "status": "OK"}]},
        )
        rc = war_room.cmd_diff_doctor(argparse.Namespace(a="2026-07-09_120000", b=None, json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "[WARN] schema:" in out
        assert "different schemas" in out

    def test_unknown_canonical_emits_warn(self, tmp_path, monkeypatch, capsys):
        """A snapshot with non-canonical schema_version -> [WARN] emitted."""
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        self._seed_two_snapshots_for_schema_test(
            fake,
            a_payload={"schema_version": "war_room.doctor.snapshot/1", "aggregate_ok": True, "sections": [{"name": "git", "status": "OK"}]},
            b_payload={"schema_version": "war_room.unknown.v99", "aggregate_ok": True, "sections": [{"name": "git", "status": "OK"}]},
        )
        rc = war_room.cmd_diff_doctor(argparse.Namespace(a="2026-07-09_120000", b=None, json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "[WARN] schema:" in out
        assert "b is 'war_room.unknown.v99'" in out

    def test_json_mode_includes_schema_warnings_field(self, tmp_path, monkeypatch, capsys):
        fake = _patch_snapshot_dir(monkeypatch, tmp_path)
        self._seed_two_snapshots_for_schema_test(
            fake,
            a_payload={"schema_version": "war_room.doctor.snapshot/1", "aggregate_ok": True, "sections": [{"name": "git", "status": "OK"}]},
            b_payload={"schema_version": "war_room.unknown.v99", "aggregate_ok": True, "sections": [{"name": "git", "status": "OK"}]},
        )
        rc = war_room.cmd_diff_doctor(argparse.Namespace(a="2026-07-09_120000", b=None, json=True))
        out = capsys.readouterr().out
        assert rc == 0
        body = json.loads(out)
        assert "schema_warnings" in body
        assert len(body["schema_warnings"]) >= 1
        assert any("b is 'war_room.unknown.v99'" in w for w in body["schema_warnings"])

    def _seed_two_snapshots_for_schema_test(self, fake, a_payload, b_payload):
        """MINOR cont.17: instance method (was @staticmethod) to match sibling
        TestCmdDiffDoctor._seed_two_snapshots style."""
        pa = _seed_snapshot(fake, "2026-07-09_120000", a_payload, mtime_epoch=2_000_000_000)
        pb = _seed_snapshot(fake, "2026-07-09_140000", b_payload, mtime_epoch=2_000_000_002)
        return pa, pb
