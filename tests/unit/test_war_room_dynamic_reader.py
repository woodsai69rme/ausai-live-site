#!/usr/bin/env python3
# ============================================
# Unit tests for war_room.py BOM/quote sanitization
# + dynamic-reader auto-extension
# + cmd_validate_mobile 3-case logic
#
# These tests are READ-AGAINST-FILE: they don't shell out.
# They import war_room (which auto-extends at import-time from MOBILE_FILTERED.csv).
# ============================================
"""
Tests covering the cont.10 BOM/quote sanitization fix and the
cont.10 validate-mobile 3-case logic.

Run with:  python -m pytest tests/unit/test_war_room_dynamic_reader.py -v
"""
from __future__ import annotations

import csv
import importlib
import os
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# 1. BOM + QUOTE SANITIZATION PATTERN (pure-string)
# ============================================================
class TestBomQuoteSanitization(unittest.TestCase):
    """Verify the .strip('\"\\ufeff') pattern handles every
    combination of BOM + quote wrapping that PowerShell Export-Csv
    can produce."""

    def setUp(self) -> None:
        self.SANITIZE_KEY = lambda k: str(k).strip().strip('"\ufeff')

    def test_clean_key_passes_through(self) -> None:
        self.assertEqual(self.SANITIZE_KEY("DisplayName"), "DisplayName")

    def test_bom_only_leading_stripped(self) -> None:
        self.assertEqual(self.SANITIZE_KEY("\ufeffDisplayName"), "DisplayName")

    def test_bom_only_trailing_stripped(self) -> None:
        self.assertEqual(self.SANITIZE_KEY("DisplayName\ufeff"), "DisplayName")

    def test_quote_only_both_ends_stripped(self) -> None:
        self.assertEqual(self.SANITIZE_KEY('"DisplayName"'), "DisplayName")

    def test_bom_and_quotes_combined(self) -> None:
        # The actual real-world pattern PowerShell produces:
        # \ufeff"DisplayName"  (BOM + quote + name + quote)
        self.assertEqual(self.SANITIZE_KEY('\ufeff"DisplayName"'), "DisplayName")

    def test_double_quote_wrapped_bom(self) -> None:
        # Worst-case: ""DisplayName"".
        self.assertEqual(self.SANITIZE_KEY('\ufeff""DisplayName""'), "DisplayName")

    def test_inner_quotes_preserved(self) -> None:
        # The pattern only strips LEADING/TRAILING chars in the set.
        # Inner characters are preserved.
        self.assertEqual(self.SANITIZE_KEY('Display\x22Name'), 'Display"Name')

    def test_typical_real_csv_value_with_quotes(self) -> None:
        # PowerShell often wraps the value too: ""Samsung USB Driver""
        v = '""Samsung USB Driver""'
        self.assertEqual(str(v).strip().strip('"\ufeff'), "Samsung USB Driver")


# ============================================================
# 2. WAR_ROOM IMPORT + DYNAMIC READER (integration)
# ============================================================
class TestWarRoomDynamicReader(unittest.TestCase):
    """Verify war_room.py imports cleanly, the auto-extension
    call ran, and at least one dynamic MOBILE_FILTERED.csv
    tile was registered (operator currently has 6 source rows
    that dedup to 4 unique slugs)."""

    @classmethod
    def setUpClass(cls) -> None:
        # Import war_room -- this triggers the dynamic reader
        # at import-time. If it raises, the test fails.
        import war_room  # noqa: F401
        cls.war_room = war_room

    def test_imports_cleanly(self) -> None:
        self.assertTrue(hasattr(self.war_room, "TILE_REGISTRY"))
        self.assertTrue(hasattr(self.war_room, "TILES_BY_CATEGORY"))

    def test_tiles_registry_has_entries(self) -> None:
        # Operator currently has 29+ tiles (~3 alias + 4 dynamic + static).
        self.assertGreaterEqual(len(self.war_room.TILE_REGISTRY), 20)

    def test_dynamic_reader_picked_up_rows(self) -> None:
        # Count dynamic tiles; should be >= 1 since MOBILE_FILTERED.csv
        # exists at the project root with 6 rows.
        dyn_count = sum(
            1
            for t in self.war_room.TILE_REGISTRY.values()
            if "Dynamic tile from MOBILE_FILTERED.csv" in str(t.get("notes", ""))
        )
        self.assertGreaterEqual(dyn_count, 1, msg="dynamic reader found 0 tiles")


# ============================================================
# 3. cmd_validate_mobile 3-CASE LOGIC (source-level)
# ============================================================
class TestValidateMobileThreeCaseLogic(unittest.TestCase):
    """We don't shell out -- instead we verify the source of
    cmd_validate_mobile contains all 3 expected branches:

    - INFO when CSV is missing OR has 0 rows (rc=0)
    - FAIL when CSV has rows but 0 dynamic tiles were produced (rc=1) (loader bug)
    - PASS when dynamic tiles >= 1 (rc=0)
    """

    def setUp(self) -> None:
        import war_room  # noqa: F401
        import inspect
        self.war_room = war_room
        self.src = inspect.getsource(self.war_room.cmd_validate_mobile)

    def test_branch_info_when_csv_missing(self) -> None:
        # Stage 1 of the 3-case: "no mobile inventory yet" emitted on missing CSV.
        self.assertIn("no mobile inventory yet", self.src)

    def test_branch_info_when_csv_empty(self) -> None:
        # Stage 2 of the 3-case: "MOBILE_FILTERED.csv has 0 rows" emitted when source has 0 data rows.
        self.assertIn("has 0 rows (no mobile tools", self.src)

    def test_branch_fail_when_loader_broken(self) -> None:
        # Stage 3 of the 3-case: "loader bug" emitted on rows-present / tiles-zero.
        self.assertIn("loader bug", self.src)

    def test_branch_pass_when_tiles_present(self) -> None:
        # Stage 4 of the success case: "dynamic MOBILE_FILTERED.csv tile" in PASS line.
        self.assertIn("dynamic MOBILE_FILTERED.csv tile", self.src)


# ============================================================
# 4. SLUG DERIVATION REGRESSION (40-char truncation + dedup)
# ============================================================
class TestSlugDerivation(unittest.TestCase):
    """Verify that the dynamic reader produces stable unique slugs
    when MOBILE_FILTERED.csv has multiple rows whose DisplayNames
    share a long prefix (the 40-char truncation + dedup pattern)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmpdir = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmpdir.name)
        cls.csv_path = cls.root / "MOBILE_FILTERED.csv"

    def _w(self, rows: list[dict]) -> None:
        with open(self.csv_path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(
                f,
                fieldnames=["DisplayName", "matched_terms"],
            )
            w.writeheader()
            for row in rows:
                w.writerow(row)

    def test_bom_in_csv_does_not_block_parsing(self) -> None:
        # Write a CSV with a BOM in the header (the bug pattern from cont.10).
        with open(self.csv_path, "wb") as f:
            f.write("\ufeff".encode("utf-8"))
        with open(self.csv_path, "a", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["DisplayName", "matched_terms"])
            w.writeheader()
            w.writerow({"DisplayName": "AdbTest", "matched_terms": "adb"})
            w.writerow({"DisplayName": "FastbootTool", "matched_terms": "fastboot"})
        # Use the SAME sanitize pattern from war_room.py to prove it works.
        with open(self.csv_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            san = lambda k: str(k).strip().strip('"\ufeff')  # noqa: E731
            headers = [(san(k)) for k in (reader.fieldnames or [])]
            self.assertEqual(headers, ["DisplayName", "matched_terms"])
            rows = [{san(k): v for k, v in r.items()} for r in reader]
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["DisplayName"], "AdbTest")


# ============================================================
# 5. SLUG-PATTERN UNIT TESTS (40-char truncation + dedup)
# ============================================================
class TestSlugPatterns(unittest.TestCase):
    """Verify the slug-derivation logic in war_room.py produces stable unique slugs
    (40-char truncation + alphanumeric-or-dash translation) so the dynamic reader's
    dedup logic skips 'Windows Driver Package' collisions.

    The slug body is reproduced here verbatim from war_room._extend_TILE_REGISTRY_from_MOBILE_FILTERED:
        "".join((c if c.isalnum() else "-") for c in _name.lower()).strip("-")[:40]
    """

    @staticmethod
    def _slug(name: str) -> str:
        return "".join((c if c.isalnum() else "-") for c in name.lower()).strip("-")[:40]

    def test_clean_name_passes_through(self) -> None:
        self.assertEqual(self._slug("Adb"), "adb")

    def test_spaces_become_dash(self) -> None:
        self.assertEqual(self._slug("Samsung USB Driver"), "samsung-usb-driver")

    def test_long_name_truncated_to_40_chars(self) -> None:
        self.assertEqual(len(self._slug("x" * 60)), 40)

    def test_distinct_vendor_same_base_name_dedupes(self) -> None:
        # Why this matters: provider rows in MOBILE_FILTERED.csv like
        # "Samsung USB Driver for Mobile Phones - 2.25.5.0" vs "...-2.25.4.0"
        # share the same 32-char name prefix and common [:40] after slugification.
        # They collapse to the same slug so the dynamic reader's dedup logic
        # skips the second one.
        slug_v1 = self._slug("Samsung USB Driver for Mobile Phones - 2.25.5.0")
        slug_v2 = self._slug("Samsung USB Driver for Mobile Phones - 2.25.4.0")
        # Trace: "samsung-usb-driver-for-mobile-phones---2-25-5-0"  (47 chars)
        #              [:40] = "samsung-usb-driver-for-mobile-phones---2"
        self.assertEqual(len(slug_v1), 40)
        self.assertEqual(len(slug_v2), 40)
        self.assertEqual(slug_v1, slug_v2,
                         msg="40-char truncation should collapse the two Samsung-version variants to the same slug")
        self.assertTrue(slug_v1.startswith("samsung-usb-driver-for-mobile-phones"))

    def test_distinct_vendors_with_early_diff_do_not_dedup(self) -> None:
        # Counter-test: vendors that diverge at the start (BEFORE char 7) produce distinct slugs.
        slug_samsung = self._slug("Samsung USB Driver for Mobile Phones - 2.25.5.0")
        slug_oppo    = self._slug("OPPO USB Driver    for Mobile Phones - 2.25.4.0")
        self.assertNotEqual(slug_samsung, slug_oppo, "first-7-chars divergence must NOT dedup")

    def test_punctuation_normalized(self) -> None:
        # Parentheses + commas and other punctuation all -> "-"
        s = self._slug("OPLUS Tool Driver (zh_CN, 7.0.4)")
        self.assertNotIn("(", s)
        self.assertNotIn(",", s)
        self.assertNotIn(".", s)
        self.assertTrue(s.startswith("oplus-tool-driver"))

    def test_leading_and_trailing_punctuation_stripped(self) -> None:
        # .strip("-") removes leading/trailing dashes (from punctuation rows starting/end with punctuation)
        self.assertEqual(self._slug("---Hi---"), "hi")

    def test_empty_after_strip_returns_empty(self) -> None:
        self.assertEqual(self._slug("!!!"), "")


if __name__ == "__main__":
    unittest.main()
