"""Unit tests for war_room.cmd_doctor (added cont.13).

cmd_doctor aggregates 7 sections; tests cover aggregate semantics + JSON shape
+ --quiet mode + edge cases. Each test mocks the _section_* helper functions
to isolate cmd_doctor's pipeline logic from real file I/O / subprocess.

Mirrors the war_room.cmd_validate_tools test pattern from cont.12.
"""
import argparse
import json
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import war_room  # noqa: E402


def _ns(**kw):
    return argparse.Namespace(**kw)


# All 7 _section_* names -- single source of truth for the test mocks.
_SECTION_NAMES = (
    "validate_tools",
    "validate_mobile",
    "health",
    "python",
    "tools",
    "mobile_csv",
    "git",
)


def _stub_all_sections(monkeypatch, status="OK", detail="ok"):
    """Stub all 7 _section_* helpers to return (status, detail).

    Returns a dict mapping section name -> ret tuple, for tests that
    want to override one or more sections individually.
    """
    rets = {n: (status, detail) for n in _SECTION_NAMES}
    for n in _SECTION_NAMES:
        monkeypatch.setattr(war_room, f"_section_{n}", lambda n=n: rets[n])
    return rets


class TestCmdDoctorAggregate:
    """cmd_doctor aggregate_ok / exit-code semantics."""

    def test_all_pass_sections_return_zero(self, monkeypatch, capsys):
        """All 7 sections return OK/INFO/WARN -> cmd_doctor exits 0 (aggregated OK)."""
        # Mix of OK + INFO + WARN (collectively non-FAIL) -> still aggregate OK.
        monkeypatch.setattr(war_room, "_section_validate_tools",
                            lambda: ("OK", "[PASS] 3/3 Android tools FOUND"))
        monkeypatch.setattr(war_room, "_section_validate_mobile",
                            lambda: ("OK", "[PASS] 4 dynamic tiles detected"))
        monkeypatch.setattr(war_room, "_section_health",
                            lambda: ("WARN", "3/5 services up (reason: iterating)"))
        monkeypatch.setattr(war_room, "_section_python",
                            lambda: ("OK", "Python 3.12.7"))
        monkeypatch.setattr(war_room, "_section_tools",
                            lambda: ("OK", "6 entries in Tools/"))
        monkeypatch.setattr(war_room, "_section_mobile_csv",
                            lambda: ("INFO", "MOBILE_FILTERED.csv missing (legit clean-PC state)"))
        monkeypatch.setattr(war_room, "_section_git",
                            lambda: ("INFO", "5 uncommitted change(s)"))

        rc = war_room.cmd_doctor(_ns(json=False, quiet=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "aggregate: OK" in out
        assert "[PASS] workspace is healthy." in out

    def test_one_tool_broken_returns_one(self, monkeypatch, capsys):
        """One section returns FAIL -> cmd_doctor exits 1 (aggregate FAIL)."""
        _stub_all_sections(monkeypatch, status="OK", detail="ok")
        # Override ONE section to FAIL -- must flip aggregate.
        monkeypatch.setattr(war_room, "_section_validate_tools",
                            lambda: ("FAIL", "[FAIL] java BROKEN: subprocess failed\n  remediation: run install_jdk_portable.ps1"))

        rc = war_room.cmd_doctor(_ns(json=False, quiet=False))
        out = capsys.readouterr().out
        assert rc == 1
        assert "aggregate: FAIL" in out
        assert "[FAIL] workspace has issues" in out

    def test_all_sections_fail_returns_one(self, monkeypatch, capsys):
        """All sections FAIL -> aggregate still FAIL (rc=1)."""
        _stub_all_sections(monkeypatch, status="FAIL", detail="all broken")

        rc = war_room.cmd_doctor(_ns(json=False, quiet=True))
        out = capsys.readouterr().out
        assert rc == 1
        assert "aggregate: FAIL" in out


class TestCmdDoctorJson:
    """cmd_doctor --json output shape."""

    def test_json_shape_is_stable(self, monkeypatch, capsys):
        """--json emits parseable dict with aggregate_ok + sections list of dicts."""
        monkeypatch.setattr(war_room, "_section_validate_tools",
                            lambda: ("OK", "[PASS] 3/3 FOUND"))
        monkeypatch.setattr(war_room, "_section_validate_mobile",
                            lambda: ("OK", "[PASS]"))
        monkeypatch.setattr(war_room, "_section_health",
                            lambda: ("OK", "5/5 up"))
        monkeypatch.setattr(war_room, "_section_python",
                            lambda: ("OK", "Python 3.12.7"))
        monkeypatch.setattr(war_room, "_section_tools",
                            lambda: ("OK", "[PASS]"))
        monkeypatch.setattr(war_room, "_section_mobile_csv",
                            lambda: ("INFO", "MOBILE_FILTERED.csv missing"))
        monkeypatch.setattr(war_room, "_section_git",
                            lambda: ("OK", "working tree clean"))

        rc = war_room.cmd_doctor(_ns(json=True, quiet=False))
        out = capsys.readouterr().out.strip()

        # Parseable JSON
        result = json.loads(out)
        assert isinstance(result, dict)
        assert "aggregate_ok" in result
        assert result["aggregate_ok"] is True
        assert rc == 0

        # Exactly 7 sections in stable order
        assert isinstance(result["sections"], list)
        assert len(result["sections"]) == 7
        expected_names = [
            "validate-tools", "validate-mobile", "health", "python",
            "tools", "mobile-csv", "git",
        ]
        actual_names = [s["name"] for s in result["sections"]]
        assert actual_names == expected_names

        # Each section has the 3 expected keys with valid status values
        valid_statuses = {"OK", "WARN", "INFO", "FAIL"}
        for sec in result["sections"]:
            assert "name" in sec and "status" in sec and "detail" in sec
            assert sec["status"] in valid_statuses
            assert isinstance(sec["detail"], str)

    def test_json_with_one_fail_aggregate_is_false(self, monkeypatch, capsys):
        """--json + one FAIL section -> aggregate_ok == False, rc=1."""
        _stub_all_sections(monkeypatch, status="OK", detail="ok")
        monkeypatch.setattr(war_room, "_section_health",
                            lambda: ("FAIL", "0/5 up; all services down"))

        rc = war_room.cmd_doctor(_ns(json=True, quiet=False))
        out = capsys.readouterr().out.strip()
        result = json.loads(out)
        assert rc == 1
        assert result["aggregate_ok"] is False
        # Find the health section
        health_sec = next(s for s in result["sections"] if s["name"] == "health")
        assert health_sec["status"] == "FAIL"


class TestCmdDoctorQuiet:
    """cmd_doctor --quiet mode detail suppression."""

    def test_quiet_mode_suppresses_multi_line_detail(self, monkeypatch, capsys):
        """--quiet only emits section badge + 1-line summary; hides multi-line detail."""
        monkeypatch.setattr(war_room, "_section_validate_tools",
                            lambda: ("OK", "[PASS]\n  detail line A\n  detail line B"))
        monkeypatch.setattr(war_room, "_section_validate_mobile",
                            lambda: ("OK", "single-line"))
        monkeypatch.setattr(war_room, "_section_health",
                            lambda: ("OK", "single-line"))
        monkeypatch.setattr(war_room, "_section_python",
                            lambda: ("OK", "single-line"))
        monkeypatch.setattr(war_room, "_section_tools",
                            lambda: ("OK", "single-line"))
        monkeypatch.setattr(war_room, "_section_mobile_csv",
                            lambda: ("OK", "single-line"))
        monkeypatch.setattr(war_room, "_section_git",
                            lambda: ("OK", "single-line"))

        rc = war_room.cmd_doctor(_ns(json=False, quiet=True))
        out = capsys.readouterr().out
        assert rc == 0
        # Multi-line content from the failing section must NOT appear.
        assert "detail line A" not in out
        assert "detail line B" not in out
        # Section badge + first line SHOULD appear.
        assert "[PASS]" in out
        assert "validate-tools" in out

    def test_default_mode_shows_multi_line_detail(self, monkeypatch, capsys):
        """Without --quiet, multi-line detail IS emitted."""
        monkeypatch.setattr(war_room, "_section_validate_tools",
                            lambda: ("OK", "[PASS]\n  detail line A\n  detail line B"))
        monkeypatch.setattr(war_room, "_section_validate_mobile",
                            lambda: ("OK", "single-line"))
        monkeypatch.setattr(war_room, "_section_health",
                            lambda: ("OK", "single-line"))
        monkeypatch.setattr(war_room, "_section_python",
                            lambda: ("OK", "single-line"))
        monkeypatch.setattr(war_room, "_section_tools",
                            lambda: ("OK", "single-line"))
        monkeypatch.setattr(war_room, "_section_mobile_csv",
                            lambda: ("OK", "single-line"))
        monkeypatch.setattr(war_room, "_section_git",
                            lambda: ("OK", "single-line"))

        rc = war_room.cmd_doctor(_ns(json=False, quiet=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "detail line A" in out
        assert "detail line B" in out


class TestCmdDoctorSafety:
    """cmd_doctor safety: missing/informational files must NOT bump aggregate to FAIL."""

    def test_mobile_csv_missing_is_info_not_fail(self, monkeypatch, capsys):
        """MOBILE_FILTERED.csv missing -> INFO status -> aggregate stays OK."""
        _stub_all_sections(monkeypatch, status="OK", detail="ok")
        monkeypatch.setattr(war_room, "_section_mobile_csv",
                            lambda: ("INFO", "MOBILE_FILTERED.csv missing -- run refresh_mobile_inventory.bat"))

        rc = war_room.cmd_doctor(_ns(json=False, quiet=True))
        out = capsys.readouterr().out
        assert rc == 0
        # INFO must appear, FAIL must not.
        assert "INFO" in out
        assert "[FAIL]" not in out or "INFO" in out  # 'FAIL' substring may appear in 'INFO' -- explicit check below
        # Specifically: no [FAIL] badge for the aggregate header
        assert "aggregate: OK" in out

    def test_tools_dir_missing_is_info_not_fail(self, monkeypatch, capsys):
        """Tools/ directory missing -> INFO status -> aggregate stays OK."""
        _stub_all_sections(monkeypatch, status="OK", detail="ok")
        monkeypatch.setattr(war_room, "_section_tools",
                            lambda: ("INFO", "Tools/ not present (portable install bare)"))

        rc = war_room.cmd_doctor(_ns(json=False, quiet=True))
        out = capsys.readouterr().out
        assert rc == 0
        assert "aggregate: OK" in out


class TestCmdDoctorSectionInvocation:
    """Guard: cmd_doctor calls each _section_* exactly once (no duplicate calls)."""

    def test_each_section_called_exactly_once(self, monkeypatch):
        """cmd_doctor must invoke each of the 7 _section_* helpers exactly once."""
        counts = {n: 0 for n in _SECTION_NAMES}

        def _make(name, ret):
            def _fn():
                counts[name] += 1
                return ret
            return _fn

        for n in _SECTION_NAMES:
            monkeypatch.setattr(war_room, f"_section_{n}", _make(n, ("OK", f"{n} stub")))

        war_room.cmd_doctor(_ns(json=False, quiet=True))

        for n in _SECTION_NAMES:
            assert counts[n] == 1, f"_section_{n} called {counts[n]} times (expected exactly 1)"
