# 🔍 SEARCH_FEDERATION_DESIGN.md — federated search architecture

> **OPT-9 follow-on.** Phase D's hybrid search operates on a single local corpus. **Federation goes one step further:** it queries the local Phase-D index AND any number of remote MCP backends **in parallel**, then merges results with project-scoped weighting. Local-first; remote-fan-out is opt-in and SLA-bounded.

---

## ✅ COMPLIANCE — this document is ADDITIVE ONLY.

- ✔ Adds: NEW `SEARCH_FEDERATION_DESIGN.md`. Nothing modified.
- ✔ Phase B personal-folder guard fully inherited.
- ✔ Phase D BM25+vector semantics preserved; federation is **a wrapper**, not a replacement.
- ✔ Phase G project scoping is enforced at the source of every result.
- ✓ Never deletes or relabels prior search docs.
- ✦ Does NOT touch Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD.

---

## 1. Problem statement

After Phase D, a single search is `BM25 + vector + rerank` against the local corpus. **But** the corpus is only one endpoint. The user has 5+ known MCP servers and growing. Federation extends a single search into a **multi-backend** query, with:

1. **Local-first semantics** — a result must always be reachable from the local index, even if all remote backends are offline. Local is the floor; remote is the ceiling.
2. **Project scoping** — Phase G's isolation invariant must hold end-to-end.
3. **SLA-bounded fan-out** — never let a slow remote backend stall the UI. Per-remote timeout, parallel fan-out, ceiling on concatenated result count.
4. **Personal-folder guard** — never index, never query, never cache any result whose source resolved inside Rule #8 folders.

---

## 2. Core invariant

```
FedSearch(q, project_id) =
     LocalPhaseD(q, project_id)
     ∥ (parallel) Fed(remote_backends, q, project_id)
     WeightedMerge(results, weights, project_id)
```

- Local search is **always** executed.
- Remote backends are **opt-in**: `--remote none` (default), known server NAMES, or `*` (all known).
- Each remote is bounded: `--remote-timeout-ms 1500` (default), `--remote-max-results 25`.
- Each result row carries `project_id`; results with mismatched `project_id` are dropped **before** merge.

---

## 3. CLI surface (purely additive)

| Flag                          | Purpose                                                          |
| ----------------------------- | ---------------------------------------------------------------- |
| `--remote <none\|name\|*>`    | which MCP backends to query (default `none`)                    |
| `--remote-timeout-ms <int>`   | per-remote timeout (default 1500)                                |
| `--remote-max-results <int>`  | per-remote result cap (default 25)                               |
| `--remote-weight <float>`     | per-remote weight in merge (default 1.0)                         |
| `--local-weight <float>`      | local result weight in merge (default 1.0)                       |
| `--max-results <int>`         | total result cap after merge (default 25)                        |
| `--fan-out <int>`             | max concurrent remote calls (default 4)                          |

> All flags are **purely additive**; none rename or replace Phase D flags.

---

## 4. Backend discovery

The federation layer reads `MCP_REGISTRY.md` / `~/.config/mcp/registry.json` (catalogue) **and** `MCP_HOST_CONNECTOR.ps1` output (`$HOME/MCP_HOST_HEALTH.log`) for freshness. A backend is considered "live" iff the most recent health-check entry is `ok=True` and ≤ 15 minutes old; otherwise it is marked "unknown" and skipped silently within the fan-out window (but the skip is logged).

> The freshness check is **read-only** of the audit log. It never modifies the log.

---

## 5. Query flow (per query)

1. **Local search** — Phase D BM25+vector+rerank, project-scoped, personal-folder guard preserved.
2. **Parallel remote fan-out** — for each live backend:
   - serialize `q` + `project_id` + `max_results` per remote
   - race against `--remote-timeout-ms`
   - on timeout: log `remote_timeout`, drop result row
   - on error: log `remote_error`, drop result row
3. **Per-backend filter** — drop any row whose `project_id` mismatches the requested one.
4. **Weighted merge** — assign `score = local_weight * local_score || remote_weight[i] * remote_score[i]`, sort, take top `--max-results`.
5. **Audit line** — append `federation_search` to `audit.log` with `local_count`, `remote_counts` (per backend), `merged_count`.

> No source files are written. The only write is the **append-only audit line**.

---

## 6. Personal-folder guard (preserved)

Whenever a chunk's `source_path` is present (it always is in local results), the result is filtered out if `source_path` resolves inside any of:

`Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD`.

For remote results, the same rule applies: `source_path` is mandatory. If absent, the result is dropped (PCI-style: trust the source, refuse the row).

The merger **never** prefers personal-folder content even when its cosine score is otherwise high.

---

## 7. Refusal matrix

| Scenario                                              | Behaviour                                                       |
| ----------------------------------------------------- | --------------------------------------------------------------- |
| `--remote *` but registry resolves to personal folder | REFUSE — never read a personal-folder registry. |
| `--remote-timeout-ms 0`                               | REFUSE — zero timeout means infinite stall risk.                |
| Local search returns 0 rows AND `--remote none`       | Return empty result set; logged to audit.                       |
| Local search returns 0 rows AND `--remote *`          | Continue with remote fan-out; merger runs.                      |
| All remotes timeout                                   | Log `remote_timeout_all`; local results only.                   |
| `project_id` mismatch in any row                      | Row removed; logged `cross_project_drop`.                       |

---

## 8. Audit log

A new structured line gets appended to `audit.log` (the same file Phase F introduced):

```
<ISO8601 UTC> | event=federation_search | project=<id> | local_count=<n> | remote_counts={"zen":<n>,"n8n":<n>,...} | merged_count=<n> | drop_reasons=[...]
```

> Append-only. No reformatting of older lines.

---

## 9. Acceptance tests

- `test_local_only_default` — `--remote none` produces the same results as Phase D for the same query.
- `test_fan_out_two_backends` — `--remote zen-mcp-server,n8n-mcp` produces local + 2 backend result sets, properly weighted.
- `test_timeout_does_not_stall` — backend stub that `sleep 5s` times out at the 1.5s default; local results still served.
- `test_project_mismatch_dropped` — backend result row with `project_id=B` against a query for `project_id=A` is dropped.
- `test_personal_folder_source_dropped` — a row whose `source_path` is in Documents is filtered out pre-merge.
- `test_zero_timeout_refused` — `--remote-timeout-ms 0` refuses immediately.
- `test_registry_personal_refused` — registry path inside Rule #8 folder causes refusal with no fan-out.

---

## 10. Compatibility matrix

| Prior surface         | Status                                                |
| --------------------- | ----------------------------------------------------- |
| Phase D hybrid search | Untouched. Federation is a wrapper.                   |
| Phase E Brain API     | Endpoint shape unchanged; new flags are absorbed silently. |
| Phase F audit log     | Format-extended (new `event=federation_search` line). |
| Phase G project scope | Untouched; enforced through every layer.              |
| MCP_REGISTRY.md       | Read-only.                                            |
| MCP_HOST_CONNECTOR.ps1| Read-only of its health log for freshness.            |

> No prior artifact is renamed, deleted, or replaced.

---

## 11. What federation does NOT do

- Does NOT add a vector store replication layer.
- Does NOT cache remote results on disk across queries (each query is fresh; persistent caching is a future enhancement).
- Does NOT skip the local index. Local is the floor.
- Does NOT authenticate against remote MCP servers. Federation sends only the search envelope (`q`, `project_id`, `max_results`); it never sends `.env` values.

---

## 12. Sequencing after this doc

A future turn may build `MCP_REMOTE_QUERY.ps1` (the actual fan-out executor) plus extend Project Brain Phase E (Brain API) to surface `--remote` in `/search`. Federation today is **a design**, not a runtime.

---

*Designed under the user's Golden Rules: append, never delete; preserve, never relabel; protect, never rewrite. Rule #8 personal folders (Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD) are fenced off at every layer.*
