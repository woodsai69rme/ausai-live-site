# 🔌 MCP_FEDERATION_MERGER.ps1 — companion explainer

> **Second-stage MCP federation merger.** Reads `MCP_QUERY_AUDIT.log` (read-only) and a local `chunks.jsonl` (read-only); drops rows whose `project_id` mismatches the operator-supplied `--project-id`; drops rows whose `source_path` resolves inside a Rule #8 personal folder (pre-merge); appends a single JSONL summary row per invocation to `MCP_FEDERATION_RESULT.jsonl`. **Default `-DryRun`**. Personal-folder guard rigid on every path.

---

## ✅ COMPLIANCE — this document and its companion script are ADDITIVE ONLY.

- ✔ Adds: NEW `MCP_FEDERATION_MERGER.ps1` + NEW `MCP_FEDERATION_MERGER.md`. Nothing modified.
- ✔ Honors: `SEARCH_FEDERATION_DESIGN.md` (read-only); `MCP_REMOTE_QUERY.ps1`, `MCP_HOST_CONNECTOR.ps1` (read-only); `PROJECT_BRAIN_2_0/chunks.jsonl` (read-only).
- ✔ Honors: every prior artifact listed in §6 untouched.
- ✦ Does NOT touch Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD.
- ✦ Does NOT propose replacing `MCP_REMOTE_QUERY.ps1` or the federation design.

---

## 1. Defaults

The merger is **`-DryRun` by default**. To actually emit a row, omit `-DryRun`.

```
powershell -ExecutionPolicy Bypass -File MCP_FEDERATION_MERGER.ps1 `
    -ProjectId default
# (dry-run; prints plan; writes nothing; exit 0)
```

```
powershell -ExecutionPolicy Bypass -File MCP_FEDERATION_MERGER.ps1 `
    -ProjectId default `
    -QueryLog MCP_QUERY_AUDIT.log `
    -ChunksPath PROJECT_BRAIN_2_0/chunks.jsonl `
    -ResultPath MCP_FEDERATION_RESULT.jsonl
# (writes one summary row to MCP_FEDERATION_RESULT.jsonl)
```

---

## 2. Closed outcome enum

`MERGE_OUTCOME_ENUM = @('kept','dropped_project_mismatch','dropped_unknown_status','dropped_unreadable','dropped_personal_source')` — five values. Each chunk-row is bucketed into exactly one of these outcomes by the merger.

| Outcome                       | Trigger                                                       |
| ----------------------------- | ------------------------------------------------------------- |
| `kept`                        | `project_id` matches AND `source_path` is non-personal         |
| `dropped_project_mismatch`    | `project_id` ≠ `--project-id`                                 |
| `dropped_unknown_status`      | observed row lacks the required fields                       |
| `dropped_unreadable`          | chunk-line didn't parse as JSON                                |
| `dropped_personal_source`     | chunk's `source_path` resolves inside a Rule #8 folder        |

> The merger **never** auto-fixes mismatched rows; it ONLY drops them with a counter increment. Operator decides recovery.

---

## 3. Refusal matrix

| Trigger                                              | Exit      |
| ---------------------------------------------------- | --------- |
| `--project-id` blank                                 | 4         |
| `--query-log` inside a Rule #8 personal folder       | 2         |
| `--chunks-path` inside a Rule #8 personal folder     | 2         |
| `--result-path` inside a Rule #8 personal folder     | 2         |
| `--query-log` not found / unreadable                 | 3         |
| `--chunks-path` not found / unreadable               | 3         |

> On any refusal, **no row is appended** to `MCP_FEDERATION_RESULT.jsonl`.

---

## 4. Append discipline (per invocation)

For each invocation, **ONE JSONL summary row** is appended:

```
<ts> | {"ts":"<ISO8601 UTC>","project_id":"<id>","kept":<n>,"dropped_project_mismatch":<n>,"dropped_unknown_status":<n>,"dropped_unreadable":<n>,"dropped_personal_source":<n>,"total_query_rows":<n>,"total_chunk_rows":<n>}
```

> Two runs produce two non-overlapping JSONL rows; strictly append-only. The result file is suitable for jq / a future aggregation runner.

---

## 5. Personal-folder guard

The merger **MUST NEVER**:

- Read or write inside Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, or `Downloads\ARCHIVE_OLD`.
- Emit a `kept` row whose chunk's `source_path` resolves inside any Rule #8 folder.
- Treat any of `--query-log` / `--chunks-path` / `--result-path` as living inside a personal folder.

---

## 6. Companion surface

| Companion artifact                                | Status                                                |
| ------------------------------------------------- | ----------------------------------------------------- |
| `SEARCH_FEDERATION_DESIGN.md`                     | Untouched.                                            |
| `MCP_HOST_CONNECTOR.ps1` / `MCP_HOST_HEALTH.log`   | Untouched.                                            |
| `MCP_REMOTE_QUERY.ps1` / `MCP_QUERY_AUDIT.log`    | Untouched. (Read-only input.)                         |
| `PROJECT_BRAIN_2_0/chunks.jsonl` (when live)      | Untouched. (Read-only input.)                        |
| `MCP_FEDERATION_RESULT.jsonl` (when live)         | Append-only output.                                   |
| `Ultimate AI Empire` family                        | Untouched.                                            |

> No prior surface is renamed, replaced, or erased.

---

## 7. Never-do list (carried forward)

The merger **MUST NEVER**:

- DELETE or REWRITE the query log.
- DELETE or REWRITE the chunks file.
- DELETE or REWRITE prior summary rows of `MCP_FEDERATION_RESULT.jsonl`.
- Emit a row whose `project_id` is empty / outside the closed enum.
- Forward a chunk whose `source_path` is in a Rule #8 folder.

---

## 8. Acceptance tests

- `test_append_only_growth` — running twice produces 2 JSONL rows in the result file, never 1.
- `test_personal_folder_query_refused` — exit 2 on query log under Music/Downloads.
- `test_personal_folder_chunks_refused` — exit 2 on chunks path under any Rule #8 folder.
- `test_personal_folder_result_refused` — exit 2 on result path under any Rule #8 folder.
- `test_missing_query_refused` — exit 3 on a non-existent query log path.
- `test_missing_chunks_refused` — exit 3 on a non-existent chunks path.
- `test_project_mismatch_drop` — chunks whose `project_id` ≠ `--project-id` increment `dropped_project_mismatch`.
- `test_personal_source_drop` — chunks whose `source_path` is personal increment `dropped_personal_source`.
- `test_dry_run_no_write` — `-DryRun` performs zero writes; result file byte-identical.

---

## 9. What this merger does NOT do

- Does NOT auto-relate rows between query-log and chunks beyond their `project_id` overlap.
- Does NOT modify Project Brain 2.0 chunks.
- Does NOT enforce semantic overlap. Project_id match is the deterministic lower bound.
- Does NOT score or re-rank.

---

*Designed under the user's Golden Rules: append, never delete; preserve, never relabel; protect, never rewrite. Rule #8 personal folders (Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD) are fenced off at every layer.*
