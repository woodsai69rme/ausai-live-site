#!/usr/bin/env python3
"""
_live_send_test.py — exercise one real webhook POST to verify the round-trip.

Usage:
    python _live_send_test.py                  # auto-pick first set channel
    python _live_send_test.py --channel slack  # force a specific channel
    python _live_send_test.py --trigger actionable_spread  # different trigger

Reads opt_d_alerts.CHANNEL_ENV_REQUIREMENTS so the env var list stays in
sync with the main module. Refuses politely if no channel env vars are set
and prints setup guidance instead of crashing.

Exits:
    0  - real POST succeeded (audit row records http=200/204)
    1  - audit row recorded a failure (http error, missing env var, refused)
    2  - setup error (config unreadable, opt_d_alerts.py missing)
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ALERTS = ROOT / "opt_d_alerts.py"
CONFIG = ROOT / "opt_d_config.json"
AUDIT = ROOT / "SLEEP_TRIPLE_AUDIT.jsonl"

# Mirror opt_d_alerts.CHANNEL_ENV_REQUIREMENTS so we don't have to import.
CHANNEL_ENV = {
    "discord":   ("DISCORD_WEBHOOK_URL",),
    "telegram":  ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"),
    "slack":     ("SLACK_WEBHOOK_URL",),
    "pushover":  ("PUSHOVER_APP_TOKEN", "PUSHOVER_USER_KEY"),
}
SETUP_GUIDANCE = [
    "No webhook env vars are set. Pick a channel and set the env var(s):",
    "  Discord   : set DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/<id>/<token>",
    "  Telegram  : set TELEGRAM_BOT_TOKEN=<from @BotFather> AND TELEGRAM_CHAT_ID=<chat id>",
    "  Slack     : set SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T.../B.../...",
    "  Pushover  : set PUSHOVER_APP_TOKEN=<app-token> AND PUSHOVER_USER_KEY=<user-key>",
    "On Windows: System Properties -> Environment Variables, or setx VAR \"value\" in cmd.exe.",
    "Restart your shell after changing env vars (or schtasks will inherit stale values).",
]


def detect_set_channels() -> list:
    out = []
    for name, reqs in CHANNEL_ENV.items():
        if all(os.environ.get(v) for v in reqs):
            out.append(name)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Live webhook round-trip test")
    ap.add_argument("--channel", choices=tuple(CHANNEL_ENV), default=None,
                    help="Force a specific channel. Default: first env-set channel.")
    ap.add_argument("--trigger", choices=("actionable_spread", "audit_failure", "morning_digest"),
                    default="morning_digest", help="Trigger to send (default: morning_digest)")
    ap.add_argument("--timeout", type=int, default=20, help="Process timeout, seconds")
    args = ap.parse_args()

    if not ALERTS.exists():
        print(f"ERROR: opt_d_alerts.py missing at {ALERTS}", file=sys.stderr)
        return 2
    if not CONFIG.exists():
        print(f"ERROR: opt_d_config.json missing at {CONFIG}", file=sys.stderr)
        return 2

    set_channels = detect_set_channels()
    if args.channel:
        target = args.channel
        missing = [v for v in CHANNEL_ENV[args.channel] if not os.environ.get(v)]
        if missing:
            print(f"ERROR: --channel={args.channel} but env var(s) missing: {missing}", file=sys.stderr)
            for line in SETUP_GUIDANCE:
                print(line)
            return 1
    else:
        if not set_channels:
            print("ERROR: no webhook env vars set.", file=sys.stderr)
            for line in SETUP_GUIDANCE:
                print(line)
            return 1
        target = set_channels[0]

    print(f"[live-send-test] channel={target} trigger={args.trigger}")
    # Mark audit-log size before, so we can scan only the new row.
    audit_size = AUDIT.stat().st_size if AUDIT.exists() else 0

    proc = subprocess.run(
        [sys.executable, str(ALERTS), "--run",
         "--trigger", args.trigger, "--channel", target],
        capture_output=True, text=True, timeout=args.timeout,
    )
    print(f"[live-send-test] opt_d_alerts exit code: {proc.returncode}")
    if proc.stdout.strip():
        print("--- opt_d_alerts stdout ---")
        print(proc.stdout.strip())
    if proc.stderr.strip():
        print("--- opt_d_alerts stderr ---")
        print(proc.stderr.strip())

    # Wait briefly for the audit-flush (writes happen synchronously in
    # opt_d_alerts so this is paranoia, but cheap).
    for _ in range(20):
        if AUDIT.exists() and AUDIT.stat().st_size > audit_size:
            break
        time.sleep(0.1)

    if not AUDIT.exists():
        print("ERROR: audit log not created by opt_d_alerts.", file=sys.stderr)
        return 2
    with open(AUDIT, "r", encoding="utf-8") as f:
        f.seek(audit_size)
        new_text = f.read()
    new_lines = [ln.strip() for ln in new_text.splitlines() if ln.strip()]
    if not new_lines:
        print("ERROR: no new audit rows after opt_d_alerts run.", file=sys.stderr)
        return 2

    import json as _json
    last = _json.loads(new_lines[-1])
    print(f"[live-send-test] last audit row: {last}")
    sent = last.get("sent", False)
    info = last.get("info", "")
    sc = last.get("status_code", -1)
    http_ok = bool(re.search(r"http=(200|204)", info))

    if sent and http_ok:
        print(f"PASS: real POST to {target} returned http={sc}.")
        return 0
    # Audit row recorded a failure or refused; report diagnostically.
    print(f"FAIL: opt_d_alerts returned sent={sent} status_code={sc} info={info[:200]}",
          file=sys.stderr)
    if sc == -1 and "env var" in info.lower():
        print("Hint: the channel's env var disappeared after the process started. "
              "Restart your shell.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
