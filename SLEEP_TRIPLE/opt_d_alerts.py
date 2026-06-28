#!/usr/bin/env python3
"""
opt_d_alerts.py — Option D: Webhook Alerter.

Reads SLEEP_TRIPLE_AUDIT.jsonl (last N hours), finds actionable signals or
failures, formats per configured channel (Discord / Telegram / Slack /
Pushover), and POSTs. Default --dry-run prints payload to stdout.

Closed enums:
    EXEC_STATUS    = (started, ok, skipped, refused, noop, failed)
    ALERT_CHANNEL  = (discord, telegram, slack, pushover)
    ALERT_TRIGGER  = (actionable_spread, audit_failure, morning_digest)
    ALERT_TIER     = (info, warning, critical)

Auth: webhook URLs and bot tokens are read from environment variables, NOT
from opt_d_config.json. This way secrets never land in git-tracked JSON.

Env vars:
  DISCORD_WEBHOOK_URL      e.g. https://discord.com/api/webhooks/<id>/<token>
  TELEGRAM_BOT_TOKEN       e.g. 123456789:ABC...
  TELEGRAM_CHAT_ID         e.g. 987654321
  SLACK_WEBHOOK_URL        e.g. https://hooks.slack.com/services/T.../B.../...
  PUSHOVER_APP_TOKEN       app-level token from pushover.net
  PUSHOVER_USER_KEY        user-level key from pushover.net
"""
from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "opt_d_config.json"
AUDIT_LOG = ROOT / "SLEEP_TRIPLE_AUDIT.jsonl"
MASTER = ROOT / "sleep_config.json"

EXEC_STATUS = ("started", "ok", "skipped", "refused", "noop", "failed")
ALERT_CHANNEL = ("discord", "telegram", "slack", "pushover")
ALERT_TRIGGER = ("actionable_spread", "audit_failure", "morning_digest")
ALERT_TIER = ("info", "warning", "critical")

# Windows Python 3.12 ships an older CA store that trips BasicConstraints-not-
# critical on some webhooks. Try verified first, fall back to CERT_NONE so
# public endpoints don't fail closed.
_UNVERIFIED_CTX = ssl.create_default_context()
_UNVERIFIED_CTX.check_hostname = False
_UNVERIFIED_CTX.verify_mode = ssl.CERT_NONE

RULE_8_FOLDERS = frozenset([
    "Documents", "Downloads", "Pictures", "Videos", "Music", "Desktop",
    "OneDrive", "ARCHIVE_OLD",
])


def is_rule_8(p: Path) -> bool:
    return bool({seg.name for seg in p.resolve().parents} & RULE_8_FOLDERS)


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def load_master() -> dict:
    return json.loads(MASTER.read_text(encoding="utf-8"))


def append_audit(row: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, separators=(",", ":")) + "\n")


def https_post_json(url: str, body: dict, timeout: float = 10.0):
    """HTTPS POST with verified TLS first, unverified fallback on SSL errors.
    Returns (status_code_or_-1, response_text_or_error)."""
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "SLEEP_TRIPLE/1.0"},
    )
    last_ssl = None
    for label, ctx in (("verified", None), ("unverified", _UNVERIFIED_CTX)):
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                return resp.status, resp.read().decode("utf-8", errors="replace")
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, ssl.SSLError) or "CERTIFICATE_VERIFY_FAILED" in str(exc):
                last_ssl = exc
                continue
            return -1, f"{exc.__class__.__name__}: {exc}"
        except (OSError, TimeoutError) as exc:
            return -1, f"{exc.__class__.__name__}: {exc}"
    return -1, f"SSL fallback failed: {last_ssl}"


def read_audit_last_window(hours: int = 24) -> list:
    """Read JSONL audit log, filter to rows with ts within last `hours`."""
    if not AUDIT_LOG.exists():
        return []
    cutoff = datetime.now() - timedelta(hours=hours)
    rows = []
    try:
        text = AUDIT_LOG.read_text(encoding="utf-8")
    except OSError:
        return []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts_str = row.get("ts")
        if not ts_str:
            continue
        try:
            ts = datetime.fromisoformat(ts_str)
        except ValueError:
            continue
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=ZoneInfo("UTC"))
        if ts.astimezone(tz=None).replace(tzinfo=None) >= cutoff:
            rows.append(row)
    return rows


def detect_actionable_spreads(rows: list) -> list:
    """Find opt_c rows where task=arbitrage and actionable_pairs > 0."""
    return [r for r in rows if r.get("module") == "opt_c"
            and r.get("task") == "arbitrage"
            and r.get("status") == "ok"
            and r.get("actionable_pairs", 0) > 0]


def detect_audit_failures(rows: list) -> list:
    """Find rows with status=failed or refused across any module."""
    return [r for r in rows if r.get("status") in ("failed", "refused")
            and r.get("module") != "opt_d_alerts"]  # don't self-loop


def rate_limited(rows: list, trigger: str, channel: str, min_seconds: int) -> bool:
    """Scan recent ok rows from THIS module: if the last sent (trigger, channel)
    was within `min_seconds`, return True to debounce."""
    if min_seconds <= 0:
        return False
    cutoff = datetime.now() - timedelta(seconds=min_seconds)
    last_ts = None
    for r in rows:
        if (r.get("module") == "opt_d_alerts"
                and r.get("status") == "ok"
                and r.get("trigger") == trigger
                and r.get("channel") == channel
                and r.get("sent") is not False):
            ts_str = r.get("ts")
            try:
                ts = datetime.fromisoformat(ts_str)
            except (TypeError, ValueError):
                continue
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=ZoneInfo("UTC"))
            if last_ts is None or ts > last_ts:
                last_ts = ts
    return (last_ts is not None
            and last_ts.astimezone(tz=None).replace(tzinfo=None) >= cutoff)


def tier_for_actionable(max_bps: float, cfg: dict) -> str:
    """Tiered severity for actionable_spread using configured thresholds."""
    th = cfg.get("tier_thresholds", {}).get("actionable_spread", {})
    crit = th.get("critical_bps", 200)
    warn = th.get("warning_bps", 100)
    if max_bps >= crit:
        return "critical"
    if max_bps >= warn:
        return "warning"
    return "info"


def build_discord_payload(tier: str, headline: str, lines: list, trigger: str) -> dict:
    colors = {"info": 5814783, "warning": 15158332, "critical": 15158332}
    # The tier prefix goes in `content` so phones show it on lock-screen push;
    # the headline goes ONLY in embeds.title (don't duplicate).
    return {
        "content": f"[{tier.upper()}] {headline}"[:1900],
        "embeds": [{
            "title": headline[:256],
            "description": "\n".join(lines)[:1900],
            "color": colors.get(tier, 5814783),
            "footer": {"text": f"SLEEP_TRIPLE · {trigger}"[:64]},
        }],
        "allowed_mentions": {"parse": []},
    }


def build_telegram_payload(headline: str, lines: list) -> dict:
    text = f"<b>{headline[:200]}</b>\n" + "\n".join(line.replace("&", "&amp;").replace("<", "&lt;")
                                                              for line in lines)
    return {"text": text[:4000], "parse_mode": "HTML"}


def build_slack_payload(headline: str, lines: list) -> dict:
    return {
        "text": f"*{headline}*"[:3000],
        "blocks": [
            {"type": "section",
             "text": {"type": "mrkdwn",
                      "text": ("*" + headline + "*\n" + "\n".join(lines))[:2900]}},
        ],
    }


def build_pushover_payload(headline: str, lines: list) -> dict:
    return {"message": (headline + "\n" + "\n".join(lines))[:1024]}


def send_alert(channel: str, payload: dict, dry_run: bool) -> tuple:
    """Returns (sent: bool, info: str, status_code: int or -1).
    On dry_run, sent=True because no error occurred; info explains the no-op."""
    if dry_run:
        safe_preview = json.dumps(payload, ensure_ascii=False)[:600]
        return True, f"dry_run (would send: {safe_preview})", 0

    if channel == "discord":
        url = os.environ.get("DISCORD_WEBHOOK_URL")
        if not url:
            return False, "DISCORD_WEBHOOK_URL env var not set", -1
        rc, body = https_post_json(url, payload)
        return (rc in (200, 204)), f"http={rc} body={body[:160]}", rc

    if channel == "telegram":
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat = os.environ.get("TELEGRAM_CHAT_ID")
        if not (token and chat):
            return False, "TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID env vars required", -1
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        rc, body = https_post_json(url, {"chat_id": chat, **payload})
        return (rc == 200), f"http={rc} body={body[:160]}", rc

    if channel == "slack":
        url = os.environ.get("SLACK_WEBHOOK_URL")
        if not url:
            return False, "SLACK_WEBHOOK_URL env var not set", -1
        rc, body = https_post_json(url, payload)
        return (rc == 200), f"http={rc} body={body[:160]}", rc

    if channel == "pushover":
        token = os.environ.get("PUSHOVER_APP_TOKEN")
        user = os.environ.get("PUSHOVER_USER_KEY")
        if not (token and user):
            return False, "PUSHOVER_APP_TOKEN + PUSHOVER_USER_KEY env vars required", -1
        rc, body = https_post_json(
            "https://api.pushover.net/1/messages.json",
            {"token": token, "user": user, **payload},
        )
        return (rc == 200), f"http={rc} body={body[:160]}", rc

    return False, f"unknown channel {channel}", -1


def main() -> int:
    ap = argparse.ArgumentParser(description="Option D — Webhook Alerts")
    ap.add_argument("--dry-run", action="store_true", help="Print payload, do not send")
    ap.add_argument("--run", action="store_true", help="Allow real send")
    ap.add_argument("--trigger", choices=ALERT_TRIGGER, default="actionable_spread")
    ap.add_argument("--channel", choices=ALERT_CHANNEL, default="discord")
    ap.add_argument("--audit-window-hours", type=int, default=24)
    args = ap.parse_args()

    if args.dry_run and args.run:
        print("REFUSED: --dry-run and --run together", file=sys.stderr)
        append_audit({"ts": datetime.now().isoformat(), "module": "opt_d_alerts",
                      "status": "refused", "reason": "dryrun_and_run"})
        return 5

    try:
        cfg = load_config()
    except (json.JSONDecodeError, FileNotFoundError) as exc:
        print(f"ERROR: opt_d_config.json unreadable: {exc}", file=sys.stderr)
        append_audit({"ts": datetime.now().isoformat(), "module": "opt_d_alerts",
                      "status": "refused", "reason": "config_unreadable"})
        return 2

    master = load_master()
    dry_run = not args.run
    tz = ZoneInfo(master.get("tz", "Australia/Sydney"))
    now_iso = datetime.now(tz).isoformat()

    if is_rule_8(ROOT):
        append_audit({"ts": now_iso, "module": "opt_d_alerts", "status": "refused",
                      "reason": "rule8_path", "path": str(ROOT)})
        print(f"REFUSED: ROOT path {ROOT} violates Rule #8 fence", file=sys.stderr)
        return 2

    if args.trigger not in ALERT_TRIGGER:
        append_audit({"ts": now_iso, "module": "opt_d_alerts", "status": "refused",
                      "reason": "bad_trigger", "trigger": args.trigger})
        return 5
    if args.channel not in ALERT_CHANNEL:
        append_audit({"ts": now_iso, "module": "opt_d_alerts", "status": "refused",
                      "reason": "bad_channel", "channel": args.channel})
        return 5

    append_audit({"ts": now_iso, "module": "opt_d_alerts", "status": "started",
                  "trigger": args.trigger, "channel": args.channel,
                  "dry_run": dry_run,
                  "audit_window_hours": args.audit_window_hours})

    rows = read_audit_last_window(args.audit_window_hours)

    # Debounce: don't fire the same (trigger, channel) twice within rate_limit_seconds.
    rate_sec = int(cfg.get("rate_limit_seconds", 0) or 0)
    if rate_sec > 0 and rate_limited(rows, args.trigger, args.channel, rate_sec):
        append_audit({"ts": now_iso, "module": "opt_d_alerts", "status": "noop",
                      "reason": "rate_limited", "rate_limit_seconds": rate_sec,
                      "trigger": args.trigger, "channel": args.channel})
        print(f"[opt_d] rate-limited: same trigger+channel sent within last {rate_sec}s; noop.")
        return 0

    if args.trigger == "actionable_spread":
        actionable = detect_actionable_spreads(rows)
        if not actionable:
            append_audit({"ts": now_iso, "module": "opt_d_alerts", "status": "noop",
                          "reason": "no_actionable_in_window",
                          "trigger": args.trigger, "channel": args.channel})
            print(f"[opt_d] no actionable spreads in last {args.audit_window_hours}h; noop.")
            return 0
        lines = [f"- {r.get('best_pair','?')} on {r.get('best_exchange','?')} "
                 f"({r.get('best_spread_bps','?')} bps, {r.get('best_data_source','?')})"
                 for r in actionable[:5]]
        headline = f"{len(actionable)} actionable crypto spread(s) in last {args.audit_window_hours}h"
        max_bps = max((r.get("best_spread_bps") or 0) for r in actionable)
        tier = tier_for_actionable(max_bps, cfg)
    elif args.trigger == "audit_failure":
        failures = detect_audit_failures(rows)
        if not failures:
            append_audit({"ts": now_iso, "module": "opt_d_alerts", "status": "noop",
                          "reason": "no_failures_in_window",
                          "trigger": args.trigger, "channel": args.channel})
            print(f"[opt_d] no audit failures in last {args.audit_window_hours}h; noop.")
            return 0
        lines = [f"- {r.get('module','?')} {r.get('status','?')}: {r.get('reason','?')}"
                 for r in failures[:5]]
        headline = f"{len(failures)} audit failure(s) in last {args.audit_window_hours}h"
        tier = "warning"
    else:  # morning_digest
        total_rows = len(rows)
        by_status = {}
        by_module = {}
        for r in rows:
            s = r.get("status", "unknown")
            by_status[s] = by_status.get(s, 0) + 1
            m = r.get("module", "unknown")
            by_module[m] = by_module.get(m, 0) + 1
        lines = [f"- {s}: {n}" for s, n in sorted(by_status.items())]
        lines.append("")
        lines.append("**by module:**")
        lines.extend(f"- {m}: {n}" for m, n in sorted(by_module.items()))
        headline = f"SLEEP_TRIPLE morning digest — {total_rows} rows in last {args.audit_window_hours}h"
        tier = "info"

    if args.channel == "discord":
        payload = build_discord_payload(tier, headline, lines, args.trigger)
    elif args.channel == "telegram":
        payload = build_telegram_payload(headline, lines)
    elif args.channel == "slack":
        payload = build_slack_payload(headline, lines)
    else:
        payload = build_pushover_payload(headline, lines)

    sent, info, status = send_alert(args.channel, payload, dry_run)
    append_audit({"ts": now_iso, "module": "opt_d_alerts", "status": "ok" if sent else "failed",
                  "trigger": args.trigger, "channel": args.channel, "tier": tier,
                  "sent": sent, "info": info, "status_code": status, "dry_run": dry_run,
                  "headline_chars": len(headline), "line_count": len(lines),
                  "rows_scanned": len(rows)})
    print(f"[opt_d] channel={args.channel} trigger={args.trigger} tier={tier} "
          f"sent={sent} info={info}")
    return 0 if sent else 2


if __name__ == "__main__":
    sys.exit(main())
