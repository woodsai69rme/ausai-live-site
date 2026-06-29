"""Unit tests for lazy / thread-safe Supabase initialization.

Covers:
- src.server.middleware.auth_middleware._get_supabase()
- src.server.services.cost_optimization_service.CostOptimizationService.supabase_client
- src.server.services.cost_optimization_service.get_cost_optimization_service()
- src.server.api_routes.auth_api — 503 short-circuit when Supabase unavailable
"""

from __future__ import annotations

import os
import threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException


# ---------------------------------------------------------------------------
# auth_middleware._get_supabase()
# ---------------------------------------------------------------------------

@pytest.fixture
def reset_auth_middleware_state():
    """Reset the module-level cached client so each test starts cold.

    The conftest already seeds SUPABASE_URL / SUPABASE_SERVICE_KEY with valid
    test-mode values; we leave those alone and only reset the cached client.
    """
    from src.server.middleware import auth_middleware

    auth_middleware._supabase_client = None
    yield
    auth_middleware._supabase_client = None


def _set_supabase_env(url="https://test.supabase.co", key="test-key"):
    """Helper to set valid Supabase env vars for tests that need them."""
    os.environ["SUPABASE_URL"] = url
    os.environ["SUPABASE_SERVICE_KEY"] = key


@pytest.mark.parametrize("missing", ["SUPABASE_URL", "SUPABASE_SERVICE_KEY"])
def test_get_supabase_returns_none_when_env_missing(reset_auth_middleware_state, missing):
    """Missing SUPABASE_URL OR SUPABASE_SERVICE_KEY -> returns None without raising."""
    from src.server.middleware.auth_middleware import _get_supabase

    other = "SUPABASE_SERVICE_KEY" if missing == "SUPABASE_URL" else "SUPABASE_URL"
    if missing == "SUPABASE_URL":
        os.environ.pop("SUPABASE_URL", None)
        os.environ["SUPABASE_SERVICE_KEY"] = "test-key"
    else:
        os.environ["SUPABASE_URL"] = "https://test.supabase.co"
        os.environ.pop("SUPABASE_SERVICE_KEY", None)

    with patch("src.server.middleware.auth_middleware.create_client") as mock_create:
        assert _get_supabase() is None
        mock_create.assert_not_called()

    # Cleanup so other tests aren't polluted.
    _set_supabase_env()


def test_get_supabase_returns_none_when_create_raises(reset_auth_middleware_state):
    """If create_client raises (bad key, network, etc.), returns None."""
    from src.server.middleware.auth_middleware import _get_supabase

    _set_supabase_env(url="https://broken.supabase.co", key="invalid")

    with patch(
        "src.server.middleware.auth_middleware.create_client",
        side_effect=RuntimeError("boom"),
    ):
        assert _get_supabase() is None


def test_get_supabase_returns_cached_client(reset_auth_middleware_state):
    """Second call returns the cached client without invoking create_client again."""
    from src.server.middleware import auth_middleware
    from src.server.middleware.auth_middleware import _get_supabase

    _set_supabase_env()
    fake_client = MagicMock(name="supabase-client")
    with patch(
        "src.server.middleware.auth_middleware.create_client",
        return_value=fake_client,
    ) as mock_create:
        first = _get_supabase()
        second = _get_supabase()
        third = _get_supabase()

    assert first is fake_client
    assert second is fake_client
    assert third is fake_client
    assert mock_create.call_count == 1
    assert auth_middleware._supabase_client is fake_client


def test_get_supabase_thread_safe_single_call(reset_auth_middleware_state):
    """Concurrent first-callers only invoke create_client once (double-check lock)."""
    from src.server.middleware.auth_middleware import _get_supabase

    _set_supabase_env()
    fake_client = MagicMock(name="supabase-client")

    call_count = 0
    lock = threading.Lock()

    def fake_create(*args, **kwargs):
        nonlocal call_count
        with lock:
            call_count += 1
        import time

        time.sleep(0.02)
        return fake_client

    barrier = threading.Barrier(20)

    def worker():
        barrier.wait()
        return _get_supabase()

    with patch(
        "src.server.middleware.auth_middleware.create_client",
        side_effect=fake_create,
    ):
        with ThreadPoolExecutor(max_workers=20) as pool:
            results = list(pool.map(lambda _: worker(), range(20)))

    assert all(r is fake_client for r in results)
    assert call_count == 1, f"create_client called {call_count} times, expected 1"


# ---------------------------------------------------------------------------
# cost_optimization_service.CostOptimizationService.supabase_client
# ---------------------------------------------------------------------------


def _build_service(supabase_client=None) -> "CostOptimizationService":
    from src.server.services.cost_optimization_service import CostOptimizationService

    return CostOptimizationService(supabase_client=supabase_client)


def test_cost_service_uses_injected_client():
    """If a client was injected via __init__, the property returns it without lazy init."""
    injected = MagicMock(name="injected-supabase")
    svc = _build_service(supabase_client=injected)

    # First access must not invoke get_supabase_client.
    with patch(
        "src.server.services.cost_optimization_service.get_supabase_client"
    ) as mock_getter:
        assert svc.supabase_client is injected
        mock_getter.assert_not_called()


def test_cost_service_lazy_init_returns_client():
    """Without injection, the property fetches via get_supabase_client and caches."""
    fake = MagicMock(name="supabase-client")
    svc = _build_service()

    with patch(
        "src.server.services.cost_optimization_service.get_supabase_client",
        return_value=fake,
    ) as mock_getter:
        first = svc.supabase_client
        second = svc.supabase_client

    assert first is fake
    assert second is fake
    assert mock_getter.call_count == 1


def test_cost_service_lazy_init_returns_none_when_getter_fails():
    """If get_supabase_client raises, property returns None and does not blow up later."""
    svc = _build_service()

    with patch(
        "src.server.services.cost_optimization_service.get_supabase_client",
        side_effect=RuntimeError("no creds"),
    ):
        assert svc.supabase_client is None
        # Subsequent access keeps returning None without retrying.
        assert svc.supabase_client is None


def test_cost_service_thread_safe_single_init():
    """Concurrent first-access from many threads only calls get_supabase_client once."""
    svc = _build_service()
    fake = MagicMock(name="supabase-client")

    call_count = 0
    lock = threading.Lock()

    def fake_getter():
        nonlocal call_count
        with lock:
            call_count += 1
        import time

        time.sleep(0.02)
        return fake

    barrier = threading.Barrier(20)

    def worker():
        barrier.wait()
        return svc.supabase_client

    with patch(
        "src.server.services.cost_optimization_service.get_supabase_client",
        side_effect=fake_getter,
    ):
        with ThreadPoolExecutor(max_workers=20) as pool:
            results = list(pool.map(lambda _: worker(), range(20)))

    assert all(r is fake for r in results)
    assert call_count == 1, f"getter called {call_count} times, expected 1"


# ---------------------------------------------------------------------------
# cost_optimization_service.get_cost_optimization_service()
# ---------------------------------------------------------------------------


def test_get_cost_optimization_service_is_singleton():
    """Successive calls return the same instance."""
    from src.server.services.cost_optimization_service import (
        get_cost_optimization_service,
    )
    import src.server.services.cost_optimization_service as mod

    mod._cost_optimization_service = None
    try:
        a = get_cost_optimization_service()
        b = get_cost_optimization_service()
        assert a is b
    finally:
        mod._cost_optimization_service = None


def test_get_cost_optimization_service_thread_safe_single_construct():
    """Concurrent singleton access constructs CostOptimizationService exactly once."""
    from src.server.services import cost_optimization_service as mod
    from src.server.services.cost_optimization_service import (
        CostOptimizationService,
        get_cost_optimization_service,
    )

    mod._cost_optimization_service = None

    constructed = 0
    lock = threading.Lock()

    def counting_init(self, supabase_client=None):
        nonlocal constructed
        with lock:
            constructed += 1
        import time

        time.sleep(0.02)
        # Re-read __init__ from the class on each call so we always delegate
        # to the unpatched original even if patch ordering changes.
        cls_init = CostOptimizationService.__dict__.get("__init__")
        if cls_init is not None and cls_init is not counting_init:
            cls_init(self, supabase_client=supabase_client)

    # Barrier matched to task count so every thread releases simultaneously.
    barrier = threading.Barrier(20)

    def worker():
        barrier.wait()
        return get_cost_optimization_service()

    with patch.object(CostOptimizationService, "__init__", counting_init):
        with ThreadPoolExecutor(max_workers=20) as pool:
            results = list(pool.map(lambda _: worker(), range(20)))

    try:
        assert constructed == 1, f"constructed {constructed} times, expected 1"
        first = results[0]
        assert all(r is first for r in results)
    finally:
        mod._cost_optimization_service = None


# ---------------------------------------------------------------------------
# auth_api 503 short-circuit
# ---------------------------------------------------------------------------


@pytest.fixture
def auth_api_client():
    """TestClient bound directly to the auth_api router (no main-app prefix)."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from src.server.api_routes.auth_api import router as auth_router

    app = FastAPI()
    app.include_router(auth_router)
    return TestClient(app)


def test_auth_api_register_returns_503_when_supabase_unavailable(auth_api_client):
    """/register returns 503 when _get_supabase() returns None (no crash)."""
    with patch(
        "src.server.api_routes.auth_api._get_supabase", return_value=None
    ):
        resp = auth_api_client.post(
            "/register",
            json={"email": "u@example.com", "password": "pw"},
        )
    assert resp.status_code == 503, (
        f"expected 503, got {resp.status_code}: {resp.text}"
    )
    body = resp.json()
    assert "unavailable" in body.get("detail", "").lower()


def test_auth_api_login_returns_503_when_supabase_unavailable(auth_api_client):
    """/login returns 503 when Supabase is unavailable."""
    with patch(
        "src.server.api_routes.auth_api._get_supabase", return_value=None
    ):
        resp = auth_api_client.post(
            "/login",
            json={"email": "u@example.com", "password": "pw"},
        )
    assert resp.status_code == 503, (
        f"expected 503, got {resp.status_code}: {resp.text}"
    )


def test_auth_api_endpoints_dont_touch_supabase_when_unavailable(auth_api_client, mock_supabase_client):
    """When Supabase is None, endpoints must short-circuit BEFORE any DB call."""
    mock_supabase_client.reset_mock()
    with patch(
        "src.server.api_routes.auth_api._get_supabase", return_value=None
    ):
        with patch(
            "src.server.api_routes.auth_api.create_client",
            return_value=mock_supabase_client,
        ):
            auth_api_client.post(
                "/register",
                json={"email": "u@example.com", "password": "pw"},
            )
    # If the endpoint short-circuited, neither auth nor table methods were used.
    mock_supabase_client.auth.admin.create_user.assert_not_called()
    mock_supabase_client.table.assert_not_called()
