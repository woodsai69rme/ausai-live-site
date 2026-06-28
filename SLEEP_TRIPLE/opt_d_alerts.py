#!/usr/bin/env python3
"""
opt_d_alerts.py — Option D: Webhook Alerter.

Reads SLEEP_TRIPLE_AUDIT.jsonl (last N hours), finds actionable signals or
failures, formats per configured channel (Discord / Telegram / Slack /
Pushover), and POSTs. Default --dry-run prints payload to stdout.

Multi-channel fanout:
    When --channel is NOT specified, opt_d_alerts inspects which target
    channels have their env vars set and sends to all of them in one run.
    Each channel's result is recorded individually; the audit row uses
    the array schema (`channels: [{name, sent, info, status_code}, ...]`)
    so rate-limits and per-channel errors don't get conflated.

    When --channel IS specified, only that single channel is targeted and
    the audit row uses the legacy single-channel schema (`channel`, `sent`,
    `info`, `status_code`) for backward compat with existing dashboard
    readers. Per-channel rate-limit still enforced.

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
import time
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

# Channel -> list of env var names that must ALL be present for the channel
# to be considered "set". Used by _detect_set_channels() for fanout.
CHANNEL_ENV_REQUIREMENTS = {
    "discord":   ("DISCORD_WEBHOOK_URL",),
    "telegram":  ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"),
    "slack":     ("SLACK_WEBHOOK_URL",),
    "pushover":  ("PUSHOVER_APP_TOKEN", "PUSHOVER_USER_KEY"),
}

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


def detect_set_channels() -> list:
    """Return [name, ...] for every channel whose all required env vars are set
    in the current process environment, in the closed enum order."""
    found = []
    for name in ALERT_CHANNEL:
        reqs = CHANNEL_ENV_REQUIREMENTS.get(name, ())
        if reqs and all(os.environ.get(v) for v in reqs):
            found.append(name)
    return found


def rate_limited(rows: list, trigger: str, channel: str, min_seconds: int) -> bool:
    """Scan recent ok rows from THIS module: if the last sent (trigger, channel)
    was within `min_seconds`, return True to debounce.

    Recognizes both legacy single-channel rows (channel field is a string)
    and new multi-channel rows (channel appears in the channels array)."""
    if min_seconds <= 0:
        return False
    cutoff = datetime.now() - timedelta(seconds=min_seconds)
    last_ts = None
    for r in rows:
        if (r.get("module") != "opt_d_alerts"
                or r.get("status") != "ok"
                or r.get("trigger") != trigger):
            continue
        # Determine which channels this row succeeded for.
        chans = r.get("channels")
        if isinstance(chans, list) and chans:
            hit_channels = {c.get("name") for c in chans
                            if isinstance(c, dict) and c.get("sent") is not False}
        else:
            hit_channels = {r.get("channel")} if r.get("sent") is not False else set()
        if channel not in hit_channels:
            continue
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


def build_payload(channel: str, tier: str, headline: str, lines: list, trigger: str) -> dict:
    if channel == "discord":
        return build_discord_payload(tier, headline, lines, trigger)
    if channel == "telegram":
        return build_telegram_payload(headline, lines)
    if channel == "slack":
        return build_slack_payload(headline, lines)
    if channel == "pushover":
        return build_pushover_payload(headline, lines)
    raise ValueError(f"unknown channel {channel}")


def send_alert(channel: str, payload: dict, dry_run: bool) -> tuple:
    """Returns (sent: bool, info: str, status_code: int or -1).
    On dry_run, sent=True because no error occurred; info explains the no-op.

    Use _send_with_retry() instead of this function directly when you want
    automatic exponential-backoff retries on transient errors. This raw
    function performs exactly one attempt."""
    if dry_run:
        safe_preview = json.dumps(payload, ensure_ascii=False)[:600]
        return True, f"dry_run (would send: {safe_preview})", _STATUS_PERMANENT_CONFIG_ERROR

    # Status-code _STATUS_PERMANENT_CONFIG_ERROR (not -1) for env-var-missing
    # branches so _send_with_retry does NOT eat retry budget on a permanent
    # config error.
    if channel == "discord":
        url = os.environ.get("DISCORD_WEBHOOK_URL")
        if not url:
            return False, "DISCORD_WEBHOOK_URL env var not set", _STATUS_PERMANENT_CONFIG_ERROR
        rc, body = https_post_json(url, payload)
        return (rc in (200, 204)), f"http={rc} body={body[:160]}", rc

    if channel == "telegram":
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat = os.environ.get("TELEGRAM_CHAT_ID")
        if not (token and chat):
            return False, "TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID env vars required", _STATUS_PERMANENT_CONFIG_ERROR
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        rc, body = https_post_json(url, {"chat_id": chat, **payload})
        return (rc == 200), f"http={rc} body={body[:160]}", rc

    if channel == "slack":
        url = os.environ.get("SLACK_WEBHOOK_URL")
        if not url:
            return False, "SLACK_WEBHOOK_URL env var not set", _STATUS_PERMANENT_CONFIG_ERROR
        rc, body = https_post_json(url, payload)
        return (rc == 200), f"http={rc} body={body[:160]}", rc

    if channel == "pushover":
        token = os.environ.get("PUSHOVER_APP_TOKEN")
        user = os.environ.get("PUSHOVER_USER_KEY")
        if not (token and user):
            return False, "PUSHOVER_APP_TOKEN + PUSHOVER_USER_KEY env vars required", _STATUS_PERMANENT_CONFIG_ERROR
        rc, body = https_post_json(
            "https://api.pushover.net/1/messages.json",
            {"token": token, "user": user, **payload},
        )
        return (rc == 200), f"http={rc} body={body[:160]}", rc

    return False, f"unknown channel {channel}", _STATUS_PERMANENT_CONFIG_ERROR


# HTTP status codes that warrant a retry. 5xx are usually transient server
# issues; 408 = client-side request timeout (could be transient); 429 = rate
# limited. Everything else (especially 4xx credentials errors like 401/403)
# is treated as a permanent failure that won't fix itself on retry.
_RETRYABLE_STATUS_CODES = frozenset({408, 429, 500, 502, 503, 504})

# Sentinel status_code sent by send_alert() when a permanent configuration
# error prevents the request (e.g. required env var missing). Distinct from
# -1 (which means retryable connect/ssl/timeout) and from any literal HTTP code.
# _is_retryable() below treats this as non-retryable so we don't burn retry
# budget on a problem that retrying cannot fix. Name the convention so a
# future refactor doesn't accidentally conflate it with success.
_STATUS_PERMANENT_CONFIG_ERROR = 0


def _safe_int(value, default: int) -> int:
    """Coerce config JSON values into int without crashing on typos like
    "auto" or empty strings. Falls back to `default` on any parse issue.
    Clamps to max(1, parsed) so a config value of 0 doesn't silently disable
    retries on transient errors that legitimately benefit from a second attempt."""
    try:
        parsed = int(value) if value is not None else default
    except (TypeError, ValueError):
        parsed = default
    return max(1, parsed)


def _safe_float(value, default: float) -> float:
    """Coerce config JSON values into float without crashing on typos.
    Clamps to max(0.0, parsed) so a negative delay never causes time.sleep
    to raise a ValueError."""
    try:
        parsed = float(value) if value is not None else default
    except (TypeError, ValueError):
        parsed = default
    return max(0.0, parsed)


def _is_retryable(sent: bool, status_code: int, info: str) -> bool:
    """Decide whether to retry a failed send. Returns True for transient
    errors (connect / timeout / 5xx / 429 / 408). Returns False for failed
    config (env var missing, `_STATUS_PERMANENT_CONFIG_ERROR`) or 4xx
    credentials errors."""
    if sent:
        return False  # success, no retry
    if status_code == _STATUS_PERMANENT_CONFIG_ERROR:
        # Permanent config error: env var missing or otherwise unfixable.
        return False
    if status_code == -1:
        # Connect error / SSL / timeout. Retry these.
        return True
    return status_code in _RETRYABLE_STATUS_CODES


def _send_with_retry(channel: str, payload: dict, dry_run: bool,
                     max_attempts: int = 3, base_delay: float = 5.0
                     ) -> tuple:
    """Wrap send_alert() with exponential backoff. Returns
    (sent, info, status_code, attempts). Dry-run does single pass, no retry.

    max_attempts: total attempts including the first try. Must be >= 1.
    base_delay:   seconds before second attempt; doubled for third, etc."""
    if dry_run:
        sent, info, status_code = send_alert(channel, payload, dry_run=True)
        return sent, info, status_code, 1

    if max_attempts < 1:
        max_attempts = 1

    sent, info, status_code = send_alert(channel, payload, dry_run=False)
    attempts = 1
    while attempts < max_attempts and _is_retryable(sent, status_code, info):
        delay = base_delay * (2 ** (attempts - 1))
        time.sleep(delay)
        sent, info, status_code = send_alert(channel, payload, dry_run=False)
        attempts += 1
    return sent, info, status_code, attempts


def detect_content(trigger: str, rows: list, audit_window_hours: int) -> tuple:
    """Returns (headline, lines, tier) for the trigger, or (None, None, None) when
    there's nothing to report (caller should noop)."""
    if trigger == "actionable_spread":
        actionable = detect_actionable_spreads(rows)
        if not actionable:
            return None, None, None
        lines = [f"- {r.get('best_pair','?')} on {r.get('best_exchange','?')} "
                 f"({r.get('best_spread_bps','?')} bps, {r.get('best_data_source','?')})"
                 for r in actionable[:5]]
        headline = f"{len(actionable)} actionable crypto spread(s) in last {audit_window_hours}h"
        max_bps = max((r.get("best_spread_bps") or 0) for r in actionable)
        return headline, lines, ("__TIER__", max_bps)  # tier computed per-call
    if trigger == "audit_failure":
        failures = detect_audit_failures(rows)
        if not failures:
            return None, None, None
        lines = [f"- {r.get('module','?')} {r.get('status','?')}: {r.get('reason','?')}"
                 for r in failures[:5]]
        headline = f"{len(failures)} audit failure(s) in last {audit_window_hours}h"
        return headline, lines, "warning"
    # morning_digest
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
    headline = f"SLEEP_TRIPLE morning digest — {total_rows} rows in last {audit_window_hours}h"
    return headline, lines, "info"


# Single source of truth for signal_emitted ledger row writes; shared with
# opt_c_crypto_yield.py. Future PS1 schema changes update one file.
from _ledger_writer import append_ledger_event


def main() -> int:
    ap = argparse.ArgumentParser(description="Option D — Webhook Alerts")
    ap.add_argument("--dry-run", action="store_true", help="Print payload, do not send")
    ap.add_argument("--run", action="store_true", help="Allow real send")
    ap.add_argument("--trigger", choices=ALERT_TRIGGER, default="actionable_spread")
    ap.add_argument("--channel", choices=ALERT_CHANNEL, default=None,
                    help="Force a single channel. Default: auto-fanout to env-set channels.")
    ap.add_argument("--fanout-mode", choices=("auto", "always", "single"), default="auto",
                    help="auto=fanout if >=2 channels set; always=ignore --channel and fanout; "
                         "single=use --channel or default_channel only.")
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

    # Resolve target channel list.
    set_channels = detect_set_channels()
    if args.channel is not None:
        targets = [args.channel]
        fanout_mode = "single"
    elif args.fanout_mode == "always":
        targets = set_channels if set_channels else [cfg.get("default_channel", "discord")]
        fanout_mode = "always"
    elif args.fanout_mode == "single":
        targets = [cfg.get("default_channel", "discord")]
        fanout_mode = "single"
    else:  # auto
        if len(set_channels) >= 2:
            targets = set_channels
            fanout_mode = "auto"
        elif len(set_channels) == 1:
            targets = set_channels
            fanout_mode = "auto"
        else:
            # No env vars set — fall back to default channel for dry-run visibility.
            targets = [cfg.get("default_channel", "discord")]
            fanout_mode = "auto"

    # Validate every target is in the closed enum.
    for ch in targets:
        if ch not in ALERT_CHANNEL:
            append_audit({"ts": now_iso, "module": "opt_d_alerts", "status": "refused",
                          "reason": "bad_channel", "channel": ch})
            return 5

    append_audit({"ts": now_iso, "module": "opt_d_alerts", "status": "started",
                  "trigger": args.trigger, "channels": targets, "fanout_mode": fanout_mode,
                  "dry_run": dry_run, "audit_window_hours": args.audit_window_hours,
                  "retry_attempts": _safe_int(cfg.get("retry_attempts"), 3),
                  "retry_base_delay": _safe_float(cfg.get("retry_backoff_seconds"), 5.0)})

    rows = read_audit_last_window(args.audit_window_hours)

    headline, lines, tier_signal = detect_content(args.trigger, rows, args.audit_window_hours)
    if headline is None:
        # No-op: nothing to report. Emit one noop row with channels list.
        append_audit({"ts": now_iso, "module": "opt_d_alerts", "status": "noop",
                      "reason": f"no_signal_in_window:{args.trigger}",
                      "trigger": args.trigger, "channels": targets, "fanout_mode": fanout_mode})
        print(f"[opt_d] no {args.trigger} signal in last {args.audit_window_hours}h; noop.")
        return 0

    # Per-channel rate-limit filter.
    rate_sec = int(cfg.get("rate_limit_seconds", 0) or 0)
    if rate_sec > 0:
        targets = [ch for ch in targets
                   if not rate_limited(rows, args.trigger, ch, rate_sec)]
        if not targets:
            append_audit({"ts": now_iso, "module": "opt_d_alerts", "status": "noop",
                          "reason": "rate_limited_all_channels",
                          "rate_limit_seconds": rate_sec, "trigger": args.trigger,
                          "channels": targets})
            print(f"[opt_d] rate-limited across all channels within last {rate_sec}s; noop.")
            return 0

    per_channel_results = []
    any_sent = False
    overall_status = "ok"
    retry_attempts_cfg = _safe_int(cfg.get("retry_attempts"), 3)
    retry_base_delay_cfg = _safe_float(cfg.get("retry_backoff_seconds"), 5.0)
    tier = None  # populated in the loop; ensure it's always defined for the audit row
    for ch in targets:
        # Compute tier per channel (signalled via tuple from detect_content).
        if isinstance(tier_signal, tuple) and tier_signal[0] == "__TIER__":
            tier = tier_for_actionable(tier_signal[1], cfg)
        else:
            tier = tier_signal
        try:
            payload = build_payload(ch, tier, headline, lines, args.trigger)
        except ValueError as exc:
            per_channel_results.append({"name": ch, "sent": False, "info": str(exc),
                                        "status_code": -1, "attempts": 0,
                                        "dry_run": dry_run, "effective": False})
            overall_status = "failed"
            continue
        sent, info, status_code, attempts = _send_with_retry(
            ch, payload, dry_run,
            max_attempts=retry_attempts_cfg,
            base_delay=retry_base_delay_cfg,
        )
        # `effective` = a real POST returned 2xx. Distinguishes dry-run success
        # and config-error returns from genuine live sends, so dashboard readers
        # can never confuse the two at a glance.
        effective = (not dry_run) and sent and status_code in (200, 201, 202, 203, 204)
        per_channel_results.append({"name": ch, "sent": sent, "info": info,
                                    "status_code": status_code, "attempts": attempts,
                                    "dry_run": dry_run, "effective": effective})
        any_sent = any_sent or sent
        if not sent and not dry_run:
            overall_status = "failed"

    # Schema: multi-channel uses `channels` array; legacy single-channel ALSO
    # keeps the four flat fields populated so dashboard readers keep working.
    audit_row = {
        "ts": now_iso,
        "module": "opt_d_alerts",
        "status": overall_status,
        "trigger": args.trigger,
        "tier": tier or "unknown",
        "channels": per_channel_results,
        "fanout_mode": fanout_mode,
        "dry_run": dry_run,
        "headline_chars": len(headline),
        "line_count": len(lines),
        "rows_scanned": len(rows),
    }
    if len(per_channel_results) == 1:
        # Backward-compat: duplicate the (only) result so single-channel readers
        # see the same fields the pre-fanout code emitted.
        only = per_channel_results[0]
        audit_row["channel"] = only["name"]
        audit_row["sent"] = only["sent"]
        audit_row["info"] = only["info"]
        audit_row["status_code"] = only["status_code"]
    append_audit(audit_row)

    # Emit one signal_emitted row per effective channel so REVENUE_LEDGER.jsonl
    # tracks every live alert dispatch. Dry-run / noop / refused / failed
    # rows do NOT emit (effective=False means no live 2xx POST happened).
    # PS1 refusal surfaces on stderr; audit row remains the source of truth
    # so dashboard readers see the original per_channel_results array.
    safe_tier = (tier or "unk")[:3]
    for ch_res in per_channel_results:
        if ch_res.get("effective"):
            ch_name = ch_res["name"]
            meta_obj = {
                "trigger": args.trigger,
                "channel": ch_name,
                "tier": tier or "unknown",
                "fanout_mode": fanout_mode,
                "rows_scanned": len(rows),
                "headline_chars": len(headline),
                "headline_preview": headline[:60],
                "line_count": len(lines),
            }
            append_ledger_event(
                ts=now_iso,
                amount_usd=0.0,
                source=f"pipeline:opt_d_alerts:{args.trigger}",
                meta_obj=meta_obj,
                dry_run=dry_run,
                id_suffix=f"{args.trigger}-{ch_name}-{safe_tier}",
            )

    print(f"[opt_d] trigger={args.trigger} tier={audit_row['tier']} "
          f"targets={targets} mode={fanout_mode} results={per_channel_results}")
    return 0 if overall_status == "ok" else 2


if __name__ == "__main__":
    sys.exit(main())
