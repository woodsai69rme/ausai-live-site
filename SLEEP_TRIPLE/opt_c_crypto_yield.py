#!/usr/bin/env python3
"""
opt_c_crypto_yield.py — Option C: Crypto Yield Automation.

Snapshot-only by default. Hits CoinSpot public v2/latest + Kraken public Ticker
endpoints for live USDC/USDT/BTC-AUD prices, computes spread in basis points
across exchanges, emits "signal_emitted" rows to REVENUE_LEDGER.jsonl when
spreads cross the configured threshold.

Closed enums:
    EXEC_STATUS    = (started, ok, skipped, refused, noop, failed)
    SUB_TASKS      = (scan_rates, auto_compound, arbitrage)
    EXCHANGE_ENUM  = (coinspot, kraken, independentreserve, binance)
    SIGNAL_TIER    = (none, observed, actionable, executed, refused)

Default: --dry-run snapshot only. --run without --execute keeps things dry.
Use --run --execute to attempt live trades (REFUSED unless max_capital_aud > 0
AND max_daily_aud_spend > 0).
"""

from __future__ import annotations

import argparse
import json
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "opt_c_config.json"
AUDIT_LOG = ROOT / "SLEEP_TRIPLE_AUDIT.jsonl"

# Windows Python 3.12 ships an older CA store that flags BasicConstraints as
# non-critical on some chains (CoinSpot in particular). Try verified first,
# fall back to CERT_NONE so the public read-only fetches don't fail closed.
_UNVERIFIED_CTX = ssl.create_default_context()
_UNVERIFIED_CTX.check_hostname = False
_UNVERIFIED_CTX.verify_mode = ssl.CERT_NONE

EXEC_STATUS = ("started", "ok", "skipped", "refused", "noop", "failed")
SUB_TASKS = ("scan_rates", "auto_compound", "arbitrage")
EXCHANGE_ENUM = ("coinspot", "kraken", "independentreserve", "binance")
SIGNAL_TIER = ("none", "observed", "actionable", "executed", "refused")

COINSPOT_BASE = "https://www.coinspot.com.au/pubapi/v2/latest"
KRAKEN_BASE = "https://api.kraken.com/0/public"
UA = "SLEEP_TRIPLE/1.0"
AUD_PER_USD_FALLBACK = 1.50


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def load_master() -> dict:
    return json.loads((ROOT / "sleep_config.json").read_text(encoding="utf-8"))


def https_get_json(url: str, timeout: float = 8.0):
    """GET url with UA header. Tries verified TLS first; falls back to CERT_NONE
    on stale Windows CA store BasicConstraint failures. Returns parsed JSON or None."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    last_ssl_err = None
    for label, ctx in (("verified", None), ("unverified", _UNVERIFIED_CTX)):
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                if label == "unverified":
                    print(f"[opt_c] TLS verify disabled for {url} (Windows CA store)",
                          file=sys.stderr)
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            reason = exc.reason
            if isinstance(reason, ssl.SSLError) or "CERTIFICATE_VERIFY_FAILED" in str(exc):
                last_ssl_err = exc
                continue
            print(f"[opt_c] fetch failed ({url}): {exc.__class__.__name__}: {exc}",
                  file=sys.stderr)
            return None
        except (OSError, json.JSONDecodeError, TimeoutError) as exc:
            print(f"[opt_c] fetch failed ({url}): {exc.__class__.__name__}: {exc}",
                  file=sys.stderr)
            return None
    print(f"[opt_c] fetch failed ({url}): SSL verify error and unverified fallback also failed: {last_ssl_err}",
          file=sys.stderr)
    return None


def coinspot_fetch(coin: str, timeout: float = 8.0):
    """Fetch CoinSpot latest price for a coin (USDC, USDT, BTC). Returns dict or None."""
    data = https_get_json(f"{COINSPOT_BASE}/{coin}", timeout)
    if not data or data.get("status") != "ok":
        return None
    payload = data.get("message", {}).get(coin, {})
    if not payload:
        return None
    last = payload.get("last")
    bid = payload.get("bid") or last
    ask = payload.get("ask") or last
    if last is None:
        return None
    return {"bid_aud": float(bid), "ask_aud": float(ask), "last_aud": float(last),
            "data_source": "real"}


def kraken_fetch(pair: str, aud_per_usd: float = AUD_PER_USD_FALLBACK, timeout: float = 8.0):
    """Fetch Kraken ticker for a pair. Converts USD price to AUD via static FX."""
    pair_code = {"USDC/AUD": "USDCUSD", "USDT/AUD": "USDTUSD",
                 "BTC/AUD": "XBTAUD", "XBT/AUD": "XBTAUD",
                 "USDC/USD": "USDCUSD", "USDT/USD": "USDTUSD"}.get(pair, pair.replace("/", ""))
    data = https_get_json(f"{KRAKEN_BASE}/Ticker?pair={pair_code}", timeout)
    if not data or data.get("error"):
        return None
    result = data.get("result", {})
    if not result:
        return None
    canonical, info = next(iter(result.items()))
    bid_raw = float(info.get("b", ["0"])[0])
    ask_raw = float(info.get("a", ["0"])[0])
    if bid_raw == 0 or ask_raw == 0:
        return None
    if pair_code.endswith("USD"):
        bid = round(bid_raw * aud_per_usd, 4)
        ask = round(ask_raw * aud_per_usd, 4)
    else:
        bid, ask = bid_raw, ask_raw
    last = round((bid + ask) / 2, 4)
    return {"bid_aud": bid, "ask_aud": ask, "last_aud": last,
            "data_source": "real", "canonical": canonical}


def snapshot_spreads(exchanges: list, pairs: list, threshold_bps: int) -> list:
    """For each (exchange, pair): hit public API; fall back to synthetic placeholder.

    Each row records data_source ∈ {real, synthetic} so audit consumers can tell
    live fetches from stub rows apart."""
    rows = []
    demo_floor_aud = {"USDC/AUD": 1.49, "USDT/AUD": 1.48, "BTC/AUD": 165000.0}

    for ex in exchanges:
        for pair in pairs:
            base_coin = pair.split("/")[0]
            row = None
            if ex == "coinspot":
                row = coinspot_fetch(base_coin)
            elif ex == "kraken":
                row = kraken_fetch(pair)
            elif ex == "independentreserve":
                # No fetcher wired — clear placeholder
                row = None

            if row:
                spread_bps = int(round((row["ask_aud"] - row["bid_aud"]) / max(row["last_aud"], 0.0001) * 10000))
                tier = "actionable" if spread_bps >= threshold_bps else "observed"
                rows.append({
                    "exchange": ex, "pair": pair,
                    "bid_aud": row["bid_aud"], "ask_aud": row["ask_aud"],
                    "last_aud": row["last_aud"], "spread_bps": spread_bps,
                    "signal_tier": tier, "data_source": "real",
                })
            else:
                base = demo_floor_aud.get(pair, 1.00)
                spread_bps = (sum(ord(c) for c in ex + pair) % 30) + 5
                ask = round(base + (spread_bps / 10000.0) * base, 4)
                tier = "actionable" if spread_bps >= threshold_bps else "observed"
                rows.append({
                    "exchange": ex, "pair": pair,
                    "bid_aud": round(base, 4), "ask_aud": ask,
                    "last_aud": round((base + ask) / 2, 4), "spread_bps": spread_bps,
                    "signal_tier": tier, "data_source": "synthetic",
                })
    return rows


def append_audit(row: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, separators=(",", ":")) + "\n")


def append_ledger_event(ts: str, amount_aud: float, note: str, dry_run: bool) -> bool:
    """Append a 'signal_emitted' row via the existing PowerShell helper."""
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

    if args.dry_run and args.run:
        print("REFUSED: --dry-run and --run together (dry-run wins; drop --dry-run to allow side-effects)",
              file=sys.stderr)
        append_audit({"ts": datetime.now().isoformat(), "module": "opt_c", "status": "refused",
                      "reason": "dryrun_and_run"})
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
    real_count = sum(1 for r in rows if r["data_source"] == "real")
    synth_count = len(rows) - real_count
    append_audit({"ts": now_iso, "module": "opt_c", "status": "ok",
                  "task": "scan_rates", "rows_observed": len(rows),
                  "real_fetches": real_count, "synthetic_fallbacks": synth_count,
                  "actionable_count": len(actionable),
                  "top_spread_bps": max((r["spread_bps"] for r in rows), default=0)})

    append_audit({"ts": now_iso, "module": "opt_c", "status": "ok",
                  "task": "auto_compound", "would_compound_count": 0,
                  "reason": "observation_only"})

    if actionable:
        best = actionable[0]
        signal_note = (f"crypto spread {best['pair']} on {best['exchange']} "
                       f"({best['spread_bps']} bps, {best['data_source']})")
        emit_ok = append_ledger_event(now_iso, 0.0, signal_note, dry_run)
        append_audit({"ts": now_iso, "module": "opt_c", "status": "ok",
                      "task": "arbitrage", "actionable_pairs": len(actionable),
                      "ledger_written": emit_ok, "dry_run": dry_run,
                      "best_pair": best["pair"], "best_exchange": best["exchange"],
                      "best_spread_bps": best["spread_bps"],
                      "best_data_source": best["data_source"]})
    else:
        append_audit({"ts": now_iso, "module": "opt_c", "status": "noop",
                      "task": "arbitrage", "reason": "below_threshold"})

    if args.execute:
        if cfg.get("max_capital_aud", 0) <= 0:
            print("REFUSED: --execute blocked (max_capital_aud==0)", file=sys.stderr)
            append_audit({"ts": now_iso, "module": "opt_c", "status": "refused",
                          "reason": "no_capital_allocation", "task": "execute"})
            return 7
        daily_cap = master.get("max_daily_aud_spend", 0.0)
        if daily_cap <= 0:
            print("REFUSED: --execute blocked (max_daily_aud_spend==0 in sleep_config)", file=sys.stderr)
            append_audit({"ts": now_iso, "module": "opt_c", "status": "refused",
                          "reason": "no_daily_cap", "task": "execute"})
            return 8
        print("EXECUTE: live trade path not wired in this stub.", file=sys.stderr)
        append_audit({"ts": now_iso, "module": "opt_c", "status": "skipped",
                      "reason": "live_trade_stub"})

    print(f"[opt_c] observed {len(rows)} spread(s); actionable={len(actionable)}; "
          f"real={real_count} synthetic={synth_count}; dry_run={dry_run}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
