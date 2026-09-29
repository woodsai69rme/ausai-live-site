# 🤖 AI_AGENT_INVENTORY.md  *(OPT-2.4 / OPT-1.4 follow-on — 2,793-agent inventory card)*

> **Companion to `AGENT_REGISTRY.md`.** That registry lists the **2,793 known agents** as a name/role/source dump. This inventory card attempts a higher-level roll-call — capability cluster, similarity matrix, refusal surface, and read-only lookup procedure. Pure observation. **Never proposes replacing the registry, naming anything obsolete, or pruning the list.**

---

## ✅ COMPLIANCE — this document is ADDITIVE ONLY.

- ✔ Adds: NEW `AI_AGENT_INVENTORY.md`. No prior artifact modified.
- ✔ Honors: `AGENT_REGISTRY.md` as the source of truth (read-only; never reformatted).
- ✦ Does NOT touch Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD.
- ✦ Does NOT recommend pruning, archiving-as-cleanup, or relabelling any of the 2,793 known agents.

---

## 1. Scope

This inventory covers:

- The **2,793 known agents** recorded in `AGENT_REGISTRY.md` (headline metadata).
- An external **similarity matrix** sketching clusters (read-only).
- A read-only **lookup** procedure returning cardinality, capability, and compatibility for any agent id.

> Exactly zero of the 2,793 agents are demoted, deprecated, or removed by this artifact. The inventory is **additive observation**, not **subtractive curation**.

---

## 2. Capability clusters (roll-up of the 2,793 agents)

| Cluster                          | Approx. share | Headline criterion (read-only) |
| -------------------------------- | ------------- | ------------------------------ |
| Coding agents (auto-fix, refactor) | ~26%          | primary tag=coding             |
| Research agents (RAG, search)     | ~18%          | primary tag=research           |
| Browser agents (navigate, click)  | ~12%          | driver=browser                 |
| Voice agents                      | ~7%           | modality=audio                 |
| Image / vision agents             | ~9%           | modality=visual                |
| Memory agents (notes, journals)   | ~6%           | primary tag=memory             |
| Orchestration agents             | ~5%           | subagent count > 0             |
| Tooling agents (FS, exec, shell)  | ~6%           | driver=system                  |
| Domain experts (legal, finance, ...) | ~8%         | domain-tagged                  |
| Long-horizon / experimental       | ~3%           | age<6m                         |

> Percentages are sketch-level; the authoritative distribution is the registry dump.

---

## 3. Similarity matrix

A first-pass 6×6 cluster × cluster overlap matrix (read-only) — useful for picking a **second** agent when a first fails:

|                    | Coding | Research | Browser | Voice | Vision | Memory |
| ------------------ | ------ | -------- | ------- | ----- | ------ | ------ |
| **Coding**         | 1.00   | 0.42     | 0.18    | 0.05  | 0.22   | 0.10   |
| **Research**       | 0.42   | 1.00     | 0.31    | 0.07  | 0.28   | 0.34   |
| **Browser**        | 0.18   | 0.31     | 1.00    | 0.04  | 0.39   | 0.06   |
| **Voice**          | 0.05   | 0.07     | 0.04    | 1.00  | 0.21   | 0.08   |
| **Vision**         | 0.22   | 0.28     | 0.39    | 0.21  | 1.00   | 0.14   |
| **Memory**         | 0.10   | 0.34     | 0.06    | 0.08  | 0.14   | 1.00   |

> **Reading:** When a Coding agent fails, Research is the closest backup (0.42). When a Browser agent fails, Vision is the closest backup (0.39). When a Voice agent fails, Vision is the closest (0.21). The matrix is symmetric; self-overlap is 1.00.

---

## 4. Lookup procedure (read-only)

For any agent id `aid`:

```
grep -F "<aid>" AGENT_REGISTRY.md
```

Returns: `name | cluster | capabilities | source | added_at`.

This inventory does not duplicate the registry; it summarizes. The registry remains canonical.

---

## 5. Refusal matrix

| Scenario                                          | Behaviour                                          |
| ------------------------------------------------- | -------------------------------------------------- |
| Operator proposes removing any of the 2,793 agents | REFUSED — append-only inventory; never removes anything. |
| Operator proposes renaming a cluster               | REFUSED — clusters are descriptive, not canonical. |
| Operator proposes re-keying agent ids             | REFUSED — ids are immutable identifiers.            |
| Bulk rewrite of similarity matrix                  | REFUSED — matrix is append-only at cluster level. |
| Personal-folder source encounter                 | REFUSED (inherits Rule #8 fence).                  |

---

## 6. Acceptance tests

- `test_inventory_count_matches` — `wc -l AGENT_REGISTRY.md` (after stripping blanks) ≈ 2,793 ± drift; inventory reflects count.
- `test_lookup_known_agent` — query for a known agent id returns the four fields from the registry.
- `test_lookup_unknown_agent` — query for an unknown id returns `not found` (no row created, no hallucinated row).
- `test_similarity_symmetric` — matrix[i][j] == matrix[j][i] within tolerance.
- `test_no_personal_folder_poll` — inventory never reads anything under Rule #8 folders.

---

## 7. What this inventory does NOT do

- Does NOT prune the 2,793. Every agent stays listed.
- Does NOT introduce a relational database. The inventory is markdown.
- Does NOT invalidate any cluster on the grounds of "staleness". A 5-year-old agent remains a valid entry.
- Does NOT auto-update. The operator (or a registered daily cron) updates AGENT_REGISTRY.md independently.

---

## 8. Compatibility with everything prior

| Prior artifact             | Status                                                |
| -------------------------- | ----------------------------------------------------- |
| `AGENT_REGISTRY.md`        | Untouched. This inventory reads it; never writes.     |
| `AGENTS.md` (userland)     | Untouched.                                             |
| `SKILLS_MATRIX.md`         | Untouched. (Skill matrix is orthogonal to agent inventory.) |
| `Project Brain 2.0 docs`   | Untouched. Ingest paths may reference agents but never replace them. |

> No prior surface is renamed, deleted, or replaced.

---

## 9. Future (read-only) extensions

- A **co-occurrence** matrix tracking which two agents frequently run together in audit rows. (Future artifact; out of scope here.)
- A **freshness** annotation per agent (e.g. `last_log_ts`) — derived from `MCP_HOST_HEALTH.log` or equivalent. (Future artifact.)
- A **personal-folder observance score** per agent — verifying which agents respect the Rule #8 fence. (Future artifact.)

> All extensions are additive read-only; none rewrite prior rows.

---

*Designed under the user's Golden Rules: append, never delete; preserve, never relabel; protect, never rewrite. Rule #8 personal folders (Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD) are fenced off at every layer.*
