#!/usr/bin/env python3
"""
dashboard_server.py — tiny local HTTP server for the SLEEP_TRIPLE dashboard.

Default: 127.0.0.1:3144 (local-only).
Serves:
  GET /              → dashboard.html
  GET /audit.jsonl   → SLEEP_TRIPLE_AUDIT.jsonl (live tail)
  GET /ledger.jsonl  → REVENUE_LEDGER.jsonl (live tail)

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
AUDIT_LOG = ROOT / "SLEEP_TRIPLE_AUDIT.jsonl"
LEDGER = Path(r"C:\Users\karma\REVENUE_LEDGER.jsonl")


class Handler(BaseHTTPRequestHandler):
    def _send_bytes(self, body: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_jsonl(self, p: Path) -> None:
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
        if path.startswith("/audit.jsonl"):
            return self._send_jsonl(AUDIT_LOG)
        if path.startswith("/ledger.jsonl"):
            return self._send_jsonl(LEDGER)
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
    print(f"SLEEP_TRIPLE dashboard → http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
