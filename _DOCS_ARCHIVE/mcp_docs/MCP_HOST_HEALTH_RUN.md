# MCP_HOST_HEALTH_RUN — append-only MCP host-health checker

✅ COMPLIANCE — this document and its companion script `MCP_HOST_HEALTH_RUN.py` are **ADDITIVE ONLY**. They never delete, overwrite, clear, or rewrite any file. They never touch any Rule #8 folder. They never replace any prior artifact. The TCP-connect probe is **read-only** — it never writes to or executes anything on the target MCP host.

## 1. Overview

`MCP_HOST_HEALTH_RUN.py` performs a TCP-connect probe against each entry in `TRACKED_MCP_INSTANCES` and appends one health row per instance to `MCP_HOST_HEALTH.log`. The default instance list matches the federation source-of-truth (`MCP_FEDERATION_MERGER.ps1` Phase 2 reader), so both artifacts stay in agreement on *which* MCP hosts exist on this loopback.

## 2. Closed health enum

`MCP_HOST_HEALTH_ENUM` is a closed 5-element tuple:

| Status | Meaning |
| --- | --- |
| `up` | TCP connect succeeded within `--timeout-s`. |
| `down` | `ConnectionRefusedError` or other `OSError` during connect. |
| `degraded` | `socket.timeout` (connect probe did not complete in time). |
| `skipped` | reserved (filtered before probe; not emitted by the live probe path). |
| `refused` | reserved (audit-rule violators; not emitted by the live probe path). |

The probe path only emits `up`, `down`, or `degraded`. The other two values are reserved for future audit-rule filter surfaces.

## 3. Closed TRACKED_MCP_INSTANCES list

`TRACKED_MCP_INSTANCES` is a single source of truth across all MCP artifacts:

| Instance | Port |
| --- | --- |
| `archon-mcp` | 8051 |
| `supermemory-mcp` | 8052 |
| `github-mcp` | 8053 |

Modifying this list is a *behavior* change (a new MCP host will appear in `MCP_HOST_HEALTH.log` rows for the first time). To extend: append a new tuple to the constant in the runner, never reorder or remove. To probe just one instance for a smoke test: `--instance archon-mcp`.

## 4. Refusal matrix

| Condition | Exit | Reason |
| --- | --- | --- |
| `--health-log-out` resolves inside a Rule #8 folder | 2 | Rule #8 protection |
| `--instance=<name>` is supplied but not in `TRACKED_MCP_INSTANCES` | 5 | Closed-list protection |

The script never exits non-zero from a `down` or `degraded` probe — that is the **observed** state and is exactly the kind of row the destination log is designed to capture. Refusal exits are reserved for *configuration* and *protection* failures.

## 5. Append discipline

* Reads TCP only via `socket.create_connection((host, port), timeout=...)` (read-only OS-level connection attempt). Never sends data, never invokes the target's protocol.
* Writes destination via `open(path, "a", encoding="utf-8")` only. Never `"w"`, `"x"`, `os.truncate`, `Set-Content`, `Clear-Content`, `Remove-Item`, or `del`.
* Per invocation: one row per probed instance + one trailing `# run_complete` summary row with aggregate up/down/degraded counts.

## 6. Log row shape

```
<ISO8601 UTC> | instance=<name> | host=<host> | port=<int> | status=<enum>
# run_complete | host=<host> | up=<int> | down=<int> | degraded=<int> | total=<int> | dry_run=<bool>
```

## 7. First-run quickstart

```bash
# dry-run — probe all three instances, show what would be appended
python MCP_HOST_HEALTH_RUN.py

# dry-run against a single instance
python MCP_HOST_HEALTH_RUN.py --instance supermemory-mcp --timeout-s 5

# opt in to a real append (writes MCP_HOST_HEALTH.log)
python MCP_HOST_HEALTH_RUN.py --run

# opt in with a tighter timeout
python MCP_HOST_HEALTH_RUN.py --run --timeout-s 1.0
```

## 8. Companion surface (untouched)

These artifacts existed before `MCP_HOST_HEALTH_RUN.py` and are not modified by it:

* `MCP_FEDERATION_MERGER.ps1` — Phase 2 reader that consumes `MCP_QUERY_AUDIT.log` and `chunks.jsonl`; shares `TRACKED_MCP_INSTANCES` (project_id-keyed) but does not depend on `MCP_HOST_HEALTH.log`.
* `MCP_QUERY_AUDIT_RUN.py` — Phase 1 query audit emitter.
* `APPEND_ONLY_HYGIENE_RUNNER.py` — daily size/prefix hygiene check, including `MCP_HOST_HEALTH.log`.
* `MCP_HOST_HEALTH.log` — only ever appended to; never cleared.

## 9. Rule #8 footer (verbatim)

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
