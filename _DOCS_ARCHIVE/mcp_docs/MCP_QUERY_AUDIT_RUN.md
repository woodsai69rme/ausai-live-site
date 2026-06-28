# MCP_QUERY_AUDIT_RUN — append-only MCP query audit emitter

✅ COMPLIANCE — this document and its companion script `MCP_QUERY_AUDIT_RUN.py` are **ADDITIVE ONLY**. They never delete, overwrite, clear, or rewrite any file. They never touch any Rule #8 folder. They never replace any prior artifact.

## 1. Overview

`MCP_QUERY_AUDIT_RUN.py` reads an MCP server stdout/stderr log (read-only) and appends one audit row per parseable query record to `MCP_QUERY_AUDIT.log`. This log is the **Phase 1 source consumed by `MCP_FEDERATION_MERGER.ps1`**, so closing this loop makes the federation merger end-to-end plumbable (Phase 1: query audit → Phase 2: federation/merger → write `MCP_FEDERATION_RESULT.jsonl`).

## 2. Closed status enum

`MCP_QUERY_STATUS_ENUM` is a closed 6-element tuple. The script silently skips any source line whose `status=` token is outside this set (it is **never** coerced):

| Status | Meaning |
| --- | --- |
| `ok` | Query succeeded |
| `rate_limited` | Query refused because of rate-limit policy |
| `refused` | Query refused for policy/permissions reason |
| `error` | Query raised an internal error |
| `skipped` | Query was skipped (e.g., feature flag off) |
| `noop` | Query was a no-op (e.g., empty result set) |

## 3. Refusal matrix

| Condition | Exit | Reason |
| --- | --- | --- |
| `--mcp-server-log` resolves inside a Rule #8 folder | 2 | Rule #8 protection |
| `--query-log-out` resolves inside a Rule #8 folder | 2 | Rule #8 protection |
| `--mcp-server-log` does not exist | 3 | Source missing |
| `--mcp-server-log` exists but is unreadable | 4 | Source unreadable |

Default invocation (`--dry-run`) reads the source to count what *would* be appended but writes nothing.

## 4. Append discipline

* Reads source via `open(args.mcp_server_log, "r", encoding="utf-8")` (read-only context manager).
* Writes destination via `open(path, "a", encoding="utf-8")` only. Never `"w"`, `"x"`, `os.truncate`, `Set-Content`, `Clear-Content`, `Remove-Item`, or `del`.
* Each parseable source line → exactly one audit row (pipe-delimited, ISO-prefixed).
* Each invocation → exactly one trailing `# run_complete` summary row stating the source tag and `accepted` / `skipped` counts.

## 5. Log row shape

```
<ISO8601 UTC> | status=<status> | tool=<tool> | query_id=<id> | duration_ms=<int> | source=<host:port>
# run_complete | source=<host:port> | accepted=<int> | skipped=<int> | dry_run=<bool>
```

## 6. First-run quickstart

```bash
# dry-run — show what would be appended given the current source
python MCP_QUERY_AUDIT_RUN.py

# dry-run against a non-default source
python MCP_QUERY_AUDIT_RUN.py --mcp-server-log /var/log/archon-mcp.out --source archon-mcp:8051

# cap rows for an audit-batch smoke test
python MCP_QUERY_AUDIT_RUN.py --dry-run --max-rows 10

# opt in to a real append
python MCP_QUERY_AUDIT_RUN.py --run --source supermemory-mcp:8052
```

## 7. Companion surface (untouched)

These artifacts existed before `MCP_QUERY_AUDIT_RUN.py` and are not modified by it:

* `MCP_FEDERATION_MERGER.ps1` — Phase 2 reader of `MCP_QUERY_AUDIT.log`
* `APPEND_ONLY_HYGIENE_RUNNER.py` — daily size/prefix hygiene check across `TRACKED_LOGS`
* `BACKUP_AUDIT_RUN.ps1`, `ENV_AUDIT_RUN.ps1` — parallel siblings (other audit emitters)
* `mcp_server.log` — read-only input, never written here
* `MCP_QUERY_AUDIT.log` — only ever appended to; never cleared

## 8. Rule #8 footer (verbatim)

This artifact and all of its companion artifacts must never read, write, enumerate, or operate on any folder matching:

```
C:\Users\karma\Documents\
C:\Users\karma\Downloads\
C:\Users\karma\Pictures\
C:\Users\karma\Videos\
C:\Users\karma\Music\
C:\Users\karma\Desktop\
C:\Users\karma\OneDrive\
C:\Users\karma\Downloads\ARCHIVE_OLD\
```

(On a non-Windows host, the same rule applies under the equivalent `~/Documents`, `~/Downloads`, etc. mapping.) Operating in any of these folders is refused with exit 2.
