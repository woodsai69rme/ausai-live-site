"""Direct-IO unit tests for war_room's 7 _section_* helpers (added cont.14).

The cont.13 tests in test_war_room_cmd_doctor.py mocked all 7 _section_* helpers
to isolate cmd_doctor's pipeline logic. This file directly tests the helpers
themselves with real I/O (tmpdirs, controlled mtime via os.utime, monkeypatched
subprocess.run for git) so future contributors cannot break a section's
parsing/math without a regression test catching it.

Mirrors the cont.11/cont.12 contrib pattern: stdlib-only, no external deps.
"""
import argparse
import os
import subprocess
import sys
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import war_room  # noqa: E402


def _ns(**kw):
    return argparse.Namespace(**kw)


# ============================================================
# _section_python -- the trivial one
# ============================================================
class TestSectionPython:
    def test_returns_ok_and_format(self):
        status, detail = war_room._section_python()
        assert status == "OK"
        assert detail.startswith("Python ")
        # Strict format: "Python X.Y.Z" with 3 numeric parts separated by dots
        version_part = detail[len("Python "):]
        parts = version_part.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)
        # Must match sys.version_info triple
        sys_v = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        assert version_part == sys_v


# ============================================================
# _section_tools -- reads Tools/ inventory
# ============================================================
class TestSectionTools:
    def test_missing_tools_dir_is_info(self, monkeypatch):
        # Point USERPROFILE at a tmpdir that has NO Tools/ subdir
        monkeypatch.setenv("USERPROFILE", str(os.path.join(os.getcwd(), "tests", "__nonexistent__")))
        status, detail = war_room._section_tools()
        assert status == "INFO"
        assert "not present" in detail

    def test_tools_with_entries_returns_ok_with_count(self, monkeypatch, tmp_path):
        # Create a fake Tools/ with 4 known entries
        tools = tmp_path / "Tools"
        tools.mkdir()
        (tools / "apktool").mkdir()
        (tools / "jadx").mkdir()
        (tools / "jdk").mkdir()
        (tools / "platform-tools").mkdir()
        monkeypatch.setenv("USERPROFILE", str(tmp_path))
        status, detail = war_room._section_tools()
        assert status == "OK"
        assert "4 entries" in detail
        assert "apktool" in detail
        assert "jdk" in detail

    def test_tools_with_more_than_8_shows_ellipsis(self, monkeypatch, tmp_path):
        tools = tmp_path / "Tools"
        tools.mkdir()
        for i in range(10):
            (tools / f"tool_{i:02d}").mkdir()
        monkeypatch.setenv("USERPROFILE", str(tmp_path))
        status, detail = war_room._section_tools()
        assert status == "OK"
        assert "10 entries" in detail
        assert "..." in detail


# ============================================================
# _section_mobile_csv -- freshness math
# ============================================================
class TestSectionMobileCsv:
    def test_csv_missing_is_info(self, monkeypatch, tmp_path):
        # Move war_room.py's directory to a tmp_path that has no MOBILE_FILTERED.csv
        monkeypatch.setattr(war_room, "__file__", os.path.join(str(tmp_path), "war_room.py"))
        # tmp_path has no MOBILE_FILTERED.csv
        status, detail = war_room._section_mobile_csv()
        assert status == "INFO"
        assert "missing" in detail

    def test_fresh_csv_returns_ok(self, monkeypatch, tmp_path):
        fake_war_room = tmp_path / "war_room.py"
        fake_war_room.write_text("# placeholder so __file__ resolves")
        csv = tmp_path / "MOBILE_FILTERED.csv"
        csv.write_text("DisplayName,matched_terms\nFoo,bar\n")
        # mtime: now (fresh)
        os.utime(csv, (time.time(), time.time()))
        monkeypatch.setattr(war_room, "__file__", str(fake_war_room))
        status, detail = war_room._section_mobile_csv()
        assert status == "OK"
        assert "MOBILE_FILTERED.csv" in detail
        # "X.Xh ago" -- X.X should be < 1.0 since we just created
        assert "ago" in detail

    def test_stale_csv_returns_warn(self, monkeypatch, tmp_path):
        fake_war_room = tmp_path / "war_room.py"
        fake_war_room.write_text("# placeholder")
        csv = tmp_path / "MOBILE_FILTERED.csv"
        csv.write_text("DisplayName,matched_terms\nFoo,bar\n")
        # mtime: 200 hours ago (>168h warn-threshold)
        old_time = time.time() - 200 * 3600
        os.utime(csv, (old_time, old_time))
        monkeypatch.setattr(war_room, "__file__", str(fake_war_room))
        status, detail = war_room._section_mobile_csv()
        assert status == "WARN"
        assert "stale" in detail
        assert "168" in detail


# ============================================================
# _section_health -- parts[2] parsing (the bug fix from cont.13)
# ============================================================
class TestSectionHealth:
    def test_counts_5_up_lines(self, monkeypatch, capsys):
        """cmd_health emits 5 lines; grades each via parts[2]."""
        # Mock cmd_health to print 5 lines exactly like the real one
        def fake_cmd_health(args):
            print("\n  HEALTH PROBE:\n")
            print("  {'SVC':<10} {'URL':<48} {'STATE':<10} {'LATENCY':<10}")
            print("  " + "-" * 70)
            for i in range(5):
                print(f"  svc{i:<8} http://127.0.0.1:999{i}/api/tags     up          {i*10:>5}     ")

        monkeypatch.setattr(war_room, "cmd_health", fake_cmd_health)
        status, detail = war_room._section_health()
        assert status == "OK"
        capsys.readouterr()  # cleanup

    def test_mixed_up_down_returns_warn(self, monkeypatch, capsys):
        # NOTE: latency must use `{42:<10}` not `{'':>5}` -- an empty-string latency in the
        # fake output collapses to 5 spaces dropped by split(), leaving only 3 tokens after
        # split(), failing the len(parts) >= 4 filter and incorrectly skipping a valid "up" line.
        def fake_cmd_health(args):
            print("\n  HEALTH PROBE:\n")
            print(f"  ollama  http://127.0.0.1:11434/api/tags     up          {42:<10}")
            print(f"  comfy   http://127.0.0.1:8188/system_stats  down       {'n/a':<10}")

        monkeypatch.setattr(war_room, "cmd_health", fake_cmd_health)
        status, detail = war_room._section_health()
        assert status == "WARN"  # mixed = iterate mode, not FAIL
        capsys.readouterr()

    def test_all_down_returns_fail(self, monkeypatch, capsys):
        def fake_cmd_health(args):
            print("\n  HEALTH PROBE:\n")
            print(f"  ollama  http://127.0.0.1:11434/api/tags     down       {'n/a':<10}")
            print(f"  comfy   http://127.0.0.1:8188/system_stats  down       {'n/a':<10}")

        monkeypatch.setattr(war_room, "cmd_health", fake_cmd_health)
        status, detail = war_room._section_health()
        assert status == "FAIL"
        capsys.readouterr()

    def test_header_line_filtered_out(self, monkeypatch, capsys):
        """cmd_health prints 'HEALTH PROBE' header -- parts[2] won't be 'up'/'down'."""
        def fake_cmd_health(args):
            print("\n  HEALTH PROBE -- Live Health Probe:\n")
            print("  {'SERVICE':<10} {'URL':<48} {'STATE':<10} {'LATENCY':<10}")
            print("  " + "-" * 78)
            print(f"  ollama    http://127.0.0.1:11434/api/tags     up          {'':>5}")

        monkeypatch.setattr(war_room, "cmd_health", fake_cmd_health)
        status, detail = war_room._section_health()
        # Header doesn't count as up OR down -> up_count=1, down_count=0 -> OK
        assert status == "OK"
        capsys.readouterr()


# ============================================================
# _section_git -- subprocess.run mock for the 4 branches
# ============================================================
class TestSectionGit:
    def test_clean_tree_returns_ok(self, monkeypatch):
        fake = subprocess.CompletedProcess(args=["git"], returncode=0, stdout="", stderr="")
        monkeypatch.setattr(subprocess, "run", lambda *a, **k: fake)
        status, detail = war_room._section_git()
        assert status == "OK"
        assert "clean" in detail.lower()

    def test_uncommitted_returns_info(self, monkeypatch):
        fake = subprocess.CompletedProcess(
            args=["git"], returncode=0,
            stdout=" M war_room.py\n?? new_test.py\n",
            stderr="",
        )
        monkeypatch.setattr(subprocess, "run", lambda *a, **k: fake)
        status, detail = war_room._section_git()
        assert status == "INFO"
        assert "2 uncommitted" in detail

    def test_git_not_on_path_returns_info(self, monkeypatch):
        def raise_fnf(*a, **k):
            raise FileNotFoundError("git not installed")
        monkeypatch.setattr(subprocess, "run", raise_fnf)
        status, detail = war_room._section_git()
        assert status == "INFO"
        assert "not on PATH" in detail

    def test_timeout_returns_warn(self, monkeypatch):
        def raise_timeout(*a, **k):
            raise subprocess.TimeoutExpired(cmd="git", timeout=5)
        monkeypatch.setattr(subprocess, "run", raise_timeout)
        status, detail = war_room._section_git()
        assert status == "WARN"
        assert "TimeoutExpired" in detail


# ============================================================
# _section_validate_tools / _section_validate_mobile -- stdout capture path
# ============================================================
class TestSectionValidateDelegates:
    def test_section_validate_tools_propagates_rc(self, monkeypatch):
        def fake(args):
            print("[PASS] fake tool output")
            return 1  # BROKEN aggregate
        monkeypatch.setattr(war_room, "cmd_validate_tools", fake)
        status, detail = war_room._section_validate_tools()
        assert status == "FAIL"
        assert "[PASS] fake tool output" in detail

    def test_section_validate_mobile_returns_ok_on_rc0(self, monkeypatch):
        def fake(args):
            print("[PASS] 4 dynamic tiles detected")
            return 0
        monkeypatch.setattr(war_room, "cmd_validate_mobile", fake)
        status, detail = war_room._section_validate_mobile()
        assert status == "OK"
        assert "4 dynamic tiles" in detail

    def test_section_validate_mobile_returns_fail_on_rc1(self, monkeypatch):
        def fake(args):
            print("[FAIL] loader bug")
            return 1
        monkeypatch.setattr(war_room, "cmd_validate_mobile", fake)
        status, detail = war_room._section_validate_mobile()
        assert status == "FAIL"
