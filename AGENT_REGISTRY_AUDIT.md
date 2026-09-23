# 🧾 AGENT_REGISTRY_AUDIT.md  *(OPT-1.4 follow-on — audit criteria)*

> **A companion to `AGENT_REGISTRY.md`.** That file is the registry itself; this doc enumerates the **audit dimensions** an operator runs against it, the **pass/fail criteria**, and the **read-only** nature of every step. Pure scaffolding. **No agent is deleted, archived-as-cleanup, or relabelled obsolete by this artifact.**

---

## ✅ COMPLIANCE — this document is ADDITIVE ONLY.

- ✔ Adds: NEW `AGENT_REGISTRY_AUDIT.md`. No prior file modified.
- ✔ Honors: `AGENT_REGISTRY.md` (read-only source).
- ✔ Honors: `AI_AGENT_INVENTORY.md` (read-only summary, companion).
- ✦ Does NOT touch Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD.
- ✦ Does NOT recommend removing, archiving-as-cleanup, or relabelling any of the 2,793 agents.

---

## 1. Audit dimensions

| Dimension                                                  | Source artifact              | What is checked                         |
| ---------------------------------------------------------- | --------------------------- | --------------------------------------- |
| Cardinality (count)                                         | `AGENT_REGISTRY.md`         | The number of rows matches headline.    |
| Schema drift                                               | `AGENT_REGISTRY.md`         | Every row has the same `field_count` baseline. |
| Idempotency of ids                                          | `AGENT_REGISTRY.md`         | Each id appears exactly once.           |
| Source URLs / fingerprints                                  | `AGENT_REGISTRY.md`         | Each row carries a verifiable source.   |
| Cross-link with `AI_AGENT_INVENTORY.md` cardinality        | both                        | Inventory's count matches registry's.   |
| Append-only hygiene                                         | `AGENT_REGISTRY.md`         | No row was rewritten post-dating; lines are monotonic in `added_at`. |
| Personal-folder observance                                  | every agent row             | None has `source_path` in Rule #8 folder. |
| Cluster coverage                                            | `AI_AGENT_INVENTORY.md`     | Each agent falls into a cluster.         |

> Every dimension is **read-only**. The audit never rewrites the registry.

---

## 2. Cadence (operator-decided)

- **Weekly** — cardinality + idempotency + cluster coverage.
- **Monthly** — full sweep of all eight dimensions.
- **On-change** — any operator append affecting ≥ 10 rows triggers an immediate cardinality re-check.

> Cadence is advisory; no scheduled job is bundled here.

---

## 3. Refusal matrix

| Scenario                                                | Behaviour                                                  |
| ------------------------------------------------------- | ---------------------------------------------------------- |
| Audit script attempts to overwrite a row                | REFUSED — registry is append-only; pass/fail is reported, not enforced. |
| Audit script attempts to delete a row flagged stale     | REFUSED — staleness is descriptive; the registry is permanent. |
| Bulk rewrite to "normalize" field ordering              | REFUSED — schema drift is descriptive; the operator adjusts the doc, not the registry. |
| Personal-folder source path flagged row deletion        | REFUSED — flagged rows are kept; their flag is in the audit log. |
| Cross-link cardinality drift not investigated            | REFUSED-by-design — drift is reportable; remediation is operator-decided. |

---

## 4. Acceptance tests

- `test_count_matches_headline` — line count of registry markdown ≈ 2,793 ± drift.
- `test_id_unique` — every id appears exactly once.
- `test_iso_added_at` — every row's `added_at` parses as ISO8601.
- `test_source_present` — every row's `source` is non-empty.
- `test_personal_folder_no_poll` — none of the rows' source paths resolve into Rule #8 folders.
- `test_append_only_hygiene` — running the audit twice produces identical reports; the registry is unchanged.

---

## 5. Compatibility with everything prior

| Prior artifact                          | Status                                                |
| --------------------------------------- | ----------------------------------------------------- |
| `AGENT_REGISTRY.md`                     | Untouched. Read-only by this audit.                    |
| `AGENT_REGISTRY_AUDIT.md` (this doc)    | New.                                                   |
| `AI_AGENT_INVENTORY.md`                 | Untouched. Read-only summary, fed into audit.           |
| `SKILLS_MATRIX.md`                      | Untouched; orthogonal dimension.                       |
| `Project Brain 2.0` ingest family       | Untouched.                                              |

> Every prior surface preserved.

---

## 6. What this audit does NOT do

- Does NOT modify the registry.
- Does NOT enforce (no automated corrections).
- Does NOT replace any prior audit doc.
- Does NOT introduce a relational database.

---

## 7. Sequencing after this doc

- A **read-only audit runner** (`AGENT_REGISTRY_AUDIT_RUN.ps1` or `.py`) that emits `AGENT_REGISTRY_AUDIT_REPORT.md` with pass/fail rows.
- A **read-only dashboard** that aggregates multiple audit reports over time.

> Out of scope here; future additive turns.

---

*Designed under the user's Golden Rules: append, never delete; preserve, never relabel; protect, never rewrite. Rule #8 personal folders (Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD) are fenced off at every layer.*

---

## 🔗 Reference Docs (NEW 2026-07-09)

| Topic | Doc |
|---|---|
| YouTube + transcript + ComfyUI video ecosystem | `YOUTUBE_GITHUB_DEEP_RESEARCH_2026.md` |
| Laptop → display + peripherals | `HARDWARE_SHOPPING_LIST_2026.md` |
| GPU-accelerated remote desktop install | `SUNSHINE_MOONLIGHT_SETUP.md` |
| Curated GitHub `awesome-*` lists for YouTube | `AWESOME_YOUTUBE_REPOS_2026.md` |
| Single-page start-here index | `REFERENCE_DOCS_INDEX.md` |
| One-page daily digest | `DAILY_REFERENCE_DIGEST_2026-07-09.md` |
