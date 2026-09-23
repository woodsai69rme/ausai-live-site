#!/usr/bin/env python3
"""
Lane-aware preflight for SLEEP_TRIPLE — credentials, services, and publish readiness.
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from env_bridge import is_placeholder, load_config  # noqa: E402

LIVE_API_URL = "https://yt-transcript-api-ebon.vercel.app/health"

LANE_PLAN: list[dict[str, Any]] = [
    {
        "id": 1,
        "name": "Lane A — Gumroad Digital Factory",
        "config": "opt_a_config.json",
        "cred_keys": ["gumroad_api_key"],
        "services": [("ComfyUI :8188", "http://127.0.0.1:8188", 8188)],
        "enabled_key": ("sleep_config.json", "options.a.enabled"),
    },
    {
        "id": 2,
        "name": "Lane B — Faceless YouTube Shorts",
        "config": "opt_b_config.json",
        "cred_keys": ["youtube_oauth_credentials_path"],
        "services": [],
        "enabled_key": ("sleep_config.json", "options.b.enabled"),
    },
    {
        "id": 3,
        "name": "Lane C — Crypto Yield (observation)",
        "config": "opt_c_config.json",
        "cred_keys": [],
        "services": [],
        "enabled_key": ("sleep_config.json", "options.c.enabled"),
    },
    {
        "id": 4,
        "name": "Lane D — API Micro-SaaS",
        "config": "opt_d_config.json",
        "cred_keys": [],
        "services": [],
        "enabled_key": ("sleep_config.json", "options.d.enabled"),
        "vital_keys": ["live_api"],
    },
    {
        "id": 5,
        "name": "Lane E — Print-on-Demand",
        "config": "opt_e_config.json",
        "cred_keys": ["shopify_store_url", "shopify_admin_api_token", "printful_api_key"],
        "services": [("ComfyUI :8188", "http://127.0.0.1:8188", 8188)],
        "enabled_key": ("sleep_config.json", "options.e.enabled"),
    },
    {
        "id": 6,
        "name": "Lane F — Discovery Engine",
        "config": "opt_f_config.json",
        "cred_keys": ["openrouter_api_key"],
        "services": [("Ollama :11434", "http://127.0.0.1:11434", 11434)],
        "enabled_key": ("sleep_config.json", "options.f.enabled"),
    },
]


def _is_placeholder(value: Any) -> bool:
    return is_placeholder(value)


def _nested_get(data: dict, dotted: str) -> Any:
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def _probe_port(port: int, host: str = "127.0.0.1", timeout: float = 1.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _probe_http(url: str, timeout: float = 5.0) -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return 200 <= resp.status < 400, f"HTTP {resp.status}"
    except urllib.error.HTTPError as exc:
        return False, f"HTTP {exc.code}"
    except Exception as exc:
        return False, str(exc)


def check_path_credential(val: Any, *, min_bytes: int = 50) -> tuple[bool, str]:
    """Validate a path-type credential (e.g. YouTube OAuth token file).

    Returns (ok, detail). ok is False when empty, placeholder, missing file, or tiny file.
    """
    if not isinstance(val, str) or not val.strip() or _is_placeholder(val):
        return False, "placeholder"
    p = Path(val).expanduser()
    if not p.is_file():
        return False, "path set but file missing"
    try:
        size = p.stat().st_size
    except OSError:
        return False, "path unreadable"
    if size <= min_bytes:
        return False, f"path set but file too small ({size}B)"
    return True, "configured"


def _lane_findings(lane: dict[str, Any]) -> dict[str, list[tuple[str, bool, str]]]:
    cfg = load_config(ROOT / lane["config"])
    master = load_config(ROOT / "sleep_config.json")
    enabled = bool(_nested_get(master, lane["enabled_key"][1]))

    creds: list[tuple[str, bool, str]] = []
    for key in lane.get("cred_keys", []):
        val = cfg.get(key, "")
        # Path-type credentials (YouTube OAuth token) must exist on disk
        if key.endswith("_path") or "credentials_path" in key:
            ok, detail = check_path_credential(val)
            creds.append((key, ok, detail))
            continue
        ok = bool(val) and not _is_placeholder(val)
        creds.append((key, ok, "configured" if ok else "placeholder"))

    services: list[tuple[str, bool, str]] = []
    for label, _url, port in lane.get("services", []):
        ok = _probe_port(port)
        services.append((label, ok, "reachable" if ok else "offline"))

    vitals: list[tuple[str, bool, str]] = []
    if not enabled:
        vitals.append(("publish_path", False, "blocked by config rule"))
    for vital in lane.get("vital_keys", []):
        if vital == "live_api":
            ok, detail = _probe_http(LIVE_API_URL)
            vitals.append(("live_api", ok, detail))

    return {"creds": creds, "services": services, "vitals": vitals}


def _lane_status(lane_name: str, findings: dict[str, list[tuple[str, bool, str]]]) -> tuple[str, str]:
    missing_creds = [k for k, ok, _ in findings["creds"] if not ok]
    # Include detail for path-type failures (e.g. "path set but file missing")
    missing_detail = [
        f"{k} ({detail})" if detail not in ("placeholder", "configured") else k
        for k, ok, detail in findings["creds"]
        if not ok
    ]
    offline_svc = [s for s, ok, _ in findings["services"] if not ok]
    blocked = [v for v, ok, msg in findings["vitals"] if not ok and "blocked" in msg]
    offline_vitals = [v for v, ok, _ in findings["vitals"] if not ok and v != "publish_path"]

    if blocked:
        return "[BLOCKED]", f"{lane_name}: publish path blocked"
    if missing_creds:
        parts = missing_detail + [s for s in offline_svc]
        return "[NEEDS_CONFIG]", f"{lane_name}: missing: {', '.join(parts)}"
    if offline_svc or offline_vitals:
        parts = offline_svc + offline_vitals
        return "[OFFLINE]", f"{lane_name}: offline: {', '.join(parts)}"
    return "[OK]", f"{lane_name}: ready"


def _format_text_output(rows: list[tuple], totals: dict[str, int], *, verbose: bool = False) -> str:
    total = totals["total"]
    lines = [
        "=" * 60,
        "SLEEP_CASH_SYSTEM v2.0 - PRE-FLIGHT CHECK",
        "=" * 60,
        "",
        f"Publishable now:    {totals['publishable']}/{total}",
        f"Needs config:       {totals['needs_config']}",
        f"Offline:            {totals['offline']}",
        f"Blocked:            {totals['blocked']}",
        "",
    ]
    if totals["publishable"] == total:
        lines.append(f"All {total} Lanes ready for live operation.")
    else:
        lines.append(f"{total - totals['publishable']} lane(s) need attention before --publish.")
    lines.append("")
    for lane_id, name, tag, summary, detail in rows:
        lines.append(f"Lane {lane_id}: {name}  {tag}")
        lines.append(f"  {summary}")
    if verbose:
        lines.extend(["", "Per-Lane detail (verbose)", "-" * 40])
        for lane_id, name, tag, summary, detail in rows:
            lines.append(f"Lane {lane_id}: {name}")
            for block in detail:
                lines.append(f"  {block}")
    lines.append("=" * 60)
    return "\n".join(lines)


def _format_json_output(
    rows: list[tuple],
    totals: dict[str, int],
    *,
    strict_would_fail: bool,
) -> str:
    lanes = []
    for lane_id, name, tag, summary, _detail in rows:
        status = tag.strip("[]")
        lanes.append({
            "id": lane_id,
            "num": lane_id,
            "name": name,
            "status": status,
            "publishable": status == "OK",
            "summary": summary,
        })
    payload = {
        "totals": totals,
        "lanes": lanes,
        "strict_would_fail": strict_would_fail,
    }
    return json.dumps(payload, indent=2)


def run_checks(*, verbose: bool = False) -> tuple[list[tuple], dict[str, int], bool]:
    rows: list[tuple] = []
    counts = {"publishable": 0, "needs_config": 0, "offline": 0, "blocked": 0}

    for lane in LANE_PLAN:
        findings = _lane_findings(lane)
        tag, summary = _lane_status(lane["name"], findings)
        detail: list[str] = []
        if verbose:
            for key, ok, msg in findings["creds"]:
                detail.append(f"cred {key}: {msg}")
            for svc, ok, msg in findings["services"]:
                detail.append(f"service {svc}: {msg}")
            for vital, ok, msg in findings["vitals"]:
                detail.append(f"vital {vital}: {msg}")
        rows.append((lane["id"], lane["name"], tag, summary, detail))

        if tag == "[OK]":
            counts["publishable"] += 1
        elif tag == "[NEEDS_CONFIG]":
            counts["needs_config"] += 1
        elif tag == "[OFFLINE]":
            counts["offline"] += 1
        elif tag == "[BLOCKED]":
            counts["blocked"] += 1

    totals = {"total": len(rows), **counts}
    strict_would_fail = counts["publishable"] != totals["total"]
    return rows, totals, strict_would_fail


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SLEEP_TRIPLE lane preflight")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Exit 1 unless all lanes publishable")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    rows, totals, strict_would_fail = run_checks(verbose=args.verbose)

    if args.json:
        print(_format_json_output(rows, totals, strict_would_fail=strict_would_fail))
    else:
        print(_format_text_output(rows, totals, verbose=args.verbose))

    if args.strict and strict_would_fail:
        print("refusing to proceed: not all lanes publishable", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())