#!/usr/bin/env python3

"""

test_preflight.py — Unit tests for SLEEP_TRIPLE/preflight.py.



Run with:

  python SLEEP_TRIPLE/test_preflight.py



Covers:

  1. _is_placeholder helper (REPLACE_*, empty, brace tokens, "None"/"null"/"todo")

  2. _lane_status reducer ([OK], [NEEDS_CONFIG], [OFFLINE], [BLOCKED] paths)

  3. _format_text_output / _format_json_output pure helpers

  4. Hardcoded-5 invariant (no lane counts as literals anywhere)

  5. main() exit codes: default (0), --strict (1 when publishable != total),

     --json (0), --verbose (0, prints extra detail line per Lane)

  6. main() stdout purity (only JSON when --json set, only formatted text otherwise)



The preflight module reads SLEEP_TRIPLE/opt_*_config.json from disk and probes

LIVE_API_URL, so helper tests use synthetic inputs while main() tests rely on

the real on-disk configs (which today report 1/5 publishable so --strict

always exits 1).

"""



import io

import json

import sys

import unittest

from contextlib import redirect_stderr, redirect_stdout

from pathlib import Path



sys.path.insert(0, str(Path(__file__).resolve().parent))



import preflight  # noqa: E402





class IsPlaceholderTests(unittest.TestCase):

    """_is_placeholder must catch REPLACE_WITH_*, brace tokens, empty, and 'None'."""



    def _assert_placeholder(self, value, *, msg=""):

        self.assertTrue(preflight._is_placeholder(value),

                        f"expected {value!r} to be a placeholder ({msg})")



    def _assert_not_placeholder(self, value, *, msg=""):

        self.assertFalse(preflight._is_placeholder(value),

                         f"expected {value!r} NOT to be a placeholder ({msg})")



    def test_replace_with_prefix(self):

        self._assert_placeholder("REPLACE_WITH_GUMROAD_API_KEY")

        self._assert_placeholder("REPLACE_WITH_YOUR_SHOPIFY_URL")

        self._assert_placeholder("REPLACE_WITH_SHOPIFY_ADMIN_TOKEN")

        self._assert_placeholder("REPLACE_ME")



    def test_replaces_suffixes(self):

        self._assert_placeholder("abc_HERE")

        self._assert_placeholder("/some/path_TOKEN")

        self._assert_placeholder("https://example_KEY")



    def test_brace_tokens(self):

        self._assert_placeholder("<username>")

        self._assert_placeholder("{token}")



    def test_lowercase_sentinel_words(self):

        self._assert_placeholder("none")

        self._assert_placeholder("null")

        self._assert_placeholder("Todo")

        self._assert_placeholder("tbd")



    def test_empty_string(self):

        self._assert_placeholder("")



    def test_non_string_input(self):

        # 0, None, [], {} — not strings — must NOT be treated as placeholders.

        self._assert_not_placeholder(0)

        self._assert_not_placeholder(None)

        self._assert_not_placeholder([])

        self._assert_not_placeholder({})



    def test_real_values_are_not_placeholders(self):

        self._assert_not_placeholder("gum_abc123XYZ-real-token")

        self._assert_not_placeholder("https://karma.myshopify.com")

        self._assert_not_placeholder("/home/user/.youtube_oauth.json")





class LaneStatusTests(unittest.TestCase):

    """_lane_status must reduce findings to [OK] / [NEEDS_CONFIG] / [OFFLINE] / [BLOCKED]."""



    def test_clean_lane_returns_ok(self):

        findings = {"creds": [("k", True, "configured")],

                    "services": [(":8188", True, "reachable")],

                    "vitals": []}

        tag, summary = preflight._lane_status("Test", findings)

        self.assertEqual(tag, "[OK]", summary)

        self.assertIn("ready", summary.lower())



    def test_missing_creds_returns_needs_config(self):

        findings = {"creds": [("gumroad_api_key", False, "placeholder")],

                    "services": [],

                    "vitals": []}

        tag, summary = preflight._lane_status("Test", findings)

        self.assertEqual(tag, "[NEEDS_CONFIG]", summary)

        self.assertIn("gumroad_api_key", summary)



    def test_offline_service_returns_offline(self):

        findings = {"creds": [],

                    "services": [("ComfyUI :8188", False, "offline")],

                    "vitals": []}

        tag, summary = preflight._lane_status("Test", findings)

        self.assertEqual(tag, "[OFFLINE]", summary)

        self.assertIn("ComfyUI", summary)



    def test_vital_only_failure_returns_offline_not_silent_ok(self):

        # The pre-fix bug reported [OK] silently. This is the regression test.

        findings = {"creds": [],

                    "services": [],

                    "vitals": [("live_api", False, "HTTP 503 simulated")]}

        tag, summary = preflight._lane_status("Test", findings)

        self.assertEqual(tag, "[OFFLINE]",

                         f"vital-only failure must surface as [OFFLINE], got {tag!r}")

        self.assertIn("live_api", summary)



    def test_publish_path_blocked_returns_blocked(self):

        findings = {"creds": [],

                    "services": [],

                    "vitals": [("publish_path", False, "blocked by config rule")]}

        tag, summary = preflight._lane_status("Test", findings)

        self.assertEqual(tag, "[BLOCKED]", summary)



    def test_combined_creds_and_services_returns_needs_config(self):

        findings = {"creds": [("k1", False, "placeholder")],

                    "services": [("ComfyUI :8188", False, "offline")],

                    "vitals": []}

        tag, summary = preflight._lane_status("Test", findings)

        self.assertEqual(tag, "[NEEDS_CONFIG]", summary)

        self.assertIn("k1", summary)

        self.assertIn("ComfyUI", summary)





class FormatOutputTests(unittest.TestCase):

    """Pure helpers must produce stable output."""



    def test_text_output_includes_total_denominator(self):

        rows = [(1, "Lane A", "[OK]", "ready", [])]

        out = preflight._format_text_output(

            rows, {"total": 5, "publishable": 1, "needs_config": 0, "blocked": 0, "offline": 0}

        )

        self.assertIn("Publishable now:    1/5", out)

        self.assertIn("Lane 1:", out)



    def test_text_output_dynamic_total(self):

        rows = [(1, "Lane A", "[OK]", "ready", [])]

        out = preflight._format_text_output(

            rows, {"total": 7, "publishable": 7, "needs_config": 0, "blocked": 0, "offline": 0}

        )

        self.assertIn("Publishable now:    7/7", out)

        self.assertIn("All 7 Lanes ready", out)



    def test_json_output_is_parseable(self):

        rows = [

            (1, "Lane A", "[OK]", "ready", []),

            (2, "Lane B", "[NEEDS_CONFIG]", "missing: k2", []),

        ]

        out = preflight._format_json_output(

            rows,

            {"total": 5, "publishable": 1, "needs_config": 1, "blocked": 0, "offline": 0},

            strict_would_fail=True,

        )

        parsed = json.loads(out)

        self.assertEqual(parsed["totals"]["total"], 5)

        self.assertEqual(parsed["totals"]["publishable"], 1)

        self.assertEqual(len(parsed["lanes"]), 2)

        # Publishable = derived boolean, complementary to status string

        self.assertTrue(parsed["lanes"][0]["publishable"])

        self.assertFalse(parsed["lanes"][1]["publishable"])

        self.assertEqual(parsed["lanes"][0]["status"], "OK")

        self.assertEqual(parsed["lanes"][1]["status"], "NEEDS_CONFIG")

        self.assertTrue(parsed["strict_would_fail"])



    def test_hardcoded_5_invariant(self):

        # Read the source and ensure no language-level lane count remains.

        src_path = Path(preflight.__file__)

        src = src_path.read_text(encoding="utf-8")

        # Look for `/5"` (string literal lane counts in f-strings) and `== 5` (numeric compare).

        self.assertNotIn("/5\"", src,

                         "hardcoded /5 in f-string literal — should use totals['total']")

        self.assertNotIn("/5'", src,

                         "hardcoded /5 in f-string literal — should use totals['total']")

        self.assertNotIn("== 5", src,

                         "hardcoded == 5 lane count — should use len(rows) or totals['total']")

        self.assertNotIn("!= 5", src,

                         "hardcoded != 5 lane count — should use len(rows) or totals['total']")





class MainExitCodeTests(unittest.TestCase):

    """main() exit codes — runs against real on-disk configs."""



    def test_default_returns_zero(self):

        buf = io.StringIO()

        with redirect_stdout(buf):

            rc = preflight.main([])

        self.assertEqual(rc, 0)

        # Default mode prints formatted text (not JSON).

        self.assertIn("SLEEP_CASH_SYSTEM", buf.getvalue())



    def test_json_returns_zero_and_outputs_only_json(self):

        buf = io.StringIO()

        with redirect_stdout(buf):

            rc = preflight.main(["--json"])

        self.assertEqual(rc, 0)

        # Output must be valid JSON — no leakage of the formatted header.

        parsed = json.loads(buf.getvalue())

        self.assertIn("lanes", parsed)

        self.assertNotIn("=======", buf.getvalue(),

                         "--json mode must not print the formatted header banner")



    def test_strict_returns_one_today(self):

        # On-disk today: 1/5 publishable, so --strict must exit 1.

        buf = io.StringIO()

        stderr_buf = io.StringIO()

        with redirect_stdout(buf), redirect_stderr(stderr_buf):

            rc = preflight.main(["--strict"])

        self.assertEqual(rc, 1)

        # Stderr should mention the refusing-to-proceed line.

        self.assertIn("refusing to proceed", stderr_buf.getvalue())



    def test_strict_with_json_still_exits_one(self):

        buf = io.StringIO()

        stderr_buf = io.StringIO()

        with redirect_stdout(buf), redirect_stderr(stderr_buf):

            rc = preflight.main(["--strict", "--json"])

        self.assertEqual(rc, 1)

        # stdout: parseable JSON, stderr: refusing-to-proceed line.

        parsed = json.loads(buf.getvalue())

        self.assertTrue(parsed["strict_would_fail"])



    def test_verbose_appends_per_lane_detail(self):

        """--verbose appends 'Per-Lane detail (verbose)' block after the summary.



        Regression coverage: prior refactors collapsed this path by accident.

        """

        buf = io.StringIO()

        with redirect_stdout(buf):

            rc = preflight.main(["--verbose"])

        self.assertEqual(rc, 0)

        out = buf.getvalue()

        self.assertIn("Per-Lane detail (verbose)", out,

                      "--verbose must append the per-Lane detail block")

        self.assertIn("Lane 1:", out)

        # LANE_PLAN[0] is Lane 1 (Gumroad), whose cred_keys include gumroad_api_key.

        self.assertIn("gumroad_api_key", out,

                      "verbose detail must surface credential key names")

        # Summary block must appear BEFORE the per-Lane detail block.

        summary_idx = out.find("Publishable now:")

        verbose_idx = out.find("Per-Lane detail (verbose)")

        self.assertGreater(summary_idx, -1)

        self.assertGreater(verbose_idx, summary_idx,

                            "verbose detail must come AFTER the summary section")



    def test_verbose_ignored_under_json(self):

        """--json + --verbose: stdout is pure JSON, no human-readable block.



        Regression coverage: --verbose should never leak the per-Lane block

        when --json is set (the JSON shape already carries that info).

        """

        buf = io.StringIO()

        with redirect_stdout(buf):

            rc = preflight.main(["--json", "--verbose"])

        self.assertEqual(rc, 0)

        out = buf.getvalue()

        self.assertNotIn("Per-Lane detail (verbose)", out,

                         "--verbose must be silently ignored under --json")

        # JSON still parses cleanly and the publishable boolean is derived.

        parsed = json.loads(out)

        self.assertIn("lanes", parsed)

        self.assertTrue(all("publishable" in ln and "status" in ln

                            for ln in parsed["lanes"]))



    def test_json_publishable_boolean_is_consistent_with_status(self):

        """Regression: JSON consumers must rely on `publishable == status == 'OK'`.



        If a future refactor breaks the boolean / tag pairing, downstream

        CI gates (--strict consumers) would silently misreport.

        """

        buf = io.StringIO()

        with redirect_stdout(buf):

            preflight.main(["--json"])

        parsed = json.loads(buf.getvalue())

        for ln in parsed["lanes"]:

            self.assertIsInstance(ln["publishable"], bool,

                                  f"Lane {ln['num']}: publishable must be bool")

            self.assertEqual(ln["publishable"], ln["status"] == "OK",

                             f"Lane {ln['num']}: publishable does not match status")





def main():

    """Run all tests and report."""

    print()

    print("=" * 70)

    print("PREFLIGHT — UNIT TESTS")

    print("=" * 70)

    loader = unittest.TestLoader()

    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)

    suite = loader.loadTestsFromModule(sys.modules[__name__])

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

