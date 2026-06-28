# BACKUP_AUDIT_RUN.md — companion explainer

✅ COMPLIANCE — this document and its companion script `BACKUP_AUDIT_RUN.ps1` are ADDITIVE ONLY. They do not delete, rename, or rewrite any existing artifact.

## 1. Purpose
First concrete daily backup-integrity checker. Reads `BACKUP_MANIFEST.json` (read-only) and, under `-Run`, appends one audit row per manifest entry to `BACKUP_AUDIT.log` (append-only). Default mode is `-DryRun`; `-Run` is opt-in.

## 2. Closed status enum
`BACKUP_STATUS_ENUM = ('ok','size_mismatch','sha256_mismatch','missing','stale','unreadable')` — closed; any value outside the enum throws + exits.

## 3. Refusal matrix
| Condition | Exit |
| --- | --- |
| `-ManifestPath` is inside any Rule #8 folder | 2 |
| `-AuditLogPath` is inside any Rule #8 folder | 2 |
| Manifest file not found | 3 |
| Manifest cannot be parsed as JSON | 4 |
| Both `-DryRun` and `-Run` passed | 5 |

## 4. Append discipline
- Only writer is `Add-Content -LiteralPath` against `BACKUP_AUDIT.log`.
- One row per manifest entry per invocation.
- Format: `YYYY-MM-DDTHH:MM:SSZ | event=backup_audit | name=… | status=… | detail=…`.

## 5. How to run
```powershell
# Default dry-run (no log writes)
.\BACKUP_AUDIT_RUN.ps1 -ManifestPath .\BACKUP_MANIFEST.json

# Opt-in to write audit rows
.\BACKUP_AUDIT_RUN.ps1 -ManifestPath .\BACKUP_MANIFEST.json -Run
```

## 6. Relationship to existing artifacts
- `APPEND_ONLY_HYGIENE_RUNNER.py` — already lists `BACKUP_AUDIT.log` in its 12-item `TRACKED_LOGS` closed list. Untouched.
- `ARCHON` snapshot ecosystem and prior audit scripts — Untouched.

## 7. Manifest expected shape (JSON array)
```json
[
  {
    "name": "DREAM_BOARD_daily",
    "path": "C:/backups/DREAM_BOARD_daily.zip",
    "expected_min_size_bytes": 1048576,
    "max_age_days": 2,
    "expected_sha256": null
  }
]
```

`expected_sha256` is optional. `max_age_days` is optional. `expected_min_size_bytes` is optional. The script probes each field only when present.

## 8. Future upgrade path (operator-run)
- Adding new optional fields: extends `Test-Backup` only; enum stays closed.
- Compressed manifest: reuses the same `Read-Manifest` flow with no rewrite.

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
