#!/usr/bin/env python3
"""
sleep_orchestrator.py — SLEEP_TRIPLE master controller.

Runs three independent systems sequentially while user sleeps:
  Option A — AI Digital Product Factory (opt_a_digital_factory.py)
  Option B — Faceless YouTube Shorts + Affiliate (opt_b_faceless_shorts.py)
  Option C — Crypto Yield Automation (opt_c_crypto_yield.py)

Design:
  - Sequential execution to avoid GPU OOM + file-lock collisions.
  - Closed status enum: (started, ok, skipped, refused, noop, failed).
  - Each option is idempotent via today's deterministic-ID check.
  - Default --dry-run. --run gates downstream writes.
  - Rule #8 personal-folder fence rigid (refuses with exit 2).
  - Time-window gate (sleep_window) refuses with exit 3 outside.
  - All outputs append to REVENUE_LEDGER.jsonl on success.
  - All state changes append to SLEEP_TRIPLE_AUDIT.jsonl (append-only).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "sleep_config.json"
AUDIT_LOG = ROOT / "SLEEP_TRIPLE_AUDIT.jsonl"

EXEC_STATUS = ("started", "ok", "skipped", "refused", "noop", "failed")
MODULE_NAMES = ("opt_a_digital_factory.py", "opt_b_faceless_shorts.py", "opt_c_crypto_yield.py")


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def in_sleep_window(now: time, window: list[str]) -> bool:
    """Inclusive start, exclusive end. Handles overnight windows (e.g. 23:00->07:00)."""
    start = time.fromisoformat(window[0])
    end = time.fromisoformat(window[1])
    if start <= end:
        return start <= now < end
    # overnight case: e.g. 23:00 -> 07:00
    return now >= start or now < end


def is_rule_8(p: Path, fence: list[str]) -> bool:
    """Walk all path components; if any segment matches Rule #8, return True."""
    parts = {seg for seg in p.resolve().parts}
    return bool(parts & set(fence))


def check_idempotent(audit_log: Path, today_iso: str, slug: str) -> bool:
    """Return True if today's (date+slug) was already emitted with status=ok.
    Parses each JSONL line as JSON (forward-compatible with field reordering)."""
    if not audit_log.exists():
        return False
    try:
        text = audit_log.read_text(encoding="utf-8")
    except OSError:
        return False
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (row.get("date") == today_iso
                and row.get("slug") == slug
                and row.get("status") == "ok"):
            return True
    return False


def append_audit(row: dict) -> None:
    """Append-only JSONL write. Creates file on first run."""
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, separators=(",", ":")) + "\n")


def emit(row: dict, dry_run: bool) -> None:
    """Emit audit row. In dry-run, prefix [DRY-RUN] on stdout."""
    if dry_run:
        print(f"[DRY-RUN] {json.dumps(row)}")
    append_audit(row)


def run_module(module_path: Path, run_mode: bool, dry_run_default: bool, extra: list[str]) -> int:
    subprocess_args = [sys.executable, str(module_path)]
    if run_mode:
        subprocess_args.append("--run")
    else:
        subprocess_args.append("--dry-run")
    subprocess_args.extend(extra)
    return subprocess.call(subprocess_args)


def main() -> int:
    ap = argparse.ArgumentParser(description="SLEEP_TRIPLE orchestrator")
    ap.add_argument("--run", action="store_true", help="Allow live side-effects (default: --dry-run for every module)")
    ap.add_argument("--force-window", action="store_true", help="Run outside sleep window")
    ap.add_argument("--skip-a", action="store_true", help="Skip Option A")
    ap.add_argument("--skip-b", action="store_true", help="Skip Option B")
    ap.add_argument("--skip-c", action="store_true", help="Skip Option C")
    ap.add_argument("--list", action="store_true", help="List audit log and exit")
    args = ap.parse_args()

    cfg = load_config()
    fence = cfg["personal_folders_fence"]
    tz = ZoneInfo(cfg.get("tz", "Australia/Sydney"))
    now_local = datetime.now(tz)
    today_iso = now_local.date().isoformat()
    dry_run = cfg.get("dry_run_default", True) and not args.run

    if args.list:
        if not AUDIT_LOG.exists():
            print("[no audit log yet]")
            return 0
        print(AUDIT_LOG.read_text(encoding="utf-8"))
        return 0

    if is_rule_8(ROOT, fence):
        print(f"REFUSED: ROOT path {ROOT} violates Rule #8 fence ({fence})", file=sys.stderr)
        return 2

    in_window = in_sleep_window(now_local.time(), cfg["sleep_window"])
    if not in_window and not args.force_window:
        print(f"REFUSED: not in sleep window {cfg['sleep_window']} (use --force-window to override)", file=sys.stderr)
        emit({"ts": now_local.isoformat(), "module": "orchestrator", "slug": "orchestrator", "status": "refused",
              "reason": "outside_window", "window": cfg["sleep_window"], "dry_run": dry_run}, dry_run)
        return 3

    emit({"ts": now_local.isoformat(), "module": "orchestrator", "status": "started",
          "slug": "orchestrator", "date": today_iso, "dry_run": dry_run,
          "skip_a": args.skip_a, "skip_b": args.skip_b, "skip_c": args.skip_c}, dry_run)

    skips = {"opt_a_digital_factory.py": args.skip_a,
             "opt_b_faceless_shorts.py": args.skip_b,
             "opt_c_crypto_yield.py": args.skip_c}

    failures = 0
    for module_name in MODULE_NAMES:
        slug = module_name.replace(".py", "")
        module_path = ROOT / module_name
        if not module_path.exists():
            print(f"SKIP: {module_name} not found", file=sys.stderr)
            emit({"ts": now_local.isoformat(), "module": slug, "slug": slug, "status": "skipped",
                  "reason": "missing_module", "date": today_iso}, dry_run)
            continue
        if skips[module_name]:
            print(f"SKIP: {slug} (--skip flag)")
            emit({"ts": now_local.isoformat(), "module": slug, "slug": slug, "status": "skipped",
                  "reason": "user_skip", "date": today_iso}, dry_run)
            continue
        if check_idempotent(AUDIT_LOG, today_iso, slug):
            print(f"NOOP: {slug} (already completed today)")
            emit({"ts": now_local.isoformat(), "module": slug, "slug": slug, "status": "noop",
                  "reason": "idempotent_today", "date": today_iso}, dry_run)
            continue

        rc = run_module(module_path, args.run, dry_run, [])
        status = "ok" if rc == 0 else "failed"
        emit({"ts": now_local.isoformat(), "module": slug, "slug": slug, "status": status,
              "exit_code": rc, "date": today_iso, "dry_run": dry_run}, dry_run)
        if rc != 0:
            failures += 1

    emit({"ts": now_local.isoformat(), "module": "orchestrator", "slug": "orchestrator",
          "status": "ok" if failures == 0 else "failed",
          "failures": failures, "date": today_iso, "dry_run": dry_run}, dry_run)
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
