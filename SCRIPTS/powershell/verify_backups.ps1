# verify_backups.ps1 - OPT-1.7 Backup Integrity Verifier
#
# ✅ COMPLIANCE: ADDITIVE ONLY. Reads every backup file, computes SHA-256, appends to
# BACKUP_INTEGRITY_REPORT.md. NEVER deletes, modifies, moves, or archives
# any backup. Personal folders are listed (read-only) but not indexed.
#
# Usage: powershell -ExecutionPolicy Bypass -File .\verify_backups.ps1
#
# Compliance footer (canonical, mirrors all .md docs):
#   Golden Rule #1 - Nothing is obsolete (we never delete)
#   Golden Rule #5 - All backups are critical (we never alter backups)
#   Golden Rule #7 - Enhancement not reduction
#   Golden Rule #8 - Personal folders are read-only

[CmdletBinding()]
param(
    [string[]]$Roots = @(
        "$HOME\BACKUPS",
        "$HOME\SCRIPTS\BACKUPS",
        "$HOME\COMPLETED_PROJECTS",
        "$HOME\.claude\backups",
        "$HOME\Documents\backup.txt"
    ),
    [string]$ReportPath = "$HOME\BACKUP_INTEGRITY_REPORT.md",
    [string]$ManifestPath = "$HOME\BACKUP_INTEGRITY_MANIFEST.csv"
)

# Personal folders: never index
$PersonalFolders = @(
    "$HOME\Documents",
    "$HOME\Downloads",
    "$HOME\Pictures",
    "$HOME\Videos",
    "$HOME\Music",
    "$HOME\Desktop",
    "$HOME\OneDrive",
    "$HOME\Downloads\ARCHIVE_OLD"
)

# 1. Fail loud if FILE-WHITELIST accidentally points into personal folders
foreach ($r in $Roots) {
    foreach ($p in $PersonalFolders) {
        if ($r -like "$p*") {
            throw "REFUSED: root '$r' is inside personal folder '$p' (Rule #8)."
        }
    }
}

# 2. Discover backup files (read-only)
$files = foreach ($root in $Roots) {
    if (-not (Test-Path -LiteralPath $root)) { continue }
    Get-ChildItem -LiteralPath $root -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch '^(.*\\(Documents|Downloads|Pictures|Videos|Music|Desktop|OneDrive|Downloads\\ARCHIVE_OLD))($|\\)' }
}

if (-not $files -or $files.Count -eq 0) {
    Write-Host "No backup files discovered in $($Roots -join ', ')."
    exit 0
}

# 3. Compute SHA-256 (append-only audit log)
$rows = foreach ($f in $files) {
    try {
        $h = Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256 -ErrorAction Stop
        [pscustomobject]@{
            Path      = $f.FullName
            SizeBytes = $f.Length
            LastWrite = $f.LastWriteTime.ToString('o')
            Sha256    = $h.Hash
            Status    = 'ok'
            Error     = ''
        }
    } catch {
        [pscustomobject]@{
            Path      = $f.FullName
            SizeBytes = $f.Length
            LastWrite = $f.LastWriteTime.ToString('o')
            Sha256    = ''
            Status    = 'error'
            Error     = $_.Exception.Message
        }
    }
}

# 4. Append-only manifest
$rows | Export-Csv -LiteralPath $ManifestPath -NoTypeInformation -Append

# 5. Append-only integrity report
$ts = (Get-Date).ToString('o')
$okCount  = ($rows | Where-Object Status -eq 'ok').Count
$errCount = ($rows | Where-Object Status -eq 'error').Count

$report = @"
## Verification run - $ts

- Files inspected: $(@($rows).Count)
- OK: $okCount
- Errors flagged (NOT deleted; per Rule #5): $errCount
- Roots scanned: $($Roots -join ', ')
- Manifest appended to: $ManifestPath
- Personal folders excluded: Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\\ARCHIVE_OLD

### Files (top 50 by size)

| Status | Size | SHA-256 (head) | Path |
|---|---|---|---|
"@
$top = $rows | Sort-Object SizeBytes -Descending | Select-Object -First 50
foreach ($r in $top) {
    $sha = if ($r.Sha256) { $r.Sha256.Substring(0,12) } else { '-' }
    $report += "`n| $($r.Status) | $($r.SizeBytes) | $sha | $($r.Path) |"
}

$report | Out-File -LiteralPath $ReportPath -Append -Encoding utf8

Write-Host "verify_backups: $($rows.Count) files; $okCount ok; $errCount flagged."" Appended to $ReportPath and $ManifestPath."

# 6. Compliance log
"$(Get-Date -Format 'o') VERIFY_BACKUPS ok=$okCount err=$errCount" |
    Out-File -LiteralPath "$HOME\08_SCRIPTS\BACKUP_AUDIT.log" -Append -Encoding utf8
