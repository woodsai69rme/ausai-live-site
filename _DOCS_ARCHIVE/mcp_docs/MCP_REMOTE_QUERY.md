# 🔌 MCP_REMOTE_QUERY.ps1 — companion explainer

> **First concrete federation executor** (`SEARCH_FEDERATION_DESIGN.md` ⇒ runtime). Reads one MCP backend entry from the registry, sends a search envelope, and appends ONE line per result to `MCP_QUERY_AUDIT.log`. **Local search is not invoked here;** this script is the REMOTE side of the federation pipeline.

---

## ✅ COMPLIANCE — this document and its companion script are ADDITIVE ONLY.

- ✔ Adds: NEW `MCP_REMOTE_QUERY.ps1` + NEW `MCP_REMOTE_QUERY.md`. Nothing modified.
- ✔ Honors: `SEARCH_FEDERATION_DESIGN.md` (read-only). Federation invariants -- local is the floor, remote is opt-in, project-scoped, SLA-bounded.
- ✔ Honors: append-only audit discipline — every invocation appends exactly one line.
- ✦ Does NOT touch Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD.
- ✦ Does NOT propose replacing `MCP_HOST_CONNECTOR.ps1` or the registry.

---

## 1. Search envelope

```
POST <endpoint>/search
Content-Type: application/json
{
  "query":       <Query>,
  "project_id":  <Project>,
  "max_results": <RemoteMaxResults>
}
```

Response (the operator wires a real fetcher; this script currently treats the response as opaque bytes):

```
HTTP/<status>
<bytes>
```

The runner enforces `--remote-timeout-ms` (default 1500) and `--remote-max-results` (default 25, capped at 100 server-side).

---

## 2. Refusal matrix

| Trigger                                             | Exit  |
| --------------------------------------------------- | ----- |
| `--registry-path` inside a Rule #8 personal folder  | 2     |
| `--audit-out` inside a Rule #8 personal folder      | 2     |
| `--registry-path` not found                         | 3     |
| `--server` not in registry                          | 3     |
| `--remote-timeout-ms < 50`                          | 4     |
| `--remote-max-results > 100`                        | 5     |
| `--project` empty                                   | 6     |
| Remote endpoint non-2xx                            | 7     |
| Unhandled internal error                            | 8     |

> On any refusal, **no line is appended** to the audit log.

---

## 3. Audit-log shape (append-only)

```
<ISO8601 UTC> | event=federation_search | server=<name> | endpoint=<url> | project=<id> | timeout_ms=<n> | max_results=<n> | result=<ok=true|ok=false | status=<code> | bytes=<n> | error=<msg>>
```

The log `open(..., "a")` only. No rotation, no truncation, no rewriting.

---

## 4. Project-scoped semantics (Phase G)

Every search envelope carries `project_id`. The runner requires `--project <id>` (Phase G mandate). Mismatched-`project_id` results from the remote backend are dropped pre-merge by the **federation merger** (a follow-on turn). This script's responsibility stops at the per-backend audit log.

---

## 5. Companion surface

| Companion artifact                  | Status                                                |
| ----------------------------------- | ----------------------------------------------------- |
| `MCP_HOST_CONNECTOR.ps1` / `.md`    | Untouched. This script is the search counterpart.     |
| `SEARCH_FEDERATION_DESIGN.md`       | Untouched.                                            |
| `~/.config/mcp/registry.json`       | Read-only source.                                     |
| `MCP_QUERY_AUDIT.log` (when live)   | Append-only target.                                   |
| `PROJECT_BRAIN_2_0/audit.log`       | Untouched. (Cross-system correlation is a follow-on.) |
| `Ultimate AI Empire` registry docs  | Untouched.                                             |

---

## 6. Never-do list

The runner **MUST NEVER**:

- DELETE or REWRITE the registry or the audit log.
- Bypass the personal-folder guard.
- Forward a `project_id` that resolves inside a Rule #8 folder.
- Send zero-timeout queries.
- Cache remote results across runs.

---

## 7. Acceptance tests

- `test_append_one_line` — happy path appends exactly one audit line.
- `test_personal_folder_registry_refused` — exit 2 on registry under Music.
- `test_personal_folder_audit_refused` — exit 2 on `--audit-out` under Downloads.
- `test_unknown_server_refused` — exit 3 on `-ServerName ghost-mcp`.
- `test_low_timeout_refused` — exit 4 on `--remote-timeout-ms 5`.
- `test_high_max_results_refused` — exit 5 on `--remote-max-results 500`.
- `test_project_missing_refused` — exit 6 on blank `--project`.
- `test_remote_endpoint_timeout` — backend stub `sleep 5s` triggers ok=false row, exit 7.
- `test_remote_endpoint_2xx` — backend `200 OK` returns ok=true, exit 0.

---

## 8. Compatibility with everything prior

| Prior artifact                          | Status                                                |
| --------------------------------------- | ----------------------------------------------------- |
| `MCP_HOST_CONNECTOR.ps1` / `.md`        | Untouched. Health-check counterpart to this query.      |
| `MCP_REGISTRY.md`                       | Untouched.                                             |
| `MCP_INSTALL_PLAN.md`                   | Untouched.                                             |
| `MCP_HOST_HEALTH.log`                   | Untouched (operated by MCP_HOST_CONNECTOR, not this). |
| `SEARCH_FEDERATION_DESIGN.md`           | Untouched. This script is its runtime.                 |
| `PROJECT_BRAIN_2_0/audit.log`           | Untouched.                                             |

> No prior surface is renamed, replaced, or erased.

---

## 9. What this runner does NOT do

- Does NOT invoke local search. Local is the floor (a follow-on script does that).
- Does NOT merge remote results with local. The merger is a follow-on.
- Does NOT drop mismatched-`project_id` rows here. The merger does.
- Does NOT cache remote results across runs (per design).

---

*Designed under the user's Golden Rules: append, never delete; preserve, never relabel; protect, never rewrite. Rule #8 personal folders (Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD) are fenced off at every layer.*
