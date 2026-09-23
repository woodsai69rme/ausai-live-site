#!/usr/bin/env python3
"""
test_kv_store.py — Unit tests for the Lane-4 key-value storage layer.

Covers both in-memory and (mocked) Redis code paths for:
  - Cache
  - RateLimiter
  - ApiKeyStore
"""

import time
import unittest
from unittest.mock import patch

from SLEEP_CASH_API.kv_store import (
    ApiKeyStore,
    Cache,
    RateLimiter,
)


class CacheTests(unittest.TestCase):
    """Tests for the generic TTL Cache."""

    def setUp(self):
        self.cache = Cache()
        self.cache._in_memory.clear()

    def test_cache_set_and_get(self):
        self.cache.set("key:1", ["segment"], ttl_seconds=60)
        self.assertEqual(self.cache.get("key:1"), ["segment"])

    def test_cache_returns_none_after_ttl(self):
        self.cache.set("key:1", ["segment"], ttl_seconds=0)
        time.sleep(0.01)
        self.assertIsNone(self.cache.get("key:1"))

    def test_cache_missing_key_returns_none(self):
        self.assertIsNone(self.cache.get("missing"))

    def test_cache_set_if_absent_claims_once(self):
        self.assertTrue(self.cache.set_if_absent("event:1", True, ttl_seconds=60))
        self.assertFalse(self.cache.set_if_absent("event:1", True, ttl_seconds=60))

    def test_cache_delete_releases_claim(self):
        self.assertTrue(self.cache.set_if_absent("event:1", True, ttl_seconds=60))
        self.cache.delete("event:1")
        self.assertTrue(self.cache.set_if_absent("event:1", True, ttl_seconds=60))

    def test_cache_prunes_expired_entries(self):
        self.cache.set("a", 1, ttl_seconds=0)
        self.cache.set("b", 2, ttl_seconds=3600)
        self.cache._prune_expired()
        self.assertIsNone(self.cache.get("a"))
        self.assertEqual(self.cache.get("b"), 2)


class RateLimiterTests(unittest.TestCase):
    """Tests for the IP-based RateLimiter."""

    def setUp(self):
        self.limiter = RateLimiter()
        self.limiter._in_memory.clear()

    def test_under_limit_allowed(self):
        for i in range(5):
            allowed, remaining = self.limiter.check("1.2.3.4", limit=5, window_hours=24)
            self.assertTrue(allowed)
            self.assertEqual(remaining, 4 - i)

    def test_over_limit_blocked(self):
        for _ in range(5):
            self.limiter.check("1.2.3.4", limit=5, window_hours=24)
        allowed, remaining = self.limiter.check("1.2.3.4", limit=5, window_hours=24)
        self.assertFalse(allowed)
        self.assertEqual(remaining, 0)

    def test_different_ips_independent(self):
        self.limiter.check("1.2.3.4", limit=1, window_hours=24)
        allowed, _ = self.limiter.check("5.6.7.8", limit=1, window_hours=24)
        self.assertTrue(allowed)

    def test_window_expires(self):
        self.limiter.check("1.2.3.4", limit=1, window_hours=24)
        # Simulate old timestamp to force expiry
        self.limiter._in_memory["1.2.3.4"] = [time.time() - 25 * 3600]
        allowed, _ = self.limiter.check("1.2.3.4", limit=1, window_hours=24)
        self.assertTrue(allowed)


class ApiKeyStoreTests(unittest.TestCase):
    """Tests for the API key store."""

    def setUp(self):
        self.store = ApiKeyStore()
        self.store._in_memory.clear()

    def test_is_valid_missing(self):
        self.assertFalse(self.store.is_valid("missing-key"))

    def test_add_and_check_key(self):
        self.store.add_key("ytx_test_123", "test@example.com", "cus_123")
        self.assertTrue(self.store.is_valid("ytx_test_123"))

    def test_get_key_by_event_id(self):
        self.store.add_key("ytx_event_key", "a@example.com", "cus_1", stripe_event_id="evt_1")
        self.assertEqual(self.store.get_key_by_event_id("evt_1"), "ytx_event_key")
        self.assertTrue(self.store.has_event_id("evt_1"))
        self.assertIsNone(self.store.get_key_by_event_id("evt_missing"))
        self.assertFalse(self.store.has_event_id("evt_missing"))

    def test_deactivate_by_customer(self):
        self.store.add_key("ytx_test_1", "a@example.com", "cus_1")
        self.store.add_key("ytx_test_2", "b@example.com", "cus_2")
        self.store.deactivate_by_customer("cus_1")
        self.assertFalse(self.store.is_valid("ytx_test_1"))
        self.assertTrue(self.store.is_valid("ytx_test_2"))

    def test_empty_key_is_invalid(self):
        self.assertFalse(self.store.is_valid(""))


class RedisBackendTests(unittest.TestCase):
    """Smoke tests that exercise Redis code paths with a mocked client."""

    def _make_fake_redis(self):
        class FakeRedis:
            def __init__(self):
                self.data = {}
                self._exp = {}

            def get(self, key):
                return self.data.get(key)

            def setex(self, key, ttl, value):
                self.data[key] = value
                self._exp[key] = time.time() + ttl

            def set(self, key, value, ex=None, nx=False):
                if nx and key in self.data:
                    return False
                self.data[key] = value
                if ex is not None:
                    self._exp[key] = time.time() + ex
                return True

            def delete(self, key):
                self.data.pop(key, None)
                self._exp.pop(key, None)

            def eval(self, script, numkeys, key, expected, *args):
                current = self.data.get(key)
                if current != expected:
                    return 0
                if "DEL" in script:
                    self.delete(key)
                else:
                    ttl, value = args
                    self.setex(key, int(ttl), value)
                return 1

            def zremrangebyscore(self, key, min_score, max_score):
                pass

            def zcard(self, key):
                return 0

            def zadd(self, key, mapping):
                pass

            def expire(self, key, ttl):
                pass

            def hset(self, hash_name, key, value):
                if hash_name not in self.data:
                    self.data[hash_name] = {}
                self.data[hash_name][key] = value

            def hget(self, hash_name, key):
                return self.data.get(hash_name, {}).get(key)

            def hgetall(self, hash_name):
                return self.data.get(hash_name, {})

        return FakeRedis()

    def test_cache_uses_redis_when_available(self):
        fake = self._make_fake_redis()
        with patch("SLEEP_CASH_API.kv_store._redis", fake), patch(
            "SLEEP_CASH_API.kv_store._redis_init_attempted", True
        ):
            cache = Cache()
            cache.set("k", [1, 2, 3], ttl_seconds=10)
            self.assertEqual(cache.get("k"), [1, 2, 3])
            self.assertFalse(cache.set_if_absent("k", [4], ttl_seconds=10))
            cache.delete("k")
            self.assertTrue(cache.set_if_absent("k", [4], ttl_seconds=10))

    def test_redis_conditional_claim_operations(self):
        fake = self._make_fake_redis()
        with patch("SLEEP_CASH_API.kv_store._redis", fake), patch(
            "SLEEP_CASH_API.kv_store._redis_init_attempted", True
        ):
            cache = Cache()
            owner = {"status": "processing", "owner": "one"}
            other = {"status": "processing", "owner": "two"}
            self.assertTrue(cache.set_if_absent("claim", owner, ttl_seconds=10))
            self.assertFalse(cache.set_if_value("claim", other, {"status": "completed"}, 10))
            self.assertTrue(cache.set_if_value("claim", owner, {"status": "completed"}, 10))
            self.assertFalse(cache.delete_if_value("claim", owner))
            self.assertTrue(cache.delete_if_value("claim", {"status": "completed"}))

    def test_api_key_store_redis(self):
        fake = self._make_fake_redis()
        with patch("SLEEP_CASH_API.kv_store._redis", fake), patch(
            "SLEEP_CASH_API.kv_store._redis_init_attempted", True
        ):
            store = ApiKeyStore()
            store.add_key("ytx_redis", "user@example.com", "cus_r1", stripe_event_id="evt_redis")
            self.assertTrue(store.is_valid("ytx_redis"))
            self.assertEqual(store.get_key_by_event_id("evt_redis"), "ytx_redis")
            store.deactivate_by_customer("cus_r1")
            self.assertFalse(store.is_valid("ytx_redis"))


if __name__ == "__main__":
    unittest.main()
