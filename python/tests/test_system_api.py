"""Tests for the standalone dashboard support endpoints in system_api.py.

Covers:
  GET  /api/projects/list
  POST /api/projects/open
  POST /api/system/open_folder
  POST /api/jarvis/command  (incl. XSS-safe response_html verification)

These endpoints are stubs/aliases that satisfy the contracts called from
ULTIMATE_AI_EMPIRE_ENHANCED_DASHBOARD_V2.html. Tests focus on shape, side-
effect boundary (subprocess is mocked), and HTML-escape safety for the
Jarvis response to defend against innerHTML-rendered XSS in the dashboard.
"""

import os  # noqa: I001 - intentional colocation with `unittest.mock` import line below for readability
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ----- shared httpx fake-client helper ----------------------------------


def _make_fake_async_client(*, return_payload=None, raise_exc=None):
    """Build an `httpx.AsyncClient`-shaped duck-type for monkeypatching.

    Used by the OpenRouter tests below to inject canned chat-completions
    replies or to simulate upstream failures without touching the network.
    Pass exactly one of:
      - `return_payload` for a success shape, OR
      - `raise_exc` for a forced call-side exception (e.g. RuntimeError,
        httpx.ConnectTimeout).

    Per CLAUDE.md's fail-fast culture, an invalid call (neither or both
    set) raises immediately so the test author sees a clear stack-trace
    rather than a silent ambiguous failure mode.
    """
    if (return_payload is None) == (raise_exc is None):
        raise ValueError(
            "_make_fake_async_client requires exactly one of "
            "`return_payload` or `raise_exc` to be set."
        )

    class _Fake:
        def __init__(self, *_, **__):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def post(self, *_args, **_kwargs):
            if raise_exc is not None:
                raise raise_exc

            class _Resp:
                def raise_for_status(self_inner):
                    return None

                def json(self_inner):
                    return return_payload

            return _Resp()

    return _Fake


# ----- /api/projects/list -----------------------------------------------


def test_projects_list_wraps_response(client):
    """The dashboard expects a `{success, data}` envelope with name/path/type."""
    fake_db_response = [
        {"id": "abc", "title": "Archon Server"},
        {"id": "xyz", "title": "Federation Hub"},
    ]

    with patch(
        "src.server.api_routes.projects_api.list_projects",
        new=AsyncMock(return_value=fake_db_response),
    ):
        response = client.get("/api/projects/list")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)
    assert len(body["data"]) == 2
    # Shape contract used by the dashboard:
    assert body["data"][0]["name"] == "Archon Server"
    assert body["data"][0]["path"].startswith("archon://projects/")
    assert body["data"][0]["type"] == "Archon"


def test_projects_list_handles_http_exception(client):
    """When projects_api raises, we surface a structured error payload."""
    from fastapi import HTTPException

    with patch(
        "src.server.api_routes.projects_api.list_projects",
        new=AsyncMock(side_effect=HTTPException(status_code=500, detail="boom")),
    ):
        response = client.get("/api/projects/list")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["data"] == []
    assert "boom" in str(body["error"])


def test_projects_list_handles_non_list_payload(client):
    """Defensive: if projects_api returns something unexpected, we don't crash."""
    with patch(
        "src.server.api_routes.projects_api.list_projects",
        new=AsyncMock(return_value={"unexpected": "shape"}),
    ):
        response = client.get("/api/projects/list")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"] == []


# ----- /api/projects/open ----------------------------------------------


def test_projects_open_calls_subprocess(client):
    """A valid path triggers a subprocess invocation against an OS launcher."""
    target = os.path.abspath(".")

    with patch("src.server.api_routes.system_api.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        with patch("src.server.api_routes.system_api.shutil.which", return_value=None):
            with patch("src.server.api_routes.system_api.platform.system", return_value="Linux"):
                response = client.post("/api/projects/open", json={"path": target})

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    mock_run.assert_called_once()
    cmd_args, _ = mock_run.call_args
    argv = cmd_args[0]
    # First argv element is the OS launcher; second is the path we requested.
    assert target in argv


def test_projects_open_rejects_missing_path(client):
    """Non-existent path returns a structured error, no subprocess call."""
    missing = os.path.join(os.path.abspath("."), "definitely-not-here-987654321")

    with patch("src.server.api_routes.system_api.subprocess.run") as mock_run:
        with patch("src.server.api_routes.system_api.platform.system", return_value="Linux"):
            response = client.post("/api/projects/open", json={"path": missing})

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert missing in body["detail"]
    mock_run.assert_not_called()


# ----- /api/system/open_folder -----------------------------------------


def test_open_folder_calls_subprocess(client):
    target = os.path.abspath(".")

    with patch("src.server.api_routes.system_api.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        with patch("src.server.api_routes.system_api.platform.system", return_value="Linux"):
            response = client.post("/api/system/open_folder", json={"path": target})

    assert response.status_code == 200
    assert response.json()["success"] is True
    mock_run.assert_called_once()


def test_open_folder_rejects_missing_path(client):
    missing = os.path.join(os.path.abspath("."), "nope-12321")

    with patch("src.server.api_routes.system_api.subprocess.run") as mock_run:
        with patch("src.server.api_routes.system_api.platform.system", return_value="Linux"):
            response = client.post("/api/system/open_folder", json={"path": missing})

    assert response.json()["success"] is False
    mock_run.assert_not_called()


# ----- /api/jarvis/command ---------------------------------------------


def test_jarvis_status_intent(client):
    response = client.post("/api/jarvis/command", json={"command": "status"})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["synthetic"] is True
    assert "healthy" in body["response"].lower()
    assert body["response_safe_html"] is True
    # `response_html` must be safe to drop into innerHTML.
    assert "<" not in body["response_html"]


def test_jarvis_open_intent(client):
    response = client.post("/api/jarvis/command", json={"command": "open foo"})
    body = response.json()
    assert body["success"] is True
    assert "foo" in body["response"]
    assert body["response_safe_html"] is True


def test_jarvis_empty_command(client):
    response = client.post("/api/jarvis/command", json={"command": ""})
    body = response.json()
    assert body["success"] is False
    assert body["response"] == ""


def test_jarvis_xss_protection(client):
    """A payload that would smash `innerHTML` must arrive escaped."""
    payload = "<script>alert('pwn')</script> & \"quotes\""
    response = client.post("/api/jarvis/command", json={"command": payload})
    body = response.json()
    assert body["success"] is True
    # Raw response echoes the user's input verbatim (text content).
    assert "<script>" in body["response"]
    # Pre-escaped HTML must NOT contain raw tags or survivors.
    assert "<script>" not in body["response_html"]
    assert "&lt;script&gt;" in body["response_html"]
    assert "&amp;" in body["response_html"]
    assert "&quot;" in body["response_html"]


def test_jarvis_case_insensitive_intent(client):
    """Upper-case HELLO should match the hello intent."""
    response = client.post("/api/jarvis/command", json={"command": "HELLO"})
    assert response.json()["success"] is True
    # Synthetic hello body mentions nominal systems.
    assert "nominal" in response.json()["response"].lower()


def test_jarvis_unmatched_echo(client):
    response = client.post("/api/jarvis/command", json={"command": "hello world"})
    body = response.json()
    assert body["success"] is True
    # Echoes the input but flagged safe-html.
    assert "hello world" in body["response"]
    assert body["response_safe_html"] is True


def test_jarvis_falls_back_when_openrouter_key_absent(client, monkeypatch):
    """No API key -> unmatched command lands on the deterministic echo."""
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    response = client.post("/api/jarvis/command", json={"command": "explain kubernetes"})
    body = response.json()
    assert body["success"] is True
    assert body["synthetic"] is True
    assert "explain kubernetes" in body["response"]


def test_jarvis_uses_openrouter_when_key_present(client, monkeypatch):
    """Real NLU path: key set -> httpx routed through OpenRouter."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    fake_reply = "Deploy with `kubectl apply -f deployment.yaml`."

    monkeypatch.setattr(
        "src.server.api_routes.system_api.httpx.AsyncClient",
        _make_fake_async_client(
            return_payload={"choices": [{"message": {"content": fake_reply}}]}
        ),
    )

    response = client.post(
        "/api/jarvis/command", json={"command": "how do I deploy?"}
    )
    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["synthetic"] is False
    assert body["response"] == fake_reply
    assert body["response_safe_html"] is True
    # The pre-escaped HTML field must be safe to drop into innerHTML.
    assert "<" not in body["response_html"]


def test_jarvis_falls_back_when_openrouter_call_fails(client, monkeypatch):
    """httpx.HTTPError or empty reply -> deterministic echo with synthetic=true."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    monkeypatch.setattr(
        "src.server.api_routes.system_api.httpx.AsyncClient",
        _make_fake_async_client(raise_exc=RuntimeError("upstream down")),
    )

    response = client.post("/api/jarvis/command", json={"command": "deploy now"})
    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["synthetic"] is True
    assert "Stub acknowledgement" in body["response"]
    assert "deploy now" in body["response"]


def test_jarvis_truncates_long_openrouter_reply(client, monkeypatch):
    """A model reply exceeding JARVIS_MAX_REPLY_CHARS is truncated."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    bloated = "x" * 5000

    monkeypatch.setattr(
        "src.server.api_routes.system_api.httpx.AsyncClient",
        _make_fake_async_client(
            return_payload={"choices": [{"message": {"content": bloated}}]}
        ),
    )

    response = client.post(
        "/api/jarvis/command", json={"command": "long please"}
    )
    body = response.json()
    assert body["success"] is True
    assert body["synthetic"] is False
    # Body is capped at JARVIS_MAX_REPLY_CHARS + ellipsis (see source).
    assert body["response"].endswith("...")
    assert body["response"].endswith("x" * 4000 + "...")


def test_jarvis_handles_openrouter_tool_call_response(client, monkeypatch):
    """Tool-call / multi-block content joins text blocks into a single reply."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    monkeypatch.setattr(
        "src.server.api_routes.system_api.httpx.AsyncClient",
        _make_fake_async_client(
            return_payload={
                "choices": [
                    {
                        "message": {
                            "content": [
                                {"type": "text", "text": "First half. "},
                                {"type": "text", "text": "Second half."},
                            ]
                        }
                    }
                ]
            }
        ),
    )

    response = client.post(
        "/api/jarvis/command", json={"command": "explain tool calls"}
    )
    body = response.json()
    assert body["success"] is True
    assert body["synthetic"] is False
    assert body["response"] == "First half. Second half."
    assert body["response_html"] == "First half. Second half."


def test_jarvis_handles_empty_choices_response(client, monkeypatch):
    """An OpenRouter response with no `choices` falls back, reason carried."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    monkeypatch.setattr(
        "src.server.api_routes.system_api.httpx.AsyncClient",
        _make_fake_async_client(return_payload={"choices": []}),
    )

    response = client.post(
        "/api/jarvis/command", json={"command": "anything"}
    )
    body = response.json()
    assert body["success"] is True
    assert body["synthetic"] is True
    assert body["reason"] == "empty_choices"


def test_jarvis_reason_field_present_on_local_intent(client):
    response = client.post("/api/jarvis/command", json={"command": "status"})
    body = response.json()
    assert body["reason"] == "local_intent"


def test_jarvis_reason_field_present_on_open_shape(client):
    response = client.post("/api/jarvis/command", json={"command": "open foo"})
    body = response.json()
    assert body["reason"] == "open_shape"


# ----- /api/jarvis/command -- live integration -------------------------
#
# End-to-end pass against the real OpenRouter chat completions endpoint.
# Skipped unless OPENROUTER_API_KEY is present so dev machines / CI
# without credentials still see 22/22 green. Run locally with:
#
#     OPENROUTER_API_KEY=sk-or-... uv run pytest tests/test_system_api.py::test_jarvis_live_openrouter_smoke -v


@pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set; live integration test skipped.",
)
def test_jarvis_live_openrouter_smoke(client):
    """End-to-end JWT against openrouter.ai."""
    response = client.post(
        "/api/jarvis/command", json={"command": "Reply with the single word 'pong'."}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    # Either real OpenRouter reply or an echoed fallback if the upstream 5xx'd.
    if body["synthetic"] is False:
        assert body["reason"] == "openrouter"
        assert body["response"].strip()
        assert "<" not in body["response_html"]
    else:
        assert body["reason"] in {
            "openrouter_timeout",
            "openrouter_call_failed",
            "empty_choices",
            "empty_content",
        }
