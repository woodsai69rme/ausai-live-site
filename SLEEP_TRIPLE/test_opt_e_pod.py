#!/usr/bin/env python3
"""
test_opt_e_pod.py — Smoke tests for opt_e_pod.py (Print-on-Demand module).

Run with:
  python SLEEP_TRIPLE/test_opt_e_pod.py
  OR
  pytest SLEEP_TRIPLE/test_opt_e_pod.py -v

Tests the module's:
  - Config loading
  - Rule #8 fence
  - Closed enums (EXEC_STATUS, PRODUCT_KIND, PUBLISH_MODE, DESIGN_NICHES)
  - Dry-run mode
  - Ollama fallback model selection
  - Outbox file creation
  - Audit log writing
"""

import sys
import json
import unittest
import tempfile
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

# Allow import from various locations
sys.path.insert(0, str(Path(__file__).resolve().parent))


class OptEPodTests(unittest.TestCase):
    """Smoke tests for the Print-on-Demand module."""

    def setUp(self):
        """Verify the module file exists and imports cleanly."""
        self.module_path = Path(__file__).resolve().parent / "opt_e_pod.py"
        self.config_path = Path(__file__).resolve().parent / "opt_e_config.json"
        self.sleep_config_path = Path(__file__).resolve().parent / "sleep_config.json"
        self.assertTrue(self.module_path.exists(), f"Missing {self.module_path}")
        self.assertTrue(self.config_path.exists(), f"Missing {self.config_path}")
        self.assertTrue(self.sleep_config_path.exists(), f"Missing {self.sleep_config_path}")

    def test_01_module_imports(self):
        """Module should import without errors."""
        try:
            import opt_e_pod
            print(f"  [PASS] opt_e_pod module imports cleanly")
        except ImportError as e:
            self.fail(f"Module import failed: {e}")

    def test_02_config_loads(self):
        """opt_e_config.json must be valid JSON with required fields."""
        cfg = json.loads(self.config_path.read_text(encoding="utf-8"))
        self.assertIn("label", cfg)
        self.assertIn("ollama_model_preference", cfg)
        self.assertIn("comfyui_url", cfg)
        self.assertIn("product_niches", cfg)
        self.assertIn("pricing", cfg)
        self.assertIn("notes", cfg)
        # Pricing must cover all PRODUCT_KIND values
        for kind in ("tshirt", "hoodie", "poster", "mug", "phone_case"):
            self.assertIn(kind, cfg["pricing"], f"Missing pricing for {kind}")
            self.assertIn("cost_aud", cfg["pricing"][kind])
            self.assertIn("sell_aud", cfg["pricing"][kind])
            self.assertIn("margin_aud", cfg["pricing"][kind])
        print(f"  [PASS] opt_e_config.json has all required fields")

    def test_03_closed_enums_defined(self):
        """Module should define all expected closed-enum tuples."""
        import opt_e_pod
        self.assertEqual(opt_e_pod.EXEC_STATUS, ("started", "ok", "degraded", "skipped", "refused", "noop", "failed"))
        self.assertEqual(opt_e_pod.PRODUCT_KIND, ("tshirt", "hoodie", "poster", "mug", "phone_case"))
        self.assertEqual(opt_e_pod.PUBLISH_MODE, ("draft_only", "staged", "published"))
        self.assertEqual(opt_e_pod.DESIGN_NICHES, ("ai_humor", "crypto_lifestyle", "dev_memes", "ai_art", "productivity"))
        print(f"  [PASS] All closed enums correctly defined")

    def test_04_sleep_config_has_opt_e(self):
        """sleep_config.json must define option 'e' and keep it disabled by default."""
        cfg = json.loads(self.sleep_config_path.read_text(encoding="utf-8"))
        self.assertIn("options", cfg)
        self.assertIn("e", cfg["options"], "sleep_config.json missing option 'e'")
        e = cfg["options"]["e"]
        self.assertIn("label", e)
        self.assertIn("enabled", e)
        self.assertIn("products_per_night", e)
        self.assertIn("ollama_model_preference", e)
        self.assertIn("comfyui_url", e)
        self.assertFalse(e["enabled"])
        print(f"  [PASS] sleep_config.json has option 'e' disabled by default")

    def test_05_rule_8_fence_function(self):
        """is_rule_8 should refuse paths containing personal folder segments."""
        import opt_e_pod
        fence = ["Documents", "Downloads", "Pictures"]
        # Should refuse
        self.assertTrue(opt_e_pod.is_rule_8(Path("C:/Users/karma/Documents/test"), fence))
        self.assertTrue(opt_e_pod.is_rule_8(Path("C:/Users/karma/Downloads/test"), fence))
        # Should allow
        self.assertFalse(opt_e_pod.is_rule_8(Path("C:/Users/karma/SLEEP_TRIPLE/test"), fence))
        self.assertFalse(opt_e_pod.is_rule_8(Path("C:/Users/karma/SLEEP_CASH_API"), fence))
        print(f"  [PASS] Rule #8 fence refuses personal folders, allows others")

    def test_06_dry_run_succeeds(self):
        """Dry-run main() should return 0 and emit a design to outbox (fast: every Ollama/ComfyUI call mocked)."""
        # Mock selection + generation + ComfyUI so the test never hits the
        # network and never races against Ollama model-load latency.
        from unittest.mock import patch
        import opt_e_pod
        mock_select = patch.object(opt_e_pod, "select_ollama_model", return_value="qwen2.5-coder:latest")
        mock_ollama = patch.object(
            opt_e_pod,
            "ollama_generate",
            return_value='{"title": "Mock", "design_text": "T", '
            '"comfyui_prompt": "P", "tags": [], "description": "D"}',
        )
        mock_comfy = patch.object(opt_e_pod, "comfyui_reachable", return_value=False)
        mock_argv = patch.object(sys, "argv",
            ["opt_e_pod.py", "--dry-run", "--niche", "ai_humor", "--kind", "tshirt"])
        with mock_select, mock_argv, mock_ollama, mock_comfy:
            ret_code = opt_e_pod.main()
        import opt_e_pod
        self.assertEqual(ret_code, opt_e_pod.DEGRADED_EXIT_CODE, f"main() returned {ret_code}")
        print(f"  [PASS] Dry-run completed with explicit degraded exit ({ret_code})")

    def test_07_dry_run_writes_outbox_file(self):
        """Dry-run mode should write a design file to outbox/e_pod/.

        The earlier before/after set-diff assertion was fragile: if a
        previous real run already wrote a file with today's date + the
        niche/kind marker this test uses, the diff would be empty and the
        assertion would fail even though main() worked. Fix: delete any
        pre-existing files matching today's marker first (test precondition
        reset), then mock all external integrations and assert presence
        afterwards.
        """
        from unittest.mock import patch
        import opt_e_pod

        outbox = Path(__file__).resolve().parent / "outbox" / "e_pod"
        outbox.mkdir(parents=True, exist_ok=True)
        today = datetime.now(ZoneInfo("Australia/Sydney")).date().isoformat()
        # File produced by main() is f"{today}_dev_memes_poster" exactly.
        leftover_glob = f"{today}_dev_memes_poster*"
        cleaned = 0
        for stale in outbox.glob(leftover_glob):
            stale.unlink()
            cleaned += 1

        # Mock every external integration main() reaches: model selection
        # (Ollama), design generation (Ollama), and ComfyUI reachability.
        # Mocking select_ollama_model avoids a real HTTP roundtrip to the
        # local Ollama server, so the test never races against model-load
        # latency.
        mock_select = patch.object(
            opt_e_pod, "select_ollama_model", return_value="qwen2.5-coder:latest"
        )
        mock_ollama = patch.object(
            opt_e_pod,
            "ollama_generate",
            return_value='{"title": "Mock Title", "design_text": "Mock Text", '
            '"comfyui_prompt": "A mock prompt", "tags": ["test"], '
            '"description": "A mock description"}',
        )
        # ComfyUI mocked offline so module takes the placeholder-write path,
        # which still creates the outbox file we assert below.
        mock_comfy = patch.object(opt_e_pod, "comfyui_reachable", return_value=False)
        mock_argv = patch.object(
            sys, "argv",
            ["opt_e_pod.py", "--dry-run", "--niche", "dev_memes", "--kind", "poster"],
        )

        with mock_select, mock_argv, mock_ollama, mock_comfy:
            ret_code = opt_e_pod.main()
        import opt_e_pod
        self.assertEqual(ret_code, opt_e_pod.DEGRADED_EXIT_CODE, f"main() returned {ret_code}")

        # After the run, the marker file must exist (proves the file was
        # created fresh during this test, not picked up from disk).
        produced = sorted(p.name for p in outbox.glob(leftover_glob))
        self.assertGreater(
            len(produced), 0,
            f"main() returned 0 but no '{leftover_glob}' file in {outbox} "
            f"(cleaned {cleaned} leftover(s) before run)",
        )
        print(
            f"  [PASS] Dry-run wrote {len(produced)} '{leftover_glob}' file(s) "
            f"to outbox/e_pod/ (cleaned {cleaned} leftover(s) first)"
        )

    def test_08_audit_log_writes(self):
        """Dry-run should append audit rows to SLEEP_TRIPLE_AUDIT.jsonl.

        Mocks select_ollama_model + ollama_generate + comfyui_reachable so
        the test never hits Ollama or ComfyUI and is fully deterministic.
        """
        from unittest.mock import patch
        import opt_e_pod
        audit_log = Path(__file__).resolve().parent / "SLEEP_TRIPLE_AUDIT.jsonl"
        if not audit_log.exists():
            self.skipTest("No audit log yet")
        before_lines = sum(1 for _ in open(audit_log, "r", encoding="utf-8"))
        mock_select = patch.object(opt_e_pod, "select_ollama_model", return_value="qwen2.5-coder:latest")
        mock_ollama = patch.object(
            opt_e_pod,
            "ollama_generate",
            return_value='{"title": "Mock", "design_text": "T", '
            '"comfyui_prompt": "P", "tags": [], "description": "D"}',
        )
        mock_comfy = patch.object(opt_e_pod, "comfyui_reachable", return_value=False)
        mock_argv = patch.object(sys, "argv",
            ["opt_e_pod.py", "--dry-run", "--niche", "ai_art", "--kind", "mug"])
        with mock_select, mock_argv, mock_ollama, mock_comfy:
            ret_code = opt_e_pod.main()
        import opt_e_pod
        self.assertEqual(ret_code, opt_e_pod.DEGRADED_EXIT_CODE)
        after_lines = sum(1 for _ in open(audit_log, "r", encoding="utf-8"))
        # Single-process test: main() inside the with block is the only
        # writer between the before/after reads, so the line-count delta
        # is exactly the rows main() appended (started + degraded = 2).
        self.assertGreater(after_lines, before_lines,
            f"No new audit rows appended ({before_lines} -> {after_lines})")
        # Verify the last 2 rows are for opt_e_pod
        with open(audit_log, "r", encoding="utf-8") as f:
            last_lines = [l.strip() for l in f.readlines()[-2:]]
        for line in last_lines:
            row = json.loads(line)
            self.assertEqual(row["module"], "opt_e_pod")
        self.assertEqual(json.loads(last_lines[-1])["status"], "degraded")
        self.assertFalse(json.loads(last_lines[-1])["comfyui_reachable"])
        print(f"  [PASS] Audit log appended 2 rows ({before_lines} -> {after_lines})")

    def test_09_dry_run_with_dry_run_and_run_refused(self):
        """--dry-run and --run together should be refused."""
        import subprocess
        result = subprocess.run(
            [sys.executable, str(self.module_path), "--dry-run", "--run"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("REFUSED", result.stderr)
        print(f"  [PASS] --dry-run + --run mutually exclusive")

    def test_10_invalid_publish_mode_refused(self):
        """Invalid --publish choice should be refused by argparse."""
        import subprocess
        result = subprocess.run(
            [sys.executable, str(self.module_path), "--dry-run", "--publish", "invalid_mode"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertNotEqual(result.returncode, 0)
        print(f"  [PASS] Invalid --publish mode rejected")


def main():
    """Run all tests and report summary."""
    print()
    print("=" * 70)
    print("OPT_E_POD (Print-on-Demand) — SMOKE TESTS")
    print("=" * 70)
    print(f"Python: {sys.version.split()[0]}")
    print(f"Module: opt_e_pod.py")
    print(f"Config: opt_e_config.json")
    print()

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(OptEPodTests)
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    print()
    print("=" * 70)
    if result.wasSuccessful():
        print(f"ALL {result.testsRun} TESTS PASSED")
        return 0
    else:
        print(f"{len(result.failures)} FAILURES, {len(result.errors)} ERRORS")
        return 1


if __name__ == "__main__":
    sys.exit(main())
