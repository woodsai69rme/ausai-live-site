"""MCP_QUERY_AUDIT_RUN.py — append-only MCP query audit emitter.

Purpose
-------
Reads an MCP server stdout/stderr log (read-only) and appends one audit row per
parseable query record to MCP_QUERY_AUDIT.log. The audit log is the Phase 1
source consumed by MCP_FEDERATION_MERGER.ps1, so closing this loop makes the
federation merger end-to-end plumbable.

Operator contract
-----------------
Default: --dry-run. Prints the rows that *would* be appended and exits 0.
Opt-in:  --run. Reads source, appends rows + run_complete summary, exits 0.
Refusal: exit 2 (path inside a Rule #8 folder), exit 3 (source missing),
         exit 4 (source unreadable).

Closed status enum
------------------
MCP_QUERY_STATUS_ENUM = ("ok", "rate_limited", "refused", "error", "skipped", "noop")
Any token outside this set is silently skipped (not surfaced as a row).

Log row shape (pipe-delimited, ISO-prefixed)
-------------------------------------------
<ISO8601 UTC> | status=<status> | tool=<tool> | query_id=<id> | duration_ms=<int> | source=<host:port>
...followed by ONE run_complete row per invocation:
# run_complete | source=<host:port> | accepted=<int> | skipped=<int> | dry_run=<bool>

✅ COMPLIANCE — this script is ADDITIVE ONLY.
   - Never deletes / overwrites / clears any file.
   - Reads --mcp-server-log read-only via open(..., 'r', encoding='utf-8').
   - Writes --query-log-out append-only via open(path, 'a', encoding='utf-8').
   - Never touches any folder listed in PERSONAL_FOLDERS (Rule #8).
   - Never replaces any prior artifact.
"""

from __future__ import annotations

import argparse
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
)

# ---------------------------------------------------------------------------
# Personal folders (Rule #8) — closed 8-item tuple ending in ARCHIVE_OLD
# ---------------------------------------------------------------------------
PERSONAL_FOLDERS = (
    "Documents", "Downloads", "Pictures", "Videos", "Music",
    "Desktop", "OneDrive", "ARCHIVE_OLD",
)

# ---------------------------------------------------------------------------
# Closed status enum (append-only emitter never writes a status outside this set)
# ---------------------------------------------------------------------------
MCP_QUERY_STATUS_ENUM = ("ok", "rate_limited", "refused", "error", "skipped", "noop")

REQUIRED_FIELDS = ("tool", "query_id", "duration_ms", "status")


def is_in_personal(path: str) -> bool:
    """Rule #8 guard: collapsed suffix/segment form.

    Mirrors the pattern used in youtube_transcript_harvest.py and the Footclan
    runners so a path matches if it equals /<pf> , is a subdirectory of /<pf>/,
    or contains /<pf>/ as a segment.
    """
    norm = (path or "").replace("\\", "/").rstrip("/")
    if not norm:
        return False
    for pf in PERSONAL_FOLDERS:
        suffix = "/" + pf
        if norm.endswith(suffix) or (suffix + "/") in (norm + "/"):
            return True
    return False


def iso_now() -> str:
    """Current UTC time formatted as ISO-8601 (suffix Z, no fractional seconds)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_mcp_server_line(line: str) -> dict | None:
    """Extract tool / query_id / duration_ms / status tokens from an MCP server log line.

    Returns None when any required field is missing OR status is outside the
    closed MCP_QUERY_STATUS_ENUM (silent-skip, never coerced).
    """
    if not line:
        return None
    fields: dict[str, str] = {}
    for tok in line.split():
        if "=" not in tok:
            continue
        k, v = tok.split("=", 1)
        fields[k.strip()] = v.strip()
    if not all(req in fields for req in REQUIRED_FIELDS):
        return None
    if fields["status"] not in MCP_QUERY_STATUS_ENUM:
        return None
    try:
        fields["duration_ms"] = int(fields["duration_ms"])
    except ValueError:
        return None
    return fields


def append_log(path: str, line: str) -> None:
    """Append-only writer. Never truncates, never rewrites."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Append-only MCP query audit emitter.")
    ap.add_argument(
        "--mcp-server-log",
        default="mcp_server.log",
        help="read-only source path (default: mcp_server.log in cwd)",
    )
    ap.add_argument(
        "--query-log-out",
        default="MCP_QUERY_AUDIT.log",
        help="append-only destination (default: MCP_QUERY_AUDIT.log in cwd)",
    )
    ap.add_argument(
        "--source",
        default="archon-mcp:8051",
        help="host:port tag written into every audit row (default: archon-mcp:8051)",
    )
    ap.add_argument(
        "--max-rows",
        type=int,
        default=0,
        help="cap on accepted rows per invocation (0 = no cap, default)",
    )
    ap.add_argument(
        "--run",
        action="store_true",
        help="opt in to real append; default is dry-run",
    )
    args = ap.parse_args()

    # Rule #8 fence on both source and destination
    for label, p in (("--mcp-server-log", args.mcp_server_log),
                     ("--query-log-out", args.query_log_out)):
        if is_in_personal(p):
            print(f"REFUSED: {label}={p} is inside a Rule #8 folder.", file=sys.stderr)
            return 2

    # Read-only source load
    try:
        with open(args.mcp_server_log, "r", encoding="utf-8") as f:
            server_lines = f.readlines()
    except FileNotFoundError:
        print(f"REFUSED: --mcp-server-log not found: {args.mcp_server_log}", file=sys.stderr)
        return 3
    except OSError as e:
        print(f"REFUSED: --mcp-server-log unreadable: {e}", file=sys.stderr)
        return 4

    rows_planned: list[str] = []
    accepted = 0
    skipped = 0
    for line in server_lines:
        f = parse_mcp_server_line(line)
        if f is None:
            skipped += 1
            continue
        if args.max_rows and accepted >= args.max_rows:
            skipped += 1
            continue
        out = (
            f"{iso_now()} | status={f['status']} | tool={f['tool']} | "
            f"query_id={f['query_id']} | duration_ms={f['duration_ms']} | "
            f"source={args.source}"
        )
        rows_planned.append(out)
        accepted += 1

    summary = (
        f"# run_complete | source={args.source} | accepted={accepted} | "
        f"skipped={skipped} | dry_run={str(not args.run).lower()}"
    )

    if not args.run:
        print("(dry-run: rows that WOULD be appended to MCP_QUERY_AUDIT.log)")
        print(f"  accepted={accepted}  skipped={skipped}  source={args.source}")
        for r in rows_planned[:5]:
            print(f"  {r}")
        if len(rows_planned) > 5:
            print(f"  ... +{len(rows_planned) - 5} more")
        print(f"  {summary}")
        return 0

    for r in rows_planned:
        append_log(args.query_log_out, r)
    append_log(args.query_log_out, summary)
    print(
        f"appended {accepted} rows + 1 summary to "
        f"{args.query_log_out}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
