#!/usr/bin/env python3
"""
_ledger_writer.py — canonical SLEEP_TRIPLE signal_emitted helper.

Single source of truth shared by opt_c_crypto_yield and opt_d_alerts.
Future Append-RevenueEvent.ps1 schema changes (param renames, new
mandatory fields) update ONE place rather than two. Importable as::

    from _ledger_writer import append_ledger_event

Signature, return contract, and PS1 argv shape are unchanged from the
private copies that lived in opt_c / opt_d. safe_id derivation strips
':' and '.' so PS1's `[string]::IsNullOrWhiteSpace($Id)` check passes.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LEDGER_APPENDER_PS1 = Path(r"C:\Users\karma\Append-RevenueEvent.ps1")
PROJECT_LOCAL_LEDGER = ROOT / "REVENUE_LEDGER.jsonl"


def append_ledger_event(
    ts: str,
    amount_usd: float,
    source: str,
    meta_obj: dict,
    dry_run: bool,
    id_suffix: str = "",
) -> bool:
    """Append a 'signal_emitted' row to REVENUE_LEDGER.jsonl via
    Append-RevenueEvent.ps1.

    Returns True on PS1 success (rc=0). On PS1 refusal (rc>0) the reason
    is logged to stderr and False is returned. PS1 script missing is
    logged and False is returned. The function never raises.

    Args:
        ts: ISO-format timestamp (used to derive the unique --id).
        amount_usd: realized USD-equivalent amount (default 0 for spot signals).
        source: --source string (must NOT be a personal folder; colons fine).
        meta_obj: dict serialized to --meta-json.
        dry_run: forward `-DryRun` to PS1 (prints what would be written, no write).
        id_suffix: appended to safe_id to disambiguate same-second emissions.

    Notes:
        - safe_id = ts.replace(":", "-").replace(".", "-") + id_suffix
          Produces only [a-zA-Z0-9._-] so PS1 IsNullOrWhiteSpace check passes.
        - -LedgerPath is the project-local path; dashboard_server.py prefers
          it over the historical $HOME absolute path.
    """
    if not LEDGER_APPENDER_PS1.exists():
        print(f"[ledger_writer] PS1 helper missing: {LEDGER_APPENDER_PS1}", file=sys.stderr)
        return False

    safe_id = ts.replace(":", "-").replace(".", "-") + (f"-{id_suffix}" if id_suffix else "")
    meta_json_str = json.dumps(meta_obj)

    args = [
        "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
        "-File", str(LEDGER_APPENDER_PS1),
        "-Event", "signal_emitted",
        "-Source", source,
        "-Id", safe_id,
        "-AmountUsd", f"{amount_usd:.2f}",
        "-MetaJson", meta_json_str,
        "-LedgerPath", str(PROJECT_LOCAL_LEDGER),
    ]
    if dry_run:
        args.append("-DryRun")

    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[ledger_writer] Ledger append refused (exit {r.returncode}): {r.stderr.strip()}",
              file=sys.stderr)
    return r.returncode == 0
