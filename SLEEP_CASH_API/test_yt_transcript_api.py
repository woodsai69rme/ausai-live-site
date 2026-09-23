#!/usr/bin/env python3
"""
test_yt_transcript_api.py — Smoke tests for the YouTube Transcript API.

Run with:
  python SLEEP_CASH_API/test_yt_transcript_api.py
  OR
  pytest SLEEP_CASH_API/test_yt_transcript_api.py -v

Coverage includes:
  - Root, health, pricing, transcript formats, validation, rate limits, and CORS
  - Cryptographically random Stripe-issued API keys
  - Legacy key compatibility
  - Explicit opt-in for unsigned local webhooks
  - Generic invalid-signature errors
  - Verification of valid signed webhooks before activation
"""

import json
import sys
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

# Add parent to path so import works from any cwd
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from fastapi.testclient import TestClient
    from SLEEP_CASH_API.kv_store import rate_limiter
    from SLEEP_CASH_API.youtube_transcript_api_service import (
        app, FREE_TIER_DAILY_LIMIT,
    )
    HAS_FASTAPI = True
except ImportError as e:
    print(f"SKIP: fastapi not available ({e})")
    HAS_FASTAPI = False


def _reset_rate_limits() -> None:
    """Clear in-memory rate-limit state using the limiter's per-IP locks."""
    for lock in rate_limiter._locks.values():
        lock.acquire()
    try:
        rate_limiter._in_memory.clear()
    finally:
        for lock in rate_limiter._locks.values():
            lock.release()


# Known transcript-available video ID (Rick Astley — never going to give you up)
KNOWN_VIDEO_ID = "dQw4w9WgXcQ"


def _unique_event_id(label: str) -> str:
    """Avoid collisions with shared Redis when tests run repeatedly."""
    return f"evt_{label}_{uuid.uuid4().hex}"


def _build_mock_transcript():
    """Construct a mock FetchedTranscript-like object with three snippets."""
    snippet = type("MockSnippet", (), {"text": "Never gonna give you up", "start": 0.0, "duration": 2.5})
    fetched = type("MockFetched", (), {"snippets": [snippet, snippet, snippet]})
    return fetched()


@unittest.skipUnless(HAS_FASTAPI, "fastapi not installed")
class TranscriptAPITests(unittest.TestCase):
    """Smoke tests for the YouTube Transcript Extractor API."""

    def setUp(self):
        self.client = TestClient(app)
        _reset_rate_limits()
        # Clear the local webhook replay cache between tests. Production uses
        # shared Redis; these tests deliberately isolate the singleton fallback.
        import SLEEP_CASH_API.youtube_transcript_api_service as service
        service.cache._in_memory.clear()
        # Mock YouTubeTranscriptApi to avoid YouTube anti-bot rate limiting and
        # ensure tests are deterministic. This makes the tests true unit tests
        # of our FastAPI code, not integration tests against YouTube.
        self._fetch_patcher = patch(
            "SLEEP_CASH_API.youtube_transcript_api_service.YouTubeTranscriptApi.fetch",
            return_value=_build_mock_transcript(),
        )
        self._fetch_patcher.start()

    def tearDown(self):
        self._fetch_patcher.stop()

    def test_01_root_returns_api_info(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("service", data)
        self.assertIn("YouTube Transcript", data["service"])
        self.assertIn("free_tier_limit", data)
        self.assertIn("pro_pricing", data)
        print(f"  [PASS] Root endpoint returns API info")

    def test_02_pricing_page(self):
        r = self.client.get("/pricing")
        self.assertEqual(r.status_code, 200)
        self.assertIn("A$19", r.text)
        self.assertIn("Subscribe", r.text)
        print("  [PASS] /pricing returns checkout page")

    def test_03_healthz_returns_ok(self):
        r = self.client.get("/healthz")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("timestamp", data)
        print(f"  [PASS] /healthz returns status=ok")

    def test_04_transcript_json_format(self):
        r = self.client.get(f"/api/v1/transcript?video_id={KNOWN_VIDEO_ID}&format=json")
        self.assertEqual(r.status_code, 200, f"Expected 200, got {r.status_code}: {r.text[:200]}")
        data = r.json()
        self.assertEqual(data["video_id"], KNOWN_VIDEO_ID)
        self.assertGreater(data["segment_count"], 0)
        self.assertGreater(data["total_duration_seconds"], 0)
        self.assertIsInstance(data["transcript"], list)
        if data["transcript"]:
            seg = data["transcript"][0]
            self.assertIn("text", seg)
            self.assertIn("start", seg)
            self.assertIn("duration", seg)
        print(f"  [PASS] JSON format: {data['segment_count']} segments, {data['total_duration_seconds']:.1f}s")

    def test_05_transcript_text_format(self):
        r = self.client.get(f"/api/v1/transcript?video_id={KNOWN_VIDEO_ID}&format=text")
        self.assertEqual(r.status_code, 200)
        self.assertIn("text/plain", r.headers.get("content-type", ""))
        self.assertGreater(len(r.text), 0)
        print(f"  [PASS] Text format: {len(r.text)} chars returned")

    def test_06_transcript_srt_format(self):
        r = self.client.get(f"/api/v1/transcript?video_id={KNOWN_VIDEO_ID}&format=srt")
        self.assertEqual(r.status_code, 200)
        self.assertIn("text/plain", r.headers.get("content-type", ""))
        # SRT should have arrow separator
        self.assertIn("-->", r.text)
        print(f"  [PASS] SRT format: contains SRT timing markers")

    def test_07_invalid_video_id_length(self):
        # Too short (10 chars instead of 11)
        r = self.client.get("/api/v1/transcript?video_id=abc1234567")
        self.assertEqual(r.status_code, 422)
        print(f"  [PASS] Short video ID rejected (422)")

    def test_08_invalid_format_rejected(self):
        r = self.client.get(f"/api/v1/transcript?video_id={KNOWN_VIDEO_ID}&format=xml")
        self.assertEqual(r.status_code, 422)
        print(f"  [PASS] Invalid format rejected (422)")

    def test_09_missing_video_id(self):
        r = self.client.get("/api/v1/transcript")
        self.assertEqual(r.status_code, 422)
        print(f"  [PASS] Missing video_id rejected (422)")

    def test_10_cors_headers_present(self):
        r = self.client.get("/", headers={"Origin": "https://example.com"})
        self.assertEqual(r.status_code, 200)
        # CORS middleware should set allow-origin
        self.assertIn("access-control-allow-origin", {k.lower() for k in r.headers.keys()})
        print(f"  [PASS] CORS headers configured")

    def test_11_rate_limit_free_tier(self):
        """Make FREE_TIER_DAILY_LIMIT free-tier requests successfully, then the next must hit rate limit."""
        calls: list[str] = []

        def fake_check(ip: str, limit: int, window_hours: int) -> tuple[bool, int]:
            calls.append(ip)
            if len(calls) > limit:
                return False, 0
            return True, limit - len(calls)

        with patch(
            "SLEEP_CASH_API.youtube_transcript_api_service.rate_limiter.check",
            side_effect=fake_check,
        ):
            client = TestClient(app)
            statuses = []
            for _ in range(FREE_TIER_DAILY_LIMIT):
                r = client.get(f"/api/v1/transcript?video_id={KNOWN_VIDEO_ID}&format=text")
                statuses.append(r.status_code)
            for i, code in enumerate(statuses, 1):
                self.assertEqual(code, 200, f"Request {i}/{FREE_TIER_DAILY_LIMIT} should succeed but got {code}")
            over_limit = client.get(f"/api/v1/transcript?video_id={KNOWN_VIDEO_ID}&format=text")
            self.assertEqual(over_limit.status_code, 429)
        self.assertEqual(len(calls), FREE_TIER_DAILY_LIMIT + 1)
        print(f"  [PASS] First {FREE_TIER_DAILY_LIMIT} succeed (200), next is rejected (429)")

    def test_12_stripe_issued_api_key_is_random(self):
        """Checkout webhooks issue random keys and retain legacy key compatibility."""
        import SLEEP_CASH_API.youtube_transcript_api_service as service

        legacy_key = "ytx_existing_customer_1720000000"

        class IsolatedKeyStore:
            def __init__(self):
                self.keys = set()

            def add_key(self, key: str, email: str, customer_id: str) -> None:
                self.keys.add(key)

            def is_valid(self, key: str) -> bool:
                return key in self.keys

            def deactivate_by_customer(self, customer_id: str) -> None:
                pass

        isolated_store = IsolatedKeyStore()
        with patch.object(service, "api_key_store", isolated_store):
            isolated_store.add_key(legacy_key, "legacy@example.com", "cus_legacy")
            self.assertTrue(isolated_store.is_valid(legacy_key))

        generated_keys: list[str] = []

        def capture_key(
            key: str,
            email: str,
            customer_id: str,
            stripe_event_id: str | None = None,
        ) -> None:
            generated_keys.append(key)

        event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer_details": {"email": "customer@example.com"},
                    "customer": "cus_test_123",
                },
            },
            "id": _unique_event_id("secure_key"),
        }
        with patch.object(service.api_key_store, "add_key", side_effect=capture_key), patch.object(
            service.api_key_store, "get_key_by_event_id", return_value=None
        ), patch.object(service, "STRIPE_WEBHOOK_SECRET", ""), patch.object(
            service, "STRIPE_WEBHOOK_ALLOW_UNSIGNED", True
        ), patch.object(
            service, "STRIPE_WEBHOOK_IS_DEVELOPMENT", True
        ):
            response = self.client.post("/webhook/stripe", json=event)
            duplicate_response = self.client.post("/webhook/stripe", json=event)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(generated_keys), 1)
        self.assertEqual(duplicate_response.status_code, 200)
        self.assertEqual(duplicate_response.json()["reason"], "duplicate")
        self.assertRegex(generated_keys[0], r"^ytx_[0-9a-f]{64}$")
        self.assertNotIn("customer", generated_keys[0])
        self.assertNotRegex(generated_keys[0], r"_\d{10,}$")
        print("  [PASS] Stripe webhook issues a cryptographically random API key")

    def test_13_unsigned_stripe_webhook_requires_opt_in(self):
        """Missing verification config must not activate a subscription."""
        import SLEEP_CASH_API.youtube_transcript_api_service as service

        event = {
            "type": "checkout.session.completed",
            "data": {"object": {"customer_details": {"email": "blocked@example.com"}}},
        }
        with patch.dict("os.environ", {"APP_ENV": "production", "NODE_ENV": "development"}, clear=False), patch.object(
            service, "STRIPE_WEBHOOK_SECRET", ""
        ), patch.object(service, "STRIPE_WEBHOOK_ALLOW_UNSIGNED", True), patch.object(
            service.cache, "is_durable", return_value=False
        ), patch.object(service.api_key_store, "add_key") as add_key:
            response = self.client.post("/webhook/stripe", json=event)

        self.assertEqual(response.status_code, 503)
        add_key.assert_not_called()
        print("  [PASS] Unsigned webhook is rejected without explicit opt-in")

    def test_14_invalid_signed_webhook_does_not_leak_error_details(self):
        """Signature failures are generic and never activate a subscription."""
        import SLEEP_CASH_API.youtube_transcript_api_service as service

        event = {"type": "checkout.session.completed", "data": {"object": {}}}
        with patch.object(service, "STRIPE_WEBHOOK_SECRET", "whsec_test_secret"), patch(
            "stripe.Webhook.construct_event",
            side_effect=ValueError("sensitive verification detail"),
        ), patch.object(service, "STRIPE_WEBHOOK_IS_DEVELOPMENT", False), patch.object(
            service.api_key_store, "add_key"
        ) as add_key:
            response = self.client.post(
                "/webhook/stripe",
                json=event,
                headers={"Stripe-Signature": "invalid"},
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Stripe signature verification failed")
        self.assertNotIn("sensitive verification detail", response.text)
        add_key.assert_not_called()
        print("  [PASS] Invalid signed webhook returns a generic error")

    def test_15_valid_signed_webhook_is_verified_before_activation(self):
        """A configured webhook secret requires construct_event verification."""
        import SLEEP_CASH_API.youtube_transcript_api_service as service

        event = {
            "id": _unique_event_id("signed"),
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer_details": {"email": "signed@example.com"},
                    "customer": "cus_signed_123",
                }
            },
        }
        generated_keys: list[str] = []
        with patch.object(service, "STRIPE_WEBHOOK_SECRET", "whsec_test_secret"), patch(
            "stripe.Webhook.construct_event", return_value=event
        ) as construct_event, patch.object(service, "STRIPE_WEBHOOK_IS_DEVELOPMENT", False), patch.object(
            service.api_key_store,
            "add_key",
            side_effect=lambda key, email, customer, stripe_event_id=None: generated_keys.append(key),
        ):
            response = self.client.post(
                "/webhook/stripe",
                json={"ignored": "body"},
                headers={"Stripe-Signature": "valid-test-signature"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(generated_keys), 1)
        construct_event.assert_called_once()
        args = construct_event.call_args.args
        self.assertEqual(args[0], b'{"ignored":"body"}')
        self.assertEqual(args[1], "valid-test-signature")
        self.assertEqual(args[2], "whsec_test_secret")
        print("  [PASS] Valid signed webhook is verified before activation")

    def test_16_webhook_lease_renews_until_stopped(self):
        """A long-running webhook keeps its owner claim alive."""
        import time
        import SLEEP_CASH_API.youtube_transcript_api_service as service

        claim = {"status": "processing", "owner": "lease-test"}
        with patch.object(service, "STRIPE_WEBHOOK_PROCESSING_TTL_SECONDS", 1), patch.object(
            service.cache, "set_if_value", return_value=True
        ) as renew:
            stop_event, lease_lost = service._start_webhook_lease_renewal(
                "stripe:webhook:event:lease-test", claim
            )
            time.sleep(1.1)
            stop_event.set()

        self.assertFalse(lease_lost.is_set())
        self.assertGreaterEqual(renew.call_count, 1)
        self.assertEqual(renew.call_args.args[0], "stripe:webhook:event:lease-test")
        self.assertEqual(renew.call_args.args[1], claim)
        print("  [PASS] Webhook processing lease renews while running")

    def test_17_lost_claim_cannot_acknowledge_success(self):
        """A failed owner-conditional completion is retryable, not HTTP 200."""
        import SLEEP_CASH_API.youtube_transcript_api_service as service

        event = {
            "id": _unique_event_id("lost_claim"),
            "type": "customer.subscription.deleted",
            "data": {"object": {"customer": "cus_lost_claim"}},
        }
        with patch.object(service, "STRIPE_WEBHOOK_SECRET", "whsec_test_secret"), patch(
            "stripe.Webhook.construct_event", return_value=event
        ), patch.object(service, "STRIPE_WEBHOOK_IS_DEVELOPMENT", False), patch.object(
            service.cache, "set_if_value", return_value=False
        ), patch.object(service.api_key_store, "deactivate_by_customer"):
            response = self.client.post(
                "/webhook/stripe",
                json={"ignored": "body"},
                headers={"Stripe-Signature": "valid-test-signature"},
            )

        self.assertEqual(response.status_code, 409)
        print("  [PASS] Lost webhook claim cannot acknowledge success")

    def test_18_in_progress_duplicate_is_retryable(self):
        """A concurrent duplicate receives 409 instead of a success acknowledgement."""
        import SLEEP_CASH_API.youtube_transcript_api_service as service

        event = {
            "id": _unique_event_id("in_progress"),
            "type": "checkout.session.completed",
            "data": {"object": {}},
        }
        with patch.object(service, "STRIPE_WEBHOOK_SECRET", "whsec_test_secret"), patch(
            "stripe.Webhook.construct_event", return_value=event
        ), patch.object(service, "STRIPE_WEBHOOK_IS_DEVELOPMENT", False), patch.object(
            service.cache, "set_if_absent", return_value=False
        ), patch.object(service.cache, "get", return_value={"status": "processing"}), patch.object(
            service.api_key_store, "add_key"
        ) as add_key:
            response = self.client.post(
                "/webhook/stripe",
                json={"ignored": "body"},
                headers={"Stripe-Signature": "valid-test-signature"},
            )

        self.assertEqual(response.status_code, 409)
        add_key.assert_not_called()
        print("  [PASS] In-progress duplicate remains retryable")

    def test_19_failed_processing_releases_event_claim(self):
        """A handler failure removes its claim so Stripe can retry."""
        import SLEEP_CASH_API.youtube_transcript_api_service as service

        event = {
            "id": _unique_event_id("failure_cleanup"),
            "type": "checkout.session.completed",
            "data": {"object": {}},
        }
        with patch.object(service, "STRIPE_WEBHOOK_SECRET", "whsec_test_secret"), patch(
            "stripe.Webhook.construct_event", return_value=event
        ), patch.object(service, "STRIPE_WEBHOOK_IS_DEVELOPMENT", False), patch.object(
            service.api_key_store, "get_key_by_event_id", return_value=None
        ), patch.object(
            service.api_key_store, "add_key", side_effect=RuntimeError("storage unavailable")
        ):
            with self.assertRaises(RuntimeError):
                import asyncio
                asyncio.run(service.stripe_webhook(self._request_for_json({"ignored": "body"})))

        self.assertIsNone(service.cache.get(service._webhook_event_cache_key(event["id"])))
        print("  [PASS] Failed processing releases the event claim")

    def test_20_production_requires_durable_replay_storage(self):
        """Production webhooks fail closed when shared replay storage is absent."""
        import SLEEP_CASH_API.youtube_transcript_api_service as service

        event = {
            "id": _unique_event_id("production_storage"),
            "type": "checkout.session.completed",
            "data": {"object": {}},
        }
        with patch.object(service, "STRIPE_WEBHOOK_SECRET", "whsec_test_secret"), patch(
            "stripe.Webhook.construct_event", return_value=event
        ), patch.object(service, "_is_production_environment", return_value=True), patch.object(
            service.cache, "is_durable", return_value=False
        ), patch.object(service.api_key_store, "add_key") as add_key:
            response = self.client.post(
                "/webhook/stripe",
                json={"ignored": "body"},
                headers={"Stripe-Signature": "valid-test-signature"},
            )

        self.assertEqual(response.status_code, 503)
        add_key.assert_not_called()
        print("  [PASS] Production requires durable replay storage")

    def test_21_conflicting_environment_values_fail_closed(self):
        """Production wins over development when environment values conflict."""
        import SLEEP_CASH_API.youtube_transcript_api_service as service

        event = {
            "id": _unique_event_id("conflicting_environment"),
            "type": "checkout.session.completed",
            "data": {"object": {}},
        }
        with patch.dict(
            "os.environ",
            {"APP_ENV": "production", "NODE_ENV": "development"},
            clear=True,
        ), patch.object(service, "STRIPE_WEBHOOK_SECRET", ""), patch.object(
            service, "STRIPE_WEBHOOK_ALLOW_UNSIGNED", True
        ), patch.object(service.api_key_store, "add_key") as add_key:
            response = self.client.post("/webhook/stripe", json=event)

        self.assertEqual(response.status_code, 503)
        add_key.assert_not_called()
        print("  [PASS] Conflicting environment values fail closed")

    def _request_for_json(self, payload: dict):
        """Build a minimal Starlette request for direct async handler tests."""
        from starlette.requests import Request

        body = json.dumps(payload).encode("utf-8")
        messages = [{"type": "http.request", "body": body, "more_body": False}]

        async def receive():
            return messages.pop(0)

        scope = {
            "type": "http",
            "method": "POST",
            "path": "/webhook/stripe",
            "headers": [(b"stripe-signature", b"valid-test-signature")],
            "query_string": b"",
            "client": ("testclient", 123),
            "server": ("testserver", 80),
            "scheme": "http",
        }
        return Request(scope, receive)


def main():
    """Run all tests and report summary."""
    print()
    print("=" * 70)
    print("YOUTUBE TRANSCRIPT API — SMOKE TESTS")
    print("=" * 70)
    if not HAS_FASTAPI:
        print("FAIL: fastapi not installed")
        return 1
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TranscriptAPITests)
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
