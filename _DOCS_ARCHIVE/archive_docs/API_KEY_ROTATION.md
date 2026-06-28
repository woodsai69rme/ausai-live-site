# 🔐 API_KEY_ROTATION.md  *(OPT-7.1 follow-on — rotation playbook)*

> **A companion doc to `API_KEY_REGISTRY.json`.** That registry is the source of truth for *which keys exist*. This document prescribes *how a key is rotated* without breaking any running tool — graceful dual-key window, ordered swap, audit trail. Never destructive. Always reversible.

---

## ✅ COMPLIANCE — this document is ADDITIVE ONLY.

- ✔ Adds: NEW `API_KEY_ROTATION.md`. No file modified.
- ✔ Honors: `API_KEY_REGISTRY.json` schema (untouched); every prior artifact listed below is untouched.
- ✔ Honors: append-only discipline — rotation APPLIES changes; never DESTROYS a prior entry.
- ✦ Does NOT touch Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD.
- ✦ Does NOT recommend destroying, archiving, or relabelling any prior key, registry row, or audit line.

---

## 1. Why rotate

- A key is approaching its expiry / cyclic-rotation threshold.
- A key was seen in an untrusted location (a logfile, a screenshot, an email).
- A provider announced mandatory rotation.
- Routine hygiene (quarterly / half-yearly).

Rotation is performed **without service interruption** via a dual-key window.

---

## 2. The dual-key window (graceful swap)

```
T0    | current=KEY_OLD only                       | tools read KEY_OLD
T0+1d | current=KEY_OLD, current+1d=KEY_NEW (NEW appended) | tools may read either
T0+7d | current=KEY_OLD, current+1d=KEY_NEW        | tools SHOULD read KEY_NEW
T0+14d| current=KEY_NEW only; KEY_OLD becomes "rotated-out"  | old line remains in registry + audit
```

> At every T, the **JSON registry row for KEY_OLD is preserved**. It transitions through four lifecycle states: `active` → `dual-window` → `deprecating-soon` → **`rotated-out`** (preserved forever). It is **never deleted**.

> The audit log gains a single `api_key_rotation` event line at each T. Lines are append-only.

---

## 3. State machine

```
                  ┌────────┐  append NEW key    ┌──────────────┐
   existing   ──► │ active │ ─────────────────► │ dual-window  │
                  └────────┘                    └──────┬───────┘
                                                      │ T+7d mark
                                                      ▼
                                                ┌──────────────┐
                                                │ deprecating- │
                                                │   soon       │
                                                └──────┬───────┘
                                                      │ T+14d mark
                                                      ▼
                                                ┌──────────────┐
                                                │ rotated-out  │   (preserved forever)
                                                └──────────────┘
```

> Four states. Each transition is an **append-only** audit line. There is no destroy-state.

---

## 4. Rotation procedure (operator or runner-driven)

1. **Append** the NEW key row to `API_KEY_REGISTRY.json` with state `dual-window`.
2. Update all currently-running tools to read either `active` or `dual-window` keys. (Tools that ignore `dual-window` continue to read `active` automatically — backwards-compatible.)
3. After a grace period, **transition** the OLD key row to `deprecating-soon`. **The row stays in the file.**
4. After the second grace period, **transition** the OLD key row to `rotated-out`. **The row stays in the file.**
5. Each step appends a `api_key_rotation` line to `API_KEY_AUDIT.log`.
6. **Never delete** the OLD key row, regardless of state.

---

## 5. Refusal matrix

| Scenario                                                | Behaviour                                                  |
| ------------------------------------------------------- | ---------------------------------------------------------- |
| Attempt to DELETE a key row from `API_KEY_REGISTRY.json` | **REFUSED** — append `rotation_refused_delete` audit line. |
| Set state of a key to a value outside the four states   | **REFUSED** — append `rotation_refused_state` line.        |
| Skip a state (e.g. `active` → `rotated-out`)            | **REFUSED** — must traverse all four in order.             |
| Bulk-rewrite `API_KEY_REGISTRY.json` via Set-Content     | **REFUSED** — only appends ARE permitted.                  |
| Audit log unwritable                                     | **REFUSED** — rotation cannot proceed without an audit trail. |
| Personal-folder detected as new key path                | **REFUSED** — KEY_NEW may not have `source_path` inside Rule #8 folders. |

---

## 6. Audit log line shapes

Append-only. The log is **never truncated, never reformatted**:

```
<ISO8601 UTC> | event=api_key_append | key_id=<id> | label=<label> | state=dual-window
<ISO8601 UTC> | event=api_key_rotation | key_id=<id> | state=deprecating-soon
<ISO8601 UTC> | event=api_key_rotation | key_id=<id> | state=rotated-out
<ISO8601 UTC> | event=rotation_refused_delete | key_id=<id> | reason=delete-attempt-blocked
<ISO8601 UTC> | event=rotation_refused_state | key_id=<id> | attempted_state=<bad>
```

---

## 7. Acceptance tests

- `test_append_dual_window` — append NEW key in state `dual-window` succeeds; OLD key remains.
- `test_double_skip_blocked` — direct transition `active` → `rotated-out` is REFUSED.
- `test_delete_refused` — `Remove-Item` or `del` against a key row is REFUSED with audit line.
- `test_audit_log_required` — rotation with read-only audit log is REFUSED.
- `test_personal_folder_path_refused` — NEW key whose `source_path` resides in any Rule #8 folder is REFUSED.
- `test_backwards_compat_after_rotation` — a tool still pointing at `active` state reads either old or new depending on the registry's grace-period flags.

---

## 8. Compatibility with everything prior

| Prior artifact               | Status                                                       |
| ---------------------------- | ------------------------------------------------------------ |
| `API_KEY_REGISTRY.json`       | Untouched schema. Rows are appended, never deleted.           |
| `API_KEY_AUDIT.log`           | Format-extended with `event=api_key_rotation` lines (additive). |
| `API_USAGE.html`              | Untouched; reads audit.log (which now contains rotation entries). |
| `EnvironmentSanitizer.ps1`    | Untouched; SHA-256 stamps each `.env*` file; never deletes.   |
| `verify_backups.ps1`          | Untouched.                                                    |

> Every prior surface is preserved. No schema rename. No file replacement. The rotation lifecycle is **append-only**.

---

## 9. What API_KEY_ROTATION does NOT do

- Does NOT auto-rotate. Operator-driven or scheduled-job-driven (e.g. weekly).
- Does NOT broadcast alerts. (Notification system is OPT-4.9 — out of scope here.)
- Does NOT modify provider-side keys. The provider dashboard handles that.
- Does NOT delete a key from the registry under any circumstance.

---

*Designed under the user's Golden Rules: append, never delete; preserve, never relabel; protect, never rewrite. Rule #8 personal folders (Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD) are fenced off at every layer.*
