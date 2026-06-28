#!/usr/bin/env python3
"""
dashboard_server.py — tiny local HTTP server for the SLEEP_TRIPLE dashboard.

Default: 127.0.0.1:3144 (local-only).
Serves:
  GET /              -> dashboard.html
  GET /audit.jsonl   -> SLEEP_TRIPLE_AUDIT.jsonl (live tail)
  GET /ledger.jsonl  -> REVENUE_LEDGER.jsonl (live tail)

Refreshing the page picks up new rows; no manual cache busting needed.
Read-only by design — no /run endpoints exposed.
"""

from __future__ import annotations

import argparse
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX_HTML = ROOT / "dashboard.html"
TRACKER_HTML = ROOT / "WEEK_1_TRACKER.html"

# Per-request resolvers so late-created ledgers are picked up by long-running servers.
# Evaluated on every GET (not at module-import time) so starting the server before
# REVENUE_LEDGER.jsonl exists doesn't lock in a stale default.


def _resolve_audit() -> Path:
    """SLEEP_TRIPLE audit log; always project-local so the dashboard ships portable."""
    return ROOT / "SLEEP_TRIPLE_AUDIT.jsonl"


def _resolve_ledger() -> Path:
    """REVENUE ledger; prefer project-local, fall back to historical global path."""
    _local = ROOT / "REVENUE_LEDGER.jsonl"
    _global = Path(r"C:\Users\karma\REVENUE_LEDGER.jsonl")
    if _local.exists():
        return _local
    if _global.exists():
        return _global
    return _local


class Handler(BaseHTTPRequestHandler):
    def _send_bytes(self, body: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_jsonl(self, resolver) -> None:
        """Resolve the path on every request (handles late-created log files).
        `resolver` is a zero-arg callable returning the current Path.
        """
        p = resolver()
        if not p.exists():
            self._send_bytes(b"", "application/jsonl")
            return
        self._send_bytes(p.read_bytes(), "application/jsonl")

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            try:
                self._send_bytes(INDEX_HTML.read_bytes(), "text/html; charset=utf-8")
            except FileNotFoundError:
                self.send_error(404, "dashboard.html missing — re-run setup")
            return
        if path in ("/tracker", "/tracker.html", "/WEEK_1_TRACKER.html"):
            try:
                self._send_bytes(TRACKER_HTML.read_bytes(), "text/html; charset=utf-8")
            except FileNotFoundError:
                self.send_error(404, "WEEK_1_TRACKER.html missing — re-run setup")
            return
        if path.startswith("/audit.jsonl"):
            return self._send_jsonl(_resolve_audit)
        if path.startswith("/ledger.jsonl"):
            return self._send_jsonl(_resolve_ledger)
        if path == "/healthz":
            self._send_bytes(b'{"status":"ok"}', "application/json")
            return
        self.send_error(404, f"unknown path: {path}")

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("[dashboard-server] " + (fmt % args) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="SLEEP_TRIPLE dashboard server")
    ap.add_argument("--host", default="127.0.0.1", help="bind host (default 127.0.0.1)")
    ap.add_argument("--port", type=int, default=3144, help="bind port (default 3144)")
    args = ap.parse_args()
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    # SO_REUSEADDR: TIME_WAIT sockets from prior server runs don't block the
    # bind. Without this, _smoke_retry.py's Section 11 HTTP smoke flaps to
    # rc=1 when the previous dashboard server hasn't fully released the port.
    httpd.allow_reuse_address = True
    # Use ASCII arrows ('->') instead of Unicode '->' because Windows
    # Python's default console codec (cp1252) crashes on the unicode
    # arrow when --log-stdout is the only place stdout gets touched.
    print(f"SLEEP_TRIPLE dashboard -> http://{args.host}:{args.port}")
    print(f"SLEEP_TRIPLE tracker  -> http://{args.host}:{args.port}/tracker")
    _audit_path = _resolve_audit()
    _ledger_path = _resolve_ledger()
    print(f"[dashboard-server] audit path:  {_audit_path} (exists={_audit_path.exists()})")
    print(f"[dashboard-server] ledger path: {_ledger_path} (exists={_ledger_path.exists()})")
    print("[dashboard-server] Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
