#!/usr/bin/env python3
"""
monitor.py — Lightweight health monitor for the YouTube Transcript API.

Polls the live /healthz endpoint on a configurable interval and reports
status. If DISCORD_WEBHOOK_URL env var is set, posts a Discord message
to that webhook after `--discord-threshold` consecutive failures (default 3).
Otherwise the monitor is fully offline (dry-run) — it only prints to stdout.

Usage:
  python SLEEP_CASH_API/monitor.py                  # poll every 60s, no Discord webhook
  python SLEEP_CASH_API/monitor.py --interval 30    # poll every 30s
  python SLEEP_CASH_API/monitor.py --once           # single probe, exit
  python SLEEP_CASH_API/monitor.py --probe-all     # multi-service single-shot probe (live API + ComfyUI + Ollama)
  set DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
  python SLEEP_CASH_API/monitor.py --discord-threshold 3

Exit codes:
  0  graceful (Ctrl+C handled, or --once healthy)
  1  --once saw an unhealthy probe

Stdlib-only (json, urllib, time, argparse, signal, os, datetime).
"""

import argparse
import json
import os
import signal
import socket
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

try:
    from zoneinfo import ZoneInfo
    _TZ = ZoneInfo("Australia/Sydney")
except ImportError:
    _TZ = timezone.utc

DEFAULT_URL = "https://yt-transcript-api-ebon.vercel.app/healthz"
DEFAULT_INTERVAL = 60
DEFAULT_THRESHOLD = 3

# Local services to probe for --probe-all mode. Mirrors the local_services
# rows in SLEEP_TRIPLE/preflight.py LANE_PLAN so the monitor surfaces the
# same shape as preflight.
PROBE_ALL_LOCAL_SERVICES = [
    ("ComfyUI", "127.0.0.1", 8188),
    ("Ollama", "127.0.0.1", 11434),
]
PROBE_ALL_TIMEOUT = 3.0
HTTP_PROBE_TIMEOUT = 8.0  # for `_probe(url)` against the live API


def _now_local() -> str:
    return datetime.now(_TZ).strftime("%Y-%m-%d %H:%M:%S %Z")


def _probe_port(host: str, port: int, timeout: float = PROBE_ALL_TIMEOUT) -> tuple[bool, str]:
    """TCP probe a host:port; return (reachable, detail). Stdlib-only."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return (True, f"{host}:{port} reachable")
    except (socket.error, OSError) as e:
        return (False, f"{host}:{port} unreachable: {type(e).__name__}")


def _probe_all(api_url: str, services, timeout: float = PROBE_ALL_TIMEOUT) -> list[tuple[str, bool, str]]:
    """Probe the live API + every local service; return [(label, ok, detail), ...]."""
    results: list[tuple[str, bool, str]] = []
    ok, detail = _probe(api_url, timeout=timeout)
    results.append((f"live_api {api_url}", ok, detail))
    for (label, host, port) in services:
        ok, detail = _probe_port(host, port, timeout=timeout)
        results.append((f"{label} {host}:{port}", ok, detail))
    return results


def _probe(url: str, timeout: float = HTTP_PROBE_TIMEOUT) -> tuple[bool, str]:
    """Hit /healthz; return (ok, detail)."""
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(300).decode("utf-8", errors="replace").strip()
            try:
                parsed = json.loads(body)
                status = parsed.get("status", "?")
            except json.JSONDecodeError:
                status = body[:40]
            return (resp.status == 200 and status == "ok",
                    f"HTTP {resp.status} status={status}")
    except urllib.error.HTTPError as e:
        return (False, f"HTTP {e.code}")
    except Exception as e:
        return (False, f"{type(e).__name__}: {e}")


def _discord_post(webhook_url: str, content: str, timeout: float = 8.0) -> bool:
    """Post a Discord webhook message; return True on HTTP 204/200."""
    data = json.dumps({"content": content}).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status in (200, 204)
    except Exception:
        return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Poll the YouTube Transcript API /healthz endpoint.")
    ap.add_argument("--url", default=DEFAULT_URL, help=f"URL to probe (default: {DEFAULT_URL})")
    ap.add_argument("--interval", type=int,
                    default=int(os.environ.get("MONITOR_INTERVAL", DEFAULT_INTERVAL)),
                    help=f"Polling interval in seconds, env override: MONITOR_INTERVAL "
                         f"(default: {DEFAULT_INTERVAL})")
    ap.add_argument("--once", action="store_true", help="Single probe, no loop")
    ap.add_argument("--probe-all", action="store_true",
                    help="Single-shot multi-probe: Vercel /healthz + every local service in "
                         "PROBE_ALL_LOCAL_SERVICES (ComfyUI :8188, Ollama :11434). Exits 0 "
                         "only if every probe is OK (strict: any unreachable service exits 1). "
                         "Use this in scheduled checks for full ecosystem visibility; --once is "
                         "the lighter single-URL probe.")
    ap.add_argument("--discord-threshold", type=int, default=DEFAULT_THRESHOLD,
                    help=f"Consecutive failures before Discord alert (default: {DEFAULT_THRESHOLD})")
    args = ap.parse_args(argv)
    webhook = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()

    print(f"monitor URL: {args.url}")
    print(f"monitor interval: {args.interval}s (use --once to skip the loop)")
    print(f"discord webhook: {'configured' if webhook else 'not configured (dry-run)'}")
    print(f"local time: {_now_local()}")
    print()

    # --probe-all branch: single-shot multi-probe, no loop, no Discord auto-post
    # (a single slow service could spam the channel). Exit code reflects
    # aggregate health so callers can use it in scheduled checks.
    if args.probe_all:
        results = _probe_all(args.url, PROBE_ALL_LOCAL_SERVICES)
        ts = _now_local()
        all_ok = True
        print(f"[monitor] {ts} probe-all results ({len(results)} targets):")
        for label, ok, detail in results:
            mark = "OK  " if ok else "FAIL"
            print(f"  [{mark}] {label} -- {detail}")
            if not ok:
                all_ok = False
        return 0 if all_ok else 1

    # Graceful Ctrl+C handling
    stop = {"flag": False}

    def _handle_sigint(signum, frame):
        stop["flag"] = True
        print("\n[monitor] stopping on SIGINT")

    signal.signal(signal.SIGINT, _handle_sigint)

    failures_in_a_row = 0
    while not stop["flag"]:
        ok, detail = _probe(args.url)
        ts = _now_local()
        if ok:
            print(f"  [{ts}] OK    — {detail}")
            failures_in_a_row = 0
        else:
            failures_in_a_row += 1
            print(f"  [{ts}] FAIL  — {detail} (consecutive: {failures_in_a_row})")
            if webhook and failures_in_a_row >= args.discord_threshold:
                msg = (f"[SLEEP_CASH] YouTube Transcript API unhealthy: "
                       f"{failures_in_a_row} consecutive failures. "
                       f"Last: {detail} at {ts}")
                posted = _discord_post(webhook, msg)
                print(f"  [{ts}] discord posted={posted}")
        if args.once:
            return 0 if ok else 1
        # Sleep in small slices so SIGINT aborts quickly
        for _ in range(args.interval):
            if stop["flag"]:
                return 0
            time.sleep(1)
    return 0


if __name__ == "__main__":
    sys.exit(main())


# --probe-all behavior summary (kept near the bottom for easy review):
#   python SLEEP_CASH_API/monitor.py --probe-all
#   Probes the live Vercel /healthz endpoint + every local service port listed
#   in PROBE_ALL_LOCAL_SERVICES. Prints one row per target. Exits 0 only if
#   every probe is OK; exits 1 if any probe is unreachable. Designed to be
#   runnable from Task Scheduler on the same cadence as --once, but with full
#   ecosystem visibility (ComfyUI + Ollama + live API). Not Discord-pinged by
#   default -- this is a wider net and a single slow service could spam the
#   channel. Operators can wire `monitor.py --probe-all` into a separate Task
#   Scheduler entry that posts its own digest if they want alerts here.
