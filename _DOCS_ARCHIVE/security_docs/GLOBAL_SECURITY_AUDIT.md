# 🛡️ GLOBAL_SECURITY_AUDIT.md  *(OPT-7.6 — compliance monitoring scaffolding)*

> **A read-only doc.** Catalogues the audit surfaces already in operation across the system, prescribes the dimensions an audit examines, and provides a hand-off onto `GITLEAKS_REPORT.md`, `BACKUP_AUDIT.log`, `API_KEY_AUDIT.log`, `ENV_AUDIT.log`, `MCP_HOST_HEALTH.log`, and `audit.log` from Project Brain. Pure observation. **No tool, registry, log, or dashboard is altered, replaced, or relabelled by this artifact.**

---

## ✅ COMPLIANCE — this document is ADDITIVE ONLY.

- ✔ Adds: NEW `GLOBAL_SECURITY_AUDIT.md`. No prior file modified.
- ✔ Honors: every audit artifact named below is maintained as-is.
- ✦ Does NOT touch Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD.
- ✦ Does NOT recommend destroying, archiving-as-cleanup, or relabelling any audit log, secret scanner, key manager, or backup pipeline.

---

## 1. Audit dimensions

| Dimension                           | Surface (read-only)                                |
| ----------------------------------- | -------------------------------------------------- |
| Secret leakage                      | `GITLEAKS_REPORT.md`                                |
| Backup integrity                    | `BACKUP_INTEGRITY_REPORT.md`, `BACKUP_INTEGRITY_MANIFEST.csv`, `BACKUP_AUDIT.log` |
| API key rotation hygiene            | `API_KEY_AUDIT.log`                                 |
| Environment file discovery          | `ENV_AUDIT.log`                                      |
| MCP-server reachability             | `MCP_HOST_HEALTH.log`                                |
| Project Brain ingest audit          | `PROJECT_BRAIN_2_0/audit.log` (per project)        |
| Personal-folder observance          | Refusal matrix across every script                  |
| Append-only hygiene                 | Diff any audit log; expect strict monotonic growth |
| Operator incident trail             | `incident_<ts>.json` (only when incidents occur)   |

> This scaffolding observes each surface; it does not change any of them.

---

## 2. Cadence recommendations (operator-decided)

| Dimension              | Cadence     | Rationale                              |
| ---------------------- | ----------- | -------------------------------------- |
| Secret leakage         | weekly      | small surface; big swing-detectability |
| Backup integrity       | weekly      | rotation cycle of source repos         |
| API key rotation       | monthly     | matches typical cyclic rotation        |
| Environment file discovery | monthly  | rare to change; quick scan suffices    |
| MCP-server reachability | per-burst  | tied to operator workflow              |
| Project Brain ingest   | per-run     | matches `--watch` cadence               |
| Personal-folder observance | per-script-run | embedded in each script's refusal-trail |
| Append-only hygiene    | monthly     | ensures no audit log was truncated     |
| Operator incident      | on-event    | only fires when triggered              |

> All cadences are **read-only** observations; no audit framework runs scheduled writes.

---

## 3. Audit-trail discipline

Three rules apply across **every** audit surface named above:

1. **Append-only.** Audit lines are committed in the order they're generated. There is no re-order, re-format, or in-place edit.
2. **Time-prefixed.** Every audit line begins with `<ISO8601 UTC>` so out-of-order or rollback detection is easy.
3. **Refusal-logged.** Every refusal is logged with a distinct `event=...` tag. No refusal is silent.

> The scaffolding does not enforce these rules — it observes whether they hold. New artifacts that violate any of the three must be flagged in a future revision.

---

## 4. Refusal matrix (for any audit follow-up)

| Scenario                                                  | Behaviour                                       |
| --------------------------------------------------------- | ----------------------------------------------- |
| Audit framework rewrites an audit log via Set-Content     | REFUSED — append-only invariant violated.       |
| Audit framework deletes an "old" audit line              | REFUSED — the line is historical record.        |
| Audit framework writes inside a Rule #8 personal folder   | REFUSED — Personal-folder fence violated.        |
| Audit framework proposes renaming an audit log            | REFUSED — names are stable identifiers.         |
| Bulk edit of an audit-summary doc (`GITLEAKS_REPORT.md`)  | REFUSED — append-only report; revisit via new generation. |

---

## 5. Incident response (read-only scaffolding)

When a single dimension fires an incident:

- The originating audit line becomes the incident anchor.
- `incident_<ts>.json` is **created** (additive) with: `origin_log`, `ts`, `event`, `observed_value`, `expected_value`, `recommended_response`.
- Operator decides on response. The framework does **not** auto-act.

> Every action is operator-confirmed; the audit scaffolding is observational by design.

---

## 6. Acceptance tests

- `test_secrets_scan_runs` — weekly gitleaks scan produces `GITLEAKS_REPORT.md` with zero hits.
- `test_backup_audit_minimum` — `BACKUP_AUDIT.log` gains ≥ 1 line per run; never shrinks.
- `test_api_key_audit_refuses_deleted` — a `Remove-Item` on a registry row leaves a `rotation_refused_delete` line in `API_KEY_AUDIT.log`.
- `test_env_audit_personal_folder_skip` — `ENV_AUDIT.log` shows `SKIPPED:` lines for any `.env*` residing inside Rule #8 folders.
- `test_mcp_health_refuses_personal_registry` — `MCP_HOST_HEALTH.log` shows `REFUSED:` when registry is in a personal folder.
- `test_brain_audit_offset_persistence` — `audit.log` shows the offset file remains byte-identical across two consecutive runs.

---

## 7. Compatibility with everything prior

| Prior artifact                                | Status                                                |
| --------------------------------------------- | ----------------------------------------------------- |
| `GITLEAKS_REPORT.md`                          | Untouched; surfaced in dimension table.                |
| `BACKUP_INTEGRITY_REPORT.md`                  | Untouched.                                             |
| `BACKUP_AUDIT.log`                            | Untouched.                                             |
| `API_KEY_AUDIT.log`                           | Untouched.                                             |
| `ENV_AUDIT.log` (generated by EnvironmentSanitizer.ps1) | Untouched.                                    |
| `MCP_HOST_HEALTH.log`                         | Untouched.                                             |
| `PROJECT_BRAIN_2_0/audit.log`                 | Untouched.                                             |
| `incident_<ts>.json` (when generated)          | Untouched.                                             |

> Every prior surface is preserved. No dimension is renamed, replaced, or pruned.

---

## 8. What this scaffolding does NOT do

- Does NOT enforce. The scaffolding observes; humans enforce.
- Does NOT auto-notify. The notification system (OPT-4.9) is a future artefact.
- Does NOT modify provider keys. Key handling is OPT-7.1 (preserved).
- Does NOT replace gitleaks with a different scanner.
- Does NOT collapse multiple audit dimensions into a single log.

---

## 9. Next-step placebo (out of scope here)

- A **read-only** dashboard that polls each audit dimension at the cadence in §2 and emits a flat summary. **Deliberately deferred**; no runnable artifact accompanies this doc.
- A **read-only** weekly digest aggregating headlines via simple grep over each `*.log`. **Deliberately deferred.**

> Placebos above are listed to **make the absence explicit** rather than scramble coverage. Add them in a future additive turn.

---

*Designed under the user's Golden Rules: append, never delete; preserve, never relabel; protect, never rewrite. Rule #8 personal folders (Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD) are fenced off at every layer.*
