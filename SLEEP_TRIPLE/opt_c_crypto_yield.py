#!/usr/bin/env python3
"""
opt_c_crypto_yield.py — Option C: Crypto Yield Automation.

Snapshot-only by default. Scans stablecoin spreads across AU/global exchanges,
emits "signal_emitted" rows to REVENUE_LEDGER.jsonl (mapped through the existing
event enum) and "scan_rates" / "auto_compound" / "arbitrage" markers to the audit log.

Closed enums:
    EXEC_STATUS    = (started, ok, skipped, refused, noop, failed)
    SUB_TASKS      = (scan_rates, auto_compound, arbitrage)
    EXCHANGE_ENUM  = (coinspot, kraken, independentreserve, binance)
    SIGNAL_TIER    = (none, observed, actionable, executed, refused)

Default: --dry-run snapshot only. --run without --execute keeps things dry.
Use --run --execute to attempt live trades (REFUSED unless max_capital_aud > 0).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "opt_c_config.json"
AUDIT_LOG = ROOT / "SLEEP_TRIPLE_AUDIT.jsonl"

EXEC_STATUS = ("started", "ok", "skipped", "refused", "noop", "failed")
SUB_TASKS = ("scan_rates", "auto_compound", "arbitrage")
EXCHANGE_ENUM = ("coinspot", "kraken", "independentreserve", "binance")
SIGNAL_TIER = ("none", "observed", "actionable", "executed", "refused")


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def load_master() -> dict:
    return json.loads((ROOT / "sleep_config.json").read_text(encoding="utf-8"))


def snapshot_spreads(exchanges: list[str], pairs: list[str], threshold_bps: int) -> list[dict]:
    """Return spread observations. Stub returns synthetic, deterministic-but-marked data.

    Real implementation would call CoinSpot / Kraken / IndependentReserve public APIs
    (no KYC required for snapshot endpoints). Snapshot is non-trade and zero-risk.
    Every row bears ``synthetic: True`` until a real fetcher is wired in; operators
    must NOT treat the values as authoritative.
    """
    rows = []
    demo_floor_aud = {
        "USDC/AUD": 1.49,
        "USDT/AUD": 1.48,
    }
    for ex in exchanges:
        for pair in pairs:
            base = demo_floor_aud.get(pair, 1.00)
            spread_bps = (sum(ord(c) for c in ex + pair) % 30) + 5
            ask = round(base + (spread_bps / 10000.0) * base, 4)
            tier = "actionable" if spread_bps >= threshold_bps else "observed"
            rows.append({
                "exchange": ex,
                "pair": pair,
                "ask_aud": ask,
                "spread_bps": spread_bps,
                "signal_tier": tier,
                "synthetic": True,
            })
    return rows


def append_audit(row: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, separators=(",", ":")) + "\n")


def append_ledger_event(ts: str, amount_aud: float, note: str, dry_run: bool) -> bool:
    """Append a 'signal_emitted' row to the existing REVENUE_LEDGER via the
    existing PowerShell helper. Dry-run default; helper itself defaults dry-run."""
    script = Path(r"C:\Users\karma\Append-RevenueEvent.ps1")
    if not script.exists():
        return False
    args = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", str(script),
            "-Event", "signal_emitted", "-AmountAud", f"{amount_aud:.2f}", "-Note", note]
    if dry_run:
        args.append("-DryRun")
    r = subprocess.run(args, capture_output=True, text=True)
    return r.returncode == 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Option C — Crypto Yield Automation (observation-only)")
    ap.add_argument("--dry-run", action="store_true", help="Snapshot only, no ledger writes")
    ap.add_argument("--run", action="store_true", help="Allow ledger writes (still no live trades)")
    ap.add_argument("--execute", action="store_true", help="Attempt live trade (REFUSED if max_capital_aud==0)")
    args = ap.parse_args()

    if args.execute and args.dry_run:
        print("REFUSED: --execute requires --run (cannot combine with --dry-run)", file=sys.stderr)
        append_audit({"ts": datetime.now().isoformat(), "module": "opt_c", "status": "refused",
                      "reason": "execute_with_dryrun"})
        return 5

    cfg = load_config()
    master = load_master()
    dry_run = not args.run
    tz = ZoneInfo(master.get("tz", "Australia/Sydney"))
    now_iso = datetime.now(tz).isoformat()

    append_audit({"ts": now_iso, "module": "opt_c", "status": "started",
                  "task": "scan_rates", "exchanges": cfg["exchanges_observed"],
                  "pairs": cfg["stablecoin_pairs"],
                  "dry_run": dry_run, "execute": args.execute,
                  "snapshot_only": cfg["snapshot_only"]})

    rows = snapshot_spreads(cfg["exchanges_observed"], cfg["stablecoin_pairs"],
                            cfg["stablecoin_threshold_bps"])
    actionable = [r for r in rows if r["signal_tier"] == "actionable"]
    append_audit({"ts": now_iso, "module": "opt_c", "status": "ok",
                  "task": "scan_rates", "rows_observed": len(rows),
                  "actionable_count": len(actionable),
                  "top_spread_bps": max((r["spread_bps"] for r in rows), default=0)})

    append_audit({"ts": now_iso, "module": "opt_c", "status": "ok",
                  "task": "auto_compound", "would_compound_count": 0,
                  "reason": "observation_only"})

    if actionable:
        signal_note = f"crypto spread {actionable[0]['pair']} on {actionable[0]['exchange']} " \
                      f"({actionable[0]['spread_bps']} bps)"
        emit_ok = append_ledger_event(now_iso, 0.0, signal_note, dry_run)
        append_audit({"ts": now_iso, "module": "opt_c", "status": "ok",
                      "task": "arbitrage", "actionable_pairs": len(actionable),
                      "ledger_written": emit_ok, "dry_run": dry_run})
    else:
        append_audit({"ts": now_iso, "module": "opt_c", "status": "noop",
                      "task": "arbitrage", "reason": "below_threshold"})

    if args.execute:
        if cfg.get("max_capital_aud", 0) <= 0:
            print("REFUSED: --execute blocked (max_capital_aud==0)", file=sys.stderr)
            append_audit({"ts": now_iso, "module": "opt_c", "status": "refused",
                          "reason": "no_capital_allocation", "task": "execute"})
            return 7
        master = load_master()
        daily_cap = master.get("max_daily_aud_spend", 0.0)
        if daily_cap <= 0:
            print("REFUSED: --execute blocked (max_daily_aud_spend==0 in sleep_config)", file=sys.stderr)
            append_audit({"ts": now_iso, "module": "opt_c", "status": "refused",
                          "reason": "no_daily_cap", "task": "execute"})
            return 8
        print("EXECUTE: live trade path not wired in this stub.", file=sys.stderr)
        append_audit({"ts": now_iso, "module": "opt_c", "status": "skipped",
                      "reason": "live_trade_stub"})

    print(f"[opt_c] observed {len(rows)} spread(s); actionable={len(actionable)}; dry_run={dry_run}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
