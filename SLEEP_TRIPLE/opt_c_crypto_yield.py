#!/usr/bin/env python3
"""
opt_c_crypto_yield.py — Option C: Crypto Yield Automation.

Snapshot-only by default. Hits CoinSpot public v2/latest + Kraken public Ticker
+ IndependentReserve public GetMarketSummary for live AUD prices on
USDC/USDT/BTC. Derives live AUD/USD via BTC pivot when needed for USD-pair
fetches. Computes spread in basis points across exchanges, emits
"signal_emitted" rows to REVENUE_LEDGER.jsonl when spreads cross the configured
threshold.

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
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# Single source of truth for signal_emitted ledger row writes; shared with
# opt_d_alerts.py. Future PS1 schema changes update one file.
from _ledger_writer import append_ledger_event

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "opt_c_config.json"
AUDIT_LOG = ROOT / "SLEEP_TRIPLE_AUDIT.jsonl"

EXEC_STATUS = ("started", "ok", "skipped", "refused", "noop", "failed")
SUB_TASKS = ("scan_rates", "auto_compound", "arbitrage")
EXCHANGE_ENUM = ("coinspot", "kraken", "independentreserve", "binance")
SIGNAL_TIER = ("none", "observed", "actionable", "executed", "refused")

COINSPOT_BASE = "https://www.coinspot.com.au/pubapi/v2/latest"
KRAKEN_BASE = "https://api.kraken.com/0/public"
IR_BASE = "https://api.independentreserve.com/Public"
UA = "SLEEP_TRIPLE/1.0"

# Some Windows Python 3.12 installs trip BasicConstraints-not-critical on
# weaker CAs (CoinSpot in particular). Try verified first, fall back to
# CERT_NONE so public read-only fetches don't fail closed.
_UNVERIFIED_CTX = ssl.create_default_context()
_UNVERIFIED_CTX.check_hostname = False
_UNVERIFIED_CTX.verify_mode = ssl.CERT_NONE


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def load_master() -> dict:
    return json.loads((ROOT / "sleep_config.json").read_text(encoding="utf-8"))


def https_get_json(url: str, timeout: float = 8.0):
    """GET url with UA header. Tries verified TLS first; falls back to CERT_NONE
    on Windows CA store BasicConstraint failures. Returns parsed JSON or None."""
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


KRAKEN_SYM_MAP = {"BTC": "XBT", "XBT": "XBT"}


def kraken_fetch(pair: str, aud_per_usd: float | None = None, timeout: float = 8.0):
    """Fetch Kraken ticker. Pairs ending in /USD return raw USD; pairs ending
    in /AUD return AUD directly. If aud_per_usd is supplied and the pair is
    /USD, also returns AUD-converted values.

    data_source values:
      - 'real'            : pair was /AUD, native AUD market (XBTAUD).
      - 'real_derived_fx' : /USD pair converted to AUD via passed fx_aud_per_usd.

    Returns None when fetch fails, response empty, or unsupported pair shape.
    """
    if "/" not in pair:
        return None
    base = pair.split("/")[0].upper()
    quote = pair.split("/")[1].upper()
    sym = KRAKEN_SYM_MAP.get(base, base)
    pair_code = f"{sym}{quote}"

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
    last_raw = (bid_raw + ask_raw) / 2

    if quote == "AUD":
        return {"bid_aud": round(bid_raw, 4),
                "ask_aud": round(ask_raw, 4),
                "last_aud": round(last_raw, 4),
                "data_source": "real",
                "canonical": canonical, "pair_code": pair_code}
    if quote == "USD" and aud_per_usd is not None:
        return {"bid_usd": round(bid_raw, 6),
                "ask_usd": round(ask_raw, 6),
                "last_usd": round(last_raw, 6),
                "bid_aud": round(bid_raw * aud_per_usd, 4),
                "ask_aud": round(ask_raw * aud_per_usd, 4),
                "last_aud": round(last_raw * aud_per_usd, 4),
                "fx_aud_per_usd": aud_per_usd,
                "data_source": "real_derived_fx",
                "canonical": canonical, "pair_code": pair_code}
    return None


def _derive_aud_per_usd(timeout: float = 8.0):
    """Live AUD/USD via BTC pivot: CoinSpot BTC/AUD ÷ Kraken BTCUSD midpoint.

    Both legs do real fetches. If either fails or the derived rate falls
    outside the sanity band (1.00 ≤ x ≤ 2.00, ruling out malformed inputs),
    returns None so the caller can fall back to synthetic data."""
    cs = coinspot_fetch("BTC", timeout)
    if not cs:
        return None
    data = https_get_json(f"{KRAKEN_BASE}/Ticker?pair=XBTUSD", timeout)
    if not data or data.get("error") or not data.get("result"):
        return None
    _, info = next(iter(data["result"].items()))
    bid_raw = float(info.get("b", ["0"])[0])
    ask_raw = float(info.get("a", ["0"])[0])
    if bid_raw == 0 or ask_raw == 0:
        return None
    last_usd = round((bid_raw + ask_raw) / 2, 6)
    if last_usd <= 0:
        return None
    aud_per_usd = cs["last_aud"] / last_usd
    if not (1.0 <= aud_per_usd <= 2.0):
        return None
    return round(aud_per_usd, 4)


# IR public API uses mixed-case symbol prefixes; map common AU pairs.
IR_SYM_MAP = {
    "BTC": "Xbt", "ETH": "Eth", "USDT": "Usdt", "USDC": "Usdc",
    "XRP": "Xrp", "DOGE": "Doge", "ADA": "Ada", "BCH": "Bch",
    "LTC": "Ltc", "EOS": "Eos", "XLM": "Xlm", "DOT": "Dot",
    "LINK": "Link", "ZEC": "Zec",
}


def independentreserve_fetch(pair: str, timeout: float = 8.0):
    """Fetch IndependentReserve GetMarketSummary for a primary/AUD pair.

    Uses IR's BestBid/BestAsk for true top-of-book bid/ask when present.
    Falls back to a conservative day-range approximation around LastPrice
    (DayLow/DayHigh) when BestBid/BestAsk are missing — common on less-liquid
    pairs. Annotates data_source as 'real' or 'real_dayrange_approx' so the
    audit log distinguishes them."""
    if "/" not in pair:
        return None
    base = pair.split("/")[0].upper()
    quote = pair.split("/")[1].upper()
    if quote != "AUD":
        return None
    ir_sym = IR_SYM_MAP.get(base)
    if ir_sym is None:
        return None  # unsupported pair; caller falls back to synthetic
    url = (f"{IR_BASE}/GetMarketSummary"
           f"?primaryCurrencyCode={ir_sym}&secondaryCurrencyCode=Aud")
    data = https_get_json(url, timeout)
    if not data or not isinstance(data, dict):
        return None
    last = data.get("LastPrice")
    if last is None:
        return None
    last = float(last)
    # IR public API uses CurrentHighestBidPrice / CurrentLowestOfferPrice for
    # top-of-book (NOT BestBid/BestAsk — those keys return null in IR schema).
    top_bid = data.get("CurrentHighestBidPrice")
    top_ask = data.get("CurrentLowestOfferPrice")
    if top_bid is not None and top_ask is not None:
        bid, ask = float(top_bid), float(top_ask)
        source_label = "real"
    else:
        # Conservative day-range approx when order-book fields missing.
        day_low = float(data.get("DayLow") or last)
        day_high = float(data.get("DayHigh") or last)
        bid = (day_low + last) / 2
        ask = (last + day_high) / 2
        source_label = "real_dayrange_approx"
    return {"bid_aud": round(bid, 4), "ask_aud": round(ask, 4),
            "last_aud": round(last, 4), "data_source": source_label,
            "canonical": f"{ir_sym}Aud"}


def snapshot_spreads(exchanges: list, pairs: list, threshold_bps: int) -> list:
    """For each (exchange, pair): hit public API; fall back to synthetic placeholder.

    Each row records data_source in one of:
      - 'real'                  — AUD-native fetch (CoinSpot, IR w/ BestBid, XBTAUD).
      - 'real_dayrange_approx'  — IR fetch whose BestBid/BestAsk were missing;
                                   bid/ask derived from DayLow/DayHigh around LastPrice.
      - 'real_derived_fx'       — USD-pair fetch converted via live BTC-pivot FX.
      - 'synthetic'             — every real leg failed for this (ex, pair).
    """
    rows = []
    demo_floor_aud = {"USDC/AUD": 1.49, "USDT/AUD": 1.48, "BTC/AUD": 165000.0}

    live_fx = None
    for ex in exchanges:
        for pair in pairs:
            base_coin = pair.split("/")[0]
            row = None
            if ex == "coinspot":
                row = coinspot_fetch(base_coin)
            elif ex == "kraken":
                if pair.endswith("/AUD") and base_coin in ("BTC", "XBT"):
                    row = kraken_fetch("BTC/AUD")
                else:
                    if live_fx is None:
                        live_fx = _derive_aud_per_usd()
                    if live_fx is not None:
                        row = kraken_fetch(f"{base_coin}/USD", aud_per_usd=live_fx)
            elif ex == "independentreserve":
                row = independentreserve_fetch(pair)

            if row and "last_aud" in row:
                spread_bps = int(round((row["ask_aud"] - row["bid_aud"]) / max(row["last_aud"], 0.0001) * 10000))
                tier = "actionable" if spread_bps >= threshold_bps else "observed"
                rows.append({
                    "exchange": ex, "pair": pair,
                    "bid_aud": row["bid_aud"], "ask_aud": row["ask_aud"],
                    "last_aud": row["last_aud"], "spread_bps": spread_bps,
                    "signal_tier": tier, "data_source": row["data_source"],
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
    real_native = sum(1 for r in rows if r["data_source"] == "real")
    fx_derived_count = sum(1 for r in rows if r["data_source"] == "real_derived_fx")
    real_dayrange = sum(1 for r in rows if r["data_source"] == "real_dayrange_approx")
    real_count = real_native + fx_derived_count + real_dayrange  # all non-synthetic
    synth_count = len(rows) - real_count
    append_audit({"ts": now_iso, "module": "opt_c", "status": "ok",
                  "task": "scan_rates", "rows_observed": len(rows),
                  "real_native": real_native,
                  "real_derived_fx": fx_derived_count,
                  "real_dayrange_approx": real_dayrange,
                  "synthetic_fallbacks": synth_count,
                  "actionable_count": len(actionable),
                  "top_spread_bps": max((r["spread_bps"] for r in rows), default=0)})

    append_audit({"ts": now_iso, "module": "opt_c", "status": "ok",
                  "task": "auto_compound", "would_compound_count": 0,
                  "reason": "observation_only"})

    if actionable:
        best = actionable[0]
        signal_note = (f"crypto spread {best['pair']} on {best['exchange']} "
                       f"({best['spread_bps']} bps, {best['data_source']})")

        meta_obj = {
            "pair": best["pair"],
            "exchange": best["exchange"],
            "spread_bps": best["spread_bps"],
            "data_source": best["data_source"],
            "note": signal_note,
        }
        # Derive id_suffix from signal identity so 2 actionable spreads within
        # the same second don't collide on --Id. (Collision would dup the id in
        # Append-RevenueAggregator.ps1's per-group id list; a downstream
        # idempotency check that assumes id-uniqueness would undercount.)
        id_suffix = f"{best['pair'].replace('/', '-')}-{best['exchange']}-{best['spread_bps']}b"
        emit_ok = append_ledger_event(
            ts=now_iso,
            amount_usd=0.0,
            source="pipeline:opt_c_crypto_yield",
            meta_obj=meta_obj,
            dry_run=dry_run,
            id_suffix=id_suffix,
        )
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
          f"real={real_count} (native={real_native}, fx_derived={fx_derived_count}, "
          f"dayrange={real_dayrange}) synthetic={synth_count}; dry_run={dry_run}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
