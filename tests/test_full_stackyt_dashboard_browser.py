"""Optional browser smoke test for the generated Full Stack dashboard.

The test is intentionally local-only: it serves the repository through a
loopback HTTP server, never follows external links, and does not write project
artifacts. It skips when Playwright or the locally installed Chrome channel is
unavailable.
"""
from __future__ import annotations

import functools
import threading
import unittest
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

try:
    from playwright.sync_api import Error as PlaywrightError
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - environment-dependent optional test
    PlaywrightError = Exception  # type: ignore[assignment]
    sync_playwright = None  # type: ignore[assignment]

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(sync_playwright is not None, "Playwright is not installed")
class DashboardBrowserSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        handler = functools.partial(SimpleHTTPRequestHandler, directory=str(ROOT))
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def test_search_filter_and_keyboard_detail_interactions(self) -> None:
        console_errors: list[str] = []
        with sync_playwright() as playwright:
            try:
                browser = playwright.chromium.launch(channel="chrome", headless=True)
            except PlaywrightError as exc:
                self.skipTest(f"local Chrome channel unavailable: {exc}")
            page = browser.new_page()
            page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
            page.goto(f"{self.base_url}/FULL_STACKYT_DASHBOARD.html", wait_until="networkidle")

            initial_count = page.locator("#rows tr").count()
            self.assertGreater(initial_count, 0)
            self.assertIn("of 99 items", page.locator("#resultCount").inner_text())
            self.assertIn("Saved snapshot:", page.locator("#freshness").inner_text())

            ask = page.get_by_label("Ask Buffy a catalog question")
            ask.fill("What is OpenCut?")
            page.get_by_role("button", name="Ask").click()
            self.assertIn("OpenCut:", page.locator("#askAnswer").inner_text())
            ask.fill("Compare OpenCut and OpenMontage")
            page.get_by_role("button", name="Ask").click()
            self.assertIn("Comparison:", page.locator("#askAnswer").inner_text())
            ask.fill("Compare Open and React")
            page.get_by_role("button", name="Ask").click()
            self.assertIn("Ambiguous comparison:", page.locator("#askAnswer").inner_text())
            ask.fill("Install OpenCut")
            page.get_by_role("button", name="Ask").click()
            self.assertIn("Refused:", page.locator("#askAnswer").inner_text())
            ask.fill("What is OpenCut?")
            ask.press("Enter")
            self.assertIn("OpenCut:", page.locator("#askAnswer").inner_text())

            search = page.get_by_label("Search catalog")
            search.fill("OpenCut")
            self.assertGreater(page.locator("#rows tr").count(), 0)
            self.assertIn("OpenCut", page.locator("#rows").inner_text())

            page.get_by_label("Filter by source").select_option("verified")
            self.assertLessEqual(page.locator("#rows tr").count(), initial_count)

            # Reset the source filter so the searched item remains available,
            # then activate its detail button through keyboard interaction.
            page.get_by_label("Filter by source").select_option("")
            detail_button = page.locator('#rows button[aria-label*="OpenCut"]').first
            detail_button.focus()
            detail_button.press("Enter")
            self.assertTrue(page.locator("#detail.open").is_visible())
            self.assertIn("OpenCut", page.locator("#detailTitle").inner_text())
            self.assertEqual(console_errors, [])
            browser.close()


if __name__ == "__main__":
    unittest.main()
