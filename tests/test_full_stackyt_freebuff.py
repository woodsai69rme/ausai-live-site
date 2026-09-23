"""Tests for the read-only Full Stack Freebuff wrapper."""
from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import full_stackyt_freebuff as skill
import full_stackyt_query as query


class FullStackytFreebuffTests(unittest.TestCase):
    def test_explain_returns_structured_evidence_and_related_video(self):
        response = skill.explain("OpenCut")

        self.assertEqual(response["status"], "ok")
        self.assertEqual(response["mode"], "read-only")
        self.assertEqual(response["intent"], "explain")
        self.assertEqual(response["results"][0]["name"], "OpenCut")
        self.assertTrue(response["explanation"]["sources"])
        self.assertTrue(response["explanation"]["record_paths"])
        self.assertTrue(response["explanation"]["record_paths"][0].startswith("FULL_STACKYT_EXECUTION_PACK.json#/records/"))
        self.assertEqual(response["results"][0]["execution_record_path"], response["explanation"]["record_paths"][0])
        self.assertTrue(response["explanation"]["related_videos"])
        self.assertTrue(response["explanation"]["not_proven"])
        self.assertTrue(response["explanation"]["next_safe_action"])
        self.assertFalse(response["safety"]["catalog_execution"])
        self.assertFalse(response["safety"]["external_actions"])

    def test_explain_exposes_proven_citations_and_freshness(self):
        response = skill.explain("Claude Code")
        self.assertTrue(response["explanation"]["proven"])
        self.assertTrue(response["explanation"]["citations"])
        citation = response["explanation"]["citations"][0]
        self.assertIn("official_source_url", citation)
        self.assertIn(response["validation"]["freshness"]["state"], {"current", "aging", "stale", "future-dated", "unknown"})
        self.assertIn("evidence_policy", response["validation"])
        self.assertEqual(response["results"][0]["status"], "Backlog")

    def test_freshness_states_are_deterministic_for_missing_future_and_stale_timestamps(self):
        now = datetime(2026, 8, 9, tzinfo=timezone.utc)
        missing = query.freshness_metadata({"refresh": {}}, now=now)
        future = query.freshness_metadata({"refresh": {"refreshed_at_utc": "2026-08-10T00:00:00Z"}}, now=now)
        stale = query.freshness_metadata({"refresh": {"refreshed_at_utc": "2026-06-01T00:00:00Z"}}, now=now)
        malformed = query.freshness_metadata({"refresh": {"refreshed_at_utc": "not-a-date"}}, now=now)
        self.assertEqual(missing["state"], "unknown")
        self.assertEqual(future["state"], "future-dated")
        self.assertEqual(stale["state"], "stale")
        self.assertEqual(malformed["state"], "unknown")

    def test_compare_returns_two_items_and_explicit_limits(self):
        response = skill.compare("OpenCut", "OpenMontage")
        self.assertEqual(response["status"], "ok")
        self.assertEqual(response["intent"], "compare")
        self.assertEqual([item["name"] for item in response["results"]], ["OpenCut", "OpenMontage"])
        self.assertTrue(response["explanation"]["proven"])
        self.assertTrue(any("benchmark" in value for value in response["explanation"]["not_proven"]))
        self.assertTrue(response["explanation"]["citations"])

    def test_compare_and_freshness_ambiguous_or_missing_are_explicit(self):
        ambiguous = skill.compare("Open", "OpenCut")
        self.assertEqual(ambiguous["status"], "ambiguous")
        routed = skill.ask("Compare OpenCut and OpenMontage")
        self.assertEqual(routed["intent"], "compare")
        self.assertEqual(routed["status"], "ok")
        broad = skill.ask("Compare Open and React")
        self.assertEqual(broad["status"], "ambiguous")

    def test_response_contract_fields_exist_for_refusal_and_refresh(self):
        for response in (skill.ask("Install OpenCut"), skill.ask("When should this package be refreshed?")):
            self.assertIn("proven", response["explanation"])
            self.assertIn("citations", response["explanation"])

    def test_ask_routes_video_mentions_and_summary(self):
        videos = skill.ask("Which videos mention MCP?")
        self.assertEqual(videos["status"], "ok")
        self.assertEqual(videos["intent"], "video_search")
        self.assertTrue(videos["results"])
        self.assertIn("title", videos["explanation"]["evidence_state"])
        self.assertIn("youtube.com/watch", videos["explanation"]["related_videos"][0]["url"])

        counts = skill.ask("What are the package counts?")
        self.assertEqual(counts["intent"], "summary")
        self.assertEqual(counts["results"][0]["catalog_videos"], 115)
        self.assertEqual(counts["results"][0]["catalog_items"], 99)

    def test_ask_filters_high_risk_browser_or_desktop_tools(self):
        response = skill.ask("Show high-risk browser or desktop tools")

        self.assertEqual(response["status"], "ok")
        self.assertTrue(response["results"])
        self.assertTrue(all(item["risk"] == "High" for item in response["results"]))
        self.assertTrue(all(any(term in item["category"].casefold() for term in ("browser", "desktop")) for item in response["results"]))

    def test_ask_supports_filters_and_explainable_text(self):
        response = skill.ask("Which tools are high risk?")

        self.assertEqual(response["status"], "ok")
        self.assertTrue(response["results"])
        self.assertTrue(all(item["risk"] == "High" for item in response["results"]))
        rendered = skill.format_response(response)
        self.assertIn("Evidence:", rendered)
        self.assertIn("Records: FULL_STACKYT_EXECUTION_PACK.json#/records/", rendered)
        self.assertIn("Not proven:", rendered)
        self.assertIn("Next safe action:", rendered)
        self.assertIn("read-only", rendered)

    def test_side_effect_requests_are_refused_without_loading_or_mutating_catalog(self):
        with patch.object(skill, "_load", side_effect=AssertionError("must not load for refusal")):
            response = skill.ask("Install OpenCut and run it")
            run_response = skill.ask("Run the OpenCut tool")
            load_response = skill.ask("Load the OpenCut skill")

        self.assertEqual(response["status"], "refused")
        self.assertEqual(run_response["status"], "refused")
        self.assertEqual(load_response["status"], "refused")
        self.assertEqual(response["intent"], "refusal")
        self.assertIn("cannot install", response["answer"])
        self.assertFalse(response["safety"]["external_actions"])

    def test_unknown_item_is_explicitly_not_found(self):
        response = skill.explain("Definitely Not A Catalog Item")

        self.assertEqual(response["status"], "not_found")
        self.assertFalse(response["results"])
        self.assertTrue(response["explanation"]["ambiguity"])

    def test_refresh_guidance_validates_the_package(self):
        response = skill.ask("When should this package be refreshed?")
        self.assertEqual(response["status"], "ok")
        self.assertTrue(response["validation"]["catalog_loaded"])
        self.assertTrue(response["validation"]["execution_pack_loaded"])

    def test_read_only_run_word_is_not_automatically_refused(self):
        with patch.object(skill, "search", return_value={"status": "ok", "answer": "read-only"}) as mocked:
            response = skill.ask("Run a read-only search for OpenCut")
        self.assertEqual(response["status"], "ok")
        mocked.assert_called_once()

    def test_public_urls_pass_private_path_validation(self):
        skill._assert_public_safe(
            {"schema_version": "1.0", "url": "https://example.com/source"},
            {"schema_version": "1.0", "records": []},
        )

    def test_private_path_validation_does_not_answer_from_local_data(self):
        catalog = {"schema_version": "1.0", "private": "C:\\\\Users\\\\private.json"}
        pack = {"schema_version": "1.0", "records": []}
        with self.assertRaises(ValueError):
            skill._assert_public_safe(catalog, pack)

    def test_validation_failure_does_not_answer_from_partial_data(self):
        with patch.object(skill, "_load", side_effect=ValueError("safety invariants failed")):
            response = skill.explain("OpenCut")

        self.assertEqual(response["status"], "unavailable")
        self.assertEqual(response["results"], [])
        self.assertIn("unavailable or stale", response["answer"])
        self.assertIn("safety invariants failed", response["validation"]["error"])

    def test_cli_json_is_machine_readable(self):
        # Exercise the API's serialization contract without spawning a process.
        payload = skill.ask("What is OpenCut?")
        encoded = json.dumps(payload, ensure_ascii=False)
        decoded = json.loads(encoded)
        self.assertEqual(decoded["results"][0]["name"], "OpenCut")
        self.assertIn("schema_version", decoded)


if __name__ == "__main__":
    unittest.main()
