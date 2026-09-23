# 💵 Append-RevenueEvent.ps1 — companion explainer

> **First concrete appender for `REVENUE_LEDGER.jsonl`** (per `REVENUE_TRACKING_DESIGN.md`). Appends exactly ONE line per call. Never rewrites, never truncates, never dedupes by deletion. Personal-folder guard rigid.

---

## ✅ COMPLIANCE — this document and its companion script are ADDITIVE ONLY.

- ✔ Adds: NEW `Append-RevenueEvent.ps1` + NEW `Append-RevenueEvent.md`. Nothing modified.
- ✔ Honors: `REVENUE_TRACKING_DESIGN.md` (read-only). The closed event enum, ledger shape, refusal matrix, and read-only aggregator semantics are unchanged.
- ✦ Does NOT touch Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD.
- ✦ Does NOT propose rewriting `REVENUE_READINESS_REPORT.md` or any existing revenue line.

---

## 1. Allowed event enum (closed)

| Event kind           | Source example              | Amount semantics           |
| -------------------- | --------------------------- | -------------------------- |
| `provider_key_active`| `pipeline:rotation-runner`  | null (realized post-cycle) |
| `deploy_published`   | `pipeline:marketplace`      | 0 (realized post-deploy)   |
| `creative_published` | `pipeline:ad-creative`      | 0 (realized post-impression)|
| `signal_emitted`     | `pipeline:crypto-sentiment` | null                       |
| `notify_dispatched`  | `pipeline:notify`           | null                       |

> Five event kinds. The retry refuses any other event kind with exit 3.

---

## 2. Refusal matrix

| Trigger                                          | Exit code |
| ------------------------------------------------ | --------- |
| `--source` resolves inside a Rule #8 personal    | 2         |
| `--ledger-path` resolves inside a Rule #8 personal| 2         |
| `--event` outside the closed enum                 | 3         |
| `--amount-usd < 0` without `--refund`             | 4         |
| `--id` empty                                     | 5         |
| `--meta-json` not parseable as JSON                | 6         |

> All refusals are followed by an error line on stderr. **No line is written to the ledger on refusal.**

---

## 3. Append discipline

For each successful call:

- **Exactly one line** is appended to `REVENUE_LEDGER.jsonl`.
- The line begins with `{"ts":"<ISO8601 UTC>"`.
- `event` ∈ closed enum.
- `id` is unique per source per event (operator-asserted; not enforced by the script).
- `amount_usd` is either a float or null.
- `meta` is well-formed JSON (compact).

> The script never truncates, never rewrites, never reflows. `Truncate`/`Set-Content`/`Clear-Content` is never invoked.

---

## 4. The refund marker

A negative `amount_usd` is only valid when accompanied by `--refund`. On `--refund`, the script ensures `meta.refund == true` is present (auto-injected if absent).

> A "silent negative" is impossible to log via this script. Refunds are an explicit event, not a noise line.

---

## 5. Never-do list (carried forward)

- The script **MUST NEVER**: DELETE the ledger, REWRITE a line, BULK-IMPORT a batch, MERGE id-replays into a single line, RESTRUCTURE schema.
- The script **MUST NEVER**: write to a path inside a Rule #8 personal folder.
- The script **MUST NEVER**: accept an `event` kind outside the closed enum.
- The script **MUST NEVER**: emit a line whose `ts` is not ISO8601 UTC.

---

## 6. Acceptance tests

- `test_append_one_line` — happy path appends exactly one line.
- `test_personal_folder_source_refused` — exit 2 on `--source` inside Music.
- `test_personal_folder_ledger_refused` — exit 2 on a ledger path inside Downloads.
- `test_unknown_event_refused` — exit 3 on `--event nonexistent_kind`.
- `test_negative_without_refund_refused` — exit 4 on `--amount-usd -1.0` without `--refund`.
- `test_refund_marker_injected` — `--refund` adds `meta.refund=true`.
- `test_id_empty_refused` — exit 5 on `--id ''`.
- `test_meta_json_invalid_refused` — exit 6 on `--meta-json 'broken'`.
- `test_dry_run_no_write` — ledger file is byte-identical post `--dry-run`.

---

## 7. Compatibility with everything prior

| Prior artifact                        | Status                                                |
| ------------------------------------- | ----------------------------------------------------- |
| `REVENUE_TRACKING_DESIGN.md`          | Untouched. This script implements its append contract. |
| `REVENUE_LEDGER.jsonl` (when live)    | First writer; established by this script.              |
| `API_KEY_REGISTRY.json`               | Untouched. Its `api_key_active` events surface here.   |
| `GITLEAKS_REPORT.md`                  | Untouched.                                             |

> No prior surface is renamed, replaced, or erased.

---

## 8. What this script does NOT do

- Does NOT auto-publish events. Operator-driven.
- Does NOT generate revenue events from inference. A future runner (a sister script) may feed this script.
- Does NOT modify any source registry. The script reads no source; only `--source` is a free-form id.
- Does NOT log to `audit.log` (the brain audit). Cross-system correlation is a future turn.

---

*Designed under the user's Golden Rules: append, never delete; preserve, never relabel; protect, never rewrite. Rule #8 personal folders (Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD) are fenced off at every layer.*
