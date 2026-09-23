# 🧾 AGENT_REGISTRY_AUDIT_RUN.ps1 — companion explainer

> **First concrete read-only audit runner** for the eight dimensions in `AGENT_REGISTRY_AUDIT.md`. Emits an append-only section to `AGENT_REGISTRY_AUDIT_REPORT.md` per run. **Never modifies** `AGENT_REGISTRY.md`.

---

## ✅ COMPLIANCE — this document and its companion script are ADDITIVE ONLY.

- ✔ Adds: NEW `AGENT_REGISTRY_AUDIT_RUN.ps1` + NEW `AGENT_REGISTRY_AUDIT_RUN.md`. Nothing modified.
- ✔ Honors: `AGENT_REGISTRY_AUDIT.md` (read-only). The eight audit dimensions are unchanged.
- ✔ Honors: `AI_AGENT_INVENTORY.md` (read-only). Inventory roll-ups remain untouched.
- ✦ Does NOT touch Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD.
- ✦ Does NOT propose pruning, archiving-as-cleanup, or relabelling any of the 2,793 agents.

---

## 1. Eight audit dimensions (operational form)

| # | Dimension                          | Status result        |
| - | ---------------------------------- | -------------------- |
| 1 | cardinality                        | PASS/WARN            |
| 2 | id_uniqueness                      | PASS/WARN            |
| 3 | iso_added_at                       | PASS/WARN            |
| 4 | source_present                     | PASS/WARN            |
| 5 | personal_folder_observance         | INFO                 |
| 6 | schema_drift                       | PASS/WARN            |
| 7 | append_only_hygiene                | INFO                 |
| 8 | cluster_coverage                   | INFO                 |

> Each run emits a `## Run <run-id> @ <ISO8601>` section with a one-line summary per dimension.

---

## 2. Refusal matrix

| Trigger                                                    | Exit      |
| ---------------------------------------------------------- | --------- |
| Registry path inside a Rule #8 personal folder             | 2         |
| Report path inside a Rule #8 personal folder               | 2         |
| Registry file not found                                    | 3         |
| Unhandled internal error (e.g. Get-Content fails)          | 4         |

> On any refusal, **no section is appended** to the audit report.

---

## 3. Output shape (append-only)

The audit report grows by one section per run:

```
## Run 2026-03-09T... @ <ts>
- **cardinality**: {"dimension":"cardinality","count":2800,"status":"PASS"}
- **id_uniqueness**: {"dimension":"id_uniqueness","dupes_estimate":0,"status":"PASS"}
... etc
```

The report file is opened with `Add-Content` (`"a"`-mode) only. No rewrite, no truncate.

---

## 4. The 2,793-agent headroom

The cardinality check accepts anything in the **[2700, 2900]** band as PASS, otherwise WARN. Drift outside the band is non-fatal: the operator decides whether to grow inventory or run the audit finer-grained.

> **No row is removed** when cardinality drifts. The audit observes; it does not enforce.

---

## 5. Read-only discipline

The runner **MUST NEVER**:

- Modify `AGENT_REGISTRY.md` (Set-Content / Clear-Content is forbidden).
- Truncate the audit report.
- Reorder or rewrite prior audit sections.
- Write into Rule #8 personal folders.

---

## 6. Acceptance tests

- `test_append_only_growth` — running twice produces two append-only sections in the report.
- `test_personal_folder_registry_refused` — registry path inside Music refuses with exit 2.
- `test_personal_folder_report_refused` — report path inside Downloads refuses with exit 2.
- `test_missing_registry_refused` — registry not found refuses with exit 3.
- `test_eight_dimensions_all_present` — every run's section lists the eight dimension labels.
- `test_pass_warn_only_states` — no audit row contains "FAIL" (only PASS / WARN / INFO).

---

## 7. Compatibility with everything prior

| Prior artifact                | Status                                                |
| ----------------------------- | ----------------------------------------------------- |
| `AGENT_REGISTRY.md`           | Untouched. Strictly read-only.                         |
| `AGENT_REGISTRY_AUDIT.md`     | Untouched. Source-of-truth for the eight dimensions.  |
| `AI_AGENT_INVENTORY.md`       | Untouched. Cross-link target.                         |
| `SKILLS_MATRIX.md`            | Untouched.                                            |
| `Project Brain 2.0` family    | Untouched.                                            |

> No prior surface is renamed, replaced, or erased.

---

## 8. What this runner does NOT do

- Does NOT auto-correct. The audit reports; the operator decides.
- Does NOT prune. The registry is permanent.
- Does NOT force a schema on the registry.
- Does NOT tie cluster names to canonical spellings.

---

*Designed under the user's Golden Rules: append, never delete; preserve, never relabel; protect, never rewrite. Rule #8 personal folders (Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD) are fenced off at every layer.*
