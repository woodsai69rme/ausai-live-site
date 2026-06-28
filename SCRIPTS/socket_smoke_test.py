"""Socket.IO smoke test for the Archon server.

Boots a Socket.IO client against an already-running Archon server (defaults
to `http://localhost:8181`), waits for the server-side `connect` event, and
exits with code 0 on success / non-zero on failure.

Intended use:
  - Local pre-merge check:    python scripts/socket_smoke_test.py
  - CI healthcheck step:      python scripts/socket_smoke_test.py --timeout 5
  - Docker healthcheck:       see docker-compose.yml notes

This script deliberately does NOT start the server -- the caller is
responsible for bringing the service up first. The script just verifies
that the Socket.IO mount added in `python/src/server/main.py` is forward-
reachable. If we ever wire a regression that wraps the FastAPI app without
the Socket.IO ASGI middleware, this test will fail with a clear timeout.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass

try:  # python-socketio client is already a project dep.
    import socketio  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - install hint
    print("error: python-socketio is not installed. Run `uv sync --extra test`.",
          file=sys.stderr)
    sys.exit(2)


@dataclass
class SmokeResult:
    """Captures the outcome of one smoke run."""

    connected: bool
    handler_seen: bool
    elapsed_ms: int
    error: str | None


def run_smoke(base_url: str, timeout: float) -> SmokeResult:
    """Open a Socket.IO connection against `base_url` and wait for the event.

    Proves the Socket.IO ASGI mount in main.py works (the `connect` event
    must fire). With `--require-handler`, also emits `subscribe_projects`
    and waits for `projects_update` -- that path is the one emitted by the
    server-side `@sio.event async def subscribe_projects(...)` handler in
    socketio_handlers.py and is a strong proof the handler is registered.
    """
    client = socketio.Client(logger=False, engineio_logger=False)
    state: dict[str, bool] = {"connected": False, "handler": False}
    error_msgs: list[str] = []

    @client.event
    def connect():  # type: ignore[no-redef]
        state["connected"] = True

    @client.event
    def projects_update(_data):  # type: ignore[no-redef]
        state["handler"] = True

    @client.event
    def connect_error(data):  # type: ignore[no-redef]
        error_msgs.append(f"connect_error: {data!r}")

    started = time.monotonic()
    try:
        client.connect(base_url, transports=["websocket"], wait_timeout=timeout)
        deadline = started + timeout
        while time.monotonic() < deadline and not state["connected"]:
            client.sleep(0.05)

        if state["connected"]:
            # Emit `subscribe_projects` -- the server-side handler
            # responds with a `projects_update` event, which we use as
            # the registration sentinel.
            client.emit("subscribe_projects", {})
            handler_deadline = started + timeout
            while time.monotonic() < handler_deadline and not state["handler"]:
                client.sleep(0.05)
    except (socketio.exceptions.ConnectionError, OSError) as exc:
        error_msgs.append(f"connect failed: {exc!r}")
    finally:
        try:
            client.disconnect()
        except Exception:  # pragma: no cover - best effort cleanup
            pass

    elapsed_ms = int((time.monotonic() - started) * 1000)
    return SmokeResult(
        connected=state["connected"],
        handler_seen=state["handler"],
        elapsed_ms=elapsed_ms,
        error="; ".join(error_msgs) if error_msgs else None,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--url",
        default=os.getenv("ARCHON_SERVER_URL", "http://localhost:8181"),
        help="Server base URL (default: $ARCHON_SERVER_URL or http://localhost:8181).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=float(os.getenv("ARCHON_SMOKE_TIMEOUT", "5")),
        help="Seconds to wait for the connect event (default: 5).",
    )
    parser.add_argument(
        "--require-handler",
        action="store_true",
        help="Also require the `joined_project` / `subscribe_projects` round-trip.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress success log line -- only print on failure / exit code.",
    )
    args = parser.parse_args()

    result = run_smoke(args.url, args.timeout)
    ok = result.connected and (not args.require_handler or result.handler_seen)

    if ok:
        if not args.quiet:
            print(
                f"[smoke] ok: Socket.IO connected in {result.elapsed_ms}ms "
                f"(handler_seen={result.handler_seen})"
            )
        return 0

    print(
        f"[smoke] fail: connected={result.connected} "
        f"handler_seen={result.handler_seen} elapsed_ms={result.elapsed_ms} "
        f"error={result.error or 'n/a'}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
