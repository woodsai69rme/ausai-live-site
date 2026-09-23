#!/usr/bin/env python3
"""
autonomous_master.py — Fully autonomous SLEEP_TRIPLE controller.

Runs once per night (intended to be triggered by Windows Task Scheduler):
  1. Service recovery — ensure Ollama, ComfyUI, and other dependencies are up.
  2. Preflight — verify lane readiness (non-blocking in dry-run mode).
  3. Orchestrator — run sleep_orchestrator.py to execute revenue lanes.
  4. Audit — append a summary row to SLEEP_TRIPLE_AUDIT.jsonl.

Safety:
  - Respects Rule #8 personal-folder fence.
  - Never leaves dry-run mode unless sleep_config.json explicitly sets
    "autonomous_master.dry_run_default": false AND the --run flag is passed.
  - Capital protection: Lane C crypto execution remains observation-only
    unless max_capital_aud > 0.

Usage:
  python autonomous_master.py              # dry-run, safe default
  python autonomous_master.py --run        # allow live side-effects (requires config opt-in)
  python autonomous_master.py --recover    # only recover services, then exit
  python autonomous_master.py --status     # print last autonomous run summary
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
CONFIG_PATH = ROOT / "sleep_config.json"
AUDIT_LOG = ROOT / "SLEEP_TRIPLE_AUDIT.jsonl"
ORCHESTRATOR = ROOT / "sleep_orchestrator.py"
PREFLIGHT = ROOT / "preflight.py"
SERVICE_STARTER = ROOT.parent / "TOOLS" / "start_offline_services.py"
WATCHDOG = ROOT.parent / "ZEROONE" / "core" / "service_watchdog.py"

RULE_8_FOLDERS = frozenset(
    ["Documents", "Downloads", "Pictures", "Videos", "Music", "Desktop",
     "OneDrive", "ARCHIVE_OLD"]
)


def is_rule_8(p: Path) -> bool:
    return bool({seg.name for seg in p.resolve().parents} & RULE_8_FOLDERS)


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def append_audit(row: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, separators=(",", ":")) + "\n")


def run_command(cmd: list[str], timeout: float | None = 300.0) -> tuple[int, str, str]:
    """Run a command and return (rc, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            cwd=str(ROOT)
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"command timed out after {timeout}s"
    except Exception as exc:
        return -1, "", f"{exc.__class__.__name__}: {exc}"


def _tail(text: str, n: int = 10) -> str:
    """Return the last n non-empty lines of text as a single string."""
    lines = [line for line in (text or "").splitlines() if line.strip()]
    return "\n".join(lines[-n:]) if lines else ""


def recover_services(timeout: int) -> tuple[bool, str]:
    """Attempt to start/recover required services. Returns (ok, details).

    Runs the ZeroOne watchdog first, then the full offline-service starter,
    so even if watchdog succeeds we still ensure all revenue services
    (ComfyUI, Ollama, PasteGrab, etc.) are started.
    """
    lines = []

    if WATCHDOG.exists():
        rc, out, err = run_command([sys.executable, str(WATCHDOG), "--recover"], timeout=max(30, timeout // 2))
        lines.append(f"watchdog --recover rc={rc}")
        if out:
            lines.append(_tail(out, 5))
        if err:
            lines.append(f"stderr: {_tail(err, 3)}")

    if SERVICE_STARTER.exists():
        rc, out, err = run_command([sys.executable, str(SERVICE_STARTER), "--all"], timeout=timeout)
        lines.append(f"start_offline_services --all rc={rc}")
        if out:
            lines.append(_tail(out, 5))
        if err:
            lines.append(f"stderr: {_tail(err, 3)}")
        return rc == 0, "\n".join(lines)

    return False, "no service recovery tool found"


def run_preflight(timeout: int) -> tuple[int, str]:
    """Run preflight and return (rc, summary)."""
    rc, out, err = run_command([sys.executable, str(PREFLIGHT), "--json"], timeout=timeout)
    summary = _tail(out or err, 10) or "no output"
    return rc, summary


def run_orchestrator(run_mode: bool, timeout: int) -> tuple[int, str]:
    """Run the nightly orchestrator and return (rc, summary)."""
    cmd = [sys.executable, str(ORCHESTRATOR), "--force-window"]
    if run_mode:
        cmd.append("--run")
    rc, out, err = run_command(cmd, timeout=timeout)
    summary = _tail(out or err, 20) or "no output"
    return rc, summary


def get_last_run_summary() -> dict:
    """Return the most recent autonomous_master audit row, or empty dict."""
    if not AUDIT_LOG.exists():
        return {}
    try:
        lines = AUDIT_LOG.read_text(encoding="utf-8").strip().splitlines()
    except OSError:
        return {}
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("module") == "autonomous_master":
            return row
    return {}


def main() -> int:
    ap = argparse.ArgumentParser(description="SLEEP_TRIPLE autonomous master controller")
    ap.add_argument("--run", action="store_true", help="Allow live side-effects (requires config opt-in)")
    ap.add_argument("--recover", action="store_true", help="Only recover services, then exit")
    ap.add_argument("--status", action="store_true", help="Print last autonomous run summary")
    args = ap.parse_args()

    cfg = load_config()
    tz = ZoneInfo(cfg.get("tz", "Australia/Sydney"))
    now_local = datetime.now(tz)
    today_iso = now_local.date().isoformat()

    if is_rule_8(ROOT):
        print("REFUSED: ROOT path violates Rule #8 fence", file=sys.stderr)
        append_audit({"ts": now_local.isoformat(), "module": "autonomous_master",
                      "status": "refused", "reason": "rule8_path", "path": str(ROOT)})
        return 2

    if args.status:
        summary = get_last_run_summary()
        if not summary:
            print("[autonomous_master] no previous run found")
            return 0
        print(json.dumps(summary, indent=2, default=str))
        return 0

    am_cfg = cfg.get("autonomous_master", {})
    dry_run_default = am_cfg.get("dry_run_default", True)
    run_mode = args.run and not dry_run_default
    dry_run_forced = args.run and dry_run_default
    if dry_run_forced:
        print("[autonomous_master] WARNING: --run requested but config autonomous_master.dry_run_default=true; "
              "staying in dry-run mode. Set dry_run_default=false in sleep_config.json to go live.", file=sys.stderr)

    if args.recover:
        svc_timeout = am_cfg.get("service_recovery_timeout", 180)
        ok, details = recover_services(svc_timeout)
        print(f"[autonomous_master] service recovery: {'ok' if ok else 'failed'}")
        print(details)
        return 0 if ok else 1

    append_audit({"ts": now_local.isoformat(), "module": "autonomous_master",
                  "status": "started", "date": today_iso, "dry_run": not run_mode,
                  "run_flag": args.run, "config_dry_run_default": dry_run_default,
                  "dry_run_forced_by_config": dry_run_forced})

    # 1. Service recovery
    svc_timeout = am_cfg.get("service_recovery_timeout", 180)
    pre_timeout = am_cfg.get("preflight_timeout", 60)
    orch_timeout = am_cfg.get("orchestrator_timeout", 600)
    services_ok, services_details = recover_services(svc_timeout)
    if not services_ok:
        append_audit({"ts": now_local.isoformat(), "module": "autonomous_master",
                      "status": "failed", "reason": "service_recovery_failed",
                      "details": services_details, "date": today_iso})
        print(f"[autonomous_master] service recovery failed: {services_details}", file=sys.stderr)
        return 1

    # 2. Preflight is operational evidence, not an informational detail.
    preflight_rc, preflight_summary = run_preflight(pre_timeout)

    # 3. Run orchestrator
    orch_rc, orch_summary = run_orchestrator(run_mode, orch_timeout)

    # 4. Final audit row. A successful orchestrator with an unhealthy
    # preflight is degraded, so dashboards cannot report a false green run.
    if orch_rc not in (0, 10):
        status = "failed"
    elif orch_rc == 10 or preflight_rc != 0:
        status = "degraded"
    else:
        status = "ok"
    append_audit({"ts": now_local.isoformat(), "module": "autonomous_master",
                  "status": status, "date": today_iso, "dry_run": not run_mode,
                  "preflight_rc": preflight_rc, "preflight_summary": preflight_summary,
                  "orchestrator_rc": orch_rc, "orchestrator_summary": orch_summary,
                  "services_recovered": services_ok})

    print(f"[autonomous_master] run complete: status={status}, dry_run={not run_mode}, "
          f"preflight_rc={preflight_rc}, orchestrator_rc={orch_rc}")
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
