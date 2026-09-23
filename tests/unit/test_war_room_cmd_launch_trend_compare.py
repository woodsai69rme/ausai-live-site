"""Unit tests for cont.22 launch-trend-compare subcommand.

Covers (no live services, mock-based, real tmpdir I/O):
  - STABLE verdict (no MORE_FLAPPING): subprocess.run NOT called, no alert fired
  - FLAPPING verdict: subprocess.run IS called with opt_d_alerts.py + formatted --msg
  - --emit-report writes .md + .json to outbox/trend_reports/ with correct content
  - Invalid --a (0d) propagates rc=1 (no subprocess, no file writes)
  - Invalid --b (0d) propagates rc=1 (no subprocess, no file writes)
  - --json mode emits full composite payload (8 keys: payload + degraded_count + ...)

Pattern: patch `war_room.cmd_trend_compare` to print a controlled JSON payload
to stdout (which cmd_launch_trend_compare captures via _capture_stdout), then
patch `subprocess.run` to verify opt_d_alerts is/isn't invoked.

Why mock-based (not snapshot-based like trend-compare tests):
  cmd_launch_trend_compare WRAPS cmd_trend_compare -- the inner verdict logic
  is already covered by test_war_room_cmd_trend_compare.py. These tests focus
  on the wrapper's responsibilities: JSON parsing, degraded-set filtering, file
  emission, conditional subprocess fanout, and --json composite shape.
"""
import argparse
import json
import os
import sys
from unittest import mock

import pytest

import war_room


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _make_payload(verdicts):
    """Build a cmd_trend_compare --json shaped payload.

    verdicts: dict mapping section_name -> 'MORE_FLAPPING' | 'STABLE' | 'MORE_STABLE'
    """
    sections = {}
    for name, v in verdicts.items():
        # Pick rate_a/rate_b numbers consistent with the verdict.
        if v == "MORE_FLAPPING":
            rate_a, rate_b = 2.0, 0.5
        elif v == "MORE_STABLE":
            rate_a, rate_b = 0.5, 2.0
        else:  # STABLE
            rate_a, rate_b = 1.0, 1.0
        sections[name] = {
            "transitions_a": int(rate_a * 1),  # 1d window
            "transitions_b": int(rate_b * 7),  # 7d window
            "rate_a_per_day": rate_a,
            "rate_b_per_day": rate_b,
            "verdict": v,
        }
    return {
        "window_a_days": 1,
        "window_b_days": 7,
        "snapshot_count_a": 5,
        "snapshot_count_b": 20,
        "sections": sections,
    }


def _patch_trend_compare(monkeypatch, payload):
    """Make war_room.cmd_trend_compare print the given JSON payload + return 0.

    The wrapper uses _capture_stdout to read what cmd_trend_compare prints, so
    we just print to the real sys.stdout and return 0.
    """
    def fake(args):
        print(json.dumps(payload))
        return 0
    monkeypatch.setattr(war_room, "cmd_trend_compare", fake)


def _patch_outbox_dir(monkeypatch, tmp_path):
    """Redirect outbox to a tmp dir so test runs don't pollute real SLEEP_TRIPLE/outbox."""
    fake_outbox = tmp_path / "outbox"
    fake_outbox.mkdir(parents=True, exist_ok=True)
    # The wrapper hardcodes `os.path.dirname(os.path.abspath(__file__))` as the
    # outbox root. We patch os.path.abspath to return a path that resolves into
    # our tmp dir so the final outbox path lands inside tmp_path.
    return fake_outbox


def _redirect_abspath(monkeypatch, fake_root, seed_opt_d=False):
    """Make os.path.abspath(__file__) resolve into fake_root for the outbox path calc.

    Also creates a fake `SLEEP_TRIPLE/opt_d_alerts.py` inside the redirected dir
    so the wrapper's alert-fanout path (which checks `os.path.exists(_opt_d)`)
    sees a present file. Without this, the wrapper's `if not os.path.exists(_opt_d)`
    branch fires, sets `_alert_fired = False`, and any test asserting `alert_fired=True`
    would fail.
    """
    real_abspath = os.path.abspath

    def fake_abspath(p):
        # When called with __file__ (the war_room.py path), return a path inside fake_root
        # so that `os.path.join(fake_root, "SLEEP_TRIPLE", "outbox", "trend_reports")`
        # lands in our tmp dir.
        abs_p = real_abspath(p)
        if abs_p.endswith("war_room.py"):
            return os.path.join(str(fake_root), "_war_room.py")
        return abs_p
    monkeypatch.setattr(os.path, "abspath", fake_abspath)
    if seed_opt_d:
        # Only when the test exercises the alert subprocess path -- opt-in prevents
        # stale fake files from polluting the tmp dirs of opt-d-irrelevant tests.
        fake_opt_d = fake_root / "SLEEP_TRIPLE" / "opt_d_alerts.py"
        fake_opt_d.parent.mkdir(parents=True, exist_ok=True)
        fake_opt_d.write_text("# fake opt_d_alerts.py for tests\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# TestCmdLaunchTrendCompare
# ---------------------------------------------------------------------------
class TestCmdLaunchTrendCompare:
    def test_stable_verdict_no_alert_no_subprocess(self, monkeypatch, capsys):
        """All sections STABLE -> subprocess.run NOT called, alert NOT fired."""
        payload = _make_payload({"health": "STABLE", "tools": "STABLE"})
        _patch_trend_compare(monkeypatch, payload)
        # Subprocess guard: if subprocess.run is called, fail the test.
        with mock.patch.object(war_room.subprocess, "run") as mock_run:
            rc = war_room.cmd_launch_trend_compare(
                argparse.Namespace(
                    a="1d", b="7d",
                    emit_report=False, alert_on_degraded=True, json=False,
                )
            )
        out = capsys.readouterr().out
        assert rc == 0
        # No subprocess call to opt_d_alerts.
        opt_d_calls = [
            c for c in mock_run.call_args_list
            if "opt_d_alerts.py" in str(c)
        ]
        assert opt_d_calls == [], f"opt_d_alerts should NOT be called for STABLE verdict, got: {opt_d_calls}"
        # Text output reflects stable.
        assert "degraded sections: 0" in out
        assert "no degraded sections, no alert fired" in out

    def test_flapping_verdict_fires_alert_subprocess(self, tmp_path, monkeypatch, capsys):
        """At least one section MORE_FLAPPING -> subprocess.run IS called with opt_d_alerts + formatted --msg."""
        payload = _make_payload({
            "health": "STABLE",
            "tools": "MORE_FLAPPING",  # the degraded one
        })
        _patch_trend_compare(monkeypatch, payload)
        # alert-subprocess path -- seed fake opt_d so exists() check passes
        _redirect_abspath(monkeypatch, tmp_path, seed_opt_d=True)
        with mock.patch.object(war_room.subprocess, "run") as mock_run:
            # Return a CompletedProcess-like object with returncode 0
            mock_run.return_value = mock.Mock(returncode=0, stdout="ok", stderr="")
            rc = war_room.cmd_launch_trend_compare(
                argparse.Namespace(
                    a="1d", b="7d",
                    emit_report=False, alert_on_degraded=True, json=False,
                )
            )
        out = capsys.readouterr().out
        assert rc == 0
        # Exactly one opt_d_alerts subprocess call.
        opt_d_calls = [
            c for c in mock_run.call_args_list
            if "opt_d_alerts.py" in str(c)
        ]
        assert len(opt_d_calls) == 1, f"expected 1 opt_d_alerts call, got {len(opt_d_calls)}"
        # The call's argv includes --msg with the formatted degraded summary.
        call_argv = opt_d_calls[0][0][0]  # positional arg list
        assert "--msg" in call_argv
        msg_idx = call_argv.index("--msg")
        msg_value = call_argv[msg_idx + 1]
        assert "MORE_FLAPPING" in msg_value
        assert "tools" in msg_value
        assert "[WARN] Workspace degraded" in msg_value
        # --channel discord is the default.
        assert "--channel" in call_argv
        ch_idx = call_argv.index("--channel")
        assert call_argv[ch_idx + 1] == "discord"
        # shell=False (no shell injection).
        assert opt_d_calls[0][1].get("shell", "MISSING") is False or opt_d_calls[0][1].get("shell") is False
        # Text output reflects degraded + alert fired.
        assert "degraded sections: 1" in out
        assert "tools:" in out
        assert "alert fired" in out

    def test_emit_report_writes_md_and_json(self, tmp_path, monkeypatch, capsys):
        """--emit-report writes .md + .json files to outbox/trend_reports/ with correct content."""
        payload = _make_payload({
            "health": "STABLE",
            "tools": "MORE_FLAPPING",
        })
        _patch_trend_compare(monkeypatch, payload)
        # Redirect outbox into tmp_path via os.path.abspath patch.
        _redirect_abspath(monkeypatch, tmp_path)
        with mock.patch.object(war_room.subprocess, "run") as mock_run:
            rc = war_room.cmd_launch_trend_compare(
                argparse.Namespace(
                    a="1d", b="7d",
                    emit_report=True, alert_on_degraded=False, json=False,
                )
            )
        out = capsys.readouterr().out
        assert rc == 0
        # Find the outbox/trend_reports/ dir created by the wrapper.
        # The wrapper does os.path.join(<fake_root>, "SLEEP_TRIPLE", "outbox", "trend_reports").
        report_dir = tmp_path / "SLEEP_TRIPLE" / "outbox" / "trend_reports"
        assert report_dir.is_dir(), f"expected outbox dir at {report_dir}, got: {list(tmp_path.iterdir())}"
        files = sorted(p.name for p in report_dir.iterdir())
        # Should have exactly one .md and one .json (same stamp).
        md_files = [f for f in files if f.endswith(".md")]
        json_files = [f for f in files if f.endswith(".json")]
        assert len(md_files) == 1
        assert len(json_files) == 1
        # Stamps match (same timestamp -> same prefix).
        assert md_files[0].replace(".md", "") == json_files[0].replace(".json", "")
        # .json content matches the payload.
        with open(report_dir / json_files[0], encoding="utf-8") as f:
            written_json = json.load(f)
        assert written_json == payload
        # .md content has table header + degraded callout.
        with open(report_dir / md_files[0], encoding="utf-8") as f:
            md_text = f.read()
        assert "# Trend Compare Report" in md_text
        assert "Window A: 1d" in md_text
        assert "Window B: 7d" in md_text
        assert "| Section | A (rate) | B (rate) | Verdict |" in md_text
        assert "MORE_FLAPPING" in md_text
        assert "## \u26a0\ufe0f Degraded sections (1)" in md_text
        # No subprocess call (--alert-on-degraded False).
        opt_d_calls = [
            c for c in mock_run.call_args_list
            if "opt_d_alerts.py" in str(c)
        ]
        assert opt_d_calls == []
        # Text output echoes the report paths.
        assert "reports written:" in out
        assert str(md_files[0]) in out

    def test_invalid_a_returns_fail_no_side_effects(self, monkeypatch, capsys):
        """--a 0d (or any invalid format) -> rc=1, no subprocess, no file writes, no trend-compare call."""
        # Guard: if cmd_trend_compare IS called despite invalid input, fail.
        with mock.patch.object(war_room, "cmd_trend_compare") as mock_tc:
            with mock.patch.object(war_room.subprocess, "run") as mock_run:
                rc = war_room.cmd_launch_trend_compare(
                    argparse.Namespace(
                        a="0d", b="7d",
                        emit_report=True, alert_on_degraded=True, json=False,
                    )
                )
        out = capsys.readouterr().out
        assert rc == 1
        # No trend-compare call (early validation prevented it).
        assert mock_tc.call_count == 0
        # No subprocess call.
        opt_d_calls = [
            c for c in mock_run.call_args_list
            if "opt_d_alerts.py" in str(c)
        ]
        assert opt_d_calls == []
        # Clear error message.
        assert "[FAIL]" in out
        assert "--a" in out
        assert "0d" in out

    def test_invalid_b_returns_fail_no_side_effects(self, monkeypatch, capsys):
        """--b 0d (or any invalid format) -> rc=1, no subprocess, no file writes, no trend-compare call.

        Mirrors test_invalid_a but for the --b flag (validates the SECOND
        _parse_window_days call in the wrapper, not the first).
        """
        with mock.patch.object(war_room, "cmd_trend_compare") as mock_tc:
            with mock.patch.object(war_room.subprocess, "run") as mock_run:
                rc = war_room.cmd_launch_trend_compare(
                    argparse.Namespace(
                        a="1d", b="0d",
                        emit_report=True, alert_on_degraded=True, json=False,
                    )
                )
        out = capsys.readouterr().out
        assert rc == 1
        assert mock_tc.call_count == 0
        opt_d_calls = [
            c for c in mock_run.call_args_list
            if "opt_d_alerts.py" in str(c)
        ]
        assert opt_d_calls == []
        assert "[FAIL]" in out
        assert "--b" in out
        assert "0d" in out

    def test_json_mode_composite(self, tmp_path, monkeypatch, capsys):
        """--json mode emits the full composite payload (8 keys: payload + degraded_count + degraded_sections + report_paths + alert_requested + alert_fired + alert_rc + alert_error)."""
        payload = _make_payload({
            "health": "STABLE",
            "tools": "MORE_FLAPPING",
        })
        _patch_trend_compare(monkeypatch, payload)
        # alert-subprocess path -- seed fake opt_d so exists() check passes
        _redirect_abspath(monkeypatch, tmp_path, seed_opt_d=True)
        with mock.patch.object(war_room.subprocess, "run") as mock_run:
            mock_run.return_value = mock.Mock(returncode=0, stdout="ok", stderr="")
            rc = war_room.cmd_launch_trend_compare(
                argparse.Namespace(
                    a="1d", b="7d",
                    emit_report=True, alert_on_degraded=True, json=True,
                )
            )
        out = capsys.readouterr().out
        assert rc == 0
        # Parse the composite JSON (it's the only thing the wrapper prints in --json mode).
        composite = json.loads(out)
        # All 8 expected keys present.
        expected_keys = {
            "payload", "degraded_count", "degraded_sections",
            "report_paths", "alert_requested", "alert_fired",
            "alert_rc", "alert_error",
        }
        assert expected_keys.issubset(set(composite.keys())), \
            f"missing keys: {expected_keys - set(composite.keys())}"
        # payload matches what cmd_trend_compare emitted.
        assert composite["payload"] == payload
        # 1 degraded section (tools).
        assert composite["degraded_count"] == 1
        assert composite["degraded_sections"] == ["tools"]
        # report_paths has 2 entries (md + json) since --emit-report was set.
        assert len(composite["report_paths"]) == 2
        assert any(p.endswith(".md") for p in composite["report_paths"])
        assert any(p.endswith(".json") for p in composite["report_paths"])
        # alert_requested=True, alert_fired=True (degraded section exists, subprocess ran).
        assert composite["alert_requested"] is True
        assert composite["alert_fired"] is True
        # alert_rc=0 (mock subprocess returned 0).
        assert composite["alert_rc"] == 0
        # alert_error=None (no error).
        assert composite["alert_error"] is None

    def test_strict_alert_rc_fails_when_alert_delivery_fails(self, tmp_path, monkeypatch, capsys):
        """--strict-alert-rc=True + degraded exists + opt_d_alerts returns rc=1 -> wrapper rc=1.

        MINOR #1 (cont.22 followups #2): opt-in strict mode. Default rc=0 contract
        preserved (without the flag, the same scenario returns rc=0). With the flag,
        alert DELIVERY failures bump the wrapper rc to 1 so a strict CI pipeline
        can fail loud instead of silently returning 0.
        """
        payload = _make_payload({
            "health": "STABLE",
            "tools": "MORE_FLAPPING",  # the degraded one
        })
        _patch_trend_compare(monkeypatch, payload)
        # alert-subprocess path -- seed fake opt_d so exists() check passes
        _redirect_abspath(monkeypatch, tmp_path, seed_opt_d=True)
        with mock.patch.object(war_room.subprocess, "run") as mock_run:
            # Simulate opt_d_alerts.py returns nonzero (delivery failure).
            mock_run.return_value = mock.Mock(returncode=1, stdout="", stderr="network timeout")
            rc = war_room.cmd_launch_trend_compare(
                argparse.Namespace(
                    a="1d", b="7d",
                    emit_report=False, alert_on_degraded=True,
                    strict_alert_rc=True,  # opt-in strict mode
                    json=False,
                )
            )
        out = capsys.readouterr().out
        # Strict mode bumps wrapper rc to 1 because alert was requested+fired+failed.
        assert rc == 1, f"expected rc=1 under strict mode with delivery failure; got rc={rc}"
        # Strict-mode fail line present.
        assert "--strict-alert-rc" in out
        assert "alert delivery failed" in out
        assert "[FAIL]" in out

    def test_strict_alert_rc_passes_when_no_alert_fired(self, monkeypatch, capsys):
        """--strict-alert-rc=True + NO degraded sections -> wrapper rc=0 (no-op).

        Mirrors test_stable_verdict_no_alert_no_subprocess but with strict mode on.
        The flag must NOT bump rc when no alert was attempted (no degraded =
        no delivery needed). Validates the precise condition under which the
        strict-mode bump applies: alert_fired=True AND alert_rc != 0.
        """
        payload = _make_payload({"health": "STABLE", "tools": "STABLE"})
        _patch_trend_compare(monkeypatch, payload)
        with mock.patch.object(war_room.subprocess, "run") as mock_run:
            rc = war_room.cmd_launch_trend_compare(
                argparse.Namespace(
                    a="1d", b="7d",
                    emit_report=False, alert_on_degraded=True,
                    strict_alert_rc=True,  # strict but no degraded
                    json=False,
                )
            )
        out = capsys.readouterr().out
        # No degraded -> no alert fired -> strict mode is a no-op.
        assert rc == 0
        opt_d_calls = [
            c for c in mock_run.call_args_list
            if "opt_d_alerts.py" in str(c)
        ]
        assert opt_d_calls == []
        assert "no degraded sections" in out
        # Under strict mode but no degraded, the strict failure line should NOT appear.
        assert "--strict-alert-rc: alert delivery failed" not in out

    def test_strict_alert_rc_fails_when_opt_d_alerts_missing(self, monkeypatch, capsys):
        """--strict-alert-rc=True + degraded exists + opt_d_alerts.py MISSING -> wrapper rc=1.

        REVISION (reviewer-feedback MAJOR): covers the opt_d_alerts.py-missing path
        that the original `_alert_fired`-gated condition missed. In this path:
          - subprocess.run was NOT called (file didn't exist, we never Popen'd)
          - `_alert_error` is set to "not found at ..."
          - `_alert_fired` stays False
          - `_alert_rc` is set to 1
        Operator set --strict-alert-rc because they want delivery failures to
        surface loudly; opt_d_alerts missing IS a delivery failure. So strict
        mode bumps rc=1 here even though subprocess never ran.
        """
        payload = _make_payload({
            "health": "STABLE",
            "tools": "MORE_FLAPPING",  # degraded
        })
        _patch_trend_compare(monkeypatch, payload)
        # Crucially: _redirect_abspath is NOT called here, so the wrapper resolves
        # opt_d_alerts path against the REAL war_room.py directory. The real
        # opt_d_alerts.py path is `SLEEP_TRIPLE/opt_d_alerts.py` relative to
        # war_room.py's here-directory; if it doesn't exist there, the wrapper
        # enters the missing-script branch. We don't assert on its presence/absence
        # in this repo (test runs across environments); instead we patch the
        # wrapper to FORCE the missing-script branch by simulating the
        # os.path.exists() returning False.
        with mock.patch.object(os.path, "exists") as mock_exists:
            # Allow the real exists() checks BUT force the opt_d_alerts path to return False.
            real_exists = os.path.exists

            def selective_exists(p):
                # The wrapper checks `if not os.path.exists(_opt_d):` for the opt_d_alerts script.
                # Force that specific path to "missing" while passing everything else through.
                if "opt_d_alerts.py" in str(p):
                    return False
                return real_exists(p)
            mock_exists.side_effect = selective_exists
            with mock.patch.object(war_room.subprocess, "run") as mock_run:
                rc = war_room.cmd_launch_trend_compare(
                    argparse.Namespace(
                        a="1d", b="7d",
                        emit_report=False, alert_on_degraded=True,
                        strict_alert_rc=True,  # opt-in strict mode
                        json=False,
                    )
                )
        out = capsys.readouterr().out
        # subprocess.run MUST NOT have been called (script missing -> never Popen).
        opt_d_calls = [
            c for c in mock_run.call_args_list
            if "opt_d_alerts.py" in str(c)
        ]
        assert opt_d_calls == [], f"expected 0 opt_d_alerts subprocess calls (script missing), got: {opt_d_calls}"
        # But strict mode still bumps rc=1 because operator wanted delivery failures to fail loud.
        assert rc == 1, f"expected rc=1 under strict mode when opt_d_alerts missing; got rc={rc}"
        # The strict-fail line is present.
        assert "--strict-alert-rc" in out
        assert "alert delivery failed" in out
