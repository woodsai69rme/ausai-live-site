"""
kv_store.py — Abstracted key-value storage for the YouTube Transcript API (Lane-4).

Supports two backends, auto-selected at runtime:
  1. Redis    — when KV_URL or REDIS_URL env var is set (Vercel KV / Upstash)
  2. InMemory — fallback when no Redis URL is configured

Usage:
  from kv_store import rate_limiter, api_key_store

  allowed, remaining = rate_limiter.check("192.168.1.1", limit=5, window_hours=24)
  valid = api_key_store.is_valid("ytx_abc123")
"""

from __future__ import annotations

import os
import json
import time
import threading
from collections import defaultdict
from typing import Optional

# ---------------------------------------------------------------------------
# Redis connection (lazy, thread-safe, one-time init)
# ---------------------------------------------------------------------------
_redis = None
_redis_init_attempted = False
_redis_init_lock = threading.Lock()


def _get_redis_url() -> Optional[str]:
    """Read the Redis connection URL from environment."""
    return os.environ.get("KV_URL") or os.environ.get("REDIS_URL")


def _ensure_redis():
    """Lazy-init the Redis client. Returns the client or None."""
    global _redis, _redis_init_attempted

    if _redis_init_attempted:
        return _redis

    with _redis_init_lock:
        # Double-check after acquiring the lock
        if _redis_init_attempted:
            return _redis
        _redis_init_attempted = True

        url = _get_redis_url()
        if not url:
            return None

        try:
            import redis  # type: ignore[import-untyped]
        except ImportError:
            return None

        try:
            # Vercel KV / Upstash Redis support with connection pooling for serverless
            # Both use standard Redis protocol with TLS
            _redis = redis.Redis.from_url(
                url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                # Connection pool settings for serverless (Vercel, Cloudflare Workers)
                max_connections=10,
                retry_on_timeout=True,
                health_check_interval=30,
            )
            # Quick ping to verify connectivity
            _redis.ping()
            return _redis
        except Exception:
            _redis = None
            return None


# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------
class RateLimiter:
    """IP-based rate limiter with Redis and in-memory backends."""

    def __init__(self) -> None:
        self._in_memory: dict[str, list[float]] = defaultdict(list)
        self._locks: dict[str, threading.Lock] = defaultdict(threading.Lock)

    def check(self, ip: str, limit: int, window_hours: int) -> tuple[bool, int]:
        """Check if an IP is allowed. Returns (allowed, remaining_requests)."""
        r = _ensure_redis()
        if r is not None:
            return self._check_redis(r, ip, limit, window_hours)
        return self._check_memory(ip, limit, window_hours)

    # ---- Redis backend ----
    @staticmethod
    def _check_redis(r, ip: str, limit: int, window_hours: int) -> tuple[bool, int]:
        key = f"rate_limit:{ip}"
        now = time.time()
        cutoff = now - (window_hours * 3600)

        # Remove expired entries
        r.zremrangebyscore(key, 0, cutoff)
        # Count remaining
        count = r.zcard(key)

        if count >= limit:
            return (False, 0)

        # Add current request timestamp (unique suffix prevents collision at same microsecond)
        member = f"{now}:{os.urandom(4).hex()}"
        r.zadd(key, {member: now})
        # Auto-expire the key after the window (plus a small buffer)
        r.expire(key, int(window_hours * 3600) + 60)
        return (True, limit - count - 1)

    # ---- In-memory backend ----
    def _check_memory(self, ip: str, limit: int, window_hours: int) -> tuple[bool, int]:
        now = time.time()
        cutoff = now - (window_hours * 3600)

        # Per-IP lock to prevent thundering herd on single process
        with self._locks[ip]:
            # Purge expired timestamps
            self._in_memory[ip] = [ts for ts in self._in_memory[ip] if ts > cutoff]
            count = len(self._in_memory[ip])

            if count >= limit:
                return (False, 0)

            self._in_memory[ip].append(now)
            return (True, limit - count - 1)


# ---------------------------------------------------------------------------
# Generic cache (transcript results, etc.)
# ---------------------------------------------------------------------------
class Cache:
    """Generic TTL cache with Redis and in-memory backends."""

    MAX_IN_MEMORY_ENTRIES = 1000

    def __init__(self) -> None:
        self._in_memory: dict[str, tuple[float, str]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[object]:
        """Return cached value or None if missing/expired."""
        r = _ensure_redis()
        if r is not None:
            data = r.get(key)
            if not data:
                return None
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return None

        with self._lock:
            self._prune_expired()
            entry = self._in_memory.get(key)
            if entry is None:
                return None
            expiry, value = entry
            if time.time() >= expiry:
                self._in_memory.pop(key, None)
                return None
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None

    def set(self, key: str, value: object, ttl_seconds: int) -> None:
        """Store a JSON-serializable value with TTL."""
        r = _ensure_redis()
        try:
            payload = json.dumps(value)
        except TypeError:
            return

        if r is not None:
            r.setex(key, ttl_seconds, payload)
            return

        with self._lock:
            self._prune_expired()
            self._enforce_capacity()
            self._in_memory[key] = (time.time() + ttl_seconds, payload)

    def set_if_absent(self, key: str, value: object, ttl_seconds: int) -> bool:
        """Atomically store a value only when ``key`` does not already exist."""
        r = _ensure_redis()
        try:
            payload = json.dumps(value)
        except TypeError:
            return False

        if r is not None:
            # Redis SET NX EX provides an atomic claim across workers/processes.
            return bool(r.set(key, payload, ex=ttl_seconds, nx=True))

        with self._lock:
            self._prune_expired()
            if key in self._in_memory:
                return False
            self._enforce_capacity()
            self._in_memory[key] = (time.time() + ttl_seconds, payload)
            return True

    def delete(self, key: str) -> None:
        """Delete a cache entry when processing cannot complete."""
        r = _ensure_redis()
        if r is not None:
            r.delete(key)
            return

        with self._lock:
            self._in_memory.pop(key, None)

    def delete_if_value(self, key: str, expected: object) -> bool:
        """Delete ``key`` only when it still contains ``expected``.

        Webhook processing claims carry an owner token. Conditional deletion
        prevents a slow/stale handler from deleting a newer retry's claim.
        """
        try:
            expected_payload = json.dumps(expected)
        except TypeError:
            return False

        r = _ensure_redis()
        if r is not None:
            script = (
                "local current = redis.call('GET', KEYS[1]); "
                "if current ~= ARGV[1] then return 0 end; "
                "redis.call('DEL', KEYS[1]); return 1"
            )
            return bool(r.eval(script, 1, key, expected_payload))

        with self._lock:
            self._prune_expired()
            entry = self._in_memory.get(key)
            if entry is None:
                return False
            try:
                matches = json.loads(entry[1]) == expected
            except json.JSONDecodeError:
                matches = False
            if not matches:
                return False
            self._in_memory.pop(key, None)
            return True

    def set_if_value(
        self,
        key: str,
        expected: object,
        value: object,
        ttl_seconds: int,
    ) -> bool:
        """Replace ``key`` only when it still contains ``expected``."""
        try:
            expected_payload = json.dumps(expected)
            payload = json.dumps(value)
        except TypeError:
            return False

        r = _ensure_redis()
        if r is not None:
            script = (
                "local current = redis.call('GET', KEYS[1]); "
                "if current ~= ARGV[1] then return 0 end; "
                "redis.call('SETEX', KEYS[1], ARGV[2], ARGV[3]); return 1"
            )
            return bool(r.eval(script, 1, key, expected_payload, ttl_seconds, payload))

        with self._lock:
            self._prune_expired()
            entry = self._in_memory.get(key)
            if entry is None:
                return False
            try:
                matches = json.loads(entry[1]) == expected
            except json.JSONDecodeError:
                matches = False
            if not matches:
                return False
            self._in_memory[key] = (time.time() + ttl_seconds, payload)
            return True

    def is_durable(self) -> bool:
        """Return whether this cache is backed by a shared Redis store."""
        return _ensure_redis() is not None

    def _prune_expired(self) -> None:
        now = time.time()
        expired = [k for k, (exp, _) in self._in_memory.items() if now >= exp]
        for k in expired:
            self._in_memory.pop(k, None)

    def _enforce_capacity(self) -> None:
        """Evict oldest entries when the in-memory cache exceeds its cap."""
        while len(self._in_memory) >= self.MAX_IN_MEMORY_ENTRIES:
            oldest = min(self._in_memory, key=lambda k: self._in_memory[k][0])
            self._in_memory.pop(oldest, None)


# ---------------------------------------------------------------------------
# API key store
# ---------------------------------------------------------------------------
class ApiKeyStore:
    """API key storage with Redis and in-memory backends."""

    REDIS_HASH = "api_keys"

    def __init__(self) -> None:
        self._in_memory: dict[str, dict] = {}
        self._lock = threading.Lock()

    def is_valid(self, key: str) -> bool:
        """Check if an API key is valid and active."""
        if not key:
            return False
        r = _ensure_redis()
        if r is not None:
            return self._is_valid_redis(r, key)
        return self._is_valid_memory(key)

    def add_key(
        self,
        key: str,
        email: str,
        stripe_customer_id: str,
        stripe_event_id: str | None = None,
    ) -> None:
        """Register a new API key, optionally linked to a Stripe event."""
        entry = {
            "email": email,
            "stripe_customer_id": stripe_customer_id,
            "active": True,
            "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        if stripe_event_id:
            entry["stripe_event_id"] = stripe_event_id
        r = _ensure_redis()
        if r is not None:
            r.hset(self.REDIS_HASH, key, json.dumps(entry))
            return
        with self._lock:
            self._in_memory[key] = entry

    def get_key_by_event_id(self, stripe_event_id: str) -> str | None:
        """Find an active key previously issued for a Stripe event."""
        if not stripe_event_id:
            return None
        r = _ensure_redis()
        if r is not None:
            entries = r.hgetall(self.REDIS_HASH)
            for api_key, data_str in entries.items():
                try:
                    entry = json.loads(data_str)
                except json.JSONDecodeError:
                    continue
                if entry.get("stripe_event_id") == stripe_event_id and entry.get("active", False):
                    return api_key
            return None

        with self._lock:
            for api_key, entry in self._in_memory.items():
                if entry.get("stripe_event_id") == stripe_event_id and entry.get("active", False):
                    return api_key
        return None

    def has_event_id(self, stripe_event_id: str) -> bool:
        """Return whether any key record already belongs to a Stripe event."""
        if not stripe_event_id:
            return False
        r = _ensure_redis()
        entries = r.hgetall(self.REDIS_HASH) if r is not None else None
        if entries is not None:
            records = entries.items()
        else:
            with self._lock:
                records = list(self._in_memory.items())
        for _api_key, data in records:
            try:
                entry = json.loads(data) if isinstance(data, str) else data
            except json.JSONDecodeError:
                continue
            if entry.get("stripe_event_id") == stripe_event_id:
                return True
        return False

    def deactivate_by_customer(self, stripe_customer_id: str) -> None:
        """Deactivate all API keys for a Stripe customer."""
        r = _ensure_redis()
        if r is not None:
            self._deactivate_redis(r, stripe_customer_id)
            return
        with self._lock:
            for entry in self._in_memory.values():
                if entry.get("stripe_customer_id") == stripe_customer_id:
                    entry["active"] = False

    # ---- Redis helpers ----
    @staticmethod
    def _is_valid_redis(r, key: str) -> bool:
        data = r.hget(ApiKeyStore.REDIS_HASH, key)
        if not data:
            return False
        try:
            return json.loads(data).get("active", False)
        except json.JSONDecodeError:
            return False

    @staticmethod
    def _deactivate_redis(r, stripe_customer_id: str) -> None:
        all_entries = r.hgetall(ApiKeyStore.REDIS_HASH)
        for api_key, data_str in all_entries.items():
            try:
                entry = json.loads(data_str)
            except json.JSONDecodeError:
                continue
            if entry.get("stripe_customer_id") == stripe_customer_id:
                entry["active"] = False
                r.hset(ApiKeyStore.REDIS_HASH, api_key, json.dumps(entry))

    # ---- In-memory helpers ----
    def _is_valid_memory(self, key: str) -> bool:
        with self._lock:
            entry = self._in_memory.get(key)
            return entry is not None and entry.get("active", False)

    def load_from_file(self, path: str) -> None:
        """Migrate existing API keys from a JSON file into the store."""
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return
        with self._lock:
            self._in_memory.update(data)


# ---------------------------------------------------------------------------
# Singleton instances (imported by the service)
# ---------------------------------------------------------------------------
rate_limiter = RateLimiter()
api_key_store = ApiKeyStore()
cache = Cache()
