"""MCP_HOST_HEALTH_RUN.py — append-only MCP host-health checker.

Purpose
-------
Performs a TCP-connect probe against each entry in TRACKED_MCP_INSTANCES and
appends one health row per instance to MCP_HOST_HEALTH.log. The default instance
list mirrors the federation source-of-truth (archon-mcp, supermemory-mcp,
github-mcp) so this script and MCP_FEDERATION_MERGER.ps1 stay in agreement on
*which* MCP hosts exist.

Operator contract
-----------------
Default: --dry-run. Probes every tracked instance, prints the rows that
         *would* be appended, exits 0.
Opt-in:  --run. Performs the same probes and appends rows + a run_complete
         summary, exits 0.
Refusal: exit 2 (path inside a Rule #8 folder).

Closed HEALTH enum
------------------
MCP_HOST_HEALTH_ENUM = ("up", "down", "degraded", "skipped", "refused")
  - "up"        — TCP connect succeeded within --timeout-s.
  - "down"      — ConnectionRefusedError or other OSError during connect.
  - "degraded"  — socket.timeout (connect probe did not complete in time).
  - "skipped"   — reserved for future use (filtered out at present).
  - "refused"   — reserved for future use (filter rule violations).

Closed TRACKED_MCP_INSTANCES list
---------------------------------
TRACKED_MCP_INSTANCES = (("archon-mcp", 8051),
                         ("supermemory-mcp", 8052),
                         ("github-mcp", 8053))
Three host:port pairs, closed.

Log row shape (pipe-delimited, ISO-prefixed)
-------------------------------------------
<ISO8601 UTC> | instance=<name> | host=<host> | port=<int> | status=<enum>
# run_complete | host=<host> | up=<int> | down=<int> | degraded=<int> | total=<int> | dry_run=<bool>

✅ COMPLIANCE — this script is ADDITIVE ONLY.
   - Never deletes / overwrites / clears / truncates any file.
   - Probes TCP only — never reads, writes, or executes anything on the
     target MCP host.
   - Writes --health-log-out append-only via open(path, 'a', encoding='utf-8').
   - Never touches any folder listed in PERSONAL_FOLDERS (Rule #8).
"""

from __future__ import annotations

import argparse
import socket
import sys
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Golden Rules baked in
# ---------------------------------------------------------------------------
GOLDEN_RULES = (
    "additive_only",
    "no_delete",
    "no_overwrite",
    "no_set_content",
    "no_clear_content",
    "no_remove_item",
    "no_del",
    "no_rm",
    "personal_folders_protected",
    "append_only_log_emitters",
    "no_remote_write",
    "tcp_probe_only",
)

# ---------------------------------------------------------------------------
# Personal folders (Rule #8) — closed 8-item tuple ending in ARCHIVE_OLD
# ---------------------------------------------------------------------------
PERSONAL_FOLDERS = (
    "Documents", "Downloads", "Pictures", "Videos", "Music",
    "Desktop", "OneDrive", "ARCHIVE_OLD",
)

# ---------------------------------------------------------------------------
# Closed TRACKED_MCP_INSTANCES list (single source of truth across MCP files)
# ---------------------------------------------------------------------------
TRACKED_MCP_INSTANCES = (
    ("archon-mcp", 8051),
    ("supermemory-mcp", 8052),
    ("github-mcp", 8053),
)

# ---------------------------------------------------------------------------
# Closed health status enum
# ---------------------------------------------------------------------------
MCP_HOST_HEALTH_ENUM = ("up", "down", "degraded", "skipped", "refused")


def is_in_personal(path: str) -> bool:
    """Rule #8 guard: collapsed suffix/segment form (matches the runner family)."""
    norm = (path or "").replace("\\", "/").rstrip("/")
    if not norm:
        return False
    for pf in PERSONAL_FOLDERS:
        suffix = "/" + pf
        if norm.endswith(suffix) or (suffix + "/") in (norm + "/"):
            return True
    return False


def iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def probe(host: str, port: int, timeout_s: float) -> str:
    """TCP-connect probe. Discriminates three outcomes:

    - "up":       socket.create_connection() returned without exception.
    - "down":     ConnectionRefusedError / OSError during connect.
    - "degraded": socket.timeout (connect probe did not complete in time).
    """
    try:
        with socket.create_connection((host, port), timeout=timeout_s):
            return "up"
    except socket.timeout:
        return "degraded"
    except (ConnectionRefusedError, OSError):
        return "down"


def append_log(path: str, line: str) -> None:
    """Append-only writer. Never truncates, never rewrites."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Append-only MCP host-health checker.")
    ap.add_argument(
        "--health-log-out",
        default="MCP_HOST_HEALTH.log",
        help="append-only destination (default: MCP_HOST_HEALTH.log in cwd)",
    )
    ap.add_argument(
        "--host",
        default="127.0.0.1",
        help="loopback host to probe (default: 127.0.0.1)",
    )
    ap.add_argument(
        "--timeout-s",
        type=float,
        default=2.0,
        help="per-instance TCP-connect timeout in seconds (default: 2.0)",
    )
    ap.add_argument(
        "--instance",
        default=None,
        help=(
            "probe only one instance (must be a member of "
            "TRACKED_MCP_INSTANCES); default: probe all"
        ),
    )
    ap.add_argument(
        "--run",
        action="store_true",
        help="opt in to real append; default is dry-run",
    )
    args = ap.parse_args()

    # Validate --instance if provided
    if args.instance:
        valid_names = tuple(name for name, _ in TRACKED_MCP_INSTANCES)
        if args.instance not in valid_names:
            print(
                f"REFUSED: --instance={args.instance} is not in TRACKED_MCP_INSTANCES "
                f"(valid: {', '.join(valid_names)})",
                file=sys.stderr,
            )
            return 5

    # Rule #8 fence on destination
    if is_in_personal(args.health_log_out):
        print(
            f"REFUSED: --health-log-out={args.health_log_out} is inside a Rule #8 folder.",
            file=sys.stderr,
        )
        return 2

    plans: list[str] = []
    up = down = degraded = 0
    for name, port in TRACKED_MCP_INSTANCES:
        if args.instance and name != args.instance:
            continue
        status = probe(args.host, port, args.timeout_s)
        if status == "up":
            up += 1
        elif status == "down":
            down += 1
        elif status == "degraded":
            degraded += 1
        line = (
            f"{iso_now()} | instance={name} | host={args.host} | "
            f"port={port} | status={status}"
        )
        plans.append(line)

    summary = (
        f"# run_complete | host={args.host} | up={up} | down={down} | "
        f"degraded={degraded} | total={len(plans)} | dry_run={str(not args.run).lower()}"
    )

    if not args.run:
        print("(dry-run: rows that WOULD be appended to MCP_HOST_HEALTH.log)")
        for p in plans:
            print(f"  {p}")
        print(f"  {summary}")
        return 0

    for p in plans:
        append_log(args.health_log_out, p)
    append_log(args.health_log_out, summary)
    print(
        f"appended {len(plans)} rows + 1 summary to {args.health_log_out}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
