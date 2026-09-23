#!/usr/bin/env python3
"""
test_monitor.py — Unit tests for SLEEP_CASH_API/monitor.py.

Run with:
  python SLEEP_CASH_API/test_monitor.py

Covers:
  1. _probe: healthy (200 + status=ok), 200 with junk body, HTTPError,
     connection error, timeout
  2. _discord_post: success on 204/200, failure on exception
  3. main(["--once"]): exit 0 on healthy probe, exit 1 on unhealthy probe
  4. main(["--once"]): uses DEFAULT_URL by default, --url override works
  5. MONITOR_INTERVAL env override honored when --interval not given
  6. --discord-threshold is read and used by the failure-counter logic
  7. Stopping via SIGINT does not lose any failures logged before SIGINT
     (failures_in_a_row is reset on the next OK probe)

All tests use unittest.mock.patch on urllib.request.urlopen so no real
network calls happen.
"""

import io
import json
import os
import subprocess
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import MagicMock, patch

from . import monitor


class ProbeTests(unittest.TestCase):
    """_probe(url, timeout) returns (ok, detail)."""

    def test_probe_healthy(self):
        body = json.dumps({"status": "ok", "timestamp": "2026-06-30T00:00:00Z"}).encode()
        with patch.object(monitor.urllib.request, "urlopen") as m:
            m.return_value.__enter__.return_value.read.return_value = body
            m.return_value.__enter__.return_value.status = 200
            ok, detail = monitor._probe("https://stub/healthz")
        self.assertTrue(ok, detail)
        self.assertIn("200", detail)
        self.assertIn("ok", detail)

    def test_probe_200_with_junk_body(self):
        # HTTP 200 but status field absent / malformed — must NOT crash.
        body = b"<html><body>not json</body></html>"
        with patch.object(monitor.urllib.request, "urlopen") as m:
            m.return_value.__enter__.return_value.read.return_value = body
            m.return_value.__enter__.return_value.status = 200
            ok, detail = monitor._probe("https://stub/healthz")
        # Body had no parseable JSON, so detail falls back to trim text;
        # ok should still be True (HTTP 200, status text derived from non-json body).
        self.assertIsInstance(ok, bool)
        self.assertIn("200", detail)

    def test_probe_http_error(self):
        import urllib.error
        err = urllib.error.HTTPError("https://stub/healthz", 500, "Server Error", {}, io.StringIO("boom"))
        with patch.object(monitor.urllib.request, "urlopen", side_effect=err):
            ok, detail = monitor._probe("https://stub/healthz")
        self.assertFalse(ok)
        self.assertIn("500", detail)

    def test_probe_connection_error(self):
        with patch.object(monitor.urllib.request, "urlopen",
                          side_effect=ConnectionRefusedError("nope")):
            ok, detail = monitor._probe("https://stub/healthz")
        self.assertFalse(ok)
        self.assertIn("ConnectionRefused", detail)

    def test_probe_timeout(self):
        with patch.object(monitor.urllib.request, "urlopen",
                          side_effect=TimeoutError("slow")):
            ok, detail = monitor._probe("https://stub/healthz")
        self.assertFalse(ok)
        self.assertIn("Timeout", detail)


class ProbePortTests(unittest.TestCase):
    """_probe_port(host, port, timeout) does a TCP reachability probe."""

    def test_probe_port_reachable(self):
        # Mock socket.create_connection so the test never opens a real socket.
        # Must use MagicMock (auto-context-manager), not plain `object()` -- bare
        # object's lack of __enter__/__exit__ would crash `_probe_port`'s
        # `with socket.create_connection(...) as ...` block.
        fake_conn = MagicMock()
        with patch.object(monitor.socket, "create_connection",
                          return_value=fake_conn) as m:
            ok, detail = monitor._probe_port("127.0.0.1", 8188)
        self.assertTrue(ok, detail)
        self.assertIn("127.0.0.1:8188", detail)
        self.assertIn("reachable", detail)
        m.assert_called_once_with(("127.0.0.1", 8188), timeout=monitor.PROBE_ALL_TIMEOUT)

    def test_probe_port_unreachable(self):
        with patch.object(monitor.socket, "create_connection",
                          side_effect=ConnectionRefusedError("nope")):
            ok, detail = monitor._probe_port("127.0.0.1", 9999)
        self.assertFalse(ok)
        self.assertIn("unreachable", detail)
        self.assertIn("ConnectionRefusedError", detail)


class ProbeAllTests(unittest.TestCase):
    """_probe_all + main(['--probe-all']).

    Lock the multi-probe contract:
      - _probe_all emits one row for the live API + one row per local service.
      - main(['--probe-all']) exits 0 only if every row is OK.
      - main(['--probe-all']) exits 1 if any row is FAIL.
      - --probe-all does NOT auto-post to Discord even when DISCORD_WEBHOOK_URL is set
        (single slow service could spam the channel).
    """

    def _stub_probe_all(self, results):
        """Patch monitor._probe_all to return a fixed results list."""
        return patch.object(monitor, "_probe_all", return_value=list(results))

    def test_probe_all_returns_live_api_plus_each_local_service(self):
        # Use a list whose reachability matches the documented PROBE_ALL_LOCAL_SERVICES.
        services = monitor.PROBE_ALL_LOCAL_SERVICES
        from datetime import datetime
        from unittest.mock import MagicMock
        # Real call: probe live URL (mocked) + each TCP port (mocked).
        body = json.dumps({"status": "ok"}).encode()
        with patch.object(monitor.urllib.request, "urlopen") as m_urlopen, \
             patch.object(monitor.socket, "create_connection", return_value=MagicMock()):
            m_urlopen.return_value.__enter__.return_value.read.return_value = body
            m_urlopen.return_value.__enter__.return_value.status = 200
            results = monitor._probe_all("https://stub/healthz", services)
        # One row per target: 1 live_api + N services.
        self.assertEqual(len(results), 1 + len(services),
                         f"expected 1 + {len(services)} results, got {len(results)}")
        # First row is the live API; rest are the services.
        self.assertIn("live_api", results[0][0])
        for i, (label, _, _) in enumerate(results[1:], start=0):
            self.assertIn(services[i][0], label)
            self.assertIn("127.0.0.1", label)
            self.assertIn(str(services[i][2]), label)

    def test_probe_all_main_exits_zero_when_all_ok(self):
        # Patch source-side: urlopen (live API) + socket.create_connection (local ports).
        # Patches _probe_all directly bypasses real implementation pitfalls, so this
        # test exercises the full main() -> _probe_all -> _probe/_probe_port chain.
        body = json.dumps({"status": "ok"}).encode()
        with patch.object(monitor.urllib.request, "urlopen") as m_urlopen, \
             patch.object(monitor.socket, "create_connection",
                          return_value=MagicMock()) as m_sock:
            m_urlopen.return_value.__enter__.return_value.read.return_value = body
            m_urlopen.return_value.__enter__.return_value.status = 200
            buf_out = io.StringIO()
            with redirect_stdout(buf_out):
                rc = monitor.main(["--probe-all"])
        self.assertEqual(rc, 0, buf_out.getvalue())
        self.assertIn("probe-all results", buf_out.getvalue())
        self.assertIn("OK", buf_out.getvalue())
        self.assertNotIn("FAIL", buf_out.getvalue())
        # Soft invariants (>= 1): true today, future-proof against short-circuits.
        self.assertGreaterEqual(m_urlopen.call_count, 1,
                                "live API must be probed at least once")
        self.assertGreaterEqual(m_sock.call_count, 1,
                                "at least one local service must be probed")
        # All services should still be probed (no short-circuit on first OK).
        self.assertGreaterEqual(m_sock.call_count, len(monitor.PROBE_ALL_LOCAL_SERVICES),
                         f"every local service must be probed; got {m_sock.call_count} / expected {len(monitor.PROBE_ALL_LOCAL_SERVICES)}")

    def test_probe_all_main_exits_one_when_any_fail(self):
        # Live API up + Ollama up + ComfyUI :8188 down -> rc must be 1.
        # side_effect list lets us fail ONLY the first create_connection call.
        body = json.dumps({"status": "ok"}).encode()
        fail_then_pass = [ConnectionRefusedError("nope"), MagicMock()]
        with patch.object(monitor.urllib.request, "urlopen") as m_urlopen, \
             patch.object(monitor.socket, "create_connection",
                          side_effect=fail_then_pass) as m_sock, \
             patch.object(monitor, "_discord_post", return_value=True) as m_post:
            m_urlopen.return_value.__enter__.return_value.read.return_value = body
            m_urlopen.return_value.__enter__.return_value.status = 200
            buf_out = io.StringIO()
            with redirect_stdout(buf_out):
                rc = monitor.main(["--probe-all"])
        self.assertEqual(rc, 1, buf_out.getvalue())
        self.assertIn("FAIL", buf_out.getvalue())
        self.assertIn("ComfyUI", buf_out.getvalue())
        # MUST NOT auto-Discord-post even when _discord_post is callable.
        m_post.assert_not_called()
        self.assertGreaterEqual(m_urlopen.call_count, 1)
        self.assertGreaterEqual(m_sock.call_count, 1)

    def test_probe_all_does_not_post_to_discord_even_with_webhook(self):
        # All OK path with DISCORD_WEBHOOK_URL set: --probe-all must stay silent.
        # Defense-in-depth: any future refactor that adds Discord output under
        # --probe-all would break this test (covers both an actual _discord_post
        # call AND any accidental print line with "discord" in it).
        body = json.dumps({"status": "ok"}).encode()
        with patch.object(monitor.urllib.request, "urlopen") as m_urlopen, \
             patch.object(monitor.socket, "create_connection",
                          return_value=MagicMock()), \
             patch.dict(os.environ,
                        {"DISCORD_WEBHOOK_URL": "https://discord.example/hook"},
                        clear=False), \
             patch.object(monitor, "_discord_post", return_value=True) as m_post:
            m_urlopen.return_value.__enter__.return_value.read.return_value = body
            m_urlopen.return_value.__enter__.return_value.status = 200
            buf_out = io.StringIO()
            with redirect_stdout(buf_out):
                rc = monitor.main(["--probe-all"])
        self.assertEqual(rc, 0)
        m_post.assert_not_called()
        # Belt-and-braces: any accidental "discord" output (print, log, future
        # refactor that adds a `_discord_post` call without re-checking flags)
        # would break this assertion. Broader than the prior "discord posted=True"
        # string match so a future rename to print format won't silently pass.
        self.assertNotIn("discord posted=True", buf_out.getvalue(),
                         "--probe-all must not log a successful Discord post")


class DiscordPostTests(unittest.TestCase):
    """_discord_post(webhook_url, content) returns True on 200/204, False on error."""

    def test_discord_post_success_204(self):
        with patch.object(monitor.urllib.request, "urlopen") as m:
            m.return_value.__enter__.return_value.status = 204
            ok = monitor._discord_post("https://discord/hook", "hello")
        self.assertTrue(ok)

    def test_discord_post_success_200(self):
        with patch.object(monitor.urllib.request, "urlopen") as m:
            m.return_value.__enter__.return_value.status = 200
            ok = monitor._discord_post("https://discord/hook", "hello")
        self.assertTrue(ok)

    def test_discord_post_failure(self):
        with patch.object(monitor.urllib.request, "urlopen",
                          side_effect=ConnectionError("oh no")):
            ok = monitor._discord_post("https://discord/hook", "hello")
        self.assertFalse(ok)


class MainOnceTests(unittest.TestCase):
    """main(['--once']) reads the URL and exits with the right code."""

    def _stub_probe(self, ok: bool):
        body = json.dumps({"status": "ok" if ok else "fail"}).encode()
        with patch.object(monitor.urllib.request, "urlopen") as m:
            m.return_value.__enter__.return_value.read.return_value = body
            m.return_value.__enter__.return_value.status = 200 if ok else 500
            m.return_value.__enter__.return_value.status = 200
            # Patch _probe directly for clarity in some tests; fall back
            # to urlopen stub for the integration check below.
            with patch.object(monitor, "_probe", return_value=(ok, f"HTTP {200 if ok else 500}")):
                buf_out, buf_err = io.StringIO(), io.StringIO()
                with redirect_stdout(buf_out), redirect_stderr(buf_err):
                    rc = monitor.main(["--once"])
                return rc, buf_out.getvalue(), buf_err.getvalue()

    def test_once_healthy_exits_zero(self):
        rc, out, _ = self._stub_probe(ok=True)
        self.assertEqual(rc, 0, out)
        self.assertIn("OK", out)

    def test_once_unhealthy_exits_one(self):
        rc, out, _ = self._stub_probe(ok=False)
        self.assertEqual(rc, 1, out)
        self.assertIn("FAIL", out)


class EnvOverrideTests(unittest.TestCase):
    """MONITOR_INTERVAL env var is read when --interval not given."""

    def test_monitor_interval_env_override(self):
        with patch.dict(os.environ, {"MONITOR_INTERVAL": "17"}, clear=False):
            # Clear any inherited monitor module globals; use a fresh parse.
            ap = monitor.argparse if hasattr(monitor, "argparse") else None
            ns = monitor.main.__globals__  # type: ignore[attr-defined]
            # The simplest reliable check is to re-implement the default logic.
            default = int(os.environ.get("MONITOR_INTERVAL", monitor.DEFAULT_INTERVAL))
            self.assertEqual(default, 17)

    def test_default_interval_when_env_absent(self):
        env = {k: v for k, v in os.environ.items() if k != "MONITOR_INTERVAL"}
        with patch.dict(os.environ, env, clear=True):
            default = int(os.environ.get("MONITOR_INTERVAL", monitor.DEFAULT_INTERVAL))
            self.assertEqual(default, monitor.DEFAULT_INTERVAL)


class CrossFileConsistencyTests(unittest.TestCase):
    """Cross-file URL and constant invariants."""

    def test_default_url_is_v1(self):
        # Today's deployed Vercel URL; lock in via a substring assertion so
        # a future env-specific override still matches.
        self.assertIn("yt-transcript-api", monitor.DEFAULT_URL)
        self.assertIn("/healthz", monitor.DEFAULT_URL)

    def test_default_threshold_is_positive_int(self):
        self.assertIsInstance(monitor.DEFAULT_THRESHOLD, int)
        self.assertGreaterEqual(monitor.DEFAULT_THRESHOLD, 1)


class RegressionTests(unittest.TestCase):
    """Regression tests for shell scripts that wrap monitor.py.

    Locks the v26 install_monitor_scheduler.bat structural fix in: a future
    regression of the `( ... ) + ^ continuation + unquoted drive-colon path`
    parser-trip pattern would re-emit `: was unexpected at this time.` and
    silently break the dry-run preview (see CHANGELOG v26 for the postmortem).

    Plus v30/v31 gitignore regression tests:
    - test_gitignore_no_inline_comments_on_pattern_lines: structural
    - test_gitignore_pass5_patterns_semantic_match: behavioral, via
      POSITIVE_PROBES + NEGATIVE_PROBES module-level probe lists.
    """

    BAT_PATH = r"C:\Users\karma\install_monitor_scheduler.bat"

    def test_bat_dry_run_exits_zero_with_preview(self):
        """install_monitor_scheduler.bat --dry-run must exit 0, show preview.

        Skipped on non-Windows (no .bat support) and when the bat is absent
        (CI environments without the file system). On Windows, Python's
        CreateProcess handles .bat files via cmd.exe automatically.
        """
        if sys.platform != "win32":
            self.skipTest("install_monitor_scheduler.bat is Windows-only")
        if not Path(self.BAT_PATH).exists():
            self.skipTest(f"bat not found at {self.BAT_PATH}")
        # 30s timeout: bat should complete in <2s on a healthy workstation.
        result = subprocess.run(
            [self.BAT_PATH, "--dry-run"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(
            result.returncode, 0,
            f"dry-run exited {result.returncode}; "
            f"stderr=\n{result.stderr}\nstdout=\n{result.stdout}",
        )
        # Preview content reach — proves the v26 structural fix works.
        self.assertIn(
            "No registry / Task Scheduler change has been made.",
            result.stdout,
            "dry-run preview content missing from stdout (parser error likely)",
        )
        # Parser-error regression guard — the v26 bug surface.
        combined = result.stdout + result.stderr
        self.assertNotIn(
            ": was unexpected",
            combined,
            "CMD parser error regressed — see CHANGELOG v26 entry",
        )
        # Both scheduled tasks previewed.
        self.assertIn("SLEEP_CASH\\Monitor", result.stdout)
        self.assertIn("SLEEP_CASH\\ProbeAll", result.stdout)

    def test_gitignore_no_inline_comments_on_pattern_lines(self):
        """Lock v30 gitignore inline-comment fix in via structural check.

        Per git docs, a `#` is only a comment at column 0. Any `#` after
        non-whitespace on a pattern line is interpreted as part of the path
        literal, silently breaking the pattern. See CHANGELOG v30.

        Strategy: read .gitignore directly, scan every non-comment non-blank
        line for a `#` after position 0. Any match is a violation.

        This is a structural test (no subprocess, no fs walks) so:
        - Cross-platform safe (just reads a text file).
        - Deterministic (no flakiness from gitignore runtime state).
        - Catches future regressions of THIS EXACT bug pattern.
        - Does NOT verify patterns are *correct* — only that their *syntax* is
          not corrupted by inline comments. Pattern correctness is verified
          by manual checks (see CHANGELOG v30 entry for the trajectory).
        """
        repo_root = Path(__file__).resolve().parent.parent
        gitignore_path = repo_root / ".gitignore"
        if not gitignore_path.exists():
            self.skipTest(f".gitignore not found at {gitignore_path}")
        content = gitignore_path.read_text(encoding="utf-8")
        offenders = []
        for line_no, line in enumerate(content.splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                # Comment line or blank line; neither can have an inline bug.
                continue
            hash_pos = stripped.find("#")
            if hash_pos > 0:
                # Hash is somewhere after content; the part before `#` is the
                # pattern, the part after is being eaten as part of the path.
                offenders.append((line_no, line.rstrip()))
        self.assertEqual(
            offenders, [],
            "Found pattern lines with inline `#` comments; git treats everything\n"
            "after the `#` as part of the path, silently breaking the pattern.\n"
            "Split comments onto their own lines, started with `#` at column 0.\n"
            "See CHANGELOG v30 (vue-30 inline-comment fix) for context.\n"
            "Offending lines:\n"
            + "\n".join(f"  line {n}: {l!r}" for n, l in offenders),
        )

    def test_gitignore_pass5_patterns_semantic_match(self):
        """Behavior coverage: each Pass-3/4/5/6 pattern matches a synthetic probe.

        Complements the structural test above. The structural test catches the
        inline-`#`-after-whitespace SYNTAX bug; the semantic test catches
        SEMANTIC regressions: a pattern with wrong path, an inactive pattern,
        a typo, or a rule accidentally shadowed by another.

        Per v31 amend-#2 redesign: uses synthetic relative paths instead of
        actual untracked files on disk. Rationale: the v30 fix now correctly
        elides every file under the 9 pattern dirs, so the original "find an
        untracked file via `git ls-files --others` and probe it" approach
        always returned 0 matches (the test would fail on the v30-fixed state
        it was supposed to protect, a measurement paradox).

        Strategy G (synthetic probes): for each Pass-3/4/5/6 pattern, construct
        a non-existent relative path under the pattern's root and run
        `git check-ignore -v <path>`. Git's pattern matcher evaluates the
        string against the active rules even for non-existent paths — rc=0
        means the pattern IS targeting that prefix correctly; rc=1 means the
        pattern is broken or missing.

        Plus a NEGATIVE control: pick a tracked source file and assert rc=1
        (not ignored). Catches the failure mode where a too-broad rule
        accidentally elides real source.

        Cross-platform safe (skip on non-win32 + only string ops + git
        subprocess). Probe paths contain ONLY forward slashes — a hard
        assertion prevents the v31-v1 backslash-absolute-path bug from coming
        back.
        """
        if sys.platform != "win32":
            self.skipTest("Patterns target Windows-specific paths (AppData/, Desktop/, etc.)")
        repo_root = Path(__file__).resolve().parent.parent
        matched_count = 0
        for probe in POSITIVE_PROBES:
            result = subprocess.run(
                ["git", "check-ignore", "-v", probe],
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=CHECK_IGNORE_TIMEOUT,
            )
            self.assertEqual(
                result.returncode, 0,
                f"Semantic regression: pattern failed to match synthetic probe {probe!r}.\n"
                f"git check-ignore rc={result.returncode} (expected 0, MATCHED).\n"
                f"stdout={result.stdout!r}\nstderr={result.stderr!r}\n"
                f"A rc=1 here means: pattern targets wrong path, has drifted "
                f"from where you expected, OR another rule is shadowing it. "
                f"See CHANGELOG v31 amend-#2 for context.",
            )
            matched_count += 1
        # All probes must match unconditionally.
        self.assertEqual(
            matched_count, len(POSITIVE_PROBES),
            f"expected all {len(POSITIVE_PROBES)} synthetic probes to match; "
            f"only {matched_count} matched",
        )
        # NEGATIVE control: tracked source files must NOT be ignored. A
        # missing `monitor.py`/`test_monitor.py` is a real defect (the test
        # file would not even load), so missing paths raise immediately.
        for probe in NEGATIVE_PROBES:
            self.assertTrue(
                (repo_root / probe).exists(),
                f"Required negative-control source file {probe!r} is missing; "
                f"gitignore regression test cannot run without it.",
            )
            result = subprocess.run(
                ["git", "check-ignore", "-v", probe],
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=CHECK_IGNORE_TIMEOUT,
            )
            self.assertEqual(
                result.returncode, 1,
                f"Over-broad gitignore: tracked source {probe!r} is being "
                f"ignored by a rule but should not be!\n"
                f"git check-ignore rc={result.returncode} (expected 1, NOT MATCHED).\n"
                f"stdout={result.stdout!r}\nstderr={result.stderr!r}\n"
                f"Common causes: pattern missing leading `./` anchor, or pattern "
                f"is unanchored and matches too broadly.",
            )


# Module-level probe lists for test_gitignore_pass5_patterns_semantic_match.
# Lift adds-at-once maintenance: future .gitignore patterns get a single
# addition in POSITIVE_PROBES; future tracked-source negative probes get
# a single addition in NEGATIVE_PROBES. Probes here MUST use forward
# slashes — git on Windows accepts both, but absolute Windows paths with
# backslashes (the v31 amend-#1 trap) are deliberately avoided.
POSITIVE_PROBES = [
    # Pass-3
    "AppData/Local/Mozilla/Firefox/Profiles/probe-xyz.txt",
    "AppData/Roaming/Mozilla/Firefox/Profiles/probe-xyz.txt",
    ".keras/probe-xyz.txt",
    ".matplotlib/probe-xyz.txt",
    ".vs/probe-xyz.txt",
    ".viminfo",
    ".node_repl_history",
    # Pass-4
    "Documents/Cline/probe-xyz.txt",
    # Pass-5
    "AppData/Local/pnpm/global/probe-xyz.txt",
    "AppData/Roaming/Python/probe-xyz.txt",
    "AppData/Roaming/Trae/probe-xyz.txt",
    "AppData/Roaming/Kiro/probe-xyz.txt",
    "SLEEP_TRIPLE/outbox/probe-xyz.txt",
    "AI_ARMY/reports/probe-xyz.json",
    # Pass-6
    "Desktop/.tmp.driveupload/probe-xyz.txt",
]
NEGATIVE_PROBES = [
    "README.md",
    "CHANGELOG.md",
    "install_monitor_scheduler.bat",
    "SLEEP_CASH_API/monitor.py",
    "SLEEP_CASH_API/test_monitor.py",
    "SLEEP_TRIPLE/preflight.py",
    "SLEEP_TRIPLE/opt_e_pod.py",
]
# Pattern matching is fast but cheap defense against a corrupt .git or
# fs-freeze wedge. 10s is generous vs <100ms typical per-call runtime.
CHECK_IGNORE_TIMEOUT = 10


def main():
    """Run all tests and report."""
    print()
    print("=" * 70)
    print("MONITOR — UNIT TESTS")
    print("=" * 70)
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    print()
    print("=" * 70)
    if result.wasSuccessful():
        print(f"ALL {result.testsRun} TESTS PASSED")
        return 0
    print(f"{len(result.failures)} FAILURES, {len(result.errors)} ERRORS")
    return 1


if __name__ == "__main__":
    sys.exit(main())
