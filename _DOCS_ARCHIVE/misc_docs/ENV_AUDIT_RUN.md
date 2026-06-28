# ENV_AUDIT_RUN.md — companion explainer

✅ COMPLIANCE — this document and its companion script `ENV_AUDIT_RUN.ps1` are ADDITIVE ONLY. They do not delete, rename, or rewrite any existing artifact. They never modify `.env` or `.env.example` — both are read-only inputs.

## 1. Purpose
First concrete env-vs-example checker. Reads `.env` and `.env.example` (read-only), and under `-Run` appends one audit row per key to `ENV_AUDIT.log` (append-only). Default mode is `-DryRun`.

## 2. Closed status enum
`ENV_KEY_STATUS_ENUM = ('present','missing_in_env','extra_in_env','placeholder_value','blank_value')` — closed; any value outside the enum is refused.

## 3. Refusal matrix
| Condition | Exit |
| --- | --- |
| Any of `-EnvPath` / `-ExamplePath` / `-AuditLogPath` under Rule #8 folder | 2 |
| `.env.example` not found | 3 |
| Both `-DryRun` and `-Run` passed | 5 |

## 4. Append discipline
- Only writer is `Add-Content -LiteralPath` against `ENV_AUDIT.log`.
- One row per key analyzed (alphabetical scan of `.env.example` keys, then any extras in `.env` that are not in `.env.example`).
- Format: `YYYY-MM-DDTHH:MM:SSZ | event=env_audit | key=… | status=…`.

## 5. How to run
```powershell
# Default dry-run (no log writes)
.\ENV_AUDIT_RUN.ps1 -EnvPath .\.env -ExamplePath .\.env.example

# Opt-in to write audit rows
.\ENV_AUDIT_RUN.ps1 -EnvPath .\.env -ExamplePath .\.env.example -Run
```

## 6. Relationship to existing artifacts
- `APPEND_ONLY_HYGIENE_RUNNER.py` — already lists `ENV_AUDIT.log` in its 12-item `TRACKED_LOGS` closed list. Untouched.
- `.env` and `.env.example` — read-only inputs.
- Prior audit/runners — Untouched.

## 7. Detection rules for `placeholder_value`
Lower-cases the value and checks for these substrings:
`your-`, `changeme`, `example`, `placeholder`, `xxx`, `todo`, `<`, `>`, `replace-me`.

This is a heuristic, not a schema validator. Operators are expected to inspect the log manually for false positives.

## 8. Future upgrade path (operator-run)
- Adding new optional fields: extends `Classify-Value` only; enum stays closed.
- New placeholder list: append to `$placeholders` inside `Classify-Value`.
- New key status: only by extending `ENV_KEY_STATUS_ENUM` (operator-side).

---

Rule #8 — Personal-Folder Fence (verbatim)
This script refuses to read from or write to any path that resolves inside any folder from the following eight list:

1. `Documents`
2. `Downloads`
3. `Pictures`
4. `Videos`
5. `Music`
6. `Desktop`
7. `OneDrive`
8. `ARCHIVE_OLD`

The match is on path segments after normalization (forward slashes + trailing-slash trim), so `C:\Downloads\foo.json` and `C:/Users/me/Downloads/` are both caught. `ARCHIVE_OLD` appears as a segment, so `…/Downloads/ARCHIVE_OLD/anything` is caught. The list is exhaustive; it does not cover other places — by design.
